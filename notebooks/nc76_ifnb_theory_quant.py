# -*- coding: utf-8 -*-
"""
nc76 (stat reviewer must-answer Q1): quantitative A1-failure anatomy on the
Kang IFN-beta dataset.

Per Note 20 definitions, for each cell type:
  E_b        = median k_n on donor-vs-donor (ctrl) pairs   (background HK rate)
  phi_HK     = median k_n on stim-vs-ctrl pairs - E_b      (A1 violation:
               functional-factor leakage onto the HK panel)
  alpha      = median k_f / median k_n on split-half pairs (E_f = 0 there)
  E_f+2C_bf  = median k_f (stim-ctrl) - alpha * median k_n (stim-ctrl)
  estimand   = alpha + (E_f + 2*C_bf) / E_b
  observed   = median omega (stim-ctrl) = k_f / (E_b + phi_HK)
  bias       = observed - estimand   (multiplicative deflation from A1 failure)
  bound      = 2 * sqrt(E_f / E_b)   (Cauchy-Schwarz cross-term bound; covers
               the NUMERATOR cross term C_bf only)

The check answers: does the omega bias under A1 failure fall inside the
2*sqrt(E_f/E_b) bound? (Expected: NO in the strongly anchor-affected types -
the bound covers C_bf, not denominator leakage; the operative guard is the
k_n rise itself, per the Identification paragraph.)

Data loading mirrors notebooks/79_kang_ifnb_demo.py verbatim.

Outputs:
  results/nc76_ifnb_theory_quant.csv
  results/nc76_ifnb_theory_quant.txt
"""
import gzip
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
N_TOP_KF = 200
N_SPLIT_HALF = 6
MIN_GROUP_CELLS = 50
SEED = 20260903

print("[nc76] loading gene ids ...", flush=True)
gene_ids = []
with gzip.open(DATA / "GSE96583_genes.txt.gz", "rt") as f:
    f.readline()
    for line in f:
        parts = line.strip().strip('"').split('"')
        gene_ids.append(parts[-1] if len(parts) >= 2 and parts[-1] else "")
n_declared = 35635
gene_ids = gene_ids + [""] * (n_declared - len(gene_ids))
gene_ids = np.array(gene_ids)

ensg2sym = {}
with open(DATA / "ensg2sym.tsv", encoding="utf-8") as f:
    f.readline()
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) == 2 and parts[0] and parts[1]:
            ensg2sym[parts[0]] = parts[1]

sym_of_row = np.array([ensg2sym.get(g, "") for g in gene_ids])
keep_rows, seen = [], set()
for i, s in enumerate(sym_of_row):
    if s and s not in seen:
        seen.add(s)
        keep_rows.append(i)
keep_rows = np.array(keep_rows)
gene_syms = sym_of_row[keep_rows]

print("[nc76] loading count matrices ...", flush=True)
X1 = mmread(DATA / "GSM2560248_2.1.mtx.gz").tocsr()
X2 = mmread(DATA / "GSM2560249_2.2.mtx.gz").tocsr()
X = sp.hstack([X1, X2]).tocsr().T
X = X[:, keep_rows].tocsr()
del X1, X2
n_cells, n_genes = X.shape

def read_barcodes(path):
    with gzip.open(path, "rt") as f:
        return [l.strip() for l in f]

barcodes = read_barcodes(DATA / "GSM2560248_barcodes.tsv.gz") + read_barcodes(
    DATA / "GSM2560249_barcodes.tsv.gz")

from collections import defaultdict  # noqa: E402
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
        raise KeyError(bc)
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
hk_idx = np.where(np.isin(sym_arr, list(hk_syms)))[0]
non_hk_idx = np.where(~np.isin(sym_arr, list(hk_syms)))[0]
print(f"  hk_syms={len(hk_syms)} hk_idx={len(hk_idx)} "
      f"example={list(hk_syms)[:3]}", flush=True)

def make_pb(row_idx):
    v = np.asarray(X[row_idx].sum(axis=0)).ravel().astype(float)
    tot = v.sum()
    if tot > 0:
        v = v / tot * 1e4
    return np.log1p(v)

def kf_kn(pb_a, pb_b):
    k_n = js_divergence(pb_a[hk_idx], pb_b[hk_idx])
    diff = np.abs(pb_a - pb_b)
    cand = non_hk_idx[diff[non_hk_idx] > 0]
    if len(cand) > N_TOP_KF:
        cand = cand[np.argsort(-diff[cand])[:N_TOP_KF]]
    k_f = js_divergence(pb_a[cand], pb_b[cand])
    return k_n, k_f

