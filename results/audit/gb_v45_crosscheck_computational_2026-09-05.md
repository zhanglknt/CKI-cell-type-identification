# v45 交叉验证核销报告（r-computational 视角）

- **核销对象**: version3/CKI_Submission_v45/（正文/补充/复现指南 fulltext）+ `cki/` v0.4.8 源码 + `results/*_v45_report.md` 分析工件
- **基准**: 本人 v44 盲审报告 results/audit/gb_v44_blind_review_computational_2026-09-05.md（6.8/10，Major-light）
- **方法**: 逐条独立开文件核实（文稿长行已折行为临时文件辅助阅读；代码直接精读；测试因本会话沙箱阻断进程派生无法执行，改为静态核对测试函数清单）
- **日期**: 2026-09-05

## 总结表

| 条目 | 判定 | 关键证据（文件:位置） |
|---|---|---|
| P1-1 中性漂变与 HK 锚定同构 | **CLOSED** | SN 3.22（_v45_sn_wrapped.txt:469-482）；MS Results 段（_v45_ms_wrapped.txt:134-138）；摘要更新（同:13-15）；Limitations N2 披露（同:513-516）；results/nonhk_drift_v45_report.md 全文 |
| P1-2 竞品基准薄弱/不公平 | **PARTIAL** | Augur 新增且混杂受控（MS:359-365；SN 3.23:483-496；results/augur_comparison_v45_report.md）；但 scDist 仍为 Python 近似（MS:517-519 保留明确告诫）、MELD 饱和、头对头仍是单一 lane 混杂数据集 |
| P1-3 `ci_95` 误命名等 API 缺陷 | **CLOSED** | cki/bootstrap.py:31-66（`null_ci_95` + `_ALIASES` + `.get()` 覆盖）、555-604（nonfinite 守卫 + 警告 + `n_null_finite`）、649（`permutation_test = bootstrap_test`）；__init__.py:31,51 导出；测试 test_smoke.py:544,583 |
| P2-1 SN 1.5-fold 笔误 | **CLOSED** | SN 3.5 已改 1.3-fold（_v45_sn_wrapped.txt:186）；复现指南同步（_v45_rg_wrapped.txt:322） |
| P2-2 ε=1e-9 描述与代码不符 | **CLOSED** | SN 3.11(2) 重写为"零掩码 + softmax 分母守卫，从不进入 k_n/k_f/ω"（_v45_sn_wrapped.txt:256-257），与 utils.py:91、core.py:77-86 逐字一致 |
| P2-3 包默认参数不复现论文 | **CLOSED** | core.py:355,423-431,518-522 `preset="manuscript"`（pairwise_absdiff/top-200/HRT 参考）；测试 test_smoke.py:638 |
| P2-4 可扩展性/复杂度 | **PARTIAL** | MS 新增 Computational environment 段（_v45_ms_wrapped.txt:698-702：<5 min/对、72 核时、32GB）；但仍无形式复杂度分析，MS/指南未显式分层"包内内存实现 vs 流式 notebook"（仅 blocknull.py:30-33 docstring 有说明） |
| P2-5 次要一致性（10vs20 细胞、Algorithm 1 记号、.get 绕过） | **CLOSED** | MS:548 "≥20 cells/entry；≥1 donor ≥10 cells" 与数据描述统一；SN Note 1.1 记号已精确化（_v45_sn_wrapped.txt:29-34，并新增 TCGA log2 softmax 幂变换披露——超出原修复范围）；bootstrap.py:63-66 `.get()` 覆盖 |

## 专项复核（team-lead 指定）

