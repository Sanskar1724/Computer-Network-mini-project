"""Single source of truth for the Assignment 8 LAN mini project."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS = PROJECT_ROOT / "assets"

STUDENT = {
    "name": "Sanskar Chandawar",
    "prn": "<PRN>",
    "roll": "<ROLL>",
    "division": "<DIVISION>",
    "program": "Computer Engineering",
    "year": "Third Year",
    "semester": "V",
    "subject": "Computer Networks Laboratory (2304312L)",
    "academic_year": "2026 \u2013 27",
}

# Personal identifiers live in student_details.json (git-ignored); the
# placeholders above are used when that file is absent.
_details = Path(__file__).with_name("student_details.json")
if _details.exists():
    import json
    STUDENT.update(json.loads(_details.read_text(encoding="utf-8")))

PROJECT = {
    "title": ("Design and Implementation of a Local Area Network for a "
              "Small Office: Architecture, IP Addressing and Cost Analysis"),
    "short_title": "NexaSoft Office LAN",
    "site": ("2nd Floor, Wing B, Sunrise Business Park, Baner, Pune "
             "411045 (site details anonymised)"),
    "area": "70 ft \u00d7 40 ft (2,800 sq ft)",
    "users": "48 wired ports and up to 24 concurrent wireless clients",
    "option": "Project Option 1 \u2014 LAN design, IP addressing and cost analysis",
}

# VLANs are allocated as one contiguous VLSM block: 192.168.10.0/24.
VLANS = [
    {
        "id": 10, "name": "Servers", "subnet": "192.168.10.0/26",
        "gateway": "192.168.10.1", "purpose": "DNS, file/backup and ERP servers",
        "dhcp": None,
        "reserved": "192.168.10.10 \u2013 192.168.10.19 are static server addresses",
    },
    {
        "id": 30, "name": "Engineering", "subnet": "192.168.10.64/26",
        "gateway": "192.168.10.65",
        "purpose": "24 engineering workstations, printer and engineering Wi-Fi",
        "dhcp": ("192.168.10.66", "192.168.10.124"),
        "reserved": "192.168.10.125 \u2013 192.168.10.126 are static printers",
    },
    {
        "id": 20, "name": "Staff", "subnet": "192.168.10.128/27",
        "gateway": "192.168.10.129",
        "purpose": "Admin, HR, finance, management, reception and staff Wi-Fi",
        "dhcp": ("192.168.10.132", "192.168.10.158"),
        "reserved": "192.168.10.130 \u2013 192.168.10.131 are static printers",
    },
    {
        "id": 40, "name": "Guest", "subnet": "192.168.10.160/27",
        "gateway": "192.168.10.161",
        "purpose": "Guest Wi-Fi; internet-only access with client isolation",
        "dhcp": ("192.168.10.162", "192.168.10.190"),
        "reserved": "No static guest devices",
    },
    {
        "id": 99, "name": "Management", "subnet": "192.168.10.192/28",
        "gateway": "192.168.10.193",
        "purpose": "Router, switches, access points and out-of-band management",
        "dhcp": None,
        "reserved": "192.168.10.194 \u2013 192.168.10.198 are network devices",
    },
]

VLAN_BY_ID = {v["id"]: v for v in VLANS}

WAN = {
    "network": "203.0.113.0/30",
    "isp_gateway": "203.0.113.1",
    "router_ip": "203.0.113.2",
    "public_nat": "203.0.113.2",
    "isp_bandwidth": "100 Mbps business fibre",
}

DNS_RECORDS = [
    ("intranet.nexasoft.local", "192.168.10.10", "Intranet portal"),
    ("files.nexasoft.local", "192.168.10.11", "File server"),
    ("erp.nexasoft.local", "192.168.10.12", "ERP application"),
]

STATIC_ASSIGNMENTS = [
    ("SRV-DNS", "10", "192.168.10.10", "DNS, NTP and management portal"),
    ("SRV-FILE", "10", "192.168.10.11", "File and backup server"),
    ("SRV-ERP", "10", "192.168.10.12", "ERP application server"),
    ("PRN-ENG", "30", "192.168.10.125", "Engineering floor printer"),
    ("PRN-STAFF", "20", "192.168.10.130", "Staff and reception printer"),
    ("NXS-CORE-SW", "99", "192.168.10.194", "Core switch management"),
    ("NXS-ENG-SW", "99", "192.168.10.195", "Engineering access switch"),
    ("AP-ENG", "99", "192.168.10.196", "Engineering ceiling access point"),
    ("AP-STAFF", "99", "192.168.10.197", "Conference and reception access point"),
    ("AP-MGMT", "99", "192.168.10.198", "Management and HR access point"),
]

# The 48 physical Cat6 drops include 3 APs, 2 printers and 3 servers.
ROOMS = [
    {"name": "Reception", "x": 0, "y": 0, "w": 12, "h": 14, "drops": 2,
     "ap": None, "note": "ISP entry and visitor seating"},
    {"name": "Conference", "x": 12, "y": 0, "w": 20, "h": 14, "drops": 3,
     "ap": "AP-STAFF", "note": "2 data drops + 1 AP"},
    {"name": "Admin / HR / Finance", "x": 32, "y": 0, "w": 22, "h": 14,
     "drops": 9, "ap": None, "note": "8 workstations + printer"},
    {"name": "Store / Utility", "x": 54, "y": 0, "w": 16, "h": 14,
     "drops": 0, "ap": None, "note": "No data outlets"},
    {"name": "Engineering", "x": 0, "y": 18, "w": 30, "h": 22,
     "drops": 26, "ap": "AP-ENG", "note": "24 workstations + printer + AP"},
    {"name": "Server room", "x": 30, "y": 28, "w": 8, "h": 12,
     "drops": 3, "ap": None, "note": "Rack, router, core switch, servers"},
    {"name": "Pantry", "x": 38, "y": 18, "w": 8, "h": 10,
     "drops": 0, "ap": None, "note": "No data outlets"},
    {"name": "Breakout", "x": 46, "y": 18, "w": 8, "h": 10,
     "drops": 0, "ap": None, "note": "Informal collaboration area"},
    {"name": "Restrooms", "x": 54, "y": 18, "w": 16, "h": 10,
     "drops": 0, "ap": None, "note": "No data outlets"},
    {"name": "Management", "x": 54, "y": 28, "w": 16, "h": 12,
     "drops": 5, "ap": "AP-MGMT", "note": "4 workstations + AP"},
]

AP_POSITIONS = {
    "AP-ENG": (15, 29, "Engineering"),
    "AP-STAFF": (22, 7, "Conference / reception"),
    "AP-MGMT": (62, 34, "Management / HR"),
}

SSIDS = [
    ("NEXA-ENG", "30", "WPA2-AES (PSK)", "Engineering laptops and phones", "No"),
    ("NEXA-STAFF", "20", "WPA2-AES (PSK)", "Staff laptops and phones", "No"),
    ("NEXA-GUEST", "40", "WPA2-AES (PSK)", "Visitors", "Yes"),
]

REQUIREMENTS = [
    ("R1", "Wired access", "48 switched 1 Gbps ports with at least 15% spare capacity"),
    ("R2", "Wireless access", "3 APs; 24 concurrent clients; WPA2-AES; guest isolation"),
    ("R3", "Segmentation", "Separate VLANs for servers, engineering, staff, guest and management"),
    ("R4", "Inter-VLAN routing", "Router-on-a-stick with 802.1Q trunk; all internal VLANs reachable"),
    ("R5", "Addressing and services", "VLSM IPv4 plan; centralized DHCP and DNS"),
    ("R6", "Internet access", "100 Mbps ISP link with NAT/PAT and a default route"),
    ("R7", "Availability", "UPS-backed core; RSTP; redundant 2 \u00d7 1 Gbps access uplink"),
    ("R8", "Security", "Guest ACL, management ACL, SSH only, port security, DHCP snooping, DAI"),
    ("R9", "Growth", "At least 20% free ports and addresses in each user VLAN"),
    ("R10", "Cost", "CapEx at or below Rs. 6.0 lakh including 5% contingency"),
]

SITE_OBSERVATIONS = [
    ("Location and area", "2nd floor, Wing B; 70 ft \u00d7 40 ft; 2,800 sq ft; 10 rooms plus corridor",
     "Single wiring closet in the server room; 48 drops planned"),
    ("Construction", "Gypsum partitions, false ceiling at 9.5 ft, concrete columns, existing 25 mm conduits",
     "Use ceiling tiles and surface trunking; no structural drilling"),
    ("Cable paths", "Corridor ceiling tray from reception to server room; longest run 42 m, average 24 m",
     "Cat6 is within the 90 m permanent-link limit; no repeaters"),
    ("Power", "Dedicated 16 A circuits at server room; 1 kVA UPS for access closet; earthing available",
     "Add 3 kVA online UPS for core; APs powered by PoE+"),
    ("Wireless survey", "12 neighbouring SSIDs on 2.4 GHz; 5 on 5 GHz; 2.4 GHz utilisation 38%",
     "Prefer 5 GHz; use 1/6/11 and 36/44/149; keep AP power auto"),
    ("Coverage target", "RSSI \u2265 \u221267 dBm in work areas; 15% overlap between cells",
     "3 ceiling APs: engineering, conference/reception and management"),
    ("Security", "Lockable server room, CCTV coverage, reception controls visitor access",
     "Guest SSID isolated; management VLAN restricted by ACL"),
    ("Operating hours", "Office 09:00\u201319:00, Monday to Saturday; cabling after hours",
     "Schedule cutover outside business hours; keep existing link during migration"),
]

DESIGN_GOALS = [
    ("Scalability", "VLSM and 20% spare ports/addresses; a second access switch can be added on the core"),
    ("Performance", "1 Gbps access, 2 Gbps aggregated access uplink, 5 GHz preferred for wireless"),
    ("Availability", "RSTP, redundant fibre uplink, UPS-backed core and access closet"),
    ("Security", "VLAN segmentation, guest ACL, management ACL, SSH, port security, DHCP snooping and DAI"),
    ("Manageability", "Static infrastructure addressing, DHCP for endpoints, consistent naming and labelling"),
    ("Cost", "Refurbished Cisco router, PoE+ core switch and three APs; total within the Rs. 6 lakh cap"),
]

DEVICES = [
    ("NXS-GW", "Cisco 2911-SEC/K9 router", "1", "Inter-VLAN routing, NAT/PAT, DHCP, ACL, WAN"),
    ("NXS-CORE-SW", "Cisco Catalyst 2960X-48FPD-L", "1", "Core switching, PoE+, VLAN trunking, STP root"),
    ("NXS-ENG-SW", "Cisco Catalyst 2960X-24TS-L", "1", "Engineering access switching and fibre uplink"),
    ("AP-ENG / AP-STAFF / AP-MGMT", "Cisco Aironet 1832I-B-K9", "3", "802.11ac Wave 2 staff and guest Wi-Fi"),
    ("ISP-RTR", "ISP-managed fibre termination", "1", "100 Mbps WAN handoff (not part of project cost)"),
]

LINK_SCHEDULE = [
    ("ISP \u2192 NXS-GW", "203.0.113.1 \u2192 203.0.113.2", "100 Mbps fibre", "WAN / NAT outside"),
    ("NXS-GW G0/0 \u2192 NXS-CORE-SW Gi1/0/48", "802.1Q trunk, native VLAN 99", "1 Gbps copper", "Router-on-a-stick"),
    ("NXS-CORE-SW Po1 \u2192 NXS-ENG-SW Po2", "2 \u00d7 1 Gbps OM3 fibre, LACP", "2 Gbps aggregate", "802.1Q trunk, native VLAN 99"),
    ("NXS-CORE-SW \u2192 AP-ENG/STAFF/MGMT", "802.1Q trunk, native VLAN 99", "1 Gbps copper", "SSIDs on VLAN 20 and 40"),
    ("NXS-CORE-SW \u2192 servers", "Access VLAN 10", "1 Gbps copper", "Static server addresses"),
    ("NXS-CORE-SW \u2192 staff / printers", "Access VLAN 20", "1 Gbps copper", "DHCP and static printers"),
    ("NXS-ENG-SW \u2192 engineering PCs", "Access VLAN 30", "1 Gbps copper", "DHCP endpoints"),
]

SECURITY_CONTROLS = [
    ("VLAN segmentation", "Separate broadcast domains for servers, engineering, staff, guest and management"),
    ("Guest ACL", "GUEST-IN denies 192.168.10.0/24; DHCP and internet are permitted"),
    ("Management ACL", "STAFF-MGMT denies VLAN 20/30 hosts access to 192.168.10.192/28"),
    ("VTY access", "SSH version 2 only; VTY access-class permits the management subnet only"),
    ("Port security", "Maximum 1 MAC on access ports; violation restrict; sticky MAC addresses"),
    ("STP protection", "RSTP, core root primary, PortFast and BPDU Guard on edge ports"),
    ("DHCP snooping", "Enabled on VLAN 20/30/40; router and uplink ports trusted"),
    ("Dynamic ARP inspection", "Enabled on VLAN 20/30/40; uplink ports trusted"),
    ("Unused ports", "Administratively shut down and placed in an unused VLAN"),
    ("Wireless", "WPA2-AES; guest client isolation; management SSID not exposed"),
]

BOM = [
    # category, item, specification, qty, unit price (Rs.)
    ("Active equipment", "Cisco 2911-SEC/K9 router", "2 x GE, security licence, 512 MB DRAM, refurbished with 3-year warranty", 1, 42000),
    ("Active equipment", "Cisco Catalyst 2960X-48FPD-L", "48 x 1 Gbps PoE+, 4 x SFP, 740 W PoE budget", 1, 95000),
    ("Active equipment", "Cisco Catalyst 2960X-24TS-L", "24 x 1 Gbps, 2 x SFP, 1 RU", 1, 48000),
    ("Active equipment", "Cisco Aironet 1832I-B-K9", "802.11ac Wave 2, 2x2 MU-MIMO, PoE", 3, 18500),
    ("Active equipment", "1000BASE-SX SFP module", "LC duplex, 850 nm, OM3 multimode", 4, 3500),
    ("Cabling & passive", "12U wall-mount rack", "600 mm depth, lockable glass door, fan tray", 1, 12000),
    ("Cabling & passive", "9U wall-mount rack", "Engineering closet, lockable", 1, 6500),
    ("Cabling & passive", "24-port Cat6 patch panel", "1U, 568B, rear cable management bar", 2, 3500),
    ("Cabling & passive", "Cat6 UTP cable, 305 m box", "23 AWG solid copper, 550 MHz, LSZH", 5, 6800),
    ("Cabling & passive", "Cat6 keystone jack and faceplate", "Shuttered RJ45, 568B termination, label window", 50, 450),
    ("Cabling & passive", "RJ45 plugs and boots", "Cat6 strain-relief boots, pack of 100", 2, 1500),
    ("Cabling & passive", "1U cable manager", "Horizontal finger duct with cover", 2, 2000),
    ("Cabling & passive", "OM3 LC-LC fibre patch cord, 3 m", "Duplex multimode, 50/125 \u00b5m", 2, 2500),
    ("Cabling & passive", "Cat6 patch cords, 1 m / 3 m", "Moulded, 568B, mixed lengths", 96, 250),
    ("Cabling & passive", "Cable tray, conduit and trunking", "Ceiling tray, PVC trunking, clamps and fixings", 1, 30000),
    ("Racks & power", "3 kVA online UPS", "Double conversion, 30 min backup at 1.5 kW load", 1, 32000),
    ("Racks & power", "1 kVA line-interactive UPS", "Engineering closet, 20 min backup", 1, 12000),
    ("Racks & power", "Electrical points and earthing", "Dedicated circuits, RCBO, earth pit connection", 1, 15000),
    ("Installation & services", "Cabling, termination and testing", "48 drops, labelling, Fluke-style certification", 48, 900),
    ("Installation & services", "Configuration and commissioning", "Router, switches, APs, VLANs, ACLs, testing", 1, 25000),
    ("Installation & services", "ISP installation and activation", "Fibre termination and first-month setup", 1, 5000),
    ("Installation & services", "Documentation and handover training", "As-built drawings, IP plan, 2-hour training", 1, 8000),
]

OPEX = [
    ("ISP business fibre 100 Mbps", 12000, "Per month"),
    ("Annual maintenance contract", 36920, "8% of active and passive equipment"),
    ("Electricity (network equipment)", 12000, "Estimated annual consumption"),
]

CONTINGENCY_RATE = 0.05
