"""
CKI Brain Block-Shuffle Null — Results Processing (08e)
========================================================
Reads the outputs of 08d_brain_blockshuffle_null.py and computes:

1. Per-pair one-sided LOWER permutation P-values from the null matrices
   (migration-candidate direction: omega anomalously LOW vs block-shuffle null):
       P_i = (# null_omega <= observed_omega_i + 1) / (B + 1)
   Upper-tail P (anomalously high differentiation) is also stored as p_perm_high.
2. BH-FDR (Benjamini-Hochberg) q-values across ALL 31,764 brain pairs.
3. Tier breakdown of significant pairs at q<0.05 / q<0.10 / p<0.05.
4. Per-CT summary with permutation-based P and SES (already in ct_test.csv),
   plus per-CT FDR-adjusted counts.

This directly addresses Critical issue C1 of the v5 expert review
(31,764 comparisons without FDR; P-value floor at 9.99e-5; dual selection):
the block-shuffle null preserves the cell-type x region joint distribution,
and the P-value resolution is now 1/(B+1) = 1e-3 (no floor saturation).

Outputs (RESULTS_DIR):
    brain_bs_null_results.csv       pairs + omega + null P + BH q + tier
    brain_bs_null_summary.txt       human-readable summary of FDR outcomes
    brain_bs_null_fdr_manifest.json run metadata
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR q-values with tie handling."""
    p = np.asarray(pvals, dtype=float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n, dtype=float)
    running = np.inf
    for i in order[::-1]:
        # rank = number of p-values <= p[i] (ties share the largest rank)
        rank = np.searchsorted(p, p[i], side='right')
        val = p[i] * n / rank
        running = min(running, val)
        q[i] = running
    return np.minimum(q, 1.0)


