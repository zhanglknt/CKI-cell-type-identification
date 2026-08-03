# CKI v26 专家团综合审稿报告

**审稿日期**: 2026-08-02
**审稿团**: 4位独立专家（算法方法学 / 统计学与数据分析 / 生物学与单细胞基因组学 / 稿件质量与期刊策略）
**审稿对象**: CKI_NAR_Submission_v26.zip（27 文件，2.6 MB）
**delta 范围**: v25 → v26（P0 N1-N4 + P1 N6-N9 修复）
**对比基准**: v25 综合审稿（7.50/10）

---

## 1. 执行摘要

**v26 综合评分：加权平均 7.60/10**（v25: 7.50/10, +0.10）

| 专家 | 角色 | 评分 | 权重 | v25 评分 | Δ | 新发现 Critical | 新发现 Major |
|------|------|------|------|----------|------|:---:|:---:|
| E1 | 算法与方法学 | 8.0/10 | 25% | 7.5 | +0.5 | 0 | 1 (A-M1) |
| E2 | 统计学与数据分析 | 7.2/10 | 30% | 7.0 | +0.2 | 0 | 0 |
| E3 | 生物学与单细胞基因组学 | 7.5/10 | 25% | 7.5 | 0 | 0 | 2 (N1, N2) |
| E4 | 稿件质量与期刊策略 | 7.80/10 | 20% | 8.30 | −0.50 | 1 (N-E4-1) | 0 |
| **综合** | — | **7.60/10** | 100% | 7.50 | **+0.10** | **1** | **3** |

**核心结论**：v26 在 NAR 投稿准备方面取得了关键进展——N2（Cohen's d → SES）100%修复，N4（neutral 术语）彻底清理，N9（PMI 讨论）实质性扩展。然而，发现 1 个新 Critical 问题（Supplementary Figures S8-S12 缺失，desk reject 风险）和 3 个跨专家共识的 Major 问题（MANIFEST EVT/FDR 矛盾、Abstract/Introduction 脑分析过度解读、Limitations N8 新编号重复）。此外，v26 放弃了 v25 的 EVT 外推方案（改为描述性 P 值），但 MANIFEST 未同步更新。

**准备度评估**：~80%（v25: 82%, −2%）。修复全部 P0 后预计 85%，P0+P1 后预计 87%。

---

## 2. v25 → v26 变更追踪

### P0 修复（N1-N4）

| Issue | 描述 | E1 | E2 | E3 | E4 |
|-------|------|:--:|:--:|:--:|:--:|
| **N1** | Supplementary/Cover Letter 标题 "Selective" → "Baseline-Normalized" | ✅ | ✅ | ✅ | ✅ |
| **N2** | 全局 "Cohen's d" → "SES"（7处残留） | ✅ 0残留 | ✅ 100% | ✅ | ✅ |
| **N3** | Table 1 数值 99/4,851 → 102/5,151 | ✅ | ✅ | ✅ | ✅ |
| **N4** | "neutral" → "constrained baseline"（CKI 上下文） | ✅ 正文 ⚠️ 图形摘要残留 | ✅ | ✅ 完全 | ✅ |

### P1 修复（N6-N9）

| Issue | 描述 | E1 | E2 | E3 | E4 |
|-------|------|:--:|:--:|:--:|:--:|
| **N6** | Repro Guide brain k_n 描述修正 | ✅ | ✅ | — | ✅ |
| **N7** | EVT GPD 拟合诊断 | ❌ 声称未实现，EVT已移除 | ❌ moot | — | ✅ moot |
| **N8** | Limitations 编号重复 "Seventh" → "Eleventh" | ✅ | ✅ | ⚠️ 部分修复，新重复 | ⚠️ 部分修复 |
| **N9** | Brain PMI 讨论扩展 | ✅ | ✅ | ✅ 8.5/10 | ✅ |

### N8 详细分析（跨专家分歧）

