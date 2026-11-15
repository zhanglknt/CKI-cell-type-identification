"""
nc49 LUAD smoking covariate analysis (R2-P0-2)
==============================================
Smoking-status adjustment for the LUAD EGFR/KRAS mutation-group divergence
gradient, using patient-level clinical data obtained from cBioPortal
(study luad_tcga, patient attributes TOBACCO_SMOKING_HISTORY_INDICATOR,
SMOKING_PACK_YEARS, SEX, AGE; fetched 2026-09-18 to
data/tcga/luad_patient_clinical_cbioportal.json).

TCGA smoking indicator codes: 1=lifelong non-smoker; 2=current smoker;
3=reformed <15 yr; 4=reformed >15 yr; 5=reformed, duration unspecified.
Ever-smoker = code in {2,3,4,5}; never-smoker = 1.

Analyses
--------
1. Smoking (ever/never) x mutation-group crosstab + chi-square.
2. OLS: metric ~ group + ever_smoke (+ age, sex) for omega/kf/kn;
   adjusted group contrasts (KRAS-EGFR, KRAS-WT, EGFR-WT).
3. If results/nc49_tcga_admix_scores.csv exists: combined model
   metric ~ group + ever_smoke + admix_z (purity + smoking jointly).
4. KW + Dunn-Holm on smoking-residualized metrics.

Inputs (read-only):
  data/tcga/luad_patient_clinical_cbioportal.json
  data/tcga/luad_egfr_kras_mutations.json
  results/tcga_linear_norm_v44_all_pairs.csv
  results/nc49_tcga_admix_scores.csv (optional)

Outputs:
  results/nc49_tcga_luad_smoking.csv
  _tmp_fa_review/_nc49_smoking_log.txt
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal, norm, chi2_contingency
import statsmodels.api as sm

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
CLIN = ROOT / "data" / "tcga" / "luad_patient_clinical_cbioportal.json"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
OUT = ROOT / "results" / "nc49_tcga_luad_smoking.csv"
LOG = ROOT / "_tmp_fa_review" / "_nc49_smoking_log.txt"

GROUPS = ["WT", "EGFR", "KRAS"]
lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

log("== nc49 LUAD smoking covariate analysis (R2-P0-2) ==")

# ---------------------------------------------------------------------------
# 1. cBioPortal clinical data -> patient table
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
     "pack_years": v.get("SMOKING_PACK_YEARS"), "sex": v.get("SEX"),
     "age": v.get("AGE"), "stage": v.get("AJCC_PATHOLOGIC_TUMOR_STAGE")}
    for k, v in pat.items()])
log(f"cBioPortal patients with any target attribute: {len(df_pat)}")

def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan

df_pat["ever_smoke"] = df_pat.smoke_ind.map(
    lambda x: 1.0 if str(x) in ("2", "3", "4", "5", "6") else (0.0 if str(x) == "1" else np.nan))
df_pat["age_f"] = df_pat.age.map(to_float)
df_pat["pack_f"] = df_pat.pack_years.map(to_float)
log(f"smoking status known: {df_pat.ever_smoke.notna().sum()}/{len(df_pat)} "
    f"(never={int((df_pat.ever_smoke==0).sum())}, ever={int((df_pat.ever_smoke==1).sum())}); "
    f"pack-years known: {df_pat.pack_f.notna().sum()}")

# ---------------------------------------------------------------------------
# 2. LUAD per-tumour metrics + mutation groups
# ---------------------------------------------------------------------------
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
df = per_tumor.merge(df_pat[["patient", "ever_smoke", "pack_f", "age_f", "sex", "stage"]],
                     on="patient", how="left")
log(f"LUAD per-tumour: WT={sum(df.group=='WT')}, EGFR={sum(df.group=='EGFR')}, "
    f"KRAS={sum(df.group=='KRAS')}; smoking matched: {df.ever_smoke.notna().sum()}/{len(df)}")

results = []

# ---------------------------------------------------------------------------
# 3. smoking x group crosstab
# ---------------------------------------------------------------------------
ct = pd.crosstab(df.group, df.ever_smoke)
log("")
log("smoking (ever/never) x mutation group:")
log(ct.to_string())
if ct.shape == (3, 2):
    chi2, p_chi, dof, _ = chi2_contingency(ct.values)
    results.append({"section": "A_smoking_dist", "test": "chi2 ever/never x group",
                    "n": int(ct.values.sum()), "stat": round(chi2, 3), "p": p_chi})
    log(f"chi2={chi2:.2f}, dof={dof}, P={p_chi:.3g}")
    for g in GROUPS:
        n = ct.loc[g].sum()
        ev = ct.loc[g].get(1.0, 0)
        results.append({"section": "A_smoking_dist", "test": f"ever-smoker pct {g}",
                        "n": int(n), "stat": round(100 * ev / n, 1), "p": np.nan})
        log(f"  {g}: ever-smoker {100*ev/n:.1f}% ({ev}/{n})")

# pack-years by group (descriptive)
for g in GROUPS:
    pk = df.loc[df.group == g, "pack_f"].dropna()
    results.append({"section": "A_smoking_dist", "test": f"pack-years mean {g}",
                    "n": len(pk), "stat": round(pk.mean(), 1) if len(pk) else np.nan,
                    "p": np.nan})
log(f"pack-years mean: " + ", ".join(
    f"{g}={df.loc[df.group==g,'pack_f'].dropna().mean():.1f}"
    f"(n={df.loc[df.group==g,'pack_f'].notna().sum()})" for g in GROUPS))

# ---------------------------------------------------------------------------
# 4. OLS adjustments
# ---------------------------------------------------------------------------
d = df[df.ever_smoke.notna()].copy()
d["ever_smoke"] = d.ever_smoke.astype(float)
d["male"] = (d.sex == "Male").astype(float)
d["age_c"] = d.age_f - d.age_f.mean()

def fit_ols(dat, metric, covars, label):
    X = pd.get_dummies(dat["group"], drop_first=False)[GROUPS].astype(float).drop(columns=["WT"])
    for cv in covars:
        X.insert(0, cv, dat[cv].values)
    X.insert(0, "const", 1.0)
    fit = sm.OLS(dat[metric].values, X.values).fit()
    col = {n: i for i, n in enumerate(X.columns)}  # const, covars..., EGFR, KRAS
    cm = np.zeros((3, len(fit.params)))
    cm[0, col["EGFR"]] = 1.0   # EGFR - WT
    cm[1, col["KRAS"]] = 1.0   # KRAS - WT
    cm[2, col["KRAS"]] = 1.0   # KRAS - EGFR
    cm[2, col["EGFR"]] = -1.0
    tt = fit.t_test(cm)
    names = ["EGFR - WT", "KRAS - WT", "KRAS - EGFR"]
    out = []
    for k, nm in enumerate(names):
        est, se, pv = float(tt.effect[k]), float(tt.sd[k]), float(tt.pvalue[k])
        out.append((nm, est, se, pv))
        results.append({"section": f"B_{label}", "metric": metric,
                        "test": f"OLS adj diff ({'+'.join(['group']+covars)})",
                        "n": len(dat), "comparison": nm,
                        "stat": round(est, 4), "se": round(se, 4), "p": pv})
    return out

log("")
for metric in ["omega", "kf", "kn"]:
    # unadjusted group effect (group only, same n as smoking model)
    out0 = fit_ols(d, metric, [], "group_only")
    log(f"--- {metric} (group only, n={len(d)}) ---")
    for nm, est, se, pv in out0:
        log(f"  {nm}: {est:.4f} (SE {se:.4f}), P={pv:.3g}")
    # smoking adjusted
    out1 = fit_ols(d, metric, ["ever_smoke"], "smoke_adj")
    log(f"--- {metric} (group + ever_smoke) ---")
    for nm, est, se, pv in out1:
        log(f"  {nm}: {est:.4f} (SE {se:.4f}), P={pv:.3g}")
    # smoking + age + sex
    d2 = d[d.age_c.notna()].copy()
    out2 = fit_ols(d2, metric, ["ever_smoke", "age_c", "male"], "smoke_agesex_adj")
    log(f"--- {metric} (group + ever_smoke + age + sex, n={len(d2)}) ---")
    for nm, est, se, pv in out2:
        log(f"  {nm}: {est:.4f} (SE {se:.4f}), P={pv:.3g}")

# combined: group + ever_smoke + admix_z (if available)
if ADMIX.exists():
    adm = pd.read_csv(ADMIX)
    adm = adm[adm.type == "Tumor"][["sample", "admix"]]
    d3 = d.merge(adm, on="sample", how="inner")
    d3["admix_z"] = (d3["admix"] - d3["admix"].mean()) / d3["admix"].std(ddof=1)
    log("")
    log(f"--- combined model (group + ever_smoke + admix_z, n={len(d3)}) ---")
    for metric in ["omega", "kf", "kn"]:
        out3 = fit_ols(d3, metric, ["ever_smoke", "admix_z"], "smoke_admix_adj")
        log(f"{metric}:")
        for nm, est, se, pv in out3:
            log(f"  {nm}: {est:.4f} (SE {se:.4f}), P={pv:.3g}")
else:
    log("admix scores file not found - combined model skipped")

# ---------------------------------------------------------------------------
# 5. residual-based rank tests (residualize on ever_smoke within LUAD)
# ---------------------------------------------------------------------------
def dunn_holm(sub, val_col):
    groups = [sub.loc[sub.group == g, val_col].values for g in GROUPS]
    H, p_kw = kruskal(*groups)
    ranks = sub[val_col].rank().values
    sub2 = sub.assign(_r=ranks)
    Nn = len(sub2)
    _, counts = np.unique(sub[val_col].values, return_counts=True)
    tie_term = np.sum(counts ** 3 - counts) / (Nn ** 3 - Nn)
    sigma2_bar = (Nn * (Nn + 1) / 12.0) - tie_term / (Nn - 1)
    out = []
    for i, j in [(1, 2), (0, 2), (0, 1)]:
        gi, gj = GROUPS[i], GROUPS[j]
        ri = sub2.loc[sub2.group == gi, "_r"].mean()
        rj = sub2.loc[sub2.group == gj, "_r"].mean()
        ni, nj = sum(sub.group == gi), sum(sub.group == gj)
        se = np.sqrt(sigma2_bar * (1.0 / ni + 1.0 / nj))
        z = (ri - rj) / se
        out.append({"pair": f"{gi} vs {gj}", "z": z,
                    "p_raw": 2 * (1 - norm.cdf(abs(z)))})
    ps = [o["p_raw"] for o in out]
    order = np.argsort(ps)
    m = len(ps)
    adj, running = {}, 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * ps[idx])
        running = max(running, val)
        adj[idx] = running
    for idx, o in enumerate(out):
        o["p_holm"] = adj[idx]
    return H, p_kw, out

log("")
for metric in ["omega", "kf", "kn"]:
    beta = np.polyfit(d.ever_smoke, d[metric], 1)[0]
    d[f"{metric}_resid"] = d[metric] - beta * d.ever_smoke
    Hr, pr, dr = dunn_holm(d, f"{metric}_resid")
    results.append({"section": "C_resid", "metric": metric,
                    "test": "KW on ever-smoke residuals", "n": len(d),
                    "stat": round(Hr, 3), "p": pr})
    for dd in dr:
        results.append({"section": "C_resid", "metric": metric,
                        "test": "Dunn-Holm (smoke-resid)", "n": len(d),
                        "comparison": dd["pair"], "stat": round(dd["z"], 3),
                        "p": dd["p_holm"]})
    log(f"{metric} smoke-residual KW: H={Hr:.2f}, P={pr:.3g}; " +
        "; ".join(f"{dd['pair']} P_holm={dd['p_holm']:.3g}" for dd in dr))

df_out = pd.DataFrame(results)
OUT.write_text(df_out.to_csv(index=False), encoding="utf-8")
log("")
log("saved: " + str(OUT))
LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(lines), encoding="utf-8")
print("DONE")
