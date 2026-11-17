# -*- coding: utf-8 -*-
"""nc80 M-H round 2: constraint x abundance 2x2 grid for the brain
neuronal-superclass regional elevation.

Round-1 finding (results/nc80_mh_expr_matched_cv.*): the lowest-CV panel is
the HIGH-abundance panel (mean 1.07-1.16 log1p-CP10k vs HRT 0.31-0.32), and
an upward-matched pool (expression >= 25th pct of HRT = 0.13) does not bind
-- CVhi == CV identically. The SI Note 18 wording is directionally correct
("mean expression 1.13 versus 0.32", lowest-CV as antecedent); the panel's
bio-m7 reading had the direction reversed. The decisive control therefore
matches abundance DOWNWARD.

Grid (each arm internally calibrated against its own block-shuffle null):
  HRT / EL   literature anchor, low abundance      : elevation present
             (nc78 arm, results/nc78_alt_hk_brain.csv)
  CV         lowest-CV, high abundance             : elevation absent
             (nc78 arm; CVhi == CV, round 1)
  CVlo       lowest-CV within the HRT abundance stratum (expr <= 90th pct
             of in-file HRT expression, positive in all regions),
             size-matched                                          -- NEW
  RNDhi      random anchor drawn from the same detected high-abundance
             pool the CV panel is drawn from, size-matched, seed 43     -- NEW

Attribution logic:
  CVlo elevation returns  -> CV-panel null is an abundance artifact;
                             headline survives with a constrained-low-
                             abundance nuance.
  CVlo stays null         -> the data-driven constrained panel removes the
                             elevation even at matched abundance -> genuine
                             anchor-type dependence -> demote headline to
                             anchor-conditional.
  RNDhi stays null        -> high abundance alone suffices to remove the
                             elevation (independent of the CV rule).
  RNDhi elevation present -> abundance alone does not remove it; the CV
                             selection rule itself is what matters.

Mechanism is nc78-arm-identical: block = sample_id; permute sample -> region
vector (preserves per-region sample counts); region pseudobulks =
cell-count-weighted sample means -> norm 1e4 -> log1p; per-pair top-200
non-anchor identity genes; softmax-on-log1p JS; mean pair omega; one-sided
upper-tail P; B = 200 per arm, seed 43 (fresh per arm).

Outputs: results/nc80_mh2_grid.csv / .txt
"""
import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HK_HRT = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
OUT_CSV = ROOT / "results" / "nc80_mh2_grid.csv"
OUT_TXT = ROOT / "results" / "nc80_mh2_grid.txt"

MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
B_PERM = 200
SEED = 43
BATCH = 5000
EPS = 1e-15

hrt_syms = set(pd.read_csv(HK_HRT, sep=";")["Human"].dropna().astype(str))

lines = []
def log(msg=""):
    print(msg, flush=True)
    lines.append(str(msg))

def read_cat(obj, name):
    g = obj[name]
    if isinstance(g, h5py.Dataset):
        return np.array([x.decode() if isinstance(x, bytes) else str(x)
                         for x in g[:]], dtype=object)
    cats = [x.decode() if isinstance(x, bytes) else str(x)
            for x in g["categories"][:]]
    return np.array(cats, dtype=object)[g["codes"][:]]

def region_pbs(assign_idx, weights, means):
    n_r = int(assign_idx.max()) + 1 if len(assign_idx) else 0
    pbs = np.zeros((n_r, means.shape[1]))
    np.add.at(pbs, assign_idx, means * weights[:, None])
    cnts = np.zeros(n_r)
    np.add.at(cnts, assign_idx, weights)
    pbs /= np.maximum(cnts, 1)[:, None]
    t = pbs.sum(1, keepdims=True)
    pbs = np.log1p(pbs / np.maximum(t, 1e-12) * 1e4)
    return pbs

