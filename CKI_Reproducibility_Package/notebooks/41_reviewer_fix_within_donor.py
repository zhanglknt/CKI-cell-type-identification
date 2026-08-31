"""
Reviewer fix C-J (#963): donor-confounding structure and within-donor
cross-region omega analysis in Siletti brain data.

Question
--------
Each brain region in the Siletti dataset is dominated by one donor, so
cross-region comparisons are partially cross-donor comparisons. Does the
per-cell-type omega gradient (e.g. Astrocyte 76.8 >> Bergmann glia 11.2)
survive when only *within-donor* cross-region pairs are used?

Design
------
Part 1 (obs only): region x donor contingency structure
    - donors per region, top-donor share per region, regions per donor
    - fraction of region pairs sharing >= 1 donor
Part 2 (expression): within-donor gradient
    - Same gene set as 08d (HRT-derived HK + top-5000 non-HK HVG, global)
    - For each of the 10 non-neuronal classes: build per-(donor, region)
      pseudobulks (donor-region blocks with >= 20 nuclei), compute omega
      for all same-donor cross-region pairs, average per CT.
    - Compare per-CT within-donor means vs pooled (08d) means:
      Spearman correlation + gradient extremes.

Usage
-----
    ./cki_env/Scripts/python.exe -u notebooks/41_reviewer_fix_within_donor.py
"""

import sys, os, time, gc, json
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


# ============================================================
# Backed CSR extraction (same as 08d)
# ============================================================
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


def pair_omegas(pbs, hk_idx, non_hk_idx, n_top=200):
    """All upper-triangle pair omegas from pseudobulks."""
    n = len(pbs)
    omegas = []
    for i in range(n):
        pi = pbs[i]
        for j in range(i + 1, n):
            pj = pbs[j]
            kn = js_divergence(pi[hk_idx], pj[hk_idx])
            ad = np.abs(pi - pj)
            ad_nh = ad[non_hk_idx]
            top_n = min(n_top, len(ad_nh))
            top_local = np.argpartition(ad_nh, -top_n)[-top_n:]
            tg = non_hk_idx[top_local]
            kf = js_divergence(pi[tg], pj[tg])
            omegas.append(kf / kn if kn > 1e-15 else np.inf)
    return np.array(omegas)


