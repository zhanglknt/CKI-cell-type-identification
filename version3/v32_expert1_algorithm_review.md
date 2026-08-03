# CKI v32 独立审稿 — E1: 计算方法与可复现性

**审稿日期**: 2026-08-02
**评分**: 8.7/10 (v28: 8.4/10, Δ: +0.3)
**审稿文件**: CKI_NAR_Manuscript_fulltext.txt, CKI_NAR_Supplementary_fulltext.txt, CKI_NAR_Reproducibility_Guide_fulltext.txt, CKI_NAR_Cover_Letter_fulltext.txt, MANIFEST_v32.txt, Table1-2_fulltext.txt, CKI_graphical_abstract.svg (术语检查)

---

## 1. 核心发现概要

v32 在 v28 基础上完成了 P0 (3/3) + P1 (8/8) + P2 (19/19) 全部 30 项修复，是迄今最完整的版本。算法核心数学（softmax → JS divergence → ω = k_f/k_n）保持正确无 Critical。最显著的改进是 P0-3 校准因子 CI [4.12, 9.33] 在正文 5 处位置完整添加，以及 Limitation #17 对跨方案校准因子的全面讨论（含 1.62× / 0.71× 因子偏移量化）。图形摘要中 v26 残留的 "selective" / "neutral" 术语已清除。Python ≥3.10 在正文和 Cover Letter 中一致声明。

扣分主要来自：(1) Repro Guide Section 6 (Parameter Summary) 实际为空，参数表被遗弃在文档末尾（Major）；(2) 数据源声明在 Repro Guide 与正文间不一致（Major）；(3) MANIFEST 中 "FDR-significant descriptive" 术语自相矛盾（Minor）。这些问题不影响算法正确性，但损害可复现性体验。

**Critical: 0 | Major: 2 | Minor: 5**

---

## 2. v28→v32 修复验证

### P0 修复（3/3 已解决）

| 编号 | v28 问题 | v32 验证结果 | 说明 |
|------|----------|:------------:|------|
| **P0-1** | Strong candidate 计数 58 vs 30 矛盾 | ✅ 已解决 | Manuscript L81: "Astrocyte (6), oligodendrocyte (10), microglia (10), fibroblast (1), and vascular cells (3)" = 6+10+10+1+3 = **30** ✓。MANIFEST L57 同样写 "6+10+10+1+3=30"。L81 后文 16+14=30 一致。Bergmann glia 明确声明 0 Strong signals (L89)。计数完全正确。 |
| **P0-2** | MANIFEST EVT/FDR 声明与正文矛盾 | ✅ 已解决 | MANIFEST L58: "P0-2: MANIFEST FDR statement: 'No formal FDR'" ✓。Manuscript L81: "formal FDR correction is not applicable" ✓。Supp SN 3.3 (L68): "precluding meaningful Benjamini-Hochberg FDR correction" ✓。Repro Guide §5.3 (L166): "precluding meaningful BH-FDR correction" ✓。MANIFEST L72 仍使用 "FDR-significant descriptive" 术语，略有矛盾（见 New-M2）。 |
| **P0-3** | 校准因子跨方案转移未验证 + 精度不足 | ✅ 已解决 | CI [4.12, 9.33] 在正文 **5 处**位置确认：① Abstract (L11) ② Introduction (L18) ③ Methods/Statistical reporting (L42) ④ Discussion (L93) ⑤ Limitation #17 (L100)。Limitation #17 全面重写：解释 global HVG vs per-pair DE 方案差异、量化 CI 范围影响（下界 4.12 → 1.62× 上移，上界 9.33 → 0.71× 下移）、论证 rank-based 解释鲁棒性、提供 calibrate_omega() 函数供用户验证。Repro Guide §5.4a (L176) 记录校准脚本路径。 |

### P1 修复（8/8 已解决）

