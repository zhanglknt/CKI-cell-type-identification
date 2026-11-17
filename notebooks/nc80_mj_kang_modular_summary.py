#!/usr/bin/env python3
"""nc80 M-J (iii): summarise the 10x modular operating characteristic.

Reads results/nc80_mj_kang_modular_raw.csv and produces the publishable
summary table (marginal ROC with a global threshold, plus the design-matched
paired detection rate whose null value is exactly 0.5 because every injected
replicate is compared with the split-half null of the same cells).

Outputs:
  results/nc80_mj_kang_modular_summary.csv
  results/nc80_mj_kang_modular_summary.txt
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
MET = ["omega", "k_f", "k_n", "k_total", "cosine", "mahal_pc", "mahal_diag"]
DELTAS = [0.25, 0.5, 1.0]

raw = pd.read_csv(OUT / "nc80_mj_kang_modular_raw.csv")
rows = []
for n in sorted(raw["n"].unique()):
    s = raw[raw["n"] == n]
    nul = s[s["series"] == "split_half"]
    eff = s[s["series"] == "effect"]
    for m in MET:
        pooled_auc = roc_auc_score([1] * len(eff) + [0] * len(nul),
                                   np.r_[eff[m].to_numpy(float),
                                         nul[m].to_numpy(float)])
        # design-matched paired detection rate: injected vs the null of the
        # same cell set (null value 0.5 by construction)
        base = eff["rep"].map(nul.set_index("rep")[m])
        win = (eff[m].to_numpy(float) > base.to_numpy(float))
        rec = {"n": n, "metric": m, "auc_pooled_delta_ge_0.25": round(pooled_auc, 3)}
        for d in DELTAS:
            sel = (eff["delta"] == d).to_numpy()
            rec[f"win_d{d}"] = round(float(win[sel].mean()), 3)
            e = eff[eff["delta"] == d][m].to_numpy(float)
            rec[f"auc_d{d}"] = round(float(roc_auc_score(
                [1] * len(e) + [0] * len(nul), np.r_[e, nul[m].to_numpy(float)])), 3)
        # marginal TPR at the global q95 threshold, for continuity with the
        # TPR table
        tpr = pd.read_csv(OUT / "nc80_mj_kang_modular_tpr.csv")
        t = tpr[(tpr["n"] == n) & (tpr["metric"] == m)]
        rec["fpr_heldout_null"] = float(t["fpr_heldout_null"].iloc[0])
        rec["tpr_d1.0_global"] = float(t["tpr_d1.0"].iloc[0])
        rows.append(rec)

df = pd.DataFrame(rows)
df.to_csv(OUT / "nc80_mj_kang_modular_summary.csv", index=False)

lines = ["nc80 M-J(iii): 10x modular off-anchor operating characteristic",
         "=" * 66,
         "Kang GSE96583 ctrl cells, donor-paired split-half, 200-gene module",
         "from the top-5,000 non-HK genes, multiplicative 2**delta on B,",
         "n = 50/100/200 cells per group, 200 null slots (100 calibration +",
         "100 held out), 300 injected replicates per delta.",
         "",
         "auc_pooled = AUC of all injected replicates (delta >= 0.25) against",
         "the split-half nulls; win = fraction of injected replicates exceeding",
         "the null of the same cell set (null value 0.500); tpr/tpr_global =",
         "detection at the global q95 threshold of the calibration nulls.",
         "",
         df.to_string(index=False)]
(OUT / "nc80_mj_kang_modular_summary.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
