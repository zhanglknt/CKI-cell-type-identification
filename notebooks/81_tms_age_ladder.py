"""
CKI Tabula Muris Senis Ageing Ladder (C task)
==============================================
Tests whether CKI omega tracks chronological ageing in real tissue:
per tissue x cell-type x age pseudobulks, omega between age points,
"which cell types age fastest" ranking.

Data: data/tms/TMS_Smart-seq2_All.h5ad (110,824 cells, 22 tissues,
119 cell types; ages 3m / 18m / 21m / 24m; 21m nearly all mammary).

Pipeline (identical to 08c observed path, mouse HK from HRT
Human_Mouse_Common 'Mouse' column):
  HK + top-5000 non-HK HVG by mean expression;
  pseudobulk = mean -> norm 1e4 -> log1p;
  kn = JS on HK; kf = JS on top-200 |diff| non-HK genes (per pair);
  omega = kf / kn.

Outputs:
  results/tms_age_ladder.csv   (tissue x cell_type x age pair)
  results/tms_age_report.md
"""

import sys, os, time, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
_real_print = print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _real_print(*args, **kwargs)

import numpy as np
import pandas as pd
import h5py
from scipy.sparse import csr_matrix
from cki.core import js_divergence

# Extraction function (verbatim from 77, isolated namespace)
SRC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "77_brain_hallmark_program_omega.py"),
           encoding="utf-8").read()
_NS = {"__file__": os.path.abspath(
           os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "77_brain_hallmark_program_omega.py")),
       "__name__": "not_main"}
exec(SRC.split("# === Config (identical to 08c) ===")[0], _NS)
extract_csr_from_backed = _NS["extract_csr_from_backed"]

# === Config ===
RANDOM_SEED = 42
MIN_CELLS_PER_GROUP = 20
N_TOP_KF = 200
N_HVG = 5000

TMS_PATH = DATA_DIR / "tms" / "TMS_Smart-seq2_All.h5ad"
OUT_CSV = Path("results/tms_age_ladder.csv")
OUT_MD = Path("results/tms_age_report.md")

hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
hk_mouse = set(hk_df["Mouse"].dropna().astype(str))
print(f"HRT Atlas: {len(hk_mouse)} mouse HK genes")


def read_cat(obj, name):
    g = obj[name]
    if isinstance(g, h5py.Dataset):
        return np.array([x.decode() if isinstance(x, bytes) else str(x)
                         for x in g[:]], dtype=object)
    cats = [x.decode() if isinstance(x, bytes) else str(x)
            for x in g["categories"][:]]
    return np.array(cats, dtype=object)[g["codes"][:]]


def age_months(a):
    return float(a.rstrip("m")) if a.endswith("m") else np.nan


with h5py.File(TMS_PATH, "r") as f:
    X = f["X"]
    indptr = X["indptr"][:]
    data = X["data"]
    indices = X["indices"]
    n_cells = len(indptr) - 1
    var_gene = read_cat(f["var"], "feature_name").astype(str)
    n_genes = len(var_gene)
    tissue = read_cat(f["obs"], "tissue").astype(str)
    ctype = read_cat(f["obs"], "cell_type").astype(str)
    age = read_cat(f["obs"], "age").astype(str)
    print(f"cells={n_cells} genes={n_genes} "
          f"tissues={len(set(tissue))} cell_types={len(set(ctype))}")

    # HK mapping (mouse symbols)
    hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                                 if s in hk_mouse}), dtype=int)
    print(f"HK genes matched: {len(hk_global)}")

    # global means for HVG
    gene_sums = np.zeros(n_genes, dtype=np.float64)
    np.add.at(gene_sums, indices[:], data[:].astype(np.float64))
    means = gene_sums / n_cells
    m = np.ones(n_genes, bool)
    m[hk_global] = False
    nm = means.copy()
    nm[~m] = -np.inf
    hvg = np.argsort(nm)[-N_HVG:][::-1]
    keep = np.sort(np.union1d(hk_global, hvg))
    is_hk = np.isin(keep, hk_global)
    hk_r = np.where(is_hk)[0]
    nh_r = np.where(~is_hk)[0]
    print(f"reduced: {len(keep)} (HK {len(hk_r)} + non-HK {len(nh_r)})")

    # groups
    dfm = pd.DataFrame({"tissue": tissue, "ct": ctype, "age": age})
    grp = dfm.groupby(["tissue", "ct", "age"]).size().reset_index(name="n")
    grp = grp[grp.n >= MIN_CELLS_PER_GROUP]
    grp["age_m"] = grp.age.map(age_months)

