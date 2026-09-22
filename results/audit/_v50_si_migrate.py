# v50: insert migrated-detail paragraphs into SI generator (bottom-to-top line inserts)
P = r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks\68_gen_supplementary_nc.py"
src = open(P, encoding="utf-8").read().split("\n")

NOTE13 = """add_para(
    'Microglia composition null (migrated from the main text in v50). The '
    'microglial share-level enrichment among Strong candidates (16 of 39; raw '
    'share-level 2.30-fold, hypergeometric P = 6.0 \\u00d7 10\\u207b\\u2074) does '
    'not survive the design-matched null: the Strong rule fires preferentially on '
    'low-\\u03c9 classes, so 52.0 of the 148.3 null-rule candidates are microglial '
    '(observed 16, fold 0.31, P = 0.990), and the concentration does not survive '
    'the leave-pair-out panel.'
)"""

NOTE10 = """add_para(
    'Span-matched and equal-n decomposition controls (migrated from the main text '
    'in v50). Restricting astrocytes to the 21 intra-cerebellar region pairs that '
    'define Bergmann glia yields a span-matched gradient of 3.68 (ratio of class '
    'means; paired per-region-pair median 4.30, bootstrap 95% CI [3.40, 4.95]; '
    'notebooks/95_brain_region_matched_v49.py), so the gradient persists, at '
    'reduced magnitude, after size and span controls. Decomposing the equal-n '
    'residual: the astrocyte/Bergmann-glia k_f ratio is 2.09 (95% CI [2.02, 2.18]) '
    'under equal-n\\u2014essentially the full-data value (2.03)\\u2014whereas the k_n '
    'ratio reverses direction (equal-n 1.29, 95% CI [1.21, 1.41], astrocyte '
    'higher; full-data 0.31, Bergmann glia higher), so the Bergmann-glia k_n '
    'elevation in the full data is largely a class-size artefact '
    '(notebooks/96_brain_downsample_decomp_v49.py). Ordering controls: the '
    'k_f-only gradient is 4.1-fold and the k_n-only gradient 6.7-fold; the '
    'class-mean ordering is stable under an aggregate-first k_n estimator '
    '(Spearman \\u03c1 = 0.988, gradient 6.51-fold) but not under a single global '
    'k_n (\\u03c1 = 0.09).'
)"""

S313 = """add_para(
    'Additional driver-stratification controls (migrated from the main text in '
    'v50). The admixture-adjusted KRAS\\u2013wild-type differences were significant '
    'for both components (\\u0394\\u03c9 +16.8, P = 4.0 \\u00d7 10\\u207b\\u2076; '
    '\\u0394k_f +0.012, P = 0.009; \\u0394k_n \\u22120.0004, P = 0.003; adjusted '
    'log-\\u03c9 ratio 1.19, bootstrap 95% CI [1.12, 1.26]). KRAS-mutant tumors '
    'were strongly enriched for ever-smokers (94% versus 63% EGFR-mutant and 86% '
    'wild-type, \\u03c7\\u00b2 = 30.3, P = 2.7 \\u00d7 10\\u207b\\u2077); '
    'smoking-adjusted contrasts remained significant (\\u0394\\u03c9 +13.9, '
    'P = 5.9 \\u00d7 10\\u207b\\u2074 smoking alone; +13.6, P = 3.3 \\u00d7 '
    '10\\u207b\\u2074 with admixture; +13.3, P = 1.4 \\u00d7 10\\u207b\\u00b3 '
    'with smoking, age, and sex; smoking status covered 427 of 492 tumors, 87%). '
    'KRAS-mutant LUAD also differs from wild-type in TP53 co-mutation rate and '
    'histological subtype (invasive mucinous adenocarcinoma is KRAS-enriched); '
    'neither was adjusted for. Excluding the 32 cell-line-derived (CC) LIHC '
    'samples leaves the LIHC null result and the high-purity-half analysis '
    'unchanged (NN/TT 1.11 [0.93, 1.30]; high-purity-half 1.17 versus 1.19 '
    'excluding CC, 95% CI [1.01, 1.44]); the full barcode source-code audit is '
    'documented in the Reproducibility Guide '
    '(notebooks/94_cc_audit_sensitivity_v49.py).'
)"""

S310 = """add_para(
    'Leave-one-population-out sensitivity. Removing each control population in '
    'turn moves the 50-split baseline within 6.75\\u20138.08 '
    '(median-of-population-means 7.12); removing hepatocyte lowers it to 6.75 '
    '(\\u221212.3%). All ratio statements are baseline-invariant, but absolute '
    '\\u03c9_cal magnitudes shift by up to 14% under the outlier-free baseline '
    '(Bergmann glia \\u03c9_cal 1.76 \\u2192 2.01; astrocytes 10.75 \\u2192 12.26).'
)"""

# bottom-to-top inserts: (line_number_to_insert_before, expected_next_line_prefix, text)
INSERTS = [
    (2407, "add_heading('Supplementary Note 14", NOTE13),
    (2237, "add_heading('Supplementary Note 11", NOTE10),
    (1464, "doc.add_page_break()", S313),
    (836, "add_para('3.11 Competitor Benchmark", S310),
]
for ln, prefix, text in INSERTS:
    cur = src[ln - 1]
    assert cur.strip().startswith(prefix), f"line {ln}: {cur[:80]!r}"
    src.insert(ln - 1, text)
    src.insert(ln - 1, "")
    print("inserted before line", ln, "->", prefix[:40])

open(P, "w", encoding="utf-8", newline="\n").write("\n".join(src))
print("OK SI migrate")
