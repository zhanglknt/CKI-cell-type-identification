# CKI v35 同行评审报告（Expert 2：统计学 / 数据分析）

**稿件**：CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling（NAR，v35，2026-08-28 构建）
**审稿范围**：置换检验、FDR、AUC、数字一致性、校准、回归/相关、统计已知关注点
**审稿方式**：独立复核 `review_material/` 全部材料，并与 `results/` 下真实结果文件（phase35、phase32、brain_bs_null、tcga_bootstrap、mouse_pilot_v2b、phaseB/phaseC 系列）交叉核对

---

## 总体评价

**倾向：大修（Major Revision）。**

v35 的核心修订方向正确且大部分数值已在正文层面落实：block-shuffle null 重算的脑区结果（55 Strong、37 个 raw P<0.05、min q=0.949、0 个 FDR 显著）、human phase35 全量统计（n=4,851，mean 21.61/median 19.65）、AUC 表（0.680/0.690/0.801/0.849/0.887）、负相关 r=-0.36~-0.46、cross-organ r=-0.40~0.02、per-pair vs global-kn ρ=+0.181、kn CV=92.89%，均与我用原始 CSV 的独立复算**完全一致**，置换检验 MC 误差声明（0.016@P=0.5）数学上成立，SES 的非参数描述性定位恰当。

但存在**系统性问题**：v35 的修订没有贯穿全部材料——**正文/图注已更新到 block-shuffle/softmax 新数值，而补充材料（SN 3.2/3.3/3.5/3.7、Table S1/S4）与复现指南（Section 4.4/5.2/5.3/5.4、checklist、TABLE 1）仍大量保留 v5 旧方法与旧数值**，部分结论方向相反（如校准后的 Bergmann glia 从 ω_cal=0.36 变成 1.67、OPC 从"0 Strong"变成 27 Strong、per-pair vs global-kn 相关从 -0.027 变成 +0.181）。此外正文内部存在两处自相矛盾（Methods 中 FDR 检验数表述与 per-pair FDR；Limitation #17 与 Results 校准方案）。此类问题若不解决，复现性声明（"numerically identical results"）无法成立。

---

## Critical 问题

### C1. Methods「Statistical reporting」段与正文自己的 per-pair FDR 直接矛盾，且 BH 阈值数值错误
- **问题**：主稿 L41 写 "The number of tests is determined by the number of cell types (10 for brain, 17 for human per-cell-type, 15 for mouse), **not the number of region pairs**"；但主稿 L35（Methods, multiplicative residual model）明确 "Benjamini-Hochberg FDR correction was applied across all **m = 31,764** pairs"，Results L80 也报告 per-pair q（min q=0.949）。同一稿件内对脑区多重检验的定义互相矛盾。L41 的 "brain: 1.0 × 10⁻³, at the resolution limit" 亦错误：按该段自身的 m=10，BH 阈值应为 0.05/10 = **5.0×10⁻³** 而非 1.0×10⁻³（1.0×10⁻³ 恰等于最小可分辨 P≈9.99×10⁻⁴，疑似把"分辨率下限"误写成"BH 阈值"）。该段整体是 v5 遗留文案。
- **位置**：`CKI_NAR_Manuscript_full_extract.txt` L41（Statistical reporting）；对照 L35、L80
- **建议**：重写 Statistical reporting 段：区分（i）脑区 **per-pair** BH-FDR（m=31,764，B=1,000，min q=0.949）与（ii）cell-class 水平检验（10 类）、human per-CT（17）、mouse pilot（15）、TCGA（5 癌种）的组级检验，分别说明检验数依据与 B 的分辨率含义。删除或更正 "not the number of region pairs" 与 "brain: 1.0×10⁻³"。

