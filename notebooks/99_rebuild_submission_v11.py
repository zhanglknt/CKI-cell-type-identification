"""Rebuild CKI GenomeBiology submission package v11.

Adds missing clinical analysis files (07_phase34_clinical.py + bundled data
+ PAM50 cache + clinical outputs) to the reproducibility code zip,
then repackages the full submission.
"""
import zipfile, io, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# ============================================================================
# Step 1: Reproduce the existing code zip content, but with added clinical files
# ============================================================================

# --- existing files in code zip v1 (from inspection) ---
# these are grouped by source directory
CODE_FILES = {
    # cki package
    ROOT: [
        ".gitignore", "pyproject.toml", "README.md",
    ],
    ROOT / "cki": [
        "__init__.py", "core.py", "utils.py", "bootstrap.py",
        "gene_sets.py", "preprocess.py", "species.py",
    ],
    ROOT / "cki/data": [
        "__init__.py", "hrt_atlas.csv",
    ],
    ROOT / "notebooks": [
        "01_pilot_mouse.py",
        "02_ct_pilot.py",
        "02b_pilot_v2.py",
        "02c_pilot_v2b.py",
        "03_full_matrix.py",
        "04_phase32_sweep.py",
        "05_phase33_human.py",
        "05_phase33_v2.py",
        "05_phase33_v3.py",
        "05_phase33_v3_fixed.py",
        "05b_phase33_diagnose.py",
        "05c_phase33_diag_light.py",
        "06_phase34_tcga.py",
        "06_phase34_v2.py",
        "07_brain_siletti_analysis.py",
        "07b_brain_siletti_v2.py",
        "07c_brain_siletti_v3.py",
        "07d_brain_siletti_v4.py",
        "08a_tcga_bootstrap.py",
        "08a_tcga_permutation.py",
        "08b_human_bootstrap_csv.py",
        "08c_brain_bootstrap.py",
        "08c_brain_bootstrap_csv.py",
        "13_phase35_method_comparison.py",
        "30_genome_biology_figures.py",
        "_compute_phase35_auc.py",
        "precompute_figure_data.py",
    ],
    # Root-level scripts
    "__root_scripts__": [
        "generate_cover_letter_genome_biology.py",
        "generate_manuscript_genome_biology.py",
    ],
}

# --- NEW: clinical analysis files to add ---
CLINICAL_FILES = {
    ROOT / "notebooks": [
        "07_phase34_clinical.py",          # clinical analysis script
    ],
    ROOT / "data/tcga": [
        "lihc_patient_clinical.json",       # LIHC Edmondson grade
        "luad_egfr_kras_mutations.json",    # LUAD EGFR/KRAS mutations
        "probemap.tsv",                     # TCGA probeMap for gene mapping
    ],
    ROOT / "data/housekeeping": [
        "Human_Mouse_Common.csv",           # HK gene reference (same as cki/data/hrt_atlas.csv)
    ],
}

# Clinical output files and cache
CLINICAL_RESULTS_FILES = [
    "phase34_clinical_paired_unpaired.csv",
    "phase34_clinical_severity.csv",
    "phase34_clinical_plots.png",
    "phase34_clinical_report.md",
    "phase34_pam50_cache.json",             # BRCA PAM50 cache (CBioPortal snapshot)
]

# Results files already in code zip
RESULTS_FILES_ORIG = [
    "brain_bootstrap_results.csv",
    "brain_siletti_ct_summary_v3.csv",
    "brain_siletti_key_values_v3.csv",
    "brain_siletti_migration_candidates_v3.csv",
    "brain_siletti_omega_pairs_v3.csv",
    "figure_data_auc.npy",
    "figure_data_correlations.npy",
    "figure_data_pathways.csv",
    "full_matrix_kf.csv",
    "full_matrix_kn.csv",
    "full_matrix_omega.csv",
    "full_matrix_pairs.csv",
    "human_bootstrap_results.csv",
    "mouse_pilot_v2_key_values.csv",
    "mouse_pilot_v2_results.csv",
    "mouse_pilot_v2b_key_values.csv",
    "mouse_pilot_v2b_results.csv",
    "omega_matrix_tissue.csv",
    "phase33_v3_human_kf.csv",
    "phase33_v3_human_kn.csv",
    "phase33_v3_human_omega.csv",
    "phase33_v3_human_pairs.csv",
    "phase34_summary.csv",
    "phase34_v2_all_pairs.csv",
    "phase34_v2_summary.csv",
    "phase34_v2_TCGA-BRCA_pairs.csv",
    "phase34_v2_TCGA-KIRC_pairs.csv",
    "phase34_v2_TCGA-LIHC_pairs.csv",
    "phase34_v2_TCGA-LUAD_pairs.csv",
    "phase34_v2_TCGA-LUSC_pairs.csv",
    "phase35_all_metrics_pairs.csv",
    "phase35_cross_organ_conservation.csv",
    "phase35_metric_correlation.csv",
    "pilot_results.csv",
    "tcga_bootstrap_results.csv",
]

# CKI_Reproducibility_Guide.md
REPRO_GUIDE = RESULTS / "CKI_Reproducibility_Guide.md"

# ============================================================================
# Build code zip
# ============================================================================
print("=" * 60)
print("Building CKI_Reproducibility_Code_v2.zip...")
print("=" * 60)

code_zip_path = RESULTS / "CKI_Reproducibility_Code_v2.zip"
missing = []
total_bytes = 0

