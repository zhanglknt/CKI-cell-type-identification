"""
91_augur_v45.py — Analysis D: Augur cell-type prioritization vs CKI brain ranking
=================================================================================
Question (r-singlecell P1-4): does CKI's brain-region gradient ranking of
non-neuronal classes agree with an independent, classifier-based cell-type
prioritization (Augur; Skinnider et al., Nat Biotechnol 2021)?

Design
------
1. Siletti adult human brain non-neurons (Nonneurons.h5ad, 888,263 nuclei).
   Stratified sample: up to 50 nuclei per (supercluster_term x roi) group,
   keeping only groups with >=20 nuclei and regions with >=50 total nuclei
   (mirrors the CKI v4 pipeline filters).
2. Per class: library-size normalize (CP10k) + log1p, then run Augur-style
   prioritization with pyaugur (pure-Python port of R Augur v1.0.3; benchmark
   Spearman rho = 1.0 vs R). Condition label = brain region (`roi`, 108 regions);
   per class only regions with >=20 sampled nuclei are used (same eligibility
   as CKI). Classifier = random forest (100 trees), multiclass macro-OvR AUC,
   5 subsample seeds x 3-fold stratified CV = 15 AUC estimates per class.
   Augur score per class = mean AUC.
3. Consistency: Spearman rho between the 10-class Augur ranking and CKI
   class-level mean omega, and separately vs k_f-only and k_n-only means
   (results/brain_v44_class_confound.csv), to test whether agreement comes
   from the HK-anchored numerator (k_f) or denominator (k_n).

Note: augurpy is not available on PyPI for Python 3.13; pyaugur (PyPI,
GPL-3.0) is a numerically faithful port of the same R reference
implementation and is used here instead.

Outputs
-------
results/augur_comparison_v45.json
results/augur_comparison_v45_report.md
"""

import json
import time
import warnings

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import spearmanr

import pyaugur

warnings.filterwarnings("ignore")

t0 = time.time()
SEED = 42
CAP_PER_GROUP = 50          # max nuclei sampled per (class, region)
MIN_NUCLEI_GROUP = 20       # mirrors CKI v4 filter
MIN_NUCLEI_REGION = 50      # mirrors CKI v4 filter
AUGUR_SEEDS = [42, 43, 44, 45, 46]
SUBSAMPLE_SIZE = 20         # cells per region per Augur subsample
FOLDS = 3

from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
H5AD_FILE = DATA_DIR / "brain" / "Nonneurons.h5ad"
CKI_CLASS_FILE = RESULTS_DIR / "brain_v44_class_confound.csv"

print("=" * 70)
print("Analysis D: Augur prioritization vs CKI brain class ranking")
print("=" * 70)

# ---------------------------------------------------------------- 1. obs only
print("\n[1] Loading obs (backed)...")
adata = sc.read_h5ad(H5AD_FILE, backed="r")
print(f"    shape: {adata.shape}")

obs = adata.obs[["supercluster_term", "roi"]].copy()
obs.columns = ["cell_type", "region"]

# ------------------------------------------------- 2. group filters + sample
print("\n[2] Group filters (mirror CKI v4)...")
grp_counts = obs.groupby(["cell_type", "region"]).size()
groups_ok = grp_counts[grp_counts >= MIN_NUCLEI_GROUP]
region_totals = groups_ok.groupby("region").sum()
regions_ok = set(region_totals[region_totals >= MIN_NUCLEI_REGION].index)
groups_ok = groups_ok[groups_ok.index.get_level_values("region").isin(regions_ok)]
print(f"    eligible (ct, region) groups: {len(groups_ok)}")
print(f"    eligible regions: {len(regions_ok)}")

rng = np.random.default_rng(SEED)
key = list(zip(obs["cell_type"], obs["region"]))
ok_set = set(groups_ok.index)
sampled_idx = []
# group row positions once
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
print(f"    sampled nuclei: {len(sampled_idx)}")

sampled_obs = obs.iloc[sampled_idx].copy()

# ------------------------------------------------- 3. per-class Augur runs
print("\n[3] Per-class extraction + Augur (pyaugur, RF, macro-OvR AUC)...")
ck_classes = list(groups_ok.index.get_level_values("cell_type").unique())
print(f"    classes: {len(ck_classes)}")

per_class_records = []   # every individual AUC estimate
augur_scores = {}
region_sets = {}

