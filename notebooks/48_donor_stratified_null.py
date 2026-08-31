"""
48 Donor-Stratified Block-Shuffle Null (Sensitivity Analysis)
=============================================================
Responds to round-3 R2 P1-1: the brain class-level block-shuffle null
(08d) permutes library->region assignments freely across all 606
libraries, which destroys the donor-region association that the observed
landscape retains (4 donors; median top-donor share within a region =
0.61). Any donor-level expression signature therefore contributes to the
observed class means but not to the null means, potentially inflating
the class-level test statistics.

Design
------
Two permutation nulls are computed in the same pass, everything else
identical to 08d (same HK + top-5000 non-HK HVG gene set, same
pseudobulk construction cell-mean -> /total*1e4 -> log1p, same per-pair
top-200 |A-B| gene re-selection at every permutation, B = 1000,
one-sided upper-tail class test):

- FREE block shuffle (08d scheme): permute library->region labels
  globally, per-region library counts preserved.
- DONOR-STRATIFIED block shuffle (new): within each donor
  (obs['donor_id']), permute that donor's library->region labels,
  preserving the per-(donor, region) library-count multiset exactly.
  Consequences: per-region library counts exactly preserved; each
  region's donor composition preserved -> the null is CONDITIONAL on
  donor structure; libraries of a donor present in only one region are
  fixed (correct behavior for a conditional null).

CRITICAL BUG FIX vs 08d/08c/41
------------------------------
extract_csr_from_backed() in the 08c/08d lineage contains a row-
assignment bug: it writes each cell's data to output row
`unsort[ci]` (the inverse permutation) instead of `sort_order[ci]`.
For ASCENDING cell_indices the two coincide (this is why the unit
tests of 08c passed), but for the region-sorted inputs actually used
by 08c/08d/41 the extracted matrix rows are a scrambled permutation of
the requested cells, so every downstream pseudobulk mixed cells across
libraries/regions. Verified on this dataset: extracting with input
[1000, 5000, 2000, 3000] returns rows [0, 3, 1, 2]; a 300-row check of
the 08d-style (region-sorted) Ependymal extraction matched the true
cell data in 0/300 rows. The published brain_bs_null_ct_test.csv values
(e.g. Astrocyte 76.83) therefore do NOT equal the correctly-extracted
landscape; this script recomputes observed + both nulls with the fixed
extraction and reports the corrected values alongside the published
ones. The vectorized pair-omega routine is validated against the scalar
08d code path (max |diff| < 1e-9) before use.

Additionally (null-side diagnostic requested by R2 P1-1):
- per-region top-donor share (nuclei-weighted and library-count) under
  (i) the FREE block shuffle and (ii) the donor-stratified shuffle,
  vs observation.

Outputs (results/):
  v38_donor_stratified_null.csv        per-CT tests: corrected observed,
                                       corrected free null, donor-stratified
                                       null, published 08d values, BH q
  v48_free_null_pairs_<CT>.npy         corrected free-shuffle null (audit)
  v48_strat_null_pairs_<CT>.npy        donor-stratified null (audit)
  v38_donor_stratified_manifest.json   run metadata
  v38_topdonor_share_null.csv          top-donor share diagnostic

Usage
-----
    python 48_donor_stratified_null.py [--max-perm N] [--ct NAME]
    python 48_donor_stratified_null.py --diag-only
    python 48_donor_stratified_null.py --validate
"""

import sys, os, time, gc, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import h5py
from scipy.sparse import csr_matrix
from cki.core import js_divergence

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)


# ============================================================
# Backed CSR extraction -- FIXED version of the 08c/08d function
# ============================================================
def extract_csr_from_backed(h5_path, cell_indices, keep_global, n_genes_total,
                            chunk_size=20000):
    """Extract CSR matrix (rows follow the INPUT order of cell_indices).

    Bug fix vs 08c/08d: data is written to row ``sort_order[ci]``
    (input position of the ci-th smallest cell) instead of the buggy
    ``unsort[ci]``; the indptr accumulation is fixed consistently.
    """
    n_cells = len(cell_indices)
    n_keep = len(keep_global)
    if n_cells == 0:
        return csr_matrix((0, n_keep), dtype=np.float32)

    gene_map = np.full(n_genes_total, -1, dtype=np.int32)
    gene_map[keep_global] = np.arange(n_keep, dtype=np.int32)

    sort_order = np.argsort(cell_indices, kind='stable')
    sorted_cells = cell_indices[sort_order]

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
                chunk_keep = np.array([], dtype=np.bool_)
                chunk_data = np.array([], dtype=X['data'].dtype)
            for ci in range(cs, ce):
                orig_pos = int(sort_order[ci])          # FIX (was unsort[ci])
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
    cell_nnz_orig[sort_order] = cell_nnz_sorted            # FIX (was unsort)
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


