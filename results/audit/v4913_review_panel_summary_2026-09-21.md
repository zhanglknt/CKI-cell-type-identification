# v49.13 盲审汇总（第四轮，2026-09-21）

**对象**：CKI_Submission_v49_NC.zip v49.13（commit 3a084ef + 8d407f7，远端 main=8d407f7；zip 12,266,868B sha256 43b98c06…，构建 184/184 + verify 117+109+39 全 0-fail；Release v0.5.0 资产 577119599）
**盲审材料**：results/audit/_v4913_review/ 四件套提取文本（MS sha eb27cc39 / SI 6755ae00 / CL a1678767 / GUIDE bbfdde33），任务书锚点数字全部取自当版文本
**前轮轨迹**：v49.9 4.42（1R+4M+1Minor）→ v49.10 5.83（4M+2Minor）→ v49.12 7.73（6/6 Minor）

## 一、评分与推荐

| 审稿人 | 视角 | 评分 | 推荐 | 报告 |
|---|---|---|---|---|
| R1 | 算法与方法学 | 8.2（上轮 7.2） | Minor | v4913_review_R1_2026-09-21.md |
| R2 | 概念/进化框架 | 8.5（上轮 8.0） | Minor（M1–M2 后支持接收） | v4913_review_R2_2026-09-21.md |
| R3 | 统计学 | 8.9（上轮 8.3） | Accept（M 项为可选微调） | v4913_review_R3_2026-09-21.md |
| R4 | TCGA/泛癌 | 8.5（上轮 8.0） | Minor（M1–M4 后可转 Accept） | v4913_review_R4_2026-09-21.md |
| R5 | 脑科学 | 8.3（上轮 7.5） | Minor | v4913_review_R5_2026-09-21.md |
| R6 | NC 编辑 | 8.8（上轮 7.4） | Accept（copy-edit 级残余） | v4913_review_R6_2026-09-21.md |
| **均分** | | **8.53**（上轮 7.73，**+0.80**） | **4 Minor + 2 Accept，零 Major 零 Reject** | |

单人均分轨迹：4.42 → 5.83 → 7.73 → **8.53**。六人全部零 Major；两位直接 Accept，三位注明修完 Minor 后支持接收。

## 二、数值核验统计

- R3：7/7 命中（含 2 项 bit-exact：LUAD 置换 RNG 流回放、donor 表 BH q 值全行重算；Wilson 区间三组独立复算命中，上轮"2.16 vs 0.1135"指控正式证伪）
- R4：12/12 命中（CC 审计/composition/置换/log-ω 全对）
- R5：6/6 命中（span-matched、equal-n、donor 表、Strong 统计、Augur 相关独立重算）
- R1：14 项核验表全对（Kang FPR、drift ladder、大小依赖等独立重算）
- R2：校准常数三数据集（mouse 7.696/brain 9.726/TS 7.671）全对
- R6：格式硬指标程序核验全过（Abstract 197 词、57 条文献连续、图表引用完整、可用性声明齐全）
- 误报：0。唯一偏差为 lead 任务书笔误（"30 Strong/16 FDR"），稿件与 ground truth 自洽（实际 39 Strong / min q=0.520）

## 三、问题清单（去重合并，全 Minor）

### A. 共识/交叉重复项（多审稿人独立指出，优先修）
| # | 问题 | 来源 | 修法 |
|---|---|---|---|
| A1 | NI 方向措辞：MS Discussion "ω_cal parallels the direction of the neutrality index"——按标准定义 NI=(Pn/Ps)/(Dn/Ds)，ω_cal 实为 **1/NI（MK α 方向）**；SI 1.4 同步 | R1-M1 + R2-M2 | 改 "parallels the reciprocal of the neutrality index (the α-direction of the MK test)"；一处措辞 + SI 同步句 |
| A2 | ex-CC LIHC k_n CI 印 [1.00, 1.88]，ground truth [0.997, 1.880]——0.997 进位 1.00 使读者误判 CI 恰好排除 1 | R1-M3 + R4-M2 | 照实印 0.997（或注明包含 1） |

