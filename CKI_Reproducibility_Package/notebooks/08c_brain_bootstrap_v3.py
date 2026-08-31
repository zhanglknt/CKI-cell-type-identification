"""
CKI Brain Bootstrap v3: Backed mode + HVG pre-filtering
=========================================================
Fixes v2 OOM: Oligodendrocyte 490K cells x 59K genes = ~115GB (dense).

Strategy:
1. Open Siletti Nonneurons.h5ad in backed='r' mode (no full load)
2. Compute global gene means ONCE (O(nnz) pass) to select top-5000 HVG
3. For each cell type: extract only HK + HVG genes (~6K) as CSR sparse
   → memory reduction ~10x (59K → 6K genes)
4. Bootstrap with cell-level permutation as in v2

Gene sets:
- k_n: HK genes (mapped to reduced gene set)
- k_f: top-200 by |pseudobulk difference| from reduced non-HK set
"""

import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

# Force unbuffered stdout for real-time log visibility
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)

import numpy as np
import pandas as pd
import scanpy as sc
import h5py
from scipy.sparse import issparse, csr_matrix
from pathlib import Path
from cki.core import js_divergence
from cki.bootstrap import benjamini_hochberg


def extract_csr_from_backed(h5_path, cell_indices, keep_global, n_genes_total,
                            chunk_size=20000):
    """
    Extract CSR matrix for selected cells, keeping only keep_global genes.
    
    Optimized: chunk-based h5py batch reads instead of per-cell reads.
    For 490K cells: ~25 batch reads vs ~490K per-cell reads → ~100x I/O speedup.
    
    Strategy:
    1. Sort cell indices by global row → contiguous I/O
    2. Process in chunks of chunk_size sorted cells
    3. Per chunk: ONE h5py read for indices + ONE for data
    4. Gene filtering done in-memory (vectorized per chunk)
    5. Unsort results to match original cell order
    
    Parameters
    ----------
    h5_path : str/Path
        Path to the .h5ad file
    cell_indices : ndarray (int)
        Global row indices of cells to extract
    keep_global : ndarray (int)
        Global gene indices to retain
    n_genes_total : int
        Total number of genes in the full dataset
    chunk_size : int
        Number of cells per h5py read batch (default 20000)
    
    Returns
    -------
    csr_matrix of shape (len(cell_indices), len(keep_global))
    """
    n_cells = len(cell_indices)
    n_keep = len(keep_global)
    
    if n_cells == 0:
        return csr_matrix((0, n_keep), dtype=np.float32)
    
    # Gene index mapping: global -> local (-1 for dropped genes)
    gene_map = np.full(n_genes_total, -1, dtype=np.int32)
    gene_map[keep_global] = np.arange(n_keep, dtype=np.int32)
    
    # Sort by global cell index for contiguous I/O
    sort_order = np.argsort(cell_indices, kind='stable')
    sorted_cells = cell_indices[sort_order]
    # Reverse mapping: sorted position -> original position
    unsort = np.empty(n_cells, dtype=np.int64)
    unsort[sort_order] = np.arange(n_cells)
    
    # Per-cell results (indexed by original cell order)
    new_data_list = [None] * n_cells
    new_idx_list = [None] * n_cells
    # Per-cell nnz counts in SORTED order (filled during loop)
    cell_nnz_sorted = np.zeros(n_cells, dtype=np.int64)
    
    with h5py.File(h5_path, 'r') as f:
        X = f['X']
        # Read full indptr once (~3.5MB for 888K cells)
        indptr_full = X['indptr'][:]
        
        n_chunks = (n_cells + chunk_size - 1) // chunk_size
        for chunk_i in range(n_chunks):
            chunk_start = chunk_i * chunk_size
            chunk_end = min(chunk_start + chunk_size, n_cells)
            chunk_cells = sorted_cells[chunk_start:chunk_end]
            
            # Global data range covering entire chunk
            data_start = int(indptr_full[chunk_cells[0]])
            data_end = int(indptr_full[chunk_cells[-1] + 1])
            
            if data_end > data_start:
                # Single batch read for all indices and data in this chunk
                chunk_indices = X['indices'][data_start:data_end]
                chunk_data = X['data'][data_start:data_end]
                # Map all gene indices at once (vectorized)
                chunk_mapped = gene_map[chunk_indices]
                chunk_keep = chunk_mapped >= 0
            else:
                chunk_mapped = np.array([], dtype=np.int32)
                chunk_keep = np.array([], dtype=bool)
                chunk_data = np.array([], dtype=X['data'].dtype)
            
            # Per-cell filtering from in-memory arrays
            for ci in range(chunk_start, chunk_end):
                orig_pos = int(sort_order[ci])   # FIX (was unsort[ci])
                global_row = int(sorted_cells[ci])
                r_start = int(indptr_full[global_row]) - data_start
                r_end = int(indptr_full[global_row + 1]) - data_start
                
                if r_start == r_end:
                    continue  # cell_nnz_sorted[ci] stays 0
                
                keep_mask = chunk_keep[r_start:r_end]
                n_kept = int(keep_mask.sum())
                cell_nnz_sorted[ci] = n_kept
                
                if n_kept > 0:
                    new_data_list[orig_pos] = chunk_data[r_start:r_end][keep_mask]
                    new_idx_list[orig_pos] = chunk_mapped[r_start:r_end][keep_mask]
            
            if n_chunks > 5 and (chunk_i + 1) % 5 == 0:
                print(f"      Extraction chunk {chunk_i+1}/{n_chunks} "
                      f"({chunk_end}/{n_cells} sorted cells)")
    
    # Build indptr: map nnz counts from sorted order to original order, then cumsum
    cell_nnz_orig = np.zeros(n_cells, dtype=np.int64)
    cell_nnz_orig[sort_order] = cell_nnz_sorted   # FIX (was unsort)
    new_indptr = np.zeros(n_cells + 1, dtype=np.int64)
    np.cumsum(cell_nnz_orig, out=new_indptr[1:])
    
    nnz = int(new_indptr[-1])
    if nnz == 0:
        return csr_matrix((n_cells, n_keep), dtype=np.float32)
    
    # Concatenate in original cell order
    all_data = [d for d in new_data_list if d is not None]
    all_idx = [d for d in new_idx_list if d is not None]
    
    new_data = np.concatenate(all_data)
    new_indices_arr = np.concatenate(all_idx)
    
    return csr_matrix((new_data, new_indices_arr, new_indptr), shape=(n_cells, n_keep))


