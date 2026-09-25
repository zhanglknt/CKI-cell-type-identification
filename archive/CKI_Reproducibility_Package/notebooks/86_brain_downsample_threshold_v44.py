"""
CKI Brain v44 Reviewer Controls (script 86)
===========================================
Addresses three blind-review questions for the v44 Genome Biology revision:

  A. Count/depth confound control:
     - Class-level k_n / omega vs log10(nuclei per class), vs mean detected
       genes per class, vs mean total counts per class (Spearman + Pearson, p).
     - Downsample every class to the smallest class size (no replacement,
       proportional across regions, R=20 replicates), recompute class-level
       k_n / omega and the Astrocyte/Bergmann-glia gradient; report class
       rank correlation (Spearman rho vs full data) and gradient retention.

  B. min-cells threshold sensitivity:
     - min cells per (roi, ct) group in {10, 20, 50, 100}; for each threshold
       report passing classes, pair counts, Strong/Moderate/Weak tier counts,
       class omega ranking (is Bergmann glia still lowest?), and the
       Astrocyte/Bergmann-glia gradient.

Pipeline mirrors notebooks/08d_brain_blockshuffle_null.py exactly (observed
part): region_col='roi', MIN_REGION_N=50, gene set = HRT HK + top-5000 non-HK
HVG by global mean, region pseudobulk = raw mean -> norm 1e4 -> log1p,
k_n = JS on HK, k_f = JS on per-pair top-200 non-HK DE, omega = k_f/k_n,
multiplicative tiers with lowest_in_pair Strong filter.

Memory: per-region chunked CSR extraction (16GB machine); backed h5py only.
Seed: 42. Outputs use _v44 suffix; no existing results file is overwritten.
"""

import sys, os, time, gc, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import h5py
from scipy.sparse import csr_matrix
from scipy.stats import spearmanr, pearsonr
from cki.core import js_divergence

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_t0_all = time.time()

# ===== Config =====
RANDOM_SEED = 42
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
R_DS = 20                      # downsample replicates
THRESHOLDS = [10, 20, 50, 100]
REF_THRESHOLD = 20             # authoritative threshold (matches 08d)
ct_col = 'supercluster_term'
region_col = 'roi'

rng = np.random.RandomState(RANDOM_SEED)

# ============================================================
# 1. HK genes + metadata
# ============================================================
print("=" * 60)
print("1. Loading HK genes + obs metadata (backed h5py)...")
hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"  HRT Atlas: {len(hk_human)} human HK genes")

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
print(f"  Shape: ({N_CELLS}, {N_GENES})")

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
print(f"  Matched HK genes: {len(hk_global)}")

# ============================================================
# 2. Global gene means (HVG selection) + per-cell depth metrics
# ============================================================
print("\n2. Global gene means + per-cell detected genes / total counts...")
t0 = time.time()
gene_sums = np.zeros(N_GENES, dtype=np.float64)
cell_nnz = np.diff(indptr_full).astype(np.int64)     # detected genes per cell
cell_totals = np.zeros(N_CELLS, dtype=np.float64)
BATCH = 50000
for start in range(0, N_CELLS, BATCH):
    end = min(start + BATCH, N_CELLS)
    lo, hi = int(indptr_full[start]), int(indptr_full[end])
    data_batch = X['data'][lo:hi]
    idx_batch = X['indices'][lo:hi]
    np.add.at(gene_sums, idx_batch, data_batch)
    # row totals within batch (reduceat; guard empty rows)
    row_ptr = indptr_full[start:end + 1] - lo
    counts = np.diff(row_ptr)
    nz_rows = np.where(counts > 0)[0]
    sums = np.add.reduceat(data_batch, row_ptr[nz_rows])
    cell_totals[start + nz_rows] = sums
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
print(f"  Reduced set: {N_KEEP} genes (HK={len(hk_in_reduced)} + HVG={len(non_hk_in_reduced)})")

# ============================================================
# 3. Groups at superset threshold (>=10), region filter >=50
# ============================================================
print("\n3. Group structure...")
df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names})
groups = df_meta.groupby(['ct', 'roi']).size().reset_index(name='count')
region_counts = df_meta['roi'].value_counts()
regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
groups = groups[groups['roi'].isin(regions_ok)].reset_index(drop=True)
groups_sup = groups[groups['count'] >= min(THRESHOLDS)].reset_index(drop=True)
print(f"  Groups (>={min(THRESHOLDS)}): {len(groups_sup)}")

# group count lookup
gcount = {(r['ct'], r['roi']): int(r['count']) for _, r in groups.iterrows()}

