#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
P1-4 (blind-review round 1, E1-M4 + E2-M5): selection-rule-matched null
for the thalamo-temporal axis enrichment of mature-oligodendrocyte
Strong candidates.

Reviewer complaint: the published axis permutation test (notebook 78)
draws 10 pairs uniformly without replacement from the 5,778-pair
oligodendrocyte pool.  This preserves the pool's endpoint co-occurrence
structure but NOT the Strong selection rule: the rule (low omega with
high multiplicative deviation, lowest-in-pair) has its own region
composition signature, and survivors of the rule are not a uniform
subset of the pool.  The microglia composition analysis
(_v38_candidate_composition.py B) already uses a rule-matched null
(the Strong rule re-evaluated on every block-shuffle permutation); the
axis test is brought to the same specification here.

For each of the B = 1,000 block-shuffle permutations:
  1. re-evaluate the Strong rule (residual < 0.3, null omega < 15,
     lowest-in-pair across cell types) on the null omega values,
     exactly as in the microglia composition addendum (S1b);
  2. collect the surviving mature-oligodendrocyte pairs;
  3. count axis-endpoint hits among the survivors.

The null distribution of hit counts (and of the hit rate among
survivors) is compared with the observed 6/10 thalamic-relay, 4/10
temporal-fusiform, and 9/10 combined-axis counts.

Inputs:
  results/brain_bs_null_results.csv
  results/brain_bs_null_pairs_<cell_type>.npy   (all classes)

Outputs:
  results/axis_rule_matched_null.json
  results/axis_rule_matched_null.txt
