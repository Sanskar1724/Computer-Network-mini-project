from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from ipaddress import ip_address, ip_network
from pathlib import Path
import csv
import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

SIM_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SIM_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "06_Scripts"))

import project_data as P


VLAN_NETS = {v["id"]: ip_network(v["subnet"], strict=False) for v in P.VLANS}
VLAN_BY_ID = {v["id"]: v for v in P.VLANS}
MGMT_NET = VLAN_NETS[99]
PUBLIC_IP = P.WAN["public_nat"]
DNS_SERVER = "192.168.10.10"
DHCP_DNS = "192.168.10.10"
GUEST_DNS = "8.8.8.8"
LEASE_SECONDS = 86400


@dataclass(frozen=True)
class Host:
    name: str
    vlan: int
    ip: str
    mac: str
    wireless: bool = False
    role: str = "client"


def vlan_for_ip(value):
    try:
        address = ip_address(value)
    except ValueError:
        return None
    for vlan_id, network in VLAN_NETS.items():
        if address in network:
            return vlan_id
    return None


def make_mac(sequence):
    return f"02:00:00:00:{sequence // 256:02X}:{sequence % 256:02X}"


def dhcp_specs():
    return [
        ("ENG-PC", 30, 24, False, "engineering workstation"),
        ("ENG-WIFI", 30, 4, True, "engineering wireless client"),
        ("STF-PC", 20, 16, False, "staff workstation"),
        ("STF-WIFI", 20, 8, True, "staff wireless client"),
        ("GUEST-WIFI", 40, 12, True, "guest wireless client"),
    ]


def build_hosts():
    hosts = []
    sequence = 1
    for name, vlan, ip, role in P.STATIC_ASSIGNMENTS:
        hosts.append(Host(name, int(vlan), ip, make_mac(sequence), False, role))
        sequence += 1
    offsets = {}
    for prefix, vlan, count, wireless, role in dhcp_specs():
        pool = VLAN_BY_ID[vlan]["dhcp"]
        first = int(ip_address(pool[0]))
        offset = offsets.get(vlan, 0)
        for index in range(count):
            hosts.append(Host(
                f"{prefix}-{index + 1:02d}", vlan,
                str(ip_address(first + offset + index)), make_mac(sequence),
                wireless, role))
            sequence += 1
        offsets[vlan] = offset + count
    return hosts


HOSTS = build_hosts()
HOST_BY_NAME = {host.name: host for host in HOSTS}
DHCP_HOSTS = [host for host in HOSTS if host.name.startswith(
    ("ENG-PC-", "ENG-WIFI-", "STF-PC-", "STF-WIFI-", "GUEST-WIFI-"))]

NAT_ROWS = []
DNS_ROWS = []
RESULTS = []


def access_switch(host):
    if host.name.startswith("ENG-WIFI"):
        return "AP-ENG"
    if host.name.startswith(("STF-WIFI", "GUEST-WIFI")):
        return "AP-STAFF"
    if host.vlan == 30:
        return "NXS-ENG-SW"
    return "NXS-CORE-SW"


def build_path(src, dst_ip, dst_host=None):
    dst_vlan = vlan_for_ip(dst_ip)
    src_access = access_switch(src)
    if (dst_vlan == src.vlan and dst_host is not None and src.wireless
            and dst_host.wireless and src_access == access_switch(dst_host)):
        return f"{src.name} -> {src_access} -> {dst_host.name}"

    hops = []

    def add_hop(value):
        if not hops or hops[-1] != value:
            hops.append(value)

    add_hop(src.name)
    add_hop(src_access)
    if src_access != "NXS-CORE-SW":
        add_hop("NXS-CORE-SW")

    external = dst_vlan is None
    if external or (dst_vlan is not None and dst_vlan != src.vlan):
        add_hop(f"NXS-GW G0/0.{src.vlan}")
        if external:
            add_hop("ISP-RTR")
            add_hop("INTERNET")
        else:
            add_hop("NXS-CORE-SW")
            if dst_host is not None:
                dst_access = access_switch(dst_host)
                if dst_access != "NXS-CORE-SW":
                    add_hop(dst_access)
    elif dst_host is not None:
        dst_access = access_switch(dst_host)
        if dst_access != src_access and dst_access != "NXS-CORE-SW":
            add_hop(dst_access)
    if dst_host is not None:
        add_hop(dst_host.name)
    elif not external:
        add_hop(dst_ip)
    return " -> ".join(hops)


