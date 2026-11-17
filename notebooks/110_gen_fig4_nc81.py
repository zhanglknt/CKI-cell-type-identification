#!/usr/bin/env python3
"""Figure 4 (NC) - brain regional divergence, re-plotted for NC legibility.

nc81 rewrite.  The previous version (results/figures_v58_author/figure6.pdf
stitched by results/audit/_nc70_mainfigs.py) was drawn on a 441 x 354 mm
canvas, so at the NC double-column width of 180 mm every label printed at
2.4-3.3 pt (results/audit/_nc81_review_expert_panel.md, F11).  Vector
rescaling cannot fix that: the text is small *relative to the data*, so the
panels are re-plotted here from the authoritative result tables.

Data sources (all reproduced by the scripts listed in the Methods):
  results/brain_bs_null_observed_pairs.csv   31,764 cross-region pairs
  results/brain_bs_null_ct_test.csv          per-class block-shuffle means
  results/nc79_a5_scheme_tiers.csv           tier counts, main scheme
  results/brain_neuron_blockshuffle.csv      superclass permutation stats
  results/brain_neuron_blockshuffle_null_means.npy   B = 1,000 null means

Panel (a) is redrawn as a simplified schematic: the anatomical region names
that previously sat at 2-3 pt are not carried over (region lists are in
Supplementary Tables 10-11), so every label left in the panel is >= 7 pt.

Output: results/figures_nc81/figure4.pdf  (180 mm wide, Arial >= 7 pt)
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _fig_style as st  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.gridspec as gridspec  # noqa: E402
from matplotlib.patches import (  # noqa: E402
    Ellipse, FancyBboxPatch, PathPatch, Polygon, Rectangle,
)
from matplotlib.path import Path  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(BASE, 'results')
OUT = os.path.join(RES, 'figures_nc81')
os.makedirs(OUT, exist_ok=True)

st.apply_style()
MM = st.MM
FIG_W = 180 * MM            # NC double column
FIG_H = 214 * MM

TICK = 7.0                  # nothing below 7 pt
BODY = 7.5
TITLE = 7.5
PANEL = 9.0

C_BLUE, C_PURPLE, C_RED = st.C_BLUE, st.C_PURPLE, st.C_RED
C_AMBER, C_ORANGE, C_TEAL = st.C_AMBER, st.C_ORANGE, st.C_TEAL
C_GRAY, C_STEEL, C_GREEN = st.C_GRAY, st.C_STEEL, st.C_GREEN


# ---------------------------------------------------------------- load data
pairs = pd.read_csv(os.path.join(RES, 'brain_bs_null_observed_pairs.csv'))
ct = pd.read_csv(os.path.join(RES, 'brain_bs_null_ct_test.csv'))
tiers = pd.read_csv(os.path.join(RES, 'nc79_a5_scheme_tiers.csv'))
bs = pd.read_csv(os.path.join(RES, 'brain_neuron_blockshuffle.csv'))
null_means = np.load(os.path.join(RES, 'brain_neuron_blockshuffle_null_means.npy'))

ct = ct.sort_values('omega_mean', ascending=True).reset_index(drop=True)
main_tier = tiers[tiers.scheme.str.startswith('(a)')].iloc[0]
n_total = int(main_tier.n_pairs)
strong5 = pairs[pairs.tier == 'Strong'].nsmallest(5, 'residual').reset_index(drop=True)

assert int(main_tier.strong) == 39 and int(main_tier.moderate) == 1171
assert int(main_tier.weak) == 5381 and n_total == 31764
assert abs(ct.omega_mean.max() / ct.omega_mean.min() - 6.105) < 0.01
assert abs(strong5.residual.iloc[0] - 0.1964) < 1e-3

print('[fig4] classes', len(ct), 'pairs', len(pairs),
      'gradient %.2f-fold' % (ct.omega_mean.max() / ct.omega_mean.min()))
print('[fig4] top-5 Strong residuals',
      ', '.join('%.3f' % v for v in strong5.residual))

# ------------------------------------------------------------- panel layout
# Explicit axes rectangles (figure fractions).  The two bar panels carry long
# cell-class labels, so their left edge is set at 0.28; the violins and the
# candidate bars use the space freed on their left.
fig = plt.figure(figsize=(FIG_W, FIG_H))
AX = {
    'a': [0.015, 0.800, 0.970, 0.195],
    'b': [0.280, 0.612, 0.320, 0.163],
    'e': [0.700, 0.612, 0.285, 0.163],
    'c': [0.130, 0.402, 0.450, 0.140],
    'd': [0.660, 0.402, 0.325, 0.140],
    'f': [0.280, 0.060, 0.705, 0.215],
}
LET = {'a': (0.012, 0.996), 'b': (0.240, 0.780), 'e': (0.644, 0.780),
       'c': (0.090, 0.546), 'd': (0.620, 0.546), 'f': (0.240, 0.300)}


def panel(letter):
    x, y = LET[letter]
    fig.text(x, y, letter, fontsize=PANEL, fontweight='bold',
             va='bottom', ha='left')


def two_line_title(ax, main, sub=None):
    """Bold title with an optional grey subtitle above it.

    Each subtitle line is a separate text object anchored just above the
    axes, so a two-line note cannot drift into the title the way a single
    multi-line string with va='bottom' does.
    """
    lines = sub.split('\n') if sub else []
    ax.set_title(main, fontsize=TITLE, fontweight='bold',
                 pad=4 + 13 * len(lines), loc='left')
    for k, ln in enumerate(reversed(lines)):
        ax.text(0, 1.035 + k * 0.082, ln, transform=ax.transAxes,
                fontsize=TICK, va='bottom', ha='left', color=C_GRAY)


# ------------------------------------------------------- (a) atlas schematic
axA = fig.add_axes(AX['a'])
axA.set_xlim(0, 100)
axA.set_ylim(0, 100)
axA.axis('off')

# --- sagittal outline (stylised): cerebrum, diencephalon, brainstem, cerebellum
cerebrum = Path(
    [(3, 56), (2, 79), (13, 94), (27, 93), (40, 92), (48, 79),
     (47, 61), (46, 48), (36, 41), (25, 43), (11, 44), (4, 49), (3, 56)],
    [Path.MOVETO] + [Path.CURVE4] * 12,
)
axA.add_patch(PathPatch(cerebrum, facecolor='#E3EDF7', edgecolor=C_BLUE,
                        linewidth=0.7, zorder=2))
for (x0, y0, x1, y1, bump) in [(7, 71, 19, 90, 6), (19, 63, 30, 90, -5),
                               (30, 60, 40, 88, 5), (9, 55, 21, 73, -5)]:
    verts = [(x0, y0), ((x0 + x1) / 2, max(y0, y1) + bump), (x1, y1)]
    axA.add_patch(PathPatch(Path(verts, [Path.MOVETO, Path.CURVE3, Path.CURVE3]),
                            facecolor='none', edgecolor='#A9BFD4',
                            linewidth=0.4, zorder=3))
axA.add_patch(Ellipse((24, 53), 10, 8, facecolor='#F6E2C0', edgecolor=C_AMBER,
                      linewidth=0.5, zorder=4))
axA.add_patch(Rectangle((21.5, 37), 5.6, 11, facecolor='#D6EAD8', edgecolor=C_GREEN,
                        linewidth=0.5, zorder=4))
axA.add_patch(Rectangle((21.5, 25), 5.9, 12, facecolor='#E2D8EE', edgecolor=C_PURPLE,
                        linewidth=0.5, zorder=4))
axA.add_patch(Rectangle((22.2, 14), 4.4, 11, facecolor='#CFE7E5', edgecolor=C_TEAL,
                        linewidth=0.5, zorder=4))
axA.add_patch(Ellipse((40, 31), 17, 13, facecolor='#F7D9C4', edgecolor=C_ORANGE,
                      linewidth=0.5, zorder=4))
for k in range(-2, 3):
    axA.plot([35, 45], [31 + 2.4 * k, 31 + 2.4 * k], color='#DBA079',
             linewidth=0.4, zorder=5)

for xy, txt, col, ha in [((26, 80), 'Cerebrum', C_BLUE, 'center'),
                         ((10.5, 51), 'Diencephalon', C_AMBER, 'right'),
                         ((10.5, 40), 'Midbrain', C_GREEN, 'right'),
                         ((10.5, 29), 'Pons', C_PURPLE, 'right'),
                         ((10.5, 18), 'Medulla', C_TEAL, 'right'),
                         ((40, 19), 'Cerebellum', C_ORANGE, 'center')]:
    axA.text(xy[0], xy[1], txt, fontsize=TICK, color=col, ha=ha, va='center',
             zorder=6,
             bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.8))

axA.text(50, 96, '108 regions  \u00b7  888,263 nuclei  \u00b7  10 cell types',
         fontsize=BODY, ha='left', va='center', fontweight='bold', color=st.C_DARK)

chips = [
    ('Astrocyte', '#DCE8F4', 'astro'),
    ('Oligodendrocyte', '#E2D8EE', 'oligo'),
    ('Oligodendrocyte precursor', '#EFE7F5', 'opc'),
    ('Committed OL precursor', '#F3EDF8', 'copc'),
    ('Microglia', '#D6EAD8', 'micro'),
    ('Bergmann glia', '#D9F0EE', 'berg'),
    ('Ependymal', '#CFE7E5', 'epen'),
    ('Vascular', '#F7D9C4', 'vasc'),
    ('Fibroblast', '#F6E2C0', 'fib'),
    ('Choroid plexus', '#E8E8E8', 'chor'),
]
CHIP_X, CHIP_Y0, CHIP_DY = 51.5, 86.0, 8.4


def glyph(ax, x, y, kind, fc, ec):
    if kind == 'astro':
        ax.add_patch(plt.Circle((x, y), 1.5, fc=fc, ec=ec, lw=0.45, zorder=6))
        for a in np.linspace(0, 2 * np.pi, 7)[:-1]:
            ax.plot([x, x + 3.0 * np.cos(a)], [y, y + 3.0 * np.sin(a)],
                    color=ec, lw=0.45, zorder=5)
    elif kind in ('oligo', 'copc'):
        ax.add_patch(plt.Circle((x, y), 1.6, fc=fc, ec=ec, lw=0.45, zorder=6))
        for a in (0.5, 2.1, 3.7, 5.3):
            ax.add_patch(Ellipse((x + 3.3 * np.cos(a), y + 3.3 * np.sin(a)),
                                 3.0, 1.9, angle=np.degrees(a), fc=fc,
                                 ec=ec, lw=0.35, zorder=5))
    elif kind == 'opc':
        ax.add_patch(plt.Circle((x, y), 1.5, fc=fc, ec=ec, lw=0.45, zorder=6))
        for a in (0.9, 2.9, 4.9):
            ax.plot([x, x + 3.2 * np.cos(a)], [y, y + 3.2 * np.sin(a)],
                    color=ec, lw=0.45, zorder=5)
    elif kind == 'micro':
        pts = [(x + 3.0 * np.cos(a), y + 3.0 * np.sin(a))
               for a in np.linspace(0, 2 * np.pi, 9)[:-1]]
        ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=0.45, zorder=6))
    elif kind == 'berg':
        ax.add_patch(plt.Circle((x, y), 1.4, fc=fc, ec=ec, lw=0.45, zorder=6))
        for a in np.linspace(0.35, np.pi - 0.35, 4):
            ax.plot([x, x + 3.3 * np.cos(a)], [y, y + 3.3 * np.sin(a)],
                    color=ec, lw=0.45, zorder=5)
    elif kind == 'epen':
        pts = [(x, y + 3.2), (x + 1.9, y - 2.5), (x - 1.9, y - 2.5)]
        ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=0.45, zorder=6))
    elif kind == 'vasc':
        ax.add_patch(plt.Circle((x, y), 1.9, fc=fc, ec=ec, lw=0.45, zorder=6))
        ax.add_patch(plt.Circle((x, y), 0.8, fc='white', ec=ec, lw=0.35, zorder=7))
    elif kind == 'fib':
        ax.add_patch(Rectangle((x - 2.5, y - 1.1), 5.0, 2.2, fc=fc, ec=ec,
                               lw=0.45, zorder=6))
    else:
        ax.add_patch(FancyBboxPatch((x - 2.3, y - 1.4), 4.6, 2.8,
                                    boxstyle='round,pad=0.15,rounding_size=0.6',
                                    fc=fc, ec=ec, lw=0.45, zorder=6))


for i, (name, fc, kind) in enumerate(chips):
    cy = CHIP_Y0 - i * CHIP_DY
    glyph(axA, CHIP_X, cy, kind, fc, C_STEEL)
    axA.text(CHIP_X + 5.0, cy, name, fontsize=TICK, va='center', ha='left',
             color=st.C_DARK)

# ------------------------------------------------- (b) per-class omega bars
axB = fig.add_axes(AX['b'])
for i, row in ct.iterrows():
    m = row.omega_mean
    col = C_BLUE if m < 25 else (C_PURPLE if m < 45 else C_RED)
    axB.barh(i, m, height=0.70, color=col, edgecolor='none')
    axB.text(m + 1.8, i, '%.1f' % m, va='center', ha='left', fontsize=TICK,
             color=st.C_DARK)
axB.set_yticks(np.arange(len(ct)))
axB.set_yticklabels(ct.cell_type, fontsize=TICK)
axB.set_xlim(0, 98)
axB.set_xlabel('\u03c9 at regional divergence', fontsize=BODY)
axB.tick_params(axis='x', labelsize=TICK)
st.subtle_grid(axB, axis='x')
two_line_title(axB, '6.10-fold \u03c9 gradient across 10 cell classes', None)
leg = [Line2D([], [], marker='s', ls='none', ms=4.5, color=C_BLUE, label='low (< 25)'),
       Line2D([], [], marker='s', ls='none', ms=4.5, color=C_PURPLE,
              label='intermediate (25\u201345)'),
       Line2D([], [], marker='s', ls='none', ms=4.5, color=C_RED, label='high (\u2265 45)')]
axB.legend(handles=leg, loc='lower right', fontsize=TICK, frameon=True,
           handletextpad=0.4, borderpad=0.35, labelspacing=0.25,
           handlelength=1.0)
panel('b')

# ------------------------------------------------ (e) block-shuffle nulls
axE = fig.add_axes(AX['e'])
for i in range(3):
    vals = null_means[i]
    vp = axE.violinplot([vals], positions=[i], widths=0.66, showextrema=False)
    for body in vp['bodies']:
        body.set_facecolor('#CFD3D8')
        body.set_edgecolor(C_STEEL)
        body.set_linewidth(0.45)
        body.set_alpha(0.9)
    axE.plot([i - 0.24, i + 0.24], [vals.mean()] * 2, color=st.C_DARK,
             linewidth=1.1, solid_capstyle='butt', zorder=4)
    axE.plot(i, bs.omega_mean.iloc[i], marker='o', ms=3.8, color=C_RED,
             zorder=5, clip_on=False)
    p = bs.p_value.iloc[i]
    txt = 'P < 0.001' if p <= 0.0015 else 'P = %.3f' % p
    axE.text(i, 88, txt, ha='center', va='top', fontsize=TICK, color=st.C_DARK)
axE.set_xticks([0, 1, 2])
axE.set_xticklabels(['MGE', 'Thalamic', 'Upper-layer\nIT'], fontsize=TICK)
axE.set_xlim(-0.62, 2.62)
axE.set_ylim(38, 90)
axE.set_ylabel('Mean regional \u03c9', fontsize=BODY)
axE.tick_params(axis='y', labelsize=TICK)
st.subtle_grid(axE, axis='y')
two_line_title(axE, 'Block-shuffle null (B = 1,000)', None)
panel('e')

# --------------------------------------------------- (c) candidate tiers
axC = fig.add_axes(AX['c'])
tiers3 = [('Strong', int(main_tier.strong), C_RED),
          ('Moderate', int(main_tier.moderate), C_AMBER),
          ('Weak', int(main_tier.weak), C_PURPLE)]
for i, (name, n, col) in enumerate(tiers3):
    pct = 100.0 * n / n_total
    axC.barh(i, pct, height=0.58, color=col, edgecolor='none')
    axC.text(pct + 0.4, i, '%.2f%%  (%s)' % (pct, format(n, ',')),
             va='center', ha='left', fontsize=TICK, color=st.C_DARK)
axC.set_yticks(range(3))
axC.set_yticklabels(['%s (%s)' % (n, format(k, ',')) for n, k, _ in tiers3],
                    fontsize=TICK)
axC.set_xlim(0, 26)
axC.set_xlabel('Percentage of 31,764 pairs', fontsize=BODY)
axC.tick_params(axis='x', labelsize=TICK)
st.subtle_grid(axC, axis='x')
axC.invert_yaxis()
two_line_title(axC, 'Region-associated candidates', None)
panel('c')

# ------------------------------------- (d) observed vs expected, top-5 Strong
axD = fig.add_axes(AX['d'])
x = np.arange(len(strong5))
w = 0.38
axD.bar(x - w / 2, strong5.omega, w, color=C_PURPLE, edgecolor='none',
        label='Observed')
axD.bar(x + w / 2, strong5.expected_omega, w, color='#C9CCD1', edgecolor='none',
        label='Expected')
for i, row in strong5.iterrows():
    axD.text(x[i] + w / 2, row.expected_omega + 2.0, '%.2f' % row.residual,
             ha='center', va='bottom', fontsize=TICK, color=C_RED, rotation=90)
axD.set_xticks(x)
axD.set_xticklabels(['%s\n%s\u2013%s' % (
    r.cell_type.replace('Oligodendrocyte', 'Oligo.'),
    r.region_a.replace('Human ', ''), r.region_b.replace('Human ', ''))
    for _, r in strong5.iterrows()], fontsize=TICK)
axD.set_ylim(0, 84)
axD.set_yticks([0, 20, 40, 60])
axD.set_ylabel('\u03c9 (region pair)', fontsize=BODY)
axD.tick_params(axis='y', labelsize=TICK)
st.subtle_grid(axD, axis='y')
axD.legend(loc='upper left', fontsize=TICK, frameon=False, ncol=2,
           handlelength=1.0, columnspacing=0.9, handletextpad=0.35,
           bbox_to_anchor=(0.0, 1.02))
two_line_title(axD, 'Five strongest Strong candidates', None)
panel('d')

# ------------------------------------- (f) neuronal vs non-neuronal medians
axF = fig.add_axes(AX['f'])
med = bs.set_index('supercluster').omega_median
rows = [('Upper-layer IT', med['Upper-layer intratelencephalic'], C_PURPLE),
        ('Thalamic excitatory', med['Thalamic excitatory'], C_PURPLE),
        ('MGE interneurons', med['MGE interneuron'], C_PURPLE)]
for _, r in ct.sort_values('omega_median', ascending=False).iterrows():
    rows.append((r.cell_type, r.omega_median,
                 C_RED if r.cell_type == 'Astrocyte' else '#9AA0A6'))
ypos = np.arange(len(rows))
for i, (name, val, col) in enumerate(rows):
    axF.barh(i, val, height=0.66, color=col, edgecolor='none')
    axF.text(val + 1.4, i, '%.1f' % val, va='center', ha='left', fontsize=TICK,
             color=st.C_DARK)
axF.set_yticks(ypos)
axF.set_yticklabels([r[0] for r in rows], fontsize=TICK)
axF.set_xlim(0, 86)
axF.set_xlabel('Median pair \u03c9', fontsize=BODY)
axF.tick_params(axis='x', labelsize=TICK)
st.subtle_grid(axF, axis='x')
axF.invert_yaxis()
two_line_title(axF, 'Neuronal superclasses (purple) vs non-neuronal classes',
               'Mann\u2013Whitney z = 52.6, pair-level pseudoreplicated '
               '(P in legend)')
panel('f')

out_pdf = os.path.join(OUT, 'figure4.pdf')
fig.savefig(out_pdf, format='pdf', dpi=st.DPI, facecolor='white')
fig.savefig(os.path.join(OUT, 'figure4.png'), format='png', dpi=200,
            facecolor='white')
plt.close(fig)

print('[fig4] wrote', out_pdf)
print('[fig4] figsize %.1f x %.1f mm' % (FIG_W / MM, FIG_H / MM))
print('[fig4] median of class medians (excl. astrocytes):',
      '%.2f' % ct[ct.cell_type != 'Astrocyte'].omega_median.median())
print('[fig4] median of class medians (all ten):',
      '%.2f' % ct.omega_median.median())
print('[fig4] neuronal medians:', ', '.join('%.1f' % v for v in bs.omega_median))
