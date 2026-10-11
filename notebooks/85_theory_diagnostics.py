"""
Theory diagnostics for the scoped theoretical framework (SI Note 20, #1145).

Four diagnostics, feeding the wording strength of Note 20:

  A. Quadratic-regime check. For real pairs (TS cross-organ populations,
     TS split-half nulls, brain cross-region observed, brain split-half
     nulls), compare JS(p, p+d) against its second-order expansion
     Q = (1/(8 ln 2)) * sum(d_i^2 / p_i). Reports |JS - Q| / JS and the
     cubic-to-quadratic ratio sum|d|^3/p^2 / sum d^2/p per panel
     (HK panel = k_n scale; pair-specific top-200 panel = k_f scale).

  B. Background-energy exchangeability. On split-half null pairs, compare
     the per-gene background energy e_i = d_i^2 / p_i between the HK panel
     and the pair-specific top-200 panel: per-gene Spearman/Pearson
     correlation and per-gene mean-energy ratio. Tests condition C2
     (background drift is shared across panels).

  C. Null ancillarity (Q2 added value). From existing split-half products
     (brain + mouse + TS), compute the cross-class dispersion of the null
     k_f distribution vs the null omega distribution (CV and max/min of
     class-level null medians). If omega's null is tighter across classes,
     a single global calibration is legitimate for omega but not for k_f.

  D. Ground-truth monotonicity + invariance. From
     groundtruth_simulation_background2_raw.csv (factorial delta x eta x
     eps) and nonhk_drift_v45_raw.csv: omega vs functional shift delta at
     fixed background (monotonicity), omega vs background drift eta at
     delta = 0 (invariance), k_f under the same contrasts (control), and
     linearity of omega - 1 in delta (quadratic regime vs saturation).

Outputs (into RESULTS_DIR):
  theory_diagnostics.csv   long-format per-pair / per-contrast metrics
  theory_diagnostics.md    human-readable summary tables

Usage
-----
    python notebooks/85_theory_diagnostics.py
"""

import sys, os, time, gc, importlib.util
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
import h5py
from scipy.sparse import issparse
from scipy.stats import spearmanr, pearsonr
from cki.core import js_divergence

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)

RANDOM_SEED = 42
N_TOP_KF = 200
N_PAIRS_TARGET = 500
LN2 = np.log(2.0)

rng = np.random.RandomState(RANDOM_SEED)

# import the chunked backed reader from 08d (no side effects at import)
_spec = importlib.util.spec_from_file_location(
    "bs08d", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "08d_brain_blockshuffle_null.py"))
_bs08d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bs08d)
extract_csr_from_backed = _bs08d.extract_csr_from_backed

ROWS = []  # long-format output rows


# ----------------------------------------------------------------------
# core diagnostics
# ----------------------------------------------------------------------
def softmax_norm(x):
    x = np.asarray(x, dtype=np.float64)
    e = np.exp(x - x.max())
    return e / (e.sum() + 1e-9)


def panel_diag(xa, xb):
    """Second-order expansion diagnostics for one gene panel."""
    p = softmax_norm(xa)
    q = softmax_norm(xb)
    d = q - p
    js = float(js_divergence(xa, xb))
    quad_terms = d * d / p
    quad = float(quad_terms.sum())
    Q = quad / (8.0 * LN2)
    cubic = float((np.abs(d) ** 3 / p ** 2).sum())
    return dict(
        js=js, quad_approx=Q,
        rel_err=abs(js - Q) / js if js > 0 else np.nan,
        cubic_over_quad=cubic / quad if quad > 0 else np.nan,
        max_d_over_p=float(np.max(np.abs(d) / p)),
        n_genes=len(p),
    )


def pair_panels(pb_a, pb_b, hk_idx, non_hk_idx):
    """k_n-scale (HK) and k_f-scale (pair-specific top-200) diagnostics."""
    out = {}
    out['hk'] = panel_diag(pb_a[hk_idx], pb_b[hk_idx])
    ad = np.abs(pb_a - pb_b)
    ad_nh = ad[non_hk_idx]
    top_n = min(N_TOP_KF, len(ad_nh))
    top_local = np.argpartition(ad_nh, -top_n)[-top_n:]
    tg = non_hk_idx[top_local]
    out['top200'] = panel_diag(pb_a[tg], pb_b[tg])
    out['top200_genes'] = tg
    return out


