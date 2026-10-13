# -*- coding: utf-8 -*-
"""
nc76 (cancer reviewer must-answer Q2c + Q5): KRAS AUC increment over standard
DE, and the 13 unmatched EGFR labels.

Q2c: per-tumor scores (mean pair omega / k_f, fixed-panel variants,
proliferation, and a leave-one-out standard-DE projection score) -> AUC for
KRAS-vs-WT and EGFR-vs-WT classification; bootstrap CI for delta-AUC of omega
over the DE score.

Q5: the EGFR mutation list (data/tcga/luad_egfr_kras_mutations.json, 75
samples) vs the expression-matrix tumor set: why 13 do not match, and whether
the exclusion introduces selection bias (compare TP53/KRAS co-mutation rates
and patient-level clinical availability between matched and unmatched).

Expression loading mirrors notebooks/nc75_tcga_kras_incremental.py.

Outputs:
  results/nc76_tcga_followup.csv / .txt
"""
import json
import sys
import time
import gzip
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TCGA_FILE = ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz"
PROBEMAP = ROOT / "data" / "tcga" / "probemap.tsv"
HK_FILE = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
TP53_CACHE = ROOT / "data" / "tcga" / "luad_tp53_cbioportal.json"
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
FIXED = ROOT / "results" / "nc75_tcga_kras_incremental.csv"
OUT_CSV = ROOT / "results" / "nc76_tcga_followup.csv"
OUT_TXT = ROOT / "results" / "nc76_tcga_followup.txt"
SEED = 42
B_BOOT = 2000

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

t0 = time.time()

# ---- tumor universe from authoritative pairs ----
pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
luad_tt = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")]
tumor_ids = sorted(set(luad_tt.sample_a) | set(luad_tt.sample_b))
tumor_set = set(tumor_ids)
log(f"LUAD TT tumors: {len(tumor_ids)}")

# ---- Q5: EGFR label matching audit ----
mut = json.load(open(MUT))
egfr_all = sorted({s[:15] for s in mut["egfr_samples"]})
kras_all = sorted({s[:15] for s in mut["kras_samples"]})
log(f"mutation lists: EGFR {len(egfr_all)}, KRAS {len(kras_all)}")

# full expression header for reason coding
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")[1:]
hdr15 = {s[:15] for s in header}
LUAD_TSS = {"05", "35", "38", "44", "49", "50", "55", "64", "67", "73",
            "75", "78", "86", "91", "93", "97", "J2", "L3", "L4", "M1",
            "MP", "MT", "N1", "N6", "O1", "S2", "TR", "TV", "TQ", "NJ",
            "KN", "LF"}
hdr_luad = {s[:15] for s in header if s.split("-")[1] in LUAD_TSS}

def reason(sid):
    if sid in tumor_set:
        return "matched"
    if sid not in hdr15:
        return "no_aliquot_in_expression_matrix"
    if sid not in hdr_luad:
        return "TSS_not_in_LUAD_set"
    code = sid.split("-")[3][:2]
    if code != "01":
        return f"sample_type_{code}_not_primary_tumor"
    return "filtered_out_by_pairs_pipeline"

egfr_stat = pd.DataFrame({"sample": egfr_all})
egfr_stat["status"] = egfr_stat["sample"].map(reason)
log("\nEGFR label matching audit:")
log(egfr_stat.status.value_counts().to_string())

# selection-bias check: TP53 co-mutation (patient level, cBioPortal cache)
tp53_mut = {s[:12] for s in json.load(open(TP53_CACHE))["tp53_mut_samples"]}
egfr_stat["patient"] = egfr_stat["sample"].str[:12]
egfr_stat["tp53"] = egfr_stat["patient"].isin(tp53_mut)
kras_set12 = {s[:12] for s in kras_all}
egfr_stat["kras_comut"] = egfr_stat["patient"].isin(kras_set12)
tab = egfr_stat.groupby("status").agg(
    n=("sample", "size"), tp53_rate=("tp53", "mean"),
    kras_comut_rate=("kras_comut", "mean"))
log("\n" + tab.to_string())
matched = egfr_stat[egfr_stat.status == "matched"]
unmatched = egfr_stat[egfr_stat.status != "matched"]

