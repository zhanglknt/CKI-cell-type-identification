# CKI: Cell-state Kinetic Index

A Ka/Ks-inspired framework for quantifying selective transcriptomic remodeling in single-cell RNA-seq data.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-CKI_cell_type_identification-181717)](https://github.com/zhanglknt/CKI-cell-type-identification)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.xxxxxxx.svg)](https://doi.org/10.5281/zenodo.xxxxxxx)

## Overview

CKI (Cell-state Kinetic Index) operationalizes the Ka/Ks concept from molecular evolution at the single-cell transcriptomic level. By decomposing gene expression into housekeeping (neutral) and functional (identity) components and computing their Jensen-Shannon divergence ratio, CKI quantifies transcriptomic selection pressure between any two cell populations.

## Key Findings

CKI was validated on four independent datasets totaling millions of cells:

| Dataset | Pairs | Result | P-value |
|---|---|---|---|
| Mouse (Tabula Muris) | 703 | 8/15 cell types significant | FDR < 0.05 |
| Human (Tabula Sapiens) | 5,151 | 15/16 cell types significant | P = 9.99e-04 |
| TCGA (BRCA/LIHC/LUAD) | — | Exploratory convergence analysis | Descriptive |
| Brain (Siletti Atlas) | 31,764 | 10/10 cell types significant | P < 0.01, FDR < 0.05 |

### Brain Regional Analysis Highlights

| Cell Type | omega | null mean | Cohen's d | P |
|---|---|---|---|---|
| Astrocyte | 76.20 | 12.58 | 321.85 | 9.99e-04 |
| Oligodendrocyte | 41.73 | 10.59 | 234.42 | 9.99e-04 |
| Choroid plexus | 33.97 | 14.89 | 9.32 | 9.99e-04 |
| Microglia | 13.54 | 8.98 | 34.22 | 9.99e-04 |
| Bergmann glia | 11.17 | 8.75 | 6.46 | 2.997e-03 |

All 10 brain cell types show significant regional differentiation gradients (one-sided permutation test, B = 1,000, BH FDR correction).

## Installation

```bash
pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git
```

For a specific version (e.g., v0.4.0):

```bash
pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git@v0.4.0
```

Or build the Docker image (see `Dockerfile` in the repository root):

```bash
docker build -t cki:0.4.0 .
docker run --rm cki:0.4.0
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

omega_cal < 0.75    Purifying selection (constrained)
omega_cal ~ 0.75-1.5  Neutral range
omega_cal > 1.5    Positive selection (divergent)
```

Calibration against split-half controls of equivalent populations yields an empirical baseline of omega = 6.67 (not the theoretical ideal of 1.0), reflecting systematic inflation from HVG gene selection. The `calibrate_omega()` function rescales all values so that equivalent populations yield omega_cal ~ 1.0.

## Statistical Testing

All bootstrap tests use one-sided permutation testing (B = 1,000) with Benjamini-Hochberg FDR correction applied within each dataset. The null distribution is built by randomly shuffling cell labels and recalculating omega. Empirical P-values: P = (count(omega_null >= omega_obs) + 1)/(B + 1).

## Publication

Li Zhang. *CKI: A Ka/Ks-inspired metric for quantifying transcriptomic selection pressure in single-cell data.* Submitted to Nucleic Acids Research (2026).

## License

MIT