def record(part, dataset, pair_id, panel, diag, extra=None):
    row = dict(part=part, dataset=dataset, pair_id=pair_id, panel=panel)
    row.update({k: v for k, v in diag.items() if k != 'top200_genes'})
    if extra:
        row.update(extra)
    ROWS.append(row)


def exchangeability_diag(pb_a, pb_b, hk_idx, top_genes, dataset, pair_id):
    """Part B: per-gene background energy, HK panel vs top-200 panel."""
    p = softmax_norm(pb_a)
    q = softmax_norm(pb_b)
    d = q - p
    e = d * d / p  # per-gene energy, common normalization
    e_h = e[hk_idx]
    e_i = e[top_genes]
    # align on a common gene set: use rank correlation of e over all kept
    # genes restricted to the union, and per-gene mean-energy ratio
    sp, _ = spearmanr(e_h, e_i) if len(e_h) == len(e_i) else (np.nan, np.nan)
    # panel sizes differ (HK ~ hundreds vs 200); compare mean energy instead
    mean_ratio = float(np.mean(e_i) / np.mean(e_h)) if np.mean(e_h) > 0 else np.nan
    # correlation of per-gene energy between HK panel and its complement
    # subsample: match sizes by sampling HK-sized sets from non-HK genes
    return dict(exch_mean_energy_ratio=mean_ratio,
                exch_e_hk_mean=float(np.mean(e_h)),
                exch_e_top_mean=float(np.mean(e_i)))


# ----------------------------------------------------------------------
# TS data (6-organ pipeline, mirrors notebooks/43)
# ----------------------------------------------------------------------
def load_ts():
    print("=" * 60)
    print("Loading TS human data (6-organ pipeline)...")
    adatas_raw = {}
    for organ in TS_ORGANS:
        fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
        if fname.exists():
            adata = sc.read_h5ad(fname)
            adata.obs["organ"] = organ
            adatas_raw[organ] = adata
            print(f"  {organ}: {adata.n_obs} cells")
    common_genes = sorted(set.intersection(*[set(a.var_names)
                                             for a in adatas_raw.values()]))
    adata_list = []
    for organ, adata in adatas_raw.items():
        adata_sub = adata[:, common_genes].copy()
        adata_sub.obs["organ"] = organ
        adata_list.append(adata_sub)
    adata = sc.concat(adata_list, axis=0, join="inner", index_unique="-")
    del adatas_raw, adata_list
    gc.collect()
    sc.pp.filter_cells(adata, min_genes=500)
    sc.pp.filter_genes(adata, min_cells=3)
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)
    print(f"  Pooled: {adata.n_obs} cells x {adata.n_vars} genes")

    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().tolist())
    gene_names = adata.var_names.tolist()
    hk_idx = np.array([i for i, g in enumerate(gene_names) if g in hk_human])
    non_hk_idx = np.where(~np.isin(np.arange(len(gene_names)), hk_idx))[0]
    print(f"  HK genes: {len(hk_idx)}")
    return adata, hk_idx, non_hk_idx


def pb_of(ct_data):
    X = ct_data.X
    return np.asarray(X.mean(axis=0)).flatten()


