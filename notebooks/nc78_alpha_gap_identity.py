"""
nc78 P0-5 / stat-M2: direct measurement of the softmax mass shares entering
the alpha-gap identity.

The SI Note 20 C2 estimates alpha as the ratio of MEAN per-gene background
energy (top-200 vs HK panel) under split-half nulls, with full-set softmax
weights (notebooks/85 part B): alpha_hat = mean_200(e) / mean_HK(e),
e_i = d_i^2/p_i. Proposition 3 needs alpha* = E_b(top-200)/E_b(HK) with
panel-restricted measures, identified on nulls as omega_null = k_f/k_n.

Identity (first-order, split-half nulls where S_p ~ S_q):
    E_b(panel) = (1/S_panel) * sum_{panel} d_i^2/p_i
    => alpha_hat = alpha* * (N_HK/N_200) * (S_200/S_HK)
where S_panel = sum of full-set softmax mass on the panel.

The 1.44x "gap" (brain: 13.99 vs 8.81 per-pair medians) should therefore
decompose as 5.575 (panel counts) x ~0.26 (mass shares). Here we measure
S_200/S_HK DIRECTLY on TS split-half null pairs (production 43/85 recipe)
and compare against the implied value 0.204 from results/theory_diagnostics.csv.

Output: results/nc78_alpha_gap_identity.{csv,md}
"""
import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc

RANDOM_SEED = 42
N_TOP_KF = 200
N_POP = 6
N_PAIRS_PER_POP = 5

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None


def softmax_norm(x):
    x = np.asarray(x, dtype=np.float64)
    e = np.exp(x - x.max())
    return e / (e.sum() + 1e-9)


def main():
    t0 = time.time()
    print("Loading TS (43/85 recipe)...")
    adatas_raw = {}
    for organ in TS_ORGANS:
        fname = TS_HUMAN_DIR / f"TS_{organ}.h5ad"
        if fname.exists():
            a = sc.read_h5ad(fname)
            a.obs["organ"] = organ
            adatas_raw[organ] = a
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
    sc.pp.log1p(adata)
    print(f"  Pooled: {adata.n_obs} cells x {adata.n_vars} genes")
    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().tolist())
    genes = adata.var_names.tolist()
    hk_idx = np.array([i for i, g in enumerate(genes) if g in hk_human])
    non_hk_idx = np.where(~np.isin(np.arange(len(genes)), hk_idx))[0]
    N_HK = len(hk_idx)
    print(f"  HK: {N_HK}")

    # pick the N_POP largest populations (same >=100 rule as 85)
    rng = np.random.RandomState(RANDOM_SEED)
    organ_arr = adata.obs["organ"].to_numpy().astype(str)
    ct_arr = adata.obs["cell_ontology_class"].to_numpy().astype(str)
    pops = []
    for organ in TS_ORGANS:
        om = organ_arr == organ
        for ct in pd.unique(ct_arr[om]):
            if ct.lower() == "unknown":
                continue
            n = int((om & (ct_arr == ct)).sum())
            if n >= 400:
                pops.append((organ, ct, n))
    pops = sorted(pops, key=lambda t: -t[2])[:N_POP]
    print(f"  Populations: {[(o, c, n) for o, c, n in pops]}")

    rows = []
    for organ, ct, n in pops:
        mask = (organ_arr == organ) & (ct_arr == ct)
        X = adata.X[np.where(mask)[0]]
        nn = X.shape[0]
        for b in range(N_PAIRS_PER_POP):
            perm = rng.permutation(nn)
            half = nn // 2
            pbA = np.asarray(X[perm[:half]].mean(axis=0)).flatten()
            pbB = np.asarray(X[perm[half:2*half]].mean(axis=0)).flatten()
            p_full = softmax_norm(pbA)
            S_HK = float(p_full[hk_idx].sum())
            ad = np.abs(pbA - pbB)
            ad_nh = ad[non_hk_idx]
            tl = np.argpartition(ad_nh, -N_TOP_KF)[-N_TOP_KF:]
            tg = non_hk_idx[tl]
            S_200 = float(p_full[tg].sum())
            rows.append(dict(organ=organ, ct=ct, rep=b,
                             S_HK=S_HK, S_200=S_200,
                             ratio=S_200 / S_HK, N_HK=N_HK))
        print(f"  {ct}|{organ}: done")
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / 'nc78_alpha_gap_identity.csv', index=False)
    r = df['ratio']
    md = ["# nc78 P0-5: direct S_200/S_HK measurement (TS split-half nulls)\n",
          f"- pairs: {len(df)} ({len(pops)} populations x {N_PAIRS_PER_POP} reps)",
          f"- S_200/S_HK: median {r.median():.3f}, "
          f"p10 {r.quantile(.1):.3f}, p90 {r.quantile(.9):.3f}",
          f"- implied value from theory_diagnostics.csv per-pair identity: 0.204",
          f"- predicted alpha_hat = alpha* x (N_HK/200) x (S_200/S_HK) "
          f"= alpha* x {N_HK/200:.3f} x {r.median():.3f} "
          f"= alpha* x {(N_HK/200)*r.median():.3f}",
          f"- observed alpha_hat/alpha* gap (TS): 8.468/7.360 = {8.468/7.360:.3f}",
          ""]
    with open(RESULTS_DIR / 'nc78_alpha_gap_identity.md', 'w') as fh:
        fh.write("\n".join(md))
    print("\n".join(md))
    print(f"({time.time()-t0:.0f}s) DONE.")


if __name__ == '__main__':
    main()
