# diag2: mtimes + KIRC deep-dive
from pathlib import Path
import datetime
import numpy as np
import pandas as pd
from scipy.stats import linregress

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
for f in ["results/nc49_tcga_purity.csv", "results/nc49_tcga_admix_scores.csv",
          "results/tcga_linear_norm_v44_all_pairs.csv", "results/nc49_tcga_luad_smoking.csv",
          "results/nc49_tcga_pancancer.csv", "notebooks/nc49_tcga_purity.py",
          "results/nc49_tcga_luad_mutation.csv"]:
    p = ROOT / f
    print(f, datetime.datetime.fromtimestamp(p.stat().st_mtime), p.stat().st_size)

pairs = pd.read_csv(ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv").rename(columns={"omega_floor": "omega"})
adm = pd.read_csv(ROOT / "results" / "nc49_tcga_admix_scores.csv")
adm_t = adm[adm.type == "Tumor"][["sample", "admix"]]
print("admix tumor counts by cancer:", adm[adm.type == "Tumor"].groupby("cancer").size().to_dict())
print("admix normal counts by cancer:", adm[adm.type == "Normal"].groupby("cancer").size().to_dict())

# KIRC: recompute r on merged subset, both raw admix and z over full KIRC tumor set
c = "TCGA-KIRC"
sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
long = pd.concat([
    sub[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
    sub[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"})])
pt = long.groupby("sample").agg(omega=("omega", "mean"), kf=("kf", "mean"), kn=("kn", "mean")).reset_index()
pt = pt.merge(adm_t, on="sample", how="inner")
print("KIRC merged n:", len(pt))
full = adm[adm.cancer == c]
z_full = (pt["admix"] - full["admix"].mean()) / full["admix"].std(ddof=1)
z_sub = (pt["admix"] - pt["admix"].mean()) / pt["admix"].std(ddof=1)
for m in ["kn", "omega", "kf"]:
    r_full = linregress(z_full, pt[m])
    r_sub = linregress(z_sub, pt[m])
    print(f"KIRC {m}: r(z over all admix tumors of cancer)={r_full.rvalue:+.4f} P={r_full.pvalue:.3e} | "
          f"r(z over matched subset)={r_sub.rvalue:+.4f} P={r_sub.pvalue:.3e}")
