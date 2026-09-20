# Expert 1 审稿报告：方法学 / 计算生物学

**稿件**：CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling  
**目标期刊**：Nucleic Acids Research (NAR)  
**版本**：v35（2026-08-28 构建，softmax 归一化全尺度统一修订版）  
**审稿人**：方法学 / 计算生物学  
**日期**：2026-08-28  
**核查方式**：精读主稿件全文（207 行）、补充材料、复现指南、参数表；逐项核对 `cki/core.py`（v0.3.2）、`cki/utils.py`、`notebooks/08d_brain_blockshuffle_null.py`、`notebooks/08e_brain_blockshuffle_results.py`、`notebooks/13_phase35_method_comparison.py`、`notebooks/_compute_phase35_auc.py`、`notebooks/precompute_figure_data.py`；Python 独立重算 softmax 等价性、pair count、BH-FDR 可行性等关键数字。

---

## 总体评价

**建议：大修（Major Revision）。**

CKI 的概念内核——将 HK 基因散度作为内参基线、对功能基因散度做归一化——具有方法学创新性。v35 相对 v5 确有实质改进：softmax 统一后 base-2 log JS 声明与代码一致（`cki/core.py` line 47 使用 `np.log2`），block-shuffle null 的设计逻辑正确（10x library 为 block、置换 library→region 分配、保留 per-region library 计数多重集），per-pair k_f 的循环依赖（data snooping）在 Limitations 中如实披露，且 null 中每轮置换重做基因选择保证内部自洽。方法比较的负相关发现与 AUC 数值可从 `results/phase35_*` 文件复算验证。

但当前版本存在 **6 项 Critical 问题**，涉及代码-稿件一致性失败、结构性统计功效缺陷、占位数据混入正文图、以及补充材料与正文叙事方向性矛盾。这些问题虽严重但均可修复，不需要推翻方法本身。

---

## Critical 问题

### C1. block-shuffle null 的 B=1,000 与 m=31,764 组合使 BH-FDR 显著在数学上不可能发生；Methods 对 B 值充分性的声明与正文结果自相矛盾

**位置**：Methods Statistical reporting（主稿件 line 41）与 Methods Multiplicative residual model（line 35）。

**核查**（Python 独立重算）：
- per-pair P 的分辨下限 = 1/(B+1) = 1/1001 ≈ 9.99×10⁻⁴。
- 对 m=31,764 做 BH-FDR，要使最小 rank 的 q<0.05，需 P ≤ 0.05×(1/31,764) ≈ 1.57×10⁻⁶。
- 9.99×10⁻⁴ >> 1.57×10⁻⁶：**无论生物学信号多强，在 B=1,000 + m=31,764 的设计下，没有任何 pair 能达到 q<0.05**。实际 min q=0.949 与此计算吻合。
- 相比之下，cell-type 级检验（m=10）的 BH 阈值 = 0.05/10 = 0.005 > 0.001，B=1,000 确实足够。

**矛盾**：
- line 41 声称 *"The number of tests is determined by the number of cell types (10 for brain...), not the number of region pairs... confirming that B = 1,000 provides sufficient resolution for all tests."*
- 但 line 35 明确写 per-pair BH-FDR *"across all m = 31,764 pairs"*，min q=0.949。
- 两处对检验数的描述直接矛盾（已知关注点 #5 属实）：一处理论上只做 10 个 cell-type 级检验，另一处实际做了 31,764 个 per-pair 检验。

**影响**：(i) "no candidate survived FDR correction" 在该设计下是**结构性必然**而非实证发现；Abstract 以此作为结果陈述但未注明结构性约束，有误导性。(ii) Limitation 19（line 97）虽承认需更大 B 或层级模型，但与 Methods 的"sufficient resolution"说法直接冲突。

**建议**：
1. 明确区分两类检验：(a) cell-class 级检验（m=10，B=1,000 足够）；(b) per-pair migration screen（m=31,764，B=1,000 结构性不可达 FDR 显著）。
2. 对 per-pair screen，或提高 B 至 ≥2×10⁵（使 min P ≈ 5×10⁻⁶，可在 BH 下达标），或改用按 cell type 分层的层级 FDR 并报告功效约束。
3. Abstract 中对"no candidate survived FDR"加结构性说明（"under a permutation design where FDR significance is structurally precluded at B=1,000"）。

