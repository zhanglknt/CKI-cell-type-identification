#!/usr/bin/env python3
"""Figure 1: CKI Framework — Clean layout for NAR submission.

Layout strategy:
  - Outer GridSpec: 2 rows (Panel A, Panel B)
  - Panel B inner GridSpec: 2 rows (pipeline + C/D/E)
  - Pipeline drawn in its OWN axes (no figure-coordinate tricks)
  - All elements have dedicated space, no overlapping

Visual identity comes from the shared module notebooks/_fig_style.py
(colours, type scale, rcParams, despine/grid/save helpers).  Data and
numeric computations are untouched relative to the previous version.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import _fig_style as st

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
from pathlib import Path
import numpy as np
import warnings
warnings.filterwarnings('ignore')

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
C_TEAL   = st.C_TEAL
C_GRAY   = st.C_GRAY
C_DARK   = st.C_DARK
C_LIGHT_GRAY = st.C_LIGHT_GRAY
C_STEEL  = st.C_STEEL

LABEL_SIZE = st.LABEL_SIZE   # A/B/C/D/E panel labels (bold, 9 pt)
TITLE_SIZE = st.TITLE_SIZE   # section titles (bold, 9 pt)
BODY_SIZE  = st.BODY_SIZE    # body text
SMALL_SIZE = st.SMALL_SIZE   # NAR minimum (7 pt)

# Global style from the shared module + Arial mathtext for the omega formula
st.apply_style()
matplotlib.rcParams.update({
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial:italic',
    'mathtext.bf': 'Arial:bold',
    'mathtext.sf': 'Arial',
})

# ---- Create figure ----
# Slightly taller to give everything breathing room
FIG_H = 172 * MM
print(f'Figure: {DOUBLE/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = plt.figure(figsize=(DOUBLE, FIG_H), dpi=DPI)

# Outer GridSpec: 2 rows
# Panel A gets ~35%, Panel B gets ~65%
gs = gridspec.GridSpec(
    2, 1, fig,
    height_ratios=[0.90, 2.10],
    left=0.08, right=0.97, top=0.97, bottom=0.04,
    hspace=0.20,
)

# ================================================================
# PANEL A: Ka/Ks molecular evolution analogy
# ================================================================
axA = fig.add_subplot(gs[0])
axA.set_xlim(0, 1)
axA.set_ylim(0, 1)
axA.axis('off')

# Label (fig.text for left-column alignment)
st.add_panel_label(fig, axA, 'A', axes_relative=False, x=0.035, y=0.974)

# Title
axA.text(0.5, 0.98, 'Ka/Ks in molecular evolution: ratio of evolutionary rates',
         transform=axA.transAxes, ha='center',
         fontsize=TITLE_SIZE, fontweight='bold')

# Nucleotide colours
nt_colours = {'A': C_BLUE, 'T': C_RED, 'G': C_GREEN, 'C': C_AMBER}
ref_seq  = ['A','T','G','C','A','A','G','T','C','G','A','T']
syn_seq  = ['A','T','G','C','A','A','G','C','C','G','A','T']   # T->C synonymous
nsyn_seq = ['A','T','G','C','G','A','G','T','C','G','A','T']   # A->G non-synonymous

# Sequence layout — bottom-to-top, generous spacing
NX  = 0.05          # left margin
NW  = 0.064         # nucleotide block width
NH  = 0.065         # nucleotide block height
VG  = 0.08          # vertical gap between rows
Y0  = 0.38          # bottom of lowest row (Ref) — raised for formula clearance

y_rows = {
    'Ref': Y0,
    'Ks':  Y0 + NH + VG,
    'Ka':  Y0 + 2*(NH + VG),
}

# Draw each row
for label, seq, row_y, hl_col, txt_col in [
    ('Ref.', ref_seq,  y_rows['Ref'], None,    C_DARK),
    ('Ks',   syn_seq,  y_rows['Ks'],  C_BLUE,  C_BLUE),
    ('Ka',   nsyn_seq, y_rows['Ka'],  C_RED,   C_RED),
]:
    is_ref = (label == 'Ref.')
    # Row label
    axA.text(NX - 0.038, row_y + NH/2, label,
             fontsize=SMALL_SIZE, ha='right', va='center',
             fontweight='bold', color=txt_col, transform=axA.transAxes)

    for j, nt in enumerate(seq):
        x = NX + j * NW
        is_diff = (not is_ref and nt != ref_seq[j])

        if is_ref:
            fc, ec, lw = nt_colours.get(nt, '#AAA'), C_DARK, 0.6
            txt_c, txt_fw = 'white', 'bold'
        elif is_diff:
            fc, ec, lw = hl_col, hl_col, 1.2
            txt_c, txt_fw = 'white', 'bold'
        else:
            fc, ec, lw = '#F4F6F6', C_LIGHT_GRAY, 0.4
            txt_c, txt_fw = C_DARK, 'normal'

        rect = mpatches.FancyBboxPatch(
            (x, row_y), NW, NH,
            boxstyle="round,pad=0.004,rounding_size=0.008",
            linewidth=lw, edgecolor=ec,
            facecolor=fc, alpha=1.0 if not is_diff else 0.88)
        axA.add_patch(rect)
        axA.text(x + NW/2, row_y + NH/2, nt,
                 ha='center', va='center', fontsize=BODY_SIZE,
                 fontweight=txt_fw, color=txt_c)

    # Annotation arrow for substitution rows
    # Both annotations go to the RIGHT of sequences — zero vertical overlap
    if not is_ref:
        for j, nt in enumerate(seq):
            if nt != ref_seq[j]:
                arrow_start = NX + 12*NW + 0.012  # just past right edge of sequences
                if label == 'Ks':
                    txt = 'synonymous'
                else:
                    txt = 'non-synonymous\n(amino acid change)'
                axA.annotate(txt,
                             xy=(arrow_start, row_y + NH/2),
                             xytext=(arrow_start + 0.035, row_y + NH/2),
                             fontsize=SMALL_SIZE, color=hl_col,
                             ha='left', va='center',
                             arrowprops=dict(arrowstyle='-|>', color=hl_col,
                                             lw=0.8, shrinkA=1, shrinkB=1))
                break

# Omega formula box — tall enough for \frac + interpretation, even internal padding
FORM_Y = 0.05
BOX_H = 0.26
formula_box = mpatches.FancyBboxPatch(
    (0.06, FORM_Y), 0.88, BOX_H,
    boxstyle="round,pad=0.02,rounding_size=0.02",
    facecolor='#F2F3F4', edgecolor=C_GRAY, linewidth=0.6)
axA.add_patch(formula_box)

# Formula text in upper portion, interpretation in lower, with even margins
formula_text_y  = FORM_Y + BOX_H * 0.72    # upper third
interp_text_y   = FORM_Y + BOX_H * 0.28    # lower third

axA.text(0.5, formula_text_y,
         r'$\mathbf{\omega = \frac{K_a}{K_s}}$',
         ha='center', va='center', fontsize=10, color=C_RED,
         fontweight='bold', transform=axA.transAxes)

axA.text(0.5, interp_text_y,
         '\u03c9 > 1: positive selection      \u03c9 \u2248 1: neutral drift      \u03c9 < 1: purifying selection',
         ha='center', va='center',
         fontsize=SMALL_SIZE, style='italic', color=C_GRAY,
         transform=axA.transAxes)


# ================================================================
# PANEL B: CKI pipeline + sub-panels C/D/E
# ================================================================
# Inner GridSpec inside gs[1]: pipeline row + C/D/E row
inner_gs = gridspec.GridSpecFromSubplotSpec(
    2, 1, gs[1],
    height_ratios=[1.0, 1.35],
    hspace=0.28,
)

# -- Pipeline row (top) --
ax_pipe = fig.add_subplot(inner_gs[0])
ax_pipe.set_xlim(0, 1)
ax_pipe.set_ylim(0, 1)
ax_pipe.axis('off')

# Title
ax_pipe.text(0.5, 0.97, 'CKI: translating Ka/Ks to single-cell transcriptomics',
             transform=ax_pipe.transAxes, ha='center',
             fontsize=TITLE_SIZE, fontweight='bold')
# Label (fig.text for left-column alignment)
st.add_panel_label(fig, ax_pipe, 'B', axes_relative=False, x=0.035, y=0.636)

# Pipeline boxes — drawn in axes coordinates (clean!)
n_steps = 4
step_labels = [
    ('Housekeeping\nGenes',   'Neutral\nbaseline'),
    ('Identity\nGenes',       'Functional\nmarkers'),
    ('JS\nDivergence',        'per gene'),
    ('CKI Index\n\u03c9 = kf/kn', 'Selection\nmetric'),
]
box_cols = [C_BLUE, C_GREEN, C_AMBER, C_RED]

BW = 0.19          # box width (in axes coords)
GAP = 0.065        # gap between boxes
BTOTAL = n_steps * BW + (n_steps - 1) * GAP
BX0 = (1.0 - BTOTAL) / 2
BH = 0.46           # box height (reduced for spacing)
BY0 = 0.32          # box bottom (raised for annotation below)

for i, (tit, sub) in enumerate(step_labels):
    xf = BX0 + i * (BW + GAP)
    # Shadow (soft drop shadow)
    shadow = mpatches.FancyBboxPatch(
        (xf + 0.005, BY0 - 0.005), BW, BH,
        boxstyle="round,pad=0.03,rounding_size=0.02",
        facecolor='#BFC9CA', edgecolor='none', alpha=0.30, zorder=1)
    ax_pipe.add_patch(shadow)
    # Main box
    box = mpatches.FancyBboxPatch(
        (xf, BY0), BW, BH,
        boxstyle="round,pad=0.03,rounding_size=0.02",
        facecolor=box_cols[i], edgecolor='white', linewidth=1.0, zorder=2)
    ax_pipe.add_patch(box)
    # Title text
    ax_pipe.text(xf + BW/2, BY0 + BH*0.62, tit,
                 ha='center', va='center',
                 fontsize=BODY_SIZE, color='white', fontweight='bold', zorder=3)
    # Subtitle text
    ax_pipe.text(xf + BW/2, BY0 + BH*0.22, sub,
                 ha='center', va='center',
                 fontsize=SMALL_SIZE, color='white', style='italic',
                 alpha=0.92, zorder=3)
    # Arrow
    if i < n_steps - 1:
        a0 = xf + BW + 0.010
        a1 = xf + BW + GAP - 0.010
        ay = BY0 + BH/2
        ax_pipe.annotate('', xy=(a1, ay), xytext=(a0, ay),
                         arrowprops=dict(arrowstyle='-|>', color=C_DARK,
                                         lw=1.6, mutation_scale=12,
                                         shrinkA=0, shrinkB=0),
                         zorder=2)

# Annotation below pipeline boxes — well separated
ann_y = BY0 - 0.08
ax_pipe.text(BX0 + 0.02, ann_y,
             'Gene sets: auto-detected from expression matrix',
             fontsize=SMALL_SIZE, color=C_GRAY, transform=ax_pipe.transAxes)
ax_pipe.text(BX0 + BTOTAL - 0.02, ann_y,
             'Bootstrap CI',
             fontsize=SMALL_SIZE, color=C_GRAY, ha='right',
             transform=ax_pipe.transAxes)


# -- C/D/E row (bottom) --
cde_gs = gridspec.GridSpecFromSubplotSpec(
    1, 3, inner_gs[1],
    wspace=0.34,
)

# Panel C: Bootstrap omega
axC = fig.add_subplot(cde_gs[0])

# ---- Real data: mouse pilot (results/mouse_pilot_v2_results.csv) ----
import pandas as pd
mp = pd.read_csv('results/mouse_pilot_v2_results.csv')
ctrl_omega = mp.loc[mp['category'] == 'C_control', 'omega'].to_numpy()   # 6 controls
print(f'Mouse pilot: {len(mp)} pairs, {len(ctrl_omega)} C controls '
      f'(mean {ctrl_omega.mean():.2f}, median {np.median(ctrl_omega):.2f})')

# Panel C: Bootstrap omega distribution (B = 1,000, resampling the 6
# split-half control omega values; empirical baseline 6.67 [4.24, 9.24])
np.random.seed(42)
bootstrap_omega = np.random.choice(ctrl_omega, size=(1000, len(ctrl_omega)),
                                   replace=True).mean(axis=1)
axC.hist(bootstrap_omega, bins=28, color=C_BLUE, alpha=0.85,
         edgecolor='white', linewidth=0.4, zorder=2)
axC.axvline(np.median(bootstrap_omega), color=C_RED,
            linestyle='--', linewidth=1.1,
            label=f'Median = {np.median(bootstrap_omega):.2f}', zorder=3)
axC.axvline(ctrl_omega.mean(), color=C_DARK, linestyle=':',
            linewidth=1.0,
            label=f'Baseline = {ctrl_omega.mean():.2f}', zorder=3)
axC.set_title('Bootstrap \u03c9 (mouse pilot)', fontsize=TITLE_SIZE,
              fontweight='bold', pad=3)
axC.set_xlabel('Bootstrap mean \u03c9', fontsize=BODY_SIZE, labelpad=1)
axC.set_ylabel('Frequency', fontsize=BODY_SIZE, labelpad=1)
axC.legend(fontsize=SMALL_SIZE, loc='upper right', frameon=False)
axC.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axC)
st.subtle_grid(axC)
# Label (fig.text for left-column alignment)
st.add_panel_label(fig, axC, 'C', axes_relative=False, x=0.035, y=0.342)

# Panel D: kn vs kf (real mouse pilot pairs, log-log)
axD = fig.add_subplot(cde_gs[1])
kn = mp['kn'].to_numpy()
kf = mp['kf'].to_numpy()
cat_col = {'C_control': C_BLUE, 'S': C_GREEN, 'D': C_AMBER, 'X': C_RED}
for cat, col in cat_col.items():
    sel = (mp['category'] == cat).to_numpy()
    if sel.any():
        axD.scatter(kn[sel], kf[sel], c=col, alpha=0.85, s=22,
                    edgecolors='white', linewidths=0.3, zorder=3,
                    label=cat.split('_')[0])
axD.set_xscale('log'); axD.set_yscale('log')
lims = [min(kn.min(), kf.min()) * 0.6, max(kn.max(), kf.max()) * 1.6]
axD.plot(lims, lims, '--', color=C_GRAY, linewidth=0.8, alpha=0.6, zorder=2)
axD.set_xlim(lims); axD.set_ylim(lims)
axD.set_title('k_n vs k_f (mouse pilot)', fontsize=TITLE_SIZE,
              fontweight='bold', pad=3)
axD.set_xlabel('k_n (neutral)', fontsize=BODY_SIZE, labelpad=1)
axD.set_ylabel('k_f (functional)', fontsize=BODY_SIZE, labelpad=1)
axD.legend(fontsize=SMALL_SIZE, loc='upper left', frameon=False,
           handletextpad=0.2, borderaxespad=0.2)
axD.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axD)
st.subtle_grid(axD, axis='both')
st.add_panel_label(fig, axD, 'D', x=-0.02, y=1.04)

# Panel E: omega distribution (real mouse pilot, n = 15 pairs)
axE = fig.add_subplot(cde_gs[2])
omega = mp['omega'].to_numpy()
axE.hist(omega, bins=12, color=C_AMBER, alpha=0.85,
         edgecolor='white', linewidth=0.4, zorder=2)
axE.axvline(1.0, color=C_RED, linestyle='--', linewidth=1.1,
            label='\u03c9 = 1 (neutral)', zorder=3)
axE.set_title('\u03c9 distribution (n = 15)', fontsize=TITLE_SIZE,
              fontweight='bold', pad=3)
axE.set_xlabel('\u03c9 = k_f / k_n', fontsize=BODY_SIZE, labelpad=1)
axE.set_ylabel('Frequency', fontsize=BODY_SIZE, labelpad=1)
axE.legend(fontsize=SMALL_SIZE, loc='upper right', frameon=False)
axE.tick_params(labelsize=SMALL_SIZE, pad=2)
st.despine(axE)
st.subtle_grid(axE)
st.add_panel_label(fig, axE, 'E', x=-0.02, y=1.04)


# ---- Save ----
written = st.save_fig(fig, 'figure1_concept_pipeline')
for p in written:
    print(f'Saved: {p}')
print('Figure 1 (clean layout) DONE.')
