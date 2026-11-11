"""Generate the Excel / Google Sheets workbooks for every product tier.

Usage:  python3 build_workbooks.py [output_dir]

Produces, for each tier (starter, complete, premium):
  * <Brand>-<Tier>.xlsx           blank, ready to use (example assumptions only)
  * <Brand>-<Tier>-EXAMPLE.xlsx   same file filled with fictional sample data
plus the free lead-magnet <Brand>-Quick-Price-Check-FREE.xlsx.

Design rules (see docs/04_PRODUCT_SPECIFICATION.md):
  * no macros, no scripts, no external links
  * only functions supported by Excel 2019+/365, Excel for the web,
    Google Sheets and LibreOffice (checked by tests/test_workbooks.py)
  * plain ranges (no Excel "Tables"), so structured references never break
  * every formula mirrors kit/pricing.py, which is unit-tested
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Protection, Side
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand  # noqa: E402
import sample_data  # noqa: E402
from pricing import FREQUENCIES, PROPERTY_TYPES, SERVICE_TYPES, Settings  # noqa: E402

# ---------------------------------------------------------------- styles ----
C = brand.COLORS
FONT = "Arial"
USD = '"$"#,##0.00'
USD0 = '"$"#,##0'
PCT = "0.0%"
DATE = "mm/dd/yyyy"
TIME = "h:mm AM/PM"
NUM2 = "#,##0.00"

thin = Side(style="thin", color=C["line"])
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
INPUT_FILL = PatternFill("solid", fgColor=C["input"])
AUTO_FILL = PatternFill("solid", fgColor=C["auto"])
HEAD_FILL = PatternFill("solid", fgColor=C["primary"])
SECTION_FILL = PatternFill("solid", fgColor=C["primary_light"])
KEY_FILL = PatternFill("solid", fgColor=C["accent_light"])
UNLOCK = Protection(locked=False)

SVC = list(SERVICE_TYPES)
PROP = list(PROPERTY_TYPES)
FREQ = list(FREQUENCIES)
JOB_STATUS = ["Scheduled", "Confirmed", "In Progress", "Completed", "Cancelled"]
CLIENT_STATUS = ["Active", "Paused", "Former"]
PAY_STATUS = ["Received", "Paid", "Pending"]
CATEGORIES = [  # (category, group)
    ("Cleaning revenue", "Income"),
    ("Add-on services revenue", "Income"),
    ("Other income", "Income"),
    ("Wages & contractor pay", "Labor"),
    ("Payroll taxes & workers comp", "Labor"),
    ("Cleaning supplies", "Supplies"),
    ("Fuel & mileage", "Transport"),
    ("Vehicle maintenance", "Transport"),
    ("Card processing fees", "Other variable"),
    ("Other job expense", "Other variable"),
    ("Equipment & tools", "Fixed"),
    ("Insurance & bonding", "Fixed"),
    ("Marketing & advertising", "Fixed"),
    ("Phone, internet & software", "Fixed"),
    ("Rent & storage", "Fixed"),
    ("Licenses & permits", "Fixed"),
    ("Accounting & legal", "Fixed"),
    ("Taxes paid / set aside", "Tax"),
]
GROUPS = ["Labor", "Supplies", "Transport", "Other variable", "Fixed"]

CLIENT_ROWS = (5, 304)
SCHED_ROWS = (5, 604)
TX_ROWS = (5, 1504)
TIERS = {
    "starter": ["start", "settings", "calculator", "quotes", "margin"],
    "complete": ["start", "settings", "calculator", "quotes", "margin", "clients",
                 "schedule", "transactions", "summary", "estimate", "invoice"],
    "premium": ["start", "dashboard", "settings", "calculator", "quotes", "margin",
                "clients", "schedule", "transactions", "summary", "estimate",
                "invoice", "goals", "commercial", "crew", "checklists"],
}
SHEET_TITLES = {
    "start": "Start Here", "dashboard": "Dashboard", "settings": "Settings",
    "calculator": "Price Calculator", "quotes": "Quote Table",
    "margin": "Margin vs Markup", "clients": "Clients", "schedule": "Schedule",
    "transactions": "Transactions", "summary": "Monthly Summary",
    "estimate": "Estimate", "invoice": "Invoice", "goals": "Goal Planner",
    "commercial": "Commercial Bid", "crew": "Crew Cost", "checklists": "Checklists",
}


def font(size=10, bold=False, color=None, italic=False):
    return Font(name=FONT, size=size, bold=bold, italic=italic, color=color or C["ink"])


class Sheet:
    """Small helper around a worksheet with the brand styles."""

    def __init__(self, wb, title, tab_color=None):
        self.ws = wb.create_sheet(title)
        self.wb = wb
        self.ws.sheet_view.showGridLines = False
        self.ws.sheet_properties.tabColor = tab_color or C["primary"]

    def title(self, text, subtitle=None, width_cols="B:H"):
        ws = self.ws
        ws.row_dimensions[1].height = 8
        ws["B2"] = text
        ws["B2"].font = font(18, True, C["primary"])
        ws.row_dimensions[2].height = 28
        if subtitle:
            ws["B3"] = subtitle
            ws["B3"].font = font(10, False, C["muted"], italic=True)

    def section(self, ref, text, span=None):
        cell = self.ws[ref]
        cell.value = text
        cell.font = font(11, True, C["white"])
        cell.fill = HEAD_FILL
        if span:
            for row in self.ws[f"{ref}:{span}"]:
                for c in row:
                    c.fill = HEAD_FILL

    def label(self, ref, text, bold=False, note=None, note_ref=None):
        self.ws[ref] = text
        self.ws[ref].font = font(10, bold)
        if note and note_ref:
            self.ws[note_ref] = note
            self.ws[note_ref].font = font(9, False, C["muted"], italic=True)
            self.ws[note_ref].alignment = Alignment(wrap_text=False)

    def inp(self, ref, value=None, fmt=None):
        c = self.ws[ref]
        if value is not None:
            c.value = value
        c.fill = INPUT_FILL
        c.border = BORDER
        c.protection = UNLOCK
        c.font = font(10, False, C["ink"])
        if fmt:
            c.number_format = fmt
        return c

    def out(self, ref, formula, fmt=None, bold=False, key=False):
        c = self.ws[ref]
        c.value = formula
        c.fill = KEY_FILL if key else AUTO_FILL
        c.border = BORDER
        c.font = font(12 if key else 10, bold or key, C["primary_dark"] if key else C["ink"])
        if fmt:
            c.number_format = fmt
        return c

    def widths(self, **w):
        for col, width in w.items():
            self.ws.column_dimensions[col].width = width

    def header_row(self, row, headers, start_col=1, auto_cols=()):
        for i, h in enumerate(headers):
            c = self.ws.cell(row=row, column=start_col + i, value=h)
            auto = (start_col + i) in auto_cols
            c.font = font(10, True, C["white"])
            c.fill = PatternFill("solid", fgColor=C["primary_dark"] if auto else C["primary"])
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            c.border = BORDER
        self.ws.row_dimensions[row].height = 32

    def protect(self):
        p = self.ws.protection
        p.sheet = True
        p.formatColumns = False
        p.formatRows = False
        p.formatCells = False
        p.sort = False
        p.autoFilter = False
        p.selectLockedCells = False
        p.selectUnlockedCells = False


def name(wb, nm, ref):
    wb.defined_names[nm] = DefinedName(nm, attr_text=ref)


def dv_list(ws, formula, rng, allow_blank=True, prompt=None):
    dv = DataValidation(type="list", formula1=formula, allow_blank=allow_blank,
                        showErrorMessage=True, errorTitle="Pick from the list",
                        error="Please choose a value from the drop-down list.")
    if prompt:
        dv.promptTitle = "Tip"
        dv.prompt = prompt
        dv.showInputMessage = True
    ws.add_data_validation(dv)
    dv.add(rng)
    return dv


def dv_min(ws, rng, minimum=0, decimal=True, maximum=None, msg="Enter a number of 0 or more."):
    kwargs = dict(type="decimal" if decimal else "whole", allow_blank=True,
                  showErrorMessage=True, errorTitle="Invalid value", error=msg)
    if maximum is None:
        dv = DataValidation(operator="greaterThanOrEqual", formula1=str(minimum), **kwargs)
    else:
        dv = DataValidation(operator="between", formula1=str(minimum), formula2=str(maximum), **kwargs)
    ws.add_data_validation(dv)
    dv.add(rng)
    return dv


def quoted_list(items):
    return '"' + ",".join(items) + '"'


# ================================================================ sheets ====

def build_settings(wb, tier, example):
    sh = Sheet(wb, "Settings", C["accent"])
    ws = sh.ws
    s = Settings()
    sh.title("Settings", "Your business details and pricing assumptions. Yellow cells are yours to edit. "
             "All default numbers are EXAMPLES — replace them with your real costs.")
    sh.widths(A=2, B=34, C=22, D=70)
    biz = sample_data.BUSINESS if example else {k: "" for k in sample_data.BUSINESS}

    sh.section("B5", "YOUR BUSINESS", "D5")
    rows = [
        ("BizName", "Business name", biz["name"] or "Your Cleaning Company"),
        ("BizOwner", "Owner / contact name", biz["owner"]),
        ("BizPhone", "Phone", biz["phone"]),
        ("BizEmail", "Email", biz["email"]),
        ("BizAddress", "Business address (city, state)", biz["address"]),
        ("BizWeb", "Website or social page", biz["web"]),
    ]
    r = 6
    for nm, lab, val in rows:
        sh.label(f"B{r}", lab)
        sh.inp(f"C{r}", val or None)
        name(wb, nm, f"Settings!$C${r}")
        r += 1

    sh.section("B13", "LABOR & COSTS", "D13")
    rows = [
        ("Wage", "Cleaner pay per labor hour", s.wage, USD, "What you pay per hour worked (or your own target hourly pay)."),
        ("Burden", "Payroll burden %", s.payroll_burden, PCT, "Payroll taxes, workers comp, etc. Use 0% for 1099 contractors (ask your accountant)."),
        ("SqftRate", "Sq ft cleaned per labor hour", s.sqft_per_labor_hour, "#,##0", "EXAMPLE production rate for a standard clean. Time your own crew and replace it."),
        ("BedHours", "Extra labor hours per bedroom", s.hours_per_bedroom, NUM2, "EXAMPLE. Added on top of the square-footage time."),
        ("BathHours", "Extra labor hours per bathroom", s.hours_per_bathroom, NUM2, "EXAMPLE. Bathrooms usually take the longest."),
        ("MileCost", "Vehicle cost per mile", s.cost_per_mile, USD, "Fuel + wear. The IRS standard mileage rate is one reference; use your own."),
        ("Overhead", "Monthly overhead (fixed costs)", s.monthly_overhead, USD, "Insurance, phone, software, marketing, equipment… everything not tied to one job."),
        ("JobsPerMonth", "Expected jobs per month", s.jobs_per_month, "#,##0", "Used to spread overhead across jobs (overhead ÷ jobs)."),
        ("CardFee", "Card processing fee %", s.card_fee, "0.00%", "Fee your payment app charges on what the client pays. Use 0% for cash/check."),
    ]
    r = 14
    for nm, lab, val, fmt, note in rows:
        sh.label(f"B{r}", lab, note=note, note_ref=f"D{r}")
        sh.inp(f"C{r}", val, fmt)
        name(wb, nm, f"Settings!$C${r}")
        r += 1
    dv_min(ws, "C14:C22")

    sh.section("B24", "PRICING RULES", "D24")
    rows = [
        ("TargetMargin", "Target net profit MARGIN %", s.target_margin, PCT, "Profit as % of the PRICE (not markup on cost). See 'Margin vs Markup'."),
        ("TaxRate", "Sales tax % (if your state taxes cleaning)", s.sales_tax, "0.00%", "Many states do not tax residential cleaning — check your state. Leave 0% if not taxed."),
        ("RoundTo", "Round prices up to the nearest $", s.rounding, USD0, "e.g. 5 turns $142.30 into $145. Use 0 for no rounding."),
        ("MinPrice", "Minimum job price", s.minimum_price, USD, "You never quote below this, even for tiny jobs."),
        ("EstValidDays", "Estimates valid for (days)", 30, "0", "Shown on the Estimate as 'Valid until'."),
        ("InvoiceDays", "Invoice payment terms (days)", 7, "0", "Due date = invoice date + this many days."),
        ("PayMethods", "Payment methods (shown on invoices)", biz.get("pay_methods") or "Card, Zelle, Venmo, check", None, "Plain text. This kit does NOT process payments."),
        ("TrackerYear", "Year shown in summaries", 2026, "0", "Change at the start of each year (or keep one file per year)."),
        ("FollowUpDays", "Flag clients for follow-up after (days)", 45, "0", "Active clients with no visit booked and no service in this many days are flagged."),
    ]
    r = 25
    for nm, lab, val, fmt, note in rows:
        sh.label(f"B{r}", lab, note=note, note_ref=f"D{r}")
        sh.inp(f"C{r}", val, fmt)
        name(wb, nm, f"Settings!$C${r}")
        r += 1
    dv_min(ws, "C25:C26", 0, True, 0.95, "Enter a percentage between 0% and 95%.")
    dv_min(ws, "C27:C33")

    # --- lookup tables (row 36+) ---
    def table(top, title, headers, data, names, fmts):
        sh.section(f"B{top}", title, f"D{top}")
        for i, h in enumerate(headers):
            c = ws.cell(row=top + 1, column=2 + i, value=h)
            c.font = font(10, True)
            c.border = BORDER
        first = top + 2
        for j, rowvals in enumerate(data):
            for i, v in enumerate(rowvals):
                cell = ws.cell(row=first + j, column=2 + i)
                sh.inp(cell.coordinate, v, fmts[i])
        last = first + len(data) - 1
        for i, nm in enumerate(names):
            col = "BCD"[i]
            name(wb, nm, f"Settings!${col}${first}:${col}${last}")
        return first, last

    svc_rows = [(n, m) for n, m in SERVICE_TYPES.items()] + [(None, None), (None, None)]
    f, l = table(36, "SERVICE TYPES (time multipliers — EXAMPLES)", ["Service type", "Labor time ×"],
                 svc_rows, ["SvcNames", "SvcMult"], [None, "0.00"])
    sh.label("D37", "1.00 = standard clean. 1.75 = takes 75% longer. Add your own in the blank rows.")
    ws["D37"].font = font(9, False, C["muted"], True)
    prop_rows = [(n, m) for n, m in PROPERTY_TYPES.items()] + [(None, None)]
    table(46, "PROPERTY TYPES (time multipliers)", ["Property type", "Labor time ×"],
          prop_rows, ["PropNames", "PropMult"], [None, "0.00"])
    freq_rows = [(n, d, days) for n, (d, days) in FREQUENCIES.items()] + [(None, None, None)]
    table(56, "FREQUENCY DISCOUNTS (EXAMPLES)", ["Frequency", "Discount %", "Repeat every (days)"],
          freq_rows, ["FreqNames", "FreqDisc", "FreqDays"], [None, PCT, "0"])
    if tier != "starter":
        table(65, "EXPENSE & INCOME CATEGORIES", ["Category", "Group"],
              CATEGORIES + [(None, None)] * 4, ["CatNames", "CatGroup"], [None, None])
        dv_list(ws, quoted_list(["Income"] + GROUPS + ["Tax"]), "C67:C88")
    ws.freeze_panes = "A5"
    sh.protect()
    return sh


def calc_hours_formula(prop, svc, sqft, bed, bath, override):
    return (f'IF({override}<>"",{override},IF(OR({svc}="",{prop}=""),0,'
            f'(IFERROR({sqft}/SqftRate,0)+N({bed})*BedHours+N({bath})*BathHours)'
            f'*IFERROR(INDEX(SvcMult,MATCH({svc},SvcNames,0)),1)'
            f'*IFERROR(INDEX(PropMult,MATCH({prop},PropNames,0)),1)))')


def build_calculator(wb, example):
    sh = Sheet(wb, "Price Calculator", C["primary"])
    ws = sh.ws
    sh.title("Cleaning Price Calculator",
             "Fill the yellow cells. Your recommended price appears on the right. Blank optional cells use your Settings.")
    sh.widths(A=2, B=30, C=20, D=3, E=2, F=34, G=18, H=3, I=60)
    ex = sample_data.CALC_EXAMPLE if example else {}

    sh.section("B5", "1. THE JOB", "C5")
    inputs = [
        (6, "Client or job name", "client", None),
        (7, "Property type", "property", None),
        (8, "Service type", "service", None),
        (9, "Frequency", "frequency", None),
        (10, "Square feet", "sqft", "#,##0"),
        (11, "Bedrooms", "bedrooms", "0"),
        (12, "Bathrooms", "bathrooms", "0.0"),
        (13, "Crew size (cleaners on site)", "crew", "0"),
        (14, "Labor hours override (optional)", "hours_override", NUM2),
    ]
    for r, lab, key, fmt in inputs:
        sh.label(f"B{r}", lab)
        default = {"crew": 2, "property": "House", "service": "Standard Cleaning",
                   "frequency": "One-time"}.get(key) if not example else None
        sh.inp(f"C{r}", ex.get(key, default), fmt)
    sh.section("B16", "2. JOB COSTS", "C16")
    inputs2 = [
        (17, "Supplies for this job ($)", "supplies", USD),
        (18, "Round-trip miles", "miles", "#,##0"),
        (19, "Other direct costs ($)", "other_direct", USD),
        (20, "Extra discount % (promo, referral)", "extra_discount", PCT),
    ]
    for r, lab, key, fmt in inputs2:
        sh.label(f"B{r}", lab)
        sh.inp(f"C{r}", ex.get(key), fmt)
    sh.section("B22", "3. OPTIONAL OVERRIDES", "C22")
    inputs3 = [
        (23, "Hourly pay for this job", "wage_override", USD),
        (24, "Target margin for this job", "margin_override", PCT),
        (25, "Sales tax % for this job", "tax_override", "0.00%"),
    ]
    for r, lab, key, fmt in inputs3:
        sh.label(f"B{r}", lab)
        sh.inp(f"C{r}", ex.get(key), fmt)
    sh.section("B27", "4. CHECK A PRICE", "C27")
    sh.label("B28", "Price you are thinking of quoting")
    sh.inp("C28", ex.get("planned_price"), USD)

    dv_list(ws, "=Settings!$B$48:$B$54", "C7")
    dv_list(ws, "=Settings!$B$38:$B$45", "C8")
    dv_list(ws, "=Settings!$B$58:$B$63", "C9")
    dv_min(ws, "C10:C12")
    dv_min(ws, "C13", 1, False, None, "Crew size must be a whole number of 1 or more.")
    dv_min(ws, "C14")
    dv_min(ws, "C17:C19")
    dv_min(ws, "C20", 0, True, 0.9, "Enter a discount between 0% and 90%.")
    dv_min(ws, "C23")
    dv_min(ws, "C24", 0, True, 0.95, "Enter a margin between 0% and 95%.")
    dv_min(ws, "C25", 0, True, 0.3, "Enter a tax rate between 0% and 30%.")
    dv_min(ws, "C28")

    sh.section("F5", "RESULTS", "G5")
    hours = calc_hours_formula("C7", "C8", "C10", "C11", "C12", "C14")
    results = [
        (6, "Hourly pay used", '=IF(C23="",Wage,C23)', USD),
        (7, "Target margin used", '=IF(C24="",TargetMargin,C24)', PCT),
        (8, "Sales tax used", '=IF(C25="",TaxRate,C25)', "0.00%"),
        (9, "Estimated labor hours", "=" + hours, NUM2),
        (10, "Time on site (hours)", "=IF(N(C13)>0,G9/C13,G9)", NUM2),
        (11, "Labor cost (incl. burden)", "=G9*G6*(1+Burden)", USD),
        (12, "Supplies", "=N(C17)", USD),
        (13, "Travel", "=N(C18)*MileCost", USD),
        (14, "Other direct costs", "=N(C19)", USD),
        (15, "Direct job cost", "=SUM(G11:G14)", USD),
        (16, "Share of overhead", "=IF(JobsPerMonth>0,Overhead/JobsPerMonth,0)", USD),
        (17, "TOTAL COST OF THIS JOB", "=G15+G16", USD),
        (18, "Price before rounding", "=IF(1-G7-CardFee*(1+G8)<=0,0,G17/(1-G7-CardFee*(1+G8)))", USD),
        (19, "YOUR PRICE (per visit)", "=IF(OR(G9<=0,G17<=0,G18<=0),0,MAX(MinPrice,IF(RoundTo>0,ROUNDUP(G18/RoundTo,0)*RoundTo,G18)))", USD),
        (20, "Total discount shown to client", "=1-(1-IFERROR(INDEX(FreqDisc,MATCH(C9,FreqNames,0)),0))*(1-N(C20))", PCT),
        (21, "Regular price (before discount)", "=IF(G20<1,ROUNDUP(G19/(1-G20),0),G19)", USD),
        (22, "Discount amount", "=G21-G19", USD),
        (23, "Sales tax", "=G19*G8", USD),
        (24, "Client pays (price + tax)", "=G19+G23", USD),
        (25, "Card processing fee", "=G24*CardFee", USD),
        (26, "Gross profit (price − labor − supplies)", "=G19-(G11+G12)", USD),
        (27, "Gross margin", "=IF(G19>0,G26/G19,0)", PCT),
        (28, "Contribution (price − all job costs − fee)", "=G19-(G15+G25)", USD),
        (29, "Contribution margin", "=IF(G19>0,G28/G19,0)", PCT),
        (30, "NET PROFIT (after overhead share)", "=G28-G16", USD),
        (31, "Net profit margin", "=IF(G19>0,G30/G19,0)", PCT),
        (32, "Same profit as markup on cost", "=IF(G17>0,G30/G17,0)", PCT),
        (33, "Price per labor hour", "=IF(G9>0,G19/G9,0)", USD),
        (34, "Price per sq ft", "=IF(N(C10)>0,G19/C10,0)", '"$"#,##0.000'),
    ]
    for r, lab, f, fmt in results:
        key = r in (17, 19, 30)
        sh.label(f"F{r}", lab, bold=key)
        sh.out(f"G{r}", f, fmt, key=key)
    sh.section("F36", "CHECK A PRICE — RESULT", "G36")
    sh.label("F37", "Net profit at your price")
    sh.out("G37", '=IF(C28="","",C28-G17-C28*(1+G8)*CardFee)', USD)
    sh.label("F38", "Net margin at your price")
    sh.out("G38", '=IF(C28="","",IF(C28>0,G37/C28,0))', PCT)
    sh.label("F39", "Verdict")
    sh.out("G39", '=IF(C28="","Enter a price in C28",IF(G37<0,"LOSES MONEY",'
           'IF(G38<G7,"Below target margin","Meets target margin")))', None, bold=True)
    ws["B31"] = ('=IF(1-G7-CardFee*(1+G8)<=0,"⚠ Target margin + card fees must be below 100%.",'
                 'IF(COUNTIF(C10:C19,"<0")>0,"⚠ Negative numbers are not allowed.",'
                 'IF(AND(C14="",N(C10)=0,G9=0),"Enter square feet (or a labor hours override) to get a price.","")))')
    ws["B31"].font = font(10, True, C["danger"])
    ws["B31"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells("B31:C33")
    notes = [
        "HOW TO READ THIS",
        "• YOUR PRICE already includes your target profit margin, card fees and a share of overhead.",
        "• If a frequency discount applies, quote the Regular price and show the discount — you still keep your margin.",
        "• Gross margin ignores overhead; Net margin is what is left after everything.",
        "• Markup ≠ margin: a 30% markup on cost is only a 23.1% margin.",
        "• Default rates are EXAMPLES. Time your own jobs and update Settings.",
        "• Red verdict = the price does not cover your costs.",
    ]
    for i, t in enumerate(notes):
        c = ws.cell(row=6 + i, column=9, value=t)
        c.font = font(10 if i else 11, i == 0, C["primary"] if i == 0 else C["ink"])
    ws.conditional_formatting.add("G39", FormulaRule(formula=['G37<0'], fill=PatternFill("solid", fgColor=C["danger_light"]),
                                                     font=Font(name=FONT, bold=True, color=C["danger"])))
    ws.conditional_formatting.add("G39", FormulaRule(formula=['AND(ISNUMBER(G37),G37>=0,G38>=G7)'],
                                                     fill=PatternFill("solid", fgColor=C["success_light"]),
                                                     font=Font(name=FONT, bold=True, color=C["success"])))
    names = {"CalcHours": "G9", "CalcTotalCost": "G17", "CalcPrice": "G19", "CalcRegular": "G21",
             "CalcNetProfit": "G30", "CalcService": "C8", "CalcFrequency": "C9"}
    for nm, ref in names.items():
        name(wb, nm, f"'Price Calculator'!${ref[0]}${ref[1:]}")
    ws.print_area = "B2:G39"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    sh.protect()
    return sh


def build_quotes(wb, example):
    sh = Sheet(wb, "Quote Table", C["primary"])
    ws = sh.ws
    sh.title("Quote Table — price many jobs at once",
             "One row per job. Uses the rates in Settings. Grey columns calculate automatically.")
    headers = ["Client / job", "Property type", "Service type", "Frequency", "Sq ft", "Bedrooms",
               "Bathrooms", "Crew", "Labor hrs override", "Supplies $", "Round-trip miles",
               "Other costs $", "Extra discount %", "Labor hours", "Total cost", "YOUR PRICE",
               "Regular price", "Net profit", "Net margin", "Price / labor hr"]
    sh.header_row(4, headers, 1, auto_cols=range(14, 21))
    widths = [24, 18, 20, 15, 9, 9, 10, 7, 11, 10, 10, 10, 10, 10, 12, 12, 12, 12, 10, 11]
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    first, last = 5, 54
    rows = sample_data.QUOTE_ROWS if example else []
    for r in range(first, last + 1):
        data = rows[r - first] if r - first < len(rows) else None
        for col in range(1, 14):
            c = ws.cell(row=r, column=col)
            if data:
                c.value = data[col - 1]
            c.protection = UNLOCK
            c.border = BORDER
            c.font = font()
        ws[f"E{r}"].number_format = "#,##0"
        ws[f"J{r}"].number_format = USD
        ws[f"L{r}"].number_format = USD
        ws[f"M{r}"].number_format = PCT
        hrs = calc_hours_formula(f"B{r}", f"C{r}", f"E{r}", f"F{r}", f"G{r}", f"I{r}")
        den = "(1-TargetMargin-CardFee*(1+TaxRate))"
        f = {
            "N": f'=IF(C{r}="","",{hrs})',
            "O": f'=IF(N{r}="","",N{r}*Wage*(1+Burden)+N(J{r})+N(K{r})*MileCost+N(L{r})+IF(JobsPerMonth>0,Overhead/JobsPerMonth,0))',
            "P": f'=IF(O{r}="","",IF({den}<=0,"Check margin",IF(OR(O{r}<=0,N(N{r})<=0),0,MAX(MinPrice,IF(RoundTo>0,ROUNDUP(O{r}/{den}/RoundTo,0)*RoundTo,O{r}/{den})))))',
            "Q": f'=IF(OR(P{r}="",NOT(ISNUMBER(P{r}))),"",IFERROR(ROUNDUP(P{r}/((1-IFERROR(INDEX(FreqDisc,MATCH(D{r},FreqNames,0)),0))*(1-N(M{r}))),0),P{r}))',
            "R": f'=IF(OR(P{r}="",NOT(ISNUMBER(P{r}))),"",P{r}-O{r}-P{r}*(1+TaxRate)*CardFee)',
            "S": f'=IF(OR(R{r}="",N(P{r})=0),"",R{r}/P{r})',
            "T": f'=IF(OR(R{r}="",N(N{r})=0),"",P{r}/N{r})',
        }
        fmts = {"N": NUM2, "O": USD, "P": USD, "Q": USD, "R": USD, "S": PCT, "T": USD}
        for col, formula in f.items():
            c = ws[f"{col}{r}"]
            c.value = formula
            c.fill = KEY_FILL if col == "P" else AUTO_FILL
            c.border = BORDER
            c.number_format = fmts[col]
            c.font = font(10, col == "P")
    dv_list(ws, "=Settings!$B$48:$B$54", f"B{first}:B{last}")
    dv_list(ws, "=Settings!$B$38:$B$45", f"C{first}:C{last}")
    dv_list(ws, "=Settings!$B$58:$B$63", f"D{first}:D{last}")
    dv_min(ws, f"E{first}:G{last}")
    dv_min(ws, f"H{first}:H{last}", 1, False)
    dv_min(ws, f"I{first}:L{last}")
    dv_min(ws, f"M{first}:M{last}", 0, True, 0.9)
    ws.conditional_formatting.add(f"S{first}:S{last}", CellIsRule(operator="lessThan", formula=["TargetMargin"],
                                  fill=PatternFill("solid", fgColor=C["danger_light"])))
    ws.freeze_panes = "B5"
    ws.auto_filter.ref = f"A4:T{last}"
    ws.print_area = f"A1:T{last}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    sh.protect()


def build_margin(wb):
    sh = Sheet(wb, "Margin vs Markup", C["accent"])
    ws = sh.ws
    sh.title("Margin vs Markup", "The #1 pricing mistake: adding 30% to your cost does NOT give you a 30% profit margin.")
    sh.widths(A=2, B=36, C=18, D=4, E=70)
    sh.section("B5", "CONVERTER", "C5")
    sh.label("B6", "Your cost ($)")
    sh.inp("C6", 100, USD)
    sh.label("B7", "Markup % you add to cost")
    sh.inp("C7", 0.30, PCT)
    sh.label("B8", "→ Price with that markup")
    sh.out("C8", "=C6*(1+C7)", USD)
    sh.label("B9", "→ Actual profit MARGIN you get")
    sh.out("C9", "=IF(C8>0,(C8-C6)/C8,0)", PCT, key=True)
    sh.label("B11", "Profit margin % you WANT")
    sh.inp("C11", 0.30, PCT)
    sh.label("B12", "→ Price you need")
    sh.out("C12", '=IF(C11<1,C6/(1-C11),"Margin must be < 100%")', USD, key=True)
    sh.label("B13", "→ Markup that equals")
    sh.out("C13", '=IF(C11<1,C11/(1-C11),"")', PCT)
    dv_min(ws, "C6")
    dv_min(ws, "C7", 0, True, 10)
    dv_min(ws, "C11", 0, True, 0.99, "Enter a margin between 0% and 99%.")
    sh.section("B15", "QUICK REFERENCE", "C15")
    ws["B16"], ws["C16"] = "Margin wanted", "Markup needed"
    ws["B16"].font = ws["C16"].font = font(10, True)
    for i, m in enumerate([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]):
        r = 17 + i
        ws[f"B{r}"] = m
        ws[f"B{r}"].number_format = PCT
        sh.out(f"C{r}", f"=B{r}/(1-B{r})", PCT)
    text = [
        "Why it matters",
        "Margin = profit ÷ PRICE.   Markup = profit ÷ COST.",
        "If a job costs you $100 and you charge $130, you made $30 — that is 30% markup but only 23.1% margin.",
        "To keep 30 cents of every dollar the client pays, you must charge $142.86 on a $100 cost.",
        "The Price Calculator always solves for MARGIN, so your target is actually reached.",
        "",
        "Gross vs net",
        "Gross margin looks only at labor + supplies. Net margin also covers travel, card fees and overhead",
        "(insurance, phone, marketing…). Net margin is what you actually keep before income taxes.",
        "",
        "Profit is not cash",
        "A job can be profitable on paper while the client has not paid yet. The Monthly Summary shows",
        "estimated profit and cash received separately.",
    ]
    for i, t in enumerate(text):
        c = ws.cell(row=5 + i, column=5, value=t)
        c.font = font(11 if t in ("Why it matters", "Gross vs net", "Profit is not cash") else 10,
                      t in ("Why it matters", "Gross vs net", "Profit is not cash"),
                      C["primary"] if t in ("Why it matters", "Gross vs net", "Profit is not cash") else C["ink"])
    sh.protect()


def build_clients(wb, example):
    sh = Sheet(wb, "Clients", C["success"])
    ws = sh.ws
    sh.title("Clients", "One row per client. Only collect what you need to do the job. "
             "Grey columns update automatically from the Schedule.")
    headers = ["Client ID", "Client name *", "Company", "Phone", "Email", "Service address",
               "Usual service", "Frequency", "Agreed price", "Status", "Notes (access, pets, preferences)",
               "Last completed visit", "Next booked visit", "Days since last visit", "Follow-up?",
               "Completed visits", "Lifetime revenue"]
    sh.header_row(4, headers, 1, auto_cols=[1] + list(range(12, 18)))
    widths = [9, 24, 18, 15, 26, 32, 20, 15, 12, 10, 36, 13, 13, 11, 12, 11, 13]
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    data = sample_data.CLIENTS if example else []
    a, b = CLIENT_ROWS
    for r in range(a, b + 1):
        d = data[r - a] if r - a < len(data) else None
        for col in range(2, 12):
            c = ws.cell(row=r, column=col)
            if d:
                c.value = d[col - 2]
            c.protection = UNLOCK
            c.border = BORDER
            c.font = font()
        ws[f"I{r}"].number_format = USD
        f = {
            "A": f'=IF(B{r}="","","C"&TEXT(ROW()-4,"000"))',
            "L": f'=IF(B{r}="","",IFERROR(1/(1/_xlfn.MAXIFS(Schedule!$A:$A,Schedule!$C:$C,B{r},Schedule!$I:$I,"Completed")),""))',
            "M": f'=IF(B{r}="","",IFERROR(1/(1/_xlfn.MINIFS(Schedule!$A:$A,Schedule!$C:$C,B{r},Schedule!$A:$A,">="&TODAY(),Schedule!$I:$I,"<>Cancelled")),""))',
            "N": f'=IF(L{r}="","",TODAY()-L{r})',
            "O": f'=IF(B{r}="","",IF(AND(J{r}="Active",M{r}="",OR(L{r}="",N(N{r})>FollowUpDays)),"Follow up",""))',
            "P": f'=IF(B{r}="","",COUNTIFS(Schedule!$C:$C,B{r},Schedule!$I:$I,"Completed"))',
            "Q": f'=IF(B{r}="","",SUMIFS(Schedule!$F:$F,Schedule!$C:$C,B{r},Schedule!$I:$I,"Completed"))',
        }
        fmts = {"A": None, "L": DATE, "M": DATE, "N": "0", "O": None, "P": "0", "Q": USD}
        for col, formula in f.items():
            c = ws[f"{col}{r}"]
            c.value = formula
            c.fill = AUTO_FILL
            c.border = BORDER
            c.font = font(10, col == "O", C["danger"] if col == "O" else None)
            if fmts[col]:
                c.number_format = fmts[col]
    dv_list(ws, "=Settings!$B$38:$B$45", f"G{a}:G{b}")
    dv_list(ws, "=Settings!$B$58:$B$63", f"H{a}:H{b}")
    dv_list(ws, quoted_list(CLIENT_STATUS), f"J{a}:J{b}")
    dv_min(ws, f"I{a}:I{b}")
    ws.freeze_panes = "C5"
    ws.auto_filter.ref = f"A4:Q{b}"
    name(wb, "ClientNames", f"Clients!$B${a}:$B${b}")
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def build_schedule(wb, example):
    sh = Sheet(wb, "Schedule", C["success"])
    ws = sh.ws
    sh.title("Schedule", "One row per visit. Sort or filter by date. Grey columns are automatic. "
             "Upcoming 7 days are highlighted; mark finished visits as Completed.")
    headers = ["Date", "Start time", "Client", "Service address", "Service type", "Price",
               "Labor hours", "Assigned to", "Status", "Notes", "Day", "Suggested next visit", "Month"]
    sh.header_row(4, headers, 1, auto_cols=[4, 11, 12, 13])
    widths = [12, 10, 24, 32, 20, 11, 10, 16, 13, 30, 7, 14, 10]
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    data = sample_data.SCHEDULE if example else []
    a, b = SCHED_ROWS
    for r in range(a, b + 1):
        d = data[r - a] if r - a < len(data) else None
        for col in [1, 2, 3, 5, 6, 7, 8, 9, 10]:
            c = ws.cell(row=r, column=col)
            if d:
                c.value = d[[1, 2, 3, 5, 6, 7, 8, 9, 10].index(col)]
            c.protection = UNLOCK
            c.border = BORDER
            c.font = font()
        ws[f"A{r}"].number_format = DATE
        ws[f"B{r}"].number_format = TIME
        ws[f"F{r}"].number_format = USD
        ws[f"G{r}"].number_format = NUM2
        f = {
            "D": f'=IF(C{r}="","",IFERROR(INDEX(Clients!$F:$F,MATCH(C{r},Clients!$B:$B,0)),""))',
            "K": f'=IF(A{r}="","",CHOOSE(WEEKDAY(A{r}),"Sun","Mon","Tue","Wed","Thu","Fri","Sat"))',
            "L": f'=IF(OR(A{r}="",C{r}="",I{r}="Cancelled"),"",IFERROR(IF(INDEX(FreqDays,MATCH(INDEX(Clients!$H:$H,MATCH(C{r},Clients!$B:$B,0)),FreqNames,0))>0,A{r}+INDEX(FreqDays,MATCH(INDEX(Clients!$H:$H,MATCH(C{r},Clients!$B:$B,0)),FreqNames,0)),""),""))',
            "M": f'=IF(A{r}="","",DATE(YEAR(A{r}),MONTH(A{r}),1))',
        }
        fmts = {"D": None, "K": None, "L": DATE, "M": "mmm yyyy"}
        for col, formula in f.items():
            c = ws[f"{col}{r}"]
            c.value = formula
            c.fill = AUTO_FILL
            c.border = BORDER
            c.font = font()
            if fmts[col]:
                c.number_format = fmts[col]
    dv_list(ws, f"=Clients!$B${CLIENT_ROWS[0]}:$B${CLIENT_ROWS[1]}", f"C{a}:C{b}",
            prompt="Add the client on the Clients sheet first.")
    dv_list(ws, "=Settings!$B$38:$B$45", f"E{a}:E{b}")
    dv_list(ws, quoted_list(JOB_STATUS), f"I{a}:I{b}")
    dv_min(ws, f"F{a}:G{b}")
    dvd = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True,
                         showErrorMessage=True, errorTitle="Invalid date", error="Enter a date like 03/15/2026.")
    ws.add_data_validation(dvd)
    dvd.add(f"A{a}:A{b}")
    rng = f"A{a}:M{b}"
    status_colors = {"Completed": C["success_light"], "Cancelled": C["muted_light"],
                     "In Progress": C["accent_light"], "Confirmed": C["primary_light"]}
    for st, color in status_colors.items():
        ws.conditional_formatting.add(f"I{a}:I{b}", CellIsRule(operator="equal", formula=[f'"{st}"'],
                                      fill=PatternFill("solid", fgColor=color)))
    ws.conditional_formatting.add(rng, FormulaRule(
        formula=[f'AND($A{a}<>"",$A{a}>=TODAY(),$A{a}<=TODAY()+7,$I{a}<>"Cancelled",$I{a}<>"Completed")'],
        font=Font(name=FONT, bold=True, color=C["primary_dark"])))
    ws.freeze_panes = "D5"
    ws.auto_filter.ref = f"A4:M{b}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def build_transactions(wb, example):
    sh = Sheet(wb, "Transactions", C["accent"])
    ws = sh.ws
    sh.title("Transactions — money in and money out",
             "Log every payment received and every expense. Mark unpaid items as Pending. "
             "This is a management tool, not accounting or tax advice.")
    headers = ["Date", "Category", "Description", "Client (optional)", "Service type (income)",
               "Amount ($)", "Payment status", "Type", "Group", "Month"]
    sh.header_row(4, headers, 1, auto_cols=[8, 9, 10])
    for col, w in zip("ABCDEFGHIJ", [12, 28, 32, 22, 20, 12, 13, 10, 14, 10]):
        ws.column_dimensions[col].width = w
    data = sample_data.TRANSACTIONS if example else []
    a, b = TX_ROWS
    for r in range(a, b + 1):
        d = data[r - a] if r - a < len(data) else None
        for col in range(1, 8):
            c = ws.cell(row=r, column=col)
            if d:
                c.value = d[col - 1]
            c.protection = UNLOCK
            c.border = BORDER
            c.font = font()
        ws[f"A{r}"].number_format = DATE
        ws[f"F{r}"].number_format = USD
        f = {
            "I": f'=IF(B{r}="","",IFERROR(INDEX(CatGroup,MATCH(B{r},CatNames,0)),"Other variable"))',
            "H": f'=IF(B{r}="","",IF(I{r}="Income","Income","Expense"))',
            "J": f'=IF(A{r}="","",DATE(YEAR(A{r}),MONTH(A{r}),1))',
        }
        for col, formula in f.items():
            c = ws[f"{col}{r}"]
            c.value = formula
            c.fill = AUTO_FILL
            c.border = BORDER
            c.font = font()
        ws[f"J{r}"].number_format = "mmm yyyy"
    dv_list(ws, "=Settings!$B$67:$B$88", f"B{a}:B{b}")
    dv_list(ws, "=Settings!$B$38:$B$45", f"E{a}:E{b}")
    dv_list(ws, quoted_list(PAY_STATUS), f"G{a}:G{b}",
            prompt="Income: Received or Pending. Expenses: Paid or Pending.")
    dv_min(ws, f"F{a}:F{b}", 0, True, None, "Enter the amount as a positive number. The category decides if it is income or expense.")
    dvd = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True,
                         showErrorMessage=True, errorTitle="Invalid date", error="Enter a date like 03/15/2026.")
    ws.add_data_validation(dvd)
    dvd.add(f"A{a}:A{b}")
    ws.conditional_formatting.add(f"G{a}:G{b}", CellIsRule(operator="equal", formula=['"Pending"'],
                                  fill=PatternFill("solid", fgColor=C["accent_light"])))
    ws.freeze_panes = "B5"
    ws.auto_filter.ref = f"A4:J{b}"


def build_summary(wb):
    sh = Sheet(wb, "Monthly Summary", C["accent"])
    ws = sh.ws
    sh.title("Monthly Summary", "Calculated from Transactions and Schedule for the year set in Settings. "
             "Estimated profit is not the same as cash in the bank.")
    ws.column_dimensions["A"].width = 2
    ws.column_dimensions["B"].width = 34
    for i in range(13):
        ws.column_dimensions[chr(67 + i)].width = 12
    ws["B4"] = "Year"
    ws["B4"].font = font(10, True)
    sh.out("C4", "=TrackerYear", "0", bold=True)
    months = [chr(67 + i) for i in range(12)]  # C..N
    ws["B5"] = "Month"
    ws["B5"].font = font(10, True, C["white"])
    ws["B5"].fill = HEAD_FILL
    for i, col in enumerate(months):
        c = ws[f"{col}5"]
        c.value = f"=DATE($C$4,{i + 1},1)"
        c.number_format = "mmm"
        c.font = font(10, True, C["white"])
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="center")
    ws["O5"] = "Year total"
    ws["O5"].font = font(10, True, C["white"])
    ws["O5"].fill = PatternFill("solid", fgColor=C["primary_dark"])
    T = "Transactions!"
    rows = [
        (6, "Revenue (earned)", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$H:$H,"Income")', USD, True),
        (7, "  of which received (cash in)", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$H:$H,"Income",{T}$G:$G,"Received")', USD, False),
        (8, "Labor", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$I:$I,"Labor")', USD, False),
        (9, "Supplies", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$I:$I,"Supplies")', USD, False),
        (10, "Transport", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$I:$I,"Transport")', USD, False),
        (11, "Other variable costs", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$I:$I,"Other variable")', USD, False),
        (12, "Fixed costs (overhead)", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$I:$I,"Fixed")', USD, False),
        (13, "Total expenses", lambda m: f"=SUM({m}8:{m}12)", USD, True),
        (14, "ESTIMATED PROFIT (before income tax)", lambda m: f"={m}6-{m}13", USD, True),
        (15, "Profit margin", lambda m: f'=IF({m}6>0,{m}14/{m}6,0)', PCT, False),
        (16, "Taxes paid / set aside", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$I:$I,"Tax")', USD, False),
        (17, "Profit after tax set-aside", lambda m: f"={m}14-{m}16", USD, True),
        (19, "Cash in (received)", lambda m: f"={m}7", USD, False),
        (20, "Cash out (expenses + taxes paid)", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$H:$H,"Expense",{T}$G:$G,"Paid")', USD, False),
        (21, "NET CASH FLOW", lambda m: f"={m}19-{m}20", USD, True),
        (22, "Unpaid client balances (pending income)", lambda m: f'=SUMIFS({T}$F:$F,{T}$J:$J,{m}$5,{T}$H:$H,"Income",{T}$G:$G,"Pending")', USD, False),
        (24, "Visits completed (Schedule)", lambda m: f'=COUNTIFS(Schedule!$M:$M,{m}$5,Schedule!$I:$I,"Completed")', "0", False),
        (25, "Value of completed visits", lambda m: f'=SUMIFS(Schedule!$F:$F,Schedule!$M:$M,{m}$5,Schedule!$I:$I,"Completed")', USD, False),
        (26, "Average price per visit", lambda m: f'=IF({m}24>0,{m}25/{m}24,0)', USD, False),
        (27, "Labor hours on completed visits", lambda m: f'=SUMIFS(Schedule!$G:$G,Schedule!$M:$M,{m}$5,Schedule!$I:$I,"Completed")', NUM2, False),
        (28, "Revenue per labor hour", lambda m: f'=IF({m}27>0,{m}25/{m}27,0)', USD, False),
        (29, "Cancelled visits", lambda m: f'=COUNTIFS(Schedule!$M:$M,{m}$5,Schedule!$I:$I,"Cancelled")', "0", False),
    ]
    for r, lab, fn, fmt, bold in rows:
        ws[f"B{r}"] = lab
        ws[f"B{r}"].font = font(10, bold)
        for col in months:
            sh.out(f"{col}{r}", fn(col), fmt, bold=bold)
        if r in (15,):
            total = '=IF(O6>0,O14/O6,0)'
        elif r == 26:
            total = '=IF(O24>0,O25/O24,0)'
        elif r == 28:
            total = '=IF(O27>0,O25/O27,0)'
        else:
            total = f"=SUM(C{r}:N{r})"
        sh.out(f"O{r}", total, fmt, bold=True)
    for r in (14, 17, 21):
        ws.conditional_formatting.add(f"C{r}:O{r}", CellIsRule(operator="lessThan", formula=["0"],
                                      font=Font(name=FONT, bold=True, color=C["danger"])))

    # Period comparison
    sh.section("B32", "COMPARE A MONTH WITH THE MONTH BEFORE", "F32")
    ws["B33"] = "Month to review (1–12)"
    sh.inp("C33", 6 if wb._example else dt.date.today().month, "0")
    dv_min(ws, "C33", 1, False, 12, "Enter a month number from 1 to 12.")
    for col, h in zip("CDEF", ["This month", "Previous month", "Change $", "Change %"]):
        ws[f"{col}34"] = h
        ws[f"{col}34"].font = font(10, True)
    ws["B34"] = '=TEXT(DATE(C4,C33,1),"mmmm yyyy")'
    ws["B34"].font = font(10, True)
    this_m, prev_m = "DATE($C$4,$C$33,1)", "EDATE(DATE($C$4,$C$33,1),-1)"
    comp = [
        (35, "Revenue", 'SUMIFS({T}$F:$F,{T}$J:$J,{m},{T}$H:$H,"Income")'),
        (36, "Total expenses (excl. taxes)", 'SUMIFS({T}$F:$F,{T}$J:$J,{m},{T}$H:$H,"Expense")-SUMIFS({T}$F:$F,{T}$J:$J,{m},{T}$I:$I,"Tax")'),
        (37, "Estimated profit", None),
        (38, "Visits completed", 'COUNTIFS(Schedule!$M:$M,{m},Schedule!$I:$I,"Completed")'),
    ]
    for r, lab, tmpl in comp:
        ws[f"B{r}"] = lab
        ws[f"B{r}"].font = font(10, r == 37)
        fmt = "0" if r == 38 else USD
        if tmpl:
            sh.out(f"C{r}", "=" + tmpl.format(T=T, m=this_m), fmt)
            sh.out(f"D{r}", "=" + tmpl.format(T=T, m=prev_m), fmt)
        else:
            sh.out(f"C{r}", "=C35-C36", fmt, bold=True)
            sh.out(f"D{r}", "=D35-D36", fmt, bold=True)
        sh.out(f"E{r}", f"=C{r}-D{r}", fmt)
        sh.out(f"F{r}", f'=IF(D{r}=0,"n/a",(C{r}-D{r})/ABS(D{r}))', PCT)

    # Results by service type
    sh.section("H32", "RESULTS BY SERVICE TYPE (year)", "L32")
    for col, h in zip("HIJKL", ["Service type", "Revenue", "% of revenue", "Visits done", "Avg price"]):
        ws[f"{col}33"] = h
        ws[f"{col}33"].font = font(10, True)
    y0, y1 = "DATE($C$4,1,1)", "DATE($C$4,12,31)"
    for i in range(8):
        r = 34 + i
        sh.out(f"H{r}", f'=IF(INDEX(SvcNames,{i + 1})="","",INDEX(SvcNames,{i + 1}))')
        sh.out(f"I{r}", f'=IF(H{r}="","",SUMIFS({T}$F:$F,{T}$E:$E,H{r},{T}$H:$H,"Income",{T}$A:$A,">="&{y0},{T}$A:$A,"<="&{y1}))', USD)
        sh.out(f"J{r}", f'=IF(OR(H{r}="",$O$6=0),"",I{r}/$O$6)', PCT)
        sh.out(f"K{r}", f'=IF(H{r}="","",COUNTIFS(Schedule!$E:$E,H{r},Schedule!$I:$I,"Completed",Schedule!$A:$A,">="&{y0},Schedule!$A:$A,"<="&{y1}))', "0")
        sh.out(f"L{r}", f'=IF(OR(H{r}="",N(K{r})=0),"",SUMIFS(Schedule!$F:$F,Schedule!$E:$E,H{r},Schedule!$I:$I,"Completed",Schedule!$A:$A,">="&{y0},Schedule!$A:$A,"<="&{y1})/K{r})', USD)

    chart = BarChart()
    chart.type = "col"
    chart.title = "Revenue, expenses and estimated profit by month"
    chart.y_axis.title = "USD"
    chart.y_axis.numFmt = '"$"#,##0'
    chart.height, chart.width = 8, 26
    for r in (6, 13, 14):
        ref = Reference(ws, min_col=2, max_col=14, min_row=r, max_row=r)
        chart.add_data(ref, titles_from_data=True, from_rows=True)
    chart.set_categories(Reference(ws, min_col=3, max_col=14, min_row=5, max_row=5))
    for s, color in zip(chart.series, [C["primary"], C["accent"], C["success"]]):
        s.graphicalProperties.solidFill = color
        s.graphicalProperties.line.solidFill = color
    ws.add_chart(chart, "B44")
    ws.freeze_panes = "C6"
    ws.print_area = "B2:O42"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    sh.protect()


def build_document(wb, kind, example):
    """Estimate or Invoice — printable, one page."""
    is_inv = kind == "invoice"
    sh = Sheet(wb, "Invoice" if is_inv else "Estimate", C["primary_dark"])
    ws = sh.ws
    sh.widths(A=2, B=40, C=10, D=13, E=15, F=16, G=3, H=48)
    ex = sample_data.INVOICE if is_inv else sample_data.ESTIMATE
    ex = ex if example else {}
    ws["B2"] = "=BizName"
    ws["B2"].font = font(18, True, C["primary"])
    for i, nm in enumerate(["BizAddress", "BizPhone", "BizEmail", "BizWeb"]):
        ws[f"B{3 + i}"] = f'=IF({nm}="","",{nm})'
        ws[f"B{3 + i}"].font = font(10, False, C["muted"])
    ws["E2"] = "INVOICE" if is_inv else "ESTIMATE"
    ws["E2"].font = font(22, True, C["primary_dark"])
    ws.merge_cells("E2:F2")
    ws["E2"].alignment = Alignment(horizontal="right")
    meta = [("Invoice #" if is_inv else "Estimate #", "number", None),
            ("Date", "date", DATE)]
    r = 3
    for lab, key, fmt in meta:
        ws[f"E{r}"] = lab
        ws[f"E{r}"].font = font(10, True)
        ws[f"E{r}"].alignment = Alignment(horizontal="right")
        sh.inp(f"F{r}", ex.get(key), fmt)
        r += 1
    ws["E5"] = "Due date" if is_inv else "Valid until"
    ws["E5"].font = font(10, True)
    ws["E5"].alignment = Alignment(horizontal="right")
    sh.out("F5", '=IF(F4="","",F4+' + ("InvoiceDays" if is_inv else "EstValidDays") + ")", DATE)

    ws["B8"] = "BILL TO" if is_inv else "PREPARED FOR"
    ws["B8"].font = font(10, True, C["white"])
    ws["B8"].fill = HEAD_FILL
    sh.inp("B9", ex.get("client"))
    dv_list(ws, f"=Clients!$B${CLIENT_ROWS[0]}:$B${CLIENT_ROWS[1]}", "B9",
            prompt="Pick a client from your Clients sheet (or type a name).")
    lookups = [("C", "Company"), ("F", "Address"), ("E", "Email"), ("D", "Phone")]
    for i, (col, _lab) in enumerate(lookups):
        c = ws[f"B{10 + i}"]
        c.value = f'=IF($B$9="","",IFERROR(""&INDEX(Clients!${col}:${col},MATCH($B$9,Clients!$B:$B,0)),""))'
        c.font = font(10, False, C["muted"])
    ws["D8"] = "SERVICE DETAILS"
    ws["D8"].font = font(10, True, C["white"])
    for col in "DEF":
        ws[f"{col}8"].fill = HEAD_FILL
    ws["D9"] = "Service date"
    sh.inp("E9", ex.get("service_date"), DATE)
    ws.merge_cells("E9:F9")
    ws["D10"] = "Frequency"
    sh.inp("E10", ex.get("frequency"))
    ws.merge_cells("E10:F10")
    dv_list(ws, "=Settings!$B$58:$B$63", "E10")
    ws["D11"] = "Address"
    ws["E11"] = '=IF(B13="","",B13)' if False else '=IF($B$9="","",IFERROR(""&INDEX(Clients!$F:$F,MATCH($B$9,Clients!$B:$B,0)),""))'
    ws.merge_cells("E11:F11")
    for ref in ("D9", "D10", "D11"):
        ws[ref].font = font(10, True)

    hdr = ["Description", "Qty", "Unit price", "", "Amount"]
    for i, h in enumerate(["Description", "", "Qty", "Unit price", "Amount"]):
        c = ws.cell(row=15, column=2 + i, value=h or None)
        c.font = font(10, True, C["white"])
        c.fill = HEAD_FILL
        c.alignment = Alignment(horizontal="left" if i == 0 else "right")
    del hdr
    items = ex.get("items", [])
    for i in range(10):
        r = 16 + i
        it = items[i] if i < len(items) else (None, None, None)
        sh.inp(f"B{r}", it[0])
        ws.merge_cells(f"B{r}:C{r}")
        sh.inp(f"D{r}", it[1], "0.##")
        sh.inp(f"E{r}", it[2], USD)
        sh.out(f"F{r}", f'=IF(OR(D{r}="",E{r}=""),"",D{r}*E{r})', USD)
    dv_min(ws, "D16:E25")
    tot = [
        (27, "Subtotal", "=SUM(F16:F25)", None),
        (28, "Discount %", None, PCT),
        (29, "Discount", "=-F27*N(E28)", None),
        (30, "Sales tax % (blank = Settings)", None, "0.00%"),
        (31, "Sales tax", "=(F27+F29)*IF(E30=\"\",TaxRate,E30)", None),
        (32, "TOTAL", "=F27+F29+F31", None),
    ]
    if is_inv:
        tot += [(33, "Amount paid", None, USD), (34, "BALANCE DUE", "=F32-N(F33)", None)]
    for r, lab, f, fmt in tot:
        ws[f"D{r}"] = lab
        ws[f"D{r}"].font = font(10, lab in ("TOTAL", "BALANCE DUE"))
        ws[f"D{r}"].alignment = Alignment(horizontal="right")
        ws.merge_cells(f"D{r}:E{r}") if f or r == 33 else None
        if f:
            sh.out(f"F{r}", f, USD, key=lab in ("TOTAL", "BALANCE DUE"))
        elif r == 33:
            sh.inp("F33", ex.get("paid"), USD)
        else:
            ws[f"D{r}"].value = lab
            sh.inp(f"E{r}", ex.get("discount" if r == 28 else "tax"), fmt)
            sh.out(f"F{r}", None)
    dv_min(ws, "E28", 0, True, 1)
    dv_min(ws, "E30", 0, True, 0.3)
    nr = 36
    ws[f"B{nr}"] = "Payment methods: " if is_inv else "Notes & terms"
    ws[f"B{nr}"].font = font(10, True, C["primary"])
    if is_inv:
        ws[f"B{nr + 1}"] = '=PayMethods'
        ws[f"B{nr + 1}"].font = font(10)
        ws[f"B{nr + 2}"] = '="Please pay by "&IF(F5="","the due date",TEXT(F5,"mmmm d, yyyy"))&". Thank you for your business!"'
        ws[f"B{nr + 2}"].font = font(10)
        sh.inp(f"B{nr + 3}", ex.get("notes"))
        ws.merge_cells(f"B{nr + 3}:F{nr + 5}")
    else:
        sh.inp(f"B{nr + 1}", ex.get("notes") or
               "Price based on the details provided. Final price may change if the condition or size of the "
               "property is different from what was described.")
        ws.merge_cells(f"B{nr + 1}:F{nr + 4}")
        ws[f"B{nr + 1}"].alignment = Alignment(wrap_text=True, vertical="top")
        ws[f"B{nr + 6}"] = "Accepted by (client signature) ______________________   Date __________"
        ws[f"B{nr + 6}"].font = font(10)
    ws[f"B{nr + 8}"] = '="Thank you for choosing "&BizName&"!"'
    ws[f"B{nr + 8}"].font = font(10, True, C["primary"])

    # helper box outside print area
    ws["H8"] = "CALCULATOR SUGGESTION (not printed)"
    ws["H8"].font = font(10, True, C["white"])
    ws["H8"].fill = PatternFill("solid", fgColor=C["accent"])
    ws["H9"] = '="Price Calculator says: "&TEXT(CalcPrice,"$#,##0.00")&" per visit"'
    ws["H10"] = '="Regular price before discount: "&TEXT(CalcRegular,"$#,##0.00")'
    ws["H11"] = '="Service: "&CalcService&" — "&CalcFrequency'
    ws["H12"] = "Type the price into a line item to use it."
    for ref in ("H9", "H10", "H11", "H12"):
        ws[ref].font = font(10, False, C["ink"])
    ws.print_area = f"A1:F{nr + 9}"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    sh.protect()


# ------------------------------------------------------------- premium ----

def build_dashboard(wb):
    sh = Sheet(wb, "Dashboard", C["primary"])
    ws = sh.ws
    sh.title("Business Dashboard", "Everything updates from your Schedule, Clients and Transactions. Nothing to type here except the month.")
    sh.widths(A=2, B=30, C=16, D=3, E=30, F=16, G=3, H=30, I=16)
    ws["B4"] = "Year"
    sh.out("C4", "=TrackerYear", "0", bold=True)
    ws["E4"] = "Month to highlight (1–12)"
    ws["F4"] = "='Monthly Summary'!C33"
    sh.out("F4", "='Monthly Summary'!C33", "0", bold=True)
    ws["H4"] = "Change it on Monthly Summary (cell C33)"
    ws["H4"].font = font(9, False, C["muted"], True)
    MS = "'Monthly Summary'!"
    sel = f"INDEX({MS}$C$6:$N$29,{{row}},$F$4)"

    def kpis(col_label, col_val, top, title, items):
        sh.section(f"{col_label}{top}", title, f"{col_val}{top}")
        for i, (lab, f, fmt) in enumerate(items):
            r = top + 1 + i
            ws[f"{col_label}{r}"] = lab
            ws[f"{col_label}{r}"].font = font(10)
            sh.out(f"{col_val}{r}", f, fmt, key=(i == 0))
            ws.row_dimensions[r].height = 20
    kpis("B", "C", 6, "YEAR TO DATE", [
        ("Revenue", f"={MS}O6", USD),
        ("Total expenses", f"={MS}O13", USD),
        ("Estimated profit", f"={MS}O14", USD),
        ("Profit margin", f"={MS}O15", PCT),
        ("Net cash flow", f"={MS}O21", USD),
        ("Unpaid client balances", f"={MS}O22", USD),
    ])
    kpis("E", "F", 6, "SELECTED MONTH", [
        ("Revenue", "=" + sel.format(row=1), USD),
        ("Estimated profit", "=" + sel.format(row=9), USD),
        ("Profit margin", "=" + sel.format(row=10), PCT),
        ("Revenue vs previous month", f"={MS}F35", PCT),
        ("Visits completed", "=" + sel.format(row=19), "0"),
        ("Average price per visit", "=" + sel.format(row=21), USD),
    ])
    kpis("H", "I", 6, "OPERATIONS", [
        ("Active clients", '=COUNTIF(Clients!$J:$J,"Active")', "0"),
        ("Recurring active clients", '=COUNTIFS(Clients!$J:$J,"Active",Clients!$H:$H,"<>One-time",Clients!$H:$H,"<>")', "0"),
        ("Clients to follow up", '=COUNTIF(Clients!$O:$O,"Follow up")', "0"),
        ("Visits booked next 7 days", '=COUNTIFS(Schedule!$A:$A,">="&TODAY(),Schedule!$A:$A,"<="&TODAY()+7,Schedule!$I:$I,"<>Cancelled",Schedule!$I:$I,"<>Completed")', "0"),
        ("Revenue per labor hour (YTD)", f"={MS}O28", USD),
        ("Cancellation rate (YTD)", f'=IF(({MS}O24+{MS}O29)>0,{MS}O29/({MS}O24+{MS}O29),0)', PCT),
    ])
    sh.section("B14", "SAME MONTH LAST YEAR", "C14")
    ly = "EDATE(DATE($C$4,$F$4,1),-12)"
    ws["B15"] = "Revenue (same month last year)"
    sh.out("C15", f'=SUMIFS(Transactions!$F:$F,Transactions!$J:$J,{ly},Transactions!$H:$H,"Income")', USD)
    ws["B16"] = "Change vs last year"
    sh.out("C16", f'=IF(C15=0,"n/a",(F7-C15)/C15)', PCT)

    line = LineChart()
    line.title = "Revenue and estimated profit — 12 months"
    line.height, line.width = 8, 17
    msws = wb["Monthly Summary"]
    for r in (6, 14):
        line.add_data(Reference(msws, min_col=2, max_col=14, min_row=r, max_row=r), titles_from_data=True, from_rows=True)
    line.set_categories(Reference(msws, min_col=3, max_col=14, min_row=5, max_row=5))
    line.y_axis.numFmt = '"$"#,##0'
    for s, color in zip(line.series, [C["primary"], C["success"]]):
        s.graphicalProperties.line.solidFill = color
        s.graphicalProperties.line.width = 28000
    ws.add_chart(line, "B19")
    bar = BarChart()
    bar.type = "bar"
    bar.title = "Revenue by service type (year)"
    bar.height, bar.width = 8, 15
    bar.add_data(Reference(msws, min_col=9, min_row=33, max_row=41), titles_from_data=True)
    bar.set_categories(Reference(msws, min_col=8, min_row=34, max_row=41))
    bar.legend = None
    bar.series[0].graphicalProperties.solidFill = C["accent"]
    ws.add_chart(bar, "F19")
    ws.print_area = "B2:I36"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    sh.protect()


def build_goals(wb):
    sh = Sheet(wb, "Goal Planner", C["success"])
    ws = sh.ws
    sh.title("Goal & Break-even Planner", "How many jobs do you need each month to cover costs and pay yourself?")
    sh.widths(A=2, B=44, C=18, D=4, E=64)
    sh.section("B5", "INPUTS", "C5")
    rows = [
        (6, "Monthly fixed costs (overhead)", "=Overhead", USD, "Defaults to Settings. Type over it to test another number."),
        (7, "Owner pay you want per month", 4000, USD, "What you want to take home from the business (before income tax)."),
        (8, "Average price per job", 180, USD, "Tip: see 'Average price per visit' on Monthly Summary."),
        (9, "Variable costs as % of price", 0.55, PCT, "Labor + supplies + travel + card fees ÷ price. Price Calculator shows it per job."),
        (10, "Average labor hours per job", 4, NUM2, "From your Schedule or Price Calculator."),
        (11, "Working days per month", 22, "0", ""),
        (12, "Cleaners available (incl. you)", 2, "0", ""),
        (13, "Paid hours per cleaner per day", 7, NUM2, ""),
    ]
    for r, lab, v, fmt, note in rows:
        sh.label(f"B{r}", lab, note=note, note_ref=f"E{r}")
        sh.inp(f"C{r}", v, fmt)
    dv_min(ws, "C6:C8")
    dv_min(ws, "C9", 0, True, 0.99, "Enter a percentage below 100%.")
    dv_min(ws, "C10:C13")
    sh.section("B15", "RESULTS", "C15")
    res = [
        (16, "Contribution per job (price − variable costs)", "=C8*(1-C9)", USD),
        (17, "Break-even jobs per month (covers overhead only)", '=IF(C16>0,C6/C16,"n/a")', NUM2),
        (18, "Jobs per month to reach your pay goal", '=IF(C16>0,ROUNDUP((C6+C7)/C16,0),"n/a")', "0"),
        (19, "Jobs per week (≈ 4.33 weeks/month)", '=IF(ISNUMBER(C18),C18/(52/12),"n/a")', "0.0"),
        (20, "Monthly revenue needed", '=IF(ISNUMBER(C18),C18*C8,"n/a")', USD),
        (21, "Labor hours needed per month", '=IF(ISNUMBER(C18),C18*C10,"n/a")', "#,##0"),
        (22, "Labor hours your team has per month", "=C11*C12*C13", "#,##0"),
        (23, "Capacity used", '=IF(AND(ISNUMBER(C21),C22>0),C21/C22,"n/a")', PCT),
        (24, "Verdict", '=IF(NOT(ISNUMBER(C23)),"Price must be higher than variable costs",IF(C23>1,"Goal needs more people or higher prices",IF(C23>0.85,"Possible, but your schedule will be very tight","Reachable with your current team")))', None),
    ]
    for r, lab, f, fmt in res:
        sh.label(f"B{r}", lab, bold=r in (18, 24))
        sh.out(f"C{r}", f, fmt, key=r in (18, 24))
    ws["C24"].alignment = Alignment(wrap_text=True)
    ws.row_dimensions[24].height = 34
    ws.conditional_formatting.add("C23", CellIsRule(operator="greaterThan", formula=["1"],
                                  fill=PatternFill("solid", fgColor=C["danger_light"])))
    sh.protect()


def build_commercial(wb):
    sh = Sheet(wb, "Commercial Bid", C["primary_dark"])
    ws = sh.ws
    sh.title("Commercial Cleaning Bid Calculator", "Monthly contract price for offices and commercial spaces.")
    sh.widths(A=2, B=44, C=18, D=4, E=64)
    sh.section("B5", "INPUTS", "C5")
    rows = [
        (6, "Area to clean (sq ft)", 5000, "#,##0", ""),
        (7, "Sq ft cleaned per labor hour", 2500, "#,##0", "EXAMPLE only. Offices are often faster than homes — time a walkthrough."),
        (8, "Visits per week", 3, "0.0", ""),
        (9, "Hourly pay", "=Wage", USD, "Defaults to Settings."),
        (10, "Payroll burden %", "=Burden", PCT, "Defaults to Settings."),
        (11, "Supplies per visit ($)", 8, USD, "Trash liners, paper goods if you supply them, chemicals…"),
        (12, "Overhead to assign to this account per month ($)", 150, USD, "Insurance, admin time, supervision."),
        (13, "Target net margin %", "=TargetMargin", PCT, "Defaults to Settings."),
        (14, "Card fee % (0 if paid by ACH/check)", "=CardFee", "0.00%", ""),
    ]
    for r, lab, v, fmt, note in rows:
        sh.label(f"B{r}", lab, note=note, note_ref=f"E{r}")
        sh.inp(f"C{r}", v, fmt)
    dv_min(ws, "C6:C12")
    dv_min(ws, "C13", 0, True, 0.95)
    dv_min(ws, "C14", 0, True, 0.2)
    sh.section("B16", "RESULTS", "C16")
    res = [
        (17, "Labor hours per visit", '=IF(C7>0,C6/C7,0)', NUM2),
        (18, "Visits per month (52 weeks ÷ 12)", "=C8*52/12", NUM2),
        (19, "Labor cost per month", "=C17*C18*C9*(1+C10)", USD),
        (20, "Supplies per month", "=C11*C18", USD),
        (21, "Total monthly cost", "=C19+C20+C12", USD),
        (22, "MONTHLY CONTRACT PRICE", '=IF(1-C13-C14<=0,"Margin too high",C21/(1-C13-C14))', USD),
        (23, "Price per visit", '=IF(AND(ISNUMBER(C22),C18>0),C22/C18,"")', USD),
        (24, "Price per sq ft per month", '=IF(AND(ISNUMBER(C22),C6>0),C22/C6,"")', '"$"#,##0.000'),
        (25, "Estimated net profit per month", '=IF(ISNUMBER(C22),C22-C21-C22*C14,"")', USD),
    ]
    for r, lab, f, fmt in res:
        sh.label(f"B{r}", lab, bold=r == 22)
        sh.out(f"C{r}", f, fmt, key=r == 22)
    sh.protect()


def build_crew(wb):
    sh = Sheet(wb, "Crew Cost", C["success"])
    ws = sh.ws
    sh.title("Crew Cost Planner", "What does one hour of a cleaner really cost once drive time and downtime are included?")
    sh.widths(A=2, B=44, C=18, D=4, E=64)
    sh.section("B5", "INPUTS", "C5")
    rows = [
        (6, "Hourly pay", "=Wage", USD, "Defaults to Settings."),
        (7, "Payroll burden %", "=Burden", PCT, ""),
        (8, "Paid hours per week", 35, NUM2, ""),
        (9, "Billable % (time actually cleaning)", 0.75, PCT, "Drive time, training and gaps between jobs are paid but not billable."),
        (10, "Target net margin %", "=TargetMargin", PCT, ""),
    ]
    for r, lab, v, fmt, note in rows:
        sh.label(f"B{r}", lab, note=note, note_ref=f"E{r}")
        sh.inp(f"C{r}", v, fmt)
    dv_min(ws, "C6:C8")
    dv_min(ws, "C9", 0.01, True, 1, "Enter a percentage between 1% and 100%.")
    dv_min(ws, "C10", 0, True, 0.95)
    sh.section("B12", "RESULTS", "C12")
    res = [
        (13, "Loaded cost per paid hour", "=C6*(1+C7)", USD),
        (14, "Weekly cost of this cleaner", "=C13*C8", USD),
        (15, "Billable hours per week", "=C8*C9", NUM2),
        (16, "Real cost per BILLABLE hour", '=IF(C15>0,C14/C15,"")', USD),
        (17, "Minimum rate per billable hour for your margin", '=IF(AND(ISNUMBER(C16),C10<1),C16/(1-C10),"")', USD),
        (18, "Monthly cost of this cleaner", "=C14*52/12", USD),
    ]
    for r, lab, f, fmt in res:
        sh.label(f"B{r}", lab, bold=r == 17)
        sh.out(f"C{r}", f, fmt, key=r == 17)
    ws["B20"] = "Use the 'minimum rate' as a floor when you check prices: price ÷ labor hours should stay above it."
    ws["B20"].font = font(10, False, C["muted"], True)
    sh.protect()


def build_checklists(wb):
    sh = Sheet(wb, "Checklists", C["accent"])
    ws = sh.ws
    sh.title("Cleaning Checklists", "Print for your crew or attach to an estimate so clients know exactly what is included.")
    sh.widths(A=2, B=5, C=44, D=3, E=5, F=44, G=3, H=5, I=44)
    for col_box, col_txt, (title, items) in zip("BEH", "CFI", sample_data.CHECKLISTS):
        sh.section(f"{col_box}5", title, f"{col_txt}5")
        for i, it in enumerate(items):
            r = 6 + i
            if it.startswith("#"):
                ws[f"{col_txt}{r}"] = it[1:].strip().upper()
                ws[f"{col_txt}{r}"].font = font(10, True, C["primary"])
            else:
                ws[f"{col_box}{r}"] = "☐"
                ws[f"{col_box}{r}"].alignment = Alignment(horizontal="center")
                ws[f"{col_txt}{r}"] = it
                ws[f"{col_txt}{r}"].font = font(10)
                ws[f"{col_txt}{r}"].protection = UNLOCK
    ws.print_area = "B2:I60"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    sh.protect()


def build_start(wb, tier, example):
    sh = Sheet(wb, "Start Here", C["accent"])
    ws = sh.ws
    sh.widths(A=2, B=26, C=90)
    ws["B2"] = f"{brand.NAME} — {tier.title()}"
    ws["B2"].font = font(20, True, C["primary"])
    ws["B3"] = brand.TAGLINE
    ws["B3"].font = font(11, False, C["muted"], True)
    if example:
        ws["B4"] = "EXAMPLE FILE — filled with fictional sample data so you can see how it works. Use the blank file for your business."
        ws["B4"].font = font(10, True, C["danger"])
    sh.section("B6", "GET STARTED IN 3 STEPS", "C6")
    steps = [
        ("1. Settings", "Enter your business name and YOUR real costs. Every default number is an example."),
        ("2. Price Calculator", "Describe a job, get a price that covers costs, overhead, card fees and your profit margin."),
        ("3. Use it every week", "Starter: save quotes in the Quote Table. Complete/Premium: add clients, schedule visits, log money in and out."),
    ]
    r = 7
    for a, b in steps:
        ws[f"B{r}"], ws[f"C{r}"] = a, b
        ws[f"B{r}"].font = font(10, True)
        ws[f"C{r}"].font = font(10)
        r += 1
    sh.section("B11", "WHAT IS IN THIS FILE", "C11")
    desc = {
        "Dashboard": "Year-to-date and monthly results, operations KPIs and charts.",
        "Settings": "Business info, labor rate, overhead, margin, tax, rounding, service types and discounts.",
        "Price Calculator": "Price one job. Includes 'Check a price' to see if a price you have in mind loses money.",
        "Quote Table": "Price up to 50 jobs side by side.",
        "Margin vs Markup": "Converter + explanation of the most common pricing mistake.",
        "Clients": "Client list with last visit, next visit, follow-up flag and lifetime revenue (automatic).",
        "Schedule": "Every visit with status (Scheduled → Completed), staff, price and suggested next visit.",
        "Transactions": "Income and expenses. Mark items Pending until paid.",
        "Monthly Summary": "Revenue, expenses, estimated profit, cash flow, month-to-month comparison, results by service, chart.",
        "Estimate": "Printable estimate. File → Download/Save as PDF.",
        "Invoice": "Printable invoice with due date and balance. It does not collect payments.",
        "Goal Planner": "Jobs per month to break even and to reach your pay goal, with a capacity check.",
        "Commercial Bid": "Monthly contract price for offices.",
        "Crew Cost": "True cost of a cleaner per billable hour.",
        "Checklists": "Standard, deep and move-out checklists to print.",
    }
    r = 12
    for key in TIERS[tier]:
        t = SHEET_TITLES[key]
        if t in desc:
            ws[f"B{r}"], ws[f"C{r}"] = t, desc[t]
            ws[f"B{r}"].hyperlink = f"#'{t}'!A1"
            ws[f"B{r}"].font = font(10, True, C["primary"])
            ws[f"C{r}"].font = font(10)
            r += 1
    r += 1
    sh.section(f"B{r}", "COLOR GUIDE", f"C{r}")
    r += 1
    sh.inp(f"B{r}", "Yellow")
    ws[f"C{r}"] = "Your input. Type here."
    r += 1
    sh.out(f"B{r}", "Grey")
    ws[f"C{r}"] = "Automatic formula. Calculation sheets are protected (no password) so you do not break formulas by accident."
    r += 1
    sh.out(f"B{r}", "Gold", key=True)
    ws[f"C{r}"] = "Key result."
    r += 2
    sh.section(f"B{r}", "IMPORTANT", f"C{r}")
    notes = [
        "Works in Microsoft Excel 2019/2021/365, Excel for the web (free) and Google Sheets. No macros.",
        "To unlock a protected sheet: Excel → Review → Unprotect Sheet (no password). Google Sheets ignores protection.",
        "Default rates and multipliers are examples, not market prices for your area. Time your jobs and use your numbers.",
        "This kit is a business-management tool. It is not accounting, tax or legal advice — talk to a professional.",
        "Your data stays in your own file. We never see it. To delete a client, delete the row.",
        f"Help: {brand.SUPPORT_EMAIL}   ·   Version {brand.VERSION}",
    ]
    for t in notes:
        r += 1
        ws[f"C{r}"] = t
        ws[f"C{r}"].font = font(10)
    sh.protect()


# ----------------------------------------------------------- free demo ----

def build_free(path):
    wb = Workbook()
    wb.remove(wb.active)
    wb._example = False
    sh = Sheet(wb, "Quick Price Check", C["primary"])
    ws = sh.ws
    sh.title(f"Quick Price Check — free from {brand.NAME}",
             "A simple version of our Price Calculator. Yellow = your numbers.")
    sh.widths(A=2, B=40, C=18, D=4, E=70)
    sh.section("B5", "YOUR JOB", "C5")
    rows = [
        (6, "Total labor hours (all cleaners)", 4, NUM2),
        (7, "Hourly pay per cleaner", 18, USD),
        (8, "Supplies + travel for this job", 15, USD),
        (9, "Share of monthly overhead per job", 30, USD),
        (10, "Target profit MARGIN %", 0.30, PCT),
        (11, "Card fee %", 0.029, "0.00%"),
    ]
    for r, lab, v, fmt in rows:
        sh.label(f"B{r}", lab)
        sh.inp(f"C{r}", v, fmt)
    dv_min(ws, "C6:C9")
    dv_min(ws, "C10", 0, True, 0.9)
    dv_min(ws, "C11", 0, True, 0.1)
    sh.section("B13", "RESULT", "C13")
    res = [
        (14, "Total cost of the job", "=C6*C7+C8+C9", USD, False),
        (15, "Price for your margin", '=IF(1-C10-C11<=0,"Margin too high",C14/(1-C10-C11))', USD, True),
        (16, "Price if you just add the same % as markup", "=C14*(1+C10)", USD, False),
        (17, "Profit you would miss with markup", '=IF(ISNUMBER(C15),C15-C16,"")', USD, False),
    ]
    for r, lab, f, fmt, key in res:
        sh.label(f"B{r}", lab, bold=key)
        sh.out(f"C{r}", f, fmt, key=key)
    lines = [
        "What the full kit adds",
        "• Hours estimated from sq ft, bedrooms and bathrooms, by service type",
        "• Frequency discounts that keep your margin, rounding, minimum price, sales tax",
        "• Check-a-price verdict, 50-job Quote Table",
        "• Complete/Premium: clients, schedule, profit tracker, estimates, invoices, dashboard",
        f"Get it: {brand.STORE_URL}",
    ]
    for i, t in enumerate(lines):
        c = ws.cell(row=5 + i, column=5, value=t)
        c.font = font(11 if i == 0 else 10, i == 0, C["primary"] if i in (0, 5) else C["ink"])
    sh.protect()
    wb.save(path)


# ------------------------------------------------------------- builder ----

BUILDERS = {
    "start": lambda wb, t, e: build_start(wb, t, e),
    "dashboard": None,  # built last (needs Monthly Summary), moved to position 1
    "settings": lambda wb, t, e: build_settings(wb, t, e),
    "calculator": lambda wb, t, e: build_calculator(wb, e),
    "quotes": lambda wb, t, e: build_quotes(wb, e),
    "margin": lambda wb, t, e: build_margin(wb),
    "clients": lambda wb, t, e: build_clients(wb, e),
    "schedule": lambda wb, t, e: build_schedule(wb, e),
    "transactions": lambda wb, t, e: build_transactions(wb, e),
    "summary": lambda wb, t, e: build_summary(wb),
    "estimate": lambda wb, t, e: build_document(wb, "estimate", e),
    "invoice": lambda wb, t, e: build_document(wb, "invoice", e),
    "goals": lambda wb, t, e: build_goals(wb),
    "commercial": lambda wb, t, e: build_commercial(wb),
    "crew": lambda wb, t, e: build_crew(wb),
    "checklists": lambda wb, t, e: build_checklists(wb),
}


def build_tier(tier, example, path):
    wb = Workbook()
    wb.remove(wb.active)
    wb._example = example
    for key in TIERS[tier]:
        if BUILDERS[key]:
            BUILDERS[key](wb, tier, example)
    if "dashboard" in TIERS[tier]:
        build_dashboard(wb)
        wb.move_sheet("Dashboard", offset=-(len(wb.sheetnames) - 2))
    wb.active = 0
    props = wb.properties
    props.creator = brand.NAME
    props.title = f"{brand.NAME} {tier.title()}"
    props.subject = "Cleaning business pricing and management workbook"
    props.created = dt.datetime(2026, 1, 1)
    wb.save(path)


def file_name(tier, example):
    return f"{brand.FILE_PREFIX}-{tier.title()}{'-EXAMPLE' if example else ''}.xlsx"


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    made = []
    for tier in TIERS:
        (out / tier).mkdir(exist_ok=True)
        for example in (False, True):
            p = out / tier / file_name(tier, example)
            build_tier(tier, example, p)
            made.append(p)
    (out / "free").mkdir(exist_ok=True)
    free = out / "free" / f"{brand.FILE_PREFIX}-Quick-Price-Check-FREE.xlsx"
    build_free(free)
    made.append(free)
    for p in made:
        print("built", p)
    return made


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "products")
