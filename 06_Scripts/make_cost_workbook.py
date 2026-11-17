from collections import Counter
from pathlib import Path
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "05_Cost_Analysis" / "BoM_and_Cost.xlsx"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import project_data as P


NAVY = "1F3864"
BLUE = "2F5597"
LIGHT_BLUE = "D9E2F3"
PALE_BLUE = "EEF3FA"
LIGHT_GREY = "F3F4F6"
GREEN = "E2EFDA"
WHITE = "FFFFFF"
DARK = "111827"
ORANGE = "C2410C"


def money(value):
    return f"Rs. {value:,.0f}"


def style_title(ws, row, columns, text, subtitle):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=columns)
    cell = ws.cell(row=row, column=1, value=text)
    cell.font = Font(name="Calibri", size=15, bold=True, color=WHITE)
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row].height = 27
    ws.merge_cells(start_row=row + 1, start_column=1,
                   end_row=row + 1, end_column=columns)
    sub = ws.cell(row=row + 1, column=1, value=subtitle)
    sub.font = Font(name="Calibri", size=9, italic=True, color="4B5563")
    sub.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
    sub.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row + 1].height = 18


def header_row(ws, row, headers):
    for col, text in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=text)
        cell.font = Font(name="Calibri", size=10, bold=True, color=WHITE)
        cell.fill = PatternFill("solid", fgColor=BLUE)
        cell.alignment = Alignment(horizontal="center", vertical="center",
                                   wrap_text=True)
        cell.border = Border(bottom=Side(style="thin", color=WHITE))
    ws.row_dimensions[row].height = 24


def write_bom(ws):
    style_title(ws, 1, 7, "NexaSoft Office LAN - Bill of Materials",
                "Budgetary CapEx estimate for 48 wired drops and 24 wireless clients | "
                f"{P.TEAM_NAMES} | 2026-27")
    headers = ["#", "Category", "Item", "Specification", "Qty",
               "Unit Rate (Rs.)", "Amount (Rs.)"]
    header_row(ws, 4, headers)
    thin = Side(style="thin", color="D1D5DB")
    start = 5
    for offset, (category, item, spec, qty, unit) in enumerate(P.BOM):
        row = start + offset
        values = [offset + 1, category, item, spec, qty, unit, qty * unit]
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.font = Font(name="Calibri", size=9, color=DARK)
            cell.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            cell.alignment = Alignment(vertical="top", wrap_text=col in (2, 3, 4))
            if col in (6, 7):
                cell.number_format = '"Rs. "#,##0'
                cell.alignment = Alignment(horizontal="right", vertical="top")
            if col == 5:
                cell.alignment = Alignment(horizontal="center", vertical="top")
            if col == 1:
                cell.alignment = Alignment(horizontal="center", vertical="top")
            if offset % 2:
                cell.fill = PatternFill("solid", fgColor=PALE_BLUE)
    total_row = start + len(P.BOM)
    subtotal = sum(qty * unit for _, _, _, qty, unit in P.BOM)
    ws.merge_cells(start_row=total_row, start_column=3,
                   end_row=total_row, end_column=5)
    ws.cell(row=total_row, column=3, value="Subtotal")
    ws.cell(row=total_row, column=7, value=subtotal)
    ws.cell(row=total_row, column=3).font = Font(bold=True, color=WHITE)
    ws.cell(row=total_row, column=7).font = Font(bold=True, color=WHITE)
    ws.cell(row=total_row, column=3).alignment = Alignment(horizontal="right")
    ws.cell(row=total_row, column=7).number_format = '"Rs. "#,##0'
    ws.cell(row=total_row, column=7).alignment = Alignment(horizontal="right")
    for col in range(1, 8):
        cell = ws.cell(row=total_row, column=col)
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.border = Border(top=Side(style="medium", color=NAVY))
    ws.row_dimensions[total_row].height = 23
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:G{total_row - 1}"
    widths = {1: 5, 2: 20, 3: 34, 4: 55, 5: 7, 6: 16, 7: 16}
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "4:4"


