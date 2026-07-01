"""
Fast Phase35 AUC: Use CKI package + 4 other metrics on Tabula Sapiens.
Unbuffered output for monitoring.
"""
import sys, os
os.environ['PYTHONUNBUFFERED'] = '1'

import scanpy as sc
import pandas as pd
import numpy as np
from scipy.spatial.distance import jensenshannon, cosine
from scipy.stats import spearmanr
from scipy.special import softmax
from sklearn.metrics import roc_auc_score
from pathlib import Path
import warnings, pickle
warnings.filterwarnings('ignore')

DATA_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\ts_human")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")
CACHE = RESULTS_DIR / "phase35_pseudobulk_cache.pkl"
TS_ORGANS = ["Bone_Marrow", "Heart", "Kidney", "Liver", "Lung", "Spleen"]
N_MARKER = 200
MIN_CELLS = 10

def log(msg):
    print(msg, flush=True)

def ensure_prob(x):
    x = np.asarray(x, dtype=np.float64)
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    s = np.sum(np.abs(x))
    if s < 1e-12:
        return np.ones(len(x)) / len(x)
    return softmax(x)

# Step 1: Load pseudobulks (or read from cache)
if CACHE.exists():
    log(f'Loading cached pseudobulks from {CACHE}')
    with open(CACHE, 'rb') as f:
        ct_entries = pickle.load(f)
    log(f'Loaded {len(ct_entries)} CT entries')
else:
    # Detect HK genes from Bone_Marrow only (fast)
    log('Loading Bone_Marrow for HK detection...')
    bm = sc.read_h5ad(DATA_DIR / 'TS_Bone_Marrow.h5ad')
    all_gene_names = list(bm.var_names)
    n_genes = len(all_gene_names)
    
    expr = bm.X.toarray() if hasattr(bm.X, 'toarray') else bm.X
    detection_rate = np.array((expr > 0).mean(axis=0)).flatten()
    means = np.array(expr.mean(axis=0)).flatten()
    means[means == 0] = 1e-10
    stds = np.array(np.std(expr, axis=0)).flatten()
    cv = stds / means
    cv_median = np.median(cv)
    hk_mask = (detection_rate > 0.9) & (cv < cv_median)
    hk_indices = np.where(hk_mask)[0]
    log(f'Detected {len(hk_indices)} HK genes from Bone_Marrow')
    del bm, expr
    
    # Load each organ, build pseudobulks
    ct_entries = []
    for organ in TS_ORGANS:
        fp = DATA_DIR / f'TS_{organ}.h5ad'
        log(f'Loading {organ}...')
        adata = sc.read_h5ad(fp)
        
        # Map to global gene order
        current_genes = list(adata.var_names)
        gene_mask = np.array([g in all_gene_names for g in current_genes])
        
        expr = adata.X.toarray() if hasattr(adata.X, 'toarray') else adata.X
        expr = expr[:, gene_mask]
        expr_genes = [g for g, m in zip(current_genes, gene_mask) if m]
        
        # Build gene index map
        gene_to_global = {g: all_gene_names.index(g) for g in expr_genes}
        
        ct_col = 'cell_ontology_class'
        for ct in adata.obs[ct_col].unique():
            mask = adata.obs[ct_col] == ct
            if mask.sum() < MIN_CELLS:
                continue
            pb_raw = expr[mask].mean(axis=0)
            
            # Map to full n_genes vector
            pb_full = np.zeros(n_genes)
            for j, g in enumerate(expr_genes):
                pb_full[gene_to_global[g]] = pb_raw[j]
            
            ct_entries.append({
                'name': f'{organ}|{ct}',
                'organ': organ,
                'ct': ct,
                'pb': pb_full,
            })
        del adata, expr
        log(f'  {organ}: added cell types, total now {len(ct_entries)}')
    
    log(f'Total CT entries: {len(ct_entries)}')
    
    # Save cache with hk_indices
    with open(CACHE, 'wb') as f:
        pickle.dump({'entries': ct_entries, 'hk_indices': hk_indices, 'n_genes': n_genes}, f)
    log(f'Cached to {CACHE}')

# Unpack cache
if isinstance(ct_entries, dict):
    hk_indices = ct_entries['hk_indices']
    n_genes = ct_entries['n_genes']
    ct_entries = ct_entries['entries']

n_ct = len(ct_entries)
total_pairs = n_ct * (n_ct - 1) // 2
log(f'CT entries: {n_ct}, Total pairs: {total_pairs}')

