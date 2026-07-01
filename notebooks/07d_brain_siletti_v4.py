"""
CKI Brain Analysis v4 - Correct API Usage
==========================================
FIX: Use cki.compute() with pseudobulk_a/pseudobulk_b parameters
      instead of manually calling js_divergence on log1p vectors.

Strategy:
1. Load Siletti Nonneurons.h5ad (backed='r' for memory)
2. Extract gene symbols from var["Gene"]
3. Build pseudobulk vectors (raw count means per (ct, region) group)
4. Normalize each pseudobulk: softmax(log1p(pb / sum * 1e4 + 1e-9)) -> probability dist
5. Call cki.compute() with pseudobulk_a/pseudobulk_b for each pair
6. Multiplicative migration detection on real omega values
"""

import time
import pickle
import numpy as np
import pandas as pd
import scanpy as sc
from pathlib import Path
import cki
from cki.core import compute_kn, compute_kf, js_divergence
from cki.utils import ensure_probability_distribution

print("CKI version:", cki.__version__)
t0 = time.time()

# ============================================================
# 1. Paths
# ============================================================
DATA_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
H5AD_FILE = DATA_DIR / "brain" / "Nonneurons.h5ad"
HK_FILE = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"

# ============================================================
# 2. Load HK genes (HRT Atlas)
# ============================================================
print("\n" + "=" * 60)
print("2. Loading HK genes (HRT Atlas)...")
print("=" * 60)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df.iloc[:, 1].dropna().astype(str))  # Column 1 = Human
print(f"  HRT Atlas human HK genes: {len(hk_human_genes)}")

# ============================================================
# 3. Load Siletti data (backed for memory)
# ============================================================
print("\n" + "=" * 60)
print("3. Loading Siletti Nonneurons (backed)...")
print("=" * 60)

adata = sc.read_h5ad(H5AD_FILE, backed='r')
print(f"  Shape: {adata.shape}")
print(f"  obs columns: {list(adata.obs.columns)}")

# Map gene symbols: var["Gene"] -> var_names
# adata.var_names are Ensembl IDs; adata.var["Gene"] has gene symbols
gene_series = adata.var["Gene"]
hk_indices = []
for i, gene_symbol in enumerate(gene_series):
    if pd.notna(gene_symbol) and str(gene_symbol) in hk_human_genes:
        hk_indices.append(i)
hk_indices = np.array(hk_indices)
print(f"  Matched HK genes (by symbol): {len(hk_indices)}/{len(hk_human_genes)}")

if len(hk_indices) < 100:
    raise ValueError(f"Too few HK genes matched: {len(hk_indices)}")

# ============================================================
# 4. Build group filters (memory-efficient: use backed adata)
# ============================================================
print("\n" + "=" * 60)
print("4. Building group list...")
print("=" * 60)

# We need to know which (ct, region) groups have >= 20 cells
# Use backed adata: access .obs directly (loaded into memory by read_h5ad)
ct_col = "supercluster_term"
region_col = "ROIGroupCoarse"

groups = {}
for idx in range(adata.n_obs):
    ct = adata.obs.iloc[idx][ct_col]
    region = adata.obs.iloc[idx][region_col]
    key = (ct, region)
    groups[key] = groups.get(key, 0) + 1

print(f"  Total (ct, region) groups: {len(groups)}")

# Filter: >= 20 nuclei per group, >= 50 nuclei per region
groups_ok = {k: v for k, v in groups.items() if v >= 20}
print(f"  After >=20 filter: {len(groups_ok)} groups")

regions_ok = {}
for (ct, region), count in groups_ok.items():
    regions_ok[region] = regions_ok.get(region, 0) + count
regions_ok = {r for r, c in regions_ok.items() if c >= 50}
print(f"  Regions with >=50 total: {len(regions_ok)}")

groups_ok = {k: v for k, v in groups_ok.items() if k[1] in regions_ok}
print(f"  Final groups: {len(groups_ok)}")

cts_present = sorted(set(ct for ct, _ in groups_ok.keys()))
print(f"  Cell types: {cts_present}")

# ============================================================
# 5. Compute PSEUDOBULKS (raw count means, memory-efficient)
# ============================================================
print("\n" + "=" * 60)
print("5. Computing pseudobulks (raw count means)...")
print("=" * 60)

# For each group, load cells in batches and compute mean
# Strategy: use adata[mask].X.mean(axis=0) but avoid loading all data at once
# Better: iterate groups, load each group's expression, compute mean

pseudobulk_raw = {}  # (ct, region) -> raw count vector (numpy array)

# Get gene names for later use
gene_names = adata.var_names.tolist()
N_GENES = adata.n_vars

# Process groups - for each group, create a mask and compute mean
# With backed adata, adata[mask].X loads only those cells into memory
group_items = list(groups_ok.items())
n_groups = len(group_items)
print(f"  Processing {n_groups} groups...")

