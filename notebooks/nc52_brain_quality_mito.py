# -*- coding: utf-8 -*-
"""
nc52_brain_quality_mito.py — NC v52 C1 addendum (R4-brain query).

R4 asked whether the quality regression includes mitochondrial fraction.
The original C1 used only detected genes / total UMI proxies. This script
computes per-nucleus mitochondrial fraction (MT-* gene UMI share) in one
sequential pass over the atlas, aggregates it to (class, library) and
(class, region), and re-runs the two-level quality regressions of
notebooks/nc52_brain_quality_regression.py WITH the mito covariate added.

Caveat (declared, per R4): depth/detection/mito proxies capture
capture-efficiency and composition-shift-type technical variation; they
cannot capture degradation-driven transcript-composition distortion
(PMI/RIN effects), which the atlas metadata does not carry.

Inputs : data/brain/Nonneurons.h5ad, results/nc49_brain_drift_ladder.csv,
         results/reviewer_brain_pair_kf_kn.csv,
         results/nc52_brain_quality_classlib.csv,
         results/nc52_brain_quality_classregion.csv
Outputs: results/nc52_brain_quality_mito_classlib.csv
         results/nc52_brain_quality_mito_classregion.csv
         results/nc52_brain_quality_regression_mito.csv

Seed: none (deterministic).
"""
import sys
import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
H5 = PROJECT_ROOT / "data" / "brain" / "Nonneurons.h5ad"
OUT = PROJECT_ROOT / "results"
_t0 = time.time()


def log(msg):
    print(f"[{time.time()-_t0:6.0f}s] {msg}", flush=True)


f = h5py.File(H5, "r")
X = f["X"]
indptr = X["indptr"][:].astype(np.int64)
N_CELLS = indptr.shape[0] - 1

vg = f["var"]["Gene"]
if isinstance(vg, h5py.Dataset):
    var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
else:
    cats = [x.decode() if isinstance(x, bytes) else str(x) for x in vg["categories"][:]]
    codes = vg["codes"][:]
    var_gene = [cats[c] if c >= 0 else None for c in codes]
N_GENES = len(var_gene)
mt_mask = np.array([bool(s) and s.startswith("MT-") for s in var_gene])
log(f"MT genes: {int(mt_mask.sum())}")


def read_codes(name):
    g = f["obs"][name]
    cats = np.array([x.decode() if isinstance(x, bytes) else str(x)
                     for x in g["categories"][:]], dtype=object)
    return cats, g["codes"][:]


ct_cats, ct_codes = read_codes("supercluster_term")
roi_cats, roi_codes = read_codes("roi")
samp_cats, samp_codes = read_codes("sample_id")
donor_cats, donor_codes = read_codes("donor_id")

log("=== pass: per-cell MT counts + total counts ===")
cell_total = np.zeros(N_CELLS)
cell_mt = np.zeros(N_CELLS)
BATCH = 100_000
for start in range(0, N_CELLS, BATCH):
    end = min(start + BATCH, N_CELLS)
    lo, hi = int(indptr[start]), int(indptr[end])
    data = X["data"][lo:hi].astype(np.float64)
    idx = X["indices"][lo:hi]
    row_nnz = np.diff(indptr[start:end + 1])
    row_id = np.repeat(np.arange(start, end), row_nnz)
    cell_total += np.bincount(row_id, weights=data, minlength=N_CELLS)
    is_mt = mt_mask[idx]
    if is_mt.any():
        cell_mt += np.bincount(row_id[is_mt], weights=data[is_mt],
                               minlength=N_CELLS)
f.close()
with np.errstate(divide="ignore", invalid="ignore"):
    mito_frac = np.where(cell_total > 0, cell_mt / cell_total, np.nan)
log(f"pass done; median mito frac: {np.nanmedian(mito_frac):.4f}")

meta = pd.DataFrame({
    "ct": np.where(ct_codes >= 0, ct_cats[np.clip(ct_codes, 0, None)], None),
    "roi": roi_cats[np.clip(roi_codes, 0, None)],
    "sample": samp_cats[np.clip(samp_codes, 0, None)],
    "donor": donor_cats[np.clip(donor_codes, 0, None)],
    "mito_frac": mito_frac,
})
meta = meta[meta["ct"].notna()].reset_index(drop=True)

