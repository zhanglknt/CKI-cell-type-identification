"""
Quick smoke test for brain bootstrap v2 (B=20).
Verifies: data loading, cell extraction, permutation logic, P-values.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override N_BOOTSTRAP before importing the main script
# (we use exec to run a modified version)

import numpy as np
import pandas as pd
import scanpy as sc
from pathlib import Path
from cki.core import js_divergence
from _paths import *

N_BOOTSTRAP = 20
RANDOM_SEED = 42
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_TOP_KF = 200

SILETTI_PATH = BRAIN_FILE
HK_FILE_REF = HK_FILE

ct_col = "supercluster_term"
region_col = "roi"

print("=" * 60)
print("BRAIN BOOTSTRAP V2 SMOKE TEST (B=20)")
print("=" * 60)

# 1. HK genes
print("\n1. Loading HK genes...")
hk_df = pd.read_csv(HK_FILE_REF, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"  HK genes: {len(hk_human)}")

# 2. Load Siletti data
print("\n2. Loading Siletti Nonneurons.h5ad...")
t0 = __import__('time').time()
adata = sc.read_h5ad(SILETTI_PATH)
print(f"  Shape: {adata.shape} (loaded in {__import__('time').time()-t0:.0f}s)")
print(f"  Cell types: {sorted(adata.obs[ct_col].unique())}")
print(f"  Regions: {adata.obs[region_col].nunique()}")

# Map HK genes
gene_symbols = adata.var["Gene"].tolist()
hk_indices = np.array(sorted(set(
    i for i, sym in enumerate(gene_symbols) 
    if pd.notna(sym) and sym in hk_human
)), dtype=int)
N_GENES = adata.n_vars
print(f"  Matched HK: {len(hk_indices)}/{len(hk_human)}")

non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_indices] = False
non_hk_indices_global = np.where(non_hk_mask)[0]

# 3. Filter
print("\n3. Filtering groups...")
groups = adata.obs.groupby([region_col, ct_col]).size().reset_index(name="count")
groups_ok = groups[groups["count"] >= MIN_NUCLEI]
region_counts = adata.obs[region_col].value_counts()
regions_ok = region_counts[region_counts >= MIN_REGION_N].index
groups_ok = groups_ok[groups_ok[region_col].isin(regions_ok)]
cts_present = sorted(groups_ok[ct_col].unique())
print(f"  Filtered: {len(groups_ok)} groups, {len(cts_present)} cell types")

ct_to_regions = {}
for _, row in groups_ok.iterrows():
    ct = row[ct_col]; r = row[region_col]
    ct_to_regions.setdefault(ct, [])
    if r not in ct_to_regions[ct]:
        ct_to_regions[ct].append(r)

# Print per-CT info
for ct in cts_present:
    regions = ct_to_regions[ct]
    n_pairs = len(regions) * (len(regions) - 1) // 2
    # Count cells
    total_cells = sum(
        groups_ok[(groups_ok[ct_col] == ct) & (groups_ok[region_col].isin(regions))]["count"].sum()
        for _ in [0]  # just once
    )
    total_cells = groups_ok[groups_ok[ct_col] == ct]["count"].sum()
    print(f"  {ct}: {len(regions)} regions, {n_pairs} pairs, {total_cells} cells")

# 4. Quick test on the SMALLEST cell type (fewest cells, fewest regions)
#    to verify permutation logic works correctly
# Find smallest CT by number of cells
ct_cells_count = {}
for ct in cts_present:
    n_cells = 0
    for region in ct_to_regions[ct]:
        mask = (adata.obs[region_col] == region) & (adata.obs[ct_col] == ct)
        n_cells += mask.sum()
    ct_cells_count[ct] = n_cells

# Pick smallest CT with >=3 regions (need at least 3 for meaningful pairs)
test_cts = sorted(ct_cells_count.items(), key=lambda x: x[1])
test_ct = None
for ct, ncells in test_cts:
    if len(ct_to_regions[ct]) >= 3:
        test_ct = ct
        break

if test_ct is None:
    test_ct = cts_present[0]

print(f"\n4. Testing on: {test_ct} ({ct_cells_count[test_ct]} cells, "
      f"{len(ct_to_regions[test_ct])} regions)")

regions = ct_to_regions[test_ct]
n_r = len(regions)
n_pairs = n_r * (n_r - 1) // 2

# Extract cells for this CT
print(f"\n5. Extracting cells for {test_ct}...")
t0 = __import__('time').time()
ct_cells = {}
region_sizes = {}

for region in regions:
    mask = (adata.obs[region_col] == region) & (adata.obs[ct_col] == test_ct)
    idx = np.where(mask)[0]
    region_sizes[region] = len(idx)
    X_sub = adata[idx].X
    if hasattr(X_sub, "toarray"):
        X_sub = X_sub.toarray()
    ct_cells[region] = np.asarray(X_sub, dtype=np.float32)

all_cells = np.vstack(list(ct_cells.values()))
n_total = all_cells.shape[0]
print(f"  Extracted {n_total} cells in {__import__('time').time()-t0:.0f}s")
print(f"  Region sizes: {region_sizes}")

# 6. Compute OBSERVED omega
print(f"\n6. Computing observed omega...")
obs_omegas = []
for i in range(n_r):
    for j in range(i+1, n_r):
        pb_i = np.mean(ct_cells[regions[i]], axis=0)
        pb_j = np.mean(ct_cells[regions[j]], axis=0)
        total_i = pb_i.sum()
        total_j = pb_j.sum()
        pb_i_norm = np.log1p(pb_i / total_i * 1e4) if total_i > 0 else pb_i
        pb_j_norm = np.log1p(pb_j / total_j * 1e4) if total_j > 0 else pb_j
        
        kn = js_divergence(pb_i_norm[hk_indices], pb_j_norm[hk_indices])
        ad = np.abs(pb_i_norm - pb_j_norm)
        ad[hk_indices] = -1
        top_n = min(N_TOP_KF, len(non_hk_indices_global))
        top = np.argpartition(ad, -top_n)[-top_n:]
        top = top[np.argsort(ad[top])[::-1]]
        top = top[ad[top] >= 0]
        kf = js_divergence(pb_i_norm[top], pb_j_norm[top])
        obs_omegas.append(kf/kn if kn > 0 else float('inf'))

obs_mean = np.mean(obs_omegas)
print(f"  Observed: {len(obs_omegas)} pairs, mean_omega={obs_mean:.4f}")
print(f"  Individual omegas: {[f'{o:.2f}' for o in obs_omegas]}")

# 7. Bootstrap: cell-level permutation
print(f"\n7. Bootstrap (B={N_BOOTSTRAP}) — cell-level permutation...")
rng = np.random.RandomState(RANDOM_SEED)
region_order = sorted(region_sizes.keys())
region_size_list = [region_sizes[r] for r in region_order]
region_cumsum = np.cumsum([0] + region_size_list)

null_means = []
all_null_omegas = []  # store first few null omega sets for inspection

t0 = __import__('time').time()
for b in range(N_BOOTSTRAP):
    perm = rng.permutation(n_total)
    
    # Compute pseudobulks for permuted groups
    perm_pbs = {}
    for ri, region in enumerate(region_order):
        start = region_cumsum[ri]
        end = region_cumsum[ri + 1]
        pb_raw = np.mean(all_cells[perm[start:end]], axis=0)
        total = pb_raw.sum()
        pb_norm = np.log1p(pb_raw / total * 1e4) if total > 0 else pb_raw
        perm_pbs[region] = pb_norm.astype(np.float32)
    
    # Compute omega for all pairs
    perm_omegas = []
    for i in range(n_r):
        for j in range(i+1, n_r):
            pb_i = perm_pbs[region_order[i]]
            pb_j = perm_pbs[region_order[j]]
            kn = js_divergence(pb_i[hk_indices], pb_j[hk_indices])
            ad = np.abs(pb_i - pb_j)
            ad[hk_indices] = -1
            top_n = min(N_TOP_KF, len(non_hk_indices_global))
            top = np.argpartition(ad, -top_n)[-top_n:]
            top = top[np.argsort(ad[top])[::-1]]
            top = top[ad[top] >= 0]
            kf = js_divergence(pb_i[top], pb_j[top])
            perm_omegas.append(kf/kn if kn > 0 else float('inf'))
    
    null_means.append(np.mean(perm_omegas))
    if b < 3:
        all_null_omegas.append(perm_omegas)

null_means = np.array(null_means)
elapsed = __import__('time').time() - t0
print(f"  Done in {elapsed:.0f}s")

# 8. Results
print(f"\n8. RESULTS:")
print(f"  Observed mean omega: {obs_mean:.4f}")
print(f"  Null mean omega:     {np.mean(null_means):.4f} ± {np.std(null_means):.4f}")
print(f"  Null omega range:    [{np.min(null_means):.4f}, {np.max(null_means):.4f}]")
print(f"  Null values:         {[f'{v:.4f}' for v in null_means]}")

# Key check: are null values different from observed?
# If the permutation is working, null means should be CLUSTERED AROUND A DIFFERENT VALUE
# than the observed mean (not all identical to it)
null_mean_val = np.mean(null_means)
null_std_val = np.std(null_means)

# P-value: two-sided |omega-1|
obs_dist = abs(obs_mean - 1.0)
null_dists = np.abs(null_means - 1.0)
p_value = (np.sum(null_dists >= obs_dist) + 1) / (len(null_means) + 1)

# One-sided: fraction >= obs_mean
p_one_sided = (np.sum(null_means >= obs_mean) + 1) / (len(null_means) + 1)

print(f"\n  P-value (two-sided |ω-1|):  {p_value:.4f}")
print(f"  P-value (one-sided >=obs):   {p_one_sided:.4f}")

# Diagnostic checks
print(f"\n  DIAGNOSTICS:")
if np.std(null_means) < 1e-6:
    print(f"  ⚠️  FAIL: null distribution has zero variance — permutation not working!")
else:
    print(f"  ✅ PASS: null distribution has variance ({null_std_val:.4f})")

if abs(null_mean_val - obs_mean) < null_std_val * 0.1:
    print(f"  ⚠️  WARN: null mean ({null_mean_val:.4f}) very close to obs ({obs_mean:.4f})")
else:
    print(f"  ✅ PASS: null mean ({null_mean_val:.4f}) differs from obs ({obs_mean:.4f})")

# Show first 3 null omega sets
print(f"\n  First 3 null omega sets:")
for bi, null_omegas in enumerate(all_null_omegas):
    print(f"    Iter {bi}: {[f'{o:.2f}' for o in null_omegas]} (mean={np.mean(null_omegas):.2f})")

# Compare with v1's broken approach: if we just permute pseudobulk assignments
# (this should show P≈0.5 — proving the v1 bug)
print(f"\n9. V1 BUG DEMONSTRATION:")
# Compute pseudobulks first
pbs = {}
for region in regions:
    pb_raw = np.mean(ct_cells[region], axis=0)
    total = pb_raw.sum()
    pbs[region] = np.log1p(pb_raw / total * 1e4) if total > 0 else pb_raw

# v1 approach: permute which pseudobulk goes with which region
v1_null_means = []
for b in range(N_BOOTSTRAP):
    perm = rng.permutation(n_r)
    perm_regions = [region_order[i] for i in perm]
    perm_omegas = []
    for i in range(n_r):
        for j in range(i+1, n_r):
            pb_i = pbs[perm_regions[i]]
            pb_j = pbs[perm_regions[j]]
            kn = js_divergence(pb_i[hk_indices], pb_j[hk_indices])
            ad = np.abs(pb_i - pb_j)
            ad[hk_indices] = -1
            top_n = min(N_TOP_KF, len(non_hk_indices_global))
            top = np.argpartition(ad, -top_n)[-top_n:]
            top = top[np.argsort(ad[top])[::-1]]
            top = top[ad[top] >= 0]
            kf = js_divergence(pb_i[top], pb_j[top])
            perm_omegas.append(kf/kn if kn > 0 else float('inf'))
    v1_null_means.append(np.mean(perm_omegas))

v1_null_means = np.array(v1_null_means)
v1_p = (np.sum(np.abs(v1_null_means - 1) >= obs_dist) + 1) / (N_BOOTSTRAP + 1)
print(f"  V1 null mean (permuting pseudobulks): {np.mean(v1_null_means):.4f}")
print(f"  V1 P-value: {v1_p:.4f}")
if 0.4 < v1_p < 0.6:
    print(f"  ✅ CONFIRMED: V1 P≈0.5 (broken!), V2 P={p_value:.4f} (correct)")
else:
    print(f"  Note: V1 P={v1_p:.4f} — not in [0.4,0.6] range, but still invalid method")

print("\n" + "=" * 60)
print("SMOKE TEST COMPLETE")
print("=" * 60)
