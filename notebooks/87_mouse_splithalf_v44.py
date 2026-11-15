"""
CKI Mouse Split-Half Calibration v44 (script 87)
=================================================
Blind-review request: the omega baseline 6.67 rests on only 6 split-half
comparisons (notebooks/02b_pilot_v2.py, C_control category). Increase to
50 independent random splits per control population (6 populations ->
300 split-half omegas) and report mean / SD / 95% CI, compared with 6.67.

Pipeline mirrors 02b exactly (same data, QC, normalization, k_n/k_f/omega
definitions, same 6 control populations); the permutation bootstrap test is
skipped (only observed split-half omegas are needed for calibration).

Seed: 42. Outputs use _v44 suffix; no existing results file is overwritten.
"""

import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import scanpy as sc
from scipy import stats as sstats
from cki.core import js_divergence

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_t0 = time.time()

# ===== Config (identical to 02b) =====
TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10
N_TOP_KF = 200
N_SPLITS = 50

CONTROL_PAIRS = [
    ("Liver", "hepatocyte"),
    ("Heart", "endothelial cell"),
    ("Spleen", "B cell"),
    ("Marrow", "B cell"),
    ("Heart", "fibroblast"),
    ("Marrow", "neutrophil"),
]

# ===== 1. Load data (as 02b) =====
print("=" * 60)
print("1. Loading mouse FACS data...")
hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
hk_mouse_genes = set(hk_df.iloc[:, 0].tolist())
print(f"  HK genes: {len(hk_mouse_genes)}")

annot = pd.read_csv(FACS_ANNOTATIONS)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
print(f"  Annotations: {len(annot)} cells")

adatas, all_genes = {}, set()
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
print(f"  Common genes: {len(common_genes)}")

