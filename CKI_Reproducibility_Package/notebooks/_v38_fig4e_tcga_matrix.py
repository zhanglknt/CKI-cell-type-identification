#!/usr/bin/env python3
"""
_v38_fig4e_tcga_matrix.py

Compute the 5 x 5 TCGA cross-cancer tumor-pseudobulk CKI omega matrix for
Figure 4 Panel E.

Each off-diagonal entry (i, j) is the CKI omega between the mean tumor
pseudobulk profiles of cancers[i] and cancers[j].  Diagonals are filled from
the median within-cancer Tumor-Tumor omega in the authoritative
results/phase34_v2_TCGA-<cancer>_pairs.csv files.

Output: results/figures_final/fig4e_tcga_cross_cancer_matrix.npz
  - omega : (5, 5) float array
  - cancers : (5,) str array

v38 fix: Panel E was previously left blank because this matrix did not exist.
"""
import sys, os, io, warnings, time

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path

from _paths import TCGA_FILE, PROBEMAP_FILE, HK_FILE, RESULTS_DIR
from cki.core import compute_omega

warnings.filterwarnings("ignore")

# === Config ===
RANDOM_SEED = 42
N_TOP_KF = 200
MIN_GENE_MEAN_TPM = 0.5
CANCERS = ["BRCA", "KIRC", "LIHC", "LUAD", "LUSC"]

# === TSS -> Project mapping (mirrors 06_phase34_v2.py) ===
TSS_TO_PROJECT = {}
for c in ["A1","A2","A7","A8","AN","AO","AQ","AR","B6","BH","C8","D8",
          "E2","EW","GI","WT","XX","E9","GM","HN","JL","LD","LL","MS",
          "OL","PE","PL","S3","UL","V7","W8","WV"]:
    TSS_TO_PROJECT[c] = "TCGA-BRCA"
for c in ["05","35","38","44","49","50","55","64","67","73","75","78",
          "86","91","93","97","J2","L3","L4","M1","MP","MT","N1","N6",
          "O1","S2","TR","TV","TQ","NJ","KN","LF"]:
    TSS_TO_PROJECT[c] = "TCGA-LUAD"
for c in ["18","21","22","33","34","37","39","43","51","52","56","60",
          "63","66","68","70","77","85","90","92","94","96","98","CC",
          "L5","N2","NK","Q1","IE","IF","IG"]:
    TSS_TO_PROJECT[c] = "TCGA-LUSC"
for c in ["BC","DD","ED","EP","ES","FV","FY","G3","GJ","HP","HU","K7",
          "KR","LG","NI","O8","PD","QN","RC","RG","T6","UB","WQ","XR",
          "YA","ZP","ZS","MI","F5"]:
    TSS_TO_PROJECT[c] = "TCGA-LIHC"
for c in ["A3","AK","AL","AY","B0","B1","B2","B3","B4","B8","BP","BW",
          "CJ","CW","CZ","DV","DX","EU","GK","HE","I6","K6","KL","MM",
          "MW","P4","Q2","RG","UZ","V5","XM","YE"]:
    TSS_TO_PROJECT[c] = "TCGA-KIRC"


def load_hk_mapping():
    pm = pd.read_csv(PROBEMAP_FILE, sep="\t", header=None, usecols=[0, 1])
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
    return ens_to_symbol, symbol_to_ens, hk_human


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1.0
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)