# ---- load expression (mirrors nc75) ----
log("\nloading LUAD expression ...")
luad_cols, luad_sids = [], []
for k, sid in enumerate(header, 0):
    parts = sid.split("-")
    if len(parts) < 4 or parts[1] not in LUAD_TSS:
        continue
    if parts[3][:2] in ("01", "11"):
        luad_cols.append(k + 1)  # +1 for gene col
        luad_sids.append(sid)
usecols = [0] + luad_cols
df = pd.read_csv(TCGA_FILE, sep="\t", usecols=usecols, compression="gzip")
df.columns = ["gene"] + luad_sids
vals = df[luad_sids].values.astype(np.float64)
present = (vals > 0).any(axis=1)
vals = vals[present]
genes = df.gene.values[present]
keep = vals.mean(axis=1) >= 0.5
vals = vals[keep]
genes = genes[keep]
del df
expr_log = np.log2(np.maximum(vals, 0) + 1)
del vals
log(f"  genes after filters: {len(genes)}; samples {len(luad_sids)}")

sid_row = {s: i for i, s in enumerate(luad_sids)}
tum_cols = np.array([sid_row[s] for s in tumor_ids if s in sid_row])
tum_ids = [s for s in tumor_ids if s in sid_row]

# groups (drop doubles, as nc75)
egfr = {s[:15] for s in mut["egfr_samples"]}
kras = {s[:15] for s in mut["kras_samples"]}
def group_of(s):
    e, k = s in egfr, s in kras
    if e and k:
        return "DOUBLE"
    return "EGFR" if e else ("KRAS" if k else "WT")
groups = np.array([group_of(s) for s in tum_ids])

# ---- per-tumor scores ----
# omega / kf / kn from authoritative pairs (long aggregation)
long = pd.concat([
    luad_tt[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "s"}),
    luad_tt[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "s"}),
], ignore_index=True)
per_t = long.groupby("s").agg(omega=("omega", "mean"), kf=("kf", "mean"),
                              kn=("kn", "mean")).reindex(tum_ids)

# proliferation
pm = pd.read_csv(PROBEMAP, sep="\t")
ens_to_symbol = {str(r[0]).split(".")[0]: str(r[1]) for r in pm.itertuples(index=False)}
gene_ens = np.array([g.split(".")[0] for g in genes])
ens_local = {e: i for i, e in enumerate(gene_ens)}
prolif_idx = [ens_local[e] for sym in ("MKI67", "TOP2A", "PCNA")
              for e, s2 in ens_to_symbol.items() if s2 == sym and e in ens_local][:3]
prolif = expr_log[prolif_idx][:, tum_cols].mean(axis=0)

# ---- LOO standard-DE projection score (KRAS vs WT direction) ----
def loo_de_score(mask_case, mask_wt):
    X = expr_log[:, tum_cols]  # (G, n_tum)
    n_case = mask_case.sum(); n_wt = mask_wt.sum()
    s_case = X[:, mask_case].sum(1); ss_case = (X[:, mask_case] ** 2).sum(1)
    s_wt = X[:, mask_wt].sum(1); ss_wt = (X[:, mask_wt] ** 2).sum(1)
    scores = np.zeros(X.shape[1])
    for i in range(X.shape[1]):
        x = X[:, i]
        if mask_case[i]:
            sc, ssc, nc = s_case - x, ss_case - x ** 2, n_case - 1
            sw, ssw, nw = s_wt, ss_wt, n_wt
        elif mask_wt[i]:
            sc, ssc, nc = s_case, ss_case, n_case
            sw, ssw, nw = s_wt - x, ssw - x ** 2, n_wt - 1
        else:
            sc, ssc, nc = s_case, ss_case, n_case
            sw, ssw, nw = s_wt, ss_wt, n_wt
        m1, m0 = sc / nc, sw / nw
        v1 = np.maximum(ssc / nc - m1 ** 2, 1e-9)
        v0 = np.maximum(ssw / nw - m0 ** 2, 1e-9)
        t = (m1 - m0) / np.sqrt(v1 / nc + v0 / nw)
        w = t / np.maximum(np.abs(t).sum(), 1e-12)
        scores[i] = float((w * (x - (s_case + s_wt) / (nc + nw))).sum())
    return scores

is_wt = groups == "WT"
is_kras = groups == "KRAS"
is_egfr = groups == "EGFR"
log("computing LOO DE projection scores (KRAS-vs-WT) ...")
de_kras = loo_de_score(is_kras, is_wt)
log("computing LOO DE projection scores (EGFR-vs-WT) ...")
de_egfr = loo_de_score(is_egfr, is_wt)