### B. 文本级单项（一句话级）
| # | 问题 | 来源 |
|---|---|---|
| B1 | 样本量三口径（3,567 分析 / 3,593 pair table / "29 excluded" 隐含 3,596）算术不可互推，Datasets 段一句澄清 | R4-M1 |
| B2 | smoking "jointly with age, sex, and admixture" 与实际模型（group+smoke+admix，+13.6/P=3.3e-4；含 age/sex 模型为 +13.3/P=1.4e-3）不符，措辞改 | R4-M3 |
| B3 | split-half↔polymorphism 对应缺 caveat：split-half 度量抽样/技术噪声而非 standing variation，作分母使 ω_cal 系统偏高（NI 经典偏倚方向）；文中数字已有，补一句 | R2-M1 |
| B4 | Fig 1a legend k_n "counterpart of the synonymous baseline" 缺 constrained 限定词 | R2-M3 |
| B5 | 孤儿文献：ref.39 全文未引、ref.15 仅 Data Availability author-year 未按编号引 | R6-1 |
| B6 | Supplementary Tables 5–19 未在主文引用（仅 SI 内部），加一句指针 | R6-2 |
| B7 | 阈值式 P 值（"all P<0.001"、"P<10⁻³⁰⁰"）给精确值 | R6-3 |
| B8 | 一作 ORCID 缺失 | R6-4 |
| B9 | span-matched 子集 k_f/k_n 分解（k_f 1.39 / k_n 0.33）已算未入文，补 SI Note 10 一句——3.68 比 6.10 更由 k_n 主导，诚实披露 | R5-M1 |
| B10 | ependymal donor-stratified P 反向变小（0.021 vs free 0.058/0.075），SI Note 12 补一句说明 | R5-M2 |
| B11 | Guide 5.9e "primary" 与 MS "in parallel" 口径不齐 | R5-M3 |
| B12 | Bergmann SD 5.72 (ddof=1) vs 5.583 (ddof=0)，Supp Table 3 图注注明 ddof | R5-M4 |
| B13 | Introduction "functional adaptation" → "functional change"（进化语境偏重） | R2-M4 |
| B14 | LOO 对外表述张力："非单一群体驱动"（CL 层）vs MS 正文 "depends on one outlier population"——MS 版正确，CL/回复信勿过度声称 | R1-M4 |
| B15 | 置换 P 末位 MC 精度：KRAS–EGFR 0.0034 换流 0.0049（MC SE≈6e-4），"P=0.003" 少报一位或注 MC 分辨率 | R3-M1 |
| B16 | composition ρ/|Δz| P 值按对独立算有 dyadic 依赖，Note 8 加 "descriptive" 注记（实质推断已用 cluster bootstrap） | R3-M2 |
| B17 | median k_n ratio 2.18–3.70（Note 8 表）与 Supp Table 11（2.08–3.61）口径不同，注出处 | R4-M5（可不改） |
| B18 | BRCA CI 上界 1.845 印 1.84 | R4-M6（可不改） |

### C. 计算级（低成本补算）
| # | 问题 | 来源 |
|---|---|---|
| C1 | composition cluster bootstrap B=200 与全文 B=1,000 不一致，重跑统一 | R3-M3 |
| C2 | ex-CC Cox 敏感性（32 CC 占 n=304 约 10%）或明示理由；NN/TT 与 high-purity 已做 | R4-M4 |
| C3 | 聚合顺序默认化缺同数据量化：mouse pilot 15 对在 brain 顺序下重算（秩相关/中位倍变）+ MS/GUIDE 两处 legacy 归因统一（mouse/human vs TCGA）+ 一句"包默认顺序不可复现 mouse/TS 绝对 ω" | R1-M2 |
| C4 | log-ω bootstrap CI 仅存 stdout，归档入 CSV | R3-M4 |

## 四、结论

- 第四轮 6/6 零 Major（连续第二轮），均分 7.73 → 8.53（+0.80），两位直接 Accept
- 全部问题为 Minor：A 组 2 条共识项 + B 组 16 条一句话级 + C 组 4 条低成本补算；无一项触及科学结论
- 数值核验 39+ 项全命中、零误报；上轮 Wilson 指控经独立复算证伪
- 分数轨迹 4.42 → 5.83 → 7.73 → 8.53 收敛良好；修复 A+B+C 后（预计 v49.14）具备投稿或终审条件，是否进行第五轮确认轮待作者定夺
