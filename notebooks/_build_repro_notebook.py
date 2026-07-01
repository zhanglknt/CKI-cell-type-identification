"""
Build CKI_Reproducibility.ipynb — one-time generator script.
Run: python _build_repro_notebook.py
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    'kernelspec': {
        'display_name': 'Python 3',
        'language': 'python',
        'name': 'python3'
    },
    'language_info': {
        'name': 'python',
        'version': '3.9.0'
    }
}

cells = []

def md(source):
    cells.append(nbf.v4.new_markdown_cell(source))

def code(source):
    cells.append(nbf.v4.new_code_cell(source))

# ==============================
# CELL 0: Title
# ==============================
md("""# CKI Complete Reproducibility Notebook

**CKI v0.3.0** — Genome Biology Submission

This notebook reproduces all four datasets analysed in the CKI manuscript:

| Part | Dataset | Species | Pairs | Runtime (est.) |
|------|---------|---------|-------|-----------------|
| 1 | Tabula Muris FACS | Mouse | 15 pilot + 703 full | 10-20 min |
| 2 | Tabula Sapiens | Human | 5,151 | 1-2 h |
| 3 | TCGA Pan-Cancer | Human | ~20,000 | 1-2 h |
| 4 | Siletti Brain Atlas | Human | 31,764 | 4-8 h |

**Requirements**: Python >= 3.9, >= 16 GB RAM (>= 32 GB for Part 4), CKI v0.3.0 installed.

**Data**: All expression matrices must be placed in the `data/` directory before running.
See the accompanying `README_STARTER_DATA.md` for download links and instructions.
""")

# ==============================
# CELL 1: Environment Setup
# ==============================
code(r"""# ── Environment Setup ─────────────────────────────────────────────
import sys, os, gc, time, gzip, warnings
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc_mod
from tqdm import tqdm

warnings.filterwarnings('ignore')

# ── Paths ────────────────────────────────────────────────────
PROJECT_DIR = Path.cwd()
DATA_DIR = PROJECT_DIR / 'data'
RESULTS_DIR = PROJECT_DIR / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ── Verify CKI installation ──────────────────────────────────
try:
    import cki
    from cki.core import js_divergence, compute_omega
    from cki.gene_sets import genes_to_indices
    print(f'CKI version: {cki.__version__}')
    print(f'CKI location: {cki.__file__}')
    assert cki.__version__ >= '0.3.0', f'Need CKI >= 0.3.0, got {cki.__version__}'
except ImportError:
    print('ERROR: CKI not installed!')
    print('  cd <project_dir> && pip install -e .')
    sys.exit(1)

# ── Global Parameters (matching reproducibility guide) ───────
RANDOM_SEED = 42
N_TOP_KF = 200          # top-N DE genes for per-pair k_f
MIN_CELLS_PER_CT = 10   # min cells per cell type (mouse/human)
N_BOOTSTRAP = 500       # bootstrap iterations (mouse pilot only)
EPSILON = 1e-9          # tiny epsilon for bootstrap null

np.random.seed(RANDOM_SEED)
print(f'Random seed: {RANDOM_SEED}')
print(f'Python: {sys.version}')
print(f'Project: {PROJECT_DIR}')
""")

# ==============================
# PART 1: Tabula Muris (Mouse)
# ==============================
md("""---
# Part 1: Tabula Muris (Mouse FACS)

**Dataset**: Tabula Muris FACS SmartSeq2 (Schaum et al., Nature 2018)  
**Input**: Per-tissue CSV count matrices in `data/FACS/FACS/`  
**Organs**: Liver, Kidney, Spleen, Lung, Heart, Marrow  
**Output**: `results/mouse_pilot_v2b_results.csv`, `results/full_matrix_*.csv`
""")

# CELL 2
code(r"""# ── Part 1.1: Load Mouse Data ───────────────────────────────────
FACS_DIR = DATA_DIR / 'FACS' / 'FACS'
HK_FILE = DATA_DIR / 'housekeeping' / 'Human_Mouse_Common.csv'
ANNOT_FILE = DATA_DIR / 'annotations_FACS.csv'
TARGET_TISSUES = ['Liver', 'Kidney', 'Spleen', 'Lung', 'Heart', 'Marrow']

# Helper: extract mouse ID from cell name
def extract_mouse_id(cell_name):
    parts = cell_name.split('.')
    for p in parts:
        if '_' in p and (p.endswith('_M') or p.endswith('_F')):
            return p
    return 'unknown'

def random_split_cells(cells, seed=RANDOM_SEED):
    n = cells.shape[0]
    n_half = n // 2
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    return cells[idx[:n_half]], cells[idx[n_half:]]

# Load HK genes
hk_df = pd.read_csv(HK_FILE, sep=';', engine='python')
hk_mouse_genes = set(hk_df.iloc[:, 0].dropna().astype(str))
print(f'  HRT Atlas mouse HK genes: {len(hk_mouse_genes)}')

# Load annotations
annot = pd.read_csv(ANNOT_FILE)
annot = annot[annot['tissue'].isin(TARGET_TISSUES)]
annot['mouse.id'] = annot['cell'].apply(extract_mouse_id)
print(f'  Annotations: {len(annot)} cells')

# Load per-tissue count matrices
adatas = {}
all_genes = set()
for tissue in TARGET_TISSUES:
    fname = FACS_DIR / f'{tissue}-counts.csv'
    if not fname.exists():
        print(f'  WARNING: {fname} not found!')
        continue
    df = pd.read_csv(fname, index_col=0)
    adatas[tissue] = df
    all_genes.update(df.index.tolist())
    print(f'  {tissue}: {df.shape[1]} cells x {df.shape[0]} genes')
""")

# CELL 3
code(r"""# ── Part 1.2: Build Unified AnnData ──────────────────────────────
# Intersect genes across all tissues
common_genes = all_genes.copy()
for tissue, df in adatas.items():
    common_genes &= set(df.index)
common_genes = sorted(common_genes)
print(f'  Common genes: {len(common_genes)}')

# Build expression matrix + obs
expr_parts, obs_parts = [], []
for tissue, df in adatas.items():
    df_aligned = df.loc[df.index.isin(common_genes)].reindex(common_genes, fill_value=0).T
    expr_parts.append(df_aligned.values)
    tissue_annot = annot[annot['tissue'] == tissue].copy()
    cell_ids = df_aligned.index.tolist()
    obs_tissue = pd.DataFrame({'cell': cell_ids, 'tissue': tissue})
    obs_tissue = obs_tissue.merge(
        tissue_annot[['cell', 'cell_ontology_class', 'mouse.id']],
        on='cell', how='left'
    )
    obs_tissue['cell_ontology_class'] = obs_tissue['cell_ontology_class'].fillna('unknown')
    obs_tissue.set_index('cell', inplace=True)
    obs_parts.append(obs_tissue)

X = np.vstack(expr_parts)
obs = pd.concat(obs_parts, axis=0)
var = pd.DataFrame({'gene': common_genes}).set_index('gene')

adata_mouse = sc_mod.AnnData(X=X, obs=obs, var=var)
adata_mouse.obs['tissue'] = adata_mouse.obs['tissue'].astype('category')
print(f'  Unified: {adata_mouse.n_obs} cells x {adata_mouse.n_vars} genes')
""")

# CELL 4
code(r"""# ── Part 1.3: Preprocessing ──────────────────────────────────────
# QC
sc_mod.pp.filter_cells(adata_mouse, min_genes=500)
sc_mod.pp.filter_genes(adata_mouse, min_cells=3)
print(f'  After QC: {adata_mouse.n_obs} cells x {adata_mouse.n_vars} genes')

# Normalize: CP10k + log1p
sc_mod.pp.normalize_total(adata_mouse, target_sum=1e4)
sc_mod.pp.log1p(adata_mouse)

# HVG selection (for full matrix analysis)
sc_mod.pp.highly_variable_genes(adata_mouse, n_top_genes=2000, flavor='seurat')
print(f'  HVGs: {adata_mouse.var["highly_variable"].sum()}')

# Gene name list
gene_names_mouse = adata_mouse.var_names.tolist()

