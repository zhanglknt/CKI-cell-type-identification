#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
_v38_statistical_addenda.py -- P1 statistical addenda for the CKI v38 revision.

Implements the statistics gap fixes requested in
version3/v38_reviews/panel_synthesis.md (P1 items 4-6 and auxiliary requests):

  S1   Yekutieli-Benjamini-style empirical FDR for the brain block-shuffle
       permutation p-value family:
       S1a  resampling FDR at p-value thresholds (global + tier strata)
       S1b  selection-rule empirical FDR (tier rule fully re-evaluated under
            each of the B = 1000 block-shuffle permutations)
  S2   Region-level cluster block bootstrap 95% CIs (B = 2,000) for the
       class-level omega gradient, per-class mean omega, grand mean and
       Strong/Moderate/Weak tier counts.
  S3   Cell-class-level Benjamini-Hochberg correction (m = 10), with
       two-sided and leave-pair-out fixed-panel sensitivities.
  S4   Clopper-Pearson intervals for ground-truth simulation detection
       rates and type-I error rates.
  S5   Bootstrap 95% CIs for method-comparison AUCs:
       S5a  Table 1 (Tabula Sapiens, 4,851 pairs): pair-level bootstrap and
            CT-entry cluster bootstrap
       S5b  ground-truth simulation AUC (omega vs k_f), replicate-block
            stratified bootstrap

Read-only inputs:
  results/brain_bs_null_results.csv            (31,764 pairs)
  results/brain_bs_null_ct_test.csv            (m = 10 class-level tests)
  results/brain_bs_null_pairs_<CT>.npy         (10 null matrices, (n_pairs, 1000))
  results/fixed_panel_ablation_ct.csv
  results/groundtruth_simulation_raw.csv
  results/groundtruth_simulation_metrics.json
  results/phase35_all_metrics_pairs.csv        (Table 1 source)

New outputs (no existing file is modified):
  results/v38_statistical_addenda.md
  results/v38_statistical_addenda_empirical_fdr.csv
  results/v38_statistical_addenda_block_bootstrap.csv
  results/v38_statistical_addenda_classlevel_bh.csv
  results/v38_statistical_addenda_clopper_pearson.csv
  results/v38_statistical_addenda_auc_ci.csv