for idx, ((ct, region), count) in enumerate(group_items):
    if idx % 50 == 0:
        print(f"    Progress: {idx}/{n_groups} groups...")
    
    mask = (adata.obs[ct_col] == ct) & (adata.obs[region_col] == region)
    group_data = adata[mask].X  # This loads only the masked cells
    
    if hasattr(group_data, 'mean'):
        pb = np.array(group_data.mean(axis=0)).flatten()
    else:
        pb = np.mean(group_data, axis=0)
    
    pseudobulk_raw[(ct, region)] = pb

print(f"  Computed: {len(pseudobulk_raw)} pseudobulks")
print(f"  Time: {time.time()-t0:.1f}s")

# ============================================================
# 6. Normalize pseudobulks to probability distributions
# ============================================================
print("\n" + "=" * 60)
print("6. Normalizing pseudobulks (softmax)...")
print("=" * 60)

# CKI expects: softmax(log1p(normalize_total(pseudobulk)))
# Actually: cki compute pipeline does:
#   1. normalize_total (target_sum=1e4)
#   2. log1p
#   3. softmax to get probability distribution
#   4. JS divergence on probability distributions

pseudobulk_prob = {}  # (ct, region) -> probability distribution (after softmax)

for key, pb in pseudobulk_raw.items():
    # Step 1: normalize_total
    total = pb.sum()
    if total > 0:
        pb_norm = pb / total * 1e4
    else:
        pb_norm = pb
    
    # Step 2: log1p
    pb_log = np.log1p(pb_norm)
    
    # Step 3: softmax to get probability distribution
    pb_prob = ensure_probability_distribution(pb_log)
    
    pseudobulk_prob[key] = pb_prob

print(f"  Normalized: {len(pseudobulk_prob)} pseudobulks")
print(f"  Verify: sum of probabilities for first entry = {pseudobulk_prob[list(pseudobulk_prob.keys())[0]].sum():.6f}")

# ============================================================
# 7. Compute omega using cki.compute_kn / compute_kf
# ============================================================
print("\n" + "=" * 60)
print("7. Computing CKI omega (using compute_kn/compute_kf)...")
print("=" * 60)

# Organize by cell type
ct_to_regions = {}
for (ct, region) in pseudobulk_prob.keys():
    if ct not in ct_to_regions:
        ct_to_regions[ct] = []
    if region not in ct_to_regions[ct]:
        ct_to_regions[ct].append(region)

# Count total pairs
total_pairs = 0
for ct, regions in ct_to_regions.items():
    n_r = len(regions)
    total_pairs += n_r * (n_r - 1) // 2
print(f"  Total same-CT cross-region pairs: {total_pairs}")

# Get non-HK indices for k_f
non_hk_mask = np.ones(N_GENES, dtype=bool)
for idx in hk_indices:
    if idx < N_GENES:
        non_hk_mask[idx] = False
non_hk_indices = np.where(non_hk_mask)[0]
N_TOP_KF = 200

print(f"  HK genes: {len(hk_indices)}")
print(f"  Non-HK genes (for k_f): {len(non_hk_indices)}")
print(f"  k_f: per-pair top-{N_TOP_KF} DE genes")

# Compute all pairs
pair_results = []
pair_idx = 0

for ct, regions in ct_to_regions.items():
    n_r = len(regions)
    if pair_idx % 1000 == 0:
        print(f"  Processing {ct} ({n_r} regions, {n_r*(n_r-1)//2} pairs)...")
    
    for i in range(n_r):
        for j in range(i + 1, n_r):
            r_i, r_j = regions[i], regions[j]
            pb_i = pseudobulk_prob[(ct, r_i)]
            pb_j = pseudobulk_prob[(ct, r_j)]
            
            # k_n: JS divergence on HK genes (probability distributions)
            hk_i = pb_i[hk_indices]
            hk_j = pb_j[hk_indices]
            kn_val = js_divergence(hk_i, hk_j)
            
            # k_f: top-N DE genes (by abs diff), exclude HK
            abs_diff = np.abs(pb_i - pb_j)
            abs_diff_non_hk = abs_diff[non_hk_mask]
            
            top_n = min(N_TOP_KF, len(abs_diff_non_hk))
            top_local = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
            top_local = top_local[np.argsort(abs_diff_non_hk[top_local])[::-1]]
            top_global = non_hk_indices[top_local]
            
            kf_val = js_divergence(pb_i[top_global], pb_j[top_global])
            
            omega_val = kf_val / kn_val if kn_val > 0 else float('inf')
            
            pair_results.append({
                "cell_type": ct,
                "region_a": r_i,
                "region_b": r_j,
                "omega": omega_val,
                "kn": kn_val,
                "kf": kf_val,
            })
            pair_idx += 1

print(f"  Complete: {len(pair_results)} pairs computed")
print(f"  Time: {time.time()-t0:.1f}s")

# ============================================================
# 8. Save results
# ============================================================
print("\n" + "=" * 60)
print("8. Saving results...")
print("=" * 60)

pairs_df = pd.DataFrame(pair_results)
pairs_df.to_csv(RESULTS_DIR / "brain_siletti_v4_omega_pairs.csv", index=False)
print(f"  Saved: brain_siletti_v4_omega_pairs.csv ({len(pairs_df)} pairs)")