E1/E2 验证"Seventh"→"Eleventh"替换成功，认为 N8 已修复。E3/E4 深入检查发现 line 103 已有 Eleventh 和 Twelfth，line 104 的替换引入了新的 Eleventh 和 Twelfth 重复。实际 Limitations 共 17 条但编号仅到 15，且 11 和 12 各出现两次。

---

## 3. 跨专家共识分析

### 最强共识（4/4 专家）

所有专家一致认为：
- **N2（Cohen's d → SES）100%修复**，全文档零 "Cohen" 残留。这是本轮最重要的改进，v25 最大的执行失误已被完全纠正
- **N1（Supplementary 标题）已修复**，三文档标题完全一致
- **N3（Table 1 数值对齐）已修复**，102 cell types / 5,151 pairs 全文一致

### 跨学科共识：MANIFEST EVT/FDR 矛盾（E1 + E2 + E4，共 3/4）

E1（算法）、E2（统计学）和 E4（期刊策略）独立发现了 MANIFEST 声称使用 "BH-FDR across 31,764 EVT-extrapolated P-values, 16/30 significant (FDR<0.05)"，但稿件正文和补充材料中所有 EVT/GPD 内容已被完全移除，改为 "FDR correction is not applicable" 的描述性 P 值方案。MANIFEST 的过时声明与实际正文直接矛盾。

**E2 的统计学评估**：v26 的描述性方法在统计学上更透明、更保守——放弃未充分验证的 EVT 外推，改为诚实的描述性定位。但 "descriptive evidence" 是比 "FDR < 0.05 significant" 更弱的统计声明。16/14 的分离在效应量（残差 < 0.3）和独立生物学验证方面仍然可靠，不改变生物学结论。

**E1 的算法评估**：v25 专家团批准的 EVT 方案在 v26 中被替换，但 MANIFEST 声称仍在用 EVT。这不是算法本身的问题，而是文档管理失误。

**E4 的投稿评估**：MANIFEST 声称不存在的方法（EVT/FDR）是误导性的。投稿前必须更新。

### 跨学科共识：S8-S12 缺失（E4，确认级别 = 1/4 发现，但 Critical 性质无争议）

E4 独立发现 Supplementary Figures S8-S12（ω 分布、置换零分布、维度不变性、k_n 变异性、校准 omega）未被打包进投稿包。稿件正文多处引用 S8-S12（line 24, 54, 56, 73, 75, 77），补充材料包含完整图注（line 134-137），但投稿包仅含 S1-S7。Repro Guide 确认文件存在于 `results/figures_final/ed_fig8-12.pdf`，仅需重命名并加入投稿包。

E1/E2/E3 在各自审稿中未检查文件完整性，但 E3 在审稿中确认了 S8-S12 的生物学必要性（ω 分布特征、置换检验 null distribution 等统计诊断）。

### 跨文档一致性问题汇总

| 不一致项 | 发现专家 | 严重程度 |
|----------|----------|:--------:|
| MANIFEST 声称 EVT/FDR vs 正文描述性 P 值 | E1, E2, E4 | 🔴 Major |
| S8-S12 文件缺失（正文引用 vs 投稿包无文件） | E4 | 🔴 Critical |
| Limitations 编号新的 Eleventh/Twelfth 重复 | E3, E4 | 🟡 Medium |
| Abstract/Introduction 脑分析 "four biological mechanisms" 过度解读 | E3 | 🟡 Medium |
| 图形摘要 SVG "selective" 残留 | E1 | ⚪ Minor |
| 图形摘要 SVG "neutral" 残留 | E1 | ⚪ Minor |
| Graphical Abstract 占位符文本未更新 | E4 | ⚪ Minor |
| Python 版本 3.8+ vs ≥3.9 | E4 | ⚪ Minor |
| TCGA ω 尺度异常仍未讨论 | E3 | 🟡 Medium |

---

## 4. 新发现问题汇总（合并去重，共 13 项）

### Critical（1 项，desk reject 风险）

