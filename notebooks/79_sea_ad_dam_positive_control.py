"""
CKI SEA-AD DAM Positive Control (D task)
=========================================
Tests whether CKI recovers the known AD disease-associated microglia
(DAM) and reactive astrocyte signals in the SEA-AD MTG atlas —
converting methodological credibility into a named pathological
discovery.

Design (mirrors the TCGA tumor-vs-normal CKI analysis):
  1. Per-donor pseudobulks within each cell class (Microglia-PVM,
     Astrocyte; MTG, single region — no region confound)
  2. Groups by ADNC: control = 'Not AD' + 'Reference' donors vs
     case = 'High' ADNC donors
  3. k_n = JS on HRT housekeeping genes (baseline)
  4. k_f^(S) = JS on externally pre-registered gene sets:
       - DAM core (Keren-Shaul 2017; Krasemann 2017 human orthologs)
       - Homeostatic microglia (Krasemann 2017)
       - Pan-reactive / A1 / A2 astrocyte (Liddelow 2017)
     omega_S = k_f / k_n for AD-vs-control donor pairs
  5. Empirical null: size-matched random non-HK gene sets (N_NULL)
  6. Severity ladder: mean omega per ADNC level
     (Reference/NotAD -> Low -> Intermediate -> High) — adjacent
     contrasts should increase if CKI tracks disease severity

Data: data/sea_ad/{Microglia-PVM_MTG,Astrocyte_MTG}.h5ad
      (CELLxGENE collection 1ca90a2d-2943-483d-b678-b809bf464c30)

Outputs:
  results/sea_ad_dam_positive_control.csv
  results/sea_ad_severity_ladder.csv
  results/sea_ad_dam_report.md
"""

import sys, os, time, gc, json
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
from cki.bootstrap import benjamini_hochberg


# === Config ===
RANDOM_SEED = 42
N_HVG = 5000
MIN_CELLS_PER_DONOR = 50
N_NULL = 2000

CTRL_LEVELS = {"Not AD", "Reference"}
CASE_LEVEL = "High"

# Pre-registered external gene sets (human symbols)
GENE_SETS = {
    # Disease-associated microglia core (Keren-Shaul et al. 2017 Cell;
    # Krasemann et al. 2017 ImmunoRev — human orthologs)
    "DAM_core": [
        "APOE", "LPL", "TREM2", "TYROBP", "CST7", "CLEC7A", "ITGAX",
        "SPP1", "CSF1", "CCL2", "CTSB", "CTSD", "CD9", "B2M", "LYZ",
        "FTL", "APOC1", "TGFBR1",
    ],
    # Homeostatic microglia signature (Krasemann et al. 2017)
    "Homeostatic_microglia": [
        "P2RY12", "TMEM119", "SELPLG", "OLFML3", "CX3CR1", "CSF1R",
        "SALL1", "MEF2A", "FCRLS", "TGFBR1",
    ],
    # Pan-reactive astrocytes (Liddelow et al. 2017 Nature, human)
    "Pan_reactive_astro": [
        "GFAP", "SERPINA3", "CXCL10", "HSPB1", "STEAP4", "DUSP15",
        "TIMP1", "HIVEP2", "S1PR3", "CD44",
    ],
    # A1 neurotoxic astrocytes (Liddelow et al. 2017)
    "A1_astro": [
        "C2", "C3", "SERPING1", "GBGT1", "AMIGO2", "HLA-A", "HLA-B",
        "HLA-C",
    ],
    # A2 neuroprotective astrocytes (Liddelow et al. 2017)
    "A2_astro": [
        "EMP1", "CLCF1", "OSMR", "PTX3", "SPHK1", "TGM1",
    ],
}

OUT_CSV = Path("results/sea_ad_dam_positive_control.csv")
OUT_LADDER = Path("results/sea_ad_severity_ladder.csv")
OUT_MD = Path("results/sea_ad_dam_report.md")

FILES = {
    "Microglia-PVM": DATA_DIR / "sea_ad" / "Microglia-PVM_MTG.h5ad",
    "Astrocyte": DATA_DIR / "sea_ad" / "Astrocyte_MTG.h5ad",
}

