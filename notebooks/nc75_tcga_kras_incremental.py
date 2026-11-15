# -*- coding: utf-8 -*-
"""
nc75 (blind-review R5, cancer reviewer M4 / panel P0-2): KRAS incremental
validation for the LUAD driver-mutation contrast.

Three gaps flagged by the review panel:
  (a) The published KRAS contrast uses per-pair circular top-200 panels;
      the effect of a FIXED functional panel (fixed across pairs and
      within permutations) on the empirical P was never reported.
      -> Recompute k_f / omega for the authoritative 2,000 LUAD TT pairs
         with a pre-specified fixed panel (top-200 non-HK genes by
         across-tumor variance of the log representation), reusing the
         published k_n (HK computation is panel-independent), and rerun
         the whole-tumor label permutation (B = 10,000, seed 42).
  (b) TP53 co-mutation was never adjusted.
      -> TP53 mutation status fetched from cBioPortal
         (luad_tcga_pan_can_atlas_2018, entrez 7157), cached to
         data/tcga/luad_tp53_cbioportal.json; added as a covariate.
  (c) Increment over a proliferation index was never tested.
      -> Proliferation score = mean of log representation of
         MKI67, TOP2A, PCNA per tumor; added as a covariate.

Expression loading and filtering mirror notebooks/85_tcga_linear_norm_v44.py
verbatim (LUAD TSS codes, expression>0 presence pass, mean >= 0.5 filter,
per-cancer HK mapping, linear probability mapping p_i = (x+1)/sum(x+1),
identity ranking on the log representation). Only the functional panel
selection changes (fixed vs per-pair circular).

Outputs (all NEW files, nc75 suffix):
  results/nc75_tcga_kras_incremental.csv    model x metric x contrast table
  results/nc75_tcga_kras_incremental.txt    run log
  data/tcga/luad_tp53_cbioportal.json       TP53 status cache (network once)
"""
import json
import sys
import time
import urllib.request
import gzip
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TCGA_FILE = ROOT / "data" / "tcga" / "tcga_RSEM_gene_tpm.gz"
PROBEMAP = ROOT / "data" / "tcga" / "probemap.tsv"
HK_FILE = ROOT / "data" / "housekeeping" / "Human_Mouse_Common.csv"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
CLIN = ROOT / "data" / "tcga" / "luad_patient_clinical_cbioportal.json"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
TP53_CACHE = ROOT / "data" / "tcga" / "luad_tp53_cbioportal.json"
OUT_CSV = ROOT / "results" / "nc75_tcga_kras_incremental.csv"
OUT_TXT = ROOT / "results" / "nc75_tcga_kras_incremental.txt"

B = 10_000
SEED = 42
N_TOP_KF = 200
PROLIF_GENES = ["MKI67", "TOP2A", "PCNA"]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

t0 = time.time()

# ---------------------------------------------------------------------------
# 0. TP53 mutation status (cBioPortal; cached after first successful fetch)
# ---------------------------------------------------------------------------
log("0. TP53 mutation status")
pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
luad_tt = pairs[(pairs.cancer == "TCGA-LUAD") & (pairs.pair_type == "TT")]
tumor_ids = sorted(set(luad_tt.sample_a) | set(luad_tt.sample_b))
log(f"  LUAD TT pairs: {len(luad_tt)}, tumors: {len(tumor_ids)}")

if TP53_CACHE.exists():
    tp53_mut = set(json.load(open(TP53_CACHE, encoding="utf-8"))["tp53_mut_samples"])
    log(f"  loaded cache: {len(tp53_mut)} TP53-mutant samples")
