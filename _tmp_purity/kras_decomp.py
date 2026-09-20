# -*- coding: utf-8 -*-
"""R2-P1-2: KRAS-WT omega decomposition at full precision (from pair table)."""
import json
import numpy as np
import pandas as pd

ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
pairs = pd.read_csv(ROOT + "/results/tcga_linear_norm_v44_all_pairs.csv")
pairs = pairs.rename(columns={"omega_floor": "omega"})
lu = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")]
long = pd.concat([
    lu[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
    lu[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
], ignore_index=True)
pt = long.groupby("sample").agg(omega=("omega", "mean"), kf=("kf", "mean"), kn=("kn", "mean"))

mut = json.load(open(ROOT + "/data/tcga/luad_egfr_kras_mutations.json"))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])

def grp(s):
    e, k = s in egfr, s in kras
    return "DOUBLE" if (e and k) else ("EGFR" if e else ("KRAS" if k else "WT"))

pt["group"] = [grp(s) for s in pt.index]
pt = pt[pt.group != "DOUBLE"]

m = pt.groupby("group")[["omega", "kf", "kn"]].mean()
out = ["group means (full precision):", m.to_string(), ""]
w, k = m.loc["WT"], m.loc["KRAS"]

d_log_w_obs = np.log(k.omega / w.omega)
d_log_kf = np.log(k.kf / w.kf)
d_log_kn = np.log(k.kn / w.kn)
d_log_w_comp = d_log_kf - d_log_kn

out.append(f"observed omega ratio KRAS/WT: {k.omega/w.omega:.4f} (log {d_log_w_obs:.4f})")
out.append(f"kf ratio: {k.kf/w.kf:.4f} (log {d_log_kf:+.4f})")
out.append(f"kn ratio: {k.kn/w.kn:.4f} (log {d_log_kn:+.4f}); kn drop {100*(1-k.kn/w.kn):.1f}%")
out.append(f"component-mean log-omega increment: {d_log_w_comp:.4f}")
out.append(f"kn share of increment: {100*(-d_log_kn)/d_log_w_comp:.1f}%")
out.append(f"kf share of increment: {100*d_log_kf/d_log_w_comp:.1f}%")
out.append("")
out.append("Dunn-Holm (from nc49_tcga_luad_mutation.csv): k_f WT vs KRAS P=0.0969; "
           "bootstrap mean diff k_f KRAS-WT +0.0105 CI95 [0.0024,0.0192]")
open(ROOT + "/_tmp_purity/kras_decomp.txt", "w").write("\n".join(out))
