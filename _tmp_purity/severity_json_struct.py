# -*- coding: utf-8 -*-
import json
ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
d = json.load(open(ROOT + "/results/tcga_clinical_severity_v44.json"))
out = [f"top keys: {list(d.keys())}"]
for k in d.keys():
    v = d[k]
    out.append(f"{k}: type={type(v).__name__}, preview={str(v)[:400]}")
open(ROOT + "/_tmp_purity/severity_json_struct.txt", "w").write("\n".join(out))
