"""Figure 6: Brain Regional CKI & Region-associated

Layout: 3x3 GridSpec
All fonts >= 7pt, panel labels 9pt bold, no tight_layout().
Presentation only: shared style via _fig_style (st.*).

v38 fix: all panel data now loaded dynamically from the block-shuffle
authoritative sources:
  - results/brain_bs_null_results.csv  (mu_ct class means, astrocyte region
    matrix, tier counts, OPC Strong candidates)
  - results/brain_bs_null_summary.txt  (tier counts cross-check)
No hardcoded landscape values remain.
"""

import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import _fig_style as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Arc, Ellipse, PathPatch
from matplotlib.path import Path
import numpy as np
import pandas as pd

# ---- Layout constants ----
DPI = st.DPI
MM = st.MM
FIG_W = st.DOUBLE   # 178 mm NAR double column
FIG_H = 150 * MM

# ---- Font sizes (shared, floor 7pt) ----
LABEL_SIZE = st.LABEL_SIZE   # 9
SMALL_SIZE = st.SMALL_SIZE   # 7
MID_SIZE   = st.BODY_SIZE    # 8

# ---- Colors (shared palette) ----
C_BLUE   = st.C_BLUE
C_GREEN  = st.C_GREEN
C_RED    = st.C_RED
C_AMBER  = st.C_AMBER
C_ORANGE = st.C_ORANGE
C_PURPLE = st.C_PURPLE
C_TEAL   = st.C_TEAL
C_GRAY   = st.C_STEEL
C_DARK   = st.C_DARK

# ---- Output directory ----
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'figures_final')
os.makedirs(OUTDIR, exist_ok=True)

# ---- Data directory ----
RESDIR = os.path.join(os.path.dirname(__file__), '..', 'results')

# ================================================================
# Authoritative data: block-shuffle null results (v38)
# ================================================================
print('[Figure 6] Loading block-shuffle authoritative data ...')
bs = pd.read_csv(os.path.join(RESDIR, 'brain_bs_null_results.csv'))
n_pairs_total = len(bs)

# Class-mean omega (mu_ct) per cell type, ascending
CLASS_SHORT = {
    'Oligodendrocyte precursor': 'OPC',
    'Committed oligodendrocyte precursor': 'COP',
    'Oligodendrocyte': 'ODC',
}
mu_ct = bs.groupby('cell_type')['mu_ct'].first().sort_values()
cell_classes = [CLASS_SHORT.get(ct, ct) for ct in mu_ct.index]
omega_vals = mu_ct.values.tolist()
omega_fold = mu_ct.max() / mu_ct.min()
print(f'  class means: {dict(zip(cell_classes, [round(v,2) for v in omega_vals]))}')
print(f'  fold = {omega_fold:.2f}')

# Tier counts from CSV, cross-checked against summary.txt
tier_counts = {t: int((bs['tier'] == t).sum()) for t in ('Strong', 'Moderate', 'Weak')}
tier_pct = {t: 100.0 * n / n_pairs_total for t, n in tier_counts.items()}
with open(os.path.join(RESDIR, 'brain_bs_null_summary.txt')) as fh:
    summary_txt = fh.read()
for t in ('Strong', 'Moderate', 'Weak'):
    m = re.search(rf'{t}\s+n=\s*(\d+)', summary_txt)
    assert m and int(m.group(1)) == tier_counts[t], \
        f'tier count mismatch for {t}: CSV={tier_counts[t]} summary={m.group(1) if m else None}'
print(f'  tiers (CSV==summary): {tier_counts} of {n_pairs_total:,} pairs')

# Astrocyte region-pair matrix (representative regions: top 10 by
# Strong/Moderate candidate involvement)
ast = bs[bs['cell_type'] == 'Astrocyte']
cand = ast[ast['tier'].isin(['Strong', 'Moderate'])]
involvement = {}
for _, r in cand.iterrows():
    involvement[r['region_a']] = involvement.get(r['region_a'], 0) + 1
    involvement[r['region_b']] = involvement.get(r['region_b'], 0) + 1
