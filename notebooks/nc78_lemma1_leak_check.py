"""
nc78 P0-4 / stat-M1 ground-truth check: Lemma 1 log1p leak bound.

The SI (Note 20, Lemma 1) states: for depth rescaling c in [1/2, 2], the
p-weighted energy of the leak field (1/c - 1)/x is at most
((1-c)/c)^2 Var_p(1/x), "which is <= 1e-4 ((1-c)/c)^2 at pseudobulk count
scales (detected genes have x >= 1e2)".

stat-M1 (nc78 blind review) claims the premise x >= 1e2 contradicts the
operative pipeline scale: normalize_total(target_sum=1e4) puts per-gene
expression on a scale where a ~1,115-gene HK panel has mean x ~ 9, so
Var_p(1/x) could exceed 1e-4 by 2-3 orders of magnitude and the c=2 leak
energy could be of the same order as Q(k_n) = 8 ln 2 * k_n.

This script measures, on REAL population pseudobulks at the OPERATIVE
scale (post-normalize_total(1e4), pre-log1p), restricted to the HK panel:

  - the empirical distribution of x (median / p10 / p90 / min,
    fraction with x >= 1e2),
  - Var_p(1/x) with p = softmax(v_hk) exactly as k_n computes it,
  - leak energies: c=2 -> ((1-c)/c)^2 = 1/4; worst case c=1/2 -> 1,
  - the leak contribution to JS = leak / (8 ln 2),

and benchmarks these against the empirical split-half null k_n of the
same datasets (from results/theory_diagnostics.csv for TS/brain and
results/mouse_splithalf_v44.csv for mouse FACS).

Datasets / recipes (mirroring the production pipelines):
  mouse FACS : notebooks/87 recipe (per-cell normalize_total(1e4) +
               log1p; pseudobulk = group mean of log1p values; x = group
               mean of the PRE-log normalized counts) - 6 control pops
  TS         : notebooks/43/85 recipe (same per-cell recipe), all
               (organ, cell type) populations with >= 100 cells
  brain      : notebooks/08d recipe (region pseudobulk raw sums,
               normalized to 1e4 at the pseudobulk level, then log1p;
               x = the pre-log1p normalized pseudobulk), 3 non-neuron
               cell types x regions

Outputs:
  results/nc78_lemma1_leak_check.csv   per-population measurements
  results/nc78_lemma1_leak_check.md    summary + verdict-relevant tables

Usage: python notebooks/nc78_lemma1_leak_check.py
"""

import sys, os, time, gc, importlib.util
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
import h5py
from scipy.sparse import issparse, csr_matrix

RANDOM_SEED = 42
LN2 = np.log(2.0)
MIN_CELLS = 100

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)

ROWS = []


def softmax_norm(x):
    x = np.asarray(x, dtype=np.float64)
    e = np.exp(x - x.max())
    return e / (e.sum() + 1e-9)


def measure_population(dataset, pop, n_cells, x_pre, v_log):
    """x_pre: pre-log1p normalized expression (operative x scale);
    v_log: the log1p-scale vector that k_n's softmax actually sees.
    Both already restricted to the HK panel."""
    x = np.asarray(x_pre, dtype=np.float64)
    v = np.asarray(v_log, dtype=np.float64)
    p = softmax_norm(v)
    n = len(x)
    n_zero = int((x <= 0).sum())
    pos = x > 0
    # p-weighted Var(1/x) on detected genes (renormalized p)
    if pos.sum() >= 10:
        pw = p[pos] / p[pos].sum()
        inv = 1.0 / x[pos]
        mu = float((pw * inv).sum())
        var_p = float((pw * (inv - mu) ** 2).sum())
        # unweighted counterpart for context
        var_u = float(np.var(inv))
    else:
        var_p, var_u = np.nan, np.nan
    leak_c2 = var_p / 4.0                 # ((1-c)/c)^2 at c=2
    leak_chalf = var_p * 1.0              # ((1-c)/c)^2 at c=1/2 (worst case)
    ROWS.append(dict(
        dataset=dataset, population=pop, n_cells=int(n_cells), n_hk=n,
        n_zero=n_zero,
        x_min=float(np.min(x)), x_p10=float(np.percentile(x, 10)),
        x_med=float(np.median(x)), x_p90=float(np.percentile(x, 90)),
        frac_x_ge_100=float((x >= 100).mean()),
        frac_x_ge_10=float((x >= 10).mean()),
        p_weight_on_x_lt_100=float(p[x < 100].sum()),
        var_p_inv_x=var_p, var_unweighted_inv_x=var_u,
        leak_energy_c2=leak_c2, leak_energy_chalf=leak_chalf,
        leakJS_c2=leak_c2 / (8 * LN2), leakJS_chalf=leak_chalf / (8 * LN2),
    ))


