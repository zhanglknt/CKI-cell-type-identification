# CKI v49.9 专家团盲审汇总报告（2026-09-20）

对象：CKI_Submission_v49_NC.zip（v49.9，12,258,746B，sha256 43256f99…eed3e，commit fa775c3）
审稿文本：results/audit/_v499_review/{MS,SI,CL,GUIDE}.txt + TABLE1.tsv（一段一行，从 zip 提取）
个人报告：results/audit/v499_review_R{1..6}_2026-09-20.md
核验方式：主代理对全部 Major 指控做三轮文本核验（grep 级，上下文 ±110 字符），裁定 确认/误读/伪影。

---

## 一、评分与推荐

| 审稿人 | 领域 | 分数 | 推荐 |
|---|---|---|---|
| R1 | 单细胞方法学 | 3/10 | Reject |
| R2 | 进化基因组（Ka/Ks 类比） | 4/10 | Major Revision |
| R3 | 生物统计 | 5/10 | Major Revision |
| R4 | 肿瘤基因组（TCGA） | 4/10 | Major Revision |
| R5 | 脑图谱应用 | 4/10 | Major Revision |
| R6 | NC 编辑视角+可复现性 | 6.5/10 | Minor Revision |
| **汇总** | | **均值 4.42 / 中位 4** | **Major Revision（多数票）** |

口径说明：本轮任务书刻意设为 NC 最严标准+逐领域攻击线，与 v44–v46（7.08→8.45，GB 版不同评审团）不可直接比；且 R3/R5 的部分"数字不符"源自任务书旧口径（见 C 类核销）。R3 原话承认文稿自我审计 "exemplary"。

## 二、A 类：必改（编辑级，文本已确认）

| # | 问题 | 出处 | 核验 |
|---|---|---|---|
| A1 | MS 数据可用性句 "Supplementary Tables 1–4"，SI 实有 19 表 | MS 末段 | 确认（v49.4 遗留，上轮已标记） |
| A2 | SI 两处主图指针错：drift-ladder 复制指 "Fig. 4d"（实为 Fig. 3 系）；per-tier 七指标值指 "Fig. 4b,c"（应为 Fig. 3b,c——Fig. 4b,c 是 LUAD 突变分层） | SI Note 3/4 区 | 确认（图注逐字比对） |
| A3 | SI Note 9 "the cross-organ conservation ranking of cell types (Table 2 / Fig. 5)"——Table 2 不存在（仅 Table 1，在 xlsx） | SI Note 9 | 确认 |
| A4 | Reproducibility Guide 双估计量排序（ρ=0.142）指 "Supplementary Fig. 8"，SI 上下文表明估计量选择图为 Supp. Fig. 7（Supp. Fig. 8 是候选散点） | GUIDE | 确认 |
| A5 | 脑候选枚举句 16 microglia+10 oligo+6 fibro+3 astro+2 ependymal=37≠39，OPC 2 个未列（"the rest" 不成立；lineage 12 句隐含） | MS 脑筛查段 | 确认（算术） |
| A6 | MS k_n 倍数用 mean（KIRC 3.29 [2.54,4.35]、LIHC 1.35 [1.02,1.88]），SI 同量用 median（3.70、2.18）——并排引用易被当矛盾，需显式 mean/median 标注 | MS/SI TCGA 段 | 确认（R4 因此误读） |

## 三、B 类：概念/框架之争（需回应或重构，非文字修复）