else:
    url = ("https://www.cbioportal.org/api/molecular-profiles/"
           "luad_tcga_pan_can_atlas_2018_mutations/mutations/fetch"
           "?projection=SUMMARY&pageSize=100000")
    body = json.dumps({"entrezGeneIds": [7157],
                       "sampleIds": tumor_ids}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        recs = json.loads(resp.read().decode("utf-8"))
    tp53_mut = set(r["sampleId"][:15] for r in recs)
    json.dump({"source": url, "entrez": 7157, "n_records": len(recs),
               "tp53_mut_samples": sorted(tp53_mut)},
              open(TP53_CACHE, "w", encoding="utf-8"), indent=2)
    log(f"  fetched cBioPortal: {len(recs)} records, "
        f"{len(tp53_mut)} TP53-mutant of {len(tumor_ids)} tumors")

# ---------------------------------------------------------------------------
# 1. Expression matrix: LUAD tumor + normal, mirrors 85_tcga_linear_norm_v44
# ---------------------------------------------------------------------------
log("\n1. Loading LUAD expression (mirrors 85_tcga_linear_norm_v44)")
LUAD_TSS = {"05", "35", "38", "44", "49", "50", "55", "64", "67", "73",
            "75", "78", "86", "91", "93", "97", "J2", "L3", "L4", "M1",
            "MP", "MT", "N1", "N6", "O1", "S2", "TR", "TV", "TQ", "NJ",
            "KN", "LF"}
with gzip.open(TCGA_FILE, "rt") as fh:
    header = fh.readline().strip().split("\t")
luad_cols, luad_sids = [], []
for k, sid in enumerate(header[1:], 1):
    parts = sid.split("-")
    if len(parts) < 4 or parts[1] not in LUAD_TSS:
        continue
    if parts[3][:2] in ("01", "11"):
        luad_cols.append(k)
        luad_sids.append(sid)
log(f"  LUAD columns: {len(luad_sids)}")

usecols = [0] + luad_cols
df = pd.read_csv(TCGA_FILE, sep="\t", usecols=usecols, compression="gzip")
df.columns = ["gene"] + luad_sids
vals = df[luad_sids].values.astype(np.float64)
# presence pass (expression > 0 in any sample) then mean >= 0.5 (verbatim v44)
present = (vals > 0).any(axis=1)
vals = vals[present]
genes = df.gene.values[present]
keep = vals.mean(axis=1) >= 0.5
vals = vals[:, :][keep]
genes = genes[keep]
del df
log(f"  genes after filters: {len(genes)}")

expr_log = np.log2(np.maximum(vals, 0) + 1)          # identity ranking scale
expr_lin = np.maximum(vals, 0) + 1.0                  # linear mapping scale
del vals

# HK mapping (verbatim v44)
pm = pd.read_csv(PROBEMAP, sep="\t")
ens_to_symbol = {}
for r in pm.itertuples(index=False):
    ens_to_symbol[str(r[0]).split(".")[0]] = str(r[1])
symbol_to_ens = {}
for eid, sym in ens_to_symbol.items():
    symbol_to_ens.setdefault(sym, []).append(eid)
hk_df = pd.read_csv(HK_FILE)
hk_human = set()
for row in hk_df.iloc[:, 0].dropna().astype(str):
    p_ = row.split(";")
    if len(p_) >= 2:
        hk_human.add(p_[1].strip())
gene_ens = np.array([g.split(".")[0] for g in genes])
ens_local = {e: i for i, e in enumerate(gene_ens)}
hk_idx = sorted({ens_local[e] for s in hk_human for e in symbol_to_ens.get(s, [])
                 if e in ens_local})
hk_set = set(hk_idx)
log(f"  HK genes mapped: {len(hk_idx)}")

# ---------------------------------------------------------------------------
# 2. Fixed functional panel: top-200 non-HK by across-tumor variance (log)
# ---------------------------------------------------------------------------
tumor_mask = np.array([s in set(tumor_ids) for s in luad_sids])
var_t = expr_log[:, tumor_mask].var(axis=1)
order = np.argsort(var_t)[::-1]
panel = np.array([g for g in order if g not in hk_set][:N_TOP_KF])
panel_syms = sorted({ens_to_symbol.get(gene_ens[i], "?") for i in panel[:10]})
log(f"  fixed panel: {len(panel)} genes; top-10 by variance: {panel_syms}")

# proliferation score (log representation), per sample
prolif_idx = []
for sym in PROLIF_GENES:
    for eid in symbol_to_ens.get(sym, []):
        if eid in ens_local:
            prolif_idx.append(ens_local[eid])
            break
log(f"  proliferation genes mapped: {[PROLIF_GENES[i] for i in range(len(prolif_idx))]}")
prolif_score = expr_log[prolif_idx, :].mean(axis=0)
prolif_map = dict(zip(luad_sids, prolif_score))

# ---------------------------------------------------------------------------
# 3. k_f / omega under the fixed panel for the authoritative TT pairs
# ---------------------------------------------------------------------------
log("\n2. Recomputing k_f/omega with fixed panel for authoritative pairs")
sid_row = {s: i for i, s in enumerate(luad_sids)}

def js_linear(a, b):
    sa, sb = a.sum(), b.sum()
    if sa <= 0 or sb <= 0:
        return 0.0 if (sa <= 0 and sb <= 0) else 1.0
    p, q = a / sa, b / sb
    m = 0.5 * (p + q)
    kl = 0.0
    mp = p > 0
    if mp.any():
        kl += np.sum(p[mp] * np.log2(p[mp] / m[mp]))
    mq = q > 0
    if mq.any():
        kl += np.sum(q[mq] * np.log2(q[mq] / m[mq]))
    return float(0.5 * kl)

lin_panel = expr_lin[panel, :]   # (200, n_samples)
kf_fixed = np.empty(len(luad_tt))
pa = luad_tt.sample_a.map(sid_row).values
pb = luad_tt.sample_b.map(sid_row).values
for k in range(len(luad_tt)):
    kf_fixed[k] = js_linear(lin_panel[:, pa[k]], lin_panel[:, pb[k]])
kn = luad_tt.kn.values
luad_tt = luad_tt.assign(kf_fixed=kf_fixed,
                         omega_fixed=kf_fixed / np.maximum(kn, 1e-12))
log(f"  kf_fixed: median {np.median(kf_fixed):.4f} "
    f"(circular median {luad_tt.kf.median():.4f}); "
    f"omega_fixed median {np.median(luad_tt.omega_fixed):.1f} "
    f"(circular median {luad_tt.omega.median():.1f})")

# per-tumor means (same long-format aggregation as nc52)
long = pd.concat([
    luad_tt[["sample_a", "omega", "kf", "kn", "omega_fixed", "kf_fixed"]]
        .rename(columns={"sample_a": "sample"}),
    luad_tt[["sample_b", "omega", "kf", "kn", "omega_fixed", "kf_fixed"]]
        .rename(columns={"sample_b": "sample"}),
], ignore_index=True)
per_tumor = long.groupby("sample").agg(
    n_pairs=("omega", "size"), omega=("omega", "mean"), kf=("kf", "mean"),
    kn=("kn", "mean"), omega_fixed=("omega_fixed", "mean"),
    kf_fixed=("kf_fixed", "mean")).reset_index()

# ---------------------------------------------------------------------------
# 4. Covariates + mutation groups (verbatim nc52 prep) + TP53 + proliferation
# ---------------------------------------------------------------------------
log("\n3. Covariates and models")
clin = json.load(open(CLIN, encoding="utf-8"))
pat = {}
for rec in clin:
    b = rec.get("patientId", "")
    key = b if b.startswith("TCGA") else "TCGA-" + b
    if rec.get("clinicalAttributeId") in ("TOBACCO_SMOKING_HISTORY_INDICATOR",
                                          "SEX", "AGE"):
        pat.setdefault(key, {})[rec["clinicalAttributeId"]] = rec.get("value")
df_pat = pd.DataFrame([
    {"patient": k,
     "smoke_ind": v.get("TOBACCO_SMOKING_HISTORY_INDICATOR"),
     "sex": v.get("SEX"), "age": v.get("AGE")}
    for k, v in pat.items()])
df_pat["ever_smoke"] = df_pat.smoke_ind.map(
    lambda x: 1.0 if str(x) in ("2", "3", "4", "5", "6")
    else (0.0 if str(x) == "1" else np.nan))
df_pat["age_f"] = pd.to_numeric(df_pat.age, errors="coerce")

mut = json.load(open(MUT))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])
def group_of(s):
    e, k = s in egfr, s in kras
    if e and k:
        return "DOUBLE"
    return "EGFR" if e else ("KRAS" if k else "WT")