top_regions = [rg for rg, _ in sorted(involvement.items(),
                                       key=lambda kv: -kv[1])[:10]]
rg_idx = {rg: i for i, rg in enumerate(top_regions)}
astro_matrix = np.full((len(top_regions), len(top_regions)), np.nan)
for _, r in ast.iterrows():
    ia, ib = rg_idx.get(r['region_a']), rg_idx.get(r['region_b'])
    if ia is not None and ib is not None:
        astro_matrix[ia, ib] = r['omega']
        astro_matrix[ib, ia] = r['omega']
region_labels = [rg.replace('Human ', '') for rg in top_regions]
print(f'  astrocyte matrix: {len(top_regions)} representative regions, '
      f'{int((~np.isnan(astro_matrix)).sum())} filled cells')

# Top 5 strongest OPC Strong candidates (lowest residuals)
opc = bs[(bs['cell_type'] == 'Oligodendrocyte precursor') & (bs['tier'] == 'Strong')]
opc_top = opc.sort_values('residual').head(5)
opc_pairs = [f"{r['region_a'].replace('Human ', '')}-"
             f"{r['region_b'].replace('Human ', '')}" for _, r in opc_top.iterrows()]
opc_omega = opc_top['omega'].tolist()
opc_expected = opc_top['expected_omega'].tolist()
opc_residual = opc_top['residual'].tolist()
print(f'  OPC Strong: {len(opc)} total; top5 = {opc_pairs}')


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
    left=0.07, right=0.98, top=0.93, bottom=0.06,
    hspace=0.48, wspace=0.45,
)

# Pre-compute row tops for aligned labels
H_TOTAL = 0.93 - 0.06  # = 0.87
N_ROWS = 3
ROW_H = H_TOTAL / (N_ROWS + (N_ROWS - 1) * 0.48)  # ≈0.2253
HSPACE_ABS = 0.48 * ROW_H
ROW_TOPS = [0.93 - i * (ROW_H + HSPACE_ABS) for i in range(3)]
LABEL_X = 0.035
LABEL_Y_OFFSET = 0.012

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
# Reuse the original six regions (CTX/HIP/TH/STR/HY/CB) — palette-mapped
regions_raw = [
    (0.48, 0.80, 'CTX', C_BLUE),     # Cortex
    (0.65, 0.68, 'HIP', C_GREEN),    # Hippocampus
    (0.44, 0.57, 'TH',  C_AMBER),    # Thalamus
    (0.34, 0.46, 'STR', C_PURPLE),   # Striatum
    (0.42, 0.37, 'HY',  C_RED),      # Hypothalamus
    (0.83, 0.32, 'CB',  C_TEAL),     # Cerebellum
]
region_data = []
R = 0.052  # enlarged to fit 7pt label
for cx_raw, cy, abbr, fc in regions_raw:
    cx = cx_raw * SX + OX
    region_data.append((cx, cy, R, abbr, fc))
    # Outer glow
    axA.add_patch(Ellipse((cx, cy), R*1.8, R*1.8,
                  facecolor='none', edgecolor=fc,
                  linewidth=1.0, alpha=0.25, zorder=3))
    # Marker
    axA.add_patch(Ellipse((cx, cy), R*1.35, R*1.35,
                  facecolor=fc, edgecolor='white',
                  linewidth=0.9, alpha=0.92, zorder=4))
    axA.text(cx, cy, abbr, ha='center', va='center',
             fontsize=SMALL_SIZE, fontweight='bold', color='white', zorder=5)

# --- Region labels on the RIGHT side ---
label_info = [
    ('Cortex',        C_BLUE),
    ('Hippocampus',   C_GREEN),
    ('Thalamus',      C_AMBER),
    ('Striatum',      C_PURPLE),
    ('Hypothalamus',  C_RED),
    ('Cerebellum',    C_TEAL),
]
label_y = np.linspace(0.82, 0.25, len(label_info))
label_x_dot = 0.56
label_x_txt = 0.60