### C2. Figure 2D 通路富集数据为硬编码占位数值，非真实分析结果

**位置**：主稿件 line 113（Figure 2D legend）：*"Pathway enrichment in the k_f component, showing fold change (k_f/k_n) for top enriched pathways. Stars indicate significance: *** P < 0.001, ** P < 0.01, * P < 0.05."*

**核查**：`notebooks/precompute_figure_data.py` line 144–158 在找不到 gene-level k_f 文件（`phase35_gene_level_kf.csv` 等，均不存在于 `results/`）时回退到**硬编码的 8 条"canonical pathway data"**：

```python
pathways_data = [
    ("Oxidative phosphorylation",  4.2, 1e-12),
    ("Protein folding",            3.1, 1e-8),
    ("Immune response",            5.8, 1e-15),
    ("Cell adhesion",              3.4, 1e-9),
    ("Signaling",                  2.9, 1e-6),
    ("Metabolism",                 2.1, 1e-4),
    ("Transcription",              3.7, 1e-10),
    ("Cell cycle",                 2.5, 1e-5),
]
```

这些值带有显著性星号出现在正式投稿图中，但完全是占位数据，非 gseapy/Enrichr 的真实富集结果。`ENRICHMENT_SUCCESS` 标志必为 False（gene_level_csv 不存在 → gseapy 从未执行）。

**影响**：数据完整性问题。带 P 值和星号的通路富集统计是虚构的。

**建议**：(i) 删除回退分支，从真实 gene-level k_f 结果重跑 gseapy/Enrichr 富集并重制 Figure 2D；(ii) 审计其他 figure-data 脚本是否存在同类硬编码回退。

### C3. 补充图 S7(B) 图注与正文核心叙事直接矛盾（OPC 0 Strong vs 27 Strong）

**位置**：
- 主稿件 line 125（Supplementary Figure S7(B) legend）：*"OPCs (0 Strong despite highest motility among the 10 non-neuronal classes) provide a key internal consistency check, supporting that the model detects developmental-origin signatures rather than general motility."*
- 正文 line 80–82：*"OPCs contributed the largest share of Strong candidates (27 of 55, of which 16 had raw block-shuffle P < 0.05)—roughly 2.7-fold more than expected from their share of comparisons (17.9% of pairs)."*

**核查**：v35 的 `results/brain_bs_null_results.csv` 中 Strong=55、OPC=27（与正文一致）。S7(B) 图注的"OPC 0 Strong"来自 v5 旧分析管线（per-pair shuffle，44 Strong 中 OPC=0、microglia=17）。

**影响**：这不是笔误，而是两条**互斥的生物学结论**同时存在于投稿包中：图注说"模型检测的是发育起源信号而非运动性"，正文说"候选集中与 OPC 运动性一致"。若 S7 图本身也是旧图，则图与正文数据不符。已知关注点 #2 属实且比预想更严重。

**建议**：以 block-shuffle 结果为准，重写 S7(B) 图注并重新核对该图是否由当前数据生成；删除"internal consistency check"旧叙事。

### C4. k_n floor（1e-4）在 Methods/SN/参数表中声明但全部分析脚本均未实现

**位置**：
- SN 1.1 / Algorithm 2 line 36：*"if k_n < 1e-4: k_n ← 1e-4"*。
- 复现指南参数表：*"k_n floor (minimum) | 1e-4 | all analyses"*。
- `cki/core.py` line 242–244：确有 clamp（`kn_min = 1e-4; if kn < kn_min: omega = kf / kn_min`）。

**核查**（逐脚本比对）：
| 脚本 | 实际阈值 | 位置 |
|---|---|---|
| `08d_brain_blockshuffle_null.py` | `kn > 1e-15` | line 146 |
| `13_phase35_method_comparison.py` | `kn > 0` | line 210 |
| `_compute_phase35_auc.py` | `kn > 1e-12` | line 154 |
| `08e_brain_blockshuffle_results.py` | 不涉及 omega 计算（仅处理 null 矩阵） | — |

