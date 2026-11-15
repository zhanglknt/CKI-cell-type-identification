#!/usr/bin/env python3
"""Regenerate NC Figure 2 top row (panels A-C) at native 178 mm width.

Reason: the first-author figure2.pdf was designed at 234.7 mm width; scaled
to the 178 mm double column its inner text drops to ~5.5 pt effective, below
the NC 7 pt floor.  This script rebuilds the three panels from the source
data (results/mouse_pilot_v2_results.csv) with Arial >= 7 pt throughout,
Type 42 embedded fonts, 9 pt bold panel labels.

Output: results/figures_submission_nc/_fig2_toprow_nc49.pdf (+ .png preview)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, 'notebooks')

import _fig_style as st

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

MM = st.MM
DPI = st.DPI
OUT = Path('results/figures_final')
OUT.mkdir(parents=True, exist_ok=True)

st.apply_style()
# NC strict: mathtext must also be Arial (default DejaVu violates the
# Arial/Helvetica rule); sub/superscripts then stay in the Arial family.
matplotlib.rcParams.update({
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial:italic',
    'mathtext.bf': 'Arial:bold',
    'mathtext.default': 'regular',
})

# ---------------------------------------------------------------- data ----
mp = pd.read_csv('results/mouse_pilot_v2_results.csv')
cat_keys = {'C': 'C_control', 'S': 'S_same_ct', 'D': 'D_diff_ct', 'X': 'X_cross'}
cats = ['C', 'S', 'D', 'X']
grp = mp.groupby('category')
ctrl = mp[mp['category'] == 'C_control'].reset_index(drop=True)
ctrl_ct = [c.split(':')[-1].split('(')[0].strip() for c in ctrl['comparison']]
ctrl_org = [c.split('(')[-1].rstrip(')').strip() for c in ctrl['comparison']]
ctrl_names = [f'{ct}\n({org})' for ct, org in zip(ctrl_ct, ctrl_org)]
kn_vals = ctrl['kn'].to_numpy() * 1e4
kn_mean = kn_vals.mean()
kn_cv = ctrl['kn'].std() / ctrl['kn'].mean() * 100

kn_med = [grp.get_group(cat_keys[c])['kn'].mean() for c in cats]
kf_med = [grp.get_group(cat_keys[c])['kf'].mean() for c in cats]
n_per = [len(grp.get_group(cat_keys[c])) for c in cats]
omega_by_cat = [grp.get_group(cat_keys[c])['omega'].to_numpy() for c in cats]
u_stat, p_val = stats.mannwhitneyu(omega_by_cat[3], omega_by_cat[0],
                                   alternative='greater')

# --------------------------------------------------------------- figure ---
FIG_W = 178 * MM
FIG_H = 74 * MM
fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
gs = gridspec.GridSpec(1, 3, fig, left=0.055, right=0.99, top=0.86,
                       bottom=0.24, wspace=0.38, width_ratios=[1.35, 1.0, 1.0])

SMALL = st.SMALL_SIZE   # 7
BODY = st.BODY_SIZE     # 8
TITLE = st.TITLE_SIZE   # 9

# ---- Panel A: k_n calibration ---------------------------------------------
axA = fig.add_subplot(gs[0, 0])
axA.bar(np.arange(len(ctrl)), kn_vals, width=0.62,
        color=st.C_LIGHT_BLUE, edgecolor=st.C_BLUE, linewidth=0.7, alpha=0.9)
axA.axhline(kn_mean, color=st.C_RED, linestyle='--', linewidth=1.0)
axA.text(0.97, 0.96, f'k$_n$ mean = {kn_mean:.2f} (\u00d710$^{{-4}}$)\n'
                     f'k$_n$ CV = {kn_cv:.0f}% (n=6)',
         transform=axA.transAxes, fontsize=SMALL, va='top', ha='right',
         color=st.C_RED)
axA.set_xticks(np.arange(len(ctrl)))
axA.set_xticklabels(ctrl_names, fontsize=SMALL, rotation=42, ha='right',
                    rotation_mode='anchor')
axA.set_ylabel('k$_n$ (\u00d710$^{-4}$)', fontsize=BODY, labelpad=2)
axA.tick_params(axis='y', labelsize=SMALL, pad=2)
axA.set_ylim(0, 4.6)
axA.set_title('k$_n$ calibration (split-half controls)', fontsize=TITLE,
              fontweight='bold', pad=4)
st.despine(axA)
st.subtle_grid(axA)
st.add_panel_label(fig, axA, 'A', axes_relative=False, x=0.012, y=0.935)

# ---- Panel B: k_n / k_f decomposition --------------------------------------
axB = fig.add_subplot(gs[0, 1])
x = np.arange(len(cats))
width = 0.32
axB.bar(x - width / 2, kn_med, width, label='k$_n$ (neutral)',
        color=st.C_BLUE, edgecolor=st.C_DARK, linewidth=0.4, alpha=0.85)
axB.bar(x + width / 2, kf_med, width, label='k$_f$ (functional)',
        color=st.C_GREEN, edgecolor=st.C_DARK, linewidth=0.4, alpha=0.85)
axB.set_yscale('log')
axB.set_xticks(x)
axB.set_xticklabels([f'{c}\n(n={n})' for c, n in zip(cats, n_per)],
                    fontsize=SMALL)
axB.set_ylabel('Rate (JS divergence, log)', fontsize=BODY, labelpad=2)
axB.tick_params(axis='y', labelsize=SMALL, pad=2)
axB.legend(fontsize=SMALL, loc='upper left', frameon=False)
for xi, kv, fv in zip(x, kn_med, kf_med):
    axB.text(xi - width / 2, kv * 1.35, f'{kv:.1e}', fontsize=SMALL,
             ha='center', va='bottom', color=st.C_BLUE)
    axB.text(xi + width / 2, fv * 1.35, f'{fv:.1e}', fontsize=SMALL,
             ha='center', va='bottom', color=st.C_DARK)
axB.set_ylim(None, max(kf_med) * 24)
axB.set_title('k$_n$ / k$_f$ decomposition', fontsize=TITLE,
              fontweight='bold', pad=4)
st.despine(axB)
st.subtle_grid(axB)
st.add_panel_label(fig, axB, 'B', x=-0.06, y=1.04)

# ---- Panel C: omega by category --------------------------------------------
axC = fig.add_subplot(gs[0, 2])
bp = axC.boxplot(omega_by_cat, labels=cats, patch_artist=True,
                 showfliers=True, flierprops=dict(marker='o', markersize=2.5,
                                                  markerfacecolor=st.C_GRAY,
                                                  markeredgecolor=st.C_DARK,
                                                  alpha=0.6))
box_cols = [st.C_BLUE, st.C_GREEN, st.C_AMBER, st.C_RED]
for patch, col in zip(bp['boxes'], box_cols):
    patch.set_facecolor(col); patch.set_alpha(0.55)
    patch.set_edgecolor(st.C_DARK); patch.set_linewidth(0.7)
for median in bp['medians']:
    median.set_color(st.C_DARK); median.set_linewidth(1.2)
for whisker in bp['whiskers']:
    whisker.set_color(st.C_GRAY); whisker.set_linewidth(0.8)
for cap in bp['caps']:
    cap.set_color(st.C_GRAY); cap.set_linewidth(0.8)
axC.set_yscale('log')
axC.set_ylabel('\u03c9 (log scale)', fontsize=BODY, labelpad=2)
axC.tick_params(labelsize=SMALL, pad=2)
axC.set_title('\u03c9 by category (mouse pilot)', fontsize=TITLE,
              fontweight='bold', pad=4)
axC.text(0.03, 0.04, f'X vs. C one-sided Mann-Whitney\nP = {p_val:.3f}',
         transform=axC.transAxes, fontsize=SMALL, va='bottom', ha='left',
         color=st.C_DARK,
         bbox=dict(facecolor='white', edgecolor=st.C_LIGHT_GRAY,
                   linewidth=0.5, alpha=0.85))
st.despine(axC)
st.subtle_grid(axC, axis='x')
st.add_panel_label(fig, axC, 'C', x=-0.16, y=1.04)

# ------------------------------------------------------------------ save ---
pdf = OUT / '_fig2_toprow_nc49.pdf'
png = OUT / '_fig2_toprow_nc49.png'
fig.savefig(pdf, dpi=DPI, facecolor='white', metadata={'Creator': 'CKI NC Figures'})
fig.savefig(png, dpi=DPI, facecolor='white')
print(f'Saved: {pdf}')
print(f'Saved: {png}')
print(f'Panel A: kn mean = {kn_mean:.2f}e-4, CV = {kn_cv:.0f}% (n=6)')
print('Panel B: kn =', [f'{v:.1e}' for v in kn_med], 'kf =', [f'{v:.1e}' for v in kf_med])
print(f'Panel C: X vs C Mann-Whitney P = {p_val:.3f}')
print('DONE.')
