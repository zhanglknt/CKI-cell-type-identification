"""
CKI Phase 3.4 v2: TCGA Tumor Perturbation (per-cancer-type loading)
===================================================================
FIX: Load each cancer type independently with its own gene filtering,
     rather than globally filtering across all cancers (which dilutes signal).

Method: Phase 3.3 v3 hybrid omega (global k_n + per-pair k_f)
Data: UCSC Xena TCGA RSEM gene TPM (bulk RNA-seq)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import gzip, time, warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from cki.core import compute_omega, js_divergence

warnings.filterwarnings("ignore")

# === Config ===
RANDOM_SEED = 42
N_TOP_KF = 200
MIN_TUMOR = 30
MIN_NORMAL = 10
MAX_PAIRS_TT = 2000
MAX_PAIRS_TN = 2000

TARGET = [
    "TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"
]

# === Font ===
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
if os.path.exists(FONT_PATH):
    fm.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = "Microsoft YaHei"
    plt.rcParams["axes.unicode_minus"] = False

# ====================================================================
# 0. Preload HK gene mapping (done once)
# ====================================================================
print("=" * 60)
print("0. Loading HK gene mapping...")
print("=" * 60)

pm = pd.read_csv(PROBEMAP_FILE, sep="\t")
ens_to_symbol = {}
for _, row in pm.iterrows():
    ens_id = str(row.iloc[0]).split(".")[0]
    symbol = str(row.iloc[1])
    if ens_id and symbol and symbol != "nan":
        ens_to_symbol[ens_id] = symbol

symbol_to_ens = {}
for eid, sym in ens_to_symbol.items():
    symbol_to_ens.setdefault(sym, []).append(eid)

hk_df = pd.read_csv(HK_FILE)
hk_raw = hk_df.iloc[:, 0].dropna().astype(str)
hk_human = set()
for row in hk_raw:
    parts = row.split(";")
    if len(parts) >= 2:
        hk_human.add(parts[1].strip())
print(f"  HK gene symbols: {len(hk_human)}, probeMap: {len(ens_to_symbol)}")

# ====================================================================
# 1. Parse sample metadata (fast, no data load)
# ====================================================================
print("\n" + "=" * 60)
print("1. Parsing sample metadata...")
print("=" * 60)

TSS_TO_PROJECT = {
    "A1":"TCGA-BRCA","A2":"TCGA-BRCA","A7":"TCGA-BRCA","A8":"TCGA-BRCA",
    "AN":"TCGA-BRCA","AO":"TCGA-BRCA","AQ":"TCGA-BRCA","AR":"TCGA-BRCA",
    "B6":"TCGA-BRCA","BH":"TCGA-BRCA","C8":"TCGA-BRCA","D8":"TCGA-BRCA",
    "E2":"TCGA-BRCA","EW":"TCGA-BRCA","GI":"TCGA-BRCA","WT":"TCGA-BRCA",
    "XX":"TCGA-BRCA","E9":"TCGA-BRCA","GM":"TCGA-BRCA","HN":"TCGA-BRCA",
    "JL":"TCGA-BRCA","LD":"TCGA-BRCA","LL":"TCGA-BRCA","MS":"TCGA-BRCA",
    "OL":"TCGA-BRCA","PE":"TCGA-BRCA","PL":"TCGA-BRCA","S3":"TCGA-BRCA",
    "UL":"TCGA-BRCA","V7":"TCGA-BRCA","W8":"TCGA-BRCA","WV":"TCGA-BRCA",
    "05":"TCGA-LUAD","35":"TCGA-LUAD","38":"TCGA-LUAD","44":"TCGA-LUAD",
    "49":"TCGA-LUAD","50":"TCGA-LUAD","55":"TCGA-LUAD","64":"TCGA-LUAD",
    "67":"TCGA-LUAD","73":"TCGA-LUAD","75":"TCGA-LUAD","78":"TCGA-LUAD",
    "86":"TCGA-LUAD","91":"TCGA-LUAD","93":"TCGA-LUAD","97":"TCGA-LUAD",
    "J2":"TCGA-LUAD","L3":"TCGA-LUAD","L4":"TCGA-LUAD","M1":"TCGA-LUAD",
    "MP":"TCGA-LUAD","MT":"TCGA-LUAD","N1":"TCGA-LUAD","N6":"TCGA-LUAD",
    "O1":"TCGA-LUAD","S2":"TCGA-LUAD","TR":"TCGA-LUAD","TV":"TCGA-LUAD",
    "TQ":"TCGA-LUAD","NJ":"TCGA-LUAD","KN":"TCGA-LUAD","LF":"TCGA-LUAD",
    "18":"TCGA-LUSC","21":"TCGA-LUSC","22":"TCGA-LUSC","33":"TCGA-LUSC",
    "34":"TCGA-LUSC","37":"TCGA-LUSC","39":"TCGA-LUSC","43":"TCGA-LUSC",
    "51":"TCGA-LUSC","52":"TCGA-LUSC","56":"TCGA-LUSC","60":"TCGA-LUSC",
    "63":"TCGA-LUSC","66":"TCGA-LUSC","68":"TCGA-LUSC","70":"TCGA-LUSC",
    "77":"TCGA-LUSC","85":"TCGA-LUSC","90":"TCGA-LUSC","92":"TCGA-LUSC",
    "94":"TCGA-LUSC","96":"TCGA-LUSC","98":"TCGA-LUSC","CC":"TCGA-LUSC",
    "L5":"TCGA-LUSC","N2":"TCGA-LUSC","NK":"TCGA-LUSC","Q1":"TCGA-LUSC",
    "IE":"TCGA-LUSC","IF":"TCGA-LUSC","IG":"TCGA-LUSC",
    "BC":"TCGA-LIHC","DD":"TCGA-LIHC","ED":"TCGA-LIHC","EP":"TCGA-LIHC",
    "ES":"TCGA-LIHC","FV":"TCGA-LIHC","FY":"TCGA-LIHC","G3":"TCGA-LIHC",
    "GJ":"TCGA-LIHC","HP":"TCGA-LIHC","HU":"TCGA-LIHC","K7":"TCGA-LIHC",
    "KR":"TCGA-LIHC","LG":"TCGA-LIHC","NI":"TCGA-LIHC","O8":"TCGA-LIHC",
    "PD":"TCGA-LIHC","QN":"TCGA-LIHC","RC":"TCGA-LIHC","RG":"TCGA-LIHC",
    "T6":"TCGA-LIHC","UB":"TCGA-LIHC","WQ":"TCGA-LIHC","XR":"TCGA-LIHC",
    "YA":"TCGA-LIHC","ZP":"TCGA-LIHC","ZS":"TCGA-LIHC",
    "MI":"TCGA-LIHC","F5":"TCGA-LIHC",
    "A3":"TCGA-KIRC","AK":"TCGA-KIRC","AL":"TCGA-KIRC","AY":"TCGA-KIRC",
    "B0":"TCGA-KIRC","B1":"TCGA-KIRC","B2":"TCGA-KIRC","B3":"TCGA-KIRC",
    "B4":"TCGA-KIRC","B8":"TCGA-KIRC","BP":"TCGA-KIRC","BW":"TCGA-KIRC",
    "CJ":"TCGA-KIRC","CW":"TCGA-KIRC","CZ":"TCGA-KIRC","DV":"TCGA-KIRC",
    "DX":"TCGA-KIRC","EU":"TCGA-KIRC","GK":"TCGA-KIRC","HE":"TCGA-KIRC",
    "I6":"TCGA-KIRC","K6":"TCGA-KIRC","KL":"TCGA-KIRC","MM":"TCGA-KIRC",
    "MW":"TCGA-KIRC","P4":"TCGA-KIRC","Q2":"TCGA-KIRC","RG":"TCGA-KIRC",
    "UZ":"TCGA-KIRC","V5":"TCGA-KIRC","XM":"TCGA-KIRC","YE":"TCGA-KIRC",
}

t0_total = time.time()

with gzip.open(TCGA_FILE, "rt") as fh:
    header_line = fh.readline().strip().split("\t")

# Build project -> (tumor_ids, normal_ids) mapping
proj_tumor = {}
proj_normal = {}
for sid in header_line[1:]:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    tss = parts[1]
    proj = TSS_TO_PROJECT.get(tss)
    if proj is None or proj not in TARGET:
        continue
    sc = parts[3][:2]
    if sc == "01":
        proj_tumor.setdefault(proj, []).append(sid)
    elif sc == "11":
        proj_normal.setdefault(proj, []).append(sid)

usable = []
for proj in TARGET:
    nt = len(proj_tumor.get(proj, []))
    nn = len(proj_normal.get(proj, []))
    if nt >= MIN_TUMOR and nn >= MIN_NORMAL:
        usable.append(proj)
        print(f"  {proj}: T={nt}, N={nn}")
    else:
        print(f"  {proj}: T={nt}, N={nn} -> SKIP")

print(f"\n  Usable: {len(usable)} cancers")

# ====================================================================
# 2. Per-cancer-type loading and analysis
# ====================================================================

def load_cancer_data(cancer, tumor_ids, normal_ids):
    """Load expression matrix for ONE cancer type with its own gene filtering."""
    wanted = set(tumor_ids + normal_ids)
    
    # Build column index
    col_idx_map = {}
    for k, sid in enumerate(header_line[1:], 1):
        if sid in wanted:
            col_idx_map[sid] = k
    
    sample_list = sorted(wanted)
    col_arr = np.array([col_idx_map[s] for s in sample_list], dtype=np.int32)
    
    # Pass 1: count qualifying genes (expression > 0 in any wanted sample)
    gene_names = []
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split("\t")
            has_expr = False
            for ci in col_arr:
                if ci < len(parts):
                    try:
                        if float(parts[ci]) > 0:
                            has_expr = True
                            break
                    except (ValueError, IndexError):
                        pass
            if has_expr:
                gene_names.append(parts[0])
    
    n_genes = len(gene_names)
    
    # Pass 2: fill matrix
    expr = np.zeros((len(sample_list), n_genes), dtype=np.float32)
    gene_idx = 0
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split("\t")
            if gene_idx < n_genes and parts[0] == gene_names[gene_idx]:
                for si, ci in enumerate(col_arr):
                    if ci < len(parts):
                        try:
                            expr[si, gene_idx] = float(parts[ci])
                        except (ValueError, IndexError):
                            pass
                gene_idx += 1
                if gene_idx >= n_genes:
                    break
    
    # Per-cancer gene filtering: mean TPM >= 0.5
    gene_means = np.mean(expr, axis=0)
    keep = gene_means >= 0.5
    expr = expr[:, keep]
    genes = [g for g, k in zip(gene_names, keep) if k]
    
    # log2 transform
    expr_log = np.log2(np.maximum(expr, 0) + 0.001)
    
    # Map HK genes
    gene_ens = [g.split(".")[0] for g in genes]
    ens_to_idx_local = {ens: i for i, ens in enumerate(gene_ens)}
    hk_local = []
    for sym in hk_human:
        if sym in symbol_to_ens:
            for eid in symbol_to_ens[sym]:
                if eid in ens_to_idx_local:
                    hk_local.append(ens_to_idx_local[eid])
    hk_arr = np.array(sorted(set(hk_local)), dtype=int)
    
    # Build tumor/normal index arrays
    tumor_mask = np.array([s in tumor_ids for s in sample_list])
    normal_mask = np.array([s in normal_ids for s in sample_list])
    
    return expr_log, hk_arr, tumor_mask, normal_mask, genes


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    """Select top-N non-HK genes by absolute expression difference."""
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)


# ====================================================================
# 3. Per-cancer omega computation
# ====================================================================
print("\n" + "=" * 60)
print("3. Per-cancer omega analysis...")
print("=" * 60)

all_summary = []
all_pair_details = []  # store all TT/NN/TN pairs for combined analysis

for cancer in usable:
    t0_cancer = time.time()
    print(f"\n--- {cancer} ---")
    
    # Load
    print(f"  Loading data...")
    expr_log, hk_arr, tumor_mask, normal_mask, genes = load_cancer_data(
        cancer, proj_tumor[cancer], proj_normal[cancer]
    )
    t_idx = np.where(tumor_mask)[0]
    n_idx = np.where(normal_mask)[0]
    n_t = len(t_idx)
    n_n = len(n_idx)
    print(f"  Genes: {len(genes)}, HK: {len(hk_arr)}, T={n_t}, N={n_n}")
    
    # === TT pairs ===
    all_tt = [(i, j) for i in range(n_t) for j in range(i + 1, n_t)]
    n_tt_total = len(all_tt)
    np.random.seed(RANDOM_SEED)
    if n_tt_total > MAX_PAIRS_TT:
        tt_pairs = [all_tt[k] for k in np.random.choice(n_tt_total, MAX_PAIRS_TT, replace=False)]
    else:
        tt_pairs = all_tt
    
    omega_tt = np.full((n_t, n_t), np.nan)
    tt_details = []
    for idx, (i, j) in enumerate(tt_pairs):
        p1, p2 = expr_log[t_idx[i], :], expr_log[t_idx[j], :]
        id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
        omega_tt[i, j] = r["omega"]
        omega_tt[j, i] = r["omega"]
        tt_details.append({"pair_type": "TT", "cancer": cancer, "omega": r["omega"], "kn": r["kn"], "kf": r["kf"]})
        if (idx + 1) % 500 == 0:
            print(f"    TT: {idx+1}/{len(tt_pairs)}", end="\r")
    print(f"    TT: {len(tt_pairs)}/{n_tt_total} done")
    
    # === NN pairs ===
    n_nn_total = n_n * (n_n - 1) // 2
    omega_nn = np.full((n_n, n_n), np.nan)
    nn_details = []
    for i in range(n_n):
        for j in range(i + 1, n_n):
            p1, p2 = expr_log[n_idx[i], :], expr_log[n_idx[j], :]
            id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
            r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
            omega_nn[i, j] = r["omega"]
            omega_nn[j, i] = r["omega"]
            nn_details.append({"pair_type": "NN", "cancer": cancer, "omega": r["omega"], "kn": r["kn"], "kf": r["kf"]})
    print(f"    NN: {n_nn_total} done")
    
    # === TN pairs ===
    all_tn = [(i, j) for i in range(n_t) for j in range(n_n)]
    n_tn_total = len(all_tn)
    if n_tn_total > MAX_PAIRS_TN:
        tn_pairs = [all_tn[k] for k in np.random.choice(n_tn_total, MAX_PAIRS_TN, replace=False)]
    else:
        tn_pairs = all_tn
    
    omega_tn = np.full((n_t, n_n), np.nan)
    tn_details = []
    for idx, (i, j) in enumerate(tn_pairs):
        p1, p2 = expr_log[t_idx[i], :], expr_log[n_idx[j], :]
        id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
        omega_tn[i, j] = r["omega"]
        tn_details.append({"pair_type": "TN", "cancer": cancer, "omega": r["omega"], "kn": r["kn"], "kf": r["kf"]})
        if (idx + 1) % 500 == 0:
            print(f"    TN: {idx+1}/{len(tn_pairs)}", end="\r")
    print(f"    TN: {len(tn_pairs)}/{n_tn_total} done")
    
    # Stats
    tt_vals = omega_tt[np.triu_indices(n_t, k=1)]
    tt_vals = tt_vals[~np.isnan(tt_vals)]
    nn_vals = omega_nn[np.triu_indices(n_n, k=1)]
    nn_vals = nn_vals[~np.isnan(nn_vals)]
    tn_vals = omega_tn.flatten()
    tn_vals = tn_vals[~np.isnan(tn_vals)]
    
    baseline = (np.nanmean(tt_vals) + np.nanmean(nn_vals)) / 2
    from scipy.stats import mannwhitneyu
    combined = np.concatenate([tt_vals, nn_vals])
    # Fixed: TN < baseline (tumors more homogeneous), use alternative="less"
    _, p_val = mannwhitneyu(tn_vals, combined, alternative="less") if len(combined) > 0 else (0, 1.0)
    
    print(f"    omega_TT: mean={np.nanmean(tt_vals):.1f}, median={np.nanmedian(tt_vals):.1f}, std={np.nanstd(tt_vals):.1f}")
    print(f"    omega_NN: mean={np.nanmean(nn_vals):.1f}, median={np.nanmedian(nn_vals):.1f}, std={np.nanstd(nn_vals):.1f}")
    print(f"    omega_TN: mean={np.nanmean(tn_vals):.1f}, median={np.nanmedian(tn_vals):.1f}, std={np.nanstd(tn_vals):.1f}")
    print(f"    TN/baseline: {np.nanmean(tn_vals)/baseline:.2f}x, p={p_val:.2e}")
    
    # Save per-cancer details
    df_details = pd.DataFrame(tt_details + nn_details + tn_details)
    df_details.to_csv(RESULTS_DIR / f"phase34_v2_{cancer}_pairs.csv", index=False)
    
    all_pair_details.append(df_details)
    
    all_summary.append({
        "Project": cancer,
        "n_Tumor": n_t,
        "n_Normal": n_n,
        "n_Genes": len(genes),
        "n_HK": len(hk_arr),
        "omega_TT_mean": f"{np.nanmean(tt_vals):.1f}",
        "omega_TT_median": f"{np.nanmedian(tt_vals):.1f}",
        "omega_NN_mean": f"{np.nanmean(nn_vals):.1f}",
        "omega_NN_median": f"{np.nanmedian(nn_vals):.1f}",
        "omega_TN_mean": f"{np.nanmean(tn_vals):.1f}",
        "omega_TN_median": f"{np.nanmedian(tn_vals):.1f}",
        "TN_Baseline": f"{np.nanmean(tn_vals)/baseline:.2f}x",
        "p_value": f"{p_val:.2e}",
        "time_s": f"{time.time()-t0_cancer:.0f}",
    })

# ====================================================================
# 4. Combined analysis (all pairs from all cancers)
# ====================================================================
print("\n" + "=" * 60)
print("4. Combined cross-cancer analysis...")
print("=" * 60)

df_all = pd.concat(all_pair_details, ignore_index=True)
print(f"  Total pairs: {len(df_all)}")

# Save combined
df_all.to_csv(RESULTS_DIR / "phase34_v2_all_pairs.csv", index=False)

# Summary
df_summary = pd.DataFrame(all_summary)
print("\n" + df_summary.to_string(index=False))
df_summary.to_csv(RESULTS_DIR / "phase34_v2_summary.csv", index=False)

# ====================================================================
# 5. Visualization
# ====================================================================
print("\n" + "=" * 60)
print("5. Visualization...")
print("=" * 60)

# 5a. Per-cancer boxplot
n_cancers = len(usable)
fig, axes = plt.subplots(1, n_cancers, figsize=(5*n_cancers, 5))
if n_cancers == 1:
    axes = [axes]

for ax, cancer in zip(axes, usable):
    sub = df_all[df_all["cancer"] == cancer]
    tt = sub[sub["pair_type"] == "TT"]["omega"].dropna()
    nn = sub[sub["pair_type"] == "NN"]["omega"].dropna()
    tn = sub[sub["pair_type"] == "TN"]["omega"].dropna()
    
    data = [tt.values, nn.values, tn.values]
    labels = ["Tumor-Tumor", "Normal-Normal", "Tumor-Normal"]
    colors = ["#E74C3C", "#2ECC71", "#8E44AD"]
    
    bp = ax.boxplot(data, labels=labels, patch_artist=True, widths=0.5)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    n_t = len(proj_tumor[cancer])
    n_n = len(proj_normal[cancer])
    ax.set_title(f"{cancer}\n(T={n_t}, N={n_n})", fontsize=10, fontweight="bold")
    ax.set_ylabel("Omega")
    ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase34_v2_boxplot_per_project.png", dpi=150, bbox_inches="tight")
plt.close()

# 5b. Cross-cancer bar chart
fig, ax = plt.subplots(figsize=(12, 6))
projects = usable
x = np.arange(len(projects))
width = 0.25

tt_means, nn_means, tn_means = [], [], []
for p in projects:
    sub = df_all[df_all["cancer"] == p]
    tt_means.append(sub[sub["pair_type"] == "TT"]["omega"].mean())
    nn_means.append(sub[sub["pair_type"] == "NN"]["omega"].mean())
    tn_means.append(sub[sub["pair_type"] == "TN"]["omega"].mean())

ax.bar(x - width, tt_means, width, label="Tumor-Tumor", color="#E74C3C", alpha=0.7)
ax.bar(x, nn_means, width, label="Normal-Normal", color="#2ECC71", alpha=0.7)
ax.bar(x + width, tn_means, width, label="Tumor-Normal", color="#8E44AD", alpha=0.7)

for i in range(len(projects)):
    for vals, dx in [(tt_means, -width), (nn_means, 0), (tn_means, +width)]:
        ax.text(x[i] + dx, vals[i] + 2, f"{vals[i]:.0f}", ha="center", va="bottom", fontsize=7)

ax.set_xticks(x)
ax.set_xticklabels(projects, fontsize=10)
ax.set_ylabel("Mean Omega", fontsize=12)
ax.set_title("CKI Omega: Tumor vs Normal Perturbation (TCGA, v2 per-cancer)", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase34_v2_cross_project_bar.png", dpi=150, bbox_inches="tight")
plt.close()

# 5c. Effect size
fig, ax = plt.subplots(figsize=(10, 5))
effects = []
for p in projects:
    sub = df_all[df_all["cancer"] == p]
    tt = sub[sub["pair_type"] == "TT"]["omega"].mean()
    nn = sub[sub["pair_type"] == "NN"]["omega"].mean()
    tn = sub[sub["pair_type"] == "TN"]["omega"].mean()
    baseline = (tt + nn) / 2
    effects.append(tn / baseline if baseline > 0 else 0)

colors_eff = ["#E74C3C" if e > 2 else "#F39C12" if e > 1 else "#95A5A6" for e in effects]
bars = ax.bar(projects, effects, color=colors_eff, alpha=0.7)
for bar, e in zip(bars, effects):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{e:.2f}x",
            ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.axhline(y=1.0, color="gray", linestyle="--", label="Baseline (no perturbation)")
ax.set_ylabel("TN / Baseline Ratio", fontsize=12)
ax.set_title("Tumor Perturbation Effect Size (omega_TN / omega_self)", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase34_v2_effect_size.png", dpi=150, bbox_inches="tight")
plt.close()

# 5d. Combined density across all cancers
fig, ax = plt.subplots(figsize=(10, 5))
for pair_type, color, label in [("TT", "#E74C3C", "Tumor-Tumor"), ("NN", "#2ECC71", "Normal-Normal"), ("TN", "#8E44AD", "Tumor-Normal")]:
    vals = df_all[df_all["pair_type"] == pair_type]["omega"].dropna()
    if len(vals) > 0:
        ax.hist(vals, bins=40, alpha=0.4, color=color, label=label, density=True)

ax.set_xlabel("Omega", fontsize=12)
ax.set_ylabel("Density", fontsize=12)
ax.set_title("CKI Omega Distribution: All TCGA Cancer Types Combined", fontsize=13, fontweight="bold")
ax.legend(fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "phase34_v2_combined_histogram.png", dpi=150, bbox_inches="tight")
plt.close()

print("  All plots saved.")

# ====================================================================
# 6. Report
# ====================================================================
print("\n" + "=" * 60)
print("6. Generating report...")
print("=" * 60)

elapsed = time.time() - t0_total

report = f"""# CKI Phase 3.4 v2 Report: TCGA Tumor Perturbation (Per-Cancer Loading)

