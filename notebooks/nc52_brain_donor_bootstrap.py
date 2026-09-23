# -*- coding: utf-8 -*-
"""
nc52_brain_donor_bootstrap.py — NC v52 A2 + C2.

A2  Donor-level cluster bootstrap for the brain regional gradient.
    The published intervals are (a) equal-n downsample gradient 1.74
    [1.64, 1.84] over 20 downsample replicates (downsampling noise only)
    and (b) span-matched paired median 4.30 [3.40, 4.95] over 21 matched
    region pairs (pair-level bootstrap, pairs NOT independent: only 4
    donors, median top-donor share 0.61). This script puts both
    statistics on a donor-cluster basis:
      - donor cluster bootstrap: resample the 4 donors with replacement
        (B = 1,000, seed 42); within a replicate each drawn donor keeps
        its full cell/pair structure (cluster bootstrap); the whole
        equal-n pipeline (class totals -> min-class target ->
        proportional allocation -> cell-level downsample without
        replacement -> per-pair omega -> class means -> gradient) is
        re-run per replicate.
      - only 4 clusters exist, so the bootstrap distribution is
        discrete/coarse: we therefore ALSO report leave-one-donor-out
        gradient ranges and a donor x region block bootstrap as the
        pre-registered fallback for the small-cluster problem.
      - span-matched gradient: per replicate the region pseudobulks are
        rebuilt from the resampled donors' cells (full depth, no
        downsampling) and both the ratio-of-class-means and the paired
        per-region-pair median ratio are recomputed, so the pair
        dependence through shared donors is respected.

C2  Combined equal-n x span-matched control: astrocytes restricted to
    the 7 cerebellar regions defining Bergmann glia (21 region pairs),
    both classes downsampled to a common total (proportional across
    regions, without replacement; R = 20 replicates, seed 42); donor
    cluster bootstrap (B = 1,000) and LODO reported alongside.

Inputs : results/nc52_brain_ab_cells.npz, results/nc52_brain_ab_cellmeta.csv,
         results/nc52_brain_group_counts.csv, results/nc52_brain_genes.json
Outputs: results/nc52_brain_gradient_donor_bootstrap.csv  (long, per-replicate)
         results/nc52_brain_gradient_donor_bootstrap.json (summary + CIs)
         results/nc52_brain_combined_equaln_spanmatch.csv (R=20 observed reps)

Seeds: 42 throughout (per-analysis default_rng streams).
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "results"

MIN_REGION_N = 20
N_TOP_KF = 200
B_BOOT = 1000
R_DS = 20
SEED = 42
ASTRO, BERG = "Astrocyte", "Bergmann glia"

_t0 = time.time()


def log(msg):
    print(f"[{time.time()-_t0:7.0f}s] {msg}", flush=True)


# ================================================================ load
log("loading extraction ...")
z = np.load(OUT / "nc52_brain_ab_cells.npz")
data, indices, indptr = z["data"], z["indices"], z["indptr"]
N_KEEP = int(z["n_keep"])
cellmeta = pd.read_csv(OUT / "nc52_brain_ab_cellmeta.csv")
ginfo = json.load(open(OUT / "nc52_brain_genes.json"))
is_hk_keep = np.array(ginfo["is_hk_keep"], dtype=bool)
hk_loc = np.where(is_hk_keep)[0]
nonhk_loc = np.where(~is_hk_keep)[0]
gcounts = pd.read_csv(OUT / "nc52_brain_group_counts.csv")

cellmeta = cellmeta.reset_index(drop=True)
cellmeta["row"] = np.arange(len(cellmeta))

DONORS = sorted(cellmeta["donor"].unique())
ALL_CTS = sorted(gcounts["ct"].unique())
log(f"donors: {DONORS}; classes: {len(ALL_CTS)}")

# per (ct, roi, donor) -> row array (astro/berg only)
cells_of = {}
for (ct, roi, dn), g in cellmeta.groupby(["ct", "roi", "donor"]):
    cells_of[(ct, roi, dn)] = g["row"].values

# per (ct, roi, donor) counts — all classes (for allocation)
n_of = {(r.ct, r.roi, r.donor): int(r.n_cells)
        for r in gcounts.itertuples(index=False)}

# Bergmann reference regions (full data, >= MIN_REGION_N)
berg_regions = sorted({roi for (ct, roi, dn), n in n_of.items()
                       if ct == BERG and n >= MIN_REGION_N})
# pool across donors for the region definition (full data)
berg_reg_full = sorted(gcounts[(gcounts.ct == BERG)]
                       .groupby("roi")["n_cells"].sum()
                       .loc[lambda s: s >= MIN_REGION_N].index)
log(f"Bergmann regions (full data, >= {MIN_REGION_N}): {len(berg_reg_full)} "
    f"-> {berg_reg_full}")
assert len(berg_reg_full) == 7, "expected the 7 cerebellar regions"


# ================================================================ core ops
def rowsum(rows):
    """Sum CSR rows (repeated rows allowed) -> dense vector (N_KEEP,)."""
    rows = np.asarray(rows)
    counts = indptr[rows + 1] - indptr[rows]
    total = int(counts.sum())
    if total == 0:
        return np.zeros(N_KEEP)
    cum = np.zeros(len(rows) + 1, dtype=np.int64)
    np.cumsum(counts, out=cum[1:])
    ar = np.arange(total)
    which = np.searchsorted(cum[1:], ar, side="right")
    pos = indptr[rows[which]] + (ar - cum[which])
    return np.bincount(indices[pos], weights=data[pos], minlength=N_KEEP)


def pb_from_sum(col_sum, n):
    pb = col_sum / max(n, 1)
    tot = pb.sum()
    if tot > 0:
        pb = pb / tot * 1e4
    return np.log1p(pb).astype(np.float64)


def _js_rows(P, q):
    """JS(P_i || q) base-2 with the EXACT cki.core.js_divergence
    convention: inputs are log1p pseudobulks converted to probability
    distributions by SOFTMAX (exp(x - max) / (sum + 1e-9)), PER ROW for
    P and for q (cki.utils.ensure_probability_distribution, mode=
    'softmax' default). q may be 1D (shared gene set, e.g. HK) or 2D
    (per-pair gene sets, e.g. top-200 k_f); softmax is always along the
    last axis."""
    Pe = np.exp(P - P.max(axis=-1, keepdims=True))
    Pn = Pe / (Pe.sum(axis=-1, keepdims=True) + 1e-9)
    qe = np.exp(q - q.max(axis=-1, keepdims=True))
    qn = qe / (qe.sum(axis=-1, keepdims=True) + 1e-9)
    M = 0.5 * (Pn + qn)
    with np.errstate(divide="ignore", invalid="ignore"):
        t1 = np.where(Pn > 0, Pn * np.log2(Pn / M), 0.0)
        t2 = np.where(qn > 0, qn * np.log2(qn / M), 0.0)
    return 0.5 * (t1.sum(axis=-1) + t2.sum(axis=-1))


def pair_means(pbs):
    """Mean (kn, kf, omega) over all region pairs of pb list (script 96
    pair_stats semantics: per-pair top-200 |dpb| non-HK for k_f)."""
    P = np.asarray(pbs)
    R = P.shape[0]
    kns, kfs, oms = [], [], []
    for i in range(R - 1):
        Q = P[i + 1:]
        q = P[i]
        kn = _js_rows(Q[:, hk_loc], q[hk_loc])
        ad = np.abs(Q[:, nonhk_loc] - q[nonhk_loc])
        top = min(N_TOP_KF, ad.shape[1])
        tl = np.argpartition(ad, -top, axis=1)[:, -top:]
        r_idx = np.arange(Q.shape[0])[:, None]
        kf = _js_rows(Q[:, nonhk_loc][r_idx, tl], q[nonhk_loc][tl])
        kns.append(kn)
        kfs.append(kf)
        oms.append(np.where(kn > 1e-15, kf / kn, np.nan))
    kn = np.concatenate(kns)
    kf = np.concatenate(kfs)
    om = np.concatenate(oms)
    return float(np.mean(kn)), float(np.mean(kf)), float(np.nanmean(om))


# ================================================================ pipelines
def class_regions_resampled(ct, mult):
    """n'(roi) = sum_d mult_d * n(ct, roi, d); returns {roi: n'} with n'>0."""
    out = {}
    for d_i, m in enumerate(mult):
        if m == 0:
            continue
        dn = DONORS[d_i]
        for (c, roi, d), n in n_of.items():
            if c == ct and d == dn:
                out[roi] = out.get(roi, 0) + m * n
    return out


