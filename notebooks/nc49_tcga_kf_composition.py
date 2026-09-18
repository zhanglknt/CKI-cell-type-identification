"""
nc49 k_f composition analysis (R2-P1-1)
========================================
(a) k_f composition correction: does the TT-vs-NN k_f comparison and the
    LUAD mutation-group k_f gradient survive adjustment for ESTIMATE-style
    stromal/immune admixture?
      - per-cancer pair-level OLS:  log k_f ~ is_TT + admix_mean + |dAdmix|
        (mirrors the 4-marker composition regression of Discussion L81,
        but with the ESTIMATE admixture score per endpoint; log k_n for
        reference)
      - per-tumour k_f ~ admix regression per cancer
      - LUAD k_f ~ group + admix_z ANCOVA (recomputed here for a
        self-contained CSV)
(b) LUAD KRAS TT top-200 panel semantics: recompute the per-pair identity
    panels for all KRAS-KRAS tumour pairs (verbatim mirror of
    85_tcga_linear_norm_v44.py: per-cancer gene filter mean>=0.5, log2
    representation, HK exclusion, top-200 |delta|), aggregate gene
    frequency, and test over-representation against the 50 MSigDB
    Hallmark gene sets (hypergeometric, BH-FDR).

Inputs (read-only):
  data/tcga/tcga_RSEM_gene_tpm.gz, data/tcga/probemap.tsv,
  data/tcga/hallmark_2020.gmt (MSigDB Hallmark via Enrichr, 2026-09-18),
  data/tcga/luad_egfr_kras_mutations.json,
  results/tcga_linear_norm_v44_all_pairs.csv,
  results/nc49_tcga_admix_scores.csv
  data/cki/... HK file via _paths (same as 85)

Outputs:
  results/nc49_tcga_kf_composition.csv
  _tmp_fa_review/_nc49_kf_composition_log.txt
"""
import gzip
import json
import sys
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal, norm, linregress, hypergeom
from statsmodels.stats.multitest import multipletests
import statsmodels.api as sm

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
sys.path.insert(0, str(ROOT))
from _paths import TCGA_FILE, PROBEMAP_FILE, HK_FILE  # noqa: E402

PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
HALLMARK = ROOT / "data" / "tcga" / "hallmark_2020.gmt"
OUT = ROOT / "results" / "nc49_tcga_kf_composition.csv"
LOG = ROOT / "_tmp_fa_review" / "_nc49_kf_composition_log.txt"

CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]
N_TOP_KF = 200
SEED = 42

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

results = []

# ======================================================================
# PART A: k_f composition correction
# ======================================================================
log("== PART A: k_f composition correction ==")
pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
adm = pd.read_csv(ADMIX).set_index("sample")["admix"]
pairs["adm_a"] = pairs.sample_a.map(adm)
pairs["adm_b"] = pairs.sample_b.map(adm)
pairs["adm_mean"] = (pairs.adm_a + pairs.adm_b) / 2.0
pairs["adm_d"] = (pairs.adm_a - pairs.adm_b).abs()

# A1. pair-level: log k_f ~ is_TT + admix_mean + |dAdmix|  (per cancer)
log("")
log("-- A1 pair-level OLS: log metric ~ is_TT + admix_mean + |dAdmix| --")
for c in CANCERS:
    sub = pairs[(pairs.cancer == c) & pairs.pair_type.isin(["TT", "NN"])].copy()
    sub = sub.dropna(subset=["adm_mean", "adm_d"])
    sub["is_tt"] = (sub.pair_type == "TT").astype(float)
    for metric in ["kf", "kn"]:
        y = np.log(sub[metric].clip(lower=1e-12))
        # unadjusted gap
        gap_unadj = y[sub.is_tt == 1].mean() - y[sub.is_tt == 0].mean()
        X = sm.add_constant(sub[["is_tt", "adm_mean", "adm_d"]].astype(float))
        fit = sm.OLS(y.values, X.values).fit()
        b_tt, se_tt, p_tt = fit.params[1], fit.bse[1], fit.pvalues[1]
        results.append({"section": "A1_pair_level", "cancer": c, "metric": metric,
                        "n": len(sub), "test": "OLS log ~ is_TT + admix",
                        "comparison": "TT vs NN",
                        "stat": round(float(b_tt), 4), "se": round(float(se_tt), 4),
                        "p": float(p_tt), "extra": f"unadj_loggap={gap_unadj:.4f}"})
        log(f"{c} {metric}: TT-vs-NN log gap unadj={gap_unadj:+.3f} -> "
            f"adj={b_tt:+.3f} (SE {se_tt:.3f}, P={p_tt:.3g})")

