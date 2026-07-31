"""
Quick smoke test for brain bootstrap v3 (B=20).
Verifies: backed='r' loading, HVG selection, CSR extraction, permutation logic.
Tests on the SMALLEST cell type first to verify correctness quickly.
"""

import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse
from scipy.sparse import issparse, csr_matrix
from cki.core import js_divergence

N_BOOTSTRAP = 20
RANDOM_SEED = 42
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000

SILETTI_PATH = BRAIN_FILE
HK_FILE_REF = HK_FILE
ct_col = "supercluster_term"
region_col = "roi"

print("=" * 60)
print("BRAIN BOOTSTRAP V3 SMOKE TEST (B=20)")
print("=" * 60)

# 1. HK genes
print("\n1. Loading HK genes...")
hk_df = pd.read_csv(HK_FILE_REF, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"  HK genes: {len(hk_human)}")

# 2. Open in backed='r'
print("\n2. Opening Siletti Nonneurons.h5ad (backed='r')...")
t0 = time.time()
adata = sc.read_h5ad(SILETTI_PATH, backed='r')
print(f"  Shape: {adata.shape} (backed, {time.time()-t0:.0f}s)")
print(f"  X type: {type(adata.X)}")

gene_symbols = adata.var["Gene"].tolist()
hk_global = np.array(sorted(set(
    i for i, sym in enumerate(gene_symbols) if pd.notna(sym) and sym in hk_human
)), dtype=int)
N_GENES = adata.n_vars
print(f"  Matched HK: {len(hk_global)}")

# 3. Compute global HVG (batch-based, backed CSR has no .mean())
print(f"\n3. Computing global gene means for HVG selection...")
t0 = time.time()
N_CELLS = adata.n_obs
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
print(f"  Computed in {time.time()-t0:.0f}s")

non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_global] = False
non_hk_means = gene_means.copy()
non_hk_means[~non_hk_mask] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]

keep_global = np.sort(np.union1d(hk_global, hvg_global))
N_KEEP = len(keep_global)
print(f"  Reduced gene set: {N_KEEP} genes")

is_hk_in_keep = np.isin(keep_global, hk_global)
hk_in_reduced = np.where(is_hk_in_keep)[0]
non_hk_in_reduced = np.where(~is_hk_in_keep)[0]

# 4. Filter groups
print("\n4. Filtering groups...")
groups = adata.obs.groupby([region_col, ct_col]).size().reset_index(name="count")
groups_ok = groups[groups["count"] >= MIN_NUCLEI]
region_counts = adata.obs[region_col].value_counts()
regions_ok = region_counts[region_counts >= MIN_REGION_N].index
groups_ok = groups_ok[groups_ok[region_col].isin(regions_ok)]
cts_present = sorted(groups_ok[ct_col].unique())

ct_to_regions = {}
for _, row in groups_ok.iterrows():
    ct = row[ct_col]; r = row[region_col]
    ct_to_regions.setdefault(ct, [])
    if r not in ct_to_regions[ct]:
        ct_to_regions[ct].append(r)

# 5. Pick the SMALLEST cell type with >= 3 regions (fastest test)
ct_cells_count = {}
for ct in cts_present:
    n = groups_ok[groups_ok[ct_col] == ct]["count"].sum()
    ct_cells_count[ct] = n

test_ct = None
for ct, ncells in sorted(ct_cells_count.items(), key=lambda x: x[1]):
    if len(ct_to_regions[ct]) >= 3:
        test_ct = ct
        break
if test_ct is None:
    test_ct = cts_present[0]

print(f"\n5. Testing on: {test_ct} ({ct_cells_count[test_ct]} cells, "
      f"{len(ct_to_regions[test_ct])} regions)")

regions = ct_to_regions[test_ct]
region_order = sorted(regions)
n_r = len(regions)
n_pairs = n_r * (n_r - 1) // 2
print(f"  {n_r} regions, {n_pairs} pairs")

# 6. Extract cells as CSR (reduced gene set)
print(f"\n6. Extracting cells for {test_ct} (reduced gene set)...")
t0 = time.time()
ct_mask = (adata.obs[ct_col] == test_ct)
X_ct = adata[ct_mask, keep_global].X
if not issparse(X_ct):
    X_ct = csr_matrix(X_ct)
elif X_ct.format != 'csr':
    X_ct = X_ct.tocsr()

n_cells_ct = X_ct.shape[0]
print(f"  Extracted {n_cells_ct} cells x {X_ct.shape[1]} genes "
      f"(CSR, {X_ct.nnz} nnz, {X_ct.nnz/(n_cells_ct*X_ct.shape[1])*100:.1f}% dense, "
      f"~{X_ct.data.nbytes/1e6:.1f}MB data, {time.time()-t0:.0f}s)")