def write_summary(ws, category_totals, subtotal, contingency, total):
    style_title(ws, 1, 4, "Cost Summary and Key Indicators",
                "All amounts are budgetary, in Indian rupees, including applicable taxes")
    header_row(ws, 4, ["Cost element", "Amount (Rs.)", "Share", "Notes"])
    rows = []
    for category in ("Active equipment", "Cabling & passive", "Racks & power",
                     "Installation & services"):
        value = category_totals[category]
        rows.append((category, value, value / subtotal,
                     "Equipment, materials and services"))
    rows.append(("Subtotal", subtotal, 1.0, "Before contingency"))
    rows.append(("Contingency (5%)", contingency, contingency / subtotal,
                 "Scope and price variation buffer"))
    rows.append(("Total CapEx", total, 1.0, "Within Rs. 6.00 lakh cap"))
    for offset, (label, value, share, note) in enumerate(rows, start=5):
        ws.cell(row=offset, column=1, value=label).font = Font(
            bold=label in ("Subtotal", "Total CapEx"), color=DARK)
        ws.cell(row=offset, column=2, value=value).number_format = '"Rs. "#,##0'
        ws.cell(row=offset, column=3, value=share).number_format = "0.0%"
        ws.cell(row=offset, column=4, value=note).font = Font(size=9, color="4B5563")
        for col in range(1, 5):
            cell = ws.cell(row=offset, column=col)
            cell.border = Border(bottom=Side(style="hair", color="D1D5DB"))
            cell.alignment = Alignment(vertical="center",
                                       horizontal="right" if col in (2, 3) else "left")
        if label == "Total CapEx":
            for col in range(1, 5):
                ws.cell(row=offset, column=col).fill = PatternFill(
                    "solid", fgColor=GREEN)
                ws.cell(row=offset, column=col).font = Font(bold=True, color=NAVY)
    kpi_row = 14
    ws.cell(row=kpi_row, column=1, value="Key indicators").font = Font(
        bold=True, size=11, color=NAVY)
    kpis = [
        ("CapEx per wired drop", total / 48),
        ("CapEx per connected client", total / 64),
        ("Wired drop count", 48),
        ("Dynamic DHCP leases", 64),
    ]
    for offset, (label, value) in enumerate(kpis, start=kpi_row + 1):
        ws.cell(row=offset, column=1, value=label).font = Font(size=9)
        cell = ws.cell(row=offset, column=2, value=value)
        cell.font = Font(size=9, bold=True)
        cell.number_format = '"Rs. "#,##0' if isinstance(value, float) else "0"
        cell.alignment = Alignment(horizontal="right")
    widths = {1: 27, 2: 17, 3: 10, 4: 48}
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.sheet_view.showGridLines = False


def write_tco(ws, capex):
    annual_isp = next(value for label, value, unit in P.OPEX
                      if label.startswith("ISP")) * 12
    annual_amc = next(value for label, value, unit in P.OPEX
                      if "maintenance" in label.lower())
    annual_power = next(value for label, value, unit in P.OPEX
                        if "electricity" in label.lower())
    annual_opex = annual_isp + annual_amc + annual_power
    total_3y = capex + annual_opex * 3
    style_title(ws, 1, 4, "Three-Year Total Cost of Ownership",
                "CapEx plus recurring ISP, AMC and electricity estimates")
    header_row(ws, 4, ["Cost item", "Year 1 (Rs.)", "Years 2-3 each (Rs.)",
                       "Basis"])
    rows = [
        ("Capital expenditure", capex, 0, "One-time project CapEx"),
        ("ISP business fibre", annual_isp, annual_isp, "Rs. 12,000 per month"),
        ("Annual maintenance contract", annual_amc, annual_amc,
         "8% of active, passive and rack equipment"),
        ("Electricity", annual_power, annual_power,
         "Estimated annual consumption"),
    ]
    for offset, (label, first, recurring, basis) in enumerate(rows, start=5):
        ws.cell(row=offset, column=1, value=label)
        ws.cell(row=offset, column=2, value=first).number_format = '"Rs. "#,##0'
        ws.cell(row=offset, column=3, value=recurring).number_format = '"Rs. "#,##0'
        ws.cell(row=offset, column=4, value=basis).font = Font(size=9, color="4B5563")
        for col in range(1, 5):
            cell = ws.cell(row=offset, column=col)
            cell.border = Border(bottom=Side(style="hair", color="D1D5DB"))
            cell.alignment = Alignment(vertical="center",
                                       horizontal="right" if col in (2, 3) else "left")
    total_row = 10
    labels = [
        ("Annual recurring cost", annual_isp + annual_amc + annual_power),
        ("Year 1 total", capex + annual_isp + annual_amc + annual_power),
        ("Three-year total cost of ownership", total_3y),
    ]
    for offset, (label, value) in enumerate(labels, start=total_row):
        ws.cell(row=offset, column=1, value=label).font = Font(bold=True, color=NAVY)
        cell = ws.cell(row=offset, column=2, value=value)
        cell.number_format = '"Rs. "#,##0'
        cell.font = Font(bold=True, color=NAVY)
        cell.alignment = Alignment(horizontal="right")
        for col in (1, 2):
            ws.cell(row=offset, column=col).fill = PatternFill(
                "solid", fgColor=GREEN if offset == total_row + 2 else LIGHT_BLUE)
    ws.merge_cells("A14:D14")
    note = ws["A14"]
    note.value = ("TCO excludes client devices, ISP installation already included in CapEx, "
                  "and any future switch/AP replacement beyond year 3.")
    note.font = Font(size=8, italic=True, color="4B5563")
    note.alignment = Alignment(wrap_text=True, vertical="top")
    widths = {1: 34, 2: 20, 3: 24, 4: 46}
    for col, width in widths.items():
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.sheet_view.showGridLines = False


