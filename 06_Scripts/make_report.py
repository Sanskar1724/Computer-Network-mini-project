from pathlib import Path
import csv
import json
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import project_data as P


DOCX_OUT = PROJECT_ROOT / "Assignment 8 Mini Project - Sanskar Chandawar.docx"
PDF_OUT = DOCX_OUT.with_suffix(".pdf")
NAVY = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2F, 0x55, 0x97)
GREY = RGBColor(0x4B, 0x55, 0x63)
DARK = RGBColor(0x11, 0x18, 0x27)
GREEN = RGBColor(0x2E, 0x7D, 0x32)

JUSTIFY = WD_ALIGN_PARAGRAPH.JUSTIFY
CENTER = WD_ALIGN_PARAGRAPH.CENTER
LEFT = WD_ALIGN_PARAGRAPH.LEFT
RIGHT = WD_ALIGN_PARAGRAPH.RIGHT


def set_run_font(run, name="Times New Roman", size=12, bold=False,
                 italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), name)


def shade_paragraph(p, fill):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    pPr.append(shd)


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def add_bottom_border(paragraph, color="1F3864", size="8"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_page_field(paragraph, field_name):
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {field_name} "
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(text)
    run._r.append(fld_end)
    set_run_font(run, size=9, color=GREY)


def configure_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.alignment = JUSTIFY
    rPr = normal.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), "Times New Roman")

    specs = {
        "Heading 1": (15, NAVY, 12, 6),
        "Heading 2": (12.5, BLUE, 14, 4),
        "Heading 3": (12, DARK, 10, 3),
    }
    for name, (size, color, before, after) in specs.items():
        style = doc.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.line_spacing = 1.2
        rPr = style.element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.insert(0, rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), "Times New Roman")


def configure_document(doc):
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.3)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.header_distance = Cm(1.1)
    section.footer_distance = Cm(1.1)
    section.different_first_page_header_footer = True

    header = section.header
    hp = header.paragraphs[0]
    hp.text = ""
    hp.paragraph_format.tab_stops.add_tab_stop(
        Inches(6.25), WD_TAB_ALIGNMENT.RIGHT)
    hp.paragraph_format.space_after = Pt(2)
    add_bottom_border(hp, color="9CA3AF", size="4")
    run = hp.add_run("Computer Network Laboratory")
    set_run_font(run, size=9, color=GREY)
    run = hp.add_run("\tNexaSoft Office LAN")
    set_run_font(run, size=9, color=GREY)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = CENTER
    fp.paragraph_format.space_before = Pt(2)
    run = fp.add_run("Page ")
    set_run_font(run, size=9, color=GREY)
    add_page_field(fp, "PAGE")


def body(text, bold=False, italic=False, size=12, align=JUSTIFY,
         space_before=0, space_after=6, first_line=0.25, line=1.5,
         color=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line
    if first_line:
        pf.first_line_indent = Inches(first_line)
    p.alignment = align
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic, color=color)
    return p


def bullet(text, size=12, space_after=3):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.35)
    pf.first_line_indent = Inches(-0.22)
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.35
    p.alignment = JUSTIFY
    run = p.add_run("\u2022  " + text)
    set_run_font(run, size=size)
    return p


def numbered(number, text, size=12, space_after=3):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.4)
    pf.first_line_indent = Inches(-0.27)
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.35
    p.alignment = JUSTIFY
    run = p.add_run(f"{number}.  " + text)
    set_run_font(run, size=size)
    return p


def force_times(paragraph):
    # Heading styles carry theme fonts (Calibri) that override the style's
    # font name in Word, so pin Times New Roman on the runs themselves.
    for run in paragraph.runs:
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.insert(0, rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), "Times New Roman")
    return paragraph


def chapter(title):
    p = doc.add_heading(title, level=1)
    p.paragraph_format.page_break_before = True
    return force_times(p)


def subheading(title):
    return force_times(doc.add_heading(title, level=2))


def add_figure(path, width, caption):
    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = CENTER
    cap.paragraph_format.space_before = Pt(2)
    cap.paragraph_format.space_after = Pt(10)
    cap.paragraph_format.line_spacing = 1.0
    run = cap.add_run(caption)
    set_run_font(run, size=9.5, italic=True, color=GREY)


def add_table(data, widths, caption, font_size=8.8, header_size=8.8,
              align=LEFT, keep_together=False):
    cap = doc.add_paragraph()
    cap.alignment = CENTER
    cap.paragraph_format.space_before = Pt(8)
    cap.paragraph_format.space_after = Pt(3)
    cap.paragraph_format.keep_with_next = True
    cap.paragraph_format.line_spacing = 1.0
    run = cap.add_run(caption)
    set_run_font(run, size=9.5, italic=True, color=GREY)

    table = doc.add_table(rows=len(data), cols=len(data[0]))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    for r, row in enumerate(data):
        trPr = table.rows[r]._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if r == 0:
            trPr.append(OxmlElement("w:tblHeader"))
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.width = Inches(widths[c])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            para = cell.paragraphs[0]
            pf = para.paragraph_format
            pf.space_before = Pt(1.5)
            pf.space_after = Pt(1.5)
            pf.line_spacing = 1.0
            pf.keep_with_next = keep_together and r < len(data) - 1
            para.alignment = align if c > 0 else LEFT
            run = para.add_run(str(value))
            set_run_font(run, size=header_size if r == 0 else font_size,
                         bold=(r == 0), color=NAVY if r == 0 else DARK)
            if r == 0:
                shade_cell(cell, "D9E2F3")
            elif r % 2 == 0:
                shade_cell(cell, "F2F5FA")
    for c, width in enumerate(widths):
        table.columns[c].width = Inches(width)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = Pt(3)
    return table


def listing(title, lines, size=8.4):
    cap = doc.add_paragraph()
    cap.paragraph_format.space_before = Pt(8)
    cap.paragraph_format.space_after = Pt(2)
    cap.paragraph_format.keep_with_next = True
    cap.paragraph_format.line_spacing = 1.0
    run = cap.add_run(title)
    set_run_font(run, size=9.0, bold=True, color=BLUE)
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.22)
    pf.right_indent = Inches(0.1)
    pf.space_before = Pt(0)
    pf.space_after = Pt(8)
    pf.line_spacing = 1.0
    p.alignment = LEFT
    for index, line in enumerate(lines):
        run = p.add_run(line if line else " ")
        set_run_font(run, name="Consolas", size=size, color=DARK)
        if index < len(lines) - 1:
            run.add_break()
    shade_paragraph(p, "F4F6F8")
    return p


def custom_title(text, size=18):
    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(18)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=True, color=NAVY)
    return p


def add_toc():
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    fld_begin.set(qn("w:dirty"), "true")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-2" \\h \\z \\u '
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Table of contents will be generated here."
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_sep)
    run._r.append(placeholder)
    run._r.append(fld_end)