# HK indices (HRT Atlas only, no auto-detection on full matrix)
hk_indices_mouse = [i for i, g in enumerate(gene_names_mouse) if g in hk_mouse_genes]
print(f'  HK genes found: {len(hk_indices_mouse)}')
""")

# CELL 5
code(r"""# ── Part 1.4: Build Pseudobulks ──────────────────────────────────
MIN_CELLS_PER_CT_MOUSE = 20  # min 20 cells = 2 * MIN_CELLS_PER_CT

ct_all_cells = {}
ct_pb_largest = {}
ct_cells_largest = {}

for tissue in TARGET_TISSUES:
    tdata = adata_mouse[adata_mouse.obs['tissue'] == tissue]
    t_cts = tdata.obs['cell_ontology_class'].unique()
    for ct in t_cts:
        if ct.lower() == 'unknown':
            continue
        ct_mask = tdata.obs['cell_ontology_class'] == ct
        ct_data = tdata[ct_mask]
        if ct_data.n_obs < MIN_CELLS_PER_CT_MOUSE:
            continue
        
        X_all = ct_data.X
        if hasattr(X_all, 'toarray'):
            X_all = X_all.toarray()
        ct_all_cells[(tissue, ct)] = X_all
        
        # Largest mouse group pseudobulk
        mouse_counts = ct_data.obs['mouse.id'].value_counts()
        mice_ok = [(m, n) for m, n in mouse_counts.items() if n >= MIN_CELLS_PER_CT]
        if len(mice_ok) >= 1:
            mice_ok.sort(key=lambda x: -x[1])
            largest_mouse = mice_ok[0][0]
            mask_largest = ct_data.obs['mouse.id'] == largest_mouse
            X_largest = ct_data[mask_largest].X
            if hasattr(X_largest, 'toarray'):
                X_largest = X_largest.toarray()
            if X_largest.shape[0] >= MIN_CELLS_PER_CT:
                ct_pb_largest[(tissue, ct)] = np.mean(X_largest, axis=0)
                ct_cells_largest[(tissue, ct)] = X_largest

print(f'  CTs with >= {MIN_CELLS_PER_CT_MOUSE} cells: {len(ct_all_cells)}')
print(f'  CTs with largest-mouse group: {len(ct_pb_largest)}')
""")

# CELL 6
code(r"""# ── Part 1.5: Define Pilot Comparisons ──────────────────────────
comparisons = []

# C: Control (random split, same CT/same tissue -> omega ~1)
control_pairs = [
    ('Liver', 'hepatocyte'),
    ('Heart', 'endothelial cell'),
    ('Spleen', 'B cell'),
    ('Marrow', 'B cell'),
    ('Heart', 'fibroblast'),
    ('Marrow', 'neutrophil'),
]
for tissue, ct in control_pairs:
    key = (tissue, ct)
    if key in ct_all_cells:
        cells_a, cells_b = random_split_cells(ct_all_cells[key])
        comparisons.append({
            'label': f'C: {ct} ({tissue})',
            'category': 'C_control',
            'tissue': tissue, 'ct': ct,
            'pb_a': np.mean(cells_a, axis=0),
            'pb_b': np.mean(cells_b, axis=0),
            'cells_a': cells_a, 'cells_b': cells_b,
        })

# S: Same CT across tissues
same_ct_pairs = [
    ('B cell', 'Marrow', 'Spleen'),
    ('B cell', 'Spleen', 'Lung'),
    ('endothelial cell', 'Heart', 'Lung'),
    ('natural killer cell', 'Marrow', 'Liver'),
]
for ct, t1, t2 in same_ct_pairs:
    key1, key2 = (t1, ct), (t2, ct)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        comparisons.append({
            'label': f'S: {ct} ({t1} vs {t2})',
            'category': 'S_same_ct',
            'tissue_a': t1, 'tissue_b': t2, 'ct': ct,
            'pb_a': ct_pb_largest[key1], 'pb_b': ct_pb_largest[key2],
            'cells_a': ct_cells_largest[key1], 'cells_b': ct_cells_largest[key2],
        })

# D: Different CT, same tissue
diff_ct_pairs = [
    ('Liver', 'hepatocyte', 'endothelial cell of hepatic sinusoid'),
    ('Marrow', 'B cell', 'neutrophil'),
    ('Heart', 'endothelial cell', 'fibroblast'),
]
for tissue, ct1, ct2 in diff_ct_pairs:
    key1, key2 = (tissue, ct1), (tissue, ct2)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        comparisons.append({
            'label': f'D: {ct1} vs {ct2} ({tissue})',
            'category': 'D_diff_ct',
            'tissue': tissue, 'ct_a': ct1, 'ct_b': ct2,
            'pb_a': ct_pb_largest[key1], 'pb_b': ct_pb_largest[key2],
            'cells_a': ct_cells_largest[key1], 'cells_b': ct_cells_largest[key2],
        })

# X: Cross (different CT, different tissue)
cross_pairs = [
    ('Liver', 'hepatocyte', 'Marrow', 'B cell'),
    ('Heart', 'cardiac muscle cell', 'Marrow', 'neutrophil'),
]
for t1, ct1, t2, ct2 in cross_pairs:
    key1, key2 = (t1, ct1), (t2, ct2)
    if key1 in ct_pb_largest and key2 in ct_pb_largest:
        comparisons.append({
            'label': f'X: {ct1}({t1}) vs {ct2}({t2})',
            'category': 'X_cross',
            'tissue_a': t1, 'tissue_b': t2, 'ct_a': ct1, 'ct_b': ct2,
            'pb_a': ct_pb_largest[key1], 'pb_b': ct_pb_largest[key2],
            'cells_a': ct_cells_largest[key1], 'cells_b': ct_cells_largest[key2],
        })

print(f'  Total comparisons: {len(comparisons)}')
for cat in ['C_control', 'S_same_ct', 'D_diff_ct', 'X_cross']:
    n = sum(1 for c in comparisons if c['category'] == cat)
    print(f'    {cat}: {n}')
""")

# CELL 7
code(r"""# ── Part 1.6: CKI Pilot + Two-Sided Bootstrap ───────────────────
# Non-HK mask for k_f selection
N_GENES_MOUSE = len(gene_names_mouse)
non_hk_mask = np.ones(N_GENES_MOUSE, dtype=bool)
for idx in hk_indices_mouse:
    if idx < N_GENES_MOUSE:
        non_hk_mask[idx] = False
non_hk_indices_mouse = np.where(non_hk_mask)[0]
print(f'  Non-HK indices for k_f: {len(non_hk_indices_mouse)}')

results_list = []
for comp in comparisons:
    label = comp['label']
    pb_a = comp['pb_a']
    pb_b = comp['pb_b']
    cells_a = comp['cells_a']
    cells_b = comp['cells_b']
    n_a, n_b = cells_a.shape[0], cells_b.shape[0]
    
    # k_n: global HK genes
    hk_i = pb_a[hk_indices_mouse]
    hk_j = pb_b[hk_indices_mouse]
    kn_val = js_divergence(hk_i, hk_j)
    
    # k_f: per-pair top-N DE genes (exclude HK)
    abs_diff = np.abs(pb_a - pb_b)
    abs_diff_non_hk = abs_diff[non_hk_mask]
    top_n = min(N_TOP_KF, len(abs_diff_non_hk))
    top_local = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
    top_local = top_local[np.argsort(abs_diff_non_hk[top_local])[::-1]]
    top_global = non_hk_indices_mouse[top_local]
    kf_val = js_divergence(pb_a[top_global], pb_b[top_global])
    
    omega_obs = kf_val / kn_val if kn_val > 0 else float('inf')
    
    # TWO-SIDED bootstrap
    pooled = np.vstack([cells_a, cells_b])
    n_total = n_a + n_b
    rng = np.random.RandomState(RANDOM_SEED)
    
    null_omega = []
    for b in range(N_BOOTSTRAP):
        perm = rng.permutation(n_total)
        pb_perm1 = np.mean(pooled[perm[:n_a]], axis=0)
        pb_perm2 = np.mean(pooled[perm[n_a:]], axis=0)
        
        hk_1 = pb_perm1[hk_indices_mouse]
        hk_2 = pb_perm2[hk_indices_mouse]
        kn_null = js_divergence(hk_1, hk_2)
        
        abs_diff_null = np.abs(pb_perm1 - pb_perm2)
        abs_diff_non_hk_null = abs_diff_null[non_hk_mask]
        top_local_null = np.argpartition(abs_diff_non_hk_null, -top_n)[-top_n:]
        top_local_null = top_local_null[np.argsort(abs_diff_non_hk_null[top_local_null])[::-1]]
        top_global_null = non_hk_indices_mouse[top_local_null]
        
        kf_null = js_divergence(pb_perm1[top_global_null], pb_perm2[top_global_null])
        omega_null_val = kf_null / (kn_null + EPSILON)
        if not np.isnan(omega_null_val):
            null_omega.append(omega_null_val)
    
    null_omega = np.array(null_omega)
    if len(null_omega) == 0:
        p_value, null_mean, null_std, cohens_d = 1.0, np.nan, np.nan, np.nan
    else:
        p_value = (np.sum(np.abs(null_omega - 1) >= np.abs(omega_obs - 1)) + 1) / (len(null_omega) + 1)
        null_mean = np.mean(null_omega)
        null_std = np.std(null_omega)
        cohens_d = (omega_obs - null_mean) / null_std if null_std > 1e-12 else 0.0
    
    sig = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
    print(f'  {label}: omega={omega_obs:.3f}, kn={kn_val:.5f}, kf={kf_val:.5f}, '
          f'p={p_value:.4f}{sig}, d={cohens_d:.2f}')
    
    results_list.append({
        'comparison': label,
        'category': comp['category'],
        'omega': omega_obs, 'kn': kn_val, 'kf': kf_val,
        'p_value': p_value, 'null_mean': null_mean,
        'null_std': null_std, 'cohens_d': cohens_d,
        'n_cells_A': n_a, 'n_cells_B': n_b,
    })

