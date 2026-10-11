#!/usr/bin/env python3
"""nc70 reference renumber: MS + SI + Guide after figure consolidation.

Main figures:  1->1, 2->2 (2c->2b, 2d->2c, 2e->2d), 3->2 (3a->2e, 3b->2f,
               3c->2e), 4->3 (letters kept), 5->4, 6->5, 7->'5e, f'
Supp figures:  1->1, 2->2, 3->3, 4->3, 5->2 (5b->2d), 6->6, 7->4, 8->4,
               9->5, 10->5, 11->6, 12->6, 13->1, 14->1, 15->7 (letters
               kept), 16->7 (16b->7e, 16c->7f), 17->8, 18->8, 19->9

Order: reference passes run on the ORIGINAL text first; the new legend
blocks (already carrying FINAL numbers) are swapped in afterwards so the
renumber never touches them.
Non-reentrant: on failure `git checkout -- generate_manuscript_nc.py
notebooks/68_gen_supplementary_nc.py notebooks/100_gen_reproducibility_nc.js`.
"""
import re

MS = 'generate_manuscript_nc.py'
SI = 'notebooks/68_gen_supplementary_nc.py'
GD = 'notebooks/100_gen_reproducibility_nc.js'

SFIG = {1: 1, 2: 2, 3: 3, 4: 3, 5: 2, 6: 6, 7: 4, 8: 4, 9: 5, 10: 5,
        11: 6, 12: 6, 13: 1, 14: 1, 15: 7, 16: 7, 17: 8, 18: 8, 19: 9}
SFIG_LET = {'5b': '2d', '15a': '7a', '15b': '7b', '15c': '7c',
            '16b': '7e', '16c': '7f'}
MAIN_LET = {'2a': '2a', '2b': '2b', '2c': '2b', '2d': '2c', '2e': '2d',
            '3a': '2e', '3b': '2f', '3c': '2e',
            '4a': '3a', '4b': '3b', '4c': '3c', '4d': '3d'}
MAIN_BARE = {'3': '2', '4': '3', '5': '4', '6': '5', '7': '5e, f'}

stats = []


def note(msg):
    stats.append(msg)
    print(msg)


def supp_sub(text, label):
    n = text.count('Supplementary Figs. 15, 16')
    text = text.replace('Supplementary Figs. 15, 16', '@@GRP7@@')
    if n:
        note(f'  [{label}] group Figs. 15,16 -> Fig. 7  x{n}')
    store = []

    logs = []

    def _rep(m):
        key = m.group(1) + (m.group(2) or '')
        new = SFIG_LET.get(key) or (str(SFIG[int(m.group(1))]) + (m.group(2) or ''))
        store.append(new)
        logs.append(f'{key}->{new}')
        return f'@@S{len(store)-1}@@'

    text = re.sub(r'Supplementary Fig\. (\d+)([a-z])?', _rep, text)
    note(f'  [{label}] supp refs: {logs}')
    return text, store


def main_sub(text, label):
    text = text.replace('Fig. 3b,c', '@@MBC@@')
    store = []
    logs = []

    def _rep(m):
        num, lett = m.group(1), m.group(2)
        if lett:
            letters = [lett[0]] + ([lett[-1]] if ',' in lett else [])
            mapped = [MAIN_LET[num + l] for l in letters]
            new = mapped[0][0] + (', '.join(x[1:] for x in mapped)
                                  if len(mapped) > 1 else mapped[0][1:])
        else:
            new = MAIN_BARE.get(num, num)
        store.append(new)
        logs.append(f'{num}{lett or ""}->{new}')
        return f'@@M{len(store)-1}@@'

    text = re.sub(r'Fig\. (\d+)([a-z](?:, [a-z])?)?', _rep, text)
    note(f'  [{label}] main refs: {logs}')
    return text, store


