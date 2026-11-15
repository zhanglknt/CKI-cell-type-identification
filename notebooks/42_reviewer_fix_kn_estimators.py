"""
Reviewer fix C-C (#964): is the 6.88x per-class omega gradient a k_n
denominator artifact?

Design
------
For each of the 10 non-neuronal brain classes, rebuild the region
pseudobulks exactly as in 08d (sample-mean weighted, norm 1e4, log1p,
same HK + top-5000 non-HK HVG gene set), and record k_f, k_n and omega
for EVERY cross-region pair.

Then:
  (1) per-CT means of k_f, k_n, omega (per-pair k_n)  [reproduces 08d]
  (2) global-k_n estimator: omega_g = k_f / kn_global, where kn_global is
      the grand mean of k_n across all pairs -> per-CT mean omega_g
  (3) CT-level k_n estimator: omega_ct = k_f / mean_kn(CT) -> per-CT mean
  (4) k_f-only and k_n-only per-CT gradients
  (5) Spearman consistency between all orderings + gradient extremes
      (Astrocyte vs Bergmann glia) under each estimator
  (6) k_n cross-pair CV per CT

Usage
-----
    ./cki_env/Scripts/python.exe -u notebooks/42_reviewer_fix_kn_estimators.py
"""

import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import h5py
from scipy.sparse import csr_matrix
from scipy.stats import spearmanr
from cki.core import js_divergence

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)


def extract_csr_from_backed(h5_path, cell_indices, keep_global, n_genes_total,
                            chunk_size=20000):
    n_cells = len(cell_indices)
    n_keep = len(keep_global)
    if n_cells == 0:
        return csr_matrix((0, n_keep), dtype=np.float32)
    gene_map = np.full(n_genes_total, -1, dtype=np.int32)
    gene_map[keep_global] = np.arange(n_keep, dtype=np.int32)
    sort_order = np.argsort(cell_indices, kind='stable')
    sorted_cells = cell_indices[sort_order]
    unsort = np.empty(n_cells, dtype=np.int64)
    unsort[sort_order] = np.arange(n_cells)
    new_data_list = [None] * n_cells
    new_idx_list = [None] * n_cells
    cell_nnz_sorted = np.zeros(n_cells, dtype=np.int64)
    with h5py.File(h5_path, 'r') as f:
        X = f['X']
        indptr_full = X['indptr'][:]
        n_chunks = (n_cells + chunk_size - 1) // chunk_size
        for chunk_i in range(n_chunks):
            cs = chunk_i * chunk_size
            ce = min(cs + chunk_size, n_cells)
            chunk_cells = sorted_cells[cs:ce]
            d_start = int(indptr_full[chunk_cells[0]])
            d_end = int(indptr_full[chunk_cells[-1] + 1])
            if d_end > d_start:
                chunk_indices = X['indices'][d_start:d_end]
                chunk_data = X['data'][d_start:d_end]
                chunk_mapped = gene_map[chunk_indices]
                chunk_keep = chunk_mapped >= 0
            else:
                chunk_mapped = np.array([], dtype=np.int32)
                chunk_keep = np.array([], dtype=bool)
                chunk_data = np.array([], dtype=X['data'].dtype)
            for ci in range(cs, ce):
                orig_pos = int(sort_order[ci])   # FIX (was unsort[ci])
                g_row = int(sorted_cells[ci])
                r_start = int(indptr_full[g_row]) - d_start
                r_end = int(indptr_full[g_row + 1]) - d_start
                if r_start == r_end:
                    continue
                km = chunk_keep[r_start:r_end]
                nk = int(km.sum())
                cell_nnz_sorted[ci] = nk
                if nk > 0:
                    new_data_list[orig_pos] = chunk_data[r_start:r_end][km]
                    new_idx_list[orig_pos] = chunk_mapped[r_start:r_end][km]
    cell_nnz_orig = np.zeros(n_cells, dtype=np.int64)
    cell_nnz_orig[sort_order] = cell_nnz_sorted   # FIX (was unsort)
    new_indptr = np.zeros(n_cells + 1, dtype=np.int64)
    np.cumsum(cell_nnz_orig, out=new_indptr[1:])
    nnz = int(new_indptr[-1])
    if nnz == 0:
        return csr_matrix((n_cells, n_keep), dtype=np.float32)
    all_data = [d for d in new_data_list if d is not None]
    all_idx = [d for d in new_idx_list if d is not None]
    new_data = np.concatenate(all_data).astype(np.float64)
    new_indices_arr = np.concatenate(all_idx)
    return csr_matrix((new_data, new_indices_arr, new_indptr),
                      shape=(n_cells, n_keep))


