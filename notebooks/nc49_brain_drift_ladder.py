# -*- coding: utf-8 -*-
"""
nc49_brain_drift_ladder.py — Brain four-tier neutral-drift ladder (NC v49 对策 C 主分析).

Data: Siletti et al. 2023 non-neuronal nuclei (Nonneurons.h5ad, 888,263 nuclei
x 59,480 genes; 606 10x libraries nested in (roi, donor); 4 donors; 106 ROIs;
10 non-neuronal superclusters).

Design — all comparisons at LIBRARY-PAIR level within a cell type (groups =
(ct, library) with >= MIN_CELLS nuclei):
  T1 techrep   : same (roi, donor), different libraries   -> pure technical
                 drift; ground truth = NO functional difference. All pairs.
  T2 cross-don : same roi, different donors               -> donor drift
                 (technical + inter-individual). Capped sample per CT.
  T3 cross-roi : same donor, different rois               -> regional biology
                 (positive control; all metrics should rise). Capped per CT.
Per-pair n-matched null (B draws): pool the two libraries' nuclei, shuffle,
split into disjoint subsets of the observed sizes (na, nb). Calibration
cal = observed / null_median; FPR element = observed > own null p95.

Metrics (pb = sum -> normalize_total(1e4) -> log1p; HRT Atlas HK; per-pair
top-200 |dpb| non-HK hybrid for k_f):
  k_n, k_f, omega (kn_floor=0), raw JS (reduced gene set), cosine dist,
  Spearman dist (1 - rho), marker Jaccard dist (top-200 markers of each
  library vs cell-weighted background of all OTHER cell types; 1 - Jaccard).

Passes over the 4.4 GB file:
  pass 0 (sequential): global + per-CT gene sums -> HVG selection (top-5000
         non-HK by mean, 08d convention) -> keep_global (~6k genes).
  pass 1 (sequential): per-GROUP gene sums on keep_global -> group pbs,
         per-CT backgrounds, marker sets.
  pass 2 (per CT, backed random access): extract CT CSR, compute observed +
         null metrics for that CT's T1/T2/T3 pairs.

Outputs:
  results/nc49_brain_drift_ladder.csv  (long: one row per pair, all metrics +
        null summaries)
  results/audit/_nc49_brain_ladder_stdout.log

Run (workbuddy env; system Python312 h5py DLL is broken):
  C:/Users/KnightZ/.workbuddy/binaries/python/envs/default/Scripts/python.exe
      -u notebooks/nc49_brain_drift_ladder.py
"""
import gc
import json
import sys
import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from cki.core import js_divergence  # noqa: E402

H5 = PROJECT_ROOT / "data" / "brain" / "Nonneurons.h5ad"
HK_FILE = PROJECT_ROOT / "cki" / "data" / "hrt_atlas.csv"
OUT = PROJECT_ROOT / "results"
LOG = OUT / "audit" / "_nc49_brain_ladder_stdout.log"

CT_COL = "supercluster_term"
ROI_COL = "roi"
SAMPLE_COL = "sample_id"
DONOR_COL = "donor_id"

MIN_CELLS = 20
N_HVG = 5000
N_TOP_KF = 200
N_TOP_MARKERS = 200
B_T1 = 100
B_T23 = 30
CAP_T2_PER_CT = 200
CAP_T3_PER_CT = 200
SEED = 42

METRICS = ["k_n", "k_f", "omega", "raw_js", "cosine", "spearman", "marker_jaccard"]

_t0 = time.time()


def log(msg):
    line = f"[{time.time()-_t0:7.0f}s] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ================================================================ pass 0
log("=== pass 0: global + per-CT gene sums (sequential) ===")
hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))

f = h5py.File(H5, "r")
X = f["X"]
indptr = X["indptr"][:]
N_CELLS = indptr.shape[0] - 1

# var gene symbols (08d logic)
var_gene = None
if "Gene" in f["var"]:
    vg = f["var"]["Gene"]
    if isinstance(vg, h5py.Dataset):
        var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
    elif isinstance(vg, h5py.Group) and "categories" in vg:
        cats = [x.decode() if isinstance(x, bytes) else str(x) for x in vg["categories"][:]]
        codes = vg["codes"][:]
        var_gene = [cats[c] if c >= 0 else None for c in codes]
if var_gene is None:
    idx_name = f["var"].attrs.get("_index", None)
    vg = f["var"][idx_name]
    var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
