# -*- coding: utf-8 -*-
"""
TCGA composition-contribution sanity check (reviewer-facing).

Motivation:
  In the TCGA analysis, Tumor-Tumor (TT) pairs show 2-3.7x higher k_n than
  Normal-Normal (NN) pairs, and the NN>TT omega reversal is a k_n effect.
  A natural objection: bulk tumor samples differ in cellular composition
  (purity), which inflates TT k_n - i.e. the k_n "baseline" is contaminated
  by composition, not just technical noise.

This check replicates the AUTHORITATIVE per-cancer pipeline of
06_phase34_v2.py (per-cancer gene loading and mean TPM>=0.5 filtering,
log2(TPM+1), per-cancer HK mapping, top-200 abs-diff k_f genes,
kn_floor=1e-4, seed 42, MAX_PAIRS_TT=2000, all NN pairs) while adding:
  C1. Reproduce the NN/TT k_n reversal with sample-labelled pairs.
  C2. Estimate per-sample lineage composition from marker panels
      (immune / stromal / epithelial), z-scored within each cancer.
  C3. Test whether |Delta composition| between the two members of a pair
      is larger for TT than NN pairs (MWU).
  C4. Regression: k_n ~ |Delta immune| + |Delta stromal| + |Delta epithelial|
      + pair_type (TT=1), per cancer and pooled; report the attenuation of
      the TT coefficient when composition covariates are added.
  C5. Spearman correlation of k_n with overall |Delta composition| within
      TT pairs.

Outputs:
  results/tcga_composition_pairs.csv   (per-pair k_n/k_f/omega + composition deltas)
  results/tcga_composition_check.csv   (test-level results)
  results/tcga_composition_check.txt   (summary)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gzip, time, warnings
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from cki.core import compute_omega

warnings.filterwarnings("ignore")

# === Config (mirrors 06_phase34_v2.py) ===
TCGA_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\tcga\tcga_RSEM_gene_tpm.gz")
HK_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\housekeeping\Human_Mouse_Common.csv")
PROBEMAP_FILE = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\data\tcga\probemap.tsv")
RESULTS_DIR = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\results")

RANDOM_SEED = 42
N_TOP_KF = 200
MIN_NORMAL_SAMPLES = 15
MIN_TUMOR_SAMPLES = 30
MAX_PAIRS_TT = 2000   # same cap as v2 (output used n_TT = 2000 per cancer)

TARGET_PROJECTS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-LIHC", "TCGA-KIRC", "TCGA-BRCA"]

PANELS = {
    "immune": ["CD3D", "CD3E", "CD8A", "GZMB", "NKG7", "MS4A1", "CD79A"],
    "stromal": ["COL1A1", "COL1A2", "DCN", "LUM", "FAP", "VIM"],
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
# 1. Header + sample classification
# ====================================================================
print("1. Reading TCGA header...")
with gzip.open(TCGA_FILE, "rt") as fh:
    header_line = fh.readline().strip().split("\t")

sample_info = []
for sid in header_line[1:]:
    proj, code = parse_tcga_barcode(sid)
    if proj in TARGET_PROJECTS and code in ("01", "11"):
        sample_info.append({"sample_id": sid, "project": proj, "code": code})
df_samples = pd.DataFrame(sample_info)

proj_tumor, proj_normal = {}, {}
for proj in TARGET_PROJECTS:
    sub = df_samples[df_samples["project"] == proj]
    t = sub[sub["code"] == "01"]["sample_id"].tolist()
    n = sub[sub["code"] == "11"]["sample_id"].tolist()
    if len(n) >= MIN_NORMAL_SAMPLES and len(t) >= MIN_TUMOR_SAMPLES:
        proj_tumor[proj] = t
        proj_normal[proj] = n
        print(f"  {proj}: tumor={len(t)}, normal={len(n)}")
usable = list(proj_tumor.keys())

# ====================================================================
# 2. Global gene maps (probeMap + HK symbols)
# ====================================================================
print("2. Loading probeMap + HK symbols...")
pm = pd.read_csv(PROBEMAP_FILE, sep="\t")
ens_to_symbol = {}
for _, row in pm.iterrows():
    ens_id = str(row.iloc[0]).split(".")[0]
    symbol = str(row.iloc[1])
    if ens_id and symbol and symbol != "nan":
        ens_to_symbol[ens_id] = symbol
symbol_to_ens = {}
for ens_id, symbol in ens_to_symbol.items():
    symbol_to_ens.setdefault(symbol, []).append(ens_id)

hk_df = pd.read_csv(HK_FILE)
hk_human = set()
for row in hk_df.iloc[:, 0].dropna().astype(str):
    parts = row.split(";")
    if len(parts) >= 2:
        hk_human.add(parts[1].strip())
print(f"  HK symbols: {len(hk_human)}")

# ====================================================================
# 3. Per-cancer loading (mirrors v2 load_cancer_data)
# ====================================================================
def load_cancer_data(cancer):
    tumor_ids, normal_ids = proj_tumor[cancer], proj_normal[cancer]
    wanted = set(tumor_ids + normal_ids)
    col_idx_map = {}
    for k, sid in enumerate(header_line[1:], 1):
        if sid in wanted:
            col_idx_map[sid] = k
    sample_list = sorted(wanted)
    col_arr = np.array([col_idx_map[s] for s in sample_list], dtype=np.int32)

    gene_names = []
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split("\t")
            has_expr = False
            for ci in col_arr:
                if ci < len(parts):
                    try:
                        if float(parts[ci]) > 0:
                            has_expr = True
                            break
                    except (ValueError, IndexError):
                        pass
            if has_expr:
                gene_names.append(parts[0])
    n_genes = len(gene_names)

    expr = np.zeros((len(sample_list), n_genes), dtype=np.float32)
    gene_idx = 0
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.strip().split("\t")
            if gene_idx < n_genes and parts[0] == gene_names[gene_idx]:
                for si, ci in enumerate(col_arr):
                    if ci < len(parts):
                        try:
                            expr[si, gene_idx] = float(parts[ci])
                        except (ValueError, IndexError):
                            pass
                gene_idx += 1
                if gene_idx >= n_genes:
                    break

    # Per-cancer gene filtering: mean TPM >= 0.5 (v2)
    keep = np.mean(expr, axis=0) >= 0.5
    expr = expr[:, keep]
    genes = [g for g, k in zip(gene_names, keep) if k]
    expr_log = np.log2(np.maximum(expr, 0) + 1)

    gene_ens = [g.split(".")[0] for g in genes]
    ens_to_idx_local = {ens: i for i, ens in enumerate(gene_ens)}
    hk_arr = np.array(sorted({
        ens_to_idx_local[ens]
        for sym in hk_human if sym in symbol_to_ens
        for ens in symbol_to_ens[sym] if ens in ens_to_idx_local
    }), dtype=int)

    tumor_mask = np.array([s in set(tumor_ids) for s in sample_list])
    return sample_list, expr_log, hk_arr, tumor_mask, ens_to_idx_local

def select_top_diff(pb1, pb2, hk_idx, n_top=200):
    diff = np.abs(pb1 - pb2)
    mask = np.ones(len(pb1), dtype=bool)
    mask[hk_idx] = False
    diff[~mask] = -1
    top = np.argsort(diff)[-n_top:]
    top = top[diff[top] >= 0]
    return np.sort(top).astype(int)

# ====================================================================
# 4. Per-cancer pairs + composition
# ====================================================================
print("3. Per-cancer pair generation (v2 pipeline, seed 42)...")
pair_rows = []

for cancer in usable:
    sample_list, expr_log, hk_arr, tumor_mask, ens_local = load_cancer_data(cancer)
    sid_pos = {s: i for i, s in enumerate(sample_list)}
    t_idx = np.where(tumor_mask)[0]
    n_idx = np.where(~tumor_mask)[0]
    print(f"  {cancer}: genes={expr_log.shape[1]}, HK={len(hk_arr)}, "
          f"T={len(t_idx)}, N={len(n_idx)}  ({time.time()-t0:.0f}s)")

    # marker panel indices per cancer
    panel_idx = {}
    for pname, symbols in PANELS.items():
        idxs = []
        for sym in symbols:
            for ens in symbol_to_ens.get(sym, []):
                if ens in ens_local:
                    idxs.append(ens_local[ens])
        panel_idx[pname] = np.array(sorted(set(idxs)), dtype=int)

    # composition scores, z-scored within cancer (tumor+normal)
    comp_scores = {}
    for pname, idxs in panel_idx.items():
        raw = expr_log[:, idxs].mean(axis=1)
        sd = raw.std(ddof=0)
        comp_scores[pname] = (raw - raw.mean()) / sd if sd > 0 else raw * 0.0

    def add_pair(ptype, ids, i, j):
        s1, s2 = ids[i], ids[j]
        p1 = expr_log[sid_pos[s1], :]
        p2 = expr_log[sid_pos[s2], :]
        id_idx = select_top_diff(p1, p2, hk_arr, N_TOP_KF)
        r = compute_omega(p1, p2, hk_arr, id_idx, w1=1.0, w2=0.0, kn_floor=1e-4)
        row = {"cancer": cancer, "pair_type": ptype,
               "sample_a": s1, "sample_b": s2,
               "kn": r["kn"], "kf": r["kf"], "omega": r["omega"]}
        for pname in PANELS:
            row[f"d_{pname}"] = abs(comp_scores[pname][sid_pos[s1]] -
                                    comp_scores[pname][sid_pos[s2]])
        row["d_overall"] = np.mean([row[f"d_{p}"] for p in PANELS])
        pair_rows.append(row)

    # TT pairs: random subsample cap 2000 (v2)
    all_tt = [(i, j) for i in range(len(t_idx)) for j in range(i + 1, len(t_idx))]
    np.random.seed(RANDOM_SEED)
    if len(all_tt) > MAX_PAIRS_TT:
        sel = np.random.choice(len(all_tt), MAX_PAIRS_TT, replace=False)
        tt_pairs = [all_tt[k] for k in sel]
    else:
        tt_pairs = all_tt
    t_ids = [sample_list[i] for i in t_idx]
    for (i, j) in tt_pairs:
        add_pair("TT", t_ids, i, j)
    print(f"    TT: {len(tt_pairs)} done  ({time.time()-t0:.0f}s)")

    # NN pairs: all (v2)
    n_ids = [sample_list[i] for i in n_idx]
    for i in range(len(n_ids)):
        for j in range(i + 1, len(n_ids)):
            add_pair("NN", n_ids, i, j)
    print(f"    NN: {len(n_ids)*(len(n_ids)-1)//2} done  ({time.time()-t0:.0f}s)")

pdf = pd.DataFrame(pair_rows)
pdf.to_csv(RESULTS_DIR / "tcga_composition_pairs.csv", index=False)

# ====================================================================
# 5. Tests
# ====================================================================
print("4. Running tests...")
tests = []

for cancer in usable:
    nn = pdf[(pdf["cancer"] == cancer) & (pdf["pair_type"] == "NN")]["kn"]
    tt = pdf[(pdf["cancer"] == cancer) & (pdf["pair_type"] == "TT")]["kn"]
    u, p = stats.mannwhitneyu(tt, nn, alternative="greater")
    tests.append((f"C1_kn_reversal_{cancer}",
                  f"median k_n NN={nn.median():.5f} TT={tt.median():.5f} "
                  f"ratio(TT/NN)={tt.median()/nn.median():.2f}x",
                  tt.median() / nn.median(), p))

for pname in list(PANELS) + ["overall"]:
    col = f"d_{pname}"
    tt = pdf[pdf["pair_type"] == "TT"][col]
    nn = pdf[pdf["pair_type"] == "NN"][col]
    u, p = stats.mannwhitneyu(tt, nn, alternative="greater")
    tests.append((f"C3_dcomp_TT_gt_NN_{pname}",
                  f"|Delta {pname}|: TT median={tt.median():.3f} NN median={nn.median():.3f}",
                  tt.median() / max(nn.median(), 1e-12), p))

def ols(y, X, names):
    n = len(y)
    Xd = np.column_stack([np.ones(n), X])
    beta, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    resid = y - Xd @ beta
    dof = n - Xd.shape[1]
    s2 = resid @ resid / dof
    covb = s2 * np.linalg.inv(Xd.T @ Xd)
    se = np.sqrt(np.diag(covb))
    tstats = beta / se
    pvals = 2 * stats.t.sf(np.abs(tstats), dof)
    r2 = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
    return dict(zip(["intercept"] + names, zip(beta, pvals))), r2

for scope in usable + ["pooled"]:
    d = pdf if scope == "pooled" else pdf[pdf["cancer"] == scope]
    y = np.log(d["kn"].values)  # log k_n: k_n is heavily right-skewed
    tt = (d["pair_type"] == "TT").astype(float).values
    Xc = d[["d_immune", "d_stromal", "d_epithelial"]].values

    b0, r2_0 = ols(y, tt.reshape(-1, 1), ["TT"])
    b1, r2_1 = ols(y, np.column_stack([Xc, tt]),
                   ["d_immune", "d_stromal", "d_epithelial", "TT"])
    att = 1 - b1["TT"][0] / b0["TT"][0]
    tests.append((f"C4_ols_{scope}",
                  f"log k_n ~ ...: TT coef {b0['TT'][0]:+.4f} (P={b0['TT'][1]:.1e}) -> "
                  f"{b1['TT'][0]:+.4f} (P={b1['TT'][1]:.1e}) after composition "
                  f"covariates; attenuation {att:.0%}; R2 {r2_0:.3f}->{r2_1:.3f}; "
                  f"d_imm P={b1['d_immune'][1]:.1e}, d_str P={b1['d_stromal'][1]:.1e}, "
                  f"d_epi P={b1['d_epithelial'][1]:.1e}",
                  att, b1["TT"][1]))

for cancer in usable:
    tt = pdf[(pdf["cancer"] == cancer) & (pdf["pair_type"] == "TT")]
    rho, p = stats.spearmanr(tt["kn"], tt["d_overall"])
    tests.append((f"C5_spearman_kn_dcomp_TT_{cancer}",
                  f"rho={rho:.3f} (n={len(tt)})", rho, p))
# pooled TT Spearman
tt_all = pdf[pdf["pair_type"] == "TT"]
rho, p = stats.spearmanr(tt_all["kn"], tt_all["d_overall"])
tests.append(("C5_spearman_kn_dcomp_TT_pooled", f"rho={rho:.3f} (n={len(tt_all)})", rho, p))

out = pd.DataFrame(tests, columns=["test_id", "description", "effect", "p_value"])
out.to_csv(RESULTS_DIR / "tcga_composition_check.csv", index=False)

lines = ["TCGA composition-contribution sanity check (per-cancer v2 pipeline)", "=" * 70,
         f"Pairs analysed: {len(pdf)} "
         f"(NN={len(pdf[pdf.pair_type=='NN'])}, TT={len(pdf[pdf.pair_type=='TT'])}, "
         f"TT cap {MAX_PAIRS_TT}/cancer, all NN pairs, seed {RANDOM_SEED})", ""]
for tid, desc, eff, p in tests:
    lines.append(f"[{tid}] {desc}")
    lines.append(f"    effect = {eff:.4g}    P = {p:.3g}")
    lines.append("")
(RESULTS_DIR / "tcga_composition_check.txt").write_text("\n".join(lines), encoding="utf-8")

print("\n".join(lines))
print(f"\nSaved: {RESULTS_DIR/'tcga_composition_pairs.csv'}")
print(f"Saved: {RESULTS_DIR/'tcga_composition_check.csv'}")
print(f"Saved: {RESULTS_DIR/'tcga_composition_check.txt'}")
