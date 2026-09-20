# CKI NAR v37 投稿包 — 模拟专家审稿报告（五位审稿人）

日期：2026-08-28（22:48）
对象：`version3/CKI_NAR_Submission_v37/`（144 项构建检查全部通过的最终包）
方式：5 个独立 Agent 并行模拟 NAR 审稿人，各自通读主稿/补充材料/复现指南/cover letter 后独立评审，评审前互不可见。

## 综合结论

| 审稿人 | 视角 | 总分 | 档位 | 报告 |
|---|---|---|---|---|
| R1 | 计算方法学/算法 | 4.0/10 | Major Revision | results/v37_review_R1.md |
| R2 | 单细胞基因组学 | 5.0/10 | Major Revision | results/v37_review_R2.md |
| R3 | 统计推断 | 4.5/10 | Major Revision | results/v37_review_R3.md |
| R4 | NAR 编辑视角 | 4.0/10 | Major Revision | results/v37_review_R4.md |
| R5 | 可复现性/软件工程（新增角色） | 4.5/10 | Major Revision | results/v37_review_R5.md |
| **综合** | | **4.4/10** | **Major Revision** | |

五位审稿人一致 Major Revision（对比 v36 四人 4.6/10）。注意口径差异：本轮新增 R5（可复现性）审稿人、且本轮审稿人普遍做了底层数据抽查（多个指控经复核属实），评审深度高于 v36 轮。v36 轮的表层文字问题（C-A 表述、C-B 校准验证、C-F 数字矛盾等）已基本清除，但修订本身暴露出更深层的结构性问题——**多篇审稿人独立指出：论文自己的新增分析（k_f/k_n 分解、内部校准）恰好证明了核心主张不成立**。

## 审稿人共识（按出现次数排序）

### 4/5 提出的 Critical

**V37-C1. ω 的核心效度主张未被证明，且论文自身数据在拆台。**
- R1 实测复核（属实）：pair 级 ρ(ω, k_n) = −0.54、ρ(ω, k_f) ≈ −0.03（reviewer_brain_pair_kf_kn.csv, n=31,764）——ω 排序由分母主导；脑 6.88 倍类间梯度主要反映 k_n 差异（k_n 分量 5.7× vs k_f 分量 1.2×），与 "functional divergence" 命题冲突
- 唯一 ground-truth 指标（分类 AUC 0.680）五方法垫底（R1/R2/R3/R4）
- 全员要求：**注入已知分化的模拟数据验证**（ground-truth simulation），否则把核心主张降格为描述性
- R2/R3 指出作者已在 Limitation 14 自认无 ground-truth 验证，但摘要仍按效度主张写

**V37-C2. cover letter 与主稿主张不一致（R1/R4/R5，已复核属实）。**
Cover letter 第 18 行仍宣称 "Independent information dimension…measures something fundamentally different from raw JS divergence"——该主张在主稿 v37 修订中已撤回/降格，但 cover letter 未同步。

### 3/5 提出的 Critical

**V37-C3. kn_floor 三处文档互相矛盾（R1/R4/R5，已复核属实）。**
- 主稿 Methods：单细胞全部 kn_floor = 0（仅 positivity guard），TCGA 例外用 1e-4
- 补充材料伪代码（SN 第 39 行）：无条件 `if k_n < 1e-4: k_n <- 1e-4`
- 复现指南参数表（第 346 行）："k_n floor (minimum) | 1e-4 | all analyses"
- 复现 blocker：按补充材料/指南跑不出主稿数字

**V37-C4. 上尾选择性报告（R3，已复核属实）。**
block-shuffle 结果中上尾 P<0.05 达 **6,153/31,764 对（19.4%）**（p_perm_high），稿件只报告下尾 938 对 "anomalously similar"。19.4% 上尾信号未呈现也未解释——审稿人认为这改变了 brain 结果的解读（null 可能双向失配）。

### 2/5 提出

