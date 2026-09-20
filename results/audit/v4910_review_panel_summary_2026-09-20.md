# CKI v49.10 专家团盲审汇总报告（2026-09-20）

对象：CKI_Submission_v49_NC.zip（v49.10，12,259,394B，sha256 5602c15e…afebd，commit b8a7acc）
审稿文本：results/audit/_v4910_review/{MS,SI,CL,GUIDE}.txt（v49.10 当版）
个人报告：results/audit/v4910_review_R{1..6}_2026-09-20.md
前轮基线：v49.9 均分 4.42（1 Reject + 4 Major + 1 Minor）

## 一、评分与推荐

| 审稿人 | 领域 | v49.9 | v49.10 | 推荐 | Δ |
|---|---|---|---|---|---|
| R1 | 单细胞方法学 | 3 (Reject) | 5 | Major | +2 |
| R2 | 进化 Ka/Ks | 4 (Major) | 5 | Major | +1 |
| R3 | 生物统计 | 5 (Major) | 7 | Minor | +2 |
| R4 | 肿瘤 TCGA | 4 (Major) | 5 | Major | +1 |
| R5 | 脑图谱 | 4 (Major) | 5.5 | Major | +1.5 |
| R6 | 编辑+可复现 | 6.5 (Minor) | 7.5 | Minor | +1 |
| **汇总** | | **4.42** | **5.83** | **Major Revision（4/6）** | **+1.41** |

全员升分、Reject 消失、两位转 Minor。判定：**Major Revision**。

## 二、v49.10 修复获确认的部分（前轮 Major 已销项）

- A 类编辑级 7 项全员认可（R6 逐项核对通过）
- R1：scDist 披露、ω 分母主导披露 "均已妥善处理"
- R3：从 Major 转 Minor（"exemplary self-audit"）
- R5：枚举修复 "经 MS/SI/图8 三方核对为实质性修复"
- B6（脑分辨力）：R3 认可 Methods 已有披露

## 三、本轮新发现问题（跨审稿人交叉印证 + 主代理文本确认）

| # | 问题 | 提出 | 状态 |
|---|---|---|---|
| N1 | **seed 20260905 未申报**：SI Note 2 "(seed 20260905; B = 5,000 on the real data)"（studentized bootstrap-t, notebook 89），但 MS Methods 只报 "seed 42 throughout, except scripts 77/78/79, which used seed 20260903"、Guide 同 | R3+R6 双证 | **文本确认（MS 0 处/SI 1 处/Guide 0 处）；我上轮 C4 "误读"裁定错误，实为真问题** |
| N2 | **Discussion 引用被取代的 softmax 组成数字**：Discussion 引 −0.5% [−3.2,+2.6]（superseded softmax 口径），Results 权威 linear 口径 −1.2% [−4.1,+2.6] | R3+R1 | **文本确认（MS 两处并存，自相矛盾）** |
| N3 | **阈值扫描 4 阈值只给 3 梯度值**："thresholds of 10, 20 (reported), 50, and 100 nuclei retain 10, 10, 10, and 8 classes with gradients of 6.60, 6.10, and 4.12"——4 个阈值、4 个类数、3 个梯度值，缺一个 | R5 | **文本确认** |
| N4 | SI 1.6 "minimum of 10 cells per group"（pseudobulk 构造）vs Methods 脑区 "≥ 20 nuclei per group" | R1 | 上下文不同（通用 pseudobulk vs 脑区 (region,cell_type) 过滤），待小牛裁定是否需澄清 |
| N5 | Guide 环境清单缺 statsmodels/seaborn/meld 1.0.2/pyaugur 0.1.0；§2.1 参数表悬空；无有序运行命令 | R6 | 文本确认（前轮已知，本轮复现） |
| N6 | Abstract 199 词超 NC 内部 ~150 词房规 | R6 | 合规但接近上限 |

## 四、遗留概念问题（前轮未销项 + 新提出）

| # | 问题 | 提出 | 性质 |
|---|---|---|---|
| C1 | MK 引用被判 "name-drop"：MK 的多态性/分化对比在 CKI 无对应物；SI 仍称类比 "structurally similar"；标题/Fig 1a 仍宣传 "ω = Ka/Ks > 1 indicates positive selection" 与 Discussion "never evidence of positive selection" 矛盾 | R2 | 需小牛定夺（是否改标题/Fig 1a） |
| C2 | ω 实际价值未证实：k_f+匹配 null 之外 ω 的增量未被单细胞分析证明；Tabula Sapiens 跨器官用单一最大 donor 存在 donor 混杂 | R1 | 概念 |
| C3 | Table 1 跨类型 ω 排名与 scope 让步矛盾未解（ρ(ω,k_f) CI 跨零、ρ(ω,k_n) CI 排除零） | R2 | 前轮 B3 已加警示句，R2 判不足 |
| C4 | CC 修正仅披露未做敏感性分析（LIHC without CC samples）；"并非混杂伪影"结论过于绝对 vs LIHC +33.5% 衰减 | R4 | 需新分析 |
| C5 | Results/Discussion 仍以 6.10 领衔（仅 Abstract/Introduction 改 1.74）；供体混杂仅披露未分析（筛选层面 shuffle 跨供体自由） | R5 | B4 修复不完整 + B5 深度不足 |
| C6 | studentized bootstrap-t pivot/SE 未定义、覆盖率 DGP 未写明、Bergmann joint calibrated CI 可能仍是 percentile | R3 | 统计描述补全 |
| C7 | SI Pearson −0.850 (P=0.0018) 被 MS 隐去（MS 只引较弱 Spearman −0.648） | R5 | 选择性引用 |

## 五、建议

N1/N2/N3/N5 为编辑级可即修（N1 种子例外句、N2 Discussion 数字改 linear 口径、N3 补第 4 个梯度值、N5 Guide 补依赖+参数表）；C1/C4/C5 需小牛定夺或新分析；C2/C3 为框架之争。

## 教训

1. 上轮 C4 核销（seed 20260905"误读"）经双审稿人+文本确认为**裁定错误**——核销任何指控前必须做与指控同级的文本检索（我只查了 "20260905" 在 Guide，未查 SI）。
2. 任务书数字取自当版文本有效：本轮无伪 Major，R3/R5 均未再误报旧口径。