def run_ts(adata, hk_idx, non_hk_idx):
    print("\n--- TS: population pseudobulks ---")
    pops = {}   # (organ, ct) -> pb
    pop_cells = {}
    for organ in TS_ORGANS:
        tdata = adata[adata.obs["organ"] == organ]
        for ct in tdata.obs["cell_ontology_class"].unique():
            if str(ct).lower() == "unknown":
                continue
            ct_data = tdata[tdata.obs["cell_ontology_class"] == ct]
            if ct_data.n_obs >= 100:
                pops[(organ, ct)] = pb_of(ct_data)
                pop_cells[(organ, ct)] = ct_data.n_obs
    print(f"  Populations >=100 cells: {len(pops)}")

    # A: cross-organ same-CT pairs
    pairs = []
    cts = sorted({ct for _, ct in pops})
    for ct in cts:
        organs = sorted([o for (o, c) in pops if c == ct])
        for i in range(len(organs)):
            for j in range(i + 1, len(organs)):
                pairs.append((ct, organs[i], organs[j]))
    print(f"  Cross-organ same-CT pairs: {len(pairs)}")
    sel = rng.choice(len(pairs), size=min(N_PAIRS_TARGET, len(pairs)),
                     replace=False)
    for k, pi in enumerate(sel):
        ct, oa, ob = pairs[pi]
        res = pair_panels(pops[(oa, ct)], pops[(ob, ct)], hk_idx, non_hk_idx)
        pid = f"ts_obs_{k}"
        record('A_quadratic', 'ts_observed', pid, 'hk', res['hk'],
               dict(ct=ct, side_a=oa, side_b=ob))
        record('A_quadratic', 'ts_observed', pid, 'top200', res['top200'],
               dict(ct=ct, side_a=oa, side_b=ob))
        # B on observed pairs is not a null; skip
    print(f"  A/ts_observed recorded: {len(sel)} pairs")

    # A+B: split-half null pairs (largest donor per population)
    print("\n--- TS: split-half null pairs ---")
    null_specs = []
    for organ in TS_ORGANS:
        tdata = adata[adata.obs["organ"] == organ]
        for ct in tdata.obs["cell_ontology_class"].unique():
            if str(ct).lower() == "unknown":
                continue
            ct_data = tdata[tdata.obs["cell_ontology_class"] == ct]
            if "donor" in ct_data.obs.columns:
                dc = ct_data.obs["donor"].value_counts()
                ct_data = ct_data[ct_data.obs["donor"] == dc.index[0]]
            if ct_data.n_obs >= 100:
                null_specs.append((organ, ct, ct_data))
    print(f"  Null populations: {len(null_specs)}")
    per_pop = max(1, int(np.ceil(N_PAIRS_TARGET / max(1, len(null_specs)))))
    n_null = 0
    for organ, ct, ct_data in null_specs:
        n = ct_data.n_obs
        X = ct_data.X
        for b in range(per_pop):
            if n_null >= N_PAIRS_TARGET:
                break
            perm = rng.permutation(n)
            half = n // 2
            pbA = np.asarray(X[perm[:half]].mean(axis=0)).flatten()
            pbB = np.asarray(X[perm[half:2 * half]].mean(axis=0)).flatten()
            res = pair_panels(pbA, pbB, hk_idx, non_hk_idx)
            pid = f"ts_null_{n_null}"
            record('A_quadratic', 'ts_splithalf', pid, 'hk', res['hk'],
                   dict(ct=ct, side_a=organ, side_b='halfA/halfB'))
            record('A_quadratic', 'ts_splithalf', pid, 'top200', res['top200'],
                   dict(ct=ct, side_a=organ, side_b='halfA/halfB'))
            ex = exchangeability_diag(pbA, pbB, hk_idx, res['top200_genes'],
                                      'ts_splithalf', pid)
            record('B_exchangeability', 'ts_splithalf', pid, 'all', {},
                   dict(ct=ct, **ex))
            n_null += 1
    print(f"  A+B/ts_splithalf recorded: {n_null} null pairs")


# ----------------------------------------------------------------------
# brain data (Siletti non-neurons, mirrors 08d observed recipe)
# ----------------------------------------------------------------------
BRAIN_CTS = ["Astrocyte", "Microglia", "Oligodendrocyte"]
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_HVG = 5000


