"""LODO addendum for nc75_brain_neuron_decomposition: report leave-one-
donor-out on median omega and mean log omega (finite) instead of mean
omega (can hit inf when a residual pair has kn ~ 0). Appends columns to
results/nc75_brain_neuron_decomposition.csv."""

import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import h5py
from cki.core import js_divergence

MIN_REGION_N, N_TOP_KF, N_HVG, BATCH, EPS = 50, 200, 5000, 5000, 1e-15
FILES = {
    "MGE interneuron": DATA_DIR / "brain" / "neurons" / "MGE_interneuron.h5ad",
    "Thalamic excitatory": DATA_DIR / "brain" / "neurons" / "Thalamic_excitatory.h5ad",
    "Upper-layer intratelencephalic": DATA_DIR / "brain" / "neurons"
                                       / "Upper-layer_intratelencephalic.h5ad",
}
OUT = Path("results/nc75_brain_neuron_decomposition.csv")
hk_human = set(pd.read_csv(HK_FILE, sep=";", engine="python")
               ["Human"].dropna().astype(str))


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
    for r in range(n_r):
        m = assign_idx == r
        if not m.any():
            continue
        w = weights[m]
        pb = (means[m] * w[:, None]).sum(0) / w.sum()
        t = pb.sum()
        pbs[r] = np.log1p(pb / t * 1e4) if t > 0 else pb
    return pbs


def pair_stats(PB, hk_r, nh_r):
    n = PB.shape[0]
    w, lw = [], []
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
            lw.append(np.log(max(kf, EPS)) - np.log(max(kn, EPS)))
    return np.array(w), np.array(lw)


df = pd.read_csv(OUT)
for col in ["lodo_med_min", "lodo_med_max", "lodo_mlogw_min",
            "lodo_mlogw_max"]:
    if col not in df:
        df[col] = np.nan

for sc_name, path in FILES.items():
    print(f"== {sc_name}", flush=True)
    with h5py.File(path, "r") as f:
        X = f["X"]
        indptr = X["indptr"][:]
        data = X["data"]; indices = X["indices"]
        n_cells = len(indptr) - 1
        var_gene = read_cat(f["var"], "Gene").astype(str)
        roi = read_cat(f["obs"], "roi").astype(str)
        samp = read_cat(f["obs"], "sample_id").astype(str)
        donor = read_cat(f["obs"], "donor_id").astype(str)
        region_counts = pd.Series(roi).value_counts()
        regions_ok = sorted(region_counts[region_counts >= MIN_REGION_N].index)
        region_idx = {r: i for i, r in enumerate(regions_ok)}
        roi_ok = np.isin(roi, regions_ok)
        uniq_s, samp_code = np.unique(samp, return_inverse=True)
        samp_region = np.array([region_idx.get(r, -1) for r in roi])
        donor_of_code = np.full(len(uniq_s), "", dtype=object)
        seen = np.zeros(len(uniq_s), bool)
        for ci in range(n_cells):
            s = samp_code[ci]
            if not seen[s]:
                donor_of_code[s] = donor[ci]; seen[s] = True
        n_genes = len(var_gene)
        gene_sums = np.zeros(n_genes)
        s_sums = np.zeros((len(uniq_s), n_genes))
        s_counts = np.zeros(len(uniq_s), dtype=np.int64)
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
                        np.add.at(s_sums[s], idx[r0:r1], dat[r0:r1])
                        s_counts[s] += 1
    hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                                 if s in hk_human}), dtype=int)
    means_all = gene_sums / n_cells
    m = np.ones(n_genes, bool); m[hk_global] = False
    nm = means_all.copy(); nm[~m] = -np.inf
    hvg = np.argsort(nm)[-N_HVG:][::-1]
    keep = np.sort(np.union1d(hk_global, hvg))
    hk_r = np.where(np.isin(keep, hk_global))[0]
    nh_r = np.where(~np.isin(keep, hk_global))[0]
    s_means = s_sums[:, keep] / np.maximum(s_counts, 1)[:, None]
    ok = s_counts > 0
    s_means = s_means[ok]
    s_weights = s_counts[ok].astype(np.float64)
    region_per_code = np.zeros(len(uniq_s), dtype=int)
    region_per_code[samp_code] = samp_region
    s_region = region_per_code[ok]
    s_donor = donor_of_code[ok]
    meds, mlws = [], []
    for d in sorted(set(s_donor.tolist())):
        msk = s_donor != d
        pb = region_pbs(s_region[msk], s_weights[msk], s_means[msk])
        w, lw = pair_stats(pb, hk_r, nh_r)
        meds.append(float(np.median(w))); mlws.append(float(lw.mean()))
        print(f"  drop {d}: median_w={meds[-1]:.2f} mean_logw={mlws[-1]:.3f}",
              flush=True)
    i = df.index[df.supercluster == sc_name][0]
    df.loc[i, "lodo_med_min"] = min(meds)
    df.loc[i, "lodo_med_max"] = max(meds)
    df.loc[i, "lodo_mlogw_min"] = min(mlws)
    df.loc[i, "lodo_mlogw_max"] = max(mlws)
    del s_sums, s_means
    gc.collect()

df.to_csv(OUT, index=False)
print("DONE", flush=True)
