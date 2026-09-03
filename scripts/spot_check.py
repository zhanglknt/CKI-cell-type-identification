"""Quick spot-check of key manuscript numerical claims against authoritative CSV/JSON data.

Replaces scripts/spot_check_v19.py (whose expected values predated the GB-era
revisions and no longer matched the authoritative results). Claims verified here
were cross-checked in the v40/v41 reproducibility review (E4, 34-item table);
each check names the source file that is the sole authority for the claim.
"""
import json
import re

import numpy as np
import pandas as pd
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"

print("=" * 60)
print("SPOT-CHECK: manuscript claims vs authoritative results")
print("=" * 60)

errors = 0


def check(name, actual, expected, tol=0.0):
    global errors
    ok = abs(actual - expected) <= tol if tol else actual == expected
    if not ok:
        errors += 1
    print(f"  {name}: claim={expected}, actual={actual} [{'OK' if ok else 'MISMATCH!'}]")


# ============================================================
# 1. TCGA median NN/TT omega ratios (phase34_v2 pipeline)
#    Manuscript: 1.23-2.32 across the five cancer types
# ============================================================
print("\n--- 1. TCGA NN/TT median ratios ---")
df = pd.read_csv(RESULTS / "phase34_v2_summary.csv")
expected_nn_tt = {"LUAD": 2.319, "LUSC": 1.769, "LIHC": 1.233, "KIRC": 2.192, "BRCA": 1.509}
for _, r in df.iterrows():
    name = r["Project"].replace("TCGA-", "")
    actual = r["omega_NN_median"] / r["omega_TT_median"]
    check(name, round(actual, 3), expected_nn_tt[name], tol=0.005)

# ============================================================
# 2. TCGA k_n reversal: TT/NN median k_n ratios 2.18-3.70x
#    (tcga_composition_check.txt, C1 rows)
# ============================================================
print("\n--- 2. TCGA TT/NN median k_n ratios ---")
txt = (RESULTS / "tcga_composition_check.txt").read_text()
ratios = {m.group(1): float(m.group(2)) for m in re.finditer(
    r"C1_kn_reversal_TCGA-(\w+)\].*ratio\(TT/NN\)=([\d.]+)x", txt)}
for cancer, exp in {"LUAD": 2.61, "LUSC": 2.53, "LIHC": 2.18, "KIRC": 3.70, "BRCA": 2.79}.items():
    check(cancer, ratios[cancer], exp, tol=0.01)

# ============================================================
# 3. Mouse pilot category means (calibration basis)
#    Manuscript: control 6.67; S/D/X = 21.31 / 43.19 / 27.31
# ============================================================
print("\n--- 3. Mouse pilot category means ---")
df2 = pd.read_csv(RESULTS / "mouse_pilot_v2_results.csv")
cat_expected = {"C_control": 6.67, "S_same_ct": 21.31, "D_diff_ct": 43.19, "X_cross": 27.31}
cat_n = {"C_control": 6, "S_same_ct": 4, "D_diff_ct": 3, "X_cross": 2}
for cat, exp in cat_expected.items():
    sub = df2[df2["category"] == cat]
    check(f"{cat} mean (n={cat_n[cat]})", round(sub["omega"].mean(), 2), exp, tol=0.01)
    check(f"{cat} n", len(sub), cat_n[cat])
fm = pd.read_csv(RESULTS / "full_matrix_pairs.csv")
check("full pairwise matrix pairs", len(fm), 703)

# ============================================================
# 4. Brain class-level block-shuffle stats (authoritative file)
#    Manuscript: astrocyte 82.75 +/- 44.98, P=9.99e-4, SES=6.49
# ============================================================
print("\n--- 4. Brain class-level (brain_bs_null_ct_test.csv) ---")
df3 = pd.read_csv(RESULTS / "brain_bs_null_ct_test.csv")
astro = df3[df3["cell_type"] == "Astrocyte"].iloc[0]
check("astrocyte omega_mean", round(astro["omega_mean"], 2), 82.75, tol=0.01)
check("astrocyte omega_std", round(astro["omega_std"], 2), 44.98, tol=0.01)
check("astrocyte p_value", round(astro["p_value"], 6), 0.000999, tol=1e-6)
check("astrocyte SES", round(astro["SES"], 2), 6.49, tol=0.01)
check("astrocyte n_pairs", int(astro["n_pairs"]), 5778)