results_df_pilot = pd.DataFrame(results_list)
""")

# CELL 8
code(r"""# ── Part 1.7: Pilot Summary & Save ──────────────────────────────
for cat in ['C_control', 'S_same_ct', 'D_diff_ct', 'X_cross']:
    subset = results_df_pilot[results_df_pilot['category'] == cat]
    if len(subset) > 0:
        print(f'  {cat}: n={len(subset)}, mean_omega={subset["omega"].mean():.2f}, '
              f'median={subset["omega"].median():.2f}')

# Save
results_df_pilot.to_csv(RESULTS_DIR / 'mouse_pilot_v2b_results.csv', index=False)
print(f'\n  Saved: mouse_pilot_v2b_results.csv')

key_vals = {}
for cat in ['C_control', 'S_same_ct', 'D_diff_ct', 'X_cross']:
    subset = results_df_pilot[results_df_pilot['category'] == cat]
    if len(subset) > 0:
        key_vals[f'{cat}_mean'] = round(subset['omega'].mean(), 2)
        key_vals[f'{cat}_n'] = len(subset)
ctrl = results_df_pilot[results_df_pilot['category'] == 'C_control']
if len(ctrl) > 0:
    key_vals['control_mean'] = round(ctrl['omega'].mean(), 2)
    key_vals['control_median'] = round(ctrl['omega'].median(), 2)
pd.DataFrame([key_vals]).to_csv(RESULTS_DIR / 'mouse_pilot_v2b_key_values.csv', index=False)
print('  Saved: mouse_pilot_v2b_key_values.csv')
""")

# CELL 9
code(r"""# ── Part 1.8: Full Pairwise Matrix (703 pairs, no bootstrap) ────
# Build CT pseudobulk list (largest mouse group per CT)
ct_entries_full = []
for tissue in TARGET_TISSUES:
    tdata = adata_mouse[adata_mouse.obs['tissue'] == tissue]
    for ct in tdata.obs['cell_ontology_class'].unique():
        if ct.lower() == 'unknown':
            continue
        ct_mask = tdata.obs['cell_ontology_class'] == ct
        ct_data = tdata[ct_mask]
        if ct_data.n_obs < MIN_CELLS_PER_CT_MOUSE:
            continue
        mouse_counts = ct_data.obs['mouse.id'].value_counts()
        mice_ok = [(m, n) for m, n in mouse_counts.items() if n >= MIN_CELLS_PER_CT]
        if len(mice_ok) < 1:
            continue
        mice_ok.sort(key=lambda x: -x[1])
        largest_mouse = mice_ok[0][0]
        mask_largest = ct_data.obs['mouse.id'] == largest_mouse
        X_large = ct_data[mask_largest].X
        if hasattr(X_large, 'toarray'):
            X_large = X_large.toarray()
        if X_large.shape[0] < MIN_CELLS_PER_CT:
            continue
        pb = np.mean(X_large, axis=0)
        ct_entries_full.append({
            'key': f'{tissue}|{ct}', 'tissue': tissue, 'ct': ct,
            'pb': pb, 'n_cells': X_large.shape[0],
        })

n_ct = len(ct_entries_full)
print(f'  Viable CT entries: {n_ct}')

# HVG identity indices
identity_indices = np.where(adata_mouse.var['highly_variable'].values)[0].tolist()

# Compute all pairwise omega
omega_matrix_full = np.zeros((n_ct, n_ct))
kn_matrix_full = np.zeros((n_ct, n_ct))
kf_matrix_full = np.zeros((n_ct, n_ct))

total_pairs = n_ct * (n_ct - 1) // 2
print(f'  Total pairs: {total_pairs}')

pair_count = 0
for i in tqdm(range(n_ct), desc='Computing pairs'):
    for j in range(i + 1, n_ct):
        result = compute_omega(
            ct_entries_full[i]['pb'], ct_entries_full[j]['pb'],
            hk_indices_mouse, identity_indices
        )
        omega_matrix_full[i, j] = result['omega']
        omega_matrix_full[j, i] = result['omega']
        kn_matrix_full[i, j] = result['kn']
        kn_matrix_full[j, i] = result['kn']
        kf_matrix_full[i, j] = result['kf']
        kf_matrix_full[j, i] = result['kf']
        pair_count += 1

np.fill_diagonal(omega_matrix_full, 0)
np.fill_diagonal(kn_matrix_full, 0)
np.fill_diagonal(kf_matrix_full, 0)

print(f'\n  Computed {pair_count} pairs')
""")

# CELL 10
code(r"""# ── Part 1.9: Full Matrix Save & Summary ────────────────────────
# Build labels
labels_full = []
for e in ct_entries_full:
    ct_short = e['ct'].replace('endothelial cell of hepatic sinusoid', 'liver sinusoid EC')
    ct_short = ct_short.replace('cardiac muscle cell', 'cardiac muscle')
    ct_short = ct_short.replace('natural killer cell', 'NK cell')
    if len(ct_short) > 18:
        ct_short = ct_short[:16] + '..'
    labels_full.append(f"{e['tissue'][:4]}|{ct_short}")

# Save matrices
omega_df = pd.DataFrame(omega_matrix_full, index=labels_full, columns=labels_full)
omega_df.to_csv(RESULTS_DIR / 'full_matrix_omega.csv')
print('  Saved: full_matrix_omega.csv')

kn_df = pd.DataFrame(kn_matrix_full, index=labels_full, columns=labels_full)
kn_df.to_csv(RESULTS_DIR / 'full_matrix_kn.csv')
print('  Saved: full_matrix_kn.csv')

kf_df = pd.DataFrame(kf_matrix_full, index=labels_full, columns=labels_full)
kf_df.to_csv(RESULTS_DIR / 'full_matrix_kf.csv')
print('  Saved: full_matrix_kf.csv')

# Long-form pairs list
pairs_list_full = []
for i in range(n_ct):
    for j in range(i + 1, n_ct):
        pairs_list_full.append({
            'pair': f'{labels_full[i]} vs {labels_full[j]}',
            'omega': omega_matrix_full[i, j],
            'kn': kn_matrix_full[i, j],
            'kf': kf_matrix_full[i, j],
            'same_tissue': ct_entries_full[i]['tissue'] == ct_entries_full[j]['tissue'],
            'same_ct': ct_entries_full[i]['ct'] == ct_entries_full[j]['ct'],
        })
pairs_full_df = pd.DataFrame(pairs_list_full).sort_values('omega', ascending=False)
pairs_full_df.to_csv(RESULTS_DIR / 'full_matrix_pairs.csv', index=False)
print('  Saved: full_matrix_pairs.csv')

