# nc50: independent human-brain validation on the CELLxGENE Microglia supercluster
# (Human Brain Cell Atlas v1.0, collection 283d65eb-dd53-496d-adb7-7570c7caa443).
# Functional contrast: sample-matched microglial cell vs CNS macrophage pairs.
# Neutral contrast: random half-splits of the same (cell_type, sample) group (x20 per type).
# Metrics: CKI omega (kn_floor 1e-4), k_n, k_f, raw JS, cosine, Spearman, Jaccard.
# Pipeline: per-cell normalize_total(1e4) + log1p, group means (Tabula Sapiens human order);
# k_n on HRT Atlas v1.0 human HK genes; k_f on global seurat HVG 2000 excluding HK.
# Seed 42 throughout. Outputs: results/nc50_brain_atlas_microglia.csv / .txt
import json
import numpy as np
import pandas as pd
import scipy.sparse as sp
import scanpy as sc
import anndata as ad
from scipy.stats import mannwhitneyu, spearmanr
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cki.core import js_divergence

RNG = np.random.default_rng(42)
H5AD = r"data/human_brain_atlas_microglia.h5ad"
OUT_CSV = r"results/nc50_brain_atlas_microglia.csv"
OUT_TXT = r"results/nc50_brain_atlas_microglia.txt"
MIN_CELLS = 20
SPLIT_MIN = 200          # groups eligible for neutral half-splits (halves >= 100 cells)
N_SPLITS = 20            # neutral replicates per cell type
KN_FLOOR = 1e-4

print("loading h5ad ...", flush=True)
a = ad.read_h5ad(H5AD)
print("shape", a.shape, flush=True)

genes = a.var["feature_name"].astype(str).values
# unique gene index (first occurrence), matching project convention
seen = {}
keep_idx = []
for i, g in enumerate(genes):
    if g not in seen:
        seen[g] = i
        keep_idx.append(i)
keep_idx = np.array(keep_idx)
genes_u = genes[keep_idx]
gpos = {g: i for i, g in enumerate(genes_u)}

hk = pd.read_csv(r"cki/data/hrt_atlas.csv", sep=";", header=0, names=["Mouse", "Human"])
hk_genes = [g for g in hk["Human"].astype(str) if g in gpos]
hk_idx = np.array([gpos[g] for g in hk_genes])
print("HK matched:", len(hk_idx), flush=True)

X = a.X[:, keep_idx].tocsr().astype(np.float32)
obs = a.obs[["cell_type", "sample_id", "donor_id", "Region"]].reset_index(drop=True)

print("per-cell normalize_total(1e4) + log1p ...", flush=True)
lib = np.asarray(X.sum(axis=1)).ravel()
lib[lib == 0] = 1.0
X = sp.diags(1e4 / lib) @ X
X = X.tocsr()
X.data = np.log1p(X.data)

obs["group"] = obs["cell_type"].astype(str) + "@@" + obs["sample_id"].astype(str)
gcounts = obs.groupby("group").size()
elig = gcounts[gcounts >= MIN_CELLS].index
mask = obs["group"].isin(elig).values
print("eligible groups:", len(elig), "cells retained:", int(mask.sum()), flush=True)

Xg = X[mask]
obsg = obs[mask].reset_index(drop=True)
group_ids = obsg["group"].values
ugroups = np.array(sorted(set(group_ids)))
gcol = {g: i for i, g in enumerate(ugroups)}
rows = np.arange(len(group_ids))
cols = np.array([gcol[g] for g in group_ids])
G = sp.csr_matrix((np.ones(len(rows), dtype=np.float32), (cols, rows)),
                  shape=(len(ugroups), len(group_ids)))
ns = np.asarray(G.sum(axis=1)).ravel()
PB = (G @ Xg).toarray().astype(np.float64) / ns[:, None]
del Xg, G
print("pseudobulk matrix:", PB.shape, flush=True)

# HVG 2000 (seurat flavor on log data), excluding HK
adpb = sc.AnnData(PB)
sc.pp.highly_variable_genes(adpb, flavor="seurat", n_top_genes=2000)
hvg_mask = adpb.var["highly_variable"].values.copy()
hvg_mask[hk_idx] = False
id_idx = np.where(hvg_mask)[0]
print("identity genes (HVG2000 excl HK):", len(id_idx), flush=True)

all_idx = np.arange(PB.shape[1])


def metrics(va, vb):
    kn = js_divergence(va[hk_idx], vb[hk_idx])
    kf = js_divergence(va[id_idx], vb[id_idx])
    kn_f = max(kn, KN_FLOOR)
    omega = kf / kn_f
    rjs = js_divergence(va[all_idx], vb[all_idx])
    na = np.linalg.norm(va)
    nb = np.linalg.norm(vb)
    cos = 1.0 - float(va @ vb) / (na * nb + 1e-12)
    spear = 1.0 - float(spearmanr(va, vb).statistic)
    ta = set(np.argsort(va)[-200:])
    tb = set(np.argsort(vb)[-200:])
    jac = 1.0 - len(ta & tb) / len(ta | tb)
    return dict(k_n=kn, k_f=kf, omega=omega, raw_js=rjs, cosine=cos,
                spearman=spear, jaccard=jac)


