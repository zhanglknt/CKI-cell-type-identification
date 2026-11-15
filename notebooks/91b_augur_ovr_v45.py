"""
91b_augur_ovr_v45.py — Sensitivity for Analysis D: binary one-vs-rest Augur
============================================================================
The multiclass run (91_augur_v45.py) assigns each class a different number of
eligible regions (6–107), which confounds mean macro-OvR AUC with region-set
size. This sensitivity re-scores every class with strictly binary tasks:
for each eligible region r of a class, classify r vs the class's other
eligible regions (Augur-style RF, 100 trees, mtry=2, 3-fold stratified CV,
3 subsample repeats), then average AUC over regions. Every sub-task is
two-class, so scores are comparable across classes regardless of how many
regions each class has.

Uses the identical stratified sample as 91_augur_v45.py (same code, seed 42)
and pyaugur.select_variance for the Augur feature-selection step; the
per-region CV loop mirrors pyaugur's estimator settings
(Augur-style classifier prioritization, binary OvR variant).

Outputs
-------
results/augur_ovr_sensitivity_v45.json
Console: Spearman of binary-OvR Augur score vs CKI omega / k_f / k_n.
"""

import json
import time
import warnings

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

import pyaugur

warnings.filterwarnings("ignore")

t0 = time.time()
SEED = 42
CAP_PER_GROUP = 50
MIN_NUCLEI_GROUP = 20
MIN_NUCLEI_REGION = 50
SUBSAMPLE_SIZE = 20
REPEATS = 3
FOLDS = 3
REPEAT_SEEDS = [142, 242, 342]

from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
H5AD_FILE = DATA_DIR / "brain" / "Nonneurons.h5ad"
CKI_CLASS_FILE = RESULTS_DIR / "brain_v44_class_confound.csv"

print("=" * 70)
print("Analysis D sensitivity: binary one-vs-rest Augur vs CKI ranking")
print("=" * 70, flush=True)

# ------------------------------------------------- identical sampling to 91
print("\n[1] Loading obs (backed)...", flush=True)
adata = sc.read_h5ad(H5AD_FILE, backed="r")
obs = adata.obs[["supercluster_term", "roi"]].copy()
obs.columns = ["cell_type", "region"]

grp_counts = obs.groupby(["cell_type", "region"]).size()
groups_ok = grp_counts[grp_counts >= MIN_NUCLEI_GROUP]
region_totals = groups_ok.groupby("region").sum()
regions_ok = set(region_totals[region_totals >= MIN_NUCLEI_REGION].index)
groups_ok = groups_ok[groups_ok.index.get_level_values("region").isin(regions_ok)]

rng = np.random.default_rng(SEED)
key = list(zip(obs["cell_type"], obs["region"]))
ok_set = set(groups_ok.index)
sampled_idx = []
pos_by_group = {}
for i, k in enumerate(key):
    if k in ok_set:
        pos_by_group.setdefault(k, []).append(i)
for k, positions in pos_by_group.items():
    positions = np.asarray(positions)
    if len(positions) > CAP_PER_GROUP:
        positions = rng.choice(positions, size=CAP_PER_GROUP, replace=False)
    sampled_idx.append(positions)
sampled_idx = np.sort(np.concatenate(sampled_idx))
sampled_obs = obs.iloc[sampled_idx].copy()
print(f"    sampled nuclei: {len(sampled_idx)}", flush=True)

# ------------------------------------------------- per-class binary OvR
print("\n[2] Per-class binary one-vs-rest Augur-style scoring...", flush=True)
ck_classes = list(groups_ok.index.get_level_values("cell_type").unique())

ovr_scores = {}
per_region_records = []