# ============================================================
# Pair omegas: scalar reference (08d code path) + vectorized
# ============================================================
def pair_omegas(pbs, n_pairs, hk_idx, non_hk_idx, n_top=200):
    """Scalar 08d code path (reference for validation)."""
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


def _softmax_rows(M):
    """Row-wise softmax identical to cki.utils.ensure_probability_distribution
    (mode='softmax', epsilon=1e-9)."""
    mx = M.max(axis=1, keepdims=True)
    e = np.exp(M - mx)
    return e / (e.sum(axis=1, keepdims=True) + 1e-9)


def _js_rows(P, Q):
    """Row-wise JS divergence for paired probability rows (base-2)."""
    M = 0.5 * (P + Q)
    with np.errstate(divide='ignore', invalid='ignore'):
        lp = np.where(P > 0, P * np.log2(P / M), 0.0)
        lq = np.where(Q > 0, Q * np.log2(Q / M), 0.0)
    return 0.5 * lp.sum(axis=1) + 0.5 * lq.sum(axis=1)


def pair_omegas_fast(pbs, hk_idx, non_hk_idx, n_top=200, chunk=1000):
    """Vectorized equivalent of pair_omegas (validated to <1e-9)."""
    M = np.asarray(pbs, dtype=np.float64)
    n = M.shape[0]
    I, J = np.triu_indices(n, k=1)
    n_pairs = len(I)
    A_hk = _softmax_rows(M[:, hk_idx])
    nh = M[:, non_hk_idx]
    k = min(n_top, nh.shape[1])
    omegas = np.empty(n_pairs, dtype=np.float64)
    rr = None
    for s in range(0, n_pairs, chunk):
        i = I[s:s + chunk]
        j = J[s:s + chunk]
        c = len(i)
        kn = _js_rows(A_hk[i], A_hk[j])
        D = np.abs(nh[i] - nh[j])
        top = np.argpartition(D, -k, axis=1)[:, -k:]
        if rr is None or len(rr) != c:
            rr = np.arange(c)[:, None]
        Pa = _softmax_rows(nh[i][rr, top])
        Pb = _softmax_rows(nh[j][rr, top])
        kf = _js_rows(Pa, Pb)
        omegas[s:s + c] = np.where(kn > 1e-15, kf / np.maximum(kn, 1e-300),
                                   np.inf)
    return omegas