def min_class_target(mult):
    """min over classes of tot'(ct) = sum of n' over regions with n'>=20."""
    tots = {}
    for ct in ALL_CTS:
        regs = class_regions_resampled(ct, mult)
        tot = sum(n for n in regs.values() if n >= MIN_REGION_N)
        if tot > 0:
            tots[ct] = tot
    return tots, (min(tots.values()) if tots else 0)


def alloc(n, target, tot):
    k = max(1, int(round(n * target / tot)))
    return min(k, n)


def pooled_rows(ct, roi, mult):
    """Cell rows of (ct, roi) with donor multiplicity (cluster bootstrap:
    a twice-drawn donor contributes its cells twice)."""
    parts = []
    for d_i, m in enumerate(mult):
        if m == 0:
            continue
        rows = cells_of.get((ct, roi, DONORS[d_i]))
        if rows is not None and len(rows):
            parts.extend([rows] * m)
    return np.concatenate(parts) if parts else np.array([], dtype=np.int64)


def equaln_gradient(mult, rng, restrict_regions=None):
    """Full equal-n pipeline under donor multiplicities.
    restrict_regions: if given, only these regions enter (combined
    control) and the target is the min over the two classes only."""
    if restrict_regions is None:
        tots, target = min_class_target(mult)
    else:
        tots = {}
        for ct in (ASTRO, BERG):
            regs = {r: n for r, n in class_regions_resampled(ct, mult).items()
                    if r in restrict_regions}
            tot = sum(n for n in regs.values() if n >= MIN_REGION_N)
            if tot > 0:
                tots[ct] = tot
        target = min(tots.values()) if len(tots) == 2 else 0
    if target == 0 or ASTRO not in tots or BERG not in tots:
        return None
    out = {}
    for ct in (ASTRO, BERG):
        regs = class_regions_resampled(ct, mult)
        if restrict_regions is not None:
            regs = {r: n for r, n in regs.items() if r in restrict_regions}
        regs = {r: n for r, n in regs.items() if n >= MIN_REGION_N}
        if len(regs) < 2:
            return None
        pbs = []
        for roi, n in sorted(regs.items()):
            k = alloc(n, target, tots[ct])
            pool = pooled_rows(ct, roi, mult)
            sel = pool[rng.choice(len(pool), size=k, replace=False)]
            pbs.append(pb_from_sum(rowsum(sel), k))
        out[ct] = pair_means(pbs) + (len(regs),)
    ga = out[ASTRO][2] / out[BERG][2]
    return {"gradient": ga,
            "omega_astro": out[ASTRO][2], "omega_berg": out[BERG][2],
            "kf_ratio": out[ASTRO][1] / out[BERG][1],
            "kn_ratio": out[ASTRO][0] / out[BERG][0],
            "n_regions_astro": out[ASTRO][3], "n_regions_berg": out[BERG][3],
            "target": target}


