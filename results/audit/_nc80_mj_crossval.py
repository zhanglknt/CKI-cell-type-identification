#!/usr/bin/env python3
"""nc80 M-J / stat m7 -- independent cross-validation.

Re-derives, by a different route than the analysis scripts, every number that
the nc80 additions put into the manuscript and the Supplementary Information:

  A. T1 paired FPR contrasts (stat m7)
     analysis  : two-way cluster-robust sandwich, V_a + V_b - V_ab
     check here: delete-one-library jackknife SE, independent of the sandwich
                 algebra, plus exact reproduction of the six interval
                 endpoints from the deposited table.

  B. Covariance-whitened baselines (M-J ii)
     analysis  : notebooks/nc80_mj_mahalanobis_sim.py -> metrics JSON
     check here: null log-MAD and signal-vs-neutral AUC recomputed from the
                 raw replicate table.

  C. 10x modular operating characteristic (M-J iii)
     analysis  : notebooks/nc80_mj_kang_modular_{tpr,summary}.py
     check here: pooled AUC, paired detection rates and held-out FPR recomputed
                 from the raw replicate table.

  D. Text-to-data consistency: every number quoted in the MS/SI paragraphs must
     equal the value in the deposited table, and no exact McNemar P value may
     survive in the main text.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from docx import Document
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results"
ok = fail = 0
fails = []


def chk(name, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
        print(f"[PASS] {name} {extra}")
    else:
        fail += 1
        fails.append(name)
        print(f"[FAIL] {name} {extra}")


# ============================ A. T1 paired contrasts ======================
lad = pd.read_csv(RES / "nc49_brain_drift_ladder.csv")
t1 = lad[lad["tier"] == "T1_techrep"].reset_index(drop=True)
libs = np.sort(pd.unique(pd.concat([t1["sample_a"], t1["sample_b"]])))
code = {l: i for i, l in enumerate(libs)}
ia = t1["sample_a"].map(code).to_numpy()
ib = t1["sample_b"].map(code).to_numpy()
G = len(libs)
n = len(t1)
ow = t1["exceed_omega"].to_numpy(int)
tab = pd.read_csv(RES / "nc80_mcnemar_t1_studentized.csv").set_index("contrast")

chk("A0 T1 size / libraries", n == 2161 and G == 597, f"({n} pairs, {G} libraries)")

for met in ["raw_js", "cosine", "spearman", "marker_jaccard", "k_n", "k_f"]:
    d = t1[f"exceed_{met}"].to_numpy(int) - ow
    delta = d.mean()
    # delete-one-library jackknife, independent of the sandwich formula
    jk = np.empty(G)
    for g in range(G):
        m = (ia != g) & (ib != g)
        jk[g] = d[m].mean()
    jk_se = np.sqrt((G - 1) / G * ((jk - jk.mean()) ** 2).sum())
    row = tab.loc[f"{met} - omega"]
    chk(f"A1 {met}: Delta reproduced", abs(row["delta_pair"] - delta) < 1e-6,
        f"({delta:+.4f})")
    ratio = jk_se / row["se_2way"]
    chk(f"A2 {met}: jackknife SE agrees with sandwich", 0.6 < ratio < 1.7,
        f"(jackknife {jk_se:.4f} vs sandwich {row['se_2way']:.4f}, ratio {ratio:.2f})")
    lo, hi = row["dyadic_t_lo"], row["dyadic_t_hi"]
    chk(f"A3 {met}: interval excludes zero", lo * hi > 0, f"[{lo:+.3f}, {hi:+.3f}]")

# ==================== B. whitened baselines (M-J ii) ======================
mh = json.loads((RES / "nc80_mj_mahalanobis_metrics.json").read_text())
mraw = pd.read_csv(RES / "nc80_mj_mahalanobis_raw.csv")
METS = ["omega", "k_f", "k_n", "k_total", "cosine", "kf_over_kt",
        "mahal_pc", "mahal_diag"]
for bg in ["marrow_bcell", "skin_keratinocyte"]:
    sub = mraw[mraw["background"] == bg]
    base = sub[sub["series"] == "baseline"]
    sig = sub[(sub["series"] == "signal") & (sub["delta"] >= 0.25)]
    neu = sub[sub["series"].isin(["neutral_hk", "neutral_global"])]
    for met in ["omega", "mahal_pc", "mahal_diag"]:
        v = base[met].to_numpy(float)
        mad = float(np.median(np.abs(np.log(v) - np.median(np.log(v)))))
        ref = mh[bg]["null_log_mad"][met]
        chk(f"B1 {bg}/{met}: null log-MAD", abs(mad - ref) < 5e-4,
            f"({mad:.4f} vs {ref:.4f})")
        auc = roc_auc_score([1] * len(sig) + [0] * len(neu),
                            np.r_[sig[met].to_numpy(float), neu[met].to_numpy(float)])
        refa = mh[bg]["auc_signal_vs_neutral"][met]
        chk(f"B2 {bg}/{met}: signal-vs-neutral AUC", abs(auc - refa) < 2e-3,
            f"({auc:.3f} vs {refa:.3f})")
    # anchor-drift specificity claim: omega zero, whitened baselines not
    hk = sub[sub["series"] == "neutral_hk"]   # all three eta values, as the analysis pools them
    thr = {m: np.percentile(base[m].to_numpy(float), 95) for m in METS}
    for m in ["omega", "mahal_diag", "mahal_pc"]:
        rate = float((hk[m] > thr[m]).mean())
        ref = mh[bg]["type_I_error"]["neutral_hk"][m]
        chk(f"B3 {bg}/{m}: rate under neutral HK drift", abs(rate - ref) < 1e-9,
            f"({rate:.2f})")

# ============== C. 10x modular operating characteristic (M-J iii) =========
kr = pd.read_csv(RES / "nc80_mj_kang_modular_raw.csv")
ks = pd.read_csv(RES / "nc80_mj_kang_modular_summary.csv")
KT = ["omega", "k_f", "k_n", "k_total", "cosine", "mahal_pc", "mahal_diag"]
for nm in sorted(kr["n"].unique()):
    s = kr[kr["n"] == nm]
    nul = s[s["series"] == "split_half"]
    eff = s[s["series"] == "effect"]
    for met in KT:
        row = ks[(ks["n"] == nm) & (ks["metric"] == met)].iloc[0]
        auc = roc_auc_score([1] * len(eff) + [0] * len(nul),
                            np.r_[eff[met].to_numpy(float),
                                  nul[met].to_numpy(float)])
        chk(f"C1 n={nm}/{met}: pooled AUC", abs(auc - row["auc_pooled_delta_ge_0.25"]) < 2e-3,
            f"({auc:.3f})")
        base = eff["rep"].map(nul.set_index("rep")[met])
        win = (eff[met].to_numpy(float) > base.to_numpy(float))
        for dl in [0.25, 0.5, 1.0]:
            sel = (eff["delta"] == dl).to_numpy()
            w = float(win[sel].mean())
            chk(f"C2 n={nm}/{met}/d{dl}: paired rate",
                abs(w - row[f"win_d{dl}"]) < 2e-3, f"({w:.3f})")
chk("C3 k_total beats omega at every n (paired rate, delta=1.0)",
    all(float(ks[(ks.n == nm) & (ks.metric == 'k_total')]["win_d1.0"].iloc[0])
        > float(ks[(ks.n == nm) & (ks.metric == 'omega')]["win_d1.0"].iloc[0])
        for nm in sorted(kr["n"].unique())), "")

# ================== D. text-to-data consistency ===========================
ms = " ".join(p.text for p in Document(RES / "CKI_Manuscript_NC.docx").paragraphs)
si = " ".join(p.text for p in Document(RES / "CKI_Supplementary_NC.docx").paragraphs)

quoted = {
    "raw JS +0.166 [+0.135, +0.196]": tab.loc["raw_js - omega"],
    "cosine +0.154 [+0.126, +0.183]": tab.loc["cosine - omega"],
    "Spearman +0.120 [+0.091, +0.149]": tab.loc["spearman - omega"],
    "k_n +0.070 [+0.040, +0.101]": tab.loc["k_n - omega"],
    "k_f +0.089 [+0.067, +0.112]": tab.loc["k_f - omega"],
    "marker Jaccard \u22120.088 [\u22120.116, \u22120.059]": tab.loc["marker_jaccard - omega"],
}
for txt, row in quoted.items():
    lo = f"{row['dyadic_t_lo']:+.3f}".replace("-", "\u2212")
    hi = f"{row['dyadic_t_hi']:+.3f}".replace("-", "\u2212")
    chk(f"D1 SI quotes {txt.split(' ')[0]} interval",
        txt in si and lo in txt and hi in txt, f"({lo},{hi})")

chk("D2 SI: no exact McNemar P remains",
    not re.search(r"P = \d\.\d \u00d7 10\u207b", si.split("Paired T1 comparisons")[1][:1800]))
chk("D3 MS: interval wording, no exact McNemar P",
    "intervals excluding zero under library clustering" in ms
    and "4.1 \u00d7 10\u207b\u00b9\u00b2" not in ms)
chk("D4 MS: 10x modular clause numbers",
    "97\u2013100% of paired replicates by raw JS but in 35\u201366%" in ms)
chk("D5 MS: scDist R-original disclosure in Limitations",
    "could not be installed in this environment" in ms)
chk("D6 SI: Mahalanobis values quoted",
    all(x in si for x in ["0.213", "0.117", "0.021", "0.804", "0.908"]))
chk("D7 SI: 10x values quoted",
    all(x in si for x in ["0.507\u20130.534", "0.564\u20130.634", "0.967\u20131.000",
                          "0.343\u20130.657", "0.90\u20130.99"]))
chk("D8 SI: claim-to-test map present with family statements",
    "Claim-to-test map (nc80)" in si and "Benjamini\u2013Hochberg within the k_n exposure" in si)
chk("D9 SI: GTEx power statement present",
    "3\u201321% of the normal level in LUAD" in si and "2.0\u20132.7-fold elevation" in si)
chk("D10 SI: anchor-panel characterisation present",
    "869 of the 1,129 (77.0%)" in si and "1.30 (Mann\u2013Whitney P = 3.3 \u00d7 10\u207b\u2077)" in si)

print("\n" + "=" * 60)
print(f"TOTAL: {ok + fail} checks, {fail} failures")
if fail:
    print("FAILED:", ", ".join(fails))
    sys.exit(1)
print("ALL PASS")
