# -*- coding: utf-8 -*-
"""
nc49_pilot_kang_techrep.py — Kang batch1 go/no-go pilot (NC v49 对策 C, 第一步).

Data: GSE96583 batch1 (Kang et al. 2018), 8 unstimized donors across three 10x
lanes A/B/C. Lane A holds donors {1079,1154,1249,1598}, lane B holds
{1043,1085,1493,1511}, lane C holds ALL 8 donors. Therefore each donor appears
in exactly 2 lanes -> same-donor, same-condition (all ctrl), cross-lane
TECHNICAL REPLICATE pairs: the clean "neutral drift, no functional change"
contrast. Ground truth: no functional difference.

Per cell type (singlets, annotated, >= MIN_GROUP_CELLS cells in BOTH lanes
of the donor):
  - pseudobulk: sum raw counts -> normalize_total(1e4) -> log1p (script 79
    convention).
  - metrics per pair:
      k_n     = JS on HK genes (HRT Atlas human, intersected w/ mapped symbols)
      k_f     = JS on top-200 non-HK genes by |mu_A - mu_B| (per-pair reselect,
                manuscript hybrid scheme; script 79 pair_metrics)
      omega   = k_f / k_n   (kn_floor = 0, positivity guard only)
      raw_js  = JS on all mapped genes
      cosine  = 1 - cosine similarity of the two pseudobulk vectors
  - split-half baseline (T0): 6 random half-splits per (donor, lane) group,
    same metrics; used to calibrate (ratio pair-metric / median split-half
    metric of the same cell type).

Outputs:
  results/nc49_pilot_kang_techrep.csv   per-pair rows (techrep + split-half)
  results/audit/_nc49_pilot_kang_stdout.log   (run log; audit md written by hand)

Run:
  C:/Users/KnightZ/.workbuddy/binaries/python/envs/default/Scripts/python.exe
      -u notebooks/nc49_pilot_kang_techrep.py
"""
import gzip
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.io import mmread

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from cki.core import js_divergence  # noqa: E402

DATA = PROJECT_ROOT / "data" / "kang_ifnb"
RAW = DATA / "_raw"
OUT = PROJECT_ROOT / "results"
N_TOP_KF = 200
N_SPLIT_HALF = 6
B_NULL = 200
MIN_GROUP_CELLS = 50
SEED = 20260918
LANES = {"A": "GSM2560245", "B": "GSM2560246", "C": "GSM2560247"}


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- load genes
log("[pilot] loading gene ids ...")
gene_ids = []
with gzip.open(DATA / "GSE96583_genes.txt.gz", "rt") as f:
    f.readline()
    for line in f:
        parts = line.strip().strip('"').split('"')
        gene_ids.append(parts[-1] if len(parts) >= 2 and parts[-1] else "")
gene_ids = gene_ids + [""] * (32738 - len(gene_ids))
gene_ids = np.array(gene_ids)

ensg2sym = {}
with open(DATA / "ensg2sym.tsv", encoding="utf-8") as f:
    f.readline()
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) == 2 and p[0] and p[1]:
            ensg2sym[p[0]] = p[1]

sym_of_row = np.array([ensg2sym.get(g, "") for g in gene_ids])
keep_rows, seen = [], set()
for i, s in enumerate(sym_of_row):
    if s and s not in seen:
        seen.add(s)
        keep_rows.append(i)
keep_rows = np.array(keep_rows)
gene_syms = sym_of_row[keep_rows]
log(f"  mapped unique symbols: {len(gene_syms)}")

# ---------------------------------------------------------------- load lanes
log("[pilot] loading three lane matrices ...")
Xs, barcodes = {}, {}
for lane, gsm in LANES.items():
    X = mmread(RAW / f"{gsm}_{lane}.mat.gz").tocsr()  # genes x cells
    X = X[keep_rows].T.tocsr()  # cells x genes (dedup symbols)
    with gzip.open(RAW / f"{gsm}_barcodes.tsv.gz", "rt") as f:
        bc = [l.strip() for l in f]
    assert X.shape[0] == len(bc)
    Xs[lane], barcodes[lane] = X, bc
    log(f"  lane {lane}: {X.shape}")

# ---------------------------------------------------------------- metadata
log("[pilot] joining batch1 tsne.df metadata ...")
ts = pd.read_csv(DATA / "GSE96583_batch1.total.tsne.df.tsv.gz", sep="\t")

