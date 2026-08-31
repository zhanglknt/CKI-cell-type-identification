"""Figure 5: Cross-Organ Conservation — Clean layout for NAR submission.

Data source: results/phase35_cross_organ_conservation.csv (59 same-CT cross-organ
pairs) and results/phase35_cross_organ_summary.csv (17 cell-type summaries).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import _fig_style as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

# ---- Layout constants ----
DPI = st.DPI
MM = st.MM
FIG_W = st.DOUBLE
FIG_H = 150 * MM

LABEL_SIZE = st.LABEL_SIZE
SMALL_SIZE = st.SMALL_SIZE
MID_SIZE   = st.BODY_SIZE

C_BLUE   = st.C_BLUE
C_GREEN  = st.C_GREEN
C_RED    = st.C_RED
C_ORANGE = st.C_ORANGE
C_AMBER  = st.C_AMBER
C_PURPLE = st.C_PURPLE
C_DARK   = st.C_DARK
C_GRAY   = st.C_GRAY

OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'figures_final')
os.makedirs(OUTDIR, exist_ok=True)


def savefig(name, w, h):
    for ext in ['.pdf', '.png']:
        path = os.path.join(OUTDIR, name + ext)
        plt.savefig(path, dpi=DPI if ext == '.png' else None,
                    bbox_inches='tight', pad_inches=0.02)
    print(f'  -> {name}.pdf + .png')


# Load authoritative data
ROOT = os.path.join(os.path.dirname(__file__), '..')
pairs = pd.read_csv(os.path.join(ROOT, 'results', 'phase35_cross_organ_conservation.csv'))
summary = pd.read_csv(os.path.join(ROOT, 'results', 'phase35_cross_organ_summary.csv'))

# Short display labels
CT_SHORT = {
    'cd8-positive, alpha-beta t cell': 'CD8+ T',
    'cd4-positive, alpha-beta t cell': 'CD4+ T',
    'plasma cell': 'Plasma',
    'memory b cell': 'Memory B',
    'naive b cell': 'Naive B',
    'b cell': 'B cell',
    'nk cell': 'NK',
    'neutrophil': 'Neutrophil',
    'macrophage': 'Macrophage',
    'classical monocyte': 'Classical Mono.',
    'intermediate monocyte': 'Inter. Mono.',
    'monocyte': 'Monocyte',
    'endothelial cell': 'Endothelial',
    'erythrocyte': 'Erythrocyte',
    'hepatocyte': 'Hepatocyte',
    'smooth muscle cell': 'Smooth muscle',
    'hematopoietic stem cell': 'HSC',
}
summary['ct_short'] = summary['ct'].map(CT_SHORT).fillna(summary['ct'])

# Sort by mean omega; separate well-sampled (n>=5) and sparse
well = summary[summary['n_pairs'] >= 5].sort_values('mean_omega')
sparse = summary[summary['n_pairs'] < 5].sort_values('mean_omega')
ranked = pd.concat([well, sparse])

# Organ-pair means for Panel C
pairs['organ_pair'] = pairs.apply(lambda r: '-'.join(sorted([r['organ_i'], r['organ_j']])), axis=1)
organ_summary = pairs.groupby('organ_pair')['omega'].agg(['mean', 'std', 'count']).reset_index()
organ_summary = organ_summary.sort_values('mean')

print('[Figure 5] Cross-Organ Conservation ...')
print(f'Figure 5: {FIG_W/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
gs = gridspec.GridSpec(
    2, 2, fig,
    height_ratios=[1.0, 1.0],
    left=0.08, right=0.97, top=0.92, bottom=0.07,
    hspace=0.55, wspace=0.40,
)

# ----------------------------------------------------------------
# PANEL A: Ranking of 17 cell types
# ----------------------------------------------------------------
axA = fig.add_subplot(gs[0, 0])
y_pos = np.arange(len(ranked))
colors_a = [C_GREEN if n >= 5 else C_GRAY for n in ranked['n_pairs']]
axA.barh(y_pos, ranked['mean_omega'], color=colors_a, alpha=0.85,
         edgecolor=C_DARK, linewidth=0.5, zorder=2)
# Error bars for well-sampled types
for i, (_, row) in enumerate(ranked.iterrows()):
    if row['n_pairs'] >= 5 and not np.isnan(row['std_omega']):
        axA.errorbar(row['mean_omega'], i, xerr=row['std_omega'],
                     fmt='none', ecolor=C_DARK, elinewidth=0.8, capsize=2, alpha=0.7)
axA.set_yticks(y_pos)
axA.set_yticklabels(ranked['ct_short'], fontsize=SMALL_SIZE)
axA.set_xlabel('Mean CKI \u03c9', fontsize=MID_SIZE, labelpad=2)
axA.set_title('17 cross-organ cell-type ranks (n=59 pairs)',
              fontsize=SMALL_SIZE, fontweight='bold', pad=4)
axA.tick_params(axis='x', labelsize=SMALL_SIZE)
axA.invert_yaxis()
st.subtle_grid(axA, axis='x')
st.despine(axA)
st.add_panel_label(fig, axA, 'A', x=-0.18, y=1.04)

# ----------------------------------------------------------------
# PANEL B: Distribution of all 59 pair omega values
# ----------------------------------------------------------------
axB = fig.add_subplot(gs[0, 1])
# Split into conserved (<15) vs variable
conserved = pairs[pairs['omega'] < 15]['omega']
variable = pairs[pairs['omega'] >= 15]['omega']
bins = np.linspace(0, 80, 25)
axB.hist([conserved, variable], bins=bins, stacked=True,
         color=[C_GREEN, C_AMBER], edgecolor='white', linewidth=0.4,
         label=[f'Conserved (<15), n={len(conserved)}',
                f'Variable (\u226515), n={len(variable)}'])
axB.set_xlabel('CKI \u03c9', fontsize=MID_SIZE, labelpad=2)
axB.set_ylabel('Number of pairs', fontsize=MID_SIZE, labelpad=2)
axB.set_title('\u03c9 distribution across cross-organ pairs',
              fontsize=SMALL_SIZE, fontweight='bold', pad=4)
axB.tick_params(labelsize=SMALL_SIZE)
axB.legend(fontsize=SMALL_SIZE, frameon=False, loc='upper right')
st.subtle_grid(axB, axis='y')
st.despine(axB)
st.add_panel_label(fig, axB, 'B', x=-0.14, y=1.04)

# ----------------------------------------------------------------
# PANEL C: Cross-organ omega gradient (mean \u00b1 SD by organ pair)
# ----------------------------------------------------------------
axC = fig.add_subplot(gs[1, 0])
x_pos = np.arange(len(organ_summary))
axC.bar(x_pos, organ_summary['mean'], color=C_BLUE, alpha=0.8,
        edgecolor=C_DARK, linewidth=0.5, zorder=2)
axC.errorbar(x_pos, organ_summary['mean'], yerr=organ_summary['std'],
             fmt='none', ecolor=C_DARK, elinewidth=0.8, capsize=2, zorder=3)
axC.set_xticks(x_pos)
axC.set_xticklabels(organ_summary['organ_pair'], rotation=35, ha='right',
                    fontsize=SMALL_SIZE)
axC.set_ylabel('Mean CKI \u03c9 \u00b1 SD', fontsize=MID_SIZE, labelpad=2)
axC.set_title('Cross-organ \u03c9 gradient', fontsize=SMALL_SIZE,
              fontweight='bold', pad=4)
axC.tick_params(axis='y', labelsize=SMALL_SIZE)
st.subtle_grid(axC, axis='y')
st.despine(axC)
st.add_panel_label(fig, axC, 'C', x=-0.14, y=1.04)

# ----------------------------------------------------------------
# PANEL D: Top conserved cell-type pairs
# ----------------------------------------------------------------
axD = fig.add_subplot(gs[1, 1])
top5 = pairs.nsmallest(5, 'omega').copy()
top5['label'] = top5.apply(
    lambda r: f"{CT_SHORT.get(r['ct'], r['ct'])}\n{r['organ_i'][:4]}-{r['organ_j'][:4]}", axis=1)
axD.barh(np.arange(len(top5)), top5['omega'], color=C_GREEN, alpha=0.85,
         edgecolor=C_DARK, linewidth=0.5, zorder=2)
for i, (_, row) in enumerate(top5.iterrows()):
    axD.text(row['omega'] + 0.5, i, f"{row['omega']:.1f}",
             va='center', fontsize=SMALL_SIZE, fontweight='bold', color=C_DARK)
axD.set_yticks(np.arange(len(top5)))
axD.set_yticklabels(top5['label'], fontsize=SMALL_SIZE)
axD.set_xlabel('CKI \u03c9', fontsize=MID_SIZE, labelpad=2)
axD.set_title('Top 5 conserved cross-organ pairs',
              fontsize=SMALL_SIZE, fontweight='bold', pad=4)
axD.tick_params(axis='x', labelsize=SMALL_SIZE)
axD.invert_yaxis()
st.subtle_grid(axD, axis='x')
st.despine(axD)
st.add_panel_label(fig, axD, 'D', x=-0.14, y=1.04)

savefig('figure5_cross_organ_conservation', FIG_W, FIG_H)
print('Done.')
