# -*- coding: utf-8 -*-
"""nc80 bio Q8 (bio major): does k_n detect the HCC housekeeping
de-regulation the LIHC motivation cites (Waxman & Wurmbach 2007)?

Waxman & Wurmbach 2007 (BMC Genomics 8:243, GSE6764, HCV-induced HCC
progression series, Affymetrix U133 Plus 2.0) publish no machine-readable
gene list; the explicitly named significantly de-regulated reference genes
are GAPDH, ACTB, RPS20 and TBP (all up-regulated, strongest in advanced
stages), and their recommended stable pair is RPL41 + SFRS4.

Two arms, both on the deposited TCGA LIHC arm (tumour 01 / adjacent
normal 11, UCSC Xena Toil log2(TPM+0.001) matrix):

(1) Replication arm. Per-gene tumour-vs-adjacent-normal shift for the six
    named W-W genes (Mann-Whitney on the matrix scale; median log2
    difference). W-W claim: GAPDH/ACTB/RPS20/TBP are UP-regulated in HCC.

(2) Anchor arm. TT / NN / TN k_n medians for LIHC under three anchor
    panels, using the frozen v44 convention verbatim (probability mapping
    p_i = (clip(log2(TPM+0.001), 0) + 1) / sum -- the published linear
    mapping; JS base 2):
      - HRT Atlas in-file panel          (reproduces the published arm)
      - WW-dereg: the four named W-W de-regulated reference genes
      - CANONICAL: the classical reference-gene panel (17 mapped genes,
        a superset of the W-W named set that qPCR normalisation practice
        uses -- none of which are HRT members, per bio m1)
    If the canonical / W-W anchors show a much stronger LIHC tumour
    elevation than the HRT anchor, the HCC prior is real in TCGA LIHC but
    invisible to the HRT-anchored k_n (the panel lacks those genes) --
    explaining "strongest prior evidence, weakest signal". If no anchor
    shows it, the HCC motivation is cohort-specific and is dropped.

Outputs: results/nc80_q8_waxman_lihc.csv / .txt
"""
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parent.parent
TCGA_FILE = ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz"
PROBEMAP = ROOT / "data" / "tcga" / "probemap.tsv"
HK_HRT = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
OUT_CSV = ROOT / "results" / "nc80_q8_waxman_lihc.csv"
OUT_TXT = ROOT / "results" / "nc80_q8_waxman_lihc.txt"
RNG = np.random.RandomState(42)

lines = []
def log(msg=""):
    print(msg, flush=True)
    lines.append(str(msg))

WW_DEREG = ["GAPDH", "ACTB", "RPS20", "TBP"]
WW_STABLE = ["RPL41", "SRSF4"]  # SFRS4 renamed SRSF4 (HGNC)
ALIAS = {"SFRS4": "SRSF4"}
CANONICAL = ["ACTB", "GAPDH", "B2M", "PPIA", "EEF1A1", "RPLP0", "HPRT1",
             "TBP", "SDHA", "GUSB", "YWHAZ", "ACTG1", "RPL13", "RPS18",
             "PGK1", "LDHA", "UBC"]

# ---- symbol -> ensembl (versioned) ----
pm = pd.read_csv(PROBEMAP, sep="\t", dtype=str)
sym_to_ens = {}
for ens, sym in zip(pm["id"], pm["gene"]):
    sym_to_ens.setdefault(sym, []).append(ens)
    a = ALIAS.get(sym)
    if a:
        sym_to_ens.setdefault(a, []).append(ens)
hrt_syms = set(pd.read_csv(HK_HRT, sep=";")["Human"].dropna().astype(str))

target_syms = sorted(set(WW_DEREG + WW_STABLE + CANONICAL))
target_ens = set()
for s in target_syms:
    target_ens.update(sym_to_ens.get(s, []))
hrt_ens = set()
for s in hrt_syms:
    hrt_ens.update(sym_to_ens.get(s, []))
keep_ens = target_ens | hrt_ens
log(f"target symbols={len(target_syms)} -> {len(target_ens)} rows; "
    f"HRT={len(hrt_syms)} symbols -> {len(hrt_ens)} rows")

# ---- LIHC sample columns (short TSS codes, verbatim v44 mapping) ----
LIHC_TSS = {"CC", "BC", "DD", "ED", "EP", "ES", "FV", "FY", "G3", "GJ",
            "HP", "HU", "K7", "KR", "LG", "NI", "O8", "PD", "QN", "RC",
            "RG", "T6", "UB", "WQ", "XR", "YA", "ZP", "ZS", "MI", "F5"}
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().rstrip("\n").split("\t")
tumor_cols, normal_cols = [], []
for k, sid in enumerate(header[1:], 1):
    parts = sid.split("-")
    if len(parts) < 4 or parts[0] != "TCGA" or parts[1] not in LIHC_TSS:
        continue
    sc = parts[3][:2]
    if sc == "01":
        tumor_cols.append((sid, k))
    elif sc == "11":
        normal_cols.append((sid, k))
log(f"LIHC: {len(tumor_cols)} tumour, {len(normal_cols)} adjacent-normal "
    f"samples")

