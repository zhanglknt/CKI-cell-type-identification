# -*- coding: utf-8 -*-
"""
nc52_brain_extract.py — Shared extraction for the NC v52 brain revisions.

One-time extraction reused by all nc52 brain analyses (A2 donor bootstrap,
C1 quality regression, C2 combined control). Two sequential passes over
data/brain/Nonneurons.h5ad (888,263 nuclei x 59,480 genes):

  pass 1: global gene sums (HVG selection, identical convention to
          notebooks/86/96: HRT Atlas HK + top-5000 non-HK by mean) and
          per-cell total counts; per-cell detected genes come free from
          indptr diffs.
  pass 2: per-cell CSR on the reduced gene set for Astrocyte + Bergmann
          glia cells (needed for cell-level equal-n downsampling under
          donor resampling).

Also aggregates RNA-quality proxies. NOTE: the Siletti atlas obs carries
NO PMI/RIN and no per-cell QC columns (checked: obs has only ontology /
dissection / donor / roi / sample fields), so detected genes per nucleus
and total UMI per nucleus are computed from the matrix and used as
proxies (declared in the audit).

Outputs (results/):
  nc52_brain_ab_cells.npz        CSR (data uint16, indices uint16,
                                 indptr int64) for Astrocyte+Bergmann
                                 cells on the reduced gene set
  nc52_brain_ab_cellmeta.csv     per-cell ct/donor/roi/sample codes
  nc52_brain_genes.json          reduced-gene layout (HK positions)
  nc52_brain_group_counts.csv    per (ct, roi, donor) cell counts, all
                                 classes (allocation under resampling)
  nc52_brain_quality_classlib.csv     per (ct, sample_id) quality agg
  nc52_brain_quality_classregion.csv  per (ct, roi) quality agg

Seed: no randomness here (deterministic extraction).
"""
import json
import sys
import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

H5 = PROJECT_ROOT / "data" / "brain" / "Nonneurons.h5ad"
HK_FILE = PROJECT_ROOT / "cki" / "data" / "hrt_atlas.csv"
OUT = PROJECT_ROOT / "results"

CT_COL = "supercluster_term"
ROI_COL = "roi"
SAMPLE_COL = "sample_id"
DONOR_COL = "donor_id"
N_HVG = 5000
TARGET_CTS = ["Astrocyte", "Bergmann glia"]

_t0 = time.time()


def log(msg):
    print(f"[{time.time()-_t0:7.0f}s] {msg}", flush=True)


hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_human = set(hk_df["Human"].dropna().astype(str))

f = h5py.File(H5, "r")
X = f["X"]
indptr = X["indptr"][:].astype(np.int64)
N_CELLS = indptr.shape[0] - 1

vg = f["var"]["Gene"]
if isinstance(vg, h5py.Dataset):
    var_gene = [x.decode() if isinstance(x, bytes) else str(x) for x in vg[:]]
else:
    cats = [x.decode() if isinstance(x, bytes) else str(x) for x in vg["categories"][:]]
    codes = vg["codes"][:]
    var_gene = [cats[c] if c >= 0 else None for c in codes]
N_GENES = len(var_gene)
log(f"shape: ({N_CELLS}, {N_GENES})")


def read_codes(name):
    g = f["obs"][name]
    cats = np.array([x.decode() if isinstance(x, bytes) else str(x)
                     for x in g["categories"][:]], dtype=object)
    return cats, g["codes"][:]


ct_cats, ct_codes = read_codes(CT_COL)
roi_cats, roi_codes = read_codes(ROI_COL)
samp_cats, samp_codes = read_codes(SAMPLE_COL)
donor_cats, donor_codes = read_codes(DONOR_COL)

hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                             if s and s in hk_human}), dtype=int)
log(f"HK genes matched: {len(hk_global)}")

# ================================================================ pass 1
log("=== pass 1: global gene sums + per-cell total counts ===")
gene_sums = np.zeros(N_GENES)
cell_counts = np.zeros(N_CELLS)
BATCH = 100_000
for start in range(0, N_CELLS, BATCH):
    end = min(start + BATCH, N_CELLS)
    lo, hi = int(indptr[start]), int(indptr[end])
    data = X["data"][lo:hi].astype(np.float64)
    idx = X["indices"][lo:hi]
    gene_sums += np.bincount(idx, weights=data, minlength=N_GENES)
    row_nnz = np.diff(indptr[start:end + 1])
    row_id = np.repeat(np.arange(start, end), row_nnz)
    cell_counts += np.bincount(row_id, weights=data, minlength=N_CELLS)
gene_means = gene_sums / N_CELLS
cell_detected = np.diff(indptr)  # detected genes per nucleus (free)
log("pass 1 done")

