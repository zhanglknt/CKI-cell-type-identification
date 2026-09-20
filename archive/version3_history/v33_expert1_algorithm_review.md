# CKI v33 独立审稿 — E1: 计算方法与可复现性

**审稿日期**: 2026-08-03
**评分**: 8.9/10 (v32: 8.7/10, Δ: +0.2)
**审稿文件**: CKI_NAR_Manuscript_fulltext.txt, CKI_NAR_Supplementary_fulltext.txt, CKI_NAR_Reproducibility_Guide_fulltext.txt, CKI_NAR_Cover_Letter_fulltext.txt, MANIFEST_v33.txt, Table1-2_fulltext.txt

---

## 1. 核心发现概要

v33 声称完成 4 Major + 20 Minor 共 24 项修复（MANIFEST L6）。经逐项验证，**实际完成情况为：1/4 Major 已修复，12/17 Minor 完全修复，5/17 Minor 部分修复**。MANIFEST 中 Phase C 标注 "17/17" 但仅列出 m4–m17 共 14 项，实际 Minor 总数为 17（3+14），而非声称的 20——存在计数错误。

算法核心数学（softmax → JS divergence → ω = k_f/k_n）自 v26 以来保持正确，v33 未引入新的算法问题。最实质性的改进是：v32 E1 的 New-M2（数据源声明不一致）已修复（M2），Repro Guide §4 现为每个数据集同时标注 GitHub 原始仓库和 GEO/CELLxGENE 处理版本。CV 从 60% 修正为 52%（m2）、P-value 精度从 0.001 修正为 9.99×10⁻⁴（m5）、requirements.txt 引用补入 Repro Guide §1（m4）、Abstract 术语软化（m8）、单侧检验局限性说明（m10）、P-value floor 替代解释（m11）、非神经元范围限制（m15）等 Minor 修复均验证通过。

**关键问题**：3 个声称的 Major 修复实际未完成：
- **M1 未修复**：Repro Guide §6 仍为空，参数表仍在 §8 之后（L301–329），未移入 §6
- **M3 未修复**：S3–S9 补充图在正文 Body 中未被引用（Grep 确认零匹配）
- **M4 未修复**：8 个孤儿参考文献中 7 个（refs 31–35, 40–41）仍未在正文被引用

此外，m6（脑区细胞类型 9→10）仅改数字未补条目，m9（Limitation #20）缺失（编号从 #19 跳至 #21），m17（"orthogonal"→"complementary"）仍有 2 处残留。

**Critical: 0 | Major: 3 (声称已修复但实际未修复) | Minor: 8 (含部分修复)**

---

## 2. v32→v33 修复验证

### Phase A — Major (实际 1/4 已修复)

