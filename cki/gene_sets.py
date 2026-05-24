"""
Gene Set Auto-Detection
========================
Automatic detection of housekeeping (HK) and functional (identity) gene sets
from single-cell expression data, eliminating the need for manual gene list input.
"""

from typing import List, Optional, Tuple, Union, Dict, Set
import warnings

import numpy as np
from scipy import sparse
from anndata import AnnData

from .species import load_reference_hk_genes


# ── Housekeeping Gene Detection ────────────────────────────────────────

def detect_housekeeping_genes(
    adata: AnnData,
    species: str = "human",
    method: str = "combined",
    detection_threshold: float = 0.9,
    cv_percentile: float = 0.3,
    min_mean_expr: float = 0.5,
    use_reference: bool = True,
    merge_mode: str = "union",
    cell_type_col: Optional[str] = None,
    layer: Optional[str] = None,
    random_state: int = 42,
) -> Tuple[List[int], Dict]:
    """
    Auto-detect housekeeping genes from single-cell expression matrix.

    Housekeeping genes are defined as genes that are:
    1. Expressed in a high fraction of cells (low cell-to-cell variation)
    2. Exhibit low expression coefficient of variation (stable across cells)

    Three detection methods are available, and an optional HRT Atlas
    reference can be used to enhance or validate the detected gene set.

    Parameters
    ----------
    adata : AnnData
        Expression matrix (cells x genes). Should be log-normalized
        (e.g., log1p(CP10k)).
    species : str
        "human" or "mouse". Used for reference gene matching.
    method : str
        Detection method:
        - ``"detection_rate"``: genes expressed in > threshold fraction of cells
        - ``"cv"``: genes with low coefficient of variation (Eisenberg-style)
        - ``"combined"``: both detection rate AND low CV (most stringent)
    detection_threshold : float
        Fraction of cells a gene must be detected in.
        Default 0.9 (expressed in >90% of cells).
    cv_percentile : float
        Upper percentile for CV threshold. Default 0.3 means genes with
        CV below the 30th percentile are candidate HK genes.
    min_mean_expr : float
        Minimum mean expression for CV-based filtering.
        Genes below this threshold are excluded from CV calculation.
    use_reference : bool
        If True, load HRT Atlas reference genes as enhancement/fallback.
    merge_mode : str
        How to merge reference with detected:
        - ``"union"``: detected OR reference (most comprehensive)
        - ``"intersection"``: detected AND reference (most conservative)
        - ``"detected_only"``: reference is for validation report only
    cell_type_col : Optional[str]
        Column in ``adata.obs`` for cell type labels.
        If provided, require detection in > threshold fraction of cells
        within EACH cell type (stricter pan-cellular criterion).
    layer : Optional[str]
        If provided, use ``adata.layers[layer]`` instead of ``adata.X``.
    random_state : int
        Random seed for reproducibility (reserved for future use).

    Returns
    -------
    hk_indices : list of int
        Indices of housekeeping genes in ``adata.var_names``.
    info : dict
        Metadata about the detected gene set:
        - ``gene_names``: list of gene symbols
        - ``n_genes``: number of detected HK genes
        - ``method``: detection method used
        - ``detection_threshold``: threshold applied
        - ``cv_percentile``: CV percentile used
        - ``mean_cv``: mean CV of detected HK genes
        - ``reference_overlap``: fraction of detected HK also in HRT Atlas (if use_reference)
    """
    X = _get_matrix(adata, layer)
    gene_names = adata.var_names.tolist()
    n_cells, n_genes = X.shape

    # Warn on small datasets
    if n_cells < 100:
        warnings.warn(
            f"Small dataset ({n_cells} cells). "
            f"Auto-detection of housekeeping genes may be unreliable. "
            f"Consider using use_reference=True for more robust results."
        )

    if method == "detection_rate":
        hk_candidates = _detect_by_detection_rate(
            X, detection_threshold, cell_type_col, adata
        )
    elif method == "cv":
        hk_candidates = _detect_by_cv(
            X, cv_percentile, min_mean_expr
        )
    elif method == "combined":
        dr = _detect_by_detection_rate(
            X, detection_threshold, cell_type_col, adata
        )
        cv_set = _detect_by_cv(
            X, cv_percentile, min_mean_expr
        )
        hk_candidates = dr & cv_set
    else:
        raise ValueError(
            f"Unknown method '{method}'. "
            f"Valid options: 'detection_rate', 'cv', 'combined'."
        )

    detected_genes = {gene_names[i] for i in hk_candidates}

    # Reference enhancement
    info: Dict = {
        "method": method,
        "detection_threshold": detection_threshold,
    }
    if method in ("cv", "combined"):
        info["cv_percentile"] = cv_percentile
    if method != "cv":
        info["cell_type_col"] = cell_type_col

    if use_reference:
        try:
            ref_genes = load_reference_hk_genes(species)
        except Exception as e:
            warnings.warn(
                f"Could not load HRT Atlas reference: {e}. "
                f"Proceeding with detected-only gene set."
            )
            ref_genes = set()

        overlap_genes = detected_genes & ref_genes

        if merge_mode == "union":
            final_genes = detected_genes | ref_genes
        elif merge_mode == "intersection":
            final_genes = overlap_genes
        elif merge_mode == "detected_only":
            final_genes = detected_genes
        else:
            raise ValueError(
                f"Unknown merge_mode '{merge_mode}'. "
                f"Valid: 'union', 'intersection', 'detected_only'."
            )

        info["reference_overlap"] = (
            len(overlap_genes) / len(detected_genes)
            if len(detected_genes) > 0
            else 0.0
        )
        info["n_reference"] = len(ref_genes)
        info["n_detected"] = len(detected_genes)
        info["n_overlap"] = len(overlap_genes)
        info["merge_mode"] = merge_mode
    else:
        final_genes = detected_genes

    hk_indices = [i for i, g in enumerate(gene_names) if g in final_genes]

    # Compute mean CV for report
    if len(hk_indices) > 0:
        mean_expr = np.array(X.mean(axis=0)).flatten()
        std_expr = np.array(
            X[:, hk_indices].toarray().std(axis=0)
            if hasattr(X, "toarray")
            else X[:, hk_indices].std(axis=0)
        ).flatten()
        cv_values = std_expr / (mean_expr[hk_indices] + 1e-8)
        info["mean_cv"] = float(np.mean(cv_values))
    else:
        info["mean_cv"] = float("nan")

    info["gene_names"] = [gene_names[i] for i in hk_indices]
    info["n_genes"] = len(hk_indices)

    if info["n_genes"] < 30:
        warnings.warn(
            f"Only {info['n_genes']} housekeeping genes detected. "
            f"This may be insufficient for reliable normalization. "
            f"Consider lowering detection_threshold or using use_reference=True "
            f"with merge_mode='union'."
        )

    return hk_indices, info


