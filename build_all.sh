#!/usr/bin/env bash
# Rebuild every deliverable from source and run all tests.
# Requires: python3 + openpyxl + reportlab + pypdfium2 + pillow, LibreOffice (soffice), node + playwright (Chromium).
set -euo pipefail
cd "$(dirname "$0")"
python3 kit/build_workbooks.py          # products/<tier>/*.xlsx
python3 kit/render_previews.py          # brand/screenshots (authentic)
python3 kit/make_brand_assets.py        # brand/src/*.html + manifest
node brand/render.cjs                   # brand/covers, brand/social, brand/logo PNGs
python3 kit/make_guides.py              # PDFs + products/release/*.zip
python3 marketing/calendar_data.py      # marketing calendar
python3 kit/build_site.py               # website/dist
python3 -m unittest discover -s tests -v
node tests/site_check.cjs
