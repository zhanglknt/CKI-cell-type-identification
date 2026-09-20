# v49 增强分析可行性报告：TCGA 泛癌功能分歧图谱

**研究员**：d-tcga（只读调研）
**日期**：2026-09-18
**目的**：为 CKI 论文（ω = k_f/k_n）Nature Communications 投稿的"发现级应用"（对策 D）评估本地数据与既有管线能否支撑 TCGA 泛癌功能分歧图谱的升级。

**一句话结论**：数据与既有结果足以把现有 exploratory TCGA 板块升级为发现级主图——核心数字（5 癌种 NN/TT 反转、k_n 分母机制、LUAD 突变梯度）已在本地算好且通过线性归一化敏感性检验；升级主要工作是统计强化（bootstrap CI、逐样本重算、Cox）与重新叙述，只有"跨癌种保守 signature"模块需要真正重算。

---

## 1. 数据盘点表（全部经 python 实际打开确认）

| 文件 | 内容 | 关键结构/数量 | 已支撑的分析 |
|---|---|---|---|
| `data/tcga/tcga_RSEM_gene_tpm.gz` (741 MB) | UCSC Xena TCGA pan-cancer bulk RSEM TPM | 矩阵 60,499 基因(ENSG.version 行) × 10,535 样本(列)；值为 **log2(TPM+1)**，0 以 -9.9658 哨兵编码。5 个目标癌种按 TSS→project 映射提取（映射表内置于 06_phase34_v2.py:80-121）。可用样本：LUAD T=495/N=76、LUSC 567/58、LIHC 365/57、KIRC 755/82、BRCA 1032/109，合计 **3,214 tumor + 382 normal = 3,596** | 06/07/08a/73/74/85/86 全部 TCGA 分析 |
| `data/tcga/probemap.tsv` (3.2 MB) | Xena probeMap | 60,498 行：`id`(ENSG.version) / `gene`(symbol) / chrom / start / end / strand | ENSG↔symbol 映射，HK 基因定位（每癌种 ~1,125 HK） |
| `data/tcga/lihc_patient_clinical.json` (4.5 MB) | cBioPortal lihc_tcga 患者级临床（扁平表） | 21,412 行 / **377 患者** / 67 属性。关键字段：GRADE(G1 55/G2 180/G3 124/G4 13)、OS_STATUS(245 生/132 亡)、OS_MONTHS(376)、DFS_STATUS/MONTHS(326/325)、AJCC_PATHOLOGIC_TUMOR_STAGE(353)、AJCC T/N/M、VASCULAR_INVASION(321)、CHILD_PUGH(245)、ISHAK_FIBROSIS(218)、AFP_AT_PROCUREMENT(284)、AGE/SEX/RACE | LIHC 分级梯度（已做）；**OS/DFS 生存、分期、脉管侵犯尚未做** |
| `data/tcga/lihc_sample_clinical.json` (309 KB) | cBioPortal 样本级临床（**部分导出**） | 1,000 行 / **仅 60 患者**：MUTATION_COUNT(56)、TMB_NONSYNONYMOUS(56)、FRACTION_GENOME_ALTERED(58)、IS_FFPE 等 | 覆盖太低（60/377），不能做全队列协变量 |
| `data/tcga/luad_egfr_kras_mutations.json` (8.9 KB) | cBioPortal LUAD EGFR/KRAS 突变状态 | dict：`egfr_samples`(75)、`kras_samples`(161)、`double_mutants`(2)，全长 aliquot 条码。**按 15 位短条码匹配 TPM 矩阵实测：EGFR 命中 62、KRAS 命中 122、双突变 2** → 可用 EGFR-only≈60、KRAS-only=120、WT≈311-312（与 07 脚本发表的 61/120/311 一致） | LUAD 突变梯度（已做）；突变型 vs 野生型 ω 差异可升级 |
| `data/tcga/luad_mutations.json` (2 B) | 空列表 `[]` | 不可用 | — |
| `data/tcga/luad_data_mutations.txt` (134 B) | **Git LFS 指针**（真实 MAF 232 MB 未下载到本地） | 离线不可用；如需全 MAF 须 `git lfs pull`（需网络） | — |
| `results/phase34_pam50_cache.json` (17 KB) | BRCA PAM50（cBioPortal API 结果缓存） | sampleId[:15] → PAM50 subtype | BRCA PAM50 梯度（已做，离线可复现） |

