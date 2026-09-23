# nc52 brain implementation audit (W-brain)

NC v52 修订：R4（脑图谱）+ R1（统计）Major 对应的四项新分析。所有脚本 `notebooks/nc52_*.py`，
结果 `results/nc52_*`，种子 42。环境：`cki_env/Scripts/python.exe`（venv；conda 命令不存在，
环境为仓库内 venv）。

## 共享提取（nc52_brain_extract.py）

- 输入：`data/brain/Nonneurons.h5ad`（888,263 核 × 59,480 基因；X 为 int16 原始计数）、
  `cki/data/hrt_atlas.csv`（HK 基因；与 script 86/96 一致——`_paths.py` 的 HK_FILE 指向
  `data/housekeeping/Human_Mouse_Common.csv`，与本文件内容一致，hk 匹配 1,115 个）。
- 方法：两遍顺序扫描。pass 1 全局基因和 → HVG（HK 1,115 + 非 HK 全局均值 top-5,000 =
  6,115 基因，与 86/96 同口径）+ 每核 total counts；detected genes = indptr 差分。
  pass 2 提取 Astrocyte + Bergmann glia 共 163,066 细胞的 reduced-gene CSR
  （uint16，277.4M nnz）。
- **质量代理声明**：atlas obs 无 PMI/RIN 及任何 per-cell QC 列（已核实 obs 仅含
  ontology/dissection/donor/roi/sample 字段），故用矩阵计算的 detected genes/nucleus 与
  total UMI/nucleus 作为 RNA 质量代理。
- 输出：`nc52_brain_ab_cells.npz`、`nc52_brain_ab_cellmeta.csv`、`nc52_brain_genes.json`、
  `nc52_brain_group_counts.csv`（ct×roi×donor 计数，1,980 行）、
  `nc52_brain_quality_classlib.csv`（ct×library 质量聚合）、
  `nc52_brain_quality_classregion.csv`（ct×roi 质量聚合）。
  （注：`nc52_brain_ab_cells.npz` 412MB 与 `nc52_brain_ab_cellmeta.csv` 8.8MB 为可再生的
  中间产物，未纳入 git；由 `nc52_brain_extract.py` 3 分钟可重建。）
- 运行 3m09s。确定性（无随机）。

## 关键实现事实（调试结论）

- `cki.core.js_divergence` 对 log1p pseudobulk 子向量先做 **softmax**
  （`ensure_probability_distribution` 默认 mode="softmax"：exp(x−max)/(Σ+1e−9)），
  不是按和归一化。所有 nc52 向量化 JS 均按此口径逐行实现。
- 管线校验门（写进 nc52_brain_donor_bootstrap.py，bootstrap 前硬断言）：
  identity-donor equal-n 20 复本梯度 = **1.754 [1.654, 1.847]**（published 1.74 [1.64, 1.84]）；
  span-matched observed = **3.685 / 4.298**（published 3.68 / 4.30）。另用 script 96 逐字副本
  （`notebooks/_nc52_tmp_96_verify.py`，输出改 _tmp 名）在本环境复现 1.7406，且其 rep0
  pseudobulk 上本管线各分量 15 位有效数字一致（astro om 20.28、berg om 11.04、grad 1.837…）。

## A2 donor-level cluster bootstrap（nc52_brain_donor_bootstrap.py）

- 输入：上述提取产物。
- 方法：
  - equal-n 梯度（astro/Bergmann 类均值 ω 之比）：donor cluster bootstrap B=1,000
    （seed 42；4 donor 有放回重采样，被抽中 donor 保留其全部细胞/对结构，重复抽中按重数计）；
    每个复本完整重跑 equal-n 管线（类总量→最小类 target→按比例分配→细胞级无放回下采样→
    per-pair top-200 k_f、HK k_n、ω→类均值→梯度）。仅 4 个簇 → 同时报 LODO（每缺失 donor
    20 个下采样复本）与 donor×region 块级 bootstrap（B=1,000，类内重采样 (donor,roi) 块）。
  - span-matched 梯度：每复本由重采样 donor 的细胞重建 7 个 cerebellar 区域的全深度
    pseudobulk，重算 ratio-of-class-means 与 21 对配对中位数比（对间经共享 donor 的依赖性
    由此进入抽样分布）。
- 结果（B=1,000，seed 42；identity-donor observed = 1.754 [1.654, 1.847] 通过校验门）：
  - **donor cluster bootstrap：median 1.560，95% CI [0.804, 2.336]**（n=998/1,000 有效；
    12.6% 复本 < 1，min 0.627）。4 簇 → 分布粗离散，按预案同时报：
  - **LODO 梯度范围 [0.931, 1.763]**：去 H18.30.001（最小 donor）1.763；去 H18.30.002
    （最大 donor）1.085；去 H19.30.001 **0.931**；去 H19.30.002 1.374（各 20 下采样复本均值）。
  - **donor×region 块级 bootstrap：median 1.385，95% CI [0.758, 2.134]**（16.3% 复本 < 1）。
  - **结论性数字：donor 层区间不排除 1。** equal-n 全脑残余梯度（1.74）在 donor 层面
    不可与 donor 组成区分——仅 4 个 donor 且 Bergmann glia 仅存在于 3 个 donor。
  - span-matched（published 3.68 / 4.30 [3.40, 4.95]；observed 校验 3.685 / 4.298）：
    **donor cluster bootstrap ratio-of-means 3.280 [1.670, 3.973]；paired median
    3.988 [2.558, 4.298]——两个统计量的 donor 层区间均排除 1**（frac<1 = 0）；
    LODO 四个值 3.685 / 3.280 / 1.670 / 3.193 全部 > 1。
