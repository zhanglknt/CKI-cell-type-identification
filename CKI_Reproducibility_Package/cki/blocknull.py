"""
CKI Block-Shuffle Null
======================
Block-level permutation null for CKI omega significance.

This module exposes the **block-shuffle null** used by the manuscript's
brain-atlas analysis (Siletti dataset; see analysis notebook
``notebooks/08d_brain_blockshuffle_null.py``): group labels are permuted
at the level of whole *blocks* (10x libraries / samples), not individual
cells, and the k_f gene set is **re-selected at every permutation** from
the permuted pseudobulks (top-N by absolute pseudobulk difference,
housekeeping genes excluded — the hybrid scheme Delta rule).

Rationale
---------
Permuting individual cell labels is anti-conservative when cells are
correlated within a library/sample (shared capture environment, donor,
region). Permuting at the block level preserves within-block correlation
structure while breaking the block-to-group assignment, which is the
null of interest ("no group structure at the block level"). The
permutation also preserves the observed per-group block-count multiset.

This construction is the authoritative null for the manuscript's brain
analysis. For the mouse / Tabula Sapiens calibration analyses the paper
uses per-cell label permutation with per-pair k_f re-selection, exposed
as :func:`cki.bootstrap.bootstrap_test` (``reselect_identity=True``,
the default); the TCGA analysis instead holds a fixed global identity
panel (``reselect_identity=False``).

The implementation here is a thin in-memory wrapper: the expression
matrix for the cells of the two groups is densified once. For atlas-scale
data (hundreds of thousands of cells) use the streaming implementation in
the analysis notebook instead.
"""

from typing import Dict, List, Optional, Union

import numpy as np
from anndata import AnnData
from tqdm import tqdm

from .core import js_divergence
from .gene_sets import detect_housekeeping_genes


def _top_absdiff_genes(
    pb_a: np.ndarray,
    pb_b: np.ndarray,
    hk_indices: List[int],
    n_top: int,
) -> np.ndarray:
    """Hybrid-scheme k_f selection: top-N genes by |mu_A - mu_B|, HK excluded.

    Mirrors the Delta rule implemented inline in the analysis notebooks
    (``02b_pilot_v2.py``, ``07d_brain_siletti_v4.py``) and exposed as
    ``func_method="pairwise_absdiff"`` in :func:`cki.core.compute`.
    """
    delta = np.abs(pb_a - pb_b)
    keep = np.ones(len(pb_a), dtype=bool)
    if hk_indices:
        keep[np.asarray(hk_indices, dtype=int)] = False
    candidate_idx = np.where(keep)[0]
    top_n = min(n_top, len(candidate_idx))
    top_local = np.argpartition(delta[candidate_idx], -top_n)[-top_n:]
    return candidate_idx[top_local]


def _omega_from_pbs(
    pb_a: np.ndarray,
    pb_b: np.ndarray,
    hk_indices: List[int],
    n_top: int,
) -> Dict[str, float]:
    """Compute omega with per-pair k_f re-selection (hybrid scheme)."""
    kn = js_divergence(pb_a[hk_indices], pb_b[hk_indices])
    kf_genes = _top_absdiff_genes(pb_a, pb_b, hk_indices, n_top)
    kf = js_divergence(pb_a[kf_genes], pb_b[kf_genes])
    omega = kf / kn if kn > 1e-15 else float("inf")
    return {"omega": omega, "kn": kn, "kf": kf}


