# CKI nc73 专家团盲审汇总（5 人，2026-10-13）

评审报告原文：`results/audit/_nc75_review_{scmethod,stat,cancer,brain,editor}.md`

## 一、评分与中稿率共识

| 审稿人 | 评分 | NC 中稿率 |
|---|---|---|
| 单细胞方法学 | 6.0/10 | 20–30% |
| 信息论/统计 | 7/10 | 25–35% |
| 癌症基因组 | 6.5/10 | 25–35% |
| 脑图谱 | 7/10 | 40–50% |
| 编辑（送审 45–60% × 条件录用 25–40%） | — | 折算 ~15–25% |
| **共识中位** | **6.75/10** | **~25–35%（送审后）；含 desk 风险综合 ~20%** |

nc69 轮共识为 15–25%（中位 ~20%），nc73 理论修订后统计审稿人确认数学无硬伤（Lemma 2 常数 1/(8ln2)、5/(48ln2) 手工复核精确），共识小幅上移。

## 二、Major concerns 去重合并（按共识强度排序）

**P0（≥3 人独立命中，须优先处理）**
1. **A1 "excluded by construction" 与 Note 8 自相矛盾**（stat-M1；scmethod-M4、cancer-M1 同源）：HK 锚在 IFN-β（ACTB/GAPDH 降 40%）与 TCGA（k_n 升 1.3–3.3 倍）中实证失效，恰在最有趣的场景失效。→ "by construction" 改 "by assumption"，交叉引用 Note 8 anchor-visibility boundary，给出失效 regime 检测信号。
2. **TCGA 章定位**：pan-cancer 反转是 HK 失稳副产品，验证证据力近零（scmethod-M4、cancer-M1）；临床增量价值缺失（唯一生存分析阴性，未 vs PAM50/增殖指数/TP53）。→ 降级机制表述、撤"selection"语汇、补 KRAS 增量验证（leave-pair-out null、TP53 共突变校正、vs LUAD 亚型）。
3. **ω 相对 k_f 的真实数据增量未确立**（scmethod-M3、brain-M1）：ordering 应默认 k_f + design-matched null，CKI「新指数」必要性主张受挑战；神经元 MGE 梯度未做 k_f/k_n 分解（SES=7.2 是分子还是分母驱动？）。→ 补神经元超类 k_f/k_n 分解；正面回答定位问题。

**P1（2 人命中）**
4. **基准比较不足**：DA 方法（Milo/scCODA/DA-seq）缺席、scDist 用 Python 近似、Augur n=10 不显著；组合性未与 CLR 类对照（scmethod-M1/M5；编辑亦点出伪 bulk 辩护需前置）。
5. **供体稳健性**（brain-M2/M4）：MGE P=0.001 缺 donor-stratified 与 leave-one-donor-out；四供体外部效度。
6. **理论残留**（stat-M2/M3）：Prop 4(b) 在 k_f 尺度 90 分位展开误差 103% 下退化为定性陈述；理论 α（14/8.5）与操作校准（9.73/7.70）1.4 倍断裂未闭合。
7. **SEA-AD "positive control" 过强**（brain-M3）：q_min=0.145 弱方向性，降格或改 ADNC 分期剂量-反应。

**P2**：39 Strong 候选章节实为阴性结果、占比过大（scmethod-M6）；Fig 5 密度过高（编辑）；Fig 1a "positive selection" 标签淡化（brain-M5）；"evolutionary cell biology" 措辞删除（brain-m7）。

## 三、期刊梯队（编辑 agent，主 lead 核定）

- **主投：Nature Communications（维持）**——定位最贴合；desk reject 风险主防线 = 封面信第一段钉死 Ka/Ks 类比 + 第二段主推泛癌逆转 headline。
- **冲刺档**：Nature Methods（送审 ~20–30%，不建议现投）、Science Advances（~10–15%，可行并行替代）。
- **备选档（NC desk reject 后）**：首推 **Cell Systems**（气质最契合，录用 ~20–30%）、次选 **Cell Reports Methods**（最稳，~35–45%，中位 210 天）；不建议回投 Genome Biology（有拒稿史）。
- **保底档**：NAR Genomics and Bioinformatics（$2,633、最快 156 天）、Bioinformatics、Genome Research、PLOS CB。

## 四、建议行动序（待用户定夺）

1. P0-1（A1 措辞 + Note 8 交叉引用）——SI 内小改，成本低收益高。
2. P0-3（神经元超类 k_f/k_n 分解 + donor-stratified/LODO）——需跑 notebooks/83 扩展，中等成本。
3. P0-2（TCGA 表述收敛 + KRAS 增量验证）——中等成本。
4. stat P1-6（Prop 4(b) 定量界或降格、α 断裂数值示例）——SI 小改。
5. 封面信策略更新（编辑建议三条）。