def span_gradient(mult, rng=None):
    """Span-matched (full-depth) gradient over the 7 cerebellar regions:
    region pbs rebuilt from resampled donors; both ratio-of-class-means
    and paired per-region-pair median ratio."""
    pbs = {}
    for ct in (ASTRO, BERG):
        regs = class_regions_resampled(ct, mult)
        pbs[ct] = {}
        for roi in berg_reg_full:
            n = regs.get(roi, 0)
            if n < MIN_REGION_N:
                continue
            pool = pooled_rows(ct, roi, mult)
            if len(pool) == 0:
                continue
            pbs[ct][roi] = pb_from_sum(rowsum(pool), len(pool))
    common = sorted(set(pbs[ASTRO]) & set(pbs[BERG]))
    if len(common) < 2:
        return None
    pairs = [(common[i], common[j]) for i in range(len(common))
             for j in range(i + 1, len(common))]
    om_a, om_b = [], []
    for ra, rb in pairs:
        ka, fa, oa = pair_means([pbs[ASTRO][ra], pbs[ASTRO][rb]])
        kb, fb, ob = pair_means([pbs[BERG][ra], pbs[BERG][rb]])
        om_a.append(oa)
        om_b.append(ob)
    om_a = np.array(om_a)
    om_b = np.array(om_b)
    ratios = om_a / om_b
    return {"ratio_means": float(om_a.mean() / om_b.mean()),
            "paired_median": float(np.median(ratios)),
            "omega_astro": float(om_a.mean()), "omega_berg": float(om_b.mean()),
            "n_pairs": len(pairs), "n_regions": len(common)}


