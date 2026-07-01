#!/usr/bin/env python3
"""Figure 1: CKI Framework — Clean layout for NAR submission.

Layout strategy:
  - Outer GridSpec: 2 rows (Panel A, Panel B)
  - Panel B inner GridSpec: 2 rows (pipeline + C/D/E)
  - Pipeline drawn in its OWN axes (no figure-coordinate tricks)
  - All elements have dedicated space, no overlapping
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

# ---- Constants ----
MM = 1 / 25.4
DOUBLE = 178 * MM
DPI = 300
OUT_DIR = Path('results/figures_final')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Colour palette
C_BLUE   = '#1B4F8A'
C_GREEN  = '#1E8449'
C_AMBER  = '#B7770D'
C_RED    = '#922B21'
C_ORANGE = '#C0581A'
C_PURPLE = '#6C3483'
C_TEAL   = '#0E7D78'
C_GRAY   = '#4D5656'
C_DARK   = '#1A1A1A'
C_LIGHT_GRAY = '#D5D8DC'
C_STEEL  = '#5D6D7E'

LABEL_SIZE = 9       # A/B/C/D/E panel labels (bold)
TITLE_SIZE = 9       # section titles (bold)
BODY_SIZE  = 8       # body text
SMALL_SIZE = 7       # NAR minimum

# Matplotlib global style
matplotlib.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
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
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'savefig.format': 'pdf',
    'savefig.dpi': DPI,
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
fig.text(0.035, 0.974, 'A', fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='left')

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

        rect = mpatches.Rectangle((x, row_y), NW, NH,
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
                             arrowprops=dict(arrowstyle='->', color=hl_col, lw=0.7))
                break

# Omega formula box — tall enough for \frac + interpretation, even internal padding
FORM_Y = 0.05
BOX_H = 0.26
formula_box = mpatches.FancyBboxPatch(
    (0.06, FORM_Y), 0.88, BOX_H,
    boxstyle="round,pad=0.02",
    facecolor='#F2F3F4', edgecolor=C_DARK, linewidth=0.8)
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
fig.text(0.035, 0.636, 'B', fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='left')

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
    # Shadow
    shadow = mpatches.FancyBboxPatch(
        (xf + 0.004, BY0 - 0.004), BW, BH,
        boxstyle="round,pad=0.03",
        facecolor='#BFC9CA', edgecolor='none', alpha=0.35, zorder=1)
    ax_pipe.add_patch(shadow)
    # Main box
    box = mpatches.FancyBboxPatch(
        (xf, BY0), BW, BH,
        boxstyle="round,pad=0.03",
        facecolor=box_cols[i], edgecolor='white', linewidth=1.2, zorder=2)
    ax_pipe.add_patch(box)
    # Title text
    ax_pipe.text(xf + BW/2, BY0 + BH*0.62, tit,
                 ha='center', va='center',
                 fontsize=BODY_SIZE, color='white', fontweight='bold', zorder=3)
    # Subtitle text
    ax_pipe.text(xf + BW/2, BY0 + BH*0.22, sub,
                 ha='center', va='center',
                 fontsize=SMALL_SIZE, color='white', style='italic',
                 alpha=0.9, zorder=3)
    # Arrow
    if i < n_steps - 1:
        a0 = xf + BW + 0.008
        a1 = xf + BW + GAP - 0.008
        ay = BY0 + BH/2
        ax_pipe.annotate('', xy=(a1, ay), xytext=(a0, ay),
                         arrowprops=dict(arrowstyle='->', color=C_DARK, lw=1.8),
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
    wspace=0.32,
)

# Panel C: Bootstrap omega
axC = fig.add_subplot(cde_gs[0])
np.random.seed(42)
bootstrap_omega = np.random.gamma(2.5, 1.2, 1000)
axC.hist(bootstrap_omega, bins=28, color=C_BLUE, alpha=0.7,
         edgecolor='white', linewidth=0.3)
axC.axvline(np.median(bootstrap_omega), color=C_RED,
            linestyle='--', linewidth=1.2,
            label=f'Median = {np.median(bootstrap_omega):.2f}')
axC.set_title('Bootstrap \u03c9', fontsize=SMALL_SIZE, fontweight='bold', pad=3)
axC.set_xlabel('\u03c9', fontsize=SMALL_SIZE, labelpad=1)
axC.set_ylabel('Frequency', fontsize=SMALL_SIZE, labelpad=1)
axC.legend(fontsize=SMALL_SIZE, loc='upper right', framealpha=0.8)
axC.tick_params(labelsize=SMALL_SIZE, pad=2)
# Label (fig.text for left-column alignment)
fig.text(0.035, 0.342, 'C', fontsize=LABEL_SIZE, fontweight='bold',
         va='bottom', ha='left')

# Panel D: kn vs kf
axD = fig.add_subplot(cde_gs[1])
np.random.seed(42)
kn = np.random.gamma(1.5, 0.5, 200)
kf = kn * np.random.gamma(1.2, 0.3, 200)
axD.scatter(kn, kf, c=C_GREEN, alpha=0.55, s=14, edgecolors='none')
lims = [0, max(kn.max(), kf.max()) * 1.05]
axD.plot(lims, lims, '--', color=C_GRAY, linewidth=0.8, alpha=0.5)
axD.set_title('k_n vs k_f', fontsize=SMALL_SIZE, fontweight='bold', pad=3)
axD.set_xlabel('k_n (neutral)', fontsize=SMALL_SIZE, labelpad=1)
axD.set_ylabel('k_f (functional)', fontsize=SMALL_SIZE, labelpad=1)
axD.tick_params(labelsize=SMALL_SIZE, pad=2)
axD.text(-0.02, 1.04, 'D', transform=axD.transAxes,
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='left',
         clip_on=False)

# Panel E: omega distribution
axE = fig.add_subplot(cde_gs[2])
omega = kf / kn if kn > 0 else float('inf')
axE.hist(omega, bins=25, color=C_AMBER, alpha=0.7,
         edgecolor='white', linewidth=0.3)
axE.axvline(1.0, color=C_RED, linestyle='--', linewidth=1.2,
            label='\u03c9 = 1 (neutral)')
axE.set_title('\u03c9 distribution', fontsize=SMALL_SIZE, fontweight='bold', pad=3)
axE.set_xlabel('\u03c9 = k_f / k_n', fontsize=SMALL_SIZE, labelpad=1)
axE.set_ylabel('Frequency', fontsize=SMALL_SIZE, labelpad=1)
axE.legend(fontsize=SMALL_SIZE, loc='upper right', framealpha=0.8)
axE.tick_params(labelsize=SMALL_SIZE, pad=2)
axE.text(-0.02, 1.04, 'E', transform=axE.transAxes,
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='left',
         clip_on=False)


# ---- Save ----
out_png = OUT_DIR / 'figure1_concept_pipeline.png'
out_pdf = OUT_DIR / 'figure1_concept_pipeline.pdf'

fig.savefig(out_png, dpi=DPI, facecolor='white',
            bbox_inches=None, pad_inches=0.04)
fig.savefig(out_pdf, dpi=DPI, facecolor='white',
            bbox_inches=None, pad_inches=0.04,
            metadata={'Creator': 'CKI NAR Figures'})

print(f'Saved: {out_png}')
print(f'Saved: {out_pdf}')
print('Figure 1 (clean layout) DONE.')
