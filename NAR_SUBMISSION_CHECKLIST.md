# CKI → NAR Submission Checklist (as of 2026-05-26)

## ✅ P0 Issues (Fixed)

- [x] **Abstract**: 0 citations, 190 words ✓
- [x] **Code Availability**: GitHub URL + version + Zenodo DOI placeholder ✓
  - GitHub Release v0.2.0 created: https://github.com/zhanglknt/CKI-cell-type-identification/releases/tag/v0.2.0
  - Zenodo DOI: pending (10-30 min after Release creation)
  - **ACTION**: After Zenodo assigns DOI, update Code Availability section in manuscript
- [x] **Supplementary**: DOCX → PDF (81.5 KB, multi-page A4) ✓
- [x] **AI Disclosure**: Added to Acknowledgements ✓
- [x] **References**: 36/36 fixed — journal name italic, volume number bold ✓

## ⚠️ P1 Issues (Pending)

- [ ] **Reference format fine-tuning**: Some journal abbreviations may need verification against OUP NAR style guide
  - Current: `*eLife*, **6**, e27041.` ✓
  - Current: `*Mol. Syst. Biol.*, **15**, e8746.` ✓
  - Verify: `*Nucleic Acids Res.*` vs `*Nucleic Acids Res.*` (abbreviation format)

## 📝 P2 Issues (Optional / Nice-to-have)

- [ ] **Figure widths**: Currently 6.0-7.1" (NAR max 7.0" / 178mm)
  - `ed_fig5_cross_organ_table.pdf`: 7.10" → reduce to 7.0" 
  - Others: 6.0-6.9" → acceptable for NAR (will be resized during typesetting)
- [ ] **Data accession**: Tabula Sapiens / brain atlas are from CZ CELLxGENE (public portal), no accession needed ✓

## 📦 Submission Package

```
results/NAR_Submission_Final_v2/
├── manuscript/
│   └── CKI_NAR_Manuscript_v4.docx          ← REFERENCES FIXED (italic journal, bold volume)
├── cover_letter/
│   └── CKI_NAR_Cover_Letter.docx
├── supplementary/
│   ├── CKI_NAR_Supplementary.pdf            ← GENERATED (was DOCX)
│   └── CKI_NAR_Supplementary.docx (backup)
├── figures/
│   ├── figure1_concept_pipeline.pdf          (161mm wide)
│   ├── figure2_calibration_tabula_muris.pdf  (176mm wide)
│   ├── figure3_orthogonal_information.pdf   (156mm wide)
│   ├── figure4_tcga_pancancer.pdf          (155mm wide)
│   ├── figure5_cross_organ_conservation.pdf (153mm wide)
│   └── figure6_brain_regional_cki.pdf      (170mm wide)
├── extended_data/
│   ├── ed_fig1_parameter_sweep_pathway.pdf
│   ├── ed_fig2_cross_species_validation.pdf
│   ├── ed_fig3_tcga_per_cancer.pdf
│   ├── ed_fig4_method_comparison_auc.pdf   (88mm wide = single column ✓)
│   ├── ed_fig5_cross_organ_table.pdf       (180mm → resize to 178mm)
│   ├── ed_fig6_brain_analysis.pdf
│   └── ed_fig7_migration_candidates.pdf
└── presentation/
    ├── CKI_Lecture_2026_v4.pptx           (EN, 23 slides)
    └── CKI_Lecture_2026_v4_ZH.pptx        (ZH, 23 slides)
```

## 🚀 Next Steps (Before Submission)

1. **Wait 10-30 min** for Zenodo to harvest GitHub Release v0.2.0
2. **Get DOI** from Zenodo: https://zenodo.org/record/[id]
3. **Update manuscript** Code Availability section with real DOI
4. **Final proofread** of reference format (compare with NAR published articles)
5. **Resize `ed_fig5`** to 178mm (optional)
6. **Submit** via NAR online submission system

## 🔗 Links

- GitHub Release: https://github.com/zhanglknt/CKI-cell-type-identification/releases/tag/v0.2.0
- Zenodo (after harvest): https://doi.org/10.5281/zenodo.XXXXXXX
- NAR Submission: https://www.editorialmanager.com/nar/