| ID | 描述 | 发现专家 | 涉及文件 |
|----|------|----------|----------|
| **C1** | **Supplementary Figures S8-S12 缺失**。投稿包仅含 S1-S7，缺失 S8（ω分布）、S9（置换零分布）、S10（维度不变性）、S11（k_n变异性）、S12（校准omega）。正文多处引用这些图。 | E4 | 投稿包目录, 生成脚本 |

### Major（3 项，投稿前必须修复）

| ID | 描述 | 发现专家 |
|----|------|----------|
| **M1** | **MANIFEST EVT/FDR 矛盾**。MANIFEST 声称 "BH-FDR across 31,764 EVT-extrapolated P-values, 16/30 significant (FDR<0.05)"，但正文明确声明 "formal FDR correction is not applicable"。EVT 方法已在 v26 中移除完毕（全正文 0 处提及）。 | E1, E2, E4 |
| **M2** | **Abstract/Introduction 脑分析结论过度解读**。Abstract 声称 "four biological mechanisms"，但仅 2/4 有统计支持（DO + DS, astrocyte + oligodendrocyte）。Introduction 提到 "colonization route boundaries"（microglia, all P ≥ 0.76）和 "postnatal migration event"（fibroblast, P = 1.0）作为已检测信号。Results 和 Discussion 中表述是准确的。 | E3 |
| **M3** | **Limitations 编号新重复**。v25 的 "两个 Seventh" 被替换为 "两个 Eleventh + 两个 Twelfth"。Line 103 有 Eleventh(k_n/k_f gene set sizes)/Twelfth(hybrid scheme)；line 104 有 Eleventh(multiplicative residual model permutation)/Twelfth(calibration factor cross-scheme)。实际 17 条但编号仅到 15。 | E3, E4 |

### Medium（4 项）

| ID | 描述 | 发现专家 |
|----|------|----------|
| **Med1** | **N7 修复声称未实际实现**。MANIFEST 声称 "EVT GPD fit diagnostics reference added"，但 v26 已完全移除 EVT 方法（正文零提及）。应标记为 "moot" 而非 "fixed"。 | E1, E2 |
| **Med2** | **TCGA ω 尺度异常仍未讨论**。TCGA ω (344.5) 比单细胞数据 (8-14) 高 12-43 倍。v25 E3 审稿已提出，v26 仍未讨论原因（bulk averaging 压缩 k_n 导致 ω 膨胀）。 | E3 |
| **Med3** | **参考文献未按首次引用顺序编号（N5 残留）**。首次引用序列为 (16), (1), (2), (3), (32), (31), (5)... 严重不按顺序。NAR 编辑可能标记。 | E4 |
| **Med4** | **图形摘要 SVG "selective"/"neutral" 术语残留**。A-m2: graphical abstract 仍使用 "selective transcriptomic remodeling"（与标题 "Baseline-Normalized" 不一致）；A-m3: 使用 "neutral transcriptomic drift"（与 N4 精神不一致）。 | E1 |

### Minor（4 项）

| ID | 描述 | 发现专家 |
|----|------|----------|
| **m1** | **OPC 术语混用**。"internal consistency check"（header, Supplementary）vs "orthogonal validation"（正文, Discussion）。 | E3 |
| **m2** | **Python 版本声明不一致（N10 残留）**。Manuscript 说 3.8+，Cover Letter 说 ≥3.9。 | E4 |
| **m3** | **Graphical Abstract 占位符文本**。Manuscript line 9 仍为 "[A graphical abstract figure (landscape, 5:2 aspect ratio) will be provided separately.]"，但实际文件已在投稿包中。 | E4 |
| **m4** | **Oligodendrocyte "distinguish" 措辞过强**。CKI 检测的是低 ω 空间模式匹配发育边界，而非直接区分单细胞身份。建议改为 "detect the transcriptional boundary"。 | E3 |

### Observation（1 项，不阻塞）

| ID | 描述 | 发现专家 |
|----|------|----------|
| **O1** | **k_n floor (1e-4) 缺乏理论论证/敏感性分析**。建议补充 floor 值 (1e-3 / 1e-4 / 1e-5) 对 ω 分布影响的敏感性测试。 | E1 |