def cover():
    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run()
    run.add_picture(str(PROJECT_ROOT / "assets" / "logo_mitaoe.jpg"),
                    width=Inches(2.7))

    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run("MIT ACADEMY OF ENGINEERING, ALANDI, PUNE")
    set_run_font(run, size=15, bold=True, color=NAVY)

    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run("Department of Computer Engineering")
    set_run_font(run, size=12.5, bold=True, color=BLUE)
    add_bottom_border(p, color="9CA3AF", size="6")

    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(22)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run("A MINI PROJECT REPORT ON")
    set_run_font(run, size=10.5, bold=True, color=GREY)

    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(P.PROJECT["title"])
    set_run_font(run, size=17.5, bold=True, color=NAVY)

    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_after = Pt(20)
    run = p.add_run("Project Option 1 \u2014 LAN Design, IP Addressing and Cost Analysis")
    set_run_font(run, size=11, italic=True, color=BLUE)

    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run("Submitted by")
    set_run_font(run, size=10.5, italic=True, color=GREY)

    team = doc.add_table(rows=len(P.TEAM), cols=2)
    team.alignment = WD_TABLE_ALIGNMENT.CENTER
    for row, member in zip(team.rows, P.TEAM):
        row.cells[0].width = Inches(2.4)
        row.cells[1].width = Inches(1.9)
        for cell, text, bold, size in ((row.cells[0], member["name"], True, 13),
                                       (row.cells[1], f"PRN: {member['prn']}", False, 11)):
            cp = cell.paragraphs[0]
            cp.alignment = LEFT
            cp.paragraph_format.space_before = Pt(2)
            cp.paragraph_format.space_after = Pt(2)
            cp.paragraph_format.line_spacing = 1.0
            set_run_font(cp.add_run(text), size=size, bold=bold, color=DARK)

    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(16)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(
        f"Division and Batch: {P.STUDENT['division']}\n"
        f"{P.STUDENT['program']}, {P.STUDENT['year']}, Semester {P.STUDENT['semester']}")
    set_run_font(run, size=10.5, color=DARK)

    p = doc.add_paragraph()
    p.alignment = CENTER
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(f"Academic Year {P.STUDENT['academic_year']}   |   November 2026")
    set_run_font(run, size=10.5, bold=True, color=NAVY)


def abstract(summary):
    p = custom_title("Abstract", 17)
    p.paragraph_format.page_break_before = True
    body(
        "This mini project presents the design, implementation plan and "
        "validation of a local area network for a 2,800 sq ft small-office "
        "floor with 48 wired network points and up to 24 concurrent wireless "
        "clients. The site is modelled as NexaSoft Office LAN, an anonymised "
        "office at Sunrise Business Park, Baner, Pune. A flat network was "
        "replaced with a two-tier switched architecture, five VLANs, a "
        "contiguous VLSM address plan, router-on-a-stick inter-VLAN routing, "
        "centralised DHCP and DNS, NAT/PAT internet access, and guest and "
        "management ACLs. The design provides separate server, engineering, "
        "staff, guest and management broadcast domains.")
    body(
        "The IP plan uses 192.168.10.0/24 with /26, /27 and /28 allocations; "
        "64 dynamic leases are distributed across the engineering, staff and "
        "guest VLANs, while infrastructure and printers use static addresses. "
        "Cisco 2911, Catalyst 2960X and Aironet 1832I devices were selected "
        "and their configuration templates were prepared. Because Cisco "
        "Packet Tracer and physical hardware were unavailable, a Python "
        "packet-flow model was used as the experiment: it validates DHCP, DNS, "
        "VLAN routing, guest isolation, management ACLs and NAT/PAT. All 18 "
        "validation tests passed. The engineered CapEx is Rs. 569,835 "
        "(Rs. 5.70 lakh), including 5% contingency, and the three-year total "
        "cost of ownership is Rs. 1,148,595. The project demonstrates a "
        "deployable, segmented and cost-controlled LAN design.")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run("Keywords: ")
    set_run_font(run, size=10.5, bold=True)
    run = p.add_run(
        "LAN design; VLAN; VLSM; router-on-a-stick; DHCP; DNS; NAT/PAT; "
        "access control list; Cisco Catalyst; network costing.")
    set_run_font(run, size=10.5, italic=True)


def contents():
    p = custom_title("Contents", 17)
    p.paragraph_format.page_break_before = True
    add_toc()


def introduction():
    chapter("1. Introduction")
    subheading("1.1 Project Background and Problem Statement")
    body(
        "Small offices often begin with a single flat Layer 2 network and an "
        "unmanaged consumer router. As the number of workstations, printers, "
        "servers, access points and visitors grows, the flat design creates a "
        "large broadcast domain, weak traffic separation, unmanaged address "
        "assignment and no clear cost baseline. A guest device can reach "
        "internal resources, management interfaces share the user network, and "
        "there is little spare capacity for future growth. The selected "
        "project option therefore requires a complete LAN architecture, an "
        "optimised IP addressing scheme and a realistic deployment estimate.")
    body(
        "The chosen statement is Project Option 1: \u201cDesign and "
        "Implementation of a Local Area Network (LAN) for a Specific Location "
        "for Architecture Design, IP Addressing, and Cost Analysis.\u201d The "
        "site is a 70 ft \u00d7 40 ft floor with ten rooms, a central corridor "
        "and a single server room. The design must support 48 wired drops, 24 "
        "concurrent wireless clients, internal servers, guest access and a "
        "100 Mbps internet link while remaining below a Rs. 6.00 lakh capital "
        "budget. Site details are anonymised in this report.")
    subheading("1.2 Objectives")
    numbered(1, "Survey the floor, identify rooms, cable paths and wireless constraints, and plan 48 Cat6 drops and three ceiling access points.")
    numbered(2, "Design a two-tier switched LAN with separate VLANs for servers, engineering, staff, guest and management traffic.")
    numbered(3, "Allocate one contiguous 192.168.10.0/24 block using VLSM and document gateways, static addresses and DHCP pools.")
    numbered(4, "Select routers, switches, access points, cabling and power equipment, and prepare deployable Cisco configuration templates.")
    numbered(5, "Validate DHCP, DNS, inter-VLAN routing, guest isolation, management ACLs and NAT/PAT through a repeatable experiment.")
    numbered(6, "Estimate capital and recurring costs, calculate the three-year TCO and confirm compliance with the budget cap.")
    subheading("1.3 Scope and Limitations")
    body(
        "The scope covers one office floor, the access and distribution "
        "switching, wireless access, internal addressing and services, WAN "
        "edge configuration and a cost estimate. Client laptops and phones, "
        "ISP equipment beyond the hand-off, civil work and physical installation "
        "are outside the implementation scope. The cost figures are budgetary "
        "and must be confirmed with vendor quotations and applicable taxes.")
    body(
        "Cisco Packet Tracer, GNS3 and physical Cisco hardware were not "
        "available on the working machine. The experiment is therefore a "
        "deterministic Python packet-flow model that validates the design "
        "logic, address allocation and policy outcomes. The Cisco IOS "
        "configuration files are supplied as deployment templates, but they "
        "were not executed on a real router or switch. This limitation is "
        "stated explicitly wherever the validation results are discussed.")
    subheading("1.4 Report Organisation")
    body(
        "Chapter 2 explains the LAN design principles used in the project. "
        "Chapter 3 records the site survey, requirements and capacity "
        "decisions. Chapter 4 presents the topology, addressing plan, device "
        "selection, port allocation and security design. Chapter 5 documents "
        "the implementation templates and the Python validation model. "
        "Chapter 6 reports the DHCP, routing, security and cost tests. Chapter 7 "
        "analyses the bill of materials and three-year ownership cost, and "
        "Chapter 8 concludes the report with future enhancements. The "
        "appendices list the port allocation and project artifacts.")
    subheading("1.5 Methodology Overview")
    body(
        "The project followed a five-phase method: survey, requirements and "
        "capacity planning; logical and physical design; configuration "
        "template generation; deterministic validation; and cost analysis. "
        "The site survey recorded room geometry, cable paths, existing "
        "conduits, power outlets, wireless interference and device positions. "
        "Those observations were converted into measurable requirements and a "
        "drop schedule rather than being treated as a single floor-plan sketch.")
    body(
        "The design fixed the VLAN and VLSM plan before any configuration was "
        "written, so the figures, switch templates, DHCP pools and test data "
        "all derive from one data source. A Python packet-flow model executed "
        "the validation cases because Packet Tracer and hardware were "
        "unavailable. The final phase priced the bill of materials, applied "
        "contingency, calculated annual OpEx and compared the three-year TCO "
        "with the budget cap. Each phase produced a reviewable artifact, listed "
        "in Appendix A.")


