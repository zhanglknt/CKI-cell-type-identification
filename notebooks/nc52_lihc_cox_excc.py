# -*- coding: utf-8 -*-
"""
nc52 (v52 revision, reviewer B1, LIHC survival): ex-CC LIHC Cox models with
stage as a CATEGORICAL covariate, proportional-hazards assumption testing
(cox.zph, Grambsch-Therneau), and the k_f model reported alongside omega.

Changes vs notebooks/nc49_lihc_cox_excc.py (v49.14 sensitivity):
  1. ex-CC is now the DEFAULT cohort (the with-CC fit is kept as a reference
     block in the same output for continuity).
  2. AJCC stage enters as a categorical factor (I/II/III/IV dummies, ref I),
     not an ordinal score.
  3. PH assumption: survival::cox.zph per model (per-covariate + GLOBAL),
     reported for every model.
  4. k_f model (M4) reported in full, mirroring the omega M1.

Cohort construction (per-tumour TT-mean omega/kf/kn + TN omega, clinical join)
is verbatim nc49_lihc_cox_excc.py. Model fitting is delegated to R
(survival package, R 4.1.3 at C:/Program Files/R/R-4.1.3) so that the PH
diagnostic is the reference cox.zph implementation rather than a hand-rolled
Schoenfeld test. If the R call fails the script aborts loudly (no silent
fallback).

Inputs (read-only):
  results/tcga_linear_norm_v44_all_pairs.csv
  data/tcga/lihc_patient_clinical.json
Outputs:
  results/nc52_lihc_cox_excc.csv        coefficient table (all models, PH cols)
  results/nc52_lihc_cox_excc_zph.csv    cox.zph per-covariate + GLOBAL table
  results/nc52_lihc_cox_excc_cohort.csv analysis cohort (transparency)
Seed: none (Cox PH is deterministic).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
CLIN = ROOT / "data" / "tcga" / "lihc_patient_clinical.json"
OUT_CSV = ROOT / "results" / "nc52_lihc_cox_excc.csv"
OUT_ZPH = ROOT / "results" / "nc52_lihc_cox_excc_zph.csv"
OUT_COHORT = ROOT / "results" / "nc52_lihc_cox_excc_cohort.csv"

RSCRIPT = r"C:/Program Files/R/R-4.1.3/bin/x64/Rscript.exe"

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

def is_cc(s):
    return len(s) >= 7 and s[5:7] == "CC"

# ---- 1. per-tumor table (verbatim nc49_lihc_cox_excc) ----
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
log(f"per-tumor table: {n_full} tumours; CC (ILSBio) tumours: {len(cc_tumours)}")

# ---- 2. clinical join (verbatim nc49) ----
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
df["cohort"] = np.where(df["sample"].map(is_cc), "full_onlyCC", "exCC_member")

# z-standardize exposures over the ex-CC cohort (the default population);
# the same scaling is applied to the with-CC reference fit for comparability.
df_ex = df[~df["sample"].map(is_cc)].copy()
log(f"ex-CC tumours: {len(df_ex)} (full {n_full} minus {n_full - len(df_ex)} CC)")
for col, z in [("tt_omega", "z_omega"), ("tt_kf", "z_kf"), ("tt_kn", "z_kn"),
               ("tn_omega", "z_tnomega")]:
    mu, sd = df_ex[col].mean(), df_ex[col].std(ddof=1)
    df[z] = (df[col] - mu) / sd

cohort = df[["sample", "patient", "os_months", "event", "stage", "grade_ord",
             "age", "sex", "z_omega", "z_kf", "z_kn", "z_tnomega",
             "tt_omega", "tt_kf", "tt_kn", "tn_omega", "cohort"]].copy()
cohort.to_csv(OUT_COHORT, index=False)
log("saved cohort: " + str(OUT_COHORT))

# ---- 3. R survival fits (coxph + cox.zph) ----
R_CODE = r"""
suppressMessages(library(survival))
args <- commandArgs(trailingOnly = TRUE)
cohort_file <- args[1]; out_coef <- args[2]; out_zph <- args[3]
d <- read.csv(cohort_file, stringsAsFactors = FALSE)
d$stage_f <- factor(d$stage, levels = c(1, 2, 3, 4))
d$male <- as.integer(d$sex == "Male")

