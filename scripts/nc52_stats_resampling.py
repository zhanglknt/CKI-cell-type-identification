"""nc52 statistical resampling for R1 (stats) / R2 (single-cell) major revisions.

Sections
--------
A1  Two-stage bootstrap of the split-half calibration baseline (mean omega=7.70):
    stage 1 resamples the 6 FACS populations, stage 2 resamples the 50
    split-half values within each drawn population. B=5,000, seed 42.
    Triangulated against the t-interval on 6 population means and the
    leave-one-population-out (LOPO) range. Also quantifies what CI widening
    implies for the effective precision of omega_cal = omega / 7.70 (Note 3).

A2b Entry-clustered bootstrap of the Tabula Sapiens metric correlations:
    4,851 pairs are nested in 99 cell-type pseudobulk entries (dyadic data).
    Resample entries with replacement; pair weight = m_i * m_j (product of
    endpoint multiplicities); weighted Spearman recomputed per replicate.
    B=5,000, seed 42. Replaces independence-assuming P values.

A4  (a) AUC CI by two methods: DeLong and module-seed cluster bootstrap
    (3 clusters: seeds 42/137/2024; signal side clustered, neutral side iid).
    (b) Sensitivity at fixed specificity {0.90, 0.95, 0.99} (matched
    thresholds from the neutral distribution).
    (c) Per-background AUC (marrow B cell vs keratinocyte stem cell).

D   (a) omega-vs-k_f benchmark-by-benchmark comparison table from
    authoritative results files.
    (b) "Mathematical floor" of the omega-k_f correlation: permute k_n
    (B=1,000, seed 42), recompute omega_perm = k_f / k_n_perm, and measure
    how much omega-k_f correlation survives k_n randomization.
    (c) scDist original R implementation feasibility: R unavailable on this
    machine -> documented; fairness wording for the Python approximation.

Outputs (results/):
    nc52_stats_baseline_twostage_bootstrap.csv / .json
    nc52_stats_tabula_entrycluster.csv
    nc52_stats_auc_ci_methods.csv
    nc52_stats_omega_vs_kf_realdata.csv
    nc52_stats_omega_kf_math_floor.csv
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr, t as t_dist

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SEED = 42
B = 5000
rng = np.random.default_rng(SEED)

METRIC_COLS = ["omega", "k_f", "k_n", "k_total", "cosine", "kf_over_kt"]


# ============================================================
# A1: two-stage bootstrap of the 7.70 split-half baseline
# ============================================================
def a1():
    print("[A1] two-stage bootstrap of split-half baseline ...", flush=True)
    df = pd.read_csv(RESULTS / "mouse_splithalf_v44.csv")
    df["pop"] = df["tissue"] + "|" + df["cell_type"]
    pops = sorted(df["pop"].unique())
    assert len(pops) == 6
    mat = np.stack([df.loc[df["pop"] == p, "omega"].to_numpy() for p in pops])
    assert mat.shape == (6, 50)

    pop_means = mat.mean(axis=1)
    obs_mean = float(mat.mean())

    # two-stage bootstrap: resample 6 pops, then 50 values within each draw
    boot = np.empty(B)
    for b in range(B):
        pi = rng.integers(0, 6, size=6)
        vi = rng.integers(0, 50, size=(6, 50))
        boot[b] = mat[pi[:, None], vi].mean()
    ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])

    # triangulation 1: t-interval on the 6 population means (df=5)
    se = pop_means.std(ddof=1) / np.sqrt(6)
    tcrit = t_dist.ppf(0.975, df=5)
    t_lo, t_hi = obs_mean - tcrit * se, obs_mean + tcrit * se

    # triangulation 2: leave-one-population-out
    lopo = sorted(float((mat.sum() - mat[i].sum()) / 250.0) for i in range(6))

    # single-stage (naive, 300 iid) bootstrap for contrast with the old CI
    flat = mat.ravel()
    naive = np.empty(B)
    for b in range(B):
        naive[b] = rng.choice(flat, size=300, replace=True).mean()
    naive_lo, naive_hi = np.percentile(naive, [2.5, 97.5])

    # omega_cal = omega / baseline: impact of CI widening on precision
    # relative half-width of baseline CI -> relative uncertainty of omega_cal
    rel_half_old = (8.02 - 7.37) / 2 / obs_mean
    rel_half_new = float((ci_hi - ci_lo) / 2 / obs_mean)
    # for an omega_cal value of c, the induced 95% range is c * [m/hi, m/lo]
    def cal_range(c, lo, hi):
        return [c * obs_mean / hi, c * obs_mean / lo]

    rows = [
        {"method": "two_stage_bootstrap_B5000", "mean": obs_mean,
         "ci_lo": round(float(ci_lo), 4), "ci_hi": round(float(ci_hi), 4),
         "note": "stage1: resample 6 populations; stage2: resample 50 split-half values within drawn population"},
        {"method": "single_stage_iid300_bootstrap_B5000", "mean": obs_mean,
         "ci_lo": round(float(naive_lo), 4), "ci_hi": round(float(naive_hi), 4),
         "note": "treats 300 split-half values as independent (close to published [7.37, 8.02]); anti-conservative because values are nested in 6 populations"},
        {"method": "t_interval_6pop_means_df5", "mean": obs_mean,
         "ci_lo": round(float(t_lo), 4), "ci_hi": round(float(t_hi), 4),
         "note": "t interval on the 6 population means (n=6, df=5)"},
        {"method": "leave_one_population_out_range", "mean": obs_mean,
         "ci_lo": round(lopo[0], 4), "ci_hi": round(lopo[-1], 4),
         "note": "range of the 6 LOPO means (not a CI; sensitivity diagnostic)"},
    ]
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "nc52_stats_baseline_twostage_bootstrap.csv", index=False)

    payload = {
        "seed": SEED, "B": B,
        "n_populations": 6, "n_splits_per_population": 50,
        "observed_mean": round(obs_mean, 4),
        "population_means_sd": {
            p: {"mean": round(float(mat[i].mean()), 4),
                "sd": round(float(mat[i].std(ddof=1)), 4)}
            for i, p in enumerate(pops)},
        "two_stage_ci95": [round(float(ci_lo), 4), round(float(ci_hi), 4)],
        "single_stage_iid300_ci95": [round(float(naive_lo), 4), round(float(naive_hi), 4)],
        "published_ci95_v44": [7.37, 8.02],
        "t_ci95_6pop": [round(float(t_lo), 4), round(float(t_hi), 4)],
        "lopo_values": [round(v, 4) for v in lopo],
        "omega_cal_precision": {
            "definition": "omega_cal = omega / baseline_mean",
            "relative_halfwidth_published": round(float(rel_half_old), 4),
            "relative_halfwidth_two_stage": round(rel_half_new, 4),
            "example_omega_cal_1_induced_range_two_stage": [round(v, 3) for v in cal_range(1.0, ci_lo, ci_hi)],
            "example_omega_cal_2_induced_range_two_stage": [round(v, 3) for v in cal_range(2.0, ci_lo, ci_hi)],
            "interpretation": ("A two-stage 95% CI half-width of ~"
                               f"{rel_half_new*100:.1f}% of the baseline means omega_cal carries "
                               "roughly 1 significant digit of calibration precision; reporting "
                               "omega_cal to more than ~0.1 absolute resolution overstates the "
                               "calibration constant (supports Note 3 argument)."),
        },
    }
    with open(RESULTS / "nc52_stats_baseline_twostage_bootstrap.json", "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"  observed mean {obs_mean:.3f}; two-stage 95% CI [{ci_lo:.3f}, {ci_hi:.3f}]")
    print(f"  t-interval (6 pop means) [{t_lo:.3f}, {t_hi:.3f}]; LOPO [{lopo[0]:.3f}, {lopo[-1]:.3f}]")
    return payload


# ============================================================
# A2b: entry-clustered bootstrap of Tabula Sapiens correlations
# ============================================================
def weighted_corr(rx, ry, w):
    """Weighted Pearson correlation on precomputed rank vectors."""
    mx = np.average(rx, weights=w)
    my = np.average(ry, weights=w)
    cov = np.average((rx - mx) * (ry - my), weights=w)
    vx = np.average((rx - mx) ** 2, weights=w)
    vy = np.average((ry - my) ** 2, weights=w)
    return cov / np.sqrt(vx * vy)


def a2b():
    print("[A2b] entry-clustered bootstrap of Tabula Sapiens correlations ...", flush=True)
    df = pd.read_csv(RESULTS / "phase35_all_metrics_pairs.csv")
    df["e_i"] = df["organ_i"] + "|" + df["ct_i"]
    df["e_j"] = df["organ_j"] + "|" + df["ct_j"]
    entries = sorted(set(df["e_i"]) | set(df["e_j"]))
    assert len(entries) == 99 and len(df) == 4851
    eidx = {e: k for k, e in enumerate(entries)}
    pi = df["e_i"].map(eidx).to_numpy()
    pj = df["e_j"].map(eidx).to_numpy()

    metrics = ["js_raw", "spearman_dist", "cosine_dist", "marker_jaccard_dist"]
    r_omega = rankdata(df["omega"].to_numpy())
    ranks = {m: rankdata(df[m].to_numpy()) for m in metrics}

    obs = {m: float(spearmanr(df["omega"], df[m]).statistic) for m in metrics}

    # naive (pair-level iid) bootstrap for contrast
    n = len(df)
    boot = {m: np.empty(B) for m in metrics}
    naive = {m: np.empty(B) for m in metrics}
    for b in range(B):
        counts = np.bincount(rng.integers(0, 99, size=99), minlength=99)
        w = (counts[pi] * counts[pj]).astype(float)
        for m in metrics:
            boot[m][b] = weighted_corr(r_omega, ranks[m], w)
        ii = rng.integers(0, n, size=n)
        for m in metrics:
            naive[m][b] = weighted_corr(r_omega[ii], ranks[m][ii], np.ones(n))

    rows = []
    for m in metrics:
        lo, hi = np.percentile(boot[m], [2.5, 97.5])
        nlo, nhi = np.percentile(naive[m], [2.5, 97.5])
        rows.append({
            "metric": m, "observed_spearman_r": round(obs[m], 4),
            "cluster_boot_ci_lo": round(float(lo), 4),
            "cluster_boot_ci_hi": round(float(hi), 4),
            "naive_pair_boot_ci_lo": round(float(nlo), 4),
            "naive_pair_boot_ci_hi": round(float(nhi), 4),
            "cluster_boot_se": round(float(boot[m].std(ddof=1)), 4),
            "naive_boot_se": round(float(naive[m].std(ddof=1)), 4),
            "note": ("entry-cluster bootstrap (99 pseudobulk entries, pair weight = "
                     "product of endpoint multiplicities), B=5000, seed=42; "
                     "replaces independence-assuming P values (P < 1e-145)"),
        })
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "nc52_stats_tabula_entrycluster.csv", index=False)
    for r in rows:
        print(f"  omega vs {r['metric']}: r={r['observed_spearman_r']:.3f} "
              f"cluster-CI [{r['cluster_boot_ci_lo']:.3f}, {r['cluster_boot_ci_hi']:.3f}]")
    return rows


# ============================================================
# A4: AUC CI methods + matched-threshold sensitivity + per-background
# ============================================================
def compute_midrank(x):
    J = np.argsort(x, kind="mergesort")
    Z = x[J]
    N = len(x)
    T = np.zeros(N)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = 0.5 * (i + j - 1) + 1
        i = j
    T2 = np.empty(N)
    T2[J] = T
    return T2


def delong_auc(pos, neg):
    """AUC and DeLong variance for one score vector."""
    m, n = len(pos), len(neg)
    allx = np.r_[pos, neg]
    tx = compute_midrank(pos)
    ty = compute_midrank(neg)
    tz = compute_midrank(allx)
    auc = tz[:m].sum() / m / n - (m + 1.0) / 2.0 / n
    v01 = (tz[:m] - tx) / n
    v10 = 1.0 - (tz[m:] - ty) / m
    sx = np.var(v01, ddof=1)
    sy = np.var(v10, ddof=1)
    var = sx / m + sy / n
    return float(auc), float(var)


def rank_auc(pos, neg):
    scores = np.r_[pos, neg]
    r = compute_midrank(scores)
    m, n = len(pos), len(neg)
    return float(r[:m].sum() / m / n - (m + 1.0) / 2.0 / n)


def load_sim(path):
    raw = pd.read_csv(path)
    sig = raw[(raw["series"] == "signal") & (raw["delta"] >= 0.25)]
    neu = raw[raw["series"].isin(["neutral_hk", "neutral_global"])]
    return raw, sig, neu


def a4():
    print("[A4] AUC CI methods + sensitivity + per-background ...", flush=True)
    rows = []

    raw1, sig1, neu1 = load_sim(RESULTS / "groundtruth_simulation_raw.csv")
    raw2, sig2, neu2 = load_sim(RESULTS / "groundtruth_simulation_background2_raw.csv")

    # ---- (a) AUC with DeLong CI and module-seed cluster bootstrap CI ----
    for m in METRIC_COLS:
        pos = sig1[m].to_numpy()
        neg = neu1[m].to_numpy()
        auc, var = delong_auc(pos, neg)
        d_lo, d_hi = auc - 1.96 * np.sqrt(var), auc + 1.96 * np.sqrt(var)

        # cluster bootstrap: resample 3 module seeds for the signal side,
        # iid resample the neutral side
        seeds = np.array([42, 137, 2024])
        sig_by_seed = {s: sig1.loc[sig1["module_seed"] == s, m].to_numpy() for s in seeds}
        cb = np.empty(B)
        n_pos, n_neg = len(pos), len(neg)
        for b in range(B):
            ds = rng.choice(seeds, size=3, replace=True)
            p = np.concatenate([sig_by_seed[s] for s in ds])
            # keep replicate count comparable: subsample to n_pos if needed
            if len(p) > n_pos:
                p = p[rng.integers(0, len(p), size=n_pos)]
            nn = neg[rng.integers(0, n_neg, size=n_neg)]
            cb[b] = rank_auc(p, nn)
        c_lo, c_hi = np.percentile(cb, [2.5, 97.5])

        rows.append({"section": "A4a_auc_ci", "background": "marrow_B_cell",
                     "metric": m, "auc": round(auc, 4),
                     "delong_ci_lo": round(float(d_lo), 4),
                     "delong_ci_hi": round(float(d_hi), 4),
                     "clusterboot_ci_lo": round(float(c_lo), 4),
                     "clusterboot_ci_hi": round(float(c_hi), 4),
                     "specificity": "", "sensitivity": "",
                     "n_signal": n_pos, "n_neutral": n_neg,
                     "note": "signal = delta>=0.25 (600 reps, 3 module seeds); neutral = neutral_hk+neutral_global (250); cluster bootstrap resamples the 3 module-seed clusters (signal side) + iid neutral, B=5000, seed=42"})
        print(f"  {m}: AUC={auc:.4f} DeLong [{d_lo:.3f},{d_hi:.3f}] "
              f"clusterBoot [{c_lo:.3f},{c_hi:.3f}]")

    # ---- (b) sensitivity at fixed specificity ----
    for m in METRIC_COLS:
        pos = sig1[m].to_numpy()
        neg = neu1[m].to_numpy()
        auc, _ = delong_auc(pos, neg)
        orient = 1.0 if auc >= 0.5 else -1.0
        for spec in (0.90, 0.95, 0.99):
            thr = np.quantile(orient * neg, spec)
            sens = float(np.mean(orient * pos > thr))
            rows.append({"section": "A4b_sensitivity_at_fixed_specificity",
                         "background": "marrow_B_cell", "metric": m,
                         "auc": round(auc, 4),
                         "delong_ci_lo": "", "delong_ci_hi": "",
                         "clusterboot_ci_lo": "", "clusterboot_ci_hi": "",
                         "specificity": spec, "sensitivity": round(sens, 4),
                         "n_signal": len(pos), "n_neutral": len(neg),
                         "note": f"threshold = neutral {spec:.0%} quantile; orientation {'higher=signal' if orient > 0 else 'lower=signal (score negated)'}"})

    # ---- (c) per-background AUC (pooled delta>=0.25 and delta=1.0)
    #          + detection power at delta=1.0 against each background's own
    #          null-95th threshold (explains the keratinocyte 0.91 vs marrow
    #          0.00 power contrast despite comparable AUCs) ----
    thr1 = json.load(open(RESULTS / "groundtruth_simulation_metrics.json"))["null_thresholds"]
    thr2 = json.load(open(RESULTS / "groundtruth_simulation_background2_metrics.json"))["null_thresholds"]
    for bg, raws, sigs, neus, thr in [
            ("marrow_B_cell", raw1, sig1, neu1, thr1),
            ("keratinocyte_stem_cell", raw2, sig2, neu2, thr2)]:
        for m in METRIC_COLS:
            auc_p, var_p = delong_auc(sigs[m].to_numpy(), neus[m].to_numpy())
            sig_d1 = raws[(raws["series"] == "signal") & (raws["delta"] == 1.0)]
            auc_1, var_1 = delong_auc(sig_d1[m].to_numpy(), neus[m].to_numpy())
            power_1 = float(np.mean(sig_d1[m].to_numpy() > thr[m]))
            rows.append({"section": "A4c_per_background_auc", "background": bg,
                         "metric": m,
                         "auc": round(auc_p, 4),
                         "delong_ci_lo": round(float(auc_p - 1.96 * np.sqrt(var_p)), 4),
                         "delong_ci_hi": round(float(auc_p + 1.96 * np.sqrt(var_p)), 4),
                         "clusterboot_ci_lo": round(auc_1, 4),
                         "clusterboot_ci_hi": round(power_1, 4),
                         "specificity": "", "sensitivity": "",
                         "n_signal": len(sigs), "n_neutral": len(neus),
                         "note": ("auc: pooled delta>=0.25 with DeLong CI; "
                                  "clusterboot_ci_lo column = AUC at delta=1.0; "
                                  "clusterboot_ci_hi column = detection power at delta=1.0 "
                                  f"(signal above background-specific null-95th threshold {thr[m]:.4g}, n="
                                  f"{len(sig_d1)}); power is strongly background-dependent even when AUC is not")})
            if m == "omega":
                print(f"  [{bg}] omega pooled AUC={auc_p:.4f}, delta=1 AUC={auc_1:.4f}, "
                      f"delta=1 power={power_1:.3f}")

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "nc52_stats_auc_ci_methods.csv", index=False)
    return out


# ============================================================
# D: omega vs k_f on real data
# ============================================================
def d_table():
    print("[D] omega-vs-k_f benchmark table ...", flush=True)
    rows = []

    def add(benchmark, scenario, omega, kf, kn, other, verdict, source):
        rows.append({"benchmark": benchmark, "scenario": scenario,
                     "omega": omega, "k_f": kf, "k_n": kn, "other_metrics": other,
                     "omega_adds_value_over_kf": verdict, "source": source})

    # ground-truth simulation, two backgrounds
    m1 = json.load(open(RESULTS / "groundtruth_simulation_metrics.json"))
    m2 = json.load(open(RESULTS / "groundtruth_simulation_background2_metrics.json"))
    add("GT simulation (marrow B cell)", "AUC signal vs neutral",
        m1["auc_signal_vs_neutral"]["omega"], m1["auc_signal_vs_neutral"]["k_f"],
        m1["auc_signal_vs_neutral"]["k_n"],
        f"k_total {m1['auc_signal_vs_neutral']['k_total']}, cosine {m1['auc_signal_vs_neutral']['cosine']}",
        "YES (detection): +0.09 AUC over k_f",
        "groundtruth_simulation_metrics.json")
    add("GT simulation (keratinocyte)", "AUC signal vs neutral",
        m2["auc_signal_vs_neutral"]["omega"], m2["auc_signal_vs_neutral"]["k_f"],
        m2["auc_signal_vs_neutral"]["k_n"],
        f"k_total {m2['auc_signal_vs_neutral']['k_total']}, cosine {m2['auc_signal_vs_neutral']['cosine']}",
        "YES (detection): +0.05 AUC over k_f",
        "groundtruth_simulation_background2_metrics.json")
    add("GT simulation (marrow)", "type-I error under neutral HK drift",
        m1["type_I_error"]["neutral_hk"]["overall"]["omega"],
        m1["type_I_error"]["neutral_hk"]["overall"]["k_f"],
        m1["type_I_error"]["neutral_hk"]["overall"]["k_n"],
        f"k_total {m1['type_I_error']['neutral_hk']['overall']['k_total']}, cosine {m1['type_I_error']['neutral_hk']['overall']['cosine']}",
        "NO extra specificity over k_f here (both ~0); both far better than k_n/k_total/cosine",
        "groundtruth_simulation_metrics.json")
    add("GT simulation (marrow)", "false detection under 4:1 imbalance (eta=1.0)",
        m1["robustness"]["imbalance"]["1.0"]["omega"],
        m1["robustness"]["imbalance"]["1.0"]["k_f"],
        m1["robustness"]["imbalance"]["1.0"]["k_n"],
        f"k_total {m1['robustness']['imbalance']['1.0']['k_total']}, cosine {m1['robustness']['imbalance']['1.0']['cosine']}",
        "YES (robustness): k_f false-fires at 0.38, omega at 0.00",
        "groundtruth_simulation_metrics.json")
    add("GT simulation (marrow)", "false detection under 2x depth difference",
        m1["robustness"]["depth"]["1.0"]["omega"],
        m1["robustness"]["depth"]["1.0"]["k_f"],
        m1["robustness"]["depth"]["1.0"]["k_n"],
        f"k_total {m1['robustness']['depth']['1.0']['k_total']}, cosine {m1['robustness']['depth']['1.0']['cosine']}",
        "Marginal over k_f (0.00 vs 0.02); both suppress the depth artefact that fires k_total (0.98)",
        "groundtruth_simulation_metrics.json")

    # Kang IFN-beta per-cell-type AUCs
    kang = json.load(open(RESULTS / "kang_ifnb_demo_summary.json"))["cell_types"]
    for ct, d in kang.items():
        delta = d["auc_omega"] - d["auc_kf"]
        verdict = ("NO (omega more conservative by design: neutral/compositional "
                   "shift inflates k_f but is discounted by omega)") if delta < -0.05 else \
                  ("no material difference" if abs(delta) <= 0.05 else "YES")
        add(f"Kang IFN-beta PBMC ({ct})",
            f"within-type stim-vs-ctrl AUC (n_donors={d['n_donors']})",
            round(d["auc_omega"], 3), round(d["auc_kf"], 3), "",
            f"raw_js {round(d['auc_raw_js'], 3)}; omega_cal stim {d['omega_cal_stim_ctrl']:.2f} vs donor {d['omega_cal_donor_donor']:.2f}",
            verdict, "kang_ifnb_demo_summary.json")

    # Kang technical-replicate null (30 cross-lane pairs)
    tr = pd.read_csv(RESULTS / "nc49_pilot_kang_techrep.csv")
    add("Kang technical replicates (30 cross-lane pairs)",
        "pairs exceeding own permutation-null 95th percentile",
        f"{int(tr['exceed_omega'].sum())}/30", f"{int(tr['exceed_k_f'].sum())}/30",
        f"{int(tr['exceed_k_n'].sum())}/30",
        f"raw_js {int(tr['exceed_raw_js'].sum())}/30, cosine {int(tr['exceed_cosine'].sum())}/30",
        "NO extra over k_f under pure technical null (both 0/30); raw_js/cosine anti-conservative",
        "nc49_pilot_kang_techrep.csv")

    # Brain atlas microglia
    add("Human Brain Atlas microglia (35 functional vs 40 neutral pairs)",
        "AUC functional > neutral",
        1.000, 1.000, 0.891, "raw_js 1.000, cosine 1.000, jaccard 1.000, spearman 0.901",
        "NO separation from k_f at this effect size (both perfect); omega separates at mean level (21.83+/-7.20 vs 1.30+/-0.36) as do k_f/raw_js",
        "nc50_brain_atlas_microglia.txt")

    # TCGA
    add("TCGA 5 cancers (paired NN vs TT)", "median omega NN/TT ratio",
        "1.23-2.32x elevation", "n/a", "TT/NN k_n ratio 2.18-3.70x (reversed)",
        "per-cancer ratios in phase34_v2_summary.csv",
        "YES (direction): omega elevated tumour-adjacent vs tumour while k_n moves oppositely; k_f not directly comparable in bulk design",
        "phase34_v2_summary.csv; tcga_composition_check.txt")

    # Mouse pilot categories
    add("Mouse pilot (Tabula Muris)", "category mean omega",
        "control 6.67; same-CT 21.31; diff-CT 43.19; cross-tissue 27.31",
        "n/a", "n/a", "n=15 pairs",
        "Ordinal separation matches biological expectation; k_f-only ranking not calibrated against split-half null (6.67) without omega",
        "mouse_pilot_v2_results.csv")

    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "nc52_stats_omega_vs_kf_realdata.csv", index=False)
    print(f"  {len(out)} benchmark rows written")
    return out


def d_math_floor():
    print("[D] k_n-permutation mathematical floor of omega-k_f correlation ...", flush=True)
    B_PERM = 1000
    rows = []
    for name, path, pairkey in [
            ("Tabula Sapiens human pairs (phase33 inventory)",
             RESULTS / "phase33_v3_human_pairs.csv", 5151),
            ("Mouse full matrix (Tabula Muris)",
             RESULTS / "full_matrix_pairs.csv", 703)]:
        df = pd.read_csv(path)
        assert len(df) == pairkey, (name, len(df))
        kf = df["kf"].to_numpy()
        kn = df["kn"].to_numpy()
        om = df["omega"].to_numpy()
        r_obs = float(spearmanr(om, kf).statistic)
        r_okn = float(spearmanr(om, kn).statistic)
        r_kfkn = float(spearmanr(kf, kn).statistic)
        r_floor = np.empty(B_PERM)
        prng = np.random.default_rng(SEED)
        kf_rank = rankdata(kf)
        for b in range(B_PERM):
            om_perm = kf / kn[prng.permutation(len(kn))]
            r_floor[b] = spearmanr(om_perm, kf).statistic
        lo, hi = np.percentile(r_floor, [2.5, 97.5])
        rows.append({
            "dataset": name, "n_pairs": len(df),
            "spearman_omega_kf_observed": round(r_obs, 4),
            "spearman_omega_kn_observed": round(r_okn, 4),
            "spearman_kf_kn_observed": round(r_kfkn, 4),
            "kn_permutation_floor_mean": round(float(r_floor.mean()), 4),
            "kn_permutation_floor_ci_lo": round(float(lo), 4),
            "kn_permutation_floor_ci_hi": round(float(hi), 4),
            "residual_above_floor": round(r_obs - float(r_floor.mean()), 4),
            "B": B_PERM, "seed": SEED,
            "note": ("floor = corr(k_f/k_n_perm, k_f) with k_n shuffled; any omega-k_f "
                     "correlation at/below the floor is mathematically forced by the shared "
                     "k_f numerator, not evidence of biological coupling"),
        })
        print(f"  {name}: observed {r_obs:.3f}, floor {r_floor.mean():.3f} "
              f"[{lo:.3f},{hi:.3f}], residual {r_obs - r_floor.mean():.3f}")
    out = pd.DataFrame(rows)
    out.to_csv(RESULTS / "nc52_stats_omega_kf_math_floor.csv", index=False)
    return out


if __name__ == "__main__":
    a1()
    a2b()
    a4()
    d_table()
    d_math_floor()
    print("nc52 stats resampling DONE")
