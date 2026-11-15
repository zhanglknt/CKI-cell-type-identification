# -*- coding: utf-8 -*-
"""
nc76 (cancer reviewer must-answer Q4): time-dependent handling of the LIHC
cox.zph GLOBAL P = 0.023 (M2) violation.

Two standard remedies on the ex-CC analysis cohort (verbatim
results/nc52_lihc_cox_excc_cohort.csv, M2 = omega + stage(categorical) +
grade):
  (a) time-transform Cox: coxph(Surv ~ z_omega + tt(z_omega) + stage_f +
      grade_ord), tt(x,t) = x*log(t) -- tests and adjusts a log-time-varying
      omega effect;
  (b) epoch-split Cox: survSplit at the median event time; separate HRs per
      epoch for z_omega (with stage/grade per epoch), testing HR(early) =
      HR(late) via a Wald test on their difference.

If the omega HR stays near the original 1.08 [0.88,1.33] P=0.467 in both
remedies, the PH violation is driven by covariates (stage/grade), not omega,
and the null conclusion is time-robust.

Outputs:
  results/nc76_lihc_cox_timevarying.csv / .txt
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COHORT = ROOT / "results" / "nc52_lihc_cox_excc_cohort.csv"
OUT_CSV = ROOT / "results" / "nc76_lihc_cox_timevarying.csv"
OUT_TXT = ROOT / "results" / "nc76_lihc_cox_timevarying.txt"
RSCRIPT = r"C:/Program Files/R/R-4.1.3/bin/x64/Rscript.exe"

R_CODE = r"""
suppressMessages(library(survival))
args <- commandArgs(trailingOnly = TRUE)
d <- read.csv(args[1], stringsAsFactors = FALSE)
d <- d[d$cohort == "exCC_member", ]
d$stage_f <- factor(d$stage, levels = c(1, 2, 3, 4))
d$male <- as.integer(d$sex == "Male")
dd <- d[complete.cases(d[, c("os_months", "event", "z_omega", "stage_f",
                             "grade_ord")]), ]
dd$os_months <- pmax(dd$os_months, 0.01)  # floor zero/negative follow-ups
rows <- list()
add <- function(model, covariate, n, events, coef, se, p) {
  rows[[length(rows) + 1]] <<- data.frame(
    model = model, covariate = covariate, n = n, events = events,
    coef = coef, se = se, HR = exp(coef),
    HR_lower = exp(coef - 1.96 * se), HR_upper = exp(coef + 1.96 * se),
    p = p, stringsAsFactors = FALSE)
}

# --- (a) time-transform Cox ---
f <- try(coxph(Surv(os_months, event) ~ z_omega + tt(z_omega) + stage_f +
               grade_ord, data = dd,
               tt = function(x, t, ...) x * log(t)), silent = TRUE)
if (!inherits(f, "try-error")) {
  s <- summary(f)$coefficients
  for (rn in rownames(s)) {
    add("tt_logt", rn, f$n, f$nevent, s[rn, "coef"], s[rn, "se(coef)"],
        s[rn, "Pr(>|z|)"])
  }
} else {
  cat("tt model failed:", conditionMessage(attr(f, "condition")), "\n")
}

# --- (b) epoch-split Cox at median event time ---
med <- median(dd$os_months[dd$event == 1])
sp <- survSplit(Surv(os_months, event) ~ ., data = dd, cut = med,
                episode = "epoch_idx", id = "id")
f2 <- coxph(Surv(tstart, os_months, event) ~ z_omega * strata(epoch_idx) +
            stage_f + grade_ord, data = sp)
s2 <- summary(f2)$coefficients
for (rn in rownames(s2)) {
  add("epoch_split", rn, f2$n, f2$nevent, s2[rn, "coef"], s2[rn, "se(coef)"],
      s2[rn, "Pr(>|z|)"])
}
# epochs for reporting
ep1 <- sp[sp$epoch_idx == 1, ]; ep2 <- sp[sp$epoch_idx == 2, ]
cat("epoch 1 (<= median ", round(med, 1), " mo): ", length(unique(ep1$id)),
    " subjects, ", sum(ep1$event), " events\n", sep = "")
cat("epoch 2 (> median): ", length(unique(ep2$id)), " subjects, ",
    sum(ep2$event), " events\n", sep = "")
# Wald test HR difference across epochs
co <- coef(f2); V <- vcov(f2)
nm_int <- grep("z_omega:strata", names(co), value = TRUE)
stopifnot(length(nm_int) == 1)
b2 <- co[nm_int]
v <- V[c("z_omega", nm_int), c("z_omega", nm_int)]
d12 <- b2  # difference of epoch2 vs epoch1 log-HRs under interaction coding
se_d <- sqrt(v[1, 1] + v[2, 2] - 2 * v[1, 2])
z_d <- d12 / se_d
cat("Wald (log-HR epoch2 - epoch1): diff=", round(d12, 3),
    " se=", round(se_d, 3), " z=", round(z_d, 3),
    " p=", round(2 * pnorm(-abs(z_d)), 4), "\n", sep = "")
rows[[length(rows) + 1]] <- data.frame(
  model = "wald_diff_epoch2_minus_epoch1", covariate = "z_omega",
  n = f2$n, events = f2$nevent, coef = d12, se = se_d,
  HR = exp(d12), HR_lower = exp(d12 - 1.96 * se_d),
  HR_upper = exp(d12 + 1.96 * se_d), p = 2 * pnorm(-abs(z_d)),
  stringsAsFactors = FALSE)

write.csv(do.call(rbind, rows), args[2], row.names = FALSE)
cat("R_OK\n")
"""

with tempfile.TemporaryDirectory() as td:
    r_script = Path(td) / "nc76.R"
    r_cohort = Path(td) / "cohort.csv"
    r_out = Path(td) / "out.csv"
    import shutil
    shutil.copyfile(COHORT, r_cohort)
    r_script.write_text(R_CODE, encoding="utf-8")
    proc = subprocess.run([RSCRIPT, str(r_script), str(r_cohort), str(r_out)],
                          capture_output=True, timeout=600)
    out = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")
    print(out)
    if proc.returncode != 0 or "R_OK" not in out:
        print("R STDERR:\n" + err)
        sys.exit("R time-varying Cox FAILED")
    res = pd.read_csv(r_out)

res.to_csv(OUT_CSV, index=False)
lines = ["nc76 LIHC time-dependent Cox (cancer Q4)", "=" * 50, out,
         "", res.to_string(index=False)]
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("DONE")
