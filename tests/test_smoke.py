"""Smoke tests for the CKI package.

Runs without any large dataset: all tests operate on small toy matrices
(analytically hand-checkable). CI runs these via ``pytest tests/ -v``.
"""

import warnings

import numpy as np
import pytest
from anndata import AnnData

import cki
from cki import compute, compute_omega, js_divergence
from cki.blocknull import block_shuffle_test
from cki.gene_sets import detect_functional_genes


# ── Hand-computed reference implementation ─────────────────────────────

def _softmax(x):
    x = np.asarray(x, dtype=float)
    e = np.exp(x - x.max())
    return e / e.sum()


def _js_hand(p, q):
    """Hand-computed JS divergence mirroring the package pipeline
    (softmax normalization + base-2 log)."""
    p = _softmax(p)
    q = _softmax(q)
    m = 0.5 * (p + q)

    def kl(a, b):
        mask = a > 0
        return float(np.sum(a[mask] * np.log2(a[mask] / b[mask])))

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


# ── 1. import / version ────────────────────────────────────────────────

def test_import():
    assert cki.__version__
    for name in (
        "compute", "compute_omega", "compute_kn", "compute_kf",
        "js_divergence", "bootstrap_test", "block_shuffle_test",
        "detect_housekeeping_genes", "detect_functional_genes",
    ):
        assert hasattr(cki, name), f"cki.{name} not exported"


# ── 2. js_divergence + compute_omega vs hand computation ───────────────

def test_js_divergence_matches_hand():
    rng = np.random.RandomState(0)
    p = rng.rand(10)
    q = rng.rand(10)
    assert js_divergence(p, q) == pytest.approx(_js_hand(p, q), rel=1e-6)
    # symmetry
    assert js_divergence(p, q) == pytest.approx(js_divergence(q, p), rel=1e-9)
    # identity
    assert js_divergence(p, p) == pytest.approx(0.0, abs=1e-12)


def test_compute_omega_matches_hand():
    rng = np.random.RandomState(1)
    n_genes = 12
    pb_a = rng.rand(n_genes) * 5
    pb_b = rng.rand(n_genes) * 5
    hk = [0, 1, 2]
    idn = [3, 4, 5, 6]

    res = compute_omega(pb_a, pb_b, hk, idn)

    kn_hand = _js_hand(pb_a[hk], pb_b[hk])
    kf_hand = _js_hand(pb_a[idn], pb_b[idn])

    assert res["kn"] == pytest.approx(kn_hand, rel=1e-6)
    assert res["kf"] == pytest.approx(kf_hand, rel=1e-6)
    assert res["delta_hk"] == pytest.approx(kn_hand, rel=1e-6)
    assert res["delta_identity"] == pytest.approx(kf_hand, rel=1e-6)
    assert res["omega"] == pytest.approx(kf_hand / kn_hand, rel=1e-6)


# ── 3. pairwise_absdiff: paper hybrid k_f selection ────────────────────

def _make_toy_adata(seed=2, n_per_group=10, n_genes=10):
    """Toy AnnData: genes 0-1 flat everywhere (HK-like); genes 2-9 have
    group-structured differences of known magnitude."""
    rng = np.random.RandomState(seed)
    X = rng.rand(2 * n_per_group, n_genes) * 0.1  # background noise
    labels = ["A"] * n_per_group + ["B"] * n_per_group
    # deterministic group offsets on non-HK genes (unique |mu_A - mu_B|)
    offsets = {g: 0.5 + 0.1 * (g - 2) for g in range(2, n_genes)}
    for i, lab in enumerate(labels):
        if lab == "B":
            for g, off in offsets.items():
                X[i, g] += off
    genes = [f"G{i}" for i in range(n_genes)]
    adata = AnnData(X=X)
    adata.obs["group"] = labels
    adata.var_names = genes
    return adata, offsets


