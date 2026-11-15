# -*- coding: utf-8 -*-
"""
nc78 P0-4 (#1221, scmethod-M1 extended): alternative housekeeping-anchor
sensitivity for the TCGA primary claims.

Claims under test (all recomputed under TWO independent HK definitions):
  (1) the pan-cancer NN/TT k_n reversal (tumour-tumour pairs show higher
      housekeeping divergence than normal-normal pairs);
  (2) the LUAD KRAS contrast (KRAS-mutant tumours separated by per-tumour
      omega from WT, EGFR in between / below).

Independent HK definitions:
  DEF-EL   Eisenberg & Levanon 2013 human housekeeping list (3,804 genes,
           data/housekeeping/eisenberg_levanon_2013_hk.txt; literature
           definition, independent of the HRT Atlas);
  DEF-CV   data-driven lowest-CV panel, size-matched to the in-cancer HRT
           panel (CV across samples among genes passing the pipeline filters;
           mirrors the brain alternative-anchor construction).

Pipeline is otherwise VERBATIM the authoritative linear-normalization
caliber (notebooks/85_tcga_linear_norm_v44.py): per-cancer gene filters
(expressed in any wanted sample; mean TPM >= 0.5), log2(TPM+1) for the
per-pair top-200 identity-gene ranking among non-anchor genes, linear
probability mapping (TPM+1)/sum for JS, kn_floor = 1e-4, and the SAME
seeded pair sets as results/tcga_linear_norm_v44_all_pairs.csv (the
authoritative pair table is read and re-scored, not resampled).

Outputs:
  results/nc78_alt_hk_tcga.csv / .txt
Seed: none needed (no resampling; pair sets taken from the authoritative
table). Runtime ~15 min (one gzip sweep of the 741 MB expression matrix).
"""
import gzip
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal

ROOT = Path(__file__).resolve().parent.parent
TCGA_FILE = ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz"
PROBEMAP = ROOT / "data" / "tcga" / "probemap.tsv"
HK_HRT = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
HK_EL = ROOT / "data" / "housekeeping" / "eisenberg_levanon_2013_hk.txt"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
OUT_CSV = ROOT / "results" / "nc78_alt_hk_tcga.csv"
OUT_TXT = ROOT / "results" / "nc78_alt_hk_tcga.txt"
N_TOP_KF = 200
KN_FLOOR = 1e-4
EPS = 1e-15

lines = []
def log(msg=""):
    print(msg, flush=True)
    lines.append(str(msg))

t0 = time.time()

pairs = pd.read_csv(PAIRS)
CANCERS = sorted(pairs.cancer.unique())
wanted = sorted(set(pairs.sample_a) | set(pairs.sample_b))
log(f"cancers: {CANCERS}; wanted samples: {len(wanted)}")

# ---- HK symbol sets ----
hrt = pd.read_csv(HK_HRT, sep=";")
hrt_syms = set(hrt.Human.dropna().astype(str))
el_syms = set(l.split("\t")[0].strip() for l in
              HK_EL.read_text().splitlines() if l.strip())
log(f"HRT symbols: {len(hrt_syms)}; EL symbols: {len(el_syms)}")

pm = pd.read_csv(PROBEMAP, sep="\t")
ens_to_symbol = {str(r[0]).split(".")[0]: str(r[1])
                 for r in pm.itertuples(index=False)}
symbol_to_ens = {}
for eid, sym in ens_to_symbol.items():
    symbol_to_ens.setdefault(sym, []).append(eid)

def sym_local(syms, gene_ens):
    s2i = {}
    for i, e in enumerate(gene_ens):
        s2i.setdefault(e, i)
    idx = set()
    for s in syms:
        for eid in symbol_to_ens.get(s, []):
            if eid in s2i:
                idx.add(s2i[eid])
    return np.array(sorted(idx), dtype=int)

# ---- single-pass load of the wanted columns ----
log("loading expression (single gzip sweep) ...")
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")[1:]
col_map = {}
for k, sid in enumerate(header, 1):
    if sid in set(wanted):
        col_map[sid] = k
missing = [s for s in wanted if s not in col_map]
assert not missing, f"{len(missing)} samples missing from matrix"

