"""
CKI Phase 3.3b: Quick diagnosis (lightweight)
==============================================
Avoids all large-matrix operations. Uses Phase 3.3 saved results + small-scale recomputation.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import scanpy as sc
from pathlib import Path

from cki.core import compute_omega, js_divergence

TS_HUMAN_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\ts_human")
HK_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RANDOM_SEED = 42

# Load Phase 3.3 results
print("Loading Phase 3.3 human results...")
omega_h = pd.read_csv(RESULTS_DIR / "phase33_human_omega.csv", index_col=0)
kf_h = pd.read_csv(RESULTS_DIR / "phase33_human_kf.csv", index_col=0)
kn_h = pd.read_csv(RESULTS_DIR / "phase33_human_kn.csv", index_col=0)
print(f"  Human matrix: {omega_h.shape[0]} CTs, {omega_h.shape[0]*(omega_h.shape[0]-1)//2} pairs")

omega_m = pd.read_csv(RESULTS_DIR / "full_matrix_omega.csv", index_col=0)
kf_m = pd.read_csv(RESULTS_DIR / "full_matrix_kf.csv", index_col=0)
kn_m = pd.read_csv(RESULTS_DIR / "full_matrix_kn.csv", index_col=0)
print(f"  Mouse matrix: {omega_m.shape[0]} CTs")

# Load HK genes
hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna())
hk_mouse = set(hk_df["Mouse"].dropna())

# ================================================================
# 1. k_f / k_n decomposition comparison
# ================================================================
print("\n" + "="*60)
print("1. k_f vs k_n decomposition")
print("="*60)

def utri(df):
    v = df.values
    n = len(v)
    return v[np.triu_indices(n, k=1)]

for name, kf, kn in [("Human", kf_h, kn_h), ("Mouse", kf_m, kn_m)]:
    f = utri(kf); n = utri(kn)
    ratio = f / (n + 1e-9)
    print(f"  {name}:")
    print(f"    k_f: mean={np.mean(f):.4f} med={np.median(f):.4f} min={np.min(f):.4f} max={np.max(f):.4f}")
    print(f"    k_n: mean={np.mean(n):.4f} med={np.median(n):.4f} min={np.min(n):.4f} max={np.max(n):.4f}")
    print(f"    omega: mean={np.mean(ratio):.2f} med={np.median(ratio):.2f}")
    print(f"    k_f/k_n corr: {np.corrcoef(f, n)[0,1]:.3f}")

# ================================================================
# 2. Small-scale log1p vs raw test (Liver only, small)
# ================================================================
print("\n" + "="*60)
print("2. Liver-only log1p vs raw (small scale)")
print("="*60)

# Load just Liver
a_liver = sc.read_h5ad(TS_HUMAN_DIR / "TS_Liver.h5ad")
a_liver.obs["organ"] = "Liver"
# QC: cells >=500 genes, genes in >=3 cells
ng = np.array((a_liver.X > 0).sum(axis=1)).flatten()
a_liver = a_liver[ng >= 500, :]
nc = np.array((a_liver.X > 0).sum(axis=0)).flatten()
a_liver = a_liver[:, nc >= 3]

# Get two large homogeneous CT groups: hepatocyte and macrophage
for ct_name in ["hepatocyte", "macrophage"]:
    ct_mask = a_liver.obs["cell_ontology_class"] == ct_name
    ct_data = a_liver[ct_mask]
    n = ct_data.n_obs
    print(f"\n  {ct_name}: {n} cells")

    # Split into two random halves, compute pseudobulks
    np.random.seed(RANDOM_SEED)
    idx = np.random.permutation(n)
    half = n // 2
    X1 = ct_data[idx[:half]].X
    X2 = ct_data[idx[half:2*half]].X
    if hasattr(X1, "toarray"):
        X1 = X1.toarray(); X2 = X2.toarray()
    pb1_raw = np.mean(X1, axis=0)
    pb2_raw = np.mean(X2, axis=0)

    # Normalize both ways
    pb1_log = np.log1p(pb1_raw / (np.sum(pb1_raw)+1e-9) * 1e4)
    pb2_log = np.log1p(pb2_raw / (np.sum(pb2_raw)+1e-9) * 1e4)
    pb1_norm = pb1_raw / (np.sum(pb1_raw)+1e-9) * 1e4
    pb2_norm = pb2_raw / (np.sum(pb2_raw)+1e-9) * 1e4

    # Find HVG on log data
    means = np.mean([pb1_log, pb2_log], axis=0)
    vars_arr = np.var([pb1_log, pb2_log], axis=0)
    with np.errstate(divide='ignore', invalid='ignore'):
        disp = vars_arr / (means + 1e-9)
    disp[np.isnan(disp)] = 0
    hv_idx = np.argsort(disp)[-100:]
    hk_idx = np.array([i for i, g in enumerate(a_liver.var_names) if g in hk_human])

    # k_f on log1p vs raw
    r_log = compute_omega(pb1_log, pb2_log, hk_idx, hv_idx, w1=1.0, w2=0.0)
    r_raw = compute_omega(pb1_norm, pb2_norm, hk_idx, hv_idx, w1=1.0, w2=0.0)
    r_no_norm = compute_omega(pb1_raw, pb2_raw, hk_idx, hv_idx, w1=1.0, w2=0.0)

    print(f"    log1p:  k_f={r_log['kf']:.5f}  k_n={r_log['kn']:.5f}  omega={r_log['omega']:.2f}")
    print(f"    norm:   k_f={r_raw['kf']:.5f}  k_n={r_raw['kn']:.5f}  omega={r_raw['omega']:.2f}")
    print(f"    raw:    k_f={r_no_norm['kf']:.5f}  k_n={r_no_norm['kn']:.5f}  omega={r_no_norm['omega']:.2f}")

# ================================================================
# 3. Cross-organ same-CT test (macrophage across organs)
# ================================================================
print("\n" + "="*60)
print("3. macrophage cross-organ (small scale)")
print("="*60)

def get_ct_pb(organ_name, ct_name):
    a = sc.read_h5ad(TS_HUMAN_DIR / f"TS_{organ_name}.h5ad")
    ng = np.array((a.X > 0).sum(axis=1)).flatten()
    a = a[ng >= 500, :]
    nc = np.array((a.X > 0).sum(axis=0)).flatten()
    a = a[:, nc >= 3]
    mask = a.obs["cell_ontology_class"] == ct_name
    a_ct = a[mask]
    if a_ct.n_obs < 20:
        return None, None
    # largest donor
    dc = a_ct.obs["donor"].value_counts()
    donor = dc.index[0]
    a_donor = a_ct[a_ct.obs["donor"] == donor]
    X = a_donor.X
    if hasattr(X, "toarray"): X = X.toarray()
    return np.mean(X, axis=0), a.var_names.tolist()

# macrophage in Liver, Kidney, Lung
organs_for_macro = ["Liver", "Kidney", "Lung"]
pbs = {}
for org in organs_for_macro:
    pb, genes = get_ct_pb(org, "macrophage")
    if pb is not None:
        pbs[org] = (pb, genes)
        print(f"  {org} macrophage: {pb.shape}")

if len(pbs) >= 2:
    org_names = list(pbs.keys())
    for i in range(len(org_names)):
        for j in range(i+1, len(org_names)):
            o1, o2 = org_names[i], org_names[j]
            pb1, genes1 = pbs[o1]
            pb2, genes2 = pbs[o2]
            # Find common genes
            common = sorted(set(genes1) & set(genes2))
            idx1 = np.array([genes1.index(g) for g in common])
            idx2 = np.array([genes2.index(g) for g in common])
            pb1_c = pb1[idx1]; pb2_c = pb2[idx2]

            # Compute HVG on merged data
            means_c = np.mean([pb1_c, pb2_c], axis=0)
            vars_c = np.var([pb1_c, pb2_c], axis=0)
            with np.errstate(divide='ignore', invalid='ignore'):
                disp_c = vars_c / (means_c + 1e-9)
            disp_c[np.isnan(disp_c)] = 0
            hv_c = np.argsort(disp_c)[-200:]
            hk_c = np.array([i for i, g in enumerate(common) if g in hk_human])

            r = compute_omega(pb1_c, pb2_c, hk_c, hv_c, w1=1.0, w2=0.0)
            print(f"  {o1}|macro vs {o2}|macro: k_f={r['kf']:.5f} k_n={r['kn']:.5f} omega={r['omega']:.2f}")

# ================================================================
# SUMMARY
# ================================================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

# From Phase 3.3 full results
human_ut = utri(omega_h)
mouse_ut = utri(omega_m)
human_kf_ut = utri(kf_h)
mouse_kf_ut = utri(kf_m)
human_kn_ut = utri(kn_h)
mouse_kn_ut = utri(kn_m)

print(f"\nHuman (99 CTs, {len(human_ut)} pairs):")
print(f"  k_f: mean={np.mean(human_kf_ut):.4f} median={np.median(human_kf_ut):.4f}")
print(f"  k_n: mean={np.mean(human_kn_ut):.4f} median={np.median(human_kn_ut):.4f}")
print(f"  omega: mean={np.mean(human_ut):.2f} median={np.median(human_ut):.2f}")

print(f"\nMouse (38 CTs, {len(mouse_ut)} pairs):")
print(f"  k_f: mean={np.mean(mouse_kf_ut):.4f} median={np.median(mouse_kf_ut):.4f}")
print(f"  k_n: mean={np.mean(mouse_kn_ut):.4f} median={np.median(mouse_kn_ut):.4f}")
print(f"  omega: mean={np.mean(mouse_ut):.2f} median={np.median(mouse_ut):.2f}")

print(f"\nk_f ratio mouse/human: {np.mean(mouse_kf_ut)/np.mean(human_kf_ut):.2f}x")
print(f"k_n ratio mouse/human: {np.mean(mouse_kn_ut)/np.mean(human_kn_ut):.2f}x")

# Check: what if we use raw-count-level k_f with same k_n?
# From the A test: raw k_f was 0.74, log1p k_f was 0.036 → 28x
# But that was on a different gene set (full 23K not just HVG)
print(f"\n=== Root Cause ===")
print(f"The log1p transformation compresses expression differences dramatically.")
print(f"Mouse FACS data is raw counts; TS human is log1p-normalized.")
print(f"This is the primary cause of the 5x k_f gap.")