# Step 2: Compute marker gene sets
log('Computing marker gene sets...')
ct_marker_sets = []
for e in ct_entries:
    pb = e['pb']
    top_n = min(N_MARKER, n_genes)
    top_idx = np.argpartition(pb, -top_n)[-top_n:]
    top_idx = top_idx[np.argsort(pb[top_idx])[::-1]]
    ct_marker_sets.append(set(top_idx))

# Step 3: Compute all 5 metrics
log(f'Computing {total_pairs} pairwise metrics...')
results = []
batch_size = 50000
batch = []
for i in range(n_ct):
    if i % 10 == 0:
        log(f'  Progress: {i}/{n_ct}')
    for j in range(i + 1, n_ct):
        pb_i = ct_entries[i]['pb']
        pb_j = ct_entries[j]['pb']
        same_ct = ct_entries[i]['ct'] == ct_entries[j]['ct']
        
        # CKI omega
        hk_i = pb_i[hk_indices]
        hk_j = pb_j[hk_indices]
        pi_hk = ensure_prob(hk_i)
        pj_hk = ensure_prob(hk_j)
        kn = float(jensenshannon(pi_hk, pj_hk, base=2.0) ** 2)
        
        abs_diff = np.abs(pb_i - pb_j)
        non_hk = np.ones(n_genes, dtype=bool)
        non_hk[hk_indices] = False
        abs_diff_non_hk = abs_diff.copy()
        abs_diff_non_hk[hk_indices] = -1
        top_kf = min(N_MARKER, n_genes - len(hk_indices))
        kf_idx = np.argpartition(abs_diff_non_hk, -top_kf)[-top_kf:]
        kf_idx = kf_idx[np.argsort(abs_diff_non_hk[kf_idx])[::-1]]
        
        pi_func = ensure_prob(pb_i[kf_idx])
        pj_func = ensure_prob(pb_j[kf_idx])
        kf = float(jensenshannon(pi_func, pj_func, base=2.0) ** 2)
        omega = kf / kn if kn > 1e-12 else np.inf
        
        # Raw JS
        pi_all = ensure_prob(pb_i)
        pj_all = ensure_prob(pb_j)
        js_raw = float(jensenshannon(pi_all, pj_all, base=2.0) ** 2)
        
        # Spearman distance
        sp_r, _ = spearmanr(pb_i, pb_j)
        sp_dist = 1.0 - sp_r
        
        # Cosine distance
        cos_dist = float(cosine(pb_i, pb_j))
        
        # Marker Jaccard
        set_i = ct_marker_sets[i]
        set_j = ct_marker_sets[j]
        inter = len(set_i & set_j)
        union = len(set_i | set_j)
        jaccard_dist = 1.0 - (inter / union if union > 0 else 0)
        
        batch.append({
            'omega': omega, 'kn': kn, 'kf': kf,
            'js_raw': js_raw, 'spearman_dist': sp_dist,
            'cosine_dist': cos_dist, 'jaccard_dist': jaccard_dist,
            'same_ct': same_ct,
        })
        
        if len(batch) >= batch_size:
            results.extend(batch)
            batch = []
            log(f'  Computed {len(results)} pairs...')

if batch:
    results.extend(batch)

df = pd.DataFrame(results)
log(f'Computed {len(df)} pairs total')

# Step 4: AUC computation
log('\n=== ROC-AUC for same-CT classification ===')
y_true = df['same_ct'].astype(int)
auc_results = {}
for metric_name, col in [('CKI omega', 'omega'), ('Raw JS', 'js_raw'),
                          ('Spearman dist', 'spearman_dist'), ('Cosine dist', 'cosine_dist'),
                          ('Marker Jaccard', 'jaccard_dist')]:
    vals = df[col].values
    vals = np.where(np.isinf(vals), np.nan, vals)
    mask = ~np.isnan(vals)
    if mask.sum() < 2:
        log(f'  {metric_name:>20}: insufficient valid values')
        continue
    auc = roc_auc_score(y_true[mask], -vals[mask])
    auc_results[col] = auc
    log(f'  {metric_name:>20}: AUC = {auc:.4f}')

# Save
out_csv = RESULTS_DIR / 'phase35_minimal_metrics.csv'
df.to_csv(out_csv, index=False)
log(f'\nSaved: {out_csv}')
log('Done!')
