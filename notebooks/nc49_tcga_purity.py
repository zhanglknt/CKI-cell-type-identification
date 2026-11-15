"""
nc49 purity sensitivity analysis (R2-P0-1)
==========================================
ESTIMATE-style tumour purity correction for the pan-cancer divergence map.

Question (R2 blind review, P0-1): does the TT-vs-NN divergence elevation and
the LUAD mutation-group gradient survive adjustment for tumour purity /
stromal-immune admixture?

Method
------
1. Per-sample stromal (141) + immune (141) ssGSEA scores using the OFFICIAL
   ESTIMATE signature gene sets (SI_geneset.gmt from the estimate R package,
   r-forge/estimate @ GitHub, blob SHA d5dda04e64af0ecef20653fcb6171f721141dfb5).
   Scoring: rank-based empirical-CDF difference (the ESTIMATE algorithm of
   Yoshihara et al., Nat Commun 2013), computed over all expressed genes of
   the pooled 5-cancer sample set. Combined admixture score = stromal + immune
   (higher = more non-tumour admixture = lower purity). The published
   ESTIMATE purity is a monotone transform of this combined score, so
   regression adjustment on the combined score is invariant to the transform.
2. (a) Per-cancer per-tumour mean k_n / omega / k_f (TT pairs, v44 linear
   pair table) regressed on the admixture score: Pearson r, P, slope per SD.
3. (b) LUAD WT/EGFR/KRAS: admixture score across groups (KW + Dunn-Holm);
   metric ~ group + admixture ANCOVA (OLS); residual-based KW + Dunn-Holm.
4. (c) NN/TT ratio sensitivity restricted to the high-purity (low-admixture)
   half of tumours, sample-level cluster bootstrap CI (B=1000, seed 42).

Inputs (read-only):
  data/tcga/tcga_RSEM_gene_tpm.gz, data/tcga/probemap.tsv
  results/tcga_linear_norm_v44_all_pairs.csv
  data/tcga/luad_egfr_kras_mutations.json

Outputs:
  results/nc49_tcga_purity.csv
  _tmp_fa_review/_nc49_purity_log.txt
"""
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal, mannwhitneyu, norm, rankdata, linregress
import statsmodels.api as sm

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
TCGA_FILE = ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz"
PROBEMAP = ROOT / "data" / "tcga" / "probemap.tsv"
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
OUT = ROOT / "results" / "nc49_tcga_purity.csv"
LOG = ROOT / "_tmp_fa_review" / "_nc49_purity_log.txt"

B = 1000
SEED = 42
CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

# ---------------------------------------------------------------------------
# OFFICIAL ESTIMATE signatures (SI_geneset.gmt, estimate R package;
# source: github.com/r-forge/estimate, blob d5dda04e64af0ecef20653fcb6171f721141dfb5)
# ---------------------------------------------------------------------------
STROMAL_141 = """DCN PAPPA SFRP4 THBS2 LY86 CXCL14 FOXF1 COL10A1 ACTG2 APBB1IP
SH2D1A SULF1 MSR1 C3AR1 FAP PTGIS ITGBL1 BGN CXCL12 ECM2 FCGR2A MS4A4A WISP1
COL1A2 MS4A6A EDNRA VCAM1 GPR124 SCUBE2 AIF1 HEPH LUM PTGER3 RUNX1T1 CDH5
PIK3R5 RAMP3 LDB2 COX7A1 EDIL3 DDR2 FCGR2B LPPR4 COL15A1 AOC3 ITIH3 FMO1
PRKG1 PLXDC1 VSIG4 COL6A3 SGCD COL3A1 F13A1 OLFML1 IGSF6 COMP HGF GIMAP5
ABCA6 ITGAM MAF ITM2A CLEC7A ASPN LRRC15 ERG CD86 TRAT1 COL8A2 TCF21 CD93
CD163 GREM1 LMOD1 TLR2 ZEB2 C1QB KCNJ8 KDR CD33 RASGRP3 TNFSF4 CCR1 CSF1R
BTK MFAP5 MXRA5 ISLR ARHGAP28 ZFPM2 TLR7 ADAM12 OLFML2B ENPP2 CILP SIGLEC1
SPON2 PLXNC1 ADAMTS5 SAMSN1 CH25H COL14A1 EMCN RGS4 PCDH12 RARRES2 CD248
PDGFRB C1QA COL5A3 IGF1 SP140 TFEC TNN ATP8B4 ZNF423 FRZB SERPING1 ENPEP
CD14 DIO2 FPR1 IL18R1 HDC TXNDC3 PDE2A RSAD2 ITIH5 FASLG MMP3 NOX4 WNT2
LRRC32 CXCL9 ODZ4 FBLN2 EGFL6 IL1B SPON1 CD200""".split()

