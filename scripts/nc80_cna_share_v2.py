# -*- coding: utf-8 -*-
"""nc80 CNA share v2 (stat M1/M2 fixes, ground-truth rulings 6 & 2).

Replaces the nc79_a1 measured share with three corrections:

1. Denominator unification (ruling 6): delta_obs is now the FULL-pair-table
   TT-vs-NN mean log-k_n gap (the caliber of the manuscript's reported
   reversal), not the DNA-profiled-subset gap. KIRC's DNA coverage is only
   44% of sampled TT pairs and the subset gap (0.833) is 42% smaller than
   the full-table gap (1.181).
2. Direct bootstrap pooling replaces IVW ratio pooling (the IVW assumed
   symmetric SEs back-computed from skewed percentile CIs; LIHC's interval
   is 5.4x wider above than below). The pooled share is the per-draw
   contribution ratio sum(C_c)/sum(G_c) -- the share of the pooled gap --
   plus the unweighted mean of per-cancer shares as a secondary descriptive.
3. Per-cancer shares and CIs are reported in full, including LIHC's
   unstable estimate (share can exceed 1).

Panel B adds the joint confounder model (stat M2):
    log k_n ~ is_TT + cna_l1(delta for NN, cancer-mean imputation for
    non-profiled TT) + d_overall4 (+ mean RIN variant)
per cancer and pooled, sample-cluster bootstrap, reporting the additive
decomposition share_CNA / share_comp / residual, which replaces the
incommensurable "60% CNA / +44% composition / largely intact" triple.

Cohort: ex-CC default (authoritative Section 1.7 caliber) as primary; a
CC-inclusive variant of Panel A is reported for continuity with v1 (CC
affects LIHC only).

Outputs:
  results/nc80_cna_share_v2.csv          Panel A (scope x delta x cohort variant)
  results/nc80_cna_joint_model.csv       Panel B (scope x delta x model variant)
  results/nc80_cna_share_v2_report.txt   human-readable summary
Seed: 20261116, per-scope crc32-derived. B = 2000.
"""
import gzip
import json
import os
import sys
import time
import zlib

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
DATA = os.path.join(ROOT, "data")

CANCERS = ["BRCA", "KIRC", "LIHC", "LUAD", "LUSC"]
CANCER_IDS = ["TCGA-" + c for c in CANCERS]
B = 2000
SEED = 20261116
DELTAS = [round(d, 2) for d in np.arange(0.0, 0.11, 0.01)]
DELTAS_REPORT = [0.0, 0.02, 0.05, 0.10]

TCGA_FILE = os.path.join(DATA, "tcga", "tcga_RSEM_gene_tpm.gz")
PROBEMAP_FILE = os.path.join(DATA, "tcga", "probemap.tsv")
RIN_CACHE = os.path.join(DATA, "tcga", "gdc_rin_cache.json")

