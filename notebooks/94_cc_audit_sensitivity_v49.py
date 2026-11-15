"""
v49.13 B5 + B6: complete reporting of the CC (cell-line) sample audit and
ex-CC sensitivity analyses for TCGA.
============================================================================
Reviewers: R4-N1/N2/N3.
  1. Full barcode source audit: per-cancer distribution of TCGA sample source
     codes (barcode positions 14-15, 0-indexed [13:15]) over every sample in
     the v44 linear-normalization pair table, plus identification of the
     32 ILSBio (TSS code 'CC') LIHC tumour samples (the audit rule published
     in Methods: TSS 'CC' -> LIHC; formerly mis-assigned to LUSC).
  2. Ex-CC NN/TT + k_n ratio sensitivity for LIHC (promoted from the v49.12
     temporary script to a permanent, seeded, output-logged notebook):
     cluster bootstrap B=1,000, seed 42.
  3. Ex-CC high-purity (low-admixture) half sensitivity for all five cancers
     (R4-N3: CC purity could inflate the LIHC 1.10 -> 1.17 half-sample rise).
  4. CC presence ledger: count of CC tumours entering each LIHC downstream
     analysis (purity/admixture regression, composition regression TT pairs,
     severity strata, Cox cohort via clinical JSON).

Input : results/tcga_linear_norm_v44_all_pairs.csv
        results/nc49_tcga_admix_scores.csv
        data/tcga/lihc_patient_clinical.json
Output: results/nc49_cc_barcode_audit.csv
        results/nc49_cc_excl_sensitivity.csv
        results/nc49_cc_audit_report.txt
Seed  : 42.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
PAIRS = ROOT / "results" / "tcga_linear_norm_v44_all_pairs.csv"
ADMIX = ROOT / "results" / "nc49_tcga_admix_scores.csv"
CLIN = ROOT / "data" / "tcga" / "lihc_patient_clinical.json"
OUT_BARCODE = ROOT / "results" / "nc49_cc_barcode_audit.csv"
OUT_SENS = ROOT / "results" / "nc49_cc_excl_sensitivity.csv"
OUT_LOG = ROOT / "results" / "nc49_cc_audit_report.txt"

B = 1000
SEED = 42
CANCERS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

lines = []
def log(msg=""):
    print(msg)
    lines.append(str(msg))

pairs = pd.read_csv(PAIRS).rename(columns={"omega_floor": "omega"})
admix = pd.read_csv(ADMIX)

def is_cc(s):
    s = str(s)
    return len(s) >= 7 and s[5:7] == "CC"

def source_code(s):
    s = str(s)
    return s[13:15] if len(s) >= 15 else "?"

# =====================================================================
# 1. Barcode source-code audit (all samples in the pair table)
# =====================================================================
log("=" * 70)
log("1. Barcode source-code audit (all samples in the v44 pair table)")
log("=" * 70)
all_samples = pd.DataFrame(
    {"sample": sorted(set(pairs.sample_a) | set(pairs.sample_b))})
cancer_of = dict(zip(admix["sample"], admix["cancer"]))
all_samples["cancer"] = all_samples["sample"].map(cancer_of)
all_samples["tss"] = all_samples["sample"].str[5:7]
all_samples["source_code"] = all_samples["sample"].map(source_code)
all_samples["is_cc"] = all_samples["sample"].map(is_cc)

rows_bar = []
for c in CANCERS:
    sub = all_samples[all_samples.cancer == c]
    dist = sub.source_code.value_counts().to_dict()
    cc_n = int(sub.is_cc.sum())
    row = {"cancer": c, "n_samples_total": len(sub), "n_cc_ilshio": cc_n}
    for code in ["01", "11"]:
        row[f"n_source_{code}"] = dist.get(code, 0)
    other = {k: v for k, v in dist.items() if k not in ("01", "11")}
    row["other_source_codes"] = "; ".join(f"{k}:{v}" for k, v in sorted(other.items())) or "none"
    row["tss_codes_present"] = "; ".join(
        f"{t}:{n}" for t, n in sub.tss.value_counts().items())
    rows_bar.append(row)
    log(f"{c}: samples={len(sub)}, source 01={row['n_source_01']}, "
        f"11={row['n_source_11']}, other={row['other_source_codes']}, "
        f"CC (ILSBio)={cc_n}")
bar_df = pd.DataFrame(rows_bar)
bar_df.to_csv(OUT_BARCODE, index=False)
log("saved: " + str(OUT_BARCODE))

# =====================================================================
# 2. Ex-CC NN/TT + k_n sensitivity (LIHC) -- cluster bootstrap
# =====================================================================
log("")
log("=" * 70)
log("2. Ex-CC NN/TT omega and TT/NN k_n sensitivity (LIHC), B=1000 seed 42")
log("=" * 70)
rng = np.random.default_rng(SEED)

def weighted_pair_mean(vals, ia, ib, w):
    ww = w[ia] * w[ib]
    return np.sum(vals * ww) / np.sum(ww)

def boot_ratio(df_tt, df_nn):
    t_samples = sorted(set(df_tt.sample_a) | set(df_tt.sample_b))
    n_samples = sorted(set(df_nn.sample_a) | set(df_nn.sample_b))
    t_idx = {s: i for i, s in enumerate(t_samples)}
    n_idx = {s: i for i, s in enumerate(n_samples)}
    ia_t = df_tt.sample_a.map(t_idx).to_numpy()
    ib_t = df_tt.sample_b.map(t_idx).to_numpy()
    ia_n = df_nn.sample_a.map(n_idx).to_numpy()
    ib_n = df_nn.sample_b.map(n_idx).to_numpy()
    v_t = df_tt.omega.to_numpy(); v_n = df_nn.omega.to_numpy()
    kt_t = df_tt.kn.to_numpy(); kt_n = df_nn.kn.to_numpy()
    ratios, knratios = [], []
    nT, nN = len(t_samples), len(n_samples)
    for _ in range(B):
        wt = rng.multinomial(nT, np.ones(nT) / nT) / nT
        wn = rng.multinomial(nN, np.ones(nN) / nN) / nN
        ww_t = wt[ia_t] * wt[ib_t]; ww_n = wn[ia_n] * wn[ib_n]
        tt_m = np.sum(v_t * ww_t) / np.sum(ww_t)
        nn_m = np.sum(v_n * ww_n) / np.sum(ww_n)
        ratios.append(nn_m / tt_m)
        ktt = np.sum(kt_t * ww_t) / np.sum(ww_t)
        knn = np.sum(kt_n * ww_n) / np.sum(ww_n)
        knratios.append(ktt / knn)
    return np.percentile(ratios, [2.5, 97.5]), np.percentile(knratios, [2.5, 97.5])

sens_rows = []
lihc = pairs[pairs.cancer == "TCGA-LIHC"].copy()
kept = lihc[~lihc.sample_a.map(is_cc) & ~lihc.sample_b.map(is_cc)].copy()
tt_x = kept[kept.pair_type == "TT"]
nn_x = kept[kept.pair_type == "NN"]
tt_f = lihc[lihc.pair_type == "TT"]
nn_f = lihc[lihc.pair_type == "NN"]
ci_om, ci_kn = boot_ratio(tt_x, nn_x)
r_full = nn_f.omega.mean() / tt_f.omega.mean()
r_ex = nn_x.omega.mean() / tt_x.omega.mean()
kn_ex = tt_x.kn.mean() / nn_x.kn.mean()
log(f"LIHC full: NN/TT={r_full:.3f} | ex-CC: NN/TT={r_ex:.3f} "
    f"[{ci_om[0]:.3f},{ci_om[1]:.3f}], TT/NN k_n={kn_ex:.3f} "
    f"[{ci_kn[0]:.3f},{ci_kn[1]:.3f}] (tumours {len(set(tt_f.sample_a)|set(tt_f.sample_b))}"
    f" -> {len(set(tt_x.sample_a)|set(tt_x.sample_b))})")
sens_rows.append({"analysis": "ex_cc_nntt", "cancer": "TCGA-LIHC",
                  "n_tumours_full": len(set(tt_f.sample_a) | set(tt_f.sample_b)),
                  "n_tumours_excc": len(set(tt_x.sample_a) | set(tt_x.sample_b)),
                  "stat": round(r_ex, 3), "ci95": f"[{ci_om[0]:.3f},{ci_om[1]:.3f}]",
                  "full_stat": round(r_full, 3)})
sens_rows.append({"analysis": "ex_cc_kn_ratio", "cancer": "TCGA-LIHC",
                  "n_tumours_full": None,
                  "n_tumours_excc": None,
                  "stat": round(kn_ex, 3), "ci95": f"[{ci_kn[0]:.3f},{ci_kn[1]:.3f}]",
                  "full_stat": 1.35})

# =====================================================================
# 3. Ex-CC high-purity (low-admixture) half sensitivity, all 5 cancers
# =====================================================================
log("")
log("=" * 70)
log("3. Ex-CC high-purity half sensitivity (all cancers)")
log("=" * 70)
adm_t = admix[admix.type == "Tumor"][["sample", "admix"]]
for c in CANCERS:
    tt = pairs[(pairs.cancer == c) & (pairs.pair_type == "TT")]
    nn = pairs[(pairs.cancer == c) & (pairs.pair_type == "NN")]
    if not len(tt):
        continue
    # ex-CC tumours
    tt_xc = tt[~tt.sample_a.map(is_cc) & ~tt.sample_b.map(is_cc)]
    adm_c = adm_t[adm_t["sample"].isin(set(tt_xc.sample_a) | set(tt_xc.sample_b))]
    thr = adm_c["admix"].median()
    keep = set(adm_c.loc[adm_c["admix"] <= thr, "sample"])
    tt_hi = tt_xc[tt_xc.sample_a.isin(keep) & tt_xc.sample_b.isin(keep)]
    if len(tt_hi) < 30:
        log(f"{c}: too few ex-CC high-purity TT pairs ({len(tt_hi)}), skipped")
        continue
    # full-data published half analysis (all tumours incl. CC)
    adm_all = adm_t[adm_t["sample"].isin(set(tt.sample_a) | set(tt.sample_b))]
    thr_all = adm_all["admix"].median()
    keep_all = set(adm_all.loc[adm_all["admix"] <= thr_all, "sample"])
    tt_hi_all = tt[tt.sample_a.isin(keep_all) & tt.sample_b.isin(keep_all)]
    ratio_all = nn.omega.mean() / tt_hi_all.omega.mean()
    ratio_x = nn.omega.mean() / tt_hi.omega.mean()
    ci_x, _ = boot_ratio(tt_hi, nn)
    ci_lo_x, ci_hi_x = float(ci_x[0]), float(ci_x[1])
    log(f"{c}: high-purity half NN/TT all={ratio_all:.3f} -> ex-CC={ratio_x:.3f} "
        f"[{ci_lo_x:.3f},{ci_hi_x:.3f}] (pairs {len(tt_hi_all)} -> {len(tt_hi)})")
    sens_rows.append({"analysis": "ex_cc_highpurity_half", "cancer": c,
                      "n_tumours_full": len(keep_all),
                      "n_tumours_excc": len(keep),
                      "stat": round(float(ratio_x), 3),
                      "ci95": f"[{ci_lo_x:.3f},{ci_hi_x:.3f}]",
                      "full_stat": round(float(ratio_all), 3)})

# =====================================================================
# 4. CC presence ledger in other LIHC analyses
# =====================================================================
log("")
log("=" * 70)
log("4. CC presence ledger (other LIHC downstream analyses)")
log("=" * 70)
# composition regression (Note 8) draws its TT/NN pairs from the v44 pair
# table (post-CC-fix): count CC-touching LIHC TT pairs there directly.
lihc_tt = pairs[(pairs.cancer == "TCGA-LIHC") & (pairs.pair_type == "TT")]
tt_comp_cc = int((lihc_tt.sample_a.map(is_cc) |
                  lihc_tt.sample_b.map(is_cc)).sum())
log(f"composition-regression LIHC TT pairs touching a CC sample: "
    f"{tt_comp_cc} of {len(lihc_tt)}")

clin_patients = 0
cc_in_clin = 0
try:
    clin = json.load(open(CLIN))
    ids = sorted({str(x["patientId"]) for x in clin if "patientId" in x})
    clin_patients = len(ids)
    cc_in_clin = sum(1 for i in ids if i.startswith("TCGA-CC"))
except Exception as e:  # noqa: BLE001
    log(f"clinical json read failed: {e}")

cc_tumours = sorted(set(pairs[(pairs.cancer == "TCGA-LIHC")].sample_a) |
                    set(pairs[(pairs.cancer == "TCGA-LIHC")].sample_b))
cc_tumours = [s for s in cc_tumours if is_cc(s)]
log(f"LIHC clinical JSON patients: {clin_patients}, of which TCGA-CC: {cc_in_clin}")
log("Edmondson/severity strata and Cox cohort draw from the clinical JSON; "
    "CC patients present there enter those analyses (counts above).")
sens_rows.append({"analysis": "cc_ledger", "cancer": "TCGA-LIHC",
                  "n_tumours_full": clin_patients, "n_tumours_excc": cc_in_clin,
                  "stat": len(cc_tumours), "ci95": "", "full_stat": None})

sens_df = pd.DataFrame(sens_rows)
sens_df.to_csv(OUT_SENS, index=False)
OUT_LOG.write_text("\n".join(lines), encoding="utf-8")
log("")
log("saved: " + str(OUT_SENS) + ", " + str(OUT_LOG))
print("DONE")
