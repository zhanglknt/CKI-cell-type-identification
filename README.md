# CKI: Cell-type Identity Index

A Ka/Ks-inspired framework for quantifying baseline-normalized transcriptomic remodeling in single-cell RNA-seq data.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-CKI_cell_type_identification-181717)](https://github.com/zhanglknt/CKI-cell-type-identification)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20405458.svg)](https://doi.org/10.5281/zenodo.20405458)

## Overview

CKI (Cell-type Identity Index) operationalizes the Ka/Ks concept from molecular evolution at the single-cell transcriptomic level. By decomposing gene expression into housekeeping (neutral) and functional (identity) components and computing their Jensen-Shannon divergence ratio, CKI quantifies baseline-normalized transcriptomic divergence between any two cell populations.

## Key Findings

CKI was validated on four independent datasets totaling millions of cells:

| Dataset | Pairs | Result | P-value |
|---|---|---|---|
| Mouse (Tabula Muris) | 703 | 8/15 cell types significant | FDR < 0.05 |
| Human (Tabula Sapiens) | 4,851 | 16/17 cell types significant | P = 9.99e-04 |
| TCGA (BRCA/KIRC/LIHC/LUAD/LUSC) | — | Exploratory convergence analysis | Descriptive |
| Brain (Siletti Atlas) | 31,764 | 8/10 cell classes significant; 0/31,764 pairs survive FDR | Block-shuffle null, B = 1,000 |

Sources: mouse — `results/full_matrix_pairs.csv` (703 pairs) and
`results/mouse_pilot_v2b_results.csv` (8/15 pilot comparisons pass BH q < 0.05);
human — `results/phase35_all_metrics_pairs.csv` (4,851 analyzed pairs) and
`results/human_bootstrap_per_ct_results.csv` (16 of 17 cell types at BH
q < 0.05; hepatocyte not significant); TCGA — `results/phase34_v2_*_pairs.csv`
(five cancer types) and `results/tcga_bootstrap_results.csv` (per-cancer
bootstrap, all P > 0.9 — hence reported as exploratory/descriptive).

### Brain Regional Analysis Highlights

Class-level results under the block-shuffle null (B = 1,000; block = 10x library / sample_id):

| Cell Type | omega (mean) | null mean | SES | P |
|---|---|---|---|---|
| Astrocyte | 76.83 | 46.74 | 15.85 | 9.99e-04 |
| Oligodendrocyte | 42.22 | 27.45 | 12.71 | 9.99e-04 |
| Choroid plexus | 33.97 | 41.93 | -0.77 | 0.761 (n.s.) |
| Microglia | 13.50 | 10.96 | 12.13 | 9.99e-04 |
| Bergmann glia | 11.17 | 10.03 | 2.03 | 0.034 |

Eight of ten non-neuronal classes show significant regional differentiation under the
block-shuffle permutation null (one-sided upper-tail class-level test, B = 1,000;
Bergmann glia borderline at one-sided q = 0.034; choroid plexus not significant, n = 15 pairs).
For the per-pair migration-candidate screen (31,764 pairs, one-sided lower-tail),
no pair survives Benjamini-Hochberg FDR correction (minimum q = 0.949); the 55
Strong-tier candidates (37 with raw P < 0.05) are hypothesis-generating signals only.
Source: `results/brain_bs_null_ct_test.csv` (class-level tests),
`results/brain_bs_null_results.csv` and `results/brain_bs_null_summary.txt`
(per-pair screen and FDR summary).

## Installation

```bash
pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git
```

The Python import name is `cki`:

```python
import cki
```

Or build the Docker image (see `Dockerfile` in the repository root):

```bash
docker build -t cki:0.4.1 .
docker run --rm cki:0.4.1
```

## Quick Start (3 lines)

```python
import scanpy as sc
from cki import compute

adata = sc.read_h5ad("data.h5ad")
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# One-liner: auto-detect gene sets, compute omega
result = compute(
    adata, species="human",
    groupby="cell_type", group_a="T_cell", group_b="B_cell",
)
print(f"omega = {result['omega']:.4f}")
```

## Functional Gene Modes

`func_method` controls how identity/functional genes are selected:

| `func_method` | Description | Gene set scope |
|---|---|---|
| `"hvg"` *(default)* | Global HVG 2000 (excl. HK) | Same for all pairs |
| `"markers"` | Per-cluster DE markers (merged) | Same for all pairs |
| `"hvg_and_markers"` | Union of HVG + cluster markers | Same for all pairs |
| `"pairwise_de"` | **Pairwise DE between group_a and group_b** | **Tailored per pair** |

`"pairwise_de"` (Hybrid mode) selects the top `n_top_genes` differentially expressed genes specifically between the two groups being compared — the functional gene set changes with each comparison. Requires `groupby`, `group_a`, `group_b`.

```python
# Hybrid mode: per-pair DE
result = compute(
    adata, species="human",
    groupby="cell_type", group_a="T_cell", group_b="B_cell",
    func_method="pairwise_de", n_top_genes=200,
)
```

## Low-Level API

```python
from cki import compute_omega, compute_kn, compute_kf
from cki import (
    detect_housekeeping_genes,
    detect_functional_genes,
    pseudobulk,
    bootstrap_test,
)

# Manual gene sets
hk_idx = [0, 1, 2, ...]           # HK gene indices
func_idx = [10, 11, 12, ...]      # functional gene indices

result = compute_omega(pb_a, pb_b, hk_idx, func_idx)
print(result["omega"], result["kn"], result["kf"])
```

## Bootstrap

```python
from cki import bootstrap_test

boot = bootstrap_test(
    adata, species="human",
    groupby="cell_type", group_a="T_cell", group_b="B_cell",
    n_iterations=1000,
)
print(f"omega={boot['omega']:.4f}, P={boot['p_value']:.4f}")
```

## Interpretation

```
omega = k_f / k_n
omega_cal = omega / 6.67  (empirically calibrated)

omega_cal < 0.75    Below calibration range (relative constraint)
omega_cal ~ 0.75-1.5  Calibration range (equivalent populations)
omega_cal > 1.5    Above calibration range (divergent transcriptome)
```

Calibration against split-half controls of equivalent populations yields an empirical baseline of omega = 6.67 (not the theoretical ideal of 1.0), reflecting systematic inflation from HVG gene selection. The `calibrate_omega()` function rescales all values so that equivalent populations yield omega_cal ~ 1.0. omega is a heuristic index of identity-gene divergence relative to housekeeping-gene divergence, not a formal measure of Darwinian selection. The 6.67 baseline is dataset-internal (mouse split-half); brain split-half calibration yields 12.29 and Tabula Sapiens 7.67, so the factor is not transferable across datasets.

## Statistical Testing

All bootstrap tests use one-sided permutation testing (B = 1,000) with Benjamini-Hochberg FDR correction applied within each dataset. The null distribution is built by randomly shuffling cell labels and recalculating omega. Empirical P-values: P = (count(omega_null >= omega_obs) + 1)/(B + 1).

## Publication

Li Zhang. *CKI: A Cell-type Identity Index for Quantifying Baseline-Normalized Transcriptomic Remodeling.* Submitted to Nucleic Acids Research (2026).

## License & Citation

**Code.** The CKI source code and analysis notebooks are released under the
[MIT License](LICENSE) (Copyright (c) 2026 CKI contributors).

**Data.** Analysis outputs and processed data matrices distributed with this
repository and in the Zenodo archive are licensed under
[Creative Commons Attribution 4.0 International (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/).
Underlying source data are governed by their original licenses and are not
redistributed under the CC-BY-4.0 grant:

- Tabula Muris — original data (Schaum et al., 2018), available via GEO
  (GSE109774) under the Tabula Muris data-use terms;
- Tabula Sapiens — available via CZ CELLxGENE Discover under its
  data-use policy;
- Siletti et al. (2023) human brain atlas — available via CZ CELLxGENE
  Discover under its data-use policy;
- TCGA — genomic data made available through the NCI Genomic Data Commons
  under the TCGA data-use policies;
- HRT Atlas v1.0 housekeeping gene reference — see
  https://www.housekeeping.unicamp.br for its terms.

**Citation.** If you use CKI, please cite:

> Li Zhang. *CKI: A Cell-type Identity Index for Quantifying Baseline-Normalized
> Transcriptomic Remodeling.* Submitted to Nucleic Acids
> Research (2026). Zenodo, DOI: [10.5281/zenodo.20405458](https://doi.org/10.5281/zenodo.20405458).

Concept DOI (all versions): [10.5281/zenodo.20405458](https://doi.org/10.5281/zenodo.20405458).
