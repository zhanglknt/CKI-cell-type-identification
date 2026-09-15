# v47.3 方案A Abstract 合规 + 三项修复 — 审计与交叉验证报告

**日期**: 2026-09-15
**范围**: CKI_Manuscript.docx（v47.2 → v47.3）
**指令**: 选择方案A（Abstract 非结构化 ~150 词 + Keywords 独立）；Skinnider 文献补第 6 作者；Methods 指南章节 1.3→1.1；附图图注移至图注标题下

---

## 1. 修复项

### 1.1 方案A：Abstract 合规（GB Methodology）
- 原状：结构化三段（Background/Results/Conclusions 标签）250 词，Keywords 混排在 Abstract 块内（居中 10pt）
- 修复：单段非结构化 **148 词**（保留全部关键锚点：FPR 0.00 vs 0.55–0.58 raw JS and cosine、no anchoring artifact、AUC 0.80、~50–200 cells power window、ω = 7.70 95% CI [7.37, 8.02]、6.10-fold 梯度、equal-n 1.74 [1.64, 1.84] 上界、gene selection inflates 1.6-fold、CKI 全称展开）；Keywords 改为独立行（Arial 11 左对齐，5 个关键词，符合 GB 3-10）
- 附带更新断言：V46-b（≤165 词非结构化）、E4-1/V38-4a（同口径）、V46-a（'at moderate-to-strong drift' 2x→1x，0.81–1.00 区间披露保留于 Results）

### 1.2 Skinnider/Augur 文献六作者
- 原状：`Skinnider MA, Squair JW, Kathe C, Anderson MA, Gautier M, et al.`（5 作者，v45 新增时格式偏差）
- 全表核验（CrossRef DOI 10.1038/s41587-020-0605-1，14 位作者）：第 6 作者 **Matson KJE**
- 修复后：`…Gautier M, Matson KJE, et al.`——与其余 24 条 et al. 条目（全部 6 作者+et al.）格式完全一致

### 1.3 Methods 指南指针 1.3→1.1
- 核实指南目录：1.1 = "Python and Core Packages (verified environment)"，1.3 = "System Requirements"——用户指认正确
- 修复：`the verified environment of the Reproducibility Guide, Section 1.1`；断言 V41-14 收紧为精确匹配

### 1.4 附图图注位置
- 原状：`Additional file 1: Supplementary figure legends` 标题下为空（13 行空填充），S1–S13 图注段实际生成于 References 列表之后
- 修复：13 段图注移至标题下、References 之前；全文字节位置验证 legends heading(127134) < S1(127182) < S13(133806) < References(134269)
- 附带收益：References 节不再混入图注文本

## 2. 交叉验证（fresh DOCX 重建后）

- 构建 **670/670 全 PASS**（新增 V47.3a–e 五项断言全绿；V46-b = 148 词）
- 独立复核（不依赖构建断言）：Abstract 148 词无结构化标签 ✓；Keywords 独立行后接 Background 标题 ✓；ref 38 = 六作者+Matson KJE ✓；Section 1.1 ✓；图注位置链 ✓
- 引用首引顺序无回归：真实引用 1..56 严格递增（[0] JS-range 与 [74] bootstrap-CI 为已知非引用误报；图注移入 body 后未引入新误报）
- finalize：v47 zip 65,439,685 B / 34 条目 / 复现包 297 文件（sha a517677b…）；主目录副本同步

## 3. 过程备注

- 首轮构建 669/670：T3 断言要求 CKI 全称展开（压缩摘要时误删）→ 恢复 `(Cell-type Ka/Ks-inspired Index)`，148 词
- safe-delete 钩子拦截 finalize 的 zip 覆盖 move（本轮累计 78 文件>50 阈值）→ 旧 zip 先归档 `_tmp_archive/`，从 tmp zip 续接完成（`finalize_v473_resume.py`）

## 4. 结论

**CLOSED** — 方案A 落地 + 三项修复全部完成，构建断言与独立审计双通道一致。

审计脚本：`_tmp_fa_review/fix_v473.py`（四项修复补丁，含全部锚点断言）、`_tmp_fa_review/finalize_v473_resume.py`（finalize 续接）
