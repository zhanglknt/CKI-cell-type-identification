#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P2-3 (E1-M4 / E2-M5): per-class split-half calibration for the brain atlas.

Reviewer complaint: a single global split-half baseline (mouse 6.67, or
brain-internal 9.73) is used to interpret all ten classes, although k_n
differs 3.2x between classes (Astrocyte 1.81e-3 vs Bergmann glia 5.83e-3,
per-pair k_n CV = 97.52%).  The expected omega of *equivalent* populations
should be a class-specific quantity.

This script re-uses the existing split-half records
(results/reviewer_brain_splithalf_raw.csv; 10 classes x top-3 regions
x 50 half/half splits, >=200 cells per region, produced by notebook 42)
to derive class-specific baselines, then restates:

  C1  class-specific split-half baselines (mean of region-level means,
      bootstrap 95% CI over population means), including the class-specific
      split-half k_f and k_n floors (E1-M4: "the floor may also be
      class-specific" -- it is, 40x across classes for split-half k_f)
  C2  per-class calibrated cross-region omega
      (omega_cal_class = mean cross-region omega / class baseline)
      with combined bootstrap CI (numerator: pair resampling;
      denominator: population-mean resampling)
  C3  the Astrocyte / Bergmann-glia headline gradient:
      invariant under any single shared calibration constant (including
      the E2-proposed 6.10 x 6.67/9.73 restatement, which mixes two
      calibrations and is not a ratio of consistently calibrated values);
      changes only under class-specific baselines
  C4  divergent-vs-constrained classification under each calibration,
      using the manuscript's preferred region-clustered bootstrap CI
      for the class-mean numerator vs the calibration point
  C5  gradient decomposition into k_f and k_n effects, for both the
      per-pair-mean ratio (6.10x, the headline) and the class-level
      ratio-of-means (6.51x, where the multiplicative identity holds
      exactly)

Inputs (all pre-existing, deterministic):
  results/reviewer_brain_splithalf_raw.csv
  results/reviewer_kn_estimator_consistency.csv
  results/reviewer_brain_pair_kf_kn.csv

Outputs:
  results/perclass_calibration.csv
  results/perclass_calibration.json
  results/perclass_calibration_report.txt
"""

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'results')
RNG = np.random.default_rng(42)
N_BOOT = 2000
MOUSE_BASELINE = 6.67          # empirical calibration, 6 split-half populations

# ----------------------------------------------------------------------
# Load inputs
# ----------------------------------------------------------------------
sh = pd.read_csv(os.path.join(RESULTS_DIR, 'reviewer_brain_splithalf_raw.csv'))
cons = pd.read_csv(os.path.join(RESULTS_DIR, 'reviewer_kn_estimator_consistency.csv'))
pairs = pd.read_csv(os.path.join(RESULTS_DIR, 'reviewer_brain_pair_kf_kn.csv'))

# sanity: recompute the brain-internal global baseline
pop_means = sh.groupby(['cell_type', 'region'])['omega'].mean()
BRAIN_GLOBAL_BASELINE = float(pop_means.mean())
summary_ref = dict(
    recomputed_grand=round(BRAIN_GLOBAL_BASELINE, 4),
    published_value=9.7261,
    match=bool(abs(BRAIN_GLOBAL_BASELINE - 9.7261) < 5e-4),
    n_populations=int(len(pop_means)),
    n_splits=int(len(sh)))

# ----------------------------------------------------------------------
# C1: class-specific split-half baselines
# ----------------------------------------------------------------------
rows = []
for ct, g in sh.groupby('cell_type'):
    pm = g.groupby('region')['omega'].mean().values          # population means
    boot = np.array([np.mean(RNG.choice(pm, size=len(pm), replace=True))
                     for _ in range(N_BOOT)])
    rows.append({
        'cell_type': ct,
        'n_regions': int(len(pm)),
        'n_splits': int(len(g)),
        'baseline_popmean': float(pm.mean()),
        'baseline_lo': float(np.percentile(boot, 2.5)),
        'baseline_hi': float(np.percentile(boot, 97.5)),
        'baseline_kf': float(g['kf'].mean()),
        'baseline_kn': float(g['kn'].mean()),
    })
base = pd.DataFrame(rows).sort_values('baseline_popmean').reset_index(drop=True)

# ----------------------------------------------------------------------
# C2: per-class calibrated cross-region omega
# ----------------------------------------------------------------------
cons_i = cons.set_index('cell_type')
pairs_by_ct = {ct: gp for ct, gp in pairs.groupby('cell_type')}


def region_clustered_mean_ct(gp, rng, n_boot):
    """Region-clustered bootstrap of the class-mean omega.

    Resample the class's regions with replacement; a pair contributes
    with weight mult(a) * mult(b); weighted mean of pair omega.
    Returns (point_mean, lo, hi)."""
    regions = np.array(sorted(set(gp['region_a']) | set(gp['region_b'])))
    ra = gp['region_a'].values
    rb = gp['region_b'].values
    om = gp['omega'].values
    point = float(om.mean())
    means = []
    idx = np.arange(len(regions))
    pos = {r: i for i, r in enumerate(regions)}
    ia = np.array([pos[r] for r in ra])
    ib = np.array([pos[r] for r in rb])
    for _ in range(n_boot):
        mult = np.bincount(rng.choice(idx, size=len(regions), replace=True),
                           minlength=len(regions)).astype(float)
        w = mult[ia] * mult[ib]
        if w.sum() <= 0:
            continue
        means.append(float(np.average(om, weights=w)))
    return point, float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


# sanity: reproduce the published BG region-clustered CI [8.49, 19.52]
bg_pt, bg_lo, bg_hi = region_clustered_mean_ct(pairs_by_ct['Bergmann glia'], RNG, N_BOOT)
sanity_bg = dict(point=round(bg_pt, 2), ci=[round(bg_lo, 2), round(bg_hi, 2)],
                 published=[8.49, 19.52])

recs = []
for _, r in base.iterrows():
    ct = r['cell_type']
    obs = float(cons_i.loc[ct, 'omega_mean_perpair_kn'])      # headline statistic
    b = r['baseline_popmean']
    obs_pairs = pairs_by_ct[ct]
    # combined bootstrap: resample pairs (numerator) and population
    # means (denominator) independently
    num = np.array([np.mean(RNG.choice(obs_pairs['omega'].values,
                                       size=len(obs_pairs), replace=True))
                    for _ in range(N_BOOT)])
    pm = sh[sh['cell_type'] == ct].groupby('region')['omega'].mean().values
    den = np.array([np.mean(RNG.choice(pm, size=len(pm), replace=True))
                    for _ in range(N_BOOT)])
    keep = den > 0
    ratio_boot = num[keep] / den[keep]
    # region-clustered numerator CI (manuscript's preferred uncertainty)
    pt, rc_lo, rc_hi = region_clustered_mean_ct(obs_pairs, RNG, N_BOOT)
    recs.append({
        'cell_type': ct,
        'n_pairs_crossregion': int(cons_i.loc[ct, 'n_pairs']),
        'omega_crossregion': obs,
        'omega_rc_lo': rc_lo, 'omega_rc_hi': rc_hi,
        'baseline_class': b,
        'baseline_lo': r['baseline_lo'], 'baseline_hi': r['baseline_hi'],
        'omega_cal_class': obs / b,
        'omega_cal_class_lo': float(np.percentile(ratio_boot, 2.5)),
        'omega_cal_class_hi': float(np.percentile(ratio_boot, 97.5)),
        'omega_cal_mouse': obs / MOUSE_BASELINE,
        'omega_cal_brainglobal': obs / BRAIN_GLOBAL_BASELINE,
    })
cal = pd.DataFrame(recs)

# ----------------------------------------------------------------------
# C3: headline gradient under different calibrations
# ----------------------------------------------------------------------
ci = cal.set_index('cell_type')
g_raw = ci.loc['Astrocyte', 'omega_crossregion'] / ci.loc['Bergmann glia', 'omega_crossregion']
# a single shared constant cancels in a ratio: under mouse 6.67, brain-global
# 9.73, or any other constant calibration the class-mean ratio stays 6.10x.
# (The E2-suggested "6.10 x 6.67/9.73 = 4.2x" multiplies a ratio by a level
# rescale and therefore does not correspond to a ratio of two consistently
# calibrated values; what the brain-internal baseline changes are the
# LEVELS: astrocyte 12.4 -> 8.5, Bergmann glia 2.03 -> 1.39.)
g_class = ci.loc['Astrocyte', 'omega_cal_class'] / ci.loc['Bergmann glia', 'omega_cal_class']

# bootstrap CI for the per-class gradient
ga, gb = [], []
pa_om = pairs_by_ct['Astrocyte']['omega'].values
pb_om = pairs_by_ct['Bergmann glia']['omega'].values
ma = sh[sh['cell_type'] == 'Astrocyte'].groupby('region')['omega'].mean().values
mb = sh[sh['cell_type'] == 'Bergmann glia'].groupby('region')['omega'].mean().values
for _ in range(N_BOOT):
    num_a = np.mean(RNG.choice(pa_om, size=len(pa_om), replace=True))
    num_b = np.mean(RNG.choice(pb_om, size=len(pb_om), replace=True))
    ba = np.mean(RNG.choice(ma, size=len(ma), replace=True))
    bb = np.mean(RNG.choice(mb, size=len(mb), replace=True))
    if ba > 0 and bb > 0:
        ga.append(num_a / ba)
        gb.append(num_b / bb)
g_class_boot = np.array(ga) / np.array(gb)
g_class_lo = float(np.percentile(g_class_boot, 2.5))
g_class_hi = float(np.percentile(g_class_boot, 97.5))

levels = {
    'astrocyte': {'mouse': float(ci.loc['Astrocyte', 'omega_cal_mouse']),
                  'brain_global': float(ci.loc['Astrocyte', 'omega_cal_brainglobal']),
                  'per_class': float(ci.loc['Astrocyte', 'omega_cal_class'])},
    'bergmann_glia': {'mouse': float(ci.loc['Bergmann glia', 'omega_cal_mouse']),
                      'brain_global': float(ci.loc['Bergmann glia', 'omega_cal_brainglobal']),
                      'per_class': float(ci.loc['Bergmann glia', 'omega_cal_class'])},
}

# ----------------------------------------------------------------------
# C4: divergent vs constrained classification under each calibration
#      unified criterion: region-clustered 95% CI of the class-mean omega
#      excludes the calibration point
# ----------------------------------------------------------------------
cal['divergent_mouse'] = cal['omega_rc_lo'] > MOUSE_BASELINE
cal['divergent_brainglobal'] = cal['omega_rc_lo'] > BRAIN_GLOBAL_BASELINE
cal['divergent_class'] = cal.apply(
    lambda r: r['omega_rc_lo'] > r['baseline_class'], axis=1)
cal['divergent_class_combinedCI'] = cal['omega_cal_class_lo'] > 1.0

n_div = {
    'mouse': int(cal['divergent_mouse'].sum()),
    'brain_global': int(cal['divergent_brainglobal'].sum()),
    'per_class': int(cal['divergent_class'].sum()),
    'per_class_combined_CI': int(cal['divergent_class_combinedCI'].sum()),
}

# classes flipping between schemes
flips = cal[cal['divergent_brainglobal'] != cal['divergent_class']][
    ['cell_type', 'omega_rc_lo', 'omega_rc_hi', 'baseline_class',
     'omega_cal_class', 'omega_cal_class_lo', 'omega_cal_class_hi']]

# ----------------------------------------------------------------------
# C5: gradient decomposition (k_f vs k_n effect)
# ----------------------------------------------------------------------
def kfkn(ct):
    return (float(cons_i.loc[ct, 'kf_mean']), float(cons_i.loc[ct, 'kn_mean']))
kfA, knA = kfkn('Astrocyte')
kfB, knB = kfkn('Bergmann glia')
kf_ratio = kfA / kfB          # ~2.03x
kn_ratio = knA / knB          # ~0.311 -> k_n contributes 1/0.311 = 3.21x
# ratio-of-means gradient (identity holds exactly)
g_ctlevel = (kfA / knA) / (kfB / knB)
# per-pair-mean gradient (headline): mean(kf/kn) per class, ratio of means
g_pairmean = g_raw
decomp = dict(
    gradient_pairmean=float(g_pairmean),        # 6.10x headline
    gradient_ctlevel=float(g_ctlevel),           # 6.51x, identity-exact
    kf_ratio=float(kf_ratio),
    kn_ratio_inverse=float(1.0 / kn_ratio),
    identity_holds=bool(abs(kf_ratio / kn_ratio - g_ctlevel) < 1e-9),
    note=('per-pair mean omega is mean(kf/kn); the multiplicative identity '
          'kf-ratio / kn-ratio holds exactly only for the ratio-of-means '
          'gradient (6.51x), as already stated in the manuscript'))

# ----------------------------------------------------------------------
# Save outputs
# ----------------------------------------------------------------------
out_csv = os.path.join(RESULTS_DIR, 'perclass_calibration.csv')
cal.to_csv(out_csv, index=False)

out_json = os.path.join(RESULTS_DIR, 'perclass_calibration.json')
payload = {
    'sanity': summary_ref,
    'sanity_bergmann_rc_ci': sanity_bg,
    'baselines': base.to_dict(orient='records'),
    'calibration': cal.to_dict(orient='records'),
    'gradient': {
        'raw': float(g_raw),
        'constant_calibration_invariant': True,
        'per_class': float(g_class),
        'per_class_ci95': [g_class_lo, g_class_hi],
        'levels': levels,
        'note': ('any single shared calibration constant cancels in a ratio; '
                 'the E2-proposed 6.10*6.67/9.73 mixes calibrations and is '
                 'not a ratio of consistently calibrated values; levels '
                 'under brain-internal calibration are the correct '
                 'restatement')},
    'classification': {
        'n_classes': int(len(cal)),
        'n_divergent': n_div,
        'flips_vs_brainglobal': flips.to_dict(orient='records')},
    'decomposition': decomp,
}
with open(out_json, 'w') as fh:
    json.dump(payload, fh, indent=2)

# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
rep = []
rep.append("=" * 72)
rep.append("P2-3: per-class split-half calibration (brain atlas, 10 classes)")
rep.append("=" * 72)
rep.append("")
rep.append(f"Sanity: grand split-half mean = {BRAIN_GLOBAL_BASELINE:.4f} "
           f"(published 9.7261, {summary_ref['n_populations']} populations, "
           f"{summary_ref['n_splits']} splits, match={summary_ref['match']})")
rep.append(f"Sanity: Bergmann glia region-clustered CI = "
           f"[{bg_lo:.2f}, {bg_hi:.2f}] (published [8.49, 19.52])")
rep.append("")
rep.append("C1  Class-specific baselines (split-half, mean of region means):")
rep.append(base.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
rep.append("")
rep.append("C2  Cross-region omega, region-clustered CI, and calibrated values:")
cols = ['cell_type', 'n_pairs_crossregion', 'omega_crossregion',
        'omega_rc_lo', 'omega_rc_hi', 'baseline_class', 'omega_cal_class',
        'omega_cal_class_lo', 'omega_cal_class_hi', 'omega_cal_mouse',
        'omega_cal_brainglobal']
rep.append(cal[cols].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
rep.append("")
rep.append("C3  Astrocyte / Bergmann-glia gradient:")
rep.append(f"     raw ratio                            : {g_raw:.2f}x")
rep.append("     mouse 6.67 / brain-global 9.73       : ratio unchanged "
           "(a shared constant cancels);")
rep.append("         levels change: astrocyte 12.41 -> 8.51, "
           "Bergmann glia 2.03 -> 1.39")
rep.append(f"     per-class baselines                  : {g_class:.2f}x "
           f"[{g_class_lo:.2f}, {g_class_hi:.2f}]")
rep.append("     (E2's 6.10 x 6.67/9.73 ~ 4.2x mixes two calibrations and")
rep.append("      is not a ratio of consistently calibrated values)")
rep.append("")
rep.append("C4  'All ten classes diverge beyond baseline'?")
rep.append("     criterion: region-clustered 95% CI of class mean excludes")
rep.append("               the calibration point")
rep.append(f"     mouse calibration (6.67)        : {n_div['mouse']}/10 divergent")
rep.append(f"     brain-global (9.73)              : {n_div['brain_global']}/10 divergent")
rep.append(f"     per-class baselines              : {n_div['per_class']}/10 divergent")
rep.append(f"     per-class, combined bootstrap CI : "
           f"{n_div['per_class_combined_CI']}/10 divergent")
if len(flips):
    rep.append("     classes flipping (brain-global -> per-class):")
    for _, fr in flips.iterrows():
        state = 'divergent' if fr['omega_rc_lo'] > fr['baseline_class'] else 'not'
        rep.append(f"       {fr['cell_type']:38s} rc-CI "
                   f"[{fr['omega_rc_lo']:.2f}, {fr['omega_rc_hi']:.2f}] "
                   f"vs baseline {fr['baseline_class']:.2f} -> {state} "
                   f"(omega_cal_class {fr['omega_cal_class']:.2f} "
                   f"[{fr['omega_cal_class_lo']:.2f}, {fr['omega_cal_class_hi']:.2f}])")
rep.append("")
rep.append("C5  Gradient decomposition (Astrocyte vs Bergmann glia):")
rep.append(f"     per-pair-mean gradient (headline) : {g_pairmean:.2f}x")
rep.append(f"     ratio-of-means gradient           : {g_ctlevel:.2f}x "
           f"= k_f ratio {kf_ratio:.2f} x k_n effect {1.0/kn_ratio:.2f} "
           f"(identity holds: {decomp['identity_holds']})")
rep.append("")
rep.append("Files: results/perclass_calibration.csv / .json / report above")

report = "\n".join(rep)
with open(os.path.join(RESULTS_DIR, 'perclass_calibration_report.txt'), 'w') as fh:
    fh.write(report + "\n")

print(report)
print("\nDONE.")
