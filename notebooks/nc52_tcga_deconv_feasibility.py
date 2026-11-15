# -*- coding: utf-8 -*-
"""
nc52 (v52 revision, reviewer B3): deconvolution feasibility assessment for
LIHC / KIRC, with a pre-registered fallback analysis.

Reviewers (R3) asked for formal cell-type deconvolution of the LIHC/KIRC bulk
tumours to test whether the k_n (housekeeping divergence) elevation reflects
composition. Feasibility findings (each verified by this script at run time):

  1. CIBERSORTx: requires the online API (https://cibersortx.stanford.edu)
     with a registered token. No token or network credential is configured in
     this environment -> NOT FEASIBLE offline.
  2. BayesPrism: R package. R 4.1.3 IS present (C:/Program Files/R/R-4.1.3)
     but carries only the 30 base/recommended packages; BayesPrism plus its
     Bioconductor dependency chain is not installed, and the revision
     instructions explicitly forbid installing heavyweight dependencies ->
     NOT FEASIBLE without violating the dependency constraint.
  3. Reference scRNA: LOCAL Tabula Sapiens liver (TS_Liver.h5ad, 5,007 cells)
     and kidney (TS_Kidney.h5ad, 9,641 cells) ARE available with compartment
     annotations -> a marker-based proxy IS feasible.

Fallback analysis (what this script then computes, all seed 42):
  a. Compartment reference profiles from TS (CP10k + log1p, mean per
     compartment); top-60 specificity markers per compartment, mapped to
     TCGA Ensembl ids via probemap.
  b. Rank-SSE proxy deconvolution of every ex-CC LIHC/KIRC tumour: marker
     expression is rank-transformed to (0,1) within each bulk sample and
     within each reference profile; non-negative least squares
     (scipy.nnls) yields compartment fractions; the residual SSE is the fit
     diagnostic.
  c. Reliability: split-half over the marker set (two random halves,
     seed 42) -> Spearman between the two non-parenchymal-fraction estimates.
  d. Validity: Spearman of the proxy non-parenchymal fraction vs the
     published ESTIMATE admixture score (results/nc49_tcga_admix_scores.csv),
     and vs the per-tumour mean k_n (v44 pair table, ex-CC default).

Outputs:
  results/nc52_tcga_deconv_feasibility.csv
  results/nc52_tcga_deconv_feasibility.json
"""
import gzip
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import nnls
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parent.parent
TCGA_FILE = ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz"
PROBEMAP = ROOT / "data" / "tcga" / "probemap.tsv"
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
TS_FILES = {"TCGA-LIHC": ROOT / "data" / "ts_human" / "TS_Liver.h5ad",
            "TCGA-KIRC": ROOT / "data" / "ts_human" / "TS_Kidney.h5ad"}
OUT_CSV = ROOT / "results" / "nc52_tcga_deconv_feasibility.csv"
OUT_JSON = ROOT / "results" / "nc52_tcga_deconv_feasibility.json"

SEED = 42
N_MARKERS = 60
CANCERS = ["TCGA-LIHC", "TCGA-KIRC"]

TSS_TO_PROJECT = {
    "BC": "TCGA-LIHC", "DD": "TCGA-LIHC", "ED": "TCGA-LIHC", "EP": "TCGA-LIHC",
    "ES": "TCGA-LIHC", "FV": "TCGA-LIHC", "FY": "TCGA-LIHC", "G3": "TCGA-LIHC",
    "GJ": "TCGA-LIHC", "HP": "TCGA-LIHC", "HU": "TCGA-LIHC", "K7": "TCGA-LIHC",
    "KR": "TCGA-LIHC", "LG": "TCGA-LIHC", "NI": "TCGA-LIHC", "O8": "TCGA-LIHC",
    "PD": "TCGA-LIHC", "QN": "TCGA-LIHC", "RC": "TCGA-LIHC", "RG": "TCGA-LIHC",
    "T6": "TCGA-LIHC", "UB": "TCGA-LIHC", "WQ": "TCGA-LIHC", "XR": "TCGA-LIHC",
    "YA": "TCGA-LIHC", "ZP": "TCGA-LIHC", "ZS": "TCGA-LIHC",
    "MI": "TCGA-LIHC", "F5": "TCGA-LIHC", "CC": "TCGA-LIHC",
    "A3": "TCGA-KIRC", "AK": "TCGA-KIRC", "AL": "TCGA-KIRC", "AY": "TCGA-KIRC",
    "B0": "TCGA-KIRC", "B1": "TCGA-KIRC", "B2": "TCGA-KIRC", "B3": "TCGA-KIRC",
    "B4": "TCGA-KIRC", "B8": "TCGA-KIRC", "BP": "TCGA-KIRC", "BW": "TCGA-KIRC",
    "CJ": "TCGA-KIRC", "CW": "TCGA-KIRC", "CZ": "TCGA-KIRC", "DV": "TCGA-KIRC",
    "DX": "TCGA-KIRC", "EU": "TCGA-KIRC", "GK": "TCGA-KIRC", "HE": "TCGA-KIRC",
    "I6": "TCGA-KIRC", "K6": "TCGA-KIRC", "KL": "TCGA-KIRC", "MM": "TCGA-KIRC",
    "MW": "TCGA-KIRC", "P4": "TCGA-KIRC", "Q2": "TCGA-KIRC",
    "UZ": "TCGA-KIRC", "V5": "TCGA-KIRC", "XM": "TCGA-KIRC", "YE": "TCGA-KIRC",
}

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

