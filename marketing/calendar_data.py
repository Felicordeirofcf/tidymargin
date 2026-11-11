"""30-day organic content calendar (source of truth).

Run `python3 marketing/calendar_data.py` to regenerate content_calendar.csv and
CONTENT_CALENDAR_30_DAYS.md.  Channels (see 09_MARKETING_PLAN.md):
  primary   -> Pinterest (PIN) and YouTube Shorts/long (YTS / YT)
  secondary -> SEO articles on the site (ART)
Shorts scripts are reused as TikTok / Instagram Reels only if the owner opts in.
No fake testimonials, no income claims, no posting in communities that forbid promotion.
FACELESS: the owner does not appear. Videos = screen recordings of the EXAMPLE file + on-screen text
(optional royalty-free music); no face, no voice required.
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
FREE = "Free Quick Price Check (link in bio / description)"
KIT = "TidyMargin kit (link in bio / description)"

# day, channel, title, script_or_outline, caption, keywords, cta, asset
ITEMS = [
    (1, "YTS", "30% markup is NOT a 30% margin",
     "HOOK: 'You add 30% to your costs. You think you keep 30%. You don't.' | SHOW: $100 cost -> $130 price -> $30 profit = 23.1% of the price. | FIX: for a real 30% margin divide by 0.7 -> $142.86. | CLOSE: 'Free calculator in the description.'",
     "Markup and margin are not the same number. Here is the 20-second math every cleaning business owner should know. #cleaningbusiness #pricing #smallbusiness",
     "markup vs margin, cleaning business pricing", FREE, "brand/social/yt-markup-mistake.png + Margin vs Markup sheet screen recording"),
    (1, "PIN", "Are you undercharging for house cleaning?",
     "Pin -> article markup-vs-margin-cleaning", "A 30% markup is only a 23% margin. See the math and the conversion table.",
     "cleaning business pricing, house cleaning prices", "Read the guide", "brand/social/pin-undercharging.png"),
    (2, "ART", "How to Price House Cleaning Jobs (Step by Step)",
     "Publish website/content/how-to-price-house-cleaning.md; share link on Pinterest board 'Cleaning Business Tips'.",
     "Step-by-step pricing from your own hours and costs.", "how to price house cleaning, cleaning business pricing calculator", FREE, "site article"),
    (3, "YTS", "I priced a 2,200 sq ft deep clean with real costs",
     "HOOK: 'How much for a 2,200 square foot deep clean? Let's do the real math.' | SHOW calculator: 3 bed/2 bath, 2 cleaners, 6.9 labor hours, $18/h + 12% burden, supplies, 14 miles, overhead share -> cost $197 -> $295 at 30% margin. | NOTE: 'These are example numbers - plug in yours.' | CLOSE: 'Calculator in the description.'",
     "Real deep-clean pricing math with example numbers. Use your own costs! #deepcleaning #cleaningbusiness",
     "how much to charge for deep cleaning, deep cleaning price calculator", KIT, "Price Calculator screen recording (EXAMPLE file)"),
    (3, "PIN", "How much should you charge for a deep clean?",
     "Pin -> article how-to-price-house-cleaning", "Price a deep clean from your real hours, pay, supplies and overhead.",
     "deep cleaning prices, cleaning estimate", "Read the guide", "brand/social/pin-deep-clean.png"),
    (4, "YTS", "The cost most cleaners forget: drive time",
     "HOOK: 'Your cleaner is paid 40 hours but only cleans 30.' | SHOW Crew Cost: $18/h, 75% billable -> $26.88 real cost per billable hour. | CLOSE: 'Price for the hours you pay, not just the hours you clean.'",
     "Non-billable time is a real cost. #cleaningbusiness #smallbusinesstips", "cleaning business labor cost", KIT, "Crew Cost sheet"),
    (5, "PIN", "Cleaning estimate layout (printable)",
     "Pin -> site #features", "A clean, professional estimate you can save as PDF.", "cleaning estimate template, house cleaning estimate template", "See the kit", "brand/social/pin-estimate.png"),
    (6, "YTS", "Set a minimum job price (here's why)",
     "HOOK: 'A $60 job can cost you money.' | SHOW: drive + setup + 1.5 h -> cost vs price. | FIX: minimum price in Settings. | CLOSE.",
     "Small jobs still cost a drive and a slot in your day. #cleaningtips #pricing", "minimum price cleaning service", FREE, "Settings + calculator"),
    (7, "YT", "Cleaning Business Pricing Calculator - full walkthrough (8 min)",
     "OUTLINE: 1) why averages fail 2) Settings tour 3) price a standard clean 4) recurring discount done right 5) check-a-price 6) estimate to PDF 7) where to get it. Show EXAMPLE file only.",
     "Full walkthrough of the TidyMargin price calculator for Excel and Google Sheets. Default numbers are examples - use your own.",
     "cleaning business pricing calculator, cleaning service quote calculator", KIT, "screen recording"),
    (8, "PIN", "Know your real profit every month",
     "Pin -> site #pricing", "Revenue, expenses, cash flow and profit per labor hour in one sheet.", "cleaning business profit tracker", "See the kit", "brand/social/pin-profit.png"),
    (9, "YTS", "Recurring discount without losing money",
     "HOOK: '15% off weekly cleans... from whose pocket?' | SHOW: price that keeps margin + regular price shown before discount. | CLOSE.",
     "Discount the regular price, keep your margin. #recurringrevenue #cleaningbusiness", "weekly cleaning discount, biweekly cleaning price", KIT, "calculator Weekly example"),
    (10, "ART", "Markup vs Margin for Cleaning Businesses",
     "Publish website/content/markup-vs-margin-cleaning.md.", "The conversion table every owner should bookmark.", "markup vs margin", FREE, "site article"),
    (11, "YTS", "Profit vs cash: why a busy month can feel broke",
     "HOOK: 'Best month ever... and the bank account is empty?' | SHOW Monthly Summary: profit vs cash in vs pending. | CLOSE.",
     "Profit is not cash. Track both. #smallbusinessfinance #cleaningbusiness", "cleaning business cash flow", KIT, "Monthly Summary sheet"),
    (12, "PIN", "How to bid an office cleaning contract",
     "Pin -> article commercial-cleaning-bid", "Monthly price from sq ft, visits per week and production rate.", "commercial cleaning bid, office cleaning pricing", "Read the guide", "brand/social/pin-commercial.png"),
    (13, "YTS", "Price an office cleaning contract in 30 seconds",
     "HOOK: '5,000 square feet, 3 nights a week. What's the monthly price?' | SHOW Commercial Bid: 2 h/visit, 13 visits -> cost $778 -> ~$1,160/month at 30% margin (example rates). | CLOSE.",
     "Commercial bid math with example numbers. #commercialcleaning #janitorial", "commercial cleaning pricing calculator, cleaning contract pricing", KIT, "Commercial Bid sheet"),
    (14, "ART", "How to Bid a Commercial Cleaning Contract",
     "Publish website/content/commercial-cleaning-bid.md.", "", "commercial cleaning bid calculator excel", KIT, "site article"),
    (15, "YTS", "3 numbers to check every Friday",
     "HOOK: '15 minutes every Friday.' | SHOW Dashboard: unpaid balances, follow-ups, next week's bookings. | CLOSE.",
     "A weekly money routine for cleaning business owners. #cleaningbusinessowner", "cleaning business management template", KIT, "Dashboard"),
    (16, "PIN", "Free cleaning price calculator (Excel + Google Sheets)",
     "Pin -> free tool", "See the price your margin needs - and what markup misses.", "free cleaning price calculator", "Get it free", "brand/covers/cover-free.png"),
    (17, "YTS", "How long should a standard clean take? Time YOUR crew",
     "HOOK: 'Stop guessing hours.' | SHOW: write sq ft + labor hours for 5 jobs -> sq ft per labor hour -> Settings. | CLOSE.",
     "Your speed is your most important pricing number. #cleaningtips", "cleaning time per square foot", FREE, "Settings sheet"),
    (18, "PIN", "Move-out cleaning checklist (printable)",
     "Pin -> site #features", "Room-by-room move-out checklist for your crew.", "move out cleaning checklist", "See the kit", "Checklists screenshot (render from Premium)"),
    (19, "YTS", "Card fees eat your margin (unless you price them in)",
     "HOOK: '2.9% doesn't sound like much...' | SHOW: price with and without fee in the formula. | CLOSE.",
     "Price card fees in, don't absorb them. #smallbusiness", "cleaning business fees", FREE, "calculator"),
    (20, "YTS", "Clients you forgot to rebook",
     "HOOK: 'Your easiest revenue is a client you already have.' | SHOW Clients follow-up flag. | CLOSE.",
     "Follow-up flags for clients with no visit booked. #customerretention", "cleaning client list template", KIT, "Clients sheet"),
    (21, "YT", "Run your cleaning business numbers in Google Sheets (10 min)",
     "OUTLINE: upload to Drive, save as Google Sheets, Settings, Clients, Schedule, Transactions, Summary; tips for phone use.",
     "How to use the TidyMargin kit in Google Sheets.", "cleaning business template google sheets", KIT, "screen recording"),
    (22, "PIN", "Cleaning business pricing mistakes",
     "Idea pin / list pin -> markup article", "7 common pricing mistakes and how to fix them.", "cleaning business pricing mistakes", "Read the guide", "new pin from template"),
    (23, "YTS", "When to raise your cleaning prices",
     "HOOK: 'Full schedule? That's a pricing signal.' | SHOW: margin below target 3 months + script for a 30-day notice. | CLOSE.",
     "Signs it's time to raise prices + a polite message template. #pricing", "how to raise cleaning prices", KIT, "Quote Table"),
    (24, "PIN", "Cleaning invoice layout",
     "Pin -> site", "Invoice with due date, payments and balance due.", "cleaning business invoice template", "See the kit", "Invoice screenshot"),
    (25, "YTS", "How many cleans do you need per month?",
     "HOOK: 'Want $4,000 a month for yourself?' | SHOW Goal Planner (example inputs). | CLOSE.",
     "Break-even + pay goal in one sheet (example numbers). #cleaningbusiness", "cleaning business break even", KIT, "Goal Planner"),
    (26, "PIN", "How much to charge for move-out cleaning",
     "Pin -> article how-to-price", "Price move-outs from time, not guesses.", "move out cleaning prices", "Read the guide", "new pin from template"),
    (27, "YTS", "Estimate in 60 seconds",
     "HOOK: 'Client wants a quote now.' | SHOW calculator -> estimate -> PDF. | CLOSE.",
     "From calculator to PDF estimate. #cleaningbusiness", "house cleaning estimate template", KIT, "Estimate sheet"),
    (28, "PIN", "Revenue per labor hour: the number that matters",
     "Pin -> site #features", "Track it monthly on the summary.", "cleaning business profit", "See the kit", "Summary screenshot"),
    (29, "YTS", "Gross vs net margin in 30 seconds",
     "HOOK: '46% margin... or 30%?' | SHOW calculator gross/contribution/net. | CLOSE.",
     "Gross margin ignores overhead. #smallbusinessfinance", "gross vs net margin", FREE, "calculator results"),
    (30, "REVIEW", "Month-1 review",
     "Run: python3 agents/run_agents.py report. Compare views/clicks/sales per channel, keep the top 2 formats, drop the bottom 2.",
     "", "", "", "reports/"),
]


def main():
    with open(HERE / "content_calendar.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["day", "channel", "title", "script_or_outline", "caption", "keywords", "cta", "asset", "status", "published_url"])
        for it in ITEMS:
            w.writerow([*it, "draft", ""])
    names = {"YTS": "YouTube Short (also Reels/TikTok if opted in)", "YT": "YouTube video", "PIN": "Pinterest pin",
             "ART": "Site article", "REVIEW": "Review"}
    lines = ["# 30-Day Content Calendar (English, US audience)", "",
             "Generated from `marketing/calendar_data.py`. Status is tracked in `content_calendar.csv`.",
             "Every video uses the EXAMPLE file and says the numbers are examples. No testimonials, no income promises.",
             "**Faceless format:** screen recording + on-screen text captions. The owner never appears on camera or voice.", ""]
    for d, ch, title, script, cap, kw, cta, asset in ITEMS:
        lines += [f"## Day {d} · {names[ch]}: {title}", "",
                  f"- **Script / outline:** {script}" if script else "",
                  f"- **Caption:** {cap}" if cap else "",
                  f"- **Keywords:** {kw}" if kw else "",
                  f"- **CTA:** {cta}" if cta else "",
                  f"- **Asset:** {asset}", ""]
    (HERE / "CONTENT_CALENDAR_30_DAYS.md").write_text("\n".join(l for l in lines if l is not None))
    print(f"{len(ITEMS)} items written")


if __name__ == "__main__":
    main()