| # | 问题 | 提出 | 核验状态 |
|---|---|---|---|
| B1 | v49.9 Scope 句"not to discriminate cell-type identity" vs SI 权重方案选择标准 "optimal cell type discrimination (AUC=0.786, n=703 mouse pairs)" 表面矛盾——需加和解句（那是 identity-gene 配置的选择准则，非 CKI 用途） | R1 | 文本确认存在张力 |
| B2 | Ka/Ks 类比结构性颠倒：Ks 是中性标准，k_n 是最受稳定选择约束的基因集——机制相反；McDonald–Kreitman 框架未引用；ω>1 的生物学方向定义全文不统一（低 ω 既称 "most conserved" 又可源于分母膨胀） | R2 | 概念成立，需定位决策 |
| B3 | Table 1 跨细胞类型 mean ω 排名 vs "k_n 仅同类可比"让步自相矛盾风险；MS 已披露 ρ(ω,k_n)=−0.73（分母驱动）+ k_f-only 排序对照，但排名表本身未加同等警示 | R2/R1 | 文本确认（MS 已部分对冲） |
| B4 | 脑头条 6.10 倍（未校正上限）vs 等 n 估计 1.74 [1.64,1.84]：Abstract 已双报，R5 主张 1.74 应为头条——编辑判断题 | R5 | 已缓解（双报），框架待定 |
| B5 | 脑图谱仅 4 供体、供体-脑区纠缠（区域内主导供体中位 0.61）；筛查层面无供体分层 null；缺供体×脑区覆盖表 | R5 | 供体数文本确认 |
| B6 | B=1,000 × m=31,764 → FDR 发现力数学上限（MS 自报 min q=0.520、零通过）；筛查应定位为"候选优先级"而非"发现"；期望 null 148.3 vs 观测 39 的反富集已有披露 | R3/R5 | 部分披露，建议改框架措辞 |
| B7 | TCGA 为 bulk 组织 vs CKI 域"同细胞类型跨状态"的范畴错位：追踪细胞区室从未命名；32 CC 样本 LUSC→LIHC 修正未在 MS/SI 披露；LIHC 零结果（1.10 [0.93,1.29]）恰坐最弱 k_n 抬升+最大组成衰减 | R4 | 范畴问题成立；CC 修正披露缺失确认 |
| B8 | TCGA "4/5 CI 不含 1" 的 dyadic cluster bootstrap 区间类型未写明；固定面板下设计匹配置换反保守（P>0.9 指控未独立复核） | R3 | 待复核（本轮未全验） |

## 四、C 类：核销（审稿人误读 / 任务书伪影）

| # | 指控 | 裁定 |
|---|---|---|
| C1 | "30 Strong/16 FDR 与文本不符"（R3/R5） | 任务书用了旧版本数字；v49.9 文本一致为 39 Strong/0 FDR（期望 null 148.3、min q=0.520），非文稿错误 |
| C2 | "1.3-fold ratio bias"（R3） | 任务书混淆：实际 ratio 偏差中位 +0.2%（最差 bin +6.5%）；1.3-fold 指脑内基线 vs 小鼠校准 |
| C3 | R1 "scDist never run / 基准被操纵" | 误读：scDist Python 近似+MELD(v1.0.2) 已跑；SI 披露 ω 在 G=100 不敏感（AUC 0.52→0.79）、G=500 被自身分母湮灭（k_n AUC=1.000），并以 N0/N1 非 HK 锚定 null 正面回应"构造伪影" |
| C4 | R6 "seed 20260905 未申报" | 误读：Guide 已申报 seed 42 + 三例外（20260903、777000），硬编码于脚本 |
| C5 | R4 "LIHC k_n 1.35 vs 2.18、KIRC 3.29 vs 3.70 矛盾" | mean（MS，含 CI）vs median（SI），非矛盾；触发 A6 标注改进 |
| C6 | R1 "global HK set 与 cell-type-specific 锚点矛盾（基线 9.26 vs 9.08）" | 过强：两基线接近恰说明这两类可比；Scope 句措辞是 "may differ"，无直接冲突，但经验支撑可引用更准 |

## 五、综合判定与建议路径

判定：**Major Revision**（1 Reject + 4 Major + 1 Minor）。

但结构清晰：A 类 6 项全为编辑级、零新实验、一轮构建可清；B 类中 B1/B3/B6 可用 1–3 句框架措辞对冲（文稿已有自我披露传统，顺势补强即可）；真正需要决策的只有 B2（Ka/Ks 类比是否加限定/引 MK 框架）、B4（6.10 vs 1.74 头条取舍）、B7（TCGA bulk 范畴句+CC 修正披露句）。

建议：先做 A 类全修（v49.10），再把 B1/B3/B6/B7 各加一句对冲，B2/B4 留待用户定夺。
