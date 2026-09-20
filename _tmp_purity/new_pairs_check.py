# -*- coding: utf-8 -*-
import pandas as pd
ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
pairs = pd.read_csv(ROOT + "/results/tcga_linear_norm_v44_all_pairs.csv")
out = [f"total pairs: {len(pairs)}"]
for c in ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]:
    sub = pairs[pairs.cancer == c]
    tt = sub[sub.pair_type == "TT"]
    nn = sub[sub.pair_type == "NN"]
    tn = sub[sub.pair_type == "TN"]
    n_t = len(set(tt.sample_a) | set(tt.sample_b))
    n_n = len(set(nn.sample_a) | set(nn.sample_b))
    out.append(f"{c}: TT={len(tt)}/{n_t}T NN={len(nn)}/{n_n}N TN={len(tn)}")
rg = pairs[(pairs.sample_a == "TCGA-RG-A7D4-01") | (pairs.sample_b == "TCGA-RG-A7D4-01")]
out.append(f"RG: cancers={sorted(rg.cancer.unique())}, pairs={dict(rg.pair_type.value_counts())}")
cc = pairs[pairs.sample_a.str.startswith("TCGA-CC-") | pairs.sample_b.str.startswith("TCGA-CC-")]
out.append(f"CC-*: cancers={sorted(cc.cancer.unique())}, n_pairs={len(cc)}")
open(ROOT + "/_tmp_purity/new_pairs_check.txt", "w").write("\n".join(out))
