# -*- coding: utf-8 -*-
import json
ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
old = json.load(open(ROOT + "/_tmp_purity/before_cc/tcga_clinical_severity_v44.json"))
new = json.load(open(ROOT + "/results/tcga_clinical_severity_v44.json"))
out = []
for tag, d in [("old", old), ("new", new)]:
    tests = d.get("tests", {})
    for k, v in tests.items():
        if "LIHC" in k:
            out.append(f"{tag} {k}: {v}")
open(ROOT + "/_tmp_purity/severity_tests.txt", "w").write("\n".join(out))