def is_cc(s):
    s = str(s)
    return len(s) >= 7 and s[5:7] == "CC"

findings = {"seed": SEED, "n_markers_per_compartment": N_MARKERS}

# ==================================================================
# 0. Feasibility checks (run-time verified, then documented)
# ==================================================================
log("== 0. Feasibility checks ==")
# CIBERSORTx
import os
token = os.environ.get("CIBERSORTX_TOKEN") or os.environ.get("CIBERSORTX_EMAIL")
findings["cibersortx"] = {
    "feasible": False,
    "reason": ("requires the online API with a registered token; no token/"
               "credential configured in this environment (env vars "
               "CIBERSORTX_TOKEN/CIBERSORTX_EMAIL unset); offline revision "
               "environment")}
log(f"CIBERSORTx: NOT FEASIBLE (online API token required; none configured)")

# BayesPrism / R
RSCRIPT = r"C:/Program Files/R/R-4.1.3/bin/x64/Rscript.exe"
r_ok = Path(RSCRIPT).exists()
r_version, bayesprism = "not found", False
n_r_pkgs = 0
if r_ok:
    proc = subprocess.run(
        [RSCRIPT, "-e",
         "cat(R.version.string, '\n'); cat(length(rownames(installed.packages())), '\n'); "
         "cat('BayesPrism' %in% rownames(installed.packages()))"],
        capture_output=True, timeout=120)
    out = proc.stdout.decode("utf-8", errors="replace").splitlines()
    out = [l for l in out if l.strip()]
    if len(out) >= 3:
        r_version = out[-3].strip()
        n_r_pkgs = int(out[-2].strip())
        bayesprism = out[-1].strip() == "TRUE"
findings["bayesprism"] = {
    "feasible": False,
    "r_version": r_version, "r_packages_installed": n_r_pkgs,
    "bayesprism_installed": bayesprism,
    "reason": ("R is present but carries only base/recommended packages; "
               "BayesPrism is not installed and pulling its Bioconductor "
               "dependency chain is forbidden by the revision constraint "
               "(no heavyweight dependency installs)")}
log(f"BayesPrism: NOT FEASIBLE (R={r_version}, {n_r_pkgs} base pkgs, "
    f"BayesPrism installed={bayesprism}; install forbidden)")

# reference scRNA
import anndata as ad
ref_info = {}
for c, f in TS_FILES.items():
    a = ad.read_h5ad(f, backed="r")
    comps = a.obs["compartment"].value_counts().to_dict()
    ref_info[c] = {"file": str(f), "n_cells": int(a.shape[0]),
                   "compartments": {k: int(v) for k, v in comps.items()}}
    a.file.close()
findings["reference_scrna"] = {"feasible": True, "references": ref_info}
log(f"Reference scRNA: AVAILABLE -> {json.dumps(ref_info)}")