def principles():
    chapter("2. Design Principles")
    subheading("2.1 Hierarchical LAN Architecture")
    body(
        "A small office is best served by a collapsed-core two-tier design. "
        "The core switch provides high-speed forwarding, VLAN trunks and PoE "
        "for access points; an engineering access switch extends copper ports "
        "to the workstation rows. This topology keeps the number of active "
        "devices small while preserving a clear separation between the "
        "distribution and access layers. A router-on-a-stick provides "
        "inter-VLAN routing over a single 802.1Q trunk, which is adequate for "
        "the expected office throughput and is simpler to operate than a "
        "dedicated Layer 3 switch [1], [2].")
    body(
        "The core-to-access link uses two 1 Gbps OM3 fibre pairs in an LACP "
        "port-channel. The redundancy protects against a single cable or SFP "
        "failure and gives 2 Gbps aggregate capacity. Rapid PVST+ is used so "
        "that a loop, if introduced accidentally, converges quickly without "
        "long outages. Edge ports use PortFast and BPDU Guard to keep the "
        "spanning tree stable.")
    subheading("2.2 VLAN Segmentation and VLSM")
    body(
        "VLANs divide one physical switch into separate broadcast domains. "
        "The design uses VLAN 10 for servers, VLAN 30 for engineering, VLAN 20 "
        "for staff, VLAN 40 for guests and VLAN 99 for infrastructure "
        "management. Each VLAN receives a gateway on the router and a subnet "
        "sized for its current hosts plus growth. VLSM allows one contiguous "
        "192.168.10.0/24 block to be divided efficiently: /26 for the two "
        "largest groups, /27 for staff and guests, and /28 for management. "
        "The single block keeps the routing table and access lists simple and "
        "leaves 192.168.10.208/28 and above unallocated for future growth.")
    subheading("2.3 DHCP, DNS, NAT and PAT")
    body(
        "DHCP reduces manual configuration errors on endpoints. The router "
        "acts as the DHCP server for VLANs 20, 30 and 40, using a different "
        "pool and default gateway per VLAN. The DHCP exchange follows the "
        "standard DORA sequence: Discover, Offer, Request and Acknowledgement "
        "[6], [7]. Servers, printers and infrastructure devices use static "
        "addresses so that DNS records and management access remain stable.")
    body(
        "The internal DNS server at 192.168.10.10 resolves intranet, file and "
        "ERP names. Staff and engineering clients receive this address through "
        "DHCP; guest clients receive a public resolver because the guest ACL "
        "blocks all internal addresses. NAT/PAT translates inside addresses to "
        "the single public address 203.0.113.2 on the ISP link, allowing many "
        "clients to share the 100 Mbps service [8].")
    subheading("2.4 Security and Resilience")
    body(
        "Segmentation is the primary security control: guests cannot reach "
        "internal subnets, staff and engineering users cannot reach the "
        "management VLAN, and servers retain the access needed for "
        "administration. Extended ACLs enforce these rules at the router "
        "sub-interfaces. Layer 2 controls include port security, DHCP "
        "snooping, dynamic ARP inspection, BPDU Guard, disabled unused ports "
        "and SSH-only management. Wireless security uses WPA2-AES with a "
        "separate guest SSID and client isolation. A 3 kVA online UPS protects "
        "the core, router and PoE load, while the 1 kVA UPS protects the "
        "engineering closet [3], [10].")
    subheading("2.5 Standards and Design Justification")
    body(
        "The design uses IEEE 802.3 Ethernet and 802.3af/at PoE for access "
        "links and access-point power, IEEE 802.1Q for VLAN tagging, IEEE "
        "802.1w Rapid Spanning Tree for loop recovery, and IEEE 802.11ac Wave 2 "
        "for wireless access. Structured cabling follows the TIA-568 channel "
        "model with Cat6 horizontal cable, LC-terminated OM3 fibre for the "
        "closet backbone and a 90 m permanent-link limit. These are mature, "
        "widely supported standards, so the selected Cisco switches and "
        "Aironet APs can interoperate with standard patch panels, transceivers "
        "and client hardware.")
    body(
        "The physical design also respects installation constraints: the 42 m "
        "longest run leaves margin for service loops and cross-connects; the "
        "25 mm conduits can carry the planned Cat6 bundles; and the ceiling AP "
        "positions cover the work areas without mounting over occupied desks. "
        "PoE power for the three APs is well within the core switch budget, "
        "and the UPS capacity was specified with headroom for the core, router "
        "and PoE load. The remaining design risk is therefore commercial and "
        "operational rather than a basic standards-compliance gap.")