- 输出：`nc52_brain_gradient_donor_bootstrap.csv`（3,989 行 per-replicate 长表）、
  `nc52_brain_gradient_donor_bootstrap.json`（汇总+CI）。

## C2 equal-n × span-matched 组合对照（同脚本）

- 方法：两类同时限制在 Bergmann 的 7 个 cerebellar 区域（21 region pairs），同时 equal-n
  下采样（target = 两类在该 7 区域内的较小类总量 = 7,965 细胞/类，按比例跨区域分配，
  无放回；R=20，seed 42）；donor cluster bootstrap B=1,000 + LODO。
- 结果：
  - observed（R=20）：**3.660 [3.598, 3.705]**（target 7,965 细胞/类 = Bergmann 在该 7
    区域的总量，即 Bergmann 基本不抽样、astrocyte 下采样到同量）。
  - **donor cluster bootstrap：median 3.275，95% CI [1.918, 3.779]**（n=995/1,000，
    frac<1 = 0，min 1.298）——组合对照在 donor 层排除 1。
  - LODO：3.676 / 3.260 / 2.306 / 3.219，全部 > 1。
  - 解读：在解剖跨度匹配的小脑内部，astro/Bergmann 梯度 ~3.3–3.7 对 donor 重采样与
    样本量均衡均稳健（全深度 3.68、equal-n 3.66）；全脑 equal-n 1.74 的衰减主要来自
    跨度差异（astro 对遍及全脑 vs Bergmann 对仅小脑），且该全脑估计 donor 层不稳健，
    稿面应以 span-matched/combined 为梯度主证据。
- 输出：`nc52_brain_combined_equaln_spanmatch.csv`（20 个 observed 复本）。

## C1 (class,library) 水平质量回归（nc52_brain_quality_regression.py）

- 输入：`results/nc49_brain_drift_ladder.csv`（4,906 对）、
  `results/reviewer_brain_pair_kf_kn.csv`（31,764 对）、上述质量聚合。
- 方法：①(class×library) 对级：log10(k_n/k_f/ω) ~ |Δlog detected| + |Δlog depth| +
  |Δlog n_cells| + tier 哑变量；报质量加入前后 T3（跨区域）系数变化。②(class×region) 对级：
  log10(metric) ~ 质量 + 类哑变量；ω 残差化后重算 astro/Bergmann 梯度。
- 关键数字：
  - 梯级对级 R²（仅 tier → +质量）：k_n 0.208→0.225；k_f 0.430→0.442；ω 0.231→0.300。
  - T3 系数（log10，质量调整前→后）：k_n 0.492→0.469；k_f 0.750→0.688；ω 0.257→0.219。
    **区域（T3）抬升在质量调整后基本保留**（ω 仅衰减 15%）。
  - 区域对级：ω R² 0.551（仅类）→0.556（+质量）；**梯度 6.10 → 质量调整后 6.33**。
    区域梯度不被 RNA 质量差异解释（调整后反而略升）。
- 输出：`nc52_brain_quality_regression_classlib.csv`（level 列区分两级）。确定性。

## C3 候选筛查效应量（nc52_brain_candidate_effectsize.py）

- 输入：`results/phaseC_omega_pair_vs_global.csv`（31,764 对，per-pair 与 global-k_n ω）、
  `results/brain_bs_null_observed_pairs.csv`（multiplicative residual + tier）。
- 方法：复算 Supp Fig 7b 相关；在 global-k_n ω 上用同一 multiplicative 模型
  （expected = μ_ct×μ_pair/μ_grand）与同一 Strong 规则（residual<0.3, ω<15, 对内最低）
  重算候选集合，比较与 published 39 个 Strong 的重合。
- 关键数字：
  - Spearman ρ = **0.142**（复算与 published 一致），ρ² = **0.020**（共享方差 ~2%）；
    每对 |log2 FC| 中位数 = 1.14。
  - 用 per-pair ω 重算 Strong = **39/39 完全复现**（验证规则正确）；用 global-k_n ω 重算
    Strong = 107 个；**仅 3/39 保留**（7.7%），36 丢失、104 新增；残差秩相关仅 0.337。
  - 结论（供稿面降级叙事，≤150 词）：k_n 估计器选择对 ω 排序影响极大
    （两估计器仅共享 ~2% 排序方差）。区域候选集合对估计器高度敏感：global-k_n 口径下
    39 个 Strong 候选仅 3 个保留且新增 104 个。因此候选筛查只能作为
    hypothesis-generating 名单（手稿已如此定位），不宜按具体 (cell_type, region_pair)
    逐条解读生物学；block-shuffle 零模型下的类水平结论（区域结构显著抬升 ω）不依赖
    单一候选的稳定性。
- 输出：`nc52_brain_candidate_effectsize.csv`。确定性。

## 运行日志与临时文件

- 日志：`results/audit/_nc52_brain_donor_bootstrap.log`。
- 调试用临时文件（不提交）：`notebooks/_nc52_tmp_96_verify.py`、
  `results/_nc52_tmp_replicates_kfkn.csv`、`results/_nc52_tmp_kfkn_summary.json`、
  `results/_nc52_tmp_pbs_rep0.npz`。
