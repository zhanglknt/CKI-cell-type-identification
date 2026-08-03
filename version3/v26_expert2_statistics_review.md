# 专家2：统计学与数据分析审稿报告 — CKI v26

**Reviewer**: E2 — 统计学与数据分析专家
**Date**: 2026-08-02 (更新于同日，补充 EVT/FDR MANIFEST 不一致分析)
**Manuscript**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling
**Target Journal**: Nucleic Acids Research
**Files reviewed**: CKI_NAR_Submission_v26 (Manuscript, Supplementary, MANIFEST_v26, v25 expert panel synthesis)
**Review baseline**: v25 score: 7.0/10

---

## 1. 总体评估

**v26 评分: 7.2/10** (v25: 7.0/10, +0.2)

v26 是 v25 的 P0+P1 修复版本，重点清理了 N2（Cohen's d→SES 残留）和 N4（neutral 术语残留）。N2 修复现已完全完成（6 处→0 处残留），N4 图注术语清理充分。其他修复（N1/N3/N8/N6/N9）验证通过。

**关键发现：EVT 方法被移除，MANIFEST 过时。** v26 版稿件中零处提及 "EVT"、"GPD" 或 "extrapolat"——v25 的核心 EVT/GPD 外推方法已被完全移除。脑残差模型现在使用纯置换 P 值 + 描述性解释（"FDR not applicable"）。这是与 v25 的根本方法学差异，但 MANIFEST_v26.txt 仍声称 "BH-FDR across 31,764 EVT-extrapolated P-values" 和 "16/30 significant (FDR<0.05)"——与实际文本直接矛盾。

从统计学角度看，v26 的描述性方法**更透明、更保守**，但放弃了 v25 通过 EVT 建立的正式 FDR 控制。"descriptive evidence" 比 "FDR-controlled discovery" 弱一个层级。两种方法得出相同的生物学结论（16 astrocyte + oligodendrocyte 信号），但统计声明的强度不同。

### 评分变化理由

| 变化项 | 评分影响 |
|--------|----------|
| N2 Cohen's d → SES 100%清理（6 处→0 处） | +0.3 |
| N4 neutral→constrained 图注修复 | +0.1 |
| EVT 移除：BH-FDR → 描述性 P 值（方法论降级） | −0.3 |
| N7 EVT 诊断：EVT 移除后无意义，非修复 | −0.1（N7 声明误导） |
| Limitation #12：跨方案校准问题透明标注 | +0.1 |
| MANIFEST-text EVT/FDR 不一致（文档 bug） | −0.0（非统计，阻塞） |

---

## 2. 重大发现：EVT 方法移除与 MANIFEST-text 不一致 🚨

### 2.1 事实核实

| 来源 | EVT/GPD 提及数 | FDR 声明 |
|------|:--:|------|
| v26 Manuscript (205 行) | **0** | "FDR correction **is not applicable**"（L35, L81, L103, L104） |
| v26 Supplementary (110 行) | **0** | "**precluding** meaningful BH-FDR correction"（L68, L69） |
| MANIFEST_v26.txt | 多次 | "BH-FDR across 31,764 **EVT-extrapolated** P-values, 16/30 **significant (FDR<0.05)**" |

结论：版稿件 + 补充材料中无 EVT/GPD/extrapolat 提及——EVT 方法已被完全移除。MANIFEST 仍声称 EVT 正在使用。

### 2.2 v25 → v26: 脑残差模型统计方法变更

| 维度 | v25 方法 | v26 方法 |
|------|---------|---------|
| P 值计算 | Permutation B=10,000 | Permutation B=10,000（相同） |
| Floor 处理 | EVT/GPD 外推（11,541 次 GPD 拟合） | **无处理**——接受 floor |
| 多重检验 | BH-FDR m=31,764 (EVT-extrapolated P) | **FDR "not applicable"** |
| 统计声明 | "16/30 **statistically significant** at FDR<0.05" | "16/30 **descriptive evidence** of deviation" |
| 非显著信号 | P≥0.76, q=1.0 | P≥0.76（无 q 值） |
| 核心结论 | 16 astrocyte+oligo 显著 | 16 astrocyte+oligo floor-reaching（相同生物学，较弱统计） |

### 2.3 统计学评估

v26 的描述性方法在统计学上 **正确且诚实**，原因如下：

