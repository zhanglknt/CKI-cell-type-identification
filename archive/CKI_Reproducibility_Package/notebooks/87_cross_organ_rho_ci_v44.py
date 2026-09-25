# -*- coding: utf-8 -*-
"""
Cross-organ rank concordance: bootstrap CI for the CT-level Spearman rho
=========================================================================

Existing conclusion (notebook 83 Part A, kf_only_ordering.{csv,json,txt}):
across 17 Tabula Sapiens cell types, the per-cell-type mean cross-organ
omega ranks vs mean k_f ranks give Spearman r = 0.233 (P = 0.368;
well-sampled subset r = 0.100) -- i.e. the cross-organ conservation
ranking is NOT recovered by k_f alone; omega is a composite of
functional divergence (k_f) and baseline stability (k_n). No interval
estimate existed for this correlation.

This script rebuilds the 83 Part A pipeline verbatim (largest-donor
pseudobulk per organ|cell-type, common genes, log1p, HK from
Human_Mouse_Common.csv, per-pair top-200 non-HK |delta| k_f genes,
softmax JS exactly as published -- this analysis only ADDS uncertainty
quantification to the published numbers, it does not change the
probability mapping), verifies the per-CT means against
results/phase35_cross_organ_summary.csv (assert < 1e-9, same sanity
check as 83), and then computes bootstrap CIs:

  Primary: joint organ-clustered bootstrap (B=1000, seed 42), mirroring
  the region-clustered scheme of 81_perclass_uncertainty.py: per cell
  type, resample its organs with replacement; a pair enters with weight
  mult(organ_i) * mult(organ_j); per-CT weighted mean omega / k_f / k_n;
  Spearman across the 17 CTs. Replicates in which any CT has zero total
  weight are redrawn (while-loop, as in 74).

  Sensitivity: classical CT-level bootstrap (resample the 17 CT point
  estimates with replacement), B=1000.

Outputs (NEW files, _v44 suffix):
  results/cross_organ_rho_ci_v44.csv
  results/cross_organ_rho_ci_v44.json
  results/cross_organ_rho_ci_v44.txt
"""
import sys, os, json, time, warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")

from cki.core import js_divergence

RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10
N_TOP_KF = 200
N_BOOT = 1000
MAX_ATTEMPTS = 200000

t0 = time.time()

# ====================================================================
# PART A rebuild: cross-organ pairs (verbatim from 83_kf_only_ordering.py)
# ====================================================================
print("=" * 60)
print("Rebuilding 83 Part A cross-organ pairs (published pipeline)...")
print("=" * 60)

adatas_raw = {}
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
    if fname.exists():
        a = sc.read_h5ad(fname, backed="r")
        adatas_raw[organ] = set(a.var_names)
        a.file.close()
        print(f"  TS_{organ}: var_names read (backed)")

all_gene_sets = list(adatas_raw.values())
common_genes = sorted(all_gene_sets[0].intersection(*all_gene_sets[1:]))

# Memory-equivalent re-implementation of 83's
#   concat -> filter_cells(500) -> filter_genes(3) -> normalize_total -> log1p
# without ever concatenating (the 11 GB concat subset exceeds RAM on this
# machine). Every step is per-cell or a gene-detection count, so the
# per-organ decomposition is mathematically identical; the phase35 sanity
# assert below verifies equivalence numerically.
organ_data = {}
det_counts = np.zeros(len(common_genes), dtype=np.int64)
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
    a = sc.read_h5ad(fname)
    a = a[:, common_genes].copy()
    sc.pp.filter_cells(a, min_genes=500)          # per-cell: identical to post-concat
    X = a.X.tocsr()
    det_counts += np.asarray((X > 0).sum(axis=0)).ravel()
    organ_data[organ] = {"X": X,
                         "obs": a.obs[["cell_ontology_class", "donor"]].copy()}
    del a
    print(f"  TS_{organ}: {X.shape[0]} cells after min_genes=500")

keep_gene = det_counts >= 3                        # filter_genes(min_cells=3) across all organs
kept_genes = [g for g, k in zip(common_genes, keep_gene) if k]
gene_names = kept_genes

