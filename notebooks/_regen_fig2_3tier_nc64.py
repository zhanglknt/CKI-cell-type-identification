#!/usr/bin/env python3
"""NC Figure 2, three-tier layout: (a)(b) / (c)(d) / (e).

Replaces the 3+2 layout (a-c top, d-e bottom) with three stacked tiers so that
each panel gets a wider, taller box; value labels, legends and annotation boxes
no longer crowd the plotted marks.

Data sources are exactly those of the previous generators
(_regen_fig2_toprow_nc49.py, _regen_fig2_bottomrow_v497.py) and the numeric
assertions on the ROC AUCs are carried over verbatim, so every number in the
figure stays identical to the manuscript.

Style: Arial everywhere (mathtext included), Type 42 embedded, panel labels
'(a)'..'(e)' bold 9 pt, all body text >= 7 pt (NC floor).

Output: results/figures_final/_fig2_3tier_nc64.pdf  (+ PNG preview)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _fig_style as st

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_curve, roc_auc_score
import json
import warnings
warnings.filterwarnings('ignore')

MM = st.MM
DPI = st.DPI
OUT_PDF = Path('results/figures_final/_fig2_3tier_nc64.pdf')
OUT_PNG = Path('results/audit/_fig2_3tier_nc64.png')
OUT_PDF.parent.mkdir(parents=True, exist_ok=True)

st.apply_style()
matplotlib.rcParams.update({
    'mathtext.fontset': 'custom',
    'mathtext.rm': 'Arial',
    'mathtext.it': 'Arial:italic',
    'mathtext.bf': 'Arial:bold',
    'mathtext.default': 'regular',
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
})

SMALL = st.SMALL_SIZE   # 7  ticks / legends
BODY = st.BODY_SIZE     # 8  axis labels
TITLE = st.TITLE_SIZE   # 9  panel titles
LABEL = st.LABEL_SIZE   # 9  panel letters

# =========================== data (unchanged) ===============================
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

corr = np.load('results/figure_data_correlations.npy', allow_pickle=True).item()
C = corr['corr_matrix']
M3 = corr['metrics_3a']   # ['CKI \u03c9','Cosine','Raw JS','Marker Jaccard','Spearman']

raw = pd.read_csv('results/groundtruth_simulation_raw.csv')
pos = raw[(raw['series'] == 'signal') & (raw['delta'] >= 0.25)]
neg = raw[raw['series'].isin(['neutral_hk', 'neutral_global'])]
y = np.array([1] * len(pos) + [0] * len(neg))
vals = pd.concat([pos, neg])
met_keys = ['omega', 'k_f', 'k_total', 'cosine', 'kf_over_kt', 'k_n']
met_disp = ['CKI \u03c9', r'$k_f$', r'$k_{total}$', 'Cosine',
            r'$k_f$/$k_{total}$', r'$k_n$']
aucs = {m: roc_auc_score(y, vals[m]) for m in met_keys}
ref = json.load(open('results/groundtruth_simulation_metrics.json'))['auc_signal_vs_neutral']
for m in met_keys:
    assert abs(aucs[m] - ref[m]) < 5e-4, (m, aucs[m], ref[m])
bg2 = json.load(open('results/groundtruth_simulation_background2_metrics.json'))
bg2_omega = bg2['auc_signal_vs_neutral']['omega']
assert abs(bg2_omega - 0.9076) < 5e-4
assert abs(aucs['omega'] - 0.8042) < 5e-4
print('AUC check OK: marrow omega=%.4f, skin omega=%.4f' % (aucs['omega'], bg2_omega))

# ============================ figure layout =================================
FIG_W_MM = 178.0
FIG_H_MM = 208.0
fig = plt.figure(figsize=(FIG_W_MM * MM, FIG_H_MM * MM), dpi=DPI)

# hspace is sized so the tier gap clears the longest rotated tick label of the
# tier above plus the title block of the tier below.
gs = gridspec.GridSpec(
    3, 2, figure=fig,
    left=0.075, right=0.935, top=0.966, bottom=0.034,
    hspace=0.493, wspace=0.30,
    height_ratios=[1.105, 1.00, 1.737],
)

axA = fig.add_subplot(gs[0, 0])
axB = fig.add_subplot(gs[0, 1])
axC = fig.add_subplot(gs[1, 0])
axD = fig.add_subplot(gs[1, 1])
axE = fig.add_subplot(gs[2, :])

# Tier 3: align (e) with the FIRST column (same x as a and c) and make it tall.
# Centring it would put it under (d), whose rotated x tick labels hang ~14 mm
# below its axes and would collide with (e)'s two-line title.
posE = axE.get_position()
_w = 0.4494                       # 80 mm wide: stops 6 mm short of column 2
axE.set_position([axA.get_position().x0, posE.y0, _w, posE.height])


def panel_label(ax, text, dx=-0.115, dy=1.05):
    """Arial bold 9 pt label anchored just outside the top-left of the axes."""
    bb = ax.get_position()
    fig.text(bb.x0 + dx * bb.width, bb.y0 + dy * bb.height, text,
             fontsize=LABEL, fontweight='bold', ha='left', va='top')


# ---------------------------- (a) k_n calibration ---------------------------
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
axA.set_ylim(0, 5.2)
axA.set_title('k$_n$ calibration (split-half controls)', fontsize=TITLE,
              fontweight='bold', pad=5)
st.despine(axA)
st.subtle_grid(axA)
panel_label(axA, '(a)')

# ------------------------- (b) k_n / k_f decomposition ----------------------
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
axB.legend(fontsize=SMALL, loc='upper left', frameon=False,
           handlelength=1.2, handletextpad=0.5)
for xi, kv, fv in zip(x, kn_med, kf_med):
    axB.text(xi - width / 2, kv * 1.45, f'{kv:.1e}', fontsize=SMALL,
             ha='center', va='bottom', color=st.C_BLUE)
    axB.text(xi + width / 2, fv * 1.45, f'{fv:.1e}', fontsize=SMALL,
             ha='center', va='bottom', color=st.C_DARK)
axB.set_ylim(6e-5, 2.5)      # tight: value labels sit ~1/10 decade below the top
axB.set_title('k$_n$ / k$_f$ decomposition', fontsize=TITLE,
              fontweight='bold', pad=5)
st.despine(axB)
st.subtle_grid(axB)
panel_label(axB, '(b)')

# --------------------------- (c) omega by category --------------------------
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
              fontweight='bold', pad=5)
axC.text(0.03, 0.04, f'X vs. C one-sided Mann-Whitney\nP = {p_val:.3f}',
         transform=axC.transAxes, fontsize=SMALL, va='bottom', ha='left',
         color=st.C_DARK,
         bbox=dict(facecolor='white', edgecolor=st.C_LIGHT_GRAY,
                   linewidth=0.5, alpha=0.9))
st.despine(axC)
st.subtle_grid(axC, axis='x')
panel_label(axC, '(c)')

# --------------------- (d) Tabula Sapiens correlation -----------------------
im = axD.imshow(C, cmap='RdBu_r', vmin=-1, vmax=1)

# imshow shrinks the axes to a square and centres it in its grid cell; force it
# back to the column start so (d) lines up with (b) above it.
_d = axD.get_position()
_col_x = axB.get_position().x0
_side = _d.height                      # height fraction == square side in mm
axD.set_position([_col_x, _d.y0, _side * FIG_H_MM / FIG_W_MM, _d.height])

axD.set_xticks(range(5)); axD.set_yticks(range(5))
axD.set_xticklabels(M3, fontsize=SMALL, rotation=38, ha='right')
axD.set_yticklabels(M3, fontsize=SMALL)
for i in range(5):
    for j in range(5):
        axD.text(j, i, f'{C[i, j]:.2f}', ha='center', va='center',
                 fontsize=SMALL, color='black' if abs(C[i, j]) < 0.75 else 'white')
# left-aligned: a centred title would reach back over the '(d)' label
axD.set_title('Tabula Sapiens pairs: metric correlation', fontsize=TITLE,
              fontweight='bold', pad=5, loc='left')
for s in axD.spines.values():
    s.set_visible(False)
axD.tick_params(length=0)
# anchored outside the top-left of the (narrow) heatmap box, clear of the
# centred title which starts at ~96 mm
panel_label(axD, '(d)', dx=-0.30)

# colorbar aligned with the rendered (square) heatmap box
dbb = axD.get_position()
side = min(dbb.width, dbb.height)
cbar_y0 = dbb.y0 + (dbb.height - side) / 2
axCB = fig.add_axes([dbb.x0 + dbb.width + 0.018, cbar_y0, 0.012, side])
cb = fig.colorbar(im, cax=axCB)
cb.ax.tick_params(labelsize=SMALL, length=2)
cb.set_label("Pearson's r", fontsize=SMALL)
cb.outline.set_linewidth(0.6)

# ------------------------- (e) change-detection ROC -------------------------
colors = {'omega': '#C8102E', 'k_f': '#2166AC', 'k_total': '#1B7837',
          'cosine': '#E08214', 'kf_over_kt': '#762A83', 'k_n': '#636363'}
for m, d in zip(met_keys, met_disp):
    fpr, tpr, _ = roc_curve(y, vals[m])
    lw = 1.8 if m == 'omega' else 1.0
    zo = 10 if m == 'omega' else 5
    axE.plot(fpr, tpr, color=colors[m], lw=lw, zorder=zo,
             label=f'{d} ({aucs[m]:.2f})')
axE.plot([0, 1], [0, 1], ls='--', lw=0.7, color='#999999', zorder=1)
axE.set_xlim(0, 1); axE.set_ylim(0, 1.02)
axE.set_xlabel('False positive rate', fontsize=BODY)
axE.set_ylabel('True positive rate', fontsize=BODY)
axE.tick_params(labelsize=SMALL)
axE.set_title('Functional-change vs neutral-drift detection\n'
              f'replicated on skin background: CKI \u03c9 AUC = {bg2_omega:.2f} (rank 1/6)',
              fontsize=TITLE, fontweight='bold', pad=5, loc='left')
leg = axE.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=SMALL,
                 frameon=True, framealpha=1.0, edgecolor='#CCCCCC',
                 borderpad=0.5, labelspacing=0.45, handlelength=1.7,
                 handletextpad=0.6)
leg.set_zorder(20)
st.despine(axE)
panel_label(axE, '(e)', dx=-0.095)

# ================================= save =====================================
fig.savefig(OUT_PDF, dpi=DPI, facecolor='white',
            metadata={'Creator': 'CKI NC Figures'})
fig.savefig(OUT_PNG, dpi=150, facecolor='white')
print('saved', OUT_PDF, 'and', OUT_PNG)

# ---------------------------- layout geometry audit --------------------------
import math
print('\n--- layout geometry (mm) ---')
for nm, ax in [('a', axA), ('b', axB), ('c', axC), ('d', axD), ('e', axE)]:
    bb = ax.get_position()
    print(f'  {nm}: x0={bb.x0*FIG_W_MM:6.1f}  w={bb.width*FIG_W_MM:6.1f}  '
          f'y0={bb.y0*FIG_H_MM:6.1f}  h={bb.height*FIG_H_MM:6.1f}')

# (a) six wrapped two-line tick labels, rotated 42 deg
a_sp = axA.get_position().width * FIG_W_MM / 6          # mm between ticks
a_sep_pt = a_sp * math.sin(math.radians(42)) * 72 / 25.4
print(f'  (a) tick spacing {a_sp:.1f} mm -> normal separation {a_sep_pt:.1f} pt '
      f'vs 2-line glyph block 14 pt -> {"OK" if a_sep_pt > 14 else "TIGHT"}')
a_ext = (18.0 * math.sin(math.radians(42)) + 5.0 * math.cos(math.radians(42)))
gap_mm = (axA.get_position().y0 - (axC.get_position().y0 + axC.get_position().height)) * FIG_H_MM
print(f'  (a) label vertical extent ~{a_ext:.1f} mm vs tier gap {gap_mm:.1f} mm '
      f'-> {"OK" if a_ext < gap_mm else "OVERLAP RISK"}')

# (d) five rotated single-line tick labels, rotation 38 deg, square cells
d_side = min(axD.get_position().width * FIG_W_MM, axD.get_position().height * FIG_H_MM)
d_sep_pt = (d_side / 5) * math.sin(math.radians(38)) * 72 / 25.4
print(f'  (d) heatmap side {d_side:.1f} mm, cell {d_side/5:.1f} mm -> normal '
      f'separation {d_sep_pt:.1f} pt vs glyph 7 pt -> {"OK" if d_sep_pt > 7 else "TIGHT"}')
d_ext = (20.0 * math.sin(math.radians(38)) + 2.5 * math.cos(math.radians(38)))
gap2_mm = (axC.get_position().y0 - (axE.get_position().y0 + axE.get_position().height)) * FIG_H_MM
print(f'  (d) label vertical extent ~{d_ext:.1f} mm vs tier gap {gap2_mm:.1f} mm '
      f'-> {"OK" if d_ext < gap2_mm else "OVERLAP RISK"}')

# (e) legend placed outside the axes -> cannot cover any curve
eb = axE.get_position()
print(f'  (e) axes right edge {(eb.x0+eb.width)*FIG_W_MM:.1f} mm, legend anchored at '
      f'{((eb.x0+eb.width)+0.02*eb.width)*FIG_W_MM:.1f} mm (outside axes)')

# ---- cross-tier clearance: upper tick labels vs lower title block ----------
def gap_mm(upper, lower):
    return (upper.get_position().y0
            - (lower.get_position().y0 + lower.get_position().height)) * FIG_H_MM


def xmm(ax):
    p = ax.get_position()
    return p.x0 * FIG_W_MM, (p.x0 + p.width) * FIG_W_MM


a_ext = 18.0 * math.sin(math.radians(42)) + 5.0 * math.cos(math.radians(42))
d_ext = 20.0 * math.sin(math.radians(38)) + 2.5 * math.cos(math.radians(38))
c_lab = 3.2                 # horizontal single-line tick label + pad
title1 = 5.0                # one-line title block (9 pt + pad)
title2 = 10.0               # two-line title block
g12, g23 = gap_mm(axA, axC), gap_mm(axC, axE)
print(f'  tier1->2 gap {g12:.1f} mm vs need {a_ext + title1:.1f} mm '
      f'(a labels {a_ext:.1f} + c title {title1:.1f}) -> {"OK" if g12 > a_ext + title1 else "OVERLAP RISK"}')
print(f'  tier2->3 gap {g23:.1f} mm vs need {c_lab + title2:.1f} mm '
      f'(c label {c_lab:.1f} + e title {title2:.1f}) -> {"OK" if g23 > c_lab + title2 else "OVERLAP RISK"}')
ex0, ex1 = xmm(axE)
dx0, _dx1 = xmm(axD)
print(f'  (e) x {ex0:.1f}-{ex1:.1f} mm vs (d) x {dx0:.1f}-{_dx1:.1f} mm -> '
      f'{"column-disjoint (d labels cannot reach e)" if ex1 < dx0 else "X-OVERLAP: d labels may hit e title"}')
print(f'  (d) labels hang {d_ext:.1f} mm below tier 2; (e) top at '
      f'{(axE.get_position().y0 + axE.get_position().height) * FIG_H_MM:.1f} mm')

# -------------------------------- self-check --------------------------------
import fitz
doc = fitz.open(OUT_PDF)
pg = doc[0]
print(f'size: {pg.rect.width/72*25.4:.2f} x {pg.rect.height/72*25.4:.2f} mm')
sizes, fonts = {}, set()
for b in pg.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        for s in l['spans']:
            sizes[round(s['size'], 1)] = sizes.get(round(s['size'], 1), 0) + 1
            fonts.add(s['font'])
print('span sizes:', dict(sorted(sizes.items())))
print('fonts:', sorted(fonts))
print('sub-7pt spans:', {k: v for k, v in sorted(sizes.items()) if k < 6.95})
print('DONE.')