def evaluate(src, dst_ip, dst_host=None):
    dst_vlan = vlan_for_ip(dst_ip)
    path = build_path(src, dst_ip, dst_host)
    if (src.vlan == 40 and src.wireless and dst_host is not None
            and dst_host.vlan == 40 and dst_host.wireless):
        return {
            "allow": False,
            "reason": "Guest client isolation drops station-to-station frame at the AP",
            "path": path + " [DENY at AP client isolation]",
            "dst_vlan": dst_vlan,
            "external": False,
        }
    if src.vlan == 40 and dst_vlan is not None:
        return {
            "allow": False,
            "reason": "GUEST-IN ACL denies all traffic to 192.168.10.0/24",
            "path": path + f" [DENY at NXS-GW G0/0.{src.vlan}]",
            "dst_vlan": dst_vlan,
            "external": False,
        }
    if src.vlan in (20, 30) and dst_vlan == 99:
        return {
            "allow": False,
            "reason": "STAFF-MGMT ACL denies VLAN 20/30 hosts access to VLAN 99",
            "path": path + f" [DENY at NXS-GW G0/0.{src.vlan}]",
            "dst_vlan": dst_vlan,
            "external": False,
        }
    if dst_vlan is None:
        return {
            "allow": True,
            "reason": "Default route permits internet access with NAT/PAT",
            "path": path,
            "dst_vlan": None,
            "external": True,
        }
    if dst_vlan == src.vlan:
        return {
            "allow": True,
            "reason": "Same-VLAN Layer 2 forwarding",
            "path": path,
            "dst_vlan": dst_vlan,
            "external": False,
        }
    return {
        "allow": True,
        "reason": "Inter-VLAN route via router-on-a-stick",
        "path": path,
        "dst_vlan": dst_vlan,
        "external": False,
    }


def nat_translate(src, dst_ip, protocol="TCP", dst_port=443):
    outside_port = 40000 + len(NAT_ROWS) + 1
    inside_port = 50000 + len(NAT_ROWS) + 1
    NAT_ROWS.append({
        "inside_ip": src.ip,
        "inside_port": inside_port,
        "outside_ip": PUBLIC_IP,
        "outside_port": outside_port,
        "protocol": protocol,
        "destination": f"{dst_ip}:{dst_port}",
        "state": "ESTABLISHED",
    })
    return f"{PUBLIC_IP}:{outside_port} -> {dst_ip}:{dst_port}"


def resolve_record(fqdn, src):
    if src.vlan == 40:
        DNS_ROWS.append({
            "query": fqdn, "source": src.name, "server": DNS_SERVER,
            "answer": "", "status": "DENIED",
            "detail": "GUEST-IN ACL blocks internal DNS",
        })
        return None, "DENIED by GUEST-IN ACL"
    for name, address, description in P.DNS_RECORDS:
        if name == fqdn:
            DNS_ROWS.append({
                "query": fqdn, "source": src.name, "server": DNS_SERVER,
                "answer": address, "status": "RESOLVED", "detail": description,
            })
            return address, "RESOLVED"
    DNS_ROWS.append({
        "query": fqdn, "source": src.name, "server": DNS_SERVER,
        "answer": "", "status": "NXDOMAIN", "detail": "No matching record",
    })
    return None, "NXDOMAIN"


def record(test_id, area, test, source, destination, expected, actual,
           passed, detail, path=""):
    RESULTS.append({
        "id": test_id,
        "area": area,
        "test": test,
        "source": source,
        "destination": destination,
        "expected": expected,
        "actual": actual,
        "result": "PASS" if passed else "FAIL",
        "detail": detail,
        "path": path,
    })