ct_to_regions_sup = {}
for _, row in groups_sup.iterrows():
    ct_to_regions_sup.setdefault(row['ct'], []).append(row['roi'])
for ct in ct_to_regions_sup:
    ct_to_regions_sup[ct] = sorted(ct_to_regions_sup[ct])

# class totals at reference threshold (t=20) for downsample design
class_total_t20 = {}
for ct, regs in ct_to_regions_sup.items():
    class_total_t20[ct] = sum(gcount[(ct, r)] for r in regs
                              if gcount.get((ct, r), 0) >= REF_THRESHOLD)
cts_all = sorted(ct_to_regions_sup.keys())
min_class_total = min(class_total_t20.values())
print(f"  Classes: {len(cts_all)}; class totals @t=20: "
      f"min={min_class_total} ({min(class_total_t20, key=class_total_t20.get)})")

# downsample allocation per (ct, roi): k = max(1, round(n * min_total/class_total))
ds_alloc = {}
for ct in cts_all:
    tot = class_total_t20[ct]
    for r in ct_to_regions_sup[ct]:
        n = gcount.get((ct, r), 0)
        if n >= REF_THRESHOLD:
            k = max(1, int(round(n * min_class_total / tot)))
            ds_alloc[(ct, r)] = min(k, n)

# ============================================================
# 4. Vectorized chunked accumulation (no per-cell Python loop)
# ============================================================
# For each CT (cells sorted by region, contiguous region blocks) we read the
# raw CSR arrays in chunks and accumulate, via np.bincount:
#   - full column sums per region                       -> full pseudobulk
#   - per-replicate sampled column sums per region      -> downsample pseudobulks
# Nothing larger than one chunk is held in memory.
GENE_MAP = np.full(N_GENES, -1, dtype=np.int32)
GENE_MAP[keep_global] = np.arange(N_KEEP, dtype=np.int32)

def pb_from_sum(col_sum, n):
    """raw mean -> norm 1e4 -> log1p (08d convention)."""
    pb = col_sum / max(n, 1)
    tot = pb.sum()
    if tot > 0:
        pb = pb / tot * 1e4
    return np.log1p(pb).astype(np.float64)

def pair_stats(pbs, hk_idx, non_hk_idx, n_top=N_TOP_KF):
    """All upper-triangle pairs -> arrays (kn, kf, omega)."""
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

# ============================================================
# 5. Per-CT pass: full region sums + downsample replicate sums
# ============================================================
print("\n" + "=" * 60)
print("5. Per-region extraction (full + downsample replicate sums)")
print("=" * 60)

region_pb_full = {}          # (ct, roi) -> log1p pb (all cells)
region_pb_ds = {r: {} for r in range(R_DS)}   # rep -> (ct, roi) -> log1p pb
region_n = {}                # (ct, roi) -> n cells

# group index per (ct, roi) in the superset (>=10 cells, region>=50)
group_list = []              # list of (ct, roi)
group_code = {}              # (ct, roi) -> g
for ct in cts_all:
    for r in ct_to_regions_sup[ct]:
        group_code[(ct, r)] = len(group_list)
        group_list.append((ct, r))
G = len(group_list)
print(f"  Superset groups: {G}")

# per-cell group code (int32, -1 if not in any superset group)
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

# group sizes (cells in superset groups)
gsizes = np.bincount(gcode_row[gcode_row >= 0], minlength=G).astype(np.int64)
for (ct, r), g in group_code.items():
    region_n[(ct, r)] = int(gsizes[g])

# pre-draw downsample selections (global cell ids per replicate)
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

# single sequential scan over the whole matrix
full_sums = np.zeros((G, N_KEEP), dtype=np.float64)
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
    rid = np.repeat(np.arange(start, end), counts)   # global row per nnz
    grow = gcode_row[rid]
    mapped = GENE_MAP[cidx]
    keepm = (grow >= 0) & (mapped >= 0)
    gk = grow[keepm]
    mk = mapped[keepm]
    wk = cdat[keepm].astype(np.float64)
    bc = np.bincount(gk * N_KEEP + mk, weights=wk, minlength=G * N_KEEP)
    full_sums += bc.reshape(G, N_KEEP)
    rid_k = rid[keepm]
    for rep in range(R_DS):
        sm = sel_flat[rep, rid_k]
        if not sm.any():
            continue
        key = gk[sm] * N_KEEP + mk[sm]
        bc = np.bincount(key, weights=wk[sm], minlength=G * N_KEEP)
        ds_sums[rep] += bc.reshape(G, N_KEEP)
    print(f"    block {bi+1}/{n_blocks} ({end}/{N_CELLS} cells)", flush=True)

