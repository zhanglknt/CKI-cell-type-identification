# CKI NAR v36 投稿包 — 模拟专家审稿报告

日期：2026-08-28
对象：`version3/CKI_NAR_Submission_v36/`（110 项构建检查全部通过的最终包）

## 综合结论

| 审稿人 | 视角 | 总分 | 档位 |
|---|---|---|---|
| R1 | 计算方法学/算法 | 5.0/10 | Major Revision |
| R2 | 单细胞基因组学 | 4.5/10 | Major Revision |
| R3 | 统计推断 | 4.0/10 | Major Revision |
| R4 | NAR 编辑视角 | 5.0/10 | Major Revision |
| **综合** | | **4.6/10** | **Major Revision** |

四位审稿人一致给 Major Revision。R4 额外提示：若编辑部对 scope 从严，不排除建议转投 Genome Biology / Bioinformatics / NAR Genomics and Bioinformatics。

## 审稿人共识（跨审稿人重复出现的问题，按出现次数排序）

### 全员 4/4 提出的 Critical

**C-A. "负相关 = 独立信息维度"疑似比值度量的数学伪影。**
ω = k_f/k_n，而 k_n 本身与标准距离度量正相关（k_n 从 control 到 D/X 类增长 72–118 倍）。任何 A/B 形式的度量在分母与外部度量 M 正相关时，corr(A/B, M) 系统性偏低甚至变负——Pearson (1897) 经典 spurious correlation。正文却将 r=-0.36~-0.46 的负相关称为 "the strongest evidence that CKI measures something fundamentally different"（行 56）并写入摘要。
要求：分解 corr(k_f, M) 与 corr(k_n, M)；给出控制 k_n 后的偏 Spearman 相关；否则摘要与正文该主张撤回或降格。

**C-B. 校准因子 6.67 跨数据集/跨平台迁移未经验证，而验证数据是现成的。**
6.67 来自小鼠 SmartSeq2 单数据集 n=6 次 split-half（CV≈52%，CI [4.24, 9.24] 相对宽度 ~75%），却被直接用于 10x snRNA-seq 人脑与 TCGA bulk，且 ω_cal 报告到两位小数（4.88、11.52、1.67）。Bergmann glia ω_cal=1.67 在校准不确定性下是否 >1 都不确定（因子取 9.24 则降为 1.21）。
要求：在 brain 与 Tabula Sapiens 数据内部各自做 scheme-matched split-half 校准；ω_cal 改为区间或 1 位有效数字。

### 3/4 提出的 Critical

**C-C. per-pair k_n 估计量使 ω 排序近乎任意（R1/R2/R3）。**
SN 3.7：per-pair k_n vs global k_n 的 ω 排序 Spearman ρ 仅 0.181（~3% 方差保留），k_n 跨对 CV=92.89%——ω 排序主要由分母噪声驱动。Bergmann glia 11.17 → Astrocyte 76.83 的 6.88 倍梯度究竟是 k_f 信号还是 k_n 差异伪影未验证。
要求：类均值梯度在两种 k_n 估计量下的一致性检验 + k_f-only/k_n-only 梯度分解。

**C-D. tier 阈值（res<0.3/0.5/0.75，ω<15/25/35）无统计依据（R1/R3，R2 间接）。**
全文无来源推导、无敏感性分析；ω 上限用 raw ω 表达而作者自己强调 raw ω 跨方案不可比。55 个 Strong 候选对阈值稳健性未知。

**C-E. k_n floor 包/脚本不一致（R1/R3/R4）。**
论文脚本只用正性保护，包 API 默认 floor=1e-4，而脑数据最小 k_n=7.7e-5 低于 floor——按发布的包默认参数复现脑分析会得到被截断的 k_n，与"numerically identical results"承诺矛盾。应统一实现重跑，而非留作 caveat（Limitation 20）。

### 2/4 提出的 Critical/Major

**C-F. Strong 候选组成数字矛盾（R1/R3/R4）。**
正文行 80：OPC 27 / committed OPC 12 (13) / oligodendrocytes 11——"12 (13)"逻辑不可能；S7 图例（行 127）：27/13/12 合计 57 ≠ 55。55 个候选的构成在文中至少三个版本。

**C-G. FDR 阴性结果与 OPC 叙事篇幅不匹配（R2/R3/R4）。**
minimum q=0.949、938 raw P<0.05 少于 null 期望 ~1,588（无信号超额），却用两节篇幅做逐区域机制解读。出路：(a) 谱系级 m=10 的置换富集检验（OPC 谱系 50/55 vs 17.9% 份额）；(b) 压缩至一段诚实阴性报告。

