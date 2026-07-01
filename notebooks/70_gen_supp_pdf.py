"""
70_gen_supp_pdf.py — Generate proper PDF from Supplementary DOCX
Uses mammoth (DOCX→HTML) + Chrome headless (HTML→PDF).
"""
import mammoth
import subprocess
import os
import sys

BASE = r"C:\Users\KnightZ\Desktop\细胞受选择"
DOCX_PATH = os.path.join(BASE, "results", "NAR_Submission_Final", "supplementary", "CKI_NAR_Supplementary.docx")
HTML_PATH = os.path.join(BASE, "results", "NAR_Submission_Final", "supplementary", "CKI_NAR_Supplementary.html")
PDF_PATH = os.path.join(BASE, "results", "NAR_Submission_Final", "supplementary", "CKI_NAR_Supplementary.pdf")

# Step 1: Convert DOCX to HTML using mammoth
print("Step 1: Converting DOCX to HTML with mammoth...")
with open(DOCX_PATH, "rb") as f:
    result = mammoth.convert_to_html(f)
html_body = result.value

if result.messages:
    for msg in result.messages:
        print(f"  [mammoth] {msg}")

# Step 2: Wrap in full HTML with NAR styling
html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CKI NAR Supplementary Materials</title>
<style>
  @page {{
    size: A4;
    margin: 25mm 20mm 25mm 20mm;
  }}
  body {{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 10pt;
    color: #000000;
    line-height: 1.5;
    max-width: 170mm;
    margin: 0 auto;
    padding: 20px;
  }}
  h1 {{
    font-size: 14pt;
    font-weight: bold;
    margin-top: 24pt;
    margin-bottom: 12pt;
    page-break-after: avoid;
  }}
  h2 {{
    font-size: 12pt;
    font-weight: bold;
    margin-top: 18pt;
    margin-bottom: 9pt;
    page-break-after: avoid;
  }}
  p {{
    margin: 6pt 0;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 12pt 0;
    font-size: 8pt;
    page-break-inside: avoid;
  }}
  table th {{
    background-color: #f0f0f0;
    font-weight: bold;
    text-align: left;
    padding: 4px 6px;
    border: 1px solid #000000;
    font-size: 8pt;
  }}
  table td {{
    padding: 3px 6px;
    border: 1px solid #000000;
    font-size: 8pt;
    vertical-align: top;
  }}
  .superscript {{ vertical-align: super; font-size: 0.75em; }}
  .subscript {{ vertical-align: sub; font-size: 0.75em; }}
  strong {{ font-weight: bold; }}
  em {{ font-style: italic; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_full)
print(f"  HTML saved: {HTML_PATH} ({len(html_full)} chars)")

# Step 3: Use Chrome headless to print HTML to PDF
print("\nStep 2: Converting HTML to PDF with Chrome headless...")

# Find Chrome or Edge
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
chrome_exe = None
for p in chrome_paths:
    if os.path.exists(p):
        chrome_exe = p
        break

if not chrome_exe:
    print("ERROR: Chrome/Edge not found!")
    sys.exit(1)

print(f"  Using: {chrome_exe}")

# Use file:// URL
html_url = f"file:///{HTML_PATH.replace(chr(92), '/')}"

cmd = [
    chrome_exe,
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--print-to-pdf=" + PDF_PATH,
    "--print-to-pdf-no-header",
    "--no-pdf-header-footer",
    html_url
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
print(f"  Chrome exit code: {result.returncode}")
if result.stderr:
    # Only show non-info stderr lines
    errors = [l for l in result.stderr.split('\n') if 'ERROR' in l or 'error' in l]
    if errors:
        for e in errors[:5]:
            print(f"  [stderr] {e}")

# Verify
if os.path.exists(PDF_PATH):
    size_kb = os.path.getsize(PDF_PATH) / 1024
    print(f"\nDone! PDF saved: {PDF_PATH} ({size_kb:.0f} KB)")
else:
    print(f"\nERROR: PDF not created at {PDF_PATH}")
    sys.exit(1)