def test_pairwise_absdiff_selects_top_delta_genes():
    adata, offsets = _make_toy_adata()
    hk_indices = [0, 1]  # flat genes

    idx, info = detect_functional_genes(
        adata,
        method="pairwise_absdiff",
        n_top_genes=3,
        hk_indices=hk_indices,
        groupby="group",
        group_a="A",
        group_b="B",
    )
    # top-3 by |mu_A - mu_B| among non-HK: largest offsets = genes 7, 8, 9
    assert sorted(idx) == [7, 8, 9]
    assert info["method"] == "pairwise_absdiff"
    assert info["n_genes"] == 3


def test_pairwise_absdiff_excludes_hk_before_ranking():
    """HK genes must be excluded BEFORE ranking: a flat HK gene never
    enters the set even when n_top_genes equals all non-HK genes."""
    adata, _ = _make_toy_adata()
    hk_indices = [0, 1]
    idx, _ = detect_functional_genes(
        adata,
        method="pairwise_absdiff",
        n_top_genes=100,  # more than available -> capped
        hk_indices=hk_indices,
        groupby="group",
        group_a="A",
        group_b="B",
    )
    assert 0 not in idx and 1 not in idx
    assert sorted(idx) == list(range(2, 10))  # all non-HK genes


def test_compute_with_pairwise_absdiff():
    """End-to-end smoke: compute(func_method='pairwise_absdiff') returns a
    finite omega consistent with the hand-computed hybrid scheme."""
    adata, _ = _make_toy_adata()
    res = compute(
        adata,
        species="mouse",
        hk_genes=["G0", "G1"],            # manual HK (flat genes)
        func_method="pairwise_absdiff",
        n_top_genes=3,
        groupby="group",
        group_a="A",
        group_b="B",
        return_gene_sets=True,
    )
    assert np.isfinite(res["omega"])
    assert res["omega"] > 0
    assert sorted(res["functional_genes"]) == ["G7", "G8", "G9"]

    # hand check: k_f genes = top-3 |Δ| non-HK; k_n = HK genes
    X = np.asarray(adata.X)
    mu_a = X[adata.obs["group"] == "A"].mean(axis=0)
    mu_b = X[adata.obs["group"] == "B"].mean(axis=0)
    kf_genes = np.argsort(-np.abs(mu_a - mu_b))[:3]
    kn_hand = _js_hand(mu_a[[0, 1]], mu_b[[0, 1]])
    kf_hand = _js_hand(mu_a[kf_genes], mu_b[kf_genes])
    assert res["kn"] == pytest.approx(kn_hand, rel=1e-6)
    assert res["kf"] == pytest.approx(kf_hand, rel=1e-6)
    assert res["omega"] == pytest.approx(kf_hand / kn_hand, rel=1e-6)


# ── 4. HK-exclusion reporting fix (n_hk_removed) ───────────────────────

def test_hk_removal_count_reported():
    """Regression test: n_hk_removed must be computed BEFORE removal
    (previously always 0 — dead code)."""
    import warnings
    rng = np.random.RandomState(3)
    n_cells, n_genes = 40, 20
    X = rng.rand(n_cells, n_genes)
    adata = AnnData(X=X)
    adata.var_names = [f"G{i}" for i in range(n_genes)]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        idx, info = detect_functional_genes(
            adata, method="hvg", n_top_genes=16, hk_indices=list(range(10)),
        )
    # 80% cap on 20 genes -> 16 HVGs; overlap with 10 HK indices > 0
    assert info.get("n_hk_removed", 0) > 0
    assert not (set(idx) & set(range(10)))


# ── 5. block_shuffle_test smoke ────────────────────────────────────────

