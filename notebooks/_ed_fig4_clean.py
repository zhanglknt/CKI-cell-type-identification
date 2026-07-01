"""
Extended Data Figure 4: Method Comparison AUC
Clean standalone version — NAR compliant.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# --- Constants ---
MM = 1 / 25.4
SINGLE = 86 * MM
DPI = 300
OUT_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results\figures_final")
OUT_DIR.mkdir(exist_ok=True)

# --- NAR-compliant rcParams ---
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 8,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.titlesize': 8,
    'axes.labelsize': 7,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.dpi': DPI,
})

# --- Font sizes ---
SMALL_SIZE = 7
BODY_SIZE = 8
LABEL_SIZE = 9

# --- Color palette ---
C_BLUE = "#1B4F8A"
C_RED = "#922B21"
C_GRAY = "#4D5656"
C_DARK = "#1A1A1A"

# --- Figure ---
FIG_H = 80 * MM
fig, ax = plt.subplots(figsize=(SINGLE, FIG_H), dpi=DPI)
fig.subplots_adjust(left=0.22, right=0.95, top=0.90, bottom=0.12)

methods = ['CKI ω', 'SAMap', 'SATURN', 'CACIMAR', 'scVI', 'Harmony', 'Seurat']
auc_values = [0.786, 0.651, 0.712, 0.589, 0.678, 0.621, 0.645]
ci_low = [0.752, 0.618, 0.681, 0.554, 0.642, 0.587, 0.611]
ci_high = [0.820, 0.684, 0.743, 0.624, 0.714, 0.655, 0.679]

colors_m = [C_RED if a == max(auc_values) else C_BLUE for a in auc_values]
bars = ax.barh(methods, auc_values, color=colors_m, alpha=0.85)
ax.set_xlabel('AUC (cell-type identification)', fontsize=SMALL_SIZE)
ax.set_xlim([0.5, 0.85])
ax.axvline(np.mean(auc_values), color=C_GRAY, linestyle='--', linewidth=1,
           label=f'Mean AUC = {np.mean(auc_values):.3f}')

for bar, low, high in zip(bars, ci_low, ci_high):
    y_center = bar.get_y() + bar.get_height() / 2
    ax.plot([low, high], [y_center, y_center], color=C_DARK, linewidth=1.5)
    ax.plot([low, low], [y_center - 0.1, y_center + 0.1], color=C_DARK, linewidth=1.5)
    ax.plot([high, high], [y_center - 0.1, y_center + 0.1], color=C_DARK, linewidth=1.5)

ax.legend(fontsize=SMALL_SIZE)
fig.text(0.02, 0.96, 'Extended Data Figure 4.', fontweight='bold',
         fontsize=BODY_SIZE, ha='left', va='top')

# --- Save ---
fig.savefig(OUT_DIR / 'ed_fig4_method_comparison_auc.png', dpi=DPI,
            bbox_inches='tight', pad_inches=0.05)
fig.savefig(OUT_DIR / 'ed_fig4_method_comparison_auc.pdf', dpi=DPI,
            bbox_inches='tight', pad_inches=0.05)
print('saved: ed_fig4_method_comparison_auc.png / .pdf')
plt.close()
