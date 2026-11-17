"""
#nc80 M-J (iii): 10x modular off-anchor TPR@FPR operating characteristic
=======================================================================
Responds to nc80 methods M3 / editor R8: "no 10x functional-module
operating characteristic in omega's intended regime -- the only 10x
ground-truth simulation (notebook 101, SI 3.11) injects broad mean
shifts (G = 100/500, additive fold 2-8) that sit exactly in omega's
disclosed anchor-visibility blind spot."

Design: a semi-synthetic *modular* injection on the Kang 10x PBMC
background (GSE96583 batch 1+2, same loading path as notebooks/79 and
101), evaluated at omega's stated operating window:

  - donor-paired split-half: for each eligible (donor, cell_type) ctrl
    group with >= 2n cells, resample 2n cells and split into disjoint
    A/B halves of n each (ground-truth functional divergence = 0);
  - multiplicative off-anchor module shift: a fixed module of 200
    non-HK genes (HRT HK genes excluded, module seeds {42, 137, 2024},
    eligible = >= 1 CPM in the pooled ctrl pseudobulk of the group)
    is shifted in group B by 2**delta (log2 FC), delta in {0.25, 0.5, 1.0}
    -- the modular design of notebook 45, transplanted to 10x;
  - n grid: 50, 100, 200 cells per group (the manuscript's stated
    operating window);
  - metrics: omega, k_f, k_n, raw JS, cosine, and the two covariance-
    whitened baselines of nc80_mj_mahalanobis_sim.py (mahal_pc,
    mahal_diag), whitening fit ONLY on the null split-half replicates
    of the same n;
  - TPR @ FPR 5%: threshold = 95th percentile of the first half of the
    null replicates, TPR evaluated on the held-out null half and on the
    effect replicates; plus rank AUC (effect vs null).

Outputs:
  results/nc80_mj_kang_modular_raw.csv        (all replicates)
  results/nc80_mj_kang_modular_tpr.csv        (per n x delta x metric:
                                               FPR, TPR@FPR5, AUC)
  results/nc80_mj_kang_modular_metrics.json  (design + eligibility)
"""

import csv
import gzip
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.io import mmread
from scipy.stats import rankdata

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from cki.core import js_divergence  # noqa: E402

DATA = PROJECT_ROOT / "data" / "kang_ifnb"
OUT = PROJECT_ROOT / "results"

SEED = 42
N_TOP_KF = 200
N_HVG = 5000
MODULE_SIZE = 200
POOL_SIZE = 500
MODULE_SEEDS = [42, 137, 2024]
N_GRID = [50, 100, 200]
DELTA_GRID = [0.25, 0.5, 1.0]
N_NULL_REPS = 200
N_REPS = 100
FPR_TARGET = 0.05
N_PC = 20
RIDGE = 1e-6
METRIC_COLS = ["omega", "k_f", "k_n", "k_total", "cosine",
               "mahal_pc", "mahal_diag"]

# smoke test only (NC80_MJ_SMOKE=1): tiny grid, not the published design
import os  # noqa: E402
if os.environ.get("NC80_MJ_SMOKE"):
    N_GRID, N_NULL_REPS, N_REPS = [50], 20, 3
    OUT = OUT / "_smoke"
    OUT.mkdir(parents=True, exist_ok=True)

# ======================================================================
# Data loading (mirrors notebooks/101_competitors_v44.py)
# ======================================================================
print("[nc80-mj-kang] loading gene ids ...", flush=True)
gene_ids = []
with gzip.open(DATA / "GSE96583_genes.txt.gz", "rt") as f:
    f.readline()
    for line in f:
        parts = line.strip().strip('"').split('"')
        gene_ids.append(parts[-1] if len(parts) >= 2 and parts[-1] else "")
n_declared = 35635
gene_ids = np.array(gene_ids + [""] * (n_declared - len(gene_ids)))

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
print(f"  mapped unique symbols: {len(gene_syms)}", flush=True)

print("[nc80-mj-kang] loading count matrices ...", flush=True)
X1 = mmread(DATA / "GSM2560248_2.1.mtx.gz").tocsr()
X2 = mmread(DATA / "GSM2560249_2.2.mtx.gz").tocsr()
X = sp.hstack([X1, X2]).tocsr().T
X = X[:, keep_rows].tocsr()
del X1, X2
n_cells, n_genes = X.shape
print(f"  combined: {X.shape}", flush=True)


def read_barcodes(path):
    with gzip.open(path, "rt") as f:
        return [l.strip() for l in f]