def run_brain():
    print("\n" + "=" * 60)
    print("Brain (Siletti non-neurons, 08d observed recipe)")
    print("=" * 60)
    h5_path = str(BRAIN_FILE)
    f = h5py.File(h5_path, 'r')
    N_CELLS = int(f['X/indptr'].shape[0]) - 1
    var_gene = None
    if 'Gene' in f['var']:
        vg = f['var']['Gene']
        if isinstance(vg, h5py.Dataset):
            var_gene = [x.decode() if isinstance(x, bytes) else str(x)
                        for x in vg[:]]
        elif isinstance(vg, h5py.Group) and 'categories' in vg:
            categories = [x.decode() if isinstance(x, bytes) else str(x)
                          for x in vg['categories'][:]]
            codes = vg['codes'][:]
            var_gene = [categories[c] if c >= 0 else np.nan for c in codes]
    if var_gene is None:
        idx_name = f['var'].attrs.get('_index', None)
        if idx_name and idx_name in f['var']:
            vg = f['var'][idx_name]
            var_gene = [x.decode() if isinstance(x, bytes) else str(x)
                        for x in vg[:]]
    if var_gene is None:
        raise RuntimeError("Could not read gene symbols from var group")
    N_GENES = len(var_gene)
    print(f"  Shape: ({N_CELLS}, {N_GENES})")

    obs = f['obs']
    def read_codes(name):
        g = obs[name]
        cats = [x.decode() if isinstance(x, bytes) else str(x)
                for x in g['categories'][:]]
        return g['codes'][:], cats
    ct_codes, ct_cats = read_codes('supercluster_term')
    roi_codes, roi_cats = read_codes('roi')
    samp_codes, _ = read_codes('sample_id')
    ct_names = np.array(ct_cats)[ct_codes]
    roi_names = np.array(roi_cats)[roi_codes]

    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().tolist())
    hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                                 if s in hk_human}), dtype=int)
    print(f"  Matched HK genes: {len(hk_global)}")

    # global gene means for HVG selection (08d recipe)
    print("  Global gene means pass...")
    t0 = time.time()
    X = f['X']
    indptr_full = X['indptr']
    gene_sums = np.zeros(N_GENES, dtype=np.float64)
    BATCH = 50000
    for start in range(0, N_CELLS, BATCH):
        end = min(start + BATCH, N_CELLS)
        lo, hi = int(indptr_full[start]), int(indptr_full[end])
        np.add.at(gene_sums, X['indices'][lo:hi], X['data'][lo:hi])
    gene_means = gene_sums / N_CELLS
    print(f"  Means in {time.time()-t0:.0f}s")
    non_hk_means = gene_means.copy()
    non_hk_means[hk_global] = -np.inf
    hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
    keep_global = np.sort(np.union1d(hk_global, hvg_global))
    is_hk = np.isin(keep_global, hk_global)
    hk_red = np.where(is_hk)[0]
    non_hk_red = np.where(~is_hk)[0]
    print(f"  Reduced: {len(keep_global)} genes "
          f"(HK={len(hk_red)} + HVG={len(non_hk_red)})")

    df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names,
                            'sample': samp_codes})
    groups = df_meta.groupby(['roi', 'ct']).size().reset_index(name='count')
    groups_ok = groups[groups['count'] >= MIN_NUCLEI]
    region_counts = df_meta['roi'].value_counts()
    regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
    groups_ok = groups_ok[groups_ok['roi'].isin(regions_ok)]

    done_cts = set()
    for ct in BRAIN_CTS:
        ck = RESULTS_DIR / f'theory_diagnostics_partial_brain_{ct}.csv'
        if ck.exists():
            ROWS.extend(pd.read_csv(ck).to_dict('records'))
            done_cts.add(ct)
            print(f"  Resumed {ct}: checkpoint loaded")
    for ct in BRAIN_CTS:
        if ct in done_cts:
            continue
        regs = sorted(groups_ok[groups_ok['ct'] == ct]['roi'].unique())
        n_r = len(regs)
        if n_r < 5:
            print(f"  {ct}: only {n_r} regions, skipped")
            continue
        print(f"\n  --- {ct}: {n_r} regions ---")
        n_rows_before = len(ROWS)
        ct_bool = (ct_names == ct) & np.isin(roi_names, regs)
        ct_global_idx = np.where(ct_bool)[0]
        region_of_cell = roi_names[ct_global_idx]
        samp_of_cell = samp_codes[ct_global_idx]
        sort_idx = np.argsort(region_of_cell.astype(str))
        region_sorted = region_of_cell[sort_idx].astype(str)
        samp_sorted = samp_of_cell[sort_idx]
        idx_sorted = ct_global_idx[sort_idx]

        t0 = time.time()
        X_ct = extract_csr_from_backed(h5_path, idx_sorted, keep_global,
                                       N_GENES)
        print(f"    Extracted {X_ct.shape[0]} cells x {X_ct.shape[1]} genes "
              f"({X_ct.nnz/1e6:.0f}M nnz, {time.time()-t0:.0f}s)")

        # sample-level means -> observed region pbs (08d recipe)
        uniq_samples, sample_inv = np.unique(samp_sorted, return_inverse=True)
        sample_rows = [np.where(sample_inv == s)[0]
                       for s in range(len(uniq_samples))]
        sample_weights = np.array([len(r) for r in sample_rows], float)
        region_index = {r: k for k, r in enumerate(regs)}
        sample_region_idx = np.array(
            [region_index[region_sorted[r[0]]] for r in sample_rows])
        sample_means = np.zeros((len(uniq_samples), X_ct.shape[1]))
        for s, rows in enumerate(sample_rows):
            if len(rows):
                sample_means[s] = np.asarray(
                    X_ct[rows].mean(axis=0)).flatten()

        obs_pbs = []
        for r in range(len(regs)):
            mask = sample_region_idx == r
            if not mask.any():
                obs_pbs.append(None)
                continue
            w = sample_weights[mask]
            pb_raw = (sample_means[mask] * w[:, None]).sum(axis=0) / w.sum()
            tot = pb_raw.sum()
            pb_norm = pb_raw / tot * 1e4 if tot > 0 else pb_raw
            obs_pbs.append(np.log1p(pb_norm).astype(np.float64))

        # A: observed cross-region pairs (sample 500 per CT)
        all_pairs = [(i, j) for i in range(len(regs))
                     for j in range(i + 1, len(regs))
                     if obs_pbs[i] is not None and obs_pbs[j] is not None]
        sel = rng.choice(len(all_pairs),
                         size=min(N_PAIRS_TARGET, len(all_pairs)),
                         replace=False)
        for k, pi in enumerate(sel):
            i, j = all_pairs[pi]
            res = pair_panels(obs_pbs[i], obs_pbs[j], hk_red, non_hk_red)
            pid = f"brain_obs_{ct}_{k}"
            record('A_quadratic', 'brain_observed', pid, 'hk', res['hk'],
                   dict(ct=ct, side_a=regs[i], side_b=regs[j]))
            record('A_quadratic', 'brain_observed', pid, 'top200',
                   res['top200'], dict(ct=ct, side_a=regs[i], side_b=regs[j]))
        print(f"    A/brain_observed: {len(sel)} pairs")

        # A+B: within-region split-half nulls
        n_null = 0
        target_null = 300
        regs_with_cells = [r for r in regs
                           if int(np.sum(region_sorted == r)) >= 100]
        per_reg = max(1, int(np.ceil(target_null / max(1, len(regs_with_cells)))))
        for r in regs_with_cells:
            rmask = np.where(region_sorted == r)[0]
            n = len(rmask)
            for b in range(per_reg):
                if n_null >= target_null:
                    break
                perm = rng.permutation(n)
                half = n // 2
                def split_pb(rows):
                    pb_raw = np.asarray(X_ct[rows].mean(axis=0)).flatten()
                    tot = pb_raw.sum()
                    return np.log1p(pb_raw / tot * 1e4) if tot > 0 else pb_raw
                pbA = split_pb(rmask[perm[:half]])
                pbB = split_pb(rmask[perm[half:2 * half]])
                res = pair_panels(pbA, pbB, hk_red, non_hk_red)
                pid = f"brain_null_{ct}_{n_null}"
                record('A_quadratic', 'brain_splithalf', pid, 'hk', res['hk'],
                       dict(ct=ct, side_a=r, side_b='halfA/halfB'))
                record('A_quadratic', 'brain_splithalf', pid, 'top200',
                       res['top200'], dict(ct=ct, side_a=r, side_b='halfA/halfB'))
                ex = exchangeability_diag(pbA, pbB, hk_red,
                                          res['top200_genes'],
                                          'brain_splithalf', pid)
                record('B_exchangeability', 'brain_splithalf', pid, 'all', {},
                       dict(ct=ct, **ex))
                n_null += 1
        print(f"    A+B/brain_splithalf: {n_null} null pairs")
        del X_ct, sample_means, obs_pbs
        gc.collect()
        ck = RESULTS_DIR / f'theory_diagnostics_partial_brain_{ct}.csv'
        pd.DataFrame(ROWS[n_rows_before:]).to_csv(ck, index=False)
        print(f"    Checkpoint: {len(ROWS) - n_rows_before} rows -> {ck.name}")
    f.close()


