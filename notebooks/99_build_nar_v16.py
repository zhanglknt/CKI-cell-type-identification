#!/usr/bin/env python3
"""Build CKI NAR Submission v16 ZIP package.

Uses regenerated DOCX files (manuscript, supplementary, cover letter, repro guide,
Table1-2) and the optimized Graphical Abstract. Figure PDFs are reused from the
v15 package (high-quality version) because the current figures_final/ copies are
corrupted/low-quality placeholders.
"""
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS = PROJECT_ROOT / "results"
FIGURES_V15 = PROJECT_ROOT / "version3" / "v16_figures" / "CKI_NAR_Submission_v15"
VERSION = "v16"
SUBMIT_DIR = f"CKI_NAR_Submission_{VERSION}"
SUBMIT_DATE = datetime.now().strftime("%Y-%m-%d")

# Regenerated DOCX files
SUBMIT_FILES = [
    (RESULTS / "CKI_NAR_Manuscript.docx", "CKI_NAR_Manuscript.docx"),
    (RESULTS / "CKI_NAR_Supplementary.docx", "CKI_NAR_Supplementary.docx"),
    (RESULTS / "CKI_NAR_Cover_Letter.docx", "CKI_NAR_Cover_Letter.docx"),
    (RESULTS / "CKI_NAR_Reproducibility_Guide.docx", "CKI_NAR_Reproducibility_Guide.docx"),
    (RESULTS / "Table1-2.docx", "Table1-2.docx"),
]

# Figure PDFs reused from v15 package (high-quality)
FIGURE_FILES = [
    "figure1.pdf",
    "figure2.pdf",
    "figure3.pdf",
    "figure4.pdf",
    "figure5.pdf",
    "figure6.pdf",
    "Supplementary_Figure_S1.pdf",
    "Supplementary_Figure_S2.pdf",
    "Supplementary_Figure_S3.pdf",
    "Supplementary_Figure_S4.pdf",
    "Supplementary_Figure_S5.pdf",
]

# Graphical Abstract files (newly optimized)
GRAPHICAL_ABSTRACT = [
    (RESULTS / "figures_final" / "CKI_graphical_abstract.png", "CKI_graphical_abstract.png"),
    (RESULTS / "figures_final" / "CKI_graphical_abstract.pdf", "CKI_graphical_abstract.pdf"),
    (RESULTS / "figures_final" / "CKI_graphical_abstract.svg", "CKI_graphical_abstract.svg"),
]


def main():
    zip_path = RESULTS / f"CKI_NAR_Submission_{VERSION}.zip"
    warnings = []

    print(f"=== Building CKI NAR Submission {VERSION} ===")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # DOCX files
        for src, arcname in SUBMIT_FILES:
            full_arcname = f"{SUBMIT_DIR}/{arcname}"
            if src.exists():
                zf.write(src, full_arcname)
                print(f"  + {full_arcname}  ({src.stat().st_size/1024:.1f} KB)")
            else:
                warnings.append(f"MISSING: {full_arcname}")
                print(f"  ! MISSING: {full_arcname}")

        # Figure PDFs (from v15 high-quality set)
        for arcname in FIGURE_FILES:
            src = FIGURES_V15 / arcname
            full_arcname = f"{SUBMIT_DIR}/{arcname}"
            if src.exists():
                zf.write(src, full_arcname)
                print(f"  + {full_arcname}  ({src.stat().st_size/1024:.1f} KB)")
            else:
                warnings.append(f"MISSING: {full_arcname}")
                print(f"  ! MISSING: {full_arcname}")

        # Graphical Abstract (new optimized version)
        for src, arcname in GRAPHICAL_ABSTRACT:
            full_arcname = f"{SUBMIT_DIR}/{arcname}"
            if src.exists():
                zf.write(src, full_arcname)
                print(f"  + {full_arcname}  ({src.stat().st_size/1024:.1f} KB)")
            else:
                warnings.append(f"MISSING: {full_arcname}")
                print(f"  ! MISSING: {full_arcname}")

        # Manifest
        manifest = f"""CKI NAR Submission Package {VERSION}
Built: {SUBMIT_DATE}

This package contains the final NAR submission materials after resolving all
P0 Critical contradictions identified in the v15 expert review (4 reviewers).

Contents:
1. CKI_NAR_Manuscript.docx - Main manuscript (English)
2. CKI_NAR_Supplementary.docx - Supplementary materials (English)
3. CKI_NAR_Cover_Letter.docx - Cover letter with 6 suggested reviewers
4. CKI_NAR_Reproducibility_Guide.docx - Computational reproducibility guide
5. Table1-2.docx - Standalone tables extracted from manuscript
6. figure1.pdf through figure6.pdf - Main figures
7. Supplementary_Figure_S1.pdf through Supplementary_Figure_S5.pdf - Supplementary figures
8. CKI_graphical_abstract.png/pdf/svg - Graphical Abstract (300 DPI, NAR-compliant)

Key fixes in v16:
- Unified terminology: baseline/functional divergence rate throughout all documents
- Corrected bootstrap scope: B=500 only for mouse pilot; descriptive statistics for human/TCGA/brain
- Fixed TCGA log2 transformation: log2(TPM + 0.001)
- Corrected software versions: Python 3.13.12, CKI v0.3.1
- Added k_f selection-bias discussion and TOST calibration note in manuscript
- Updated Graphical Abstract: arrow placement, step labels, balanced layout, readable text
- Reproducibility Guide synchronized with manuscript/supplementary methods

Note: Figure PDFs are reused from the v15 high-quality set. The current
figures_final/ copies in the working directory are low-quality placeholders.
"""
        zf.writestr(f"{SUBMIT_DIR}/MANIFEST_{VERSION}.txt", manifest)
        print(f"  + {SUBMIT_DIR}/MANIFEST_{VERSION}.txt")

    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"\n  Submission zip: {zip_path.name} ({zip_size_mb:.1f} MB)")
    if warnings:
        print(f"  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"    {w}")
    else:
        print("  No warnings.")
    print(f"\n=== Done ===")


if __name__ == "__main__":
    main()
