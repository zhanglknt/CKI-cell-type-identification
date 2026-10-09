"""
CKI Siletti Neuron Superclass Omega (A task) — streaming v2
============================================================
v1 (extract_csr_from_backed) materializes a full CSR per group; on the
Upper-layer intratelencephalic file (455k cells, high nnz) it exceeds
the 15.7 GB system RAM and thrashes. v2 computes every pseudobulk in a
SINGLE streaming pass per file with O(groups x genes) memory:

  - superclass level: per-region sums (region = roi)
  - subcluster level: per-(subcluster, region) sums

Both accumulators are filled in one pass over the CSR data (batched
contiguous h5py reads). The omega pipeline itself is unchanged
(08c-identical: HK 1,115 + top-5000 HVG, norm-1e4 log1p pseudobulks,
kn = JS(HK), kf = JS(top-200 |diff|), omega = kf/kn).

Outputs:
  results/brain_neuron_superclass_omega.csv
  results/brain_neuron_subcluster_omega.csv
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
import h5py
from cki.core import js_divergence

# === Config ===
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
BATCH = 5000  # cells per h5py contiguous read

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


def read_cat(obj, name):
    g = obj[name]
    if isinstance(g, h5py.Dataset):
        return np.array([x.decode() if isinstance(x, bytes) else str(x)
                         for x in g[:]], dtype=object)
    cats = [x.decode() if isinstance(x, bytes) else str(x)
            for x in g["categories"][:]]
    return np.array(cats, dtype=object)[g["codes"][:]]


def pb_from_sum(s, n):
    raw = s / max(n, 1)
    tot = raw.sum()
    return np.log1p(raw / tot * 1e4) if tot > 0 else raw


def region_pair_omegas(PB, hk_r, nh_r):
    n = PB.shape[0]
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
    t_file = time.time()
    with h5py.File(path, "r") as f:
        X = f["X"]
        indptr = X["indptr"][:]
        data = X["data"]
        indices = X["indices"]
        n_cells = len(indptr) - 1
        var_gene = read_cat(f["var"], "Gene").astype(str)
        n_genes = len(var_gene)
        roi = read_cat(f["obs"], "roi").astype(str)
        sub = read_cat(f["obs"], "subcluster_id").astype(str)
        print(f"  cells={n_cells} genes={n_genes}")

        # HK + HVG (batched global means — never materialize the full X)
        hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                                     if s in hk_human}), dtype=int)
        gene_sums = np.zeros(n_genes, dtype=np.float64)
        t0 = time.time()
        for start in range(0, n_cells, BATCH):
            end = min(start + BATCH, n_cells)
            lo, hi = int(indptr[start]), int(indptr[end])
            np.add.at(gene_sums, indices[lo:hi],
                      data[lo:hi].astype(np.float64))
        print(f"  gene means pass: {time.time()-t0:.0f}s")
        means = gene_sums / n_cells
        m = np.ones(n_genes, bool)
        m[hk_global] = False
        nm = means.copy()
        nm[~m] = -np.inf
        hvg = np.argsort(nm)[-N_HVG:][::-1]
        keep = np.sort(np.union1d(hk_global, hvg))
        is_hk = np.isin(keep, hk_global)
        hk_r = np.where(is_hk)[0]
        nh_r = np.where(~is_hk)[0]
        K = len(keep)
        print(f"  HK={len(hk_global)} reduced={K} "
              f"(HK {len(hk_r)} + non-HK {len(nh_r)})")

        # groups
        region_counts = pd.Series(roi).value_counts()
        regions_ok = sorted(region_counts[region_counts >= MIN_REGION_N].index)
        roi_ok = np.isin(roi, regions_ok)
        dfm = pd.DataFrame({"roi": roi, "sub": sub, "ok": roi_ok})
        grp = dfm[dfm.ok].groupby(["roi", "sub"]).size().reset_index(name="n")
        grp = grp[grp.n >= MIN_NUCLEI]
        sub_ok = grp.groupby("sub")["roi"].nunique()
        subs_keep = sorted(sub_ok[sub_ok >= 3].index)
        print(f"  superclass: {len(regions_ok)} regions; "
              f"subclusters with >=3 regions: {len(subs_keep)}")

        # group key arrays
        region_idx = {r: i for i, r in enumerate(regions_ok)}
        sc_key = np.where(roi_ok,
                          [region_idx.get(r, -1) for r in roi], -1)
        subpair = {}
        for i, s in enumerate(subs_keep):
            for r in grp[grp["sub"] == s].roi.unique():
                subpair[(s, r)] = i
        sub_key = np.array([subpair.get((s, r), -1)
                            for s, r in zip(sub, roi)], dtype=int)
        n_subgroups = len(subs_keep) and max(
            [len(v) for v in [set(grp[grp['sub'] == s].roi)
                              for s in subs_keep]]) or 0
        # simpler: enumerate actual (sub, region) groups
        sub_groups = sorted(subpair.keys())
        subpair = {k: i for i, k in enumerate(sub_groups)}
        sub_key = np.array([subpair.get((s, r), -1)
                            for s, r in zip(sub, roi)], dtype=int)
        n_subgroups = len(sub_groups)

        # streaming accumulation (batched reads, O(groups x genes) memory)
        gene_map = np.full(n_genes, -1, dtype=np.int32)
        gene_map[keep] = np.arange(K, dtype=np.int32)
        sc_sums = np.zeros((len(regions_ok), K), dtype=np.float64)
        sc_counts = np.zeros(len(regions_ok), dtype=np.int64)
        sub_sums = np.zeros((n_subgroups, K), dtype=np.float64)
        sub_counts = np.zeros(n_subgroups, dtype=np.int64)

        t0 = time.time()
        for start in range(0, n_cells, BATCH):
            end = min(start + BATCH, n_cells)
            lo, hi = int(indptr[start]), int(indptr[end])
            idx = indices[lo:hi]
            dat = data[lo:hi].astype(np.float64)
            mapped = gene_map[idx]
            ok = mapped >= 0
            # per cell scatter
            for ci in range(start, end):
                g1, g2 = sc_key[ci], sub_key[ci]
                r0, r1 = int(indptr[ci]) - lo, int(indptr[ci + 1]) - lo
                if g1 >= 0:
                    okm = ok[r0:r1]
                    if okm.any():
                        sc_sums[g1, mapped[r0:r1][okm]] += dat[r0:r1][okm]
                    sc_counts[g1] += 1
                if g2 >= 0:
                    okm = ok[r0:r1]
                    if okm.any():
                        sub_sums[g2, mapped[r0:r1][okm]] += dat[r0:r1][okm]
                    sub_counts[g2] += 1
        print(f"  streaming pass done in {time.time()-t0:.0f}s")

    # ---- superclass level ----
    order = regions_ok
    PB = np.stack([pb_from_sum(sc_sums[i], sc_counts[i])
                   for i in range(len(order))])
    om = region_pair_omegas(PB, hk_r, nh_r)
    om_arr = np.array([o[0] for o in om])
    print(f"  superclass: {len(om)} pairs mean={om_arr.mean():.2f} "
          f"median={np.median(om_arr):.2f} max={om_arr.max():.2f}")
    sc_summary.append((sc_name, len(om), om_arr.mean(),
                       np.median(om_arr), om_arr.max()))
    k = 0
    for i in range(len(order)):
        for j in range(i + 1, len(order)):
            o, kn, kf = om[k]
            sc_rows.append({"supercluster": sc_name, "region_a": order[i],
                            "region_b": order[j], "omega": o, "kn": kn,
                            "kf": kf})
            k += 1
    del PB, sc_sums
    gc.collect()

    # ---- subcluster level ----
    # per (sub, region) pseudobulks -> per-sub pair omegas
    for si, s in enumerate(subs_keep):
        regs = [r for (ss, r) in sub_groups if ss == s]
        regs = sorted(regs)
        if len(regs) < 3:
            continue
        rows_idx = [subpair[(s, r)] for r in regs]
        PBs = np.stack([pb_from_sum(sub_sums[g], sub_counts[g])
                        for g in rows_idx])
        oms = region_pair_omegas(PBs, hk_r, nh_r)
        oa = np.array([o[0] for o in oms])
        k = 0
        for i in range(len(regs)):
            for j in range(i + 1, len(regs)):
                o, kn, kf = oms[k]
                sub_rows.append({"supercluster": sc_name, "subcluster": s,
                                 "region_a": regs[i], "region_b": regs[j],
                                 "omega": o, "kn": kn, "kf": kf})
                k += 1
        print(f"    {s}: {len(regs)} regions {len(oms)} pairs "
              f"mean={oa.mean():.2f}")
    del sub_sums
    gc.collect()
    print(f"  file done in {time.time()-t_file:.0f}s total")

# === Save + report ===
df_sc = pd.DataFrame(sc_rows)
df_sc.to_csv(OUT_SC, index=False)
df_sub = pd.DataFrame(sub_rows)
df_sub.to_csv(OUT_SUB, index=False)

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
