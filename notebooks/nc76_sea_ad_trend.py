# -*- coding: utf-8 -*-
"""
nc76 (brain reviewer must-answer Q5): SEA-AD dose-response trend.

Per-donor omega (donor pseudobulk vs control-group centroid, k_f on the
pre-registered gene set / k_n on HRT HK) correlated with:
  (a) the Continuous Pseudo-progression Score (donor-level, SEA-AD metadata)
  (b) the ordinal ADNC ladder (Reference=0, Not AD=1, Low=2, Intermediate=3,
      High=4)
via Spearman, per cell class x gene set. Loading mirrors
notebooks/79_sea_ad_dam_positive_control.py.

Outputs: results/nc76_sea_ad_trend.csv / .txt
"""
import sys, os, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _paths import *

import numpy as np
import pandas as pd
import h5py
from scipy.stats import spearmanr
from cki.core import js_divergence

MIN_CELLS_PER_DONOR = 50
N_HVG = 5000
CTRL_LEVELS = ("Not AD", "Reference")

FILES = {
    "Microglia-PVM": DATA_DIR / "sea_ad" / "Microglia-PVM_MTG.h5ad",
    "Astrocyte": DATA_DIR / "sea_ad" / "Astrocyte_MTG.h5ad",
}
GENE_SETS = {
    "DAM_core": ["APOE", "LPL", "TREM2", "TYROBP", "CST7", "CLEC7A", "ITGAX",
                 "SPP1", "CSF1", "CCL2", "CTSB", "CTSD", "CD9", "B2M", "LYZ",
                 "FTL", "APOC1", "TGFBR1"],
    "Homeostatic_microglia": ["P2RY12", "TMEM119", "SELPLG", "OLFML3",
                              "CX3CR1", "CSF1R", "SALL1", "MEF2A", "FCRLS",
                              "TGFBR1"],
    "Pan_reactive_astro": ["GFAP", "SERPINA3", "CXCL10", "HSPB1", "STEAP4",
                           "DUSP15", "TIMP1", "HIVEP2", "S1PR3", "CD44"],
    "A1_astro": ["C2", "C3", "SERPING1", "GBGT1", "AMIGO2", "HLA-A", "HLA-B",
                 "HLA-C"],
    "A2_astro": ["EMP1", "CLCF1", "OSMR", "PTX3", "SPHK1", "TGM1"],
}
ADNC_ORD = {"Reference": 0, "Not AD": 1, "Low": 2, "Intermediate": 3, "High": 4}
OUT_CSV = Path("results/nc76_sea_ad_trend.csv")
OUT_TXT = Path("results/nc76_sea_ad_trend.txt")

hk_human = set(pd.read_csv(HK_FILE, sep=";", engine="python")
               ["Human"].dropna().astype(str))

def read_cat(obj, name):
    g = obj[name]
    if isinstance(g, h5py.Dataset):
        return np.array([x.decode() if isinstance(x, bytes) else str(x)
                         for x in g[:]], dtype=object)
    cats = [x.decode() if isinstance(x, bytes) else str(x)
            for x in g["categories"][:]]
    return np.array(cats, dtype=object)[g["codes"][:]]

lines = []
def log(msg=""):
    print(msg, flush=True)
    lines.append(str(msg))

