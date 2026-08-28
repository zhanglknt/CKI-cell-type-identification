"""
Reviewer fix C-B (#965, TS part): scheme-matched split-half calibration
inside Tabula Sapiens (10x), analogous to the mouse SmartSeq2 calibration
(mean omega = 6.67, CI [4.12, 9.33]) that is currently transferred to the
human brain and TCGA analyses.

Design
------
Pipeline identical to phase35 / 37 (common genes, QC, normalize 1e4 +
log1p, HK genes from Human_Mouse_Common.csv). For every (organ, CT)
population with >= 100 cells in its largest donor, do B = 50 random
split-half replicates: pseudobulk each half (mean of log1p values), compute
k_n = JS(HK genes) and k_f = JS(top-200 |diff| non-HK genes), omega = k_f/k_n.

Report: per-population means, dataset grand mean + 95% bootstrap CI.

Usage
-----
    ./cki_env/Scripts/python.exe -u notebooks/43_reviewer_fix_ts_splithalf.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
from cki.core import js_divergence

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)

RANDOM_SEED = 42
MIN_POP_CELLS = 100
B_SPLIT = 50
N_TOP_KF = 200

rng = np.random.RandomState(RANDOM_SEED)

print("=" * 60)
print("Loading TS human data (phase35 pipeline)...")
print("=" * 60)

adatas_raw = {}
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
    if fname.exists():
        adata = sc.read_h5ad(fname)
        adata.obs["organ"] = organ
        adatas_raw[organ] = adata
        print(f"  {organ}: {adata.n_obs} cells")

all_gene_sets = [set(a.var_names) for a in adatas_raw.values()]
common_genes = sorted(all_gene_sets[0].intersection(*all_gene_sets[1:]))

adata_list = []
for organ, adata in adatas_raw.items():
    adata_sub = adata[:, common_genes].copy()
    adata_sub.obs["organ"] = organ
    adata_list.append(adata_sub)

adata = sc.concat(adata_list, axis=0, join="inner", index_unique="-")
del adatas_raw, adata_list
sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
print(f"  Pooled: {adata.n_obs} cells x {adata.n_vars} genes")

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().tolist())
gene_names = adata.var_names.tolist()
hk_idx = np.array([i for i, g in enumerate(gene_names) if g in hk_human_genes])
non_hk_mask = np.ones(adata.n_vars, dtype=bool)
non_hk_mask[hk_idx] = False
non_hk_idx = np.where(non_hk_mask)[0]
print(f"  HK genes: {len(hk_idx)}")


def pair_kf_kn(pb_a, pb_b):
    kn = js_divergence(pb_a[hk_idx], pb_b[hk_idx])
    ad = np.abs(pb_a - pb_b)
    ad_nh = ad[non_hk_idx]
    top_n = min(N_TOP_KF, len(ad_nh))
    top_local = np.argpartition(ad_nh, -top_n)[-top_n:]
    tg = non_hk_idx[top_local]
    kf = js_divergence(pb_a[tg], pb_b[tg])
    return kf, kn


records = []
for organ in TS_ORGANS:
    tdata = adata[adata.obs["organ"] == organ]
    for ct, count in tdata.obs["cell_ontology_class"].value_counts().items():
        if ct.lower() == "unknown":
            continue
        ct_data = tdata[tdata.obs["cell_ontology_class"] == ct]
        if "donor" in ct_data.obs.columns:
            donor_counts = ct_data.obs["donor"].value_counts()
            largest_donor = donor_counts.index[0]
            ct_data = ct_data[ct_data.obs["donor"] == largest_donor]
        n = ct_data.n_obs
        if n < MIN_POP_CELLS:
            continue
        Xct = ct_data.X
        if hasattr(Xct, "toarray"):
            pass  # keep sparse
        omegas = []
        for b in range(B_SPLIT):
            perm = rng.permutation(n)
            half = n // 2
            pbA = np.asarray(Xct[perm[:half]].mean(axis=0)).flatten()
            pbB = np.asarray(Xct[perm[half:2*half]].mean(axis=0)).flatten()
            kf, kn = pair_kf_kn(pbA, pbB)
            omegas.append(kf / kn if kn > 1e-15 else np.inf)
        records.append({
            'organ': organ, 'ct': ct, 'n_cells': n,
            'omega_mean': float(np.mean(omegas)),
            'omega_median': float(np.median(omegas))})
        print(f"  {organ}|{ct}: n={n}, split-half omega={np.mean(omegas):.2f}")

df = pd.DataFrame(records)
df.to_csv(RESULTS_DIR / 'reviewer_ts_splithalf_populations.csv', index=False)

all_sh = []
for r in records:
    all_sh.extend([r['omega_mean']] * 1)  # population-level bootstrap below

# bootstrap over populations (matching the mouse n=6 population-level convention)
pop_vals = df['omega_mean'].values
grand = float(np.mean(pop_vals))
boot = [float(np.mean(rng.choice(pop_vals, size=len(pop_vals), replace=True)))
        for _ in range(2000)]
lo, hi = np.percentile(boot, [2.5, 97.5])
print("\n" + "=" * 60)
print(f"TS split-half baseline (population-level, n={len(pop_vals)} populations): "
      f"mean omega = {grand:.2f}, 95% bootstrap CI [{lo:.2f}, {hi:.2f}]")
print(f"Mouse SmartSeq2 reference: 6.67 [4.12, 9.33]")
print("=" * 60)

with open(RESULTS_DIR / 'reviewer_ts_splithalf_summary.txt', 'w') as fh:
    fh.write(f"ts_split_half_mean_omega\t{grand:.4f}\n")
    fh.write(f"ts_split_half_ci95\t[{lo:.4f}, {hi:.4f}]\n")
    fh.write(f"n_populations\t{len(pop_vals)}\n")
    fh.write(f"B_per_population\t{B_SPLIT}\n")
    fh.write(f"min_pop_cells\t{MIN_POP_CELLS}\n")

print("Saved -> results/reviewer_ts_splithalf_populations.csv")
print("DONE.")