| 编号 | MANIFEST 声称 | 验证结果 | 证据 |
|------|-------------|:--------:|------|
| **M1** | Repro Guide §6 参数表移入 | ❌ **未修复** | Repro Guide L218–220: §6 仅有标题 + 一行介绍 + "See Section 7..."。参数表实际位于 L301–329，在 §8 (Reproducibility Checklist, L273–299) 之后。与 v32 完全相同——§6 仍为空壳，参数表仍被遗弃在文档末尾。v33 仅在 L220 新增一句引导文字，但未执行实际的表格迁移。 |
| **M2** | 数据源声明统一 | ✅ **已修复** | Repro Guide §4.1 L72: "Source: https://github.com/czbiohub-sf/tabula-muris (raw data; GEO accession GSE109774 provides the processed version used in this study)" ✓。§4.2 L88: "Source: https://github.com/czbiohub-sf/tabula-sapiens (raw data; CZ CELLxGENE Discover provides the processed version used in this study)" ✓。§4.4 L118: "Source: https://github.com/linnarsson-lab/snRNA_brain_atlas (raw data; CZ CELLxGENE Discover provides the processed version used in this study)" ✓。三个数据集均同时标注 GitHub + GEO/CELLxGENE，与正文 L103 Data availability 一致。 |
| **M3** | S3–S9 补充图在正文引用 | ❌ **未修复** | Grep 搜索 manuscript body (L1–120) 中 "Supplementary Fig. S[3-9]" 返回 **零匹配**。正文实际引用的补充图为：S1 (L49)、S2 (L98)、S10 (L24)、S11 (L56)。S3–S9 仅出现在 Supplementary Figure legends 部分 (L124–130)，未在正文 Body 任何位置被引用。S3 (TCGA per-cancer matrices)、S4 (Method comparison)、S5 (Cross-organ raw data)、S6 (Brain regional details)、S7 (Developmental signature detection)、S8 (ω distribution)、S9 (Permutation null) 均为孤儿图。 |
| **M4** | 8 个孤儿参考文献已引用或移除 | ❌ **未修复** (7/8 仍孤儿) | Grep 搜索作者名确认：ref 31 (Shemer & Jung) — 仅出现在参考目录 L166，正文无引用 ❌；ref 32 (Menassa) — L167，正文无引用 ❌；ref 33 (Barry-Carroll) — L168，正文无引用 ❌；ref 34 (Schaffenrath) — L169，正文无引用 ❌；ref 35 (Jones 2023) — L170，正文无引用 ❌；ref 40 (Yang/PAML) — L175，正文无引用 ❌；ref 41 (Tan 2020) — L176，正文无引用 ❌；ref 44 (Bakken 2021) — L179，正文 L98 引用 "(44; Supplementary Fig. S2)" ✓。**7/8 孤儿参考文献仍未被引用**，且全部仍在参考列表中。 |

### Phase B — High-Consensus Minor (3/3 已修复)

| 编号 | MANIFEST 声称 | 验证结果 | 证据 |
|------|-------------|:--------:|------|
| **m1** | FDR 术语统一为 "P-value floor (descriptive)" | ✅ 已修复 | MANIFEST L54: "Residual Model: 30 Strong, 16/30 P-value floor (descriptive), 14/30 non-significant" ✓。v32 的 "FDR-significant descriptive" 自相矛盾已消除。 |
| **m2** | CV 60% → 52% | ✅ 已修复 | Manuscript L52: "The mean ω was 6.67 (median 6.46, range 1.59–12.16, CV ≈ 52%)" ✓。 |
| **m3** | Cover Letter "30 signatures" → "30 threshold-passing candidates (16 significant)" | ✅ 已修复 | Cover Letter L18: "30 threshold-passing candidates (16 statistically significant)" ✓。 |

### Phase C — Low-Consensus Minor (实际 14 项，声称 17/17)

**MANIFEST 计数错误**：Phase C 标注 "17/17" 但 m4–m17 共 14 项。Phase B (3) + Phase C (14) = 17 项 Minor，非声称的 20 项。MANIFEST L6 "4 Major + 20 Minor" 的 "20" 应为 "17"。