def _detect_by_detection_rate(
    X,
    detection_threshold: float,
    cell_type_col: Optional[str],
    adata: AnnData,
) -> Set[int]:
    """Detect HK genes by expression detection rate."""
    is_sparse = sparse.issparse(X)
    if is_sparse:
        X_arr = X.toarray()
    else:
        X_arr = np.asarray(X)
    expressed = X_arr > 0

    if cell_type_col is not None and cell_type_col in adata.obs.columns:
        # Per-cell-type detection requirement
        cell_types = adata.obs[cell_type_col].unique()
        n_cell_types = len(cell_types)
        ct_masks = np.zeros((n_cell_types, expressed.shape[0]), dtype=bool)
        for i, ct in enumerate(cell_types):
            ct_masks[i] = (adata.obs[cell_type_col] == ct).values

        pan_ct_detected = np.ones(expressed.shape[1], dtype=bool)
        for i in range(n_cell_types):
            n_ct = ct_masks[i].sum()
            if n_ct == 0:
                continue
            ct_rate = expressed[ct_masks[i]].sum(axis=0) / n_ct
            pan_ct_detected &= (ct_rate > detection_threshold)
        candidates = set(np.where(pan_ct_detected)[0])
    else:
        # Global detection rate
        det_rate = expressed.sum(axis=0) / expressed.shape[0]
        candidates = set(np.where(det_rate > detection_threshold)[0])

    return candidates


def _detect_by_cv(
    X,
    cv_percentile: float,
    min_mean_expr: float,
) -> Set[int]:
    """Detect HK genes by low coefficient of variation (Eisenberg-style)."""
    if sparse.issparse(X):
        X_arr = X.toarray()
    else:
        X_arr = np.asarray(X)

    n_cells, n_genes = X_arr.shape
    mean_expr = np.mean(X_arr, axis=0)
    std_expr = np.std(X_arr, axis=0)

    # Only consider well-expressed genes
    well_expr_mask = mean_expr > min_mean_expr

    cv_values = np.full(n_genes, np.inf)
    cv_values[well_expr_mask] = (
        std_expr[well_expr_mask] / (mean_expr[well_expr_mask] + 1e-8)
    )

    # CV threshold at the given percentile among well-expressed genes
    well_cv = cv_values[well_expr_mask]
    cv_threshold = np.percentile(well_cv, cv_percentile * 100)

    low_cv_mask = (cv_values <= cv_threshold) & well_expr_mask
    candidates = set(np.where(low_cv_mask)[0])

    return candidates


