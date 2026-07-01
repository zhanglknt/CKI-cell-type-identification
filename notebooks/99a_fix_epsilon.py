"""
Bulk fix: remove epsilon from all omega calculations.
Changes:  omega_val = kf_val / (kn_val + 1e-9)
          omega = kf / (kn + 1e-9)
To:    omega_val = kf_val / kn_val if kn_val > 0 else float('inf')
          omega = kf / kn if kn > 0 else float('inf')
"""
import os
import re

NOTEBOOKS_DIR = r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks"

# Files to fix (from grep results)
target_files = [
    "02b_pilot_v2.py",
    "02c_pilot_v2b.py",
    "05_phase33_v3.py",
    "05_phase33_v3_fixed.py",
    "07b_brain_siletti_v2.py",
    "07c_brain_siletti_v3.py",
    "07d_brain_siletti_v4.py",
    "07_brain_siletti_analysis.py",
    "13_phase35_method_comparison.py",
    "30_nar_figures_final.py",
    "_fig1_clean.py",
]

old1 = "omega_val = kf_val / (kn_val + 1e-9)"
new1 = "omega_val = kf_val / kn_val if kn_val > 0 else float('inf')"

old2 = "omega = kf / (kn + 1e-9)"
new2 = "omega = kf / kn if kn > 0 else float('inf')"

total_replaced = 0

for fname in target_files:
    fpath = os.path.join(NOTEBOOKS_DIR, fname)
    if not os.path.exists(fpath):
        print(f"  SKIP (not found): {fname}")
        continue

    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()

    count1 = content.count(old1)
    count2 = content.count(old2)

    if count1 == 0 and count2 == 0:
        print(f"  SKIP (no match): {fname}")
        continue

    content = content.replace(old1, new1)
    content = content.replace(old2, new2)
    replaced = count1 + count2

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)

    total_replaced += replaced
    print(f"  FIXED: {fname} ({replaced} replacements: {count1}x old1, {count2}x old2)")

# Also fix compute_omega obs in 02b and 02c
# They use: omega_obs = kf_val / (kn_val + 1e-9)
old3 = "omega_obs = kf_val / (kn_val + 1e-9)"
new3 = "omega_obs = kf_val / kn_val if kn_val > 0 else float('inf')"

for fname in ["02b_pilot_v2.py", "02c_pilot_v2b.py"]:
    fpath = os.path.join(NOTEBOOKS_DIR, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    count3 = content.count(old3)
    if count3 > 0:
        content = content.replace(old3, new3)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        total_replaced += count3
        print(f"  FIXED: {fname} ({count3}x omega_obs)")

print(f"\nTotal replacements: {total_replaced}")