1. **P 值地板确实阻碍了 FDR**：36.3% 信号共享 P=9.99×10⁻⁵，BH-FDR 无法区分具有区分度的显著信号
2. **替代方法（EVT）有自身的假设**：GPD 拟合需要重尾分布假设和足够大的超阈值样本，11,541 次独立 GPD 拟合的可靠性从未被验证（v25 的 N2-S）
3. **二元区分已在置换层面足够**：16 个 floor 信号（B=10,000 次置换中无一次 null 超过观测），14 个信号 P≥0.76——这是一个基于客观标准的清晰定性分离
4. **效应量才是关键**：残差是最小值（16 个 floor = 前 16 个最小残差），解释权重落在效应量上

然而，将 "FDR < 0.05 significant" 降级为 "descriptive evidence" 是一个 **实质性的统计声明降级**。在生物学背景下，16/14 的分离仍然具有说服力——所有 16 个 floor 信号来自 astrocyte 和 oligodendrocyte（两种具有明确独立发育证据的细胞类型），而 14 个非显著信号来自 microglia/vascular/fibroblast（三种无独立验证的细胞类型）。

### 2.4 N7（EVT GPD 诊断）状态

MANIFEST 声称 "N7 — Supplementary SN 3.3: EVT GPD fit diagnostics reference added"。因为版稿件中不存在 EVT 方法，N7 **无意义**——无法为不存在的方法添加拟合诊断。MANIFEST 不应将 N7 标记为已修复。

### 2.5 建议

**P0 — MUST FIX**: 更新 MANIFEST_v26.txt 以反映实际的统计方法：
- 删除所有提及 "EVT"、"GPD"、"EVT-extrapolated" 和 "FDR<0.05"（在残差模型上下文中）
- 将残差模型的状态更新为 "30 Strong candidates, permutation-based descriptive validation. 16/30 reached P-value floor (P=9.99×10⁻⁵), 14/30 showed no evidence (P≥0.76)"
- 将 N7 标记为 "Moot — EVT approach removed, GPD diagnostics not applicable"
- 将 C1 描述更新为 "C1: BH-FDR m=31,764 corrected; EVT/GPD approach removed in favor of descriptive permutation P-values"

---

## 3. N2 修复验证：Cohen's d → SES 全局清理 ✅ 100%完成

（不变，同第一版审稿）

---

## 4. N4 修复验证：neutral → constrained 术语清理 ✅

（不变，同第一版审稿）

---

## 5. 其他 v25→v26 修复验证

| Fix | 描述 | v26 状态 |
|:---:|------|:--:|
| N1 | Supplementary 标题 → Baseline-Normalized | ✅ |
| N3 | Table 1 102/5,151 对齐 | ✅ |
| N6 | Repro Guide brain k_n 描述 | ✅ |
| N7 | EVT GPD 诊断 | ❌ 无意义（EVT 已移除） |
| N8 | Limitations 编号修复 | ✅ |
| N9 | Brain PMI 讨论 | ✅（非统计维度） |

---

## 6. Bootstrap/置换检验设计评估 ✅

v26 方法部分（行 26, 41）中 B=1,000 充分性的定量论证保持不变且正确。单侧检验论证清晰。P = (count+1)/(B+1) 公式正确。术语精度可接受。

**脑残差模型**：B=10,000 标签置换，P = (count(null_residual ≤ observed_residual) + 1)/(B + 1)，单侧检验（检测相对于乘法零模型的异常低 ω）。这是标准的置换检验设计。

---

## 7. 多重检验校正评估（更新）

### 7.1 校正总体方案

| 级别 | 数据集 | m | 方法 | 状态 |
|------|----------|:--:|------|:--:|
| Cell-type bootstrap | Mouse | 15 | BH-FDR | ✅ |
| Cell-type bootstrap | Human | 17 | BH-FDR | ✅ |
| Cell-type bootstrap | Brain | 10 | BH-FDR (10/10 significant) | ✅ |
| Cell-type bootstrap | TCGA | 5 | Descriptive only | ✅ |
| Residual model | Brain (31,764 对) | n/a | FDR "not applicable"，描述性 | ⚠️（见 7.2） |

### 7.2 残差模型：FDR 不存在

