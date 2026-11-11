"""Write the HTML sources for product covers, Pinterest pins, Instagram and YouTube
templates into brand/src/ plus a manifest; then run `node brand/render.mjs`.

All product images use AUTHENTIC screenshots rendered from the real workbooks
(brand/screenshots/*.png, produced by kit/render_previews.py).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "brand" / "src"

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,'Segoe UI',Helvetica,Arial,sans-serif;color:#1E2A30;-webkit-font-smoothing:antialiased}
.teal{color:#0F5257}.gold{color:#E8A33D}
.canvas{position:relative;overflow:hidden;width:100vw;height:100vh;background:#F4F8F8}
.logo{display:flex;align-items:center;gap:14px;font-weight:800;font-size:34px;letter-spacing:-.5px}
.logo img{width:52px;height:52px}
.badge{display:inline-block;padding:8px 16px;border-radius:999px;font-weight:700;font-size:20px}
.b-teal{background:#0F5257;color:#fff}.b-gold{background:#E8A33D;color:#1E2A30}.b-soft{background:#D7ECEC;color:#0B3B3F}
.window{background:#fff;border-radius:18px;box-shadow:0 30px 70px rgba(11,59,63,.28);overflow:hidden;border:1px solid #C9D3D6}
.window .bar{height:34px;background:#EEF2F3;display:flex;gap:8px;align-items:center;padding:0 14px}
.window .bar i{width:12px;height:12px;border-radius:50%;background:#C9D3D6;display:block}
.window img{display:block;width:100%}
ul.ticks{list-style:none}
ul.ticks li{position:relative;padding-left:40px;margin:14px 0;font-size:26px;font-weight:600}
ul.ticks li:before{content:"";position:absolute;left:0;top:4px;width:26px;height:26px;border-radius:8px;background:#2E8B57;
 -webkit-mask:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M5 12l5 5 9-10" stroke="black" stroke-width="3.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>') center/80% no-repeat, linear-gradient(#000,#000);
 -webkit-mask-composite:source-in}
.blob{position:absolute;border-radius:50%;filter:blur(2px)}
"""


def page(body, extra_css=""):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><style>{CSS}{extra_css}</style></head>
<body><div class="canvas">{body}</div></body></html>"""


def window(shot, style=""):
    return (f'<div class="window" style="{style}"><div class="bar"><i></i><i></i><i></i></div>'
            f'<img src="../screenshots/{shot}.png" alt=""></div>')


LOGO = '<div class="logo"><img src="../logo/icon.svg" alt=""><span><span class="teal">Tidy</span><span class="gold">Margin</span></span></div>'

COVERS = {
    "free": ("FREE TOOL", "Quick Price Check", "Is your cleaning price really profitable?",
             ["Price for a true profit margin", "See the money markup pricing misses", "Excel + Google Sheets"],
             "calculator", "b-soft"),
    "starter": ("STARTER", "Cleaning Price Calculator", "Quote every job from your real costs.",
                ["Sq ft, rooms, service type & condition", "Margin, card fees & overhead built in",
                 "50-job Quote Table + printable Estimate", "Excel + Google Sheets"], "calculator", "b-soft"),
    "complete": ("COMPLETE · MOST POPULAR", "Cleaning Business Profit Kit", "Price, schedule, invoice and track profit in one file.",
                 ["Price Calculator + Quote Table", "Clients, Schedule & follow-up flags", "Profit tracker + monthly summary",
                  "Estimates & invoices", "Excel + Google Sheets"], "summary", "b-gold"),
    "premium": ("PREMIUM", "Profit Kit + Commercial Pro", "Residential AND commercial pricing, plus a live dashboard.",
                ["Everything in Complete", "Business dashboard with charts", "Commercial contract bid calculator",
                 "Goal planner, crew cost, checklists", "Pricing Playbook (PDF)"], "dashboard", "b-teal"),
}


SECOND = {"starter": "estimate", "complete": "calculator", "premium": "commercial", "free": "margin"}


def cover(key):
    tag, title, sub, bullets, shot, badge = COVERS[key]
    lis = "".join(f"<li>{b}</li>" for b in bullets)
    body = f"""
<div class="blob" style="width:900px;height:900px;right:-300px;top:-250px;background:#D7ECEC"></div>
<div class="blob" style="width:420px;height:420px;left:-160px;bottom:-180px;background:#FCEFD6"></div>
<div style="position:absolute;left:80px;top:70px;width:640px">
  {LOGO}
  <div style="margin-top:56px"><span class="badge {badge}">{tag}</span></div>
  <h1 style="font-size:64px;line-height:1.04;margin-top:22px;letter-spacing:-1.5px" class="teal">{title}</h1>
  <p style="font-size:28px;margin-top:18px;color:#5F6F76;line-height:1.3">{sub}</p>
  <ul class="ticks" style="margin-top:26px">{lis}</ul>
