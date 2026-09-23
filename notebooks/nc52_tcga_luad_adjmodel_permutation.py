# -*- coding: utf-8 -*-
"""
nc52 (v52 revision, reviewer B4): whole-tumour label permutation for the LUAD
covariate-adjusted OLS models.

The published adjusted models (notebooks/nc49_tcga_luad_smoking.py; results/
nc49_tcga_luad_smoking.csv, sections B_smoke_adj / B_smoke_agesex_adj /
B_smoke_admix_adj) are ordinary OLS whose P values assume i.i.d. errors.
Reviewers (R1) require a resampling-based calibration: permute the mutation
GROUP LABELS (WT/EGFR/KRAS) across whole tumours, keeping every covariate
(ever_smoke, age, sex, admix_z) and the metric values attached to their
tumours; refit the same OLS; the group-contrast coefficients are the test
statistics. B = 10,000 permutations, seed 42. Two-sided permutation
P = (1 + #{|T_perm| >= |T_obs|}) / (B + 1).

Also reported: the design effect 1 + (m - 1) * rho for the pair-level data
behind the per-tumour means, where m = median number of TT pairs per tumour
and rho is the intra-tumour correlation of pair-level values estimated by the
pairwise moment estimator over all pairs sharing a tumour
(rho = sum_t sum_{p<q in S_t} (x_p - mu)(x_q - mu) / (sigma^2 * sum_t C(n_t, 2))).

Inputs (read-only):
  data/tcga/luad_patient_clinical_cbioportal.json
  data/tcga/luad_egfr_kras_mutations.json
  results/tcga_linear_norm_v44_all_pairs.csv
  results/nc49_tcga_admix_scores.csv
Output:
  results/nc52_tcga_luad_adjmodel_permutation.csv
Seed: 42. B = 10,000.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLIN = ROOT / "data" / "tcga" / "luad_patient_clinical_cbioportal.json"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
OUT = ROOT / "results" / "nc52_tcga_luad_adjmodel_permutation.csv"

B = 10_000
SEED = 42
GROUPS = ["WT", "EGFR", "KRAS"]
METRICS = ["omega", "kf", "kn"]
CONTRASTS = ["EGFR - WT", "KRAS - WT", "KRAS - EGFR"]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

# ---------------------------------------------------------------------------
# 1. Data prep (verbatim nc49_tcga_luad_smoking.py)
# ---------------------------------------------------------------------------
clin = json.load(open(CLIN, encoding="utf-8"))
pat = {}
for rec in clin:
    b = rec.get("patientId", "")
    key = b if b.startswith("TCGA") else "TCGA-" + b
    a = rec.get("clinicalAttributeId")
    v = rec.get("value")
    if a in ("TOBACCO_SMOKING_HISTORY_INDICATOR", "SMOKING_PACK_YEARS",
             "SEX", "AGE", "AJCC_PATHOLOGIC_TUMOR_STAGE"):
        pat.setdefault(key, {})[a] = v
df_pat = pd.DataFrame([
    {"patient": k, "smoke_ind": v.get("TOBACCO_SMOKING_HISTORY_INDICATOR"),
     "sex": v.get("SEX"), "age": v.get("AGE")}
    for k, v in pat.items()])

def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan

df_pat["ever_smoke"] = df_pat.smoke_ind.map(
    lambda x: 1.0 if str(x) in ("2", "3", "4", "5", "6") else (0.0 if str(x) == "1" else np.nan))
df_pat["age_f"] = df_pat.age.map(to_float)

pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
luad_tt = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")]
long = pd.concat([
    luad_tt[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
    luad_tt[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
], ignore_index=True)
per_tumor = long.groupby("sample").agg(
    n_pairs=("omega", "size"), omega=("omega", "mean"),
    kf=("kf", "mean"), kn=("kn", "mean")).reset_index()

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

per_tumor["group"] = per_tumor["sample"].map(group_of)
per_tumor = per_tumor[per_tumor.group != "DOUBLE"]
per_tumor["patient"] = per_tumor["sample"].str[:12]
df = per_tumor.merge(df_pat[["patient", "ever_smoke", "age_f", "sex"]],
                     on="patient", how="left")

d = df[df.ever_smoke.notna()].copy()
d["ever_smoke"] = d.ever_smoke.astype(float)
d["male"] = (d.sex == "Male").astype(float)
d["age_c"] = d.age_f - d.age_f.mean()
d2 = d[d.age_c.notna()].copy()
adm = pd.read_csv(ADMIX)
adm = adm[adm.type == "Tumor"][["sample", "admix"]]
d3 = d.merge(adm, on="sample", how="inner")
d3["admix_z"] = (d3["admix"] - d3["admix"].mean()) / d3["admix"].std(ddof=1)
log(f"cohorts: smoke_adj n={len(d)}, smoke_agesex_adj n={len(d2)}, "
    f"smoke_admix_adj n={len(d3)}")

# ---------------------------------------------------------------------------
# 2. OLS contrasts + whole-tumour label permutation
# ---------------------------------------------------------------------------
# contrast matrix on [EGFR, KRAS] coefficient positions:
#   EGFR - WT = b_EGFR ; KRAS - WT = b_KRAS ; KRAS - EGFR = b_KRAS - b_EGFR
CM = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 1.0]])

def design(dat, covars):
    """Return (fixed part F, group dummy matrix Gobs). X = [F, G]."""
    F = np.column_stack([np.ones(len(dat))] + [dat[c].values for c in covars])
    G = np.column_stack([(dat.group == "EGFR").astype(float).values,
                         (dat.group == "KRAS").astype(float).values])
    return F, G

def ols_contrasts(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return CM @ beta[-2:]

rng = np.random.default_rng(SEED)
rows = []
MODELS = [("B_smoke_adj", d, ["ever_smoke"]),
          ("B_smoke_agesex_adj", d2, ["ever_smoke", "age_c", "male"]),
          ("B_smoke_admix_adj", d3, ["ever_smoke", "admix_z"])]

for label, dat, covars in MODELS:
    F, Gobs = design(dat, covars)
    X_obs = np.column_stack([F, Gobs])
    for metric in METRICS:
        y = dat[metric].values.astype(float)
        t_obs = ols_contrasts(y, X_obs)
        exceed = np.zeros(3, dtype=int)
        for _ in range(B):
            Gp = Gobs[rng.permutation(len(dat))]
            X = np.column_stack([F, Gp])
            t_perm = ols_contrasts(y, X)
            exceed += (np.abs(t_perm) >= np.abs(t_obs)).astype(int)
        p_perm = (1.0 + exceed) / (B + 1.0)
        for k, cname in enumerate(CONTRASTS):
            rows.append({"model": label, "metric": metric, "contrast": cname,
                         "n": len(dat), "B": B, "seed": SEED,
                         "obs_coef": round(float(t_obs[k]), 4),
                         "perm_p_two_sided": float(p_perm[k])})
        log(f"{label} {metric}: " + "; ".join(
            f"{cname} obs={t_obs[k]:+.4f} permP={p_perm[k]:.4g}"
            for k, cname in enumerate(CONTRASTS)))

# ---------------------------------------------------------------------------
# 3. Design effect for the pair-level data behind the per-tumour means
# ---------------------------------------------------------------------------
log("")
m_pairs = float(per_tumor.n_pairs.median())
log(f"median TT pairs per tumour (m): {m_pairs:.0f} "
    f"(n_tumours={len(per_tumor)})")

def icc_pairs(luad_tt, valcol):
    """Pairwise moment estimator of the intra-tumour correlation of
    pair-level values (clusters = tumours, members = incident pairs)."""
    vals = luad_tt[valcol].values
    mu = vals.mean()
    var = vals.var(ddof=1)
    num, den_pairs = 0.0, 0
    # group pair indices by endpoint tumour
    membership = {}
    for idx, (a, b) in enumerate(zip(luad_tt.sample_a.values,
                                     luad_tt.sample_b.values)):
        membership.setdefault(a, []).append(idx)
        membership.setdefault(b, []).append(idx)
    for idxs in membership.values():
        x = vals[idxs] - mu
        n_t = len(x)
        if n_t < 2:
            continue
        s = x.sum()
        num += (s * s - np.sum(x * x)) / 2.0   # sum over p<q of x_p x_q
        den_pairs += n_t * (n_t - 1) // 2
    return num / (var * den_pairs), den_pairs

de_rows = []
for metric in METRICS:
    rho, npair_terms = icc_pairs(luad_tt, metric)
    deff = 1.0 + (m_pairs - 1.0) * rho
    de_rows.append({"statistic": "design_effect", "metric": metric,
                    "m_median_pairs_per_tumor": m_pairs,
                    "rho_intra_tumor": round(float(rho), 5),
                    "design_effect": round(float(deff), 3)})
    log(f"design effect ({metric}): 1 + ({m_pairs:.0f}-1)*{rho:.5f} = {deff:.3f}")

de_df = pd.DataFrame(de_rows)
de_df["model"] = "design_effect_context"
de_df["contrast"] = ""
de_df["n"] = len(per_tumor)
de_df["B"] = np.nan
de_df["seed"] = SEED
de_df["obs_coef"] = np.nan
de_df["perm_p_two_sided"] = np.nan
de_df = de_df.rename(columns={"metric": "metric"})
de_df = de_df[["model", "metric", "contrast", "n", "B", "seed", "obs_coef",
               "perm_p_two_sided", "m_median_pairs_per_tumor",
               "rho_intra_tumor", "design_effect"]]

perm_df = pd.DataFrame(rows)
perm_df["m_median_pairs_per_tumor"] = np.nan
perm_df["rho_intra_tumor"] = np.nan
perm_df["design_effect"] = np.nan

out_df = pd.concat([perm_df, de_df], ignore_index=True)
OUT.write_text(out_df.to_csv(index=False), encoding="utf-8")
log("")
log("saved: " + str(OUT))
print("DONE")
