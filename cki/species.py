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
        "ribosomal_prefixes": ["Rpl", "Rps"],
        "mitochondrial_prefix": "mt-",
    },
}


def get_species_config(species: str) -> dict:
    """
    Get species configuration by name, scientific name, or taxon ID.

    Parameters
    ----------
    species : str
        Species identifier. Supports:
        - Common name: "human", "mouse"
        - Scientific name: "homo sapiens", "mus musculus"
        - Taxon ID: "9606", "10090"

    Returns
    -------
    dict
        Species configuration dictionary.

    Raises
    ------
    ValueError
        If the species is not recognized.
    """
    species_lower = species.lower().strip()

    # exact match
    if species_lower in SPECIES_CONFIG:
        return SPECIES_CONFIG[species_lower]

    # fuzzy match by scientific name or taxon ID
    for key, config in SPECIES_CONFIG.items():
        if species_lower in config["name"].lower():
            return config
        if str(config["taxon_id"]) == species_lower:
            return config

    raise ValueError(
        f"Unknown species '{species}'. "
        f"Supported: {list(SPECIES_CONFIG.keys())} "
        f"(or use scientific names / taxon IDs: "
        f"{[(c['name'], c['taxon_id']) for c in SPECIES_CONFIG.values()]})"
    )


def list_supported_species() -> Dict[str, dict]:
    """
    Return the full species configuration dictionary.

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

    Parameters
    ----------
    species : str
        "human" or "mouse".
    reference_path : Optional[str]
        Path to custom HK reference CSV. If None, uses the bundled
        HRT Atlas at ``cki/data/hrt_atlas.csv``.

    Returns
    -------
    set of str
        Housekeeping gene symbols for the specified species.
    """
    if reference_path is None:
        reference_path = str(
            Path(__file__).parent / "data" / "hrt_atlas.csv"
        )

    config = get_species_config(species)
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