# === Config ===
SILETTI_PATH = BRAIN_FILE  # data/brain/Nonneurons.h5ad
HK_FILE_REF = HK_FILE       # Human_Mouse_Common.csv

N_BOOTSTRAP = 1000
RANDOM_SEED = 42
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000  # number of HVG genes to retain (excluding HK)

ct_col = "supercluster_term"
region_col = "roi"


# ============================================================
# 1. Load HK genes from HRT Atlas
# ============================================================
print("=" * 60)
print("1. Loading HK genes from HRT Atlas...")
print("=" * 60)

hk_df = pd.read_csv(HK_FILE_REF, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"  HRT Atlas: {len(hk_human)} human HK genes")

# ============================================================
# 2. Open Siletti in backed='r' mode
# ============================================================
print("\n" + "=" * 60)
print("2. Opening Siletti Nonneurons.h5ad (backed='r')...")
print("=" * 60)

t0 = time.time()
adata = sc.read_h5ad(SILETTI_PATH, backed='r')
print(f"  Shape: {adata.shape}  (backed, loaded in {time.time()-t0:.0f}s)")
print(f"  X type: {type(adata.X)}")
print(f"  Cell types: {sorted(adata.obs[ct_col].unique())}")
print(f"  Regions: {adata.obs[region_col].nunique()}")

N_GENES = adata.n_vars
N_CELLS = adata.n_obs

# Map HK genes to global indices via var["Gene"]
gene_symbols = adata.var["Gene"].tolist()
hk_global = []
for i, sym in enumerate(gene_symbols):
    if pd.notna(sym) and sym in hk_human:
        hk_global.append(i)
hk_global = np.array(sorted(set(hk_global)), dtype=int)
print(f"  Matched HK genes: {len(hk_global)}")

# ============================================================
# 3. Compute global HVG (top-N by mean expression, exclude HK)
# ============================================================
print("\n" + "=" * 60)
print(f"3. Computing global gene means for HVG selection...")
print("=" * 60)

