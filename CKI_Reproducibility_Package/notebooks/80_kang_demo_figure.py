#!/usr/bin/env python3
"""Generate Supplementary Figure S13: Kang et al. IFN-beta PBMC demonstration.

Two panels (double column):
  (A) AUC for separating perturbation pairs (stim-vs-ctrl) from donor-drift
      pairs (donor-vs-donor), per cell type, for omega / k_f / raw JS.
      Shows the anchor-visibility boundary: where IFN-beta moves the HK anchor
      hardest (CD14+ monocytes), the omega AUC collapses (0.55) while k_f
      retains discrimination (0.98).
  (B) Median k_n by comparison class (split-half < donor-donor < stim-vs-ctrl),
      log scale, per cell type — IFN-beta raises k_n itself 1.2-5.7-fold above
      the donor-drift level.

Data: results/kang_ifnb_demo_summary.json, results/kang_ifnb_demo_pairs.csv
(output of notebooks/79_kang_ifnb_demo.py; GSE96583, Kang et al. 2018).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _fig_style as st

import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'results'
OUT_DIR = DATA_DIR / 'figures_final'
OUT_DIR.mkdir(parents=True, exist_ok=True)

MM = 1 / 25.4
DOUBLE = 178 * MM
DPI = 300

# ---- Load data ----
with open(DATA_DIR / 'kang_ifnb_demo_summary.json') as fh:
    summary = json.load(fh)
pairs = pd.read_csv(DATA_DIR / 'kang_ifnb_demo_pairs.csv')

ct_info = summary['cell_types']
# Order cell types by k_n ratio (stim/ctrl vs donor-donor), descending
order = sorted(
    ct_info,
    key=lambda ct: -(
        pairs[(pairs.cell_type == ct) & (pairs.comparison == 'stim_vs_ctrl')]['k_n'].median()
        / pairs[(pairs.cell_type == ct) & (pairs.comparison.str.startswith('donor'))]['k_n'].median()
    ),
)
short_names = {
    'CD14+ Monocytes': 'CD14+ Mono',
    'FCGR3A+ Monocytes': 'FCGR3A+ Mono',
    'B cells': 'B cells',
    'NK cells': 'NK cells',
    'CD4 T cells': 'CD4 T',
    'CD8 T cells': 'CD8 T',
}
labels = [short_names.get(ct, ct) for ct in order]

# ---- Figure ----
st.apply_style()
fig, (axA, axB) = plt.subplots(1, 2, figsize=(DOUBLE, 2.9))

# ============================================================
# Panel A: AUC per cell type (omega / k_f / raw JS)
# ============================================================
y = np.arange(len(order))[::-1]  # top = largest k_n ratio
auc_omega = [ct_info[ct]['auc_omega'] for ct in order]
auc_kf = [ct_info[ct]['auc_kf'] for ct in order]
auc_raw = [ct_info[ct]['auc_raw_js'] for ct in order]

h = 0.26
base = 0.5
axA.barh(y + h, [v - base for v in auc_omega], left=base, height=h,
         color=st.C_BLUE, label='ω', zorder=3)
axA.barh(y, [v - base for v in auc_kf], left=base, height=h,
         color=st.C_GREEN, label=r'$k_f$ only', zorder=3)
axA.barh(y - h, [v - base for v in auc_raw], left=base, height=h,
         color=st.C_LIGHT_GRAY, edgecolor=st.C_GRAY,
         linewidth=0.5, label='raw JS', zorder=3)

# Value labels on the omega bars (the anchor-visibility story)
for yi, v in zip(y + h, auc_omega):
    axA.text(min(v + 0.008, 1.015), yi, f'{v:.2f}', va='center', ha='left',
             fontsize=7, color=st.C_BLUE)

axA.set_yticks(y)
axA.set_yticklabels(labels)
axA.set_xlim(0.5, 1.06)
axA.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
axA.axvline(0.5, color=st.C_DARK, lw=0.6, ls=':')
axA.set_xlabel('AUC: perturbation vs. donor drift')
axA.set_title('Separation of IFN-β effect from donor drift', loc='left',
              fontsize=9, fontweight='bold', pad=8)
axA.legend(fontsize=7, loc='lower right', frameon=False)
st.despine(axA)
st.subtle_grid(axA, axis='x')

# ============================================================
# Panel B: median k_n by comparison class (log scale)
# ============================================================
x = np.arange(len(order))
w = 0.34
kn_donor = [pairs[(pairs.cell_type == ct) & (pairs.comparison.str.startswith('donor'))]['k_n'].median() for ct in order]
kn_stim = [pairs[(pairs.cell_type == ct) & (pairs.comparison == 'stim_vs_ctrl')]['k_n'].median() for ct in order]

axB.bar(x - w / 2, kn_donor, width=w, color=st.C_STEEL, label='donor drift', zorder=3)
axB.bar(x + w / 2, kn_stim, width=w, color=st.C_RED, label='IFN-β stim', zorder=3)

# Ratio annotations (stim / donor), kept inside the axes
for xi, ks, kd in zip(x, kn_stim, kn_donor):
    axB.text(xi + w / 2, ks * 1.15, f'{ks / kd:.1f}×', ha='center', va='bottom',
             fontsize=7, color=st.C_RED)

axB.set_yscale('log')
axB.set_xticks(x)
axB.set_xticklabels(labels, rotation=38, ha='right')
axB.set_ylabel('median $k_n$ (JS, HK genes)')
axB.set_title('IFN-β raises the HK anchor itself', loc='left',
              fontsize=9, fontweight='bold', pad=8)
axB.legend(fontsize=7, frameon=False, loc='lower left')
axB.set_ylim(1.4e-3, 5e-2)
axB.set_yticks([2e-3, 5e-3, 1e-2, 2e-2])
st.despine(axB)
st.subtle_grid(axB, axis='y')

st.add_panel_label(fig, axA, 'A')
st.add_panel_label(fig, axB, 'B')
fig.subplots_adjust(left=0.125, right=0.985, bottom=0.26, top=0.87, wspace=0.38)

st.save_fig(fig, 'Supplementary_Figure_S13', out_dir=str(OUT_DIR))
print('Saved Supplementary_Figure_S13 (pdf + png) to', OUT_DIR)
