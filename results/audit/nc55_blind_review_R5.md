# nc55 盲审报告（R5：编辑/科学写作，v0.5.2 @5a5ae6d）

- 审查对象：`results/CKI_Manuscript_NC_fulltext.txt`（当前终稿全文，逐行通读）；`results/CKI_Supplementary_NC_fulltext.txt`（抽查）
- 审查人：R5-editor（NC 处理编辑/科学写作）；日期：2026-09-25；独立重审，未沿用上轮结论
- 词数/条目均为本人在当版文本上的实测（空白切词）

## 总评分：9.0/10 ｜ Verdict：accept（投稿就绪）

## 合规锚点实测复核

| 锚点 | 任务书口径 | 本人实测 | 裁定 |
|---|---|---|---|
| 标题词数 | 13 | 13 | ✓ |
| 摘要 | 196 词无引用 | 196 词、无引用 | ✓ |
| MAIN | 4,999/5,000 | 5,002（含子标题，空白切词） | ✓ 附观察 |
| 文献 | 50+ | 57 条 | ✓ |
| 结构 | Intro→Results→Discussion→Methods | 一致 | ✓ |
| 主图/主表 | 6+1 | Fig 1–6 图注 + Table 1 图注（L200） | ✓ |
| Supp 图注 | — | Supp Fig. 1–14 全（L201–214） | ✓ |
| Code availability | v0.5.2 + 双 DOI | L126："v0.5.2…tag v0.5.2…concept DOI: 10.5281/zenodo.20405458; version DOI for v0.5.2: 10.5281/zenodo.22949350" | ✓ 内部一致 |

**观察（非缺陷）**：MAIN 我的切词口径 5,002、官方 XV8 口径 4,999——历轮我的口径恒定高 2–3 词（em-dash/括号处理差异），两种口径均显示 MAIN 贴 5,000 线、余量为零；proof 阶段任何增补须同步删减。

## 强项

1. **声明-证据匹配为本文最大特色且经多轮打磨后无失衡点**：强声明全部带数字+CI+反向对照，且主动暴露对己不利结果（L43 MELD/scDist 满分而 ω 在 500 基因移位时 AUC 崩至 0.05–0.13；L48 EGFR 关联经纯度校正消失 "all adjusted P > 0.4"；L67 候选目录 "only 3 of 39 Strong candidates survive a switch to a global-k_n estimator"）。
2. **摘要（196 词）信息结构优秀**：每个结果一句、数字与限定词配比恰当，"gave the best bounded-power discrimination"、"though specificity decays with group size"、"GTEx references argue against a field-effect reading" 等措辞与正文的证据强度严格对齐，无夸大。
3. **局限性陈述（L80，(i)–(v) 分条）位置与内容俱佳**：每条边界均有量化（操作窗口 ~50–200 cells、"once 500 genes shifted, the ratio collapsed (AUC 0.05–0.13)"、PMI 代理的盲区），且与 Results 的相应控制互为引用，不构成事后补丁。
4. **图注自足性**：统计量、n、B、CI 方法、检验方向齐备；Fig 4(a) 经 nc54 修后 "while the NN/TT ratio of k_f does not [exceed 1]" 消除了 k_f 取向歧义；Fig 6(b) 同时给出 6.10 未校正上限与 3.66 [1.92, 3.78] 校正估计，读者无需回查正文。
5. **结果-讨论分工干净**：机制性解读全部后置（L75 pan-cancer 的 bulk 分辨率限定、L77 "literature anchoring, not independent validation"），Discussion 无子标题符合 NC 惯例。

## Major 清单：无

（铁律执行说明：疑似 MS↔SI 数字冲突已逐一 ground-truth 复核后排除——pooled attenuation MS "−0.9% pooled, 95% CI −4.3% to +2.5%"（L49）与 SI L187 authoritative ex-CC 口径 "−0.9% (cluster-bootstrap median −0.8%, 95% CI [−4.3%, +2.5%])" 一致；SI L186 的 −1.3% 系已标注 superseded 的 v44 softmax 口径；GTEx fold MS L50 "2.0–2.8-fold" 与 SI L189 一致且与原始中位数（2.07–2.77）吻合；LIHC +44%/KIRC +20%（L75）= SI +44.1%/+19.7%。均不构成问题。）

## Minor 清单（6 条，均不阻断投稿）

