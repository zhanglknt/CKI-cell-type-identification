# -*- coding: utf-8 -*-
"""
79_kang_ifnb_demo.py — Real perturbation demonstration for CKI (v40 review E2-M2/M6).

Dataset: Kang et al. 2018 Science (GSE96583), PBMC from 8 donors, control vs
IFN-beta stimulation (6 h), droplet (10x) arm: lane 2.1 = control (14,619 cells),
lane 2.2 = stimulated (14,446 cells); donor identity via demuxlet (ind column);
cell-type annotations in batch2 tsne.df.

Design question (E2-M2): on a real perturbation dataset with a known ground
truth, does omega (CKI) separate the perturbation from donor drift better than
k_f-only or raw JS?

Analysis per cell type (singlets, annotated types, >= 50 cells per group):
  - Pseudobulk per (donor, condition): sum raw counts -> normalize_total(1e4)
    -> log1p (project convention).
  - Per-pair metrics (mouse-pilot per-pair DE hybrid scheme): k_n = JS on HK
    genes (HRT Atlas human column intersected with mapped symbols); k_f = JS on
    top-200 non-HK genes ranked by |mu_A - mu_B| (re-selected per pair);
    omega = k_f / k_n (kn_floor = 0); raw JS on all mapped genes as reference.
  - Comparisons: (a) stim-vs-ctrl within donor (8 per cell type);
    (b) donor-vs-donor within condition (28 ctrl + 28 stim);
    (c) split-half baseline: 6 random half-splits per (donor, condition) group.
  - Permutation test for (a): cell labels shuffled between the two conditions
    within donor (B = 1000, genes re-selected per permutation), one-sided
    upper-tail P = (#{null >= obs} + 1)/(B + 1).
  - AUC for classifying perturbation pairs (a) vs donor-drift pairs (b):
    computed for omega, k_f, and raw JS (exact rank statistic).

Outputs:
  results/kang_ifnb_demo_pairs.csv
  results/kang_ifnb_demo_summary.json / .txt

Run: python notebooks/79_kang_ifnb_demo.py
"""
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.io import mmread

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from cki.core import js_divergence  # noqa: E402

DATA = PROJECT_ROOT / "data" / "kang_ifnb"
OUT = PROJECT_ROOT / "results"
B_PERM = 1000
N_TOP_KF = 200
N_SPLIT_HALF = 6
MIN_GROUP_CELLS = 50
SEED = 20260903

# ---------------------------------------------------------------- load data
print("[79] loading gene ids ...", flush=True)
gene_ids = []
with gzip.open(DATA / "GSE96583_genes.txt.gz", "rt") as f:
    f.readline()  # header "x"
    for line in f:
        # lines look like: "1""ENSG00000243485"  (R write.table, quoted, no sep)
        parts = line.strip().strip('"').split('"')
        if len(parts) >= 2 and parts[-1]:
            gene_ids.append(parts[-1])
        else:
            gene_ids.append("")
n_declared = 35635  # mtx row count; genes.txt lists the first 32,738 rows
gene_ids = gene_ids + [""] * (n_declared - len(gene_ids))
gene_ids = np.array(gene_ids)
print(f"  genes in mtx: {len(gene_ids)} ({np.sum(gene_ids != '')} annotated)")

ensg2sym = {}
with open(DATA / "ensg2sym.tsv", encoding="utf-8") as f:
    header = f.readline()
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 2 and parts[0] and parts[1]:
            ensg2sym[parts[0]] = parts[1]

# map + deduplicate symbols (keep the first ENSG per symbol)
sym_of_row = np.array([ensg2sym.get(g, "") for g in gene_ids])
keep_rows, seen = [], set()
for i, s in enumerate(sym_of_row):
    if s and s not in seen:
        seen.add(s)
        keep_rows.append(i)
keep_rows = np.array(keep_rows)
gene_syms = sym_of_row[keep_rows]
print(f"  mapped unique symbols: {len(gene_syms)}")

print("[79] loading count matrices ...", flush=True)
X1 = mmread(DATA / "GSM2560248_2.1.mtx.gz").tocsr()  # genes x cells (ctrl lane)
X2 = mmread(DATA / "GSM2560249_2.2.mtx.gz").tocsr()  # genes x cells (stim lane)
print(f"  lane1(ctrl): {X1.shape}, lane2(stim): {X2.shape}")