rows = []
for ct, path in FILES.items():
    log(f"\n== {ct}")
    if not path.exists():
        log("  MISSING - skip"); continue
    with h5py.File(path, "r") as f:
        X = f["X"]
        ip = X["indptr"][:]
        dat = X["data"]; ind = X["indices"]
        n_cells = len(ip) - 1
        var_gene = read_cat(f["var"], "feature_name").astype(str)
        n_genes = len(var_gene)
        adnc = read_cat(f["obs"], "ADNC").astype(str)
        donors = read_cat(f["obs"], "donor_id").astype(str)
        prog = np.array([float(x) for x in
                         read_cat(f["obs"], "Continuous Pseudo-progression Score")])
        d_adnc, d_prog, d_cells = {}, {}, {}
        for d, a, p in zip(donors, adnc, prog):
            d_adnc.setdefault(d, a); d_prog.setdefault(d, p)
            d_cells[d] = d_cells.get(d, 0) + 1
        keep_donors = sorted([d for d in d_cells if d_cells[d] >= MIN_CELLS_PER_DONOR])
        kept = set(keep_donors)
        log(f"  donors kept: {len(keep_donors)} "
            f"({', '.join(f'{a}:{sum(1 for d in keep_donors if d_adnc[d]==a)}' for a in sorted(set(d_adnc.values())))})")

        hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                                     if s in hk_human}), dtype=int)
        # gene sums for HVG
        gene_sums = np.zeros(n_genes)
        np.add.at(gene_sums, ind[:], dat[:])
        gene_means = gene_sums / n_cells
        mask = np.ones(n_genes, bool); mask[hk_global] = False
        m = gene_means.copy(); m[~mask] = -np.inf
        hvg = np.argsort(m)[-N_HVG:][::-1]
        sym_global = {}
        for i, s in enumerate(var_gene):
            if s:
                sym_global.setdefault(s, []).append(i)
        set_global = {}
        for name, genes in GENE_SETS.items():
            idx = []
            for g in genes:
                idx.extend(sym_global.get(g, []))
            if idx:
                set_global[name] = np.array(sorted(set(idx)), dtype=int)
        extra = np.unique(np.concatenate(list(set_global.values())))
        keep = np.sort(np.union1d(np.union1d(hk_global, hvg), extra))
        hk_r = np.where(np.isin(keep, hk_global))[0]
        sets = {name: np.where(np.isin(keep, gidx))[0]
                for name, gidx in set_global.items()}

        gene_map = np.full(n_genes, -1, dtype=np.int32)
        gene_map[keep] = np.arange(len(keep), dtype=np.int32)
        sums = {d: np.zeros(len(keep)) for d in kept}
        counts = {d: 0 for d in kept}
        mapped = gene_map[ind[:]]
        okm = mapped >= 0
        for i in range(n_cells):
            d = donors[i]
            if d not in kept:
                continue
            s0, s1 = int(ip[i]), int(ip[i + 1])
            if s1 > s0:
                mo = okm[s0:s1]
                if mo.any():
                    gi = mapped[s0:s1][mo]
                    sums[d][gi] += dat[s0:s1][mo].astype(np.float64)
            counts[d] += 1
    PB = {}
    for d in keep_donors:
        raw = sums[d] / max(counts[d], 1)
        tot = raw.sum()
        PB[d] = np.log1p(raw / tot * 1e4) if tot > 0 else raw
    del sums
    gc.collect()

    ctrl = [d for d in keep_donors if d_adnc[d] in CTRL_LEVELS]
    centroid = np.mean(np.stack([PB[d] for d in ctrl]), axis=0)
    log(f"  control centroid over {len(ctrl)} donors")

    for name, idx in sets.items():
        if len(idx) == 0:
            continue
        om, pr, ad = [], [], []
        for d in keep_donors:
            kf = js_divergence(PB[d][idx], centroid[idx])
            kn = js_divergence(PB[d][hk_r], centroid[hk_r])
            om.append(kf / kn if kn > 1e-15 else np.nan)
            pr.append(d_prog[d]); ad.append(ADNC_ORD.get(d_adnc[d], np.nan))
        om = np.array(om); pr = np.array(pr); ad = np.array(ad)
        ok = ~np.isnan(om)
        rho_p, p_p = spearmanr(om[ok], pr[ok])
        ok2 = ok & ~np.isnan(ad)
        rho_a, p_a = spearmanr(om[ok2], ad[ok2])
        log(f"  {name}: Spearman(omega, progression) = {rho_p:.3f} "
            f"(P={p_p:.2e}); vs ADNC ordinal = {rho_a:.3f} (P={p_a:.2e})")
        rows.append({"cell_class": ct, "gene_set": name, "n_donors": int(ok.sum()),
                     "rho_progression": rho_p, "p_progression": p_p,
                     "rho_adnc": rho_a, "p_adnc": p_a})

pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
log("\nDONE")