所有产出投稿数值的脚本都绕过了 `core.py` 的 `compute_omega` 函数，自行实现 `kf/kn` 比值，使用了不同的数值保护阈值。

**影响**：(i) Methods 声明的 floor=1e-4 在实际分析中未生效，影响 TCGA 饱和分析的可信度（TCGA kn 最小值 3.0×10⁻⁵ ~ 1.9×10⁻⁴，3/5 癌种触底——但这是否在脚本中实际 clamp 未知）。(ii) 脑区 kn 最小值约 7.7×10⁻⁵（`phaseC_kn_variability.json`），个别 pair 受 floor 影响但脚本未 clamp。(iii) 复现者按 Methods 描述无法复现数值。

**建议**：统一 floor 行为——在 08d/13 等脚本中调用 `core.compute_omega` 或显式实现 `max(kn, 1e-4)` clamp，并报告受影响 pair 数；或修正 Methods 说明 floor 仅在包 API 中生效而分析脚本未使用。

### C5. Methods 对 k_n 计算方式的描述（"global k_n，全数据集常数"）与所有代码的实现不符

**位置**：
- SN 3.7（line 71）：*"In the hybrid scheme used for human and TCGA analyses, k_n is computed once globally (constant across all pairs), which reduces omega to a scaled k_f ranking."*
- 正文 line 56：*"k_n was computed once globally (using the full gene-by-cell-type pseudobulk matrix with the shared HK gene set)."*
- 复现指南 §4.2（line 99）：*"Global k_n: JS divergence on full pseudobulk matrix with shared HK set."*

**核查**：所有相关脚本均**逐对计算** k_n（即对每对 pseudobulk A/B 算 `js_divergence(pb_A[HK], pb_B[HK])`）：
- `13_phase35_method_comparison.py` line 197–199：`kn_val = float(js_divergence(hk_i, hk_j))` ← 产出 4,851 对人类 omega 值（mean 21.61 等正文数值即由此产生）。
- `_compute_phase35_auc.py` line 140–142：同样逐对计算。
- `08d_brain_blockshuffle_null.py` line 138：`kn = js_divergence(pi[hk_idx], pj[hk_idx])` ← 逐对。

**影响**：(i) 方法描述失实——"global k_n"在代码中不存在；所有数据集（包括人类/TCGA）均使用 per-pair k_n。(ii) 论文将"脑区用 per-pair k_n 而人类用 global k_n"作为重要方法学区分（正文 line 56：*"For the brain analysis, k_n was computed per-pair (not globally), because regional comparisons within the same cell type demand pair-specific baselines"*），但代码中该区分不存在——所有数据集的 k_n 都是 per-pair 的。(iii) SN 3.7 的核心论证（"omega 退化为 k_f 的缩放排序"）建立在错误前提上。(iv) 复现者按文中描述（常数 k_n）无法复现任何人类数值。

**建议**：改写 Methods / SN 3.7 / 复现指南 §4.2，如实描述"所有分析中 k_n 均逐对计算于共享 HK 基因集"；删除"omega 退化为 k_f 的缩放排序"的错误推论；重新表述 per-pair k_n 变异分析（CV=92.89%、ρ=0.181）的动机——它适用于所有数据集而不仅是脑区。

### C6. BH-FDR 引用错配：ref 23 为 Storey & Tibshirani 2003（q-value 法），非 Benjamini & Hochberg 1995

**位置**：
- Methods line 26 & 41：*"Benjamini-Hochberg false discovery rate (FDR) correction is applied within each dataset (23)."*
- 参考文献列表 line 155：*"Storey,J.D. and Tibshirani,R. (2003) Statistical significance for genomewide studies. Proc. Natl. Acad. Sci. USA, 100, 9440–9445."*

