"""
CKI Bootstrap for TCGA (Bulk RNA-seq)
=========================================
Convert TCGA bulk data to AnnData, then run bootstrap_test for each cancer type.
"""

import sys, os, time, gzip
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *
PROBEMAP = PROBEMAP_FILE
RESULTS = RESULTS_DIR

import numpy as np
import pandas as pd
from anndata import AnnData
from pathlib import Path

from cki.bootstrap import bootstrap_test

# === Config ===
# TCGA_FILE, HK_FILE, PROBEMAP_FILE, RESULTS_DIR from _paths
# PROBEMAP = PROBEMAP_FILE, RESULTS = RESULTS_DIR (aliases above)
N_BOOTSTRAP = 100
RANDOM_STATE = 42

TARGET = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

# TSS -> Project mapping (same as phase34_v2.py)
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

# === Load HK gene mapping ===
print("Loading HK gene mapping...")
pm = pd.read_csv(PROBEMAP, sep="\t")
ens_to_symbol = {}
for _, row in pm.iterrows():
    eid = str(row.iloc[0]).split(".")[0]
    sym = str(row.iloc[1])
    if eid and sym and sym != "nan":
        ens_to_symbol[eid] = sym

hk_df = pd.read_csv(HK_FILE)
hk_raw = hk_df.iloc[:, 0].dropna().astype(str)
hk_symbols = set()
for row in hk_raw:
    parts = row.split(";")
    if len(parts) >= 2:
        hk_symbols.add(parts[1].strip())

hk_ens_ids = []
for sym in hk_symbols:
    for eid in [e for e, s in ens_to_symbol.items() if s == sym]:
        hk_ens_ids.append(eid)
hk_set = set(hk_ens_ids)
print(f"  HK symbols: {len(hk_symbols)}, HK Ensembl IDs: {len(hk_set)}")

# === Parse TCGA header ===
print("\nParsing TCGA header...")
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")

sample_info = {}
for i, sid in enumerate(header[1:]):
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    tss = parts[1]
    proj = TSS_TO_PROJECT.get(tss)
    if proj not in TARGET:
        continue
    sc = parts[3][:2]
    sample_type = "Tumor" if sc == "01" else ("Normal" if sc == "11" else None)
    if sample_type:
        sample_info[i] = {"sid": sid, "project": proj, "type": sample_type}

print(f"  Found {len(sample_info)} samples across {len(TARGET)} projects")

# === Build per-cancer AnnData and run bootstrap ===
print("\n" + "=" * 60)
print("Running bootstrap for each TCGA cancer type (B=100)...")
print("=" * 60)

all_results = []

for cancer in TARGET:
    print(f"\n--- {cancer} ---")
    t0 = time.time()
    
    # Collect sample indices for this cancer
    cancer_samples = {idx: v for idx, v in sample_info.items() if v["project"] == cancer}
    tumor_idx = [i for i, v in cancer_samples.items() if v["type"] == "Tumor"]
    normal_idx = [i for i, v in cancer_samples.items() if v["type"] == "Normal"]
    
    if len(tumor_idx) < 10 or len(normal_idx) < 5:
        print(f"  SKIP: T={len(tumor_idx)}, N={len(normal_idx)}")
        continue
    
    print(f"  Samples: T={len(tumor_idx)}, N={len(normal_idx)}")
    
    # Load expression matrix for this cancer
    # Pass 1: identify genes with expression > 0 in any sample
    wanted = set(cancer_samples.keys())
    gene_names = []
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split("\t")
            has_expr = False
            for ci in wanted:
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
    print(f"  Genes (expressed): {n_genes}")
    
    # Pass 2: fill matrix
    expr = np.zeros((len(cancer_samples), n_genes), dtype=np.float32)
    sorted_indices = sorted(cancer_samples.keys())
    idx_map = {orig: new for new, orig in enumerate(sorted_indices)}
    
    gene_idx = 0
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split("\t")
            if gene_idx < n_genes and parts[0] == gene_names[gene_idx]:
                for orig_idx, new_idx in idx_map.items():
                    if orig_idx < len(parts):
                        try:
                            expr[new_idx, gene_idx] = float(parts[orig_idx])
                        except (ValueError, IndexError):
                            pass
                gene_idx += 1
                if gene_idx >= n_genes:
                    break
    
    # Filter genes: mean TPM >= 0.5
    gene_means = np.mean(expr, axis=0)
    keep = gene_means >= 0.5
    expr = expr[:, keep]
    genes = [g for g, k in zip(gene_names, keep) if k]
    print(f"  Genes (filtered, mean>=0.5): {len(genes)}")
    
    # log2 transform
    expr_log = np.log2(np.maximum(expr, 0) + 0.001)
    
    # Map HK genes
    gene_ens = [g.split(".")[0] for g in genes]
    ens_to_idx = {e: i for i, e in enumerate(gene_ens)}
    hk_indices = sorted(set([ens_to_idx[e] for e in hk_set if e in ens_to_idx]))
    print(f"  HK genes (matched): {len(hk_indices)}")
    
    # Create AnnData
    sample_types = ["Tumor" if cancer_samples[sorted_indices[i]]["type"] == "Tumor" else "Normal"
                   for i in range(len(sorted_indices))]
    
    adata = AnnData(
        X=expr_log,
        obs=pd.DataFrame({"sample_type": sample_types}, index=[cancer_samples[s]["sid"] for s in sorted_indices]),
        var=pd.DataFrame(index=genes),
    )
    adata.obs["sample_type"] = adata.obs["sample_type"].astype("category")
    
    # Run bootstrap
    print(f"  Running bootstrap (B={N_BOOTSTRAP})...")
    try:
        result = bootstrap_test(
            adata,
            species="human",
            groupby="sample_type",
            group_a="Tumor",
            group_b="Normal",
            hk_indices=hk_indices,
            n_bootstrap=N_BOOTSTRAP,
            random_state=RANDOM_STATE,
            verbose=True,
        )
        
        all_results.append({
            "Cancer": cancer,
            "n_Tumor": len(tumor_idx),
            "n_Normal": len(normal_idx),
            "n_Genes": len(genes),
            "n_HK": len(hk_indices),
            "omega": f"{result['omega']:.4f}",
            "kn": f"{result['kn']:.6f}",
            "kf": f"{result['kf']:.6f}",
            "p_value": f"{result['p_value']:.4e}",
            "cohens_d": f"{result['cohens_d']:.4f}",
            "null_mean": f"{result['null_mean']:.4f}",
            "null_std": f"{result['null_std']:.4f}",
            "ci_95_lower": f"{result['ci_95'][0]:.4f}",
            "ci_95_upper": f"{result['ci_95'][1]:.4f}",
            "time_s": f"{time.time()-t0:.0f}",
        })
        print(f"  Result: omega={result['omega']:.4f}, p={result['p_value']:.4e}, d={result['cohens_d']:.2f}")
    except Exception as e:
        print(f"  ERROR: {e}")
        all_results.append({
            "Cancer": cancer,
            "n_Tumor": len(tumor_idx),
            "n_Normal": len(normal_idx),
            "error": str(e),
        })

# === Save results ===
print("\n" + "=" * 60)
print("Saving results...")
print("=" * 60)

df = pd.DataFrame(all_results)
print("\n" + df.to_string(index=False))
df.to_csv(RESULTS / "tcga_bootstrap_results.csv", index=False)

print(f"\nDone! Results saved to tcga_bootstrap_results.csv")
