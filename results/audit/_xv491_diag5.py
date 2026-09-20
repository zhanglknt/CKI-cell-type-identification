# diag5: numeric pathology hunt on KIRC z-scores
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import linregress

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
pt = long.groupby("sample").agg(omega=("omega", "mean"), kf=("kf", "mean"), kn=("kn", "mean")).reset_index()
pt = pt.merge(df_tumor[["sample", "admix", "admix_z"]], on="sample", how="inner").sort_values("sample")

kn = pt["kn"].values
adm = pt["admix"].values
z1 = pt["admix_z"].values                                     # z over 754
z2 = (adm - adm.mean()) / adm.std(ddof=1)                     # z over 746

print("corrcoef(kn, admix raw):", np.corrcoef(kn, adm)[0, 1])
print("corrcoef(kn, z1):", np.corrcoef(kn, z1)[0, 1])
print("corrcoef(kn, z2):", np.corrcoef(kn, z2)[0, 1])
print("linregress r (z1):", linregress(z1, kn).rvalue)
print("linregress r (z2):", linregress(z2, kn).rvalue)

# affine relation z1 -> z2 ?
M1 = df_tumor.loc[df_tumor.cancer == c, "admix"].mean()
S1 = df_tumor.loc[df_tumor.cancer == c, "admix"].std(ddof=1)
M2, S2 = adm.mean(), adm.std(ddof=1)
z2_pred = (S1 / S2) * z1 + (M1 - M2) / S2
print("max |z2 - affine(z1)|:", np.abs(z2 - z2_pred).max())
print("z1[:5]:", z1[:5])
print("z2[:5]:", z2[:5])
print("dtypes:", pt["admix_z"].dtype, pt["kn"].dtype)
print("any NaN z1/kn:", np.isnan(z1).any(), np.isnan(kn).any())
