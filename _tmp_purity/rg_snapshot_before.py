# -*- coding: utf-8 -*-
"""Snapshot current v44 pair table state for the RG fix (before re-run)."""
import pandas as pd

ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
pairs = pd.read_csv(ROOT + "/results/tcga_linear_norm_v44_all_pairs.csv")

out = []
out.append("== BEFORE RG fix ==")
out.append(f"total pairs: {len(pairs)}")
for c in ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]:
    sub = pairs[pairs.cancer == c]
    tt = sub[sub.pair_type == "TT"]
    nn = sub[sub.pair_type == "NN"]
    tn = sub[sub.pair_type == "TN"]
    n_t = len(set(tt.sample_a) | set(tt.sample_b))
    n_n = len(set(nn.sample_a) | set(nn.sample_b))
    out.append(f"{c}: TT={len(tt)} pairs/{n_t} tumors, NN={len(nn)}/{n_n} normals, TN={len(tn)}")

rg = pairs[(pairs.sample_a == "TCGA-RG-A7D4-01") | (pairs.sample_b == "TCGA-RG-A7D4-01")]
out.append("")
out.append(f"RG sample pairs: {len(rg)}")
if len(rg):
    out.append(str(rg.groupby(["cancer", "pair_type"]).size()))

# check CC-tss samples existence in table
cc = pairs[pairs.sample_a.str.startswith("TCGA-CC-") | pairs.sample_b.str.startswith("TCGA-CC-")]
out.append("")
out.append(f"pairs involving TSS 'CC' samples: {len(cc)}")

# KIRC/LIHC current headline numbers (from existing results csv)
pan = pd.read_csv(ROOT + "/results/nc49_tcga_pancancer.csv")
out.append("")
out.append("== current nc49_tcga_pancancer.csv (KIRC/LIHC rows) ==")
cols = ["cancer", "n_tumor", "n_normal", "n_TT_pairs", "NN_TT_ratio",
        "NN_TT_ratio_CI95_lower", "NN_TT_ratio_CI95_upper",
        "kn_TT_NN_median_ratio", "kn_TT_NN_mean_ratio"]
out.append(pan.loc[pan.cancer.isin(["TCGA-KIRC", "TCGA-LIHC"]), cols].to_string(index=False))

open(ROOT + "/_tmp_purity/rg_before_snapshot.txt", "w").write("\n".join(out))
