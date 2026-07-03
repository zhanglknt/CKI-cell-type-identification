#!/usr/bin/env python3
"""Rebuild Genome Biology submission package v13 and reproducibility code v4.

v13 changes from v12:
  - Removed 12 scripts that cannot reproduce manuscript results
    (01, 02_ct, 04, 05_human/v2/v3, 05b, 05c, 06_tcga, 07, 07b, 07d)
  - Removed orphaned CSVs from deleted scripts
  - Fixed dead code in 30_genome_biology_figures.py (ct_pilot_results.csv ref)
  - Updated reproducibility guide Section 3.3: clean table, excluded scripts list
  - Updated cross-organ conservation numbers (60→59 pairs, 5,151→4,851)
"""

import zipfile
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT_ROOT / "results"
NOTEBOOKS = PROJECT_ROOT / "notebooks"
DATA_DIR = PROJECT_ROOT / "data"
CKI_DIR = PROJECT_ROOT / "cki"

# ============================================================
# PART 1: Build Reproducibility Code Package v4
# ============================================================

CODE_ZIP = RESULTS / "CKI_Reproducibility_Code_v4.zip"
VERSION = "v4"
SUBMIT_DATE = datetime.now().strftime("%Y-%m-%d")

print(f"=== Building CKI Reproducibility Code {VERSION} ===")

# --- Notebooks to include (ONLY the 10 reproducible scripts + 1 utility) ---
KEPT_NOTEBOOKS = [
    "02b_pilot_v2.py",
    "02c_pilot_v2b.py",
    "03_full_matrix.py",
    "05_phase33_v3_fixed.py",
    "06_phase34_v2.py",
    "07_phase34_clinical.py",
    "07c_brain_siletti_v3.py",
    "08a_tcga_bootstrap.py",
    "13_phase35_method_comparison.py",
    "30_genome_biology_figures.py",
    "build_combined_notebook.py",
]

# --- CSVs produced by kept scripts (all others excluded) ---
KEPT_RESULTS_CSVS = [
    # Mouse (02b/02c/03)
    "mouse_pilot_v2_results.csv",
    "mouse_pilot_v2_key_values.csv",
    "mouse_pilot_v2b_results.csv",
    "mouse_pilot_v2b_key_values.csv",
    "full_matrix_omega.csv",
    "full_matrix_kn.csv",
    "full_matrix_kf.csv",
    "full_matrix_pairs.csv",
    # Human (05_v3_fixed)
    "phase33_v3_human_omega.csv",
    "phase33_v3_human_kn.csv",
    "phase33_v3_human_kf.csv",
    "phase33_v3_human_pairs.csv",
    # Method comparison (13)
    "phase35_all_metrics_pairs.csv",
    "phase35_cross_organ_conservation.csv",
    "phase35_metric_correlation.csv",
    # TCGA (06_v2)
    "phase34_v2_summary.csv",
    "phase34_v2_all_pairs.csv",
    "phase34_v2_TCGA-BRCA_pairs.csv",
    "phase34_v2_TCGA-KIRC_pairs.csv",
    "phase34_v2_TCGA-LIHC_pairs.csv",
    "phase34_v2_TCGA-LUAD_pairs.csv",
    "phase34_v2_TCGA-LUSC_pairs.csv",
    # TCGA clinical (07_clinical)
    "phase34_clinical_paired_unpaired.csv",
    "phase34_clinical_severity.csv",
    # Brain (07c_v3)
    "brain_siletti_omega_pairs_v3.csv",
    "brain_siletti_ct_summary_v3.csv",
    "brain_siletti_migration_candidates_v3.csv",
    "brain_siletti_key_values_v3.csv",
    # Bootstrap (08a)
    "tcga_bootstrap_results.csv",
    # Figure data
    "omega_matrix_tissue.csv",
    "figure_data_pathways.csv",
]

KEPT_RESULTS_NPY = [
    "figure_data_auc.npy",
    "figure_data_correlations.npy",
]

KEPT_RESULTS_OTHER = [
    "phase34_clinical_plots.png",
    "phase34_clinical_report.md",
    "phase34_pam50_cache.json",
]

# --- Data files to include ---
KEPT_DATA_FILES = [
    "housekeeping/Human_Mouse_Common.csv",
    "tcga/probemap.tsv",
    "tcga/lihc_patient_clinical.json",
    "tcga/luad_egfr_kras_mutations.json",
]

# --- CKU package files ---
CKI_FILES = [
    "__init__.py",
    "core.py",
    "bootstrap.py",
    "gene_sets.py",
    "preprocess.py",
    "species.py",
    "utils.py",
    "data/__init__.py",
    "data/hrt_atlas.csv",
]

# --- Root-level scripts ---
ROOT_SCRIPTS = [
    "generate_manuscript_genome_biology.py",
    "generate_cover_letter_genome_biology.py",
]

warnings = []

