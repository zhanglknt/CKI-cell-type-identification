# -*- coding: utf-8 -*-
"""
Set-level coherence checks for the brain block-shuffle null analysis (post-hoc).

Motivation (reviewer-facing, honest framing):
  The pair-level block-shuffle null (B=1000, m=31,764 region pairs) yields no
  q<0.05 survivors after BH (min q = 0.520).  However, the RAW p-value
  distribution is strongly enriched among high-effect (Strong-tier) pairs,
  and the mature-oligodendrocyte Strong candidates cluster on a
  thalamo-temporal axis.  These are post-hoc coherence checks, NOT
  FDR-controlled discovery claims.

Tests implemented:
  S1. Global enrichment: hypergeometric P(P<0.05 | Strong) vs overall rate.
  S2. Dose-response: Cochran-Armitage trend of P(raw p<0.05) across
      effect tiers (unclassified < Weak < Moderate < Strong), plus
      Mann-Whitney U and KS tests on the raw p_perm distributions.
  S3. Mature-OL axis enrichment: among mature oligodendrocyte pairs
      (n=5,778), enrichment of (a) thalamic-relay endpoints,
      (b) temporal-fusiform (TF) endpoints, (c) combined
      thalamo-temporal axis (thalamic relay ∪ STH ∪ TF) among the 10
      Strong candidates, vs base rates over all mature-OL pairs.

Outputs:
  results/brain_setlevel_tests.csv   (one row per test, effect + P)
  results/brain_setlevel_tests.txt   (human-readable summary)
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

try:
    from _paths import RESULTS
except Exception:
    RESULTS = Path("results")

IN_CSV = RESULTS / "brain_bs_null_results.csv"
OUT_CSV = RESULTS / "brain_setlevel_tests.csv"
OUT_TXT = RESULTS / "brain_setlevel_tests.txt"

# ---------------------------------------------------------------- load
df = pd.read_csv(IN_CSV)
df["region_a"] = df["region_a"].astype(str)
df["region_b"] = df["region_b"].astype(str)

N = len(df)
sig = (df["p_perm"] < 0.05)
K = int(sig.sum())                      # total raw p<0.05
p_global = K / N

tier_of = df["tier"].fillna("Unclassified")
strong = df[tier_of == "Strong"]
n_strong = len(strong)
x_strong = int((strong["p_perm"] < 0.05).sum())
rate_strong = x_strong / n_strong

rows = []  # (test_id, description, effect, p_value)

# ---------------------------------------------------------------- S1
# Hypergeometric: probability that >= x_strong of the n_strong Strong pairs
# are raw-p<0.05, given the global base rate K/N.
p_s1 = stats.hypergeom.sf(x_strong - 1, N, K, n_strong)
rows.append((
    "S1_global_enrichment",
    f"Strong-tier pairs with raw p<0.05: {x_strong}/{n_strong} ({rate_strong:.1%}) "
    f"vs overall {K}/{N} ({p_global:.1%}); hypergeometric enrichment",
    rate_strong,
    p_s1,
))

# ---------------------------------------------------------------- S2
# Dose-response across tiers (unclassified < Weak < Moderate < Strong)
tier_order = ["Unclassified", "Weak", "Moderate", "Strong"]
tier_score = {t: i for i, t in enumerate(tier_order)}
counts, succ, n_i, w_i = [], [], [], []
for t in tier_order:
    m = (tier_of == t).values
    ni = int(m.sum())
    xi = int(sig[m].sum())
    counts.append(f"{t} {xi}/{ni} ({xi/ni:.1%})")
    n_i.append(ni)
    succ.append(xi)
    w_i.append(tier_score[t])

n_i = np.array(n_i, float)
xi = np.array(succ, float)
w_i = np.array(w_i, float)
N_tot = n_i.sum()
X_tot = xi.sum()
pbar = X_tot / N_tot
# Cochran-Armitage trend statistic (Agresti 2002, eq. 5.24)
num = np.sum(w_i * (xi - n_i * pbar))
den = np.sqrt(pbar * (1 - pbar) * (np.sum(w_i**2 * n_i) - (np.sum(w_i * n_i)) ** 2 / N_tot))
z_ca = num / den
p_ca = 2 * stats.norm.sf(abs(z_ca))
rows.append((
    "S2_dose_response_CA",
    f"Raw p<0.05 rate by tier: {'; '.join(counts)}; Cochran-Armitage trend z={z_ca:.2f}",
    z_ca,
    p_ca,
))

# Mann-Whitney U: Strong p_perm vs all others
u_stat, p_mwu = stats.mannwhitneyu(
    strong["p_perm"], df[tier_of != "Strong"]["p_perm"], alternative="less"
)
rows.append((
    "S2_strong_vs_rest_MWU",
    f"Strong raw p_perm stochastically smaller than rest; MWU U={u_stat:.0f}",
    u_stat,
    p_mwu,
))

# KS test: distribution shape
ks_stat, p_ks = stats.ks_2samp(strong["p_perm"], df[tier_of != "Strong"]["p_perm"])
rows.append((
    "S2_strong_vs_rest_KS",
    f"KS two-sample on raw p_perm; D={ks_stat:.3f}",
    ks_stat,
    p_ks,
))

# ---------------------------------------------------------------- S3
# Region-set definitions (conservative thalamic-relay nuclei; Pu=putamen
# excluded, STH=subthalamic listed separately, TF=temporal fusiform cortex)
def strip(r):
    return r.replace("Human ", "")

THALAMIC_RELAY = {
    "MG", "LG", "LP", "LP-VPL", "Pul", "VPL", "VA", "MD", "MD-Re", "CM-Pf", "CM",
}
STH_SET = {"STH"}
TF_SET = {"TF"}

ol = df[df["cell_type"] == "Oligodendrocyte"].copy()
ol["ra"] = ol["region_a"].map(strip)
ol["rb"] = ol["region_b"].map(strip)
ol_strong = ol[ol["tier"] == "Strong"]
n_ol, n_ol_strong = len(ol), len(ol_strong)

def endpoint_hits(d, aset):
    a = d["ra"].isin(aset) | d["rb"].isin(aset)
    return a

for tid, aset, label in [
    ("S3_OL_thalamic_endpoint", THALAMIC_RELAY, "thalamic-relay endpoint"),
    ("S3_OL_TF_endpoint", TF_SET, "temporal-fusiform (TF) endpoint"),
    ("S3_OL_thalamotemporal", THALAMIC_RELAY | STH_SET | TF_SET,
     "thalamo-temporal axis endpoint (thalamic relay ∪ STH ∪ TF)"),
]:
    hit_all = endpoint_hits(ol, aset)
    K_ol = int(hit_all.sum())
    x_ol = int(hit_all[ol_strong.index].sum())
    rate_base = K_ol / n_ol
    rate_obs = x_ol / n_ol_strong
    p_enr = stats.hypergeom.sf(x_ol - 1, n_ol, K_ol, n_ol_strong)
    rows.append((
        tid,
        f"Mature-OL Strong candidates with {label}: {x_ol}/{n_ol_strong} "
        f"({rate_obs:.0%}) vs base rate {K_ol}/{n_ol} ({rate_base:.1%}); "
        f"hypergeometric enrichment",
        rate_obs,
        p_enr,
    ))

# Pair list of the OL Strong candidates for the record
ol_pairs_txt = ", ".join(
    f"{a}–{b}" for a, b in zip(ol_strong["ra"], ol_strong["rb"])
)

# ---------------------------------------------------------------- write
out = pd.DataFrame(rows, columns=["test_id", "description", "effect", "p_value"])
out.to_csv(OUT_CSV, index=False)

lines = [
    "Set-level coherence checks (post-hoc; NOT FDR-controlled discovery)",
    "=" * 70,
    f"Input: {IN_CSV}  (m = {N} region pairs, B = 1000 block-shuffle null)",
    f"Overall raw p<0.05: {K}/{N} = {p_global:.2%}",
    "",
]
for tid, desc, eff, p in rows:
    lines.append(f"[{tid}] {desc}")
    lines.append(f"    effect = {eff:.4g}    P = {p:.3g}")
    lines.append("")
lines += [
    "Mature-oligodendrocyte Strong candidates (n=10):",
    f"  {ol_pairs_txt}",
    "",
    "Interpretation guardrails:",
    "  - These are post-hoc coherence checks in a single dataset; the tier",
    "    variable and the axis definition were chosen after inspecting the",
    "    data. They support 'the signal is not random noise' but do not",
    "    substitute for pair-level FDR control (min q = 0.520).",
]
OUT_TXT.write_text("\n".join(lines), encoding="utf-8")

print("\n".join(lines))
print(f"\nSaved: {OUT_CSV}")
print(f"Saved: {OUT_TXT}")
