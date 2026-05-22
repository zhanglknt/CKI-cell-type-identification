
CKI-cell-type-identification
================================

## Data availability

### Raw data sources

| Dataset | Source | Access |
|----------|--------|--------|
| Tabula Muris (FACS) | https://tabula-muris.ds.czbiohub.com/ | Public download |
| Tabula Sapiens | https://tabula-sapiens.single-cell.czip.org/ | Public download (58.87 GB) |
| TCGA bulk RNA-seq | https://portal.gdc.cancer.gov/ | GDC Data Portal, controlled access for some cohorts |
| HRT Atlas v1.0 (HK genes) | https://hrt-atlas.org/ | Public |

### Processed data

Processed data (pseudobulk matrices, omega matrices, figure source data) are available at:  
**https://github.com/knightz/CKI-cell-type-identification/releases**

### Notebooks to reproduce all results

All analysis notebooks are in `notebooks/`:
- `01_pilot_mouse.py` — Phase 3.1 pilot (Tabula Muris FACS)
- `03_full_matrix.py` — Phase 3.1 full (703 pairs)
- `05_phase33_human.py` — Phase 3.3 (Tabula Sapiens)
- `06_phase34_tcga.py` — Phase 3.4 (TCGA tumor-normal)
- `13_phase35_method_comparison.py` — Phase 3.5 (4,851 pairs, 5-metric comparison)

### Reproducibility

All random seeds are fixed (`random_state=42`).  
Package versions are pinned in `environment.yml`.