N_GENES = len(var_gene)
log(f"shape: ({N_CELLS}, {N_GENES})")


def read_codes(name):
    g = f["obs"][name]
    cats = [x.decode() if isinstance(x, bytes) else str(x) for x in g["categories"][:]]
    codes = g["codes"][:]
    return np.array(cats, dtype=object), codes


ct_cats, ct_codes = read_codes(CT_COL)
roi_cats, roi_codes = read_codes(ROI_COL)
samp_cats, samp_codes = read_codes(SAMPLE_COL)
donor_cats, donor_codes = read_codes(DONOR_COL)
ct_names = np.where(ct_codes >= 0, ct_cats[ct_codes], None)
roi_names = np.where(roi_codes >= 0, roi_cats[roi_codes], None)
donor_names = np.where(donor_codes >= 0, donor_cats[donor_codes], None)
CTS = sorted(set(c for c in ct_names if c is not None))
ct_idx = {c: i for i, c in enumerate(CTS)}
ct_of_cell = np.array([ct_idx[c] if c is not None else -1 for c in ct_names])

hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                             if s and s in hk_human}), dtype=int)
log(f"HK genes matched: {len(hk_global)}")

# sequential pass: global + per-CT sums (bincount-vectorized)
gene_sums = np.zeros(N_GENES)
ct_sums = np.zeros((len(CTS), N_GENES))
ct_counts = np.zeros(len(CTS), dtype=np.int64)
BATCH = 100_000
for start in range(0, N_CELLS, BATCH):
    end = min(start + BATCH, N_CELLS)
    lo, hi = int(indptr[start]), int(indptr[end])
    data = X["data"][lo:hi].astype(np.float64)
    idx = X["indices"][lo:hi]
    gene_sums += np.bincount(idx, weights=data, minlength=N_GENES)
    row_ct = ct_of_cell[start:end]
    row_nnz = np.diff(indptr[start:end + 1])
    row_id = np.repeat(np.arange(end - start), row_nnz)
    ct_of_entry = row_ct[row_id]
    ok = ct_of_entry >= 0
    flat = ct_of_entry[ok].astype(np.int64) * N_GENES + idx[ok]
    ct_sums += np.bincount(flat, weights=data[ok],
                           minlength=len(CTS) * N_GENES).reshape(len(CTS), N_GENES)
    ct_counts += np.bincount(row_ct[row_ct >= 0], minlength=len(CTS))
gene_means = gene_sums / N_CELLS
log(f"pass 0 done; CT sizes: {dict(zip(CTS, ct_counts.tolist()))}")

# HVG selection (08d convention): top-5000 non-HK by mean expression
non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_global] = False
non_hk_means = gene_means.copy()
non_hk_means[~non_hk_mask] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
keep_global = np.sort(np.union1d(hk_global, hvg_global))
is_hk_keep = np.isin(keep_global, hk_global)
hk_loc = np.where(is_hk_keep)[0]
nonhk_loc = np.where(~is_hk_keep)[0]
gene_map = np.full(N_GENES, -1, dtype=np.int32)
gene_map[keep_global] = np.arange(len(keep_global), dtype=np.int32)
log(f"reduced set: {len(keep_global)} genes (HK={len(hk_loc)}, HVG={len(nonhk_loc)})")

# ================================================================ groups
log("=== building groups ===")
meta_df = pd.DataFrame({
    "ct": ct_names, "roi": roi_names, "sample": samp_codes,
    "donor": donor_names,
})
groups = meta_df.groupby(["ct", "sample"], sort=True).indices  # positions
group_info = []
for (ct, samp), pos in groups.items():
    n = len(pos)
    if n < MIN_CELLS or ct is None:
        continue
    group_info.append({
        "ct": ct, "sample": int(samp),
        "sample_name": samp_cats[samp],
        "roi": roi_names[pos[0]], "donor": donor_names[pos[0]],
        "cells": np.sort(pos), "n": int(n),
    })
gdf = pd.DataFrame([{k: v for k, v in g.items() if k != "cells"} for g in group_info])
log(f"valid groups (>= {MIN_CELLS} cells): {len(gdf)}")
log(f"T1 potential pairs: "
    f"{int(sum(k*(k-1)//2 for k in gdf.groupby(['ct','roi','donor']).size() if k >= 2))}")

