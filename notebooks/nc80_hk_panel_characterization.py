# -*- coding: utf-8 -*-
"""nc80 bio m1/Q5: characterisation of the HRT Atlas anchor panel.

bio m1: "The housekeeping panel is atypical and is never characterised."
Requested: expression-rank distribution, functional-class composition,
overlap with canonical HK sets. (The Note 8 ACTB/GAPDH non-member
disclosure already exists; this script supplies the missing panel
characterisation.)

Sources:
  - Panel: data/housekeeping/Human_Mouse_Common.csv (1,130 rows, 1,129
    unique human symbols; human column, as loaded by the analysis code).
  - Canonical HK comparison sets:
      * Eisenberg & Levanon 2013 constitutive list (3,804);
      * classical reference genes (ACTB, GAPDH, B2M, PPIA, EEF1A1, RPLP0,
        HPRT1, TBP, SDHA, GUSB, YWHAZ, ...).
  - Expression ranks: GTEx v8 RSEM gene TPM (7,862 samples,
    log2(TPM+0.001) scale); per-gene mean across samples; percentile
    rank among the 60,499 mapped genes (100 = most highly expressed).

Outputs: results/nc80_hk_panel_characterization.csv (per-set summary)
         results/nc80_hk_panel_characterization.txt (full log)
"""
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HK_HRT = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
HK_EL = ROOT / "data" / "housekeeping" / "eisenberg_levanon_2013_hk.txt"
GTEX = ROOT / "data" / "gtex" / "gtex_RSEM_gene_tpm.gz"
PROBEMAP = ROOT / "data" / "tcga" / "probemap.tsv"
OUT_CSV = ROOT / "results" / "nc80_hk_panel_characterization.csv"
OUT_TXT = ROOT / "results" / "nc80_hk_panel_characterization.txt"

lines = []
def log(msg=""):
    print(msg, flush=True)
    lines.append(str(msg))

# ---- gene sets ----
hrt_rows = pd.read_csv(HK_HRT, sep=";")
hrt_all = hrt_rows["Human"].dropna().astype(str).tolist()
hrt = set(hrt_all)
el = set(l.split("\t")[0].strip() for l in HK_EL.read_text().splitlines()
         if l.strip())
canonical = ["ACTB", "GAPDH", "B2M", "PPIA", "EEF1A1", "RPLP0", "HPRT1",
             "TBP", "SDHA", "GUSB", "YWHAZ", "ACTG1", "RPL13", "RPS18",
             "PGK1", "LDHA", "UBC", "18S"]
log(f"panel rows={len(hrt_all)} unique symbols={len(hrt)}")
dups = [g for g, c in Counter(hrt_all).items() if c > 1]
log(f"duplicate symbols in file: {dups}")
log(f"Eisenberg-Levanon list: {len(el)} genes; overlap with HRT: "
    f"{len(hrt & el)} ({len(hrt & el)/len(hrt):.1%} of the panel)")
log(f"classical reference genes in HRT: "
    f"{sorted(g for g in canonical if g in hrt) or 'none'}")

# ---- functional-class composition (prefix rules) ----
def func_class(g):
    if g.startswith(("MRPL", "MRPS")):
        return "mitochondrial ribosomal"
    if g.startswith(("RPL", "RPS")) and not g.endswith("BP1"):
        return "cytoplasmic ribosomal"
    if g.startswith(("HNRNP", "SRSF", "SNR", "ELAV", "RBM", "PCBP",
                     "SNU", "SF")):
        return "RNA binding / splicing"
    if g.startswith(("HSP", "DNAJ", "CCT")):
        return "chaperone"
    if g.startswith("EEF"):
        return "translation elongation"
    if g.startswith(("ACT", "TUB", "VCL", "TLN", "MYH", "MYL")):
        return "cytoskeleton"
    if g.startswith("RAB"):
        return "RAB GTPase (vesicle trafficking)"
    if g.startswith(("ATP", "COX", "NDU", "UQC", "SDH", "MT-")):
        return "mitochondrial energy metabolism"
    return "other"
comp = Counter(func_class(g) for g in hrt)
log("functional-class composition of the panel:")
for k, v in sorted(comp.items(), key=lambda x: -x[1]):
    log(f"  {k}: {v} ({v/len(hrt):.1%})")

ribo_members = {g for g in hrt if func_class(g) == "cytoplasmic ribosomal"}
log(f"cytoplasmic ribosomal members: {sorted(ribo_members)}")
log("note: the single RPS-prefixed member RPS19BP1 encodes an RPS19-"
    "interacting chromatin factor, not a ribosomal structural protein")

# ---- GTEx expression ranks ----
log("computing per-gene mean expression over GTEx (7,862 samples) ...")
pm = pd.read_csv(PROBEMAP, sep="\t", dtype=str)
ensg2sym = dict(zip(pm["id"], pm["gene"]))
means = {}
CH = 2000
for chunk in pd.read_csv(GTEX, sep="\t", index_col=0, chunksize=CH):
    idx = [ensg2sym.get(i, i) for i in chunk.index]
    m = chunk.mean(axis=1).to_numpy()
    for s, v in zip(idx, m):
        # first occurrence wins (probe map may duplicate symbols)
        if s not in means or v > means[s]:
            means[s] = float(v)
log(f"genes with expression data: {len(means)}")

vals = pd.Series(means)
ranks = vals.rank(pct=True, ascending=True) * 100  # 100 = most expressed

def rank_stats(syms, label):
    have = [g for g in syms if g in ranks.index]
    if not have:
        log(f"{label}: none mapped")
        return None
    r = ranks[have]
    return {"set": label, "n_total": len(syms), "n_mapped": len(have),
            "median_pct": float(r.median()),
            "q25_pct": float(r.quantile(.25)),
            "q75_pct": float(r.quantile(.75)),
            "min_pct": float(r.min()), "max_pct": float(r.max())}

rows = []
for syms, label in [(sorted(hrt), "HRT panel (1,129)"),
                    (sorted(el), "Eisenberg-Levanon 2013"),
                    ([g for g in canonical if g in ranks.index],
                     "classical reference genes")]:
    st = rank_stats(syms, label)
    if st:
        rows.append(st)
        log(f"{label}: mapped {st['n_mapped']}/{st['n_total']}, "
            f"median expression percentile {st['median_pct']:.1f} "
            f"(IQR {st['q25_pct']:.1f}-{st['q75_pct']:.1f}, "
            f"range {st['min_pct']:.1f}-{st['max_pct']:.1f})")

# per-gene rank table for the canonical genes for narrative use
can_ranks = {g: round(float(ranks[g]), 1) for g in canonical
             if g in ranks.index}
log(f"classical reference gene expression percentiles: {can_ranks}")

pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
comp_df = pd.DataFrame(sorted(comp.items(), key=lambda x: -x[1]),
                       columns=["functional_class", "n_genes"])
comp_df.to_csv(OUT_CSV.with_name(
    "nc80_hk_panel_functional_classes.csv"), index=False)
log(f"saved: {OUT_CSV}")
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("DONE")
