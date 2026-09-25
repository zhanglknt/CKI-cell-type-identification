# Non-HK-anchored neutral drift control simulation (v45, Analysis C)

Responds to v44 blind-review r-computational P1-1: the original ground-truth simulation defines neutral drift as a 2^eta shift on housekeeping genes -- the same gene set omega uses as its denominator (k_n). The headline 'omega FPR=0.00 vs raw JS/cosine 0.55-0.58' could therefore be a construction artifact. This analysis tests whether omega's specificity survives NON-HK-anchored neutral drift definitions on the identical background and scheme.

## Design

- Background: Tabula Muris FACS Marrow, B cell (1848 cells); kept gene set 6064 (HK=1064, non-HK top-5000 by mean), pseudobulk /1e4+log1p, per-pair top-200 |A-B| k_f -- all identical to script 45.
- Thresholds: 95th percentile of 200 pure-resampling baseline replicates, per metric (identical calibration).
- Replicates: 30 per condition; FPR with 95% Clopper-Pearson CIs.
- **N0 (internal control)**: original HK drift, 2^eta x HK genes on group A, eta in {0.25, 0.5, 1.0}.
- **N1**: random low-variance non-HK gene set (bottom-half CV; greedy log-mean matched to the HK set; same size n=1064; 3 random sets) shifted by 2^eta on group A -- same amplitude, same scheme, different anchor.
- **N2**: composition-preserving drift -- random gene-pair swap of non-HK expression profiles within group A (266/532/1064 swapped genes = 0.25x/0.5x/1x n_hk; 3 random pairings). Per-cell library size and the multiset of gene expression vectors are exactly preserved; only gene identity is reassigned, with no functional directionality.

## Results

Pooled FPR (threshold = baseline 95th percentile; 95% Clopper-Pearson CI):

| Scenario | level | omega | raw JS (k_total) | cosine |
|---|---|---|---|---|
| N0 HK drift (control) | eta=0.25 | 0.000 [0.000-0.116] | 0.067 [0.008-0.221] | 0.100 [0.021-0.265] |
| N0 HK drift (control) | eta=0.5 | 0.000 [0.000-0.116] | 0.600 [0.406-0.773] | 0.700 [0.506-0.853] |
| N0 HK drift (control) | eta=1.0 | 0.000 [0.000-0.116] | 1.000 [0.884-1.000] | 1.000 [0.884-1.000] |
| N1 low-var non-HK drift | eta=0.25 | 0.067 [0.025-0.140] | 0.067 [0.025-0.140] | 0.089 [0.039-0.168] |
| N1 low-var non-HK drift | eta=0.5 | 0.011 [0.000-0.060] | 0.811 [0.715-0.886] | 0.878 [0.792-0.937] |
| N1 low-var non-HK drift | eta=1.0 | 0.000 [0.000-0.040] | 1.000 [0.960-1.000] | 1.000 [0.960-1.000] |
| N2 composition-preserving swap | 0.25x n_hk | 1.000 [0.960-1.000] | 1.000 [0.960-1.000] | 1.000 [0.960-1.000] |
| N2 composition-preserving swap | 0.5x n_hk | 1.000 [0.960-1.000] | 1.000 [0.960-1.000] | 1.000 [0.960-1.000] |
| N2 composition-preserving swap | 1.0x n_hk | 1.000 [0.960-1.000] | 1.000 [0.960-1.000] | 1.000 [0.960-1.000] |

N0 pooled (all eta): omega 0.000 [0.000-0.040], raw JS 0.556 [0.447-0.660], cosine 0.600 [0.491-0.702].
Reference (original script-45 run, neutral HK drift, all eta pooled): omega FPR=0.000, raw JS=0.553, cosine=0.580 (this run's thresholds: omega=20.813, k_total=0.00357, cosine=0.01461).

## Interpretation

The two non-HK-anchored neutral models give DIFFERENT answers, and both are informative:

- **N1 (multiplicative drift moved off HK genes): omega stays calibrated.** FPR(omega) = 0.067 at eta=0.25, 0.011 at eta=0.5, 0.000 at eta=1.0, versus FPR(raw JS) = 0.067, 0.811, 1.000 at the same amplitudes. The specificity advantage of omega therefore does NOT depend on the drift landing on housekeeping genes: multiplicative drift on 1,064 random expression-matched non-HK genes inflates group A's library, and the /1e4 renormalization propagates a uniform compositional scaling into the HK genes, which k_n absorbs. omega's specificity comes from its ratio structure, which cancels global multiplicative/compositional drift wherever it acts -- not from the drift being HK-anchored by construction.
- **N2 (composition-preserving gene-identity swap): no gene-aware metric retains specificity.** FPR = 1.000 for omega AND for raw JS AND for cosine at every swap size. A gene-pair swap preserves library size and the expression-value multiset exactly, so k_n sees no compositional signal while the swapped genes dominate the top-|A-B| set and k_f fires. Note, however, that whether N2 counts as 'neutral' is debatable: reassigning which gene carries which expression level is precisely a gene-identity-specific (i.e., potentially functional) change, and omega is designed to detect exactly that. Under N2 omega behaves no worse than -- and identically to -- anchor-free global metrics.
- Internal control N0 reproduces the original simulation (omega FPR=0.000, raw JS=0.556, cosine=0.600; cf. script 45: 0.000 / 0.553 / 0.580), confirming scheme identity.

**Bottom line:** the reviewer's concern is partially answered in omega's favour (N1: specificity is not an HK-anchoring artifact for multiplicative/compositional neutral drift) and partially upheld (N2: omega has no specificity advantage when the neutral model reassigns gene identity -- but no gene-aware metric does, and such rearrangement arguably is functional divergence). The abstract's 'FPR=0.00' claim should state the neutral model explicitly.

## Suggested manuscript wording

> "The low false-positive rate of omega under neutral drift is not an artifact of anchoring the neutral model on housekeeping genes. When the same 2^eta multiplicative drift is instead applied to a random, expression-matched low-variance non-HK gene set (N1), omega remains at its calibrated false-positive rate (0.000-0.067 across eta), whereas raw JS and cosine inflate to 0.81-1.00; the ratio structure of omega cancels global compositional drift wherever it acts. Under a stronger neutral model that reassigns gene identity while exactly preserving library size and composition (N2, gene-pair swap), omega, raw JS and cosine all flag every replicate (FPR=1.00): no gene-aware metric can treat identity reassignment as neutral, and we argue it should not be treated as such. The FPR=0.00 figure thus pertains to compositional/multiplicative neutral drift, whether HK- or non-HK-anchored (SN 3.13, notebooks/90_nonhk_drift_v45.py)."
