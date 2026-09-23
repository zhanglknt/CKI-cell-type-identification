import sys

PATH = 'generate_manuscript_nc.py'
src = open(PATH, encoding='utf-8').read().splitlines()

REPL = [
    (r"""p('No real dataset provides pairs""",
     r"""p('No real dataset provides pairs with known functional divergence, so we built a semi-synthetic ground truth by injecting perturbations into a real background (Tabula Muris FACS marrow B cells; true pre-injection divergence zero; Methods). Under pure neutral housekeeping drift, raw JS and cosine exceeded their null thresholds in 55% and 58% of replicates, \u03c9 in none (2% under global overdispersion); detecting an injected functional module required strong signals (0 of 150 replicates at \u03b4 = 1, 13% at \u03b4 = 2), because per-pair top-200 selection saturates with noise even under the null (median baseline k_f = 0.025). \u03c9 is structurally blind to modules placed on HK genes (detection 0.000 at every \u03b4; k_n itself fired at 0.61\u20131.00), yet under expression-matched low-variance non-HK drift \u03c9 stayed at its calibrated false-positive rate (0.000\u20130.067) while raw JS and cosine inflated to 0.81\u20131.00 (Supplementary Notes 1, 5)\u2014the ratio cancels global compositional drift wherever it acts.')"""),
    (r"""p('\u03c9 best discriminated functional""",
     r"""p('\u03c9 best discriminated functional (\u03b4 \u2265 0.25) from neutral perturbations (Fig. 2e; AUC = 0.80 versus 0.72 k_f, 0.64 raw JS, 0.58 cosine, 0.21 k_n; 95% CI [0.777, 0.831]): the standard metrics\u2019 apparent power is purchased with false positives on neutral drift. The ratio also conferred robustness to technical asymmetry (fourfold cell-count imbalance: \u03c9 \u221232%, k_f +67%, cosine +108%). \u03c9 is thus a specificity-first screen, rejecting neutral drift at the cost of bounded power for weak-to-moderate signals (Supplementary Note 1).')"""),
    (r"""p('The design was repeated in a second""",
     r"""p('The design fully reproduced in a second background\u2014skin keratinocyte stem cells (1,371 cells; 1,750 replicates per background; Methods): AUC(\u03c9) = 0.908 versus AUC(k_f) = 0.859 (Fig. 2e). The power bound is background-dependent (skin k_f selection floor median 0.011 versus 0.025; at \u03b4 = 1, \u03c9 detection 0.91 versus 0.00 in marrow), and under fourfold imbalance k_f retained higher power (0.98\u20131.00 versus 0.04\u20130.20).')"""),
    (r"""p('The simulation\u2019s neutral-drift benchmark""",
     r"""p('We tested the same specificity on real technical replicates, calibrating each pair against a per-pair size-matched cell-shuffle null (B = 200; Methods). In the first batch of the IFN-\u03b2 PBMC dataset [14], the 30 same-donor, same-condition cross-lane pairs serve as clean technical replicates: \u03c9 was fully calibrated (0 of 30 above its null 95th percentile; median calibration ratio 0.963; k_f likewise 0 of 30), whereas raw JS misreported 36.7% and cosine 23.3% (Fig. 3d).')"""),
    (r"""p('The same design scales to the brain atlas""",
     r"""p('The design scales to the brain atlas (606 10x libraries) as a three-tier drift ladder of library-level pairs [12]: T1, same donor, region, and cell type (2,161 pairs); T2, different donors within a region (1,089); T3, different regions within a donor (1,656). On T1, \u03c9 misreported least among the continuous metrics (FPR 28.6% versus 45.2% raw JS, 44.1% cosine, 40.6% Spearman, 37.6% k_f; Fig. 3b, c); marker Jaccard was lower still (19.9%) but responded weakest to genuine regional divergence (T3 calibration ratio 1.41 versus 1.80 for \u03c9). At T2 \u03c9 again misreported least (90.9% versus 98.4\u201398.7%), and its calibration gradient across the ladder is the shallowest (1.04 \u2192 1.76 \u2192 1.80 versus 1.07 \u2192 3.32 \u2192 2.98 for raw JS).')"""),
    (r"""p('Two qualifications temper the brain result""",
     r"""p('Two qualifications temper the brain result. The absolute \u03c9 FPR is not zero and grows with group size (14.1% below 30 nuclei per library to 48.0% above 500; raw JS 28.6% to 72.5%), a library-level technical component the anchor absorbs only partially\u2014the 0-of-30 Kang outcome sits at the favorable end of this size dependence. A minority of classes show gene-specific library effects the anchor cannot absorb (choroid plexus median calibration 2.31; Bergmann glia 1.16). Neutral-drift immunity thus transfers to real data only as a relative-calibration advantage (Section 3.12).')"""),
    (r"""p('How \u03c9 behaves on a real perturbation""",
     r"""p('On a real perturbation whose effect on the housekeeping anchor is unknown\u2014PBMCs from eight donors, control versus 6-hour IFN-\u03b2 stimulation [14] (24,413 cells, six cell types; Methods)\u2014condition is fully confounded with lane, so we read the analysis as a relative architecture demonstration. The perturbation was visible at the \u03c9 level in all six cell types, but k_f alone separated perturbation from donor drift as well or better (rank AUC: \u03c9 0.55\u20130.92, k_f 0.74\u20131.00); in CD14+ monocytes \u03c9 fell to 0.55 while k_f retained 0.98, because stimulation raises housekeeping expression itself (median k_n 1.2\u20135.7-fold) and the inflating denominator partially cancels the functional signal (Supplementary Fig. 3; Supplementary Note 6).')"""),
    (r"""p('We benchmarked CKI against MELD""",
     r"""p('We benchmarked CKI against MELD (v1.0.2) and scDist (Python approximation of the R-only package) on the Kang IFN-\u03b2 dataset [14]. CKI and MELD agreed on effect direction in 6 of 6 cell types, but MELD\u2019s within-type separation was near-saturated (AUC 0.997\u20130.9998). In an additive mean-shift simulation, MELD and the scDist approximation detected every configuration (sensitivity 1.00), whereas CKI \u03c9 rose from AUC 0.52 to 0.79 as the shift grew on 100 genes but collapsed to 0.05\u20130.13 on 500 genes, where the anchor itself responds (k_n AUC = 1.000) and the ratio is annihilated by its denominator; users seeking maximal detection power for broad perturbations should use MELD, scDist, or CKI\u2019s own k_f component.')"""),
    (r"""p('The reference implementation first reproduced""",
     r"""p('The reference implementation first reproduced the reported landscape exactly (maximum per-pair |\u0394\u03c9| = 6.4 \u00d7 10\u207b\u00b9\u00b3 over 31,764 pairs). Non-circular panels left rankings essentially untouched (pair-level \u03c1 = 0.937 leave-pair-out, 0.918\u20130.931 other panels; class means \u03c1 = 0.90\u20130.99), and the astrocyte-to-Bergmann-glia gradient was preserved and amplified (6.10-fold reported; 6.53-fold leave-pair-out), with class-level significance largely robust under scheme-matched block-shuffle nulls (Supplementary Note 7). Circular selection inflated k_f by a median 1.61-fold versus leave-pair-out (grand mean \u03c9 38.55 reported; 26.5 leave-pair-out; 6.5 fixed), so absolute \u03c9 values are upper-bound, scheme-specific estimates: rank-based conclusions are robust, but the tier cutoffs (\u03c9 < 15/25/35) are calibrated to the reported scheme\u2019s inflated scale and do not transfer (Supplementary Note 7).')"""),
    (r"""p('The ablation also quantifies""",
     r""""""),
]

used = set()
for idx, (pre, new) in enumerate(REPL):
    hits = [i for i, l in enumerate(src) if l.strip().startswith(pre) and i not in used]
    if len(hits) != 1:
        print(f'FAIL[{idx}] matched {len(hits)}: {pre[:70]}')
        sys.exit(1)
    i = hits[0]
    used.add(i)
    ow = len(src[i].split()); nw = len(new.split())
    src[i] = new
    print(f'L{i+1}: {ow} -> {nw}')

open(PATH, 'w', encoding='utf-8').write('\n'.join(src) + '\n')
print('WROTE OK')