for ct in ck_classes:
    tct = time.time()
    # rows of this class within the sampled set
    ct_mask = sampled_obs["cell_type"] == ct
    ct_obs = sampled_obs[ct_mask]
    # eligible regions for this class (>=20 sampled nuclei; same as CKI)
    reg_counts = ct_obs["region"].value_counts()
    elig_regions = sorted(reg_counts[reg_counts >= SUBSAMPLE_SIZE].index)
    ct_obs = ct_obs[ct_obs["region"].isin(elig_regions)]
    region_sets[ct] = elig_regions

    # global positions of these cells in the backed object
    global_idx = np.sort(obs.index.get_indexer(ct_obs.index))

    sub = adata[global_idx].to_memory()
    sc.pp.normalize_total(sub, target_sum=1e4)
    sc.pp.log1p(sub)
    X = sub.X
    if hasattr(X, "toarray"):
        X = X.toarray()
    X = np.asarray(X, dtype=np.float32)  # cells x genes
    # drop genes never detected in this class subset (speed + memory)
    detected = (X > 0).sum(axis=0) >= max(2, int(0.01 * X.shape[0]))
    X = X[:, detected]
    expr = X.T  # genes x cells (pyaugur convention)

    meta = pd.DataFrame({
        "cell_type": ct,
        "label": ct_obs["region"].astype(str).values,
    })

    auc_vals = []
    for sd in AUGUR_SEEDS:
        res = pyaugur.calculate_auc(
            expr,
            meta=meta,
            label_col="label",
            cell_type_col="cell_type",
            n_subsamples=1,
            subsample_size=SUBSAMPLE_SIZE,
            folds=FOLDS,
            min_cells=SUBSAMPLE_SIZE,
            var_quantile=0.5,
            feature_perc=0.5,
            classifier="rf",
            seed=sd,
        )
        r = res["results"]
        aucs = r[r["metric"] == "roc_auc"]["estimate"].values
        auc_vals.extend(aucs)
        for v in aucs:
            per_class_records.append({"cell_type": ct, "seed": sd, "auc": float(v)})

    augur_scores[ct] = float(np.mean(auc_vals))
    print(f"    {ct:45s} regions={len(elig_regions):3d} cells={X.shape[0]:5d} "
          f"genes={X.shape[1]:5d} meanAUC={augur_scores[ct]:.4f} "
          f"({time.time()-tct:.0f}s)")

# ------------------------------------------------- 4. CKI class-level values
print("\n[4] CKI class-level omega / k_f / k_n ...")
cki_cls = pd.read_csv(CKI_CLASS_FILE)
cki_cls = cki_cls.set_index("cell_type")

rows = []
for ct in ck_classes:
    rows.append({
        "cell_type": ct,
        "augur_auc": augur_scores[ct],
        "cki_omega": float(cki_cls.loc[ct, "omega_mean"]),
        "cki_kf": float(cki_cls.loc[ct, "kf_mean"]),
        "cki_kn": float(cki_cls.loc[ct, "kn_mean"]),
        "n_regions": len(region_sets[ct]),
    })
cmp_df = pd.DataFrame(rows)

spearman_results = {}
for target, col in [("omega", "cki_omega"), ("k_f", "cki_kf"), ("k_n", "cki_kn")]:
    rho, p = spearmanr(cmp_df["augur_auc"], cmp_df[col])
    spearman_results[target] = {"rho": float(rho), "p": float(p)}
    print(f"    Augur vs CKI {target:6s}: Spearman rho = {rho:+.4f}, P = {p:.4g}")

# ------------------------------------------------- 5. outputs
out = {
    "design": {
        "tool": "pyaugur 0.1.0 (pure-Python port of R Augur v1.0.3; augurpy "
                "unavailable for Python 3.13)",
        "condition_label": "brain region (roi, multiclass macro-OvR AUC)",
        "classifier": "random forest (100 trees, package defaults)",
        "subsample_size_per_region": SUBSAMPLE_SIZE,
        "folds": FOLDS,
        "seeds": AUGUR_SEEDS,
        "sampling": f"<= {CAP_PER_GROUP} nuclei per (class, region); "
                    f">={MIN_NUCLEI_GROUP} nuclei/group; "
                    f">={MIN_NUCLEI_REGION} nuclei/region",
        "normalization": "CP10k + log1p",
        "n_sampled_nuclei": int(len(sampled_idx)),
        "seed": SEED,
    },
    "per_class": rows,
    "per_class_auc_estimates": per_class_records,
    "spearman": spearman_results,
    "runtime_sec": time.time() - t0,
}
json_path = RESULTS_DIR / "augur_comparison_v45.json"
with open(json_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"\n[5] Wrote {json_path}")

