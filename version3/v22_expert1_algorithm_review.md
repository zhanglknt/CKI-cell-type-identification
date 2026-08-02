# 专家1：算法与方法学审稿报告 — CKI v22

**Reviewer**: E1 — 算法方法与计算实现专家
**Date**: 2026-08-01
**Manuscript**: CKI: Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling at Single-cell Resolution
**Target Journal**: Nucleic Acids Research (Methods)
**Files reviewed**: CKI_NAR_Submission_v22.zip (22 files, 2.5 MB)
**Review baseline**: v20→v21→v22 incremental. v20 expert score: 5.5/10

---

## 1. Overall Assessment

**v22 Score: 6.0/10** (v20: 5.5/10, +0.5)

v22 是一个精准的增量修复版本。唯一实质性变化是修复了我在 v20 审稿中标记的 **C2（k_n floor 参数表缺失）**。修复本身正确——复现指南参数表新增了 `k_n floor (minimum) = 1e-4` 行，位于 `k_n scaling (alpha)` 之后，与 `cki/core.py:242` 的 `kn_min = 1e-4` 一致。

但这是 v20 7 个 Critical 中最简单的一个（单行文档补全）。我标记的另外两个 Critical——**C1（残差模型 BH-FDR q值疑误）**和 **C3（Mouse k_n 方案矛盾）**——仍然未修复。这两个问题的算法含义远重于 C2。

### 评分变动理由

| 维度 | v20 | v22 | 变动原因 |
|------|-----|-----|----------|
| 算法正确性 | 5 | 5 | C1（BH-FDR）和 C3（Mouse方案）未修复 |
| 文档完整性 | 5 | 6 | C2 修复，参数表现在列出完整保护参数 |
| 代码质量 | 6 | 6 | 无代码变更 |
| 复现性 | 5 | 6 | k_n floor 现在文档化，复现者不再遗漏 |

---

## 2. v22 变更审核

### 2.1 C2 修复验证 [PASS]

**修复内容**：`100_gen_reproducibility_docx.js` 参数表新增：
```
k_n floor (minimum) | 1e-4 | all analyses
```

**验证**：
- 值与 `cki/core.py:242` (`kn_min = 1e-4`) 一致 ✓
- 位置合理（紧接 `k_n scaling (alpha)`） ✓
- 未与 `Epsilon (omega ratio) = 1e-9` 混淆（v20 报告中的问题是两个参数曾被合并讨论） ✓

**残留问题**：参数表现在有两类"epsilon"——`k_n floor = 1e-4` 和 `Epsilon (omega ratio) = 1e-9`。两者的描述词不同（"floor" vs "epsilon"），不会混淆。但建议在复现指南正文中也解释 `k_n floor` 的作用机制（当前只解释了 epsilon 的伪计数作用），而非仅在参数表中列出。

---

## 3. v20 遗留 Critical Issues 状态

| v20 Issue | 描述 | v22 状态 | 备注 |
|-----------|------|----------|------|
| C1 | 残差模型 BH-FDR q值疑误 | **未修复** | 仍报告 q=2.75e-4，标准 BH 计算应为 q~0.198 |
| **C2** | **k_n floor 参数表缺失** | **✅ 已修复** | 复现指南参数表已添加 |
| C3 | Mouse k_n 方案矛盾 | **未修复** | 稿件"per-pair" vs 复现指南"global" 仍然矛盾 |
| C4 | HK中性假设根基不足 | 未修复 | 生物学问题，非算法范围 |
| C5 | OPC阴性对照可能是模型产物 | 未修复 | 混合问题 |
| C6 | 标题措辞矛盾 | 未修复 | 格式问题 |
| C7 | NAR格式缺失 | 未修复 | 格式问题 |

**C1 和 C3 的持续存在是我维持算法评分 5/10 的主要原因。** C1 是数学正确性问题，C3 是文档与实现一致性问题——两者都是算法方法学专家的核心关切。

---

## 4. Major Issues (v20 遗留)

我标记的 v20 Major Issues 在 v22 中均未处理：
- **M1**: 校准因子跨方案适用性未验证 ✓ C2 修复不影响此问题
- **M3**: "Global k_n" 描述歧义（标量 vs 矩阵）
- **M4**: DE gene 选择（top-200 by |mu_A-mu_B|）循环膨胀
- **M6**: 跨数据集 omega 不可比（与 C3 部分相关）
- **M9**: 置换检验中 mu_ct/mu_pair 是否重新计算不明确
- **M11**: 维度不变性模拟测试了错误偏倚源
- **M12**: 补充材料误写 mouse k_f 为 top-200 DE
- **M14**: 归一化策略跨数据集不同未讨论可比性
- **M15**: "absolute-deviation test" 未在复现指南中定义

---

## 5. Novelty Evaluation

与 v20 评价无变化。CKI 的核心算法创新（双基因集 JS 散度归一化）仍然成立。C2 修复不涉及算法变更。

---

## 6. Recommendations

### Must-fix (提交前)
1. **C1 — BH-FDR 验证**：最高优先级。运行实际代码，确认 m 值，若 m=31,764 则所有信号不显著
2. **C3 — Mouse k_n 方案统一**：确认实际使用的方案，统一稿件和复现指南描述

### Strongly recommended
3. **k_n floor 的作用解释**：在复现指南 Section 3.1 或 Section 6 添加一段说明 kn_min 何时触发及其影响

### Recommended improvements
4. 参数表中 "Epsilon (omega ratio) = 1e-9" 可改名为 "JS pseudocount epsilon" 以与 k_n floor 明确区分

---

## 7. Summary

v22 修复了标记中最简单的 Critical，方向正确。但要达到 NAR 算法方法学标准，**C1 和 C3 是阻塞项**——C1 决定脑分析核心结论是否成立，C3 影响校准基线的可信度。两者修复后算法评分可从 6.0 提升至 7.0+。

**v22 评分: 6.0/10** | v20: 5.5/10 | +0.5（C2 文档修复）
