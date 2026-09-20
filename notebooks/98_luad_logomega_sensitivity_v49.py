"""
v49.13 C4(b): log-omega scale sensitivity for the LUAD driver-group ANCOVA.
============================================================================
Reviewer: R4-N6(b). The published adjustment regresses raw omega on
group + z-admixture (OLS), while the k_f analysis uses log k_f; omega is
right-skewed, so the two components use inconsistent model scales. This
script reruns the same ANCOVA with log(omega) as the response and reports
the group coefficients and P values alongside the raw-scale model, plus the
KRAS-WT adjusted difference with 95% CI on the log scale (exponentiated to
a ratio).

Also adds the KRAS-WT contrast on log k_f and log k_n for completeness.

Input : results/tcga_linear_norm_v44_all_pairs.csv
        results/nc49_tcga_admix_scores.csv
        data/tcga/luad_egfr_kras_mutations.json
Output: results/nc49_tcga_luad_logomega_sensitivity.csv
Seed  : 42 (bootstrap CIs of the exponentiated KRAS-WT ratio).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
OUT = ROOT / "results" / "nc49_tcga_luad_logomega_sensitivity.csv"

SEED = 42
B = 1000
GROUPS = ["WT", "EGFR", "KRAS"]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
adm = pd.read_csv(ADMIX)
adm_t = adm[adm.type == "Tumor"][["sample", "admix"]]

luad_tt = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")].copy()
long = pd.concat([
    luad_tt[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
    luad_tt[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
], ignore_index=True)
per_tumor = long.groupby("sample").agg(
    omega=("omega", "mean"), kf=("kf", "mean"), kn=("kn", "mean")).reset_index()
per_tumor = per_tumor.merge(adm_t, on="sample", how="inner")
mu, sd = per_tumor.admix.mean(), per_tumor.admix.std()
per_tumor["admix_z"] = (per_tumor.admix - mu) / sd

mut = json.load(open(MUT))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])
def group_of(s):
    e, k = s[:15] in egfr, s[:15] in kras
    if e and k:
        return "DOUBLE"
    if e:
        return "EGFR"
    if k:
        return "KRAS"
    return "WT"
per_tumor["group"] = per_tumor["sample"].map(group_of)
pt = per_tumor[per_tumor.group != "DOUBLE"].copy()
pt["log_omega"] = np.log(pt.omega)
pt["log_kf"] = np.log(pt.kf)
pt["log_kn"] = np.log(pt.kn)
log(f"n tumours: WT={sum(pt.group=='WT')}, EGFR={sum(pt.group=='EGFR')}, "
    f"KRAS={sum(pt.group=='KRAS')}")

results = []
for metric in ["omega", "log_omega", "log_kf", "log_kn"]:
    X = pd.DataFrame({"const": 1.0,
                      "admix_z": pt.admix_z.values,
                      "EGFR": (pt.group == "EGFR").astype(float).values,
                      "KRAS": (pt.group == "KRAS").astype(float).values})
    fit = sm.OLS(pt[metric].values, X.values).fit()
    names = ["const", "admix_z", "EGFR", "KRAS"]
    for n in names:
        i = names.index(n)
        results.append({"response": metric, "term": n,
                        "coef": round(float(fit.params[i]), 4),
                        "p": float(fit.pvalues[i])})
        log(f"{metric} ~ group + admix_z: {n}: coef={fit.params[i]:.4f}, "
            f"P={fit.pvalues[i]:.3g}")

# exponentiated KRAS-vs-WT adjusted ratio on the log-omega scale + bootstrap CI
X = pd.DataFrame({"const": 1.0,
                  "admix_z": pt.admix_z.values,
                  "EGFR": (pt.group == "EGFR").astype(float).values,
                  "KRAS": (pt.group == "KRAS").astype(float).values})
fit = sm.OLS(pt.log_omega.values, X.values).fit()
ratio_kras = float(np.exp(fit.params[3]))
rng = np.random.default_rng(SEED)
boots = []
idx_wt = np.where(pt.group.values == "WT")[0]
idx_kr = np.where(pt.group.values == "KRAS")[0]
idx_eg = np.where(pt.group.values == "EGFR")[0]
for _ in range(B):
    sel = np.concatenate([rng.choice(idx_wt, len(idx_wt), replace=True),
                          rng.choice(idx_eg, len(idx_eg), replace=True),
                          rng.choice(idx_kr, len(idx_kr), replace=True)])
    Xb = pd.DataFrame({"const": 1.0,
                       "admix_z": pt.admix_z.values[sel],
                       "EGFR": (pt.group.values[sel] == "EGFR").astype(float),
                       "KRAS": (pt.group.values[sel] == "KRAS").astype(float)})
    try:
        fb = sm.OLS(pt.log_omega.values[sel], Xb.values).fit()
        boots.append(np.exp(fb.params[3]))
    except Exception:  # noqa: BLE001
        continue
ci = np.percentile(boots, [2.5, 97.5])
log("")
log(f"KRAS-vs-WT adjusted omega ratio (log-scale model, exponentiated): "
    f"{ratio_kras:.3f}, bootstrap 95% CI [{ci[0]:.3f}, {ci[1]:.3f}] (B={B})")
results.append({"response": "log_omega", "term": "KRAS/WT ratio (exp)",
                "coef": round(ratio_kras, 3),
                "p": float(fit.pvalues[3])})
# v49.14 (R3-M4): archive the bootstrap CI in the CSV itself (previously stdout-only)
results.append({"response": "log_omega", "term": "KRAS/WT ratio CI low (exp)",
                "coef": round(float(ci[0]), 3), "p": np.nan})
results.append({"response": "log_omega", "term": "KRAS/WT ratio CI high (exp)",
                "coef": round(float(ci[1]), 3), "p": np.nan})

pd.DataFrame(results).to_csv(OUT, index=False)
log("")
log("saved: " + str(OUT))
print("DONE")
