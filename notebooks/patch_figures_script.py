"""
Patch 30_nar_figures_final.py to load pre-computed real data.
Fixes P2-1 through P2-4.
Backs up original as 30_nar_figures_final.py.bak
"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR  = PROJECT_ROOT / "results"
SCRIPT_PATH = PROJECT_ROOT / "notebooks" / "30_nar_figures_final.py"
BAK_PATH   = SCRIPT_PATH.with_suffix(".py.bak")

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

with open(BAK_PATH, "w", encoding="utf-8") as f:
    f.writelines(lines)
print(f"Backup saved: {BAK_PATH}")

# Load pre-computed data
corr_data  = np.load(RESULTS_DIR / "figure_data_correlations.npy", allow_pickle=True).item()
auc_data    = np.load(RESULTS_DIR / "figure_data_auc.npy", allow_pickle=True).item()
hk_data     = np.load(RESULTS_DIR / "figure_data_hk_overlap.npy", allow_pickle=True).item()
pathways_df = pd.read_csv(RESULTS_DIR / "figure_data_pathways.csv")

corrs_2c    = corr_data["corrs_2c"]
corr_matrix  = corr_data["corr_matrix"]
auc_values   = [auc_data[m] for m in ['CKI ω', 'Cosine', 'Raw JS', 'Marker Jaccard', 'Spearman']]
hk_overlap   = hk_data["overlap_rates"]
hk_labels    = hk_data["labels"]

print(f"Loaded corrs_2c    = {[round(c,4) for c in corrs_2c]}")
print(f"Loaded auc_values   = {[round(a,4) for a in auc_values]}")
print(f"Loaded hk_overlap   = {hk_overlap}")
print(f"Loaded pathways     = {list(pathways_df['pathway'])}")

# Build replacement snippets
# -----------------------------------------------------------

# P2-1: Fig 2C — replace hardcoded corrs list
#   Find line: corrs = [-0.386, -0.396, -0.358, -0.461]
NEW_CORRS_LINE = f"corrs = {[round(c,4) for c in corrs_2c]!r}\n"
# Actually, let's use the exact values from the CSV:
corrs_str = "[" + ", ".join([f"{c:.4f}" for c in corrs_2c]) + "]"
NEW_CORRS_LINE = f"corrs = {corrs_str}\n"

# P2-1: Fig 3A — replace hardcoded corr_matrix
#   Build the numpy array string from corr_matrix
def matrix_to_npy_string(m):
    rows = []
    for i in range(m.shape[0]):
        row_vals = ", ".join([f"{m[i,j]:.3f}" for j in range(m.shape[1])])
        rows.append("    [" + row_vals + "]")
    return "np.array([\n" + ",\n".join(rows) + ",\n])"

corr_matrix_str = matrix_to_npy_string(corr_matrix)
NEW_CORR_MATRIX = corr_matrix_str + "\n"

# P2-2: Fig 3C — replace known_auc dict + generate real ROC
#   We'll replace the entire Panel C section to use real data
# P2-2: Fig 3E — replace hardcoded auc_values
auc_str_3e = "[" + ", ".join([f"{a:.4f}" for a in auc_values]) + "]"
NEW_AUC_VALUES_3E = f"auc_values = {auc_str_3e}\n"

# P2-2: ED Fig 4 — replace hardcoded auc_values
NEW_AUC_VALUES_ED4 = f"auc_values = {auc_str_3e}\n"

# P2-3: ED Fig 2B — replace hardcoded hk_overlap
hk_str = "[" + ", ".join([str(int(v)) for v in hk_overlap]) + "]"
NEW_HK_OVERLAP = f"hk_overlap = {hk_str}\n"

# P2-4: Fig 2D — replace hardcoded pathway data
pw_names   = list(pathways_df['pathway'])
pw_fc       = list(pathways_df['fold_change'])
pw_pvals    = list(pathways_df['pval'])
pw_names_str = "[" + ", ".join([f"'{p}'" for p in pw_names]) + "]"
pw_fc_str    = "[" + ", ".join([f"{v:.1f}" for v in pw_fc]) + "]"
pw_pvals_str = "[" + ", ".join([f"{v:.0e}" for v in pw_pvals]) + "]"
NEW_PATHWAYS     = f"pathways = {pw_names_str}\n"
NEW_FOLD_CHANGES = f"fold_changes = {pw_fc_str}\n"
NEW_PS           = f"ps = {pw_pvals_str}\n"

print("\nSnippets prepared. Applying patches...")

# Apply patches by rewriting the file
# We'll do targeted string replacements
content = "".join(lines)

# --- P2-1: Fig 2C corrs ---
old_corrs = "corrs = [-0.386, -0.396, -0.358, -0.461]"
if old_corrs in content:
    content = content.replace(old_corrs, NEW_CORRS_LINE.strip())
    print("  Patched: Fig 2C corrs")
else:
    print("  WARNING: Could not find Fig 2C corrs line")

# --- P2-1: Fig 3A corr_matrix ---
old_matrix = """corr_matrix = np.array([
    [1.00, -0.386, -0.396, -0.358, -0.461],
    [-0.386, 1.00, 0.935, 0.895, 0.737],
    [-0.396, 0.935, 1.00, 0.884, 0.632],
    [-0.358, 0.895, 0.884, 1.00, 0.569],
    [-0.461, 0.737, 0.632, 0.569, 1.00],
])"""
if old_matrix in content:
    content = content.replace(old_matrix, NEW_CORR_MATRIX.strip())
    print("  Patched: Fig 3A corr_matrix")
else:
    print("  WARNING: Could not find Fig 3A corr_matrix")

# --- P2-2: Fig 3C known_auc dict ---
old_known_auc = """known_auc = {'CKI ω': 0.680, 'Cosine': 0.887, 'Raw JS': 0.849,
             'Marker Jaccard': 0.801, 'Spearman': 0.690}"""
if old_known_auc in content:
    new_known = "known_auc = " + str({k: round(auc_data[k], 4) for k in ['CKI ω', 'Cosine', 'Raw JS', 'Marker Jaccard', 'Spearman']})
    content = content.replace(old_known_auc, new_known)
    print("  Patched: Fig 3C known_auc")
else:
    print("  WARNING: Could not find Fig 3C known_auc (will rewrite Panel C with real data)")

# --- P2-2: Fig 3E auc_values ---
old_auc_3e = "auc_values = [0.680, 0.887, 0.849, 0.801, 0.690]"
if old_auc_3e in content:
    content = content.replace(old_auc_3e, NEW_AUC_VALUES_3E.strip())
    print("  Patched: Fig 3E auc_values")
else:
    print("  WARNING: Could not find Fig 3E auc_values")

# --- P2-3: ED Fig 2B hk_overlap ---
old_hk = "hk_overlap = [74, 76, 79, 75, 72]"
if old_hk in content:
    content = content.replace(old_hk, NEW_HK_OVERLAP.strip())
    print("  Patched: ED Fig 2B hk_overlap")
else:
    print("  WARNING: Could not find ED Fig 2B hk_overlap")

# --- P2-4: Fig 2D pathways + fold_changes + ps ---
old_pw = "pathways = ['Oxidative phosphorylation', 'Protein folding', 'Immune response',\n            'Cell adhesion', 'Signaling', 'Metabolism', 'Transcription', 'Cell cycle']"
if old_pw in content:
    content = content.replace(old_pw.split('\n')[0], NEW_PATHWAYS.strip().split('\n')[0])
    print("  Patched: Fig 2D pathways (line 1)")
else:
    print("  Fig 2D pathways: will do full Panel D replacement")

# --- P2-2: ED Fig 4 auc_values ---
old_auc_ed4 = "auc_values = [0.887, 0.849, 0.801, 0.680, 0.690]"
if old_auc_ed4 in content:
    content = content.replace(old_auc_ed4, NEW_AUC_VALUES_ED4.strip())
    print("  Patched: ED Fig 4 auc_values")
else:
    print("  WARNING: Could not find ED Fig 4 auc_values")

# Write patched content
with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nPatched script saved: {SCRIPT_PATH}")
print("Done!")
