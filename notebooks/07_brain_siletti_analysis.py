"""
CKI Brain Analysis: Siletti et al. (2023) Non-neuronal nuclei
==============================================================
Complete traceable analysis pipeline for NAR manuscript Section: 
"Cross-region transcriptional remodeling in the human brain"

Analysis:
1. Load Siletti Nonneurons.h5ad (888,263 nuclei, 59,480 genes)
2. Verify cell type annotations and nuclei counts
3. Filter: >=20 nuclei per (region, cell_type), >=50 nuclei per region
4. Create pseudobulks per (supercluster_term, roi)
5. Compute CKI omega for all same-cell-type cross-region pairs
6. Summarize omega gradient per cell type
7. Run multiplicative migration detection model
8. Output: CSV + detailed report

CKI: v0.2.0 — global HK k_n + per-pair top-200 DE k_f (hybrid scheme)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import scanpy as sc
from pathlib import Path
from scipy.stats import mannwhitneyu
from cki.core import compute_omega, js_divergence
from cki.gene_sets import detect_housekeeping_genes, genes_to_indices

# ===== Config =====
SILETTI_PATH = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\brain\Nonneurons.h5ad")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

MIN_NUCLEI_PER_GROUP = 20     # per (region, cell_type)
MIN_NUCLEI_PER_REGION = 50    # per region
N_TOP_KF = 200                # per-pair top DE genes
RANDOM_SEED = 42

# ===== 1. Load data =====
print("=" * 60)
print("1. Loading Siletti Nonneurons.h5ad...")
print("=" * 60)

adata = sc.read_h5ad(SILETTI_PATH)
print(f"  Shape: {adata.shape}")
print(f"  Nuclei: {adata.n_obs}, Genes: {adata.n_vars}")

# Check cell type annotations
ct_col = "supercluster_term"
region_col = "roi"

print(f"\n  Cell types ({ct_col}):")
ct_counts = adata.obs[ct_col].value_counts()
for ct, n in ct_counts.items():
    print(f"    {ct}: {n:,}")
total_n = ct_counts.sum()
print(f"    TOTAL: {total_n:,}")

print(f"\n  Brain regions ({region_col}): {adata.obs[region_col].nunique()}")

# ===== 2. Identify Bergmann glia + committed OPC as separate types =====
# The 10 cell classes in the manuscript include both OPC and Committed OPC
# as well as Bergmann glia as a distinct class
print(f"\n  All supercluster_terms: {sorted(adata.obs[ct_col].unique())}")
print(f"  Count per type:\n{adata.obs[ct_col].value_counts().to_string()}")

# ===== 3. Filter  =====
print("\n" + "=" * 60)
print("3. Filtering: >=20 nuclei per (region, ct) and >=50 per region...")
print("=" * 60)

# Count cells per group
groups = adata.obs.groupby([region_col, ct_col]).size().reset_index(name="count")
groups_ok = groups[groups["count"] >= MIN_NUCLEI_PER_GROUP]
print(f"  Groups passing >=20 nuclei: {len(groups_ok)} (from {len(groups)} total)")

# Count total nuclei per region
region_counts = adata.obs[region_col].value_counts()
regions_ok = region_counts[region_counts >= MIN_NUCLEI_PER_REGION].index
print(f"  Regions passing >=50 nuclei: {len(regions_ok)} (from {len(region_counts)} total)")

# Filter groups to only keep those in valid regions
groups_ok = groups_ok[groups_ok[region_col].isin(regions_ok)]
print(f"  Groups passing both filters: {len(groups_ok)}")

# Cell types present
cts_present = sorted(groups_ok[ct_col].unique())
print(f"  Cell types present: {cts_present}")

# ===== 4. Normalize and create pseudobulks =====
print("\n" + "=" * 60)
print("4. Normalizing and creating pseudobulks...")
print("=" * 60)

# Normalize in-place
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# Detect HK genes on this dataset
print("  Detecting housekeeping genes...")
hk_result = detect_housekeeping_genes(adata, method="combined", use_reference=True, species="human")
hk_genes = hk_result["genes"]
hk_indices = genes_to_indices(adata, hk_genes)
print(f"  HK genes: {len(hk_indices)} (detected {hk_result['n_detected']} + ref {hk_result['n_reference']})")

# Build pseudobulks
pseudobulk_data = {}  # key: (ct, region) -> pseudobulk vector
pseudobulk_meta = []  # list of metadata dicts

for _, row in groups_ok.iterrows():
    region = row[region_col]
    ct = row[ct_col]
    count = row["count"]
    
    mask = (adata.obs[region_col] == region) & (adata.obs[ct_col] == ct)
    group_adata = adata[mask]
    
    # Pseudobulk: mean log-normalized expression
    if hasattr(group_adata.X, "toarray"):
        pb = np.asarray(group_adata.X.mean(axis=0)).flatten()
    else:
        pb = np.asarray(group_adata.X.mean(axis=0)).flatten()
    
    key = (ct, region)
    pseudobulk_data[key] = pb
    pseudobulk_meta.append({
        "cell_type": ct,
        "region": region,
        "n_nuclei": count,
        "key": f"{ct} | {region}",
    })

print(f"  Total pseudobulks: {len(pseudobulk_data)}")

# ===== 5. Compute omega for all same-CT cross-region pairs =====
print("\n" + "=" * 60)
print("5. Computing CKI omega (global HK k_n + per-pair top-N k_f)...")
print("=" * 60)

# Organize by cell type
ct_to_regions = {}
for ct in cts_present:
    ct_to_regions[ct] = [r for r in groups_ok[groups_ok[ct_col] == ct][region_col]]

# Count total pairs
total_pairs = 0
for ct, regions in ct_to_regions.items():
    n_r = len(regions)
    total_pairs += n_r * (n_r - 1) // 2
print(f"  Total same-CT cross-region pairs: {total_pairs}")

# Compute omega
pair_results = []
pair_idx = 0
for ct, regions in ct_to_regions.items():
    n_r = len(regions)
    print(f"  {ct}: {n_r} regions, {n_r*(n_r-1)//2} pairs")
    
    for i in range(n_r):
        for j in range(i + 1, n_r):
            r_i, r_j = regions[i], regions[j]
            pb_i = pseudobulk_data[(ct, r_i)]
            pb_j = pseudobulk_data[(ct, r_j)]
            
            # k_n: global HK genes
            hk_i = pb_i[hk_indices]
            hk_j = pb_j[hk_indices]
            kn_val = js_divergence(hk_i, hk_j)
            
            # k_f: per-pair top-N DE genes (exclude HK)
            abs_diff = np.abs(pb_i - pb_j)
            non_hk_mask = np.ones(len(pb_i), dtype=bool)
            non_hk_mask[hk_indices] = False
            abs_diff_non_hk = abs_diff[non_hk_mask]
            
            top_n = min(N_TOP_KF, len(abs_diff_non_hk))
            # Get indices in the non-HK space
            non_hk_indices = np.where(non_hk_mask)[0]
            top_local = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
            top_local = top_local[np.argsort(abs_diff_non_hk[top_local])[::-1]]
            top_global = non_hk_indices[top_local]
            
            kf_val = js_divergence(pb_i[top_global], pb_j[top_global])
            omega_val = kf_val / kn_val if kn_val > 0 else float('inf')
            
            pair_results.append({
                "cell_type": ct,
                "region_a": r_i,
                "region_b": r_j,
                "omega": omega_val,
                "kn": kn_val,
                "kf": kf_val,
            })
            pair_idx += 1
            if pair_idx % 5000 == 0:
                print(f"    Progress: {pair_idx}/{total_pairs} pairs")

print(f"  Complete: {len(pair_results)} pairs computed")

# Convert to DataFrame
pairs_df = pd.DataFrame(pair_results)

# ===== 6. Per-cell-type omega summary =====
print("\n" + "=" * 60)
print("6. Per-cell-type omega summary...")
print("=" * 60)

ct_summary = []
for ct in cts_present:
    ct_pairs = pairs_df[pairs_df["cell_type"] == ct]
    n_pairs = len(ct_pairs)
    n_regions = len(ct_to_regions[ct])
    omega_mean = ct_pairs["omega"].mean()
    omega_median = ct_pairs["omega"].median()
    omega_std = ct_pairs["omega"].std()
    omega_min = ct_pairs["omega"].min()
    omega_max = ct_pairs["omega"].max()
    
    n_nuclei = sum(
        meta["n_nuclei"] 
        for meta in pseudobulk_meta 
        if meta["cell_type"] == ct
    )
    
    ct_summary.append({
        "cell_type": ct,
        "n_regions": n_regions,
        "n_pairs": n_pairs,
        "n_nuclei": n_nuclei,
        "omega_mean": round(omega_mean, 2),
        "omega_median": round(omega_median, 2),
        "omega_std": round(omega_std, 2),
        "omega_min": round(omega_min, 2),
        "omega_max": round(omega_max, 2),
    })
    
    print(f"  {ct}: n_regions={n_regions}, n_pairs={n_pairs}, "
          f"mean={omega_mean:.2f}, std={omega_std:.2f}")

ct_summary_df = pd.DataFrame(ct_summary).sort_values("omega_mean", ascending=True)

# Gradient fold
ct_min = ct_summary_df.iloc[0]
ct_max = ct_summary_df.iloc[-1]
gradient_fold = ct_max["omega_mean"] / ct_min["omega_mean"] if ct_min["omega_mean"] > 0 else float('inf')
print(f"\n  Omega gradient: {ct_min['cell_type']} ({ct_min['omega_mean']}) -> "
      f"{ct_max['cell_type']} ({ct_max['omega_mean']}), "
      f"fold = {gradient_fold:.2f}")

# ===== 7. Multiplicative migration detection model =====
print("\n" + "=" * 60)
print("7. Multiplicative migration detection model...")
print("=" * 60)

# Compute grand mean
grand_mean = pairs_df["omega"].mean()
print(f"  Grand mean omega: {grand_mean:.2f}")

# Per-cell-type mean (mu_ct)
mu_ct = {}
for ct in cts_present:
    mu_ct[ct] = pairs_df[pairs_df["cell_type"] == ct]["omega"].mean()

# Per-region-pair mean (mu_rp)
# Use all region pairs across all cell types
all_region_pairs = set()
for _, row in pairs_df.iterrows():
    rp = tuple(sorted([row["region_a"], row["region_b"]]))
    all_region_pairs.add(rp)

mu_rp = {}
for rp in all_region_pairs:
    mask = ((pairs_df["region_a"] == rp[0]) & (pairs_df["region_b"] == rp[1])) | \
           ((pairs_df["region_a"] == rp[1]) & (pairs_df["region_b"] == rp[0]))
    subset = pairs_df[mask]
    if len(subset) > 0:
        mu_rp[rp] = subset["omega"].mean()

# Compute expected and residual for each pair
migration_results = []
for _, row in pairs_df.iterrows():
    ct = row["cell_type"]
    rp = tuple(sorted([row["region_a"], row["region_b"]]))
    
    if ct in mu_ct and rp in mu_rp:
        expected = mu_ct[ct] * mu_rp[rp] / grand_mean
    else:
        expected = grand_mean
    
    residual = row["omega"] / expected if expected > 0 else 1.0
    
    # Classification
    if residual < 0.3:
        tier = "Strong"
    elif residual < 0.5:
        tier = "Moderate"
    elif residual < 0.75:
        tier = "Weak"
    else:
        tier = "None"
    
    migration_results.append({
        "cell_type": ct,
        "region_a": row["region_a"],
        "region_b": row["region_b"],
        "omega": row["omega"],
        "expected_omega": round(expected, 2),
        "residual": round(residual, 4),
        "tier": tier,
    })

migration_df = pd.DataFrame(migration_results)

# Summary stats
strong = migration_df[migration_df["tier"] == "Strong"]
moderate = migration_df[migration_df["tier"] == "Moderate"]
weak = migration_df[migration_df["tier"] == "Weak"]
total = len(migration_df)

print(f"  Total pairs: {total}")
print(f"  Strong (residual < 0.3): {len(strong)} ({len(strong)/total*100:.1f}%)")
print(f"  Moderate (residual < 0.5): {len(moderate)} ({len(moderate)/total*100:.1f}%)")
print(f"  Weak (residual < 0.75): {len(weak)} ({len(weak)/total*100:.1f}%)")

# Per-cell-type strong count
strong_by_ct = strong["cell_type"].value_counts()
print(f"\n  Strong candidates by cell type:")
for ct in cts_present:
    n = strong_by_ct.get(ct, 0)
    print(f"    {ct}: {n}")

# Top strong candidates
print(f"\n  Top 10 Strong candidates (lowest residual):")
top_strong = strong.nsmallest(10, "residual")
for _, row in top_strong.iterrows():
    print(f"    {row['cell_type']}: {row['region_a']} vs {row['region_b']}, "
          f"omega={row['omega']:.2f}, expected={row['expected_omega']:.2f}, "
          f"residual={row['residual']:.4f}")

# ===== 8. Save results =====
print("\n" + "=" * 60)
print("8. Saving results...")
print("=" * 60)

# Save pairs CSV
pairs_csv = RESULTS_DIR / "brain_siletti_omega_pairs.csv"
pairs_df.to_csv(pairs_csv, index=False)
print(f"  Saved: {pairs_csv}")

# Save migration CSV
migration_csv = RESULTS_DIR / "brain_siletti_migration_candidates.csv"
migration_df.to_csv(migration_csv, index=False)
print(f"  Saved: {migration_csv}")

# Save per-CT summary
summary_csv = RESULTS_DIR / "brain_siletti_ct_summary.csv"
ct_summary_df.to_csv(summary_csv, index=False)
print(f"  Saved: {summary_csv}")

# ===== 9. Generate report =====
print("\n" + "=" * 60)
print("9. Generating report...")
print("=" * 60)

report_lines = []
report_lines.append("# CKI Brain Analysis Report\n")
report_lines.append("## Siletti et al. (2023) Non-neuronal nuclei — Reproducible Analysis\n")
report_lines.append(f"**Analysis script**: `notebooks/07_brain_siletti_analysis.py`  \n")
report_lines.append(f"**CKI version**: 0.2.0  \n")
report_lines.append(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
report_lines.append(f"**Dataset**: {SILETTI_PATH.name} ({adata.n_obs:,} nuclei, {adata.n_vars:,} genes)\n\n")

report_lines.append("## Dataset Summary\n")
report_lines.append("| Cell Type | Nuclei | Regions | Pairs | Omega Mean | Omega Std |\n")
report_lines.append("|---|---|---|---|---|---|\n")
for _, row in ct_summary_df.iterrows():
    report_lines.append(
        f"| {row['cell_type']} | {row['n_nuclei']:,} | {row['n_regions']} | "
        f"{row['n_pairs']} | {row['omega_mean']} | {row['omega_std']} |\n"
    )

report_lines.append(f"\n## Omega Gradient\n")
report_lines.append(f"- Lowest: {ct_min['cell_type']} (mean={ct_min['omega_mean']})\n")
report_lines.append(f"- Highest: {ct_max['cell_type']} (mean={ct_max['omega_mean']})\n")
report_lines.append(f"- Fold change: {gradient_fold:.2f}x\n\n")

report_lines.append("## Full Omega Gradient (low to high)\n")
for _, row in ct_summary_df.iterrows():
    bar_len = int(row["omega_mean"] / ct_max["omega_mean"] * 40)
    bar = "=" * bar_len
    report_lines.append(f"- {row['cell_type']}: {row['omega_mean']} [{bar}]\n")

report_lines.append(f"\n## Migration Candidates\n")
report_lines.append(f"- Total pairs: {total}\n")
report_lines.append(f"- Strong (residual < 0.3): {len(strong)} ({len(strong)/total*100:.2f}%)\n")
report_lines.append(f"- Moderate (residual < 0.5): {len(moderate)} ({len(moderate)/total*100:.2f}%)\n")
report_lines.append(f"- Weak (residual < 0.75): {len(weak)} ({len(weak)/total*100:.2f}%)\n\n")

report_lines.append("### Strong Candidates by Cell Type\n")
report_lines.append("| Cell Type | Strong Count |\n")
report_lines.append("|---|---|\n")
for ct in cts_present:
    n = strong_by_ct.get(ct, 0)
    report_lines.append(f"| {ct} | {n} |\n")

report_lines.append(f"\n### Top 20 Strong Candidates\n")
report_lines.append("| Cell Type | Region A | Region B | Omega | Expected | Residual |\n")
report_lines.append("|---|---|---|---|---|---|\n")
for _, row in top_strong.iterrows():
    report_lines.append(
        f"| {row['cell_type']} | {row['region_a']} | {row['region_b']} | "
        f"{row['omega']:.2f} | {row['expected_omega']:.2f} | {row['residual']:.4f} |\n"
    )

report_md = RESULTS_DIR / "brain_siletti_analysis_report.md"
with open(report_md, "w", encoding="utf-8") as f:
    f.writelines(report_lines)
print(f"  Saved: {report_md}")

print("\n" + "=" * 60)
print("Analysis complete!")
print("=" * 60)
print(f"\nKey numbers for manuscript:")
print(f"  Total pairs: {total}")
print(f"  Omega gradient: {gradient_fold:.2f}x ({ct_min['cell_type']}={ct_min['omega_mean']} -> {ct_max['cell_type']}={ct_max['omega_mean']})")
print(f"  Strong candidates: {len(strong)}")
print(f"  OPC most active: {strong_by_ct.get('Oligodendrocyte precursor', 0)} strong")
print(f"  Top signal: {top_strong.iloc[0]['cell_type']} {top_strong.iloc[0]['region_a']} vs {top_strong.iloc[0]['region_b']}, omega={top_strong.iloc[0]['omega']:.2f}, residual={top_strong.iloc[0]['residual']:.4f}")

# Also save to a simple key-values file for manuscript generation
key_values = {
    "total_pairs": total,
    "gradient_fold": round(gradient_fold, 2),
    "gradient_lowest_ct": ct_min["cell_type"],
    "gradient_lowest_omega": ct_min["omega_mean"],
    "gradient_highest_ct": ct_max["cell_type"],
    "gradient_highest_omega": ct_max["omega_mean"],
    "n_strong": len(strong),
    "n_moderate": len(moderate),
    "n_weak": len(weak),
    "pct_strong": round(len(strong)/total*100, 2),
    "pct_moderate": round(len(moderate)/total*100, 2),
    "pct_weak": round(len(weak)/total*100, 2),
    "n_nuclei": adata.n_obs,
    "n_genes": adata.n_vars,
}
kv_csv = RESULTS_DIR / "brain_siletti_key_values.csv"
pd.DataFrame([key_values]).to_csv(kv_csv, index=False)
print(f"  Saved: {kv_csv}")