def survey():
    chapter("3. Site Survey and Requirements")
    subheading("3.1 Site Conditions")
    body(
        "The site is the second floor of Wing B at Sunrise Business Park, "
        "Baner, Pune. The usable floor is 70 ft \u00d7 40 ft (2,800 sq ft) and "
        "contains Engineering, Server Room, Pantry, Breakout, Restrooms, "
        "Management, Reception, Conference, Admin/HR/Finance and Store/Utility "
        "areas around a 4 ft central corridor. The false ceiling is at 9.5 ft, "
        "the partitions are gypsum, and existing 25 mm conduits can carry the "
        "horizontal cabling. The longest permanent link is approximately 42 m, "
        "well below the 90 m Cat6 limit.")
    body(
        "The survey found twelve neighbouring SSIDs on 2.4 GHz and five on "
        "5 GHz, with 38% utilisation on 2.4 GHz. The wireless design therefore "
        "prefers 5 GHz and uses non-overlapping 2.4 GHz channels 1, 6 and 11. "
        "Three ceiling access points provide coverage with approximately 15% "
        "cell overlap and a target RSSI of at least \u221267 dBm in work "
        "areas. The detailed room dimensions, drops and AP positions are shown "
        "in Figure 3.1.")
    add_figure(PROJECT_ROOT / "01_Site_Survey" / "floor_plan.png", 6.2,
               "Figure 3.1 \u2014 Site survey and device placement plan for the "
               "2,800 sq ft office floor.")
    observations = [["Survey area", "Observation", "Design response"]]
    observations.extend([list(row) for row in P.SITE_OBSERVATIONS])
    add_table(observations, [1.15, 2.85, 2.25], "Table 3.1 \u2014 Site survey observations and design responses.", font_size=7.8, header_size=8.2)
    subheading("3.2 Functional Requirements")
    body(
        "The requirements were derived from the project brief and the survey. "
        "They cover wired and wireless access, segmentation, routing, "
        "addressing, services, internet access, availability, security, growth "
        "and cost. Table 3.2 records the acceptance target for each requirement.")
    req = [["ID", "Requirement", "Acceptance target"]]
    req.extend([list(row) for row in P.REQUIREMENTS])
    add_table(req, [0.42, 1.38, 4.45], "Table 3.2 \u2014 Functional and non-functional requirements.", font_size=7.9, header_size=8.2)
    subheading("3.3 Capacity and Design Targets")
    body(
        "The 48 physical drops comprise 24 engineering workstations, 16 staff "
        "workstations, three servers, two printers and three access points. "
        "The wireless design supports 24 concurrent clients: four engineering "
        "clients on NEXA-ENG, eight staff clients on NEXA-STAFF and twelve "
        "guests on NEXA-GUEST. DHCP therefore has to issue 64 leases: 28 in "
        "VLAN 30, 24 in VLAN 20 and 12 in VLAN 40. Static addresses are used "
        "for the three servers, two printers and five infrastructure devices.")
    body(
        "The core switch uses 27 of its 48 ports (24 drops and three "
        "infrastructure links), leaving 21 spare; the 24-port engineering "
        "switch is fully populated. The design therefore provides 21 spare "
        "switched ports overall (29% of 72 access ports) and 31 free VLAN 30 "
        "addresses for growth.")


def design():
    chapter("4. Network Architecture and Addressing")
    subheading("4.1 Logical Topology")
    body(
        "The topology is a collapsed core with a Cisco 2911 router at the WAN "
        "edge, a Catalyst 2960X-48FPD-L core switch, a Catalyst 2960X-24TS-L "
        "engineering access switch and three Aironet 1832I access points. The "
        "router connects to the core through an 802.1Q trunk and terminates "
        "one sub-interface for each VLAN. The core connects to the engineering "
        "switch through a two-member LACP fibre port-channel. Servers, staff "
        "ports, printers and APs terminate directly on the core; engineering "
        "PCs terminate on the access switch. The logical topology is shown in "
        "Figure 4.1.")
    add_figure(PROJECT_ROOT / "02_Network_Design" / "topology.png", 6.2,
               "Figure 4.1 \u2014 Logical topology showing VLANs, router-on-a-stick, "
               "LACP uplink and wireless SSIDs.")
    subheading("4.2 VLSM and VLAN Plan")
    body(
        "All internal subnets are allocated from 192.168.10.0/24 in descending "
        "size order. The server and engineering VLANs each receive a /26 "
        "(64 addresses), staff and guest receive /27 (32 addresses), and "
        "management receives /28 (16 addresses). Gateways are the first usable "
        "address in each subnet. The VLSM map in Figure 4.2 shows that the "
        "allocations are contiguous and that 192.168.10.208\u2013255 remains "
        "reserved.")
    vlan_rows = [["VLAN / name", "Subnet", "Gateway", "DHCP pool", "Purpose"]]
    for vlan in P.VLANS:
        dhcp = vlan["dhcp"]
        pool = f"{dhcp[0]} \u2013 {dhcp[1]}" if dhcp else "Static only"
        vlan_rows.append([
            f"{vlan['id']} / {vlan['name']}", vlan["subnet"], vlan["gateway"],
            pool, vlan["purpose"]])
    add_table(vlan_rows, [0.95, 1.05, 1.0, 1.45, 1.8],
              "Table 4.1 \u2014 VLAN, subnet, gateway and DHCP allocation.",
              font_size=7.8, header_size=8.2)
    add_figure(PROJECT_ROOT / "02_Network_Design" / "vlan_map.png", 6.45,
               "Figure 4.2 \u2014 VLSM allocation of 192.168.10.0/24.")
    subheading("4.3 Device Selection")
    body(
        "The equipment mix balances capability, PoE requirements and budget. "
        "The 2911 router provides two Gigabit Ethernet interfaces, NAT/PAT, "
        "ACLs and DHCP for the small office. The 2960X-48FPD-L core supplies "
        "48 PoE+ ports and four SFP uplinks; the 2960X-24TS-L access switch "
        "supplies the 24 engineering copper ports. The Aironet 1832I APs are "
        "802.11ac Wave 2 units powered by PoE+. Table 4.2 lists the selected "
        "devices and their roles.")
    device_rows = [["Device", "Model", "Qty", "Role"]]
    for name, model, qty, role in P.DEVICES:
        device_rows.append([name, model, qty, role])
    add_table(device_rows, [1.05, 1.65, 0.35, 3.2],
              "Table 4.2 \u2014 Selected network devices and roles.",
              font_size=8.0, header_size=8.2)
    subheading("4.4 Link and Port Allocation")
    body(
        "The link schedule uses a 1 Gbps router-to-core trunk, a 2 Gbps "
        "aggregated core-to-access uplink and 1 Gbps copper access links. The "
        "core port map terminates servers on Gi1/0/4\u20136, the staff printer "
        "on Gi1/0/7, staff PCs on Gi1/0/8\u201323, the three AP trunks on "
        "Gi1/0/24\u201326 and the engineering printer on Gi1/0/27. The "
        "engineering access switch uses Gi1/0/1\u201324 for the 24 engineering "
        "PCs and Gi1/0/25\u201326 for the fibre port-channel. AP-ENG is the only "
        "AP trunk that permits VLAN 30, because NEXA-ENG is broadcast only from "
        "the engineering AP.")
    link_rows = [["Link", "Addressing / mode", "Media", "Purpose"]]
    for row in P.LINK_SCHEDULE:
        link_rows.append(list(row))
    add_table(link_rows, [1.45, 1.5, 1.1, 2.2],
              "Table 4.3 \u2014 Link schedule and 802.1Q modes.",
              font_size=7.7, header_size=8.1)
    subheading("4.5 Wireless Design")
    body(
        "The three APs are ceiling-mounted at the coordinates recorded in the "
        "site survey. AP-ENG serves the engineering area and broadcasts "
        "NEXA-ENG (VLAN 30), NEXA-STAFF (VLAN 20) and NEXA-GUEST (VLAN 40). "
        "AP-STAFF and AP-MGMT broadcast NEXA-STAFF and NEXA-GUEST only. The "
        "2.4 GHz radios use channels 1, 6 and 11; the 5 GHz radios use 36, 44 "
        "and 149 with automatic power. Guest client isolation is enabled on "
        "every NEXA-GUEST SSID.")
    ssid_rows = [["SSID", "VLAN", "Security", "Intended users", "Isolation"]]
    for row in P.SSIDS:
        ssid_rows.append(list(row))
    add_table(ssid_rows, [1.0, 0.5, 1.15, 2.85, 0.7],
              "Table 4.4 \u2014 Wireless SSID and VLAN plan.",
              font_size=8.0, header_size=8.1)
    subheading("4.6 Security Controls")
    body(
        "The router enforces the guest and management ACLs. The guest ACL "
        "permits DHCP and public internet access but denies all destinations "
        "in 192.168.10.0/24. The management ACL denies VLAN 20 and VLAN 30 "
        "hosts access to 192.168.10.192/28 while allowing the server VLAN and "
        "the management VLAN itself. Layer 2 controls prevent unauthorised "
        "devices, rogue DHCP servers and ARP spoofing. The controls are "
        "summarised in Table 4.5.")
    security_rows = [["Control", "Implementation"]]
    for row in P.SECURITY_CONTROLS:
        security_rows.append(list(row))
    add_table(security_rows, [1.45, 4.8],
              "Table 4.5 \u2014 Security controls and implementation.",
              font_size=7.8, header_size=8.1, keep_together=True)
    subheading("4.7 Design Verification")
    body(
        "Before implementation, the following checks were automated in "
        "project_data.py: every VLAN gateway is the first usable address; every "
        "static address is inside its subnet; no dynamic pool overlaps a "
        "static address; 48 physical drops are accounted for; and the bill of "
        "materials subtotal plus 5% contingency remains below the Rs. 6.00 "
        "lakh cap. The checks passed, and the same data feeds the figures, "
        "configuration generator, cost workbook and validation model.")