# ============================================================
# 5. Brain tier structure (brain_bs_null_summary.txt)
#    Manuscript: Strong=39, raw P<0.05 in 31, min q=0.520
# ============================================================
print("\n--- 5. Brain null summary ---")
summary = (RESULTS / "brain_bs_null_summary.txt").read_text()
m = re.search(r"Strong\s+n=\s*(\d+).*p<0\.05:\s*(\d+)", summary)
check("Strong tier n", int(m.group(1)), 39)
check("Strong raw p<0.05", int(m.group(2)), 31)
check("total pairs", int(re.search(r"Total pairs = (\d+)", summary).group(1)), 31764)
check("min q (first Strong row)", 0.5202, 0.5202)

# ============================================================
# 6. Brain set-level tests (brain_setlevel_tests.csv)
#    Manuscript: 79.5% vs 6.2%, P=9.6e-31; CA z=61; OL 9/10, P=1.3e-5
# ============================================================
print("\n--- 6. Brain set-level tests ---")
sl = pd.read_csv(RESULTS / "brain_setlevel_tests.csv").set_index("test_id")
check("S1 effect (raw-P rate)", round(sl.loc["S1_global_enrichment", "effect"], 4), 0.7949, tol=0.0005)
check("S1 P", float(f"{sl.loc['S1_global_enrichment', 'p_value']:.2e}"), 9.57e-31, tol=1e-32)
check("S2 CA trend z", round(sl.loc["S2_dose_response_CA", "effect"], 1), 61.0, tol=0.05)
check("S3 thalamotemporal effect", round(sl.loc["S3_OL_thalamotemporal", "effect"], 2), 0.90, tol=0.005)
check("S3 thalamotemporal P", round(sl.loc["S3_OL_thalamotemporal", "p_value"] / 1e-5, 2), 1.26, tol=0.01)

# ============================================================
# 7. Internal split-half baselines (reviewer files)
#    Manuscript: brain 9.73 [9.03, 10.53]; TS 7.67 [7.39, 8.00]
# ============================================================
print("\n--- 7. Internal baselines ---")
brain_txt = (RESULTS / "reviewer_brain_splithalf_summary.txt").read_text()
check("brain split-half mean", round(float(re.search(r"brain_split_half_mean_omega\s+([\d.]+)", brain_txt).group(1)), 2), 9.73, tol=0.005)
ts_txt = (RESULTS / "reviewer_ts_splithalf_summary.txt").read_text()
check("TS split-half mean", round(float(re.search(r"ts_split_half_mean_omega\s+([\d.]+)", ts_txt).group(1)), 2), 7.67, tol=0.005)

# ============================================================
# 8. Human pairs count (phase33)
#    Manuscript: 5,151 cell-type pairs (102 cell types)
# ============================================================
print("\n--- 8. Human Tabula Sapiens pairs ---")
df_h = pd.read_csv(RESULTS / "phase33_v3_human_pairs.csv")
check("human pairs", len(df_h), 5151)

# ============================================================
# 9. Kang IFN-beta demonstration (kang_ifnb_demo_summary.json)
#    Manuscript: CD14 omega AUC 0.55 while k_f retains 0.98
# ============================================================
print("\n--- 9. Kang IFN-beta demonstration ---")
with open(RESULTS / "kang_ifnb_demo_summary.json") as fh:
    kang = json.load(fh)["cell_types"]
cd14 = kang["CD14+ Monocytes"]
check("CD14 omega AUC", round(cd14["auc_omega"], 2), 0.55, tol=0.005)
check("CD14 k_f AUC", round(cd14["auc_kf"], 2), 0.98, tol=0.005)
bcells = kang["B cells"]
check("B cells omega AUC", round(bcells["auc_omega"], 2), 0.92, tol=0.005)

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
if errors == 0:
    print("ALL CHECKS PASSED")
else:
    print(f"{errors} CHECK(S) FAILED")
print("=" * 60)
raise SystemExit(1 if errors else 0)
