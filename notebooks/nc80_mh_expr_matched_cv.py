# -*- coding: utf-8 -*-
"""nc80 M-H (panel methods-M4 = bio-m7 = editor R6/R7): expression-matched
lowest-CV HK control for the brain neuronal-superclass regional elevation.

Question: the superclass elevation survives the two literature HK lists
(HRT Atlas; Eisenberg & Levanon 2013) but vanishes under the matched-size
lowest-CV data-driven panel (nc78 arm, results/nc78_alt_hk_brain.csv), whose
member genes are far less abundant (mean 1.13 vs 0.32 log1p-CP10k). Is the
vanishing an abundance artifact, or a genuine anchor-type dependence?

Decisive control (DEF-CVhi): lowest-CV panel of matched size drawn from an
abundance-matched candidate pool -- detected genes whose region-pseudobulk
mean expression is at or above the 25th percentile of the in-file HRT panel
(the literature anchor the main text uses). If the elevation returns under
CVhi, the lowest-CV null result is an abundance artifact; if it stays null,
the elevation requires literature-list anchors and the headline must be
demoted to anchor-conditional.

Mechanism is nc78-arm-identical (block = sample_id; permute the sample ->
region vector, which preserves per-region sample counts; region pseudobulks
= cell-count-weighted sample means -> norm 1e4 -> log1p; per-pair top-200
non-anchor identity genes; softmax-on-log1p JS; mean pair omega; one-sided
upper-tail P; B = 200, seed 43 -- resolution floor 1/201).

Observed mean omega is also recomputed for DEF-EL and DEF-CV (no
permutations) so the three panels can be compared side by side; the DEF-CV
observed values must reproduce results/nc78_alt_hk_brain.csv to the digit
(internal validation that the streaming machinery matches).

Outputs: results/nc80_mh_expr_matched_cv.csv / .txt
"""
import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HK_HRT = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
HK_EL = ROOT / "data" / "housekeeping" / "eisenberg_levanon_2013_hk.txt"
OUT_CSV = ROOT / "results" / "nc80_mh_expr_matched_cv.csv"
OUT_TXT = ROOT / "results" / "nc80_mh_expr_matched_cv.txt"

MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
B_PERM = 200
SEED = 43
BATCH = 5000
EPS = 1e-15

hrt_syms = set(pd.read_csv(HK_HRT, sep=";")["Human"].dropna().astype(str))
el_syms = set(l.split("\t")[0].strip() for l in
              HK_EL.read_text().splitlines() if l.strip())

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
    """Weighted sample-mean aggregation -> norm-1e4 log1p (08d convention)."""
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
    """Vectorized all-pairs omega (cki softmax-on-log1p mapping)."""
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