### C2. 补充材料 SN 3.3 与复现指南 5.3c 仍是 v5 旧统计方法/旧结果，与正文 block-shuffle 结果矛盾
- **问题**：补充 L62–63（SN 3.3）与复现指南 L166（5.3c）描述的是**旧版 per-signal 细胞标签 shuffle（B=10,000）**：30 个 Strong 候选、36.3%（11,541/31,764）落在 P 下限、16/30（6 astro + 10 oligo）达下限、14 个 P≥0.76、"precluding meaningful BH-FDR correction"。正文（L35、L80–87）则报告 **block-shuffle null（B=1,000，以 10x library 为块）**：55 Strong、37/55 raw P<0.05、per-pair BH-FDR（m=31,764）min q=0.949、0 个显著，且已明确说明 per-signal shuffle 是"anti-conservative"的旧实现。补充/复现指南仍在教读者复现已废弃的方法与结论。
- **位置**：`CKI_NAR_Supplementary_full_extract.txt` L62–63；`CKI_NAR_Reproducibility_Guide_full_extract.txt` L166（5.3c，引用 `phaseB_residual_pervisign.csv`）
- **建议**：SN 3.3 全文重写为 block-shuffle 版本（B=1,000、55/37/min q=0.949），并说明与旧 per-signal shuffle 的差异及弃用理由；复现指南 5.3c 同步更新并指向新输出文件。

### C3. 补充 SN 3.7 与复现指南 5.4c / checklist / TABLE 1 中的 k_n 变异性仍是旧值（CV=97.35%、ρ=−0.027），与正文/图 S11 的新值（92.89%、+0.181）矛盾
- **问题**：正文 L56 与图 S11（主稿 L129）报告 per-pair k_n CV=**92.89%**、per-pair vs global-kn Spearman ρ=**0.181**（P=9.38e-232）。我复核 `results/phaseC_kn_variability.json`：kn CV=0.9289 ✓；`phaseC_omega_pair_vs_global.csv` 复算 ρ=0.1809 ✓。但补充 L71（SN 3.7）与复现指南 L180（5.4c）、L259（checklist）仍写 CV=**97.35%**（mean=0.0141, median=0.0086）、ρ=**−0.027**（P=9.96e-7），并据此得出 "per-pair vs global-kn yields substantially different rankings" 的旧结论。新旧不仅数值不同，**符号相反**，说明该相关对实现（softmax 重跑）高度敏感，必须统一。另：补充 SN 3.7 的 per-cell-type CV 范围 "37.6%–81.4%" 与现数据（json 中 36.5%–69.8%）不符。
- **位置**：`CKI_NAR_Supplementary_full_extract.txt` L71；`CKI_NAR_Reproducibility_Guide_full_extract.txt` L180、L259；对照主稿 L56、L129
- **建议**：三处材料统一为 92.89% / +0.181；补报新 mean/median；并建议在正文中承认该相关从 −0.027 变为 +0.181 的敏感性（两个方向都表明 per-pair 与 global-kn 排名几乎正交，0.181 仅解释约 3.3% 方差，应如实陈述）。

### C4. 补充 SN 3.5 的校准后脑区数值为旧版，且结论方向与正文相反
- **问题**：补充 L67（SN 3.5）写 "brain global mean becomes ω_cal = 1.20 (raw 8.01)，astrocytes ω_cal = 2.15 (raw 14.36)，Bergmann glia ω_cal = 0.36 (raw 2.37)"；正文 L54 写 "brain global mean becomes ω_cal = 4.88 (raw 32.56)，astrocytes ω_cal = 11.52 (raw 76.83)，Bergmann glia ω_cal = 1.67 (raw 11.17)"。两组数值分别自洽（均为 raw/6.67），但**结论方向相反**：旧版 Bergmann glia ω_cal<1（"比经验基线更受约束"），新版 ω_cal>1（"所有类均在基线之上"）。读者按补充材料会得到与正文相反的生物学结论。复现指南 L135（Section 4.4）的 mu_grand=8.01 同样是旧值（正文为 32.56）；`results/phaseC_calibration.json`（复现指南 5.4a 引用的输出）中 brain 仍为 raw mean 47.74、ω_cal 7.16。
- **位置**：`CKI_NAR_Supplementary_full_extract.txt` L67；`CKI_NAR_Reproducibility_Guide_full_extract.txt` L135、L174（5.4a）；对照主稿 L54
- **建议**：SN 3.5 与复现指南全部改用 32.56/76.83/11.17 及相应 ω_cal；重新生成 phaseC 校准输出；明确 "brain global mean" 指 31,764 对的全对均值。