for organ in TS_ORGANS:
    X = organ_data[organ]["X"][:, keep_gene].copy()
    a = sc.AnnData(X=X, obs=organ_data[organ]["obs"],
                   var=pd.DataFrame(index=kept_genes))
    sc.pp.normalize_total(a, target_sum=1e4)      # per-cell: identical to post-concat
    sc.pp.log1p(a)
    organ_data[organ]["X"] = a.X.tocsr()
    del a, X

n_cells_total = sum(organ_data[o]["X"].shape[0] for o in TS_ORGANS)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().tolist())
hk_global_idx = np.array([i for i, g in enumerate(gene_names) if g in hk_human_genes])
print(f"  Unified: {n_cells_total} cells x {len(gene_names)} genes; HK: {len(hk_global_idx)}")

ct_entries = []
for organ in TS_ORGANS:
    obs = organ_data[organ]["obs"]
    X_organ = organ_data[organ]["X"]
    ct_labels = obs["cell_ontology_class"].value_counts()
    for ct, count in ct_labels.items():
        if ct.lower() == "unknown":
            continue
        ct_mask = (obs["cell_ontology_class"] == ct).values
        if ct_mask.sum() < MIN_CELLS_PER_CT * 2:
            continue
        obs_ct = obs[ct_mask]
        if "donor" in obs_ct.columns:
            donor_counts = obs_ct["donor"].value_counts()
            donors_ok = [(d, n) for d, n in donor_counts.items() if n >= MIN_CELLS_PER_CT]
        else:
            donors_ok = [("pooled", int(ct_mask.sum()))]
        if len(donors_ok) < 1:
            continue
        donors_ok.sort(key=lambda x: -x[1])
        largest_donor = donors_ok[0][0]
        if "donor" in obs_ct.columns:
            mask_largest = (obs_ct["donor"] == largest_donor).values
        else:
            mask_largest = slice(None)
        X_large = X_organ[ct_mask][mask_largest]
        if hasattr(X_large, "toarray"):
            X_large = X_large.toarray()
        if X_large.shape[0] < MIN_CELLS_PER_CT:
            continue
        pb = np.mean(X_large, axis=0)
        ct_entries.append({"key": f"{organ}|{ct}", "organ": organ, "ct": ct,
                           "pb": np.asarray(pb).ravel()})

del organ_data

n_ct_entries = len(ct_entries)
print(f"  Viable CT entries: {n_ct_entries}")

rows = []
for i in range(n_ct_entries):
    for j in range(i + 1, n_ct_entries):
        if ct_entries[i]["ct"] != ct_entries[j]["ct"]:
            continue
        if ct_entries[i]["organ"] == ct_entries[j]["organ"]:
            continue
        pb_i = ct_entries[i]["pb"]
        pb_j = ct_entries[j]["pb"]

        hk_i = pb_i[hk_global_idx]
        hk_j = pb_j[hk_global_idx]
        kn_val = float(js_divergence(hk_i, hk_j))

        abs_diff = np.abs(pb_i - pb_j)
        non_hk_mask = np.ones(len(gene_names), dtype=bool)
        non_hk_mask[hk_global_idx] = False
        abs_diff_non_hk = abs_diff.copy()
        abs_diff_non_hk[hk_global_idx] = -1
        top_n = min(N_TOP_KF, non_hk_mask.sum())
        top_idx = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
        top_idx = top_idx[np.argsort(abs_diff_non_hk[top_idx])[::-1]]
        kf_val = float(js_divergence(pb_i[top_idx], pb_j[top_idx]))
        omega_val = kf_val / kn_val if kn_val > 0 else float("inf")

        rows.append({
            "ct": ct_entries[i]["ct"],
            "organ_i": ct_entries[i]["organ"],
            "organ_j": ct_entries[j]["organ"],
            "omega": omega_val,
            "kf": kf_val,
            "kn": kn_val,
        })

pairs_df = pd.DataFrame(rows)
print(f"\n  Same-CT cross-organ pairs: {len(pairs_df)} ({pairs_df['ct'].nunique()} cell types)")

