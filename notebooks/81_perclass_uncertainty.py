#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P1-2 (blind-review round 1, E1-M2): propagate per-class calibration
uncertainty into the per-class calibrated omega and the
astrocyte/Bergmann-glia gradient with a region-clustered joint bootstrap.

Reviewer complaint: the published per-class gradient CI (5.99x,
[4.86, 7.42], notebook 76 C3) resamples pairs i.i.d. in the numerator
while the manuscript's preferred class-mean uncertainty is the
region-clustered block bootstrap; the i.i.d. scheme ignores within-region
correlation and is therefore suspected anti-conservative.  In addition,
each class baseline rests on only 2-3 split-half populations (top-3
regions per class, >= 200 nuclei, 50 splits each), a sampling error the
published text does not carry.

This script recomputes, for every class:
  U1  per-class baseline n (regions, splits) and two-stage bootstrap CI
      (stage 1: resample regions with replacement; stage 2: within each
      drawn region resample its 50 split-half omega values; the baseline
      draw is the mean of the drawn region means)
  U2  joint region-clustered calibrated omega: each replicate draws the
      NUMERATOR as the region-clustered weighted mean of pair omega
      (regions resampled with replacement; a pair enters with weight
      mult(a) * mult(b)) and the DENOMINATOR as the two-stage baseline
      draw of U1, independently of the numerator draw
  U3  the astrocyte/Bergmann-glia gradient under the same joint scheme
      (replaces [4.86, 7.42])
  U4  divergent-vs-own-baseline classification: how many classes have
      the joint 95% CI of omega_cal_class excluding 1

Inputs (pre-existing, deterministic):
  results/reviewer_brain_splithalf_raw.csv   (notebook 42 split-half records)
  results/reviewer_brain_pair_kf_kn.csv      (authoritative per-pair omega)

Outputs:
  results/perclass_uncertainty.csv
  results/perclass_uncertainty.json
  results/perclass_uncertainty_report.txt
