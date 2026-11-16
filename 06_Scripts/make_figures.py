"""Generate the floor plan, topology, VLSM map and cost figure."""

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import (Circle, Ellipse, FancyArrowPatch,
                                FancyBboxPatch, Patch, Rectangle)
import matplotlib.patheffects as pe

import project_data as P

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.linewidth": 0.8,
    "savefig.facecolor": "white",
})

NAVY = "#1F3864"
BLUE = "#2F5597"
LIGHT_BLUE = "#D9E2F3"
TEAL = "#0F766E"
GREEN = "#2E7D32"
ORANGE = "#C2410C"
RED = "#B91C1C"
PURPLE = "#6B21A8"
GREY = "#4B5563"
LIGHT_GREY = "#F3F4F6"
MAROON = "#7B1E2B"


def save(fig, path, dpi=220):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", path)


# ---------------------------------------------------------------------------
# 1. Site survey / floor plan
# ---------------------------------------------------------------------------

ROOM_FILL = {
    "Engineering": "#E8F0FE",
    "Reception": "#FFF4E5",
    "Conference": "#FFF4E5",
    "Admin": "#EAF5EA",
    "Management": "#F3E8FF",
    "Server": "#FDE8E8",
    "Store": "#F3F4F6",
    "Pantry": "#F3F4F6",
    "Breakout": "#F3F4F6",
    "Restroom": "#F3F4F6",
}


def room_color(name):
    for key, colour in ROOM_FILL.items():
        if key.lower() in name.lower():
            return colour
    return "#FFFFFF"


def desk(ax, x, y, w=2.1, h=1.1):
    ax.add_patch(Rectangle((x, y), w, h, facecolor="white",
                           edgecolor="#6B7280", linewidth=0.7, zorder=5))
    ax.plot([x + 0.25, x + w - 0.25], [y + h - 0.3, y + h - 0.3],
            color="#9CA3AF", linewidth=0.7, zorder=6)


