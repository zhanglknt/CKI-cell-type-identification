#!/usr/bin/env python3
"""Build CKI NAR Submission Package v20.

v20 incorporates all Phase D expert review fixes (4 Critical + 19 Major issues)
on top of v19's text-wide contradiction fixes and brain bootstrap v3.

Key changes from v19:
  Phase D (Task #705) - Interpretation corrections + Major Issues:

  Critical fixes:
    C-B1: HK gene neutrality assumption - expanded mechanistic discussion
    C-B3: TCGA "convergence" - rewritten as exploratory analysis with confounders
    C-S4: Cross-organ sample size - added n<5 flag and bootstrap CIs
    C-S6: TCGA paired statistics - removed Mann-Whitney P-values, descriptive only

  Major fixes (19 items):
    M-M1: Added limitation re: no synthetic ground-truth validation
    M-M2/M-B2: Added limitation re: no quantitative benchmarking vs specialized methods
    M-M4: TCGA bulk-level confounders explicitly listed
    M-M5: Added limitation re: parameter justification (6 parameters)
    M-S1: One-sided permutation test justification added
    M-S2: BH-FDR per-dataset caveat added
    M-S3: Spearman CI reference added
    M-S5/M-B4: PAM50/Edmondson small subgroup caveats
    M-S6: omega=8.01 vs 14.36 clarification (grand mean dominated by low-omega CTs)
    M-B1: Cross-species validation mentioned in Discussion
    M-W1: Cover Letter "orthogonal" -> "independent"
    M-W2: Cover Letter "proving" -> "demonstrating that"
    M-W3: Cover Letter "confirmed baseline behavior" -> "empirical baseline"
    M-W4: Figure 5 legend verified correct
    M-W5: Graphical Abstract verified present
    M-W6: pair count verified as 59 (cross_organ_n_total)
    M-W7: Figure legends - added "Statistical conventions" paragraph

  New supplementary sections (3.8-3.11):
    3.8 TCGA Exploratory Analysis Caveats
    3.9 Cross-Organ Sample Size Considerations
    3.10 One-Sided Permutation Test Justification
    3.11 Parameter Justification

  New reproducibility guide section:
    5.5 Phase D Interpretation Corrections (14 items a-n)
    Parameter table: 3 new rows
    Reproduction checklist: 5 new items

Files regenerated:
  - CKI_NAR_Manuscript.docx (13 text edits)
  - CKI_NAR_Supplementary.docx (4 new sections)
  - CKI_NAR_Cover_Letter.docx (3 wording fixes)
  - CKI_NAR_Reproducibility_Guide.docx (new section + table + checklist)

Files unchanged from v19 (no visual changes needed):
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

V20_ZIP = VERSION3_DIR / "CKI_NAR_Submission_v20.zip"
WORK_DIR = VERSION3_DIR / "CKI_NAR_Submission_v20"
V19_DIR = VERSION3_DIR / "CKI_NAR_Submission_v19"


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


def build_v20():
    print("=" * 60)
    print("  CKI NAR Submission Package v20 Builder")
    print("=" * 60)

    # 0. Prepare work directory
    print(f"\n[0] Preparing {WORK_DIR.name}...")
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    if V19_DIR.exists():
        for f in V19_DIR.iterdir():
            if f.name.startswith("MANIFEST"):
                continue
            shutil.copy2(f, WORK_DIR / f.name)
        print(f"  Copied base files from v19")
    else:
        print(f"  ERROR: v19 directory not found at {V19_DIR}")
        return

    # 1. Regenerate DOCX files with Phase D fixes
    print(f"\n[1] Regenerating DOCX files with Phase D fixes...")

    # 1a. Main manuscript (13 text edits from Phase D)
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

    # 1b. Supplementary materials (4 new sections 3.8-3.11)
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

    # 1c. Cover letter (3 wording fixes)
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

    # 1d. Reproducibility guide (new section 5.5 + table + checklist)
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
    print(f"\n[2] Writing MANIFEST_v20.txt...")
    manifest = f"""CKI NAR Submission Package v20
Built: {datetime.now().strftime('%Y-%m-%d %H:%M')}

