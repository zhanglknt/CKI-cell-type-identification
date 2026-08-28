"""
Extended Data Figure 5 (Supplementary Figure S5): Cross-Organ Conservation.
Complete raw data of the 59 same-cell-type cross-organ pairs in Tabula Sapiens
(results/phase35_cross_organ_conservation.csv; Supplementary Table S2).

Layout: 2 rows x 1 column
  A: mean CKI omega per cell type (SD error bars where n >= 2), ordered as in
     Table 2: well-sampled cell types (n >= 5 pairs) ranked by mean omega,
     sparsely sampled cell types (n < 5) to the right of the divider.
  B: individual pair-level omega values (raw data, 59 pairs).
Visual identity shared via notebooks/_fig_style.py (Arial, Type 42, >=7 pt).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig_style as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from pathlib import Path
import numpy as np
import pandas as pd

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

# ---- Data: authoritative 59 same-CT cross-organ pairs ----
co = pd.read_csv(RESDIR / 'phase35_cross_organ_conservation.csv')
grp = co.groupby('ct')['omega']
stats = pd.DataFrame({'mean': grp.mean(), 'sd': grp.std(ddof=1), 'n': grp.size()})

# Table 2 ordering: well-sampled (n >= 5) ranked by mean omega first,
# then sparsely sampled (n < 5) sorted by mean omega.
well = stats[stats['n'] >= 5].sort_values('mean')
sparse = stats[stats['n'] < 5].sort_values('mean')
ordered = pd.concat([well, sparse])

CT_SHORT = {
    'cd8-positive, alpha-beta t cell': 'CD8 T',
    'cd4-positive, alpha-beta t cell': 'CD4 T',
    'hematopoietic stem cell': 'HSC',
    'classical monocyte': 'class. mono',
    'intermediate monocyte': 'interm. mono',
    'naive b cell': 'naive B',
    'memory b cell': 'memory B',
}
labels = [CT_SHORT.get(ct, ct) for ct in ordered.index]
means = ordered['mean'].values
sds = ordered['sd'].fillna(0).values
ns = ordered['n'].values
is_well = ns >= 5
n_well = int(is_well.sum())
n_total = len(ordered)
print(f'  {len(co)} cross-organ pairs across {n_total} cell types '
      f'({n_well} well-sampled, {n_total - n_well} sparse)')

C_WELL = st.C_BLUE
C_SPARSE = st.C_GRAY

# ---- Figure ----
FIG_H = 120 * MM
fig = st.new_figure(DOUBLE, FIG_H)

GS_LEFT   = 0.09
GS_RIGHT  = 0.97
GS_TOP    = 0.93
GS_BOTTOM = 0.16
GS_HSPACE = 0.42

gs = gridspec.GridSpec(2, 1, fig,
    left=GS_LEFT, right=GS_RIGHT, top=GS_TOP, bottom=GS_BOTTOM,
    hspace=GS_HSPACE)

x = np.arange(n_total)
DIVIDER = n_well - 0.5   # between well-sampled and sparse blocks

# ---- Panel A: mean omega per cell type ----
axA = fig.add_subplot(gs[0])
colors_a = [C_WELL if w else C_SPARSE for w in is_well]
axA.bar(x, means, width=0.62, color=colors_a, alpha=0.9,
        edgecolor=st.C_DARK, linewidth=0.4, zorder=3)
axA.errorbar(x, means, yerr=[np.zeros(n_total), sds], fmt='none',
             ecolor=st.C_DARK, elinewidth=0.7, capsize=2, capthick=0.7,
             zorder=4)
for xi, m, n in zip(x, means, ns):
    axA.text(xi, 0.5, f'n={n}', ha='center', va='bottom',
             fontsize=5.5, color='white', fontweight='bold', zorder=5)
axA.axvline(DIVIDER, color=st.C_DARK, linestyle=':', linewidth=0.9, zorder=2)
axA.set_ylabel('Mean CKI \u03c9', fontsize=BODY_SIZE, labelpad=2)
axA.set_ylim(0, max(means + sds) * 1.12)
axA.set_xlim(-0.6, n_total - 0.4)
axA.set_xticks(x)
axA.set_xticklabels([])
axA.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
st.despine(axA)
st.subtle_grid(axA, axis='y')
axA.set_title('Cross-organ \u03c9 by cell type (n \u2265 5 left of divider)',
              fontsize=TITLE_SIZE, fontweight='bold', pad=4)

fig.text(0.035, GS_TOP + 0.012, 'A',
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ---- Panel B: raw pair-level omega values ----
axB = fig.add_subplot(gs[1])
rng = np.random.default_rng(42)
for i, ct in enumerate(ordered.index):
    vals = co.loc[co['ct'] == ct, 'omega'].values
    jitter = rng.uniform(-0.13, 0.13, size=len(vals))
    axB.scatter(np.full(len(vals), i) + jitter, vals, s=14,
                color=(C_WELL if is_well[i] else C_SPARSE), alpha=0.75,
                edgecolors='none', zorder=3)
axB.axvline(DIVIDER, color=st.C_DARK, linestyle=':', linewidth=0.9, zorder=2)
axB.set_ylabel('Pair-level CKI \u03c9', fontsize=BODY_SIZE, labelpad=2)
axB.set_xticks(x)
axB.set_xticklabels(labels, rotation=30, ha='right', fontsize=SMALL_SIZE)
axB.set_xlim(-0.6, n_total - 0.4)
axB.set_ylim(0, co['omega'].max() * 1.08)
axB.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
st.despine(axB)
st.subtle_grid(axB, axis='y')

fig.text(0.035, GS_BOTTOM + 0.42 + 0.012, 'B',
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ---- Legend (top-right) ----
legend_elements = [
    Patch(facecolor=C_WELL, alpha=0.9, edgecolor=st.C_DARK, linewidth=0.4,
          label='Well-sampled (n \u2265 5 pairs)'),
    Patch(facecolor=C_SPARSE, alpha=0.9, edgecolor=st.C_DARK, linewidth=0.4,
          label='Sparsely sampled (n < 5 pairs)'),
]
fig.legend(handles=legend_elements, loc='lower right',
           bbox_to_anchor=(0.99, 0.90), fontsize=SMALL_SIZE,
           frameon=False, ncol=1, handlelength=1.5, handleheight=0.9)

# ---- Caption ----
fig.text(0.5, 0.030,
         'Extended Data Figure 5. Cross-organ conservation raw data: '
         f'{len(co)} same-cell-type cross-organ pairs (Tabula Sapiens).\n'
         '(A) Mean \u03c9 per cell type (error bars: SD where n \u2265 2; '
         'Table 2 ordering: n \u2265 5 ranked by mean \u03c9, left of divider). '
         '(B) Individual pair \u03c9 values.',
         ha='center', fontsize=SMALL_SIZE, linespacing=1.3)

# ---- Save ----
out_png = OUT_DIR / 'ed_fig5_cross_organ_table.png'
out_pdf = OUT_DIR / 'ed_fig5_cross_organ_table.pdf'

fig.savefig(out_png, dpi=DPI, facecolor='white',
            bbox_inches='tight', pad_inches=0.02)
fig.savefig(out_pdf, dpi=DPI, facecolor='white',
            bbox_inches='tight', pad_inches=0.02,
            metadata={'Creator': 'CKI NAR Extended Data Figures'})

print(f'Saved: {out_png}')
print(f'Saved: {out_pdf}')
plt.close()
print('Extended Data Figure 5 (real data, 59 cross-organ pairs) DONE.')
