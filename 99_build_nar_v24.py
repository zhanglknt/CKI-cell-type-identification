#!/usr/bin/env python3
"""Build CKI NAR Submission Package v24.

v24 incorporates Phase 2: C1 BH-FDR fix from v23 expert panel review.

C1 Fix: Remove EVT/BH-FDR q-values from residual model permutation analysis.
- Replaced EVT-extrapolated P-values and BH-FDR q-values with honest reporting
- 16/30 Strong signals reach P-value floor (9.99e-5, B=10,000), no FDR applied
- Added explicit limitation about FDR inapplicability due to P-value floor saturation
- All EVT/GPD references removed from manuscript, supplementary, and repro guide

Changes from v23:
  - Manuscript: Methods/Results/Discussion/Limitations all updated
  - Supplementary: Section 3.3 rewritten, EVT content removed
  - Reproducibility Guide: EVT references removed, parameter table updated

Files regenerated:
  - CKI_NAR_Manuscript.docx (fresh, C1 fixes)
  - CKI_NAR_Supplementary.docx (fresh, C1 fixes)
  - CKI_NAR_Cover_Letter.docx (fresh)
  - CKI_NAR_Reproducibility_Guide.docx (fresh, C1 fixes)

Files unchanged from v23:
  - Figures (figure1-6.pdf)
  - Supplementary Figures (S1-S7)
  - Graphical Abstract (png/pdf/svg)
  - Table1-2.docx
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
NODE_PATH = r"C:\Users\KnightZ\.workbuddy\binaries\node\workspace\node_modules"

V24_ZIP = VERSION3_DIR / "CKI_NAR_Submission_v24.zip"
WORK_DIR = VERSION3_DIR / "CKI_NAR_Submission_v24"
V23_DIR = VERSION3_DIR / "CKI_NAR_Submission_v23"


def run_script(cmd, label, env=None):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                            cwd=str(BASE_DIR), env=env)
    if result.stdout:
        print(result.stdout[-800:] if len(result.stdout) > 800 else result.stdout)
    if result.returncode != 0:
        print(f"  WARNING: Return code {result.returncode}")
        if result.stderr:
            print(f"  STDERR: {result.stderr[-500:]}")
    else:
        print(f"  OK")
    return result.returncode == 0


def build_v24():
    print("=" * 60)
    print("  CKI NAR Submission Package v24 Builder")
    print("  Phase 2: C1 BH-FDR fix (remove EVT, honest P-value reporting)")
    print("=" * 60)

    # 0. Prepare work directory
    print(f"\n[0] Preparing {WORK_DIR.name}...")
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    # Copy base files from v23
    if V23_DIR.exists():
        for f in V23_DIR.iterdir():
            if f.name.startswith("MANIFEST"):
                continue
            if f.name.endswith(".docx") and f.name != "Table1-2.docx":
                continue
            shutil.copy2(f, WORK_DIR / f.name)
        print(f"  Copied figures/tables/GA from v23")
    else:
        print(f"  ERROR: v23 directory not found at {V23_DIR}")
        return

    # 1. Regenerate DOCX files fresh
    print(f"\n[1] Regenerating all DOCX files with C1 fixes...")

    # 1a. Main manuscript
    run_script(
        f'"{PYTHON}" -u generate_manuscript_nar.py',
        "Generating CKI_NAR_Manuscript.docx (C1 fixes)"
    )
    ms_src = RESULTS_DIR / "CKI_NAR_Manuscript.docx"
    if ms_src.exists():
        shutil.copy2(ms_src, WORK_DIR / "CKI_NAR_Manuscript.docx")
        print(f"  Copied: {ms_src.name} ({ms_src.stat().st_size/1024:.1f} KB)")
    else:
        print(f"  ERROR: Manuscript not generated!")
        return

    # 1b. Supplementary materials
    run_script(
        f'"{PYTHON}" -u notebooks/68_gen_supplementary_en.py',
        "Generating CKI_NAR_Supplementary.docx (C1 fixes)"
    )
    sm_src = RESULTS_DIR / "CKI_NAR_Supplementary.docx"
    if sm_src.exists():
        shutil.copy2(sm_src, WORK_DIR / "CKI_NAR_Supplementary.docx")
        print(f"  Copied: {sm_src.name} ({sm_src.stat().st_size/1024:.1f} KB)")
    else:
        print(f"  ERROR: Supplementary not generated!")
        return

    # 1c. Cover letter
    run_script(
        f'"{PYTHON}" -u generate_cover_letter_nar.py',
        "Generating CKI_NAR_Cover_Letter.docx"
    )
    cl_src = RESULTS_DIR / "CKI_NAR_Cover_Letter.docx"
    if cl_src.exists():
        shutil.copy2(cl_src, WORK_DIR / "CKI_NAR_Cover_Letter.docx")
        print(f"  Copied: {cl_src.name} ({cl_src.stat().st_size/1024:.1f} KB)")
    else:
        print(f"  ERROR: Cover letter not generated!")
        return

    # 1d. Reproducibility guide
    node_env = os.environ.copy()
    node_env["NODE_PATH"] = NODE_PATH
    run_script(
        f'"{NODE}" notebooks/100_gen_reproducibility_docx.js',
        "Generating CKI_Reproducibility_Guide.docx (C1 fixes)",
        env=node_env
    )
    rg_src = RESULTS_DIR / "CKI_Reproducibility_Guide.docx"
    if rg_src.exists():
        shutil.copy2(rg_src, WORK_DIR / "CKI_NAR_Reproducibility_Guide.docx")
        print(f"  Copied: {rg_src.name} ({rg_src.stat().st_size/1024:.1f} KB)")
    else:
        print(f"  ERROR: Reproducibility guide not generated!")
        return

    # 2. Write manifest
    print(f"\n[2] Writing MANIFEST_v24.txt...")
    manifest = f"""CKI NAR Submission Package v24
