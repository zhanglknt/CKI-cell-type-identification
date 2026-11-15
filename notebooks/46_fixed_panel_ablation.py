"""
Fixed Gene-Panel Ablation (46)
=============================
Addresses the circular-selection concern for the per-pair top-200 DE scheme
used by k_f in the brain regional analysis (reviewer issue R2-C3/R3):

    In the reported pipeline, the top-200 DE genes for a pair are selected
    using the |pseudobulk difference| of the SAME two pseudobulks on which
    k_f is then computed. Selection and evaluation share the same data.

This script recomputes the full observed brain landscape (all same-CT
cross-region pairs) under four k_f gene-selection schemes, holding everything
else identical (same keep gene set, same pseudobulks, same k_n):

    S0_perpair   : reported scheme -- per-pair top-200 by |pb_A - pb_B|
                   (circular selection; reference)
    S1_fixed2000 : fixed panel of the 2,000 non-HK genes with the highest
                   global mean expression (selected once, pair-independent)
    S2_loo200    : leave-pair-out panel -- for pair (i,j), the top-200 genes
                   ranked by the MEAN |difference| over all OTHER pairs of
                   the same cell type (adaptive but not circular for the
                   tested pair)
    S3_all5000   : all 5,000 non-HK genes in the keep set (no selection)

It also reruns the block-shuffle permutation null under the S2 scheme
(B = 200 by default) to verify that per-class significance is preserved
under a non-circular, scheme-matched null.

Outputs (RESULTS_DIR):
    fixed_panel_ablation_pairs.csv        pair-level omega/kf under all schemes
    fixed_panel_ablation_ct.csv           per-CT summary + S2 null test
    fixed_panel_ablation_null_<CT>.npy    S2 null pair-omega matrices (pairs x B)
    fixed_panel_ablation_summary.json     rank correlations, tier concordance,
                                          circularity inflation, key values

Usage:
    python 46_fixed_panel_ablation.py [--max-perm 200] [--observed-only]
"""

import sys, os, time, gc, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import h5py
from scipy.stats import spearmanr
from cki.core import js_divergence

# reuse the exact CSR extraction code of the reported pipeline (08d)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "brain08d", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "08d_brain_blockshuffle_null.py"))
brain08d = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(brain08d)
extract_csr_from_backed = brain08d.extract_csr_from_backed

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)


SCHEMES = ['s0', 's1', 's2', 's3']


def ct_observed_all_schemes(pbs, hk_idx, non_hk_idx, n_top, fixed_panel):
    """All four schemes for one cell type.

    Returns dict with keys 'kn', 'omega_<s>', 'kf_<s>' (arrays in i<j order).
    S0: per-pair top-n_top of own |diff| (circular; the reported scheme)
    S1: fixed panel (pair-independent)
    S2: leave-pair-out top-n_top of mean |diff| over the other pairs
    S3: all non-HK genes
    """
    n = len(pbs)
    n_pairs = n * (n - 1) // 2
    n_non_hk = len(non_hk_idx)
    top_n = min(n_top, n_non_hk)

    pair_list = []
    kn_arr = np.empty(n_pairs, dtype=np.float64)
    ad_all = np.empty((n_pairs, n_non_hk), dtype=np.float32)
    k = 0
    for i in range(n):
        pi = pbs[i]
        for j in range(i + 1, n):
            pj = pbs[j]
            kn_arr[k] = js_divergence(pi[hk_idx], pj[hk_idx])
            ad_all[k] = np.abs(pi[non_hk_idx] - pj[non_hk_idx])
            pair_list.append((i, j))
            k += 1
    ad_sum = ad_all.sum(axis=0, dtype=np.float64)

    kf = {s: np.empty(n_pairs, dtype=np.float64) for s in SCHEMES}
    for k, (i, j) in enumerate(pair_list):
        pi, pj = pbs[i], pbs[j]
        # S0 circular per-pair top-n_top
        tl = np.argpartition(ad_all[k], -top_n)[-top_n:]
        kf['s0'][k] = js_divergence(pi[non_hk_idx[tl]], pj[non_hk_idx[tl]])
        # S1 fixed panel
        kf['s1'][k] = js_divergence(pi[fixed_panel], pj[fixed_panel])
        # S2 leave-pair-out top-n_top
        if n_pairs > 1:
            loo_mean = (ad_sum - ad_all[k]) / (n_pairs - 1)
            tl2 = np.argpartition(loo_mean, -top_n)[-top_n:]
            kf['s2'][k] = js_divergence(pi[non_hk_idx[tl2]], pj[non_hk_idx[tl2]])
        else:  # degenerate; fall back to circular panel
            kf['s2'][k] = kf['s0'][k]
        # S3 all non-HK genes
        kf['s3'][k] = js_divergence(pi[non_hk_idx], pj[non_hk_idx])

    out = {'kn': kn_arr}
    for s in SCHEMES:
        with np.errstate(divide='ignore', invalid='ignore'):
            om = np.where(kn_arr > 1e-15, kf[s] / kn_arr, np.inf)
        out[f'omega_{s}'] = om
        out[f'kf_{s}'] = kf[s]
    return out