def block_bootstrap_mults(rng):
    """donor x region block bootstrap: resample (donor, roi) blocks within
    each class; returns cell-pool spec per (ct, roi) as list of
    (donor,) with multiplicity, plus resampled counts for all classes."""
    blocks = {}
    for (ct, roi, dn), n in n_of.items():
        blocks.setdefault(ct, []).append((roi, dn, n))
    reg_counts = {ct: {} for ct in ALL_CTS}
    reg_pools = {ASTRO: {}, BERG: {}}
    for ct, bl in blocks.items():
        idx = rng.integers(0, len(bl), len(bl))
        for bi in idx:
            roi, dn, n = bl[bi]
            reg_counts[ct][roi] = reg_counts[ct].get(roi, 0) + n
            if ct in reg_pools:
                reg_pools[ct].setdefault(roi, []).append(dn)
    return reg_counts, reg_pools


def equaln_gradient_blocks(reg_counts, reg_pools, rng):
    tots = {}
    for ct in ALL_CTS:
        tot = sum(n for n in reg_counts.get(ct, {}).values()
                  if n >= MIN_REGION_N)
        if tot > 0:
            tots[ct] = tot
    if ASTRO not in tots or BERG not in tots:
        return None
    target = min(tots.values())
    out = {}
    for ct in (ASTRO, BERG):
        regs = {r: n for r, n in reg_counts[ct].items() if n >= MIN_REGION_N}
        if len(regs) < 2:
            return None
        pbs = []
        for roi, n in sorted(regs.items()):
            k = alloc(n, target, tots[ct])
            parts = [cells_of[(ct, roi, dn)] for dn in reg_pools[ct][roi]
                     if (ct, roi, dn) in cells_of]
            pool = np.concatenate(parts)
            sel = pool[rng.choice(len(pool), size=k, replace=False)]
            pbs.append(pb_from_sum(rowsum(sel), k))
        out[ct] = pair_means(pbs) + (len(regs),)
    return {"gradient": out[ASTRO][2] / out[BERG][2],
            "omega_astro": out[ASTRO][2], "omega_berg": out[BERG][2],
            "n_regions_astro": out[ASTRO][3], "n_regions_berg": out[BERG][3],
            "target": target}


# ================================================================ run
rows = []
summary = {"seed": SEED, "B_boot": B_BOOT, "R_ds": R_DS,
           "min_region_n": MIN_REGION_N, "donors": DONORS,
           "bergmann_regions": berg_reg_full}

# ---- 0. observed checks (identity multiplicity) -------------------------
log("=== observed equal-n (identity donors, R=20 downsample reps) ===")
rng = np.random.default_rng(SEED)
obs_eq = [equaln_gradient((1, 1, 1, 1), rng) for _ in range(R_DS)]
g_obs = np.array([r["gradient"] for r in obs_eq])
log(f"equal-n observed: mean={g_obs.mean():.3f} "
    f"[{np.percentile(g_obs, 2.5):.3f}, {np.percentile(g_obs, 97.5):.3f}] "
    f"(published 1.74 [1.64, 1.84])")
