# 专家3：生物学与单细胞基因组学审稿报告 — CKI v22

**Reviewer**: E3 — 生物学与单细胞基因组学专家
**Date**: 2026-08-01
**Manuscript**: CKI: Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling at Single-cell Resolution
**Target Journal**: Nucleic Acids Research (Methods)
**Files reviewed**: CKI_NAR_Submission_v22.zip (22 files, 2.5 MB)
**Review baseline**: v20 expert score: 6.0/10

---

## 1. Overall Assessment

**v22 Score: 6.0/10** (无变化)

v22 只有一个技术性文档修复（k_n floor 参数表补全），不涉及任何生物学内容变更。我在 v20 中标记的 2 个 Critical（C4 HK 基因中性假设、C5 OPC 阴性对照）和 6 个 Major Issues 在 v22 中均未处理。

从生物学角度看，v22 与 v20/v21 完全等同——作为生物学审稿人，我只能重申之前的关切。

---

## 2. C2 修复的生物学含义

**零影响。** k_n floor = 1e-4 是纯数值保护机制，不影响生物学解释。但 C2 修复揭示了一个有趣的潜在问题：文档化 k_n floor 之后，复现者可以自己验证 floor 对 omega 的驱动程度——特别是 TCGA 中 BRCA Luminal A 的 omega=344.5。如果该值由接近 floor 的 k_n 驱动，其生物学含义（"高度选择性重塑"）需要更谨慎的解读。

---

## 3. v20 遗留 Critical Issues（生物学相关）

### C4（E3-C1 · **未修复**）：HK基因"中性"基线假设生物学根基不足

这是 v20 审稿中我最关心的生物学问题。HK 基因处于强纯化选择下（GAPDH、ACTB、TUBB 高度保守），低表达方差是自然选择的**结果**，不是中性的**证据**。与 Ka/Ks 类比有根本性区别——同义位点的中性是遗传密码的机制属性，而非选择结果。

稿件 P96 的一句承认（"HK genes may be subject to stabilizing selection"）不足以解决问题。建议的修复方向：
- 将 "neutral baseline" → "constrained baseline" 或 "housekeeping expression background"
- 在 Discussion 中展开论述：CKI 测量的不是"偏离中性"，而是"相对于高约束基因集的表达分歧"
- 明确说明：CKI 在进化含义上与 Ka/Ks 不具可比性，是启发式类比而非严格的同源框架

### C5（E3-C2 · **未修复**）：OPC"阴性对照"可能是数学模型产物

OPC 产生 0 个 Strong 信号被作为验证。但 OPC 的全局 omega=7.65（第三高），接近总均值 8.01。残差模型的乘法结构使全局 omega 接近均值的细胞类型在结构上更难达到 Strong 层。0 个 Strong 信号至少部分是数学设计的结果——这不是对方法灵敏度的"验证"，而是其内部结构的一致性检验。

建议：
- 重新标记 OPC 为 "internal consistency check" 而非 "negative control validation"
- 讨论 omega 接近均值的细胞类型在残差模型下的预期行为

---

## 4. v20 遗留 Major Issues（生物学相关）

| v20 Issue | 描述 | v22 状态 |
|-----------|------|----------|
| M4 | k_n/k_f 基因集"独立性"仅为技术分离 | 未修复 |
| M8 | TCGA 转录趋同在 bulk 分辨率下存在替代解释 | 未修复 |
| M10 | 脑分析发育起源推断为相关性非因果 | 未修复 |
| M16 | 脑数据集死后间隔和细胞数不对称混杂 | 未修复 |
| M18 | 交叉器官排名 n<=3 占比高（10/17）| 未修复 |
| M20 | 微胶质细胞定殖波叙事在统计 caveat 之前 | 未修复 |

---

## 5. 生物学创新性评估

与 v20 评价无变化。CKI 的核心生物学主张——"功能基因表达分歧超过 HK 基线时指示细胞状态重塑"——在概念水平上是有价值的。但 C4（HK 中性假设根基）和 C5（OPC 验证逻辑）限制了"选择性重塑"这一生物学标签的合法性。

---

## 6. Recommendations

### 阻塞项 (生物学层面)
1. **C4 — HK 基因假设重构**：从 "neutral baseline" 改为 "constrained baseline"，并增加机制性讨论
2. **C5 — OPC 角色重新定位**：从 "negative control validation" 改为 "internal consistency check"

### 强烈建议
3. **M20 — 叙事结构调整**：统计 caveat 前置，避免微胶质细胞定殖波先入为主
4. **M8 — TCGA 替代解释讨论**：明确列出细胞组成、瘤周组织、RNA 质量等 confounders
5. **k_n floor 对 omega 生物学解读的影响**：报告 TCGA 高 omega 值的 floor 驱动程度

---

## 7. Summary

v22 对生物学内容无变更。我在 v20 中的 2 个生物学 Critical（C4、C5）仍然是向 NAR 投稿的实质性障碍。这两个问题不涉及代码或数据，是纯概念/叙事级别的修复，时间成本较低（约 2-3 天），但对审稿人接受度的影响巨大。

**v22 评分: 6.0/10** | v20: 6.0/10 | 无变化（无生物学内容变更）
