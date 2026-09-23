"""v51 splice batch 8: candidate screen paragraphs [63]-[68]."""
import io

P = 'generate_manuscript_nc.py'
lines = io.open(P, encoding='utf-8').read().split('\n')

R = []
R.append((r"p('Low CKI \u03c9 for a cell type",
 r'''p('Low CKI \u03c9 for a cell type across two regions indicates transcriptomic similarity beyond baseline expectation, with non-exclusive candidate mechanisms (developmental origin heterogeneity, colonization-route boundaries [20\u201322], postnatal migration [23,24]). We report the screen\u2019s global verdict first: under a design-matched null that recomputes the full selection rule on every block-shuffle permutation, the expected number of Strong candidates is 148.3 across the full 31,764-pair pool\u2014the 39 observed lie 3.8-fold below the null expectation (P(null count \u2265 39) = 1.0), and no candidate survives FDR correction (minimum q = 0.520). The catalogue below is therefore a prioritized hypothesis list, not discoveries, and inherits the atlas\u2019s four-donor structure (region glossary in Supplementary Note 11).')'''))
R.append((r"p('The screen uses a multiplicative model",
 r'''p('The screen uses a multiplicative model, expected_\u03c9 = \u03bc_ct \u00d7 \u03bc_pair / \u03bc_grand (Methods): a residual (observed / expected) well below 1 marks a cell type far less differentiated between two regions than expected from its own plasticity and the pair\u2019s divergence. Three confidence tiers were defined: Strong (residual < 0.3, \u03c9 < 15, lowest \u03c9 in the region pair), Moderate (residual < 0.5, \u03c9 < 25), and Weak (residual < 0.75, \u03c9 < 35; Supplementary Fig. 8).')'''))
R.append((r"p(f'Among {_br",
 r'''p(f'Among {_br["total_pairs"]:,} comparisons, criteria identified {_br["n_strong"]} ({_br["pct_strong"]:.2f}%) Strong, {_br["n_moderate"]:,} ({_br["pct_moderate"]:.2f}%) Moderate, and {_br["n_weak"]:,} ({_br["pct_weak"]:.2f}%) Weak candidates (Supplementary Table 4). Under the block-shuffle null (B = 1,000; Supplementary Fig. 9), 31 Strong candidates showed raw P < 0.05 but none survived Benjamini-Hochberg correction (minimum q = 0.520); the only sub-nominal stratified family is intra-cerebellar Bergmann-glia (m = 21; minimum q = 0.042). Candidates concentrate in microglia (16 Strong) and oligodendrocytes (10), but the microglial enrichment does not survive the design-matched null (observed 16, fold 0.31, P = 0.990): we make no class-composition claim.')'''))
R.append((r"p('A negative control confirms",
 r'''p('A negative control confirms the null is calibrated by library-level, not regional, structure: libraries of every region were split at random into pseudo-regions and the identical test re-run on 127,756 pseudo-pairs (Supplementary Note 12; Supplementary Fig. 10)\u2014cross-region pseudo-pairs gave near-nominal tail rates, whereas same-region halves showed a 37.6% lower-tail rate, confirming retained power.')'''))
R.append((r"p('The catalogue converges on anatomically coherent themes",
 r'''p('The catalogue converges on anatomically coherent themes. Microglial candidates (16 of 39) converge on visual-relay and orbitofrontal dissections (five pairs involve the lateral geniculate nucleus; Supplementary Note 11). Mature-oligodendrocyte candidates (10, all raw P < 0.05) show a thalamo-temporal orientation that crosses rather than follows the dorsoventral origin boundary [25], so their mechanistic basis is left unassigned (Supplementary Note 13). Astrocytes, fibroblasts, and ependymal cells contributed sparse candidates [26,27]; Bergmann glia, vascular cells, and choroid plexus contributed none [26,28]. All are hypothesis-generating targets for spatial-transcriptomic and lineage follow-up [19], not discoveries.')'''))
R.append((r"p('In summary, the block-shuffle re-analysis",
 r'''p('In summary, the block-shuffle re-analysis substantially tempers the brain candidate catalogue: the cell-class-level gradient is supported for 4 of 10 classes (3 of 10 after correction), no individual candidate survives FDR correction (minimum q = 0.520), and the Strong rule itself is anti-enriched relative to its null (148.3 expected versus 39 observed). An earlier per-pair label-shuffle implementation was anti-conservative (36.3% of P-values at the floor) by ignoring the 10x-library block structure. We therefore position the entire candidate list as hypothesis-generating rather than discoveries.')'''))

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
print('batch 8 written')
