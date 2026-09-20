# -*- coding: utf-8 -*-
"""分层 FPR（按 n_min 分层，每层用该层 pooled null 分布定阈值）"""
import numpy as np
import pandas as pd

df = pd.read_csv("C:/Users/KnightZ/Desktop/细胞受选择/results/nc49_brain_drift_ladder.csv")
t1 = df[df.tier == "T1_techrep"].copy()
t1["n_min"] = t1[["n_cells_a", "n_cells_b"]].min(axis=1)
mets = ["k_n", "k_f", "omega", "raw_js", "cosine", "spearman", "marker_jaccard"]

# pooled global threshold per metric (null p95 across all T1 pairs)
out = ["== T1 FPR vs GLOBAL threshold (null p95 pooled over all 2161 pairs) =="]
for met in mets:
    thr = t1[f"null_p95_{met}"].quantile(0.95)  # conservative: upper envelope
    # better: each pair's own null p95 already stored; global test:
    # observed > median(null_p95)? No — report two versions:
    pass
# version A: per-pair own null p95 (current headline)
out.append("version A (own null p95): " + str({m: round(t1[f'exceed_{m}'].mean(),3) for m in mets}))
# version B: global pooled threshold = median of per-pair null_p95
out.append("version B (pooled null_p95 median as global threshold):")
for met in mets:
    thr = t1[f"null_p95_{met}"].median()
    out.append(f"  {met:<16} thr={thr:.4g} FPR={(t1[met] > thr).mean():.3f}")
# version C: stratified by n-bin: threshold = median null_p95 within bin
out.append("version C (n-bin-stratified threshold):")
t1["n_bin"] = pd.cut(t1["n_min"], [20, 50, 100, 200, 500, 5000])
for met in mets:
    fprs = []
    for b, h in t1.groupby("n_bin", observed=True):
        thr = h[f"null_p95_{met}"].median()
        fprs.append((h[met] > thr).mean())
    out.append(f"  {met:<16} " + " ".join(f"{x:.3f}" for x in fprs))

# per-CT calibration medians for the ladder narrative
out.append("\n== T2/T3 cal_omega per CT (median) ==")
for tier in ["T2_cross_donor", "T3_cross_roi"]:
    sub = df[df.tier == tier]
    out.append(f"--- {tier} ---")
    out.append(sub.groupby("cell_type")["cal_omega"].median().round(3).to_string())

open("C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_fpr_versions.txt",
     "w", encoding="utf-8").write("\n".join(out))
