"""Quick check of Siletti Nonneurons.h5ad structure"""
import scanpy as sc
import sys

path = r"C:\Users\KnightZ\Desktop\细胞受选择\data\brain\Nonneurons.h5ad"
print(f"Loading {path}...")
adata = sc.read_h5ad(path)
print(f"Shape: {adata.shape}")
print(f"n_obs: {adata.n_obs}, n_vars: {adata.n_vars}")
print()

print("obs columns:", list(adata.obs.columns))
print()

# Check key columns
for col in adata.obs.columns:
    n_unique = adata.obs[col].nunique()
    dtype = adata.obs[col].dtype
    if n_unique <= 200:
        vals = sorted(adata.obs[col].dropna().unique())
        print(f"  {col} ({dtype}): n={n_unique}")
        for v in vals[:30]:
            print(f"    - {v}")
        if len(vals) > 30:
            print(f"    ... and {len(vals)-30} more")
    else:
        print(f"  {col} ({dtype}): n={n_unique}")