# ----------------------------------------------------------------------
# Part C: null ancillarity from existing products
# ----------------------------------------------------------------------
def part_c():
    print("\n--- Part C: cross-class null dispersion (k_f vs omega) ---")
    # brain split-half replicates: per-class null medians
    b = pd.read_csv(RESULTS_DIR / 'reviewer_brain_splithalf_raw.csv')
    for cls_col, tag in [('cell_type', 'brain_by_ct')]:
        g = b.groupby(cls_col).agg(kf_med=('kf', 'median'),
                                   kn_med=('kn', 'median'),
                                   om_med=('omega', 'median'))
        for metric, vals in [('kf', g['kf_med']), ('kn', g['kn_med']),
                             ('omega', g['om_med'])]:
            v = vals.values
            record('C_ancillarity', tag, f'{metric}_dispersion', 'summary',
                   {}, dict(ct=metric,
                            exch_mean_energy_ratio=np.nan,
                            js=float(np.std(v) / np.mean(v)),  # CV
                            quad_approx=float(v.max() / v.min()),
                            rel_err=float(np.subtract(*np.percentile(v, [75, 25]))
                                        / np.median(v))))
    # mouse split-half: per tissue-CT medians
    m = pd.read_csv(RESULTS_DIR / 'mouse_splithalf_v44.csv')
    g = m.groupby(['tissue', 'cell_type']).agg(kf_med=('kf', 'median'),
                                               kn_med=('kn', 'median'),
                                               om_med=('omega', 'median'))
    for metric, vals in [('kf', g['kf_med']), ('kn', g['kn_med']),
                         ('omega', g['om_med'])]:
        v = vals.values
        record('C_ancillarity', 'mouse_by_tissue_ct', f'{metric}_dispersion',
               'summary', {}, dict(ct=metric,
                                   js=float(np.std(v) / np.mean(v)),
                                   quad_approx=float(v.max() / v.min()),
                                   rel_err=float(np.subtract(
                                       *np.percentile(v, [75, 25]))
                                       / np.median(v))))
    print("  C recorded (js=CV, quad_approx=max/min, rel_err=IQR/median)")


