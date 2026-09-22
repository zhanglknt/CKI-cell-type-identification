# v50 Phase B batch 5: Screen section (merge L576-580 into one, blank L578/L580)
P = r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_nc.py"
src = open(P, encoding="utf-8").read().split("\n")

REPL = {}

REPL[568] = (r"p('Low CKI \u03c9 for a cell type",
r"""p('Low CKI \u03c9 for a cell type across two regions indicates transcriptomic similarity beyond baseline expectation, arising from non-exclusive mechanisms (developmental origin heterogeneity, embryonic colonization route boundaries [20-22], postnatal migration [23,24]). We report the screen\u2019s global verdict first: under a design-matched null that recomputes the full selection rule on every block-shuffle permutation, the expected number of Strong candidates is 148.3 across the full 31,764-pair pool\u2014the 39 observed lie 3.8-fold below the null expectation (P(null count \u2265 39) = 1.0), and no candidate survives FDR correction (minimum q = 0.520). The catalogue below is therefore a prioritized hypothesis list, not discoveries; it also inherits the atlas\u2019s donor structure (four donors; 94.5% of region pairs share at least one), leaving pair-level nominations subject to donor confounding. Region abbreviations follow the Siletti et al. dissection nomenclature (glossary in Supplementary Note 11).')""")

REPL[572] = (r"p(f'Among {_br",
r"""p(f'Among {_br["total_pairs"]:,} cross-region comparisons, threshold criteria identified {_br["n_strong"]} ({_br["pct_strong"]:.2f}%) Strong candidates, with {_br["n_moderate"]:,} ({_br["pct_moderate"]:.2f}%) Moderate and {_br["n_weak"]:,} ({_br["pct_weak"]:.2f}%) Weak (Supplementary Table 4). Under the block-shuffle null (B = 1,000; Supplementary Fig. 9), 31 of the 39 Strong candidates showed raw one-sided P < 0.05, but none survived Benjamini-Hochberg correction (minimum q = 0.520); a cell-type-stratified sensitivity analysis yields a single sub-nominal family\u2014the intra-cerebellar Bergmann-glia family (m = 21; minimum q = 0.042)\u2014crossing no class boundaries. Candidates concentrate in microglia (16 Strong) and oligodendrocytes (10), but the microglial share-level enrichment (2.30-fold) does not survive the design-matched null: the Strong rule fires preferentially on low-\u03c9 classes (52.0 of the 148.3 null candidates are microglial; observed 16, fold 0.31, P = 0.990). We make no class-composition claim, consistent with the class-level test (microglial mean below null, P = 0.904).')""")

REPL[574] = (r"p('A design-matched negative control confirms",
r"""p('A design-matched negative control confirms the block-shuffle null is calibrated by library-level, not regional, structure: the libraries of every region were split uniformly at random into two pseudo-regions and the identical test re-run on the resulting 127,756 pseudo-pairs (B = 1,000; Supplementary Note 12; Supplementary Fig. 10). Pseudo-pairs between halves of different regions gave near-nominal tail rates (5.79% lower, 6.87% upper, versus 6.17% and 7.90% in the real analysis), whereas same-region halves showed a 37.6% lower-tail rate, confirming retained power; the small excess of real over pseudo rates is the marginal signature of true regional biology.')""")

REPL[576] = (r"p('Microglia contributed the largest share",
r"""p('The candidate catalogue converges on anatomically coherent themes. Microglia contributed the largest share (16 of 39, 13 with raw P < 0.05), converging on visual-relay and orbitofrontal dissections (five pairs involve the lateral geniculate nucleus, four the pulvinar, four the occipitotemporal area TF, with orbitofrontal areas A13 and A14 recurring; Supplementary Note 11). Mature oligodendrocytes contributed 10 candidates, all with raw P < 0.05, six with a thalamic relay-nucleus endpoint\u2014a thalamo-temporal orientation tested post hoc under two null references (Discussion; Supplementary Note 13)\u2014that cross rather than follow the dorsoventral origin boundary of oligodendrocyte development [25], so their mechanistic basis is left unassigned. Astrocytes, fibroblasts, and ependymal cells contributed sparse candidates compatible with published developmental mechanisms [26,28]; Bergmann glia, vascular cells, and choroid plexus contributed none. None of these signals survives multiple-testing correction; they are catalogued as hypothesis-generating targets for spatial-transcriptomic and lineage follow-up [19], not discoveries.')""")

REPL[578] = (r"p('Mature oligodendrocytes contributed 10 Strong candidates", r"""""")
REPL[580] = (r"p('Astrocytes, the most regionally divergent class", r"""""")
# blank lines: replace with empty string (paragraph removed)
REPL[578] = (REPL[578][0], "")
REPL[580] = (REPL[580][0], "")

REPL[582] = (r"p('In summary, the block-shuffle re-analysis",
r"""p('In summary, the block-shuffle re-analysis substantially tempers the brain candidate catalogue: the cell-class-level gradient is supported for 4 of 10 classes (3 of 10 after Benjamini-Hochberg correction), no individual candidate survives FDR correction (minimum q = 0.520), and the Strong rule itself is anti-enriched relative to its null (148.3 expected versus 39 observed). An earlier per-pair label-shuffle implementation produced anti-conservative P-values (36.3% at the floor) by ignoring the 10x-library block structure that the block-shuffle null preserves. We therefore position the entire candidate list as hypothesis-generating, prioritized for lineage-tracing and spatial-transcriptomic validation rather than presented as discoveries.')""")

for ln, (prefix, new) in REPL.items():
    cur = src[ln - 1]
    assert cur.startswith(prefix), f"line {ln} prefix mismatch: {cur[:80]!r}"
    src[ln - 1] = new
    print(f"line {ln}: {len(cur)} -> {len(new)} ch")

open(P, "w", encoding="utf-8", newline="\n").write("\n".join(src))
print("OK batch5")
