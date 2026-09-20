# diag3: replicate the ORIGINAL script's section (a) code path verbatim
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import linregress

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
OUT_SCORES = ROOT / "results" / "nc49_tcga_admix_scores.csv"
CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
df_ss = pd.read_csv(OUT_SCORES)

# verbatim from nc49_tcga_purity.py
df_tumor = df_ss[df_ss.type == "Tumor"].copy()
df_tumor["admix_z"] = df_tumor.groupby("cancer")["admix"].transform(
    lambda x: (x - x.mean()) / x.std(ddof=1))

long_rows = []
for c in CANCERS:
    sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    if not len(sub):
        continue
    long_rows.append(pd.concat([
        sub[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
        sub[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
    ], ignore_index=True).assign(cancer=c))
long = pd.concat(long_rows, ignore_index=True)
per_tumor = long.groupby(["cancer", "sample"]).agg(
    n_pairs=("omega", "size"), omega=("omega", "mean"),
    kf=("kf", "mean"), kn=("kn", "mean")).reset_index()
per_tumor = per_tumor.merge(df_tumor[["sample", "admix", "admix_z"]], on="sample", how="inner")

for c in CANCERS:
    sub = per_tumor[per_tumor.cancer == c]
    for metric in ["kn", "omega", "kf"]:
        res = linregress(sub["admix_z"], sub[metric])
        print(f"{c} {metric}: r={res.rvalue:+.4f}, P={res.pvalue:.3g}, "
              f"r2={100*res.rvalue**2:.1f}% slope={res.slope:.6f} (n={len(sub)})")