| 编号 | v28 问题 | v32 验证结果 | 说明 |
|------|----------|:------------:|------|
| **P1-1** | 脑区非显著信号应从 Strong tier 降级 | ✅ 已解决 | Manuscript L91 新增 "Threshold-passing but non-significant signals" 段落，明确 14 个信号 "should not be interpreted as evidence of biological structure"。L98 Discussion 重申 "did not reach statistical significance (all P ≥ 0.76), suggesting they may reflect stochastic variation"。 |
| **P1-2** | Python 版本差距 (3.13.12 vs ≥3.9) | ✅ 已解决 | Manuscript L103: "Python ≥3.10" ✓。Cover Letter L19: "Python (≥3.10)" ✓。MANIFEST L48: "P1-2: Python >=3.10 (pyproject.toml)" ✓。Repro Guide L9: "Python: 3.13.12" (实测环境) ✓。三处文档一致声明 ≥3.10 最低要求。 |
| **P1-3** | 缺少环境锁定文件 (requirements.txt) | ✅ 已解决(有保留) | MANIFEST L14: "E1-1 Dockerfile/runtime: requirements.txt + Repro Guide section 2 covers env setup"。Manuscript L103: "A Dockerfile is provided in the repository"。但 Repro Guide 正文未明确提到 requirements.txt 文件名或 `pip install -r requirements.txt` 命令（仅 L22 `pip install -e .`）。文件可能存在于 GitHub repo 但文档引用不完整（见 New-m2）。 |
| **P1-4** | TCGA 结论表述顺序需调整 | ✅ 已解决 | Manuscript L64: "a notable observation, **at bulk RNA-seq resolution**, was that tumors appeared more transcriptionally homogeneous" — 限定语已前置 ✓。L97 Discussion 全面讨论三种替代解释 ✓。 |
| **P1-5** | SES 非正态分布下应补充非参数替代 | ✅ 已解决(软修复) | Manuscript L26: "SES is interpreted as a non-parametric descriptive statistic complementing the permutation P-value, not as a parametric test statistic such as Cohen's d" ✓。L42 同样声明 ✓。Supp SN 3.4 (L71) 重申。修复方式为"重新定性"SES 为非参数描述统计量，而非新增独立非参数指标。这是可接受的但偏软的修复。 |
| **P1-6** | TCGA k_n floor 对 ω 值的影响需量化 | ✅ 已解决 | Manuscript L97 (Discussion): "in all 5 cancer types, the aggregate tumor-versus-normal k_n reached the floor value of 1 × 10⁻⁴, compared to mean k_n of 0.048–0.073 in single-cell datasets" — 明确量化了 floor 效应对 TCGA ω 值的膨胀机制 ✓。 |
| **P1-7** | 缺失神经元排除分析的理由说明 | ✅ 已解决 | Manuscript L74: "Neurons were excluded because the supercluster_term annotation does not resolve the extensive neuronal subtype heterogeneity (glutamatergic, GABAergic, dopaminergic, etc.)... Treating neurons as a single cell class would violate the same-cell-type assumption" ✓。理由充分。 |
| **P1-8** | Bergmann glia 1 个 Strong signal 归属不清 | ✅ 已解决 | Manuscript L88-89 新增 "Bergmann glia: cerebellar molecular topography" 专题段落 ✓。明确声明 "Bergmann glia had the lowest global ω (2.37) and **no Strong signals**" ✓。astrocyte CBL vs CBV 信号归属为 astrocyte 而非 Bergmann glia ✓。 |

### P2 修复（19/19 声称已解决）

MANIFEST L11-44 逐项列出 E1-1~E1-6 (6/6)、E2-1~E2-6 (6/6)、E3-1~E3-6 (6/6)、E4-1~E4-7 (7/7)。抽查验证：

