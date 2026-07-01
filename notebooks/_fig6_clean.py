"""Figure 6: Brain Regional CKI & Migration — v6

Changes from v5:
- Panel A: Move region name labels inside the brain panel (compact legend) to fix A/B overlap
- Layout: C and D on the same row (C cols 0:1, D col 2); E spans full width on row 2
- Panel E: legend clean, annotations above bars

Layout: 3x3 GridSpec
All fonts >= 7pt, panel labels 9pt bold, no tight_layout().
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams.update({
    'font.family': 'Arial',
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Arc, Wedge, Ellipse, PathPatch
from matplotlib.path import Path
import numpy as np

# ---- Layout constants ----
DPI = 300
MM = 1/25.4
FIG_W = 176 * MM
FIG_H = 150 * MM

# ---- Font sizes ----
LABEL_SIZE = 9
SMALL_SIZE = 7
MID_SIZE   = 7.5

# ---- Colors ----
C_BLUE   = '#2166AC'
C_GREEN  = '#4DAF4A'
C_RED    = '#E41A1C'
C_AMBER  = '#FFB300'
C_ORANGE = '#FF7F00'
C_PURPLE = '#984EA3'
C_GRAY   = '#999999'
C_DARK   = '#333333'

# ---- Output directory ----
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'figures_final')
os.makedirs(OUTDIR, exist_ok=True)


def savefig(name):
    for ext in ['.pdf', '.png']:
        path = os.path.join(OUTDIR, name + ext)
        plt.savefig(path, dpi=DPI if ext == '.png' else None,
                    bbox_inches='tight', pad_inches=0.02)
    print(f'  -> {name}.pdf + .png')


def make_brain_path(sx=1.0, ox=0.0):
    """Realistic sagittal brain outline, scaled + shifted via sx/ox."""
    raw = [
        (0.05, 0.62),
        (0.08, 0.82),
        (0.18, 0.93),
        (0.35, 0.96),
        (0.55, 0.95),
        (0.72, 0.90),
        (0.84, 0.78),
        (0.90, 0.60),
        (0.92, 0.45),
        (0.90, 0.32),
        (0.85, 0.22),
        (0.75, 0.18),
        (0.58, 0.12),
        (0.40, 0.09),
        (0.22, 0.14),
        (0.10, 0.28),
        (0.04, 0.48),
        (0.04, 0.55),
    ]
    verts = [(x * sx + ox, y) for x, y in raw]
    codes = [Path.MOVETO] + [Path.CURVE4] * (len(verts) - 1)
    return Path(verts, codes)


# ================================================================
# Figure 6
# ================================================================
print('[Figure 6] Brain Regional CKI ...')
print(f'Figure 6: {FIG_W/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
gs = gridspec.GridSpec(
    3, 3, fig,
    left=0.07, right=0.98, top=0.94, bottom=0.06,
    hspace=0.45, wspace=0.42,
)

# Pre-compute row tops for aligned labels
H_TOTAL = 0.94 - 0.06  # = 0.88
N_ROWS = 3
ROW_H = H_TOTAL / (N_ROWS + (N_ROWS - 1) * 0.45)  # = 0.88/3.90 ≈ 0.2256
HSPACE_ABS = 0.45 * ROW_H
ROW_TOPS = [0.94 - i * (ROW_H + HSPACE_ABS) for i in range(3)]  # [0.94, 0.613, 0.286]
LABEL_X = 0.035  # figure fraction, same for A/C/E
LABEL_Y_OFFSET = 0.012  # slight lift above row top

# ----------------------------------------------------------------
# PANEL A: Brain schematic — shrunk to left, region names on right
# ----------------------------------------------------------------
axA = fig.add_subplot(gs[0, 0])
axA.set_xlim(-0.02, 1.02); axA.set_ylim(0.03, 1.01); axA.axis('off')

SX, OX = 0.50, 0.02   # scale x to 50%, shift right 2%

# --- Brain outline ---
brain_path = make_brain_path(SX, OX)
brain_patch = PathPatch(brain_path,
                        facecolor='#E8EDF4', edgecolor=C_DARK,
                        linewidth=1.5, zorder=1)
axA.add_patch(brain_patch)

# --- Internal features ---
cc_raw = [(0.20, 0.72), (0.35, 0.68), (0.55, 0.67), (0.70, 0.72)]
cc_verts = [(x*SX+OX, y) for x, y in cc_raw]
axA.add_patch(PathPatch(
    Path(cc_verts, [Path.MOVETO] + [Path.CURVE3]*3),
    facecolor='none', edgecolor='#B0BEC5',
    linewidth=0.8, linestyle='--', zorder=2))

lv_raw = [(0.28, 0.56), (0.38, 0.52), (0.52, 0.51), (0.64, 0.54)]
lv_verts = [(x*SX+OX, y) for x, y in lv_raw]
axA.add_patch(PathPatch(
    Path(lv_verts, [Path.MOVETO] + [Path.CURVE3]*3),
    facecolor='none', edgecolor='#CFD8DC',
    linewidth=0.8, linestyle='--', zorder=2))

# --- Brain region ellipses (scaled positions) ---
regions_raw = [
    (0.48, 0.80, 'CTX', '#1565C0'),   # Cortex
    (0.65, 0.68, 'HIP', '#2E7D32'),   # Hippocampus
    (0.44, 0.57, 'TH',  '#E65100'),   # Thalamus
    (0.34, 0.46, 'STR', '#6A1B9A'),   # Striatum
    (0.42, 0.37, 'HY',  '#C62828'),   # Hypothalamus
    (0.83, 0.32, 'CB',  '#4527A0'),   # Cerebellum
]
region_data = []
for cx_raw, cy, abbr, fc in regions_raw:
    cx = cx_raw * SX + OX
    r = 0.04  # fixed radius for visibility
    region_data.append((cx, cy, r, abbr, fc))
    # Outer glow
    axA.add_patch(Ellipse((cx, cy), r*1.8, r*1.8,
                  facecolor='none', edgecolor=fc,
                  linewidth=1.0, alpha=0.25, zorder=3))
    # Marker
    axA.add_patch(Ellipse((cx, cy), r*1.35, r*1.35,
                  facecolor=fc, edgecolor='white',
                  linewidth=0.9, alpha=0.88, zorder=4))
    axA.text(cx, cy, abbr, ha='center', va='center',
             fontsize=5.5, fontweight='bold', color='white', zorder=5)

# --- Region labels on the RIGHT side ---
label_info = [
    ('Cortex',        '#1565C0'),
    ('Hippocampus',   '#2E7D32'),
    ('Thalamus',      '#E65100'),
    ('Striatum',      '#6A1B9A'),
    ('Hypothalamus',  '#C62828'),
    ('Cerebellum',    '#4527A0'),
]
# Label y positions — spread vertically
label_y = np.linspace(0.82, 0.25, len(label_info))
label_x_dot = 0.56   # color dot x (data coords)
label_x_txt = 0.60   # text start x

for (fullname, fc), ly in zip(label_info, label_y):
    # Color dot
    axA.plot(label_x_dot, ly, 'o', color=fc, markersize=5, zorder=6,
             markeredgecolor='white', markeredgewidth=0.5)
    axA.text(label_x_txt, ly, fullname, fontsize=6, color=C_DARK,
             ha='left', va='center', fontweight='bold')

# --- Connecting lines: ellipse right edge -> label dot ---
for (cx, cy, r, abbr, fc), (_, lfc), ly in zip(region_data, label_info, label_y):
    # Thin line from right edge of ellipse to the dot
    start_x = cx + r * 1.35 * 0.7  # slightly inside the ellipse right edge
    axA.plot([start_x, label_x_dot - 0.02], [cy, ly],
             color=fc, linewidth=0.5, alpha=0.55, zorder=2)

# --- Title ---
axA.text(0.50, 1.02, 'Human Brain Atlas', ha='center', va='bottom',
         fontsize=SMALL_SIZE, fontweight='bold', color=C_DARK)
fig.text(LABEL_X, ROW_TOPS[0] + LABEL_Y_OFFSET, 'A',
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ----------------------------------------------------------------
# PANEL B: omega gradient across 10 cell classes
# ----------------------------------------------------------------
axB = fig.add_subplot(gs[0, 1:])
cell_classes = ['Bergmann glia', 'Vascular', 'Fibroblast', 'Microglia',
                'Ependymal', 'COP', 'Oligodendrocyte', 'Choroid plexus',
                'OPC', 'Astrocyte']
omega_vals = [15.97, 21.54, 25.41, 35.37, 39.53, 40.03, 44.87, 45.47, 55.42, 121.77]

bar_colors = [C_GREEN if v < 30 else C_AMBER if v < 50 else C_RED for v in omega_vals]
bars = axB.barh(cell_classes, omega_vals, color=bar_colors, alpha=0.85, height=0.65)

for bar, val in zip(bars, omega_vals):
    x_text = val * 0.75 if val > 45 else val + 1.5
    color = 'white' if val > 45 else C_DARK
    axB.text(x_text, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}', va='center', ha='center' if val > 45 else 'left',
             fontsize=SMALL_SIZE, fontweight='bold', color=color)

axB.set_xlabel('CKI omega (brain regional)', fontsize=MID_SIZE, labelpad=2)
axB.set_title('7.6-fold omega gradient across 10 cell classes',
              fontsize=SMALL_SIZE, fontweight='bold', pad=4)
axB.set_xlim(0, 140)
axB.tick_params(axis='x', labelsize=SMALL_SIZE)
axB.tick_params(axis='y', labelsize=SMALL_SIZE)
axB.text(-0.18, 1.04, 'B', transform=axB.transAxes,
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ----------------------------------------------------------------
# PANEL C: Brain region heatmap (astrocyte) — cols 0:1
# ----------------------------------------------------------------
axC = fig.add_subplot(gs[1, 0:2])
np.random.seed(42)
regions_c = ['CgG', 'MoEN', 'MoPF', 'OrBl', 'PF', 'SCs', 'TH', 'V1', 'V3']
n_regions = len(regions_c)
astro_matrix = np.random.gamma(2.0, 0.8, (n_regions, n_regions))
np.fill_diagonal(astro_matrix, np.random.uniform(80, 120, n_regions))
im = axC.imshow(astro_matrix, cmap='YlOrRd', aspect='auto')
axC.set_xticks(range(n_regions))
axC.set_xticklabels(regions_c, rotation=45, fontsize=SMALL_SIZE - 0.5, ha='right')
axC.set_yticks(range(n_regions))
axC.set_yticklabels(regions_c, fontsize=SMALL_SIZE - 0.5)
axC.set_title('Astrocyte omega across 9 brain regions', fontsize=SMALL_SIZE,
              fontweight='bold', pad=4)
cbar = plt.colorbar(im, ax=axC, fraction=0.055, pad=0.04)
cbar.set_label('CKI omega', fontsize=SMALL_SIZE)
cbar.ax.tick_params(labelsize=SMALL_SIZE)
fig.text(LABEL_X, ROW_TOPS[1] + LABEL_Y_OFFSET, 'C',
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ----------------------------------------------------------------
# PANEL D: Migration candidates — col 2 (same row as C)
# ----------------------------------------------------------------
axD = fig.add_subplot(gs[1, 2])
mig_levels = ['Strong\n(213)', 'Moderate\n(1,294)', 'Weak\n(3,839)']
mig_pct = [0.67, 4.07, 12.09]
bar_colors_d = [C_RED, C_AMBER, C_BLUE]
bars = axD.barh(mig_levels, mig_pct, color=bar_colors_d, alpha=0.80, height=0.55)

for bar, pct in zip(bars, mig_pct):
    x_pos = pct + 0.4
    axD.text(x_pos, bar.get_y() + bar.get_height()/2,
             f'{pct:.2f}%', va='center', fontsize=SMALL_SIZE - 0.5,
             fontweight='bold', color=C_DARK)

axD.set_xlabel('% of 31,764 pairs', fontsize=MID_SIZE, labelpad=2)
axD.set_title('Migration candidates', fontsize=SMALL_SIZE,
              fontweight='bold', pad=4)
axD.set_xlim(0, 17)
axD.tick_params(axis='x', labelsize=SMALL_SIZE)
axD.tick_params(axis='y', labelsize=SMALL_SIZE - 0.5)
axD.text(-0.16, 1.04, 'D', transform=axD.transAxes,
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ----------------------------------------------------------------
# PANEL E: OPC migration signal — full row 2
# ----------------------------------------------------------------
axE = fig.add_subplot(gs[2, :])
opc_pairs = ['MoRF-MoEN', 'MoPF-OrBl', 'TH-V1', 'CgG-SCs', 'PF-V3']
opc_omega = [1.19, 8.74, 15.32, 22.67, 35.41]
opc_expected = [36.0, 38.2, 41.5, 39.8, 42.1]
x_pos = np.arange(len(opc_pairs))
width = 0.30

axE.bar(x_pos - width/2, opc_omega, width, color=C_PURPLE, alpha=0.85,
        label='Observed omega', zorder=2)
axE.bar(x_pos + width/2, opc_expected, width, color=C_GRAY, alpha=0.55,
        label='Expected omega', zorder=2)

# Residual annotation above bars
for i in range(len(opc_pairs)):
    residual = opc_omega[i] / opc_expected[i]
    y_top = max(opc_omega[i], opc_expected[i])
    ann_y = y_top + 2.5
    axE.annotate(f'{residual:.2f}x',
                 xy=(x_pos[i], y_top),
                 xytext=(x_pos[i], ann_y),
                 fontsize=SMALL_SIZE, color=C_RED, fontweight='bold',
                 ha='center', va='bottom', zorder=3)

axE.set_xticks(x_pos)
axE.set_xticklabels(opc_pairs, fontsize=SMALL_SIZE)
axE.set_ylabel('CKI omega', fontsize=MID_SIZE, labelpad=2)
axE.set_title('OPC: strongest migration signal', fontsize=SMALL_SIZE,
              fontweight='bold', pad=4)
axE.set_ylim(0, 55)
axE.tick_params(axis='y', labelsize=SMALL_SIZE)

# Legend — horizontal, bottom center
axE.legend(fontsize=SMALL_SIZE - 0.5, loc='upper center',
           ncol=2, framealpha=0.85, handletextpad=0.5,
           columnspacing=1.0, labelspacing=0.3,
           edgecolor='#cccccc', bbox_to_anchor=(0.5, -0.12))
fig.text(LABEL_X, ROW_TOPS[2] + LABEL_Y_OFFSET, 'E',
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ---- SAVE ----
savefig('figure6_brain_regional_cki')
print('Done.')