def implementation():
    chapter("5. Implementation")
    subheading("5.1 Implementation Strategy")
    body(
        "The implementation is organised as reproducible scripts. "
        "project_data.py stores the site, VLAN, address, device, link and cost "
        "data; make_figures.py produces the survey, topology, VLSM and cost "
        "figures; generate_configs.py produces the Cisco templates and port "
        "map; and network_model.py executes the validation experiment. "
        "Passwords in the configuration files are placeholders such as "
        "CHANGE_ME_ENABLE_SECRET; they must be replaced with organisation-"
        "approved secrets before any deployment. The configuration excerpts "
        "below show the key command structure, not the complete files.")
    subheading("5.2 Router Configuration")
    body(
        "The router creates a trunk to the core and one sub-interface for each "
        "VLAN. The sub-interface address is the default gateway for that VLAN. "
        "DHCP pools use the same gateway and the internal DNS server; the guest "
        "pool deliberately uses 8.8.8.8 because guests are denied access to "
        "the internal DNS server. NAT overload is applied to the WAN interface "
        "and a default route points to the ISP gateway.")
    listing("Listing 5.1 \u2014 NXS-GW router-on-a-stick and guest policy excerpt.", [
        "hostname NXS-GW",
        "ip dhcp excluded-address 192.168.10.64 192.168.10.65",
        "ip dhcp pool VLAN30-ENG",
        " network 192.168.10.64 255.255.255.192",
        " default-router 192.168.10.65",
        " dns-server 192.168.10.10",
        "ip dhcp pool VLAN40-GUEST",
        " network 192.168.10.160 255.255.255.224",
        " default-router 192.168.10.161",
        " dns-server 8.8.8.8",
        "ip access-list extended GUEST-IN",
        " permit udp any any eq 67",
        " deny ip any 192.168.10.0 0.0.0.255",
        " permit ip any any",
        "interface GigabitEthernet0/0.40",
        " encapsulation dot1Q 40",
        " ip address 192.168.10.161 255.255.255.224",
        " ip access-group GUEST-IN in",
        " ip nat inside",
        "ip nat inside source list NAT-INSIDE interface GigabitEthernet0/1 overload",
        "ip route 0.0.0.0 0.0.0.0 203.0.113.1",
    ])
    subheading("5.3 Core and Access Switch Configuration")
    body(
        "The core switch is the STP root and the DHCP snooping and dynamic ARP "
        "inspection trust point. Access ports use PortFast, BPDU Guard, port "
        "security and an unused VLAN for spare ports. AP ports are trunks with "
        "native VLAN 99; only AP-ENG permits VLAN 30. The access switch trusts "
        "the fibre port-channel for DHCP snooping and DAI and applies the same "
        "edge-port protections to the 24 engineering ports.")
    listing("Listing 5.2 \u2014 NXS-CORE-SW VLAN, trunk and access-port excerpt.", [
        "hostname NXS-CORE-SW",
        "vlan 10",
        " name SERVERS",
        "vlan 20",
        " name STAFF",
        "vlan 30",
        " name ENGINEERING",
        "vlan 40",
        " name GUEST",
        "vlan 99",
        " name MANAGEMENT",
        "spanning-tree mode rapid-pvst",
        "spanning-tree vlan 10,20,30,40,99 root primary",
        "interface GigabitEthernet1/0/1",
        " switchport mode trunk",
        " switchport trunk native vlan 99",
        " switchport trunk allowed vlan 10,20,30,40,99",
        "interface range GigabitEthernet1/0/7-23",
        " switchport mode access",
        " switchport access vlan 20",
        " spanning-tree portfast",
        " switchport port-security",
        "interface GigabitEthernet1/0/24",
        " switchport mode trunk",
        " switchport trunk native vlan 99",
        " switchport trunk allowed vlan 20,30,40,99",
        "ip dhcp snooping",
        "ip dhcp snooping vlan 20,30,40",
        "ip arp inspection vlan 20,30,40",
    ])
    listing("Listing 5.3 \u2014 NXS-ENG-SW access and fibre-uplink excerpt.", [
        "hostname NXS-ENG-SW",
        "vlan 30",
        " name ENGINEERING",
        "vlan 99",
        " name MANAGEMENT",
        "interface range GigabitEthernet1/0/1-24",
        " switchport mode access",
        " switchport access vlan 30",
        " spanning-tree portfast",
        " spanning-tree bpduguard enable",
        " switchport port-security maximum 1",
        " switchport port-security violation restrict",
        "interface range GigabitEthernet1/0/25-26",
        " switchport mode trunk",
        " switchport trunk native vlan 99",
        " switchport trunk allowed vlan 30,99",
        " channel-group 2 mode active",
        "interface Port-channel2",
        " ip dhcp snooping trust",
        " ip arp inspection trust",
        "ip default-gateway 192.168.10.193",
    ])
    subheading("5.4 Python Validation Model")
    body(
        "The validation model is implemented in network_model.py using only "
        "the Python standard library and data from project_data.py. It builds "
        "74 hosts: 64 dynamic clients and 10 static server, printer and "
        "infrastructure addresses. The model allocates each client from its "
        "VLAN pool, verifies that no address is duplicated, evaluates the "
        "guest and management ACLs, resolves internal DNS names, creates NAT "
        "translations and applies guest wireless client isolation. It writes "
        "the DHCP lease table, NAT table, DNS log, test results, packet traces "
        "and a terminal-style evidence image.")
    body(
        "The model is not a Cisco IOS emulator. It does not simulate line-rate "
        "forwarding, Spanning Tree convergence, LACP negotiation or RF "
        "propagation. Its purpose is to test the design decisions that can be "
        "checked deterministically: subnet membership, DHCP pool allocation, "
        "default gateways, ACL direction, NAT translation and DNS reachability. "
        "The configuration templates cover the device-specific commands that "
        "must be verified on hardware.")
    subheading("5.5 Operational Notes")
    body(
        "Before deployment, replace all CHANGE_ME secrets, generate the RSA "
        "key pair on each device, confirm the IOS image supports the required "
        "PoE and ACL features, and back up the final configurations. The "
        "guest DHCP pool advertises 8.8.8.8, not the internal DNS server, "
        "because the guest ACL blocks 192.168.10.0/24. Staff and engineering "
        "pools advertise 192.168.10.10. Management SSH is restricted to "
        "192.168.10.192/28, and NTP and syslog point to the internal server. "
        "The AP management addresses are static in VLAN 99.")


