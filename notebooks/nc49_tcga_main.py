"""
nc49 main analysis: pancancer omega ranking (a) + LUAD mutation gradient (b)
===========================================================================
Module a: per-cancer TT vs NN omega (v44 linear-normalization pair table),
          NN/TT ratio ranking, sample-level cluster bootstrap 95% CIs,
          k_n denominator mechanism (TT k_n / NN k_n).
Module b: LUAD per-tumor omega/kf/kn by EGFR/KRAS/WT status; Kruskal-Wallis +
          Dunn post-hoc (Holm), bootstrap CIs of group differences,
          k_f-only / k_n-only sensitivity (mechanism contrast).

Inputs (all local, read-only):
  results/tcga_linear_norm_v44_all_pairs.csv   (35,306 pairs, sample-labelled)
  data/tcga/luad_egfr_kras_mutations.json

Outputs:
  results/nc49_tcga_pancancer.csv
  results/nc49_tcga_luad_mutation.csv
  (audit md written by the caller-side summary; log at _tmp_fa_review)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, norm

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
OUT_A = ROOT / "results" / "nc49_tcga_pancancer.csv"
OUT_B = ROOT / "results" / "nc49_tcga_luad_mutation.csv"
LOG = ROOT / "_tmp_fa_review" / "_nc49_main_log.txt"

B = 1000
SEED = 42

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

pairs = pd.read_csv(PAIRS)
pairs = pairs.rename(columns={"omega_floor": "omega"})
CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

# ==================================================================
# MODULE A: pancancer TT vs NN with cluster bootstrap CIs
# ==================================================================
rng = np.random.default_rng(SEED)

def weighted_pair_mean(vals, ia, ib, w):
    """Mean of pair values under sample weights w (cluster bootstrap)."""
    ww = w[ia] * w[ib]
    return np.sum(vals * ww) / np.sum(ww)

def boot_ratio(df_tt, df_nn, n_t, n_n, B, rng):
    """Bootstrap NN/TT (and kn TT/NN) ratio CIs via sample resampling.

    Resample tumor samples and normal samples with replacement; each pair's
    weight is the product of endpoint weights. TT pairs are the 2000-pair
    seeded subsample; NN pairs are complete.
    """
    t_samples = sorted(set(df_tt.sample_a) | set(df_tt.sample_b))
    n_samples = sorted(set(df_nn.sample_a) | set(df_nn.sample_b))
    t_idx = {s: i for i, s in enumerate(t_samples)}
    n_idx = {s: i for i, s in enumerate(n_samples)}

    tt_ia = df_tt.sample_a.map(t_idx).values
    tt_ib = df_tt.sample_b.map(t_idx).values
    tt_w = df_tt.omega.values
    tt_kn = df_tt.kn.values
    nn_ia = df_nn.sample_a.map(n_idx).values
    nn_ib = df_nn.sample_b.map(n_idx).values
    nn_w = df_nn.omega.values
    nn_kn = df_nn.kn.values

    ratios, kn_ratios = [], []
    for _ in range(B):
        wt = rng.multinomial(len(t_samples), np.full(len(t_samples), 1.0 / len(t_samples))).astype(float)
        wn = rng.multinomial(len(n_samples), np.full(len(n_samples), 1.0 / len(n_samples))).astype(float)
        tt_m = weighted_pair_mean(tt_w, tt_ia, tt_ib, wt)
        nn_m = weighted_pair_mean(nn_w, nn_ia, nn_ib, wn)
        ratios.append(nn_m / tt_m)
        kn_ratios.append(weighted_pair_mean(tt_kn, tt_ia, tt_ib, wt)
                         / weighted_pair_mean(nn_kn, nn_ia, nn_ib, wn))
    return np.percentile(ratios, [2.5, 97.5]), np.percentile(kn_ratios, [2.5, 97.5])

rows_a = []
for c in CANCERS:
    tt = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    nn = pairs[(pairs.cancer == c) & (pairs.pair_type == "NN")]
    n_t = len(set(tt.sample_a) | set(tt.sample_b))
    n_n = len(set(nn.sample_a) | set(nn.sample_b))
    tt_m, nn_m = tt.omega.mean(), nn.omega.mean()
    ratio = nn_m / tt_m
    p_mwu = mannwhitneyu(nn.omega.values, tt.omega.values, alternative="greater").pvalue
    ci_ratio, ci_knratio = boot_ratio(tt, nn, n_t, n_n, B, rng)
    kn_tt_med, kn_nn_med = tt.kn.median(), nn.kn.median()
    rows_a.append({
        "cancer": c, "n_tumor": n_t, "n_normal": n_n,
        "n_TT_pairs": len(tt), "n_NN_pairs": len(nn),
        "omega_TT_mean": round(tt_m, 2), "omega_NN_mean": round(nn_m, 2),
        "NN_TT_ratio": round(ratio, 3),
        "NN_TT_ratio_CI95_lower": round(ci_ratio[0], 3),
        "NN_TT_ratio_CI95_upper": round(ci_ratio[1], 3),
        "p_MWU_NN_gt_TT": p_mwu,
        "kn_TT_median": kn_tt_med, "kn_NN_median": kn_nn_med,
        "kn_TT_NN_median_ratio": round(kn_tt_med / kn_nn_med, 2),
        "kn_TT_NN_mean_ratio": round(tt.kn.mean() / nn.kn.mean(), 3),
        "kn_TT_NN_mean_ratio_CI95_lower": round(ci_knratio[0], 3),
        "kn_TT_NN_mean_ratio_CI95_upper": round(ci_knratio[1], 3),
        "kf_TT_mean": round(tt.kf.mean(), 4), "kf_NN_mean": round(nn.kf.mean(), 4),
    })
    log(f"{c}: NN/TT={ratio:.2f} [{ci_ratio[0]:.2f},{ci_ratio[1]:.2f}] "
        f"P={p_mwu:.2e}; kn TT/NN={kn_tt_med/kn_nn_med:.1f}x "
        f"(mean CI [{ci_knratio[0]:.2f},{ci_knratio[1]:.2f}])")

df_a = pd.DataFrame(rows_a)
# rank by effect size
df_a["rank_by_NN_TT_ratio"] = df_a.NN_TT_ratio.rank(ascending=False).astype(int)
OUT_A.write_text(df_a.to_csv(index=False), encoding="utf-8")
log("")
log(df_a.to_string(index=False))
log("")

# ==================================================================
# MODULE B: LUAD mutation gradient (WT / EGFR / KRAS)
# ==================================================================
luad_tt = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")].copy()
long = pd.concat([
    luad_tt[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
    luad_tt[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
], ignore_index=True)
per_tumor = long.groupby("sample").agg(
    n_pairs=("omega", "size"), omega=("omega", "mean"),
    kf=("kf", "mean"), kn=("kn", "mean"))

mut = json.load(open(MUT))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])

def group_of(s):
    e, k = s in egfr, s in kras
    if e and k:
        return "DOUBLE"
    if e:
        return "EGFR"
    if k:
        return "KRAS"
    return "WT"

pt = per_tumor.reset_index()
pt["group"] = pt["sample"].map(group_of)
pt = pt[pt.group != "DOUBLE"]  # n=2, excluded per published convention
log(f"LUAD per-tumor: WT={sum(pt.group=='WT')}, EGFR={sum(pt.group=='EGFR')}, "
    f"KRAS={sum(pt.group=='KRAS')}, DOUBLE excluded")

GROUPS = ["WT", "EGFR", "KRAS"]

def dunn_test(sub, val_col):
    """Kruskal-Wallis + Dunn post-hoc with Holm correction (manual impl)."""
    groups = [sub.loc[sub.group == g, val_col].values for g in GROUPS]
    H, p_kw = kruskal(*groups)
    # ranks over pooled sample
    ranks = pd.Series(sub[val_col].rank().values)
    sub2 = sub.assign(_r=ranks.values)
    N = len(sub2)
    # tie correction
    _, counts = np.unique(sub[val_col].values, return_counts=True)
    tie_term = np.sum(counts ** 3 - counts) / (N ** 3 - N)
    sigma2_bar = (N * (N + 1) / 12.0) - tie_term / (N - 1) if N > 1 else np.nan
    out = []
    for i, j in [(1, 2), (0, 2), (0, 1)]:  # EGFR-KRAS, WT-KRAS, WT-EGFR
        gi, gj = GROUPS[i], GROUPS[j]
        ri = sub2.loc[sub2.group == gi, "_r"].mean()
        rj = sub2.loc[sub2.group == gj, "_r"].mean()
        ni, nj = sum(sub.group == gi), sum(sub.group == gj)
        se = np.sqrt(sigma2_bar * (1.0 / ni + 1.0 / nj))
        z = (ri - rj) / se
        out.append({"pair": f"{gi} vs {gj}", "z": z,
                    "p_raw": 2 * (1 - norm.cdf(abs(z)))})
    # Holm
    ps = [o["p_raw"] for o in out]
    order = np.argsort(ps)
    m = len(ps)
    adj = {}
    running = 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * ps[idx])
        running = max(running, val)
        adj[idx] = running
    for idx, o in enumerate(out):
        o["p_holm"] = adj[idx]
    return H, p_kw, out

results_b = []
for metric in ["omega", "kf", "kn"]:
    H, p_kw, dunn = dunn_test(pt, metric)
    gstats = pt.groupby("group")[metric].agg(["size", "mean", "median", "std"])
    log(f"--- {metric}: KW H={H:.2f}, P={p_kw:.3g} ---")
    for g in GROUPS:
        s = gstats.loc[g]
        log(f"  {g}: n={int(s['size'])}, mean={s['mean']:.4f}, median={s['median']:.4f}")
    for d in dunn:
        log(f"  Dunn {d['pair']}: z={d['z']:.2f}, P_holm={d['p_holm']:.3g}")
        results_b.append({"metric": "LUAD_" + metric, "test": "Dunn (Holm)",
                          "comparison": d["pair"], "n_total": len(pt),
                          "stat": round(d["z"], 3), "p": d["p_holm"]})
    results_b.append({"metric": "LUAD_" + metric, "test": "Kruskal-Wallis",
                      "comparison": "WT vs EGFR vs KRAS", "n_total": len(pt),
                      "stat": round(H, 3), "p": p_kw})
    for g in GROUPS:
        s = gstats.loc[g]
        results_b.append({"metric": "LUAD_" + metric, "test": "descriptive",
                          "comparison": g, "n_total": int(s["size"]),
                          "stat": round(s["mean"], 4), "p": np.nan})

# bootstrap CI of mean differences (resample within groups)
rng_b = np.random.default_rng(SEED)
def boot_diff(g1, g2, val_col, B=1000):
    a = pt.loc[pt.group == g1, val_col].values
    b = pt.loc[pt.group == g2, val_col].values
    diffs = []
    for _ in range(B):
        aa = rng_b.choice(a, len(a), replace=True)
        bb = rng_b.choice(b, len(b), replace=True)
        diffs.append(aa.mean() - bb.mean())
    return np.percentile(diffs, [2.5, 97.5]), a.mean() - b.mean()

log("")
for metric in ["omega", "kf", "kn"]:
    for g1, g2 in [("KRAS", "WT"), ("KRAS", "EGFR"), ("EGFR", "WT")]:
        ci, diff = boot_diff(g1, g2, metric)
        log(f"{metric} mean diff {g1}-{g2}: {diff:.4f} [{ci[0]:.4f},{ci[1]:.4f}]")
        results_b.append({"metric": "LUAD_" + metric, "test": "bootstrap mean diff",
                          "comparison": f"{g1} - {g2}", "n_total": len(pt),
                          "stat": round(diff, 4),
                          "p": f"CI95 [{ci[0]:.4f},{ci[1]:.4f}]"})

df_b = pd.DataFrame(results_b)
OUT_B.write_text(df_b.to_csv(index=False), encoding="utf-8")
log("")
log("saved: " + str(OUT_A) + ", " + str(OUT_B))
LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(lines), encoding="utf-8")
print("DONE")
