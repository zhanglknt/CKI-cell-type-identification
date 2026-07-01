"""Check Siletti gene mapping"""
import scanpy as sc
import pandas as pd

adata = sc.read_h5ad(r"C:\Users\KnightZ\Desktop\细胞受选择\data\brain\Nonneurons.h5ad")

print("var columns:", list(adata.var.columns))
print("var_names[:10]:", list(adata.var_names[:10]))
print("Gene[:20]:", list(adata.var["Gene"].dropna()[:20]))

n_gene = adata.var["Gene"].notna().sum()
print(f"\nNon-null Gene: {n_gene}/{adata.n_vars}")

# Build gene symbol -> index mapping
gene_to_idx = {}
for i, gene in enumerate(adata.var["Gene"]):
    if pd.notna(gene) and gene != "":
        if gene not in gene_to_idx:
            gene_to_idx[gene] = []
        gene_to_idx[gene].append(i)
print(f"Unique gene symbols: {len(gene_to_idx)}")

# Load HRT Atlas
hk_df = pd.read_csv(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv", sep=";", engine="python")
hk_human_genes = set(hk_df["Human"].dropna().astype(str))
print(f"HRT Atlas human HK genes: {len(hk_human_genes)}")

# Match
matched = 0
matched_idx = []
for gene in hk_human_genes:
    if gene in gene_to_idx:
        matched += 1
        matched_idx.extend(gene_to_idx[gene])
matched_idx = sorted(set(matched_idx))
print(f"Matched HK genes: {matched}/{len(hk_human_genes)}")
print(f"Total matched indices: {len(matched_idx)}")

# Check a few known HK genes
for gene in ["ACTB", "GAPDH", "ACTG1", "B2M", "HMBS", "HPRT1", "PPIA", "RPLP0", "RPL19", "TBP"]:
    if gene in gene_to_idx:
        indices = gene_to_idx[gene]
        names = [adata.var_names[i] for i in indices]
        print(f"  {gene}: {len(indices)} match(es), ensembl={names}")
    else:
        print(f"  {gene}: NOT FOUND")