# finalize pseudobulks
for (ct, r), g in group_code.items():
    n = int(gsizes[g])
    region_pb_full[(ct, r)] = pb_from_sum(full_sums[g], n)
    k = ds_alloc.get((ct, r))
    if k is not None:
        for rep in range(R_DS):
            region_pb_ds[rep][(ct, r)] = pb_from_sum(
                ds_sums[rep, g].astype(np.float64), k)
del full_sums, ds_sums, sel_flat
gc.collect()
print(f"  Pseudobulks finalized: {len(region_pb_full)} full, "
      f"{len(ds_alloc)} x {R_DS} downsampled", flush=True)

# ============================================================
# 6. Threshold sensitivity (from full region pseudobulks)
# ============================================================
print("\n" + "=" * 60)
print("6. min-cells threshold sensitivity")
print("=" * 60)

def build_pairs(threshold):
    """Return pairs DataFrame for a min-cells threshold."""
    rows = []
    for ct in cts_all:
        regs = [r for r in ct_to_regions_sup[ct]
                if gcount.get((ct, r), 0) >= threshold]
        if len(regs) * (len(regs) - 1) // 2 < 5:
            continue
        pbs = [region_pb_full[(ct, r)] for r in regs]
        for (i, j), (kn, kf, om) in zip(
                [(i, j) for i in range(len(regs)) for j in range(i + 1, len(regs))],
                pair_stats(pbs, hk_in_reduced, non_hk_in_reduced)):
            rows.append({'cell_type': ct, 'region_a': regs[i], 'region_b': regs[j],
                         'kn': kn, 'kf': kf, 'omega': om})
    df = pd.DataFrame(rows)
    if len(df) == 0:
        return df
    mu_grand = df['omega'].mean()
    mu_ct = df.groupby('cell_type')['omega'].mean().to_dict()
    mu_pair = df.groupby(['region_a', 'region_b'])['omega'].mean().to_dict()
    df['expected'] = df.apply(
        lambda r: mu_ct[r['cell_type']] * mu_pair.get((r['region_a'], r['region_b']), mu_grand) / mu_grand,
        axis=1)
    df['residual'] = df['omega'] / df['expected']
    lowest = df.groupby(['region_a', 'region_b'])['omega'].transform('min') == df['omega']
    df['lowest_in_pair'] = lowest
    def tier(r):
        if r['residual'] < 0.3 and r['omega'] < 15 and r['lowest_in_pair']:
            return 'Strong'
        if r['residual'] < 0.5 and r['omega'] < 25:
            return 'Moderate'
        if r['residual'] < 0.75 and r['omega'] < 35:
            return 'Weak'
        return 'None'
    df['tier'] = df.apply(tier, axis=1)
    return df

pairs_by_t = {}
sens_rows = []
for t in THRESHOLDS:
    t_t = time.time()
    df = build_pairs(t)
    pairs_by_t[t] = df
    cts_pass = sorted(df['cell_type'].unique())
    ct_means = df.groupby('cell_type')['omega'].mean().sort_values()
    tiers = df['tier'].value_counts().to_dict()
    astro = ct_means.get('Astrocyte', np.nan)
    berg = ct_means.get('Bergmann glia', np.nan)
    grad = astro / berg if berg and berg > 0 else np.nan
    berg_rank = int((ct_means < berg).sum()) + 1 if 'Bergmann glia' in ct_means.index else None
    sens_rows.append({
        'min_cells': t,
        'n_classes': len(cts_pass),
        'classes': '; '.join(cts_pass),
        'n_pairs': len(df),
        'n_strong': tiers.get('Strong', 0),
        'n_moderate': tiers.get('Moderate', 0),
        'n_weak': tiers.get('Weak', 0),
        'grand_mean_omega': round(df['omega'].mean(), 3),
        'lowest_omega_class': ct_means.index[0] if len(ct_means) else None,
        'bergmann_glia_omega_rank_low_to_high': berg_rank,
        'bergmann_glia_omega_mean': round(berg, 3) if berg == berg else None,
        'astrocyte_omega_mean': round(astro, 3) if astro == astro else None,
        'astro_over_bergmann_gradient': round(grad, 3) if grad == grad else None,
    })
    print(f"  t={t}: classes={len(cts_pass)}, pairs={len(df)}, "
          f"Strong={tiers.get('Strong',0)}, lowest={ct_means.index[0] if len(ct_means) else '-'}, "
          f"grad={grad:.2f} ({time.time()-t_t:.0f}s)")