# 7. Sort rows by region for contiguous slices
ct_global_indices = np.where(ct_mask)[0]
region_of_cell = adata.obs[region_col].values[ct_global_indices]
sort_idx = np.argsort(region_of_cell)
sorted_region = region_of_cell[sort_idx]
X_ct = X_ct[sort_idx]

region_sizes = {}
cum = 0
for region in region_order:
    n = int(np.sum(sorted_region == region))
    region_sizes[region] = n
    cum += n
print(f"  Region sizes: {region_sizes}")

# 8. Compute OBSERVED omega
print(f"\n7. Computing observed omega...")

# Pre-compute region row boundaries
region_starts = {}
region_lengths = {}
cum = 0
for r in region_order:
    region_starts[r] = cum
    region_lengths[r] = region_sizes[r]
    cum += region_sizes[r]

obs_omegas = []
for i in range(n_r):
    for j in range(i+1, n_r):
        ri, rj = region_order[i], region_order[j]
        
        # Region i pseudobulk
        si, ei = region_starts[ri], region_starts[ri] + region_lengths[ri]
        pb_i_raw = np.array(X_ct[si:ei].mean(axis=0)).flatten()
        total_i = pb_i_raw.sum()
        pb_i = np.log1p(pb_i_raw / total_i * 1e4) if total_i > 0 else pb_i_raw
        
        # Region j pseudobulk
        sj, ej = region_starts[rj], region_starts[rj] + region_lengths[rj]
        pb_j_raw = np.array(X_ct[sj:ej].mean(axis=0)).flatten()
        total_j = pb_j_raw.sum()
        pb_j = np.log1p(pb_j_raw / total_j * 1e4) if total_j > 0 else pb_j_raw
        
        kn = js_divergence(pb_i[hk_in_reduced], pb_j[hk_in_reduced])
        ad = np.abs(pb_i - pb_j)
        ad_nhk = ad[non_hk_in_reduced]
        top_n = min(N_TOP_KF, len(non_hk_in_reduced))
        top_local = np.argpartition(ad_nhk, -top_n)[-top_n:]
        top_local = top_local[np.argsort(ad_nhk[top_local])[::-1]]
        top_genes = non_hk_in_reduced[top_local]
        kf = js_divergence(pb_i[top_genes], pb_j[top_genes])
        obs_omegas.append(kf/kn if kn > 0 else float('inf'))

obs_mean = np.mean(obs_omegas)
print(f"  Observed: {len(obs_omegas)} pairs, mean_omega={obs_mean:.4f}")
print(f"  Individual omegas: {[f'{o:.2f}' for o in obs_omegas]}")

# 9. Bootstrap: cell-level permutation
print(f"\n8. Bootstrap (B={N_BOOTSTRAP}) — cell-level permutation...")
rng = np.random.RandomState(RANDOM_SEED)
region_cumsum = np.cumsum([0] + [region_sizes[r] for r in region_order])

null_means = []
all_null_omegas = []

t0 = time.time()
for b in range(N_BOOTSTRAP):
    perm = rng.permutation(n_cells_ct)
    
    perm_pbs = {}
    for ri, region in enumerate(region_order):
        start = region_cumsum[ri]
        end = region_cumsum[ri + 1]
        pb_raw = np.array(X_ct[perm[start:end]].mean(axis=0)).flatten()
        total = pb_raw.sum()
        pb_norm = np.log1p(pb_raw / total * 1e4) if total > 0 else pb_raw
        perm_pbs[region] = pb_norm.astype(np.float32)
    
    perm_omegas = []
    for i in range(n_r):
        for j in range(i+1, n_r):
            pb_i = perm_pbs[region_order[i]]
            pb_j = perm_pbs[region_order[j]]
            kn = js_divergence(pb_i[hk_in_reduced], pb_j[hk_in_reduced])
            ad = np.abs(pb_i - pb_j)
            ad_nhk = ad[non_hk_in_reduced]
            top_n = min(N_TOP_KF, len(non_hk_in_reduced))
            top_local = np.argpartition(ad_nhk, -top_n)[-top_n:]
            top_local = top_local[np.argsort(ad_nhk[top_local])[::-1]]
            top_genes = non_hk_in_reduced[top_local]
            kf = js_divergence(pb_i[top_genes], pb_j[top_genes])
            perm_omegas.append(kf/kn if kn > 0 else float('inf'))
    
    null_means.append(np.mean(perm_omegas))
    if b < 3:
        all_null_omegas.append(perm_omegas)

