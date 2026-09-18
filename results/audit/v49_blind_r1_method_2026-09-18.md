# v49 盲审报告 R1 — 计算方法学（单细胞算法与指标评估）

日期：2026-09-18　评审人：r1-method（独立盲审）
材料：CKI_Manuscript_NC_fulltext.txt、CKI_Supplementary_NC_fulltext.txt、figure4/figure5（PNG 同源版）、nc49_pilot_kang / nc49_brain_ladder / nc49_tcga_main 三份审计、results/nc49_brain_drift_ladder.csv（4,906 对，独立重算核对）

## 总体判定

**评分：6 / 10　判定：Major Revision**（全部问题可在不重跑实验的前提下修复；核心分析本身扎实）

v49 新增的两块内容（真实数据漂移校准、TCGA 图谱）在**执行层面**方法学质量高：n-matched null 实现正确（我核对了 `notebooks/nc49_brain_drift_ladder.py:275-287`，每次打乱严格按 (na,nb) 重分、top-200 与 marker 集合逐次重选，null 内含基因选择步骤），TCGA 的样本级 cluster bootstrap（端点权重乘积）是正确的 dyadic 重抽样。稿件自我批判的密度在同类方法学论文中罕见。

**但展示层面存在一个会被统计审稿人一击命中的结构性问题**：新 centerpiece（图 4 漂移阶梯）的核心主张"ω 误报最低"在纳入 marker Jaccard 后**在全部三层都不成立**（我用逐对 CSV 独立重算验证，见 P1-1），而稿件把 Jaccard 从"对比指标"范畴里悄悄移出来维持这一主张。这恰好落在 GB 拒稿意见①的回应上，必须正面重做表述，否则复审风险极高。

## 独立重算验证（results/nc49_brain_drift_ladder.csv）

三层 FPR（exceed own null p95），7 指标：

| tier | n | B | ω | k_f | k_n | raw JS | cosine | Spearman | marker Jaccard |
|---|---|---|---|---|---|---|---|---|---|
| T1 | 2,161 | 100 | 0.286 | 0.376 | 0.357 | 0.452 | 0.441 | 0.406 | **0.199** |
| T2 | 1,089 | 30 | 0.909 | 0.987 | 0.886 | 0.984 | 0.978 | 0.964 | **0.747** |
| T3 | 1,656 | 30 | 0.848 | 0.942 | 0.848 | 0.968 | 0.955 | 0.952 | **0.801** |

- **marker Jaccard 在三层 FPR 全部低于 ω**；T1 上 Jaccard 在 **10/10 细胞类**全部低于 ω（逐类：Astro 0.193<0.261 … Vascular 0.126<0.176，无一例外）。
- T1–T3 分离度（T3 检出 − T1 FPR，Youden 式间隔）：Jaccard 0.602 > **ω 0.562** > raw JS 0.516 > cosine 0.514；比值口径（T3/T1 FPR）同样是 Jaccard 4.03 > ω 2.97。即按 FPR 的同类统计量，Jaccard 的"区分技术漂移与生物学"能力**优于** ω；ω 的唯一反证是 T3 校准比（1.80 vs 1.41）——一个不同的统计量。
- 逐类计数核对：稿件 line 40 "below raw JS in 10 of 10 … below cosine in 9 of 10, below Spearman in 8 of 10" **与 CSV 一致（正确）**；审计文档 nc49_brain_ladder 第 35 行"10/10 全部低于 raw JS/cosine/Spearman"是陈旧错误（审计需更正，稿件无需动）。

## P0（阻断性）

无。核心计算与 null 设计无错误；问题集中在主张表述与统计报告口径，均可文本/补充分析修复。

## P1（重要，必须修改）

### P1-1 "误报最低"主张与 marker Jaccard 的事实冲突（图 4 全节）

