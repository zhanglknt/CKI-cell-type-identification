"""
v12 -> v13 fix script
Based on code audit ground truth, fix both Manuscript and Supplementary DOCX.

Ground truth from code:
1. JS log base: BASE-2 (np.log2) — main text WRONG (says natural), supplementary CORRECT
2. Normalization: SOFTMAX for all data — main text WRONG (says sum-norm for sc), supplementary CORRECT
3. TCGA: TPM from UCSC Xena, NOT FPKM from GDC — main text CORRECT, supplementary WRONG
4. TCGA samples: 3,596 total — main text CORRECT, supplementary WRONG (3,358/10,535)
5. Bootstrap: mouse=500, human/brain=1000, TCGA=100/1000 — main text says 500 everywhere (WRONG)
6. HVG flavor: 'seurat' — main text says 'seurat_v3' in some places (WRONG)
7. Grammar: P056 broken sentence, P057 missing space, P054 missing space
"""
import zipfile, io, os, shutil, re
from docx import Document

ZIP_PATH = "version3/CKI_NAR_Submission_v12.zip"
OUT_ZIP = "version3/CKI_NAR_Submission_v13.zip"
WORK_DIR = "version3/v13_work"

# --- Step 1: Extract ---
if os.path.exists(WORK_DIR):
    shutil.rmtree(WORK_DIR)
os.makedirs(WORK_DIR, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, 'r') as z:
    z.extractall(WORK_DIR)

# Find the DOCX files
manuscript_path = None
supplementary_path = None
for root, dirs, files in os.walk(WORK_DIR):
    for f in files:
        if f.endswith('.docx') and 'Manuscript' in f:
            manuscript_path = os.path.join(root, f)
        elif f.endswith('.docx') and 'Supplementary' in f:
            supplementary_path = os.path.join(root, f)

print(f"Manuscript: {manuscript_path}")
print(f"Supplementary: {supplementary_path}")

# --- Step 2: Fix Manuscript ---
doc = Document(manuscript_path)
fixes_log = []