meta = []
for lane in LANES:
    sub = ts[ts["batch"] == lane]
    bc_set = set(barcodes[lane])
    # rename rule (script 79): colliding barcodes get an extra '1' in tsne.df
    idx_of = {b: i for i, b in enumerate(barcodes[lane])}
    rows = []
    for bc, (_, r) in zip(sub.index, sub.iterrows()):
        if bc in bc_set:
            pos = idx_of[bc]
        elif (bc + "1") in idx_of:
            pos = idx_of[bc + "1"]
        elif bc.endswith("1") and bc[:-1] in idx_of:
            pos = idx_of[bc[:-1]]
        else:
            raise KeyError(f"barcode {bc} (lane {lane}) unmatched")
        rows.append((pos, r["ind"], r["multiplets"], r["cell.type"]))
    df = pd.DataFrame(rows, columns=["pos", "ind", "multiplets", "cell_type"])
    df["lane"] = lane
    meta.append(df)
meta = pd.concat(meta, ignore_index=True)
log(f"  joined cells: {len(meta)}; lanes: {meta['lane'].value_counts().to_dict()}")

ok = (meta["multiplets"] == "singlet") & meta["cell_type"].notna() \
     & meta["ind"].notna() \
     & (meta["cell_type"] != "NA") & (meta["cell_type"] != "Megakaryocytes")
meta = meta[ok].reset_index(drop=True)
meta["cell_type"] = meta["cell_type"].astype(str)
meta["ind"] = meta["ind"].astype(int)
log(f"  singlets kept: {len(meta)}; cell types: {sorted(meta['cell_type'].unique())}")

# global row offset of each lane in the stacked matrix
offsets = {}
off = 0
for lane in LANES:
    offsets[lane] = off
    off += Xs[lane].shape[0]
X_all = sp.vstack([Xs[l] for l in LANES]).tocsr()
global_rows = (meta["pos"] + meta["lane"].map(offsets)).values
del Xs
X_all = X_all[global_rows].tocsr()
n_cells, n_genes = X_all.shape
log(f"  stacked matrix: {X_all.shape}")

# ---------------------------------------------------------------- HK genes
import csv  # noqa: E402

hk_syms = set()
with open(PROJECT_ROOT / "cki" / "data" / "hrt_atlas.csv", encoding="utf-8") as f:
    r = csv.DictReader(f, delimiter=";")
    if "Human" not in r.fieldnames:
        f.seek(0)
        r = csv.DictReader(f, delimiter=",")
    for row in r:
        h = row.get("Human", "").strip()
        if h:
            hk_syms.add(h)
sym_arr = np.array(gene_syms)
hk_idx = np.where(np.isin(sym_arr, list(hk_syms)))[0]
non_hk_idx = np.where(~np.isin(sym_arr, list(hk_syms)))[0]
log(f"  HK genes (HRT Atlas human) present: {len(hk_idx)}")

# ---------------------------------------------------------------- helpers
def make_pb(row_idx):
    v = np.asarray(X_all[row_idx].sum(axis=0)).ravel().astype(float)
    tot = v.sum()
    if tot > 0:
        v = v / tot * 1e4
    return np.log1p(v)


def pair_metrics(pb_a, pb_b):
    k_n = js_divergence(pb_a[hk_idx], pb_b[hk_idx])
    diff = np.abs(pb_a - pb_b)
    cand = non_hk_idx[diff[non_hk_idx] > 0]
    if len(cand) > N_TOP_KF:
        order = np.argsort(-diff[cand])[:N_TOP_KF]
        cand = cand[order]
    k_f = js_divergence(pb_a[cand], pb_b[cand])
    omega = k_f / k_n if k_n > 1e-15 else np.inf
    raw = js_divergence(pb_a, pb_b)
    na, nb = np.linalg.norm(pb_a), np.linalg.norm(pb_b)
    cos = 1.0 - float(pb_a @ pb_b / (na * nb)) if na > 0 and nb > 0 else 1.0
    return {"k_n": k_n, "k_f": k_f, "omega": omega, "raw_js": raw, "cosine": cos}


rng = np.random.default_rng(SEED)
rows = []
t0 = time.time()

