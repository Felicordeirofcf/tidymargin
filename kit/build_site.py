"""Build the static TidyMargin website into website/dist/.

Usage: python3 kit/build_site.py
Reads deployment/store_config.json (checkout links, support email, analytics).
Empty checkout links render as disabled "Coming soon" buttons — never a fake checkout.
Static HTML/CSS only, no JavaScript framework, no cookies.
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "website"
DIST = WEB / "dist"
CFG = json.loads((ROOT / "deployment" / "store_config.json").read_text())
UPDATED = "November 11, 2026"


def esc(s):
    return html.escape(str(s), quote=True)


# ------------------------------------------------------------- markdown ----

def md_inline(t):
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', t)
    return t


def md_to_html(md):
    out, lst, table = [], None, []

    def close():
        nonlocal lst, table
        if lst:
            out.append(f"</{lst}>")
            lst = None
        if table:
            rows = [r for r in table if not re.match(r"^\|[\s\-|]+\|$", r)]
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            h = "".join(f"<th>{md_inline(c)}</th>" for c in cells[0])
            b = "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>" for r in cells[1:])
            out.append(f'<div class="table-wrap"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>')
            table = []

    for line in md.splitlines():
        s = line.rstrip()
        if s.startswith("|"):
            table.append(s)
            continue
        m = re.match(r"^(\d+)\. (.*)", s)
        if s.startswith("- ") or m:
            kind = "ul" if s.startswith("- ") else "ol"
            if table:
                close()
            if lst != kind:
                if lst:
                    out.append(f"</{lst}>")
                out.append(f"<{kind}>")
                lst = kind
            out.append(f"<li>{md_inline(s[2:] if kind == 'ul' else m.group(2))}</li>")
            continue
        close()
        if not s:
            continue
        if s.startswith("### "):
            out.append(f"<h3>{md_inline(s[4:])}</h3>")
        elif s.startswith("## "):
            out.append(f"<h2>{md_inline(s[3:])}</h2>")
        elif s.startswith("# "):
            out.append(f"<h1>{md_inline(s[2:])}</h1>")
        elif s.startswith("> "):
            out.append(f"<blockquote>{md_inline(s[2:])}</blockquote>")
        else:
            out.append(f"<p>{md_inline(s)}</p>")
    close()
    return "\n".join(out)


def front_matter(text):
    meta = {}
    if text.startswith("---"):
        _, fm, text = text.split("---", 2)
        for line in fm.strip().splitlines():
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text


# --------------------------------------------------------------- layout ----

CSS = """
:root{--teal:#0F5257;--teal-d:#0B3B3F;--teal-l:#D7ECEC;--gold:#E8A33D;--gold-l:#FCEFD6;--ink:#1E2A30;--muted:#5F6F76;--line:#DDE5E7;--bg:#F6F9F9;--ok:#2E8B57;--r:16px}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--ink);line-height:1.6;background:#fff;-webkit-font-smoothing:antialiased}
a{color:var(--teal)}a:hover{color:var(--teal-d)}
img{max-width:100%;height:auto;display:block}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-999px}.skip:focus{left:12px;top:12px;background:#fff;padding:8px;z-index:9}
header.site{position:sticky;top:0;background:rgba(255,255,255,.94);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);z-index:5}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;height:64px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:20px;text-decoration:none;color:var(--teal);letter-spacing:-.3px}
.brand img{width:32px;height:32px}.brand b{color:var(--gold)}
nav.top a{margin-left:20px;text-decoration:none;color:var(--ink);font-weight:500;font-size:15px}
nav.top a.btn{color:#fff}
.btn{display:inline-block;background:var(--teal);color:#fff;text-decoration:none;font-weight:700;padding:12px 22px;border-radius:12px;border:2px solid var(--teal);transition:.15s}
.btn:hover{background:var(--teal-d);color:#fff}
.btn.gold{background:var(--gold);border-color:var(--gold);color:var(--ink)}.btn.gold:hover{background:#d8922c}
.btn.ghost{background:transparent;color:var(--teal)}.btn.ghost:hover{background:var(--teal-l)}
.btn.disabled{background:#E6E9EA;border-color:#E6E9EA;color:#5F6F76;cursor:not-allowed}
.hero{background:linear-gradient(180deg,var(--bg),#fff);padding:64px 0 40px}
.hero .wrap{display:grid;grid-template-columns:1.05fr 1fr;gap:48px;align-items:center}
.eyebrow{display:inline-block;background:var(--teal-l);color:var(--teal-d);font-weight:700;font-size:13px;padding:6px 12px;border-radius:999px;letter-spacing:.3px}
h1{font-size:clamp(34px,5vw,54px);line-height:1.06;letter-spacing:-1.2px;margin:16px 0;color:var(--teal-d)}
h2{font-size:clamp(26px,3.4vw,36px);line-height:1.15;letter-spacing:-.6px;color:var(--teal-d);margin:0 0 14px}
h3{font-size:19px;margin:0 0 6px;color:var(--ink)}
.lead{font-size:19px;color:var(--muted);max-width:560px}
.cta-row{display:flex;gap:12px;flex-wrap:wrap;margin:26px 0 12px}
.small{font-size:14px;color:var(--muted)}
.shot{border-radius:var(--r);box-shadow:0 24px 60px rgba(11,59,63,.18);border:1px solid var(--line);background:#fff;overflow:hidden}
section{padding:64px 0}section.alt{background:var(--bg)}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:40px;align-items:center}
.card{background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:24px}
.card p{margin:6px 0 0;color:var(--muted)}
.num{display:inline-flex;width:34px;height:34px;border-radius:10px;background:var(--gold-l);color:var(--teal-d);font-weight:800;align-items:center;justify-content:center;margin-bottom:10px}
ul.checks{list-style:none;padding:0;margin:14px 0}ul.checks li{padding-left:30px;position:relative;margin:9px 0}
ul.checks li:before{content:"✓";position:absolute;left:0;top:0;color:#fff;background:var(--ok);width:20px;height:20px;border-radius:6px;font-size:13px;display:flex;align-items:center;justify-content:center;margin-top:3px}
ul.checks li.no{color:#9AA6AB}ul.checks li.no:before{content:"–";background:#C9D3D6}
.pricing{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;align-items:stretch}
.plan{background:#fff;border:1px solid var(--line);border-radius:20px;padding:28px;display:flex;flex-direction:column}
.plan.pop{border:2px solid var(--gold);box-shadow:0 18px 40px rgba(232,163,61,.18);position:relative}
.plan .tag{position:absolute;top:-14px;left:28px;background:var(--gold);color:var(--ink);font-weight:800;font-size:12px;padding:5px 12px;border-radius:999px}
.price{font-size:44px;font-weight:800;color:var(--teal-d);letter-spacing:-1px}.price span{font-size:16px;color:var(--muted);font-weight:500}
.plan .btn{margin-top:auto;text-align:center}
.compare{width:100%;border-collapse:collapse;background:#fff;border-radius:var(--r);overflow:hidden;font-size:15px}
.compare th,.compare td{padding:12px 14px;border-bottom:1px solid var(--line);text-align:center}
.compare th:first-child,.compare td:first-child{text-align:left}
.compare thead th{background:var(--teal);color:#fff}
.yes{color:var(--ok);font-weight:800}.nope{color:#B7C1C5}
details{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin:10px 0}
summary{cursor:pointer;font-weight:700}details p{margin:10px 0 0;color:var(--muted)}
.notice{background:var(--gold-l);border-radius:12px;padding:14px 18px;font-size:15px}
footer{background:var(--teal-d);color:#D7ECEC;padding:44px 0 30px;font-size:15px}
footer a{color:#fff;text-decoration:none}footer a:hover{text-decoration:underline}
footer .cols{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:24px}
footer h4{color:#fff;margin:0 0 10px;font-size:15px}footer ul{list-style:none;padding:0;margin:0}footer li{margin:6px 0}
article{max-width:760px;margin:0 auto;padding:48px 20px}
article h1{font-size:clamp(30px,4.4vw,44px)}article h2{font-size:26px;margin-top:34px}
article blockquote{background:var(--gold-l);margin:18px 0;padding:14px 18px;border-radius:12px;font-weight:600}
.table-wrap{overflow-x:auto}article table{border-collapse:collapse;width:100%;margin:12px 0}
article th,article td{border:1px solid var(--line);padding:8px 12px;text-align:left}article th{background:var(--teal-l)}
.toc a{display:block;margin:4px 0}
@media (max-width:860px){.hero .wrap,.grid2{grid-template-columns:1fr}.grid3,.pricing{grid-template-columns:1fr}footer .cols{grid-template-columns:1fr 1fr}nav.top a:not(.btn){display:none}}
"""


def checkout(tier, label, cls="btn"):
    url = CFG["checkout"].get(tier)
    if url:
        return f'<a class="{cls}" href="{esc(url)}" rel="noopener">{esc(label)}</a>'
    return f'<span class="btn disabled" aria-disabled="true" title="Checkout link not configured yet">Coming soon</span>'


def analytics():
    tok = CFG.get("cloudflare_analytics_token")
    if not tok:
        return ""
    return ("<script defer src='https://static.cloudflareinsights.com/beacon.min.js' "
            f"data-cf-beacon='{{\"token\": \"{esc(tok)}\"}}'></script>")


def layout(title, description, body, depth=0, canonical="", jsonld=None):
    up = "../" * depth
    site = CFG.get("site_url", "").rstrip("/")
    canon = f'<link rel="canonical" href="{esc(site + "/" + canonical)}">' if site else ""
    og_img = f'<meta property="og:image" content="{esc(site)}/assets/cover-complete.png">' if site else ""
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{canon}
<meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">{og_img}
<meta name="theme-color" content="#0F5257">
<link rel="icon" href="{up}assets/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="wrap">
  <a class="brand" href="{up}index.html" aria-label="TidyMargin home"><img src="{up}assets/icon.svg" alt="" width="32" height="32"><span>Tidy<b>Margin</b></span></a>
  <nav class="top" aria-label="Main"><a href="{up}index.html#features">Features</a><a href="{up}index.html#pricing">Pricing</a><a href="{up}articles/index.html">Guides</a><a href="{up}help.html">Help</a><a class="btn" href="{up}index.html#pricing">Get the kit</a></nav>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
  <div class="cols">
    <div><a class="brand" href="{up}index.html" style="color:#fff"><img src="{up}assets/icon.svg" alt="" width="32" height="32"><span>Tidy<b>Margin</b></span></a>
      <p>Pricing and profit spreadsheets for cleaning businesses. Excel + Google Sheets. One-time purchase.</p>
      <p class="small" style="color:#9fc4c4">TidyMargin is a business-management tool, not accounting, tax or legal advice.</p></div>
    <div><h4>Product</h4><ul><li><a href="{up}index.html#pricing">Pricing</a></li><li><a href="{up}index.html#free">Free calculator</a></li><li><a href="{up}articles/index.html">Guides</a></li></ul></div>
    <div><h4>Support</h4><ul><li><a href="{up}help.html">Help center</a></li><li><a href="{up}help.html#contact">Contact</a></li><li><a href="{up}refund.html">Refund policy</a></li></ul></div>
    <div><h4>Legal</h4><ul><li><a href="{up}privacy.html">Privacy</a></li><li><a href="{up}terms.html">Terms</a></li></ul></div>
  </div>
  <p class="small" style="color:#9fc4c4;margin-top:28px">© 2026 TidyMargin. Microsoft Excel and Google Sheets are trademarks of their owners; TidyMargin is not affiliated with Microsoft or Google.</p>
</div></footer>
{analytics()}
</body>
</html>
"""


# ---------------------------------------------------------------- pages ----

FEATURES = [
    ("Price Calculator", "Square feet, bedrooms, bathrooms, service type, frequency and home condition become labor hours, cost and a price that hits your margin.", "starter"),
    ("Check-a-price verdict", "Type a price you have in mind. See instantly if it meets your margin, is below target, or loses money.", "starter"),
    ("Quote Table", "Price up to 50 jobs side by side. Margins below target turn red.", "starter"),
    ("Printable estimate", "A clean, branded estimate you can save as PDF and send.", "starter"),
    ("Clients & Schedule", "Client list with last and next visit, follow-up flags and lifetime revenue. Visit schedule with status and staff.", "complete"),
    ("Profit tracker", "Income and expenses by month, estimated profit, cash flow and revenue per labor hour.", "complete"),
    ("Invoices", "Invoice with due date, payments received and balance due.", "complete"),
    ("Dashboard", "Year-to-date and monthly results, operations KPIs and charts on one screen.", "premium"),
    ("Commercial Bid", "Monthly contract price for offices from sq ft, production rate and visits per week.", "premium"),
    ("Planners & Playbook", "Goal/break-even planner, crew cost planner, printable checklists and the Pricing Playbook PDF.", "premium"),
]

COMPARE = [
    ("Price Calculator + Check a price", 1, 1, 1),
    ("Quote Table (50 jobs)", 1, 1, 1),
    ("Margin vs Markup converter", 1, 1, 1),
    ("Printable estimate", 1, 1, 1),
    ("Clients with follow-up flags", 0, 1, 1),
    ("Schedule with status & staff", 0, 1, 1),
    ("Transactions + Monthly Summary", 0, 1, 1),
    ("Invoice", 0, 1, 1),
    ("Dashboard with charts", 0, 0, 1),
    ("Commercial contract bid calculator", 0, 0, 1),
    ("Goal planner & crew cost planner", 0, 0, 1),
    ("Cleaning checklists", 0, 0, 1),
    ("Pricing Playbook (PDF)", 0, 0, 1),
    ("User guide (PDF) + example file", 1, 1, 1),
]

FAQ = [
    ("Does it work in Google Sheets?", "Yes. Upload the .xlsx file to Google Drive and choose File > Save as Google Sheets. All formulas, drop-downs and charts work. Sheet protection is not imported, so the grey formula cells are not locked in Google Sheets."),
    ("Which Excel versions are supported?", "Excel 2019, 2021 and Microsoft 365 (Windows and Mac) and the free Excel for the web. There are no macros. Excel 2016 and older lack two functions used by the Clients sheet."),
    ("Is this a subscription?", "No. You pay once and keep the files. There is nothing to log in to."),
    ("Will it tell me what to charge in my city?", "No tool can know your local market. TidyMargin calculates the price your own costs and target margin require. The default rates are examples that you replace with your own numbers. Compare the result with your local market and decide."),
    ("Where is my data stored?", "In your own file, on your computer or in your own Google or Microsoft account. We never see it."),
    ("Can I use it on my phone?", "Yes, in the Excel or Google Sheets app. Setting it up is easier on a computer."),
    ("Does the invoice collect payments?", "No. It is a professional document you send. Your clients pay you the way you already accept payments."),
    ("Is this tax or accounting advice?", "No. It is a business-management tool that estimates profit. Talk to a tax professional about taxes."),
    ("What if it does not work for me?", "Contact us and we will help. If we cannot fix a problem with the files, see our refund policy."),
]


def index_page():
    prices = CFG["prices_usd"]
    feats = "".join(f'<div class="card"><h3>{esc(t)}</h3><p>{esc(d)}</p><p class="small" style="margin-top:10px">Included in: '
                    f'<strong>{"Starter, Complete, Premium" if tier == "starter" else "Complete, Premium" if tier == "complete" else "Premium"}</strong></p></div>'
                    for t, d, tier in FEATURES)
    rows = "".join(f"<tr><td>{esc(n)}</td>" + "".join(f'<td class="{"yes" if v else "nope"}" aria-label="{"Included" if v else "Not included"}">{"✓" if v else "–"}</td>' for v in vals) + "</tr>"
                   for n, *vals in COMPARE)
    faq = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in FAQ)
    plan = lambda tier, title, sub, items, pop=False: f"""
<div class="plan{' pop' if pop else ''}">{'<span class="tag">MOST POPULAR</span>' if pop else ''}
<h3>{title}</h3><p class="small">{sub}</p>
<div class="price">${prices[tier]}<span> one-time</span></div>
<ul class="checks">{''.join(f'<li>{esc(i)}</li>' for i in items)}</ul>
{checkout(tier, f'Buy {title} — ${prices[tier]}', 'btn gold' if pop else 'btn')}
</div>"""
    body = f"""
<section class="hero"><div class="wrap">
  <div>
    <span class="eyebrow">For residential & commercial cleaning businesses</span>
    <h1>Price every cleaning job for profit.</h1>
    <p class="lead">TidyMargin turns your real costs — pay, time, supplies, travel, overhead and card fees — into a price that hits the margin you choose. Then it tracks clients, visits and profit. Excel + Google Sheets, one-time purchase.</p>
    <div class="cta-row"><a class="btn gold" href="#pricing">See the kits — from ${prices['starter']}</a><a class="btn ghost" href="#free">Try the free calculator</a></div>
    <p class="small">Instant download · No subscription · No macros · Your data stays in your file</p>
  </div>
  <div class="shot"><img src="assets/shot-calculator.png" alt="TidyMargin Price Calculator showing a deep clean priced at $295 with a 30.3% net margin" width="1100" height="1400" loading="eager"></div>
</div></section>

<section id="problem"><div class="wrap grid2">
  <div><h2>Busy all week, but where is the profit?</h2>
  <p>Many cleaning owners price by copying competitors or national averages. Then payroll taxes, drive time, card fees and insurance quietly eat the margin. A 30% markup is only a 23% margin — before overhead.</p>
  <ul class="checks"><li>See the full cost of every job before you quote it</li><li>Price for the margin you actually want, with discounts that do not eat it</li><li>Catch prices that lose money — with a red warning, not a surprise at tax time</li></ul></div>
  <div class="shot"><img src="assets/shot-margin.png" alt="Margin vs markup converter: a 30% markup on a $100 cost is only a 23.1% margin" width="1100" height="700" loading="lazy"></div>
</div></section>

<section class="alt" id="how"><div class="wrap">
  <h2>How it works</h2>
  <div class="grid3">
    <div class="card"><span class="num">1</span><h3>Enter your numbers once</h3><p>Pay rate, speed, overhead, card fee, target margin, minimum price. Every default is an example you replace.</p></div>
    <div class="card"><span class="num">2</span><h3>Describe the job</h3><p>Sq ft, rooms, service type, frequency, condition, supplies and miles.</p></div>
    <div class="card"><span class="num">3</span><h3>Quote with confidence</h3><p>Get the price, the regular price before discounts and your profit — then print the estimate.</p></div>
  </div>
</div></section>

<section id="features"><div class="wrap">
  <h2>Everything a small cleaning business needs to run the numbers</h2>
  <p class="lead">Real screenshots from the kit (example data).</p>
  <div class="grid2" style="margin:26px 0 36px">
    <div class="shot"><img src="assets/shot-dashboard.png" alt="Premium dashboard with year-to-date revenue, profit, cash flow and charts" loading="lazy" width="1600" height="1100"></div>
    <div class="shot"><img src="assets/shot-estimate.png" alt="Printable cleaning estimate with line items, discount and total" loading="lazy" width="1100" height="1400"></div>
  </div>
  <div class="grid3">{feats}</div>
</div></section>

<section class="alt" id="pricing"><div class="wrap">
  <h2>Pick your kit</h2>
  <p class="lead">One-time price in USD. Less than one month of most cleaning scheduling software — and you keep it.</p>
  <div class="pricing" style="margin-top:30px">
    {plan('starter', 'Starter', 'Price jobs right', ['Price Calculator + Check a price', 'Quote Table for 50 jobs', 'Printable estimate', 'Margin vs Markup converter', 'User guide + example file'])}
    {plan('complete', 'Complete', 'Price, schedule & track profit', ['Everything in Starter', 'Clients with follow-up flags', 'Schedule with status & staff', 'Profit tracker + monthly summary', 'Invoice'], True)}
    {plan('premium', 'Premium', 'Residential + commercial pro', ['Everything in Complete', 'Dashboard with charts', 'Commercial contract bid calculator', 'Goal & crew cost planners, checklists', 'Pricing Playbook (PDF)'])}
  </div>
  <h3 style="margin-top:44px">Compare</h3>
  <div class="table-wrap"><table class="compare"><thead><tr><th>Feature</th><th>Starter</th><th>Complete</th><th>Premium</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="small" style="margin-top:14px">Checkout, payment and instant download are handled securely by our store platform (Payhip). Prices in USD; applicable taxes are calculated at checkout.</p>
</div></section>

<section id="free"><div class="wrap grid2">
  <div><span class="eyebrow">Free</span><h2>Try the Quick Price Check</h2>
  <p>A one-sheet calculator that shows the price for your margin — and how much money markup pricing leaves on the table. Free download, Excel + Google Sheets.</p>
  {checkout('free', 'Get the free calculator', 'btn gold')}</div>
  <div class="shot"><img src="assets/cover-free.png" alt="Quick Price Check free calculator cover" loading="lazy" width="1600" height="1200"></div>
</div></section>

<section class="alt" id="faq"><div class="wrap" style="max-width:820px">
  <h2>Questions</h2>{faq}
  <p style="margin-top:20px">More answers in the <a href="help.html">help center</a>.</p>
</div></section>
"""
    product_ld = {
        "@context": "https://schema.org", "@type": "Product", "name": brand.PRODUCT,
        "description": "Excel and Google Sheets kit for cleaning businesses: price calculator, quote table, estimates, invoices, clients, schedule and profit tracker.",
        "brand": {"@type": "Brand", "name": brand.NAME},
        "offers": [{"@type": "Offer", "name": f"{t.title()} kit", "price": f"{prices[t]}.00", "priceCurrency": "USD",
                    "availability": "https://schema.org/InStock" if CFG["checkout"].get(t) else "https://schema.org/PreOrder",
                    **({"url": CFG["checkout"][t]} if CFG["checkout"].get(t) else {})}
                   for t in ("starter", "complete", "premium")],
    }
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    return layout("TidyMargin — Cleaning Business Pricing Calculator & Profit Kit (Excel + Google Sheets)",
                  "Price every cleaning job for profit. Pricing calculator, estimates, invoices, client schedule and profit tracker for cleaning businesses. Excel + Google Sheets. One-time purchase.",
                  body, 0, "", [product_ld, faq_ld])


def support_email_html():
    e = CFG.get("support_email")
    if e:
        return f'<a href="mailto:{esc(e)}">{esc(e)}</a>'
    return "the contact option in your Payhip purchase email"


def seller():
    return esc(CFG.get("seller_name") or "the owner of TidyMargin")


def text_page(slug, title, desc, md):
    body = f'<article>{md_to_html(md)}<p class="small">Last updated: {UPDATED}</p></article>'
    return layout(f"{title} — TidyMargin", desc, body, 0, f"{slug}.html")


def help_md():
    guide = (ROOT / "products" / "guides" / "user-guide.md").read_text()
    guide = guide.split("\n", 1)[1]  # drop H1
    return f"""# Help Center

Quick answers for TidyMargin customers. Can't find what you need? [Contact us](#contact).

## Contents

- [How to download](#download)
- [Getting started](#start)
- [Refunds](#refunds)
- [Contact support](#contact)

## How to download {{#download}}

1. After checkout you see a download button, and you receive an email from Payhip with a download link.
2. Download the ZIP file and unzip it (Windows: right-click > Extract All. Mac: double-click).
3. If the email does not arrive within 15 minutes, check spam and promotions folders. Still nothing? Contact us with the email address you used at checkout.

## Getting started {{#start}}
{guide}

## Refunds {{#refunds}}

See our [refund policy](refund.html).

## Contact support {{#contact}}

Email: {support_email_html()}. Please include your order email and, if possible, a screenshot. We reply within 2 business days (Monday to Friday). We will never ask for your passwords or card details.
"""


def anchors(htm):
    return re.sub(r"<h2>(.+?) \{#(\w+)\}</h2>", r'<h2 id="\2">\1</h2>', htm)


PRIVACY = """# Privacy Policy

This policy explains what information is handled when you visit this website or buy a TidyMargin product. This website and the TidyMargin products are operated by {seller}, an independent seller based in Brazil.

## The short version

- The spreadsheets run on your own computer or account. **We never see what you type into them.**
- This website does not use advertising cookies or trackers.
- Purchases are processed by Payhip and its payment partners (PayPal or Stripe). We do not see or store your full card number.

## Information we receive

- **Order information** from our store platform (Payhip): your name, email address, the product you bought, the amount, the date and your country. We use it to deliver your purchase, provide support, handle refunds and keep the records required by law.
- **Support messages** you send us. We use them only to answer you.
- **Website statistics.** If enabled, we use Cloudflare Web Analytics, which reports aggregate visit counts without cookies and without building individual profiles.

## Information we do not collect

We do not collect the client, schedule or financial data you enter into the spreadsheets. We do not sell or rent personal information, and we do not share it for advertising.

## Service providers

- **Payhip** (store, checkout, file delivery, sales tax/VAT handling): see payhip.com for its privacy policy.
- **PayPal / Stripe** (payment processing): see their privacy policies.
- **Cloudflare** (website hosting and, if enabled, cookieless analytics).
- **Email provider** used to answer support messages.

These providers process information on their own systems, which may be located in the United States and other countries.

## How long we keep information

Order records are kept as long as needed for support, refunds, and legal and tax obligations. Support emails are deleted when no longer needed, normally within 24 months.

## Your choices and rights

You can ask us to access, correct or delete the personal information we hold about you, or ask questions about it, by writing to {email}. Depending on where you live (for example California, other US states, the EU/UK or Brazil under the LGPD) you may have additional rights; we will honor them as required. Some information may have to be kept to meet legal obligations. We will not discriminate against you for exercising your rights.

## Children

Our products are intended for business owners and are not directed to children under 16.

## Changes

If we change this policy, we will update the date below.
"""

TERMS = """# Terms of Sale and Use

These terms apply to purchases of TidyMargin digital products and to the use of this website. The products are sold by {seller}, an independent seller based in Brazil, through the Payhip platform.

## The product

TidyMargin products are digital spreadsheet files (Microsoft Excel .xlsx, compatible with Google Sheets) and PDF guides, delivered by instant download after payment. Product pages describe what each tier includes. Screenshots show the real files with fictional example data.

## License

When you buy a TidyMargin product you receive a non-exclusive, non-transferable license for **one business** to use the files on any number of devices used by that business. You may edit the files for your own business. You may not resell, share, publish, or distribute the files or modified versions of them, in whole or in part.

## No professional advice

TidyMargin is a business-management tool. Results depend entirely on the numbers you enter. Default values in the files are examples, not recommendations or market prices. The products do not provide accounting, tax, legal or financial advice. You are responsible for your prices, your tax filings and your compliance with the laws that apply to your business. Consult a qualified professional for advice.

## No guarantee of results

We do not promise any specific income, profit or business result.

## Compatibility

The files are designed for Microsoft Excel 2019, 2021, Microsoft 365, Excel for the web and Google Sheets. Older or other spreadsheet programs may not support every feature.

## Prices and payment

Prices are shown in US dollars. Payment and any applicable sales tax or VAT are processed by Payhip and its payment partners at checkout.

## Refunds

See our [Refund Policy](refund.html).

## Limitation of liability

To the maximum extent permitted by law, our total liability for any claim related to a product is limited to the amount you paid for it, and we are not liable for indirect or consequential damages, including lost profits. Nothing in these terms limits rights you have under consumer-protection laws that cannot be waived.

## Contact

{email}
"""

REFUND = """# Refund Policy

We want TidyMargin to work for your business.

## 14-day promise

If a TidyMargin product does not work as described on its product page and we cannot fix the problem, you can request a full refund within **14 days** of purchase.

How to request:

1. Write to {email} with your order email and a short description of the problem (a screenshot helps).
2. We usually reply within 2 business days, and most problems are solved with a quick tip (for example opening the file in Google Sheets or Excel for the web).
3. If we cannot solve it, we refund the full price through the original payment method via Payhip. Your bank or PayPal may take several business days to show it.

## When refunds are not available

Because the files are delivered instantly and cannot be returned, we do not normally refund because of a change of mind after downloading, or for a product bought by mistake when a different tier was intended — but contact us: in that case we are happy to help you switch tiers by paying only the difference.

## Duplicate purchases

If you were charged twice for the same product, contact us and we will refund the duplicate.

## Chargebacks

Please contact us before opening a dispute with your bank or PayPal. We respond quickly and it is usually faster for you.

Nothing in this policy limits rights you may have under applicable consumer-protection laws.
"""


def article_pages():
    items = []
    for md in sorted((WEB / "content").glob("*.md")):
        meta, text = front_matter(md.read_text())
        cta = (f'<div class="notice" style="margin-top:30px"><strong>Do the math in seconds.</strong> '
               f'<a href="../index.html#free">Get the free Quick Price Check</a> or see the '
               f'<a href="../index.html#pricing">TidyMargin kits</a>.</div>')
        ld = {"@context": "https://schema.org", "@type": "Article", "headline": meta["title"],
              "description": meta["description"], "author": {"@type": "Organization", "name": brand.NAME},
              "datePublished": "2026-11-11", "dateModified": "2026-11-11"}
        body = f'<article><p class="small"><a href="index.html">Guides</a></p>{md_to_html(text)}{cta}<p class="small">Published {UPDATED}. General business education, not tax or legal advice.</p></article>'
        (DIST / "articles" / f"{meta['slug']}.html").write_text(
            layout(f"{meta['title']} — TidyMargin", meta["description"], body, 1, f"articles/{meta['slug']}.html", [ld]))
        items.append(meta)
    lis = "".join(f'<div class="card"><h3><a href="{m["slug"]}.html">{esc(m["title"])}</a></h3><p>{esc(m["description"])}</p></div>' for m in items)
    (DIST / "articles" / "index.html").write_text(layout(
        "Cleaning Business Pricing Guides — TidyMargin", "Free guides on pricing cleaning jobs, margins and commercial bids.",
        f'<article style="max-width:900px"><h1>Pricing guides</h1><p class="lead">Practical, free guides for cleaning business owners.</p><div class="grid3" style="grid-template-columns:1fr">{lis}</div></article>',
        1, "articles/index.html"))
    return items


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    (DIST / "articles").mkdir()
    (DIST / "assets" / "site.css").write_text(CSS)
    shutil.copy(ROOT / "brand" / "logo" / "icon.svg", DIST / "assets" / "icon.svg")
    for name in ("calculator", "dashboard", "estimate", "margin", "summary", "commercial"):
        shutil.copy(ROOT / "brand" / "screenshots" / f"{name}.png", DIST / "assets" / f"shot-{name}.png")
    for name in ("free", "complete"):
        shutil.copy(ROOT / "brand" / "covers" / f"cover-{name}.png", DIST / "assets" / f"cover-{name}.png")
    email = support_email_html()
    (DIST / "index.html").write_text(index_page())
    (DIST / "help.html").write_text(layout("Help Center — TidyMargin", "How to download, open and use TidyMargin in Excel and Google Sheets.",
                                           f'<article>{anchors(md_to_html(help_md()))}</article>', 0, "help.html"))
    (DIST / "privacy.html").write_text(text_page("privacy", "Privacy Policy", "How TidyMargin handles personal information.",
                                                 PRIVACY.format(seller=seller(), email=email)))
    (DIST / "terms.html").write_text(text_page("terms", "Terms of Sale and Use", "License and terms for TidyMargin products.",
                                               TERMS.format(seller=seller(), email=email)))
    (DIST / "refund.html").write_text(text_page("refund", "Refund Policy", "TidyMargin refund policy.", REFUND.format(email=email)))
    (DIST / "404.html").write_text(layout("Page not found — TidyMargin", "Page not found.",
                                          '<article><h1>Page not found</h1><p><a href="index.html">Go to the home page</a></p></article>'))
    arts = article_pages()
    site = CFG.get("site_url", "").rstrip("/")
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\n" + (f"Sitemap: {site}/sitemap.xml\n" if site else ""))
    if site:
        urls = ["", "help.html", "privacy.html", "terms.html", "refund.html", "articles/index.html"] + [f"articles/{a['slug']}.html" for a in arts]
        (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                          + "".join(f"  <url><loc>{site}/{u}</loc><lastmod>2026-11-11</lastmod></url>\n" for u in urls) + "</urlset>\n")
    warnings = [k for k in ("site_url", "support_email", "seller_name") if not CFG.get(k)]
    warnings += [f"checkout.{k}" for k, v in CFG["checkout"].items() if not v]
    print(f"built {len(list(DIST.rglob('*.html')))} pages into {DIST}")
    if warnings:
        print("NOT READY TO PUBLISH — fill in deployment/store_config.json:", ", ".join(warnings))


if __name__ == "__main__":
    main()