rows_log = {}
expr_blocks = {}
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()
    genes = []
    mat_cols = sorted(set(col_map.values()))
    col_arr = np.array(mat_cols, dtype=np.int32)
    sid_of_col = {col_map[s]: s for s in col_map}
    col_sids = [sid_of_col[c] for c in mat_cols]
    blocks = []
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        vals = np.array([float(parts[c]) if c < len(parts) else 0.0
                         for c in col_arr], dtype=np.float32)
        blocks.append(vals)
        genes.append(parts[0])
expr_g = np.vstack(blocks)  # (n_genes, n_samples)
del blocks
genes = np.array(genes)
log(f"matrix: {expr_g.shape[0]} genes x {expr_g.shape[1]} samples; "
    f"load {time.time()-t0:.0f}s")

row_of = {s: i for i, s in enumerate(col_sids)}

def js_lin(a, b):
    """JS (base-2) on linear probability vectors (TPM+1)/sum -- mirrors 85."""
    a = np.asarray(a, np.float64); b = np.asarray(b, np.float64)
    sa, sb = a.sum(), b.sum()
    if sa <= 0 and sb <= 0:
        return 0.0
    if sa <= 0 or sb <= 0:
        return 1.0
    p, q = a / sa, b / sb
    m = 0.5 * (p + q)
    with np.errstate(divide="ignore", invalid="ignore"):
        kl1 = np.where(p > 0, p * np.log2(np.where(p > 0, p, 1) / m), 0.0).sum()
        kl2 = np.where(q > 0, q * np.log2(np.where(q > 0, q, 1) / m), 0.0).sum()
    return float(0.5 * kl1 + 0.5 * kl2)

def pair_metrics(i, j, expr_log, expr_lin, hk):
    p1, p2 = expr_log[i], expr_log[j]
    diff = np.abs(p1 - p2)
    mask = np.ones(len(p1), bool)
    mask[hk] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-N_TOP_KF:]
    top = np.sort(top[diff[top] >= 0])
    kn = js_lin(expr_lin[i, hk], expr_lin[j, hk]) if len(hk) else 0.0
    kf = js_lin(expr_lin[i, top], expr_lin[j, top]) if len(top) else 0.0
    om = kf / KN_FLOOR if kn < KN_FLOOR else kf / kn
    return kn, kf, om

results = []

for ca in CANCERS:
    tc0 = time.time()
    sub = pairs[pairs.cancer == ca]
    sids = sorted(set(sub.sample_a) | set(sub.sample_b))
    cidx = np.array([row_of[s] for s in sids])
    E = expr_g[:, cidx].T  # (n_samples, n_genes)
    present = (E > 0).any(axis=0)
    E = E[:, present]
    g_pres = genes[present]
    means = E.mean(axis=0)
    keep = means >= 0.5
    E = E[:, keep]
    g_keep = g_pres[keep]
    gene_ens = np.array([g.split(".")[0] for g in g_keep])
    expr_log = np.log2(np.maximum(E, 0).astype(np.float64) + 1.0)
    expr_lin = np.maximum(E, 0).astype(np.float64) + 1.0
    local = {s: i for i, s in enumerate(sids)}

    hk_hrt = sym_local(hrt_syms, gene_ens)
    hk_el = sym_local(el_syms, gene_ens)
    # DEF-CV: lowest CV across samples, size-matched to the HRT panel
    mu = expr_lin.mean(axis=0)
    cv = np.full(E.shape[1], np.inf)
    ok = mu > 0
    cv[ok] = expr_lin[:, ok].std(axis=0) / mu[ok]
    hk_cv = np.sort(np.argsort(cv)[:len(hk_hrt)])
    log(f"{ca}: genes {E.shape[1]}; HK panels HRT {len(hk_hrt)} / "
        f"EL {len(hk_el)} / CV {len(hk_cv)}")

    pair_rows = []
    for _, r in sub.iterrows():
        i, j = local[r.sample_a], local[r.sample_b]
        pair_rows.append((r.pair_type, i, j))

    for defname, hk in [("EL", hk_el), ("CV", hk_cv)]:
        kn_arr = np.empty(len(pair_rows))
        om_arr = np.empty(len(pair_rows))
        pt_arr = np.empty(len(pair_rows), dtype=object)
        for k, (pt, i, j) in enumerate(pair_rows):
            kn, kf, om = pair_metrics(i, j, expr_log, expr_lin, hk)
            kn_arr[k] = kn
            om_arr[k] = om
            pt_arr[k] = pt
        nn = kn_arr[pt_arr == "NN"].mean()
        tt = kn_arr[pt_arr == "TT"].mean()
        ratio = nn / tt  # published convention: NN/TT < 1 = reversal
        n_nn = int((pt_arr == "NN").sum()); n_tt = int((pt_arr == "TT").sum())
        results.append({"cancer": ca, "definition": defname,
                        "n_hk_genes": int(len(hk)),
                        "mean_kn_NN": nn, "mean_kn_TT": tt,
                        "NN_over_TT_kn": ratio, "n_NN": n_nn, "n_TT": n_tt})
        log(f"  {ca} DEF-{defname}: NN/TT k_n = {ratio:.3f} "
            f"(NN {nn:.4f} / TT {tt:.4f}; n {n_nn}/{n_tt})")
        # store per-pair omega for the KRAS arm
        if ca == "TCGA-LUAD":
            out = pd.DataFrame({"sample_a": sub.sample_a.values,
                                "sample_b": sub.sample_b.values,
                                "pair_type": pt_arr.astype(str),
                                "kn_alt": kn_arr, "omega_alt": om_arr})
            out.to_csv(ROOT / "results"
                       / f"nc78_alt_hk_luad_{defname}_pairs.csv", index=False)

    # HRT reference ratio from the authoritative table (apples-to-apples)
    nn = sub[sub.pair_type == "NN"].kn.mean()
    tt = sub[sub.pair_type == "TT"].kn.mean()
    results.append({"cancer": ca, "definition": "HRT(ref)",
                    "n_hk_genes": int(len(hk_hrt)),
                    "mean_kn_NN": nn, "mean_kn_TT": tt,
                    "NN_over_TT_kn": nn / tt,
                    "n_NN": int((sub.pair_type == "NN").sum()),
                    "n_TT": int((sub.pair_type == "TT").sum())})
    log(f"  {ca} HRT(ref): NN/TT k_n = {nn/tt:.3f} [from authoritative table]")
    log(f"  {ca} done {time.time()-tc0:.0f}s")

