"""
CKI Mouse Pilot v2b: Re-Validation - FIXED for memory
===================================================
FIX: Do NOT call detect_housekeeping_genes() on full matrix.
      Load HRT Atlas reference directly for mouse HK genes.
Uses CKI v0.2.0 hybrid scheme (global HK k_n + per-pair top-200 DE k_f).
Uses TWO-SIDED bootstrap test.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import scanpy as sc
from pathlib import Path
from cki.core import js_divergence
from cki.gene_sets import genes_to_indices

# ===== Config =====
DATA_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data")
FACS_DIR = DATA_DIR / "FACS" / "FACS"
HK_FILE = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"
ANNOT_FILE = DATA_DIR / "annotations_FACS.csv"
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
N_BOOTSTRAP = 500
RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10
N_TOP_KF = 200

# ===== Helper =====
def extract_mouse_id(cell_name):
    parts = cell_name.split(".")
    for p in parts:
        if "_" in p and (p.endswith("_M") or p.endswith("_F")):
            return p
    return "unknown"

def random_split_cells(cells, seed=RANDOM_SEED):
    n = cells.shape[0]
    n_half = n // 2
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    return cells[idx[:n_half]], cells[idx[n_half:]]

# ===== 1. Load Data =====
print("=" * 60)
print("1. Loading mouse data...")
print("=" * 60)

# Load HK genes from HRT Atlas file (mouse = column 0, human = column 1)
hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_mouse_genes = set(hk_df.iloc[:, 0].dropna().astype(str))  # Column 0 = Mouse
print(f"  HRT Atlas mouse HK genes: {len(hk_mouse_genes)}")

annot = pd.read_csv(ANNOT_FILE)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
annot["mouse.id"] = annot["cell"].apply(extract_mouse_id)
print(f"  Annotations: {len(annot)} cells")

adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if not fname.exists():
        continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())

# ===== 2. Build Unified AnnData =====
print("\n" + "=" * 60)
print("2. Building unified AnnData...")
print("=" * 60)

common_genes = all_genes.copy()
for tissue, df in adatas.items():
    common_genes &= set(df.index)
common_genes = sorted(common_genes)
print(f"  Common genes: {len(common_genes)}")

expr_parts, obs_parts = [], []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
    expr_parts.append(df_aligned.values)
    tissue_annot = annot[annot["tissue"] == tissue].copy()
    cell_ids = df_aligned.index.tolist()
    obs_tissue = pd.DataFrame({"cell": cell_ids, "tissue": tissue})
    obs_tissue = obs_tissue.merge(tissue_annot[["cell", "cell_ontology_class", "mouse.id"]],
                                   on="cell", how="left")
    obs_tissue["cell_ontology_class"] = obs_tissue["cell_ontology_class"].fillna("unknown")
    obs_tissue.set_index("cell", inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({"gene": common_genes}).set_index("gene")

adata = sc.AnnData(X=X, obs=obs, var=var)
adata.obs["tissue"] = adata.obs["tissue"].astype("category")
print(f"  Unified AnnData: {adata.n_obs} cells x {adata.n_vars} genes")

# ===== 3. Preprocessing =====
print("\n" + "=" * 60)
print("3. Preprocessing...")
print("=" * 60)

sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
print(f"  After QC: {adata.n_obs} cells x {adata.n_vars} genes")

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# ===== 4. HK Genes: HRT Atlas (no detect on full matrix) =====
print("\n" + "=" * 60)
print("4. HK genes from HRT Atlas reference...")
print("=" * 60)

gene_names = adata.var_names.tolist()
hk_indices = [i for i, g in enumerate(gene_names) if g in hk_mouse_genes]
print(f"  HK genes found in common set: {len(hk_indices)}")

# ===== 5. Build pseudobulks =====
print("\n" + "=" * 60)
print("5. Building pseudobulks per (tissue, ct)...")
print("=" * 60)

ct_all_cells = {}
ct_pb_largest = {}
ct_cells_largest = {}

for tissue in TARGET_TISSUES:
    tdata = adata[adata.obs["tissue"] == tissue]
    t_cts = tdata.obs["cell_ontology_class"].unique()
    for ct in t_cts:
        if ct.lower() == "unknown":
            continue
        ct_mask = tdata.obs["cell_ontology_class"] == ct
        ct_data = tdata[ct_mask]
        if ct_data.n_obs < MIN_CELLS_PER_CT * 2:
            continue
        
        X_all = ct_data.X
        if hasattr(X_all, "toarray"): 
            X_all = X_all.toarray()
        ct_all_cells[(tissue, ct)] = X_all
        
        mouse_counts = ct_data.obs["mouse.id"].value_counts()
        mice_ok = [(m, n) for m, n in mouse_counts.items() if n >= MIN_CELLS_PER_CT]
        if len(mice_ok) >= 1:
            mice_ok.sort(key=lambda x: -x[1])
            largest_mouse = mice_ok[0][0]
            mask_largest = ct_data.obs["mouse.id"] == largest_mouse
            X_largest = ct_data[mask_largest].X
            if hasattr(X_largest, "toarray"):
                X_largest = X_largest.toarray()
            if X_largest.shape[0] >= MIN_CELLS_PER_CT:
                ct_pb_largest[(tissue, ct)] = np.mean(X_largest, axis=0)
                ct_cells_largest[(tissue, ct)] = X_largest

print(f"  CTs with >= {MIN_CELLS_PER_CT*2} cells: {len(ct_all_cells)}")
print(f"  CTs with largest-mouse group: {len(ct_pb_largest)}")

# ===== 6. Define comparisons =====
print("\n" + "=" * 60)
print("6. Defining comparisons...")
print("=" * 60)

comparisons = []

# C: Control
control_pairs = [
    ("Liver", "hepatocyte"),
    ("Heart", "endothelial cell"),
    ("Spleen", "B cell"),
    ("Marrow", "B cell"),
    ("Heart", "fibroblast"),
    ("Marrow", "neutrophil"),
]
for tissue, ct in control_pairs:
    key = (tissue, ct)
    if key in ct_all_cells:
        cells_a, cells_b = random_split_cells(ct_all_cells[key])
        comparisons.append({
            "label": f"C: {ct} ({tissue})",
            "category": "C_control",
            "tissue": tissue, "ct": ct,
            "pb_a": np.mean(cells_a, axis=0),
            "pb_b": np.mean(cells_b, axis=0),
            "cells_a": cells_a, "cells_b": cells_b,
        })

# S: Same CT across tissues
same_ct_pairs = [
    ("B cell", "Marrow", "Spleen"),
    ("B cell", "Spleen", "Lung"),
    ("endothelial cell", "Heart", "Lung"),
    ("natural killer cell", "Marrow", "Liver"),
]
for ct, t1, t2 in same_ct_pairs:
    key1, key2 = (t1, ct), (t2, ct)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        comparisons.append({
            "label": f"S: {ct} ({t1} vs {t2})",
            "category": "S_same_ct",
            "tissue_a": t1, "tissue_b": t2, "ct": ct,
            "pb_a": ct_pb_largest[key1], "pb_b": ct_pb_largest[key2],
            "cells_a": ct_cells_largest[key1], "cells_b": ct_cells_largest[key2],
        })

# D: Different CT, same tissue
diff_ct_pairs = [
    ("Liver", "hepatocyte", "endothelial cell of hepatic sinusoid"),
    ("Marrow", "B cell", "neutrophil"),
    ("Heart", "endothelial cell", "fibroblast"),
]
for tissue, ct1, ct2 in diff_ct_pairs:
    key1, key2 = (tissue, ct1), (tissue, ct2)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        comparisons.append({
            "label": f"D: {ct1} vs {ct2} ({tissue})",
            "category": "D_diff_ct",
            "tissue": tissue, "ct_a": ct1, "ct_b": ct2,
            "pb_a": ct_pb_largest[key1], "pb_b": ct_pb_largest[key2],
            "cells_a": ct_cells_largest[key1], "cells_b": ct_cells_largest[key2],
        })

# X: Different CT, different tissue
cross_pairs = [
    ("Liver", "hepatocyte", "Marrow", "B cell"),
    ("Heart", "cardiac muscle cell", "Marrow", "neutrophil"),
]
for t1, ct1, t2, ct2 in cross_pairs:
    key1, key2 = (t1, ct1), (t2, ct2)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        comparisons.append({
            "label": f"X: {ct1}({t1}) vs {ct2}({t2})",
            "category": "X_cross",
            "tissue_a": t1, "tissue_b": t2, "ct_a": ct1, "ct_b": ct2,
            "pb_a": ct_pb_largest[key1], "pb_b": ct_pb_largest[key2],
            "cells_a": ct_cells_largest[key1], "cells_b": ct_cells_largest[key2],
        })

print(f"  Total comparisons: {len(comparisons)}")

# ===== 7. Run CKI v0.2.0 =====
print("\n" + "=" * 60)
print(f"7. Running CKI v0.2.0 (global HK + per-pair top-{N_TOP_KF} DE)...")
print("=" * 60)

# Build non-HK mask for k_f selection
N_GENES = len(gene_names)
non_hk_mask = np.ones(N_GENES, dtype=bool)
for idx in hk_indices:
    if idx < N_GENES:
        non_hk_mask[idx] = False
non_hk_indices = np.where(non_hk_mask)[0]
print(f"  Non-HK indices for k_f: {len(non_hk_indices)}")

results_list = []
for comp in comparisons:
    label = comp["label"]
    pb_a = comp["pb_a"]
    pb_b = comp["pb_b"]
    cells_a = comp["cells_a"]
    cells_b = comp["cells_b"]
    n_a, n_b = cells_a.shape[0], cells_b.shape[0]
    
    # k_n: global HK
    hk_i = pb_a[hk_indices]
    hk_j = pb_b[hk_indices]
    kn_val = js_divergence(hk_i, hk_j)
    
    # k_f: per-pair top-N DE (exclude HK)
    abs_diff = np.abs(pb_a - pb_b)
    abs_diff_non_hk = abs_diff[non_hk_mask]
    
    top_n = min(N_TOP_KF, len(abs_diff_non_hk))
    top_local = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
    top_local = top_local[np.argsort(abs_diff_non_hk[top_local])[::-1]]
    top_global = non_hk_indices[top_local]
    
    kf_val = js_divergence(pb_a[top_global], pb_b[top_global])
    omega_obs = kf_val / kn_val if kn_val > 0 else float('inf')
    
    # TWO-SIDED bootstrap
    pooled = np.vstack([cells_a, cells_b])
    n_total = n_a + n_b
    rng = np.random.RandomState(RANDOM_SEED)
    
    null_omega = []
    for b in range(N_BOOTSTRAP):
        perm = rng.permutation(n_total)
        pb_perm1 = np.mean(pooled[perm[:n_a]], axis=0)
        pb_perm2 = np.mean(pooled[perm[n_a:]], axis=0)
        
        hk_1 = pb_perm1[hk_indices]
        hk_2 = pb_perm2[hk_indices]
        kn_null = js_divergence(hk_1, hk_2)
        
        abs_diff_null = np.abs(pb_perm1 - pb_perm2)
        abs_diff_non_hk_null = abs_diff_null[non_hk_mask]
        top_local_null = np.argpartition(abs_diff_non_hk_null, -top_n)[-top_n:]
        top_local_null = top_local_null[np.argsort(abs_diff_non_hk_null[top_local_null])[::-1]]
        top_global_null = non_hk_indices[top_local_null]
        
        kf_null = js_divergence(pb_perm1[top_global_null], pb_perm2[top_global_null])
        omega_null_val = kf_null / (kn_null + 1e-9)
        
        if not np.isnan(omega_null_val):
            null_omega.append(omega_null_val)
    
    null_omega = np.array(null_omega)
    if len(null_omega) == 0:
        p_value, null_mean, null_std, cohens_d = 1.0, np.nan, np.nan, np.nan
    else:
        # TWO-SIDED: count(|null - 1| >= |obs - 1|)
        p_value = (np.sum(np.abs(null_omega - 1) >= np.abs(omega_obs - 1)) + 1) / (len(null_omega) + 1)
        null_mean = np.mean(null_omega)
        null_std = np.std(null_omega)
        cohens_d = (omega_obs - null_mean) / null_std if null_std > 1e-12 else 0.0
    
    sig = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else "ns"
    print(f"  {label}: omega={omega_obs:.3f}, kn={kn_val:.5f}, kf={kf_val:.5f}, "
          f"p={p_value:.4f}{sig}, d={cohens_d:.2f}")
    
    results_list.append({
        "comparison": label,
        "category": comp["category"],
        "omega": omega_obs,
        "kn": kn_val,
        "kf": kf_val,
        "p_value": p_value,
        "null_mean": null_mean,
        "null_std": null_std,
        "cohens_d": cohens_d,
        "n_cells_A": n_a,
        "n_cells_B": n_b,
    })

results_df = pd.DataFrame(results_list)

# ===== 8. Summary =====
print("\n" + "=" * 60)
print("8. Category summary...")
print("=" * 60)

for cat in ["C_control", "S_same_ct", "D_diff_ct", "X_cross"]:
    subset = results_df[results_df["category"] == cat]
    if len(subset) > 0:
        print(f"  {cat}: n={len(subset)}, mean_omega={subset['omega'].mean():.2f}, "
              f"median={subset['omega'].median():.2f}")
        for _, row in subset.iterrows():
            print(f"    {row['comparison']}: omega={row['omega']:.3f}, p={row['p_value']:.4f}")

# ===== 9. Save =====
print("\n" + "=" * 60)
print("9. Saving results...")
print("=" * 60)

results_csv = RESULTS_DIR / "mouse_pilot_v2b_results.csv"
results_df.to_csv(results_csv, index=False)
print(f"  Saved: {results_csv}")

key_vals = {}
for cat in ["C_control", "S_same_ct", "D_diff_ct", "X_cross"]:
    subset = results_df[results_df["category"] == cat]
    if len(subset) > 0:
        key_vals[f"{cat}_mean"] = round(subset["omega"].mean(), 2)
        key_vals[f"{cat}_n"] = len(subset)

ctrl = results_df[results_df["category"] == "C_control"]
if len(ctrl) > 0:
    key_vals["control_mean"] = round(ctrl["omega"].mean(), 2)
    key_vals["control_median"] = round(ctrl["omega"].median(), 2)

kv_csv = RESULTS_DIR / "mouse_pilot_v2b_key_values.csv"
pd.DataFrame([key_vals]).to_csv(kv_csv, index=False)
print(f"  Saved: {kv_csv}")

print("\n" + "=" * 60)
print("Pilot v2b analysis complete!")
print("=" * 60)
