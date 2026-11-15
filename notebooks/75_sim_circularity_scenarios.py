# -*- coding: utf-8 -*-
"""
#75 Simulation circularity check: two adversarial scenarios
============================================================
Responds to v40 review P2-1 (E1-M1 / E2-M1): the original ground-truth
simulation defines "neutral drift" on HK genes -- exactly the component CKI
is designed to normalize away -- so the FPR = 0.00 and AUC advantages are
partly tautological. This script adds the two missing adversarial designs
on the SAME background, gene set, metric code path and baseline null as
notebooks/45_groundtruth_simulation.py:

  S1. functional_on_hk   -- the functional module is placed on HK genes
      (200 of them, shifted by 2**delta in group B). CKI's numerator k_f
      excludes HK genes by construction, and the denominator k_n absorbs
      the shift, so omega is expected to MISS this signal while raw
      distances / cosine detect it. This quantifies CKI's blind spot when
      the functional signal lands on housekeeping genes (e.g. cancer HK
      dysregulation, ref [35]).

  S2. neutral_on_nonhk   -- neutral drift is placed on 200 random NON-HK
      genes (shifted by 2**eta in group A), i.e. drift that CKI's
      denominator does NOT normalize away. If the top-200 selection picks
      up the drifted genes, k_f (and omega) inflate -> honest type-I
      error estimate under a drift process CKI is not calibrated for.

All six metrics are reported for every condition (omega, k_f, k_n,
k_total, cosine, kf_over_kt), detection rates are computed against the
same baseline null thresholds (95th percentile, 200 reps, same seeds).

Outputs:
  results/sim_circularity_raw.csv
  results/sim_circularity_summary.csv
  results/sim_circularity_report.txt
"""

import json
import sys, os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from cki.core import js_divergence

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

BACKGROUND_CSV = DATA_DIR / "FACS" / "FACS" / "Marrow-counts.csv"
ANNOT_CSV = DATA_DIR / "annotations_FACS.csv"
BACKGROUND_CT = "B cell"
HK_FILE = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"

RANDOM_SEED = 42
N_HVG = 5000
N_TOP_KF = 200
MODULE_SIZE = 200
N_CELLS_PER_GROUP = 200
N_REPS = 50
N_NULL_REPS = 200
DELTA_GRID = [0.25, 0.5, 1.0, 2.0]     # functional log2 FC (on HK genes)
ETA_GRID = [0.25, 0.5, 1.0]            # neutral log2 FC (on non-HK genes)
NULL_Q = 95.0
MODULE_SEEDS = [42, 137, 2024]

METRIC_COLS = ["omega", "k_f", "k_n", "k_total", "cosine", "kf_over_kt"]

# ---------------------------------------------------------------- load data
t0 = time.time()
print("=" * 64)
print("1. Loading real background: Tabula Muris FACS Marrow (B cell)")
counts_t = pd.read_csv(BACKGROUND_CSV, index_col=0)
gene_names = counts_t.index.astype(str).tolist()
ann = pd.read_csv(ANNOT_CSV, index_col=0)
ann_marrow = ann[ann["tissue"] == "Marrow"]
ct_cells = ann_marrow.index[ann_marrow["cell_ontology_class"] == BACKGROUND_CT]
ct_cells = [c for c in ct_cells if c in counts_t.columns]
X = counts_t[ct_cells].T.to_numpy(dtype=np.float32)
n_cells_total, n_genes = X.shape
print(f"   {n_cells_total} cells x {n_genes} genes ({time.time()-t0:.0f}s)")

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_mouse = set(hk_df["Mouse"].dropna().astype(str))
hk_mask = np.array([g in hk_mouse for g in gene_names])
print(f"   HK genes matched in data: {int(hk_mask.sum())}")

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
n_keep = X.shape[1]
print(f"   Kept gene set: {n_keep} (HK={len(hk_in_keep)}, "
      f"non-HK={len(non_hk_in_keep)})")

# ------------------------------------------------- module pools (fixed seeds)
# S1: functional module drawn from HK genes
hk_module_pools = {}
for _s in MODULE_SEEDS:
    hk_module_pools[_s] = np.sort(
        np.random.RandomState(_s).choice(hk_in_keep, size=500, replace=False))
