# nc49 pilot audit: LIHC Cox survival go/no-go

**Date**: 2026-09-18
**Script**: notebooks/nc49_pilot_lihc_cox.py
**Data**: results/tcga_linear_norm_v44_all_pairs.csv (LIHC TT 2000 pairs, TN 2000 pairs; per-tumor mean omega/kf/kn); data/tcga/lihc_patient_clinical.json (377 patients, cBioPortal lihc_tcga export).

## Design
- Exposure: per-tumor tissue-level divergence omega (mean over each tumor's TT pairs, v44 linear-normalization values; median 11 pairs/tumor).
- Outcome: OS (status/months); Cox PH (statsmodels PHReg), HR reported per +1 SD.
- Covariates: AJCC stage (I-IV ordinal), Edmondson grade (G1-G4 ordinal), age, sex (full model M1); lead-specified minimum M2 (omega + stage + grade); unadjusted M3; k_f-only M4; k_n-only M5; TN-based omega M6.

## Key numbers (HR per +1 SD)
- M1 omega full-adjusted: HR/SD = 1.06 [0.85, 1.32], P = 0.592 (n = 271, 79 deaths)
- M2 omega + stage + grade: HR/SD = 1.01 [0.81, 1.25], P = 0.932 (n = 271, 79 deaths)
- M3 omega unadjusted: HR/SD = 1.08 [0.88, 1.33], P = 0.451 (n = 293, 93 deaths)
- M4 k_f full-adjusted: HR/SD = 1.07 [0.85, 1.36], P = 0.553 (n = 271, 79 deaths)
- M5 k_n full-adjusted: HR/SD = 0.95 [0.80, 1.14], P = 0.58 (n = 271, 79 deaths)
- M6 TN-omega full-adjusted: HR/SD = 0.89 [0.71, 1.11], P = 0.302 (n = 270, 79 deaths)
- Descriptive: mean TT omega deceased 75.4 vs living 76.4 (MWU P = 0.846, n = 293)

## Verdict
**NO-GO (P >= 0.05 in fully adjusted model)**

Interpretation notes:
- Exposure is bulk tissue-level divergence; composition (purity/stroma) is a known confounder; k_f / k_n component models (M4/M5) indicate which component drives any association.
- HR per SD, so effect magnitude is comparable across models; listwise deletion for missing covariates.
- Full coefficient table: results/nc49_pilot_lihc_cox.csv.
