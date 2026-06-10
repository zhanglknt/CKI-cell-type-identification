"""
CKI Core Computation
=====================
Core functions for computing the Cell-state Kinetic Index (omega)
and its components: k_n (neutral offset rate), k_f (functional conversion rate),
and Jensen-Shannon divergence.
"""

from typing import Dict, List, Optional, Union

import numpy as np
from anndata import AnnData

from .utils import ensure_probability_distribution


# ── Jensen-Shannon Divergence ───────────────────────────────────────────

def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """
    Compute Jensen-Shannon divergence between two probability distributions.

    JS(P || Q) = 0.5 * KL(P || M) + 0.5 * KL(Q || M)
    where M = 0.5 * (P + Q).

    Parameters
    ----------
    p : np.ndarray
        First probability distribution (1D, non-negative, sums to 1).
    q : np.ndarray
        Second probability distribution (1D, non-negative, sums to 1).

    Returns
    -------
    float
        JS divergence value in [0, 1] (using natural log).
    """
    p = ensure_probability_distribution(p)
    q = ensure_probability_distribution(q)

    m = 0.5 * (p + q)

    # KL(P || M)
    kl_pm = 0.0
    mask_p = p > 0
    if mask_p.any():
        kl_pm = np.sum(p[mask_p] * np.log(p[mask_p] / m[mask_p]))

    # KL(Q || M)
    kl_qm = 0.0
    mask_q = q > 0
    if mask_q.any():
        kl_qm = np.sum(q[mask_q] * np.log(q[mask_q] / m[mask_q]))

    return float(0.5 * kl_pm + 0.5 * kl_qm)


# ── k_n: Neutral Offset Rate ────────────────────────────────────────────

def compute_kn(
    pseudobulk_a: np.ndarray,
    pseudobulk_b: np.ndarray,
    hk_indices: List[int],
    alpha: float = 1.0,
) -> float:
    """
    Compute k_n (neutral offset rate) from housekeeping gene expression.

    k_n measures the baseline expression divergence between two
    pseudobulk samples using housekeeping genes, analogous to the
    neutral substitution rate (Ks) in molecular evolution.

    Parameters
    ----------
    pseudobulk_a : np.ndarray
        Pseudobulk expression vector for group A (1D, n_genes).
    pseudobulk_b : np.ndarray
        Pseudobulk expression vector for group B (1D, n_genes).
    hk_indices : list of int
        Indices of housekeeping genes.
    alpha : float
        Scaling factor. Default 1.0.

    Returns
    -------
    float
        k_n value (0 to infinity).
    """
    if len(hk_indices) == 0:
        return 0.0

    pb_a = np.asarray(pseudobulk_a, dtype=float)
    pb_b = np.asarray(pseudobulk_b, dtype=float)

    hk_idx_arr = np.array(hk_indices)

    p = pb_a[hk_idx_arr]
    q = pb_b[hk_idx_arr]

    p_dist = ensure_probability_distribution(p)
    q_dist = ensure_probability_distribution(q)

    return alpha * js_divergence(p_dist, q_dist)


# ── k_f: Functional Conversion Rate ─────────────────────────────────────

