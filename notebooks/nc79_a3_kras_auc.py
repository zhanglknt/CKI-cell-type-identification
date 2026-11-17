# -*- coding: utf-8 -*-
"""
nc79 a3: statistical strength of the LUAD KRAS-vs-EGFR discrimination claim
(panel P0-4b) and the double-panel delta-omega sensitivity.

Analysis only. Reads existing authoritative artefacts, writes NEW files:
  results/nc79_a3_kras_scores.csv
  results/nc79_a3_kras_auc.csv
  results/nc79_a3_kras_compare.csv
  results/audit/_nc79_a3_ruling.md        (written by hand afterwards)

Score definitions (all aligned with the published pipeline):
  omega_main    : per-tumor MEAN of per-pair omega_floor over the 2,000
                  authoritative LUAD TT pairs containing the tumor
                  (exactly the nc76_tcga_followup.py / Fig. 3b convention).
  omega_lowestcv: same aggregation on results/nc78_alt_hk_luad_CV_pairs.csv
                  (data-driven lowest-CV panel, size-matched to the HRT panel).
  omega_EL      : same on results/nc78_alt_hk_luad_EL_pairs.csv
                  (Eisenberg-Levanon 2013 literature list; extra context).
  de_score      : leave-one-out standard-DE projection, per-gene Welch t on the
                  log2(TPM+1) representation, KRAS vs EGFR (mirrors nc76's
                  loo_de_score, which produced the published 0.736 for KRAS-WT).
  de_score_5cv  : 5-fold cross-validated Wilcoxon top-200 DE score (spec check).

Class: KRAS = positive, EGFR = negative, DOUBLE mutants dropped (n=2).
"""
import gzip
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parent.parent
TCGA_FILE = ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_TCGA-LUAD_pairs.csv"
CV_PAIRS = ROOT / "results" / "nc78_alt_hk_luad_CV_pairs.csv"
EL_PAIRS = ROOT / "results" / "nc78_alt_hk_luad_EL_pairs.csv"
OUT_SCORES = ROOT / "results" / "nc79_a3_kras_scores.csv"
OUT_AUC = ROOT / "results" / "nc79_a3_kras_auc.csv"
OUT_CMP = ROOT / "results" / "nc79_a3_kras_compare.csv"

SEED = 42
B_BOOT = 2000
LUAD_TSS = {"05", "35", "38", "44", "49", "50", "55", "64", "67", "73",
            "75", "78", "86", "91", "93", "97", "J2", "L3", "L4", "M1",
            "MP", "MT", "N1", "N6", "O1", "S2", "TR", "TV", "TQ", "NJ",
            "KN", "LF"}

lines = []
def log(msg=""):
    print(msg, flush=True)
    lines.append(str(msg))

t0 = time.time()

# --------------------------------------------------------------------------
# 1. per-tumor omega under the three panels
# --------------------------------------------------------------------------
pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
tt = pairs[pairs.pair_type == "TT"]
tumor_ids = sorted(set(tt.sample_a) | set(tt.sample_b))
log(f"authoritative LUAD TT pairs: {len(tt)}; tumors: {len(tumor_ids)}")

def per_tumor_omega(df, col):
    long = pd.concat([
        df[["sample_a", col]].rename(columns={"sample_a": "s"}),
        df[["sample_b", col]].rename(columns={"sample_b": "s"}),
    ], ignore_index=True)
    g = long.groupby("s")[col]
    return g.mean().rename("mean"), g.median().rename("median"), g.size().rename("n_pairs")

om_main, med_main, npr_main = per_tumor_omega(tt, "omega")
kf_main, _, _ = per_tumor_omega(tt, "kf")
kn_main, _, _ = per_tumor_omega(tt, "kn")

cv = pd.read_csv(CV_PAIRS)
om_cv, med_cv, npr_cv = per_tumor_omega(cv[cv.pair_type == "TT"], "omega_alt")
el = pd.read_csv(EL_PAIRS)
om_el, med_el, npr_el = per_tumor_omega(el[el.pair_type == "TT"], "omega_alt")

# sensitivity: omega against normal tissue (TN pairs) -- NOT the published
# per-tumor statistic, reported only as an aggregation-choice check
tn = pairs[pairs.pair_type == "TN"]
tum_in_tn = tn[tn.sample_a.str[-2:].isin(["01", "02", "06"])]
om_tn = per_tumor_omega(tum_in_tn, "omega")[0]
log(f"TN pairs: {len(tn)} (tumor endpoints {len(om_tn)}); "
    f"median pairs/tumor: main {int(npr_main.median())}, cv {int(npr_cv.median())}")