def make_floor_plan():
    fig, ax = plt.subplots(figsize=(13.2, 8.0))
    ax.set_xlim(-2.5, 74.5)
    ax.set_ylim(-4.2, 44.0)
    ax.set_aspect("equal")
    ax.axis("off")

    outer = Rectangle((0, 0), 70, 40, facecolor="white",
                      edgecolor="#111827", linewidth=3.0, zorder=1)
    ax.add_patch(outer)

    # Corridor
    ax.add_patch(Rectangle((0, 14), 70, 4, facecolor="#F9FAFB",
                           edgecolor="#9CA3AF", linewidth=1.0, zorder=2))
    ax.text(35, 16, "CENTRAL CORRIDOR  \u2022  4 ft wide",
            ha="center", va="center", fontsize=8.5, color=GREY,
            fontweight="bold", zorder=8)

    # Rooms
    for room in P.ROOMS:
        x, y, w, h = room["x"], room["y"], room["w"], room["h"]
        ax.add_patch(Rectangle(
            (x, y), w, h, facecolor=room_color(room["name"]),
            edgecolor="#374151", linewidth=1.25, zorder=4))

        name = room["name"]
        label = name
        if name == "Admin / HR / Finance":
            label = "ADMIN / HR / FINANCE"
        else:
            label = label.upper()

        # Keep the room label in the upper-left, clear of furniture.
        tx, ty = x + 1.0, y + h - 1.6
        if name == "Reception":
            tx, ty = x + 1.0, y + h - 1.8
        if name == "Conference":
            tx, ty = x + 1.0, y + h - 1.8
        if name == "Server room":
            tx, ty = x + 0.8, y + h - 1.5
        ax.text(tx, ty, label, ha="left", va="top", fontsize=8.2,
                fontweight="bold", color=NAVY, zorder=9)

        dims = f"{w} \u00d7 {h} ft"
        if room["drops"]:
            dims += f"  \u2022  {room['drops']} drops"
        ax.text(tx, ty - 1.15, dims, ha="left", va="top", fontsize=6.8,
                color=GREY, zorder=9)
    # Engineering desks: 4 rows x 6 columns = 24 seats
    for row in range(4):
        for col in range(6):
            desk(ax, 1.6 + col * 4.65, 20.2 + row * 3.7)

    # Admin / HR / Finance desks: 8 seats
    for row in range(2):
        for col in range(4):
            desk(ax, 33.5 + col * 4.8, 4.0 + row * 4.5)

    # Management desks: 4 seats
    for row in range(2):
        for col in range(2):
            desk(ax, 56.2 + col * 6.5, 29.8 + row * 3.6, 2.3, 1.2)

    # Reception desks
    desk(ax, 2.0, 4.2, 2.3, 1.2)
    desk(ax, 7.0, 4.2, 2.3, 1.2)

    # Conference table
    ax.add_patch(FancyBboxPatch((16.4, 3.0), 11.0, 5.0,
                                boxstyle="round,pad=0.15,rounding_size=0.8",
                                facecolor="#FFFFFF", edgecolor="#9CA3AF",
                                linewidth=1.0, zorder=6))
    ax.text(21.9, 5.5, "CONFERENCE TABLE", ha="center", va="center",
            fontsize=6.7, color=GREY, zorder=7)

    # Server rack
    ax.add_patch(Rectangle((31.0, 29.4), 5.5, 6.2, facecolor="#FFFFFF",
                           edgecolor=RED, linewidth=1.3, zorder=6))
    for yy in (30.2, 31.4, 32.6, 33.8, 35.0):
        ax.plot([31.3, 36.2], [yy, yy], color="#D1D5DB", linewidth=0.8, zorder=7)
    ax.text(33.75, 33.1, "RACK\nGW + CORE\nPATCH\nUPS", ha="center",
            va="center", fontsize=6.0, color=RED, fontweight="bold", zorder=8)

    # Ceiling cable tray and ISP fibre path
    ax.plot([1.5, 68.5], [16.9, 16.9], color=ORANGE, linewidth=4.2,
            alpha=0.45, solid_capstyle="round", zorder=7)
    ax.plot([1.5, 68.5], [16.9, 16.9], color=ORANGE, linewidth=0.8,
            linestyle=(0, (2, 3)), zorder=8)
    ax.text(51.0, 15.20, "CEILING CABLE TRAY (Cat6)", ha="center",
            va="center", fontsize=6.4, color=ORANGE, fontweight="bold",
            zorder=9)

    ax.plot([0.55, 0.55], [2.4, 16.9], color=RED, linewidth=1.3,
            linestyle=(0, (3, 2)), zorder=8)
    ax.plot([0.55, 33.75], [16.9, 16.9], color=RED, linewidth=1.3,
            linestyle=(0, (3, 2)), zorder=8)
    ax.plot([33.75, 33.75], [16.9, 29.4], color=RED, linewidth=1.3,
            linestyle=(0, (3, 2)), zorder=8)
    ax.text(3.0, 2.05, "ISP fibre entry", ha="left", va="center",
            fontsize=6.6, color=RED, fontweight="bold", zorder=10)

    # AP markers
    ap_labels = {
        "AP-ENG": (17.2, 29.7, "AP1"),
        "AP-STAFF": (24.5, 8.8, "AP2"),
        "AP-MGMT": (67.0, 34.0, "AP3"),
    }
    for name, (x, y, where) in P.AP_POSITIONS.items():
        ax.scatter([x], [y], s=190, marker="*", color=RED,
                   edgecolor="white", linewidth=0.8, zorder=12)
        lx, ly, label = ap_labels[name]
        ax.text(lx, ly, label, ha="center", va="center", fontsize=6.8,
                color="white", fontweight="bold", zorder=13,
                bbox=dict(boxstyle="round,pad=0.20", facecolor=RED,
                          edgecolor="none"))

    # Door openings on the corridor side
    for x in (5.0, 18.0, 38.0, 60.0):
        ax.plot([x, x + 2.2], [14, 14], color="#FFFFFF", linewidth=4.0, zorder=10)
        ax.plot([x, x + 2.2], [18, 18], color="#FFFFFF", linewidth=4.0, zorder=10)

    # North arrow and scale
    ax.annotate("", xy=(72.0, 39.0), xytext=(72.0, 35.5),
                arrowprops=dict(arrowstyle="-|>", color=NAVY, linewidth=1.4),
                zorder=10)
    ax.text(72.0, 39.5, "N", ha="center", va="bottom", fontsize=9,
            fontweight="bold", color=NAVY)
    ax.plot([57.0, 67.0], [-2.2, -2.2], color="#111827", linewidth=2.0)
    ax.plot([57.0, 57.0], [-2.6, -1.8], color="#111827", linewidth=1.0)
    ax.plot([67.0, 67.0], [-2.6, -1.8], color="#111827", linewidth=1.0)
    ax.text(62.0, -1.6, "10 ft", ha="center", va="bottom", fontsize=7,
            color=GREY)

    handles = [
        Line2D([0], [0], marker="*", color="none", markerfacecolor=RED,
               markeredgecolor="white", markersize=12, label="Ceiling AP (AP1\u2013AP3)"),
        Patch(facecolor="#FDE8E8", edgecolor=RED, label="Server / rack"),
        Line2D([0], [0], color=ORANGE, linewidth=3, label="Cable tray"),
        Line2D([0], [0], color=RED, linewidth=1.3, linestyle="--",
               label="ISP fibre"),
        Line2D([0], [0], color=BLUE, linewidth=1.0, linestyle=(0, (4, 3)),
               label="Wi-Fi target \u221267 dBm"),
    ]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, -0.17),
              ncol=5, frameon=False, fontsize=7.2, handlelength=2.0,
              columnspacing=1.6, handletextpad=0.6)

    fig.suptitle("Site Survey and Device Placement Plan",
                 fontsize=15.5, fontweight="bold", color=NAVY, y=0.985)
    fig.text(0.5, 0.945,
             "2nd Floor, Wing B, Sunrise Business Park, Baner, Pune  \u2022  "
             "70 ft \u00d7 40 ft  \u2022  48 Cat6 drops  \u2022  3 ceiling APs",
             ha="center", va="top", fontsize=8.6, color=GREY)

    save(fig, P.PROJECT_ROOT / "01_Site_Survey" / "floor_plan.png")