for i, para in enumerate(doc.paragraphs):
    text = para.text
    original = text
    changed = False

    # Fix 1: JS log base — "natural logarithm" -> "base-2 logarithm"
    if "JS divergence uses the natural logarithm" in text:
        text = text.replace(
            "JS divergence uses the natural logarithm",
            "JS divergence uses base-2 logarithm"
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: JS log base natural->base-2")

    # Fix 2: Normalization — remove sum-normalization, use softmax for all
    if "norm is sum-normalization for non-negative single-cell data (softmax only for TCGA bulk RNA-seq)" in text:
        text = text.replace(
            "norm is sum-normalization for non-negative single-cell data (softmax only for TCGA bulk RNA-seq)",
            "norm is softmax normalization for all data types"
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: normalization sum-norm->softmax")

    if "Sum-normalization converts expression vectors to probability distributions for non-negative single-cell data; softmax normalization is used only for TCGA bulk RNA-seq data where negative values may occur from log-transformation." in text:
        text = text.replace(
            "Sum-normalization converts expression vectors to probability distributions for non-negative single-cell data; softmax normalization is used only for TCGA bulk RNA-seq data where negative values may occur from log-transformation.",
            "Softmax normalization converts expression vectors into probability distributions for all data types."
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: normalization description unified to softmax")

    # Fix 3: HVG flavor — "Seurat v3 flavor" -> "Seurat flavor"
    if "Seurat v3 flavor" in text:
        text = text.replace("Seurat v3 flavor", "Seurat flavor")
        changed = True
        fixes_log.append(f"P{i+1:03d}: HVG flavor seurat_v3->seurat")

    if "flavor='seurat_v3'" in text:
        text = text.replace("flavor='seurat_v3'", "flavor='seurat'")
        changed = True
        fixes_log.append(f"P{i+1:03d}: HVG flavor code seurat_v3->seurat")

    # Fix 4: Bootstrap B values
    if "B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration" in text:
        text = text.replace(
            "B = 500 for mouse calibration and exploratory analyses; B = 500 for mouse calibration",
            "B = 500 for mouse calibration; B = 1,000 for human, TCGA, and brain analyses"
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: Bootstrap B redundancy fixed + B=1000 for primary")

    if "bootstrap permutation testing (B = 500) was used to assess statistical significance" in text:
        text = text.replace(
            "bootstrap permutation testing (B = 500) was used to assess statistical significance",
            "bootstrap permutation testing (B = 500 for mouse calibration; B = 1,000 for primary analyses) was used to assess statistical significance"
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: Bootstrap B clarified (P023)")

    if "Bootstrap inference uses B = 500 permutations" in text:
        text = text.replace(
            "Bootstrap inference uses B = 500 permutations",
            "Bootstrap inference uses B = 1,000 permutations for primary analyses (B = 500 for mouse calibration)"
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: Bootstrap B P038 fixed")

    if "bootstrap permutation testing (B = 500)" in text:
        text = text.replace(
            "bootstrap permutation testing (B = 500)",
            "bootstrap permutation testing (B = 1,000 for primary analyses; B = 500 for mouse calibration)"
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: Bootstrap B P044 fixed")

    if "Bootstrap inference uses B = 500 for mouse calibration" in text:
        text = text.replace(
            "Bootstrap inference uses B = 500 for mouse calibration",
            "Bootstrap inference uses B = 500 for mouse calibration and B = 1,000 for primary analyses"
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: Bootstrap B P044 second instance fixed")

    # Fix 5: Grammar — P056 "we applied per-cancer P-values are reported"
    if "we applied per-cancer P-values are reported" in text:
        text = text.replace(
            "we applied per-cancer P-values are reported",
            "per-cancer P-values are reported"
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: P056 grammar fixed")

    # Fix 6: Remove orphaned fragment
    if "ω magnitudes, which are not directly comparable to single-cell-derived ω values." in text:
        text = text.replace(
            " ω magnitudes, which are not directly comparable to single-cell-derived ω values.",
            ""
        )
        changed = True
        fixes_log.append(f"P{i+1:03d}: P056 orphaned fragment removed")

    # Fix 7: "Cohen's danalysis" -> "Cohen's d analysis"
    if "Cohen's danalysis" in text:
        text = text.replace("Cohen's danalysis", "Cohen's d analysis")
        changed = True
        fixes_log.append(f"P{i+1:03d}: P057 danalysis->d analysis")

    # Fix 8: P054 missing space after (Fig. 3C)
    if "(Fig. 3C)Although" in text:
        text = text.replace("(Fig. 3C)Although", "(Fig. 3C) Although")
        changed = True
        fixes_log.append(f"P{i+1:03d}: P054 missing space after Fig 3C")

    # Fix 9: Double space
    if "without multiple testing.  The empirical" in text:
        text = text.replace("without multiple testing.  The empirical", "without multiple testing. The empirical")
        changed = True
        fixes_log.append(f"P{i+1:03d}: P044 double space fixed")

    if changed:
        # Replace all runs' text with the new text, preserving first run's formatting
        if para.runs:
            para.runs[0].text = text
            for run in para.runs[1:]:
                run.text = ""
        else:
            para.text = text

print(f"\n--- Manuscript fixes: {len(fixes_log)} ---")
for f in fixes_log:
    print(f"  {f}")

doc.save(manuscript_path)
print(f"\nManuscript saved: {manuscript_path}")

# --- Step 3: Fix Supplementary ---
doc2 = Document(supplementary_path)
supp_fixes = []

for i, para in enumerate(doc2.paragraphs):
    text = para.text
    original = text
    changed = False

    # Fix: FPKM -> TPM in TCGA context
    if "FPKM values from GDC" in text:
        text = text.replace("FPKM values from GDC", "RSEM gene TPM from UCSC Xena")
        changed = True
        supp_fixes.append(f"SupP{i:03d}: FPKM->TPM (GDC->UCSC Xena)")

    if "FPKM normalization is used instead" in text:
        text = text.replace("FPKM normalization is used instead", "TPM normalization (UCSC Xena RSEM gene TPM) is used instead")
        changed = True
        supp_fixes.append(f"SupP{i:03d}: FPKM normalization->TPM")

    if "FPKM values" in text and "TCGA" in text:
        text = text.replace("FPKM values", "TPM values")
        changed = True
        supp_fixes.append(f"SupP{i:03d}: FPKM values->TPM values")

    # Fix: TCGA sample numbers — replace ALL wrong numbers
    # Wrong: LUAD 515+59, LUSC 501+51, LIHC 371+50, KIRC 533+72, BRCA 1093+113
    # Right: LUAD 495+76, LUSC 567+58, LIHC 365+57, KIRC 755+82, BRCA 1032+109
    replacements = [
        ("LUAD: 515 tumor + 59 normal", "LUAD: 495 tumor + 76 normal"),
        ("LUSC: 501 tumor + 51 normal", "LUSC: 567 tumor + 58 normal"),
        ("LIHC: 371 tumor + 50 normal", "LIHC: 365 tumor + 57 normal"),
        ("KIRC: 533 tumor + 72 normal", "KIRC: 755 tumor + 82 normal"),
        ("BRCA: 1093 tumor + 113 normal", "BRCA: 1032 tumor + 109 normal"),
        ("515 tumor + 59 normal", "495 tumor + 76 normal"),
        ("501 tumor + 51 normal", "567 tumor + 58 normal"),
        ("371 tumor + 50 normal", "365 tumor + 57 normal"),
        ("533 tumor + 72 normal", "755 tumor + 82 normal"),
        ("1093 tumor + 113 normal", "1032 tumor + 109 normal"),
        ("totaling n = 10,535 samples", "totalling 3,596 samples"),
        ("totaling n=10,535 samples", "totalling 3,596 samples"),
        ("n = 10,535", "n = 3,596"),
        ("n=10,535", "n = 3,596"),
        ("10,535 samples", "3,596 samples"),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed = True
            supp_fixes.append(f"SupP{i:03d}: TCGA samples {old}->{new}")

    if changed:
        if para.runs:
            para.runs[0].text = text
            for run in para.runs[1:]:
                run.text = ""
        else:
            para.text = text

print(f"\n--- Supplementary fixes: {len(supp_fixes)} ---")
for f in supp_fixes:
    print(f"  {f}")

doc2.save(supplementary_path)
print(f"\nSupplementary saved: {supplementary_path}")

# --- Step 4: Repack to v13 zip ---
# Copy the zip structure
with zipfile.ZipFile(ZIP_PATH, 'r') as zin:
    with zipfile.ZipFile(OUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            file_path = os.path.join(WORK_DIR, item.filename)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    zout.writestr(item, f.read())
            else:
                # Directory entry
                zout.writestr(item, b'')

print(f"\n=== v13 zip created: {OUT_ZIP} ===")
print(f"Size: {os.path.getsize(OUT_ZIP) / 1024 / 1024:.1f} MB")

# --- Step 5: Verify ---
with zipfile.ZipFile(OUT_ZIP, 'r') as z:
    names = z.namelist()
    print(f"\nFiles in v13: {len(names)}")
    for n in sorted(names):
        info = z.getinfo(n)
        print(f"  {n} ({info.file_size / 1024:.1f} KB)")

# --- Step 6: Quick text verification ---
with zipfile.ZipFile(OUT_ZIP, 'r') as z:
    # Check manuscript
    mname = [n for n in z.namelist() if 'Manuscript' in n and n.endswith('.docx')][0]
    with z.open(mname) as f:
        mdoc = Document(io.BytesIO(f.read()))
    
    for i, p in enumerate(mdoc.paragraphs):
        if "natural logarithm" in p.text:
            print(f"\nWARNING: 'natural logarithm' still in P{i+1:03d}")
        if "sum-normalization" in p.text and "softmax" not in p.text.lower():
            print(f"\nWARNING: 'sum-normalization' still in P{i+1:03d} without softmax")
        if "seurat_v3" in p.text.lower():
            print(f"\nWARNING: 'seurat_v3' still in P{i+1:03d}")
        if "danalysis" in p.text:
            print(f"\nWARNING: 'danalysis' still in P{i+1:03d}")
        if "(Fig. 3C)Although" in p.text:
            print(f"\nWARNING: '(Fig. 3C)Although' still in P{i+1:03d}")
    
    # Check supplementary
    sname = [n for n in z.namelist() if 'Supplementary' in n and n.endswith('.docx')][0]
    with z.open(sname) as f:
        sdoc = Document(io.BytesIO(f.read()))
    
    for i, p in enumerate(sdoc.paragraphs):
        if "FPKM" in p.text and "TCGA" in p.text:
            print(f"\nWARNING: 'FPKM' still in SupP{i:03d} with TCGA context")
        if "10,535" in p.text:
            print(f"\nWARNING: '10,535' still in SupP{i:03d}")
    
    print("\n=== Verification complete ===")

# Clean up
shutil.rmtree(WORK_DIR)
print("\nWork directory cleaned up.")
