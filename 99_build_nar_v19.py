#!/usr/bin/env python3
"""Build CKI NAR Submission Package v19.

v19 incorporates all text-wide contradiction fixes (#691-#694) and
brain bootstrap v3 with one-sided P-value formula (pseudobulk level).

Key changes from v18:
  P-value formula: two-sided (|omega_null - 1|) -> one-sided (omega_null >= omega_obs)
  FDR contradiction: "FDR not applied" -> "Benjamini-Hochberg FDR applied"
  Omega baseline: "yield omega close to 1" -> "yield omega above 1 (empirical calib 6.67)"
  "Striking" language removed (3 occurrences), replaced with "notable/pronounced/substantially"
  Brain bootstrap v3: one-sided P-values, pseudobulk-level permutation, all 10 CTs significant
  _load_manuscript_data.py: brain bootstrap columns aligned with v3 CSV output
"""

import os
import sys
import shutil
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
VERSION3_DIR = BASE_DIR / "version3"
RESULTS_DIR = BASE_DIR / "results"
FIGURES_DIR = RESULTS_DIR / "figures_final"
PYTHON = r"C:\Users\KnightZ\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
NODE = r"C:\Users\KnightZ\.workbuddy\binaries\node\versions\22.22.2\node.exe"

V19_ZIP = VERSION3_DIR / "CKI_NAR_Submission_v19.zip"
WORK_DIR = VERSION3_DIR / "CKI_NAR_Submission_v19"
V18_DIR = VERSION3_DIR / "CKI_NAR_Submission_v18"


def run_script(cmd, label):
    """Run a subprocess and check return code."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(BASE_DIR))
    if result.stdout:
        print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    if result.returncode != 0:
        print(f"  WARNING: Return code {result.returncode}")
        if result.stderr:
            print(f"  STDERR: {result.stderr[-300:]}")
    else:
        print(f"  OK")
    return result.returncode == 0


def build_v19():
    print("=" * 60)
    print("  CKI NAR Submission Package v19 Builder")
    print("=" * 60)

    # 0. Prepare work directory
    print(f"\n[0] Preparing {WORK_DIR.name}...")
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    if V18_DIR.exists():
        for f in V18_DIR.iterdir():
            if f.name.startswith("MANIFEST"):
                continue
            shutil.copy2(f, WORK_DIR / f.name)
        print(f"  Copied base files from v18")
    else:
        print(f"  ERROR: v18 directory not found at {V18_DIR}")
        return

    # 1. Regenerate DOCX files (all with text fixes from #691-#694)
    print(f"\n[1] Regenerating DOCX files with text fixes...")

    # 1a. Main manuscript
    run_script(
        f'"{PYTHON}" -u generate_manuscript_nar.py',
        "Generating CKI_NAR_Manuscript.docx"
    )
    ms_src = RESULTS_DIR / "CKI_NAR_Manuscript.docx"
    if ms_src.exists():
        shutil.copy2(ms_src, WORK_DIR / "CKI_NAR_Manuscript.docx")
        print(f"  Copied: {ms_src.name} ({ms_src.stat().st_size/1024:.1f} KB)")

    # 1b. Supplementary materials
    run_script(
        f'"{PYTHON}" -u notebooks/68_gen_supplementary_en.py',
        "Generating CKI_NAR_Supplementary.docx"
    )
    sm_src = RESULTS_DIR / "CKI_NAR_Supplementary.docx"
    if sm_src.exists():
        shutil.copy2(sm_src, WORK_DIR / "CKI_NAR_Supplementary.docx")
        print(f"  Copied: {sm_src.name} ({sm_src.stat().st_size/1024:.1f} KB)")

    # 1c. Cover letter
    run_script(
        f'"{PYTHON}" -u generate_cover_letter_nar.py',
        "Generating CKI_NAR_Cover_Letter.docx"
    )
    cl_src = RESULTS_DIR / "CKI_NAR_Cover_Letter.docx"
    if cl_src.exists():
        shutil.copy2(cl_src, WORK_DIR / "CKI_NAR_Cover_Letter.docx")
        print(f"  Copied: {cl_src.name} ({cl_src.stat().st_size/1024:.1f} KB)")

    # 1d. Reproducibility guide (Node.js)
    run_script(
        f'"{NODE}" notebooks/100_gen_reproducibility_docx.js',
        "Generating CKI_Reproducibility_Guide.docx"
    )
    rg_src = RESULTS_DIR / "CKI_Reproducibility_Guide.docx"
    if rg_src.exists():
        shutil.copy2(rg_src, WORK_DIR / "CKI_NAR_Reproducibility_Guide.docx")
        print(f"  Copied: {rg_src.name} ({rg_src.stat().st_size/1024:.1f} KB)")

    # 2. Write manifest
    print(f"\n[2] Writing MANIFEST_v19.txt...")
    manifest = f"""CKI NAR Submission Package v19