def restore(text, sstore, mstore):
    for i, new in enumerate(sstore):
        text = text.replace(f'@@S{i}@@', f'Supplementary Fig. {new}')
    for i, new in enumerate(mstore):
        text = text.replace(f'@@M{i}@@', f'Fig. {new}')
    text = text.replace('@@MBC@@', 'Fig. 2e, f')
    text = text.replace('@@GRP7@@', 'Supplementary Fig. 7')
    # multi-letter maps that collapsed to one panel ('2b, c'->'2b, b') dedupe
    text = text.replace('Fig. 2b, b', 'Fig. 2b')
    text = text.replace('Fig. 2f, e', 'Fig. 2e, f')
    return text


def renumber(src, label):
    src, ss = supp_sub(src, label)
    src, ms_ = main_sub(src, label)
    return restore(src, ss, ms_)


# ------------------------------------------------------------------ MS
def do_ms():
    src = open(MS, encoding='utf-8').read()
    n = src.count('Supplementary Figs. 1\\u201319')
    src = src.replace('Supplementary Figs. 1\\u201319',
                      'Supplementary Figs. 1\\u20139')
    note(f'[MS] availability Figs. 1-19 -> 1-9  x{n}')

    src = renumber(src, 'MS')

    i0 = src.find("p('Figure 1. The CKI framework.")
    i1 = src.find("p('Table 1. Cross-organ conservation ranking")
    assert i0 > 0 and i1 > i0
    src = src[:i0] + LEGENDS + '\n\n' + src[i1:]
    note('[MS] legend block swapped (7 -> 5)')
    open(MS, 'w', encoding='utf-8', newline='\n').write(src)
    note('[MS] written')