# ================================================================ pass 1
log("=== pass 1: per-group sums on reduced genes (sequential) ===")
n_keep = len(keep_global)
gsums = np.zeros((len(group_info), n_keep))
gpos_of_cell = np.full(N_CELLS, -1, dtype=np.int32)
for gi, g in enumerate(group_info):
    gpos_of_cell[g["cells"]] = gi
for start in range(0, N_CELLS, BATCH):
    end = min(start + BATCH, N_CELLS)
    lo, hi = int(indptr[start]), int(indptr[end])
    idx = X["indices"][lo:hi]
    data = X["data"][lo:hi].astype(np.float64)
    mapped = gene_map[idx]
    keep = mapped >= 0
    row_nnz = np.diff(indptr[start:end + 1])
    row_id = np.repeat(np.arange(start, end), row_nnz)
    g_of_entry = gpos_of_cell[row_id]
    sel = keep & (g_of_entry >= 0)
    flat = g_of_entry[sel].astype(np.int64) * n_keep + mapped[sel]
    gsums += np.bincount(flat, weights=data[sel],
                         minlength=len(group_info) * n_keep).reshape(
                             len(group_info), n_keep)
log("pass 1 done")

# group pbs (mean -> normalize 1e4 -> log1p; mean==sum after normalization)
gm = gsums / gdf["n"].values[:, None]
gtot = gm.sum(axis=1, keepdims=True)
gtot[gtot == 0] = 1.0
pb_raw = gm / gtot * 1e4
pb = np.log1p(pb_raw)
gdf["pb"] = list(pb)  # dense rows

# per-CT background (cell-weighted mean of OTHER CTs) + bg pb
ct_tot = {c: ct_counts[ct_idx[c]] for c in CTS}
bg_pb = {}
for c in CTS:
    others = [i for i in range(len(group_info)) if group_info[i]["ct"] != c]
    w = gdf["n"].values[others]
    bg_mean = (gm[others] * w[:, None]).sum(axis=0) / w.sum()
    tot = bg_mean.sum()
    v = bg_mean / tot * 1e4 if tot > 0 else bg_mean
    bg_pb[c] = np.log1p(v)

# marker sets per group: top-N_TOP_MARKERS by (pb - bg_pb) over reduced genes
for gi, g in enumerate(group_info):
    d = pb[gi] - bg_pb[g["ct"]]
    g["markers"] = set(np.argpartition(-d, -N_TOP_MARKERS)[-N_TOP_MARKERS:].tolist())
log("marker sets computed")


# ================================================================ metrics
def pair_metrics(pb_a, pb_b, markers_a=None, markers_b=None):
    k_n = js_divergence(pb_a[hk_loc], pb_b[hk_loc])
    diff = np.abs(pb_a - pb_b)
    ad = diff[nonhk_loc]
    top_n = min(N_TOP_KF, len(ad))
    top_local = np.argpartition(ad, -top_n)[-top_n:]
    k_f = js_divergence(pb_a[nonhk_loc[top_local]], pb_b[nonhk_loc[top_local]])
    omega = k_f / k_n if k_n > 1e-15 else np.inf
    raw = js_divergence(pb_a, pb_b)
    na_, nb_ = np.linalg.norm(pb_a), np.linalg.norm(pb_b)
    cos = 1.0 - float(pb_a @ pb_b / (na_ * nb_))
    rho = spearmanr(pb_a, pb_b)[0]
    spear = 1.0 - float(rho) if np.isfinite(rho) else 1.0
    out = {"k_n": k_n, "k_f": k_f, "omega": omega, "raw_js": raw,
           "cosine": cos, "spearman": spear}
    if markers_a is not None:
        inter = len(markers_a & markers_b)
        union = len(markers_a | markers_b)
        out["marker_jaccard"] = 1.0 - inter / union if union else 1.0
    return out


def null_metrics(pool_csr, na, nb, bg, n_draws, rng):
    """Cell-level n-matched null: shuffle pooled rows, split (na, nb)."""
    out = []
    n_pool = pool_csr.shape[0]
    for _ in range(n_draws):
        pm = rng.permutation(n_pool)
        pa = _pb_of(pool_csr[pm[:na]])
        pbn = _pb_of(pool_csr[pm[na:na + nb]])
        # marker sets of null groups vs bg
        ma = set(np.argpartition(-(pa - bg), -N_TOP_MARKERS)[-N_TOP_MARKERS:].tolist())
        mb = set(np.argpartition(-(pbn - bg), -N_TOP_MARKERS)[-N_TOP_MARKERS:].tolist())
        out.append(pair_metrics(pa, pbn, ma, mb))
    return out


