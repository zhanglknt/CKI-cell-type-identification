# -*- coding: utf-8 -*-
"""
nc52 (v52 revision, reviewer B5 prerequisite): softmax-mapping TCGA pair table
with sample labels.

The published softmax (v2) pair tables (results/phase34_v2_<cancer>_pairs.csv)
carry no sample labels, so the sample-level cluster bootstrap CIs required for
the linear-vs-softmax mapping comparison (nc52 B5) cannot be computed from
them. This script is a LINE-FOR-LINE MIRROR of notebooks/06_phase34_v2.py
(same per-cancer streaming load, expression>0 gene presence pass,
mean TPM >= 0.5 filter, per-cancer HK mapping, N_TOP_KF=200 per-pair |delta|
identity genes ranked on log2(TPM+1), cki.core.compute_omega with
kn_floor=1e-4, RANDOM_SEED=42, MAX_PAIRS_TT=MAX_PAIRS_TN=2000, same
TT-subsample seeding order) with ONE change only:

    pair records additionally carry sample_a / sample_b barcodes.

CC (ILSBio cell-line) samples are KEPT in the table (TSS 'CC' -> LIHC, the
audit-corrected mapping already used by 06_phase34_v2.py); ex-CC filtering is
applied downstream so both cohorts can be derived from this one file.

Input : data/tcga/tcga_RSEM_gene_tpm.gz, data/tcga/probemap.tsv,
        data/housekeeping/Human_Mouse_Common.csv
Output: results/nc52_tcga_softmax_all_pairs.csv
Seed  : 42 (verbatim v2 seeding).
"""
import sys, os, time, gzip, warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *  # noqa: F401,F403

import numpy as np
import pandas as pd
from cki.core import compute_omega

warnings.filterwarnings("ignore")

# === Config (verbatim from 06_phase34_v2.py) ===
RANDOM_SEED = 42
N_TOP_KF = 200
MIN_TUMOR = 30
MIN_NORMAL = 10
MAX_PAIRS_TT = 2000
MAX_PAIRS_TN = 2000

TARGET = [
    "TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"
]

t0_total = time.time()

# ====================================================================
# 0. Preload HK gene mapping (verbatim v2)
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
# 1. Parse sample metadata (verbatim v2)
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
    "94":"TCGA-LUSC","96":"TCGA-LUSC","98":"TCGA-LUSC","CC":"TCGA-LIHC",
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
    "MW":"TCGA-KIRC","P4":"TCGA-KIRC","Q2":"TCGA-KIRC",
    "UZ":"TCGA-KIRC","V5":"TCGA-KIRC","XM":"TCGA-KIRC","YE":"TCGA-KIRC",
}

with gzip.open(TCGA_FILE, "rt") as fh:
    header_line = fh.readline().strip().split("\t")

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
# 2. Per-cancer-type loading (verbatim v2)
# ====================================================================

def load_cancer_data(cancer, tumor_ids, normal_ids):
    wanted = set(tumor_ids + normal_ids)

    col_idx_map = {}
    for k, sid in enumerate(header_line[1:], 1):
        if sid in wanted:
            col_idx_map[sid] = k

    sample_list = sorted(wanted)
    col_arr = np.array([col_idx_map[s] for s in sample_list], dtype=np.int32)

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

    gene_means = np.mean(expr, axis=0)
    keep = gene_means >= 0.5
    expr = expr[:, keep]
    genes = [g for g, k in zip(gene_names, keep) if k]

    expr_log = np.log2(np.maximum(expr, 0) + 1)

    gene_ens = [g.split(".")[0] for g in genes]
    ens_to_idx_local = {ens: i for i, ens in enumerate(gene_ens)}
    hk_local = []
    for sym in hk_human:
        if sym in symbol_to_ens:
            for eid in symbol_to_ens[sym]:
                if eid in ens_to_idx_local:
                    hk_local.append(ens_to_idx_local[eid])
    hk_arr = np.array(sorted(set(hk_local)), dtype=int)

    tumor_mask = np.array([s in tumor_ids for s in sample_list])
    normal_mask = np.array([s in normal_ids for s in sample_list])

    return expr_log, hk_arr, tumor_mask, normal_mask, genes, sample_list


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)