with zipfile.ZipFile(CODE_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:

    def add_file(src, arcname):
        """Add file to zip; warn if missing."""
        if src.exists():
            zf.write(str(src), arcname)
        else:
            warnings.append(f"  MISSING: {src}")
            print(f"  WARNING: Missing file: {src}")

    print("  Adding cki/ package...")
    for f in CKI_FILES:
        add_file(CKI_DIR / f, f"cki/{f}")

    print("  Adding notebooks/ (10 scripts)...")
    for f in KEPT_NOTEBOOKS:
        add_file(NOTEBOOKS / f, f"notebooks/{f}")

    print("  Adding data/...")
    for f in KEPT_DATA_FILES:
        add_file(DATA_DIR / f, f"data/{f}")

    print("  Adding results/ CSVs...")
    for f in KEPT_RESULTS_CSVS:
        add_file(RESULTS / f, f"results/{f}")

    print("  Adding results/ .npy...")
    for f in KEPT_RESULTS_NPY:
        add_file(RESULTS / f, f"results/{f}")

    print("  Adding results/ other...")
    for f in KEPT_RESULTS_OTHER:
        add_file(RESULTS / f, f"results/{f}")

    print("  Adding root scripts...")
    for f in ROOT_SCRIPTS:
        add_file(PROJECT_ROOT / f, f)

    print("  Adding guide + metadata...")
    add_file(RESULTS / "CKI_Reproducibility_Guide_v1.docx", "CKI_Reproducibility_Guide_v1.docx")
    add_file(PROJECT_ROOT / "README.md", "README.md")
    add_file(PROJECT_ROOT / "pyproject.toml", "pyproject.toml")

    # Add version file
    version_info = f"CKI Reproducibility Code {VERSION}\nBuilt: {SUBMIT_DATE}\n"
    version_info += f"Based on CKI v0.3.1\n"
    version_info += f"Target journal: Genome Biology\n"
    zf.writestr("VERSION.txt", version_info)

code_size_mb = CODE_ZIP.stat().st_size / (1024 * 1024)
print(f"  Code package: {CODE_ZIP.name} ({code_size_mb:.1f} MB)")

# ============================================================
# PART 2: Build Submission Package v13
# ============================================================

SUBMIT_ZIP = RESULTS / "CKI_GenomeBiology_Submission_v13.zip"
VERSION_NUM = "v13"

print(f"\n=== Building CKI Genome Biology Submission {VERSION_NUM} ===")

SUBMIT_FILES = {
    "Main manuscript": "CKI_GenomeBiology_Manuscript_v1.docx",
    "Cover letter":    "CKI_GenomeBiology_Cover_Letter_v2.docx",
    "Supplementary tables": "CKI_Supplementary_Tables_v1.docx",
    "Reproducibility code": "CKI_Reproducibility_Code_v4.zip",
    "Reproducibility guide": "CKI_Reproducibility_Guide_v1.docx",
}

# Figures (in results/figures_final/)
FIG_DIR = RESULTS / "figures_final"
FIGURES = {
    "figure1_concept_pipeline.pdf":            "figure1_concept_pipeline.pdf",
    "figure2_calibration_tabula_muris.pdf":     "figure2_calibration_tabula_muris.pdf",
    "figure3_orthogonal_information.pdf":       "figure3_orthogonal_information.pdf",
    "figure4_tcga_pancancer.pdf":               "figure4_tcga_pancancer.pdf",
    "figure5_cross_organ_conservation.pdf":     "figure5_cross_organ_conservation.pdf",
    "figure6_brain_regional_cki.pdf":           "figure6_brain_regional_cki.pdf",
    "ed_fig1_parameter_sweep_pathway.pdf":      "ed_fig1_parameter_sweep_pathway.pdf",
    "ed_fig2_cross_species_validation.pdf":     "ed_fig2_cross_species_validation.pdf",
    "ed_fig3_tcga_per_cancer.pdf":              "ed_fig3_tcga_per_cancer.pdf",
    "ed_fig4_method_comparison_auc.pdf":        "ed_fig4_method_comparison_auc.pdf",
    "ed_fig5_cross_organ_table.pdf":            "ed_fig5_cross_organ_table.pdf",
    "ed_fig6_brain_analysis.pdf":               "ed_fig6_brain_analysis.pdf",
    "ed_fig7_migration_candidates.pdf":         "ed_fig7_migration_candidates.pdf",
}

with zipfile.ZipFile(SUBMIT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for label, fname in SUBMIT_FILES.items():
        src = RESULTS / fname
        if label == "Reproducibility code":
            src = CODE_ZIP  # the v4 code zip we just built
        add_file(src, fname)
        if not src.exists():
            warnings.append(f"  SUBMIT MISSING: {fname}")

    for arcname, fname in FIGURES.items():
        src = FIG_DIR / fname
        add_file(src, arcname)

    zf.writestr("MANIFEST_v13.txt", f"CKI Genome Biology Submission {VERSION_NUM}\n"
               f"Built: {SUBMIT_DATE}\n"
               f"Target: Genome Biology (Springer Nature / BioMed Central)\n")

submit_size_mb = SUBMIT_ZIP.stat().st_size / (1024 * 1024)
print(f"  Submission package: {SUBMIT_ZIP.name} ({submit_size_mb:.1f} MB)")

# ============================================================
# Summary
# ============================================================
if warnings:
    print(f"\n  WARNINGS ({len(warnings)}):")
    for w in warnings:
        print(w)

print(f"\n=== Done ===")
print(f"  Code:      {CODE_ZIP}")
print(f"  Submission: {SUBMIT_ZIP}")
print(f"  Code size: {code_size_mb:.1f} MB")
print(f"  Submit size: {submit_size_mb:.1f} MB")