- **E1-1** (Dockerfile/runtime): Manuscript L103 提及 Dockerfile ✓
- **E1-2** (CELLxGENE version): Manuscript L29, L31 引用 CZ CELLxGENE Discover ✓
- **E1-3** (Abstract calibration): Abstract 含 "mean ω = 6.67, 95% bootstrap CI [4.12, 9.33]" ✓
- **E1-4** (Spell check): 未发现拼写错误 ✓
- **E1-5** (Parameter table): 参数表存在于 Repro Guide L298-326（但位置错误，见 New-M1）
- **E1-6** (Repro Guide complete): Repro Guide 25,350 bytes，覆盖所有数据集 ✓
- **E4-1** (Abstract ≤200 words): MANIFEST 声明 195 词 ✓（NAR 限制 ≤200）
- **E4-7** (Embedded tables): Tables1-2 独立为 Table1-2.docx ✓

---

## 3. P0/P1/P2 逐项验证

### 已验证通过的项目

**P0-1 (Strong candidate 计数)**: 
- Manuscript L81: "identified 30 (0.09%) threshold-passing candidates: Astrocyte (6), oligodendrocyte (10), microglia (10), fibroblast (1), and vascular cells (3)"
- 算术验证: 6+10+10+1+3 = 30 ✓
- 后文一致性: "16 of these 30 candidates reached the permutation P-value floor" + "The remaining 14 threshold-passing candidates (10 microglia, 1 fibroblast, 3 vascular)" = 16+14 = 30 ✓
- MANIFEST L57: "6+10+10+1+3=30" ✓
- MANIFEST L72: "30 Strong, 16/30... 14/30" ✓

**P0-2 (MANIFEST FDR 声明)**:
- MANIFEST L58: "P0-2: MANIFEST FDR statement: 'No formal FDR'" ✓
- Manuscript L81: "formal FDR correction is not applicable" ✓
- Supp SN 3.3 (L68): "precluding meaningful Benjamini-Hochberg FDR correction" ✓
- Repro Guide §5.3c (L166): "precluding meaningful BH-FDR correction" ✓
- **残留问题**: MANIFEST L72 仍写 "16/30 FDR-significant descriptive" — "FDR-significant" 与 "No formal FDR" 自相矛盾（见 New-m1）

**P0-3 (校准因子 CI)**:
- 5 处位置全部确认 CI [4.12, 9.33]:
  1. Abstract (L11): "mean ω = 6.67, 95% bootstrap CI [4.12, 9.33]"
  2. Introduction (L18): "empirical calibration baseline 6.67, 95% bootstrap CI [4.12, 9.33]"
  3. Methods/Statistical reporting (L42): "mean ω = 6.67 (95% bootstrap CI [4.12, 9.33], B = 10,000 resamples)"
  4. Discussion (L93): "mean ω = 6.67 (95% bootstrap CI [4.12, 9.33])"
  5. Limitation #17 (L100): "95% bootstrap CI [4.12, 9.33]"
- Limitation #17 内容验证: 解释 global HVG vs per-pair DE 方案差异 ✓、1.62× / 0.71× 因子偏移 ✓、rank-based 鲁棒性论证 ✓、calibrate_omega() 函数 ✓

**P1 全部 8 项**: 见上表，全部通过验证 ✓

### v26 遗留问题验证