- **位置**：Results line 41（"lowest misreporting among all compared metrics at every tier"）；Discussion line 84（同句复述）；Figure 4c legend（line 207，"ω misreports least among divergence metrics at both tiers"）；SI 3.20（line 119，T2 处"ω again misreported least among the divergence metrics"）。
- **问题**：上述句子只有在把 marker Jaccard 排除出"divergence metrics"范畴时才成立。Jaccard 是 Table 1 五指标之一、图 4b/c 七指标之一；按 CSV 重算它在 T1（0.199 vs 0.286）、T2（0.747 vs 0.909）、T3（0.801 vs 0.848）FPR 全部低于 ω，且 T1 逐类 10/10 全胜。NC 审稿人从 SI Table 3.20b 一行就能算出同样结果。"misreports least at both tiers"（图注）在 T2 尤其硬伤（Jaccard 低 16 个百分点）。
- **修改建议**：(i) 删除一切"lowest at every tier / least at both tiers"绝对化表述，改为精确限定："lowest among the four continuous divergence metrics (raw JS, cosine, Spearman, k_f)"；(ii) 正面加入 operating-point/frontier 分析：以 T1 FPR（特异度）对 T3 检出率/校准比（灵敏度）作 2D 散点，说明 ω 处于中间工作点、Jaccard 更保守、raw JS 更宽松，并用**同一统计量**（FPR 间隔或 T3/T1 比）承认 Jaccard 按该口径不劣于 ω；(iii) 把 ω 的不可替代性重新锚定在 k_n/k_f 可分解性（Jaccard 无此结构）与 Table 1/交叉器官分析已建立的互补定位上，而非"校准最优"。这同时回应 GB 意见①——别再给审稿人留一个一行就能戳破的最高级。

### P1-2 Abstract/模拟 FPR 0.00 与真实数据 28.6–48% 的口径落差

- **位置**：Abstract（line 8）"ω rejected neutral housekeeping drift (false-positive rate 0.00 versus 0.55–0.58 …)"；对照 Results line 41 与 SI 3.20：真实 T1 FPR 28.6%，>500 核组 48.0%。
- **问题**：Abstract 只引模拟的 0.00，只字不提真实数据校准（v49 两条主线之一）。Kang 0/30 的 Wilson CI 上界 0.114 与 brain T1 28.6% 统计上不相容——稿件用"FPR 随 n 增长"解释了梯度，但未明说两个实验在该模型下定量自洽。更深一层：特异度随功效增长而消失，本质就是"低功效"（与模拟节 δ=1 检出 0–13% 是同一枚硬币），稿件把两件事分置两节、回避了这个综合表述。
- **修改建议**：(i) Abstract 增加一句真实数据口径（"on 2,191 real technical-replicate pairs, ω misreported least among continuous divergence metrics, though its absolute false-positive rate grows with group size"——措辞自定但不得只留 0.00）；(ii) Results line 41 或 Discussion 补一句综合：ω 的 T1 优势与其有界检出力是同一保守性操作点的两面；(iii) 明确写出 Kang 小组规模（≥50 细胞）处于 FPR-n 梯度低端，故两点估计不自相矛盾。

### P1-3 TCGA pair 级 Mann-Whitney P 值为 dyadic 伪重复

- **位置**：Results line 50（"Mann-Whitney P = 1.2 × 10⁻²³⁸ to 2.6 × 10⁻⁷⁵; LIHC P = 9.9 × 10⁻³"）；Methods line 123；SI 3.21（line 124）。
- **问题**：35,306 对共享样本端点（每肿瘤中位仅 4–11 对），pair 间强相关；MWU 把对当独立观测，P 值无意义地小。最刺眼的内部矛盾：LIHC 的 MWU P=0.0099（单侧）与稿件自己的 cluster bootstrap CI [0.97, 1.34] 含 1 直接打架——这正是伪重复低估不确定性的教科书表现。稿件已把 cluster bootstrap 当主口径（好），但仍并排印刷 MWU P。
- **修改建议**：(i) 删除或明确降级 pair 级 MWU P 为"描述性、未校正 dyadic 依赖"；(ii) 用样本级检验替代（如每样本取均值后做 per-cancer 的样本级 Wilcoxon/t 检验，或以 cluster bootstrap CI 为唯一推断依据）；(iii) LUAD 突变分析同理：KW/Dunn 把 per-tumor 均值当独立样本，但肿瘤间共享 pair（311+61+120 个肿瘤来自同一 2,000 对池），建议加一句依赖性说明或用 pair-sharing-aware 的重抽样（现 within-group bootstrap 未含此结构，作 P2 亦可接受）。

