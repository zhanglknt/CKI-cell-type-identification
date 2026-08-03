# CKI Reproducibility Package

**Cell-state Kinetic Index (CKI)** — A Ka/Ks-inspired framework for quantifying selective transcriptomic remodeling.

Version: 0.3.2 | Manuscript target: Nucleic Acids Research (NAR)

## What This Package Contains

This package provides all code needed to **fully reproduce** the CKI manuscript results:

- `cki/` — Core CKI algorithm (v0.3.2)
- `notebooks/` — 24 analysis scripts (Phase 1-6 pipeline + figure generation)
- `run_all.py` — One-command reproducibility pipeline
- `generate_manuscript_nar.py` — Manuscript generation
- `generate_cover_letter_nar.py` — Cover letter generation

## Quick Start

```bash
# 1. Install CKI
pip install -e .

# 2. Download data (see data/README.md)

# 3. Run full pipeline (skip TCGA for open-access reproducibility)
python run_all.py --skip-tcga

# 4. Generate manuscript
python generate_manuscript_nar.py

# 5. Generate supplementary materials
python notebooks/68_gen_supplementary_en.py

# 6. Generate reproducibility guide
node notebooks/100_gen_reproducibility_docx.js
```

## Pipeline Overview

| Phase | Group | Scripts | Description |
|---|---|---|---|
| 1 | A | 01b-04 | Tabula Muris FACS (mouse) |
| 1 | B | 05 | Tabula Sapiens (human) |
| 1 | C | 06-07 | TCGA (optional) |
| 1 | D | 07c | Brain Siletti Atlas |
| 1 | F | 13 | Method comparison |
| 2 | E | 08a-c | Bootstrap (B=1000) |
| 3 | — | precompute, spot_check | Figure data + verification |
| 4 | Phase B | 09, 09b | Statistical upgrades |
| 5 | Phase C | 09c | Methodological reinforcement |
| 6 | — | 30 | Main + Supplementary figures |

## Requirements

- Python >= 3.10
- Node.js >= 18 (for reproducibility guide generation only)
- Dependencies listed in `requirements.txt`

## Key Parameters

- TS pairs: 5,151 (102 cell types)
- Brain regions: 108
- Normalization: normalize_total + log1p (pseudobulk)
- Bootstrap: B=1,000
- P-value: one-sided permutation test, BH FDR per-dataset
- HK genes: auto-detected (combined criterion)
- HVG flavor: seurat (2,000)
- Omega baseline: 6.67 (empirical calibration)

## Data Availability

Raw data download instructions: see `data/README.md`

## Citation

Li Zhang, Xianming Wu. CKI: Cell-state Kinetic Index — A Ka/Ks-inspired framework for quantifying selective transcriptomic remodeling. *Nucleic Acids Research*, 2026.

## License

MIT