barcodes = read_barcodes(DATA / "GSM2560248_barcodes.tsv.gz") + read_barcodes(
    DATA / "GSM2560249_barcodes.tsv.gz")
assert len(barcodes) == n_cells

tsne_rows = []
with gzip.open(DATA / "GSE96583_batch2.total.tsne.df.tsv.gz", "rt") as f:
    f.readline()
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
        lst = by_bc.get(bc + "1")
    if not lst:
        raise KeyError(f"barcode {bc} not in tsne.df")
    assign.append(lst.pop(0))

p_assign = [tsne_rows[i] for i in assign]
inds = np.array([p[3] for p in p_assign])
stims = np.array([p[4] for p in p_assign])
ctypes = np.array([p[6] for p in p_assign])
mults = np.array([p[7] for p in p_assign])

ok = (mults == "singlet") & (ctypes != "NA") & (ctypes != "Megakaryocytes")
X = X[ok].tocsr()
inds, stims, ctypes = inds[ok], stims[ok], ctypes[ok]
print(f"  singlets kept: {X.shape[0]} cells", flush=True)

# HK genes (HRT atlas, same convention as notebooks 79/101)
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
print(f"  HK genes present: {len(hk_idx)}", flush=True)

# eligibility: ctrl cells per (donor, cell type)
ctrl_mask = stims == "ctrl"
combos = []
for ct in sorted(set(ctypes[ctrl_mask])):
    for d in sorted(set(inds[ctrl_mask & (ctypes == ct)])):
        m = ctrl_mask & (ctypes == ct) & (inds == d)
        n_c = int(m.sum())
        if n_c >= 2 * N_GRID[0]:
            combos.append((ct, d, n_c))
combos_df = pd.DataFrame(combos, columns=["cell_type", "donor", "n_ctrl"])
print(f"  eligible (donor, cell_type) ctrl groups "
      f"(>= {2 * N_GRID[0]} cells): {len(combos)}", flush=True)
print(combos_df.to_string(index=False))

combo_list = [(ct, d) for ct, d, _ in combos]


def make_pb(mat, row_idx):
    """Pseudobulk: sum counts -> normalize 1e4 -> log1p (101 convention)."""
    v = np.asarray(mat[row_idx].sum(axis=0)).ravel().astype(float)
    tot = v.sum()
    if tot > 0:
        v = v / tot * 1e4
    return np.log1p(v)


def cki_components(pb_a, pb_b):
    k_n = js_divergence(pb_a[hk_idx], pb_b[hk_idx])
    diff = np.abs(pb_a - pb_b)
    cand = non_hk_idx[diff[non_hk_idx] > 0]
    if len(cand) > N_TOP_KF:
        cand = cand[np.argsort(-diff[cand])[:N_TOP_KF]]
    k_f = js_divergence(pb_a[cand], pb_b[cand])
    return k_n, k_f


def base_metrics(pb_a, pb_b):
    k_n, k_f = cki_components(pb_a, pb_b)
    omega = k_f / k_n if k_n > 1e-15 else np.inf
    kt = js_divergence(pb_a, pb_b)
    na, nb = np.linalg.norm(pb_a), np.linalg.norm(pb_b)
    cosine = 1.0 - float(np.dot(pb_a, pb_b) / (na * nb)) if na > 0 and nb > 0 else 1.0
    return {"omega": omega, "k_f": k_f, "k_n": k_n, "k_total": kt,
            "cosine": cosine}


# Module pool mirrors notebook 45: HK genes plus the top-5,000 non-HK genes by
# mean expression, module = first 200 of a 500-gene draw per seed.
ctrl_idx = np.where(ctrl_mask)[0]
gene_means = np.asarray(X[ctrl_idx].mean(axis=0)).ravel()
non_hk_means = gene_means.copy()
non_hk_means[hk_idx] = -np.inf
eligible_mod = np.sort(np.argsort(non_hk_means)[-N_HVG:])
print(f"  module pool (top-{N_HVG} non-HK by mean expression): "
      f"{len(eligible_mod)}", flush=True)
assert len(eligible_mod) >= 2000, "module pool too small"
_pb_ctrl = make_pb(X, ctrl_idx)
_raw_ctrl = np.asarray(X[ctrl_idx].sum(axis=0)).ravel()
print(f"  total UMI in pooled ctrl PB: {_raw_ctrl.sum():.0f}", flush=True)
module_pools = {s: np.sort(np.random.RandomState(s).choice(
    eligible_mod, size=POOL_SIZE, replace=False)) for s in MODULE_SEEDS}