# --------------------------------------------------------------------------
# 2. expression matrix (verbatim nc76 loader) + DE scores
# --------------------------------------------------------------------------
log("\nloading LUAD expression (verbatim nc76 loader) ...")
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")[1:]
luad_cols, luad_sids = [], []
for k, sid in enumerate(header, 0):
    parts = sid.split("-")
    if len(parts) < 4 or parts[1] not in LUAD_TSS:
        continue
    if parts[3][:2] in ("01", "11"):
        luad_cols.append(k + 1)
        luad_sids.append(sid)
df = pd.read_csv(TCGA_FILE, sep="\t", usecols=[0] + luad_cols, compression="gzip")
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
log(f"  genes after filters: {len(genes)}; LUAD columns: {len(luad_sids)}")

sid_row = {s: i for i, s in enumerate(luad_sids)}
tum_ids = [s for s in tumor_ids if s in sid_row]
tum_cols = np.array([sid_row[s] for s in tum_ids])
log(f"  tumors with expression: {len(tum_ids)} / {len(tumor_ids)}")

mut = json.load(open(MUT, encoding="utf-8"))
egfr = {s[:15] for s in mut["egfr_samples"]}
kras = {s[:15] for s in mut["kras_samples"]}
def group_of(s):
    e, k = s in egfr, s in kras
    if e and k:
        return "DOUBLE"
    return "EGFR" if e else ("KRAS" if k else "WT")
groups = np.array([group_of(s) for s in tum_ids])
is_kras, is_egfr = groups == "KRAS", groups == "EGFR"
is_wt = groups == "WT"
log(f"  groups: KRAS {is_kras.sum()}, EGFR {is_egfr.sum()}, WT {is_wt.sum()}, "
    f"DOUBLE {(groups=='DOUBLE').sum()}")

X = expr_log[:, tum_cols]  # (G, n_tum)

def loo_de_score(mask_case, mask_neg):
    """LOO Welch-t weighted projection (verbatim nc76 loo_de_score)."""
    n_case, n_neg = mask_case.sum(), mask_neg.sum()
    s_c = X[:, mask_case].sum(1); ss_c = (X[:, mask_case] ** 2).sum(1)
    s_n = X[:, mask_neg].sum(1); ss_n = (X[:, mask_neg] ** 2).sum(1)
    out = np.zeros(X.shape[1])
    for i in range(X.shape[1]):
        x = X[:, i]
        if mask_case[i]:
            sc, ssc, nc = s_c - x, ss_c - x ** 2, n_case - 1
            sn, ssn, nn = s_n, ss_n, n_neg
        elif mask_neg[i]:
            sc, ssc, nc = s_c, ss_c, n_case
            sn, ssn, nn = s_n - x, ss_n - x ** 2, n_neg - 1
        else:
            sc, ssc, nc = s_c, ss_c, n_case
            sn, ssn, nn = s_n, ss_n, n_neg
        m1, m0 = sc / nc, sn / nn
        v1 = np.maximum(ssc / nc - m1 ** 2, 1e-9)
        v0 = np.maximum(ssn / nn - m0 ** 2, 1e-9)
        t = (m1 - m0) / np.sqrt(v1 / nc + v0 / nn)
        w = t / max(np.abs(t).sum(), 1e-12)
        out[i] = float((w * (x - (s_c + s_n) / (nc + nn))).sum())
    return out

log("LOO DE projection, KRAS vs EGFR ...")
de_kras_egfr = loo_de_score(is_kras, is_egfr)
log("LOO DE projection, KRAS vs WT (reproduction check) ...")
de_kras_wt = loo_de_score(is_kras, is_wt)

