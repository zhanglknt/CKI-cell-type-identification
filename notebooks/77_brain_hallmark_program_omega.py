"""
CKI Brain Hallmark Program Omega Decomposition (B task)
========================================================
Decomposes the brain region-pair omega signal into named Hallmark
programs, replacing the data-driven top-200 k_f gene set with
externally defined programs (hallmark_2020.gmt).

For each cell type (Siletti Nonneurons, 08c v3 pipeline):
  1. Same reduced gene set as 08c: HRT HK (1,115) + top-5000 HVG (non-HK)
  2. Same region x cell-type groups (MIN_NUCLEI=20, MIN_REGION_N=50)
  3. Same pseudobulk: mean over cells -> norm to 1e4 -> log1p
  4. Per pair: kn = JS on HK (identical to 08c);
     per program p: kf_p = JS on (program genes ∩ reduced non-HK),
     omega_p = kf_p / kn
  5. Empirical null: size-bucketed random non-HK gene sets
     (bucket = round(size/10)*10, N_NULL replicates per bucket)
  6. BH-FDR across all CT x program tests

Validation: reproduces data-driven top-200 omega per pair and
cross-checks against results/brain_siletti_v4_omega_pairs.csv.

Vectorization: JS via entropy identity
  JS(p,q) = H((p+q)/2) - (H(p)+H(q))/2   (base-2)
with softmax (max-subtracted, eps=1e-9) exactly matching
cki.utils.ensure_probability_distribution(mode="softmax").

Outputs:
  results/brain_hallmark_program_omega.csv   (CT x program summary)
  results/brain_hallmark_program_pairs.npz   (per-pair omega_p arrays)
  results/brain_hallmark_program_pairs_index.csv (pair labels)
  results/brain_hallmark_program_report.md
"""

import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)

import numpy as np
import pandas as pd
import scanpy as sc
import h5py
from scipy.sparse import issparse, csr_matrix
from pathlib import Path

from cki.core import js_divergence
from cki.bootstrap import benjamini_hochberg


# === extract_csr_from_backed: verbatim copy from 08c_brain_bootstrap_v3.py ===
def extract_csr_from_backed(h5_path, cell_indices, keep_global, n_genes_total,
                            chunk_size=20000):
    n_cells = len(cell_indices)
    n_keep = len(keep_global)
    if n_cells == 0:
        return csr_matrix((0, n_keep), dtype=np.float32)

    gene_map = np.full(n_genes_total, -1, dtype=np.int32)
    gene_map[keep_global] = np.arange(n_keep, dtype=np.int32)

    sort_order = np.argsort(cell_indices, kind='stable')
    sorted_cells = cell_indices[sort_order]
    unsort = np.empty(n_cells, dtype=np.int64)
    unsort[sort_order] = np.arange(n_cells)

    new_data_list = [None] * n_cells
    new_idx_list = [None] * n_cells
    cell_nnz_sorted = np.zeros(n_cells, dtype=np.int64)

    with h5py.File(h5_path, 'r') as f:
        X = f['X']
        indptr_full = X['indptr'][:]
        n_chunks = (n_cells + chunk_size - 1) // chunk_size
        for chunk_i in range(n_chunks):
            chunk_start = chunk_i * chunk_size
            chunk_end = min(chunk_start + chunk_size, n_cells)
            chunk_cells = sorted_cells[chunk_start:chunk_end]
            data_start = int(indptr_full[chunk_cells[0]])
            data_end = int(indptr_full[chunk_cells[-1] + 1])
            if data_end > data_start:
                chunk_indices = X['indices'][data_start:data_end]
                chunk_data = X['data'][data_start:data_end]
                chunk_mapped = gene_map[chunk_indices]
                chunk_keep = chunk_mapped >= 0
            else:
                chunk_mapped = np.array([], dtype=np.int32)
                chunk_keep = np.array([], dtype=bool)
                chunk_data = np.array([], dtype=X['data'].dtype)
            # Per-cell filtering from in-memory arrays
            for ci in range(chunk_start, chunk_end):
                orig_pos = int(sort_order[ci])   # FIX (was unsort[ci])
                global_row = int(sorted_cells[ci])
                r_start = int(indptr_full[global_row]) - data_start
                r_end = int(indptr_full[global_row + 1]) - data_start

                if r_start == r_end:
                    continue  # cell_nnz_sorted[ci] stays 0

                keep_mask = chunk_keep[r_start:r_end]
                n_kept = int(keep_mask.sum())
                cell_nnz_sorted[ci] = n_kept

                if n_kept > 0:
                    new_data_list[orig_pos] = chunk_data[r_start:r_end][keep_mask]
                    new_idx_list[orig_pos] = chunk_mapped[r_start:r_end][keep_mask]

            if n_chunks > 5 and (chunk_i + 1) % 5 == 0:
                print(f"      Extraction chunk {chunk_i+1}/{n_chunks} "
                      f"({chunk_end}/{n_cells} sorted cells)")

    # Build indptr: map nnz counts from sorted order to original order, then cumsum
    cell_nnz_orig = np.zeros(n_cells, dtype=np.int64)
    cell_nnz_orig[sort_order] = cell_nnz_sorted   # FIX (was unsort)
    new_indptr = np.zeros(n_cells + 1, dtype=np.int64)
    np.cumsum(cell_nnz_orig, out=new_indptr[1:])
    nnz = int(new_indptr[-1])
    if nnz == 0:
        return csr_matrix((n_cells, n_keep), dtype=np.float32)

    all_data = [d for d in new_data_list if d is not None]
    all_idx = [d for d in new_idx_list if d is not None]
    new_data = np.concatenate(all_data)
    new_indices_arr = np.concatenate(all_idx)

    return csr_matrix((new_data, new_indices_arr, new_indptr), shape=(n_cells, n_keep))