X = sp.hstack([X1, X2]).tocsr().T  # cells x genes
X = X[:, keep_rows].tocsr()
del X1, X2
n_cells, n_genes = X.shape
print(f"  combined: {X.shape}")


def read_barcodes(path):
    with gzip.open(path, "rt") as f:
        return [l.strip() for l in f]


barcodes = read_barcodes(DATA / "GSM2560248_barcodes.tsv.gz") + read_barcodes(
    DATA / "GSM2560249_barcodes.tsv.gz"
)
assert len(barcodes) == n_cells

# metadata from batch2 tsne.df: barcode, tsne1, tsne2, ind, stim, cluster, cell, multiplets
# NOTE: 313 barcodes appear in both lanes; join via ordered multimap (lane1
# cells consume their tsne copies first, lane2 cells the remaining ones).
from collections import defaultdict  # noqa: E402

tsne_rows = []
with gzip.open(DATA / "GSE96583_batch2.total.tsne.df.tsv.gz", "rt") as f:
    f.readline()  # header
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) >= 8:
            tsne_rows.append(p)

by_bc = defaultdict(list)
for i, p in enumerate(tsne_rows):
    by_bc[p[0]].append(i)

assign = []
n_lane1 = 14619
for i, bc in enumerate(barcodes):
    lst = by_bc.get(bc)
    if not lst and i >= n_lane1 and bc.endswith("-1"):
        # 313 lane-2 barcodes colliding with lane 1 are renamed to "<bc>1"
        # (e.g. "AAACGCTGTGTCAG-1" -> "AAACGCTGTGTCAG-11") in the tsne.df
        lst = by_bc.get(bc + "1")
    if not lst:
        raise KeyError(f"barcode {bc} not in tsne.df")
    assign.append(lst.pop(0))
assert not any(lst for lst in by_bc.values()), "unconsumed tsne rows remain"

p_assign = [tsne_rows[i] for i in assign]
inds = np.array([p[3] for p in p_assign])
stims = np.array([p[4] for p in p_assign])
ctypes = np.array([p[6] for p in p_assign])
mults = np.array([p[7] for p in p_assign])
# lane-implied condition must match tsne.df stim
lane_stim = np.array(["ctrl"] * 14619 + ["stim"] * 14446)
assert (lane_stim == stims).all(), "lane/condition mismatch"

ok = (mults == "singlet") & (ctypes != "NA") & (ctypes != "Megakaryocytes")
X = X[ok].tocsr()
inds, stims, ctypes = inds[ok], stims[ok], ctypes[ok]
print(f"  singlets kept: {X.shape[0]} cells; cell types: {sorted(set(ctypes))}")

# ---------------------------------------------------------------- HK genes
import csv as _csv  # noqa: E402

hk_syms = set()
with open(PROJECT_ROOT / "cki" / "data" / "hrt_atlas.csv", encoding="utf-8") as f:
    r = _csv.DictReader(f, delimiter=";")
    if "Human" not in r.fieldnames:
        f.seek(0)
        r = _csv.DictReader(f, delimiter=",")
    for row in r:
        h = row.get("Human", "").strip()
        if h:
            hk_syms.add(h)
sym_arr = np.array(gene_syms)
hk_mask = np.isin(sym_arr, list(hk_syms))
hk_idx = np.where(hk_mask)[0]
non_hk_idx = np.where(~hk_mask)[0]
print(f"  HK genes (HRT Atlas human) present: {len(hk_idx)} of {len(hk_syms)}")

# ---------------------------------------------------------------- helpers


def make_pb(row_idx):
    """Pseudobulk: sum counts -> normalize 1e4 -> log1p. Returns dense (n_genes,)."""
    v = np.asarray(X[row_idx].sum(axis=0)).ravel().astype(float)
    tot = v.sum()
    if tot > 0:
        v = v / tot * 1e4
    return np.log1p(v)


