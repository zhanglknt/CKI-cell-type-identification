"""
#45 Ground-Truth Simulation Injection Experiment
=================================================
Responds to v37 review consensus Critical (R1-C4 / R2-C1 / R3-C2 / R4-C1):
no synthetic-data validation of the omega metric.

Design: semi-synthetic injection on a REAL single-cell background
(Tabula Muris FACS Marrow counts). Two groups of cells are resampled from
the same tissue (ground-truth functional divergence = 0), then known
perturbations are injected:

  - Functional signal (delta): a fixed module of 200 non-HK genes in
    group B is multiplicatively shifted by 2**delta (log2 fold change).
  - Neutral HK drift (eta): housekeeping genes in group A are shifted by
    2**eta -- a pure "neutral" perturbation that should NOT count as
    functional divergence.
  - Global overdispersion (eps): extra Poisson noise on all genes in
    group A (technical batch noise).
  - Dropout / depth / cell-count imbalance robustness scenarios.

Metrics computed per replicate (identical code path to the manuscript
brain pipeline, notebooks/08d_brain_blockshuffle_null.py::pair_omegas):

  omega      = k_f / k_n   (manuscript hybrid scheme, per-pair top-200 DE)
  k_f        = JS(pseudobulk A, B restricted to per-pair top-200 |A-B| non-HK genes)
  k_n        = JS(pseudobulk A, B restricted to HK genes)
  k_total    = JS(pseudobulk A, B over the full kept gene set)  (raw JS)
  cosine     = 1 - cosine similarity of pseudobulks
  kf_over_kt = k_f / k_total (reviewer-suggested simple ratio baseline)

Outputs:
  results/groundtruth_simulation_raw.csv      (one row per replicate)
  results/groundtruth_simulation_summary.csv  (per condition x metric)
  results/groundtruth_simulation_metrics.json (monotonicity, type-I error,
                                               power, AUC, bias/variance)
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from cki.core import js_divergence

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

BACKGROUND_CSV = DATA_DIR / "FACS" / "FACS" / "Marrow-counts.csv"
ANNOT_CSV = DATA_DIR / "annotations_FACS.csv"
BACKGROUND_CT = "B cell"   # single cell type -> matches the manuscript's
#                          per-cell-type usage (08d analyses one CT at a time);
#                          removes composition noise so the null reflects
#                          pure cell-resampling noise, as in the brain pipeline
HK_FILE = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"

RANDOM_SEED = 42
N_HVG = 5000          # non-HK genes kept, selected by global mean (as in 08d)
N_TOP_KF = 200        # per-pair top-|A-B| genes for k_f (as in 08d)
MODULE_SIZE = 200     # injected functional module size
N_CELLS_PER_GROUP = 200
N_REPS = 50           # replicates per condition
N_NULL_REPS = 200      # replicates for null threshold calibration
DELTA_GRID = [0.125, 0.25, 0.5, 1.0, 2.0]      # functional log2 FC
ETA_GRID = [0.25, 0.5, 1.0]                    # neutral HK drift log2 FC
EPS_GRID = [0.3, 1.0]                          # global overdispersion
NULL_Q = 95.0                                  # percentile threshold

# ---------------------------------------------------------------- load data
t0 = time.time()
print("=" * 64)
print("1. Loading real background: Tabula Muris FACS Marrow")
print("   (this may take 1-2 minutes for the 270 MB CSV)")
counts_t = pd.read_csv(BACKGROUND_CSV, index_col=0)  # genes x cells
gene_names = counts_t.index.astype(str).tolist()
ann = pd.read_csv(ANNOT_CSV, index_col=0)
ann_marrow = ann[ann["tissue"] == "Marrow"]
ct_cells = ann_marrow.index[ann_marrow["cell_ontology_class"] == BACKGROUND_CT]
ct_cells = [c for c in ct_cells if c in counts_t.columns]
print(f"   Background cell type '{BACKGROUND_CT}': {len(ct_cells)} cells")
X = counts_t[ct_cells].T.to_numpy(dtype=np.float32)  # cells x genes
n_cells_total, n_genes = X.shape
print(f"   Loaded: {n_cells_total} cells x {n_genes} genes "
      f"({time.time() - t0:.0f}s)")

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_mouse = set(hk_df["Mouse"].dropna().astype(str))
hk_mask = np.array([g in hk_mouse for g in gene_names])
print(f"   HK genes matched in data: {int(hk_mask.sum())}")

# ------------------------------------------------- gene set (as in 08d)
# keep = HK genes  U  top-N_HVG non-HK genes by global mean
gene_means = X.mean(axis=0)
non_hk_means = np.where(hk_mask, -np.inf, gene_means)
hvg_idx = np.argsort(non_hk_means)[-N_HVG:]
keep_mask = hk_mask.copy()
keep_mask[hvg_idx] = True
keep_idx = np.where(keep_mask)[0]
keep_idx = keep_idx[gene_means[keep_idx] > 0]        # drop all-zero genes
X = X[:, keep_idx]
kept_names = [gene_names[i] for i in keep_idx]
kept_hk = hk_mask[keep_idx]
hk_in_keep = np.where(kept_hk)[0]
non_hk_in_keep = np.where(~kept_hk)[0]
n_keep = X.shape[1]
print(f"   Kept gene set: {n_keep} (HK={len(hk_in_keep)}, "
      f"non-HK={len(non_hk_in_keep)})")

# ------------------------------------------- fixed functional module (seed 42)
rng = np.random.RandomState(RANDOM_SEED)
# fixed functional module pools (seeds below); module-size sensitivity uses
# the first m genes of the seed-42 pool so conditions stay comparable
MODULE_SEEDS = [42, 137, 2024]
module_pools = {}
for _s in MODULE_SEEDS:
    module_pools[_s] = np.sort(
        np.random.RandomState(_s).choice(non_hk_in_keep, size=500,
                                          replace=False))
module_local = module_pools[42][:MODULE_SIZE]
print(f"   Functional module: {MODULE_SIZE} non-HK genes "
      f"({len(MODULE_SEEDS)} random seeds: {MODULE_SEEDS})")


# ---------------------------------------------------------------- injection
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
    return {
        "omega": omega, "k_f": kf, "k_n": kn, "k_total": kt,
        "cosine": cosine, "kf_over_kt": kf_over_kt,
    }


def simulate_pair(delta=0.0, eta=0.0, eps=0.0, dropout=0.0, depth=1.0,
                  n_b=None, rng=None, module_size=None, module_seed=42):
    """Resample two cell groups from the real background and inject."""
    rng = rng or np.random.RandomState(0)
    n_a = N_CELLS_PER_GROUP
    n_b = n_b or N_CELLS_PER_GROUP
    ia = rng.choice(n_cells_total, size=n_a, replace=False)
    ib = rng.choice(n_cells_total, size=n_b, replace=False)
    A = X[ia].astype(np.float64)
    B = X[ib].astype(np.float64)
    pool = module_pools[module_seed]
    mod = pool[:module_size] if module_size else pool[:MODULE_SIZE]

    # neutral HK drift on group A (hits k_n only)
    if eta != 0.0:
        A[:, hk_in_keep] = np.round(A[:, hk_in_keep] * (2.0 ** eta))
    # global overdispersion (extra Poisson noise) on group A
    if eps != 0.0:
        A = A + rng.poisson(A * eps).astype(np.float64)
    # functional module shift on group B
    if delta != 0.0:
        B[:, mod] = np.round(B[:, mod] * (2.0 ** delta))
    # dropout on group B
    if dropout > 0.0:
        drop = rng.random((B.shape[0], n_keep)) < dropout
        B[drop] = 0.0
    # sequencing depth on group B
    if depth != 1.0:
        B = np.round(B * depth)

    return compute_metrics(build_pseudobulk(A), build_pseudobulk(B))


METRIC_COLS = ["omega", "k_f", "k_n", "k_total", "cosine", "kf_over_kt"]

# ---------------------------------------------------------------- run grid
rows = []


def run_series(series, delta=0.0, eta=0.0, eps=0.0, dropout=0.0,
               depth=1.0, n_b=None, n_reps=N_REPS, module_size=None,
               module_seed=42):
    print(f"  {series:24s} delta={delta:<5} eta={eta:<5} eps={eps:<4} "
          f"dropout={dropout:<4} depth={depth:<4} nB={n_b or N_CELLS_PER_GROUP}"
          f" m={module_size or MODULE_SIZE} seed={module_seed}")
    for r in range(n_reps):
        m = simulate_pair(delta, eta, eps, dropout, depth, n_b,
                          rng=np.random.RandomState(1000 + r),
                          module_size=module_size, module_seed=module_seed)
        rows.append({"series": series, "rep": r, "delta": delta, "eta": eta,
                     "eps": eps, "dropout": dropout, "depth": depth,
                     "n_b": n_b or N_CELLS_PER_GROUP,
                     "module_size": module_size or MODULE_SIZE,
                     "module_seed": module_seed, **m})


print("\n2. Running simulation grid")
t0 = time.time()
run_series("baseline", n_reps=N_NULL_REPS)                                   # calibration
for d in DELTA_GRID:
    for s in MODULE_SEEDS:                                              # power / monotonicity
        run_series("signal", delta=d, module_seed=s)
for e in ETA_GRID:
    run_series("neutral_hk", eta=e)                                      # type-I (HK drift)
for e in EPS_GRID:
    run_series("neutral_global", eps=e)                                  # type-I (batch noise)
for e in ETA_GRID:
    run_series("confounded", delta=0.5, eta=e)                           # signal + drift
for d in [0.25, 1.0]:
    run_series("dropout", delta=d, dropout=0.3)
    run_series("depth", delta=d, depth=0.5)
    run_series("imbalance", delta=d, n_b=N_CELLS_PER_GROUP // 4)
for m in [50, 500]:                                   # module-size sensitivity
    run_series("module_size", delta=1.0, module_size=m)
print(f"   Done: {len(rows)} replicates ({time.time() - t0:.0f}s)")

raw = pd.DataFrame(rows)
raw.to_csv(RESULTS_DIR / "groundtruth_simulation_raw.csv", index=False)

# ---------------------------------------------------------------- analysis
print("\n3. Analysis")
base = raw[raw["series"] == "baseline"]
thresholds = {m: float(np.nanpercentile(base[m], NULL_Q)) for m in METRIC_COLS}
print("   Null thresholds (95th percentile):",
      {k: round(v, 5) for k, v in thresholds.items()})


def exceed_rate(df):
    return {m: float((df[m] > thresholds[m]).mean()) for m in METRIC_COLS}


analysis = {"null_thresholds": thresholds, "n_baseline": len(base),
            "seed": RANDOM_SEED,
            "background": f"Tabula Muris FACS Marrow ({BACKGROUND_CT})",
            "n_cells_background": int(n_cells_total), "n_keep_genes": int(n_keep),
            "n_hk": int(len(hk_in_keep)), "module_size": MODULE_SIZE,
            "n_cells_per_group": N_CELLS_PER_GROUP, "n_reps": N_REPS}

# 1) monotonicity: Spearman(delta level, mean metric) over signal series + null
grid_d = [0.0] + DELTA_GRID
means_by_d = {}
for d in grid_d:
    sub = base if d == 0.0 else raw[(raw["series"] == "signal") & (raw["delta"] == d)]
    means_by_d[d] = {m: float(sub[m].mean()) for m in METRIC_COLS}
from scipy.stats import spearmanr
monotonicity = {}
for m in METRIC_COLS:
    rho, p = spearmanr(grid_d, [means_by_d[d][m] for d in grid_d])
    monotonicity[m] = {"spearman_rho": round(float(rho), 4), "p": float(p)}
analysis["monotonicity_vs_delta"] = monotonicity

# 2) type-I error: neutral series
typeI = {}
for s in ["neutral_hk", "neutral_global"]:
    sub = raw[raw["series"] == s]
    typeI[s] = {"rates_by_condition": {}, "overall": exceed_rate(sub)}
    for _, g in sub.groupby(["eta", "eps"]):
        typeI[s]["rates_by_condition"][f"eta={g['eta'].iat[0]},eps={g['eps'].iat[0]}"] = \
            exceed_rate(g)
analysis["type_I_error"] = typeI

# 3) power per delta (pooled across module seeds + per-seed spread)
power = {}
for d in DELTA_GRID:
    sub = raw[(raw["series"] == "signal") & (raw["delta"] == d)]
    power[str(d)] = exceed_rate(sub)
    power[str(d)]["by_seed"] = {
        str(s): exceed_rate(sub[sub["module_seed"] == s]) for s in MODULE_SEEDS}
analysis["power"] = power

# 4) confounded: detection rate under signal+drift (delta=0.5 fixed)
conf = {}
for e in ETA_GRID:
    sub = raw[(raw["series"] == "confounded") & (raw["eta"] == e)]
    conf[str(e)] = exceed_rate(sub)
analysis["confounded_detection_delta0.5"] = conf

# 5) AUC separating signal (delta>=0.25) vs neutral (HK drift + global noise)
from sklearn.metrics import roc_auc_score
sig = raw[(raw["series"] == "signal") & (raw["delta"] >= 0.25)]
neu = raw[raw["series"].isin(["neutral_hk", "neutral_global"])]
y = np.r_[np.ones(len(sig)), np.zeros(len(neu))]
auc = {}
for m in METRIC_COLS:
    x = np.r_[sig[m].to_numpy(), neu[m].to_numpy()]
    auc[m] = round(float(roc_auc_score(y, x)), 4)
analysis["auc_signal_vs_neutral"] = auc

# 6) bias / variance: CV per signal condition
cv = {}
for d in DELTA_GRID:
    sub = raw[(raw["series"] == "signal") & (raw["delta"] == d)]
    cv[str(d)] = {m: round(float(sub[m].std() / sub[m].mean()), 4)
                  for m in METRIC_COLS}
analysis["cv_by_delta"] = cv

# 7) robustness: detection rates in dropout/depth/imbalance scenarios
rob = {}
for s in ["dropout", "depth", "imbalance"]:
    sub = raw[raw["series"] == s]
    rob[s] = {}
    for d in [0.25, 1.0]:
        g = sub[sub["delta"] == d]
        rob[s][str(d)] = exceed_rate(g)
analysis["robustness"] = rob

# 8) module-size sensitivity (delta=1.0)
ms = {}
for m in [50, 200, 500]:
    sub = raw[(raw["series"].isin(["module_size", "signal"]))
              & (raw["delta"] == 1.0)
              & (raw["module_size"] == m)]
    ms[str(m)] = {"means": {c: round(float(sub[c].mean()), 5)
                             for c in METRIC_COLS},
                  "power": exceed_rate(sub)}
analysis["module_size_sensitivity_delta1"] = ms

with open(RESULTS_DIR / "groundtruth_simulation_metrics.json", "w") as f:
    json.dump(analysis, f, indent=2)

# summary CSV
summ_rows = []
for (series, d, e, eps, msz, mseed), g in raw.groupby(
        ["series", "delta", "eta", "eps", "module_size", "module_seed"]):
    row = {"series": series, "delta": d, "eta": e, "eps": eps,
           "module_size": msz, "module_seed": mseed, "n": len(g)}
    for m in METRIC_COLS:
        row[f"{m}_mean"] = round(float(g[m].mean()), 5)
        row[f"{m}_sd"] = round(float(g[m].std()), 5)
        row[f"{m}_power"] = round(float((g[m] > thresholds[m]).mean()), 3)
    summ_rows.append(row)
pd.DataFrame(summ_rows).to_csv(
    RESULTS_DIR / "groundtruth_simulation_summary.csv", index=False)

print("\n" + "=" * 64)
print("KEY RESULTS")
print("=" * 64)
print("\nMonotonicity vs injected delta (Spearman):")
for m, v in monotonicity.items():
    print(f"  {m:12s} rho={v['spearman_rho']:+.3f}  p={v['p']:.2e}")
print("\nType-I error (should be ~0.05 for a calibrated metric):")
for s in ["neutral_hk", "neutral_global"]:
    print(f"  {s}: " + ", ".join(f"{m}={v:.3f}"
          for m, v in typeI[s]["overall"].items()))
print("\nPower (detection rate at each delta, pooled over 3 module seeds):")
hdr = "  delta | " + " ".join(f"{m:>10s}" for m in METRIC_COLS)
print(hdr)
for d in DELTA_GRID:
    print(f"  {d:5.3f} | " + " ".join(f"{power[str(d)][m]:10.3f}" for m in METRIC_COLS))
print("  per-seed omega power:")
for d in DELTA_GRID:
    seeds = power[str(d)]["by_seed"]
    print(f"  delta={d:5.3f}: " + " ".join(f"seed{s}={v['omega']:.2f}"
                                           for s, v in seeds.items()))
print("\nConfounded (delta=0.5 + HK drift eta) detection:")
print(hdr.replace("delta", " eta  "))
for e in ETA_GRID:
    print(f"  {e:5.2f} | " + " ".join(f"{conf[str(e)][m]:10.3f}" for m in METRIC_COLS))
print("\nAUC signal vs neutral:")
print("  " + ", ".join(f"{m}={v:.3f}" for m, v in auc.items()))
print("\nModule-size sensitivity (delta=1.0):")
for m in [50, 200, 500]:
    v = ms[str(m)]
    print(f"  m={m:4d}: omega_mean={v['means']['omega']:7.3f}  "
          f"k_f_mean={v['means']['k_f']:.5f}  "
          f"power(omega)={v['power']['omega']:.2f}  "
          f"power(cosine)={v['power']['cosine']:.2f}")
print("\nOutputs written:")
print(f"  {RESULTS_DIR / 'groundtruth_simulation_raw.csv'}")
print(f"  {RESULTS_DIR / 'groundtruth_simulation_summary.csv'}")
print(f"  {RESULTS_DIR / 'groundtruth_simulation_metrics.json'}")
