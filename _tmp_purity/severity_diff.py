# -*- coding: utf-8 -*-
import pandas as pd
ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
old = pd.read_csv(ROOT + "/_tmp_purity/before_cc/tcga_clinical_severity_v44.csv")
new = pd.read_csv(ROOT + "/results/tcga_clinical_severity_v44.csv")
out = [f"severity rows old={len(old)} new={len(new)}", f"cols: {list(old.columns)}"]
try:
    m = old.merge(new, on=list(old.columns[:2]), suffixes=("_old", "_new"), how="outer", indicator=True)
    out.append(str(m["_merge"].value_counts()))
except Exception as e:
    out.append(f"merge failed: {e}; showing heads:")
    out.append(old.head(8).to_string())
    out.append(new.head(8).to_string())
open(ROOT + "/_tmp_purity/severity_diff.txt", "w").write("\n".join(out))
