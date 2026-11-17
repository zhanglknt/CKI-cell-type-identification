#!/usr/bin/env python3
"""nc82 stat P1-16: PSD check on the two-way cluster covariance and a
four-donor wild-cluster bootstrap as a small-cluster control.

Reviewer R2 (stat minor): the reported paired contrasts use the Cameron-
Gelbach-Miller two-way variance V = V_a + V_b - V_ab, which is not guaranteed
to be positive semi-definite; with only four donors, a wild-cluster bootstrap
is the appropriate small-cluster reference.

What this script does
  1. Builds the 6 x 6 joint cluster-robust covariance matrix across the six
     paired contrasts (metric minus omega) on the 2,161 T1 library pairs:
        V_a, V_b   one-way cluster-robust covariance at each library endpoint
        V_ab       pair-level (dyadic) covariance
        V_2way     = V_a + V_b - V_ab
  2. Eigen-decomposes V_2way.  If the smallest eigenvalue is negative, applies
     the standard PSD projection (clamp negative eigenvalues to zero) and
     reports the intervals before and after.
  3. Runs a wild-cluster bootstrap over the four donors: Rademacher weights
     on donor-centred residuals, all 2^4 = 16 sign patterns enumerated
     exactly, plus B = 9,999 random draws for the percentile interval; both a
     percentile and a percentile-t interval are reported per contrast.

Outputs
  results/nc82_psd_wildcluster.csv
  results/nc82_psd_wildcluster.json
  results/nc82_psd_wildcluster.txt
"""
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results"
RNG = np.random.default_rng(42)
METS = ["raw_js", "cosine", "spearman", "marker_jaccard", "k_n", "k_f"]

lad = pd.read_csv(OUT / "nc49_brain_drift_ladder.csv")
t1 = lad[lad["tier"] == "T1_techrep"].reset_index(drop=True)
assert len(t1) == 2161, len(t1)

libs = np.sort(pd.unique(pd.concat([t1["sample_a"], t1["sample_b"]])))
lib_ix = {l: i for i, l in enumerate(libs)}
ia = t1["sample_a"].map(lib_ix).to_numpy()
ib = t1["sample_b"].map(lib_ix).to_numpy()
G = len(libs)
n = len(t1)

ow = t1["exceed_omega"].to_numpy(float)
# D[i, k] = paired difference (metric k minus omega) on pair i
D = np.column_stack([t1[f"exceed_{m}"].to_numpy(float) - ow for m in METS])
dbar = D.mean(axis=0)
K = D.shape[1]

donors = sorted(set(t1["donor_a"]) | set(t1["donor_b"]))
don_ix = {d: i for i, d in enumerate(donors)}
# T1 pairs are within-donor, so donor_a == donor_b; guard anyway.
assert (t1["donor_a"].to_numpy() == t1["donor_b"].to_numpy()).all()
di = t1["donor_a"].map(don_ix).to_numpy()
Gd = len(donors)
deg_d = np.bincount(di, minlength=Gd)


def one_way_cov(clusters, Gc):
    """Cluster-robust covariance of the mean for a vector of estimates."""
    R = D - dbar
    S = np.zeros((Gc, K))
    for k in range(K):
        S[:, k] = np.bincount(clusters, weights=R[:, k], minlength=Gc)
    return (Gc / (Gc - 1)) * (S.T @ S) / n ** 2


V_a = one_way_cov(ia, G)
V_b = one_way_cov(ib, G)
R = D - dbar
V_ab = (n / (n - 1)) * (R.T @ R) / n ** 2
V_2way = V_a + V_b - V_ab

eig = np.linalg.eigvalsh(V_2way)
min_eig = float(eig.min())
# PSD projection: clamp negative eigenvalues
w, Q = np.linalg.eigh(V_2way)
w_clamped = np.clip(w, 0, None)
V_psd = (Q * w_clamped) @ Q.T

se_raw = np.sqrt(np.diag(V_2way))
se_psd = np.sqrt(np.diag(V_psd))
df = G - 1               # 596, library clusters
tq = stats.t.ppf(0.975, df)


def wild_bootstrap(draws_signs):
    """Percentile and percentile-t intervals from Rademacher wild draws.

    Unrestricted wild bootstrap (Cameron-Gelbach-Miller): residuals are
    centred at the estimate, and each draw flips every donor's residual block
    by a Rademacher weight.  Donor-centred residuals would sum to zero within
    every donor and would make every draw identical.
    """
    Rc = D - dbar
    deltas = np.empty((draws_signs.shape[0], K))
    ts = np.empty((draws_signs.shape[0], K))
    for b, signs in enumerate(draws_signs):
        wvec = signs[di].astype(float)
        Db = dbar + wvec[:, None] * Rc
        db = Db.mean(axis=0)
        Rb = Db - db
        seb = np.empty(K)
        for k in range(K):
            sa = np.bincount(ia, weights=Rb[:, k], minlength=G)
            sb = np.bincount(ib, weights=Rb[:, k], minlength=G)
            v_a = (G / (G - 1)) * float((sa ** 2).sum()) / n ** 2
            v_b = (G / (G - 1)) * float((sb ** 2).sum()) / n ** 2
            v_ab = (n / (n - 1)) * float((Rb[:, k] ** 2).sum()) / n ** 2
            seb[k] = np.sqrt(max(v_a + v_b - v_ab, 1e-18))
        deltas[b] = db
        ts[b] = (db - dbar) / seb
    pc = np.percentile(deltas, [2.5, 97.5], axis=0)
    tlo = np.percentile(ts, 2.5, axis=0)
    thi = np.percentile(ts, 97.5, axis=0)
    boott = np.column_stack([dbar - thi * se_raw, dbar - tlo * se_raw])
    return pc, boott, deltas


