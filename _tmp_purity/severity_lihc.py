# -*- coding: utf-8 -*-
import json
ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
old = json.load(open(ROOT + "/_tmp_purity/before_cc/tcga_clinical_severity_v44.json"))
new = json.load(open(ROOT + "/results/tcga_clinical_severity_v44.json"))
out = []
for tag, d in [("old", old), ("new", new)]:
    sev = d["severity"]["TCGA-LIHC"]
    out.append(f"== {tag} LIHC severity keys: {list(sev.keys())}")
    out.append(str({k: v for k, v in sev.items() if k != "groups"})[:800])
    for g, s in sev.get("groups", {}).items():
        out.append(f"  {g}: n={s['n']}, omega={s['omega_mean']:.2f}, kn={s['kn_mean']:.5f}")
open(ROOT + "/_tmp_purity/severity_lihc.txt", "w").write("\n".join(out))