sens_df = pd.DataFrame(sens_rows)
sens_df.to_csv(RESULTS_DIR / "brain_v44_threshold_sensitivity.csv", index=False)
print(f"  Saved: brain_v44_threshold_sensitivity.csv")

# per-class omega table at each threshold (for stability inspection)
ct_omega_rows = []
for t in THRESHOLDS:
    df = pairs_by_t[t]
    m = df.groupby('cell_type')['omega'].agg(['mean', 'median', 'count']).reset_index()
    m['min_cells'] = t
    ct_omega_rows.append(m)
pd.concat(ct_omega_rows).to_csv(RESULTS_DIR / "brain_v44_threshold_class_omega.csv", index=False)
print(f"  Saved: brain_v44_threshold_class_omega.csv")

# ============================================================
# 7. Validation vs authoritative observed pairs (t=20)
# ============================================================
print("\n7. Validation vs brain_bs_null_observed_pairs.csv (t=20)...")
ref = pd.read_csv(RESULTS_DIR / "brain_bs_null_observed_pairs.csv")
mine = pairs_by_t[REF_THRESHOLD]
ref_ct = ref.groupby('cell_type')['omega'].mean()
my_ct = mine.groupby('cell_type')['omega'].mean()
common = ref_ct.index.intersection(my_ct.index)
max_rel = float(np.max(np.abs(ref_ct[common] - my_ct[common]) / ref_ct[common]))
print(f"  pairs: ref={len(ref)}, mine={len(mine)}")
print(f"  class omega mean max rel diff: {max_rel:.2e}")
print(f"  grand mean: ref={ref['omega'].mean():.3f}, mine={mine['omega'].mean():.3f}")
n_strong_ref = int((ref['tier'] == 'Strong').sum()) if 'tier' in ref.columns else None
print(f"  Strong: ref={n_strong_ref}, mine={sens_rows[THRESHOLDS.index(REF_THRESHOLD)]['n_strong']}")

# ============================================================
# 8. Confound correlations (t=20, full data)
# ============================================================
print("\n" + "=" * 60)
print("8. Confound correlations (class level, t=20)")
print("=" * 60)

df20 = pairs_by_t[REF_THRESHOLD]
class_rows = []
for ct in sorted(df20['cell_type'].unique()):
    sub = df20[df20['cell_type'] == ct]
    cell_mask = (ct_names == ct) & np.isin(
        roi_names, [r for r in ct_to_regions_sup[ct]
                    if gcount.get((ct, r), 0) >= REF_THRESHOLD])
    n_cells = int(cell_mask.sum())
    class_rows.append({
        'cell_type': ct,
        'n_cells': n_cells,
        'log10_n_cells': np.log10(n_cells),
        'mean_detected_genes': float(cell_nnz[cell_mask].mean()),
        'mean_total_counts': float(cell_totals[cell_mask].mean()),
        'kn_mean': float(sub['kn'].mean()),
        'kf_mean': float(sub['kf'].mean()),
        'omega_mean': float(sub['omega'].mean()),
        'n_pairs': len(sub),
    })
class_df = pd.DataFrame(class_rows)

corr_rows = []
for metric in ['kn_mean', 'omega_mean']:
    for conf in ['log10_n_cells', 'mean_detected_genes', 'mean_total_counts']:
        rho, p_s = spearmanr(class_df[metric], class_df[conf])
        r_p, p_p = pearsonr(class_df[metric], class_df[conf])
        corr_rows.append({'metric': metric, 'confound': conf,
                          'spearman_rho': round(rho, 4), 'spearman_p': f"{p_s:.4g}",
                          'pearson_r': round(r_p, 4), 'pearson_p': f"{p_p:.4g}",
                          'n_classes': len(class_df)})
        print(f"  {metric} vs {conf}: rho={rho:.3f} (p={p_s:.3g}), "
              f"r={r_p:.3f} (p={p_p:.3g})")
corr_df = pd.DataFrame(corr_rows)
corr_df.to_csv(RESULTS_DIR / "brain_v44_confound_correlations.csv", index=False)
print(f"  Saved: brain_v44_confound_correlations.csv")

# ============================================================
# 9. Downsample to smallest class (R=20 replicates)
# ============================================================
print("\n" + "=" * 60)
print(f"9. Downsample all classes to {min_class_total} cells x {R_DS} reps")
print("=" * 60)

