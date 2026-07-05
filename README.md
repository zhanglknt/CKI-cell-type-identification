# CKI: Cell-state Kinetic Index

A Ka/Ks-inspired framework for quantifying selective transcriptomic remodeling in single-cell RNA-seq data.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-CKI_cell_type_identification-181717)](https://github.com/zhanglknt/CKI-cell-type-identification)

## Installation

```bash
pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git
```

For a specific version (e.g., v0.3.1):

```bash
pip install git+https://github.com/zhanglknt/CKI-cell-type-identification.git@v0.3.1
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

omega < 0.5    Convergent / Purifying selection
omega ~ 0.5–1.5  Neutral range
omega > 1.5    Divergent / Positive selection
```

## Citation

Li Zhang. *CKI: A Ka/Ks-inspired metric for quantifying transcriptomic selection pressure in single-cell data.* Submitted to Genome Biology (2026).

## License

MIT
