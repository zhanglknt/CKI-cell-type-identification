# 专家4：稿件质量与期刊策略审稿报告 — CKI v22

**Reviewer**: E4 — 稿件质量与期刊策略专家
**Date**: 2026-08-01
**Manuscript**: CKI: Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling at Single-cell Resolution
**Target Journal**: Nucleic Acids Research (Methods)
**Files reviewed**: CKI_NAR_Submission_v22.zip (22 files, 2.5 MB)
**Review baseline**: v20 expert score: 7.8/10

---

## 1. Overall Assessment

**v22 Score: 8.0/10** (v20: 7.8/10, +0.2)

v22 修复了 v20 中标记的 7 个 Critical 之一（C2: k_n floor 参数表）。修复方式简洁、正确、可验证。但我在 v20 中标记的另外 3 个 Critical（C6 标题措辞、C7 NAR 格式缺失）和 6 个 Major Issues 仍未处理。

评分微升 +0.2 反映复现指南完整性的边际提升——参数表现在列出了所有数值保护参数，这对审稿人的复现信任度有正面影响。但提升幅度有限，因为 C7（NAR 格式）中的 3 个必需元素缺失仍是硬性格式要求。

### 评分变动理由

| 维度 | v20 | v22 | 变动原因 |
|------|-----|-----|----------|
| 稿件撰写质量 | 8 | 8 | 无文本变更（仅复现指南） |
| Cover Letter | 8 | 8 | 未变更 |
| 图表质量 | 8 | 8 | 继承自 v21 |
| 复现指南完整性 | 7 | 8 | C2 修复：k_n floor 已文档化 |
| 格式合规 | 6 | 6 | C7（Keywords/Running Title/OS）仍未修复 |
| 期刊策略 | 8 | 8 | 无变化 |

---

## 2. v22 变更审核

### 2.1 C2 修复验证 [PASS]

复现指南 `CKI_NAR_Reproducibility_Guide.docx` 的 Section 6 Parameter Summary 新增：
```
k_n floor (minimum) | 1e-4 | all analyses
```

**格式验证**：
- 值 1e-4 与源代码一致 ✓
- 不与 Epsilon (omega ratio) = 1e-9 混淆（v20 中两个参数曾被合并讨论） ✓
- 位置合理（紧接 k_n scaling） ✓

**期刊策略视角评价**：此修复对 NAR 审稿人的信任建立有正面效果。计算方法的参数文档化是 NAR Methods 类稿件的核心要求之一。k_n floor 现在被显式列出，审稿人无需翻源代码即可验证 omega 计算的边界行为。

---

## 3. v20 遗留 Critical Issues（期刊策略相关）

| v20 Issue | 描述 | v22 状态 | 严重性 |
|-----------|------|----------|--------|
| C6 | 标题"Selective"与稿件自述矛盾 | **未修复** | 审稿人第一印象扣分 |
| C7 | NAR 格式缺失（Keywords/Running Title/OS）| **未修复** | NAR 投稿形式要求，可能被 desk reject |

### C7 详情（NAR 硬性格式要求）

NAR 投稿系统要求以下字段，v22 仍然缺失：
1. **Keywords**: 4-6 个关键词，位于 Abstract 之后
2. **Running Title**: ≤50 字符的短标题
3. **OS 字段**: 软件可用性声明中须包含操作系统（当前仅列出 Programming language: Python 3.8+）

---

## 4. v20 遗留 Major Issues（期刊策略相关）

| v20 Issue | 描述 | v22 状态 |
|-----------|------|----------|
| M17 | Discussion 重复 Results 内容，需压缩 ~20% | 未修复 |
| M19 | 参考文献编号顺序跳跃 | 未修复 |

---

## 5. 提交可行性分析

### 当前状态：不建议直接提交

| 障碍 | 类型 | 修复难度 | 时间 |
|------|------|----------|------|
| C7 NAR 格式缺失 | 硬性要求 | 低 | 1-2h |
| C6 标题措辞 | 审稿人感知 | 低 | 30min |
| C4 HK 中性假设 | 生物学 valid | 中 | 1-2d |
| C1 BH-FDR 验证 | 统计 valid | 中-高 | 1-3d |
| C5 OPC 验证逻辑 | 生物学 valid | 低 | 1-2h |

**预计时间**：修复所有 Critical (C1-C7) 需 3-5 个工作日。

### 若只修复格式问题 (C6-C7)

v22 + C6 + C7 修复 → 可以提交，但 C1（BH-FDR）和 C4（HK 中性假设）会在 peer review 中被审稿人抓住。建议至少修复 C1 和 C4 后再提交。

---

## 6. 期刊推荐（与 v20 一致）

| 排名 | 期刊 | IF (估) | fit | 接受概率 | 状态 |
|------|------|---------|-----|----------|------|
| 1 | **NAR** | ~16.6 | 8.0/10 | 30-40% | 首选（需修复 C1-C7） |
| 2 | **Bioinformatics** | ~5.8 | 8.5/10 | 40-50% | 最强备选 |
| 3 | **Cell Reports Methods** | ~3.0 | 8.0/10 | 35-40% | 方法学期刊 |
| 4 | **PLOS Computational Biology** | ~3.5 | 7.5/10 | 35-45% | 保险选项 |

---

## 7. Recommendations

### 提交前必须修复（格式硬性要求）
1. **C7 — NAR 格式补全**：Keywords (4-6个)、Running Title (≤50字符)、OS 字段 (如 "Linux, macOS, Windows")
2. **C6 — 标题调整**：建议 "Baseline-Normalized Transcriptomic Divergence as a Single-cell Resolution Metric of Cell-state Remodeling"

### 强烈建议修复（审稿人感知）
3. **C4 — HK 中性→约束假设重构**：E3 的生物学 critique 是可被 NAR 审稿人独立发现的
4. **M17 — Discussion 压缩**：移除与 Results 的重叠段落
5. **M19 — 参考文献顺序**：修复编号跳跃

---

## 8. Summary

v22 在复现指南完整性上有小幅但正确的提升（C2 修复）。作为期刊策略顾问，我必须指出：v22 仍缺少 NAR 投稿的必要格式要素（C7），这意味着**即使所有科学问题都解决了，稿件仍然会在投稿系统层面被 desk reject**。建议优先修复 C6 和 C7（最低时间成本，1-2 小时），然后处理 C1（BH-FDR）和 C4（HK 中性假设）等科学问题。

**v22 评分: 8.0/10** | v20: 7.8/10 | +0.2（复现指南完整性提升）