rows = []
done = 0
for (t, c), g in grp.groupby(["tissue", "ct"]):
    ages = sorted(g.age.tolist(), key=age_months)
    if len(ages) < 2:
        continue
    with h5py.File(TMS_PATH, "r") as f:
        PB = {}
        for a in ages:
            mask = (tissue == t) & (ctype == c) & (age == a)
            gidx = np.where(mask)[0]
            if len(gidx) < MIN_CELLS_PER_GROUP:
                continue
            Xs = extract_csr_from_backed(str(TMS_PATH), gidx, keep, n_genes)
            raw = np.array(Xs.mean(axis=0)).flatten()
            tot = raw.sum()
            PB[a] = np.log1p(raw / tot * 1e4) if tot > 0 else raw
            del Xs
            gc.collect()
    ages_ok = [a for a in ages if a in PB]
    for i in range(len(ages_ok)):
        for j in range(i + 1, len(ages_ok)):
            pi, pj = PB[ages_ok[i]], PB[ages_ok[j]]
            kn = js_divergence(pi[hk_r], pj[hk_r])
            ad = np.abs(pi - pj)[nh_r]
            top_n = min(N_TOP_KF, len(ad))
            tl = np.argpartition(ad, -top_n)[-top_n:]
            tg = nh_r[tl]
            kf = js_divergence(pi[tg], pj[tg])
            rows.append({
                "tissue": t, "cell_type": c,
                "age_a": ages_ok[i], "age_b": ages_ok[j],
                "age_gap_months": age_months(ages_ok[j]) - age_months(ages_ok[i]),
                "n_cells_a": int(g[(g.age == ages_ok[i])].n.iloc[0]),
                "n_cells_b": int(g[(g.age == ages_ok[j])].n.iloc[0]),
                "kn": kn, "kf": kf,
                "omega": kf / kn if kn > 0 else np.inf,
            })
    done += 1
    if done % 10 == 0:
        print(f"  processed {done} tissue x cell-type groups...")

df = pd.DataFrame(rows)
df.to_csv(OUT_CSV, index=False)
print(f"Saved {OUT_CSV}: {len(df)} age pairs")

# === Summary/report ===
main = df[df.age_gap_months >= 15]  # 3->18, 3->24, 18->24
ladder = df[(df.age_a == "3m") & (df.age_b == "24m")].copy()
adj = df[((df.age_a == "3m") & (df.age_b == "18m")) |
         ((df.age_a == "18m") & (df.age_b == "24m"))].copy()

lines = ["# TMS Ageing Ladder (CKI omega)", "",
         f"- Groups: tissue x cell_type x age pseudobulks "
         f"(min {MIN_CELLS_PER_GROUP} cells per age)",
         f"- Age pairs: {len(df)}; 3m->24m pairs: {len(ladder)}", "",
         "## Gap effect: far vs adjacent age pairs (paired check)",
         ""]
from scipy.stats import wilcoxon
key = ["tissue", "cell_type"]
mg = ladder.merge(adj.groupby(key)["omega"].mean().rename("omega_adj_mean"),
                  on=key, how="inner")
if len(mg) >= 10:
    stat, p = wilcoxon(mg.omega, mg.omega_adj_mean)
    lines.append(f"- mean omega(3m->24m) = {mg.omega.mean():.2f}; "
                 f"mean omega(adjacent) = {mg.omega_adj_mean.mean():.2f}")
    lines.append(f"- Wilcoxon paired n={len(mg)}: W={stat:.0f}, p={p:.3g}")
lines += ["", "## Top 25 fastest-ageing cell types (omega 3m->24m)", "",
          "| tissue | cell_type | n_3m | n_24m | omega | kn | kf |",
          "|---|---|---|---|---|---|---|"]
for _, r in ladder.nlargest(25, "omega").iterrows():
    lines.append(f"| {r.tissue} | {r.cell_type} | {r.n_cells_a} | "
                 f"{r.n_cells_b} | {r.omega:.2f} | {r.kn:.2e} | {r.kf:.2e} |")
lines += ["", "## Slowest 10", "",
          "| tissue | cell_type | n_3m | n_24m | omega |",
          "|---|---|---|---|---|"]
for _, r in ladder.nsmallest(10, "omega").iterrows():
    lines.append(f"| {r.tissue} | {r.cell_type} | {r.n_cells_a} | "
                 f"{r.n_cells_b} | {r.omega:.2f} |")
OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(f"Saved {OUT_MD}")
print("DONE")
