"""
Test: Verify CKI compute() input format.
"""
import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData
from cki import compute
from cki.core import compute_kn, compute_kf
from cki.utils import ensure_probability_distribution

print("=== Test 1: ensure_probability_distribution on log1p values ===")
np.random.seed(42)
n = 1000
# Simulate: normalize_total + log1p
raw = np.random.poisson(1.0, n).astype(float)
raw_norm = raw / raw.sum() * 1e4
raw_log = np.log1p(raw_norm)

print(f"  log1p values: min={raw_log.min():.4f}, max={raw_log.max():.4f}")
print(f"  All non-negative? { (raw_log >= 0).all()}")

prob = ensure_probability_distribution(raw_log)
print(f"  After ensure_prob_dist: sum={prob.sum():.6f}")
print(f"  (this is softmax(log1p(x)), not softmax(x))")
print()

print("=== Test 2: compute_kn with log1p input ===")
hk_indices = list(range(50))
# Create two pseudobulk vectors (log1p space)
pb1 = np.log1p(np.random.poisson(2.0, n).astype(float))
pb2 = np.log1p(np.random.poisson(1.5, n).astype(float))
kn_log = compute_kn(pb1, pb2, hk_indices)
print(f"  k_n (log1p input) = {kn_log:.6f}")
print()

print("=== Test 3: compute_kn with normalized input (no log1p) ===")
pb1_norm = np.random.poisson(2.0, n).astype(float)
pb1_norm = pb1_norm / pb1_norm.sum() * 1e4
pb2_norm = np.random.poisson(1.5, n).astype(float)
pb2_norm = pb2_norm / pb2_norm.sum() * 1e4
kn_norm = compute_kn(pb1_norm, pb2_norm, hk_indices)
print(f"  k_n (normalized input) = {kn_norm:.6f}")
print(f"  Ratio (log/norm) = {kn_log/kn_norm:.4f}")
print()

print("=== Test 4: Full adata flow (as CKI docs recommend) ===")
n_cells = 20
X = np.random.poisson(1.0, (n_cells, n)).astype(float)
obs = pd.DataFrame({'cell_type': ['CT1']*10 + ['CT2']*10})
var = pd.DataFrame(index=[f'GENE_{i}' for i in range(n)])
adata = AnnData(X=X, obs=obs, var=var)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

result = compute(adata, species='human', groupby='cell_type', group_a='CT1', group_b='CT2')
print(f"  compute() result: omega={result['omega']:.4f}, k_n={result['kn']:.6f}, k_f={result['kf']:.6f}")
print()

print("=== Test 5: Same adata, extract pseudobulk and call compute(..., pseudobulk_a/b) ===")
pb_ct1 = adata[adata.obs['cell_type'] == 'CT1'].X.mean(axis=0)
pb_ct2 = adata[adata.obs['cell_type'] == 'CT2'].X.mean(axis=0)
result2 = compute(adata, species='human', pseudobulk_a=pb_ct1, pseudobulk_b=pb_ct2)
print(f"  compute(pseudobulk_a/b) result: omega={result2['omega']:.4f}, k_n={result2['kn']:.6f}")
print(f"  Match Test 4? omega diff = {abs(result['omega'] - result2['omega']):.6f}")
print()

print("=== CONCLUSION ===")
print("  CKI compute() expects adata to be pre-normalized (normalize_total + log1p).")
print("  When passing pseudobulk_a/b, they should be log1p-transformed vectors.")
print("  The JS divergence is computed on softmax(log1p(x)), which is a valid")
print("  (though not theoretically perfect) way to measure distributional divergence.")
print("  The absolute scale of omega may differ from a 'perfect' implementation,")
print("  but the RELATIVE rankings and biological conclusions should be consistent.")
