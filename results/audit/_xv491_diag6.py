# diag6: find KIRC rows where stored admix_z deviates from manual per-group z
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
df_ss = pd.read_csv(ROOT / "results" / "nc49_tcga_admix_scores.csv")
df_tumor = df_ss[df_ss.type == "Tumor"].copy()
df_tumor["admix_z"] = df_tumor.groupby("cancer")["admix"].transform(
    lambda x: (x - x.mean()) / x.std(ddof=1))

c = "TCGA-KIRC"
g = df_tumor[df_tumor.cancer == c].copy()
g["z_manual"] = (g["admix"] - g["admix"].mean()) / g["admix"].std(ddof=1)
g["err"] = (g["admix_z"] - g["z_manual"]).abs()
print("KIRC rows:", len(g), "max err:", g["err"].max())
bad = g[g["err"] > 1e-9].sort_values("err", ascending=False)
print("bad rows:", len(bad))
print(bad[["sample", "admix", "admix_z", "z_manual", "err"]].head(15).to_string())

# check the original csv file: does it contain an admix_z column? No - admix_scores has no z.
# So z is computed identically in both paths. Where does stored z1 for those samples
# come from? Try: z computed over the POOLED 5-cancer tumor set?
allM, allS = df_tumor["admix"].mean(), df_tumor["admix"].std(ddof=1)
bad2 = bad.copy()
bad2["z_pooled"] = (bad2["admix"] - allM) / allS
print("\nvs pooled-tumor z:")
print(bad2[["sample", "admix_z", "z_pooled"]].head(15).to_string())
print("pooled err max:", (bad2["admix_z"] - bad2["z_pooled"]).abs().max())

# or z computed over all samples (tumor+normal) of that cancer?
gc = df_ss[df_ss.cancer == c]
z_all = (bad["admix"] - gc["admix"].mean()) / gc["admix"].std(ddof=1)
print("vs all-samples-of-cancer z max err:", (bad["admix_z"] - z_all).abs().max())

# groupby structure sanity: how many groups, group sizes
print("\ngroup sizes:", df_tumor.groupby("cancer").size().to_dict())
# does transform return aligned? spot check a few good rows
ok = g[g["err"] <= 1e-9]
print("ok rows:", len(ok))