- **A-m2** (图形摘要 "selective"): SVG 搜索无 "selective" 残留 ✓ (v26→v32 已修复)
- **A-m3** (图形摘要 "neutral"): SVG 搜索无 "neutral" 残留 ✓ (v26→v32 已修复)
- **N2** (Cohen's d → SES): 正文仅出现 "Cohen's d" 作为对比参照 ("not as a parametric test statistic such as Cohen's d")，非作为 CKI 效应量名称使用 ✓

---

## 4. 算法正确性评估

### 4.1 核心数学推导 ✅

**JS divergence** (Supp SN 1.1, L18):
- JS(p,q) = ½ D(p||m) + ½ D(q||m), m = ½(p+q) — 标准公式 ✓
- Base-2 对数, range [0,1] ✓
- Supp SN 3.11 (L85): "the base does not affect omega since it cancels in the ratio" — 数学正确 ✓

**Softmax normalization** (Manuscript L22; Supp SN 1.2):
- p_i = exp(x_i) / Σ exp(x_j) ✓
- log1p 预变换缓解 softmax 饱和 ✓

**k_n/k_f 定义** (Manuscript L22; Supp SN 1.2-1.3):
- k_n = JS(softmax(μ_A[H]), softmax(μ_B[H])) — HK 基因子集 ✓
- k_f = JS(softmax(μ_A[I]), softmax(μ_B[I])) — identity 基因子集 ✓
- HK 基因从 I 中显式排除 → k_n/k_f 独立性 ✓

**ω 比值** (Manuscript L22):
- ω = k_f/k_n ✓
- ω_cal = ω/6.67 — 经验校准 ✓
- k_n floor = 1e-4 (Algorithm 1 L7; Supp SN 1.1; Repro Guide L311) — 一致 ✓

### 4.2 基因集选择策略 ✅

| 数据集 | k_n 方案 | k_f 方案 | 位置 |
|--------|----------|----------|------|
| Mouse full matrix (Fig.2) | global HK | global HVG 2,000 | Repro Guide §3.2, L303 |
| Mouse pilot (calibration) | global HK | per-pair top-200 DE | Repro Guide L304 |
| Human (Tabula Sapiens) | global HK | per-pair top-200 DE | Repro Guide L305 |
| TCGA | global HK | per-pair top-200 DE | Repro Guide L305 |
| Brain (Siletti) | **per-pair** HK | per-pair top-200 DE | Repro Guide L323 |

跨文档一致性验证: Manuscript L47/L51/L56, Supp SN 1.3/3.7, Repro Guide §3.2 — 全部一致 ✓

### 4.3 统计推断实现 ✅

**Permutation test** (Manuscript L26; Supp SN 1.5; Algorithm 1):
- H0: 两群体来自相同分布 ✓
- B = 1,000 (4 个数据集) / B = 10,000 (residual model) ✓
- P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) — one-sided, +1 pseudocount ✓
- SES = (ω_obs − μ_null)/σ_null ✓
- BH-FDR within each dataset (cell-type level) ✓

**Bootstrap CI** (Manuscript L42; Supp SN 3.2):
- B = 10,000 pair-level resampling, 2.5th/97.5th percentiles ✓
- 明确区分 CI (precision of point estimate) vs permutation test (hypothesis testing) ✓

**One-sided test justification** (Supp SN 3.10):
- "our hypothesis is directional" ✓
- Low-tail test for Strong candidates: P = (count(null_residual ≤ observed) + 1)/(B+1) ✓

### 4.4 ω 解释框架 ✅

- Ka/Ks 类比局限性透明声明 (Manuscript L16, L93, L99; Supp SN 1.4) ✓
- ω < 1, ≈1, >1 作为 operational thresholds 而非 selection regime claims ✓
- 校准因子跨方案转移性在 Limitation #17 中全面讨论 ✓
- calibrate_omega() 函数供用户自行验证 ✓

### 4.5 跨文档参数一致性验证

| 参数 | Manuscript | Supplementary | Repro Guide | MANIFEST | 一致性 |
|------|:----------:|:-------------:|:----------:|:--------:|:------:|
| ω baseline | 6.67 | 6.67 | 6.67 | 6.67 | ✅ |
| CI [4.12, 9.33] | 5处 | 1处 | — | 2处 | ✅ |
| B (permutation) | 1,000 | 1,000 | 1,000 | 1,000 | ✅ |
| B (bootstrap CI) | 10,000 | 10,000 | 10,000 | — | ✅ |
| B (residual null) | 10,000 | 10,000 | 10,000 | — | ✅ |
| P-value floor | 9.99×10⁻⁵ | 9.99×10⁻⁵ | 9.99e-5 | — | ✅ |
| Floor saturation | 36.3% | 36.3% | 36.3% | — | ✅ |
| Brain pairs | 31,764 | 31,764 | 31,764 | — | ✅ |
| Strong candidates | 30 | 30 | 30 | 30 | ✅ |
| k_n floor | 1e-4 | 1e-4 | 1e-4 | — | ✅ |
| Random seed | 42 | — | 42 | — | ✅ |
| k_n CV (brain) | 97.35% | 97.35% | 97.35% | — | ✅ |
| Python ≥ | 3.10 | — | 3.13.12 (env) | 3.10 | ✅ |
| HK genes (ref) | 1,130 | 1,130 | 1,130 | — | ✅ |
| HK matched (brain) | 1,115 | — | — | — | ✅ |
| HK matched (human) | — | 1,129 | — | — | ✅ |

