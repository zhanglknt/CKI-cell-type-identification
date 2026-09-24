# NC v52 终审 — R3 肿瘤基因组学审稿（TCGA/癌症部分）

- 审稿人：R3-cancer（TCGA、肿瘤纯度/混杂校正、驱动分层、Cox 生存）
- 对象：commit 7133b43 工作树；MS `results/CKI_Manuscript_NC.docx`（fulltext 18:57）、SI `results/CKI_Supplementary_NC.docx`、附表 `results/CKI_Supplementary_Tables_NC.xlsx`
- 范围：ex-CC 队列、Cox 生存、severity/Edmondson、泛癌 map、GTEx field effect
- 方法：逐条对照输出文件 ground truth 复核稿面数字与措辞

## 一、上一轮 Major issues 处置核验（M1–M6 全部落实）

| 上轮问题 | 处置 | ground truth 核验 |
|---|---|---|
| M1 CC 细胞系入主分析 | **已修复**：ex-CC 为默认（"All TCGA results exclude 32 cell-line-derived aliquots"，MS line 47；3,535 样本 = 3,567−32） | `nc52_tcga_pancancer_excc.csv`：LIHC 366 肿瘤、TT 1,709 对；SI 3.13/5.12：34,828 对（35,306−478）✓；Cox/severity 均 ex-CC ✓ |
| M2 缺 GTEx 健康参照 | **已修复**：四器官三组 k_n；肺/肝/乳腺 GG≈NN（1.03–1.21）、TT/GG 2.0–2.7；肾例外（GG/NN 3.30、TT/GG 1.09 P=0.34，n=28） | `nc52_gtex_summary.json` ✓；SI Note 8 line 188 还披露跨队列 GA k_n 达肿瘤水平（P≤1.4×10⁻²⁶）并声明"mechanistic claims rest on within-cohort orderings only"——比我上轮要求的更严谨 ✓ |
| M3 组成校正 pooled 掩盖异质性 | **已修复**：Discussion line 75 明确"the pooled value masks heterogeneity: attenuation is strongest where the reversal is weakest (LIHC +44%, KIRC +20%)" | `nc52_tcga_composition_excc.txt`：LIHC +43.4% [+29.9%,+60.0%]、KIRC +19.5% [+14.5%,+25.3%]、pooled −0.8% [−4.3,+2.5] ✓ |
| M4 调整模型无置换对应 | **已修复**：whole-tumor 标签置换重拟合全 OLS（B=10,000）：KRAS-WT P≤0.001、EGFR-WT P≥0.28；并给 design effect 背景（intra-tumor ρ 0.31–0.42，design effect 2.5–4.0，证实上轮担忧量级） | `nc52_tcga_luad_adjmodel_permutation.csv` ✓；MS line 48、SI 3.13 line 135 均已引用 ✓ |
| M5 映射口径全表 | **已修复**：两口径五癌种全表；主文明确"only LIHC is mapping-sensitive (linear 1.11 [0.94,1.30] versus softmax 1.29 [1.09,1.53], the latter excluding 1 in all five)" | Supp Table 5 = `nc52_tcga_mapping_schemes_table.csv` ✓ |
| M6 HCC 机制引用张力 | **已修复**：Discussion line 75 明确"The hepatocellular literature motivating this reading 38 concerns the weakest-reversal cancer type, where the mechanism is least certain" ✓ |

上轮 minors 亦多处落实：Note 8 中位数口径差异已 reconciliation（line 185"the difference is the pair set, not the estimator"，对应旧 m2）；"high-purity-half... NN/TT ω ratios, not k_n fold-changes" 标签已修正（line 187，对应旧 m3）；Cox 改 R coxph + stage 分类变量 + zph 报告（对应旧 m7）；kn_floor 敏感性表（对应旧 m12）。

## 二、本轮权威口径逐项复核（全部通过）