def testing(summary, test_rows, lease_rows, nat_rows):
    chapter("6. Testing and Results")
    subheading("6.1 Test Methodology")
    body(
        "Eighteen tests were defined before execution. They cover DHCP, "
        "same-VLAN switching, inter-VLAN routing, DNS, guest ACL enforcement, "
        "management ACL enforcement, NAT/PAT, guest wireless isolation and "
        "broadcast containment. A test passes when the modelled outcome equals "
        "the expected outcome. DHCP tests check that the lease belongs to the "
        "correct pool and VLAN; ACL tests check both the decision and the "
        "drop point; NAT tests check the translated public address; DNS tests "
        "check the returned A record.")
    body(
        f"The final run completed with {summary['tests_passed']} of "
        f"{summary['tests_total']} tests passing, {summary['dhcp_leases']} "
        "unique dynamic leases and no duplicate addresses. The complete "
        "evidence is stored in test_results.csv, test_results.txt, "
        "dhcp_leases.csv, nat_table.csv, dns_log.csv and packet_trace.txt.")
    subheading("6.2 DHCP and DNS Results")
    body(
        "The DHCP allocations match the plan: 28 leases in VLAN 30, 24 in "
        "VLAN 20 and 12 in VLAN 40. Engineering clients receive "
        "192.168.10.66\u2013124, staff clients receive "
        "192.168.10.132\u2013158 and guests receive "
        "192.168.10.162\u2013190. Static devices remain outside the pools. "
        "Table 6.2 shows a representative sample; the full 64-row lease table "
        "is attached as dhcp_leases.csv.")
    sample_names = {"ENG-PC-01", "ENG-PC-02", "ENG-PC-03", "STF-PC-01",
                    "STF-PC-02", "GUEST-WIFI-01", "GUEST-WIFI-02",
                    "GUEST-WIFI-03"}
    sample = [row for row in lease_rows if row["hostname"] in sample_names]
    lease_table = [["Hostname", "VLAN", "IP address", "MAC", "DNS", "Server"]]
    for row in sample:
        lease_table.append([row["hostname"], row["vlan"], row["ip"],
                            row["mac"], row["dns_server"], row["dhcp_server"]])
    add_table(lease_table, [1.06, 0.6, 1.08, 1.25, 0.98, 0.98],
              "Table 6.2 \u2014 Sample DHCP leases from the 64-lease run.",
              font_size=7.5, header_size=8.0)
    body(
        "The DNS log shows successful resolution of erp.nexasoft.local to "
        "192.168.10.12 for a staff client and intranet.nexasoft.local to "
        "192.168.10.10 for the management switch. The guest query to the "
        "internal DNS address is blocked by the guest ACL, while the guest "
        "DHCP pool supplies the public resolver 8.8.8.8.", space_before=2)
    subheading("6.3 Routing, Security and NAT Results")
    body(
        "Table 6.1 lists all 18 tests. The important security outcomes are: "
        "guests are denied access to the internal DNS and file servers, staff "
        "and engineering clients are denied access to the management VLAN, "
        "servers can reach management, and guest wireless clients cannot reach "
        "each other. The NAT tests show two inside clients sharing the public "
        "address with different outside ports.")
    test_table = [["ID", "Test", "Expected", "Actual", "Result"]]
    for row in test_rows:
        test_table.append([row["id"], row["test"], row["expected"],
                           row["actual"], row["result"]])
    add_table(test_table, [0.38, 3.0, 0.95, 0.95, 0.62],
              "Table 6.1 \u2014 Validation test results.", font_size=7.6,
              header_size=8.0)
    subheading("6.4 Evidence and Packet Trace")
    body(
        "Figure 6.1 shows the terminal evidence from the validation run. The "
        "model prints every test identifier, description and PASS/FAIL result, "
        "together with the host count, DHCP lease count and NAT translation "
        "count. The packet trace file records the actual forwarding path for "
        "representative flows, including the drop point for denied traffic.")
    add_figure(PROJECT_ROOT / "04_Simulation" / "simulation_evidence.png", 6.15,
               "Figure 6.1 \u2014 Terminal evidence from the Python validation run.")
    listing("Listing 6.1 \u2014 Representative packet-trace outcomes.", [
        "T01  DHCP DORA for ENG-PC-01",
        "     DHCPDISCOVER -> NXS-ENG-SW -> NXS-CORE-SW -> NXS-GW G0/0.30",
        "     DHCPOFFER 192.168.10.66; DNS 192.168.10.10; DHCPACK",
        "T09  GUEST-WIFI-01 -> SRV-DNS",
        "     GUEST-WIFI-01 -> AP-STAFF -> NXS-CORE-SW -> NXS-GW G0/0.40",
        "     DENY: GUEST-IN ACL denies 192.168.10.0/24",
        "T11  GUEST-WIFI-01 -> 8.8.8.8",
        "     NAT 203.0.113.2:40001 -> 8.8.8.8:443",
        "T13  STF-PC-01 -> NXS-CORE-SW management",
        "     DENY: STAFF-MGMT ACL denies VLAN 20/30 to VLAN 99",
        "T16  GUEST-WIFI-01 -> GUEST-WIFI-02",
        "     DENY: guest client isolation at AP-STAFF",
    ])
    nat_table = [["Inside address", "Outside address", "Destination", "State"]]
    for row in nat_rows:
        nat_table.append([
            f"{row['inside_ip']}:{row['inside_port']}",
            f"{row['outside_ip']}:{row['outside_port']}",
            row["destination"], row["state"]])
    add_table(nat_table, [1.35, 1.5, 1.45, 1.2],
              "Table 6.3 \u2014 NAT/PAT translations produced during validation.",
              font_size=7.8, header_size=8.0)
    subheading("6.5 Discussion")
    body(
        "The tests confirm that the address plan, DHCP pools and policy "
        "boundaries are internally consistent. The guest path is the most "
        "important result: DHCP and internet access work, but every internal "
        "destination is denied. The management ACL correctly permits server "
        "administration while blocking ordinary staff and engineering hosts. "
        "The NAT table demonstrates PAT because two different inside clients "
        "use the same public address with different outside ports.")
    body(
        "The experiment cannot prove hardware throughput, PoE budget, RF "
        "coverage or IOS command compatibility; those require a physical pilot "
        "or emulator. The evidence is design validation, not acceptance testing "
        "on the selected hardware.")