---

## 5. 各维度核心发现

### 5.1 方法学变更：EVT → 描述性 P 值

| 维度 | v25 | v26 | 变化 |
|------|-----|-----|------|
| P 值计算 | Permutation B=10,000 | 相同 | — |
| Floor 处理 | EVT/GPD 外推（11,541 次拟合） | 无处理，接受 floor | 降级 |
| 多重检验 | BH-FDR m=31,764 (EVT-extrapolated) | "FDR not applicable" | 降级 |
| 统计声明 | "16/30 significant at FDR<0.05" | "16/30 descriptive evidence" | 降级 |
| 非显著信号 | P≥0.76, q=1.0 | P≥0.76（无 q 值） | — |
| 生物学结论 | 相同（16 astrocyte+oligo） | 相同 | 不变 |

**E2 评估**：描述性方法在统计学上正确且诚实。"Descriptive evidence" 比 "FDR-controlled discovery" 弱，但 16/14 的分离在效应量和独立生物学验证方面仍然可靠。

### 5.2 最显著的改进

1. **N2 Cohen's d → SES（100%修复）**：v25 最大的执行失误（6-7 处残留）已完全纠正。E2 将此维度从 6.0 → 8.5（+2.5）。全文档零 "Cohen" 残留，"SES" 术语 100% 一致。
2. **N4 neutral 术语清理（完全修复）**：所有指代 CKI k_n/HK 基因的 "neutral" 均改为 "constrained baseline"。仅保留合法 Ka/Ks 上下文中的 "neutral"。
3. **N9 Brain PMI 讨论（实质性扩展）**：从 v25 的 1 句话扩展为完整段落，包含 PMI 区域异质性、细胞类型特异性敏感性、胶质细胞主导论点。

### 5.3 最显著的倒退

1. **S8-S12 缺失（新 Critical）**：5 张关键统计诊断图未打包。正文引用存在但文件不存在。desk reject 级别风险。
2. **MANIFEST EVT/FDR 矛盾（新 Major）**：v25 批准的 EVT 方案在 v26 中被移除，但 MANIFEST 未更新。
3. **Abstract/Introduction 脑分析过度解读（新 Major）**：声称 "four biological mechanisms" 但仅 2/4 有统计支持。

---

## 6. v22 → v26 评分维度演化

| 维度 | v22 | v25 | v26 | v22→v26 Δ |
|------|-----|-----|-----|------------|
| 算法正确性 | 5.0 | 8.0 | 8.0 | +3.0 |
| 统计严谨性 | 5.0 | 7.5 | 7.2 | +2.2 |
| 生物学框架 | 5.5 | 7.5 | 7.5 | +2.0 |
| 文档完整性 | 5.5 | 7.0 | 7.0 | +1.5 |
| 复现性 | 6.0 | 7.5 | 7.5 | +1.5 |
| 稿件质量 | 7.5 | 8.0 | 7.8 | +0.3 |
| **综合** | **6.40** | **7.50** | **7.60** | **+1.20** |

---

## 7. 期刊推荐更新

| 排名 | 期刊 | IF (估) | fit | v25 接受概率 | v26 接受概率 | 变化原因 |
|------|------|---------|-----|:--:|:--:|------|
| 1 | **NAR** | ~16.6 | 8.5/10 | 40-50% | **42-52%** | S8-S12 缺失需投稿前修复，否则下降至 30-35% |
| 2 | **Bioinformatics** | ~5.8 | 8.5/10 | 50-60% | **50-60%** | 无变化 |
| 3 | **Cell Reports Methods** | ~3.0 | 8.0/10 | 45-55% | **45-55%** | 无变化 |

**推荐**：NAR 首选。修复 P0 三项（S8-S12 + MANIFEST + Limitations 编号）后预计 48-55%。

---

## 8. 优先级行动方案

### P0 — 投稿前必须修复（阻塞项，~50 min）

