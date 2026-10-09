"""
CKI Neuron Superclass Block-Shuffle Null (A-stat, #1138)
========================================================
Adds statistical control to the neuron-superclass finding (script 80):
the 08d sample-level block-shuffle null, applied to the three neuronal
superclasses.

Design (08d-identical mechanism):
- Blocks = 10x libraries (obs['sample_id']); each sample is nested within
  exactly one roi (verified: max 1 region per sample in all 3 files).
- Permutation: shuffle the sample -> region assignment vector
  (preserves the observed per-region sample-count multiset), recompute
  region pseudobulks as cell-count-weighted means of sample raw means,
  norm-1e4 log1p, recompute all same-superclass cross-region pair omega.
- B = 1000; one-sided upper-tail p on mean omega per superclass.
- Gene set: per-file HK (HRT Atlas) + top-5000 non-HK HVG by mean --
  identical to script 80, so observed omegas must reproduce
  results/brain_neuron_superclass_omega.csv (x-check, tol 1e-3).

Second component: Wilcoxon rank-sum (Mann-Whitney U) test of the
neuronal pair-omega distribution (2,995 pairs) vs the non-neuronal
reference landscape (08d, 31,764 pairs), one-sided greater, with
rank-biserial effect size and common-language probability.

Outputs:
  results/brain_neuron_blockshuffle.csv        per-superclass test summary
  results/brain_neuron_blockshuffle_null_means.npy  (3 x B) null mean omegas
  results/brain_neuron_blockshuffle_report.md  full report incl. Wilcoxon
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
from scipy.stats import mannwhitneyu
from cki.core import js_divergence

# === Config (08d/80 convention) ===
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
B_PERM = 1000
if "--b" in sys.argv:
    B_PERM = int(sys.argv[sys.argv.index("--b") + 1])
RANDOM_SEED = 42
BATCH = 5000

FILES = {
    "MGE interneuron": DATA_DIR / "brain" / "neurons" / "MGE_interneuron.h5ad",
    "Thalamic excitatory": DATA_DIR / "brain" / "neurons" / "Thalamic_excitatory.h5ad",
    "Upper-layer intratelencephalic": DATA_DIR / "brain" / "neurons"
                                       / "Upper-layer_intratelencephalic.h5ad",
}

OUT_CSV = Path("results/brain_neuron_blockshuffle.csv")
OUT_NPY = Path("results/brain_neuron_blockshuffle_null_means.npy")
OUT_MD = Path("results/brain_neuron_blockshuffle_report.md")

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


def region_pbs_from_samples(assign_idx, weights, means):
    """08d-identical: assign_idx: sample -> region index; weighted mean
    of sample raw means -> norm 1e4 -> log1p. Returns (n_regions, G)."""
    n_r = int(assign_idx.max()) + 1 if len(assign_idx) else 0
    pbs = np.zeros((n_r, means.shape[1]), dtype=np.float64)
    for r in range(n_r):
        mask = assign_idx == r
        if not mask.any():
            continue
        w = weights[mask]
        pb_raw = (means[mask] * w[:, None]).sum(axis=0) / w.sum()
        tot = pb_raw.sum()
        pbs[r] = np.log1p(pb_raw / tot * 1e4) if tot > 0 else pb_raw
    return pbs


def pair_omegas(PB, hk_r, nh_r):
    """08d-identical pair omega over all upper-triangle region pairs."""
    n = PB.shape[0]
    out = np.empty(n * (n - 1) // 2, dtype=np.float64)
    k = 0
    for i in range(n):
        pi = PB[i]
        for j in range(i + 1, n):
            pj = PB[j]
            kn = js_divergence(pi[hk_r], pj[hk_r])
            ad = np.abs(pi - pj)[nh_r]
            top_n = min(N_TOP_KF, len(ad))
            tl = np.argpartition(ad, -top_n)[-top_n:]
            tg = nh_r[tl]
            kf = js_divergence(pi[tg], pj[tg])
            out[k] = kf / kn if kn > 1e-15 else np.inf
            k += 1
    return out


rng = np.random.RandomState(RANDOM_SEED)
rows = []
null_all = {}

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
        samp = read_cat(f["obs"], "sample_id").astype(str)
        print(f"  cells={n_cells} genes={n_genes}")

        # region filter (80 convention: >= MIN_REGION_N cells of this sc)
        region_counts = pd.Series(roi).value_counts()
        regions_ok = sorted(region_counts[region_counts >= MIN_REGION_N].index)
        n_r = len(regions_ok)
        region_idx = {r: i for i, r in enumerate(regions_ok)}
        roi_ok = np.isin(roi, regions_ok)
        print(f"  regions passing >={MIN_REGION_N} cells: {n_r} "
              f"({n_r*(n_r-1)//2} pairs)")

        # sample table (sample codes over ALL cells; ok-filter applied by
        # roi_ok mask inside the streaming loop)
        uniq_s, samp_code = np.unique(samp, return_inverse=True)
        samp_region = np.array([region_idx.get(r, -1) for r in roi])
        n_samples = len(uniq_s)
        print(f"  blocks (samples): {n_samples}")

        # single streaming pass: global gene sums + per-sample full-gene sums
        gene_sums = np.zeros(n_genes, dtype=np.float64)
        s_sums = np.zeros((n_samples, n_genes), dtype=np.float64)
        s_counts = np.zeros(n_samples, dtype=np.int64)
        t0 = time.time()
        for start in range(0, n_cells, BATCH):
            end = min(start + BATCH, n_cells)
            lo, hi = int(indptr[start]), int(indptr[end])
            idx = indices[lo:hi]
            dat = data[lo:hi].astype(np.float64)
            np.add.at(gene_sums, idx, dat)
            # per-cell scatter into sample sums (cells outside ok regions skipped)
            for ci in range(start, end):
                if roi_ok[ci]:
                    s = samp_code[ci]
                    r0, r1 = int(indptr[ci]) - lo, int(indptr[ci + 1]) - lo
                    if r1 > r0:
                        np.add.at(s_sums[s], idx[r0:r1], dat[r0:r1])
                        s_counts[s] += 1
        print(f"  streaming pass done in {time.time()-t0:.0f}s")

    # HK + HVG (80 convention: global means over ALL cells in file)
    hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                                 if s in hk_human}), dtype=int)
    means_all = gene_sums / n_cells
    m = np.ones(n_genes, bool)
    m[hk_global] = False
    nm = means_all.copy()
    nm[~m] = -np.inf
    hvg = np.argsort(nm)[-N_HVG:][::-1]
    keep = np.sort(np.union1d(hk_global, hvg))
    is_hk = np.isin(keep, hk_global)
    hk_r = np.where(is_hk)[0]
    nh_r = np.where(~is_hk)[0]
    print(f"  HK={len(hk_global)} reduced={len(keep)} "
          f"(HK {len(hk_r)} + non-HK {len(nh_r)})")

    # sample means over reduced set; drop empty samples
    s_means = (s_sums[:, keep] / np.maximum(s_counts, 1)[:, None])
    ok_s = s_counts > 0
    s_means = s_means[ok_s]
    s_weights = s_counts[ok_s].astype(np.float64)
    # region per sample (each sample nested in exactly one roi;
    # scatter over its ok cells — all share the same region)
    region_per_code = np.zeros(n_samples, dtype=int)
    region_per_code[samp_code] = samp_region
    s_region = region_per_code[ok_s]
    n_s = len(s_weights)
    n_pairs = n_r * (n_r - 1) // 2
    print(f"  usable blocks: {n_s} (median cells/sample="
          f"{np.median(s_weights):.0f})")

    # observed
    obs_pbs = region_pbs_from_samples(s_region, s_weights, s_means)
    obs_omegas = pair_omegas(obs_pbs, hk_r, nh_r)
    obs_mean = float(obs_omegas.mean())
    obs_median = float(np.median(obs_omegas))
    print(f"  Observed: mean={obs_mean:.3f} median={obs_median:.3f} "
          f"max={obs_omegas.max():.3f}")

    # ---- block-shuffle null ----
    null_means = np.empty(B_PERM, dtype=np.float64)
    t0 = time.time()
    for b in range(B_PERM):
        perm = s_region[rng.permutation(n_s)]
        pb = region_pbs_from_samples(perm, s_weights, s_means)
        w = pair_omegas(pb, hk_r, nh_r)
        null_means[b] = w.mean()
        if (b + 1) % 100 == 0:
            el = time.time() - t0
            print(f"    perm {b+1}/{B_PERM} elapsed={el:.0f}s "
                  f"ETA={el/(b+1)*(B_PERM-b-1):.0f}s")
    p_val = (np.sum(null_means >= obs_mean) + 1) / (B_PERM + 1)
    null_mu, null_sd = float(null_means.mean()), float(null_means.std())
    ses = (obs_mean - null_mu) / null_sd if null_sd > 1e-12 else 0.0
    print(f"  null mean={null_mu:.3f} sd={null_sd:.3f} "
          f"p={p_val:.4f} SES={ses:.2f}")
    print(f"  file done in {time.time()-t_file:.0f}s total")

    rows.append({
        "supercluster": sc_name, "n_regions": n_r, "n_pairs": n_pairs,
        "n_cells_ok": int(s_weights.sum()), "n_blocks": n_s,
        "omega_mean": obs_mean, "omega_median": obs_median,
        "omega_max": float(obs_omegas.max()),
        "null_mean": null_mu, "null_sd": null_sd,
        "p_value": p_val, "SES": ses,
    })
    null_all[sc_name] = null_means

    # x-check observed vs script 80
    ref = pd.read_csv("results/brain_neuron_superclass_omega.csv")
    ref = ref[ref.supercluster == sc_name]
    if len(ref) == n_pairs:
        d = np.abs(np.sort(ref.omega.values) - np.sort(obs_omegas))
        print(f"  X-CHECK vs 80: n={len(ref)} max|d_omega|={d.max():.2e}")
    del s_sums, s_means, obs_pbs, obs_omegas
    gc.collect()

# ============================================================
# Wilcoxon rank-sum: neurons vs non-neurons (08d reference)
# ============================================================
print("\n" + "=" * 60)
print("Wilcoxon rank-sum: neuronal vs non-neuronal pair omega")
print("=" * 60)
neu = pd.read_csv("results/brain_neuron_superclass_omega.csv")
non = pd.read_csv("results/brain_bs_null_observed_pairs.csv")
astro = non[non.cell_type == "Astrocyte"]
non_all = non["omega"].values
neu_all = neu["omega"].values

def mw(a, b, label):
    u, p = mannwhitneyu(a, b, alternative="greater")
    rb = 2 * u / (len(a) * len(b)) - 1  # rank-biserial
    cl = u / (len(a) * len(b))          # P(a > b)
    print(f"  {label}: U={u:.0f} p={p:.3e} rank-biserial={rb:.3f} "
          f"P(neuron>ref)={cl:.4f}")
    return {"comparison": label, "n_a": len(a), "n_b": len(b),
            "U": float(u), "p_value": float(p),
            "rank_biserial": float(rb), "P_a_gt_b": float(cl)}

mw_rows = [mw(neu_all, non_all, "neurons vs non-neurons (all)")]
for sc in FILES:
    mw_rows.append(mw(neu[neu.supercluster == sc]["omega"].values, non_all,
                      f"{sc} vs non-neurons"))
mw_rows.append(mw(neu_all, astro["omega"].values, "neurons vs astrocytes"))
mw_rows.append(mw(astro["omega"].values, non[non.cell_type != "Astrocyte"]
                  ["omega"].values, "astrocytes vs other non-neurons"))

med_non = np.median(non_all)
med_non_ex_astro = np.median(
    non[non.cell_type != "Astrocyte"]["omega"].values)
print(f"  medians: neurons={np.median(neu_all):.2f} "
      f"non-neurons={med_non:.2f} non-neurons(ex-astro)={med_non_ex_astro:.2f} "
      f"astrocytes={astro.omega.median():.2f}")

# ============================================================
# Save
# ============================================================
df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)
np.save(OUT_NPY, np.stack([null_all[r["supercluster"]] for r in rows]))
mw_df = pd.DataFrame(mw_rows)

lines = ["# Neuron Superclass Block-Shuffle Null (A-stat)", "",
         "08d-identical sample-level block-shuffle (sample_id -> roi,",
         "per-region sample-count multiset preserved, B=1,000, seed 42).", "",
         "## Per-superclass test (one-sided upper on mean omega)", "",
         "| supercluster | regions | pairs | blocks | obs mean | null mean |"
         " null sd | SES | p |", "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(
        f"| {r['supercluster']} | {r['n_regions']} | {r['n_pairs']} | "
        f"{r['n_blocks']} | {r['omega_mean']:.2f} | {r['null_mean']:.2f} | "
        f"{r['null_sd']:.2f} | {r['SES']:.1f} | {r['p_value']:.4f} |")
lines += ["", "## Wilcoxon rank-sum (one-sided greater)", "",
          "| comparison | n_a | n_b | U | p | rank-biserial | P(a>b) |",
          "|---|---|---|---|---|---|---|"]
for r in mw_rows:
    lines.append(f"| {r['comparison']} | {r['n_a']} | {r['n_b']} | "
                 f"{r['U']:.0f} | {r['p_value']:.2e} | "
                 f"{r['rank_biserial']:.3f} | {r['P_a_gt_b']:.4f} |")
lines += ["", f"Medians: neurons {np.median(neu_all):.2f} | "
          f"non-neurons {med_non:.2f} | non-neurons ex-astrocytes "
          f"{med_non_ex_astro:.2f} | astrocytes {astro.omega.median():.2f}",
          ""]
OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"\nSaved: {OUT_CSV}\nSaved: {OUT_NPY}\nSaved: {OUT_MD}")
print("DONE")
