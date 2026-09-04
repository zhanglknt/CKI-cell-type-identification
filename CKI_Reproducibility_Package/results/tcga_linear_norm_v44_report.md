# TCGA 线性归一化重算报告（v44 敏感性分析）

**日期**：2026-09-04
**触发**：盲审专家指出权威 TCGA 管线（`notebooks/06_phase34_v2.py`）对 log2(TPM+1) 做 softmax，数学上等价于 p_i ∝ (TPM+1)^{1/ln2} = (TPM+1)^1.4427，是一个未披露的幂变换。
**处理**：将概率映射替换为线性归一化 p_i = (TPM+1)/Σ(TPM+1)，其余逻辑（per-cancer 流式加载、expression>0 存在性扫描、mean TPM≥0.5 过滤、per-cancer HK 映射、per-pair top-200 |Δ| identity 基因、kn_floor=1e-4、seed 42、TT/TN 上限 2000、TT 抽样播种顺序）逐行镜像 v2。
**隔离设计**：identity 基因排序仍在 log2(TPM+1) 表示上进行（与 v2 完全一致），因此 identity 基因集合与权威运行相同，唯一变化是进入 JS divergence 的概率向量。
**seed**：42（与 v2 相同；本机 scipy 1.17.1 无 `jttest_on_ranks`，JT 检验使用与 83 号脚本一致的手工实现——即发表数值所用的同一回退路径）。

## 脚本与输出

| 脚本 | 内容 | 运行时长 |
|---|---|---|
| `notebooks/85_tcga_linear_norm_v44.py` | 主管线（5 癌种 TT/NN/TN，kn_floor=1e-4）+ 07/83 式 clinical severity（kn_floor=0） | 550 s |
| `notebooks/86_tcga_composition_linear_norm_v44.py` | composition v2 镜像（四 panel 含 myeloid、cluster bootstrap B=200） | 78 s |
| `notebooks/87_cross_organ_rho_ci_v44.py` | 83 Part A 重建 + CT 级 rank ρ 的 organ-clustered bootstrap CI（B=1000） | 175 s |

新输出文件（全部新文件，未覆盖任何既有权威结果）：
`tcga_linear_norm_v44_summary.csv`、`tcga_linear_norm_v44_all_pairs.csv`（35,306 pairs）、`tcga_linear_norm_v44_<cancer>_pairs.csv`（5 个）、`tcga_clinical_severity_v44.csv/.json`、`tcga_composition_v44.csv/.txt`、`cross_organ_rho_ci_v44.csv/.json/.txt`、日志 `_log_85/86/87_v44.txt`。

## 1. 主管线（v2 镜像）：旧值 vs 新值

omega 使用 v2 语义（kn_floor=1e-4）。基因/样本/HK 数与 v2 完全一致（如 LUAD 14,178 基因、1,125 HK），证实加载逻辑镜像无误。

| Project | ω_TT mean 旧→新 | ω_NN mean 旧→新 | ω_TN mean 旧→新 | TN/baseline 旧→新 | p 旧→新 |
|---|---|---|---|---|---|
| LUAD | 105.8 → 121.7 | 277.2 → 299.8 | 124.9 → 147.0 | 0.65 → 0.70 | 1.2e-67 → 2.5e-49 |
| LUSC | 98.2 → 114.1 | 196.4 → 207.8 | 98.7 → 119.2 | 0.67 → 0.74 | 1.1e-28 → 2.4e-14 |
| LIHC | 66.6 → 75.4 | 87.6 → 85.4 | 60.4 → 66.7 | 0.78 → 0.83 | 3.7e-28 → 1.9e-19 |
| KIRC | 110.6 → 124.7 | 228.8 → 236.4 | 125.2 → 146.5 | 0.74 → 0.81 | 5.6e-68 → 4.5e-37 |
| BRCA | 110.3 → 128.2 | 192.8 → 201.0 | 117.9 → 137.8 | 0.78 → 0.84 | 3.6e-33 → 3.1e-15 |