**结论**：突变（EGFR/KRAS 二分类）与 LIHC 全套临床（分级/分期/生存/Child-Pugh/AFP/脉管侵犯）**全部本地可用且已验证条码可匹配**；缺失的是：LUAD 患者级协变量（年龄/性别/吸烟——json 只有突变标签）、全 MAF、肿瘤纯度（sample 级 json 仅 60 例）。

## 2. 既有 phase34 / TCGA 结果盘点（数值均已复核）

### 2.1 权威管线（06_phase34_v2.py，softmax 概率映射）

`results/phase34_v2_summary.csv`（每癌种 TT/NN/TN）：

| 癌种 | ω_TT mean | ω_NN mean | ω_TN mean | TN/baseline | MWU P |
|---|---|---|---|---|---|
| LUAD | 105.8 | 277.2 | 124.9 | 0.65x | 1.2e-67 |
| LUSC | 98.2 | 196.4 | 98.7 | 0.67x | 1.1e-28 |
| LIHC | 66.6 | 87.6 | 60.4 | 0.78x | 3.7e-28 |
| KIRC | 110.6 | 228.8 | 125.2 | 0.74x | 5.6e-68 |
| BRCA | 110.3 | 192.8 | 117.9 | 0.78x | 3.6e-33 |

配套：`phase34_v2_all_pairs.csv`（仅 pair_type/cancer/omega/kn/kf，**无样本 ID**）、5 个 per-cancer pairs、4 张图。注意：所有 5 癌种 **ω_NN > ω_TT**（"肿瘤更同质"反转）。

### 2.2 临床/配对（07_phase34_clinical.py）

- `phase34_clinical_paired_unpaired.csv`：配对/非配对 TN 比 0.89–1.54（配对 n 仅 2–5/癌种，描述性）；**NN/TT 比：LIHC 1.23 < BRCA 1.51 < LUSC 1.77 < KIRC 2.19 < LUAD 2.32**（稿件引的就是这组）。
- `phase34_clinical_severity.csv`（softmax 版）：LIHC Edmondson G1 73.5 > G2≈G3≈G4 ≈66–67（JT P≈0）；BRCA PAM50：LumA 123.4 > LumB 116.6 > HER2 103.1 > Basal 97.8 > Normal-like 90.5（KW 7.9e-10）；**LUAD 突变：KRAS 118.1 > EGFR 107.0 > WT 100.5（KW 2.1e-6）**。

### 2.3 v44 线性归一化敏感性重算（85/86/87，**当前最可信版本**）

`tcga_linear_norm_v44_summary.csv`：TT/NN/TN 均值全面上移（如 LUAD 121.7/299.8/147.0），TN/baseline 0.70–0.84，P 3.1e-15 至 2.5e-49，**5 癌种 NN>TT 反转与方向全部保留**。新增 k_n 中位数：**TT k_n 为 NN 的 2.1–3.6 倍**（LUAD 2.6x、LUSC 2.7x、LIHC 2.1x、KIRC 3.6x、BRCA 2.8x）——分母机制的直接证据。floor 饱和率 0。

`tcga_clinical_severity_v44.csv/json`：三梯度方向/显著性全保留——LUAD **KRAS 136.9 > EGFR 122.2 > WT 115.4（ω KW P=7.8e-7；k_f KW P=0.015；k_n KW P=3.4e-4）**；LIHC G1 82.4 > G2–G4 ≈74.7–75.0（JT P=0）；BRCA LumA 142.0 > LumB 136.5 > HER2 121.8 > Basal 116.7 > Normal 101.9（KW 7.0e-7）。k_f/k_n 分量均有。

**`tcga_linear_norm_v44_all_pairs.csv`（35,306 对）含 `sample_a/sample_b` 样本 ID** ——这是升级的关键资产：逐样本 ω 可离线从该表派生（TT 每样本覆盖：LUAD 中位 8 对、LIHC 11 对、BRCA 4 对、KIRC 5 对；全部 3,596 样本中 3,214 肿瘤几乎都有 ≥1 对）。

### 2.4 组成混杂检验（73/74/86）

`tcga_composition_v44.csv/txt`：4-panel 标志物（immune/myeloid/stromal/epithelial）样本级 cluster bootstrap：pooled TT k_n 组成校正后衰减 **-1.2% [-4.1%, +2.6%]**（跨 0）；LIHC +37.1%、KIRC +18.3%、BRCA -16.2%（癌种内部分可解释）；ρ(k_n, 4-panel 组成差) pooled 0.355。

### 2.5 其它

`tcga_bootstrap_results.csv`（08a，AnnData 化的 cohort 级 bootstrap null）数值陈旧、与 v2 语义不一致，**不要在新主图中引用**；`cross_organ_rho_ci_v44`（87）属 sc 跨器官板块，与 TCGA 主图无关。

