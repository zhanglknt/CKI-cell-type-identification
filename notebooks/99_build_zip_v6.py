"""Build CKI NAR Submission v6 ZIP package.
Updates Fig.6, ED Fig.6, ED Fig.7 with real-data versions.
"""
import zipfile
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures_final"

# All files to include with their source paths and archive names
FILES = [
    # --- Manuscript & Cover Letter ---
    (RESULTS / "CKI_NAR_Manuscript_v4.docx", "CKI_NAR_Manuscript_v4.docx"),
    (RESULTS / "CKI_NAR_Cover_Letter.docx", "CKI_NAR_Cover_Letter.docx"),

    # --- Reproducibility ---
    (RESULTS / "reproducibility_doc_v1.md", "reproducibility_doc_v1.md"),

    # --- Analysis Reports ---
    (RESULTS / "brain_siletti_analysis_report_v3.md", "brain_siletti_analysis_report_v3.md"),
    (RESULTS / "phase33_v3_report.md", "phase33_v3_report.md"),
    (RESULTS / "phase34_v2_report.md", "phase34_v2_report.md"),

    # --- Data (CSV) ---
    (RESULTS / "brain_siletti_omega_pairs_v3.csv", "brain_siletti_omega_pairs_v3.csv"),
    (RESULTS / "brain_siletti_ct_summary_v3.csv", "brain_siletti_ct_summary_v3.csv"),
    (RESULTS / "brain_siletti_migration_candidates_v3.csv", "brain_siletti_migration_candidates_v3.csv"),

    # --- CKI Package Source ---
    (ROOT / "cki" / "__init__.py", "cki/__init__.py"),
    (ROOT / "cki" / "core.py", "cki/core.py"),
    (ROOT / "cki" / "utils.py", "cki/utils.py"),
    (ROOT / "cki" / "bootstrap.py", "cki/bootstrap.py"),

    # --- Notebooks ---
    (ROOT / "notebooks" / "05_phase33_v3_fixed.py", "notebooks/05_phase33_v3_fixed.py"),
    (ROOT / "notebooks" / "06_phase34_v2.py", "notebooks/06_phase34_v2.py"),
    (ROOT / "notebooks" / "07c_brain_siletti_v3.py", "notebooks/07c_brain_siletti_v3.py"),
]

# Figure files (PNG + PDF pairs)
FIGURE_FILES = [
    "figure1_concept_pipeline",
    "figure2_calibration_tabula_muris",
    "figure3_orthogonal_information",
    "figure4_tcga_pancancer",
    "figure5_cross_organ_conservation",
    "figure6_brain_regional_cki",
    "ed_fig1_parameter_sweep_pathway",
    "ed_fig2_cross_species_validation",
    "ed_fig3_tcga_per_cancer",
    "ed_fig4_method_comparison_auc",
    "ed_fig5_cross_organ_table",
    "ed_fig6_brain_analysis",
    "ed_fig7_migration_candidates",
    "usage_guide_en",
    "usage_guide_zh",
    "_s16_anomaly_v3",
    "_s17_brain_final",
    "_s17_migration_v3",
    "_s2_cell_states_en_v2",
]

for fname in FIGURE_FILES:
    for ext in [".png", ".pdf"]:
        src = FIGURES / f"{fname}{ext}"
        arcname = f"figures_final/{fname}{ext}"
        FILES.append((src, arcname))

# Add ed_fig3 NPZ data file
FILES.append((FIGURES / "ed_fig3_tcga_omega_matrices.npz", "figures_final/ed_fig3_tcga_omega_matrices.npz"))


def build_zip(output_path, file_list):
    """Build ZIP, reporting missing files and sizes."""
    missing = []
    sizes = {}
    for src, _ in file_list:
        if not src.exists():
            missing.append(str(src))
            sizes[str(src)] = 0
        else:
            sizes[str(src)] = src.stat().st_size

    if missing:
        print(f"\nWARNING: {len(missing)} file(s) not found:")
        for m in missing:
            print(f"  - {m}")
        print()

    total = sum(sizes.values())
    print(f"Total files: {len(file_list)} ({len(file_list) - len(missing)} found)")
    print(f"Total size: {total:,} bytes ({total/1024/1024:.1f} MB)")

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for src, arcname in file_list:
            if src.exists():
                zf.write(src, arcname)

    zip_size = output_path.stat().st_size
    print(f"ZIP size: {zip_size:,} bytes ({zip_size/1024/1024:.1f} MB)")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    output = RESULTS / "CKI_NAR_Submission_v6.zip"
    build_zip(output, FILES)

    # Also list contents for verification
    print("\n--- ZIP Contents ---")
    with zipfile.ZipFile(output, 'r') as zf:
        for info in zf.infolist():
            print(f"  {info.filename:<55} {info.file_size:>10,} bytes")
    print(f"\nTotal: {len(FILES)} entries")
