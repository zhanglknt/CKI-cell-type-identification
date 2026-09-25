# nc55 专家团盲审汇总（v0.5.2 终稿 @5a5ae6d）

2026-09-25 ｜ 六审独立重审 + 打分 ｜ 稿面冻结评审（review 期间零改动）

## 一、评分总览

| 审稿人 | 领域 | 分数 | verdict | Major |
|---|---|---|---|---|
| R1-stats | 统计方法学 | 8.0 | accept | 0 |
| R2-sccomp | 单细胞计算 | 8.0 | minor revision | 1 |
| R3-cancer | 肿瘤基因组 | 8.0 | minor revision | 0 |
| R4-brain | 脑图谱 | 7.5 | accept | 0 |
| R5-editor | 编辑/写作 | 9.0 | accept | 0 |
| R6-repro | 可复现性 | 7.0 | minor revision | 2 |
| **均分** | | **7.92** | 3 accept + 3 minor | **3** |

- 均分 7.92（R6 以其终版为准——git-archive 干净检出实测，取代其预评 8.0）；六审全部正面结论，无任何"缺陷/拒稿"级裁定。
- Major 3 条：① **R2-M1** GTEx field-effect 措辞——即 nc53 已沿留 proof 的 R2-B1 项，R2 本轮盲审独立重新导出同一问题，并明确"沿留 proof 接受、落实措辞软化即达接收标准"；② **R6-Major1** spot_check.py 在干净归档 L37 即崩（13 个模块级输入 7 个未跟踪）且 Section 1–2 停留在退役 softmax 口径、L93 自指断言；③ **R6-Major2** 复现指南 "data:" 核验指针指向归档中不存在的文件（tcga_composition_v44.txt 等），且从未披露 reference_results 镜像与 .gitignore 白名单策略。

## 二、类 A：ground-truth 确认的失配（一行级修复，建议本轮处理）

| # | 问题 | 来源 | 核验证据（当版文本/数据） |
|---|---|---|---|
| F1 | ref 19 引用错配：L60 "regionally specialized astrocytes highest 19" 引的是 Tan 2020 microglia 综述；句末 "strictly hypothesis-generating 19" 悬空 | R4/R2 | 文献表 L146：19. Tan, Yuan & Tian, Microglial regional heterogeneity, Mol. Psychiatry 2020。microglia 综述不能支撑星形胶质区域特化。修：L60 换 Batiuk 2020/Bayraktar 2020 类；悬空 19 移挂 microglial 区域异质性句或删 |
| F2 | Data availability "Tables 1–4 are cited in the main text" 失真 | R5-④/R2-M4 | 正文 L49 实引 Supplementary Table 5 与 Table 14（v49.5 后 GTEx/microglia 新增把 5/14 带进正文，声明未同步）。修：采 R5 建议整句替换为 "All Supplementary Tables (1–19) are provided in CKI_Supplementary_Tables_NC.xlsx."（**已落实**） |
| F3 | GTEx 措辞过强：Intro "GTEx healthy references confirm as tumor-specific"；L50 "tumor-specific rather than a field effect" vs 摘要仅 "argue against a field-effect reading" + KIRC 例外 + SI Note 8 自家限定 "mechanistic claims rest on within-cohort orderings only"（GA 跨队列对达 tumor 水平） | **R2-Major**/R5-①/R3-N4 | L14/L50/摘要/SI 原文均已核。修：Intro 软化为 "consistent with tumor-specific elevation in three of four organs" 类；L50 保留结论但补 within-cohort 限定——与 proof 沿留 B1 为同一修复 |
| F4 | KIRC 754（SI Note 8 matrix 级）vs 750（MS pair 级）缺桥 | R3-N1 | SI L186 "754 tumors, 84 NATs"；MS pair 级 750/82。修：SI 句补 "(750 retained in pair-level analysis)" |
| F5 | "the housekeeping floor (k_n ≥ 10⁻⁴) is never reached" 需层级限定 | R3-N2/R2-③ | MS L49 原文已核；R3 引敏感性表 KIRC NN 1/3,321 对触及 floor（比值不变）；R2 补聚合层面对照。修：加 "at pair level" 或 "essentially never reached"，具体措辞定稿时对照源数据 |
| F6 | "attenuation is strongest where the reversal is weakest (LIHC +44%, KIRC +20%)" 例证与趋势相反 | R3-N3 | 源数据 ex-CC：衰减 LIHC +44.1/KIRC +19.7/LUAD −2.0/LUSC −9.0；反转强度 LUAD 2.46>KIRC 1.88>LUSC 1.71>BRCA 1.57>LIHC 1.11。KIRC 衰减第二强但反转第二强。修：改 "strongest in LIHC (+44%), whose reversal is weakest (1.11)" |
| F7 | ~~Cox/文献处 "the the" 叠字（+Karagöz 变音符核对）~~ **FALSE POSITIVE** | R3-⑥ | fulltext grep 复核：命中均系 "the theoretical" 子串假象；MS 全文无 "the the"、无 Karagöz。**不改稿** |
| F8 | ~~"all four standard distance metrics" vs Table 2 五列（含 Pearson）~~ **FALSE POSITIVE（幽灵条目）** | 误挂 R2-M1 | 六审报告全文 grep 无任何 Pearson/−0.18 指控（R2-M1 实为 GTEx 措辞=F3）；Supp Table 2 xlsx 实查仅 ω+四距离逐对值、无 Pearson 列；4,851 对复算 Spearman −0.36~−0.46 与 Pearson −0.31~−0.42 同号同档；正文三处相关表述均已点明 Spearman。**不改稿** |

