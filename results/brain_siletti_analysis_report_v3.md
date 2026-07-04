# CKI Brain Analysis Report (v3 - Efficient)

**CKI version**: 0.2.0  
**HK genes**: HRT Atlas v1.0 (1115 genes)  
**Date**: 2026-07-04 09:56

**Strategy**: Pseudobulk-only normalization (NO full-matrix normalize_total)  

## Per-Cell-Type Omega Summary
| Cell Type | Nuclei | Regions | Pairs | Omega Mean | Omega Std | Omega Min | Omega Max |
|---|---|---|---|---|---|---|---|
| Bergmann glia | 7,965 | 7 | 21 | 2.37 | 1.14 | 1.24 | 6.29 |
| Committed oligodendrocyte precursor | 4,118 | 52 | 1326 | 3.17 | 1.47 | 1.35 | 11.04 |
| Vascular | 9,586 | 82 | 3321 | 3.4 | 1.24 | 1.57 | 11.24 |
| Fibroblast | 8,897 | 83 | 3403 | 3.99 | 1.9 | 1.68 | 22.14 |
| Ependymal | 5,779 | 40 | 780 | 4.13 | 1.73 | 1.63 | 14.67 |
| Choroid plexus | 7,643 | 6 | 15 | 4.8 | 1.45 | 2.91 | 7.7 |
| Oligodendrocyte precursor | 105,723 | 107 | 5671 | 7.65 | 4.03 | 1.57 | 32.55 |
| Microglia | 91,826 | 107 | 5671 | 8.02 | 4.93 | 1.53 | 79.41 |
| Oligodendrocyte | 490,246 | 108 | 5778 | 8.66 | 4.44 | 1.76 | 42.02 |
| Astrocyte | 155,025 | 108 | 5778 | 14.36 | 8.68 | 1.63 | 68.79 |

## Omega Gradient
- Lowest: Bergmann glia (mean=2.37)
- Highest: Astrocyte (mean=14.36)
- Fold change: 6.06x

## Full Omega Gradient (low to high)
- Bergmann glia: 2.37 [======]
- Committed oligodendrocyte precursor: 3.17 [========]
- Vascular: 3.4 [=========]
- Fibroblast: 3.99 [===========]
- Ependymal: 4.13 [===========]
- Choroid plexus: 4.8 [=============]
- Oligodendrocyte precursor: 7.65 [=====================]
- Microglia: 8.02 [======================]
- Oligodendrocyte: 8.66 [========================]
- Astrocyte: 14.36 [========================================]

## Migration Candidates
- Total pairs: 31764
- Strong (residual < 0.3): 30 (0.09%)
- Moderate (residual < 0.5): 1247 (3.93%)
- Weak (residual < 0.75): 6567 (20.67%)

### Strong Candidates by Cell Type
| Cell Type | Strong Count |
|---|---|
| Astrocyte | 6 |
| Bergmann glia | 0 |
| Choroid plexus | 0 |
| Committed oligodendrocyte precursor | 0 |
| Ependymal | 0 |
| Fibroblast | 1 |
| Microglia | 10 |
| Oligodendrocyte | 10 |
| Oligodendrocyte precursor | 0 |
| Vascular | 3 |

### Top 20 Strong Candidates
| Cell Type | Region A | Region B | Omega | Expected | Residual |
|---|---|---|---|---|---|
| Astrocyte | Human VLN | Human VPL | 2.51 | 12.42 | 0.2021 |
| Oligodendrocyte | Human A19 | Human Pul | 3.71 | 15.67 | 0.2369 |
| Oligodendrocyte | Human A32 | Human Pul | 4.68 | 19.50 | 0.2398 |
| Microglia | Human DTg | Human TF | 3.36 | 13.61 | 0.2465 |
| Oligodendrocyte | Human MoRF-MoEN | Human PnRF | 2.52 | 10.13 | 0.2488 |
| Astrocyte | Human Pul | Human VPL | 2.60 | 10.41 | 0.2499 |
| Microglia | Human IC | Human TF | 3.89 | 15.31 | 0.2540 |
| Microglia | Human A29-A30 | Human MoRF-MoEN | 2.89 | 11.02 | 0.2620 |
| Microglia | Human A29-A30 | Human DTg | 2.53 | 9.51 | 0.2664 |
| Microglia | Human A29-A30 | Human PnEN | 2.59 | 9.63 | 0.2689 |
| Vascular | Human ITG | Human PnRF | 2.06 | 7.62 | 0.2708 |
| Microglia | Human A14 | Human IC | 3.89 | 14.27 | 0.2728 |
| Astrocyte | Human CBL | Human CBV | 2.28 | 8.32 | 0.2735 |
| Oligodendrocyte | Human LP | Human TF | 3.31 | 11.96 | 0.2765 |
| Astrocyte | Human CA2U-CA3U | Human DGU-CA4Upy | 7.38 | 26.45 | 0.2790 |
| Oligodendrocyte | Human A14 | Human Pul | 3.52 | 12.58 | 0.2802 |
| Oligodendrocyte | Human A40 | Human Pul | 3.66 | 12.98 | 0.2823 |
| Oligodendrocyte | Human A19 | Human LP | 3.34 | 11.82 | 0.2825 |
| Vascular | Human ITG | Human PB | 1.90 | 6.68 | 0.2852 |
| Oligodendrocyte | Human A13 | Human Pul | 4.71 | 16.45 | 0.2866 |