def _pb_of(csr_rows):
    v = np.asarray(csr_rows.sum(axis=0)).ravel().astype(float)
    tot = v.sum()
    if tot > 0:
        v = v / tot * 1e4
    return np.log1p(v)


# ================================================================ pairs
rng = np.random.default_rng(SEED)
pairs = []  # (tier, gi_a, gi_b)
for ct in CTS:
    sub = gdf[gdf["ct"] == ct]
    idxs = {int(i): gi for gi, i in zip(sub.index, sub.index)}
    # T1: same (roi, donor), different libraries — all pairs
    for _, h in sub.groupby(["roi", "donor"]):
        gis = list(h.index)
        if len(gis) >= 2:
            for i in range(len(gis)):
                for j in range(i + 1, len(gis)):
                    pairs.append(("T1_techrep", int(gis[i]), int(gis[j])))
    # T2: same roi, different donors — capped
    t2 = []
    for _, h in sub.groupby("roi"):
        for i in range(len(h)):
            for j in range(i + 1, len(h)):
                if h.iloc[i]["donor"] != h.iloc[j]["donor"]:
                    t2.append((int(h.index[i]), int(h.index[j])))
    if len(t2) > CAP_T2_PER_CT:
        t2 = [t2[i] for i in rng.choice(len(t2), CAP_T2_PER_CT, replace=False)]
    pairs.extend(("T2_cross_donor", a, b) for a, b in t2)
    # T3: same donor, different roi — capped
    t3 = []
    for _, h in sub.groupby("donor"):
        for i in range(len(h)):
            for j in range(i + 1, len(h)):
                if h.iloc[i]["roi"] != h.iloc[j]["roi"]:
                    t3.append((int(h.index[i]), int(h.index[j])))
    if len(t3) > CAP_T3_PER_CT:
        t3 = [t3[i] for i in rng.choice(len(t3), CAP_T3_PER_CT, replace=False)]
    pairs.extend(("T3_cross_roi", a, b) for a, b in t3)
pairs_df = pd.DataFrame(pairs, columns=["tier", "gi_a", "gi_b"])
log(f"total pairs: {len(pairs_df)}; per tier: {pairs_df['tier'].value_counts().to_dict()}")

# ================================================================ pass 2
log("=== pass 2: per-CT extraction + observed & null metrics ===")


def extract_ct_csr(cell_indices):
    """Extract CSR (cells x keep genes) for sorted cell indices (08d style)."""
    order = np.argsort(cell_indices, kind="stable")
    sorted_cells = cell_indices[order]
    unsort = np.empty(len(cell_indices), dtype=np.int64)
    unsort[order] = np.arange(len(cell_indices))
    new_data = [None] * len(cell_indices)
    new_idx = [None] * len(cell_indices)
    nnz_sorted = np.zeros(len(cell_indices), dtype=np.int64)
    CH = 20000
    n_ch = (len(cell_indices) + CH - 1) // CH
    for c in range(n_ch):
        cs, ce = c * CH, min((c + 1) * CH, len(cell_indices))
        cc = sorted_cells[cs:ce]
        d0, d1 = int(indptr[cc[0]]), int(indptr[cc[-1] + 1])
        if d1 > d0:
            ch_idx = X["indices"][d0:d1]
            ch_dat = X["data"][d0:d1]
            ch_map = gene_map[ch_idx]
            ch_keep = ch_map >= 0
        else:
            ch_map = np.array([], dtype=np.int32)
            ch_keep = np.array([], dtype=bool)
            ch_dat = np.array([], dtype=X["data"].dtype)
        for ci in range(cs, ce):
            op = int(order[ci])
            r0 = int(indptr[sorted_cells[ci]]) - d0
            r1 = int(indptr[sorted_cells[ci] + 1]) - d0
            if r1 == r0:
                continue
            km = ch_keep[r0:r1]
            nk = int(km.sum())
            nnz_sorted[ci] = nk
            if nk:
                new_data[op] = ch_dat[r0:r1][km]
                new_idx[op] = ch_map[r0:r1][km]
    nnz_orig = np.zeros(len(cell_indices), dtype=np.int64)
    nnz_orig[order] = nnz_sorted
    new_indptr = np.zeros(len(cell_indices) + 1, dtype=np.int64)
    np.cumsum(nnz_orig, out=new_indptr[1:])
    nnz = int(new_indptr[-1])
    if nnz == 0:
        return sp.csr_matrix((len(cell_indices), n_keep))
    data = np.concatenate([d for d in new_data if d is not None]).astype(np.float64)
    indices = np.concatenate([d for d in new_idx if d is not None])
    return sp.csr_matrix((data, indices, new_indptr), shape=(len(cell_indices), n_keep))