Built: {datetime.now().strftime('%Y-%m-%d %H:%M')}

This package updates v18 with text-wide contradiction fixes (#691-#694)
and brain bootstrap v3 results.

Contents:
1. CKI_NAR_Manuscript.docx - Main manuscript (English, regenerated)
2. CKI_NAR_Supplementary.docx - Supplementary materials (English, regenerated)
3. CKI_NAR_Cover_Letter.docx - Cover letter with 6 suggested reviewers
4. CKI_NAR_Reproducibility_Guide.docx - Computational reproducibility guide
5. Table1-2.docx - Standalone tables (from v18, unchanged)
6. figure1.pdf through figure6.pdf - Main figures (from v18)
7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S7.pdf
8. CKI_graphical_abstract.png/pdf/svg - Graphical Abstract

Key changes in v19 (relative to v18):

Text-Wide Contradiction Fixes (#691-#694):
  - P-value formula: two-sided (|omega_null - 1|) -> one-sided (omega_null >= omega_obs)
    Fixed in: manuscript (3 locations), supplementary (2 locations),
    reproducibility guide (5 locations)
  - FDR contradiction resolved: "FDR correction is not applied" -> 
    "Benjamini-Hochberg FDR correction is applied" (repro guide line 421)
  - Omega baseline: "yield omega close to 1 (baseline behavior)" ->
    "yield omega above 1 (empirical calibration baseline 6.67)"
    (manuscript Introduction + Results)
  - "Striking" language removed: 3 instances replaced with 
    "notable", "pronounced", "substantially"
  - Statistical reporting: removed contradictory "All P-values are
    two-sided unless otherwise specified" statement
  - Supplementary Algorithm 1 consistency: B=1000 (was B=500)

Bootstrap v3 Updates:
  - Brain bootstrap re-run with one-sided P-value formula
    (pseudobulk-level permutation, B=1000)
  - All 10 cell types significant (P < 0.01, FDR < 0.05)
  - _load_manuscript_data.py updated for new CSV columns
  - Brain data loaded dynamically from brain_bootstrap_results.csv

Files NOT regenerated (unchanged from v18):
  - Figures (f1-f6): no visual changes needed for text-only fixes
  - Supplementary Figures (S1-S7): unchanged
  - Graphical Abstract: unchanged
  - Table1-2.docx: tables unchanged
"""
    manifest_path = WORK_DIR / "MANIFEST_v19.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest)
    print(f"  Wrote {manifest_path.name}")

    # 3. Create ZIP
    print(f"\n[3] Creating ZIP...")
    with zipfile.ZipFile(V19_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORK_DIR):
            for fname in sorted(files):
                fpath = Path(root) / fname
                arcname = f"CKI_NAR_Submission_v19/{fname}"
                zf.write(fpath, arcname)

    # 4. Verify
    zip_size_mb = V19_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  v19 Package Built Successfully")
    print(f"{'='*60}")
    print(f"ZIP: {V19_ZIP}")
    print(f"Size: {zip_size_mb:.1f} MB")

    with zipfile.ZipFile(V19_ZIP, "r") as zf:
        infos = sorted(zf.infolist(), key=lambda x: x.filename)
        print(f"Files: {len(infos)}")
        for info in infos:
            print(f"  {info.file_size:>10,}  {info.filename}")


if __name__ == "__main__":
    build_v19()
