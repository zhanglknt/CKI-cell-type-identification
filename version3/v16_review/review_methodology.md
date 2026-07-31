# CKI v16 方法学审稿报告

**审稿人**: 方法学专家
**审稿日期**: 2026-07-27
**版本**: v16

## 评分
- 方法学评分: 7.0/10 (v14: 6.8)
- 投稿准备度（方法学维度）: 72%
- Critical: 4 | Major: 9 | Minor: 10

---

## v14→v16 改进确认

### 已修复的v14 Critical Issues

| v14编号 | 问题 | v16状态 | 确认依据 |
|---------|------|---------|----------|
| C1 (v14) | 多重检验校正缺失 | **部分改善** | Bootstrap范围缩减至mouse pilot (P22, P37, P43; Sup Note 1.5, 3.2, 3.3)；大规模分析改用描述性统计。但30个Strong candidate仍无FDR控制（见M2） |
| C2 (v14) | Bootstrap P值公式三方不一致 | **正文/补充材料已统一** | Manuscript P22/P37/P43、Sup Note 1.5、Algorithm 1 line 15 均使用 `2×min((count+1)/(B+1), ...)` 双侧+1伪计数公式。**但可复现性指南仍使用不同公式**（见C2） |
| C3 (v14) | 校准实验n=6 + TOST被移除 | **部分改善** | TOST注释已添加 (P47)；但n=6未扩展（见M3） |
| C4 (v14) | CKI缩写Kinetic/Comparative矛盾 | **✅ 已修复** | 全文统一为 "Cell-state Kinetic Index" |
| C5 (v14) | P020 softmax文本重复 | **✅ 已修复** | softmax公式在正文中仅出现一次 (P20) |
| C6 (v14) | k_n/k_f跨维度可比性无理论支撑 | **未修复** | P50仍为断言而非证明（见M1） |

### 已修复的v14 Major Issues

| v14编号 | 问题 | v16状态 |
|---------|------|---------|
| M3 (v14) | 负相关"proving"过强 | **未修复** — 摘要仍有"proving"，P52仍有"strongest evidence"（见M4） |
| M4 (v14) | 同器官>跨器官反转无替代验证 | **未修复** — 仍无固定基因集验证（见m9） |
| M5 (v14) | 乘法残差模型阈值无正式零分布 | **未修复** — 仍无置换验证（见M5） |

### v15→v16 新增修复确认

- **P0-4 (Bootstrap scope)**: ✅ 已确认。Manuscript P22/P37/P43、Sup Note 1.5/3.2/3.3 一致声明 B=500 仅用于 mouse pilot (15 pairs + 6 calibration controls)，人类/TCGA/脑图谱使用描述性统计。
- **P0-5 (Software versions)**: ✅ 已确认。P35: Python 3.13.12; Reproducibility guide 1.1: numpy 2.4.6, scipy 1.17.1 等。
- **P0-7 (Terminology)**: ✅ 已确认。全文统一使用 "baseline divergence rate k_n" 和 "functional divergence rate k_f"。
- **P0-9 (k_f selection bias)**: ✅ 已确认。P97 Limitations 第三点提供了论证：校准对照 (mean ω=1.54) 表明HVG选择本身不会膨胀ω。
- **P0-10 (CI concept)**: ✅ 已确认。Sup Note 1.5 和 Reproducibility guide 5.1 均明确标注 "permutation-based test critical values... NOT confidence intervals for omega itself"。
- **P0-11 (TOST note)**: ✅ 已确认。P47: "formal equivalence testing (e.g., two one-sided tests, TOST) with a larger calibration sample would provide stronger statistical evidence"。
- **TCGA log2 transformation**: ✅ 已确认。P26: "log2(TPM + 0.001)"; Sup Note 1.6: "log2(TPM + 0.001)"。
- **Extended Data → Supplementary Figure**: ✅ 已确认。全部使用 "Supplementary Figure S1-S7"。

---

## Critical Issues

### C1. HK基因选择方法在正文与可复现性指南之间存在根本性矛盾

**这是v16最严重的可复现性问题。**

