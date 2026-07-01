"""Quick check of Siletti var_names format"""
import scanpy as sc
adata = sc.read_h5ad(r"C:\Users\KnightZ\Desktop\细胞受选择\data\brain\Nonneurons.h5ad")
print("var_names (first 30):", list(adata.var_names[:30]))
print()
print("var columns:", list(adata.var.columns))
if "gene_symbol" in adata.var.columns:
    print("gene_symbols (first 30):", list(adata.var["gene_symbol"][:30]))
if "feature_name" in adata.var.columns:
    print("feature_names (first 30):", list(adata.var["feature_name"][:30]))
if "feature_id" in adata.var.columns:
    print("feature_ids (first 30):", list(adata.var["feature_id"][:30]))
if "feature_biotype" in adata.var.columns:
    print("biotypes (first 30):", list(adata.var["feature_biotype"][:30]))