# ---------------------------------------------------------------------------
# 2. Logical topology
# ---------------------------------------------------------------------------

def rbox(ax, cx, cy, w, h, text, fc="#FFFFFF", ec=NAVY, fs=8.0,
         bold=False, text_color="#111827", lw=1.3, z=5):
    p = FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                       boxstyle="round,pad=0.04,rounding_size=0.10",
                       facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z)
    ax.add_patch(p)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
            color=text_color, fontweight="bold" if bold else "normal",
            linespacing=1.22, zorder=z + 1)
    return p


def edge(ax, p1, p2, color=NAVY, lw=1.8, style="-", z=3):
    ax.add_patch(FancyArrowPatch(
        p1, p2, arrowstyle="-", linewidth=lw, color=color,
        linestyle=style, zorder=z, shrinkA=2, shrinkB=2))


def edge_label(ax, x, y, text, color=GREY, fs=6.7, ha="center", va="center"):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color, zorder=9,
            bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                      edgecolor="none"))


def make_topology():
    fig, ax = plt.subplots(figsize=(13.2, 8.6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0.3, 10.2)
    ax.axis("off")

    # Internet cloud
    ax.add_patch(Ellipse((7.0, 9.55), 2.5, 1.05, facecolor="#E5E7EB",
                         edgecolor=GREY, linewidth=1.2, zorder=4))
    ax.add_patch(Ellipse((6.3, 9.7), 1.1, 0.75, facecolor="#E5E7EB",
                         edgecolor=GREY, linewidth=1.0, zorder=4))
    ax.add_patch(Ellipse((7.7, 9.7), 1.1, 0.75, facecolor="#E5E7EB",
                         edgecolor=GREY, linewidth=1.0, zorder=4))
    ax.text(7.0, 9.62, "INTERNET\n8.8.8.8", ha="center", va="center",
            fontsize=7.9, fontweight="bold", color=GREY, zorder=6)

    # Devices
    rbox(ax, 7.0, 8.35, 2.6, 0.72, "ISP-RTR\n203.0.113.1", fc="#F3F4F6",
         ec=GREY, fs=7.8)
    rbox(ax, 7.0, 7.05, 3.0, 0.82,
         "NXS-GW  \u2022  Cisco 2911\nNAT/PAT  \u2022  DHCP  \u2022  ACL",
         fc="#FDE8E8", ec=MAROON, fs=7.7, bold=False)
    rbox(ax, 7.0, 5.55, 3.0, 0.82,
         "NXS-CORE-SW  \u2022  2960X-48FPD-L\nSTP root  \u2022  PoE+  \u2022  802.1Q",
         fc="#E8F0FE", ec=BLUE, fs=7.7)
    rbox(ax, 2.05, 5.55, 2.55, 0.72,
         "MGMT  \u2022  VLAN 99\n192.168.10.192/28",
         fc="#F3E8FF", ec=PURPLE, fs=7.6)
    rbox(ax, 1.90, 3.70, 2.85, 0.92,
         "SERVERS  \u2022  VLAN 10\n192.168.10.0/26\nDNS .10  \u2022  FILE .11  \u2022  ERP .12",
         fc="#FDE8E8", ec=RED, fs=7.1)
    rbox(ax, 5.05, 3.70, 2.85, 0.92,
         "STAFF  \u2022  VLAN 20\n192.168.10.128/27\nDHCP  \u2022  24 clients",
         fc="#EAF5EA", ec=GREEN, fs=7.1)
    rbox(ax, 8.65, 3.85, 2.55, 0.95,
         "3 \u00d7 CEILING APs\nNEXA-ENG 30  \u2022  STAFF 20\nGUEST 40  \u2022  mgmt 99",
         fc="#F3F4F6", ec=GREY, fs=6.4)
    rbox(ax, 8.30, 2.40, 2.40, 0.78,
         "GUEST WI-FI  \u2022  VLAN 40\n192.168.10.160/27  \u2022  isolated",
         fc="#FFF4E5", ec=ORANGE, fs=7.1)
    rbox(ax, 11.35, 5.55, 2.75, 0.82,
         "NXS-ENG-SW  \u2022  2960X-24TS-L\nVLAN 30 access  \u2022  RSTP",
         fc="#E8F0FE", ec=BLUE, fs=7.5)
    rbox(ax, 11.35, 3.70, 2.75, 0.92,
         "ENGINEERING  \u2022  VLAN 30\n192.168.10.64/26\nDHCP  \u2022  28 clients",
         fc="#E8F0FE", ec=BLUE, fs=7.1)

    # WAN and routed core links
    edge(ax, (7.0, 9.05), (7.0, 8.71), color=RED, lw=2.0)
    edge(ax, (7.0, 8.0), (7.0, 7.46), color=RED, lw=2.0)
    edge(ax, (7.0, 6.64), (7.0, 5.96), color=NAVY, lw=2.2)
    edge_label(ax, 5.45, 8.85, "WAN 203.0.113.0/30\nNAT/PAT", color=RED, fs=6.6, ha="right")
    edge_label(ax, 8.55, 6.25, "802.1Q trunk\nG0/0.10\u2013.99", color=NAVY, fs=6.4)

    # Core to distribution / endpoints
    edge(ax, (5.5, 5.55), (3.33, 5.55), color=PURPLE, lw=1.6, style=(0, (4, 2)))
    edge_label(ax, 4.42, 5.78, "VLAN 99 SSH", color=PURPLE, fs=6.3)

    edge(ax, (5.70, 5.18), (3.00, 4.17), color=RED, lw=1.6)
    edge_label(ax, 4.15, 4.82, "VLAN 10", color=RED, fs=6.4)

    edge(ax, (6.35, 5.17), (5.70, 4.17), color=GREEN, lw=1.6)
    edge_label(ax, 5.45, 4.78, "VLAN 20", color=GREEN, fs=6.4)

    edge(ax, (8.05, 5.18), (8.65, 4.28), color=GREY, lw=1.6)
    edge_label(ax, 8.95, 4.85, "trunk\nVLAN 20/40", color=GREY, fs=6.2)

    edge(ax, (8.5, 5.55), (9.97, 5.55), color=NAVY, lw=2.2)
    edge_label(ax, 9.23, 5.85, "Po1  2\u00d71G LACP", color=NAVY, fs=6.4)

    edge(ax, (11.35, 5.13), (11.35, 4.17), color=NAVY, lw=1.8)
    edge_label(ax, 11.95, 4.65, "VLAN 30", color=BLUE, fs=6.4)

    # Wireless links
    edge(ax, (7.55, 4.20), (6.95, 4.20), color=ORANGE, lw=1.5,
         style=(0, (4, 2)))
    edge(ax, (8.65, 3.42), (8.65, 2.80), color=ORANGE, lw=1.5,
         style=(0, (4, 2)))
    edge_label(ax, 7.28, 4.43, "NEXA-STAFF\nVLAN 20", color=ORANGE, fs=6.0)
    edge_label(ax, 7.65, 3.08, "NEXA-GUEST\nVLAN 40", color=ORANGE, fs=6.0, ha="right")

    # Simple legend
    handles = [
        Line2D([0], [0], color=RED, lw=2.0, label="WAN / NAT outside"),
        Line2D([0], [0], color=NAVY, lw=2.0, label="802.1Q trunk"),
        Line2D([0], [0], color=GREY, lw=1.6, label="Access link"),
        Line2D([0], [0], color=ORANGE, lw=1.5, linestyle="--",
               label="Wireless SSID"),
        Patch(facecolor="#E8F0FE", edgecolor=BLUE, label="User VLAN"),
        Patch(facecolor="#FDE8E8", edgecolor=RED, label="Server VLAN"),
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.10),
              ncol=6, frameon=False, fontsize=6.7, handlelength=2.0,
              columnspacing=1.2, handletextpad=0.5)

    fig.suptitle("Logical Network Topology \u2014 NexaSoft Office LAN",
                 fontsize=15.5, fontweight="bold", color=NAVY, y=0.985)
    fig.text(0.5, 0.948,
             "VLSM 192.168.10.0/24  \u2022  router-on-a-stick  \u2022  "
             "centralised DHCP/DNS  \u2022  NAT/PAT  \u2022  VLAN isolation",
             ha="center", va="top", fontsize=8.3, color=GREY)
    fig.text(0.5, 0.918,
             "Wired: 48 Cat6 drops  |  Wireless: 24 concurrent clients  |  "
             "Core-to-access: 2 \u00d7 1 Gbps OM3 fibre",
             ha="center", va="top", fontsize=7.7, color=GREY)

    save(fig, P.PROJECT_ROOT / "02_Network_Design" / "topology.png")


