# -*- coding: utf-8 -*-
"""
Permutation test for the thalamo-temporal axis enrichment (78)
================================================================
Reviewer request (v40 round, E1-M2 / P2-5): the hypergeometric tests used
for the thalamo-temporal axis enrichment assume independent draws, but the
10 mature-oligodendrocyte Strong candidates share endpoints (MG appears in
3 pairs, TF in 4).  Replace with a permutation test that samples 10 pairs
uniformly without replacement from the 5,778 mature-oligodendrocyte pairs,
preserving the pool's endpoint co-occurrence structure by construction, and
recomputes the axis hit count.

Endpoint sets are identical to 72_brain_setlevel_tests.py:
  thalamic relay nuclei (conservative list, Pu excluded, STH separate),
  STH, temporal-fusiform cortex (TF), and the combined thalamo-temporal
  axis (thalamic relay U STH U TF).

Outputs:
  results/axis_permutation_test.json
  results/axis_permutation_test.txt
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

try:
    from _paths import RESULTS
except Exception:
    RESULTS = Path("results")

IN_CSV = RESULTS / "brain_bs_null_results.csv"
OUT_JSON = RESULTS / "axis_permutation_test.json"
OUT_TXT = RESULTS / "axis_permutation_test.txt"

B_PERM = 100000
SEED = 20260903
N_STRONG = 10

THALAMIC_RELAY = {
    "MG", "LG", "LP", "LP-VPL", "Pul", "VPL", "VA", "MD", "MD-Re", "CM-Pf", "CM",
}
STH_SET = {"STH"}
TF_SET = {"TF"}


def strip(r):
    return r.replace("Human ", "")


def main():
    df = pd.read_csv(IN_CSV)
    ol = df[df["cell_type"] == "Oligodendrocyte"].copy()
    ol["ra"] = ol["region_a"].map(strip)
    ol["rb"] = ol["region_b"].map(strip)
    ol_strong = ol[ol["tier"] == "Strong"]
    assert len(ol_strong) == N_STRONG, f"expected {N_STRONG} Strong, got {len(ol_strong)}"

    n_pool = len(ol)

    def endpoint_hits(d, aset):
        return (d["ra"].isin(aset) | d["rb"].isin(aset)).values

    rng = np.random.RandomState(SEED)
    results = {}
    for tid, aset, label in [
        ("thalamic_relay", THALAMIC_RELAY, "thalamic-relay endpoint"),
        ("TF", TF_SET, "temporal-fusiform (TF) endpoint"),
        ("thalamotemporal", THALAMIC_RELAY | STH_SET | TF_SET,
         "thalamo-temporal axis endpoint (thalamic relay U STH U TF)"),
    ]:
        hits_pool = endpoint_hits(ol, aset)
        hits_obs = endpoint_hits(ol_strong, aset)
        x_obs = int(hits_obs.sum())
        base_rate = float(hits_pool.mean())

        # permutation null: draw n Strong-sized subsets of pairs uniformly
        # without replacement from the pool; endpoint co-occurrence structure
        # of the pool is preserved automatically
        counts = np.empty(B_PERM, dtype=np.int32)
        for b in range(B_PERM):
            idx = rng.choice(n_pool, size=N_STRONG, replace=False)
            counts[b] = hits_pool[idx].sum()
        p_perm = float((counts >= x_obs).mean() + 1) / (B_PERM + 1)
        null_mean = float(counts.mean())
        # hypergeometric for reference
        from scipy import stats
        K = int(hits_pool.sum())
        p_hyp = float(stats.hypergeom.sf(x_obs - 1, n_pool, K, N_STRONG))
        results[tid] = {
            "label": label,
            "observed_hits": x_obs,
            "n_candidates": N_STRONG,
            "pool_base_rate": base_rate,
            "pool_hits": K,
            "pool_n": n_pool,
            "perm_p": p_perm,
            "perm_null_mean": null_mean,
            "perm_null_max": int(counts.max()),
            "hypergeom_p_reference": p_hyp,
        }

    with open(OUT_JSON, "w") as jf:
        json.dump({"B": B_PERM, "seed": SEED, "results": results}, jf, indent=2)

    lines = [
        "Thalamo-temporal axis enrichment: permutation test (78)",
        "=" * 70,
        f"Pool: {n_pool} mature-oligodendrocyte pairs (brain_bs_null_results.csv)",
        f"Observed: {N_STRONG} Strong candidates; B = {B_PERM} permutations",
        "",
    ]
    for tid, r in results.items():
        lines.append(f"[{tid}] {r['label']}")
        lines.append(f"    observed {r['observed_hits']}/{r['n_candidates']} "
                      f"(pool base rate {r['pool_base_rate']:.1%})")
        lines.append(f"    permutation P (>= observed) = {r['perm_p']:.4g}   "
                      f"[null mean {r['perm_null_mean']:.2f}, "
                      f"max {r['perm_null_max']}]")
        lines.append(f"    hypergeometric P (reference, assumes independent "
                      f"draws) = {r['hypergeom_p_reference']:.4g}")
        lines.append("")
    lines.append("Interpretation: the permutation null resamples candidate sets")
    lines.append("from the same pair pool, preserving endpoint co-occurrence;")
    lines.append("it does not require independent endpoint draws. P-values are")
    lines.append("nominal: the axis definition was fixed after inspecting the")
    lines.append("ten candidates (post-hoc, single version reported).")
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"Saved: {OUT_JSON}")
    print(f"Saved: {OUT_TXT}")


if __name__ == "__main__":
    main()
