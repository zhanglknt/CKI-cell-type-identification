"""
CKI Brain Bootstrap v2: Correct cell-level permutation test
============================================================
Fixes the critical v1 bug where permuting pre-computed pseudobulks
produced P-values ~0.5 regardless of data (code admitted 
"This doesn't change anything" at line 164).

v2 implements proper cell-level permutation:
1. Load Siletti Nonneurons.h5ad (raw counts)
2. For each cell type, extract all single cells across regions
3. Bootstrap: pool cells, permute region labels at cell level,
   recompute pseudobulks + normalize + omega for all regional pairs
4. Test statistic: mean omega across all C(n_regions, 2) pairs

Replaces both 08c_brain_bootstrap.py (broken) and
08c_brain_bootstrap_csv.py (broken, CSV-based resampling).
"""

import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
from pathlib import Path
from cki.core import js_divergence

# === Config ===
SILETTI_PATH = BRAIN_FILE  # from _paths
HK_FILE_REF = HK_FILE       # from _paths: Human_Mouse_Common.csv

N_BOOTSTRAP = 1000
RANDOM_SEED = 42
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_TOP_KF = 200

ct_col = "supercluster_term"
region_col = "roi"

# === 1. Load HK genes from HRT Atlas ===
print("=" * 60)
print("1. Loading HK genes from HRT Atlas...")
print("=" * 60)

hk_df = pd.read_csv(HK_FILE_REF, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"  HRT Atlas: {len(hk_human)} human HK genes")

# === 2. Load Siletti data in backed mode ===
print("\n" + "=" * 60)
print("2. Loading Siletti Nonneurons.h5ad (backed mode)...")
print("=" * 60)

adata = sc.read_h5ad(SILETTI_PATH)
print(f"  Shape: {adata.shape}")
print(f"  Cell types: {sorted(adata.obs[ct_col].unique())}")
print(f"  Regions: {adata.obs[region_col].nunique()}")

# Map HK gene indices via var["Gene"] column
gene_symbols = adata.var["Gene"].tolist()
hk_indices = []
for i, sym in enumerate(gene_symbols):
    if pd.notna(sym) and sym in hk_human:
        hk_indices.append(i)
hk_indices = np.array(sorted(set(hk_indices)), dtype=int)
N_GENES = adata.n_vars
print(f"  Matched HK genes: {len(hk_indices)}")

# Build non-HK mask for k_f selection
non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_indices] = False
non_hk_indices_global = np.where(non_hk_mask)[0]
print(f"  Non-HK genes (for k_f): {len(non_hk_indices_global)}")

# === 3. Filter groups and identify cell types / regions ===
print("\n" + "=" * 60)
print("3. Filtering groups...")
print("=" * 60)

groups = adata.obs.groupby([region_col, ct_col]).size().reset_index(name="count")
groups_ok = groups[groups["count"] >= MIN_NUCLEI]
region_counts = adata.obs[region_col].value_counts()
regions_ok = region_counts[region_counts >= MIN_REGION_N].index
groups_ok = groups_ok[groups_ok[region_col].isin(regions_ok)]

cts_present = sorted(groups_ok[ct_col].unique())
print(f"  Groups passing: {len(groups_ok)} (from {len(groups)} total)")
print(f"  Cell types: {len(cts_present)}: {cts_present}")

# Build region lists per cell type
ct_to_regions = {}
for _, row in groups_ok.iterrows():
    ct = row[ct_col]
    r = row[region_col]
    if ct not in ct_to_regions:
        ct_to_regions[ct] = []
    if r not in ct_to_regions[ct]:
        ct_to_regions[ct].append(r)

# === 4. Pre-compute OBSERVED omega per cell type ===
print("\n" + "=" * 60)
print("4. Computing OBSERVED omega for each cell type...")
print("=" * 60)

# Compute pseudobulks for observed data
pseudobulk_obs = {}  # (ct, region) -> normalized pseudobulk
for ct in cts_present:
    for region in ct_to_regions[ct]:
        mask = (adata.obs[region_col] == region) & (adata.obs[ct_col] == ct)
        X = adata[mask].X
        if hasattr(X, "toarray"):
            pb = np.array(X.mean(axis=0)).flatten()
        else:
            pb = np.mean(X, axis=0)
        # Normalize
        total = pb.sum()
        if total > 0:
            pb_norm = pb / total * 1e4
        else:
            pb_norm = pb
        pb_log = np.log1p(pb_norm)
        pseudobulk_obs[(ct, region)] = pb_log.astype(np.float32)

