# v46 终审签署（r-computational）

- **核销对象**: version3/CKI_Submission_v46/（CKI_Manuscript_fulltext.txt、CKI_Supplementary_fulltext.txt）
- **范围**: 本人 v45 交叉验证报告（results/audit/gb_v45_crosscheck_computational_2026-09-05.md，7.8/10）遗留的 2 条轻微问题
- **日期**: 2026-09-05

## 逐条核销

### 残留 1：摘要 "0.81–1.00" 幅度选择性表述 → **CLOSED**

- 摘要（正文提取件 0010 段）："…staying ≤0.067 under expression-matched non-housekeeping drift (**raw JS and cosine at moderate-to-strong drift**: 0.81–1.00)" —— 0.81–1.00 区间已明确限定于中强漂变（η ≥ 0.5），不再暗示全幅度优势。
- 正文 Results（0039 段）：同一限定措辞（"inflated to 0.81–1.00 at moderate-to-strong drift"），且 ω 的完整范围 "0.000–0.067 across η" 保留，句子结构正确。
- η=0.25 处 raw JS FPR = 0.067（与 ω 持平）的完整 N1 数字在 SN 3.22 中明确列出（"FPR 0.067, 0.011, and 0.000 at η = 0.25, 0.5, and 1.0, versus raw JS 0.067/0.811/1.000"），读者可在补充材料中核验幅度依赖性。
- 判定依据：摘要表述现已数学准确，无误导。

### 残留 2：pyaugur ρ=1.0 基准出处 → **CLOSED**

- SN 3.23（0145 段）："we used pyaugur 0.1.0, a pure-Python port of R Augur v1.0.3; **the port's own validation benchmark (shipped with the pyaugur package) reports Spearman ρ = 1.0 against the R reference implementation**" —— 基准来源已明确归属于 pyaugur 包自带的验证，读者可按此独立核验，不再是无出处的宣称。

## 最终评分

**8.0 / 10**（v44：6.8 → v45：7.8 → v46：8.0）

签署意见：本人 v44 盲审提出的全部 8 条问题（3 P1 + 5 P2）及 v45 复核发现的 2 条轻微残留，在 v46 中均已关闭或降至充分披露的可接受水平（P1-2 竞品基准、P2-4 复杂度分层为披露式部分关闭，属方法定位内可接受）。三轮抽查未发现任何数学/统计错误，文稿—代码—工件三层一致性保持良好。**从计算生物学/算法视角，同意以现稿发表（Accept 级别签署）**。构建断言 621/621 与 Release sha256 为离线不可核验项，不在本签署范围内。
