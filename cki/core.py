"""
CKI Core Computation
=====================
Core functions for computing the Cell-type Identity Index (omega)
and its components: k_n (neutral offset rate), k_f (functional conversion rate),
and Jensen-Shannon divergence.
"""

from typing import Dict, List, Optional, Union

import numpy as np
from anndata import AnnData

from .utils import _EPS, densify, ensure_probability_distribution

# ── Numerical guards (single source of truth) ─────────────────────────
# The package uses THREE distinct guard conventions. They are NOT
# interchangeable; each applies to a specific stage of the pipeline:
#
# _EPS = 1e-9  (defined in cki.utils, re-exported here)
#     Additive epsilon used ONLY inside probability-distribution
#     normalization (utils.ensure_probability_distribution) to keep
#     the softmax denominator well-defined. It is NEVER added to
#     k_n / k_f / omega — the JS divergences are computed from exact
#     probability vectors with explicit zero-masking instead.
#
# Omega-denominator positivity guard  (k_n <= 0 -> omega = inf)
#     Used in compute_omega: when k_n is numerically zero, omega is
#     returned as inf (no epsilon is ever added to the denominator).
#     The blocknull hybrid path (blocknull._omega_from_pbs) uses the
#     float-tolerance variant k_n <= _KN_POS_TOL instead.
#     This guard alone governs the single-cell analyses in the
#     manuscript (mouse, Tabula Sapiens, brain).
#
# _KN_FLOOR = 1e-4
#     Optional denominator floor for compute_omega(kn_floor=...):
#     when 0 < k_n < kn_floor, omega is computed as k_f / kn_floor.
#     Disabled by default (kn_floor=0). The manuscript uses it ONLY
#     for the TCGA bulk RNA-seq analysis, where k_n can collapse to
#     near-zero because housekeeping profiles are nearly identical
#     across bulk pseudobulks; 1e-4 is an empirical value chosen well
#     below the k_n range observed in the single-cell datasets, so it
#     truncates only degenerate near-zero denominators without
#     materially altering typical omega values (see Methods).
_KN_POS_TOL = 1e-15
_KN_FLOOR = 1e-4


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
        JS divergence value in [0, 1] (using base-2 log, range [0, 1]).
    """
    p = ensure_probability_distribution(p)
    q = ensure_probability_distribution(q)

    m = 0.5 * (p + q)

    # KL(P || M)
    kl_pm = 0.0
    mask_p = p > 0
    if mask_p.any():
        kl_pm = np.sum(p[mask_p] * np.log2(p[mask_p] / m[mask_p]))

    # KL(Q || M)
    kl_qm = 0.0
    mask_q = q > 0
    if mask_q.any():
        kl_qm = np.sum(q[mask_q] * np.log2(q[mask_q] / m[mask_q]))

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

    return alpha * js_divergence(p, q)


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
        js_id = js_divergence(p_id, q_id)

    # Pathway component (optional)
    js_pathway = 0.0
    if pathway_a is not None and pathway_b is not None and w2 > 0:
        js_pathway = js_divergence(pathway_a, pathway_b)

    return w1 * js_id + w2 * js_pathway


# ── omega: Cell-type Identity Index ─────────────────────────────────────

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
    kn_floor: float = 0.0,
) -> Dict[str, float]:
    """
    Compute the Cell-type Identity Index (omega) between two pseudobulk samples.

    omega = k_f / k_n, analogous to Ka/Ks in molecular evolution.

    By default (``kn_floor=0``) only a positivity guard is applied: if
    k_n is numerically zero, omega is returned as ``inf``. An optional
    lower bound on the denominator can be enabled via ``kn_floor``
    (e.g. ``kn_floor=1e-4``); when k_n falls below this value, omega is
    computed as ``k_f / kn_floor`` instead. The manuscript analyses use
    the positivity guard only for the single-cell datasets (mouse,
    Tabula Sapiens, brain), and an explicit ``kn_floor=1e-4`` for the
    TCGA bulk RNA-seq analysis (see Methods).

    omega is a heuristic index of identity-gene divergence relative to
    housekeeping-gene divergence, not a formal measure of Darwinian
    selection. Interpretation should be anchored in the empirical
    distribution of omega (see the calibrated baseline in
    ``calibrate_omega``), not in the theoretical value omega = 1:
    in practice omega > 1 for nearly all comparisons because HVG-based
    identity-gene selection inflates k_f relative to k_n.

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
    kn_floor : float
        Optional lower bound on k_n (denominator). Default 0.0 disables
        the bound (positivity guard only, matching the single-cell
        analyses in the manuscript).

    Returns
    -------
    dict
        Keys:
        - ``omega``: Cell-type Identity Index (k_f / k_n)
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
        delta_hk = js_divergence(pb_a[hk_arr], pb_b[hk_arr])
    else:
        delta_hk = 0.0

    if len(identity_indices) > 0:
        id_arr = np.array(identity_indices)
        delta_identity = js_divergence(pb_a[id_arr], pb_b[id_arr])
    else:
        delta_identity = 0.0

    # Denominator handling (see the numerical-guards block at the top
    # of this module): optional lower bound on k_n (kn_floor > 0,
    # e.g. _KN_FLOOR = 1e-4 for the TCGA analysis) or exact positivity
    # guard only (kn_floor = 0, the default, matching the single-cell
    # analyses in the manuscript).
    if kn_floor > 0 and kn < kn_floor:
        omega = kf / kn_floor
    elif kn <= 0.0:
        omega = float("inf")
    else:
        omega = kf / kn

    return {
        "omega": omega,
        "kn": kn,
        "kf": kf,
        "delta_hk": delta_hk,
        "delta_identity": delta_identity,
    }