IMMUNE_141 = """LCP2 LSP1 FYB PLEK HCK IL10RA LILRB1 NCKAP1L LAIR1 NCF2 CYBB
PTPRC IL7R LAPTM5 CD53 EVI2B SLA ITGB2 GIMAP4 MYO1F HCLS1 MNDA IL2RG CD48
AOAH CCL5 LTB GMFG GIMAP6 GZMK LST1 GPR65 LILRB2 WIPF1 CD37 BIN2 FCER1G
IKZF1 TYROBP FGL2 FLI1 IRF8 ARHGAP15 SH2B3 TNFRSF1B DOCK2 CD2 ARHGEF6
CORO1A LY96 LYZ ITGAL TNFAIP3 RNASE6 TGFB1 PSTPIP1 CST7 RGS1 FGR SELL
MICAL1 TRAF3IP3 ITGA4 MAFB ARHGDIB IL4R RHOH HLA-DPA1 NKG7 NCF4 LPXN ITK
SELPLG HLA-DPB1 CD3D CD300A IL2RB ADCY7 PTGER4 SRGN CD247 CCR7 MSN ALOX5AP
PTGER2 RAC2 GBP2 VAV1 CLEC2B P2RY14 NFKBIA S100A9 IFI30 MFSD1 RASSF2 TPP1
RHOG CLEC4A GZMB PVRIG S100A8 CASP1 BCL2A1 HLA-E KLRB1 GNLY RAB27A IL18RAP
TPST2 EMP3 GMIP LCK IL32 PTPRCAP LGALS9 CCDC69 SAMHD1 TAP1 GBP1 CTSS GZMH
ADAM8 GLRX PRF1 CD69 HLA-B HLA-DMA CD74 KLRK1 PTPRE HLA-DRA VNN2 TCIRG1
RABGAP1L CSTA ZAP70 HLA-F HLA-G CD52 CD302 CD27""".split()

# a few signature symbols renamed since the 2013 release; try these aliases
# if the primary symbol is absent from the probeMap
ALIASES = {
    "WISP1": ["CCN4"], "ODZ4": ["TENM4"], "TXNDC3": ["NME8"],
    "LPPR4": ["PLPPR4"], "CLEC2B": ["KLRF1"], "RUNX1T1": ["CBFA2T1"],
    "GPR124": ["ADGRA2"],
}

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

log("== nc49 purity sensitivity (R2-P0-1) ==")
log(f"stromal sig: {len(STROMAL_141)} genes; immune sig: {len(IMMUNE_141)} genes")
assert len(STROMAL_141) == 141 and len(IMMUNE_141) == 141
assert len(set(STROMAL_141)) == 141 and len(set(IMMUNE_141)) == 141

