# diag7: verify alignment inside the merged KIRC frame
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
pairs = pd.read_csv(ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv").rename(columns={"omega_floor": "omega"})
df_ss = pd.read_csv(ROOT / "results" / "nc49_tcga_admix_scores.csv")
df_tumor = df_ss[df_ss.type == "Tumor"].copy()
df_tumor["admix_z"] = df_tumor.groupby("cancer")["admix"].transform(
    lambda x: (x - x.mean()) / x.std(ddof=1))

c = "TCGA-KIRC"
sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
long = pd.concat([
    sub[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
    sub[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"})])
pt = long.groupby("sample").agg(kn=("kn", "mean")).reset_index()
pt = pt.merge(df_tumor[["sample", "admix", "admix_z"]], on="sample", how="inner")

M1 = df_tumor.loc[df_tumor.cancer == c, "admix"].mean()
S1 = df_tumor.loc[df_tumor.cancer == c, "admix"].std(ddof=1)
z_manual = (pt["admix"] - M1) / S1
err = (pt["admix_z"] - z_manual).abs()
print("merged n:", len(pt), "max err vs manual z:", err.max())
bad = pt[err > 1e-9].copy()
print("bad:", len(bad))
if len(bad):
    bad["z_manual"] = z_manual[err > 1e-9]
    bad["err"] = err[err > 1e-9]
    print(bad.sort_values("err", ascending=False).head(10).to_string())
    # are these samples duplicated in pairs table with different case/whitespace?
    for s in bad["sample"].head(5):
        rows = df_tumor[df_tumor["sample"] == s]
        print(s, "-> df_tumor rows:", len(rows), rows[["cancer", "admix", "admix_z"]].to_dict("records"))