def pair_kf_kn(pb_a, pb_b, hk_idx, non_hk_idx, n_top=200):
    """k_f, k_n for one pseudobulk pair (08d convention)."""
    kn = js_divergence(pb_a[hk_idx], pb_b[hk_idx])
    ad = np.abs(pb_a - pb_b)
    ad_nh = ad[non_hk_idx]
    top_n = min(n_top, len(ad_nh))
    top_local = np.argpartition(ad_nh, -top_n)[-top_n:]
    tg = non_hk_idx[top_local]
    kf = js_divergence(pb_a[tg], pb_b[tg])
    return kf, kn


def logpb_from_mean(raw_mean):
    """raw mean vector -> norm 1e4 -> log1p (08d pseudobulk convention)."""
    tot = raw_mean.sum()
    m = raw_mean / tot * 1e4 if tot > 0 else raw_mean
    return np.log1p(m).astype(np.float64)


def main():
    MIN_NUCLEI = 20
    MIN_REGION_N = 50
    N_TOP_KF = 200
    N_HVG = 5000
    ct_col = 'supercluster_term'
    region_col = 'roi'
    sample_col = 'sample_id'

    print("=" * 60)
    print("1. Loading HK genes...")
    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().astype(str))

    print("2. Opening Siletti (backed h5py)...")
    f = h5py.File(BRAIN_FILE, 'r')
    X = f['X']
    indptr_full = X['indptr'][:]
    N_CELLS = indptr_full.shape[0] - 1

    var_gene = None
    if 'Gene' in f['var']:
        vg = f['var']['Gene']
        if isinstance(vg, h5py.Dataset):
            var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
        elif isinstance(vg, h5py.Group) and 'categories' in vg:
            categories = [x.decode() if isinstance(x, bytes) else str(x)
                          for x in vg['categories'][:]]
            codes = vg['codes'][:]
            var_gene = [categories[c] if c >= 0 else np.nan for c in codes]
    if var_gene is None:
        idx_name = f['var'].attrs.get('_index', None)
        if idx_name and idx_name in f['var']:
            vg = f['var'][idx_name]
            var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
    N_GENES = len(var_gene)
    print(f"  Shape: ({N_CELLS}, {N_GENES})")

    obs = f['obs']
    def read_codes(name):
        g = obs[name]
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g['categories'][:]]
        return g['codes'][:], cats
    ct_codes, ct_cats = read_codes(ct_col)
    roi_codes, roi_cats = read_codes(region_col)
    samp_codes, _ = read_codes(sample_col)
    ct_names = np.array(ct_cats)[ct_codes]
    roi_names = np.array(roi_cats)[roi_codes]

    print("3. Global gene means (HVG selection, same as 08d)...")
    t0 = time.time()
    gene_sums = np.zeros(N_GENES, dtype=np.float64)
    BATCH = 50000
    for start in range(0, N_CELLS, BATCH):
        end = min(start + BATCH, N_CELLS)
        lo, hi = int(indptr_full[start]), int(indptr_full[end])
        np.add.at(gene_sums, X['indices'][lo:hi], X['data'][lo:hi])
    gene_means = gene_sums / N_CELLS
    print(f"  Done in {time.time()-t0:.0f}s")

    hk_global = np.array(sorted({i for i, sym in enumerate(var_gene)
                                 if pd.notna(sym) and sym in hk_human}), dtype=int)
    non_hk_mask = np.ones(N_GENES, dtype=bool)
    non_hk_mask[hk_global] = False
    non_hk_means = gene_means.copy()
    non_hk_means[~non_hk_mask] = -np.inf
    hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
    keep_global = np.sort(np.union1d(hk_global, hvg_global))
    is_hk_in_keep = np.isin(keep_global, hk_global)
    hk_in_reduced = np.where(is_hk_in_keep)[0]
    non_hk_in_reduced = np.where(~is_hk_in_keep)[0]
    print(f"  HK matched: {len(hk_global)}; reduced set: {len(keep_global)} genes")

    # filter groups (same as 08d)
    df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names, 'sample': samp_codes})
    groups = df_meta.groupby(['roi', 'ct']).size().reset_index(name='count')
    groups_ok = groups[groups['count'] >= MIN_NUCLEI]
    region_counts = df_meta['roi'].value_counts()
    regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
    groups_ok = groups_ok[groups_ok['roi'].isin(regions_ok)]
    cts_present = sorted(groups_ok['ct'].unique())
    print(f"  CTs: {len(cts_present)}: {cts_present}")

    ct_to_regions = {}
    for _, row in groups_ok.iterrows():
        ct_to_regions.setdefault(row['ct'], [])
        if row['roi'] not in ct_to_regions[row['ct']]:
            ct_to_regions[row['ct']].append(row['roi'])

    # ============================================================
    # Per-CT: all-pair kf/kn  +  split-half calibration (C-B, brain part)
    # ============================================================
    RNG = np.random.RandomState(12345)
    B_SPLIT = 50
    MIN_SPLIT_REGION_CELLS = 200
    split_records = []   # (cell_type, region, split_b, omega, kf, kn)
    all_pair_rows = []
    for ct in cts_present:
        regions = sorted(ct_to_regions[ct])
        n_r = len(regions)
        n_pairs = n_r * (n_r - 1) // 2
        if n_pairs < 5:
            continue
        t_ct = time.time()
        print(f"\n  --- {ct} ({n_r} regions, {n_pairs} pairs) ---")

        ct_bool = (ct_names == ct) & np.isin(roi_names, regions)
        ct_global_idx = np.where(ct_bool)[0]
        region_of_cell = roi_names[ct_global_idx]
        samp_of_cell = samp_codes[ct_global_idx]
        sort_idx = np.argsort(region_of_cell)
        region_sorted = region_of_cell[sort_idx]
        samp_sorted = samp_of_cell[sort_idx]
        idx_sorted = ct_global_idx[sort_idx]

        X_ct = extract_csr_from_backed(str(BRAIN_FILE), idx_sorted,
                                        keep_global, N_GENES)
        print(f"    Extracted {X_ct.shape[0]} cells "
              f"({X_ct.nnz/1e6:.0f}M nnz, {time.time()-t_ct:.0f}s)")

        # ---- split-half calibration (C-B, brain): top-3 regions by n ----
        region_sizes_now = {}
        for rg in np.unique(region_sorted):
            region_sizes_now[rg] = int(np.sum(region_sorted == rg))
        top_regions = sorted(region_sizes_now.items(), key=lambda kv: -kv[1])[:3]
        for rg, n_rg in top_regions:
            if n_rg < MIN_SPLIT_REGION_CELLS:
                continue
            rg_rows = np.where(region_sorted == rg)[0]
            for b in range(B_SPLIT):
                perm = RNG.permutation(n_rg)
                half = n_rg // 2
                rA, rB = rg_rows[perm[:half]], rg_rows[perm[half:2*half]]
                pbA = logpb_from_mean(np.asarray(X_ct[rA].mean(axis=0)).flatten())
                pbB = logpb_from_mean(np.asarray(X_ct[rB].mean(axis=0)).flatten())
                kf_s, kn_s = pair_kf_kn(pbA, pbB, hk_in_reduced, non_hk_in_reduced)
                split_records.append({
                    'cell_type': ct, 'region': rg, 'split': b,
                    'kf': kf_s, 'kn': kn_s,
                    'omega': kf_s / kn_s if kn_s > 1e-15 else np.inf})
        if any(s['cell_type'] == ct for s in split_records):
            ct_splits = [s['omega'] for s in split_records
                         if s['cell_type'] == ct]
            print(f"    Split-half ({len(top_regions)} regions x "
                  f"{B_SPLIT} splits): mean omega="
                  f"{np.mean(ct_splits):.3f}")

        region_order = regions
        uniq_samples, sample_inv = np.unique(samp_sorted, return_inverse=True)
        n_samples = len(uniq_samples)
        sample_rows = [np.where(sample_inv == s)[0] for s in range(n_samples)]
        sample_weights = np.array([len(r) for r in sample_rows], dtype=np.float64)
        sample_region_idx = np.array(
            [region_order.index(region_sorted[r[0]]) for r in sample_rows], dtype=int)
        sample_means = np.zeros((n_samples, X_ct.shape[1]), dtype=np.float64)
        for s in range(n_samples):
            if len(sample_rows[s]) > 0:
                sample_means[s] = np.asarray(X_ct[sample_rows[s]].mean(axis=0)).flatten()

        # observed region pseudobulks (08d convention)
        pbs = []
        for r in range(len(region_order)):
            mask = sample_region_idx == r
            if not mask.any():
                pbs.append(None)
                continue
            w = sample_weights[mask]
            pb_raw = (sample_means[mask] * w[:, None]).sum(axis=0) / w.sum()
            tot = pb_raw.sum()
            pb_norm = pb_raw / tot * 1e4 if tot > 0 else pb_raw
            pbs.append(np.log1p(pb_norm).astype(np.float64))

        for i in range(n_r):
            for j in range(i + 1, n_r):
                if pbs[i] is None or pbs[j] is None:
                    continue
                kf, kn = pair_kf_kn(pbs[i], pbs[j], hk_in_reduced, non_hk_in_reduced)
                all_pair_rows.append({
                    'cell_type': ct, 'region_a': region_order[i],
                    'region_b': region_order[j],
                    'kf': kf, 'kn': kn,
                    'omega': kf / kn if kn > 1e-15 else np.inf})
        del X_ct, sample_means, pbs
        gc.collect()

    f.close()

    pairs_df = pd.DataFrame(all_pair_rows)
    out_pair = RESULTS_DIR / 'reviewer_brain_pair_kf_kn.csv'
    pairs_df.to_csv(out_pair, index=False)
    print(f"\nSaved {len(pairs_df)} pairs -> {out_pair}")

    # ============================================================
    # Aggregation
    # ============================================================
    print("\n" + "=" * 60)
    print("Per-CT aggregation")
    print("=" * 60)
    agg = pairs_df.groupby('cell_type').agg(
        n_pairs=('omega', 'size'),
        kf_mean=('kf', 'mean'),
        kn_mean=('kn', 'mean'),
        kn_cv=('kn', lambda s: np.std(s) / np.mean(s)),
        omega_mean_perpair_kn=('omega', 'mean')).reset_index()

    kn_global = float(pairs_df['kn'].mean())
    print(f"\nGrand mean k_n (all pairs, all CTs) = {kn_global:.4f}")

    agg['omega_mean_global_kn'] = agg['kf_mean'] / kn_global
    agg['omega_mean_ct_kn'] = agg['kf_mean'] / agg['kn_mean']
    # per-pair omega with global kn then per-CT mean (weights pairs equally)
    pairs_df['omega_g'] = pairs_df['kf'] / kn_global
    agg2 = pairs_df.groupby('cell_type')['omega_g'].mean().rename('omega_pairmean_global_kn')
    agg = agg.merge(agg2, on='cell_type')
    agg = agg.sort_values('omega_mean_perpair_kn', ascending=False)

    pooled_ref = pd.read_csv(RESULTS_DIR / 'brain_bs_null_ct_test.csv')[
        ['cell_type', 'omega_mean']].rename(columns={'omega_mean': 'omega_mean_08d'})
    agg = agg.merge(pooled_ref, on='cell_type')
    agg.to_csv(RESULTS_DIR / 'reviewer_kn_estimator_consistency.csv', index=False)

    cols = ['cell_type', 'n_pairs', 'kf_mean', 'kn_mean', 'kn_cv',
            'omega_mean_perpair_kn', 'omega_mean_08d',
            'omega_mean_global_kn', 'omega_mean_ct_kn']
    print(agg[cols].to_string(index=False,
          float_format=lambda x: f"{x:.3f}"))

    # Spearman consistency between orderings
    print("\n" + "=" * 60)
    print("Ordering consistency (Spearman rho between per-CT means)")
    print("=" * 60)
    orderings = {
        'omega (per-pair kn)': agg['omega_mean_perpair_kn'],
        'omega (global kn)': agg['omega_mean_global_kn'],
        'omega (pair-mean, global kn)': agg['omega_pairmean_global_kn'],
        'omega (CT-level kn)': agg['omega_mean_ct_kn'],
        'k_f only': agg['kf_mean'],
        'k_n only': agg['kn_mean'],
    }
    keys = list(orderings)
    print(f"{'':34s}" + "".join(f"{k[:14]:>16s}" for k in keys))
    for ka in keys:
        row = f"{ka[:33]:34s}"
        for kb in keys:
            r, _ = spearmanr(orderings[ka], orderings[kb])
            row += f"{r:>16.3f}"
        print(row)

    # gradient extremes
    print("\n" + "=" * 60)
    print("Gradient extremes (Astrocyte / Bergmann glia)")
    print("=" * 60)
    for name, col in [('omega (per-pair kn)', 'omega_mean_perpair_kn'),
                      ('omega (global kn)', 'omega_mean_global_kn'),
                      ('omega (CT-level kn)', 'omega_mean_ct_kn'),
                      ('k_f only', 'kf_mean'),
                      ('k_n only', 'kn_mean')]:
        sub = agg.set_index('cell_type')[col]
        if 'Astrocyte' in sub.index and 'Bergmann glia' in sub.index:
            print(f"  {name:26s}: {sub['Astrocyte']:.3f} / {sub['Bergmann glia']:.3f} "
                  f"= {sub['Astrocyte']/sub['Bergmann glia']:.2f}x")

    # ============================================================
    # Split-half calibration summary (C-B, brain part)
    # ============================================================
    print("\n" + "=" * 60)
    print("Split-half calibration (brain, scheme-matched to 08d pipeline)")
    print("=" * 60)
    sdf = pd.DataFrame(split_records)
    sdf.to_csv(RESULTS_DIR / 'reviewer_brain_splithalf_raw.csv', index=False)
    pop_mean = sdf.groupby(['cell_type', 'region'])['omega'].mean().reset_index()
    print(pop_mean.to_string(index=False))
    all_sh = sdf['omega'].values
    pop_means = pop_mean['omega'].values
    grand_sh = float(np.mean(pop_means))
    # Population-level bootstrap (the 29 population means are the exchangeability
    # unit, matching the Methods description). Resampling the 1,450 split-level
    # values would treat the 50 highly correlated within-population splits as
    # independent and understate the CI by roughly 3x.
    boot = [float(np.mean(RNG.choice(pop_means, size=len(pop_means), replace=True)))
            for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print(f"\n  Brain split-half baseline: mean omega = {grand_sh:.2f} "
          f"(95% bootstrap CI [{lo:.2f}, {hi:.2f}], "
          f"n = {len(all_sh)} splits, {len(pop_mean)} populations; "
          f"CI resamples the {len(pop_means)} population means)")
    print(f"  Mouse SmartSeq2 reference (manuscript): 6.67 [4.12, 9.33]")
    with open(RESULTS_DIR / 'reviewer_brain_splithalf_summary.txt', 'w') as fh:
        fh.write(f"brain_split_half_mean_omega\t{grand_sh:.4f}\n")
        fh.write(f"brain_split_half_ci95\t[{lo:.4f}, {hi:.4f}]\n")
        fh.write(f"n_splits\t{len(all_sh)}\n")
        fh.write(f"n_populations\t{len(pop_mean)}\n")
        fh.write(f"B_per_population\t{B_SPLIT}\n")
        fh.write(f"min_region_cells\t{MIN_SPLIT_REGION_CELLS}\n")

    print("\nSaved -> results/reviewer_kn_estimator_consistency.csv")
    print("DONE.")


if __name__ == '__main__':
    main()
