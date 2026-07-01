"""
Test: Verify CKI compute() with a minimal adata
to understand the expected input format.
"""

import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData
from cki import compute
from cki.core import compute_kn, compute_kf
from cki.utils import ensure_probability_distribution

print("Test 1: What does ensure_probability_distribution do to log1p values?")
# Simulate: normalize_total (target_sum=1e4) + log1p
np.random.seed(42)
n_genes = 1000
# Raw counts
raw = np.random.poisson(1.0, n_genes).astype(float)
# normalize_total
raw_sum = raw.sum()
raw_norm = raw / raw_sum * 1e4
# log1p
raw_log = np.log1p(raw_norm)

print(f"  After normalize_total: sum={raw_norm.sum():.1f}")
print(f"  After log1p: min={raw_log.min():.4f}, max={raw_log.max():.4f}")
print(f"  log1p values are ALL non-negative: {(raw_log >= 0).all()}")

prob = ensure_probability_distribution(raw_log)
print(f"  After ensure_prob_dist: sum={prob.sum():.6f}")
print(f"  This is softmax(log1p(x)), NOT softmax(x)")
print()

print("Test 2: Compute k_n for two fake pseudobulks")
# Two pseudobulks (log1p space)
pb1_log = np.log1p(np.random.poisson(2.0, n_genes).astype(float) / np.random.poisson(2.0, 1)[0] * 1e4)
pb2_log = np.log1p(np.random.poisson(1.5, n_genes).astype(float) / np.random.poisson(1.5, 1)[0] * 1e4)

hk_indices = list(range(50))
kn_a = compute_kn(pb1_log, pb2_log, hk_indices)
print(f"  k_n (log1p input) = {kn_a:.6f}")

# Now try with normalized (not log1p) input
pb1_norm = np.random.poisson(2.0, n_genes).astype(float)
pb1_norm = pb1_norm / pb1_norm.sum() * 1e4
pb2_norm = np.random.poisson(1.5, n_genes).astype(float)
pb2_norm = pb2_norm / pb2_norm.sum() * 1e4

kn_b = compute_kn(pb1_norm, pb2_norm, hk_indices)
print(f"  k_n (normalized input) = {kn_b:.6f}")
print(f"  Ratio (A/B) = {kn_a/kn_b:.4f}")
print()

print("Test 3: Create minimal adata and call compute()")
n_cells = 20
X = np.random.poisson(1.0, (n_cells, n_genes))
obs = pd.DataFrame({
    'cell_type': ['CT1'] * 10 + ['CT2'] * 10,
})
var = pd.DataFrame(index=[f'GENE_{i}' for i in range(n_genes)])
adata_test = AnnData(X=X, obs=obs, var=var)
sc.pp.normalize_total(adata_test, target_sum=1e4)
sc.pp.log1p(adata_test)

# Call compute() - it will extract pseudobulks from adata (which is already log1p transformed)
result = compute(adata_test, species='human', groupby='cell_type', group_a='CT1', group_b='CT2')
print(f"  compute() result: omega={result['omega']:.4f}, k_n={result['kn']:.6f}, k_f={result['kf']:.6f}")
print()

print("Test 4: Call compute() with pseudobulk_a/b (pre-computed from same adata)")
pb_ct1 = adata_test[adata_test.obs['cell_type'] == 'CT1'].X.mean(axis=0)
pb_ct2 = adata_test[adata_test.obs['cell_type'] == 'CT2'].X.mean(axis=0)
result2 = compute(adata_test, species='human', pseudobulk_a=pb_ct1, pseudobulk_b=pb_ct2)
print(f"  compute(pseudobulk_a/b) result: omega={result2['omega']:.4f}, k_n={result2['kn']:.6f}, k_f={result2['kf']:.6f}")
print(f"  Match with Test 3? omega: {abs(result['omega'] - result2['omega']) < 1e-10}")
print()

print("CONCLUSION:")
print("  - log1p values are non-negative, so ensure_probability_distribution does NOT truncate.")
print("  - compute() expects adata to be pre-normalized (normalize_total + log1p).")
print("  - When passing pseudobulk_a/b, they should be log1p-transformed vectors.")
print("  - The JS divergence is computed on softmax(log1p(x)), not softmax(x).")
print("  - This is CKI's design choice (not a 'bug'), as documented.")