# ---- KRAS arm: per-tumour omega under each definition ----
mut = json.load(open(MUT))
egfr = {s[:15] for s in mut["egfr_samples"]}
kras = {s[:15] for s in mut["kras_samples"]}
def group_of(s):
    e, k = s[:15] in egfr, s[:15] in kras
    if e and k:
        return "DOUBLE"
    return "EGFR" if e else ("KRAS" if k else "WT")

for defname in ("EL", "CV"):
    dfp = pd.read_csv(ROOT / "results" / f"nc78_alt_hk_luad_{defname}_pairs.csv")
    tt = dfp[dfp.pair_type == "TT"]
    long = pd.concat([
        tt[["sample_a", "omega_alt"]].rename(columns={"sample_a": "s"}),
        tt[["sample_b", "omega_alt"]].rename(columns={"sample_b": "s"}),
    ], ignore_index=True)
    per_t = long.groupby("s").omega_alt.mean().reset_index()
    per_t["group"] = per_t.s.map(group_of)
    per_t = per_t[per_t.group != "DOUBLE"]
    grp = [per_t[per_t.group == g].omega_alt.values
           for g in ("WT", "EGFR", "KRAS")]
    H, P = kruskal(*grp)
    med = {g: float(np.median(per_t[per_t.group == g].omega_alt))
           for g in ("WT", "EGFR", "KRAS")}
    results.append({"cancer": "TCGA-LUAD", "definition": defname,
                    "n_hk_genes": -1,
                    "mean_kn_NN": np.nan, "mean_kn_TT": np.nan,
                    "NN_over_TT_kn": np.nan,
                    "kras_kw_H": H, "kras_kw_P": P,
                    "median_omega_WT": med["WT"],
                    "median_omega_EGFR": med["EGFR"],
                    "median_omega_KRAS": med["KRAS"],
                    "n_WT": len(grp[0]), "n_EGFR": len(grp[1]),
                    "n_KRAS": len(grp[2])})
    log(f"KRAS DEF-{defname}: KW H={H:.2f} P={P:.4g}; medians "
        f"WT {med['WT']:.2f} / EGFR {med['EGFR']:.2f} / KRAS {med['KRAS']:.2f}")

res = pd.DataFrame(results)
res.to_csv(OUT_CSV, index=False)
log(f"saved: {OUT_CSV}")
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
log(f"total {time.time()-t0:.0f}s")
print("DONE")
