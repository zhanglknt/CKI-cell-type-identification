#!/usr/bin/env python3
"""nc60 R2-M1 + R2-M2: paired statistics.

R2-M1: paired DeLong test for the Fig. 2e simulation AUC contrast
       (CKI omega 0.8042 vs k_f 0.7159; same 850 replicates, so AUCs are
       correlated). Implementation cross-validated against the authoritative
       single-metric DeLong CIs in results/nc52_stats_auc_ci_methods.csv
       (omega [0.7703, 0.8380], k_f [0.6773, 0.7545]).
       Cluster sensitivity: module-seed cluster bootstrap of Delta-AUC
       (3 signal module seeds resampled + iid neutral, B=5000, seed 42),
       matching the nc52 caliber.

R2-M2: McNemar-style paired comparison of T1 (technical-replicate) false
       reports on the brain drift ladder (2,161 pairs, 4 donors):
       discordant-pair counts, exact two-sided binomial P, and a
       donor-cluster bootstrap (4 donors resampled, B=10000, seed 42)
       95% CI for Delta-FPR (metric minus omega).

Outputs: results/nc60_paired_dauc.csv, results/nc60_mcnemar_t1.csv
"""
import json
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(42)

# ---------------------------------------------------------------- DeLong ----
def compute_midrank(x):
    J = np.argsort(x)
    Z = x[J]
    N = len(x)
    T = np.zeros(N)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = 0.5 * (i + j - 1) + 1.0
        i = j
    T2 = np.empty(N)
    T2[J] = T
    return T2

def fast_delong(predictions_sorted_transposed, label_1_count):
    """predictions_sorted_transposed: 2D array [k, n] with all positive
    examples first. Returns (aucs, delongcov)."""
    m = label_1_count
    n = predictions_sorted_transposed.shape[1] - m
    k = predictions_sorted_transposed.shape[0]
    positive = predictions_sorted_transposed[:, :m]
    negative = predictions_sorted_transposed[:, m:]
    tx = np.empty([k, m]); ty = np.empty([k, n]); tz = np.empty([k, m + n])
    for r in range(k):
        tx[r, :] = compute_midrank(positive[r, :])
        ty[r, :] = compute_midrank(negative[r, :])
        tz[r, :] = compute_midrank(predictions_sorted_transposed[r, :])
    aucs = tz[:, :m].sum(axis=1) / m / n - (m + 1.0) / 2.0 / n
    v01 = (tz[:, :m] - tx) / n
    v10 = 1.0 - (tz[:, m:] - ty) / m
    sx = np.cov(v01)
    sy = np.cov(v10)
    delongcov = sx / m + sy / n
    return aucs, delongcov

def delong_test(y, scores_a, scores_b):
    """Paired DeLong test A vs B. Returns dict with aucs, delta, se, z, p, ci."""
    order = (-y).argsort(kind='stable')
    m = int(y.sum())
    preds = np.vstack([scores_a[order], scores_b[order]])
    aucs, cov = fast_delong(preds, m)
    var_a, var_b = cov[0, 0], cov[1, 1]
    delta = aucs[0] - aucs[1]
    se = np.sqrt(var_a + var_b - 2 * cov[0, 1])
    z = delta / se
    p = 2 * stats.norm.sf(abs(z))
    ci = (delta - 1.959964 * se, delta + 1.959964 * se)
    return dict(auc_a=aucs[0], auc_b=aucs[1], var_a=var_a, var_b=var_b,
                cov_ab=cov[0, 1], delta=delta, se=se, z=z, p=p,
                ci_lo=ci[0], ci_hi=ci[1])

# ------------------------------------------------------------- R2-M1 ---------
raw = pd.read_csv('results/groundtruth_simulation_raw.csv')
pos = raw[(raw['series'] == 'signal') & (raw['delta'] >= 0.25)]
neg = raw[raw['series'].isin(['neutral_hk', 'neutral_global'])]
y = np.array([1] * len(pos) + [0] * len(neg))
vals = pd.concat([pos, neg]).reset_index(drop=True)
assert len(pos) == 600 and len(neg) == 250

# --- implementation validation against authoritative nc52 DeLong CIs ---
ref = pd.read_csv('results/nc52_stats_auc_ci_methods.csv')
ref = ref[ref['section'] == 'A4a_auc_ci'].set_index('metric')
checks = []
for met in ('omega', 'k_f'):
    s = vals[met].to_numpy(float)
    r = delong_test(y, s, s)
    lo = r['auc_a'] - 1.959964 * np.sqrt(r['var_a'])
    hi = r['auc_a'] + 1.959964 * np.sqrt(r['var_a'])
    ok = (abs(r['auc_a'] - ref.loc[met, 'auc']) < 5e-4
          and abs(lo - ref.loc[met, 'delong_ci_lo']) < 5e-4
          and abs(hi - ref.loc[met, 'delong_ci_hi']) < 5e-4)
    checks.append(ok)
    print(f'validate {met}: auc={r["auc_a"]:.4f} CI=[{lo:.4f},{hi:.4f}] '
          f'vs nc52 [{ref.loc[met,"delong_ci_lo"]:.4f},{ref.loc[met,"delong_ci_hi"]:.4f}] -> {"OK" if ok else "MISMATCH"}')
assert all(checks), 'DeLong implementation failed nc52 cross-validation'

