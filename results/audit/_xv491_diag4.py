# diag4: element-wise compare of KIRC subset between two construction paths
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import linregress

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
pairs = pd.read_csv(ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv").rename(columns={"omega_floor": "omega"})
df_ss = pd.read_csv(ROOT / "results" / "nc49_tcga_admix_scores.csv")
CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

# path 1 (verbatim original)
df_tumor = df_ss[df_ss.type == "Tumor"].copy()
df_tumor["admix_z"] = df_tumor.groupby("cancer")["admix"].transform(
    lambda x: (x - x.mean()) / x.std(ddof=1))
long_rows = []
for c in CANCERS:
    sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    long_rows.append(pd.concat([
        sub[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
        sub[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
    ], ignore_index=True).assign(cancer=c))
long = pd.concat(long_rows, ignore_index=True)
pt1 = long.groupby(["cancer", "sample"]).agg(omega=("omega", "mean"), kf=("kf", "mean"),
                                             kn=("kn", "mean")).reset_index()
pt1 = pt1.merge(df_tumor[["sample", "admix", "admix_z"]], on="sample", how="inner")

# path 2 (my recalc): same but merge on admix only, z on matched subset
adm_t = df_ss[df_ss.type == "Tumor"][["sample", "admix"]]
pt2 = long.groupby(["cancer", "sample"]).agg(omega=("omega", "mean"), kf=("kf", "mean"),
                                             kn=("kn", "mean")).reset_index()
pt2 = pt2.merge(adm_t, on="sample", how="inner")
pt2["admix_z"] = pt2.groupby("cancer")["admix"].transform(lambda x: (x - x.mean()) / x.std(ddof=1))

for c in CANCERS:
    s1 = pt1[pt1.cancer == c].sort_values("sample").reset_index(drop=True)
    s2 = pt2[pt2.cancer == c].sort_values("sample").reset_index(drop=True)
    same_samples = s1["sample"].tolist() == s2["sample"].tolist()
    d_kn = np.abs(s1["kn"].values - s2["kn"].values).max()
    d_admix = np.abs(s1["admix"].values - s2["admix"].values).max()
    r1 = linregress(s1["admix_z"], s1["kn"]).rvalue
    r2 = linregress(s2["admix_z"], s2["kn"]).rvalue
    print(f"{c}: n1={len(s1)} n2={len(s2)} same_samples={same_samples} "
          f"max|dKn|={d_kn:.3e} max|dAdmix|={d_admix:.3e} r1={r1:+.6f} r2={r2:+.6f}")
    if not same_samples:
        set1, set2 = set(s1["sample"]), set(s2["sample"])
        print("  only in 1:", sorted(set1 - set2)[:5], " only in 2:", sorted(set2 - set1)[:5])