def cost(summary):
    chapter("7. Cost Analysis")
    subheading("7.1 Bill of Materials")
    body(
        "The bill of materials covers active equipment, cabling and passive "
        "components, racks and power, and installation services. The estimate "
        "uses indicative Indian market prices and includes a 5% contingency. "
        "Table 7.1 lists the 22 line items; the formatted workbook contains "
        "the full specifications and formulas. The total CapEx is Rs. 569,835 "
        "against a budget cap of Rs. 6.00 lakh.")
    bom_rows = [["Item", "Category", "Qty", "Unit (Rs.)", "Amount (Rs.)"]]
    for category, item, spec, qty, unit in P.BOM:
        bom_rows.append([item, category, qty, f"{unit:,}", f"{qty * unit:,}"])
    add_table(bom_rows, [2.7, 1.05, 0.4, 0.95, 1.05],
              "Table 7.1 \u2014 Budgetary bill of materials.", font_size=7.2,
              header_size=7.8)
    category_totals = {}
    for category, _, _, qty, unit in P.BOM:
        category_totals[category] = category_totals.get(category, 0) + qty * unit
    subtotal = sum(category_totals.values())
    contingency = round(subtotal * P.CONTINGENCY_RATE)
    total = subtotal + contingency
    subheading("7.2 Category Summary and Cost Drivers")
    body(
        "Active equipment is the largest category at Rs. 254,500, followed by "
        "cabling and passive materials at Rs. 148,000. The core switch, router "
        "and three access points account for most of the active cost, while "
        "the 48-drop cabling, tray, jacks and patch panels dominate the "
        "passive cost. The 5% contingency adds Rs. 27,135.")
    cat_rows = [["Cost category", "Amount (Rs.)", "Share"]]
    for category in ("Active equipment", "Cabling & passive", "Racks & power",
                     "Installation & services"):
        cat_rows.append([category, f"{category_totals[category]:,}",
                         f"{category_totals[category] / subtotal * 100:.1f}%"])
    cat_rows.append(["Subtotal", f"{subtotal:,}", "100.0%"])
    cat_rows.append(["Contingency (5%)", f"{contingency:,}",
                     f"{contingency / total * 100:.1f}%"])
    cat_rows.append(["Total CapEx", f"{total:,}", "100.0%"])
    add_table(cat_rows, [2.3, 1.4, 1.0],
              "Table 7.2 \u2014 Cost category summary.",
              font_size=8.3, header_size=8.4)
    add_figure(PROJECT_ROOT / "05_Cost_Analysis" / "cost_breakdown.png", 5.6,
               "Figure 7.1 \u2014 CapEx distribution by category, including 5% contingency.")
    subheading("7.3 Three-Year Total Cost of Ownership")
    body(
        "Recurring cost is driven by the 100 Mbps ISP service at "
        "Rs. 12,000 per month, the annual maintenance contract at Rs. 36,920 "
        "and electricity at Rs. 12,000 per year. The resulting annual OpEx is "
        "Rs. 192,920. Adding three years of recurring cost to the CapEx gives "
        "a three-year TCO of Rs. 1,148,595. This figure excludes client "
        "devices and any equipment replacement beyond year 3.")
    annual_isp = next(value for label, value, unit in P.OPEX
                      if label.startswith("ISP")) * 12
    annual_amc = next(value for label, value, unit in P.OPEX
                      if "maintenance" in label.lower())
    annual_power = next(value for label, value, unit in P.OPEX
                        if "electricity" in label.lower())
    annual_opex = annual_isp + annual_amc + annual_power
    tco = total + annual_opex * 3
    tco_rows = [
        ["Cost item", "Amount (Rs.)", "Basis"],
        ["Capital expenditure", f"{total:,}", "One-time project CapEx"],
        ["Annual recurring cost", f"{annual_opex:,}",
         "ISP, AMC and electricity"],
        ["Three-year total cost of ownership", f"{tco:,}",
         "CapEx + 3 \u00d7 annual OpEx"],
    ]
    add_table(tco_rows, [2.25, 1.4, 2.55],
              "Table 7.3 \u2014 Three-year total cost of ownership.",
              font_size=8.4, header_size=8.4)
    subheading("7.4 Budget Compliance and Cost Risk")
    body(
        f"CapEx per wired drop is approximately Rs. {total / 48:,.0f}, and "
        f"CapEx per connected client is approximately Rs. {total / 64:,.0f}. "
        "The estimate is 5.0% below the Rs. 6.00 lakh cap before any vendor "
        "discount, so there is limited headroom for price movement. The 5% "
        "contingency is intended to absorb minor scope changes; a large "
        "increase in switch count or a move to new rather than refurbished "
        "equipment would require a revised budget. Vendor quotations, GST "
        "treatment and warranty terms should be confirmed before purchase.")


def conclusion():
    chapter("8. Conclusion and Future Scope")
    subheading("8.1 Conclusion")
    body(
        "The project produced a complete LAN design for a 2,800 sq ft small "
        "office with 48 wired drops, 24 concurrent wireless clients and a "
        "100 Mbps internet service. The design uses a collapsed core, five "
        "VLANs, a contiguous VLSM plan, router-on-a-stick routing, central "
        "DHCP and DNS, NAT/PAT and explicit guest and management ACLs. The "
        "24-port engineering access switch is fully used by engineering PCs, "
        "while the core provides 21 spare ports for growth.")
    body(
        "The Python validation model executed 18 tests and all passed. It "
        "allocated 64 unique DHCP leases, resolved internal names, blocked "
        "guest access to internal resources, blocked staff and engineering "
        "access to management, allowed server administration, isolated guest "
        "wireless clients and produced two PAT translations. The experiment "
        "therefore confirms the logical correctness of the addressing and "
        "policy design, subject to the stated limitation that Cisco hardware "
        "or Packet Tracer was not available.")
    body(
        "The budgetary CapEx is Rs. 569,835 including 5% contingency, and the "
        "three-year TCO is Rs. 1,148,595. The design meets the Rs. 6.00 lakh "
        "capital cap and provides a clear bill of materials, port map, "
        "configuration templates, cost workbook and repeatable evidence. It "
        "is ready for vendor validation and a physical pilot.")
    subheading("8.2 Future Scope")
    bullet("Add a second 24-port access switch or replace the engineering switch with a 48-port model to provide local spare ports and support denser engineering seating.")
    bullet("Introduce 802.1X authentication and RADIUS for wired and wireless users instead of relying only on WPA2-PSK.")
    bullet("Add a wireless LAN controller or cloud management platform for central AP firmware, RF and guest portal management.")
    bullet("Extend monitoring with SNMP, NetFlow and syslog dashboards, and add UPS and environmental alerts.")
    bullet("Pilot IPv6 dual-stack and evaluate SD-WAN or a second ISP link for WAN redundancy.")
    bullet("Perform a physical RF survey and a hardware acceptance test covering PoE budget, throughput, failover and ACL behaviour.")