# HVG selection (identical to scripts 86/96)
non_hk_mask = np.ones(N_GENES, dtype=bool)
non_hk_mask[hk_global] = False
non_hk_means = gene_means.copy()
non_hk_means[~non_hk_mask] = -np.inf
hvg_global = np.argsort(non_hk_means)[-N_HVG:][::-1]
keep_global = np.sort(np.union1d(hk_global, hvg_global))
is_hk_keep = np.isin(keep_global, hk_global)
N_KEEP = len(keep_global)
gene_map = np.full(N_GENES, -1, dtype=np.int32)
gene_map[keep_global] = np.arange(N_KEEP, dtype=np.int32)
log(f"reduced set: {N_KEEP} genes (HK={int(is_hk_keep.sum())})")

with open(OUT / "nc52_brain_genes.json", "w") as jf:
    json.dump({
        "n_genes_total": N_GENES,
        "n_keep": int(N_KEEP),
        "keep_global": keep_global.tolist(),
        "is_hk_keep": is_hk_keep.tolist(),
        "hk_genes": [var_gene[i] for i in hk_global],
    }, jf)

# ================================================================ metadata / quality agg
ct_names = np.where(ct_codes >= 0, ct_cats[np.clip(ct_codes, 0, None)], None)
meta = pd.DataFrame({
    "ct": ct_names,
    "roi": roi_cats[np.clip(roi_codes, 0, None)],
    "sample": samp_cats[np.clip(samp_codes, 0, None)],
    "donor": donor_cats[np.clip(donor_codes, 0, None)],
    "detected": cell_detected,
    "total_counts": cell_counts,
})
meta = meta[meta["ct"].notna()].reset_index(drop=True)

# group counts per (ct, roi, donor) — all classes
gc = (meta.groupby(["ct", "roi", "donor"]).size()
      .reset_index(name="n_cells"))
gc.to_csv(OUT / "nc52_brain_group_counts.csv", index=False)
log(f"group counts: {len(gc)} (ct, roi, donor) rows")


def quality_agg(df, keys):
    g = df.groupby(keys)
    out = g.agg(n_cells=("detected", "size"),
                mean_detected=("detected", "mean"),
                sd_detected=("detected", "std"),
                mean_total_counts=("total_counts", "mean"),
                sd_total_counts=("total_counts", "std")).reset_index()
    return out


quality_agg(meta, ["ct", "sample", "donor", "roi"]).to_csv(
    OUT / "nc52_brain_quality_classlib.csv", index=False)
quality_agg(meta, ["ct", "roi"]).to_csv(
    OUT / "nc52_brain_quality_classregion.csv", index=False)
log("quality aggregates saved (no PMI/RIN in atlas; proxies used)")

# ================================================================ pass 2
log("=== pass 2: CSR extraction for Astrocyte + Bergmann glia ===")
ct_idx = {c: i for i, c in enumerate(ct_cats)}
target_codes = {ct_idx[c] for c in TARGET_CTS}
sel_mask = np.isin(ct_codes, list(target_codes))
sel_cells = np.where(sel_mask)[0]
N_SEL = len(sel_cells)
log(f"selected cells: {N_SEL}")

new_indptr = np.zeros(N_SEL + 1, dtype=np.int64)
new_indptr[1:] = np.diff(indptr)[sel_cells]  # upper bound (pre-filter)
# count kept nnz per selected cell requires mapping; do it in chunks
chunks_data = []
chunks_idx = []
kept_nnz = np.zeros(N_SEL, dtype=np.int64)
CH = 20000
for cs in range(0, N_SEL, CH):
    ce = min(cs + CH, N_SEL)
    cc = sel_cells[cs:ce]
    d0, d1 = int(indptr[cc[0]]), int(indptr[cc[-1] + 1])
    ch_idx = X["indices"][d0:d1]
    ch_dat = X["data"][d0:d1]
    ch_map = gene_map[ch_idx]
    ch_keep = ch_map >= 0
    for ci in range(ce - cs):
        r0 = int(indptr[cc[ci]]) - d0
        r1 = int(indptr[cc[ci] + 1]) - d0
        if r1 == r0:
            continue
        km = ch_keep[r0:r1]
        nk = int(km.sum())
        kept_nnz[cs + ci] = nk
        if nk:
            chunks_data.append(ch_dat[r0:r1][km].astype(np.uint16))
            chunks_idx.append(ch_map[r0:r1][km].astype(np.uint16))
new_indptr[1:] = np.cumsum(kept_nnz)
data_all = np.concatenate(chunks_data)
idx_all = np.concatenate(chunks_idx)
log(f"CSR built: {data_all.size/1e6:.1f}M nnz")

np.savez_compressed(
    OUT / "nc52_brain_ab_cells.npz",
    data=data_all, indices=idx_all, indptr=new_indptr,
    n_keep=N_KEEP)

cellmeta = pd.DataFrame({
    "ct": ct_cats[ct_codes[sel_cells]],
    "donor": donor_cats[donor_codes[sel_cells]],
    "roi": roi_cats[roi_codes[sel_cells]],
    "sample": samp_cats[samp_codes[sel_cells]],
    "detected": cell_detected[sel_cells],
    "total_counts": cell_counts[sel_cells],
})
cellmeta.to_csv(OUT / "nc52_brain_ab_cellmeta.csv", index=False)
log(f"cellmeta saved: {len(cellmeta)} cells")
f.close()
log("DONE")
