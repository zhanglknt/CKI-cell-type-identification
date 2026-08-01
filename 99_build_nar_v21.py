#!/usr/bin/env python3
"""Build CKI NAR Submission Package v21.

v21 refreshes v20 with confirmed brain bootstrap v3 results and updates
the README/project homepage with the latest findings.

Key changes from v20:
  - Brain bootstrap v3 confirmed: 10/10 cell types significant (P<0.01, FDR<0.05)
    after fixing region filter bug (Bergmann glia cell/region mismatch)
  - Fresh regeneration of all 4 DOCX files with latest data
  - README.md updated with current results and project status
  - All 4 bootstrap datasets validated: mouse (8/15), human (15/16),
    TCGA (descriptive), brain (10/10)

Files regenerated:
  - CKI_NAR_Manuscript.docx (fresh with brain v3 confirmation)
  - CKI_NAR_Supplementary.docx (fresh)
  - CKI_NAR_Cover_Letter.docx (fresh)
  - CKI_NAR_Reproducibility_Guide.docx (fresh)

Files unchanged from v20:
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

V21_ZIP = VERSION3_DIR / "CKI_NAR_Submission_v21.zip"
WORK_DIR = VERSION3_DIR / "CKI_NAR_Submission_v21"
V20_DIR = VERSION3_DIR / "CKI_NAR_Submission_v20"


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


def build_v21():
    print("=" * 60)
    print("  CKI NAR Submission Package v21 Builder")
    print("  Brain v3 Confirmation + Fresh Rebuild")
    print("=" * 60)

    # 0. Prepare work directory
    print(f"\n[0] Preparing {WORK_DIR.name}...")
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    # Copy base files from v20 (figures, tables, graphical abstract)
    if V20_DIR.exists():
        for f in V20_DIR.iterdir():
            if f.name.startswith("MANIFEST"):
                continue
            # DOCX files will be regenerated fresh, except Table1-2
            if f.name.endswith(".docx") and f.name != "Table1-2.docx":
                continue
            shutil.copy2(f, WORK_DIR / f.name)
        print(f"  Copied figures/tables/GA from v20")
    else:
        print(f"  ERROR: v20 directory not found at {V20_DIR}")
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

    # 1d. Reproducibility guide
    node_env = os.environ.copy()
    node_env["NODE_PATH"] = NODE_PATH
    run_script(
        f'"{NODE}" notebooks/100_gen_reproducibility_docx.js',
        "Generating CKI_Reproducibility_Guide.docx",
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
    print(f"\n[2] Writing MANIFEST_v21.txt...")
    manifest = f"""CKI NAR Submission Package v21
Built: {datetime.now().strftime('%Y-%m-%d %H:%M')}

This package is a fresh rebuild of v20 with:
- Brain bootstrap v3 confirmed (10/10 cell types significant)
- All 4 DOCX files regenerated with latest data
- Bootstrap validation complete for all 4 datasets

Contents:
1. CKI_NAR_Manuscript.docx - Main manuscript (English, fresh)
2. CKI_NAR_Supplementary.docx - Supplementary materials (English, fresh)
3. CKI_NAR_Cover_Letter.docx - Cover letter (fresh)
4. CKI_NAR_Reproducibility_Guide.docx - Computational reproducibility guide (fresh)
5. Table1-2.docx - Standalone tables (unchanged from v20)
6. figure1.pdf through figure6.pdf - Main figures (unchanged from v20)
7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S7.pdf
8. CKI_graphical_abstract.png/pdf/svg - Graphical Abstract

Bootstrap Status (all 4 datasets):
  Mouse (Tabula Muris): 8/15 significant, B=1000, one-sided + BH FDR
  Human (Tabula Sapiens): 15/16 significant, P=9.99e-04, B=1000
  TCGA (BRCA/LIHC/LUAD): descriptive omega + Cohen's d, B=1000
  Brain (Siletti Atlas): 10/10 significant, P<0.01, FDR<0.05, B=1000

Brain Bootstrap v3 Details:
  Astrocyte: omega=76.20, null_mean=12.58, d=321.85, P=9.99e-04
  Oligodendrocyte: omega=41.73, null_mean=10.59, d=234.42, P=9.99e-04
  Choroid plexus: omega=33.97, null_mean=14.89, d=9.32, P=9.99e-04
  Committed OPC: omega=30.57, null_mean=18.76, d=13.77, P=9.99e-04
  Oligodendrocyte precursor: omega=22.69, null_mean=11.16, d=32.23, P=9.99e-04
  Ependymal: omega=14.52, null_mean=10.82, d=9.98, P=9.99e-04
  Fibroblast: omega=13.99, null_mean=12.00, d=9.27, P=9.99e-04
  Microglia: omega=13.54, null_mean=8.98, d=34.22, P=9.99e-04
  Vascular: omega=12.60, null_mean=10.06, d=16.39, P=9.99e-04
  Bergmann glia: omega=11.17, null_mean=8.75, d=6.46, P=2.997e-03

Changes from v20:
  - Fresh DOCX regeneration (all 4 files)
  - Brain v3 results confirmed and embedded
  - README.md updated on GitHub
  - No figure/table changes (text-only refresh)

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
    manifest_path = WORK_DIR / "MANIFEST_v21.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest)
    print(f"  Wrote {manifest_path.name}")

    # 3. Create ZIP
    print(f"\n[3] Creating ZIP...")
    with zipfile.ZipFile(V21_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORK_DIR):
            for fname in sorted(files):
                fpath = Path(root) / fname
                arcname = f"CKI_NAR_Submission_v21/{fname}"
                zf.write(fpath, arcname)

    # 4. Verify
    zip_size_mb = V21_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  v21 Package Built Successfully")
    print(f"{'='*60}")
    print(f"ZIP: {V21_ZIP}")
    print(f"Size: {zip_size_mb:.1f} MB")

    with zipfile.ZipFile(V21_ZIP, "r") as zf:
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
    success = build_v21()
    sys.exit(0 if success else 1)
