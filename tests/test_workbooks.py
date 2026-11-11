"""Integration tests: build every workbook, recalculate it with LibreOffice
(headless) and compare the results with the reference math in kit/pricing.py.

Requires LibreOffice (`soffice`) on PATH.  Run:
    python3 -m unittest discover -s tests -v
"""
import datetime as dt
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import openpyxl

KIT = Path(__file__).resolve().parent.parent / "kit"
sys.path.insert(0, str(KIT))
import build_workbooks as bw  # noqa: E402
import sample_data as sd  # noqa: E402
from pricing import (Job, Settings, break_even, commercial_bid, crew_cost,  # noqa: E402
                     quote)

# Functions that exist in Excel 2019+/365, Excel for the web, Google Sheets and LibreOffice.
PORTABLE_FUNCTIONS = {
    "ABS", "AND", "CHOOSE", "COUNTIF", "COUNTIFS", "DATE", "EDATE", "IF", "IFERROR",
    "INDEX", "ISNUMBER", "MATCH", "MAX", "MAXIFS", "MINIFS", "MONTH", "N", "NOT", "OR",
    "ROUNDUP", "ROW", "SUM", "SUMIFS", "TEXT", "TODAY", "WEEKDAY", "YEAR",
}
ERRORS = ("#REF!", "#NAME?", "#VALUE!", "#DIV/0!", "#N/A", "#NUM!", "#NULL!", "Err:")
CALC_ROWS = {  # result key -> row in 'Price Calculator'!G
    "labor_hours": 9, "onsite_hours": 10, "labor_cost": 11, "travel_cost": 13,
    "direct_cost": 15, "overhead": 16, "total_cost": 17, "raw_price": 18, "price": 19,
    "total_discount": 20, "regular_price": 21, "discount_amount": 22, "sales_tax": 23,
    "customer_total": 24, "card_fee": 25, "gross_profit": 26, "gross_margin": 27,
    "contribution": 28, "contribution_margin": 29, "net_profit": 30, "net_margin": 31,
    "markup_on_cost": 32, "price_per_labor_hour": 33, "price_per_sqft": 34,
}
EDGE_CASES = {
    # name: (calculator inputs C-row -> value, Job kwargs or None if warning expected)
    "weekly_discount_tax": ({7: "House", 8: "Recurring Cleaning", 9: "Weekly", 10: 2600, 11: 4,
                             12: 3, 13: 2, 17: 10, 18: 12, 20: 0.05, 25: 0.0825},
                            dict(service_type="Recurring Cleaning", frequency="Weekly", sqft=2600,
                                 bedrooms=4, bathrooms=3, crew=2, supplies=10, miles=12,
                                 extra_discount=0.05, tax_override=0.0825)),
    "override_hours_wage_margin": ({7: "Office", 8: "Office Cleaning", 9: "One-time", 13: 3, 14: 9,
                                    17: 30, 23: 22, 24: 0.4},
                                   dict(property_type="Office", service_type="Office Cleaning",
                                        crew=3, hours_override=9, supplies=30, wage_override=22,
                                        margin_override=0.4)),
    "condition_pets": ({7: "House", 8: "Standard Cleaning", 9: "Every 4 weeks", 10: 1800, 11: 3,
                        12: 2, 13: 2, 15: "Pets / heavy use", 17: 12},
                       dict(sqft=1800, bedrooms=3, bathrooms=2, crew=2, frequency="Every 4 weeks",
                            condition="Pets / heavy use", supplies=12)),
    "tiny_job_minimum": ({7: "Apartment / Condo", 8: "Standard Cleaning", 9: "One-time", 10: 300, 13: 1},
                         dict(property_type="Apartment / Condo", sqft=300, crew=1)),
    "margin_too_high": ({7: "House", 8: "Standard Cleaning", 9: "One-time", 10: 1000, 13: 1, 24: 0.98}, None),
    "negative_sqft": ({7: "House", 8: "Standard Cleaning", 9: "One-time", 10: -500, 13: 1}, None),
}


def recalc(files, outdir):
    subprocess.run(["soffice", "--headless", "--calc", "--convert-to",
                    "xlsx:Calc MS Excel 2007 XML", "--outdir", str(outdir), *map(str, files)],
                   check=True, capture_output=True, timeout=300)
    return {f.name: openpyxl.load_workbook(outdir / f.name, data_only=True) for f in files}


