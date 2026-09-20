# -*- coding: utf-8 -*-
"""从两个 CSV 重算稿件将引用的全部数字（禁止凭记忆）。"""
import numpy as np
import pandas as pd

R = "C:/Users/KnightZ/Desktop/细胞受选择/results/"
kang = pd.read_csv(R + "nc49_pilot_kang_techrep.csv")
brain = pd.read_csv(R + "nc49_brain_drift_ladder.csv")
out = []
mets = ["k_n", "k_f", "omega", "raw_js", "cosine", "spearman", "marker_jaccard"]

out.append("== KANG PILOT (n=%d) ==" % len(kang))
for m in ["k_n", "k_f", "omega", "raw_js", "cosine"]:
    cv = kang[f"cal_{m}"]
    out.append(f"{m:<8} obs_med={kang[m].median():.4g} null_med={kang[f'null_med_{m}'].median():.4g} "
               f"cal_med={cv.median():.3f} cal_q25={cv.quantile(.25):.3f} cal_q75={cv.quantile(.75):.3f} "
               f"FPR={kang[f'exceed_{m}'].mean():.4f} ({int(kang[f'exceed_{m}'].sum())}/{len(kang)})")

out.append("\n== BRAIN LADDER ==")
for tier in ["T1_techrep", "T2_cross_donor", "T3_cross_roi"]:
    sub = brain[brain.tier == tier]
    out.append(f"--- {tier} (n={len(sub)}) ---")
    for m in mets:
        cv = sub[f"cal_{m}"]
        out.append(f"{m:<16} obs_med={sub[m].median():.4g} cal_med={cv.median():.3f} "
                   f"[{cv.quantile(.25):.3f},{cv.quantile(.75):.3f}] "
                   f"FPR={sub[f'exceed_{m}'].mean():.4f} ({int(sub[f'exceed_{m}'].sum())}/{len(sub)})")

# T1: omega FPR lowest in how many CTs vs raw_js/cosine/spearman
t1 = brain[brain.tier == "T1_techrep"]
g = t1.groupby("cell_type")
cmp_tab = pd.DataFrame({
    "n": g.size(),
    "FPR_omega": g["exceed_omega"].mean(),
    "FPR_raw_js": g["exceed_raw_js"].mean(),
    "FPR_cosine": g["exceed_cosine"].mean(),
    "FPR_spearman": g["exceed_spearman"].mean(),
    "cal_omega_med": g["cal_omega"].median(),
})
cmp_tab["omega_lowest_vs_rawjs"] = cmp_tab.FPR_omega < cmp_tab.FPR_raw_js
cmp_tab["omega_lowest_vs_cosine"] = cmp_tab.FPR_omega < cmp_tab.FPR_cosine
cmp_tab["omega_lowest_vs_spearman"] = cmp_tab.FPR_omega < cmp_tab.FPR_spearman
out.append("\n== T1 per-CT FPR comparison ==")
out.append(cmp_tab.round(4).to_string())
out.append(f"omega < raw_js in {cmp_tab.omega_lowest_vs_rawjs.sum()}/{len(cmp_tab)} CTs")
out.append(f"omega < cosine in {cmp_tab.omega_lowest_vs_cosine.sum()}/{len(cmp_tab)} CTs")
out.append(f"omega < spearman in {cmp_tab.omega_lowest_vs_spearman.sum()}/{len(cmp_tab)} CTs")
ratios = []
for ct, r in cmp_tab.iterrows():
    ratios.append(r.FPR_raw_js / r.FPR_omega if r.FPR_omega > 0 else np.nan)
out.append(f"raw_js/omega FPR ratio range: {np.nanmin(ratios):.2f}-{np.nanmax(ratios):.2f}")

# n-dependence
t1n = t1.assign(n_min=t1[["n_cells_a", "n_cells_b"]].min(axis=1))
bins = pd.cut(t1n["n_min"], [20, 30, 500, 5000])
nb = t1n.groupby(bins, observed=True).agg(
    n=("exceed_omega", "size"),
    FPR_omega=("exceed_omega", "mean"),
    FPR_raw_js=("exceed_raw_js", "mean"))
out.append("\n== T1 FPR by n_min bin ==")
out.append(nb.round(4).to_string())
# finer for the text claim 13.8@<=30 / 47.8@>500
lo = t1n[t1n.n_min <= 30]
hi = t1n[t1n.n_min > 500]
out.append(f"n_min<=30: n={len(lo)} FPR_omega={lo['exceed_omega'].mean():.4f} FPR_raw={lo['exceed_raw_js'].mean():.4f}")
out.append(f"n_min>500: n={len(hi)} FPR_omega={hi['exceed_omega'].mean():.4f} FPR_raw={hi['exceed_raw_js'].mean():.4f}")

# Choroid/Bergmann cal
for ct in ["Choroid plexus", "Bergmann glia"]:
    s = t1[t1.cell_type == ct]
    out.append(f"{ct}: n={len(s)} cal_omega_med={s['cal_omega'].median():.3f} "
               f"FPR_omega={s['exceed_omega'].mean():.3f}")

# Wilson CI for headline FPRs
def wilson(p, n, z=1.96):
    den = 1 + z**2 / n
    ctr = (p + z**2 / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return ctr - half, ctr + half

out.append("\n== Wilson 95% CI for headline FPRs ==")
for label, p, n in [
    ("Kang omega 0", 0.0, len(kang)),
    ("Kang raw_js", kang["exceed_raw_js"].mean(), len(kang)),
    ("Kang cosine", kang["exceed_cosine"].mean(), len(kang)),
    ("Brain T1 omega", t1["exceed_omega"].mean(), len(t1)),
    ("Brain T1 raw_js", t1["exceed_raw_js"].mean(), len(t1)),
    ("Brain T1 cosine", t1["exceed_cosine"].mean(), len(t1)),
    ("Brain T1 spearman", t1["exceed_spearman"].mean(), len(t1)),
    ("Brain T1 marker_jaccard", t1["exceed_marker_jaccard"].mean(), len(t1)),
]:
    lo_, hi_ = wilson(p, n)
    out.append(f"{label:<24} p={p:.4f} CI=[{lo_:.3f},{hi_:.3f}] n={n}")

open(R + "audit/_nc49_ms_numbers.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
