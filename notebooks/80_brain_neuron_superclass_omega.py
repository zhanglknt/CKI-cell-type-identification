"""
CKI Siletti Neuron Superclass Omega (A task)
=============================================
Runs the 08c-identical observed-omega pipeline on the per-supercluster
neuron slices from the Siletti collection, to test whether region-drift
omega is stronger in neuronal superclasses (Siletti's own region signal
is concentrated in neurons) — the cell-type class the Nonneurons.h5ad
analysis could not see.

Two levels per supercluster file:
  1. superclass level: region x region pairs within the supercluster
     (directly comparable to the 08c/08d non-neuronal per-CT omega)
  2. subcluster level: subcluster_id x region groups (finer granularity,
     MIN_NUCLEI filter) — which neuronal subclusters drift most

Pipeline (identical to 08c/08d observed path):
  HK 1,115 (HRT) + top-5000 non-HK HVG by mean expression;
  pseudobulk = mean -> norm 1e4 -> log1p;
  kn = JS on HK; kf = JS on top-200 |diff| non-HK genes (per pair);
  omega = kf / kn.

Outputs:
  results/brain_neuron_superclass_omega.csv   (superclass-level pairs)
  results/brain_neuron_subcluster_omega.csv   (subcluster-level pairs)
  results/brain_neuron_report.md
"""

import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)

import numpy as np
import pandas as pd
import scanpy as sc
import h5py
from scipy.sparse import issparse, csr_matrix
from cki.core import js_divergence

# Extraction + vectorized pairwise JS (verbatim from 77, isolated namespace)
SRC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "77_brain_hallmark_program_omega.py"),
           encoding="utf-8").read()
_NS = {"__file__": os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "77_brain_hallmark_program_omega.py")),
       "__name__": "not_main"}
exec(SRC.split("# === Config (identical to 08c) ===")[0], _NS)
extract_csr_from_backed = _NS["extract_csr_from_backed"]
pairwise_js = _NS["pairwise_js"]


# === Config ===
RANDOM_SEED = 42
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000

FILES = {
    "MGE interneuron": DATA_DIR / "brain" / "neurons" / "MGE_interneuron.h5ad",
    "Thalamic excitatory": DATA_DIR / "brain" / "neurons" / "Thalamic_excitatory.h5ad",
    "Upper-layer intratelencephalic": DATA_DIR / "brain" / "neurons"
                                       / "Upper-layer_intratelencephalic.h5ad",
}

OUT_SC = Path("results/brain_neuron_superclass_omega.csv")
OUT_SUB = Path("results/brain_neuron_subcluster_omega.csv")
OUT_MD = Path("results/brain_neuron_report.md")

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"HRT Atlas: {len(hk_human)} human HK genes")


def region_pair_omegas(PB, region_order, hk_r, nh_r):
    """All upper-triangle pair omegas (08c observed path, exact)."""
    n = len(region_order)
    out = []
    for i in range(n):
        for j in range(i + 1, n):
            pi, pj = PB[i], PB[j]
            kn = js_divergence(pi[hk_r], pj[hk_r])
            ad = np.abs(pi - pj)[nh_r]
            top_n = min(N_TOP_KF, len(ad))
            tl = np.argpartition(ad, -top_n)[-top_n:]
            tg = nh_r[tl]
            kf = js_divergence(pi[tg], pj[tg])
            out.append((kf / kn if kn > 0 else np.inf, kn, kf))
    return out


sc_rows = []
sub_rows = []
sc_summary = []