# ---------------------------------------------------------------------------
# TSS -> project mapping (identical to 06_phase34_tcga.py)
# ---------------------------------------------------------------------------
TSS_TO_PROJECT = {
    "A1": "TCGA-BRCA", "A2": "TCGA-BRCA", "A7": "TCGA-BRCA", "A8": "TCGA-BRCA",
    "AN": "TCGA-BRCA", "AO": "TCGA-BRCA", "AQ": "TCGA-BRCA", "AR": "TCGA-BRCA",
    "B6": "TCGA-BRCA", "BH": "TCGA-BRCA", "C8": "TCGA-BRCA", "D8": "TCGA-BRCA",
    "E2": "TCGA-BRCA", "EW": "TCGA-BRCA", "GI": "TCGA-BRCA", "WT": "TCGA-BRCA",
    "XX": "TCGA-BRCA", "E9": "TCGA-BRCA", "GM": "TCGA-BRCA", "HN": "TCGA-BRCA",
    "JL": "TCGA-BRCA", "LD": "TCGA-BRCA", "LL": "TCGA-BRCA", "MS": "TCGA-BRCA",
    "OL": "TCGA-BRCA", "PE": "TCGA-BRCA", "PL": "TCGA-BRCA", "S3": "TCGA-BRCA",
    "UL": "TCGA-BRCA", "V7": "TCGA-BRCA", "W8": "TCGA-BRCA", "WV": "TCGA-BRCA",
    "05": "TCGA-LUAD", "35": "TCGA-LUAD", "38": "TCGA-LUAD", "44": "TCGA-LUAD",
    "49": "TCGA-LUAD", "50": "TCGA-LUAD", "55": "TCGA-LUAD", "64": "TCGA-LUAD",
    "67": "TCGA-LUAD", "73": "TCGA-LUAD", "75": "TCGA-LUAD", "78": "TCGA-LUAD",
    "86": "TCGA-LUAD", "91": "TCGA-LUAD", "93": "TCGA-LUAD", "97": "TCGA-LUAD",
    "J2": "TCGA-LUAD", "L3": "TCGA-LUAD", "L4": "TCGA-LUAD", "M1": "TCGA-LUAD",
    "MP": "TCGA-LUAD", "MT": "TCGA-LUAD", "N1": "TCGA-LUAD", "N6": "TCGA-LUAD",
    "O1": "TCGA-LUAD", "S2": "TCGA-LUAD", "TR": "TCGA-LUAD", "TV": "TCGA-LUAD",
    "TQ": "TCGA-LUAD", "NJ": "TCGA-LUAD", "KN": "TCGA-LUAD", "LF": "TCGA-LUAD",
    "18": "TCGA-LUSC", "21": "TCGA-LUSC", "22": "TCGA-LUSC", "33": "TCGA-LUSC",
    "34": "TCGA-LUSC", "37": "TCGA-LUSC", "39": "TCGA-LUSC", "43": "TCGA-LUSC",
    "51": "TCGA-LUSC", "52": "TCGA-LUSC", "56": "TCGA-LUSC", "60": "TCGA-LUSC",
    "63": "TCGA-LUSC", "66": "TCGA-LUSC", "68": "TCGA-LUSC", "70": "TCGA-LUSC",
    "77": "TCGA-LUSC", "85": "TCGA-LUSC", "90": "TCGA-LUSC", "92": "TCGA-LUSC",
    "94": "TCGA-LUSC", "96": "TCGA-LUSC", "98": "TCGA-LUSC", "CC": "TCGA-LIHC",
    "L5": "TCGA-LUSC", "N2": "TCGA-LUSC", "NK": "TCGA-LUSC", "Q1": "TCGA-LUSC",
    "IE": "TCGA-LUSC", "IF": "TCGA-LUSC", "IG": "TCGA-LUSC",
    "BC": "TCGA-LIHC", "DD": "TCGA-LIHC", "ED": "TCGA-LIHC", "EP": "TCGA-LIHC",
    "ES": "TCGA-LIHC", "FV": "TCGA-LIHC", "FY": "TCGA-LIHC", "G3": "TCGA-LIHC",
    "GJ": "TCGA-LIHC", "HP": "TCGA-LIHC", "HU": "TCGA-LIHC", "K7": "TCGA-LIHC",
    "KR": "TCGA-LIHC", "LG": "TCGA-LIHC", "NI": "TCGA-LIHC", "O8": "TCGA-LIHC",
    "PD": "TCGA-LIHC", "QN": "TCGA-LIHC", "RC": "TCGA-LIHC", "RG": "TCGA-LIHC",
    "T6": "TCGA-LIHC", "UB": "TCGA-LIHC", "WQ": "TCGA-LIHC", "XR": "TCGA-LIHC",
    "YA": "TCGA-LIHC", "ZP": "TCGA-LIHC", "ZS": "TCGA-LIHC", "MI": "TCGA-LIHC",
    "F5": "TCGA-LIHC",
    "A3": "TCGA-KIRC", "AK": "TCGA-KIRC", "AL": "TCGA-KIRC", "AY": "TCGA-KIRC",
    "B0": "TCGA-KIRC", "B1": "TCGA-KIRC", "B2": "TCGA-KIRC", "B3": "TCGA-KIRC",
    "B4": "TCGA-KIRC", "B8": "TCGA-KIRC", "BP": "TCGA-KIRC", "BW": "TCGA-KIRC",
    "CJ": "TCGA-KIRC", "CW": "TCGA-KIRC", "CZ": "TCGA-KIRC", "DV": "TCGA-KIRC",
    "DX": "TCGA-KIRC", "EU": "TCGA-KIRC", "GK": "TCGA-KIRC", "HE": "TCGA-KIRC",
    "I6": "TCGA-KIRC", "K6": "TCGA-KIRC", "KL": "TCGA-KIRC", "MM": "TCGA-KIRC",
    "MW": "TCGA-KIRC", "P4": "TCGA-KIRC", "Q2": "TCGA-KIRC", "UZ": "TCGA-KIRC",
    "V5": "TCGA-KIRC", "XM": "TCGA-KIRC", "YE": "TCGA-KIRC",
}