# classes in the t=20 analysis set
cts_t20 = sorted(df20['cell_type'].unique())
rep_rows = []
class_ds_kn = {ct: [] for ct in cts_t20}
class_ds_om = {ct: [] for ct in cts_t20}
grad_ds = []
for rep in range(R_DS):
    om_means = {}
    for ct in cts_t20:
        regs = [r for r in ct_to_regions_sup[ct]
                if gcount.get((ct, r), 0) >= REF_THRESHOLD]
        pbs = [region_pb_ds[rep][(ct, r)] for r in regs]
        stats = pair_stats(pbs, hk_in_reduced, non_hk_in_reduced)
        kn_m = float(np.mean([s[0] for s in stats]))
        om_m = float(np.mean([s[2] for s in stats]))
        class_ds_kn[ct].append(kn_m)
        class_ds_om[ct].append(om_m)
        om_means[ct] = om_m
    g = om_means.get('Astrocyte', np.nan) / om_means.get('Bergmann glia', np.nan)
    grad_ds.append(g)
    rep_rows.append({'rep': rep, 'astro_over_bergmann_gradient': g,
                     **{f'omega__{ct}': om_means[ct] for ct in cts_t20}})

rep_df = pd.DataFrame(rep_rows)
rep_df.to_csv(RESULTS_DIR / "brain_v44_downsample_replicates.csv", index=False)
print(f"  Saved: brain_v44_downsample_replicates.csv")

# class-level downsampled stats + rank correlation vs full
for ct in cts_t20:
    class_df.loc[class_df['cell_type'] == ct, 'kn_mean_downsampled'] = np.mean(class_ds_kn[ct])
    class_df.loc[class_df['cell_type'] == ct, 'omega_mean_downsampled'] = np.mean(class_ds_om[ct])
    class_df.loc[class_df['cell_type'] == ct, 'omega_downsampled_sd'] = np.std(class_ds_om[ct])

rho_kn, p_kn = spearmanr(class_df['kn_mean'], class_df['kn_mean_downsampled'])
rho_om, p_om = spearmanr(class_df['omega_mean'], class_df['omega_mean_downsampled'])
print(f"  Class rank Spearman (full vs downsampled): k_n rho={rho_kn:.3f} (p={p_kn:.3g}), "
      f"omega rho={rho_om:.3f} (p={p_om:.3g})")

grad_full = (class_df.loc[class_df['cell_type'] == 'Astrocyte', 'omega_mean'].iloc[0] /
             class_df.loc[class_df['cell_type'] == 'Bergmann glia', 'omega_mean'].iloc[0])
grad_ds = np.array(grad_ds)
print(f"  Astrocyte/Bergmann-glia gradient: full={grad_full:.2f}, "
      f"downsampled mean={grad_ds.mean():.2f} +/- {grad_ds.std():.2f} "
      f"[{np.percentile(grad_ds, 2.5):.2f}, {np.percentile(grad_ds, 97.5):.2f}]")

class_df.to_csv(RESULTS_DIR / "brain_v44_class_confound.csv", index=False)
print(f"  Saved: brain_v44_class_confound.csv")

# downsampled omega ranking (is Bergmann glia still lowest?)
ds_rank = class_df[['cell_type', 'omega_mean', 'omega_mean_downsampled']].sort_values(
    'omega_mean_downsampled')
print("\n  Downsampled class omega ranking (low to high):")
for _, r in ds_rank.iterrows():
    print(f"    {r['cell_type']}: {r['omega_mean_downsampled']:.2f} "
          f"(full {r['omega_mean']:.2f})")

# ============================================================
# 10. Run metadata
# ============================================================
meta = {
    'seed': RANDOM_SEED,
    'downsample_replicates': R_DS,
    'downsample_target_cells': int(min_class_total),
    'thresholds': THRESHOLDS,
    'reference_threshold': REF_THRESHOLD,
    'runtime_sec': round(time.time() - _t0_all, 1),
    'validation_max_rel_diff_class_omega': max_rel,
    'rank_spearman_kn_full_vs_downsampled': [float(rho_kn), float(p_kn)],
    'rank_spearman_omega_full_vs_downsampled': [float(rho_om), float(p_om)],
    'gradient_full': float(grad_full),
    'gradient_downsampled_mean': float(grad_ds.mean()),
    'gradient_downsampled_sd': float(grad_ds.std()),
    'gradient_downsampled_ci95': [float(np.percentile(grad_ds, 2.5)),
                                  float(np.percentile(grad_ds, 97.5))],
}
with open(RESULTS_DIR / "brain_v44_run_metadata.json", 'w') as jf:
    json.dump(meta, jf, indent=2)
print(f"\n  Saved: brain_v44_run_metadata.json")
print(f"\nTotal runtime: {time.time()-_t0_all:.0f}s")
print("DONE")