rng = np.random.RandomState(RANDOM_SEED)


def read_cat(obj, name):
    """Read h5ad obs/var column (categorical or string array)."""
    g = obj[name]
    if isinstance(g, h5py.Dataset):
        return np.array([x.decode() if isinstance(x, bytes) else str(x)
                         for x in g[:]], dtype=object)
    cats = [x.decode() if isinstance(x, bytes) else str(x)
            for x in g["categories"][:]]
    codes = g["codes"][:]
    return np.array(cats, dtype=object)[codes]


def pairwise_js_means(PB, idx_a, idx_b, gene_idx):
    """Mean JS between group-A and group-B pseudobulks on gene subset."""
    vals = []
    for i in idx_a:
        pi = PB[i]
        for j in idx_b:
            pj = PB[j]
            vals.append(js_divergence(pi[gene_idx], pj[gene_idx]))
    return float(np.mean(vals))


def main():
    hk_df = pd.read_csv(HK_FILE, sep=";", engine="python")
    hk_human = set(hk_df["Human"].dropna().astype(str))
    print(f"HRT Atlas: {len(hk_human)} human HK genes")

    rows = []
    ladder_rows = []

    for ct, path in FILES.items():
        print("\n" + "=" * 60)
        print(f"{ct}: {path}")
        print("=" * 60)
        if not path.exists():
            print("  MISSING — skip")
            continue
        with h5py.File(path, "r") as f:
            X = f["X"]
            indptr = X["indptr"][:]
            n_cells = indptr.shape[0] - 1
            n_genes = f["X"]["indices"][:1]  # placeholder
            var_gene = read_cat(f["var"], "feature_name")
            n_genes = len(var_gene)
            adnc = read_cat(f["obs"], "ADNC").astype(str)
            donors = read_cat(f["obs"], "donor_id").astype(str)
            prog = read_cat(f["obs"], "Continuous Pseudo-progression Score")
            prog = np.array([float(x) for x in prog])

            # donor -> ADNC / progression (mode)
            d_adnc, d_prog, d_cells = {}, {}, {}
            for d, a, p in zip(donors, adnc, prog):
                d_adnc.setdefault(d, a)
                d_prog.setdefault(d, p)
                d_cells[d] = d_cells.get(d, 0) + 1
            keep_donors = [d for d in d_cells if d_cells[d] >= MIN_CELLS_PER_DONOR]
            print(f"  cells={n_cells} genes={n_genes} "
                  f"donors={len(d_adnc)} (kept {len(keep_donors)} "
                  f">= {MIN_CELLS_PER_DONOR} cells)")

            ctrl = [d for d in keep_donors if d_adnc[d] in CTRL_LEVELS]
            case = [d for d in keep_donors if d_adnc[d] == CASE_LEVEL]
            print(f"  control donors (NotAD/Reference): {len(ctrl)}")
            print(f"  case donors (High ADNC): {len(case)}")
            if len(ctrl) < 4 or len(case) < 4:
                print("  SKIP: too few donors in a group")
                continue

            # Global gene means for HVG selection (non-HK top-5000)
            hk_global = np.array(sorted({i for i, s in enumerate(var_gene)
                                         if s in hk_human}), dtype=int)
            print(f"  HK genes matched: {len(hk_global)}")
            gene_sums = np.zeros(n_genes, dtype=np.float64)
            data = X["data"]
            indices = X["indices"]
            np.add.at(gene_sums, indices[:], data[:])
            gene_means = gene_sums / n_cells
            mask = np.ones(n_genes, dtype=bool)
            mask[hk_global] = False
            m = gene_means.copy()
            m[~mask] = -np.inf
            hvg = np.argsort(m)[-N_HVG:][::-1]
            # Map pre-registered gene sets to GLOBAL indices first — these
            # are externally defined (no circularity), so unlike the
            # data-driven k_f they must NOT be truncated by the HVG filter
            # (LPL/CST7/CSF1/CCL2/CD9/LYZ rank 9k-16k by mean expression but
            # are precisely the DAM markers, induced only in disease).
            sym_global = {}
            for i, s in enumerate(var_gene):
                if pd.notna(s):
                    sym_global.setdefault(s, []).append(i)
            set_global = {}
            for name, genes in GENE_SETS.items():
                idx = []
                for g in genes:
                    idx.extend(sym_global.get(g, []))
                if idx:
                    set_global[name] = np.array(sorted(set(idx)), dtype=int)
            extra = np.unique(np.concatenate(
                [v for v in set_global.values()])) if set_global else np.array([], dtype=int)
            keep = np.sort(np.union1d(np.union1d(hk_global, hvg), extra))
            is_hk = np.isin(keep, hk_global)
            hk_r = np.where(is_hk)[0]
            nh_r = np.where(~is_hk)[0]
            # null pool: non-HK reduced positions EXCLUDING pre-registered genes
            set_pos_all = np.unique(np.concatenate(
                [np.where(np.isin(keep, v))[0] for v in set_global.values()])) \
                if set_global else np.array([], dtype=int)
            null_pool = np.setdiff1d(nh_r, set_pos_all)
            # per-set positions in the reduced set
            sets = {}
            for name, gidx in set_global.items():
                pos = np.where(np.isin(keep, gidx))[0]
                if len(pos):
                    sets[name] = pos
            print(f"  reduced: {len(keep)} (HK {len(hk_r)} + HVG {N_HVG} "
                  f"+ pre-registered {len(extra)}; null pool {len(null_pool)})")
            for name, idx in sets.items():
                print(f"  set {name}: {len(idx)} genes mapped")

            # Per-donor pseudobulks on the reduced set
            gene_map = np.full(n_genes, -1, dtype=np.int32)
            gene_map[keep] = np.arange(len(keep), dtype=np.int32)
            kept_set = set(keep_donors)
            donor_pb = {}
            donor_idx_rows = {}
            row_donor = np.empty(n_cells, dtype=object)
            for i, d in enumerate(donors):
                row_donor[i] = d
            with h5py.File(path, "r") as f2:
                X2 = f2["X"]
                ip = X2["indptr"][:]
                dat = X2["data"]
                ind = X2["indices"]
                # accumulate per-donor sums on reduced genes
                sums = {d: np.zeros(len(keep), dtype=np.float64) for d in kept_set}
                counts = {d: 0 for d in kept_set}
                mapped = gene_map[ind[:]]
                ok = mapped >= 0
                # loop rows
                for i in range(n_cells):
                    d = row_donor[i]
                    if d not in kept_set:
                        continue
                    s0, s1 = int(ip[i]), int(ip[i + 1])
                    if s1 == s0:
                        counts[d] += 1
                        continue
                    m_ok = ok[s0:s1]
                    if m_ok.any():
                        gi = mapped[s0:s1][m_ok]
                        vv = dat[s0:s1][m_ok].astype(np.float64)
                        sums[d][gi] += vv
                    counts[d] += 1
            for d in kept_set:
                raw = sums[d] / max(counts[d], 1)
                tot = raw.sum()
                donor_pb[d] = (np.log1p(raw / tot * 1e4)
                               if tot > 0 else raw)
            del sums
            gc.collect()

            PB = np.stack([donor_pb[d] for d in sorted(donor_pb)])
            pb_names = sorted(donor_pb)
            pb_index = {d: i for i, d in enumerate(pb_names)}
            idx_ctrl = [pb_index[d] for d in ctrl]
            idx_case = [pb_index[d] for d in case]

            # k_n: AD-vs-control baseline on HK
            kn_ac = pairwise_js_means(PB, idx_case, idx_ctrl, hk_r)
            kn_within = 0.5 * (
                pairwise_js_means(PB, idx_case, idx_case, hk_r) +
                pairwise_js_means(PB, idx_ctrl, idx_ctrl, hk_r))
            print(f"  k_n AD-vs-ctrl={kn_ac:.6e} within={kn_within:.6e}")

            # Pre-registered sets
            for name, idx in sets.items():
                kf_ac = pairwise_js_means(PB, idx_case, idx_ctrl, idx)
                kf_within = 0.5 * (
                    pairwise_js_means(PB, idx_case, idx_case, idx) +
                    pairwise_js_means(PB, idx_ctrl, idx_ctrl, idx))
                om_ac = kf_ac / kn_ac
                om_w = kf_within / kn_within
                # size-bucketed random null
                size = len(idx)
                nulls = np.empty(N_NULL)
                for r_ in range(N_NULL):
                    ridx = rng.choice(null_pool, size=size, replace=False)
                    kf_n = pairwise_js_means(PB, idx_case, idx_ctrl, ridx)
                    nulls[r_] = kf_n / kn_ac
                p_emp = float((1 + np.sum(nulls >= om_ac)) / (1 + N_NULL))
                rows.append({
                    "cell_class": ct, "gene_set": name, "n_genes": size,
                    "omega_ad_vs_ctrl": om_ac, "omega_within": om_w,
                    "ratio_ad_within": om_ac / om_w if om_w > 0 else np.nan,
                    "kn_ad_vs_ctrl": kn_ac,
                    "null_mean": float(nulls.mean()),
                    "null_sd": float(nulls.std()),
                    "null_max": float(nulls.max()),
                    "p_emp": p_emp,
                })
                print(f"  {name}: omega_AC={om_ac:.2f} omega_within={om_w:.2f} "
                      f"null={nulls.mean():.2f}±{nulls.std():.2f} p={p_emp:.4g}")

            # Severity ladder for DAM_core / Pan_reactive (whichever present)
            ladder_targets = [n for n in ("DAM_core", "Pan_reactive_astro",
                                          "Homeostatic_microglia")
                              if n in sets]
            levels = ["Not AD", "Reference", "Low", "Intermediate", "High"]
            for name in ladder_targets:
                idx = sets[name]
                for lvl in levels:
                    ds = [d for d in keep_donors if d_adnc[d] == lvl]
                    if len(ds) < 3:
                        continue
                    ii = [pb_index[d] for d in ds]
                    kf_w = pairwise_js_means(PB, ii, ii, idx)
                    kn_w = pairwise_js_means(PB, ii, ii, hk_r)
                    ladder_rows.append({
                        "cell_class": ct, "gene_set": name, "level": lvl,
                        "n_donors": len(ds),
                        "mean_progression": float(np.mean([d_prog[d] for d in ds])),
                        "omega_within": kf_w / kn_w if kn_w > 0 else np.nan,
                    })

    # === Save + report ===
    print("\n" + "=" * 60)
    print("Saving")
    print("=" * 60)
    df = pd.DataFrame(rows)
    if len(df):
        df["q_bh"] = benjamini_hochberg(df["p_emp"].values)
        df = df.sort_values(["cell_class", "p_emp"])
        df.to_csv(OUT_CSV, index=False)
        print(f"  {OUT_CSV}: {len(df)} rows")
    dl = pd.DataFrame(ladder_rows)
    dl.to_csv(OUT_LADDER, index=False)
    print(f"  {OUT_LADDER}: {len(dl)} rows")

    lines = ["# SEA-AD DAM Positive Control", "",
             f"- Groups: control={sorted(CTRL_LEVELS)} vs case={CASE_LEVEL}",
             f"- Null: {N_NULL} size-matched random non-HK gene sets",
             "", "## Pre-registered gene sets (AD vs control omega)", "",
             "| cell_class | gene_set | n_genes | omega_AC | omega_within | ratio | null_mean | p_emp | q_bh |",
             "|---|---|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        lines.append(
            f"| {r.cell_class} | {r.gene_set} | {r.n_genes} | "
            f"{r.omega_ad_vs_ctrl:.2f} | {r.omega_within:.2f} | "
            f"{r.ratio_ad_within:.2f} | {r.null_mean:.2f} | "
            f"{r.p_emp:.4g} | {r.q_bh:.3g} |")
    lines += ["", "## Severity ladder (within-group omega by ADNC)", "",
              "| cell_class | gene_set | level | n_donors | mean_prog | omega_within |",
              "|---|---|---|---|---|---|"]
    for _, r in dl.iterrows():
        lines.append(f"| {r.cell_class} | {r.gene_set} | {r.level} | "
                     f"{r.n_donors} | {r.mean_progression:.2f} | "
                     f"{r.omega_within:.2f} |")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"  {OUT_MD}")
    print("DONE")


if __name__ == "__main__":
    main()
