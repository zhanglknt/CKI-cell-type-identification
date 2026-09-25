# nc57 终审报告 — R2（单细胞/计算生物学）

**对象**：v0.5.3 @ 3d220ac（nc55 修复 + nc56 proof 30 处编辑后）；正文 213 行通读，SI 定点核验（L132/L167/L189/L215），proof 修复矩阵 `results/audit/nc56_proof_fix_matrix.md` 逐项对照。
**声明**：全部数字引自当版文本并亲自核对（含摘要词数实测、python 字符串级核验）；无法核验项已标注。

---

## 一、评分：**8.5 / 10**　verdict：**accept**（余 3 条 cosmetic Minor，可在排版阶段顺手处理）

子项：soundness 8.5 / novelty 6.5 / significance 7 / presentation 8.5。

上轮唯一 Major（M1，GTEx 措辞）及 B2 已全部按协商口径落实，proof 轮编辑未发现断链或数字矛盾；新导出 3 条 Minor（1 条数字区间遗漏、2 条措辞微瑕），均不触及结论。

---

## 二、上轮问题逐项核销（nc55 R2 清单）

| # | 上轮问题 | 当版证据（引文） | 结论 |
|---|----------|------------------|------|
| M1 | GTEx"否定野效应"四处断言式措辞 + Note 8 不确定度句 | ①摘要 L8："GTEx references in lung, liver, and breast **are consistent with** tumor-specific elevation"；②引言 L14："GTEx references **support as largely** tumor-specific"；③结果 L50："adjacent non-tumor resembles healthy tissue, **consistent with** tumor-specific elevation rather than a field effect **within cohorts**"；④讨论 L75："**consistent with** tumor-specific housekeeping elevation over a field effect **within cohorts**"；⑤SI Note 8 L189 新增量化容差句："The cross-cohort shift (GTEx–adjacent versus GTEx–GTEx pair k_n, **ratio ≈ 1.8–2.3×**) bounds the resolution of the healthy–adjacent comparison; the healthy ≈ adjacent similarity should be read within that tolerance (**tentative, GTEx cross-cohort discrepancy unresolved**)" | **RESOLVED**——四处均由断言降为"consistent with/support"+队列内限定，SI 侧给出 1.8–2.3× 容差与 tentative 声明，跨队列证据强度与措辞现已匹配 |
| m1 | 摘要 FPR 0.00 缺 HK 锚定限定 | L8："(**housekeeping-anchored** false-positive rate 0.00 versus 0.55–0.58 …)" | **RESOLVED** |
| m2 | 推荐细胞数下界 100 vs 50 不一 | L79："(i) at least ~100 cells per group (**operating window ~50–200**; power already erodes inside this window; …)"，与 L80(iv)"~50–200 cells"、SI 3.11、Note 16 口径一致 | **RESOLVED** |
| m3 | kn_floor"never reached"（逐对）vs"sits at the floor"（聚合）表观矛盾 | L49 已改"**essentially** never reached, leaving ratios identical across floors 0–10⁻⁴"（语境为逐对比率）；L90 聚合侧自带限定"**aggregate** k_n sits at the denominator floor in 3 of 5 cancer types"。显式"(pair-level)"未加，但两句各自语境已可消歧 | **PARTIAL（可接受，trivial 残余）** |
| m4 | FDR 全球/分层口径 | L63："no candidate survives **global** FDR correction (minimum q = 0.520)"；L65："**within-family** minimum q = 0.042" ✓；**残留**：L14 引言同句"no candidate survives FDR correction"未带 global（见新问题 N3） | **PARTIAL**（主体已修，L14 残留降为新 micro） |
| m5 | Note 14 Python 版本过时 | SI L215："the reference Python port augurpy is not distributed for Python **3.14**"，对齐 MS L116 钉死环境 3.14.4 | **RESOLVED** |
| m6 | TCGA 两段超长单句 | L48 现拆为 5 句（分层→分解→调整→置换→未调整声明）；L49 现拆为 5 句（四对照各居其所） | **RESOLVED**（当版文本状态判定） |
| m7 | TS 单供体基址结果处补指针 | L28："4,851 pairs across six organs (**largest-donor pseudobulks; Methods**)"；Methods L97 本体句在 | **RESOLVED** |
| B2 | KIRC/组成异质性句方向缠绕 | L75："A marker-panel composition check (Supplementary Note 8) **shifts** the pooled k_n coefficient by only −0.9%, but this masks heterogeneity: **the shift is largest in LIHC (+44%, the weakest reversal)** and KIRC (+20%)"——"attenuation is strongest where…"的缠绕表述已消除，方向词中性化且与 Note 8（LIHC +44.1%、KIRC +19.7%）一致 | **RESOLVED** |