## 三、类 B：措辞/放置优化（确认存在，可修可沿留 proof）

- 摘要 FPR 0.00 加 "with the HK anchor" 限定（R2-①）
- panel 推荐下界两处口径 100–200 vs 50–200（R2-②，L79 已核 "at least 100–200"）
- FDR 表述加 global / within-family 层级限定（R2-④）
- 模拟 FPR 0/35 补 Wilson 95% CI ≈ [0, 0.082]（R1/R2 建议性增强，SI 一句）
- Bergmann 6.10 [3.16,11.69]（L22 原文已核）↔ span-matched 3.66（L34/45）正文加桥句（R2-M3）
- microglia three-tier vs four-tier 层级表述协调（R5-③/R3-①）
- 28.6% 双现（ω FPR 28.6% vs raw JS 28.6%，相邻段不同量同值，已核）改一处精度（R5-⑥）
- 摘要 1.11–2.46 升序 vs Results 2.46→1.11 降序统一（R3-⑤，首现已核在摘要）
- 7.70/CI "one significant digit" 限定前置到首次使用处（R3-②/R1；6.38 五处均与 7.70 同现，披露已足，仅前置问题）
- Fig 1(b) 补 "(b) 30/2,161"、Fig 3 图注数字是否自 SI 上提（R6-N3/N4，图注级）
- TS 单供体基址结果处补指针（R2-⑦）；Note 14 Python 版本串与钉死声明口径核对（R6 称 3.13.12 已钉、R2 称 conda 3.14.4——以 Note 14 原文为准核对一次）
- DeLong 方法 SI-only（R1-④）、脑残差三项 MS vs SI（R1-②）、独立性限定位置（R1-③）、Bergmann-Glia n=21 SM-only（R1-⑤）、internal pairing 强度分级（R1-⑥）——披露位置类

## 四、类 C：与既有决策冲突，需用户定夺

- **摘要措辞回退**：R5-② 建议 "best discrimination at bounded power"（可读性，+2 词 → 198/200）vs nc54 决策 B 既定 "best bounded-power discrimination"（196/200，为 proof 留 4 词余量）。回退吃掉余量的 2/4。
- **packagist 预注册占位**（R6-N2）：外部动作，注册后发版可复用名称。

## 五、结论

nc55 轮均分 7.92（与 nc53 确认轮 8.08 同档）。Major 3 条：R2-M1 系已沿留 proof 的 B1 GTEx 措辞之再发现（软化措辞即关闭，本轮 F3 已落实 Intro/Results 两处软化，Discussion/摘要留 proof）；R6 两条基建 Major（spot_check 断裂、指南指针断裂）属机械修复、零分析返工，本轮已全部修复（spot_check Section 1–2 改读 nc52 excc 权威 CSV、L93 改真读 brain_bs_null_results.csv q_fdr=0.5202、8 个输入文件入库含 mouse_splithalf_v44 与 hallmark_2020.gmt、指南指针重定向 superseded/excc + 跟踪策略披露段、test_reference_values MIRROR 随 46fa93a 目录迁移同步）。类 A 八项中 F1–F6 已修，F7/F8 经 ground-truth 复核为假阳性不改稿。稿面无统计学/生物学实质缺陷被提出。

各审稿报告：results/audit/nc55_blind_review_R1.md … R6.md