t0 = time.time()
BATCH_SIZE = 50000
gene_sums = np.zeros(N_GENES, dtype=np.float64)
for start in range(0, N_CELLS, BATCH_SIZE):
    end = min(start + BATCH_SIZE, N_CELLS)
    X_batch = adata[start:end].X
    if issparse(X_batch):
        gene_sums += np.array(X_batch.sum(axis=0)).flatten()
    else:
        gene_sums += X_batch.sum(axis=0)
    if start % 200000 == 0 and start > 0:
        print(f"    Processed {start}/{N_CELLS} cells...")
gene_means = gene_sums / N_CELLS
elapsed = time.time() - t0
print(f"  Computed means for {N_GENES} genes in {elapsed:.0f}s")

# Select top-N_HVG non-HK genes by mean expression
non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_global] = False

non_hk_means = gene_means.copy()
non_hk_means[~non_hk_mask] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
print(f"  Selected top {N_HVG} HVG (non-HK, by mean expression)")

# ============================================================
# 4. Build reduced gene set: HK + HVG
# ============================================================
keep_global = np.sort(np.union1d(hk_global, hvg_global))
N_KEEP = len(keep_global)
print(f"  Reduced gene set: {N_KEEP} genes (HK={len(hk_global)} + HVG={len(np.intersect1d(hvg_global, keep_global))})")

# Map HK indices to positions within the reduced set
is_hk_in_keep = np.isin(keep_global, hk_global)
hk_in_reduced = np.where(is_hk_in_keep)[0]
non_hk_in_reduced = np.where(~is_hk_in_keep)[0]
print(f"  HK positions in reduced set: {len(hk_in_reduced)}")
print(f"  Non-HK positions in reduced set: {len(non_hk_in_reduced)}")

# ============================================================
# 5. Filter groups and identify cell types / regions
# ============================================================
print("\n" + "=" * 60)
print("5. Filtering groups...")
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

# Print cell counts per CT
print(f"\n  Cells per cell type:")
for ct in cts_present:
    n_cells = groups_ok[groups_ok[ct_col] == ct]["count"].sum()
    n_regions = len(ct_to_regions[ct])
    n_pairs = n_regions * (n_regions - 1) // 2
    print(f"    {ct}: {n_cells} cells, {n_regions} regions, {n_pairs} pairs")

# ============================================================
# 6. Per-CT: Extract cells (h5py) → Observed ω → Bootstrap
#    Combined into single loop to avoid double extraction
# ============================================================
print("\n" + "=" * 60)
print(f"6. Per-CT extraction + observed omega + bootstrap (B={N_BOOTSTRAP})")
print("=" * 60)

rng = np.random.RandomState(RANDOM_SEED)
all_bootstrap_results = []
STR_H5AD = str(SILETTI_PATH)

