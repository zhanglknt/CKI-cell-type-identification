# -*- coding: utf-8 -*-
"""
TCGA composition check, v44 linear-normalization edition
=========================================================

Line-for-line mirror of 74_tcga_composition_v2.py (four-panel marker set
including the myeloid panel, per-cancer z-scored panel scores, log(k_n)
OLS attenuation, sample-level cluster bootstrap B=200 seed 42, Spearman
rho of k_n vs four-panel |Delta composition|), with ONE change: the pair
table is the v44 linear-normalization recompute
(results/tcga_linear_norm_v44_all_pairs.csv, produced by
notebooks/85_tcga_linear_norm_v44.py) instead of the softmax(log2)
pipeline pairs (results/tcga_composition_pairs.csv).

The composition panel scores are identical in construction to 73/74
(same single-pass extraction, same mean TPM>=0.5 per-cancer filter, same
log2(TPM+1) -> z-score rule); they do not depend on the CKI probability
mapping. All four panel deltas (immune/myeloid/stromal/epithelial) are
recomputed here from the panel scores (73 precomputed three of them in
its pair table; the v44 pair table carries only k_n/k_f/omega).

Outputs (NEW files, _v44 suffix):
  results/tcga_composition_v44.csv
  results/tcga_composition_v44.txt
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import gzip, time, warnings
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

PAIRS_FILE = RESULTS_DIR / "tcga_linear_norm_v44_all_pairs.csv"

TARGET_PROJECTS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

PANELS = {
    "immune":   ["CD3D", "CD3E", "CD8A", "GZMB", "NKG7", "MS4A1", "CD79A"],
    "myeloid":  ["CD68", "CD163", "LST1", "FCGR3A", "C1QA"],
    "stromal":  ["COL1A1", "COL1A2", "DCN", "LUM", "FAP", "VIM"],
    "epithelial": ["EPCAM", "KRT8", "KRT18", "KRT19"],
}

TSS_TO_PROJECT = {
    "A1": "BRCA", "A2": "BRCA", "A7": "BRCA", "A8": "BRCA", "AN": "BRCA",
    "AO": "BRCA", "AQ": "BRCA", "AR": "BRCA", "B6": "BRCA", "BH": "BRCA",
    "C8": "BRCA", "D8": "BRCA", "E2": "BRCA", "EW": "BRCA", "GI": "BRCA",
    "WT": "BRCA", "XX": "BRCA", "E9": "BRCA", "GM": "BRCA", "HN": "BRCA",
    "JL": "BRCA", "LD": "BRCA", "LL": "BRCA", "MS": "BRCA", "OL": "BRCA",
    "PE": "BRCA", "PL": "BRCA", "S3": "BRCA", "UL": "BRCA", "V7": "BRCA",
    "W8": "BRCA", "WV": "BRCA",
    "05": "LUAD", "35": "LUAD", "38": "LUAD", "44": "LUAD", "49": "LUAD",
    "50": "LUAD", "55": "LUAD", "64": "LUAD", "67": "LUAD", "73": "LUAD",
    "75": "LUAD", "78": "LUAD", "86": "LUAD", "91": "LUAD", "93": "LUAD",
    "97": "LUAD", "J2": "LUAD", "L3": "LUAD", "L4": "LUAD", "M1": "LUAD",
    "MP": "LUAD", "MT": "LUAD", "N1": "LUAD", "N6": "LUAD", "O1": "LUAD",
    "S2": "LUAD", "TR": "LUAD", "TV": "LUAD", "TQ": "LUAD", "NJ": "LUAD",
    "KN": "LUAD", "LF": "LUAD",
    "18": "LUSC", "21": "LUSC", "22": "LUSC", "33": "LUSC", "34": "LUSC",
    "37": "LUSC", "39": "LUSC", "43": "LUSC", "51": "LUSC", "52": "LUSC",
    "56": "LUSC", "60": "LUSC", "63": "LUSC", "66": "LUSC", "68": "LUSC",
    "70": "LUSC", "77": "LUSC", "85": "LUSC", "90": "LUSC", "92": "LUSC",
    "94": "LUSC", "96": "LUSC", "98": "LUSC", "L5": "LUSC", "N2": "LUSC",
    "NK": "LUSC", "Q1": "LUSC", "IE": "LUSC", "IF": "LUSC", "IG": "LUSC",
    "BC": "LIHC", "DD": "LIHC", "ED": "LIHC", "EP": "LIHC", "ES": "LIHC",
    "FV": "LIHC", "FY": "LIHC", "G3": "LIHC", "GJ": "LIHC", "HP": "LIHC",
    "HU": "LIHC", "K7": "LIHC", "KR": "LIHC", "LG": "LIHC", "NI": "LIHC",
    "O8": "LIHC", "PD": "LIHC", "QN": "LIHC", "RC": "LIHC", "RG": "LIHC",
    "T6": "LIHC", "UB": "LIHC", "WQ": "LIHC", "XR": "LIHC", "YA": "LIHC",
    "ZP": "LIHC", "ZS": "LIHC", "MI": "LIHC", "F5": "LIHC",
    "A3": "KIRC", "AK": "KIRC", "AL": "KIRC", "AY": "KIRC", "B0": "KIRC",
    "B1": "KIRC", "B2": "KIRC", "B3": "KIRC", "B4": "KIRC", "B8": "KIRC",
    "BP": "KIRC", "BW": "KIRC", "CJ": "KIRC", "CW": "KIRC", "CZ": "KIRC",
    "DV": "KIRC", "DX": "KIRC", "EU": "KIRC", "GK": "KIRC", "HE": "KIRC",
    "I6": "KIRC", "K6": "KIRC", "KL": "KIRC", "MM": "KIRC", "MW": "KIRC",
    "P4": "KIRC", "Q2": "KIRC", "UZ": "KIRC", "V5": "KIRC", "XM": "KIRC",
    "YE": "KIRC",
}

RANDOM_SEED = 42
N_BOOT = 200

def parse_tcga_barcode(barcode):
    parts = barcode.split("-")
    if len(parts) >= 4:
        tss = parts[1]
        project = TSS_TO_PROJECT.get(tss, None)
        if project is not None:
            project = "TCGA-" + project
        sample_code = parts[3][:2]
        return project, sample_code
    return None, None

t0 = time.time()

# ====================================================================
# 1. Load v44 pair table (TT + NN only, mirroring 73/74's pair set)
# ====================================================================
print("1. Loading v44 pair table...")
pdf = pd.read_csv(PAIRS_FILE)
pdf = pdf[pdf["pair_type"].isin(["TT", "NN"])].reset_index(drop=True)
n_kn_nonpos = int((pdf["kn"] <= 0).sum())
if n_kn_nonpos:
    print(f"  WARNING: {n_kn_nonpos} pairs with k_n <= 0 dropped for log(k_n) regression")
pdf = pdf[pdf["kn"] > 0].reset_index(drop=True)
print(f"  {len(pdf)} pairs "
      f"(NN={len(pdf[pdf.pair_type=='NN'])}, TT={len(pdf[pdf.pair_type=='TT'])})")

# ====================================================================
# 2. Single pass over TCGA matrix: raw TPM for panel genes (verbatim 74)
# ====================================================================
print("2. Scanning TCGA matrix for panel genes (single pass)...")
with gzip.open(TCGA_FILE, "rt") as fh:
    header_line = fh.readline().strip().split("\t")

target_cols = []
for k, sid in enumerate(header_line[1:], 1):
    proj, code = parse_tcga_barcode(sid)
    if proj in TARGET_PROJECTS and code in ("01", "11"):
        target_cols.append((sid, proj, code, k))
print(f"  target samples in matrix: {len(target_cols)}")

pm = pd.read_csv(PROBEMAP_FILE, sep="\t")
ens_to_symbol = {}
for _, row in pm.iterrows():
    ens_id = str(row.iloc[0]).split(".")[0]
    symbol = str(row.iloc[1])
    if ens_id and symbol and symbol != "nan":
        ens_to_symbol[ens_id] = symbol

panel_symbols = set()
for syms in PANELS.values():
    panel_symbols.update(syms)

raw = {}
n_panel_rows = 0
with gzip.open(TCGA_FILE, "rt") as fh:
    fh.readline()
    for line in fh:
        parts = line.rstrip("\n").split("\t")
        ens = parts[0].split(".")[0]
        sym = ens_to_symbol.get(ens)
        if sym is None or sym not in panel_symbols:
            continue
        vals = None
        for (sid, proj, code, ci) in target_cols:
            if ci < len(parts):
                try:
                    v = float(parts[ci])
                except (ValueError, IndexError):
                    v = 0.0
                if v != v or v < 0.0:
                    v = 0.0
            else:
                v = 0.0
            if vals is None:
                vals = []
            vals.append(v)
        n_panel_rows += 1
        for (sid, proj, code, ci), v in zip(target_cols, vals):
            key = (proj, code)
            raw.setdefault(key, {}).setdefault(sym, []).append((sid, v))
print(f"  panel gene rows captured: {n_panel_rows} ({time.time()-t0:.0f}s)")

# ====================================================================
# 3. Per-cancer z-scored panel scores (identical rule to 73/74)
# ====================================================================
print("3. Per-cancer panel scores...")
comp_scores = {}
gene_report = {}
for cancer in TARGET_PROJECTS:
    tumor_ids = [sid for (sid, proj, code, ci) in target_cols
                 if proj == cancer and code == "01"]
    normal_ids = [sid for (sid, proj, code, ci) in target_cols
                  if proj == cancer and code == "11"]
    all_ids = tumor_ids + normal_ids
    for pname, symbols in PANELS.items():
        gene_vals = {}
        for sym in symbols:
            if sym not in raw.get((cancer, "01"), {}) and \
               sym not in raw.get((cancer, "11"), {}):
                continue
            d_acc = {}
            for code_key in ("01", "11"):
                for (sid, v) in raw.get((cancer, code_key), {}).get(sym, []):
                    if sid in set(all_ids):
                        d_acc.setdefault(sid, []).append(v)
            d = {sid: float(np.mean(vs)) for sid, vs in d_acc.items()}
            if len(d) < len(all_ids):
                for sid in all_ids:
                    d.setdefault(sid, 0.0)
            m = np.mean([d[s] for s in all_ids])
            if m >= 0.5:
                gene_vals[sym] = d
        kept = sorted(gene_vals.keys())
        gene_report.setdefault(cancer, {})[pname] = kept
        if not kept:
            for sid in all_ids:
                comp_scores[(cancer, pname, sid)] = 0.0
            continue
        mu = np.array([np.mean([np.log2(gene_vals[g][s] + 1) for g in kept])
                       for s in all_ids])
        sd = mu.std(ddof=0)
        for sid, v in zip(all_ids, mu):
            comp_scores[(cancer, pname, sid)] = (v - mu.mean()) / sd if sd > 0 else 0.0
    print(f"  {cancer}: " + ", ".join(
        f"{p}({len(gene_report[cancer][p])})" for p in PANELS))

# ====================================================================
# 4. Attach all four panel deltas to the v44 pair table
# ====================================================================
def dz(cancer, pname, sid):
    return comp_scores.get((cancer, pname, sid), 0.0)

for pname in PANELS:
    pdf[f"d_{pname}"] = [
        abs(dz(r.cancer, pname, r.sample_a) - dz(r.cancer, pname, r.sample_b))
        for r in pdf.itertuples()
    ]
pdf["d_overall3"] = pdf[["d_immune", "d_stromal", "d_epithelial"]].mean(axis=1)
pdf["d_overall4"] = pdf[["d_immune", "d_myeloid", "d_stromal", "d_epithelial"]].mean(axis=1)

# ====================================================================
# 5. Weighted OLS helpers (verbatim 74)
# ====================================================================
def wls(y, X, names, w=None):
    n = len(y)
    if w is None:
        w = np.ones(n)
    sw = np.sqrt(w)
    Xd = np.column_stack([np.ones(n), X]) * sw[:, None]
    yw = y * sw
    beta, *_ = np.linalg.lstsq(Xd, yw, rcond=None)
    return dict(zip(["intercept"] + names, beta))

tests = []

# --- C3: |Delta| TT vs NN for myeloid and both overall variants ---
for pname in ["myeloid", "overall3", "overall4"]:
    col = f"d_{pname}"
    tt = pdf[pdf["pair_type"] == "TT"][col]
    nn = pdf[pdf["pair_type"] == "NN"][col]
    u, p = stats.mannwhitneyu(tt, nn, alternative="greater")
    tests.append((f"C3_dcomp_TT_gt_NN_{pname}",
                  f"|Delta {pname}|: TT median={tt.median():.3f} NN median={nn.median():.3f}",
                  tt.median() / max(nn.median(), 1e-12), p))

# --- C4: attenuation, 3-panel vs 4-panel adjustment, per cancer + pooled ---
for scope in TARGET_PROJECTS + ["pooled"]:
    d = pdf if scope == "pooled" else pdf[pdf["cancer"] == scope]
    y = np.log(d["kn"].values)
    tt = (d["pair_type"] == "TT").astype(float).values
    X3 = d[["d_immune", "d_stromal", "d_epithelial"]].values
    X4 = d[["d_immune", "d_myeloid", "d_stromal", "d_epithelial"]].values

    b0 = wls(y, tt.reshape(-1, 1), ["TT"])["TT"]
    b3 = wls(y, np.column_stack([X3, tt]),
             ["d_immune", "d_stromal", "d_epithelial", "TT"])["TT"]
    b4 = wls(y, np.column_stack([X4, tt]),
             ["d_immune", "d_myeloid", "d_stromal", "d_epithelial", "TT"])["TT"]
    att3 = 1 - b3 / b0
    att4 = 1 - b4 / b0
    tests.append((f"C4_attenuation_{scope}",
                  f"TT coef {b0:+.4f} -> 3-panel {b3:+.4f} (att {att3:+.1%}) -> "
                  f"4-panel(+myeloid) {b4:+.4f} (att {att4:+.1%})",
                  att4, np.nan))

# --- C5: Spearman with 4-panel overall ---
tt_all = pdf[pdf["pair_type"] == "TT"]
rho, p = stats.spearmanr(tt_all["kn"], tt_all["d_overall4"])
tests.append(("C5_spearman_kn_dcomp4_TT_pooled",
              f"rho(4-panel)={rho:.3f} (n={len(tt_all)})", rho, p))
for cancer in TARGET_PROJECTS:
    tt = pdf[(pdf["cancer"] == cancer) & (pdf["pair_type"] == "TT")]
    rho, p = stats.spearmanr(tt["kn"], tt["d_overall4"])
    tests.append((f"C5_spearman_kn_dcomp4_TT_{cancer}",
                  f"rho(4-panel)={rho:.3f} (n={len(tt)})", rho, p))

# ====================================================================
# 6. Sample-level cluster bootstrap (B=200, verbatim 74 scheme)
# ====================================================================
print(f"4. Cluster bootstrap by sample (B={N_BOOT}, seed {RANDOM_SEED})...")
rng = np.random.default_rng(RANDOM_SEED)

by_cancer = {}
for cancer in TARGET_PROJECTS:
    d = pdf[pdf["cancer"] == cancer]
    tumor_ids = sorted(set(d[d.pair_type == "TT"]["sample_a"]) |
                       set(d[d.pair_type == "TT"]["sample_b"]))
    normal_ids = sorted(set(d[d.pair_type == "NN"]["sample_a"]) |
                        set(d[d.pair_type == "NN"]["sample_b"]))
    by_cancer[cancer] = {
        "tt": d[d.pair_type == "TT"].reset_index(drop=True),
        "nn": d[d.pair_type == "NN"].reset_index(drop=True),
        "tumor": tumor_ids, "normal": normal_ids,
    }

def boot_attenuation(panels):
    ys, Xs, tts, ws = [], [], [], []
    atts = {}
    for cancer in TARGET_PROJECTS:
        info = by_cancer[cancer]
        t_draw = rng.choice(info["tumor"], size=len(info["tumor"]), replace=True)
        n_draw = rng.choice(info["normal"], size=len(info["normal"]), replace=True)
        ct = pd.Series(t_draw).value_counts()
        cn = pd.Series(n_draw).value_counts()
        sub_frames = []
        for ptype, draw_counts, ids in (("TT", ct, t_draw), ("NN", cn, n_draw)):
            dd = info["tt"] if ptype == "TT" else info["nn"]
            w = (dd["sample_a"].map(draw_counts).fillna(0) *
                 dd["sample_b"].map(draw_counts).fillna(0))
            keep = w > 0
            if keep.sum() == 0:
                return None
            dds = dd[keep].copy()
            dds["w"] = w[keep].values
            sub_frames.append(dds)
        d = pd.concat(sub_frames, ignore_index=True)
        y = np.log(d["kn"].values)
        tt = (d["pair_type"] == "TT").astype(float).values
        Xc = d[panels].values
        b0 = wls(y, tt.reshape(-1, 1), ["TT"])["TT"]
        b1 = wls(y, np.column_stack([Xc, tt]), panels + ["TT"])["TT"]
        atts[cancer] = 1 - b1 / b0
        ys.append(y); Xs.append(Xc); tts.append(tt); ws.append(d["w"].values)
    y = np.concatenate(ys); Xc = np.concatenate(Xs)
    tt = np.concatenate(tts); w = np.concatenate(ws)
    b0 = wls(y, tt.reshape(-1, 1), ["TT"])["TT"]
    b1 = wls(y, np.column_stack([Xc, tt]), panels + ["TT"])["TT"]
    return 1 - b1 / b0, atts

P4 = ["d_immune", "d_myeloid", "d_stromal", "d_epithelial"]
P3 = ["d_immune", "d_stromal", "d_epithelial"]
boot4_pool, boot4_by = [], {c: [] for c in TARGET_PROJECTS}
boot3_pool = []
n_ok = 0
while n_ok < N_BOOT:
    r4 = boot_attenuation(P4)
    if r4 is None:
        continue
    r3 = boot_attenuation(P3)
    if r3 is None:
        continue
    a4, by4 = r4
    a3, _ = r3
    boot4_pool.append(a4); boot3_pool.append(a3)
    for c in TARGET_PROJECTS:
        boot4_by[c].append(by4[c])
    n_ok += 1
    if n_ok % 50 == 0:
        print(f"    {n_ok}/{N_BOOT}  ({time.time()-t0:.0f}s)")

boot4_pool = np.array(boot4_pool); boot3_pool = np.array(boot3_pool)
lo, hi = np.percentile(boot4_pool, [2.5, 97.5])
lo3, hi3 = np.percentile(boot3_pool, [2.5, 97.5])
tests.append(("BOOT_attenuation_pooled_4panel",
              f"median {np.median(boot4_pool):+.1%}, 95% CI [{lo:+.1%}, {hi:+.1%}] "
              f"(B={N_BOOT}, sample-level cluster bootstrap)",
              np.median(boot4_pool), np.nan))
tests.append(("BOOT_attenuation_pooled_3panel",
              f"median {np.median(boot3_pool):+.1%}, 95% CI [{lo3:+.1%}, {hi3:+.1%}] "
              f"(B={N_BOOT})",
              np.median(boot3_pool), np.nan))
for c in TARGET_PROJECTS:
    arr = np.array(boot4_by[c])
    l, h = np.percentile(arr, [2.5, 97.5])
    tests.append((f"BOOT_attenuation_{c}_4panel",
                  f"median {np.median(arr):+.1%}, 95% CI [{l:+.1%}, {h:+.1%}]",
                  np.median(arr), np.nan))

# ====================================================================
# 7. Save
# ====================================================================
out = pd.DataFrame(tests, columns=["test_id", "description", "effect", "p_value"])
out.to_csv(RESULTS_DIR / "tcga_composition_v44.csv", index=False)

lines = ["TCGA composition check v44 (linear normalization): myeloid panel + cluster bootstrap",
         "=" * 78,
         f"Pairs: {len(pdf)} (v44 linear-norm recompute, 85_tcga_linear_norm_v44.py, seed 42; "
         f"{n_kn_nonpos} pairs with k_n<=0 excluded); "
         f"panels: immune(7) + myeloid(5) + stromal(6) + epithelial(4)", ""]
lines.append("Panel genes kept per cancer (after mean TPM>=0.5 filter):")
for cancer in TARGET_PROJECTS:
    lines.append(f"  {cancer}: " + "; ".join(
        f"{p}={','.join(gene_report[cancer][p]) if gene_report[cancer][p] else 'NONE'}"
        for p in PANELS))
lines.append("")
for tid, desc, eff, p in tests:
    lines.append(f"[{tid}] {desc}")
    if not (isinstance(p, float) and np.isnan(p)):
        lines.append(f"    effect = {eff:.4g}    P = {p:.3g}")
    else:
        lines.append(f"    effect = {eff:.4g}")
    lines.append("")
(RESULTS_DIR / "tcga_composition_v44.txt").write_text("\n".join(lines), encoding="utf-8")

print("\n".join(lines))
print(f"\nSaved: {RESULTS_DIR/'tcga_composition_v44.csv'}")
print(f"Saved: {RESULTS_DIR/'tcga_composition_v44.txt'}")
print(f"Total time: {time.time()-t0:.0f}s")
