#!/usr/bin/env python3
"""Extended Data Figure 1: Parameter Sweep & Pathway Analysis — Clean layout for NAR submission.

Layout: 1x3 GridSpec (A/B/C horizontal)
Visual identity shared via notebooks/_fig_style.py (Arial, Type 42, >=7 pt).

v38 fix: all three panels now read from the authoritative results CSVs:
  - results/hk_stability_sweep.csv
  - results/figure_data_module_variance.csv
  - results/phase32_sweep_results.csv
Previously hardcoded/example values have been removed.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig_style as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

MM = st.MM
DOUBLE = st.DOUBLE
DPI = st.DPI
OUT_DIR = Path('results/figures_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

LABEL_SIZE = st.LABEL_SIZE
TITLE_SIZE = st.TITLE_SIZE
BODY_SIZE  = st.BODY_SIZE
SMALL_SIZE = st.SMALL_SIZE

ROOT = Path(__file__).resolve().parent.parent

# ---- Create figure ----
FIG_H = 100 * MM
print(f'ED Figure 1: {DOUBLE/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = st.new_figure(DOUBLE, FIG_H)

# GridSpec: 1 row x 3 columns
# wspace generous so panel-B colorbar never collides with panel-C title/labels
gs = gridspec.GridSpec(
    1, 3, fig,
    left=0.10, right=0.97, top=0.84, bottom=0.17,
    wspace=0.55,
)

# ================================================================
# PANEL A: k_n stability vs. HK gene set size
# ================================================================
axA = fig.add_subplot(gs[0, 0])
hk = pd.read_csv(ROOT / 'results/hk_stability_sweep.csv')
axA.fill_between(hk['n_hk'], hk['kn_mean'] - hk['kn_std'],
                 hk['kn_mean'] + hk['kn_std'],
                 color=st.C_BLUE, alpha=0.12, linewidth=0)
axA.errorbar(hk['n_hk'], hk['kn_mean'], yerr=hk['kn_std'], fmt='o-',
             color=st.C_BLUE, capsize=3, capthick=0.8, elinewidth=0.8,
             linewidth=1.3, markersize=4.5, markerfacecolor='white',
             markeredgecolor=st.C_BLUE, markeredgewidth=1.0)
axA.set_xlabel('Number of HK genes', fontsize=SMALL_SIZE, labelpad=2)
axA.set_ylabel('k_n (mean \u00b1 SD)', fontsize=SMALL_SIZE, labelpad=2)
axA.set_title('k_n stability vs. HK gene set size', fontsize=TITLE_SIZE,
             fontweight='bold', pad=6)
axA.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axA)
st.subtle_grid(axA, axis='y')
st.add_panel_label(fig, axA, 'A', axes_relative=False, x=0.035, y=0.875)

# ================================================================
# PANEL B: Module-level GSVA variance
# ================================================================
axB = fig.add_subplot(gs[0, 1])
mod = pd.read_csv(ROOT / 'results/figure_data_module_variance.csv')
mod = mod.sort_values('variance', ascending=False).reset_index(drop=True)
mod_labels = [f'M{i}' for i in mod['module']]
colors_b = [st.C_RED if i == 0 else st.C_BLUE for i in range(len(mod))]
bars = axB.bar(range(len(mod)), mod['variance'], color=colors_b,
               edgecolor='white', linewidth=0.4, alpha=0.85)
axB.set_xticks(range(len(mod)))
axB.set_xticklabels(mod_labels, rotation=45, ha='right', fontsize=SMALL_SIZE)
axB.set_xlabel('HVG-partition module', fontsize=SMALL_SIZE, labelpad=2)
axB.set_ylabel('Variance of GSVA score', fontsize=SMALL_SIZE, labelpad=2)
axB.set_title('Module-level enrichment variance', fontsize=TITLE_SIZE,
              fontweight='bold', pad=6)
axB.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axB)
st.subtle_grid(axB, axis='y')
axB.text(-0.02, 1.04, 'B', transform=axB.transAxes,
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='left',
         clip_on=False)

# ================================================================
# PANEL C: k_f weight sweep
# ================================================================
axC = fig.add_subplot(gs[0, 2])
sweep = pd.read_csv(ROOT / 'results/phase32_sweep_results.csv')
# Order from identity-only to pathway-only
order = ['identity_only', 'w1=0.8_w2=0.2', 'w1=0.5_w2=0.5',
         'w1=0.2_w2=0.8', 'pathway_only']
sweep['order'] = sweep['label'].apply(lambda x: order.index(x))
sweep = sweep.sort_values('order')
sweep_labels = ['Identity\nonly', '80/20', '50/50', '20/80', 'Pathway\nonly']
sweep_auc = sweep['auc'].values
colors_sweep = [st.C_RED if lab == 'identity_only' else st.C_LIGHT_BLUE
                for lab in sweep['label']]
axC.bar(sweep_labels, sweep_auc, color=colors_sweep, width=0.6,
        edgecolor=st.C_BLUE, linewidth=0.6, zorder=3)
for xi, a in enumerate(sweep_auc):
    axC.text(xi, a + 0.01, f'{a:.3f}', ha='center', va='bottom',
             fontsize=SMALL_SIZE, color=st.C_DARK)
axC.set_ylabel('AUC (cell-type classification)', fontsize=SMALL_SIZE, labelpad=2)
axC.set_title('Identity vs pathway weight sweep', fontsize=TITLE_SIZE,
              fontweight='bold', pad=6)
axC.set_ylim(0.3, 0.88)
axC.tick_params(axis='x', labelsize=SMALL_SIZE, pad=2)
axC.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
st.despine(axC)
st.subtle_grid(axC, axis='y')
axC.text(-0.02, 1.04, 'C', transform=axC.transAxes,
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='left',
         clip_on=False)

# ---- Caption ----
fig.text(0.5, 0.03,
         'Supplementary Figure S1. Parameter sweep and pathway analysis.',
         ha='center', fontsize=BODY_SIZE, fontweight='bold')

# ---- Save ----
out_png = OUT_DIR / 'ed_fig1_parameter_sweep_pathway.png'
out_pdf = OUT_DIR / 'ed_fig1_parameter_sweep_pathway.pdf'

fig.savefig(out_png, dpi=DPI, facecolor='white',
            bbox_inches=None, pad_inches=0.04)
fig.savefig(out_pdf, dpi=DPI, facecolor='white',
            bbox_inches=None, pad_inches=0.04,
            metadata={'Creator': 'CKI GB Supplementary Figures'})

print(f'Saved: {out_png}')
print(f'Saved: {out_pdf}')
print('Extended Data Figure 1 (clean layout) DONE.')
