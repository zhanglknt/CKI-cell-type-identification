# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
df = pd.read_csv("C:/Users/KnightZ/Desktop/细胞受选择/results/nc49_brain_drift_ladder.csv")
t1 = df[df.tier == "T1_techrep"]
out = []
out.append("Choroid plexus T1 pairs:")
sub = t1[t1.cell_type == "Choroid plexus"]
cols = ["roi_a", "roi_b", "donor_a", "n_cells_a", "n_cells_b", "omega",
        "cal_omega", "exceed_omega", "k_f", "cal_k_f"]
out.append(sub[cols].to_string(index=False))
out.append("")
out.append("Bergmann glia T1: n_min distribution")
sub2 = t1[t1.cell_type == "Bergmann glia"]
sub2 = sub2.assign(n_min=sub2[["n_cells_a", "n_cells_b"]].min(axis=1))
out.append(sub2["n_min"].describe().to_string())
out.append("cal_omega by n_min bin:")
out.append(sub2.groupby(pd.cut(sub2["n_min"], [20, 50, 100, 500]))["cal_omega"].median().to_string())
out.append("")
out.append("Oligodendrocyte T1: cal_omega by n_min bin")
sub3 = t1[t1.cell_type == "Oligodendrocyte"].assign(
    n_min=lambda d: d[["n_cells_a", "n_cells_b"]].min(axis=1))
out.append(sub3.groupby(pd.cut(sub3["n_min"], [20, 50, 100, 200, 500, 8000]),
                        observed=True)[["cal_omega", "exceed_omega"]].agg(
                            {"cal_omega": "median", "exceed_omega": "mean"}).to_string())
out.append("")
out.append("T1 all: rho between log n_min and cal metrics")
for m in ["cal_omega", "cal_raw_js", "cal_k_n", "cal_k_f"]:
    out.append(f"  {m}: Spearman rho={t1.assign(n_min=t1[['n_cells_a','n_cells_b']].min(axis=1)).pipe(lambda d: d[['n_min', m]].corr(method='spearman').iloc[0,1]):.3f}")
open("C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_outlier_diag.txt",
     "w", encoding="utf-8").write("\n".join(out))