**核查**：Storey & Tibshirani 2003 描述的是 q-value 方法（基于 pFDR 的正假发现率估计），与 Benjamini & Hochberg 1995（BH-FDR）是不同的 FDR 方法。BH 1995 原始文献（Benjamini, Y. & Hochberg, Y. (1995). J. Royal Stat. Soc. B, 57, 289–300）不在参考文献列表中。已知关注点 #3 属实。

**影响**：方法学引用错误，影响可重复性——读者若查 ref 23 会看到不同的 FDR 程序。`cki/bootstrap.py:benjamini_hochberg()` 和 `08e_brain_blockshuffle_results.py:bh_fdr()` 实现的是标准 BH 步进式校正（非 Storey q-value），故代码正确但引用错误。

**建议**：补引 Benjamini & Hochberg 1995 并替换 ref 23 的引用位置；若同时引用 q-value 方法，另编号并在正文中区分两者。

---

## Major 问题

### M1. 脑区分析存在两条并行管线，投稿包混合 reporting 两套结果

**位置与证据**：
- **正文脑区数值来自 block-shuffle 管线（08d）**：grand mean 32.56、astrocyte 76.83、Bergmann 11.17、6.88-fold gradient、55 Strong——与 `results/brain_bs_null_observed_pairs.csv` / `brain_bs_null_ct_test.csv` 完全一致（已复算）。
- **补充材料与复现指南数值来自更旧管线（07c）**：
  - SN 3.3（line 62–63）描述已被否决的 per-pair shuffle（B=10,000、30 Strong、16 个触底、36.3% floor 饱和）。
  - SN 3.5（line 67）：ω_cal=1.20/2.15/0.36（raw 8.01/14.36/2.37）——与正文 4.88/11.52/1.67（raw 32.56/76.83/11.17）矛盾。
  - SN 3.7（line 71）：CV=97.35%、ρ=−0.027——与正文 CV=92.89%、ρ=0.181 矛盾。
  - 复现指南 §4.4（line 135）：μ_grand=8.01——与正文 32.56 矛盾。
  - Supplementary Table 4 的 top-5 候选（microglia A14-Pul ω=10.29, residual=0.194 等）为 07c 结果，但正文 v35 候选中 microglia 为 0。
- **未披露的参数差异**：`08d` line 166 设 `N_HVG=5000`，k_f 的 per-pair top-200 DE 基因在**全局平均表达量 top-5,000 的非 HK 基因池**内选择（且实为按 mean expression 选择，非 variance-based HVG，命名有误导）；而 Methods line 31 只写"Top-200 identity genes were selected per comparison, excluding HK genes"，未提及 5,000 基因池。07c 则在全部 ~58,365 个非 HK 基因中选择。

**影响**：(i) 5,000 基因池的预筛选使 grand mean 从 ~47.74 降到 32.56，并使 Strong 目录发生**定性翻转**（microglia 主导 → OPC 主导），说明候选目录对预处理选择高度敏感。(ii) 正文引用的 CV=92.89%、ρ=0.181 来自 07c 数据（`phaseC_kn_variability.json`），与正文主数值不同源。(iii) 投稿包内三套脑区数字并存。

**建议**：统一为单一管线（建议 08d），在 Methods 完整披露 5,000 基因池及其选择标准；用同一管线重算 CV/ρ/ω_cal；重写 SN 3.3/3.5/3.7、Supp Table 3/4、复现指南 §4.4/§5.3；补充 k_f 基因池大小（如 200/1,000/5,000/全基因）对 Strong 目录的敏感性分析。

### M2. softmax(log1p(x)) 等价于 L1 归一化加伪计数；"softmax vs L1 normalize"的区别实际不存在，但论文未如实说明

**核查**（Python 独立验证）：
```
softmax(log1p(x)) = exp(log1p(x)) / Σ exp(log1p(x)) = (1+x) / Σ(1+x)
```
即 softmax 应用于 log1p 变换后的表达向量，**数学上等价于对 CP10k 表达量加 1 伪计数后做 L1 归一化**。二者完全相同（数值验证通过，误差 < 1e-16）。

与 L1 归一化 log1p(x) 本身（即 log1p(x)/Σlog1p(x)）不同——后者会使零表达基因权重为零，而 softmax 版本给每个基因至少权重 1/(d+Σx)。