LEGENDS = r"""p('Figure 1. The CKI framework. (a) Conceptual analogy between Ka/Ks in molecular evolution and CKI in transcriptomics. Ka/Ks uses synonymous substitution rate (Ks) as a neutral baseline; \u03c9 = Ka/Ks > 1 indicates positive selection (a heuristic analogy only, not a formal population-genetic claim). CKI uses housekeeping gene divergence for k_n\u2014the constrained counterpart of the synonymous baseline\u2014and identity gene divergence for k_f\u2014the counterpart of nonsynonymous divergence; \u03c9 = k_f/k_n quantifies transcriptomic divergence relative to the baseline, read against the empirical calibration baseline rather than against 1; and the computational pipeline: raw count matrix \u2192 pseudobulk \u2192 JS divergence on HK genes (k_n) and identity genes (k_f) \u2192 \u03c9 = k_f/k_n. (b) Bootstrap distribution of the mean split-half control \u03c9 (B = 10,000 resamples of the 300 mouse-pilot split-half control \u03c9 values from 50 replicates across six control populations), with the median indicated by the dashed line and the control mean (the empirical calibration baseline 7.70, two-stage population-bootstrap 95% CI [6.38, 9.82]) by the dotted line. (c) Scatter plot of k_n vs. k_f, showing that functional variation dominates constrained baseline. (d) \u03c9 distribution with \u03c9 = 1 (the full-matching expectation for k_f = k_n, marked by dashed line) and the empirical calibration baseline \u03c9 = 7.70 indicated; \u03c9 = 1 is never observed in practice because identity-gene selection inflates k_f relative to k_n (see Results).')

p(f'Figure 2. CKI calibration on Tabula Muris, metric correlation on Tabula Sapiens, functional-change detection in the ground-truth simulation, and neutral-drift calibration on technical replicates. (a) k_n calibration across six Tabula Muris cell types from control comparisons (random split of the same population); k_n is stable across cell types, consistent with constrained baseline behavior. (b) Component decomposition of k_n and k_f across four comparison categories (C, random split of the same population; S, same cell type, different organ; D, different cell type, same organ; X, different cell type, different organ) and \u03c9 distribution by category (log scale): k_f and \u03c9 increase monotonically with biological distance, while k_n varies little. (c) Spearman correlation heatmap of five metrics on n = {_h["n_pairs_total"]:,} Tabula Sapiens pairs: CKI \u03c9 is negatively correlated with all four standard metrics, partly because k_n itself correlates positively with them (the \u03c9 denominator; see Results). (d) ROC curves for discriminating injected functional signal (\u03b4 \u2265 0.25) from neutral drift in the semi-synthetic ground-truth simulation (marrow B-cell background; 600 functional versus 250 neutral replicates). CKI \u03c9 gave the highest AUC of six metrics (0.80; paired DeLong \u0394AUC versus the runner-up k_f = +0.088, P = 2.4 \u00d7 10\u207b\u00b9\u2077, module-seed cluster bootstrap [0.070, 0.108]); independent replication on a skin keratinocyte background gave AUC = 0.91. (e) Neutral-drift calibration on the Kang IFN-\u03b2 PBMC technical replicates (30 same-donor cross-lane pairs, n-matched null, B = 200 per pair): \u03c9 FPR = 0 of 30 (calibration median 0.96) versus 36.7% for raw JS and 23.3% for cosine; and brain false-positive rates on T1 (technical) and T2 (donor) drift: \u03c9 misreports least among the continuous divergence metrics (T1: 28.6% versus 35.7\u201345.2%; paired McNemar exact P \u2264 4.1 \u00d7 10\u207b\u00b9\u00b2); marker Jaccard is lower still (T1 19.9%, T2 74.7%; versus \u03c9 on T1, P = 5.6 \u00d7 10\u207b\u00b2\u00b9) but responds weakest to real regional divergence. (f) Brain calibration distributions (observed / own n-matched null median; log scale) for seven metrics across the three-tier drift ladder (T1: 2,161 pairs, pure technical drift; T2: 1,089 pairs, crosses donors; T3: 1,656 pairs, crosses regions within a donor as positive control): \u03c9 (leftmost) stays near 1 at T1 with the shallowest gradient to T3 (T3 calibration 1.80 for \u03c9 and 2.98 for raw JS versus 1.41 for marker Jaccard).')

p('Figure 3. Pan-cancer tissue-level divergence in tumors. (a) Ratio of mean normal\u2013normal (NN) to tumor\u2013tumor (TT) \u03c9 per cancer type (blue; ranked by effect size), with sample-level cluster-bootstrap 95% CIs (B = 1,000); the amber axis shows the corresponding tumor/normal ratio of the housekeeping baseline k_n (TT/NN, means with 95% CIs), which exceeds 1 in all five cancer types while the NN/TT ratio of k_f does not\u2014the reversal is denominator-driven. The two axes use independent scales so that both series remain legible. Dotted line, ratio = 1. (b) Per-tumor \u03c9 in LUAD by driver mutation (wild-type n = 311, EGFR-mutant n = 61, KRAS-mutant n = 120; boxes, median and IQR; points, individual tumors). Kruskal-Wallis P = 7.8 \u00d7 10\u207b\u2077; brackets, Dunn post-hoc P-values with Holm correction. (c, d) The same stratification for the components k_f (c) and k_n (d): the KRAS contrast carries a functional component (KRAS > EGFR under k_f alone, P_Holm = 0.015; KRAS versus WT retained after purity and smoking adjustment, adjusted P = 0.009 and 0.029) together with a lower k_n baseline (WT > KRAS, P_Holm = 4.2 \u00d7 10\u207b\u2074), whereas the apparent EGFR elevation dissolved under purity adjustment (all adjusted P > 0.4), consistent with an admixture artefact rather than a baseline shift. All values from the linear-normalization re-computation (Methods).')

p(f'Figure 4. Cross-organ cell-type conservation. (a) CKI \u03c9 ranking of 17 cell types with cross-organ comparisons (n = 59 pairs) within the Tabula Sapiens human atlas, with well-sampled cell types (n \u2265 5 pairs) ranked first and sparsely sampled types (n < 5) listed separately. Among well-sampled types, CD8+ T cells, plasma cells, and neutrophils rank lowest; endothelial cells and erythrocytes rank highest (n = 3 pairs each, suggestive only). (b) \u03c9 distribution across all cell-type pairs, showing conserved vs. variable cell types. (c) Cross-organ \u03c9 gradient (mean \u00b1 SD) showing systematic variation across organ pairs. (d) Top 5 conserved cell-type pairs with the lowest cross-organ \u03c9 values.')

p('Figure 5. Brain regional cell-type differentiation, region-association inference, and neuronal superclass divergence. (a) Brain region map schematic showing anatomical regions analyzed in the Siletti et al. atlas. (b) \u03c9 gradient across 10 non-neuronal cell classes (mean \u03c9 per class, block-shuffle observed landscape): Bergmann glia and vascular cells lowest (mean \u03c9 = 13.56), astrocytes highest (82.75); the 6.10-fold raw gradient is an uncorrected upper bound, the span- and size-matched control giving 3.66-fold (donor-level bootstrap median 3.28, 95% CI [1.92, 3.78]; Supplementary Note 11), and the signal is dominated by the k_n denominator (3.21-fold k_n versus 2.03-fold k_f at the endpoint contrast; see Results). (c) Region-associated candidate detection: the multiplicative residual model identifies 39 Strong candidates (residual < 0.3, \u03c9 < 15, lowest \u03c9 in pair) among 31,764 cross-region comparisons; a design-matched null expects 148.3, so the observed 39 are anti-enriched (P(null count \u2265 39) = 1.0), none survives FDR correction, and only 3 of 39 are retained under a global-k_n estimator\u2014the catalogue is hypothesis-generating. (d) Observed vs. expected \u03c9 for the five strongest Strong candidates across all cell classes (lowest residuals), showing the gap between observed regional similarity and the cell-type-specific expectation. (e) Sample-level block-shuffle null for the three neuronal superclasses (grey violins, B = 1,000 permutations preserving the per-region library-count multiset; dark dash = null mean; red dot = observed mean regional \u03c9): MGE interneurons sit at the permutation floor (P = 0.001, SES = 7.2); upper-layer intratelencephalic neurons P = 0.014; thalamic excitatory neurons P = 0.163. (f) Median pair \u03c9 across the three neuronal superclasses (purple) and the ten non-neuronal classes (grey; astrocytes highlighted in red): neuronal medians 59.3\u201364.2 versus a non-neuronal median of 24.5 excluding astrocytes (descriptive cross-class contrast: one-sided Mann\u2013Whitney z = 52.6, P < 10\u207b\u00b3\u2070\u2070, pseudoreplicated at the pair level), so the non-neuronal screen understates atlas-wide regional divergence (Supplementary Note 18; Supplementary Fig. 8; Supplementary Table 22).')"""


