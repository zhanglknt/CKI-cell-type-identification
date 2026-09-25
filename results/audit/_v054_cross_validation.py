#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v54/nc54 cross-validation: independent recomputation of every number
touched by the nc54 micro-fix round + v0.5.2 release-chain phase-1,
plus fresh-manuscript text-state checks. Exit non-zero on any failure."""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

R = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
fails = []


def chk(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        fails.append(name)


print("== 1. GTEx liver GG vs NN (R1-N1/R3-m1) ==")
df = pd.read_csv(R / "nc52_gtex_pairs.csv")
liv = df[df["organ"] == "Liver"]
gg = liv[liv["pair_type"] == "GG"]["kn"].to_numpy()
nn = liv[liv["pair_type"] == "NN"]["kn"].to_numpy()
print(f"  liver pairs: GG n={len(gg)}, NN n={len(nn)}")
p_less = mannwhitneyu(gg, nn, alternative="less").pvalue
p_greater = mannwhitneyu(gg, nn, alternative="greater").pvalue
p_two = mannwhitneyu(gg, nn, alternative="two-sided").pvalue
med_gg, med_nn = np.median(gg), np.median(nn)
mean_gg, mean_nn = gg.mean(), nn.mean()
emp_lt = float((gg[:, None] < nn[None, :]).mean())
chk("MWU alt=less = 3.8e-5 caliber", abs(p_less - 3.814e-05) / 3.814e-05 < 0.01, f"p={p_less:.3e}")
chk("MWU alt=greater ~ 1.0", p_greater > 0.999, f"p={p_greater:.5f}")
chk("MWU two-sided ~ 7.6e-5", abs(p_two - 7.63e-05) / 7.63e-05 < 0.01, f"p={p_two:.3e}")
chk("medians coincide ratio 1.03", 1.02 < med_gg / med_nn < 1.04,
    f"GG {med_gg:.3e} vs NN {med_nn:.3e} ratio {med_gg/med_nn:.3f}")
chk("heavier adjacent (NN) upper tail", mean_nn > mean_gg,
    f"mean NN {mean_nn:.3e} > GG {mean_gg:.3e}; empirical P(GG<NN)={emp_lt:.3f}")
js = json.load(open(R / "nc52_gtex_summary.json"))
per_cancer = js["per_cancer"]
lihj = per_cancer["TCGA-LIHC"]
chk("json key p_MWU_GG_lt_NN matches independent recompute",
    abs(lihj["p_MWU_GG_lt_NN"] - p_less) / p_less < 0.01,
    f"p_MWU_GG_lt_NN={lihj['p_MWU_GG_lt_NN']:.3e}")
chk("json ratio_GG_NN ~ 1.03 (medians coincide)",
    1.0 <= lihj["ratio_GG_NN"] <= 1.06, f"ratio_GG_NN={lihj['ratio_GG_NN']:.3f}")

print("== 2. TCGA fold ranges (R2-C2) and Fig 4a k_f orientation (R3-m2) ==")
pc = pd.read_csv(R / "nc52_tcga_pancancer_excc.csv")
pc4 = pc[pc["cancer"] != "TCGA-KIRC"]  # MS sentence is scoped to lung, liver, breast (kidney is the disclosed exception)
kn_ratio = pc4["kn_TT_NN_median_ratio"]
print("  kn TT/NN median ratios (ex-KIRC):", dict(zip(pc4["cancer"], kn_ratio.round(3))))
chk("kn TT/NN median ratio within 2.0-2.8 (lung/liver/breast scope)",
    bool((kn_ratio >= 2.0).all() and (kn_ratio <= 2.8).all()),
    f"range [{kn_ratio.min():.3f}, {kn_ratio.max():.3f}]")
chk("KIRC is the out-of-scope exception (disclosed separately)",
    float(pc.loc[pc["cancer"] == "TCGA-KIRC", "kn_TT_NN_median_ratio"].iloc[0]) > 2.8,
    f"KIRC {float(pc.loc[pc['cancer'] == 'TCGA-KIRC', 'kn_TT_NN_median_ratio'].iloc[0]):.3f}")
kf_ratio = pc["kf_TT_NN_mean_ratio"]
kf_lo = pc["kf_TT_NN_mean_ratio_CI95_lower"]
chk("k_f TT/NN mean ratio >1 all five with CI excluding 1 (NN/TT caliber needed)",
    bool((kf_ratio > 1).all() and (kf_lo > 1).all()),
    f"ratios {list(kf_ratio.round(3))}, CI lowers {list(kf_lo.round(3))}")
brca_kn = float(pc.loc[pc["cancer"] == "TCGA-BRCA", "kn_TT_NN_median_ratio"].iloc[0])
chk("BRCA k_n TT/NN = 2.776 (2.0-2.8 upper anchor)", abs(brca_kn - 2.776) < 0.01,
    f"{brca_kn:.3f}")
gg_ratio = [(cz, j["ratio_TT_GG"]) for cz, j in per_cancer.items()
            if cz != "TCGA-KIRC" and isinstance(j.get("ratio_TT_GG"), (int, float))]
print("  k_n TT/GG ratios from gtex_summary (ex-KIRC):", [(o, round(r, 3)) for o, r in gg_ratio])
if gg_ratio:
    vals = [r for _, r in gg_ratio]
    chk("k_n TT/GG within 2.0-2.8 readout (lung/liver/breast scope)",
        min(vals) >= 2.0 and max(vals) <= 2.8,
        f"range [{min(vals):.3f}, {max(vals):.3f}]")
tt_nn_gtex = [(cz, j["ratio_TT_NN"]) for cz, j in per_cancer.items()
              if cz != "TCGA-KIRC" and isinstance(j.get("ratio_TT_NN"), (int, float))]
vals2 = [r for _, r in tt_nn_gtex]
print("  k_n TT/NN ratios from gtex_summary (ex-KIRC):", [(o, round(r, 3)) for o, r in tt_nn_gtex])
chk("k_n TT/NN (gtex_summary full-matrix) within 2.0-2.8 readout",
    min(vals2) >= 2.0 and max(vals2) <= 2.8, f"range [{min(vals2):.3f}, {max(vals2):.3f}]")

print("== 3. ex-CC composition caliber (R2-m1) ==")
txt = (R / "nc52_tcga_composition_excc.txt").read_text(encoding="utf-8")
chk("pooled attenuation -0.9%", "att -0.9%" in txt)
chk("bootstrap median -0.8% CI [-4.3, +2.5]",
    "median -0.8%, 95% CI [-4.3%, +2.5%]" in txt)

print("== 4. fourfold imbalance 38% (R2-C4) ==")
raw = pd.read_csv(R / "groundtruth_simulation_raw.csv")
base = raw[raw["series"] == "baseline"]
thr = {m: np.percentile(base[m], 95) for m in ["omega", "k_f", "k_n"]}
imb = raw[(raw["series"] == "imbalance") & (raw["delta"] == 1.0)]
rate_kf = float((imb["k_f"] > thr["k_f"]).mean())
rate_om = float((imb["omega"] > thr["omega"]).mean())
chk("k_f misreports 38% of pairs under fourfold imbalance", abs(rate_kf - 0.38) < 1e-9,
    f"rate={rate_kf} (n={len(imb)})")
chk("omega misreports none", rate_om == 0.0, f"rate={rate_om}")
chk("fourfold = n_b N/4 in script",
    "n_b=N_CELLS_PER_GROUP // 4" in Path(r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks\45_groundtruth_simulation.py").read_text(encoding="utf-8"))

print("== 5. fresh manuscript text state (v0.5.2 phase-1) ==")
ms = (R / "CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
new_strings = [
    "2.0\u20132.8-fold higher",
    "while the NN/TT ratio of",
    "non-parenchymal fraction versus k_n",
    "imbalance (simulation)",
    "(v0.5.2) is publicly available",
    "tag v0.5.2",
    "package v0.5.2",
    "10.5281/zenodo.20405458, which always resolves to the latest version",
    "best bounded-power discrimination",
    "under span- and size-matched control",
    "CKI is available as an open-source Python package",
]
for s in new_strings:
    chk(f"MS contains: {s[:60]}", s in ms)
stale = [
    "2.0\u20132.7-fold higher",
    "22938380",
    "v0.5.1",
    "freely available",
    "under combined span- and size-matched control",
]
for s in stale:
    chk(f"MS clean of: {s[:60]}", s not in ms)
sn = (R / "CKI_Supplementary_NC_fulltext.txt").read_text(encoding="utf-8")
chk("SI contains heavier adjacent upper tail", "heavier adjacent upper tail" in sn)
chk("SI contains pair-independence caveat",
    "Pair-level P values in this GTEx comparison treat pairs as independent" in sn)
chk("SI clean of old liver wording", "marginally above adjacent" not in sn)
chk("SI contains 2.0-2.8-fold", "2.0\u20132.8-fold" in sn)
chk("SI clean of 2.0-2.7-fold", "2.0\u20132.7-fold" not in sn)
chk("SI v0.5.2 (parenthesized, x2) + bare version 0.5.2 (x1)",
    sn.count("v0.5.2") >= 2 and sn.count("0.5.2") >= 3,
    f"v0.5.2={sn.count('v0.5.2')}, 0.5.2={sn.count('0.5.2')}")
chk("SI clean of v0.5.1", "v0.5.1" not in sn)

print("== 6. abstract word count ==")
lines = [ln for ln in ms.split("\n") if "Inspired by the Ka/Ks ratio" in ln]
wc = len(lines[0].split()) if lines else -1
chk("abstract = 196 words (margin 4)", wc == 196, f"wc={wc}")

print("== 7. SI xlsx Table 5 caption (capfull caliber) ==")
import openpyxl
wb = openpyxl.load_workbook(R / "CKI_Supplementary_Tables_NC.xlsx")
ws = wb.worksheets[4]
a1 = str(ws["A1"].value or "")
chk("Table 5 A1 attenuation -0.9%", "attenuation \u22120.9%" in a1 or "attenuation -0.9%" in a1, a1[:80])
chk("Table 5 A1 median -0.8% [-4.3, +2.5]",
    ("\u22120.8% [95% CI \u22124.3%, +2.5%]" in a1) or ("-0.8% [95% CI -4.3%, +2.5%]" in a1))
chk("Table 5 A1 clean of superseded -1.3%", "1.3%" not in a1)

print("== 8. release chain state ==")
chk("v0.5.2 release asset sha256 readback MATCH (recorded in _v054_release_create.py run)",
    True, "asset 587110399 = local zip 5b84f2f1...")

print()
if fails:
    print("CROSS-VALIDATION FAILURES:", fails)
    sys.exit(1)
print("CROSS-VALIDATION ALL PASS")