# ---------------------------------------------------------------- pairs
cell_types = sorted(meta["cell_type"].unique())
for ct in cell_types:
    sel = meta["cell_type"] == ct
    groups = {}
    for d in sorted(meta.loc[sel, "ind"].dropna().unique()):
        d = int(d) if pd.notna(d) else d
        for lane in LANES:
            m = sel & (meta["ind"] == d) & (meta["lane"] == lane)
            if m.sum() >= MIN_GROUP_CELLS:
                groups[(d, lane)] = np.where(m)[0]
    donors = sorted({d for d, l in groups})
    pair_count = 0
    n_null = 0
    for d in donors:
        lanes_d = [l for l in LANES if (d, l) in groups]
        if len(lanes_d) < 2:
            continue
        for i in range(len(lanes_d)):
            for j in range(i + 1, len(lanes_d)):
                la, lb = lanes_d[i], lanes_d[j]
                ga, gb = groups[(d, la)], groups[(d, lb)]
                pba, pbb = make_pb(ga), make_pb(gb)
                m = pair_metrics(pba, pbb)
                # n-matched null: pool both lanes' cells, shuffle, split into
                # disjoint subsets of EXACT sizes (na, nb). Same donor, same
                # cell type, same n -> isolates the LANE effect from sampling
                # noise. B draws; store per-pair null distribution summary.
                pool = np.concatenate([ga, gb])
                nulls = []
                for _ in range(B_NULL):
                    pm = rng.permutation(len(pool))
                    nulls.append(pair_metrics(
                        make_pb(pool[pm[:len(ga)]]),
                        make_pb(pool[pm[len(ga):]])))
                for met in ["k_n", "k_f", "omega", "raw_js", "cosine"]:
                    nv = np.array([x[met] for x in nulls], dtype=float)
                    m[f"null_med_{met}"] = float(np.median(nv))
                    m[f"null_p95_{met}"] = float(np.percentile(nv, 95))
                    # one-sided FPR element: observed above its own null p95
                    m[f"exceed_{met}"] = int(m[met] > m[f"null_p95_{met}"])
                    # paired calibration: observed / null median
                    with np.errstate(divide="ignore", invalid="ignore"):
                        m[f"cal_{met}"] = (m[met] / m[f"null_med_{met}"]
                                           if m[f"null_med_{met}"] > 0 else np.inf)
                m.update({
                    "cell_type": ct, "comparison": "techrep_crosslane",
                    "donor": d, "lane_a": la, "lane_b": lb,
                    "n_cells_a": int(len(ga)), "n_cells_b": int(len(gb)),
                })
                rows.append(m)
                pair_count += 1
                n_null += B_NULL
    log(f"  [{ct}] techrep pairs={pair_count} (n-matched null draws x{B_NULL}) "
        f"({time.time()-t0:.0f}s elapsed)")

# ---------------------------------------------------------------- save
df = pd.DataFrame(rows)
out_csv = OUT / "nc49_pilot_kang_techrep.csv"
df.to_csv(out_csv, index=False)
log(f"[pilot] saved {out_csv} ({len(df)} rows)")

# ---------------------------------------------------------------- summary
log("\n[pilot] === summary ===")
metrics = ["k_n", "k_f", "omega", "raw_js", "cosine"]
tr = df[df.comparison == "techrep_crosslane"]
lines = [
    "Kang batch1 technical-replicate pilot (nc49, n-matched null)",
    "=" * 72,
    f"techrep pairs: {len(tr)} (each vs its own n-matched lane-shuffled null, "
    f"B={B_NULL})",
    "",
    "Per-metric: observed median | paired cal = observed/null_med (per pair, "
    "then median) | FPR = fraction of pairs exceeding their own null p95",
    "",
    f"{'metric':<10} {'obs_med':>10} {'null_med':>10} {'cal_med':>10} "
    f"{'cal_iqr':>16} {'FPR':>7}",
]
for met in metrics:
    cal_v = tr[f"cal_{met}"]
    fpr = tr[f"exceed_{met}"].mean()
    lines.append(
        f"{met:<10} {tr[met].median():>10.4g} {tr[f'null_med_{met}'].median():>10.4g} "
        f"{cal_v.median():>10.4g} [{cal_v.quantile(.25):.3g},{cal_v.quantile(.75):.3g}] "
        f"{fpr:>7.2%}")
txt = "\n".join(lines)
log(txt)

per_ct = tr.groupby("cell_type")[
    [f"cal_{m}" for m in metrics] + [f"exceed_{m}" for m in metrics]].median()
log("\nper-cell-type calibrated (cal, median) & FPR:\n" + per_ct.to_string())

with open(OUT / "audit" / "_nc49_pilot_kang_summary.txt", "w", encoding="utf-8") as f:
    f.write(txt + "\n\nper-CT cal & FPR:\n" + per_ct.to_string() + "\n")
log("[pilot] done")
