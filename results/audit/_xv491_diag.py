# diag: why KIRC r differs slightly from purity csv
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import linregress

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
pairs = pd.read_csv(ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv").rename(columns={"omega_floor": "omega"})
adm = pd.read_csv(ROOT / "results" / "nc49_tcga_admix_scores.csv")

print("admix rows:", len(adm), "unique samples:", adm["sample"].nunique())
dups = adm[adm.duplicated("sample", keep=False)].sort_values("sample")
print("duplicated sample rows in admix_scores:", len(dups))
if len(dups):
    print(dups.to_string())

adm_t = adm[adm.type == "Tumor"]
print("tumor rows:", len(adm_t), "unique:", adm_t["sample"].nunique())

for c in ["TCGA-KIRC"]:
    sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    ss = set(sub.sample_a) | set(sub.sample_b)
    print(c, "TT unique samples:", len(ss))
    a_c = adm_t[adm_t["sample"].isin(ss)]
    print(c, "admix rows matching TT samples:", len(a_c), "unique:", a_c["sample"].nunique())
    # median split count check
    print("admix median:", a_c["admix"].median())
