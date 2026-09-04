# Genome Biology 盲审报告（统计学视角）

- **稿件**: CKI: a Ka/Ks-inspired index for quantifying functional cell-type divergence in single-cell transcriptomics（投稿包 v44）
- **评审人角色**: 生物统计学审稿人（独立评审，仅依据投稿包文件内容）
- **评审日期**: 2026-09-05
- **评审材料**: CKI_Manuscript_fulltext.txt（正文+方法）、CKI_Supplementary_fulltext.txt（Note 1–5、Table S1–S4）、Table1-2_fulltext.txt；抽查 figure6.pdf（图内数值与正文一致：13.6/13.6→82.7，6.10-fold，39/1,171/5,381 tier 计数）

---

## 总分与判定

| 项目 | 结果 |
|---|---|
| **总分** | **7.5 / 10** |
| **判定** | **Minor Revision** |
| P0 / P1 / P2 | 0 / 4 / 3 |

**总体评价**: 这是一篇在统计自我审计方面远超同类方法学论文平均水平的稿件。设计匹配的 block-shuffle 置换零假设、pseudo-region 阴性对照、置换分辨率对 FDR 可达性的显式论证、以及对自身几乎所有排序声明的 k_f-only/k_n 分解对照，构成了罕见完整的内部效度链条。主要保留意见集中在四点：比值估计量 ω 本身的偏差-方差行为从未被形式化刻画；关键置信区间依赖仅 6–7 个 cluster 的百分位 cluster bootstrap；候选筛查相对零假设为"反富集"（P=1.0）却仍占据大量篇幅并使用条件性 post-hoc P 值；以及 ω 置换检验在大 pseudobulk 下功效趋于零这一检验不一致性未进入摘要/结论层面。所有问题均可通过补充分析、报告规范调整与篇幅压缩解决，无需推翻研究设计，故判 Minor Revision。

---

## 主要问题

### P1-1 比值估计量 ω = k_f/k_n 的偏差与方差行为从未形式化刻画

ω 是两个 JS 散度（均经 +1 伪计数平滑）的比值。比值型估计量在小分母下有系统性上偏与重右尾，而本文:(i) 单细胞分析 kn_floor = 0（脑数据最小 per-pair k_n = 9.2×10⁻⁵，未封顶）;(ii) 类水平摘要采用 per-pair 比值的均值（脑 ω 偏度 2.22、超额峰度 6.02）;(iii) 头条结果"6.10-fold 梯度"本身是两个重尾比值均值之比。作者注意到了"均值的比值 ≠ 比值的均值"（6.51 vs 6.10 的 gap）并将其归因说明，但未对 ω 估计量本身做任何偏差/方差分析（delta method、或分裂半模拟下的偏差量化）。split-half 基线 7.70 吸收了选择膨胀，但逐对 ω 的估计量属性（偏倚方向、尾重对类均值的杠杆作用）仍是黑箱。**要求**：补充对 ω 比值估计量的偏差-方差刻画（模拟或解析近似），并对类水平梯度提供中位数/截尾均值等稳健摘要的敏感性对照；明确讨论近零 k_n 对逐对 ω 的杠杆效应（当前仅 1/31,764 对低于 1e-4 的事实声明不足以替代分析）。

### P1-2 关键置信区间依赖 6–7 个 cluster 的百分位 cluster bootstrap

脑区 region-clustered bootstrap 是恰当的方向（pair 嵌套于 region，pair-level i.i.d. bootstrap 反保守——作者已正确弃用 i.i.d. 区间 [4.86, 7.42]）。但百分位 cluster bootstrap 在 cluster 数极少时已知严重欠覆盖：Bergmann glia 仅 7 个 region、choroid plexus 仅 6 个，而 Bergmann glia 的区间 [8.49, 19.52] 直接进入两个头条量——"最保守类贴近 split-half 基线"的论证和联合校准梯度 CI [4.12, 9.18]。作者对 Bergmann 区间有一句"sensitive to bootstrap resampling"的披露，但这不足以替代方法学修正。**要求**：对小 cluster 类采用 wild cluster bootstrap 或 studentized/bootstrap-t 区间（或明确以 Monte Carlo 覆盖率模拟证明 7-cluster 百分位区间的实际覆盖率），并对 [4.12, 9.18] 给出相应敏感性；在正文中将 Bergmann/choroid 相关区间声明降级为定性结论。

