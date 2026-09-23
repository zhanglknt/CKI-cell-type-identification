# -*- coding: utf-8 -*-
"""
nc52 (v52 revision, reviewer B1): ex-CC as the DEFAULT TCGA cohort — rerun of
the main TCGA chain.

The 32 ILSBio cell-line tumours (barcode TSS code 'CC', i.e. sample[5:7] ==
'CC', the audit rule of notebooks/94_cc_audit_sensitivity_v49.py) previously
entered the LIHC analyses. Reviewers (R3) require the ex-CC cohort to be the
default rather than a sensitivity. This script recomputes, on the ex-CC pair
set (every pair touching a CC sample dropped):

  A. Five-cancer NN/TT omega ratio + sample-level cluster bootstrap 95% CI
     (B=1,000, seed 42; multinomial endpoint weights, verbatim mirror of
     notebooks/nc49_tcga_main.py Module A), MWU P, TT/NN k_n and k_f median
     ratios, k_n TT/NN mean ratio + CI.
  B. Edmondson/severity stratification (LIHC Edmondson grade JT, BRCA PAM50
     KW, LUAD mutation KW; per-tumour mean over TT pairs of raw omega
     (kn_floor=0 convention) / k_f / k_n; mirrors the severity block of
     notebooks/85_tcga_linear_norm_v44.py).
  C. Composition regression: pair-level OLS log k_f ~ is_TT + admix_mean +
     |dAdmix| per cancer (mirrors Part A1 of
     notebooks/nc49_tcga_kf_composition.py), ex-CC pairs only.

The LIHC ex-CC Cox models (stage categorical, PH-assumption test, k_f model)
are produced by the companion script notebooks/nc52_lihc_cox_excc.py.

Inputs (read-only):
  results/tcga_linear_norm_v44_all_pairs.csv
  results/nc49_tcga_admix_scores.csv
  data/tcga/lihc_patient_clinical.json
  data/tcga/luad_egfr_kras_mutations.json
  results/phase34_pam50_cache.json

Outputs:
  results/nc52_tcga_pancancer_excc.csv
  results/nc52_tcga_excc_severity.csv
  results/nc52_tcga_excc_composition.csv
  results/nc52_tcga_excc_summary.json
Seed: 42.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, kruskal, norm
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parent.parent
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
LIHC_CLIN = ROOT / "data" / "tcga" / "lihc_patient_clinical.json"
LUAD_MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
PAM50 = ROOT / "results" / "phase34_pam50_cache.json"

OUT_MAIN = ROOT / "results" / "nc52_tcga_pancancer_excc.csv"
OUT_SEV = ROOT / "results" / "nc52_tcga_excc_severity.csv"
OUT_COMP = ROOT / "results" / "nc52_tcga_excc_composition.csv"
OUT_SUM = ROOT / "results" / "nc52_tcga_excc_summary.json"

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

pairs_full = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
cc_mask = pairs_full.sample_a.map(is_cc) | pairs_full.sample_b.map(is_cc)
n_cc_pairs = int(cc_mask.sum())
pairs = pairs_full[~cc_mask].copy()
log(f"pairs: full={len(pairs_full)}, CC-touching dropped={n_cc_pairs}, "
    f"ex-CC={len(pairs)}")

# ==================================================================
# MODULE A: pancancer TT vs NN, ex-CC default
# ==================================================================
rng = np.random.default_rng(SEED)

def weighted_pair_mean(vals, ia, ib, w):
    ww = w[ia] * w[ib]
    return np.sum(vals * ww) / np.sum(ww)

def boot_ratio(df_tt, df_nn, B, rng):
    """Cluster bootstrap of NN/TT omega ratio + TT/NN kn & kf mean ratios."""
    t_samples = sorted(set(df_tt.sample_a) | set(df_tt.sample_b))
    n_samples = sorted(set(df_nn.sample_a) | set(df_nn.sample_b))
    t_idx = {s: i for i, s in enumerate(t_samples)}
    n_idx = {s: i for i, s in enumerate(n_samples)}

    tt_ia = df_tt.sample_a.map(t_idx).values
    tt_ib = df_tt.sample_b.map(t_idx).values
    tt_w = df_tt.omega.values
    tt_kn = df_tt.kn.values
    tt_kf = df_tt.kf.values
    nn_ia = df_nn.sample_a.map(n_idx).values
    nn_ib = df_nn.sample_b.map(n_idx).values
    nn_w = df_nn.omega.values
    nn_kn = df_nn.kn.values
    nn_kf = df_nn.kf.values

    ratios, kn_ratios, kf_ratios = [], [], []
    for _ in range(B):
        wt = rng.multinomial(len(t_samples), np.full(len(t_samples), 1.0 / len(t_samples))).astype(float)
        wn = rng.multinomial(len(n_samples), np.full(len(n_samples), 1.0 / len(n_samples))).astype(float)
        tt_m = weighted_pair_mean(tt_w, tt_ia, tt_ib, wt)
        nn_m = weighted_pair_mean(nn_w, nn_ia, nn_ib, wn)
        ratios.append(nn_m / tt_m)
        kn_ratios.append(weighted_pair_mean(tt_kn, tt_ia, tt_ib, wt)
                         / weighted_pair_mean(nn_kn, nn_ia, nn_ib, wn))
        kf_ratios.append(weighted_pair_mean(tt_kf, tt_ia, tt_ib, wt)
                         / weighted_pair_mean(nn_kf, nn_ia, nn_ib, wn))
    return (np.percentile(ratios, [2.5, 97.5]),
            np.percentile(kn_ratios, [2.5, 97.5]),
            np.percentile(kf_ratios, [2.5, 97.5]))

rows_a = []
for c in CANCERS:
    tt = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    nn = pairs[(pairs.cancer == c) & (pairs.pair_type == "NN")]
    n_t = len(set(tt.sample_a) | set(tt.sample_b))
    n_n = len(set(nn.sample_a) | set(nn.sample_b))
    tt_m, nn_m = tt.omega.mean(), nn.omega.mean()
    ratio = nn_m / tt_m
    p_mwu = mannwhitneyu(nn.omega.values, tt.omega.values, alternative="greater").pvalue
    ci_ratio, ci_knratio, ci_kfratio = boot_ratio(tt, nn, B, rng)
    kn_tt_med, kn_nn_med = tt.kn.median(), nn.kn.median()
    kf_tt_med, kf_nn_med = tt.kf.median(), nn.kf.median()
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
        "kf_TT_median": kf_tt_med, "kf_NN_median": kf_nn_med,
        "kf_TT_NN_median_ratio": round(kf_tt_med / kf_nn_med, 3),
        "kf_TT_mean": round(tt.kf.mean(), 4), "kf_NN_mean": round(nn.kf.mean(), 4),
        "kf_TT_NN_mean_ratio": round(tt.kf.mean() / nn.kf.mean(), 3),
        "kf_TT_NN_mean_ratio_CI95_lower": round(ci_kfratio[0], 3),
        "kf_TT_NN_mean_ratio_CI95_upper": round(ci_kfratio[1], 3),
    })
    log(f"{c}: NN/TT={ratio:.3f} [{ci_ratio[0]:.3f},{ci_ratio[1]:.3f}] "
        f"P={p_mwu:.2e}; kn TT/NN med={kn_tt_med/kn_nn_med:.2f}x "
        f"(mean CI [{ci_knratio[0]:.3f},{ci_knratio[1]:.3f}]); "
        f"kf TT/NN med={kf_tt_med/kf_nn_med:.3f}x")

df_a = pd.DataFrame(rows_a)
df_a["rank_by_NN_TT_ratio"] = df_a.NN_TT_ratio.rank(ascending=False).astype(int)
OUT_MAIN.write_text(df_a.to_csv(index=False), encoding="utf-8")
log("")
log(df_a.to_string(index=False))
log("")

# ==================================================================
# MODULE B: Edmondson / severity stratification, ex-CC default
# ==================================================================
log("== MODULE B: severity strata (ex-CC) ==")

# clinical maps (verbatim 85)
lihc_grade_map = {}
with open(LIHC_CLIN) as f:
    for entry in json.load(f):
        if entry["clinicalAttributeId"] == "GRADE":
            grade = entry["value"]
            if grade in ("G1", "G2", "G3", "G4"):
                lihc_grade_map[entry["patientId"]] = grade

luad_mutation_map = {}
with open(LUAD_MUT) as f:
    luad_mut = json.load(f)
for sid_full in luad_mut.get("egfr_samples", []):
    luad_mutation_map[sid_full[:15]] = "EGFR"
for sid_full in luad_mut.get("kras_samples", []):
    sid_short = sid_full[:15]
    if sid_short in luad_mutation_map:
        luad_mutation_map[sid_short] = "EGFR+KRAS"
    else:
        luad_mutation_map[sid_short] = "KRAS"

pam50_map = {}
if PAM50.exists():
    with open(PAM50) as f:
        pam50_map = json.load(f)

STRATA = {
    "TCGA-LIHC": ("Edmondson_grade", lambda sid, part: lihc_grade_map.get(part),
                  ["G1", "G2", "G3", "G4"], "jt"),
    "TCGA-BRCA": ("PAM50", lambda sid, part: pam50_map.get(sid),
                  sorted(set(pam50_map.values())), "kw"),
    "TCGA-LUAD": ("mutation", lambda sid, part: luad_mutation_map.get(sid, "WT"),
                  ["WT", "EGFR", "KRAS"], "kw"),
}

def jttest_on_ranks_manual(groups):
    n_total = sum(len(g) for g in groups)
    if n_total < 2:
        return 0, 1.0
    jt = 0
    for k1 in range(len(groups)):
        for k2 in range(k1 + 1, len(groups)):
            for i in range(len(groups[k1])):
                for j in range(len(groups[k2])):
                    if groups[k1][i] < groups[k2][j]:
                        jt += 1
                    elif groups[k1][i] == groups[k2][j]:
                        jt += 0.5
    n = sum(len(g) for g in groups)
    ni_sq_sum = sum(len(g) ** 2 for g in groups)
    ni_sum_cu = sum(len(g) ** 3 for g in groups)
    E = n * (n - 1) / 4.0
    V = (2 * (n ** 3) + 3 * (n ** 2) - n - ni_sq_sum * (2 * n + 3) + ni_sum_cu) / 72.0
    if V <= 0:
        return 0, 1.0
    z = (jt - E) / np.sqrt(V)
    p = 2 * (1 - norm.cdf(abs(z)))
    return jt, p

# per-tumour means over ex-CC TT pairs (raw omega = kn_floor 0 convention)
tt_all = pairs[pairs.pair_type == "TT"].copy()
n_inf = int(np.isinf(tt_all.omega_raw).sum())
if n_inf:
    log(f"WARNING: {n_inf} TT pairs with omega_raw=inf dropped from severity means")
tt_all = tt_all[np.isfinite(tt_all.omega_raw)]
long = pd.concat([
    tt_all[["cancer", "sample_a", "omega_raw", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
    tt_all[["cancer", "sample_b", "omega_raw", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
], ignore_index=True)
per_tumor = long.groupby(["cancer", "sample"]).agg(
    n_pairs=("omega_raw", "size"), omega=("omega_raw", "mean"),
    kf=("kf", "mean"), kn=("kn", "mean")).reset_index()
per_tumor["patient"] = per_tumor["sample"].str[:12]

sev_rows = []
sev_tests = {}
for cancer, (strat_name, strat_fn, order, test_kind) in STRATA.items():
    sub = per_tumor[per_tumor.cancer == cancer].copy()
    sub["stratum"] = [strat_fn(s, p) for s, p in zip(sub["sample"], sub["patient"])]
    sub = sub[sub.stratum.notna() & (sub.stratum != "EGFR+KRAS")]
    order_use = [g for g in order if g in set(sub.stratum)]
    log(f"{cancer} {strat_name} (ex-CC):")
    sev_tests[cancer] = {"stratification": strat_name, "groups": {}}
    for g in order_use:
        sg = sub[sub.stratum == g]
        log(f"  {g:<10} n={len(sg):>4} omega={sg.omega.mean():>8.2f} "
            f"kf={sg.kf.mean():.4f} kn={sg.kn.mean():.6e}")
        sev_rows.append({
            "cancer": cancer.replace("TCGA-", ""), "stratification": strat_name,
            "group": g, "n": len(sg),
            "omega_mean": round(sg.omega.mean(), 4), "omega_std": round(sg.omega.std(), 4),
            "kf_mean": round(sg.kf.mean(), 6), "kf_std": round(sg.kf.std(), 6),
            "kn_mean": round(sg.kn.mean(), 8), "kn_std": round(sg.kn.std(), 8),
        })
        sev_tests[cancer]["groups"][g] = {
            "n": int(len(sg)), "omega_mean": float(sg.omega.mean()),
            "kf_mean": float(sg.kf.mean()), "kn_mean": float(sg.kn.mean())}
    tests = {}
    for m in ("omega", "kf", "kn"):
        groups = [sg[m].values for _, sg in sub.groupby("stratum")]
        groups = [sub.loc[sub.stratum == g, m].values for g in order_use]
        if test_kind == "jt":
            stat, p = jttest_on_ranks_manual(groups)
            tests[m] = {"test": "Jonckheere-Terpstra", "stat": float(stat), "p": float(p)}
        else:
            stat, p = kruskal(*groups)
            tests[m] = {"test": "Kruskal-Wallis", "stat": float(stat), "p": float(p)}
        log(f"  {m:>5}: {tests[m]['test']} stat={tests[m]['stat']:.2f}, P={tests[m]['p']:.3e}")
        sev_rows.append({
            "cancer": cancer.replace("TCGA-", ""), "stratification": strat_name,
            "group": f"TEST_{m}", "n": int(len(sub)),
            "omega_mean": round(tests[m]["stat"], 4), "omega_std": np.nan,
            "kf_mean": tests[m]["p"], "kf_std": np.nan,
            "kn_mean": np.nan, "kn_std": np.nan,
        })
    sev_tests[cancer]["tests"] = tests

pd.DataFrame(sev_rows).to_csv(OUT_SEV, index=False)
log("saved: " + str(OUT_SEV))

# ==================================================================
# MODULE C: composition regression (pair-level OLS), ex-CC default
# ==================================================================
log("")
log("== MODULE C: composition regression (ex-CC) ==")
adm = pd.read_csv(ADMIX).set_index("sample")["admix"]
pairs["adm_a"] = pairs.sample_a.map(adm)
pairs["adm_b"] = pairs.sample_b.map(adm)
pairs["adm_mean"] = (pairs.adm_a + pairs.adm_b) / 2.0
pairs["adm_d"] = (pairs.adm_a - pairs.adm_b).abs()

comp_rows = []
for c in CANCERS:
    sub = pairs[(pairs.cancer == c) & pairs.pair_type.isin(["TT", "NN"])].copy()
    sub = sub.dropna(subset=["adm_mean", "adm_d"])
    sub["is_tt"] = (sub.pair_type == "TT").astype(float)
    for metric in ["kf", "kn"]:
        y = np.log(sub[metric].clip(lower=1e-12))
        gap_unadj = y[sub.is_tt == 1].mean() - y[sub.is_tt == 0].mean()
        X = sm.add_constant(sub[["is_tt", "adm_mean", "adm_d"]].astype(float))
        fit = sm.OLS(y.values, X.values).fit()
        b_tt, se_tt, p_tt = fit.params[1], fit.bse[1], fit.pvalues[1]
        comp_rows.append({"section": "A1_pair_level_excc", "cancer": c, "metric": metric,
                          "n": len(sub), "test": "OLS log ~ is_TT + admix",
                          "comparison": "TT vs NN",
                          "stat": round(float(b_tt), 4), "se": round(float(se_tt), 4),
                          "p": float(p_tt), "extra": f"unadj_loggap={gap_unadj:.4f}"})
        log(f"{c} {metric}: TT-vs-NN log gap unadj={gap_unadj:+.3f} -> "
            f"adj={b_tt:+.3f} (SE {se_tt:.3f}, P={p_tt:.3g})")

pd.DataFrame(comp_rows).to_csv(OUT_COMP, index=False)
log("saved: " + str(OUT_COMP))

# ==================================================================
# Summary JSON
# ==================================================================
lihc_row = df_a[df_a.cancer == "TCGA-LIHC"].iloc[0]
summary = {
    "analysis": "nc52 B1: ex-CC default TCGA main chain",
    "seed": SEED, "bootstrap_B": B,
    "cohort": {
        "pairs_full": int(len(pairs_full)),
        "pairs_cc_touching_dropped": n_cc_pairs,
        "pairs_excc": int(len(pairs)),
        "cc_rule": "sample barcode positions [5:7] == 'CC' (ILSBio cell line)",
    },
    "pancancer_excc": df_a.to_dict(orient="records"),
    "LIHC_focus": {
        "NN_TT_ratio_excc": float(lihc_row.NN_TT_ratio),
        "CI95": [float(lihc_row.NN_TT_ratio_CI95_lower),
                 float(lihc_row.NN_TT_ratio_CI95_upper)],
        "CI_excludes_1": bool(lihc_row.NN_TT_ratio_CI95_lower > 1.0),
        "p_MWU_NN_gt_TT": float(lihc_row.p_MWU_NN_gt_TT),
        "kn_TT_NN_mean_ratio": float(lihc_row.kn_TT_NN_mean_ratio),
        "kn_TT_NN_mean_ratio_CI95": [float(lihc_row.kn_TT_NN_mean_ratio_CI95_lower),
                                     float(lihc_row.kn_TT_NN_mean_ratio_CI95_upper)],
        "kn_CI_excludes_1": bool(lihc_row.kn_TT_NN_mean_ratio_CI95_lower > 1.0),
        "n_tumor_excc": int(lihc_row.n_tumor),
        "reference_full_cohort_ratio": 1.104,
        "reference_full_cohort_CI95": [0.933, 1.286],
    },
    "severity_tests_excc": sev_tests,
    "outputs": [str(OUT_MAIN), str(OUT_SEV), str(OUT_COMP)],
}
OUT_SUM.write_text(json.dumps(summary, indent=2), encoding="utf-8")
log("saved: " + str(OUT_SUM))
log("")
log(f"LIHC ex-CC FOCUS: NN/TT={lihc_row.NN_TT_ratio:.3f} "
    f"[{lihc_row.NN_TT_ratio_CI95_lower:.3f},{lihc_row.NN_TT_ratio_CI95_upper:.3f}] "
    f"CI_excludes_1={summary['LIHC_focus']['CI_excludes_1']}; "
    f"kn mean ratio CI [{lihc_row.kn_TT_NN_mean_ratio_CI95_lower:.3f},"
    f"{lihc_row.kn_TT_NN_mean_ratio_CI95_upper:.3f}] "
    f"excludes_1={summary['LIHC_focus']['kn_CI_excludes_1']}")
print("DONE")