# ----------------------------------------------------------------------
# mouse FACS (notebooks/87 recipe; 6 control populations)
# ----------------------------------------------------------------------
def run_mouse():
    print("=" * 60)
    print("Mouse FACS (87 recipe, 6 control populations)")
    print("=" * 60)
    CONTROL_PAIRS = [
        ("Liver", "hepatocyte"), ("Heart", "endothelial cell"),
        ("Spleen", "B cell"), ("Marrow", "B cell"),
        ("Heart", "fibroblast"), ("Marrow", "neutrophil"),
    ]
    TARGET_TISSUES = sorted({t for t, _ in CONTROL_PAIRS})
    hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
    hk_mouse = set(hk_df.iloc[:, 0].tolist())

    annot = pd.read_csv(FACS_ANNOTATIONS)
    annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
    adatas, all_genes = {}, set()
    for tissue in TARGET_TISSUES:
        fname = FACS_DIR / f"{tissue}-counts.csv"
        if not fname.exists():
            print(f"  {tissue}: file missing, skipped")
            continue
        df = pd.read_csv(fname, index_col=0)
        adatas[tissue] = df
        all_genes.update(df.index.tolist())
    common_genes = sorted(set.intersection(*[set(d.index) for d in adatas.values()]))
    expr_parts, obs_parts = [], []
    for tissue, df in adatas.items():
        da = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
        expr_parts.append(da.values)
        ta = annot[annot["tissue"] == tissue][["cell", "cell_ontology_class"]]
        ob = pd.DataFrame({"cell": da.index.tolist(), "tissue": tissue})
        ob = ob.merge(ta, on="cell", how="left")
        ob["cell_ontology_class"] = ob["cell_ontology_class"].fillna("unknown")
        obs_parts.append(ob.set_index("cell"))
        del df, da
    X = np.vstack(expr_parts).astype(np.float64)
    obs = pd.concat(obs_parts, axis=0)
    del expr_parts, adatas
    gc.collect()
    adata = sc.AnnData(X=X, obs=obs,
                       var=pd.DataFrame(index=common_genes))
    sc.pp.filter_cells(adata, min_genes=500)
    sc.pp.filter_genes(adata, min_cells=3)
    print(f"  After QC: {adata.n_obs} cells x {adata.n_vars} genes")
    sc.pp.normalize_total(adata, target_sum=1e4)
    X_norm = adata.X.copy()           # pre-log operative scale
    sc.pp.log1p(adata)
    genes = adata.var_names.tolist()
    hk_idx = np.array([i for i, g in enumerate(genes) if g in hk_mouse])
    print(f"  HK matched: {len(hk_idx)}")
    for tissue, ct in CONTROL_PAIRS:
        mask = (adata.obs["tissue"] == tissue) & \
               (adata.obs["cell_ontology_class"] == ct)
        n = int(mask.sum())
        if n < 2 * 10:
            print(f"  SKIP {ct} ({tissue}): {n} cells")
            continue
        rows = np.where(mask)[0]
        xbar = np.asarray(X_norm[rows].mean(axis=0)).flatten()
        v = np.asarray(adata.X[rows].mean(axis=0)).flatten()
        measure_population("mouse_facs", f"{ct}|{tissue}", n,
                           xbar[hk_idx], v[hk_idx])
        print(f"  {ct} ({tissue}): {n} cells measured")
    del adata, X_norm, X
    gc.collect()