def main():
    MIN_NUCLEI_DONOR = 20     # per (donor, region, CT) block
    N_TOP_KF = 200
    N_HVG = 5000
    ct_col = 'supercluster_term'
    region_col = 'roi'
    donor_col = 'donor_id'
    POOLED_REF = RESULTS_DIR / 'brain_bs_null_ct_test.csv'

    # ============================================================
    # 1. HK genes + backed open
    # ============================================================
    print("=" * 60)
    print("1. Loading HK genes (same set as 08d)...")
    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().astype(str))
    print(f"  {len(hk_human)} human HK genes")

    print("\n2. Opening Siletti (backed h5py)...")
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
    if var_gene is None:
        raise RuntimeError("Could not read gene symbols")
    N_GENES = len(var_gene)
    print(f"  Shape: ({N_CELLS}, {N_GENES})")

    obs = f['obs']
    def read_codes(name):
        g = obs[name]
        if isinstance(g, h5py.Dataset):
            vals = g[:]
            return vals, None
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g['categories'][:]]
        codes = g['codes'][:]
        return codes, cats

    ct_codes, ct_cats = read_codes(ct_col)
    roi_codes, roi_cats = read_codes(region_col)
    donor_codes, donor_cats = read_codes(donor_col)
    ct_names = np.array(ct_cats)[ct_codes] if ct_cats is not None else ct_codes.astype(str)
    roi_names = np.array(roi_cats)[roi_codes] if roi_cats is not None else roi_codes.astype(str)
    donor_names = (np.array(donor_cats)[donor_codes] if donor_cats is not None
                   else donor_codes.astype(str))
    print(f"  Unique: {len(set(ct_names))} CTs, {len(set(roi_names))} ROIs, "
          f"{len(set(donor_names))} donors")

    # ============================================================
    # 3. Global gene means -> keep set (same as 08d)
    # ============================================================
    print("\n3. Computing global gene means (HVG selection)...")
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
    print(f"  Means computed in {time.time()-t0:.0f}s")

    hk_global = np.array(sorted({i for i, sym in enumerate(var_gene)
                                 if pd.notna(sym) and sym in hk_human}), dtype=int)
    print(f"  Matched HK genes: {len(hk_global)}")
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
    # 4. PART 1 — donor/region confounding structure
    # ============================================================
    print("\n" + "=" * 60)
    print("PART 1: region x donor confounding structure")
    print("=" * 60)
    meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names, 'donor': donor_names})
    ct_region_counts = meta.groupby('roi')['ct'].count().sort_values(ascending=False)
    regions_major = set(ct_region_counts[ct_region_counts >= 50].index)
    meta_maj = meta[meta['roi'].isin(regions_major)]
    print(f"  Major regions (>=50 cells): {len(regions_major)}")

    rt = meta_maj.groupby(['roi', 'donor']).size().reset_index(name='n')
    tot_per_region = rt.groupby('roi')['n'].transform('sum')
    rt['share'] = rt['n'] / tot_per_region
    top_share = rt.loc[rt.groupby('roi')['share'].idxmax()]
    print(f"\n  Donors per region: median={top_share.shape[0] and rt.groupby('roi').size().median():.0f}, "
          f"max={rt.groupby('roi').size().max()}, min={rt.groupby('roi').size().min()}")
    print(f"  Top-donor share per region: median={top_share['share'].median():.2f}, "
          f"mean={top_share['share'].mean():.2f}")
    print(f"  Regions where top donor share >= 0.90: "
          f"{(top_share['share'] >= 0.90).sum()}/{len(top_share)}")

    donors_per_region_full = rt.groupby('roi')['donor'].nunique()
    regions_per_donor = rt.groupby('donor')['roi'].nunique()
    print(f"  Regions per donor: median={regions_per_donor.median():.0f}, "
          f"max={regions_per_donor.max()}")
    print(f"  Donors covering >=2 major regions: {(regions_per_donor >= 2).sum()} / "
          f"{len(regions_per_donor)}")

    # region pairs sharing >=1 donor
    reg_list = sorted(regions_major)
    donor_sets = {r: set(rt[rt['roi'] == r]['donor']) for r in reg_list}
    n_pair_tot, n_pair_share = 0, 0
    for i in range(len(reg_list)):
        for j in range(i + 1, len(reg_list)):
            n_pair_tot += 1
            if donor_sets[reg_list[i]] & donor_sets[reg_list[j]]:
                n_pair_share += 1
    print(f"  Region pairs sharing >=1 donor: {n_pair_share}/{n_pair_tot} "
          f"({100*n_pair_share/n_pair_tot:.1f}%)")

    # save part 1
    out1 = pd.DataFrame({
        'metric': [
            'n_major_regions', 'n_donors', 'donors_per_region_median',
            'donors_per_region_max', 'top_donor_share_median',
            'top_donor_share_mean', 'regions_with_top_share_ge_90pct',
            'region_pairs_total', 'region_pairs_sharing_donor',
            'region_pairs_sharing_donor_pct'],
        'value': [
            len(regions_major), len(regions_per_donor),
            donors_per_region_full.median(), donors_per_region_full.max(),
            top_share['share'].median(), top_share['share'].mean(),
            (top_share['share'] >= 0.90).sum(),
            n_pair_tot, n_pair_share, 100*n_pair_share/n_pair_tot],
    })
    out1.to_csv(RESULTS_DIR / 'reviewer_donor_confounding_structure.csv', index=False)
    print("  Saved -> results/reviewer_donor_confounding_structure.csv")

    # ============================================================
    # 5. PART 2 — within-donor cross-region omegas per CT
    # ============================================================
    print("\n" + "=" * 60)
    print(f"PART 2: within-donor cross-region omega (block >= {MIN_NUCLEI_DONOR} nuclei)")
    print("=" * 60)

    pooled = pd.read_csv(POOLED_REF)[['cell_type', 'omega_mean']]
    pooled = pooled.rename(columns={'omega_mean': 'omega_mean_pooled'})
    target_cts = list(pooled['cell_type'])

    rows = []
    for ct in target_cts:
        t_ct = time.time()
        # blocks = (donor, region) with >= MIN_NUCLEI_DONOR cells of this CT
        sub = meta[meta['ct'] == ct]
        blk = sub.groupby(['donor', 'roi']).size().reset_index(name='n')
        blk = blk[blk['n'] >= MIN_NUCLEI_DONOR]
        if blk.empty:
            print(f"\n  --- {ct}: no qualifying donor-region blocks ---")
            rows.append({'cell_type': ct, 'n_blocks': 0, 'n_donors': 0,
                         'n_pairs_within_donor': 0})
            continue
        blk_keys = set(zip(blk['donor'], blk['roi']))

        # donors with >=2 regions
        dcnt = blk.groupby('donor')['roi'].nunique()
        donors_multi = set(dcnt[dcnt >= 2].index)
        n_pairs_wd = sum(int(k * (k - 1) / 2) for k in
                         [dcnt[d] for d in donors_multi])
        print(f"\n  --- {ct}: {len(blk)} blocks, {len(donors_multi)} donors "
              f"with >=2 regions, {n_pairs_wd} within-donor pairs ---")
        if n_pairs_wd < 3:
            print("    (too few within-donor pairs; skipping)")
            rows.append({'cell_type': ct, 'n_blocks': len(blk),
                         'n_donors': len(donors_multi),
                         'n_pairs_within_donor': n_pairs_wd})
            continue

        # extract cells belonging to qualifying blocks
        mask = np.isin(ct_names, [ct]) & np.array([
            (d, r) in blk_keys for d, r in zip(donor_names, roi_names)])
        # cheaper: build boolean via pandas map
        key_series = pd.Series(list(zip(donor_names, roi_names)))
        in_blk = key_series.isin(blk_keys) & (ct_names == ct)
        ct_global_idx = np.where(in_blk.values)[0]

        # per (donor, region) means
        cell_donor = donor_names[ct_global_idx]
        cell_roi = roi_names[ct_global_idx]
        order = np.argsort(cell_donor, kind='stable')
        ct_global_idx = ct_global_idx[order]
        cell_donor = cell_donor[order]
        cell_roi = cell_roi[order]

        X_ct = extract_csr_from_backed(str(BRAIN_FILE), ct_global_idx,
                                        keep_global, N_GENES)
        print(f"    Extracted {X_ct.shape[0]} cells "
              f"({X_ct.nnz/1e6:.1f}M nnz, {time.time()-t_ct:.0f}s)")

        # unique (donor, region) groups in sorted order
        keys = pd.DataFrame({'donor': cell_donor, 'roi': cell_roi})
        grp = keys.groupby(['donor', 'roi'], sort=True)
        grp_sizes = grp.size().values
        grp_starts = np.concatenate([[0], np.cumsum(grp_sizes)[:-1]])
        grp_names = list(grp.size().index)  # (donor, roi)

        # block mean + pseudobulk (norm 1e4 + log1p)
        pbs = []
        for gi, (dn, rg) in enumerate(grp_names):
            s, e = grp_starts[gi], grp_starts[gi] + grp_sizes[gi]
            m = np.asarray(X_ct[s:e].mean(axis=0)).flatten()
            tot = m.sum()
            m_norm = m / tot * 1e4 if tot > 0 else m
            pbs.append(np.log1p(m_norm).astype(np.float64))

        # within-donor pairs
        omegas_wd = []
        for dn in donors_multi:
            idxs = [gi for gi, (d_, r_) in enumerate(grp_names) if d_ == dn]
            for a in range(len(idxs)):
                for b in range(a + 1, len(idxs)):
                    pi, pj = pbs[idxs[a]], pbs[idxs[b]]
                    kn = js_divergence(pi[hk_in_reduced], pj[hk_in_reduced])
                    ad = np.abs(pi - pj)
                    ad_nh = ad[non_hk_in_reduced]
                    top_n = min(N_TOP_KF, len(ad_nh))
                    top_local = np.argpartition(ad_nh, -top_n)[-top_n:]
                    tg = non_hk_in_reduced[top_local]
                    kf = js_divergence(pi[tg], pj[tg])
                    omegas_wd.append(kf / kn if kn > 1e-15 else np.inf)
        omegas_wd = np.array(omegas_wd)
        mu_wd = float(np.mean(omegas_wd))
        print(f"    Within-donor: mean={mu_wd:.3f}, median={np.median(omegas_wd):.3f}, "
              f"n={len(omegas_wd)} (pooled mean="
              f"{pooled.loc[pooled['cell_type']==ct,'omega_mean_pooled'].iloc[0]:.3f})")
        rows.append({'cell_type': ct, 'n_blocks': len(blk),
                     'n_donors': len(donors_multi),
                     'n_pairs_within_donor': len(omegas_wd),
                     'omega_mean_within_donor': mu_wd,
                     'omega_median_within_donor': float(np.median(omegas_wd)),
                     'omega_std_within_donor': float(np.std(omegas_wd))})
        del X_ct, pbs
        gc.collect()

    f.close()

    # ============================================================
    # 6. Summary: within-donor vs pooled gradient
    # ============================================================
    print("\n" + "=" * 60)
    print("SUMMARY: within-donor vs pooled per-CT gradient")
    print("=" * 60)
    wd = pd.DataFrame(rows).merge(pooled, on='cell_type')
    wd.to_csv(RESULTS_DIR / 'reviewer_within_donor_gradient.csv', index=False)
    print(wd.to_string(index=False))

    ok = wd.dropna(subset=['omega_mean_within_donor'])
    if len(ok) >= 3:
        r, p = spearmanr(ok['omega_mean_within_donor'], ok['omega_mean_pooled'])
        print(f"\n  Spearman corr(within-donor mean, pooled mean) = {r:.3f} (P = {p:.2g}, n={len(ok)})")
        print(f"  Pooled gradient extremes: Astrocyte/Bergmann glia = "
              f"{76.83/11.17:.2f}x")
        if 'Astrocyte' in set(ok['cell_type']):
            a = ok.loc[ok['cell_type'] == 'Astrocyte', 'omega_mean_within_donor'].iloc[0]
            print(f"  Astrocyte within-donor mean = {a:.2f}")
        if 'Bergmann glia' in set(ok['cell_type']):
            b = ok.loc[ok['cell_type'] == 'Bergmann glia', 'omega_mean_within_donor']
            if len(b):
                print(f"  Bergmann glia within-donor mean = {b.iloc[0]:.2f}")
    print("\nSaved -> results/reviewer_within_donor_gradient.csv")
    print("DONE.")


if __name__ == '__main__':
    main()
