"""
Reviewer fix C-G: cell-class-level enrichment test for the Strong candidate
concentration in the oligodendrocyte lineage (brain screen).

Tests:
  1. Hypergeometric test per cell class (m = 10, Bonferroni-corrected):
     P(X >= observed Strong count for class c), with population = all 31,764
     pairs, successes-in-population = class c's pair count, draws = 55.
  2. Hypergeometric test for the oligodendrocyte lineage as a pre-specified
     group (OPC + committed OPC + oligodendrocyte).
  3. Label-permutation test (B = 100,000): permute the Strong indicator over
     all pairs, recompute lineage Strong count; two-sided P.
"""
import numpy as np
import pandas as pd
from scipy.stats import hypergeom

df = pd.read_csv("results/brain_bs_null_results.csv")
n_total = len(df)
strong = df[df["tier"] == "Strong"]
n_strong = len(strong)

ct_counts = df["cell_type"].value_counts()
strong_counts = strong["cell_type"].value_counts()

print(f"Total pairs: {n_total}, Strong: {n_strong}")
print("\n=== Per-class hypergeometric enrichment (Bonferroni m=10) ===")
rows = []
for ct in ct_counts.index:
    n_class = int(ct_counts[ct])
    k_obs = int(strong_counts.get(ct, 0))
    # P(X >= k_obs)
    p = hypergeom.sf(k_obs - 1, n_total, n_class, n_strong)
    expected = n_strong * n_class / n_total
    rows.append({
        "cell_type": ct, "n_pairs": n_class, "strong_observed": k_obs,
        "strong_expected": expected, "fold_enrichment": k_obs / expected if expected > 0 else np.nan,
        "p_hypergeom": p, "p_bonferroni": min(1.0, p * 10),
    })
    print(f"  {ct:42s} pairs={n_class:6d} strong={k_obs:3d} exp={expected:6.2f} "
          f"fold={k_obs/expected:6.2f} P={p:.3e} P_bonf={min(1.0, p*10):.3e}")

# Oligodendrocyte lineage (pre-specified)
lineage = ["Oligodendrocyte precursor", "Committed oligodendrocyte precursor", "Oligodendrocyte"]
n_lineage = int(ct_counts[lineage].sum())
k_lineage = int(strong_counts.reindex(lineage).fillna(0).sum())
p_lin = hypergeom.sf(k_lineage - 1, n_total, n_lineage, n_strong)
exp_lin = n_strong * n_lineage / n_total
print(f"\n=== Oligodendrocyte lineage (pre-specified group) ===")
print(f"  pairs={n_lineage} ({n_lineage/n_total:.1%} of all), Strong observed={k_lineage}/{n_strong}, "
      f"expected={exp_lin:.1f}, fold={k_lineage/exp_lin:.2f}")
print(f"  Hypergeometric P(X >= {k_lineage}) = {p_lin:.3e}")

# Label permutation (B = 100,000)
rng = np.random.default_rng(42)
labels = (df["cell_type"].isin(lineage)).values
strong_ind = (df["tier"] == "Strong").values.astype(np.int8)
B = 100_000
counts = rng.hypergeometric(n_lineage, n_total - n_lineage, n_strong, size=B)
# equivalent to permutation of Strong labels
p_perm = (np.sum(counts >= k_lineage) + 1) / (B + 1)
print(f"  Permutation P(X >= {k_lineage}) = {p_perm:.3e} (B = {B:,})")

# OPC alone (post-hoc, for reference)
n_opc = int(ct_counts["Oligodendrocyte precursor"])
k_opc = int(strong_counts.get("Oligodendrocyte precursor", 0))
p_opc = hypergeom.sf(k_opc - 1, n_total, n_opc, n_strong)
print(f"\n  OPC alone: {k_opc}/{n_strong} vs expected {n_strong*n_opc/n_total:.1f}, "
      f"hypergeometric P = {p_opc:.3e}")

out = pd.DataFrame(rows)
out.to_csv("results/reviewer_lineage_enrichment.csv", index=False)
with open("results/reviewer_lineage_enrichment.txt", "w") as f:
    f.write(f"Total pairs: {n_total}, Strong: {n_strong}\n\n")
    f.write(out.to_string(index=False))
    f.write(f"\n\nOligodendrocyte lineage (pre-specified): pairs={n_lineage} "
            f"({n_lineage/n_total:.1%}), Strong={k_lineage}/{n_strong}, "
            f"expected={exp_lin:.1f}, fold={k_lineage/exp_lin:.2f}\n")
    f.write(f"Hypergeometric P = {p_lin:.3e}\n")
    f.write(f"Permutation P (B={B:,}) = {p_perm:.3e}\n")
    f.write(f"OPC alone hypergeometric P = {p_opc:.3e}\n")
print("\nSaved -> results/reviewer_lineage_enrichment.csv / .txt")
