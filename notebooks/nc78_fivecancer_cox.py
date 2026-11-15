# -*- coding: utf-8 -*-
"""
nc78 P0 (cancer reviewer M5): unified five-cancer overall-survival Cox
analysis of per-tumour omega / k_f / k_n.

Motivation: the pre-revision manuscript reported Cox models only for LIHC
(HR/SD 1.08 [0.88,1.33], P=0.467), and LIHC is the cancer with the weakest
housekeeping-divergence reversal -- "testing clinical translation only at the
weakest link". Here the SAME model is fit in all five cancers
(BRCA/KIRC/LIHC/LUAD/LUSC), on the authoritative per-tumour scores aggregated
from results/tcga_linear_norm_v44_all_pairs.csv (TT pairs), with clinical
covariates from the uniform PanCanAtlas follow-up table
(data/fivecancer_mechanisms_20261031/metadata/
clinical_PANCAN_patient_with_followup.tsv).

Design (mirrors notebooks/nc52_lihc_cox_excc.py for cross-consistency):
  - exposure: per-tumour TT-mean omega (primary), k_f and k_n (reference),
    z-standardised WITHIN cancer over the analysis cohort;
  - adjustments: AJCC pathologic stage (categorical I-IV) + age + male;
    histologic grade (ordinal G1-G4) is only available in KIRC and LIHC in
    the PanCanAtlas table and enters the model only there;
  - LIHC excludes ILSBio "CC" tumours exactly as nc52 (the published
    analysis cohort); other cancers have no CC aliquots;
  - proportional-hazards diagnostics: survival::cox.zph per model
    (per-covariate + GLOBAL), fit in R 4.1.3 (reference implementation);
    the script aborts loudly if the R call fails (no silent fallback);
  - multiplicity: BH FDR across the five z_omega Wald P values (M1 family)
    and, separately, across the five z_kf and five z_kn P values.

Outputs:
  results/nc78_fivecancer_cox.csv        coefficient table (all models)
  results/nc78_fivecancer_cox_zph.csv    cox.zph per-covariate + GLOBAL
  results/nc78_fivecancer_cox_cohort.csv analysis cohort (transparency)
  results/nc78_fivecancer_cox.txt        human-readable digest
Seed: none (Cox PH is deterministic).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
CLIN = (ROOT / "data" / "fivecancer_mechanisms_20261031" / "metadata"
        / "clinical_PANCAN_patient_with_followup.tsv")
OUT_CSV = ROOT / "results" / "nc78_fivecancer_cox.csv"
OUT_ZPH = ROOT / "results" / "nc78_fivecancer_cox_zph.csv"
OUT_COHORT = ROOT / "results" / "nc78_fivecancer_cox_cohort.csv"
OUT_TXT = ROOT / "results" / "nc78_fivecancer_cox.txt"
RSCRIPT = r"C:/Program Files/R/R-4.1.3/bin/x64/Rscript.exe"

CANCERS = ["TCGA-BRCA", "TCGA-KIRC", "TCGA-LIHC", "TCGA-LUAD", "TCGA-LUSC"]
GRADE_OK = {"KIRC", "LIHC"}  # PanCanAtlas grade coverage

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

def is_cc(s):
    return len(s) >= 7 and s[5:7] == "CC"

# ---- 1. per-tumour scores from authoritative TT pairs (verbatim nc52) ----
pairs = pd.read_csv(PAIRS)
tt = pairs[(pairs.cancer.isin(CANCERS)) & (pairs.pair_type == "TT")].copy()

rows_long = []
for col in ["sample_a", "sample_b"]:
    rows_long.append(tt[["cancer", col, "omega_floor", "kf", "kn"]].rename(
        columns={col: "sample", "omega_floor": "omega"}))
long = pd.concat(rows_long, ignore_index=True)
per_tumor = long.groupby(["cancer", "sample"]).agg(
    n_pairs=("omega", "size"), omega=("omega", "mean"),
    kf=("kf", "mean"), kn=("kn", "mean")).reset_index()
per_tumor["patient"] = per_tumor["sample"].str[:12]
log("per-tumour TT-mean table: " +
    ", ".join(f"{c[5:]}={n}" for c, n in
              per_tumor.groupby("cancer").size().items()))

# ---- 2. clinical join (PanCanAtlas follow-up table, latin1) ----
clin = pd.read_csv(CLIN, sep="\t", low_memory=False, encoding="latin1")
clin = clin[clin.acronym.isin([c[5:] for c in CANCERS])].copy()
clin["patient"] = clin["bcr_patient_barcode"].str.upper()

STAGE_MAP = {}
for base, v in [("Stage I", 1), ("Stage II", 2), ("Stage III", 3),
                ("Stage IV", 4)]:
    for suf in ["", "A", "B", "C", "D", "A1", "A2", "NOS"]:
        STAGE_MAP[base + suf] = v
GRADE_MAP = {"G1": 1, "G2": 2, "G3": 3, "G4": 4}

clin["days_to_death"] = pd.to_numeric(clin["days_to_death"],
                                      errors="coerce")
clin["days_to_last_followup"] = pd.to_numeric(
    clin["days_to_last_followup"], errors="coerce")

def os_months(r):
    d = r["days_to_death"] if pd.notna(r["days_to_death"]) \
        else r["days_to_last_followup"]
    return d / 30.4375 if pd.notna(d) else np.nan

clin["event"] = (clin["vital_status"] == "Dead").astype(int)
clin["os_months"] = clin.apply(os_months, axis=1)
clin["stage"] = clin["pathologic_stage"].map(STAGE_MAP)
clin["grade_ord"] = clin["neoplasm_histologic_grade"].map(GRADE_MAP)
clin["age"] = pd.to_numeric(clin["age_at_initial_pathologic_diagnosis"],
                            errors="coerce")
clin["male"] = (clin["gender"] == "MALE").astype(int)
keep = ["patient", "event", "os_months", "stage", "grade_ord", "age", "male"]
clin = clin[keep].drop_duplicates("patient")

df = per_tumor.merge(clin, on="patient", how="left")
df["cohort_ok"] = True
# LIHC: exclude ILSBio CC tumours exactly as nc52 (default analysis cohort)
cc_mask = (df.cancer == "TCGA-LIHC") & df["sample"].map(is_cc)
df.loc[cc_mask, "cohort_ok"] = False
log(f"LIHC CC (ILSBio) tumours excluded: {int(cc_mask.sum())}")

# z-standardise exposures within cancer over the analysis cohort
for col in ["omega", "kf", "kn"]:
    df["z_" + col] = np.nan
    for c in CANCERS:
        m = (df.cancer == c) & df.cohort_ok
        mu, sd = df.loc[m, col].mean(), df.loc[m, col].std(ddof=1)
        df.loc[df.cancer == c, "z_" + col] = (df.loc[df.cancer == c, col]
                                              - mu) / sd

df["grade_ord"] = df.apply(
    lambda r: r["grade_ord"] if r["cancer"][5:] in GRADE_OK else np.nan,
    axis=1)

cohort = df[["cancer", "sample", "patient", "os_months", "event", "stage",
             "grade_ord", "age", "male", "z_omega", "z_kf", "z_kn",
             "omega", "kf", "kn", "n_pairs", "cohort_ok"]].copy()
cohort.to_csv(OUT_COHORT, index=False)
log("saved cohort: " + str(OUT_COHORT))
ok = cohort[cohort.cohort_ok]
log("analysis cohort sizes / events / complete cases:")
for c in CANCERS:
    d = ok[ok.cancer == c]
    cc = d.dropna(subset=["os_months", "event", "z_omega", "stage", "age",
                          "male"])
    log(f"  {c[5:]}: n={len(d)}, events={int(d.event.sum())}, "
        f"complete={len(cc)} (grade avail: {int(d.grade_ord.notna().sum())})")

# ---- 3. R survival fits (coxph + cox.zph), per cancer ----
R_CODE = r"""
suppressMessages(library(survival))
args <- commandArgs(trailingOnly = TRUE)
cohort_file <- args[1]; out_coef <- args[2]; out_zph <- args[3]
d <- read.csv(cohort_file, stringsAsFactors = FALSE)
d <- d[d$cohort_ok == "True", ]
d$stage_f <- factor(d$stage, levels = c(1, 2, 3, 4))
cancers <- c("TCGA-BRCA", "TCGA-KIRC", "TCGA-LIHC", "TCGA-LUAD", "TCGA-LUSC")
grade_ok <- c("TCGA-KIRC", "TCGA-LIHC")