| 优先级 | ID | 描述 | 估计时间 | desk reject 风险 |
|:--:|------|------|:--:|:--:|
| 🥇 | C1 | 补齐 Supplementary Figures S8-S12（5 个 PDF）并更新 MANIFEST | 30min | 🔴 高 |
| 🥈 | M1 | 更新 MANIFEST EVT/FDR 描述（移除 EVT，改为 descriptive） | 10min | 🟡 中 |
| 🥉 | M3 | 修复 Limitations 编号重复（line 104 旧条目 → Sixteenth/Seventeenth） | 5min | ⚪ 低 |
| 4 | m2 | 统一 Python 版本声明（Manuscript "3.8+" → "≥3.9"） | 5min | ⚪ 低 |

### P1 — 强烈建议（增强稿件，~1.5h）

| ID | 描述 | 估计时间 |
|------|------|:--:|
| M2 | Abstract/Introduction 脑分析结论修正（限定 "four biological mechanisms" 为 "two reaching statistical significance"） | 20min |
| Med1 | N7 状态修正（MANIFEST 中标注为 moot） | 5min |
| Med2 | TCGA ω 尺度讨论补充（1-2 句 bulk averaging 效应） | 10min |
| Med4 | 图形摘要 SVG "selective"/"neutral" 修复 | 15min |
| m1 | OPC 术语统一 | 5min |
| m3 | Graphical Abstract 占位符文本更新 | 5min |
| m4 | Oligodendrocyte "distinguish" → "detect the transcriptional boundary" | 5min |

### P2 — 建议改进（~3h）

| ID | 描述 | 估计时间 |
|------|------|:--:|
| Med3 | 参考文献按首次引用顺序重新编号（N5） | 1-2h |
| O1 | k_n floor 敏感性分析 | 2h |

---

## 9. 时序估算

| 阶段 | 内容 | 时间 |
|------|------|------|
| Phase 1 — P0 批量修复 | C1 + M1 + M3 + m2 | 50min |
| Phase 2 — v27 build | Fresh rebuild + 全局验证 | 20min |
| Phase 3 — P1 深化 | M2 + Med1 + Med2 + Med4 + m1 + m3 + m4 | 1h |
| **总计** | — | **~2 小时** |

修复 P0 后 v27 预计评分 ≥8.0/10，P0+P1 后 ≥8.3/10。

---

## 10. 底线

1. **v26 是可投稿版本的基础。** N2（Cohen's d → SES）100%修复、N4（neutral 术语）彻底清理、N9（PMI 讨论）实质性扩展——这些是本次迭代的核心成果。MANIFEST 过时和 S8-S12 缺失是投稿前必须修复的最后障碍。

2. **EVT → 描述性 P 值的方案变更在方法学上是合理的。** v26 用更诚实的描述性定位替换了 v25 的 EVT 外推。虽然统计声明从 "FDR-controlled discovery" 降为 "descriptive evidence"，但 16/14 的分离在效应量和生物学验证层面仍然可靠。MANIFEST 必须同步更新以反映这一方案变更。

3. **S8-S12 缺失是 v26 投稿包的唯一 desk reject 级别风险。** 修复成本极低——文件已存在于 Repro Guide 记录的 `results/figures_final/` 路径，仅需重命名并加入投稿包。

4. **N2 100%修复是跨专家最高共识的进展。** v25 最大的执行失误已被完全纠正。这是专家团机制的直接成果——没有独立审稿，工具辅助的全局搜索漏检不会在跨文档验证中被暴露。

5. **建议流程**：P0 修复（50min）→ v27 自动 build + 全局验证 → 直接投稿 NAR。P1 修复建议在投稿前同步完成，不阻塞投稿。

---

*独立审稿报告存档:*
- `version3/v26_expert1_algorithm_review.md` — E1 算法与方法学 (8.0/10)
- `version3/v26_expert2_statistics_review.md` — E2 统计学与数据分析 (7.2/10)
- `version3/v26_expert3_biology_review.md` — E3 生物学与单细胞基因组学 (7.5/10)
- `version3/v26_expert4_journal_review.md` — E4 稿件质量与期刊策略 (7.80/10)
