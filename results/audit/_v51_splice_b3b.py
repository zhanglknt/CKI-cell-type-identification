"""v51 splice batch 3b: fix prefixes + real compression of [36]/[37]."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append((r"p('The simulation\u2019s neutral-drift benchmark",
 r"p('The simulation\u2019s neutral-drift benchmark concerns synthetic drift; we therefore tested the same specificity on real technical replicates, calibrating each pair against a per-pair size-matched cell-shuffle null (B = 200 per pair; Methods). In the first batch of the IFN-\u03b2 PBMC dataset [14], the 30 same-donor, same-condition cross-lane pairs provide clean technical replicates: \u03c9 was fully calibrated (0 of 30 pairs above its own null 95th percentile; median calibration ratio 0.963; k_f alone likewise 0 of 30), whereas raw JS misreported 36.7% of pairs and cosine 23.3% as divergence (Fig. 3d).')"))
R.append((r"p('The same design scales",
 r"p('The same design scales to the brain atlas (606 10x libraries) as a three-tier drift ladder of library-level pairs\u2014T1, same donor, region, and cell type (2,161 pairs); T2, different donors within a region (1,089 pairs); T3, different regions within a donor (1,656 pairs) [12]. On T1, \u03c9 had the lowest misreporting rate among the continuous divergence metrics (FPR 28.6% versus 45.2% raw JS, 44.1% cosine, 40.6% Spearman, 37.6% k_f; Fig. 3b, c); marker Jaccard distance was lower still (19.9%) but responded weakest to genuine regional divergence (T3 calibration ratio 1.41 versus 1.80 for \u03c9) and offers no k_n/k_f decomposition. At T2 \u03c9 again misreported least among the continuous metrics (90.9% versus 98.4\u201398.7%), and across the ladder its calibration gradient is the shallowest of all metrics (1.04 \u2192 1.76 \u2192 1.80 versus 1.07 \u2192 3.32 \u2192 2.98 for raw JS).')"))

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
print('batch 3b written')