for s in MODULE_SEEDS:
    mod = module_pools[s][:MODULE_SIZE]
    print(f"  module seed {s}: {MODULE_SIZE} genes, "
          f"{100 * _raw_ctrl[mod].sum() / _raw_ctrl.sum():.2f}% of pooled ctrl "
          f"counts", flush=True)


def draw_pair(rng, n, combo_index=None):
    """Donor-paired split-half: 2n ctrl cells of one (donor, cell type) group,
    split into disjoint halves of n.  combo_index fixes the group (stratified
    scheduling); None draws it at random."""
    elig = [i for i, (ct, d, nc_) in enumerate(combos) if nc_ >= 2 * n]
    ci = elig[rng.randint(len(elig))] if combo_index is None else combo_index
    ct, d = combo_list[ci][0], combo_list[ci][1]
    pool = np.where(ctrl_mask & (ctypes == ct) & (inds == d))[0]
    pick = rng.choice(pool, size=2 * n, replace=False)
    return pick[:n], pick[n:], d, ct


def pb_pair(rows_a, rows_b, delta, mod):
    """Pseudobulk pair for a fixed cell set; optional module shift on B.

The injected fold change is applied without integer rounding: at a median
    depth of ~1,300 UMI per 10x cell, round(1 * 2**0.25) = 1, so rounding would
    silently absorb the smallest shifts -- an attenuation that does not arise
    in the deeply sequenced SmartSeq2 background of notebook 45."""
    A = X[rows_a].toarray().astype(np.float64)
    B = X[rows_b].toarray().astype(np.float64)
    if delta != 0.0:
        B[:, mod] = B[:, mod] * (2.0 ** delta)
    return make_pb_dense(A), make_pb_dense(B)


def make_pb_dense(counts):
    """Pseudobulk from dense counts array (cells x genes)."""
    v = counts.sum(axis=0)
    tot = v.sum()
    if tot > 0:
        v = v / tot * 1e4
    return np.log1p(v)