**影响**：
- SN 3.11（line 79）对 softmax 的辩护（*"preserves relative magnitude information while ensuring non-negativity and sum-to-one"*）虽然不错，但没有揭示其与 L1+伪计数的等价性，也未讨论 +1 伪计数对低表达基因的均匀化效应（当 d=1,130 时，每个基因至少占 1/(1130+Σx) ≈ 0.09% 权重，对零表达基因影响显著）。
- 维度饱和问题：当 d 很大且大多数基因表达为零时，伪计数使分布趋近均匀，可能压降 k_n/k_f 的区分度。Supplementary Fig S10 的维度不变性模拟（`09c`）直接对 Dirichlet 概率向量算 JS，**未经过 softmax(log1p) 通路**，不能代表实际分析中的行为。

**建议**：
1. 在 Methods 写明 softmax(log1p) 的伪计数等价性：*"softmax normalization of log1p-transformed values is equivalent to L1 normalization with a pseudocount of 1, i.e., p_i = (1+x_i) / Σ(1+x_j)"*。
2. 讨论 +1 伪计数对低表达基因的影响及对维度饱和的潜在效应。
3. 将 S10 维度不变性模拟改为对 softmax(log1p(表达)) 向量（不同 d、不同基因池）重做。

### M3. per-pair k_f 的循环依赖（data snooping）已如实披露，但 AUC 比较的公平性未讨论

**位置**：Limitation 3（line 95）已如实承认循环依赖：*"the top-200 differentially expressed genes are selected by |μ_A − μ_B|, meaning that the genes defining 'functional divergence' are precisely those with the largest expression differences."*

**问题**：Table 1 的 AUC 比较中，CKI 使用 per-pair top-200 DE 基因（pair-specific 选择，直接基于被比较对的差异），而其他四个度量使用全局基因集：
- Raw JS：全部基因
- Spearman/Cosine：全部基因
- Marker Jaccard：per-CT top-200 highest expression（非 pair-specific）

这使 CKI 在 same-CT vs diff-CT 分类中享有信息优势（它"看到了"被比较对的差异基因），但仍排名垫底（AUC=0.680），这实际上是更强的证据说明 CKI 捕获了不同的信号维度。但论文未讨论这一比较的不对称性。

**建议**：在 Results 或 Discussion 中明确指出 CKI 的 per-pair 基因选择与其他度量的全局基因集的不对称性，并论证"即使享有 pair-specific 信息优势，CKI 的分类 AUC 仍最低"这一结果反而支持其设计目标。

### M4. 校准因子 6.67 的来源方案在文内自相矛盾

**位置**：
- 正文 line 51：pilot calibration 使用 hybrid 方案（per-pair top-200 DE k_f）。
- Limitation 17（line 96）：*"The empirical calibration factor (ω_cal = ω / 6.67...) was derived from mouse split-half controls using a global HVG set for k_f, but is applied to human, TCGA, and brain analyses that use per-pair DE gene selection for k_f."*

**核查**：`02b_pilot_v2.py` 代码证实为 hybrid（per-pair top-200 DE），与正文 line 51 一致，与 Limitation 17 矛盾。

**影响**：Limitation 17 的整个跨方案可迁移性讨论建立在错误前提上（实际上校准与人类/脑区方案一致，跨方案偏差问题比文中声称的小）。但 6.67 仅来自 n=6、CV≈52% 的 split-half，这一点文中已如实披露。

**建议**：更正 Limitation 17 前提；建议在人类或脑区数据内补做 per-pair DE 方案的 split-half 校准以验证 6.67 的可迁移性。

### M5. Figure 2B / 3D 图注类别定义与正文矛盾

**位置**：
- Fig 2B legend（line 113）：*"S (same sub-organ)"*。
- Fig 3D legend（line 114）：*"S (same sub-organ)"*。
- 正文 line 53：*"Same cell type across different organs (S category: mean ω = 21.31, n = 4 pairs)"*。
- 正文 line 57：人类分析中 same cell type across organs（mean ω = 15.83, n = 59）对应 X 类别，但文中未标注。

