"""
#nc80 M-J (ii): covariance-whitened / Mahalanobis baseline
==========================================================
Responds to nc80 methods M3 / editor R8: "no covariance-whitened/
Mahalanobis baseline despite studentization being the central claim".

The paper's central precision claim is that HK-anchored studentization
(omega = k_f / k_n) collapses null dispersion 8-fold relative to
unnormalized metrics (log-MAD 0.113 vs 0.267-0.586).  The reviewers ask
whether the classical *studentized comparator* -- a covariance-whitened
pseudobulk distance -- achieves the same collapse without the HK anchor.

Design: repeats the published notebook-45 / notebook-49 semi-synthetic
injection design UNCHANGED (same backgrounds: Tabula Muris FACS Marrow
B cell and Skin keratinocyte stem cell; same delta/eta/eps grids; same
module seeds {42, 137, 2024}; same 200-gene module, 200 cells/group,
50 reps, 200 null reps; same pseudobulk and k_f/k_n code path) and adds
TWO whitened baselines whose whitening operator is fit ONLY on the
null (baseline) replicates:

  mahal_pc   full Mahalanobis in the top-20 PC space of the null
             pseudobulks: d = sqrt(dp' S^{-1} dp), S = null covariance
             of the PC-score differences (20 x 20, ridge 1e-6 tr).
  mahal_diag gene-wise (diagonal) whitening: d = sqrt(mean_g
             (delta_g / sigma_g)^2), sigma_g = null per-gene SD of the
             pseudobulk difference.

Both are *studentized by construction* on the null, so their null
dispersion is the honest benchmark for whether omega's precision gain
comes from studentization per se or from the HK anchor.

Series run (reduced from the published grid to the rows the
comparisons need): baseline (200, null calibration), signal
(5 deltas x 3 module seeds x 50 reps), neutral_hk (3 etas x 50),
neutral_global (2 eps x 50).

Outputs:
  results/nc80_mj_mahalanobis_raw.csv           (all replicates, both backgrounds)
  results/nc80_mj_mahalanobis_summary.csv        (per background x series x metric)
  results/nc80_mj_mahalanobis_metrics.json       (thresholds, type-I, power,
                                                  AUC, monotonicity, null log-MAD)
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cki.core import js_divergence  # noqa: E402

DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

HK_FILE = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"

N_HVG = 5000
N_TOP_KF = 200
MODULE_SIZE = 200
N_CELLS_PER_GROUP = 200
N_REPS = 50
N_NULL_REPS = 200
DELTA_GRID = [0.125, 0.25, 0.5, 1.0, 2.0]
ETA_GRID = [0.25, 0.5, 1.0]
EPS_GRID = [0.3, 1.0]
NULL_Q = 95.0
N_PC = 20
RIDGE = 1e-6

MODULE_SEEDS = [42, 137, 2024]
METRIC_COLS = ["omega", "k_f", "k_n", "k_total", "cosine", "kf_over_kt",
               "mahal_pc", "mahal_diag"]


def load_background(background_csv, annot_csv, tissue, ct_name):
    counts_t = pd.read_csv(background_csv, index_col=0)  # genes x cells
    gene_names = counts_t.index.astype(str).tolist()
    ann = pd.read_csv(ANNOT_CSV if False else annot_csv, index_col=0)
    ann_t = ann[ann["tissue"] == tissue]
    ct_cells = ann_t.index[ann_t["cell_ontology_class"] == ct_name]
    ct_cells = [c for c in ct_cells if c in counts_t.columns]
    X = counts_t[ct_cells].T.to_numpy(dtype=np.float32)  # cells x genes

    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_mouse = set(hk_df["Mouse"].dropna().astype(str))
    hk_mask = np.array([g in hk_mouse for g in gene_names])

    gene_means = X.mean(axis=0)
    non_hk_means = np.where(hk_mask, -np.inf, gene_means)
    hvg_idx = np.argsort(non_hk_means)[-N_HVG:]
    keep_mask = hk_mask.copy()
    keep_mask[hvg_idx] = True
    keep_idx = np.where(keep_mask)[0]
    keep_idx = keep_idx[gene_means[keep_idx] > 0]
    X = X[:, keep_idx]
    kept_hk = hk_mask[keep_idx]
    hk_in_keep = np.where(kept_hk)[0]
    non_hk_in_keep = np.where(~kept_hk)[0]
    return X, hk_in_keep, non_hk_in_keep


def build_pseudobulk(counts):
    """08d pseudobulk: cell-mean -> /total*1e4 -> log1p."""
    pb = counts.mean(axis=0)
    tot = pb.sum()
    pb = pb / tot * 1e4 if tot > 0 else pb
    return np.log1p(pb).astype(np.float64)


def base_metrics(pb_a, pb_b, hk_in_keep, non_hk_in_keep):
    kn = js_divergence(pb_a[hk_in_keep], pb_b[hk_in_keep])
    ad = np.abs(pb_a - pb_b)
    ad_nh = ad[non_hk_in_keep]
    top_n = min(N_TOP_KF, len(ad_nh))
    top_local = np.argpartition(ad_nh, -top_n)[-top_n:]
    tg = non_hk_in_keep[top_local]
    kf = js_divergence(pb_a[tg], pb_b[tg])
    omega = kf / kn if kn > 1e-15 else np.inf
    kt = js_divergence(pb_a, pb_b)
    na, nb = np.linalg.norm(pb_a), np.linalg.norm(pb_b)
    cosine = 1.0 - float(np.dot(pb_a, pb_b) / (na * nb)) if na > 0 and nb > 0 else 1.0
    kf_over_kt = kf / kt if kt > 1e-15 else np.inf
    return {"omega": omega, "k_f": kf, "k_n": kn, "k_total": kt,
            "cosine": cosine, "kf_over_kt": kf_over_kt}


def simulate_pair_pbs(X, delta=0.0, eta=0.0, eps=0.0, rng=None, mod=None,
                      hk_in_keep=None):
    rng = rng or np.random.RandomState(0)
    n_cells_total = X.shape[0]
    n_keep = X.shape[1]
    ia = rng.choice(n_cells_total, size=N_CELLS_PER_GROUP, replace=False)
    ib = rng.choice(n_cells_total, size=N_CELLS_PER_GROUP, replace=False)
    A = X[ia].astype(np.float64)
    B = X[ib].astype(np.float64)
    if eta != 0.0:
        A[:, hk_in_keep] = np.round(A[:, hk_in_keep] * (2.0 ** eta))
    if eps != 0.0:
        A = A + rng.poisson(A * eps).astype(np.float64)
    if delta != 0.0:
        B[:, mod] = np.round(B[:, mod] * (2.0 ** delta))
    return build_pseudobulk(A), build_pseudobulk(B)


def run_all(backgrounds):
    all_rows = []
    per_bg = {}
    for bg_name, bg_cfg in backgrounds.items():
        print(f"\n===== background: {bg_name} =====", flush=True)
        t0 = time.time()
        X, hk_in_keep, non_hk_in_keep = load_background(**bg_cfg)
        n_cells_total, n_keep = X.shape
        print(f"  loaded {n_cells_total} cells x {n_keep} genes "
              f"({time.time() - t0:.0f}s)", flush=True)

        module_pools = {s: np.sort(np.random.RandomState(s).choice(
            non_hk_in_keep, size=500, replace=False)) for s in MODULE_SEEDS}

        # ---- stage 1: null baseline reps, collect pseudobulks
        null_pbs = []   # list of (pb_a, pb_b)
        null_rows = []
        for r in range(N_NULL_REPS):
            rng = np.random.RandomState(1000 + r)
            pb_a, pb_b = simulate_pair_pbs(X, rng=rng, hk_in_keep=hk_in_keep)
            null_pbs.append((pb_a, pb_b))
            m = base_metrics(pb_a, pb_b, hk_in_keep, non_hk_in_keep)
            null_rows.append({"background": bg_name, "series": "baseline",
                              "rep": r, "delta": 0.0, "eta": 0.0, "eps": 0.0,
                              "module_seed": 42, **m})
        print(f"  baseline: {N_NULL_REPS} reps ({time.time() - t0:.0f}s)", flush=True)

        # ---- stage 2: fit whitening operators on the null ONLY
        pb_all = np.vstack([np.asarray(v) for pair in null_pbs for v in pair])   # (400, G)
        pb_mean = pb_all.mean(axis=0)
        # PCA on centered null pseudobulks
        U, S, Vt = np.linalg.svd(pb_all - pb_mean, full_matrices=False)
        V = Vt[:N_PC].T                       # (G, 20)
        # null PC-score differences
        d_pc = np.vstack([(a - b) @ V for a, b in null_pbs])      # (200, 20)
        mu_pc = d_pc.mean(axis=0)
        S_pc = np.cov(d_pc, rowvar=False)                         # (20, 20)
        S_pc = (S_pc + S_pc.T) / 2
        S_pc[np.diag_indices(N_PC)] += RIDGE * np.trace(S_pc)
        S_inv = np.linalg.inv(S_pc)
        # diagonal gene-wise whitening from null differences
        d_gene = np.vstack([a - b for a, b in null_pbs])           # (200, G)
        sig_g = d_gene.std(axis=0)
        sig_g[sig_g < 1e-12] = 1e-12
        print("  whitening operators fit on null "
              f"(PC var range {np.trace(S_pc)/N_PC:.4g})", flush=True)

        def whiten_metrics(pb_a, pb_b):
            dp = (pb_a - pb_b) @ V - mu_pc
            m_pc = float(np.sqrt(dp @ S_inv @ dp))
            dg = (pb_a - pb_b) / sig_g
            m_diag = float(np.sqrt(np.mean(dg ** 2)))
            return {"mahal_pc": m_pc, "mahal_diag": m_diag}

        # baseline rows get whitened scores too (same operator)
        for r, (pb_a, pb_b) in enumerate(null_pbs):
            null_rows[r].update(whiten_metrics(pb_a, pb_b))
        rows = null_rows

        # ---- stage 3: signal + neutral series with same operators
        def run_series(series, delta=0.0, eta=0.0, eps=0.0, n_reps=N_REPS,
                       module_seed=42):
            mod = module_pools[module_seed][:MODULE_SIZE]
            out = []
            for r in range(n_reps):
                rng = np.random.RandomState(1000 + r)
                pb_a, pb_b = simulate_pair_pbs(
                    X, delta=delta, eta=eta, eps=eps, rng=rng, mod=mod,
                    hk_in_keep=hk_in_keep)
                m = base_metrics(pb_a, pb_b, hk_in_keep, non_hk_in_keep)
                m.update(whiten_metrics(pb_a, pb_b))
                out.append({"background": bg_name, "series": series, "rep": r,
                            "delta": delta, "eta": eta, "eps": eps,
                            "module_seed": module_seed, **m})
            return out

        t1 = time.time()
        for d in DELTA_GRID:
            for s in MODULE_SEEDS:
                rows += run_series("signal", delta=d, module_seed=s)
        for e in ETA_GRID:
            rows += run_series("neutral_hk", eta=e)
        for e in EPS_GRID:
            rows += run_series("neutral_global", eps=e)
        print(f"  signal+neutral series done ({time.time() - t1:.0f}s)", flush=True)

        raw = pd.DataFrame(rows)
        all_rows.append(raw)

        # ---- per-background analysis
        base = raw[raw["series"] == "baseline"]
        thresholds = {m: float(np.nanpercentile(base[m], NULL_Q))
                     for m in METRIC_COLS}
        logmad = {}
        for m in METRIC_COLS:
            v = np.log(base[m].to_numpy(dtype=float))
            logmad[m] = float(np.median(np.abs(v - np.median(v))))
        analysis = {"null_thresholds_q95": thresholds,
                    "null_log_mad": logmad, "n_baseline": len(base)}

        def exceed(df):
            return {m: float((df[m] > thresholds[m]).mean()) for m in METRIC_COLS}

        typeI = {s: exceed(raw[raw["series"] == s])
                 for s in ["neutral_hk", "neutral_global"]}
        power = {str(d): exceed(raw[(raw["series"] == "signal") &
                                    (raw["delta"] == d)]) for d in DELTA_GRID}
        grid_d = [0.0] + DELTA_GRID
        means_by_d = {}
        for d in grid_d:
            sub = base if d == 0.0 else raw[(raw["series"] == "signal") &
                                            (raw["delta"] == d)]
            means_by_d[d] = {m: float(sub[m].mean()) for m in METRIC_COLS}
        mono = {}
        for m in METRIC_COLS:
            rho, p = spearmanr(grid_d, [means_by_d[d][m] for d in grid_d])
            mono[m] = {"spearman_rho": round(float(rho), 4), "p": float(p)}
        sig = raw[(raw["series"] == "signal") & (raw["delta"] >= 0.25)]
        neu = raw[raw["series"].isin(["neutral_hk", "neutral_global"])]
        y = np.r_[np.ones(len(sig)), np.zeros(len(neu))]
        auc = {}
        for m in METRIC_COLS:
            x = np.r_[sig[m].to_numpy(), neu[m].to_numpy()]
            rk = rankdata(x)
            auc[m] = round(float((rk[y == 1].sum() - len(sig) * (len(sig) + 1) / 2)
                                 / (len(sig) * len(neu))), 4)
        analysis.update({"type_I_error": typeI, "power": power,
                         "monotonicity_vs_delta": mono,
                         "auc_signal_vs_neutral": auc})
        per_bg[bg_name] = analysis
        print(f"  [{bg_name}] null log-MAD: "
              + ", ".join(f"{m}={logmad[m]:.4f}" for m in METRIC_COLS))
        print(f"  [{bg_name}] type-I neutral_hk: "
              + ", ".join(f"{m}={v:.3f}" for m, v in typeI["neutral_hk"].items()))
        print(f"  [{bg_name}] AUC signal vs neutral: "
              + ", ".join(f"{m}={v:.3f}" for m, v in auc.items()))

    raw_all = pd.concat(all_rows, ignore_index=True)
    raw_all.to_csv(RESULTS_DIR / "nc80_mj_mahalanobis_raw.csv", index=False)

    with open(RESULTS_DIR / "nc80_mj_mahalanobis_metrics.json", "w") as f:
        json.dump(per_bg, f, indent=2)

    # flat summary csv
    summ_rows = []
    for bg_name, raw in [(b, raw_all[raw_all.background == b]) for b in per_bg]:
        for (series, d, e, eps), g in raw.groupby(
                ["series", "delta", "eta", "eps"]):
            row = {"background": bg_name, "series": series, "delta": d,
                   "eta": e, "eps": eps, "n": len(g)}
            thr = per_bg[bg_name]["null_thresholds_q95"]
            for m in METRIC_COLS:
                row[f"{m}_mean"] = round(float(g[m].mean()), 5)
                row[f"{m}_sd"] = round(float(g[m].std()), 5)
                row[f"{m}_power"] = round(float((g[m] > thr[m]).mean()), 3)
            summ_rows.append(row)
    pd.DataFrame(summ_rows).to_csv(
        RESULTS_DIR / "nc80_mj_mahalanobis_summary.csv", index=False)

    print("\nOutputs written:")
    print(f"  {RESULTS_DIR / 'nc80_mj_mahalanobis_raw.csv'}")
    print(f"  {RESULTS_DIR / 'nc80_mj_mahalanobis_summary.csv'}")
    print(f"  {RESULTS_DIR / 'nc80_mj_mahalanobis_metrics.json'}")


ANNOT_CSV = DATA_DIR / "annotations_FACS.csv"
BACKGROUNDS = {
    "marrow_bcell": dict(background_csv=DATA_DIR / "FACS" / "FACS" / "Marrow-counts.csv",
                         annot_csv=ANNOT_CSV, tissue="Marrow",
                         ct_name="B cell"),
    "skin_keratinocyte": dict(background_csv=DATA_DIR / "FACS" / "FACS" / "Skin-counts.csv",
                              annot_csv=ANNOT_CSV, tissue="Skin",
                              ct_name="keratinocyte stem cell"),
}

if __name__ == "__main__":
    run_all(BACKGROUNDS)
