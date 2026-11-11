"""Render the Markdown guides in products/guides/ to branded PDFs and package
each tier into a ready-to-upload ZIP.

Usage: python3 kit/make_guides.py
Outputs:
  products/guides/TidyMargin-User-Guide.pdf
  products/guides/TidyMargin-Pricing-Playbook.pdf
  products/release/TidyMargin-{Starter,Complete,Premium}.zip
  products/release/TidyMargin-Quick-Price-Check-FREE.zip
"""
import re
import sys
import zipfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import brand  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GUIDES = ROOT / "products" / "guides"
RELEASE = ROOT / "products" / "release"
TEAL = colors.HexColor("#" + brand.COLORS["primary"])
GOLD = colors.HexColor("#" + brand.COLORS["accent"])
INK = colors.HexColor("#" + brand.COLORS["ink"])
MUTED = colors.HexColor("#" + brand.COLORS["muted"])
SOFT = colors.HexColor("#" + brand.COLORS["accent_light"])

S = {
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=24, leading=29, textColor=TEAL, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=TEAL, spaceBefore=14, spaceAfter=6, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=INK, spaceBefore=8, spaceAfter=3, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK, spaceAfter=6, alignment=TA_LEFT),
    "quote": ParagraphStyle("q", fontName="Helvetica-Oblique", fontSize=10.5, leading=15, textColor=INK,
                            backColor=SOFT, borderPadding=(8, 10, 8, 10), leftIndent=6, rightIndent=6,
                            spaceBefore=6, spaceAfter=12),
    "cell": ParagraphStyle("c", fontName="Helvetica", fontSize=9.5, leading=12, textColor=INK),
    "cellb": ParagraphStyle("cb", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.white),
}

SUBS = {"≠": "is not", "→": "->", "×": "x", "−": "-", "“": '"', "”": '"', "’": "'"}


def inline(text):
    for a, b in SUBS.items():
        text = text.replace(a, b)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text


def parse(md):
    flow, bullets, numbered, table = [], [], [], []

    def flush():
        nonlocal bullets, numbered, table
        if bullets:
            flow.append(ListFlowable([ListItem(Paragraph(inline(b), S["p"]), leftIndent=14) for b in bullets],
                                     bulletType="bullet", bulletColor=GOLD, leftIndent=14, bulletFontSize=8))
        if numbered:
            flow.append(ListFlowable([ListItem(Paragraph(inline(b), S["p"]), leftIndent=16) for b in numbered],
                                     bulletType="1", bulletColor=TEAL, leftIndent=16,
                                     bulletFontName="Helvetica-Bold", bulletFontSize=10))
        if table:
            rows = [r for r in table if not re.match(r"^\|[\s\-|]+\|$", r)]
            data = [[Paragraph(inline(c.strip()), S["cellb"] if i == 0 else S["cell"])
                     for c in r.strip("|").split("|")] for i, r in enumerate(rows)]
            t = Table(data, hAlign="LEFT", repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TEAL),
                                   ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D3D6")),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F5F6")]),
                                   ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
            flow.extend([t, Spacer(1, 10)])
        bullets, numbered, table = [], [], []

    for line in md.splitlines():
        s = line.rstrip()
        if s.startswith("|"):
            table.append(s)
            continue
        if s.startswith("- "):
            if numbered or table:
                flush()
            bullets.append(s[2:])
            continue
        m = re.match(r"^\d+\. (.*)", s)
        if m:
            if bullets or table:
                flush()
            numbered.append(m.group(1))
            continue
        flush()
        if not s:
            continue
        if s.startswith("# "):
            flow.append(Paragraph(inline(s[2:]), S["h1"]))
        elif s.startswith("## "):
            flow.append(KeepTogether([Paragraph(inline(s[3:]), S["h2"])]))
        elif s.startswith("### "):
            flow.append(Paragraph(inline(s[4:]), S["h3"]))
        elif s.startswith("> "):
            flow.append(Paragraph(inline(s[2:]), S["quote"]))
        else:
            flow.append(Paragraph(inline(s), S["p"]))
    flush()
    return flow