for (fullname, fc), ly in zip(label_info, label_y):
    axA.plot(label_x_dot, ly, 'o', color=fc, markersize=5, zorder=6,
             markeredgecolor='white', markeredgewidth=0.5)
    axA.text(label_x_txt, ly, fullname, fontsize=SMALL_SIZE, color=C_DARK,
             ha='left', va='center', fontweight='bold')

# --- Connecting lines: ellipse right edge -> label dot ---
for (cx, cy, r, abbr, fc), (_, lfc), ly in zip(region_data, label_info, label_y):
    start_x = cx + r * 1.35 * 0.7
    axA.plot([start_x, label_x_dot - 0.02], [cy, ly],
             color=fc, linewidth=0.5, alpha=0.55, zorder=2)

# --- Title ---
axA.text(0.50, 1.02, 'Human Brain Atlas', ha='center', va='bottom',
         fontsize=SMALL_SIZE, fontweight='bold', color=C_DARK)
fig.text(LABEL_X, ROW_TOPS[0] + LABEL_Y_OFFSET, 'A',
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ----------------------------------------------------------------
# PANEL B: omega gradient across 10 cell classes (mu_ct, block-shuffle)
# ----------------------------------------------------------------
axB = fig.add_subplot(gs[0, 1:])

bar_colors = [C_GREEN if v < 25 else C_AMBER if v < 45 else C_RED
              for v in omega_vals]
bars = axB.barh(cell_classes, omega_vals, color=bar_colors, alpha=0.92,
                edgecolor=C_DARK, linewidth=0.5, height=0.65, zorder=3)

for bar, val in zip(bars, omega_vals):
    x_text = val * 0.75 if val > 60 else val + 1.5
    color = 'white' if val > 60 else C_DARK
    axB.text(x_text, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}', va='center', ha='center' if val > 60 else 'left',
             fontsize=SMALL_SIZE, fontweight='bold', color=color)

axB.set_xlabel('CKI omega (brain regional)', fontsize=MID_SIZE, labelpad=2)
axB.set_title(f'{omega_fold:.2f}-fold omega gradient across 10 cell classes',
              fontsize=SMALL_SIZE, fontweight='bold', pad=4)
axB.set_xlim(0, 90)
axB.tick_params(axis='x', labelsize=SMALL_SIZE)
axB.tick_params(axis='y', labelsize=SMALL_SIZE)
st.subtle_grid(axB, axis='x')
st.despine(axB)
st.add_panel_label(fig, axB, 'B', x=-0.14, y=1.04)

# ----------------------------------------------------------------
# PANEL C: Astrocyte region x region omega matrix (block-shuffle data)
# ----------------------------------------------------------------
axC = fig.add_subplot(gs[1, 0:2])
n_regions = len(region_labels)
masked = np.ma.masked_invalid(astro_matrix)
cmap = plt.cm.YlOrRd.copy()
cmap.set_bad('#F4F6F8')
im = axC.imshow(masked, cmap=cmap, aspect='auto')
axC.set_xticks(range(n_regions))
axC.set_xticklabels(region_labels, rotation=45, fontsize=SMALL_SIZE, ha='right')
axC.set_yticks(range(n_regions))
axC.set_yticklabels(region_labels, fontsize=SMALL_SIZE)
axC.set_title('Astrocyte omega across 10 representative regions',
              fontsize=SMALL_SIZE, fontweight='bold', pad=4)
# thin cell frame
axC.set_xticks(np.arange(-0.5, n_regions, 1), minor=True)
axC.set_yticks(np.arange(-0.5, n_regions, 1), minor=True)
axC.grid(which='minor', color='white', linewidth=0.7)
axC.tick_params(which='minor', length=0)
for sp in axC.spines.values():
    sp.set_visible(True)
    sp.set_linewidth(0.6)
    sp.set_edgecolor('#3A3A3A')