**k_n 反转（TT k_n > NN k_n，核心"分母主导"证据）**：

| Project | kn_TT median | kn_NN median | TT/NN 倍数 |
|---|---|---|---|
| LUAD | 2.45e-3 | 9.41e-4 | 2.6x |
| LUSC | 2.69e-3 | 1.00e-3 | 2.7x |
| LIHC | 4.06e-3 | 1.92e-3 | 2.1x |
| KIRC | 2.62e-3 | 7.20e-4 | 3.6x |
| BRCA | 2.41e-3 | 8.69e-4 | 2.8x |

- **NN>TT omega 反转为全部 5 癌种保留**（ω_NN > ω_TT，同旧版）。
- **TN<baseline 方向与显著性全部保留**；比值略向 1 衰减（0.65-0.78 → 0.70-0.84）。
- **k_n 反转全部保留**（TT k_n 为 NN 的 2.1-3.6 倍）。
- kn_floor=1e-4 饱和度：所有癌种所有 pair 类型 kn<1e-4 比例 = 0（线性映射下 kn ~7e-4 至 6e-3，不触 floor；floor 在新映射下不构成 artifact）。
- 结论判定：**主管线定性结论完全稳健**。

## 2. Clinical severity（07/83 镜像，kn_floor=0）

方向（旧 → 新，per-tumor TT 均值）：

| 分层 | 旧 omega 梯度 | 新 omega 梯度 | 检验 P 旧 → 新 |
|---|---|---|---|
| LIHC Edmondson | G1 73.5 > G2 67.0 ≈ G3 66.2 ≈ G4 66.2（降） | G1 82.4 > G2 74.7 ≈ G3 74.9 ≈ G4 75.0（降后平） | JT 0 → 0 |
| BRCA PAM50 | LumA 123.4 > LumB 116.6 > HER2 103.1 > Basal 97.8 > Normal 90.5 | LumA 142.0 > LumB 136.5 > HER2 121.8 > Basal 116.7 > Normal 101.9 | KW 7.9e-10 → 7.0e-7 |
| LUAD mutation | KRAS 118.1 > EGFR 107.0 > WT 100.5 | KRAS 136.9 > EGFR 122.2 > WT 115.4 | KW 2.1e-6 → 7.8e-7 |

k_f / k_n 分解（"分母主导"判据）：

| 分层 | k_f P 旧 → 新 | k_n P 旧 → 新 |
|---|---|---|
| LIHC (JT) | 1.06e-12 → 1.05e-12 | 0 → 0 |
| BRCA (KW) | 1.31e-11 → 8.32e-12 | 1.25e-10 → 3.58e-10 |
| LUAD (KW) | 1.50e-2 → 1.51e-2 | 3.21e-4 → 3.35e-4 |

- 三个 severity 梯度的**排序、方向、显著性全部保留**；数值系统性上移（omega +10~19），k_f 显著性、分母 k_n 的强梯度均不变。
- 结论判定：**severity 方向/显著性/分母主导格局完全稳健**（v44 仍应维持 exploratory 降级表述，但无需因映射问题进一步改变定性结论）。

## 3. Composition（74 镜像，pair 表换为线性归一化 kn）

pair 表 25,306（TT 10,000 + NN 15,306）与 73 完全一致（TT 子样本逐对复现）；panel 基因过滤结果与 74 逐基因一致；kn≤0 的 pair 数 = 0。

