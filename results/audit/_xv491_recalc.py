# xv491 independent recomputation (read-only verification)
# Recomputes all v49.1 purity/smoking numbers from authoritative raw inputs:
#   results/tcga_linear_norm_v44_all_pairs.csv  (per-pair omega/kf/kn)
#   results/nc49_tcga_admix_scores.csv          (per-sample ESTIMATE admix)
#   data/tcga/luad_egfr_kras_mutations.json     (driver labels)
#   data/tcga/luad_patient_clinical_cbioportal.json (smoking/age/sex)
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kruskal, linregress, chi2_contingency, f as fdist
import statsmodels.api as sm

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
MUT = ROOT / "data" / "tcga" / "luad_egfr_kras_mutations.json"
CLIN = ROOT / "data" / "tcga" / "luad_patient_clinical_cbioportal.json"
PUR_CSV = ROOT / "results" / "nc49_tcga_purity.csv"
SMK_CSV = ROOT / "results" / "nc49_tcga_luad_smoking.csv"
CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]
GROUPS = ["WT", "EGFR", "KRAS"]
B, SEED = 1000, 42

def out(s=""):
    print(s)

# ---------------------------------------------------------------- per-tumor
pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
out(f"pairs total: {len(pairs)} (text: 35,306)")
long_rows = []
for c in CANCERS:
    sub = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    long_rows.append(pd.concat([
        sub[["sample_a", "omega", "kf", "kn"]].rename(columns={"sample_a": "sample"}),
        sub[["sample_b", "omega", "kf", "kn"]].rename(columns={"sample_b": "sample"}),
    ], ignore_index=True).assign(cancer=c))
long = pd.concat(long_rows, ignore_index=True)
per_tumor = long.groupby(["cancer", "sample"]).agg(
    omega=("omega", "mean"), kf=("kf", "mean"), kn=("kn", "mean")).reset_index()

adm = pd.read_csv(ADMIX)
adm_t = adm[adm.type == "Tumor"][["sample", "admix"]]
per_tumor = per_tumor.merge(adm_t, on="sample", how="inner")
per_tumor["admix_z"] = per_tumor.groupby("cancer")["admix"].transform(
    lambda x: (x - x.mean()) / x.std(ddof=1))
out(f"per-tumor matched: n={len(per_tumor)} by cancer {per_tumor.groupby('cancer').size().to_dict()}")

# ------------------------------------------------------- (a) regressions
out("\n== (a) per-cancer metric ~ admix_z ==")
pur = pd.read_csv(PUR_CSV)
for c in CANCERS:
    sub = per_tumor[per_tumor.cancer == c]
    for m in ["kn", "omega", "kf"]:
        r = linregress(sub["admix_z"], sub[m])
        csv_row = pur[(pur.section == "A_regression") & (pur.cancer == c) & (pur.metric == m)]
        out(f"{c} {m}: r={r.rvalue:+.4f} P={r.pvalue:.3e} "
            f"(csv r={float(csv_row.pearson_r.iloc[0]):+.4f} P={float(csv_row.p.iloc[0]):.3e})")

# ------------------------------------------------------- (b) LUAD groups
out("\n== (b) LUAD driver groups ==")
mut = json.load(open(MUT))
egfr = set(s[:15] for s in mut["egfr_samples"])
kras = set(s[:15] for s in mut["kras_samples"])
out(f"mutation json: {len(mut['egfr_samples'])} EGFR aliquots, {len(mut['kras_samples'])} KRAS aliquots "
    f"(15-char: {len(egfr)}/{len(kras)})")

def group_of(s):
    e, k = s in egfr, s in kras
    return "DOUBLE" if e and k else ("EGFR" if e else ("KRAS" if k else "WT"))

lu = per_tumor[per_tumor.cancer == "TCGA-LUAD"].copy()
lu["group"] = lu["sample"].map(group_of)
out(f"DOUBLE excluded: {(lu.group == 'DOUBLE').sum()}")
lu = lu[lu.group != "DOUBLE"]
out(f"LUAD groups: WT={sum(lu.group=='WT')} EGFR={sum(lu.group=='EGFR')} KRAS={sum(lu.group=='KRAS')} (n={len(lu)})")

H, p_kw = kruskal(*[lu.loc[lu.group == g, "admix"].values for g in GROUPS])
out(f"admix KW H={H:.3f} P={p_kw:.4e}; means " +
    " ".join(f"{g}={lu.loc[lu.group==g,'admix'].mean():.2f}" for g in GROUPS))