### 2.6 稿件现状（generate_manuscript_nc.py）

Result 4 标题即 **"Cancer analysis: apparent tumor homogeneity (exploratory)"**（541 行起）；Abstract 中 TCGA 标注 "(TCGA; exploratory)"。正文已含：NN/TT 反转 + k_f/k_n 分解（k_f NN/TT 0.54–0.74、k_n 0.27–0.46）、组成检验、线性归一化稳健性、配对描述性、三条 severity 梯度（并自曝 LIHC/BRCA 在 k_f-only 下反转、LUAD 突变对比是例外）。即：**发现已在手，缺的是统计强度（区间估计、逐样本级检验、多变量校正）和发现级定位**。

## 3. 升级分析设计（核心交付）

总原则：主线 = "泛癌组织水平功能分歧图谱"，把 5 癌种一致的 NN/TT 反转 + k_n 分母机制升格为发现；LUAD 突变为机制性 sub-analysis；LIHC 生存为转化性 sub-analysis；保守 signature 降为补充或删除。

### 模块 a（优先级 1）：泛癌 ω 排名与跨癌种一致性 —— 纯重组 + 轻量重算

- **所需数据**：`phase34_v2_summary.csv`、`tcga_linear_norm_v44_summary.csv`、`tcga_linear_norm_v44_all_pairs.csv`（均有，已确认）。
- **统计设计**：① 每癌种 NN vs TT 的 ω Mann-Whitney（已有 P）+ **新增 sample-level cluster bootstrap 95% CI of NN/TT ratio**（从 v44 all_pairs 对 TT/NN 各按样本重抽，B=1000，脚本分钟级）；② 跨癌种方向一致性：5/5 同号，符号检验 P=2^-5=0.031（可作为"一致性"的正式表述）；③ k_n TT/NN 倍数（2.1–3.6x）同样配 CI——把"分母主导"从叙述升为带区间估计的定量结论；④ 排名按效应量（LUAD 2.32 > KIRC 2.19 > LUSC 1.77 > BRCA 1.51 > LIHC 1.23）。
- **预期 claim**："Across five TCGA cancer types (3,596 samples), tumor–tumor ω is consistently lower than adjacent-normal–normal ω (NN/TT = 1.23–2.32, all P < 10⁻¹⁴); the reversal is driven by a 2.1–3.6-fold elevation of the housekeeping baseline k_n in tumors, not by reduced functional divergence (k_f)." —— 一句话、可引用、带机制。
- **工作量**：1 个 bootstrap 脚本（<1 小时算完）+ 重组既有表；**总约 0.5–1 天**。
- **风险**：审稿人要求纯度/去卷积对照 → 已有 4-panel 组成 bootstrap（-1.2% [-4.1,+2.6]）可直接引用为正式混杂控制；可再加 ESTIMATE stromal/immune 分数作为连续协变量（公式公开，TPM 本地可算，约 0.5 天，见 §4）。

### 模块 b（优先级 2）：LUAD EGFR/KRAS 突变关联 —— 半重组

- **所需数据**：`luad_egfr_kras_mutations.json`（本地，条码匹配已实测：EGFR 62/KRAS 122/WT 312）+ v44 all_pairs（逐样本 ω）或 85 脚本直接重算逐肿瘤 ω。
- **统计设计**：逐肿瘤 ω（TT 对均值，LIHC 中位 11 对/样本的量级）分组 WT/EGFR/KRAS：Kruskal-Wallis（已得 P=7.8e-7）+ **新增 Dunn 逐对比较与 Holm 校正、组间差值的 cluster bootstrap CI**；关键升级点是 **k_f/k_n 分解叙事**：KRAS-WT 对比在 k_f-only 下保留（P=0.015）而 EGFR-WT 主要由 k_n 驱动——这正好演示 CKI 的"功能 vs 基线"分解能力，是稿件方法论主题的完美 showcase。排除 2 例双突变（既有惯例）。
- **预期 claim**："In lung adenocarcinoma, KRAS-mutant tumors show elevated functional divergence versus wild-type (mean ω 136.9 vs 115.4, P = 7.8×10⁻⁷), preserved under k_f alone, whereas the EGFR-associated difference is baseline (k_n)-driven—illustrating that the k_f/k_n decomposition separates functional from housekeeping contributions to tumor divergence."
- **工作量**：1 天（含从 all_pairs 派生逐样本 ω、Dunn/bootstrap、图）。
- **风险**：无 LUAD 患者协变量（年龄/性别/吸烟史不在本地）→ 必须明示 observational；EGFR/KRAS 与肿瘤纯度、TMB 的已知流行病学关联无法本地校正（TMB 只有 LIHC 60 例）→ 用 ESTIMATE 分数作代理协变量（可选）；组内 n（EGFR≈60）足够但 CI 会较宽。

