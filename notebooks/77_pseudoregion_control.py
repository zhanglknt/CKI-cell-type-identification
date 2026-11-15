# -*- coding: utf-8 -*-
"""
Pseudo-region negative control for the brain block-shuffle null (77)
====================================================================
Reviewer request (v40 round, E1-M3 / P2-4):
  "将每 region 的文库随机对半分为两个'伪区域'，跑同一 block-shuffle 检验，
   验证 per-pair P 的均匀性（QQ 图）" — i.e. a design-matched negative
  control that isolates null calibration from real regional structure.

Design (identical to 08d wherever possible)
---------------------------------------------
- Gene set: HRT Atlas HK genes + top-5000 non-HK HVG by global mean
  (same selection as 08d; gene model cached in
  results/pseudoregion_control_genemodel.npz).
- Group filter: MIN_NUCLEI=20 per (region, CT), MIN_REGION_N=50 per region,
  and >=2 libraries in the (region, CT) group (needed to split).
- Pseudo-regions: within each CT, every eligible region's libraries are
  split uniformly at random into halves A/B (seeded).  The observed
  pseudo-landscape is the omega matrix over all C(2R, 2) pseudo pairs.
  Pairs (A_i, B_i) are "same-origin" (both halves of one real region);
  all other pairs are "cross-origin".
- Block-shuffle null: exactly as 08d — permute sample -> pseudo-region
  labels preserving the observed per-pseudo-region library-count multiset;
  B=1000 (default).
- Per-pair P: one-sided lower  P = (#{null <= obs} + 1)/(B + 1) and upper
  P = (#{null >= obs} + 1)/(B + 1), exactly as 08e.
- Diagnostics: KS test vs U(0,1), binomial tail tests, same-origin vs
  cross-origin decomposition, per-CT table, and a QQ figure.

Why this is informative
-----------------------
Under exchangeability (no library-level structure), the random split is
drawn from the same assignment space as the null, so per-pair P values are
uniform by construction; deviations therefore measure library-level
grouping structure (donor / dissection / batch effects tied to region),
which is exactly the "null width mismatch" concern raised for the real
analysis.  The same-origin / cross-origin split additionally localises
whether within-region library similarity drives any deviation.

Outputs (RESULTS_DIR):
  pseudoregion_control_pairs.csv        per-pair records
  pseudoregion_control_summary.json     machine-readable summary
  pseudoregion_control_summary.txt      human-readable summary
  pseudoregion_control_genemodel.npz    gene-model cache
  results/figures_final/pseudoregion_control_qq.{png,pdf}   (--qq-only)

Usage
-----
  python 77_pseudoregion_control.py [--max-perm 1000] [--workers 5]
  python 77_pseudoregion_control.py --qq-only
  python 77_pseudoregion_control.py --ct "Bergmann glia" --max-perm 50   # debug
"""

import sys, os, time, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import RESULTS_DIR, BRAIN_FILE, HK_FILE

import numpy as np
import pandas as pd
import h5py
from scipy.sparse import csr_matrix

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

# Optional detached logging: when CKI_DETACHED_LOG points to a file, all
# print output (in this process and in multiprocessing-spawned workers,
# which re-execute this module-level code) is appended to that file at the
# Python level.  The OS-level stdio handles are left untouched so the
# launcher-side pipes never see EOF (detached-run compatibility).
_DETACHED_LOG = os.environ.get('CKI_DETACHED_LOG')
if _DETACHED_LOG:
    _log_fh = open(_DETACHED_LOG, 'a', buffering=1, encoding='utf-8')
    sys.stdout = _log_fh
    sys.stderr = _log_fh

_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)

# ---------------------------------------------------------------- constants
SEED_SPLIT = 20260903
SEED_PERM_BASE = 777000
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
CT_COL = 'supercluster_term'
REGION_COL = 'roi'
SAMPLE_COL = 'sample_id'