rows = []
t0 = time.time()
per_n = {}
for n in N_GRID:
    print(f"\n=== n = {n} cells/group ===", flush=True)
    # ---- fixed sampling slots: each slot is one donor-paired split-half cell
    # set, used for BOTH the null and the injected series.  Sharing slots
    # removes cell-type / donor composition differences between the null and
    # effect series (which a composition-sensitive metric would otherwise read
    # as signal) and pairs every replicate.
    slots = []
    elig_combos = [i for i, (ct, d, nc_) in enumerate(combos) if nc_ >= 2 * n]
    for s in range(N_NULL_REPS):
        rng = np.random.RandomState(20000 + 7 * n + s)
        # stratified scheduling: cycle the eligible (donor, cell type) groups so
        # that the calibration half, the held-out half and the effect series all
        # carry the same cell-type / donor composition
        slots.append(draw_pair(rng, n, combo_index=elig_combos[s % len(elig_combos)]))

    null_pbs, null_rows = [], []
    for s, (ra, rb, donor, ct) in enumerate(slots):
        pb_a, pb_b = pb_pair(ra, rb, 0.0, None)
        null_pbs.append((pb_a, pb_b))
        null_rows.append({"n": n, "series": "split_half", "rep": s, "delta": 0.0,
                          "donor": donor, "cell_type": ct, "module_seed": 42,
                          **base_metrics(pb_a, pb_b)})
    # ---- whitening fit on null only
    pb_all = np.vstack([np.asarray(v) for pair in null_pbs for v in pair])
    pb_mean = pb_all.mean(axis=0)
    U, S, Vt = np.linalg.svd(pb_all - pb_mean, full_matrices=False)
    V = Vt[:N_PC].T
    d_pc = np.vstack([(a - b) @ V for a, b in null_pbs])
    mu_pc = d_pc.mean(axis=0)
    S_pc = np.cov(d_pc, rowvar=False)
    S_pc = (S_pc + S_pc.T) / 2
    S_pc[np.diag_indices(N_PC)] += RIDGE * np.trace(S_pc)
    S_inv = np.linalg.inv(S_pc)
    d_gene = np.vstack([a - b for a, b in null_pbs])
    sig_g = d_gene.std(axis=0)
    sig_g[sig_g < 1e-12] = 1e-12

    def whiten_metrics(pb_a, pb_b):
        dp = (pb_a - pb_b) @ V - mu_pc
        m_pc = float(np.sqrt(dp @ S_inv @ dp))
        dg = (pb_a - pb_b) / sig_g
        m_diag = float(np.sqrt(np.mean(dg ** 2)))
        return {"mahal_pc": m_pc, "mahal_diag": m_diag}

    for r, (pb_a, pb_b) in enumerate(null_pbs):
        null_rows[r].update(whiten_metrics(pb_a, pb_b))
    rows += null_rows
    print(f"  null: {N_NULL_REPS} reps ({time.time() - t0:.0f}s)", flush=True)

    # ---- effect reps on the held-out half of the slots (paired with the
    # held-out nulls, disjoint from the calibration half)
    test_slots = range(N_NULL_REPS // 2, N_NULL_REPS)
    for delta in DELTA_GRID:
        for s in MODULE_SEEDS:
            for r in test_slots:
                ra, rb, donor, ct = slots[r]
                pb_a, pb_b = pb_pair(ra, rb, delta, module_pools[s][:MODULE_SIZE])
                m = base_metrics(pb_a, pb_b)
                m.update(whiten_metrics(pb_a, pb_b))
                rows.append({"n": n, "series": "effect", "rep": r,
                             "delta": delta, "donor": donor, "cell_type": ct,
                             "module_seed": s, **m})
        print(f"  effect delta={delta}: {3 * len(test_slots)} reps "
              f"({time.time() - t0:.0f}s)", flush=True)

    # ---- operating characteristic at this n
    raw_n = [r_ for r_ in rows if r_["n"] == n]
    df_n = pd.DataFrame(raw_n)
    cal = df_n[(df_n.series == "split_half") & (df_n.rep < N_NULL_REPS // 2)]
    test = df_n[(df_n.series == "split_half") & (df_n.rep >= N_NULL_REPS // 2)]
    tpr_rows = []
    for m in METRIC_COLS:
        thr = float(np.nanpercentile(cal[m], 100 * (1 - FPR_TARGET)))
        fpr = float((test[m] > thr).mean())
        eff = df_n[df_n.series == "effect"]
        entry = {"n": n, "metric": m, "threshold_q95_calib": thr,
                 "fpr_heldout_null": fpr}
        for delta in DELTA_GRID:
            e = eff[eff.delta == delta]
            tpr = float((e[m] > thr).mean())
            # rank AUC effect vs null (all nulls)
            nn = df_n[df_n.series == "split_half"]
            vals = np.r_[e[m].to_numpy(), nn[m].to_numpy()]
            rk = rankdata(vals)
            npos = len(e)
            auc = float((rk[:npos].sum() - npos * (npos + 1) / 2)
                        / (npos * len(nn)))
            entry[f"tpr_d{delta}"] = round(tpr, 3)
            entry[f"auc_d{delta}"] = round(auc, 3)
        tpr_rows.append(entry)
    per_n[n] = tpr_rows
    print(f"  TPR@FPR5%: " + "; ".join(
        f"{e['metric']}: d0.25={e['tpr_d0.25']} d0.5={e['tpr_d0.5']} "
        f"d1.0={e['tpr_d1.0']} (FPR={e['fpr_heldout_null']:.3f})"
        for e in tpr_rows), flush=True)

raw = pd.DataFrame(rows)
raw.to_csv(OUT / "nc80_mj_kang_modular_raw.csv", index=False)

tpr_df = pd.DataFrame([e for n in N_GRID for e in per_n[n]])
tpr_df.to_csv(OUT / "nc80_mj_kang_modular_tpr.csv", index=False)

metrics = {
    "design": {
        "background": "Kang GSE96583 10x PBMC, ctrl cells only",
        "donor_paired": True,
        "n_grid": N_GRID, "delta_grid_log2fc": DELTA_GRID,
        "module_size": MODULE_SIZE, "module_seeds": MODULE_SEEDS,
        "module_off_anchor": True,
        "n_null_reps": N_NULL_REPS,
        "n_effect_reps_per_delta": 3 * (N_NULL_REPS // 2),
        "paired_slots": True,
        "calibration": "first half of the null slots (thresholds); held-out "
                       "second half gives the FPR; effect reps reuse the "
                       "held-out slots with injection",
        "fpr_target": FPR_TARGET, "seed": SEED,
        "eligible_combos": [{ "cell_type": ct, "donor": d, "n_ctrl": int(nc_)}
                            for ct, d, nc_ in combos],
        "n_eligible_module_genes": int(len(eligible_mod)),
    },
}
with open(OUT / "nc80_mj_kang_modular_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("\nOutputs written:")
print(f"  {OUT / 'nc80_mj_kang_modular_raw.csv'}")
print(f"  {OUT / 'nc80_mj_kang_modular_tpr.csv'}")
print(f"  {OUT / 'nc80_mj_kang_modular_metrics.json'}")