已知关注点 #1 属实。S 类别在图注中为"same sub-organ"但在正文中用于"same cell type across different organs"，二者是不同概念。

**建议**：统一为 "S: same cell type across different organs"（与代码中 `mouse_pilot_v2b_results.csv` 的 `S_same_ct` 一致），并核对图中 C/S/D/X 分组数据是否按正确定义绘制。

### M6. 人类 vs 小鼠基准比较不当且解释混乱

**位置**：正文 line 57：*"Human ω values ranged from 1.35 to 87.69 (mean 21.61, median 19.65, n = 4,851 pairs), substantively lower than mouse (mean 27.31)."*

**核查**：`mouse_pilot_v2b_results.csv` 中 27.31 为 X 类别（cross-organ，n=2 对）均值。用 n=2 的子类均值与人类 4,851 对全均值比较，统计上不当。随后正文给出的解释自相矛盾：先说方案相同（"same hybrid scheme"），又说方案不同（"global HVG 2,000 vs per-pair DE"），逻辑不通。

**建议**：删除该跨物种绝对值比较或改为同方案、同规模的 rank-based 比较，并澄清 27.31 的来源与 n=2。

### M7. tier 阈值无依据、无敏感性分析

**位置**：Methods line 35、Results line 79：
- Strong：residual < 0.3, ω < 15, lowest ω in pair
- Moderate：residual < 0.5, ω < 25
- Weak：residual < 0.75, ω < 35

**问题**：
1. 0.3/0.5/0.75 和 15/25/35 均为裸值，无任何 rationale（如残差分布分位点）或敏感性扫描。
2. 乘法残差模型中 μ_ct、μ_pair 由含被检验 pair 自身的观测数据估计（自 leverage / 收缩效应），残差的不确定性未量化。
3. "lowest ω in pair" 的 Strong 约束使每对 region 最多 1 个 cell type 可入选 Strong——这是非标准过滤步骤。
4. C1/M1 已示 Strong 目录对 k_f 基因池选择高度敏感（5,000 vs 全基因 → microglia↔OPC 翻转），tier 体系稳健性存疑。

**建议**：给出阈值选择的依据或做阈值敏感性表（如 residual < 0.2/0.3/0.4 各产生多少 Strong 及 cell-type 构成）；对残差模型做 leave-one-out 或 bootstrap 误差条。

### M8. Data availability 声明与实际投稿包不符

**位置**：主稿件 line 100：*"All analysis notebooks and processed data matrices are included in the Supplementary Data."*

**核查**：v35 投稿包内仅含 DOCX/PDF/图文件，无代码或 processed data 矩阵。补充材料 Supplementary Data 1（line 97–98）仅列出脚本索引并指向 GitHub 仓库。代码在 GitHub/Zenodo 属实（可访问），但"included in Supplementary Data"的声明不实。已知关注点 #4 属实。

**建议**：改为 *"All analysis notebooks and processed data matrices are available at the GitHub repository (https://github.com/zhanglknt/CKI-cell-type-identification) and archived at Zenodo (DOI: 10.5281/zenodo.15670808)."* 或真正补充数据文件。

### M9. 人类分析的 pseudobulk 构建方式未披露（仅取每 CT 最大 donor）

**位置**：Methods line 21/29 声称 pseudobulk 为"averaging expression across cells sharing the same cell-type annotation"。

**核查**：`13_phase35_method_comparison.py` line ~100–120 对每个 CT 仅取**细胞数最多的单个 donor** 构建 pseudobulk（代码逻辑：`donors_ok` 排序取 `largest_donor`）。脚本自述承认"Single-donor pseudobulks limit assessment of inter-individual variation"。

**影响**：与 CKI 的核心卖点直接相关——若 pseudobulk 本就是单 donor，则 k_n 度量的是技术/区域噪声而非个体间变异，论文"通过 k_n 扣除个体间噪声"的叙事基础受损。

**建议**：在 Methods 如实披露 donor 选择规则，并讨论其对 k_n 解释的影响；或改为跨 donor 聚合重跑。