# ----------------------------------------------------------------------
# Part D: ground-truth monotonicity + invariance
# ----------------------------------------------------------------------
def part_d():
    print("\n--- Part D: ground-truth monotonicity / invariance ---")
    g = pd.read_csv(RESULTS_DIR / 'groundtruth_simulation_background2_raw.csv')

    def emit(tag, sub, xcol):
        for metric in ['omega', 'k_f', 'k_n', 'k_total']:
            rho, p = spearmanr(sub[xcol], sub[metric])
            record('D_groundtruth', tag, f'{metric}_vs_{xcol}', 'summary',
                   {}, dict(ct=metric, js=float(rho), quad_approx=float(p),
                            rel_err=np.nan))

    # monotonicity in functional shift at zero background
    sub = g[(g['eta'] == 0) & (g['eps'] == 0) & (g['delta'] > 0)]
    emit('mono_delta_bg0', sub, 'delta')
    # invariance to background drift at delta=0
    sub = g[(g['delta'] == 0) & (g['eps'] == 0)]
    emit('invar_eta_d0', sub, 'eta')
    # joint: omega-1 vs delta at each eta (linearity / estimand)
    for eta in sorted(g['eta'].unique()):
        sub = g[(g['eta'] == eta) & (g['eps'] == 0)]
        piv = sub.groupby('delta')[['omega', 'k_f', 'k_n']].mean()
        for delta in piv.index:
            record('D_groundtruth', f'estimand_eta{eta}', f'delta_{delta}',
                   'summary', {},
                   dict(ct='grid_mean', js=float(piv.loc[delta, 'omega']),
                        quad_approx=float(piv.loc[delta, 'k_f']),
                        rel_err=float(piv.loc[delta, 'k_n']),
                        exch_mean_energy_ratio=float(eta)))
    # non-HK drift series: omega vs eta under drift-only
    d = pd.read_csv(RESULTS_DIR / 'nonhk_drift_v45_raw.csv')
    for series in d['series'].unique():
        sub = d[d['series'] == series].dropna(subset=['eta'])
        if len(sub) < 5:
            continue
        for metric in ['omega', 'k_f', 'k_n']:
            rho, p = spearmanr(sub['eta'], sub[metric])
            record('D_groundtruth', f'drift_{series}', f'{metric}_vs_eta',
                   'summary', {},
                   dict(ct=metric, js=float(rho), quad_approx=float(p)))
    print("  D recorded (js=Spearman rho / grid mean)")


