# v44 Reviewer Controls: Confound, Threshold Sensitivity, and ω Re-calibration

**Date**: 2026-09-04 · **Seed**: 42 (all analyses) · **Scripts**: `notebooks/86_brain_downsample_threshold_v44.py`, `notebooks/87_mouse_splithalf_v44.py` · **Runtime**: 86 = 757 s (12.6 min), 87 = 90 s

Responds to three blind-review questions: (1) is k_n confounded by cell count / sequencing depth? (2) is the 20-cell threshold arbitrary? (3) is the ω = 6.67 baseline calibration stable?

All brain analyses mirror the authoritative observed pipeline of `08d_brain_blockshuffle_null.py` (region = `roi`, region filter ≥ 50 nuclei, gene set = 1,115 HRT HK + top-5,000 non-HK HVG by global mean, pseudobulk = raw mean → normalize 1e4 → log1p, k_n = JS on HK, k_f = JS on per-pair top-200 non-HK DE, ω = k_f/k_n, multiplicative tiers with lowest-in-pair Strong filter). **Validation**: at min-cells = 20 the rerun reproduces `brain_bs_null_observed_pairs.csv` exactly (31,764 pairs; class ω means max relative diff 4.1e-15; grand mean 38.545; Strong = 39).

---

## 1. Count / depth confound control (brain, min-cells = 20, 10 classes)

### 1a. Class-level correlations

| metric | confound | Spearman ρ (p) | Pearson r (p) |
|---|---|---|---|
| k_n | log10(nuclei per class) | **−0.648 (0.043)** | **−0.850 (0.0018)** |
| k_n | mean detected genes | −0.345 (0.33) | −0.192 (0.59) |
| k_n | mean total counts | −0.418 (0.23) | −0.181 (0.62) |
| ω | log10(nuclei per class) | 0.406 (0.24) | 0.562 (0.091) |
| ω | mean detected genes | 0.358 (0.31) | 0.243 (0.50) |
| ω | mean total counts | 0.418 (0.23) | 0.209 (0.56) |

### 1b. Downsample to equal class size (4,118 cells = smallest class, 20 replicates, proportional across regions, no replacement)

- **Class k_n ranking, full vs equal-n: Spearman ρ = −0.055 (p = 0.88)** — the class-level k_n ordering is essentially fully explained by class size.
- **Class ω ranking, full vs equal-n: ρ = 0.370 (p = 0.29)** — attenuated; ordering not preserved at equal n.
- **Astrocyte / Bergmann-glia gradient: 6.10 (full) → 1.74 ± 0.07 (mean ± SD over 20 reps; 95% percentile interval [1.64, 1.84])** — direction retained (interval excludes 1.0), magnitude strongly attenuated.
- Equal-n ω ranking (low→high): Microglia 8.03, Vascular 10.61, Oligodendrocyte 10.76, Bergmann glia 11.41, OPC 12.36, Fibroblast 13.18, Astrocyte 19.83, Ependymal 20.41, Committed OPC 28.84 (reference class, unchanged), Choroid plexus 30.69.

**Conclusion (1)**: class-level **k_n is significantly confounded by class nuclei count** (small classes → noisier HK pseudobulks → larger k_n), but **not by detection depth** (detected genes / total counts: all p > 0.22). **ω itself shows no significant correlation with class size or depth** (all p ≥ 0.091): the sampling-noise factor is shared by k_f and k_n and cancels in the ratio. The Bergmann-glia gradient survives equal-n downsampling in direction (1.74-fold, 95% PI [1.64, 1.84]) but ~70% of the full-data 6.10-fold magnitude reflects class-size imbalance and should be disclosed as such.

## 2. min-cells threshold sensitivity (brain)

| min cells | classes | pairs | Strong | Moderate | Weak | lowest-ω class | Bergmann ω (rank) | Astrocyte ω | Astro/Bergmann |
|---|---|---|---|---|---|---|---|---|---|
| 10 | 10 | 37,361 | 29 | 1,530 | 6,824 | Vascular | 12.53 (2nd) | 82.75 | 6.60 |
| **20 (reference)** | **10** | **31,764** | **39** | **1,171** | **5,381** | **Bergmann glia** | **13.56 (1st)** | **82.75** | **6.10** |
| 50 | 10 | 25,876 | 31 | 784 | 3,964 | Vascular | 20.34 (2nd) | 83.72 | 4.12 |
| 100 | 8 | 22,968 | 22 | 535 | 3,453 | Vascular | dropped | 83.72 | n/a |

