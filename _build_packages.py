"""Build submission and reproducibility packages for Genome Biology."""
import zipfile
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures_final"

VERSION = "v16"
REPRO_VERSION = "v7"
DATE_STR = datetime.now().strftime("%Y-%m-%d")

# ================================================================
# 1. Build Reproducibility Code zip
# ================================================================
print(f"=== Building CKI_Reproducibility_Code_{REPRO_VERSION}.zip ===")

repro_files = []

# cki/ package
for f in (ROOT / "cki").rglob("*"):
    if f.is_file() and "__pycache__" not in str(f):
        repro_files.append(f)

# notebooks/
for f in (ROOT / "notebooks").glob("*.py"):
    repro_files.append(f)

# data/ (small reference files only; raw .h5ad data >10 GB excluded)
data_include = [
    "data/housekeeping/Human_Mouse_Common.csv",
    "data/tcga/probemap.tsv",
    "data/tcga/lihc_patient_clinical.json",
    "data/tcga/luad_egfr_kras_mutations.json",
    "data/annotations_FACS.csv",
    "data/metadata_FACS.csv",
    "data/README_data.md",
]
for p in data_include:
    f = ROOT / p
    if f.exists():
        repro_files.append(f)

# results/ CSVs and key files
results_include_patterns = [
    "omega_matrix_tissue.csv",
    "hk_stability_sweep.csv",
    "hk_overlap_subsamples.csv",
    "phase32_sweep_results.csv",
    "phase32_pathway_scores.csv",
    "mouse_pilot_v2_results.csv",
    "mouse_pilot_v2_key_values.csv",
    "mouse_pilot_v2b_results.csv",
    "mouse_pilot_v2b_key_values.csv",
    "full_matrix_omega.csv",
    "full_matrix_kn.csv",
    "full_matrix_kf.csv",
    "full_matrix_pairs.csv",
    "phase33_v3_human_omega.csv",
    "phase33_v3_human_kn.csv",
    "phase33_v3_human_kf.csv",
    "phase33_v3_human_pairs.csv",
    "phase35_all_metrics_pairs.csv",
    "phase35_cross_organ_conservation.csv",
    "phase35_cross_organ_summary.csv",
    "phase35_metric_correlation.csv",
    "phase34_v2_summary.csv",
    "phase34_v2_all_pairs.csv",
    "phase34_v2_TCGA-BRCA_pairs.csv",
    "phase34_v2_TCGA-KIRC_pairs.csv",
    "phase34_v2_TCGA-LIHC_pairs.csv",
    "phase34_v2_TCGA-LUAD_pairs.csv",
    "phase34_v2_TCGA-LUSC_pairs.csv",
    "phase34_clinical_paired_unpaired.csv",
    "phase34_clinical_severity.csv",
    "brain_siletti_omega_pairs_v3.csv",
    "brain_siletti_ct_summary_v3.csv",
    "brain_siletti_migration_candidates_v3.csv",
    "brain_siletti_key_values_v3.csv",
    "tcga_bootstrap_results.csv",
    "human_bootstrap_results.csv",
    "brain_bootstrap_results.csv",
    "figure_data_pathways.csv",
    "figure_data_auc.npy",
    "figure_data_correlations.npy",
    "phase34_clinical_plots.png",
    "phase34_clinical_report.md",
    "phase34_pam50_cache.json",
]
for name in results_include_patterns:
    f = RESULTS / name
    if f.exists():
        repro_files.append(f)

# Key scripts
for name in ["generate_manuscript_genome_biology.py",
             "generate_cover_letter_genome_biology.py",
             "_load_manuscript_data.py",
             "_paths.py",
             "run_all.py",
             "pyproject.toml",
             "README.md"]:
    f = ROOT / name
    if f.exists():
        repro_files.append(f)

# Reproducibility Guide
f = RESULTS / "CKI_Reproducibility_Guide_v1.docx"
if f.exists():
    repro_files.append(f)

# VERSION.txt
version_path = ROOT / "VERSION.txt"
version_path.write_text(f"CKI Reproducibility Code {REPRO_VERSION}\nBuilt: {DATE_STR}\ncki package version: 0.3.1\n", encoding="utf-8")
repro_files.append(version_path)

