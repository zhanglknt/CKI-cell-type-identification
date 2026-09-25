# nc57 终审报告（R5：编辑/科学写作，v0.5.3）

- 审查对象：`results/CKI_Manuscript_NC_fulltext.txt`（v0.5.3 当版全文，逐行重读）；`results/CKI_Supplementary_NC_fulltext.txt`（276 行，抽查 proof 修复点）
- 参照：`results/audit/nc56_proof_fix_matrix.md`（30 处编辑清单）；本人上轮报告 `nc55_blind_review_R5.md`
- 审查人：R5-editor（NC 处理编辑/科学写作）；日期：2026-09-25；全文重读 + 全部数字当版实测，未凭上轮记忆

## 总评分：9.0/10 ｜ Verdict：accept（投稿就绪）

Major 0 条；Minor 3 条（1 条团队裁定维持 + 2 条 proof 轮新增残留，均为一词/一指针级 cosmetic）。

## 一、合规锚点实测复核（当版亲自测量）

| 锚点 | 任务书口径 | 本人实测 | 裁定 |
|---|---|---|---|
| 标题 | 未变 | 13 词，"decomposing" 在位 | ✓ |
| 摘要 | 196 词无引用 | 196 词、无引用 | ✓ |
| MAIN（Intro+Results+Discussion 含子标题，L9–L81） | 4,999 | **4,999**（本轮与官方口径零偏差；历轮 +2~3 差异消失） | ✓ |
| 文献 | — | 57 条（编号 1–57） | ✓ |
| 主图/主表图注 | ≤350 词/条 | Fig 1–6 + Table 1 全在（222/264/315/216/108/229/100 词，最长 Fig 3 = 315） | ✓ |
| Supp 图注 | — | Supp Fig. 1–14 全（L201–214，30–144 词） | ✓ |
| Code availability | v0.5.3 + 新 version DOI | L126："v0.5.3…tag v0.5.3…concept DOI: 10.5281/zenodo.20405458; version DOI for v0.5.3: **10.5281/zenodo.22954782**"；Methods L86 "package v0.5.3" | ✓ 内部一致且与发布链口径一致 |
| 版本残留 | 无 | 全文 grep：v0.5.2 / 22949350 / 0.5.1 / 22938380 均 0 次 | ✓ |
| 声明区块 | 齐 | Data availability（L124，含 Supp Tables 1–19 句）、Code availability（L126）、LLM 声明（L121–122）、Statistics and reproducibility（L117–120）、Acknowledgements/Author contributions/Competing interests | ✓ |
| 结构 | Intro→Results→Discussion→Methods | 一致，Discussion 无子标题 | ✓ |

## 二、上轮（nc55）6 条 Minor 逐条核销

| # | 上轮问题 | 当版证据 | 裁定 |
|---|---|---|---|
| 1 | Intro L14 "GTEx healthy references **confirm** as tumor-specific" 动词过强 | L14 现作 "an elevated housekeeping baseline that GTEx references **support** as **largely** tumor-specific"；摘要同步软化为 "GTEx references in lung, liver, and breast are consistent with tumor-specific elevation"（L8），kidney 例外由 "largely" 与摘要器官限定共同兜住 | **RESOLVED** |
| 2 | 摘要 "best **bounded-power** discrimination" 连字符链 | 仍在（L8）；fix matrix 第四节裁定"维持"（nc54 决策 B，类 C 冲突项按既定决策跳过） | **UNRESOLVED（团队裁定维持）**——尊重裁定，保留个人意见见三.N3 |
| 3 | 术语/编号打包（three-tier vs four-tier；Fig 5(d) conservative；Fig 2(b) relatively constrained；L78 "(14; Results)"；裸节号 3.12/1.4） | 逐项验证：L37 "four-tier drift ladder"；L198 "Top 5 **conserved** cell-type pairs"；L195 "k_n shows **far smaller variation** across categories"；L78 "(**ref.** 14; Results)"；裸节号全灭（grep 复核：MS 现存 8 处 "Section X.Y" 引文 7 处为全式，唯 L48 一处残留，见三.N2） | **RESOLVED**（遗留 1 处同类见 N2） |
| 4 | Data availability Supp Tables 二分句失实 | L124 末句已整句替换为 "All Supplementary Tables (1–19) are provided in CKI_Supplementary_Tables_NC.xlsx."——即上轮建议原文 | **RESOLVED** |
| 5 | SI Note 3 "all key results" + Discussion L69 "operational scale" 与 L26 降级不同步 | SI L167 现作 "reported in **the calibration-relevant results**"；L69 现作 "ω_cal = ω / 7.70 is **an indicative, dataset-relative scale**"；且 L26 新增 "(one-significant-digit resolution)" 前置精度限定，三处口径已对齐 | **RESOLVED** |
| 6 | L38 raw JS 28.6% 与 L37 ω T1 28.6% 同值相邻；L75 "attenuates…by only −0.9%" | L38 现作 "**small-stratum** raw JS 28.6% to 72.5%"；L75 现作 "**shifts** the pooled k_n coefficient by only −0.9%…the shift is largest in LIHC" | **RESOLVED** |

核销结论：6 条中 5 条完全落实（其中 #4 按我建议原文落地），1 条经团队裁定维持。

## 三、proof 轮（nc56）编辑复核与新增问题

### 3.1 30 处编辑复核

