# nc52 统计重采样实现审计（R1 统计 / R2 单细胞 Major）

脚本：`scripts/nc52_stats_resampling.py`（单脚本四节；B=5,000，seed=42；仿真模块既有种子 42/137/2024 沿用）。
运行：`./cki_env/Scripts/python.exe scripts/nc52_stats_resampling.py`（本机无全局 conda；仓库内 venv `cki_env`，Python 3.14.4，`scripts/spot_check.py` 全部通过）。
未触碰 `generate_manuscript_nc.py`、`notebooks/68_gen_supplementary_nc.py`、`99_build_nc_v49.py`、`results/audit/` 既有 verify 脚本。

## A1 — 7.70 split-half 基线的两阶段 bootstrap

数据：`results/mouse_splithalf_v44.csv`，6 个 FACS 群体 × 50 split-half = 300 值，总均值 7.696。
群体间异质性大：Liver hepatocyte 12.44±5.98，Marrow neutrophil 5.77±2.67，Spleen B cell 6.37±0.93。

| 方法 | 95% CI |
|---|---|
| **两阶段 bootstrap（B=5,000；先抽 6 群体、再抽群内 50 值）** | **[6.380, 9.818]** |
| 单阶段 iid(300) bootstrap（≈ 既有 v44 口径） | [7.308, 8.109]（v44 公布 [7.37, 8.02]） |
| 6 群体均值 t 区间（df=5） | [5.180, 10.211] |
| leave-one-population-out 范围 | [6.748, 8.081]（非 CI，敏感性诊断） |

结论：把 300 个值当独立观测的既有区间 [7.37, 8.02] **反保守**；两阶段区间宽约 3.44（相对半宽 ±21.1%），t 区间更宽（±32.6%）。LOPO 下界 6.75 与两阶段下界 6.38 同向，三角验证一致。

对 ω_cal = ω/7.70 的含义（Note 3 论证）：基线相对半宽从公布的 ±4.2% 放宽到 ±21.1%；ω_cal = 1 的诱导 95% 范围为 [0.784, 1.207]，ω_cal = 2 为 [1.568, 2.413]。即 ω_cal 只承载约 1 位有效数字的校准精度，报告超过 ~0.1 绝对分辨率会夸大校准常数。

输出：`results/nc52_stats_baseline_twostage_bootstrap.csv` / `.json`。

## A2b — Tabula Sapiens entry-clustered bootstrap

数据：`results/phase35_all_metrics_pairs.csv`，4,851 对嵌套于 99 个 (organ, cell_type) pseudobulk entries（配对为二元数据，独立性假设不成立）。
方法：重采样 99 个 entries（B=5,000），配对权重 = 两端点重数的乘积，加权 Spearman（秩预先固定，仅权重变）。对照：pair 级 iid bootstrap。

| ω vs | 观测 r | cluster bootstrap 95% CI | naive pair CI | SE 放大 |
|---|---|---|---|---|
| Raw JS | −0.396 | [−0.536, −0.227] | [−0.421, −0.372] | 0.079 vs 0.013（6.3×） |
| Spearman dist | −0.461 | [−0.576, −0.335] | [−0.483, −0.439] | 0.062 vs 0.011（5.5×） |
| Cosine dist | −0.386 | [−0.518, −0.226] | [−0.411, −0.362] | 0.074 vs 0.013（5.9×） |
| Marker Jaccard | −0.358 | [−0.506, −0.188] | [−0.383, −0.333] | 0.081 vs 0.013（6.2×） |

结论：按独立观测的 P 值（P < 10⁻¹⁴⁵ 等）无效；entry 聚类后标准差放大约 6 倍。四条相关在聚类 CI 下仍全部显著异于 0（区间不含 0），方向与量级结论稳健，但精度表述必须改用 cluster CI。

输出：`results/nc52_stats_tabula_entrycluster.csv`。

## A4 — AUC CI 方法、matched-threshold sensitivity、分背景

数据：`results/groundtruth_simulation_raw.csv`（marrow B cell 背景）与 `groundtruth_simulation_background2_raw.csv`（keratinocyte stem cell 背景）。AUC 定义与 #45 一致：signal = δ≥0.25（600 reps，3 个 module seeds × 4 δ × 50）vs neutral = neutral_hk+neutral_global（250）。

### (a) AUC 0.804 的 CI —— 两种方法

| 方法 | ω AUC 95% CI |
|---|---|
| DeLong | [0.770, 0.838] |
| module-seed 聚类 bootstrap（3 簇；signal 侧按 seed 重采样、neutral 侧 iid） | [0.771, 0.836] |
| 既有公布 [0.777, 0.831] | 与 DeLong 基本一致（原方法未记录，数值上最接近 DeLong/正态近似） |

k_f：DeLong [0.677, 0.755]，cluster [0.679, 0.751]。两方法在所有 6 个指标上一致（见 CSV）；注意 module seed 仅 3 簇，聚类 bootstrap 分布离散（27 种组合），此处簇间方差小故两法接近。

### (b) matched-threshold sensitivity（marrow 背景，中性分布定阈值）

| 指标 | spec=0.90 | spec=0.95 | spec=0.99 |
|---|---|---|---|
| ω | 0.420 | 0.273 | 0.038 |
| k_f | 0.323 | 0.152 | 0.048 |
| k_n | 0.297 | 0.150 | 0.050 |
| k_total | 0.250 | 0.250 | 0.250 |
| cosine | 0.245 | 0.235 | 0.080 |
| kf_over_kt | 0.003 | 0.000 | 0.000 |