def compute_kf(
    pseudobulk_a: np.ndarray,
    pseudobulk_b: np.ndarray,
    identity_indices: List[int],
    pathway_a: Optional[np.ndarray] = None,
    pathway_b: Optional[np.ndarray] = None,
    w1: float = 1.0,
    w2: float = 0.0,
) -> float:
    """
    Compute k_f (functional conversion rate) from identity gene expression.

    k_f measures expression divergence in cell-type-identity genes,
    analogous to the non-synonymous substitution rate (Ka).

    Parameters
    ----------
    pseudobulk_a : np.ndarray
        Pseudobulk expression vector for group A (1D, n_genes).
    pseudobulk_b : np.ndarray
        Pseudobulk expression vector for group B (1D, n_genes).
    identity_indices : list of int
        Indices of functional/identity genes.
    pathway_a : Optional[np.ndarray]
        Pathway-level expression vector for group A.
    pathway_b : Optional[np.ndarray]
        Pathway-level expression vector for group B.
    w1 : float
        Weight for identity gene component. Default 1.0.
    w2 : float
        Weight for pathway component. Default 0.0 (pathway disabled).

    Returns
    -------
    float
        k_f value (0 to infinity).
    """
    pb_a = np.asarray(pseudobulk_a, dtype=float)
    pb_b = np.asarray(pseudobulk_b, dtype=float)

    # Identity gene component
    if len(identity_indices) == 0:
        js_id = 0.0
    else:
        id_idx_arr = np.array(identity_indices)
        p_id = pb_a[id_idx_arr]
        q_id = pb_b[id_idx_arr]
        p_id_dist = ensure_probability_distribution(p_id)
        q_id_dist = ensure_probability_distribution(q_id)
        js_id = js_divergence(p_id_dist, q_id_dist)

    # Pathway component (optional)
    js_pathway = 0.0
    if pathway_a is not None and pathway_b is not None and w2 > 0:
        p_pw = ensure_probability_distribution(pathway_a)
        q_pw = ensure_probability_distribution(pathway_b)
        js_pathway = js_divergence(p_pw, q_pw)

    return w1 * js_id + w2 * js_pathway


# ── omega: Cell-state Kinetic Index ─────────────────────────────────────

def compute_omega(
    pseudobulk_a: np.ndarray,
    pseudobulk_b: np.ndarray,
    hk_indices: List[int],
    identity_indices: List[int],
    pathway_a: Optional[np.ndarray] = None,
    pathway_b: Optional[np.ndarray] = None,
    alpha: float = 1.0,
    w1: float = 1.0,
    w2: float = 0.0,
) -> Dict[str, float]:
    """
    Compute the Cell-state Kinetic Index (omega) between two pseudobulk samples.

    omega = k_f / k_n, analogous to Ka/Ks in molecular evolution.

    - omega < 1: Purifying selection (conserved transcriptome)
    - omega = 1: Neutral drift
    - omega > 1: Positive selection (divergent transcriptome)

    Parameters
    ----------
    pseudobulk_a : np.ndarray
        Pseudobulk expression vector for group A (1D, n_genes).
    pseudobulk_b : np.ndarray
        Pseudobulk expression vector for group B (1D, n_genes).
    hk_indices : list of int
        Indices of housekeeping genes (for computing k_n).
    identity_indices : list of int
        Indices of functional/identity genes (for computing k_f).
    pathway_a : Optional[np.ndarray]
        Pathway-level expression vector for group A.
    pathway_b : Optional[np.ndarray]
        Pathway-level expression vector for group B.
    alpha : float
        Scaling factor for k_n. Default 1.0.
    w1 : float
        Weight for identity gene component in k_f. Default 1.0.
    w2 : float
        Weight for pathway component in k_f. Default 0.0.

    Returns
    -------
    dict
        Keys:
        - ``omega``: Cell-state Kinetic Index (k_f / k_n)
        - ``kn``: Neutral offset rate
        - ``kf``: Functional conversion rate
        - ``delta_hk``: JS divergence on HK genes
        - ``delta_identity``: JS divergence on identity genes
    """
    kn = compute_kn(pseudobulk_a, pseudobulk_b, hk_indices, alpha=alpha)
    kf = compute_kf(
        pseudobulk_a, pseudobulk_b, identity_indices,
        pathway_a=pathway_a, pathway_b=pathway_b,
        w1=w1, w2=w2,
    )

    # JS divergence on full gene sets (for diagnostic reporting)
    pb_a = np.asarray(pseudobulk_a, dtype=float)
    pb_b = np.asarray(pseudobulk_b, dtype=float)

    if len(hk_indices) > 0:
        hk_arr = np.array(hk_indices)
        delta_hk = js_divergence(
            ensure_probability_distribution(pb_a[hk_arr]),
            ensure_probability_distribution(pb_b[hk_arr]),
        )
    else:
        delta_hk = 0.0

    if len(identity_indices) > 0:
        id_arr = np.array(identity_indices)
        delta_identity = js_divergence(
            ensure_probability_distribution(pb_a[id_arr]),
            ensure_probability_distribution(pb_b[id_arr]),
        )
    else:
        delta_identity = 0.0

    omega = kf / kn if kn > 0 else float('inf')  # kn=0 → omega=∞ (consistent with Ka/Ks)

    return {
        "omega": omega,
        "kn": kn,
        "kf": kf,
        "delta_hk": delta_hk,
        "delta_identity": delta_identity,
    }