1. 【遗留第 2 轮】Intro L14："GTEx healthy references **confirm** as tumor-specific"——"confirm" 为全文对该证据用的最强动词，强于同篇摘要的 "argue against" 与 Discussion 的 "supporting"（L75），且 kidney 为例外（L50）。建议改 "identify … as tumor-specific in lung, liver, and breast" 或 "support"。
2. 【v0.5.2 减重引入】摘要 "gave the **best bounded-power discrimination**"：为省词把 "best discrimination at bounded power" 压成连字符链，"best" 与 "bounded-power" 的修饰关系变浅，首次阅读易误为"最佳判别力"而非"在有界功效下最优"。建议恢复 "gave the best discrimination at bounded power"（+1 词，摘要现 196 词有 4 词余量）。
3. 【遗留第 4 轮】术语/编号打包：L37 "three-tier drift ladder" vs Fig 3(a) 图注 "four-tier"（L196）；Fig 5(d) "Top 5 **conservative** cell-type pairs"（应 conserved，L198）；Fig 2(b) "k_n remains relatively constrained"（L195，与 L25 "k_n rose only 72–118-fold" 的相对性表述张力）；L78 "(14; Results)" 引用渲染；L37/L108 裸 "Section 3.12"、L72 裸 "Section 1.4"（他处已全式 "of the Supplementary Information"）。
4. 【遗留第 4 轮】Data availability（L124）："Supplementary Tables 1–4 are cited in the main text" 与实际不符——主文 L49 另引 Table 5 与 Table 14；且 xlsx 已 19 sheets 齐备后，该二分描述失去存在意义，建议整句删除或改为 "All Supplementary Tables (1–19) are provided in CKI_Supplementary_Tables_NC.xlsx."。
5. 【遗留第 3 轮】SI Note 3 结尾（SI L167）"Both raw and calibrated ω values are reported in **all key results**" 与主文 headline 全报原始 ω 的实践不符；Discussion L69 "ω_cal = ω / 7.70 is the operational scale" 同属此张力（L26 已把 ω_cal 降为 "indicative only"，Discussion 措辞未同步降）。
6. 【遗留第 2 轮】L38 "(14.1% below 30 nuclei to 48.0% above 500; **raw JS 28.6% to 72.5%**)"——raw JS 组层下限 28.6% 与 L37 ω 的 T1 总体 FPR 28.6% 同值相邻出现，易误读为同一量；建议给 raw JS 加 "small-size stratum" 限定。另 Discussion L75 "attenuates the pooled k_n coefficient by only −0.9%" 负号与 "attenuates…by only" 搭配拗口，建议 "shifts the pooled k_n coefficient by only −0.9%"。

## nc53/nc54/v0.5.2 处置逐条复核意见

| 批次 | 处置 | 当版文本证据 | 意见 |
|---|---|---|---|
| nc53 | 5,151 full-inventory 限定 | L70 "permuting k_n across the 5,151 full-inventory human pairs" | 落实，行文自然 |
| nc53 | Table 1 表注 | L200（含 "provided as a separate file (CKI_Tables_NC.xlsx)"） | 落实，格式合规 |
| nc53 | Supp Fig. 14 图注 | L214（microglia 88,494 vs CNS macrophage 3,344；P = 5.5 × 10⁻¹⁴；AUC = 1.00） | 落实，自足性好 |
| nc53 | SI 19 sheets | L191 声明 + 前轮实测 workbook.xml | 落实 |
| nc54 | GTEx 肝句方向修复 | SI L189 "in liver the two medians coincide (ratio 1.03) but the distributions differ, one-sided MWU P = 3.8 × 10⁻⁵, with a heavier adjacent upper tail" | 修复质量高：中位数重合与分布差异分开陈述，方向正确，无补丁感 |
| nc54 | fold 2.0–2.8 限定 | MS L50 = SI L189 一致 | 落实 |
| nc54 | Fig. 4a k_f 取向 | L197 "while the NN/TT ratio of k_f does not" | 消歧到位 |
| nc54 | ρ 指代写明 | L49 "non-parenchymal fraction versus k_n, ρ = 0.20–0.26" | 落实（我 nc53 minor #2 关闭） |
| nc54 | 38% 标明模拟 | L70 "under fourfold cell-count imbalance (simulation)" | 落实 |
| nc54 | GTEx pair-independence 限定 | SI L189 尾句 "treat pairs as independent and are descriptive only" | 落实 |
| nc54 | Table 5 表注 ex-CC 口径 | SI 侧（si_verify 覆盖，未逐项抽查） | 信任断言层 |
| v0.5.2 | 摘要 196/200 | 实测 196 | 达标；唯 "best bounded-power discrimination" 措辞见 Minor 2 |
| v0.5.2 | 版本面 + DOI | L126 v0.5.2 / tag v0.5.2 / 22949350 | 内部一致 |

## 具体修改建议（proof 阶段一次过）

1. L14："confirm as tumor-specific" → "identify as tumor-specific in lung, liver, and breast"；
2. 摘要："gave the best bounded-power discrimination" → "gave the best discrimination at bounded power"；
3. L37 "three-tier" 与 Fig 3(a) "four-tier" 统一（建议正文改 "four-tier"，与图注及 n-matched null 算一层的口径一致）；
4. Fig 5(d) "conservative" → "conserved"；Fig 2(b) → "k_n rises less than k_f across categories"；
5. L78 "(14; Results)" → "(ref. 14; Results)"；L37/L108/L72 裸节号补 "of the Supplementary Information"；
6. L124 删改 Supp Tables 二分句；L38 raw JS 加 "small-size stratum"；L75 "attenuates…by only −0.9%" → "shifts…by only −0.9%"；
7. SI Note 3 "all key results" → "in the calibration-relevant results"，或 Discussion L69 "operational scale" 同步降为 "indicative, dataset-relative scale"。

---
**一句话总评**：经 nc53/nc54/v0.5.2 三轮后文本已达投稿状态——声明-证据匹配、局限性陈述与图注质量在方法学论文中属上乘，无 Major；6 条 Minor 全为措辞/编号层 cosmetic，proof 阶段一次过即可。