# Summary
upper_tri = omega_matrix_full[np.triu_indices(n_ct, k=1)]
print(f'\n  Omega range: [{np.min(upper_tri):.2f}, {np.max(upper_tri):.2f}]')
print(f'  Omega mean: {np.mean(upper_tri):.2f}, median: {np.median(upper_tri):.2f}')
print('\nPart 1 COMPLETE.')
""")

# ==============================
# PART 2: Tabula Sapiens (Human)
# ==============================
md("""---
# Part 2: Tabula Sapiens (Human)

**Dataset**: Tabula Sapiens (Jones et al., Science 2022)  
**Input**: Per-organ h5ad files in `data/ts_human/` (TS_Liver.h5ad, TS_Kidney.h5ad, etc.)  
**Organs**: Liver, Kidney, Heart, Bone Marrow, Spleen, Lung  
**Output**: `results/phase33_v3_human_*.csv`
""")

# CELL 11
code(r"""# ── Part 2.1: Human Gene Lists ──────────────────────────────────
TS_HUMAN_DIR = DATA_DIR / 'ts_human'
TS_ORGANS = ['Liver', 'Kidney', 'Heart', 'Bone_Marrow', 'Spleen', 'Lung']

import h5py
all_var_names = []
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f'TS_{organ}.h5ad'
    if not fname.exists():
        print(f'  WARNING: {fname} not found!')
        continue
    with h5py.File(fname, 'r') as f:
        var_names = [x.decode('utf-8') if isinstance(x, bytes) else x
                     for x in f['var']['_index'][:]]
    all_var_names.append(set(var_names))
    print(f'  {organ}: {len(all_var_names[-1])} genes')

common_genes_human = sorted(all_var_names[0].intersection(*all_var_names[1:]))
common_genes_human_set = set(common_genes_human)
print(f'\n  Common genes: {len(common_genes_human)}')
""")

# CELL 12
code(r"""# ── Part 2.2: Human HK Genes ────────────────────────────────────
hk_df_human = pd.read_csv(HK_FILE, sep=';', engine='python')
hk_human_genes_set = set(hk_df_human['Human'].dropna().tolist())

# HK genes that are in the common gene set
hk_global_genes = sorted(hk_human_genes_set & common_genes_human_set)
hk_global_idx_map = {g: i for i, g in enumerate(common_genes_human)}
hk_global_idx = np.array([hk_global_idx_map[g] for g in hk_global_genes])
print(f'  Global HK genes in common set: {len(hk_global_idx)}')
""")

# CELL 13
code(r"""# ── Part 2.3: Build CT Pseudobulks (memory-optimized) ───────────
ct_entries_human = []
for organ in TS_ORGANS:
    fname = TS_HUMAN_DIR / f'TS_{organ}.h5ad'
    if not fname.exists():
        continue

    print(f'  Loading {organ}...')
    adata = sc_mod.read_h5ad(fname)

    # Subset to common genes
    gene_mask = np.array([g in common_genes_human_set for g in adata.var_names])
    adata = adata[:, gene_mask].copy()

    # Preprocess
    sc_mod.pp.filter_cells(adata, min_genes=500)
    sc_mod.pp.normalize_total(adata, target_sum=1e4)
    sc_mod.pp.log1p(adata)

    # Map var indices to common gene order
    var_to_common_idx = {}
    for idx, g in enumerate(adata.var_names):
        if g in common_genes_human_set:
            var_to_common_idx[idx] = common_genes_human.index(g)

    ct_labels = adata.obs['cell_ontology_class'].value_counts()
    for ct, count in ct_labels.items():
        if ct.lower() == 'unknown':
            continue
        ct_mask = adata.obs['cell_ontology_class'] == ct
        ct_data = adata[ct_mask]

        # Largest donor group
        if 'donor' in ct_data.obs.columns:
            donor_counts = ct_data.obs['donor'].value_counts()
            donors_ok = [(d, n) for d, n in donor_counts.items() if n >= MIN_CELLS_PER_CT]
        else:
            donors_ok = [('pooled', ct_data.n_obs)]
        if len(donors_ok) < 1:
            continue
        donors_ok.sort(key=lambda x: -x[1])
        largest_donor = donors_ok[0][0]

        if 'donor' in ct_data.obs.columns:
            mask_largest = ct_data.obs['donor'] == largest_donor
        else:
            mask_largest = slice(None)

        X_large = ct_data[mask_largest].X
        if hasattr(X_large, 'toarray'):
            X_large = X_large.toarray()
        if X_large.shape[0] < MIN_CELLS_PER_CT:
            continue

        # Map to common gene order
        pb_common = np.zeros(len(common_genes_human))
        for local_idx, common_idx in var_to_common_idx.items():
            pb_common[common_idx] = np.mean(X_large[:, local_idx])

        ct_entries_human.append({
            'key': f'{organ}|{ct}', 'organ': organ, 'ct': ct,
            'pb': pb_common, 'n_cells': X_large.shape[0], 'donor': largest_donor,
        })
        print(f'    {organ}|{ct}: {X_large.shape[0]} cells')

    del adata; gc.collect()

n_ct_human = len(ct_entries_human)
print(f'\n  Total viable CT entries: {n_ct_human}')
""")

# CELL 14
code(r"""# ── Part 2.4: Compute Omega (global k_n + per-pair k_f) ─────────
omega_matrix_human = np.zeros((n_ct_human, n_ct_human))
kn_matrix_human = np.zeros((n_ct_human, n_ct_human))
kf_matrix_human = np.zeros((n_ct_human, n_ct_human))
total_pairs_human = n_ct_human * (n_ct_human - 1) // 2

for i in range(n_ct_human):
    for j in range(i + 1, n_ct_human):
        pb_i = ct_entries_human[i]['pb']
        pb_j = ct_entries_human[j]['pb']

        # k_n: GLOBAL HK
        hk_i = pb_i[hk_global_idx]
        hk_j = pb_j[hk_global_idx]
        kn_val = js_divergence(hk_i, hk_j)

        # k_f: per-pair top-N DE (exclude HK)
        abs_diff = np.abs(pb_i - pb_j)
        abs_diff_non_hk = abs_diff.copy()
        abs_diff_non_hk[hk_global_idx] = -1

        top_n = min(N_TOP_KF, len(abs_diff_non_hk) - len(hk_global_idx))
        top_idx = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
        top_idx = top_idx[np.argsort(abs_diff_non_hk[top_idx])[::-1]]

        kf_val = js_divergence(pb_i[top_idx], pb_j[top_idx])
        omega_val = kf_val / kn_val if kn_val > 0 else float('inf')

        omega_matrix_human[i, j] = omega_val
        omega_matrix_human[j, i] = omega_val
        kn_matrix_human[i, j] = kn_val
        kn_matrix_human[j, i] = kn_val
        kf_matrix_human[i, j] = kf_val
        kf_matrix_human[j, i] = kf_val

    if (i + 1) % 10 == 0:
        print(f'  Progress: row {i+1}/{n_ct_human}')

np.fill_diagonal(omega_matrix_human, 0)
np.fill_diagonal(kn_matrix_human, 0)
np.fill_diagonal(kf_matrix_human, 0)
""")

# CELL 15
code(r"""# ── Part 2.5: Method Comparison (AUC + Spearman) ─────────────────
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr
from scipy.spatial.distance import cosine

same_type = np.zeros((n_ct_human, n_ct_human), dtype=bool)
for i in range(n_ct_human):
    for j in range(i + 1, n_ct_human):
        same_type[i, j] = ct_entries_human[i]['ct'] == ct_entries_human[j]['ct']

upper_mask = np.triu_indices(n_ct_human, k=1)
y_true = same_type[upper_mask].astype(int)

# CKI omega (invert: higher omega = more different)
omega_scores = -omega_matrix_human[upper_mask]
omega_scores[np.isinf(omega_scores) | np.isnan(omega_scores)] = -1000
auc_omega = roc_auc_score(y_true, omega_scores)
print(f'  CKI omega AUC: {auc_omega:.4f}')

# Cosine distance
pb_matrix = np.array([e['pb'] for e in ct_entries_human])
cosine_dists = np.zeros(len(y_true))
idx = 0
for i in range(n_ct_human):
    for j in range(i + 1, n_ct_human):
        cosine_dists[idx] = cosine(pb_matrix[i], pb_matrix[j])
        idx += 1