# ---------------------------------------------------------------------------
# 1. Load expression matrix for the 5 cancer types (tumour + normal)
# ---------------------------------------------------------------------------
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")
sample_ids, sample_meta = [], []
for sid in header[1:]:
    parts = sid.split("-")
    if len(parts) < 4:
        continue
    proj = TSS_TO_PROJECT.get(parts[1])
    code = parts[3][:2]
    if proj in CANCERS and code in ("01", "11"):
        sample_ids.append(sid)
        sample_meta.append({"sample": sid, "cancer": proj,
                            "type": "Tumor" if code == "01" else "Normal"})
col_index = {sid: i + 1 for i, sid in enumerate(header[1:])}
sample_col = np.array([col_index[s] for s in sample_ids], dtype=np.int32)
log(f"samples to load: {len(sample_ids)} (5 cancers, codes 01/11)")

# pass 1: qualifying genes (any value > 0 among wanted samples)
SENTINEL = -9.0  # Xena -9.9658 marks zero
qualifying = []
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        vals = [parts[ci] for ci in sample_col if ci < len(parts)]
        ok = False
        for v in vals:
            try:
                if float(v) > 0:
                    ok = True
                    break
            except ValueError:
                pass
        if ok:
            qualifying.append(parts[0])
N_genes = len(qualifying)
log(f"qualifying genes: {N_genes}")

# pass 2: fill matrix (samples x genes)
expr = np.zeros((len(sample_ids), N_genes), dtype=np.float32)
gpos = {g: i for i, g in enumerate(qualifying)}
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        gi = gpos.get(parts[0])
        if gi is None:
            continue
        for si, ci in enumerate(sample_col):
            if ci < len(parts):
                try:
                    v = float(parts[ci])
                except ValueError:
                    v = 0.0
                expr[si, gi] = 0.0 if v < SENTINEL / 2 else v
del gpos
log(f"expression matrix: {expr.shape}")

# ---------------------------------------------------------------------------
# 2. Map signature genes to matrix rows
# ---------------------------------------------------------------------------
pm = pd.read_csv(PROBEMAP, sep="\t")
ens_to_symbol = {}
for _, row in pm.iterrows():
    ens_to_symbol[str(row.iloc[0]).split(".")[0]] = str(row.iloc[1])
row_symbol = []
for g in qualifying:
    row_symbol.append(ens_to_symbol.get(g.split(".")[0], None))
sym_rows = {}
for i, s in enumerate(row_symbol):
    if s and s != "nan":
        sym_rows.setdefault(s, []).append(i)

