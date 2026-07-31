#!/usr/bin/env python3
"""Build CKI NAR Submission Package v17 — simplified (no directory deletion).

Uses the existing extracted v16 directory (leftover from previous run),
overwrites the three DOCX files, writes manifest, creates ZIP.
"""

import os
import shutil
import zipfile
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION3_DIR = os.path.join(BASE_DIR, "version3")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

V17_ZIP = os.path.join(VERSION3_DIR, "CKI_NAR_Submission_v17.zip")

# Use the existing extracted directory (from previous run)
WORK_DIR = os.path.join(VERSION3_DIR, "CKI_NAR_Submission_v17")

# Files to replace with freshly generated versions
REPLACEMENTS = {
    "CKI_NAR_Manuscript.docx": os.path.join(RESULTS_DIR, "CKI_NAR_Manuscript.docx"),
    "CKI_NAR_Supplementary.docx": os.path.join(RESULTS_DIR, "CKI_NAR_Supplementary.docx"),
    "CKI_NAR_Reproducibility_Guide.docx": os.path.join(RESULTS_DIR, "CKI_Reproducibility_Guide.docx"),
}


def build_v17():
    # Verify work directory exists
    if not os.path.isdir(WORK_DIR):
        print(f"ERROR: Work directory not found: {WORK_DIR}")
        print("Extracting from v16 zip...")
        with zipfile.ZipFile(os.path.join(VERSION3_DIR, "CKI_NAR_Submission_v16.zip"), "r") as zf:
            zf.extractall(VERSION3_DIR)
        # Try renaming
        old = os.path.join(VERSION3_DIR, "CKI_NAR_Submission_v16")
        if os.path.isdir(old):
            os.rename(old, WORK_DIR)

    # 1. Replace the three DOCX files (shutil.copy2 overwrites destination)
    print("Replacing DOCX files:")
    for dest_name, src_path in REPLACEMENTS.items():
        dest = os.path.join(WORK_DIR, dest_name)
        shutil.copy2(src_path, dest)
        size_kb = os.path.getsize(dest) / 1024
        print(f"  {dest_name} ({size_kb:.1f} KB)")

    # 2. Write updated manifest
    manifest_path = os.path.join(WORK_DIR, "MANIFEST_v17.txt")
    manifest_content = f"""CKI NAR Submission Package v17
Built: {datetime.now().strftime('%Y-%m-%d')}

This package updates v16 with three DOCX files regenerated after
code-ground-truth verification (Task #631). All numerical parameters
and method descriptions now match the actual CKI source code.

Contents:
1. CKI_NAR_Manuscript.docx - Main manuscript (English, regenerated)
2. CKI_NAR_Supplementary.docx - Supplementary materials (English, regenerated)
3. CKI_NAR_Cover_Letter.docx - Cover letter with 6 suggested reviewers
4. CKI_NAR_Reproducibility_Guide.docx - Computational reproducibility guide (regenerated)
5. Table1-2.docx - Standalone tables extracted from manuscript
6. figure1.pdf through figure6.pdf - Main figures
7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S5.pdf - Supplementary figures
8. CKI_graphical_abstract.png/pdf/svg - Graphical Abstract (300 DPI, NAR-compliant)

Key fixes in v17 (code-ground-truth alignment):

Manuscript (generate_manuscript_nar.py, ~15 edits):
- P-value formula: 2x min(two-sided) -> absolute deviation from omega=1
- "descriptive statistics only" -> "non-parametric tests and descriptive statistics"
- "proving/proves" -> "supporting/supports" (hedge language)
- Brain region count: ~100 -> 108
- Brain normalization: softmax -> normalize_total + log1p (pseudobulk level)
- Removed non-existent reference (Wang et al. 2024)
- Panel labels: (A)/(B)/(C) -> (A), (B), (C) per NAR format (13 fixes)

Supplementary (68_gen_supplementary_en.py, 11 edits):
- SN1.5 P-value formula corrected (absolute deviation from omega=1)
- Algorithm 1 pseudocode P-value line corrected
- "descriptive statistics only" -> "non-parametric tests and descriptive statistics" (3 fixes)
- SN3.2 P-value formula corrected
- SN3.3 TS pairs 4,851 -> 5,151; TS cell types 99 -> 102 (3 fixes)
- QC threshold <200 -> <500 detected genes
- Reporting Conventions: bootstrap P-value declaration clarified

Reproducibility Guide (100_gen_reproducibility_docx.js, ~20 edits):
- HK genes: "pre-specified file" -> "auto-detected (combined criterion)"
- HK genes: use_reference=False (data-driven), HRT Atlas available
- P-value: "two-sided" -> "absolute deviation from omega=1"
- TS pairs: 4,851 -> 5,151 (complete omega matrix)
- TCGA clinical strata sample counts corrected (LIHC/BRCA/LUAD)
- Brain regions: ~100 -> 108
- Brain normalization: softmax -> normalize_total + log1p
- Strong criterion: removed "pair median omega > 20"
- Bootstrap B values: 500 mouse, 1000 human, 100 TCGA, 100 brain
- HVG flavor: "Seurat v3" -> "seurat flavor"
- Mouse k_f: "per-pair top-200 DE" -> "global HVG 2,000"
- Parameter Summary table updated (HK + Bootstrap + HVG rows)
- Checklist updated to match all parameter corrections
"""
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest_content)
    print(f"  Wrote MANIFEST_v17.txt")

    # 3. Create ZIP
    print(f"\nCreating {V17_ZIP}")
    with zipfile.ZipFile(V17_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORK_DIR):
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                arcname = os.path.join("CKI_NAR_Submission_v17", os.path.relpath(fpath, WORK_DIR))
                zf.write(fpath, arcname)

    # 4. Verify
    zip_size_mb = os.path.getsize(V17_ZIP) / (1024 * 1024)
    print(f"\n=== v17 Package Built ===")
    print(f"ZIP: {V17_ZIP}")
    print(f"Size: {zip_size_mb:.1f} MB")

    with zipfile.ZipFile(V17_ZIP, "r") as zf:
        infos = sorted(zf.infolist(), key=lambda x: x.filename)
        print(f"Files: {len(infos)}")
        for info in infos:
            print(f"  {info.file_size:>10,}  {info.filename}")

    # 5. Quick sanity check: verify the three replaced files have new timestamps
    print("\n=== Sanity Check ===")
    for dest_name in REPLACEMENTS:
        dest = os.path.join(WORK_DIR, dest_name)
        mtime = datetime.fromtimestamp(os.path.getmtime(dest))
        size_kb = os.path.getsize(dest) / 1024
        print(f"  {dest_name}: {size_kb:.1f} KB, modified {mtime:%Y-%m-%d %H:%M}")


if __name__ == "__main__":
    build_v17()