auc_cosine = roc_auc_score(y_true, cosine_dists)
print(f'  Cosine distance AUC: {auc_cosine:.4f}')

# Spearman distance
spearman_dists = np.zeros(len(y_true))
idx = 0
for i in range(n_ct_human):
    for j in range(i + 1, n_ct_human):
        r, _ = spearmanr(pb_matrix[i], pb_matrix[j])
        spearman_dists[idx] = 1 - r
        idx += 1
auc_spearman = roc_auc_score(y_true, spearman_dists)
print(f'  Spearman distance AUC: {auc_spearman:.4f}')

# Raw JS divergence (all genes)
js_all = np.zeros(len(y_true))
idx = 0
for i in range(n_ct_human):
    for j in range(i + 1, n_ct_human):
        js_all[idx] = js_divergence(pb_matrix[i], pb_matrix[j])
        idx += 1
auc_js = roc_auc_score(y_true, js_all)
print(f'  Raw JS AUC: {auc_js:.4f}')

# Correlations
print(f'\n  Spearman: omega vs cosine = {spearmanr(omega_scores, cosine_dists)[0]:.4f}')
print(f'  Spearman: omega vs spearman dist = {spearmanr(omega_scores, spearman_dists)[0]:.4f}')
print(f'  Spearman: omega vs raw JS = {spearmanr(omega_scores, js_all)[0]:.4f}')

auc_data = {'CKI_omega': auc_omega, 'Cosine': auc_cosine,
            'Spearman': auc_spearman, 'Raw_JS': auc_js}
np.save(RESULTS_DIR / 'figure_data_auc.npy', auc_data)
""")

# CELL 16
code(r"""# ── Part 2.6: Save Human Results ────────────────────────────────
labels_human = [e['key'] for e in ct_entries_human]

omega_df_human = pd.DataFrame(omega_matrix_human, index=labels_human, columns=labels_human)
omega_df_human.to_csv(RESULTS_DIR / 'phase33_v3_human_omega.csv')

kn_df_human = pd.DataFrame(kn_matrix_human, index=labels_human, columns=labels_human)
kn_df_human.to_csv(RESULTS_DIR / 'phase33_v3_human_kn.csv')

kf_df_human = pd.DataFrame(kf_matrix_human, index=labels_human, columns=labels_human)
kf_df_human.to_csv(RESULTS_DIR / 'phase33_v3_human_kf.csv')

pairs_human_list = []
for i in range(n_ct_human):
    for j in range(i + 1, n_ct_human):
        pairs_human_list.append({
            'pair': f'{labels_human[i]} vs {labels_human[j]}',
            'omega': omega_matrix_human[i, j],
            'kn': kn_matrix_human[i, j],
            'kf': kf_matrix_human[i, j],
            'same_type': int(ct_entries_human[i]['ct'] == ct_entries_human[j]['ct']),
            'same_organ': int(ct_entries_human[i]['organ'] == ct_entries_human[j]['organ']),
        })
pairs_human_df = pd.DataFrame(pairs_human_list).sort_values('omega', ascending=False)
pairs_human_df.to_csv(RESULTS_DIR / 'phase33_v3_human_pairs.csv', index=False)

upper_human = omega_matrix_human[np.triu_indices(n_ct_human, k=1)]
print(f'  Omega range: [{np.min(upper_human):.2f}, {np.max(upper_human):.2f}]')
print(f'  Omega mean: {np.mean(upper_human):.2f}, median: {np.median(upper_human):.2f}')
print('\nPart 2 COMPLETE.')
""")

# ==============================
# PART 3: TCGA
# ==============================
md("""---
# Part 3: TCGA Pan-Cancer

**Dataset**: TCGA RSEM gene TPM (UCSC Xena)  
**Input**: `data/tcga/tcga_RSEM_gene_tpm.gz` + `data/tcga/probemap.tsv`  
**Cancer types**: LUAD, LUSC, LIHC, KIRC, BRCA  
**Output**: `results/phase34_v2_*.csv`
""")

# CELL 17
code(r"""# ── Part 3.1: TCGA Metadata + HK Mapping ────────────────────────
TCGA_FILE = DATA_DIR / 'tcga' / 'tcga_RSEM_gene_tpm.gz'
PROBEMAP_FILE = DATA_DIR / 'tcga' / 'probemap.tsv'
TARGET_CANCERS = ['TCGA-LUAD', 'TCGA-LUSC', 'TCGA-LIHC', 'TCGA-KIRC', 'TCGA-BRCA']
MIN_TUMOR = 30
MIN_NORMAL = 10
MAX_PAIRS_TT = 2000
MAX_PAIRS_TN = 2000

pm = pd.read_csv(PROBEMAP_FILE, sep='\t')
ens_to_symbol = {}
for _, row in pm.iterrows():
    ens_id = str(row.iloc[0]).split('.')[0]
    symbol = str(row.iloc[1])
    if ens_id and symbol and symbol != 'nan':
        ens_to_symbol[ens_id] = symbol
symbol_to_ens = {}
for eid, sym in ens_to_symbol.items():
    symbol_to_ens.setdefault(sym, []).append(eid)

hk_human_tcga = set()
for row in hk_df_human.iloc[:, 0].dropna().astype(str):
    parts = row.split(';')
    if len(parts) >= 2:
        hk_human_tcga.add(parts[1].strip())

# TSS -> Project mapping
TSS_TO_PROJECT = {
    'A1':'TCGA-BRCA','A2':'TCGA-BRCA','A7':'TCGA-BRCA','A8':'TCGA-BRCA',
    'AN':'TCGA-BRCA','AO':'TCGA-BRCA','AQ':'TCGA-BRCA','AR':'TCGA-BRCA',
    'B6':'TCGA-BRCA','BH':'TCGA-BRCA','C8':'TCGA-BRCA','D8':'TCGA-BRCA',
    'E2':'TCGA-BRCA','EW':'TCGA-BRCA','GI':'TCGA-BRCA','WT':'TCGA-BRCA',
    'XX':'TCGA-BRCA','E9':'TCGA-BRCA','GM':'TCGA-BRCA','HN':'TCGA-BRCA',
    'JL':'TCGA-BRCA','LD':'TCGA-BRCA','LL':'TCGA-BRCA','MS':'TCGA-BRCA',
    'OL':'TCGA-BRCA','PE':'TCGA-BRCA','PL':'TCGA-BRCA','S3':'TCGA-BRCA',
    'UL':'TCGA-BRCA','V7':'TCGA-BRCA','W8':'TCGA-BRCA','WV':'TCGA-BRCA',
    '05':'TCGA-LUAD','35':'TCGA-LUAD','38':'TCGA-LUAD','44':'TCGA-LUAD',
    '49':'TCGA-LUAD','50':'TCGA-LUAD','55':'TCGA-LUAD','64':'TCGA-LUAD',
    '67':'TCGA-LUAD','73':'TCGA-LUAD','75':'TCGA-LUAD','78':'TCGA-LUAD',
    '86':'TCGA-LUAD','91':'TCGA-LUAD','93':'TCGA-LUAD','97':'TCGA-LUAD',
    'J2':'TCGA-LUAD','L3':'TCGA-LUAD','L4':'TCGA-LUAD','M1':'TCGA-LUAD',
    'MP':'TCGA-LUAD','MT':'TCGA-LUAD','N1':'TCGA-LUAD','N6':'TCGA-LUAD',
    'O1':'TCGA-LUAD','S2':'TCGA-LUAD','TR':'TCGA-LUAD','TV':'TCGA-LUAD',
    'TQ':'TCGA-LUAD','NJ':'TCGA-LUAD','KN':'TCGA-LUAD','LF':'TCGA-LUAD',
    '18':'TCGA-LUSC','21':'TCGA-LUSC','22':'TCGA-LUSC','33':'TCGA-LUSC',
    '34':'TCGA-LUSC','37':'TCGA-LUSC','39':'TCGA-LUSC','43':'TCGA-LUSC',
    '51':'TCGA-LUSC','52':'TCGA-LUSC','56':'TCGA-LUSC','60':'TCGA-LUSC',
    '63':'TCGA-LUSC','66':'TCGA-LUSC','68':'TCGA-LUSC','70':'TCGA-LUSC',
    '77':'TCGA-LUSC','85':'TCGA-LUSC','90':'TCGA-LUSC','92':'TCGA-LUSC',
    '94':'TCGA-LUSC','96':'TCGA-LUSC','98':'TCGA-LUSC','CC':'TCGA-LUSC',
    'L5':'TCGA-LUSC','N2':'TCGA-LUSC','NK':'TCGA-LUSC','Q1':'TCGA-LUSC',
    'IE':'TCGA-LUSC','IF':'TCGA-LUSC','IG':'TCGA-LUSC',
    'BC':'TCGA-LIHC','DD':'TCGA-LIHC','ED':'TCGA-LIHC','EP':'TCGA-LIHC',
    'ES':'TCGA-LIHC','FV':'TCGA-LIHC','FY':'TCGA-LIHC','G3':'TCGA-LIHC',
    'GJ':'TCGA-LIHC','HP':'TCGA-LIHC','HU':'TCGA-LIHC','K7':'TCGA-LIHC',
    'KR':'TCGA-LIHC','LG':'TCGA-LIHC','NI':'TCGA-LIHC','O8':'TCGA-LIHC',
    'PD':'TCGA-LIHC','QN':'TCGA-LIHC','RC':'TCGA-LIHC','RG':'TCGA-LIHC',
    'T6':'TCGA-LIHC','UB':'TCGA-LIHC','WQ':'TCGA-LIHC','XR':'TCGA-LIHC',
    'YA':'TCGA-LIHC','ZP':'TCGA-LIHC','ZS':'TCGA-LIHC',
    'MI':'TCGA-LIHC','F5':'TCGA-LIHC',
    'A3':'TCGA-KIRC','AK':'TCGA-KIRC','AL':'TCGA-KIRC','AY':'TCGA-KIRC',
    'B0':'TCGA-KIRC','B1':'TCGA-KIRC','B2':'TCGA-KIRC','B3':'TCGA-KIRC',
    'B4':'TCGA-KIRC','B8':'TCGA-KIRC','BP':'TCGA-KIRC','BW':'TCGA-KIRC',
    'CJ':'TCGA-KIRC','CW':'TCGA-KIRC','CZ':'TCGA-KIRC','DV':'TCGA-KIRC',
    'DX':'TCGA-KIRC','EU':'TCGA-KIRC','GK':'TCGA-KIRC','HE':'TCGA-KIRC',
    'I6':'TCGA-KIRC','K6':'TCGA-KIRC','KL':'TCGA-KIRC','MM':'TCGA-KIRC',
    'MW':'TCGA-KIRC','P4':'TCGA-KIRC','Q2':'TCGA-KIRC','RG':'TCGA-KIRC',
    'UZ':'TCGA-KIRC','V5':'TCGA-KIRC','XM':'TCGA-KIRC','YE':'TCGA-KIRC',
}

