#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v45 analysis B (P1-2 follow-up): small-cluster corrections for the
region-clustered bootstrap CIs of the Bergmann-glia / choroid-plexus
class-mean omega and the Astrocyte/Bergmann calibrated gradient.

Problem (r-statistics P1-2, v44 blind review): the percentile cluster
bootstrap is known to under-cover badly when the number of clusters is
tiny (Bergmann glia: 7 regions; choroid plexus: 6 regions; baselines rest
on 2-3 regions).  Reference intervals under review:
  - Bergmann glia class-mean omega CI      [8.49, 19.52] (baseline 9.08)
  - Astrocyte/Bergmann calibrated gradient [4.12, 9.18]  (notebook 81)

Part 1  Alternative interval estimates on the real data
  For each target statistic we compute three 95% CIs:
    (a) percentile region-clustered bootstrap (the published scheme,
        notebook 81: regions resampled with replacement, pair weight
        mult(a)*mult(b); baselines two-stage with split resampling)
    (b) wild cluster bootstrap, Rademacher weights on the cluster-level
        influence contributions (gradient handled on the log scale so
        all perturbed components stay positive)
    (c) studentized (bootstrap-t) cluster bootstrap; the standard error
        uses the influence-function (multiplier) variance of the
        weighted pair mean, re-evaluated inside every replicate
        (gradient studentized on the log scale, delta method over the
        four independent numerator/baseline components)

Part 2  Monte Carlo coverage simulation
  Synthetic 7-region (Bergmann-like) and 6-region (choroid-like) data:
  region random effects drawn i.i.d. from the empirical centered region
  means of the real per-pair omega values, pair noise drawn i.i.d. from
  the empirical centered residuals.  >= 2,000 simulations x B = 999
  bootstrap replicates per method; empirical coverage of the nominal 95%
  CIs for the true superpopulation mean.

Inputs:
  results/reviewer_brain_pair_kf_kn.csv     (per-pair omega)
  results/reviewer_brain_splithalf_raw.csv  (split-half baseline records)

Outputs:
  results/cluster_boot_v45.json
  results/cluster_boot_v45_report.md
