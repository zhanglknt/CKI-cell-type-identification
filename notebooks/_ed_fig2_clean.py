#!/usr/bin/env python3
"""Extended Data Figure 2 (Supplementary Figure S2): Cross-Species Validation.

Layout: 1x3 GridSpec (A/B/C horizontal)
Visual identity shared via notebooks/_fig_style.py (Arial, Type 42, >=7 pt).

v38 fix: all panels now use real data (no synthetic values):
  - Panel A: per-cell-type mean omega for the 15 shared cell types between
    Tabula Muris (results/full_matrix_pairs.csv) and Tabula Sapiens
    (results/phase35_all_metrics_pairs.csv). Mouse labels are un-aliased with
    the reverse of the label-shortening map in 03_full_matrix.py
    ('liver sinusoid EC' -> 'endothelial cell of hepatic sinusoid',
     'cardiac muscle' -> 'cardiac muscle cell').
  - Panel B: HK gene set detection stability from
    results/hk_overlap_subsamples.csv (produced by 01c_hk_overlap.py).
  - Panel C: omega distribution comparison, mouse (n = 15 shared cell-type
    means) vs. human (n = 4,851 pairs from phase35_all_metrics_pairs.csv).
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
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings('ignore')

MM = st.MM
DOUBLE = st.DOUBLE
DPI = st.DPI
OUT_DIR = Path('results/figures_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESDIR = Path('results')

LABEL_SIZE = st.LABEL_SIZE
TITLE_SIZE = st.TITLE_SIZE
BODY_SIZE  = st.BODY_SIZE
SMALL_SIZE = st.SMALL_SIZE

# ---- Create figure ----
FIG_H = 100 * MM
print(f'ED Figure 2: {DOUBLE/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = st.new_figure(DOUBLE, FIG_H)

# GridSpec: 1 row x 3 columns
gs = gridspec.GridSpec(
    1, 3, fig,
    left=0.09, right=0.97, top=0.84, bottom=0.17,
    wspace=0.45,
)

# ================================================================
# Load real data
# ================================================================
def parse_pair_ct(p):
    left, right = p.split(' vs ', 1)
    return left.split('|', 1)[1], right.split('|', 1)[1]

# Reverse of the label-shortening map in 03_full_matrix.py (lines 196-198)
MOUSE_ALIAS = {
    'liver sinusoid EC': 'endothelial cell of hepatic sinusoid',
    'cardiac muscle': 'cardiac muscle cell',
}

mouse_pairs = pd.read_csv(RESDIR / 'full_matrix_pairs.csv')
mouse_ct_omega = {}
for _, r in mouse_pairs.iterrows():
    a, b = parse_pair_ct(r['pair'])
    for ct in (a, b):
        ct = MOUSE_ALIAS.get(ct, ct)
        mouse_ct_omega.setdefault(ct, []).append(r['omega'])
mouse_ct_mean = {ct: float(np.mean(v)) for ct, v in mouse_ct_omega.items()}

human_pairs = pd.read_csv(RESDIR / 'phase35_all_metrics_pairs.csv')
human_ct_omega = {}
for _, r in human_pairs.iterrows():
    human_ct_omega.setdefault(r['ct_i'], []).append(r['omega'])
    human_ct_omega.setdefault(r['ct_j'], []).append(r['omega'])
human_ct_mean = {ct: float(np.mean(v)) for ct, v in human_ct_omega.items()}

# Case-insensitive matching (mouse labels use title case, human lowercase)
m_ci = {ct.lower(): (ct, v) for ct, v in mouse_ct_mean.items()}
h_ci = {ct.lower(): (ct, v) for ct, v in human_ct_mean.items()}
shared_keys = sorted(set(m_ci) & set(h_ci), key=str.lower)
shared_cts = [m_ci[k][0] for k in shared_keys]
mouse_vals = [m_ci[k][1] for k in shared_keys]
human_vals = [h_ci[k][1] for k in shared_keys]
print(f'  shared cell types: n = {len(shared_cts)}')

# ================================================================
# PANEL A: Mouse vs. Human per-CT mean omega (shared cell types)
# ================================================================
axA = fig.add_subplot(gs[0, 0])
r_sp, p_sp = spearmanr(mouse_vals, human_vals)
print(f'  Spearman r = {r_sp:.2f}, P = {p_sp:.2e}')
axA.scatter(mouse_vals, human_vals, c=st.C_PURPLE, s=22, alpha=0.8,
            edgecolors='none', zorder=3)
for i, ct in enumerate(shared_cts):
    axA.annotate(ct[:14], (mouse_vals[i], human_vals[i]),
                 textcoords='offset points', xytext=(3, 2),
                 fontsize=5.5, color=st.C_DARK, alpha=0.75)
axA.set_xlabel('Mean CKI \u03c9 (mouse, Tabula Muris)', fontsize=SMALL_SIZE, labelpad=2)
axA.set_ylabel('Mean CKI \u03c9 (human, Tabula Sapiens)', fontsize=SMALL_SIZE, labelpad=2)
axA.set_title(f'Shared cell types (n = {len(shared_cts)}): '
              f'r = {r_sp:.2f}, P = {p_sp:.2f}',
              fontsize=TITLE_SIZE, fontweight='bold', pad=6)
axA.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axA)
st.subtle_grid(axA, axis='both')
st.add_panel_label(fig, axA, 'A', axes_relative=False, x=0.035, y=0.875)

# ================================================================
# PANEL B: HK gene set detection stability (real data)
# ================================================================
axB = fig.add_subplot(gs[0, 1])
hk_ov = pd.read_csv(RESDIR / 'hk_overlap_subsamples.csv')
hk_labels = [str(s).replace('Subset', 'Set') for s in hk_ov['subset']]
hk_overlap = hk_ov['overlap_pct'].astype(float).tolist()
print('  HK overlap with HRT Atlas: ' + ', '.join(f'{v:.1f}' for v in hk_overlap))
axB.bar(hk_labels, hk_overlap, color=st.C_GREEN, alpha=0.9, width=0.6,
        edgecolor=st.C_DARK, linewidth=0.4, zorder=3)
mean_ov = float(np.mean(hk_overlap))
axB.axhline(mean_ov, color=st.C_GRAY, linestyle='--', linewidth=0.8, zorder=2)
axB.text(4.4, mean_ov + 1.0, f'{mean_ov:.1f}%', ha='right', va='bottom',
         fontsize=SMALL_SIZE, color=st.C_GRAY)
axB.set_ylim(0, 100)
axB.set_ylabel('Overlap with HRT Atlas (%)', fontsize=SMALL_SIZE, labelpad=2)
axB.set_title('HK gene set detection stability', fontsize=TITLE_SIZE,
              fontweight='bold', pad=6)
axB.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axB)
st.subtle_grid(axB, axis='y')
# Panel B label via fig.text at panel-left margin (clears title)
fig.text(0.417, 0.895, 'B', fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='right')

# ================================================================
# PANEL C: Omega distribution (mouse vs. human, real data)
# ================================================================
axC = fig.add_subplot(gs[0, 2])
mouse_dist = np.array(mouse_vals, dtype=float)          # n = 15 shared CT means
human_dist = human_pairs['omega'].dropna().values        # n = 4,851 pairs
print(f'  mouse dist: n={len(mouse_dist)}, mean={mouse_dist.mean():.2f}')
print(f'  human dist: n={len(human_dist)}, mean={human_dist.mean():.2f}')
axC.hist(mouse_dist, bins=12, color=st.C_BLUE, alpha=0.6,
         label=f'Mouse (n = {len(mouse_dist)} CTs)', density=True,
         edgecolor='white', linewidth=0.4, zorder=3)
axC.hist(human_dist, bins=30, color=st.C_RED, alpha=0.6,
         label=f'Human (n = {len(human_dist):,} pairs)', density=True,
         edgecolor='white', linewidth=0.4, zorder=3)
axC.set_xlabel('CKI \u03c9', fontsize=SMALL_SIZE, labelpad=2)
axC.set_ylabel('Density', fontsize=SMALL_SIZE, labelpad=2)
axC.legend(fontsize=SMALL_SIZE, frameon=False, loc='upper right',
           handlelength=1.2, handleheight=0.9, borderaxespad=0.2)
axC.set_title('Mouse vs. human distribution', fontsize=TITLE_SIZE,
              fontweight='bold', pad=6)
axC.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axC)
st.subtle_grid(axC, axis='y')
# Panel C label via fig.text at panel-left margin (clears title)
fig.text(0.746, 0.895, 'C', fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='right')

# ---- Caption ----
fig.text(0.5, 0.03, 'Supplementary Figure S10. Cross-species validation of CKI.',
         ha='center', fontsize=BODY_SIZE, fontweight='bold')

# ---- Save ----
out_png = OUT_DIR / 'ed_fig2_cross_species_validation.png'
out_pdf = OUT_DIR / 'ed_fig2_cross_species_validation.pdf'

fig.savefig(out_png, dpi=DPI, facecolor='white',
            bbox_inches=None, pad_inches=0.04)
fig.savefig(out_pdf, dpi=DPI, facecolor='white',
            bbox_inches=None, pad_inches=0.04,
            metadata={'Creator': 'CKI GB Supplementary Figures'})

print(f'Saved: {out_png}')
print(f'Saved: {out_pdf}')
print('Extended Data Figure 2 (real data) DONE.')
