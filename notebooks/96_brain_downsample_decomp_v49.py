"""
v49.13 B2: k_f / k_n decomposition of the equal-n (size-balanced) brain
regional gradient.
============================================================================
Reviewer: R5-N5. The 20 equal-n downsample replicates (script 86) reported
only the omega gradient (1.74-fold). This script reruns the identical
downsample pipeline (same seed, same allocation, same pseudobulk construction
as notebooks/86_brain_downsample_threshold_v44.py) and additionally records,
per replicate, the class-level k_f and k_n means, so the residual equal-n
gradient can be attributed to its components:
  - gradient_omega = astro_omega / berg_omega
  - gradient_kf    = astro_kf / berg_kf
  - gradient_kn    = astro_kn / berg_kn
plus the across-class correlation of downsampled omega with each component.

Only the observed downsample part of script 86 is rerun; the threshold
sensitivity and confound sections are not repeated. Outputs use the _v49
suffix; no existing results file is overwritten.

Runtime: single sequential scan over the brain matrix (888k nuclei) with 20
replicate accumulations. Seed 42 (matches script 86's draw sequence).
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import h5py
from scipy.stats import spearmanr
from cki.core import js_divergence

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_t0_all = time.time()

# ===== Config (identical to script 86) =====
RANDOM_SEED = 42
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
R_DS = 20
THRESHOLDS = [10, 20, 50, 100]
REF_THRESHOLD = 20
ct_col = 'supercluster_term'
region_col = 'roi'

rng = np.random.RandomState(RANDOM_SEED)

# ===== 1. HK genes + metadata (as script 86) =====
print("1. Loading HK genes + obs metadata (backed h5py)...")
hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))

f = h5py.File(BRAIN_FILE, 'r')
X = f['X']
indptr_full = X['indptr'][:]
N_CELLS = indptr_full.shape[0] - 1

vg = f['var']['Gene']
if isinstance(vg, h5py.Dataset):
    var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
else:
    categories = [x.decode() if isinstance(x, bytes) else str(x) for x in vg['categories'][:]]
    codes = vg['codes'][:]
    var_gene = [categories[c] if c >= 0 else None for c in codes]
N_GENES = len(var_gene)

obs = f['obs']
def read_codes(name):
    g = obs[name]
    cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g['categories'][:]]
    codes = g['codes'][:]
    return np.array(cats)[codes]

ct_names = read_codes(ct_col)
roi_names = read_codes(region_col)

hk_global = np.array(sorted({i for i, sym in enumerate(var_gene)
                             if sym is not None and sym in hk_human}), dtype=int)

# ===== 2. Global gene means (HVG selection) =====
print("2. Global gene means...")
t0 = time.time()
gene_sums = np.zeros(N_GENES, dtype=np.float64)
BATCH = 50000
for start in range(0, N_CELLS, BATCH):
    end = min(start + BATCH, N_CELLS)
    lo, hi = int(indptr_full[start]), int(indptr_full[end])
    data_batch = X['data'][lo:hi]
    idx_batch = X['indices'][lo:hi]
    np.add.at(gene_sums, idx_batch, data_batch)
gene_means = gene_sums / N_CELLS
print(f"  done in {time.time()-t0:.0f}s")

non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_global] = False
non_hk_means = gene_means.copy()
non_hk_means[~non_hk_mask] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
keep_global = np.sort(np.union1d(hk_global, hvg_global))
is_hk_in_keep = np.isin(keep_global, hk_global)
hk_in_reduced = np.where(is_hk_in_keep)[0]
non_hk_in_reduced = np.where(~is_hk_in_keep)[0]
N_KEEP = len(keep_global)
print(f"  Reduced set: {N_KEEP} genes")

# ===== 3. Groups (as script 86) =====
print("3. Group structure...")
df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names})
groups = df_meta.groupby(['ct', 'roi']).size().reset_index(name='count')
region_counts = df_meta['roi'].value_counts()
regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
groups = groups[groups['roi'].isin(regions_ok)].reset_index(drop=True)
groups_sup = groups[groups['count'] >= min(THRESHOLDS)].reset_index(drop=True)

gcount = {(r['ct'], r['roi']): int(r['count']) for _, r in groups.iterrows()}

ct_to_regions_sup = {}
for _, row in groups_sup.iterrows():
    ct_to_regions_sup.setdefault(row['ct'], []).append(row['roi'])
for ct in ct_to_regions_sup:
    ct_to_regions_sup[ct] = sorted(ct_to_regions_sup[ct])

class_total_t20 = {}
for ct, regs in ct_to_regions_sup.items():
    class_total_t20[ct] = sum(gcount[(ct, r)] for r in regs
                              if gcount.get((ct, r), 0) >= REF_THRESHOLD)
cts_all = sorted(ct_to_regions_sup.keys())
min_class_total = min(class_total_t20.values())
print(f"  min class total @t=20: {min_class_total}")

ds_alloc = {}
for ct in cts_all:
    tot = class_total_t20[ct]
    for r in ct_to_regions_sup[ct]:
        n = gcount.get((ct, r), 0)
        if n >= REF_THRESHOLD:
            k = max(1, int(round(n * min_class_total / tot)))
            ds_alloc[(ct, r)] = min(k, n)

# ===== 4-5. Chunked accumulation: full + downsample sums (as script 86) =====
GENE_MAP = np.full(N_GENES, -1, dtype=np.int32)
GENE_MAP[keep_global] = np.arange(N_KEEP, dtype=np.int32)

def pb_from_sum(col_sum, n):
    pb = col_sum / max(n, 1)
    tot = pb.sum()
    if tot > 0:
        pb = pb / tot * 1e4
    return np.log1p(pb).astype(np.float64)

def pair_stats(pbs, hk_idx, non_hk_idx, n_top=N_TOP_KF):
    n = len(pbs)
    out = []
    for i in range(n):
        pi = pbs[i]
        for j in range(i + 1, n):
            pj = pbs[j]
            kn = js_divergence(pi[hk_idx], pj[hk_idx])
            ad = np.abs(pi - pj)
            ad_nh = ad[non_hk_idx]
            top_n = min(n_top, len(ad_nh))
            tl = np.argpartition(ad_nh, -top_n)[-top_n:]
            tl = tl[np.argsort(ad_nh[tl])[::-1]]
            tg = non_hk_idx[tl]
            kf = js_divergence(pi[tg], pj[tg])
            out.append((kn, kf, kf / kn if kn > 1e-15 else np.inf))
    return out

print("5. Per-region extraction (full + downsample replicate sums)")
region_pb_ds = {r: {} for r in range(R_DS)}

group_list = []
group_code = {}
for ct in cts_all:
    for r in ct_to_regions_sup[ct]:
        group_code[(ct, r)] = len(group_list)
        group_list.append((ct, r))
G = len(group_list)

ct_codes_all = obs[ct_col]['codes'][:]
roi_codes_all = obs[region_col]['codes'][:]
ct_cats = [x.decode() if isinstance(x, bytes) else str(x)
           for x in obs[ct_col]['categories'][:]]
roi_cats = [x.decode() if isinstance(x, bytes) else str(x)
            for x in obs[region_col]['categories'][:]]
combo = ct_codes_all.astype(np.int64) * len(roi_cats) + roi_codes_all
combo_to_g = {}
for (ct, r), g in group_code.items():
    ci = ct_cats.index(ct)
    ri = roi_cats.index(r)
    combo_to_g[ci * len(roi_cats) + ri] = g
map_arr = np.full(len(ct_cats) * len(roi_cats), -1, dtype=np.int32)
for c, g in combo_to_g.items():
    map_arr[c] = g
gcode_row = map_arr[combo]
del combo

gsizes = np.bincount(gcode_row[gcode_row >= 0], minlength=G).astype(np.int64)

sel_flat = np.zeros((R_DS, N_CELLS), dtype=bool)
cells_by_group = [np.where(gcode_row == g)[0] for g in range(G)]
for (ct, r), g in group_code.items():
    k = ds_alloc.get((ct, r))
    if k is None:
        continue
    cells_g = cells_by_group[g]
    for rep in range(R_DS):
        idx_sel = rng.choice(len(cells_g), size=k, replace=False)
        sel_flat[rep, cells_g[idx_sel]] = True
del cells_by_group

ds_sums = np.zeros((R_DS, G, N_KEEP), dtype=np.float32)
BLOCK = 100000
n_blocks = (N_CELLS + BLOCK - 1) // BLOCK
for bi, start in enumerate(range(0, N_CELLS, BLOCK)):
    end = min(start + BLOCK, N_CELLS)
    lo, hi = int(indptr_full[start]), int(indptr_full[end])
    if hi <= lo:
        continue
    cdat = X['data'][lo:hi]
    cidx = X['indices'][lo:hi]
    ptr = indptr_full[start:end + 1] - lo
    counts = np.diff(ptr)
    rid = np.repeat(np.arange(start, end), counts)
    grow = gcode_row[rid]
    mapped = GENE_MAP[cidx]
    keepm = (grow >= 0) & (mapped >= 0)
    gk = grow[keepm]
    mk = mapped[keepm]
    wk = cdat[keepm].astype(np.float64)
    rid_k = rid[keepm]
    for rep in range(R_DS):
        sm = sel_flat[rep, rid_k]
        if not sm.any():
            continue
        key = gk[sm] * N_KEEP + mk[sm]
        bc = np.bincount(key, weights=wk[sm], minlength=G * N_KEEP)
        ds_sums[rep] += bc.reshape(G, N_KEEP)
    print(f"    block {bi+1}/{n_blocks} ({end}/{N_CELLS} cells)", flush=True)

for (ct, r), g in group_code.items():
    k = ds_alloc.get((ct, r))
    if k is not None:
        for rep in range(R_DS):
            region_pb_ds[rep][(ct, r)] = pb_from_sum(
                ds_sums[rep, g].astype(np.float64), k)
del ds_sums, sel_flat
print(f"  downsampled pseudobulks finalized ({len(ds_alloc)} x {R_DS})")

# ===== 9'. Downsample with k_f / k_n decomposition =====
print("\n9'. Equal-n downsample replicates with k_f/k_n decomposition")
# t=20 analysis classes (must match script 86's cts_t20)
class_total_pass = {ct: sum(gcount.get((ct, r), 0) >= REF_THRESHOLD
                             for r in ct_to_regions_sup[ct])
                    for ct in cts_all}
cts_t20 = [ct for ct in cts_all
           if class_total_pass[ct] * (class_total_pass[ct] - 1) // 2 >= 5]
print(f"  classes: {len(cts_t20)}")

rep_rows = []
for rep in range(R_DS):
    om_means, kf_means, kn_means = {}, {}, {}
    for ct in cts_t20:
        regs = [r for r in ct_to_regions_sup[ct]
                if gcount.get((ct, r), 0) >= REF_THRESHOLD]
        pbs = [region_pb_ds[rep][(ct, r)] for r in regs]
        stats = pair_stats(pbs, hk_in_reduced, non_hk_in_reduced)
        kn_means[ct] = float(np.mean([s[0] for s in stats]))
        kf_means[ct] = float(np.mean([s[1] for s in stats]))
        om_means[ct] = float(np.mean([s[2] for s in stats]))
    row = {'rep': rep,
           'gradient_omega': om_means.get('Astrocyte', np.nan) / om_means.get('Bergmann glia', np.nan),
           'gradient_kf': kf_means.get('Astrocyte', np.nan) / kf_means.get('Bergmann glia', np.nan),
           'gradient_kn': kn_means.get('Astrocyte', np.nan) / kn_means.get('Bergmann glia', np.nan),
           'astro_kf': kf_means.get('Astrocyte', np.nan),
           'berg_kf': kf_means.get('Bergmann glia', np.nan),
           'astro_kn': kn_means.get('Astrocyte', np.nan),
           'berg_kn': kn_means.get('Bergmann glia', np.nan)}
    row.update({f'omega__{ct}': om_means[ct] for ct in cts_t20})
    row.update({f'kf__{ct}': kf_means[ct] for ct in cts_t20})
    row.update({f'kn__{ct}': kn_means[ct] for ct in cts_t20})
    rep_rows.append(row)
    print(f"  rep {rep}: omega grad={row['gradient_omega']:.3f}, "
          f"kf grad={row['gradient_kf']:.3f}, kn grad={row['gradient_kn']:.3f}")

rep_df = pd.DataFrame(rep_rows)
rep_df.to_csv(RESULTS_DIR / "brain_v49_downsample_replicates_kfkn.csv", index=False)
print("  Saved: brain_v49_downsample_replicates_kfkn.csv")

# summary
g_om = rep_df.gradient_omega.values
g_kf = rep_df.gradient_kf.values
g_kn = rep_df.gradient_kn.values
rho_kf, _ = spearmanr(rep_df.omega__Astrocyte, rep_df.astro_kf)
rho_kn, _ = spearmanr(rep_df.omega__Astrocyte, rep_df.astro_kn)
summary = {
    'seed': RANDOM_SEED,
    'downsample_replicates': R_DS,
    'downsample_target_cells': int(min_class_total),
    'gradient_omega_mean': float(np.mean(g_om)),
    'gradient_omega_sd': float(np.std(g_om)),
    'gradient_omega_ci95': [float(np.percentile(g_om, 2.5)), float(np.percentile(g_om, 97.5))],
    'gradient_kf_mean': float(np.mean(g_kf)),
    'gradient_kf_ci95': [float(np.percentile(g_kf, 2.5)), float(np.percentile(g_kf, 97.5))],
    'gradient_kn_mean': float(np.mean(g_kn)),
    'gradient_kn_ci95': [float(np.percentile(g_kn, 2.5)), float(np.percentile(g_kn, 97.5))],
    'spearman_omega_vs_kf_astrocyte': float(rho_kf),
    'spearman_omega_vs_kn_astrocyte': float(rho_kn),
    'runtime_sec': round(time.time() - _t0_all, 1),
}
with open(RESULTS_DIR / "brain_v49_downsample_kfkn_summary.json", 'w') as jf:
    json.dump(summary, jf, indent=2)
print(json.dumps(summary, indent=2))
print(f"\nTotal runtime: {time.time()-_t0_all:.0f}s")
print("DONE")
