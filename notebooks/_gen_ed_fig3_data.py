#!/usr/bin/env python3
"""
Generate real TCGA per-cancer CKI omega matrices for Extended Data Figure 3.

Output: results/figures_final/ed_fig3_tcga_omega_matrices.npz

Matrix layout (4x4 per cancer):
    Normal (11) , Tumor (01) , Metastasis (06) , Recurrence (02)

For each cancer type, builds pseudobulk profiles (mean expression) per subtype,
then computes pairwise CKI omega using per-pair top-200 non-HK differential genes.
Unavailable subtypes are filled with NaN.
"""
import sys, os, io

# Fix Windows encoding issue: redirect stdout/stderr to UTF-8
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import gzip, time, warnings
from pathlib import Path

from cki.core import compute_omega

warnings.filterwarnings("ignore")

# === Paths ===
ROOT = Path(__file__).resolve().parents[1]
TCGA_FILE = ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz"
HK_FILE = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
PROBEMAP_FILE = ROOT / "data" / "tcga" / "probemap.tsv"
OUT_DIR = ROOT / "results" / "figures_final"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# === Config ===
RANDOM_SEED = 42
N_TOP_KF = 200
MIN_GENE_MEAN_TPM = 0.5

# Target cancers & subtypes for ed_fig3
TARGET_CANCERS = ["BRCA", "KIRC", "LIHC", "LUAD", "COAD", "HNSC"]
SUBTYPE_ORDER = ["Normal", "Tumor", "Metastasis", "Recurrence"]
SAMPLE_CODE_MAP = {"01": "Tumor", "02": "Recurrence", "06": "Metastasis", "11": "Normal"}

# === TSS -> Project mapping ===
TSS_TO_PROJECT = {}
for c in ["A1","A2","A7","A8","AN","AO","AQ","AR","B6","BH","C8","D8",
          "E2","EW","GI","WT","XX","E9","GM","HN","JL","LD","LL","MS",
          "OL","PE","PL","S3","UL","V7","W8","WV"]:
    TSS_TO_PROJECT[c] = "BRCA"
for c in ["05","35","38","44","49","50","55","64","67","73","75","78",
          "86","91","93","97","J2","L3","L4","M1","MP","MT","N1","N6",
          "O1","S2","TR","TV","TQ","NJ","KN","LF"]:
    TSS_TO_PROJECT[c] = "LUAD"
for c in ["BC","DD","ED","EP","ES","FV","FY","G3","GJ","HP","HU","K7",
          "KR","LG","NI","O8","PD","QN","RC","RG","T6","UB","WQ","XR",
          "YA","ZP","ZS","MI","F5"]:
    TSS_TO_PROJECT[c] = "LIHC"
for c in ["A3","AK","AL","AY","B0","B1","B2","B3","B4","B8","BP","BW",
          "CJ","CW","CZ","DV","DX","EU","GK","HE","I6","K6","KL","MM",
          "MW","P4","Q2","RG","UZ","V5","XM","YE"]:
    TSS_TO_PROJECT[c] = "KIRC"
# COAD
for c in ["3L","A6","AA","AD","AF","AG","AH","AM","AY","AZ","BQ","BR",
          "C4","C5","C6","C7","C8","C9","CA","CB","CK","CM","CN","CO",
          "CP","CQ","CR","CS","CT","CU","CV","CW","CX","CY","CZ","D5",
          "DB","DC","DD","DM","DN","DT","DY","F4","G4","G5","HA","HC",
          "HD","HF","HG","HI","HJ","HK","HL","HM","HN","HO","HU","HV",
          "HW","HX","HY","HZ","I0","I1","I2","I3","I4","I5","I7","I8",
          "I9","IA","IB","IC","ID","IE","IF","IG","IH","II","IJ","IK",
          "IL","IM","IN","IO","IP","IQ","IR","IS","IT","IU","IV","IW",
          "IX","IY","IZ","J0","J1","J2","J3","J4","J5","J6","J7","J8",
          "J9","JA","JB","JC","JD","JE","JF","JG","JH","JI","JJ","JK",
          "JL","JM","JN","JO","JP","JQ","JR","JS","JT","JU","JV","JW",
          "JX","JY","JZ","K0","K1","K2","K3","K4","K5","K6","K7","K8",
          "K9","KA","KB","KC","KD","KE","KF","KG","KH","KI","KJ","KK",
          "KL","KM","KN","KO","KP","KQ","KR","KS","KT","KU","KV","KW",
          "KX","KY","KZ"]:
    TSS_TO_PROJECT[c] = "COAD"