# A2. per-tumour k_f ~ admix per cancer (restate; self-contained)
log("")
log("-- A2 per-tumour k_f ~ admix --")
long_rows = []
for c in CANCERS:
    sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    long_rows.append(pd.concat([
        sub[["sample_a", "kf"]].rename(columns={"sample_a": "sample"}),
        sub[["sample_b", "kf"]].rename(columns={"sample_b": "sample"}),
    ], ignore_index=True).assign(cancer=c))
long = pd.concat(long_rows, ignore_index=True)
per_tumor = long.groupby(["cancer", "sample"]).kf.mean().reset_index()
per_tumor["admix"] = per_tumor["sample"].map(adm)
per_tumor = per_tumor.dropna(subset=["admix"])
for c in CANCERS:
    sub = per_tumor[per_tumor.cancer == c]
    res = linregress(sub["admix"], sub["kf"])
    results.append({"section": "A2_pertumor", "cancer": c, "metric": "kf",
                    "n": len(sub), "test": "linregress kf ~ admix",
                    "stat": round(res.rvalue, 4), "p": res.pvalue,
                    "extra": f"r2={100*res.rvalue**2:.2f}%"})
    log(f"{c}: per-tumour kf ~ admix r={res.rvalue:+.3f}, P={res.pvalue:.3g}")

# A3. LUAD k_f ~ group + admix_z (self-contained re-run)
log("")
log("-- A3 LUAD k_f ~ group + admix_z --")
mut = json.load(open(MUT))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])

def group_of(s):
    e, k = s in egfr, s in kras
    if e and k:
        return "DOUBLE"
    if e:
        return "EGFR"
    if k:
        return "KRAS"
    return "WT"

lu = per_tumor[per_tumor.cancer == "TCGA-LUAD"].copy()
lu["group"] = lu["sample"].map(group_of)
lu = lu[lu.group != "DOUBLE"]
lu["admix_z"] = (lu.admix - lu.admix.mean()) / lu.admix.std(ddof=1)
GROUPS = ["WT", "EGFR", "KRAS"]
X = pd.get_dummies(lu["group"], drop_first=False)[GROUPS].astype(float).drop(columns=["WT"])
X.insert(0, "admix_z", lu["admix_z"].values)
X.insert(0, "const", 1.0)
fit = sm.OLS(lu["kf"].values, X.values).fit()
col = {n: i for i, n in enumerate(X.columns)}
cm = np.zeros((3, len(fit.params)))
cm[0, col["EGFR"]] = 1.0
cm[1, col["KRAS"]] = 1.0
cm[2, col["KRAS"]] = 1.0
cm[2, col["EGFR"]] = -1.0
tt = fit.t_test(cm)
for k, nm in enumerate(["EGFR - WT", "KRAS - WT", "KRAS - EGFR"]):
    est, se, pv = float(tt.effect[k]), float(tt.sd[k]), float(tt.pvalue[k])
    results.append({"section": "A3_luad_ancova", "cancer": "TCGA-LUAD",
                    "metric": "kf", "n": len(lu),
                    "test": "OLS kf ~ group + admix_z", "comparison": nm,
                    "stat": round(est, 4), "se": round(se, 4), "p": pv})
    log(f"  {nm}: {est:+.4f} (SE {se:.4f}), P={pv:.3g}")

# ======================================================================
# PART B: KRAS TT top-200 panel Hallmark enrichment
# ======================================================================
log("")
log("== PART B: LUAD KRAS-KRAS top-200 panel Hallmark enrichment ==")

