# CKI v33 专家团综合审稿报告（第四批）

**审稿日期**: 2026-08-03
**审稿团**: 4位独立专家（计算方法与可复现性 / 定量生物学与统计 / 转录组学与单细胞应用 / 学术出版与同行评议）
**审稿对象**: version3/CKI_NAR_Submission_v33.zip（32 文件，3.2 MB）
**delta 范围**: v32（8.41/10, 4 Major + 20 Minor）→ v33（声称全部修复）
**对比基准**: v32 综合审稿（8.41/10, 第三批专家团）

---

## 1. 执行摘要

**v33 综合评分：加权平均 8.64/10**（v32: 8.41/10, +0.23）

| 专家 | 角色 | 评分 | 权重 | v32 评分 | Δ | 新发现 Critical | 新发现 Major | 新发现 Minor |
|------|------|------|------|----------|------|:---:|:---:|:---:|
| E1 | 计算方法与可复现性 | 8.9/10 | 25% | 8.7 | +0.2 | 0 | 3* | 5 |
| E2 | 定量生物学与统计 | 8.7/10 | 30% | 8.4 | +0.3 | 0 | 0 | 6 |
| E3 | 转录组学与单细胞应用 | 8.5/10 | 25% | 8.2 | +0.3 | 0 | 0 | 4 |
| E4 | 学术出版与同行评议 | 8.4/10 | 20% | 8.3 | +0.1 | 0 | 2* | 3 |
| **综合** | — | **8.64/10** | 100% | 8.41 | **+0.23** | **0** | **3** | **12** |

*E1 的 3 个 Major 和 E4 的 2 个 Major 实为同一组问题（M1/M3/M4），计为 3 个独立 Major。

**核心结论**：v33 在 Minor 层面实现了实质性改进——12 项 Minor 修复完全验证通过，包括 CV 更正（60%→52%）、FDR 术语统一、P-value 精度统一、Abstract 措辞软化、Limitations 大幅扩展（#18–#21）、术语精确化（"threshold-passing candidates"、"complementary"）等。但 **MANIFEST 声称的 4 个 Major 修复中有 3 个（M1/M3/M4）实际未执行**，被 E1 和 E4 独立确认。这造成 MANIFEST 声明与文件内容不匹配的可信度问题。

四维度评分全面上升，最大升幅在 E2（+0.3）和 E3（+0.3），反映统计透明度和生物学解释精确度的重大改进。零 Critical 问题，3 个 Major 均为 v32 遗留的文档编辑性问题（参数表位置、补充图引用、参考文献引用），修复成本低（~45 min）。

**准备度评估**：~89%（v32: ~88%, +1%）。修复 3 个 Major 后预计 ~93%。投稿 NAR 准备度充裕。

**关键警告**：MANIFEST 声称 "4 Major + 20 Minor ALL resolved"，但 3/4 Major 实际未完成，且 Minor 计数 20→17 存在错误。建议投稿前修正 MANIFEST 声明以恢复可信度。

---

## 2. v32→v33 变更追踪

### 2.1 Major 修复（声称 4/4，实际 1/4）

| 编号 | v32 问题 | MANIFEST 声称 | E1 | E2 | E3 | E4 | 实际状态 |
|------|------|:--:|:--:|:--:|:--:|:--:|------|
| **M1** | Repro Guide §6 参数表位置错误 | 已修复 | ❌ | — | — | — | **未修复**：§6 仍为空，参数表仍在 §8 之后 |
| **M2** | 数据源声明不一致 | 已修复 | ✅ | — | — | — | **已修复**：3 数据集均 GitHub+GEO/CELLxGENE 双标注 |
| **M3** | S3–S9 补充图未在正文引用 | 已修复 | ❌ | — | — | ❌ | **未修复**：S3–S9 仍仅在图例定义，正文零引用 |
| **M4** | 8 篇 orphan references | 已修复 | ❌ (7/8) | — | — | ❌ (7/8) | **部分修复**：Ref 44 已引用（m12），Refs 31–35/40–41 仍孤儿 |

**E1 和 E4 独立通过 Grep 搜索确认 M3/M4 未修复，证据确凿。**

### 2.2 Minor 修复（声称 20 项全部，实际 17 项）

**MANIFEST 计数错误**：Phase B (m1–m3, 3 项) + Phase C (m4–m17, 14 项) = 17 项，非声称的 20 项。Phase C 标注 "17/17" 应为 "14/14"。

