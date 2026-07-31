"""
Debug extraction: check why Astrocyte extraction produces only 7689 nnz.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
import h5py
from scipy.sparse import csr_matrix, issparse

SILETTI_PATH = BRAIN_FILE
HK_FILE_REF = HK_FILE
ct_col = "supercluster_term"
N_HVG = 5000

print("Debug extraction test")
print("=" * 60)

# 1. Load HK
hk_df = pd.read_csv(HK_FILE_REF, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))

# 2. Open backed
adata = sc.read_h5ad(SILETTI_PATH, backed='r')
N_GENES = adata.n_vars
N_CELLS = adata.n_obs
gene_symbols = adata.var["Gene"].tolist()
hk_global = np.array(sorted(set(
    i for i, sym in enumerate(gene_symbols) if pd.notna(sym) and sym in hk_human
)), dtype=int)
print(f"Shape: {adata.shape}, HK: {len(hk_global)}")

# 3. Compute gene means (quick - use first 100K cells)
print("Computing gene means on first 100K cells...")
t0 = time.time()
BATCH = 50000
gene_sums = np.zeros(N_GENES, dtype=np.float64)
for start in range(0, min(N_CELLS, 100000), BATCH):
    end = min(start + BATCH, 100000)
    X_batch = adata[start:end].X
    if issparse(X_batch):
        gene_sums += np.array(X_batch.sum(axis=0)).flatten()
    else:
        gene_sums += X_batch.sum(axis=0)
gene_means = gene_sums / min(N_CELLS, 100000)
print(f"  Done in {time.time()-t0:.0f}s")

non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_global] = False
non_hk_means = gene_means.copy()
non_hk_means[~non_hk_mask] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
keep_global = np.sort(np.union1d(hk_global, hvg_global))
N_KEEP = len(keep_global)
print(f"keep_global: {N_KEEP} genes, range [{keep_global[0]}, {keep_global[-1]}]")

# 4. Get Astrocyte cells (SAME as main script: sorted by region)
ct = "Astrocyte"
ct_mask = (adata.obs[ct_col] == ct).values
ct_global_indices = np.where(ct_mask)[0]
region_of_cell = adata.obs["roi"].values[ct_global_indices]
sort_idx = np.argsort(region_of_cell)
sorted_region = region_of_cell[sort_idx]
ct_global_sorted = ct_global_indices[sort_idx]
print(f"\n{ct}: {len(ct_global_sorted)} cells")
print(f"  ct_global_sorted[:5]: {ct_global_sorted[:5]}")
print(f"  ct_global_sorted range: [{ct_global_sorted[0]}, {ct_global_sorted[-1]}]")

# 5. Test extraction with debug
gene_map = np.full(N_GENES, -1, dtype=np.int32)
gene_map[keep_global] = np.arange(N_KEEP, dtype=np.int32)
print(f"  gene_map: {N_GENES} entries, {N_KEEP} mapped (>0)")

STR_H5AD = str(SILETTI_PATH)
cell_indices = ct_global_sorted
chunk_size = 20000

# Sort by global index
sort_order = np.argsort(cell_indices, kind='stable')
sorted_cells = cell_indices[sort_order]
unsort = np.empty(len(cell_indices), dtype=np.int64)
unsort[sort_order] = np.arange(len(cell_indices))

print(f"\n  sorted_cells[:5]: {sorted_cells[:5]}")
print(f"  unsort[:5]: {unsort[:5]}")
print(f"  Are sorted_cells actually sorted? {(np.diff(sorted_cells) >= 0).all()}")

with h5py.File(STR_H5AD, 'r') as f:
    X = f['X']
    indptr_full = X['indptr'][:]
    print(f"\n  indptr_full dtype: {indptr_full.dtype}, shape: {indptr_full.shape}")
    print(f"  indptr_full range: [{indptr_full[0]}, {indptr_full[-1]}]")
    
    # Process first chunk
    chunk_start = 0
    chunk_end = min(chunk_size, len(sorted_cells))
    chunk_cells = sorted_cells[chunk_start:chunk_end]
    
    data_start = int(indptr_full[chunk_cells[0]])
    data_end = int(indptr_full[chunk_cells[-1] + 1])
    print(f"\n  Chunk 0: {chunk_end} cells")
    print(f"  chunk_cells[:5]: {chunk_cells[:5]}")
    print(f"  chunk_cells[-1]: {chunk_cells[-1]}")
    print(f"  data_start={data_start}, data_end={data_end}")
    print(f"  data range size: {data_end - data_start}")
    
    if data_end > data_start:
        chunk_indices = X['indices'][data_start:data_end]
        chunk_data = X['data'][data_start:data_end]
        print(f"  chunk_indices dtype: {chunk_indices.dtype}, shape: {chunk_indices.shape}")
        print(f"  chunk_data dtype: {chunk_data.dtype}, shape: {chunk_data.shape}")
        print(f"  chunk_indices[:10]: {chunk_indices[:10]}")
        print(f"  chunk_indices range: [{chunk_indices.min()}, {chunk_indices.max()}]")
        
        chunk_mapped = gene_map[chunk_indices]
        chunk_keep = chunk_mapped >= 0
        n_keep_total = int(chunk_keep.sum())
        n_total = len(chunk_indices)
        print(f"\n  Gene filtering:")
        print(f"  Total entries: {n_total}")
        print(f"  Kept entries: {n_keep_total} ({n_keep_total/n_total*100:.1f}%)")
        
        # Per-cell check for first 5 cells
        print(f"\n  Per-cell check (first 5 cells in sorted order):")
        for ci in range(5):
            global_row = int(sorted_cells[ci])
            r_start = int(indptr_full[global_row]) - data_start
            r_end = int(indptr_full[global_row + 1]) - data_start
            n_cell_total = r_end - r_start
            keep_mask = chunk_keep[r_start:r_end]
            n_cell_kept = int(keep_mask.sum())
            print(f"    Cell {ci} (global={global_row}): "
                  f"r=[{r_start},{r_end}], total={n_cell_total}, kept={n_cell_kept}")
    
    # Compare with scanpy backed extraction for same cells
    print(f"\n  Scanpy backed extraction (ground truth, first 100 cells):")
    gt_indices = sorted_cells[:100]  # first 100 sorted cells
    # Use scanpy to extract these cells
    X_gt = adata[gt_indices, keep_global].X
    if not issparse(X_gt):
        X_gt = csr_matrix(X_gt)
    elif X_gt.format != 'csr':
        X_gt = X_gt.tocsr()
    print(f"  GT: {X_gt.shape}, nnz={X_gt.nnz}, per_cell={X_gt.nnz/100:.1f}")

adata.file.close()
print("\nDebug complete.")