per_tumor["group"] = per_tumor["sample"].map(group_of)
per_tumor = per_tumor[per_tumor.group != "DOUBLE"].copy()
per_tumor["patient"] = per_tumor["sample"].str[:12]
per_tumor["tp53"] = per_tumor["sample"].isin(tp53_mut).astype(float)
per_tumor["prolif"] = per_tumor["sample"].map(prolif_map)

df_ = per_tumor.merge(df_pat[["patient", "ever_smoke", "age_f", "sex"]],
                      on="patient", how="left")
adm = pd.read_csv(ADMIX)
adm = adm[adm.type == "Tumor"][["sample", "admix"]]
d3 = df_.merge(adm, on="sample", how="inner")
d3 = d3[d3.ever_smoke.notna() & d3.prolif.notna()].copy()
d3["ever_smoke"] = d3.ever_smoke.astype(float)
d3["admix_z"] = (d3.admix - d3.admix.mean()) / d3.admix.std(ddof=1)
d3["prolif_z"] = (d3.prolif - d3.prolif.mean()) / d3.prolif.std(ddof=1)
log(f"  model cohort n={len(d3)} "
    f"(WT {(d3.group=='WT').sum()}, EGFR {(d3.group=='EGFR').sum()}, "
    f"KRAS {(d3.group=='KRAS').sum()}); TP53-mutant {int(d3.tp53.sum())}")