for sc_name, path in FILES.items():
    print("\n" + "=" * 60)
    print(f"Supercluster: {sc_name}")
    print("=" * 60)
    if not path.exists():
        print("  MISSING — skip")
        continue
    adata = sc.read_h5ad(path, backed='r')
    N_GENES, N_CELLS = adata.n_vars, adata.n_obs
    print(f"  shape: {N_CELLS} cells x {N_GENES} genes")

    gene_symbols = adata.var["Gene"].tolist()
    hk_global = np.array(sorted({i for i, s in enumerate(gene_symbols)
                                 if pd.notna(s) and s in hk_human}), dtype=int)
    print(f"  HK matched: {len(hk_global)}")

    # global means for HVG
    gene_sums = np.zeros(N_GENES)
    B = 50000
    for st in range(0, N_CELLS, B):
        Xb = adata[st:st + B].X
        gene_sums += (np.array(Xb.sum(axis=0)).flatten() if issparse(Xb)
                      else Xb.sum(axis=0))
    means = gene_sums / N_CELLS
    m = np.ones(N_GENES, bool)
    m[hk_global] = False
    nm = means.copy()
    nm[~m] = -np.inf
    hvg = np.argsort(nm)[-N_HVG:][::-1]
    keep = np.sort(np.union1d(hk_global, hvg))
    is_hk = np.isin(keep, hk_global)
    hk_r = np.where(is_hk)[0]
    nh_r = np.where(~is_hk)[0]
    print(f"  reduced: {len(keep)} (HK {len(hk_r)} + non-HK {len(nh_r)})")

    roi = np.asarray(adata.obs['roi'].values).astype(str)   # Categorical guard!

    # ---- Level 1: superclass region pairs ----
    region_counts = pd.Series(roi).value_counts()
    regions_ok = sorted(region_counts[region_counts >= MIN_REGION_N].index)
    mask = np.isin(roi, regions_ok)
    gidx = np.where(mask)[0]
    print(f"  superclass level: {len(regions_ok)} regions "
          f"(>={MIN_REGION_N} cells), {len(gidx)} cells")
    Xs = extract_csr_from_backed(str(path), gidx, keep, N_GENES)
    rois = roi[gidx]
    order = sorted(regions_ok)
    PB = np.zeros((len(order), len(keep)), dtype=np.float64)
    for ri, r in enumerate(order):
        rows = np.where(rois == r)[0]
        raw = np.array(Xs[rows].mean(axis=0)).flatten()
        tot = raw.sum()
        PB[ri] = np.log1p(raw / tot * 1e4) if tot > 0 else raw
    del Xs
    gc.collect()
    om = region_pair_omegas(PB, order, hk_r, nh_r)
    om_arr = np.array([o[0] for o in om])
    print(f"    {len(om)} pairs: mean omega={om_arr.mean():.2f} "
          f"median={np.median(om_arr):.2f} max={om_arr.max():.2f}")
    sc_summary.append((sc_name, len(om), om_arr.mean(), np.median(om_arr),
                       om_arr.max()))
    k = 0
    for i in range(len(order)):
        for j in range(i + 1, len(order)):
            o, kn, kf = om[k]
            sc_rows.append({"supercluster": sc_name, "region_a": order[i],
                            "region_b": order[j], "omega": o, "kn": kn,
                            "kf": kf})
            k += 1

    # ---- Level 2: subcluster x region ----
    sub = np.asarray(adata.obs['subcluster_id'].values).astype(str)
    dfm = pd.DataFrame({"roi": roi, "sub": sub})
    grp = dfm.groupby(["roi", "sub"]).size().reset_index(name="n")
    grp = grp[(grp.n >= MIN_NUCLEI) & grp.roi.isin(regions_ok)]
    subs = sorted(grp["sub"].unique())
    print(f"  subcluster level: {len(subs)} subclusters "
          f"(>= {MIN_NUCLEI} cells/region-group)")
    for s in subs:
        regs = sorted(grp[grp["sub"] == s].roi.unique())
        n_pairs = len(regs) * (len(regs) - 1) // 2
        if n_pairs < 5:
            continue
        smask = np.isin(roi, regs) & (sub == s)
        sidx = np.where(smask)[0]
        Xc = extract_csr_from_backed(str(path), sidx, keep, N_GENES)
        sroi = roi[sidx]
        PBs = np.zeros((len(regs), len(keep)), dtype=np.float64)
        for ri, r in enumerate(regs):
            rows = np.where(sroi == r)[0]
            raw = np.array(Xc[rows].mean(axis=0)).flatten()
            tot = raw.sum()
            PBs[ri] = np.log1p(raw / tot * 1e4) if tot > 0 else raw
        del Xc
        gc.collect()
        oms = region_pair_omegas(PBs, regs, hk_r, nh_r)
        oa = np.array([o[0] for o in oms])
        for (o, kn, kf), (i, j) in zip(oms, [(i, j) for i in range(len(regs))
                                             for j in range(i + 1, len(regs))]):
            sub_rows.append({"supercluster": sc_name, "subcluster": s,
                             "region_a": regs[i], "region_b": regs[j],
                             "omega": o, "kn": kn, "kf": kf})
        print(f"    {s}: {len(regs)} regions {n_pairs} pairs "
              f"mean omega={oa.mean():.2f}")

# === Save + report ===
df_sc = pd.DataFrame(sc_rows)
df_sc.to_csv(OUT_SC, index=False)
df_sub = pd.DataFrame(sub_rows)
df_sub.to_csv(OUT_SUB, index=False)

# non-neuronal reference (08d authoritative per-CT means)
ref = pd.read_csv("results/brain_bs_null_observed_pairs.csv")
ref_mean = ref.groupby("cell_type")["omega"].mean()

lines = ["# Siletti Neuron Superclass Omega (08c pipeline)", "",
         "## Superclass-level region pairs", "",
         "| supercluster | n_pairs | mean omega | median | max |",
         "|---|---|---|---|---|"]
for name, n, mu, med, mx in sc_summary:
    lines.append(f"| {name} | {n} | {mu:.2f} | {med:.2f} | {mx:.2f} |")
lines += ["", "## Reference: non-neuronal per-CT mean omega (08d)", "",
          "| cell_type | mean omega |", "|---|---|"]
for ct, mu in ref_mean.sort_values(ascending=False).items():
    lines.append(f"| {ct} | {mu:.2f} |")
lines += ["", "## Subcluster-level summary (top 15 by mean omega)", "",
          "| supercluster | subcluster | n_pairs | mean omega |",
          "|---|---|---|---|"]
if len(df_sub):
    summ = (df_sub.groupby(["supercluster", "subcluster"])["omega"]
            .agg(["count", "mean"]).reset_index())
    summ.columns = ["supercluster", "subcluster", "n_pairs", "mean_omega"]
    for _, r in summ.nlargest(15, "mean_omega").iterrows():
        lines.append(f"| {r.supercluster} | {r.subcluster} | "
                     f"{r.n_pairs} | {r.mean_omega:.2f} |")
OUT_MD.write_text("\n".join(lines), encoding="utf-8")

print("\n" + "=" * 60)
print(f"Saved: {OUT_SC} ({len(df_sc)}), {OUT_SUB} ({len(df_sub)}), {OUT_MD}")
print("DONE")