| 检验 | 旧（softmax） | 新（线性） |
|---|---|---|
| C4 pooled attenuation（4-panel） | -0.5% | -0.8% |
| BOOT pooled 4-panel 中位 [95% CI] | -0.4% [-3.2%, +2.6%] | -1.2% [-4.1%, +2.6%] |
| BOOT LIHC 4-panel | +33.5% [+23.0, +46.9] | +37.1% [+27.1, +51.5] |
| BOOT KIRC 4-panel | +19.6% [+14.6, +25.7] | +18.3% [+13.9, +23.4] |
| BOOT BRCA 4-panel | -14.0% [-23.2, -5.7] | -16.2% [-25.5, -7.5] |
| BOOT LUAD / LUSC 4-panel | -2.3% / -9.7% | -1.6% / -11.1% |
| C5 Spearman ρ(kn, dcomp4) pooled | 0.387 | 0.355 |
| C5 per-cancer | 0.233-0.519 | 0.146-0.492 |

- 结论判定：**组成分析结论不变**——pooled 组成衰减 ~0（CI 跨 0），"组成不能解释 k_n 反转"成立；LIHC/KIRC 的癌症内部分衰减格局保留。

## 4. Cross-organ rank ρ 的 bootstrap CI（新增）

83 Part A 重建通过 sanity（max |Δ mean omega| = 3.55e-15，17/17 CTs）。注意：87 因本机内存限制将 concat 管线改写为 per-organ 数学等价实现（filter_cells 为 per-cell 操作、filter_genes 用跨器官检测计数求和、normalize/log1p 为 per-cell 操作），sanity 已验证等价。

| 统计量 | 点估计 | organ-clustered bootstrap 95% CI（B=1000, seed 42） |
|---|---|---|
| CT 级 ρ(ω, k_f)，17 CTs | 0.233 (P=0.368) | 中位 0.186，[-0.083, +0.382] |
| CT 级 ρ(ω, k_n)，17 CTs | -0.309 (P=0.228) | 中位 -0.398，[-0.605, -0.167] |
| CT 级 ρ(ω, k_f)，well-sampled (n≥5, 5 CTs) | 0.100 | [-0.700, +0.900] |
| CT 级 ρ(ω, k_n)，well-sampled | -0.400 | [-0.900, +0.300] |
| （敏感性）CT 重抽样 ρ(ω, k_f) | — | [-0.470, +0.699] |
| （敏感性）CT 重抽样 ρ(ω, k_n) | — | [-0.795, +0.230] |

- 解读：r=0.23 的 95% CI 跨 0（[-0.08, +0.38]），与 P=0.37 一致——**k_f-only 不能恢复 cross-organ 排序**的结论在区间估计下成立（CI 不含强正相关）；ρ(ω, k_n) 为负且 cluster CI 不含 0，支持"排序主要由分母 k_n 驱动"。well-sampled 子集仅 5 个 CT，CI 极宽，不宜引用。
- 审稿措辞建议：可写 "CT-level concordance between omega and k_f rankings is low and not significantly different from zero (r = 0.23, organ-clustered bootstrap 95% CI [-0.08, 0.38])"。

## 5. 总体判定

**结论不改变**。线性归一化（无幂变换）下：severity 三梯度方向/显著性/分母主导格局保留；NN>TT 反转与 k_n 反转保留；组成 pooled 衰减 ~0 保留；cross-organ rank ρ 点估计不变（0.233）且新 CI 支持既有解读。TCGA 板块按 v44 计划降级为 vignette 在数值上成立。

## 异常与注意事项

1. 87 初次运行因 sc.concat 内存不足（ArrayMemoryError 1.17 GiB）失败；改写为 per-organ 数学等价实现后通过，sanity 3.55e-15 验证等价。
2. 87 的 joint bootstrap 初版按"整 replicate 拒绝"设计，因 2-organ CT 退化率过高在 200,000 次尝试内无法集满 1000 个有效 replicate；改为 per-CT 拒绝采样（各 CT 边际 bootstrap 分布不变），B=1000 全部有效。
3. 线性映射下 kn 不触 1e-4 floor（比例 0），与 softmax 版相同结论；`_v38_tcga_kn_floor_saturation.csv` 的 floor 饱和讨论在新映射下同样不适用。
4. 85 的 TN 对抽样沿用 v2 的随机流（seed 42 → TT 抽样后顺序抽样），与权威运行一致。
