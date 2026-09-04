"""
CKI Bootstrap Testing
======================
Permutation-based statistical testing for CKI omega significance.
Includes Benjamini-Hochberg FDR correction for multiple comparisons.
"""

import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from tqdm import tqdm
from anndata import AnnData

from .core import compute_omega
from .gene_sets import detect_housekeeping_genes, detect_functional_genes
from .blocknull import _omega_from_pbs
from .utils import densify


class _BootstrapResult(dict):
    """Result dict for :func:`bootstrap_test`.

    Provides two deprecated backward-compatible aliases, each emitting
    a :class:`DeprecationWarning` on access:

    - ``cohens_d`` -> ``ses`` (standardized effect size). The statistic
      was never a Cohen's d (there is no second-sample pooled standard
      deviation); it is a standardized effect size of the observed
      omega relative to the permutation null distribution.
    - ``ci_95`` -> ``null_ci_95``. The interval is the 2.5/97.5
      percentile range of the permutation *null* distribution, NOT a
      confidence interval for the observed omega.

    ``dict.get`` is overridden so the aliases warn through the
    ``.get()`` path as well (plain ``dict.get`` would bypass the
    ``__getitem__`` interception).
    """

    _ALIASES = {
        "cohens_d": (
            "ses",
            "'cohens_d' is deprecated and will be removed in a "
            "future release; the statistic is a standardized effect "
            "size (SES), not a Cohen's d. Use result['ses'] instead.",
        ),
        "ci_95": (
            "null_ci_95",
            "'ci_95' is deprecated and will be removed in a future "
            "release; the interval is the 2.5/97.5 percentile range "
            "of the permutation null distribution, not a confidence "
            "interval for omega. Use result['null_ci_95'] instead.",
        ),
    }

    def __getitem__(self, key):
        if key in self._ALIASES:
            canonical, message = self._ALIASES[key]
            warnings.warn(message, DeprecationWarning, stacklevel=2)
            key = canonical
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key in self._ALIASES:
            return self[key]
        return super().get(key, default)


def benjamini_hochberg(p_values: Union[np.ndarray, list]) -> np.ndarray:
    """
    Benjamini-Hochberg procedure for FDR correction.

    Adjusts P-values for multiple comparisons, controlling the
    false discovery rate at the level of the original P-values.

    Parameters
    ----------
    p_values : array-like
        Array of P-values to correct.

    Returns
    -------
    ndarray
        BH-adjusted P-values (q-values), same length as input.

    Example
    -------
    >>> p = [0.01, 0.04, 0.03, 0.20, 0.001]
    >>> q = benjamini_hochberg(p)
    >>> print(q)  # [0.025, 0.0667, 0.05, 0.25, 0.005]
    """
    p = np.asarray(p_values, dtype=float)
    n = len(p)
    if n == 0:
        return np.array([], dtype=float)
    if n == 1:
        return p.copy()

    # Sort P-values
    order = np.argsort(p)
    ranked = p[order]

    # BH adjustment: q_i = p_i * n / rank_i
    adjusted = ranked * n / np.arange(1, n + 1)

    # Enforce monotonicity from largest to smallest
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]

    # Cap at 1.0
    adjusted = np.minimum(adjusted, 1.0)

    # Unsort to original order
    result = np.empty(n, dtype=float)
    result[order] = adjusted
    return result


