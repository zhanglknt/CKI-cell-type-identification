# results/ — Notes on Archived Outputs

## Superseded calibration constant in `phaseC_calibrated_cis.csv`

`phaseC_calibrated_cis.csv` (Phase C, C-M1) derives its `omega_cal_*` columns
by deterministic division by **6.67**, the legacy six-split mouse split-half
baseline. That constant is **superseded by 7.70** (95% CI [7.37, 8.02]; 50
replicates across six control populations, 300 omega values;
`results/mouse_splithalf_v44.csv`). All calibrated values quoted in the
manuscript use the 7.70 baseline; the CSV is retained for provenance and for
downstream loaders that depend on its column layout. See the Reproducibility
Guide (Sections 5.4a and 5.7) for the authoritative calibration.

Other superseded pre-fix outputs are consolidated under `results/superseded/`
(see the Reproducibility Guide Section 6); they must not be used as numerical
sources.
