# -*- coding: utf-8 -*-
"""
notebooks/84_dirichlet_overdispersed_dimension.py
==================================================
Q5 扩展模拟：Note 16 维度不变性结论的外推边界。

Note 16 原口径：对称 Dirichlet(alpha=2) 随机对，d=50..5000，mean JS 0.155-0.159，
ratio(d=2000/d=1130)=1.001 —— 只覆盖“稠密、群体水平、无采样噪声”一族。

本脚本扩展到三族更真实的零模型，检验 mean JS 的维度依赖性是否仍然可忽略：

  (A) 群体水平 Dirichlet，浓度 alpha in {0.1, 1, 2, 10}
      （alpha=2 为 Note 16 原基线，作连续性校验；alpha->0 越稀疏/越聚集）
  (B) 零膨胀稀疏混合：先 Dirichlet(alpha=2)，再随机将比例 z 的条目置零并重归一，
      z in {0.5, 0.8, 0.9}（模拟单细胞表达的结构性零）
  (C) Dirichlet-multinomial 有限计数采样：p_true ~ Dirichlet(2)，
      两个独立多项计数样本（Poisson 分裂精确等价），总计数 N in {1e4, 1e5, 1e6, 1e7}
      —— 卡方近似理论预测 E[JS] ~ (d-1)/(4*N*ln2)（base-2），
      本族是“同分布仅采样噪声”的零假设，直接量度采样偏差项的维度标度。

d in {50, 1130, 2000, 5000}（1130=HK 面板维数，2000=HVG 上限），
每格 2,000 对，seed 42，全向量化 numpy（gamma/Poisson 技巧）。

产物：
  results/dirichlet_overdispersed_dimension.csv
  results/dirichlet_overdispersed_dimension_report.md
"""
import numpy as np
import pandas as pd
from pathlib import Path

LN2 = np.log(2.0)
DIMS = [50, 1130, 2000, 5000]
N_PAIRS = 2000
SEED = 42

OUT_CSV = Path("results/dirichlet_overdispersed_dimension.csv")
OUT_MD = Path("results/dirichlet_overdispersed_dimension_report.md")


def js_batch(p, q):
    """行向量化 JS 散度（base-2），p/q: (n, d) 概率矩阵，允许 0（0log0=0）。"""
    m = 0.5 * (p + q)

    def ent(x):
        with np.errstate(divide="ignore", invalid="ignore"):
            t = np.where(x > 0, x * np.log2(x), 0.0)
        return -t.sum(axis=1)

    return ent(m) - 0.5 * (ent(p) + ent(q))


def dirichlet_rows(rng, n, d, alpha):
    """gamma 技巧向量化 Dirichlet：X~Gamma(alpha,1) 行归一。"""
    x = rng.gamma(shape=alpha, scale=1.0, size=(n, d))
    return x / x.sum(axis=1, keepdims=True)


def zero_inflate(rng, p, z):
    """随机将每行比例 z 的条目置零并重归一（结构性零混合）。"""
    n, d = p.shape
    keep = rng.random((n, d)) >= z
    q = p * keep
    s = q.sum(axis=1, keepdims=True)
    s[s == 0] = 1.0  # 理论不可达（z<1, d>=50），防御
    return q / s


def multinomial_rows(rng, p_true, n_counts):
    """Poisson 分裂：X_j ~ Pois(N*p_j) 独立 => 行归一与 Multinomial(N,p)/N 同分布。"""
    x = rng.poisson(lam=n_counts * p_true)
    s = x.sum(axis=1, keepdims=True)
    s[s == 0] = 1.0
    return x / s


def main():
    rng = np.random.default_rng(SEED)
    rows = []

    alphas = [0.1, 1.0, 2.0, 10.0]
    zs = [0.5, 0.8, 0.9]
    ns = [10_000, 100_000, 1_000_000, 10_000_000]

    for d in DIMS:
        # ---- Family A: population-level Dirichlet ----
        for a in alphas:
            p = dirichlet_rows(rng, N_PAIRS, d, a)
            q = dirichlet_rows(rng, N_PAIRS, d, a)
            js = js_batch(p, q)
            rows.append(dict(family="A_dirichlet", param="alpha", value=a, d=d,
                             mean_js=js.mean(), sd_js=js.std(ddof=1),
                             median_js=np.median(js),
                             theory_js=np.nan, emp_over_theory=np.nan))

        # ---- Family B: zero-inflated sparse mixture ----
        for z in zs:
            p = zero_inflate(rng, dirichlet_rows(rng, N_PAIRS, d, 2.0), z)
            q = zero_inflate(rng, dirichlet_rows(rng, N_PAIRS, d, 2.0), z)
            js = js_batch(p, q)
            rows.append(dict(family="B_zero_inflated", param="z", value=z, d=d,
                             mean_js=js.mean(), sd_js=js.std(ddof=1),
                             median_js=np.median(js),
                             theory_js=np.nan, emp_over_theory=np.nan))

        # ---- Family C: Dirichlet-multinomial finite counts (same-distribution null) ----
        for n in ns:
            p_true = dirichlet_rows(rng, N_PAIRS, d, 2.0)
            ph = multinomial_rows(rng, p_true, n)
            qh = multinomial_rows(rng, p_true, n)
            js = js_batch(ph, qh)
            theory = (d - 1) / (4.0 * n * LN2)  # chi-square leading order, base-2
            rows.append(dict(family="C_multinomial", param="N", value=n, d=d,
                             mean_js=js.mean(), sd_js=js.std(ddof=1),
                             median_js=np.median(js),
                             theory_js=theory,
                             emp_over_theory=js.mean() / theory))

    df = pd.DataFrame(rows)
    df["n_pairs"] = N_PAIRS
    df["seed"] = SEED

    # 族内相对维度标度：mean(d) / mean(d=1130)
    df["ratio_vs_d1130"] = np.nan
    for (fam, val), idx in df.groupby(["family", "value"]).groups.items():
        sub = df.loc[idx].set_index("d")
        ref = sub.loc[1130, "mean_js"]
        df.loc[idx, "ratio_vs_d1130"] = (sub["mean_js"] / ref).values

    df = df[["family", "param", "value", "d", "n_pairs", "seed",
             "mean_js", "sd_js", "median_js", "ratio_vs_d1130",
             "theory_js", "emp_over_theory"]]
    df.to_csv(OUT_CSV, index=False)

    # ---- report ----
    lines = ["# Q5 extended dimensionality simulation (notebooks/84)",
             "",
             f"n_pairs={N_PAIRS}, seed={SEED}, dims={DIMS}", ""]
    for fam, g in df.groupby("family"):
        lines.append(f"## {fam}")
        for val, gg in g.groupby("value"):
            gg = gg.sort_values("d")
            rng_js = f"{gg.mean_js.min():.4f}-{gg.mean_js.max():.4f}"
            r2 = gg.loc[gg.d == 2000, "ratio_vs_d1130"].iloc[0]
            r5 = gg.loc[gg.d == 5000, "ratio_vs_d1130"].iloc[0]
            extra = ""
            if fam == "C_multinomial":
                eot = gg.emp_over_theory.mean()
                extra = f", emp/theory={eot:.2f}"
            lines.append(f"- {gg.param.iloc[0]}={val}: mean JS {rng_js}, "
                         f"ratio d2000/d1130={r2:.3f}, d5000/d1130={r5:.3f}{extra}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(df.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print(f"\nWrote {OUT_CSV} and {OUT_MD}")


if __name__ == "__main__":
    main()