PANELS = {
    "immune": ["CD3D", "CD3E", "CD8A", "GZMB", "NKG7", "MS4A1", "CD79A"],
    "myeloid": ["CD68", "CD163", "LST1", "FCGR3A", "C1QA"],
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


def is_cc(s):
    s = str(s)
    return len(s) >= 7 and s[5:7] == "CC"


def parse_barcode(barcode):
    parts = barcode.split("-")
    if len(parts) >= 4:
        proj = TSS_TO_PROJECT.get(parts[1])
        if proj is not None:
            proj = "TCGA-" + proj
        return proj, parts[3][:2]
    return None, None


def load_pairs():
    ap = pd.read_csv(os.path.join(RESULTS, "tcga_linear_norm_v44_all_pairs.csv"))
    ap = ap[ap["pair_type"].isin(["TT", "NN"])]
    ap = ap[ap["kn"] > 0].reset_index(drop=True)
    cp = pd.read_csv(os.path.join(RESULTS, "nc79_a1_cna_pairs.csv"))
    cpt = cp[cp["pair_type"] == "TT"][["cancer", "sample_a", "sample_b", "cna_l1"]]
    cpt = cpt.dropna(subset=["cna_l1"])
    cpt = cpt[cpt["cancer"].isin(CANCERS)]
    cna_map = {("TCGA-" + r.cancer, r.sample_a, r.sample_b): r.cna_l1
               for r in cpt.itertuples()}
    ap["cna_l1"] = [
        cna_map.get((r.cancer, r.sample_a, r.sample_b), np.nan) for r in ap.itertuples()
    ]
    return ap


def compute_panel_scores():
    """Four-panel per-cancer z-scores, ex-CC standardization (nc52 rule)."""
    with gzip.open(TCGA_FILE, "rt") as fh:
        header_line = fh.readline().strip().split("\t")
    target_cols = []
    for k, sid in enumerate(header_line[1:], 1):
        proj, code = parse_barcode(sid)
        if proj in CANCER_IDS and code in ("01", "11") and not is_cc(sid):
            target_cols.append((sid, proj, code, k))

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
    with gzip.open(TCGA_FILE, "rt") as fh:
        fh.readline()
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            sym = ens_to_symbol.get(parts[0].split(".")[0])
            if sym is None or sym not in panel_symbols:
                continue
            for (sid, proj, code, ci) in target_cols:
                v = float(parts[ci]) if ci < len(parts) else 0.0
                if v != v or v < 0.0:
                    v = 0.0
                raw.setdefault((proj, code), {}).setdefault(sym, []).append((sid, v))

    comp_scores = {}
    for cancer in CANCER_IDS:
        tumor_ids = [s for (s, p, c, k) in target_cols if p == cancer and c == "01"]
        normal_ids = [s for (s, p, c, k) in target_cols if p == cancer and c == "11"]
        all_ids = tumor_ids + normal_ids
        allset = set(all_ids)
        for pname, symbols in PANELS.items():
            gene_vals = {}
            for sym in symbols:
                if sym not in raw.get((cancer, "01"), {}) and sym not in raw.get((cancer, "11"), {}):
                    continue
                d_acc = {}
                for code_key in ("01", "11"):
                    for (sid, v) in raw.get((cancer, code_key), {}).get(sym, []):
                        if sid in allset:
                            d_acc.setdefault(sid, []).append(v)
                d = {sid: float(np.mean(vs)) for sid, vs in d_acc.items()}
                if len(d) < len(all_ids):
                    for sid in all_ids:
                        d.setdefault(sid, 0.0)
                m = np.mean([d[s] for s in all_ids])
                if m >= 0.5:
                    gene_vals[sym] = d
            kept = sorted(gene_vals.keys())
            if not kept:
                for sid in all_ids:
                    comp_scores[(cancer, pname, sid)] = 0.0
                continue
            mu = np.array([np.mean([np.log2(gene_vals[g][s] + 1) for g in kept])
                           for s in all_ids])
            sd = mu.std(ddof=0)
            for sid, v in zip(all_ids, mu):
                comp_scores[(cancer, pname, sid)] = (v - mu.mean()) / sd if sd > 0 else 0.0
    return comp_scores


def wmean(x, w):
    return float(np.sum(w * x) / np.sum(w))


def wslope(x, y, w):
    mx, my = wmean(x, w), wmean(y, w)
    den = np.sum(w * (x - mx) ** 2)
    if den <= 0:
        return np.nan
    return float(np.sum(w * (x - mx) * (y - my)) / den)


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


# ----------------------------------------------------------------------
# Panel A
# ----------------------------------------------------------------------
def panel_a(ap, cohort):
    rows = []
    per_cancer_draws = {}
    for c in CANCERS:
        d = ap[ap["cancer"] == "TCGA-" + c].reset_index(drop=True)
        if cohort == "excc":
            m = d["sample_a"].map(is_cc) | d["sample_b"].map(is_cc)
            d = d[~m].reset_index(drop=True)
        tt = d[d["pair_type"] == "TT"].reset_index(drop=True)
        nn = d[d["pair_type"] == "NN"].reset_index(drop=True)
        y_tt = np.log(tt["kn"].values)
        y_nn = np.log(nn["kn"].values)
        dna = tt["cna_l1"].notna().values
        x_tt = tt["cna_l1"].values
        g_full = float(y_tt.mean() - y_nn.mean())
        beta = wslope(x_tt[dna], y_tt[dna], np.ones(int(dna.sum())))
        mx = float(np.mean(x_tt[dna]))

        samples = np.array(sorted(set(tt["sample_a"]) | set(tt["sample_b"])
                                  | set(nn["sample_a"]) | set(nn["sample_b"])))
        sidx = {s: i for i, s in enumerate(samples)}
        S = len(samples)
        ca_t = tt["sample_a"].map(sidx).values
        cb_t = tt["sample_b"].map(sidx).values
        ca_n = nn["sample_a"].map(sidx).values
        cb_n = nn["sample_b"].map(sidx).values

        rng = np.random.default_rng(SEED + zlib.crc32(f"v2A|{cohort}|{c}".encode()) % 10000)
        share_draws = {dd: [] for dd in DELTAS}
        ok = 0
        for _ in range(B):
            draw = rng.integers(0, S, S)
            cnt = np.bincount(draw, minlength=S).astype(float)
            wt = cnt[ca_t] * cnt[cb_t]
            wn = cnt[ca_n] * cnt[cb_n]
            kt, kn_ = wt > 0, wn > 0
            if kt.sum() < 100 or kn_.sum() < 100:
                continue
            dd_g = wmean(y_tt[kt], wt[kt]) - wmean(y_nn[kn_], wn[kn_])
            kd = kt & dna
            if kd.sum() < 30:
                continue
            b = wslope(x_tt[kd], y_tt[kd], wt[kd])
            m_b = wmean(x_tt[kd], wt[kd])
            if not np.isfinite(b) or not np.isfinite(dd_g) or abs(dd_g) < 1e-9:
                continue
            ok += 1
            for dlt in DELTAS:
                share_draws[dlt].append(b * (m_b - dlt) / dd_g)
        per_cancer_draws[c] = share_draws

        for dlt in DELTAS:
            arr = np.array(share_draws[dlt])
            lo, hi = (np.percentile(arr, [2.5, 97.5]) if len(arr) > 20 else (np.nan, np.nan))
            rows.append(dict(
                panel="A", cohort=cohort, scope=c, delta=dlt,
                gap_full=g_full, beta_CNA_TT=beta, mean_cna_TT=mx,
                n_tt_full=int(len(tt)), n_tt_dna=int(dna.sum()), n_nn=int(len(nn)),
                dna_pair_coverage=dna.sum() / len(tt),
                share=beta * (mx - dlt) / g_full,
                share_lo=float(lo), share_hi=float(hi),
                boot_ok=ok,
            ))

    # pooled scope is computed separately in panel_a_pooled()
    return pd.DataFrame(rows)


def panel_a_pooled(ap):
    """Pooled contribution-ratio share with a proper stratified bootstrap."""
    data = {}
    for c in CANCERS:
        d = ap[ap["cancer"] == "TCGA-" + c]
        m = d["sample_a"].map(is_cc) | d["sample_b"].map(is_cc)
        d = d[~m].reset_index(drop=True)
        tt = d[d["pair_type"] == "TT"].reset_index(drop=True)
        nn = d[d["pair_type"] == "NN"].reset_index(drop=True)
        data[c] = dict(tt=tt, nn=nn)
    # point
    Cs, Gs, betas, mxs = {}, {}, {}, {}
    for c in CANCERS:
        tt, nn = data[c]["tt"], data[c]["nn"]
        y_tt = np.log(tt["kn"].values)
        y_nn = np.log(nn["kn"].values)
        dna = tt["cna_l1"].notna().values
        x = tt["cna_l1"].values
        betas[c] = wslope(x[dna], y_tt[dna], np.ones(int(dna.sum())))
        mxs[c] = float(np.mean(x[dna]))
        Gs[c] = float(y_tt.mean() - y_nn.mean())
        Cs[c] = betas[c] * mxs[c]

    rng = np.random.default_rng(SEED + zlib.crc32(b"v2A|excc|pooled") % 10000)
    idx = {}
    for c in CANCERS:
        tt, nn = data[c]["tt"], data[c]["nn"]
        samples = np.array(sorted(set(tt["sample_a"]) | set(tt["sample_b"])
                                  | set(nn["sample_a"]) | set(nn["sample_b"])))
        sidx = {s: i for i, s in enumerate(samples)}
        idx[c] = dict(
            samples=samples, S=len(samples),
            ca_t=tt["sample_a"].map(sidx).values, cb_t=tt["sample_b"].map(sidx).values,
            ca_n=nn["sample_a"].map(sidx).values, cb_n=nn["sample_b"].map(sidx).values,
            y_tt=np.log(tt["kn"].values), y_nn=np.log(nn["kn"].values),
            dna=tt["cna_l1"].notna().values, x=tt["cna_l1"].values,
        )
    draws = {dlt: [] for dlt in DELTAS}
    mean_draws = {dlt: [] for dlt in DELTAS}
    ok = 0
    for _ in range(B):
        num = {dlt: 0.0 for dlt in DELTAS}
        den = 0.0
        shares = {dlt: [] for dlt in DELTAS}
        good = True
        for c in CANCERS:
            ic = idx[c]
            draw = rng.integers(0, ic["S"], ic["S"])
            cnt = np.bincount(draw, minlength=ic["S"]).astype(float)
            wt = cnt[ic["ca_t"]] * cnt[ic["cb_t"]]
            wn = cnt[ic["ca_n"]] * cnt[ic["cb_n"]]
            kt, kn_ = wt > 0, wn > 0
            kd = kt & ic["dna"]
            if kt.sum() < 100 or kn_.sum() < 100 or kd.sum() < 30:
                good = False
                break
            b = wslope(ic["x"][kd], ic["y_tt"][kd], wt[kd])
            m_b = wmean(ic["x"][kd], wt[kd])
            g_b = wmean(ic["y_tt"][kt], wt[kt]) - wmean(ic["y_nn"][kn_], wn[kn_])
            if not np.isfinite(b) or not np.isfinite(g_b) or abs(g_b) < 1e-9:
                good = False
                break
            den += g_b
            for dlt in DELTAS:
                contrib = b * (m_b - dlt)
                num[dlt] += contrib
                shares[dlt].append(contrib / g_b)
        if not good:
            continue
        ok += 1
        for dlt in DELTAS:
            draws[dlt].append(num[dlt] / den)
            mean_draws[dlt].append(float(np.mean(shares[dlt])))
    rows = []
    for dlt in DELTAS:
        point = sum(Cs[c] - dlt * betas[c] for c in CANCERS) / sum(Gs.values())
        arr = np.array(draws[dlt])
        arrm = np.array(mean_draws[dlt])
        lo, hi = np.percentile(arr, [2.5, 97.5]) if len(arr) > 20 else (np.nan, np.nan)
        rows.append(dict(
            panel="A", cohort="excc", scope="pooled", delta=dlt,
            gap_full=float(sum(Gs.values())), beta_CNA_TT=np.nan,
            mean_cna_TT=np.nan, n_tt_full=int(sum(len(data[c]["tt"]) for c in CANCERS)),
            n_tt_dna=int(sum(int(data[c]["tt"]["cna_l1"].notna().sum()) for c in CANCERS)),
            n_nn=int(sum(len(data[c]["nn"]) for c in CANCERS)),
            dna_pair_coverage=float(sum(int(data[c]["tt"]["cna_l1"].notna().sum()) for c in CANCERS)
                                    / sum(len(data[c]["tt"]) for c in CANCERS)),
            share=float(point), share_lo=float(lo), share_hi=float(hi),
            boot_ok=ok,
            share_mean_of_ratios=float(np.mean(arrm)) if len(arrm) else np.nan,
        ))
    return rows


# ----------------------------------------------------------------------
# Panel B: joint confounder model
# ----------------------------------------------------------------------
def panel_b(ap, comp_scores, rin_map):
    # attach composition delta + rin to ex-CC pairs
    d = ap[(ap["sample_a"].map(is_cc) | ap["sample_b"].map(is_cc)) == False].copy()

    def dz(cancer, pname, sid):
        return comp_scores.get((cancer, pname, sid), 0.0)

    d["d_overall4"] = [
        np.mean([abs(dz(r.cancer, p, r.sample_a) - dz(r.cancer, p, r.sample_b))
                 for p in PANELS])
        for r in d.itertuples()
    ]
    d["rin_a"] = d["sample_a"].map(rin_map)
    d["rin_b"] = d["sample_b"].map(rin_map)
    d["rin_pair"] = (d["rin_a"] + d["rin_b"]) / 2.0

    rows = []
    for c in CANCERS + ["pooled"]:
        sub = d if c == "pooled" else d[d["cancer"] == "TCGA-" + c]
        sub = sub.reset_index(drop=True)
        is_tt = (sub["pair_type"] == "TT").astype(float).values
        y = np.log(sub["kn"].values)
        dcomp = sub["d_overall4"].values
        cna_meas = sub["cna_l1"].values
        mx = np.nanmean(cna_meas[is_tt == 1])
        for variant in ["base", "rin"]:
            if variant == "rin":
                keep = ~(np.isnan(sub["rin_pair"].values))
                if keep.sum() < 500:
                    continue
                yv = y[keep]
                t_v = is_tt[keep]
                cv = cna_meas[keep]
                dv = dcomp[keep]
                rv = sub["rin_pair"].values[keep]
            else:
                yv, t_v, cv, dv, rv = y, is_tt, cna_meas, dcomp, None
            for dlt in [0.0, 0.02, 0.05]:
                cna_cov = np.where(np.isnan(cv), np.where(t_v == 1, mx, dlt), cv)
                cna_cov = np.where(t_v == 0, dlt, cna_cov)

                def fit(yv_, t_, c_, dc_, rv_, keep_mask=None):
                    cols = [np.ones(len(yv_)), t_, c_, dc_]
                    if rv_ is not None:
                        cols.append(rv_)
                    if c == "pooled":
                        cv_dum = pd.get_dummies(sub["cancer"]).values
                        if keep_mask is not None:
                            cv_dum = cv_dum[keep_mask]
                        cols.extend([cv_dum[:, j].astype(float)
                                     for j in range(1, cv_dum.shape[1])])
                    Xc = np.column_stack(cols)
                    beta = ols(Xc, yv_)
                    return beta, Xc

                keep_mask = keep if variant == "rin" else None
                beta, Xc = fit(yv, t_v, cna_cov, dv, rv, keep_mask)
                nms = ["int", "TT", "cna", "comp"] + (["rin"] if rv is not None else [])
                bmap = dict(zip(nms, beta))
                g = float(yv[t_v == 1].mean() - yv[t_v == 0].mean())
                c_cna = bmap["cna"] * (np.mean(cna_cov[t_v == 1]) - dlt)
                c_comp = bmap["comp"] * (np.mean(dv[t_v == 1]) - np.mean(dv[t_v == 0]))
                resid = bmap["TT"]
                if rv is not None:
                    c_rin = bmap["rin"] * (np.mean(rv[t_v == 1]) - np.mean(rv[t_v == 0]))
                    share_rin = c_rin / g
                else:
                    share_rin = np.nan
                share_other = 1.0 - (c_cna + c_comp + resid) / g - (0.0 if rv is None else c_rin / g)

                # cluster bootstrap
                bs_kept = keep if variant == "rin" else np.ones(len(sub), dtype=bool)
                sub_kept = sub[bs_kept]
                samples = np.array(sorted(set(sub_kept["sample_a"]) | set(sub_kept["sample_b"])))
                sidx = {s: i for i, s in enumerate(samples)}
                S = len(samples)
                ca = sub_kept["sample_a"].map(sidx).values
                cb = sub_kept["sample_b"].map(sidx).values
                rng = np.random.default_rng(
                    SEED + zlib.crc32(f"v2B|{c}|{variant}|{dlt}".encode()) % 10000)
                b_cna, b_comp, b_res = [], [], []
                ok = 0
                for _ in range(B):
                    draw = rng.integers(0, S, S)
                    cnt = np.bincount(draw, minlength=S).astype(float)
                    w = cnt[ca] * cnt[cb]
                    kw = w > 0
                    if kw.sum() < 200:
                        continue
                    try:
                        sw = np.sqrt(w[kw])
                        Xk = Xc[kw] * sw[:, None]
                        yk = yv[kw] * sw
                        XtX = Xk.T @ Xk
                        bb = np.linalg.solve(XtX, Xk.T @ yk)
                    except Exception:
                        continue
                    bm = dict(zip(nms, bb))
                    gk = wmean(yv[kw][t_v[kw] == 1], w[kw][t_v[kw] == 1]) - \
                        wmean(yv[kw][t_v[kw] == 0], w[kw][t_v[kw] == 0])
                    if not np.isfinite(gk) or abs(gk) < 1e-9:
                        continue
                    ok += 1
                    b_cna.append(bm["cna"] * (wmean(cna_cov[kw][t_v[kw] == 1], w[kw][t_v[kw] == 1]) - dlt) / gk)
                    b_comp.append(bm["comp"] * (wmean(dv[kw][t_v[kw] == 1], w[kw][t_v[kw] == 1]) - wmean(dv[kw][t_v[kw] == 0], w[kw][t_v[kw] == 0])) / gk)
                    b_res.append(bm["TT"] / gk)
                rows.append(dict(
                    scope=c, variant=variant, delta=dlt,
                    gap_obs=g, beta_TT=resid, beta_cna=bmap["cna"],
                    beta_comp=bmap["comp"], beta_rin=bmap.get("rin", np.nan),
                    share_cna=c_cna / g, share_comp=c_comp / g,
                    share_resid=resid / g,
                    share_rin=share_rin, share_other=share_other,
                    share_cna_lo=np.nanpercentile(b_cna, 2.5) if len(b_cna) > 20 else np.nan,
                    share_cna_hi=np.nanpercentile(b_cna, 97.5) if len(b_cna) > 20 else np.nan,
                    share_comp_lo=np.nanpercentile(b_comp, 2.5) if len(b_comp) > 20 else np.nan,
                    share_comp_hi=np.nanpercentile(b_comp, 97.5) if len(b_comp) > 20 else np.nan,
                    share_resid_lo=np.nanpercentile(b_res, 2.5) if len(b_res) > 20 else np.nan,
                    share_resid_hi=np.nanpercentile(b_res, 97.5) if len(b_res) > 20 else np.nan,
                    n_pairs=int(len(yv)),
                    n_rin_pairs=int((~np.isnan(sub['rin_pair'].values)).sum()) if variant == 'rin' else -1,
                    boot_ok=ok,
                ))
    return rows


def main():
    t0 = time.time()
    print("1. Loading pairs...")
    ap = load_pairs()
    print(f"   {len(ap)} pairs (TT+NN, k_n>0); "
          f"DNA TT pairs: {int(ap[ap.pair_type=='TT']['cna_l1'].notna().sum())}")

    print("2. Panel A (full-gap denominator)...")
    df_a_excc = panel_a(ap, "excc")
    df_a_incl = panel_a(ap, "inclusive")
    pooled_rows = panel_a_pooled(ap)
    df_all = pd.concat([df_a_excc, df_a_incl], ignore_index=True)
    df_all = pd.concat([df_all, pd.DataFrame(pooled_rows)], ignore_index=True)

    print("3. Panel scores (ex-CC standardization)...")
    comp_scores = compute_panel_scores()
    print(f"   {len(comp_scores)} panel scores, {time.time()-t0:.0f}s")

    print("4. Panel B (joint confounder model)...")
    rin_raw = json.load(open(RIN_CACHE, encoding="utf-8"))
    rin_map = {}
    for proj, dd in rin_raw.items():
        for bc, v in dd.items():
            rin_map[bc[:15]] = v
    rows_b = panel_b(ap, comp_scores, rin_map)
    df_b = pd.DataFrame(rows_b)

    out_a = os.path.join(RESULTS, "nc80_cna_share_v2.csv")
    out_b = os.path.join(RESULTS, "nc80_cna_joint_model.csv")
    df_all.to_csv(out_a, index=False)
    df_b.to_csv(out_b, index=False)

    rep = os.path.join(RESULTS, "nc80_cna_share_v2_report.txt")
    with open(rep, "w", encoding="utf-8") as fh:
        fh.write("NC80 CNA share v2 (full-gap denominator, direct bootstrap pooling)\n")
        fh.write("=" * 70 + "\n\n")
        fh.write("Panel A, ex-CC primary -- share(delta=0/0.02/0.05/0.10)\n\n")
        sub = df_all[(df_all.cohort == "excc") & (df_all.delta.isin(DELTAS_REPORT))]
        fh.write(sub[["scope", "delta", "gap_full", "beta_CNA_TT", "mean_cna_TT",
                      "n_tt_full", "n_tt_dna", "dna_pair_coverage",
                      "share", "share_lo", "share_hi"]].round(4).to_string(index=False))
        fh.write("\n\nPanel A, CC-inclusive (v1 continuity)\n\n")
        sub2 = df_all[(df_all.cohort == "inclusive") & (df_all.delta.isin(DELTAS_REPORT))]
        fh.write(sub2[["scope", "delta", "gap_full", "share", "share_lo", "share_hi"]].round(4).to_string(index=False))
        fh.write("\n\nPanel B joint model -- log k_n ~ is_TT + cna(delta) + d_overall4 (+RIN)\n\n")
        fh.write(df_b[["scope", "variant", "delta", "gap_obs", "beta_TT", "beta_cna",
                       "beta_comp", "share_cna", "share_comp", "share_resid",
                       "share_cna_lo", "share_cna_hi", "n_pairs"]].round(4).to_string(index=False))
    print(f"   wrote {out_a}, {out_b}, {rep}")
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
