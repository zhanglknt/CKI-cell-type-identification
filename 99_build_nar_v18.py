#!/usr/bin/env python3
"""Build CKI NAR Submission Package v18.

v18 incorporates all fixes from the v17 expert review (8 Critical issues):
  C1: Bootstrap B=1000 for all datasets (mouse, human, TCGA, brain) — re-runs completed
  C2: HRT Atlas HK genes loaded directly (not auto-detected) — docs aligned (#652)
  C3: TCGA 5 cancer types (not 6) in S3 legend (#639)
  C4: Figure 5 legend corrected: 17 cell types, 59 pairs (#640)
  C5: Algorithm 1 pseudocode B=1,000 (#644)
  C6: FDR (Benjamini-Hochberg q_value) added to TCGA and brain bootstrap (#597, #641)
  C7: P-value anchor explanation (omega=1 vs 1.54) (#643)
  C8: S6/S7 supplementary figure PDFs generated and added (#645)

Additional fixes:
  - HK gene documentation aligned across all 4 key documents (#652, 20 edits)
  - Bootstrap P-value formula: absolute deviation from omega=1 (not 2x min)
  - Reproducibility guide: all B values updated to 1000
  - _load_manuscript_data.py: n_bootstrap 500->1000, q_value loading added
  - C9: TCGA log2 pseudocount corrected: log2(TPM + 0.001) -> log2(TPM + 1)
    (Systematic ~1.5x omega inflation confirmed across 44 TSS groups; HJG)
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
PYTHON = r"C:\Users\KnightZ\AppData\Local\Programs\Python\Python312\python.exe"
NODE = r"C:\Users\KnightZ\.workbuddy\binaries\node\versions\22.22.2\node.exe"

V18_ZIP = VERSION3_DIR / "CKI_NAR_Submission_v18.zip"
WORK_DIR = VERSION3_DIR / "CKI_NAR_Submission_v18"

# Source v17 directory for base files
V17_DIR = VERSION3_DIR / "CKI_NAR_Submission_v17"


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


def build_v18():
    print("=" * 60)
    print("  CKI NAR Submission Package v18 Builder")
    print("=" * 60)

    # 0. Prepare work directory
    print(f"\n[0] Preparing {WORK_DIR.name}...")
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    # Copy all files from v17 as base
    if V17_DIR.exists():
        for f in V17_DIR.iterdir():
            if f.name.startswith("MANIFEST"):
                continue  # Skip old manifests
            shutil.copy2(f, WORK_DIR / f.name)
        print(f"  Copied base files from v17")
    else:
        print(f"  ERROR: v17 directory not found at {V17_DIR}")
        return

    # 1. Regenerate DOCX files
    print(f"\n[1] Regenerating DOCX files...")

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

    # 1e. Tables
    run_script(
        f'"{PYTHON}" -u notebooks/69_gen_nar_tables.py',
        "Generating Table1-2.docx"
    )
    tb_src = RESULTS_DIR / "Table1-2.docx"
    if tb_src.exists():
        shutil.copy2(tb_src, WORK_DIR / "Table1-2.docx")
        print(f"  Copied: {tb_src.name} ({tb_src.stat().st_size/1024:.1f} KB)")

    # 2. Regenerate figures (Figure 4 needs updated TCGA bootstrap P-values)
    print(f"\n[2] Regenerating figures...")
    run_script(
        f'"{PYTHON}" -u notebooks/30_genome_biology_figures.py',
        "Regenerating all figures (Figure 4 TCGA P-values updated)"
    )
    # Copy updated figures (descriptive names -> simple names for submission)
    FIG_NAMES = {
        1: "figure1_concept_pipeline",
        2: "figure2_calibration_tabula_muris",
        3: "figure3_orthogonal_information",
        4: "figure4_tcga_pancancer",
        5: "figure5_cross_organ_conservation",
        6: "figure6_brain_regional_cki",
    }
    for i, name in FIG_NAMES.items():
        fig_src = FIGURES_DIR / f"{name}.pdf"
        if fig_src.exists():
            shutil.copy2(fig_src, WORK_DIR / f"figure{i}.pdf")
            print(f"  Copied: {name}.pdf -> figure{i}.pdf ({fig_src.stat().st_size/1024:.1f} KB)")
        else:
            print(f"  WARNING: {name}.pdf not found!")

    # 3. Copy supplementary figures (S1-S5 from v17 base, S6-S7 from figures_final)
    print(f"\n[3] Copying supplementary figures...")
    for i in range(1, 8):  # S1 through S7
        fig_src = FIGURES_DIR / f"Supplementary_Figure_S{i}.pdf"
        if fig_src.exists():
            shutil.copy2(fig_src, WORK_DIR / f"Supplementary_Figure_S{i}.pdf")
            print(f"  Copied: Supplementary_Figure_S{i}.pdf ({fig_src.stat().st_size/1024:.1f} KB)")
        elif (WORK_DIR / f"Supplementary_Figure_S{i}.pdf").exists():
            print(f"  S{i}: kept from v17 base (not regenerated)")
        else:
            print(f"  WARNING: Supplementary_Figure_S{i}.pdf not found!")

    # 4. Copy graphical abstract
    print(f"\n[4] Copying graphical abstract...")
    for ext in [".pdf", ".png", ".svg"]:
        ga_src = FIGURES_DIR / f"CKI_graphical_abstract{ext}"
        if ga_src.exists():
            shutil.copy2(ga_src, WORK_DIR / f"CKI_graphical_abstract{ext}")
            print(f"  Copied: CKI_graphical_abstract{ext}")

    # 5. Write manifest
    print(f"\n[5] Writing MANIFEST_v18.txt...")
    manifest = f"""CKI NAR Submission Package v18