# === Vectorized pairwise JS (entropy identity, softmax like cki.utils) ===
_EPS = 1e-9

def softmax_rows(X):
    """Row-wise softmax matching ensure_probability_distribution(mode='softmax')."""
    X = X - X.max(axis=1, keepdims=True)
    E = np.exp(X)
    return E / (E.sum(axis=1, keepdims=True) + _EPS)


def row_entropy(P):
    """Row-wise Shannon entropy (base-2), 0*log0 = 0."""
    with np.errstate(divide='ignore', invalid='ignore'):
        L = np.where(P > 0, np.log2(P), 0.0)
    return -np.einsum('ij,ij->i', P, L)


def pairwise_js(PB, idx, block=16):
    """
    Pairwise JS divergence (base-2) between all rows of PB restricted to
    columns idx, using softmax normalization per row subset.
    Returns condensed vector of length n*(n-1)//2 in (i<j, i outer) order.
    """
    X = np.asarray(PB[:, idx], dtype=np.float64)  # match js_divergence float64 path
    P = softmax_rows(X)
    n = P.shape[0]
    h = row_entropy(P)
    out = np.empty(n * (n - 1) // 2, dtype=np.float64)
    w = 0
    for i0 in range(0, n - 1, block):
        i1 = min(i0 + block, n - 1)
        for i in range(i0, i1):
            M = 0.5 * (P[i:i + 1] + P[i + 1:])
            hm = row_entropy(M)
            js = hm - 0.5 * (h[i] + h[i + 1:])
            k = n - i - 1
            out[w:w + k] = js
            w += k
    return out


# === Config (identical to 08c) ===
SILETTI_PATH = BRAIN_FILE
HK_FILE_REF = HK_FILE
RANDOM_SEED = 42
MIN_NUCLEI = 20
MIN_REGION_N = 50
N_TOP_KF = 200
N_HVG = 5000
N_NULL = 2000         # random gene-set replicates per size bucket
MIN_PROG_GENES = 20   # minimum program overlap with reduced non-HK set

ct_col = "supercluster_term"
region_col = "roi"

GMT_PATH = DATA_DIR / "tcga" / "hallmark_2020.gmt"
OUT_CSV = Path("results/brain_hallmark_program_omega.csv")
OUT_NPZ = Path("results/brain_hallmark_program_pairs.npz")
OUT_IDX = Path("results/brain_hallmark_program_pairs_index.csv")
OUT_MD = Path("results/brain_hallmark_program_report.md")
REF_PAIRS = Path("results/brain_bs_null_observed_pairs.csv")  # 31,764-pair authoritative

rng = np.random.RandomState(RANDOM_SEED)

# ============================================================
# 1. Load HK genes + Hallmark programs
# ============================================================
print("=" * 60)
print("1. Loading HK genes and Hallmark programs...")
print("=" * 60)
hk_df = pd.read_csv(HK_FILE_REF, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))
print(f"  HRT Atlas: {len(hk_human)} human HK genes")