- **Manuscript P19**: "Housekeeping (HK) genes are auto-detected from data using a combined criterion: detection rate > 0.9... For human and mouse datasets, the HRT Atlas v1.0 consensus set (1,130 human-mouse shared HK genes) is optionally used as supplementary enhancement (union with detected set)."
- **Manuscript P46**: "Housekeeping genes were auto-detected from data using a combined criterion (detection rate > 0.9 and CV below the 30th percentile), supplemented with 1,130 human-mouse conserved reference HK genes from the HRT Atlas"
- **Supplementary Note 1.2**: "CKI employs data-driven automatic detection of HK genes (joint criteria: detection rate > 0.9 and CV < 30th percentile), supplemented by the HRT Atlas v1.0 consensus set"
- **Reproducibility guide 3.1**: **"In the analyses reported here, housekeeping (HK) genes were NOT auto-detected. Instead, pre-specified HK gene lists were loaded from the HRT Atlas reference file... This auto-detection was NOT used in the current analyses (the pre-specified list approach was preferred for reproducibility)"**

正文和补充材料明确说HK基因是通过数据驱动自动检测（检测率>0.9 + CV<30th percentile），HRT Atlas仅作为可选增强。但可复现性指南明确说自动检测**未被使用**，仅使用了预指定的HRT Atlas列表。这两种方法会产生不同的HK基因集，从而导致不同的k_n值和不同的ω结果。

**影响**: 读者按照正文方法操作会得到与论文报告不同的结果。这直接破坏了可复现性。

**建议**: 必须核实实际分析中使用的方法，并使正文、补充材料和可复现性指南完全一致。如果实际使用的是HRT Atlas预指定列表，则正文P19/P46和Sup Note 1.2需要修改。

### C2. P值公式在可复现性指南中与正文/补充材料不一致

- **Manuscript P22/P37/P43** 和 **Supplementary Note 1.5**、**Algorithm 1 line 15**:
  `P = 2 × min((count(ω_null ≥ ω_obs) + 1)/(B + 1), (count(ω_null ≤ ω_obs) + 1)/(B + 1)), capped at 1.0`
  （双侧，基于ω_obs在零分布中的位置）

- **Reproducibility guide 5.1, step 4**:
  `p = (count(|omega_null - 1| >= |omega_obs - 1|) + 1) / (B + 1)`
  （基于|ω-1|距离的单侧公式，无×2因子）

这两个公式在数学上不等价。公式1分别计算上尾和下尾概率取较小值后乘2（标准双侧置换检验）。公式2计算的是|ω_null - 1| ≥ |ω_obs - 1|的比例，这是一种基于偏离1的距离的检验，没有乘2因子。对于相同的零分布和观测值，这两个公式会给出不同的P值。

**影响**: 使用不同公式可能改变哪些比较达到统计显著性，直接影响mouse pilot的15个细胞类型对和6个校准对照的结论。

**建议**: 统一为正文公式（双侧+1伪计数），并修正可复现性指南5.1中的公式。

### C3. Tabula Muris小鼠数据中identity基因选择策略矛盾

- **Manuscript P19**: "k_f = JS(norm(ε_A[I]), norm(ε_B[I])), where I is the set of top-2,000 highly variable genes (HVGs; Seurat flavor) excluding HK genes" — 描述默认全局HVG策略
- **Manuscript P46 (校准实验)**: "Identity genes were the top-2,000 highly variable genes (HVGs; Seurat), excluding HK genes"
- **Reproducibility guide 4.1, step 7**: "Compute per-pair k_f with top-200 DE genes." — 使用per-pair top-200差异表达基因
- **Reproducibility guide 3.2**: "Default (CKI): top-2,000 highly variable genes (HVGs; Scanpy seurat flavor)... Hybrid mode: global k_n computed once with shared HK gene set; per-pair k_f uses the top-200 differentially expressed genes"

正文说小鼠数据使用top-2,000 HVG（全局策略），但可复现性指南说小鼠使用top-200 DE genes（per-pair策略）。这是两种根本不同的基因选择方法：
- top-2,000 HVG是全局选择的，所有比较对使用相同的identity基因集
- top-200 DE是每对比较单独选择的，不同对使用不同基因集

**影响**: 这两种策略会产生不同的k_f值，从而产生不同的ω值。703个细胞类型对的结果可能完全不同。

