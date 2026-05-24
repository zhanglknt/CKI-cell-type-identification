"""
CKI Data Preprocessing
=======================
Standard single-cell RNA-seq preprocessing pipeline for CKI analysis:
pseudobulk aggregation, normalization, and highly variable gene selection.
"""

from typing import Dict, Optional

import numpy as np
from anndata import AnnData


def pseudobulk(
    adata: AnnData,
    groupby: str,
    layer: Optional[str] = None,
    min_cells: int = 3,
) -> Dict[str, np.ndarray]:
    """
    Create pseudobulk expression vectors by averaging cells within groups.

    Each group's cells are averaged to produce a 1D pseudobulk vector.
    This reduces noise and handles unequal cell counts across groups.

    Parameters
    ----------
    adata : AnnData
        Expression matrix (cells x genes).
    groupby : str
        Column in ``adata.obs`` to group by (e.g., "cell_type", "tissue").
    layer : Optional[str]
        If provided, use ``adata.layers[layer]`` instead of ``adata.X``.
    min_cells : int
        Minimum cells required per group. Groups with fewer cells are skipped
        with a warning.

    Returns
    -------
    dict
        Mapping of group label to 1D numpy pseudobulk vector.
    """
    import warnings

    if groupby not in adata.obs.columns:
        raise ValueError(
            f"Group column '{groupby}' not found in adata.obs. "
            f"Available: {list(adata.obs.columns)}"
        )

    X = adata.X if layer is None else adata.layers[layer]

    result: Dict[str, np.ndarray] = {}
    groups = adata.obs[groupby].unique()

    for group in groups:
        mask = (adata.obs[groupby] == group).values
        n = mask.sum()
        if n < min_cells:
            warnings.warn(
                f"Group '{group}' has only {n} cells (< {min_cells}), skipping."
            )
            continue

        X_group = X[mask]
        if hasattr(X_group, "toarray"):
            X_group = X_group.toarray()

        result[group] = np.mean(X_group, axis=0)

    return result


def normalize_expression(
    adata: AnnData,
    target_sum: float = 1e4,
    log_transform: bool = True,
) -> None:
    """
    Normalize and log-transform expression data (in-place).

    Standard pipeline: library-size normalization to ``target_sum``
    followed by log1p transformation.

    Parameters
    ----------
    adata : AnnData
        Expression matrix. Modified in place.
    target_sum : float
        Target total counts per cell after normalization.
        Default 1e4 (CP10k, standard for scRNA-seq).
    log_transform : bool
        If True, apply log1p transformation after normalization.
    """
    import scanpy as sc

    sc.pp.normalize_total(adata, target_sum=target_sum)
    if log_transform:
        sc.pp.log1p(adata)


def select_hvg(
    adata: AnnData,
    n_top_genes: int = 2000,
    flavor: str = "seurat",
    batch_key: Optional[str] = None,
    layer: Optional[str] = None,
) -> None:
    """
    Select highly variable genes (in-place).

    Adds ``adata.var['highly_variable']`` boolean column.

    Parameters
    ----------
    adata : AnnData
        Log-normalized expression matrix. Modified in place.
    n_top_genes : int
        Number of HVGs to select. Default 2000.
    flavor : str
        HVG selection method: ``"seurat"``, ``"seurat_v3"``, ``"cell_ranger"``.
    batch_key : Optional[str]
        Column in ``adata.obs`` for batch-aware HVG selection.
    layer : Optional[str]
        Layer to use for variance computation.
    """
    import scanpy as sc

    sc.pp.highly_variable_genes(
        adata,
        n_top_genes=n_top_genes,
        flavor=flavor,
        batch_key=batch_key,
        layer=layer,
    )