# ------------------------------------------------------------------ SI
def get_legend(lines, num):
    head = f"'Supplementary Fig. {num}. "
    for ln in lines:
        s = ln.strip()
        if s.startswith('add_para(') and head in s:
            inner = s[len('add_para('):]
            if inner.endswith(')'):
                inner = inner[:-1].strip()
            return inner[1:-1]
    raise KeyError(num)


def split_header(body):
    i = body.find('. (a) ')
    if i > 0:
        return body[i + 2:]
    i = body.find('. ')
    return body[i + 2:]


def reletter(text, mapping):
    for old, new in mapping.items():
        text = text.replace(f'({old}) ', f'({new}) ')
    return text


def do_si():
    src = open(SI, encoding='utf-8').read()
    bodies_raw = {n: get_legend(src.split('\n'), n) for n in range(1, 20)}
    b = {n: split_header(t) for n, t in bodies_raw.items()}

    n = src.count("'Supplementary Figures (legends for Supplementary Figs. 1-19)'")
    src = src.replace("'Supplementary Figures (legends for Supplementary Figs. 1-19)'",
                      "'Supplementary Figures (legends for Supplementary Figs. 1-9)'")
    note(f'[SI] TOC Figs. 1-19 -> 1-9  x{n}')

    src = renumber(src, 'SI')

    s4 = reletter(b[4], {'a': 'd'}).replace('. (b) Median per-pair',
                                            '; and median per-pair')
    s8 = reletter(b[8], {'a': 'd'}).replace('. (b) Per-pair',
                                            '; and per-pair')
    new_legends = [
        'Supplementary Fig. 1. Parameter sweep, pathway analysis, JS divergence '
        'dimensionality invariance, and \\u03c9 distribution characterization. '
        + b[1] + ' ' + reletter(b[13], {'a': 'd', 'b': 'e'}) + ' (f) ' + b[14],
        'Supplementary Fig. 2. Calibrated \\u03c9 under two baselines and TCGA '
        'per-cancer matrices with supplementary stratification vignettes. '
        + b[2] + ' ' + reletter(b[5], {'a': 'c', 'b': 'd'}),
        'Supplementary Fig. 3. Human-brain sanity check on the microglia '
        'supercluster (Supplementary Note 7) and real perturbation demonstration '
        '(Kang et al. IFN-\\u03b2-stimulated PBMCs). ' + b[3] + ' ' + s4,
        'Supplementary Fig. 4. Brain regional analysis details and pair-specific '
        'k_n variability (brain). ' + b[7] + ' ' + s8,
        'Supplementary Fig. 5. Developmental signature detection and '
        'block-shuffle permutation null for the residual model. '
        + b[9] + ' (d) ' + b[10],
        'Supplementary Fig. 6. Pseudo-region negative control for the brain '
        'block-shuffle null, cross-species comparison details, and cross-organ '
        'conservation raw data. ' + b[11] + ' '
        + reletter(b[12], {'a': 'c'}) + ' (d) '
        + b[6].replace('panel a shows', 'upper sub-panel shows')
              .replace('panel b shows', 'lower sub-panel shows'),
        'Supplementary Fig. 7. Lineage-distance validation of k_f across two '
        'independent atlases (Supplementary Note 17). '
        + b[15] + ' ' + reletter(b[16], {'a': 'd', 'b': 'e', 'c': 'f'}),
        'Supplementary Fig. 8. Pair-level distributions and the subcluster tier '
        'for the neuronal superclass analysis, and program-level diffuseness '
        'with the SEA-AD disease-anchor positive control (Supplementary Notes '
        '18, 19; main Fig. 5e, f). '
        + b[17] + ' ' + reletter(b[18], {'a': 'c', 'b': 'd'}),
        bodies_raw[19].replace('Supplementary Fig. 19.', 'Supplementary Fig. 9.', 1),
    ]
    for i, leg in enumerate(new_legends, 1):
        assert leg.startswith(f'Supplementary Fig. {i}. '), f'header {i}'
        assert 'main Fig. 7' not in leg and 'Supplementary Fig. 1' not in leg[9:]

    i0 = src.find("add_heading('Supplementary Figures', 2)")
    assert i0 > 0
    i2 = src.find('\n', src.find('Supplementary Fig. 19.', i0))
    block = ("add_heading('Supplementary Figures', 2)\n"
             "add_para('Legends for Supplementary Figs. 1-9. Figure files are "
             "provided separately (results/ figures listed in the "
             "Reproducibility Guide).')\n\n"
             + '\n\n'.join(f"add_para('{l}')" for l in new_legends))
    src = src[:i0] + block + src[i2:]
    note('[SI] legend block rewritten (19 -> 9)')
    open(SI, 'w', encoding='utf-8', newline='\n').write(src)
    note('[SI] written')


# ------------------------------------------------------------------ Guide
def do_guide():
    src = open(GD, encoding='utf-8').read()
    src = renumber(src, 'GD')
    open(GD, 'w', encoding='utf-8', newline='\n').write(src)
    note('[GD] written')


if __name__ == '__main__':
    do_ms()
    do_si()
    do_guide()