def cv5_de_score(mask_case, mask_neg, n_top=200, folds=5, seed=SEED):
    """5-fold CV, Wilcoxon top-200 DE score. Genes and standardisation
    learned on the training folds only."""
    idx = np.where(mask_case | mask_neg)[0]
    y = np.where(mask_case[idx], 1, 0)
    rng = np.random.default_rng(seed)
    fold = np.empty(len(idx), int)
    for cls in (0, 1):
        sel = np.where(y == cls)[0]
        rng.shuffle(sel)
        fold[sel] = np.arange(len(sel)) % folds
    score = np.full(len(idx), np.nan)
    for f in range(folds):
        tr = fold != f
        te = fold == f
        A = X[:, idx[tr]]; ytr = y[tr]
        n1, n0 = ytr.sum(), (1 - ytr).sum()
        A1, A0 = A[:, ytr == 1], A[:, ytr == 0]
        r = rankdata(A, axis=1)
        R1 = r[:, ytr == 1].sum(1)
        U = R1 - n1 * (n1 + 1) / 2.0
        from scipy.stats import mannwhitneyu
        pvals = np.array([mannwhitneyu(A1[g], A0[g], alternative="two-sided").pvalue
                          for g in range(A.shape[0])])
        top = np.argsort(pvals)[:n_top]
        direction = np.sign(A1[top].mean(1) - A0[top].mean(1))
        mu = A[top].mean(1); sd = A[top].std(1, ddof=1); sd[sd < 1e-9] = 1e-9
        Z = (X[np.ix_(top, idx[te])] - mu[:, None]) / sd[:, None]
        score[te] = (Z * direction[:, None]).mean(0)
    out = np.full(X.shape[1], np.nan)
    out[idx] = score
    return out

log("5-fold CV Wilcoxon top-200 DE, KRAS vs EGFR ...")
de5 = cv5_de_score(is_kras, is_egfr)

# --------------------------------------------------------------------------
# 3. assemble the score table
# --------------------------------------------------------------------------
score_df = pd.DataFrame({
    "sample": tum_ids,
    "group": groups,
    "omega_main": [om_main.get(s, np.nan) for s in tum_ids],
    "omega_lowestcv": [om_cv.get(s, np.nan) for s in tum_ids],
    "omega_EL": [om_el.get(s, np.nan) for s in tum_ids],
    "omega_TN_median": [om_tn.get(s, np.nan) for s in tum_ids],
    "kf_main": [kf_main.get(s, np.nan) for s in tum_ids],
    "kn_main": [kn_main.get(s, np.nan) for s in tum_ids],
    "de_score": de_kras_egfr,
    "de_score_5cv": de5,
    "de_score_KRASvsWT": de_kras_wt,
})
score_df = score_df[score_df.group.isin(["KRAS", "EGFR"])].reset_index(drop=True)

# admixture-adjusted scores (the abstract claim is "after purity adjustment"):
# residualise each score on the ESTIMATE stromal+immune score inside the
# KRAS-vs-EGFR cohort, then re-rank.
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
adm = pd.read_csv(ADMIX)
adm = adm[adm.type == "Tumor"].set_index("sample").admix
score_df["admix"] = score_df["sample"].map(adm)
def residualise(y, x):
    m = np.isfinite(y) & np.isfinite(x)
    out = np.full(len(y), np.nan)
    Xd = np.column_stack([np.ones(m.sum()), x[m]])
    beta, *_ = np.linalg.lstsq(Xd, y[m], rcond=None)
    out[m] = y[m] - Xd @ beta
    return out
for c in ("omega_main", "omega_lowestcv", "de_score"):
    score_df[c + "_adj"] = residualise(score_df[c].values, score_df["admix"].values)
log(f"admixture covariate coverage: {score_df.admix.notna().sum()}/{len(score_df)}")

log(f"\nscored KRAS-vs-EGFR cohort: n={len(score_df)} "
    f"(KRAS {(score_df.group=='KRAS').sum()}, EGFR {(score_df.group=='EGFR').sum()})")

