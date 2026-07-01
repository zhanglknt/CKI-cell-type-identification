"""
CKI Bootstrap for Brain (Siletti Nonneurons)
===============================================
Works on PRE-COMPUTED pseudobulks (no need to reload 4.2GB h5ad each time).
Strategy: pre-compute pseudobulks, then bootstrap regional labels.
"""

import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path
from cki.core import compute_omega, js_divergence

# === Config ===
SILETTI_PATH = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\brain\Nonneurons.h5ad")
HK_FILE       = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv")
RESULTS_DIR   = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

N_BOOTSTRAP   = 100
RANDOM_STATE  = 42
MIN_NUCLEI     = 20
MIN_REGION_N    = 50
N_TOP_KF       = 200

ct_col     = "supercluster_term"
region_col = "roi"

# === 1. Load HK genes ===
print("=" * 60)
print("1. Loading HK genes...")
print("=" * 60)

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"  HRT Atlas: {len(hk_human)} human HK genes")

# === 2. Load Siletti data (read-only, no normalization) ===
print("\n" + "=" * 60)
print("2. Loading Siletti Nonneurons.h5ad...")
print("=" * 60)

import scanpy as sc
adata = sc.read_h5ad(SILETTI_PATH)
print(f"  Shape: {adata.shape}")
print(f"  Cell types: {sorted(adata.obs[ct_col].unique())}")
print(f"  Regions: {adata.obs[region_col].nunique()}")

# Map HK genes
gene_symbols = adata.var["Gene"].tolist()
hk_indices = []
for i, sym in enumerate(gene_symbols):
    if pd.notna(sym) and sym in hk_human:
        hk_indices.append(i)
hk_indices = np.array(sorted(set(hk_indices)), dtype=int)
print(f"  Matched HK genes: {len(hk_indices)}")

# === 3. Filter groups ===
print("\n" + "=" * 60)
print("3. Filtering groups...")
print("=" * 60)

groups = adata.obs.groupby([region_col, ct_col]).size().reset_index(name="count")
groups_ok = groups[groups["count"] >= MIN_NUCLEI]
region_counts = adata.obs[region_col].value_counts()
regions_ok = region_counts[region_counts >= MIN_REGION_N].index
groups_ok = groups_ok[groups_ok[region_col].isin(regions_ok)]

print(f"  Groups passing: {len(groups_ok)} (from {len(groups)} total)")

cts_present = sorted(groups_ok[ct_col].unique())
print(f"  Cell types: {len(cts_present)}: {cts_present}")

# === 4. Compute ALL pseudobulks ===
print("\n" + "=" * 60)
print("4. Computing pseudobulks (raw count means)...")
print("=" * 60)

pseudobulk_raw = {}
pseudobulk_meta = []

for _, row in groups_ok.iterrows():
    region = row[region_col]
    ct = row[ct_col]
    key = (ct, region)
    
    mask = (adata.obs[region_col] == region) & (adata.obs[ct_col] == ct)
    X = adata[mask].X
    if hasattr(X, "toarray"):
        pb = np.array(X.mean(axis=0)).flatten()
    else:
        pb = np.mean(X, axis=0)
    
    pseudobulk_raw[key] = pb
    pseudobulk_meta.append({"ct": ct, "region": region, "n": row["count"]})

print(f"  Computed: {len(pseudobulk_raw)} pseudobulks")

# Normalize all pseudobulks
pseudobulk_norm = {}
for key, pb in pseudobulk_raw.items():
    total = pb.sum()
    if total > 0:
        pb_norm = pb / total * 1e4
    else:
        pb_norm = pb
    pb_log = np.log1p(pb_norm)
    pseudobulk_norm[key] = pb_log

print(f"  Normalized: {len(pseudobulk_norm)}")

# Free adata
del adata
import gc
gc.collect()
print("  Freed adata.")

# === 5. Bootstrap for each cell type ===
print("\n" + "=" * 60)
print(f"5. Bootstrap (B={N_BOOTSTRAP}) for each cell type...")
print("=" * 60)

