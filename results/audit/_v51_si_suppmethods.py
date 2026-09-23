import json, sys

SIPATH = 'notebooks/68_gen_supplementary_nc.py'
paras = json.load(open('results/audit/_v51_methods_orig.json', encoding='utf-8'))
assert len(paras) == 24

# --- restore citation brackets lost in docx text extraction ---
FIX = [
    ('log1p transformation 42.', 'log1p transformation [42].'),
    ('HRT Atlas v1.0 reference 13 (', 'HRT Atlas v1.0 reference [13] ('),
    ('JS divergence 43 using', 'JS divergence [43] using'),
    ('FDR correction 44 is', 'FDR correction [44] is'),
    ('SmartSeq2 8:', 'SmartSeq2 [8]:'),
    ('scanpy 45 with', 'scanpy [45] with'),
    ('flavor="seurat" 46,47 and', 'flavor="seurat" [46,47] and'),
    ('Tabula Sapiens v1.0 9:', 'Tabula Sapiens v1.0 [9]:'),
    ('CZ CELLxGENE Discover 48.', 'CZ CELLxGENE Discover [48].'),
    ('TCGA bulk RNA-seq 49:', 'TCGA bulk RNA-seq [49]:'),
    ('TCGAbiolinks 50 and', 'TCGAbiolinks [50] and'),
    ('cBioPortal 51 APIs', 'cBioPortal [51] APIs'),
    ('subtype assignments 52,53 were', 'subtype assignments [52,53] were'),
    ('Edmondson grade 54: from', 'Edmondson grade [54]: from'),
    ('Human brain atlas 12:', 'Human brain atlas [12]:'),
    ('Kang et al. 14 (GEO', 'Kang et al. [14] (GEO'),
    ('Kang batch 1 14:', 'Kang batch 1 [14]:'),
    ('Brain drift ladder 12: from', 'Brain drift ladder [12]: from'),
    ('subtype calls 52,53 were', 'subtype calls [52,53] were'),
    ('Edmondson grades 54 came', 'Edmondson grades [54] came'),
    ('scanpy 1.12.1 45,', 'scanpy 1.12.1 [45],'),
    ('seaborn 55 \u2265', 'seaborn [55] \u2265'),
    ('scikit-learn 56 \u2265', 'scikit-learn [56] \u2265'),
    ('Resampling-based inference 57 (', 'Resampling-based inference [57] ('),
    ('HRT Atlas HK genes 13)', 'HRT Atlas HK genes [13])'),
]
for k in range(24):
    for a, b in FIX:
        if a in paras[k]:
            paras[k] = paras[k].replace(a, b)

# --- subsection map: (title, [idx]) ---
SUBS = [
    ('4.1 CKI computation', [0, 1, 2, 3]),
    ('4.2 Permutation testing', [4]),
    ('4.3 Datasets: Tabula Muris, Tabula Sapiens, TCGA', [5, 6, 7]),
    ('4.4 Dataset: human brain atlas', [8]),
    ('4.5 Method comparison', [9]),
    ('4.6 Multiplicative residual model (brain)', [10]),
    ('4.7 Brain robustness analyses and donor-stratified null', [11, 12]),
    ('4.8 Ground-truth simulation', [13]),
    ('4.9 Real perturbation demonstration (IFN-\u03b2 PBMC)', [14]),
    ('4.10 Neutral-drift calibration on technical replicates', [15]),
    ('4.11 Fixed gene-panel ablation', [16]),
    ('4.12 TCGA per-sample statistics and clinical severity analyses', [17, 18]),
    ('4.13 Computational environment', [19]),
    ('4.14 Statistical inference details', [20, 21, 22]),
]

lines = []
lines.append('# ===== Supplementary Methods (v51: procedural detail migrated verbatim from main-text Methods) =====')
lines.append("add_heading('Supplementary Methods', 2)")
lines.append("add_para('Sections 4.1\\u20134.14 collect, verbatim, the full procedural detail compressed out of the main-text Methods in v51. All parameter values, scripts, and output files are preserved; subsection numbering follows the main-text Methods order.')")
for title, idxs in SUBS:
    lines.append(f'add_para({title!r}, bold=True)')
    for j in idxs:
        lines.append(f'add_para({paras[j]!r})')
FRAG = '\n'.join(lines) + '\n'

src = open(SIPATH, encoding='utf-8').read()

# 1) insert fragment before Supplementary Tables section
anchor1 = '# ===== Supplementary Tables ====='
assert src.count(anchor1) == 1
src = src.replace(anchor1, FRAG + '\n' + anchor1)

# 2) TOC entry
anchor2 = "    'Supplementary Note 16: Independent Human-Brain Validation on the Microglia Supercluster',"
assert src.count(anchor2) == 1
src = src.replace(anchor2, anchor2 + "\n    'Supplementary Methods',")

# 3) targeted note insertions (migrated numbers)
NOTE_INS = [
    ("add_heading('Supplementary Note 2:",
     "add_para('Second-background detail (migrated from the main text in v51): the skin k_f selection floor is lower than marrow (median 0.011 versus 0.025); at \\u03b4 = 1, \\u03c9 detection was 0.91 versus 0.00 in marrow, and under the fourfold cell-count imbalance k_f retained higher power (0.98\\u20131.00 versus 0.04\\u20130.20).')"),
    ("add_heading('Supplementary Note 7:",
     "add_para('Effect-scale detail (migrated from the main text in v51): median within-donor stimulated-versus-control \\u03c9 exceeded median donor-versus-donor \\u03c9 by 1.1\\u20132.0-fold.')"),
    ("add_heading('Supplementary Note 8:",
     "add_para('Panel grand means and ranking robustness (migrated from the main text in v51): 38.55 reported, 26.5 leave-pair-out, 6.5 fixed, 5.3 unselected; the circular panel inflated k_f by a median 1.61-fold relative to leave-pair-out and by 6.1- and 7.3-fold relative to the fixed and unselected panels, and the multiplicative-residual ranking correlated at \\u03c1 = 0.86\\u20130.88 across schemes.')"),
    ("add_heading('Supplementary Note 9:",
     "add_para('Purity sensitivity detail (migrated from the main text in v51): high-purity-half comparisons increased the TT k_n elevation ratio in all five cancer types (e.g. LUAD 2.46 \\u2192 2.86).')"),
    ("add_heading('Supplementary Note 10:",
     "add_para('Same-organ decomposition values (migrated from the main text in v51): same-organ pairs have indistinguishable k_f (0.247 vs. 0.250, P = 0.60) but lower k_n (0.0130 vs. 0.0148, P = 3.0 \\u00d7 10\\u207b\\u00b9\\u2076), contributing +0.176 on the log scale (factor 1.19).')"),
    ("add_heading('Supplementary Note 13:",
     "add_para('Within-donor gradient values (migrated from the main text in v51): astrocytes remained the most divergent class (mean \\u03c9 = 75.18 across 11,139 within-donor pairs, versus 82.75 pooled) and Bergmann glia the least (16.73), a 4.50-fold gradient.')"),
]
for anchor, ins in NOTE_INS:
    assert src.count(anchor) == 1, anchor
    src = src.replace(anchor, ins + '\n\n' + anchor)

open(SIPATH, 'w', encoding='utf-8').write(src)
print('SI generator updated OK')