"""

import json
import os

import numpy as np
import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'results')
RNG = np.random.default_rng(42)
N_BOOT = 5000

# ----------------------------------------------------------------------
# Load inputs
# ----------------------------------------------------------------------
sh = pd.read_csv(os.path.join(RESULTS_DIR, 'reviewer_brain_splithalf_raw.csv'))
pairs = pd.read_csv(os.path.join(RESULTS_DIR, 'reviewer_brain_pair_kf_kn.csv'))

sh_by_ct = {ct: g for ct, g in sh.groupby('cell_type')}
pairs_by_ct = {ct: gp for ct, gp in pairs.groupby('cell_type')}

# per-region split-half omega values (stage-2 resampling units)
splits_by_ct_region = {
    ct: {rg: g['omega'].values for rg, g in gp.groupby('region')}
    for ct, gp in sh_by_ct.items()}


def region_clustered_num_draw(gp, rng, n_boot):
    """Region-clustered bootstrap draws of the class-mean pair omega."""
    regions = sorted(set(gp['region_a']) | set(gp['region_b']))
    idx = np.arange(len(regions))
    pos = {r: i for i, r in enumerate(regions)}
    ia = np.array([pos[r] for r in gp['region_a'].values])
    ib = np.array([pos[r] for r in gp['region_b'].values])
    om = gp['omega'].values
    draws = np.empty(n_boot)
    for b in range(n_boot):
        mult = np.bincount(rng.choice(idx, size=len(regions), replace=True),
                           minlength=len(regions)).astype(float)
        w = mult[ia] * mult[ib]
        if w.sum() <= 0:
            draws[b] = np.nan
        else:
            draws[b] = np.average(om, weights=w)
    return draws


def baseline_two_stage_draw(ct, rng, n_boot):
    """Two-stage baseline draws: regions with replacement, then splits."""
    region_means = splits_by_ct_region[ct]
    names = list(region_means.keys())
    vals = [region_means[n] for n in names]
    draws = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.integers(0, len(names), size=len(names))
        acc = []
        for i in pick:
            v = vals[i]
            acc.append(np.mean(rng.choice(v, size=len(v), replace=True)))
        draws[b] = float(np.mean(acc))
    return draws


# ----------------------------------------------------------------------
# U1 + U2: per-class baselines and joint calibrated omega
# ----------------------------------------------------------------------
rows = []
joint_draws = {}
for ct in sorted(sh_by_ct):
    gp = pairs_by_ct[ct]
    pm = sh_by_ct[ct].groupby('region')['omega'].mean().values
    num = region_clustered_num_draw(gp, RNG, N_BOOT)
    den = baseline_two_stage_draw(ct, RNG, N_BOOT)
    keep = den > 0
    cal = num[keep] / den[keep]
    joint_draws[ct] = cal
    rows.append({
        'cell_type': ct,
        'n_baseline_regions': int(len(pm)),
        'n_baseline_splits': int(len(sh_by_ct[ct])),
        'baseline_popmean': float(pm.mean()),
        'baseline_two_stage_lo': float(np.percentile(den, 2.5)),
        'baseline_two_stage_hi': float(np.percentile(den, 97.5)),
        'n_pairs_crossregion': int(len(gp)),
        'omega_crossregion': float(gp['omega'].mean()),
        'omega_cal_class': float(gp['omega'].mean() / pm.mean()),
        'omega_cal_class_lo': float(np.percentile(cal, 2.5)),
        'omega_cal_class_hi': float(np.percentile(cal, 97.5)),
        'divergent_joint_ci': bool(np.percentile(cal, 2.5) > 1.0),
    })
cal_df = pd.DataFrame(rows)

# ----------------------------------------------------------------------
# U3: astrocyte / Bergmann-glia gradient under the joint scheme
# ----------------------------------------------------------------------
ga = joint_draws['Astrocyte']
gb = joint_draws['Bergmann glia']
n = min(len(ga), len(gb))
grad = ga[:n] / gb[:n]
grad_point = (cal_df.set_index('cell_type').loc['Astrocyte', 'omega_cal_class']
              / cal_df.set_index('cell_type').loc['Bergmann glia', 'omega_cal_class'])
grad_lo = float(np.percentile(grad, 2.5))
grad_hi = float(np.percentile(grad, 97.5))

# reference: the published i.i.d.-numerator CI for comparison
old_lo, old_hi = 4.86, 7.42

summary = {
    'n_boot': N_BOOT,
    'seed': 42,
    'gradient': {
        'point': float(grad_point),
        'joint_region_clustered_ci': [grad_lo, grad_hi],
        'published_iid_ci': [old_lo, old_hi],
        'wider_than_published': bool((grad_hi - grad_lo) > (old_hi - old_lo)),
    },
    'n_divergent_joint': int(cal_df['divergent_joint_ci'].sum()),
    'n_classes': int(len(cal_df)),
}

# ----------------------------------------------------------------------
# Outputs
# ----------------------------------------------------------------------
cal_df.to_csv(os.path.join(RESULTS_DIR, 'perclass_uncertainty.csv'), index=False)
with open(os.path.join(RESULTS_DIR, 'perclass_uncertainty.json'), 'w') as f:
    json.dump(summary, f, indent=2)

with open(os.path.join(RESULTS_DIR, 'perclass_uncertainty_report.txt'), 'w') as f:
    f.write('=' * 72 + '\n')
    f.write('P1-2: per-class calibration uncertainty (region-clustered joint bootstrap)\n')
    f.write('=' * 72 + '\n\n')
    f.write(f'B = {N_BOOT}, seed 42. Numerator: region-clustered weighted mean of '
            'pair omega (regions resampled with replacement; pair weight '
            'mult(a)*mult(b)). Denominator: two-stage baseline draw (regions with '
            'replacement, then the 50 split-half omega values within each drawn '
            'region with replacement).\n\n')
    f.write('U1/U2  Per-class baselines and joint calibrated omega:\n')
    f.write(cal_df.to_string(index=False) + '\n\n')
    f.write('U3  Astrocyte / Bergmann-glia gradient:\n')
    f.write(f'     point estimate                     : {grad_point:.2f}x\n')
    f.write(f'     joint region-clustered 95% CI     : [{grad_lo:.2f}, {grad_hi:.2f}]\n')
    f.write(f'     published i.i.d.-numerator 95% CI  : [{old_lo:.2f}, {old_hi:.2f}]  '
            f'(wider: {summary["gradient"]["wider_than_published"]})\n\n')
    f.write('U4  Divergent vs own class baseline (joint 95% CI excludes 1):\n')
    f.write(f'     {summary["n_divergent_joint"]} of {summary["n_classes"]} classes\n')

print(open(os.path.join(RESULTS_DIR, 'perclass_uncertainty_report.txt')).read())
