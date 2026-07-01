"""
70b_gen_manuscript_pdf.py — Generate proper PDF from Manuscript DOCX
Same approach: mammoth (DOCX→HTML) + Chrome headless (HTML→PDF).
"""
import mammoth
import subprocess
import os
import sys

BASE = r"C:\Users\KnightZ\Desktop\细胞受选择"
DOCX_PATH = os.path.join(BASE, "results", "NAR_Submission_Final", "manuscript", "CKI_NAR_Manuscript_Final.docx")
HTML_PATH = os.path.join(BASE, "results", "NAR_Submission_Final", "manuscript", "CKI_NAR_Manuscript_Final.html")
PDF_PATH = os.path.join(BASE, "results", "NAR_Submission_Final", "manuscript", "CKI_NAR_Manuscript_Final.pdf")

print("Step 1: Converting DOCX to HTML...")
with open(DOCX_PATH, "rb") as f:
    result = mammoth.convert_to_html(f)
html_body = result.value

html_full = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CKI NAR Manuscript</title>
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
  h1 {{ font-size: 14pt; font-weight: bold; margin-top: 24pt; margin-bottom: 12pt; }}
  h2 {{ font-size: 12pt; font-weight: bold; margin-top: 18pt; margin-bottom: 9pt; }}
  h3 {{ font-size: 11pt; font-weight: bold; margin-top: 14pt; margin-bottom: 7pt; }}
  p {{ margin: 6pt 0; }}
  table {{
    border-collapse: collapse; width: 100%; margin: 12pt 0;
    font-size: 8pt; page-break-inside: avoid;
  }}
  table th {{
    background-color: #f0f0f0; font-weight: bold; text-align: left;
    padding: 4px 6px; border: 1px solid #000000; font-size: 8pt;
  }}
  table td {{
    padding: 3px 6px; border: 1px solid #000000; font-size: 8pt; vertical-align: top;
  }}
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
print(f"  HTML saved: {len(html_full)} chars")

print("\nStep 2: HTML → PDF with Chrome headless...")
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), None)
if not chrome_exe:
    print("ERROR: Chrome/Edge not found!")
    sys.exit(1)

html_url = f"file:///{HTML_PATH.replace(chr(92), '/')}"
cmd = [chrome_exe, "--headless", "--disable-gpu", "--no-sandbox",
       "--print-to-pdf=" + PDF_PATH, "--no-pdf-header-footer", html_url]
subprocess.run(cmd, capture_output=True, text=True, timeout=60)

if os.path.exists(PDF_PATH):
    print(f"Done! PDF: {PDF_PATH} ({os.path.getsize(PDF_PATH)/1024:.0f} KB)")
else:
    print("ERROR: PDF not created!")
    sys.exit(1)