1. **ex-CC 泛癌**：NN/TT = LUAD 2.464 [2.128,2.863]、KIRC 1.880 [1.638,2.148]、LUSC 1.708 [1.378,2.087]、BRCA 1.567 [1.342,1.815]、LIHC 1.112 [0.943,1.302] 跨 1 → "four of five"成立；k_n TT/NN 均值比 1.34–3.29 ✓（MS line 47 数字全部一致）。
2. **Cox ex-CC**（`nc52_lihc_cox_excc.csv`）：M1 z_omega HR/SD 1.081 [0.876,1.335] P=0.467 ✓（MS line 49、Table 14 一致）；M4 k_f 1.074 P=0.56（"k_f likewise null"✓）；zph M2 GLOBAL P=0.023 在 SI 5.12/3.13 照报 ✓；stage 分类（stage_f2/f3/f4）✓；n=272/79 ✓；含 CC 参照系并列存档（withCC_ref）✓。
3. **severity ex-CC**（`nc52_tcga_excc_severity.csv`）：Edmondson G1–G4 ω = 78.8/75.8/77.6/72.3（n=289：39+134+105+11 ✓），k_f JT P=8.4×10⁻¹² ✓；Note 9 与 Table 18 一致 ✓；Edmondson 勘误（372 患者/289 ex-CC 肿瘤）在 MS line 94、SI 5.3、5.12 三处一致 ✓。
4. **LUAD 调整模型置换**：KRAS-WT ω P = 0.0003–0.001（三模型）、k_f P = 0.019–0.044、k_n P = 0.010–0.018；EGFR-WT 全部 P≥0.28 ✓——摘要"both components survived purity and smoking adjustment"在置换推断下仍成立（k_f smoke_adj P=0.044，勉强过 0.05，名义水准，SI 已声明 post-hoc nominal）。
5. **GTEx**（`nc52_gtex_kn_by_grouptype.csv`）：与 MS line 50 / SI Note 8 line 188 数字一致（lung 1.14e-3/9.7e-4/2.50e-3；liver 1.98/1.92/3.98e-3；breast 9.1/8.7e-4/2.41e-3；kidney GG 2.38e-3≈TT 2.60e-3）✓；floor_frac ≤0.05% ✓。
6. **kn_floor 敏感性**（`nc52_tcga_knfloor_sensitivity.csv`）：floor ∈ {0, 1e-5, 1e-4} 下所有比值逐位相同 ✓（1e-3 时反转崩塌，但该 floor 会 cap 50–69% 的 NN 对，属不合理选择，非弱点）。

## 三、本轮发现的问题（条件清单）

### 必须修复（投稿前文本级）

**C1. MS Methods 残留 with-CC 旧口径（line 112）**
"Per-tumor statistics were derived from the linear-normalization pair table (**35,306 pairs: 2,000 TT and 2,000 TN seeded-subsampled pairs per cancer type** plus complete NN pairs)"——与 ex-CC 默认矛盾：SI 5.12/3.13 为 34,828 对、LIHC TT 为 1,709（`nc52_tcga_pancancer_excc.csv`）。同段未提及 whole-tumor 置换这一 v52 推断基准（摘要"survived adjustment"的依据）。【建议】改为"34,828 pairs after the barcode-audit exclusion (1,709 TT for LIHC)"，并加一句调整模型的置换推断说明。

**C2. SI 3.13（line 139）事实错误：CI 包含 1 的陈述已过时**
"TT k_n/NN k_n 1.34 [1.02, 1.89], **which includes 1**"——[1.022, 1.886] **排除** 1（`nc52_tcga_pancancer_excc.csv`）。该括注是 nc49 时代（[0.997,1.880]）的残留；且 ex-CC 后 LIHC k_n 升高现为名义显著，句子逻辑需重写（"keeps the LIHC null result unchanged"仅对 NN/TT ω 成立）。【建议】删"which includes 1"，并改写为"NN/TT ω CI 仍跨 1，而 TT/NN k_n 比 CI 在 ex-CC 后恰好排除 1"。

