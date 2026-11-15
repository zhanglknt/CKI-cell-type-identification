"""
Reviewer fix C-A: k_f/k_n decomposition of the negative CKI-standard metric
correlation, plus partial Spearman correlations controlling for k_n.

Rationale (Pearson 1897 spurious correlation of ratios): if k_n is positively
correlated with a standard metric M and enters omega = k_f/k_n as denominator,
corr(omega, M) can be driven negative mechanically rather than informatively.

Analyses (Tabula Sapiens, n = 4,851 pairs, identical pipeline to phase35):
  A1. Spearman corr(omega, M) for the 4 standard metrics   [reproduces Fig 3A]
  A2. Spearman corr(k_f, M) and corr(k_n, M)               [decomposition]
  A3. Partial Spearman corr(omega, M | k_n)                [ratio-artifact test]
  A4. Partial Spearman corr(k_f, M | k_n)                   [numerator test]

Partial Spearman: rank-transform all variables, residualize on rank(k_n) via
OLS, then Spearman-correlate the residuals.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import spearmanr, rankdata

RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10
N_TOP_KF = 200
N_MARKER = 200

np.random.seed(RANDOM_SEED)

print("=" * 60)
print("E0. Loading TS Human data & building CT pseudobulks...")
print("=" * 60)

adatas_raw = {}
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
    if fname.exists():
        adata = sc.read_h5ad(fname)
        adata.obs["organ"] = organ
        adatas_raw[organ] = adata

all_gene_sets = [set(a.var_names) for a in adatas_raw.values()]
common_genes = sorted(all_gene_sets[0].intersection(*all_gene_sets[1:]))

adata_list = []
for organ, adata in adatas_raw.items():
    adata_sub = adata[:, common_genes].copy()
    adata_sub.obs["organ"] = organ
    adata_list.append(adata_sub)

adata = sc.concat(adata_list, axis=0, join="inner", index_unique="-")
sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().tolist())
gene_names = adata.var_names.tolist()
hk_global_idx = np.array([i for i, g in enumerate(gene_names) if g in hk_human_genes])
print(f"  Global HK genes in data: {len(hk_global_idx)}")

ct_entries = []
for organ in TS_ORGANS:
    tdata = adata[adata.obs["organ"] == organ]
    ct_labels = tdata.obs["cell_ontology_class"].value_counts()
    for ct, count in ct_labels.items():
        if ct.lower() == "unknown":
            continue
        ct_mask = tdata.obs["cell_ontology_class"] == ct
        ct_data = tdata[ct_mask]
        if ct_data.n_obs < MIN_CELLS_PER_CT * 2:
            continue
        if "donor" in ct_data.obs.columns:
            donor_counts = ct_data.obs["donor"].value_counts()
            donors_ok = [(d, n) for d, n in donor_counts.items() if n >= MIN_CELLS_PER_CT]
        else:
            donors_ok = [("pooled", ct_data.n_obs)]
        if len(donors_ok) < 1:
            continue
        donors_ok.sort(key=lambda x: -x[1])
        largest_donor = donors_ok[0][0]
        if "donor" in ct_data.obs.columns:
            mask_largest = ct_data.obs["donor"] == largest_donor
        else:
            mask_largest = slice(None)
        X_large = ct_data[mask_largest].X
        if hasattr(X_large, "toarray"):
            X_large = X_large.toarray()
        if X_large.shape[0] < MIN_CELLS_PER_CT:
            continue
        pb = np.mean(X_large, axis=0)
        ct_entries.append({
            "key": f"{organ}|{ct}",
            "organ": organ,
            "ct": ct,
            "pb": pb,
        })

n_ct = len(ct_entries)
print(f"  Viable CT entries: {n_ct}")

from cki.core import js_divergence

# Per-CT marker sets for Jaccard
ct_marker_sets = []
for i in range(n_ct):
    pb_i = ct_entries[i]["pb"]
    top_n = min(N_MARKER, len(pb_i))
    top_idx = np.argpartition(pb_i, -top_n)[-top_n:]
    ct_marker_sets.append(set(top_idx.tolist()))

rows = []
for i in range(n_ct):
    for j in range(i + 1, n_ct):
        pb_i = ct_entries[i]["pb"]
        pb_j = ct_entries[j]["pb"]

        hk_i = pb_i[hk_global_idx]
        hk_j = pb_j[hk_global_idx]
        kn_val = float(js_divergence(hk_i, hk_j))

        abs_diff = np.abs(pb_i - pb_j)
        abs_diff_non_hk = abs_diff.copy()
        abs_diff_non_hk[hk_global_idx] = -1
        top_n = min(N_TOP_KF, len(abs_diff_non_hk))
        top_idx = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
        kf_val = float(js_divergence(pb_i[top_idx], pb_j[top_idx]))
        omega_val = kf_val / kn_val if kn_val > 0 else float("inf")

        js_raw_val = float(js_divergence(pb_i, pb_j))
        rho_val, _ = spearmanr(pb_i, pb_j)
        spearman_val = 1.0 - rho_val
        dot_ij = np.dot(pb_i, pb_j)
        norm_i, norm_j = np.linalg.norm(pb_i), np.linalg.norm(pb_j)
        cos_sim = dot_ij / (norm_i * norm_j) if (norm_i > 1e-12 and norm_j > 1e-12) else 0.0
        cosine_val = 1.0 - float(np.clip(cos_sim, -1, 1))
        si, sj = ct_marker_sets[i], ct_marker_sets[j]
        union = len(si | sj)
        marker_jaccard_val = 1.0 - (len(si & sj) / union) if union > 0 else 0.0

        rows.append({
            "ct_i": ct_entries[i]["key"], "ct_j": ct_entries[j]["key"],
            "organ_i": ct_entries[i]["organ"], "organ_j": ct_entries[j]["organ"],
            "kf": kf_val, "kn": kn_val, "omega": omega_val,
            "js_raw": js_raw_val, "spearman_dist": spearman_val,
            "cosine_dist": cosine_val, "marker_jaccard_dist": marker_jaccard_val,
        })
    if (i + 1) % 20 == 0:
        print(f"  Progress: {i+1}/{n_ct}")

df = pd.DataFrame(rows)
df.to_csv(RESULTS_DIR / "reviewer_kf_kn_decomposition.csv", index=False)
print(f"\nSaved {len(df)} pairs -> results/reviewer_kf_kn_decomposition.csv")

# ============================================================
# Correlation decomposition
# ============================================================
metrics = ["js_raw", "spearman_dist", "cosine_dist", "marker_jaccard_dist"]
metric_labels = {"js_raw": "Raw JS", "spearman_dist": "Spearman dist",
                 "cosine_dist": "Cosine dist", "marker_jaccard_dist": "Marker Jaccard dist"}

def partial_spearman(x, y, z):
    """Spearman corr of x,y after residualizing both on rank(z) (OLS on ranks)."""
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    Z = np.column_stack([np.ones_like(rz), rz])
    bx, *_ = np.linalg.lstsq(Z, rx, rcond=None)
    by, *_ = np.linalg.lstsq(Z, ry, rcond=None)
    resx = rx - Z @ bx
    resy = ry - Z @ by
    r, p = spearmanr(resx, resy)
    return r, p

print("\n" + "=" * 60)
print("A1-A3. Correlation decomposition (Spearman)")
print("=" * 60)
out = []
for m in metrics:
    r_w, p_w = spearmanr(df["omega"], df[m])
    r_f, p_f = spearmanr(df["kf"], df[m])
    r_n, p_n = spearmanr(df["kn"], df[m])
    r_pw, p_pw = partial_spearman(df["omega"].values, df[m].values, df["kn"].values)
    r_pf, p_pf = partial_spearman(df["kf"].values, df[m].values, df["kn"].values)
    out.append({
        "metric": metric_labels[m],
        "corr_omega_M": r_w, "p_omega": p_w,
        "corr_kf_M": r_f, "p_kf": p_f,
        "corr_kn_M": r_n, "p_kn": p_n,
        "partial_corr_omega_M_given_kn": r_pw, "p_partial_omega": p_pw,
        "partial_corr_kf_M_given_kn": r_pf, "p_partial_kf": p_pf,
    })
    print(f"\n  {metric_labels[m]}:")
    print(f"    corr(omega, M)           = {r_w:+.3f} (P = {p_w:.2e})")
    print(f"    corr(k_f, M)             = {r_f:+.3f} (P = {p_f:.2e})")
    print(f"    corr(k_n, M)             = {r_n:+.3f} (P = {p_n:.2e})")
    print(f"    partial corr(omega, M|kn) = {r_pw:+.3f} (P = {p_pw:.2e})")
    print(f"    partial corr(k_f, M|kn)   = {r_pf:+.3f} (P = {p_pf:.2e})")

# kf-kn intercorrelation
r_fk, p_fk = spearmanr(df["kf"], df["kn"])
print(f"\n  corr(k_f, k_n) = {r_fk:+.3f} (P = {p_fk:.2e})")

res = pd.DataFrame(out)
res.loc[len(res)] = {
    "metric": "corr(k_f, k_n)",
    "corr_omega_M": r_fk, "p_omega": p_fk,
    "corr_kf_M": np.nan, "p_kf": np.nan,
    "corr_kn_M": np.nan, "p_kn": np.nan,
    "partial_corr_omega_M_given_kn": np.nan, "p_partial_omega": np.nan,
    "partial_corr_kf_M_given_kn": np.nan, "p_partial_kf": np.nan,
}
res.to_csv(RESULTS_DIR / "reviewer_decomposition_correlations.csv", index=False)
print("\nSaved -> results/reviewer_decomposition_correlations.csv")

# Bootstrap CIs (n = 1,000) for key quantities
print("\nBootstrap CIs (B = 1000)...")
rng = np.random.default_rng(RANDOM_SEED)
n = len(df)
keys = [("omega", m) for m in metrics] + [("kf", m) for m in metrics] + [("kn", m) for m in metrics]
ci_rows = []
for v, m in keys:
    stats = []
    xv, mv = df[v].values, df[m].values
    for _ in range(1000):
        idx = rng.integers(0, n, n)
        if np.std(xv[idx]) == 0 or np.std(mv[idx]) == 0:
            continue
        stats.append(spearmanr(xv[idx], mv[idx])[0])
    lo, hi = np.percentile(stats, [2.5, 97.5])
    ci_rows.append({"variable": v, "metric": metric_labels[m],
                    "spearman_r": spearmanr(xv, mv)[0], "ci_lo": lo, "ci_hi": hi})
    print(f"  corr({v}, {metric_labels[m]}): {spearmanr(xv, mv)[0]:+.3f} [{lo:+.3f}, {hi:+.3f}]")
pd.DataFrame(ci_rows).to_csv(RESULTS_DIR / "reviewer_decomposition_bootstrap_ci.csv", index=False)
print("\nSaved -> results/reviewer_decomposition_bootstrap_ci.csv")
print("\nDONE.")