**C-H. k_f 的 DE 基因循环选择（R2/R4）。**
身份基因 = 两组 |μ_A−μ_B| top-200，即"功能分化"由被比较两组的差异本身定义。null 保留同一选择程序只保证检验水平有效，不保证 ω 是有意义度量。要求非循环基因定义（marker panel/第三参考集）的消融验证。

**C-I. human/mouse bootstrap 零模型未修 block 结构（R3）。**
brain 修好的 block-shuffle（旧实现 36.3% anti-conservative 已披露），但 Tabula Sapiens（同为 10x、有 donor/library 结构）的 bootstrap 仍是细胞层面洗牌——同一类错误。

**C-J. 区域与供体完全混杂（R2）。**
Siletti 每个脑区来自特定供体，31,764 个跨区比较同时是跨供体比较。要求供体内跨区分析验证 astrocyte ω=76.83 排序。

### 单独提出的重点

- **R4-C1 期刊契合度**：无任何核酸层面分析对象，Ka/Ks 仅是自认 "mathematically non-equivalent" 的启发式类比。scope 是编辑层面的第一道关。
- **R4-C6 篇幅**：Limitations 编号到第二十一条，统计方法描述三处重复；预计需压缩 40–50% 才达 NAR 6–9 印刷页标准。
- **R1-M1 "Kinetic" 命名**：无时间维度数据或模型，JS 散度是静态距离；建议改名（如 Cell-state Divergence Ratio）或与 RNA velocity/CytoTRACE 做概念区分。
- **R1-M4/R4-M5 环境记录可疑**：scanpy 1.10.x 不支持 Python 3.14.4；editable install 与 v0.3.1 tag 不一致；无 lockfile/CI/单元测试。
- **R4-M4 署名规范**：通讯第二作者 "performed all analyses, wrote the manuscript" 而第一作者仅 "contributed"——会触发署名审查。
- **R2-M1 小鼠 pilot n=15**（S 类 4、D 类 3、X 类 2 对）不足以支撑"ω 随生物学距离单调增加"；703 对全矩阵现成可用。
- **R2-M2 TCGA 事实错误**：TCGA normal 是癌旁组织而非健康个体，"normal individuals differ more than tumors" 表述必须更正。

## 亮点（全员认可）

1. **统计诚实罕见**：主动披露旧 null 36.3% anti-conservative 并修正；自行完成 BH 阈值 vs 置换分辨率的不可行性换算（q<0.05 需 B≈6×10⁵）；"938 vs 期望 1,588" 的 global null 诊断。
2. **可复现性工程为最大资产**：随机种子、全参数表、逐脚本输出索引、Zenodo DOI、Dockerfile、分步核查清单——超出多数已发表论文水准。
3. **block-shuffle null 设计本身是方法学贡献**：文库级 blocking 的置换方案可推广到其他图谱级筛选场景。

## 修订路线建议（若走 Major Revision）

按投入-产出排序：
1. **零成本文字修订**：删弱 "independent information dimension"（C-A）；修正数字矛盾（C-F）；统一 k_n floor（C-E）；TCGA normal 表述（R2-M2）；"Kinetic" 改名或重新定义（R1-M1）；压缩篇幅（R4-C6）。
2. **低成本计算（数据现成）**：brain/Tabula Sapiens 内部 split-half 校准（C-B）；供体内跨区分析（C-J）；tier 阈值敏感性分析（C-D）；谱系级富集检验（C-G）；两种 k_n 估计量下的梯度一致性（C-C）；human bootstrap 加 block 结构（C-I）；k_f/k_n 分解相关与偏相关（C-A）。
3. **中成本新增分析**：非循环基因定义消融（C-H）；合成 ground-truth 验证（R1-M2）；与 SAMap/SATURN 或朴素比值基线的定量对比（R1-M1/R4-M2）。

其中第 2 类是决定 6.88 倍梯度与 Strong 候选清单能否保留的关键——若这些检验失败，论文需要实质性重构主张。

---
*审稿人：4 位并行模拟 NAR 审稿人（计算方法学 / 单细胞基因组学 / 统计推断 / NAR 编辑视角），各独立阅读 Manuscript、Supplementary、Cover Letter、Reproducibility Guide 全文后评分。*