GENEMODEL_NPZ = RESULTS_DIR / 'pseudoregion_control_genemodel.npz'
OUT_PAIRS = RESULTS_DIR / 'pseudoregion_control_pairs.csv'
OUT_SUMMARY_JSON = RESULTS_DIR / 'pseudoregion_control_summary.json'
OUT_SUMMARY_TXT = RESULTS_DIR / 'pseudoregion_control_summary.txt'
FIG_DIR = RESULTS_DIR / 'figures_final'

REAL_RESULTS = RESULTS_DIR / 'brain_bs_null_results.csv'


# ---------------------------------------------------------------- 08d import
def _import_08d():
    """Import 08d to reuse its exact extraction / pair-omega code."""
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     '08d_brain_blockshuffle_null.py')
    spec = importlib.util.spec_from_file_location('bsn08d', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# region_pbs_from_samples — VERBATIM from 08d (nested there, copied here)
def region_pbs_from_samples(assign_idx, weights, means):
    """assign_idx: sample -> region index. Return list of pbs."""
    pbs = []
    for r in range(int(assign_idx.max()) + 1 if len(assign_idx) else 0):
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


# ---------------------------------------------------------------- parent
def load_gene_model():
    """HK + HVG selection identical to 08d; cached."""
    if GENEMODEL_NPZ.exists():
        z = np.load(GENEMODEL_NPZ, allow_pickle=False)
        print(f"  Gene model cache hit: {GENEMODEL_NPZ}")
        return (z['keep_global'], z['hk_in_reduced'], z['non_hk_in_reduced'],
                z['gene_sums'], int(z['n_cells']), int(z['n_genes']))

    print("  Loading HK genes from HRT Atlas...")
    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().astype(str))

    f = h5py.File(BRAIN_FILE, 'r')
    X = f['X']
    indptr_full = X['indptr'][:]
    N_CELLS = indptr_full.shape[0] - 1

    # gene symbols
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

    hk_global = np.array(sorted({i for i, sym in enumerate(var_gene)
                                 if pd.notna(sym) and sym in hk_human}), dtype=int)
    print(f"  Matched HK genes: {len(hk_global)}")

    print("  Computing global gene means (HVG selection)...")
    t0 = time.time()
    gene_sums = np.zeros(N_GENES, dtype=np.float64)
    BATCH = 50000
    for start in range(0, N_CELLS, BATCH):
        end = min(start + BATCH, N_CELLS)
        lo, hi = int(indptr_full[start]), int(indptr_full[end])
        data_batch = X['data'][lo:hi]
        idx_batch = X['indices'][lo:hi]
        np.add.at(gene_sums, idx_batch, data_batch)
    print(f"  Means computed in {time.time()-t0:.0f}s")
    f.close()

    gene_means = gene_sums / N_CELLS
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

    np.savez(GENEMODEL_NPZ, keep_global=keep_global,
             hk_in_reduced=hk_in_reduced, non_hk_in_reduced=non_hk_in_reduced,
             gene_sums=gene_sums, n_cells=N_CELLS, n_genes=N_GENES)
    return keep_global, hk_in_reduced, non_hk_in_reduced, gene_sums, N_CELLS, N_GENES


def read_obs_meta():
    f = h5py.File(BRAIN_FILE, 'r')
    obs = f['obs']
    def read_codes(name):
        g = obs[name]
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g['categories'][:]]
        codes = g['codes'][:]
        return codes, cats
    ct_codes, ct_cats = read_codes(CT_COL)
    roi_codes, roi_cats = read_codes(REGION_COL)
    samp_codes, _ = read_codes(SAMPLE_COL)
    f.close()
    return (np.array(ct_cats)[ct_codes], np.array(roi_cats)[roi_codes], samp_codes)


