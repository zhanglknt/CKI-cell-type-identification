"""
Generate the Siletti ROI -> dissection full-name glossary (v38, Round-5 P0-1 fix).

Extracts the roi/dissection metadata mapping from the non-neuronal brain h5ad
(the same file the brain pipeline reads) and writes results/v38_region_glossary.csv
with one row per ROI abbreviation. The full-path dissection strings come verbatim
from the dataset metadata (Ding et al. structural ontology, as used by Siletti
et al. 2023), so the glossary cannot drift from the data.

Run: cki_env/Scripts/python.exe notebooks/_v38_region_glossary.py
"""
from pathlib import Path

import h5py
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
H5AD = ROOT / "data" / "brain" / "Nonneurons.h5ad"
OUT = ROOT / "results" / "v38_region_glossary.csv"


def _cats(group):
    cats = [c.decode() if isinstance(c, bytes) else str(c)
            for c in group["categories"][:]]
    return cats, group["codes"][:]


def main():
    with h5py.File(H5AD, "r") as f:
        obs = f["obs"]
        roi_cats, roi_codes = _cats(obs["roi"])
        dis_cats, dis_codes = _cats(obs["dissection"])

    mapping = {}
    for r, d in zip(roi_codes, dis_codes):
        key = roi_cats[r].replace("Human ", "")
        val = dis_cats[d]
        if val:  # two ROIs carry empty dissection strings; drop blanks
            mapping.setdefault(key, set()).add(val)

    rows = [(k, "; ".join(sorted(v))) for k, v in sorted(mapping.items())]
    df = pd.DataFrame(rows, columns=["abbreviation", "dissection_full_path"])
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT} ({len(df)} ROIs; the dataset carries 108 distinct ROI "
          f"labels; 'A35-36' and 'Gpe' are label variants of 'A35-A36'/'GPe' "
          f"with empty dissection metadata)")


if __name__ == "__main__":
    main()
