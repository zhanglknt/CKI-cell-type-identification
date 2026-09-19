#!/usr/bin/env python3
"""v49.7: regenerate Figure 2 bottom row natively (panels D + E).

Panel D: 5-metric correlation heatmap on Tabula Sapiens pairs
         (source: results/figure_data_correlations.npy, unchanged content).
Panel E: ROC for functional-change vs neutral-drift detection in the
         semi-synthetic ground-truth simulation (marrow background),
         6 metrics; skin-background independent replication annotated
         (CKI omega AUC = 0.91, rank 1/6).

Replaces the old bottom row (v47 figure3.pdf with whited-out labels).
Output: results/figures_final/_fig2_bottomrow_nc49.pdf
        178 x 72 mm, Arial >= 7 pt, Type 42, native panel labels D/E.
"""
import sys
sys.path.insert(0, r'C:\Users\KnightZ\.workbuddy\binaries\python\envs\default\Lib\site-packages')
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score

plt.rcParams.update({
    'font.family': 'Arial',
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.linewidth': 0.6,
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.major.size': 2.5,
    'ytick.major.size': 2.5,
})

MM = 1 / 25.4
OUT = 'results/figures_final/_fig2_bottomrow_nc49.pdf'

# ---------------- data ------------------------------------------------------
corr = np.load('results/figure_data_correlations.npy', allow_pickle=True).item()
C = corr['corr_matrix']
M3 = corr['metrics_3a']            # ['CKI ω','Cosine','Raw JS','Marker Jaccard','Spearman']

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

# ---------------- figure ----------------------------------------------------
fig = plt.figure(figsize=(178 * MM, 72 * MM))

# panel labels (native, Arial bold 9 pt)
fig.text(4 * MM / (178 * MM), 0.945, 'D', fontsize=9, fontweight='bold', ha='left', va='top')
fig.text(96 * MM / (178 * MM), 0.945, 'E', fontsize=9, fontweight='bold', ha='left', va='top')

# ---- Panel D: correlation heatmap -----------------------------------------
axd = fig.add_axes([0.085, 0.19, 0.30, 0.62])
im = axd.imshow(C, cmap='RdBu_r', vmin=-1, vmax=1)
axd.set_xticks(range(5)); axd.set_yticks(range(5))
axd.set_xticklabels(M3, fontsize=7, rotation=38, ha='right')
axd.set_yticklabels(M3, fontsize=7)
for i in range(5):
    for j in range(5):
        axd.text(j, i, f'{C[i, j]:.2f}', ha='center', va='center',
                 fontsize=7, color='black' if abs(C[i, j]) < 0.75 else 'white')
axd.set_title('Tabula Sapiens pairs: metric correlation', fontsize=7.5, pad=3)
for s in axd.spines.values():
    s.set_visible(False)
axd.tick_params(length=0)
cbd = fig.add_axes([0.395, 0.19, 0.012, 0.62])
cb = fig.colorbar(im, cax=cbd)
cb.ax.tick_params(labelsize=7, length=2)
cb.set_label("Pearson's r", fontsize=7)
cb.outline.set_linewidth(0.6)

# ---- Panel E: change-detection ROC ----------------------------------------
axe = fig.add_axes([0.565, 0.16, 0.30, 0.60])
colors = {'omega': '#C8102E', 'k_f': '#2166AC', 'k_total': '#1B7837',
          'cosine': '#E08214', 'kf_over_kt': '#762A83', 'k_n': '#636363'}
for m, d in zip(met_keys, met_disp):
    fpr, tpr, _ = roc_curve(y, vals[m])
    lw = 1.8 if m == 'omega' else 1.0
    zo = 10 if m == 'omega' else 5
    axe.plot(fpr, tpr, color=colors[m], lw=lw, zorder=zo,
             label=f'{d} ({aucs[m]:.2f})')
axe.plot([0, 1], [0, 1], ls='--', lw=0.7, color='#999999', zorder=1)
axe.set_xlim(0, 1); axe.set_ylim(0, 1.02)
axe.set_xlabel('False positive rate', fontsize=7.5)
axe.set_ylabel('True positive rate', fontsize=7.5)
axe.tick_params(labelsize=7)
axe.set_title('Functional-change vs neutral-drift detection\n'
              f'replicated on skin background: CKI \u03c9 AUC = {bg2_omega:.2f} (rank 1/6)',
              fontsize=7.5, pad=3)
leg = axe.legend(loc='lower right', fontsize=7, frameon=True, framealpha=0.95,
                 edgecolor='#CCCCCC', borderpad=0.4, labelspacing=0.35,
                 handlelength=1.6, handletextpad=0.6)
leg.set_zorder(20)

fig.savefig(OUT)
print('saved', OUT)

# ---- audit -----------------------------------------------------------------
import fitz
doc = fitz.open(OUT)
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
sub = {k: v for k, v in sorted(sizes.items()) if k < 6.95}
print('sub-7pt spans (mathtext only):', sub)
pix = pg.get_pixmap(dpi=150)
pix.save('results/audit/_fig2_bottomrow_v497.png')
print('preview: results/audit/_fig2_bottomrow_v497.png', pix.width, 'x', pix.height)
