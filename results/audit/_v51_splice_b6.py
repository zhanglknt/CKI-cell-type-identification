"""v51 splice batch 6: cross-organ paragraphs [52]/[53] (f-string preserving)."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append((r"p(f'Of the {_h",
 r'''p(f'Of the {_h["n_pairs_total"]:,} Tabula Sapiens cell-type pairs, {DATA["cross_organ_n_total"]} are same-cell-type cross-organ comparisons, which ask which cell types maintain their identity regardless of residence and which are shaped by their organ environment (Fig. 5; Table 1; Supplementary Fig. 5). Anchoring on well-sampled cell types (n \u2265 5 pairs; upper block of Table 1): {t2[0][0]}s (mean \u03c9 = {t2[0][1]} \u00b1 {t2[0][2]}, n = {t2[0][3]}) and {t2[1][0]}s (mean \u03c9 = {t2[1][1]} \u00b1 {t2[1][2]}, n = {t2[1][3]}) were the most conserved, followed by {t2[2][0]}s and {t2_next[0]}s; {mac[0]}s (n = {mac[3]}) were intermediate. {last2[0][0]}s and {last2[1][0]}s were the most divergent, consistent with organ-specific endothelial gene programs [16], though both rest on n = 3 pairs; sparsely sampled types (n = 1\u20133 pairs) carry no reliable signal.')'''))
R.append((r"p(f'The cross-organ ranking showed little agreement",
 r'''p(f'The cross-organ ranking showed little agreement with rankings from standard metrics (Spearman r = {f'{min(DATA["cross_organ_spearman"].values()):.2f}'.replace('-', '\u2212')} to {f'{max(DATA["cross_organ_spearman"].values()):.2f}'.replace('-', '\u2212')}, n = {DATA["cross_organ_n_total"]} pairs; Supplementary Table 2), because CKI explicitly normalizes. A k_f-only control qualifies the interpretation (Supplementary Note 9): per-cell-type mean \u03c9 and mean k_f are only weakly concordant (r = 0.23, 95% CI [\u22120.08, 0.38], n = 17 cell types), and while the extremes reproduce, the middle does not. The cross-organ ranking is thus a composite of functional divergence and baseline differences; because the k_n anchor is not calibrated across cell types (Discussion), cross-type gaps in mean \u03c9 should be read as descriptive rather than calibrated differences.')'''))

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
print('batch 6 written')