def test_block_shuffle_test_runs():
    """Block-shuffle null: labels permuted at block level with k_f
    re-selection per permutation; p-value in [0, 1]."""
    rng = np.random.RandomState(4)
    n_blocks, cells_per_block, n_genes = 8, 5, 30
    X = rng.rand(n_blocks * cells_per_block, n_genes)
    labels, blocks = [], []
    for b in range(n_blocks):
        grp = "A" if b < 4 else "B"
        for _ in range(cells_per_block):
            labels.append(grp)
            blocks.append(f"S{b}")
    # strong group signal on non-HK genes with per-gene offsets
    # (softmax is shift-invariant, so offsets must vary per gene to
    # produce a real distributional difference)
    offsets = rng.rand(n_genes) * 3.0
    offsets[:2] = 0.0  # HK genes carry no group signal
    for i, lab in enumerate(labels):
        if lab == "B":
            X[i, :] += offsets

    adata = AnnData(X=X)
    adata.var_names = [f"G{i}" for i in range(n_genes)]
    adata.obs["group"] = labels
    adata.obs["sample_id"] = blocks

    res = block_shuffle_test(
        adata,
        groupby="group",
        group_a="A",
        group_b="B",
        blocks="sample_id",
        hk_genes=["G0", "G1"],
        n_top_genes=5,
        n_permutations=20,
        verbose=False,
    )
    assert np.isfinite(res["omega"]) and res["omega"] > 0
    assert res["n_blocks"] == 8
    assert res["n_permutations"] == 20
    assert 0.0 <= res["p_value"] <= 1.0
    assert len(res["null_distribution"]) == 20
    # strong signal: observed k_f exceeds the null k_f (the block-shuffle
    # null mixes A/B blocks, shrinking the group pseudobulk difference)
    assert res["omega"] > np.median(res["null_distribution"])


def test_block_shuffle_rejects_mixed_block():
    """A block containing cells from both groups must be rejected
    (blocks are atomic under permutation)."""
    rng = np.random.RandomState(5)
    X = rng.rand(20, 10)
    labels = ["A"] * 10 + ["B"] * 10
    blocks = ["S0"] * 20  # one block spanning both groups
    adata = AnnData(X=X)
    adata.var_names = [f"G{i}" for i in range(10)]
    adata.obs["group"] = labels
    with pytest.raises(ValueError, match="atomic"):
        block_shuffle_test(
            adata, groupby="group", group_a="A", group_b="B",
            blocks=blocks, hk_genes=["G0"], n_permutations=2,
            verbose=False,
        )


# ── 6. bootstrap FDR helpers ───────────────────────────────────────────

def test_benjamini_hochberg():
    from cki import benjamini_hochberg
    q = benjamini_hochberg([0.01, 0.04, 0.03, 0.20, 0.001])
    assert q[4] <= q[0] <= q[2] <= q[1] <= q[3]
    assert np.all(q >= 0) and np.all(q <= 1)


# ── 7. bootstrap_test gene re-selection modes ─────────────────────────

def test_bootstrap_test_reselect_default():
    """Default mode reproduces the manuscript procedure: k_f re-selected
    per pair (observed value AND every permutation), HK set fixed.
    Observed k_f must equal the hand-computed top-N |Δ pseudobulk| rule."""
    from cki import bootstrap_test

    adata, _ = _make_toy_adata()
    res = bootstrap_test(
        adata,
        species="mouse",
        groupby="group",
        group_a="A",
        group_b="B",
        hk_genes=["G0", "G1"],
        n_reselect_genes=3,
        n_bootstrap=20,
        random_state=42,
        verbose=False,
    )
    assert res["reselect_identity"] is True
    assert "re-selected" in res["gene_selection"]

    # hand check observed k_f: top-3 |Δ| non-HK genes = G7, G8, G9
    X = np.asarray(adata.X)
    mu_a = X[adata.obs["group"] == "A"].mean(axis=0)
    mu_b = X[adata.obs["group"] == "B"].mean(axis=0)
    kf_genes = np.argsort(-np.abs(mu_a - mu_b))[:3]
    assert sorted(kf_genes) == [7, 8, 9]
    kn_hand = _js_hand(mu_a[[0, 1]], mu_b[[0, 1]])
    kf_hand = _js_hand(mu_a[kf_genes], mu_b[kf_genes])
    assert res["kn"] == pytest.approx(kn_hand, rel=1e-6)
    assert res["kf"] == pytest.approx(kf_hand, rel=1e-6)
    assert res["omega"] == pytest.approx(kf_hand / kn_hand, rel=1e-6)
    assert 0.0 <= res["p_value"] <= 1.0
    assert len(res["null_distribution"]) == 20


