"""
v13 patch 2: Fix remaining issues
- 'danalysis' (curly apostrophe U+2019, search for 'danalysis' directly)
- Supplementary TCGA sample numbers in format "LUSC (501 + 51)" etc.
"""
import zipfile, io, os, shutil
from docx import Document

ZIP_PATH = "version3/CKI_NAR_Submission_v13.zip"
WORK_DIR = "version3/v13_work2"

if os.path.exists(WORK_DIR):
    shutil.rmtree(WORK_DIR)
os.makedirs(WORK_DIR, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    z.extractall(WORK_DIR)

manuscript_path = None
supplementary_path = None
for root, dirs, files in os.walk(WORK_DIR):
    for f in files:
        if f.endswith('.docx') and 'Manuscript' in f:
            manuscript_path = os.path.join(root, f)
        elif f.endswith('.docx') and 'Supplementary' in f:
            supplementary_path = os.path.join(root, f)

fixes = []

# --- Fix Manuscript: danalysis ---
doc = Document(manuscript_path)
for i, p in enumerate(doc.paragraphs):
    text = p.text
    if "danalysis" in text:
        # Replace directly
        new_text = text.replace("danalysis", "d analysis")
        # Put in first run, clear rest
        if p.runs:
            p.runs[0].text = new_text
            for r in p.runs[1:]:
                r.text = ""
        fixes.append(f"Manuscript P{i+1:03d}: danalysis -> d analysis")
        print(f"Fixed P{i+1:03d}: danalysis -> d analysis")
        print(f"  Before: ...{text[text.index('danalysis')-20:text.index('danalysis')+30]}...")
        print(f"  After:  ...{new_text[new_text.index('d analysis')-20:new_text.index('d analysis')+31]}...")

doc.save(manuscript_path)

# --- Fix Supplementary: TCGA sample numbers ---
doc2 = Document(supplementary_path)
for i, p in enumerate(doc2.paragraphs):
    text = p.text
    original = text
    changed = False

    # Fix remaining TCGA sample numbers in format "LUSC (501 + 51)" etc.
    replacements = [
        ("LUSC (501 + 51)", "LUSC (567 + 58)"),
        ("LIHC (371 + 50)", "LIHC (365 + 57)"),
        ("KIRC (533 + 72)", "KIRC (755 + 82)"),
        ("BRCA (1,093 + 113)", "BRCA (1,032 + 109)"),
        ("BRCA (1093 + 113)", "BRCA (1032 + 109)"),
        # Also check for other formats
        ("501 + 51", "567 + 58"),
        ("371 + 50", "365 + 57"),
        ("533 + 72", "755 + 82"),
        ("1,093 + 113", "1,032 + 109"),
        ("1093 + 113", "1032 + 109"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed = True
            fixes.append(f"Supplementary P{i:03d}: {old} -> {new}")
            print(f"Fixed SupP{i:03d}: {old} -> {new}")

    if changed:
        if p.runs:
            p.runs[0].text = text
            for r in p.runs[1:]:
                r.text = ""
        else:
            p.text = text

doc2.save(supplementary_path)

# --- Repack ---
OUT_ZIP = "version3/CKI_NAR_Submission_v13.zip"
with zipfile.ZipFile(ZIP_PATH, 'r') as zin:
    with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            file_path = os.path.join(WORK_DIR, item.filename)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    zout.writestr(item, f.read())

print(f"\n=== Total fixes in patch 2: {len(fixes)} ===")
for f in fixes:
    print(f"  {f}")

# --- Verify ---
with zipfile.ZipFile(OUT_ZIP, 'r') as z:
    mname = [n for n in z.namelist() if 'Manuscript' in n and n.endswith('.docx')][0]
    with z.open(mname) as f:
        mdoc = Document(io.BytesIO(f.read()))
    for i, p in enumerate(mdoc.paragraphs):
        if "danalysis" in p.text:
            print(f"\nWARNING: 'danalysis' STILL in P{i+1:03d}")
        if "d analysis" in p.text and "Cohen" in p.text:
            print(f"  OK: 'd analysis' confirmed in P{i+1:03d}")

    sname = [n for n in z.namelist() if 'Supplementary' in n and n.endswith('.docx')][0]
    with z.open(sname) as f:
        sdoc = Document(io.BytesIO(f.read()))
    for i, p in enumerate(sdoc.paragraphs):
        for wrong in ["501 + 51", "371 + 50", "533 + 72", "1,093 + 113", "1093 + 113"]:
            if wrong in p.text:
                print(f"\nWARNING: '{wrong}' STILL in SupP{i:03d}")
        if "3,596" in p.text:
            print(f"  OK: '3,596' confirmed in SupP{i:03d}")

print(f"\n=== v13 zip updated: {OUT_ZIP} ===")
print(f"Size: {os.path.getsize(OUT_ZIP) / 1024 / 1024:.1f} MB")

shutil.rmtree(WORK_DIR)