for ct in cts_present:
    regions = ct_to_regions[ct]
    n_r = len(regions)
    n_pairs = n_r * (n_r - 1) // 2
    
    if n_pairs < 5:
        print(f"\n  {ct}: SKIP (only {n_pairs} pairs)")
        continue
    
    t_ct = time.time()
    print(f"\n  --- {ct} ({n_r} regions, {n_pairs} pairs) ---")
    
    # 6a. Get global cell indices for this CT (only in regions that passed filter), sorted by region
    ct_mask = (adata.obs[ct_col] == ct).values
    region_mask = np.isin(adata.obs[region_col].values, regions)
    ct_mask = ct_mask & region_mask
    ct_global_indices = np.where(ct_mask)[0]
    region_of_cell = adata.obs[region_col].values[ct_global_indices]
    
    sort_idx = np.argsort(region_of_cell)
    sorted_region = region_of_cell[sort_idx]
    ct_global_sorted = ct_global_indices[sort_idx]
    
    # 6b. Extract CSR via direct h5py (avoids backed-mode to_memory() OOM)
    t0 = time.time()
    X_ct_sparse = extract_csr_from_backed(
        STR_H5AD, ct_global_sorted, keep_global, N_GENES
    )
    n_cells_ct = X_ct_sparse.shape[0]
    nnz = X_ct_sparse.nnz
    sparsity = nnz / (n_cells_ct * N_KEEP) * 100
    print(f"    Extracted {n_cells_ct} cells x {N_KEEP} genes "
          f"(CSR, {nnz} nnz, {sparsity:.1f}% dense, "
          f"~{X_ct_sparse.data.nbytes/1e6:.1f}MB data, {time.time()-t0:.0f}s)")
    
    # 6c. Region boundaries (cells already sorted by region)
    region_order = sorted(regions)
    region_sizes = {}
    region_starts = {}
    cum = 0
    for region in region_order:
        n = int(np.sum(sorted_region == region))
        region_sizes[region] = n
        region_starts[region] = cum
        cum += n
    assert cum == n_cells_ct, f"Region size sum {cum} != n_cells {n_cells_ct}"
    
    # 6d. Compute observed pseudobulks + omega
    obs_pbs = {}
    for region in region_order:
        r_start = region_starts[region]
        r_end = r_start + region_sizes[region]
        pb_raw = np.array(X_ct_sparse[r_start:r_end].mean(axis=0)).flatten()
        total = pb_raw.sum()
        if total > 0:
            pb_norm = pb_raw / total * 1e4
        else:
            pb_norm = pb_raw
        obs_pbs[region] = np.log1p(pb_norm).astype(np.float32)
    
    obs_omegas = []
    for i in range(n_r):
        for j in range(i + 1, n_r):
            pb_i = obs_pbs[regions[i]]
            pb_j = obs_pbs[regions[j]]
            
            kn_val = js_divergence(pb_i[hk_in_reduced], pb_j[hk_in_reduced])
            
            abs_diff = np.abs(pb_i - pb_j)
            abs_diff_non_hk = abs_diff[non_hk_in_reduced]
            top_n = min(N_TOP_KF, len(non_hk_in_reduced))
            top_local = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
            top_local = top_local[np.argsort(abs_diff_non_hk[top_local])[::-1]]
            top_genes = non_hk_in_reduced[top_local]
            
            kf_val = js_divergence(pb_i[top_genes], pb_j[top_genes])
            omega_val = kf_val / kn_val if kn_val > 0 else float('inf')
            obs_omegas.append(omega_val)
    
    obs_mean = float(np.mean(obs_omegas))
    obs_max = float(np.max(obs_omegas))
    obs_std = float(np.std(obs_omegas))
    print(f"    Observed: {len(obs_omegas)} pairs, mean={obs_mean:.2f}, "
          f"max={obs_max:.2f}, std={obs_std:.2f}")
    
    # 6e. Bootstrap
    null_means = []
    region_cumsum = np.cumsum([0] + [region_sizes[r] for r in region_order])
    t_bs = time.time()
    
    for b in range(N_BOOTSTRAP):
        perm = rng.permutation(n_cells_ct)
        
        perm_pbs = {}
        for ri, region in enumerate(region_order):
            start = region_cumsum[ri]
            end = region_cumsum[ri + 1]
            perm_rows = perm[start:end]
            X_perm = X_ct_sparse[perm_rows]
            pb_raw = np.array(X_perm.mean(axis=0)).flatten()
            
            total = pb_raw.sum()
            if total > 0:
                pb_norm = pb_raw / total * 1e4
            else:
                pb_norm = pb_raw
            perm_pbs[region] = np.log1p(pb_norm).astype(np.float32)
        
        perm_omegas = []
        for i in range(n_r):
            for j in range(i + 1, n_r):
                pb_i = perm_pbs[region_order[i]]
                pb_j = perm_pbs[region_order[j]]
                
                kn_val = js_divergence(pb_i[hk_in_reduced], pb_j[hk_in_reduced])
                
                abs_diff = np.abs(pb_i - pb_j)
                abs_diff_non_hk = abs_diff[non_hk_in_reduced]
                top_n = min(N_TOP_KF, len(non_hk_in_reduced))
                top_local = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
                top_local = top_local[np.argsort(abs_diff_non_hk[top_local])[::-1]]
                top_genes = non_hk_in_reduced[top_local]
                
                kf_val = js_divergence(pb_i[top_genes], pb_j[top_genes])
                omega_val = kf_val / kn_val if kn_val > 0 else float('inf')
                perm_omegas.append(omega_val)
        
        if perm_omegas:
            null_means.append(np.mean(perm_omegas))
        
        if (b + 1) % 200 == 0:
            elapsed = time.time() - t_bs
            eta = elapsed / (b + 1) * (N_BOOTSTRAP - b - 1)
            print(f"    Iter {b+1}/{N_BOOTSTRAP}, elapsed={elapsed:.0f}s, "
                  f"ETA={eta:.0f}s")
    
    # 6f. Statistics
    null_means = np.array(null_means)
    null_mean_val = float(np.mean(null_means))
    null_std_val = float(np.std(null_means))
    
    # One-sided permutation test: H0 = no regional variation (ω not elevated)
    p_value = (np.sum(null_means >= obs_mean) + 1) / (len(null_means) + 1)
    
    cohens_d = (obs_mean - null_mean_val) / null_std_val if null_std_val > 1e-12 else 0.0
    ci_95_lower = float(np.percentile(null_means, 2.5))
    ci_95_upper = float(np.percentile(null_means, 97.5))
    
    bs_elapsed = time.time() - t_bs
    ct_elapsed = time.time() - t_ct
    print(f"    BS done in {bs_elapsed:.0f}s (total CT: {ct_elapsed:.0f}s)")
    print(f"    obs_mean={obs_mean:.4f}, null_mean={null_mean_val:.4f}, "
          f"null_std={null_std_val:.4f}")
    print(f"    p_value={p_value:.4e}, d={cohens_d:.2f}, "
          f"95% CI=[{ci_95_lower:.4f}, {ci_95_upper:.4f}]")
    
    all_bootstrap_results.append({
        "cell_type": ct,
        "n_regions": n_r,
        "n_pairs": n_pairs,
        "n_cells": n_cells_ct,
        "omega_mean": f"{obs_mean:.4f}",
        "omega_max": f"{obs_max:.4f}",
        "omega_std": f"{obs_std:.4f}",
        "p_value": f"{p_value:.4e}",
        "null_mean": f"{null_mean_val:.4f}",
        "null_std": f"{null_std_val:.4f}",
        "cohens_d": f"{cohens_d:.4f}",
        "ci_95_lower": f"{ci_95_lower:.4f}",
        "ci_95_upper": f"{ci_95_upper:.4f}",
    })
    
    # Free CT data
    del X_ct_sparse, obs_pbs, null_means, ct_global_indices, sorted_region
    gc.collect()