expr_parts, obs_parts = [], []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
    expr_parts.append(df_aligned.values)
    tissue_annot = annot[annot["tissue"] == tissue].copy()
    obs_tissue = pd.DataFrame({"cell": df_aligned.index.tolist(), "tissue": tissue})
    obs_tissue = obs_tissue.merge(tissue_annot[["cell", "cell_ontology_class"]], on="cell", how="left")
    obs_tissue["cell_ontology_class"] = obs_tissue["cell_ontology_class"].fillna("unknown")
    obs_tissue.set_index("cell", inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({"gene": common_genes}).set_index("gene")
adata = sc.AnnData(X=X, obs=obs, var=var)
print(f"  Unified AnnData: {adata.n_obs} cells x {adata.n_vars} genes")

# ===== 2. QC + normalization (as 02b) =====
print("\n2. QC + normalize_total(1e4) + log1p...")
sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
print(f"  After QC: {adata.n_obs} cells x {adata.n_vars} genes")
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

gene_names = adata.var_names.tolist()
hk_indices = np.array([i for i, g in enumerate(gene_names) if g in hk_mouse_genes])
non_hk_mask = np.ones(len(gene_names), dtype=bool)
non_hk_mask[hk_indices] = False
non_hk_global_idx = np.where(non_hk_mask)[0]
print(f"  HK genes matched: {len(hk_indices)}")

# ===== 3. Control population cells =====
print("\n3. Control populations...")
ct_all_cells = {}
for tissue, ct in CONTROL_PAIRS:
    mask = (adata.obs["tissue"] == tissue) & (adata.obs["cell_ontology_class"] == ct)
    sub = adata[mask]
    if sub.n_obs < MIN_CELLS_PER_CT * 2:
        print(f"  SKIP {ct} ({tissue}): only {sub.n_obs} cells")
        continue
    Xs = sub.X
    if hasattr(Xs, "toarray"):
        Xs = Xs.toarray()
    ct_all_cells[(tissue, ct)] = np.asarray(Xs)
    print(f"  {ct} ({tissue}): {sub.n_obs} cells")

# ===== 4. Omega for one split (02b definitions) =====
def split_omega(cells, rng):
    n = cells.shape[0]
    idx = rng.permutation(n)
    a, b = cells[idx[:n // 2]], cells[idx[n // 2:]]
    pb_a, pb_b = a.mean(axis=0), b.mean(axis=0)
    kn = js_divergence(pb_a[hk_indices], pb_b[hk_indices])
    ad = np.abs(pb_a - pb_b)
    ad_nh = ad[non_hk_mask]
    top_n = min(N_TOP_KF, len(ad_nh))
    tl = np.argpartition(ad_nh, -top_n)[-top_n:]
    tl = tl[np.argsort(ad_nh[tl])[::-1]]
    tg = non_hk_global_idx[tl]
    kf = js_divergence(pb_a[tg], pb_b[tg])
    return kn, kf, (kf / kn if kn > 0 else np.inf), n // 2, n - n // 2

# ===== 5. 50 independent splits per population =====
print(f"\n5. {N_SPLITS} independent split-half per population (seed={RANDOM_SEED})...")
rng = np.random.RandomState(RANDOM_SEED)
rows = []
for rep in range(N_SPLITS):
    for (tissue, ct), cells in ct_all_cells.items():
        kn, kf, om, na, nb = split_omega(cells, rng)
        rows.append({"rep": rep, "tissue": tissue, "cell_type": ct,
                     "kn": kn, "kf": kf, "omega": om,
                     "n_half_a": na, "n_half_b": nb})
    if (rep + 1) % 10 == 0:
        print(f"  rep {rep+1}/{N_SPLITS} done")

df = pd.DataFrame(rows)
df.to_csv(RESULTS_DIR / "mouse_splithalf_v44.csv", index=False)
print(f"  Saved: mouse_splithalf_v44.csv ({len(df)} split-half omegas)")

# ===== 6. Summary statistics =====
print("\n6. Summary...")
# (a) replicate-level baseline (mean over the 6 populations per rep) —
#     mirrors the 6.67 construction (mean of one split per population)
rep_base = df.groupby("rep")["omega"].mean()
# (b) pooled split-half omegas (300 values)
pooled = df["omega"].values

def ci_t(x):
    x = np.asarray(x)
    m, s, n = x.mean(), x.std(ddof=1), len(x)
    h = sstats.t.ppf(0.975, n - 1) * s / np.sqrt(n)
    return m, s, m - h, m + h

def ci_boot(x, B=10000, seed=RANDOM_SEED):
    r = np.random.RandomState(seed)
    x = np.asarray(x)
    boots = r.choice(x, size=(B, len(x)), replace=True).mean(axis=1)
    return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))

m_r, s_r, lo_r, hi_r = ci_t(rep_base.values)
blo_r, bhi_r = ci_boot(rep_base.values)
m_p, s_p, lo_p, hi_p = ci_t(pooled)
blo_p, bhi_p = ci_boot(pooled)

per_pop = df.groupby(["tissue", "cell_type"])["omega"].agg(["mean", "std", "count"])
print("\n  Per-population (50 splits each):")
print(per_pop.round(3).to_string())

summary = {
    "seed": RANDOM_SEED,
    "n_populations": len(ct_all_cells),
    "n_splits_per_population": N_SPLITS,
    "n_split_omegas_total": len(df),
    "reference_baseline_6split": 6.67,
    "reference_ci95_6split": [4.24, 9.24],
    "rep_baseline_mean": round(float(m_r), 3),
    "rep_baseline_sd": round(float(s_r), 3),
    "rep_baseline_ci95_t": [round(float(lo_r), 3), round(float(hi_r), 3)],
    "rep_baseline_ci95_boot": [round(blo_r, 3), round(bhi_r, 3)],
    "pooled_mean": round(float(m_p), 3),
    "pooled_sd": round(float(s_p), 3),
    "pooled_ci95_t": [round(float(lo_p), 3), round(float(hi_p), 3)],
    "pooled_ci95_boot": [round(blo_p, 3), round(bhi_p, 3)],
    "runtime_sec": round(time.time() - _t0, 1),
}
with open(RESULTS_DIR / "mouse_splithalf_v44_summary.json", "w") as jf:
    json.dump(summary, jf, indent=2)

with open(RESULTS_DIR / "mouse_splithalf_v44_summary.txt", "w") as fh:
    fh.write("Mouse split-half calibration v44 (50 splits x 6 populations, seed=42)\n")
    fh.write("=" * 70 + "\n")
    fh.write(f"Reference (6 splits, 02b): omega = 6.67, 95% boot CI [4.24, 9.24]\n\n")
    fh.write(f"Replicate baseline (mean of 6 populations per split, n={len(rep_base)}):\n")
    fh.write(f"  mean = {m_r:.3f}, SD = {s_r:.3f}\n")
    fh.write(f"  95% CI (t)    = [{lo_r:.3f}, {hi_r:.3f}]\n")
    fh.write(f"  95% CI (boot) = [{blo_r:.3f}, {bhi_r:.3f}]\n\n")
    fh.write(f"Pooled split-half omegas (n={len(pooled)}):\n")
    fh.write(f"  mean = {m_p:.3f}, SD = {s_p:.3f}\n")
    fh.write(f"  95% CI (t)    = [{lo_p:.3f}, {hi_p:.3f}]\n")
    fh.write(f"  95% CI (boot) = [{blo_p:.3f}, {bhi_p:.3f}]\n\n")
    fh.write("Per-population:\n")
    fh.write(per_pop.round(4).to_string())
    fh.write(f"\n\nRuntime: {time.time()-_t0:.0f}s\n")

print(f"\n  Replicate baseline: mean={m_r:.3f}, SD={s_r:.3f}, "
      f"95% CI(t)=[{lo_r:.3f}, {hi_r:.3f}], boot=[{blo_r:.3f}, {bhi_r:.3f}]")
print(f"  Pooled (300): mean={m_p:.3f}, SD={s_p:.3f}, "
      f"95% CI(t)=[{lo_p:.3f}, {hi_p:.3f}]")
print(f"  Reference: 6.67 [4.24, 9.24]")
print(f"  Saved: mouse_splithalf_v44_summary.json / .txt")
print(f"\nTotal runtime: {time.time()-_t0:.0f}s")
print("DONE")