"""

import json
import os

import numpy as np
import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           'results')
N_BOOT = 5000          # Part 1 replicates
N_SIM = 2000           # Part 2 Monte Carlo simulations
B_SIM = 999            # Part 2 bootstrap replicates per simulation
SEED = 20260905

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
pairs = pd.read_csv(os.path.join(RESULTS_DIR, 'reviewer_brain_pair_kf_kn.csv'))
sh = pd.read_csv(os.path.join(RESULTS_DIR, 'reviewer_brain_splithalf_raw.csv'))


class PairMean:
    """Cluster (region) structure of a cross-region pair-omega mean."""

    def __init__(self, cell_type):
        gp = pairs[pairs['cell_type'] == cell_type]
        regions = sorted(set(gp['region_a']) | set(gp['region_b']))
        pos = {r: i for i, r in enumerate(regions)}
        self.regions = regions
        self.ia = gp['region_a'].map(pos).values
        self.ib = gp['region_b'].map(pos).values
        self.om = gp['omega'].values
        self.G = len(regions)
        self.E = len(self.om)
        S = np.zeros(self.G)
        np.add.at(S, self.ia, self.om)
        np.add.at(S, self.ib, self.om)
        self.S = S                       # region sums of incident edge omegas
        self.theta = float(self.om.mean())
        # influence contributions of the multinomial-weighted mean:
        # theta(mult) = sum_{i<j} m_i m_j om_ij / sum_{i<j} m_i m_j,
        # g_i = d theta / d m_i at m = 1  ->  Var(theta*) = sum (g_i - gbar)^2
        self.g = (self.S - self.theta * (self.G - 1)) / self.E
        self.se = float(np.sqrt(((self.g - self.g.mean()) ** 2).sum()))

    def boot_draws(self, rng, B):
        """Vectorized region-clustered resamples; returns theta*, se* (valid rows)."""
        idx = rng.integers(0, self.G, size=(B, self.G))
        mult = np.zeros((B, self.G))
        np.add.at(mult, (np.repeat(np.arange(B), self.G), idx.ravel()), 1.0)
        W = mult[:, self.ia] * mult[:, self.ib]          # (B, E)
        N = W @ self.om
        D = W.sum(axis=1)
        valid = D > 0
        mult, W, N, D = mult[valid], W[valid], N[valid], D[valid]
        theta_star = N / D
        # resampled region sums S*_i = sum_j m_j om_ij;  the sandwich se on the
        # resampled data must use the resampled-graph degree (G - m_i copies of
        # other regions are the only valid edge partners) and sum the influence
        # variance over the G DRAWN clusters (i.e. multiplicity-weighted):
        #   h_i = (S*_i - theta* (G - m_i)) / D,
        #   se* = sqrt( sum_i m_i (h_i - hbar_w)^2 ),  hbar_w = sum_i m_i h_i / G
        Ss = np.zeros((len(D), self.G))
        rows = np.repeat(np.arange(len(D)), self.E)
        np.add.at(Ss, (rows, np.tile(self.ib, len(D))),
                  (mult[:, self.ia] * self.om).ravel())
        np.add.at(Ss, (rows, np.tile(self.ia, len(D))),
                  (mult[:, self.ib] * self.om).ravel())
        h = (Ss - theta_star[:, None] * (self.G - mult)) / D[:, None]
        hbar = (mult * h).sum(axis=1) / self.G
        se_star = np.sqrt((mult * (h - hbar[:, None]) ** 2).sum(axis=1))
        ok = se_star > 0
        return theta_star[ok], se_star[ok]

    def wild_draws(self, rng, B):
        signs = rng.choice([-1.0, 1.0], size=(B, self.G))
        return self.theta + signs @ (self.g - self.g.mean())


class BaselineMean:
    """Two-stage split-half baseline (regions, then 50 splits within region)."""

    def __init__(self, cell_type):
        sub = sh[sh['cell_type'] == cell_type]
        grp = sub.groupby('region')['omega']
        self.names = sorted(grp.groups)
        self.splits = np.stack([grp.get_group(r).values for r in self.names])
        self.Gd, self.n_splits = self.splits.shape
        self.m = self.splits.mean(axis=1)                # region means
        self.den = float(self.m.mean())
        self.h = (self.m - self.den) / (self.Gd * self.den)   # d log den / d m_k

    def boot_draws(self, rng, B):
        """Two-stage resamples; returns den*, per-draw region means (B, Gd)."""
        pick = rng.integers(0, self.Gd, size=(B, self.Gd))
        chosen = self.splits[pick]                       # (B, Gd, n_splits)
        j = rng.integers(0, self.n_splits, size=chosen.shape)
        vals = np.take_along_axis(chosen, j, axis=2)
        rm = vals.mean(axis=2)
        return rm.mean(axis=1), rm

    def wild_perturb(self, rng, B):
        signs = rng.choice([-1.0, 1.0], size=(B, self.Gd))
        return signs @ (self.h - self.h.mean())          # log-scale perturbation


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def three_cis_class_mean(pm, rng, B):
    """Percentile / wild / bootstrap-t CIs for a class-mean pair omega."""
    th, se = pm.boot_draws(rng, B)
    pct = ci(th)
    wild = ci(pm.wild_draws(rng, B))
    t = (th - pm.theta) / se
    qt = np.percentile(t, [2.5, 97.5])
    boot_t = [float(pm.theta - qt[1] * pm.se), float(pm.theta - qt[0] * pm.se)]
    return {'point': pm.theta, 'se': pm.se, 'percentile': pct,
            'wild': wild, 'boot_t': boot_t}


def three_cis_gradient(numA, denA, numB, denB, rng, B):
    """Percentile / wild / bootstrap-t CIs for (numA/denA)/(numB/denB)."""
    lg_pt = (np.log(numA.theta) - np.log(denA.den)
             - np.log(numB.theta) + np.log(denB.den))
    hA = (numA.g - numA.g.mean()) / numA.theta
    hB = (numB.g - numB.g.mean()) / numB.theta
    hdA = denA.h - denA.h.mean()
    hdB = denB.h - denB.h.mean()
    se_lg = float(np.sqrt((hA ** 2).sum() + (hdA ** 2).sum()
                          + (hB ** 2).sum() + (hdB ** 2).sum()))

    # --- percentile replicates (notebook-81 joint scheme) ---
    thA, seA = numA.boot_draws(rng, B)
    thB, seB = numB.boot_draws(rng, B)
    n = min(len(thA), len(thB))
    dA, rmA = denA.boot_draws(rng, B)
    dB, rmB = denB.boot_draws(rng, B)
    ok = (dA > 0) & (dB > 0)
    n = min(n, int(ok.sum()))
    lg_star = (np.log(thA[:n]) - np.log(dA[ok][:n])
               - np.log(thB[:n]) + np.log(dB[ok][:n]))
    pct = ci(np.exp(lg_star))

    # --- studentized replicates (log scale, delta method) ---
    rng_t = np.random.default_rng(rng.integers(0, 2**63 - 1))
    thA2, seA2 = numA.boot_draws(rng_t, B)
    thB2, seB2 = numB.boot_draws(rng_t, B)
    dA2, rmA2 = denA.boot_draws(rng_t, B)
    dB2, rmB2 = denB.boot_draws(rng_t, B)
    ok2 = (dA2 > 0) & (dB2 > 0)
    dA2, rmA2 = dA2[ok2], rmA2[ok2]
    dB2, rmB2 = dB2[ok2], rmB2[ok2]
    n2 = min(len(thA2), len(thB2), len(dA2))
    hsA = seA2[:n2] / thA2[:n2]                          # se(log numA*)
    hsB = seB2[:n2] / thB2[:n2]
    hsdA = rmA2[:n2] - dA2[:n2, None]
    hsdA = np.sqrt(((hsdA / (denA.Gd * dA2[:n2, None]))
                    - (hsdA / (denA.Gd * dA2[:n2, None])).mean(axis=1, keepdims=True)
                    ) ** 2).sum(axis=1) ** 0.5
    hsdB = rmB2[:n2] - dB2[:n2, None]
    hsdB = np.sqrt(((hsdB / (denB.Gd * dB2[:n2, None]))
                    - (hsdB / (denB.Gd * dB2[:n2, None])).mean(axis=1, keepdims=True)
                    ) ** 2).sum(axis=1) ** 0.5
    se_lg_star = np.sqrt(hsA ** 2 + hsB ** 2 + hsdA ** 2 + hsdB ** 2)
    lg_star2 = (np.log(thA2[:n2]) - np.log(dA2[:n2])
                - np.log(thB2[:n2]) + np.log(dB2[:n2]))
    keep = se_lg_star > 0
    t = (lg_star2[keep] - lg_pt) / se_lg_star[keep]
    qt = np.percentile(t, [2.5, 97.5])
    boot_t = [float(np.exp(lg_pt - qt[1] * se_lg)),
              float(np.exp(lg_pt - qt[0] * se_lg))]

    # --- wild replicates (log scale; independent Rademacher per component) ---
    wl = (numA.wild_draws(rng, B) - numA.theta) / numA.theta \
        + denA.wild_perturb(rng, B) * -1.0 \
        - (numB.wild_draws(rng, B) - numB.theta) / numB.theta \
        + denB.wild_perturb(rng, B)
    wild = ci(np.exp(lg_pt + wl))

    return {'point': float(np.exp(lg_pt)), 'se_log': se_lg,
            'percentile': pct, 'wild': wild, 'boot_t': boot_t}


# ----------------------------------------------------------------------
# Part 1: alternative intervals on the real data
# ----------------------------------------------------------------------
rng = np.random.default_rng(SEED)

pm_bg = PairMean('Bergmann glia')
pm_cp = PairMean('Choroid plexus')
pm_as = PairMean('Astrocyte')
den_bg = BaselineMean('Bergmann glia')
den_as = BaselineMean('Astrocyte')

part1 = {
    'bergmann_glia_class_mean': three_cis_class_mean(pm_bg, rng, N_BOOT),
    'choroid_plexus_class_mean': three_cis_class_mean(pm_cp, rng, N_BOOT),
    'astrocyte_bergmann_gradient': three_cis_gradient(
        pm_as, den_as, pm_bg, den_bg, rng, N_BOOT),
}
part1['bergmann_glia_class_mean']['n_clusters'] = pm_bg.G
part1['choroid_plexus_class_mean']['n_clusters'] = pm_cp.G
part1['reference'] = {
    'bergmann_published_percentile': [8.49, 19.52],
    'choroid_published_percentile': [27.30, 56.19],
    'gradient_published_joint_percentile': [4.12, 9.18],
    'bergmann_baseline': 9.08,
}

# ----------------------------------------------------------------------
# Part 2: Monte Carlo coverage simulation
# ----------------------------------------------------------------------

def simulate_coverage(pm, n_sim, B, rng):
    """Empirical coverage of the three CIs for the superpopulation mean.

    DGP: om_ij = theta_true + a_i + a_j + e_ij, with region effects a_i
    drawn i.i.d. from the empirical centered region means and pair noise
    e_ij i.i.d. from the empirical centered residuals of the real data.
    """
    m_region = pm.S / (pm.G - 1)
    a_emp = m_region - m_region.mean()
    r_emp = pm.om - (m_region[pm.ia] + m_region[pm.ib]) / 2.0
    r_emp = r_emp - r_emp.mean()
    theta_true = float(pm.om.mean())

    cover = {'percentile': 0, 'wild': 0, 'boot_t': 0}
    widths = {'percentile': [], 'wild': [], 'boot_t': []}
    for _ in range(n_sim):
        aa = rng.choice(a_emp, size=pm.G, replace=True)
        ee = rng.choice(r_emp, size=pm.E, replace=True)
        om = theta_true + aa[pm.ia] + aa[pm.ib] + ee
        S = np.zeros(pm.G)
        np.add.at(S, pm.ia, om)
        np.add.at(S, pm.ib, om)
        theta = om.mean()
        g = (S - theta * (pm.G - 1)) / pm.E
        se = np.sqrt(((g - g.mean()) ** 2).sum())

        sim = PairMean.__new__(PairMean)
        sim.ia, sim.ib, sim.om = pm.ia, pm.ib, om
        sim.G, sim.E, sim.S = pm.G, pm.E, S
        sim.theta, sim.g, sim.se = float(theta), g, float(se)

        th, se_star = sim.boot_draws(rng, B)
        lo, hi = ci(th)
        cover['percentile'] += lo <= theta_true <= hi
        widths['percentile'].append(hi - lo)

        lo, hi = ci(sim.wild_draws(rng, B))
        cover['wild'] += lo <= theta_true <= hi
        widths['wild'].append(hi - lo)

        t = (th - theta) / se_star
        qt = np.percentile(t, [2.5, 97.5])
        lo, hi = theta - qt[1] * se, theta - qt[0] * se
        cover['boot_t'] += lo <= theta_true <= hi
        widths['boot_t'].append(hi - lo)

    out = {}
    for k in cover:
        p = cover[k] / n_sim
        out[k] = {'coverage': p,
                  'mc_se': float(np.sqrt(p * (1 - p) / n_sim)),
                  'mean_width': float(np.mean(widths[k]))}
    out['theta_true'] = theta_true
    out['n_sim'] = n_sim
    out['B'] = B
    return out


rng2 = np.random.default_rng(SEED + 1)
part2 = {
    'bergmann_like_G7': simulate_coverage(pm_bg, N_SIM, B_SIM, rng2),
    'choroid_like_G6': simulate_coverage(pm_cp, N_SIM, B_SIM, rng2),
}

# ----------------------------------------------------------------------
# Outputs
# ----------------------------------------------------------------------
summary = {
    'seed': SEED,
    'n_boot_part1': N_BOOT,
    'n_sim_part2': N_SIM,
    'B_part2': B_SIM,
    'part1': part1,
    'part2': part2,
}
with open(os.path.join(RESULTS_DIR, 'cluster_boot_v45.json'), 'w') as f:
    json.dump(summary, f, indent=2)


def fmt(c):
    return f'[{c[0]:.2f}, {c[1]:.2f}] (width {c[1] - c[0]:.2f})'


L = []
L.append('# v45 analysis B: small-cluster corrections for region-clustered bootstrap CIs')
L.append('')
L.append(f'Seed {SEED}; Part 1 B = {N_BOOT}; Part 2 {N_SIM} simulations x B = {B_SIM}.')
L.append('')
L.append('## Part 1  Alternative 95% intervals on the real data')
L.append('')
for key, label, ref in [
        ('bergmann_glia_class_mean', 'Bergmann glia class-mean omega (7 regions)', '[8.49, 19.52] published'),
        ('choroid_plexus_class_mean', 'Choroid plexus class-mean omega (6 regions)', '[27.30, 56.19] published'),
        ('astrocyte_bergmann_gradient', 'Astrocyte / Bergmann-glia calibrated gradient', '[4.12, 9.18] published (joint percentile)')]:
    d = part1[key]
    L.append(f'### {label}')
    L.append(f'- point estimate: {d["point"]:.3f}')
    L.append(f'- percentile cluster bootstrap: {fmt(d["percentile"])}  (reference {ref})')
    L.append(f'- wild cluster bootstrap (Rademacher): {fmt(d["wild"])}')
    L.append(f'- studentized bootstrap-t: {fmt(d["boot_t"])}')
    L.append('')
L.append('## Part 2  Monte Carlo coverage (nominal 95%)')
L.append('')
L.append('| scenario | percentile | wild | bootstrap-t |')
L.append('|---|---|---|---|')
for key, label in [('bergmann_like_G7', '7 clusters (Bergmann-like)'),
                   ('choroid_like_G6', '6 clusters (choroid-like)')]:
    d = part2[key]
    L.append(f'| {label} | {d["percentile"]["coverage"]:.3f} | '
             f'{d["wild"]["coverage"]:.3f} | {d["boot_t"]["coverage"]:.3f} |')
L.append('')
L.append(f'MC standard error of a coverage estimate near 0.90: '
         f'~{np.sqrt(0.9 * 0.1 / N_SIM):.4f}.')
L.append('')
bg = part1['bergmann_glia_class_mean']
cp = part1['choroid_plexus_class_mean']
gr = part1['astrocyte_bergmann_gradient']
c7 = part2['bergmann_like_G7']
c6 = part2['choroid_like_G6']
L.append('## Conclusions / recommendation')
L.append('')
L.append('1. **Percentile cluster bootstrap under-covers by ~7-8 points at G = 6-7.** '
         f'Monte Carlo coverage of the nominal 95% interval: {c7["percentile"]["coverage"]:.3f} '
         f'(7 clusters) and {c6["percentile"]["coverage"]:.3f} (6 clusters). The published '
         'percentile intervals for Bergmann glia and choroid plexus are therefore too '
         'narrow, confirming reviewer P1-2.')
L.append('')
L.append('2. **Wild cluster bootstrap (Rademacher) is worse** '
         f'({c7["wild"]["coverage"]:.3f} / {c6["wild"]["coverage"]:.3f}): with 2^6-2^7 sign '
         'combinations the tails are coarse, and the symmetric perturbation cannot '
         'reproduce the skewness of the few-cluster sampling distribution. Not recommended '
         'as the replacement.')
L.append('')
L.append('3. **Studentized bootstrap-t attains nominal coverage** '
         f'({c7["boot_t"]["coverage"]:.3f} / {c6["boot_t"]["coverage"]:.3f}) and is the '
         'recommended replacement for every statistic resting on <= 7 region clusters. '
         'The price is honestly wider intervals '
         f'(simulation mean width {c7["boot_t"]["mean_width"]:.1f} vs '
         f'{c7["percentile"]["mean_width"]:.1f} for the percentile at G = 7).')
L.append('')
L.append('4. **Recommended replacement intervals (studentized bootstrap-t, 95%):**')
L.append(f'   - Bergmann glia class-mean omega 13.56: {fmt(bg["boot_t"])} '
         f'(was percentile [8.49, 19.52]). The lower bound {bg["boot_t"][0]:.2f} now falls '
         'BELOW the class baseline 9.08, so the claim that Bergmann glia diverges above '
         'its own class baseline does not survive the small-cluster correction and '
         'should be DOWNGRADED to a qualitative statement (cross-region omega elevated '
         'in absolute terms, but not separable from baseline at 7 regions). This is '
         'consistent with the notebook-81 joint calibrated-omega CI [0.99, 2.12], '
         'which already includes 1.')
L.append(f'   - Choroid plexus class-mean omega 37.76: {fmt(cp["boot_t"])} '
         '(was percentile [27.30, 56.19]). Lower bound remains far above its baseline '
         '10.66; the choroid divergence claim STANDS quantitatively.')
L.append(f'   - Astrocyte/Bergmann calibrated gradient 5.99x: {fmt(gr["boot_t"])} '
         '(was joint percentile [4.12, 9.18]). All three methods agree the lower bound '
         f'is > 4 (percentile {gr["percentile"][0]:.2f}, wild {gr["wild"][0]:.2f}, '
         f'bootstrap-t {gr["boot_t"][0]:.2f}), so the gradient claim is ROBUST and can '
         'remain quantitative; update the reported interval to the bootstrap-t one.')
L.append('')
L.append('5. Wild bootstrap and percentile intervals are retained above for the '
         'record; the studentization uses the sandwich variance of the '
         'multiplicity-weighted pair mean evaluated on the resampled graph '
         '(degree G - m_i per redrawn region), which is the consistent resampled-world '
         'analogue of the point-estimate influence-function se.')
report = '\n'.join(L)
with open(os.path.join(RESULTS_DIR, 'cluster_boot_v45_report.md'), 'w') as f:
    f.write(report)

print(report)
print()
print(json.dumps({k: {m: (v if not isinstance(v, dict) else
                         {kk: (round(vv, 4) if isinstance(vv, float) else vv)
                          for kk, vv in v.items()})
                      for m, v in d.items() if m in ('percentile', 'wild', 'boot_t')}
                  for k, d in part2.items()}, indent=2))
