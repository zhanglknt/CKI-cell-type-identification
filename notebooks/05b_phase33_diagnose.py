"""
CKI Phase 3.3b: Diagnose low human k_f (memory-optimized)
==========================================================
Avoids copying the 108K×58K sparse matrix.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import scanpy as sc
from pathlib import Path
from scipy.sparse import csr_matrix, issparse

from cki.core import compute_omega, js_divergence

TS_HUMAN_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\ts_human")
HK_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv")
FACS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\FACS\FACS")
ANNOT_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\annotations_FACS.csv")

TS_ORGANS = ["Liver", "Kidney", "Heart", "Bone_Marrow", "Spleen", "Lung"]
RANDOM_SEED = 42

# ================================================================
# Load data
# ================================================================
print("="*60)
print("Loading data...")
print("="*60)

adatas_ts = {}
for organ in TS_ORGANS:
    a = sc.read_h5ad(TS_HUMAN_DIR / f"TS_{organ}.h5ad")
    a.obs["organ"] = organ
    adatas_ts[organ] = a
    print(f"  TS_{organ}: {a.n_obs} cells")

common_genes = sorted(set.intersection(*[set(a.var_names) for a in adatas_ts.values()]))
print(f"  Common genes: {len(common_genes)}")

# Load HK
hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().tolist())
hk_mouse_genes_raw = set(hk_df["Mouse"].dropna().tolist())

# ================================================================
# Preprocess human: do filtering manually, then concat
# ================================================================
print("\n" + "="*60)
print("Preprocessing human (memory-safe)...")
print("="*60)

adatas_pp = {}
for organ, a in adatas_ts.items():
    # Manual cell filter: min 500 genes expressed
    X = a.X
    if issparse(X):
        n_genes_per_cell = np.array((X > 0).sum(axis=1)).flatten()
    else:
        n_genes_per_cell = (X > 0).sum(axis=1)
    cell_mask = n_genes_per_cell >= 500
    a2 = a[cell_mask, :].copy()
    # Manual gene filter: min 3 cells
    X2 = a2.X
    if issparse(X2):
        n_cells_per_gene = np.array((X2 > 0).sum(axis=0)).flatten()
    else:
        n_cells_per_gene = (X2 > 0).sum(axis=0)
    gene_mask = n_cells_per_gene >= 3
    a2 = a2[:, gene_mask].copy()
    print(f"  {organ}: {a.n_obs}→{a2.n_obs} cells, {a.n_vars}→{a2.n_vars} genes")
    adatas_pp[organ] = a2

# Concat filtered organs (much smaller now)
adata_h = sc.concat(list(adatas_pp.values()), axis=0, join="inner", index_unique="-")
print(f"  Merged: {adata_h.n_obs} x {adata_h.n_vars}")

# Normalize + log1p (in-place or on view)
sc.pp.normalize_total(adata_h, target_sum=1e4)
sc.pp.log1p(adata_h)

# HVG
sc.pp.highly_variable_genes(adata_h, n_top_genes=2000, flavor="seurat")
hg_genes = adata_h.var_names.tolist()
hg_hk_idx = np.array([i for i, g in enumerate(hg_genes) if g in hk_human_genes])
hg_id_idx = np.array(np.where(adata_h.var["highly_variable"].values)[0].tolist())
print(f"  HVG=2000, HK={len(hg_hk_idx)}, ID={len(hg_id_idx)}")

# ================================================================
# Helper: build CT pseudobulks
# ================================================================
def build_ct_pb(adata, min_cells=10):
    entries = []
    for organ in TS_ORGANS:
        tdata = adata[adata.obs["organ"] == organ]
        for ct in tdata.obs["cell_ontology_class"].unique():
            if ct.lower() == "unknown":
                continue
            ct_data = tdata[tdata.obs["cell_ontology_class"] == ct]
            if ct_data.n_obs < min_cells * 2:
                continue
            if "donor" in ct_data.obs.columns:
                dc = ct_data.obs["donor"].value_counts()
                donors_ok = [(d,n) for d,n in dc.items() if n >= min_cells]
            else:
                donors_ok = [("pooled", ct_data.n_obs)]
            if not donors_ok:
                continue
            donors_ok.sort(key=lambda x: -x[1])
            largest = donors_ok[0][0]
            mask = ct_data.obs["donor"] == largest if "donor" in ct_data.obs.columns else slice(None)
            X_l = ct_data[mask].X
            if hasattr(X_l, "toarray"):
                X_l = X_l.toarray()
            if X_l.shape[0] < min_cells:
                continue
            entries.append({
                "key": f"{organ}|{ct}", "organ": organ, "ct": ct,
                "pb": np.mean(X_l, axis=0), "n_cells": X_l.shape[0],
            })
    return entries

ct_log = build_ct_pb(adata_h, min_cells=10)
print(f"\n  CT entries: {len(ct_log)}")

# ================================================================
# A: raw vs log1p
# ================================================================
print("\n" + "="*60)
print("A. Raw counts vs log1p effect on k_f")
print("="*60)

# Build raw AnnData (no log1p) — use same HVG genes from log1p data
# to avoid overflow in HVG computation on raw counts
adata_raw = sc.concat(list(adatas_pp.values()), axis=0, join="inner", index_unique="-")
sc.pp.normalize_total(adata_raw, target_sum=1e4)
# NO log1p — use HVG indices from log1p data (same genes, different expression values)
rg_genes = adata_raw.var_names.tolist()
rg_hk_idx = np.array([i for i, g in enumerate(rg_genes) if g in hk_human_genes])
# Use SAME gene indices as log1p HVG (not re-computed)
rg_id_idx = hg_id_idx.copy()

ct_raw = build_ct_pb(adata_raw, min_cells=10)
print(f"  log1p CTs: {len(ct_log)}, raw CTs: {len(ct_raw)}")

# Sample 300 random pairs
np.random.seed(RANDOM_SEED)
n_log = len(ct_log)
pairs_set = set()
while len(pairs_set) < 300:
    i, j = np.random.choice(n_log, 2, replace=False)
    if i > j: i, j = j, i
    pairs_set.add((i, j))
pairs_list = list(pairs_set)

kf_log_v, kf_raw_v, kn_log_v, kn_raw_v = [], [], [], []
for i, j in pairs_list:
    rl = compute_omega(ct_log[i]["pb"], ct_log[j]["pb"], hg_hk_idx, hg_id_idx, w1=1.0, w2=0.0)
    kf_log_v.append(rl["kf"]); kn_log_v.append(rl["kn"])
    if i < len(ct_raw) and j < len(ct_raw):
        rr = compute_omega(ct_raw[i]["pb"], ct_raw[j]["pb"], rg_hk_idx, rg_id_idx, w1=1.0, w2=0.0)
        kf_raw_v.append(rr["kf"]); kn_raw_v.append(rr["kn"])

kf_l = np.array(kf_log_v); kf_r = np.array(kf_raw_v)
kn_l = np.array(kn_log_v); kn_r = np.array(kn_raw_v)
print(f"  k_f log1p: mean={np.mean(kf_l):.5f} median={np.median(kf_l):.5f}")
print(f"  k_f raw:   mean={np.mean(kf_r):.5f} median={np.median(kf_r):.5f}")
ratio_a = np.mean(kf_r/(kf_l+1e-9))
print(f"  ratio raw/log1p: {ratio_a:.2f}x")
print(f"  k_n log1p: mean={np.mean(kn_l):.5f}, raw: mean={np.mean(kn_r):.5f}")

# ================================================================
# B: HVG sweep (on log1p data)
# ================================================================
print("\n" + "="*60)
print("B. HVG size sweep (2000 / 5000 / 10000 / 20000)")
print("="*60)

hvg_sizes = [2000, 5000, 10000, 20000]
sweep_results = {}

# HVG sweep — manual dispersion computed directly on sparse matrix (no copy)
from scipy.sparse import issparse, csr_matrix

def manual_hvg_sparse(X_sparse, n_top):
    """Compute HVG directly from sparse matrix (no AnnData copy needed)."""
    # Use a random subset of cells for speed
    n_cells = X_sparse.shape[0]
    n_sample_cells = min(5000, n_cells)
    np.random.seed(RANDOM_SEED)
    cell_sel = np.sort(np.random.choice(n_cells, n_sample_cells, replace=False))
    X_sub = X_sparse[cell_sel, :]

    # Compute mean and var in log space
    X_arr = X_sub.toarray().astype(np.float64)
    means = np.mean(X_arr, axis=0)
    vars_arr = np.var(X_arr, axis=0)
    with np.errstate(divide='ignore', invalid='ignore'):
        dispersion = vars_arr / (means + 1e-9)
    dispersion[np.isnan(dispersion)] = 0
    dispersion[np.isinf(dispersion)] = 0

    # Bin by mean, pick top dispersion per bin
    n_bins = 20
    order = np.argsort(means)
    bin_size = max(1, len(means) // n_bins)
    top_per_bin = max(1, n_top // n_bins)
    selected = np.zeros(len(means), dtype=bool)
    for b in range(n_bins):
        s = b * bin_size
        e = min((b+1)*bin_size, len(means))
        if s >= e: continue
        bin_idx = order[s:e]
        bin_disp = dispersion[bin_idx]
        top_local = min(top_per_bin, len(bin_idx))
        top_idx = bin_idx[np.argsort(bin_disp)[-top_local:]]
        selected[top_idx] = True
    if selected.sum() < n_top:
        remaining = n_top - selected.sum()
        unselected = np.where(~selected)[0]
        top_remain = unselected[np.argsort(dispersion[unselected])[-remaining:]]
        selected[top_remain] = True
    return selected

# Get sparse X directly
X_human = adata_h.X  # csr_matrix, log1p-normalized
print(f"  Computing HVG on {X_human.shape} sparse matrix...")

for n_hvg in hvg_sizes:
    hv_sel = manual_hvg_sparse(X_human, n_hvg)
    id_idx = np.where(hv_sel)[0].astype(int)
    hk_idx = np.array([i for i, g in enumerate(hg_genes) if g in hk_human_genes])

    ct_list = build_ct_pb(adata_h, min_cells=10)
    n_ct = len(ct_list)

    kf_v, kn_v = [], []
    np.random.seed(RANDOM_SEED)
    all_pairs = [(i,j) for i in range(n_ct) for j in range(i+1,n_ct)]
    if len(all_pairs) > 500:
        all_pairs = [all_pairs[k] for k in np.random.choice(len(all_pairs), 500, replace=False)]

    for i, j in all_pairs:
        r = compute_omega(ct_list[i]["pb"], ct_list[j]["pb"], hk_idx, id_idx, w1=1.0, w2=0.0)
        kf_v.append(r["kf"])
        kn_v.append(r["kn"])

    sweep_results[n_hvg] = {
        "kf_mean": np.mean(kf_v), "kf_median": np.median(kf_v),
        "kn_mean": np.mean(kn_v), "kn_median": np.median(kn_v),
        "n_ct": n_ct, "hvg_frac": n_hvg/adata_h.n_vars,
    }
    print(f"  HVG={n_hvg} ({n_hvg/adata_h.n_vars*100:.1f}%): "
          f"k_f={np.mean(kf_v):.5f}, kn={np.mean(kn_v):.5f}, CTs={n_ct}")

# ================================================================
# C: Mouse comparison
# ================================================================
print("\n" + "="*60)
print("C. Mouse FACS k_f (same method)")
print("="*60)

TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
annot = pd.read_csv(ANNOT_FILE)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]

def extract_mid(cn):
    for p in cn.split("."):
        if "_" in p and (p.endswith("_M") or p.endswith("_F")):
            return p
    return "unknown"
annot["mouse.id"] = annot["cell"].apply(extract_mid)

mouse_dfs_pp = {}
all_mg = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if fname.exists():
        df = pd.read_csv(fname, index_col=0)
        # Filter cells with >=500 genes
        df = df.loc[:, (df > 0).sum(axis=0) >= 500]
        mouse_dfs_pp[tissue] = df
        all_mg.update(df.index.tolist())

cmg = sorted(all_mg)
for tissue, df in mouse_dfs_pp.items():
    cmg = [g for g in cmg if g in df.index]

expr_p, obs_p = [], []
for tissue, df in mouse_dfs_pp.items():
    dfa = df.loc[df.index.isin(cmg)].reindex(cmg, fill_value=0).T
    expr_p.append(dfa.values)
    ta = annot[annot["tissue"] == tissue].copy()
    cids = dfa.index.tolist()
    ot = pd.DataFrame({"cell": cids, "tissue": tissue})
    ot = ot.merge(ta[["cell","cell_ontology_class","mouse.id"]], on="cell", how="left")
    ot["cell_ontology_class"] = ot["cell_ontology_class"].fillna("unknown")
    ot.set_index("cell", inplace=True)
    obs_p.append(ot)

adata_m = sc.AnnData(X=np.vstack(expr_p), obs=pd.concat(obs_p),
                      var=pd.DataFrame({"gene": cmg}).set_index("gene"))
print(f"  Mouse: {adata_m.n_obs} x {adata_m.n_vars}")

sc.pp.filter_genes(adata_m, min_cells=3)
sc.pp.normalize_total(adata_m, target_sum=1e4)
sc.pp.log1p(adata_m)
sc.pp.highly_variable_genes(adata_m, n_top_genes=2000, flavor="seurat")

mg_genes = adata_m.var_names.tolist()
mk_hk = np.array([i for i, g in enumerate(mg_genes) if g in hk_mouse_genes_raw])
mk_id = np.array(np.where(adata_m.var["highly_variable"].values)[0].tolist())

def build_ct_pb_mouse(adata, min_cells=10):
    entries = []
    for tissue in TARGET_TISSUES:
        tdata = adata[adata.obs["tissue"] == tissue]
        for ct in tdata.obs["cell_ontology_class"].unique():
            if ct.lower() == "unknown": continue
            ct_data = tdata[tdata.obs["cell_ontology_class"] == ct]
            if ct_data.n_obs < min_cells * 2: continue
            mc = ct_data.obs["mouse.id"].value_counts()
            ok = [(d,n) for d,n in mc.items() if n >= min_cells]
            if not ok: continue
            ok.sort(key=lambda x: -x[1])
            largest = ok[0][0]
            mask = ct_data.obs["mouse.id"] == largest
            X_l = ct_data[mask].X
            if hasattr(X_l, "toarray"): X_l = X_l.toarray()
            if X_l.shape[0] < min_cells: continue
            entries.append({
                "key": f"{tissue}|{ct}", "tissue": tissue, "ct": ct,
                "pb": np.mean(X_l, axis=0), "n_cells": X_l.shape[0],
            })
    return entries

ct_m = build_ct_pb_mouse(adata_m, min_cells=10)
print(f"  Mouse CTs: {len(ct_m)}")

# Sample mouse pairs
nm = len(ct_m)
mpairs = [(i,j) for i in range(nm) for j in range(i+1,nm)]
if len(mpairs) > 500:
    np.random.seed(RANDOM_SEED)
    mpairs = [mpairs[k] for k in np.random.choice(len(mpairs), 500, replace=False)]

mkf, mkn = [], []
for i, j in mpairs:
    r = compute_omega(ct_m[i]["pb"], ct_m[j]["pb"], mk_hk, mk_id, w1=1.0, w2=0.0)
    mkf.append(r["kf"]); mkn.append(r["kn"])

print(f"  Mouse k_f: mean={np.mean(mkf):.5f} median={np.median(mkf):.5f}")
print(f"  Mouse k_n: mean={np.mean(mkn):.5f} median={np.median(mkn):.5f}")

# ================================================================
# D: HK JS divergence distribution
# ================================================================
print("\n" + "="*60)
print("D. HK gene JS divergence distribution")
print("="*60)

def hk_js_dist(entries, hk_idx, n=500):
    js_v = []
    all_p = [(i,j) for i in range(len(entries)) for j in range(i+1,len(entries))]
    if len(all_p) > n:
        np.random.seed(RANDOM_SEED)
        all_p = [all_p[k] for k in np.random.choice(len(all_p), n, replace=False)]
    for i, j in all_p:
        js_v.append(js_divergence(entries[i]["pb"][hk_idx], entries[j]["pb"][hk_idx]))
    return np.array(js_v)

hjs = hk_js_dist(ct_log, hg_hk_idx, 500)
mjs = hk_js_dist(ct_m, mk_hk, 500)
print(f"  Human HK JS: mean={np.mean(hjs):.5f} median={np.median(hjs):.5f}")
print(f"  Mouse HK JS: mean={np.mean(mjs):.5f} median={np.median(mjs):.5f}")

# ================================================================
# E: Shared CT cross-species
# ================================================================
print("\n" + "="*60)
print("E. Shared cell types cross-species")
print("="*60)

def simplify_ct(name):
    n = name.lower().strip()
    for p in ["cardiac ", "kidney ", "liver ", "lung ", "alveolar ", "bronchial ",
              "intrahepatic ", "capillary ", "vein ", "vascular associated ",
              "endothelial cell of hepatic sinusoid"]:
        n = n.replace(p, "")
    n = n.replace("cardiac muscle cell", "cardiomyocyte")
    n = n.replace("natural killer cell", "nk cell")
    n = n.replace("cd8-positive, alpha-beta t cell", "cd8 t cell")
    n = n.replace("cd4-positive, alpha-beta t cell", "cd4 t cell")
    n = n.replace("cd4-positive helper t cell", "cd4 t cell")
    n = n.replace("cd4-positive alpha-beta t cell", "cd4 t cell")
    n = n.replace("cd8-positive alpha-beta t cell", "cd8 t cell")
    n = n.replace("classical monocyte", "monocyte")
    n = n.replace("non-classical monocyte", "monocyte")
    return n.strip()

hm_ct = {}
for e in ct_log:
    hm_ct.setdefault(simplify_ct(e["ct"]), []).append(e)
mm_ct = {}
for e in ct_m:
    mm_ct.setdefault(simplify_ct(e["ct"]), []).append(e)

shared = set(hm_ct.keys()) & set(mm_ct.keys())
print(f"  Shared simplified CTs: {len(shared)}")
for s in sorted(shared):
    print(f"    {s}: human={len(hm_ct[s])} mouse={len(mm_ct[s])}")

# ================================================================
# SUMMARY
# ================================================================
print("\n" + "="*60)
print("DIAGNOSIS SUMMARY")
print("="*60)

print(f"\nA. Raw vs log1p k_f ratio: {ratio_a:.2f}x")
if ratio_a > 1.5:
    print("   >> log1p IS a major compressor of k_f")
else:
    print("   >> log1p has minor effect")

print(f"\nB. HVG sweep:")
ref_kf = sweep_results[2000]["kf_mean"]
for s in hvg_sizes:
    r = sweep_results[s]
    ratio = r["kf_mean"] / ref_kf
    bar = "#" * int(ratio * 10)
    print(f"   HVG={s:5d} ({r['hvg_frac']*100:4.1f}%): k_f={r['kf_mean']:.5f} ({ratio:.2f}x) {bar}")

print(f"\nC. Mouse k_f: {np.mean(mkf):.5f} (Phase 3.2 benchmark: 0.1084)")
print(f"   Human k_f (HVG=2000): {ref_kf:.5f}")
print(f"   Ratio mouse/human: {np.mean(mkf)/ref_kf:.2f}x")

print(f"\nD. HK JS divergence:")
print(f"   Human: {np.mean(hjs):.5f}")
print(f"   Mouse: {np.mean(mjs):.5f}")

print(f"\nE. Root cause assessment:")
if np.mean(hjs) < np.mean(mjs) * 0.5:
    print("   Human k_n is smaller → NOT the problem (denominator is fine)")
elif np.mean(hjs) > np.mean(mjs) * 3:
    print("   Human k_n is much larger → k_n inflates denominator")
else:
    print(f"   k_n ratio human/mouse: {np.mean(hjs)/np.mean(mjs):.2f}x")

if ratio_a > 2:
    print(f"   log1p compression is MAJOR (raw/log1p = {ratio_a:.1f}x)")
best_hvg = max(sweep_results.items(), key=lambda x: x[1]["kf_mean"])
if best_hvg[1]["kf_mean"] > ref_kf * 1.5:
    print(f"   HVG={best_hvg[0]} boosts k_f {best_hvg[1]['kf_mean']/ref_kf:.1f}x → significant")

print("\n" + "="*60)
print("DONE.")
print("="*60)
