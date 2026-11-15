"""
nc76 brain follow-up: power analysis + fixed-panel + alternative-HK sensitivity
================================================================================
Addresses nc75 blind-review must-answer items:
  brain-Q3   : is Thalamic P=0.163 size/power limited? -> size-matched power
               analysis: downsample MGE / Upper-layer IT to 20 regions
               (Thalamic scale), K replicates x B_quick perms -> rejection rate.
  scmethod-Q3: HK panel sensitivity -> alternative data-driven HK panel
               (lowest-CV genes across region pseudobulks, same count as the
               HRT-Atlas matched set, Eisenberg-style), observed omega + null.
  scmethod-Q4: circular per-pair panel dependence -> FIXED panel (top-200
               non-HK by across-region variance, pre-specified per file),
               observed omega + null; compare with circular results.

Null for the sensitivity arms uses the same sample-level block-shuffle
(B_SENS perms, seed 43) and recomputes only mean omega (P-value scale).

Outputs:
  results/nc76_brain_followup.csv
  results/nc76_brain_followup.md
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
BATCH = 5000
EPS = 1e-15

K_POWER = 40          # downsample replicates for power analysis
B_POWER = 50          # perms per replicate (P resolution ~0.02)
B_SENS = 200          # perms for fixed-panel / alt-HK arms
SEED_POWER, SEED_SENS = 2026, 43
TARGET_REGIONS = 20   # Thalamic scale

FILES = {
    "MGE interneuron": DATA_DIR / "brain" / "neurons" / "MGE_interneuron.h5ad",
    "Thalamic excitatory": DATA_DIR / "brain" / "neurons" / "Thalamic_excitatory.h5ad",
    "Upper-layer intratelencephalic": DATA_DIR / "brain" / "neurons"
                                       / "Upper-layer_intratelencephalic.h5ad",
}
POWER_FILES = ["MGE interneuron", "Upper-layer intratelencephalic"]

OUT_CSV = Path("results/nc76_brain_followup.csv")
OUT_MD = Path("results/nc76_brain_followup.md")

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


def region_pbs(assign_idx, weights, means):
    n_r = int(assign_idx.max()) + 1 if len(assign_idx) else 0
    pbs = np.zeros((n_r, means.shape[1]))
    for r in range(n_r):
        m = assign_idx == r
        if not m.any():
            continue
        w = weights[m]
        pb = (means[m] * w[:, None]).sum(0) / w.sum()
        t = pb.sum()
        pbs[r] = np.log1p(pb / t * 1e4) if t > 0 else pb
    return pbs


def mean_omega(PB, hk_r, kf_mode, fixed_panel=None):
    """kf_mode: 'circular' (per-pair top-200 on nh_r) or 'fixed' (fixed_panel
    indices into the reduced matrix)."""
    n = PB.shape[0]
    ws = []
    for i in range(n):
        pi = PB[i]
        for j in range(i + 1, n):
            pj = PB[j]
            kn = js_divergence(pi[hk_r], pj[hk_r])
            if kf_mode == "circular":
                nh_r = fixed_panel  # here fixed_panel carries nh_r
                ad = np.abs(pi - pj)[nh_r]
                t = min(N_TOP_KF, len(ad))
                tg = nh_r[np.argpartition(ad, -t)[-t:]]
            else:
                tg = fixed_panel
            kf = js_divergence(pi[tg], pj[tg])
            ws.append(kf / kn if kn > EPS else np.inf)
    return float(np.mean(ws))


rows = []

for sc_name, path in FILES.items():
    print("\n" + "=" * 60)
    print(f"Supercluster: {sc_name}")
    print("=" * 60)
    t_file = time.time()
    with h5py.File(path, "r") as f:
        X = f["X"]
        indptr = X["indptr"][:]
        data = X["data"]; indices = X["indices"]
        n_cells = len(indptr) - 1
        var_gene = read_cat(f["var"], "Gene").astype(str)
        n_genes = len(var_gene)
        roi = read_cat(f["obs"], "roi").astype(str)
        samp = read_cat(f["obs"], "sample_id").astype(str)
        region_counts = pd.Series(roi).value_counts()
        regions_ok = sorted(region_counts[region_counts >= MIN_REGION_N].index)
        n_r = len(regions_ok)
        region_idx = {r: i for i, r in enumerate(regions_ok)}
        roi_ok = np.isin(roi, regions_ok)
        uniq_s, samp_code = np.unique(samp, return_inverse=True)
        samp_region = np.array([region_idx.get(r, -1) for r in roi])
        n_samples = len(uniq_s)
        gene_sums = np.zeros(n_genes)
        s_sums = np.zeros((n_samples, n_genes))
        s_counts = np.zeros(n_samples, dtype=np.int64)
        for start in range(0, n_cells, BATCH):
            end = min(start + BATCH, n_cells)
            lo, hi = int(indptr[start]), int(indptr[end])
            idx = indices[lo:hi]; dat = data[lo:hi].astype(np.float64)
            np.add.at(gene_sums, idx, dat)
            for ci in range(start, end):
                if roi_ok[ci]:
                    s = samp_code[ci]
                    r0, r1 = int(indptr[ci]) - lo, int(indptr[ci + 1]) - lo
                    if r1 > r0:
                        np.add.at(s_sums[s], idx[r0:r1], dat[r0:r1])
                        s_counts[s] += 1
    print(f"  loaded {n_cells} cells, {n_r} regions ({time.time()-t_file:.0f}s)")

    # --- standard reduced set (HRT HK + top-5000 non-HK by mean) ---
    hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                                 if s in hk_human}), dtype=int)
    n_hk_hrt = len(hk_global)
    means_all = gene_sums / n_cells
    m = np.ones(n_genes, bool); m[hk_global] = False
    nm = means_all.copy(); nm[~m] = -np.inf
    hvg = np.argsort(nm)[-N_HVG:][::-1]
    keep = np.sort(np.union1d(hk_global, hvg))
    pos = {g: i for i, g in enumerate(keep)}
    hk_r = np.array([pos[g] for g in hk_global])
    nh_r = np.array([i for i, g in enumerate(keep) if g not in set(hk_global)])

    # --- alternative HK panel: lowest-CV genes across region pseudobulks ---
    # candidates restricted to genes DETECTED in every region pseudobulk
    # (log1p-CP10k mean > 0.5), otherwise zero-variance junk genes with
    # CV ~ 0/eps are selected and k_n degenerates to 0.
    s_means_full = s_sums / np.maximum(s_counts, 1)[:, None]
    ok_s = s_counts > 0
    region_per_code = np.zeros(n_samples, dtype=int)
    region_per_code[samp_code] = samp_region
    s_region_full = region_per_code[ok_s]
    s_w_full = s_counts[ok_s].astype(np.float64)
    pb_full = region_pbs(s_region_full, s_w_full, s_means_full[ok_s])
    detected = (pb_full > 0).all(0) & (pb_full.mean(0) > 0.5)
    cv = np.full(n_genes, np.inf)
    cv[detected] = (pb_full.std(0) / np.maximum(pb_full.mean(0), 1e-12))[detected]
    cv_rank = np.argsort(cv)
    alt_hk_global = np.sort(cv_rank[:n_hk_hrt])
    overlap = len(set(alt_hk_global) & set(hk_global))
    print(f"  alt-HK (lowest-CV, n={n_hk_hrt}): overlap with HRT = {overlap} "
          f"({overlap/n_hk_hrt*100:.0f}%)")
    keep_alt = np.sort(np.union1d(alt_hk_global, hvg))
    pos_a = {g: i for i, g in enumerate(keep_alt)}
    hk_r_alt = np.array([pos_a[g] for g in alt_hk_global])
    nh_r_alt = np.array([i for i, g in enumerate(keep_alt)
                         if g not in set(alt_hk_global)])
    del s_means_full, pb_full
    gc.collect()

    s_means = s_sums[:, keep] / np.maximum(s_counts, 1)[:, None]
    s_means_alt = s_sums[:, keep_alt] / np.maximum(s_counts, 1)[:, None]
    s_means = s_means[ok_s]; s_means_alt = s_means_alt[ok_s]
    s_weights = s_counts[ok_s].astype(np.float64)
    s_region = region_per_code[ok_s]
    n_s = len(s_weights)
    obs_pbs = region_pbs(s_region, s_weights, s_means)

    # fixed panel: top-200 non-HK by across-region variance (log pbs scale)
    v = obs_pbs.var(0)
    v[nh_r] = v[nh_r]  # explicit
    cand = nh_r[np.argsort(v[nh_r])[::-1][:N_TOP_KF]]
    fixed_panel = np.sort(cand)

    rng = np.random.RandomState(SEED_SENS)

    ALT_ONLY = "--alt-only" in sys.argv

    # ---- arm 1: fixed panel, obs + null ----
    if not ALT_ONLY:
        obs_fixed = mean_omega(obs_pbs, hk_r, "fixed", fixed_panel)
        null_fixed = np.empty(B_SENS)
        for b in range(B_SENS):
            perm = s_region[rng.permutation(n_s)]
            pb = region_pbs(perm, s_weights, s_means)
            null_fixed[b] = mean_omega(pb, hk_r, "fixed", fixed_panel)
        p_fixed = (np.sum(null_fixed >= obs_fixed) + 1) / (B_SENS + 1)
        print(f"  fixed panel: obs={obs_fixed:.2f} null={null_fixed.mean():.2f}"
              f"+-{null_fixed.std():.2f} P={p_fixed:.4f}")
        rows.append({"supercluster": sc_name, "arm": "fixed_panel",
                     "obs": obs_fixed, "null_mean": float(null_fixed.mean()),
                     "null_sd": float(null_fixed.std()), "B": B_SENS,
                     "p": p_fixed})

    # ---- arm 2: alternative HK panel, obs + null ----
    obs_pbs_alt = region_pbs(s_region, s_weights, s_means_alt)
    obs_alt = mean_omega(obs_pbs_alt, hk_r_alt, "circular", nh_r_alt)
    null_alt = np.empty(B_SENS)
    for b in range(B_SENS):
        perm = s_region[rng.permutation(n_s)]
        pb = region_pbs(perm, s_weights, s_means_alt)
        null_alt[b] = mean_omega(pb, hk_r_alt, "circular", nh_r_alt)
    p_alt = (np.sum(null_alt >= obs_alt) + 1) / (B_SENS + 1)
    print(f"  alt-HK: obs={obs_alt:.2f} null={null_alt.mean():.2f}"
          f"+-{null_alt.std():.2f} P={p_alt:.4f}")
    rows.append({"supercluster": sc_name, "arm": "alt_HK_lowCV",
                 "obs": obs_alt, "null_mean": float(null_alt.mean()),
                 "null_sd": float(null_alt.std()), "B": B_SENS,
                 "p": p_alt})

    # ---- arm 3: power at Thalamic size (MGE / IT only) ----
    if sc_name in POWER_FILES and not ALT_ONLY:
        rngp = np.random.RandomState(SEED_POWER)
        rej = 0
        ps = []
        ses_list = []
        for k in range(K_POWER):
            rsub = np.sort(rngp.choice(n_r, TARGET_REGIONS, replace=False))
            smask = np.isin(s_region, rsub)
            reg_remap = {r: i for i, r in enumerate(rsub)}
            s_reg_k = np.array([reg_remap[r] for r in s_region[smask]])
            w_k = s_weights[smask]
            m_k = s_means[smask]
            pb_o = region_pbs(s_reg_k, w_k, m_k)
            o = mean_omega(pb_o, hk_r, "circular", nh_r)
            nl = np.empty(B_POWER)
            for b in range(B_POWER):
                perm = s_reg_k[rngp.permutation(len(s_reg_k))]
                pb = region_pbs(perm, w_k, m_k)
                nl[b] = mean_omega(pb, hk_r, "circular", nh_r)
            p_k = (np.sum(nl >= o) + 1) / (B_POWER + 1)
            ps.append(p_k)
            ses_list.append((o - nl.mean()) / max(nl.std(), 1e-12))
            rej += p_k <= 0.05
        power = rej / K_POWER
        print(f"  power@{TARGET_REGIONS} regions: rejection rate "
              f"{rej}/{K_POWER} = {power:.2f}; median SES "
              f"{np.median(ses_list):.1f}")
        rows.append({"supercluster": sc_name,
                     "arm": f"power_{TARGET_REGIONS}regions",
                     "obs": power, "null_mean": float(np.median(ses_list)),
                     "null_sd": float(np.std(ses_list)), "B": B_POWER,
                     "p": float(np.median(ps))})

    del s_sums, s_means, s_means_alt, obs_pbs
    gc.collect()
    print(f"  file done in {time.time()-t_file:.0f}s")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)

lines = ["# nc76 brain follow-up: power + fixed-panel + alt-HK sensitivity", "",
         "| supercluster | arm | obs | null mean | null sd | B | p |",
         "|---|---|---|---|---|---|---|"]
for r in rows:
    lines.append(f"| {r['supercluster']} | {r['arm']} | {r['obs']:.3f} | "
                 f"{r['null_mean']:.3f} | {r['null_sd']:.3f} | {r['B']} | "
                 f"{r['p']:.4f} |")
OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\nSaved: {OUT_CSV}\nSaved: {OUT_MD}")
print("DONE")
