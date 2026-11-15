# -*- coding: utf-8 -*-
"""
nc78 P0-4 (#1221, scmethod-M1 extended): alternative housekeeping-anchor
sensitivity for the brain primary claims.

Claims under test (recomputed under TWO independent HK definitions):
  (1) neuronal-superclass regional elevation (block-shuffle A-stat:
      MGE P = 0.001, upper-layer IT P = 0.014, Thalamic P = 0.163);
  (2) the non-neuronal class gradient (astrocyte highest ~82.8 vs
      Bergmann glia lowest ~13.6; 6.10-fold raw) and the 08d per-class
      block-shuffle upper-tail tests.

Independent HK definitions:
  DEF-EL   Eisenberg & Levanon 2013 list (3,804 genes; literature);
  DEF-CV   lowest-CV data-driven panel, size-matched to the in-file HRT
           panel (verbatim the _nc76_alt_diag construction).

Mechanism is 08d-identical: blocks = 10x libraries (sample_id), permute the
sample -> region vector (preserving the per-region sample-count multiset),
region pseudobulks = cell-count-weighted means of sample raw means ->
norm 1e4 -> log1p, per-pair top-200 identity genes among non-anchor genes,
JS via the softmax(log1p) = (1+y)/sum(1+y) identity, mean pair omega,
one-sided upper-tail P. B = 200 for the three superclasses (seed 43,
matching the nc76 alternative-anchor arm), B = 100 for the ten
non-neuronal classes (resolution floor 0.01).

Outputs:
  results/nc78_alt_hk_brain.csv / .txt
"""
import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HK_HRT = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
HK_EL = ROOT / "data" / "housekeeping" / "eisenberg_levanon_2013_hk.txt"
OUT_CSV = ROOT / "results" / "nc78_alt_hk_brain.csv"
OUT_TXT = ROOT / "results" / "nc78_alt_hk_brain.txt"

MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
B_SUPER, B_NONNEU = 200, 100
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
    """softmax over rows: exp(M - max) / sum -- the cki ensure_probability
    distribution mode='softmax' applied to log1p-scale pseudobulks."""
    Z = M - M.max(1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(1, keepdims=True)

def pair_omega_vec(PB, hk_r, nh_r, n_top=N_TOP_KF):
    """Vectorized all-pairs kn/kf/omega (cki softmax-on-log1p mapping)."""
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

    # k_n panel
    P = _softmax_rows(PB[:, hk_r])
    kn = np.empty(n_pairs)
    CH = 1500
    for s in range(0, n_pairs, CH):
        e = min(s + CH, n_pairs)
        kn[s:e] = _js_chunk(P[pi_[s:e]], P[pj_[s:e]])
    # k_f: per-pair top-|delta| non-HK genes
    N = PB[:, nh_r]
    kf = np.empty(n_pairs)
    k = min(n_top, N.shape[1])
    CH2 = 400
    rows_c = np.arange(CH2)[:, None]
    for s in range(0, n_pairs, CH2):
        e = min(s + CH2, n_pairs)
        a = N[pi_[s:e]]; b = N[pj_[s:e]]
        d = np.abs(a - b)
        top = np.argpartition(d, -k, axis=1)[:, -k:]
        rr = rows_c[:e - s]
        av = _softmax_rows(a[rr, top])
        bv = _softmax_rows(b[rr, top])
        kf[s:e] = _js_chunk(av, bv)
    w = kf / np.maximum(kn, EPS)
    return w, kn, kf

def defs_for_class(var_gene, gene_means, pb_full, hk_hrt_file):
    """HK index sets (EL, CV) + per-def gene universes for one class."""
    hrt_in = {i for i, s in enumerate(var_gene) if s in hrt_syms}
    el_in = {i for i, s in enumerate(var_gene) if s in el_syms}
    detected = (pb_full > 0).all(0) & (pb_full.mean(0) > 0.5)
    cv = np.full(len(var_gene), np.inf)
    cv[detected] = (pb_full.std(0) / np.maximum(pb_full.mean(0),
                                                1e-12))[detected]
    cv_in = np.sort(np.argsort(cv)[:len(hrt_in)])
    return {"EL": np.array(sorted(el_in), dtype=int),
            "CV": cv_in.astype(int)}

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

def run_class(label, s_means, s_weights, s_region, gene_means, var_gene,
              B, rng, rows):
    # region eligibility: >= MIN_REGION_N CELLS (08d convention), counted
    # from the per-sample cell counts, not the number of samples
    cell_per_region = pd.Series(s_weights.astype(float)).groupby(
        pd.Series(s_region)).sum()
    regions_ok = sorted(cell_per_region[cell_per_region >= MIN_REGION_N].index)
    r_idx = {r: i for i, r in enumerate(regions_ok)}
    if len(regions_ok) < 2:
        log(f"{label}: <2 regions with >= {MIN_REGION_N} cells - skipped")
        return
    region_of = np.array([r_idx.get(r, -1) for r in s_region])
    keep_s = region_of >= 0
    s_means, s_weights, region_of = (s_means[keep_s], s_weights[keep_s],
                                     region_of[keep_s])
    pb_full = region_pbs(region_of, s_weights.astype(np.float64), s_means)
    hk_sets = defs_for_class(var_gene, gene_means, pb_full, None)
    n_pairs = len(regions_ok) * (len(regions_ok) - 1) // 2
    for defname, hk_idx in hk_sets.items():
        if len(hk_idx) < 20:
            log(f"{label} DEF-{defname}: only {len(hk_idx)} anchor genes "
                f"in file - skipped")
            continue
        keep, hk_r, nh_r = build_universe(hk_idx, gene_means)
        sm = s_means[:, keep]
        obs = pair_omega_vec(region_pbs(region_of, s_weights.astype(
            np.float64), sm), hk_r, nh_r)[0]
        obs_mean = float(obs.mean())
        null_means = np.empty(B)
        n_s = len(s_weights)
        for b in range(B):
            perm = region_of[rng.permutation(n_s)]
            null_means[b] = float(pair_omega_vec(region_pbs(
                perm, s_weights.astype(np.float64), sm), hk_r,
                nh_r)[0].mean())
        p_up = float((null_means >= obs_mean).mean())
        rows.append({"unit": label, "definition": defname,
                     "n_regions": len(regions_ok), "n_pairs": n_pairs,
                     "n_hk": int(len(hk_idx)),
                     "obs_mean_omega": obs_mean,
                     "null_mean_omega": float(null_means.mean()),
                     "P_upper": p_up, "B": B})
        log(f"{label} DEF-{defname}: n_regions={len(regions_ok)} "
            f"obs_mean_omega={obs_mean:.2f} null={null_means.mean():.2f} "
            f"P_upper={p_up:.4f} (B={B}, {time.time()-T0:.0f}s)")

def stream_file(path, class_col=None):
    """One h5py pass -> per-(class-)sample sums/counts + region vectors."""
    with h5py.File(path, "r") as f:
        X = f["X"]; indptr = X["indptr"][:]; data = X["data"]
        indices = X["indices"]
        n_cells = len(indptr) - 1
        var_gene = read_cat(f["var"], "Gene").astype(str)
        roi = read_cat(f["obs"], "roi").astype(str)
        samp = read_cat(f["obs"], "sample_id").astype(str)
        cls = (read_cat(f["obs"], class_col).astype(str)
               if class_col else [""] * n_cells)
        key = np.array([f"{c}\x00{s}" for c, s in zip(cls, samp)],
                       dtype=object)
        uniq, code = np.unique(key, return_inverse=True)
        n_ug = len(uniq)
        class_of = np.array([u.split("\x00")[0] for u in uniq], dtype=object)
        n_genes = len(var_gene)
        sums = np.zeros((n_ug, n_genes))
        counts = np.zeros(n_ug, dtype=np.int64)
        uniq_samp = np.array([u.split("\x00")[1] for u in uniq],
                             dtype=object)
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
        # region per group from first occurrence (single-region samples)
        seen = {}
        for ci in range(n_cells):
            g = code[ci]
            if g not in seen:
                seen[g] = roi[ci]
        region_of_ug = np.array([seen[g] for g in range(n_ug)],
                                dtype=object)
        return (uniq, class_of, uniq_samp, sums, counts, region_of_ug,
                var_gene)

T0 = time.time()
rows = []
rng = np.random.RandomState(SEED)

# ---- three neuronal superclasses (one class per file) ----
for name, fname in [
        ("MGE interneuron", "MGE_interneuron.h5ad"),
        ("Thalamic excitatory", "Thalamic_excitatory.h5ad"),
        ("Upper-layer intratelencephalic",
         "Upper-layer_intratelencephalic.h5ad")]:
    t1 = time.time()
    log(f"== {name}: streaming {fname} ...")
    (uniq, class_of, uniq_samp, sums, counts, region_of_ug,
     var_gene) = stream_file(ROOT / "data" / "brain" / "neurons" / fname)
    log(f"   {len(uniq)} (class,sample) groups; "
        f"stream {time.time()-t1:.0f}s")
    means = sums / np.maximum(counts, 1)[:, None]
    gene_means = sums.sum(0) / max(int(counts.sum()), 1)
    run_class(name, means, counts.astype(np.float64), region_of_ug,
              gene_means, var_gene, B_SUPER, rng, rows)

# ---- non-neuronal classes (10 classes in one file) ----
log("== Nonneurons.h5ad: streaming (10 classes) ...")
t1 = time.time()
(uniq, class_of, uniq_samp, sums, counts, region_of_ug,
 var_gene) = stream_file(ROOT / "data" / "brain" / "Nonneurons.h5ad",
                         class_col="supercluster_term")
log(f"   {len(uniq)} (class,sample) groups; stream {time.time()-t1:.0f}s")
means = sums / np.maximum(counts, 1)[:, None]
for cls in sorted(set(class_of)):
    m = class_of == cls
    if counts[m].sum() < 500:
        log(f"{cls}: {int(counts[m].sum())} cells - skipped")
        continue
    gm = sums[m].sum(0) / max(int(counts[m].sum()), 1)
    run_class(cls, means[m], counts[m].astype(np.float64),
              region_of_ug[m], gm, var_gene, B_NONNEU,
              rng, rows)

res = pd.DataFrame(rows)
res.to_csv(OUT_CSV, index=False)
log(f"saved: {OUT_CSV}")
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
log(f"total {time.time()-T0:.0f}s")
print("DONE")