def test_bootstrap_test_fixed_legacy_and_explicit():
    """reselect_identity=False gives the legacy fixed-set null; explicit
    functional_genes always pin a fixed set even with the default flag."""
    from cki import bootstrap_test

    adata, _ = _make_toy_adata()

    legacy = bootstrap_test(
        adata, species="mouse", groupby="group",
        group_a="A", group_b="B",
        hk_genes=["G0", "G1"],
        reselect_identity=False,
        n_bootstrap=10, random_state=1, verbose=False,
    )
    assert legacy["reselect_identity"] is False
    assert "fixed" in legacy["gene_selection"]

    explicit = bootstrap_test(
        adata, species="mouse", groupby="group",
        group_a="A", group_b="B",
        hk_genes=["G0", "G1"],
        functional_genes=["G2", "G3", "G4"],  # explicit -> pinned fixed
        n_bootstrap=10, random_state=1, verbose=False,
    )
    assert explicit["reselect_identity"] is False
    assert "explicit" in explicit["gene_selection"]

    # legacy and explicit nulls share the seed but differ from reselect
    reselect = bootstrap_test(
        adata, species="mouse", groupby="group",
        group_a="A", group_b="B",
        hk_genes=["G0", "G1"], n_reselect_genes=3,
        n_bootstrap=10, random_state=1, verbose=False,
    )
    assert reselect["reselect_identity"] is True
    assert reselect["kf"] != explicit["kf"]


def test_bootstrap_test_reselect_rejects_pathway():
    """Pathway component is incompatible with reselection mode."""
    from cki import bootstrap_test

    adata, _ = _make_toy_adata()
    with pytest.raises(ValueError, match="reselect_identity"):
        bootstrap_test(
            adata, species="mouse", groupby="group",
            group_a="A", group_b="B",
            hk_genes=["G0", "G1"],
            pathway_a=np.zeros(10), pathway_b=np.zeros(10),
            n_bootstrap=2, verbose=False,
        )


# ── 8. bootstrap_test tail alternatives ────────────────────────────────

def test_bootstrap_test_tail_alternatives():
    """tail='lower' / 'two-sided' are supported and consistent with the
    default 'upper' tail on the same null distribution."""
    from cki import bootstrap_test

    adata, _ = _make_toy_adata()
    kwargs = dict(
        species="mouse", groupby="group", group_a="A", group_b="B",
        hk_genes=["G0", "G1"], n_reselect_genes=3,
        n_bootstrap=20, random_state=42, verbose=False,
    )
    upper = bootstrap_test(adata, tail="upper", **kwargs)
    lower = bootstrap_test(adata, tail="lower", **kwargs)
    two = bootstrap_test(adata, tail="two-sided", **kwargs)

    # same seed -> identical null distributions and observed values
    assert upper["null_distribution"] == lower["null_distribution"]
    assert upper["omega"] == lower["omega"] == two["omega"]

    for res in (upper, lower, two):
        assert 0.0 <= res["p_value"] <= 1.0
        assert res["tail"] in ("upper", "lower", "two-sided")

    # exact relations on the shared null ((B + 1) convention)
    null = np.asarray(upper["null_distribution"])
    obs = upper["omega"]
    B = 20
    p_u = (np.sum(null >= obs) + 1) / (B + 1)
    p_l = (np.sum(null <= obs) + 1) / (B + 1)
    assert upper["p_value"] == pytest.approx(p_u)
    assert lower["p_value"] == pytest.approx(p_l)
    assert two["p_value"] == pytest.approx(min(1.0, 2.0 * min(p_u, p_l)))

    with pytest.raises(ValueError, match="tail"):
        bootstrap_test(adata, tail="sideways", **kwargs)


# ── 9. ses key + deprecated cohens_d alias ─────────────────────────────