# HNSC
for c in ["4P","BB","BA","C9","CN","CQ","CR","CV","CX","D6","DQ","F7",
          "H7","HD","HL","HQ","HU","I5","IQ","JQ","JU","KD","KR","M2",
          "M7","M9","MC","MD","MF","MH","MJ","ML","MM","MN","MO","MP",
          "MQ","MR","MS","MT","MU","MV","MW","MX","MY","MZ","N0","N1",
          "N2","N3","N4","N5","N6","N7","N8","N9","NA","NB","NC","ND",
          "NE","NF","NG","NH","NI","NJ","NK","NL","NM","NN","NO","NP",
          "NQ","NR","NS","NT","NU","NV","NW","NX","NY","NZ","O0","O1",
          "O2","O3","O4","O5","O6","O7","O8","O9","OA","OB","OC","OD",
          "OE","OF","OG","OH","OI","OJ","OK","OL","OM","ON","OO","OP",
          "OQ","OR","OS","OT","OU","OV","OW","OX","OY","OZ","P0","P1",
          "P2","P3","P4","P5","P6","P7","P8","P9","PA","PB","PC","PD",
          "PE","PF","PG","PH","PI","PJ","PK","PL","PM","PN","PO","PP",
          "PQ","PR","PS","PT","PU","PV","PW","PX","PY","PZ","Q0","Q1",
          "Q2","Q3","Q4","Q5","Q6","Q7","Q8","Q9","QA","QB","QC","QD",
          "QE","QF","QG","QH","QI","QJ","QK","QL","QM","QN","QO","QP","QQ"]:
    TSS_TO_PROJECT[c] = "HNSC"


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
print(f"  HK gene symbols: {len(hk_human)}, probeMap entries: {len(ens_to_symbol)}")


# ====================================================================
# 1. Parse TCGA header: group samples by cancer and sample type
# ====================================================================
print("\n" + "=" * 60)
print("1. Parsing TCGA sample metadata...")
print("=" * 60)

with gzip.open(TCGA_FILE, "rt") as fh:
    header_line = fh.readline().strip().split("\t")

all_sample_ids = header_line[1:]
print(f"  Total samples in file: {len(all_sample_ids)}")

# Build cancer -> sample_type -> [sample_ids]
cancer_samples = {c: {} for c in TARGET_CANCERS}
unmapped_by_tss = {}

for sid in all_sample_ids:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    tss = parts[1]
    st_code = parts[3][:2]
    proj = TSS_TO_PROJECT.get(tss, None)
    if proj in TARGET_CANCERS:
        st_name = SAMPLE_CODE_MAP.get(st_code, None)
        if st_name:
            cancer_samples[proj].setdefault(st_name, []).append(sid)
    elif proj is None:
        unmapped_by_tss[tss] = unmapped_by_tss.get(tss, 0) + 1

# Print summary
print("\n  Sample counts per cancer:")
for cancer in TARGET_CANCERS:
    counts = {st: len(cancer_samples[cancer].get(st, [])) for st in SUBTYPE_ORDER}
    total = sum(counts.values())
    parts = ", ".join(f"{st}={counts[st]}" for st in SUBTYPE_ORDER)
    print(f"    {cancer}: total={total} ({parts})")

print(f"\n  Unmapped TSS codes: {len(unmapped_by_tss)}")
mapped_total = sum(
    sum(len(v) for v in cancer_samples[c].values()) for c in TARGET_CANCERS
)
print(f"  Mapped samples (target cancers): {mapped_total}")