Per-class ω means across thresholds (10 / 20 / 50 / 100): Astrocyte 82.7 / 82.7 / 83.7 / 83.7; Oligodendrocyte 37.1 / 37.1 / 37.4 / 37.4; OPC 40.1 / 40.6 / 40.6 / 40.9; Microglia 24.1 / 24.3 / 24.6 / 25.2; Choroid plexus 33.8 / 37.8 / 34.4 / —; Bergmann glia 12.5 / 13.6 / 20.3 / —; Vascular 12.1 / 13.6 / 16.9 / 18.2.

**Conclusion (2)**: the 20-cell threshold is **not arbitrary-sensitive**: the high-ω end of the gradient (Astrocyte, OPC, Oligodendrocyte, Microglia) is stable across all thresholds (≤1% change for the three largest classes), and Strong-tier counts vary modestly (22–39). Two caveats to disclose: (i) the *lowest*-ω position is a near-tie between Bergmann glia and Vascular at t = 20 (13.555 vs 13.559) and flips with threshold choice; (ii) t = 100 drops the two smallest classes (Bergmann glia, Choroid plexus), so the threshold must stay ≤ 50 to retain all 10 classes. t = 20 is a reasonable operating point: it maximizes pair coverage while keeping per-group pseudobulk noise acceptable.

## 3. Mouse ω split-half re-calibration (6 → 50 splits)

50 independent random split-halves per control population × the same 6 FACS control populations as `02b_pilot_v2.py` (Liver hepatocyte, Heart endothelial, Spleen B cell, Marrow B cell, Heart fibroblast, Marrow neutrophil) = **300 split-half ω values**; identical QC / normalization / k_n / k_f definitions as the original calibration.

| statistic | replicate baseline (mean of 6 populations per split, n = 50) | pooled (n = 300) |
|---|---|---|
| mean | **7.696** | 7.696 |
| SD | 1.146 | 3.633 |
| 95% CI (t) | **[7.370, 8.021]** | [7.283, 8.109] |
| 95% CI (bootstrap, B = 10,000) | [7.382, 8.017] | — |

Per-population means (50 splits each): hepatocyte 12.44 ± 5.98, Marrow B cell 7.36 ± 1.39, Heart endothelial 7.23 ± 1.59, Heart fibroblast 7.00 ± 1.73, Spleen B cell 6.38 ± 0.93, Marrow neutrophil 5.77 ± 2.67.

**Conclusion (3)**: with 50 splits the baseline stabilizes at **ω = 7.70, 95% CI [7.37, 8.02]**, versus the previous 6.67 [4.24, 9.24] from a single split of 6 populations. The old point estimate is ~15% lower but lies well inside its own (wide) CI, which overlaps the new one; the difference is single-split sampling noise (the hepatocyte population dominates variance, SD ≈ 6.0). Recommendation: update the calibration constant to **7.70 [7.37, 8.02]** (or state 6.67–7.70 as the plausible range); calibrated-ω conclusions are unchanged qualitatively (e.g. brain grand mean 38.5 → ω_cal ≈ 5.0–5.8 under either baseline).

---

## Output files (all new, `_v44`; no existing results overwritten)

| file | content |
|---|---|
| `results/brain_v44_class_confound.csv` | per-class: n cells, log10 n, mean detected genes / total counts, k_n / k_f / ω means (full + downsampled) |
| `results/brain_v44_confound_correlations.csv` | Spearman + Pearson with p-values (k_n, ω) × (size, depth) |
| `results/brain_v44_downsample_replicates.csv` | per-replicate class ω means + Astrocyte/Bergmann gradient (20 reps) |
| `results/brain_v44_threshold_sensitivity.csv` | per-threshold classes / pairs / tiers / gradient summary |
| `results/brain_v44_threshold_class_omega.csv` | per-class ω mean/median/count at each threshold |
| `results/brain_v44_run_metadata.json` | seed, runtime, validation diff, rank correlations, gradient stats |
| `results/mouse_splithalf_v44.csv` | 300 split-half records (rep × population: k_n, k_f, ω, half sizes) |
| `results/mouse_splithalf_v44_summary.json` / `.txt` | baseline mean / SD / 95% CI vs 6.67 reference |
| `results/_log_86_v44.txt`, `results/_log_87_v44.txt` | run logs |