</div>
{window(shot, "position:absolute;left:770px;top:110px;width:790px;transform:rotate(1.5deg)")}
{window(SECOND[key], "position:absolute;left:860px;top:650px;width:560px;height:440px;transform:rotate(-2deg)") if SECOND.get(key) else ""}
<div style="position:absolute;left:80px;bottom:60px;font-size:22px;color:#5F6F76">Instant download · No subscription · No macros</div>
"""
    return page(body)


PINS = [
    ("pin-undercharging", "Are you <span class='gold'>undercharging</span> for house cleaning?",
     "A 30% markup is only a 23% profit margin. Here is the math.", "margin"),
    ("pin-deep-clean", "How much should you charge for a <span class='gold'>deep clean</span>?",
     "Price it from your real hours, pay, supplies and overhead.", "calculator"),
    ("pin-estimate", "Free-to-customize <span class='gold'>cleaning estimate</span> layout",
     "Printable, professional, Excel + Google Sheets.", "estimate"),
    ("pin-commercial", "How to bid an <span class='gold'>office cleaning</span> contract",
     "Monthly price from sq ft, visits and production rate.", "commercial"),
    ("pin-profit", "Know your <span class='gold'>real profit</span> every month",
     "Revenue, expenses, cash flow and profit per labor hour.", "summary"),
]


def pin(title, sub, shot):
    body = f"""
<div style="position:absolute;inset:0;background:linear-gradient(180deg,#0F5257 0%,#0B3B3F 100%)"></div>
<div style="position:absolute;left:70px;right:70px;top:80px;color:#fff">
  <h1 style="font-size:76px;line-height:1.05;letter-spacing:-1.5px">{title}</h1>
  <p style="font-size:34px;margin-top:28px;color:#D7ECEC;line-height:1.3">{sub}</p>
</div>
{window(shot, "position:absolute;left:70px;right:70px;top:640px")}
<div style="position:absolute;left:0;right:0;bottom:0;height:150px;background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 70px">
  {LOGO}<span class="badge b-gold" style="font-size:24px">Excel + Google Sheets</span>
</div>"""
    return page(body)


IG = [
    ("ig-tip-markup", "TIP", "30% markup ≠ 30% margin", "Cost $100 → charge $130 = only 23.1% margin.<br>For a real 30% margin, charge <b>$142.86</b>."),
    ("ig-tip-minimum", "TIP", "Set a minimum job price", "Small jobs still cost drive time, setup and a slot in your day. A minimum price protects every booking."),
    ("ig-tip-overhead", "TIP", "Spread your overhead", "Insurance + phone + software + marketing ÷ jobs per month = what each job must also cover."),
]


def ig(tag, title, text):
    body = f"""
<div style="position:absolute;inset:0;background:#F4F8F8"></div>
<div style="position:absolute;inset:60px;background:#fff;border-radius:36px;box-shadow:0 20px 50px rgba(11,59,63,.15);padding:70px">
  <span class="badge b-gold">{tag}</span>
  <h1 class="teal" style="font-size:78px;line-height:1.05;margin-top:36px;letter-spacing:-1.5px">{title}</h1>
  <p style="font-size:38px;line-height:1.4;margin-top:40px;color:#1E2A30">{text}</p>
  <div style="position:absolute;left:70px;bottom:60px">{LOGO}</div>
</div>"""
    return page(body)


YT = [
    ("yt-price-a-clean", "I priced a deep clean<br>with <span class='gold'>REAL</span> costs", "calculator"),
    ("yt-markup-mistake", "The <span class='gold'>pricing mistake</span><br>cleaners make", "margin"),
]


def yt(title, shot):
    body = f"""
<div style="position:absolute;inset:0;background:#0F5257"></div>
<div style="position:absolute;left:60px;top:70px;width:640px;color:#fff">
  <h1 style="font-size:76px;line-height:1.05;letter-spacing:-1.5px">{title}</h1>
  <div style="margin-top:34px"><span class="badge b-gold" style="font-size:28px">Free calculator inside</span></div>
</div>
{window(shot, "position:absolute;left:720px;top:80px;width:520px;transform:rotate(2deg)")}
<div style="position:absolute;left:60px;bottom:50px;background:#fff;border-radius:16px;padding:10px 18px">{LOGO}</div>"""
    return page(body)


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    manifest = [
        {"src": "../logo/icon.svg", "out": "logo/icon-512.png", "w": 128, "h": 128, "scale": 4, "transparent": True},
        {"src": "../logo/logo.svg", "out": "logo/logo-1120.png", "w": 560, "h": 128, "scale": 2, "transparent": True},
        {"src": "../logo/logo-reverse.svg", "out": "logo/logo-reverse-1120.png", "w": 560, "h": 128, "scale": 2, "transparent": True},
    ]
    for key in COVERS:
        (SRC / f"cover-{key}.html").write_text(cover(key))
        manifest.append({"src": f"src/cover-{key}.html", "out": f"covers/cover-{key}.png", "w": 1600, "h": 1200})
    for slug, title, sub, shot in PINS:
        (SRC / f"{slug}.html").write_text(pin(title, sub, shot))
        manifest.append({"src": f"src/{slug}.html", "out": f"social/{slug}.png", "w": 1000, "h": 1500})
    for slug, tag, title, text in IG:
        (SRC / f"{slug}.html").write_text(ig(tag, title, text))
        manifest.append({"src": f"src/{slug}.html", "out": f"social/{slug}.png", "w": 1080, "h": 1080})
    for slug, title, shot in YT:
        (SRC / f"{slug}.html").write_text(yt(title, shot))
        manifest.append({"src": f"src/{slug}.html", "out": f"social/{slug}.png", "w": 1280, "h": 720})
    # the SVG entries are loaded relative to brand/, fix their paths
    for m in manifest[:3]:
        m["src"] = m["src"].replace("../", "")
    (SRC / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"wrote {len(manifest)} assets to manifest")


if __name__ == "__main__":
    main()