"""

import inspect
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
SEED = 42
B_BOOT = 2000     # block bootstrap replicates (>= 1000 as requested)
B_AUC = 2000      # AUC bootstrap replicates

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LINE = {}


def mark(key):
    """Record the current source line so the report can cite it."""
    LINE[key] = inspect.currentframe().f_back.f_lineno


def log(msg):
    print(msg, flush=True)


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def bh_qvalues(p):
    """Benjamini-Hochberg adjusted p-values (q-values), step-up, tie-safe."""
    p = np.asarray(p, dtype=float)
    n = p.size
    order = np.argsort(p, kind="stable")
    ranked = p[order] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(n, dtype=float)
    out[order] = np.clip(q, 0.0, 1.0)
    return out


def cp_upper(x, n, conf=0.95):
    """One-sided Clopper-Pearson upper bound."""
    if x >= n:
        return 1.0
    return float(beta.ppf(conf, x + 1, n - x))


def cp_two_sided(x, n, conf=0.95):
    """Two-sided Clopper-Pearson interval."""
    a = (1.0 - conf) / 2.0
    lo = 0.0 if x == 0 else float(beta.ppf(a, x, n - x + 1))
    hi = 1.0 if x == n else float(beta.ppf(1.0 - a, x + 1, n - x))
    return lo, hi


def null_pvalues(null):
    """For a (n_pairs, B) null matrix, the within-row lower-tail p-value of
    each null draw: p[i, b] = (rank of null[i, b] among row i) / (B + 1).
    Under the null these are discrete-uniform, so permutation b yields a
    complete 'null experiment' of m p-values (Yekutieli-Benjamini machinery).
    """
    n, b = null.shape
    order = np.argsort(null, axis=1, kind="stable")
    rank = np.empty_like(order)
    ridx = np.arange(n)[:, None]
    rank[ridx, order] = np.arange(b)[None, :]
    return (rank + 1.0) / (b + 1.0)


md = []  # markdown report lines


def md_table(df, floatfmt=3):
    cols = list(df.columns)
    md.append("| " + " | ".join(str(c) for c in cols) + " |")
    md.append("|" + "|".join("---" for _ in cols) + "|")
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append(f"{v:.{floatfmt}f}")
            else:
                cells.append(str(v))
        md.append("| " + " | ".join(cells) + " |")


# ======================================================================
# Load brain block-shuffle data
# ======================================================================
log("Loading brain block-shuffle results...")
res = pd.read_csv(RESULTS / "brain_bs_null_results.csv")
cts = list(res["cell_type"].unique())
nulls = {}
B_perm = None
for ct in cts:
    null = np.load(RESULTS / f"brain_bs_null_pairs_{ct.replace(' ', '_')}.npy")
    nulls[ct] = null
    B_perm = null.shape[1]
    # verify row alignment between CSV and null matrix (same check as 08e)
    sub = res[res["cell_type"] == ct]
    assert null.shape[0] == len(sub), ct
    p_chk = ((null <= sub["omega"].values[:, None]).sum(axis=1) + 1) / (B_perm + 1)
    assert np.allclose(p_chk, sub["p_perm"].values), f"null alignment failed for {ct}"
log(f"  {len(res)} pairs, {len(cts)} cell types, B = {B_perm}; alignment verified")

# global region-pair factorisation (used by S1b and S2)
gp_keys = [tuple(sorted(t)) for t in zip(res["region_a"], res["region_b"])]
gp_ids, gp_uniq = pd.factorize(pd.Series(gp_keys))
n_gp = len(gp_uniq)
ct_ids, ct_uniq = pd.factorize(res["cell_type"])
assert (res.groupby(gp_ids)[["region_a", "region_b"]].nunique().max() <= 1).all()

# observed tier counts (authority check)
tier_counts_obs = res["tier"].value_counts().to_dict()
assert tier_counts_obs.get("Strong", 0) == 55
assert tier_counts_obs.get("Moderate", 0) == 2120
assert tier_counts_obs.get("Weak", 0) == 6149
n_p05_obs = int((res["p_perm"] < 0.05).sum())
log(f"  observed tiers {tier_counts_obs}; raw p<0.05: {n_p05_obs}")

STRONG_OBS = 55
MODERATE_OBS = 2120
WEAK_OBS = 6149
STRONG_P05_OBS = int(((res["tier"] == "Strong") & (res["p_perm"] < 0.05)).sum())  # 37

md.append("# v38 统计补全（P1：经验 FDR / block bootstrap CI / 类级 BH / Clopper-Pearson / AUC CI)")
md.append("")
md.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}　"
          f"脚本：`notebooks/_v38_statistical_addenda.py`（本文件，以下各节标注行号）")
md.append("")
md.append("所有输入为只读；未修改任何既有结果文件。数值精度与稿件一致（2–3 位小数）。")
md.append("")

# ======================================================================
# S1a. Yekutieli-Benjamini resampling FDR at p-value thresholds
# ======================================================================
mark("S1a")
log("S1a: Yekutieli-Benjamini resampling FDR at p-value thresholds...")
ALPHAS = [0.001, 0.005, 0.01, 0.05, 0.10]
strata = ["all", "Strong", "Moderate", "Weak"]
tier_col = res["tier"].values
p_perm_col = res["p_perm"].values

Vb = {(s, a): np.zeros(B_perm) for s in strata for a in ALPHAS}
m_stratum = {"all": len(res)}
for s in ["Strong", "Moderate", "Weak"]:
    m_stratum[s] = int((tier_col == s).sum())

for ct in cts:
    p_null = null_pvalues(nulls[ct])
    ct_tier = res.loc[res["cell_type"] == ct, "tier"].values
    for s in strata:
        msk = np.ones(nulls[ct].shape[0], bool) if s == "all" else (ct_tier == s)
        if not msk.any():
            continue
        for a in ALPHAS:
            Vb[(s, a)] += (p_null[msk] < a).sum(axis=0)

rows_fdr = []
for s in strata:
    for a in ALPHAS:
        R = int((p_perm_col[tier_col == s if s != "all" else np.ones(len(res), bool)] < a).sum()) \
            if s != "all" else int((p_perm_col < a).sum())
        Vbar = float(Vb[(s, a)].mean())
        Vmax = int(Vb[(s, a)].max())
        fdr_emp = Vbar / max(R, 1)
        bh_ref = min(1.0, m_stratum[s] * a / max(R, 1))
        rows_fdr.append({
            "family": s, "alpha": a, "m": m_stratum[s], "R_obs": R,
            "Vbar_null": round(Vbar, 1), "Vmax_null": Vmax,
            "FDR_emp": round(fdr_emp, 3), "BH_ref(m*alpha/R)": round(bh_ref, 3),
        })
df_fdr = pd.DataFrame(rows_fdr)

md.append("## 1. Yekutieli–Benjamini 经验 FDR（block-shuffle 置换族）")
md.append("")
md.append("### 1a. p 值阈值上的重采样 FDR")
md.append("")
md.append("方法：对每个置换 b（B = 1,000），将全部 31,764 个 null ω 视作一次完整"
          "“null 实验”，逐对计算其在自身 null 分布中的秩 p 值 "
          "p(i,b) = rank(ω[i,b])/（B+1）（下尾）。对阈值 α："
          "R(α) = 观测 p_perm < α 的对数；V̄(α) = B 次置换中 null p < α 的平均对数；"
          "经验 FDR = V̄(α)/max(R(α),1)（Yekutieli & Benjamini 1999 的重抽样 plug-in 估计；"
          "BH 参考列 = m·α/R）。分层（Strong/Moderate/Weak 族）为事后分层，仅作参考——"
          "tier 由同一数据的选择规则产生，严格有效的族是全族与 1b 的选择规则 FDR。")
md.append("")
md_table(df_fdr)
md.append("")
md.append(f"数据来源：`results/brain_bs_null_results.csv` + "
          f"`results/brain_bs_null_pairs_<CT>.npy`；计算："
          f"`notebooks/_v38_statistical_addenda.py` L{LINE['S1a']} 起。")
md.append("")

# ======================================================================
# S1b. selection-rule empirical FDR (tier rule re-evaluated under null)
# ======================================================================
mark("S1b")
log("S1b: selection-rule empirical FDR (tier rule under null)...")

# per-CT null means and grand mean (per permutation b)
mu_ct_null = {ct: nulls[ct].mean(axis=0) for ct in cts}
n_ct = {ct: nulls[ct].shape[0] for ct in cts}
grand_null = sum(n_ct[ct] * mu_ct_null[ct] for ct in cts) / sum(n_ct.values())

ct_rows = {ct: (res["cell_type"] == ct).values for ct in cts}
gp_of_ct = {ct: gp_ids[ct_rows[ct]] for ct in cts}

# per region-pair null mean over cell types, and running minimum (per b)
sum_val = np.zeros((n_gp, B_perm))
cnt_gp = np.zeros(n_gp)
min_val = np.full((n_gp, B_perm), np.inf)
for ct in cts:
    g = gp_of_ct[ct]
    nv = nulls[ct].astype(np.float64)
    sum_val[g] += nv
    cnt_gp[g] += 1
    min_val[g] = np.minimum(min_val[g], nv)
mu_pair_null = sum_val / cnt_gp[:, None]

counts_null = {t: np.zeros(B_perm) for t in ["Strong", "Moderate", "Weak"]}
combined_null = np.zeros(B_perm)  # Strong AND raw p < 0.05
for ct in cts:
    g = gp_of_ct[ct]
    nv = nulls[ct].astype(np.float64)
    exp = mu_ct_null[ct][None, :] * mu_pair_null[g] / grand_null[None, :]
    resid = nv / exp
    lowest = nv <= min_val[g]
    strong = (resid < 0.3) & (nv < 15) & lowest
    moderate = (~strong) & (resid < 0.5) & (nv < 25)
    weak = (~strong) & (~moderate) & (resid < 0.75) & (nv < 35)
    counts_null["Strong"] += strong.sum(axis=0)
    counts_null["Moderate"] += moderate.sum(axis=0)
    counts_null["Weak"] += weak.sum(axis=0)
    p_null = null_pvalues(nulls[ct])
    combined_null += (strong & (p_null < 0.05)).sum(axis=0)

# observed sanity check: recompute observed tiers from the model columns
obs_resid = res["residual"].values
obs_omega = res["omega"].values
obs_lowest = res["lowest_in_pair"].values.astype(bool)
o_strong = (obs_resid < 0.3) & (obs_omega < 15) & obs_lowest
o_moderate = (~o_strong) & (obs_resid < 0.5) & (obs_omega < 25)
o_weak = (~o_strong) & (~o_moderate) & (obs_resid < 0.75) & (obs_omega < 35)
assert int(o_strong.sum()) == STRONG_OBS and int(o_moderate.sum()) == MODERATE_OBS \
    and int(o_weak.sum()) == WEAK_OBS
assert int((o_strong & (p_perm_col < 0.05)).sum()) == STRONG_P05_OBS
log(f"  observed rule counts verified: {STRONG_OBS}/{MODERATE_OBS}/{WEAK_OBS}, "
    f"Strong&p<0.05 = {STRONG_P05_OBS}")

rows_rule = []
for name, R_obs, vb in [
    ("Strong 规则 (residual<0.3 & ω<15 & lowest-in-pair)", STRONG_OBS, counts_null["Strong"]),
    ("Moderate 规则 (residual<0.5 & ω<25)", MODERATE_OBS, counts_null["Moderate"]),
    ("Weak 规则 (residual<0.75 & ω<35)", WEAK_OBS, counts_null["Weak"]),
    ("Strong ∧ raw p<0.05（稿件报告的 37 个候选）", STRONG_P05_OBS, combined_null),
]:
    Vbar = float(vb.mean())
    Vmax = int(vb.max())
    p_emp = (1 + int((vb >= R_obs).sum())) / (B_perm + 1)
    rows_rule.append({
        "selection rule": name, "R_obs": R_obs,
        "null mean Vbar": round(Vbar, 1), "null max": Vmax,
        "FDR_emp=Vbar/R": round(Vbar / R_obs, 3),
        "P(null count >= R)": round(p_emp, 4),
    })
df_rule = pd.DataFrame(rows_rule)

md.append("### 1b. 选择规则经验 FDR（tier 规则在 null 下的完整重算）")
md.append("")
md.append("方法：对每个置换 b，用该次置换产生的全部 31,764 个 null ω **完整重算**"
          "乘法残差模型（mu_ct、mu_pair、grand mean、lowest-in-pair、residual），"
          "再应用与观测数据完全相同的 Strong/Moderate/Weak 阈值规则并计数。"
          "经验 FDR = null 计数均值 / 观测计数（SAM/Yekutieli–Benjamini 型 plug-in）。"
          "这是对“按该规则筛选时预期多少假发现”的直接回答。")
md.append("")
md_table(df_rule)
md.append("")
md.append(f"数据来源：同 1a；计算：`notebooks/_v38_statistical_addenda.py` L{LINE['S1b']} 起。")
md.append("")
md.append("解读：block-shuffle null 破坏区域结构后整体 ω 标度下移，使绝对阈值（ω<15/25/35）"
          "在 null 下也有大量通过者——Strong 规则的 null 期望计数达 39.8/55（经验 FDR 0.72），"
          "即 tier 阈值规则本身相对 null 并无富集；这与稿件“候选目录为假设生成列表”的"
          "定位一致，且是比“BH q<0.05 不可达”更有力的经验论证。")
md.append("")

# ----------------------------------------------------------------------
# S1c. cell-type-stratified BH over the pair family (sensitivity)
# ----------------------------------------------------------------------
mark("S1c")
log("S1c: cell-type-stratified BH (sensitivity)...")
rows_ctbh = []
for ct in cts:
    g = res[res["cell_type"] == ct]
    q_ct = bh_qvalues(g["p_perm"].values)
    rows_ctbh.append({
        "cell_type": ct, "n_pairs": len(g),
        "min_q": round(float(q_ct.min()), 4),
        "n_q<0.05": int((q_ct < 0.05).sum()),
        "n_q<0.10": int((q_ct < 0.10).sum()),
    })
df_ctbh = pd.DataFrame(rows_ctbh).sort_values("min_q")

md.append("### 1c. 按 cell-type 分层的 BH（敏感性分析）")
md.append("")
md.append("方法：把 31,764 对按细胞类拆成 10 个族，各自独立做 BH（族定义改为最有利的"
          "事后分层）。结果：任何分层下都**没有** q < 0.05 的对（最小 q = "
          f"{df_ctbh['min_q'].min():.2f}，Oligodendrocyte precursor 族）。"
          "即“q<0.05 不可达”的结论对族定义稳健。")
md.append("")
md_table(df_ctbh, floatfmt=4)
md.append("")
md.append(f"数据来源：`results/brain_bs_null_results.csv`；计算："
          f"`notebooks/_v38_statistical_addenda.py` L{LINE['S1c']} 起。")
md.append("")

# ======================================================================
# S2. region-level cluster block bootstrap
# ======================================================================
mark("S2")
log("S2: region-level cluster block bootstrap (B = 2000)...")

regions = sorted(set(res["region_a"]) | set(res["region_b"]))
n_reg = len(regions)
rpos = {r: i for i, r in enumerate(regions)}
ia = res["region_a"].map(rpos).values.astype(np.int64)
ib = res["region_b"].map(rpos).values.astype(np.int64)
omega_all = res["omega"].values.astype(np.float64)
n_ct_total = len(ct_uniq)
log(f"  {n_reg} region clusters (design unit of the pair statistic)")


def evaluate_weights(w_all):
    """Recompute the multiplicative model + tier counts under pair weights w."""
    sw_ct = np.bincount(ct_ids, weights=w_all, minlength=n_ct_total)
    swx_ct = np.bincount(ct_ids, weights=w_all * omega_all, minlength=n_ct_total)
    with np.errstate(invalid="ignore", divide="ignore"):
        mu_ct = np.where(sw_ct > 0, swx_ct / np.where(sw_ct > 0, sw_ct, 1.0), np.nan)
    grand = swx_ct.sum() / w_all.sum()
    sw_gp = np.bincount(gp_ids, weights=w_all, minlength=n_gp)
    swx_gp = np.bincount(gp_ids, weights=w_all * omega_all, minlength=n_gp)
    mu_pair = np.where(sw_gp > 0, swx_gp / np.where(sw_gp > 0, sw_gp, 1.0), 1.0)
    minv = np.full(n_gp, np.inf)
    nz = w_all > 0
    np.minimum.at(minv, gp_ids[nz], omega_all[nz])
    exp = mu_ct[ct_ids] * mu_pair[gp_ids] / grand
    resid = omega_all / exp
    lowest = omega_all <= minv[gp_ids]
    strong = (resid < 0.3) & (omega_all < 15) & lowest
    moderate = (~strong) & (resid < 0.5) & (omega_all < 25)
    weak = (~strong) & (~moderate) & (resid < 0.75) & (omega_all < 35)
    counts = ((strong * w_all).sum(), (moderate * w_all).sum(), (weak * w_all).sum())
    return mu_ct, grand, counts


# sanity: unit weights reproduce the published observed values exactly
mu_ct_obs, grand_obs, counts_obs = evaluate_weights(np.ones(len(res)))
mu_ct_pub = res.groupby("cell_type")["omega"].mean().reindex(ct_uniq).values
assert np.allclose(mu_ct_obs, mu_ct_pub, rtol=1e-9)
assert np.allclose(counts_obs, (STRONG_OBS, MODERATE_OBS, WEAK_OBS))
grad_obs = float(np.nanmax(mu_ct_obs) / np.nanmin(mu_ct_obs))
log(f"  unit-weight check OK: gradient = {grad_obs:.2f}, "
    f"Strong = {counts_obs[0]:.0f}")

rng2 = np.random.default_rng(SEED)
mu_ct_boot = np.full((B_BOOT, n_ct_total), np.nan)
grad_boot = np.full(B_BOOT, np.nan)
grand_boot = np.full(B_BOOT, np.nan)
strong_boot = np.full(B_BOOT, np.nan)
mod_boot = np.full(B_BOOT, np.nan)
weak_boot = np.full(B_BOOT, np.nan)
for b in range(B_BOOT):
    m = rng2.multinomial(n_reg, np.full(n_reg, 1.0 / n_reg))
    w_all = (m[ia] * m[ib]).astype(np.float64)
    mu_ct_b, grand_b, counts_b = evaluate_weights(w_all)
    mu_ct_boot[b] = mu_ct_b
    grand_boot[b] = grand_b
    strong_boot[b], mod_boot[b], weak_boot[b] = counts_b
    if not np.isnan(mu_ct_b).any():
        grad_boot[b] = mu_ct_b.max() / mu_ct_b.min()
n_grad_ok = int(np.isfinite(grad_boot).sum())
log(f"  bootstrap done; gradient defined in {n_grad_ok}/{B_BOOT} replicates")


def ci95(x):
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return (np.nan, np.nan)
    return tuple(np.percentile(x, [2.5, 97.5]))


rows_bb = []
rows_bb.append({"quantity": "gradient_fold (max/min class mean ω)",
                "estimate": round(grad_obs, 2),
                "CI_low": round(ci95(grad_boot)[0], 2),
                "CI_high": round(ci95(grad_boot)[1], 2)})
rows_bb.append({"quantity": "grand mean ω (all 31,764 pairs)",
                "estimate": round(grand_obs, 2),
                "CI_low": round(ci95(grand_boot)[0], 2),
                "CI_high": round(ci95(grand_boot)[1], 2)})
for k, name in [("strong", "Strong 候选计数"), ("mod", "Moderate 计数"), ("weak", "Weak 计数")]:
    arr = {"strong": strong_boot, "mod": mod_boot, "weak": weak_boot}[k]
    est = {"strong": STRONG_OBS, "mod": MODERATE_OBS, "weak": WEAK_OBS}[k]
    lo, hi = ci95(arr)
    rows_bb.append({"quantity": name, "estimate": est,
                    "CI_low": round(lo, 1), "CI_high": round(hi, 1)})
for j, ct in enumerate(ct_uniq):
    lo, hi = ci95(mu_ct_boot[:, j])
    rows_bb.append({"quantity": f"类级 mean ω: {ct}",
                    "estimate": round(float(mu_ct_pub[j]), 2),
                    "CI_low": round(lo, 2), "CI_high": round(hi, 2)})
df_bb = pd.DataFrame(rows_bb)

md.append("## 2. 区域聚类 block bootstrap 95% CI（B = 2,000）")
md.append("")
md.append("方法：以**区域**（108 个，成对统计量的设计单元；10x library/sample 嵌套于区域内，"
          "供体层仅 4 簇、过粗无法 bootstrap）为聚类单元，有放回重抽样 108 个区域，"
          "按区域多重数得到每对权重 w = m(a)·m(b)，**完整重算**乘法残差模型与全部统计量，"
          "取 2.5/97.5 百分位。单位权重下精确复现观测值（gradient 6.88、Strong 55、"
          "Astrocyte 76.83），已作断言校验。")
md.append("")
md_table(df_bb, floatfmt=2)
md.append("")
md.append(f"数据来源：`results/brain_bs_null_results.csv`；计算："
          f"`notebooks/_v38_statistical_addenda.py` L{LINE['S2']} 起。")
md.append("")

# ======================================================================
# S3. class-level BH (m = 10)
# ======================================================================
mark("S3")
log("S3: class-level BH (m = 10)...")
ct_test = pd.read_csv(RESULTS / "brain_bs_null_ct_test.csv")
p1 = ct_test["p_value"].values
q1 = bh_qvalues(p1)
p2 = np.minimum(1.0, 2.0 * p1)  # two-sided sensitivity (conservative)
q2 = bh_qvalues(p2)

abl = pd.read_csv(RESULTS / "fixed_panel_ablation_ct.csv").set_index("cell_type")
p_abl = abl.loc[ct_test["cell_type"], "s2_p_value"].values
q_abl = bh_qvalues(p_abl)

df_bh = pd.DataFrame({
    "cell_type": ct_test["cell_type"],
    "n_pairs": ct_test["n_pairs"],
    "p_one_sided": np.round(p1, 4),
    "q_BH_one_sided": np.round(q1, 4),
    "p_two_sided": np.round(p2, 4),
    "q_BH_two_sided": np.round(q2, 4),
    "p_fixed_panel": np.round(p_abl, 4),
    "q_BH_fixed_panel": np.round(q_abl, 4),
})
berg = df_bh[df_bh["cell_type"] == "Bergmann glia"].iloc[0]
log(f"  Bergmann glia: q(one-sided) = {berg['q_BH_one_sided']}, "
    f"q(two-sided) = {berg['q_BH_two_sided']}, q(fixed-panel) = {berg['q_BH_fixed_panel']}")

md.append("## 3. 类级多重校正（BH，m = 10 个细胞类）")
md.append("")
md.append("方法：对 `brain_bs_null_ct_test.csv` 的 10 个类级置换检验 p 值执行 BH。"
          "Bergmann glia 的 p = 0.0310 在族中排第 9（8 个类在置换分辨率下限 9.99×10⁻⁴），"
          "故 BH q = 0.0310×10/9 = 0.0344。注意：评审 R2 给出的 “q≈0.31” 相当于 p×m"
          "（按秩 1 计算），与 BH 的步进公式不符；正确的一侧 BH q = 0.034。"
          "但该结论不稳健：双侧化后 q = 0.069、leave-pair-out 固定基因面板下 q = 0.111，"
          "且仅 21 对比较。")
md.append("")
md_table(df_bh, floatfmt=4)
md.append("")
bergmann_conclusion = (
    "Bergmann glia 类级显著性结论（供稿件降级表述）：单侧 BH 下 q = 0.034（< 0.05，"
    "形式上仍显著），但 (i) 双侧检验 q = 0.069，(ii) leave-pair-out 固定面板方案 "
    "q = 0.111（p = 0.0995），(iii) 仅 21 对比较、7 个区域。建议稿件将 Bergmann glia "
    "表述降级为“类级 BH 校正后处于显著性边缘（单侧 q = 0.034；双侧 q = 0.069），"
    "且在固定基因面板敏感性分析中不显著（q = 0.111）”，不再使用 "
    "“marginal significance”（未校正）的说法。"
)
md.append(bergmann_conclusion)
md.append("")
md.append(f"数据来源：`results/brain_bs_null_ct_test.csv`、"
          f"`results/fixed_panel_ablation_ct.csv`；计算："
          f"`notebooks/_v38_statistical_addenda.py` L{LINE['S3']} 起。")
md.append("")

# ======================================================================
# S4. Clopper-Pearson intervals (ground-truth simulation)
# ======================================================================
mark("S4")
log("S4: Clopper-Pearson intervals...")
raw = pd.read_csv(RESULTS / "groundtruth_simulation_raw.csv")
mj = json.load(open(RESULTS / "groundtruth_simulation_metrics.json"))
th = mj["null_thresholds"]

sig1 = raw[(raw.series == "signal") & (raw.delta == 1.0)]
sig2 = raw[(raw.series == "signal") & (raw.delta == 2.0)]
nh = raw[raw.series == "neutral_hk"]
ng = raw[raw.series == "neutral_global"]
neu = pd.concat([nh, ng])


def rate(metric, df_, thr):
    x = int((df_[metric] > thr).sum())
    return x, len(df_)


cases = []
# task-specified framing (0/10)
cases.append(("δ=1 检出率（任务口径 0/10）", 0, 10))
# data-grounded counts
for label, metric, df_, thr in [
    ("δ=1 检出率（ω，3 个 module seed 合并 150 次重复）", "omega", sig1, th["omega"]),
    ("δ=1 检出率（k_f，同上）", "k_f", sig1, th["k_f"]),
    ("δ=2 检出率（ω，150 次重复）", "omega", sig2, th["omega"]),
    ("δ=2 检出率（raw JS，150 次重复）", "k_total", sig2, th["k_total"]),
    ("I 类错误（ω，中性 HK 漂移 η=0.25–1，150 次）", "omega", nh, th["omega"]),
    ("I 类错误（ω，全局过散 ε=0.3–1，100 次）", "omega", ng, th["omega"]),
    ("I 类错误（ω，全部中性重复，250 次）", "omega", neu, th["omega"]),
    ("I 类错误（raw JS，中性 HK 漂移，150 次）", "k_total", nh, th["k_total"]),
    ("I 类错误（cosine，中性 HK 漂移，150 次）", "cosine", nh, th["cosine"]),
]:
    x, n = rate(metric, df_, thr)
    cases.append((label, x, n))

rows_cp = []
for label, x, n in cases:
    lo, hi = cp_two_sided(x, n)
    rows_cp.append({
        "scenario": label, "x": x, "n": n, "rate": round(x / n, 3),
        "CP_95_one_sided_upper": round(cp_upper(x, n), 4),
        "CP_95_CI_low": round(lo, 4), "CP_95_CI_high": round(hi, 4),
    })
df_cp = pd.DataFrame(rows_cp)

md.append("## 4. Clopper–Pearson 精确区间（ground-truth 模拟检出率 / I 类错误）")
md.append("")
md.append("方法：检出阈值 = 200 次 baseline 重复的 95 百分位"
          "（`groundtruth_simulation_metrics.json` 的 `null_thresholds`），"
          "与稿件一致；Clopper–Pearson 单侧 95% 上界 = Beta(0.95; x+1, n−x)，"
          "双侧 95% CI = [Beta(0.025; x, n−x+1), Beta(0.975; x+1, n−x)]。")
md.append("")
md_table(df_cp, floatfmt=4)
md.append("")
md.append("说明：任务口径 “δ=1 检出率 0/10” 的单侧 95% 上界 = 1−0.05^(1/10) = **0.2589**；"
          "但数据实际口径为 3 个 module seed × 50 次重复 = **0/150**（上界 0.0197，"
          "即 < 2%），建议稿件按 0/150 报告。R2 要求的 FPR=0.00 上界：中性 HK 漂移下 "
          "0/150 → 上界 0.0197（约 2%，与 R2 估计的 “<1.5%（按 ~200 次重复）” 同量级，"
          "差异源于重复数口径）。")
md.append("")
md.append(f"数据来源：`results/groundtruth_simulation_raw.csv`、"
          f"`results/groundtruth_simulation_metrics.json`；计算："
          f"`notebooks/_v38_statistical_addenda.py` L{LINE['S4']} 起。")
md.append("")

# ======================================================================
# S5a. Table 1 AUC bootstrap CIs (phase35)
# ======================================================================
mark("S5a")
log("S5a: Table 1 AUC bootstrap CIs...")
df5 = pd.read_csv(RESULTS / "phase35_all_metrics_pairs.csv")
df5["key_i"] = df5["organ_i"] + "|" + df5["ct_i"]
df5["key_j"] = df5["organ_j"] + "|" + df5["ct_j"]
entries = sorted(set(df5["key_i"]) | set(df5["key_j"]))
eidx = {k: i for i, k in enumerate(entries)}
E = len(entries)
assert len(df5) == E * (E - 1) // 2
iu = np.triu_indices(E, k=1)

METRICS5 = [("CKI omega", "omega"), ("Raw JS", "js_raw"),
            ("Spearman dist", "spearman_dist"), ("Cosine dist", "cosine_dist"),
            ("Marker Jaccard dist", "marker_jaccard_dist")]
VAL = {}
SAME = np.zeros((E, E), bool)
ii = df5["key_i"].map(eidx).values.astype(np.int64)
jj = df5["key_j"].map(eidx).values.astype(np.int64)
lo_ij = np.minimum(ii, jj)
hi_ij = np.maximum(ii, jj)
assert len(set(zip(lo_ij, hi_ij))) == len(df5)  # each unordered entry pair once
for name, col in METRICS5:
    v = df5[col].values
    v = np.where(np.isinf(v), np.nan, v)
    M = np.full((E, E), np.nan)
    M[lo_ij, hi_ij] = v
    M[hi_ij, lo_ij] = v  # symmetric; diagonal stays NaN
    VAL[name] = M
SAME[lo_ij, hi_ij] = df5["same_ct"].values.astype(bool)
SAME = SAME | SAME.T
n_inf = int(np.isinf(df5["omega"].values).sum())
log(f"  {E} CT entries, {len(df5)} pairs, {n_inf} inf omega values")

y_true = df5["same_ct"].astype(int).values
rng5 = np.random.default_rng(SEED)


def auc_from_rows(vals, yy):
    m = np.isfinite(vals)
    if m.sum() < 2 or len(np.unique(yy[m])) < 2:
        return np.nan
    return roc_auc_score(yy[m], -vals[m])


# point estimates
auc_point = {}
for name, col in METRICS5:
    v = df5[col].values
    v = np.where(np.isinf(v), np.nan, v)
    auc_point[name] = float(auc_from_rows(v, y_true))

# (i) pair-level bootstrap
auc_pair = {name: np.full(B_AUC, np.nan) for name, _ in METRICS5}
for b in range(B_AUC):
    idx = rng5.integers(0, len(df5), len(df5))
    yy = y_true[idx]
    for name, col in METRICS5:
        v = df5[col].values[idx]
        v = np.where(np.isinf(v), np.nan, v)
        auc_pair[name][b] = auc_from_rows(v, yy)

# (ii) CT-entry cluster bootstrap (resample the 99 entries; pairs of the same
# resampled entry are structural duplicates and carry no information -> excluded)
# identity sanity check: pos = arange(E) must reproduce the point AUC exactly
_id = np.arange(E)
_pi, _pj = _id[iu[0]], _id[iu[1]]
for name, _ in METRICS5:
    _v = VAL[name][_pi, _pj]
    _m = np.isfinite(_v)
    _a = roc_auc_score(SAME[_pi, _pj][_m], -_v[_m])
    assert abs(_a - auc_point[name]) < 1e-9, (name, _a, auc_point[name])
log("  cluster-bootstrap identity check OK (pos=arange reproduces point AUC)")

auc_clust = {name: np.full(B_AUC, np.nan) for name, _ in METRICS5}
for b in range(B_AUC):
    pos = rng5.integers(0, E, E)
    pi, pj = pos[iu[0]], pos[iu[1]]
    dup = pi == pj
    yy = SAME[pi, pj]
    for name, _ in METRICS5:
        v = VAL[name][pi, pj]
        m = (~dup) & np.isfinite(v)
        if m.sum() < 2 or len(np.unique(yy[m])) < 2:
            continue
        auc_clust[name][b] = roc_auc_score(yy[m], -v[m])

rows_auc = []
for name, _ in METRICS5:
    lo_p, hi_p = ci95(auc_pair[name])
    lo_c, hi_c = ci95(auc_clust[name])
    rows_auc.append({
        "metric": name, "AUC": round(auc_point[name], 4),
        "pair_boot_CI_low": round(lo_p, 3), "pair_boot_CI_high": round(hi_p, 3),
        "cluster_boot_CI_low": round(lo_c, 3), "cluster_boot_CI_high": round(hi_c, 3),
    })
df_auc5 = pd.DataFrame(rows_auc)

md.append("## 5a. Table 1 方法比较 AUC 的 bootstrap 95% CI（Tabula Sapiens，4,851 对）")
md.append("")
md.append("方法：(i) 对级 bootstrap（4,851 行有放回重抽样）；(ii) CT 条目聚类 "
          "bootstrap（99 个 cell-type 条目有放回重抽样，重抽样条目间的全部 "
          "C(99,2) 对重构 AUC；同一原始条目被抽中两次形成的自配对不携带信息，"
          "予以剔除）。B = 2,000。聚类 bootstrap 反映 CT 条目层面的抽样不确定性，"
          "为更保守的口径。")
md.append("")
md_table(df_auc5, floatfmt=3)
md.append("")
md.append(f"数据来源：`results/phase35_all_metrics_pairs.csv`；计算："
          f"`notebooks/_v38_statistical_addenda.py` L{LINE['S5a']} 起。")
md.append("")

# ======================================================================
# S5b. ground-truth simulation AUC bootstrap CI
# ======================================================================
mark("S5b")
log("S5b: simulation AUC bootstrap CI...")
pos_mask = (raw.series == "signal") & (raw.delta >= 0.25)
neg_mask = raw.series.isin(["neutral_hk", "neutral_global"])
simsub = raw[pos_mask | neg_mask].copy()
simsub["y"] = pos_mask[pos_mask | neg_mask].astype(int)
cond_cols = ["series", "delta", "eta", "eps", "module_seed"]
cond_groups = [g.index.values for _, g in simsub.groupby(cond_cols)]
METRICS_SIM = ["omega", "k_f", "k_n", "k_total", "cosine", "kf_over_kt"]

auc_sim_point = {}
for c in METRICS_SIM:
    auc_sim_point[c] = float(roc_auc_score(simsub["y"], simsub[c]))

rng6 = np.random.default_rng(SEED + 1)
auc_sim_boot = {c: np.full(B_AUC, np.nan) for c in METRICS_SIM}
omega_gt_kf = np.full(B_AUC, np.nan)
for b in range(B_AUC):
    idx = np.concatenate([rng6.choice(g, size=len(g), replace=True) for g in cond_groups])
    sub = simsub.loc[idx]
    yy = sub["y"].values
    for c in METRICS_SIM:
        auc_sim_boot[c][b] = roc_auc_score(yy, sub[c].values)
    omega_gt_kf[b] = auc_sim_boot["omega"][b] > auc_sim_boot["k_f"][b]

rows_simauc = []
for c in METRICS_SIM:
    lo, hi = ci95(auc_sim_boot[c])
    rows_simauc.append({
        "metric": c, "AUC": round(auc_sim_point[c], 3),
        "CI_low": round(lo, 3), "CI_high": round(hi, 3),
    })
df_aucsim = pd.DataFrame(rows_simauc)
p_rank = float(np.nanmean(omega_gt_kf))

md.append("## 5b. Ground-truth 模拟 AUC（功能 vs 中性扰动）的 bootstrap 95% CI")
md.append("")
md.append("方法：按重复块（每个 series×δ×η×ε×module_seed 条件内的 50 次重复）分层 "
          "bootstrap（B = 2,000），正类 = signal δ≥0.25（12 条件 × 50 = 600），"
          "负类 = neutral_hk + neutral_global（5 条件 × 50 = 250），AUC 直接用度量值作"
          "分数（与稿件 0.80/0.72 口径一致，已数值复核：0.8042/0.7159）。")
md.append("")
md_table(df_aucsim, floatfmt=3)
md.append("")
md.append(f"ω > k_f 的 bootstrap 概率 = {p_rank:.3f}（即 ω 对 k_f 的 AUC 排序优势在 "
          f"重抽样下成立的比例）。")
md.append("")
md.append(f"数据来源：`results/groundtruth_simulation_raw.csv`；计算："
          f"`notebooks/_v38_statistical_addenda.py` L{LINE['S5b']} 起。")
md.append("")

# ======================================================================
# write outputs
# ======================================================================
md.append("## 附注（供修改稿件时的口径提示）")
md.append("")
md.append("1. 1a 的全局族在 α = 0.05 下 R = 938 < V̄ ≈ 1,588（下尾发现数少于 null 期望），"
          "经验 FDR > 1——这正是稿件“下尾亏缺、上尾过剩”论述的重抽样版本；"
          "此时经验 FDR 应解读为“α = 0.05 的下尾筛查在全局 null 下不可用”，而非字面 FDR。")
md.append("2. 1b 的选择规则 FDR 是对候选目录最直接的经验 FDR 陈述：Strong 规则的 null "
          "期望计数为 39.8/55（经验 FDR 0.72），稿件报告的 37 个 Strong ∧ p<0.05 候选的"
          "经验 FDR 为 0.66——tier 阈值规则相对 null 无富集，候选目录应保持"
          "“假设生成”定位；1c 表明该结论对族定义（按类分层）稳健。")
md.append("3. 2 的聚类 bootstrap CI 显著宽于稿件原有的对级重抽样 CI（R2-M2 所指"
          "“CI 系统性过窄”），建议正文/图注全部替换为本表口径。")
md.append("4. 3 的类级 BH 表可直接替换稿件的类级显著性陈述；Bergmann glia 建议按"
          "上文结论降级。")
md.append("")

out_md = RESULTS / "v38_statistical_addenda.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")
log(f"\nWrote {out_md}")

df_fdr.to_csv(RESULTS / "v38_statistical_addenda_empirical_fdr.csv", index=False)
df_rule.to_csv(RESULTS / "v38_statistical_addenda_rule_fdr.csv", index=False)
df_ctbh.to_csv(RESULTS / "v38_statistical_addenda_ctstratified_bh.csv", index=False)
df_bb.to_csv(RESULTS / "v38_statistical_addenda_block_bootstrap.csv", index=False)
df_bh.to_csv(RESULTS / "v38_statistical_addenda_classlevel_bh.csv", index=False)
df_cp.to_csv(RESULTS / "v38_statistical_addenda_clopper_pearson.csv", index=False)
pd.concat([df_auc5.assign(analysis="Table1_phase35"),
           df_aucsim.rename(columns={"metric": "metric"}).assign(analysis="groundtruth_sim")],
          ignore_index=True).to_csv(
    RESULTS / "v38_statistical_addenda_auc_ci.csv", index=False)
log("Wrote CSV outputs:")
for fn in ["v38_statistical_addenda_empirical_fdr.csv",
           "v38_statistical_addenda_rule_fdr.csv",
           "v38_statistical_addenda_block_bootstrap.csv",
           "v38_statistical_addenda_classlevel_bh.csv",
           "v38_statistical_addenda_clopper_pearson.csv",
           "v38_statistical_addenda_auc_ci.csv"]:
    log(f"  results/{fn}")

# console summary of headline numbers
log("\n===== headline numbers =====")
r = df_rule.iloc[0]
log(f"empirical FDR (Strong rule):        {r['FDR_emp=Vbar/R']}")
r = df_rule.iloc[3]
log(f"empirical FDR (Strong & p<0.05):    {r['FDR_emp=Vbar/R']}")
log(f"gradient_fold 6.88  CI:             [{df_bb.iloc[0]['CI_low']}, {df_bb.iloc[0]['CI_high']}]")
log(f"Astrocyte mu_ct 76.83 CI:           see block_bootstrap table")
log(f"Bergmann q (1-sided/2-sided/panel): {berg['q_BH_one_sided']} / "
    f"{berg['q_BH_two_sided']} / {berg['q_BH_fixed_panel']}")
log(f"CP upper 0/10:                      {cp_upper(0, 10):.4f}")
log(f"CP upper 0/150 (delta=1, omega):    {cp_upper(0, 150):.4f}")
log(f"Table1 omega AUC 0.680 CI (clust):  "
    f"[{df_auc5.iloc[0]['cluster_boot_CI_low']}, {df_auc5.iloc[0]['cluster_boot_CI_high']}]")
log(f"sim omega AUC 0.804 CI:             "
    f"[{df_aucsim[df_aucsim['metric'] == 'omega'].iloc[0]['CI_low']}, "
    f"{df_aucsim[df_aucsim['metric'] == 'omega'].iloc[0]['CI_high']}]; "
    f"P(omega>k_f) = {p_rank:.3f}")
log("Done.")