programs = {}
with open(GMT_PATH, "r", encoding="utf-8") as fh:
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        name = parts[0].strip()
        genes = [g.strip() for g in parts[2:] if g.strip()]
        if name and genes:
            programs[name] = genes
print(f"  Hallmark programs loaded: {len(programs)}")

# ============================================================
# 2. Open Siletti backed, reduced gene set (same as 08c)
# ============================================================
print("\n" + "=" * 60)
print("2. Opening Siletti Nonneurons.h5ad (backed='r')...")
print("=" * 60)
adata = sc.read_h5ad(SILETTI_PATH, backed='r')
print(f"  Shape: {adata.shape}")
N_GENES = adata.n_vars
N_CELLS = adata.n_obs

gene_symbols = adata.var["Gene"].tolist()
hk_global = []
for i, sym in enumerate(gene_symbols):
    if pd.notna(sym) and sym in hk_human:
        hk_global.append(i)
hk_global = np.array(sorted(set(hk_global)), dtype=int)
print(f"  Matched HK genes: {len(hk_global)}")

print("\n3. Computing global gene means for HVG selection...")
t0 = time.time()
BATCH_SIZE = 50000
gene_sums = np.zeros(N_GENES, dtype=np.float64)
for start in range(0, N_CELLS, BATCH_SIZE):
    end = min(start + BATCH_SIZE, N_CELLS)
    X_batch = adata[start:end].X
    if issparse(X_batch):
        gene_sums += np.array(X_batch.sum(axis=0)).flatten()
    else:
        gene_sums += X_batch.sum(axis=0)
gene_means = gene_sums / N_CELLS
print(f"  Computed means for {N_GENES} genes in {time.time()-t0:.0f}s")

non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_global] = False
non_hk_means = gene_means.copy()
non_hk_means[~non_hk_mask] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]

keep_global = np.sort(np.union1d(hk_global, hvg_global))
N_KEEP = len(keep_global)
is_hk_in_keep = np.isin(keep_global, hk_global)
hk_in_reduced = np.where(is_hk_in_keep)[0]
non_hk_in_reduced = np.where(~is_hk_in_keep)[0]
print(f"  Reduced gene set: {N_KEEP} (HK={len(hk_in_reduced)} + non-HK={len(non_hk_in_reduced)})")

# Symbol -> reduced-position map (non-HK only), for program overlap
sym_to_reduced = {}
for pos in non_hk_in_reduced:
    sym = gene_symbols[keep_global[pos]]
    if pd.notna(sym):
        sym_to_reduced.setdefault(sym, []).append(pos)

prog_sets = {}
for name, genes in programs.items():
    idx = []
    for g in genes:
        idx.extend(sym_to_reduced.get(g, []))
    idx = np.array(sorted(set(idx)), dtype=int)
    if len(idx) >= MIN_PROG_GENES:
        prog_sets[name] = idx
print(f"  Programs with >= {MIN_PROG_GENES} genes in reduced non-HK set: "
      f"{len(prog_sets)}/{len(programs)}")
for name in sorted(prog_sets):
    print(f"    {name}: {len(prog_sets[name])} genes")

# ============================================================
# 4. Groups (identical filter to 08c)
# ============================================================
print("\n" + "=" * 60)
print("4. Filtering groups...")
print("=" * 60)
groups = adata.obs.groupby([region_col, ct_col]).size().reset_index(name="count")
groups_ok = groups[groups["count"] >= MIN_NUCLEI]
region_counts = adata.obs[region_col].value_counts()
regions_ok = region_counts[region_counts >= MIN_REGION_N].index
groups_ok = groups_ok[groups_ok[region_col].isin(regions_ok)]
cts_present = sorted(groups_ok[ct_col].unique())
ct_to_regions = {}
for _, row in groups_ok.iterrows():
    ct_to_regions.setdefault(row[ct_col], [])
    if row[region_col] not in ct_to_regions[row[ct_col]]:
        ct_to_regions[row[ct_col]].append(row[region_col])
print(f"  Cell types: {len(cts_present)}: {cts_present}")

# ============================================================
# 5. Per-CT: extract -> pseudobulks -> program omega + nulls
# ============================================================
print("\n" + "=" * 60)
print("5. Per-CT program decomposition")
print("=" * 60)

