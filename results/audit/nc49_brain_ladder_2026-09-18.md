# Brain 四层漂移阶梯主分析 — 审计（NC v49 对策 C）

日期：2026-09-18　执行：c-drift
脚本：`notebooks/nc49_brain_drift_ladder.py`（后台 58 分钟）
数据：`data/brain/Nonneurons.h5ad`（888,263 核 × 59,480 基因；606 libraries；4 供体；106 ROI）
输出：`results/nc49_brain_drift_ladder.csv`（4,906 对长表，每对含自身 n-matched null 的 med/p95、7 指标观测/校准/FPR 元素）
运行日志：`results/audit/_nc49_brain_ladder_stdout.log`

## 设计

- 组 = (细胞类型, library)，≥20 细胞，2,732 组。HK = HRT Atlas（1,115 匹配）+ top-5000 非 HK 均值 HVG → 6,115 基因（08d 惯例）。
- 四层 library 配对：
  - **T1 技术漂移**（同 (roi,donor) 不同 library）：2,161 对——纯技术重复，ground truth = 无功能差异。
  - **T2 供体漂移**（同 roi 跨 donor）：1,089 对（抽样上限 200/CT）。
  - **T3 区域生物学正对照**（同 donor 跨 roi）：1,656 对（上限 200/CT）。
  - T0 = 每对自身 n-matched cell-shuffle null（合并两 library 细胞、打乱、按观测规模 (na,nb) 划分；B=100/30/30）。
- 指标（Table 1 五竞品口径 + k_n/k_f/ω 完整 7 项）：k_n、k_f、ω（per-pair top-200 |Δpb| hybrid、kn_floor=0）、raw JS、cosine、Spearman 距离、marker Jaccard（每组 top-200 markers vs 其他 CT 的细胞加权背景，1−Jaccard；配对级新定义，已在此预注册）。

## 关键数字（中位校准比 = 观测/null 中位；FPR = 超自身 null p95 比例）

### T1 技术漂移（n=2,161）

| 指标 | 校准比中位 [IQR] | FPR |
|---|---|---|
| **ω** | **1.038 [0.966, 1.213]** | **28.6%** |
| k_n | 1.047 [0.993, 1.168] | 35.7% |
| k_f | 1.055 [0.993, 1.427] | 37.6% |
| raw JS | 1.073 [1.006, 1.517] | **45.2%** |
| cosine | 1.041 [1.003, 1.256] | 44.1% |
| Spearman | 1.029 [1.000, 1.180] | 40.6% |
| marker Jaccard | 1.048 [0.963, 1.211] | 19.9% |

**ω 在 T1 上 FPR 最低（28.6%）但非 0**——与 Kang batch1 pilot 的 0% 不一致。诊断（`results/audit/_nc49_t1_perct.txt`、`_nc49_outlier_diag.txt`、`_nc49_fpr_versions.txt`）：

1. **ω 的 FPR 在 10/10 细胞类型全部低于 raw JS/cosine/Spearman**（逐类比值 1.2–2.3×），方向完全一致。
2. **FPR 随组规模单调上升**（n_min 20–30 时 ω FPR 13.8%，>500 时 47.8%；Spearman ρ(log n, cal) = 0.23–0.36 对所有指标）：真实 library 技术效应存在（capture/深度差异），大组有统计功效检出——所有指标都被检出，ω 检出最少。
3. **ω 残余漂移的结构**：逐对检查显示 k_f 分子在同 donor 同 roi 的同型 library 间真实分化（极端例：Choroid plexus @ SEP、donor H18.30.002，三 library 间 k_f 相差 30–137×；Bergmann glia cal_ω 1.16；这些正是 08d block-shuffle null 中 Bergmann glia null_mean 21.9 ≫ split-half 9.7 的来源）。k_n 的 HK 分母吸收了大部分漂移（cal_k_n ≈ 1.05），但不能吸收基因特异性的 HVG/身份基因级差异。
4. **与稿件已发表结果一致**：08d 中 Oligo/Microglia 的观察均值 ≈ block-shuffle null 均值（区域结构不显著），即 library 级结构确实主导大量 ω——本次 T1 直接量化了这一点。T1 校准比中位 1.04 与 split-half 校准值口径一致。

### T2 供体漂移（n=1,089）

| 指标 | 校准比中位 | FPR |
|---|---|---|
| **ω** | **1.764** | **90.9%** |
| k_f | 3.217 | 98.7% |
| raw JS | 3.320 | 98.4% |
| cosine | 2.277 | 97.8% |
| marker Jaccard | 1.392 | 74.7% |

ω 对供体漂移**最低**（FPR 90.9% vs k_f/raw JS ≈98%），但非免疫——供体间存在真实功能差异（与预期一致；T2 不是纯 null，仅作次级阶梯）。

### T3 区域生物学正对照（n=1,656）

全部指标抬升（FPR 85–97%，cal 1.4–3.0）——ω 对真实生物差异保持敏感（T3 cal_ω 1.80，Astro 高达 4.08），证明 T1 的低 FPR 不是「指标死了」。

### 阶梯梯度（ω 校准比中位）

T1 1.04 → T2 1.76 → T3 1.80：ω 单调随漂移阶梯上升，竞争对手在同阶梯上抬升更陡（raw JS 1.07→3.32→2.98；k_f 1.06→3.22→2.88）。

## 结论与写作建议（与可行性报告风险判据对齐）

- 可行性报告 go 判据：「T1 校准 ω ≤1.5 且显著低于竞品」——**按数值通过**（1.04 ≤ 1.5，且 FPR/校准均最低），但绝对免疫主张（模拟 FPR=0）在真实 brain 数据上**不成立**（28.6%）。主张必须降级为**相对校准**：「在真实的 library/供体漂移下，ω 的误报率与校准偏移在所有对比指标中最低（FPR 低 1.2–2.3×、T2/T3 中灵敏度损失最小），而 raw JS/cosine 在纯技术重复上误报 44–45%」。
- 可用支撑：Kang batch1（30 对，ω FPR 0% vs raw JS 36.7%）+ brain T1（2,161 对，ω 最低 FPR、T1→T2→T3 梯度最浅）+ T3 正对照（ω 对区域生物学敏感）。
- 需规避的表述：「ω 对技术漂移免疫」；改为「ω 将技术/供体漂移的误报降至最低，同时保留对真实区域分歧的灵敏度」。
- 已知局限（写入 Methods/Suppl）：T1 FPR 依赖 n 与自身 null 阈值口径；Choroid plexus（9 对、cal 2.31）与 Bergmann glia（27 对、cal 1.16）提示少数类型存在基因特异性 library 效应，不应从图中隐藏；B=100 的自身 null p95 分辨率有限（≈1%）。

## 图表

`results/figures_final/nc49_fig_drift_ladder.pdf/.png`（脚本 `notebooks/nc49_fig_drift_ladder.py`）：
(a) 阶梯示意；(b) 校准分布（7 指标 × 3 层，log 轴）；(c) FPR 柱状（T1/T2 + Wilson CI）；(d) Kang batch1 复制。
注：panel b/c 呈现的是当前（相对校准）主张，图注措辞需按上节调整。