for m in ["omega", "kf", "kn"]:
    X = pd.get_dummies(lu["group"], drop_first=False)[GROUPS].astype(float).drop(columns=["WT"])
    X.insert(0, "admix_z", lu["admix_z"].values)
    X.insert(0, "const", 1.0)
    fit = sm.OLS(lu[m].values, X.values).fit()
    col = {n: i for i, n in enumerate(X.columns)}
    cm = np.zeros((3, len(fit.params)))
    cm[0, col["EGFR"]] = 1.0
    cm[1, col["KRAS"]] = 1.0
    cm[2, col["KRAS"]] = 1.0; cm[2, col["EGFR"]] = -1.0
    tt = fit.t_test(cm)
    fit_r = sm.OLS(lu[m].values, X[["const", "admix_z"]].values).fit()
    F = ((fit_r.ssr - fit.ssr) / 2) / (fit.ssr / fit.df_resid)
    out(f"{m}: admix_z coef={fit.params[col['admix_z']]:.4f} P={fit.pvalues[col['admix_z']]:.3e}; "
        f"EGFR-WT {tt.effect[0]:+.4f} (P={tt.pvalue[0]:.4f}); "
        f"KRAS-WT {tt.effect[1]:+.4f} (P={tt.pvalue[1]:.3e}); "
        f"KRAS-EGFR {tt.effect[2]:+.4f} (P={tt.pvalue[2]:.3e}); "
        f"group F={F:.3f} P={fdist.sf(F, 2, fit.df_resid):.3e}")

# ------------------------------------------------------- (c) high-purity half
out("\n== (c) NN/TT high-purity half (exact bootstrap replication, seed 42 B=1000) ==")
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

for c in CANCERS:
    tt = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    nn = pairs[(pairs.cancer == c) & (pairs.pair_type == "NN")]
    adm_c = adm_t[adm_t["sample"].isin(set(tt.sample_a) | set(tt.sample_b))]
    thr = adm_c["admix"].median()
    keep = set(adm_c.loc[adm_c["admix"] <= thr, "sample"])
    tt_hi = tt[tt.sample_a.isin(keep) & tt.sample_b.isin(keep)]
    ratio_full = nn.omega.mean() / tt.omega.mean()
    ratio_hi = nn.omega.mean() / tt_hi.omega.mean()
    ci_hi = boot_ratio(tt_hi, nn, B, rng)
    out(f"{c}: all={ratio_full:.3f} (n={len(tt)}); low-admix half={ratio_hi:.3f} "
        f"[{ci_hi[0]:.3f},{ci_hi[1]:.3f}] (n={len(tt_hi)})")

# ------------------------------------------------------- (d) smoking
out("\n== (d) LUAD smoking ==")
clin = json.load(open(CLIN, encoding="utf-8"))
pat = {}
for rec in clin:
    b = rec.get("patientId", "")
    key = b if b.startswith("TCGA") else "TCGA-" + b
    a = rec.get("clinicalAttributeId")
    if a in ("TOBACCO_SMOKING_HISTORY_INDICATOR", "SMOKING_PACK_YEARS", "SEX", "AGE"):
        pat.setdefault(key, {})[a] = rec.get("value")
df_pat = pd.DataFrame([
    {"patient": k, "smoke_ind": v.get("TOBACCO_SMOKING_HISTORY_INDICATOR"),
     "pack_years": v.get("SMOKING_PACK_YEARS"), "sex": v.get("SEX"), "age": v.get("AGE")}
    for k, v in pat.items()])

def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan

df_pat["ever_smoke"] = df_pat.smoke_ind.map(
    lambda x: 1.0 if str(x) in ("2", "3", "4", "5", "6") else (0.0 if str(x) == "1" else np.nan))
df_pat["age_f"] = df_pat.age.map(to_float)
df_pat["pack_f"] = df_pat.pack_years.map(to_float)
out(f"cBioPortal patients: {len(df_pat)}; smoking known {df_pat.ever_smoke.notna().sum()} "
    f"(never={int((df_pat.ever_smoke==0).sum())}, ever={int((df_pat.ever_smoke==1).sum())}); "
    f"pack-years known {df_pat.pack_f.notna().sum()}; age known {df_pat.age_f.notna().sum()}; "
    f"sex known {df_pat.sex.notna().sum()}")