# ====================================================================
# 2. Per-cancer loading and omega computation
# ====================================================================
def load_cancer_expression(cancer, sample_dict, header_line):
    """Load expression matrix for one cancer type.

    Args:
        cancer: cancer name (for logging)
        sample_dict: dict subtype -> list of sample IDs
        header_line: TCGA file header (list of column names)

    Returns:
        expr_log: samples x genes (log2(TPM + 0.001))
        hk_arr: array of HK gene indices
        sample_list: list of sample IDs (same order as rows)
        genes: list of gene Ensembl IDs
    """
    # Collect all samples for this cancer
    all_sids = []
    for st_name in SUBTYPE_ORDER:
        for sid in sample_dict.get(st_name, []):
            all_sids.append(sid)

    if not all_sids:
        return None, None, None, None

    wanted = set(all_sids)
    sample_list = sorted(wanted)

    # Build column index map
    col_idx_map = {}
    for k, sid in enumerate(header_line[1:], 1):
        if sid in wanted:
            col_idx_map[sid] = k

    if not col_idx_map:
        print(f"    [{cancer}] WARNING: no columns matched")
        return None, None, None, None

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
    if n_genes == 0:
        print(f"    [{cancer}] WARNING: no qualifying genes found")
        return None, None, None, None

    # Pass 2: fill expression matrix
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

    # Per-cancer gene filter
    gene_means = np.mean(expr, axis=0)
    keep = gene_means >= MIN_GENE_MEAN_TPM
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

    return expr_log, hk_arr, sample_list, genes


def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    """Select top-N non-HK genes by absolute expression difference."""
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1.0
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)


# ====================================================================
# 3. Compute omega matrices
# ====================================================================
print("\n" + "=" * 60)
print("3. Computing per-cancer omega matrices...")
print("=" * 60)

t0_total = time.time()
omega_matrices = {}  # cancer -> 4x4 numpy array
sample_counts = {}   # cancer -> dict of subtype -> n_samples

