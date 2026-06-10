"""
CKI Bootstrap Testing
======================
Permutation-based statistical testing for CKI omega significance.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
from tqdm import tqdm
from anndata import AnnData

from .core import compute_omega
from .gene_sets import detect_housekeeping_genes, detect_functional_genes


def bootstrap_test(
    adata: AnnData,
    species: str = "human",
    # Grouping
    groupby: Optional[str] = None,
    group_a: Optional[str] = None,
    group_b: Optional[str] = None,
    pseudobulk_a: Optional[np.ndarray] = None,
    pseudobulk_b: Optional[np.ndarray] = None,
    # Gene set options (auto-detected if not provided)
    hk_indices: Optional[List[int]] = None,
    identity_indices: Optional[List[int]] = None,
    hk_genes: Optional[List[str]] = None,
    functional_genes: Optional[List[str]] = None,
    # Gene set auto-detection params
    hk_method: str = "combined",
    hk_detection_threshold: float = 0.9,
    hk_cv_percentile: float = 0.3,
    use_reference_hk: bool = True,
    func_method: str = "hvg",
    n_top_genes: int = 2000,
    # Layer
    layer: Optional[str] = None,
    # Cell type info
    cell_type_col: Optional[str] = None,
    # Bootstrap params
    n_bootstrap: int = 1000,
    # Computation
    alpha: float = 1.0,
    w1: float = 1.0,
    w2: float = 0.0,
    pathway_a: Optional[np.ndarray] = None,
    pathway_b: Optional[np.ndarray] = None,
    random_state: int = 42,
    verbose: bool = True,
) -> dict:
    """
    Bootstrap permutation test for CKI omega significance.

    Tests the null hypothesis that omega = 1 (no selective remodeling)
    by permuting cell labels between the two groups.

    **Minimal usage**::

        from cki import bootstrap_test

        result = bootstrap_test(
            adata, species="human",
            groupby="cell_type", group_a="T_cell", group_b="B_cell",
            n_bootstrap=1000,
        )
        print(f"omega={result['omega']:.4f}, p={result['p_value']:.4f}")

    Parameters
    ----------
    adata : AnnData
        Expression matrix (cells x genes). Should be log-normalized.
    species : str
        "human" or "mouse".
    groupby : optional
        Column in ``adata.obs`` for pseudobulk grouping.
    group_a, group_b : optional
        Group labels for the two samples to compare.
    pseudobulk_a, pseudobulk_b : optional
        Pre-computed pseudobulk vectors.
    hk_indices : optional
        Manual HK gene indices.
    identity_indices : optional
        Manual functional gene indices.
    hk_genes : optional
        Manual HK gene symbols (auto-converted to indices).
    functional_genes : optional
        Manual functional gene symbols (auto-converted to indices).
    hk_method : str
        HK auto-detection method.
    hk_detection_threshold : float
        Detection threshold for HK detection.
    hk_cv_percentile : float
        CV percentile for HK detection.
    use_reference_hk : bool
        Enhance with HRT Atlas reference.
    func_method : str
        Functional gene detection method.
    n_top_genes : int
        Number of HVGs for functional genes.
    layer : optional
        Layer in adata to use.
    cell_type_col : optional
        Column for per-cell-type HK detection.
    n_bootstrap : int
        Number of bootstrap permutations. Default 1000.
    alpha : float
        Scaling factor for k_n.
    w1 : float
        Weight for identity genes.
    w2 : float
        Weight for pathway component.
    pathway_a, pathway_b : optional
        Pathway expression vectors.
    random_state : int
        Random seed for reproducibility.
    verbose : bool
        If True, show progress bar and print summary.

    Returns
    -------
    dict
        - ``omega``: observed omega value
        - ``kn``, ``kf``: component values
        - ``delta_hk``, ``delta_identity``: JS divergences
        - ``p_value``: bootstrap p-value
        - ``null_mean``: mean of null distribution
        - ``null_std``: std of null distribution
        - ``cohens_d``: effect size (Cohen's d vs null)
        - ``ci_95``: 95% confidence interval [lower, upper]
        - ``null_distribution``: full null omega distribution (list)
    """
    rng = np.random.RandomState(random_state)
    gene_names = adata.var_names.tolist()

    # 1. Resolve gene sets
    if hk_indices is None:
        if hk_genes is not None:
            hk_set = set(hk_genes)
            hk_indices = [i for i, g in enumerate(gene_names) if g in hk_set]
        else:
            hk_indices, _ = detect_housekeeping_genes(
                adata,
                species=species,
                method=hk_method,
                detection_threshold=hk_detection_threshold,
                cv_percentile=hk_cv_percentile,
                use_reference=use_reference_hk,
                cell_type_col=cell_type_col or groupby,
                layer=layer,
                random_state=random_state,
            )
    if identity_indices is None:
        if functional_genes is not None:
            fg_set = set(functional_genes)
            identity_indices = [
                i for i, g in enumerate(gene_names) if g in fg_set
            ]
        else:
            identity_indices, _ = detect_functional_genes(
                adata,
                method=func_method,
                n_top_genes=n_top_genes,
                hk_indices=hk_indices,
                cell_type_col=cell_type_col or groupby,
                layer=layer,
                random_state=random_state,
            )

    if verbose:
        print(f"HK genes: {len(hk_indices)}, Functional genes: {len(identity_indices)}")

    # 2. Build observed pseudobulks and pooled data
    if pseudobulk_a is not None and pseudobulk_b is not None:
        pb_a = np.asarray(pseudobulk_a, dtype=float)
        pb_b = np.asarray(pseudobulk_b, dtype=float)
        X = adata.X if layer is None else adata.layers[layer]
        if hasattr(X, "toarray"):
            X = X.toarray()
        X = np.asarray(X, dtype=float)
        pooled = X
        n_a = X.shape[0] // 2
        n_total = X.shape[0]
    elif groupby is not None and group_a is not None and group_b is not None:
        mask_a = (adata.obs[groupby] == group_a).values
        mask_b = (adata.obs[groupby] == group_b).values
        n_a = mask_a.sum()
        n_b = mask_b.sum()

        if n_a == 0:
            raise ValueError(f"No cells for group '{group_a}' in '{groupby}'")
        if n_b == 0:
            raise ValueError(f"No cells for group '{group_b}' in '{groupby}'")

        X = adata.X if layer is None else adata.layers[layer]
        if hasattr(X, "toarray"):
            X = X.toarray()
        X = np.asarray(X, dtype=float)

        pb_a = np.mean(X[mask_a], axis=0)
        pb_b = np.mean(X[mask_b], axis=0)

        pooled = np.vstack([X[mask_a], X[mask_b]])
        n_total = n_a + n_b
    else:
        raise ValueError(
            "Must provide either (pseudobulk_a, pseudobulk_b) "
            "or (groupby, group_a, group_b)."
        )

    # 3. Compute observed omega
    obs_result = compute_omega(
        pb_a, pb_b, hk_indices, identity_indices,
        pathway_a=pathway_a, pathway_b=pathway_b,
        alpha=alpha, w1=w1, w2=w2,
    )

    # 4. Bootstrap permutation
    null_omega = []
    iterator = tqdm(range(n_bootstrap), desc="Bootstrap") if verbose else range(n_bootstrap)

    for _ in iterator:
        perm = rng.permutation(n_total)
        pb_perm1 = np.mean(pooled[perm[:n_a]], axis=0)
        pb_perm2 = np.mean(pooled[perm[n_a:]], axis=0)

        r = compute_omega(
            pb_perm1, pb_perm2, hk_indices, identity_indices,
            pathway_a=pathway_a, pathway_b=pathway_b,
            alpha=alpha, w1=w1, w2=w2,
        )
        if not np.isnan(r["omega"]):
            null_omega.append(r["omega"])

    null_omega = np.array(null_omega)

    # 5. Compute statistics (two-sided test: |null-1| >= |obs-1|)
    obs_dist = abs(obs_result["omega"] - 1.0)
    null_dists = np.abs(null_omega - 1.0)
    p_value = (np.sum(null_dists >= obs_dist) + 1) / (len(null_omega) + 1)
    null_mean = float(np.mean(null_omega))
    null_std = float(np.std(null_omega))
    cohens_d = (
        (obs_result["omega"] - null_mean) / null_std
        if null_std > 1e-12
        else 0.0
    )
    ci_95 = [
        float(np.percentile(null_omega, 2.5)),
        float(np.percentile(null_omega, 97.5)),
    ]

    if verbose:
        print(
            f"omega={obs_result['omega']:.4f} (kn={obs_result['kn']:.6f}, "
            f"kf={obs_result['kf']:.6f})"
        )
        print(
            f"Null: mean={null_mean:.4f}, std={null_std:.4f}, "
            f"p={p_value:.4f}, d={cohens_d:.2f}"
        )

    return {
        "omega": obs_result["omega"],
        "kn": obs_result["kn"],
        "kf": obs_result["kf"],
        "delta_hk": obs_result["delta_hk"],
        "delta_identity": obs_result["delta_identity"],
        "p_value": p_value,
        "null_mean": null_mean,
        "null_std": null_std,
        "cohens_d": cohens_d,
        "ci_95": ci_95,
        "null_distribution": null_omega.tolist(),
        "n_bootstrap": len(null_omega),
    }