### P1-3 候选筛查相对零假设为反富集（P(null count ≥ 39) = 1.0），但解剖学编目仍占约六段 Results 并使用条件性 P 值

这是全文统计论证链条中最薄弱的一环。作者自己完成的 selection-rule empirical FDR 分析表明：在 block-shuffle 零假设下 Strong 规则的期望候选数为 148.3，**观测值 39 显著低于零假设期望**（4.2 倍方向相反）；restricted 版本同样如此（131.2 vs 31）。即该筛查规则在真实数据上的命中数比纯设计结构噪声还少。在此背景下，Results 仍以约六段篇幅编目 microglia 的 LG/Pulvinar/TF 端点汇聚、少突胶质细胞的 thalamo-temporal 轴向等，并报告"hit rate P = 0.005/0.001"——这些 P 值是在已选定的幸存者集合上条件计算的（selection-rule-matched null 下的 per-candidate hit rate），属于未经形式化校正的选择后推断（post-selection inference），即使标注 exploratory 也极易被读者误读为独立证据（Note 5.1 已承认 tier 变量与 per-pair P 值数学耦合、"quantify the pattern rather than provide independent evidence"）。**要求**：(i) 将反富集结果（null expectation 148 vs 39, P = 1.0）提升至摘要与 Figure 6 层面与"no pair survived FDR"并列陈述——当前摘要只报告了后者，而后者已被作者正确论证为置换分辨率产物，两事并列才是完整图景；(ii) 压缩候选编目篇幅或移入补充材料；(iii) 删除或以更强措辞隔离条件性 hit-rate P 值，明确其不是有效的 post-selection P 值。

### P1-4 ω 置换检验在大 pseudobulk 下功效崩溃（检验不一致性）未进入摘要/结论层面

功效曲线 n=50 时 0.67–0.93，n=500 时 ≈ 0——即该检验随着数据量增加而**失去**功效，原因是零假设分布随 pseudobulk 增大而爆炸（null 中 k_n→0 而 top-200 选择使 k_f 保持高位）。这在统计上意味着该置换检验不是一致检验（inconsistent test），且 50–200 cells/donor/condition 的"操作窗口"极窄。作者以完整功效曲线诚实披露（Note 3.19，且在 Limitations 与 usage guide 中说明），值得肯定；但作为本文核心的推断机器，这一性质只出现在补充材料和 Limitations 中段，摘要与 Conclusions 均未提及。包用户默认会对大规模 atlas  pseudobulk 使用 `bootstrap_test()` 并获得名义上可用但功效趋零的结果。**要求**：(i) 在摘要或 Conclusions 中以一句话声明该操作窗口；(ii) 在包层面为超出窗口的使用加入警告；(iii) 最好补充对该现象的简明理论说明（为何零假设方差随 n 增长快于观测信号），而不仅是经验曲线。

---

### P2-1 小鼠 pilot 分类均值在 n = 2–4 对上报告 bootstrap CI

S 类 n = 4（CI 11.4–35.7）、D 类 n = 3（CI 30.1–61.7）、X 类 n = 2。n ≤ 4 的百分位 bootstrap 区间在统计上无意义（重抽样空间极小、区间宽度由抽样伪影主导）。作者已声明"calibration-scale estimates rather than precise effect sizes"，但更规范的做法是只报告 range 或不报告区间。同类问题亦见于 cross-organ 排序中 n = 3 的 Endothelial/Erythrocyte（已标 suggestive，处理尚可）。

### P2-2 ω_cal 报告精度约定与校准不确定性的传播不一致