# S2: neutral drift module drawn from NON-HK genes (disjoint from S1 by
# construction; may overlap the old functional pools -- irrelevant since
# delta is 0 in S2 series)
nh_module_pools = {}
for _s in MODULE_SEEDS:
    nh_module_pools[_s] = np.sort(
        np.random.RandomState(10000 + _s).choice(non_hk_in_keep, size=500,
                                                 replace=False))
print(f"   HK/non-HK module pools ready ({len(MODULE_SEEDS)} seeds, "
      f"first {MODULE_SIZE} used per condition)")


# ---------------------------------------------------------------- helpers
def build_pseudobulk(counts):
    """08d pseudobulk: cell-mean -> /total*1e4 -> log1p."""
    pb = counts.mean(axis=0)
    tot = pb.sum()
    pb = pb / tot * 1e4 if tot > 0 else pb
    return np.log1p(pb).astype(np.float64)


def compute_metrics(pb_a, pb_b):
    """All six metrics, k_f code path identical to 08d pair_omegas."""
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


def simulate_pair(delta=0.0, eta=0.0, rng=None, module_seed=42,
                  module_source="hk"):
    """Resample two cell groups and inject ONE adversarial perturbation.

    module_source='hk'   : delta (functional) applied to HK genes     (S1)
    module_source='nonhk': eta   (neutral)   applied to non-HK genes  (S2)
    """
    rng = rng or np.random.RandomState(0)
    ia = rng.choice(n_cells_total, size=N_CELLS_PER_GROUP, replace=False)
    ib = rng.choice(n_cells_total, size=N_CELLS_PER_GROUP, replace=False)
    A = X[ia].astype(np.float64)
    B = X[ib].astype(np.float64)

    if module_source == "hk":
        mod = hk_module_pools[module_seed][:MODULE_SIZE]
        if delta != 0.0:
            B[:, mod] = np.round(B[:, mod] * (2.0 ** delta))
    else:
        mod = nh_module_pools[module_seed][:MODULE_SIZE]
        if eta != 0.0:
            A[:, mod] = np.round(A[:, mod] * (2.0 ** eta))

    return compute_metrics(build_pseudobulk(A), build_pseudobulk(B))


# ---------------------------------------------------------------- run grid
rows = []

def run_series(series, delta=0.0, eta=0.0, module_seed=42,
               module_source="hk", n_reps=N_REPS):
    print(f"  {series:18s} delta={delta:<5} eta={eta:<5} seed={module_seed} "
          f"src={module_source}")
    for r in range(n_reps):
        m = simulate_pair(delta, eta, rng=np.random.RandomState(1000 + r),
                          module_seed=module_seed, module_source=module_source)
        rows.append({"series": series, "rep": r, "delta": delta, "eta": eta,
                     "module_seed": module_seed, **m})

print("\n2. Running adversarial simulation grid")
t0 = time.time()
# baseline null (same seeds/code as 45 -> identical thresholds)
run_series("baseline", n_reps=N_NULL_REPS)
# S1: functional signal on HK genes
for d in DELTA_GRID:
    for s in MODULE_SEEDS:
        run_series("functional_on_hk", delta=d, module_seed=s,
                   module_source="hk")
# S2: neutral drift on non-HK genes
for e in ETA_GRID:
    for s in MODULE_SEEDS:
        run_series("neutral_on_nonhk", eta=e, module_seed=s,
                   module_source="nonhk")
print(f"   Done: {len(rows)} replicates ({time.time()-t0:.0f}s)")

raw = pd.DataFrame(rows)
raw.to_csv(RESULTS_DIR / "sim_circularity_raw.csv", index=False)

# ---------------------------------------------------------------- analysis
print("\n3. Analysis")
base = raw[raw["series"] == "baseline"]
thresholds = {m: float(np.nanpercentile(base[m], NULL_Q)) for m in METRIC_COLS}
print("   Null thresholds (95th pct):",
      {k: round(v, 5) for k, v in thresholds.items()})

def exceed_rate(df):
    return {m: round(float((df[m] > thresholds[m]).mean()), 3)
            for m in METRIC_COLS}

report = {"null_thresholds": thresholds, "n_baseline": len(base),
          "seed": RANDOM_SEED,
          "background": f"Tabula Muris FACS Marrow ({BACKGROUND_CT})",
          "module_size": MODULE_SIZE,
          "n_cells_per_group": N_CELLS_PER_GROUP, "n_reps": N_REPS}

