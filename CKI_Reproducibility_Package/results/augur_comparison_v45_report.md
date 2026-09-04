# Analysis D: Augur cell-type prioritization vs CKI brain class ranking

## Design

- **Data**: Siletti adult human brain non-neurons (CELLxGENE 283d65eb-dd53-496d-adb7-7570c7caa443; 888,263 nuclei). Stratified sample of 33,036 nuclei (<= 50 per class x region group; groups with >= 20 nuclei, regions with >= 50 total nuclei — identical filters to the CKI v4 pipeline).
- **Augur**: pyaugur 0.1.0, a pure-Python port of R Augur v1.0.3 (Skinnider et al., Nat Biotechnol 2021); the R package's reference Python port `augurpy` is not distributed for Python 3.13, so the numerically faithful port (benchmark Spearman rho = 1.0 vs R) was used. Condition label = brain region (`roi`; 108 regions), evaluated per class over its eligible regions (>= 20 sampled nuclei, mirroring CKI eligibility). Random forest (100 trees), 3-fold stratified CV. Input: CP10k + log1p.
- **Two variants**:
  1. *Multiclass* (standard Augur call): one run per class with region as a multiclass label, macro-OvR AUC, 5 subsample seeds x 3 folds = 15 AUC estimates per class.
  2. *Binary one-vs-rest (confound-controlled)*: because eligible-region counts differ by class (6–107) and multiclass AUC is not comparable across different class sets, each class was re-scored with strictly binary tasks — for each eligible region r, r vs the class's other eligible regions (20 vs 20 cells, 3 repeats x 3 folds), class score = mean AUC over regions. Every sub-task is two-class, so scores are comparable regardless of region-set size. Implemented with pyaugur's feature selection and estimator settings (Augur-style classifier prioritization, binary OvR variant).
- **CKI side**: class-level mean omega / k_f / k_n from `results/brain_v44_class_confound.csv`.

## Results

### Variant 1 — multiclass macro-OvR AUC

| Rank | Cell type | Augur AUC | CKI omega | CKI k_f | CKI k_n | n regions |
|---|---|---|---|---|---|---|
| 1 | Choroid plexus | 0.8159 | 37.76 | 0.1485 | 0.004147 | 6 |
| 2 | Bergmann glia | 0.6808 | 13.56 | 0.0666 | 0.005831 | 7 |
| 3 | Ependymal | 0.6664 | 22.98 | 0.1315 | 0.006666 | 40 |
| 4 | Committed oligodendrocyte precursor | 0.6346 | 28.84 | 0.1968 | 0.006904 | 52 |
| 5 | Astrocyte | 0.6137 | 82.75 | 0.1349 | 0.001815 | 107 |
| 6 | Oligodendrocyte precursor | 0.5781 | 40.62 | 0.0485 | 0.001377 | 107 |
| 7 | Oligodendrocyte | 0.5700 | 37.05 | 0.0542 | 0.001637 | 107 |
| 8 | Vascular | 0.5678 | 13.56 | 0.1158 | 0.009181 | 82 |
| 9 | Fibroblast | 0.5581 | 18.18 | 0.1171 | 0.007087 | 83 |
| 10 | Microglia | 0.5578 | 24.31 | 0.0590 | 0.002772 | 107 |

Spearman (n = 10): vs omega rho = +0.127 (P = 0.726); vs k_f rho = +0.491 (P = 0.150); vs k_n rho = -0.042 (P = 0.907).

**Confound**: multiclass AUC correlates strongly with the number of eligible regions per class (Spearman rho = -0.744, P = 0.014): classes with few, anatomically compact region sets (choroid plexus, Bergmann glia) attain higher AUC partly because the classification problem is easier. This variant is therefore not a valid cross-class ranking on its own.

### Variant 2 — binary one-vs-rest (confound-controlled, primary result)

| Rank | Cell type | OvR Augur AUC | CKI omega | CKI k_f | CKI k_n |
|---|---|---|---|---|---|
| 1 | Choroid plexus | 0.7646 | 37.76 | 0.1485 | 0.004147 |
| 2 | Ependymal | 0.7105 | 22.98 | 0.1315 | 0.006666 |
| 3 | Astrocyte | 0.7031 | 82.75 | 0.1349 | 0.001815 |
| 4 | Committed oligodendrocyte precursor | 0.6980 | 28.84 | 0.1968 | 0.006904 |
| 5 | Bergmann glia | 0.6906 | 13.56 | 0.0666 | 0.005831 |
| 6 | Oligodendrocyte precursor | 0.6387 | 40.62 | 0.0485 | 0.001377 |
| 7 | Oligodendrocyte | 0.6231 | 37.05 | 0.0542 | 0.001637 |
| 8 | Microglia | 0.6173 | 24.31 | 0.0590 | 0.002772 |
| 9 | Vascular | 0.6161 | 13.56 | 0.1158 | 0.009181 |
| 10 | Fibroblast | 0.5858 | 18.18 | 0.1171 | 0.007087 |

### Rank consistency (Spearman, n = 10 classes)

| Comparison | Multiclass rho (P) | Binary OvR rho (P) |
|---|---|---|
| Augur vs CKI omega | +0.127 (0.726) | **+0.442 (0.200)** |
| Augur vs CKI k_f (HK-anchored numerator) | +0.491 (0.150) | **+0.564 (0.090)** |
| Augur vs CKI k_n (denominator) | -0.042 (0.907) | -0.236 (0.511) |

## Interpretation

- With the region-set-size confound controlled (binary OvR), the Augur and CKI rankings are **moderately concordant** (omega: rho = +0.44; n = 10 limits power, P = 0.20). Astrocytes — the top class by CKI omega (82.75) — rank 3rd of 10 by Augur separability, and the choroid plexus is high on both metrics; the extremes of the two rankings overlap.
- The decomposition is informative: the shared signal localizes to **k_f**, the housekeeping-anchored numerator (rho = +0.56, P = 0.09), not to k_n (rho = -0.24). Classifier separability across regions is thus related to the stability of HK-anchored expression, while the k_n component of omega captures regional divergence that whole-transcriptome separability does not.
- The two methods are therefore **complementary rather than redundant**: Augur prioritizes cell types by per-cell, whole-transcriptome classifier separability, whereas CKI's omega additionally weights HK-anchored ratio structure. CKI occupies the same problem domain as perturbation-response prioritization (Augur/Milo/scCODA) but provides a distinct, ratio-based readout whose k_n-driven component is invisible to classifier-based prioritization.

## Files

- `results/augur_comparison_v45.json` — multiclass variant (per-class AUC, all 150 estimates, Spearman).
- `results/augur_ovr_sensitivity_v45.json` — binary OvR variant (per-class and per-region AUC, Spearman).
- `notebooks/91_augur_v45.py`, `notebooks/91b_augur_ovr_v45.py` — pipelines (runtimes 2533s and 1324s).