# ====================================================================
# 3. Per-cancer omega computation (verbatim v2 + sample labels)
# ====================================================================
print("\n" + "=" * 60)
print("3. Per-cancer omega analysis (softmax mapping, sample-labelled)...")
print("=" * 60)

all_pair_details = []

for cancer in usable:
    t0_cancer = time.time()
    print(f"\n--- {cancer} ---")

    print(f"  Loading data...")
    expr_log, hk_arr, tumor_mask, normal_mask, genes, sample_list = load_cancer_data(
        cancer, proj_tumor[cancer], proj_normal[cancer]
    )
    t_idx = np.where(tumor_mask)[0]
    n_idx = np.where(normal_mask)[0]
    n_t = len(t_idx)
    n_n = len(n_idx)
    tumor_sids = [sample_list[i] for i in t_idx]
    print(f"  Genes: {len(genes)}, HK: {len(hk_arr)}, T={n_t}, N={n_n}")

    # === TT pairs (verbatim v2 seeding) ===
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
        id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0, kn_floor=1e-4)
        tt_details.append({"pair_type": "TT", "cancer": cancer,
                           "sample_a": tumor_sids[i], "sample_b": tumor_sids[j],
                           "omega": r["omega"], "kn": r["kn"], "kf": r["kf"]})
        if (idx + 1) % 500 == 0:
            print(f"    TT: {idx+1}/{len(tt_pairs)}", end="\r")
    print(f"    TT: {len(tt_pairs)}/{n_tt_total} done")

    # === NN pairs ===
    n_nn_total = n_n * (n_n - 1) // 2
    nn_details = []
    for i in range(n_n):
        for j in range(i + 1, n_n):
            p1, p2 = expr_log[n_idx[i], :], expr_log[n_idx[j], :]
            id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
            r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0, kn_floor=1e-4)
            nn_details.append({"pair_type": "NN", "cancer": cancer,
                               "sample_a": sample_list[n_idx[i]],
                               "sample_b": sample_list[n_idx[j]],
                               "omega": r["omega"], "kn": r["kn"], "kf": r["kf"]})
    print(f"    NN: {n_nn_total} done")

    # === TN pairs (continues v2's rng stream, verbatim) ===
    all_tn = [(i, j) for i in range(n_t) for j in range(n_n)]
    n_tn_total = len(all_tn)
    if n_tn_total > MAX_PAIRS_TN:
        tn_pairs = [all_tn[k] for k in np.random.choice(n_tn_total, MAX_PAIRS_TN, replace=False)]
    else:
        tn_pairs = all_tn

    tn_details = []
    for idx, (i, j) in enumerate(tn_pairs):
        p1, p2 = expr_log[t_idx[i], :], expr_log[n_idx[j], :]
        id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0, kn_floor=1e-4)
        tn_details.append({"pair_type": "TN", "cancer": cancer,
                           "sample_a": tumor_sids[i],
                           "sample_b": sample_list[n_idx[j]],
                           "omega": r["omega"], "kn": r["kn"], "kf": r["kf"]})
        if (idx + 1) % 500 == 0:
            print(f"    TN: {idx+1}/{len(tn_pairs)}", end="\r")
    print(f"    TN: {len(tn_pairs)}/{n_tn_total} done")

    df_c = pd.DataFrame(tt_details + nn_details + tn_details)
    all_pair_details.append(df_c)
    print(f"  {cancer} done in {time.time()-t0_cancer:.0f}s")

# ====================================================================
# 4. Save combined output
# ====================================================================
df_all = pd.concat(all_pair_details, ignore_index=True)
out = RESULTS_DIR / "nc52_tcga_softmax_all_pairs.csv"
df_all.to_csv(out, index=False)
print(f"\nSaved: {out} ({len(df_all)} pairs)")
print(f"Total time: {time.time()-t0_total:.0f}s")
print("DONE")
