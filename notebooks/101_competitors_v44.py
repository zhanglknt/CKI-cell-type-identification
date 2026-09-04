# -*- coding: utf-8 -*-
"""
101_competitors_v44.py — Competitor benchmark for CKI (v44 revision).

Compares CKI against two competitor methods for detecting cell-type-specific
perturbation effects:

  1. MELD (Burkhardt et al. 2021, Nat Biotechnol): per-cell likelihood of the
     perturbed condition from a kNN-graph density estimate. Installed from
     PyPI (meld 1.0.2, minimal --no-deps install; see report).
  2. scDist-approx: R unavailable on this machine, so we implement the core
     idea of scDist (Mitsakos et al. 2023) in Python: in PC space, per cell
     type, per-PC OLS of PC score on condition with donor fixed effects;
     cell-type distance = sqrt(sum_j beta_j^2 * lambda_j), lambda_j = PC
     eigenvalue. Explicitly labelled "Python approximation of scDist".

Analyses:
  A. Kang et al. 2018 IFN-beta PBMC (GSE96583): per-cell-type effect sizes
     from all three methods; sign agreement and Spearman correlation with the
     existing CKI results (results/kang_ifnb_demo_*, produced by
     notebooks/79_kang_ifnb_demo.py; CKI values are READ, not recomputed).
  B. Simulation with known ground truth on the Kang ctrl background:
     one target cell type gets an ADDITIVE Poisson mean shift on G in
     {100, 500} genes (fold ladder 2/4/8; multiplicative injection was
     rejected because library inflation + CPM normalization artefactually
     moves the HK anchor); all other types are pure null. >= 20 replicates
     per scenario plus 20 pure-null replicates for FPR. Seed base 42.
  C. CKI power formalization on Kang: per condition n in
     {50, 100, 200, 500, 1000} downsampling, 20 replicates, detection =
     per-pair permutation test on omega (B=100, P<0.05), replicating
     script 79's rule; C1 donor-paired + C2 pooled designs.

Outputs (all NEW files, no overwrite of existing results):
  results/competitors_v44_kang_pertype.csv
  results/competitors_v44_kang_perdonor.csv
  results/competitors_v44_kang_agreement.json
  results/competitors_v44_simulation.csv
  results/competitors_v44_simulation_summary.json
  results/competitors_v44_power.csv
  results/competitors_v44_power_summary.json
  results/competitors_v44_runmeta.json
  results/competitors_v44_report.md

Run: python notebooks/101_competitors_v44.py
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
from scipy.stats import spearmanr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from cki.core import js_divergence  # noqa: E402

DATA = PROJECT_ROOT / "data" / "kang_ifnb"
OUT = PROJECT_ROOT / "results"

# section selector: python notebooks/101_competitors_v44.py A B C (default: all)
SECTIONS = set(sys.argv[1:]) or {"A", "B", "C"}

SEED = 42
N_REPS = 20
N_TOP_KF = 200          # same per-pair DE-hybrid scheme as script 79
N_PCS = 20
N_HVG = 3000
POWER_NS = [50, 100, 200, 500, 1000]
POWER_NULL_DRAWS = 200
SIM_CELLS_PER_TYPE = 200   # per replicate per type (100 per group)
SIM_FOLDS = [2.0, 4.0, 8.0]  # additive mean-shift ladder: +(fold-1) x baseline mean
SIM_GENE_SETS = [100, 500]

t_start = time.time()

# ======================================================================
# Data loading (mirrors notebooks/79_kang_ifnb_demo.py)
# ======================================================================
print("[101] loading gene ids ...", flush=True)
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

print("[101] loading count matrices ...", flush=True)
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
    DATA / "GSM2560249_barcodes.tsv.gz"
)
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

# HK genes (same convention as script 79)
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

# HVG selection (by variance of log1p-CPM on a sample, for PCA-based methods)
print("[101] selecting HVGs ...", flush=True)
lib = np.asarray(X.sum(axis=1)).ravel().astype(float)
lib[lib == 0] = 1.0
Xn_sample = X[::5].multiply(1e4 / lib[::5, None]).tocsr()
Xn_sample.data = np.log1p(Xn_sample.data)
mean_g = np.asarray(Xn_sample.mean(axis=0)).ravel()
sq_g = np.asarray(Xn_sample.multiply(Xn_sample).mean(axis=0)).ravel()
var_g = sq_g - mean_g ** 2
hvg_idx = np.argsort(-var_g)[:N_HVG]
hvg_idx = np.sort(hvg_idx)
print(f"  HVGs: {len(hvg_idx)}", flush=True)


# ======================================================================
# Shared helpers
# ======================================================================
def make_pb(mat, row_idx):
    """Pseudobulk: sum counts -> normalize 1e4 -> log1p (project convention)."""
    v = np.asarray(mat[row_idx].sum(axis=0)).ravel().astype(float)
    tot = v.sum()
    if tot > 0:
        v = v / tot * 1e4
    return np.log1p(v)


def cki_components(pb_a, pb_b, hk, non_hk):
    """Per-pair DE-hybrid components, identical scheme to script 79."""
    k_n = js_divergence(pb_a[hk], pb_b[hk])
    diff = np.abs(pb_a - pb_b)
    cand = non_hk[diff[non_hk] > 0]
    if len(cand) > N_TOP_KF:
        cand = cand[np.argsort(-diff[cand])[:N_TOP_KF]]
    k_f = js_divergence(pb_a[cand], pb_b[cand])
    return k_n, k_f, (k_f / k_n if k_n > 0 else np.inf)


def cki_omega(pb_a, pb_b, hk, non_hk):
    """Per-pair DE-hybrid omega, identical scheme to script 79."""
    return cki_components(pb_a, pb_b, hk, non_hk)[2]


def norm_hvg_dense(mat):
    """Library-size normalize (1e4) + log1p, subset to HVGs, dense array."""
    l = np.asarray(mat.sum(axis=1)).ravel().astype(float)
    l[l == 0] = 1.0
    m = mat.multiply(1e4 / l[:, None]).tocsr()
    m.data = np.log1p(m.data)
    return np.asarray(m[:, hvg_idx].todense())


def pca_fit_transform(mat_dense, n_pc=N_PCS):
    from sklearn.decomposition import PCA
    pca = PCA(n_components=n_pc, random_state=SEED)
    scores = pca.fit_transform(mat_dense)
    return scores, pca.explained_variance_


def scdist_distance(pc_scores, cond_binary, donor_arr, eigenvalues):
    """Python approximation of scDist cell-type distance.

    Per-PC OLS: pc_j ~ intercept + condition + donor dummies (fixed effects).
    Distance = sqrt(sum_j beta_cond,j^2 * lambda_j).
    """
    donors = sorted(set(donor_arr))
    cols = [np.ones(len(cond_binary)), cond_binary.astype(float)]
    for d in donors[1:]:
        cols.append((donor_arr == d).astype(float))
    D = np.column_stack(cols)
    betas = np.linalg.lstsq(D, pc_scores, rcond=None)[0][1, :]  # condition row
    return float(np.sqrt(np.sum(betas ** 2 * eigenvalues)))


def auc_binary(scores, label1_mask):
    """P(score(label=1) > score(label=0)) with tie correction (rank AUC)."""
    from scipy.stats import rankdata
    s = np.asarray(scores, dtype=float)
    m1 = np.asarray(label1_mask, dtype=bool)
    n1, n0 = int(m1.sum()), int((~m1).sum())
    if n1 == 0 or n0 == 0:
        return np.nan
    rk = rankdata(s)
    return float((rk[m1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def run_meld(mat_dense, cond_labels):
    """MELD per-cell stim likelihood. cond_labels: array of 'ctrl'/'stim'."""
    import scprep
    import graphtools
    import meld as meld_pkg
    X_sqrt = scprep.transform.sqrt(mat_dense - mat_dense.min())  # sqrt needs >= 0
    # random_state fixed: graphtools uses randomized SVD/PCA internally;
    # without it the MELD likelihoods drift at the 1e-4 level between runs,
    # which flips ranks of near-saturated within-type AUCs (N2 xval finding)
    G = graphtools.Graph(X_sqrt, n_pca=N_PCS, knn=10, random_state=SEED,
                         verbose=False)
    op = meld_pkg.MELD(verbose=False)
    dens = op.fit_transform(G, pd.Series(cond_labels))
    lik = np.asarray(meld_pkg.utils.normalize_densities(dens))
    cols = list(dens.columns)
    return lik[:, cols.index("stim")]


# ======================================================================
# A. Kang real-data comparison
# ======================================================================
# shared by sections A/B/C even when A is skipped
with open(OUT / "kang_ifnb_demo_summary.json") as f:
    cki_summary = json.load(f)
ctypes_used = sorted(cki_summary["cell_types"].keys())

if "A" in SECTIONS:
    print("[101][A] Kang comparison: MELD + scDist-approx ...", flush=True)
    tA = time.time()
    
    # CKI per-type effects: read from authoritative script-79 outputs
    with open(OUT / "kang_ifnb_demo_summary.json") as f:
        cki_summary = json.load(f)
    pairs = pd.read_csv(OUT / "kang_ifnb_demo_pairs.csv")
    cki_perdonor = pairs[pairs["comparison"] == "stim_vs_ctrl"][
        ["cell_type", "donor", "omega", "perm_P"]].copy()
    
    ctypes_used = sorted(cki_summary["cell_types"].keys())
    selA = np.isin(ctypes, ctypes_used)
    XA = norm_hvg_dense(X[selA])
    ctA = ctypes[selA]
    stimA = stims[selA]
    donorA = inds[selA]
    
    print("  running MELD on all cells ...", flush=True)
    meld_res = run_meld(XA, stimA)
    
    print("  PCA for scDist-approx ...", flush=True)
    pc_scores, eigenvalues = pca_fit_transform(XA)
    
    pertype_rows = []
    perdonor_rows = []
    for ct in ctypes_used:
        m = ctA == ct
        stim_m = stimA[m] == "stim"
        meld_eff = float(meld_res[m].mean() - 0.5)
        meld_auc = auc_binary(meld_res[m], stim_m)  # P(RES_stim > RES_ctrl) within type
        sd = scdist_distance(pc_scores[m], stim_m.astype(int),
                             donorA[m], eigenvalues)
        cki_cal = cki_summary["cell_types"][ct]["omega_cal_stim_ctrl"]
        pertype_rows.append({
            "cell_type": ct,
            "n_cells": int(m.sum()),
            "cki_omega_cal_stim_ctrl": cki_cal,
            "meld_mean_res_stim_minus_half": meld_eff,
            "meld_auc_within_type": meld_auc,
            "scdist_approx_distance": sd,
        })
        for d in sorted(set(donorA[m])):
            md = m & (donorA == d)
            stim_md = stimA[md] == "stim"
            if stim_md.sum() < 10 or (~stim_md).sum() < 10:
                continue
            row = cki_perdonor[(cki_perdonor.cell_type == ct) & (cki_perdonor.donor == d)]
            perdonor_rows.append({
                "cell_type": ct, "donor": d,
                "n_cells": int(md.sum()),
                "cki_omega": float(row.omega.iloc[0]) if len(row) else np.nan,
                "meld_mean_res_stim": float(meld_res[md].mean()),
                "meld_auc_within_donor": auc_binary(meld_res[md], stim_md),
            })
    
    df_type = pd.DataFrame(pertype_rows)
    df_donor = pd.DataFrame(perdonor_rows)
    df_type.to_csv(OUT / "competitors_v44_kang_pertype.csv", index=False)
    df_donor.to_csv(OUT / "competitors_v44_kang_perdonor.csv", index=False)
    
    # agreement metrics
    sign_cki = np.sign(df_type["cki_omega_cal_stim_ctrl"] - 1.0)
    sign_meld = np.sign(df_type["meld_auc_within_type"] - 0.5)
    agree_meld = float((sign_cki == sign_meld).mean())
    rho_meld, p_meld = spearmanr(df_type["cki_omega_cal_stim_ctrl"],
                                 df_type["meld_auc_within_type"])
    rho_sd, p_sd = spearmanr(df_type["cki_omega_cal_stim_ctrl"],
                             df_type["scdist_approx_distance"])
    rho_meld_sd, p_meld_sd = spearmanr(df_type["meld_auc_within_type"],
                                       df_type["scdist_approx_distance"])
    dd = df_donor.dropna()
    rho_pd, p_pd = spearmanr(dd["cki_omega"], dd["meld_auc_within_donor"])
    agreement = {
        "n_cell_types": int(len(df_type)),
        "direction_rule": ("CKI: omega_cal>1 (stim effect above split-half null); "
                           "MELD: within-type AUC = P(RES_stim > RES_ctrl) > 0.5"),
        "sign_agreement_cki_vs_meld": agree_meld,
        "spearman_pertype_cki_vs_meld_auc": {"rho": float(rho_meld), "p": float(p_meld)},
        "spearman_pertype_cki_vs_scdist_approx": {"rho": float(rho_sd), "p": float(p_sd)},
        "spearman_pertype_meld_vs_scdist_approx": {"rho": float(rho_meld_sd), "p": float(p_meld_sd)},
        "spearman_per_typedonor_cki_vs_meld_auc": {"rho": float(rho_pd), "p": float(p_pd),
                                                    "n_pairs": int(len(dd))},
    }
    with open(OUT / "competitors_v44_kang_agreement.json", "w") as f:
        json.dump(agreement, f, indent=2)
    print(f"  [A] done in {time.time()-tA:.0f}s; sign agree={agree_meld:.2f}, "
          f"rho(CKI,MELD-auc)={rho_meld:.3f}, rho(CKI,scDist)={rho_sd:.3f}, "
          f"rho per-donor(CKI,MELD-auc)={rho_pd:.3f}", flush=True)

# ======================================================================
# B. Simulation benchmark (Kang ctrl background)
# ======================================================================
if "B" in SECTIONS:
    print("[101][B] simulation benchmark ...", flush=True)
    tB = time.time()
    
    ctrl_pool = {ct: np.where((ctypes == ct) & (stims == "ctrl"))[0] for ct in ctypes_used}
    donor_of = inds  # global donor labels
    target_ct = "CD14+ Monocytes"
    
    # Eligible injection genes: non-HK genes with appreciable expression in the
    # target cell type (mean >= 1 CPM in target-ctrl pseudobulk). Random
    # low-expression genes would make the mean shift undetectable by ANY method.
    _pb_tgt = make_pb(X, ctrl_pool[target_ct])
    eligible_inj = np.array([g for g in non_hk_idx if _pb_tgt[g] >= np.log1p(1.0)])
    _mu_counts = np.asarray(X[ctrl_pool[target_ct]].mean(axis=0)).ravel()  # mean raw counts/cell
    print(f"  eligible injection genes (non-HK, >=1 CPM in target): {len(eligible_inj)}",
          flush=True)
    
    # indices needed for CKI on the HVG-independent full gene set: use global hk_idx/non_hk_idx
    sim_rows = []
    
    
    def sim_scores(reps_seed, inject_genes, fold):
        """One replicate. inject_genes: None (null) or gene index array."""
        rng = np.random.default_rng(reps_seed)
        gA, gB, ctA_lab, ctB_lab, dA_lab, dB_lab = [], [], [], [], [], []
        for ct in ctypes_used:
            pool = ctrl_pool[ct]
            take = min(SIM_CELLS_PER_TYPE, len(pool))
            pick = rng.choice(pool, size=take, replace=False)
            rng.shuffle(pick)
            h = take // 2
            gA.append(pick[:h])
            gB.append(pick[h:2 * h])
            ctA_lab += [ct] * h
            ctB_lab += [ct] * h
            dA_lab += list(donor_of[pick[:h]])
            dB_lab += list(donor_of[pick[h:2 * h]])
        gA = np.concatenate(gA)
        gB = np.concatenate(gB)
        # inject ADDITIVE mean shift into target type group B
        Xs = X[np.concatenate([gA, gB])].tocsr().copy()
        if inject_genes is not None:
            tgt = np.where(np.array(ctB_lab) == target_ct)[0]
            rowsB = len(gA) + tgt
            mu = (fold - 1.0) * _mu_counts[inject_genes]  # per-gene added mean
            add = rng.poisson(np.broadcast_to(mu, (len(rowsB), len(mu))))
            Xs_lil = Xs.tolil()
            for i, r in enumerate(rowsB):
                Xs_lil[r, inject_genes] = np.asarray(
                    Xs[r, inject_genes].todense()).ravel() + add[i]
            Xs = Xs_lil.tocsr()
        nA = len(gA)
        cond = np.array(["ctrl"] * nA + ["stim"] * (Xs.shape[0] - nA))
        ct_all = np.array(ctA_lab + ctB_lab)
        donor_all = np.array(dA_lab + dB_lab)
    
        # CKI per-type omega
        out = {}
        for ct in ctypes_used:
            mA = np.where((ct_all == ct) & (cond == "ctrl"))[0]
            mB = np.where((ct_all == ct) & (cond == "stim"))[0]
            kn_, kf_, om_ = cki_components(make_pb(Xs, mA), make_pb(Xs, mB),
                                           hk_idx, non_hk_idx)
            out.setdefault("cki", {})[ct] = om_
            out.setdefault("cki_kn", {})[ct] = kn_
            out.setdefault("cki_kf", {})[ct] = kf_
        # MELD: score = within-type AUC P(RES_stim > RES_ctrl)
        mat = norm_hvg_dense(Xs)
        try:
            res = run_meld(mat, cond)
            for ct in ctypes_used:
                m = ct_all == ct
                out.setdefault("meld", {})[ct] = auc_binary(res[m], cond[m] == "stim")
        except Exception as e:  # noqa: BLE001
            print(f"    [warn] MELD failed in rep: {e}", flush=True)
            for ct in ctypes_used:
                out.setdefault("meld", {})[ct] = np.nan
        # scDist-approx
        pcs, ev = pca_fit_transform(mat)
        for ct in ctypes_used:
            m = ct_all == ct
            out.setdefault("scdist", {})[ct] = scdist_distance(
                pcs[m], (cond[m] == "stim").astype(int), donor_all[m], ev)
        return out
    
    
    # effect-size ladder: fold in SIM_FOLDS (added mean = (fold-1) x baseline)
    effect_grid = [(gs, fold) for gs in SIM_GENE_SETS for fold in SIM_FOLDS]
    for scenario, grid in [("null", [(None, None)]), ("effect", effect_grid)]:
        for gs, fold in grid:
            for rep in range(N_REPS):
                rep_seed = SEED + 1000 * (0 if gs is None else gs) + rep
                rng = np.random.default_rng(rep_seed)
                inj = None
                if gs is not None:
                    inj = np.sort(rng.choice(eligible_inj, size=gs, replace=False))
                sc = sim_scores(rep_seed, inj, fold)
                for ct in ctypes_used:
                    sim_rows.append({
                        "scenario": scenario, "n_genes_shifted": gs or 0,
                        "fold": fold or 0,
                        "rep": rep, "seed": rep_seed, "cell_type": ct,
                        "is_target": ct == target_ct,
                        "cki_omega": sc["cki"][ct],
                        "cki_k_n": sc["cki_kn"][ct],
                        "cki_k_f": sc["cki_kf"][ct],
                        "meld_auc_within_type": sc["meld"][ct],
                        "scdist_approx_dist": sc["scdist"][ct],
                    })
                print(f"  [B] scenario={scenario} G={gs} fold={fold} rep={rep} done "
                      f"({time.time()-tB:.0f}s)", flush=True)
    
    df_sim = pd.DataFrame(sim_rows)
    df_sim.to_csv(OUT / "competitors_v44_simulation.csv", index=False)
    
    # --- simulation summary: threshold from first half of null reps, FPR on second half
    methods = {"cki_omega": "CKI omega", "meld_auc_within_type": "MELD within-type AUC",
               "scdist_approx_dist": "scDist-approx distance",
               "cki_k_f": "CKI k_f component (diagnostic)",
               "cki_k_n": "CKI k_n anchor component (diagnostic, expected to INCREASE with shift)"}
    null_df = df_sim[df_sim.scenario == "null"]
    cal_null = null_df[null_df.rep < N_REPS // 2]
    test_null = null_df[null_df.rep >= N_REPS // 2]
    sim_summary = {"target_cell_type": target_ct, "sim_folds": SIM_FOLDS,
                   "cells_per_type": SIM_CELLS_PER_TYPE, "n_reps": N_REPS,
                   "seed_base": SEED, "methods": {}}
    for col, label in methods.items():
        thr = float(np.nanpercentile(cal_null[col], 95))
        # FPR: fraction of test-null (rep, type) scores above threshold
        fpr_type = float((test_null[col] > thr).mean())
        fpr_any = float(test_null.groupby("rep")[col].apply(lambda s: (s > thr).any()).mean())
        entry = {"label": label, "threshold_q95_from_null_calib": thr,
                 "fpr_per_type_heldout_null": fpr_type,
                 "fpr_any_type_per_rep_heldout_null": fpr_any}
        for gs, fold in effect_grid:
            eff = df_sim[(df_sim.scenario == "effect") & (df_sim.n_genes_shifted == gs)
                         & (df_sim.fold == fold)]
            tgt = eff[eff.is_target]
            sens = float((tgt[col] > thr).mean())
            # top-1 hit rate: target has the max score among all types in the rep
            wide = eff.pivot_table(index="rep", columns="cell_type", values=col)
            top1 = float((wide.idxmax(axis=1) == target_ct).mean())
            # AUC of target scores vs null-type scores (pooled across reps)
            from scipy.stats import rankdata
            pos = tgt[col].to_numpy()
            neg = eff[~eff.is_target][col].to_numpy()
            vals = np.concatenate([pos, neg])
            rk = rankdata(vals)[: len(pos)]
            auc = float((rk.sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))
            entry[f"G{gs}_F{fold}"] = {"sensitivity_at_null_q95": sens,
                                        "top1_hit_rate": top1, "auc_target_vs_nulltypes": auc}
        sim_summary["methods"][col] = entry
    
    with open(OUT / "competitors_v44_simulation_summary.json", "w") as f:
        json.dump(sim_summary, f, indent=2)
    print(f"  [B] done in {time.time()-tB:.0f}s", flush=True)

# ======================================================================
# C. CKI power formalization on Kang
#    Detection rule replicates script 79: per-pair permutation test on omega
#    (cell labels shuffled within the pair, B perms, one-sided P < 0.05).
#    Two designs:
#      C1 donor-paired: n ctrl + n stim cells within each usable donor.
#      C2 pooled: n ctrl vs n stim pooled across donors (allows large n).
#    Fast omega: dense float32 submatrix + BLAS gemv pseudobulk sums.
# ======================================================================
if "C" in SECTIONS:
    print("[101][C] CKI power curves (permutation-based) ...", flush=True)
    tC = time.time()
    B_PERM_POWER = 100
    
    
    def dense_counts(row_idx):
        return np.asarray(X[row_idx].todense(), dtype=np.float32)
    
    
    def omega_from_dense(sub):
        """sub: (2n, G) dense counts, first half = group A. Returns omega."""
        n2 = sub.shape[0]
        w = np.zeros(n2, dtype=np.float32)
        w[: n2 // 2] = 1.0
        return _omega_w(sub, w)
    
    
    def _omega_w(sub, w):
        pa = w @ sub
        pb = (1.0 - w) @ sub
        ta, tb = pa.sum(), pb.sum()
        if ta > 0:
            pa = pa / ta * 1e4
        if tb > 0:
            pb = pb / tb * 1e4
        pa = np.log1p(pa)
        pb = np.log1p(pb)
        return cki_omega(pa, pb, hk_idx, non_hk_idx)
    
    
    def perm_test(sub, obs, rng, B=B_PERM_POWER):
        """One-sided permutation P for omega on dense (2n, G) matrix."""
        n2 = sub.shape[0]
        cnt = 0
        for _ in range(B):
            w = np.zeros(n2, dtype=np.float32)
            w[rng.choice(n2, n2 // 2, replace=False)] = 1.0
            if _omega_w(sub, w) >= obs:
                cnt += 1
        return (cnt + 1) / (B + 1)
    
    
    power_rows = []
    power_summary = {
        "detection_rule": ("per-pair permutation test on CKI omega (labels shuffled, "
                           f"B={B_PERM_POWER}, one-sided P<0.05), replicating script 79"),
        "designs": {"C1_donor_paired": "n ctrl + n stim within each usable donor",
                    "C2_pooled": "n ctrl vs n stim pooled across donors"},
        "n_reps": N_REPS, "seed_base": SEED, "B_perm": B_PERM_POWER,
        "C1_donor_paired": {}, "C2_pooled": {}}
    
    for ct in ctypes_used:
        # ---- C1: donor-paired
        power_summary["C1_donor_paired"][ct] = {}
        for n in POWER_NS:
            donors_ok = [d for d in sorted(set(inds[ctypes == ct]))
                         if ((ctypes == ct) & (inds == d) & (stims == "ctrl")).sum() >= n
                         and ((ctypes == ct) & (inds == d) & (stims == "stim")).sum() >= n]
            if len(donors_ok) < 2:
                power_summary["C1_donor_paired"][ct][str(n)] = {
                    "note": f"skipped: {len(donors_ok)} donors with >= {n} cells/condition"}
                continue
            det, tot = 0, 0
            for rep in range(N_REPS):
                rng = np.random.default_rng(SEED + 7000 * n + rep)
                for d in donors_ok:
                    pc_ = np.where((ctypes == ct) & (inds == d) & (stims == "ctrl"))[0]
                    ps_ = np.where((ctypes == ct) & (inds == d) & (stims == "stim"))[0]
                    rows_ = np.concatenate([rng.choice(pc_, n, replace=False),
                                            rng.choice(ps_, n, replace=False)])
                    sub = dense_counts(rows_)
                    obs = omega_from_dense(sub)
                    p = perm_test(sub, obs, rng)
                    det += int(p < 0.05)
                    tot += 1
                    power_rows.append({"design": "C1_donor_paired", "cell_type": ct,
                                       "n_per_condition": n, "rep": rep, "donor": d,
                                       "omega": obs, "perm_P": p, "detected": p < 0.05})
            power = det / tot
            power_summary["C1_donor_paired"][ct][str(n)] = {
                "power": power, "n_donors": len(donors_ok), "n_pairs": tot}
            print(f"  [C1] {ct} n={n}: power={power:.2f} ({len(donors_ok)} donors)",
                  flush=True)
        # ---- C2: pooled
        power_summary["C2_pooled"][ct] = {}
        pool_c = np.where((ctypes == ct) & (stims == "ctrl"))[0]
        pool_s = np.where((ctypes == ct) & (stims == "stim"))[0]
        for n in POWER_NS:
            if len(pool_c) < n or len(pool_s) < n:
                power_summary["C2_pooled"][ct][str(n)] = {
                    "note": f"skipped: insufficient cells (ctrl={len(pool_c)}, stim={len(pool_s)})"}
                continue
            det = 0
            for rep in range(N_REPS):
                rng = np.random.default_rng(SEED + 9000 * n + rep)
                rows_ = np.concatenate([rng.choice(pool_c, n, replace=False),
                                        rng.choice(pool_s, n, replace=False)])
                sub = dense_counts(rows_)
                obs = omega_from_dense(sub)
                p = perm_test(sub, obs, rng)
                det += int(p < 0.05)
                power_rows.append({"design": "C2_pooled", "cell_type": ct,
                                   "n_per_condition": n, "rep": rep, "donor": "pooled",
                                   "omega": obs, "perm_P": p, "detected": p < 0.05})
            power = det / N_REPS
            power_summary["C2_pooled"][ct][str(n)] = {"power": power}
            print(f"  [C2] {ct} n={n}: power={power:.2f}", flush=True)
    
    pd.DataFrame(power_rows).to_csv(OUT / "competitors_v44_power.csv", index=False)
    with open(OUT / "competitors_v44_power_summary.json", "w") as f:
        json.dump(power_summary, f, indent=2)
    print(f"  [C] done in {time.time()-tC:.0f}s", flush=True)

# ======================================================================
# Run metadata
# ======================================================================
import meld as _meld_pkg
import scprep as _scprep
import graphtools as _gt
runmeta = {
    "script": "notebooks/101_competitors_v44.py",
    "seed_base": SEED, "n_reps": N_REPS,
    "meld_version": _meld_pkg.__version__,
    "scprep_version": _scprep.__version__,
    "graphtools_version": _gt.__version__,
    "numpy_version": np.__version__, "pandas_version": pd.__version__,
    "meld_install": ("pip install --no-deps meld==1.0.2 scprep graphtools tasklogger pygsp "
                     "+ decorator/networkx/future (scprep pins pandas<2.1 which has no "
                     "cp313 wheel; pandas 2.3.3 kept, runtime-compatible)"),
    "scdist": "R unavailable; core idea re-implemented in Python "
              "(PC-space fixed-effects condition regression, eigenvalue-weighted norm)",
    "elapsed_seconds_total": time.time() - t_start,
}
with open(OUT / "competitors_v44_runmeta.json", "w") as f:
    json.dump(runmeta, f, indent=2)
print(f"[101] all done in {runmeta['elapsed_seconds_total']:.0f}s", flush=True)