# ── Functional Gene Set Detection ────────────────────────────────────────

def detect_functional_genes(
    adata: AnnData,
    method: str = "hvg",
    n_top_genes: int = 2000,
    hk_indices: Optional[List[int]] = None,
    go_terms: Optional[Union[str, List[str]]] = None,
    kegg_pathways: Optional[Union[str, List[str]]] = None,
    cell_type_col: Optional[str] = None,
    n_marker_per_cluster: int = 50,
    layer: Optional[str] = None,
    flavor: str = "seurat",
    batch_key: Optional[str] = None,
    random_state: int = 42,
) -> Tuple[List[int], Dict]:
    """
    Auto-detect functional/identity gene set.

    Functional genes are genes with high cell-to-cell variability that
    capture biological differences between cell states. They are used
    to compute k_f (functional conversion rate) in CKI.

    Parameters
    ----------
    adata : AnnData
        Expression matrix (cells x genes). Should be log-normalized.
    method : str
        Detection method:
        - ``"hvg"``: Scanpy highly_variable_genes (recommended)
        - ``"markers"``: differential expression per cluster
        - ``"hvg_and_markers"``: union of HVG and cluster markers
    n_top_genes : int
        Number of top HVGs. Default 2000 (standard for scRNA-seq).
    hk_indices : Optional[List[int]]
        Housekeeping gene indices to EXCLUDE from functional gene set.
        Essential for maintaining the k_n/k_f independence assumption.
    go_terms : Optional[Union[str, List[str]]]
        GO term ID(s) to include. E.g., ``"GO:0006955"`` for immune response.
        Requires optional ``gseapy`` dependency.
    kegg_pathways : Optional[Union[str, List[str]]]
        KEGG pathway ID(s) to include. E.g., ``"hsa04610"`` for complement.
        Requires optional ``gseapy`` dependency.
    cell_type_col : Optional[str]
        Column in ``adata.obs`` for cell type labels.
        Required for ``method="markers"``.
    n_marker_per_cluster : int
        Number of top marker genes per cluster for marker detection.
    layer : Optional[str]
        Layer to use for HVG computation.
    flavor : str
        HVG flavor for Scanpy: ``"seurat"``, ``"seurat_v3"``, ``"cell_ranger"``.
    batch_key : Optional[str]
        Batch key for batch-aware HVG selection.
    random_state : int
        Random seed for reproducibility.

    Returns
    -------
    identity_indices : list of int
        Indices of functional genes in ``adata.var_names``.
    info : dict
        Metadata about the gene set:
        - ``method``: detection method
        - ``n_genes``: number of functional genes
        - ``n_pathway_genes``: number added from GO/KEGG (if applicable)
    """
    import scanpy as sc

    info: Dict = {"method": method}
    identity_set: Set[int] = set()

    # Primary detection
    if method in ("hvg", "hvg_and_markers"):
        # Work on a copy to avoid mutating source adata
        adata_tmp = adata.copy() if method == "hvg_and_markers" else adata
        sc.pp.highly_variable_genes(
            adata_tmp,
            n_top_genes=n_top_genes,
            flavor=flavor,
            batch_key=batch_key,
            layer=layer,
        )
        hvg_idx = set(np.where(adata_tmp.var["highly_variable"].values)[0])
        identity_set |= hvg_idx
        info["n_hvg"] = len(hvg_idx)
        info["n_top_genes"] = n_top_genes

    if method in ("markers", "hvg_and_markers"):
        if cell_type_col is None or cell_type_col not in adata.obs.columns:
            raise ValueError(
                f"cell_type_col='{cell_type_col}' required for marker detection. "
                f"Available columns: {list(adata.obs.columns)}"
            )
        markers = _detect_by_markers(
            adata, cell_type_col, n_marker_per_cluster, layer, random_state
        )
        identity_set |= markers
        info["n_markers"] = len(markers)
        info["n_marker_per_cluster"] = n_marker_per_cluster

    if not identity_set:
        raise RuntimeError(
            f"No functional genes detected with method '{method}'. "
            f"Check input data quality."
        )

    # Exclude HK genes (maintain k_n/k_f independence)
    if hk_indices is not None:
        hk_set = set(hk_indices)
        identity_set -= hk_set
        n_removed = len(hk_set & identity_set) if hk_set & identity_set else 0
        if n_removed > 0:
            info["n_hk_removed"] = n_removed

    # GO/KEGG pathway enhancement
    pathway_genes = set()
    if go_terms is not None or kegg_pathways is not None:
        pathway_genes = _get_pathway_genes(go_terms, kegg_pathways)
        if pathway_genes:
            gene_names = adata.var_names.tolist()
            pathway_idx = {
                i for i, g in enumerate(gene_names) if g in pathway_genes
            }
            identity_set |= pathway_idx
            info["n_pathway_genes"] = len(pathway_idx)

    identity_indices = sorted(identity_set)  # sort for reproducibility
    info["n_genes"] = len(identity_indices)

    if info["n_genes"] < 50:
        warnings.warn(
            f"Only {info['n_genes']} functional genes detected. "
            f"Consider lowering n_top_genes or using method='hvg_and_markers'."
        )

    return identity_indices, info