### C5. 脑区原始数据文件指向旧版 v3 文件，且投稿包中无任何代码/数据文件，与 Data availability 声明不符
- **问题**：（i）补充 Tab3（L94）与复现指南 Section 6（L212）声明脑区原始数据为 `results/brain_siletti_omega_pairs_v3.csv`（31,764 rows）。但该文件是旧数据：我复核其 grand mean=47.74、Astrocyte=103.08，与正文（32.56、76.83，位于 `results/brain_bs_null_observed_pairs.csv`）完全不同。（ii）主稿 L100 Data availability 声明 "All analysis notebooks and processed data matrices are included in the Supplementary Data"，但 v35 投稿包 `version3/CKI_NAR_Submission_v35/` 中只有 DOCX/PDF/图表/Table1-2，**没有任何代码或数据文件**。（iii）复现指南 5.2（L155）引用 `brain_bootstrap_results.csv` 作为脑区 FDR 结果，但该文件是旧的 cell-type-level bootstrap（Astrocyte SES=321.8 等，与正文 cell-class SES 4.8–15.8 不符）。
- **位置**：`CKI_NAR_Supplementary_full_extract.txt` L94；`CKI_NAR_Reproducibility_Guide_full_extract.txt` L155、L212；主稿 L100；投稿包目录
- **建议**：脑区数据声明改为 v35 实际使用的文件（并随稿提供）；Data availability 改为真实可获取的仓库/数据链接，或将代码与数据矩阵实际纳入补充材料（如 Zenodo）；复现指南 5.2 引用文件更新为 v35 分析输出。

---

## Major 问题

### M1. 校准 CI [4.12, 9.33] 无法由现有数据复现，且统计量（mean 或 median）未澄清
- **问题**：审稿重点要求核查 ω=6.67（n=6，CV≈52%）的 bootstrap CI。我以 `mouse_pilot_v2b_results.csv` 的 6 个 control 值 [12.16, 6.57, 6.34, 5.22, 8.15, 1.59] 重采样 B=10,000（seed 42）：**mean 重采样 CI=[4.20, 9.29]，median 重采样 CI=[3.41, 10.15]**；`phaseB_bootstrap_cis.csv` 记录 [4.24, 9.24]；正文/摘要/复现指南写 [4.12, 9.33]。四个版本不一致。补充 SN 3.2（L60）规定 CI 用 pair-level resampling 的 **median**，若按 median，CI 应为 [3.41, 10.15] 而非 [4.12, 9.33]，即**正文 CI 与补充规定方法不匹配**。n=6 的 bootstrap 本身作为"重采样精度"可接受（正文已声明非经典 CI），但边界不可复现。
- **位置**：主稿 L11（摘要）、L42、L89；补充 L60；复现指南 L174；`phaseB_bootstrap_cis.csv`
- **建议**：明确校准 CI 的重采样统计量（mean/median）、B 与 seed，或直接给出可复现脚本；统一全文 CI 值；并补充一句说明 n=6 下 bootstrap CI 覆盖率本身受限。

### M2. Limitation #17 与 Results 对校准方案（k_f 基因选择）的自相矛盾
- **问题**：主稿 L96（Limitation #17）称校准基线 "was derived from mouse split-half controls **using a global HVG set for k_f**, but is applied to human, TCGA, and brain analyses that use **per-pair DE gene selection**"，据此推断校准因子"低估"per-pair 基线通胀。但主稿 L51（Results）明确 "For the pilot calibration (controls, S/D/X categories), we used a hybrid scheme: global k_n ... with **per-pair k_f (top-200 differentially expressed genes)**"，复现指南 4.1（L85–86）同样写 pilot 用 per-pair top-200 DE。**两处对同一 6.67 的基因方案描述相反**。若校准实际用的是 per-pair DE（与 human/TCGA 同方案），则 #17 关于"外推/低估"的前提不成立，整个段落需重写；若确为 global HVG，则 Results L51 错误。
- **位置**：主稿 L51 vs L96；复现指南 L85–86
- **建议**：核对脚本确认 6.67 的确切 k_f 方案，然后统一两处；若为 per-pair DE，则把 Limitation #17 改为"校准与 per-pair 方案同源，外推主要风险在于跨数据集 k_n 尺度（见 TCGA floor 讨论）而非 k_f 方案"。