**注**: HK 基因匹配数因数据集而异（HRT Atlas 参考 1,130 → Siletti 匹配 1,115, Tabula Sapiens 匹配 1,129），这是正常的数据匹配差异，非不一致。

---

## 5. 复现性评估

### 5.1 Repro Guide 结构审查

| 章节 | 内容 | 评估 |
|------|------|:----:|
| §1 Software Environment | Python 3.13.12, 包版本, 系统要求, 数据依赖 | ✅ 完整 |
| §2 CKI Algorithm Definition | JS 公式, softmax, k_n/k_f 定义 | ✅ 正确 |
| §3 Gene Set Selection | HK 来源, HVG/DE 方案, per-pair k_n 说明 | ✅ 清晰 |
| §4 Data Sources & Preprocessing | 4 数据集详细处理步骤 | ⚠️ 数据源不一致 (见 New-M2) |
| §5 Statistical Testing | Bootstrap, FDR, Phase B/C/D 升级 | ✅ 完整 |
| **§6 Parameter Summary** | **标题 + 一行文字，无参数表** | ❌ **空 (见 New-M1)** |
| §7 Output Files | 所有输出文件路径 | ✅ 完整 |
| §8 Reproducibility Checklist | 22 项检查项 | ✅ 完整 |
| (末尾) Parameter table | 参数表实际位于 L298-326 | ⚠️ 位置错误 |

### 5.2 Phase B/C/D 升级验证

**§5.3 Phase B Statistical Upgrades** (L153-170):
- a. Adaptive permutation analysis (C-S1): B=1,000 充分性验证 ✓
- b. Bootstrap CIs (C-S2): B=10,000, pair-level resampling ✓
- c. Permutation null for residual model (C-S3): B=10,000, 36.3% at floor ✓
- d. Omega distribution characterization (C-S5): skewness, kurtosis, normality tests ✓

**§5.4 Phase C Methodological Reinforcement** (L171-184):
- a. Calibrated omega (C-M1): ω_cal = ω/6.67, calibrate_omega() 函数 ✓
- b. JS dimensionality invariance (C-M2): Dirichlet simulation, ratio=1.001 ✓
- c. Pair-specific k_n variability (C-M3): CV=97.35%, ρ=-0.027 ✓

**§5.5 Phase D Interpretation Corrections** (L185-214):
- 14 项文本修订 (HK neutrality, TCGA reframing, paired analysis, sample size, PAM50, one-sided test, method comparison, BH-FDR, simulation ground truth, parameter justification, omega 8.01 vs 14.36, cross-species, cover letter, figure legends) — 全部验证通过 ✓

### 5.3 代码/环境要求验证

- Python ≥3.10: Manuscript L103, Cover Letter L19 ✓
- Dockerfile: Manuscript L103 "A Dockerfile is provided in the repository" ✓
- requirements.txt: MANIFEST L14 声称存在，但 Repro Guide 正文未明确引用 ⚠️
- Random seed 42: Repro Guide L35, L299 ✓
- Runtime: Manuscript L39 "under 5 minutes" (single pair), "72 core-hours" (brain) ✓
- GitHub repo: https://github.com/zhanglknt/CKI-cell-type-identification (L19, L101, L103) ✓
- Zenodo DOI: 10.5281/zenodo.15670808 (L103) ✓
- CKI version: v0.3.1 (L18, L101, L103) ✓

---

## 6. 新发现问题

### Critical: 0

### Major: 2

#### New-M1: Repro Guide Section 6 (Parameter Summary) 为空

**位置**: Repro Guide L216-217