## P2（次要）

1. **FPR 的 Wilson CI 忽略聚类**（line 39–40、SI 3.20）：2,161 对共享 library（每 library 出现在多对）且嵌套于 4 供体/10 细胞类；Kang 30 对嵌套于 8 供体。有效样本量远小于对数，CI [26.8, 30.6]、[0, 0.114] 偏窄。建议按 library（或供体）cluster bootstrap FPR 的 CI。
2. **B 在层间不对称（T1=100，T2/T3=30）**：B=30 时 p95 相当于第 2 大值，单层 MC 分辨率 ≈3.2 个百分点；跨层 FPR 比较带有不同的 MC 误差结构。建议 SI 补一句 MC 误差量化（或对 T2/T3 提到 B=100 抽查子集验证）。
3. **层间细胞类构成不同**：T1 全取、T2/T3 按 200/类封顶，三层的类混合不同，"阶梯梯度 1.04→1.76→1.80"的跨层比较混入了构成效应。建议补一个类匹配（common-class）敏感性，或在文中声明。
4. **Kang 主文遗漏 k_f=0/30 并列**（line 39）：SI 3.20 披露了 k_f 同样 0/30，主文只写"ω 0/30 whereas raw JS 36.7%, cosine 23.3%"。在该数据集 ω 相对 k_f 无增量；图 4d 其实画出了 k_f=0。主文一句话补上，避免审稿人"发现"后定性为选择性报告。
5. **per-tumor ω 的解释口径**（line 51）：per-tumor 统计 = 该肿瘤与**所有其他肿瘤**（含跨组对）的均值，不是瘤内异质性也不是组内凝聚度。KRAS 升高部分反映"与 WT/EGFR 的差异"，建议一句话澄清。
6. **EGFR/KRAS 样本数对账不闭合**（line 105/123）：62 EGFR 匹配 → 61（−1 双突变）；122 KRAS → 120（−1 双突变、−1 无 pair 覆盖？）。括号补全即可。
7. **TCGA 的 k_f 循环选择未做固定 panel 敏感性**：固定 panel 消融只做了 brain；bulk 对的 top-200 |Δ| 循环选择对 NN/TT 比的方向影响未检验（线性归一化敏感性不覆盖这一条）。建议 SI 补一个小规模固定 panel 重算或文字限定。
8. **图 5a 双轴不同量程**（ω 轴 1–3、k_n 轴 1–4）视觉上放大 k_n 效应；建议同量程或分面。
9. **图 4c 的 5% 虚线**：在 null 本身误设（library 效应破坏细胞可交换性）时 5% 并非期望值；图注已写 "nominal"，建议正文再点一句"偏差的大小即 library 效应的可检性"，防止误读为校准失败。
10. **小样本对的 p95 稳定性**：B=100 的 per-pair p95 为第 95 次序统计量，20–30 核组 pseudobulk null 粗粒化、易并列；经验上最小组 FPR 最低（14.1%）说明未膨胀，但建议 SI 补一个 pooled-null（类×规模分层）敏感性作对照。

## 评审清单逐条回答