# load probemap + HK (verbatim style from 85)
pm = pd.read_csv(PROBEMAP_FILE, sep="\t")
ens_to_symbol = {}
for _, row in pm.iterrows():
    ens_id = str(row.iloc[0]).split(".")[0]
    symbol = str(row.iloc[1])
    if ens_id and symbol and symbol != "nan":
        ens_to_symbol[ens_id] = symbol
symbol_to_ens = {}
for eid, sym in ens_to_symbol.items():
    symbol_to_ens.setdefault(sym, []).append(eid)
hk_df = pd.read_csv(HK_FILE)
hk_raw = hk_df.iloc[:, 0].dropna().astype(str)
hk_human = set()
for row in hk_raw:
    parts_hk = row.split(";")
    if len(parts_hk) >= 2:
        hk_human.add(parts_hk[1].strip())
log(f"HK symbols: {len(hk_human)}")

# TSS->LUAD only
LUAD_TSS = {"05", "35", "38", "44", "49", "50", "55", "64", "67", "73", "75",
            "78", "86", "91", "93", "97", "J2", "L3", "L4", "M1", "MP", "MT",
            "N1", "N6", "O1", "S2", "TR", "TV", "TQ", "NJ", "KN", "LF"}
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")
sample_list, col_idx = [], []
for i, sid in enumerate(header[1:], 1):
    parts = sid.split("-")
    if len(parts) >= 4 and parts[1] in LUAD_TSS and parts[3][:2] in ("01", "11"):
        sample_list.append(sid)
        col_idx.append(i)
col_arr = np.array(col_idx, dtype=np.int32)
log(f"LUAD samples: {len(sample_list)}")

# pass 1: qualifying genes
gene_names = []
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        ok = False
        for ci in col_arr:
            if ci < len(parts):
                try:
                    if float(parts[ci]) > 0:
                        ok = True
                        break
                except ValueError:
                    pass
        if ok:
            gene_names.append(parts[0])
n_genes = len(gene_names)
log(f"qualifying genes: {n_genes}")

# pass 2: fill matrix
expr = np.zeros((len(sample_list), n_genes), dtype=np.float32)
gpos = {g: i for i, g in enumerate(gene_names)}
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        gi = gpos.get(parts[0])
        if gi is None:
            continue
        for si, ci in enumerate(col_arr):
            if ci < len(parts):
                try:
                    expr[si, gi] = float(parts[ci])
                except (ValueError, IndexError):
                    pass

# per-cancer gene filter (verbatim): mean raw value >= 0.5
gene_means = expr.mean(axis=0)
keep = gene_means >= 0.5
expr = expr[:, keep]
genes = [g for g, k in zip(gene_names, keep) if k]
expr_log = np.log2(np.maximum(expr, 0) + 1)
del expr
log(f"after mean>=0.5 filter: {len(genes)} genes")

gene_ens = [g.split(".")[0] for g in genes]
ens_to_idx = {ens: i for i, ens in enumerate(gene_ens)}
hk_local = []
for sym in hk_human:
    if sym in symbol_to_ens:
        for eid in symbol_to_ens[sym]:
            if eid in ens_to_idx:
                hk_local.append(ens_to_idx[eid])
hk_arr = np.array(sorted(set(hk_local)), dtype=int)
hk_mask = np.zeros(len(genes), dtype=bool)
hk_mask[hk_arr] = True
nonhk_idx = np.where(~hk_mask)[0]
log(f"HK genes mapped: {len(hk_arr)}; non-HK background: {len(nonhk_idx)}")

# KRAS tumours among expression samples (15-char match, exclude DOUBLE)
kras_samples = [s for s in sample_list
                if s.split("-")[3][:2] == "01" and group_of(s) == "KRAS"]
log(f"KRAS tumours in expression matrix: {len(kras_samples)}")
row_of = {s: i for i, s in enumerate(sample_list)}
kras_rows = [row_of[s] for s in kras_samples]

