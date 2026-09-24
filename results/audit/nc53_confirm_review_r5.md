# nc53 确认轮报告（R5：编辑/格式终审确认）

- 审查对象：修复后 MS（`results/CKI_Manuscript_NC_fulltext.txt` + docx 双层核对）、SI 抽查（`CKI_Supplementary_NC_fulltext.txt`）、CL docx、SI xlsx（zipfile 读 workbook.xml）、图资产目录、git log
- 审查人：R5-editor；日期：2026-09-24；基线：上轮报告 `nc52_final_review_r5.md` + 轮次汇总 `nc53_final_review_round_2026-09-24.md`

## A. 逐条裁定表

| # | 条件项 | 裁定 | 引文证据（当前文本原句） |
|---|---|---|---|
| 1 | M5 "5,151 vs 4,851" | **RESOLVED（裁定反转，原指控撤回）** | 经 ground truth 复核确认我上一轮"疑为笔误"的指控错误：SI Note 9 新增小节明示 "On the full-inventory human pair set (**5,151 pairs, the 102-entry inventory** before the 99-entry filter that yields the 4,851 analyzed pairs), the floor is 0.524 (95% CI [0.506, 0.541]) while the observed Spearman correlation is 0.089"（SI L193），与 `nc52_stats_omega_kf_math_floor.csv` 逐字吻合；MS L70 已加限定 "permuting k_n across the 5,151 **full-inventory** human pairs"。两个输入集（102-entry inventory / 99-entry filtered）各自成立，修法（加限定词 + SI 补 provenance）正确。 |
| 2 | M1 主表 Table 1 表注 | **RESOLVED** | MS L200 新增 "Table 1. Cross-organ conservation ranking by cell type (Tabula Sapiens, n = 59 same-cell-type cross-organ pairs). … The table is provided as a separate file (CKI_Tables_NC.xlsx)."，位置在 Figure 6 图注之后、Supp 图注之前，格式与 NC 惯例一致（题注+解读限定+文件指针）。 |
| 3 | M2 Supp Fig. 14 图注+资产 | **RESOLVED** | MS L214 新增 "Supplementary Fig. 14. Human-brain sanity check on the microglia supercluster (Supplementary Note 16). …ω = 21.83 ± 7.20 functional versus 1.30 ± 0.36 neutral; Mann-Whitney P = 5.5 × 10⁻¹⁴; exact rank AUC = 1.00"（约 140 词，≤350，n/统计量/AUC 自足）；图资产 `results/figures_submission_nc/Supplementary_Fig_14.pdf` 已存在（git 4a7a34c 随批提交）。 |
| 4 | M3 CL 口径 | **RESOLVED** | CL 现为 "across **3,535** TCGA samples…(NN/TT ω ratio **1.11–2.46**, bootstrap CIs excluding 1 in four of five)"、"gave the best functional-versus-neutral discrimination **at bounded power** (AUC = 0.80)"，并新增 GTEx 句 "A GTEx healthy reference further shows adjacent-normal k_n at healthy-tissue levels in lung, liver, and breast, arguing against a field-effect reading"。 |
| 5 | M4 SI xlsx 缺 Tables 1–4 | **RESOLVED** | xlsx 实测 sheet 清单 = Table 1–Table 19 全 19 张；SI docx 四段各补指针，如 L264 "Table content: CKI_Supplementary_Tables_NC.xlsx (sheet Table 1)"、L273 (sheet Table 4，6,591 threshold-passing rows)。 |
| 6 | 声明区块内部一致性（DOI 写回） | **RESOLVED** | MS L126："The CKI source code (**v0.5.1**) is publicly available at … (tag **v0.5.1**) under the MIT License. A permanent archival copy has been deposited at Zenodo (concept DOI: **10.5281/zenodo.20405458**; version DOI for v0.5.1: **10.5281/zenodo.22938380**)." 版本号/tag/concept+version DOI 四处口径一致；git 95a4cf7 记录 Zenodo record 22938380 归档确认。R6 唯一硬条件随之关闭。 |
| 7 | 期刊合规复核 | **RESOLVED（附 1 条观察）** | 标题 13 词 ✓；摘要无引用 ✓；6 主图 + 1 主表 ✓；文献 57 条首现单调 ✓；结构 Intro→Results→Discussion→Methods ✓；声明区块齐备 ✓。**观察（非缺陷）**：词数口径差异——任务书报摘要 197 / MAIN 4,997，我用空白切词独立实测为摘要 200 / MAIN 4,999（±2–3 为切词器对 em-dash/括号的处理差异）。两种口径均达标，但摘要按我口径恰好 200 词、余量为零，proof 阶段任何增补都需同步删减。 |
| 8 | SI 修复抽查（非我条件项，顺带验证） | **RESOLVED** | Table 11 图注不再出现 "Fig. 5a"（grep 零命中）✓；Note 9 floor 段 ✓；Note 1 DeLong 方法段 "[0.770, 0.838]…cluster bootstrap [0.771, 0.836]"（SI L159）✓；GTEx 段含 liver 边际与 "P ≤ 3.2 × 10⁻⁸⁴"、kidney 例外（L189）✓；severity JT "P < 10⁻¹⁵"（L195）✓；4.3 队列层级 "3,567…before the barcode audit…ex-CC default…3,535…full expression-matrix cohort (3,596…KIRC 754)"（L147）✓。 |

