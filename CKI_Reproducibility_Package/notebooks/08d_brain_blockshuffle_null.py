"""
CKI Brain Block-Shuffle Null Analysis (08d)
===========================================
Implements a strict block-shuffle permutation null for the brain regional
CKI analysis, addressing Critical issue C1 of the v5 expert review.

Design
------
- Blocks = 10x libraries (obs['sample_id']). Every sample is nested within
  exactly one brain region, so permuting *sample* labels across regions
  preserves within-library (spatial / technical) correlation while removing
  regional structure at the block level. This is the "block-shuffle null
  preserving the cell-type x region joint distribution" requested by the
  reviewers (an alternative to the anti-conservative per-cell shuffle).
- Gene set: HRT Atlas HK genes + top-5000 non-HK HVG by mean expression,
  used identically for observed and null omega (v3 bootstrap convention).
- Per-cell-type (CT):
    1. Observed: region pseudobulks (raw mean -> norm 1e4 -> log1p) ->
       all same-CT cross-region pair omega.
    2. Block-shuffle null (B = 1000): permute sample -> region labels
       (preserving the observed per-region sample-count multiset),
       recompute region pseudobulks as weighted means of precomputed
       sample raw means, recompute all pair omega.
- Outputs (into RESULTS_DIR):
    brain_bs_null_observed_pairs.csv   observed pairs + multiplicative model
    brain_bs_null_pairs_<CT>.npy       null pair-omega matrices (pairs x B)
    brain_bs_null_ct_test.csv          per-CT observed-vs-null summary
    brain_bs_null_manifest.json        run metadata

Usage
-----
    python 08d_brain_blockshuffle_null.py [--max-perm N] [--observed-only]
"""

import sys, os, time, gc, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import h5py
from scipy.sparse import csr_matrix, issparse
from cki.core import js_divergence

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)


# ============================================================
# Backed CSR extraction (from 08c v3, int16-safe)
# ============================================================
def extract_csr_from_backed(h5_path, cell_indices, keep_global, n_genes_total,
                            chunk_size=20000):
    """
    Extract CSR matrix for selected cells, keeping only keep_global genes.
    Chunked h5py batch reads; handles int16/float32 data dtypes.
    """
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
                orig_pos = int(sort_order[ci])   # FIX (was unsort[ci]): place row at its original index
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
            if n_chunks > 5 and (chunk_i + 1) % 5 == 0:
                print(f"      Extraction chunk {chunk_i+1}/{n_chunks} "
                      f"({ce}/{n_cells} sorted cells)")

    cell_nnz_orig = np.zeros(n_cells, dtype=np.int64)
    cell_nnz_orig[sort_order] = cell_nnz_sorted   # FIX (was unsort): scatter to original order
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


