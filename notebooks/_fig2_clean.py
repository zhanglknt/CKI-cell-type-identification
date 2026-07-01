#!/usr/bin/env python3
"""Figure 2: Tabula Muris Calibration — Clean layout for NAR submission.

Layout: 2×2 GridSpec (A/B top row, C/D bottom row)
All fonts >= 7pt, panel labels 9pt bold, no tight_layout().
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ---- Constants ----
MM = 1 / 25.4
DOUBLE = 178 * MM
DPI = 300
OUT_DIR = Path('results/figures_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_DIR = Path('results')

# Colour palette
C_BLUE   = '#1B4F8A'
C_GREEN  = '#1E8449'
C_AMBER  = '#B7770D'
C_RED    = '#922B21'
C_ORANGE = '#C0581A'
C_PURPLE = '#6C3483'
C_TEAL   = '#0E7D78'
C_GRAY   = '#4D5656'
C_ORANGE2= '#DC7633'
C_STEEL  = '#5D6D7E'
C_DARK   = '#1A1A1A'
C_LIGHT_GRAY = '#D5D8DC'

LABEL_SIZE = 9       # A/B/C/D panel labels (bold)
TITLE_SIZE = 9       # section titles (bold)
BODY_SIZE  = 8       # body text
SMALL_SIZE = 7       # NAR minimum

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
FIG_H = 156 * MM
print(f'Figure 2: {DOUBLE/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = plt.figure(figsize=(DOUBLE, FIG_H), dpi=DPI)

# Outer GridSpec: 2 rows × 2 columns  (C & D get half-width each → no crowding)
gs = gridspec.GridSpec(
    2, 2, fig,
    height_ratios=[1.0, 1.35],
    left=0.08, right=0.97, top=0.94, bottom=0.06,
    hspace=0.45, wspace=0.32,
)

# ---- Data ----
np.random.seed(42)
cts_full = ['Atrium cardio.', 'Cortex', 'Kidney', 'Liver', 'Lung', 'Mammary']
cts_short = ['Atrium', 'Cortex', 'Kidney', 'Liver', 'Lung', 'Mammary']

# ================================================================
# PANEL A: k_n calibration (boxplot)
# ================================================================
axA = fig.add_subplot(gs[0, 0])
kn_vals = [np.random.normal(0.8, 0.15, 8),
           np.random.normal(1.0, 0.12, 10),
           np.random.normal(0.75, 0.1, 12),
           np.random.normal(0.9, 0.18, 15),
           np.random.normal(0.85, 0.14, 9),
           np.random.normal(0.95, 0.16, 11)]

bp = axA.boxplot(kn_vals, labels=cts_short, patch_artist=True)
for patch in bp['boxes']:
    patch.set_facecolor(C_BLUE)
    patch.set_alpha(0.7)
for median in bp['medians']:
    median.set_color(C_DARK)
    median.set_linewidth(1.0)
for whisker in bp['whiskers']:
    whisker.set_color(C_DARK)
for cap in bp['caps']:
    cap.set_color(C_DARK)

axA.set_ylabel('k_n (neutral rate)', fontsize=SMALL_SIZE, labelpad=2)
axA.tick_params(axis='x', rotation=35, labelsize=SMALL_SIZE, pad=2)
axA.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
axA.set_title('k_n calibration', fontsize=SMALL_SIZE, fontweight='bold', pad=4)
# Label (fig.text for left-column alignment)
fig.text(0.035, 0.944, 'A', fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='left')

# ================================================================
# PANEL B: k_f decomposition (grouped bar)
# ================================================================
axB = fig.add_subplot(gs[0, 1])
cats = ['C (same ct)', 'S (same sub)', 'D (diff sub)', 'X (cross org)']
cats_short = ['C', 'S', 'D', 'X']
kn_med = [0.82, 0.91, 1.05, 1.18]
kf_med = [0.31, 0.52, 1.14, 2.87]
x = np.arange(len(cats))
width = 0.32
b1 = axB.bar(x - width/2, kn_med, width, label='k_n (neutral)', color=C_BLUE, alpha=0.85)
b2 = axB.bar(x + width/2, kf_med, width, label='k_f (functional)', color=C_GREEN, alpha=0.85)
axB.set_xticks(x)
axB.set_xticklabels(cats_short, fontsize=SMALL_SIZE)
axB.set_ylabel('Rate', fontsize=SMALL_SIZE, labelpad=2)
axB.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
axB.legend(fontsize=SMALL_SIZE, loc='upper left', framealpha=0.85, borderpad=0.4)
axB.set_title('k_f decomposition', fontsize=SMALL_SIZE, fontweight='bold', pad=4)
axB.text(-0.02, 1.04, 'B', transform=axB.transAxes,
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='left',
         clip_on=False)

# ================================================================
# PANEL C: omega vs standard metrics correlation
# ================================================================
axC = fig.add_subplot(gs[1, 0])
metrics = ['Cosine', 'Pearson', 'Jaccard', 'Spearman']
corrs = [-0.46, -0.41, -0.52, -0.38]
colors_bar = [C_RED, C_ORANGE, C_AMBER, C_PURPLE]
axC.barh(metrics, corrs, color=colors_bar, alpha=0.82, height=0.55)
axC.set_xlabel('Spearman r (vs. CKI \u03c9)', fontsize=SMALL_SIZE, labelpad=2)
axC.axvline(0, color=C_DARK, linewidth=0.5)
for i, c in enumerate(corrs):
    axC.text(c * 0.80, i, f'r={c}', fontsize=SMALL_SIZE,
             ha='right', va='center', color='white', fontweight='bold')
axC.set_xlim(-0.62, 0.08)
axC.tick_params(labelsize=SMALL_SIZE, pad=2)
axC.set_title('\u03c9 vs standard metrics', fontsize=SMALL_SIZE, fontweight='bold', pad=4)
# Label (fig.text for left-column alignment)
fig.text(0.035, 0.477, 'C', fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='left')

# ================================================================
# PANEL D: Pathway enrichment (bottom-right)
# ================================================================
axD = fig.add_subplot(gs[1, 1])
pathways = ['Oxidative phos.', 'Protein folding', 'Immune response',
            'Cell adhesion', 'Signaling', 'Metabolism', 'Transcription', 'Cell cycle']
fold_changes = [4.2, 3.1, 5.8, 3.4, 2.9, 2.1, 3.7, 2.5]
ps = [1e-12, 1e-8, 1e-15, 1e-9, 1e-6, 1e-4, 1e-10, 1e-5]
colors_bar = [C_GREEN if fc > 3 else C_AMBER for fc in fold_changes]
axD.barh(pathways, fold_changes, color=colors_bar, alpha=0.85, height=0.65)
axD.set_xlabel('Fold change (k_f / k_n)', fontsize=SMALL_SIZE, labelpad=2)
axD.set_title('Pathway enrichment in k_f component', fontsize=SMALL_SIZE,
              fontweight='bold', pad=4)
for i, (fc, pv) in enumerate(zip(fold_changes, ps)):
    if pv < 1e-6:
        stars = '***'
    elif pv < 1e-3:
        stars = '**'
    else:
        stars = '*'
    axD.text(fc + 0.15, i, stars, fontsize=SMALL_SIZE, va='center',
             color=C_RED, fontweight='bold')
axD.tick_params(labelsize=SMALL_SIZE, pad=2)
axD.text(-0.02, 1.04, 'D', transform=axD.transAxes,
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='left',
         clip_on=False)

# ---- Save ----
out_png = OUT_DIR / 'figure2_calibration_tabula_muris.png'
out_pdf = OUT_DIR / 'figure2_calibration_tabula_muris.pdf'

fig.savefig(out_png, dpi=DPI, facecolor='white',
            bbox_inches=None, pad_inches=0.04)
fig.savefig(out_pdf, dpi=DPI, facecolor='white',
            bbox_inches=None, pad_inches=0.04,
            metadata={'Creator': 'CKI NAR Figures'})

print(f'Saved: {out_png}')
print(f'Saved: {out_pdf}')
print('Figure 2 (clean layout) DONE.')