def write_assumptions(ws):
    style_title(ws, 1, 2, "Estimation Assumptions",
                "Use these assumptions when comparing vendor quotations")
    assumptions = [
        ("Site and scope", "2,800 sq ft office; 48 Cat6 drops; 3 ceiling APs; 24 concurrent wireless clients"),
        ("Addressing", "One contiguous 192.168.10.0/24 block using VLSM; 64 dynamic DHCP leases"),
        ("Switching", "Cisco 2960X core and access switches; 2 x 1 Gbps OM3 fibre LACP uplink"),
        ("Routing and security", "Cisco 2911 router-on-a-stick; NAT/PAT; guest and management ACLs"),
        ("Pricing basis", "Indicative Indian market prices; vendor quotes and GST to be verified"),
        ("Contingency", "5% of subtotal for scope variation and price movement"),
        ("Warranty", "Three-year warranty on active equipment as assumed in the BoM"),
        ("Exclusions", "Client laptops/phones, civil work and equipment replacement beyond year 3"),
        ("AMC", "8% of active, passive and rack equipment per year"),
        ("Electricity", "Estimated annual network equipment consumption at institutional tariff"),
    ]
    header_row(ws, 4, ["Assumption", "Value / basis"])
    for offset, (label, value) in enumerate(assumptions, start=5):
        ws.cell(row=offset, column=1, value=label).font = Font(bold=True, size=9)
        ws.cell(row=offset, column=2, value=value).font = Font(size=9)
        ws.cell(row=offset, column=2).alignment = Alignment(wrap_text=True,
                                                            vertical="top")
        for col in (1, 2):
            ws.cell(row=offset, column=col).border = Border(
                bottom=Side(style="hair", color="D1D5DB"))
        ws.row_dimensions[offset].height = 31
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 88
    ws.sheet_view.showGridLines = False


def main():
    category_totals = Counter()
    for category, _, _, qty, unit in P.BOM:
        category_totals[category] += qty * unit
    subtotal = sum(category_totals.values())
    contingency = round(subtotal * P.CONTINGENCY_RATE)
    total = subtotal + contingency

    wb = Workbook()
    bom = wb.active
    bom.title = "BoM"
    write_bom(bom)
    summary = wb.create_sheet("Cost Summary")
    write_summary(summary, category_totals, subtotal, contingency, total)
    tco = wb.create_sheet("3-Year TCO")
    write_tco(tco, total)
    assumptions = wb.create_sheet("Assumptions")
    write_assumptions(assumptions)
    for ws in wb.worksheets:
        ws.sheet_properties.tabColor = BLUE
    wb.save(OUTPUT)
    print("wrote", OUTPUT)
    print("subtotal", money(subtotal))
    print("contingency", money(contingency))
    print("total", money(total))
    print("annual_opex", money(sum(
        value * (12 if label.startswith("ISP") else 1)
        for label, value, unit in P.OPEX)))


if __name__ == "__main__":
    main()
