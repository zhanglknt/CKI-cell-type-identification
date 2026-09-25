#!/usr/bin/env python3
"""Figure 3: Orthogonal Information — Clean layout for NAR submission.

Layout: 2×3 GridSpec (A/B/C top row, D/E bottom row, E spans 2 columns)
All fonts >= 7pt, panel labels 9pt bold, no tight_layout(), no bottom caption.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import _fig_style as st

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from sklearn.metrics import roc_curve, auc as _auc
from scipy.stats import spearmanr as _sp

# ---- Authoritative figure data ----
ROOT = Path(__file__).resolve().parent.parent
phase35 = pd.read_csv(ROOT / 'results/phase35_all_metrics_pairs.csv')
# ROC uses same_ct as the positive class; larger distance => different cell type,
# so we classify "diff-CT" (y=1) with the raw distances. This yields the AUCs
# stored in figure_data_auc.npy.
roc_y = (phase35['same_ct'] == 0).astype(int)
roc_scores = {
    'CKI \u03c9': phase35['omega'].values,
    'Cosine': phase35['cosine_dist'].values,
    'Raw JS': phase35['js_raw'].values,
    'Marker Jaccard': phase35['marker_jaccard_dist'].values,
    'Spearman': phase35['spearman_dist'].values,
}
roc_aucs = {m: _auc(*roc_curve(roc_y, s)[:2]) for m, s in roc_scores.items()}

# Correlation matrix for Panel A
corr_data = np.load(ROOT / 'results/figure_data_correlations.npy', allow_pickle=True).item()
corr_matrix = corr_data['corr_matrix']
metrics_3a = corr_data['metrics_3a']          # ['CKI \u03c9', 'Cosine', 'Raw JS', 'Marker Jaccard', 'Spearman']

# Categories for Panel D
phase35['category'] = 'X'
phase35.loc[phase35['same_ct'] & phase35['same_organ'], 'category'] = 'C'
phase35.loc[phase35['same_ct'] & ~phase35['same_organ'], 'category'] = 'S'
phase35.loc[~phase35['same_ct'] & phase35['same_organ'], 'category'] = 'D'

decomp_score = [1.0, 0.0, 0.0, 0.0, 0.0]      # CKI is the only fully decomposable metric

# ---- Shared constants (single source of truth: _fig_style) ----
MM = st.MM
DOUBLE = st.DOUBLE
DPI = st.DPI
OUT_DIR = Path('results/figures_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Colour palette (shared)
C_BLUE   = st.C_BLUE
C_GREEN  = st.C_GREEN
C_AMBER  = st.C_AMBER
C_RED    = st.C_RED
C_ORANGE = st.C_ORANGE
C_PURPLE = st.C_PURPLE
C_DARK   = st.C_DARK
C_LIGHT_BLUE = st.C_LIGHT_BLUE
C_LIGHT_GRAY = st.C_LIGHT_GRAY
C_GRAY   = st.C_GRAY

CAT_COLORS = {
    'C': C_BLUE,
    'S': C_GREEN,
    'D': C_AMBER,
    'X': C_RED,
}

LABEL_SIZE = st.LABEL_SIZE
TITLE_SIZE = st.TITLE_SIZE
BODY_SIZE  = st.BODY_SIZE
SMALL_SIZE = st.SMALL_SIZE

# Global style from the shared module
st.apply_style()

# ---- Create figure ----
FIG_H = 138 * MM
print(f'Figure 3: {DOUBLE/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = plt.figure(figsize=(DOUBLE, FIG_H), dpi=DPI)

# Outer GridSpec: 2 rows × 3 columns
gs = gridspec.GridSpec(
    2, 3, fig,
    height_ratios=[1.0, 1.15],
    left=0.10, right=0.97, top=0.93, bottom=0.08,
    hspace=0.48, wspace=0.34,
)

# ================================================================
# PANEL A: Correlation heatmap
# ================================================================
axA = fig.add_subplot(gs[0, 0])
metrics = metrics_3a
n = len(metrics)

# Draw heatmap manually for full control
im = axA.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
for i in range(n):
    for j in range(n):
        val = corr_matrix[i, j]
        color = 'white' if abs(val) > 0.55 else C_DARK
        axA.text(j, i, f'{val:.2f}', ha='center', va='center',
                 fontsize=SMALL_SIZE, color=color, fontweight='bold')
axA.set_xticks(range(n))
axA.set_xticklabels(metrics, rotation=30, fontsize=SMALL_SIZE)
axA.set_yticks(range(n))
axA.set_yticklabels(metrics, fontsize=SMALL_SIZE)
# Very light grid lines between cells for polish
axA.set_xticks(np.arange(-0.5, n, 1), minor=True)
axA.set_yticks(np.arange(-0.5, n, 1), minor=True)
axA.grid(which='minor', color='white', linewidth=0.6)
axA.tick_params(which='minor', size=0)
axA.set_title('Metric correlation', fontsize=TITLE_SIZE, fontweight='bold', pad=4)
# Label (fig.text for left-column alignment)
st.add_panel_label(fig, axA, 'A', axes_relative=False, x=0.035, y=0.944)

# ================================================================
# PANEL B: Scatter CKI ω vs k_n colored by same-organ / cross-organ
# ================================================================
axB = fig.add_subplot(gs[0, 1])
# Use reviewer_kf_kn_decomposition.csv because it contains per-pair k_n.
kk = pd.read_csv(ROOT / 'results/reviewer_kf_kn_decomposition.csv')
kk['same_organ'] = kk['organ_i'] == kk['organ_j']
r, p = _sp(kk['omega'], kk['kn'])
for same, c, lab in [(True, C_BLUE, 'Same organ'),
                       (False, C_RED, 'Cross organ')]:
    sub = kk[kk['same_organ'] == same]
    axB.scatter(sub['kn'], sub['omega'], c=c, s=10, alpha=0.35,
                label=lab, edgecolors='none')
axB.set_xlabel('Neutral divergence  $k_n$', fontsize=BODY_SIZE, labelpad=2)
axB.set_ylabel('CKI \u03c9', fontsize=BODY_SIZE, labelpad=2)
axB.set_title(f'Spearman r = {r:.3f}\n(P < 1e-10)',
              fontsize=BODY_SIZE, fontweight='bold', pad=8)
axB.legend(fontsize=SMALL_SIZE, loc='upper left', frameon=False,
           bbox_to_anchor=(0.02, 0.98), borderaxespad=0)
axB.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axB)
st.subtle_grid(axB, axis='both')
st.add_panel_label(fig, axB, 'B', x=-0.02, y=1.04)
# ================================================================
# PANEL C: ROC curves
# ================================================================
axC = fig.add_subplot(gs[0, 2])
roc_colors = [C_RED, C_BLUE, C_GREEN, C_AMBER, C_PURPLE]
for i, method in enumerate(metrics_3a):
    fpr, tpr, _ = roc_curve(roc_y, roc_scores[method])
    a = roc_aucs[method]
    axC.plot(fpr, tpr, label=f'{method} (AUC={a:.3f})',
              color=roc_colors[i], linewidth=1.3, alpha=0.9)
axC.plot([0, 1], [0, 1], 'k--', linewidth=0.8, alpha=0.5, label='Random')
axC.set_xlabel('False positive rate', fontsize=BODY_SIZE, labelpad=2)
axC.set_ylabel('True positive rate', fontsize=BODY_SIZE, labelpad=2)
axC.set_title('Cell-type classification', fontsize=TITLE_SIZE,
              fontweight='bold', pad=4)
axC.legend(fontsize=SMALL_SIZE, loc='lower right', frameon=False,
           ncol=2, columnspacing=0.8, labelspacing=0.25,
           handlelength=1.4, handletextpad=0.4)
axC.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axC)
st.subtle_grid(axC, axis='both')
st.add_panel_label(fig, axC, 'C', x=-0.02, y=1.04)

# ================================================================
# PANEL D: log10(ω) distribution by category
# ================================================================
axD = fig.add_subplot(gs[1, 0])
cats_short = ['S', 'D', 'X']
cat_data = [np.log10(phase35.loc[phase35['category'] == cat, 'omega'].values)
            for cat in cats_short]
bp = axD.boxplot(cat_data, labels=cats_short, patch_artist=True,
                  showfliers=False, widths=0.55)
for patch, cat in zip(bp['boxes'], cats_short):
    patch.set_facecolor(CAT_COLORS[cat])
    patch.set_edgecolor(C_DARK)
    patch.set_linewidth(0.6)
    patch.set_alpha(0.8)
for median in bp['medians']:
    median.set_color('white')
    median.set_linewidth(1.2)
for whisker in bp['whiskers']:
    whisker.set_color(C_GRAY)
    whisker.set_linewidth(0.8)
for cap in bp['caps']:
    cap.set_color(C_GRAY)
    cap.set_linewidth(0.8)
axD.set_xlabel('Category', fontsize=BODY_SIZE, labelpad=2)
axD.set_ylabel('$\\log_{10}$ CKI \u03c9', fontsize=BODY_SIZE, labelpad=2)
axD.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axD)
st.subtle_grid(axD)
st.add_panel_label(fig, axD, 'D', axes_relative=False, x=0.035, y=0.455)

# ================================================================
# PANEL E: Metric comparison — classification AUC and decomposability
# ================================================================
axE = fig.add_subplot(gs[1, 1:])
method_names = metrics_3a
auc_vals = [roc_aucs[m] for m in method_names]
x = np.arange(len(method_names))
width = 0.32
b1 = axE.bar(x - width / 2, auc_vals, width, label='Classification AUC',
             color=C_BLUE, edgecolor=C_DARK, linewidth=0.4, alpha=0.85)
b2 = axE.bar(x + width / 2, decomp_score, width, label='Fully decomposable',
             color=C_GREEN, edgecolor=C_DARK, linewidth=0.4, alpha=0.85)
for bar, v in zip(b1, auc_vals):
    axE.text(bar.get_x() + bar.get_width()/2, v + 0.015,
             f'{v:.3f}', ha='center', fontsize=SMALL_SIZE, fontweight='bold')
axE.set_xticks(x)
axE.set_xticklabels(method_names, rotation=20, fontsize=SMALL_SIZE)
axE.set_ylabel('Score', fontsize=BODY_SIZE, labelpad=2)
axE.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
axE.legend(fontsize=SMALL_SIZE, loc='upper right', frameon=False)
axE.set_title('Method comparison', fontsize=TITLE_SIZE, fontweight='bold', pad=4)
axE.set_ylim(0, 1.08)
st.despine(axE)
st.subtle_grid(axE)
# Label (fig.text at E panel left edge, same row as D)
st.add_panel_label(fig, axE, 'E', axes_relative=False, x=0.395, y=0.455)

# ---- Save ----
written = st.save_fig(fig, 'figure3_orthogonal_information')
for p in written:
    print(f'Saved: {p}')
print('Figure 3 (clean layout) DONE.')
