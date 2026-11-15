"""
Reviewer fix C-D: sensitivity analysis of the Strong/Moderate/Weak tier
thresholds.

Grid: residual threshold res_th in {0.20, 0.25, 0.30, 0.35, 0.40} x omega cap
in {12, 15, 20, 25}. For each combination report:
  - number of Strong candidates
  - per-cell-class counts
  - oligodendrocyte-lineage share of Strong and hypergeometric enrichment P

The 'lowest omega in pair' criterion is retained throughout (it is part of the
Strong definition); sensitivity varies only the two numeric thresholds.
"""
import itertools
import numpy as np
import pandas as pd
from scipy.stats import hypergeom

df = pd.read_csv("results/brain_bs_null_results.csv")
n_total = len(df)
lineage = ["Oligodendrocyte precursor", "Committed oligodendrocyte precursor", "Oligodendrocyte"]
n_lineage = int(df["cell_type"].isin(lineage).sum())

lowest = df["lowest_in_pair"].fillna(False).astype(bool)
res = df["residual"].values
om = df["omega"].values

rows = []
for res_th, om_cap in itertools.product([0.20, 0.25, 0.30, 0.35, 0.40], [12, 15, 20, 25]):
    sel = (res < res_th) & (om < om_cap) & lowest.values
    n_strong = int(sel.sum())
    sub = df[sel]
    k_lin = int(sub["cell_type"].isin(lineage).sum())
    k_opc = int((sub["cell_type"] == "Oligodendrocyte precursor").sum())
    k_copc = int((sub["cell_type"] == "Committed oligodendrocyte precursor").sum())
    k_odo = int((sub["cell_type"] == "Oligodendrocyte").sum())
    if n_strong > 0:
        p_lin = hypergeom.sf(k_lin - 1, n_total, n_lineage, n_strong)
        fold = (k_lin / n_strong) / (n_lineage / n_total)
        share = k_lin / n_strong
    else:
        p_lin, fold, share = np.nan, np.nan, np.nan
    rows.append({
        "res_threshold": res_th, "omega_cap": om_cap, "n_strong": n_strong,
        "OPC": k_opc, "committed_OPC": k_copc, "oligodendrocyte": k_odo,
        "lineage_strong": k_lin, "lineage_share": share,
        "lineage_fold_enrichment": fold, "lineage_hypergeom_P": p_lin,
    })

out = pd.DataFrame(rows)
out.to_csv("results/reviewer_tier_sensitivity.csv", index=False)
print(out.to_string(index=False))

# Baseline check
base = out[(out["res_threshold"] == 0.30) & (out["omega_cap"] == 15)]
print(f"\nBaseline (res<0.3, omega<15): n_strong={base['n_strong'].iloc[0]}, "
      f"lineage share={base['lineage_share'].iloc[0]:.1%}, "
      f"fold={base['lineage_fold_enrichment'].iloc[0]:.2f}, "
      f"P={base['lineage_hypergeom_P'].iloc[0]:.2e}")

sig = out[out["lineage_hypergeom_P"] < 0.05]
print(f"\nCombinations with significant lineage enrichment (P < 0.05): "
      f"{len(sig)}/{len(out)}")
print(f"Lineage share range across grid: "
      f"{out['lineage_share'].min():.1%} - {out['lineage_share'].max():.1%}")
print("Saved -> results/reviewer_tier_sensitivity.csv")