with gzip.open(TCGA_FILE, 'rt') as fh:
    header_line = fh.readline().strip().split('\t')

proj_tumor = {}
proj_normal = {}
for sid in header_line[1:]:
    parts = sid.split('-')
    if len(parts) < 4: continue
    tss = parts[1]
    proj = TSS_TO_PROJECT.get(tss)
    if proj is None or proj not in TARGET_CANCERS: continue
    sc_ = parts[3][:2]
    if sc_ == '01':
        proj_tumor.setdefault(proj, []).append(sid)
    elif sc_ == '11':
        proj_normal.setdefault(proj, []).append(sid)

usable_cancers = []
for proj in TARGET_CANCERS:
    nt = len(proj_tumor.get(proj, []))
    nn = len(proj_normal.get(proj, []))
    if nt >= MIN_TUMOR and nn >= MIN_NORMAL:
        usable_cancers.append(proj)
        print(f'  {proj}: T={nt}, N={nn}')
    else:
        print(f'  {proj}: T={nt}, N={nn} -> SKIP')
""")

# CELL 18
code(r"""# ── Part 3.2: TCGA Per-Cancer Data Loading ──────────────────────
def load_cancer_data(cancer, tumor_ids, normal_ids):
    wanted = set(tumor_ids + normal_ids)
    col_idx_map = {}
    for k, sid in enumerate(header_line[1:], 1):
        if sid in wanted:
            col_idx_map[sid] = k
    sample_list = sorted(wanted)
    col_arr = np.array([col_idx_map[s] for s in sample_list], dtype=np.int32)
    
    gene_names_tcga = []
    with gzip.open(TCGA_FILE, 'rt') as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split('\t')
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
                gene_names_tcga.append(parts[0])
    
    n_genes_tcga = len(gene_names_tcga)
    expr = np.zeros((len(sample_list), n_genes_tcga), dtype=np.float32)
    gene_idx = 0
    with gzip.open(TCGA_FILE, 'rt') as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split('\t')
            if gene_idx < n_genes_tcga and parts[0] == gene_names_tcga[gene_idx]:
                for si, ci in enumerate(col_arr):
                    if ci < len(parts):
                        try:
                            expr[si, gene_idx] = float(parts[ci])
                        except (ValueError, IndexError):
                            pass
                gene_idx += 1
                if gene_idx >= n_genes_tcga:
                    break
    
    gene_means = np.mean(expr, axis=0)
    keep = gene_means >= 0.5
    expr = expr[:, keep]
    genes = [g for g, k in zip(gene_names_tcga, keep) if k]
    expr_log = np.log2(np.maximum(expr, 0) + 0.001)
    
    gene_ens = [g.split('.')[0] for g in genes]
    ens_to_idx_local = {ens: i for i, ens in enumerate(gene_ens)}
    hk_local = []
    for sym in hk_human_tcga:
        if sym in symbol_to_ens:
            for eid in symbol_to_ens[sym]:
                if eid in ens_to_idx_local:
                    hk_local.append(ens_to_idx_local[eid])
    hk_arr = np.array(sorted(set(hk_local)), dtype=int)
    
    tumor_mask = np.array([s in tumor_ids for s in sample_list])
    normal_mask = np.array([s in normal_ids for s in sample_list])
    return expr_log, hk_arr, tumor_mask, normal_mask, genes

def select_top_diff_tcga(pb1, pb2, hk_idx, n_top=N_TOP_KF):
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)

print('  Functions defined.')
""")

# CELL 19
code(r"""# ── Part 3.3: TCGA Per-Cancer Omega ─────────────────────────────
from scipy.stats import mannwhitneyu

all_summary_tcga = []
all_pair_details = []