**建议**: 核实小鼠数据实际使用的策略。如果确实使用了top-200 DE（如可复现性指南所述），则正文P19和P46需要修改。

### C4. TCGA临床分层样本量在正文与可复现性指南之间存在严重不一致

| 临床变量 | 分层 | Manuscript P60 | Reproducibility guide 4.3 | 差异 |
|----------|------|----------------|---------------------------|------|
| LIHC Edmondson | G1 | n=39 | n=12 | **27** |
| | G2 | n=133 | n=118 | 15 |
| | G3 | n=105 | n=127 | 22 |
| | G4 | n=11 | n=32 | 21 |
| | 总计 | 288 | 289 | 1 |
| BRCA PAM50 | Luminal A | n=224 | n=562 (LumA) | **338** |
| | Luminal B | n=123 | n=207 (LumB) | 84 |
| | HER2 | n=55 | n=78 | 23 |
| | Basal-like | n=97 | n=181 | 84 |
| | Normal-like | n=7 | n=36 | 29 |
| | 总计 | 506 | 1,064 | 558 |
| LUAD mutation | EGFR | n=61 | n=97 | 36 |
| | KRAS | n=120 | n=152 | 32 |
| | WT | n=311 | n=283 | 28 |
| | 总计 | 492 | 532 | 40 |

每个分层的样本量都不同，且差异巨大（如BRCA Luminal A: 224 vs 562）。这表明正文和可复现性指南描述的可能是不同的数据子集或不同的过滤标准。

**影响**: 样本量直接影响统计检验的功效和结果。无法确定哪个是正确的。

**建议**: 核实实际分析样本量，统一正文和可复现性指南。

---

## Major Issues

### M1. k_n/k_f跨维度可比性仍无理论支撑或模拟验证

v14 C6（Critical）未修复。P50的辩护仍为断言：

> "Critically, since ω = k_f/k_n is a ratio of JS divergences computed from the same underlying pseudobulk expression space, the normalization remains internally valid despite the different gene selection strategies."

问题在于：k_n在~1,130个HK基因上计算JS散度，k_f在200个（hybrid模式）或2,000个（默认模式）identity基因上计算JS散度。JS散度的期望值依赖于概率向量的维度——维度越高，两个随机分布纯偶然产生较大散度的概率越高。因此k_f/k_n的比值可能被维度差异系统性扭曲，而非反映生物学信号。

Discussion P93承认"CKI currently lacks a formal phylogenetic framework"，但未提及维度问题。Supplementary Note 1.1提到"when both k_n and k_f approach 1, omega = k_f/k_n may still vary"，但未深入分析。

**建议**: 补充模拟实验：在零假设下（两组来自同一分布），对不同维度组合（如|M|=1130, |I|=200/500/2000）计算ω的期望值，验证ω≈1是否在维度不匹配时成立。

### M2. 大规模分析中无多重检验校正，但Strong候选信号被深度解读

v14 C1（Critical）部分改善——bootstrap范围缩减至mouse pilot，大规模分析改用描述性统计。但问题仍然存在：

- 31,764个脑区比较中，通过乘法残差模型识别出30个Strong候选信号（残差<0.3, ω<15等硬阈值）
- 这些信号被逐一进行深度生物学解读（P79-89），已超出纯探索性分析范畴
- 在31,764次比较中，即使零假设为真，期望的残差<0.3的假阳性数量可能不可忽略
- 未报告任何形式的多重检验控制（FDR、Bonferroni等），也未通过置换模拟估计零分布下的假阳性率

Supplementary Note 3.3声明"descriptive statistics are reported without permutation testing"，但乘法残差模型的硬阈值筛选本身就是一种隐式假设检验。

**建议**: 至少补充置换模拟：在随机打乱区域标签后，计算残差<0.3的期望假阳性数，以量化30个Strong信号的统计可信度。

### M3. 校准实验n=6仍然不足，TOST注释虽已添加但未实质解决

P47的TOST注释是积极改进，但n=6仍然不充分：

