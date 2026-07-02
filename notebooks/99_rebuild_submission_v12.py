"""Rebuild CKI GenomeBiology submission package v12.

Includes all fixes from cross-audit + reproducibility feedback:
- 02_ct_pilot.py: fixed fname->fname typo (line 72)
- 04_phase32_sweep.py: fixed fname->fname typo (line 69)
- CKI_Reproducibility_Guide.md: added Section 3.3 (script-to-results mapping)
- generate_manuscript_genome_biology.py: all numeric corrections (TCGA counts,
  pair counts 4851/59, cross-organ r range, Conclusions omega=1.54)
- CKI_Reproducibility.ipynb: combined notebook (11 scripts -> 1 .ipynb)
"""
import zipfile, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"

# ============================================================================
# Step 1: Regenerate manuscript DOCX with latest fixes
# ============================================================================
print("=" * 60)
print("Regenerating manuscript DOCX...")
print("=" * 60)

import subprocess, sys
py = str(ROOT / "cki_env/Scripts/python.exe") if (ROOT / "cki_env").exists() else "python"
rc = subprocess.call([py, str(ROOT / "generate_manuscript_genome_biology.py")])
if rc != 0:
    print("WARNING: manuscript regeneration returned non-zero, trying default python...")
    rc2 = subprocess.call([sys.executable, str(ROOT / "generate_manuscript_genome_biology.py")])
    print(f"  Return code: {rc2}")

# ============================================================================
# Step 2: Build reproducibility code zip v3
# ============================================================================
print("\n" + "=" * 60)
print("Building CKI_Reproducibility_Code_v3.zip...")
print("=" * 60)

CODE_FILES = {
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
        "02_ct_pilot.py",          # v0.3.2: fixed fname typo
        "02b_pilot_v2.py",
        "02c_pilot_v2b.py",
        "03_full_matrix.py",
        "04_phase32_sweep.py",    # v0.3.2: fixed fname typo
        "05_phase33_v3_fixed.py",
        "06_phase34_v2.py",
        "07_phase34_clinical.py",
        "07c_brain_siletti_v3.py",
        "08a_tcga_bootstrap.py",
        "13_phase35_method_comparison.py",
        "30_genome_biology_figures.py",
        "build_combined_notebook.py",
    ],
}

# Results CSVs (all 33 files)
RESULTS_FILES = [
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
    "phase34_v2_all_pairs.csv",
    "phase34_v2_summary.csv",
    "phase34_v2_TCGA-BRCA_pairs.csv",
    "phase34_v2_TCGA-KIRC_pairs.csv",
    "phase34_v2_TCGA-LIHC_pairs.csv",
    "phase34_v2_TCGA-LUAD_pairs.csv",
    "phase34_v2_TCGA-LUSC_pairs.csv",
    "phase34_clinical_paired_unpaired.csv",
    "phase34_clinical_severity.csv",
    "phase35_all_metrics_pairs.csv",
    "phase35_cross_organ_conservation.csv",
    "phase35_metric_correlation.csv",
    "tcga_bootstrap_results.csv",
    # sweep results (fixed, do not re-run)
    "phase32_sweep_results.csv",
    "phase32_pathway_scores.csv",
]

# Data files
DATA_FILES = {
    ROOT / "data/housekeeping": ["Human_Mouse_Common.csv"],
    ROOT / "data/tcga": [
        "probemap.tsv",
        "lihc_patient_clinical.json",
        "luad_egfr_kras_mutations.json",
    ],
}

code_zip_path = RESULTS / "CKI_Reproducibility_Code_v3.zip"
missing = []
total_files = 0

with zipfile.ZipFile(code_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:

    # CKI package
    for base_dir, fnames in CODE_FILES.items():
        for fname in fnames:
            if base_dir == ROOT:
                src = ROOT / fname
                arc = fname
            else:
                src = base_dir / fname
                arc = str(src.relative_to(ROOT))
            if src.exists():
                zf.write(src, arc)
                total_files += 1
            else:
                missing.append(str(src))

    # Results CSVs
    for fname in RESULTS_FILES:
        src = RESULTS / fname
        arc = f"results/{fname}"
        if src.exists():
            zf.write(src, arc)
            total_files += 1
        else:
            missing.append(str(src))

    # Data files
    for base_dir, fnames in DATA_FILES.items():
        for fname in fnames:
            src = base_dir / fname
            arc = str(src.relative_to(ROOT))
            if src.exists():
                zf.write(src, arc)
                total_files += 1
            else:
                missing.append(str(src))

    # Reproducibility guide (MD + DOCX)
    for guide_file in ["CKI_Reproducibility_Guide.md", "CKI_Reproducibility_Guide.docx"]:
        src = RESULTS / guide_file
        if src.exists():
            zf.write(src, guide_file)
            total_files += 1
        else:
            missing.append(str(src))

    # Combined notebook
    ipynb = RESULTS / "CKI_Reproducibility.ipynb"
    if ipynb.exists():
        zf.write(ipynb, "CKI_Reproducibility.ipynb")
        total_files += 1

    # Generate scripts
    for gen_script in ["generate_manuscript_genome_biology.py", "generate_cover_letter_genome_biology.py"]:
        src = ROOT / gen_script
        if src.exists():
            zf.write(src, gen_script)
            total_files += 1

if missing:
    print(f"\nWARNING: {len(missing)} file(s) not found:")
    for m in missing:
        print(f"  - {m}")

code_size = code_zip_path.stat().st_size
print(f"\nCode zip v3: {total_files} files, {code_size:,} bytes ({code_size/1024/1024:.1f} MB)")

# ============================================================================
# Step 3: Build submission package v12
# ============================================================================
print("\n" + "=" * 60)
print("Building CKI_GenomeBiology_Submission_v12.zip...")
print("=" * 60)

submission_zip = RESULTS / "CKI_GenomeBiology_Submission_v12.zip"
FIGURES = RESULTS / "figures_final"

SUBMISSION_FILES = [
    # Manuscript & Cover Letter
    (RESULTS / "CKI_GenomeBiology_Manuscript_v1.docx", "CKI_GenomeBiology_Manuscript_v1.docx"),
    (RESULTS / "CKI_GenomeBiology_Cover_Letter_v2.docx", "CKI_GenomeBiology_Cover_Letter_v2.docx"),

    # Supplementary materials
    (RESULTS / "CKI_Supplementary_Tables_v1.docx", "CKI_Supplementary_Tables_v1.docx"),
    (code_zip_path, "CKI_Reproducibility_Code_v3.zip"),

    # Reproducibility guide
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
print(f"\nSubmission zip v12: {sub_size:,} bytes ({sub_size/1024/1024:.1f} MB)")
print(f"Saved: {submission_zip}")

print("\n" + "=" * 60)
print("SUMMARY of v12 changes vs v11")
print("=" * 60)
print("- 02_ct_pilot.py: fixed fname->fname typo")
print("- 04_phase32_sweep.py: fixed fname->fname typo")
print("- CKI_Reproducibility_Guide.md: added Section 3.3 (script-to-results mapping)")
print("- CKI_Reproducibility.ipynb: added (combined notebook)")
print("- Manuscript: all numeric corrections applied")
print(f"\nPaths:")
print(f"  Submission:  {submission_zip}")
print(f"  Reproducibility code: {code_zip_path}")
print("Done!")
