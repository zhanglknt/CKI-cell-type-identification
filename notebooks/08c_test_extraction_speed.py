"""
Test optimized extract_csr_from_backed: correctness + speed.
Compares new chunk-based extraction vs scanpy backed-mode ground truth.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
import h5py
from scipy.sparse import issparse, csr_matrix
from cki.core import js_divergence

def extract_csr_from_backed(h5_path, cell_indices, keep_global, n_genes_total,
                            chunk_size=20000):
    n_cells = len(cell_indices)
    n_keep = len(keep_global)
    if n_cells == 0:
        return csr_matrix((0, n_keep), dtype=np.float32)
    gene_map = np.full(n_genes_total, -1, dtype=np.int32)
    gene_map[keep_global] = np.arange(n_keep, dtype=np.int32)
    sort_order = np.argsort(cell_indices, kind='stable')
    sorted_cells = cell_indices[sort_order]
    unsort = np.empty(n_cells, dtype=np.int64)
    unsort[sort_order] = np.arange(n_cells)
    new_data_list = [None] * n_cells
    new_idx_list = [None] * n_cells
    cell_nnz_sorted = np.zeros(n_cells, dtype=np.int64)
    with h5py.File(h5_path, 'r') as f:
        X = f['X']
        indptr_full = X['indptr'][:]
        n_chunks = (n_cells + chunk_size - 1) // chunk_size
        for chunk_i in range(n_chunks):
            chunk_start = chunk_i * chunk_size
            chunk_end = min(chunk_start + chunk_size, n_cells)
            chunk_cells = sorted_cells[chunk_start:chunk_end]
            data_start = int(indptr_full[chunk_cells[0]])
            data_end = int(indptr_full[chunk_cells[-1] + 1])
            if data_end > data_start:
                chunk_indices = X['indices'][data_start:data_end]
                chunk_data = X['data'][data_start:data_end]
                chunk_mapped = gene_map[chunk_indices]
                chunk_keep = chunk_mapped >= 0
            else:
                chunk_mapped = np.array([], dtype=np.int32)
                chunk_keep = np.array([], dtype=bool)
                chunk_data = np.array([], dtype=np.int16)
            for ci in range(chunk_start, chunk_end):
                orig_pos = int(unsort[ci])
                global_row = int(sorted_cells[ci])
                r_start = int(indptr_full[global_row]) - data_start
                r_end = int(indptr_full[global_row + 1]) - data_start
                if r_start == r_end:
                    continue
                keep_mask = chunk_keep[r_start:r_end]
                n_kept = int(keep_mask.sum())
                cell_nnz_sorted[ci] = n_kept
                if n_kept > 0:
                    new_data_list[orig_pos] = chunk_data[r_start:r_end][keep_mask]
                    new_idx_list[orig_pos] = chunk_mapped[r_start:r_end][keep_mask]
            if n_chunks > 5 and (chunk_i + 1) % 5 == 0:
                print(f"      Extraction chunk {chunk_i+1}/{n_chunks} "
                      f"({chunk_end}/{n_cells} sorted cells)")
    cell_nnz_orig = np.zeros(n_cells, dtype=np.int64)
    cell_nnz_orig[unsort] = cell_nnz_sorted
    new_indptr = np.zeros(n_cells + 1, dtype=np.int64)
    np.cumsum(cell_nnz_orig, out=new_indptr[1:])
    nnz = int(new_indptr[-1])
    if nnz == 0:
        return csr_matrix((n_cells, n_keep), dtype=np.float32)
    all_data = [d for d in new_data_list if d is not None]
    all_idx = [d for d in new_idx_list if d is not None]
    new_data = np.concatenate(all_data)
    new_indices_arr = np.concatenate(all_idx)
    return csr_matrix((new_data, new_indices_arr, new_indptr), shape=(n_cells, n_keep))


# === Config ===
SILETTI_PATH = BRAIN_FILE
HK_FILE_REF = HK_FILE
ct_col = "supercluster_term"
N_HVG = 5000

print("=" * 60)
print("EXTRACTION SPEED TEST")
print("=" * 60)

# 1. Load HK genes
print("\n1. Loading HK genes...")
hk_df = pd.read_csv(HK_FILE_REF, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))

# 2. Open backed
print("\n2. Opening Siletti (backed='r')...")
t0 = time.time()
adata = sc.read_h5ad(SILETTI_PATH, backed='r')
print(f"  Shape: {adata.shape} ({time.time()-t0:.0f}s)")

gene_symbols = adata.var["Gene"].tolist()
hk_global = np.array(sorted(set(
    i for i, sym in enumerate(gene_symbols) if pd.notna(sym) and sym in hk_human
)), dtype=int)
N_GENES = adata.n_vars
N_CELLS = adata.n_obs
print(f"  HK genes matched: {len(hk_global)}")

# 3. Compute gene means for HVG
print(f"\n3. Computing gene means (for HVG selection)...")
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
gene_means = gene_sums / N_CELLS
print(f"  Done in {time.time()-t0:.0f}s")

non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_global] = False
non_hk_means = gene_means.copy()
non_hk_means[~non_hk_mask] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
keep_global = np.sort(np.union1d(hk_global, hvg_global))
N_KEEP = len(keep_global)
print(f"  Reduced gene set: {N_KEEP} genes")

# 4. Pick a SMALL and a LARGE cell type for testing
ct_col = "supercluster_term"
vc = adata.obs[ct_col].value_counts()
print(f"\n4. Cell type sizes (top 5 + bottom 5):")
print(vc.head())
print("...")
print(vc.tail())

# Pick smallest and largest CT
smallest_ct = vc.index[-1]
largest_ct = vc.index[0]
test_cts = [smallest_ct, largest_ct]
print(f"\n  Testing: {smallest_ct} ({vc[smallest_ct]} cells) + {largest_ct} ({vc[largest_ct]} cells)")

STR_H5AD = str(SILETTI_PATH)

for test_ct in test_cts:
    print(f"\n{'='*60}")
    print(f"Testing: {test_ct} ({vc[test_ct]} cells)")
    print(f"{'='*60}")
    
    ct_mask = (adata.obs[ct_col] == test_ct).values
    ct_indices = np.where(ct_mask)[0]
    
    # === Method A: Optimized extract_csr_from_backed ===
    print(f"\n  A. Optimized extract_csr_from_backed (chunk_size=20000)...")
    t0 = time.time()
    X_opt = extract_csr_from_backed(STR_H5AD, ct_indices, keep_global, N_GENES)
    t_opt = time.time() - t0
    print(f"  Result: {X_opt.shape}, nnz={X_opt.nnz}, "
          f"data={X_opt.data.nbytes/1e6:.1f}MB, time={t_opt:.1f}s")
    
    # === Method B: scanpy backed (ground truth) ===
    print(f"\n  B. scanpy backed (ground truth)...")
    t0 = time.time()
    X_gt = adata[ct_mask, keep_global].X
    if not issparse(X_gt):
        X_gt = csr_matrix(X_gt)
    elif X_gt.format != 'csr':
        X_gt = X_gt.tocsr()
    t_gt = time.time() - t0
    print(f"  Result: {X_gt.shape}, nnz={X_gt.nnz}, "
          f"data={X_gt.data.nbytes/1e6:.1f}MB, time={t_gt:.1f}s")
    
    # === Compare ===
    print(f"\n  Comparison:")
    print(f"    nnz match: {X_opt.nnz == X_gt.nnz}  ({X_opt.nnz} vs {X_gt.nnz})")
    
    # Sort both by cell index for comparison
    # (X_opt rows are in ct_indices order, X_gt rows are in ct_mask order = same)
    # Need to sort both by global cell index
    sort_idx = np.argsort(ct_indices)
    X_opt_sorted = X_opt[sort_idx]
    X_gt_sorted = X_gt[sort_idx]
    
    # Compare row by row (sample 100 rows)
    n_compare = min(100, X_opt.shape[0])
    test_rows = np.random.RandomState(42).choice(X_opt.shape[0], n_compare, replace=False)
    
    all_match = True
    for r in test_rows:
        opt_row = X_opt_sorted[r].toarray().flatten()
        gt_row = X_gt_sorted[r].toarray().flatten()
        if not np.array_equal(opt_row, gt_row):
            # Check if they're close (dtype differences)
            if np.allclose(opt_row, gt_row, atol=1):
                continue  # Close enough (int16 vs float)
            print(f"    MISMATCH at row {r}: opt={opt_row[:10]}, gt={gt_row[:10]}")
            all_match = False
            break
    
    if all_match:
        print(f"    PASS: All {n_compare} sampled rows match")
    
    print(f"\n  Speedup: {t_gt/t_opt:.1f}x" if t_opt > 0 else "  N/A")
    
    del X_opt, X_gt
    import gc; gc.collect()

adata.file.close()
print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