**C3. 去卷积 fallback 分析已执行但未入稿**
`nc52_tcga_deconv_feasibility.json` + `nc52_tcga_deconv_{lihc,kirc}_pertumor.csv`：单细胞参照非参数去卷积对 LIHC/KIRC 可行且已运行（split-half ρ 0.934/0.964；去卷积非实质分数 vs k_n ρ = 0.20 (P=1.2×10⁻⁴) / 0.26 (P=2.9×10⁻¹³)；vs ESTIMATE ρ = 0.59/0.24）。这正是上轮 M3 建议的"正式去卷积复核"，直接回应两个组成敏感癌种；但 MS/SI 全文仅三处"deconvolution-based validation remains necessary"，分析结果只字未提。【建议】在 Note 8 增一段报告（含其局限：LIHC stromal 参照仅 76 细胞、跨方法一致性中等），或明确说明不纳入的理由；现状是做了关键实验却隐身，评审视角等同于未做。

### 建议修复（措辞/精度）

**C4. MS Methods line 94 计数口径**：列出的 per-cancer 计数为排除前（LIHC 398；合计 3,567），括号内总数为排除后 3,535——同句自相矛盾。建议标"LIHC 398 (366 after CC exclusion)"或注明列出值为审计前。

**C5. Fig 4 图注（line 197）**："KRAS versus WT retained after purity and smoking adjustment, adjusted P = 0.009 and 0.029"——0.009/0.029 为 OLS 值；v52 推断基准为置换（k_f KRAS-WT P = 0.019–0.044 跨模型）。建议改为置换 P 或明确标注"OLS; permutation P = 0.019–0.044 (Section 3.13)"。

**C6. MS line 49**："the housekeeping floor (k_n ≥ 10⁻⁴) is never reached"——`nc52_tcga_knfloor_sensitivity.csv` 显示 KIRC NN 有 1/3,321 对（0.03%）触及 floor。建议改"essentially never (one KIRC NN pair)"。

**C7. 摘要 GTEx 句**："GTEx references argue against a field-effect reading"——肾例外未在摘要体现（主文有）。建议"in lung, liver, and breast, GTEx references argue against a field-effect reading (kidney unresolved)"。

### 观察项（不要求行动）

- ex-CC 后 Cox M1 中 grade_ord 由不显著（withCC P=0.43）变为显著（HR 1.45 [1.04,2.02]，P=0.030），k_f 模型由 P=0.067 变为 0.56——CC 排除实质改变临床模型系数，事后证明 ex-CC 默认的必要性；可在 SI 加一句（可选）。
- zph M2 GLOBAL P=0.023 由 stage 驱动（stage_f P=0.028），z_omega 项本身 PH 成立（P=0.113），且 ω null 在 M1–M3 全部稳健——已照报，可接受；如需更稳可做 RMST 敏感性（可选）。
- GTEx 肾皮质仅 n=28（GG 378 对）且自溶文献已知——已如实标注，结论限定恰当。

## 四、评分（0–10，NC 标准）

- **soundness: 8/10**——上轮全部六个 Major 的底层分析均已落实且经 ground truth 复核一致；推断基准（置换、cluster bootstrap、coxph+zph、两口径）现与摘要声明匹配。残留问题为文本一致性，非分析缺陷。
- **novelty: 6.5/10**——GTEx 第三组把"肿瘤特异性管家基线升高"从相对观察升级为有外部参照的主张；TCGA 章节作为方法演示与分母陷阱警示的定位清晰。
- **significance: 6.5/10**——对 bulk 转录组比较方法用户有实际警示价值；癌症生物学直接增量仍有限（KRAS 组织水平发散的探索性分层）。
- **presentation: 7.5/10**——披露与勘误（Edmondson 372/289、CC provenance、superseded 存档）达罕见水准；C1–C6 是投稿前必须清掉的数字/口径残留。
- **总评 overall: 7.2/10**

## 五、结论

**Verdict: accept after minor revisions（有条件接受 / 小修）**

放行条件：C1、C2、C3 必须处理（均为文本/报告层面，无需新分析；C3 若选择不纳入需一句理由）；C4–C7 建议同批修复。TCGA 章节在修复上述残留后可达到 NC 投稿状态。
