"""
CKI Phase 3.2: Multi-component k_f Calibration
====================================================
Extend k_f with Delta_pathway (ssGSEA). Sweep w1/w2 weights. — direct omega computation for scalability.
then sweep w1/w2 weights to calibrate multi-component k_f.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import scanpy as sc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list
from scipy.spatial.distance import squareform

# CJK font setup
_cjk_fonts = [f for f in fm.findSystemFonts() if "msyh" in f.lower() or "microsoft yahei" in f.lower() or "simhei" in f.lower()]
if _cjk_fonts:
    _cjk_prop = fm.FontProperties(fname=_cjk_fonts[0])
    plt.rcParams["font.family"] = _cjk_prop.get_name()
else:
    plt.rcParams["font.family"] = "sans-serif"

from cki.core import compute_omega

# -- Config --
DATA_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data")
FACS_DIR = DATA_DIR / "FACS" / "FACS"
HK_FILE  = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"
ANNOT_FILE = DATA_DIR / "annotations_FACS.csv"
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
RESULTS_DIR.mkdir(exist_ok=True)

TARGET_TISSUES = ["Liver", "Kidney", "Spleen", "Lung", "Heart", "Marrow"]
RANDOM_SEED = 42
MIN_CELLS_PER_CT = 10

def extract_mouse_id(cell_name):
    parts = cell_name.split(".")
    for p in parts:
        if "_" in p and (p.endswith("_M") or p.endswith("_F")):
            return p
    return "unknown"

# -- 1. Load Data --
print("="*60)
print("1. Loading data...")
print("="*60)

hk_df = pd.read_csv(HK_FILE, sep=None, engine="python")
hk_mouse_genes = set(hk_df.iloc[:, 0].tolist())
print(f"  HK genes: {len(hk_mouse_genes)}")

annot = pd.read_csv(ANNOT_FILE)
annot = annot[annot["tissue"].isin(TARGET_TISSUES)]
annot["mouse.id"] = annot["cell"].apply(extract_mouse_id)
print(f"  Annotations: {len(annot)} cells")

adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f"{tissue}-counts.csv"
    if not fname.exists(): continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())

# -- 2. Unified AnnData --
print("\n" + "="*60)
print("2. Building unified AnnData...")
print("="*60)

common_genes = sorted(all_genes.copy())
for tissue, df in adatas.items():
    common_genes = [g for g in common_genes if g in df.index]
print(f"  Common genes: {len(common_genes)}")

expr_parts, obs_parts = [], []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
    expr_parts.append(df_aligned.values)
    tissue_annot = annot[annot["tissue"] == tissue].copy()
    cell_ids = df_aligned.index.tolist()
    obs_tissue = pd.DataFrame({"cell": cell_ids, "tissue": tissue})
    obs_tissue = obs_tissue.merge(tissue_annot[["cell","cell_ontology_class","mouse.id"]], on="cell", how="left")
    obs_tissue["cell_ontology_class"] = obs_tissue["cell_ontology_class"].fillna("unknown")
    obs_tissue.set_index("cell", inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({"gene": common_genes}).set_index("gene")
adata = sc.AnnData(X=X, obs=obs, var=var)
print(f"  Unified: {adata.n_obs} cells x {adata.n_vars} genes")

# -- 3. Preprocessing --
print("\n" + "="*60)
print("3. Preprocessing...")
print("="*60)

sc.pp.filter_cells(adata, min_genes=500)
sc.pp.filter_genes(adata, min_cells=3)
print(f"  After QC: {adata.n_obs} x {adata.n_vars}")

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat")
print(f"  HVGs: {adata.var['highly_variable'].sum()}")

# -- 4. Gene Indices --
gene_names = adata.var_names.tolist()
hk_indices = [i for i,g in enumerate(gene_names) if g in hk_mouse_genes]
identity_indices = np.where(adata.var["highly_variable"].values)[0].tolist()
print(f"  HK: {len(hk_indices)}, Identity: {len(identity_indices)}")

# -- 5. Build CT pseudobulk dict --
print("\n" + "="*60)
print("5. Building CT pseudobulk (largest mouse group)...")
print("="*60)

ct_entries = []  # list of {key, tissue, ct, pb, n_cells}
for tissue in TARGET_TISSUES:
    tdata = adata[adata.obs["tissue"] == tissue]
    for ct in tdata.obs["cell_ontology_class"].unique():
        if ct.lower() == "unknown": continue
        ct_mask = tdata.obs["cell_ontology_class"] == ct
        ct_data = tdata[ct_mask]
        if ct_data.n_obs < MIN_CELLS_PER_CT * 2: continue
        mouse_counts = ct_data.obs["mouse.id"].value_counts()
        mice_ok = [(m,n) for m,n in mouse_counts.items() if n >= MIN_CELLS_PER_CT]
        if len(mice_ok) < 1: continue
        mice_ok.sort(key=lambda x: -x[1])
        largest_mouse = mice_ok[0][0]
        mask_largest = ct_data.obs["mouse.id"] == largest_mouse
        X_large = ct_data[mask_largest].X
        if hasattr(X_large, "toarray"): X_large = X_large.toarray()
        if X_large.shape[0] < MIN_CELLS_PER_CT: continue
        pb = np.mean(X_large, axis=0)
        ct_entries.append({
            "key": f"{tissue}|{ct}",
            "tissue": tissue,
            "ct": ct,
            "pb": pb,
            "n_cells": X_large.shape[0],
        })

print(f"  Viable CT entries: {len(ct_entries)}")
for e in ct_entries:
    print(f"    {e['key']} (n={e['n_cells']})")

# -- 6. Compute all pairwise omega --
print("\n" + "="*60)
print("6. Computing all pairwise omega...")
print("="*60)

n_ct = len(ct_entries)
omega_matrix = np.zeros((n_ct, n_ct))
kn_matrix = np.zeros((n_ct, n_ct))
kf_matrix = np.zeros((n_ct, n_ct))
dhk_matrix = np.zeros((n_ct, n_ct))
did_matrix = np.zeros((n_ct, n_ct))

from tqdm import tqdm
total_pairs = n_ct * (n_ct - 1) // 2
print(f"  Total pairs: {total_pairs}")

pair_count = 0
for i in tqdm(range(n_ct), desc="Rows"):
    for j in range(i+1, n_ct):
        result = compute_omega(ct_entries[i]["pb"], ct_entries[j]["pb"],
                               hk_indices, identity_indices)
        omega_matrix[i,j] = result["omega"]
        omega_matrix[j,i] = result["omega"]
        kn_matrix[i,j] = result["kn"]
        kn_matrix[j,i] = result["kn"]
        kf_matrix[i,j] = result["kf"]
        kf_matrix[j,i] = result["kf"]
        dhk_matrix[i,j] = result["delta_hk"]
        dhk_matrix[j,i] = result["delta_hk"]
        did_matrix[i,j] = result["delta_identity"]
        did_matrix[j,i] = result["delta_identity"]
        pair_count += 1

# Diagonal: zero (self-comparison)
np.fill_diagonal(omega_matrix, 0)
np.fill_diagonal(kn_matrix, 0)
np.fill_diagonal(kf_matrix, 0)

print(f"\n  Computed {pair_count} pairs")

# -- 7. Build labels --
labels = []
for e in ct_entries:
    ct_short = e["ct"].replace("endothelial cell of hepatic sinusoid", "liver sinusoid EC")
    ct_short = ct_short.replace("cardiac muscle cell", "cardiac muscle")
    ct_short = ct_short.replace("natural killer cell", "NK cell")
    if len(ct_short) > 18:
        ct_short = ct_short[:16] + ".."
    labels.append(f"{e['tissue'][:4]}|{ct_short}")

# -- 8. Save matrices --
print("\n" + "="*60)
print("8. Saving matrices...")
print("="*60)

omega_df = pd.DataFrame(omega_matrix, index=labels, columns=labels)
omega_df.to_csv(RESULTS_DIR / "full_matrix_omega.csv")
print("  Saved: full_matrix_omega.csv")

kn_df = pd.DataFrame(kn_matrix, index=labels, columns=labels)
kn_df.to_csv(RESULTS_DIR / "full_matrix_kn.csv")
print("  Saved: full_matrix_kn.csv")

kf_df = pd.DataFrame(kf_matrix, index=labels, columns=labels)
kf_df.to_csv(RESULTS_DIR / "full_matrix_kf.csv")
print("  Saved: full_matrix_kf.csv")

# -- 9. Summary statistics --
print("\n" + "="*60)
print("9. Summary Statistics")
print("="*60)

upper_tri = omega_matrix[np.triu_indices(n_ct, k=1)]
print(f"  Omega range: [{np.min(upper_tri):.2f}, {np.max(upper_tri):.2f}]")
print(f"  Omega mean: {np.mean(upper_tri):.2f}")
print(f"  Omega median: {np.median(upper_tri):.2f}")
print(f"  Omega std: {np.std(upper_tri):.2f}")

# By category: same tissue, same CT (broad class)
same_tissue_mask = np.zeros((n_ct,n_ct), dtype=bool)
same_ct_class = np.zeros((n_ct,n_ct), dtype=bool)
for i in range(n_ct):
    for j in range(n_ct):
        if i >= j: continue
        same_tissue_mask[i,j] = ct_entries[i]["tissue"] == ct_entries[j]["tissue"]
        same_ct_class[i,j] = ct_entries[i]["ct"] == ct_entries[j]["ct"]

same_tissue = upper_tri[same_tissue_mask[np.triu_indices(n_ct,k=1)]]
diff_tissue = upper_tri[~same_tissue_mask[np.triu_indices(n_ct,k=1)]]
same_ct = upper_tri[same_ct_class[np.triu_indices(n_ct,k=1)]]
diff_ct = upper_tri[~same_ct_class[np.triu_indices(n_ct,k=1)]]

print(f"\n  Same tissue (n={len(same_tissue)}): mean={np.mean(same_tissue):.2f}, median={np.median(same_tissue):.2f}")
print(f"  Diff tissue (n={len(diff_tissue)}): mean={np.mean(diff_tissue):.2f}, median={np.median(diff_tissue):.2f}")
print(f"  Same CT class (n={len(same_ct)}): mean={np.mean(same_ct):.2f}, median={np.median(same_ct):.2f}")
print(f"  Diff CT class (n={len(diff_ct)}): mean={np.mean(diff_ct):.2f}, median={np.median(diff_ct):.2f}")

# -- 10. Heatmap with clustering --
print("\n" + "="*60)
print("10. Generating heatmap...")
print("="*60)

# Hierarchical clustering
condensed_dist = squareform(upper_tri, checks=False)
# Use 1/omega or omega for distance? Higher omega = more different, so use omega as distance
linkage_matrix = linkage(condensed_dist, method="ward")
leaf_order = leaves_list(linkage_matrix)

# Reorder matrix
omega_clustered = omega_matrix[leaf_order][:, leaf_order]
labels_clustered = [labels[i] for i in leaf_order]

fig, ax = plt.subplots(figsize=(18, 15))
im = ax.imshow(omega_clustered, cmap="RdYlBu_r", aspect="equal", vmin=0, vmax=max(30, np.max(upper_tri)*1.1))

ax.set_xticks(range(n_ct))
ax.set_yticks(range(n_ct))
ax.set_xticklabels(labels_clustered, rotation=90, ha="center", fontsize=6)
ax.set_yticklabels(labels_clustered, fontsize=6)
ax.set_title("CKI Phase 3.1: Full Matrix Pairwise Omega (32 CT Pairs)", fontsize=14, fontweight="bold", pad=20)

cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
cbar.set_label("omega", fontsize=11)

# Annotate with omega values (small font)
for i in range(n_ct):
    for j in range(n_ct):
        val = omega_clustered[i,j]
        if val > 0:
            ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=4,
                    color="white" if val > np.percentile(upper_tri, 70) else "black")

plt.tight_layout()
fig.savefig(RESULTS_DIR / "full_matrix_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: full_matrix_heatmap.png")

# -- 11. Dendrogram only --
fig, ax = plt.subplots(figsize=(20, 5))
dn = dendrogram(linkage_matrix, labels=labels, ax=ax, leaf_font_size=7,
                color_threshold=np.percentile(linkage_matrix[:,2], 60))
ax.set_title("CKI omega-based Hierarchical Clustering of Cell Types", fontsize=13, fontweight="bold")
ax.set_ylabel("Omega distance (Ward linkage)", fontsize=10)
plt.tight_layout()
fig.savefig(RESULTS_DIR / "full_matrix_dendrogram.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: full_matrix_dendrogram.png")

# -- 12. Top/bottom pairs --
print("\n" + "="*60)
print("12. Top 15 Most Differentiated Pairs")
print("="*60)

pairs_list = []
for i in range(n_ct):
    for j in range(i+1, n_ct):
        pairs_list.append({
            "pair": f"{labels[i]} vs {labels[j]}",
            "omega": omega_matrix[i,j],
            "kn": kn_matrix[i,j],
            "kf": kf_matrix[i,j],
            "same_tissue": ct_entries[i]["tissue"] == ct_entries[j]["tissue"],
            "same_ct": ct_entries[i]["ct"] == ct_entries[j]["ct"],
        })

pairs_df = pd.DataFrame(pairs_list)
pairs_df = pairs_df.sort_values("omega", ascending=False)

print("\n  Top 15 (highest omega = most differentiated):")
for _, row in pairs_df.head(15).iterrows():
    st = " (same tissue)" if row["same_tissue"] else ""
    sct = " (same CT)" if row["same_ct"] else ""
    print(f"    {row['pair']}: omega={row['omega']:.2f}, kn={row['kn']:.5f}, kf={row['kf']:.5f}{st}{sct}")

print("\n  Bottom 15 (lowest omega = most similar):")
for _, row in pairs_df.tail(15).iterrows():
    st = " (same tissue)" if row["same_tissue"] else ""
    sct = " (same CT)" if row["same_ct"] else ""
    print(f"    {row['pair']}: omega={row['omega']:.2f}, kn={row['kn']:.5f}, kf={row['kf']:.5f}{st}{sct}")

pairs_df.to_csv(RESULTS_DIR / "full_matrix_pairs.csv", index=False)
print("  Saved: full_matrix_pairs.csv")

# -- 13. Category boxplot --
print("\n" + "="*60)
print("13. Generating category boxplot...")
print("="*60)

# Define four categories based on same/different tissue and CT
cat_data = {"same_tissue+same_ct": [], "same_tissue+diff_ct": [],
            "diff_tissue+same_ct": [], "diff_tissue+diff_ct": []}

for _, row in pairs_df.iterrows():
    if row["same_tissue"] and row["same_ct"]:
        cat_data["same_tissue+same_ct"].append(row["omega"])
    elif row["same_tissue"] and not row["same_ct"]:
        cat_data["same_tissue+diff_ct"].append(row["omega"])
    elif not row["same_tissue"] and row["same_ct"]:
        cat_data["diff_tissue+same_ct"].append(row["omega"])
    else:
        cat_data["diff_tissue+diff_ct"].append(row["omega"])

cat_names = ["SameTissue\nSameCT", "SameTissue\nDiffCT", "DiffTissue\nSameCT", "DiffTissue\nDiffCT"]
cat_colors = ["#059669", "#E67E22", "#D4AF37", "#C0392B"]
cat_data_values = [np.array(cat_data["same_tissue+same_ct"]),
                   np.array(cat_data["same_tissue+diff_ct"]),
                   np.array(cat_data["diff_tissue+same_ct"]),
                   np.array(cat_data["diff_tissue+diff_ct"])]

fig, ax = plt.subplots(figsize=(8, 5))
bp = ax.boxplot(cat_data_values, labels=cat_names, patch_artist=True, widths=0.5)
for i in range(4):
    bp["boxes"][i].set_facecolor(cat_colors[i])
    jitter = np.random.RandomState(RANDOM_SEED).normal(0, 0.03, len(cat_data_values[i]))
    ax.scatter(np.ones(len(cat_data_values[i]))*(i+1) + jitter, cat_data_values[i],
               color="#1E3A5F", s=15, alpha=0.4, zorder=3)

ax.set_ylabel("omega", fontsize=12)
ax.set_title(f"Full Matrix: omega by Tissue/CT Category\n(n_total={len(pairs_df)})", fontsize=13, fontweight="bold")
for i, vals in enumerate(cat_data_values):
    if len(vals) > 0:
        ax.annotate(f"n={len(vals)}\nmean={np.mean(vals):.1f}", (i+1, np.max(vals)*1.02),
                    ha="center", fontsize=7, color="#333")

plt.tight_layout()
fig.savefig(RESULTS_DIR / "full_matrix_category_boxplot.png", dpi=150)
plt.close()
print("  Saved: full_matrix_category_boxplot.png")

print("\n" + "="*60)
print("DONE. Phase 3.1 complete.")
print("="*60)

# ================================================================
# Phase 3.2: ssGSEA pathway scores + weight sweep
# ================================================================

print('\n' + '='*60)
print('Phase 3.2: Multi-component k_f Calibration')
print('='*60)

import gseapy as gsp
import warnings as _w
_w.filterwarnings('ignore')

# -- Load MSigDB Hallmark --
print('\n  Loading MSigDB Hallmark...')
try:
    gmt_path = gsp.utils.download_library('H', 'Mouse', save_dir=None)
    pw_dict = gsp.gmt_parser(gmt_path)
    pw_source = f'MSigDB Hallmark ({len(pw_dict)} pathways)'
    print(f'  Loaded {len(pw_dict)} Hallmark pathways')
except Exception as e:
    print(f'  [MSigDB failed: {e}]')
    print('  Fallback: pseudo-pathways from HVG partitions')
    hvg_idx = np.where(adata.var['highly_variable'].values)[0]
    np.random.shuffle(hvg_idx)
    K = 20
    chunk = max(1, len(hvg_idx) // K)
    pw_dict = {}
    gn = adata.var_names.tolist()
    for k in range(K):
        s = k * chunk
        e = (k+1)*chunk if k < K-1 else len(hvg_idx)
        pw_dict[f'pseudo_{k}'] = [gn[i] for i in hvg_idx[s:e]]
    pw_source = f'Pseudo-pathways (HVG partitions, {len(pw_dict)} modules)'
    print(f'  Using {len(pw_dict)} pseudo-pathways')

# -- Build pb DataFrame for ssGSEA --
print('\n  Building pb DataFrame for ssGSEA...')
pb_matrix = np.vstack([e['pb'] for e in ct_entries])
pb_df = pd.DataFrame(
    pb_matrix,
    index=[e['key'] for e in ct_entries],
    columns=adata.var_names.tolist()
).T
print(f'  ssGSEA input: {pb_df.shape}')

# -- Custom ssGSEA fallback --
def _custom_ssgsea(pb_df, pw_dict):
    n_pw = len(pw_dict)
    pw_items = list(pw_dict.items())
    gene_names = pb_df.index.tolist()
    result = {}
    for col_name in pb_df.columns:
        pb = pb_df[col_name].values
        n = len(pb)
        order = np.argsort(pb)[::-1]
        scores = np.zeros(n_pw)
        for pw_idx, (pw_name, pw_genes) in enumerate(pw_items):
            pw_set = set(i for i, g in enumerate(gene_names) if g in pw_genes)
            if len(pw_set) < 5:
                scores[pw_idx] = 0.0
                continue
            Nh = len(pw_set)
            step_hit = (n - Nh) / (Nh + 1e-9)
            step_miss = -1.0
            rs = 0.0
            mx = 0.0
            for i in order:
                if i in pw_set:
                    rs += step_hit
                else:
                    rs += step_miss
                if abs(rs) > mx:
                    mx = abs(rs)
            scores[pw_idx] = mx / ((n - Nh) + 1e-9)
        mn, mx = scores.min(), scores.max()
        if mx > mn:
            scores = (scores - mn) / (mx - mn + 1e-9)
        result[col_name] = scores
    return result

# -- Run ssGSEA via gseapy --
print('\n  Running ssGSEA (gseapy)...')
try:
    ssgsea_res = gsp.ssgsea(
        data=pb_df, gene_sets=pw_dict,
        sample_norm='rank', permutation_num=0,
        no_plot=True, processes=1, verbose=False
    )
    pw_names = ssgsea_res.results_df.index.tolist()
    pathway_vecs = {}
    for idx, e in enumerate(ct_entries):
        pathway_vecs[e['key']] = ssgsea_res.results_df.iloc[:, idx].values
    print(f'  ssGSEA done: {len(pw_names)} pathways x {len(ct_entries)} CTs')
except Exception as e:
    print(f'  [ssGSEA failed: {e}]')
    print('  Falling back to custom ssGSEA...')
    pathway_vecs = _custom_ssgsea(pb_df, pw_dict)
    pw_names = list(pw_dict.keys())

# -- Save pathway scores --
pw_df_out = pd.DataFrame(pathway_vecs).T
pw_df_out.to_csv(RESULTS_DIR / 'phase32_pathway_scores.csv')
print(f'  Saved pathway scores: {pw_df_out.shape}')

# -- Weight sweep --
print('\n' + '='*60)
print('Weight Sweep: w1 (identity) + w2 (pathway)')
print('='*60)

sweep_configs = [
    (1.0, 0.0, 'identity_only'),
    (0.8, 0.2, 'w1=0.8_w2=0.2'),
    (0.5, 0.5, 'w1=0.5_w2=0.5'),
    (0.2, 0.8, 'w1=0.2_w2=0.8'),
    (0.0, 1.0, 'pathway_only'),
]

from tqdm import tqdm
from sklearn.metrics import roc_auc_score
from scipy.stats import mannwhitneyu

def run_sweep(w1, w2, label):
    print(f'\n  Sweep: {label} (w1={w1}, w2={w2})')
    omega_m = np.zeros((n_ct, n_ct))
    kn_m   = np.zeros((n_ct, n_ct))
    kf_m   = np.zeros((n_ct, n_ct))
    for i in range(n_ct):
        pb_i = ct_entries[i]['pb']
        pw_i = pathway_vecs.get(ct_entries[i]['key'])
        for j in range(i+1, n_ct):
            pb_j = ct_entries[j]['pb']
            pw_j = pathway_vecs.get(ct_entries[j]['key'])
            res = compute_omega(
                pb_i, pb_j,
                hk_indices, identity_indices,
                pathway_a=pw_i, pathway_b=pw_j,
                alpha=1.0, w1=w1, w2=w2
            )
            omega_m[i,j] = res['omega']
            omega_m[j,i] = res['omega']
            kn_m[i,j]   = res['kn']
            kn_m[j,i]   = res['kn']
            kf_m[i,j]   = res['kf']
            kf_m[j,i]   = res['kf']
    np.fill_diagonal(omega_m, 0.0)

    # Category evaluation
    y_true, y_score = [], []
    for i in range(n_ct):
        for j in range(i+1, n_ct):
            y_true.append(1 if ct_entries[i]['ct'] == ct_entries[j]['ct'] else 0)
            y_score.append(omega_m[i,j])
    auc = roc_auc_score(y_true, [-s for s in y_score])

    same_vals = [omega_m[i,j] for i in range(n_ct) for j in range(i+1,n_ct)
                   if ct_entries[i]['ct'] == ct_entries[j]['ct']]
    diff_vals = [omega_m[i,j] for i in range(n_ct) for j in range(i+1,n_ct)
                   if ct_entries[i]['ct'] != ct_entries[j]['ct']]
    if len(same_vals) > 0 and len(diff_vals) > 0:
        u_stat, p_val = mannwhitneyu(same_vals, diff_vals, alternative='less')
        effect_sep = np.mean(diff_vals) / (np.mean(same_vals) + 1e-9)
    else:
        u_stat, p_val, effect_sep = 0, 1.0, 1.0

    utri = omega_m[np.triu_indices(n_ct, k=1)]
    return {
        'label': label, 'w1': w1, 'w2': w2,
        'auc': auc, 'u_stat': u_stat, 'p_val': p_val,
        'effect_sep': effect_sep,
        'omega_mean': float(np.mean(utri)),
        'omega_median': float(np.median(utri)),
        'omega_matrix': omega_m.copy(),
    }

sweep_results = []
for w1, w2, label in sweep_configs:
    r = run_sweep(w1, w2, label)
    sweep_results.append(r)
    print(f'    AUC={r["auc"]:.3f}  effect_sep={r["effect_sep"]:.2f}')

# -- Save sweep results --
sweep_df = pd.DataFrame([
    {k: v for k, v in r.items() if k != 'omega_matrix'}
    for r in sweep_results
])
sweep_df.to_csv(RESULTS_DIR / 'phase32_sweep_results.csv', index=False)
print('\n  Sweep summary:')
print(sweep_df[['label','w1','w2','auc','effect_sep','omega_mean','omega_median']].to_string(index=False))

# -- Find best weight --
best_idx = int(np.argmax([r['auc'] for r in sweep_results]))
best = sweep_results[best_idx]
print(f'\n  Best: {best["label"]} (AUC={best["auc"]:.3f})')

# -- Plots: heatmap comparison --
print('\n  Generating heatmap comparison...')
_cjk2 = [f for f in fm.findSystemFonts() if 'msyh' in f.lower() or 'microsoft yahei' in f.lower()]
if _cjk2:
    plt.rcParams['font.family'] = fm.FontProperties(fname=_cjk2[0]).get_name()

om_single = sweep_results[0]['omega_matrix']
om_best   = best['omega_matrix']

labels_viz = []
for e in ct_entries:
    cs = e['ct'].replace('endothelial cell of hepatic sinusoid', 'livEC')
    cs = cs.replace('cardiac muscle cell', 'cardio')
    cs = cs.replace('natural killer cell', 'NK')
    if len(cs) > 12:
        cs = cs[:10] + '..'
    labels_viz.append(f'{e["tissue"][:4]}|{cs}')

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 10))
vmax = max(30, float(np.nanmax(om_single)) * 1.1)
for ax, om, title in [(ax1, om_single, '(a) Single-component (k_f = Delta_identity only)'),
                        (ax2, om_best,   f'(b) Best: {best["label"]}')]:
    im = ax.imshow(om, cmap='RdYlBu_r', aspect='equal', vmin=0, vmax=vmax)
    ax.set_xticks(range(n_ct))
    ax.set_yticks(range(n_ct))
    ax.set_xticklabels(labels_viz, rotation=90, ha='center', fontsize=5)
    ax.set_yticklabels(labels_viz, fontsize=5)
    ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
    plt.colorbar(im, ax=ax, shrink=0.6, pad=0.02)
plt.suptitle('CKI Phase 3.2: Omega Heatmap Comparison', fontsize=14, fontweight='bold')
plt.tight_layout()
fig.savefig(RESULTS_DIR / 'phase32_heatmap_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: phase32_heatmap_comparison.png')

# -- Category boxplot comparison --
print('  Generating category boxplot comparison...')
cat_colors = ['#059669', '#D4AF37', '#1E3A5F', '#C0392B']
cat_names  = ['SameTissue\nSameCT', 'SameTissue\nDiffCT',
              'DiffTissue\nSameCT', 'DiffTissue\nDiffCT']

def _cat_data(om):
    cd = {'sts': [], 'std': [], 'dts': [], 'dtd': []}
    for i in range(n_ct):
        for j in range(i+1, n_ct):
            st = ct_entries[i]['tissue'] == ct_entries[j]['tissue']
            sc = ct_entries[i]['ct'] == ct_entries[j]['ct']
            if st and sc:
                cd['sts'].append(om[i,j])
            elif st and not sc:
                cd['std'].append(om[i,j])
            elif not st and sc:
                cd['dts'].append(om[i,j])
            else:
                cd['dtd'].append(om[i,j])
    return cd

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
np.random.seed(RANDOM_SEED)
for ax, om, title in [(ax1, om_single, 'Single-component'),
                        (ax2, om_best,   f'Best: {best["label"]}')]:
    cd   = _cat_data(om)
    vals = [np.array(cd['sts']), np.array(cd['std']),
            np.array(cd['dts']), np.array(cd['dtd'])]
    bp = ax.boxplot(vals, labels=cat_names, patch_artist=True, widths=0.5)
    for i in range(4):
        bp['boxes'][i].set_facecolor(cat_colors[i])
        if len(vals[i]) > 0:
            jit = np.random.normal(0, 0.03, len(vals[i]))
            ax.scatter(np.ones(len(vals[i]))*(i+1) + jit, vals[i],
                       color='#1E3A5F', s=15, alpha=0.4, zorder=3)
            ax.annotate(f'n={len(vals[i])}\nmean={np.mean(vals[i]):.1f}',
                         (i+1, np.max(vals[i])*1.02),
                         ha='center', fontsize=7, color='#333')
    ax.set_ylabel('omega', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
plt.tight_layout()
fig.savefig(RESULTS_DIR / 'phase32_category_comparison.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: phase32_category_comparison.png')

# -- Sweep bar plot --
print('  Generating sweep bar plot...')
fig, ax1 = plt.subplots(figsize=(10, 5))
x = np.arange(len(sweep_df))
ax1.bar(x - 0.2, sweep_df['auc'], width=0.4,
         label='AUC (higher=better)', color='#1E3A5F', alpha=0.8)
ax1.set_ylabel('AUC', fontsize=11, color='#1E3A5F')
ax1.set_ylim([0.5, 1.0])
ax1.tick_params(axis='y', labelcolor='#1E3A5F')
ax2 = ax1.twinx()
ax2.bar(x + 0.2, sweep_df['effect_sep'], width=0.4,
         label='Effect Sep (ratio)', color='#D4AF37', alpha=0.8)
ax2.set_ylabel('Effect Sep (diffCT / sameCT)', fontsize=11, color='#D4AF37')
ax2.tick_params(axis='y', labelcolor='#D4AF37')
ax1.set_xticks(x)
xticklabels = [f'w1={r["w1"]:.1f}\nw2={r["w2"]:.1f}' for _, r in sweep_df.iterrows()]
ax1.set_xticklabels(xticklabels, fontsize=9)
ax1.set_xlabel('k_f weight (w1=Delta_identity, w2=Delta_pathway)', fontsize=11)
ax1.set_title('Phase 3.2: Weight Sweep - AUC & Category Separation',
               fontsize=13, fontweight='bold')
ax1.axhline(0.5, color='gray', linestyle='--', alpha=0.5)
plt.tight_layout()
fig.savefig(RESULTS_DIR / 'phase32_sweep_barplot.png', dpi=150, bbox_inches='tight')
plt.close()
print('  Saved: phase32_sweep_barplot.png')

# -- Report --
print('\n  Writing report...')
report_lines = [
    '# CKI Phase 3.2 Report: Multi-component k_f Calibration',
    '',
    f'## Date: {pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")}',
    '',
    '## Method',
    '```',
    'k_f = w1 * Delta_identity + w2 * Delta_pathway',
    'omega = k_f / k_n',
    '```',
    '- **Delta_identity**: JS divergence of HVG expression',
    '- **Delta_pathway**: JS divergence of ssGSEA pathway enrichment scores',
    f'- **Pathway database**: {pw_source}',
    '',
    '## Dataset',
    f'- **CT entries**: {n_ct}',
    f'- **Total pairs**: {n_ct*(n_ct-1)//2}',
    f'- **Gene space (post-QC)**: {adata.n_vars} genes',
    '',
    '## Weight Sweep Results',
    '',
    '| w1 | w2 | AUC | Effect_Sep | omega_mean | omega_median |',
    '|----|----|-----|------------|------------|---------------|',
]
for _, r in sweep_df.iterrows():
    report_lines.append(
        f'| {r["w1"]:.1f} | {r["w2"]:.1f} '
        f'| {r["auc"]:.3f} | {r["effect_sep"]:.2f} '
        f'| {r["omega_mean"]:.2f} | {r["omega_median"]:.2f} |'
    )
report_lines += [
    '',
    '## Conclusion',
    f'- **Best weight**: {best["label"]} (AUC={best["auc"]:.3f}, effect_sep={best["effect_sep"]:.2f})',
    f'- **Category separation** (diff_CT / same_CT mean omega): {best["effect_sep"]:.2f}',
    '',
]
if best['w2'] > 0:
    report_lines.append('Adding Delta_pathway **improves** CT discrimination.')
else:
    report_lines.append('Delta_identity alone is sufficient; Delta_pathway does not improve.')
report_lines += [
    '',
    '## Files Generated',
    '- `phase32_pathway_scores.csv`',
    '- `phase32_sweep_results.csv`',
    '- `phase32_heatmap_comparison.png`',
    '- `phase32_category_comparison.png`',
    '- `phase32_sweep_barplot.png`',
    '',
    '## Next Steps',
    '- Phase 3.3: Tabula Sapiens cross-species validation',
    '- Phase 3.4: TCGA tumor perturbation',
    '- Phase 3.5: Method comparison (SAMap / SATURN / CACIMAR)',
]
with open(RESULTS_DIR / 'phase32_report.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print('  Saved: phase32_report.md')

print('\n' + '='*60)
print('DONE. Phase 3.2 complete.')
print('='*60)