**1. n-matched null 与阶梯设计**：合并-打乱-按 (na,nb) 精确重分是两组比较的标准正确 null（首轮 min(na,nb)×2 的 n 伪影已被发现并修正，审计记录透明）；我核对代码确认每次打乱重选 top-200/marker 基因，null 内含选择步骤——这是本文最扎实的部分。概念注意点：cell-shuffle null 只校准细胞级抽样噪声，library 级系统效应（capture/深度）天然落在"信号"侧——因此 FPR>5% 不是校准失败而是 library 效应的可检性，稿件 line 41 的解读方向正确。四层对照逻辑成立（T2 明确定位为非 null 的次级阶梯）；残留漏洞为 P2-1/2/3（聚类 CI、B 不对称、类构成）。

**2. 28.6% vs 0% 的收口**：relative-calibration 方向正确但执行留有硬伤（P1-1、P1-2）。被回避的更诚实表述：(a) "特异度随功效消失 = 低功效"，与模拟节低检出力是同一性质；(b) Jaccard 在 FPR 口径三层全胜 ω（我的重算）；(c) Kang 与 brain 两点估计需在 FPR-n 模型下显式对账。现有表述（"relative-calibration advantage, not immunity"）本身好，但被同段落的"every tier"最高级自相破坏。

**3. 口径自洽**：模拟 FPR 0.00（Abstract line 8）与真实 28.6% 的桥接只在 Results 内完成，Abstract 缺失（P1-2）；Table 1 AUC 垫底的"by design"辩护（line 33）与图 4 存在未言明的张力——Jaccard 同时赢下分类 AUC 与 T1/T2 特异性，ω 的剩余独卖点是可分解性，决策规则（line 84）已部分收口但需删"every tier"；Discussion 的 specificity-first 框架与新结果基本自洽。

**4. TCGA bulk**：NN/TT 的 cluster bootstrap（端点权重乘积、肿瘤/正常独立重抽）是正确的 dyadic 重抽样，可信；逐样本 ω 派生作为探索性统计可接受，但 pair 级 MWU P 是伪重复（P1-3），KW/Dunn 的 pair-sharing 依赖未说明（P2-5 相关）；bulk 局限处理到位（组成 bootstrap 三件套的"bound not settle"措辞诚实、线性归一化敏感性、adjacent-normal 限定、LIHC 生存 NO-GO 如实上报为负面结果——这反而加分）。未覆盖项：固定 panel 敏感性（P2-7）。

**5. 泛审稿人最可能攻击的三点**：
(i) **Jaccard 三层全胜 + "every tier" 最高级**（P1-1）——现有防御（T3 校准比 1.41 vs 1.80）顶不住，因为它是不同统计量；必须换 frontier 表述。
(ii) **Abstract 的 FPR 0.00 vs 正文 28.6%/48%**（P1-2）——现有防御（正文限定"in ground-truth simulation"）在 GB 意见①的复审语境下顶不住，审稿人会读作 cherry-picking。
(iii) **dyadic MWU P**（P1-3）——现有防御（bootstrap CI 为主）基本顶得住，但 P 值必须降级，否则统计审稿人要求删除。
第四近威胁：bulk 组成混杂（4-marker panel 弱）——现有"lower bound / bounds not settles"防御诚实，可接受。

**6. 评分与判定**：6/10，Major Revision。执行质量 8 分、展示/主张纪律 4 分。三条 P1 全部是可快速修复的表述与报告口径问题，不需要新实验；修完后本文的诚实度反而成为卖点。

## 优点（应保留）

- null 设计纪律：n-matched 精确重分、基因逐次重选、block-shuffle 保留 library 结构、pseudo-region 阴性对照、donor-stratified 敏感性——这是本文方法论的真正贡献，建议在修改中把它从"诚实的局限"升格为"设计模板"卖点。
- 负面结果如实上报（LIHC Cox NO-GO、FDR 无幸存候选、组成校正的 per-cancer 异质性）。
- 双背景模拟复制（marrow + skin）与固定 panel 消融（brain）为方法学严谨性树立了好先例。