# --- Per-CT aggregation + sanity vs phase35 (verbatim 83) ---
grp = pairs_df.groupby("ct").agg(
    n_pairs=("omega", "count"),
    mean_omega=("omega", "mean"),
    mean_kf=("kf", "mean"),
    mean_kn=("kn", "mean"),
).reset_index().sort_values("mean_omega").reset_index(drop=True)

ref = pd.read_csv(RESULTS_DIR / "phase35_cross_organ_summary.csv")
merged = grp.merge(ref, on="ct", suffixes=("_new", "_ref"))
max_delta = float(np.max(np.abs(merged["mean_omega_new"] - merged["mean_omega_ref"])))
print(f"  Sanity vs phase35_cross_organ_summary.csv: max |delta mean omega| = {max_delta:.2e} "
      f"over {len(merged)}/{len(ref)} CTs")
assert max_delta < 1e-9, "Rebuild does NOT reproduce phase35 summary!"

grp["well_sampled"] = grp["n_pairs"] >= 5
ws_cts = set(grp.loc[grp["well_sampled"], "ct"])

r_ct_kf, p_ct_kf = spearmanr(grp["mean_omega"], grp["mean_kf"])
r_ct_kn, p_ct_kn = spearmanr(grp["mean_omega"], grp["mean_kn"])
ws = grp[grp["well_sampled"]]
r_ws_kf, p_ws_kf = spearmanr(ws["mean_omega"], ws["mean_kf"])
r_ws_kn, p_ws_kn = spearmanr(ws["mean_omega"], ws["mean_kn"])
r_pair, p_pair = spearmanr(pairs_df["omega"], pairs_df["kf"])
print(f"  Point estimates: CT-level r(omega,kf)={r_ct_kf:.3f} (P={p_ct_kf:.3f}); "
      f"r(omega,kn)={r_ct_kn:.3f}; well-sampled r(omega,kf)={r_ws_kf:.3f}; "
      f"pair-level r={r_pair:.3f}")

# ====================================================================
# Joint organ-clustered bootstrap (mirrors 81's region-clustered scheme)
# ====================================================================
print(f"\nJoint organ-clustered bootstrap (B={N_BOOT}, seed {RANDOM_SEED})...")
rng = np.random.default_rng(RANDOM_SEED)

pairs_by_ct = {ct: g.reset_index(drop=True) for ct, g in pairs_df.groupby("ct")}
ct_list = list(pairs_by_ct.keys())
n_cts = len(ct_list)

# precompute per-CT organ index structures
ct_struct = {}
for ct, gp in pairs_by_ct.items():
    organs = sorted(set(gp["organ_i"]) | set(gp["organ_j"]))
    pos = {o: k for k, o in enumerate(organs)}
    ct_struct[ct] = {
        "n_organs": len(organs),
        "ia": np.array([pos[o] for o in gp["organ_i"].values]),
        "ib": np.array([pos[o] for o in gp["organ_j"].values]),
        "omega": gp["omega"].values,
        "kf": gp["kf"].values,
        "kn": gp["kn"].values,
    }

boot_kf_all, boot_kn_all = [], []
boot_kf_ws, boot_kn_ws = [], []
ct_list_arr = list(ct_list)
ws_mask = np.array([ct in ws_cts for ct in ct_list_arr])
n_ok = 0
while n_ok < N_BOOT:
    mo = np.empty(n_cts); mk = np.empty(n_cts); mn = np.empty(n_cts)
    for k, ct in enumerate(ct_list_arr):
        s = ct_struct[ct]
        # per-CT rejection sampling: redraw this CT's organs until the
        # draw covers >= 2 organs (nonzero total pair weight). Each CT's
        # bootstrap marginal is unchanged; this avoids rejecting the
        # whole 17-CT replicate when any single 2-organ CT degenerates.
        for _ in range(1000):
            mult = np.bincount(rng.integers(0, s["n_organs"], size=s["n_organs"]),
                               minlength=s["n_organs"]).astype(float)
            w = mult[s["ia"]] * mult[s["ib"]]
            if w.sum() > 0:
                break
        mo[k] = np.average(s["omega"], weights=w)
        mk[k] = np.average(s["kf"], weights=w)
        mn[k] = np.average(s["kn"], weights=w)
    rk, _ = spearmanr(mo, mk)
    rn, _ = spearmanr(mo, mn)
    boot_kf_all.append(rk)
    boot_kn_all.append(rn)
    rk_ws, _ = spearmanr(mo[ws_mask], mk[ws_mask])
    rn_ws, _ = spearmanr(mo[ws_mask], mn[ws_mask])
    boot_kf_ws.append(rk_ws)
    boot_kn_ws.append(rn_ws)
    n_ok += 1
    if n_ok % 200 == 0:
        print(f"    {n_ok}/{N_BOOT} ({time.time()-t0:.0f}s)")