# Compute observed omega for all pairs
obs_results = {}
for ct in cts_present:
    regions = ct_to_regions[ct]
    n_r = len(regions)
    n_pairs = n_r * (n_r - 1) // 2
    
    if n_pairs < 5:
        print(f"  {ct}: SKIP (only {n_pairs} pairs)")
        continue
    
    obs_omegas = []
    for i in range(n_r):
        for j in range(i + 1, n_r):
            pb_i = pseudobulk_obs[(ct, regions[i])]
            pb_j = pseudobulk_obs[(ct, regions[j])]
            
            # k_n: global HK
            kn_val = js_divergence(pb_i[hk_indices], pb_j[hk_indices])
            
            # k_f: per-pair top-N DE (exclude HK)
            abs_diff = np.abs(pb_i - pb_j)
            abs_diff_non_hk = abs_diff.copy()
            abs_diff_non_hk[hk_indices] = -1  # ensure HK never selected
            top_n = min(N_TOP_KF, len(non_hk_indices_global))
            top = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
            top = top[np.argsort(abs_diff_non_hk[top])[::-1]]
            top = top[abs_diff_non_hk[top] >= 0]
            
            kf_val = js_divergence(pb_i[top], pb_j[top])
            omega_val = kf_val / kn_val if kn_val > 0 else float('inf')
            obs_omegas.append(omega_val)
    
    obs_mean = np.mean(obs_omegas) if obs_omegas else 0.0
    obs_max = np.max(obs_omegas) if obs_omegas else 0.0
    
    obs_results[ct] = {
        "n_regions": n_r,
        "n_pairs": n_pairs,
        "omega_mean": obs_mean,
        "omega_max": obs_max,
        "omega_std": np.std(obs_omegas),
        "omegas": obs_omegas,
    }
    print(f"  {ct}: {n_r} regions, {n_pairs} pairs, mean_omega={obs_mean:.2f}")

# Free pseudobulk_obs to save memory
del pseudobulk_obs
gc.collect()

# === 5. Bootstrap: cell-level permutation (one cell type at a time) ===
print("\n" + "=" * 60)
print(f"5. Bootstrap (B={N_BOOTSTRAP}) — cell-level permutation...")
print("=" * 60)

rng = np.random.RandomState(RANDOM_SEED)
all_bootstrap_results = []