with zipfile.ZipFile(code_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:

    # Write existing code files
    for base_dir, fnames in CODE_FILES.items():
        for fname in fnames:
            if base_dir == "__root_scripts__":
                src = ROOT / fname
                arc = fname
            else:
                src = base_dir / fname
                arc = str(src.relative_to(ROOT))
            if src.exists():
                zf.write(src, arc)
                total_bytes += src.stat().st_size
            else:
                missing.append(str(src))

    # Write new clinical code + data files
    for base_dir, fnames in CLINICAL_FILES.items():
        for fname in fnames:
            src = base_dir / fname
            arc = str(src.relative_to(ROOT))
            if src.exists():
                zf.write(src, arc)
                total_bytes += src.stat().st_size
                print(f"  + ADDED: {arc}")
            else:
                missing.append(str(src))

    # Write results files (original)
    for fname in RESULTS_FILES_ORIG:
        src = RESULTS / fname
        arc = f"results/{fname}"
        if src.exists():
            zf.write(src, arc)
            total_bytes += src.stat().st_size
        else:
            missing.append(str(src))

    # Write new clinical results + PAM50 cache
    for fname in CLINICAL_RESULTS_FILES:
        src = RESULTS / fname
        arc = f"results/{fname}"
        if src.exists():
            zf.write(src, arc)
            total_bytes += src.stat().st_size
            print(f"  + ADDED: {arc}")
        else:
            missing.append(str(src))

    # Write reproducibility guide
    if REPRO_GUIDE.exists():
        zf.write(REPRO_GUIDE, "CKI_Reproducibility_Guide.md")
        total_bytes += REPRO_GUIDE.stat().st_size

if missing:
    print(f"\nWARNING: {len(missing)} file(s) not found:")
    for m in missing:
        print(f"  - {m}")

code_zip_size = code_zip_path.stat().st_size
n_entries = sum(1 for _ in zipfile.ZipFile(code_zip_path, "r").infolist())
print(f"\nCode zip: {n_entries} entries, {code_zip_size:,} bytes ({code_zip_size/1024/1024:.1f} MB)")

# ============================================================================
# Step 2: Build the full submission package v11
# ============================================================================
print("\n" + "=" * 60)
print("Building CKI_GenomeBiology_Submission_v11.zip...")
print("=" * 60)

submission_zip = RESULTS / "CKI_GenomeBiology_Submission_v11.zip"
FIGURES = RESULTS / "figures_final"

SUBMISSION_FILES = [
    # Manuscript & Cover Letter
    (RESULTS / "CKI_GenomeBiology_Manuscript_v1.docx", "CKI_GenomeBiology_Manuscript_v1.docx"),
    (RESULTS / "CKI_GenomeBiology_Cover_Letter_v2.docx", "CKI_GenomeBiology_Cover_Letter_v2.docx"),

    # Supplementary materials
    (RESULTS / "CKI_Supplementary_Tables_v1.docx", "CKI_Supplementary_Tables_v1.docx"),
    (code_zip_path, "CKI_Reproducibility_Code_v2.zip"),

    # Updated reproducibility guide as standalone doc
    (RESULTS / "CKI_Reproducibility_Guide_v1.docx", "CKI_Reproducibility_Guide_v1.docx"),

    # Main figures
    (FIGURES / "figure1_concept_pipeline.pdf", "figure1_concept_pipeline.pdf"),
    (FIGURES / "figure2_calibration_tabula_muris.pdf", "figure2_calibration_tabula_muris.pdf"),
    (FIGURES / "figure3_orthogonal_information.pdf", "figure3_orthogonal_information.pdf"),
    (FIGURES / "figure4_tcga_pancancer.pdf", "figure4_tcga_pancancer.pdf"),
    (FIGURES / "figure5_cross_organ_conservation.pdf", "figure5_cross_organ_conservation.pdf"),
    (FIGURES / "figure6_brain_regional_cki.pdf", "figure6_brain_regional_cki.pdf"),

    # Extended data figures
    (FIGURES / "ed_fig1_parameter_sweep_pathway.pdf", "ed_fig1_parameter_sweep_pathway.pdf"),
    (FIGURES / "ed_fig2_cross_species_validation.pdf", "ed_fig2_cross_species_validation.pdf"),
    (FIGURES / "ed_fig3_tcga_per_cancer.pdf", "ed_fig3_tcga_per_cancer.pdf"),
    (FIGURES / "ed_fig4_method_comparison_auc.pdf", "ed_fig4_method_comparison_auc.pdf"),
    (FIGURES / "ed_fig5_cross_organ_table.pdf", "ed_fig5_cross_organ_table.pdf"),
    (FIGURES / "ed_fig6_brain_analysis.pdf", "ed_fig6_brain_analysis.pdf"),
    (FIGURES / "ed_fig7_migration_candidates.pdf", "ed_fig7_migration_candidates.pdf"),
]

sub_missing = []
sub_total = 0
with zipfile.ZipFile(submission_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
    for src, arc in SUBMISSION_FILES:
        if src.exists():
            zf.write(src, arc)
            sub_total += src.stat().st_size
        else:
            sub_missing.append(str(src))

if sub_missing:
    print(f"\nWARNING: {len(sub_missing)} file(s) not found:")
    for m in sub_missing:
        print(f"  - {m}")

sub_size = submission_zip.stat().st_size
n_sub = sum(1 for _ in zipfile.ZipFile(submission_zip, "r").infolist())
print(f"\nSubmission zip: {n_sub} entries, {sub_size:,} bytes ({sub_size/1024/1024:.1f} MB)")
print(f"Saved: {submission_zip}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 60)
print("SUMMARY: New files added vs v10")
print("=" * 60)
for base_dir, fnames in CLINICAL_FILES.items():
    for fname in fnames:
        print(f"  notebooks/{fname}" if "notebooks" in str(base_dir) else f"  data/tcga/{fname}")
for fname in CLINICAL_RESULTS_FILES:
    print(f"  results/{fname}")
print(f"\nSubmission package: {submission_zip}")
print("Done!")