def main():
    print("=" * 60)
    print("Brain block-shuffle null: results processing")
    print("=" * 60)

    pairs_path = RESULTS_DIR / 'brain_bs_null_observed_pairs.csv'
    ct_path = RESULTS_DIR / 'brain_bs_null_ct_test.csv'
    if not pairs_path.exists():
        raise SystemExit(f"Missing {pairs_path} — run 08d first")

    pairs = pd.read_csv(pairs_path)
    print(f"Loaded {len(pairs)} observed pairs")

    # per-pair permutation P from null matrices
    p_vals = np.full(len(pairs), np.nan)
    p_hi_vals = np.full(len(pairs), np.nan)
    B_used = None
    for ct in pairs['cell_type'].unique():
        ct_mask = (pairs['cell_type'] == ct).values
        obs = pairs.loc[ct_mask, 'omega'].values
        npy = RESULTS_DIR / f"brain_bs_null_pairs_{ct.replace(' ', '_')}.npy"
        if not npy.exists():
            print(f"  WARNING: missing null matrix for {ct}: {npy}")
            continue
        null = np.load(npy)          # (n_pairs, B)
        B = null.shape[1]
        B_used = B
        # one-sided lower (migration candidates: omega anomalously LOW):
        # P = (#null <= obs + 1)/(B+1)
        n_le = (null <= obs[:, None]).sum(axis=1)
        p_vals[ct_mask] = (n_le + 1) / (B + 1)
        # one-sided upper (anomalously high differentiation), reference only
        n_ge = (null >= obs[:, None]).sum(axis=1)
        p_hi_vals[ct_mask] = (n_ge + 1) / (B + 1)
        print(f"  {ct}: {ct_mask.sum()} pairs, B={B}, "
              f"P_low range [{p_vals[ct_mask].min():.4f}, {p_vals[ct_mask].max():.4f}]")

    pairs['p_perm'] = p_vals
    pairs['p_perm_high'] = p_hi_vals

    # BH-FDR over all pairs with non-NaN P
    ok = ~np.isnan(p_vals)
    q_vals = np.full(len(pairs), np.nan)
    q_vals[ok] = bh_fdr(p_vals[ok])
    pairs['q_fdr'] = q_vals

    # tier breakdown
    print("\n" + "-" * 60)
    print("FDR outcome by tier (all 31,764 brain pairs)")
    print("-" * 60)
    for tier in ['Strong', 'Moderate', 'Weak', 'None']:
        sub = pairs[pairs['tier'] == tier]
        if len(sub) == 0:
            continue
        n_q05 = int((sub['q_fdr'] < 0.05).sum())
        n_q10 = int((sub['q_fdr'] < 0.10).sum())
        n_p05 = int((sub['p_perm'] < 0.05).sum())
        print(f"  {tier:9s} n={len(sub):6d}  q<0.05: {n_q05:5d}  "
              f"q<0.10: {n_q10:5d}  p<0.05: {n_p05:5d}")

    # per-CT FDR summary
    print("\n" + "-" * 60)
    print("Per-CT FDR summary")
    print("-" * 60)
    ct_rows = []
    for ct, sub in pairs.groupby('cell_type'):
        ct_rows.append({
            'cell_type': ct,
            'n_pairs': len(sub),
            'q<0.05': int((sub['q_fdr'] < 0.05).sum()),
            'q<0.10': int((sub['q_fdr'] < 0.10).sum()),
            'p<0.05': int((sub['p_perm'] < 0.05).sum()),
            'p<0.01': int((sub['p_perm'] < 0.01).sum()),
            'min_q': float(sub['q_fdr'].min()) if len(sub) else np.nan,
        })
    ct_summary = pd.DataFrame(ct_rows).sort_values('min_q')
    print(ct_summary.to_string(index=False))

    # save
    out_csv = RESULTS_DIR / 'brain_bs_null_results.csv'
    pairs.to_csv(out_csv, index=False)
    print(f"\nSaved: {out_csv}")

    # human-readable summary
    summary_lines = [
        "=" * 60,
        "Brain block-shuffle null (C1) — FDR summary",
        "=" * 60,
        f"B = {B_used} permutations (block = 10x library / sample_id)",
        f"Total pairs = {len(pairs)}",
        "",
        "All pairs (BH-FDR over all brain pairs):",
        f"  q < 0.05 : {int((pairs['q_fdr'] < 0.05).sum())}",
        f"  q < 0.10 : {int((pairs['q_fdr'] < 0.10).sum())}",
        f"  p < 0.05 (raw) : {int((pairs['p_perm'] < 0.05).sum())}",
        "",
        "By tier:",
    ]
    for tier in ['Strong', 'Moderate', 'Weak', 'None']:
        sub = pairs[pairs['tier'] == tier]
        if len(sub) == 0:
            continue
        summary_lines.append(
            f"  {tier:9s} n={len(sub):6d}  q<0.05: {int((sub['q_fdr']<0.05).sum()):5d}  "
            f"q<0.10: {int((sub['q_fdr']<0.10).sum()):5d}  p<0.05: {int((sub['p_perm']<0.05).sum()):5d}")
    summary_lines.append("")
    summary_lines.append("Strong candidates surviving FDR:")
    strong_sig = pairs[(pairs['tier'] == 'Strong') & (pairs['q_fdr'] < 0.05)]
    if len(strong_sig):
        for _, r in strong_sig.iterrows():
            summary_lines.append(
                f"  {r['cell_type']:<35s} {r['region_a']:<35s} {r['region_b']:<35s} "
                f"omega={r['omega']:8.3f} residual={r['residual']:5.3f} "
                f"p={r['p_perm']:.4f} q={r['q_fdr']:.4f}")
    else:
        summary_lines.append("  (none at q<0.05)")
    summary_lines.append("")
    summary_lines.append("Strong candidates with raw p<0.05 (hypothesis-generating):")
    strong_p = pairs[(pairs['tier'] == 'Strong') & (pairs['p_perm'] < 0.05)]
    if len(strong_p):
        for _, r in strong_p.iterrows():
            summary_lines.append(
                f"  {r['cell_type']:<35s} {r['region_a']:<35s} {r['region_b']:<35s} "
                f"omega={r['omega']:8.3f} residual={r['residual']:5.3f} "
                f"p={r['p_perm']:.4f} q={r['q_fdr']:.4f}")
    else:
        summary_lines.append("  (none at p<0.05)")

    summary_txt = RESULTS_DIR / 'brain_bs_null_summary.txt'
    with open(summary_txt, 'w') as f:
        f.write("\n".join(summary_lines))
    print(f"Saved: {summary_txt}")

    manifest = {
        'script': '08e_brain_blockshuffle_results.py',
        'B': B_used,
        'n_pairs_total': int(len(pairs)),
        'n_q<0.05': int((pairs['q_fdr'] < 0.05).sum()),
        'n_q<0.10': int((pairs['q_fdr'] < 0.10).sum()),
        'n_p<0.05': int((pairs['p_perm'] < 0.05).sum()),
    }
    with open(RESULTS_DIR / 'brain_bs_null_fdr_manifest.json', 'w') as jf:
        json.dump(manifest, jf, indent=2, default=str)
    print("Done!")


if __name__ == '__main__':
    main()