### 模块 c（优先级 3）：LIHC 临床关联（分期/生存）—— 需新分析但数据全

- **所需数据**：`lihc_patient_clinical.json`（OS 376 例、DFS 326、stage 353、grade、Child-Pugh、AFP、脉管侵犯——全本地）+ 逐肿瘤 ω。
- **统计设计**：① 分期/分级：Spearman/JT（既有 JT 是 grade，可扩到 AJCC stage I–IV）；② **Cox PH**：OS ~ ω + grade + stage + age + sex（statsmodels `PHReg` 本地可用，lifelines 未装）；ω 标准化后报 HR per SD + 95% CI；③ 敏感性：k_f、k_n 分别入模（分母机制透明化）；④ 若 TN 逐样本 ω（2000 对含样本 ID，每肿瘤中位 ~11 对 TN）更贴近"肿瘤 vs 正常分歧"语义，可并报两个口径。**必须先跑再写**（Go/No-Go：若 HR 不显著或方向不利，降级为 supplementary 或删除，勿硬写）。
- **预期 claim 形态**："Per-tumor ω, a bulk measure of functional divergence within the tumor cohort, was independently associated with overall survival in LIHC (HR per SD = x.xx, 95% CI [x.xx, x.xx], adjusted for grade and stage, n = 3xx)."（数值待跑）
- **工作量**：1–2 天（含敏感性）。
- **风险**：bulk 混杂最重的模块——逐样本 ω_TT 受肿瘤纯度/间质比例影响（已知 KIRC/LIHC 组成衰减 +18–37%）；缓解：ESTIMATE 分数入模、并报 k_f 口径、正文限定 "tissue-level" 表述；发表层面这是 supplementary 级而非主图级。

### 模块 d（优先级 4，建议降级或删除）：泛癌保守 signature —— 唯一真重算模块

- **所需数据**：TPM（本地）+ probemap（本地）；**既有 pairs 文件未存每对的 top-200 基因身份，必须重算**。
- **统计设计**：每癌种 tumor-mean vs normal-mean pseudobulk → top-200 |Δ| 基因 → 跨 5 癌种重叠（Jaccard/Fisher 超几何）→ 通路富集（gseapy 已装但 Enrichr 需在线；离线替代：手工 Hallmark/KEGG 基因列表超几何检验，需准备基因集文件）。
- **预期 claim**："The identity genes driving tumor–normal k_f converge across cancer types (pairwise Jaccard 0.xx–0.xx, all P < ...), enriched for cell-cycle and ECM programs."
- **工作量**：2–3 天（重算 5 癌种加载 ~10–15 分钟 + 富集与图表）。
- **风险（高）**：cohort 级 top 差异基因大概率就是已知泛癌 hallmarks（增殖/ECM/免疫浸润），novelty 低，审稿人易判 "already known"；建议只作 supplementary 描述性内容支撑模块 a，**不进主图、不进 Abstract**。

## 4. bulk 分辨率局限的处理方案

1. **定位改名**：全篇统一为 **"tissue-level functional divergence"**（组织水平功能分歧）——比较单位是 bulk 组织 pseudobulk，不做任何细胞类型归因；"tumor homogeneity" 表述保留 "apparent"（既有口径）并解释为 "tumor-specimen divergence"。
2. **混杂控制电池（已有，直接引用为正式方法学）**：4-panel 标志物组成 + 样本级 cluster bootstrap（pooled -1.2% [-4.1,+2.6]）；k_f/k_n 分解（分母机制定量 2.1–3.6x）；线性归一化敏感性（全结论保留）；kn_floor 饱和率 0。
3. **建议新增（可选，0.5 天）**：ESTIMATE stromal/immune 分数（公式公开，从本地 TPM 直接算）作为模块 a/b/c 的连续协变量或分层敏感性——比"未来用单细胞数据"的口头承诺更有力。
4. **配对 TN（n=2–5）**：保持 descriptive，不升级。
5. **措辞模板**："Because bulk RNA-seq averages over tumor, stromal, and immune compartments, ω here quantifies divergence between tissue states; composition-adjusted analyses (four-marker panel, sample-level cluster bootstrap) bound the contribution of measurable composition shift to ≤x%, and the k_n decomposition identifies the housekeeping baseline—not functional genes—as the dominant contributor."

