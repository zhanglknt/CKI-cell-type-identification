"""
nc49 pilot: LIHC Cox survival go/no-go
======================================
Per-tumor omega (TT-pair mean, v44 linear-normalization pair table, sample-labelled)
joined with cBioPortal lihc_tcga patient clinical; Cox PH via statsmodels PHReg.

Inputs (all local, read-only):
  results/tcga_linear_norm_v44_all_pairs.csv   (35,306 pairs with sample_a/sample_b)
  data/tcga/lihc_patient_clinical.json         (377 patients)

Outputs:
  results/nc49_pilot_lihc_cox.csv              (coefficient tables, all models)
  results/audit/nc49_pilot_lihc_2026-09-18.md  (GO/NO-GO audit)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
import statsmodels.api as sm
from statsmodels.duration.hazard_regression import PHReg

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
CLIN = ROOT / "data" / "tcga" / "lihc_patient_clinical.json"
OUT_CSV = ROOT / "results" / "nc49_pilot_lihc_cox.csv"
OUT_MD = ROOT / "results" / "audit" / "nc49_pilot_lihc_2026-09-18.md"
LOG = ROOT / "_tmp_fa_review" / "_nc49_pilot_log.txt"

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

# ------------------------------------------------------------------
# 1. Per-tumor omega from LIHC TT pairs (and TN-based variant)
# ------------------------------------------------------------------
pairs = pd.read_csv(PAIRS)
lihc_tt = pairs[(pairs.cancer == "TCGA-LIHC") & (pairs.pair_type == "TT")].copy()
lihc_tn = pairs[(pairs.cancer == "TCGA-LIHC") & (pairs.pair_type == "TN")].copy()
log(f"LIHC TT pairs: {len(lihc_tt)}; TN pairs: {len(lihc_tn)}")

def per_sample_stats(df):
    """Mean omega/kf/kn per sample across its pairs (both endpoints)."""
    rows = []
    for col, other in [("sample_a", "sample_b"), ("sample_b", "sample_a")]:
        sub = df[[col, other, "omega_floor", "kf", "kn"]].rename(
            columns={col: "sample", other: "partner",
                     "omega_floor": "omega", "kf": "kf", "kn": "kn"})
        rows.append(sub)
    long = pd.concat(rows, ignore_index=True)
    agg = long.groupby("sample").agg(
        n_pairs=("omega", "size"),
        omega=("omega", "mean"), kf=("kf", "mean"), kn=("kn", "mean"))
    return agg

tt_stats = per_sample_stats(lihc_tt).add_prefix("tt_")
log(f"per-tumor TT stats: n={len(tt_stats)}, "
    f"median pairs/tumor={tt_stats.tt_n_pairs.median()}")

# TN-based: tumor-vs-normal divergence per tumor (omega of its TN pairs)
tn_rows = []
for col, other in [("sample_a", "sample_b")]:
    tn_rows.append(lihc_tn[[col, "omega_floor", "kf", "kn"]].rename(
        columns={col: "sample", "omega_floor": "omega"}))
tn_stats = pd.concat(tn_rows, ignore_index=True).groupby("sample").agg(
    tn_n_pairs=("omega", "size"), tn_omega=("omega", "mean"),
    tn_kf=("kf", "mean"), tn_kn=("kn", "mean"))
log(f"per-tumor TN stats: n={len(tn_stats)} (TN pairs carry tumor as sample_a)")

per_tumor = tt_stats.join(tn_stats, how="outer")
per_tumor["patient"] = [s[:12] for s in per_tumor.index]
log(f"per-tumor table: {len(per_tumor)} tumors")

# ------------------------------------------------------------------
# 2. Clinical join
# ------------------------------------------------------------------
pc = json.load(open(CLIN))
attrs = ["GRADE", "AJCC_PATHOLOGIC_TUMOR_STAGE", "SEX", "AGE",
         "OS_STATUS", "OS_MONTHS", "DFS_STATUS", "DFS_MONTHS"]
clin = {}
for r in pc:
    if r["clinicalAttributeId"] in attrs:
        clin.setdefault(r["patientId"], {})[r["clinicalAttributeId"]] = r["value"]

df = per_tumor.reset_index().rename(columns={"index": "sample"})
df["grade"] = df["patient"].map(lambda p: clin.get(p, {}).get("GRADE", None))
df["stage_raw"] = df["patient"].map(lambda p: clin.get(p, {}).get("AJCC_PATHOLOGIC_TUMOR_STAGE", None))
df["sex"] = df["patient"].map(lambda p: clin.get(p, {}).get("SEX", None))
df["age"] = pd.to_numeric(df["patient"].map(lambda p: clin.get(p, {}).get("AGE", None)), errors="coerce")
df["os_status"] = df["patient"].map(lambda p: clin.get(p, {}).get("OS_STATUS", None))
df["os_months"] = pd.to_numeric(df["patient"].map(lambda p: clin.get(p, {}).get("OS_MONTHS", None)), errors="coerce")

STAGE_MAP = {"Stage I": 1, "Stage II": 2, "Stage III": 3, "Stage IIIA": 3,
             "Stage IIIB": 3, "Stage IIIC": 3, "Stage IV": 4,
             "Stage IVA": 4, "Stage IVB": 4}
GRADE_MAP = {"G1": 1, "G2": 2, "G3": 3, "G4": 4}
df["stage"] = df["stage_raw"].map(STAGE_MAP)
df["grade_ord"] = df["grade"].map(GRADE_MAP)
df["event"] = (df["os_status"] == "1:DECEASED").astype(int)
log(f"joined: {len(df)} tumors; event=1: {int(df.event.sum())}; "
    f"OS months available: {int(df.os_months.notna().sum())}")

# ------------------------------------------------------------------
# 3. Cox models
# ------------------------------------------------------------------
def fit_cox(sub, covars, label, exposure):
    """PHReg with listwise deletion; returns row dict list."""
    d = sub.dropna(subset=["os_months", "event"] + covars).copy()
    # standardize exposure (per SD) for interpretable HR
    sd = d[exposure].std(ddof=1)
    d["z"] = (d[exposure] - d[exposure].mean()) / sd
    X = d[["z"] + [c for c in covars if c != exposure]].copy()
    X = pd.get_dummies(X, columns=[c for c in X.columns if c in ("sex",)],
                       drop_first=True).astype(float)
    model_cols = list(X.columns)
    ph = PHReg(d["os_months"].values, X.values, status=d["event"].values)
    res = ph.fit()
    rows = []
    names = list(res.model.exog_names) if hasattr(res.model, "exog_names") else model_cols
    # PHReg param order follows X column order
    for i, name in enumerate(model_cols):
        b = res.params[i]
        se = res.bse[i]
        from scipy.stats import norm
        z = b / se
        p = 2 * (1 - norm.cdf(abs(z)))
        hr = np.exp(b)
        lo, hi = np.exp(b - 1.959963985 * se), np.exp(b + 1.959963985 * se)
        rows.append({"model": label, "covariate": name, "n": len(d),
                     "events": int(d.event.sum()),
                     "coef": round(b, 5), "se": round(se, 5),
                     "HR": round(hr, 3),
                     "HR_lower": round(lo, 3), "HR_upper": round(hi, 3),
                     "z": round(z, 3), "p": p})
    return rows

all_rows = []

# M1: omega + stage + grade + age + sex (full adjustment)
all_rows += fit_cox(df, ["tt_omega", "stage", "grade_ord", "age", "sex"],
                    "M1_omega_full", "tt_omega")
# M2: omega + stage + grade (lead-specified minimum)
all_rows += fit_cox(df, ["tt_omega", "stage", "grade_ord"],
                    "M2_omega_stage_grade", "tt_omega")
# M3: unadjusted omega
all_rows += fit_cox(df, ["tt_omega"], "M3_omega_unadjusted", "tt_omega")
# M4: kf-only
all_rows += fit_cox(df, ["tt_kf", "stage", "grade_ord", "age", "sex"],
                    "M4_kf_full", "tt_kf")
# M5: kn-only
all_rows += fit_cox(df, ["tt_kn", "stage", "grade_ord", "age", "sex"],
                    "M5_kn_full", "tt_kn")
# M6: TN-based omega (tumor-vs-normal divergence), full adjustment
all_rows += fit_cox(df, ["tn_omega", "stage", "grade_ord", "age", "sex"],
                    "M6_tnomega_full", "tn_omega")

coef = pd.DataFrame(all_rows)
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
coef.to_csv(OUT_CSV, index=False)
log("")
log("=== Cox coefficient table (HR per +1 SD of exposure) ===")
log(coef.to_string(index=False))

# ------------------------------------------------------------------
# 4. GO / NO-GO verdict
# ------------------------------------------------------------------
m1 = [r for r in all_rows if r["model"] == "M1_omega_full" and r["covariate"] == "z"]
m2 = [r for r in all_rows if r["model"] == "M2_omega_stage_grade" and r["covariate"] == "z"]
m3 = [r for r in all_rows if r["model"] == "M3_omega_unadjusted" and r["covariate"] == "z"]
m4 = [r for r in all_rows if r["model"] == "M4_kf_full" and r["covariate"] == "z"]
m5 = [r for r in all_rows if r["model"] == "M5_kn_full" and r["covariate"] == "z"]
m6 = [r for r in all_rows if r["model"] == "M6_tnomega_full" and r["covariate"] == "z"]

def fmt(r):
    return (f"HR/SD = {r['HR']:.2f} [{r['HR_lower']:.2f}, {r['HR_upper']:.2f}], "
            f"P = {r['p']:.3g} (n = {r['n']}, {r['events']} deaths)")

m1r = fmt(m1[0]) if m1 else "NA"
m2r = fmt(m2[0]) if m2 else "NA"
m3r = fmt(m3[0]) if m3 else "NA"
m4r = fmt(m4[0]) if m4 else "NA"
m5r = fmt(m5[0]) if m5 else "NA"
m6r = fmt(m6[0]) if m6 else "NA"

primary_p = m1[0]["p"] if m1 else 1.0
go = primary_p < 0.05

# descriptive: omega by event status (for the audit narrative)
d1 = df.dropna(subset=["tt_omega", "os_months", "event"])
mw_p = mannwhitneyu(d1.loc[d1.event == 1, "tt_omega"],
                    d1.loc[d1.event == 0, "tt_omega"], alternative="two-sided").pvalue
log("")
log(f"TT omega mean (deceased) = {d1.loc[d1.event==1,'tt_omega'].mean():.1f}; "
    f"(living) = {d1.loc[d1.event==0,'tt_omega'].mean():.1f}; MWU P = {mw_p:.3g}")

verdict = "GO (P < 0.05 in fully adjusted model)" if go else "NO-GO (P >= 0.05 in fully adjusted model)"
log(f"VERDICT: {verdict}")

md = f"""# nc49 pilot audit: LIHC Cox survival go/no-go