def build_ct_jobs(keep_global):
    """Per CT: eligible regions, random split into pseudo A/B, cell indices."""
    ct_names, roi_names, samp_codes = read_obs_meta()
    df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names, 'sample': samp_codes})
    groups = df_meta.groupby(['roi', 'ct']).size().reset_index(name='count')
    groups_ok = groups[groups['count'] >= MIN_NUCLEI]
    region_counts = df_meta['roi'].value_counts()
    regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
    groups_ok = groups_ok[groups_ok['roi'].isin(regions_ok)]

    rng = np.random.RandomState(SEED_SPLIT)
    jobs = []
    for ct_i, ct in enumerate(sorted(groups_ok['ct'].unique())):
        regs = sorted(groups_ok[groups_ok['ct'] == ct]['roi'])
        # libraries per region for this CT
        sub = df_meta[df_meta['ct'] == ct]
        lib_per_region = sub.groupby('roi')['sample'].nunique()
        regs = [r for r in regs if lib_per_region.get(r, 0) >= 2]
        if len(regs) < 2:
            continue
        n_r = len(regs)
        n_pairs = (2 * n_r) * (2 * n_r - 1) // 2

        # cells of this CT (all regions), sorted by global index for IO
        ct_bool = (ct_names == ct) & np.isin(roi_names, regs)
        cell_idx = np.where(ct_bool)[0]
        cell_roi = roi_names[cell_idx]
        cell_samp = samp_codes[cell_idx]

        # deterministic random split of each region's libraries into A/B
        sample_uniq = np.unique(cell_samp)
        samp_region = {}
        for s in sample_uniq:
            m = cell_samp == s
            samp_region[int(s)] = cell_roi[m][0]
        split_of_sample = {}
        for r in regs:
            libs = sorted(int(s) for s in sample_uniq if samp_region[s] == r)
            order = rng.permutation(len(libs))
            k = (len(libs) + 1) // 2
            for pos in order[:k]:
                split_of_sample[libs[pos]] = 0        # A
            for pos in order[k:]:
                split_of_sample[libs[pos]] = 1        # B

        # pseudo-region code: 2*i + (0=A, 1=B), region order = regs (sorted)
        pseudo_code_of_sample = {
            s: 2 * regs.index(samp_region[s]) + split_of_sample[s]
            for s in sample_uniq
        }
        n_pseudo = 2 * n_r
        assign = np.array([pseudo_code_of_sample[int(s)] for s in cell_samp],
                          dtype=np.int64)
        jobs.append({
            'ct': ct, 'ct_index': ct_i, 'regions': regs, 'n_pairs': n_pairs,
            'n_pseudo': n_pseudo,
            'cell_idx_sorted': cell_idx[np.argsort(cell_idx)],
            'samp_sorted': cell_samp[np.argsort(cell_idx)],
            'assign_sorted': assign[np.argsort(cell_idx)],
            'keep_global': keep_global,
        })
        print(f"    {ct}: {n_r} regions -> {n_pseudo} pseudo-regions, "
              f"{n_pairs} pseudo pairs")
    return jobs


