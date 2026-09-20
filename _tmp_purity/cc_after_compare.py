# -*- coding: utf-8 -*-
"""Before/after comparison for the CC+RG fix (run AFTER all re-runs)."""
import pandas as pd

ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
BEF = ROOT + "/_tmp_purity/before_cc"
out = []

pairs_new = pd.read_csv(ROOT + "/results/tcga_linear_norm_v44_all_pairs.csv")
pairs_old = pd.read_csv(BEF + "/tcga_linear_norm_v44_all_pairs.csv")

out.append("== pair table before/after ==")
out.append(f"total pairs: {len(pairs_old)} -> {len(pairs_new)}")
for c in ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]:
    row = [c]
    for df, tag in [(pairs_old, "old"), (pairs_new, "new")]:
        sub = df[df.cancer == c]
        tt = sub[sub.pair_type == "TT"]
        nn = sub[sub.pair_type == "NN"]
        tn = sub[sub.pair_type == "TN"]
        n_t = len(set(tt.sample_a) | set(tt.sample_b))
        n_n = len(set(nn.sample_a) | set(nn.sample_b))
        row.append(f"{tag}: TT={len(tt)}/{n_t}T NN={len(nn)}/{n_n}N TN={len(tn)}")
    out.append("  ".join(row))

# RG/CC sample placement after fix
for sid, pref in [("TCGA-RG-A7D4-01", None), (None, "TCGA-CC-")]:
    if sid:
        sub = pairs_new[(pairs_new.sample_a == sid) | (pairs_new.sample_b == sid)]
        out.append(f"{sid}: cancers={sorted(sub.cancer.unique())}, "
                   f"pairs={dict(sub.pair_type.value_counts())}")
    else:
        sub = pairs_new[pairs_new.sample_a.str.startswith(pref) | pairs_new.sample_b.str.startswith(pref)]
        out.append(f"{pref}*: cancers={sorted(sub.cancer.unique())}, n_pairs={len(sub)}")

pan_old = pd.read_csv(BEF + "/nc49_tcga_pancancer.csv")
pan_new = pd.read_csv(ROOT + "/results/nc49_tcga_pancancer.csv")
out.append("")
out.append("== pancancer before/after ==")
cols = ["cancer", "n_tumor", "n_normal", "NN_TT_ratio", "NN_TT_ratio_CI95_lower",
        "NN_TT_ratio_CI95_upper", "kn_TT_NN_median_ratio", "kn_TT_NN_mean_ratio",
        "kn_TT_NN_mean_ratio_CI95_lower", "kn_TT_NN_mean_ratio_CI95_upper"]
m = pan_old[cols].merge(pan_new[cols], on="cancer", suffixes=("_old", "_new"))
out.append(m.to_string(index=False))

def ci_excl_one(df, tag):
    excl = (df.NN_TT_ratio_CI95_lower > 1).sum()
    out.append(f"{tag}: CI excluding 1 in {excl}/5")
ci_excl_one(pan_old, "old")
ci_excl_one(pan_new, "new")

open(ROOT + "/_tmp_purity/cc_after_compare.txt", "w").write("\n".join(out))