@unittest.skipUnless(shutil.which("soffice"), "LibreOffice not installed")
class TestWorkbooks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="tm-wb-"))
        src = cls.tmp / "src"
        cls.files = bw.main(src)
        # edge-case variants of the blank Starter calculator
        cls.edge_files = {}
        for case, (inputs, _) in EDGE_CASES.items():
            wb = openpyxl.load_workbook(src / "starter" / bw.file_name("starter", False))
            ws = wb["Price Calculator"]
            for row in range(6, 29):
                if row in (6,):
                    continue
                if ws[f"C{row}"].fill.fgColor.rgb.endswith(bw.C["input"]):
                    ws[f"C{row}"].value = None
            for row, v in inputs.items():
                ws[f"C{row}"] = v
            p = src / f"edge-{case}.xlsx"
            wb.save(p)
            cls.edge_files[case] = p
        cls.out = cls.tmp / "out"
        cls.wbs = recalc(cls.files + list(cls.edge_files.values()), cls.out)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def wb(self, tier, example=True):
        return self.wbs[bw.file_name(tier, example)]

    # ---------------------------------------------------------- generic ----
    def test_no_formula_errors_anywhere(self):
        for fname, wb in self.wbs.items():
            for ws in wb:
                for row in ws.iter_rows():
                    for c in row:
                        if isinstance(c.value, str) and c.value.startswith(ERRORS):
                            self.fail(f"{fname} {ws.title}!{c.coordinate} = {c.value}")

    def test_only_portable_functions_no_macros_no_links(self):
        for f in self.files:
            with zipfile.ZipFile(f) as z:
                names = z.namelist()
                self.assertFalse(any("vbaProject" in n for n in names), f"macros in {f.name}")
                self.assertFalse(any("externalLink" in n for n in names), f"external link in {f.name}")
            wb = openpyxl.load_workbook(f)
            used = set()
            for ws in wb:
                for row in ws.iter_rows():
                    for c in row:
                        if isinstance(c.value, str) and c.value.startswith("="):
                            text = re.sub(r'"[^"]*"', "", c.value)
                            used |= set(re.findall(r"([A-Z][A-Z0-9_.]*)\(", text))
            used = {u.replace("_xlfn.", "") for u in used}
            self.assertEqual(used - PORTABLE_FUNCTIONS, set(), f"non-portable functions in {f.name}")

    def test_tiers_have_expected_sheets(self):
        for tier, keys in bw.TIERS.items():
            for example in (False, True):
                names = self.wb(tier, example).sheetnames
                self.assertEqual(set(names), {bw.SHEET_TITLES[k] for k in keys})
                self.assertEqual(names[0], "Start Here")

    # ------------------------------------------------------- calculator ----
    def assert_calc_matches(self, ws, job):
        expected = quote(job, Settings())
        for key, row in CALC_ROWS.items():
            got = ws[f"G{row}"].value
            self.assertAlmostEqual(got, expected[key], places=6, msg=f"{key} (G{row})")

    def test_calculator_example_matches_python(self):
        e = sd.CALC_EXAMPLE
        job = Job(property_type=e["property"], service_type=e["service"], frequency=e["frequency"],
                  sqft=e["sqft"], bedrooms=e["bedrooms"], bathrooms=e["bathrooms"], crew=e["crew"],
                  supplies=e["supplies"], miles=e["miles"])
        for tier in bw.TIERS:
            ws = self.wb(tier)["Price Calculator"]
            self.assert_calc_matches(ws, job)
            q = quote(job, Settings())
            planned = e["planned_price"]
            net = planned - q["total_cost"] - planned * Settings().card_fee
            self.assertAlmostEqual(ws["G37"].value, net, places=6)
            self.assertEqual(ws["G39"].value, "Meets target margin")

    def test_calculator_edge_cases(self):
        for case, (inputs, job_kwargs) in EDGE_CASES.items():
            ws = self.wbs[f"edge-{case}.xlsx"]["Price Calculator"]
            if job_kwargs is None:
                self.assertTrue(str(ws["B31"].value).startswith("⚠"), f"{case}: no warning")
                if case == "margin_too_high":
                    self.assertEqual(ws["G19"].value, 0)
                continue
            self.assert_calc_matches(ws, Job(**job_kwargs))

    def test_blank_calculator_shows_zero_and_hint(self):
        ws = self.wb("starter", False)["Price Calculator"]
        self.assertEqual(ws["G19"].value, 0)
        self.assertIn("Enter square feet", ws["B31"].value)
        self.assertEqual(ws["G39"].value, "Enter a price in C28")

    def test_quote_table_matches_python(self):
        ws = self.wb("complete")["Quote Table"]
        for i, row in enumerate(sd.QUOTE_ROWS):
            r = 5 + i
            (_, prop, svc, freq, sqft, bed, bath, crew, hrs, sup, miles, other, disc) = row
            q = quote(Job(property_type=prop, service_type=svc, frequency=freq, sqft=sqft,
                          bedrooms=bed, bathrooms=bath, crew=crew, hours_override=hrs,
                          supplies=sup, miles=miles, other_direct=other, extra_discount=disc),
                      Settings())
            self.assertAlmostEqual(ws[f"N{r}"].value, q["labor_hours"], places=6)
            self.assertAlmostEqual(ws[f"O{r}"].value, q["total_cost"], places=6)
            self.assertAlmostEqual(ws[f"P{r}"].value, q["price"], places=6)
            self.assertAlmostEqual(ws[f"Q{r}"].value, q["regular_price"], places=6)
            self.assertAlmostEqual(ws[f"R{r}"].value, q["net_profit"], places=6)
            self.assertAlmostEqual(ws[f"S{r}"].value, q["net_margin"], places=6)
        self.assertIn(ws["A12"].value, (None, ""))
        self.assertIn(ws["P12"].value, (None, ""))

    def test_margin_sheet(self):
        ws = self.wb("starter")["Margin vs Markup"]
        self.assertAlmostEqual(ws["C9"].value, 0.3 / 1.3)
        self.assertAlmostEqual(ws["C12"].value, 100 / 0.7)

    # ----------------------------------------------------- tracker ---------
    def test_monthly_summary_matches_sample_transactions(self):
        ws = self.wb("premium")["Monthly Summary"]
        groups = dict(bw.CATEGORIES)
        tx = sd.TRANSACTIONS
        income = sum(t[5] for t in tx if groups[t[1]] == "Income")
        received = sum(t[5] for t in tx if groups[t[1]] == "Income" and t[6] == "Received")
        expenses = sum(t[5] for t in tx if groups[t[1]] in bw.GROUPS)
        taxes = sum(t[5] for t in tx if groups[t[1]] == "Tax")
        paid_out = sum(t[5] for t in tx if groups[t[1]] != "Income" and t[6] == "Paid")
        self.assertAlmostEqual(ws["O6"].value, income, places=6)
        self.assertAlmostEqual(ws["O7"].value, received, places=6)
        self.assertAlmostEqual(ws["O13"].value, expenses, places=6)
        self.assertAlmostEqual(ws["O14"].value, income - expenses, places=6)
        self.assertAlmostEqual(ws["O16"].value, taxes, places=6)
        self.assertAlmostEqual(ws["O21"].value, received - paid_out, places=6)
        jan = [t for t in tx if t[0].month == 1 and groups[t[1]] == "Income"]
        self.assertAlmostEqual(ws["C6"].value, sum(t[5] for t in jan), places=6)
        done = [s for s in sd.SCHEDULE if s[7] == "Completed"]
        self.assertEqual(ws["O24"].value, len(done))
        self.assertAlmostEqual(ws["O25"].value, sum(s[4] for s in done), places=6)
        # month comparison (June vs May)
        june = sum(t[5] for t in tx if t[0].month == 6 and groups[t[1]] == "Income")
        may = sum(t[5] for t in tx if t[0].month == 5 and groups[t[1]] == "Income")
        self.assertAlmostEqual(ws["C35"].value, june)
        self.assertAlmostEqual(ws["D35"].value, may)

    def test_clients_and_schedule_links(self):
        wb = self.wb("complete")
        cl, sc = wb["Clients"], wb["Schedule"]
        self.assertEqual(cl["A5"].value, "C001")
        name = cl["B5"].value
        done = [s for s in sd.SCHEDULE if s[2] == name and s[7] == "Completed"]
        self.assertEqual(cl["P5"].value, len(done))
        self.assertAlmostEqual(cl["Q5"].value, sum(s[4] for s in done))
        self.assertEqual(cl["L5"].value.date(), max(s[0] for s in done).date())
        self.assertEqual(sc["D5"].value, dict((c[0], c[4]) for c in sd.CLIENTS)[sc["C5"].value])
        # suggested next visit = date + frequency interval
        freq = dict((c[0], c[6]) for c in sd.CLIENTS)[sc["C5"].value]
        days = dict((k, v[1]) for k, v in bw.FREQUENCIES.items())[freq]
        self.assertEqual((sc["L5"].value - sc["A5"].value).days, days)
        # Former client never flagged, Active client with no booking flagged
        status = {cl[f"B{r}"].value: (cl[f"J{r}"].value, cl[f"O{r}"].value) for r in range(5, 13)}
        self.assertIn(status["Riley Ortiz"][1], (None, ""))
        self.assertEqual(status["Sam Patel"][1], "Follow up")

    def test_documents(self):
        wb = self.wb("premium")
        est, inv = wb["Estimate"], wb["Invoice"]
        sub = sum(q * p for _, q, p in sd.ESTIMATE["items"])
        self.assertAlmostEqual(est["F27"].value, sub)
        self.assertAlmostEqual(est["F32"].value, sub * (1 - sd.ESTIMATE["discount"]))
        self.assertEqual(est["F5"].value.date(), (sd.ESTIMATE["date"] + dt.timedelta(days=30)).date())
        inv_total = sum(q * p for _, q, p in sd.INVOICE["items"])
        self.assertAlmostEqual(inv["F32"].value, inv_total)
        self.assertAlmostEqual(inv["F34"].value, inv_total - sd.INVOICE["paid"])
        self.assertEqual(inv["F5"].value.date(), (sd.INVOICE["date"] + dt.timedelta(days=7)).date())
        self.assertEqual(inv["B10"].value, "Maple Dental")

    def test_starter_estimate_without_client_list(self):
        est = self.wb("starter")["Estimate"]
        self.assertEqual(est["B11"].value, dict((c[0], c[4]) for c in sd.CLIENTS)["Morgan Price"])
        self.assertEqual(est["E11"].value, est["B11"].value)
        self.assertAlmostEqual(est["F32"].value, 435 * 0.95)
        self.assertIn("295.00", est["H9"].value)

    # ----------------------------------------------------- premium ---------
    def test_planners(self):
        wb = self.wb("premium")
        g = wb["Goal Planner"]
        be = break_even(1200, 4000, 180, 0.55)
        self.assertAlmostEqual(g["C17"].value, be["break_even_jobs"])
        self.assertEqual(g["C18"].value, be["goal_jobs_rounded"])
        c = wb["Commercial Bid"]
        cb = commercial_bid(5000, 2500, 3, 18, 0.12, 8, 150, 0.30, 0.029)
        self.assertAlmostEqual(c["C22"].value, cb["monthly_price"])
        self.assertAlmostEqual(c["C23"].value, cb["price_per_visit"])
        k = wb["Crew Cost"]
        cc = crew_cost(18, 0.12, 35, 0.75, 0.30)
        self.assertAlmostEqual(k["C16"].value, cc["cost_per_billable_hour"])
        self.assertAlmostEqual(k["C17"].value, cc["min_rate_for_margin"])

    def test_dashboard(self):
        wb = self.wb("premium")
        d, ms = wb["Dashboard"], wb["Monthly Summary"]
        self.assertAlmostEqual(d["C7"].value, ms["O6"].value)
        self.assertAlmostEqual(d["F7"].value, ms["H6"].value)  # June = column H
        active = sum(1 for c in sd.CLIENTS if c[8] == "Active")
        self.assertEqual(d["I7"].value, active)
        self.assertEqual(wb.sheetnames[1], "Dashboard")

    def test_free_tool(self):
        ws = self.wbs[f"{bw.brand.FILE_PREFIX}-Quick-Price-Check-FREE.xlsx"]["Quick Price Check"]
        cost = 4 * 18 + 15 + 30
        self.assertAlmostEqual(ws["C14"].value, cost)
        self.assertAlmostEqual(ws["C15"].value, cost / (1 - 0.30 - 0.029))


if __name__ == "__main__":
    unittest.main()