### M3. AUC 分类任务的非独立性未被讨论；CKI 0.680 vs Spearman 0.690 无差异检验
- **问题**：4,851 对分类任务中 positive（same-cell-type cross-organ）仅 **59 对**，由 17 个细胞类型构成且严重重复（macrophage 15 对、NK 10 对、CD8+ T 6 对等），同一细胞类型的多对高度相关，违背独立观测假设；AUC 0.680 的精度被高估。CKI 0.680 与 Spearman 0.690 仅差 0.010，正文（L60）直接作出 "ranked 5th of 5" 并给出"设计使然"的因果解释，但**未提供任何差异检验或 CI**。我按 `phase35_all_metrics_pairs.csv` 复算五方法 AUC 与 Table 1 完全一致（0.680/0.690/0.801/0.849/0.887），但一致性不代表 0.010 的差距有意义。
- **位置**：主稿 L33（Methods）、L60（Results）、Table 1
- **建议**：以细胞类型为聚类单元做 bootstrap（如 block bootstrap by cell type）给出五方法 AUC 的 95% CI，明确说明 CKI 与 Spearman 差异无统计学证据；并补充"同一细胞类型在多对中重复出现导致观测非独立"的限制说明。

### M4. "mouse (mean 27.31)" 比较基准未注明来源，且为 n=2 的类别均值
- **问题**：主稿 L57 "Human ω values ... substantively lower than mouse (mean 27.31)"。`mouse_pilot_v2b_key_values.csv` 显示 27.31 是 mouse pilot **X 类别（cross-organ）均值，n=2**；human 比较用的是 4,851 对全均值（mean 21.61）。用 n=2 的类别均值作为"mouse 代表值"与 human 全量对均值比较，统计上不成立；正文虽随后解释了 k_f 方案差异，但未披露 27.31 的样本量。指南关注点 #6 确认存在。
- **位置**：主稿 L57；`mouse_pilot_v2b_key_values.csv`
- **建议**：明确标注 "mouse X-category mean（n=2）"，或改用 mouse pilot 15 对总体均值（≈20.6）做跨物种量级比较，并弱化"substantively lower"的措辞。

### M5. 补充 SN 1.3 与 Table S1 的参数扫描 AUC=0.847 与正文/图 S1 的 0.786 矛盾
- **问题**：补充 L20（SN 1.3）与 L90（Table S1）写 identity-only 配置 "AUC = 0.847"；正文 L49 与图 S1 图注（L119）写 "AUC = 0.786"。`phase32_sweep_results.csv` 实测 identity_only AUC=**0.7855**（正文正确，补充为旧值）。
- **位置**：补充 L20、L90；主稿 L49、L119
- **建议**：补充两处改为 0.786。

### M6. 补充 SN 3.2 的 bootstrap CI 示例与任何现存数据不符（三层数值不一致）
- **问题**：补充 L60 称 "astrocytes (5,778 pairs) yield narrow intervals ([14.14, 14.58])，Bergmann glia (21 pairs) ... ([1.95, 2.90])"。这三个数值对应 v5 旧脑区均值（astro 14.36、Bergmann 2.37），与 `phaseB_bootstrap_cis.csv`（astro [101.6, 104.5]，亦旧）和正文（astro 76.83）均不同。补充例子的 CI 与正文数据完全脱节。
- **位置**：补充 L60；`phaseB_bootstrap_cis.csv`
- **建议**：按 v35 数据重算并更新示例 CI（如 astro 76.83 的 CI），并统一复现指南 5.3b 引用的 `phaseB_bootstrap_cis.csv` 输出。

### M7. 补充 Table S4 内部计数矛盾且 Top-5 候选为旧数据
- **问题**：补充 L96 称总迁移候选 7,943 对（25.0%），但同段给出的 Strong 55 + Moderate 2,120 + Weak 6,149 = **8,324 对**，且 8,324/31,764=26.2% ≠ 25.0%。我按 `brain_bs_null_results.csv` 复核 tier 计数：55/2,120/6,149 ✓（与正文一致），故 7,943 为旧值/笔误。另 Table S4 的 Top-5 候选（Microglia A14–Pul 等，omega 10.29/9.44/12.95/13.15/7.47）与新数据不符——实际 Top-5（按 residual）为 Oligo A40–SEP (0.197)、COP PnRF–SN-RN (0.206)、Astro A19–AON (0.214) 等。
- **位置**：补充 L96；`brain_bs_null_results.csv`
- **建议**：Table S4 全表按 v35 数据更新，修正候选总数与 Top-5。