def run_superclass(label, s_means, s_weights, s_region, gene_means, var_gene):
    """Panel construction + characterization + CVhi permutation test."""
    cell_per_region = pd.Series(s_weights.astype(float)).groupby(
        pd.Series(s_region)).sum()
    regions_ok = sorted(cell_per_region[cell_per_region >= MIN_REGION_N].index)
    r_idx = {r: i for i, r in enumerate(regions_ok)}
    if len(regions_ok) < 2:
        log(f"{label}: <2 eligible regions - skipped")
        return
    region_of = np.array([r_idx.get(r, -1) for r in s_region])
    keep_s = region_of >= 0
    s_means, s_weights, region_of = (s_means[keep_s], s_weights[keep_s],
                                     region_of[keep_s])
    w64 = s_weights.astype(np.float64)
    pb_full = region_pbs(region_of, w64, s_means)

    # ---- panel construction ----
    hrt_in = np.array(sorted(i for i, s in enumerate(var_gene)
                             if s in hrt_syms), dtype=int)
    el_in = np.array(sorted(i for i, s in enumerate(var_gene)
                            if s in el_syms), dtype=int)
    expr = pb_full.mean(0)
    detected = (pb_full > 0).all(0) & (expr > 0.5)
    cv = np.full(len(var_gene), np.inf)
    cv[detected] = (pb_full.std(0) / np.maximum(expr, 1e-12))[detected]
    n_hk = len(hrt_in)

    # DEF-CV: nc78-arm verbatim (lowest-CV among detected, size-matched)
    cv_in = np.sort(np.argsort(cv)[:n_hk]).astype(int)

    # DEF-CVhi: abundance-matched pool (>= 25th pct of HRT in-file
    # expression), then lowest-CV within the pool, size-matched
    hrt_expr = expr[hrt_in]
    pct = 25
    while True:
        thr = float(np.percentile(hrt_expr, pct))
        pool = detected & (expr >= thr)
        n_pool = int(pool.sum())
        if n_pool >= n_hk or pct <= 0:
            break
        pct = max(0, pct - 5)   # fall back until the pool is large enough
    pool_idx = np.where(pool)[0]
    order = np.argsort(cv[pool_idx])[:n_hk]
    cvhi = np.sort(pool_idx[order]).astype(int)

    # ---- characterization (common scale: region-pseudobulk log1p-CP10k) ----
    def char(idx):
        idx = np.asarray(idx, dtype=int)
        ov = len(set(idx.tolist()) & set(hrt_in.tolist()))
        return {"n": int(len(idx)),
                "mean_expr": float(expr[idx].mean()),
                "median_expr": float(np.median(expr[idx])),
                "median_cv": float(np.median(cv[idx])),
                "hrt_overlap": ov,
                "hrt_overlap_frac": float(ov / max(len(idx), 1))}

    log(f"{label}: n_regions={len(regions_ok)} "
        f"n_pairs={len(regions_ok)*(len(regions_ok)-1)//2} "
        f"n_hrt_in_file={n_hk} n_el_in_file={len(el_in)}")
    log(f"{label}: CVhi pool pct={pct} thr={thr:.3f} n_pool={n_pool}")
    log(f"{label}: HRT  {char(hrt_in)}")
    log(f"{label}: EL   n={char(el_in)['n']} "
        f"mean_expr={char(el_in)['mean_expr']:.3f}")
    log(f"{label}: CV   {char(cv_in)}")
    log(f"{label}: CVhi {char(cvhi)}")

    # ---- observed mean omega per def (deterministic) ----
    obs = {}
    for defname, hk_idx in [("EL", el_in), ("CV", cv_in), ("CVhi", cvhi)]:
        if len(hk_idx) < 20:
            log(f"{label} DEF-{defname}: only {len(hk_idx)} anchor genes "
                f"in file - skipped")
            continue
        keep, hk_r, nh_r = build_universe(hk_idx, gene_means)
        sm = s_means[:, keep]
        obs[defname] = float(pair_omega_vec(region_pbs(region_of, w64, sm),
                                            hk_r, nh_r)[0].mean())
        log(f"{label} DEF-{defname}: obs_mean_omega={obs[defname]:.3f}")

    # ---- permutation arm: DEF-CVhi only (B=200, seed 43) ----
    rng = np.random.RandomState(SEED)
    hk_idx = cvhi
    keep, hk_r, nh_r = build_universe(hk_idx, gene_means)
    sm = s_means[:, keep]
    obs_mean = obs.get("CVhi")
    null_means = np.empty(B_PERM)
    n_s = len(s_weights)
    for b in range(B_PERM):
        perm = region_of[rng.permutation(n_s)]
        null_means[b] = float(pair_omega_vec(region_pbs(perm, w64, sm),
                                             hk_r, nh_r)[0].mean())
    p_up = float((null_means >= obs_mean).mean())
    log(f"{label} DEF-CVhi PERM: obs={obs_mean:.3f} "
        f"null={null_means.mean():.3f} P_upper={p_up:.4f} "
        f"(B={B_PERM}, {time.time()-T0:.0f}s)")

    c_hrt, c_cv, c_cvhi = char(hrt_in), char(cv_in), char(cvhi)
    rows.append({"unit": label, "definition": "CVhi", "n_regions":
                 len(regions_ok), "n_pairs":
                 len(regions_ok) * (len(regions_ok) - 1) // 2,
                 "n_hk": c_cvhi["n"], "pool_pct": pct, "pool_thr": thr,
                 "pool_n": n_pool, "obs_mean_omega": obs_mean,
                 "null_mean_omega": float(null_means.mean()),
                 "P_upper": p_up, "B": B_PERM,
                 "obs_mean_omega_EL": obs.get("EL"),
                 "obs_mean_omega_CV": obs.get("CV"),
                 "mean_expr_HRT": c_hrt["mean_expr"],
                 "mean_expr_CV": c_cv["mean_expr"],
                 "mean_expr_CVhi": c_cvhi["mean_expr"],
                 "median_cv_HRT": c_hrt["median_cv"],
                 "median_cv_CV": c_cv["median_cv"],
                 "median_cv_CVhi": c_cvhi["median_cv"],
                 "hrt_overlap_CV": c_cv["hrt_overlap"],
                 "hrt_overlap_CVhi": c_cvhi["hrt_overlap"],
                 "hrt_overlap_frac_CV": c_cv["hrt_overlap_frac"],
                 "hrt_overlap_frac_CVhi": c_cvhi["hrt_overlap_frac"]})

def stream_file(path):
    """One h5py pass -> per-sample sums/counts + region vector."""
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
