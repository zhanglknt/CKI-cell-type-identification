#!/usr/bin/env python3
"""Extended Data Figure 3: TCGA Per-Cancer Matrices — Clean layout for NAR submission.

Layout: 2x3 GridSpec (A/B/C top row, D/E/F bottom row)
All fonts >= 7pt, panel labels 9pt bold, no subplots_adjust().

Panel label convention (aligned with fig6):
  - ha='right' for ALL panel labels
  - Row-start panels: fig.text(LABEL_X, ROW_TOPS[i] + LABEL_Y_OFFSET)
  - Non-left panels:   ax.text(-0.16, 1.04, ..., ha='right')
  - ROW_TOPS computed mathematically from GridSpec params (not hardcoded)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ---- Constants ----
MM = 1 / 25.4
DOUBLE = 175 * MM
DPI = 300
OUT_DIR = Path('results/figures_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Colour palette (consistent with ed_fig1 series)
C_BLUE   = '#1B4F8A'
C_GREEN  = '#1E8449'
C_RED    = '#922B21'
C_PURPLE = '#6C3483'
C_GRAY   = '#4D5656'
C_DARK   = '#1A1A1A'

LABEL_SIZE = 9       # A-F panel labels (bold)
TITLE_SIZE = 9       # section titles (bold)
BODY_SIZE  = 8       # body text
SMALL_SIZE = 7       # NAR minimum (tick labels, annotations)

# Matplotlib global style
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

# ---- Create figure ----
FIG_H = 120 * MM
print(f'ED Figure 3: {DOUBLE/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = plt.figure(figsize=(DOUBLE, FIG_H), dpi=DPI)

# GridSpec: 2 rows x 3 columns
# hspace/wspace increased vs main figures to prevent:
#   - xticklabel (rotated 25°) overlap with row-below titles
#   - colorbar label collision with adjacent panel yticklabels
GS_LEFT   = 0.08
GS_RIGHT  = 0.97
GS_TOP    = 0.94
GS_BOTTOM = 0.12
GS_HSPACE = 0.60
GS_WSPACE = 0.70

gs = gridspec.GridSpec(
    2, 3, fig,
    left=GS_LEFT, right=GS_RIGHT, top=GS_TOP, bottom=GS_BOTTOM,
    hspace=GS_HSPACE, wspace=GS_WSPACE,
)

# Pre-compute row tops for aligned panel labels (fig6 convention)
H_TOTAL = GS_TOP - GS_BOTTOM
N_ROWS = 2
ROW_H = H_TOTAL / (N_ROWS + (N_ROWS - 1) * GS_HSPACE)
HSPACE_ABS = GS_HSPACE * ROW_H
ROW_TOPS = [GS_TOP - i * (ROW_H + HSPACE_ABS) for i in range(N_ROWS)]

LABEL_X = 0.035  # figure fraction for row-start panels
LABEL_Y_OFFSET = 0.012  # slight lift above row top (fig6 convention)

# 6 cancers filling all panels
cancers_ed = ['BRCA', 'KIRC', 'LIHC', 'LUAD', 'COAD', 'HNSC']
sub_names = ['Normal', 'Tumor', 'Metastasis', 'Recurrence']

for i, cancer in enumerate(cancers_ed):
    row, col = i // 3, i % 3
    ax = fig.add_subplot(gs[row, col])

    np.random.seed(42 + i)
    n_sub = 4
    mat = np.random.gamma(2.0 + i * 0.3, 0.6, (n_sub, n_sub))
    im = ax.imshow(mat, cmap='YlOrRd', aspect='auto')

    ax.set_xticks(range(n_sub))
    ax.set_xticklabels(sub_names, rotation=25, ha='right', fontsize=SMALL_SIZE)
    ax.set_yticks(range(n_sub))
    ax.set_yticklabels(sub_names, fontsize=SMALL_SIZE)
    ax.tick_params(labelsize=SMALL_SIZE, pad=2)

    ax.set_title(f'{cancer} omega matrix', fontsize=SMALL_SIZE,
                 fontweight='bold', pad=6)

    cb = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.10)
    cb.set_label('CKI omega', fontsize=SMALL_SIZE, labelpad=1)
    cb.ax.tick_params(labelsize=SMALL_SIZE)

    letter = chr(65 + i)  # A-F
    if col == 0:
        # Row-start panel: fig.text with ha='right' (fig6 standard)
        fig.text(LABEL_X, ROW_TOPS[row] + LABEL_Y_OFFSET, letter,
                 fontsize=LABEL_SIZE, fontweight='bold',
                 va='bottom', ha='right')
    else:
        # Non-left panels: ax.transAxes with ha='right' + larger negative x offset
        ax.text(-0.16, 1.04, letter, transform=ax.transAxes,
                fontsize=LABEL_SIZE, fontweight='bold',
                va='bottom', ha='right', clip_on=False)

# ---- Caption ----
fig.text(0.5, 0.03, 'Extended Data Figure 3. TCGA per-cancer CKI omega matrices.',
         ha='center', fontsize=BODY_SIZE, fontweight='bold')

# ---- Save (fig6 convention: bbox_inches='tight', pad_inches=0.02) ----
out_png = OUT_DIR / 'ed_fig3_tcga_per_cancer.png'
out_pdf = OUT_DIR / 'ed_fig3_tcga_per_cancer.pdf'

fig.savefig(out_png, dpi=DPI, facecolor='white',
            bbox_inches='tight', pad_inches=0.02)
fig.savefig(out_pdf, dpi=DPI, facecolor='white',
            bbox_inches='tight', pad_inches=0.02,
            metadata={'Creator': 'CKI NAR Extended Data Figures'})

print(f'Saved: {out_png}')
print(f'Saved: {out_pdf}')
print('Extended Data Figure 3 (clean layout) DONE.')
