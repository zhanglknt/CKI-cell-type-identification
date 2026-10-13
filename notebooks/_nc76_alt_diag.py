"""Diagnostic: MGE alt-HK (lowest-CV) arm with per-pair log k_f / log k_n
tracking, to interpret the obs~null collapse under the alternative anchor
panel. B=200, seed 43 (same as nc76_brain_followup alt arm)."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *
import numpy as np
import pandas as pd
import h5py
from cki.core import js_divergence

MIN_REGION_N, N_TOP_KF, N_HVG, BATCH, EPS = 50, 200, 5000, 5000, 1e-15
B = 200
path = DATA_DIR / "brain" / "neurons" / "MGE_interneuron.h5ad"
hk_human = set(pd.read_csv(HK_FILE, sep=";", engine="python")["Human"].dropna().astype(str))

def read_cat(obj, name):
    g = obj[name]
    if isinstance(g, h5py.Dataset):
        return np.array([x.decode() if isinstance(x, bytes) else str(x) for x in g[:]], dtype=object)
    cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
    return np.array(cats, dtype=object)[g["codes"][:]]

def region_pbs(assign_idx, weights, means):
    n_r = int(assign_idx.max()) + 1 if len(assign_idx) else 0
    pbs = np.zeros((n_r, means.shape[1]))
    for r in range(n_r):
        m = assign_idx == r
        if not m.any(): continue
        w = weights[m]
        pb = (means[m] * w[:, None]).sum(0) / w.sum()
        t = pb.sum()
        pbs[r] = np.log1p(pb / t * 1e4) if t > 0 else pb
    return pbs

def stats(PB, hk_r, nh_r):
    n = PB.shape[0]
    w = []; lkf = []; lkn = []
    for i in range(n):
        pi = PB[i]
        for j in range(i + 1, n):
            pj = PB[j]
            kn = js_divergence(pi[hk_r], pj[hk_r])
            ad = np.abs(pi - pj)[nh_r]
            t = min(N_TOP_KF, len(ad))
            tg = nh_r[np.argpartition(ad, -t)[-t:]]
            kf = js_divergence(pi[tg], pj[tg])
            w.append(kf / kn if kn > EPS else np.inf)
            lkf.append(np.log(max(kf, EPS))); lkn.append(np.log(max(kn, EPS)))
    return float(np.mean(w)), float(np.mean(lkf)), float(np.mean(lkn))

with h5py.File(path, "r") as f:
    X = f["X"]; indptr = X["indptr"][:]; data = X["data"]; indices = X["indices"]
    n_cells = len(indptr) - 1
    var_gene = read_cat(f["var"], "Gene").astype(str)
    n_genes = len(var_gene)
    roi = read_cat(f["obs"], "roi").astype(str)
    samp = read_cat(f["obs"], "sample_id").astype(str)
    region_counts = pd.Series(roi).value_counts()
    regions_ok = sorted(region_counts[region_counts >= MIN_REGION_N].index)
    region_idx = {r: i for i, r in enumerate(regions_ok)}
    roi_ok = np.isin(roi, regions_ok)
    uniq_s, samp_code = np.unique(samp, return_inverse=True)
    samp_region = np.array([region_idx.get(r, -1) for r in roi])
    n_samples = len(uniq_s)
    gene_sums = np.zeros(n_genes); s_sums = np.zeros((n_samples, n_genes))
    s_counts = np.zeros(n_samples, dtype=np.int64)
    for start in range(0, n_cells, BATCH):
        end = min(start + BATCH, n_cells)
        lo, hi = int(indptr[start]), int(indptr[end])
        idx = indices[lo:hi]; dat = data[lo:hi].astype(np.float64)
        np.add.at(gene_sums, idx, dat)
        for ci in range(start, end):
            if roi_ok[ci]:
                s = samp_code[ci]
                r0, r1 = int(indptr[ci]) - lo, int(indptr[ci + 1]) - lo
                if r1 > r0:
                    np.add.at(s_sums[s], idx[r0:r1], dat[r0:r1]); s_counts[s] += 1

hk_global = np.array(sorted({i for i, s in enumerate(var_gene) if s in hk_human}), dtype=int)
means_all = gene_sums / n_cells
m = np.ones(n_genes, bool); m[hk_global] = False
nm = means_all.copy(); nm[~m] = -np.inf
hvg = np.argsort(nm)[-N_HVG:][::-1]

ok_s = s_counts > 0
region_per_code = np.zeros(n_samples, dtype=int)
region_per_code[samp_code] = samp_region
s_means_full = s_sums / np.maximum(s_counts, 1)[:, None]
pb_full = region_pbs(region_per_code[ok_s], s_counts[ok_s].astype(np.float64), s_means_full[ok_s])
detected = (pb_full > 0).all(0) & (pb_full.mean(0) > 0.5)
cv = np.full(n_genes, np.inf)
cv[detected] = (pb_full.std(0) / np.maximum(pb_full.mean(0), 1e-12))[detected]
alt_hk = np.sort(np.argsort(cv)[:len(hk_global)])
keep = np.sort(np.union1d(alt_hk, hvg))
pos = {g: i for i, g in enumerate(keep)}
hk_r = np.array([pos[g] for g in alt_hk])
nh_r = np.array([i for i, g in enumerate(keep) if g not in set(alt_hk)])
s_means = s_sums[:, keep] / np.maximum(s_counts, 1)[:, None]
s_means = s_means[ok_s]
s_weights = s_counts[ok_s].astype(np.float64)
s_region = region_per_code[ok_s]
n_s = len(s_weights)

obs = stats(region_pbs(s_region, s_weights, s_means), hk_r, nh_r)
print(f"obs: mean_w={obs[0]:.2f} mean_log_kf={obs[1]:.4f} mean_log_kn={obs[2]:.4f}")
rng = np.random.RandomState(43)
nl_w, nl_kf, nl_kn = [], [], []
for b in range(B):
    perm = s_region[rng.permutation(n_s)]
    st = stats(region_pbs(perm, s_weights, s_means), hk_r, nh_r)
    nl_w.append(st[0]); nl_kf.append(st[1]); nl_kn.append(st[2])
print(f"null: mean_w={np.mean(nl_w):.2f} mean_log_kf={np.mean(nl_kf):.4f} mean_log_kn={np.mean(nl_kn):.4f}")
print(f"kf fold obs/null = {np.exp(obs[1]-np.mean(nl_kf)):.2f}; kn fold obs/null = {np.exp(obs[2]-np.mean(nl_kn)):.2f}")
print(f"obs kn = {np.exp(obs[2]):.6f}; null kn = {np.exp(np.mean(nl_kn)):.6f}")
# also HRT reference kn scale
keep_h = np.sort(np.union1d(hk_global, hvg))
pos_h = {g: i for i, g in enumerate(keep_h)}
hk_r_h = np.array([pos_h[g] for g in hk_global])
nh_r_h = np.array([i for i, g in enumerate(keep_h) if g not in set(hk_global)])
s_means_h = s_sums[:, keep_h] / np.maximum(s_counts, 1)[:, None]
s_means_h = s_means_h[ok_s]
obs_h = stats(region_pbs(s_region, s_weights, s_means_h), hk_r_h, nh_r_h)
print(f"HRT obs: kn={np.exp(obs_h[2]):.6f} kf={np.exp(obs_h[1]):.4f} w={obs_h[0]:.2f}")
# expression level of the two panels
print(f"alt panel mean log1p expr = {pb_full[ :, alt_hk].mean():.2f}; HRT panel = {pb_full[:, hk_global].mean():.2f}")
print("DONE")