mlib = meta.groupby(["ct", "sample"]).agg(
    mean_mito_frac=("mito_frac", "mean")).reset_index()
mreg = meta.groupby(["ct", "roi"]).agg(
    mean_mito_frac=("mito_frac", "mean")).reset_index()
mlib.to_csv(OUT / "nc52_brain_quality_mito_classlib.csv", index=False)
mreg.to_csv(OUT / "nc52_brain_quality_mito_classregion.csv", index=False)

# ================================================================ regressions
def ols(y, Xdf):
    X = np.column_stack([np.ones(len(Xdf)), Xdf.values])
    names = ["intercept"] + list(Xdf.columns)
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return pd.Series(beta, index=names), r2, len(y)


qlib = pd.read_csv(OUT / "nc52_brain_quality_classlib.csv")
qreg = pd.read_csv(OUT / "nc52_brain_quality_classregion.csv")
rows = []
COVS_BASE = ["dlog_detected", "dlog_depth", "abs_dlog_ncells"]
COVS_MITO = COVS_BASE + ["d_mito_frac"]

# ---- level 1: (class, library) ladder pairs
log("=== level 1: (class, library) ladder pairs + mito ===")
lad = pd.read_csv(OUT / "nc49_brain_drift_ladder.csv")
q = qlib.merge(mlib, left_on=["ct", "sample"],
               right_on=["ct", "sample"], how="left")
q = q.rename(columns={"ct": "cell_type"})
qa = q.add_suffix("_a").rename(columns={"cell_type_a": "cell_type"})
qb = q.add_suffix("_b").rename(columns={"cell_type_b": "cell_type"})
m = lad.merge(qa[["cell_type", "sample_a", "mean_detected_a",
                  "mean_total_counts_a", "mean_mito_frac_a"]],
              on=["cell_type", "sample_a"], how="left")
m = m.merge(qb[["cell_type", "sample_b", "mean_detected_b",
                "mean_total_counts_b", "mean_mito_frac_b"]],
            on=["cell_type", "sample_b"], how="left")
m["dlog_detected"] = np.abs(np.log10(m["mean_detected_a"])
                            - np.log10(m["mean_detected_b"]))
m["dlog_depth"] = np.abs(np.log10(m["mean_total_counts_a"])
                         - np.log10(m["mean_total_counts_b"]))
m["abs_dlog_ncells"] = np.abs(np.log10(m["n_cells_a"])
                              - np.log10(m["n_cells_b"]))
m["d_mito_frac"] = np.abs(m["mean_mito_frac_a"] - m["mean_mito_frac_b"])
tier_d = pd.get_dummies(m["tier"], prefix="tier", drop_first=True).astype(float)

for metric in ["k_n", "k_f", "omega"]:
    y = np.log10(m[metric].replace([np.inf], np.nan))
    ok = y.notna() & m[COVS_MITO].notna().all(axis=1)
    X1 = pd.concat([m.loc[ok, COVS_MITO].reset_index(drop=True),
                    tier_d[ok].reset_index(drop=True)], axis=1)
    b1, r21, n = ols(y[ok].values, X1)
    t3_key = [c for c in X1.columns if "T3" in c]
    rows.append({
        "level": "class_x_library_pair", "metric": metric, "n": n,
        "r2_with_quality_mito": round(r21, 4),
        "coef_dlog_detected": round(float(b1["dlog_detected"]), 4),
        "coef_dlog_depth": round(float(b1["dlog_depth"]), 4),
        "coef_abs_dlog_ncells": round(float(b1["abs_dlog_ncells"]), 4),
        "coef_d_mito_frac": round(float(b1["d_mito_frac"]), 4),
        "t3_coef_with_mito": round(float(b1[t3_key[0]]), 4) if t3_key else "",
        "note": "as nc52_brain_quality_regression_classlib.csv + |delta "
                "mito fraction|; reference values without mito: T3 coefs "
                "k_n 0.469, k_f 0.688, omega 0.219"})