def pair_metrics(pb_a, pb_b):
    """Per-pair DE hybrid: k_n on HK, k_f on top-200 non-HK by |mu diff|, omega."""
    k_n = js_divergence(pb_a[hk_idx], pb_b[hk_idx])
    diff = np.abs(pb_a - pb_b)
    cand = non_hk_idx[diff[non_hk_idx] > 0]
    if len(cand) > N_TOP_KF:
        order = np.argsort(-diff[cand])[:N_TOP_KF]
        cand = cand[order]
    k_f = js_divergence(pb_a[cand], pb_b[cand])
    omega = k_f / k_n if k_n > 0 else np.inf
    raw = js_divergence(pb_a, pb_b)
    return k_n, k_f, omega, raw


def auc(pos, neg):
    """Exact rank AUC (Mann-Whitney)."""
    from scipy.stats import rankdata

    vals = np.concatenate([pos, neg])
    ranks = rankdata(vals)
    r_pos = ranks[: len(pos)]
    return float((r_pos.sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- main loop
cell_types = sorted(set(ctypes))
rows = []  # pair-level rows
summary = {"cell_types": {}, "config": {
    "B_PERM": B_PERM, "N_TOP_KF": N_TOP_KF, "N_SPLIT_HALF": N_SPLIT_HALF,
    "SEED": SEED, "min_group_cells": MIN_GROUP_CELLS,
}}

t0 = time.time()
for ct in cell_types:
    sel = ctypes == ct
    n_ct = int(sel.sum())

    # NOTE: groups store GLOBAL row indices into X (cells x genes)
    groups = {}
    for d in sorted(set(inds[sel])):
        for cond in ("ctrl", "stim"):
            m = sel & (inds == d) & (stims == cond)
            if m.sum() >= MIN_GROUP_CELLS:
                groups[(d, cond)] = np.where(m)[0]

    donors = sorted({d for d, c in groups if (d, "ctrl") in groups and (d, "stim") in groups})
    if len(donors) < 4:
        print(f"  [skip] {ct}: only {len(donors)} usable donors", flush=True)
        continue

    pbs = {g: make_pb(ix) for g, ix in groups.items()}

    # (a) stim vs ctrl within donor (+ permutation null)
    for d in donors:
        ga, gb = groups[(d, "ctrl")], groups[(d, "stim")]
        k_n, k_f, omega, raw = pair_metrics(pbs[(d, "ctrl")], pbs[(d, "stim")])
        # permutation: shuffle cell labels within donor
        both = np.concatenate([ga, gb])
        n1 = len(ga)
        null = np.empty(B_PERM)
        for b in range(B_PERM):
            pm = rng.permutation(len(both))
            pa = make_pb(both[pm[:n1]])
            pb_ = make_pb(both[pm[n1:]])
            _, _, null[b], _ = pair_metrics(pa, pb_)
        p_val = (np.sum(null >= omega) + 1) / (B_PERM + 1)
        rows.append({
            "cell_type": ct, "comparison": "stim_vs_ctrl", "donor": d,
            "n_cells_a": int(len(ga)), "n_cells_b": int(len(gb)),
            "k_n": k_n, "k_f": k_f, "omega": omega, "raw_js": raw,
            "perm_P": p_val, "null_mean": float(null.mean()), "null_sd": float(null.std()),
        })

    # (b) donor vs donor within condition
    for cond in ("ctrl", "stim"):
        for i, d1 in enumerate(donors):
            for d2 in donors[i + 1:]:
                if (d1, cond) in groups and (d2, cond) in groups:
                    k_n, k_f, omega, raw = pair_metrics(pbs[(d1, cond)], pbs[(d2, cond)])
                    rows.append({
                        "cell_type": ct, "comparison": f"donor_vs_donor_{cond}",
                        "donor": f"{d1}|{d2}", "n_cells_a": int(len(groups[(d1, cond)])),
                        "n_cells_b": int(len(groups[(d2, cond)])),
                        "k_n": k_n, "k_f": k_f, "omega": omega, "raw_js": raw,
                        "perm_P": "", "null_mean": "", "null_sd": "",
                    })

    # (c) split-half baseline
    sh = []
    for g, ix in groups.items():
        for _ in range(N_SPLIT_HALF):
            pm = rng.permutation(len(ix))
            h = len(ix) // 2
            if h < 10:
                continue
            pa = make_pb(ix[pm[:h]])
            pb_ = make_pb(ix[pm[h:2 * h]])
            _, _, omega, _ = pair_metrics(pa, pb_)
            sh.append(omega)
            rows.append({
                "cell_type": ct, "comparison": "split_half",
                "donor": f"{g[0]}|{g[1]}", "n_cells_a": h, "n_cells_b": h,
                "k_n": "", "k_f": "", "omega": omega, "raw_js": "",
                "perm_P": "", "null_mean": "", "null_sd": "",
            })

    # (d) AUC: perturbation vs donor-drift
    om_sc = [r for r in rows if r["cell_type"] == ct and r["comparison"] == "stim_vs_ctrl"]
    kf_sc = [r for r in rows if r["cell_type"] == ct and r["comparison"] == "donor_vs_donor_ctrl"]
    kf_ss = [r for r in rows if r["cell_type"] == ct and r["comparison"] == "donor_vs_donor_stim"]
    negs = kf_sc + kf_ss
    auc_om = auc([r["omega"] for r in om_sc], [r["omega"] for r in negs])
    auc_kf = auc([r["k_f"] for r in om_sc], [r["k_f"] for r in negs])
    auc_raw = auc([r["raw_js"] for r in om_sc], [r["raw_js"] for r in negs])
    base = float(np.median(sh)) if sh else np.nan
    summary["cell_types"][ct] = {
        "n_cells": n_ct, "n_donors": len(donors),
        "median_omega_stim_ctrl": float(np.median([r["omega"] for r in om_sc])),
        "median_omega_donor_donor": float(np.median([r["omega"] for r in negs])),
        "median_omega_split_half": base,
        "omega_cal_stim_ctrl": float(np.median([r["omega"] for r in om_sc]) / base) if base else None,
        "omega_cal_donor_donor": float(np.median([r["omega"] for r in negs]) / base) if base else None,
        "n_sig_perm": int(sum(1 for r in om_sc if r["perm_P"] < 0.05)),
        "min_perm_P": float(min(r["perm_P"] for r in om_sc)),
        "auc_omega": auc_om, "auc_kf": auc_kf, "auc_raw_js": auc_raw,
    }
    print(
        f"  [{ct}] n={n_ct}, donors={len(donors)}, "
        f"omega(stim)={summary['cell_types'][ct]['median_omega_stim_ctrl']:.1f} "
        f"vs donor={summary['cell_types'][ct]['median_omega_donor_donor']:.1f} "
        f"vs split={base:.1f}, AUC omega={auc_om:.3f} kf={auc_kf:.3f} rawJS={auc_raw:.3f}",
        flush=True,
    )

print(f"[79] total elapsed {time.time()-t0:.0f}s")

# ---------------------------------------------------------------- outputs
import csv  # noqa: E402

with open(OUT / "kang_ifnb_demo_pairs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

with open(OUT / "kang_ifnb_demo_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

lines = ["Kang et al. 2018 IFN-beta PBMC: CKI perturbation demonstration (script 79)", "=" * 70,
         f"Design: {len(rows)} pairs; per-pair top-{N_TOP_KF} DE hybrid; HRT Atlas HK ({len(hk_idx)} matched);",
         f"permutation B = {B_PERM} (labels shuffled within donor); split-half baseline x{N_SPLIT_HALF}",
         ""]
for ct, s in summary["cell_types"].items():
    lines.append(
        f"[{ct}] n={s['n_cells']} cells, {s['n_donors']} donors | "
        f"median omega: stim-ctrl {s['median_omega_stim_ctrl']:.2f}, "
        f"donor-donor {s['median_omega_donor_donor']:.2f}, split-half {s['median_omega_split_half']:.2f} | "
        f"omega_cal: stim {s['omega_cal_stim_ctrl']:.2f} vs donor {s['omega_cal_donor_donor']:.2f} | "
        f"perm P<0.05: {s['n_sig_perm']}/{s['n_donors']} (min {s['min_perm_P']:.2e}) | "
        f"AUC omega {s['auc_omega']:.3f}, k_f {s['auc_kf']:.3f}, rawJS {s['auc_raw_js']:.3f}"
    )
txt = "\n".join(lines) + "\n"
with open(OUT / "kang_ifnb_demo_summary.txt", "w", encoding="utf-8") as f:
    f.write(txt)
print(txt)