### M10. 投稿包内大量陈旧数字未随 softmax 重跑更新

**位置与证据**（均已与 results 文件核对）：
- **人类样本量矛盾**：Table 1 标题"102 cell types, 4,851 pairs"——但 C(102,2)=5,151≠4,851=C(99,2)。实际 `phase35_all_metrics_pairs.csv` 为 4,851 行（99 CT 条目）；`phase33_v3_human_pairs.csv` 为 5,151 对。复现指南 §4.2 与 SN 3.3 写 5,151 对，正文写 4,851 对。
- **参数 sweep AUC 矛盾**：正文 line 49 与 Fig S1 图注 AUC=0.786；SN 1.3（line 20）与 Supplementary Table 1 写 AUC=0.847。
- **Supp Table 4 tier 计数**：7,943 (25.0%) residual<0.75 vs 正文 55+2,120+6,149=8,324（26.2%，与 `brain_bs_null_observed_pairs.csv` 一致）。
- **复现指南 Phase B/C/D 各节**（§5.3c、§5.4）整体描述已被 block-shuffle 取代的旧分析（B=10,000 per-signal P、CV=97.35%、ρ=−0.027、ω_cal 8.01→1.20 等）。

**建议**：全面数字审计，以当前 results 文件为唯一事实来源；明确人类分析取 phase35（99 CT、4,851 对）并全文统一；复现指南删除或明确标注已废弃的 Phase B/C/D 输出。

---

## Minor 问题

1. **包版本**：正文/指南/Zenodo 均写 v0.3.1，仓库实际为 v0.3.2（`cki/__init__.py`、`pyproject.toml`）——恰是含 log2 修复与 clamp 的版本，应引用并重新打 tag/存档。
2. **Abstract 措辞**：*"a human brain single-nucleus atlas from millions of cells"*——实际分析 888,263 核（过滤后 886,808），atlas 全量 ~3.3M。建议改为准确表述（已知关注点 #7 属实）。
3. **HK 基因数表述**：Methods line 29 "1,130 genes; human column" vs SN 4.2 "1,129 matched" vs 脑区 "1,115 matched"——建议统一给出"参考 1,130、匹配数因数据集而异（人类 1,129、脑区 1,115）"。
4. **AUC 任务描述**：Table 1 / 正文应写明分类任务是"same-cell-type（跨器官）pair 检测"，正类仅 59/4,851（1.2%），并说明打分方向（negate distance for AUC）；"102 cell types"应为 99。
5. **20.80 的口径**：正文 line 60 "different-organ pairs (mean ω ... 20.80)"——20.80 为 diff-organ diff-CT（n=3,754）均值，全部 diff-organ 为 20.73（n=3,813）；两种口径混用，建议标注清楚。
6. **SN 1.5 的"critical values"**：将 permutation null 的 2.5/97.5 分位称为"test critical values at alpha=0.05"与单侧检验框架不符，属概念含混。
7. **`_compute_phase35_auc.py` 使用数据驱动 HK 基因**（Bone_Marrow 检测、CV<中位数）而非 HRT Atlas——虽然最终投稿数值来自 `13_phase35`（HRT Atlas，经 `precompute_figure_data.py` 路径确认），但该脚本仍在仓库中且输出 `phase35_minimal_metrics.csv`；为避免误用，建议删除或在脚本头注明非投稿版本。
8. **08d 的 "N_HVG=5000" 命名**：按平均表达量选择（`np.argsort(non_hk_means)`），非 variance-based HVG，命名易误导（并入 M1 处理）。
9. **Python 版本**：复现指南 §1.1 写 Python 3.13.12，正文 Computational environment（line 39）写"Python 3.13.12 with scanpy >= 1.9.0"——3.13.12 不存在（Python 3.13 最高为 3.13.x，但 3.13.12 不是真实版本号；截至 2026-08 Python 3.13 的最新 patch 版本应 < 3.13.20）。建议核实实际版本号。
10. **脑区候选描述存在多处与数据不符的事实错误**（对照 `brain_bs_null_results.csv`）：
    - line 84：*"Eleven of the twelve involve the substantia nigra pars reticulata (SN-RN)"*——需逐条核对。
    - line 82：*"nine pairs involve the temporal frontal cortex (TF)"*——所列搭档数与"nine"自相矛盾。
    - 建议所有候选叙述改为脚本自动生成的表驱动文本。