def region_pbs_from_samples(assign_idx, weights, means, n_regions):
    """assign_idx: sample -> region index. Return list of pbs (as 08d)."""
    pbs = []
    for r in range(n_regions):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-perm', type=int, default=1000)
    ap.add_argument('--ct', default=None, help='restrict to one cell type')
    ap.add_argument('--resume', action='store_true',
                    help='reuse existing null matrices for CTs already run')
    ap.add_argument('--diag-only', action='store_true',
                    help='run only the top-donor-share diagnostic')
    ap.add_argument('--validate', action='store_true',
                    help='validate fixed extraction + fast pair-omegas '
                         'against independent ground truth, then exit')
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
    donor_col = 'donor_id'

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
    f = h5py.File(SILETTI_PATH, 'r')
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
        raise RuntimeError("Could not read gene symbols from var group")
    N_GENES = len(var_gene)
    print(f"  Shape: ({N_CELLS}, {N_GENES})")

    obs = f['obs']
    def read_codes(name):
        g = obs[name]
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g['categories'][:]]
        codes = g['codes'][:]
        return codes, cats
    ct_codes, ct_cats = read_codes(ct_col)
    roi_codes, roi_cats = read_codes(region_col)
    samp_codes, _ = read_codes(sample_col)
    donor_codes, donor_cats = read_codes(donor_col)
    ct_names = np.array(ct_cats)[ct_codes]
    roi_names = np.array(roi_cats)[roi_codes]
    donor_names = np.array(donor_cats)[donor_codes]
    print(f"  Donors: {sorted(set(donor_names))}")

    hk_global = np.array(sorted({i for i, sym in enumerate(var_gene)
                                 if pd.notna(sym) and sym in hk_human}), dtype=int)
    print(f"  Matched HK genes: {len(hk_global)}")

    # ============================================================
    # 3. Global gene means for HVG selection (non-HK) -- same as 08d
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
    # 4. Filter groups (same rule as 08d)
    # ============================================================
    print("\n4. Filtering groups...")
    df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names,
                            'sample': samp_codes, 'donor': donor_names})
    groups = df_meta.groupby(['roi', 'ct']).size().reset_index(name='count')
    groups_ok = groups[groups['count'] >= MIN_NUCLEI]
    region_counts = df_meta['roi'].value_counts()
    regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
    groups_ok = groups_ok[groups_ok['roi'].isin(regions_ok)]
    cts_present = sorted(groups_ok['ct'].unique())
    if args.ct:
        cts_present = [c for c in cts_present if c == args.ct]
    print(f"  Groups passing: {len(groups_ok)} | CTs: {len(cts_present)}")

    ct_to_regions = {}
    for _, row in groups_ok.iterrows():
        ct_to_regions.setdefault(row['ct'], [])
        if row['roi'] not in ct_to_regions[row['ct']]:
            ct_to_regions[row['ct']].append(row['roi'])
    for ct in cts_present:
        n_r = len(ct_to_regions[ct])
        print(f"    {ct}: {n_r} regions, {n_r*(n_r-1)//2} pairs")

    # ============================================================
    # 4b. Validation mode
    # ============================================================
    if args.validate:
        print("\n" + "=" * 60)
        print("VALIDATION: fixed extraction vs direct h5 reads + "
              "fast vs scalar pair omegas (Ependymal)")
        print("=" * 60)
        ct = 'Ependymal'
        regions = sorted(ct_to_regions[ct])
        ct_bool = (ct_names == ct) & np.isin(roi_names, regions)
        ct_global_idx = np.where(ct_bool)[0]
        region_of_cell = roi_names[ct_global_idx]
        samp_of_cell = samp_codes[ct_global_idx]
        sort_idx = np.argsort(region_of_cell, kind='stable')
        idx_sorted = ct_global_idx[sort_idx]
        X_ct = extract_csr_from_backed(str(SILETTI_PATH), idx_sorted,
                                       keep_global, N_GENES)
        # ground truth rows read directly from h5
        gene_map = np.full(N_GENES, -1, dtype=np.int32)
        gene_map[keep_global] = np.arange(len(keep_global))
        n_check = 500
        bad = 0
        for i in range(n_check):
            cell = int(idx_sorted[i])
            lo, hi = int(indptr_full[cell]), int(indptr_full[cell + 1])
            idx = X['indices'][lo:hi]
            dat = X['data'][lo:hi]
            m = gene_map[idx] >= 0
            t = np.zeros(len(keep_global))
            t[gene_map[idx[m]]] = dat[m]
            if not np.allclose(X_ct[i].toarray().flatten(), t):
                bad += 1
        print(f"  extraction: {n_check - bad}/{n_check} checked rows exact")
        assert bad == 0, "fixed extraction still wrong!"

        region_sorted = region_of_cell[sort_idx]
        samp_sorted = samp_of_cell[sort_idx]
        uniq_samples, sample_inv = np.unique(samp_sorted, return_inverse=True)
        n_samples = len(uniq_samples)
        sample_rows = [np.where(sample_inv == s)[0] for s in range(n_samples)]
        sample_weights = np.array([len(r) for r in sample_rows], float)
        sample_region_idx = np.array(
            [regions.index(region_sorted[r[0]]) for r in sample_rows], int)
        sample_means = np.zeros((n_samples, X_ct.shape[1]))
        for s in range(n_samples):
            sample_means[s] = np.asarray(
                X_ct[sample_rows[s]].mean(axis=0)).flatten()
        obs_pbs = region_pbs_from_samples(sample_region_idx, sample_weights,
                                          sample_means, len(regions))
        n_pairs = len(regions) * (len(regions) - 1) // 2
        om_scalar = pair_omegas(obs_pbs, n_pairs, hk_in_reduced,
                                non_hk_in_reduced)
        om_fast = pair_omegas_fast(obs_pbs, hk_in_reduced, non_hk_in_reduced)
        d = np.abs(om_scalar - om_fast)
        print(f"  pair omegas: max |scalar - fast| = {d.max():.3e} "
              f"(n={n_pairs})")
        assert d.max() < 1e-9, "vectorized pair omegas mismatch!"
        print("  VALIDATION PASSED")
        f.close()
        return

    # ============================================================
    # 5. Top-donor share null-side diagnostic (metadata only)
    # ============================================================
    print("\n" + "=" * 60)
    print(f"5. Top-donor share diagnostic (B={B_PERM}, metadata level)")
    print("=" * 60)
    meta_maj = df_meta[df_meta['roi'].isin(regions_ok)]
    lib_tab = (meta_maj.groupby(['sample', 'roi', 'donor']).size()
               .reset_index(name='n_cells'))
    reg_list = sorted(regions_ok)
    reg_idx = {r: i for i, r in enumerate(reg_list)}
    don_list = sorted(lib_tab['donor'].unique())
    don_idx = {d: i for i, d in enumerate(don_list)}
    n_reg, n_don = len(reg_list), len(don_list)
    lib_region = lib_tab['roi'].map(reg_idx).to_numpy()
    lib_donor = lib_tab['donor'].map(don_idx).to_numpy()
    lib_cells = lib_tab['n_cells'].to_numpy(dtype=np.float64)
    n_lib = len(lib_tab)
    print(f"  Major regions: {n_reg} | libraries: {n_lib} | donors: {n_don}")

    def top_share_stats(assign):
        M = np.zeros((n_reg, n_don))
        np.add.at(M, (assign, lib_donor), lib_cells)
        share_cell = M.max(axis=1) / np.maximum(M.sum(axis=1), 1.0)
        L = np.zeros((n_reg, n_don))
        np.add.at(L, (assign, lib_donor), 1.0)
        share_lib = L.max(axis=1) / np.maximum(L.sum(axis=1), 1.0)
        return share_cell, share_lib

    obs_share_cell, obs_share_lib = top_share_stats(lib_region)
    print(f"  Observed per-region top-donor share (nuclei-weighted): "
          f"median={np.median(obs_share_cell):.3f} "
          f"(mean={obs_share_cell.mean():.3f})")
    print(f"  Observed per-region top-donor share (library-count): "
          f"median={np.median(obs_share_lib):.3f} "
          f"(mean={obs_share_lib.mean():.3f})")

    rng_diag = np.random.RandomState(RANDOM_SEED + 1)
    free_cell, strat_cell = np.empty(B_PERM), np.empty(B_PERM)
    free_lib, strat_lib = np.empty(B_PERM), np.empty(B_PERM)
    for b in range(B_PERM):
        free_assign = lib_region[rng_diag.permutation(n_lib)]
        sc, sl = top_share_stats(free_assign)
        free_cell[b], free_lib[b] = np.median(sc), np.median(sl)
        strat_assign = lib_region.copy()
        for d in range(n_don):
            m = lib_donor == d
            strat_assign[m] = lib_region[m][rng_diag.permutation(int(m.sum()))]
        sc, sl = top_share_stats(strat_assign)
        strat_cell[b], strat_lib[b] = np.median(sc), np.median(sl)
        if (b + 1) % 200 == 0:
            print(f"    diag iter {b+1}/{B_PERM}")
    print(f"  FREE shuffle:   top-donor share median (nuclei) = "
          f"{np.median(free_cell):.3f} [{np.percentile(free_cell,2.5):.3f}, "
          f"{np.percentile(free_cell,97.5):.3f}] | (libraries) = "
          f"{np.median(free_lib):.3f} [{np.percentile(free_lib,2.5):.3f}, "
          f"{np.percentile(free_lib,97.5):.3f}]")
    print(f"  STRATIFIED:     top-donor share median (nuclei) = "
          f"{np.median(strat_cell):.3f} [{np.percentile(strat_cell,2.5):.3f}, "
          f"{np.percentile(strat_cell,97.5):.3f}] | (libraries) = "
          f"{np.median(strat_lib):.3f} [{np.percentile(strat_lib,2.5):.3f}, "
          f"{np.percentile(strat_lib,97.5):.3f}]")

    def diag_block(scenario, arr_cell, arr_lib):
        return {'scenario': scenario,
                'median_top_donor_share_nuclei': float(np.median(arr_cell)),
                'median_top_donor_share_libcount': float(np.median(arr_lib)),
                'perm_med_nuclei_p2.5': float(np.percentile(arr_cell, 2.5)),
                'perm_med_nuclei_p97.5': float(np.percentile(arr_cell, 97.5)),
                'perm_med_libcount_p2.5': float(np.percentile(arr_lib, 2.5)),
                'perm_med_libcount_p97.5': float(np.percentile(arr_lib, 97.5)),
                'mean_top_donor_share_nuclei': float(np.mean(arr_cell)),
                'mean_top_donor_share_libcount': float(np.mean(arr_lib))}

    diag_rows = [
        diag_block('observed', obs_share_cell, obs_share_lib),
        diag_block('free_block_shuffle (08d null)', free_cell, free_lib),
        diag_block('donor_stratified_shuffle (this null)', strat_cell,
                   strat_lib),
    ]
    pd.DataFrame(diag_rows).to_csv(
        RESULTS_DIR / 'v38_topdonor_share_null.csv', index=False)
    print("  Saved -> results/v38_topdonor_share_null.csv")
    np.save(RESULTS_DIR / 'v38_topdonor_share_null_dist.npy',
            np.vstack([free_cell, free_lib, strat_cell, strat_lib]))

    if args.diag_only:
        f.close()
        print("\nDone (diagnostic only).")
        return

    # ============================================================
    # 6. Per-CT: corrected observed + free null + stratified null
    # ============================================================
    print("\n" + "=" * 60)
    print(f"6. Per-CT nulls with FIXED extraction "
          f"(B={B_PERM}, free + donor-stratified)")
    print("=" * 60)

    ct_test_rows = []
    manifest = {'seed': RANDOM_SEED, 'B': B_PERM,
                'blocks': 'sample_id', 'stratified_by': 'donor_id',
                'gene_set': f'HK_{len(hk_in_reduced)}_HVG{len(non_hk_in_reduced)}',
                'extraction': 'FIXED extract_csr_from_backed (08c/08d row bug corrected)',
                'cts': {}}

    for ct in cts_present:
        regions = sorted(ct_to_regions[ct])
        n_r = len(regions)
        n_pairs = n_r * (n_r - 1) // 2
        if n_pairs < 5:
            continue
        print(f"\n  --- {ct} ({n_r} regions, {n_pairs} pairs) ---")

        # 6a. cell indices + metadata for this CT
        ct_bool = (ct_names == ct) & np.isin(roi_names, regions)
        ct_global_idx = np.where(ct_bool)[0]
        region_of_cell = roi_names[ct_global_idx]
        samp_of_cell = samp_codes[ct_global_idx]
        donor_of_cell = donor_names[ct_global_idx]
        sort_idx = np.argsort(region_of_cell, kind='stable')
        region_sorted = region_of_cell[sort_idx]
        samp_sorted = samp_of_cell[sort_idx]
        donor_sorted = donor_of_cell[sort_idx]
        idx_sorted = ct_global_idx[sort_idx]

        # 6b. extract CSR (fixed)
        t0 = time.time()
        X_ct = extract_csr_from_backed(str(SILETTI_PATH), idx_sorted,
                                       keep_global, N_GENES)
        n_cells = X_ct.shape[0]
        print(f"    Extracted {n_cells} cells x {len(keep_global)} genes "
              f"({X_ct.nnz/1e6:.0f}M nnz, {time.time()-t0:.0f}s)")

        # 6c. sample blocks
        uniq_samples, sample_inv = np.unique(samp_sorted, return_inverse=True)
        n_samples = len(uniq_samples)
        sample_rows = [np.where(sample_inv == s)[0] for s in range(n_samples)]
        sample_weights = np.array([len(r) for r in sample_rows], dtype=np.float64)
        sample_region_idx = np.array(
            [regions.index(region_sorted[r[0]]) for r in sample_rows], dtype=int)
        uniq_donors = sorted(set(donor_sorted))
        donor_lookup = {d: i for i, d in enumerate(uniq_donors)}
        sample_donor_idx = np.array(
            [donor_lookup[donor_sorted[r[0]]] for r in sample_rows], dtype=int)
        n_shufflable = 0
        for d in range(len(uniq_donors)):
            m = sample_donor_idx == d
            if len(set(sample_region_idx[m])) >= 2:
                n_shufflable += int(m.sum())
        print(f"    Blocks (samples): {n_samples} | donors: {len(uniq_donors)} "
              f"| shufflable blocks: {n_shufflable}")

        sample_means = np.zeros((n_samples, X_ct.shape[1]), dtype=np.float64)
        for s in range(n_samples):
            if len(sample_rows[s]) > 0:
                sample_means[s] = np.asarray(X_ct[sample_rows[s]].mean(axis=0)).flatten()

        # 6d. corrected observed region pseudobulks
        obs_pbs = region_pbs_from_samples(sample_region_idx, sample_weights,
                                          sample_means, n_r)
        t0 = time.time()
        obs_omegas = pair_omegas_fast(obs_pbs, hk_in_reduced,
                                      non_hk_in_reduced)
        if ct == cts_present[0]:
            om_scalar = pair_omegas(obs_pbs, n_pairs, hk_in_reduced,
                                    non_hk_in_reduced)
            dmax = float(np.abs(om_scalar - obs_omegas).max())
            print(f"    [validation] fast vs scalar observed omegas: "
                  f"max|diff|={dmax:.3e}")
            assert dmax < 1e-9
        obs_mean = float(np.mean(obs_omegas))
        obs_median = float(np.median(obs_omegas))
        obs_std = float(np.std(obs_omegas))
        print(f"    Observed (corrected): mean={obs_mean:.3f}, "
              f"median={obs_median:.3f}, std={obs_std:.3f} "
              f"({time.time()-t0:.1f}s)")

        # ---- permutations: free + donor-stratified ----
        free_npy = RESULTS_DIR / f"v48_free_null_pairs_{ct.replace(' ', '_')}.npy"
        strat_npy = RESULTS_DIR / f"v48_strat_null_pairs_{ct.replace(' ', '_')}.npy"
        if args.resume and free_npy.exists() and strat_npy.exists():
            fa, sa = np.load(free_npy), np.load(strat_npy)
            if fa.shape == (n_pairs, B_PERM) and sa.shape == (n_pairs, B_PERM):
                free_null, strat_null = fa, sa
                print("    RESUME: reused existing null matrices")
            else:
                free_null = strat_null = None
        else:
            free_null = strat_null = None
        if free_null is None:
            free_null = np.empty((n_pairs, B_PERM), dtype=np.float32)
            strat_null = np.empty((n_pairs, B_PERM), dtype=np.float32)
            n_identity = 0
            donor_masks = [sample_donor_idx == d for d in range(len(uniq_donors))]
            t_bs = time.time()
            for b in range(B_PERM):
                # free shuffle (08d scheme)
                free_assign = sample_region_idx[rng.permutation(n_samples)]
                perm_pbs = region_pbs_from_samples(
                    free_assign, sample_weights, sample_means, n_r)
                free_null[:, b] = pair_omegas_fast(perm_pbs, hk_in_reduced,
                                                   non_hk_in_reduced)
                # donor-stratified shuffle
                strat_assign = sample_region_idx.copy()
                for m in donor_masks:
                    if m.sum() > 1:
                        strat_assign[m] = sample_region_idx[m][
                            rng.permutation(int(m.sum()))]
                if np.array_equal(strat_assign, sample_region_idx):
                    n_identity += 1
                perm_pbs = region_pbs_from_samples(
                    strat_assign, sample_weights, sample_means, n_r)
                strat_null[:, b] = pair_omegas_fast(perm_pbs, hk_in_reduced,
                                                    non_hk_in_reduced)
                if (b + 1) % 100 == 0:
                    el = time.time() - t_bs
                    eta = el / (b + 1) * (B_PERM - b - 1)
                    print(f"    Iter {b+1}/{B_PERM}, elapsed={el:.0f}s, "
                          f"ETA={eta:.0f}s")
            print(f"    Identity stratified permutations (degenerate): "
                  f"{n_identity}/{B_PERM}")
            np.save(free_npy, free_null)
            np.save(strat_npy, strat_null)

        free_ct_means = free_null.mean(axis=0)
        strat_ct_means = strat_null.mean(axis=0)

        def ct_test(null_means):
            p = (np.sum(null_means >= obs_mean) + 1) / (B_PERM + 1)
            sd = float(np.std(null_means))
            mu = float(np.mean(null_means))
            ses = (obs_mean - mu) / sd if sd > 1e-12 else 0.0
            return p, mu, sd, ses

        p_free, mu_free, sd_free, ses_free = ct_test(free_ct_means)
        p_strat, mu_strat, sd_strat, ses_strat = ct_test(strat_ct_means)
        print(f"    FREE null:  mean={mu_free:.3f}, sd={sd_free:.3f}, "
              f"p={p_free:.4f}, SES={ses_free:.2f}")
        print(f"    STRAT null: mean={mu_strat:.3f}, sd={sd_strat:.3f}, "
              f"p={p_strat:.4f}, SES={ses_strat:.2f}")

        ct_test_rows.append({
            'cell_type': ct, 'n_regions': n_r, 'n_pairs': n_pairs,
            'n_cells': n_cells, 'n_blocks': n_samples,
            'n_donors': len(uniq_donors), 'n_shufflable_blocks': n_shufflable,
            'omega_mean': obs_mean, 'omega_median': obs_median,
            'omega_std': obs_std,
            'free_p_value': p_free, 'free_null_mean': mu_free,
            'free_null_sd': sd_free, 'free_SES': ses_free,
            'strat_p_value': p_strat, 'strat_null_mean': mu_strat,
            'strat_null_sd': sd_strat, 'strat_SES': ses_strat,
        })
        manifest['cts'][ct] = {
            'n_regions': n_r, 'n_pairs': n_pairs, 'n_cells': n_cells,
            'n_blocks': n_samples, 'n_donors': len(uniq_donors),
            'n_shufflable_blocks': n_shufflable,
            'free_null_matrix': str(free_npy),
            'strat_null_matrix': str(strat_npy),
        }
        del X_ct, sample_means, free_null, strat_null
        gc.collect()

    f.close()

    # ============================================================
    # 7. Save per-CT table + published comparison + BH (m = 10)
    # ============================================================
    print("\n7. Saving per-CT table with published comparison + BH...")
    ct_df = pd.DataFrame(ct_test_rows)
    ct_df = ct_df.sort_values('omega_mean', ascending=False).reset_index(drop=True)

    def bh_q(pvals):
        p = np.asarray(pvals, float)
        m = len(p)
        order = np.argsort(p)
        ranked = p[order]
        q = ranked * m / np.arange(1, m + 1)
        q = np.minimum.accumulate(q[::-1])[::-1]
        out = np.empty(m)
        out[order] = np.minimum(q, 1.0)
        return out

    ct_df['free_q_BH'] = bh_q(ct_df['free_p_value'])
    ct_df['strat_q_BH'] = bh_q(ct_df['strat_p_value'])

    # published 08d values (buggy extraction) for side-by-side reference
    bs = pd.read_csv(RESULTS_DIR / 'brain_bs_null_ct_test.csv')
    bs = bs[['cell_type', 'omega_mean', 'p_value', 'null_mean', 'SES']].rename(
        columns={'omega_mean': 'pub08d_omega_mean', 'p_value': 'pub08d_p_value',
                 'null_mean': 'pub08d_null_mean', 'SES': 'pub08d_SES'})
    ct_df = ct_df.merge(bs, on='cell_type', how='left')

    out_csv = RESULTS_DIR / 'v38_donor_stratified_null.csv'
    ct_df.to_csv(out_csv, index=False)
    print(f"  Saved: {out_csv}")
    print("\n  Per-CT tests (corrected extraction; published = buggy 08d):")
    show_cols = ['cell_type', 'n_pairs', 'omega_mean', 'pub08d_omega_mean',
                 'free_p_value', 'free_SES', 'strat_p_value', 'strat_SES',
                 'strat_null_mean']
    print(ct_df[show_cols].to_string(index=False))

    # corrected landscape summary
    grand = float((ct_df['omega_mean'] * ct_df['n_pairs']).sum() / ct_df['n_pairs'].sum())
    grad = float(ct_df['omega_mean'].max() / ct_df['omega_mean'].min())
    print(f"\n  Corrected grand mean omega (pair-weighted): {grand:.3f}")
    print(f"  Corrected gradient (max/min class mean): {grad:.3f}")

    with open(RESULTS_DIR / 'v38_donor_stratified_manifest.json', 'w') as jf:
        json.dump(manifest, jf, indent=2, default=str)
    print("  Saved: results/v38_donor_stratified_manifest.json")
    print("\nDone!")


if __name__ == '__main__':
    main()