# report
cmp_sorted = cmp_df.sort_values("augur_auc", ascending=False)
lines = []
lines.append("# Analysis D: Augur cell-type prioritization vs CKI brain class ranking\n")
lines.append("## Design\n")
lines.append("- **Data**: Siletti adult human brain non-neurons (CELLxGENE 283d65eb-dd53-496d-adb7-7570c7caa443; "
             f"888,263 nuclei). Stratified sample of {len(sampled_idx):,} nuclei "
             f"(<= {CAP_PER_GROUP} per class x region group; groups with >= {MIN_NUCLEI_GROUP} nuclei, "
             f"regions with >= {MIN_NUCLEI_REGION} total nuclei — identical filters to the CKI v4 pipeline).")
lines.append("- **Augur**: pyaugur 0.1.0, a pure-Python port of R Augur v1.0.3 (Skinnider et al., "
             "Nat Biotechnol 2021); the R package's reference Python port `augurpy` is not distributed "
             "for Python 3.13, so the numerically faithful port (benchmark Spearman rho = 1.0 vs R) was used. "
             "Condition label = brain region (`roi`; 108 regions), evaluated per class over its eligible "
             f"regions (>= {SUBSAMPLE_SIZE} sampled nuclei, mirroring CKI eligibility). Random forest "
             f"(100 trees), multiclass macro-OvR AUC, {len(AUGUR_SEEDS)} subsample seeds x {FOLDS}-fold "
             "stratified CV = 15 AUC estimates per class; Augur score = mean AUC. Input: CP10k + log1p.")
lines.append("- **CKI side**: class-level mean omega / k_f / k_n from `results/brain_v44_class_confound.csv`.\n")
lines.append("## Results\n")
lines.append("| Rank | Cell type | Augur AUC | CKI omega | CKI k_f | CKI k_n | n regions |")
lines.append("|---|---|---|---|---|---|---|")
for i, r in enumerate(cmp_sorted.itertuples(), 1):
    lines.append(f"| {i} | {r.cell_type} | {r.augur_auc:.4f} | {r.cki_omega:.2f} | "
                 f"{r.cki_kf:.4f} | {r.cki_kn:.6f} | {r.n_regions} |")
lines.append("")
s = spearman_results
lines.append("### Rank consistency (Spearman, n = 10 classes)\n")
lines.append("| Comparison | rho | P |")
lines.append("|---|---|---|")
lines.append(f"| Augur AUC vs CKI omega | {s['omega']['rho']:+.4f} | {s['omega']['p']:.4g} |")
lines.append(f"| Augur AUC vs CKI k_f (HK-anchored numerator) | {s['k_f']['rho']:+.4f} | {s['k_f']['p']:.4g} |")
lines.append(f"| Augur AUC vs CKI k_n (denominator) | {s['k_n']['rho']:+.4f} | {s['k_n']['p']:.4g} |")
lines.append("")
lines.append("## Interpretation\n")
rho_o = s["omega"]["rho"]
if rho_o >= 0.6:
    verdict = ("The two rankings are concordant: cell types whose expression is most separable "
               "across brain regions (Augur AUC) are also those with the highest HK-anchored "
               "cross-region divergence (CKI omega). This is a complementary, methodologically "
               "independent validation — Augur measures per-cell classifier separability over the "
               "whole transcriptome, whereas CKI measures a pseudobulk housekeeping-anchored ratio — "
               "establishing that CKI occupies the same problem domain as perturbation-response "
               "prioritization (Augur/Milo/scCODA) with a distinct, ratio-based readout.")
elif rho_o >= 0.3:
    verdict = ("The rankings are moderately concordant: broad agreement at the extremes with some "
               "reordering in the middle of the ranking.")
else:
    verdict = ("The rankings diverge. Augur scores per-cell whole-transcriptome separability, "
               "whereas CKI scores HK-anchored pseudobulk ratios; the divergence indicates the two "
               "metrics capture different aspects of cross-region variation.")
lines.append(verdict)
kf_better = abs(s["k_f"]["rho"]) > abs(s["k_n"]["rho"])
lines.append(f"\nDecomposition: the Augur ranking correlates more strongly with "
             f"{'k_f (the HK-anchored numerator)' if kf_better else 'k_n (the denominator)'} "
             f"(rho = {s['k_f']['rho']:+.3f} vs {s['k_n']['rho']:+.3f}), suggesting the shared signal "
             f"is carried predominantly by the {'cross-region conservation of housekeeping-anchored '
             f'expression (k_f)' if kf_better else 'cross-region divergence of the non-HK transcriptome (k_n)'}.")
lines.append(f"\n_Runtime: {time.time()-t0:.0f}s._\n")

report_path = RESULTS_DIR / "augur_comparison_v45_report.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"    Wrote {report_path}")
print(f"\nDone in {time.time()-t0:.0f}s")