# ----------------------------------------------------------------------
# Tabula Sapiens (43/85 recipe; all populations >= 100 cells)
# ----------------------------------------------------------------------
def run_ts():
    print("=" * 60)
    print("Tabula Sapiens (43/85 recipe)")
    print("=" * 60)
    adatas_raw = {}
    for organ in TS_ORGANS:
        fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
        if fname.exists():
            a = sc.read_h5ad(fname)
            a.obs["organ"] = organ
            adatas_raw[organ] = a
            print(f"  {organ}: {a.n_obs} cells")
    common_genes = sorted(set.intersection(*[set(a.var_names)
                                             for a in adatas_raw.values()]))
    alist = []
    for organ, a in adatas_raw.items():
        s = a[:, common_genes].copy()
        s.obs["organ"] = organ
        alist.append(s)
    adata = sc.concat(alist, axis=0, join="inner", index_unique="-")
    del adatas_raw, alist
    gc.collect()
    sc.pp.filter_cells(adata, min_genes=500)
    sc.pp.filter_genes(adata, min_cells=3)
    sc.pp.normalize_total(adata, target_sum=1e4)
    X_norm = adata.X.copy()
    if not issparse(X_norm):
        X_norm = csr_matrix(X_norm)
    sc.pp.log1p(adata)
    print(f"  Pooled: {adata.n_obs} cells x {adata.n_vars} genes")
    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().tolist())
    genes = adata.var_names.tolist()
    hk_idx = np.array([i for i, g in enumerate(genes) if g in hk_human])
    print(f"  HK matched: {len(hk_idx)}")
    organ_arr = adata.obs["organ"].to_numpy().astype(str)
    ct_arr = adata.obs["cell_ontology_class"].to_numpy().astype(str)
    n_pop = 0
    for organ in TS_ORGANS:
        om = organ_arr == organ
        for ct in pd.unique(ct_arr[om]):
            if ct.lower() == "unknown":
                continue
            mask = om & (ct_arr == ct)
            n = int(mask.sum())
            if n < MIN_CELLS:
                continue
            rows = np.where(mask)[0]
            xbar = np.asarray(X_norm[rows].mean(axis=0)).flatten()
            v = np.asarray(adata.X[rows].mean(axis=0)).flatten()
            if issparse(v):
                v = np.asarray(v).flatten()
            measure_population("tabula_sapiens", f"{ct}|{organ}", n,
                               xbar[hk_idx], v[hk_idx])
            n_pop += 1
    print(f"  Populations measured: {n_pop}")
    del adata, X_norm
    gc.collect()


# ----------------------------------------------------------------------
# brain (08d recipe: region pseudobulks, pseudobulk-level normalization)
# ----------------------------------------------------------------------
BRAIN_CTS = ["Astrocyte", "Microglia", "Oligodendrocyte"]
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_HVG = 5000


def run_brain():
    print("=" * 60)
    print("Brain Siletti non-neurons (08d recipe)")
    print("=" * 60)
    _spec = importlib.util.spec_from_file_location(
        "bs08d", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "08d_brain_blockshuffle_null.py"))
    _bs08d = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_bs08d)
    extract_csr_from_backed = _bs08d.extract_csr_from_backed

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
            cats = [x.decode() if isinstance(x, bytes) else str(x)
                    for x in vg['categories'][:]]
            var_gene = [cats[c] if c >= 0 else np.nan for c in vg['codes'][:]]
    if var_gene is None:
        idx_name = f['var'].attrs.get('_index', None)
        vg = f['var'][idx_name]
        var_gene = [x.decode() if isinstance(x, bytes) else str(x)
                    for x in vg[:]]
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

    # HK + top HVGs (08d reduction; HVGs only needed to mirror the recipe,
    # but x measurement uses the HK block only)
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
    print(f"  Reduced: {len(keep_global)} genes (HK={len(hk_red)})")

    df_meta = pd.DataFrame({'ct': ct_names, 'roi': roi_names,
                            'sample': samp_codes})
    groups = df_meta.groupby(['roi', 'ct']).size().reset_index(name='count')
    groups_ok = groups[groups['count'] >= MIN_NUCLEI]
    region_counts = df_meta['roi'].value_counts()
    regions_ok = set(region_counts[region_counts >= MIN_REGION_N].index)
    groups_ok = groups_ok[groups_ok['roi'].isin(regions_ok)]

    for ct in BRAIN_CTS:
        regs = sorted(groups_ok[groups_ok['ct'] == ct]['roi'].unique())
        if len(regs) < 2:
            print(f"  {ct}: {len(regs)} regions, skipped")
            continue
        print(f"\n  --- {ct}: {len(regs)} regions ---")
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
        for r in range(len(regs)):
            mask = sample_region_idx == r
            if not mask.any():
                continue
            w = sample_weights[mask]
            pb_raw = (sample_means[mask] * w[:, None]).sum(axis=0) / w.sum()
            tot = pb_raw.sum()
            if tot <= 0:
                continue
            x_pb = pb_raw / tot * 1e4        # operative x scale (08d)
            v_pb = np.log1p(x_pb)
            n_cells_r = int(np.sum(region_sorted == regs[r]))
            measure_population("brain_siletti", f"{ct}|{regs[r]}",
                               n_cells_r, x_pb[hk_red], v_pb[hk_red])
        print(f"    {ct}: {len(regs)} regions measured")
        del X_ct, sample_means
        gc.collect()
    f.close()


