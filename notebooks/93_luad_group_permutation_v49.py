"""
v49.13 B4: label-permutation re-analysis of the LUAD driver-group comparisons
(KW + pairwise), handling the dyadic dependence of per-tumor omega.
============================================================================
Reviewer: R1-N2. Per-tumor omega/kf/kn are means over overlapping (non-
disjoint) TT pair sets, so Kruskal-Wallis / Dunn assume independence the data
do not have. This script keeps the same per-tumor statistics but replaces the
asymptotic P values with label-permutation P values: group labels are permuted
across tumors (B = 10,000, seed 42), which is valid regardless of within-tumor
pair sharing because the permutation acts on whole tumors.

Reported:
  - observed KW H for omega/kf/kn + permutation P;
  - pairwise mean differences (KRAS-WT, KRAS-EGFR, EGFR-WT) + two-sided
    permutation P for each metric;
  - descriptive group means/medians (unchanged).

Input : results/tcga_linear_norm_v44_all_pairs.csv
        data/tcga/luad_egfr_kras_mutations.json
Output: results/nc49_tcga_luad_mutation_perm.csv
Seed  : 42, B = 10,000.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
OUT = ROOT / "results" / "nc49_tcga_luad_mutation_perm.csv"

B = 10000
SEED = 42
GROUPS = ["WT", "EGFR", "KRAS"]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
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
pt = pt[pt.group != "DOUBLE"]
log(f"LUAD per-tumor: WT={sum(pt.group=='WT')}, EGFR={sum(pt.group=='EGFR')}, "
    f"KRAS={sum(pt.group=='KRAS')} (DOUBLE excluded)")

rng = np.random.default_rng(SEED)
results = []

for metric in ["omega", "kf", "kn"]:
    vals = pt[metric].values
    grp = pt.group.values
    H_obs, p_kw_asym = kruskal(*[vals[grp == g] for g in GROUPS])

    # permutation null for H (permute labels across tumors)
    cnt = 0
    for _ in range(B):
        perm = rng.permutation(grp)
        H_p, _ = kruskal(*[vals[perm == g] for g in GROUPS])
        if H_p >= H_obs:
            cnt += 1
    p_perm = (cnt + 1) / (B + 1)

    log(f"--- {metric}: KW H={H_obs:.2f}, asymptotic P={p_kw_asym:.3g}, "
        f"label-permutation P={p_perm:.4f} (B={B}) ---")
    results.append({"metric": "LUAD_" + metric, "test": "Kruskal-Wallis (perm)",
                    "comparison": "WT vs EGFR vs KRAS", "n_total": len(pt),
                    "stat": round(H_obs, 3), "p_perm": p_perm,
                    "p_asymptotic": p_kw_asym})

    # descriptive group stats
    for g in GROUPS:
        s = pt.loc[pt.group == g, metric]
        log(f"  {g}: n={len(s)}, mean={s.mean():.4f}, median={s.median():.4f}")
        results.append({"metric": "LUAD_" + metric, "test": "descriptive",
                        "comparison": g, "n_total": len(s),
                        "stat": round(s.mean(), 4), "p_perm": np.nan,
                        "p_asymptotic": np.nan})

    # pairwise mean differences with permutation P
    for g1, g2 in [("KRAS", "WT"), ("KRAS", "EGFR"), ("EGFR", "WT")]:
        a = vals[grp == g1]
        b = vals[grp == g2]
        d_obs = a.mean() - b.mean()
        m = len(a) + len(b)
        pool = np.concatenate([a, b])
        na = len(a)
        cnt = 0
        for _ in range(B):
            rng.shuffle(pool)
            d_p = pool[:na].mean() - pool[na:].mean()
            if abs(d_p) >= abs(d_obs):
                cnt += 1
        p_pair = (cnt + 1) / (B + 1)
        log(f"  mean diff {g1}-{g2}: {d_obs:.4f}, permutation P={p_pair:.4f}")
        results.append({"metric": "LUAD_" + metric, "test": "mean diff (perm)",
                        "comparison": f"{g1} - {g2}", "n_total": m,
                        "stat": round(d_obs, 4), "p_perm": p_pair,
                        "p_asymptotic": np.nan})

df = pd.DataFrame(results)
OUT.write_text(df.to_csv(index=False), encoding="utf-8")
log("")
log("saved: " + str(OUT))