STR_H5AD = str(SILETTI_PATH)
summary_rows = []
npz_store = {}
pair_index_rows = []
xcheck_rows = []

ref = pd.read_csv(REF_PAIRS) if REF_PAIRS.exists() else None
ref_lookup = {}
if ref is not None:
    for ct, r1, r2, om in ref[["cell_type", "region_a", "region_b",
                               "omega"]].itertuples(index=False):
        ref_lookup[(ct, r1, r2)] = om
    print(f"  Reference pairs loaded: {len(ref_lookup)} (omega-only)")

for ct in cts_present:
    regions = ct_to_regions[ct]
    n_r = len(regions)
    n_pairs = n_r * (n_r - 1) // 2
    if n_pairs < 5:
        print(f"\n  {ct}: SKIP ({n_pairs} pairs)")
        continue
    t_ct = time.time()
    print(f"\n  --- {ct} ({n_r} regions, {n_pairs} pairs) ---")

    ct_mask = (adata.obs[ct_col] == ct).values
    region_mask = np.isin(adata.obs[region_col].values, regions)
    ct_global_indices = np.where(ct_mask & region_mask)[0]
    # NB: .values is a pandas Categorical — np.argsort would sort by category
    # codes, NOT lexicographically; cast to str so block order == sorted(regions)
    region_of_cell = np.asarray(
        adata.obs[region_col].values[ct_global_indices]).astype(str)
    sort_idx = np.argsort(region_of_cell)
    sorted_region = region_of_cell[sort_idx]
    ct_global_sorted = ct_global_indices[sort_idx]

    t0 = time.time()
    X_ct_sparse = extract_csr_from_backed(STR_H5AD, ct_global_sorted,
                                          keep_global, N_GENES)
    print(f"    Extracted {X_ct_sparse.shape[0]} cells x {N_KEEP} genes "
          f"({time.time()-t0:.0f}s)")

    region_order = sorted(regions)
    region_sizes, region_starts, cum = {}, {}, 0
    for region in region_order:
        n = int(np.sum(sorted_region == region))
        region_sizes[region] = n
        region_starts[region] = cum
        cum += n

    # Pseudobulk matrix PB: n_r x N_KEEP (mean -> norm 1e4 -> log1p)
    PB = np.zeros((n_r, N_KEEP), dtype=np.float32)
    for ri, region in enumerate(region_order):
        s, e = region_starts[region], region_starts[region] + region_sizes[region]
        pb_raw = np.array(X_ct_sparse[s:e].mean(axis=0)).flatten()
        total = pb_raw.sum()
        PB[ri] = np.log1p(pb_raw / total * 1e4) if total > 0 else pb_raw
    del X_ct_sparse
    gc.collect()

    # kn per pair (HK) + data-driven top-200 omega (cross-check vs 08c/v4)
    kn_pairs = pairwise_js(PB, hk_in_reduced)
    kf200 = np.empty(n_pairs)
    pair_labels = []
    w = 0
    for i in range(n_r):
        for j in range(i + 1, n_r):
            d = np.abs(PB[i] - PB[j])[non_hk_in_reduced]
            top = min(N_TOP_KF, len(d))
            tl = np.argpartition(d, -top)[-top:]
            genes = non_hk_in_reduced[tl]
            kf200[w] = js_divergence(PB[i][genes], PB[j][genes])
            pair_labels.append((region_order[i], region_order[j]))
            w += 1
    omega200 = kf200 / np.where(kn_pairs > 0, kn_pairs, np.nan)
    npz_store[f"{ct}||__kn__"] = kn_pairs.astype(np.float64)
    npz_store[f"{ct}||__kf200__"] = kf200.astype(np.float64)
    npz_store[f"{ct}||__omega200__"] = omega200.astype(np.float64)
    print(f"    Data-driven top-200: mean omega={np.nanmean(omega200):.2f} "
          f"(kn mean={kn_pairs.mean():.6f})")

    # cross-check against authoritative 31,764-pair file (omega only)
    if ref_lookup:
        diffs = []
        for (r1, r2), om in zip(pair_labels, omega200):
            key = (ct, r1, r2)
            if key in ref_lookup:
                diffs.append(abs(om - ref_lookup[key]))
        if diffs:
            d = np.array(diffs)
            xcheck_rows.append((ct, len(diffs), d.max()))
            print(f"    X-check vs 31,764-pair file ({len(diffs)} pairs): "
                  f"max|d_omega|={d.max():.3e}")

    # Programs
    buckets = {}
    for name in sorted(prog_sets):
        idx = prog_sets[name]
        kf_p = pairwise_js(PB, idx)
        om_p = kf_p / np.where(kn_pairs > 0, kn_pairs, np.nan)
        npz_store[f"{ct}||{name}"] = om_p.astype(np.float32)

        b = int(round(len(idx) / 10.0) * 10)
        if b not in buckets:
            nulls = np.empty(N_NULL)
            pool = non_hk_in_reduced
            size = min(max(b, 10), len(pool))
            for r_ in range(N_NULL):
                ridx = rng.choice(pool, size=size, replace=False)
                kf_n = pairwise_js(PB, ridx)
                nulls[r_] = np.nanmean(kf_n / np.where(kn_pairs > 0,
                                                         kn_pairs, np.nan))
            buckets[b] = nulls
        null = buckets[b]
        obs = float(np.nanmean(om_p))
        p_emp = float((1 + np.sum(null >= obs)) / (1 + len(null)))
        summary_rows.append({
            "cell_type": ct, "program": name, "n_genes": len(idx),
            "n_pairs": n_pairs, "mean_omega": obs,
            "mean_kf": float(np.mean(kf_p)), "mean_kn": float(kn_pairs.mean()),
            "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "null_n": len(null), "null_bucket_size": b,
            "p_emp": p_emp,
        })
    for (r1, r2) in pair_labels:
        pair_index_rows.append((ct, r1, r2))
    print(f"    Programs done ({len(prog_sets)}), "
          f"null buckets: {sorted(buckets)}, {time.time()-t_ct:.0f}s total")