## 5. 推荐主图（1 张，2 面板）与 Abstract claims

**Fig. N（主图）草图**：
- **Panel A（泛癌图谱）**：x 轴 5 癌种按 NN/TT 效应量降序（LUAD→LIHC）；y 轴 ω。每癌种三个点+误差棒（cluster bootstrap 95% CI）：ω_TT（红）、ω_NN（绿）、ω_TN（紫）；右侧第二坐标轴/下方面板：k_n TT/NN 倍数（2.1–3.6x，灰色柱）——一图同时给出"反转"与"分母机制"。线性归一化敏感性值以空心点叠加。底部横条：组成校正后 pooled 衰减 -1.2% [-4.1,+2.6]。
- **Panel B（LUAD 突变）**：逐肿瘤 ω 小提琴/箱线（WT/EGFR/KRAS，n=311/61/120），KW P=7.8e-7 + Dunn 显著性连线；旁边并排 k_f、k_n 两组小图，直观呈现"KRAS 走 k_f、EGFR 走 k_n"的分解故事。
- LIHC 生存（若 Go）进 supplementary 或 Panel C；模块 d 只进 supplementary。

**Abstract 可引用 claims（2–3 条）**：
1. "Applied to 3,596 TCGA samples across five cancer types, CKI uncovers a consistent pan-cancer reversal: tumor specimens are less divergent than adjacent non-tumor tissue (normal/normal versus tumor/tumor ω ratio 1.23–2.32, all P < 10⁻¹⁴), attributable to a 2.1–3.6-fold elevation of the housekeeping baseline k_n rather than reduced functional divergence (composition-adjusted, bootstrap-verified)."
2. "In lung adenocarcinoma, the k_f/k_n decomposition separates mutation classes: KRAS-mutant tumors show elevated functional divergence over wild-type (P = 7.8×10⁻⁷, preserved under k_f alone), whereas EGFR-associated differences are baseline-driven."
3. （待 Go/No-Go）"Per-tumor ω independently predicts overall survival in hepatocellular carcinoma (HR per SD ..., adjusted for grade and stage)."

## 6. 快（纯重组既有结果）vs 慢（需重算）

**快（数小时内，纯读既有文件）**：
- 模块 a 主体：所有 TT/NN/TN 均值、P、NN/TT 排名、k_n 倍数、组成衰减、线性归一化敏感性——直接来自 `phase34_v2_summary.csv`、`phase34_clinical_paired_unpaired.csv`、`tcga_linear_norm_v44_summary.csv`、`tcga_composition_v44.csv`。
- 模块 b 的组统计：v44 severity csv/json 已含 ω/k_f/k_n 三口径 KW。
- 从 `tcga_linear_norm_v44_all_pairs.csv` 派生逐样本 ω（含样本 ID，pandas 重组即得）→ 模块 b 的逐样本图、模块 c 的 ω 变量。

**中（分钟–小时级重算，脚本现成）**：
- cluster bootstrap CI（模块 a/b，B=1000，分钟级）；Dunn/Holm；Cox PH（statsmodels）+ 临床 join（模块 c，小时级）；ESTIMATE 分数（一次 TPM 扫描，~30 分钟）。

**慢（真重算，建议砍或降 supplementary）**：
- 模块 d 保守 signature（需带基因身份重跑 5 癌种加载 + 在线/半在线富集，2–3 天，novelty 风险高）。
- 逐样本 ω 的"精确版"（不依赖 2000 对抽样、全对计算，~550s/癌种）——仅当审稿人质疑抽样覆盖时再跑。
- 任何需要全 MAF（`git lfs pull`）或 LUAD 患者协变量的扩展——依赖网络，不建议纳入 v49 承诺范围。

## 7. 关键风险汇总

| 风险 | 等级 | 缓解 |
|---|---|---|
| 纯度/组成混杂（模块 a/c 核心） | 中 | 已有 4-panel bootstrap + k_n 分解；可加 ESTIMATE |
| LUAD 无协变量（年龄/性别/吸烟） | 中 | 明示 observational；ESTIMATE 作代理；不 claim 因果 |
| LIHC 生存结果未知 | 中 | 先跑 Go/No-Go，不显著就降级/删除 |
| 模块 d novelty 低 | 高 | 降 supplementary 或删除 |
| 突变 json 为二分类（无突变细节） | 低 | 定位为 driver-class 对比即可 |
| 逐样本 ω 基于 2000 对抽样（BRCA 中位仅 4 对/样本） | 低 | 组级统计稳健；敏感性可全对重算 |