# --- paired test omega vs each comparator ---
rows = []
for met in ('k_f', 'k_total', 'cosine', 'kf_over_kt', 'k_n'):
    r = delong_test(y, vals['omega'].to_numpy(float), vals[met].to_numpy(float))
    rows.append(dict(contrast=f'omega - {met}', auc_omega=r['auc_a'],
                     auc_other=r['auc_b'], delta=r['delta'], se=r['se'],
                     ci_lo=r['ci_lo'], ci_hi=r['ci_hi'], z=r['z'], p=r['p'],
                     method='paired DeLong (same 850 replicates)'))
    print(f"omega vs {met}: dAUC={r['delta']:.4f} SE={r['se']:.4f} "
          f"95%CI [{r['ci_lo']:.4f},{r['ci_hi']:.4f}] z={r['z']:.2f} P={r['p']:.3e}")

# --- cluster sensitivity: module-seed bootstrap of delta-AUC (omega - k_f) ---
B = 5000
seeds = pos['module_seed'].to_numpy()
uniq_seeds = np.unique(seeds)
print('signal module seeds:', uniq_seeds, 'n per seed:',
      [int((seeds == s).sum()) for s in uniq_seeds])
pos_idx = np.arange(len(pos)); neg_idx = np.arange(len(neg))
om_p = pos['omega'].to_numpy(float); kf_p = pos['k_f'].to_numpy(float)
om_n = neg['omega'].to_numpy(float); kf_n = neg['k_f'].to_numpy(float)
deltas = np.empty(B)
for b in range(B):
    pick_seeds = rng.choice(uniq_seeds, size=len(uniq_seeds), replace=True)
    pi = np.concatenate([pos_idx[seeds == s] for s in pick_seeds])
    ni = rng.choice(neg_idx, size=len(neg_idx), replace=True)
    yy = np.array([1] * len(pi) + [0] * len(ni))
    so = np.concatenate([om_p[pi], om_n[ni]])
    sk = np.concatenate([kf_p[pi], kf_n[ni]])
    from sklearn.metrics import roc_auc_score
    deltas[b] = roc_auc_score(yy, so) - roc_auc_score(yy, sk)
lo, hi = np.percentile(deltas, [2.5, 97.5])
p_boot = 2 * min((deltas <= 0).mean(), (deltas >= 0).mean())
print(f'cluster-boot dAUC(omega-k_f): median={np.median(deltas):.4f} '
      f'95%CI [{lo:.4f},{hi:.4f}] P={p_boot:.4f}')
rows.append(dict(contrast='omega - k_f (cluster bootstrap)',
                 auc_omega=np.nan, auc_other=np.nan,
                 delta=float(np.median(deltas)), se=float(deltas.std(ddof=1)),
                 ci_lo=float(lo), ci_hi=float(hi), z=np.nan, p=float(p_boot),
                 method='module-seed cluster bootstrap B=5000 (3 seeds resampled + iid neutral), nc52 caliber'))
pd.DataFrame(rows).to_csv('results/nc60_paired_dauc.csv', index=False)
print('saved results/nc60_paired_dauc.csv')

# ------------------------------------------------------------- R2-M2 ---------
lad = pd.read_csv('results/nc49_brain_drift_ladder.csv')
t1 = lad[lad['tier'] == 'T1_techrep'].copy()
print('\nT1 pairs:', len(t1), 'donors:', sorted(t1['donor_a'].unique()))
assert len(t1) == 2161
t1['donor'] = t1['donor_a']  # T1 is intra-donor by construction
assert (t1['donor_a'] == t1['donor_b']).all()

mets = ['raw_js', 'cosine', 'spearman', 'marker_jaccard', 'k_n', 'k_f']
rows2 = []
ow = t1['exceed_omega'].to_numpy(int)
fpr_w = ow.mean()
print(f'T1 FPR omega = {fpr_w:.4f} ({ow.sum()}/{len(t1)})')
donors = t1['donor'].to_numpy()
uniq_d = np.unique(donors)
for met in mets:
    o = t1[f'exceed_{met}'].to_numpy(int)
    b = int(((ow == 1) & (o == 0)).sum())   # omega flags, metric does not
    c = int(((ow == 0) & (o == 1)).sum())   # metric flags, omega does not
    p_exact = stats.binomtest(min(b, c), b + c, 0.5).pvalue if (b + c) else 1.0
    fpr_m = o.mean()
    d_fpr = fpr_m - fpr_w
    # donor-cluster bootstrap of delta FPR
    B = 10000
    d_boot = np.empty(B)
    ow_s = pd.Series(ow); o_s = pd.Series(o)
    for i in range(B):
        pick = rng.choice(uniq_d, size=len(uniq_d), replace=True)
        idx = np.concatenate([np.where(donors == d)[0] for d in pick])
        d_boot[i] = o[idx].mean() - ow[idx].mean()
    lo, hi = np.percentile(d_boot, [2.5, 97.5])
    p_b = 2 * min((d_boot <= 0).mean(), (d_boot >= 0).mean())
    rows2.append(dict(contrast=f'{met} - omega', fpr_metric=fpr_m, fpr_omega=fpr_w,
                      delta_fpr=d_fpr, mcnemar_b=b, mcnemar_c=c,
                      mcnemar_p_exact=p_exact,
                      clusterboot_ci_lo=lo, clusterboot_ci_hi=hi,
                      clusterboot_p=p_b,
                      n_pairs=len(t1), n_donors=len(uniq_d)))
    print(f'{met}: FPR {fpr_m:.4f} vs omega {fpr_w:.4f} | discord b={b} c={c} '
          f'P_exact={p_exact:.3e} | donor-boot dFPR {d_fpr:+.4f} [{lo:+.4f},{hi:+.4f}] P={p_b:.4f}')
pd.DataFrame(rows2).to_csv('results/nc60_mcnemar_t1.csv', index=False)
print('saved results/nc60_mcnemar_t1.csv')
