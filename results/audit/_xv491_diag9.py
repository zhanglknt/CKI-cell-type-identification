# diag9: LUAD matrix vs pair-table samples; double-mutant accounting
from pathlib import Path
import json
import pandas as pd

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
pairs = pd.read_csv(ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv")
df_ss = pd.read_csv(ROOT / "results" / "nc49_tcga_admix_scores.csv")
mut = json.load(open(ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])

luad_tt = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")]
pt_samples = set(luad_tt.sample_a) | set(luad_tt.sample_b)
mat_samples = set(df_ss[(df_ss.cancer == "TCGA-LUAD") & (df_ss.type == "Tumor")]["sample"])
print("pair-table LUAD tumors:", len(pt_samples), "; matrix LUAD tumors:", len(mat_samples))
print("matrix-only (excluded):", sorted(mat_samples - pt_samples))
print("pair-table-only:", sorted(pt_samples - mat_samples))

# matched-to-matrix mutation labels
egfr_mat = {s for s in egfr if s in mat_samples}
kras_mat = {s for s in kras if s in mat_samples}
doubles_mat = egfr_mat & kras_mat
print(f"matrix-matched: EGFR {len(egfr_mat)}, KRAS {len(kras_mat)}, doubles {len(doubles_mat)} {sorted(doubles_mat)}")
# pair-table labels
lab = {s: ("DOUBLE" if s in egfr and s in kras else ("EGFR" if s in egfr else ("KRAS" if s in kras else "WT"))) for s in pt_samples}
from collections import Counter
print("pair-table label counts:", Counter(lab.values()))