def map_sig(genes, label):
    idx, unmapped = [], []
    for g in genes:
        cand = [g] + ALIASES.get(g, [])
        hit = None
        for c in cand:
            if c in sym_rows:
                hit = sym_rows[c][0]  # first probe if duplicated
                break
        if hit is None:
            unmapped.append(g)
        else:
            idx.append(hit)
    log(f"{label}: {len(idx)}/{len(genes)} mapped; unmapped: {unmapped}")
    return np.array(sorted(set(idx)), dtype=int)

stroma_idx = map_sig(STROMAL_141, "stromal")
immune_idx = map_sig(IMMUNE_141, "immune")
M_s, M_i = len(stroma_idx), len(immune_idx)
N = N_genes

# ---------------------------------------------------------------------------
# 3. ssGSEA ECDF-difference scores (chunked)
# ---------------------------------------------------------------------------
def ecdf_scores(chunk):
    """ESTIMATE-style score per sample (rank-based ECDF difference).

    Ranks computed on -expression (rank 1 = highest expression, average
    ties). score = S*(1/M + 1/(N-M)) - N(N+1)/(2(N-M)), where
    S = sum over signature genes of (N - r + 1). Positive = signature
    enriched among the most highly expressed genes.
    """
    ranks = rankdata(-chunk, axis=1)
    out = []
    for idx in (stroma_idx, immune_idx):
        M = len(idx)
        S = M * (N + 1) - ranks[:, idx].sum(axis=1)
        out.append(S * (1.0 / M + 1.0 / (N - M)) - N * (N + 1) / (2.0 * (N - M)))
    return out

score_s = np.empty(len(sample_ids))
score_i = np.empty(len(sample_ids))
CH = 128
for st in range(0, len(sample_ids), CH):
    sl = slice(st, min(st + CH, len(sample_ids)))
    s, i = ecdf_scores(expr[sl])
    score_s[sl], score_i[sl] = s, i
del expr

df_ss = pd.DataFrame(sample_meta)
df_ss["stromal_score"] = score_s
df_ss["immune_score"] = score_i
df_ss["admix"] = score_s + score_i  # higher = more stromal+immune admixture
log("")
log("admix (stromal+immune) summary by cancer/type:")
log(df_ss.groupby(["cancer", "type"])["admix"].describe()[["count", "mean", "std"]].round(1).to_string())

# purity direction: higher admix = lower purity
df_tumor = df_ss[df_ss.type == "Tumor"].copy()
df_tumor["admix_z"] = df_tumor.groupby("cancer")["admix"].transform(
    lambda x: (x - x.mean()) / x.std(ddof=1))

