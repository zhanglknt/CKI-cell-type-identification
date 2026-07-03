# CKI Phase 3.2 Report: Multi-component k_f Calibration

## Date: 2026-07-03 12:02

## Method
```
k_f = w1 * Delta_identity + w2 * Delta_pathway
omega = k_f / k_n
```
- **Delta_identity**: JS divergence of HVG expression
- **Delta_pathway**: JS divergence of ssGSEA pathway enrichment scores
- **Pathway database**: Pseudo-pathways (HVG partitions, 20 modules)

## Dataset
- **CT entries**: 38
- **Total pairs**: 703
- **Gene space (post-QC)**: 22308 genes

## Weight Sweep Results

| w1 | w2 | AUC | Effect_Sep | omega_mean | omega_median |
|----|----|-----|------------|------------|---------------|
| 1.0 | 0.0 | 0.847 | 2.11 | 7.62 | 6.91 |
| 0.8 | 0.2 | 0.837 | 2.02 | 6.32 | 5.76 |
| 0.5 | 0.5 | 0.801 | 1.84 | 4.37 | 3.98 |
| 0.2 | 0.8 | 0.697 | 1.48 | 2.41 | 2.23 |
| 0.0 | 1.0 | 0.484 | 0.98 | 1.11 | 0.99 |

## Conclusion
- **Best weight**: identity_only (AUC=0.847, effect_sep=2.11)
- **Category separation** (diff_CT / same_CT mean omega): 2.11

Delta_identity alone is sufficient; Delta_pathway does not improve.

## Files Generated
- `phase32_pathway_scores.csv`
- `phase32_sweep_results.csv`
- `phase32_heatmap_comparison.png`
- `phase32_category_comparison.png`
- `phase32_sweep_barplot.png`

## Next Steps
- Phase 3.3: Tabula Sapiens cross-species validation
- Phase 3.4: TCGA tumor perturbation
- Phase 3.5: Method comparison (SAMap / SATURN / CACIMAR)