**描述**: Section 6 标题为 "Parameter Summary"，正文仅有一行 "All parameters used in the reported analyses:"，随后立即跳到 Section 7 (Output Files)。实际的参数表（包含 27 个参数及其值和使用场景）位于文档末尾 L298-326，在 Section 8 (Reproducibility Checklist) 之后，不属于任何编号章节。

**影响**: 读者按章节阅读时会在 Section 6 找到空内容，可能错过完整参数表。这对可复现性有实际影响——参数表是复现实验的关键参考。

**建议**: 将 L298-326 的参数表移入 Section 6 内（L217 之后），使其成为有内容的章节。

#### New-M2: 数据源声明在 Repro Guide 与正文间不一致

**位置**: 
- Repro Guide L72: "Source: https://github.com/czbiohub-sf/tabula-muris"
- Repro Guide L88: "Source: https://github.com/czbiohub-sf/tabula-sapiens"
- Repro Guide L118: "Source: https://github.com/linnarsson-lab/snRNA_brain_atlas"
- vs. Manuscript L103: "Tabula Muris data: GEO accession GSE109774"
- vs. Manuscript L29: "accessed via CZ CELLxGENE Discover"
- vs. Manuscript L31: "from CZ CELLxGENE Discover (collection ID: 283d65eb-...)"

**描述**: Repro Guide §4 中三个数据集的 Source 字段指向 GitHub 仓库，而正文 Data availability 段落指向 GEO / CZ CELLxGENE Discover。虽然两个来源都指向同一数据，但访问路径不同（GitHub 原始文件 vs GEO/CELLxGENE 标准化处理版本），可能导致下载的文件格式和内容细节不同。

**影响**: 可复现性风险——不同来源的预处理版本可能存在差异。

**建议**: 在 Repro Guide 中统一使用与正文一致的数据源声明，或在 §4 中注明 "GitHub repo provides raw data; GEO/CELLxGENE provides the processed version used in this study"。

### Minor: 5

#### New-m1: MANIFEST "FDR-significant descriptive" 术语自相矛盾

**位置**: MANIFEST L72

**描述**: "Residual Model: 30 Strong, 16/30 FDR-significant descriptive, 14/30 non-significant" — 使用 "FDR-significant" 修饰语，但 MANIFEST L58 和正文明确声明 "No formal FDR"。如果 FDR correction is not applicable，信号不能被称为 "FDR-significant"，即使附加 "descriptive" 限定词。

**建议**: 改为 "16/30 reached P-value floor (descriptive evidence), 14/30 non-significant (P ≥ 0.76)"。

#### New-m2: requirements.txt 在 Repro Guide 中未明确引用

**位置**: MANIFEST L14 声称 "requirements.txt + Repro Guide section 2 covers env setup"

**描述**: Repro Guide §1.2 仅给出 `pip install -e .` 命令，未提及 requirements.txt 文件。§2 标题为 "CKI Algorithm Definition"，实际是算法描述而非环境配置。MANIFEST 的描述不准确。

**建议**: 在 Repro Guide §1.2 添加 "Alternatively: `pip install -r requirements.txt`" 并修正 MANIFEST 对 section 编号的引用。

#### New-m3: Supplementary SN 3.11 中 P-value 精度不一致

**位置**: Supp L85

**描述**: "minimum P = 0.001" — 四舍五入到 0.001，而正文 L41 和 Repro Guide L158 使用精确值 9.99×10⁻⁴ (= 1/1001)。

**建议**: 统一为 "9.99 × 10⁻⁴ (= 1/(B+1) = 1/1001)"。

#### New-m4: 脑区细胞类型列表不一致

**位置**: Manuscript L31 vs L74

**描述**: L31 列出 9 个非神经元类别（OPCs 含 committed 合并为 110,454），L74 列出 10 个类别（OPCs 和 committed OPCs 分开）。L75 的 ω 数据也分开报告（OPCs ω=7.65, committed OPCs ω=3.17）。核数总计 888,263 需要验证：L31 的 9 类总和约 886,222，差值 ~2,041 应为 Bergmann glia 核数（L31 列出 Bergmann glia 但未给核数）。

