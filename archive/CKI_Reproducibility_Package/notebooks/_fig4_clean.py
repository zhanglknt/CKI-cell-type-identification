"""Figure 4: TCGA Pan-Cancer — Clean layout for NAR submission.

Layout: 3x2 GridSpec (A/B top, C/D middle, E bottom-left, aligned with A/C)
All fonts >= 7pt, panel labels 9pt bold, no tight_layout().

v38 fix: Panels A/B/D now read from the authoritative phase34_v2 pairs CSVs.
Panel C reads the authoritative PAM50 subtype mean omega values from
results/phase34_clinical_severity.csv (stratification == 'PAM50'), i.e. the
persisted output of the per-tumor TT-mean computation in 07_phase34_clinical.py
(per-sample PAM50 labels from results/phase34_pam50_cache.json). Panel E reads
a pre-computed cross-cancer matrix from results/figures_final/_v38_fig4e_tcga_matrix.npz
if available; if not, it is left blank and a warning is printed.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import _fig_style as st
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd

# ---- Layout constants ----
DPI = st.DPI
MM = st.MM
FIG_W = st.DOUBLE   # 178 mm NAR double column

# ---- Font sizes (via shared style) ----
LABEL_SIZE = st.LABEL_SIZE   # panel labels 9pt bold
SMALL_SIZE = st.SMALL_SIZE   # >= 7pt floor
MID_SIZE   = st.BODY_SIZE    # axis labels

# ---- Colors (shared palette) ----
C_BLUE   = st.C_BLUE
C_GREEN  = st.C_GREEN
C_RED    = st.C_RED
C_ORANGE = st.C_ORANGE
C_AMBER  = st.C_AMBER
C_PURPLE = st.C_PURPLE
C_DARK   = st.C_DARK

# Sequential blue ramp for the heatmap (shared palette)
CMAP_BLUE = LinearSegmentedColormap.from_list('cki_blue', st.RAMP_BLUE)

# ---- Output directory ----
OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'results', 'figures_final')
os.makedirs(OUTDIR, exist_ok=True)
RESDIR = os.path.join(os.path.dirname(__file__), '..', 'results')


def savefig(name, w, h):
    """Save both PDF and PNG."""
    for ext in ['.pdf', '.png']:
        path = os.path.join(OUTDIR, name + ext)
        plt.savefig(path, dpi=DPI if ext == '.png' else None,
                    bbox_inches='tight', pad_inches=0.02)
    print(f'  -> {name}.pdf + .png')


# ================================================================
# Figure 4: TCGA Pan-Cancer
# ================================================================
print('[Figure 4] TCGA Pan-Cancer ...')
FIG_H = 165 * MM
print(f'Figure 4: {FIG_W/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

fig = plt.figure(figsize=(FIG_W, FIG_H), dpi=DPI)
gs = gridspec.GridSpec(
    3, 2, fig,
    height_ratios=[1.0, 1.0, 1.1],
    left=0.09, right=0.97, top=0.93, bottom=0.06,
    hspace=0.52, wspace=0.28,
)

cancers = ['BRCA', 'KIRC', 'LIHC', 'LUAD', 'LUSC']
colors_cancer = [C_BLUE, C_GREEN, C_AMBER, C_RED, C_PURPLE]

# Load authoritative pair data once
pair_med = {}
pair_nn = {}
pair_tt = {}
for c in cancers:
    df = pd.read_csv(os.path.join(RESDIR, f'phase34_v2_TCGA-{c}_pairs.csv'))
    med = df.groupby('pair_type')['omega'].median()
    pair_med[c] = med
    pair_nn[c] = df[df['pair_type'] == 'NN']['omega'].values
    pair_tt[c] = df[df['pair_type'] == 'TT']['omega'].values

nn_tt = [pair_med[c]['NN'] / pair_med[c]['TT'] for c in cancers]

# ----------------------------------------------------------------
# PANEL A: NN/TT ratio per cancer
# ----------------------------------------------------------------
axA = fig.add_subplot(gs[0, 0])
bars = axA.bar(cancers, nn_tt, color=colors_cancer, alpha=0.9,
               edgecolor=C_DARK, linewidth=0.5, zorder=3)
axA.axhline(1.0, color=st.C_GRAY, linestyle='--', linewidth=0.9,
            label='Neutral (1.0)', zorder=2)
axA.set_ylabel('NN/TT \u03c9 ratio', fontsize=MID_SIZE, labelpad=2)
axA.set_title('Tumor vs. normal CKI \u03c9', fontsize=SMALL_SIZE,
              fontweight='bold', pad=4)
axA.legend(fontsize=SMALL_SIZE, loc='upper left', frameon=False,
           handlelength=1.6, borderpad=0.2)
for bar, val in zip(bars, nn_tt):
    axA.text(bar.get_x() + bar.get_width()/2, val + 0.05,
             f'{val:.2f}\u00d7', ha='center', fontsize=SMALL_SIZE,
             fontweight='bold', color=C_DARK)
axA.set_ylim(0, 2.6)
axA.tick_params(labelsize=SMALL_SIZE)
st.subtle_grid(axA)
st.despine(axA)
st.add_panel_label(fig, axA, 'A', x=-0.14, y=1.03)

# ----------------------------------------------------------------
# PANEL B: Boxplot of NN vs TT omega per cancer
# ----------------------------------------------------------------
axB = fig.add_subplot(gs[0, 1])
# Build paired data: NN then TT for each cancer, alternating positions
positions = []
box_data = []
box_colors = []
for i, c in enumerate(cancers):
    positions.extend([i * 2.5 + 1, i * 2.5 + 2])
    box_data.extend([pair_nn[c], pair_tt[c]])
    box_colors.extend([colors_cancer[i], colors_cancer[i]])

bp = axB.boxplot(box_data, positions=positions, patch_artist=True,
                 showfliers=False, widths=0.7,
                 medianprops=dict(color=C_DARK, linewidth=1.1),
                 whiskerprops=dict(color=st.C_STEEL, linewidth=0.8),
                 capprops=dict(color=st.C_STEEL, linewidth=0.8))
for patch, c in zip(bp['boxes'], box_colors):
    patch.set_facecolor(c)
    patch.set_alpha(0.55)
    patch.set_edgecolor(C_DARK)
    patch.set_linewidth(0.6)

# Group labels
for i, c in enumerate(cancers):
    axB.text(i * 2.5 + 1.5, axB.get_ylim()[0] if axB.get_ylim()[0] else 0,
             c, ha='center', fontsize=SMALL_SIZE)
axB.set_xticks([])
axB.set_ylabel('CKI \u03c9 (tumor vs. normal)', fontsize=MID_SIZE, labelpad=2)
axB.tick_params(labelsize=SMALL_SIZE)
# Manual legend
from matplotlib.patches import Patch
axB.legend([Patch(facecolor=colors_cancer[0], alpha=0.55, edgecolor=C_DARK),
            Patch(facecolor=colors_cancer[0], alpha=0.25, edgecolor=C_DARK)],
           ['NN', 'TT'], fontsize=SMALL_SIZE, frameon=False, loc='upper right')
st.subtle_grid(axB)
st.despine(axB)
st.add_panel_label(fig, axB, 'B', x=-0.14, y=1.03)

# ----------------------------------------------------------------
# PANEL C: PAM50 subtype in BRCA (authoritative values from
# phase34_clinical_severity.csv, computed in 07_phase34_clinical.py from
# per-sample PAM50 labels + per-tumor TT-mean omega)
# ----------------------------------------------------------------
axC = fig.add_subplot(gs[1, 0])
sev = pd.read_csv(os.path.join(RESDIR, 'phase34_clinical_severity.csv'))
pam = sev[(sev['cancer'] == 'BRCA') & (sev['stratification'] == 'PAM50')]
PAM_ORDER = ['Luminal A', 'Luminal B', 'HER2-enriched', 'Basal-like', 'Normal-like']
PAM_SHORT = {'Luminal A': 'LumA', 'Luminal B': 'LumB', 'HER2-enriched': 'HER2',
             'Basal-like': 'Basal', 'Normal-like': 'Normal-like'}
pam = pam.set_index('group')
pam = pam.loc[[g for g in PAM_ORDER if g in pam.index]]
pam50 = [PAM_SHORT[g] for g in pam.index]
pam50_omega = pam['omega_mean'].astype(float).tolist()
print('  PAM50 subtype mean omega (from phase34_clinical_severity.csv):')
for lbl, val, n in zip(pam50, pam50_omega, pam['n']):
    print(f'    {lbl}: n={n}, mean={val:.1f}')
pam50_colors = [C_AMBER, C_GREEN, C_ORANGE, C_RED, C_BLUE][:len(pam50)]
bars = axC.bar(pam50, pam50_omega, color=pam50_colors, alpha=0.9,
               edgecolor=C_DARK, linewidth=0.5, zorder=3)
axC.set_ylabel('CKI \u03c9 (BRCA PAM50)', fontsize=MID_SIZE, labelpad=2)
axC.set_title('BRCA subtypes', fontsize=SMALL_SIZE, fontweight='bold', pad=4)
axC.tick_params(axis='x', rotation=25, labelsize=SMALL_SIZE)
axC.tick_params(axis='y', labelsize=SMALL_SIZE)
for bar, val in zip(bars, pam50_omega):
    axC.text(bar.get_x() + bar.get_width()/2, val + 2.5,
             f'{val:.1f}', ha='center', fontsize=SMALL_SIZE,
             fontweight='bold', color=C_DARK)
axC.set_ylim(0, max(pam50_omega) * 1.18)
st.subtle_grid(axC)
st.despine(axC)
st.add_panel_label(fig, axC, 'C', x=-0.14, y=1.03)

# ----------------------------------------------------------------
# PANEL D: Effect size per cancer (Cohen's d with bootstrap CI)
# ----------------------------------------------------------------
axD = fig.add_subplot(gs[1, 1])
np.random.seed(42)
effect_sizes = []
ci_low = []
ci_high = []
for c in cancers:
    nn = pair_nn[c]
    tt = pair_tt[c]
    pooled_sd = np.sqrt(((len(nn) - 1) * np.var(nn, ddof=1) +
                         (len(tt) - 1) * np.var(tt, ddof=1)) /
                        (len(nn) + len(tt) - 2))
    d = (nn.mean() - tt.mean()) / pooled_sd
    ds = []
    for _ in range(1000):
        nnb = np.random.choice(nn, size=len(nn), replace=True)
        ttb = np.random.choice(tt, size=len(tt), replace=True)
        psd = np.sqrt(((len(nnb) - 1) * np.var(nnb, ddof=1) +
                       (len(ttb) - 1) * np.var(ttb, ddof=1)) /
                      (len(nnb) + len(ttb) - 2))
        ds.append((nnb.mean() - ttb.mean()) / psd)
    lo, hi = np.percentile(ds, [2.5, 97.5])
    effect_sizes.append(d)
    ci_low.append(lo)
    ci_high.append(hi)

axD.errorbar(cancers, effect_sizes,
             yerr=[np.array(effect_sizes) - np.array(ci_low),
                   np.array(ci_high) - np.array(effect_sizes)],
             fmt='o', capsize=3, capthick=0.9, color=C_BLUE, ecolor=C_BLUE,
             elinewidth=0.9, markersize=5.5,
             markerfacecolor=C_BLUE, markeredgecolor='white',
             markeredgewidth=0.7, zorder=3)
axD.set_ylabel("Cohen's d (tumor vs. normal)", fontsize=MID_SIZE, labelpad=2)
axD.tick_params(labelsize=SMALL_SIZE)
axD.set_ylim(0.3, 1.4)
st.subtle_grid(axD)
st.despine(axD)
st.add_panel_label(fig, axD, 'D', x=-0.14, y=1.03)

# ----------------------------------------------------------------
# PANEL E: omega matrix heatmap (TCGA cross-cancer)
# ----------------------------------------------------------------
axE = fig.add_subplot(gs[2, :])
mat_path = os.path.join(OUTDIR, 'fig4e_tcga_cross_cancer_matrix.npz')
if os.path.exists(mat_path):
    mat_npz = np.load(mat_path, allow_pickle=True)
    omega_mat = mat_npz['omega']
    print(f'  loaded cross-cancer matrix from {mat_path}')
else:
    print(f'  WARNING: {mat_path} not found; Panel E left blank')
    omega_mat = np.full((5, 5), np.nan)

im = axE.imshow(omega_mat, cmap=CMAP_BLUE, aspect='auto')
axE.set_xticks(range(5))
axE.set_xticklabels(cancers, fontsize=SMALL_SIZE)
axE.set_yticks(range(5))
axE.set_yticklabels(cancers, fontsize=SMALL_SIZE)
axE.set_title('TCGA pairwise \u03c9 matrix (5 cancers)', fontsize=MID_SIZE,
              fontweight='bold', pad=4)
# thin white cell frame
axE.set_xticks(np.arange(-0.5, 5, 1), minor=True)
axE.set_yticks(np.arange(-0.5, 5, 1), minor=True)
axE.grid(which='minor', color='white', linewidth=0.7)
axE.tick_params(which='minor', length=0)
for sp in axE.spines.values():
    sp.set_visible(True)
    sp.set_linewidth(0.6)
    sp.set_edgecolor('#3A3A3A')
cbar = plt.colorbar(im, ax=axE, fraction=0.046, pad=0.04)
cbar.set_label('CKI \u03c9', fontsize=SMALL_SIZE)
cbar.ax.tick_params(labelsize=SMALL_SIZE, width=0.6, length=2.5)
cbar.outline.set_linewidth(0.6)
cbar.outline.set_edgecolor('#3A3A3A')
st.add_panel_label(fig, axE, 'E', x=-0.07, y=1.03)

# ---- SAVE ----
savefig('figure4_tcga_pancancer', FIG_W, FIG_H)
print('Done.')