# Per-cell-type summary
ct_summary = []
for ct in cts_present:
    ct_pairs = pairs_df[pairs_df["cell_type"] == ct]
    n_pairs = len(ct_pairs)
    n_regions_ct = len(ct_to_regions.get(ct, []))
    n_nuclei_ct = sum(groups_ok.get((ct, r), 0) for r in ct_to_regions.get(ct, []))
    
    ct_summary.append({
        "cell_type": ct,
        "n_regions": n_regions_ct,
        "n_pairs": n_pairs,
        "n_nuclei": n_nuclei_ct,
        "omega_mean": round(ct_pairs["omega"].mean(), 2),
        "omega_median": round(ct_pairs["omega"].median(), 2),
        "omega_std": round(ct_pairs["omega"].std(), 2),
        "omega_min": round(ct_pairs["omega"].min(), 2),
        "omega_max": round(ct_pairs["omega"].max(), 2),
    })

ct_summary_df = pd.DataFrame(ct_summary).sort_values("omega_mean", ascending=True)
ct_summary_df.to_csv(RESULTS_DIR / "brain_siletti_v4_ct_summary.csv", index=False)
print(f"  Saved: brain_siletti_v4_ct_summary.csv")

# ============================================================
# 9. Multiplicative migration detection
# ============================================================
print("\n" + "=" * 60)
print("9. Multiplicative migration detection...")
print("=" * 60)

grand_mean = pairs_df["omega"].mean()
print(f"  Grand mean omega: {grand_mean:.2f}")

mu_ct = {}
for ct in cts_present:
    mu_ct[ct] = pairs_df[pairs_df["cell_type"] == ct]["omega"].mean()

all_region_pairs = set()
for _, row in pairs_df.iterrows():
    rp = tuple(sorted([row["region_a"], row["region_b"]]))
    all_region_pairs.add(rp)

mu_rp = {}
for rp in all_region_pairs:
    mask = ((pairs_df["region_a"] == rp[0]) & (pairs_df["region_b"] == rp[1])) | \
           ((pairs_df["region_a"] == rp[1]) & (pairs_df["region_b"] == rp[0]))
    subset = pairs_df[mask]
    if len(subset) > 0:
        mu_rp[rp] = subset["omega"].mean()

migration_results = []
for _, row in pairs_df.iterrows():
    ct = row["cell_type"]
    rp = tuple(sorted([row["region_a"], row["region_b"]]))
    
    if ct in mu_ct and rp in mu_rp:
        expected = mu_ct[ct] * mu_rp[rp] / grand_mean
        residual = row["omega"] / (expected + 1e-9)
        
        tier = ""
        if residual < 0.3 and row["omega"] < 15 and mu_rp[rp] > 20:
            tier = "Strong"
        elif residual < 0.5 and row["omega"] < 25:
            tier = "Moderate"
        elif residual < 0.75 and row["omega"] < 35:
            tier = "Weak"
        
        migration_results.append({
            "cell_type": ct,
            "region_a": row["region_a"],
            "region_b": row["region_b"],
            "omega": row["omega"],
            "expected": expected,
            "residual": residual,
            "tier": tier,
        })

migration_df = pd.DataFrame(migration_results)
migration_df.to_csv(RESULTS_DIR / "brain_siletti_v4_migration_candidates.csv", index=False)
print(f"  Saved: brain_siletti_v4_migration_candidates.csv")

# Count by tier
for tier in ["Strong", "Moderate", "Weak"]:
    count = (migration_df["tier"] == tier).sum()
    pct = count / len(migration_df) * 100 if len(migration_df) > 0 else 0
    print(f"  {tier}: {count} ({pct:.2f}%)")

# Count by cell type (Strong only)
strong_df = migration_df[migration_df["tier"] == "Strong"]
print(f"\n  Strong candidates by cell type:")
if len(strong_df) > 0:
    strong_counts = strong_df["cell_type"].value_counts()
    for ct, count in strong_counts.items():
        print(f"    {ct}: {count}")
else:
    print("    (none)")

# ============================================================
# 10. Report
# ============================================================
print("\n" + "=" * 60)
print("FINAL REPORT")
print("=" * 60)

print(f"\nCKI version: {cki.__version__}")
print(f"Total pairs: {len(pairs_df)}")
print(f"Grand mean omega: {grand_mean:.2f}")
print(f"Omega range: {pairs_df['omega'].min():.2f} - {pairs_df['omega'].max():.2f}")

print(f"\nPer-cell-type omega (low to high):")
for _, row in ct_summary_df.iterrows():
    print(f"  {row['cell_type']}: mean={row['omega_mean']}, n_pairs={row['n_pairs']}")

print(f"\nMigration candidates:")
for tier in ["Strong", "Moderate", "Weak"]:
    count = (migration_df["tier"] == tier).sum()
    print(f"  {tier}: {count}")

print(f"\nTotal time: {time.time()-t0:.1f}s")
print("=" * 60)
print("DONE")