for ct in ck_classes:
    tct = time.time()
    ct_obs = sampled_obs[sampled_obs["cell_type"] == ct]
    reg_counts = ct_obs["region"].value_counts()
    elig_regions = sorted(reg_counts[reg_counts >= SUBSAMPLE_SIZE].index)
    ct_obs = ct_obs[ct_obs["region"].isin(elig_regions)]

    global_idx = np.sort(obs.index.get_indexer(ct_obs.index))
    sub = adata[global_idx].to_memory()
    sc.pp.normalize_total(sub, target_sum=1e4)
    sc.pp.log1p(sub)
    X = sub.X
    if hasattr(X, "toarray"):
        X = X.toarray()
    X = np.asarray(X, dtype=np.float32)
    detected = (X > 0).sum(axis=0) >= max(2, int(0.01 * X.shape[0]))
    X = X[:, detected]

    # Augur variance feature selection (once per class), genes x cells
    Xv = pyaugur.select_variance(X.T, var_quantile=0.5).T  # cells x genes_sel
    labels = ct_obs["region"].astype(str).values

    region_aucs = {}
    for r in elig_regions:
        in_r = np.where(labels == r)[0]
        out_r = np.where(labels != r)[0]
        aucs = []
        for rep, sd in enumerate(REPEAT_SEEDS):
            rrng = np.random.default_rng(sd)
            sel_in = rrng.choice(in_r, size=SUBSAMPLE_SIZE, replace=False)
            sel_out = rrng.choice(out_r, size=SUBSAMPLE_SIZE, replace=False)
            sel = np.concatenate([sel_in, sel_out])
            Xs = Xv[sel]
            ys = np.array([1] * SUBSAMPLE_SIZE + [0] * SUBSAMPLE_SIZE)
            skf = StratifiedKFold(n_splits=FOLDS, shuffle=True, random_state=rep + 1)
            for tr, te in skf.split(Xs, ys):
                np.random.seed(1)
                rf = RandomForestClassifier(
                    n_estimators=100, max_features=2, min_samples_split=2,
                    random_state=1, n_jobs=1,
                )
                rf.fit(Xs[tr], ys[tr])
                prob = rf.predict_proba(Xs[te])[:, 1]
                aucs.append(roc_auc_score(ys[te], prob))
        region_aucs[r] = float(np.mean(aucs))
        per_region_records.append({"cell_type": ct, "region": r,
                                   "auc": region_aucs[r]})

    ovr_scores[ct] = float(np.mean(list(region_aucs.values())))
    print(f"    {ct:45s} regions={len(elig_regions):3d} "
          f"meanOvR-AUC={ovr_scores[ct]:.4f} ({time.time()-tct:.0f}s)", flush=True)

# ------------------------------------------------- Spearman vs CKI
print("\n[3] Spearman vs CKI ...", flush=True)
cki_cls = pd.read_csv(CKI_CLASS_FILE).set_index("cell_type")
rows = []
for ct in ck_classes:
    rows.append({
        "cell_type": ct,
        "augur_ovr_auc": ovr_scores[ct],
        "cki_omega": float(cki_cls.loc[ct, "omega_mean"]),
        "cki_kf": float(cki_cls.loc[ct, "kf_mean"]),
        "cki_kn": float(cki_cls.loc[ct, "kn_mean"]),
    })
cmp_df = pd.DataFrame(rows)

spearman_results = {}
for target, col in [("omega", "cki_omega"), ("k_f", "cki_kf"), ("k_n", "cki_kn")]:
    rho, p = spearmanr(cmp_df["augur_ovr_auc"], cmp_df[col])
    spearman_results[target] = {"rho": float(rho), "p": float(p)}
    print(f"    OvR Augur vs CKI {target:6s}: rho = {rho:+.4f}, P = {p:.4g}", flush=True)

out = {
    "design": {
        "variant": "binary one-vs-rest per region (Augur-style; pyaugur "
                   "select_variance + sklearn RF 100 trees, mtry=2, "
                   "3-fold stratified CV x 3 repeats)",
        "sampling": "identical to 91_augur_v45.py (seed 42)",
        "subsample_per_task": f"{SUBSAMPLE_SIZE} vs {SUBSAMPLE_SIZE} cells",
        "class_score": "mean AUC over the class's eligible regions",
    },
    "per_class": rows,
    "per_region": per_region_records,
    "spearman": spearman_results,
    "runtime_sec": time.time() - t0,
}
json_path = RESULTS_DIR / "augur_ovr_sensitivity_v45.json"
with open(json_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\n[4] Wrote {json_path}", flush=True)
print(f"Done in {time.time()-t0:.0f}s", flush=True)
