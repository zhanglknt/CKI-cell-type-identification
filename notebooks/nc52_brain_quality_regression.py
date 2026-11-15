# -*- coding: utf-8 -*-
"""
nc52_brain_quality_regression.py — NC v52 C1.

Reviewer (R4 brain atlas): the regional gradient could be driven by RNA
quality / technical confounds rather than biology. The Siletti atlas obs
carries NO PMI or RIN (checked: obs has only ontology / dissection /
donor / roi / sample fields), so we use per-nucleus detected genes and
total UMI counts, aggregated to the (cell class x library) level and to
the (cell class x region) level, as quality proxies (declared).

Two regressions:

1. (class x library)-pair level — the drift-ladder pairs
   (results/nc49_brain_drift_ladder.csv; T1 technical replicates,
   T2 cross-donor, T3 cross-region):
     log10(metric) ~ |dlog detected| + |dlog depth| + dlog n_cells + C(tier)
   fit per metric (k_n, k_f, omega). Reports coefficients, R^2, and
   whether the T3-vs-T1 regional elevation (the ladder's regional
   gradient) survives quality adjustment (tier coefficient before vs
   after adding the quality terms).

2. (class x region)-pair level — the 31,764 observed region pairs
   (results/reviewer_brain_pair_kf_kn.csv):
     log10(omega) ~ |dlog detected| + |dlog depth| + dlog n_cells + C(cell_type)
   then the astrocyte/Bergmann-glia gradient is recomputed from
   quality-adjusted (residualized + class-mean) omegas to test whether
   the 6.10 full-data gradient is explained by quality differences.

Outputs: results/nc52_brain_quality_regression_classlib.csv (both levels,
column `level` distinguishes them).

Seed: none (deterministic OLS).
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "results"
_t0 = time.time()


def log(msg):
    print(f"[{time.time()-_t0:6.0f}s] {msg}", flush=True)


def ols(y, Xdf):
    """OLS with intercept; returns coef series, R2, n."""
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

# ================================================================ level 1: (class, library) pairs
log("=== level 1: (class, library) ladder pairs ===")
lad = pd.read_csv(OUT / "nc49_brain_drift_ladder.csv")
log(f"ladder pairs: {len(lad)}")

q = qlib.rename(columns={"ct": "cell_type"})
qa = q.add_suffix("_a").rename(columns={"cell_type_a": "cell_type",
                                        "sample_a": "sample_a"})
qb = q.add_suffix("_b").rename(columns={"cell_type_b": "cell_type",
                                        "sample_b": "sample_b"})
# note: the ladder CSV already carries per-group n_cells_a/n_cells_b
# (pseudobulk sizes) — use those; merge only the quality proxies.
m = lad.merge(qa[["cell_type", "sample_a", "mean_detected_a",
                  "mean_total_counts_a"]],
              on=["cell_type", "sample_a"], how="left")
m = m.merge(qb[["cell_type", "sample_b", "mean_detected_b",
                "mean_total_counts_b"]],
            on=["cell_type", "sample_b"], how="left")
miss = m["mean_detected_a"].isna().mean()
log(f"unmatched library fraction: {miss:.3%}")

m["dlog_detected"] = np.abs(np.log10(m["mean_detected_a"])
                            - np.log10(m["mean_detected_b"]))
m["dlog_depth"] = np.abs(np.log10(m["mean_total_counts_a"])
                         - np.log10(m["mean_total_counts_b"]))
m["dlog_ncells"] = np.log10(m["n_cells_a"]) - np.log10(m["n_cells_b"])
m["abs_dlog_ncells"] = np.abs(m["dlog_ncells"])

COVS = ["dlog_detected", "dlog_depth", "abs_dlog_ncells"]
tier_d = pd.get_dummies(m["tier"], prefix="tier", drop_first=True).astype(float)

for metric in ["k_n", "k_f", "omega"]:
    y = np.log10(m[metric].replace([np.inf], np.nan))
    ok = y.notna() & m[COVS].notna().all(axis=1)
    # model without quality (tier only) and with quality
    X0 = tier_d[ok]
    X1 = pd.concat([m.loc[ok, COVS].reset_index(drop=True),
                    tier_d[ok].reset_index(drop=True)], axis=1)
    b0, r20, n = ols(y[ok].values, X0)
    b1, r21, _ = ols(y[ok].values, X1)
    t3_key = [c for c in X1.columns if "T3" in c]
    t3_before = float(b0[t3_key[0]]) if t3_key else np.nan
    t3_after = float(b1[t3_key[0]]) if t3_key else np.nan
    rows.append({
        "level": "class_x_library_pair", "metric": metric, "n": n,
        "r2_tier_only": round(r20, 4), "r2_with_quality": round(r21, 4),
        "coef_dlog_detected": round(float(b1["dlog_detected"]), 4),
        "coef_dlog_depth": round(float(b1["dlog_depth"]), 4),
        "coef_abs_dlog_ncells": round(float(b1["abs_dlog_ncells"]), 4),
        "t3_coef_before_quality": round(t3_before, 4),
        "t3_coef_after_quality": round(t3_after, 4),
        "note": "log10(metric) ~ |dlog detected| + |dlog depth| + "
                "|dlog n_cells| + tier dummies; t3 coefficient = regional "
                "(cross-roi) elevation vs T1 technical baseline in log10"})
    log(f"  {metric}: R2 {r20:.3f}->{r21:.3f}; "
        f"T3 coef {t3_before:.3f}->{t3_after:.3f}")

# ================================================================ level 2: (class, region) pairs
log("=== level 2: (class, region) observed pairs ===")
pairs = pd.read_csv(OUT / "reviewer_brain_pair_kf_kn.csv")
qr = qreg.rename(columns={"ct": "cell_type"})
ra = qr.add_suffix("_a").rename(columns={"cell_type_a": "cell_type",
                                         "roi_a": "region_a"})
rb = qr.add_suffix("_b").rename(columns={"cell_type_b": "cell_type",
                                         "roi_b": "region_b"})
p = pairs.merge(ra[["cell_type", "region_a", "mean_detected_a",
                    "mean_total_counts_a", "n_cells_a"]],
                on=["cell_type", "region_a"], how="left")
p = p.merge(rb[["cell_type", "region_b", "mean_detected_b",
                "mean_total_counts_b", "n_cells_b"]],
            on=["cell_type", "region_b"], how="left")
log(f"unmatched region fraction: {p['mean_detected_a'].isna().mean():.3%}")
p["dlog_detected"] = np.abs(np.log10(p["mean_detected_a"])
                            - np.log10(p["mean_detected_b"]))
p["dlog_depth"] = np.abs(np.log10(p["mean_total_counts_a"])
                         - np.log10(p["mean_total_counts_b"]))
p["abs_dlog_ncells"] = np.abs(np.log10(p["n_cells_a"])
                              - np.log10(p["n_cells_b"]))

ct_d = pd.get_dummies(p["cell_type"], prefix="ct", drop_first=True).astype(float)
grad_full = (p.loc[p.cell_type == "Astrocyte", "omega"].mean()
             / p.loc[p.cell_type == "Bergmann glia", "omega"].mean())
log(f"full-data gradient (check): {grad_full:.2f} (published 6.10)")

for metric in ["kn", "kf", "omega"]:  # region-pair CSV uses kn/kf names
    y = np.log10(p[metric].replace([np.inf], np.nan))
    ok = y.notna() & p[COVS].notna().all(axis=1)
    X0 = ct_d[ok]
    X1 = pd.concat([p.loc[ok, COVS].reset_index(drop=True),
                    ct_d[ok].reset_index(drop=True)], axis=1)
    b0, r20, n = ols(y[ok].values, X0)
    b1, r21, _ = ols(y[ok].values, X1)
    # quality-adjusted gradient: residualize log10(metric) on quality
    # terms, re-add class means, recompute class-mean gradient in
    # original scale
    Xq = p.loc[ok, COVS].reset_index(drop=True)
    bq, _, _ = ols(y[ok].values, Xq)
    yhat_q = np.column_stack([np.ones(ok.sum()), Xq.values]) @ bq.values
    resid = y[ok].values - yhat_q
    padj = p.loc[ok, ["cell_type"]].reset_index(drop=True).copy()
    padj["adj"] = resid + np.repeat(bq["intercept"], ok.sum())
    # class mean of adjusted metric in original scale
    cls = padj.groupby("cell_type")["adj"].apply(
        lambda s: float((10 ** s).mean()))
    grad_adj = cls.get("Astrocyte", np.nan) / cls.get("Bergmann glia", np.nan)
    rows.append({
        "level": "class_x_region_pair", "metric": metric, "n": n,
        "r2_class_only": round(r20, 4), "r2_with_quality": round(r21, 4),
        "coef_dlog_detected": round(float(b1["dlog_detected"]), 4),
        "coef_dlog_depth": round(float(b1["dlog_depth"]), 4),
        "coef_abs_dlog_ncells": round(float(b1["abs_dlog_ncells"]), 4),
        "gradient_unadjusted": round(grad_full, 4) if metric == "omega" else "",
        "gradient_quality_adjusted": round(grad_adj, 4) if metric == "omega" else "",
        "note": "log10(metric) ~ quality + class dummies; adjusted gradient "
                "= class-mean 10^resid (+ intercept) after residualizing on "
                "quality covariates"})
    log(f"  {metric}: R2 {r20:.3f}->{r21:.3f}"
        + (f"; gradient {grad_full:.2f} -> {grad_adj:.2f} adjusted"
           if metric == "omega" else ""))

out = pd.DataFrame(rows)
out.to_csv(OUT / "nc52_brain_quality_regression_classlib.csv", index=False)
log(f"saved {OUT/'nc52_brain_quality_regression_classlib.csv'}")
log("DONE")