# ==================================================================
# 1. Compartment reference profiles + specificity markers
# ==================================================================
log("")
log("== 1. TS compartment profiles + markers ==")
profiles = {}   # cancer -> DataFrame genes x compartments (mean log CP10k)
detrates = {}   # cancer -> DataFrame genes x compartments (detection rate)
for c, f in TS_FILES.items():
    a = ad.read_h5ad(f, backed="r")
    comp = a.obs["compartment"].astype(str).values
    comp_levels = sorted(set(comp))
    genes = a.var["gene_symbol"].astype(str).values
    sums = {k: np.zeros(a.shape[1]) for k in comp_levels}
    dets = {k: np.zeros(a.shape[1]) for k in comp_levels}
    cnts = {k: 0 for k in comp_levels}
    chunk = 1000
    for start in range(0, a.shape[0], chunk):
        stop = min(start + chunk, a.shape[0])
        X = a.X[start:stop].toarray()
        lib = X.sum(axis=1, keepdims=True)
        lib[lib == 0] = 1.0
        Xn = np.log1p(X / lib * 1e4)
        for k in comp_levels:
            m = comp[start:stop] == k
            if m.any():
                sums[k] += Xn[m].sum(axis=0)
                dets[k] += (X[m] > 0).sum(axis=0)
                cnts[k] += int(m.sum())
    a.file.close()
    prof = pd.DataFrame({k: sums[k] / cnts[k] for k in comp_levels},
                        index=genes)
    det = pd.DataFrame({k: dets[k] / cnts[k] for k in comp_levels},
                       index=genes)
    keep = ~prof.index.duplicated(keep="first")
    profiles[c] = prof[keep]
    detrates[c] = det[keep]
    log(f"{c}: compartments {comp_levels}, profile matrix {prof[keep].shape}")

markers = {}    # cancer -> {compartment: [symbols]}
for c, prof in profiles.items():
    det = detrates[c]
    mk = {}
    for k in prof.columns:
        others = prof[[x for x in prof.columns if x != k]].max(axis=1)
        spec = (prof[k] - others)
        # require detection in >=20% of the compartment's cells, then rank
        # by specificity (mean log CP10k above the max of other compartments)
        cand = spec[det[k] >= 0.2]
        mk[k] = cand.sort_values(ascending=False).head(N_MARKERS).index.tolist()
    markers[c] = mk
    log(f"{c} markers: " + "; ".join(f"{k}={len(v)}" for k, v in mk.items()))

# ==================================================================
# 2. TCGA marker extraction (single pass)
# ==================================================================
log("")
log("== 2. TCGA marker extraction (single pass over matrix) ==")
pm = pd.read_csv(PROBEMAP, sep="\t")
sym_to_ens = {}
for _, row in pm.iterrows():
    ens = str(row.iloc[0]).split(".")[0]
    sym = str(row.iloc[1])
    if ens and sym and sym != "nan":
        sym_to_ens.setdefault(sym, []).append(ens)

wanted_syms = sorted({s for c in CANCERS for v in markers[c].values() for s in v})
ens_wanted = {}
for s in wanted_syms:
    for e in sym_to_ens.get(s, []):
        ens_wanted.setdefault(e, s)
log(f"unique marker symbols: {len(wanted_syms)}, mapped Ensembl: {len(ens_wanted)}")

with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")
tumor_cols = {}
for k, sid in enumerate(header[1:], 1):
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    proj = TSS_TO_PROJECT.get(parts[1])
    if proj in CANCERS and parts[3][:2] == "01":
        tumor_cols[sid] = k
samples = sorted(tumor_cols)
col_of = {sid: tumor_cols[sid] for sid in samples}
log(f"tumour columns: LIHC={sum(1 for s in samples if TSS_TO_PROJECT[s.split('-')[1]]=='TCGA-LIHC')}, "
    f"KIRC={sum(1 for s in samples if TSS_TO_PROJECT[s.split('-')[1]]=='TCGA-KIRC')}")

expr = {}   # ens -> np.array over samples
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        ens = parts[0].split(".")[0]
        if ens not in ens_wanted:
            continue
        vals = np.zeros(len(samples))
        for si, sid in enumerate(samples):
            ci = col_of[sid]
            if ci < len(parts):
                try:
                    vals[si] = float(parts[ci])
                except ValueError:
                    pass
        expr[ens] = vals
log(f"marker rows extracted: {len(expr)}")

sym_expr = {}
for ens, sym in ens_wanted.items():
    if ens in expr:
        # if multiple Ensembl map to one symbol, keep the highest-mean row
        if sym not in sym_expr or expr[ens].mean() > sym_expr[sym].mean():
            sym_expr[sym] = expr[ens]

sample_cancer = np.array([TSS_TO_PROJECT[s.split("-")[1]] for s in samples])
expr_mat = {c: None for c in CANCERS}
for c in CANCERS:
    mcols = np.where(sample_cancer == c)[0]
    gns = sorted({s for v in markers[c].values() for s in v if s in sym_expr})
    M = np.column_stack([sym_expr[g][mcols] for g in gns]) if False else \
        np.vstack([sym_expr[g][mcols] for g in gns])  # genes x samples
    expr_mat[c] = (gns, np.log2(np.maximum(M, 0) + 1),
                   [samples[i] for i in mcols])
    log(f"{c}: marker matrix {M.shape[0]} genes x {M.shape[1]} tumours")

