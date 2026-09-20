# -*- coding: utf-8 -*-
import traceback
try:
    import pandas as pd
    ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
    pairs = pd.read_csv(ROOT + "/results/tcga_linear_norm_v44_all_pairs.csv")
    out = []
    cc_pairs = pairs[pairs.sample_a.str.startswith("TCGA-CC-") | pairs.sample_b.str.startswith("TCGA-CC-")]
    out.append(f"pairs involving TCGA-CC-* : {len(cc_pairs)}")
    out.append(str(cc_pairs.groupby(["cancer", "pair_type"]).size()))
    out.append("")
    cc_samples = set(cc_pairs.sample_a) | set(cc_pairs.sample_b)
    out.append(f"unique CC samples in pairs: {len(cc_samples)}")
    for s in sorted(cc_samples):
        t_pairs = cc_pairs[(cc_pairs.sample_a == s) | (cc_pairs.sample_b == s)]
        out.append(f"  {s}: cancers={sorted(t_pairs.cancer.unique())}, "
                   f"types={dict(t_pairs.pair_type.value_counts())}")
    res = "\n".join(out)
except Exception:
    res = traceback.format_exc()
open(r"C:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/cc_quantify.txt", "w", encoding="utf-8").write(res)
