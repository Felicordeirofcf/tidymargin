"""Tests for the operations agents (fictional fixture data only)."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "agents"))
from common import Agent, mask, money  # noqa: E402
from dashboard import build_dashboard  # noqa: E402
from team import (CEO, ContentMarketing, CustomerSupport, FinancialController,  # noqa: E402
                  QualityMonitor, SalesAnalyst)

FIX = ROOT / "tests" / "fixtures"


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.data, self.reports, self.logs = self.tmp / "data", self.tmp / "reports", self.tmp / "logs"
        self.data.mkdir()
        for f in FIX.glob("*.csv"):
            shutil.copy(f, self.data / f.name)
        (self.data / "finance.json").write_text(json.dumps({"refund_reserve_pct": 0.1, "tax_reserve_pct": 0.0}))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def mk(self, cls):
        return cls(self.data, self.reports, self.logs)

    def test_sales_counts_only_confirmed(self):
        r = self.mk(SalesAnalyst).execute()
        self.assertEqual(r.metrics["Confirmed paid sales"], 2)
        self.assertEqual(r.metrics["Pending (NOT counted as revenue)"], 1)
        self.assertEqual(r.metrics["Gross revenue USD (confirmed)"], "28.00")
        self.assertEqual(r.metrics["Net received USD (before refunds/taxes)"], "23.37")
        self.assertEqual(r.metrics["Visit -> paid sale conversion"], "1.00%")

    def test_no_data_means_no_sales(self):
        (self.data / "sales.csv").unlink()
        r = self.mk(SalesAnalyst).execute()
        self.assertNotIn("Confirmed paid sales", r.metrics)
        self.assertTrue(any("No sales data" in s for s in r.summary))
        f = self.mk(FinancialController).execute()
        self.assertEqual(f.metrics["Free balance for reinvestment USD"], "0.00")
        self.assertEqual(f.proposals, [])

    def test_finance_never_moves_money_only_proposes(self):
        r = self.mk(FinancialController).execute()
        self.assertEqual(r.metrics["Refunds + chargebacks USD"], "29.00")
        self.assertIn("tax_reserve_pct", " ".join(r.findings))
        a = self.mk(FinancialController)
        for act in ("move_money", "refund", "spend_money"):
            with self.assertRaises(PermissionError):
                a.require(act)

    def test_support_escalates_and_masks(self):
        r = self.mk(CustomerSupport).execute()
        self.assertEqual(r.metrics["Messages: refund"], 1)
        self.assertTrue(any("refund" in p for p in r.proposals))
        drafts = (self.reports / "support_drafts").glob("*.md")
        text = "".join(p.read_text() for p in drafts)
        self.assertIn("Save as Google Sheets", text)
        self.assertIn("Excel for the web", text)
        # drafts keep the address (needed to reply) but are git-ignored; reports/logs are masked
        self.assertIn("reports/support_drafts/", (ROOT / ".gitignore").read_text())
        report = "".join(p.read_text() for p in (self.reports / "agent_runs").glob("*.md"))
        self.assertNotIn("@example.com", report)
        self.assertNotIn("@example.com", (self.reports / "PENDING_APPROVALS.md").read_text())
        logs = "".join(p.read_text() for p in self.logs.glob("*.jsonl"))
        self.assertNotIn("@example.com", logs)

    def test_mask_and_money(self):
        self.assertNotIn("@", mask("contact x.y@mail.com now"))
        self.assertEqual(money("$1,234.50"), 1234.5)
        self.assertEqual(money("(9.00)"), -9.0)
        with self.assertRaises(ValueError):
            money("abc")

    def test_agents_cannot_declare_critical_actions(self):
        class Bad(Agent):
            name = "bad"
            allowed_actions = {"send_email"}
        with self.assertRaises(AssertionError):
            Bad(self.data, self.reports, self.logs)

    def test_content_checks_claims(self):
        r = self.mk(ContentMarketing).execute()
        self.assertFalse([f for f in r.findings if "risky claim" in f], r.findings)
        self.assertEqual(len(r.proposals), 3)

    def test_quality_monitor_on_real_release(self):
        r = self.mk(QualityMonitor).execute()
        self.assertFalse([f for f in r.findings if "missing" in f.lower() and "config" not in f.lower()], r.findings)
        self.assertEqual(r.metrics["Broken internal links"], 0)

    def test_ceo_and_dashboard(self):
        r = self.mk(CEO).execute()
        self.assertEqual(r.metrics["Agents run"], 5)
        self.assertTrue((self.reports / "PENDING_APPROVALS.md").exists())
        out = build_dashboard(self.data, self.tmp / "dash.html")
        html = out.read_text()
        self.assertIn("Confirmed paid sales", html)
        self.assertIn("Orders are not payments", html)


if __name__ == "__main__":
    unittest.main()
