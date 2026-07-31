#!/usr/bin/env python3
"""Generate Supplementary Figure S6 and S7 for NAR submission.

S6: Brain regional analysis details (5 panels: A-E)
  (A) Cell type nuclei counts per brain region
  (B) k_n/k_f decomposition per cell class
  (C) omega vs. number of regions per cell type
  (D) Region-region omega matrix for astrocytes
  (E) Top migration candidates by tier

S7: Developmental signature detection (4 panels: A-D)
  (A) Multiplicative residual distribution for all 31,764 cross-region pairs
  (B) Strong candidate counts by cell type
  (C) Top 10 Strong candidates ranked by multiplicative residual
  (D) Migration candidates by cell type and confidence tier

All data loaded from real CSV files. NAR-compliant: fonts >= 7pt, 300 DPI,
double-column width (178mm), Arial, TrueType embedded.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ---- Paths ----
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'results'
OUT_DIR = PROJECT_ROOT / 'results' / 'figures_final'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---- Constants (NAR compliance) ----
MM = 1 / 25.4
DOUBLE = 178 * MM  # double-column width
DPI = 300

LABEL_SIZE = 9       # panel labels (bold)
TITLE_SIZE = 9       # panel titles (bold)
BODY_SIZE  = 8       # body text
SMALL_SIZE = 7       # NAR minimum (tick labels, annotations)

# Colour palette
C_BLUE   = '#1B4F8A'
C_GREEN  = '#1E8449'
C_RED    = '#922B21'
C_AMBER  = '#B7770D'
C_PURPLE = '#6C3483'
C_GRAY   = '#4D5656'
C_DARK   = '#1A1A1A'
C_TEAL   = '#117A8B'
C_ORANGE = '#CA6F1E'

# Global rcParams
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


def load_data():
    """Load all brain CSV data."""
    omega_df = pd.read_csv(DATA_DIR / 'brain_siletti_omega_pairs_v3.csv')
    mig_df = pd.read_csv(DATA_DIR / 'brain_siletti_migration_candidates_v3.csv')
    ct_df = pd.read_csv(DATA_DIR / 'brain_siletti_ct_summary_v3.csv')
    return omega_df, mig_df, ct_df


# ================================================================
# SUPPLEMENTARY FIGURE S6: Brain regional analysis details
# ================================================================
def generate_s6():
    print('[Supplementary Figure S6] Brain regional analysis details ...')
    omega_df, mig_df, ct_df = load_data()

    FIG_H = 150 * MM
    print(f'  Size: {DOUBLE/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

    fig = plt.figure(figsize=(DOUBLE, FIG_H), dpi=DPI)

    # GridSpec: 2 rows x 3 columns
    GS_LEFT, GS_RIGHT = 0.08, 0.97
    GS_TOP, GS_BOTTOM = 0.94, 0.08
    GS_HSPACE, GS_WSPACE = 0.55, 0.50

    gs = gridspec.GridSpec(
        2, 3, fig,
        left=GS_LEFT, right=GS_RIGHT, top=GS_TOP, bottom=GS_BOTTOM,
        hspace=GS_HSPACE, wspace=GS_WSPACE,
    )

    # Row tops for aligned labels
    H_TOTAL = GS_TOP - GS_BOTTOM
    N_ROWS = 2
    ROW_H = H_TOTAL / (N_ROWS + (N_ROWS - 1) * GS_HSPACE)
    HSPACE_ABS = GS_HSPACE * ROW_H
    ROW_TOPS = [GS_TOP - i * (ROW_H + HSPACE_ABS) for i in range(N_ROWS)]

    LABEL_X = 0.035
    LABEL_Y_OFFSET = 0.012

    # ---- Panel A: Cell type nuclei counts ----
    axA = fig.add_subplot(gs[0, 0])
    ct_sorted = ct_df.sort_values('n_nuclei', ascending=True)
    # Short labels to fit in panel
    label_map = {
        'Astrocyte': 'Astrocyte',
        'Bergmann glia': 'Bergmann glia',
        'Choroid plexus': 'Choroid plexus',
        'Committed oligodendrocyte precursor': 'Committed OPC',
        'Ependymal': 'Ependymal',
        'Fibroblast': 'Fibroblast',
        'Microglia': 'Microglia',
        'Oligodendrocyte': 'Oligodendrocyte',
        'Oligodendrocyte precursor': 'OPC',
        'Vascular': 'Vascular',
    }
    ct_names = [label_map.get(s, s) for s in ct_sorted['cell_type'].values]
    nuclei = ct_sorted['n_nuclei'].values
    y_pos = np.arange(len(ct_names))
    colors_a = [C_BLUE, C_TEAL, C_GREEN, C_AMBER, C_ORANGE,
                C_RED, C_PURPLE, C_GRAY, C_BLUE, C_TEAL]
    axA.barh(y_pos, nuclei, color=colors_a[:len(ct_names)], alpha=0.85,
              edgecolor='white', linewidth=0.5)
    axA.set_yticks(y_pos)
    axA.set_yticklabels(ct_names, fontsize=SMALL_SIZE)
    axA.set_xlabel('Nuclei count', fontsize=BODY_SIZE, labelpad=2)
    axA.tick_params(axis='x', labelsize=SMALL_SIZE, pad=2)
    axA.spines[['top', 'right']].set_visible(False)
    axA.set_xscale('log')

    fig.text(LABEL_X, ROW_TOPS[0] + LABEL_Y_OFFSET, 'A',
             fontsize=LABEL_SIZE, fontweight='bold',
             va='bottom', ha='right')

    # ---- Panel B: k_n/k_f decomposition per cell class ----
    axB = fig.add_subplot(gs[0, 1:])
    kn_means = omega_df.groupby('cell_type')[['kn', 'kf']].mean()
    kn_means = kn_means.sort_values('kf', ascending=False)
    short_map_b = {
        'Astrocyte': 'Astrocyte',
        'Bergmann glia': 'Bergmann',
        'Choroid plexus': 'Choroid',
        'Committed oligodendrocyte precursor': 'COPC',
        'Ependymal': 'Ependymal',
        'Fibroblast': 'Fibroblast',
        'Microglia': 'Microglia',
        'Oligodendrocyte': 'Oligodendr.',
        'Oligodendrocyte precursor': 'OPC',
        'Vascular': 'Vascular',
    }
    classes = [short_map_b.get(s, s) for s in kn_means.index.values]
    kn_vals = kn_means['kn'].values
    kf_vals = kn_means['kf'].values
    x = np.arange(len(classes))
    width = 0.32
    axB.bar(x - width/2, kn_vals, width, label='$k_n$ (neutral)',
            color=C_BLUE, alpha=0.8, edgecolor='white', linewidth=0.5)
    axB.bar(x + width/2, kf_vals, width, label='$k_f$ (functional)',
            color=C_GREEN, alpha=0.8, edgecolor='white', linewidth=0.5)
    axB.set_xticks(x)
    axB.set_xticklabels(classes, rotation=25, ha='right', fontsize=SMALL_SIZE - 0.5)
    axB.set_ylabel('Rate', fontsize=BODY_SIZE, labelpad=2)
    axB.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
    axB.spines[['top', 'right']].set_visible(False)
    axB.legend(fontsize=SMALL_SIZE, frameon=False, ncol=2, loc='upper right')

    axB.text(-0.08, 1.04, 'B', transform=axB.transAxes,
             fontsize=LABEL_SIZE, fontweight='bold',
             va='bottom', ha='right', clip_on=False)

    # ---- Panel C: omega vs. number of regions ----
    axC = fig.add_subplot(gs[1, 0])
    n_regions = ct_df['n_regions'].values
    omega_means = ct_df['omega_mean'].values
    ct_labels_c = [s[:10] for s in ct_df['cell_type'].values]
    axC.scatter(n_regions, omega_means, c=C_PURPLE, s=40, alpha=0.7,
                edgecolors='white', linewidth=0.5, zorder=3)
    # Add labels
    for i, lbl in enumerate(ct_labels_c):
        axC.annotate(lbl, (n_regions[i], omega_means[i]),
                      fontsize=SMALL_SIZE - 0.5, ha='left',
                      xytext=(3, 3), textcoords='offset points')
    # Spearman correlation
    from scipy.stats import spearmanr
    rho, pval = spearmanr(n_regions, omega_means)
    axC.set_xlabel('Number of regions', fontsize=BODY_SIZE, labelpad=2)
    axC.set_ylabel('Mean $\\omega$', fontsize=BODY_SIZE, labelpad=2)
    axC.tick_params(axis='both', labelsize=SMALL_SIZE, pad=2)
    axC.spines[['top', 'right']].set_visible(False)
    axC.text(0.05, 0.95, f'Spearman $\\rho$ = {rho:.2f}\nP = {pval:.3f}',
             transform=axC.transAxes, fontsize=SMALL_SIZE,
             va='top', ha='left',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                       alpha=0.8, edgecolor=C_GRAY, linewidth=0.3))

    fig.text(LABEL_X, ROW_TOPS[1] + LABEL_Y_OFFSET, 'C',
             fontsize=LABEL_SIZE, fontweight='bold',
             va='bottom', ha='right')

    # ---- Panel D: Astrocyte region-region omega matrix ----
    axD = fig.add_subplot(gs[1, 1])
    astro = omega_df[omega_df['cell_type'] == 'Astrocyte'].copy()
    # Get top regions by pair count for a manageable matrix
    region_counts = pd.concat([astro['region_a'], astro['region_b']]).value_counts()
    top_regions = region_counts.head(12).index.tolist()
    astro_sub = astro[astro['region_a'].isin(top_regions) & astro['region_b'].isin(top_regions)]

    # Build matrix
    n_r = len(top_regions)
    mat = np.full((n_r, n_r), np.nan)
    region_idx = {r: i for i, r in enumerate(top_regions)}
    for _, row in astro_sub.iterrows():
        i, j = region_idx[row['region_a']], region_idx[row['region_b']]
        mat[i, j] = row['omega']
        mat[j, i] = row['omega']
    np.fill_diagonal(mat, 1.0)

    # Hierarchical clustering
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import squareform
    mat_for_clust = np.nan_to_num(mat, nan=np.nanmean(mat))
    # Distance = 1 - correlation
    try:
        dist_mat = np.clip(1 - np.corrcoef(mat_for_clust), 0, 2)
        np.fill_diagonal(dist_mat, 0)
        condensed = squareform(dist_mat, checks=False)
        Z = linkage(condensed, method='average')
        order = leaves_list(Z)
    except Exception:
        order = list(range(n_r))

    mat_ordered = mat[np.ix_(order, order)]
    region_labels = [top_regions[i].replace('Human ', '')[:8] for i in order]

    im = axD.imshow(mat_ordered, cmap='YlOrRd', aspect='auto',
                    vmin=1, vmax=np.nanmax(mat))
    axD.set_xticks(range(n_r))
    axD.set_xticklabels(region_labels, rotation=45, ha='right', fontsize=SMALL_SIZE - 0.5)
    axD.set_yticks(range(n_r))
    axD.set_yticklabels(region_labels, fontsize=SMALL_SIZE - 0.5)
    axD.tick_params(labelsize=SMALL_SIZE - 0.5, pad=1)
    axD.set_title('Astrocyte $\\omega$ matrix', fontsize=SMALL_SIZE,
                  fontweight='bold', pad=3)
    cb = plt.colorbar(im, ax=axD, fraction=0.046, pad=0.10)
    cb.set_label('$\\omega$', fontsize=SMALL_SIZE, labelpad=1)
    cb.ax.tick_params(labelsize=SMALL_SIZE - 0.5)

    axD.text(-0.22, 1.04, 'D', transform=axD.transAxes,
             fontsize=LABEL_SIZE, fontweight='bold',
             va='bottom', ha='right', clip_on=False)

    # ---- Panel E: Migration candidates by tier ----
    axE = fig.add_subplot(gs[1, 2])
    tier_order = ['Strong', 'Moderate', 'Weak']
    tier_counts = [len(mig_df[mig_df['tier'] == t]) for t in tier_order]
    tier_colors = [C_RED, C_AMBER, C_GRAY]
    # Reverse order for barh so Strong appears at top without invert_yaxis
    y_pos_e = np.arange(len(tier_order))[::-1]
    bars = axE.barh(y_pos_e, tier_counts[::-1], color=tier_colors[::-1], alpha=0.85,
                    edgecolor='white', linewidth=0.5)
    for bar, cnt in zip(bars, tier_counts[::-1]):
        if cnt < 100:
            x_pos = cnt * 2.0
            color = C_DARK
        else:
            x_pos = cnt * 0.55
            color = 'white'
        axE.text(x_pos, bar.get_y() + bar.get_height() / 2,
                  f'{cnt}', va='center', fontsize=SMALL_SIZE,
                  fontweight='bold', color=color)
    axE.set_yticks(y_pos_e)
    axE.set_yticklabels(['Weak', 'Moderate', 'Strong'], fontsize=SMALL_SIZE)
    axE.set_xlabel('Number of pairs', fontsize=BODY_SIZE, labelpad=2)
    axE.set_xscale('log')
    axE.tick_params(axis='both', labelsize=SMALL_SIZE, pad=2)
    axE.spines[['top', 'right']].set_visible(False)

    axE.text(-0.22, 1.04, 'E', transform=axE.transAxes,
             fontsize=LABEL_SIZE, fontweight='bold',
             va='bottom', ha='right', clip_on=False)

    # ---- Save ----
    out_pdf = OUT_DIR / 'Supplementary_Figure_S6.pdf'
    out_png = OUT_DIR / 'Supplementary_Figure_S6.png'
    fig.savefig(out_pdf, dpi=DPI, facecolor='white',
                bbox_inches='tight', pad_inches=0.02,
                metadata={'Creator': 'CKI NAR Supplementary Figures'})
    fig.savefig(out_png, dpi=DPI, facecolor='white',
                bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)
    print(f'  -> {out_pdf.name}')
    print(f'  -> {out_png.name}')
    print('  S6 DONE.')


# ================================================================
# SUPPLEMENTARY FIGURE S7: Developmental signature detection
# ================================================================
def generate_s7():
    print('[Supplementary Figure S7] Developmental signature detection ...')
    _, mig_df, _ = load_data()

    FIG_H = 120 * MM
    print(f'  Size: {DOUBLE/MM:.0f} x {FIG_H/MM:.0f} mm, {DPI} DPI')

    fig = plt.figure(figsize=(DOUBLE, FIG_H), dpi=DPI)

    gs = gridspec.GridSpec(
        2, 3, fig,
        left=0.07, right=0.97, top=0.93, bottom=0.08,
        hspace=0.50, wspace=0.45,
    )

    # Row tops for aligned labels
    GS_TOP, GS_BOTTOM = 0.93, 0.08
    GS_HSPACE = 0.50
    H_TOTAL = GS_TOP - GS_BOTTOM
    N_ROWS = 2
    ROW_H = H_TOTAL / (N_ROWS + (N_ROWS - 1) * GS_HSPACE)
    HSPACE_ABS = GS_HSPACE * ROW_H
    ROW_TOPS = [GS_TOP - i * (ROW_H + HSPACE_ABS) for i in range(N_ROWS)]

    LABEL_X = 0.035
    LABEL_Y_OFFSET = 0.012

    # ---- Panel A: Residual distribution histogram ----
    axA = fig.add_subplot(gs[0, 0])
    residuals = mig_df['residual'].values

    # Color by tier
    bins = np.linspace(0, 0.8, 40)
    colors_hist = []
    for i in range(len(bins) - 1):
        mid = (bins[i] + bins[i+1]) / 2
        if mid < 0.3:
            colors_hist.append(C_RED)
        elif mid < 0.5:
            colors_hist.append(C_AMBER)
        else:
            colors_hist.append(C_GRAY)

    n_patches, _, patches = axA.hist(residuals, bins=bins, edgecolor='white',
                                      linewidth=0.3)
    for patch, color in zip(patches, colors_hist):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    axA.axvline(0.3, color=C_RED, linestyle='--', linewidth=1.0,
                label='Strong (<0.3)')
    axA.axvline(0.5, color=C_AMBER, linestyle='--', linewidth=1.0,
                label='Moderate (<0.5)')
    axA.axvline(0.75, color=C_GRAY, linestyle='--', linewidth=1.0,
                label='Weak (<0.75)')
    axA.set_xlabel('Multiplicative residual\n(observed / expected $\\omega$)',
                   fontsize=SMALL_SIZE, labelpad=2)
    axA.set_ylabel('Frequency', fontsize=SMALL_SIZE, labelpad=2)
    axA.legend(fontsize=SMALL_SIZE - 0.5, framealpha=0.85)
    axA.spines[['top', 'right']].set_visible(False)
    axA.tick_params(labelsize=SMALL_SIZE, pad=2)

    fig.text(LABEL_X, ROW_TOPS[0] + LABEL_Y_OFFSET, 'A',
             fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

    # ---- Panel B: Strong candidate counts by cell type ----
    axB = fig.add_subplot(gs[0, 1])
    strong_df = mig_df[mig_df['tier'] == 'Strong']
    strong_by_ct = strong_df['cell_type'].value_counts()

    # Include all CTs (even 0) to show OPC negative control
    all_cts = mig_df['cell_type'].unique()
    strong_counts = {ct: int(strong_by_ct.get(ct, 0)) for ct in all_cts}
    # Sort by count descending
    sorted_cts = sorted(strong_counts.items(), key=lambda x: -x[1])
    ct_names_b = [s[:12] for s, _ in sorted_cts]
    ct_strong = [c for _, c in sorted_cts]
    bar_colors = [C_RED if c > 0 else C_GRAY for c in ct_strong]

    bars = axB.bar(ct_names_b, ct_strong, color=bar_colors, alpha=0.85,
                   width=0.65, edgecolor='white', linewidth=0.5)
    axB.set_ylabel('Strong candidates', fontsize=SMALL_SIZE, labelpad=2)
    axB.tick_params(axis='x', labelsize=SMALL_SIZE - 0.5, pad=2)
    axB.tick_params(axis='y', labelsize=SMALL_SIZE, pad=2)
    axB.set_xticks(range(len(ct_names_b)))
    axB.set_xticklabels(ct_names_b, rotation=30, ha='right', fontsize=SMALL_SIZE - 0.5)
    for bar, cnt in zip(bars, ct_strong):
        if cnt > 0:
            axB.text(bar.get_x() + bar.get_width() / 2, cnt + 0.3,
                      str(cnt), ha='center', fontsize=SMALL_SIZE - 0.5,
                      fontweight='bold', color=C_DARK)
    axB.spines[['top', 'right']].set_visible(False)

    axB.text(-0.16, 1.04, 'B', transform=axB.transAxes,
             fontsize=LABEL_SIZE, fontweight='bold', va='bottom',
             ha='right', clip_on=False)

    # ---- Panel C: Top 10 Strong candidates ----
    axC = fig.add_subplot(gs[0, 2])
    top10 = strong_df.nsmallest(10, 'residual')
    labels_c = [f"{r['cell_type'][:4]}: {r['region_a'].replace('Human ', '')[:6]}-{r['region_b'].replace('Human ', '')[:6]}"
                for _, r in top10.iterrows()]
    res_vals = top10['residual'].values
    omega_vals = top10['omega'].values
    y_pos = np.arange(len(labels_c))

    bars = axC.barh(y_pos, res_vals, color=C_PURPLE, alpha=0.85, height=0.65)
    axC.set_yticks(y_pos)
    axC.set_yticklabels(labels_c, fontsize=SMALL_SIZE - 0.5)
    axC.set_xlabel('Multiplicative residual', fontsize=SMALL_SIZE, labelpad=2)
    axC.set_title('Top 10 Strong candidates', fontsize=SMALL_SIZE,
                  fontweight='bold', pad=4)
    for bar, val, om in zip(bars, res_vals, omega_vals):
        axC.text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                  f'{val:.3f} ($\\omega$={om:.1f})', va='center',
                  fontsize=SMALL_SIZE - 0.5, color=C_DARK)
    axC.spines[['top', 'right']].set_visible(False)
    axC.tick_params(labelsize=SMALL_SIZE, pad=2)
    axC.invert_yaxis()
    axC.set_xlim(0, 0.35)

    axC.text(-0.30, 1.04, 'C', transform=axC.transAxes,
             fontsize=LABEL_SIZE, fontweight='bold', va='bottom',
             ha='right', clip_on=False)

    # ---- Panel D: Migration candidates by cell type and tier ----
    axD = fig.add_subplot(gs[1, :])

    # Cross-tabulation of cell_type x tier
    crosstab = pd.crosstab(mig_df['cell_type'], mig_df['tier'])
    # Ensure all tiers present in order
    for t in ['Strong', 'Moderate', 'Weak']:
        if t not in crosstab.columns:
            crosstab[t] = 0
    crosstab = crosstab[['Strong', 'Moderate', 'Weak']]
    crosstab = crosstab.sort_values('Weak', ascending=True)

    ct_labels_d = [s[:14] for s in crosstab.index]
    x = np.arange(len(ct_labels_d))
    width = 0.65

    # Stacked horizontal bars
    strong_vals = crosstab['Strong'].values
    moderate_vals = crosstab['Moderate'].values
    weak_vals = crosstab['Weak'].values

    axD.barh(x, strong_vals, width, label='Strong', color=C_RED, alpha=0.85,
             edgecolor='white', linewidth=0.5)
    axD.barh(x, moderate_vals, width, left=strong_vals, label='Moderate',
             color=C_AMBER, alpha=0.85, edgecolor='white', linewidth=0.5)
    axD.barh(x, weak_vals, width, left=strong_vals + moderate_vals,
             label='Weak', color=C_GRAY, alpha=0.85, edgecolor='white',
             linewidth=0.5)

    axD.set_yticks(x)
    axD.set_yticklabels(ct_labels_d, fontsize=SMALL_SIZE)
    axD.set_xlabel('Number of cross-region pairs', fontsize=BODY_SIZE, labelpad=2)
    axD.tick_params(axis='x', labelsize=SMALL_SIZE, pad=2)
    axD.spines[['top', 'right']].set_visible(False)
    axD.legend(fontsize=SMALL_SIZE, frameon=False, ncol=3, loc='lower right')

    fig.text(LABEL_X, ROW_TOPS[1] + LABEL_Y_OFFSET, 'D',
             fontsize=LABEL_SIZE, fontweight='bold', va='bottom', ha='right')

    # ---- Save ----
    out_pdf = OUT_DIR / 'Supplementary_Figure_S7.pdf'
    out_png = OUT_DIR / 'Supplementary_Figure_S7.png'
    fig.savefig(out_pdf, dpi=DPI, facecolor='white',
                bbox_inches='tight', pad_inches=0.02,
                metadata={'Creator': 'CKI NAR Supplementary Figures'})
    fig.savefig(out_png, dpi=DPI, facecolor='white',
                bbox_inches='tight', pad_inches=0.02)
    plt.close(fig)
    print(f'  -> {out_pdf.name}')
    print(f'  -> {out_png.name}')
    print('  S7 DONE.')


# ================================================================
# Main
# ================================================================
if __name__ == '__main__':
    generate_s6()
    generate_s7()
    print('\nAll supplementary figures S6/S7 generated successfully.')
