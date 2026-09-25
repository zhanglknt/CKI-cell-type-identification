"""
Species-specific Gene Identifier Handling
==========================================
Provides unified species configuration and reference gene set loading
for cross-species CKI analysis.
"""

from typing import Dict, Set, Optional
from pathlib import Path

import pandas as pd


# Supported species and their gene ID conventions
SPECIES_CONFIG: Dict[str, dict] = {
    "human": {
        "name": "Homo sapiens",
        "taxon_id": 9606,
        "ensembl_prefix": "ENSG",
        "gene_id_convention": "UPPERCASE",  # TP53, GAPDH, ACTB
        "hk_atlas_column": 1,               # column in HRT Atlas CSV (0-indexed)
        "hk_atlas_alt_column_name": "Human",
        "has_hr_atlas": True,
        "ribosomal_prefixes": ["RPL", "RPS"],
        "mitochondrial_prefix": "MT-",
    },
    "mouse": {
        "name": "Mus musculus",
        "taxon_id": 10090,
        "ensembl_prefix": "ENSMUSG",
        "gene_id_convention": "Titlecase",  # Trp53, Gapdh, Actb
        "hk_atlas_column": 0,
        "hk_atlas_alt_column_name": "Mouse",
        "has_hr_atlas": True,
        "ribosomal_prefixes": ["Rpl", "Rps"],
        "mitochondrial_prefix": "mt-",
    },
    # Generic fallback for any species not in the curated list.
    # Gene sets are always data-driven; HRT Atlas is only for human/mouse.
    "generic": {
        "name": "Unknown",
        "taxon_id": 0,
        "ensembl_prefix": "",
        "gene_id_convention": "mixed",
        "has_hr_atlas": False,
        "ribosomal_prefixes": [],
        "mitochondrial_prefix": "",
    },
}


def get_species_config(species: str) -> dict:
    """
    Get species configuration by name, scientific name, or taxon ID.

    For species not in the curated list (human/mouse), a generic
    ``"generic"`` config is returned — all gene set detection is
    data-driven and works for any species without external references.

    Parameters
    ----------
    species : str
        Species identifier. Supports:
        - Common name: "human", "mouse"
        - Scientific name: "homo sapiens", "mus musculus"
        - Taxon ID: "9606", "10090"
        - Any arbitrary name (returns generic config)

    Returns
    -------
    dict
        Species configuration dictionary. Unknown species get the
        ``"generic"`` config with ``has_hr_atlas=False``.
    """
    species_lower = species.lower().strip()

    # exact match
    if species_lower in SPECIES_CONFIG:
        return SPECIES_CONFIG[species_lower]

    # fuzzy match by scientific name or taxon ID (curated species only)
    for key in ["human", "mouse"]:
        config = SPECIES_CONFIG[key]
        if species_lower in config["name"].lower():
            return config
        if str(config["taxon_id"]) == species_lower:
            return config

    # Unknown species: return generic config — CKI gene detection is
    # entirely data-driven and does not require curated reference sets.
    import warnings
    warnings.warn(
        f"Species '{species}' is not in the curated list (human/mouse). "
        f"Using generic configuration. HRT Atlas reference is unavailable; "
        f"housekeeping genes will be auto-detected from data only."
    )
    return SPECIES_CONFIG["generic"]


def list_supported_species() -> Dict[str, dict]:
    """
    Return the full species configuration dictionary.

    Note that any species name is accepted — unknown species receive
    a ``"generic"`` config. Only ``"human"`` and ``"mouse"`` have
    HRT Atlas reference coverage.

    Returns
    -------
    dict
        SPECIES_CONFIG dictionary.
    """
    return SPECIES_CONFIG


def load_reference_hk_genes(
    species: str,
    reference_path: Optional[str] = None,
) -> Set[str]:
    """
    Load housekeeping gene set from bundled HRT Atlas reference.

    HRT Atlas (Hounkpe et al., NAR 2021) provides curated housekeeping
    genes for human and mouse. The bundled CSV contains 1:1 ortholog pairs.

    For species without HRT Atlas coverage (any non-human/non-mouse species),
    returns an empty set — gene detection falls back to data-driven methods
    (detection rate + CV filtering). This is the universal default.

    Parameters
    ----------
    species : str
        "human" or "mouse" for HRT Atlas data; any other species returns
        an empty set with a warning.
    reference_path : Optional[str]
        Path to custom HK reference CSV. If None, uses the bundled
        HRT Atlas at ``cki/data/hrt_atlas.csv``.

    Returns
    -------
    set of str
        Housekeeping gene symbols for the specified species, or an empty
        set if no reference is available.
    """
    config = get_species_config(species)

    # If species has no HRT Atlas coverage, return empty set
    if not config.get("has_hr_atlas", False):
        import warnings
        warnings.warn(
            f"No HRT Atlas reference for '{species}'. "
            f"Housekeeping gene detection is entirely data-driven "
            f"(detection rate + CV filtering)."
        )
        return set()

    if reference_path is None:
        reference_path = str(
            Path(__file__).parent / "data" / "hrt_atlas.csv"
        )

    df = pd.read_csv(reference_path, sep=None, engine="python")

    # Use column index from species config
    col_idx = config["hk_atlas_column"]
    if col_idx >= df.shape[1]:
        # Try alternate column name
        alt_name = config.get("hk_atlas_alt_column_name")
        if alt_name and alt_name in df.columns:
            genes = df[alt_name].dropna().tolist()
        else:
            raise ValueError(
                f"Column {col_idx} not found in HK reference file. "
                f"Available columns: {list(df.columns)}"
            )
    else:
        genes = df.iloc[:, col_idx].dropna().tolist()

    return set(genes)