1. **比值估计量偏差-方差**（results/ratio_estimator_biasvar_v45_report.md → SN 3.20，_v45_sn_wrapped.txt:447-458）：数字逐一吻合——中位偏差 +0.2%（合并 −1.8%）、delta 法 ρ=0.99/1.00、最小分母箱 +6.5%、梯度 6.10(mean)/6.00(median)/6.09(trimmed)、剔除 k_n<5e-4 后 6.52、丢底 20% ρ=0.964。MS 正文整合正确（_v45_ms_wrapped.txt:100-102，明确"calibration absorbs ratio bias"）。注意：简报中"1.3-fold median bias"说法与文档不符——文档实际主张是中位偏差 +0.2%，1.3-fold 是校准基线比值（9.73/7.70=1.26），两处均已在 v45 中各自正确表述，无误植。
2. **ddof=1 披露**：已恢复，MS Results（_v45_ms_wrapped.txt:234："all class-level SDs in this paragraph computed with ddof = 1"）。
3. **Augur**：主结果确为混杂受控的 binary one-vs-rest 变体（pyaugur 0.1.0，ρ=+0.442 vs ω、+0.564 vs k_f、−0.236 vs k_n），multiclass（+0.127）仅作敏感性分析且区域数混杂（ρ=−0.744, P=0.014）在 MS 与 SN 3.23 中均明确披露。与 `results/augur_comparison_v45_report.md` 及两个 JSON 工件一致。
4. **非 HK 锚定漂变**（results/nonhk_drift_v45_report.md → SN 3.22）：N0 内控复现原始仿真（ω 0.000 / raw JS 0.556 / cosine 0.600 vs 原 0.000/0.553/0.580）；N1（表达匹配的低方差非 HK 集）ω FPR 0.067/0.011/0.000 vs raw JS 0.067/0.811/1.000——特异性优势对乘法/组成型漂变不依赖 HK 锚定，原 P1-1 核心关切被正面回答；N2（基因身份对调）所有指标 FPR=1.00，作者如实披露并给出合理诠释。
5. **cki v0.4.8**：pyproject.toml:7 与 __init__.py:38 均为 0.4.8；测试套件静态清点为 29 个 test 函数（test_smoke 22 + test_reference_values 7），与"pytest 29 passed"声明结构吻合，且新增测试精确覆盖本次修复（null_ci_95 别名、nonfinite 守卫、preset、大组窗口警告）。**限制**：本会话沙箱吞掉所有派生进程输出，无法实际执行 pytest，运行级验证缺失。

## 新引入问题（v45 回归扫描）

1. **[轻微] 摘要幅度选择性表述**：摘要称非 HK 漂写下 "raw JS and cosine: 0.81–1.00"，但该区间仅覆盖 η≥0.5；在最小幅度 η=0.25 时 raw JS FPR=0.067、cosine=0.089，与 ω（0.067）基本相当——优势是幅度依赖的。建议摘要括号改为 "(raw JS and cosine: 0.81–1.00 at η ≥ 0.5)" 或给出全范围。不影响结论方向。
2. **[轻微] pyaugur 出处不可独立核验**：第三个竞品（Augur）再次以"移植版"（pyaugur 0.1.0，自称对 R 版基准 ρ=1.0）而非原始实现评估；复现包/文稿未引用该基准的工件。因结论用于"互补性"而非"优越性"且已披露，可接受，但建议在 SN 3.23 补一句基准出处或链接。
3. 未发现数学/统计层面的新错误；605/605 构建断言与 Release sha256 无法离线核验（记为未验证项）。

## v45 总体评分

**7.8 / 10**（v44 为 6.8）——建议判定升级空间：**Minor Revision**。

理由：v44 的 3 条 P1 中两条（P1-1、P1-3）被实质且正确地关闭，8 条 P2 中 6 条关闭；新增的四项分析（比值偏差-方差、小簇 bootstrap 覆盖率、非 HK 锚定对照、Augur 混杂受控对比）均为真实新计算且有工件、脚本、SN 三层对应，数字抽查全部吻合；包 API 修复（null_ci_95、别名弃用、nonfinite 守卫、preset）实现质量高且有对应测试。剩余缺口集中在 P1-2（scDist 仍非原版、头对头仍单一混杂数据集——但已以充分披露 + 新增 Augur 主对比部分补偿）与 P2-4（复杂度/分层表述），均属可在小修中处理的范围。
