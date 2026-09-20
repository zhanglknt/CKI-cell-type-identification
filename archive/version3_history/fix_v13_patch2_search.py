"""
v13 patch 2: Fix remaining issues
- 'danalysis' (curly apostrophe issue)
- Supplementary FPKM and TCGA sample numbers not fully caught
"""
import zipfile, io, os, shutil
from docx import Document

ZIP_PATH = "version3/CKI_NAR_Submission_v13.zip"
OUT_ZIP = "version3/CKI_NAR_Submission_v13.zip"  # overwrite
WORK_DIR = "version3/v13_work2"

if os.path.exists(WORK_DIR):
    shutil.rmtree(WORK_DIR)
os.makedirs(WORK_DIR, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    z.extractall(WORK_DIR)

# Find DOCX files
manuscript_path = None
supplementary_path = None
for root, dirs, files in os.walk(WORK_DIR):
    for f in files:
        if f.endswith('.docx') and 'Manuscript' in f:
            manuscript_path = os.path.join(root, f)
        elif f.endswith('.docx') and 'Supplementary' in f:
            supplementary_path = os.path.join(root, f)

print("=== MANUSCRIPT: Searching for danalysis ===")
doc = Document(manuscript_path)
for i, p in enumerate(doc.paragraphs):
    if "danalysis" in p.text or "d analysis" in p.text.lower():
        print(f"  P{i+1:03d}: {p.text[:200]}")
        # Show runs
        for j, r in enumerate(p.runs):
            if "d" in r.text and "analysis" in r.text:
                print(f"    Run {j}: '{r.text}'")
            elif "danalysis" in r.text:
                print(f"    Run {j}: '{r.text}'")

    # Also check for curly apostrophe variants
    if "Cohen" in p.text and "analysis" in p.text.lower():
        print(f"  P{i+1:03d} Cohen+analysis: {p.text[:200]}")
        for j, r in enumerate(p.runs):
            if "Cohen" in r.text or "analysis" in r.text or "dan" in r.text:
                print(f"    Run {j}: '{r.text}'")

print("\n=== SUPPLEMENTARY: Searching for FPKM and TCGA samples ===")
doc2 = Document(supplementary_path)
for i, p in enumerate(doc2.paragraphs):
    if "FPKM" in p.text:
        print(f"\n  SupP{i:03d} FPKM found:")
        print(f"    Text snippet: ...{p.text[max(0,p.text.index('FPKM')-50):p.text.index('FPKM')+100]}...")
    if "10,535" in p.text or "10535" in p.text:
        print(f"\n  SupP{i:03d} 10,535 found: {p.text[:200]}")
    # Search for the wrong sample numbers
    for pattern in ["515", "501", "371", "533", "1093", "59 normal", "51 normal", "50 normal", "72 normal", "113 normal"]:
        if pattern in p.text:
            idx = p.text.index(pattern)
            print(f"\n  SupP{i:03d} '{pattern}' found: ...{p.text[max(0,idx-40):idx+60]}...")