## Key Fix
- v1 (failed): Global gene filtering across all 5 cancers diluted per-cancer signal, omega ≈ 0
- v2: Each cancer type loaded and filtered independently, preserving cancer-specific expression patterns

## Overview
- Data: UCSC Xena TCGA RSEM gene TPM (pan-cancer bulk RNA-seq)
- Method: Phase 3.3 v3 hybrid omega (global k_n + per-pair k_f, n={N_TOP_KF})
- Normalization: log2(TPM + 0.001)
- Analysis time: {elapsed:.0f}s

## Summary
{df_summary.to_string(index=False)}

## Interpretation
- TN/Baseline > 1: tumor transcriptomes are more divergent from normals than self-pairs
- CKI omega detects tumor perturbation via elevated k_f relative to stable k_n
- A ratio >>1 supports CKI's ability to detect transcriptional perturbation in bulk tumor RNA-seq

## Files
- phase34_v2_summary.csv: per-cancer summary
- phase34_v2_all_pairs.csv: all pair-level omega/kn/kf
- phase34_v2_<Cancer>_pairs.csv: per-cancer pair details
- phase34_v2_boxplot_per_project.png
- phase34_v2_cross_project_bar.png
- phase34_v2_effect_size.png
- phase34_v2_combined_histogram.png
"""

with open(RESULTS_DIR / "phase34_v2_report.md", "w", encoding="utf-8") as f:
    f.write(report.strip())

print("  Saved: phase34_v2_report.md")
print(f"\nPhase 3.4 v2 complete in {elapsed:.0f}s")
print("Done!")