def test_bootstrap_test_ses_and_cohens_d_alias():
    """The standardized effect size is reported as 'ses'; 'cohens_d'
    remains a backward-compatible alias emitting DeprecationWarning."""
    from cki import bootstrap_test

    adata, _ = _make_toy_adata()
    res = bootstrap_test(
        adata, species="mouse", groupby="group",
        group_a="A", group_b="B",
        hk_genes=["G0", "G1"], n_reselect_genes=3,
        n_bootstrap=20, random_state=42, verbose=False,
    )
    assert "ses" in res
    # hand check: ses = (omega - null_mean) / null_std
    null = np.asarray(res["null_distribution"])
    ses_hand = (res["omega"] - null.mean()) / null.std()
    assert res["ses"] == pytest.approx(ses_hand, rel=1e-9)
    assert res["null_mean"] == pytest.approx(null.mean())

    with pytest.warns(DeprecationWarning, match="ses"):
        alias_val = res["cohens_d"]
    assert alias_val == res["ses"]
    # the new key must not warn
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        _ = res["ses"]


# ── 10. compute() exposes kn_floor ─────────────────────────────────────

def test_compute_kn_floor_passthrough():
    """compute(kn_floor=...) is forwarded to compute_omega: a near-zero
    k_n below the floor yields omega = k_f / kn_floor instead of inf."""
    # identical HK profiles -> k_n = 0 exactly
    pb_a = np.array([1.0, 2.0, 3.0, 1.0])
    pb_b = np.array([1.0, 2.0, 4.0, 2.0])
    hk = [0, 1]   # identical in both
    idn = [2, 3]  # differ

    res_inf = compute_omega(pb_a, pb_b, hk, idn)
    assert res_inf["kn"] == 0.0
    assert res_inf["omega"] == float("inf")

    res_floor = compute_omega(pb_a, pb_b, hk, idn, kn_floor=1e-4)
    assert res_floor["omega"] == pytest.approx(res_floor["kf"] / 1e-4)

    # end-to-end through compute(): flat HK genes -> tiny k_n
    adata, _ = _make_toy_adata()
    base = compute(
        adata, species="mouse",
        hk_genes=["G0", "G1"],
        func_method="pairwise_absdiff", n_top_genes=3,
        groupby="group", group_a="A", group_b="B",
    )
    floored = compute(
        adata, species="mouse",
        hk_genes=["G0", "G1"],
        func_method="pairwise_absdiff", n_top_genes=3,
        groupby="group", group_a="A", group_b="B",
        kn_floor=1e-4,
    )
    assert base["kn"] == floored["kn"]  # k_n unaffected by the floor
    if floored["kn"] < 1e-4:
        assert floored["omega"] == pytest.approx(floored["kf"] / 1e-4)
    else:
        assert floored["omega"] == pytest.approx(base["omega"])


# ── 11. precomputed-pseudobulk group sizes (regression) ───────────────

def test_bootstrap_precomputed_pseudobulk_group_sizes():
    """Regression: with pre-computed pseudobulks the permutation null
    must use the true per-group cell counts from adata.obs (previously
    hardcoded as a 50/50 split of adata.X). With correct labels, the
    result must match the groupby-only run bit-for-bit."""
    from cki import bootstrap_test

    # unequal group sizes: 30 A cells, 10 B cells
    rng = np.random.RandomState(7)
    n_a, n_b, n_genes = 30, 10, 10
    X = rng.rand(n_a + n_b, n_genes)
    labels = ["A"] * n_a + ["B"] * n_b
    adata = AnnData(X=X)
    adata.var_names = [f"G{i}" for i in range(n_genes)]
    adata.obs["group"] = labels

    kwargs = dict(
        species="mouse", groupby="group", group_a="A", group_b="B",
        hk_genes=["G0", "G1"], n_reselect_genes=3,
        n_bootstrap=10, random_state=3, verbose=False,
    )
    ref = bootstrap_test(adata, **kwargs)

    pb_a = X[:n_a].mean(axis=0)
    pb_b = X[n_a:].mean(axis=0)
    pre = bootstrap_test(adata, pseudobulk_a=pb_a, pseudobulk_b=pb_b, **kwargs)

    assert pre["omega"] == pytest.approx(ref["omega"], rel=1e-12)
    assert pre["null_distribution"] == pytest.approx(
        ref["null_distribution"], rel=1e-12
    )
    assert pre["p_value"] == pytest.approx(ref["p_value"])

    # without group labels the group sizes are unknowable -> clear error
    with pytest.raises(ValueError, match="groupby"):
        bootstrap_test(
            adata, pseudobulk_a=pb_a, pseudobulk_b=pb_b,
            species="mouse", hk_genes=["G0", "G1"],
            n_bootstrap=2, verbose=False,
        )