null_means = np.array(null_means)
elapsed = time.time() - t0
print(f"  Done in {elapsed:.0f}s")

# 10. Results
print(f"\n9. RESULTS:")
print(f"  Observed mean omega: {obs_mean:.4f}")
print(f"  Null mean omega:     {np.mean(null_means):.4f} +/- {np.std(null_means):.4f}")
print(f"  Null omega range:    [{np.min(null_means):.4f}, {np.max(null_means):.4f}]")
print(f"  Null values:         {[f'{v:.4f}' for v in null_means]}")

null_mean_val = np.mean(null_means)
null_std_val = np.std(null_means)

obs_dist = abs(obs_mean - 1.0)
null_dists = np.abs(null_means - 1.0)
p_value = (np.sum(null_dists >= obs_dist) + 1) / (len(null_means) + 1)
p_one_sided = (np.sum(null_means >= obs_mean) + 1) / (len(null_means) + 1)

print(f"\n  P-value (two-sided |omega-1|):  {p_value:.4f}")
print(f"  P-value (one-sided >=obs):   {p_one_sided:.4f}")

print(f"\n  DIAGNOSTICS:")
if np.std(null_means) < 1e-6:
    print(f"  FAIL: null distribution has zero variance!")
else:
    print(f"  PASS: null distribution has variance ({null_std_val:.4f})")

if abs(null_mean_val - obs_mean) < null_std_val * 0.1:
    print(f"  WARN: null mean ({null_mean_val:.4f}) very close to obs ({obs_mean:.4f})")
else:
    print(f"  PASS: null mean ({null_mean_val:.4f}) differs from obs ({obs_mean:.4f})")

print(f"\n  First 3 null omega sets:")
for bi, null_omegas in enumerate(all_null_omegas):
    print(f"    Iter {bi}: {[f'{o:.2f}' for o in null_omegas]} (mean={np.mean(null_omegas):.2f})")

# 11. Compare with v2 approach on same CT (sanity check)
print(f"\n10. V2 COMPARISON (full gene set, same CT)...")
t0 = time.time()
# Extract same cells but ALL genes
X_ct_full = adata[ct_mask, :].X
if not issparse(X_ct_full):
    X_ct_full = csr_matrix(X_ct_full)
elif X_ct_full.format != 'csr':
    X_ct_full = X_ct_full.tocsr()
X_ct_full = X_ct_full[sort_idx]
print(f"  Full gene set: {X_ct_full.shape}, "
      f"~{X_ct_full.data.nbytes/1e6:.1f}MB data, loaded in {time.time()-t0:.0f}s")

# Compute observed with full gene set
full_obs_omegas = []
for i in range(n_r):
    for j in range(i+1, n_r):
        ri, rj = region_order[i], region_order[j]
        
        si, ei = region_starts[ri], region_starts[ri] + region_lengths[ri]
        pb_i_raw = np.array(X_ct_full[si:ei].mean(axis=0)).flatten()
        total_i = pb_i_raw.sum()
        pb_i = np.log1p(pb_i_raw / total_i * 1e4) if total_i > 0 else pb_i_raw
        
        sj, ej = region_starts[rj], region_starts[rj] + region_lengths[rj]
        pb_j_raw = np.array(X_ct_full[sj:ej].mean(axis=0)).flatten()
        total_j = pb_j_raw.sum()
        pb_j = np.log1p(pb_j_raw / total_j * 1e4) if total_j > 0 else pb_j_raw
        
        kn = js_divergence(pb_i[hk_global], pb_j[hk_global])
        ad = np.abs(pb_i - pb_j)
        ad[hk_global] = -1
        non_hk_full = np.where(np.ones(N_GENES, dtype=bool) & ~np.isin(np.arange(N_GENES), hk_global))[0]
        top_n = min(N_TOP_KF, len(non_hk_full))
        top = np.argpartition(ad, -top_n)[-top_n:]
        top = top[np.argsort(ad[top])[::-1]]
        top = top[ad[top] >= 0]
        kf = js_divergence(pb_i[top], pb_j[top])
        full_obs_omegas.append(kf/kn if kn > 0 else float('inf'))

full_obs_mean = np.mean(full_obs_omegas)
print(f"  Full gene set obs omega: {full_obs_mean:.4f}")
print(f"  Reduced gene set obs:    {obs_mean:.4f}")
print(f"  Correlation between omega sets: "
      f"{np.corrcoef(obs_omegas, full_obs_omegas)[0,1]:.4f}")

del X_ct_full
gc.collect()

# Close
adata.file.close()

print("\n" + "=" * 60)
print("SMOKE TEST COMPLETE")
print("=" * 60)
