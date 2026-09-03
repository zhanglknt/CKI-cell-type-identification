#!/usr/bin/env python3
"""Collect final figures from results/figures_final into submission-ready names.

Maps:
  figure[1-6].pdf                         <- *_clean.py outputs
  Supplementary_Figure_S[1-12].pdf        <- ed_fig* + dedicated S6/S7 outputs
  CKI_graphical_abstract.{png,pdf,svg}    <- results/figures_final

Run from repo root after all figure scripts have completed.
"""
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "results" / "figures_final"

# target_name -> source_name (without .pdf extension)
MAIN_FIGURES = {
    "figure1": "figure1_concept_pipeline",
    "figure2": "figure2_calibration_tabula_muris",
    "figure3": "figure3_orthogonal_information",
    "figure4": "figure4_tcga_pancancer",
    "figure5": "figure5_cross_organ_conservation",
    "figure6": "figure6_brain_regional_cki",
}

SUPPLEMENTARY_FIGURES = {
    "Supplementary_Figure_S1": "ed_fig1_parameter_sweep_pathway",
    "Supplementary_Figure_S2": "ed_fig12_calibrated_omega",
    "Supplementary_Figure_S3": "ed_fig4_method_comparison_auc",
    "Supplementary_Figure_S4": "ed_fig3_tcga_per_cancer",
    "Supplementary_Figure_S5": "ed_fig5_cross_organ_table",
    "Supplementary_Figure_S6": "Supplementary_Figure_S6",   # dedicated script
    "Supplementary_Figure_S7": "ed_fig11_kn_variability",
    "Supplementary_Figure_S8": "Supplementary_Figure_S8",   # dedicated script
    "Supplementary_Figure_S9": "ed_fig9_residual_null",
    "Supplementary_Figure_S10": "ed_fig2_cross_species_validation",
    "Supplementary_Figure_S11": "ed_fig8_omega_distribution",
    "Supplementary_Figure_S12": "ed_fig10_dimensionality",
}


def collect(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    missing = []
    copied = []

    for target_name, src_name in {**MAIN_FIGURES, **SUPPLEMENTARY_FIGURES}.items():
        src_pdf = SRC_DIR / f"{src_name}.pdf"
        target_pdf = target_dir / f"{target_name}.pdf"
        if src_pdf.exists():
            shutil.copy2(src_pdf, target_pdf)
            copied.append(target_name)
        else:
            missing.append(str(src_pdf))

    for ext in ("png", "pdf", "svg"):
        src_ga = SRC_DIR / f"CKI_graphical_abstract.{ext}"
        target_ga = target_dir / f"CKI_graphical_abstract.{ext}"
        if src_ga.exists():
            shutil.copy2(src_ga, target_ga)
            copied.append(f"GA {ext}")
        else:
            missing.append(str(src_ga))

    print(f"  Figures collected: {len(copied)}")
    if missing:
        print(f"  MISSING: {len(missing)} files")
        for m in missing:
            print(f"    - {m}")
        return False
    return True


if __name__ == "__main__":
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / "results" / "figures_submission"
    ok = collect(target_dir)
    sys.exit(0 if ok else 1)