- n=6时，mean ω=1.54的95%置信区间极宽（粗略估计约为[0.8, 2.3]）
- Tabula Muris有32个细胞类型条目，可轻松扩展至n≥50（每个细胞类型做多次随机分割）
- P47声称"This confirms that CKI recognizes biologically equivalent cell populations as having no functional divergence"——P>0.05不等于等价，这一点TOST注释已承认，但正文结论仍过于肯定
- mean ω=1.54（而非≈1）的偏差未被讨论：为什么不是1.0？softmax归一化或HVG选择是否引入了系统性向上偏倚？

**建议**: 将校准扩展至n≥50（利用32个细胞类型多次随机分割），并正式执行TOST等价检验。同时讨论ω=1.54>1的可能原因。

### M4. "Proving"和"independent"的声明仍过强

v14 M3未修复。

- **Abstract**: "CKI ω was negatively correlated with all standard distance metrics (Spearman r = −0.38 to −0.57, all P < 0.001), proving it captures an independent information dimension"
- **P52**: "This negative correlation is the strongest evidence that CKI measures something fundamentally different from all existing distance metrics"

r = -0.38到-0.57意味着CKI与标准指标共享14%-32%的方差（r²）。"Independent"通常要求r≈0。"Proving"在科学写作中应避免。此外，负相关而非零相关也值得解释——为什么是负相关而非不相关？如果CKI真正捕获"正交"信息，应该看到r≈0而非r≈-0.5。

可能的解释：CKI的ω = k_f/k_n是一个比值，当k_n大时ω变小，而标准距离指标与k_n正相关（因为k_n大意味着两组整体差异大），因此ω与标准指标呈负相关。这并非"独立信息维度"的证据，而可能是比值定义的数学必然性。

**建议**: (1) 将"proving"改为"indicating"或"suggesting"；(2) 讨论负相关的数学原因；(3) 考虑计算k_f本身（而非比值ω）与标准指标的相关性，以区分"比值效应"和"真正正交信息"。

### M5. 乘法残差模型的阈值无正式统计验证

v14 M5未修复。

乘法残差模型使用硬阈值定义Strong/Moderate/Weak：
- Strong: residual < 0.3, ω < 15, lowest ω in region pair, pair median ω > 20
- Moderate: residual < 0.5, ω < 25
- Weak: residual < 0.75, ω < 35

这些阈值的选择缺乏统计依据。没有：
- 零分布下的假阳性率估计
- 阈值对结果敏感性的分析（如residual < 0.2 vs 0.3 vs 0.4时Strong候选数量变化）
- 与正式统计检验（如置换检验）的对比

**建议**: 补充置换验证：随机打乱区域标签，计算残差分布，估计各阈值下的FDR。

### M6. ω值上限截断（capped at 1,000）未在正文中提及

- Supplementary Note 1.1: "in practice omega is capped at 1,000"
- Algorithm 1, line 7: "omega <- k_f / k_n // capped at 1,000"
- **Manuscript正文**: 完全未提及

如果k_n接近零（两组HK基因分布几乎相同），ω会趋向无穷大。截断至1,000是一种工程处理，但会影响结果分布。正文报告的最大ω值为58.69（人类）和344.5（BRCA Luminal A），似乎未达到截断阈值，但读者需要知道这一处理。

此外，k_n = 0的边界情况（完全相同的HK基因分布）会导致除零错误，正文和补充材料均未讨论。

**建议**: 在Methods中说明ω截断处理和k_n = 0的边界情况处理。

### M7. 脑图谱pseudobulk归一化顺序与其他数据集不一致

- **标准流程 (Sup Note 1.6)**: 先对每个细胞做library size normalization + log1p，再计算pseudobulk（均值）
- **脑图谱 (Reproducibility guide 4.4, step 4)**: "Build pseudobulk vectors: raw count means per (ct, region) group. Normalize each pseudobulk: softmax(log1p(pb / sum(pb) * 1e4 + 1e-9))" — 先计算raw count的pseudobulk均值，再做归一化

操作顺序不同会影响结果。先归一化再求均值 vs. 先求均值再归一化，在数学上不等价（log1p是非线性变换，均值不交换）。

**建议**: 统一归一化顺序，或在Methods中明确说明脑图谱使用不同流程的原因。

### M8. Algorithm 1伪代码中B的默认值与正文不一致