fit_one <- function(dat, formula_str, label) {
  dd <- dat[complete.cases(dat[, all.vars(formula(formula_str))]), ]
  f <- coxph(as.formula(formula_str), data = dd)
  s <- summary(f)
  co <- as.data.frame(coef(s))
  co$covariate <- rownames(co)
  rownames(co) <- NULL
  ci <- suppressMessages(confint(f))
  out <- data.frame(
    model = label, covariate = co$covariate, n = f$n, events = f$nevent,
    coef = co[, "coef"], se = co[, "se(coef)"],
    HR = exp(co[, "coef"]),
    HR_lower = exp(ci[, 1]), HR_upper = exp(ci[, 2]),
    z = co[, "z"], p = co[, "Pr(>|z|)"], stringsAsFactors = FALSE)
  zp <- cox.zph(f)
  zt <- as.data.frame(zp$table)
  zt$covariate <- rownames(zt)
  rownames(zt) <- NULL
  ztab <- data.frame(model = label, covariate = zt$covariate,
                     chisq = zt$chisq, df = zt$df, zph_p = zt$p,
                     stringsAsFactors = FALSE)
  list(coef = out, zph = ztab)
}

FORMS <- list(
  M1_omega_full        = "Surv(os_months, event) ~ z_omega + stage_f + grade_ord + age + male",
  M2_omega_stage_grade = "Surv(os_months, event) ~ z_omega + stage_f + grade_ord",
  M3_omega_unadjusted  = "Surv(os_months, event) ~ z_omega",
  M4_kf_full           = "Surv(os_months, event) ~ z_kf + stage_f + grade_ord + age + male",
  M5_kn_full           = "Surv(os_months, event) ~ z_kn + stage_f + grade_ord + age + male",
  M6_tnomega_full      = "Surv(os_months, event) ~ z_tnomega + stage_f + grade_ord + age + male"
)

all_coef <- list(); all_zph <- list()
ex <- d[d$cohort == "exCC_member", ]
for (nm in names(FORMS)) {
  r <- fit_one(ex, FORMS[[nm]], paste0(nm, "_exCC"))
  all_coef[[length(all_coef) + 1]] <- r$coef
  all_zph[[length(all_zph) + 1]] <- r$zph
}
# with-CC reference (legacy default; kept for continuity)
for (nm in names(FORMS)) {
  r <- fit_one(d, FORMS[[nm]], paste0(nm, "_withCC_ref"))
  all_coef[[length(all_coef) + 1]] <- r$coef
  all_zph[[length(all_zph) + 1]] <- r$zph
}
write.csv(do.call(rbind, all_coef), out_coef, row.names = FALSE)
write.csv(do.call(rbind, all_zph), out_zph, row.names = FALSE)
cat("R_OK\n")
"""

with tempfile.TemporaryDirectory() as td:
    r_script = Path(td) / "nc52_cox.R"
    r_cohort = Path(td) / "cohort.csv"  # ASCII path: R (GBK locale) cannot
    r_coef = Path(td) / "coef.csv"      # resolve the Chinese project path
    r_zph = Path(td) / "zph.csv"
    import shutil
    shutil.copyfile(OUT_COHORT, r_cohort)
    r_script.write_text(R_CODE, encoding="utf-8")
    cmd = [RSCRIPT, str(r_script), str(r_cohort), str(r_coef), str(r_zph)]
    log("calling R: " + " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, timeout=600)
    r_out = proc.stdout.decode("utf-8", errors="replace")
    r_err = proc.stderr.decode("utf-8", errors="replace")
    log(r_out.strip())
    if proc.returncode != 0 or "R_OK" not in r_out:
        log("R STDERR:\n" + r_err)
        sys.exit("R survival fit FAILED - aborting (no fallback).")
    coef = pd.read_csv(r_coef)
    zph = pd.read_csv(r_zph)

# attach GLOBAL zph p to each model block for convenience
glob = zph[zph.covariate == "GLOBAL"][["model", "zph_p"]].rename(
    columns={"zph_p": "zph_GLOBAL_p"})
coef = coef.merge(glob, on="model", how="left")
coef.to_csv(OUT_CSV, index=False)
zph.to_csv(OUT_ZPH, index=False)
log("saved: " + str(OUT_CSV))
log("saved: " + str(OUT_ZPH))

# ---- 4. console digest: exposure rows (z_*) ----
show = coef[coef.covariate.str.startswith("z_")]
log("")
log("=== exposure rows (HR per +1 SD) ===")
for _, r in show.iterrows():
    log(f"{r['model']:<38} {r['covariate']:<10} HR={r['HR']:.3f} "
        f"[{r['HR_lower']:.3f},{r['HR_upper']:.3f}] P={r['p']:.3g} "
        f"(n={int(r['n'])}, events={int(r['events'])}, zph_GLOBAL_P={r['zph_GLOBAL_p']:.3g})")
print("DONE")