for ct in cts_present:
    if ct not in obs_results:
        continue
    
    regions = ct_to_regions[ct]
    n_r = len(regions)
    n_pairs = obs_results[ct]["n_pairs"]
    
    print(f"\n  --- {ct} ({n_r} regions, {n_pairs} pairs) ---")
    
    # 5a. Extract all single cells for this cell type
    t0 = time.time()
    ct_cells = {}       # region -> list of cell vectors (raw counts)
    region_sizes = {}   # region -> number of cells
    
    for region in regions:
        mask = (adata.obs[region_col] == region) & (adata.obs[ct_col] == ct)
        idx = np.where(mask)[0]
        n_cells = len(idx)
        if n_cells == 0:
            continue
        region_sizes[region] = n_cells
        
        # Load cells
        X_sub = adata[idx].X
        if hasattr(X_sub, "toarray"):
            X_sub = X_sub.toarray()
        ct_cells[region] = np.asarray(X_sub, dtype=np.float32)
    
    # Pool all cells and region labels
    all_cells_list = []
    region_label_list = []
    for region in regions:
        if region in ct_cells:
            all_cells_list.append(ct_cells[region])
            region_label_list.extend([region] * ct_cells[region].shape[0])
    
    all_cells = np.vstack(all_cells_list)
    region_labels = np.array(region_label_list)
    n_total_cells = all_cells.shape[0]
    
    # Build region->start position mapping for efficient permutation
    region_order = sorted(region_sizes.keys())
    region_size_list = [region_sizes[r] for r in region_order]
    region_cumsum = np.cumsum([0] + region_size_list)
    
    print(f"    Extracted {n_total_cells} cells in {time.time()-t0:.0f}s")
    
    # 5b. Bootstrap loop
    obs_mean = obs_results[ct]["omega_mean"]
    null_means = []
    t_start = time.time()
    
    for b in range(N_BOOTSTRAP):
        perm = rng.permutation(n_total_cells)
        
        # Compute pseudobulks for permuted groups
        perm_pbs = {}  # region -> normalized pseudobulk
        for ri, region in enumerate(region_order):
            start = region_cumsum[ri]
            end = region_cumsum[ri + 1]
            perm_indices = perm[start:end]
            perm_cells = all_cells[perm_indices]
            pb_raw = np.mean(perm_cells, axis=0)
            
            # Normalize (same as observed)
            total = pb_raw.sum()
            if total > 0:
                pb_norm = pb_raw / total * 1e4
            else:
                pb_norm = pb_raw
            perm_pbs[region] = np.log1p(pb_norm).astype(np.float32)
        
        # Compute omega for all permuted pairs
        perm_omegas = []
        for i in range(n_r):
            for j in range(i + 1, n_r):
                pb_i = perm_pbs[region_order[i]]
                pb_j = perm_pbs[region_order[j]]
                
                kn_val = js_divergence(pb_i[hk_indices], pb_j[hk_indices])
                
                abs_diff = np.abs(pb_i - pb_j)
                abs_diff_non_hk = abs_diff.copy()
                abs_diff_non_hk[hk_indices] = -1
                top_n = min(N_TOP_KF, len(non_hk_indices_global))
                top = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
                top = top[np.argsort(abs_diff_non_hk[top])[::-1]]
                top = top[abs_diff_non_hk[top] >= 0]
                
                kf_val = js_divergence(pb_i[top], pb_j[top])
                omega_val = kf_val / kn_val if kn_val > 0 else float('inf')
                perm_omegas.append(omega_val)
        
        if perm_omegas:
            null_means.append(np.mean(perm_omegas))
        
        # Progress
        if (b + 1) % 200 == 0:
            elapsed = time.time() - t_start
            eta = elapsed / (b + 1) * (N_BOOTSTRAP - b - 1)
            print(f"    Iter {b+1}/{N_BOOTSTRAP}, elapsed={elapsed:.0f}s, ETA={eta:.0f}s")
    
    # 5c. Compute statistics
    null_means = np.array(null_means)
    null_mean_val = float(np.mean(null_means))
    null_std_val = float(np.std(null_means))
    
    # P-value: two-sided, consistent with mouse/TCGA (|omega-1| test statistic)
    obs_dist = abs(obs_mean - 1.0)
    null_dists = np.abs(null_means - 1.0)
    p_value = (np.sum(null_dists >= obs_dist) + 1) / (len(null_means) + 1)
    
    cohens_d = (obs_mean - null_mean_val) / null_std_val if null_std_val > 1e-12 else 0.0
    ci_95_lower = float(np.percentile(null_means, 2.5))
    ci_95_upper = float(np.percentile(null_means, 97.5))
    
    elapsed_ct = time.time() - t_start
    print(f"    Done in {elapsed_ct:.0f}s")
    print(f"    obs_mean={obs_mean:.4f}, null_mean={null_mean_val:.4f}, "
          f"null_std={null_std_val:.4f}")
    print(f"    p_value={p_value:.4e}, d={cohens_d:.2f}, "
          f"95% CI=[{ci_95_lower:.4f}, {ci_95_upper:.4f}]")
    
    all_bootstrap_results.append({
        "cell_type": ct,
        "n_regions": n_r,
        "n_pairs": n_pairs,
        "n_cells": n_total_cells,
        "omega_mean": f"{obs_mean:.4f}",
        "omega_max": f"{obs_results[ct]['omega_max']:.4f}",
        "omega_std": f"{obs_results[ct]['omega_std']:.4f}",
        "p_value": f"{p_value:.4e}",
        "null_mean": f"{null_mean_val:.4f}",
        "null_std": f"{null_std_val:.4f}",
        "cohens_d": f"{cohens_d:.4f}",
        "ci_95_lower": f"{ci_95_lower:.4f}",
        "ci_95_upper": f"{ci_95_upper:.4f}",
    })
    
    # Free cell data for this ct
    del ct_cells, all_cells, region_labels, null_means
    gc.collect()

# Free adata
del adata
gc.collect()

# === 6. Save results ===
print("\n" + "=" * 60)
print("6. Saving results...")
print("=" * 60)

df = pd.DataFrame(all_bootstrap_results)
df = df.sort_values("omega_mean", ascending=False)
print("\n" + df.to_string(index=False))

output_path = RESULTS_DIR / "brain_bootstrap_results.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved: {output_path}")

# Also save summary key values
p_vals = [float(r["p_value"]) for r in all_bootstrap_results]
n_sig_005 = sum(1 for p in p_vals if p < 0.05)
n_sig_001 = sum(1 for p in p_vals if p < 0.01)

print(f"\nSummary:")
print(f"  Cell types tested: {len(all_bootstrap_results)}")
print(f"  P < 0.05: {n_sig_005}")
print(f"  P < 0.01: {n_sig_001}")
print(f"  P-value range: [{min(p_vals):.4e}, {max(p_vals):.4e}]")

print("\nDone! Brain bootstrap v2 complete.")
