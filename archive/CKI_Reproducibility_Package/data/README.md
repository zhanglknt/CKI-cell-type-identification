# Data Download Guide

The raw data files are NOT included in this reproducibility package due to size constraints.
Download them from the sources below and place them in this `data/` directory.

## Required Directory Structure

After downloading, your `data/` directory should look like:

```
data/
├── ts_human/
│   ├── TS_Liver.h5ad
│   ├── TS_Kidney.h5ad
│   ├── TS_Heart.h5ad
│   ├── TS_Bone_Marrow.h5ad
│   ├── TS_Spleen.h5ad
│   └── TS_Lung.h5ad
├── FACS/
│   └── FACS/
│       ├── annotations_FACS.csv
│       └── metadata_FACS.csv
├── brain/
│   └── Nonneurons.h5ad
├── tcga/
│   ├── tcga_RSEM_gene_tpm.gz
│   └── probemap.tsv
└── housekeeping/
    └── Human_Mouse_Common.csv
```

## Data Sources

### 1. Tabula Muris (Mouse) — FACS data
- **Download**: https://figshare.com/articles/dataset/Single-cell_RNA-seq_data_from_Tabula_Muris/5829687
- Files: FACS .h5ad files, annotations_FACS.csv, metadata_FACS.csv
- After downloading, place .h5ad files under `data/FACS/FACS/`

### 2. Tabula Sapiens (Human)
- **Download**: https://tabula-sapiens-portal.ds.czbiohub.org/
- Files: TS_Liver.h5ad, TS_Kidney.h5ad, TS_Heart.h5ad, TS_Bone_Marrow.h5ad, TS_Spleen.h5ad, TS_Lung.h5ad
- Place in `data/ts_human/`

### 3. Brain — Siletti Atlas
- **Download**: https://www.science.org/doi/10.1126/science.add7046
- File: Nonneurons.h5ad (~4 GB)
- Place in `data/brain/`

### 4. TCGA Expression Data (Optional)
- **Download**: https://gdc.cancer.gov/about-data/publications/pancanatlas
- File: tcga_RSEM_gene_tpm.gz
- Place in `data/tcga/`
- Note: TCGA analysis can be skipped with `python run_all.py --skip-tcga`

### 5. Housekeeping Gene Reference
- **Download**: https://housekeeping.unicamp.br/
- File: Human_Mouse_Common.csv
- Place in `data/housekeeping/`

## Quick Start (Minimal)

To reproduce core results without TCGA (controlled-access data):

```bash
pip install -e .
python run_all.py --skip-tcga
```

This requires at minimum: Tabula Muris, Tabula Sapiens, Brain, and Housekeeping data.