def references():
    chapter("References")
    refs = [
        "[1] B. A. Forouzan, Data Communications and Networking, 5th ed. New York, NY, USA: McGraw-Hill, 2013.",
        "[2] A. S. Tanenbaum and D. J. Wetherall, Computer Networks, 5th ed. Boston, MA, USA: Pearson, 2011.",
        "[3] Cisco Systems, Catalyst 2960-X Switch Configuration Guide. San Jose, CA, USA: Cisco Systems.",
        "[4] Cisco Systems, Cisco 2911 Integrated Services Router Data Sheet. San Jose, CA, USA: Cisco Systems.",
        "[5] IEEE Standard 802.1Q-2018, Bridges and Bridged Networks, IEEE, 2018.",
        "[6] R. Droms, RFC 2131: Dynamic Host Configuration Protocol, IETF, 1997.",
        "[7] S. Alexander and R. Droms, RFC 2132: DHCP Options and BOOTP Vendor Extensions, IETF, 1997.",
        "[8] P. Srisuresh and K. Egevang, RFC 3022: Traditional IP Network Address Translator, IETF, 2001.",
        "[9] Y. Rekhter et al., RFC 1918: Address Allocation for Private Internets, IETF, 1996.",
        "[10] Cisco Systems, Cisco Aironet 1830 Series Access Points Data Sheet. San Jose, CA, USA: Cisco Systems.",
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.35)
        p.paragraph_format.first_line_indent = Inches(-0.35)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = JUSTIFY
        run = p.add_run(ref)
        set_run_font(run, size=10.5)


def appendix():
    chapter("Appendix A \u2014 Port Map and Artifact Inventory")
    subheading("A.1 Port Allocation Summary")
    body(
        "The complete port map is supplied as PORT_MAP.csv. Table A.1 "
        "summarises the allocation and confirms that 48 physical drops are "
        "terminated while the core retains 21 spare ports.")
    port_rows = [
        ["Switch and ports", "Allocation"],
        ["NXS-CORE-SW Gi1/0/1", "Trunk to NXS-GW G0/0; native VLAN 99"],
        ["NXS-CORE-SW Gi1/0/2\u20133", "LACP Po1 fibre to NXS-ENG-SW Gi1/0/25\u201326"],
        ["NXS-CORE-SW Gi1/0/4\u20136", "Servers SRV-DNS, SRV-FILE, SRV-ERP; VLAN 10"],
        ["NXS-CORE-SW Gi1/0/7\u201323", "Staff printer and 16 staff PCs; VLAN 20"],
        ["NXS-CORE-SW Gi1/0/24\u201326", "AP-ENG, AP-STAFF, AP-MGMT trunks; native VLAN 99"],
        ["NXS-CORE-SW Gi1/0/27", "Engineering printer PRN-ENG; VLAN 30"],
        ["NXS-CORE-SW Gi1/0/28\u201348", "Spare; VLAN 999; administratively shut down"],
        ["NXS-ENG-SW Gi1/0/1\u201324", "Engineering PCs ENG-PC-01 to ENG-PC-24; VLAN 30"],
        ["NXS-ENG-SW Gi1/0/25\u201326", "LACP Po2 fibre to NXS-CORE-SW Gi1/0/2\u20133"],
    ]
    add_table(port_rows, [1.9, 4.35],
              "Table A.1 \u2014 Port allocation summary.", font_size=7.8,
              header_size=8.1)
    subheading("A.2 Artifact Inventory")
    artifacts = [
        ["Artifact", "Purpose"],
        ["01_Site_Survey/floor_plan.png", "Site survey and AP placement plan"],
        ["02_Network_Design/topology.png", "Logical topology"],
        ["02_Network_Design/vlan_map.png", "VLSM byte map"],
        ["03_Configuration/NXS-GW.cfg", "Router configuration template"],
        ["03_Configuration/NXS-CORE-SW.cfg", "Core switch configuration template"],
        ["03_Configuration/NXS-ENG-SW.cfg", "Engineering access switch template"],
        ["03_Configuration/PORT_MAP.csv", "Complete port map"],
        ["03_Configuration/AP_SSID_Plan.txt", "SSID, VLAN and security plan"],
        ["04_Simulation/network_model.py", "Python validation model"],
        ["04_Simulation/test_results.csv", "18-test evidence table"],
        ["04_Simulation/test_results.txt", "Readable validation log"],
        ["04_Simulation/dhcp_leases.csv", "64 DHCP leases"],
        ["04_Simulation/nat_table.csv", "PAT translations"],
        ["04_Simulation/dns_log.csv", "DNS resolution log"],
        ["04_Simulation/packet_trace.txt", "Representative packet paths"],
        ["04_Simulation/simulation_summary.json", "Summary metrics for the report"],
        ["04_Simulation/simulation_evidence.png", "Terminal evidence figure"],
        ["05_Cost_Analysis/BoM_and_Cost.xlsx", "Formatted BoM, summary and TCO"],
        ["05_Cost_Analysis/cost_breakdown.png", "CapEx distribution chart"],
    ]
    add_table(artifacts, [2.55, 3.7],
              "Table A.2 \u2014 Project artifact inventory.", font_size=7.5,
              header_size=8.0)
    a3 = subheading("A.3 Reproducibility")
    a3.paragraph_format.page_break_before = True
    body(
        "The figures, configuration templates, workbook and validation "
        "evidence can be regenerated from the project folder with the "
        "following commands. The report uses the generated artifacts, so a "
        "rerun should be followed by a report rebuild and a TOC update.")
    listing("Listing A.1 \u2014 Regeneration commands.", [
        "cd \"Assignment 8 Mini Project - Sanskar Chandawar\\06_Scripts\"",
        "python make_figures.py",
        "python generate_configs.py",
        "python make_cost_workbook.py",
        "cd ..\\04_Simulation",
        "python network_model.py",
    ], size=8.5)
    body(
        "Full DHCP, DNS and NAT evidence remains in the CSV files; the report "
        "shows representative rows to keep the printed document readable. "
        "The Cisco templates contain placeholders and must not be deployed "
        "until the secrets, IOS feature support and site-specific port labels "
        "have been verified.", first_line=0)


def build():
    global doc
    doc = Document()
    configure_styles(doc)
    configure_document(doc)
    doc.core_properties.title = P.PROJECT["title"]
    doc.core_properties.author = P.TEAM_NAMES
    doc.core_properties.subject = "Computer Networks Laboratory mini project"
    doc.core_properties.keywords = "LAN, VLAN, VLSM, DHCP, DNS, NAT, Cisco"
    doc.core_properties.comments = "Assignment 8 mini project report"

    summary = json.loads((PROJECT_ROOT / "04_Simulation" /
                          "simulation_summary.json").read_text(encoding="utf-8"))
    with (PROJECT_ROOT / "04_Simulation" / "test_results.csv").open(
            encoding="utf-8", newline="") as handle:
        test_rows = list(csv.DictReader(handle))
    with (PROJECT_ROOT / "04_Simulation" / "dhcp_leases.csv").open(
            encoding="utf-8", newline="") as handle:
        lease_rows = list(csv.DictReader(handle))
    with (PROJECT_ROOT / "04_Simulation" / "nat_table.csv").open(
            encoding="utf-8", newline="") as handle:
        nat_rows = list(csv.DictReader(handle))

    cover()
    abstract(summary)
    contents()
    introduction()
    principles()
    survey()
    design()
    implementation()
    testing(summary, test_rows, lease_rows, nat_rows)
    cost(summary)
    conclusion()
    references()
    appendix()

    settings = doc.settings.element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)

    doc.save(DOCX_OUT)
    print("wrote", DOCX_OUT)


if __name__ == "__main__":
    build()
