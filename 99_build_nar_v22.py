#!/usr/bin/env python3
"""Build CKI NAR Submission Package v22.

v22 incorporates C2 fix from the v20 expert panel review:
k_n floor parameter (1e-4) added to the reproducibility guide parameter table.

Key changes from v21:
  - C2 fix: k_n floor (minimum) = 1e-4 added to Section 6 Parameter Summary
    in the reproducibility guide (100_gen_reproducibility_docx.js)
  - Reproducibility guide regenerated with updated parameter table
  - All other DOCX files re-generated fresh for consistency

Files regenerated:
  - CKI_NAR_Manuscript.docx (fresh)
  - CKI_NAR_Supplementary.docx (fresh)
  - CKI_NAR_Cover_Letter.docx (fresh)
  - CKI_NAR_Reproducibility_Guide.docx (fresh, C2 fix)

Files unchanged from v21:
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

V22_ZIP = VERSION3_DIR / "CKI_NAR_Submission_v22.zip"
WORK_DIR = VERSION3_DIR / "CKI_NAR_Submission_v22"
V21_DIR = VERSION3_DIR / "CKI_NAR_Submission_v21"


def run_script(cmd, label, env=None):
    """Run a subprocess and check return code."""
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


def build_v22():
    print("=" * 60)
    print("  CKI NAR Submission Package v22 Builder")
    print("  C2 Fix: k_n floor in parameter table")
    print("=" * 60)

    # 0. Prepare work directory
    print(f"\n[0] Preparing {WORK_DIR.name}...")
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    # Copy base files from v21 (figures, tables, graphical abstract)
    if V21_DIR.exists():
        for f in V21_DIR.iterdir():
            if f.name.startswith("MANIFEST"):
                continue
            # DOCX files will be regenerated fresh, except Table1-2
            if f.name.endswith(".docx") and f.name != "Table1-2.docx":
                continue
            shutil.copy2(f, WORK_DIR / f.name)
        print(f"  Copied figures/tables/GA from v21")
    else:
        print(f"  ERROR: v21 directory not found at {V21_DIR}")
        return

    # 1. Regenerate DOCX files fresh
    print(f"\n[1] Regenerating all DOCX files with latest data...")

    # 1a. Main manuscript
    run_script(
        f'"{PYTHON}" -u generate_manuscript_nar.py',
        "Generating CKI_NAR_Manuscript.docx"
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
        "Generating CKI_NAR_Supplementary.docx"
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

    # 1d. Reproducibility guide (C2 fix included)
    node_env = os.environ.copy()
    node_env["NODE_PATH"] = NODE_PATH
    run_script(
        f'"{NODE}" notebooks/100_gen_reproducibility_docx.js',
        "Generating CKI_Reproducibility_Guide.docx (C2 fix)"
    )
    rg_src = RESULTS_DIR / "CKI_Reproducibility_Guide.docx"
    if rg_src.exists():
        shutil.copy2(rg_src, WORK_DIR / "CKI_NAR_Reproducibility_Guide.docx")
        print(f"  Copied: {rg_src.name} ({rg_src.stat().st_size/1024:.1f} KB)")
    else:
        print(f"  ERROR: Reproducibility guide not generated!")
        return

    # 2. Write manifest
    print(f"\n[2] Writing MANIFEST_v22.txt...")
    manifest = f"""CKI NAR Submission Package v22
Built: {datetime.now().strftime('%Y-%m-%d %H:%M')}

This package incorporates the C2 fix from the v20 expert panel review:
- C2: k_n floor (minimum) = 1e-4 added to Section 6 Parameter Summary
  in the reproducibility guide

Contents:
1. CKI_NAR_Manuscript.docx - Main manuscript (English, fresh)
2. CKI_NAR_Supplementary.docx - Supplementary materials (English, fresh)
3. CKI_NAR_Cover_Letter.docx - Cover letter (fresh)
4. CKI_NAR_Reproducibility_Guide.docx - Computational reproducibility guide (fresh)
5. Table1-2.docx - Standalone tables (unchanged from v21)
6. figure1.pdf through figure6.pdf - Main figures (unchanged from v21)
7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S7.pdf
8. CKI_graphical_abstract.png/pdf/svg - Graphical Abstract

Bootstrap Status (all 4 datasets):
  Mouse (Tabula Muris): 8/15 significant, B=1000, one-sided + BH FDR
  Human (Tabula Sapiens): 15/16 significant, P=9.99e-04, B=1000
  TCGA (BRCA/LIHC/LUAD): descriptive omega + Cohen's d, B=1000
  Brain (Siletti Atlas): 10/10 significant, P<0.01, FDR<0.05, B=1000

Changes from v21:
  - C2 fix: k_n floor (minimum) = 1e-4 added to reproducibility guide parameter table
  - All 4 DOCX files regenerated fresh

Phase D Critical Fixes (4 items, inherited from v20):
  C-B1: HK gene neutrality assumption - expanded Discussion
  C-B3: TCGA "convergence" - rewritten as exploratory
  C-S4: Cross-organ sample size - added n<5 flag
  C-S6: TCGA paired statistics - descriptive only

Phase D Major Fixes (19 items, inherited from v20)
Phase B Statistical Upgrades (inherited from v20)
Phase C Methodological Reinforcement (inherited from v20)
Phase A Text Polish (inherited from v20)

v20 Review Fixes (7 items, Task #707-#709, inherited):
  1. "orthogonal" -> "independent information dimension"
  2. TCGA paired: removed Mann-Whitney U
  3. astrocyte: 4,489 -> 5,778 pairs
  4. Added "two-sided" non-parametric test declaration
  5. Cover Letter: dangling modifier fix
  6. Supplementary: astrocyte 4,489 -> 5,778
  7. Repro Guide: omega~1 -> empirical baseline ~6.67
"""
    manifest_path = WORK_DIR / "MANIFEST_v22.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest)
    print(f"  Wrote {manifest_path.name}")

    # 3. Create ZIP
    print(f"\n[3] Creating ZIP...")
    with zipfile.ZipFile(V22_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORK_DIR):
            for fname in sorted(files):
                fpath = Path(root) / fname
                arcname = f"CKI_NAR_Submission_v22/{fname}"
                zf.write(fpath, arcname)

    # 4. Verify
    zip_size_mb = V22_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  v22 Package Built Successfully")
    print(f"{'='*60}")
    print(f"ZIP: {V22_ZIP}")
    print(f"Size: {zip_size_mb:.1f} MB")

    with zipfile.ZipFile(V22_ZIP, "r") as zf:
        infos = sorted(zf.infolist(), key=lambda x: x.filename)
        print(f"Files: {len(infos)}")
        for info in infos:
            print(f"  {info.file_size:>10,}  {info.filename}")

    # 5. Final consistency check
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
    success = build_v22()
    sys.exit(0 if success else 1)