**建议**: 在 L31 中也列出 committed OPCs 的核数，或明确标注 "10 classes" 并为每类给出核数。

#### New-m5: MANIFEST E1-1 section 引用错误

**位置**: MANIFEST L14

**描述**: "E1-1 Dockerfile/runtime: requirements.txt + Repro Guide section 2 covers env setup" — Section 2 实际标题是 "CKI Algorithm Definition"，环境配置在 Section 1 (Software Environment)。

**建议**: 改为 "Repro Guide section 1 covers env setup"。

---

## 7. 综合评分与建议

### 评分明细

| 维度 | v26 | v28 (推估) | v32 | Δ (v28→v32) | 说明 |
|------|:---:|:----------:|:---:|:-----------:|------|
| 算法正确性 | 9.0 | 9.0 | **9.2** | +0.2 | 数学推导无误，无新算法问题；跨方案校准 Limitation #17 全面 |
| 参数一致性 | 7.0 | 8.0 | **8.8** | +0.8 | 跨文档参数一致性大幅提升；CI 5 处完整；残留 Minor 术语问题 |
| 复现指南完整性 | 7.5 | 8.0 | **8.3** | +0.3 | Phase B/C/D 完整；§6 空白和参数表位置错误扣分 |
| 文档技术准确性 | 7.5 | 8.0 | **8.5** | +0.5 | 图形摘要术语清除；数据源不一致扣分 |
| **加权综合** | **8.0** | **8.4** | **8.7** | **+0.3** | 算法稳健，文档一致性持续改进 |

### 评分理由

**+0.3 提升**来自：
1. P0-3 校准因子 CI + Limitation #17 全面修复 (+0.15)
2. P1-2/P1-3 Python ≥3.10 + Dockerfile/requirements.txt (+0.05)
3. P1-1/P1-7/P1-8 脑区分析清晰度提升 (+0.05)
4. 图形摘要 "selective"/"neutral" 术语清除 (+0.05)
5. P2 19/19 全部解决 (+0.05)

**扣分项**：
1. Repro Guide §6 空白 + 参数表位置错误 (−0.15)
2. 数据源声明不一致 (−0.10)
3. MANIFEST 术语/引用 Minor 问题 (−0.05)

### 提交建议

**推荐行动**: 修复 New-M1 和 New-M2 后即可提交 NAR。5 个 Minor 问题建议在 revision 阶段处理。

**Desk reject 风险评估**: 极低。算法核心正确，P0/P1/P2 全部声称已解决，文件齐全，Abstract 195 词（≤200）。New-M1 和 New-M2 是可复现性问题而非方法学错误，不构成 desk reject 理由。

**预计修复后评分**: ~9.0/10（修复 New-M1 + New-M2 后）

### 修复优先级

| 优先级 | 编号 | 描述 | 预计时间 |
|:------:|------|------|----------|
| **Major 1** | New-M1 | 将参数表移入 Repro Guide §6 | ~10 min |
| **Major 2** | New-M2 | 统一 Repro Guide 与正文的数据源声明 | ~15 min |
| Minor 1 | New-m1 | MANIFEST L72 "FDR-significant" → "P-value floor" | ~5 min |
| Minor 2 | New-m2 | Repro Guide §1.2 添加 requirements.txt 引用 | ~5 min |
| Minor 3 | New-m3 | Supp SN 3.11 P-value 精度统一 | ~2 min |
| Minor 4 | New-m4 | 脑区细胞类型列表统一为 10 类 | ~5 min |
| Minor 5 | New-m5 | MANIFEST L14 section 引用修正 | ~1 min |

---

**Critical: 0 | Major: 2 | Minor: 5**

*v32 是历次版本中完成度最高的。算法核心自 v26 以来保持正确，v28→v32 的改进集中在文档一致性和可复现性补强。两个 Major 问题（Repro Guide §6 空白 + 数据源不一致）均为文档层面，不影响科学结论。建议快速修复后提交。*