def block_shuffle_test(
    adata: AnnData,
    groupby: str,
    group_a: str,
    group_b: str,
    blocks: Union[str, np.ndarray, list],
    species: str = "human",
    hk_indices: Optional[List[int]] = None,
    hk_genes: Optional[List[str]] = None,
    hk_method: str = "combined",
    hk_detection_threshold: float = 0.9,
    hk_cv_percentile: float = 0.3,
    n_top_genes: int = 200,
    layer: Optional[str] = None,
    n_permutations: int = 1000,
    random_state: int = 42,
    tail: str = "upper",
    verbose: bool = True,
) -> dict:
    """Block-shuffle permutation test for CKI omega (manuscript brain null).

    Group (cell) labels are permuted at the **block** level: every cell
    belongs to exactly one block (e.g. a 10x library / sample), each block
    is assigned to one of the two groups, and permutations shuffle the
    block-to-group assignment while preserving the observed number of
    blocks per group. Group pseudobulks are recomputed at every
    permutation as cell-count-weighted means of block means, and the k_f
    gene set is **re-selected at every permutation** from the permuted
    pseudobulks (top ``n_top_genes`` genes by ``|mu_A - mu_B|``, HK genes
    excluded) — i.e. the permutation is scheme-matched to the hybrid k_f
    selection rule of the manuscript.

    This is the package counterpart of the block-shuffle null used in the
    manuscript's brain-atlas analysis (blocks = ``sample_id``; see
    ``notebooks/08d_brain_blockshuffle_null.py`` for the atlas-scale
    streaming implementation across many regions). For the mouse / human
    calibration analyses the paper instead uses per-cell label
    permutation with per-pair k_f re-selection, exposed as
    :func:`cki.bootstrap.bootstrap_test` (``reselect_identity=True``,
    the default).

    Parameters
    ----------
    adata : AnnData
        Expression matrix (cells x genes). Should be log-normalized for
        the mouse/human composition; the brain pipeline normalizes
        pseudobulks instead (see the analysis notebooks).
    groupby : str
        Column in ``adata.obs`` containing the two-group labels.
    group_a : str
        Label of the first group.
    group_b : str
        Label of the second group.
    blocks : str or array-like
        Block assignment for every cell in ``adata``: either the name of a
        column in ``adata.obs`` (e.g. ``"sample_id"``) or an array-like of
        length ``adata.n_obs``. Each block must be entirely contained in
        one of the two groups (blocks are atomic under permutation).
    species : str
        "human" or "mouse" (used only for HK auto-detection / reference).
    hk_indices : optional
        Manual HK gene indices (overrides auto-detection).
    hk_genes : optional
        Manual HK gene symbols (auto-converted to indices).
    hk_method : str
        HK auto-detection method ("combined", "cv", "detection_rate").
    hk_detection_threshold : float
        Detection threshold for HK auto-detection.
    hk_cv_percentile : float
        CV percentile for HK auto-detection.
    n_top_genes : int
        Number of k_f genes re-selected per permutation (hybrid scheme
        top-N by |Δ pseudobulk|). Default 200, as in the manuscript.
    layer : optional
        Layer in ``adata`` to use instead of ``adata.X``.
    n_permutations : int
        Number of block-shuffle permutations. Default 1000.
    random_state : int
        Random seed for reproducibility.
    tail : str
        Which tail to test: ``"upper"`` (default; observed omega exceeds
        the null — the manuscript's class-level usage), ``"lower"``
        (observed omega is anomalously low — the manuscript's per-pair
        screening for constrained pairs), or ``"two-sided"``.
    verbose : bool
        If True, print a summary line.

    Returns
    -------
    dict
        - ``omega``, ``kn``, ``kf``: observed values (k_f from the
          per-pair re-selected gene set)
        - ``p_value``: permutation P-value for the selected tail,
          computed as (n_extreme + 1) / (n_permutations + 1) —
          permutations whose omega is NaN are retained in the
          denominator (counted as non-extreme), matching the
          (B + 1) formula stated in the manuscript
        - ``null_mean``, ``null_std``: null distribution summary
        - ``null_distribution``: full null omega values (list)
        - ``n_blocks``, ``n_permutations``: run metadata
    """
    rng = np.random.RandomState(random_state)
    gene_names = adata.var_names.tolist()

    # ── Resolve blocks (obs column name or explicit vector) ──────
    if isinstance(blocks, str):
        if blocks not in adata.obs.columns:
            raise ValueError(
                f"blocks='{blocks}' not found in adata.obs. "
                f"Available columns: {list(adata.obs.columns)}"
            )
        block_labels = adata.obs[blocks].values
    else:
        block_labels = np.asarray(blocks)
        if len(block_labels) != adata.n_obs:
            raise ValueError(
                f"blocks vector has length {len(block_labels)} but "
                f"adata has {adata.n_obs} cells."
            )

    # ── Resolve HK gene indices ──────────────────────────────────
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
                use_reference=False,
            )
    hk_arr = np.asarray(hk_indices, dtype=int)
    if len(hk_arr) == 0:
        raise ValueError("No housekeeping genes available to compute k_n.")

    # ── Subset to the two groups; blocks must be atomic ──────────
    mask_a = (adata.obs[groupby] == group_a).values
    mask_b = (adata.obs[groupby] == group_b).values
    if mask_a.sum() == 0:
        raise ValueError(f"No cells for group '{group_a}' in '{groupby}'")
    if mask_b.sum() == 0:
        raise ValueError(f"No cells for group '{group_b}' in '{groupby}'")

    subset = mask_a | mask_b
    groups = np.where(mask_a[subset], 0, 1)  # 0 = group_a, 1 = group_b
    block_of_cell = block_labels[subset]

    uniq_blocks, block_inv = np.unique(block_of_cell, return_inverse=True)
    n_blocks = len(uniq_blocks)
    # block -> group (must be unique: a block is atomic)
    block_group = np.full(n_blocks, -1, dtype=int)
    for b in range(n_blocks):
        gs = np.unique(groups[block_inv == b])
        if len(gs) > 1:
            raise ValueError(
                f"Block '{uniq_blocks[b]}' contains cells from both "
                f"'{group_a}' and '{group_b}'. Blocks must be atomic "
                f"(wholly within one group) for the block-shuffle null."
            )
        block_group[b] = gs[0]

    if n_blocks < 2:
        raise ValueError(
            "Need at least 2 blocks to permute block-to-group assignments."
        )
    n_blocks_a = int(np.sum(block_group == 0))
    if n_blocks_a == 0 or n_blocks_a == n_blocks:
        raise ValueError(
            "Both groups must contain at least one block."
        )

    # ── Expression matrix for the subset (densified once) ────────
    X = adata.X if layer is None else adata.layers[layer]
    if hasattr(X, "toarray"):
        X = X.toarray()
    X = np.asarray(X[subset], dtype=float)

    # Block means and cell counts (group pseudobulk = weighted mean of
    # block means with cell-count weights == plain cell mean)
    block_means = np.zeros((n_blocks, X.shape[1]), dtype=float)
    block_counts = np.zeros(n_blocks, dtype=float)
    for b in range(n_blocks):
        rows = block_inv == b
        block_counts[b] = rows.sum()
        if rows.any():
            block_means[b] = X[rows].mean(axis=0)

    def _group_pbs(assign: np.ndarray):
        """assign: block -> group (0/1). Return (pb_a, pb_b)."""
        pbs = []
        for g in (0, 1):
            m = assign == g
            if not m.any():
                return None
            w = block_counts[m]
            pbs.append(
                (block_means[m] * w[:, None]).sum(axis=0) / w.sum()
            )
        return pbs[0], pbs[1]

    # ── Observed omega (k_f re-selected per pair, as reported) ────
    pb_a, pb_b = _group_pbs(block_group)
    obs = _omega_from_pbs(pb_a, pb_b, hk_arr.tolist(), n_top_genes)

    # ── Block-shuffle permutations (preserve per-group block counts) ──
    null_omega = []
    iterator = (
        tqdm(range(n_permutations), desc="Block shuffle")
        if verbose else range(n_permutations)
    )
    for _ in iterator:
        perm_assign = block_group[rng.permutation(n_blocks)]
        res = _group_pbs(perm_assign)
        if res is None:
            continue
        r = _omega_from_pbs(res[0], res[1], hk_arr.tolist(), n_top_genes)
        if not np.isnan(r["omega"]):
            null_omega.append(r["omega"])

    null_omega = np.array(null_omega)
    if len(null_omega) == 0:
        raise RuntimeError(
            "All block-shuffle permutations produced invalid omega values."
        )

    # P-value: (n_extreme + 1) / (n_permutations + 1). NaN-producing
    # permutations stay in the denominator (counted as non-extreme), so
    # the formula matches the manuscript's (B + 1) convention exactly.
    tail = str(tail).lower().strip()
    if tail not in ("upper", "lower", "two-sided"):
        raise ValueError("tail must be 'upper', 'lower', or 'two-sided'.")
    n_extreme = {
        "upper": int(np.sum(null_omega >= obs["omega"])),
        "lower": int(np.sum(null_omega <= obs["omega"])),
    }
    p_one = {k: (v + 1) / (n_permutations + 1) for k, v in n_extreme.items()}
    if tail == "upper":
        p_value = p_one["upper"]
    elif tail == "lower":
        p_value = p_one["lower"]
    else:
        p_value = min(1.0, 2.0 * min(p_one["upper"], p_one["lower"]))
    null_mean = float(np.mean(null_omega))
    null_std = float(np.std(null_omega))

    if verbose:
        print(
            f"omega={obs['omega']:.4f} (kn={obs['kn']:.6f}, "
            f"kf={obs['kf']:.6f}) | blocks={n_blocks} "
            f"({n_blocks_a}/{n_blocks - n_blocks_a}) | "
            f"null mean={null_mean:.4f}, p={p_value:.4f}"
        )

    return {
        "omega": obs["omega"],
        "kn": obs["kn"],
        "kf": obs["kf"],
        "p_value": p_value,
        "null_mean": null_mean,
        "null_std": null_std,
        "null_distribution": null_omega.tolist(),
        "n_blocks": n_blocks,
        "n_permutations": len(null_omega),
    }