**V37-C5. 复现产物链不一致（R3/R5，部分复核属实）。**
- 稿件 brain 最小 per-pair k_n = 7.7e-5（来自 v3 文件），但新增分解文件 reviewer_brain_pair_kf_kn.csv 实测最小 7.8e-6、1,825 对 < 1e-4——两个文件对同一数据给出不同 k_n，稿件引用值与审稿人新增分析所用的文件矛盾，需查清口径并统一
- phaseB_bootstrap_cis.csv 与稿件 CI 数字口径矛盾（R3）
- GitHub tag v0.3.1 不含 08d/08e 与 5 个 reviewer 脚本及 results 文件，Data availability 声称不实（R5，`git ls-tree` 核验）
- 与论文一致的 kn_floor=0 代码仅存在于未提交工作区，"editable install" 不可获得（R5）
- Dockerfile 声称存在但不存在；scanpy 版本两处矛盾；PAM50 方法描述（nearest centroid）与实际脚本（API 拉取标签）不符（R5）

### 单独提出的重点

- R1/R2：per-pair top-200 DE 循环基因选择使 k_f 跨对不可比（null 保检验水平不保排序）
- R2：B=1,000 下 BH q<0.05 数学不可达（m=31,764 需要 B≈6×10⁵ 或分层模型）——稿件 Limitation 19 已自认，但 OPC 叙事篇幅仍超配
- R4：TCGA headline 中 3/5 癌种 ω 被 floor 饱和（等价 k_f-only 比较）；Limitations 已达 21 条、稿件超长
- R2：供体混杂（4 供体、区域中位单供体占比 0.61）在候选 screen 层面无供体复现检验（主分析已做 within-donor）
- R3："7.67 ∈ [4.24, 9.24] 即可迁移"不是等价检验（TOST）

## 审稿人认可的亮点

- 阴性结果呈现诚实（多位审稿人点名表扬）
- 本地结果数字抽查全部吻合（R2/R5）
- 复现指南 §5.6 reviewer 分析文档化良好（R5）
- 开源/复现工程高于领域平均（R4）

## 与 v36 轮的对照

| v36 问题 | v37 状态 |
|---|---|
| C-A 负相关=独立维度（文字层面过度主张） | 文字已降格，但 cover letter 残留（→V37-C2）；且审稿人用我们自己的分解数据证明分母主导（→V37-C1，升级为实证问题） |
| C-B 校准因子跨数据集未验证 | 内部校准已做（TS 7.67 可迁移、brain 12.29 不可），但结论是校准体系自我拆台——mouse 因子对 brain 无效 |
| C-C per-pair k_n 估计量 | 敏感性已做，但暴露 ρ=0.181 的排序不稳定本质 |
| C-F Strong 候选数字矛盾 | 已修复（本轮无重复提出） |
| C-E kn floor 包/脚本不一致 | 文档层面反而恶化：三处文档互相矛盾（→V37-C3） |

## 修订路线（按投入-产出排序）

1. **零成本文字修订**：cover letter 撤 "fundamentally different"（C2）；统一 kn_floor 三处文档（C3）；补充材料/指南与主稿对齐
2. **低成本核验修订**：查清 7.7e-5 vs 7.8e-6 的 k_n 口径矛盾（C5）；上尾 6,153 对如实报告或说明单尾理由（C4）；PAM50/Dockerfile/版本号等失实描述更正（C5）
3. **中成本分析**：ground-truth 模拟注入实验（C1，多数审稿人的核心要求）；固定基因面板复验梯度（循环选择消融）
4. **工程投入**：GitHub 提交/重打 tag 使 Data availability 声明为真（C5，外部操作需确认）

## 各审稿人原始报告索引

- results/v37_review_R1.md（计算方法学，4.0）
- results/v37_review_R2.md（单细胞基因组学，5.0）
- results/v37_review_R3.md（统计推断，4.5）
- results/v37_review_R4.md（编辑视角，4.0）
- results/v37_review_R5.md（可复现性/软件工程，4.5）