# ---------------------------------------------------------------------------
# 4. Per-tumour metrics from the v44 pair table
# ---------------------------------------------------------------------------
pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
long_rows = []
for c in CANCERS:
    sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    if not len(sub):
        continue
    long_rows.append(pd.concat([
        sub[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
        sub[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
    ], ignore_index=True).assign(cancer=c))
long = pd.concat(long_rows, ignore_index=True)
per_tumor = long.groupby(["cancer", "sample"]).agg(
    n_pairs=("omega", "size"), omega=("omega", "mean"),
    kf=("kf", "mean"), kn=("kn", "mean")).reset_index()
per_tumor = per_tumor.merge(df_tumor[["sample", "admix", "admix_z"]], on="sample", how="inner")
log("")
log(f"per-tumour TT metrics matched with admix score: n={len(per_tumor)} "
    f"(by cancer: {per_tumor.groupby('cancer').size().to_dict()})")

results = []

# ---------------------------------------------------------------------------
# (a) per-cancer regression: metric ~ admixture
# ---------------------------------------------------------------------------
log("")
log("== (a) per-tumour metric ~ admixture (stromal+immune ssGSEA) ==")
for c in CANCERS:
    sub = per_tumor[per_tumor.cancer == c]
    for metric in ["kn", "omega", "kf"]:
        res = linregress(sub["admix_z"], sub[metric])
        results.append({
            "section": "A_regression", "cancer": c, "metric": metric,
            "n": len(sub), "pearson_r": round(res.rvalue, 4),
            "p": res.pvalue,
            "slope_per_SD_admix": round(res.slope, 6),
            "r2_pct": round(100 * res.rvalue ** 2, 2)})
        log(f"{c} {metric}: r={res.rvalue:+.3f}, P={res.pvalue:.3g}, "
            f"r2={100*res.rvalue**2:.1f}% (n={len(sub)})")

# ---------------------------------------------------------------------------
# (b) LUAD mutation groups: admixture + purity-adjusted tests
# ---------------------------------------------------------------------------
log("")
log("== (b) LUAD WT/EGFR/KRAS: admixture and adjusted comparisons ==")
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
GROUPS = ["WT", "EGFR", "KRAS"]
log(f"LUAD per-tumour: WT={sum(lu.group=='WT')}, EGFR={sum(lu.group=='EGFR')}, "
    f"KRAS={sum(lu.group=='KRAS')}")

# admixture across groups
H, p_kw = kruskal(*[lu.loc[lu.group == g, "admix"].values for g in GROUPS])
results.append({"section": "B_group_admix", "cancer": "TCGA-LUAD",
                "metric": "admix", "test": "Kruskal-Wallis",
                "n": len(lu), "stat": round(H, 3), "p": p_kw})
for g in GROUPS:
    s = lu.loc[lu.group == g, "admix"]
    results.append({"section": "B_group_admix", "cancer": "TCGA-LUAD",
                    "metric": "admix", "test": "group mean",
                    "n": len(s), "stat": round(s.mean(), 2), "p": np.nan})
log(f"admix KW: H={H:.2f}, P={p_kw:.3g}; "
    f"means WT={lu.loc[lu.group=='WT','admix'].mean():.1f} "
    f"EGFR={lu.loc[lu.group=='EGFR','admix'].mean():.1f} "
    f"KRAS={lu.loc[lu.group=='KRAS','admix'].mean():.1f}")

def dunn_holm(df, val_col, group_col="group"):
    groups = [df.loc[df[group_col] == g, val_col].values for g in GROUPS]
    H, p_kw = kruskal(*groups)
    ranks = df[val_col].rank().values
    df2 = df.assign(_r=ranks)
    Nn = len(df2)
    _, counts = np.unique(df[val_col].values, return_counts=True)
    tie_term = np.sum(counts ** 3 - counts) / (Nn ** 3 - Nn)
    sigma2_bar = (Nn * (Nn + 1) / 12.0) - tie_term / (Nn - 1)
    out = []
    for i, j in [(1, 2), (0, 2), (0, 1)]:  # EGFR-KRAS, WT-KRAS, WT-EGFR
        gi, gj = GROUPS[i], GROUPS[j]
        ri = df2.loc[df2[group_col] == gi, "_r"].mean()
        rj = df2.loc[df2[group_col] == gj, "_r"].mean()
        ni, nj = sum(df[group_col] == gi), sum(df[group_col] == gj)
        se = np.sqrt(sigma2_bar * (1.0 / ni + 1.0 / nj))
        z = (ri - rj) / se
        out.append({"pair": f"{gi} vs {gj}", "z": z,
                    "p_raw": 2 * (1 - norm.cdf(abs(z)))})
    ps = [o["p_raw"] for o in out]
    order = np.argsort(ps)
    m = len(ps)
    adj, running = {}, 0.0
    for rank, idx in enumerate(order):
        val = min(1.0, (m - rank) * ps[idx])
        running = max(running, val)
        adj[idx] = running
    for idx, o in enumerate(out):
        o["p_holm"] = adj[idx]
    return H, p_kw, out

# unadjusted reference (recomputed for direct comparability)
for metric in ["omega", "kf", "kn"]:
    H0, p0, d0 = dunn_holm(lu, metric)
    for d in d0:
        results.append({"section": "B_luad_unadjusted", "cancer": "TCGA-LUAD",
                        "metric": metric, "test": "Dunn-Holm (unadj)",
                        "n": len(lu), "comparison": d["pair"],
                        "stat": round(d["z"], 3), "p": d["p_holm"]})

# ANCOVA: metric ~ group + admix_z  (OLS, WT reference)
for metric in ["omega", "kf", "kn"]:
    X = pd.get_dummies(lu["group"], drop_first=False)[GROUPS].astype(float)
    X = X.drop(columns=["WT"])
    X.insert(0, "admix_z", lu["admix_z"].values)
    X.insert(0, "const", 1.0)
    fit = sm.OLS(lu[metric].values, X.values).fit()
    col = {n: i for i, n in enumerate(X.columns)}  # const, admix_z, EGFR, KRAS
    # contrasts: EGFR-WT, KRAS-WT, KRAS-EGFR
    cm = np.zeros((3, len(fit.params)))
    cm[0, col["EGFR"]] = 1.0
    cm[1, col["KRAS"]] = 1.0
    cm[2, col["KRAS"]] = 1.0
    cm[2, col["EGFR"]] = -1.0
    tt = fit.t_test(cm)
    names = ["EGFR - WT", "KRAS - WT", "KRAS - EGFR"]
    log(f"--- {metric} ~ group + admix_z (OLS) ---")
    log(f"  admix_z coefficient: {fit.params[col['admix_z']]:.4f} "
        f"(SE {fit.bse[col['admix_z']]:.4f}), P={fit.pvalues[col['admix_z']]:.3g}")
    results.append({"section": "C_luad_ancova", "cancer": "TCGA-LUAD",
                    "metric": metric, "test": "admix_z coefficient",
                    "n": len(lu), "stat": round(float(fit.params[col['admix_z']]), 4),
                    "p": float(fit.pvalues[col['admix_z']])})
    for k, nm in enumerate(names):
        est, se = tt.effect[k], tt.sd[k]
        pv = tt.pvalue[k]
        results.append({"section": "C_luad_ancova", "cancer": "TCGA-LUAD",
                        "metric": metric, "test": "OLS adj diff (group + admix)",
                        "n": len(lu), "comparison": nm,
                        "stat": round(float(est), 4),
                        "p": float(pv),
                        "se": round(float(se), 4)})
        log(f"  {nm}: {est:.4f} (SE {se:.4f}), P={pv:.3g}")
    # group F-test (group jointly, controlling admix)
    fit_reduced = sm.OLS(lu[metric].values, X[["const", "admix_z"]].values).fit()
    from scipy.stats import f as fdist
    F = ((fit_reduced.ssr - fit.ssr) / 2) / (fit.ssr / fit.df_resid)
    pF = fdist.sf(F, 2, fit.df_resid)
    results.append({"section": "C_luad_ancova", "cancer": "TCGA-LUAD",
                    "metric": metric, "test": "group F-test adj for admix",
                    "n": len(lu), "stat": round(float(F), 3), "p": float(pF)})
    log(f"  group F-test (adj admix): F={F:.2f}, P={pF:.3g}")

# residual-based rank tests (metric residualized on admix_z within LUAD)
for metric in ["omega", "kf", "kn"]:
    beta = np.polyfit(lu["admix_z"], lu[metric], 1)[0]
    lu[f"{metric}_resid"] = lu[metric] - beta * lu["admix_z"]
    Hr, pr, dr = dunn_holm(lu, f"{metric}_resid")
    results.append({"section": "C_luad_resid", "cancer": "TCGA-LUAD",
                    "metric": metric, "test": "KW on admix residuals",
                    "n": len(lu), "stat": round(Hr, 3), "p": pr})
    for d in dr:
        results.append({"section": "C_luad_resid", "cancer": "TCGA-LUAD",
                        "metric": metric, "test": "Dunn-Holm (admix-resid)",
                        "n": len(lu), "comparison": d["pair"],
                        "stat": round(d["z"], 3), "p": d["p_holm"]})
    log(f"{metric} admix-residual KW: H={Hr:.2f}, P={pr:.3g}; " +
        "; ".join(f"{d['pair']} P_holm={d['p_holm']:.3g}" for d in dr))

# ---------------------------------------------------------------------------
# (c) NN/TT ratio restricted to low-admixture (high-purity) tumour half
# ---------------------------------------------------------------------------
log("")
log("== (c) NN/TT restricted to low-admixture (high-purity) tumour half ==")
rng = np.random.default_rng(SEED)

def weighted_pair_mean(vals, ia, ib, w):
    ww = w[ia] * w[ib]
    return np.sum(vals * ww) / np.sum(ww)

def boot_ratio(df_tt, df_nn, B, rng):
    t_samples = sorted(set(df_tt.sample_a) | set(df_tt.sample_b))
    n_samples = sorted(set(df_nn.sample_a) | set(df_nn.sample_b))
    t_idx = {s: i for i, s in enumerate(t_samples)}
    n_idx = {s: i for i, s in enumerate(n_samples)}
    tt_ia = df_tt.sample_a.map(t_idx).values
    tt_ib = df_tt.sample_b.map(t_idx).values
    tt_w = df_tt.omega.values
    nn_ia = df_nn.sample_a.map(n_idx).values
    nn_ib = df_nn.sample_b.map(n_idx).values
    nn_w = df_nn.omega.values
    ratios = []
    for _ in range(B):
        wt = rng.multinomial(len(t_samples), np.full(len(t_samples), 1.0 / len(t_samples))).astype(float)
        wn = rng.multinomial(len(n_samples), np.full(len(n_samples), 1.0 / len(n_samples))).astype(float)
        ratios.append(weighted_pair_mean(nn_w, nn_ia, nn_ib, wn)
                      / weighted_pair_mean(tt_w, tt_ia, tt_ib, wt))
    return np.percentile(ratios, [2.5, 97.5])

adm_t = df_tumor[["sample", "admix"]]
for c in CANCERS:
    tt = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    nn = pairs[(pairs.cancer == c) & (pairs.pair_type == "NN")]
    if not len(tt):
        continue
    adm_c = adm_t[adm_t["sample"].isin(set(tt.sample_a) | set(tt.sample_b))]
    thr = adm_c["admix"].median()
    keep = set(adm_c.loc[adm_c["admix"] <= thr, "sample"])
    tt_hi = tt[tt.sample_a.isin(keep) & tt.sample_b.isin(keep)]
    if len(tt_hi) < 30:
        log(f"{c}: too few high-purity TT pairs ({len(tt_hi)}), skipped")
        continue
    ratio_full = nn.omega.mean() / tt.omega.mean()
    ratio_hi = nn.omega.mean() / tt_hi.omega.mean()
    ci_hi = boot_ratio(tt_hi, nn, B, rng)
    results.append({"section": "D_nntt_highpurity", "cancer": c, "metric": "omega",
                    "test": "NN/TT all tumours", "n": len(tt),
                    "stat": round(ratio_full, 3), "p": np.nan})
    results.append({"section": "D_nntt_highpurity", "cancer": c, "metric": "omega",
                    "test": "NN/TT low-admix half", "n": len(tt_hi),
                    "stat": round(ratio_hi, 3),
                    "p": f"CI95 [{ci_hi[0]:.3f},{ci_hi[1]:.3f}]"})
    log(f"{c}: NN/TT all={ratio_full:.3f}; low-admix half={ratio_hi:.3f} "
        f"[{ci_hi[0]:.3f},{ci_hi[1]:.3f}] (pairs {len(tt)} -> {len(tt_hi)})")

# ---------------------------------------------------------------------------
df_out = pd.DataFrame(results)
OUT.write_text(df_out.to_csv(index=False), encoding="utf-8")
# per-sample admixture scores (for downstream covariate reuse, e.g. smoking)
OUT_SCORES = ROOT / "results" / "nc49_tcga_admix_scores.csv"
df_ss[["sample", "cancer", "type", "stromal_score", "immune_score", "admix"]].to_csv(
    OUT_SCORES, index=False, encoding="utf-8")
log("")
log("saved: " + str(OUT) + ", " + str(OUT_SCORES))
LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(lines), encoding="utf-8")
print("DONE")