n_attempts = n_ok

boot_kf_all = np.array(boot_kf_all); boot_kn_all = np.array(boot_kn_all)
boot_kf_ws = np.array(boot_kf_ws);   boot_kn_ws = np.array(boot_kn_ws)

def ci(arr):
    lo, hi = np.percentile(arr, [2.5, 97.5])
    return float(np.median(arr)), float(lo), float(hi)

# --- sensitivity: classical CT-level bootstrap on point estimates ---
rng2 = np.random.default_rng(RANDOM_SEED + 1)
ctb_kf, ctb_kn = [], []
ow = grp["mean_omega"].values; kw = grp["mean_kf"].values; nw = grp["mean_kn"].values
for b in range(N_BOOT):
    idx = rng2.integers(0, n_cts, size=n_cts)
    rk, _ = spearmanr(ow[idx], kw[idx])
    rn, _ = spearmanr(ow[idx], nw[idx])
    ctb_kf.append(rk); ctb_kn.append(rn)
ctb_kf = np.array(ctb_kf); ctb_kn = np.array(ctb_kn)

# ====================================================================
# Outputs
# ====================================================================
rows_out = [
    {"statistic": "CT-level Spearman rho(mean_omega, mean_kf), all 17 CTs",
     "point": r_ct_kf, "point_p": p_ct_kf,
     "cluster_boot_median": ci(boot_kf_all)[0], "ci_lo": ci(boot_kf_all)[1], "ci_hi": ci(boot_kf_all)[2],
     "ct_boot_median": ci(ctb_kf)[0], "ct_ci_lo": ci(ctb_kf)[1], "ct_ci_hi": ci(ctb_kf)[2]},
    {"statistic": "CT-level Spearman rho(mean_omega, mean_kn), all 17 CTs",
     "point": r_ct_kn, "point_p": p_ct_kn,
     "cluster_boot_median": ci(boot_kn_all)[0], "ci_lo": ci(boot_kn_all)[1], "ci_hi": ci(boot_kn_all)[2],
     "ct_boot_median": ci(ctb_kn)[0], "ct_ci_lo": ci(ctb_kn)[1], "ct_ci_hi": ci(ctb_kn)[2]},
    {"statistic": "CT-level Spearman rho(mean_omega, mean_kf), well-sampled (n_pairs>=5)",
     "point": r_ws_kf, "point_p": p_ws_kf,
     "cluster_boot_median": ci(boot_kf_ws)[0], "ci_lo": ci(boot_kf_ws)[1], "ci_hi": ci(boot_kf_ws)[2],
     "ct_boot_median": np.nan, "ct_ci_lo": np.nan, "ct_ci_hi": np.nan},
    {"statistic": "CT-level Spearman rho(mean_omega, mean_kn), well-sampled (n_pairs>=5)",
     "point": r_ws_kn, "point_p": p_ws_kn,
     "cluster_boot_median": ci(boot_kn_ws)[0], "ci_lo": ci(boot_kn_ws)[1], "ci_hi": ci(boot_kn_ws)[2],
     "ct_boot_median": np.nan, "ct_ci_lo": np.nan, "ct_ci_hi": np.nan},
]
out = pd.DataFrame(rows_out)
out.to_csv(RESULTS_DIR / "cross_organ_rho_ci_v44.csv", index=False)