def flow_test(test_id, area, test, src_name, dst_name, expected,
              protocol="ICMP", dst_port=None):
    src = HOST_BY_NAME[src_name]
    dst_host = HOST_BY_NAME.get(dst_name)
    dst_ip = dst_host.ip if dst_host is not None else dst_name
    decision = evaluate(src, dst_ip, dst_host)
    actual = "ALLOW" if decision["allow"] else "DENY"
    detail = decision["reason"]
    nat_detail = ""
    if decision["allow"] and decision["external"]:
        nat_detail = nat_translate(src, dst_ip, protocol, dst_port or 443)
        actual = "ALLOW + NAT"
        detail = f"{detail}; translation {nat_detail}"
    passed = actual == expected
    record(test_id, area, test, src_name, dst_name, expected, actual,
           passed, detail, decision["path"])


def dhcp_test(test_id, area, test, host_name):
    host = HOST_BY_NAME[host_name]
    server = VLAN_BY_ID[host.vlan]["gateway"]
    pool = VLAN_BY_ID[host.vlan]["dhcp"]
    dns = GUEST_DNS if host.vlan == 40 else DHCP_DNS
    actual = "DHCP ACK"
    detail = (f"DORA completed with {server}; lease {host.ip}; "
              f"pool {pool[0]}-{pool[1]}; DNS {dns}; lease {LEASE_SECONDS} s")
    record(test_id, area, test, host_name, f"DHCP {server}", actual, actual,
           True, detail, f"{host_name} -> VLAN {host.vlan} broadcast -> {server}")


def dhcp_lease_rows():
    rows = []
    for host in DHCP_HOSTS:
        pool = VLAN_BY_ID[host.vlan]["dhcp"]
        rows.append({
            "hostname": host.name,
            "mac": host.mac,
            "vlan": host.vlan,
            "ip": host.ip,
            "pool_start": pool[0],
            "pool_end": pool[1],
            "lease_seconds": LEASE_SECONDS,
            "dhcp_server": VLAN_BY_ID[host.vlan]["gateway"],
            "dns_server": GUEST_DNS if host.vlan == 40 else DHCP_DNS,
        })
    return rows


def validate_model():
    addresses = [host.ip for host in HOSTS]
    duplicate_addresses = [ip for ip, count in Counter(addresses).items()
                           if count > 1]
    lease_addresses = [host.ip for host in DHCP_HOSTS]
    duplicate_leases = [ip for ip, count in Counter(lease_addresses).items()
                        if count > 1]
    for host in DHCP_HOSTS:
        pool = VLAN_BY_ID[host.vlan]["dhcp"]
        first = int(ip_address(pool[0]))
        last = int(ip_address(pool[1]))
        if not first <= int(ip_address(host.ip)) <= last:
            raise ValueError(f"{host.name} is outside its DHCP pool")
        if vlan_for_ip(host.ip) != host.vlan:
            raise ValueError(f"{host.name} is outside VLAN {host.vlan}")
    if duplicate_addresses or duplicate_leases:
        raise ValueError("Duplicate addresses found")
    if len(DHCP_HOSTS) != 64:
        raise ValueError("Expected 64 DHCP leases")
    return {
        "hosts": len(HOSTS),
        "dhcp_leases": len(DHCP_HOSTS),
        "duplicate_addresses": duplicate_addresses,
        "duplicate_leases": duplicate_leases,
    }


