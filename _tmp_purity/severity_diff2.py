# -*- coding: utf-8 -*-
import pandas as pd
ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
old = pd.read_csv(ROOT + "/_tmp_purity/before_cc/tcga_clinical_severity_v44.csv")
new = pd.read_csv(ROOT + "/results/tcga_clinical_severity_v44.csv")
key = ["cancer", "stratification", "group"]
m = old.merge(new, on=key, suffixes=("_old", "_new"))
out = []
for _, r in m.iterrows():
    dn = r.n_new - r.n_old
    dw = r.omega_mean_new - r.omega_mean_old
    if dn != 0 or abs(dw) > 1e-9:
        out.append(f"{r.cancer}/{r.stratification}/{r.group}: n {r.n_old}->{r.n_new}, "
                   f"omega {r.omega_mean_old:.2f}->{r.omega_mean_new:.2f}, "
                   f"kn {r.kn_mean_old:.5f}->{r.kn_mean_new:.5f}")
if not out:
    out.append("no differences")
open(ROOT + "/_tmp_purity/severity_diff2.txt", "w").write("\n".join(out))