for i, r in enumerate(obs_eq):
    rows.append({"analysis": "equaln", "method": "observed", "rep": i, **r})
summary["equaln_observed"] = {
    "mean": float(g_obs.mean()), "sd": float(g_obs.std()),
    "ci95_percentile": [float(np.percentile(g_obs, 2.5)),
                        float(np.percentile(g_obs, 97.5))],
    "published": "1.74 [1.64, 1.84] (20 downsample reps, script 96)"}

log("=== observed span-matched (identity donors, full depth) ===")
obs_span = span_gradient((1, 1, 1, 1))
log(f"span-matched observed: ratio_means={obs_span['ratio_means']:.3f} "
    f"paired_median={obs_span['paired_median']:.3f} "
    f"(published 3.68 / 4.30 [3.40, 4.95])")
rows.append({"analysis": "span_matched", "method": "observed", "rep": 0,
             **obs_span})
summary["span_observed"] = {**obs_span,
                            "published": "3.68 ratio-of-means; 4.30 "
                                         "[3.40, 4.95] paired median"}

# validation gate: do not burn hours of bootstrap on a miscalibrated
# pipeline — the identity-multiplicity observed checks must reproduce
# the published points before any bootstrap replicate is run.
assert 1.55 < g_obs.mean() < 1.95, \
    f"equal-n observed {g_obs.mean():.3f} != published 1.74"
assert 3.4 < obs_span["ratio_means"] < 3.9, \
    f"span observed {obs_span['ratio_means']:.3f} != published 3.68"
assert 4.0 < obs_span["paired_median"] < 4.6, \
    f"span observed {obs_span['paired_median']:.3f} != published 4.30"
log("observed checks PASS (equal-n ~1.74, span ~3.68/4.30)")

# ---- A2a. donor cluster bootstrap, equal-n ------------------------------
log("=== A2a: donor cluster bootstrap, equal-n (B=1000) ===")
rng = np.random.default_rng(SEED + 1)
boot_eq = []
for b in range(B_BOOT):
    mult = tuple(np.bincount(rng.integers(0, len(DONORS), len(DONORS)),
                             minlength=len(DONORS)))
    r = equaln_gradient(mult, rng)
    if r is not None:
        r["mult"] = mult
        boot_eq.append(r)
        rows.append({"analysis": "equaln", "method": "donor_bootstrap",
                     "rep": b, "donor_mult": str(mult), **r})
    if (b + 1) % 100 == 0:
        log(f"  {b+1}/{B_BOOT} ({len(boot_eq)} valid)")
ge = np.array([r["gradient"] for r in boot_eq])
log(f"equal-n donor bootstrap: n={len(ge)}, median={np.median(ge):.3f}, "
    f"95% CI [{np.percentile(ge, 2.5):.3f}, {np.percentile(ge, 97.5):.3f}], "
    f"min={ge.min():.3f}")
summary["equaln_donor_bootstrap"] = {
    "n_valid": int(len(ge)),
    "median": float(np.median(ge)),
    "ci95": [float(np.percentile(ge, 2.5)), float(np.percentile(ge, 97.5))],
    "min": float(ge.min()), "max": float(ge.max()),
    "frac_below_1": float((ge < 1).mean()),
    "note": "4 clusters only -> coarse discrete distribution; see LODO "
            "and donor x region block bootstrap"}

# ---- A2b. leave-one-donor-out, equal-n ----------------------------------
log("=== A2b: leave-one-donor-out, equal-n (R=20 each) ===")
lodo = {}
for d_i, dn in enumerate(DONORS):
    mult = tuple(0 if i == d_i else 1 for i in range(len(DONORS)))
    rng = np.random.default_rng(SEED + 2)
    reps = [equaln_gradient(mult, rng) for _ in range(R_DS)]
    reps = [r for r in reps if r is not None]
    if reps:
        g = np.array([r["gradient"] for r in reps])
        lodo[dn] = {"mean": float(g.mean()), "sd": float(g.std()),
                    "range": [float(g.min()), float(g.max())]}
        log(f"  drop {dn}: gradient {g.mean():.3f} "
            f"[{g.min():.3f}, {g.max():.3f}]")
    else:
        lodo[dn] = None
        log(f"  drop {dn}: not estimable")