# Close backed file
adata.file.close()
del adata
gc.collect()

# ============================================================
# 7. Save results
# ============================================================
print("\n" + "=" * 60)
print("7. Saving results...")
print("=" * 60)

df = pd.DataFrame(all_bootstrap_results)
df = df.sort_values("omega_mean", ascending=False)

# Apply Benjamini-Hochberg FDR correction
p_vals_numeric = np.array([float(r["p_value"]) for r in all_bootstrap_results])
q_vals = benjamini_hochberg(p_vals_numeric)
# Map q-values back to sorted DataFrame order
p_to_q = dict(zip(p_vals_numeric, q_vals))
df["q_value"] = df["p_value"].astype(float).map(p_to_q)
df["q_value"] = df["q_value"].astype(str).str.replace(r"(\.\d{4}).*", r"\1", regex=True)

print("\n" + df.to_string(index=False))

output_path = RESULTS_DIR / "brain_bootstrap_results.csv"
df.to_csv(output_path, index=False)
print(f"\nSaved: {output_path}")

# Summary
p_vals = [float(r["p_value"]) for r in all_bootstrap_results]
q_vals_list = q_vals.tolist()
n_sig_005 = sum(1 for p in p_vals if p < 0.05)
n_sig_001 = sum(1 for p in p_vals if p < 0.01)
n_fdr_005 = sum(1 for q in q_vals_list if q < 0.05)
n_fdr_001 = sum(1 for q in q_vals_list if q < 0.01)

print(f"\nSummary:")
print(f"  Cell types tested: {len(all_bootstrap_results)}")
print(f"  P < 0.05: {n_sig_005}")
print(f"  P < 0.01: {n_sig_001}")
print(f"  FDR < 0.05: {n_fdr_005}")
print(f"  FDR < 0.01: {n_fdr_001}")
print(f"  P-value range: [{min(p_vals):.4e}, {max(p_vals):.4e}]")
print(f"  Q-value range: [{min(q_vals_list):.4e}, {max(q_vals_list):.4e}]")
print(f"  P-value range: [{min(p_vals):.4e}, {max(p_vals):.4e}]")

print("\nDone! Brain bootstrap v3 complete.")