v26 在 4 处（Manuscript）+ 2 处（Supplementary）一致声明 FDR "not applicable/precluded"。这是在 EVT 移除后唯一诚实的处理。"Descriptive evidence" 不如 "FDR < 0.05 significant" 有力，但数学上无法绕过。

---

## 8. 效应量报告评估 ✅

不变。SES 术语 100%一致，定义准确（"standardized mean difference rather than a parametric test statistic"，行 42）。

---

## 9. ω 分布特性评估 ✅

不变。右偏度（brain 2.22），Shapiro-Wilk/D'Agostino-Pearson 分层检验，非参数检验辅助——全部充分。

---

## 10. 样本量与统计功效评估

不变。校准 n=6（CV≈60%），TCGA n=2-5（仅描述性），小亚组标注——全部透明处理。新 Limitation #12（行 104）承认跨方案校准因子缺乏验证。

---

## 11. P 值报告一致性 ✅

不变。全文一致，单侧/双侧区分清晰，SES 术语统一。

---

## 12. 新发现问题（更新）

### N1-Sv26 — MANIFEST-text EVT/FDR 不一致 🚨 P0 阻塞

见第 2 节。MANIFEST 声称 EVT+FDR 仍然存在，但版稿件中 EVT 已被完全移除。MANIFEST 需要更新以匹配实际的统计方法。

### N2-Sv26 — EVT 移除后 N7 无意义 🟡 中等

见第 2.4 节。MANIFEST 不应声称 N7 已修复（"EVT GPD fit diagnostics reference added"），因为版稿件中无 EVT 方法可供诊断。

### N3-Sv26 — "descriptive evidence" 统计声明的局限性 🟡 中等

v26 从 "16/30 statistically significant at FDR < 0.05"（v25）切换为 "16/30 descriptive evidence of deviation from the multiplicative null model"（v26，行 35）。虽然统计学上诚实，但支撑脑分析核心生物学结论的统计声明较弱。

**建议**：增强基于效应量的论证以加强描述性声明：
1. 报告 16 个 floor 信号的残差范围（~0.202-0.292）相对于 Strong 层阈值（<0.3）的分布——提供关于 floor 信号在 Strong 层空间内分布的连续效应量视角
2. 报告 floor 与非 floor Strong 候选之间的残差分离（这隐含了统计分离，即使 P 值无法区分）
3. 添加灵敏度分析：如果使用 B=100,000 置换，有多少强候选会达到 floor？（如果是 0，floor 不是硬限制，而是当前 B 选择下的一种测量伪影）

### N4-Sv26 — "bootstrap permutation" 语义歧义 🟢 轻微

（同原始 N3-Sv26）

---

## 13. 统计学方法总评（更新）

### 13.1 优点

1. **N2 100% 修复**：SES 术语在所有文档中一致
2. **统计诚实度**：EVT 移除和 "FDR not applicable" 是诚实的选择，避免了使用不充分验证的方法
3. **置换检验框架健全**：B=1,000 充分性论证，方向性假设清晰
4. **非正态性处理充分**：三层防护（正态检验 + 非参数 + 置换）
5. **样本量限制透明**：所有限制均已承认
6. **细胞类型级 BH-FDR 正确**：m=10（脑）、m=17（人类）、m=15（小鼠）

### 13.2 不足

1. **MANIFEST-text 不一致**：声称 EVT+FDR，但文本使用描述性 P 值——**文档 bug**
2. **脑残差模型统计支持较弱**："Descriptive evidence" < "FDR-controlled discovery"
3. **校准 n=6（CV≈60%）**：结构性限制
4. **跨方案校准因子未验证**：Limitation #12 承认但未量化
5. **No per-test P-value table**

---

## 14. 评分（更新）

### 14.1 评分分解

| 维度 | v25 | v26 | Δ | 理由 |
|------|:--:|:--:|:--:|------|
| Cell-type BH-FDR | 8.5 | 8.5 | 0 | 细胞类型级 m 值保持正确 |
| Residual model inference | 8.5 (EVT+FDR) | 7.0 (descriptive) | −1.5 | EVT 移除，无正式 FDR |
| Permutation design | 8.0 | 8.5 | +0.5 | 更清晰的论证 |
| Effect size reporting | 6.0 | 8.5 | **+2.5** | SES 术语 100%一致 |
| EVT diagnostics | 6.0 | n/a | — | EVT 移除，维度关闭 |
| Bootstrap reporting | 7.0 | 7.5 | +0.5 | 诚实度提升 |
| P-value consistency | 8.5 | 9.0 | +0.5 | SES 统一 |
| Multiple-testing description | 8.0 | 8.0 | 0 | 描述简化但更一致 |
| Calibration adequacy | 5.5 | 5.5 | 0 | n=6 结构性问题 |
| **加权总分** | **7.0** | **7.2** | **+0.2** | |