rows = []
for ct in CTS:
    ct_groups = [gi for gi, g in enumerate(group_info) if g["ct"] == ct]
    ct_pair_rows = pairs_df[
        pairs_df["gi_a"].isin(ct_groups) & pairs_df["gi_b"].isin(ct_groups)]
    if len(ct_pair_rows) == 0:
        continue
    t_ct = time.time()
    cells = np.sort(np.concatenate([group_info[gi]["cells"] for gi in ct_groups]))
    X_ct = extract_ct_csr(cells)
    # map group -> row range in X_ct (cells sorted, group cells are sorted too)
    pos_in_ct = {int(c): i for i, c in enumerate(cells)}
    row_ranges = {}
    for gi in ct_groups:
        pos = np.searchsorted(cells, group_info[gi]["cells"])
        row_ranges[gi] = pos
    log(f"  [{ct}] extracted {X_ct.shape[0]} cells ({X_ct.nnz/1e6:.0f}M nnz, "
        f"{time.time()-t_ct:.0f}s); pairs: {len(ct_pair_rows)}")
    bg = bg_pb[ct]
    for tier, gia, gib in ct_pair_rows.itertuples(index=False):
        ga, gb = group_info[gia], group_info[gib]
        ra, rb = row_ranges[gia], row_ranges[gib]
        obs = pair_metrics(pb[gia], pb[gib], ga["markers"], gb["markers"])
        B = B_T1 if tier == "T1_techrep" else B_T23
        pool = sp.vstack([X_ct[ra], X_ct[rb]]).tocsr()
        nulls = null_metrics(pool, len(ra), len(rb), bg, B, rng)
        rec = {
            "tier": tier, "cell_type": ct,
            "sample_a": ga["sample_name"], "sample_b": gb["sample_name"],
            "roi_a": ga["roi"], "roi_b": gb["roi"],
            "donor_a": ga["donor"], "donor_b": gb["donor"],
            "n_cells_a": ga["n"], "n_cells_b": gb["n"], "B": B,
        }
        rec.update(obs)
        for met in METRICS:
            nv = np.array([x[met] for x in nulls], dtype=float)
            nv = nv[np.isfinite(nv)]
            rec[f"null_med_{met}"] = float(np.median(nv)) if len(nv) else np.nan
            rec[f"null_p95_{met}"] = float(np.percentile(nv, 95)) if len(nv) else np.nan
            nm = rec[f"null_med_{met}"]
            rec[f"cal_{met}"] = obs[met] / nm if (nm and np.isfinite(nm) and nm > 0) else np.nan
            p95 = rec[f"null_p95_{met}"]
            rec[f"exceed_{met}"] = int(np.isfinite(p95) and obs[met] > p95)
        rows.append(rec)
    del X_ct, pool
    gc.collect()
    log(f"  [{ct}] done in {time.time()-t_ct:.0f}s ({len(rows)} pair rows so far)")

f.close()

# ================================================================ save
df = pd.DataFrame(rows)
out_csv = OUT / "nc49_brain_drift_ladder.csv"
df.to_csv(out_csv, index=False)
log(f"saved {out_csv} ({len(df)} rows)")

# quick summary
log("\n=== summary: median cal [IQR] and FPR by tier x metric ===")
for tier in ["T1_techrep", "T2_cross_donor", "T3_cross_roi"]:
    sub = df[df.tier == tier]
    if len(sub) == 0:
        continue
    log(f"--- {tier} (n={len(sub)}) ---")
    for met in METRICS:
        cv = sub[f"cal_{met}"]
        fpr = sub[f"exceed_{met}"].mean()
        log(f"  {met:<16} obs_med={sub[met].median():>9.4g} "
            f"cal_med={cv.median():>7.3f} [{cv.quantile(.25):.3f},{cv.quantile(.75):.3f}] "
            f"FPR={fpr:.1%}")
with open(OUT / "audit" / "_nc49_brain_ladder_summary.txt", "w", encoding="utf-8") as sf:
    sf.write("summary placeholder — see stdout log\n")
log("DONE")