**Date**: 2026-09-18
**Script**: notebooks/nc49_pilot_lihc_cox.py
**Data**: results/tcga_linear_norm_v44_all_pairs.csv (LIHC TT {len(lihc_tt)} pairs, TN {len(lihc_tn)} pairs; per-tumor mean omega/kf/kn); data/tcga/lihc_patient_clinical.json (377 patients, cBioPortal lihc_tcga export).

## Design
- Exposure: per-tumor tissue-level divergence omega (mean over each tumor's TT pairs, v44 linear-normalization values; median {int(tt_stats.tt_n_pairs.median())} pairs/tumor).
- Outcome: OS (status/months); Cox PH (statsmodels PHReg), HR reported per +1 SD.
- Covariates: AJCC stage (I-IV ordinal), Edmondson grade (G1-G4 ordinal), age, sex (full model M1); lead-specified minimum M2 (omega + stage + grade); unadjusted M3; k_f-only M4; k_n-only M5; TN-based omega M6.

## Key numbers (HR per +1 SD)
- M1 omega full-adjusted: {m1r}
- M2 omega + stage + grade: {m2r}
- M3 omega unadjusted: {m3r}
- M4 k_f full-adjusted: {m4r}
- M5 k_n full-adjusted: {m5r}
- M6 TN-omega full-adjusted: {m6r}
- Descriptive: mean TT omega deceased {d1.loc[d1.event==1,'tt_omega'].mean():.1f} vs living {d1.loc[d1.event==0,'tt_omega'].mean():.1f} (MWU P = {mw_p:.3g}, n = {len(d1)})

## Verdict
**{verdict}**

Interpretation notes:
- Exposure is bulk tissue-level divergence; composition (purity/stroma) is a known confounder; k_f / k_n component models (M4/M5) indicate which component drives any association.
- HR per SD, so effect magnitude is comparable across models; listwise deletion for missing covariates.
- Full coefficient table: results/nc49_pilot_lihc_cox.csv.
"""
OUT_MD.parent.mkdir(parents=True, exist_ok=True)
OUT_MD.write_text(md, encoding="utf-8")

LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(lines), encoding="utf-8")
print("DONE")