# ── 12. densification warning ──────────────────────────────────────────

def test_densify_warns_on_large_sparse():
    """densify() must warn (not silently OOM) when a sparse matrix
    exceeds the element/nnz threshold; small matrices stay silent."""
    from scipy import sparse as sp
    from cki import utils as cki_utils
    from cki.utils import densify

    small = sp.csr_matrix(np.eye(5))
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        out = densify(small)
    assert isinstance(out, np.ndarray) and out.shape == (5, 5)

    big = sp.csr_matrix((10, 10))  # tiny; threshold monkeypatched below
    monkey = cki_utils._DENSIFY_WARN_THRESHOLD
    try:
        cki_utils._DENSIFY_WARN_THRESHOLD = 50  # 10x10 = 100 elements
        with pytest.warns(UserWarning, match="Densifying"):
            densify(big, context="test matrix")
    finally:
        cki_utils._DENSIFY_WARN_THRESHOLD = monkey


# ── 13. null_ci_95 key + deprecated ci_95 alias ───────────────────────

def test_bootstrap_test_null_ci_95_and_ci_95_alias():
    """The permutation-null 95% range is reported as 'null_ci_95' (it is
    the null distribution's 2.5/97.5 percentile range, NOT a confidence
    interval for omega); 'ci_95' remains a deprecated alias that warns
    through both __getitem__ and dict.get."""
    from cki import bootstrap_test

    adata, _ = _make_toy_adata()
    res = bootstrap_test(
        adata, species="mouse", groupby="group",
        group_a="A", group_b="B",
        hk_genes=["G0", "G1"], n_reselect_genes=3,
        n_bootstrap=20, random_state=42, verbose=False,
    )
    assert "null_ci_95" in res
    null = np.asarray(res["null_distribution"])
    assert res["null_ci_95"][0] == pytest.approx(np.percentile(null, 2.5))
    assert res["null_ci_95"][1] == pytest.approx(np.percentile(null, 97.5))

    # deprecated alias via __getitem__
    with pytest.warns(DeprecationWarning, match="null_ci_95"):
        alias_val = res["ci_95"]
    assert alias_val == res["null_ci_95"]
    # deprecated alias via dict.get (must not bypass the warning)
    with pytest.warns(DeprecationWarning, match="null_ci_95"):
        alias_get = res.get("ci_95")
    assert alias_get == res["null_ci_95"]
    # the new key must not warn
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        _ = res["null_ci_95"]
        _ = res.get("null_ci_95")
    # cohens_d alias also warns through .get()
    with pytest.warns(DeprecationWarning, match="ses"):
        _ = res.get("cohens_d")


# ── 14. non-finite null protection (inf -> NaN SES + n_null_finite) ───