summary["equaln_lodo"] = lodo
vals = [v["mean"] for v in lodo.values() if v]
summary["equaln_lodo_range"] = [float(min(vals)), float(max(vals))]

# ---- A2c. donor x region block bootstrap, equal-n -----------------------
log("=== A2c: donor x region block bootstrap, equal-n (B=1000) ===")
rng = np.random.default_rng(SEED + 3)
boot_bl = []
for b in range(B_BOOT):
    reg_counts, reg_pools = block_bootstrap_mults(rng)
    r = equaln_gradient_blocks(reg_counts, reg_pools, rng)
    if r is not None:
        boot_bl.append(r)
        rows.append({"analysis": "equaln", "method": "block_bootstrap",
                     "rep": b, **r})
    if (b + 1) % 200 == 0:
        log(f"  {b+1}/{B_BOOT} ({len(boot_bl)} valid)")
gb = np.array([r["gradient"] for r in boot_bl])
log(f"equal-n block bootstrap: n={len(gb)}, median={np.median(gb):.3f}, "
    f"95% CI [{np.percentile(gb, 2.5):.3f}, {np.percentile(gb, 97.5):.3f}]")
summary["equaln_block_bootstrap"] = {
    "n_valid": int(len(gb)), "median": float(np.median(gb)),
    "ci95": [float(np.percentile(gb, 2.5)), float(np.percentile(gb, 97.5))],
    "min": float(gb.min()), "max": float(gb.max()),
    "frac_below_1": float((gb < 1).mean())}

# ---- A2d. donor cluster bootstrap, span-matched -------------------------
log("=== A2d: donor cluster bootstrap, span-matched (B=1000) ===")
rng = np.random.default_rng(SEED + 4)
boot_sp = []
for b in range(B_BOOT):
    mult = tuple(np.bincount(rng.integers(0, len(DONORS), len(DONORS)),
                             minlength=len(DONORS)))
    r = span_gradient(mult)
    if r is not None:
        boot_sp.append(r)
        rows.append({"analysis": "span_matched", "method": "donor_bootstrap",
                     "rep": b, "donor_mult": str(mult), **r})
    if (b + 1) % 200 == 0:
        log(f"  {b+1}/{B_BOOT} ({len(boot_sp)} valid)")
rm = np.array([r["ratio_means"] for r in boot_sp])
pm = np.array([r["paired_median"] for r in boot_sp])
log(f"span donor bootstrap: n={len(rm)}; ratio_means median "
    f"{np.median(rm):.3f} [{np.percentile(rm, 2.5):.3f}, "
    f"{np.percentile(rm, 97.5):.3f}]; paired_median median "
    f"{np.median(pm):.3f} [{np.percentile(pm, 2.5):.3f}, "
    f"{np.percentile(pm, 97.5):.3f}]")
summary["span_donor_bootstrap"] = {
    "n_valid": int(len(rm)),
    "ratio_means": {"median": float(np.median(rm)),
                    "ci95": [float(np.percentile(rm, 2.5)),
                             float(np.percentile(rm, 97.5))],
                    "min": float(rm.min()), "frac_below_1": float((rm < 1).mean())},
    "paired_median": {"median": float(np.median(pm)),
                      "ci95": [float(np.percentile(pm, 2.5)),
                               float(np.percentile(pm, 97.5))],
                      "min": float(pm.min()),
                      "frac_below_1": float((pm < 1).mean())}}

# ---- A2e. LODO, span-matched ---------------------------------------------
log("=== A2e: leave-one-donor-out, span-matched ===")
lodo_sp = {}
for d_i, dn in enumerate(DONORS):
    mult = tuple(0 if i == d_i else 1 for i in range(len(DONORS)))
    r = span_gradient(mult)
    lodo_sp[dn] = r
    if r:
        log(f"  drop {dn}: ratio_means={r['ratio_means']:.3f} "
            f"paired_median={r['paired_median']:.3f} "
            f"(n_pairs={r['n_pairs']})")
    else:
        log(f"  drop {dn}: not estimable")
