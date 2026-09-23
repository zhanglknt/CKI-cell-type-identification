"""v51 splice batch 4: IFN-beta / MELD / fixed-panel."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append((r"p('How \u03c9 behaves on a real perturbation",
 r"p('How \u03c9 behaves on a real perturbation whose effect on the housekeeping anchor is unknown was tested on PBMCs from eight donors, control versus 6-hour IFN-\u03b2 stimulation [14] (24,413 cells, six cell types; Methods). Because the two conditions were captured in separate 10x lanes, condition is fully confounded with lane for every metric; we read the analysis as a relative architecture demonstration, not an absolute detection claim. The perturbation was visible at the \u03c9 level in all six cell types, but k_f alone separated perturbation from donor drift as well or better (rank AUC: \u03c9 0.55\u20130.92, k_f 0.74\u20131.00); in CD14+ monocytes \u03c9 AUC fell to 0.55 while k_f retained 0.98\u2014stimulation raises housekeeping expression itself (median k_n rises 1.2\u20135.7-fold), so the denominator inflates and partially cancels the functional signal. The demonstration thus supports, within a lane-confounded design, the anchor-visibility boundary, while \u03c9 tracks real perturbation above donor drift when the anchor is unaffected (Supplementary Fig. 3; Supplementary Note 6).')"))
R.append((r"p('We benchmarked CKI against MELD",
 r"p('We benchmarked CKI against MELD (v1.0.2) and scDist on the Kang IFN-\u03b2 dataset [14] (using a Python approximation of the R-only scDist, labelled as such throughout). CKI and MELD agreed on effect direction in 6 of 6 cell types, but MELD\u2019s within-type separation was near-saturated (AUC 0.997\u20130.9998). In an additive mean-shift simulation, MELD and the scDist approximation detected every configuration (sensitivity 1.00), whereas CKI \u03c9 rose from AUC 0.52 to 0.79 as the shift grew on 100 genes but collapsed to 0.05\u20130.13 on 500 genes\u2014at 500 shifted genes the anchor k_n itself responds (k_n AUC = 1.000) and the ratio is annihilated by its denominator. \u03c9 therefore measures divergence in excess of the anchor and is, by design, insensitive to perturbations that move the anchor itself; users seeking maximal detection power for broad perturbations should use MELD, scDist, or CKI\u2019s own k_f component (donor-paired power bounds the operating window at ~50\u2013200 cells; Discussion).')"))
R.append((r"p('The reference implementation first reproduced",
 r"p('The reference implementation first reproduced the reported landscape exactly (maximum per-pair |\u0394\u03c9| = 6.4 \u00d7 10\u207b\u00b9\u00b3 over all 31,764 pairs). Non-circular panels left rankings essentially untouched: pair-level \u03c9 under leave-pair-out correlated with the reported scheme at \u03c1 = 0.937 (0.918\u20130.931 across the other two panels), and the ten class means at \u03c1 = 0.90\u20130.99. The astrocyte-to-Bergmann-glia gradient was preserved and, under leave-pair-out, amplified (6.10-fold reported; 6.53-fold leave-pair-out), and class-level significance was largely robust under scheme-matched block-shuffle nulls (Supplementary Note 7).')"))
R.append((r"p('The ablation also quantifies",
 r"p('The ablation also quantifies what circular selection costs: the circular panel inflated k_f by a median of 1.61-fold relative to the leave-pair-out panel, so reported absolute \u03c9 values are upper-bound, scheme-specific estimates (grand mean 38.55 reported; 26.5 leave-pair-out; 6.5 fixed; full panel comparison in Supplementary Note 7). Rank-based conclusions are robust, but absolute thresholds do not transfer: the tier cutoffs (\u03c9 < 15/25/35) are calibrated to the reported scheme\u2019s inflated scale (Supplementary Note 7).')"))

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
print('batch 4 written')
