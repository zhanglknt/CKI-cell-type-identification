# -*- coding: utf-8 -*-
"""
nc52_brain_candidate_effectsize.py — NC v52 C3.

Supp Fig. 7b reports that the omega rankings under the per-pair k_n
estimator (used throughout) and a global-k_n variant correlate at only
Spearman rho = 0.142 (P = 7.1e-143; rho^2 ~ 0.02 explained variance).
This script quantifies what that estimator sensitivity means for the
regional candidate screen:

  1. effect size: rho, rho^2, plus median |log2 fold change| of omega
     between the two estimators (per-pair table
     results/phaseC_omega_pair_vs_global.csv, 31,764 pairs);
  2. candidate-set sensitivity: the multiplicative-residual Strong tier
     (residual < 0.3, omega < 15, lowest omega in region pair) is
     recomputed under global-k_n omega, using the same expected-value
     model (expected = mu_ct * mu_pair / mu_grand) re-derived on
     global-k_n values; we report how many of the 39 Strong candidates
     persist, how many are lost / newly gained, and the rank
     correlation of per-pair residuals between the two estimators.

Inputs : results/phaseC_omega_pair_vs_global.csv
         results/brain_bs_null_observed_pairs.csv (tiers + residuals)
Output : results/nc52_brain_candidate_effectsize.csv

Seed: none (deterministic).
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT = PROJECT_ROOT / "results"
_t0 = time.time()


def log(msg):
    print(f"[{time.time()-_t0:6.0f}s] {msg}", flush=True)


om = pd.read_csv(OUT / "phaseC_omega_pair_vs_global.csv")
obs = pd.read_csv(OUT / "brain_bs_null_observed_pairs.csv")
log(f"pairs: {len(om)}; observed-with-tier: {len(obs)}")

key = ["cell_type", "region_a", "region_b"]
df = om.merge(obs[key + ["residual", "lowest_in_pair", "tier"]],
              on=key, how="left", validate="1:1")
# tier is NaN for pairs passing no tier (residual >= 0.75 or omega >= 35)
assert df["residual"].notna().all()

# ---- 1. effect size ------------------------------------------------------
rho, p_rho = spearmanr(df["omega"], df["omega_global_kn"])
log2fc = np.log2(df["omega"] / df["omega_global_kn"])
med_abs_log2fc = float(np.median(np.abs(log2fc)))
log(f"rho={rho:.3f} (published 0.142), rho^2={rho**2:.4f}, "
    f"median |log2 FC|={med_abs_log2fc:.2f}")

# ---- 2. candidate-set sensitivity ---------------------------------------
def strong_set(frame, omega_col):
    """Recompute multiplicative model + Strong tier on a given omega."""
    mu_ct = frame.groupby("cell_type")[omega_col].mean()
    rp = frame.apply(lambda r: tuple(sorted([r.region_a, r.region_b])),
                     axis=1)
    mu_pair = frame.groupby(rp)[omega_col].mean()
    mu_grand = frame[omega_col].mean()
    fr = frame.copy()
    fr["rp"] = rp
    fr["mu_ct"] = fr["cell_type"].map(mu_ct)
    fr["mu_pair"] = fr["rp"].map(mu_pair)
    fr["expected"] = fr["mu_ct"] * fr["mu_pair"] / mu_grand
    fr["resid_new"] = fr[omega_col] / fr["expected"]
    # lowest omega within region pair (across cell types)
    fr["lowest_new"] = fr.groupby("rp")[omega_col].transform(
        lambda s: s == s.min())
    strong = fr[(fr["resid_new"] < 0.3) & (fr[omega_col] < 15)
                & fr["lowest_new"]]
    return fr, strong


fr_p, strong_published = strong_set(df, "omega")
fr_g, strong_global = strong_set(df, "omega_global_kn")

# published Strong set from the authoritative tier column
strong_orig = df[df["tier"] == "Strong"]
log(f"Strong (authoritative tier col): {len(strong_orig)}; "
    f"recomputed on per-pair omega: {len(strong_published)}; "
    f"recomputed on global-k_n omega: {len(strong_global)}")

k = key
set_orig = set(map(tuple, strong_orig[k].values))
set_global = set(map(tuple, strong_global[k].values))
persist = set_orig & set_global
lost = set_orig - set_global
gained = set_global - set_orig
log(f"persist={len(persist)}, lost={len(lost)}, gained={len(gained)}")

rho_resid, p_resid = spearmanr(fr_p["resid_new"], fr_g["resid_new"])
log(f"residual rank correlation between estimators: {rho_resid:.3f}")

rows = [
    {"quantity": "spearman_omega_perpair_vs_global", "value": round(rho, 4),
     "note": "published 0.142 (Supp Fig. 7b)"},
    {"quantity": "explained_variance_rho2", "value": round(rho ** 2, 4),
     "note": "~2% of omega ranking variance shared between estimators"},
    {"quantity": "spearman_p", "value": f"{p_rho:.2e}", "note": ""},
    {"quantity": "median_abs_log2FC_omega", "value": round(med_abs_log2fc, 3),
     "note": "median |log2(per-pair-k_n omega / global-k_n omega)|"},
    {"quantity": "n_strong_published", "value": len(strong_orig),
     "note": "authoritative tier column, brain_bs_null_observed_pairs.csv"},
    {"quantity": "n_strong_recomputed_perpair", "value": len(strong_published),
     "note": "multiplicative model re-derived on per-pair omega (sanity)"},
    {"quantity": "n_strong_global_kn", "value": len(strong_global),
     "note": "same screen re-derived on global-k_n omega"},
    {"quantity": "n_strong_persist", "value": len(persist),
     "note": "candidates Strong under both estimators"},
    {"quantity": "n_strong_lost", "value": len(lost),
     "note": "published Strong candidates lost under global-k_n"},
    {"quantity": "n_strong_gained", "value": len(gained),
     "note": "new Strong candidates under global-k_n"},
    {"quantity": "frac_persist", "value": round(len(persist) / max(len(set_orig), 1), 3),
     "note": "fraction of published Strong set surviving estimator switch"},
    {"quantity": "spearman_residual_perpair_vs_global",
     "value": round(rho_resid, 4),
     "note": f"rank correlation of multiplicative residuals (P={p_resid:.1e})"},
]
pd.DataFrame(rows).to_csv(OUT / "nc52_brain_candidate_effectsize.csv",
                          index=False)
log(f"saved {OUT/'nc52_brain_candidate_effectsize.csv'}")
log("DONE")