# --------------------------------------------------------------------------
# 4. AUC machinery
# --------------------------------------------------------------------------
def auc(score, pos):
    v = score
    r = rankdata(np.concatenate([v[pos], v[~pos]]))
    n1, n0 = pos.sum(), (~pos).sum()
    return float((r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def boot_ci(score, pos, B=B_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    pi, ni = np.where(pos)[0], np.where(~pos)[0]
    vals = np.empty(B)
    for b in range(B):
        pb = rng.choice(pi, len(pi), replace=True)
        nb = rng.choice(ni, len(ni), replace=True)
        vals[b] = auc_idx(score, pb, nb)
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)), vals

def auc_idx(score, pb, nb):
    v = np.concatenate([score[pb], score[nb]])
    r = rankdata(v)
    n1, n0 = len(pb), len(nb)
    return float((r[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def delong_paired(score1, score2, pos):
    """DeLong (1988) paired AUC difference test with fast placement values."""
    struct = np.concatenate([np.ones(pos.sum()), np.zeros((~pos).sum())])
    n1, n0 = int(pos.sum()), int((~pos).sum())
    def placements(s):
        v = s if len(s) == len(pos) else s
        posv = v[pos]
        negv = v[~pos]
        return (rankdata(np.concatenate([posv, negv]))[:n1],
                rankdata(np.concatenate([posv, negv]))[n1:])
    V10 = np.empty((2, n1)); V01 = np.empty((2, n0))
    for k, s in enumerate((score1, score2)):
        rp, rn = placements(s)
        V10[k] = (rp - rankdata(rp)) / n0     # placement of positives
        V01[k] = (rn - rankdata(rn)) / n1     # placement of negatives
    # correct definitions
    for k, s in enumerate((score1, score2)):
        posv, negv = s[pos], s[~pos]
        r_all = rankdata(np.concatenate([posv, negv]))
        V10[k] = (r_all[:n1] - rankdata(posv)) / n0
        V01[k] = 1.0 - (r_all[n1:] - rankdata(negv)) / n1
    S10 = np.cov(V10); S01 = np.cov(V01)
    var = (S10[0, 0] + S10[1, 1] - 2 * S10[0, 1]) / n1 + \
          (S01[0, 0] + S01[1, 1] - 2 * S01[0, 1]) / n0
    a1, a2 = auc_idx(score1, np.where(pos)[0], np.where(~pos)[0]), \
             auc_idx(score2, np.where(pos)[0], np.where(~pos)[0])
    z = (a1 - a2) / np.sqrt(max(var, 1e-18))
    from scipy.stats import norm
    return float(z), float(2 * norm.sf(abs(z))), float(a1 - a2)

def wilson(k, n, z=1.959963985):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / den
    return float(max(0.0, c - h)), float(min(1.0, c + h))

pos = (score_df.group == "KRAS").values
n_pos, n_neg = int(pos.sum()), int((~pos).sum())

METRICS = [("omega", "omega_main", "main"),
           ("omega", "omega_lowestcv", "lowest_cv"),
           ("omega", "omega_EL", "EL_literature"),
           ("omega_TNmedian", "omega_TN_median", "main_TN"),
           ("kf", "kf_main", "main"),
           ("kn", "kn_main", "main"),
           ("DE", "de_score", "none_LOO_projection"),
           ("DE", "de_score_5cv", "none_5fold_wilcoxon_top200"),
           ("omega_admix_adj", "omega_main_adj", "main"),
           ("omega_admix_adj", "omega_lowestcv_adj", "lowest_cv"),
           ("DE_admix_adj", "de_score_adj", "none_LOO_projection")]

auc_rows, boot_store = [], {}
for name, col, panel in METRICS:
    sc = score_df[col].values
    m = np.isfinite(sc)
    p_ = pos & m
    a = auc(sc[m], pos[m])
    lo, hi, vals = boot_ci(sc[m], pos[m])
    boot_store[(name, panel, "subset")] = (sc[m], pos[m], vals)
    auc_rows.append({"metric": name, "panel": panel, "auc": round(a, 4),
                     "auc_lo": round(lo, 4), "auc_hi": round(hi, 4),
                     "n_pos": int(p_.sum()), "n_neg": int((~p_ & m).sum()),
                     "method": "rank AUC, stratified bootstrap B=2000",
                     "notes": f"{col}; bootstrap P(AUC<=0.5)={float((vals<=0.5).mean()):.4f}"})
    log(f"  {name:14s} [{panel:22s}] AUC {a:.3f} [{lo:.3f},{hi:.3f}] "
        f"(n {int(p_.sum())}/{int((~p_&m).sum())})")

# --------------------------------------------------------------------------
# 5. paired comparisons (DeLong + paired bootstrap of the difference)
# --------------------------------------------------------------------------
def paired_diff(s1, s2, pos, B=B_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    pi, ni = np.where(pos)[0], np.where(~pos)[0]
    d = np.empty(B)
    for b in range(B):
        pb = rng.choice(pi, len(pi), replace=True)
        nb = rng.choice(ni, len(ni), replace=True)
        d[b] = auc_idx(s1, pb, nb) - auc_idx(s2, pb, nb)
    obs = auc_idx(s1, pi, ni) - auc_idx(s2, pi, ni)
    # two-sided bootstrap P: 2*min share of the null-ish tail
    p_b = 2 * min((d <= 0).mean(), (d >= 0).mean())
    return obs, float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5)), min(1.0, p_b)

cmp_rows = []
PAIRS_TO_TEST = [
    ("AUC_omega_main - AUC_DE_LOO", "omega_main", "de_score"),
    ("AUC_omega_lowestcv - AUC_DE_LOO", "omega_lowestcv", "de_score"),
    ("AUC_omega_main - AUC_omega_lowestcv", "omega_main", "omega_lowestcv"),
    ("AUC_omega_EL - AUC_omega_main", "omega_EL", "omega_main"),
    ("AUC_DE_LOO - AUC_DE_5cv", "de_score", "de_score_5cv"),
    ("AUC_omega_main - AUC_DE_5cv", "omega_main", "de_score_5cv"),
    ("AUC_omega_TNmedian - AUC_omega_main", "omega_TN_median", "omega_main"),
    ("AUC_omega_main_adj - AUC_DE_adj", "omega_main_adj", "de_score_adj"),
    ("AUC_kf_main - AUC_omega_main", "kf_main", "omega_main"),
]
for label, c1, c2 in PAIRS_TO_TEST:
    s1, s2 = score_df[c1].values, score_df[c2].values
    m = np.isfinite(s1) & np.isfinite(s2)
    z, p_dl, d = delong_paired(s1[m], s2[m], pos[m])
    obs, lo, hi, p_b = paired_diff(s1[m], s2[m], pos[m])
    cmp_rows.append({"comparison": label, "delta": round(obs, 4),
                     "delta_lo": round(lo, 4), "delta_hi": round(hi, 4),
                     "p_value": round(p_dl, 4),
                     "test": "DeLong paired AUC (z={:.3f}); "
                             "paired bootstrap B=2000 delta CI, P_boot={:.4f}".format(z, p_b)})
    log(f"  {label:42s} d={obs:+.3f} [{lo:+.3f},{hi:+.3f}] "
        f"DeLong z={z:+.2f} P={p_dl:.4f} P_boot={p_b:.4f}")

# panel correlation
rho_s, p_s = spearmanr(score_df.omega_main, score_df.omega_lowestcv)
rho_all, p_all = spearmanr(score_df.omega_main, score_df.omega_EL)
log(f"  Spearman(omega_main, omega_lowestcv) = {rho_s:.3f} (P={p_s:.2e})")
log(f"  Spearman(omega_main, omega_EL)        = {rho_all:.3f} (P={p_all:.2e})")
cmp_rows.append({"comparison": "Spearman_omega_main_vs_lowestcv", "delta": round(rho_s, 4),
                 "delta_lo": np.nan, "delta_hi": np.nan, "p_value": float(p_s),
                 "test": "Spearman rho, sample-level scores, n=%d" % len(score_df)})
cmp_rows.append({"comparison": "Spearman_omega_main_vs_EL", "delta": round(rho_all, 4),
                 "delta_lo": np.nan, "delta_hi": np.nan, "p_value": float(p_all),
                 "test": "Spearman rho, sample-level scores, n=%d" % len(score_df)})

# --------------------------------------------------------------------------
# 6. threshold sensitivity (Youden; fixed specificity 0.90)
# --------------------------------------------------------------------------
def threshold_report(sc, pos, tag):
    m = np.isfinite(sc); s = sc[m]; p = pos[m]
    n1, n0 = p.sum(), (~p).sum()
    v = np.unique(s)
    cuts = np.concatenate([[v[0] - 1e-12], (v[:-1] + v[1:]) / 2, [v[-1] + 1e-12]])
    best = None
    for c in cuts:
        pred = s > c
        sens = (pred & p).sum() / n1
        spec = (~pred & ~p).sum() / n0
        j = sens + spec - 1
        if best is None or j > best[0]:
            best = (j, c, sens, spec)
    j, c, sens, spec = best
    tp = int(((s > c) & p).sum()); fp = int(((s > c) & ~p).sum())
    tn = int((~(s > c) & ~p).sum()); fn = int((~(s > c) & p).sum())
    acc = (tp + tn) / (n1 + n0)
    se_lo, se_hi = wilson(tp, int(n1))
    sp_lo, sp_hi = wilson(tn, int(n0))
    ac_lo, ac_hi = wilson(tp + tn, int(n1 + n0))
    # sensitivity at specificity >= 0.90 (threshold = 90th pct of negatives)
    c90 = np.quantile(s[~p], 0.90)
    sens90 = ((s > c90) & p).sum() / n1
    s90_lo, s90_hi = wilson(int(((s > c90) & p).sum()), int(n1))
    log(f"  [{tag}] Youden cut={c:.3f}: sens {sens:.3f} [{se_lo:.3f},{se_hi:.3f}], "
        f"spec {spec:.3f} [{sp_lo:.3f},{sp_hi:.3f}], acc {acc:.3f} [{ac_lo:.3f},{ac_hi:.3f}]")
    log(f"  [{tag}] at spec=0.90 (cut={c90:.3f}): sens {sens90:.3f} [{s90_lo:.3f},{s90_hi:.3f}]")
    return {"tag": tag, "J": j, "cut": c, "sens": sens, "se_lo": se_lo, "se_hi": se_hi,
            "spec": spec, "sp_lo": sp_lo, "sp_hi": sp_hi, "acc": acc,
            "ac_lo": ac_lo, "ac_hi": ac_hi, "sens90": sens90,
            "s90_lo": s90_lo, "s90_hi": s90_hi}

log("\nthreshold sensitivity:")
th = [threshold_report(score_df.de_score.values, pos, "DE_LOO"),
      threshold_report(score_df.omega_main.values, pos, "omega_main"),
      threshold_report(score_df.omega_lowestcv.values, pos, "omega_lowestcv")]

# --------------------------------------------------------------------------
# 7. power at the observed n
# --------------------------------------------------------------------------
from scipy.stats import norm
def power_auc(A, n1, n0, alpha=0.05):
    Q1 = A / (2 - A); Q2 = 2 * A ** 2 / (1 + A)
    se = np.sqrt((A * (1 - A) + (n1 - 1) * (Q1 - A ** 2) + (n0 - 1) * (Q2 - A ** 2))
                 / (n1 * n0))
    z_a = norm.ppf(1 - alpha / 2)
    return float(norm.sf(z_a - (A - 0.5) / se)), float(se)
pw70, se70 = power_auc(0.70, n_pos, n_neg)
pw65, _ = power_auc(0.65, n_pos, n_neg)
pw60, _ = power_auc(0.60, n_pos, n_neg)
pw75, _ = power_auc(0.75, n_pos, n_neg)
log(f"\npower (two-sided alpha=0.05, n {n_pos} vs {n_neg}): "
    f"AUC 0.60 -> {pw60:.2f}; 0.65 -> {pw65:.2f}; 0.70 -> {pw70:.2f} "
    f"(Hanley-McNeil SE {se70:.3f}); 0.75 -> {pw75:.2f}")

# --------------------------------------------------------------------------
# 7b. alignment check against the published nc76 numbers (KRAS vs WT)
# --------------------------------------------------------------------------
om_all = np.array([om_main.get(s, np.nan) for s in tum_ids])
sel_kw = is_kras | is_wt
log("\nalignment check vs nc76 (KRAS vs WT, restricted cohort):")
log(f"  omega   AUC = {auc(om_all[sel_kw], is_kras[sel_kw]):.4f}  (published 0.6608)")
log(f"  DE(LOO) AUC = {auc(de_kras_wt[sel_kw], is_kras[sel_kw]):.4f}  (published 0.7363)")

# --------------------------------------------------------------------------
# 8. write deliverables
# --------------------------------------------------------------------------
out = pd.concat([
    pd.DataFrame({"sample": score_df["sample"], "group": score_df["group"],
                  "panel": "main", "omega_score": score_df["omega_main"],
                  "de_score": score_df["de_score"]}),
    pd.DataFrame({"sample": score_df["sample"], "group": score_df["group"],
                  "panel": "lowest_cv", "omega_score": score_df["omega_lowestcv"],
                  "de_score": np.nan}),
], ignore_index=True)
out.to_csv(OUT_SCORES, index=False)
pd.DataFrame(auc_rows).to_csv(OUT_AUC, index=False)
pd.DataFrame(cmp_rows).to_csv(OUT_CMP, index=False)
log(f"\nsaved: {OUT_SCORES}\nsaved: {OUT_AUC}\nsaved: {OUT_CMP}")

# extra numbers for the report
log("\n--- report payload ---")
log(f"n_KRAS={n_pos} n_EGFR={n_neg}")
log(f"medians: KRAS omega {np.median(score_df.omega_main[pos]):.1f} vs "
    f"EGFR {np.median(score_df.omega_main[~pos]):.1f}")
log(f"reproduction KRAS vs WT AUC: omega {auc(score_df.omega_main.values, (score_df.group=='KRAS').values):.4f} (this cohort)")
log(f"power70={pw70:.3f} power75={pw75:.3f}")
for t in th:
    log("TH " + json.dumps(t))
log(f"total {time.time()-t0:.0f}s")
(ROOT / "results" / "nc79_a3_run.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("DONE")