### M8. 脑区 per-pair FDR 在 B=1,000 下数学上不可能出现显著结果，应显式声明
- **问题**：m=31,764 时 BH 阈值（对最小 P）为 0.05/31,764≈**1.57×10⁻⁶**，而 B=1,000 的最小可分辨 P=9.99×10⁻⁴，两者相差约 600 倍。因此 "no pair reached q<0.05" 在 B=1,000 下是**必然结果**，几乎不携带数据信息（min q=0.949 本身由 P floor 与 rank 决定）。正文 L80 将其作为实质结论叙述（"none reached q<0.05 ... hypothesis-generating"），虽 Limitation #19 已提及需要更大 B，但 Results/Methods 的语气未提示读者该 null 结果是 B 的函数。
- **位置**：主稿 L35、L80–87、L96（Limitation #19）
- **建议**：在 Methods/Results 增加一句显式说明：在 m=31,764 与 B=1,000 下 q<0.05 在数学上不可达，需 B≳6×10⁵ 方能分辨 BH 阈值；per-pair FDR 的意义应定位为"在当前分辨率下无信号"，并与 raw P 分布（938/31,764 < 0.05，低于全局 null 期望 1,588）一并呈现。

---

## Minor 问题

1. **图 S7(B) 图注与正文直接矛盾**（指南关注点 #2）：主稿 L125 写 "OPCs (0 Strong despite highest motility among the 10 non-neuronal classes)"，正文 L80 写 "OPCs contributed 27 Strong candidates"。数据核实 OPC=27（`brain_bs_null_results.csv`），图注为 v5 旧文案，必须修改。
2. **图 2B 图注 "S (same sub-organ)" 与正文 "S (same cell type across different organs)" 矛盾**（指南关注点 #1）：主稿 L113 vs L53。mouse pilot 的 S 类别为 same-CT cross-organ（n=4，mean 21.31），图注定义错误。
3. **摘要 "millions of cells" 不精确**（指南关注点 #7）：主稿 L11 摘要 vs L72（atlas ~3.3M，实际分析 888,263 非神经元核，过滤后 886,808）。建议改为 "from a human brain single-nucleus atlas (888,263 non-neuronal nuclei)"。
4. **BH-FDR 引用错配**（指南关注点 #3）：主稿 L41 "Benjamini-Hochberg FDR correction ... (23)"，ref 23 是 Storey & Tibshirani 2003（q-value 方法）；实现（`benjamini_hochberg()`）是 BH 1995。应改引 Benjamini & Hochberg 1995（JRSS B）；或若实际采用 Storey 程序，需改方法描述与 "q-value" 术语。
5. **human pair 数不一致**：正文/图/Table 1 为 4,851（实测 `phase35_all_metrics_pairs.csv` 4,851 对 ✓），补充 L62 与复现指南 L101 写 5,151（C(102,2) 全量）。需统一并说明 300 对差异的过滤依据。
6. **normality 检验 P 值不一致**：补充 SN 3.4（L65）写 "all P < 0.001"，正文 L42 写 "all P < 10⁻¹⁵"。统一。
7. **图 3E 图注**（L114）"CKI ω has lower AUC than cosine and raw JS divergence" 不完整——CKI 0.680 是五方法中最低（低于所有四方法），图注有误导。
8. **摘要 "Cancer analysis revealed transcriptional convergence"** 语气强于正文（L63–65 明确 exploratory），建议摘要措辞与正文 caveat 一致。
9. **mouse "k_n increased only about 100-fold"**（L53）：实测 control→X kn 增约 119 倍、→D 约 73 倍，"about 100-fold"偏宽；k_f "roughly 400-fold"（实测 420 倍）可接受。建议给出区间。
10. **mouse pilot S/D/X 小样本（n=2–4）未标不确定性**（L53）：21.31/43.19/27.31 均无 CI；`phaseB_bootstrap_cis.csv` 中 S CI=[11.4, 35.7]、D CI=[30.1, 61.7]，宽度极大，正文宜注明。
11. **复现指南 5.2 引用文件与 v35 分析不符**（L155）：所引 `brain_bootstrap_results.csv` 为旧 cell-type-level bootstrap（SES 高达 321.8，null 基于 per-cell shuffle），与正文 cell-class block-shuffle 检验（SES 4.8–15.8，`brain_bs_null_ct_test.csv`）不一致；应改引后者并更新说明。
12. **skewness 来源未注明**（L42）：正文报 mouse skewness=0.98，我按 mouse pilot 15 对实测 0.89（703 对 full matrix 或为 0.98），需注明 mouse 指哪个数据集；`phaseB_omega_distribution.json` 中 brain skewness 2.30 为旧数据，与正文 2.10（实测 bs_null 数据 2.10 ✓）不符。
13. **human_bootstrap_results.csv 与 per-CT bootstrap 并存且方法不同**（复现指南 L217–218）：4 行 group-level 与 17 行 per-CT 结果均被引用，但正文未报告任一结果，需说明两者的用途与对应关系。
14. **BH "q-value" 术语混用**：复现指南 5.2 用 "q-value" 指 BH adjusted P（L155），补充 SN 3.3 亦用 "precluding meaningful Benjamini-Hochberg FDR correction" 描述 Storey 概念；建议统一术语（adjusted P 或 FDR-adjusted）。