正文声明 ω_cal"reported to one significant figure"，但随后出现 ω_cal ≈ 8.5、1.39（两位有效数字）、1.8–3.4 fold 等；class-specific split-half 基线每个仅基于 2–3 个群体、two-stage CI 已较宽（如 Bergmann [8.71, 9.47]），而除联合 bootstrap 外的多数 ω_cal 派生声明未传播这层分母不确定性。建议统一有效数字约定，并明确哪些 ω_cal 数字经过了分母不确定性传播、哪些没有。

### P2-3 TCGA 成分校正回归的 cluster bootstrap 仅 B = 200

pooled 衰减 −0.8% [−4.1%, +2.6%] 的百分位区间基于 B = 200 次 sample-level cluster bootstrap，对 2.5%/97.5% 分位数而言重抽样次数偏低（常规 ≥ 999），区间端点的 Monte Carlo 噪声不可忽略。此外 pooled 近零估计掩盖了 per-cancer 异质性（−16% 至 +37%）——作者已披露，但建议以 per-cancer 估计为主呈现、pooled 值仅作参照。

---

## 优点（strengths）

1. **零假设构造与校准验证是方法论范本**。block-shuffle 保留了 10x library 的块结构；作者主动披露并纠正了早期 per-pair shuffle 的反保守性（36.3% 触底）；127,756 个 pseudo-pair 的阴性对照定量证明边际尾部率接近名义水平（5.79%/6.87% vs 5%）且同原点对保持 37.6% 检出率——同时证明了零假设校准与检验功效，这在单细胞方法学论文中极为罕见。

2. **多重检验与置换分辨率的处理严谨透明**。两层 BH 家族（类水平 m=10 与对水平 m=31,764）分离报告、无跨家族声明；显式论证对水平 q < 0.05 需约 635 个触底 P 值或 B ≈ 6×10⁵，从而将"无 FDR 幸存者"正确归因为分辨率而非证据；触底 P 值的 q 值以截尾上界（q = 0.010）披露。模拟部分使用精确 Clopper–Pearson 区间、replicate-block-stratified bootstrap AUC CI，并披露阈值标定的 Monte Carlo 噪声（±1.5pp）。

3. **对分母伪影的系统性自我审计树立了报告标准**。spurious-correlation-of-ratios 分解（partial Spearman +0.11~+0.54）、每条排序声明均配 k_f-only/k_n-only 对照（cross-organ ρ = 0.23 [−0.08, 0.38]；TCGA severity 三条梯度两条降级）、equal-n 下采样定量证明 6.10-fold 梯度约 70% 为类大小伪影（→1.74 [1.64, 1.84]）、并将 TCGA severity 整体降级为 denominator-dominated 的 exploratory vignette。这种"自己拆解自己头条数字"的做法显著增强了剩余结论的可信度。

---

## 其他次要意见（供作者参考，不计入判定）

- 单侧置换检验的约定总体合理（方向性假设），但类水平上 3 个类均值低于零假设期望（microglia P = 0.904 等）在上尾检验下不可见；建议正文明确一句：功能性约束（ω 显著低于零假设）需用下尾检验，且两个方向家族未做联合校正（补充材料已披露）。
- IFN-β 演示的 lane 混杂披露充分，37 个 donor 级检验的 aggregate excess 论证合理；但 ω_cal 1.8–3.4 fold 的表述建议在主文中始终与"lane-confounded"限定语绑定。
- SES 作为描述性效应量的定位恰当；建议在首次出现处即注明其不是 Cohen's d 类参数统计量（方法部分已说明，Results 首处可再加半句）。
- Figure 6 图内统计标注与正文数值一致（抽查通过）；建议在图 6B 直接标注等 n 下采样后的衰减梯度（1.74），避免读者只取走 6.10-fold。

---

## 结论

**7.5/10，Minor Revision。** 统计推断框架（设计匹配零假设、阴性对照、多重检验分辨率论证、自我分解对照）达到 Genome Biology 方法学论文的高标准；四项 P1（比值估计量性质、少 cluster bootstrap 区间、候选筛查的反富集与编目篇幅、大 n 功效崩溃的呈现层级）均可通过补充分析与报告调整解决，无需新的实验或推倒重来。修订后本文有望成为"方法学论文如何诚实处理自身统计边界"的正面案例。
