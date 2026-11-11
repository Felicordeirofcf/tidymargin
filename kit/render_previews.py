"""Render authentic PNG screenshots of individual sheets (via LibreOffice -> PDF -> PNG).

Usage: python3 kit/render_previews.py
Writes brand/screenshots/<sheet>.png from the Premium EXAMPLE workbook.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import openpyxl
from openpyxl.worksheet.print_settings import PrintArea
import pypdfium2 as pdfium
from PIL import ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "products" / "premium" / "TidyMargin-Premium-EXAMPLE.xlsx"
OUT = ROOT / "brand" / "screenshots"
SHEETS = {
    "Price Calculator": "calculator", "Dashboard": "dashboard", "Monthly Summary": "summary",
    "Estimate": "estimate", "Invoice": "invoice", "Quote Table": "quotes", "Clients": "clients",
    "Schedule": "schedule", "Goal Planner": "goals", "Commercial Bid": "commercial",
    "Checklists": "checklists", "Margin vs Markup": "margin",
}
ROW_LIMIT = {"Clients": 14, "Schedule": 24, "Quote Table": 12}


def render(sheet, slug, tmp, scale=2.2, src=SRC):
    wb = openpyxl.load_workbook(src)
    for ws in wb:
        ws.sheet_state = "visible" if ws.title == sheet else "hidden"
        ws.sheet_view.tabSelected = ws.title == sheet
        if ws.title != sheet:
            ws._print_area = PrintArea()  # LibreOffice prints hidden sheets that have a print area
    ws = wb[sheet]
    wb.active = wb.sheetnames.index(sheet)
    if sheet in ROW_LIMIT:
        ws.print_area = f"A1:{openpyxl.utils.get_column_letter(ws.max_column)}{ROW_LIMIT[sheet]}"
        ws.page_setup.fitToHeight = 1
    x = tmp / f"{slug}.xlsx"
    wb.save(x)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(tmp), str(x)],
                   check=True, capture_output=True, timeout=180)
    pdf = pdfium.PdfDocument(str(tmp / f"{slug}.pdf"))
    img = pdf[0].render(scale=scale).to_pil().convert("RGB")
    # trim the white page margins, keep a small border
    bbox = ImageOps.invert(img).getbbox()
    if bbox:
        pad = 30
        img = img.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0),
                        min(bbox[2] + pad, img.width), min(bbox[3] + pad, img.height)))
    img.save(OUT / f"{slug}.png", optimize=True)
    return OUT / f"{slug}.png"


def main(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="tm-shots-"))
    try:
        for sheet, slug in SHEETS.items():
            if only and slug not in only:
                continue
            print("rendered", render(sheet, slug, tmp))
        if not only or "free" in only:
            free = ROOT / "products" / "free" / "TidyMargin-Quick-Price-Check-FREE.xlsx"
            print("rendered", render("Quick Price Check", "free", tmp, src=free))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