# ---------------------------------------------------------------- worker
def ct_worker(job, max_perm):
    """Run the pseudo-region block-shuffle test for one CT. Returns records."""
    b08d = _import_08d()
    from cki.core import js_divergence  # noqa: F401 (import parity with 08d)

    ct = job['ct']
    n_pseudo = job['n_pseudo']
    n_pairs = job['n_pairs']
    keep_global = job['keep_global']
    cell_idx = job['cell_idx_sorted']
    samp_sorted = job['samp_sorted']
    assign_sorted = job['assign_sorted']

    t_ct = time.time()
    print(f"  --- {ct} ({n_pseudo} pseudo-regions, {n_pairs} pairs) ---")

    # N_GENES from the cached gene model (avoids re-parsing the var group)
    z0 = np.load(GENEMODEL_NPZ, allow_pickle=False)
    N_GENES = int(z0['n_genes'])

    # ---- streaming sample means over kept genes (memory-bounded) ----
    uniq_samp, samp_inv_sorted = np.unique(samp_sorted, return_inverse=True)
    n_samples = len(uniq_samp)
    n_keep = len(keep_global)
    sums = np.zeros((n_samples, n_keep), dtype=np.float64)
    cnts = np.zeros(n_samples, dtype=np.int64)
    CH = 20000
    t0 = time.time()
    for s0 in range(0, len(cell_idx), CH):
        cells = cell_idx[s0:s0 + CH]
        sidx = samp_inv_sorted[s0:s0 + CH]
        Xc = b08d.extract_csr_from_backed(str(BRAIN_FILE), cells,
                                          keep_global, N_GENES)
        n_c = Xc.shape[0]
        S = csr_matrix((np.ones(n_c, dtype=np.float32),
                        (np.arange(n_c), sidx)),
                       shape=(n_c, n_samples))
        sums += np.asarray((S.T @ Xc).toarray())
        cnts += np.bincount(sidx, minlength=n_samples)
    sample_means = sums / np.maximum(cnts, 1)[:, None]
    sample_weights = cnts.astype(np.float64)
    print(f"    Extracted {len(cell_idx)} cells / {n_samples} libraries "
          f"({time.time()-t0:.0f}s)")

    # gene model in reduced space (from the cached global model, identical to 08d)
    hk_in_reduced = z0['hk_in_reduced']
    non_hk_in_reduced = z0['non_hk_in_reduced']

    # pseudo assignment per unique-sample row
    # assign_sorted is per cell; collapse to per unique sample
    assign_per_sample = np.empty(n_samples, dtype=np.int64)
    assign_per_sample[samp_inv_sorted] = assign_sorted

    # ---- observed pseudo landscape ----
    obs_pbs = region_pbs_from_samples(assign_per_sample, sample_weights,
                                      sample_means)
    obs_omegas = b08d.pair_omegas(obs_pbs, n_pairs, hk_in_reduced,
                                  non_hk_in_reduced, N_TOP_KF)
    print(f"    Observed: mean={np.nanmean(obs_omegas):.3f}, "
          f"median={np.nanmedian(obs_omegas):.3f}")

    # ---- block-shuffle null ----
    rng = np.random.RandomState(SEED_PERM_BASE + job['ct_index'])
    n_le = np.zeros(n_pairs, dtype=np.int32)
    n_ge = np.zeros(n_pairs, dtype=np.int32)
    t_bs = time.time()
    for b in range(max_perm):
        perm_assign = assign_per_sample[rng.permutation(n_samples)]
        perm_pbs = region_pbs_from_samples(perm_assign, sample_weights,
                                           sample_means)
        null_w = b08d.pair_omegas(perm_pbs, n_pairs, hk_in_reduced,
                                  non_hk_in_reduced, N_TOP_KF)
        n_le += (null_w <= obs_omegas)
        n_ge += (null_w >= obs_omegas)
        if (b + 1) % 100 == 0:
            el = time.time() - t_bs
            eta = el / (b + 1) * (max_perm - b - 1)
            print(f"    [{ct}] iter {b+1}/{max_perm}, elapsed={el:.0f}s, "
                  f"ETA={eta:.0f}s")
    p_low = (n_le + 1) / (max_perm + 1)
    p_high = (n_ge + 1) / (max_perm + 1)
    print(f"    [{ct}] done in {time.time()-t_bs:.0f}s "
          f"(total {time.time()-t_ct:.0f}s)")

    # ---- pair records ----
    regions = job['regions']
    pseudo_names = []
    for r in regions:
        pseudo_names.append(f"{r}::A")
        pseudo_names.append(f"{r}::B")
    recs = []
    k = 0
    for i in range(n_pseudo):
        for j in range(i + 1, n_pseudo):
            same_origin = (i // 2) == (j // 2)
            recs.append((ct, pseudo_names[i], pseudo_names[j], k,
                         float(obs_omegas[k]), same_origin,
                         float(p_low[k]), float(p_high[k])))
            k += 1
    return recs, {
        'cell_type': ct, 'n_pseudo_regions': n_pseudo, 'n_pairs': n_pairs,
        'n_cells': int(len(cell_idx)), 'n_libraries': int(n_samples),
        'omega_mean': float(np.nanmean(obs_omegas)),
        'p_low_mean': float(np.mean(p_low)),
        'p_high_mean': float(np.mean(p_high)),
    }


# ---------------------------------------------------------------- summary
def make_summary(pairs_df, ct_rows, B, real_ref):
    from scipy import stats
    n = len(pairs_df)
    lo = pairs_df['p_low'].values
    hi = pairs_df['p_high'].values
    same = pairs_df['same_origin'].values.astype(bool)

    def block(pv, mask, label):
        v = pv[mask]
        m = len(v)
        rate = float((v < 0.05).mean())
        ks = stats.kstest(v, 'uniform')
        binom = stats.binomtest(int((v < 0.05).sum()), m, 0.05,
                                alternative='two-sided')
        return {
            'label': label, 'n_pairs': int(m), 'tail_rate': rate,
            'tail_count': int((v < 0.05).sum()),
            'binom_p': float(binom.pvalue),
            'ks_stat': float(ks.statistic), 'ks_p': float(ks.pvalue),
        }

    out = {
        'B': B, 'seed_split': SEED_SPLIT, 'seed_perm_base': SEED_PERM_BASE,
        'n_pairs_total': int(n),
        'overall_lower': block(lo, np.ones(n, bool), 'all pairs (lower tail)'),
        'overall_upper': block(hi, np.ones(n, bool), 'all pairs (upper tail)'),
        'same_origin_lower': block(lo, same, 'same-origin (lower tail)'),
        'same_origin_upper': block(hi, same, 'same-origin (upper tail)'),
        'cross_origin_lower': block(lo, ~same, 'cross-origin (lower tail)'),
        'cross_origin_upper': block(hi, ~same, 'cross-origin (upper tail)'),
        'per_ct': ct_rows,
        'real_data_reference': real_ref,
    }
    return out


def real_data_reference():
    df = pd.read_csv(REAL_RESULTS)
    return {
        'n_pairs': int(len(df)),
        'lower_tail_rate': float((df['p_perm'] < 0.05).mean()),
        'upper_tail_rate': float((df['p_perm_high'] < 0.05).mean()),
    }


def write_summary_txt(summary):
    L = []
    L.append("Pseudo-region negative control for the brain block-shuffle null")
    L.append("=" * 70)
    L.append(f"B = {summary['B']} permutations; split seed = {summary['seed_split']}")
    L.append(f"Pseudo pairs total = {summary['n_pairs_total']}")
    L.append("")
    for key in ['overall_lower', 'overall_upper', 'same_origin_lower',
                'same_origin_upper', 'cross_origin_lower', 'cross_origin_upper']:
        b = summary[key]
        L.append(f"[{b['label']}] n={b['n_pairs']}  "
                 f"tail(P<0.05)={b['tail_rate']:.3%}  "
                 f"binom P={b['binom_p']:.3g}  KS D={b['ks_stat']:.4f} "
                 f"(P={b['ks_p']:.3g})")
    rr = summary['real_data_reference']
    L.append("")
    L.append(f"Real-data reference (brain_bs_null_results.csv): "
             f"lower tail {rr['lower_tail_rate']:.3%}, "
             f"upper tail {rr['upper_tail_rate']:.3%}")
    L.append("")
    L.append("Per-CT:")
    for r in summary['per_ct']:
        L.append(f"  {r['cell_type']:40s} pairs={r['n_pairs']:6d} "
                 f"mean(p_low)={r['p_low_mean']:.3f} "
                 f"mean(p_high)={r['p_high_mean']:.3f}")
    return "\n".join(L)


# ---------------------------------------------------------------- QQ figure
def qq_figure():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from scipy import stats

    df = pd.read_csv(OUT_PAIRS)
    same = df['same_origin'].values.astype(bool)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        'font.family': 'Arial', 'font.size': 8,
        'axes.linewidth': 0.8, 'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
    })
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.3))

    panels = [('p_low', 'Lower-tail P', axes[0]),
              ('p_high', 'Upper-tail P', axes[1])]
    for col, title, ax in panels:
        v_all = np.sort(df[col].values)
        v_same = np.sort(df.loc[same, col].values)
        v_cross = np.sort(df.loc[~same, col].values)

        def qq(v, color, label, n_ref=None):
            n = len(v)
            expected = (np.arange(1, n + 1) - 0.5) / n
            ax.plot(expected, v, '.', ms=1.6, color=color, label=label,
                    rasterized=True)

        qq(v_all, '#3B6FB6', 'all pairs')
        qq(v_same, '#D9531E', 'same-origin')
        qq(v_cross, '#2E9E7A', 'cross-origin')
        ax.plot([0, 1], [0, 1], '-', lw=0.8, color='0.35', zorder=0)
        ax.set_xlabel('Expected P (uniform)')
        ax.set_ylabel('Observed P')
        ax.set_title(title, fontsize=9)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_aspect('equal')
        rate_all = (df[col] < 0.05).mean()
        rate_same = (df.loc[same, col] < 0.05).mean()
        rate_cross = (df.loc[~same, col] < 0.05).mean()
        ks_p = stats.kstest(df[col].values, 'uniform').pvalue
        ax.text(0.03, 0.97,
                f"tail P<0.05: all {rate_all:.1%}\n"
                f"same-origin {rate_same:.1%} | "
                f"cross {rate_cross:.1%}\nKS P = {ks_p:.2g}",
                transform=ax.transAxes, va='top', ha='left', fontsize=7)
        ax.legend(loc='lower right', fontsize=7, frameon=False,
                  handletextpad=0.2)
    fig.tight_layout()
    png = FIG_DIR / 'pseudoregion_control_qq.png'
    pdf = FIG_DIR / 'pseudoregion_control_qq.pdf'
    fig.savefig(png, dpi=300)
    fig.savefig(pdf)
    plt.close(fig)
    print(f"Saved: {png}")
    print(f"Saved: {pdf}")