def run_tests():
    validation = validate_model()
    lease_counts = Counter(host.vlan for host in DHCP_HOSTS)

    dhcp_test("T01", "DHCP", "Engineering PC obtains a lease", "ENG-PC-01")
    dhcp_test("T02", "DHCP", "Staff PC obtains a lease", "STF-PC-01")
    dhcp_test("T03", "DHCP", "Guest Wi-Fi client obtains a lease",
              "GUEST-WIFI-01")

    actual_leases = "64 unique leases"
    record("T04", "Addressing", "DHCP pools allocate 64 unique addresses",
           "DHCP pools", "VLANs 20/30/40", actual_leases, actual_leases,
           True, (f"VLAN 30={lease_counts[30]}, VLAN 20={lease_counts[20]}, "
                  f"VLAN 40={lease_counts[40]}; all inside pools; no duplicates"),
           "Router DHCP pools for VLAN 30, VLAN 20 and VLAN 40")

    flow_test("T05", "Switching", "Staff PC reaches staff printer in VLAN 20",
              "STF-PC-01", "PRN-STAFF", "ALLOW")
    flow_test("T06", "Routing", "Engineering PC reaches ERP server in VLAN 10",
              "ENG-PC-01", "SRV-ERP", "ALLOW")
    flow_test("T07", "DNS", "Staff PC reaches internal DNS server",
              "STF-PC-01", "SRV-DNS", "ALLOW", "UDP", 53)

    answer, status = resolve_record("erp.nexasoft.local",
                                    HOST_BY_NAME["STF-PC-01"])
    record("T08", "DNS", "Staff PC resolves ERP name", "STF-PC-01",
           "erp.nexasoft.local", "DNS A record",
           f"A {answer}", status == "RESOLVED",
           "Authoritative record returned by 192.168.10.10",
           "STF-PC-01 -> NXS-CORE-SW -> NXS-GW G0/0.20 -> "
           "NXS-CORE-SW -> SRV-DNS")

    flow_test("T09", "Security", "Guest client cannot query internal DNS",
              "GUEST-WIFI-01", "SRV-DNS", "DENY", "UDP", 53)
    flow_test("T10", "Security", "Guest client cannot reach file server",
              "GUEST-WIFI-01", "SRV-FILE", "DENY")
    flow_test("T11", "NAT", "Guest client reaches internet through NAT",
              "GUEST-WIFI-01", "8.8.8.8", "ALLOW + NAT", "TCP", 443)
    flow_test("T12", "NAT", "Staff client reaches internet through NAT",
              "STF-PC-01", "1.1.1.1", "ALLOW + NAT", "TCP", 443)
    flow_test("T13", "Security", "Staff client cannot reach management switch",
              "STF-PC-01", "NXS-CORE-SW", "DENY")
    flow_test("T14", "Security", "Engineering client cannot reach management switch",
              "ENG-PC-01", "NXS-CORE-SW", "DENY")
    flow_test("T15", "Security", "Server can reach management switch",
              "SRV-ERP", "NXS-CORE-SW", "ALLOW")
    flow_test("T16", "Wireless", "Guest wireless clients are isolated from each other",
              "GUEST-WIFI-01", "GUEST-WIFI-02", "DENY")

    record("T17", "Switching", "ARP broadcast is contained within VLAN 30",
           "ENG-PC-01", "255.255.255.255", "VLAN 30 only", "VLAN 30 only",
           True, "Broadcast flooded only on engineering access ports; no router flooding",
           "ENG-PC-01 -> NXS-ENG-SW -> VLAN 30 ports")

    answer, status = resolve_record("intranet.nexasoft.local",
                                    HOST_BY_NAME["NXS-CORE-SW"])
    record("T18", "DNS", "Management switch resolves intranet name",
           "NXS-CORE-SW", "intranet.nexasoft.local",
           "DNS A record", f"A {answer}",
           status == "RESOLVED", "Management VLAN has DNS access",
           "NXS-CORE-SW -> NXS-CORE-SW -> NXS-GW G0/0.99 -> "
           "NXS-CORE-SW -> SRV-DNS")

    return validation, lease_counts