summary = {
    "n_boot": N_BOOT, "seed": RANDOM_SEED, "n_valid_replicates": n_ok,
    "n_pairs": int(len(pairs_df)), "n_ct": int(n_cts),
    "n_ct_well_sampled": int(len(ws_cts)),
    "sanity_max_delta_vs_phase35": max_delta,
    "point_estimates": {
        "ct_level_omega_kf": {"r": float(r_ct_kf), "p": float(p_ct_kf)},
        "ct_level_omega_kn": {"r": float(r_ct_kn), "p": float(p_ct_kn)},
        "wellsampled_omega_kf": {"r": float(r_ws_kf), "p": float(p_ws_kf)},
        "wellsampled_omega_kn": {"r": float(r_ws_kn), "p": float(p_ws_kn)},
        "pair_level_omega_kf": {"r": float(r_pair), "p": float(p_pair)},
    },
    "organ_clustered_ci": {
        "omega_kf_all": ci(boot_kf_all), "omega_kn_all": ci(boot_kn_all),
        "omega_kf_ws": ci(boot_kf_ws), "omega_kn_ws": ci(boot_kn_ws),
    },
    "ct_level_bootstrap_ci": {
        "omega_kf_all": ci(ctb_kf), "omega_kn_all": ci(ctb_kn),
    },
    "runtime_s": time.time() - t0,
}
with open(RESULTS_DIR / "cross_organ_rho_ci_v44.json", "w") as f:
    json.dump(summary, f, indent=2)

lines = [
    "Cross-organ rank concordance: bootstrap CI for CT-level Spearman rho (v44)",
    "=" * 74,
    f"Rebuild of 83 Part A verified vs phase35_cross_organ_summary.csv "
    f"(max |delta| = {max_delta:.2e}, {len(merged)}/{len(ref)} CTs)",
    f"Pairs: {len(pairs_df)} across {n_cts} CTs (well-sampled: {len(ws_cts)})",
    f"B = {N_BOOT}, seed {RANDOM_SEED}; per-CT rejection sampling (all replicates valid)",
    "",
    "Point estimates (published, 83):",
    f"  CT-level r(mean omega, mean k_f) = {r_ct_kf:.3f} (P = {p_ct_kf:.3f})",
    f"  CT-level r(mean omega, mean k_n) = {r_ct_kn:.3f} (P = {p_ct_kn:.3f})",
    f"  Well-sampled r(omega, k_f) = {r_ws_kf:.3f}; r(omega, k_n) = {r_ws_kn:.3f}",
    f"  Pair-level r(omega, k_f) = {r_pair:.3f} (P = {p_pair:.2e})",
    "",
    "Joint organ-clustered bootstrap 95% CI (primary):",
]
for r in rows_out:
    lines.append(f"  {r['statistic']}")
    lines.append(f"    point = {r['point']:.3f}, bootstrap median = {r['cluster_boot_median']:.3f}, "
                 f"95% CI [{r['ci_lo']:.3f}, {r['ci_hi']:.3f}]")
lines += [
    "",
    "Classical CT-level bootstrap 95% CI (sensitivity):",
    f"  r(omega, k_f): median {ci(ctb_kf)[0]:.3f}, 95% CI [{ci(ctb_kf)[1]:.3f}, {ci(ctb_kf)[2]:.3f}]",
    f"  r(omega, k_n): median {ci(ctb_kn)[0]:.3f}, 95% CI [{ci(ctb_kn)[1]:.3f}, {ci(ctb_kn)[2]:.3f}]",
    "",
    f"Runtime: {time.time()-t0:.0f}s",
]
(RESULTS_DIR / "cross_organ_rho_ci_v44.txt").write_text("\n".join(lines), encoding="utf-8")

print("\n".join(lines))
print(f"\nSaved: {RESULTS_DIR/'cross_organ_rho_ci_v44.csv'}")
print(f"Saved: {RESULTS_DIR/'cross_organ_rho_ci_v44.json'}")
print(f"Saved: {RESULTS_DIR/'cross_organ_rho_ci_v44.txt'}")
print("DONE")