out("smoke_ind value counts: " + json.dumps(df_pat.smoke_ind.value_counts(dropna=False).to_dict()))

lu2 = per_tumor[per_tumor.cancer == "TCGA-LUAD"].copy()
lu2["group"] = lu2["sample"].map(group_of)
lu2 = lu2[lu2.group != "DOUBLE"]
lu2["patient"] = lu2["sample"].str[:12]
df = lu2.merge(df_pat[["patient", "ever_smoke", "pack_f", "age_f", "sex"]], on="patient", how="left")
out(f"LUAD merged: smoking matched {df.ever_smoke.notna().sum()}/{len(df)} "
    f"({100*df.ever_smoke.notna().mean():.1f}%); "
    f"never={int((df.ever_smoke==0).sum())} ever={int((df.ever_smoke==1).sum())}")

ct = pd.crosstab(df.group, df.ever_smoke)
out("crosstab:\n" + ct.to_string())
chi2, p_chi, dof, _ = chi2_contingency(ct.values)
out(f"chi2={chi2:.3f} dof={dof} P={p_chi:.3e}")
for g in GROUPS:
    n = ct.loc[g].sum(); ev = ct.loc[g].get(1.0, 0)
    pk = df.loc[df.group == g, "pack_f"].dropna()
    out(f"  {g}: ever {100*ev/n:.1f}% ({int(ev)}/{int(n)}); pack-years mean {pk.mean():.1f} (n={len(pk)})")

d = df[df.ever_smoke.notna()].copy()
d["ever_smoke"] = d.ever_smoke.astype(float)
d["male"] = (d.sex == "Male").astype(float)
d["age_c"] = d.age_f - d.age_f.mean()

def fit_ols(dat, metric, covars):
    X = pd.get_dummies(dat["group"], drop_first=False)[GROUPS].astype(float).drop(columns=["WT"])
    for cv in covars:
        X.insert(0, cv, dat[cv].values)
    X.insert(0, "const", 1.0)
    fit = sm.OLS(dat[metric].values, X.values).fit()
    col = {n: i for i, n in enumerate(X.columns)}
    cm = np.zeros((3, len(fit.params)))
    cm[0, col["EGFR"]] = 1.0
    cm[1, col["KRAS"]] = 1.0
    cm[2, col["KRAS"]] = 1.0; cm[2, col["EGFR"]] = -1.0
    tt = fit.t_test(cm)
    return [(float(tt.effect[k]), float(tt.sd[k]), float(tt.pvalue[k])) for k in range(3)]

d2 = d[d.age_c.notna()].copy()
d3 = d.copy()
d3["admix_z"] = (d3["admix"] - d3["admix"].mean()) / d3["admix"].std(ddof=1)
out(f"models n: group/smoke={len(d)}, +age+sex={len(d2)}, +admix={len(d3)}")
for m in ["omega", "kf", "kn"]:
    for label, dat, cov in [("group_only", d, []), ("smoke_adj", d, ["ever_smoke"]),
                            ("smoke_agesex", d2, ["ever_smoke", "age_c", "male"]),
                            ("smoke_admix", d3, ["ever_smoke", "admix_z"])]:
        r = fit_ols(dat, m, cov)
        out(f"{m} {label}: EGFR-WT {r[0][0]:+.4f}(P={r[0][2]:.4f}) "
            f"KRAS-WT {r[1][0]:+.4f}(P={r[1][2]:.3e}) KRAS-EGFR {r[2][0]:+.4f}(P={r[2][2]:.3e})")

# ------------------------------------------------------- (e) pancancer headline
out("\n== (e) pancancer NN/TT from raw pairs ==")
ntot = 0
for c in CANCERS:
    tt = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    nn = pairs[(pairs.cancer == c) & (pairs.pair_type == "NN")]
    out(f"{c}: TT pairs={len(tt)} NN pairs={len(nn)} NN/TT={nn.omega.mean()/tt.omega.mean():.3f} "
        f"kn median ratio={tt.kn.median()/nn.kn.median():.2f} "
        f"kf TT mean={tt.kf.mean():.4f} NN mean={nn.kf.mean():.4f}")
adm_all = pd.read_csv(ADMIX)
out(f"admix scores rows: {len(adm_all)}; by cancer/type: "
    + json.dumps(adm_all.groupby(['cancer','type']).size().to_dict()))
print("DONE")