# ----------------------------------------------------------------------
# summary
# ----------------------------------------------------------------------
def summarize(df):
    lines = ["# nc78 P0-4: Lemma 1 leak bound — empirical check (stat-M1)\n",
             "Operative scale = post-normalize_total(1e4), pre-log1p; ",
             "p = softmax(v_HK) exactly as k_n computes it.\n"]
    lines.append("\n## Per-dataset summary of x (HK panel, real populations)\n")
    lines.append("| dataset | n_pop | x median-of-medians | x p10 (worst pop) | "
                 "frac x>=100 (median) | min frac>=100 | p-weight on x<100 (median) |")
    lines.append("|---|---|---|---|---|---|---|")
    for ds, sub in df.groupby('dataset'):
        lines.append(f"| {ds} | {len(sub)} | {sub['x_med'].median():.3g} | "
                     f"{sub['x_p10'].min():.3g} | "
                     f"{sub['frac_x_ge_100'].median():.3g} | "
                     f"{sub['frac_x_ge_100'].min():.3g} | "
                     f"{sub['p_weight_on_x_lt_100'].median():.3g} |")
    lines.append("\n## Var_p(1/x) and leak energies\n")
    lines.append("| dataset | Var_p(1/x) median | max | bound claim 1e-4 holds? "
                 "| leakJS c=2 median | leakJS c=2 max | leakJS c=1/2 max |")
    lines.append("|---|---|---|---|---|---|---|")
    for ds, sub in df.groupby('dataset'):
        v = sub['var_p_inv_x']
        lines.append(f"| {ds} | {v.median():.3g} | {v.max():.3g} | "
                     f"{'yes' if v.max() <= 1e-4 else 'NO'} | "
                     f"{sub['leakJS_c2'].median():.3g} | "
                     f"{sub['leakJS_c2'].max():.3g} | "
                     f"{sub['leakJS_chalf'].max():.3g} |")
    # null k_n references
    lines.append("\n## Empirical split-half null k_n (reference scale)\n")
    try:
        td = pd.read_csv(RESULTS_DIR / 'theory_diagnostics.csv')
        a = td[(td['part'] == 'A_quadratic') & (td['panel'] == 'hk') &
               (td['dataset'].isin(['ts_splithalf', 'brain_splithalf']))]
        lines.append("| dataset | n | k_n median | k_n p10 | "
                     "8 ln2 * k_n (E_b) median |")
        lines.append("|---|---|---|---|---|")
        for ds, sub in a.groupby('dataset'):
            lines.append(f"| {ds} | {len(sub)} | {sub['js'].median():.3g} | "
                         f"{sub['js'].quantile(0.1):.3g} | "
                         f"{8*LN2*sub['js'].median():.3g} |")
    except Exception as e:
        lines.append(f"(theory_diagnostics.csv unavailable: {e})")
    try:
        m = pd.read_csv(RESULTS_DIR / 'mouse_splithalf_v44.csv')
        kn = m['kn'] if 'kn' in m.columns else m['k_n']
        lines.append(f"\nMouse FACS split-half null k_n: median "
                     f"{kn.median():.3g}, p10 {kn.quantile(0.1):.3g} "
                     f"(n={len(kn)}); 8 ln2 * k_n = {8*LN2*kn.median():.3g}")
    except Exception as e:
        lines.append(f"\n(mouse_splithalf_v44.csv unavailable: {e})")
    lines.append("\n## Worst populations (by leakJS c=2)\n")
    lines.append("| dataset | population | n_cells | x_med | frac>=100 | "
                 "Var_p(1/x) | leakJS c=2 | leakJS c=1/2 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    top = df.nlargest(10, 'leakJS_c2')
    for _, r in top.iterrows():
        lines.append(f"| {r['dataset']} | {r['population']} | "
                     f"{r['n_cells']} | {r['x_med']:.3g} | "
                     f"{r['frac_x_ge_100']:.3g} | {r['var_p_inv_x']:.3g} | "
                     f"{r['leakJS_c2']:.3g} | {r['leakJS_chalf']:.3g} |")
    return "\n".join(lines) + "\n"


def main():
    t0 = time.time()
    run_mouse()
    run_ts()
    run_brain()
    df = pd.DataFrame(ROWS)
    df.to_csv(RESULTS_DIR / 'nc78_lemma1_leak_check.csv', index=False)
    md = summarize(df)
    with open(RESULTS_DIR / 'nc78_lemma1_leak_check.md', 'w') as fh:
        fh.write(md)
    print("\n" + md)
    print(f"Saved -> results/nc78_lemma1_leak_check.{{csv,md}} "
          f"({time.time()-t0:.0f}s)")
    print("DONE.")


if __name__ == '__main__':
    main()