for cancer in usable_cancers:
    t0_cancer = time.time()
    print(f'\n--- {cancer} ---')
    expr_log, hk_arr, tumor_mask, normal_mask, genes = load_cancer_data(
        cancer, proj_tumor[cancer], proj_normal[cancer])
    t_idx = np.where(tumor_mask)[0]
    n_idx = np.where(normal_mask)[0]
    n_t = len(t_idx)
    n_n = len(n_idx)
    print(f'  Genes: {len(genes)}, HK: {len(hk_arr)}, T={n_t}, N={n_n}')

    # TT
    all_tt = [(i, j) for i in range(n_t) for j in range(i + 1, n_t)]
    n_tt_total = len(all_tt)
    np.random.seed(RANDOM_SEED)
    if n_tt_total > MAX_PAIRS_TT:
        tt_pairs = [all_tt[k] for k in np.random.choice(n_tt_total, MAX_PAIRS_TT, replace=False)]
    else:
        tt_pairs = all_tt
    tt_details = []
    for idx, (i, j) in enumerate(tt_pairs):
        p1, p2 = expr_log[t_idx[i], :], expr_log[t_idx[j], :]
        id_idx = select_top_diff_tcga(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
        tt_details.append({'pair_type': 'TT', 'cancer': cancer,
                          'omega': r['omega'], 'kn': r['kn'], 'kf': r['kf']})
        if (idx + 1) % 500 == 0:
            print(f'    TT: {idx+1}/{len(tt_pairs)}', end='\r')
    print(f'    TT: {len(tt_pairs)}/{n_tt_total} done')

    # NN
    n_nn_total = n_n * (n_n - 1) // 2
    nn_details = []
    for i in range(n_n):
        for j in range(i + 1, n_n):
            p1, p2 = expr_log[n_idx[i], :], expr_log[n_idx[j], :]
            id_idx = select_top_diff_tcga(p1, p2, hk_arr, N_TOP_KF)
            r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
            nn_details.append({'pair_type': 'NN', 'cancer': cancer,
                              'omega': r['omega'], 'kn': r['kn'], 'kf': r['kf']})
    print(f'    NN: {n_nn_total} done')

    # TN
    all_tn = [(i, j) for i in range(n_t) for j in range(n_n)]
    n_tn_total = len(all_tn)
    if n_tn_total > MAX_PAIRS_TN:
        tn_pairs = [all_tn[k] for k in np.random.choice(n_tn_total, MAX_PAIRS_TN, replace=False)]
    else:
        tn_pairs = all_tn
    tn_details = []
    for idx, (i, j) in enumerate(tn_pairs):
        p1, p2 = expr_log[t_idx[i], :], expr_log[n_idx[j], :]
        id_idx = select_top_diff_tcga(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0)
        tn_details.append({'pair_type': 'TN', 'cancer': cancer,
                          'omega': r['omega'], 'kn': r['kn'], 'kf': r['kf']})
        if (idx + 1) % 500 == 0:
            print(f'    TN: {idx+1}/{len(tn_pairs)}', end='\r')
    print(f'    TN: {len(tn_pairs)}/{n_tn_total} done')

    tt_vals = np.array([d['omega'] for d in tt_details])
    nn_vals = np.array([d['omega'] for d in nn_details])
    tn_vals = np.array([d['omega'] for d in tn_details])
    baseline = (np.mean(tt_vals) + np.mean(nn_vals)) / 2
    _, p_val = mannwhitneyu(tn_vals, np.concatenate([tt_vals, nn_vals]), alternative='less')

    print(f'    omega_TT: mean={np.mean(tt_vals):.1f}, median={np.median(tt_vals):.1f}')
    print(f'    omega_NN: mean={np.mean(nn_vals):.1f}, median={np.median(nn_vals):.1f}')
    print(f'    omega_TN: mean={np.mean(tn_vals):.1f}, median={np.median(tn_vals):.1f}')
    print(f'    TN/baseline: {np.mean(tn_vals)/baseline:.2f}x, p={p_val:.2e}')

    df_details = pd.DataFrame(tt_details + nn_details + tn_details)
    df_details.to_csv(RESULTS_DIR / f'phase34_v2_{cancer}_pairs.csv', index=False)
    all_pair_details.append(df_details)
    all_summary_tcga.append({
        'Project': cancer, 'n_Tumor': n_t, 'n_Normal': n_n,
        'n_Genes': len(genes), 'n_HK': len(hk_arr),
        'omega_TT_mean': f'{np.mean(tt_vals):.1f}',
        'omega_NN_mean': f'{np.mean(nn_vals):.1f}',
        'omega_TN_mean': f'{np.mean(tn_vals):.1f}',
        'TN_Baseline': f'{np.mean(tn_vals)/baseline:.2f}x',
        'p_value': f'{p_val:.2e}',
    })
""")

# CELL 20
code(r"""# ── Part 3.4: TCGA Save Results ─────────────────────────────────
df_all_tcga = pd.concat(all_pair_details, ignore_index=True)
df_all_tcga.to_csv(RESULTS_DIR / 'phase34_v2_all_pairs.csv', index=False)

df_summary_tcga = pd.DataFrame(all_summary_tcga)
print('\n' + df_summary_tcga.to_string(index=False))
df_summary_tcga.to_csv(RESULTS_DIR / 'phase34_v2_summary.csv', index=False)

for pt in ['TT', 'NN', 'TN']:
    sub = df_all_tcga[df_all_tcga['pair_type'] == pt]
    print(f'  Combined {pt}: n={len(sub)}, mean={sub["omega"].mean():.1f}, median={sub["omega"].median():.1f}')

print('\nPart 3 COMPLETE.')
""")

# ==============================
# PART 4: Siletti Brain
# ==============================
md("""---
# Part 4: Siletti Brain Atlas

**Dataset**: Siletti et al. (Science 2023) non-neuronal nuclei  
**WARNING: Requires >= 16 GB RAM (>= 32 GB recommended)**  
**Input**: `data/brain/Nonneurons.h5ad` (~4.4 GB)  
**Output**: `results/brain_siletti_*_v3.csv`
""")

# CELL 21
code(r"""# ── Part 4.1: Load Siletti Nonneurons ───────────────────────────
SILETTI_PATH = DATA_DIR / 'brain' / 'Nonneurons.h5ad'
if not SILETTI_PATH.exists():
    print(f'  ERROR: {SILETTI_PATH} not found!')
    print('  Download from: https://zenodo.org/records/7865491')
    print('  Place as: data/brain/Nonneurons.h5ad')
    sys.exit(1)

adata_brain = sc_mod.read_h5ad(SILETTI_PATH)
print(f'  Shape: {adata_brain.shape}')

ct_col = 'supercluster_term'
region_col = 'roi'
print(f'  Cell types: {sorted(adata_brain.obs[ct_col].unique())}')
print(f'  Brain regions: {adata_brain.obs[region_col].nunique()}')
""")

# CELL 22
code(r"""# ── Part 4.2: HK Genes + Filtering ──────────────────────────────
hk_df_brain = pd.read_csv(HK_FILE, sep=';', engine='python')
hk_human_genes_brain = set(hk_df_brain['Human'].dropna().astype(str))

gene_names_brain = adata_brain.var_names.tolist()
hk_indices_brain = []
for i, gene_symbol in enumerate(adata_brain.var['Gene']):
    if pd.notna(gene_symbol) and gene_symbol in hk_human_genes_brain:
        hk_indices_brain.append(i)
hk_indices_brain = np.array(hk_indices_brain, dtype=int)
print(f'  Matched HK genes: {len(hk_indices_brain)}/{len(hk_human_genes_brain)}')
assert len(hk_indices_brain) >= 100, 'ERROR: Too few HK genes matched!'

MIN_NUCLEI_PER_GROUP = 20
MIN_NUCLEI_PER_REGION = 50
groups = adata_brain.obs.groupby([region_col, ct_col]).size().reset_index(name='count')
groups_ok = groups[groups['count'] >= MIN_NUCLEI_PER_GROUP]
print(f'  Groups >= {MIN_NUCLEI_PER_GROUP}: {len(groups_ok)} (from {len(groups)})')
region_counts = adata_brain.obs[region_col].value_counts()
regions_ok = region_counts[region_counts >= MIN_NUCLEI_PER_REGION].index
groups_ok = groups_ok[groups_ok[region_col].isin(regions_ok)]
print(f'  Groups passing filters: {len(groups_ok)}')
cts_present = sorted(groups_ok[ct_col].unique())
""")

# CELL 23
code(r"""# ── Part 4.3: Pseudobulk from Raw Counts ────────────────────────
pseudobulk_raw = {}
pseudobulk_meta = []
for _, row in groups_ok.iterrows():
    region = row[region_col]
    ct = row[ct_col]
    mask = (adata_brain.obs[region_col] == region) & (adata_brain.obs[ct_col] == ct)
    group_adata = adata_brain[mask]
    X = group_adata.X
    if hasattr(X, 'toarray'):
        pb = np.array(X.mean(axis=0)).flatten()
    else:
        pb = np.mean(X, axis=0)
    pseudobulk_raw[(ct, region)] = pb
    pseudobulk_meta.append({'cell_type': ct, 'region': region, 'n_nuclei': row['count']})
print(f'  Pseudobulks: {len(pseudobulk_raw)}')

pseudobulk_norm = {}
for key, pb in pseudobulk_raw.items():
    total = pb.sum()
    pb_norm = pb / total * 1e4 if total > 0 else pb
    pseudobulk_norm[key] = np.log1p(pb_norm)
print(f'  Normalized: {len(pseudobulk_norm)}')

del adata_brain; gc.collect()
print('  Freed raw adata.')
""")

# CELL 24
code(r"""# ── Part 4.4: Compute Omega (global HK k_n + per-pair k_f) ─────
N_GENES_BRAIN = len(gene_names_brain)
non_hk_mask_brain = np.ones(N_GENES_BRAIN, dtype=bool)
for idx in hk_indices_brain:
    if idx < N_GENES_BRAIN:
        non_hk_mask_brain[idx] = False
non_hk_indices_brain = np.where(non_hk_mask_brain)[0]

ct_to_regions = {}
for meta in pseudobulk_meta:
    ct = meta['cell_type']
    r = meta['region']
    ct_to_regions.setdefault(ct, [])
    if r not in ct_to_regions[ct]:
        ct_to_regions[ct].append(r)

total_pairs_brain = 0
for ct, regions in ct_to_regions.items():
    total_pairs_brain += len(regions) * (len(regions) - 1) // 2
print(f'  Total pairs: {total_pairs_brain}')

pair_results_brain = []
pair_idx = 0
for ct, regions in ct_to_regions.items():
    n_r = len(regions)
    print(f'  {ct}: {n_r} regions, {n_r*(n_r-1)//2} pairs')
    for i in range(n_r):
        for j in range(i + 1, n_r):
            r_i, r_j = regions[i], regions[j]
            pb_i = pseudobulk_norm[(ct, r_i)]
            pb_j = pseudobulk_norm[(ct, r_j)]
            hk_i = pb_i[hk_indices_brain]
            hk_j = pb_j[hk_indices_brain]
            kn_val = js_divergence(hk_i, hk_j)
            abs_diff = np.abs(pb_i - pb_j)
            abs_diff_non_hk = abs_diff[non_hk_mask_brain]
            top_n = min(N_TOP_KF, len(abs_diff_non_hk))
            top_local = np.argpartition(abs_diff_non_hk, -top_n)[-top_n:]
            top_local = top_local[np.argsort(abs_diff_non_hk[top_local])[::-1]]
            top_global = non_hk_indices_brain[top_local]
            kf_val = js_divergence(pb_i[top_global], pb_j[top_global])
            omega_val = kf_val / kn_val if kn_val > 0 else float('inf')
            pair_results_brain.append({
                'cell_type': ct, 'region_a': r_i, 'region_b': r_j,
                'omega': omega_val, 'kn': kn_val, 'kf': kf_val,
            })
            pair_idx += 1
            if pair_idx % 5000 == 0:
                print(f'    Progress: {pair_idx}/{total_pairs_brain}')
print(f'  Complete: {len(pair_results_brain)} pairs')
""")

# CELL 25
code(r"""# ── Part 4.5: Per-CT Omega Summary ──────────────────────────────
pairs_brain_df = pd.DataFrame(pair_results_brain)
ct_summary_brain = []
for ct in cts_present:
    ct_pairs = pairs_brain_df[pairs_brain_df['cell_type'] == ct]
    n_pairs = len(ct_pairs)
    n_regions_ct = len(ct_to_regions.get(ct, []))
    omega_mean = ct_pairs['omega'].mean()
    n_nuclei_ct = sum(m['n_nuclei'] for m in pseudobulk_meta if m['cell_type'] == ct)
    ct_summary_brain.append({
        'cell_type': ct, 'n_regions': n_regions_ct, 'n_pairs': n_pairs,
        'n_nuclei': n_nuclei_ct,
        'omega_mean': round(omega_mean, 2),
        'omega_median': round(ct_pairs['omega'].median(), 2),
        'omega_std': round(ct_pairs['omega'].std(), 2),
        'omega_min': round(ct_pairs['omega'].min(), 2),
        'omega_max': round(ct_pairs['omega'].max(), 2),
    })
    print(f'  {ct}: n={n_regions_ct}, mean={omega_mean:.2f}')

ct_summary_brain_df = pd.DataFrame(ct_summary_brain).sort_values('omega_mean')
ct_min = ct_summary_brain_df.iloc[0]
ct_max = ct_summary_brain_df.iloc[-1]
g = ct_max['omega_mean'] / ct_min['omega_mean'] if ct_min['omega_mean'] > 0 else float('inf')
print(f'\n  Omega gradient: {ct_min["cell_type"]} ({ct_min["omega_mean"]}) -> {ct_max["cell_type"]} ({ct_max["omega_mean"]}), fold={g:.2f}')
""")

# CELL 26
code(r"""# ── Part 4.6: Multiplicative Migration Detection ─────────────────
grand_mean = pairs_brain_df['omega'].mean()
mu_ct = {}
for ct in cts_present:
    mu_ct[ct] = pairs_brain_df[pairs_brain_df['cell_type'] == ct]['omega'].mean()

all_region_pairs = set()
for _, row in pairs_brain_df.iterrows():
    rp = tuple(sorted([row['region_a'], row['region_b']]))
    all_region_pairs.add(rp)

mu_rp = {}
for rp in all_region_pairs:
    mask = ((pairs_brain_df['region_a'] == rp[0]) & (pairs_brain_df['region_b'] == rp[1])) | \
           ((pairs_brain_df['region_a'] == rp[1]) & (pairs_brain_df['region_b'] == rp[0]))
    subset = pairs_brain_df[mask]
    if len(subset) > 0:
        mu_rp[rp] = subset['omega'].mean()

migration_results = []
for _, row in pairs_brain_df.iterrows():
    ct = row['cell_type']
    rp = tuple(sorted([row['region_a'], row['region_b']]))
    expected = mu_ct[ct] * mu_rp[rp] / grand_mean if ct in mu_ct and rp in mu_rp else grand_mean
    residual = row['omega'] / expected if expected > 0 else 1.0
    tier = 'Strong' if residual < 0.3 else 'Moderate' if residual < 0.5 else 'Weak' if residual < 0.75 else 'None'
    migration_results.append({
        'cell_type': ct, 'region_a': row['region_a'], 'region_b': row['region_b'],
        'omega': row['omega'], 'expected_omega': round(expected, 2),
        'residual': round(residual, 4), 'tier': tier,
    })

migration_df = pd.DataFrame(migration_results)
for tier in ['Strong', 'Moderate', 'Weak']:
    n = len(migration_df[migration_df['tier'] == tier])
    print(f'  {tier}: {n} ({n/len(migration_df)*100:.1f}%)')

strong_by_ct = migration_df[migration_df['tier'] == 'Strong']['cell_type'].value_counts()
for ct in cts_present:
    print(f'    {ct}: {strong_by_ct.get(ct, 0)}')
""")

# CELL 27
code(r"""# ── Part 4.7: Save Brain Results ────────────────────────────────
pairs_brain_df.to_csv(RESULTS_DIR / 'brain_siletti_omega_pairs_v3.csv', index=False)
migration_df.to_csv(RESULTS_DIR / 'brain_siletti_migration_candidates_v3.csv', index=False)
ct_summary_brain_df.to_csv(RESULTS_DIR / 'brain_siletti_ct_summary_v3.csv', index=False)
print('  Saved: brain_siletti_omega_pairs_v3.csv')
print('  Saved: brain_siletti_migration_candidates_v3.csv')
print('  Saved: brain_siletti_ct_summary_v3.csv')
print('\nPart 4 COMPLETE.')
""")

# ==============================
# PART 5: Summary
# ==============================
md("""---
# Part 5: Results Summary & Cross-Validation

Cross-validate computed results to ensure numerical reproducibility.
""")

code(r"""# ── Part 5: Summary ────────────────────────────────────────────
print('=' * 60)
print('CKI COMPLETE REPRODUCIBILITY NOTEBOOK — DONE!')
print('=' * 60)
print(f'\nAll results saved to: {RESULTS_DIR}')
print('\nOutput files:')
for f in sorted(RESULTS_DIR.glob('*.csv')):
    if any(k in f.name for k in ['brain', 'phase', 'full_matrix', 'mouse']):
        print(f'  {f.name} ({f.stat().st_size:,} bytes)')

print('\nSummary:')
print(f'  Part 1 (Mouse): 15 pilot + 703 full pairs')
print(f'  Part 2 (Human): {n_ct_human} CTs, {total_pairs_human} pairs')
print(f'  Part 3 (TCGA): {len(usable_cancers)} cancers, {len(df_all_tcga)} pairs')
print(f'  Part 4 (Brain): {total_pairs_brain} cross-region pairs')
""")

# ==============================
# Assemble and write
# ==============================
nb.cells = cells
out_path = 'notebooks/CKI_Reproducibility.ipynb'
nbf.write(nb, out_path)
print(f'Notebook written to {out_path}')
print(f'Total cells: {len(cells)}')