rng = np.random.default_rng(SEED)
rows = []
for ct in sorted(set(ctypes)):
    print(f"  processing [{ct}] ...", flush=True)
    sel = ctypes == ct
    groups = {}
    for d in sorted(set(inds[sel])):
        for cond in ("ctrl", "stim"):
            m = sel & (inds == d) & (stims == cond)
            if m.sum() >= MIN_GROUP_CELLS:
                groups[(d, cond)] = np.where(m)[0]
    donors = sorted({d for d, c in groups
                     if (d, "ctrl") in groups and (d, "stim") in groups})
    if len(donors) < 4:
        continue
    pbs = {g: make_pb(ix) for g, ix in groups.items()}

    # E_b: donor-vs-donor within ctrl
    kn_dd, kf_dd = [], []
    for i, d1 in enumerate(donors):
        for d2 in donors[i + 1:]:
            a, b = pbs[(d1, "ctrl")], pbs[(d2, "ctrl")]
            k_n, k_f = kf_kn(a, b)
            kn_dd.append(k_n); kf_dd.append(k_f)
    # stim-ctrl within donor
    kn_sc, kf_sc = [], []
    for d in donors:
        k_n, k_f = kf_kn(pbs[(d, "ctrl")], pbs[(d, "stim")])
        kn_sc.append(k_n); kf_sc.append(k_f)
    # split-half (E_f = 0)
    kn_sh, kf_sh = [], []
    for g, ix in groups.items():
        for _ in range(N_SPLIT_HALF):
            pm = rng.permutation(len(ix))
            h = len(ix) // 2
            if h < 10:
                continue
            k_n, k_f = kf_kn(make_pb(ix[pm[:h]]), make_pb(ix[pm[h:2 * h]]))
            kn_sh.append(k_n); kf_sh.append(k_f)

    E_b = float(np.median(kn_dd))
    if E_b <= 0:
        E_b = float(np.mean(kn_dd))
    kn_stim = float(np.median(kn_sc))
    kf_stim = float(np.median(kf_sc))
    phi_HK = kn_stim - E_b
    kn_sh_med = float(np.median(kn_sh))
    if kn_sh_med <= 0:
        kn_sh_med = float(np.mean(kn_sh))
    alpha = float(np.median(kf_sh) / kn_sh_med)
    Ef_2C = kf_stim - alpha * kn_stim
    Ef = max(Ef_2C, 1e-9)  # C_bf >= 0 branch estimate
    estimand = alpha + Ef_2C / E_b
    omega_obs = kf_stim / kn_stim
    bias = omega_obs - estimand
    bound = 2 * np.sqrt(Ef / E_b)
    defl = phi_HK / kn_stim  # multiplicative deflation fraction
    rows.append({
        "cell_type": ct, "n_donors": len(donors),
        "E_b_med_kn_donor": E_b, "kn_stim_ctrl": kn_stim,
        "phi_HK": phi_HK, "phi_over_Eb": phi_HK / E_b,
        "deflation_frac": defl, "alpha_splithalf": alpha,
        "kf_stim_ctrl": kf_stim, "Ef_plus_2Cbf": Ef_2C,
        "estimand": estimand, "omega_obs": omega_obs,
        "bias": bias, "bound_2sqrtEfEb": float(bound),
        "inside_bound": bool(abs(bias) <= bound),
    })
    print(f"  [{ct}] E_b={E_b:.5f} phi_HK/E_b={phi_HK/E_b:.2f} "
          f"defl={defl*100:.0f}% alpha={alpha:.2f} estimand={estimand:.2f} "
          f"omega={omega_obs:.2f} bias={bias:+.2f} bound={bound:.2f} "
          f"inside={abs(bias) <= bound}", flush=True)

import csv
out_csv = OUT / "nc76_ifnb_theory_quant.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

lines = ["nc76 IFN-beta A1-failure quantitative anatomy (stat Q1)", "=" * 64, ""]
for r in rows:
    lines.append(
        f"[{r['cell_type']}] E_b={r['E_b_med_kn_donor']:.5f} "
        f"k_n(stim)={r['kn_stim_ctrl']:.5f} phi/E_b={r['phi_over_Eb']:.2f} "
        f"deflation={r['deflation_frac']*100:.0f}% alpha={r['alpha_splithalf']:.2f} "
        f"estimand={r['estimand']:.2f} omega={r['omega_obs']:.2f} "
        f"bias={r['bias']:+.2f} bound 2sqrt(E_f/E_b)={r['bound_2sqrtEfEb']:.2f} "
        f"inside={r['inside_bound']}")
(OUT / "nc76_ifnb_theory_quant.txt").write_text("\n".join(lines) + "\n",
                                                encoding="utf-8")
print("DONE", flush=True)
