"""
CKI Neuron Superclass: omega = k_f / k_n decomposition + donor robustness
==========================================================================
nc75 P0-3 (#1179). Extends script 83 (block-shuffle null, A-stat) with:

1. Component decomposition: for each neuronal superclass, report the
   observed log-omega gap over the block-shuffle null split into its
   numerator (log k_f) and denominator (log k_n) shares:
       mean log w = mean log kf - mean log kn  (exact identity)
   -> share_f  = (obs - null) mean log kf / (obs - null) mean log w
   -> share_n  = -(obs - null) mean log kn / (obs - null) mean log w
   Also median k_f and median k_n, observed vs null.

2. Donor-stratified block-shuffle (B=1,000, seed 43): region labels are
   permuted among samples WITHIN each donor only (donor composition of
   every region set preserved), guarding against donor-region confounding.

3. Leave-one-donor-out (LODO): observed mean omega recomputed after
   dropping each donor in turn (4 donors per file).

Loop A additionally recomputes the standard null mean-omega distribution
as a cross-check against results/brain_neuron_blockshuffle_null_means.npy.

Outputs:
  results/nc75_brain_neuron_decomposition.csv
  results/nc75_brain_neuron_decomposition.md
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

MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
B_PERM = 1000
if "--b" in sys.argv:
    B_PERM = int(sys.argv[sys.argv.index("--b") + 1])
SEED_STD, SEED_STRAT = 42, 43
BATCH = 5000
EPS = 1e-15

FILES = {
    "MGE interneuron": DATA_DIR / "brain" / "neurons" / "MGE_interneuron.h5ad",
    "Thalamic excitatory": DATA_DIR / "brain" / "neurons" / "Thalamic_excitatory.h5ad",
    "Upper-layer intratelencephalic": DATA_DIR / "brain" / "neurons"
                                       / "Upper-layer_intratelencephalic.h5ad",
}

OUT_CSV = Path("results/nc75_brain_neuron_decomposition.csv")
OUT_MD = Path("results/nc75_brain_neuron_decomposition.md")
REF_NPY = Path("results/brain_neuron_blockshuffle_null_means.npy")

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


def pair_components(PB, hk_r, nh_r):
    """Returns (omega, log_kf, log_kn) over all upper-triangle pairs."""
    n = PB.shape[0]
    m = n * (n - 1) // 2
    w_out = np.empty(m); lkf_out = np.empty(m); lkn_out = np.empty(m)
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
            w_out[k] = kf / kn if kn > EPS else np.inf
            lkf_out[k] = np.log(max(kf, EPS))
            lkn_out[k] = np.log(max(kn, EPS))
            k += 1
    return w_out, lkf_out, lkn_out


rows = []
ref_null = np.load(REF_NPY) if REF_NPY.exists() else None

for fi, (sc_name, path) in enumerate(FILES.items()):
    print("\n" + "=" * 60)
    print(f"Supercluster: {sc_name}")
    print("=" * 60)
    if not path.exists():
        print("  MISSING - skip")
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
        donor = read_cat(f["obs"], "donor_id").astype(str)
        print(f"  cells={n_cells} genes={n_genes}")

        region_counts = pd.Series(roi).value_counts()
        regions_ok = sorted(region_counts[region_counts >= MIN_REGION_N].index)
        n_r = len(regions_ok)
        region_idx = {r: i for i, r in enumerate(regions_ok)}
        roi_ok = np.isin(roi, regions_ok)
        print(f"  regions passing >={MIN_REGION_N} cells: {n_r} "
              f"({n_r*(n_r-1)//2} pairs)")

        uniq_s, samp_code = np.unique(samp, return_inverse=True)
        samp_region = np.array([region_idx.get(r, -1) for r in roi])
        # donor per sample (samples nested in donors; verify)
        samp_donor = donor[np.maximum(samp_code, 0)]
        # map: donor string of each unique sample (first cell seen)
        donor_of_code = np.full(len(uniq_s), "", dtype=object)
        seen = np.zeros(len(uniq_s), bool)
        for ci in range(n_cells):
            s = samp_code[ci]
            if not seen[s]:
                donor_of_code[s] = donor[ci]
                seen[s] = True
        # verify nesting
        chk = pd.DataFrame({"s": samp_code, "d": donor})
        nested = (chk.groupby("s")["d"].nunique() == 1).all()
        print(f"  samples nested in donors: {nested}")
        n_samples = len(uniq_s)

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
            for ci in range(start, end):
                if roi_ok[ci]:
                    s = samp_code[ci]
                    r0, r1 = int(indptr[ci]) - lo, int(indptr[ci + 1]) - lo
                    if r1 > r0:
                        np.add.at(s_sums[s], idx[r0:r1], dat[r0:r1])
                        s_counts[s] += 1
        print(f"  streaming pass done in {time.time()-t0:.0f}s")

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

    s_means = (s_sums[:, keep] / np.maximum(s_counts, 1)[:, None])
    ok_s = s_counts > 0
    s_means = s_means[ok_s]
    s_weights = s_counts[ok_s].astype(np.float64)
    region_per_code = np.zeros(n_samples, dtype=int)
    region_per_code[samp_code] = samp_region
    s_region = region_per_code[ok_s]
    s_donor = donor_of_code[ok_s]
    n_s = len(s_weights)
    uniq_d = sorted(set(s_donor.tolist()))
    n_pairs = n_r * (n_r - 1) // 2
    print(f"  usable blocks: {n_s}; donors: {len(uniq_d)} "
          f"({', '.join(f'{d}:{int((s_donor==d).sum())}' for d in uniq_d)})")

    # ---- observed ----
    obs_pbs = region_pbs_from_samples(s_region, s_weights, s_means)
    obs_w, obs_lkf, obs_lkn = pair_components(obs_pbs, hk_r, nh_r)
    obs_mean = float(obs_w.mean())
    obs_mlkf, obs_mlkn = float(obs_lkf.mean()), float(obs_lkn.mean())
    obs_med_kf = float(np.median(np.exp(obs_lkf)))
    obs_med_kn = float(np.median(np.exp(obs_lkn)))
    print(f"  Observed: mean_w={obs_mean:.3f} mean_log_kf={obs_mlkf:.4f} "
          f"mean_log_kn={obs_mlkn:.4f} med_kf={obs_med_kf:.5f} "
          f"med_kn={obs_med_kn:.5f}")

    # ---- Loop A: standard shuffle, track (mean_w, mean_lkf, mean_lkn) ----
    rng = np.random.RandomState(SEED_STD)
    nul_w = np.empty(B_PERM); nul_lkf = np.empty(B_PERM)
    nul_lkn = np.empty(B_PERM)
    nul_med_kf = np.empty(B_PERM); nul_med_kn = np.empty(B_PERM)
    t0 = time.time()
    for b in range(B_PERM):
        perm = s_region[rng.permutation(n_s)]
        pb = region_pbs_from_samples(perm, s_weights, s_means)
        w, lkf, lkn = pair_components(pb, hk_r, nh_r)
        nul_w[b] = w.mean(); nul_lkf[b] = lkf.mean(); nul_lkn[b] = lkn.mean()
        nul_med_kf[b] = np.median(np.exp(lkf))
        nul_med_kn[b] = np.median(np.exp(lkn))
        if (b + 1) % 200 == 0:
            el = time.time() - t0
            print(f"    [A] perm {b+1}/{B_PERM} elapsed={el:.0f}s "
                  f"ETA={el/(b+1)*(B_PERM-b-1):.0f}s")
    # x-check against script 83 null
    if ref_null is not None:
        d = np.abs(ref_null[fi] - nul_w)
        print(f"  X-CHECK vs 83 null: max|d|={d.max():.2e} "
              f"mean|d|={d.mean():.2e}")

    gap_lw = (obs_mlkf - obs_mlkn) - (nul_lkf.mean() - nul_lkn.mean())
    gap_f = obs_mlkf - nul_lkf.mean()
    gap_n = -(obs_mlkn - nul_lkn.mean())
    share_f = gap_f / gap_lw if abs(gap_lw) > 1e-12 else np.nan
    share_n = gap_n / gap_lw if abs(gap_lw) > 1e-12 else np.nan
    print(f"  Decomposition: log-w gap={gap_lw:.3f} "
          f"-> k_f share={share_f*100:.0f}%  k_n share={share_n*100:.0f}%")
    print(f"  Null medians: med_kf={np.median(nul_med_kf):.5f} "
          f"med_kn={np.median(nul_med_kn):.5f}")

    # ---- Loop B: donor-stratified shuffle ----
    rng2 = np.random.RandomState(SEED_STRAT)
    nul_strat = np.empty(B_PERM)
    donor_groups = [np.where(s_donor == d)[0] for d in uniq_d]
    t0 = time.time()
    for b in range(B_PERM):
        perm = s_region.copy()
        for gidx in donor_groups:
            perm[gidx] = s_region[gidx][rng2.permutation(len(gidx))]
        pb = region_pbs_from_samples(perm, s_weights, s_means)
        w, _, _ = pair_components(pb, hk_r, nh_r)
        nul_strat[b] = w.mean()
        if (b + 1) % 200 == 0:
            el = time.time() - t0
            print(f"    [B] perm {b+1}/{B_PERM} elapsed={el:.0f}s "
                  f"ETA={el/(b+1)*(B_PERM-b-1):.0f}s")
    p_strat = (np.sum(nul_strat >= obs_mean) + 1) / (B_PERM + 1)
    ses_strat = ((obs_mean - nul_strat.mean()) / nul_strat.std()
                 if nul_strat.std() > 1e-12 else 0.0)
    print(f"  Donor-stratified: null mean={nul_strat.mean():.3f} "
          f"sd={nul_strat.std():.3f} p={p_strat:.4f} SES={ses_strat:.2f}")

    # ---- LODO ----
    lodo = {}
    for d in uniq_d:
        msk = s_donor != d
        if msk.sum() < 2:
            continue
        pb = region_pbs_from_samples(s_region[msk], s_weights[msk],
                                     s_means[msk])
        w, _, _ = pair_components(pb, hk_r, nh_r)
        lodo[d] = float(w.mean())
    lodo_vals = np.array(list(lodo.values()))
    print(f"  LODO mean_w: min={lodo_vals.min():.3f} max={lodo_vals.max():.3f} "
          f"(full={obs_mean:.3f}; null95={np.quantile(nul_w, 0.95):.3f})")

    rows.append({
        "supercluster": sc_name, "n_regions": n_r, "n_pairs": n_pairs,
        "n_blocks": n_s, "n_donors": len(uniq_d),
        "omega_mean": obs_mean,
        "mean_log_kf": obs_mlkf, "mean_log_kn": obs_mlkn,
        "null_mean_log_kf": float(nul_lkf.mean()),
        "null_mean_log_kn": float(nul_lkn.mean()),
        "logw_gap": gap_lw, "kf_share": share_f, "kn_share": share_n,
        "obs_med_kf": obs_med_kf, "obs_med_kn": obs_med_kn,
        "null_med_kf": float(np.median(nul_med_kf)),
        "null_med_kn": float(np.median(nul_med_kn)),
        "strat_null_mean": float(nul_strat.mean()),
        "strat_null_sd": float(nul_strat.std()),
        "strat_p": p_strat, "strat_SES": ses_strat,
        "lodo_min": float(lodo_vals.min()), "lodo_max": float(lodo_vals.max()),
        "null_q95": float(np.quantile(nul_w, 0.95)),
    })
    del s_sums, s_means, obs_pbs
    gc.collect()
    print(f"  file done in {time.time()-t_file:.0f}s")

# ---- save ----
df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

lines = ["# nc75 Neuron Superclass: k_f / k_n Decomposition + Donor Robustness",
         "",
         "Standard block-shuffle null (B=1,000, seed 42) recomputed with",
         "per-pair k_f / k_n tracking; donor-stratified null (B=1,000,",
         "seed 43); leave-one-donor-out on observed mean omega.", "",
         "| supercluster | obs mean w | log-w gap | k_f share | k_n share | "
         "obs med k_f | null med k_f | obs med k_n | null med k_n |",
         "|---|---|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(
        f"| {r['supercluster']} | {r['omega_mean']:.2f} | "
        f"{r['logw_gap']:.3f} | {r['kf_share']*100:.0f}% | "
        f"{r['kn_share']*100:.0f}% | {r['obs_med_kf']:.5f} | "
        f"{r['null_med_kf']:.5f} | {r['obs_med_kn']:.5f} | "
        f"{r['null_med_kn']:.5f} |")
lines += ["", "## Donor-stratified null (region shuffled within donors)", "",
          "| supercluster | donors | null mean | null sd | p | SES |",
          "|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['supercluster']} | {r['n_donors']} | "
                 f"{r['strat_null_mean']:.2f} | {r['strat_null_sd']:.2f} | "
                 f"{r['strat_p']:.4f} | {r['strat_SES']:.1f} |")
lines += ["", "## Leave-one-donor-out (observed mean omega)", "",
          "| supercluster | LODO min | LODO max | full | null 95th pct |",
          "|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['supercluster']} | {r['lodo_min']:.2f} | "
                 f"{r['lodo_max']:.2f} | {r['omega_mean']:.2f} | "
                 f"{r['null_q95']:.2f} |")
OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nSaved: {OUT_CSV}\nSaved: {OUT_MD}")
print("DONE")