---

## 三、nc56 proof 轮编辑核验（防引入性检查，全部通过）

- **A2/A3/A7** 摘要三处：实测 196 词 ✓；"housekeeping-anchored" ✓；"consistent with tumor-specific elevation" ✓；"(k_n-dominated)"与 L58/L76 口径一致 ✓。
- **M1–M18 MAIN 编辑**：L14 末句删除 ✓；L26 "(one-significant-digit resolution)" ✓ 且与 L69"indicative, dataset-relative scale"、SI Note 3"order-of-magnitude estimates"构成一致降级链 ✓；L30 "(also descriptive; …)" ✓；L32 CP 区间指针 ✓（SI Note 1 L155 区间本体在）；L37"four-tier"与 L108"the per-pair null constituting the fourth ladder tier"及 Fig 3(a) 三处互洽 ✓；L38"small-stratum raw JS 28.6% to 72.5%"消歧 ✓；L63/L65 global/within-family ✓；M9/M10 去重后同段首个指针保留 ✓。
- **X1–X8 图注/声明区**：Fig 2(b)"far smaller variation across categories"在（但见 N2）；Fig 3(a) 补 2,161/1,089/1,656 对数 ✓（与 L37/L108 一致）；Fig 3(c) 补 T1 对照区间（但见 N1）；Fig 5(d)"conserved" ✓；Fig 14"sanity-check value" ✓；L126 CI 覆盖说明（Linux CI，macOS/Windows 本地验证）✓ 且 v0.5.3 version DOI 10.5281/zenodo.22954782 写回 ✓。
- **S1–S4 SI 编辑**：S1 容差句 ✓（见 M1-⑤）；S2"calibration-relevant results" ✓（旧"all key results"已无）；S3"Python 3.14" ✓；S4 Guide 指针 5.13（未展开核验 Guide 本体，标注为未验）。
- **词额/构建**：摘要实测 196 词 ✓；MAIN 4,999 词与构建 221/221、XV8 63/63 为 team-lead 通报值（未独立复算，标注）。

---

## 四、新问题清单

**Major：无。**

**Minor（3 条，均 cosmetic）：**

1. **【数字区间遗漏，建议修】** L37 与 Fig 3(c) 图注："FPR 28.6% versus **37.6–45.2%** for the others"——SI 3.12（L132）列出的其余连续发散度量为 raw JS 45.2%、cosine 44.1%、Spearman 40.6%、k_f 37.6%、**k_n 35.7%**，"the others"的完整区间应为 **35.7–45.2%**；现区间下界 37.6%（= k_f）把 k_n 排除在外，而 k_n 与 k_f 同为分量，包含关系不一致。X5 本轮把该区间从 L37 带入 Fig 3(c) 图注（L37 实例早于本轮存在），建议两处一并改"35.7–45.2%"。主结论（ω 28.6% 最低）不受影响。
2. **【措辞，fix-introduced】** Fig 2(b) 图注新文案"k_n shows **far smaller** variation across categories"与 L25"k_n rose only 72–118-fold"（k_f ~400-fold，仅小 3.4–5.6 倍）之间存在程度词张力：72–118 倍的绝对升幅称"far smaller variation"偏松。建议改"smaller variation"或量化"(~4-fold smaller rise than k_f)"。
3. **【一致性，m4 残留】** L14 引言"no candidate survives FDR correction"未加"global"，与 L63 已修的"global FDR correction"不一致；在 L65 族内 q = 0.042 并存的情况下，引言句需同一限定（加"global"一词即可）。

---

## 五、结语

M1 的五处落实（四处"consistent with/support…within cohorts"+ SI 1.8–2.3× 容差句）精确命中上轮异议的实质——跨队列技术位移与待定位生物效应同量级时，野效应不能被排除、只能被限定在队列内口径陈述，当版文本现在正是这么说的。B2 的方向词中性化、m2/m5/m7 的口径对齐、m6 的句式拆分均到位；proof 轮 30 处编辑经字符串级核验未发现断链或矛盾。剩余 3 条 Minor 均为一句之内的 cosmetic 修正。从上轮 8.0（minor revision）上调至 **8.5，accept**。
