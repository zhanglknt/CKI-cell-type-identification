"""Quick spot-check of key numerical claims against CSV data (v19+)."""
import pandas as pd
import numpy as np
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"

print("=" * 60)
print("SPOT-CHECK v19+: 关键数值核验")
print("=" * 60)

errors = 0

# ============================================================
# 1. TCGA NN/TT ratios (图脚本用 median, 非 mean)
# ============================================================
print("\n--- 1. TCGA NN/TT (median-based) ---")
df = pd.read_csv(RESULTS / "phase34_v2_summary.csv")
cancer_map = {
    "TCGA-LUAD": "LUAD", "TCGA-LUSC": "LUSC", "TCGA-LIHC": "LIHC",
    "TCGA-KIRC": "KIRC", "TCGA-BRCA": "BRCA"
}
expected_nn_tt = {"BRCA": 1.40, "LUSC": 1.43, "LUAD": 1.60, "KIRC": 1.98, "LIHC": 2.83}
for _, r in df.iterrows():
    name = cancer_map[r["Project"]]
    actual = r["omega_NN_median"] / r["omega_TT_median"]
    exp_val = expected_nn_tt[name]
    match = abs(actual - exp_val) < 0.02
    status = "OK" if match else "MISMATCH!"
    if not match: errors += 1
    print(f"  {name}: claim={exp_val:.2f}, actual={actual:.2f} [{status}]")

# ============================================================
# 2. Mouse pilot categories
# ============================================================
print("\n--- 2. Mouse Pilot omega ---")
df2 = pd.read_csv(RESULTS / "mouse_pilot_v2_results.csv")
cat_map = {"C_control": "C", "S_same_ct": "S", "D_diff_ct": "D", "X_cross": "X"}
cat_expected = {"C": 1.54, "S": 4.03, "D": 13.18, "X": 7.07}
cat_n = {"C": 6, "S": 4, "D": 3, "X": 2}
for cat_code in sorted(df2["category"].unique()):
    sub = df2[df2["category"] == cat_code]
    short = cat_map[cat_code]
    actual = sub["omega"].mean()
    exp_val = cat_expected[short]
    match = abs(actual - exp_val) < 0.03
    status = "OK" if match else "MISMATCH!"
    if not match: errors += 1
    print(f"  {short}: claim={exp_val:.2f}, actual={actual:.2f}, n={len(sub)} [{status}]")

# Also verify full matrix 703 pairs
df_fm = pd.read_csv(RESULTS / "full_matrix_pairs.csv")
fm_omega = df_fm["omega"].mean()
print(f"  Full matrix: 703 pairs, mean omega={fm_omega:.2f} (claim: 703, 7.62)")
if len(df_fm) != 703: errors += 1
if abs(fm_omega - 7.62) > 0.05: errors += 1

# ============================================================
# 3. Brain CT omega means
# ============================================================
print("\n--- 3. Brain CT omega ---")
df3 = pd.read_csv(RESULTS / "brain_siletti_ct_summary_v3.csv")
brain_ct_map = {
    "Bergmann glia": ("Bergmann glia", 2.37, 21),
    "Committed oligodendrocyte precursor": ("COP", 3.17, 1326),
    "Vascular": ("Vascular", 3.40, 3321),
    "Fibroblast": ("Fibroblast", 3.99, 3403),
    "Ependymal": ("Ependymal", 4.13, 780),
    "Choroid plexus": ("Choroid", 4.80, 15),
    "Oligodendrocyte precursor": ("OPC", 7.65, 5671),
    "Microglia": ("Microglia", 8.02, 5671),
    "Oligodendrocyte": ("Oligodendrocyte", 8.66, 5778),
    "Astrocyte": ("Astrocyte", 14.36, 5778),
}
for _, r in df3.iterrows():
    ct = r["cell_type"]
    info = brain_ct_map.get(ct)
    if info:
        short, exp_m, exp_n = info
        match_m = abs(r["omega_mean"] - exp_m) < 0.03
        match_n = r["n_pairs"] == exp_n
        flags = []
        if not match_m: errors += 1; flags.append(f"MEAN(exp={exp_m})")
        if not match_n: errors += 1; flags.append(f"N(exp={exp_n})")
        status = "OK" if not flags else "MISMATCH: " + ", ".join(flags)
        print(f"  {short}: claim={exp_m:.2f} n={exp_n} | actual={r['omega_mean']:.2f} n={r['n_pairs']:.0f} [{status}]")

global_mean = df3["omega_mean"].mean()
wt_mean = (df3["omega_mean"] * df3["n_pairs"]).sum() / df3["n_pairs"].sum()
print(f"  Global mean (weighted): {wt_mean:.2f} (claim: 8.01)")
if abs(wt_mean - 8.01) > 0.05: errors += 1