# ---- level 2: (class, region) observed pairs
log("=== level 2: (class, region) observed pairs + mito ===")
pairs = pd.read_csv(OUT / "reviewer_brain_pair_kf_kn.csv")
qr = qreg.merge(mreg, on=["ct", "roi"], how="left")
qr = qr.rename(columns={"ct": "cell_type"})
ra = qr.add_suffix("_a").rename(columns={"cell_type_a": "cell_type",
                                         "roi_a": "region_a"})
rb = qr.add_suffix("_b").rename(columns={"cell_type_b": "cell_type",
                                         "roi_b": "region_b"})
p = pairs.merge(ra[["cell_type", "region_a", "mean_detected_a",
                    "mean_total_counts_a", "n_cells_a", "mean_mito_frac_a"]],
                on=["cell_type", "region_a"], how="left")
p = p.merge(rb[["cell_type", "region_b", "mean_detected_b",
                "mean_total_counts_b", "n_cells_b", "mean_mito_frac_b"]],
            on=["cell_type", "region_b"], how="left")
p["dlog_detected"] = np.abs(np.log10(p["mean_detected_a"])
                            - np.log10(p["mean_detected_b"]))
p["dlog_depth"] = np.abs(np.log10(p["mean_total_counts_a"])
                         - np.log10(p["mean_total_counts_b"]))
p["abs_dlog_ncells"] = np.abs(np.log10(p["n_cells_a"])
                              - np.log10(p["n_cells_b"]))
p["d_mito_frac"] = np.abs(p["mean_mito_frac_a"] - p["mean_mito_frac_b"])
ct_d = pd.get_dummies(p["cell_type"], prefix="ct", drop_first=True).astype(float)
grad_full = (p.loc[p.cell_type == "Astrocyte", "omega"].mean()
             / p.loc[p.cell_type == "Bergmann glia", "omega"].mean())

for metric in ["kn", "kf", "omega"]:
    y = np.log10(p[metric].replace([np.inf], np.nan))
    ok = y.notna() & p[COVS_MITO].notna().all(axis=1)
    X1 = pd.concat([p.loc[ok, COVS_MITO].reset_index(drop=True),
                    ct_d[ok].reset_index(drop=True)], axis=1)
    b1, r21, n = ols(y[ok].values, X1)
    Xq = p.loc[ok, COVS_MITO].reset_index(drop=True)
    bq, _, _ = ols(y[ok].values, Xq)
    yhat_q = np.column_stack([np.ones(ok.sum()), Xq.values]) @ bq.values
    resid = y[ok].values - yhat_q
    padj = p.loc[ok, ["cell_type"]].reset_index(drop=True).copy()
    padj["adj"] = resid + np.repeat(bq["intercept"], ok.sum())
    cls = padj.groupby("cell_type")["adj"].apply(
        lambda s: float((10 ** s).mean()))
    grad_adj = cls.get("Astrocyte", np.nan) / cls.get("Bergmann glia", np.nan)
    rows.append({
        "level": "class_x_region_pair", "metric": metric, "n": n,
        "r2_with_quality_mito": round(r21, 4),
        "coef_dlog_detected": round(float(b1["dlog_detected"]), 4),
        "coef_dlog_depth": round(float(b1["dlog_depth"]), 4),
        "coef_abs_dlog_ncells": round(float(b1["abs_dlog_ncells"]), 4),
        "coef_d_mito_frac": round(float(b1["d_mito_frac"]), 4),
        "gradient_unadjusted": round(grad_full, 4) if metric == "omega" else "",
        "gradient_quality_mito_adjusted": round(grad_adj, 4) if metric == "omega" else "",
        "note": "reference without mito: omega R2 0.556, adjusted gradient 6.33"})
    log(f"  {metric}: R2(with mito) {r21:.3f}"
        + (f"; gradient {grad_full:.2f} -> {grad_adj:.2f}" if metric == "omega" else ""))

pd.DataFrame(rows).to_csv(OUT / "nc52_brain_quality_regression_mito.csv",
                          index=False)
log(f"saved {OUT/'nc52_brain_quality_regression_mito.csv'}")
log("DONE")