# ── Calibrated Omega ────────────────────────────────────────────────────

def calibrate_omega(
    omega: float,
    baseline: float = 6.67,
) -> float:
    """
    Calibrate omega by dividing by an empirical baseline.

    The theoretical baseline omega = 1 (k_f = k_n) is never observed in
    practice because highly variable gene (HVG) selection systematically
    inflates k_f relative to k_n. Empirical calibration on split-half
    equivalent populations (mouse, n = 6) yields a mean omega of 6.67.
    Calibrated omega rescales all values so that equivalent populations
    have omega_cal ~ 1.0.

    .. warning::
       The default baseline 6.67 is derived from the mouse split-half
       calibration and is NOT transferable across datasets. Dataset-
       internal baselines differ (brain split-half 9.73 [9.03, 10.53];
       Tabula Sapiens 7.67 [7.39, 8.00]), and calibration must be
       recomputed within the dataset under analysis.

    Parameters
    ----------
    omega : float
        Raw omega value (k_f / k_n).
    baseline : float
        Empirical calibration baseline. Default 6.67 (mouse split-half).

    Returns
    -------
    float
        Calibrated omega (omega / baseline).
    """
    if baseline <= 0:
        raise ValueError("baseline must be positive")
    return omega / baseline


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
    kn_floor: float = 0.0,
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
        Enhance with HRT Atlas reference. Default False (data-driven HK
        detection for any species; matches ``bootstrap_test``).
    hk_merge_mode : str
        How to merge reference: "union", "intersection", "detected_only".
    func_method : str
        Functional gene method: "hvg" (default), "markers",
        "hvg_and_markers", "pairwise_absdiff", or "pairwise_de".
        ``"pairwise_absdiff"`` is the **hybrid scheme reported in the
        manuscript** (Methods, "CKI computation"; Supplementary Note 2,
        Algorithm 2): k_f genes are the top ``n_top_genes`` genes ranked
        by absolute pseudobulk mean difference ``|mu_A - mu_B|``
        (descending), with housekeeping genes excluded before ranking.
        ``groupby``, ``group_a``, ``group_b`` are required for this mode.
        ``"pairwise_de"`` instead runs per-direction Wilcoxon DE
        (~2 x ``n_top_genes`` genes) and **differs from the reported
        hybrid scheme**; it is retained for backward compatibility.
    n_top_genes : int
        Number of HVGs (default 2000). For "pairwise_absdiff" mode, the
        total number of top-|Δ| genes (the manuscript uses 200). For
        "pairwise_de" mode, number of top DE genes per direction
        (≈ 2× total before dedup).
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
    kn_floor : float
        Optional lower bound on the k_n denominator, forwarded to
        :func:`compute_omega`. Default 0.0 disables the bound (exact
        positivity guard only: k_n == 0 yields omega = inf), matching
        the single-cell analyses in the manuscript. Set
        ``kn_floor=1e-4`` to reproduce the TCGA bulk RNA-seq analysis:
        bulk housekeeping profiles can be nearly identical across
        conditions, collapsing k_n towards zero; 1e-4 is an empirical
        floor chosen well below the k_n range observed in the
        single-cell datasets, so it truncates only degenerate
        near-zero denominators (see Methods, and the numerical-guards
        block at the top of this module).
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
            groupby=groupby,
            group_a=group_a,
            group_b=group_b,
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
        kn_floor=kn_floor,
    )

    # 5. Attach gene set info if requested
    if return_gene_sets:
        result["hk_genes"] = [gene_names[i] for i in hk_indices]
        result["functional_genes"] = [gene_names[i] for i in identity_indices]
        result["hk_info"] = hk_info
        result["functional_info"] = id_info

    return result