- Algorithm 1, line 10: "for b = 1 to B (default 1,000):"
- Manuscript P22/P37: B=500 for mouse pilot
- Reproducibility guide checklist: "500 (mouse) or 1000 (human/TCGA/brain)" — 但正文明确说human/TCGA/brain不做bootstrap

伪代码的"default 1,000"与实际使用的B=500不一致。可复现性指南的"1000 (human/TCGA/brain)"更令人困惑，因为正文明确声明这些数据集未执行bootstrap。

**建议**: 修正Algorithm 1为 B=500（与正文一致），修正可复现性指南删除"1000 (human/TCGA/brain)"。

### M9. Tabula Sapiens QC阈值在补充材料与可复现性指南之间不一致

- Supplementary Note 4.2: "cells with < 200 detected genes were removed; cells with > 20% mitochondrial gene expression were removed"
- Reproducibility guide 4.2: "filter cells with < 500 genes"

200 vs 500基因的过滤阈值会保留不同的细胞集，影响下游分析。

**建议**: 核实实际使用的QC阈值并统一。

---

## Minor Issues

### m1. "Cohen's d"术语使用不精确

P22使用"Standardized effect size"，P37/P43使用"Cohen's d"。公式均为 (ω_obs - mean(ω_null)) / sd(ω_null)。严格来说，Cohen's d定义两组均值之差除以合并标准差，而此处的公式是观测值与零分布均值的标准化距离，更接近z-score。建议统一术语为"standardized effect size"或明确定义此处的Cohen's d用法。

### m2. 可复现性指南中Tabula Sapiens细胞类型数量错误

- Manuscript P25/P50: 99 cell-type entries
- Supplementary Note 4.2: 99 entries
- Reproducibility guide 4.2: "102 cell-type entries"

99个细胞类型产生 C(99,2) = 4,851 对，与正文一致。102应为错误。

### m3. HVG flavor描述不一致

- Manuscript P24: flavor="seurat"（对应参考文献26, 27: Hao et al. 2021, 2024）
- Reproducibility guide checklist: "HVG Seurat v3"
- scanpy中 flavor="seurat" 和 flavor="seurat_v3" 是不同方法

应统一为 flavor="seurat"（如正文所述）。

### m4. 脑图谱细胞类别计数不完全匹配

P27列出"10 major non-neuronal classes"但仅列出9个有具体核数（Bergmann glia的核数未在P27给出）。P68列出10类包括committed oligodendrocyte precursors。P27说OPCs "110,454 total including committed"，但P68将committed OPCs单独列出。建议在P27中明确列出所有10类的核数。

### m5. ω = 1.54作为"close to 1"的判断标准需要更好的论证

P47说mean ω = 1.54"confirms baseline behavior"，但1.54比1高出54%。正文未讨论：
- 什么范围的ω被视为"≈1"？[0.5, 2]? [0.8, 1.2]?
- 1.54 > 1是否暗示系统性向上偏倚？
- 在实际应用中，ω = 2应被解读为"baseline"还是"functional divergence"？

### m6. k_n = 0的边界情况未讨论

如果两组的HK基因pseudobulk经过softmax归一化后完全相同，k_n = 0，则ω = k_f/0 = ∞。虽然capped at 1,000可以处理，但应在Methods中说明。

### m7. Scanpy版本与numpy 2.x的兼容性

Manuscript P35: "scanpy >= 1.9.0"；Reproducibility guide 1.1: numpy 2.4.6。numpy 2.x有破坏性变更，较旧版本的scanpy可能不兼容。应指定实际使用的scanpy版本。

### m8. Figure 5图注与正文不匹配

Figure 5 legend (P116): "CKI ω ranking of 38 shared cell types between human and mouse"
但正文P65讨论17个细胞类型，P62说n=59 same-cell-type cross-organ pairs。"38 shared cell types"未在其他地方出现。

### m9. 同器官ω > 跨器官ω的反转现象仍无替代解释验证

v14 M4未修复。P55报告CKI是唯一一个same-organ pairs > different-organ pairs的指标。正文将其归因于"functional specialization within shared microenvironments"，但未使用固定基因集验证这一解释。一个替代假说是：per-pair DE基因选择策略本身可能在same-organ对中选择出更相似的基因（因为same-organ细胞类型共享微环境基因），从而人为膨胀same-organ的ω。