fit_one <- function(dat, formula_str, label) {
  dd <- dat[complete.cases(dat[, all.vars(formula(formula_str))]), ]
  dd <- dd[dd$os_months > 0, ]
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

all_coef <- list(); all_zph <- list()
for (ca in cancers) {
  sub <- d[d$cancer == ca, ]
  adj <- "stage_f + age + male"
  if (ca %in% grade_ok) adj <- paste0(adj, " + grade_ord")
  forms <- list(
    M1_omega = paste0("Surv(os_months, event) ~ z_omega + ", adj),
    M4_kf    = paste0("Surv(os_months, event) ~ z_kf + ", adj),
    M5_kn    = paste0("Surv(os_months, event) ~ z_kn + ", adj))
  if (ca == "TCGA-LIHC") {
    # continuity with the published nc52 M2 fit (omega + stage + grade)
    forms[["M2_omega_stage_grade"]] <-
      "Surv(os_months, event) ~ z_omega + stage_f + grade_ord"
  }
  for (nm in names(forms)) {
    r <- fit_one(sub, forms[[nm]], paste0(ca, "_", nm))
    all_coef[[length(all_coef) + 1]] <- r$coef
    all_zph[[length(all_zph) + 1]] <- r$zph
  }
}
write.csv(do.call(rbind, all_coef), out_coef, row.names = FALSE)
write.csv(do.call(rbind, all_zph), out_zph, row.names = FALSE)

# --- PH-violation remedies for the nominally significant omega models ---
# (mirrors notebooks/nc76_lihc_cox_timevarying.py: tt(x)=x*log(t) and an
# epoch-split at the median event time with a Wald test of HR difference)
rem_rows <- list()
add_rem <- function(model, covariate, n, events, coef, se, p) {
  rem_rows[[length(rem_rows) + 1]] <<- data.frame(
    model = model, covariate = covariate, n = n, events = events,
    coef = coef, se = se, HR = exp(coef),
    HR_lower = exp(coef - 1.96 * se), HR_upper = exp(coef + 1.96 * se),
    p = p, stringsAsFactors = FALSE)
}
remedies <- list(
  list(ca = "TCGA-KIRC", adj = "stage_f + age + male + grade_ord",
       covs = c("stage_f", "age", "male", "grade_ord")),
  list(ca = "TCGA-LUSC", adj = "stage_f + age + male",
       covs = c("stage_f", "age", "male")))
for (rem in remedies) {
  ca <- rem$ca; adj <- rem$adj; covs <- rem$covs
  sub <- d[d$cancer == ca, ]
  dd <- sub[complete.cases(sub[, c("os_months", "event", "z_omega",
                                  covs)]) & sub$os_months > 0, ]
  f_tt <- try(coxph(as.formula(paste0(
      "Surv(os_months, event) ~ z_omega + tt(z_omega) + ", adj)),
    data = dd, tt = function(x, t, ...) x * log(t)), silent = TRUE)
  if (!inherits(f_tt, "try-error")) {
    s <- summary(f_tt)$coefficients
    for (rn in rownames(s)) {
      add_rem(paste0(ca, "_tt_logt"), rn, f_tt$n, f_tt$nevent,
              s[rn, "coef"], s[rn, "se(coef)"], s[rn, "Pr(>|z|)"])
    }
  }
  med <- median(dd$os_months[dd$event == 1])
  sp <- survSplit(Surv(os_months, event) ~ ., data = dd, cut = med,
                  episode = "epoch_idx", id = "id")
  f2 <- coxph(as.formula(paste0(
      "Surv(tstart, os_months, event) ~ z_omega * strata(epoch_idx) + ",
      adj)), data = sp)
  s2 <- summary(f2)$coefficients
  for (rn in rownames(s2)) {
    add_rem(paste0(ca, "_epoch_split"), rn, f2$n, f2$nevent,
            s2[rn, "coef"], s2[rn, "se(coef)"], s2[rn, "Pr(>|z|)"])
  }
  co <- coef(f2); V <- vcov(f2)
  nm_int <- grep("z_omega:strata", names(co), value = TRUE)
  if (length(nm_int) == 1) {
    v <- V[c("z_omega", nm_int), c("z_omega", nm_int)]
    se_d <- sqrt(v[1, 1] + v[2, 2] - 2 * v[1, 2])
    z_d <- co[nm_int] / se_d
    add_rem(paste0(ca, "_wald_epoch2_minus_epoch1"), "z_omega",
            f2$n, f2$nevent, co[nm_int], se_d, 2 * pnorm(-abs(z_d)))
  }
  cat(ca, "remedy done (median event time", round(med, 1), "mo)\n")
}
write.csv(do.call(rbind, rem_rows), args[4], row.names = FALSE)
cat("R_OK\n")
"""

with tempfile.TemporaryDirectory() as td:
    r_script = Path(td) / "nc78_cox.R"
    r_cohort = Path(td) / "cohort.csv"  # ASCII path: R (GBK locale) cannot
    r_coef = Path(td) / "coef.csv"      # resolve the Chinese project path
    r_zph = Path(td) / "zph.csv"
    r_rem = Path(td) / "remedy.csv"
    import shutil
    shutil.copyfile(OUT_COHORT, r_cohort)
    r_script.write_text(R_CODE, encoding="utf-8")
    cmd = [RSCRIPT, str(r_script), str(r_cohort), str(r_coef), str(r_zph),
           str(r_rem)]
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
    remedy = pd.read_csv(r_rem)

glob = zph[zph.covariate == "GLOBAL"][["model", "zph_p"]].rename(
    columns={"zph_p": "zph_GLOBAL_p"})
coef = coef.merge(glob, on="model", how="left")
coef.to_csv(OUT_CSV, index=False)
zph.to_csv(OUT_ZPH, index=False)
log("saved: " + str(OUT_CSV))
log("saved: " + str(OUT_ZPH))
OUT_REM = ROOT / "results" / "nc78_fivecancer_cox_remedy.csv"
remedy.to_csv(OUT_REM, index=False)
log("saved: " + str(OUT_REM))

# ---- 4. BH FDR across cancers per exposure family (M1/M4/M5) ----
def bh_q(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    q = np.empty_like(p)
    m = len(p)
    prev = 1.0
    for rank, idx in enumerate(order[::-1], start=1):
        k = m - rank + 1
        prev = min(prev, p[idx] * m / k)
        q[idx] = prev
    return q

fam_rows = []
for fam, cov in [("M1_omega", "z_omega"), ("M4_kf", "z_kf"),
                 ("M5_kn", "z_kn")]:
    sub = coef[(coef.covariate == cov)
               & coef.model.str.endswith(fam)].copy()
    sub = sub[sub.model.str.split("_").str[0].isin(
        ["TCGA-BRCA", "TCGA-KIRC", "TCGA-LIHC", "TCGA-LUAD", "TCGA-LUSC"])]
    # keep only the five primary rows (exclude LIHC M2 from the family)
    sub["q_BH5"] = bh_q(sub.p.values)
    fam_rows.append(sub)
fams = pd.concat(fam_rows, ignore_index=True)
fams.to_csv(ROOT / "results" / "nc78_fivecancer_cox_fdr.csv", index=False)

log("")
log("=== exposure rows (HR per +1 SD, fully adjusted) ===")
show = coef[coef.covariate.str.startswith("z_")].copy()
for _, r in show.iterrows():
    log(f"{r['model']:<34} {r['covariate']:<9} HR={r['HR']:.3f} "
        f"[{r['HR_lower']:.3f},{r['HR_upper']:.3f}] P={r['p']:.3g} "
        f"(n={int(r['n'])}, events={int(r['events'])}, "
        f"zph_GLOBAL_P={r['zph_GLOBAL_p']:.3g})")
log("")
log("=== BH FDR across the five cancers (per exposure family) ===")
for _, r in fams.iterrows():
    log(f"{r['model']:<34} P={r['p']:.3g}  q_BH5={r['q_BH5']:.3g}")
log("")
log("=== PH-violation remedies (tt / epoch-split), omega rows ===")
for _, r in remedy[remedy.covariate.str.contains("z_omega")].iterrows():
    log(f"{r['model']:<40} {r['covariate']:<22} HR={r['HR']:.3f} "
        f"[{r['HR_lower']:.3f},{r['HR_upper']:.3f}] P={r['p']:.3g}")

OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("DONE")