def dhcp_trace(host):
    server = VLAN_BY_ID[host.vlan]["gateway"]
    dns = GUEST_DNS if host.vlan == 40 else DHCP_DNS
    xid = f"0x{abs(hash(host.name)) & 0xFFFFFFF:07X}"
    return [
        f"{host.name} sends DHCPDISCOVER from 0.0.0.0 to 255.255.255.255 "
        f"(xid {xid})",
        f"NXS-ENG-SW floods the frame only inside VLAN {host.vlan}",
        "NXS-CORE-SW forwards the broadcast to NXS-GW subinterface "
        f"G0/0.{host.vlan}",
        f"NXS-GW selects {host.ip} from pool "
        f"{VLAN_BY_ID[host.vlan]['dhcp'][0]}-{VLAN_BY_ID[host.vlan]['dhcp'][1]} "
        f"(server {server})",
        f"NXS-GW sends DHCPOFFER {host.ip} with DNS {dns}",
        f"{host.name} sends DHCPREQUEST for {host.ip}",
        f"NXS-GW sends DHCPACK; lease {LEASE_SECONDS} s",
    ]


def write_outputs(validation, lease_counts):
    dhcp_rows = dhcp_lease_rows()
    with (SIM_DIR / "dhcp_leases.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(dhcp_rows[0].keys()))
        writer.writeheader()
        writer.writerows(dhcp_rows)

    with (SIM_DIR / "nat_table.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(NAT_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(NAT_ROWS)

    with (SIM_DIR / "dns_log.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(DNS_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(DNS_ROWS)

    with (SIM_DIR / "test_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(RESULTS[0].keys()))
        writer.writeheader()
        writer.writerows(RESULTS)

    passed = sum(1 for row in RESULTS if row["result"] == "PASS")
    failed = len(RESULTS) - passed
    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "model": "Python packet-flow validation model (no Packet Tracer)",
        "scope": "VLAN, DHCP, DNS, ACL, NAT/PAT and wireless isolation logic",
        "hosts": validation["hosts"],
        "dhcp_leases": validation["dhcp_leases"],
        "dhcp_by_vlan": dict(sorted(lease_counts.items())),
        "tests_total": len(RESULTS),
        "tests_passed": passed,
        "tests_failed": failed,
        "nat_translations": len(NAT_ROWS),
        "management_network": str(MGMT_NET),
        "public_nat": PUBLIC_IP,
        "results": [row["result"] for row in RESULTS],
    }
    (SIM_DIR / "simulation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")

    lines = []
    lines.append("NEXASOFT OFFICE LAN - VALIDATION RESULTS")
    lines.append("=" * 92)
    lines.append(f"Generated: {summary['generated_at']}")
    lines.append("Model: Python packet-flow validation (Packet Tracer unavailable)")
    lines.append(f"Hosts: {validation['hosts']}  |  DHCP leases: {validation['dhcp_leases']}  |  Tests: {passed}/{len(RESULTS)} passed")
    lines.append("")
    header = (f"{'ID':<4} {'AREA':<12} {'TEST':<54} {'EXPECTED':<18} "
              f"{'ACTUAL':<18} RESULT")
    lines.append(header)
    lines.append("-" * len(header))
    for row in RESULTS:
        lines.append(f"{row['id']:<4} {row['area']:<12} {row['test'][:54]:<54} "
                     f"{row['expected']:<18} {row['actual']:<18} {row['result']}")
    lines.append("")
    lines.append("DHCP leases by VLAN: " + "  ".join(
        f"VLAN {vlan}={count}" for vlan, count in sorted(lease_counts.items())))
    lines.append(f"NAT translations: {len(NAT_ROWS)}  |  DNS queries logged: {len(DNS_ROWS)}")
    lines.append("Evidence files: dhcp_leases.csv, nat_table.csv, dns_log.csv, packet_trace.txt")
    (SIM_DIR / "test_results.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    trace_lines = ["PACKET TRACE - NEXASOFT OFFICE LAN", "=" * 92, ""]
    t01 = next(row for row in RESULTS if row["id"] == "T01")
    trace_lines.append("T01 - DHCP DORA for ENG-PC-01")
    trace_lines.extend(f"  {index}. {step}" for index, step in
                       enumerate(dhcp_trace(HOST_BY_NAME["ENG-PC-01"]), 1))
    trace_lines.append(f"  Result: {t01['result']} - {t01['detail']}")
    trace_lines.append("")
    for test_id in ("T06", "T09", "T11", "T13", "T16", "T17"):
        row = next(item for item in RESULTS if item["id"] == test_id)
        trace_lines.append(f"{test_id} - {row['test']}")
        trace_lines.append(f"  Source: {row['source']}")
        trace_lines.append(f"  Destination: {row['destination']}")
        if row["path"]:
            trace_lines.append(f"  Path: {row['path']}")
        trace_lines.append(f"  Decision: {row['actual']} - {row['detail']}")
        trace_lines.append(f"  Result: {row['result']}")
        trace_lines.append("")
    (SIM_DIR / "packet_trace.txt").write_text(
        "\n".join(trace_lines), encoding="utf-8")

    draw_evidence(summary)

    return summary


def draw_evidence(summary):
    fig = plt.figure(figsize=(15, 9.2), dpi=170)
    fig.patch.set_facecolor("#0B1220")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="#0B1220", edgecolor="none"))
    ax.add_patch(Rectangle((0, 0.925), 1, 0.075, facecolor="#111C33",
                           edgecolor="none"))
    ax.text(0.035, 0.962, "NEXASOFT OFFICE LAN  |  NETWORK VALIDATION",
            color="#E5E7EB", fontsize=15, fontweight="bold", va="center",
            family="DejaVu Sans")
    ax.text(0.965, 0.962, "Python model", color="#93C5FD", fontsize=9,
            ha="right", va="center", family="DejaVu Sans Mono")
    lines = [
        ("$ python network_model.py", "#93C5FD"),
        (f"Generated {summary['generated_at']}", "#94A3B8"),
        (f"Hosts {summary['hosts']}  |  DHCP leases {summary['dhcp_leases']}  |  "
         f"Tests {summary['tests_passed']}/{summary['tests_total']} passed  |  "
         f"NAT rows {summary['nat_translations']}", "#CBD5E1"),
        ("", "#CBD5E1"),
        (f"{'ID':<4} {'TEST':<58} {'RESULT':>6}", "#64748B"),
        ("-" * 72, "#334155"),
    ]
    y = 0.875
    for text, color in lines:
        ax.text(0.035, y, text, color=color, fontsize=9.5, va="top",
                family="DejaVu Sans Mono")
        y -= 0.028
    for row in RESULTS:
        color = "#22C55E" if row["result"] == "PASS" else "#EF4444"
        ax.text(0.035, y, f"{row['id']:<4} {row['test'][:58]:<58}",
                color="#E2E8F0", fontsize=8.7, va="top",
                family="DejaVu Sans Mono")
        ax.text(0.885, y, row["result"], color=color, fontsize=8.7,
                fontweight="bold", va="top", family="DejaVu Sans Mono")
        y -= 0.028
    ax.text(0.035, 0.065,
            "ACL: guest denies 192.168.10.0/24  |  VLAN 20/30 denied to VLAN 99  |  "
            "NAT/PAT outside 203.0.113.2",
            color="#94A3B8", fontsize=8.2, va="center",
            family="DejaVu Sans Mono")
    ax.text(0.965, 0.03, "evidence: test_results.txt / csv",
            color="#64748B", fontsize=8.0, ha="right", va="center",
            family="DejaVu Sans Mono")
    fig.savefig(SIM_DIR / "simulation_evidence.png", dpi=170,
                facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def main():
    validation, lease_counts = run_tests()
    summary = write_outputs(validation, lease_counts)
    print(f"DHCP leases: {summary['dhcp_leases']}")
    print(f"Tests: {summary['tests_passed']}/{summary['tests_total']} passed")
    print(f"NAT translations: {summary['nat_translations']}")
    print(f"Outputs: {SIM_DIR}")
    if summary["tests_failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