def apply_fdr(
    p_values: Union[np.ndarray, list],
    method: str = "bh",
) -> np.ndarray:
    """
    Apply multiple testing correction to a set of P-values.

    Parameters
    ----------
    p_values : array-like
        Array of P-values to correct.
    method : str
        Correction method: "bh" (Benjamini-Hochberg, default)
        or "bonferroni".

    Returns
    -------
    ndarray
        Adjusted P-values (q-values).

    Example
    -------
    >>> from cki import apply_fdr
    >>> p_vals = [0.001, 0.02, 0.03, 0.5]
    >>> q_vals = apply_fdr(p_vals)
    >>> print(q_vals)
    """
    p = np.asarray(p_values, dtype=float)
    method = method.lower().strip()

    if method in ("bh", "benjamini-hochberg", "fdr", "fdr_bh"):
        return benjamini_hochberg(p)
    elif method == "bonferroni":
        return np.minimum(p * len(p), 1.0)
    else:
        raise ValueError(
            f"Unknown correction method: '{method}'. "
            "Use 'bh' (Benjamini-Hochberg) or 'bonferroni'."
        )


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
    use_reference_hk: bool = False,
    func_method: str = "hvg",
    n_top_genes: int = 2000,
    # Layer
    layer: Optional[str] = None,
    # Cell type info
    cell_type_col: Optional[str] = None,
    # Bootstrap params
    n_bootstrap: int = 1000,
    tail: str = "upper",
    # Gene re-selection (manuscript parity)
    reselect_identity: bool = True,
    n_reselect_genes: int = 200,
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
    Permutation test for CKI omega significance.

    Despite the historical name (``bootstrap_test``), this is a
    **label-permutation test**, not a bootstrap resampling procedure:
    the null distribution is built by randomly permuting group (cell)
    labels between the two groups. :func:`permutation_test` is an
    alias for this function.

    Tests whether the observed omega exceeds the null distribution
    obtained by randomly permuting group (cell) labels between the two
    groups — i.e., a test of label exchangeability, NOT of the point
    hypothesis omega = 1 (under the permutation null the median omega
    sits near the empirical calibration baseline, ~6.67 for equivalent
    populations, not 1).

    Note: by default (``reselect_identity=True``) the HK (k_n) gene set
    is resolved once (before the permutation loop) and held fixed, while
    the k_f gene set is re-selected **at every permutation** from the
    permuted pseudobulks (top ``n_reselect_genes`` non-HK genes by
    absolute pseudobulk difference) — the same per-pair selection rule
    as the observed value, so the null incorporates the gene-selection
    step. This is the label-permutation procedure reported in the
    manuscript for the mouse pilot and Tabula Sapiens analyses. Passing
    explicit ``identity_indices`` / ``functional_genes`` pins a fixed
    k_f gene set; ``reselect_identity=False`` requests the legacy
    fixed-gene-set null, which is anti-conservative relative to the
    reported analyses whenever the observed omega uses per-pair
    selection (the TCGA analysis deliberately used a fixed global
    identity panel; see the manuscript's fixed-panel caveat). The
    brain-atlas analysis uses a block-level null instead — see
    :func:`cki.blocknull.block_shuffle_test`.

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
        Enhance with HRT Atlas reference. Default False (aligned with
        ``cki.core.compute``).
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
    tail : str
        Which tail of the null distribution to test, with the same
        naming convention as :func:`cki.blocknull.block_shuffle_test`:
        ``"upper"`` (default; tests whether the observed omega is
        **greater** than the permuted-label null — the manuscript's
        usage), ``"lower"`` (tests whether the observed omega is
        anomalously **lower** than the null), or ``"two-sided"``
        (two-sided p = min(1, 2 x min(p_upper, p_lower))). All use the
        (n_extreme + 1) / (n_bootstrap + 1) permutation convention.
    reselect_identity : bool
        If True (default) and no explicit identity gene inputs are
        given, the k_f gene set is re-selected at every permutation
        (and for the observed value) as the top ``n_reselect_genes``
        non-HK genes by absolute pseudobulk difference — the
        manuscript's hybrid scheme, so the null incorporates the
        gene-selection step. If False, the resolved gene set is held
        fixed across permutations (legacy mode; faster, but
        anti-conservative relative to the reported analyses when the
        observed omega uses per-pair selection). Explicit
        ``identity_indices`` / ``functional_genes`` always pin a fixed
        gene set, regardless of this flag.
    n_reselect_genes : int
        Number of top-|Δ pseudobulk| non-HK genes selected per pair in
        reselection mode. Default 200, as in the manuscript.
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
        - ``p_value``: bootstrap p-value for the selected ``tail``
        - ``null_mean``: mean of null distribution
        - ``null_std``: std of null distribution
        - ``ses``: standardized effect size of the observed omega
          relative to the null distribution,
          ``(omega - null_mean) / null_std``. (This was previously
          reported under the misnomer ``cohens_d``; the old key is
          retained as a deprecated alias.)
        - ``null_ci_95``: central 95% range [2.5th, 97.5th percentile]
          of the permutation null distribution. This is NOT a
          confidence interval for the observed omega (the permutation
          null is a distribution of omega values under random label
          assignment, not a sampling distribution of the estimate).
          (This was previously reported under the misnomer ``ci_95``;
          the old key is retained as a deprecated alias.)
        - ``n_null_finite``: number of finite null omega values used
          for ``null_mean`` / ``null_std`` / ``ses`` / ``null_ci_95``
          (non-finite null values, e.g. ``inf`` from a degenerate
          k_n ~ 0, are excluded from those summary statistics; the
          full raw distribution is kept in ``null_distribution``)
        - ``null_distribution``: full null omega distribution (list)
        - ``gene_selection``: description of the k_f gene-set handling
          used (per-pair re-selection vs fixed)
        - ``reselect_identity``: whether per-pair re-selection was used
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

    # k_f gene-set mode: with reselect_identity=True (default) and no
    # explicit identity gene inputs, the k_f set is re-selected per pair
    # (observed value and every permutation) via the hybrid top-N rule,
    # reproducing the manuscript's testing procedure. Explicit gene
    # inputs always pin a fixed gene set.
    explicit_identity = (
        identity_indices is not None or functional_genes is not None
    )
    use_reselect = bool(reselect_identity) and not explicit_identity
    if not use_reselect and identity_indices is None:
        identity_indices, _ = detect_functional_genes(
            adata,
            method=func_method,
            n_top_genes=n_top_genes,
            hk_indices=hk_indices,
            cell_type_col=cell_type_col or groupby,
            layer=layer,
            random_state=random_state,
        )

    if use_reselect and (
        pathway_a is not None
        or pathway_b is not None
        or alpha != 1.0
        or w1 != 1.0
        or w2 != 0.0
    ):
        raise ValueError(
            "reselect_identity=True implements the plain hybrid k_f/k_n "
            "omega (top-N |Δ pseudobulk| non-HK genes re-selected per "
            "pair) and does not support the pathway component or "
            "non-default alpha/w1/w2 weights. Pass reselect_identity=False "
            "to use those options with a fixed gene set."
        )

    if verbose:
        if use_reselect:
            print(
                f"HK genes: {len(hk_indices)}, Functional genes: "
                f"re-selected per pair (top-{n_reselect_genes} by "
                f"|Δ pseudobulk|, HK excluded)"
            )
        else:
            print(
                f"HK genes: {len(hk_indices)}, Functional genes: "
                f"{len(identity_indices)} (fixed gene set)"
            )

    # 2. Build observed pseudobulks and pooled data
    if pseudobulk_a is not None and pseudobulk_b is not None:
        pb_a = np.asarray(pseudobulk_a, dtype=float)
        pb_b = np.asarray(pseudobulk_b, dtype=float)
        # The permutation null needs the per-group cell counts and the
        # pooled cell-level matrix; these must come from the group
        # labels in adata.obs, NOT from a hardcoded 50/50 split of
        # adata.X (the previous behavior silently assumed equal group
        # sizes and pooled cells outside the two groups).
        if groupby is None or group_a is None or group_b is None:
            raise ValueError(
                "bootstrap_test with pre-computed pseudobulks still "
                "requires (groupby, group_a, group_b) so the "
                "permutation null can be built from the correct "
                "per-group cell counts and pooled cells in adata."
            )
        mask_a = (adata.obs[groupby] == group_a).values
        mask_b = (adata.obs[groupby] == group_b).values
        n_a = int(mask_a.sum())
        n_b = int(mask_b.sum())

        if n_a == 0:
            raise ValueError(f"No cells for group '{group_a}' in '{groupby}'")
        if n_b == 0:
            raise ValueError(f"No cells for group '{group_b}' in '{groupby}'")

        X = adata.X if layer is None else adata.layers[layer]
        X = densify(X, context="expression matrix")

        pooled = np.vstack([X[mask_a], X[mask_b]])
        n_total = n_a + n_b
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
        X = densify(X, context="expression matrix")

        pb_a = np.mean(X[mask_a], axis=0)
        pb_b = np.mean(X[mask_b], axis=0)

        pooled = np.vstack([X[mask_a], X[mask_b]])
        n_total = n_a + n_b
    else:
        raise ValueError(
            "Must provide either (pseudobulk_a, pseudobulk_b) "
            "or (groupby, group_a, group_b)."
        )

    if n_a > 500 or n_b > 500:
        warnings.warn(
            "permutation-test power collapses for large pseudobulks "
            f"(n ≳ 500 cells per group; got n_a={n_a}, n_b={n_b}); "
            "CKI operating window is ~50–200 cells per donor per "
            "condition (see manuscript Note 3.19)",
            UserWarning,
            stacklevel=2,
        )

    # 3. Compute observed omega
    hk_arr = list(hk_indices)
    if use_reselect:
        obs_hybrid = _omega_from_pbs(pb_a, pb_b, hk_arr, n_reselect_genes)
        obs_result = {
            "omega": obs_hybrid["omega"],
            "kn": obs_hybrid["kn"],
            "kf": obs_hybrid["kf"],
            "delta_hk": obs_hybrid["kn"],
            "delta_identity": obs_hybrid["kf"],
        }
    else:
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

        if use_reselect:
            r = _omega_from_pbs(
                pb_perm1, pb_perm2, hk_arr, n_reselect_genes
            )
        else:
            r = compute_omega(
                pb_perm1, pb_perm2, hk_indices, identity_indices,
                pathway_a=pathway_a, pathway_b=pathway_b,
                alpha=alpha, w1=w1, w2=w2,
            )
        if not np.isnan(r["omega"]):
            null_omega.append(r["omega"])

    null_omega = np.array(null_omega)

    # 5. Compute statistics (permutation test on the selected tail)
    # Default ("upper"): tests whether observed omega exceeds the null
    # distribution built from randomly permuted cell labels. The null
    # distribution represents omega values expected under random group
    # assignment.
    # P-value: (n_extreme + 1) / (n_bootstrap + 1). NaN-producing permutations
    # stay in the denominator (counted as non-extreme), matching the
    # manuscript's (B + 1) formula exactly.
    tail = str(tail).lower().strip()
    if tail not in ("upper", "lower", "two-sided"):
        raise ValueError("tail must be 'upper', 'lower', or 'two-sided'.")
    n_extreme = {
        "upper": int(np.sum(null_omega >= obs_result["omega"])),
        "lower": int(np.sum(null_omega <= obs_result["omega"])),
    }
    p_one = {k: (v + 1) / (n_bootstrap + 1) for k, v in n_extreme.items()}
    if tail == "upper":
        p_value = p_one["upper"]
    elif tail == "lower":
        p_value = p_one["lower"]
    else:
        p_value = min(1.0, 2.0 * min(p_one["upper"], p_one["lower"]))
    # Guard against non-finite null values: a degenerate permuted
    # k_n ~ 0 yields omega = inf, which would poison null_mean /
    # null_std (and hence the SES) with inf/NaN. Summary statistics
    # are computed on the finite subset only; the raw distribution
    # (including non-finite values) is preserved in
    # ``null_distribution`` and still drives the p-value above.
    null_finite = null_omega[np.isfinite(null_omega)]
    n_null_finite = int(null_finite.size)
    if n_null_finite < null_omega.size:
        warnings.warn(
            f"{null_omega.size - n_null_finite} non-finite null omega "
            "value(s) (e.g. inf from a degenerate k_n ~ 0) excluded "
            "from null_mean/null_std/ses/null_ci_95; see "
            "'n_null_finite' in the result.",
            UserWarning,
            stacklevel=2,
        )

    if n_null_finite >= 2:
        null_mean = float(np.mean(null_finite))
        null_std = float(np.std(null_finite))
        # Standardized effect size (SES) of the observed omega relative
        # to the null distribution. NOTE: this is NOT a Cohen's d
        # (there is no second-sample pooled SD); it was previously
        # misreported under the key "cohens_d", which is retained as a
        # deprecated alias.
        ses = (
            (obs_result["omega"] - null_mean) / null_std
            if null_std > 1e-12
            else 0.0
        )
        # Central 95% range of the permutation NULL distribution —
        # NOT a confidence interval for omega. Previously reported
        # under the misnomer "ci_95" (retained as a deprecated alias).
        null_ci_95 = [
            float(np.percentile(null_finite, 2.5)),
            float(np.percentile(null_finite, 97.5)),
        ]
    else:
        warnings.warn(
            f"fewer than 2 finite null omega values "
            f"({n_null_finite}); null_mean/null_std/ses/null_ci_95 "
            "are NaN.",
            UserWarning,
            stacklevel=2,
        )
        null_mean = float("nan")
        null_std = float("nan")
        ses = float("nan")
        null_ci_95 = [float("nan"), float("nan")]

    if verbose:
        print(
            f"omega={obs_result['omega']:.4f} (kn={obs_result['kn']:.6f}, "
            f"kf={obs_result['kf']:.6f})"
        )
        print(
            f"Null: mean={null_mean:.4f}, std={null_std:.4f}, "
            f"p={p_value:.4f} ({tail}), ses={ses:.2f}"
        )

    if use_reselect:
        gene_selection = (
            f"per-pair top-{n_reselect_genes} by |Δ pseudobulk| "
            "(re-selected at every permutation; HK set fixed)"
        )
    elif explicit_identity:
        gene_selection = "fixed (explicit user-provided gene set)"
    else:
        gene_selection = f"fixed (auto-detected, {func_method})"

    return _BootstrapResult(
        omega=obs_result["omega"],
        kn=obs_result["kn"],
        kf=obs_result["kf"],
        delta_hk=obs_result["delta_hk"],
        delta_identity=obs_result["delta_identity"],
        p_value=p_value,
        tail=tail,
        null_mean=null_mean,
        null_std=null_std,
        ses=ses,
        null_ci_95=null_ci_95,
        n_null_finite=n_null_finite,
        null_distribution=null_omega.tolist(),
        n_bootstrap=len(null_omega),
        gene_selection=gene_selection,
        reselect_identity=use_reselect,
    )


# Descriptive alias: bootstrap_test is a label-permutation test, not a
# bootstrap resampling procedure. The historical name is kept for
# backward compatibility.
permutation_test = bootstrap_test
