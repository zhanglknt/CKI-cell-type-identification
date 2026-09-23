"""v51 splice batch 3: simulation + real-drift paragraphs."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append(("p('No real dataset provides",
 r"p('No real dataset provides pairs with known functional divergence, so we built a semi-synthetic ground truth by injecting known perturbations into a real background (Tabula Muris FACS marrow B cells; true pre-injection divergence zero; Methods). Under pure neutral housekeeping drift, raw JS and cosine exceeded their null thresholds in 55% and 58% of replicates, whereas \u03c9 produced none. Conversely, detecting an injected functional module required strong signals (\u03c9 detected none of 150 replicates at \u03b4 = 1, 13% at \u03b4 = 2): per-pair top-200 selection saturates with noise even under the null, so weak shifts do not lift k_f above the selection floor. Two adversarial scenarios quantify the boundary (Supplementary Notes 1, 5): \u03c9 is structurally blind to modules placed on HK genes, yet under expression-matched low-variance non-HK drift \u03c9 stayed at its calibrated false-positive rate while raw JS and cosine inflated to 0.81\u20131.00\u2014the ratio cancels global compositional drift wherever it acts, so its specificity is not an HK-anchoring artifact.')"))
R.append(("p('\u03c9 best discriminated functional",
 r"p('\u03c9 best discriminated functional (\u03b4 \u2265 0.25) from neutral perturbations (Fig. 2e; AUC = 0.80 versus 0.72 k_f, 0.64 raw JS, 0.58 cosine, 0.21 k_n; 95% CI [0.777, 0.831]): the apparent power of the standard metrics is purchased with false positives on neutral drift. The ratio also conferred robustness to technical asymmetry (cell-count imbalance, dropout, depth differences; Supplementary Note 1). \u03c9 is thus a specificity-first screen: its construction rejects neutral drift at the cost of bounded power for weak-to-moderate signals.')"))
R.append(("p('The design was repeated",
 r"p('The design fully reproduced in a second Tabula Muris FACS background\u2014skin keratinocyte stem cells (1,750 replicates; Methods): AUC(\u03c9) = 0.908 versus AUC(k_f) = 0.859 (Fig. 2e), with background-dependent power bounds and higher k_f power under cell-count imbalance\u2014the flip side of the ratio\u2019s neutral-drift immunity (per-scenario values in Supplementary Note 1).')"))
R.append(("p('The simulation\u2019s neutral-drift benchmark",
 r"p('The simulation\u2019s neutral-drift benchmark concerns synthetic drift; we therefore tested the same specificity on real technical replicates, calibrating each pair against a per-pair size-matched cell-shuffle null (B = 200 per pair; Methods). In the first batch of the IFN-\u03b2 PBMC dataset [14]\u2014the 30 same-donor, same-condition cross-lane pairs provide clean technical replicates: \u03c9 was fully calibrated (0 of 30 pairs above its own null 95th percentile; median calibration ratio 0.963; k_f alone likewise 0 of 30), whereas raw JS misreported 36.7% of pairs and cosine 23.3% as divergence (Fig. 3d).')"))
R.append(("p('The same design scales",
 r"p('The same design scales to the brain atlas (606 10x libraries): a three-tier drift ladder of library-level pairs\u2014T1, same donor, region, and cell type (pure technical drift; 2,161 pairs); T2, different donors within a region (1,089 pairs); T3, different regions within a donor (regional biology, positive control; 1,656 pairs) [12]. On T1, \u03c9 had the lowest misreporting rate among the continuous divergence metrics (FPR 28.6% versus 45.2% raw JS, 44.1% cosine, 40.6% Spearman, 37.6% k_f; Fig. 3b, c); marker Jaccard distance was lower still (19.9%) but responded weakest to genuine regional divergence (T3 calibration ratio 1.41 versus 1.80 for \u03c9 and 2.98 for raw JS) and offers no k_n/k_f decomposition. At T2 \u03c9 again misreported least among the continuous metrics (90.9% versus 98.4\u201398.7%); across the ladder the \u03c9 calibration gradient is the shallowest of all metrics (1.04 \u2192 1.76 \u2192 1.80, versus 1.07 \u2192 3.32 \u2192 2.98 for raw JS), so \u03c9 best separates technical drift from biology in relative terms.')"))
R.append(("p('Two qualifications temper the brain result",
 r"p('Two qualifications temper the brain result. First, the absolute \u03c9 FPR is not zero and grows with group size (14.1% below 30 nuclei per library to 48.0% above 500; raw JS 28.6% to 72.5%)\u2014the 0-of-30 PBMC outcome sits at the favorable end of this size dependence. Second, a minority of classes show gene-specific library effects the anchor cannot absorb (choroid plexus median calibration 2.31; Bergmann glia 1.16). Absolute neutral-drift immunity thus transfers to real data only as a relative-calibration advantage (Section 3.12 of the Supplementary Information).')"))

nfail = 0
for prefix, newline in R:
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(idx) != 1:
        print('FAIL prefix not unique:', prefix[:60], len(idx)); nfail += 1; continue
    old = lines[idx[0]]
    lines[idx[0]] = newline
    print(f'OK L{idx[0]+1}: {len(old.split())} -> {len(newline.split())}')
if nfail:
    raise SystemExit(1)
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('batch 3 written')