rows_out = []

# --- functional: within-sample microglia vs CNS macrophage ---
ct_of = {g: g.split("@@")[0] for g in ugroups}
sm_of = {g: g.split("@@")[1] for g in ugroups}
samples = sorted(set(sm_of.values()))
n_func = 0
for s in samples:
    gm = f"microglial cell@@{s}"
    gc = f"central nervous system macrophage@@{s}"
    if gm in gcol and gc in gcol:
        i, j = gcol[gm], gcol[gc]
        m = metrics(PB[i], PB[j])
        m.update(pair_class="functional", sample=s,
                 n_a=float(ns[i]), n_b=float(ns[j]))
        rows_out.append(m)
        n_func += 1
print("functional pairs:", n_func, flush=True)

# --- neutral: random half-splits of the same (cell_type, sample) group ---
# halves >= 100 cells for microglia (matching the calibration design) and >= 50 for
# CNS macrophages (sparse class; still inside the recommended 50-200 cell window)
SPLIT_MIN_BY_TYPE = {"microglial cell": 200, "central nervous system macrophage": 100}
Xc = X[mask]  # per-cell normalized, eligible cells only
cell_group = cols  # group col index per retained cell
for ct in ["microglial cell", "central nervous system macrophage"]:
    smin = SPLIT_MIN_BY_TYPE[ct]
    cand = [gcol[g] for g in ugroups
            if ct_of[g] == ct and ns[gcol[g]] >= smin]
    got = 0
    ci = 0
    while got < N_SPLITS and cand:
        gi = cand[ci % len(cand)]
        ci += 1
        cell_rows = np.where(cell_group == gi)[0]
        if len(cell_rows) < smin:
            continue
        perm = RNG.permutation(len(cell_rows))
        half = len(cell_rows) // 2
        ra, rb = cell_rows[perm[:half]], cell_rows[perm[half:2 * half]]
        va = np.asarray(Xc[ra].mean(axis=0)).ravel()
        vb = np.asarray(Xc[rb].mean(axis=0)).ravel()
        m = metrics(va, vb)
        m.update(pair_class=f"neutral_{ct}", sample=ugroups[gi].split("@@")[1],
                 n_a=float(len(ra)), n_b=float(len(rb)))
        rows_out.append(m)
        got += 1
    print(ct, "neutral splits:", got, "from", len(cand), "eligible groups", flush=True)

df = pd.DataFrame(rows_out)
df.to_csv(OUT_CSV, index=False)
print("wrote", OUT_CSV, df.shape, flush=True)

# --- summary ---
func = df[df.pair_class == "functional"]
neut = df[df.pair_class != "functional"]
metric_cols = ["omega", "k_n", "k_f", "raw_js", "cosine", "spearman", "jaccard"]
lines = []
lines.append("nc50 brain-atlas microglia validation (Human Brain Cell Atlas v1.0, Microglia supercluster)")
lines.append(f"h5ad nuclei: {a.shape[0]}, genes: {a.shape[1]}; HK matched: {len(hk_idx)}; HVG2000 excl HK: {len(id_idx)}")
lines.append(f"eligible (cell_type, sample) groups (>= {MIN_CELLS} cells): {len(elig)}")
lines.append(f"functional within-sample pairs: {len(func)}; neutral half-splits: {len(neut)} "
             f"(per type {N_SPLITS}; group-size floors {SPLIT_MIN_BY_TYPE})")
lines.append(f"pipeline: per-cell normalize_total(1e4)+log1p, group means; kn_floor={KN_FLOOR}; seed 42")
lines.append("")
lines.append("metric, functional mean+-sd, neutral mean+-sd, MWU P, AUC(functional>neutral)")
summary = {}
for mc in metric_cols:
    f, n = func[mc].values, neut[mc].values
    p = mannwhitneyu(f, n, alternative="greater").pvalue
    # exact rank AUC
    ranks = pd.Series(np.concatenate([f, n])).rank().values[:len(f)]
    auc = (ranks.sum() - len(f) * (len(f) + 1) / 2) / (len(f) * len(n))
    summary[mc] = dict(func_mean=float(f.mean()), func_sd=float(f.std(ddof=1)),
                       neut_mean=float(n.mean()), neut_sd=float(n.std(ddof=1)),
                       mwu_p=float(p), auc=float(auc))
    lines.append(f"{mc}: {f.mean():.4f}+-{f.std(ddof=1):.4f} vs {n.mean():.4f}+-{n.std(ddof=1):.4f}; "
                 f"P={p:.3e}; AUC={auc:.3f}")
with open(OUT_TXT, "w") as fh:
    fh.write("\n".join(lines) + "\n")
print("\n".join(lines), flush=True)
print("DONE", flush=True)