# S1: detection of functional-on-HK signal (expect omega ~ type-I level,
# raw metrics high -> quantifies the blind spot)
s1 = {}
for d in DELTA_GRID:
    sub = raw[(raw["series"] == "functional_on_hk") & (raw["delta"] == d)]
    s1[str(d)] = {"rates": exceed_rate(sub),
                  "means": {m: round(float(sub[m].mean()), 5)
                            for m in METRIC_COLS},
                  "by_seed": {str(s): exceed_rate(sub[sub["module_seed"] == s])
                              for s in MODULE_SEEDS}}
report["S1_functional_on_hk_detection"] = s1

# S2: type-I error under non-HK neutral drift (expect omega possibly
# inflated -> honest specificity estimate outside the calibration design)
s2 = {}
for e in ETA_GRID:
    sub = raw[(raw["series"] == "neutral_on_nonhk") & (raw["eta"] == e)]
    s2[str(e)] = {"rates": exceed_rate(sub),
                  "means": {m: round(float(sub[m].mean()), 5)
                            for m in METRIC_COLS},
                  "by_seed": {str(s): exceed_rate(sub[sub["module_seed"] == s])
                              for s in MODULE_SEEDS}}
report["S2_neutral_on_nonhk_typeI"] = s2

with open(RESULTS_DIR / "sim_circularity_summary.json", "w") as f:
    json.dump(report, f, indent=2)

# summary CSV
summ_rows = []
for (series, d, e, mseed), g in raw.groupby(["series", "delta", "eta",
                                              "module_seed"]):
    row = {"series": series, "delta": d, "eta": e, "module_seed": mseed,
           "n": len(g)}
    for m in METRIC_COLS:
        row[f"{m}_mean"] = round(float(g[m].mean()), 5)
        row[f"{m}_sd"] = round(float(g[m].std()), 5)
        row[f"{m}_rate"] = round(float((g[m] > thresholds[m]).mean()), 3)
    summ_rows.append(row)
pd.DataFrame(summ_rows).to_csv(
    RESULTS_DIR / "sim_circularity_summary.csv", index=False)

# txt report
lines = ["Simulation circularity check: adversarial scenarios (v40 P2-1)",
         "=" * 64,
         "Design: same background/gene set/metric code/baseline null as #45.",
         "S1 functional-on-HK: functional module on HK genes (CKI blind spot)",
         "S2 neutral-on-nonHK: neutral drift on non-HK genes (outside the",
         "   HK-anchored calibration)", "",
         f"Null thresholds (95th pct, n={len(base)}):",
         "  " + ", ".join(f"{m}={v:.5g}" for m, v in thresholds.items()), "",
         "S1. Detection of functional-on-HK signal (rate > null 95th pct):",
         "  (omega expected ~0.05 if CKI is blind to HK-located signal;",
         "   k_total/cosine expected high -> the blind spot is quantified)"]
for d in DELTA_GRID:
    r = s1[str(d)]["rates"]
    lines.append(f"  delta={d:<5} " + " ".join(f"{m}={r[m]:.3f}"
                                              for m in METRIC_COLS))
lines += ["", "S2. Type-I error under neutral-on-nonHK drift:"]
for e in ETA_GRID:
    r = s2[str(e)]["rates"]
    lines.append(f"  eta={e:<5} " + " ".join(f"{m}={r[m]:.3f}"
                                             for m in METRIC_COLS))
lines += ["", "Per-seed spread (omega):",
          "  S1: " + "; ".join(
              f"delta={d}: " + "/".join(f"{s1[str(d)]['by_seed'][str(s)]['omega']:.2f}"
                                        for s in MODULE_SEEDS)
              for d in DELTA_GRID),
          "  S2: " + "; ".join(
              f"eta={e}: " + "/".join(f"{s2[str(e)]['by_seed'][str(s)]['omega']:.2f}"
                                      for s in MODULE_SEEDS)
              for e in ETA_GRID)]
(RESULTS_DIR / "sim_circularity_report.txt").write_text(
    "\n".join(lines), encoding="utf-8")

print("\n" + "\n".join(lines))
print(f"\nOutputs written to {RESULTS_DIR / 'sim_circularity_*'}")