# ---------------------------------------------------------------- checkpoints
PAIR_COLS = ['cell_type', 'pseudo_a', 'pseudo_b', 'pair_idx', 'omega',
             'same_origin', 'p_low', 'p_high']
CKPT_DIR = RESULTS_DIR / 'pseudoregion_ct_ckpt'

def _ckpt_files(ct):
    safe = ct.replace(' ', '_').replace('/', '-').replace('\\', '-')
    cf = CKPT_DIR / f"{safe}.csv"
    return cf, cf.with_suffix('.json')

def _load_ckpt(ct):
    """Load a completed per-CT checkpoint, or return None."""
    cf, jf = _ckpt_files(ct)
    if cf.exists() and jf.exists():
        try:
            df = pd.read_csv(cf)
            if len(df) == 0:
                return None
            row = json.loads(jf.read_text(encoding='utf-8'))
            recs = list(df.itertuples(index=False, name=None))
            return recs, row
        except Exception:
            return None
    return None

def _save_ckpt(ct, recs, row):
    CKPT_DIR.mkdir(parents=True, exist_ok=True)
    cf, jf = _ckpt_files(ct)
    pd.DataFrame(recs, columns=PAIR_COLS).to_csv(cf, index=False)
    jf.write_text(json.dumps(row), encoding='utf-8')


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--max-perm', type=int, default=1000)
    ap.add_argument('--workers', type=int, default=5)
    ap.add_argument('--ct', default=None, help='restrict to one cell type (debug)')
    ap.add_argument('--qq-only', action='store_true')
    ap.add_argument('--reset-ckpt', action='store_true',
                    help='delete per-CT checkpoints before running')
    args = ap.parse_args()

    if args.qq_only:
        qq_figure()
        return

    print("=" * 60)
    print("Pseudo-region negative control (77)")
    print("=" * 60)

    print("\n1. Gene model (HK + HVG5000, as in 08d)...")
    keep_global, hk_in_reduced, non_hk_in_reduced, gene_sums, N_CELLS, N_GENES = \
        load_gene_model()

    print("\n2. Building pseudo-region split per CT...")
    jobs = build_ct_jobs(keep_global)
    if args.ct:
        jobs = [j for j in jobs if j['ct'] == args.ct]
    total_pairs = sum(j['n_pairs'] for j in jobs)
    print(f"  CTs: {len(jobs)}, total pseudo pairs: {total_pairs}")
    # biggest first for scheduling
    jobs.sort(key=lambda j: -j['n_pairs'])

    if args.reset_ckpt and CKPT_DIR.exists():
        import shutil
        shutil.rmtree(CKPT_DIR)
        print(f"  [ckpt] cleared {CKPT_DIR}")

    # ---- per-CT checkpoints: skip completed CTs ----
    all_recs, ct_rows = [], []
    pending = []
    n_skipped = 0
    for job in jobs:
        ck = _load_ckpt(job['ct'])
        if ck is not None:
            recs, row = ck
            all_recs.extend(recs)
            ct_rows.append(row)
            n_skipped += 1
            print(f"  [ckpt] {job['ct']}: {len(recs)} pairs loaded")
        else:
            pending.append(job)
    if n_skipped:
        print(f"  [ckpt] resumed: {n_skipped} CT(s) skipped, "
              f"{len(pending)} to compute")

    print(f"\n3. Pseudo-region block-shuffle test (B={args.max_perm}, "
          f"workers={args.workers})...")
    if args.workers <= 1 or len(pending) == 1:
        for job in pending:
            recs, row = ct_worker(job, args.max_perm)
            _save_ckpt(job['ct'], recs, row)
            print(f"  [main] collected {job['ct']}: {len(recs)} pairs "
                  f"(checkpointed)")
            all_recs.extend(recs)
            ct_rows.append(row)
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(ct_worker, job, args.max_perm): job['ct']
                    for job in pending}
            from concurrent.futures import as_completed
            for fut in as_completed(futs):
                ct = futs[fut]
                try:
                    recs, row = fut.result()
                except Exception as e:
                    print(f"  !! {ct} FAILED: {type(e).__name__}: {e}")
                    raise
                _save_ckpt(ct, recs, row)
                print(f"  [main] collected {ct}: {len(recs)} pairs "
                      f"(checkpointed)")
                all_recs.extend(recs)
                ct_rows.append(row)

    print("\n4. Writing outputs...")
    pairs_df = pd.DataFrame(all_recs, columns=PAIR_COLS)
    pairs_df = pairs_df.sort_values(['cell_type', 'pair_idx']).reset_index(drop=True)
    pairs_df.to_csv(OUT_PAIRS, index=False)
    print(f"  Saved: {OUT_PAIRS} ({len(pairs_df)} pairs)")

    ct_rows.sort(key=lambda r: r['cell_type'])
    summary = make_summary(pairs_df, ct_rows, args.max_perm,
                           real_data_reference())
    with open(OUT_SUMMARY_JSON, 'w') as jf:
        json.dump(summary, jf, indent=2)
    txt = write_summary_txt(summary)
    OUT_SUMMARY_TXT.write_text(txt, encoding='utf-8')
    print(txt)
    print(f"  Saved: {OUT_SUMMARY_JSON}")
    print(f"  Saved: {OUT_SUMMARY_TXT}")

    print("\n5. QQ figure...")
    qq_figure()
    print("\nDone!")


if __name__ == '__main__':
    main()
