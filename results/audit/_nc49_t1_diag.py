# -*- coding: utf-8 -*-
"""逐 CT 分解 brain ladder T1 结果 + 组规模效应诊断。"""
import numpy as np
import pandas as pd

df = pd.read_csv("C:/Users/KnightZ/Desktop/细胞受选择/results/nc49_brain_drift_ladder.csv")
out = []

t1 = df[df.tier == "T1_techrep"]
mets = ["k_n", "k_f", "omega", "raw_js", "cosine", "spearman", "marker_jaccard"]

out.append("== T1 per-CT: cal_omega median [IQR], FPR_omega, FPR_raw_js, n ==")
g = t1.groupby("cell_type")
tab = pd.DataFrame({
    "n": g.size(),
    "cal_omega_med": g["cal_omega"].median(),
    "cal_omega_q25": g["cal_omega"].quantile(.25),
    "cal_omega_q75": g["cal_omega"].quantile(.75),
    "FPR_omega": g["exceed_omega"].mean(),
    "FPR_raw_js": g["exceed_raw_js"].mean(),
    "FPR_kn": g["exceed_k_n"].mean(),
    "FPR_cosine": g["exceed_cosine"].mean(),
})
out.append(tab.to_string())

out.append("\n== T1: n_cells (min of pair) vs cal_omega / exceed ==")
t1 = t1.copy()
t1["n_min"] = t1[["n_cells_a", "n_cells_b"]].min(axis=1)
bins = [20, 30, 50, 100, 200, 500, 5000]
t1["n_bin"] = pd.cut(t1["n_min"], bins)
nb = t1.groupby("n_bin", observed=True).agg(
    n=("cal_omega", "size"),
    cal_omega_med=("cal_omega", "median"),
    FPR_omega=("exceed_omega", "mean"),
    FPR_raw_js=("exceed_raw_js", "mean"),
    FPR_kn=("exceed_k_n", "mean"),
    FPR_kf=("exceed_k_f", "mean"),
)
out.append(nb.to_string())

out.append("\n== T1: FPR ratio raw_js vs omega by CT ==")
tab2 = pd.DataFrame({
    "FPR_raw_js": g["exceed_raw_js"].mean(),
    "FPR_omega": g["exceed_omega"].mean(),
})
tab2["ratio"] = tab2["FPR_raw_js"] / tab2["FPR_omega"].replace(0, np.nan)
out.append(tab2.to_string())

out.append("\n== per-CT observed medians (T1) ==")
out.append(g[mets].median().to_string())

# n-match check: null n = observed n by construction; check odd cases
out.append("\n== sanity: any null_med_kn == 0 or nan? ==")
out.append(str(t1["null_med_k_n"].isna().sum()) + " NaN; " +
           str((t1["null_med_k_n"] <= 0).sum()) + " <=0; " +
           str(t1["cal_omega"].isna().sum()) + " cal_omega NaN")

open("C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_t1_perct.txt",
     "w", encoding="utf-8").write("\n".join(out))
