"""
v49.13 B1: region-matched (span-balanced) astrocyte vs Bergmann-glia control.
============================================================================
Reviewer: R5-N4. The size-balanced equal-n control equalizes nucleus counts
but not anatomical span: Bergmann glia pairs are all intra-cerebellar (7
regions, 21 pairs) while astrocyte pairs span 108 regions (5,778 pairs). The
residual 1.74-fold gradient therefore still mixes regional-coverage
confounding.

This script restricts astrocytes to their intra-cerebellar subset -- the same
7 regions, hence the identical 21 region pairs as Bergmann glia -- and
quantifies the span-matched gradient. Because the region pairs are identical
across the two classes, the comparison is fully paired: per region-pair
ratios, their median, and a bootstrap CI over the 21 matched region pairs
(B = 10,000, seed 42). k_f / k_n decomposition is reported alongside.

Also reports the alternative vascular-cells control (excluded-class endpoint
substitute used in the manuscript) for reference.

Input : results/reviewer_brain_pair_kf_kn.csv  (t=20 observed pairs, 31,764)
Output: results/nc49_brain_region_matched.csv
        results/nc49_brain_region_matched.txt
Seed  : 42.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
IN = ROOT / "results" / "reviewer_brain_pair_kf_kn.csv"
OUT = ROOT / "results" / "nc49_brain_region_matched.csv"
OUT_TXT = ROOT / "results" / "nc49_brain_region_matched.txt"

B = 10000
SEED = 42

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

df = pd.read_csv(IN)

def key(r):
    return tuple(sorted([r.region_a, r.region_b]))

df["rp"] = [key(r) for _, r in df.iterrows()]

ast = df[df.cell_type == "Astrocyte"].copy()
berg = df[df.cell_type == "Bergmann glia"].copy()
vasc = df[df.cell_type == "Vascular"].copy()

berg_rps = set(berg.rp)
berg_regions = sorted(set(berg.region_a) | set(berg.region_b))
log(f"Bergmann glia: {len(berg)} pairs over {len(berg_regions)} regions: "
    f"{berg_regions}")

ast_cb = ast[ast.rp.isin(berg_rps)].copy()
log(f"Astrocyte intra-cerebellar subset (same 7 regions): {len(ast_cb)} pairs "
    f"of {len(ast)} total (region-matched by construction)")
vasc_cb = vasc[vasc.rp.isin(berg_rps)].copy()
log(f"Vascular intra-cerebellar subset (reference endpoint): {len(vasc_cb)} "
    f"pairs of {len(vasc)} total")

# matched join on region pair
m = (ast_cb.set_index("rp")[["omega", "kf", "kn"]]
     .join(berg.set_index("rp")[["omega", "kf", "kn"]],
           lsuffix="_astro", rsuffix="_berg"))
log("")
log(f"Matched region pairs: {len(m)}")
m["omega_ratio"] = m.omega_astro / m.omega_berg
m["kf_ratio"] = m.kf_astro / m.kf_berg
m["kn_ratio"] = m.kn_astro / m.kn_berg

grad_full = ast.omega.mean() / berg.omega.mean()
ratio_means = m.omega_astro.mean() / m.omega_berg.mean()
ratio_paired_median = float(m.omega_ratio.median())
rng = np.random.default_rng(SEED)
boots = []
ratios_arr = m.omega_ratio.values
for _ in range(B):
    idx = rng.integers(0, len(ratios_arr), len(ratios_arr))
    boots.append(np.median(ratios_arr[idx]))
ci_lo, ci_hi = np.percentile(boots, [2.5, 97.5])

log("")
log("== Span-matched gradient (astrocyte intra-cerebellar vs Bergmann glia) ==")
log(f"  class-mean omega: astro_cb={m.omega_astro.mean():.2f}, "
    f"bergmann={m.omega_berg.mean():.2f}")
log(f"  gradient (ratio of class means): {ratio_means:.2f}  "
    f"[full-data gradient for reference: {grad_full:.2f}]")
log(f"  paired per-region-pair median ratio: {ratio_paired_median:.2f} "
    f"(bootstrap 95% CI [{ci_lo:.2f}, {ci_hi:.2f}], B={B}, seed {SEED})")
log(f"  k_f ratio of class means: {m.kf_astro.mean()/m.kf_berg.mean():.2f} "
    f"(median paired {m.kf_ratio.median():.2f})")
log(f"  k_n ratio of class means: {m.kn_astro.mean()/m.kn_berg.mean():.2f} "
    f"(median paired {m.kn_ratio.median():.2f})")

# vascular reference endpoint (same matched regions)
if len(vasc_cb):
    mv = (vasc_cb.set_index("rp")[["omega", "kf", "kn"]]
          .join(berg.set_index("rp")[["omega", "kf", "kn"]],
                lsuffix="_vasc", rsuffix="_berg"))
    log("")
    log("== Reference: vascular intra-cerebellar vs Bergmann glia ==")
    log(f"  matched pairs: {len(mv)}; gradient (ratio of class means): "
        f"{mv.omega_vasc.mean()/mv.omega_berg.mean():.2f}")

rows = []
for rp, r in m.iterrows():
    rows.append({"region_a": rp[0], "region_b": rp[1],
                 "omega_astro_cb": round(r.omega_astro, 3),
                 "omega_bergmann": round(r.omega_berg, 3),
                 "omega_ratio": round(r.omega_ratio, 3),
                 "kf_ratio": round(r.kf_ratio, 4),
                 "kn_ratio": round(r.kn_ratio, 4)})
out = pd.DataFrame(rows)
out.to_csv(OUT, index=False)

summary = pd.DataFrame([{
    "statistic": "gradient_ratio_of_class_means", "value": round(ratio_means, 3),
    "ci95": "", "note": "astro intra-cerebellar vs Bergmann glia, 21 matched region pairs"},
    {"statistic": "gradient_paired_median_ratio", "value": round(ratio_paired_median, 3),
     "ci95": f"[{ci_lo:.3f},{ci_hi:.3f}]", "note": f"bootstrap B={B} over matched region pairs"},
    {"statistic": "gradient_full_data_reference", "value": round(grad_full, 3),
     "ci95": "", "note": "unmatched full-data gradient (published 6.10)"},
    {"statistic": "kf_ratio_class_means", "value": round(m.kf_astro.mean()/m.kf_berg.mean(), 3),
     "ci95": "", "note": "span-matched k_f component"},
    {"statistic": "kn_ratio_class_means", "value": round(m.kn_astro.mean()/m.kn_berg.mean(), 3),
     "ci95": "", "note": "span-matched k_n component"},
])
summary.to_csv(OUT.with_name(OUT.stem + "_summary.csv"), index=False)
OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
log("")
log("saved: " + str(OUT) + ", " + str(OUT.with_name(OUT.stem + "_summary.csv"))
    + ", " + str(OUT_TXT))
print("DONE")