# ---------------------------------------------------------------------------
# 3. VLSM byte map
# ---------------------------------------------------------------------------

def make_vlan_map():
    fig, ax = plt.subplots(figsize=(14.0, 4.6))
    ax.set_xlim(-0.5, 16.5)
    ax.set_ylim(-0.35, 2.75)
    ax.axis("off")

    colours = {
        10: "#2F5597",
        30: "#0F766E",
        20: "#2E7D32",
        40: "#C2410C",
        99: "#6B21A8",
        "R": "#D1D5DB",
    }
    blocks = [
        (10, "VLAN 10\nServers\n/26", 0, 4),
        (30, "VLAN 30\nEngineering\n/26", 4, 4),
        (20, "VLAN 20\nStaff\n/27", 8, 2),
        (40, "VLAN 40\nGuest\n/27", 10, 2),
        (99, "VLAN 99\nMgmt\n/28", 12, 1),
        ("R", "Reserved\nfor growth", 13, 3),
    ]

    for key, label, start, span in blocks:
        ax.add_patch(Rectangle((start, 0.75), span, 0.70,
                               facecolor=colours[key], edgecolor="white",
                               linewidth=2.0))
        ax.text(start + span / 2, 1.10, str(key) if key != "R" else "R",
                ha="center", va="center", fontsize=14 if key != "R" else 11,
                color="white", fontweight="bold")
        first = start * 16
        last = (start + span) * 16 - 1
        ax.text(start + span / 2, 1.62, f"{label}\n.{first}\u2013.{last}",
                ha="center", va="bottom", fontsize=7.1, color=NAVY,
                fontweight="bold", linespacing=1.12)

    # Address ruler
    for i in range(0, 17):
        x = i
        ax.plot([x, x], [0.68, 0.60], color=GREY, linewidth=0.6)
        if i % 4 == 0:
            ax.text(x, 0.48, str(i * 16), ha="center", va="top",
                    fontsize=6.8, color=GREY)

    ax.text(8.0, -0.02,
            "One cell = 16 IPv4 addresses  \u2022  contiguous /24 block  \u2022  "
            "summary route 192.168.10.0/24",
            ha="center", va="top", fontsize=7.6, color=GREY)

    # Gateways / service notes
    ax.text(2.0, 2.35, "GW .1  \u2022  servers .10\u2013.12",
            ha="center", va="center", fontsize=6.7, color=RED)
    ax.text(6.0, 2.35, "GW .65  \u2022  DHCP .66\u2013.124",
            ha="center", va="center", fontsize=6.7, color=TEAL)
    ax.text(9.0, 2.35, "GW .129\nDHCP .132\u2013.158",
            ha="center", va="center", fontsize=6.5, color=GREEN)
    ax.text(11.0, 2.35, "GW .161\nDHCP .162\u2013.190",
            ha="center", va="center", fontsize=6.5, color=ORANGE)
    ax.text(12.5, 2.35, "GW .193", ha="center", va="center",
            fontsize=6.5, color=PURPLE)
    ax.text(14.5, 2.35, "No allocation", ha="center", va="center",
            fontsize=6.7, color=GREY)

    fig.suptitle("VLSM Allocation of 192.168.10.0/24",
                 fontsize=14.5, fontweight="bold", color=NAVY, y=1.00)
    save(fig, P.PROJECT_ROOT / "02_Network_Design" / "vlan_map.png")


