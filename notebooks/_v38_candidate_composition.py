# -*- coding: utf-8 -*-
"""v38 candidate-composition analyses (Round-4 review fixes)

Computes, from existing read-only inputs:
  A. Omnibus test (Monte-Carlo chi-square GOF) of the Strong-candidate class
     composition against the classes' share of comparisons.
  B. Per-class composition of Strong candidates UNDER the block-shuffle null
     (S1b rule re-evaluation, per permutation), giving the null-rule expected
     microglia count, fold enrichment, and a permutation P-value.
  C. Tier-sensitivity grid for the microglia enrichment (residual x omega-cap),
     mirroring the lineage sensitivity table.
  D. Permutation calibration of the lower-tail count excess
     (P(V_null >= 1,960) and null count distribution percentiles).
  E. Class composition of Strong candidates under the leave-pair-out (S2)
     and unselected (S3) scales, from results/fixed_panel_ablation_pairs.csv.

Outputs (all under results/):
  v38_candidate_composition.md
  _v38_omnibus_composition.csv
  _v38_null_rule_composition.csv
  _v38_microglia_tier_sensitivity.csv
  _v38_tailcount_calibration.csv
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pandas as pd
from scipy import stats

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")

res = pd.read_csv(os.path.join(RESULTS, "brain_bs_null_results.csv"))
cts = list(res["cell_type"].unique())
B_perm = None
nulls = {}
for ct in cts:
    nulls[ct] = np.load(os.path.join(RESULTS, f"brain_bs_null_pairs_{ct.replace(' ', '_')}.npy"))
    B_perm = nulls[ct].shape[1]

obs = res[res["tier"] == "Strong"]
n_strong = len(obs)
comp_obs = obs["cell_type"].value_counts()
n_comparisons = res["cell_type"].value_counts()
share = (n_comparisons / len(res))

md = ["# v38 candidate-composition analyses (Round-4 fixes)", ""]

# ----------------------------------------------------------------------
# A. omnibus Monte-Carlo chi-square GOF
# ----------------------------------------------------------------------
# exp_vec and prob must be ordered like obs_vec (i.e. by `cts`, the order of
# first appearance in res), NOT by share.values (value_counts descending
# order) -- previously the two vectors were ordered differently, assigning
# expected counts to the wrong classes (Round-5 review, Task #1048 bug A).
obs_vec = np.array([int(comp_obs.get(ct, 0)) for ct in cts])
exp_vec = np.array([share.get(ct, 0.0) * n_strong for ct in cts])
stat = float(((obs_vec - exp_vec) ** 2 / exp_vec).sum())
rng = np.random.default_rng(42)
n_mc = 20000
prob = np.array([share.get(ct, 0.0) for ct in cts])
counts_mc = rng.multinomial(n_strong, prob, size=n_mc)
stat_mc = ((counts_mc - exp_vec) ** 2 / exp_vec).sum(axis=1)
p_omni = float((1 + (stat_mc >= stat).sum()) / (n_mc + 1))
chi2_p = float(stats.chisquare(obs_vec, exp_vec)[1])

md.append("## A. Omnibus test of Strong-candidate class composition")
md.append("")
md.append(f"Observed Strong composition (n = {n_strong}) vs the classes' share of all "
          f"31,764 comparisons. Pearson chi-square = {stat:.2f}; asymptotic "
          f"p = {chi2_p:.4g}; Monte-Carlo p (20,000 multinomial draws, expected "
          f"counts from comparison shares) = {p_omni:.4f}.")
md.append("")
rows = {"cell_type": cts, "observed_strong": obs_vec,
        "expected_from_share": exp_vec.round(2)}
df_a = pd.DataFrame(rows)
md.append(df_a.to_markdown(index=False))
md.append("")

# ----------------------------------------------------------------------
# B. per-class composition of Strong candidates under the null
# ----------------------------------------------------------------------
gp_keys = [tuple(sorted(t)) for t in zip(res["region_a"], res["region_b"])]
gp_ids, gp_uniq = pd.factorize(pd.Series(gp_keys))
n_gp = len(gp_uniq)
ct_rows = {ct: (res["cell_type"] == ct).values for ct in cts}
gp_of_ct = {ct: gp_ids[ct_rows[ct]] for ct in cts}

mu_ct_null = {ct: nulls[ct].mean(axis=0) for ct in cts}
n_ct = {ct: nulls[ct].shape[0] for ct in cts}
grand_null = sum(n_ct[ct] * mu_ct_null[ct] for ct in cts) / sum(n_ct.values())

sum_val = np.zeros((n_gp, B_perm))
cnt_gp = np.zeros(n_gp)
min_val = np.full((n_gp, B_perm), np.inf)
for ct in cts:
    g = gp_of_ct[ct]
    nv = nulls[ct].astype(np.float64)
    sum_val[g] += nv
    cnt_gp[g] += 1
    min_val[g] = np.minimum(min_val[g], nv)
mu_pair_null = sum_val / cnt_gp[:, None]

null_strong_by_ct = {ct: np.zeros(B_perm, dtype=int) for ct in cts}
for ct in cts:
    g = gp_of_ct[ct]
    nv = nulls[ct].astype(np.float64)
    exp = mu_ct_null[ct][None, :] * mu_pair_null[g] / grand_null[None, :]
    resid = nv / exp
    lowest = nv <= min_val[g]
    strong = (resid < 0.3) & (nv < 15) & lowest
    null_strong_by_ct[ct] = strong.sum(axis=0)

total_null = sum(null_strong_by_ct.values())
micro = "Microglia"
micro_obs = int(comp_obs.get(micro, 0))
micro_null_mean = float(null_strong_by_ct[micro].mean())
p_micro_perm = (1 + int((null_strong_by_ct[micro] >= micro_obs).sum())) / (B_perm + 1)
fold_vs_null = micro_obs / micro_null_mean

md.append("## B. Strong-candidate class composition under the block-shuffle null")
md.append("")
md.append(f"The Strong rule (residual < 0.3, omega < 15, lowest-in-pair) was re-evaluated "
          f"on each of the B = {B_perm} permutations exactly as in addendum S1b; per-class "
          f"candidate counts were tallied per permutation.")
md.append("")
rows_b = []
for ct in cts:
    nb = null_strong_by_ct[ct]
    rows_b.append({"cell_type": ct,
                   "observed_strong": int(comp_obs.get(ct, 0)),
                   "null_mean": round(float(nb.mean()), 1),
                   "null_max": int(nb.max())})
df_b = pd.DataFrame(rows_b).sort_values("observed_strong", ascending=False)
md.append(df_b.to_markdown(index=False))
md.append("")
md.append(f"Microglia: observed {micro_obs} vs null-rule expectation "
          f"{micro_null_mean:.1f} (fold {fold_vs_null:.2f}); "
          f"permutation P(null microglia count >= {micro_obs}) = {p_micro_perm:.3f}.")
md.append("")

# ----------------------------------------------------------------------
# C. tier sensitivity for the microglia enrichment
# ----------------------------------------------------------------------
def hyper(k, n, K, N):
    return float(stats.hypergeom.sf(k - 1, N, K, n))

rows_c = []
for res_t in [0.2, 0.25, 0.3, 0.35, 0.4]:
    for cap in [12, 15, 20, 25]:
        strong = (res["residual"] < res_t) & (res["omega"] < cap) & res["lowest_in_pair"].astype(bool)
        n_s = int(strong.sum())
        k = int((strong & (res["cell_type"] == micro)).sum())
        K = int((res["cell_type"] == micro).sum())
        N = len(res)
        if n_s > 0 and k > 0:
            p = hyper(k, n_s, K, N)
            fold = (k / n_s) / (K / N)
        elif n_s > 0:
            p, fold = 1.0, 0.0
        else:
            p, fold = 1.0, float("nan")
        rows_c.append({"res_threshold": res_t, "omega_cap": cap, "n_strong": n_s,
                       "microglia": k, "microglia_fold": round(fold, 2),
                       "hypergeom_P": round(p, 4),
                       "bonferroni_P": round(min(1.0, p * 10), 4)})
df_c = pd.DataFrame(rows_c)
md.append("## C. Tier-sensitivity grid for the microglia enrichment")
md.append("")
md.append("The Strong rule was re-applied at alternative (residual, omega-cap) thresholds "
          "on the observed landscape; microglia enrichment is recomputed per combination "
          "(hypergeometric over the class share of comparisons, Bonferroni across the "
          "ten classes).")
md.append("")
md.append(df_c.to_markdown(index=False))
md.append("")

# ----------------------------------------------------------------------
# D. permutation calibration of the lower-tail count
# ----------------------------------------------------------------------
def null_pvalues(null):
    n, b = null.shape
    order = np.argsort(null, axis=1, kind="stable")
    rank = np.empty_like(order)
    ridx = np.arange(n)[:, None]
    rank[ridx, order] = np.arange(b)[None, :]
    return (rank + 1.0) / (b + 1.0)

V = np.zeros(B_perm)
for ct in cts:
    V += (null_pvalues(nulls[ct]) < 0.05).sum(axis=0)
V_obs = int((res["p_perm"] < 0.05).sum())
p_tail = (1 + int((V >= V_obs).sum())) / (B_perm + 1)
q95 = float(np.percentile(V, 95))
q99 = float(np.percentile(V, 99))
md.append("## D. Permutation calibration of the lower-tail count")
md.append("")
md.append(f"V = number of pairs with lower-tail p < 0.05 in one null experiment "
          f"(recomputed per permutation as in addendum S1a). Observed V = {V_obs}; "
          f"null mean = {V.mean():.1f}; null 95th percentile = {q95:.0f}; "
          f"null 99th percentile = {q99:.0f}; null max = {V.max()}; "
          f"P(V_null >= {V_obs}) = {p_tail:.3f}.")
md.append("")

# ----------------------------------------------------------------------
# E. Strong composition under the S2 (leave-pair-out) and S3 (unselected)
#    ablation scales.  S2 is the leave-pair-out panel (top-200 by mean |diff|
#    over the other pairs of the same cell type); S3 is the unselected panel
#    (all 5,000 non-HK genes).  Previously this section used omega_s3 while
#    labelling it "leave-pair-out" (Round-5 review, Task #1048 bug B).
# ----------------------------------------------------------------------
abl = pd.read_csv(os.path.join(RESULTS, "fixed_panel_ablation_pairs.csv"))

def strong_on_scale(col):
    """Apply the Strong rule (resid < 0.3, omega < 15, lowest-in-pair) on the
    given ablation omega column; return summary dict."""
    mu_ct = abl.groupby("cell_type")[col].mean()
    abl["_ct_mean"] = abl["cell_type"].map(mu_ct)
    gp_mean = abl.groupby(["region_a", "region_b"])[col].mean()
    abl["_gp_mean"] = abl.set_index(["region_a", "region_b"]).index.map(gp_mean)
    grand = abl[col].mean()
    abl["_expected"] = abl["_ct_mean"] * abl["_gp_mean"] / grand
    abl["_resid"] = abl[col] / abl["_expected"]
    minw = abl.groupby(["region_a", "region_b"])[col].transform("min")
    abl["_lowest"] = abl[col] <= minw
    strong = (abl["_resid"] < 0.3) & (abl[col] < 15) & abl["_lowest"]
    n_s = int(strong.sum())
    comp_s = abl.loc[strong, "cell_type"].value_counts()
    k_m = int(comp_s.get(micro, 0))
    K_m = int((abl["cell_type"] == micro).sum())
    if n_s:
        p_m = hyper(k_m, n_s, K_m, len(abl))
        fold_m = (k_m / n_s) / (K_m / len(abl))
    else:
        p_m, fold_m = 1.0, float("nan")
    return {"n": n_s, "comp": comp_s, "k_micro": k_m, "p": p_m, "fold": fold_m}

s2 = strong_on_scale("omega_s2")
s3 = strong_on_scale("omega_s3")

md.append("## E. Strong-candidate composition under alternative gene-selection schemes")
md.append("")
md.append(f"Applying the same Strong rule (residual < 0.3, omega < 15, lowest-in-pair) "
          f"on the leave-pair-out (S2) omega scale fires on {s2['n']} pairs; "
          f"microglia contribute {s2['k_micro']} (fold {s2['fold']:.2f}, hypergeometric "
          f"P = {s2['p']:.4g}, Bonferroni P = {min(1.0, s2['p']*10):.3f}).")
md.append("")
md.append("Class composition (S2 leave-pair-out Strong): " + ", ".join(
    f"{ct}: {int(s2['comp'].get(ct, 0))}" for ct in s2['comp'].index))
md.append("")
md.append(f"On the unselected (S3; all 5,000 non-HK genes) omega scale the same rule "
          f"fires on {s3['n']} pairs; microglia contribute {s3['k_micro']} "
          f"(fold {s3['fold']:.2f}, hypergeometric P = {s3['p']:.4g}, "
          f"Bonferroni P = {min(1.0, s3['p']*10):.3f}).")
md.append("")
md.append("Class composition (S3 unselected Strong): " + ", ".join(
    f"{ct}: {int(s3['comp'].get(ct, 0))}" for ct in s3['comp'].index))
md.append("")

out = "\n".join(md) + "\n"
with open(os.path.join(RESULTS, "v38_candidate_composition.md"), "w", encoding="utf-8") as f:
    f.write(out)
df_a.to_csv(os.path.join(RESULTS, "_v38_omnibus_composition.csv"), index=False)
df_b.to_csv(os.path.join(RESULTS, "_v38_null_rule_composition.csv"), index=False)
df_c.to_csv(os.path.join(RESULTS, "_v38_microglia_tier_sensitivity.csv"), index=False)
pd.DataFrame([{"V_obs": V_obs, "null_mean": round(V.mean(), 1),
               "null_q95": round(q95), "null_q99": round(q99),
               "null_max": int(V.max()),
               "P(V_null >= V_obs)": round(p_tail, 3)}]).to_csv(
    os.path.join(RESULTS, "_v38_tailcount_calibration.csv"), index=False)
print(out)