def decorate(title):
    def on_page(canvas, doc):
        canvas.saveState()
        w, h = LETTER
        canvas.setFillColor(TEAL)
        canvas.rect(0, h - 0.42 * inch, w, 0.42 * inch, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(0.75 * inch, h - 0.27 * inch, "Tidy")
        canvas.setFillColor(GOLD)
        canvas.drawString(0.75 * inch + canvas.stringWidth("Tidy", "Helvetica-Bold", 11), h - 0.27 * inch, "Margin")
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(w - 0.75 * inch, h - 0.27 * inch, title)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 8.5)
        canvas.drawString(0.75 * inch, 0.45 * inch, f"{brand.PRODUCT} - version {brand.VERSION}")
        canvas.drawRightString(w - 0.75 * inch, 0.45 * inch, f"Page {doc.page}")
        canvas.restoreState()
    return on_page


def render(md_path, pdf_path, title):
    doc = SimpleDocTemplate(str(pdf_path), pagesize=LETTER, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.85 * inch, bottomMargin=0.8 * inch, title=title, author=brand.NAME)
    doc.build(parse(Path(md_path).read_text()), onFirstPage=decorate(title), onLaterPages=decorate(title))
    return pdf_path


README = """TidyMargin - {tier}
====================================

Thank you for your purchase!

START HERE
1. Open TidyMargin-{tier}-EXAMPLE.xlsx to see the kit filled with a fictional business.
2. Use TidyMargin-{tier}.xlsx for your own business. Fill in the Settings sheet first.
3. Read TidyMargin-User-Guide.pdf (15 minutes).

GOOGLE SHEETS
Upload the .xlsx to Google Drive, open it, then File > Save as Google Sheets.

EXCEL
Excel 2019, 2021, Microsoft 365 or the free Excel for the web. No macros.

All default numbers are examples. Replace them with your own costs.
TidyMargin is a business-management tool, not accounting, tax or legal advice.

LICENSE: one business, any number of its own devices. Please do not resell or share.
SUPPORT: reply to your purchase email or use the contact link on the store page.
Version {version}
"""


def package():
    RELEASE.mkdir(parents=True, exist_ok=True)
    guide = GUIDES / "TidyMargin-User-Guide.pdf"
    playbook = GUIDES / "TidyMargin-Pricing-Playbook.pdf"
    made = []
    for tier in ("starter", "complete", "premium"):
        T = tier.title()
        z = RELEASE / f"TidyMargin-{T}.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in (f"TidyMargin-{T}.xlsx", f"TidyMargin-{T}-EXAMPLE.xlsx"):
                zf.write(ROOT / "products" / tier / f, f)
            zf.write(guide, guide.name)
            if tier == "premium":
                zf.write(playbook, playbook.name)
            zf.writestr("README.txt", README.format(tier=T, version=brand.VERSION))
        made.append(z)
    free = RELEASE / "TidyMargin-Quick-Price-Check-FREE.zip"
    with zipfile.ZipFile(free, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(ROOT / "products" / "free" / "TidyMargin-Quick-Price-Check-FREE.xlsx",
                 "TidyMargin-Quick-Price-Check-FREE.xlsx")
        zf.writestr("README.txt", "TidyMargin Quick Price Check (free)\n\nOpen the .xlsx in Excel or Google Sheets.\n"
                    "Yellow cells are yours. The full kit is on the TidyMargin store.\n")
    made.append(free)
    return made


def main():
    render(GUIDES / "user-guide.md", GUIDES / "TidyMargin-User-Guide.pdf", "User Guide")
    render(GUIDES / "pricing-playbook.md", GUIDES / "TidyMargin-Pricing-Playbook.pdf", "Pricing Playbook")
    for z in package():
        print("packaged", z, f"{z.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