from scipy.stats import spearmanr
rho_p, pp = spearmanr(d3.omega, d3.prolif)
log(f"  Spearman(omega, proliferation) = {rho_p:.3f} (P={pp:.2e})")
log(f"  TP53 frequency by group: " + "; ".join(
    f"{g} {d3[d3.group==g].tp53.mean():.2f}" for g in ("WT", "EGFR", "KRAS")))

# ---------------------------------------------------------------------------
# 5. Whole-tumor label permutation (verbatim nc52 machinery)
# ---------------------------------------------------------------------------
CM = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 1.0]])
CONTRASTS = ["EGFR - WT", "KRAS - WT", "KRAS - EGFR"]

def design(dat, covars):
    F = np.column_stack([np.ones(len(dat))] + [dat[c].values for c in covars])
    G = np.column_stack([(dat.group == "EGFR").astype(float).values,
                         (dat.group == "KRAS").astype(float).values])
    return F, G

def ols_contrasts(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return CM @ beta[-2:]

rng = np.random.default_rng(SEED)
MODELS = [
    ("B_smoke_admix", ["ever_smoke", "admix_z"],
     ["omega", "kf", "kn"]),
    ("B_smoke_admix_fixedpanel", ["ever_smoke", "admix_z"],
     ["omega_fixed", "kf_fixed"]),
    ("B_smoke_admix_tp53", ["ever_smoke", "admix_z", "tp53"],
     ["omega", "kf", "omega_fixed", "kf_fixed"]),
    ("B_smoke_admix_prolif", ["ever_smoke", "admix_z", "prolif_z"],
     ["omega", "omega_fixed"]),
]
rows = []
for label, covars, metrics in MODELS:
    F, Gobs = design(d3, covars)
    X_obs = np.column_stack([F, Gobs])
    for metric in metrics:
        y = d3[metric].values.astype(float)
        t_obs = ols_contrasts(y, X_obs)
        exceed = np.zeros(3, dtype=int)
        for _ in range(B):
            Gp = Gobs[rng.permutation(len(d3))]
            t_perm = ols_contrasts(y, np.column_stack([F, Gp]))
            exceed += (np.abs(t_perm) >= np.abs(t_obs)).astype(int)
        p_perm = (1.0 + exceed) / (B + 1.0)
        for k, cname in enumerate(CONTRASTS):
            rows.append({"model": label, "metric": metric, "contrast": cname,
                         "n": len(d3), "B": B, "seed": SEED,
                         "obs_coef": round(float(t_obs[k]), 4),
                         "perm_p_two_sided": float(p_perm[k])})
        log(f"  {label} {metric}: " + "; ".join(
            f"{c} obs={t_obs[k]:+.3f} P={p_perm[k]:.4g}"
            for k, c in enumerate(CONTRASTS)))

# group descriptives for fixed-panel metric
for g in ("WT", "EGFR", "KRAS"):
    sub = d3[d3.group == g]
    log(f"  {g}: omega_fixed mean {sub.omega_fixed.mean():.2f} "
        f"(circular {sub.omega.mean():.2f}); n={len(sub)}")

out = pd.DataFrame(rows)
OUT_CSV.write_text(out.to_csv(index=False), encoding="utf-8")
log(f"\nsaved: {OUT_CSV}")
log(f"total time {time.time()-t0:.0f}s")
OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
print("DONE")
