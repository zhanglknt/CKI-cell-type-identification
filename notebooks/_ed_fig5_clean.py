"""
Extended Data Figure 5: Cross-Organ CKI omega — Grouped bar chart.
Replaces the old table with a proper figure, NAR-compliant.
Layout: 2 rows x 1 column (mean omega top, CV bottom)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np

# ---- Constants ----
MM = 1 / 25.4
DOUBLE = 178 * MM
DPI = 300
OUT_DIR = Path('results/figures_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# NAR rcParams
matplotlib.rcParams.update({
    'font.family': 'Arial',
    'font.size': 8,
    'axes.titlesize': 9,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.titlesize': 10,
    'axes.linewidth': 0.5,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.0,
    'patch.linewidth': 0.5,
    'savefig.dpi': DPI,
    'savefig.format': 'pdf',
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

LABEL_SIZE = 9
TITLE_SIZE = 9
BODY_SIZE  = 8
SMALL_SIZE = 7

# ---- Data ----
cell_types = ['T cell', 'B cell', 'Macrophage', 'NK cell', 'Neutrophil',
              'Fibroblast', 'Endothelial', 'Epithelial', 'Hepatocyte', 'Neuron']
mouse_mean = np.array([0.82, 0.91, 1.14, 1.31, 1.58, 2.31, 2.54, 2.87, 3.12, 4.21])
human_mean = np.array([0.91, 0.98, 1.08, 1.42, 1.67, 2.54, 2.71, 3.12, 3.45, 4.58])
mouse_cv   = np.array([0.21, 0.18, 0.25, 0.31, 0.29, 0.38, 0.34, 0.41, 0.42, 0.51])
human_cv   = np.array([0.19, 0.17, 0.22, 0.28, 0.31, 0.35, 0.33, 0.39, 0.40, 0.49])
conserved  = ['Yes','Yes','Yes','Partial','Partial','Yes','Yes','Partial','No','No']
n_pairs_m  = [28] * 10
n_pairs_h  = [31] * 10

# Colors
C_MOUSE   = '#1B4F8A'   # blue
C_HUMAN   = '#922B21'   # red
C_YES     = '#D5F5E3'   # light green for conserved=Yes
C_PARTIAL  = '#FEF9E7'   # light yellow for Partial
C_NO      = '#FADBD8'    # light red for No

conserved_colors = [C_YES if c == 'Yes' else (C_PARTIAL if c == 'Partial' else C_NO) for c in conserved]

# ---- Figure ----
FIG_H = 115 * MM
fig = plt.figure(figsize=(DOUBLE, FIG_H), dpi=DPI)

GS_LEFT   = 0.11
GS_RIGHT  = 0.97
GS_TOP    = 0.93
GS_BOTTOM = 0.18   # more room for Panel B xtick labels + caption
GS_HSPACE = 0.45

gs = gridspec.GridSpec(2, 1, fig,
    left=GS_LEFT, right=GS_RIGHT, top=GS_TOP, bottom=GS_BOTTOM,
    hspace=GS_HSPACE)

# ---- Panel A: omega mean ----
axA = fig.add_subplot(gs[0])
x = np.arange(len(cell_types))
width = 0.32

bars_m = axA.bar(x - width/2, mouse_mean, width,
                   label='Mouse', color=C_MOUSE, edgecolor='white', linewidth=0.5)
bars_h = axA.bar(x + width/2, human_mean, width,
                   label='Human', color=C_HUMAN, edgecolor='white', linewidth=0.5)

# Conserved background stripes
for i, (xc, cc) in enumerate(zip(x, conserved_colors)):
    axA.axvspan(i - 0.5, i + 0.5, color=cc, alpha=0.25, zorder=0)

axA.set_xticks(x)
axA.set_xticklabels([])  # no labels on top panel
axA.set_ylabel('CKI omega (mean)', fontsize=BODY_SIZE, labelpad=2)
axA.set_ylim(0, 5.5)
axA.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
axA.spines[['top', 'right']].set_visible(False)
axA.legend(fontsize=SMALL_SIZE, frameon=False, loc='upper left',
           bbox_to_anchor=(0, 1.02, 1, 0.1), ncol=2)

# Panel label A (fig.text, ha='right', fig6 convention)
fig.text(0.04, GS_TOP + 0.012, 'A',
         fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='right')

# ---- Panel B: omega CV ----
axB = fig.add_subplot(gs[1], sharex=axA)
# sort by mouse_cv for visual clarity
sort_idx = np.argsort(mouse_cv)
x_sorted = np.arange(len(cell_types))

bars_m_cv = axB.bar(x_sorted - width/2, mouse_cv[sort_idx], width,
                     label='Mouse', color=C_MOUSE, edgecolor='white', linewidth=0.5)
bars_h_cv = axB.bar(x_sorted + width/2, human_cv[sort_idx], width,
                     label='Human', color=C_HUMAN, edgecolor='white', linewidth=0.5)

# Conserved background (same order as sorted)
conserved_sorted = [conserved[i] for i in sort_idx]
conserved_colors_sorted = [C_YES if c == 'Yes' else (C_PARTIAL if c == 'Partial' else C_NO)
                           for c in conserved_sorted]
for i, cc in enumerate(conserved_colors_sorted):
    axB.axvspan(i - 0.5, i + 0.5, color=cc, alpha=0.25, zorder=0)

sorted_labels = [cell_types[i] for i in sort_idx]
axB.set_xticks(x_sorted)
axB.set_xticklabels(sorted_labels, rotation=25, ha='right', fontsize=SMALL_SIZE)
axB.set_ylabel('CKI omega (CV)', fontsize=BODY_SIZE, labelpad=2)
axB.set_ylim(0, 0.6)
axB.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
axB.spines[['top', 'right']].set_visible(False)
axB.legend(fontsize=SMALL_SIZE, frameon=False, loc='upper left',
           bbox_to_anchor=(0, 1.02, 1, 0.1), ncol=2)

# Panel label B
fig.text(0.04, GS_BOTTOM + 0.38 + 0.012, 'B',
         fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='right')

# ---- Conserved legend (top-right) ----
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=C_YES,     alpha=0.7, edgecolor='#888888', linewidth=0.5, label='Conserved (Yes)'),
    Patch(facecolor=C_PARTIAL,  alpha=0.7, edgecolor='#888888', linewidth=0.5, label='Partial'),
    Patch(facecolor=C_NO,       alpha=0.7, edgecolor='#888888', linewidth=0.5, label='Not conserved (No)'),
]
fig.legend(handles=legend_elements, loc='lower right',
           bbox_to_anchor=(0.99, 0.86), fontsize=SMALL_SIZE,
           frameon=False, ncol=1, handlelength=1.5, handleheight=0.9)

# ---- Caption ----
fig.text(0.5, 0.035,
         'Extended Data Figure 5. Cross-organ CKI omega comparison between mouse and human across 10 cell types.\n'
         'Background shading indicates cross-species conservation status.',
         ha='center', fontsize=BODY_SIZE-1, linespacing=1.3)

# ---- Save ----
out_png = OUT_DIR / 'ed_fig5_cross_organ.png'
out_pdf = OUT_DIR / 'ed_fig5_cross_organ.pdf'

fig.savefig(out_png, dpi=DPI, facecolor='white',
            bbox_inches='tight', pad_inches=0.02)
fig.savefig(out_pdf, dpi=DPI, facecolor='white',
            bbox_inches='tight', pad_inches=0.02,
            metadata={'Creator': 'CKI NAR Extended Data Figures'})

print(f'Saved: {out_png}')
print(f'Saved: {out_pdf}')
plt.close()
print('Extended Data Figure 5 (grouped bar chart) DONE.')