def _detect_by_markers(
    adata: AnnData,
    cell_type_col: str,
    n_marker_per_cluster: int,
    layer: Optional[str],
    random_state: int,
) -> Set[int]:
    """Detect functional genes via differential expression per cluster."""
    import scanpy as sc

    sc.tl.rank_genes_groups(
        adata,
        groupby=cell_type_col,
        n_genes=n_marker_per_cluster,
        method="wilcoxon",
        layer=layer,
    )

    gene_names = adata.var_names.tolist()
    marker_genes: Set[str] = set()
    clusters = adata.obs[cell_type_col].unique()

    for cluster in clusters:
        try:
            genes = adata.uns["rank_genes_groups"]["names"][cluster]
            marker_genes.update(genes)
        except (KeyError, IndexError):
            continue

    return {i for i, g in enumerate(gene_names) if g in marker_genes}


def _get_pathway_genes(
    go_terms: Optional[Union[str, List[str]]],
    kegg_pathways: Optional[Union[str, List[str]]],
) -> Set[str]:
    """
    Retrieve gene symbols for GO terms or KEGG pathways.

    Requires gseapy for database queries. Returns an empty set
    if gseapy is not available or queries fail.
    """
    pathway_genes: Set[str] = set()

    try:
        import gseapy as gp
    except ImportError:
        warnings.warn(
            "gseapy not installed. GO/KEGG pathway enhancement is disabled. "
            "Install with: pip install gseapy"
        )
        return pathway_genes

    # GO terms
    if go_terms is not None:
        if isinstance(go_terms, str):
            go_terms = [go_terms]
        for go_id in go_terms:
            try:
                genes = gp.parser.gsea_gmt_parser(
                    "GO_Biological_Process_2021",
                    organism="human",
                ).get(go_id, [])
                pathway_genes.update(genes)
            except Exception:
                warnings.warn(f"Could not retrieve genes for GO term: {go_id}")

    # KEGG pathways
    if kegg_pathways is not None:
        if isinstance(kegg_pathways, str):
            kegg_pathways = [kegg_pathways]
        for kegg_id in kegg_pathways:
            try:
                # Determine organism from pathway prefix
                if kegg_id.startswith("hsa"):
                    organism = "human"
                elif kegg_id.startswith("mmu"):
                    organism = "mouse"
                else:
                    organism = "human"

                genes = gp.parser.gsea_gmt_parser(
                    f"KEGG_2021_{organism.capitalize()}",
                    organism=organism,
                ).get(kegg_id, [])
                pathway_genes.update(genes)
            except Exception:
                warnings.warn(f"Could not retrieve genes for KEGG pathway: {kegg_id}")

    return pathway_genes


# ── Utilities ─────────────────────────────────────────────────────────────

def _get_matrix(adata: AnnData, layer: Optional[str] = None):
    """Extract expression matrix from AnnData, handling layers."""
    if layer is not None:
        if layer not in adata.layers:
            raise ValueError(
                f"Layer '{layer}' not found in adata.layers. "
                f"Available: {list(adata.layers.keys())}"
            )
        return adata.layers[layer]
    return adata.X


def genes_to_indices(
    gene_names: Union[List[str], Set[str]],
    adata: AnnData,
) -> List[int]:
    """
    Convert gene symbols to integer indices in ``adata.var_names``.

    Parameters
    ----------
    gene_names : list or set of str
        Gene symbols to look up.
    adata : AnnData
        Annotated data matrix.

    Returns
    -------
    list of int
        Indices of matching genes. Genes not found are silently dropped.

    Notes
    -----
    Matches gene symbols as-is against ``adata.var_names``.
    If your data uses Ensembl IDs, convert externally before calling.
    """
    if isinstance(gene_names, set):
        gene_names = list(gene_names)

    return [
        i for i, g in enumerate(adata.var_names)
        if g in gene_names
    ]