# ---- single streaming pass: keep only wanted rows ----
col_idx = np.array([k for _, k in tumor_cols + normal_cols], dtype=int)
sample_list = [s for s, _ in tumor_cols + normal_cols]
n_t = len(tumor_cols)
rows = {}
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        ens = parts[0]
        if ens not in keep_ens:
            continue
        vals = np.array([float(parts[ci]) for ci in col_idx], dtype=np.float64)
        if ens not in rows or vals.mean() > rows[ens].mean():
            rows[ens] = vals
log(f"extracted {len(rows)} gene rows")

expr = np.vstack([rows[e] for e in sorted(rows)]).T   # samples x genes
row_ens = sorted(rows)
ens_to_row = {e: i for i, e in enumerate(row_ens)}


def anchor_rows(syms):
    idx = []
    for s in syms:
        for e in sym_to_ens.get(s, []):
            if e in ens_to_row:
                idx.append(ens_to_row[e])
    return np.array(sorted(set(idx)), dtype=int)


def kn_linear(a, b):
    """v44 convention: p = (clip(log2(TPM+0.001),0)+1)/sum, JS base 2."""
    x = np.maximum(a, 0) + 1.0
    y = np.maximum(b, 0) + 1.0
    p = x / x.sum()
    q = y / y.sum()
    m = 0.5 * (p + q)
    return float(0.5 * (np.sum(p * np.log2(p / m)) +
                        np.sum(q * np.log2(q / m))))


# ---- (1) replication arm ----
log("\n(1) W-W named genes, tumour vs adjacent normal (matrix scale "
    "log2(TPM+0.001)):")
rep_rows = []
for g in WW_DEREG + WW_STABLE:
    idx = anchor_rows([g])
    if len(idx) == 0:
        log(f"  {g}: not mapped - skipped")
        continue
    v = expr[:, idx[0]]
    t, n = v[:n_t], v[n_t:]
    u = mannwhitneyu(t, n, alternative="two-sided")
    med_diff = float(np.median(t) - np.median(n))
    # fold change on TPM scale
    fc = 2.0 ** med_diff
    rep_rows.append({"gene": g, "median_log2_TPM_tumor": float(np.median(t)),
                     "median_log2_TPM_normal": float(np.median(n)),
                     "median_log2_diff": med_diff, "fold_change_TPM": fc,
                     "MWU_P": float(u.pvalue),
                     "direction": "up" if med_diff > 0 else "down"})
    log(f"  {g}: median log2 diff {med_diff:+.3f} "
        f"(fold {fc:.2f}x), MWU P={u.pvalue:.2e}")

# ---- (2) anchor arm ----
log("\n(2) LIHC k_n by anchor panel (v44 frozen convention):")
anchor_sets = {"HRT": anchor_rows(sorted(hrt_syms)),
               "WW_dereg": anchor_rows(WW_DEREG),
               "CANONICAL": anchor_rows(CANONICAL)}
for name, idx in anchor_sets.items():
    log(f"  {name}: {len(idx)} anchor genes")

def kn_pairs(idx, mask_a, mask_b, max_pairs=2000):
    if len(idx) == 0:
        return np.array([])
    a = np.where(mask_a)[0]
    b = np.where(mask_b)[0]
    rng = np.random.RandomState(42)
    vals = []
    if mask_a is mask_b:
        if len(a) > 2:
            aa = rng.choice(a, size=min(len(a), 60), replace=False) \
                if len(a) > 60 else a
            for i in range(len(aa)):
                for j in range(i + 1, len(aa)):
                    vals.append(kn_linear(expr[aa[i], idx],
                                           expr[aa[j], idx]))
    else:
        bb = rng.choice(b, size=min(len(b), 60), replace=False) \
            if len(b) > 60 else b
        aa = rng.choice(a, size=min(len(a), 60), replace=False) \
            if len(a) > 60 else a
        for i in aa:
            for j in bb:
                vals.append(kn_linear(expr[i, idx], expr[j, idx]))
    return np.array(vals)

tumor_mask = np.zeros(expr.shape[0], bool)
tumor_mask[:n_t] = True
normal_mask = ~tumor_mask

anchor_rows_out = []
for name, idx in anchor_sets.items():
    tt = kn_pairs(idx, tumor_mask, tumor_mask)
    nn = kn_pairs(idx, normal_mask, normal_mask)
    tn = kn_pairs(idx, tumor_mask, normal_mask)
    mwu_tt_nn = mannwhitneyu(tt, nn, alternative="greater")
    anchor_rows_out.append({
        "anchor": name, "n_anchor_genes": int(len(idx)),
        "kn_median_TT": float(np.median(tt)),
        "kn_median_NN": float(np.median(nn)),
        "kn_median_TN": float(np.median(tn)),
        "ratio_TT_NN": float(np.median(tt) / np.median(nn)),
        "MWU_TT_gt_NN_P": float(mwu_tt_nn.pvalue)})
    log(f"  {name}: TT {np.median(tt):.5f} NN {np.median(nn):.5f} "
        f"TN {np.median(tn):.5f} | TT/NN {np.median(tt)/np.median(nn):.2f} "
        f"(MWU P={mwu_tt_nn.pvalue:.2e})")

rep = pd.DataFrame(rep_rows)
anc = pd.DataFrame(anchor_rows_out)
rep.to_csv(OUT_CSV.with_name("nc80_q8_waxman_replication.csv"), index=False)
anc.to_csv(OUT_CSV, index=False)
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
log(f"saved: {OUT_CSV}")
print("DONE")
