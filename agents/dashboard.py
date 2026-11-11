"""Static control panel: analytics/dashboard.html (open in any browser, no server).

Shows ONLY recorded data. Orders are separated from confirmed payments,
net revenue is shown before income taxes, and missing inputs say "no data".
"""
import collections
import html
import json
from pathlib import Path

from common import DATA, ROOT, read_csv, today
from team import PAID, PENDING, REFUNDED, CHARGEBACK, FinancialController, load_sales, product_tier


class _Reader(FinancialController):
    pass


def build_dashboard(data_dir: Path = DATA, out: Path = ROOT / "analytics" / "dashboard.html") -> Path:
    agent = _Reader(data_dir=data_dir)
    sales = load_sales(agent)
    traffic = read_csv(data_dir / "traffic.csv")
    cal = read_csv(ROOT / "marketing" / "content_calendar.csv") or []
    fin = agent.run().metrics
    k = {}
    if sales is None:
        k["Sales data"] = "no data — export sales from Payhip to analytics/data/sales.csv"
    else:
        paid = [s for s in sales if s["status"] in PAID and s["gross"] > 0]
        gross = sum(s["gross"] for s in paid)
        fees = sum(s["fees"] for s in paid)
        k.update({
            "Orders recorded": len(sales),
            "Confirmed paid sales": len(paid),
            "Pending payments (not revenue)": len([s for s in sales if s["status"] in PENDING]),
            "Gross revenue (USD)": f"${gross:,.2f}",
            "Fees (USD)": f"${fees:,.2f}",
            "Net revenue before income tax (USD)": f"${gross - fees:,.2f}",
            "Refunds": len([s for s in sales if s["status"] in REFUNDED]),
            "Chargebacks": len([s for s in sales if s["status"] in CHARGEBACK]),
            "Average order (USD)": f"${gross / len(paid):,.2f}" if paid else "n/a",
            "Products sold": ", ".join(f"{t}: {n}" for t, n in collections.Counter(product_tier(s['product']) for s in paid).most_common()) or "none",
        })
    if traffic is None:
        k["Traffic data"] = "no data — add analytics/data/traffic.csv (Cloudflare Web Analytics)"
    else:
        visits = sum(int(t.get("visits") or 0) for t in traffic)
        clicks = sum(int(t.get("buy_clicks") or 0) for t in traffic)
        by_src = collections.Counter()
        for t in traffic:
            by_src[t.get("source") or "unknown"] += int(t.get("visits") or 0)
        k["Visitors"] = visits
        k["Buy clicks"] = clicks
        if sales is not None and visits:
            k["Conversion (paid sales / visits)"] = f"{k['Confirmed paid sales'] / visits:.2%}"
        k["Traffic sources"] = ", ".join(f"{s}: {n}" for s, n in by_src.most_common(5))
    pub = [c for c in cal if c.get("status") == "published"]
    k["Content published"] = f"{len(pub)} of {len(cal)}"
    k["Balance free for reinvestment (USD)"] = "$" + fin.get("Free balance for reinvestment USD", "0.00")
    rows = "".join(f"<tr><th>{html.escape(str(a))}</th><td>{html.escape(str(b))}</td></tr>" for a, b in k.items())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TidyMargin — control panel</title><style>body{{font-family:Inter,system-ui,sans-serif;max-width:860px;margin:40px auto;padding:0 16px;color:#1E2A30}}
h1{{color:#0F5257}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #DDE5E7}}th{{width:45%;color:#5F6F76;font-weight:600}}
.note{{background:#FCEFD6;padding:12px 16px;border-radius:10px}}</style></head><body>
<h1>TidyMargin — control panel</h1><p>Generated {today().isoformat()} from recorded files only.</p>
<p class="note">Orders are not payments. Net revenue is before income taxes and currency conversion. Confirm payouts in PayPal before spending anything.</p>
<table>{rows}</table></body></html>""")
    return out