# ============================================================
# 6. Save + BH-FDR + report
# ============================================================
print("\n" + "=" * 60)
print("6. Saving outputs + BH-FDR")
print("=" * 60)

df = pd.DataFrame(summary_rows)
df["q_bh"] = benjamini_hochberg(df["p_emp"].values)
df = df.sort_values(["cell_type", "q_bh", "p_emp"])
df.to_csv(OUT_CSV, index=False)
print(f"  Saved {OUT_CSV} ({len(df)} rows)")

np.savez_compressed(OUT_NPZ, **npz_store)
pd.DataFrame(pair_index_rows, columns=["cell_type", "region_a",
                                       "region_b"]).to_csv(OUT_IDX, index=False)
print(f"  Saved {OUT_NPZ} ({len(npz_store)} arrays), {OUT_IDX}")

n_sig = int((df["q_bh"] < 0.05).sum())
lines = [
    "# Brain Hallmark Program Omega Decomposition",
    "",
    f"- Pipeline: 08c v3 identical (HK={len(hk_in_reduced)}, HVG=5000, "
    f"MIN_NUCLEI={MIN_NUCLEI}, MIN_REGION_N={MIN_REGION_N})",
    f"- Programs tested: {len(prog_sets)} (>= {MIN_PROG_GENES} genes in reduced non-HK set)",
    f"- Null: {N_NULL} size-bucketed random non-HK gene sets (bucket=round(size/10)*10)",
    f"- Tests: {len(df)} CT x program; significant q<0.05: {n_sig}",
    "",
    "## Cross-check vs brain_bs_null_observed_pairs.csv (data-driven top-200)",
    "",
    "| cell_type | n_pairs_matched | max|d_omega| |",
    "|---|---|---|",
]
for ct, n, do in xcheck_rows:
    lines.append(f"| {ct} | {n} | {do:.2e} |")
lines += ["", "## Top hits (q<0.05, up to 30)", "",
          "| cell_type | program | n_genes | mean_omega | null_mean | p_emp | q_bh |",
          "|---|---|---|---|---|---|---|"]
for _, r in df[df["q_bh"] < 0.05].head(30).iterrows():
    lines.append(f"| {r.cell_type} | {r.program} | {r.n_genes} | "
                 f"{r.mean_omega:.2f} | {r.null_mean:.2f} | {r.p_emp:.4g} | {r.q_bh:.3g} |")
if n_sig == 0:
    lines.append("(none)")
OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"  Saved {OUT_MD}")
print(f"\nDONE. Significant (q<0.05): {n_sig}/{len(df)}")