| 编号 | MANIFEST 声称 | 验证结果 | 证据 |
|------|-------------|:--------:|------|
| **m4** | requirements.txt 在 Repro Guide §1 引用 | ✅ 已修复 | Repro Guide L23: "Install (fixed dependencies): pip install -r requirements.txt" ✓。§1.2 同时提供 editable install 和固定依赖安装两种方式。 |
| **m5** | Supp P-value 精度 0.001 → 9.99e-04 | ✅ 已修复 | Supp L85: "minimum P = 9.99 × 10⁻⁴ (= 1/(B+1) = 1/1001)" ✓。与正文 L41 (9.99 × 10⁻⁴) 和 Repro Guide L160 一致。 |
| **m6** | 脑区细胞类型 9 → 10 | ⚠️ **部分修复** | L31: "10 major non-neuronal classes" — 数字已改为 10 ✓。但 L31 实际仅列出 **9 个类别**（astrocytes, oligodendrocytes, OPCs "110,454 total including committed", microglia, vascular, fibroblasts, ependymal, choroid plexus, Bergmann glia），committed OPCs 被打包进 OPCs 条目。L74 正确列出 10 个类别（含 committed OPCs 独立条目）。L31 与 L74 仍不一致：数字一致 (10) 但 L31 列表不完整。 |
| **m7** | MANIFEST "section 2" → "section 1" | ✅ 已修复 | v33 MANIFEST 已重构，不再包含 v32 的 "E1-1: Repro Guide section 2 covers env setup" 错误引用。环境配置正确指向 §1 (Software Environment)。 |
| **m8** | Abstract "two statistically significant" → "two with permutation support" | ✅ 已修复 | Manuscript L11 (Abstract): "30 cell-type developmental signatures spanning four biological mechanisms (two with permutation support)" ✓。避免了在 Abstract 中使用 "statistically significant" 的过度声明。 |
| **m9** | k_n floor TT/NN 量化 (Limitations #20) | ⚠️ **部分修复** | k_n floor 量化内容存在于 Discussion L97: "in all 5 cancer types, the aggregate tumor-versus-normal k_n reached the floor value of 1 × 10⁻⁴, compared to mean k_n of 0.048–0.073 in single-cell datasets" ✓。但 **Limitation #20 ("Twentieth") 不存在**——Grep 搜索 "Twentieth" 返回零匹配。Limitations 编号从 #19 (Nineteenth) 直接跳至 #21 (Twenty-first)。内容在 Discussion 中已有，但 MANIFEST 声称的 "Limitations #20" 未被创建。 |
| **m10** | 单侧检验局限性 (Limitations #18) | ✅ 已修复 | Manuscript L101: "Eighteenth, the one-sided permutation test (H1: ω_obs > ω_null) does not detect functional constraint (ω_obs < ω_null); users investigating bidirectional hypotheses should employ two-sided permutation tests, available via the direction parameter in the CKI package" ✓。 |
| **m11** | P-value floor 替代解释 (Limitations #19) | ✅ 已修复 | Manuscript L101: "Nineteenth, the residual model permutation test... An alternative interpretation is that the null distribution, constructed by shuffling cell-type labels within region pairs, is narrower than the true null because cell types differ in global plasticity; a null that accounts for cell-type-specific baseline plasticity could reduce the saturation rate" ✓。替代解释清晰且技术合理。 |
| **m12** | Cross-species Spearman r 在 Discussion 引用 | ⚠️ **部分修复** | Manuscript L98: "Preliminary cross-species validation using shared cell types between mouse and human atlases (44; Supplementary Fig. S2)" ✓ — 引用了 ref 44 和 S2。但 **Spearman r 数值未在正文明确给出**，仅 Supp Fig S2 图例 (L123) 提到 "with Spearman r and P-value"。MANIFEST 声称 "Cross-species Spearman r referenced in Discussion"，但正文仅引用图表未给出数值。 |
| **m13** | TCGA k_n floor 注释在 Results 部分 | ❌ **未修复** | Grep 搜索 "floor" 在 TCGA Results 部分 (L63–66) 无匹配。k_n floor 讨论仅在 Discussion L97，Results 部分未添加相关注释。 |
| **m14** | "Strong candidate" → "threshold-passing candidates" | ✅ 已修复 | Manuscript L81: "identified 30 (0.09%) threshold-passing candidates" ✓。L91: "Threshold-passing but non-significant signals" ✓。L98: "The 14 remaining threshold-passing candidates" ✓。术语在全文一致使用。 |
| **m15** | 非神经元范围限制 (Limitations #21) | ✅ 已修复 | Manuscript L101: "Twenty-first, the brain analysis was restricted to non-neuronal cell types because the supercluster_term annotation does not resolve neuronal subtype heterogeneity; this limits the generalizability of our brain regional findings to non-neuronal lineages" ✓。 |
| **m16** | 补充图编号 "Figure 8" → "S8" | ✅ 已修复 | Supplementary Figure legends (L122–133) 统一使用 "Supplementary Figure S1" 至 "S12" 格式 ✓。Supp SN 3.3 (L69): "Supplementary Figure S8" 和 "Supplementary Figure S9" ✓。 |
| **m17** | "orthogonal" → "complementary" (2 处) | ⚠️ **部分修复** | Grep 确认 "orthogonal" 仍在 2 处出现：① L77: "providing an **orthogonal** transcriptomic readout of migration history" (Discussion) ② L116: "confirming ω captures **orthogonal** information" (Figure 2 legend)。"complementary" 已在 L94 ("CKI answers a complementary question") 和 L96 ("CKI complements rather than replaces") 使用——可能是 m17 改了另外 2 处，但 L77 和 L116 的残留未处理。 |

**Phase C 汇总**：完全修复 9/14 (m4, m5, m7, m8, m10, m11, m14, m15, m16)；部分修复 4/14 (m6, m9, m12, m17)；未修复 1/14 (m13)。

---

## 3. 算法正确性评估

### 3.1 核心数学推导 ✅ (与 v32 一致，无变化)

**JS divergence** (Supp SN 1.1, L18):
- JS(p,q) = ½ D(p||m) + ½ D(q||m), m = ½(p+q) — 标准公式 ✓
- Base-2 对数, range [0,1] ✓
- Supp SN 3.11 (L85): "the base does not affect omega since it cancels in the ratio" — 数学正确 ✓

**Softmax normalization** (Manuscript L22; Supp SN 1.2):
- p_i = exp(x_i) / Σ exp(x_j) ✓
- log1p 预变换缓解 softmax 饱和 ✓

**k_n/k_f 定义** (Manuscript L22; Supp SN 1.2–1.3):
- k_n = JS(softmax(μ_A[H]), softmax(μ_B[H])) — HK 基因子集 ✓
- k_f = JS(softmax(μ_A[I]), softmax(μ_B[I])) — identity 基因子集 ✓
- HK 基因从 I 中显式排除 → k_n/k_f 独立性 ✓

**ω 比值与 floor** (Algorithm 1 L7; Supp SN 1.1; Repro Guide L314):
- ω = k_f/k_n ✓
- k_n floor = 1e-4 — 跨文档一致 ✓
- ε (pseudocount) = 1e-9 — 跨文档一致 ✓

### 3.2 基因集选择策略 ✅

| 数据集 | k_n 方案 | k_f 方案 | 一致性 |
|--------|----------|----------|:------:|
| Mouse full matrix (Fig.2) | global HK | global HVG 2,000 | ✅ |
| Mouse pilot (calibration) | global HK | per-pair top-200 DE | ✅ |
| Human (Tabula Sapiens) | global HK | per-pair top-200 DE | ✅ |
| TCGA | global HK | per-pair top-200 DE | ✅ |
| Brain (Siletti) | per-pair HK | per-pair top-200 DE | ✅ |

跨文档验证: Manuscript L47/L51/L56, Supp SN 1.3/3.7, Repro Guide §3.2 — 全部一致 ✓

### 3.3 统计推断实现 ✅

**Permutation test** (Manuscript L26; Supp SN 1.5; Algorithm 1):
- H0: 两群体来自相同分布 ✓
- B = 1,000 (4 个数据集) / B = 10,000 (residual model) ✓
- P = (count(ω_null ≥ ω_obs) + 1)/(B + 1) — one-sided, +1 pseudocount ✓
- SES = (ω_obs − μ_null)/σ_null — 非参数描述统计量 ✓
- BH-FDR within each dataset (cell-type level) ✓
- 单侧检验合理性论证 (Supp SN 3.10) + Limitation #18 新增 ✓

### 3.4 跨文档参数一致性验证

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
| CV (calibration) | 52% | — | — | — | ✅ (m2 修正) |
| Python ≥ | 3.10 | — | 3.13.12 (env) | 3.10 | ✅ |
| HK genes (ref) | 1,130 | 1,130 | 1,130 | — | ✅ |

---

## 4. 新发现问题

### Critical: 0

### Major: 3 (声称已修复但实际未完成的 MANIFEST 条目)

#### New-M1: MANIFEST 声称 M1 已修复但 Repro Guide §6 仍为空

**位置**: Repro Guide L218–220 (§6) vs L301–329 (参数表实际位置)

**描述**: MANIFEST L8 声称 "M1: Repro Guide section 6 parameter table relocated"。但实际验证：§6 (L218–220) 仅有标题 "6. Parameter Summary" 和一行引导文字 "All parameters used in the reported analyses:" 加一句 "The above parameters, when used with the exact random seed..."。参数表（27 个参数，L301–329）仍位于 §8 (Reproducibility Checklist) 之后，不属于任何编号章节。v33 仅在 L220 新增了一句过渡文字，但未执行实际的表格迁移。

**影响**: 这是 v32 E1 review 的 New-M1 的原样残留。MANIFEST 声称已修复但实际未修复，损害 MANIFEST 的可信度。读者按章节阅读时仍会在 §6 找到空内容。

**建议**: 将 L301–329 的参数表移入 §6 内（L220 之后），使其成为有内容的章节。

#### New-M2: MANIFEST 声称 M3 已修复但 S3–S9 仍为孤儿图

**位置**: Manuscript body L1–120

**描述**: MANIFEST L10 声称 "M3: S3-S9 supplementary figures cited in manuscript body"。Grep 搜索 "Supplementary Fig. S[3-9]" 在 manuscript body 返回零匹配。S3 (TCGA per-cancer matrices)、S4 (Method comparison performance)、S5 (Cross-organ conservation raw data)、S6 (Brain regional analysis details)、S7 (Developmental signature detection)、S8 (ω distribution characterization)、S9 (Permutation null distribution) 均未在正文 Body 任何位置被引用，仅出现在 Supplementary Figure legends 部分。

**影响**: 7 个补充图无法被读者从正文定位，降低可复现性。

**建议**: 在正文相应 Results 段落添加 "(Supplementary Fig. S3)" 等引用。预计每个图 1 处引用即可。

#### New-M3: MANIFEST 声称 M4 已修复但 7/8 孤儿参考文献仍为孤儿

**位置**: Manuscript reference list L166–176, L179

**描述**: MANIFEST L11 声称 "M4: 8 orphan references (31-35, 40-41, 44) cited or removed"。Grep 搜索作者名确认：
- ref 31 (Shemer & Jung 2024, microglial colonization) — 仅在 L166 参考目录，正文无引用 ❌
- ref 32 (Menassa et al. 2022, microglia spatiotemporal dynamics) — L167，正文无引用 ❌
- ref 33 (Barry-Carroll et al. 2023, microglia colonize developing brain) — L168，正文无引用 ❌
- ref 34 (Schaffenrath et al. 2024, BBB heterogeneity) — L169，正文无引用 ❌
- ref 35 (Jones et al. 2023, meningeal fibroblast origins) — L170，正文无引用 ❌
- ref 40 (Yang 2007, PAML 4) — L175，正文无引用 ❌
- ref 41 (Tan et al. 2020, microglial regional heterogeneity) — L176，正文无引用 ❌
- ref 44 (Bakken et al. 2021, comparative motor cortex) — L98 正文引用 "(44; Supplementary Fig. S2)" ✓

7 个参考文献仍为孤儿。这些文献涉及 microglia biology (refs 31–33, 41)、BBB heterogeneity (ref 34)、fibroblast development (ref 35) 和 molecular evolution (ref 40)，与 Discussion 中 microglia/vascular/fibroblast 段落和 Ka/Ks 类比段落直接相关，应有引用位置。

**影响**: 参考列表中的孤儿文献影响学术规范性和 NAR 投稿合规性。

**建议**: 在 Discussion 相应段落引用 refs 31–35 (microglia/BBB/fibroblast biology)、ref 40 (PAML in Ka/Ks discussion)、ref 41 (microglial heterogeneity)；或移除未引用的参考。

### Minor: 5

#### New-m1: MANIFEST Minor 计数错误 (声称 20 实为 17)

**位置**: MANIFEST L6

**描述**: MANIFEST L6 标题写 "Third-Batch Expert Panel Fixes (4 Major + 20 Minor)"，L1 写 "4 Major + 20 Minor ALL resolved"。但 Phase B 列出 m1–m3 (3 项)，Phase C 列出 m4–m17 (14 项)，总计 3+14=17 项 Minor。Phase C 标注 "(17/17)" 也有误——m4–m17 为 14 项，应为 "(14/14)"。

**建议**: 将 "20 Minor" 修正为 "17 Minor"；Phase C "(17/17)" 修正为 "(14/14)"。

#### New-m2: Limitation #20 缺失 (编号 19 → 21 跳跃)

**位置**: Manuscript L101

**描述**: Limitations 编号从 "Nineteenth" 直接跳至 "Twenty-first"，"Twentieth" 不存在。Grep 搜索 "Twentieth" 返回零匹配。MANIFEST m9 声称 "k_n floor TT/NN quantified (in Limitations #20)"，但 Limitation #20 从未被创建。k_n floor 量化内容存在于 Discussion L97，但未按 MANIFEST 声称的形式作为独立 Limitation 列出。

**建议**: 在 #19 和 #21 之间插入 "Twentieth, in all 5 cancer types, the aggregate tumor-versus-normal k_n reached the floor value of 1 × 10⁻⁴..." 作为正式 Limitation #20。

#### New-m3: "orthogonal" 残留 2 处未替换

**位置**: Manuscript L77, L116

**描述**: MANIFEST m17 声称 "'orthogonal' → 'complementary' (2 occurrences)"。但 Grep 确认 "orthogonal" 仍在 L77 ("providing an orthogonal transcriptomic readout of migration history") 和 L116 ("confirming ω captures orthogonal information") 出现。可能 m17 改了另外 2 处（如 L94 "complementary question"、L96 "complements rather than replaces"），但这两处残留未处理。

**建议**: L77 改为 "complementary transcriptomic readout"；L116 改为 "confirming ω captures complementary information"。

#### New-m4: 脑区细胞类型 L31 列表与 L74 不一致

**位置**: Manuscript L31 vs L74

**描述**: L31 声称 "10 major non-neuronal classes" 但仅列出 9 个条目（committed OPCs 被打包进 OPCs: "110,454 total including committed"）。L74 正确列出 10 个独立条目。m6 修改了数字 (9→10) 但未补充 committed OPCs 为独立列表条目。

**建议**: 在 L31 拆分为 "oligodendrocyte precursors (XXX nuclei)" 和 "committed oligodendrocyte precursors (XXX nuclei)" 两个独立条目，使列表与 L74 一致。

#### New-m5: TCGA k_n floor 未在 Results 部分注释

**位置**: Manuscript L63–66 (TCGA Results)

**描述**: MANIFEST m13 声称 "TCGA k_n floor note in Results section"。Grep 搜索 "floor" 在 TCGA Results 部分 (L63–66) 无匹配。k_n floor 讨论仅在 Discussion L97，Results 部分未添加。

**建议**: 在 TCGA Results 段落 (L64 或 L66) 添加 "Notably, the aggregate k_n in TCGA reached the floor value (1 × 10⁻⁴), contributing to elevated raw ω values (see Discussion)"。

---

## 5. 复现性评估

### 5.1 Repro Guide 结构审查

| 章节 | 内容 | 评估 |
|------|------|:----:|
| §1 Software Environment | Python 3.13.12, 包版本, requirements.txt, 系统要求 | ✅ 完整 (m4 已修复) |
| §2 CKI Algorithm Definition | JS 公式, softmax, k_n/k_f 定义 | ✅ 正确 |
| §3 Gene Set Selection | HK 来源, HVG/DE 方案, per-pair k_n 说明 | ✅ 清晰 |
| §4 Data Sources & Preprocessing | 4 数据集详细处理 + 双数据源声明 | ✅ 完整 (M2 已修复) |
| §5 Statistical Testing | Bootstrap, FDR, Phase B/C/D 升级 | ✅ 完整 |
| **§6 Parameter Summary** | **标题 + 一行文字，无参数表** | ❌ **仍为空 (M1 未修复)** |
| §7 Output Files | 所有输出文件路径 | ✅ 完整 |
| §8 Reproducibility Checklist | 22 项检查项 | ✅ 完整 |
| (末尾) Parameter table | 参数表仍位于 L301–329 | ❌ 位置错误 |

### 5.2 Phase B/C/D 升级验证

**§5.3 Phase B** (L155–170): C-S1 自适应置换分析 ✓ | C-S2 Bootstrap CIs ✓ | C-S3 残差模型置换零分布 ✓ | C-S5 ω分布特征化 ✓

**§5.4 Phase C** (L173–186): C-M1 校准 ω ✓ | C-M2 维度不变性 ✓ | C-M3 per-pair k_n 变异性 ✓

**§5.5 Phase D** (L187–216): 14 项文本修订全部验证通过 ✓

### 5.3 代码/环境要求验证

- Python ≥3.10: Manuscript L103, Cover Letter L19 ✓
- Dockerfile: Manuscript L103 ✓
- requirements.txt: Repro Guide L23 `pip install -r requirements.txt` ✓ (m4 已修复)
- Random seed 42: Repro Guide L37 ✓
- GitHub repo + Zenodo DOI: L103 ✓
- CKI version v0.3.1: L19, L101, L103 ✓

---

## 6. 问题汇总

| 严重性 | 编号 | 描述 | 来源 |
|:------:|------|------|------|
| **Major** | New-M1 | M1 声称已修复但 Repro Guide §6 仍为空，参数表仍在 §8 之后 | v32 New-M1 残留 |
| **Major** | New-M2 | M3 声称已修复但 S3–S9 补充图在正文 Body 零引用 | v33 新声称修复 |
| **Major** | New-M3 | M4 声称已修复但 7/8 孤儿参考文献仍未被引用 | v33 新声称修复 |
| Minor | New-m1 | MANIFEST Minor 计数错误 (声称 20 实为 17) | v33 新发现 |
| Minor | New-m2 | Limitation #20 缺失 (编号 19→21 跳跃) | m9 部分修复 |
| Minor | New-m3 | "orthogonal" 残留 2 处 (L77, L116) | m17 部分修复 |
| Minor | New-m4 | L31 列表 9 条目 vs L74 的 10 条目不一致 | m6 部分修复 |
| Minor | New-m5 | TCGA k_n floor 未在 Results 注释 | m13 未修复 |

---

## 7. 评分理由与建议

### 评分明细

| 维度 | v32 | v33 | Δ | 说明 |
|------|:---:|:---:|:---:|------|
| 算法正确性 | 9.2 | **9.2** | 0 | 数学推导无误，无新算法问题；Limitation #18/#19 增强统计透明度 |
| 参数一致性 | 8.8 | **9.0** | +0.2 | CV 修正 (m2)、P-value 精度统一 (m5)、FDR 术语修正 (m1)；残留 m6/m9 不一致 |
| 复现指南完整性 | 8.3 | **8.5** | +0.2 | requirements.txt 引用 (m4)、数据源统一 (M2)；§6 空白仍未修复 (M1) |
| 文档技术准确性 | 8.5 | **8.7** | +0.2 | Abstract 软化 (m8)、术语修正 (m14)；S3–S9 孤儿 (M3)、refs 孤儿 (M4)、"orthogonal" 残留 (m17) |
| **加权综合** | **8.7** | **8.9** | **+0.2** | 多项 Minor 修复实质有效，但 3 个 Major 声称修复未完成限制提升幅度 |

### 评分理由

**+0.2 提升来自**：
1. M2 数据源声明统一 — Repro Guide §4 三个数据集均双标注 GitHub + GEO/CELLxGENE (+0.08)
2. m1 FDR 术语修正 + m2 CV 修正 + m5 P-value 精度统一 — 跨文档一致性提升 (+0.05)
3. m4 requirements.txt 引用 + m8 Abstract 软化 + m10/m11 新增 Limitations (+0.05)
4. m14 术语统一 + m15 范围限制 + m16 图编号修正 (+0.02)

**未达 +0.5 以上的原因**：
1. M1 (Repro Guide §6 参数表) 声称已修复但实际未修复 — v32 Major 问题原样残留 (−0.10)
2. M3 (S3–S9 正文引用) 声称已修复但零引用 — 7 个补充图仍为孤儿 (−0.08)
3. M4 (孤儿参考文献) 声称已修复但 7/8 仍孤儿 — NAR 投稿合规风险 (−0.08)
4. MANIFEST 计数错误 + Limitation #20 缺失 + "orthogonal" 残留 (−0.04)

### 提交建议

**推荐行动**: 修复 3 个 Major (New-M1/M2/M3) 后可提交 NAR。5 个 Minor 建议在 revision 阶段处理。

**Desk reject 风险评估**: 低。算法核心正确，代码开源，数据可追溯。3 个 Major 问题均为文档层面（参数表位置、图引用、参考文献引用），不影响科学结论。但 MANIFEST 声称 "ALL resolved" 与实际不符，如果编辑核查 MANIFEST 声明可能产生信任问题。

**MANIFEST 可信度评估**: 24 项声称修复中，13 项完全通过验证，5 项部分通过，3 项未通过，3 项 Minor 计数有误。通过率约 54% (13/24)。建议作者重新核查 MANIFEST 声称。

### 修复优先级

| 优先级 | 编号 | 描述 | 预计工作量 |
|:------:|------|------|----------|
| **Major 1** | New-M1 | 将参数表移入 Repro Guide §6 (M1 实际修复) | ~10 min |
| **Major 2** | New-M2 | 在正文添加 S3–S9 引用 (M3 实际修复) | ~15 min |
| **Major 3** | New-M3 | 引用 refs 31–35/40/41 或移除 (M4 实际修复) | ~20 min |
| Minor 1 | New-m2 | 添加 Limitation #20 (k_n floor) | ~5 min |
| Minor 2 | New-m3 | 替换 L77/L116 "orthogonal" → "complementary" | ~2 min |
| Minor 3 | New-m4 | L31 拆分 committed OPCs 为独立条目 | ~5 min |
| Minor 4 | New-m5 | TCGA Results 添加 k_n floor 注释 | ~3 min |
| Minor 5 | New-m1 | MANIFEST 计数修正 "20" → "17" | ~1 min |

---

**Critical: 0 | Major: 3 (MANIFEST 声称已修复但实际未完成) | Minor: 5**

*v33 在 Minor 层面有实质改进（数据源统一、CV 修正、P-value 精度统一、requirements.txt 引用、Abstract 软化、Limitations 扩充），但 3 个 Major 修复声称 (M1/M3/M4) 未实际完成。算法核心自 v26 以来保持正确。建议作者完成 3 个 Major 的实际修复后提交，同时修正 MANIFEST 计数错误以恢复声明可信度。预计修复后评分 ~9.3/10。*