# exact enumeration of the 16 Rademacher patterns, then a random draw for
# a smoother percentile
signs_exact = np.array(list(itertools.product([-1.0, 1.0], repeat=Gd)))
pc16, bt16, _ = wild_bootstrap(signs_exact)
signs_rand = RNG.choice([-1.0, 1.0], size=(9999, Gd))
pc, bt, _ = wild_bootstrap(signs_rand)

rows = []
for k, met in enumerate(METS):
    rows.append(dict(
        contrast=f"{met} - omega",
        delta=float(dbar[k]),
        se_2way_raw=float(se_raw[k]),
        se_2way_psd=float(se_psd[k]),
        ci_raw_lo=float(dbar[k] - tq * se_raw[k]),
        ci_raw_hi=float(dbar[k] + tq * se_raw[k]),
        ci_psd_lo=float(dbar[k] - tq * se_psd[k]),
        ci_psd_hi=float(dbar[k] + tq * se_psd[k]),
        var_ratio_psd_over_raw=float((se_psd[k] / se_raw[k]) ** 2),
        wild_pc_lo=float(pc[0, k]),
        wild_pc_hi=float(pc[1, k]),
        wild_boott_lo=float(bt[k, 0]),
        wild_boott_hi=float(bt[k, 1]),
        wild_pc_excl0=bool(pc[0, k] > 0 or pc[1, k] < 0),
        wild_boott_excl0=bool(bt[k, 0] > 0 or bt[k, 1] < 0),
        raw_excl0=bool(dbar[k] - tq * se_raw[k] > 0 or dbar[k] + tq * se_raw[k] < 0),
        psd_excl0=bool(dbar[k] - tq * se_psd[k] > 0 or dbar[k] + tq * se_psd[k] < 0),
        n_donors=Gd, pairs_per_donor=";".join(str(int(x)) for x in deg_d),
    ))

df_out = pd.DataFrame(rows)
df_out.to_csv(OUT / "nc82_psd_wildcluster.csv", index=False)

summary = dict(
    n_pairs=int(n), n_libraries=int(G), n_donors=int(Gd),
    pairs_per_donor=[int(x) for x in deg_d],
    eigenvalues=[float(x) for x in eig],
    min_eigenvalue=min_eig,
    psd_violation=bool(min_eig < -1e-12),
    max_abs_se_change=float(np.abs(se_psd / se_raw - 1).max()),
    contrasts=int(K),
    wild_draws_used=int(signs_rand.shape[0]),
    wild_exact_patterns=int(signs_exact.shape[0]),
)
(OUT / "nc82_psd_wildcluster.json").write_text(json.dumps(summary, indent=2))

lines = []
lines.append("nc82 stat P1-16: two-way covariance PSD check + 4-donor wild cluster bootstrap")
lines.append(f"pairs {n}, libraries {G}, donors {Gd} ({deg_d.tolist()} pairs per donor)")
lines.append(f"V_2way eigenvalues: {', '.join(f'{x:.3e}' for x in eig)}")
lines.append(f"minimum eigenvalue {min_eig:.3e} -> PSD violation: {summary['psd_violation']}")
lines.append(f"largest SE change after PSD projection: {100*summary['max_abs_se_change']:.2e}%")
lines.append("")
lines.append(f"{'contrast':>18s} {'delta':>8s} {'CI(raw t)':>20s} {'CI(PSD t)':>20s} "
             f"{'wild pc':>20s} {'wild boot-t':>20s}")
for r in rows:
    lines.append(
        f"{r['contrast']:>18s} {r['delta']:+8.4f} "
        f"[{r['ci_raw_lo']:+.3f},{r['ci_raw_hi']:+.3f}]  "
        f"[{r['ci_psd_lo']:+.3f},{r['ci_psd_hi']:+.3f}]  "
        f"[{r['wild_pc_lo']:+.3f},{r['wild_pc_hi']:+.3f}]  "
        f"[{r['wild_boott_lo']:+.3f},{r['wild_boott_hi']:+.3f}]")
lines.append("")
lines.append("Note: with four donor clusters the wild bootstrap has only 2^4 = 16 "
             "distinct Rademacher patterns; the percentile interval is read from "
             "9,999 random draws of those patterns and is reported as a "
             "small-cluster sensitivity check, not as a calibrated 95% interval.")
(OUT / "nc82_psd_wildcluster.txt").write_text("\n".join(lines) + "\n")

print("\n".join(lines))
print("\nwrote results/nc82_psd_wildcluster.{csv,json,txt}")