def bootstrap_cell_type(ct, regions, pb_dict, hk_idx, n_bootstrap=100, random_state=42):
    """
    Bootstrap test for one cell type across regions.
    H0: regional omega values are not different from permuted labels.
    Permute: which regions the pseudobulks come from.
    """
    rng = np.random.RandomState(random_state)
    
    # Observed: compute mean omega across all regional pairs
    n_r = len(regions)
    obs_omegas = []
    for i in range(n_r):
        for j in range(i+1, n_r):
            pb_i = pb_dict[(ct, regions[i])]
            pb_j = pb_dict[(ct, regions[j])]
            # k_f: top-N non-HK genes by abs diff
            diff = np.abs(pb_i - pb_j)
            mask = np.ones(len(pb_i), dtype=bool)
            mask[hk_idx] = False
            diff[~mask] = -1
            top = np.argsort(diff)[-N_TOP_KF:]
            top = top[diff[top] >= 0]
            id_idx = np.sort(top).astype(int)
            
            r = compute_omega(pb_i, pb_j, hk_idx.tolist(), id_idx.tolist(), w1=1.0, w2=0.0)
            obs_omegas.append(r["omega"])
    
    obs_mean = np.mean(obs_omegas) if obs_omegas else 0.0
    obs_max = np.max(obs_omegas) if obs_omegas else 0.0
    
    # Bootstrap: permute region labels
    # Build pooled pseudobulks
    all_pbs = [pb_dict[(ct, r)] for r in regions]
    n_total = len(all_pbs)
    
    null_means = []
    for b in range(n_bootstrap):
        perm = rng.permutation(n_total)
        # Recompute omegas with permuted labels
        perm_regions = [regions[i] for i in perm]  # This doesn't change anything...
        # Actually, permuting region labels doesn't change the set of pseudobulks
        # The right permutation: permute which CELLS belong to which region
        # But we've already aggregated to pseudobulk...
        
        # Correct approach: permute the pseudobulk vectors themselves
        perm_pbs = [all_pbs[i] for i in perm]
        perm_omegas = []
        for i in range(n_total):
            for j in range(i+1, n_total):
                pb_i = perm_pbs[i]
                pb_j = perm_pbs[j]
                diff = np.abs(pb_i - pb_j)
                mask = np.ones(len(pb_i), dtype=bool)
                mask[hk_idx] = False
                diff[~mask] = -1
                top = np.argsort(diff)[-N_TOP_KF:]
                top = top[diff[top] >= 0]
                id_idx = np.sort(top).astype(int)
                r = compute_omega(pb_i, pb_j, hk_idx.tolist(), id_idx.tolist(), w1=1.0, w2=0.0)
                perm_omegas.append(r["omega"])
        
        null_means.append(np.mean(perm_omegas))
    
    null_means = np.array(null_means)
    # Two-sided P-value: |null_mean - obs_mean| >= |obs_mean - obs_mean| = 0
    # Actually, the right test is: is obs_mean > null_mean? (one-sided)
    p_value = (np.sum(null_means >= obs_mean) + 1) / (len(null_means) + 1)
    
    return obs_mean, obs_max, obs_omegas, p_value, null_means

# Run for each cell type
all_results = []
ct_to_regions = {}
for meta in pseudobulk_meta:
    ct = meta["ct"]
    r = meta["region"]
    if ct not in ct_to_regions:
        ct_to_regions[ct] = set()
    ct_to_regions[ct].add(r)

for ct in cts_present:
    if ct not in ct_to_regions:
        continue
    regions = sorted(ct_to_regions[ct])
    n_r = len(regions)
    n_pairs = n_r * (n_r - 1) // 2
    
    if n_pairs < 5:
        print(f"  {ct}: SKIP (only {n_pairs} pairs)")
        continue
    
    t0 = time.time()
    print(f"  {ct}: {n_r} regions, {n_pairs} pairs...", end=" ")
    
    try:
        obs_mean, obs_max, obs_omegas, p_val, null_means = bootstrap_cell_type(
            ct, regions, pseudobulk_norm, hk_indices,
            n_bootstrap=N_BOOTSTRAP, random_state=RANDOM_STATE
        )
        elapsed = time.time() - t0
        print(f"mean_omega={obs_mean:.2f}, p={p_val:.4f} ({elapsed:.0f}s)")
        
        all_results.append({
            "cell_type": ct,
            "n_regions": n_r,
            "n_pairs": n_pairs,
            "omega_mean": f"{obs_mean:.4f}",
            "omega_max": f"{obs_max:.4f}",
            "omega_std": f"{np.std(obs_omegas):.4f}",
            "p_value": f"{p_val:.4e}",
            "null_mean": f"{np.mean(null_means):.4f}",
            "null_std": f"{np.std(null_means):.4f}",
        })
    except Exception as e:
        print(f"ERROR: {e}")
        all_results.append({
            "cell_type": ct,
            "error": str(e),
        })

# === 6. Save results ===
print("\n" + "=" * 60)
print("6. Saving results...")
print("=" * 60)

df = pd.DataFrame(all_results)
print("\n" + df.to_string(index=False))
df.to_csv(RESULTS_DIR / "brain_bootstrap_results.csv", index=False)

print("\nDone! Results saved to brain_bootstrap_results.csv")
