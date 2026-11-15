CKI-cell-type-identification — Data Guide
==========================================

This file describes the data used by the CKI analyses and where each
artifact lives. Large raw datasets are **not** bundled in the repository;
they must be downloaded from the public sources below.

## Raw data sources

| Dataset | Source | Notes |
|---------|--------|-------|
| Tabula Muris (FACS) | https://github.com/czbiohub-sf/tabula-muris (data also mirrored on figshare) | Public download; also on figshare / Zenodo |
| Tabula Sapiens | https://tabula-sapiens-portal.ds.czbiohub.org/ | Public download (~58.9 GB, 6 h5ad files) |
| Siletti et al. brain atlas (Nonneurons + Neurons) | CELLxGENE: https://cellxgene.cziscience.com/ | See Siletti et al., Science 2023 for collection links |
| TCGA bulk RNA-seq (TPM) | UCSC Xena (https://xenabrowser.net/) / GDC https://portal.gdc.cancer.gov/ | Bulk TPM matrices for the five analyzed cancers |
| HRT Atlas v1.0 (HK genes) | https://www.housekeeping.unicamp.br/ | A copy of the human/mouse common HK gene list ships with the package at `cki/data/hrt_atlas.csv` |
| Kang et al. IFN-beta PBMC (GSE96583) | GEO: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE96583 | Download `GSE96583_RAW.tar`, `GSE96583_genes.txt.gz` and the batch2 tsne/metadata files into `data/kang_ifnb/` (exact expected files: header of `notebooks/79_kang_ifnb_demo.py`) |
| Human Brain Cell Atlas v1.0, Microglia supercluster | CELLxGENE collection 283d65eb-dd53-496d-adb7-7570c7caa443: https://cellxgene.cziscience.com/ | `data/human_brain_atlas_microglia.h5ad` (91,838 nuclei); nc50 microglia independent validation (`notebooks/nc50_brain_atlas_microglia.py`) |

## Processed data

Processed outputs (pseudobulk matrices, omega pair matrices, figure source
data) are archived in the repository under `results/` and in the Zenodo
record (concept DOI: 10.5281/zenodo.20405458), and in the GitHub release:

**https://github.com/zhanglknt/CKI-cell-type-identification/releases/tag/v0.5.0**

## Analysis notebooks

All analysis scripts are in `notebooks/`. The main-figure pipeline is:

- `01_pilot_mouse.py`, `02b_pilot_v2.py`, `02c_pilot_v2b.py` — Tabula Muris
  pilot + split-half calibration (Phase 3.1)
- `03_full_matrix.py` — mouse full pair matrix (703 pairs)
- `05_phase33_v3.py` — Tabula Sapiens analysis (Phase 3.3)
- `06_phase34_tcga.py`, `06_phase34_v2.py` — TCGA tumor–normal analysis (Phase 3.4)
- `07d_brain_siletti_v4.py` — Siletti brain atlas landscape
- `08d_brain_blockshuffle_null.py`, `08e_brain_blockshuffle_results.py` —
  brain block-shuffle null
- `13_phase35_method_comparison.py` — 4,851-pair, 5-metric comparison (Phase 3.5)
- `45_groundtruth_simulation.py` — semi-synthetic ground-truth simulation
- `46_fixed_panel_ablation.py` — fixed gene-panel circularity ablation
- `30_genome_biology_figures.py` — earlier main/supplementary figure generation
- `nc49_fig_drift_ladder.py` — Fig. 3 (drift ladder)
- `nc49_fig_tcga.py` — Fig. 4 (TCGA per-sample statistics)
- `nc50_fig_microglia.py` — Supplementary Fig. 14 (microglia validation)

See `run_all.py` for the end-to-end orchestration entry point
(`--dry-run`, `--skip-tcga`, `--verify-only`).

## Environment

Dependencies are declared in `pyproject.toml` (install with
`pip install -e .`) and listed in `requirements.txt`. The package
requires Python >= 3.10; CI tests Python 3.10–3.13.
There is no `environment.yml` — use the pip route above.

## Reproducibility

All analyses use random seed 42, with four fixed exceptions (matching the
Reproducibility Guide Section 1.4 and Supplementary Information 5.13):
`notebooks/77_pseudoregion_control.py`, `78_axis_permutation_test.py` and
`79_kang_ifnb_demo.py` use the fixed seed 20260903 (77 additionally uses a
permutation-base seed of 777000), `notebooks/89_cluster_boot_v45.py` uses the
fixed seed 20260905, and the ground-truth simulation module-sensitivity
analyses additionally use module seeds 137 and 2024 besides 42
(`notebooks/45_groundtruth_simulation.py`, `49_groundtruth_sim_background2.py`).
All seeds are hard-coded in the scripts.
