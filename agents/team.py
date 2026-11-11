"""The eight TidyMargin operations agents.

Each agent is a small, rule-based, on-demand job.  They read local files the
owner exports (sales, traffic, support inbox), check the project, and write
reports + proposals.  None of them can spend, refund, send, publish or change
prices — see agents/common.py.

Input files (all optional; missing file = "no data"):
  analytics/data/sales.csv          date,order_id,product,status,gross_usd,fees_usd,source,country
  analytics/data/traffic.csv        date,source,visits,buy_clicks
  analytics/data/support_inbox.csv  date,from,subject,message
  analytics/data/finance.json       {"refund_reserve_pct":0.10,"tax_reserve_pct":0.0,...}
  analytics/data/competitors.csv    name,url,last_price_seen
  marketing/content_calendar.csv    (status / published_url maintained by the owner)
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser
import zipfile
from pathlib import Path

from common import ROOT, Agent, Result, money, parse_date, read_csv, today

PAID = {"paid", "completed", "complete", "succeeded", "success"}
REFUNDED = {"refunded", "refund", "partially_refunded"}
CHARGEBACK = {"chargeback", "disputed", "dispute"}
PENDING = {"pending", "processing", "unpaid"}
TIERS = ("starter", "complete", "premium")


def load_sales(agent: Agent):
    rows = read_csv(agent.data_dir / "sales.csv")
    if rows is None:
        return None
    out = []
    for r in rows:
        status = r.get("status", "").lower()
        out.append({
            "date": parse_date(r.get("date", "")),
            "order_id": r.get("order_id", ""),
            "product": r.get("product", "").lower(),
            "status": status,
            "gross": money(r.get("gross_usd")),
            "fees": money(r.get("fees_usd")),
            "source": r.get("source", "") or "unknown",
        })
    return out


def product_tier(name: str) -> str:
    for t in TIERS:
        if t in name:
            return t
    return "free" if "free" in name or "quick" in name else "other"


# ============================================================ 5. SALES ======

class SalesAnalyst(Agent):
    name = "sales_analyst"

    def run(self) -> Result:
        res = Result(self.name)
        sales = load_sales(self)
        traffic = read_csv(self.data_dir / "traffic.csv")
        if sales is None:
            res.summary.append("No sales data (analytics/data/sales.csv missing). No sales are reported — none are assumed.")
        else:
            paid = [s for s in sales if s["status"] in PAID and s["gross"] > 0]
            refunded = [s for s in sales if s["status"] in REFUNDED]
            cb = [s for s in sales if s["status"] in CHARGEBACK]
            pending = [s for s in sales if s["status"] in PENDING]
            free = [s for s in sales if s["status"] in PAID and s["gross"] == 0]
            gross = sum(s["gross"] for s in paid)
            fees = sum(s["fees"] for s in paid)
            res.metrics.update({
                "Orders recorded (all statuses)": len(sales),
                "Confirmed paid sales": len(paid),
                "Free downloads": len(free),
                "Pending (NOT counted as revenue)": len(pending),
                "Refunds": len(refunded),
                "Chargebacks": len(cb),
                "Gross revenue USD (confirmed)": f"{gross:,.2f}",
                "Platform + processor fees USD": f"{fees:,.2f}",
                "Net received USD (before refunds/taxes)": f"{gross - fees:,.2f}",
                "Average order value USD": f"{gross / len(paid):,.2f}" if paid else "n/a",
            })
            by_tier = collections.Counter(product_tier(s["product"]) for s in paid)
            by_src = collections.Counter(s["source"] for s in paid)
            res.summary.append("Paid sales by product: " + (", ".join(f"{k} {v}" for k, v in by_tier.most_common()) or "none"))
            res.summary.append("Paid sales by source: " + (", ".join(f"{k} {v}" for k, v in by_src.most_common()) or "none"))
            if paid:
                res.summary.append(f"First confirmed paid sale: {min(s['date'] for s in paid if s['date'])}")
            if len(paid) >= 10 and len(refunded) / len(paid) > 0.10:
                res.findings.append(f"Refund rate {len(refunded) / len(paid):.0%} is above 10% — read refund reasons.")
            if cb:
                res.findings.append("Chargeback recorded — owner must respond in the payment processor (critical).")
        if traffic is None:
            res.summary.append("No traffic data (analytics/data/traffic.csv missing).")
        else:
            visits = sum(int(t.get("visits") or 0) for t in traffic)
            clicks = sum(int(t.get("buy_clicks") or 0) for t in traffic)
            res.metrics["Visits"] = visits
            res.metrics["Buy-button clicks"] = clicks
            res.metrics["Click rate"] = f"{clicks / visits:.1%}" if visits else "n/a"
            if sales is not None:
                n = len([s for s in sales if s["status"] in PAID and s["gross"] > 0])
                res.metrics["Visit -> paid sale conversion"] = f"{n / visits:.2%}" if visits else "n/a"
                res.metrics["Click -> paid sale"] = f"{n / clicks:.1%}" if clicks else "n/a"
                if visits >= 300 and n == 0:
                    res.findings.append("300+ visits and no sale: investigate offer, price, trust, traffic quality "
                                        "and checkout (see docs/13_OPERATIONS_MANUAL.md §Diagnosis).")
                if clicks >= 30 and n == 0:
                    res.findings.append("30+ buy clicks and no sale: possible checkout problem — test the checkout page manually.")
        return res


# ========================================================= 7. FINANCE =======

class FinancialController(Agent):
    name = "financial_controller"

    def run(self) -> Result:
        res = Result(self.name)
        cfgp = self.data_dir / "finance.json"
        cfg = json.loads(cfgp.read_text()) if cfgp.exists() else {}
        refund_pct = float(cfg.get("refund_reserve_pct", 0.10))
        tax_pct = float(cfg.get("tax_reserve_pct", 0.0))
        withdrawn = float(cfg.get("already_withdrawn_or_spent_usd", 0.0))
        sales = load_sales(self)
        if sales is None:
            res.summary.append("No sales data. Balance available for reinvestment: $0.00 (nothing is assumed).")
            res.metrics["Free balance for reinvestment USD"] = "0.00"
            return res
        paid = [s for s in sales if s["status"] in PAID]
        refunded = [s for s in sales if s["status"] in REFUNDED | CHARGEBACK]
        gross = sum(s["gross"] for s in paid)
        fees = sum(s["fees"] for s in paid)
        refunds = sum(s["gross"] for s in refunded)
        net = gross - fees - refunds
        recent = [s for s in paid if s["date"] and s["date"] >= today() - dt.timedelta(days=30)]
        refund_reserve = sum(s["gross"] for s in recent) * refund_pct
        tax_reserve = max(net, 0) * tax_pct
        free_balance = max(net - refund_reserve - tax_reserve - withdrawn, 0)
        res.metrics.update({
            "Gross confirmed sales USD": f"{gross:,.2f}",
            "Fees USD": f"{fees:,.2f}",
            "Refunds + chargebacks USD": f"{refunds:,.2f}",
            "Net after fees and refunds USD": f"{net:,.2f}",
            f"Refund reserve ({refund_pct:.0%} of last 30 days) USD": f"{refund_reserve:,.2f}",
            f"Tax reserve ({tax_pct:.0%}, set by owner/accountant) USD": f"{tax_reserve:,.2f}",
            "Already withdrawn/spent USD": f"{withdrawn:,.2f}",
            "Free balance for reinvestment USD": f"{free_balance:,.2f}",
        })
        res.summary.append("Figures come only from recorded sales. Confirm the money actually arrived in PayPal/bank "
                           "before any decision. Currency conversion to BRL and IOF are not included.")
        if tax_pct == 0:
            res.findings.append("Tax reserve is 0% — ask an accountant (Carnê-Leão / MEI / export of services) and set tax_reserve_pct.")
        if free_balance > 0:
            plan = [(0.40, "keep as cash reserve"), (0.20, "fix problems found by support/QA"),
                    (0.20, "product improvements (e.g., Spanish version)"), (0.20, "domain name (~$10-15/yr) or small tests")]
            res.proposals.append("Reinvestment plan for $%.2f: %s" % (free_balance, "; ".join(f"{p:.0%} {d} (${free_balance * p:,.2f})" for p, d in plan)))
        return res


# ========================================================= 6. SUPPORT =======

TEMPLATES = {
    "download": ("How to download", "Thanks for your order! Your download link is in the Payhip email (check spam/promotions). "
                 "You can also open the link from your receipt. If it still does not work, reply with the email used at checkout and we will resend it."),
    "google_sheets": ("Using Google Sheets", "Upload the .xlsx to Google Drive, open it, then choose File > Save as Google Sheets. "
                      "Everything (formulas, drop-downs, charts) works there. Guide: section 2 of the User Guide."),
    "excel_version": ("Excel version", "The kit needs Excel 2019, 2021 or Microsoft 365 — or the free Excel for the web (onedrive.live.com). "
                      "Older Excel versions show #NAME? on the Clients sheet. Google Sheets also works."),
    "how_to": ("How to use", "Start with the Settings sheet (your pay rate, speed, overhead, margin), then the Price Calculator. "
               "The User Guide PDF walks through every sheet in about 15 minutes. Happy to help with a specific question!"),
    "upgrade": ("Upgrade", "We can help you switch tiers by paying only the difference. Reply with your order email and the tier you want."),
}
RULES = [
    ("chargeback", r"chargeback|dispute|bank claim|fraud"),
    ("refund", r"refund|money back|cancel (my )?order"),
    ("legal", r"lawyer|attorney|legal|sue|copyright"),
    ("angry", r"scam|terrible|worst|ripoff|rip-off"),
    ("download", r"download|link|expired|didn.?t receive|did not receive|email.*(file|product)"),
    ("google_sheets", r"google|sheets|drive"),
    ("excel_version", r"#name|excel 20(1[0-6])|mac excel|won.?t open|cannot open|can.?t open|read.?only"),
    ("upgrade", r"upgrade|premium instead|wrong (tier|version)"),
    ("how_to", r"how (do|to)|where|setting|calculator|price|formula"),
]
ESCALATE = {"chargeback", "refund", "legal", "angry"}


class CustomerSupport(Agent):
    name = "customer_support"

    def classify(self, text: str) -> str:
        t = text.lower()
        for cat, rx in RULES:
            if re.search(rx, t):
                return cat
        return "other"

    def run(self) -> Result:
        res = Result(self.name)
        inbox = read_csv(self.data_dir / "support_inbox.csv")
        if inbox is None:
            res.summary.append("No support inbox file (analytics/data/support_inbox.csv). Nothing to triage.")
            return res
        counts = collections.Counter()
        drafts = []
        for i, m in enumerate(inbox, 1):
            cat = self.classify(m.get("subject", "") + " " + m.get("message", ""))
            counts[cat] += 1
            who = m.get("from", "")
            if cat in ESCALATE or cat == "other":
                res.proposals.append(f"Message #{i} from {who} ({cat}) needs a personal answer from the owner.")
            else:
                subj, body = TEMPLATES[cat]
                drafts.append(f"### Message #{i} — {cat}\nTo: {who}\nSubject: Re: {subj}\n\n{body}\n\n— TidyMargin Support\n")
        res.metrics.update({f"Messages: {k}": v for k, v in counts.most_common()})
        if drafts:
            out = self.reports_dir / "support_drafts"
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{today().isoformat()}.md").write_text("# Draft replies (NOT sent — review and send manually)\n\n" + "\n".join(drafts))
            res.summary.append(f"{len(drafts)} draft replies written to reports/support_drafts/ (not sent).")
        top = counts.most_common(1)
        if top and top[0][1] >= 3 and top[0][0] not in ESCALATE:
            res.findings.append(f"Recurring question '{top[0][0]}' ({top[0][1]}x): improve the product page/FAQ.")
        return res


# ================================================== 4. CONTENT MARKETING ====

BANNED = [r"guarantee", r"get rich", r"\$\d[\d,]* ?(a|per) (month|week) (guaranteed|easy)", r"best .* in the world",
          r"customers? (say|love)", r"\b\d+ ?(stars|★)", r"testimonial", r"passive income"]


class ContentMarketing(Agent):
    name = "content_marketing"

    def run(self) -> Result:
        res = Result(self.name)
        cal = read_csv(ROOT / "marketing" / "content_calendar.csv")
        if cal is None:
            res.ok = False
            res.findings.append("marketing/content_calendar.csv missing — run marketing/calendar_data.py")
            return res
        status = collections.Counter(r.get("status", "draft") for r in cal)
        res.metrics.update({f"Content {k}": v for k, v in status.items()})
        for r in cal:
            text = " ".join(r.get(k, "") for k in ("title", "script_or_outline", "caption"))
            for rx in BANNED:
                if re.search(rx, text, re.I):
                    res.findings.append(f"Day {r['day']} '{r['title']}': risky claim pattern /{rx}/ — rewrite.")
            if len(r.get("caption", "")) > 500:
                res.findings.append(f"Day {r['day']}: caption longer than 500 characters.")
            if r.get("status") == "published" and not r.get("published_url"):
                res.findings.append(f"Day {r['day']}: marked published but no URL recorded.")
        nxt = [r for r in cal if r.get("status", "draft") != "published"][:3]
        for r in nxt:
            res.proposals.append(f"Publish day {r['day']} [{r['channel']}] '{r['title']}' using asset {r['asset']} "
                                 "(owner posts manually; then set status=published and the URL in content_calendar.csv).")
        res.summary.append("No content is posted automatically: there is no authorized posting integration.")
        return res


# ================================================== 8. QUALITY MONITOR ======

REQUIRED_SHEETS = {
    "starter": {"Start Here", "Settings", "Price Calculator", "Quote Table", "Margin vs Markup", "Estimate"},
    "complete": {"Clients", "Schedule", "Transactions", "Monthly Summary", "Invoice"},
    "premium": {"Dashboard", "Goal Planner", "Commercial Bid", "Crew Cost", "Checklists"},
}


class QualityMonitor(Agent):
    name = "quality_monitor"
    allowed_actions = {"read_local", "write_report", "http_get_own_urls"}

    def check_url(self, url: str) -> str:
        self.require("http_get_own_urls")
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "TidyMargin-QA/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return str(r.status)
        except Exception as e:
            return f"ERROR {type(e).__name__}"

    def run(self) -> Result:
        res = Result(self.name)
        rel = ROOT / "products" / "release"
        import openpyxl
        need = set()
        for tier in TIERS:
            need |= REQUIRED_SHEETS[tier]
            z = rel / f"TidyMargin-{tier.title()}.zip"
            if not z.exists():
                res.findings.append(f"Missing release file {z.name}")
                res.ok = False
                continue
            with zipfile.ZipFile(z) as zf:
                bad = zf.testzip()
                names = zf.namelist()
                if bad:
                    res.findings.append(f"{z.name}: corrupt member {bad}")
                for must in (f"TidyMargin-{tier.title()}.xlsx", "TidyMargin-User-Guide.pdf", "README.txt"):
                    if must not in names:
                        res.findings.append(f"{z.name}: missing {must}")
                with zf.open(f"TidyMargin-{tier.title()}.xlsx") as fh:
                    import io
                    wb = openpyxl.load_workbook(io.BytesIO(fh.read()))
                    missing = need - set(wb.sheetnames)
                    if missing:
                        res.findings.append(f"{z.name}: missing sheets {sorted(missing)}")
            res.summary.append(f"{z.name}: {z.stat().st_size / 1024:.0f} KB, {len(names)} files OK")
        cfg = json.loads((ROOT / "deployment" / "store_config.json").read_text())
        empty = [k for k in ("site_url", "support_email") if not cfg.get(k)] + \
                [f"checkout.{k}" for k, v in cfg["checkout"].items() if not v]
        if empty:
            res.findings.append("Store config incomplete (site will show 'Coming soon'): " + ", ".join(empty))
        dist = ROOT / "website" / "dist"
        broken = []
        for page in dist.rglob("*.html"):
            for href in re.findall(r'href="([^"#:]+\.html)', page.read_text()):
                if not (page.parent / href).resolve().exists():
                    broken.append(f"{page.relative_to(dist)} -> {href}")
        res.metrics["Website pages"] = len(list(dist.rglob("*.html")))
        res.metrics["Broken internal links"] = len(broken)
        res.findings += [f"Broken link {b}" for b in broken]
        urls = [cfg.get("site_url")] + list(cfg["checkout"].values())
        for u in [u for u in urls if u]:
            status = self.check_url(u)
            res.metrics[f"HTTP {u}"] = status
            if not status.startswith("2"):
                res.findings.append(f"Live URL not OK: {u} -> {status}")
            time.sleep(1)
        return res


# ================================================== 3. PRODUCT MANAGER =====

class ProductManager(Agent):
    name = "product_manager"
    allowed_actions = {"read_local", "write_report", "run_tests"}

    def run(self) -> Result:
        res = Result(self.name)
        self.require("run_tests")
        p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests")],
                           capture_output=True, text=True, timeout=600)
        tail = (p.stderr or p.stdout).strip().splitlines()[-3:]
        res.metrics["Automated tests"] = "PASS" if p.returncode == 0 else "FAIL"
        res.summary.append("Test run: " + " | ".join(tail))
        if p.returncode != 0:
            res.ok = False
            res.findings.append("Automated tests failing — do not upload new files until fixed.")
        support = Path(self.reports_dir / "agent_runs" / f"{today().isoformat()}-customer_support.md")
        if support.exists() and "Recurring question" in support.read_text():
            res.proposals.append("Support shows a recurring question — add it to FAQ / product page.")
        res.summary.append("Backlog (see docs/14_GROWTH_ROADMAP.md): Spanish version, Airbnb turnover add-on, "
                           "lawn care kit (Feb 2027), Sheets template link, video walkthrough.")
        return res


# ================================================== 2. MARKET RESEARCH =====

class MarketResearch(Agent):
    name = "market_research"
    allowed_actions = {"read_local", "write_report", "http_get_public"}
    MAX_REQUESTS = 15

    def allowed_by_robots(self, url: str) -> bool:
        parts = urllib.parse.urlsplit(url)
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{parts.scheme}://{parts.netloc}/robots.txt")
        try:
            rp.read()
        except Exception:
            return False  # cannot verify -> do not fetch
        return rp.can_fetch("TidyMargin-Research/1.0", url)

    def fetch(self, url: str) -> str | None:
        self.require("http_get_public")
        if not self.allowed_by_robots(url):
            self.log("robots_block", url=url)
            return None
        req = urllib.request.Request(url, headers={"User-Agent": "TidyMargin-Research/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read(800_000).decode("utf-8", "replace")

    def run(self) -> Result:
        res = Result(self.name)
        comps = read_csv(self.data_dir / "competitors.csv")
        if comps is None:
            res.summary.append("No competitor watchlist (analytics/data/competitors.csv). See docs/market-research/COMPETITOR_ANALYSIS.md.")
            return res
        for c in comps[: self.MAX_REQUESTS]:
            url = c.get("url", "")
            try:
                page = self.fetch(url)
            except Exception as e:
                res.findings.append(f"{c.get('name')}: could not fetch ({type(e).__name__})")
                continue
            if page is None:
                res.findings.append(f"{c.get('name')}: blocked by robots.txt or unverifiable — skipped")
                continue
            prices = sorted(set(re.findall(r"\$\s?(\d{1,3}(?:\.\d{2})?)", page)))[:6]
            title = re.search(r"<title>(.*?)</title>", page, re.S | re.I)
            res.summary.append(f"{c.get('name')}: title='{(title.group(1).strip() if title else '?')[:80]}', "
                               f"$ values on page: {', '.join(prices) or 'none found'} (needs human check; not proof of sales)")
            time.sleep(3)
        return res


# ================================================================ 1. CEO =====

class CEO(Agent):
    name = "ceo"

    def __init__(self, *a, team=None, **kw):
        super().__init__(*a, **kw)
        self.team = team or [QualityMonitor, SalesAnalyst, FinancialController, CustomerSupport, ContentMarketing]

    def run(self) -> Result:
        res = Result(self.name)
        results = []
        for cls in self.team:
            r = cls(self.data_dir, self.reports_dir, self.logs_dir).execute()
            results.append(r)
            res.summary.append(f"{r.agent}: {'OK' if r.ok else 'PROBLEM'} — {len(r.findings)} findings, {len(r.proposals)} proposals")
        problems = [f"[{r.agent}] {f}" for r in results for f in r.findings]
        res.findings += problems
        # priorities: blockers first, then revenue, then growth
        sales = next((r for r in results if r.agent == "sales_analyst"), None)
        confirmed = int(sales.metrics.get("Confirmed paid sales", 0)) if sales and sales.metrics else 0
        if any("Store config incomplete" in p for p in problems):
            res.proposals.append("PRIORITY 1: finish store setup (Payhip account, PayPal, upload ZIPs, fill store_config.json, publish site).")
        if confirmed == 0:
            res.proposals.append("PRIORITY 2: publish the next 3 calendar items and record traffic weekly (no sale recorded yet — no forecast is made).")
        else:
            res.proposals.append(f"{confirmed} confirmed paid sale(s): verify payout in PayPal, then review the financial_controller reinvestment proposal.")
        res.metrics["Agents run"] = len(results)
        res.metrics["Total findings"] = len(problems)
        return res


ALL = {"ceo": CEO, "market_research": MarketResearch, "product_manager": ProductManager,
       "content_marketing": ContentMarketing, "sales_analyst": SalesAnalyst,
       "customer_support": CustomerSupport, "financial_controller": FinancialController,
       "quality_monitor": QualityMonitor}