Built: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Phase 2 Fix: C1 BH-FDR q-value validation (from v23 expert panel review)

C1 — Residual Model Permutation P-values:
  - REMOVED: All EVT (Extreme Value Theory) / GPD tail extrapolation claims
  - REMOVED: All BH-FDR q-values for residual model (m=31,764, B=10,000)
  - REPLACED WITH: Honest reporting of unadjusted permutation P-values
  - 16/30 Strong signals reach P=9.99e-5 floor (P-value floor, not FDR-controlled)
  - Added explicit limitation: FDR inapplicable due to P-value floor saturation (36.3%)
  - All 4 DOCX files regenerated with C1 fixes

Inherited from v23 (Phase 1):
  - C7: NAR formatting (Keywords after Abstract, OS field, Running title)
  - C6: Title wording verified (no "Selective" occurrences)

Inherited from v22:
  - C2 fix: k_n floor (minimum) = 1e-4 in reproducibility guide parameter table

Inherited from v20:
  - Phase D Critical Fixes (C-B1, C-B3, C-S4, C-S6)
  - Phase D Major Fixes (19 items)
  - Phase B/C/A fixes
  - v20 Review Fixes (7 items, Task #707-#709)

Remaining Critical Issues (3):
  C3: Mouse k_n scheme description
  C4: HK gene neutrality biological foundation
  C5: OPC negative control validation

Contents:
1. CKI_NAR_Manuscript.docx - Main manuscript (English, C1 fixes)
2. CKI_NAR_Supplementary.docx - Supplementary materials (English, C1 fixes)
3. CKI_NAR_Cover_Letter.docx - Cover letter (fresh)
4. CKI_NAR_Reproducibility_Guide.docx - Reproducibility guide (C1 fixes)
5. Table1-2.docx - Standalone tables
6. figure1.pdf through figure6.pdf - Main figures
7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S7.pdf
8. CKI_graphical_abstract.png/pdf/svg - Graphical Abstract

Bootstrap Status (all 4 datasets):
  Mouse (Tabula Muris): 8/15 significant, B=1000, one-sided + BH FDR
  Human (Tabula Sapiens): 15/16 significant, B=1000
  TCGA (BRCA/LIHC/LUAD): descriptive, B=1000
  Brain (Siletti Atlas): 10/10 significant, B=1000

Residual Model (Brain, 31,764 pairs):
  30 Strong candidates | 16 reached P=9.99e-5 floor (no FDR)
  6 astrocyte + 10 oligodendrocyte | 14 not significant (P>=0.76)
"""
    manifest_path = WORK_DIR / "MANIFEST_v24.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest)
    print(f"  Wrote {manifest_path.name}")

    # 3. Create ZIP
    print(f"\n[3] Creating ZIP...")
    with zipfile.ZipFile(V24_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORK_DIR):
            for fname in sorted(files):
                fpath = Path(root) / fname
                arcname = f"CKI_NAR_Submission_v24/{fname}"
                zf.write(fpath, arcname)

    zip_size_mb = V24_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  v24 Package Built Successfully")
    print(f"{'='*60}")
    print(f"ZIP: {V24_ZIP}")
    print(f"Size: {zip_size_mb:.1f} MB")

    with zipfile.ZipFile(V24_ZIP, "r") as zf:
        infos = sorted(zf.infolist(), key=lambda x: x.filename)
        print(f"Files: {len(infos)}")
        for info in infos:
            print(f"  {info.file_size:>10,}  {info.filename}")

    # 4. Final consistency check
    print(f"\n{'='*60}")
    print(f"  Final Consistency Check")
    print(f"{'='*60}")
    checks_passed = 0
    checks_failed = 0

    docx_files = [
        ("CKI_NAR_Manuscript.docx", 50),
        ("CKI_NAR_Supplementary.docx", 35),
        ("CKI_NAR_Cover_Letter.docx", 30),
        ("CKI_NAR_Reproducibility_Guide.docx", 15),
    ]
    for fname, min_kb in docx_files:
        fpath = WORK_DIR / fname
        if fpath.exists():
            size_kb = fpath.stat().st_size / 1024
            status = "OK" if size_kb >= min_kb else "WARNING: small"
            print(f"  {fname}: {size_kb:.1f} KB [{status}]")
            if size_kb >= min_kb:
                checks_passed += 1
            else:
                checks_failed += 1
        else:
            print(f"  {fname}: MISSING!")
            checks_failed += 1

    for i in range(1, 7):
        fpath = WORK_DIR / f"figure{i}.pdf"
        if fpath.exists():
            checks_passed += 1
        else:
            print(f"  figure{i}.pdf: MISSING!")
            checks_failed += 1

    for i in range(1, 8):
        fpath = WORK_DIR / f"Supplementary_Figure_S{i}.pdf"
        if fpath.exists():
            checks_passed += 1
        else:
            print(f"  Supplementary_Figure_S{i}.pdf: MISSING!")
            checks_failed += 1

    for ext in ["png", "pdf", "svg"]:
        fpath = WORK_DIR / f"CKI_graphical_abstract.{ext}"
        if fpath.exists():
            checks_passed += 1
        else:
            print(f"  CKI_graphical_abstract.{ext}: MISSING!")
            checks_failed += 1

    if (WORK_DIR / "Table1-2.docx").exists():
        checks_passed += 1
    else:
        print(f"  Table1-2.docx: MISSING!")
        checks_failed += 1

    print(f"\n  Checks passed: {checks_passed}")
    print(f"  Checks failed: {checks_failed}")
    if checks_failed == 0:
        print(f"  ALL CHECKS PASSED")
    else:
        print(f"  SOME CHECKS FAILED - review above")

    return checks_failed == 0


if __name__ == "__main__":
    success = build_v24()
    sys.exit(0 if success else 1)