def _softmax_rows(M):
    Z = M - M.max(1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(1, keepdims=True)

def pair_omega_vec(PB, hk_r, nh_r, n_top=N_TOP_KF):
    R = PB.shape[0]
    if R < 2:
        return np.array([]), np.array([]), np.array([])
    pi_, pj_ = np.triu_indices(R, 1)
    n_pairs = len(pi_)

    def _js_chunk(p, q):
        m = 0.5 * (p + q)
        with np.errstate(divide="ignore", invalid="ignore"):
            kl1 = np.where(p > 0,
                           p * np.log2(np.where(p > 0, p, 1) / m), 0.0).sum(1)
            kl2 = np.where(q > 0,
                           q * np.log2(np.where(q > 0, q, 1) / m), 0.0).sum(1)
        return 0.5 * kl1 + 0.5 * kl2

    P = _softmax_rows(PB[:, hk_r])
    kn = np.empty(n_pairs)
    CH = 1500
    for s in range(0, n_pairs, CH):
        e = min(s + CH, n_pairs)
        kn[s:e] = _js_chunk(P[pi_[s:e]], P[pj_[s:e]])
    N = PB[:, nh_r]
    kf = np.empty(n_pairs)
    k = min(n_top, N.shape[1])
    CH2 = 400
    rows_c = np.arange(CH2)[:, None]
    for s in range(0, n_pairs, CH2):
        e = min(s + CH2, n_pairs)
        a = N[pi_[s:e]]
        b = N[pj_[s:e]]
        d = np.abs(a - b)
        top = np.argpartition(d, -k, axis=1)[:, -k:]
        rr = rows_c[:e - s]
        av = _softmax_rows(a[rr, top])
        bv = _softmax_rows(b[rr, top])
        kf[s:e] = _js_chunk(av, bv)
    w = kf / np.maximum(kn, EPS)
    return w, kn, kf

def build_universe(hk_idx, gene_means):
    m = np.ones(len(gene_means), bool)
    m[hk_idx] = False
    nm = gene_means.copy()
    nm[~m] = -np.inf
    hvg = np.argsort(nm)[-N_HVG:]
    keep = np.sort(np.union1d(hk_idx, hvg))
    pos = {g: i for i, g in enumerate(keep)}
    hk_r = np.array([pos[g] for g in hk_idx])
    nh_r = np.array([i for i in range(len(keep)) if i not in set(hk_r)])
    return keep, hk_r, nh_r

T0 = time.time()
rows = []

def perm_arm(label, defname, hk_idx, s_means, w64, region_of, gene_means):
    keep, hk_r, nh_r = build_universe(hk_idx, gene_means)
    sm = s_means[:, keep]
    obs_mean = float(pair_omega_vec(region_pbs(region_of, w64, sm),
                                    hk_r, nh_r)[0].mean())
    rng = np.random.RandomState(SEED)
    null_means = np.empty(B_PERM)
    n_s = len(w64)
    for b in range(B_PERM):
        perm = region_of[rng.permutation(n_s)]
        null_means[b] = float(pair_omega_vec(region_pbs(perm, w64, sm),
                                             hk_r, nh_r)[0].mean())
    p_up = float((null_means >= obs_mean).mean())
    log(f"{label} DEF-{defname} PERM: obs={obs_mean:.3f} "
        f"null={null_means.mean():.3f} P_upper={p_up:.4f} "
        f"(B={B_PERM}, {time.time()-T0:.0f}s)")
    return {"unit": label, "definition": defname,
            "n_hk": int(len(hk_idx)),
            "obs_mean_omega": obs_mean,
            "null_mean_omega": float(null_means.mean()),
            "P_upper": p_up, "B": B_PERM}

def run_superclass(label, s_means, s_weights, s_region, gene_means, var_gene):
    cell_per_region = pd.Series(s_weights.astype(float)).groupby(
        pd.Series(s_region)).sum()
    regions_ok = sorted(cell_per_region[cell_per_region >= MIN_REGION_N].index)
    r_idx = {r: i for i, r in enumerate(regions_ok)}
    region_of = np.array([r_idx.get(r, -1) for r in s_region])
    keep_s = region_of >= 0
    s_means, s_weights, region_of = (s_means[keep_s], s_weights[keep_s],
                                     region_of[keep_s])
    w64 = s_weights.astype(np.float64)
    pb_full = region_pbs(region_of, w64, s_means)

    hrt_in = np.array(sorted(i for i, s in enumerate(var_gene)
                             if s in hrt_syms), dtype=int)
    expr = pb_full.mean(0)
    pos_all = (pb_full > 0).all(0)
    detected = pos_all & (expr > 0.5)          # nc78 CV pool
    cv = np.full(len(var_gene), np.inf)
    ok = pos_all & (expr > 0)
    cv[ok] = (pb_full.std(0) / np.maximum(expr, 1e-12))[ok]
    n_hk = len(hrt_in)

    # CVlo: lowest-CV within the HRT abundance stratum
    thr_hi = float(np.percentile(expr[hrt_in], 90))
    pool_lo = ok & (expr <= thr_hi)
    pool_lo_idx = np.where(pool_lo)[0]
    log(f"{label}: CVlo pool thr_hi={thr_hi:.3f} n_pool={len(pool_lo_idx)}")
    order = np.argsort(cv[pool_lo_idx])[:n_hk]
    cvlo = np.sort(pool_lo_idx[order]).astype(int)

    # RNDhi: random from the detected high-abundance pool (same pool as CV)
    det_idx = np.where(detected)[0]
    rng_sel = np.random.RandomState(SEED)
    rndhi = np.sort(rng_sel.choice(det_idx, size=n_hk,
                                    replace=False)).astype(int)
    log(f"{label}: RNDhi pool n={len(det_idx)}; "
        f"mean_expr CVlo={expr[cvlo].mean():.3f} "
        f"(HRT {expr[hrt_in].mean():.3f}); "
        f"mean_expr RNDhi={expr[rndhi].mean():.3f}")
    log(f"{label}: overlap with HRT: CVlo "
        f"{len(set(cvlo.tolist()) & set(hrt_in.tolist()))}, RNDhi "
        f"{len(set(rndhi.tolist()) & set(hrt_in.tolist()))}")

    rows.append(perm_arm(label, "CVlo", cvlo, s_means, w64, region_of,
                         gene_means))
    rows.append(perm_arm(label, "RNDhi", rndhi, s_means, w64, region_of,
                         gene_means))

def stream_file(path):
    with h5py.File(path, "r") as f:
        X = f["X"]; indptr = X["indptr"][:]; data = X["data"]
        indices = X["indices"]
        n_cells = len(indptr) - 1
        var_gene = read_cat(f["var"], "Gene").astype(str)
        roi = read_cat(f["obs"], "roi").astype(str)
        samp = read_cat(f["obs"], "sample_id").astype(str)
        n_genes = len(var_gene)
        uniq, code = np.unique(samp, return_inverse=True)
        n_ug = len(uniq)
        sums = np.zeros((n_ug, n_genes))
        counts = np.zeros(n_ug, dtype=np.int64)
        for start in range(0, n_cells, BATCH):
            end = min(start + BATCH, n_cells)
            lo, hi = int(indptr[start]), int(indptr[end])
            idx = indices[lo:hi]; dat = data[lo:hi].astype(np.float64)
            for ci in range(start, end):
                r0, r1 = int(indptr[ci]) - lo, int(indptr[ci + 1]) - lo
                if r1 > r0:
                    g = code[ci]
                    np.add.at(sums[g], idx[r0:r1], dat[r0:r1])
                    counts[g] += 1
        seen = {}
        for ci in range(n_cells):
            g = code[ci]
            if g not in seen:
                seen[g] = roi[ci]
        region_of_ug = np.array([seen[g] for g in range(n_ug)],
                                dtype=object)
        return sums, counts, region_of_ug, var_gene

for name, fname in [
        ("MGE interneuron", "MGE_interneuron.h5ad"),
        ("Thalamic excitatory", "Thalamic_excitatory.h5ad"),
        ("Upper-layer intratelencephalic",
         "Upper-layer_intratelencephalic.h5ad")]:
    t1 = time.time()
    log(f"== {name}: streaming {fname} ...")
    sums, counts, region_of_ug, var_gene = stream_file(
        ROOT / "data" / "brain" / "neurons" / fname)
    log(f"   {len(counts)} samples; stream {time.time()-t1:.0f}s")
    means = sums / np.maximum(counts, 1)[:, None]
    gene_means = sums.sum(0) / max(int(counts.sum()), 1)
    run_superclass(name, means, counts.astype(np.float64), region_of_ug,
                   gene_means, var_gene)

res = pd.DataFrame(rows)
res.to_csv(OUT_CSV, index=False)
log(f"saved: {OUT_CSV}")
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
log(f"total {time.time()-T0:.0f}s")
print("DONE")