在常用 spec=0.90/0.95 档 ω 灵敏度最高；spec=0.99 极端档 k_total/cosine 反超（但其 type-I 失控，见 D 表）。

### (c) 分背景 AUC 与 δ=1 检测 power

| 背景 | 指标 | 混合 AUC（DeLong CI） | δ=1 AUC | δ=1 power（自身 null-95 阈值） |
|---|---|---|---|---|
| marrow B cell | ω | 0.804 [0.770, 0.838] | 0.849 | **0.000** |
| keratinocyte | ω | 0.908 [0.888, 0.928] | 0.992 | **0.913** |
| marrow | k_f | 0.716 [0.677, 0.755] | 0.759 | 0.013 |
| keratinocyte | k_f | 0.859 [0.834, 0.883] | 0.990 | 0.927 |

关键发现：审稿人引用的 "keratinocyte 0.91 vs marrow 0.00"（δ=1）是**阈值检测 power**，不是 AUC。marrow 背景上 ω 的 null-95 阈值（20.81）高于 δ=1 信号分布，power=0 而 AUC 仍有 0.849 —— 基于绝对阈值的检测口径强背景依赖，AUC 口径背景依赖较弱。回复 R1/R2 时应明确区分两种口径。

输出：`results/nc52_stats_auc_ci_methods.csv`（长表：A4a/A4b/A4c 三节；A4c 中 clusterboot_ci_lo/hi 两列分别承载 δ=1 AUC 与 δ=1 power，note 列注明）。

## D — ω 相对 k_f 的真实数据增量

### (a) 逐基准对照表（15 行，`results/nc52_stats_omega_vs_kf_realdata.csv`）

裁决（一句话）：**ω 对 k_f 的增量价值在于"校准与抗混杂"而非"原始检出力"** —— 仿真中 ω 检出 AUC +0.05~0.09（0.80 vs 0.72；0.91 vs 0.86），在 4:1 失衡下 k_f 误检率 0.38 而 ω 为 0.00；真实 Kang 数据上 ω 更保守是设计使然（CD14 monocyte：k_f AUC 0.98 被中性/组成漂移推高，ω 0.55 正确打折扣；30 对技术重复零假设下 ω 与 k_f 均 0/30，raw_js 11/30、cosine 7/30 失控）；microglia atlas 大效应下 ω 与 k_f 均 AUC=1.00 无分离。

### (b) ω–k_f 负相关/相关的"数学必然"成分（k_n 置换 1,000 次，seed 42）

| 数据集 | n | 观测 Spearman(ω, k_f) | 数学地板（k_n 打乱后均值 [95% 区间]） | 残差 |
|---|---|---|---|---|
| Tabula Sapiens human（phase33, 5,151 对） | 5151 | 0.089 | 0.524 [0.506, 0.541] | **−0.435** |
| Mouse full matrix（703 对） | 703 | 0.821 | 0.857 [0.842, 0.869] | −0.036 |

地板定义：ω_perm = k_f / k_n_perm（k_n 打乱），corr(ω_perm, k_f) —— 共享分子 k_f 在数学上强制的相关。解读：human 真实数据中观测 ω–k_f 相关（0.089）**远低于**数学地板（0.524），即真实 k_n 结构主动把 ω 与 k_f 去相关，ω 携带 k_f 之外的真实信息；mouse 中观测（0.821）恰在地板上，相关完全由共享分子解释、无额外生物耦合。两个方向都不支持"ω 与 k_f 的（去）相关是数学 trivial"的反向指控——数学必然成分已被定量剥离。

输出：`results/nc52_stats_omega_kf_math_floor.csv`。

### (c) scDist 原始 R 实现可行性

`R --version`：本机无 R（command not found）。维持 `notebooks/101_competitors_v44.py` 的 Python 近似（PC 空间逐 PC OLS：PC ~ condition + donor 固定效应；距离 = sqrt(Σ β²λ)），脚本内已明确标注 "Python approximation of scDist"。

公平性论证措辞（可用于 response letter）：
> The original scDist is distributed as an R package; R is not available in our analysis environment, so we re-implemented its core estimator in Python (per-PC OLS of PC scores on condition with donor fixed effects, distance = √Σⱼ βⱼ²λⱼ), explicitly labelled as an approximation. Known differences from the original implementation: (i) the R package uses a mixed-model variant with per-donor random effects and empirical-Bayes shrinkage, whereas our approximation uses fixed donor effects only — this conservatively absorbs donor variance rather than partitioning it; (ii) the original adds a bootstrap-based significance calibration which we replace by cross-method rank correlation (Spearman) rather than per-method P values, so no P-value comparability is claimed; (iii) PC space and normalization follow our pipeline rather than the scDist defaults. Because all three methods (CKI, MELD, scDist-approx) were run on the same cells, same normalization and same donor structure, the comparison is internally fair even if absolute scDist-approx distances may differ from the R original; conclusions rely only on sign agreement and rank correlation, not on absolute effect magnitudes.

## 文件清单

- `scripts/nc52_stats_resampling.py`
- `results/nc52_stats_baseline_twostage_bootstrap.csv` / `.json`
- `results/nc52_stats_tabula_entrycluster.csv`
- `results/nc52_stats_auc_ci_methods.csv`
- `results/nc52_stats_omega_vs_kf_realdata.csv`
- `results/nc52_stats_omega_kf_math_floor.csv`
- `results/audit/nc52_impl_stats.md`（本文件）