- **摘要 7 处（A1–A7，净 0 词）**：全部在位且行文自然。"Inspired by Ka/Ks"（L8）无损语义；"four of five CIs excluding 1" 与 L47/L75 两处处方一致（"CI excluding 1 in four of five, LIHC excepted" / "CIs excluding 1 in four of five cancers"）；"reflected stromal/immune admixture" 比原 "was explained by" 更贴合 L48 证据强度（admixture 校正后 EGFR 关联消失是"反映"而非"解释"）。"(k_n-dominated)" 标签与 L60 "it is k_n-dominated" 口径一致。
- **MAIN 18 处（M1–M18，净 −2）**：全部在位。M1 删 L14 末句后段落收束于 "bounded, hypothesis-generating catalogue"，节奏无损；M2 精度前置与 M13 降级形成首尾呼应；M18 改写后 L79 "(i) at least ~100 cells per group (operating window ~50–200; power already erodes inside this window…)" 与 L80(iv) "bounding the operating window at ~50–200 cells" 自洽。
- **Methods/图注/声明区 8 处（X1–X8）**：全部在位。X1（L108 "in three tiers (the per-pair null constituting the fourth ladder tier)"）从定义层闭合了 three/four-tier 张力；X4 图注计数（2,161/1,089/1,656）与 L37、L108 三处一致；X8 CI 覆盖声明为事实性限定，措辞克制。
- **SI 4 处（S1–S4）**：全部在位。S1（L189）新增句 "The cross-cohort shift (GTEx–adjacent versus GTEx–GTEx pair k_n, ratio ≈ 1.8–2.3×) bounds the resolution of the healthy–adjacent comparison…(tentative, GTEx cross-cohort discrepancy unresolved)" 量化不确定度并显式 tentative，优于矩阵原文表述；S2/S3/S4 均核实。
- **词额总账**：摘要 196/200、MAIN 4,999/5,000，与矩阵宣称（净 0 / 净 −2）吻合；实测值与官方 XV8 口径本轮零偏差。

### 3.2 新增问题（proof 轮引入/暴露）

**Major：无。**

**Minor N1（proof 部分修复引入，跨文档术语不一致）**：X7 将 MS Fig 14 图注改为 "the **sanity-check** value lies"（L214），但 SI Note 16 正文（SI L222）同义句仍是 "the **validation** value lies in ω tracking the functional contrast far above its own neutral baseline on an independent dataset"——两句措辞逐字平行，术语未同步。建议 SI 同步改 "sanity-check value"。

**Minor N2（上轮 Minor 3 同类残留，proof 漏网）**：L48 "label-permutation confirmed; **Section 3.13**)." 为裸节号，而同行后文已是全式 "Section 3.13 of the Supplementary Information"。proof 轮修复 3.12/1.4 三处时漏了这处（我上轮清单未列 3.13，亦有责任）。建议补全式或删裸引（同句已有全式指针，可直接删 "Section 3.13"）。

**Minor N3（团队裁定维持，记录在案）**：摘要 "gave the **best bounded-power discrimination**"（L8）。我仍认为 "best" 与 "bounded-power" 的修饰关系对首读读者有歧义（宜 "best discrimination at bounded power"），但 fix matrix 已按 nc54 决策 B 裁定维持，摘要 196/200 有 4 词余量的事实不变。不再施压，proof 阶段若动摘要可顺带考虑。

### 3.3 观察项（不构成 Minor）

- L37 "four-tier drift ladder of library-level pairs 12: T1…; T2…; T3…" 冒号后只枚举三层，第四层（per-pair null）要靠 Fig 3(a) 图注与 Methods L108 补全。三处文本合读无矛盾，单读 L37 有半拍迟疑；若 proof 还动 L37，可写 "a four-tier drift ladder (per-pair null plus T1–T3 pair tiers)"。
- 摘要 "rejected neutral housekeeping drift (**housekeeping**-anchored false-positive rate 0.00…)" 一句内 "housekeeping" 两现（A2 为 R2-① 加的限定，功能正当）；可省括号内 "housekeeping-anchored" 而不损义。
- 标题/摘要/正文三层 GTEx 口径现已完全一致（lung, liver, and breast + kidney 例外），此为 nc54–nc56 两轮打磨的正向结果，特此记录。

## 四、强项（独立重评确认）

1. **声明-证据匹配经 proof 轮后再无失衡点**：本轮所有软化（"reflected"、"consistent with…within cohorts"、"support as largely"、"indicative, dataset-relative"）均使措辞与证据强度更贴合，无一处过度降级导致的表意损失。
2. **ω_cal 精度口径全链一致**：L26 "(one-significant-digit resolution)" → L69 "indicative, dataset-relative scale" → SI Note 3 "calibration-relevant results"，三跳同步，这是四轮评审拉扯最久的一处，现已闭合。
3. **图注自足性保持**：Fig 3(c) 新增 "(T1: 28.6% versus 37.6–45.2% for the others)" 后读者无需回查正文；Fig 3(a) 四层阶梯定义完整；最长图注 315 词仍低于 350 上限。
4. **proof 轮执行质量高**：30 处编辑词额对冲净 0/−2，实测复核无偏差；无版本号残留、无断句、无指代断裂（L14 删句后段落流完整）。

## 五、修改建议（proof 阶段一次过，均一词级）

1. SI L222："the validation value lies" → "the sanity-check value lies"（对齐 MS Fig 14）。
2. MS L48："label-permutation confirmed; Section 3.13)." → 删 "Section 3.13"（同行已有全式指针）或补 "of the Supplementary Information"。
3.（可选）L37 "four-tier drift ladder" 后补 "(per-pair null plus T1–T3)"；摘要括号内 "housekeeping-anchored" 可省。

---
**一句话总评**：nc56 proof 轮 30 处编辑全部落实到位且行文无补丁感，我上轮 6 条 Minor 核销 5 条（1 条团队裁定维持），合规锚点实测全数通过、MAIN 与摘要词数与官方口径零偏差——残留仅 2 条一词级跨文档/指针瑕疵，投稿就绪。