def main():
    t0 = time.time()
    print("=" * 60)
    print("v38 Figure 4E: TCGA cross-cancer tumor-pseudobulk omega matrix")
    print("=" * 60)

    ens_to_symbol, symbol_to_ens, hk_human = load_hk_mapping()
    print(f"  HK symbols: {len(hk_human)}")

    # Parse header to identify tumor samples for the 5 cancers
    print("\n1. Identifying tumor samples from TCGA header...")
    header = pd.read_csv(TCGA_FILE, sep="\t", nrows=0, compression="gzip").columns.tolist()
    cancer_samples = {c: [] for c in CANCERS}
    for sid in header[1:]:
        parts = sid.split("-")
        if len(parts) < 4:
            continue
        proj = TSS_TO_PROJECT.get(parts[1])
        if proj is None:
            continue
        sc = parts[3][:2]
        if sc != "01":
            continue
        cancer = proj.replace("TCGA-", "")
        if cancer in cancer_samples:
            cancer_samples[cancer].append(sid)
    for c in CANCERS:
        print(f"  {c}: {len(cancer_samples[c])} tumor samples")

    all_wanted = []
    for c in CANCERS:
        all_wanted.extend(cancer_samples[c])
    print(f"  Total tumor samples: {len(all_wanted)}")

    # Load all wanted columns in one pass
    print("\n2. Loading TCGA expression (single pass)...")
    t_load = time.time()
    usecols = [header[0]] + all_wanted
    df = pd.read_csv(
        TCGA_FILE,
        sep="\t",
        compression="gzip",
        usecols=usecols,
        dtype={col: np.float32 for col in all_wanted},
    )
    genes = df.iloc[:, 0].astype(str).tolist()
    expr_all = df[all_wanted].values.astype(np.float32)
    del df
    print(f"  Loaded {expr_all.shape[0]} genes x {expr_all.shape[1]} samples in {time.time()-t_load:.0f}s")

    # Keep genes with any expression > 0 in at least one wanted sample
    keep_any = np.any(expr_all > 0, axis=1)
    expr_all = expr_all[keep_any, :]
    genes = [g for g, k in zip(genes, keep_any) if k]
    print(f"  After nonzero filter: {expr_all.shape[0]} genes")

    # Build HK index list in global gene space
    gene_ens = [g.split(".")[0] for g in genes]
    ens_to_idx = {ens: i for i, ens in enumerate(gene_ens)}
    hk_global = []
    for sym in hk_human:
        if sym in symbol_to_ens:
            for eid in symbol_to_ens[sym]:
                if eid in ens_to_idx:
                    hk_global.append(ens_to_idx[eid])
    hk_global = np.array(sorted(set(hk_global)), dtype=int)
    print(f"  Mapped HK genes: {len(hk_global)}")

    # Compute per-cancer pseudobulk (in per-cancer filtered gene space)
    print("\n3. Building per-cancer tumor pseudobulks...")
    raw_pseudobulks = {}
    kept_indices = {}
    hk_indices_raw = {}
    for c in CANCERS:
        cols = cancer_samples[c]
        col_idx = [all_wanted.index(sid) for sid in cols]
        expr_c = expr_all[:, col_idx]
        gene_means = np.mean(expr_c, axis=1)
        keep_c = gene_means >= MIN_GENE_MEAN_TPM
        expr_c = expr_c[keep_c, :]
        kept_indices[c] = np.where(keep_c)[0]
        # Map global HK indices to local filtered space
        local_hk = []
        old_to_new = {old: new for new, old in enumerate(kept_indices[c])}
        for old_idx in hk_global:
            if old_idx in old_to_new:
                local_hk.append(old_to_new[old_idx])
        hk_indices_raw[c] = np.array(sorted(set(local_hk)), dtype=int)
        expr_log = np.log2(np.maximum(expr_c, 0) + 1)
        raw_pseudobulks[c] = np.mean(expr_log, axis=1)
        print(f"  {c}: kept {keep_c.sum()} genes, {len(hk_indices_raw[c])} HK")

    # Align all cancers to the intersection of their kept gene sets
    print("\n3b. Aligning pseudobulks to common gene intersection...")
    common_set = set(kept_indices[CANCERS[0]])
    for c in CANCERS[1:]:
        common_set &= set(kept_indices[c])
    common_genes = np.array(sorted(common_set), dtype=int)
    old_to_new_common = {old: pos for pos, old in enumerate(common_genes)}
    print(f"  Common genes: {len(common_genes)}")

    pseudobulks = {}
    hk_indices = {}
    for c in CANCERS:
        old_to_local = {old: i for i, old in enumerate(kept_indices[c])}
        idx_in_common = np.array([old_to_local[old] for old in common_genes], dtype=int)
        pseudobulks[c] = raw_pseudobulks[c][idx_in_common]
        hk_local = []
        for raw_hk in hk_indices_raw[c]:
            old = kept_indices[c][raw_hk]
            if old in old_to_new_common:
                hk_local.append(old_to_new_common[old])
        hk_indices[c] = np.array(sorted(set(hk_local)), dtype=int)
        print(f"  {c}: common pseudobulk {pseudobulks[c].shape}, {len(hk_indices[c])} HK in common space")

    del expr_all, raw_pseudobulks  # free memory

    # Compute cross-cancer omega matrix
    print("\n4. Computing pairwise cross-cancer omega...")
    omega_mat = np.full((len(CANCERS), len(CANCERS)), np.nan)
    np.random.seed(RANDOM_SEED)
    for i, ca in enumerate(CANCERS):
        for j, cb in enumerate(CANCERS):
            if i == j:
                continue
            if i > j:
                omega_mat[i, j] = omega_mat[j, i]
                continue
            pb_a = pseudobulks[ca]
            pb_b = pseudobulks[cb]
            # HK genes present in both cancers (intersection within common space)
            hk_union = np.array(sorted(set(hk_indices[ca]) & set(hk_indices[cb])), dtype=int)
            id_idx = select_top_diff(pb_a, pb_b, hk_union, N_TOP_KF)
            r = compute_omega(pb_a, pb_b, hk_union, id_idx, w1=1.0, w2=0.0, kn_floor=1e-4)
            omega_mat[i, j] = r["omega"]
            omega_mat[j, i] = r["omega"]
            print(f"  {ca}-{cb}: omega={r['omega']:.2f}")

    print("\n5. Filling diagonal from existing phase34_v2 TT medians...")
    for i, cancer in enumerate(CANCERS):
        pair_path = RESULTS_DIR / f"phase34_v2_TCGA-{cancer}_pairs.csv"
        df_pairs = pd.read_csv(pair_path)
        diag = df_pairs[df_pairs["pair_type"] == "TT"]["omega"].median()
        omega_mat[i, i] = diag
        print(f"  {cancer} TT median: {diag:.2f}")

    print("\n6. Saving matrix...")
    out_dir = RESULTS_DIR / "figures_final"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "fig4e_tcga_cross_cancer_matrix.npz"
    np.savez(out_path, omega=omega_mat, cancers=np.array(CANCERS, dtype=object))
    print(f"  Saved: {out_path}")

    print("\n  Omega matrix:")
    header_str = "       " + "".join(f"{c:>10s}" for c in CANCERS)
    print(header_str)
    for i, ca in enumerate(CANCERS):
        row = f"{ca:>6s}  " + "".join(f"{omega_mat[i,j]:10.2f}" for j in range(len(CANCERS)))
        print(row)

    print(f"\nDone in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
