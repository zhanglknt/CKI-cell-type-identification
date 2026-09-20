# diag8: fully corrected cohorts (RG-A7D4 -> LIHC per GDC) impact on (a) and NN/TT
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import linregress

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
pairs = pd.read_csv(ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv").rename(columns={"omega_floor": "omega"})
df_ss = pd.read_csv(ROOT / "results" / "nc49_tcga_admix_scores.csv")
adm_t = df_ss[df_ss.type == "Tumor"][["sample", "admix"]]
RG = "TCGA-RG-A7D4-01"

def per_tumor(c):
    sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    long = pd.concat([
        sub[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
        sub[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"})])
    pt = long.groupby("sample").agg(omega=("omega", "mean"), kf=("kf", "mean"),
                                    kn=("kn", "mean")).reset_index()
    return pt.merge(adm_t, on="sample", how="inner")

kirc = per_tumor("TCGA-KIRC")
lihc = per_tumor("TCGA-LIHC")
print(f"pair-table KIRC n={len(kirc)} (RG in it: {(kirc['sample']==RG).sum()}); "
      f"LIHC n={len(lihc)} (RG in it: {(lihc['sample']==RG).sum()})")
print(f"RG pairs in pair table: {((pairs['sample_a']==RG)|(pairs['sample_b']==RG)).sum()}")
print(f"RG pair_type counts: {pairs[(pairs['sample_a']==RG)|(pairs['sample_b']==RG)].groupby(['cancer','pair_type']).size().to_dict()}")

# corrected: move RG from KIRC to LIHC
kirc_c = kirc[kirc["sample"] != RG]
lihc_c = pd.concat([lihc, kirc[kirc["sample"] == RG]], ignore_index=True)
for name, df in [("KIRC as-analyzed (746)", kirc), ("KIRC corrected (745)", kirc_c),
                 ("LIHC as-analyzed (365)", lihc), ("LIHC corrected (366)", lihc_c)]:
    z = (df["admix"] - df["admix"].mean()) / df["admix"].std(ddof=1)
    r = linregress(z, df["kn"])
    print(f"{name}: kn r={r.rvalue:+.4f} P={r.pvalue:.3e}")

# NN/TT impact for KIRC and LIHC if RG moved
for c in ["TCGA-KIRC", "TCGA-LIHC"]:
    tt = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    nn = pairs[(pairs.cancer == c) & (pairs.pair_type == "NN")]
    ratio = nn.omega.mean() / tt.omega.mean()
    tt_c = tt[(tt["sample_a"] != RG) & (tt["sample_b"] != RG)]
    ratio_c = nn.omega.mean() / tt_c.omega.mean()
    print(f"{c}: NN/TT as-analyzed={ratio:.4f} (TT {len(tt)} pairs); "
          f"excluding RG pairs={ratio_c:.4f} (TT {len(tt_c)} pairs)")