### m10. 数据版本号和访问日期仍缺失

v14 M2(数据)未修复。四个公共数据集（Tabula Muris, Tabula Sapiens, TCGA, Siletti brain atlas）均未报告版本号或访问日期。CZ CELLxGENE等平台会更新数据，不同版本可能产生不同结果。

---

## 优点

1. **概念创新性强**：将Ka/Ks比值的启发式逻辑引入转录组比较，分解为baseline（k_n）和functional（k_f）两个组分，是真正的方法学创新。与现有方法（差异表达、Wasserstein距离、标准距离度量）形成互补而非替代关系。

2. **验证规模宏大**：跨四个数据集（小鼠图谱、人类图谱、TCGA泛癌、人脑图谱），总计数百万细胞/样本，覆盖多物种、多疾病、多组织尺度。特别是31,764个脑区交叉比较的规模令人印象深刻。

3. **对Ka/Ks类比的边界有诚实讨论**：Discussion P91-93明确列出CKI与Ka/Ks的四点本质差异（连续表达向量vs序列比对、经验定义vs遗传密码、无正式演化模型、无突变率消除机制）。这比v14的讨论更加深入和诚实。

4. **k_f选择偏倚论证合理**：Limitations P97第三点提供了有效论证——校准对照（mean ω=1.54）表明HVG选择本身不会膨胀ω，因为当两组生物学等价时，k_f和k_n同样小。

5. **OPC阴性对照设计巧妙**：P77利用OPC（成人CNS中迁移最活跃的细胞）产生0个Strong信号作为阴性对照，有力验证了乘法残差模型检测的是发育历史签名而非一般性细胞运动性。这一逻辑链条非常出色。

6. **术语统一性显著改善**：k_n/k_f命名、bootstrap范围、CI概念等在正文和补充材料间已基本一致（可复现性指南除外）。

7. **软件版本和代码可及性**：CKI v0.3.1开源、Zenodo DOI永久存档、完整分析脚本索引，可复现性基础设施完善。

8. **统计透明度提升**：明确声明FDR未校正、P值为原始经验值、效应量与P值并列报告，体现了统计诚实性。

---

## 总体评价

CKI v16在概念框架和验证规模上保持了高水平。Ka/Ks类比作为启发式框架，其边界在Discussion中得到诚实且深入的讨论——明确区分了"启发式类比"与"形式等价"，这是v16最显著的改进之一。k_f选择偏倚的论证（通过校准对照反证）逻辑清晰，OPC阴性对照的设计展现了良好的实验逻辑。四个数据集的跨尺度验证（小鼠→人类→癌症→脑发育）构成了有说服力的证据链，特别是脑区分析中30个Strong信号与发育神经科学文献的系统交叉验证，展示了计算方法产生生物学洞见的能力。

然而，v16存在一个严重的系统性问题：**可复现性指南与正文/补充材料之间的多方矛盾**。HK基因选择方法（自动检测 vs 预指定列表）、P值公式（2×min双侧 vs |ω-1|距离）、小鼠identity基因策略（top-2000 HVG vs top-200 DE）、TCGA临床分层样本量（差异达数百人）——这些不是表述差异，而是会影响结果的根本性方法学矛盾。这意味着按照正文方法操作无法复现可复现性指南中描述的结果，反之亦然。这些问题虽然部分局限于可复现性指南，但NAR审稿人几乎必然会交叉检查这两个文档。

从方法学严谨性看，k_n/k_f跨维度可比性（M1）仍是未解决的核心理论缺陷。正文P50的"internally valid"断言缺乏数学证明或模拟验证。此外，"proving independent information dimension"的声明（M4）在r=-0.38到-0.57的范围内过强——负相关可能反映比值定义的数学性质而非真正正交信息。校准实验n=6（M3）虽已添加TOST注释，但未实质扩展，仍不足以支撑"confirms baseline behavior"的结论。建议在投稿前优先解决C1-C4（可复现性指南与正文的矛盾），这些问题的修复工时较短但对审稿人印象影响最大。