---

## 已妥善解决的上一轮（v5）问题（经独立验证）

1. **softmax 统一与 base-2 声明一致**：`cki/core.py` `js_divergence` 使用 `np.log2`（line 47, 53）；`ensure_probability_distribution` 默认 mode="softmax"（`utils.py` line 13）；08d/13/09c 均经 softmax 单次归一化；13/_compute 脚本注释明确"不做双重 softmax（非幂等，会膨胀 ω 约 30×）"——v5 的双重 softmax bug 确已修复。
2. **v5 C1（脑区 FDR）已正确落实**：block-shuffle null（08d/08e）以 10x library 为 block、置换 library→region 分配（`perm_assign = sample_region_idx[rng.permutation(n_samples)]`，保留 per-region library 计数多重集）；per-pair 下尾 P + BH（m=31,764）。结果文件逐项复算吻合：Strong=55、raw P<0.05=37、min q=0.9494。该 null 确比旧 per-pair shuffle 保守（旧：36.3% 触底；新：min q=0.949），exchangeability 假设的局限已在 Limitation 19 披露。
3. **per-pair DE 的 data snooping 如实披露**：Limitation 3 明确承认 top-200 按 |μ_A−μ_B| 选择的循环性、k_f 为功能散度上界；且经代码核实，null 中每轮置换**重做**基因选择（08d `pair_omegas` 对置换后 pseudobulk 重算 top-200），检验内部自洽。
4. **phase35 方法比较重跑数值可信**：Table 1 全部 AUC（0.680/0.849/0.801/0.690/0.887）、负相关 r=−0.36~−0.46、same-organ 反转（24.87 vs 20.80）、ω 范围 1.35–87.69 与 `phase35_*` 输出一致；Table 2 的 17 个 cell type 均值/SD/n 亦逐项吻合。
5. **phaseB/C 更新值真实**：kn CV=92.89%、per-pair vs global-kn ρ=+0.181 与 `phaseC_kn_variability.json` 一致（尽管周边文档仍存旧值，见 M1/M10）。
6. **TCGA kn floor 饱和的披露**：aggregate TN kn 3.0×10⁻⁵~1.9×10⁻⁴、3/5 癌种触底、ω 饱和及"跨数据集只做 rank 比较"的告诫均已写入 Discussion / Limitation 20（叙事与代码参数一致，但需验证 floor 是否在 TCGA 脚本中实际 clamp，见 C4）。
7. **定位诚实**：CKI 明确声明为启发式指数而非选择度量、AUC 排名垫底如实报告、脑区候选定位为 hypothesis-generating——这些处理得当。
8. **block-shuffle 比 per-pair shuffle 更保守的声明可验证**：旧 per-pair shuffle 36.3% 触底（P=9.99×10⁻⁵），新 block-shuffle min q=0.949——后者确实更保守，因为保留了 library-level 结构。

---

## 结论

方法学核心（JS 分解 + block-shuffle null + 置换检验框架）基本站得住，关键统计结果可从随附结果文件复算验证。但 v35 存在**6 项 Critical**：B=1,000 与 m=31,764 的组合使 FDR 显著结构性不可能（C1）；Figure 2D 含硬编码占位数据（C2）；S7 图注与正文叙事方向性矛盾（C3）；k_n floor 声明与代码不符（C4）；Methods 对 k_n 计算方式的描述失实（C5）；BH-FDR 引用错配（C6）。6 项 Critical 全部为可修复的文档/一致性/披露/统计功效问题，无需推翻方法本身。建议大修：统一管线与数字、披露 5,000 基因池与 donor 选择、删除占位图数据、修正 k_n 描述与 B 值论证、补做基因池/阈值敏感性分析，并提高 per-pair screen 的 B 值或改用层级 FDR。