for cancer in TARGET_CANCERS:
    t0_cancer = time.time()
    print(f"\n--- {cancer} ---")

    sample_dict = cancer_samples[cancer]
    counts = {st: len(sample_dict.get(st, [])) for st in SUBTYPE_ORDER}
    sample_counts[cancer] = counts

    # Check which subtypes are available
    available = [st for st in SUBTYPE_ORDER if counts[st] > 0]
    print(f"  Available subtypes: " + ", ".join(f"{st}({counts[st]})" for st in available))

    if len(available) < 2:
        print(f"  SKIP: fewer than 2 subtypes available")
        omega_matrices[cancer] = np.full((4, 4), np.nan)
        continue

    # Load expression data
    print(f"  Loading expression data...")
    expr_log, hk_arr, sample_list, genes = load_cancer_expression(
        cancer, sample_dict, header_line
    )
    if expr_log is None:
        print(f"  SKIP: no expression data loaded")
        omega_matrices[cancer] = np.full((4, 4), np.nan)
        continue

    n_samples = len(sample_list)
    n_genes = len(genes)
    n_hk = len(hk_arr)
    print(f"  Loaded: {n_samples} samples x {n_genes} genes, {n_hk} HK genes")

    # Build subtype masks
    label_to_sample_list = {st: sample_dict.get(st, []) for st in SUBTYPE_ORDER}
    subtype_masks = {}
    for st in SUBTYPE_ORDER:
        if counts[st] > 0:
            subtype_masks[st] = np.array([s in set(label_to_sample_list[st]) for s in sample_list])
        else:
            subtype_masks[st] = np.zeros(n_samples, dtype=bool)

    # Build pseudobulks (mean expression per subtype)
    pseudobulks = {}
    for st in SUBTYPE_ORDER:
        if counts[st] > 0:
            mask = subtype_masks[st]
            pseudobulks[st] = np.mean(expr_log[mask, :], axis=0)
            print(f"    {st}: {counts[st]} samples -> pseudobulk")

    # Compute 4x4 omega matrix
    omega_mat = np.full((4, 4), np.nan)
    # subtype_list order matches SUBTYPE_ORDER indices

    for i, st_a in enumerate(SUBTYPE_ORDER):
        if st_a not in pseudobulks:
            continue
        for j, st_b in enumerate(SUBTYPE_ORDER):
            if j < i:
                # Fill symmetric entry later
                continue
            if i == j:
                # Diagonal: within-subtype mean omega
                mask = subtype_masks[st_a]
                indices = np.where(mask)[0]
                n_st = len(indices)
                if n_st >= 2:
                    # Sample up to 500 pairs
                    all_pairs = [(a, b) for a in range(n_st) for b in range(a + 1, n_st)]
                    n_pairs = min(len(all_pairs), 500)
                    np.random.seed(RANDOM_SEED)
                    chosen = [all_pairs[k] for k in np.random.choice(len(all_pairs), n_pairs, replace=False)]
                    omegas = []
                    for a, b in chosen:
                        pb1 = expr_log[indices[a], :]
                        pb2 = expr_log[indices[b], :]
                        id_idx = select_top_diff(pb1, pb2, hk_arr, N_TOP_KF)
                        r = compute_omega(pb1, pb2, hk_arr, id_idx, w1=1.0, w2=0.0)
                        omegas.append(r["omega"])
                    omega_mat[i, j] = np.mean(omegas)
                # else: stays NaN
            elif st_a in pseudobulks and st_b in pseudobulks:
                pb_a = pseudobulks[st_a]
                pb_b = pseudobulks[st_b]
                id_idx = select_top_diff(pb_a, pb_b, hk_arr, N_TOP_KF)
                r = compute_omega(pb_a, pb_b, hk_arr, id_idx, w1=1.0, w2=0.0)
                omega_mat[i, j] = r["omega"]
                omega_mat[j, i] = r["omega"]  # symmetric

            if (i * 4 + j + 1) % 4 == 0 and i * 4 + j > 0:
                print(f"    Computed {i*4 + j + 1}/16 entries", end="\r")

    omega_matrices[cancer] = omega_mat

    elapsed_cancer = time.time() - t0_cancer
    print(f"\n  Done in {elapsed_cancer:.0f}s")

    # Print the matrix
    print(f"  Omega matrix:")
    for i, st_a in enumerate(SUBTYPE_ORDER):
        row_str = "  ".join(
            f"{omega_mat[i, j]:6.2f}" if not np.isnan(omega_mat[i, j]) else "   NaN"
            for j in range(4)
        )
        print(f"    {st_a:12s}: {row_str}")


# ====================================================================
# 4. Save results
# ====================================================================
print("\n" + "=" * 60)
print("4. Saving results...")
print("=" * 60)

# Prepare save dict
save_dict = {}
for cancer in TARGET_CANCERS:
    save_dict[cancer] = omega_matrices[cancer]
    save_dict[f"{cancer}_counts"] = np.array(
        [sample_counts[cancer][st] for st in SUBTYPE_ORDER], dtype=int
    )

save_dict["cancers"] = np.array(TARGET_CANCERS, dtype=object)
save_dict["subtypes"] = np.array(SUBTYPE_ORDER, dtype=object)

out_path = OUT_DIR / "ed_fig3_tcga_omega_matrices.npz"
np.savez(out_path, **save_dict)
print(f"  Saved: {out_path}")

elapsed = time.time() - t0_total
print(f"\nTotal time: {elapsed:.0f}s")
print("Done!")


# ====================================================================
# 5. Print summary for team-lead
# ====================================================================
print("\n" + "=" * 60)
print("5. Summary for ed_fig3")
print("=" * 60)

for cancer in TARGET_CANCERS:
    mat = omega_matrices[cancer]
    counts = sample_counts[cancer]
    n_valid = np.sum(~np.isnan(mat))
    print(f"\n  {cancer}:")
    print(f"    Samples: " + ", ".join(f"{st}={counts[st]}" for st in SUBTYPE_ORDER))
    print(f"    Valid entries: {n_valid}/16")
    # Show range of real values
    vals = mat[~np.isnan(mat)]
    if len(vals) > 0:
        print(f"    Omega range: [{np.min(vals):.3f}, {np.max(vals):.3f}]")
