"""
v49.14 (R4-M4): ex-CC Cox sensitivity for the LIHC survival analysis.
======================================================================
The published LIHC Cox models (nc49_pilot_lihc_cox.py) include the 32
ILSBio cell-line (TSS 'CC') tumours that entered the pair table. This
script refits the same model family with every CC tumour excluded
(barcode positions [5:7] == 'CC', the audit rule of
94_cc_audit_sensitivity_v49.py), so the CC-presence ledger for the
survival analysis is closed by a sensitivity run rather than disclosure
alone.

Input : results/tcga_linear_norm_v44_all_pairs.csv
        data/tcga/lihc_patient_clinical.json
Output: results/nc49_lihc_cox_excc.csv
        results/audit/nc49_lihc_cox_excc_2026-09-21.md
Seed  : none needed (PHReg is deterministic; no bootstrap here).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm  # noqa: F401
from statsmodels.duration.hazard_regression import PHReg
from scipy.stats import norm

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
CLIN = ROOT / "data" / "tcga" / "lihc_patient_clinical.json"
OUT_CSV = ROOT / "results" / "nc49_lihc_cox_excc.csv"
OUT_MD = ROOT / "results" / "audit" / "nc49_lihc_cox_excc_2026-09-21.md"

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

def is_cc(s):
    return len(s) >= 7 and s[5:7] == "CC"

# ---- 1. per-tumor table (verbatim pilot logic) ----
pairs = pd.read_csv(PAIRS)
lihc_tt = pairs[(pairs.cancer == "TCGA-LIHC") & (pairs.pair_type == "TT")].copy()
lihc_tn = pairs[(pairs.cancer == "TCGA-LIHC") & (pairs.pair_type == "TN")].copy()

def per_sample_stats(df):
    rows = []
    for col, other in [("sample_a", "sample_b"), ("sample_b", "sample_a")]:
        sub = df[[col, other, "omega_floor", "kf", "kn"]].rename(
            columns={col: "sample", other: "partner",
                     "omega_floor": "omega", "kf": "kf", "kn": "kn"})
        rows.append(sub)
    long = pd.concat(rows, ignore_index=True)
    return long.groupby("sample").agg(
        n_pairs=("omega", "size"),
        omega=("omega", "mean"), kf=("kf", "mean"), kn=("kn", "mean"))

tt_stats = per_sample_stats(lihc_tt).add_prefix("tt_")
tn_rows = []
for col, other in [("sample_a", "sample_b")]:
    tn_rows.append(lihc_tn[[col, "omega_floor", "kf", "kn"]].rename(
        columns={col: "sample", "omega_floor": "omega"}))
tn_stats = pd.concat(tn_rows, ignore_index=True).groupby("sample").agg(
    tn_n_pairs=("omega", "size"), tn_omega=("omega", "mean"),
    tn_kf=("kf", "mean"), tn_kn=("kn", "mean"))
per_tumor = tt_stats.join(tn_stats, how="outer")
per_tumor["patient"] = [s[:12] for s in per_tumor.index]

n_full = len(per_tumor)
cc_tumours = [s for s in per_tumor.index if is_cc(s)]
log(f"per-tumor table: {n_full} tumours; CC (ILSBio) tumours present: {len(cc_tumours)}")

# ---- 2. clinical join (verbatim pilot) ----
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

# ---- 3. ex-CC subset + refit ----
df_ex = df[~df["sample"].map(is_cc)].copy()
log(f"ex-CC tumours: {len(df_ex)} (full {n_full} minus {n_full - len(df_ex)} CC)")

def fit_cox(sub, covars, label, exposure):
    d = sub.dropna(subset=["os_months", "event"] + covars).copy()
    sd = d[exposure].std(ddof=1)
    d["z"] = (d[exposure] - d[exposure].mean()) / sd
    X = d[["z"] + [c for c in covars if c != exposure]].copy()
    X = pd.get_dummies(X, columns=[c for c in X.columns if c in ("sex",)],
                       drop_first=True).astype(float)
    model_cols = list(X.columns)
    ph = PHReg(d["os_months"].values, X.values, status=d["event"].values)
    res = ph.fit()
    rows = []
    for i, name in enumerate(model_cols):
        b = res.params[i]
        se = res.bse[i]
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
for frame, tag in [(df, "full"), (df_ex, "exCC")]:
    all_rows += fit_cox(frame, ["tt_omega", "stage", "grade_ord", "age", "sex"],
                        f"M1_omega_full_{tag}", "tt_omega")
    all_rows += fit_cox(frame, ["tt_omega", "stage", "grade_ord"],
                        f"M2_omega_stage_grade_{tag}", "tt_omega")
    all_rows += fit_cox(frame, ["tt_omega"], f"M3_omega_unadjusted_{tag}", "tt_omega")
    all_rows += fit_cox(frame, ["tt_kf", "stage", "grade_ord", "age", "sex"],
                        f"M4_kf_full_{tag}", "tt_kf")
    all_rows += fit_cox(frame, ["tt_kn", "stage", "grade_ord", "age", "sex"],
                        f"M5_kn_full_{tag}", "tt_kn")
    all_rows += fit_cox(frame, ["tn_omega", "stage", "grade_ord", "age", "sex"],
                        f"M6_tnomega_full_{tag}", "tn_omega")

coef = pd.DataFrame(all_rows)
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
coef.to_csv(OUT_CSV, index=False)
log("")
log("=== ex-CC Cox coefficient table (HR per +1 SD) ===")
log(coef.to_string(index=False))

def fmt(model, tag):
    r = [x for x in all_rows if x["model"] == f"{model}_{tag}" and x["covariate"] == "z"]
    if not r:
        return "NA"
    r = r[0]
    return (f"HR/SD = {r['HR']:.2f} [{r['HR_lower']:.2f}, {r['HR_upper']:.2f}], "
            f"P = {r['p']:.3g} (n = {r['n']}, {r['events']} deaths)")

md = f"""# v49.14 ex-CC Cox sensitivity (LIHC survival)