cbar = plt.colorbar(im, ax=axC, fraction=0.055, pad=0.04)
cbar.set_label('CKI omega', fontsize=SMALL_SIZE)
cbar.ax.tick_params(labelsize=SMALL_SIZE, width=0.6, length=2.5)
cbar.outline.set_linewidth(0.6)
cbar.outline.set_edgecolor('#3A3A3A')
fig.text(LABEL_X, ROW_TOPS[1] + LABEL_Y_OFFSET, 'C',
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ----------------------------------------------------------------
# PANEL D: Region-associated candidate tiers — col 2 (same row as C)
# ----------------------------------------------------------------
axD = fig.add_subplot(gs[1, 2])
mig_levels = [f'Strong\n({tier_counts["Strong"]:,})',
              f'Moderate\n({tier_counts["Moderate"]:,})',
              f'Weak\n({tier_counts["Weak"]:,})']
mig_pct = [tier_pct['Strong'], tier_pct['Moderate'], tier_pct['Weak']]
bar_colors_d = [C_RED, C_AMBER, C_BLUE]
bars = axD.barh(mig_levels, mig_pct, color=bar_colors_d, alpha=0.92,
                edgecolor=C_DARK, linewidth=0.5, height=0.55, zorder=3)

for bar, pct in zip(bars, mig_pct):
    x_pos = pct + 0.6
    axD.text(x_pos, bar.get_y() + bar.get_height()/2,
             f'{pct:.2f}%', va='center', fontsize=SMALL_SIZE,
             fontweight='bold', color=C_DARK)

axD.set_xlabel(f'% of {n_pairs_total:,} pairs', fontsize=MID_SIZE, labelpad=2)
axD.set_title('Region-associated candidates', fontsize=SMALL_SIZE,
              fontweight='bold', pad=4)
axD.set_xlim(0, 26)
axD.tick_params(axis='x', labelsize=SMALL_SIZE)
axD.tick_params(axis='y', labelsize=SMALL_SIZE)
st.subtle_grid(axD, axis='x')
st.despine(axD)
st.add_panel_label(fig, axD, 'D', x=-0.16, y=1.04)

# ----------------------------------------------------------------
# PANEL E: Top 5 strongest OPC Strong candidates — full row 2
# ----------------------------------------------------------------
axE = fig.add_subplot(gs[2, :])
x_pos = np.arange(len(opc_pairs))
width = 0.30

axE.bar(x_pos - width/2, opc_omega, width, color=C_PURPLE, alpha=0.92,
        label='Observed omega', edgecolor=C_DARK, linewidth=0.5, zorder=2)
axE.bar(x_pos + width/2, opc_expected, width, color=C_GRAY, alpha=0.55,
        label='Expected omega', edgecolor=C_DARK, linewidth=0.5, zorder=2)

# Residual annotation above bars
for i in range(len(opc_pairs)):
    y_top = max(opc_omega[i], opc_expected[i])
    ann_y = y_top + 2.0
    axE.annotate(f'res={opc_residual[i]:.2f}',
                 xy=(x_pos[i], y_top),
                 xytext=(x_pos[i], ann_y),
                 fontsize=SMALL_SIZE, color=C_RED, fontweight='bold',
                 ha='center', va='bottom', zorder=3)

axE.set_xticks(x_pos)
axE.set_xticklabels(opc_pairs, fontsize=SMALL_SIZE)
axE.set_ylabel('CKI omega', fontsize=MID_SIZE, labelpad=2)
axE.set_title('OPC: five strongest region-associated candidates (lowest residuals)',
              fontsize=SMALL_SIZE, fontweight='bold', pad=4)
axE.set_ylim(0, 55)
axE.tick_params(axis='y', labelsize=SMALL_SIZE)

axE.legend(fontsize=SMALL_SIZE, loc='upper center',
           ncol=2, frameon=False, handletextpad=0.5,
           columnspacing=1.2, labelspacing=0.3,
           bbox_to_anchor=(0.5, -0.10))
fig.text(LABEL_X, ROW_TOPS[2] + LABEL_Y_OFFSET, 'E',
         fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

# ---- SAVE ----
savefig('figure6_brain_regional_cki')
print('Done.')