def loo_pair_omegas(pbs, hk_idx, non_hk_idx, n_top=200):
    """S2 (leave-pair-out) omegas for arbitrary pseudobulks (null use).

    For pair (i,j), the ranking statistic is the mean |diff| over all OTHER
    pairs of the same cell type, so the panel never sees the tested pair.
    """
    n = len(pbs)
    n_pairs = n * (n - 1) // 2
    n_non_hk = len(non_hk_idx)
    top_n = min(n_top, n_non_hk)
    if n_pairs < 2:
        omegas = np.empty(n_pairs, dtype=np.float64)
        k = 0
        for i in range(n):
            for j in range(i + 1, n):
                kn = js_divergence(pbs[i][hk_idx], pbs[j][hk_idx])
                ad = np.abs(pbs[i] - pbs[j])[non_hk_idx]
                tl = np.argpartition(ad, -top_n)[-top_n:]
                kf = js_divergence(pbs[i][non_hk_idx[tl]], pbs[j][non_hk_idx[tl]])
                omegas[k] = kf / kn if kn > 1e-15 else np.inf
                k += 1
        return omegas

    pair_list = []
    kn_arr = np.empty(n_pairs, dtype=np.float64)
    ad_all = np.empty((n_pairs, n_non_hk), dtype=np.float32)
    k = 0
    for i in range(n):
        pi = pbs[i]
        for j in range(i + 1, n):
            pj = pbs[j]
            kn_arr[k] = js_divergence(pi[hk_idx], pj[hk_idx])
            ad_all[k] = np.abs(pi[non_hk_idx] - pj[non_hk_idx])
            pair_list.append((i, j))
            k += 1
    ad_sum = ad_all.sum(axis=0, dtype=np.float64)

    omegas = np.empty(n_pairs, dtype=np.float64)
    for k, (i, j) in enumerate(pair_list):
        loo_mean = (ad_sum - ad_all[k]) / (n_pairs - 1)
        tl = np.argpartition(loo_mean, -top_n)[-top_n:]
        tg = non_hk_idx[tl]
        kf = js_divergence(pbs[i][tg], pbs[j][tg])
        omegas[k] = kf / kn_arr[k] if kn_arr[k] > 1e-15 else np.inf
    return omegas


def region_pbs_from_samples(assign_idx, weights, means, region_order):
    """Identical to 08d: weighted sample means -> norm 1e4 -> log1p."""
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