**Date**: 2026-09-21
**Script**: notebooks/nc49_lihc_cox_excc.py
**Trigger**: fourth-round review R4-M4 — the 32 ILSBio CC tumours (~10% of the n=304 published Cox cohort) entered the survival analysis; ledger disclosed but no ex-CC run existed.

## Design
Identical to results/nc49_pilot_lihc_cox.py (per-tumor TT-mean omega, PHReg, HR per +1 SD), refit after dropping every CC tumour (barcode[5:7]=='CC'): {n_full} -> {len(df_ex)} tumours.

## Full vs ex-CC (omega models)
- M1 omega full-adjusted: full = {fmt('M1_omega_full', 'full')} | ex-CC = {fmt('M1_omega_full', 'exCC')}
- M2 omega + stage + grade: full = {fmt('M2_omega_stage_grade', 'full')} | ex-CC = {fmt('M2_omega_stage_grade', 'exCC')}
- M3 omega unadjusted: full = {fmt('M3_omega_unadjusted', 'full')} | ex-CC = {fmt('M3_omega_unadjusted', 'exCC')}
- M4 k_f full-adjusted: ex-CC = {fmt('M4_kf_full', 'exCC')}
- M5 k_n full-adjusted: ex-CC = {fmt('M5_kn_full', 'exCC')}
- M6 TN-omega full-adjusted: ex-CC = {fmt('M6_tnomega_full', 'exCC')}

Full coefficient table: results/nc49_lihc_cox_excc.csv (both full and exCC rows).
"""
OUT_MD.parent.mkdir(parents=True, exist_ok=True)
OUT_MD.write_text(md, encoding="utf-8")
log("")
log("saved: " + str(OUT_CSV))
log("saved: " + str(OUT_MD))
print("DONE")