# ---------------------------------------------------------------------------
# 4. Cost breakdown
# ---------------------------------------------------------------------------

def make_cost_figure():
    category_totals = Counter()
    for category, _, _, qty, unit in P.BOM:
        category_totals[category] += qty * unit
    subtotal = sum(category_totals.values())
    contingency = round(subtotal * P.CONTINGENCY_RATE)
    category_totals["Contingency (5%)"] = contingency
    total = subtotal + contingency

    labels = list(category_totals)
    values = [category_totals[k] for k in labels]
    colours = ["#2F5597", "#0F766E", "#C2410C", "#7B1E2B", "#9CA3AF"]

    fig, ax = plt.subplots(figsize=(9.6, 6.2))
    wedges, texts, autotexts = ax.pie(
        values, colors=colours, startangle=90, counterclock=False,
        autopct=lambda pct: f"{pct:.1f}%", pctdistance=0.80,
        wedgeprops=dict(width=0.40, edgecolor="white", linewidth=2.0),
        textprops=dict(fontsize=8.5, color="#111827"))
    for autotext in autotexts:
        autotext.set_fontsize(8.0)
        autotext.set_fontweight("bold")
        autotext.set_color("white")

    ax.text(0, 0.10, "CapEx", ha="center", va="center", fontsize=11,
            color=GREY, fontweight="bold")
    ax.text(0, -0.08, f"Rs. {total/100000:.2f} lakh", ha="center",
            va="center", fontsize=14, color=NAVY, fontweight="bold")
    ax.text(0, -0.25, f"Rs. {total:,}", ha="center", va="center",
            fontsize=8, color=GREY)

    legend_labels = [f"{l}  \u2014  Rs. {v/100000:.2f} lakh"
                     for l, v in zip(labels, values)]
    ax.legend(wedges, legend_labels, loc="center left",
              bbox_to_anchor=(0.98, 0.5), frameon=False, fontsize=8.4,
              title="Cost category", title_fontsize=9.0)
    ax.set_aspect("equal")
    fig.suptitle("Project Cost Breakdown (including 5% contingency)",
                 fontsize=13.5, fontweight="bold", color=NAVY, y=0.98)
    save(fig, P.PROJECT_ROOT / "05_Cost_Analysis" / "cost_breakdown.png")


if __name__ == "__main__":
    make_floor_plan()
    make_topology()
    make_vlan_map()
    make_cost_figure()