## B. 新增问题

### Major：无

### Minor（5 项）

1. 【修复引入】Intro L14："attributable to an elevated housekeeping baseline that GTEx healthy references **confirm** as tumor-specific"——"confirm" 强于证据：Discussion 自用 "supporting"（L75），且 kidney 为例外（L50）。建议改 "support" 或 "identify as tumor-specific in lung, liver, and breast"。
2. 【修复引入】Results L49 尾句 "pending single-cell validation (reference-free composition check: **ρ = 0.20–0.26 versus k_n**; Supplementary Note 8)"——括注内 ρ 的对象未定义（读者无法判断是 composition–k_n 相关），建议写成 "composition–k_n correlation ρ = 0.20–0.26"。
3. 【既有遗留，第 3 轮】SI Note 3 结尾（L167）仍称 "Both raw and calibrated ω values are reported in **all key results**"，与主文 headline 全报原始 ω 的实践不符。前轮两轮指出未修。
4. 【既有遗留，第 3 轮】术语/表述不一致打包：MS L37 "three-tier drift ladder" vs Fig 3 图注 "four-tier"；Fig 5(d) "Top 5 **conservative**"（应 conserved）；Fig 2(b) "k_n remains relatively constrained"；L78 "(14; Results)" 渲染；L37/L108 裸 "Section 3.12"、L72 裸 "Section 1.4"（L24/L38/L47/L48/L79 已修为全式，修复**不彻底**而非未动）。
5. 【既有遗留，第 2 轮】CL "28.6% versus **35.7–45.2%** for the other five"（含 k_n）vs MS L37 "**37.6–45.2%** for the others"（不含 k_n）——两个区间各自自洽但集合定义不显化；另 CL 首段仍用 "principled **separation**" 而标题已改 "decomposing"，建议对齐动词。另注：Data availability 句 "Supplementary Tables 1–4 are cited in the main text" 仍与主文实际引用（另引 Table 5、Table 14，L49）不符，且 M4 修复后该二分描述已无必要。

## C. 总分与推荐

- **总分：9.0/10**
- **推荐：accept（投稿就绪）**
- 一句话理由：上一轮 5 项投稿阻断级 Major 与 DOI 硬条件全部经 ground truth 验证关闭（其中 M5 为我方指控反转、修复方举证正确），残留仅为 5 条文字层 Minor，可在 proof 阶段一并处理，不影响投稿决策。