repro_zip_path = RESULTS / f"CKI_Reproducibility_Code_{REPRO_VERSION}.zip"
with zipfile.ZipFile(repro_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in repro_files:
        arcname = str(f.relative_to(ROOT))
        zf.write(f, arcname)
        print(f"  + {arcname}")

repro_size = repro_zip_path.stat().st_size / (1024*1024)
print(f"  Reproducibility zip: {repro_size:.1f} MB, {len(repro_files)} files")

# ================================================================
# 2. Build Submission zip
# ================================================================
print(f"\n=== Building CKI_GenomeBiology_Submission_{VERSION}.zip ===")

sub_files = [
    (RESULTS / "CKI_GenomeBiology_Manuscript_v1.docx", "CKI_GenomeBiology_Manuscript_v1.docx"),
    (RESULTS / "CKI_GenomeBiology_Cover_Letter_v2.docx", "CKI_GenomeBiology_Cover_Letter_v2.docx"),
    (RESULTS / "CKI_Supplementary_Tables_v1.docx", "CKI_Supplementary_Tables_v1.docx"),
    (repro_zip_path, f"CKI_Reproducibility_Code_{REPRO_VERSION}.zip"),
    (RESULTS / "CKI_Reproducibility_Guide_v1.docx", "CKI_Reproducibility_Guide_v1.docx"),
]

# Figure PDFs (main + extended data)
figure_pdfs = sorted(FIGURES.glob("figure*.pdf")) + sorted(FIGURES.glob("ed_fig*.pdf"))
for f in figure_pdfs:
    sub_files.append((f, f.name))

# Manifest
manifest_text = f"""CKI Genome Biology Submission Package {VERSION}
Built: {DATE_STR}

Contents:
1. CKI_GenomeBiology_Manuscript_v1.docx - Main manuscript
2. CKI_GenomeBiology_Cover_Letter_v2.docx - Cover letter
3. CKI_Supplementary_Tables_v1.docx - Supplementary tables
4. CKI_Reproducibility_Code_{REPRO_VERSION}.zip - Reproducibility code and data
5. CKI_Reproducibility_Guide_v1.docx - Reproducibility guide
6. figure1_concept_pipeline.pdf
7. figure2_calibration_tabula_muris.pdf
8. figure3_orthogonal_information.pdf
9. figure4_tcga_pancancer.pdf
10. figure5_cross_organ_conservation.pdf
11. figure6_brain_regional_cki.pdf
12. ed_fig1_parameter_sweep_pathway.pdf
13. ed_fig2_cross_species_validation.pdf
14. ed_fig3_tcga_per_cancer.pdf
15. ed_fig4_method_comparison_auc.pdf
16. ed_fig5_cross_organ_table.pdf
17. ed_fig6_brain_analysis.pdf
18. ed_fig7_migration_candidates.pdf
"""
manifest_path = RESULTS / f"MANIFEST_{VERSION}.txt"
manifest_path.write_text(manifest_text, encoding="utf-8")
sub_files.append((manifest_path, f"MANIFEST_{VERSION}.txt"))

sub_zip_path = RESULTS / f"CKI_GenomeBiology_Submission_{VERSION}.zip"
with zipfile.ZipFile(sub_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for src, arcname in sub_files:
        if src.exists():
            zf.write(src, arcname)
            print(f"  + {arcname}")
        else:
            print(f"  ! MISSING: {arcname}")

sub_size = sub_zip_path.stat().st_size / (1024*1024)
print(f"\n  Submission zip: {sub_size:.1f} MB, {len(sub_files)} files")

# ================================================================
# 3. Clean up old versions
# ================================================================
print(f"\n=== Cleaning up old versions ===")

old_subs = sorted(RESULTS.glob("CKI_GenomeBiology_Submission_v*.zip"))
old_subs = [f for f in old_subs if f.name != sub_zip_path.name]
for f in old_subs:
    print(f"  Deleting old: {f.name}")
    f.unlink()

old_repros = sorted(RESULTS.glob("CKI_Reproducibility_Code_v*.zip"))
old_repros = [f for f in old_repros if f.name != repro_zip_path.name]
for f in old_repros:
    print(f"  Deleting old: {f.name}")
    f.unlink()

old_manifests = sorted(RESULTS.glob("MANIFEST_v*.txt"))
old_manifests = [f for f in old_manifests if f.name != manifest_path.name]
for f in old_manifests:
    print(f"  Deleting old: {f.name}")
    f.unlink()

# Clean temp version file
version_path.unlink()

print(f"\n=== Done! ===")
print(f"  Submission: {sub_zip_path.name} ({sub_size:.1f} MB)")
print(f"  Reproducibility: {repro_zip_path.name} ({repro_size:.1f} MB)")