def auc_rank(score, pos, neg):
    from scipy.stats import rankdata
    v = np.concatenate([score[pos], score[neg]])
    r = rankdata(v)[:pos.sum()]
    return float((r.sum() - pos.sum() * (pos.sum() + 1) / 2)
                 / (pos.sum() * neg.sum()))

rng = np.random.default_rng(SEED)
def boot_dauc(s1, s2, pos, neg, B=B_BOOT):
    """bootstrap percentile CI for AUC(s1)-AUC(s2)"""
    diffs = np.empty(B)
    pi = np.where(pos)[0]; ni = np.where(neg)[0]
    for b in range(B):
        pb = rng.choice(pi, len(pi), replace=True)
        nb = rng.choice(ni, len(ni), replace=True)
        pmask = np.zeros(len(pos), bool); pmask[pb] = True
        # build masks aligned to score arrays via index trick:
        diffs[b] = (auc_rank_idx(s1, pb, nb) - auc_rank_idx(s2, pb, nb))
    return float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))

def auc_rank_idx(score, pb, nb):
    from scipy.stats import rankdata
    v = np.concatenate([score[pb], score[nb]])
    r = rankdata(v)[:len(pb)]
    return float((r.sum() - len(pb) * (len(pb) + 1) / 2) / (len(pb) * len(nb)))

score_map = {
    "omega": per_t.omega.values,
    "kf": per_t.kf.values,
    "proliferation": np.asarray(prolif),
    "DE_projection": None,  # per contrast
}
rows = []
for cname, pos_m, de_sc in [("KRAS_vs_WT", is_kras, de_kras),
                            ("EGFR_vs_WT", is_egfr, de_egfr)]:
    neg_m = is_wt
    score_map["DE_projection"] = de_sc
    aucs = {}
    for mname, sc in score_map.items():
        aucs[mname] = auc_rank(np.asarray(sc, float), pos_m, neg_m)
    d_lo, d_hi = boot_dauc(per_t.omega.values, de_sc, pos_m, neg_m)
    d_lo2, d_hi2 = boot_dauc(per_t.omega.values, np.asarray(prolif), pos_m, neg_m)
    log(f"\n[{cname}] AUC: omega={aucs['omega']:.3f} kf={aucs['kf']:.3f} "
        f"DE={aucs['DE_projection']:.3f} prolif={aucs['proliferation']:.3f}")
    log(f"  dAUC(omega-DE) = {aucs['omega']-aucs['DE_projection']:+.3f} "
        f"95% bootCI [{d_lo:+.3f}, {d_hi:+.3f}]")
    log(f"  dAUC(omega-prolif) = {aucs['omega']-aucs['proliferation']:+.3f} "
        f"95% bootCI [{d_lo2:+.3f}, {d_hi2:+.3f}]")
    for mname, a in aucs.items():
        rows.append({"item": f"AUC_{cname}", "metric": mname, "value": a})
    rows.append({"item": f"dAUC_{cname}_omega_minus_DE", "metric": "ci95",
                 "value": f"{aucs['omega']-aucs['DE_projection']:+.3f} [{d_lo:+.3f},{d_hi:+.3f}]"})
    rows.append({"item": f"dAUC_{cname}_omega_minus_prolif", "metric": "ci95",
                 "value": f"{aucs['omega']-aucs['proliferation']:+.3f} [{d_lo2:+.3f},{d_hi2:+.3f}]"})

# Q5 rows
for st, n in egfr_stat.status.value_counts().items():
    rows.append({"item": "EGFR_label_audit", "metric": st, "value": int(n)})
rows.append({"item": "EGFR_tp53_rate_matched", "metric": "rate",
             "value": float(matched.tp53.mean())})
rows.append({"item": "EGFR_tp53_rate_unmatched", "metric": "rate",
             "value": float(unmatched.tp53.mean())})
rows.append({"item": "EGFR_kras_comut_matched", "metric": "rate",
             "value": float(matched.kras_comut.mean())})
rows.append({"item": "EGFR_kras_comut_unmatched", "metric": "rate",
             "value": float(unmatched.kras_comut.mean())})

pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
log(f"\nsaved: {OUT_CSV}")
log(f"total {time.time()-t0:.0f}s")
OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
print("DONE")