### 14.2 与历史版本对比

| 维度 | v22 | v25 | v26 | v25→v26 Δ |
|------|:--:|:--:|:--:|:--:|
| C1 / Cell-type BH-FDR | 4.0 | 8.5 | 8.5 | 0 |
| C1 / Residual model inference | 4.0 | 8.5 (EVT+FDR) | 7.0 (descriptive) | −1.5 |
| M5 / SES | 5.0 | 6.0 | 8.5 | **+2.5** |
| M7 / Bootstrap null | 6.0 | 8.0 | 8.5 | +0.5 |
| M20 / k_n variability | 5.0 | 9.0 | 9.0 | 0 |
| Bootstrap reporting | 6.5 | 7.0 | 7.5 | +0.5 |
| Calibration n=6 | 5.5 | 5.5 | 5.5 | 0 |
| **总分** | **6.0** | **7.0** | **7.2** | **+0.2** |

### 14.3 达标评估

| NAR 统计要求 | v25 | v26 | 说明 |
|---------------|:--:|:--:|------|
| 多重检验校正 | ✅ | ⚠️ | 细胞类型级 ✅；残差模型缺乏正式 FDR |
| P 值报告规范 | ⚠️ | ✅ | SES 100%一致 |
| 效应量报告 | ⚠️ | ✅ | SES 定义准确，全面一致 |
| 置换检验设计 | ✅ | ✅ | B 足够，论证清晰 |
| 非独立性处理 | ⚠️ | ✅ | 诚实，描述性定位 |
| 拟合诊断 | ❌ | n/a | 无 EVT → 无需诊断 |
| 校准充分性 | ⚠️ | ⚠️ | n=6 + CV≈60% |
| **MANIFEST-text 一致性** | ✅ | ❌ | EVT/FDR 声明错误 |

---

## 15. 建议（更新）

### P0 — 提交前必须修复（阻塞）

1. **MANIFEST EVT/FDR 更新**：替换 v25-era EVT 声明，使用实际的描述性置换 P 值方法（15 分钟）
2. **从 MANIFEST 中删除或修正 N7**："EVT removed" 而非 "fixed"（5 分钟）

### P1 — 强烈建议（增强统计透明度）

3. **增强基于效应量的论证**：残差范围、B 灵敏度分析（30 分钟）
4. **跨方案校准验证**：Tabula Sapiens split-half 与 DE 方案（1 小时）
5. **Per-test P-value/SES 表**（15 分钟）

### P2 — 建议改进

6. **"bootstrap" vs "permutation" 术语区分**（5 分钟）

---

## 16. 总结

v26 是 v25 的混合版本——在术语一致性方面（N2: Cohen's d → SES，100% 完成）取得了重要进展，但通过移除 EVT 方法改变了脑分析中的统计方法，而未在 MANIFEST 中更新文档。

**统计学底线**：v26 的描述性方法在统计学上正确且诚实——比 v25 更有原则，但统计声明较弱。"descriptive evidence" 文本与 16/14 分离之间的内部一致性很强：同一篇论文中，所有 astrocyte 和所有 oligodendrocyte 强候选都达到 P 值下限，但没有一个 microglia/vascular/fibroblast 候选达到。论点的真实统计力量在于效应量（残差 < 0.3）和生物学可验证性（独立发育证据），而非 P 值。

**关键的提交前修复**：MANIFEST_v26.txt 必须更新以准确反映实际的统计方法。声称不存在的方法（EVT/FDR）是误导性的，可能会在编辑或审稿中引起问题。修复后，版稿件已准备好投稿。

**v26 评分: 7.2/10** (v25: 7.0/10, +0.2)

修正 MANIFEST 不一致后（P0），预计评分: 7.2/10（评分反映实际的统计严谨性，但 MANIFEST bug 是文档问题，不改变统计评估）。

---

*审稿人: E2 — 统计学与数据分析*
*审稿日期: 2026-08-02 (更新)*