def add_tiers(pairs_df, omega_col):
    """Multiplicative residual model + tiers (identical to 08d section 6)."""
    df = pairs_df.copy()
    mu_grand = df[omega_col].mean()
    mu_ct = df.groupby('cell_type')[omega_col].mean().to_dict()
    mu_pair = df.groupby(['region_a', 'region_b'])[omega_col].mean().to_dict()
    df['mu_ct'] = df['cell_type'].map(mu_ct)
    df['mu_pair'] = df.apply(
        lambda r: mu_pair.get((r['region_a'], r['region_b']), mu_grand), axis=1)
    df['expected'] = df['mu_ct'] * df['mu_pair'] / mu_grand
    df['residual'] = df[omega_col] / df['expected']
    lowest = df.groupby(['region_a', 'region_b'])[omega_col].transform('min') == df[omega_col]
    df['lowest'] = lowest
    def tier(r):
        if r['residual'] < 0.3 and r[omega_col] < 15 and r['lowest']:
            return 'Strong'
        if r['residual'] < 0.5 and r[omega_col] < 25:
            return 'Moderate'
        if r['residual'] < 0.75 and r[omega_col] < 35:
            return 'Weak'
        return 'None'
    df['tier'] = df.apply(tier, axis=1)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-perm', type=int, default=200)
    ap.add_argument('--observed-only', action='store_true')
    args = ap.parse_args()

    B_PERM = args.max_perm
    RANDOM_SEED = 42
    MIN_NUCLEI = 20
    MIN_REGION_N = 50
    N_TOP_KF = 200
    N_HVG = 5000
    N_FIXED = 2000          # S1 fixed-panel size
    ct_col = 'supercluster_term'
    region_col = 'roi'
    sample_col = 'sample_id'

    rng = np.random.RandomState(RANDOM_SEED)
    t_start = time.time()

    # ============================================================
    # 1. HK genes (identical to 08d)
    # ============================================================
    print("=" * 60)
    print("1. Loading HK genes from HRT Atlas...")
    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().astype(str))
    print(f"  HRT Atlas: {len(hk_human)} human HK genes")

    # ============================================================
    # 2. Open backed h5ad, read gene symbols + obs codes (as 08d)
    # ============================================================
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
    ct_names = np.array(ct_cats)[ct_codes]
    roi_names = np.array(roi_cats)[roi_codes]

    hk_global = np.array(sorted({i for i, sym in enumerate(var_gene)
                                 if pd.notna(sym) and sym in hk_human}), dtype=int)
    print(f"  Matched HK genes: {len(hk_global)}")

    # ============================================================
    # 3. Global gene means -> keep set (identical to 08d, incl. argsort)
    # ============================================================
    print("\n3. Computing global gene means (keep-set selection)...")
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

    # S1 fixed panel: top-N_FIXED of the HVG pool by global mean
    # (hvg_global is sorted by descending global mean)
    fixed_panel = np.where(np.isin(keep_global, hvg_global[:N_FIXED]))[0]
    fixed_panel = np.sort(fixed_panel)
    assert len(fixed_panel) == N_FIXED
    print(f"  S1 fixed panel: {len(fixed_panel)} genes (top-{N_FIXED} by global mean)")

    # ============================================================
    # 4. Filter groups (identical to 08d)
    # ============================================================
    print("\n4. Filtering groups...")
    df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names, 'sample': samp_codes})
    groups = df_meta.groupby(['roi', 'ct']).size().reset_index(name='count')
    groups_ok = groups[groups['count'] >= MIN_NUCLEI]
    region_counts = df_meta['roi'].value_counts()
    regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
    groups_ok = groups_ok[groups_ok['roi'].isin(regions_ok)]
    cts_present = sorted(groups_ok['ct'].unique())
    print(f"  Groups passing: {len(groups_ok)} | CTs: {len(cts_present)}")

    ct_to_regions = {}
    for _, row in groups_ok.iterrows():
        ct_to_regions.setdefault(row['ct'], [])
        if row['roi'] not in ct_to_regions[row['ct']]:
            ct_to_regions[row['ct']].append(row['roi'])

    # ============================================================
    # 5. Per-CT observed landscape under 4 schemes + S2 null
    # ============================================================
    print("\n" + "=" * 60)
    print(f"5. Per-CT observed (4 schemes) + S2 block-shuffle null (B={B_PERM})")
    print("=" * 60)

    all_pair_rows = []
    ct_test_rows = []

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

        t0 = time.time()
        X_ct = extract_csr_from_backed(str(BRAIN_FILE), idx_sorted,
                                       keep_global, N_GENES)
        n_cells = X_ct.shape[0]
        print(f"    Extracted {n_cells} cells x {len(keep_global)} genes "
              f"({X_ct.nnz/1e6:.0f}M nnz, {time.time()-t0:.0f}s)")

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
        print(f"    Blocks (samples): {n_samples}")

        obs_pbs = region_pbs_from_samples(sample_region_idx,
                                          sample_weights, sample_means, region_order)

        res = ct_observed_all_schemes(obs_pbs, hk_in_reduced, non_hk_in_reduced,
                                       N_TOP_KF, fixed_panel)
        for s in SCHEMES:
            arr = res[f'omega_{s}']
            print(f"    omega_{s}: mean={np.nanmean(arr):.3f} "
                  f"median={np.nanmedian(arr):.3f}")
        print(f"    kn: mean={np.mean(res['kn']):.3e}")

        pair_idx_meta = []
        k = 0
        for i in range(n_r):
            for j in range(i + 1, n_r):
                pair_idx_meta.append((ct, region_order[i], region_order[j], k))
                k += 1

        for (ct_, ra, rb, pk) in pair_idx_meta:
            all_pair_rows.append({
                'cell_type': ct_, 'region_a': ra, 'region_b': rb, 'pair_idx': pk,
                'kn': res['kn'][pk],
                'omega_s0': res['omega_s0'][pk], 'kf_s0': res['kf_s0'][pk],
                'omega_s1': res['omega_s1'][pk], 'kf_s1': res['kf_s1'][pk],
                'omega_s2': res['omega_s2'][pk], 'kf_s2': res['kf_s2'][pk],
                'omega_s3': res['omega_s3'][pk], 'kf_s3': res['kf_s3'][pk],
            })
        row = {
            'cell_type': ct, 'n_regions': n_r, 'n_pairs': n_pairs,
            'n_cells': n_cells, 'n_blocks': n_samples,
            'omega_s0_mean': float(np.mean(res['omega_s0'])),
            'omega_s0_median': float(np.median(res['omega_s0'])),
            'omega_s1_mean': float(np.mean(res['omega_s1'])),
            'omega_s2_mean': float(np.mean(res['omega_s2'])),
            'omega_s3_mean': float(np.mean(res['omega_s3'])),
        }

        if not args.observed_only:
            # ---- S2-matched block-shuffle null ----
            null_pair_omegas = np.empty((n_pairs, B_PERM), dtype=np.float32)
            null_ct_means = np.empty(B_PERM, dtype=np.float64)
            t_bs = time.time()
            for b in range(B_PERM):
                perm_assign = sample_region_idx[rng.permutation(n_samples)]
                perm_pbs = region_pbs_from_samples(perm_assign, sample_weights,
                                                   sample_means, region_order)
                w = loo_pair_omegas(perm_pbs, hk_in_reduced, non_hk_in_reduced,
                                    N_TOP_KF)
                null_pair_omegas[:, b] = w
                null_ct_means[b] = np.mean(w)
                if (b + 1) % 20 == 0:
                    el = time.time() - t_bs
                    print(f"    null iter {b+1}/{B_PERM}, elapsed={el:.0f}s, "
                          f"ETA={el/(b+1)*(B_PERM-b-1):.0f}s")
            obs_mean = float(np.mean(res['omega_s2']))
            p_ct = (np.sum(null_ct_means >= obs_mean) + 1) / (B_PERM + 1)
            null_sd = float(np.std(null_ct_means))
            ses = ((obs_mean - float(np.mean(null_ct_means))) / null_sd
                   if null_sd > 1e-12 else 0.0)
            print(f"    S2 null: obs_mean={obs_mean:.3f}, "
                  f"null_mean={np.mean(null_ct_means):.3f}, p={p_ct:.5f}, SES={ses:.2f}")
            out_npy = RESULTS_DIR / f"fixed_panel_ablation_null_{ct.replace(' ', '_')}.npy"
            np.save(out_npy, null_pair_omegas)
            row.update({
                's2_obs_mean': obs_mean,
                's2_null_mean': float(np.mean(null_ct_means)),
                's2_null_sd': null_sd,
                's2_p_value': p_ct, 's2_SES': ses,
            })
        ct_test_rows.append(row)

        del X_ct, sample_means
        gc.collect()
        print(f"    CT done in {time.time()-t_ct:.0f}s")

    f.close()

    # ============================================================
    # 6. Save pairs + per-CT table
    # ============================================================
    print("\n6. Saving pairs + per-CT table...")
    pairs_df = pd.DataFrame(all_pair_rows)
    out_csv = RESULTS_DIR / 'fixed_panel_ablation_pairs.csv'
    pairs_df.to_csv(out_csv, index=False)
    print(f"  Saved: {out_csv} ({len(pairs_df)} pairs)")

    ct_df = pd.DataFrame(ct_test_rows).sort_values('omega_s0_mean', ascending=False)
    ct_df.to_csv(RESULTS_DIR / 'fixed_panel_ablation_ct.csv', index=False)
    print(f"  Saved: fixed_panel_ablation_ct.csv")

    # ============================================================
    # 7. Validation: S0 must reproduce the reported observed landscape
    # ============================================================
    print("\n7. Validating S0 against reported brain_bs_null_observed_pairs.csv ...")
    ref = pd.read_csv(RESULTS_DIR / 'brain_bs_null_observed_pairs.csv')
    m = pairs_df.merge(ref, on=['cell_type', 'region_a', 'region_b'], how='inner')
    print(f"  Matched {len(m)}/{len(pairs_df)} pairs with reference")
    if len(m) == len(pairs_df) and len(m) > 0:
        d = np.abs(m['omega_s0'] - m['omega'])
        print(f"  max |omega_s0 - omega_ref| = {d.max():.3e}, mean = {d.mean():.3e}")
        if d.max() > 1e-6:
            print("  WARNING: S0 differs from reference beyond 1e-6!")
    else:
        print("  WARNING: pair sets differ from reference!")

    # ============================================================
    # 8. Summary statistics
    # ============================================================
    print("\n8. Summary statistics...")
    summary = {'B_perm_s2_null': B_PERM,
               'n_pairs': int(len(pairs_df)),
               'n_cts': int(ct_df.shape[0]),
               'panel_sizes': {'s0_perpair': N_TOP_KF, 's1_fixed': N_FIXED,
                               's2_loo': N_TOP_KF, 's3_all': int(len(non_hk_in_reduced))}}

    # pair-level rank correlations between schemes
    for s in ['s1', 's2', 's3']:
        rho, p = spearmanr(pairs_df['omega_s0'], pairs_df[f'omega_{s}'])
        summary[f'spearman_pair_s0_vs_{s}'] = {'rho': float(rho), 'p': float(p)}

    # per-CT mean rank correlations
    for s in ['s1', 's2', 's3']:
        rho, p = spearmanr(ct_df['omega_s0_mean'], ct_df[f'omega_{s}_mean'])
        summary[f'spearman_ctmean_s0_vs_{s}'] = {'rho': float(rho), 'p': float(p)}

    # key values per scheme
    for s in SCHEMES:
        summary[f'grand_mean_{s}'] = float(pairs_df[f'omega_{s}'].mean())
    ast = ct_df[ct_df['cell_type'] == 'Astrocyte'].iloc[0]
    bg = ct_df[ct_df['cell_type'] == 'Bergmann glia'].iloc[0]
    for s in SCHEMES:
        col = f'omega_{s}_mean'
        summary[f'astro_mean_{s}'] = float(ast[col])
        summary[f'bergmann_mean_{s}'] = float(bg[col])
        summary[f'astro_over_bergmann_{s}'] = float(ast[col] / bg[col])

    # circularity inflation: kf ratios on same pairs
    for s in ['s1', 's2', 's3']:
        ratio = pairs_df['kf_s0'] / pairs_df[f'kf_{s}']
        summary[f'kf_ratio_s0_over_{s}'] = {
            'median': float(np.nanmedian(ratio)),
            'q25': float(np.nanpercentile(ratio, 25)),
            'q75': float(np.nanpercentile(ratio, 75)),
        }

    # tier concordance (data-driven residual model, per scheme)
    tier_counts = {}
    tier_jaccard = {}
    s0_tiers = add_tiers(pairs_df, 'omega_s0')
    tier_counts['s0'] = s0_tiers['tier'].value_counts().to_dict()
    cand_s0 = set(s0_tiers.loc[s0_tiers['tier'].isin(['Strong', 'Moderate']),
                               ['cell_type', 'region_a', 'region_b']]
                  .apply(tuple, axis=1))
    for s in ['s1', 's2', 's3']:
        tdf = add_tiers(pairs_df, f'omega_{s}')
        tier_counts[s] = tdf['tier'].value_counts().to_dict()
        cand = set(tdf.loc[tdf['tier'].isin(['Strong', 'Moderate']),
                           ['cell_type', 'region_a', 'region_b']].apply(tuple, axis=1))
        inter = len(cand_s0 & cand)
        union = len(cand_s0 | cand)
        tier_jaccard[s] = {'n_s0': len(cand_s0), 'n_scheme': len(cand),
                           'intersection': inter,
                           'jaccard': inter / union if union else 1.0}
    summary['tier_counts'] = tier_counts
    summary['tier_candidate_jaccard_vs_s0'] = tier_jaccard

    with open(RESULTS_DIR / 'fixed_panel_ablation_summary.json', 'w') as jf:
        json.dump(summary, jf, indent=2, default=str)
    print(json.dumps(summary, indent=2, default=str)[:4000])

    print(f"\nDone! Total time: {time.time()-t_start:.0f}s")


if __name__ == '__main__':
    main()
