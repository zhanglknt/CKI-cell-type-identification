"""
CKI: Cell-state Kinetic Index
==============================
A Ka/Ks-inspired framework for quantifying selective transcriptomic
remodeling in single-cell RNA-seq data.

**Minimal usage**::

    import scanpy as sc
    from cki import compute

    adata = sc.read_h5ad("data.h5ad")
    sc.pp.normalize_total(adata, target_sum=1e4)
    sc.pp.log1p(adata)

    result = compute(
        adata, species="human",
        groupby="cell_type", group_a="T_cell", group_b="B_cell",
    )
    print(f"omega = {result['omega']:.4f}")

**Low-level API** (for advanced users)::

    from cki import compute_omega, compute_kn, compute_kf, js_divergence

    result = compute_omega(pb_a, pb_b, hk_indices, identity_indices)
    print(result["omega"], result["kn"], result["kf"])
"""

from .core import js_divergence, compute_kn, compute_kf, compute_omega, compute
from .bootstrap import bootstrap_test
from .preprocess import pseudobulk, normalize_expression, select_hvg
from .utils import ensure_probability_distribution
from .gene_sets import detect_housekeeping_genes, detect_functional_genes, genes_to_indices
from .species import get_species_config, load_reference_hk_genes, list_supported_species

__version__ = "0.3.1"

__all__ = [
    # High-level API
    "compute",
    # Core computation
    "compute_omega",
    "compute_kn",
    "compute_kf",
    "js_divergence",
    # Statistical testing
    "bootstrap_test",
    # Preprocessing
    "pseudobulk",
    "normalize_expression",
    "select_hvg",
    # Gene set auto-detection
    "detect_housekeeping_genes",
    "detect_functional_genes",
    "genes_to_indices",
    # Species handling
    "get_species_config",
    "load_reference_hk_genes",
    "list_supported_species",
    # Utilities
    "ensure_probability_distribution",
]