# ============================================================
# 4. Phase35 AUC
# ============================================================
print("\n--- 4. AUC ---")
auc = np.load(RESULTS / "figure_data_auc.npy", allow_pickle=True).item()
for k, exp_v in [("CKI \u03c9", 0.716), ("Cosine", 0.887)]:
    actual_v = auc.get(k)
    if actual_v is not None:
        match = abs(actual_v - exp_v) < 0.005
        status = "OK" if match else "MISMATCH!"
        if not match: errors += 1
        print(f"  {k}: claim={exp_v:.3f}, actual={actual_v:.4f} [{status}]")
    else:
        print(f"  {k}: NOT FOUND in figure_data_auc.npy!")
        errors += 1

# ============================================================
# 5. Migration candidates
# ============================================================
print("\n--- 5. Migration candidates ---")
df_m = pd.read_csv(RESULTS / "brain_siletti_migration_candidates_v3.csv")
tiers = df_m["tier"].value_counts()
for t, exp_c in [("Strong", 30), ("Moderate", 1247), ("Weak", 6567)]:
    actual_c = int(tiers.get(t, 0))
    match = actual_c == exp_c
    status = "OK" if match else "MISMATCH!"
    if not match: errors += 1
    print(f"  {t}: claim={exp_c}, actual={actual_c} [{status}]")

strong = df_m[df_m["tier"] == "Strong"]
ct_breakdown = {"Astrocyte": 6, "Fibroblast": 1, "Microglia": 10,
                "Oligodendrocyte": 10, "Vascular": 3}
for ct, exp_c in ct_breakdown.items():
    actual_c = int((strong["cell_type"] == ct).sum())
    match = actual_c == exp_c
    status = "OK" if match else "MISMATCH!"
    if not match: errors += 1
    print(f"  Strong-{ct}: claim={exp_c}, actual={actual_c} [{status}]")

# ============================================================
# 6. Phase33 human pairs
# ============================================================
print("\n--- 6. Phase33 Human ---")
df_h = pd.read_csv(RESULTS / "phase33_v3_human_pairs.csv")
n_human = len(df_h)
print(f"  Pairs: {n_human} (claim: 5151)")
if n_human != 5151: errors += 1

# ============================================================
# 7. Table 2: Cross-organ conservation summary
# ============================================================
print("\n--- 7. Table 2 Cross-organ ---")
# Read aggregated summary (preferred) or compute from per-pair
summary_file = RESULTS / "phase35_cross_organ_summary.csv"
if summary_file.exists():
    df_cs = pd.read_csv(summary_file, index_col=0)
    expected_table2 = {
        "b cell": (2.70, 1),
        "neutrophil": (2.72, 6),
        "plasma cell": (6.61, 6),
        "erythrocyte": (6.90, 3),
        "macrophage": (9.84, 15),
        "endothelial cell": (15.09, 3),
    }
    for ct, (exp_mean, exp_n) in expected_table2.items():
        if ct in df_cs.index:
            row = df_cs.loc[ct]
            match_m = abs(row["mean_omega"] - exp_mean) < 0.02
            match_n = int(row["n_pairs"]) == exp_n
            flags = []
            if not match_m: errors += 1; flags.append(f"MEAN(exp={exp_mean})")
            if not match_n: errors += 1; flags.append(f"N(exp={exp_n})")
            status = "OK" if not flags else "MISMATCH: " + ", ".join(flags)
            print(f"  {ct:<30}: mean={row['mean_omega']:.2f} n={int(row['n_pairs'])} [{status}]")
        else:
            print(f"  {ct:<30}: NOT FOUND!")
            errors += 1
    print(f"  Summary: {len(df_cs)} cell types, {int(df_cs['n_pairs'].sum())} total pairs (claim: 17 CTs, 59 pairs)")
    if len(df_cs) != 17 or int(df_cs["n_pairs"].sum()) != 59:
        errors += 1
else:
    # Fallback: aggregate from per-pair CSV
    df_co = pd.read_csv(RESULTS / "phase35_cross_organ_conservation.csv")
    agg = df_co.groupby("ct").agg(mean_omega=("omega", "mean"), n_pairs=("omega", "count"))
    print(f"  Aggregated from per-pair CSV: {len(agg)} cell types, {len(df_co)} pairs (claim: 17 CTs, 59 pairs)")
    if len(agg) != 17 or len(df_co) != 59:
        errors += 1

# ============================================================
# FINAL
# ============================================================
print("\n" + "=" * 60)
if errors == 0:
    print("VERDICT: 全部核验通过 (0 errors). 数据准确, 引用清晰.")
else:
    print(f"VERDICT: 发现 {errors} 处不匹配!")
print("=" * 60)
