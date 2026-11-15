"""
v49.14 (R1-M2): same-data quantification of the aggregation-order switch.
==========================================================================
The manuscript states that the mouse (Tabula Muris pilot) and human
pipelines use softmax(mean(log1p)) whereas the brain pipeline and the
package default (v0.5.x) use softmax(log1p(mean counts)), and that
absolute omega values are not comparable across orders. This script
quantifies that statement on the pilot's own data: it rebuilds the 15
pilot comparisons (notebooks/02c_pilot_v2b.py, identical filters, seeds
and split logic) and computes omega under BOTH aggregation orders on the
same cells:

  legacy order: pb = mean(log1p(x_norm))        (softmax applied by js_divergence)
  brain  order: pb = log1p(mean(x_norm))        (softmax(log1p(mean counts)))

where x_norm is the normalize_total(target_sum=1e4) matrix BEFORE log1p.
Everything else (HK gene set, per-pair top-200 DE selection, JS base-2)
is order-matched: each order uses its own pseudobulks for the top-200
selection as well, mirroring how each pipeline would be run.

Outputs:
  results/nc49_agg_order_sensitivity.csv   (per-comparison omega both orders)
  results/nc49_agg_order_sensitivity.txt   (summary: Spearman, median fold)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
from scipy import stats
from cki.core import js_divergence

TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
MIN_CELLS_PER_CT = 10
N_TOP_KF = 200
RANDOM_SEED = 42

OUT_CSV = RESULTS_DIR / "nc49_agg_order_sensitivity.csv"
OUT_TXT = RESULTS_DIR / "nc49_agg_order_sensitivity.txt"

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

def extract_mouse_id(cell_name):
    parts = cell_name.split(".")
    for p in parts:
        if "_" in p and (p.endswith("_M") or p.endswith("_F")):
            return p
    return "unknown"

def random_split_cells(cells, seed=RANDOM_SEED):
    n = cells.shape[0]
    n_half = n // 2
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    return cells[idx[:n_half]], cells[idx[n_half:]]

log("1. Loading mouse data (verbatim 02c pipeline)...")
hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_mouse_genes = set(hk_df.iloc[:, 0].dropna().astype(str))

annot = pd.read_csv(FACS_ANNOTATIONS)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
annot["mouse.id"] = annot["cell"].apply(extract_mouse_id)

adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if not fname.exists():
        continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())

common_genes = all_genes.copy()
for tissue, df in adatas.items():
    common_genes &= set(df.index)
common_genes = sorted(common_genes)

expr_parts, obs_parts = [], []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
    expr_parts.append(df_aligned.values)
    tissue_annot = annot[annot["tissue"] == tissue].copy()
    cell_ids = df_aligned.index.tolist()
    obs_tissue = pd.DataFrame({"cell": cell_ids, "tissue": tissue})
    obs_tissue = obs_tissue.merge(tissue_annot[["cell", "cell_ontology_class", "mouse.id"]],
                                  on="cell", how="left")
    obs_tissue["cell_ontology_class"] = obs_tissue["cell_ontology_class"].fillna("unknown")
    obs_tissue.set_index("cell", inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({"gene": common_genes}).set_index("gene")
adata = sc.AnnData(X=X, obs=obs, var=var)
adata.obs["tissue"] = adata.obs["tissue"].astype("category")

sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
log(f"   unified AnnData after QC: {adata.n_obs} cells x {adata.n_vars} genes")

# --- the only divergence from 02c: keep the pre-log1p normalized matrix ---
X_norm = adata.X.copy()
if hasattr(X_norm, "toarray"):
    X_norm = X_norm.toarray()
sc.pp.normalize_total(adata, target_sum=1e4)
X_norm = adata.X.copy()
if hasattr(X_norm, "toarray"):
    X_norm = X_norm.toarray()
X_log = np.log1p(X_norm)  # legacy order input (what 02c then averages)

gene_names = adata.var_names.tolist()
hk_indices = [i for i, g in enumerate(gene_names) if g in hk_mouse_genes]
N_GENES = len(gene_names)
non_hk_mask = np.ones(N_GENES, dtype=bool)
for idx in hk_indices:
    non_hk_mask[idx] = False
non_hk_indices = np.where(non_hk_mask)[0]

# tissue / ct index arrays on the QC-filtered cells
tissue_arr = adata.obs["tissue"].astype(str).values
ct_arr = adata.obs["cell_ontology_class"].astype(str).values
mouse_arr = adata.obs["mouse.id"].astype(str).values

log("2. Rebuilding the 15 pilot comparisons (same filters, same seeds)...")
ct_all_cells = {}
ct_cells_largest = {}
for tissue in TARGET_TISSUES:
    tmask = tissue_arr == tissue
    for ct in np.unique(ct_arr[tmask]):
        if ct.lower() == "unknown":
            continue
        ct_mask = tmask & (ct_arr == ct)
        if ct_mask.sum() < MIN_CELLS_PER_CT * 2:
            continue
        ct_all_cells[(tissue, ct)] = np.where(ct_mask)[0]
        mouse_counts = pd.Series(mouse_arr[ct_mask]).value_counts()
        mice_ok = [(m, n) for m, n in mouse_counts.items() if n >= MIN_CELLS_PER_CT]
        if mice_ok:
            mice_ok.sort(key=lambda x: -x[1])
            largest_mouse = mice_ok[0][0]
            mask_largest = ct_mask & (mouse_arr == largest_mouse)
            if mask_largest.sum() >= MIN_CELLS_PER_CT:
                ct_cells_largest[(tissue, ct)] = np.where(mask_largest)[0]

comparisons = []
control_pairs = [
    ("Liver", "hepatocyte"),
    ("Heart", "endothelial cell"),
    ("Spleen", "B cell"),
    ("Marrow", "B cell"),
    ("Heart", "fibroblast"),
    ("Marrow", "neutrophil"),
]
for tissue, ct in control_pairs:
    key = (tissue, ct)
    if key in ct_all_cells:
        cells = ct_all_cells[key]
        n = len(cells)
        n_half = n // 2
        rng = np.random.RandomState(RANDOM_SEED)
        idx = rng.permutation(n)
        comparisons.append({
            "label": f"C: {ct} ({tissue})", "category": "C_control",
            "cells_a": cells[idx[:n_half]], "cells_b": cells[idx[n_half:]],
        })

same_ct_pairs = [
    ("B cell", "Marrow", "Spleen"),
    ("B cell", "Spleen", "Lung"),
    ("endothelial cell", "Heart", "Lung"),
    ("natural killer cell", "Marrow", "Liver"),
]
for ct, t1, t2 in same_ct_pairs:
    key1, key2 = (t1, ct), (t2, ct)
    if key1 in ct_cells_largest and key2 in ct_cells_largest:
        comparisons.append({
            "label": f"S: {ct} ({t1} vs {t2})", "category": "S_same_ct",
            "cells_a": ct_cells_largest[key1], "cells_b": ct_cells_largest[key2],
        })

diff_ct_pairs = [
    ("Liver", "hepatocyte", "endothelial cell of hepatic sinusoid"),
    ("Marrow", "B cell", "neutrophil"),
    ("Heart", "endothelial cell", "fibroblast"),
]
for tissue, ct1, ct2 in diff_ct_pairs:
    key1, key2 = (tissue, ct1), (tissue, ct2)
    if key1 in ct_cells_largest and key2 in ct_cells_largest:
        comparisons.append({
            "label": f"D: {ct1} vs {ct2} ({tissue})", "category": "D_diff_ct",
            "cells_a": ct_cells_largest[key1], "cells_b": ct_cells_largest[key2],
        })

cross_pairs = [
    ("Liver", "hepatocyte", "Marrow", "B cell"),
    ("Heart", "cardiac muscle cell", "Marrow", "neutrophil"),
]
for t1, ct1, t2, ct2 in cross_pairs:
    key1, key2 = (t1, ct1), (t2, ct2)
    if key1 in ct_cells_largest and key2 in ct_cells_largest:
        comparisons.append({
            "label": f"X: {ct1}({t1}) vs {ct2}({t2})", "category": "X_cross",
            "cells_a": ct_cells_largest[key1], "cells_b": ct_cells_largest[key2],
        })

log(f"   comparisons rebuilt: {len(comparisons)}")

def omega_under_order(cells_a_idx, cells_b_idx, order):
    """omega with the aggregation order switched; everything else identical."""
    if order == "legacy":
        pb_a = np.mean(X_log[cells_a_idx], axis=0)
        pb_b = np.mean(X_log[cells_b_idx], axis=0)
    else:  # brain / package default
        pb_a = np.log1p(np.mean(X_norm[cells_a_idx], axis=0))
        pb_b = np.log1p(np.mean(X_norm[cells_b_idx], axis=0))
    kn = js_divergence(pb_a[hk_indices], pb_b[hk_indices])
    abs_diff = np.abs(pb_a - pb_b)
    abs_diff_non_hk = abs_diff[non_hk_mask]
    top_n = min(N_TOP_KF, len(abs_diff_non_hk))
    top_local = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
    top_global = non_hk_indices[top_local]
    kf = js_divergence(pb_a[top_global], pb_b[top_global])
    return kn, kf, (kf / kn if kn > 0 else np.inf)

log("3. Computing omega under both orders...")
rows = []
for comp in comparisons:
    kn_l, kf_l, w_l = omega_under_order(comp["cells_a"], comp["cells_b"], "legacy")
    kn_b, kf_b, w_b = omega_under_order(comp["cells_a"], comp["cells_b"], "brain")
    rows.append({
        "comparison": comp["label"], "category": comp["category"],
        "n_a": len(comp["cells_a"]), "n_b": len(comp["cells_b"]),
        "omega_legacy": w_l, "kn_legacy": kn_l, "kf_legacy": kf_l,
        "omega_brain_order": w_b, "kn_brain_order": kn_b, "kf_brain_order": kf_b,
        "fold_brain_over_legacy": w_b / w_l if w_l > 0 else np.nan,
    })
    log(f"   {comp['label']}: legacy={w_l:.2f} -> brain={w_b:.2f} "
        f"(x{w_b / w_l:.2f})")

res = pd.DataFrame(rows)
res.to_csv(OUT_CSV, index=False)

rho_all = stats.spearmanr(res.omega_legacy, res.omega_brain_order)
# within-category (same biological contrast tier) rank agreement
cats = [c for c in ["C_control", "S_same_ct", "D_diff_ct", "X_cross"]
        if (res.category == c).sum() >= 3]
rho_cat = stats.spearmanr(
    res[res.category.isin(cats)].omega_legacy,
    res[res.category.isin(cats)].omega_brain_order)
med_fold = float(np.median(res.fold_brain_over_legacy))

summary = [
    "Aggregation-order sensitivity on the mouse pilot's 15 comparisons",
    "=" * 66,
    f"legacy order softmax(mean(log1p)) vs brain order softmax(log1p(mean counts))",
    f"same cells, same HK set, order-matched per-pair top-{N_TOP_KF} DE selection",
    "",
    f"Spearman rho (15 comparisons)       : {rho_all.statistic:.3f} (P = {rho_all.pvalue:.2g})",
    f"Spearman rho (within-category cats) : {rho_cat.statistic:.3f} (P = {rho_cat.pvalue:.2g})",
    f"median fold (brain/legacy omega)    : {med_fold:.2f}x",
    f"fold range                          : {res.fold_brain_over_legacy.min():.2f}x - {res.fold_brain_over_legacy.max():.2f}x",
    f"control (C) category median omega   : legacy {res[res.category=='C_control'].omega_legacy.median():.2f} "
    f"-> brain {res[res.category=='C_control'].omega_brain_order.median():.2f}",
    "",
    "Per-comparison table:",
    res.to_string(index=False),
    "",
]
(OUT_TXT).write_text("\n".join(summary), encoding="utf-8")
log("")
log(f"Spearman rho (15): {rho_all.statistic:.3f} (P={rho_all.pvalue:.2g})")
log(f"median fold brain/legacy: {med_fold:.2f}x")
log(f"saved: {OUT_CSV}")
log(f"saved: {OUT_TXT}")
print("DONE")