---

## 已妥善解决的上一轮项（可确认项）

1. **脑区 block-shuffle null 重算**：per-pair 单侧置换 + BH-FDR（m=31,764），0 个 q<0.05（min q=0.949）、Strong 55（37 raw P<0.05）——与 `brain_bs_null_summary.txt`、`brain_bs_null_results.csv` 逐项一致；OPC 27/55 亦核实（指南 C1/OPC 叙事更新落实）。
2. **human phase35 重跑**：n=4,851（实测文件行数一致）、ω mean 21.61 / median 19.65 / range 1.35–87.69 全部复现；same-CT cross-organ 15.83（n=59）、diff-CT same-organ 24.87（n=1,038）、diff-CT diff-organ 20.80（n=3,754）复现一致。
3. **Table 1 AUC 与正文/图一致**：五方法 AUC 0.680/0.690/0.801/0.849/0.887 复算完全吻合；Table 2 17 类 cross-organ 均值/SD/n 与 `phase35_cross_organ_summary.csv` 完全一致。
4. **CKI 与四标准度量负相关 r=−0.36~−0.46**：实测 −0.358（Jaccard）～−0.461（Spearman）一致；标准度量正相关簇 0.57–0.93（实测 0.569–0.935）一致。
5. **cross-organ 排名一致性 r=−0.40~0.02**：pair-level（59 对）复算为 −0.40/−0.21/−0.13/+0.02，与正文范围吻合。
6. **per-pair vs global-kn Spearman +0.181**：实测 0.1809（n=31,764）一致；正文对"per-pair k_n 必要性"的解释合理（但建议补充仅解释 ~3% 方差）。
7. **kn CV=92.89%**：`phaseC_kn_variability.json` 实测 0.9289 一致。
8. **校准描述**：ω=6.67（n=6，median 6.46，range 1.59–12.16，CV≈52%）、6 个 control 均 P>0.05（0.31–0.99）全部复现；摘要/正文/补充关于 6.67 本身的陈述一致。
9. **TCGA kn floor**：5 癌种 aggregate TN kn=3.0e-5–1.9e-4，LUAD/KIRC/BRCA 3/5 触及 floor 1e-4，与 `tcga_bootstrap_results.csv` 一致；TCGA BH q 值亦复算吻合（min q 逻辑一致）。
10. **脑区 per-class 统计**：10 类 mean（11.17–76.83）、n、6.88 倍梯度、cell-class block-shuffle P（9/10 为 9.99e-4）、Bergmann glia P=0.031/SES=2.0、Choroid P=0.76 与 `brain_bs_null_ct_test.csv` 完全一致。
11. **置换检验方法与 MC 误差**：P=(count+1)/(B+1) 为标准单侧置换公式；B=1,000 时 MC SE（P=0.5 时 ≈0.016；P=0.001 时 ≈0.001）数学上成立；SES 定位为非参数描述统计量的声明恰当。
12. **per-pair FDR 依赖结构**：正文 Limitation #16 已明确承认 per-signal 检验共享 cell types/regions、BH 为近似（并建议分层/置换 FDR 细化），处理得当。