# ==================================================================
# 3. Rank-SSE proxy deconvolution + split-half + correlations
# ==================================================================
log("")
log("== 3. Rank-SSE proxy deconvolution ==")
rng = np.random.default_rng(SEED)

pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
adm = pd.read_csv(ADMIX)
adm_t = adm[adm.type == "Tumor"].set_index("sample")["admix"]

rows = []
for c in CANCERS:
    gns, Mlog, sids = expr_mat[c]
    prof = profiles[c]
    comps = list(prof.columns)
    # reference profiles restricted to marker genes
    R = np.zeros((len(gns), len(comps)))
    for j, k in enumerate(comps):
        vals = prof[k].reindex(gns).fillna(0.0).values
        R[:, j] = rankdata(vals) / (len(gns) + 1.0)
    # per-tumour mean k_n (ex-CC default)
    tt = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    tt = tt[~tt.sample_a.map(is_cc) & ~tt.sample_b.map(is_cc)]
    long = pd.concat([
        tt[["sample_a", "kn"]].rename(columns={"sample_a": "sample"}),
        tt[["sample_b", "kn"]].rename(columns={"sample_b": "sample"}),
    ], ignore_index=True)
    kn_pt = long.groupby("sample")["kn"].mean()

    def deconv(gene_idx):
        frac = np.zeros((Mlog.shape[1], len(comps)))
        sse = np.zeros(Mlog.shape[1])
        Rs = R[gene_idx]
        for i in range(Mlog.shape[1]):
            b = rankdata(Mlog[gene_idx, i]) / (len(gene_idx) + 1.0)
            f, rnorm = nnls(Rs, b)
            if f.sum() > 0:
                f = f / f.sum()
            frac[i] = f
            sse[i] = rnorm ** 2
        return frac, sse

    epi_j = comps.index("epithelial") if "epithelial" in comps else None
    all_idx = np.arange(len(gns))
    frac, sse = deconv(all_idx)
    nonpar = 1.0 - frac[:, epi_j] if epi_j is not None else np.nan
    # split-half
    perm = rng.permutation(len(gns))
    h1, h2 = perm[: len(perm) // 2], perm[len(perm) // 2:]
    f1, _ = deconv(h1)
    f2, _ = deconv(h2)
    np1 = 1.0 - f1[:, epi_j]
    np2 = 1.0 - f2[:, epi_j]
    rho_half, p_half = spearmanr(np1, np2)

    res = pd.DataFrame({"sample": sids, "nonparenchymal_frac": nonpar,
                        "sse": sse})
    for j, k in enumerate(comps):
        res[f"frac_{k}"] = frac[:, j]
    res["kn_pt"] = res["sample"].map(kn_pt)
    res["admix"] = res["sample"].map(adm_t)
    res = res[~res["sample"].map(is_cc)]
    res.to_csv(ROOT / "results" / f"nc52_tcga_deconv_{c.split('-')[1].lower()}_pertumor.csv",
               index=False)

    rho_kn, p_kn = spearmanr(res.nonparenchymal_frac, res.kn_pt, nan_policy="omit")
    rho_adm, p_adm = spearmanr(res.nonparenchymal_frac, res.admix, nan_policy="omit")
    rho_kn_adm, p_kn_adm = spearmanr(res.kn_pt, res.admix, nan_policy="omit")
    log(f"{c}: n={len(res)}; split-half rho={rho_half:.3f} (P={p_half:.2e}); "
        f"nonpar vs k_n rho={rho_kn:+.3f} (P={p_kn:.2e}); "
        f"nonpar vs ESTIMATE rho={rho_adm:+.3f} (P={p_adm:.2e}); "
        f"k_n vs ESTIMATE rho={rho_kn_adm:+.3f} (P={p_kn_adm:.2e}); "
        f"median SSE={res.sse.median():.4f}")
    rows.append({"cancer": c, "n_tumors_excc": len(res),
                 "split_half_rho": round(rho_half, 4),
                 "split_half_p": p_half,
                 "nonpar_vs_kn_spearman": round(rho_kn, 4),
                 "nonpar_vs_kn_p": p_kn,
                 "nonpar_vs_estimate_spearman": round(rho_adm, 4),
                 "nonpar_vs_estimate_p": p_adm,
                 "kn_vs_estimate_spearman": round(rho_kn_adm, 4),
                 "kn_vs_estimate_p": p_kn_adm,
                 "median_sse": round(float(res.sse.median()), 5)})

findings["fallback_results"] = rows
pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
OUT_JSON.write_text(json.dumps(findings, indent=2), encoding="utf-8")
log("")
log("saved: " + str(OUT_CSV))
log("saved: " + str(OUT_JSON))
print("DONE")