This package updates v19 with all Phase D expert review fixes
(4 Critical + 19 Major issues, Task #705).

Contents:
1. CKI_NAR_Manuscript.docx - Main manuscript (English, regenerated with Phase D fixes)
2. CKI_NAR_Supplementary.docx - Supplementary materials (English, regenerated)
3. CKI_NAR_Cover_Letter.docx - Cover letter (regenerated with wording fixes)
4. CKI_NAR_Reproducibility_Guide.docx - Computational reproducibility guide (regenerated)
5. Table1-2.docx - Standalone tables (from v18, unchanged)
6. figure1.pdf through figure6.pdf - Main figures (from v18, unchanged)
7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S7.pdf
8. CKI_graphical_abstract.png/pdf/svg - Graphical Abstract

Key changes in v20 (relative to v19):

Phase D Critical Fixes (4 items):
  C-B1: HK gene neutrality assumption - expanded Discussion with mechanistic
        argument (synonymous sites are neutral; HK genes lack comparable argument;
        positioned as practical proxy for neutrality)
  C-B3: TCGA "convergence" interpretation - Results and Discussion rewritten as
        exploratory analysis; 3 bulk-level confounders listed (cell composition,
        peritumoral inflammation, RNA quality)
  C-S4: Cross-organ sample size - added n<5 flag (Memory B n=1, Smooth muscle n=1),
        recommended n>=5 for biological conclusions, bootstrap CIs referenced
  C-S6: TCGA paired statistics - removed Mann-Whitney P-values (n=2-5 per cancer
        type has minimum P~0.33, insufficient power); changed to descriptive only

Phase D Major Fixes (19 items):
  M-M1: New Limitation #14 - no synthetic ground-truth validation
  M-M2/M-B2: Discussion - "did not quantitatively benchmark CKI against specialized methods"
  M-M4: TCGA Results - 3 confounders explicitly listed (cell composition, peritumoral, RNA quality)
  M-M5: New Limitation #15 - 6 parameters lack formal optimization (softmax, epsilon,
        top-200 DE, HVG=2000, log-base 2, B=1000)
  M-S1: Methods - one-sided test justification (directional hypothesis)
  M-S2: New Limitation #13 - BH-FDR per-dataset, not comparable across datasets
  M-S3: Cross-organ Spearman - bootstrap 95% CIs referenced (Supplementary Table S2)
  M-S5/M-B4: PAM50/Edmondson - small subgroup caveats (Normal-like n=7, G4 n=11) +
        proliferation confound + "exploratory in nature"
  M-S6: Brain gradient - omega=8.01 vs 14.36 clarified (grand mean dominated by
        low-omega cell types)
  M-B1: Discussion - cross-species validation mentioned (Supplementary Fig. S2)
  M-W1: Cover Letter - "orthogonal information" -> "independent information dimension"
  M-W2: Cover Letter - "proving it measures" -> "demonstrating that it measures"
  M-W3: Cover Letter - "confirmed baseline behavior" -> "empirical baseline for
        equivalent populations"; "developmental origin signatures" -> "developmental signatures"
  M-W4: Figure 5 legend - verified correct ("within Tabula Sapiens")
  M-W5: Graphical Abstract - verified present
  M-W6: Pair count - verified as 59 (cross_organ_n_total from data)
  M-W7: Figure legends - added "Statistical conventions" paragraph

New Supplementary Sections (3.8-3.11):
  3.8 TCGA Exploratory Analysis Caveats (6 categories)
  3.9 Cross-Organ Sample Size Considerations
  3.10 One-Sided Permutation Test Justification
  3.11 Parameter Justification (6 parameters)

New Reproducibility Guide Content:
  Section 5.5: Phase D Interpretation Corrections (14 items a-n)
  Parameter table: 3 new rows (one-sided direction, TCGA paired, cross-organ min n)
  Reproduction checklist: 5 new Phase D verification items

Files NOT regenerated (unchanged from v19):
  - Figures (f1-f6): no visual changes needed for text-only fixes
  - Supplementary Figures (S1-S7): unchanged
  - Graphical Abstract: unchanged
  - Table1-2.docx: tables unchanged
"""
    manifest_path = WORK_DIR / "MANIFEST_v20.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest)
    print(f"  Wrote {manifest_path.name}")

    # 3. Create ZIP
    print(f"\n[3] Creating ZIP...")
    with zipfile.ZipFile(V20_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORK_DIR):
            for fname in sorted(files):
                fpath = Path(root) / fname
                arcname = f"CKI_NAR_Submission_v20/{fname}"
                zf.write(fpath, arcname)

    # 4. Verify
    zip_size_mb = V20_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  v20 Package Built Successfully")
    print(f"{'='*60}")
    print(f"ZIP: {V20_ZIP}")
    print(f"Size: {zip_size_mb:.1f} MB")

    with zipfile.ZipFile(V20_ZIP, "r") as zf:
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

    # Check DOCX file sizes
    docx_files = [
        ("CKI_NAR_Manuscript.docx", 50),        # >50 KB
        ("CKI_NAR_Supplementary.docx", 35),      # >35 KB
        ("CKI_NAR_Cover_Letter.docx", 30),       # >30 KB
        ("CKI_NAR_Reproducibility_Guide.docx", 15),  # >15 KB
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

    # Check figures
    for i in range(1, 7):
        fpath = WORK_DIR / f"figure{i}.pdf"
        if fpath.exists():
            checks_passed += 1
        else:
            print(f"  figure{i}.pdf: MISSING!")
            checks_failed += 1

    # Check supplementary figures
    for i in range(1, 8):
        fpath = WORK_DIR / f"Supplementary_Figure_S{i}.pdf"
        if fpath.exists():
            checks_passed += 1
        else:
            print(f"  Supplementary_Figure_S{i}.pdf: MISSING!")
            checks_failed += 1

    # Check graphical abstract
    for ext in ["png", "pdf", "svg"]:
        fpath = WORK_DIR / f"CKI_graphical_abstract.{ext}"
        if fpath.exists():
            checks_passed += 1
        else:
            print(f"  CKI_graphical_abstract.{ext}: MISSING!")
            checks_failed += 1

    # Check Table1-2
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
    success = build_v20()
    sys.exit(0 if success else 1)