# all KRAS-KRAS pairs: top-200 panel per pair
n_pairs = len(kras_rows) * (len(kras_rows) - 1) // 2
log(f"KRAS-KRAS pairs: {n_pairs}")
freq = np.zeros(len(genes), dtype=np.int64)
cnt = 0
for a in range(len(kras_rows)):
    va = expr_log[kras_rows[a]]
    for b in range(a + 1, len(kras_rows)):
        diff = np.abs(va - expr_log[kras_rows[b]])
        diff[hk_mask] = -1.0
        top = np.argpartition(diff, -N_TOP_KF)[-N_TOP_KF:]
        freq[top] += 1
        cnt += 1
log(f"panels computed: {cnt}")

# core panel: genes in >=50% of panels (fallback: top-300 by frequency)
thr = 0.5 * cnt
core = np.where(freq >= thr)[0]
core_rule = f">=50% of panels (n_thr={int(thr)})"
if len(core) < 50:
    core = np.argsort(freq)[-300:]
    core_rule = "top-300 by frequency (50% rule gave <50 genes)"
core_symbols = sorted(set(ens_to_symbol.get(gene_ens[i], "") for i in core) - {""})
log(f"core panel: {len(core)} gene rows -> {len(core_symbols)} symbols ({core_rule})")
# top recurrent genes
top_idx = np.argsort(freq)[-15:][::-1]
log("top-15 recurrent panel genes: " + ", ".join(
    f"{ens_to_symbol.get(gene_ens[i], gene_ens[i])}({100*freq[i]/cnt:.0f}%)" for i in top_idx))
results.append({"section": "B_panel", "cancer": "TCGA-LUAD", "metric": "kf_panel",
                "n": cnt, "test": "KRAS-KRAS core panel",
                "stat": len(core_symbols), "extra": core_rule})

# Hallmark enrichment (hypergeometric, BH)
bg_symbols = set()
for i in nonhk_idx:
    s = ens_to_symbol.get(gene_ens[i])
    if s:
        bg_symbols.add(s)
M = len(bg_symbols)
N_hit_universe = len(set(core_symbols) & bg_symbols)
log(f"background symbols: {M}; core panel intersect background: {N_hit_universe}")

hall = {}
with open(HALLMARK, encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) > 2:
            hall[parts[0]] = set(g for g in parts[2:] if g)
log(f"Hallmark sets loaded: {len(hall)}")

rows = []
core_set = set(core_symbols) & bg_symbols
for name, genes_h in hall.items():
    gs = genes_h & bg_symbols
    K = len(gs)
    if K < 5:
        continue
    x = len(gs & core_set)
    p = hypergeom.sf(x - 1, M, K, N_hit_universe)
    rows.append({"set": name, "set_size_in_bg": K, "overlap": x,
                 "odds": (x / max(N_hit_universe - x, 1)) / max((K - x), 1) / max(1 / (M - N_hit_universe - (K - x)), 1e-12) if x else 0.0,
                 "p": p})
df_h = pd.DataFrame(rows)
df_h["q_bh"] = multipletests(df_h.p, method="fdr_bh")[1]
df_h = df_h.sort_values("p")
log("")
log("top-10 Hallmark over-representation (KRAS core panel):")
for _, r in df_h.head(10).iterrows():
    log(f"  {r['set']}: overlap {r['overlap']}/{r['set_size_in_bg']}, "
        f"P={r['p']:.2e}, q={r['q_bh']:.2e}")
for _, r in df_h.iterrows():
    results.append({"section": "B_hallmark", "cancer": "TCGA-LUAD",
                    "metric": "kf_panel", "n": N_hit_universe,
                    "test": "hypergeometric (BH)", "comparison": r["set"],
                    "stat": int(r["overlap"]), "p": r["p"],
                    "extra": f"q={r['q_bh']:.3g}, set_size={r['set_size_in_bg']}"})

df_out = pd.DataFrame(results)
OUT.write_text(df_out.to_csv(index=False), encoding="utf-8")
log("")
log("saved: " + str(OUT))
LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(lines), encoding="utf-8")
print("DONE")