# ── Simplified compute() API ────────────────────────────────────────────

def compute(
    adata: AnnData,
    species: str = "human",
    # Gene set options
    hk_method: str = "combined",
    hk_detection_threshold: float = 0.9,
    hk_cv_percentile: float = 0.3,
    use_reference_hk: bool = False,
    hk_merge_mode: str = "union",
    func_method: str = "hvg",
    n_top_genes: int = 2000,
    go_terms: Optional[Union[str, List[str]]] = None,
    kegg_pathways: Optional[Union[str, List[str]]] = None,
    # Manual override
    hk_genes: Optional[List[str]] = None,
    functional_genes: Optional[List[str]] = None,
    # Grouping
    groupby: Optional[str] = None,
    group_a: Optional[str] = None,
    group_b: Optional[str] = None,
    pseudobulk_a: Optional[np.ndarray] = None,
    pseudobulk_b: Optional[np.ndarray] = None,
    # Computation
    alpha: float = 1.0,
    w1: float = 1.0,
    w2: float = 0.0,
    pathway_a: Optional[np.ndarray] = None,
    pathway_b: Optional[np.ndarray] = None,
    # Cell type info
    cell_type_col: Optional[str] = None,
    # Layer
    layer: Optional[str] = None,
    # Output
    return_gene_sets: bool = False,
    random_state: int = 42,
) -> dict:
    """
    Simplified CKI computation with auto-detected gene sets.

    **Minimal usage**::

        import scanpy as sc
        from cki import compute

        adata = sc.read_h5ad("data.h5ad")
        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)

        result = compute(
            adata, species="human",
            groupby="cell_type", group_a="T_cell", group_b="B_cell",
        )
        print(f"omega = {result['omega']:.4f}")

    **Manual gene sets** (backward-compatible)::

        result = compute(
            adata, species="human",
            hk_genes=["GAPDH", "ACTB", ...],
            functional_genes=["CD3D", "CD4", ...],
            groupby="cell_type", group_a="T", group_b="B",
        )

    Parameters
    ----------
    adata : AnnData
        Expression matrix (cells x genes). Should be log-normalized.
    species : str
        "human" or "mouse".
    hk_method : str
        HK detection method: "combined", "cv", or "detection_rate".
    hk_detection_threshold : float
        Fraction of cells for HK detection. Default 0.9.
    hk_cv_percentile : float
        CV percentile for HK detection. Default 0.3.
    use_reference_hk : bool
        Enhance with HRT Atlas reference. Default True.
    hk_merge_mode : str
        How to merge reference: "union", "intersection", "detected_only".
    func_method : str
        Functional gene method: "hvg" or "markers".
    n_top_genes : int
        Number of HVGs. Default 2000.
    go_terms : optional
        GO term IDs for pathway enhancement.
    kegg_pathways : optional
        KEGG pathway IDs for pathway enhancement.
    hk_genes : optional
        Manual HK gene symbols (overrides auto-detection).
    functional_genes : optional
        Manual functional gene symbols (overrides auto-detection).
    groupby : optional
        Column in adata.obs for pseudobulk grouping.
    group_a : optional
        Group label for sample A.
    group_b : optional
        Group label for sample B.
    pseudobulk_a : optional
        Pre-computed pseudobulk vector for A.
    pseudobulk_b : optional
        Pre-computed pseudobulk vector for B.
    alpha : float
        Scaling factor for k_n. Default 1.0.
    w1 : float
        Weight for identity genes. Default 1.0.
    w2 : float
        Weight for pathway component. Default 0.0.
    pathway_a : optional
        Pathway expression vector for A.
    pathway_b : optional
        Pathway expression vector for B.
    cell_type_col : optional
        Column for per-cell-type HK detection.
    layer : optional
        Layer in adata to use.
    return_gene_sets : bool
        If True, include gene set details in result.
    random_state : int
        Random seed.

    Returns
    -------
    dict
        ``omega``, ``kn``, ``kf``, ``delta_hk``, ``delta_identity``.
        If ``return_gene_sets=True``, also includes ``hk_genes``,
        ``functional_genes``, ``hk_info``, ``functional_info``.
    """
    from .gene_sets import detect_housekeeping_genes, detect_functional_genes

    gene_names = adata.var_names.tolist()

    # 1. Resolve housekeeping genes
    if hk_genes is not None:
        hk_set = set(hk_genes)
        hk_indices = [i for i, g in enumerate(gene_names) if g in hk_set]
        hk_info = {"method": "manual", "n_genes": len(hk_indices)}
    else:
        hk_indices, hk_info = detect_housekeeping_genes(
            adata,
            species=species,
            method=hk_method,
            detection_threshold=hk_detection_threshold,
            cv_percentile=hk_cv_percentile,
            use_reference=use_reference_hk,
            merge_mode=hk_merge_mode,
            cell_type_col=cell_type_col or groupby,
            layer=layer,
            random_state=random_state,
        )

    # 2. Resolve functional genes
    if functional_genes is not None:
        fg_set = set(functional_genes)
        identity_indices = [i for i, g in enumerate(gene_names) if g in fg_set]
        id_info = {"method": "manual", "n_genes": len(identity_indices)}
    else:
        identity_indices, id_info = detect_functional_genes(
            adata,
            method=func_method,
            n_top_genes=n_top_genes,
            hk_indices=hk_indices,
            go_terms=go_terms,
            kegg_pathways=kegg_pathways,
            cell_type_col=cell_type_col or groupby,
            layer=layer,
            random_state=random_state,
        )

    # 3. Build pseudobulks if needed
    if pseudobulk_a is not None and pseudobulk_b is not None:
        pb_a = np.asarray(pseudobulk_a, dtype=float)
        pb_b = np.asarray(pseudobulk_b, dtype=float)
    elif groupby is not None and group_a is not None and group_b is not None:
        mask_a = (adata.obs[groupby] == group_a).values
        mask_b = (adata.obs[groupby] == group_b).values

        if mask_a.sum() == 0:
            raise ValueError(f"No cells found for group '{group_a}' in '{groupby}'")
        if mask_b.sum() == 0:
            raise ValueError(f"No cells found for group '{group_b}' in '{groupby}'")

        X = adata.X if layer is None else adata.layers[layer]
        if hasattr(X, "toarray"):
            X = X.toarray()
        X = np.asarray(X, dtype=float)

        pb_a = np.mean(X[mask_a], axis=0)
        pb_b = np.mean(X[mask_b], axis=0)
    else:
        raise ValueError(
            "Must provide either (pseudobulk_a, pseudobulk_b) "
            "or (groupby, group_a, group_b) to specify the two "
            "samples to compare."
        )

    # 4. Compute omega
    result = compute_omega(
        pb_a, pb_b,
        hk_indices, identity_indices,
        pathway_a=pathway_a, pathway_b=pathway_b,
        alpha=alpha, w1=w1, w2=w2,
    )

    # 5. Attach gene set info if requested
    if return_gene_sets:
        result["hk_genes"] = [gene_names[i] for i in hk_indices]
        result["functional_genes"] = [gene_names[i] for i in identity_indices]
        result["hk_info"] = hk_info
        result["functional_info"] = id_info

    return result