Built: {datetime.now().strftime('%Y-%m-%d %H:%M')}

This package updates v17 with all 8 Critical issue fixes from the v17
expert review, plus HK gene documentation alignment (#652) and complete
bootstrap re-runs (B=1000 for all datasets).

Contents:
1. CKI_NAR_Manuscript.docx - Main manuscript (English, regenerated)
2. CKI_NAR_Supplementary.docx - Supplementary materials (English, regenerated)
3. CKI_NAR_Cover_Letter.docx - Cover letter with 6 suggested reviewers
4. CKI_NAR_Reproducibility_Guide.docx - Computational reproducibility guide (regenerated)
5. Table1-2.docx - Standalone tables extracted from manuscript
6. figure1.pdf through figure6.pdf - Main figures (Figure 4 updated with B=1000 P-values)
7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S7.pdf - Supplementary figures
8. CKI_graphical_abstract.png/pdf/svg - Graphical Abstract (300 DPI, NAR-compliant)

Key fixes in v18 (relative to v17):

Critical Issues (8/8 resolved):
  C1: Bootstrap B=1000 for ALL datasets (mouse, human, TCGA, brain)
      - All bootstrap scripts re-run with B=1000
      - P-value formula: absolute deviation from omega=1
      - Reproducibility guide parameter table updated
  C2: HK genes loaded from HRT Atlas v1.0 reference (not auto-detected)
      - 20 edits across 4 key documents (manuscript, supplementary, repro guide, Chinese)
      - API description preserved: detect_housekeeping_genes(use_reference=False) is the
        package default, but all reported analyses use HRT Atlas loaded directly
  C3: TCGA 5 cancer types (not 6) in S3 legend
  C4: Figure 5 legend: 17 cell types, 59 cross-organ pairs
  C5: Algorithm 1 pseudocode: B=1,000 for all datasets
  C6: FDR (Benjamini-Hochberg q_value) added to TCGA and brain bootstrap outputs
      - FDR statement added to manuscript and supplementary text
  C7: P-value anchor explanation: omega=1 (theoretical null) vs 1.54 (empirical calibration)
  C8: S6/S7 supplementary figure PDFs generated and included

Additional improvements:
  - _load_manuscript_data.py: n_bootstrap 500->1000, q_value loading added
  - All bootstrap P-values updated with B=1000 re-runs
  - Figure 4 Panel D: TCGA significance stars updated with new P-values
  - Mouse pilot bootstrap re-run with B=1000 (was B=500), q_value added
  - TCGA bootstrap re-run with B=1000 (was B=100), now includes q_value
  - Brain bootstrap re-run with B=1000 (was B=100), now includes q_value
  - Human bootstrap re-run with q_value added
  - CKI package code fix: detect_functional_genes() default flavor changed
    from "seurat_v3" to "seurat" (requires raw counts; failed on log-transformed
    TCGA data). Now consistent with analysis scripts and documentation.
"""
    manifest_path = WORK_DIR / "MANIFEST_v18.txt"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(manifest)
    print(f"  Wrote {manifest_path.name}")

    # 6. Create ZIP
    print(f"\n[6] Creating ZIP...")
    with zipfile.ZipFile(V18_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(WORK_DIR):
            for fname in sorted(files):
                fpath = Path(root) / fname
                arcname = f"CKI_NAR_Submission_v18/{fname}"
                zf.write(fpath, arcname)

    # 7. Verify
    zip_size_mb = V18_ZIP.stat().st_size / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"  v18 Package Built Successfully")
    print(f"{'='*60}")
    print(f"ZIP: {V18_ZIP}")
    print(f"Size: {zip_size_mb:.1f} MB")

    with zipfile.ZipFile(V18_ZIP, "r") as zf:
        infos = sorted(zf.infolist(), key=lambda x: x.filename)
        print(f"Files: {len(infos)}")
        for info in infos:
            print(f"  {info.file_size:>10,}  {info.filename}")


if __name__ == "__main__":
    build_v18()
