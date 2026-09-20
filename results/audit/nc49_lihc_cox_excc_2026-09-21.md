# v49.14 ex-CC Cox sensitivity (LIHC survival)

**Date**: 2026-09-21
**Script**: notebooks/nc49_lihc_cox_excc.py
**Trigger**: fourth-round review R4-M4 — the 32 ILSBio CC tumours (~10% of the n=304 published Cox cohort) entered the survival analysis; ledger disclosed but no ex-CC run existed.

## Design
Identical to results/nc49_pilot_lihc_cox.py (per-tumor TT-mean omega, PHReg, HR per +1 SD), refit after dropping every CC tumour (barcode[5:7]=='CC'): 398 -> 366 tumours.

## Full vs ex-CC (omega models)
- M1 omega full-adjusted: full = HR/SD = 1.07 [0.88, 1.31], P = 0.475 (n = 304, 101 deaths) | ex-CC = HR/SD = 1.08 [0.87, 1.35], P = 0.474 (n = 272, 79 deaths)
- M2 omega + stage + grade: full = HR/SD = 1.04 [0.86, 1.27], P = 0.651 (n = 304, 101 deaths) | ex-CC = HR/SD = 1.00 [0.81, 1.24], P = 0.994 (n = 272, 79 deaths)
- M3 omega unadjusted: full = HR/SD = 1.10 [0.91, 1.32], P = 0.312 (n = 326, 115 deaths) | ex-CC = HR/SD = 1.06 [0.87, 1.30], P = 0.572 (n = 294, 93 deaths)
- M4 k_f full-adjusted: ex-CC = HR/SD = 1.07 [0.84, 1.36], P = 0.573 (n = 272, 79 deaths)
- M5 k_n full-adjusted: ex-CC = HR/SD = 0.92 [0.77, 1.11], P = 0.396 (n = 272, 79 deaths)
- M6 TN-omega full-adjusted: ex-CC = HR/SD = 0.97 [0.77, 1.22], P = 0.797 (n = 268, 77 deaths)

Full coefficient table: results/nc49_lihc_cox_excc.csv (both full and exCC rows).