# ----------------------------------------------------------------------
# summary markdown
# ----------------------------------------------------------------------
def summarize(df):
    lines = ["# Theory diagnostics summary (notebooks/85)\n"]
    a = df[df['part'] == 'A_quadratic']
    lines.append("\n## A. Quadratic-regime |JS - Q| / JS\n")
    lines.append("| dataset | panel | n | JS median | rel-err median | "
                 "rel-err p90 | cubic/quad median | max|d|/p median |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for (ds, panel), sub in a.groupby(['dataset', 'panel']):
        lines.append(f"| {ds} | {panel} | {len(sub)} | "
                     f"{sub['js'].median():.4g} | "
                     f"{sub['rel_err'].median():.3g} | "
                     f"{sub['rel_err'].quantile(0.9):.3g} | "
                     f"{sub['cubic_over_quad'].median():.3g} | "
                     f"{sub['max_d_over_p'].median():.3g} |")
    b = df[df['part'] == 'B_exchangeability']
    lines.append("\n## B. Background-energy exchangeability (null pairs)\n")
    lines.append("| dataset | n | mean-energy ratio (top200/HK) median | "
                 "p10 | p90 |")
    lines.append("|---|---|---|---|---|")
    for ds, sub in b.groupby('dataset'):
        r = sub['exch_mean_energy_ratio'].dropna()
        lines.append(f"| {ds} | len={len(sub)} | {r.median():.3g} | "
                     f"{r.quantile(0.1):.3g} | {r.quantile(0.9):.3g} |")
    c = df[df['part'] == 'C_ancillarity']
    lines.append("\n## C. Cross-class null dispersion "
                 "(CV / max-min / IQR-median)\n")
    lines.append("| dataset | metric | CV | max/min | IQR/median |")
    lines.append("|---|---|---|---|---|")
    for _, r in c.iterrows():
        lines.append(f"| {r['dataset']} | {r['ct']} | {r['js']:.3g} | "
                     f"{r['quad_approx']:.3g} | {r['rel_err']:.3g} |")
    d = df[df['part'] == 'D_groundtruth']
    lines.append("\n## D. Ground-truth contrasts (Spearman rho, p)\n")
    lines.append("| contrast | metric | rho | p |")
    lines.append("|---|---|---|---|")
    dd = d[d['dataset'].isin(['mono_delta_bg0', 'invar_eta_d0'])]
    for _, r in dd.iterrows():
        lines.append(f"| {r['dataset']} | {r['ct']} | {r['js']:.3f} | "
                     f"{r['quad_approx']:.2g} |")
    dd2 = d[d['dataset'].str.startswith('drift_')]
    if len(dd2):
        lines.append("\n### Non-HK drift series (rho vs eta)\n")
        lines.append("| series | metric | rho | p |")
        lines.append("|---|---|---|---|")
        for _, r in dd2.iterrows():
            lines.append(f"| {r['dataset']} | {r['ct']} | {r['js']:.3f} | "
                         f"{r['quad_approx']:.2g} |")
    dg = d[d['dataset'].str.startswith('estimand_')]
    if len(dg):
        lines.append("\n### Estimand grid: mean omega / k_f / k_n "
                     "by (eta, delta)\n")
        lines.append("| eta | delta | omega | k_f | k_n |")
        lines.append("|---|---|---|---|---|")
        for _, r in dg.iterrows():
            lines.append(f"| {r['exch_mean_energy_ratio']:.2f} | "
                         f"{r['pair_id'].replace('delta_', '')} | "
                         f"{r['js']:.4g} | {r['quad_approx']:.4g} | "
                         f"{r['rel_err']:.4g} |")
    return "\n".join(lines) + "\n"


def main():
    t_start = time.time()
    partial = RESULTS_DIR / 'theory_diagnostics_partial_ts.csv'
    if os.environ.get('SKIP_TS') and partial.exists():
        global ROWS
        ROWS.extend(pd.read_csv(partial).to_dict('records'))
        print(f"Resumed: loaded {len(ROWS)} TS rows from {partial.name}")
    else:
        adata, hk_idx, non_hk_idx = load_ts()
        run_ts(adata, hk_idx, non_hk_idx)
        del adata
        gc.collect()
        pd.DataFrame(ROWS).to_csv(partial, index=False)
        print(f"Checkpoint: {len(ROWS)} TS rows -> {partial.name}")
    run_brain()
    part_c()
    part_d()

    df = pd.DataFrame(ROWS)
    df.to_csv(RESULTS_DIR / 'theory_diagnostics.csv', index=False)
    md = summarize(df)
    with open(RESULTS_DIR / 'theory_diagnostics.md', 'w') as fh:
        fh.write(md)
    print("\n" + "=" * 60)
    print(md)
    print(f"Saved -> results/theory_diagnostics.{{csv,md}} "
          f"({time.time()-t_start:.0f}s)")
    print("DONE.")


if __name__ == '__main__':
    main()