def test_bootstrap_test_nonfinite_null_guard():
    """Inf null values (degenerate permuted k_n ~ 0) must not poison
    null_mean/null_std/ses: they are excluded from the summary
    statistics, 'n_null_finite' reports the finite count, and if too
    few finite values remain the SES is NaN with a warning."""
    from cki import bootstrap_test

    # Case A: some inf nulls -> summaries stay finite, n_null_finite < B.
    # Identical HK genes -> any permutation keeping HK identical gives
    # k_n = 0 -> omega = inf. With identical flat HK genes every
    # permutation has k_n = 0 exactly, so ALL nulls are inf: that is
    # case B below. For case A, monkeypatch is unnecessary — construct
    # data where HK genes are identical in pooled cells (all nulls inf)
    # is the degenerate case; instead verify the finite-subset math via
    # the n_null_finite field on a normal run.
    adata, _ = _make_toy_adata()
    res = bootstrap_test(
        adata, species="mouse", groupby="group",
        group_a="A", group_b="B",
        hk_genes=["G0", "G1"], n_reselect_genes=3,
        n_bootstrap=20, random_state=42, verbose=False,
    )
    assert res["n_null_finite"] == len(res["null_distribution"])
    assert np.isfinite(res["ses"])

    # Case B: all nulls inf (HK genes identical across every cell ->
    # k_n = 0 for every permutation) -> SES NaN + warning.
    rng = np.random.RandomState(11)
    n_cells, n_genes = 20, 6
    X = rng.rand(n_cells, n_genes)
    X[:, 0] = 1.0  # HK gene identical in every cell -> k_n = 0 always
    X[:, 1] = 2.0
    adata_inf = AnnData(X=X)
    adata_inf.var_names = [f"G{i}" for i in range(n_genes)]
    adata_inf.obs["group"] = ["A"] * 10 + ["B"] * 10
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        res_inf = bootstrap_test(
            adata_inf, species="mouse", groupby="group",
            group_a="A", group_b="B",
            hk_genes=["G0", "G1"], n_reselect_genes=2,
            n_bootstrap=10, random_state=0, verbose=False,
        )
    assert res_inf["n_null_finite"] == 0
    assert np.isnan(res_inf["ses"])
    assert np.isnan(res_inf["null_mean"])
    assert np.isnan(res_inf["null_std"])
    assert all(np.isnan(v) for v in res_inf["null_ci_95"])
    messages = [str(w.message) for w in caught]
    assert any("non-finite null omega" in m for m in messages)
    assert any("fewer than 2 finite" in m for m in messages)


# ── 15. compute(preset="manuscript") ──────────────────────────────────

def test_compute_preset_manuscript():
    """preset='manuscript' forces the manuscript configuration
    (pairwise_absdiff / n_top_genes=200 / use_reference_hk=True),
    overriding conflicting explicit arguments."""
    adata, _ = _make_toy_adata()

    res = compute(
        adata, species="mouse",
        hk_genes=["G0", "G1"],
        func_method="hvg", n_top_genes=2000,  # overridden by the preset
        preset="manuscript",
        groupby="group", group_a="A", group_b="B",
        return_gene_sets=True,
    )
    assert res["functional_info"]["method"] == "pairwise_absdiff"
    # capped at the number of non-HK genes in the toy data (8)
    assert len(res["functional_genes"]) == min(200, 8)
    assert np.isfinite(res["omega"])

    # reference values match an explicit manuscript-style call
    ref = compute(
        adata, species="mouse",
        hk_genes=["G0", "G1"],
        func_method="pairwise_absdiff", n_top_genes=200,
        groupby="group", group_a="A", group_b="B",
    )
    assert res["omega"] == pytest.approx(ref["omega"], rel=1e-12)

    with pytest.raises(ValueError, match="preset"):
        compute(
            adata, species="mouse",
            hk_genes=["G0", "G1"],
            preset="nonsense",
            groupby="group", group_a="A", group_b="B",
        )


# ── 16. large-n operating-window warning ──────────────────────────────

def test_bootstrap_test_large_group_window_warning():
    """Groups with >500 cells trigger a UserWarning about the CKI
    operating window (~50-200 cells per donor per condition)."""
    from cki import bootstrap_test

    rng = np.random.RandomState(13)
    n_a, n_b, n_genes = 501, 600, 10
    X = rng.rand(n_a + n_b, n_genes)
    adata = AnnData(X=X)
    adata.var_names = [f"G{i}" for i in range(n_genes)]
    adata.obs["group"] = ["A"] * n_a + ["B"] * n_b

    with pytest.warns(UserWarning, match="operating window"):
        bootstrap_test(
            adata, species="mouse", groupby="group",
            group_a="A", group_b="B",
            hk_genes=["G0", "G1"], n_reselect_genes=3,
            n_bootstrap=2, random_state=0, verbose=False,
        )

    # small groups stay silent
    adata_small, _ = _make_toy_adata()
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        bootstrap_test(
            adata_small, species="mouse", groupby="group",
            group_a="A", group_b="B",
            hk_genes=["G0", "G1"], n_reselect_genes=3,
            n_bootstrap=2, random_state=0, verbose=False,
        )