def pair_omegas(pbs, n_pairs, hk_idx, non_hk_idx, n_top=200):
    """Compute all upper-triangle pair omegas from region pseudobulks."""
    n = len(pbs)
    omegas = np.empty(n_pairs, dtype=np.float64)
    k = 0
    for i in range(n):
        pi = pbs[i]
        for j in range(i + 1, n):
            pj = pbs[j]
            kn = js_divergence(pi[hk_idx], pj[hk_idx])
            ad = np.abs(pi - pj)
            ad_nh = ad[non_hk_idx]
            top_n = min(n_top, len(ad_nh))
            top_local = np.argpartition(ad_nh, -top_n)[-top_n:]
            top_local = top_local[np.argsort(ad_nh[top_local])[::-1]]
            tg = non_hk_idx[top_local]
            kf = js_divergence(pi[tg], pj[tg])
            omegas[k] = kf / kn if kn > 1e-15 else np.inf
            k += 1
    return omegas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-perm', type=int, default=1000)
    ap.add_argument('--observed-only', action='store_true',
                    help='compute observed landscape and stop')
    ap.add_argument('--ct', default=None, help='restrict to one cell type')
    ap.add_argument('--resume', action='store_true',
                    help='reuse existing null matrix (pairs x B) for CTs already run')
    args = ap.parse_args()

    B_PERM = args.max_perm
    RANDOM_SEED = 42
    MIN_NUCLEI = 20
    MIN_REGION_N = 50
    N_TOP_KF = 200
    N_HVG = 5000
    SILETTI_PATH = BRAIN_FILE
    HK_FILE_REF = HK_FILE
    ct_col = 'supercluster_term'
    region_col = 'roi'
    sample_col = 'sample_id'

    rng = np.random.RandomState(RANDOM_SEED)

    # ============================================================
    # 1. HK genes
    # ============================================================
    print("=" * 60)
    print("1. Loading HK genes from HRT Atlas...")
    hk_df = pd.read_csv(HK_FILE_REF, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().astype(str))
    print(f"  HRT Atlas: {len(hk_human)} human HK genes")

    # ============================================================
    # 2. Open backed + read metadata arrays via h5py
    # ============================================================
    print("\n2. Opening Siletti (backed h5py)...")
    t0 = time.time()
    f = h5py.File(SILETTI_PATH, 'r')
    X = f['X']
    indptr_full = X['indptr'][:]
    N_CELLS = indptr_full.shape[0] - 1
    N_GENES = f['var'].attrs.get('_index', None)
    # var gene symbols (Gene column preferred; else var index attr)
    var_gene = None
    if 'Gene' in f['var']:
        vg = f['var']['Gene']
        if isinstance(vg, h5py.Dataset):
            var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
        elif isinstance(vg, h5py.Group) and 'categories' in vg:
            # AnnData categorical stored as categories + codes
            categories = [x.decode() if isinstance(x, bytes) else str(x)
                          for x in vg['categories'][:]]
            codes = vg['codes'][:]
            var_gene = [categories[c] if c >= 0 else np.nan for c in codes]
    if var_gene is None:
        idx_name = f['var'].attrs.get('_index', None)
        if idx_name and idx_name in f['var']:
            vg = f['var'][idx_name]
            var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
    if var_gene is None:
        raise RuntimeError("Could not read gene symbols from var group")
    N_GENES = len(var_gene)
    print(f"  Shape: ({N_CELLS}, {N_GENES})")

    # obs codes
    obs = f['obs']
    def read_codes(name):
        g = obs[name]
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g['categories'][:]]
        codes = g['codes'][:]
        return codes, cats
    ct_codes, ct_cats = read_codes(ct_col)
    roi_codes, roi_cats = read_codes(region_col)
    samp_codes, _ = read_codes(sample_col)
    ct_names = np.array(ct_cats)[ct_codes]
    roi_names = np.array(roi_cats)[roi_codes]

    # HK gene -> global indices
    hk_global = np.array(sorted({i for i, sym in enumerate(var_gene)
                                 if pd.notna(sym) and sym in hk_human}), dtype=int)
    print(f"  Matched HK genes: {len(hk_global)}")

    # ============================================================
    # 3. Global gene means for HVG selection (non-HK)
    # ============================================================
    print("\n3. Computing global gene means (HVG selection)...")
    t0 = time.time()
    gene_sums = np.zeros(N_GENES, dtype=np.float64)
    BATCH = 50000
    for start in range(0, N_CELLS, BATCH):
        end = min(start + BATCH, N_CELLS)
        rows = np.arange(start, end)
        # batch row sums via slice of indptr
        lo, hi = int(indptr_full[start]), int(indptr_full[end])
        data_batch = X['data'][lo:hi]
        idx_batch = X['indices'][lo:hi]
        # scatter-add into gene sums
        np.add.at(gene_sums, idx_batch, data_batch)
    gene_means = gene_sums / N_CELLS
    print(f"  Means computed in {time.time()-t0:.0f}s")
    non_hk_mask = np.ones(N_GENES, dtype=bool)
    non_hk_mask[hk_global] = False
    non_hk_means = gene_means.copy()
    non_hk_means[~non_hk_mask] = -np.inf
    hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
    keep_global = np.sort(np.union1d(hk_global, hvg_global))
    is_hk_in_keep = np.isin(keep_global, hk_global)
    hk_in_reduced = np.where(is_hk_in_keep)[0]
    non_hk_in_reduced = np.where(~is_hk_in_keep)[0]
    print(f"  Reduced set: {len(keep_global)} genes "
          f"(HK={len(hk_in_reduced)} + HVG={len(non_hk_in_reduced)})")

    # ============================================================
    # 4. Filter groups
    # ============================================================
    print("\n4. Filtering groups...")
    df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names, 'sample': samp_codes})
    groups = df_meta.groupby(['roi', 'ct']).size().reset_index(name='count')
    groups_ok = groups[groups['count'] >= MIN_NUCLEI]
    region_counts = df_meta['roi'].value_counts()
    regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
    groups_ok = groups_ok[groups_ok['roi'].isin(regions_ok)]
    cts_present = sorted(groups_ok['ct'].unique())
    if args.ct:
        cts_present = [c for c in cts_present if c == args.ct]
    print(f"  Groups passing: {len(groups_ok)} | CTs: {len(cts_present)}: {cts_present}")

    ct_to_regions = {}
    for _, row in groups_ok.iterrows():
        ct_to_regions.setdefault(row['ct'], [])
        if row['roi'] not in ct_to_regions[row['ct']]:
            ct_to_regions[row['ct']].append(row['roi'])
    for ct in cts_present:
        n_r = len(ct_to_regions[ct])
        print(f"    {ct}: {n_r} regions, {n_r*(n_r-1)//2} pairs")

    # ============================================================
    # 5. Per-CT analysis
    # ============================================================
    print("\n" + "=" * 60)
    print(f"5. Per-CT observed + block-shuffle null (B={B_PERM})")
    print("=" * 60)

    all_pair_rows = []
    ct_test_rows = []
    manifest = {'seed': RANDOM_SEED, 'B': B_PERM, 'blocks': 'sample_id',
                'gene_set': f'HK_{len(hk_in_reduced)}_HVG{len(non_hk_in_reduced)}',
                'observed_only': args.observed_only, 'cts': {}}

    for ct in cts_present:
        regions = sorted(ct_to_regions[ct])
        n_r = len(regions)
        n_pairs = n_r * (n_r - 1) // 2
        if n_pairs < 5:
            continue
        t_ct = time.time()
        print(f"\n  --- {ct} ({n_r} regions, {n_pairs} pairs) ---")

        # 5a. cell indices + metadata for this CT
        ct_bool = (ct_names == ct) & np.isin(roi_names, regions)
        ct_global_idx = np.where(ct_bool)[0]
        region_of_cell = roi_names[ct_global_idx]
        samp_of_cell = samp_codes[ct_global_idx]
        sort_idx = np.argsort(region_of_cell)
        region_sorted = region_of_cell[sort_idx]
        samp_sorted = samp_of_cell[sort_idx]
        idx_sorted = ct_global_idx[sort_idx]

        # 5b. extract CSR (rows in sorted-by-region order)
        t0 = time.time()
        X_ct = extract_csr_from_backed(str(SILETTI_PATH), idx_sorted,
                                       keep_global, N_GENES)
        n_cells = X_ct.shape[0]
        print(f"    Extracted {n_cells} cells x {len(keep_global)} genes "
              f"({X_ct.nnz/1e6:.0f}M nnz, {time.time()-t0:.0f}s)")

        # 5c. region boundaries
        region_order = regions
        region_sizes = {}
        region_starts = {}
        cum = 0
        for region in region_order:
            n = int(np.sum(region_sorted == region))
            region_sizes[region] = n
            region_starts[region] = cum
            cum += n

        # 5d. sample blocks
        uniq_samples, sample_inv = np.unique(samp_sorted, return_inverse=True)
        n_samples = len(uniq_samples)
        # sample -> its cells (rows in CSR)
        sample_rows = [np.where(sample_inv == s)[0] for s in range(n_samples)]
        sample_weights = np.array([len(r) for r in sample_rows], dtype=np.float64)
        # sample -> observed region code (index into region_order)
        sample_region_idx = np.array(
            [region_order.index(region_sorted[r[0]]) for r in sample_rows],
            dtype=int)
        # sample raw means (weighted by cell counts implicitly later)
        sample_means = np.zeros((n_samples, X_ct.shape[1]), dtype=np.float64)
        for s in range(n_samples):
            if len(sample_rows[s]) > 0:
                sample_means[s] = np.asarray(X_ct[sample_rows[s]].mean(axis=0)).flatten()
        print(f"    Blocks (samples): {n_samples}, "
              f"median cells/sample={np.median(sample_weights):.0f}")

        # 5e. observed region pseudobulks
        def region_pbs_from_samples(assign_idx, weights, means):
            """assign_idx: sample -> region index. Return list of pbs."""
            pbs = []
            for r in range(len(region_order)):
                mask = assign_idx == r
                if not mask.any():
                    pbs.append(np.zeros(means.shape[1], dtype=np.float64))
                    continue
                w = weights[mask]
                pb_raw = (means[mask] * w[:, None]).sum(axis=0) / w.sum()
                tot = pb_raw.sum()
                pb_norm = pb_raw / tot * 1e4 if tot > 0 else pb_raw
                pbs.append(np.log1p(pb_norm).astype(np.float64))
            return pbs

        obs_pbs = region_pbs_from_samples(sample_region_idx,
                                          sample_weights, sample_means)
        obs_omegas = pair_omegas(obs_pbs, n_pairs, hk_in_reduced, non_hk_in_reduced)
        obs_mean = float(np.mean(obs_omegas))
        obs_median = float(np.median(obs_omegas))
        obs_std = float(np.std(obs_omegas))
        print(f"    Observed: mean={obs_mean:.3f}, median={obs_median:.3f}, "
              f"std={obs_std:.3f}, max={obs_omegas.max():.3f}")

        # store pair metadata
        pair_idx_meta = []
        k = 0
        for i in range(n_r):
            for j in range(i + 1, n_r):
                pair_idx_meta.append((ct, region_order[i], region_order[j], k))
                k += 1

        # ---- block-shuffle permutations ----
        if args.observed_only:
            for (ct_, ra, rb, pk) in pair_idx_meta:
                all_pair_rows.append({
                    'cell_type': ct_, 'region_a': ra, 'region_b': rb,
                    'pair_idx': pk, 'omega': obs_omegas[pk],
                })
            ct_test_rows.append({
                'cell_type': ct, 'n_regions': n_r, 'n_pairs': n_pairs,
                'n_cells': n_cells, 'n_blocks': n_samples,
                'omega_mean': obs_mean, 'omega_median': obs_median,
                'omega_std': obs_std,
            })
            del X_ct, sample_means
            gc.collect()
            continue

        # ---- resume: reuse existing null matrix (pairs x B matches) ----
        null_pair_omegas = None
        resume_path = None
        if args.resume:
            cand = RESULTS_DIR / f"brain_bs_null_pairs_{ct.replace(' ', '_')}.npy"
            if cand.exists():
                tmp = np.load(cand)
                if tmp.shape[0] == n_pairs and tmp.shape[1] == B_PERM:
                    null_pair_omegas = tmp
                    resume_path = cand
        if null_pair_omegas is None:
            null_pair_omegas = np.empty((n_pairs, B_PERM), dtype=np.float32)
            null_ct_means = np.empty(B_PERM, dtype=np.float64)
            t_bs = time.time()
            for b in range(B_PERM):
                perm_assign = sample_region_idx[rng.permutation(n_samples)]
                perm_pbs = region_pbs_from_samples(perm_assign,
                                                   sample_weights, sample_means)
                null_w = pair_omegas(perm_pbs, n_pairs, hk_in_reduced, non_hk_in_reduced)
                null_pair_omegas[:, b] = null_w
                null_ct_means[b] = np.mean(null_w)
                if (b + 1) % 200 == 0:
                    el = time.time() - t_bs
                    eta = el / (b + 1) * (B_PERM - b - 1)
                    print(f"    Iter {b+1}/{B_PERM}, elapsed={el:.0f}s, ETA={eta:.0f}s")
            bs_time = time.time() - t_bs
        else:
            null_ct_means = null_pair_omegas.mean(axis=0)
            bs_time = 0.0
            print(f"    RESUME: reused existing null matrix "
                  f"({n_pairs} pairs x {B_PERM})")

        # per-CT test (one-sided upper: regional structure elevates mean omega)
        p_ct = (np.sum(null_ct_means >= obs_mean) + 1) / (B_PERM + 1)
        null_sd = float(np.std(null_ct_means))
        ses = (obs_mean - float(np.mean(null_ct_means))) / null_sd if null_sd > 1e-12 else 0.0
        print(f"    BS done in {bs_time:.0f}s")
        print(f"    null mean={np.mean(null_ct_means):.3f}, sd={null_sd:.3f}, "
              f"p={p_ct:.4f}, SES={ses:.2f}")

        # save null matrix
        out_npy = RESULTS_DIR / f"brain_bs_null_pairs_{ct.replace(' ', '_')}.npy"
        np.save(out_npy, null_pair_omegas)
        print(f"    Saved null matrix: {out_npy}")

        for (ct_, ra, rb, pk) in pair_idx_meta:
            all_pair_rows.append({
                'cell_type': ct_, 'region_a': ra, 'region_b': rb,
                'pair_idx': pk, 'omega': obs_omegas[pk],
            })
        ct_test_rows.append({
            'cell_type': ct, 'n_regions': n_r, 'n_pairs': n_pairs,
            'n_cells': n_cells, 'n_blocks': n_samples,
            'omega_mean': obs_mean, 'omega_median': obs_median,
            'omega_std': obs_std, 'p_value': p_ct, 'null_mean': float(np.mean(null_ct_means)),
            'null_sd': null_sd, 'SES': ses,
        })
        manifest['cts'][ct] = {
            'n_regions': n_r, 'n_pairs': n_pairs, 'n_cells': n_cells,
            'n_blocks': n_samples, 'null_matrix': str(out_npy),
        }
        del X_ct, sample_means, null_pair_omegas, null_ct_means
        gc.collect()

    f.close()

    # ============================================================
    # 6. Save observed pairs + per-CT summary + multiplicative model
    # ============================================================
    print("\n6. Saving observed pairs + multiplicative model...")
    pairs_df = pd.DataFrame(all_pair_rows)
    mu_grand = pairs_df['omega'].mean()
    mu_ct = pairs_df.groupby('cell_type')['omega'].mean().to_dict()
    mu_pair = pairs_df.groupby(['region_a', 'region_b'])['omega'].mean().to_dict()
    pairs_df['mu_ct'] = pairs_df['cell_type'].map(mu_ct)
    pairs_df['mu_pair'] = pairs_df.apply(
        lambda r: mu_pair.get((r['region_a'], r['region_b']), mu_grand), axis=1)
    pairs_df['expected_omega'] = pairs_df['mu_ct'] * pairs_df['mu_pair'] / mu_grand
    pairs_df['residual'] = pairs_df['omega'] / pairs_df['expected_omega']
    # migration tiers (as in v5 manuscript; lowest-in-pair filter on top)
    lowest_in_pair = pairs_df.groupby(['region_a', 'region_b'])['omega'].transform('min') == pairs_df['omega']
    pairs_df['lowest_in_pair'] = lowest_in_pair
    def tier(r):
        if r['residual'] < 0.3 and r['omega'] < 15 and r['lowest_in_pair']:
            return 'Strong'
        if r['residual'] < 0.5 and r['omega'] < 25:
            return 'Moderate'
        if r['residual'] < 0.75 and r['omega'] < 35:
            return 'Weak'
        return 'None'
    pairs_df['tier'] = pairs_df.apply(tier, axis=1)
    out_csv = RESULTS_DIR / 'brain_bs_null_observed_pairs.csv'
    pairs_df.to_csv(out_csv, index=False)
    print(f"  Saved: {out_csv} ({len(pairs_df)} pairs)")
    print(f"  Grand mean omega: {mu_grand:.3f}")
    print(f"  Tiers: {pairs_df['tier'].value_counts().to_dict()}")

    ct_df = pd.DataFrame(ct_test_rows)
    ct_df = ct_df.sort_values('omega_mean', ascending=False)
    ct_out = RESULTS_DIR / 'brain_bs_null_ct_test.csv'
    ct_df.to_csv(ct_out, index=False)
    print(f"  Saved: {ct_out}")
    if 'p_value' in ct_df.columns:
        print("\n  Per-CT block-shuffle test:")
        print(ct_df[['cell_type', 'n_pairs', 'omega_mean', 'p_value', 'SES']].to_string(index=False))

    with open(RESULTS_DIR / 'brain_bs_null_manifest.json', 'w') as jf:
        json.dump(manifest, jf, indent=2, default=str)
    print("\nDone!")


if __name__ == '__main__':
    main()
