# -*- coding: utf-8 -*-
"""
nc52 (v52 revision, reviewer B5): linear vs softmax probability-mapping
comparison of the five-cancer NN/TT omega reversal, complete table.

The manuscript's authoritative TCGA pipeline feeds log2(TPM+1) into
cki.core.compute_omega, whose js_divergence maps values to a probability
distribution via softmax (a power transform of TPM+1); the v44 sensitivity
used the linear mapping p_i = (TPM_i + 1) / sum_j (TPM_j + 1). Reviewers
(R1/R3) require the headline NN/TT result under BOTH mappings side by side
with sample-level cluster bootstrap 95% CIs.

Pair tables (both sample-labelled, ex-CC default cohort):
  linear  : results/tcga_linear_norm_v44_all_pairs.csv
  softmax : results/nc52_tcga_softmax_all_pairs.csv
            (produced by notebooks/nc52_tcga_softmax_pairs.py, a line-for-line
            mirror of 06_phase34_v2.py with sample labels added)

Bootstrap: multinomial endpoint weights, B=1,000, seed 42; the rng stream is
shared across (mapping, cancer) blocks in the order linear x cancers then
softmax x cancers (stream position deterministic and documented).

Outputs:
  results/nc52_tcga_mapping_schemes_table.csv
  results/nc52_tcga_mapping_schemes_summary.json
Seed: 42.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parent.parent
LIN = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
SOFT = ROOT / "results" / "nc52_tcga_softmax_all_pairs.csv"
OUT = ROOT / "results" / "nc52_tcga_mapping_schemes_table.csv"
OUT_SUM = ROOT / "results" / "nc52_tcga_mapping_schemes_summary.json"

B = 1000
SEED = 42
CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

def is_cc(s):
    s = str(s)
    return len(s) >= 7 and s[5:7] == "CC"

tables = {
    "linear": pd.read_csv(LIN).rename(columns={"omega_floor": "omega"}),
    "softmax": pd.read_csv(SOFT),
}

rng = np.random.default_rng(SEED)

def weighted_pair_mean(vals, ia, ib, w):
    ww = w[ia] * w[ib]
    return np.sum(vals * ww) / np.sum(ww)

def boot_ratio(df_tt, df_nn, B, rng):
    t_samples = sorted(set(df_tt.sample_a) | set(df_tt.sample_b))
    n_samples = sorted(set(df_nn.sample_a) | set(df_nn.sample_b))
    t_idx = {s: i for i, s in enumerate(t_samples)}
    n_idx = {s: i for i, s in enumerate(n_samples)}
    tt_ia = df_tt.sample_a.map(t_idx).values
    tt_ib = df_tt.sample_b.map(t_idx).values
    tt_w = df_tt.omega.values
    nn_ia = df_nn.sample_a.map(n_idx).values
    nn_ib = df_nn.sample_b.map(n_idx).values
    nn_w = df_nn.omega.values
    ratios = []
    for _ in range(B):
        wt = rng.multinomial(len(t_samples), np.full(len(t_samples), 1.0 / len(t_samples))).astype(float)
        wn = rng.multinomial(len(n_samples), np.full(len(n_samples), 1.0 / len(n_samples))).astype(float)
        ratios.append(weighted_pair_mean(nn_w, nn_ia, nn_ib, wn)
                      / weighted_pair_mean(tt_w, tt_ia, tt_ib, wt))
    return np.percentile(ratios, [2.5, 97.5])

rows = []
for mapping, df in tables.items():
    cc_mask = df.sample_a.map(is_cc) | df.sample_b.map(is_cc)
    df = df[~cc_mask]
    for c in CANCERS:
        tt = df[(df.cancer == c) & (df.pair_type == "TT")]
        nn = df[(df.cancer == c) & (df.pair_type == "NN")]
        n_t = len(set(tt.sample_a) | set(tt.sample_b))
        n_n = len(set(nn.sample_a) | set(nn.sample_b))
        tt_m, nn_m = tt.omega.mean(), nn.omega.mean()
        ratio = nn_m / tt_m
        p_mwu = mannwhitneyu(nn.omega.values, tt.omega.values,
                             alternative="greater").pvalue
        ci = boot_ratio(tt, nn, B, rng)
        rows.append({
            "mapping": mapping, "cohort": "exCC", "cancer": c,
            "n_tumor": n_t, "n_normal": n_n,
            "n_TT_pairs": len(tt), "n_NN_pairs": len(nn),
            "omega_TT_mean": round(tt_m, 3), "omega_NN_mean": round(nn_m, 3),
            "NN_TT_ratio": round(ratio, 3),
            "NN_TT_ratio_CI95_lower": round(ci[0], 3),
            "NN_TT_ratio_CI95_upper": round(ci[1], 3),
            "CI_excludes_1": bool(ci[0] > 1.0),
            "p_MWU_NN_gt_TT": p_mwu,
        })
        log(f"{mapping:<8} {c}: NN/TT={ratio:.3f} [{ci[0]:.3f},{ci[1]:.3f}] "
            f"excludes_1={ci[0] > 1.0} P={p_mwu:.2e}")

out = pd.DataFrame(rows)
OUT.write_text(out.to_csv(index=False), encoding="utf-8")

n_excl = out.groupby("mapping").CI_excludes_1.sum()
summary = {
    "analysis": "nc52 B5: linear vs softmax mapping comparison (ex-CC default)",
    "seed": SEED, "bootstrap_B": B,
    "n_cancers_CI_excludes_1": {m: int(v) for m, v in n_excl.items()},
    "LIHC": {
        m: {
            "NN_TT_ratio": float(out[(out.mapping == m) & (out.cancer == "TCGA-LIHC")].NN_TT_ratio.iloc[0]),
            "CI95": [float(out[(out.mapping == m) & (out.cancer == "TCGA-LIHC")].NN_TT_ratio_CI95_lower.iloc[0]),
                     float(out[(out.mapping == m) & (out.cancer == "TCGA-LIHC")].NN_TT_ratio_CI95_upper.iloc[0])],
            "CI_excludes_1": bool(out[(out.mapping == m) & (out.cancer == "TCGA-LIHC")].CI_excludes_1.iloc[0]),
        } for m in tables
    },
    "outputs": [str(OUT)],
}
OUT_SUM.write_text(json.dumps(summary, indent=2), encoding="utf-8")
log("")
log(f"CI excludes 1: linear {n_excl['linear']}/5, softmax {n_excl['softmax']}/5")
log(f"LIHC softmax: {summary['LIHC']['softmax']}")
log("saved: " + str(OUT))
print("DONE")