summary["span_lodo"] = lodo_sp

# ---- C2. combined equal-n x span-matched --------------------------------
log("=== C2: combined equal-n x span-matched (7 cerebellar regions) ===")
cb = set(berg_reg_full)
rng = np.random.default_rng(SEED + 5)
obs_cb = [equaln_gradient((1, 1, 1, 1), rng, restrict_regions=cb)
          for _ in range(R_DS)]
gc_obs = np.array([r["gradient"] for r in obs_cb])
log(f"combined observed: mean={gc_obs.mean():.3f} "
    f"[{np.percentile(gc_obs, 2.5):.3f}, {np.percentile(gc_obs, 97.5):.3f}] "
    f"(target={obs_cb[0]['target']})")
cb_df = pd.DataFrame([{"rep": i, **r} for i, r in enumerate(obs_cb)])
cb_df.to_csv(OUT / "nc52_brain_combined_equaln_spanmatch.csv", index=False)
summary["combined_observed"] = {
    "mean": float(gc_obs.mean()), "sd": float(gc_obs.std()),
    "ci95_percentile": [float(np.percentile(gc_obs, 2.5)),
                        float(np.percentile(gc_obs, 97.5))],
    "target_cells_per_class": int(obs_cb[0]["target"]),
    "regions": berg_reg_full}

rng = np.random.default_rng(SEED + 6)
boot_cb = []
for b in range(B_BOOT):
    mult = tuple(np.bincount(rng.integers(0, len(DONORS), len(DONORS)),
                             minlength=len(DONORS)))
    r = equaln_gradient(mult, rng, restrict_regions=cb)
    if r is not None:
        boot_cb.append(r)
        rows.append({"analysis": "combined", "method": "donor_bootstrap",
                     "rep": b, "donor_mult": str(mult), **r})
    if (b + 1) % 200 == 0:
        log(f"  {b+1}/{B_BOOT} ({len(boot_cb)} valid)")
gcv = np.array([r["gradient"] for r in boot_cb])
log(f"combined donor bootstrap: n={len(gcv)}, median={np.median(gcv):.3f}, "
    f"95% CI [{np.percentile(gcv, 2.5):.3f}, {np.percentile(gcv, 97.5):.3f}], "
    f"min={gcv.min():.3f}")
summary["combined_donor_bootstrap"] = {
    "n_valid": int(len(gcv)), "median": float(np.median(gcv)),
    "ci95": [float(np.percentile(gcv, 2.5)), float(np.percentile(gcv, 97.5))],
    "min": float(gcv.min()), "max": float(gcv.max()),
    "frac_below_1": float((gcv < 1).mean())}

lodo_cb = {}
for d_i, dn in enumerate(DONORS):
    mult = tuple(0 if i == d_i else 1 for i in range(len(DONORS)))
    rng = np.random.default_rng(SEED + 7)
    reps = [equaln_gradient(mult, rng, restrict_regions=cb)
            for _ in range(R_DS)]
    reps = [r for r in reps if r is not None]
    lodo_cb[dn] = ({"mean": float(np.mean([r['gradient'] for r in reps])),
                    "range": [float(min(r['gradient'] for r in reps)),
                              float(max(r['gradient'] for r in reps))]}
                   if reps else None)
summary["combined_lodo"] = lodo_cb
log(f"combined LODO: { {k: (round(v['mean'],3) if v else None) for k,v in lodo_cb.items()} }")

# ================================================================ save
pd.DataFrame(rows).to_csv(OUT / "nc52_brain_gradient_donor_bootstrap.csv",
                          index=False)
with open(OUT / "nc52_brain_gradient_donor_bootstrap.json", "w") as jf:
    json.dump(summary, jf, indent=2)
log(f"saved csv ({len(rows)} rows) + json")
log("DONE")