"""

import json
import os

import numpy as np
import pandas as pd

RESULTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      'results')

THALAMIC_RELAY = {
    "MG", "LG", "LP", "LP-VPL", "Pul", "VPL", "VA", "MD", "MD-Re", "CM-Pf", "CM",
}
STH_SET = {"STH"}
TF_SET = {"TF"}


def strip(r):
    return r.replace("Human ", "")


def main():
    res = pd.read_csv(os.path.join(RESULTS, "brain_bs_null_results.csv"))
    cts = list(res["cell_type"].unique())
    nulls = {}
    B_perm = None
    for ct in cts:
        nulls[ct] = np.load(
            os.path.join(RESULTS, f"brain_bs_null_pairs_{ct.replace(' ', '_')}.npy"))
        B_perm = nulls[ct].shape[1]

    # ---- observed Strong oligodendrocyte candidates ----
    ol = res[res["cell_type"] == "Oligodendrocyte"].copy()
    ol["ra"] = ol["region_a"].map(strip)
    ol["rb"] = ol["region_b"].map(strip)
    ol_strong = ol[ol["tier"] == "Strong"]
    n_obs = len(ol_strong)

    def hits(d, aset):
        return (d["ra"].isin(aset) | d["rb"].isin(aset)).values

    # ---- rule-matched null: Strong rule re-evaluated per permutation ----
    # (mirrors _v38_candidate_composition.py section B exactly)
    gp_keys = [tuple(sorted(t)) for t in zip(res["region_a"], res["region_b"])]
    gp_ids, _ = pd.factorize(pd.Series(gp_keys))
    ct_rows = {ct: (res["cell_type"] == ct).values for ct in cts}
    gp_of_ct = {ct: gp_ids[ct_rows[ct]] for ct in cts}

    mu_ct_null = {ct: nulls[ct].mean(axis=0) for ct in cts}
    n_ct = {ct: nulls[ct].shape[0] for ct in cts}
    grand_null = sum(n_ct[ct] * mu_ct_null[ct] for ct in cts) / sum(n_ct.values())

    n_gp = len(set(gp_ids))
    sum_val = np.zeros((n_gp, B_perm))
    cnt_gp = np.zeros(n_gp)
    min_val = np.full((n_gp, B_perm), np.inf)
    for ct in cts:
        g = gp_of_ct[ct]
        nv = nulls[ct].astype(np.float64)
        sum_val[g] += nv
        cnt_gp[g] += 1
        min_val[g] = np.minimum(min_val[g], nv)
    mu_pair_null = sum_val / cnt_gp[:, None]

    # Oligodendrocyte rule-matched Strong mask per permutation
    ct = "Oligodendrocyte"
    g = gp_of_ct[ct]
    nv = nulls[ct].astype(np.float64)
    exp = mu_ct_null[ct][None, :] * mu_pair_null[g] / grand_null[None, :]
    resid = nv / exp
    lowest = nv <= min_val[g]
    strong_null = (resid < 0.3) & (nv < 15) & lowest       # (n_ol_pairs, B)

    # per-pair endpoint hit indicators for the oligodendrocyte pool
    ol_all = ol.reset_index(drop=True)
    hit_vecs = {}
    for tid, aset in [
        ("thalamic_relay", THALAMIC_RELAY),
        ("TF", TF_SET),
        ("thalamotemporal", THALAMIC_RELAY | STH_SET | TF_SET),
    ]:
        hit_vecs[tid] = hits(ol_all, aset).astype(float)

    # count hits among null survivors, per permutation
    n_surv = strong_null.sum(axis=0)
    counts = {tid: (strong_null * hv[:, None]).sum(axis=0)
              for tid, hv in hit_vecs.items()}

    # ---- summarize vs observed ----
    out = {}
    for tid, label in [
        ("thalamic_relay", "thalamic-relay endpoint"),
        ("TF", "temporal-fusiform (TF) endpoint"),
        ("thalamotemporal", "thalamo-temporal axis (thalamic relay U STH U TF)"),
    ]:
        obs_hits = int(hits(ol_strong, THALAMIC_RELAY if tid == "thalamic_relay"
                             else TF_SET if tid == "TF"
                             else THALAMIC_RELAY | STH_SET | TF_SET).sum())
        nc = counts[tid]
        p_hits = float((1 + int((nc >= obs_hits).sum())) / (B_perm + 1))
        # rate comparison: hits per surviving candidate
        with np.errstate(divide='ignore', invalid='ignore'):
            rate = np.where(n_surv > 0, nc / np.maximum(n_surv, 1), np.nan)
        valid = ~np.isnan(rate)
        p_rate = (float((1 + int((rate[valid] >= obs_hits / n_obs).sum()))
                        / (valid.sum() + 1))) if valid.any() else float('nan')
        out[tid] = {
            "label": label,
            "observed_hits": obs_hits,
            "observed_candidates": int(n_obs),
            "null_mean_hits": float(nc.mean()),
            "null_max_hits": int(nc.max()),
            "p_hits": p_hits,
            "null_mean_survivors": float(n_surv.mean()),
            "null_mean_rate": float(np.nanmean(rate)),
            "p_rate": p_rate,
            "uniform_draw_null_mean": None,  # filled below for reference
        }

    # reference: uniform-draw null means from notebook 78
    # (tids are nested under the "results" key of axis_permutation_test.json)
    ref = json.load(open(os.path.join(RESULTS, "axis_permutation_test.json")))
    ref_results = ref.get("results", {})
    for tid in out:
        if tid in ref_results:
            out[tid]["uniform_draw_null_mean"] = ref_results[tid].get("perm_null_mean")
    _n_ref = sum(1 for tid in out if out[tid]["uniform_draw_null_mean"] is not None)
    assert _n_ref == len(out), (
        f"uniform-draw reference missing for {len(out) - _n_ref} endpoint(s); "
        "check axis_permutation_test.json structure")

    summary = {
        "B_perm": int(B_perm),
        "strong_rule": "residual < 0.3, null omega < 15, lowest-in-pair",
        "note": "Strong rule re-evaluated on each block-shuffle permutation "
                "(same specification as the microglia composition addendum "
                "S1b); hit counts are tallied among the surviving "
                "mature-oligodendrocyte pairs per permutation.",
        "n_surv_mean": float(n_surv.mean()),
        "n_surv_percentiles": [float(np.percentile(n_surv, q)) for q in (2.5, 50, 97.5)],
        "tests": out,
    }

    with open(os.path.join(RESULTS, "axis_rule_matched_null.json"), "w") as f:
        json.dump(summary, f, indent=2)

    lines = ["=" * 72,
             "P1-4: selection-rule-matched null for the thalamo-temporal axis",
             "=" * 72, "",
             f"Strong rule re-evaluated on each of B = {B_perm} block-shuffle "
             "permutations; axis hits tallied among surviving "
             "mature-oligodendrocyte pairs.", "",
             f"null survivors per permutation: mean {n_surv.mean():.1f}, "
             f"95% [{np.percentile(n_surv, 2.5):.0f}, {np.percentile(n_surv, 97.5):.0f}]", ""]
    for tid, d in out.items():
        lines.append(f"  {d['label']}:")
        lines.append(f"    observed {d['observed_hits']}/{d['observed_candidates']}")
        lines.append(f"    rule-matched null hits: mean {d['null_mean_hits']:.2f}, "
                     f"max {d['null_max_hits']}, P {d['p_hits']:.4f}")
        if d.get("uniform_draw_null_mean") is not None:
            lines.append(f"    (uniform-draw null mean for reference: "
                         f"{d['uniform_draw_null_mean']:.2f})")
        lines.append(f"    rate test: null mean rate {d['null_mean_rate']:.3f}, "
                     f"P(rate >= obs) {d['p_rate']:.4f}")
        lines.append("")
    with open(os.path.join(RESULTS, "axis_rule_matched_null.txt"), "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
