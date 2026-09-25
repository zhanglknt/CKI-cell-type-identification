#!/usr/bin/env python3
"""Figure 2: Tabula Muris Calibration — Clean layout for NAR submission.

Layout: 2×2 GridSpec (A/B top row, C/D bottom row)
All fonts >= 7pt, panel labels 9pt bold, no tight_layout().
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import _fig_style as st

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ---- Shared constants (single source of truth: _fig_style) ----
MM = st.MM
DOUBLE = st.DOUBLE
DPI = st.DPI
OUT_DIR = Path('results/figures_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_DIR = Path('results')

# Colour palette (shared)
C_BLUE   = st.C_BLUE
C_GREEN  = st.C_GREEN
C_AMBER  = st.C_AMBER
C_RED    = st.C_RED
C_ORANGE = st.C_ORANGE
C_PURPLE = st.C_PURPLE
C_TEAL   = st.C_TEAL
C_GRAY   = st.C_GRAY
C_ORANGE2= st.C_ORANGE2
C_STEEL  = st.C_STEEL
C_DARK   = st.C_DARK
C_LIGHT_GRAY = st.C_LIGHT_GRAY
C_LIGHT_BLUE = st.C_LIGHT_BLUE

LABEL_SIZE = st.LABEL_SIZE
TITLE_SIZE = st.TITLE_SIZE
BODY_SIZE  = st.BODY_SIZE
SMALL_SIZE = st.SMALL_SIZE

# Global style from the shared module
st.apply_style()

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

# ---- Data: mouse pilot (results/mouse_pilot_v2_results.csv) ----
mp = pd.read_csv(RESULTS_DIR / 'mouse_pilot_v2_results.csv')
ctrl = mp[mp['category'] == 'C_control'].reset_index(drop=True)   # 6 controls
ctrl_labels = [c.split('(')[-1].rstrip(')').strip() for c in ctrl['comparison']]
ctrl_ct = [c.split(':')[-1].split('(')[0].strip() for c in ctrl['comparison']]
ctrl_names = [f'{ct}\n({org})' for ct, org in zip(ctrl_ct, ctrl_labels)]
print(f'Mouse pilot: {len(mp)} pairs; {len(ctrl)} C controls; '
      f'kn CV across controls = {ctrl["kn"].std()/ctrl["kn"].mean()*100:.1f}%')

# ================================================================
# PANEL A: k_n calibration (six split-half controls)
# ================================================================
axA = fig.add_subplot(gs[0, 0])
kn_vals = ctrl['kn'].to_numpy() * 1e4   # in units of 1e-4
bars = axA.bar(np.arange(len(ctrl)), kn_vals, width=0.62,
               color=C_LIGHT_BLUE, edgecolor=C_BLUE, linewidth=0.7, alpha=0.9)
kn_mean = kn_vals.mean()
axA.axhline(kn_mean, color=C_RED, linestyle='--', linewidth=1.0,
            label=f'Mean = {kn_mean:.2f}\n(CV = {ctrl["kn"].std()/ctrl["kn"].mean()*100:.0f}%)')
axA.set_xticks(np.arange(len(ctrl)))
axA.set_xticklabels(ctrl_names, fontsize=SMALL_SIZE, rotation=30,
                    ha='right')
axA.set_ylabel('k_n (\u00d710\u207b\u2074)', fontsize=BODY_SIZE, labelpad=2)
axA.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
axA.legend(fontsize=SMALL_SIZE, loc='upper right', frameon=False)
axA.set_title('k_n calibration (split-half controls)', fontsize=TITLE_SIZE,
              fontweight='bold', pad=4)
st.despine(axA)
st.subtle_grid(axA)
# Label (fig.text for left-column alignment)
st.add_panel_label(fig, axA, 'A', axes_relative=False, x=0.035, y=0.944)

# ================================================================
# PANEL B: k_n / k_f decomposition by comparison category
# ================================================================
axB = fig.add_subplot(gs[0, 1])
cats = ['C', 'S', 'D', 'X']
cat_keys = {'C': 'C_control', 'S': 'S_same_ct', 'D': 'D_diff_ct', 'X': 'X_cross'}
grp = mp.groupby('category')
kn_med = [grp.get_group(cat_keys[c])['kn'].mean() for c in cats]
kf_med = [grp.get_group(cat_keys[c])['kf'].mean() for c in cats]
n_per = [len(grp.get_group(cat_keys[c])) for c in cats]
print('Panel B category means: kn =', [f'{v:.2e}' for v in kn_med],
      'kf =', [f'{v:.2e}' for v in kf_med], 'n =', n_per)
x = np.arange(len(cats))
width = 0.32
b1 = axB.bar(x - width/2, kn_med, width, label='k_n (neutral)',
             color=C_BLUE, edgecolor=C_DARK, linewidth=0.4, alpha=0.85)
b2 = axB.bar(x + width/2, kf_med, width, label='k_f (functional)',
             color=C_GREEN, edgecolor=C_DARK, linewidth=0.4, alpha=0.85)
axB.set_yscale('log')
axB.set_xticks(x)
axB.set_xticklabels([f'{c}\n(n={n})' for c, n in zip(cats, n_per)],
                    fontsize=SMALL_SIZE)
axB.set_ylabel('Rate (JS divergence, log)', fontsize=BODY_SIZE, labelpad=2)
axB.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
axB.legend(fontsize=SMALL_SIZE, loc='upper left', frameon=False)
for xi, kv, fv in zip(x, kn_med, kf_med):
    axB.text(xi - width/2, kv * 1.35, f'{kv:.1e}', fontsize=SMALL_SIZE,
             ha='center', va='bottom', color=C_BLUE)
    axB.text(xi + width/2, fv * 1.35, f'{fv:.1e}', fontsize=SMALL_SIZE,
             ha='center', va='bottom', color=C_DARK)
axB.set_ylim(None, max(kf_med) * 12)
axB.set_title('k_n / k_f decomposition', fontsize=TITLE_SIZE,
              fontweight='bold', pad=4)
st.despine(axB)
st.subtle_grid(axB)
st.add_panel_label(fig, axB, 'B', x=-0.02, y=1.04)

# ================================================================
# PANEL C: omega vs standard metrics correlation
# (authoritative values: results/figure_data_correlations.npy, corrs_2c)
# ================================================================
axC = fig.add_subplot(gs[1, 0])
corr_data = np.load(RESULTS_DIR / 'figure_data_correlations.npy',
                    allow_pickle=True).item()
metrics = list(corr_data['metrics_2c'])          # Cosine, Raw JS, Marker Jaccard, Spearman
corrs = list(corr_data['corrs_2c'])              # -0.386, -0.396, -0.358, -0.461
colors_bar = [C_RED, C_ORANGE, C_AMBER, C_PURPLE]
bars = axC.barh(metrics, corrs, color=colors_bar, alpha=0.85,
                height=0.55, edgecolor=C_DARK, linewidth=0.4)
axC.set_xlabel('Spearman r (vs. CKI \u03c9)', fontsize=BODY_SIZE, labelpad=2)
axC.axvline(0, color=C_DARK, linewidth=0.5)
for i, c in enumerate(corrs):
    axC.text(c - 0.02, i, f'r={c:.2f}', fontsize=SMALL_SIZE,
             ha='right', va='center', color='white', fontweight='bold')
axC.set_xlim(-0.62, 0.08)
axC.tick_params(labelsize=SMALL_SIZE, pad=2)
axC.set_title('\u03c9 vs standard metrics', fontsize=TITLE_SIZE, fontweight='bold', pad=4)
st.despine(axC)
st.subtle_grid(axC, axis='x')
# Label (fig.text for left-column alignment)
st.add_panel_label(fig, axC, 'C', axes_relative=False, x=0.035, y=0.477)

# ================================================================
# PANEL D: omega distribution by comparison category (mouse pilot)
# ================================================================
axD = fig.add_subplot(gs[1, 1])
omega_by_cat = [grp.get_group(cat_keys[c])['omega'].to_numpy() for c in cats]
bp = axD.boxplot(omega_by_cat, labels=cats, patch_artist=True,
                 showfliers=True, flierprops=dict(marker='o', markersize=2.5,
                                                   markerfacecolor=C_GRAY,
                                                   markeredgecolor=C_DARK,
                                                   alpha=0.6))
box_cols = [C_BLUE, C_GREEN, C_AMBER, C_RED]
for patch, col in zip(bp['boxes'], box_cols):
    patch.set_facecolor(col); patch.set_alpha(0.55)
    patch.set_edgecolor(C_DARK); patch.set_linewidth(0.7)
for median in bp['medians']:
    median.set_color(C_DARK); median.set_linewidth(1.2)
for whisker in bp['whiskers']:
    whisker.set_color(C_GRAY); whisker.set_linewidth(0.8)
for cap in bp['caps']:
    cap.set_color(C_GRAY); cap.set_linewidth(0.8)
axD.set_yscale('log')
axD.set_ylabel('\u03c9 (log scale)', fontsize=BODY_SIZE, labelpad=2)
axD.tick_params(labelsize=SMALL_SIZE, pad=2)
# X vs C one-sided Mann-Whitney (H1: omega_X > omega_C)
u_stat, p_val = stats.mannwhitneyu(omega_by_cat[3], omega_by_cat[0],
                                   alternative='greater')
axD.set_title('\u03c9 by category (mouse pilot)', fontsize=TITLE_SIZE,
              fontweight='bold', pad=4)
axD.text(0.03, 0.95, f'X vs. C one-sided Mann-Whitney\nP = {p_val:.3f}',
         transform=axD.transAxes, fontsize=SMALL_SIZE, va='top', ha='left',
         color=C_DARK,
         bbox=dict(facecolor='white', edgecolor=C_LIGHT_GRAY,
                   linewidth=0.5, alpha=0.85))
print(f'Panel D: X vs C Mann-Whitney U = {u_stat:.1f}, P = {p_val:.4f}')
st.despine(axD)
st.subtle_grid(axD, axis='x')
st.add_panel_label(fig, axD, 'D', x=-0.02, y=1.04)

# ---- Save ----
written = st.save_fig(fig, 'figure2_calibration_tabula_muris')
for p in written:
    print(f'Saved: {p}')
print('Figure 2 (clean layout) DONE.')