#### High-Consensus Minor（3/3 全部修复）

| 编号 | 问题 | E1 | E2 | E3 | E4 | 状态 |
|------|------|:--:|:--:|:--:|:--:|:--:|
| **m1** | MANIFEST FDR 术语 → "P-value floor (descriptive)" | ✅ | ✅ | — | ✅ | ✅ |
| **m2** | CV 60% → 52% | ✅ | ✅ | ✅ | ✅ | ✅ 4/4 确认 |
| **m3** | Cover Letter "30 signatures" → "30 threshold-passing candidates" | ✅ | — | ✅ | ✅ | ✅ |

#### Low-Consensus Minor（14 项，9 完全 + 4 部分 + 1 未修复）

| 编号 | 问题 | E1 | E2 | E3 | E4 | 状态 |
|------|------|:--:|:--:|:--:|:--:|:--:|
| **m4** | requirements.txt 在 Repro Guide §1 引用 | ✅ | ✅ | — | ✅ | ✅ |
| **m5** | Supp P-value 精度 9.99e-04 | ✅ | ✅ | — | ✅ | ✅ |
| **m6** | 脑区细胞类型 9→10 | ⚠️ | ✅ | ✅ | ✅ | ⚠️ L31 列表仍仅 9 条目 |
| **m7** | MANIFEST "section 2"→"section 1" | ✅ | — | — | ✅ | ✅ |
| **m8** | Abstract "two with permutation support" | ✅ | ⚠️ | ✅ | ✅ | ⚠️ Intro L18 仍 "statistically significant" |
| **m9** | k_n floor TT/NN (Limitation #20) | ⚠️ | ❌ | — | — | ❌ Limitation #20 不存在 |
| **m10** | 单侧检验 Limitation #18 | ✅ | ✅ | — | — | ✅ |
| **m11** | P-value floor 替代解释 Limitation #19 | ✅ | ✅ | — | — | ✅ |
| **m12** | Cross-species Spearman r 在 Discussion | ⚠️ | — | ⚠️ | — | ⚠️ 引用了 S2 但无具体 r 值 |
| **m13** | TCGA k_n floor 在 Results | ❌ | — | ⚠️ | — | ❌ 仅在 Discussion，非 Results |
| **m14** | "threshold-passing candidates" | ✅ | ✅ | ✅ | — | ✅ 3/3 确认 |
| **m15** | 非神经元 scope Limitation #21 | ✅ | — | ✅ | — | ✅ |
| **m16** | Supp 图编号 S8/S9 | ✅ | ✅ | — | ✅ | ✅ |
| **m17** | "orthogonal"→"complementary" | ⚠️ | ⚠️ | ✅ | ⚠️ | ⚠️ L77/L116 残留（3/4 标记） |

### 2.3 变更追踪汇总

| 类别 | 声称 | 完全修复 | 部分修复 | 未修复 |
|------|:---:|:---:|:---:|:---:|
| Major | 4 | 1 (M2) | 0 | 3 (M1, M3, M4) |
| Minor | 17 | 12 | 4 (m6, m8, m12, m17) | 1 (m9/m13) |

**MANIFEST 可信度**：24 项声称中 13 项完全验证，5 项部分验证，3 项未验证，3 项计数错误。通过率约 54%。

---

## 3. 跨专家共识分析

### 3.1 最强共识（4/4 专家确认）

- **CV 修正 60%→52%（m2）**：E1（Grep 验证）、E2（独立计算 CV=52.1%）、E3（确认 L52 措辞）、E4（逐行验证）。全文校准因子精度问题的唯一事实性错误已更正。

### 3.2 强共识（3/4 专家独立标记）

- **M3/M4 声称修复但实际未修复**（E1 + E4 独立确认）：两位专家通过 Grep 搜索独立验证 S3–S9 在正文的引用情况（零匹配）和 orphan references 的作者名匹配（7/8 仍孤儿）。这是 v33 最严重的可信度问题。
- **"orthogonal" 残留（m17）**（E1 + E2 + E4）：L77 和 L116 两处 "orthogonal" 未被替换。E2 从统计角度指出 r=−0.38 至 −0.57 是负相关非正交，构成术语误用。
- **Limitation #20 缺失**（E1 + E2 独立发现）：编号从 #19 跳至 #21，"Twentieth" 不存在。m9 声称已创建此 Limitation。

### 3.3 中等共识（2/4 专家标记）

- **L31 细胞类型计数字面仅 9 条目 vs L74 的 10 条目**（E1 + E3）：m6 改了数字但未拆分列表，导致计数不一致
- **Introduction L18 "statistically significant" 残留**（E2 独立发现，E3 在 Conclusions 中暗示）：与 Abstract m8 修复不一致

### 3.4 独立但互补的发现

**E1 独有**：
- M1 (Repro Guide §6 为空) 未修复 —— 其他专家未审查 Repro Guide 细节
- MANIFEST 计数错误（20→17）
- TCGA k_n floor 未在 Results 注释（m13 未修复）

**E2 独有**：
- Introduction "both statistically significant" 与 Abstract 不一致
- "Future directions" 段落被 Limitations 中断（语法断裂）
- MANIFEST Bootstrap Status 格式不统一
- 独立验证了所有统计计算（CV, CI, MCSE, P 值公式一致性）

**E3 独有**：
- 跨物种验证 Spearman r 仍缺（m12 部分修复）
- TCGA Results k_n floor 简注仍缺（m13 部分修复）
- 生物学解释质量详细评估通过（四机制框架、细胞类型精准度）

**E4 独有**：
- NAR 格式合规全套检查通过（除 M3/M4）
- Cover Letter 质量评分 9.5/10
- 跨文档一致性：术语 "orthogonal" 不一致（L77 vs L98）、m14 混合短语

---

## 4. 问题汇总

### Major — 投稿前必须修复（3 项，~45 min）

| 编号 | 问题 | 来源 | 修复时间 |
|------|------|------|:--:|
| **M1** | Repro Guide §6 仍为空，参数表仍在 §8 之后。MANIFEST 声称已修复但实际未执行。 | E1 (v32 New-M1 残留) | ~10 min |
| **M3** | S3–S9（7 张补充图）仅图例定义，正文零引用。E1 和 E4 通过 Grep 独立验证。NAR 格式要求。 | E4-M1 (v32 残留) | ~15 min |
| **M4** | Refs 31–35, 40–41（7 篇）仍为 orphan。仅 Ref 44 已通过 m12 引用。E1 和 E4 通过作者名 Grep 验证。 | E4-M2 (v32 残留) | ~20 min |

### Minor — 高共识（≥3/4 专家标记，3 项，~10 min）

| 编号 | 问题 | 来源 | 修复时间 |
|------|------|------|:--:|
| **m17-残留** | L77 "orthogonal transcriptomic readout" → "complementary"；L116 "orthogonal information" → "complementary" | E1+E2+E4 | ~2 min |
| **m9-残留** | Limitation #20 不存在（编号 #19→#21 跳跃），MANIFEST 虚假声明 | E1+E2 | ~5 min |
| **m8-残留** | Introduction L18 "both statistically significant" → "both with permutation support" | E2+E3 | ~2 min |

### Minor — 中等共识（2/4 专家标记，3 项，~10 min）

| 编号 | 问题 | 来源 | 修复时间 |
|------|------|------|:--:|
| **m6-残留** | L31 列表仍仅 9 条目，需拆分 committed OPCs 为独立条目 | E1+E3 | ~5 min |
| **m12-残留** | Discussion L98 跨物种验证段未给出 Spearman r 具体数值 | E1+E3 | ~3 min |
| **m13-残留** | TCGA Results (L64–66) 缺 k_n floor 简注 | E1+E3 | ~3 min |

### Minor — 单一专家标记（6 项）

| 编号 | 问题 | 来源 | 修复时间 |
|------|------|------|:--:|
| **MANIFEST-count** | MANIFEST 声称 20 Minor 实为 17；Phase C "17/17" 实为 14/14 | E1 | ~1 min |
| **Future-directions** | Limitations 中断 "Future directions" 段落，语法断裂 | E2 | ~2 min |
| **Bootstrap-status** | MANIFEST Bootstrap Status 4 行表述格式不统一 | E2 | ~3 min |
| **N-E3-1** | L31 "10 major non-neuronal classes" 列表中 OPC/committed OPC 合并表述 | E3 | ~3 min |
| **N-E3-4** | L91 "threshold-passing Strong candidate signals" 混合短语 | E3 | ~1 min |
| **m14-残留** | （同上，与 N-E3-4 合并） | E3 | — |

---

## 5. 评分趋势

```
v25 (第一批): 7.50 ─── 4 P0 + 5 P1 + 4 Minor
     │
v26 (第一批): 7.60 ─── 1 Critical + 3 Major → N1-N9
     │
v28 (第二批): 7.78 ─── 0 Critical + 12 Major + 19 Minor
     │
     ├─ P0 (3/3) + P1 (8/8) + P2 (19/19) 全部修复
     │
v32 (第三批): 8.41 ─── 0 Critical + 4 Major + 20 Minor
     │
     ├─ 4 Major + 20 Minor 声称全部修复
     │
v33 (第四批): 8.64 ─── 0 Critical + 3 Major (v32 残留) + 12 Minor
```

**四批专家团评分趋势**：7.50 → 7.60 → 7.78 → 8.41 → 8.64。v33 的提升幅度（+0.23）较 v32（+0.63）收窄，因为：
1. v32 起点已很高（8.41），改进空间缩小
2. 3 个声称的 Major 修复未实际完成，限制了提升幅度
3. Minor 修复中多涉及术语精确化和细节完善，不改变核心科学结论

**v33 的提升主要来自**：
- E2 +0.3：CV 更正、FDR 术语统一、Limitations #18–#19 新增、P-value 精度统一
- E3 +0.3：committed OPC 独立分类、术语精确化（m14/m8）、Limitation #21
- E1 +0.2：M2 数据源统一、跨文档参数一致性、requirements.txt 引用
- E4 +0.1：m1–m8 多项 Minor + Cover Letter 质量提升，被残留 M3/M4 拉低

---

## 6. 修复路径

### Phase A：投稿前必须（3 Major + 3 高共识 Minor, ~55 min）

1. **M1（E1 New-M1）**: 将 Repro Guide 参数表（L301–329）移入 Section 6 → ~10 min
2. **M3（E4-M1）**: 在正文 Results 对应位置添加 S3–S9 引用（每个图 1 处）→ ~15 min
3. **M4（E4-M2）**: 在 Discussion 相应段落引用 Refs 31–35, 40–41（microglia/BBB/fibroblast/PAML），或移除 → ~20 min
4. **m17-残留**: 替换 L77/L116 "orthogonal" → "complementary" → ~2 min
5. **m9-残留**: 补充 Limitation #20（k_n floor TT/NN 触发比例）或修正 MANIFEST 声明 → ~5 min
6. **m8-残留**: Introduction L18 "both statistically significant" → "both with permutation support" → ~2 min

### Phase B：投稿前建议（3 项中等共识 Minor, ~10 min）

7. **m6-残留**: L31 拆分 committed OPCs 为独立条目 → ~5 min
8. **m12-残留**: L98 添加 Spearman r 具体数值 → ~3 min
9. **m13-残留**: L64–66 TCGA Results 添加 k_n floor 括号注 → ~3 min

### Phase C：Revision 阶段（6 项单专家 Minor, ~10 min）

10–15. MANIFEST-count、Future-directions、Bootstrap-status、N-E3-1、N-E3-4 等

---

## 7. 提交建议

**推荐行动**：修复 Phase A 3 Major + 3 高共识 Minor 后即可投稿 NAR。Phase B 3 项建议同步完成。Phase C 6 项可在 revision 阶段处理。

**Desk reject 风险评估**：低。稿件核心科学质量已经过 4 批共 16 位独立专家的多轮验证（v25 4 位 + v28 4 位 + v32 4 位 + v33 4 位），评分从 7.50 稳步升至 8.64。无 Critical 问题，3 个 Major 均为文档编辑性问题。Cover Letter 质量 9.5/10，Abstract 195 词合规。

**主要风险**：
1. M3/M4 在 NAR 格式审查中可能被标记——修复后在正文添加引用即可通过
2. MANIFEST 声明与实际文件内容不匹配——如果编辑核查构建流程可能产生信任问题

**MANIFEST 可信度建议**：投稿前更新 MANIFEST 如实标注 M1/M3/M4 为 "deferred" 或正确声明修复状态，避免给编辑留下面子工程的印象。

**预计投稿后评分**：修复 Phase A+B 后 ~9.0/10。Revision 阶段全部 Minor 修复后 ~9.2/10。

### 独立审稿报告

- `version3/v33_expert1_algorithm_review.md` — E1: 计算方法与可复现性 (8.9/10)
- `version3/v33_expert2_statistics_review.md` — E2: 定量生物学与统计 (8.7/10)
- `version3/v33_expert3_biology_review.md` — E3: 转录组学与单细胞应用 (8.5/10)
- `version3/v33_expert4_journal_review.md` — E4: 学术出版与同行评议 (8.4/10)
