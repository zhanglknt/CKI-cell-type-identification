"""
_paths.py — Dynamic path resolution for reproducibility.
All analysis scripts import from here instead of hardcoding absolute paths.
Works on any machine: resolves relative to this file's location.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"

# Tabula Sapiens human data
TS_HUMAN_DIR = DATA_DIR / "ts_human"
TS_ORGANS = ["Liver", "Kidney", "Heart", "Bone_Marrow", "Spleen", "Lung"]

# Tabula Muris FACS mouse data
FACS_DIR = DATA_DIR / "FACS" / "FACS"
FACS_ANNOTATIONS = DATA_DIR / "annotations_FACS.csv"
FACS_METADATA = DATA_DIR / "metadata_FACS.csv"

# Brain data
BRAIN_FILE = DATA_DIR / "brain" / "Nonneurons.h5ad"

# TCGA data
TCGA_FILE = DATA_DIR / "tcga" / "tcga_RSEM_gene_tpm.gz"
PROBEMAP_FILE = DATA_DIR / "tcga" / "probemap.tsv"

# Housekeeping genes
HK_FILE = DATA_DIR / "housekeeping" / "Human_Mouse_Common.csv"

# Ensure results directory exists
RESULTS_DIR.mkdir(exist_ok=True)
