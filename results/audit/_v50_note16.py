# v50: SI Note 16 (TOC + content) + MS pointer paragraph + micro-trims for word budget
MS = r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_nc.py"
SI = r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks\68_gen_supplementary_nc.py"

# ---------- SI ----------
src = open(SI, encoding="utf-8").read()

TOC_OLD = "    'Supplementary Note 15: JS Divergence Dimensionality Invariance',\n"
TOC_NEW = ("    'Supplementary Note 15: JS Divergence Dimensionality Invariance',\n"
           "    'Supplementary Note 16: Independent Human-Brain Validation on the Microglia Supercluster',\n")
assert src.count(TOC_OLD) == 1
src = src.replace(TOC_OLD, TOC_NEW)

N15_END = "    'consistency. (Supplementary Fig. 13.)'\n)\n"
NOTE16 = N15_END + """
doc.add_page_break()

add_heading('Supplementary Note 16: Independent Human-Brain Validation on the Microglia Supercluster', 2)
add_para(
    'This note reports an independent validation on data not used in any main-text '
    'analysis: the Microglia supercluster of the Human Brain Cell Atlas v1.0 '
    '(Siletti et al.; CZ CELLxGENE Discover, collection '
    '283d65eb-dd53-496d-adb7-7570c7caa443; 91,838 nuclei, 58,232 genes), which '
    'carries two cell_type labels\\u2014microglial cell (88,494 nuclei) and central '
    'nervous system macrophage (CNS-M\\u03c6; 3,344 nuclei)\\u2014across 4 donors, '
    '598 samples, and 10 brain regions. Pseudobulks were computed per '
    '(cell_type \\u00d7 sample) group (\\u2265 20 cells; 563 eligible groups, '
    '89,533 nuclei) with the Tabula Sapiens pipeline order (per-cell '
    'normalize_total(1e4) + log1p, then group means); k_n used the HRT Atlas v1.0 '
    'human HK genes (1,107 matched) and k_f the global seurat HVG 2,000 panel '
    'excluding HK (1,973 genes), with kn_floor = 1 \\u00d7 10\\u207b\\u2074 and '
    'seed 42. The functional contrast comprised 35 sample-matched '
    'microglia-versus-CNS-M\\u03c6 pairs (within-sample, controlling donor, '
    'region, and batch); neutral contrasts comprised 20 random half-splits per '
    'cell type of the same (cell_type, sample) group (microglia halves \\u2265 '
    '100 cells from 95 groups \\u2265 200 cells; CNS-M\\u03c6 halves \\u2265 50 '
    'cells from 4 groups \\u2265 100 cells, within the recommended 50\\u2013200 '
    'cell operating window).'
)
add_para(
    'CKI \\u03c9 separated the functional contrast from the neutral baseline '
    'completely: \\u03c9 = 21.83 \\u00b1 7.20 (functional) versus 1.30 \\u00b1 '
    '0.36 (neutral), Mann-Whitney P = 5.5 \\u00d7 10\\u207b\\u00b9\\u2074, exact '
    'rank AUC = 1.00. The margin is carried by the functional component: k_f '
    '(0.064 \\u00b1 0.012 versus 0.0020 \\u00b1 0.0016, AUC = 1.00) separates '
    'perfectly, whereas k_n (0.0033 \\u00b1 0.0011 versus 0.0014 \\u00b1 0.0009) '
    'is only partially elevated (AUC = 0.89)\\u2014the decomposition-first '
    'reading argued throughout the manuscript. Standard metrics also separated '
    'the classes (raw JS, cosine, and marker Jaccard AUC = 1.00; Spearman '
    '0.90), as expected for two genuinely distinct cell types; the validation '
    'value lies in \\u03c9 tracking the functional contrast far above its own '
    'neutral baseline on an independent dataset. Note that this analysis uses '
    'the global-HVG scheme, not the per-pair top-200 hybrid scheme, so absolute '
    '\\u03c9 values sit on a different scale from the 7.70-calibrated hybrid '
    'baseline and are compared internally only. Scripts: '
    'notebooks/nc50_brain_atlas_microglia.py and '
    'notebooks/nc50_fig_microglia.py; outputs: '
    'results/nc50_brain_atlas_microglia.csv and .txt. (Supplementary Fig. 14.)'
)
"""
assert src.count(N15_END) == 1
src = src.replace(N15_END, NOTE16)
open(SI, "w", encoding="utf-8", newline="\n").write(src)
print("SI Note 16 inserted")

# ---------- MS ----------
ms = open(MS, encoding="utf-8").read()

ANCHOR = "p('Two qualifications temper the brain result."
i = ms.index(ANCHOR)
j = ms.index("\n", i)
POINTER = (j and ms[:j]) + "\n\n" + (
    "p('An independent validation on data not used above reinforces this calibration: "
    "on the CELLxGENE Microglia supercluster [12] (91,838 nuclei), sample-matched "
    "microglia-versus-CNS-macrophage pairs (n = 35) separated cleanly from neutral "
    "half-splits (n = 40; \\u03c9 21.83 \\u00b1 7.20 versus 1.30 \\u00b1 0.36; "
    "Mann-Whitney P = 5.5 \\u00d7 10\\u207b\\u00b9\\u2074; AUC = 1.00), the margin "
    "carried by k_f (AUC 1.00) rather than k_n (0.89) (Supplementary Note 16; "
    "Supplementary Fig. 14).')"
) + ms[j:]
ms = POINTER

# micro-trims for word budget
TRIMS = [
 ("\\u03c9 is thus a specificity-first screen: its construction rejects neutral drift, at the cost of bounded power for weak-to-moderate functional signals (Supplementary Note 1).",
  "\\u03c9 is thus a specificity-first screen: its construction rejects neutral drift at the cost of bounded power for weak-to-moderate signals (Supplementary Note 1)."),
 ("A real perturbation demonstration (Kang et al. [14]; Results) makes the boundary explicit: IFN-\\u03b2 stimulation raises k_n itself 1.2\\u20135.7-fold above the donor-drift level, and where it does so most strongly (CD14+ monocytes) the \\u03c9 AUC falls to 0.55 while k_f retains 0.98\\u2014when the anchor itself moves, cross-metric contrasts, not absolute \\u03c9 values, are the reliable signal.",
  "The IFN-\\u03b2 demonstration (Kang et al. [14]; Results) makes the boundary explicit: when the anchor itself moves (k_n raised 1.2\\u20135.7-fold; monocyte \\u03c9 AUC 0.55 versus k_f 0.98), cross-metric contrasts, not absolute \\u03c9 values, are the reliable signal."),
 ("p('The entire design was repeated in a second Tabula Muris FACS background\\u2014skin keratinocyte stem cells",
  "p('The design was repeated in a second Tabula Muris FACS background\\u2014skin keratinocyte stem cells"),
]
for old, new in TRIMS:
    assert ms.count(old) == 1, old[:60]
    ms = ms.replace(old, new)

open(MS, "w", encoding="utf-8", newline="\n").write(ms)
print("MS pointer inserted + trims applied")
