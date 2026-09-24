# nc53 终审轮（v52 final review）汇总与修复报告 — 2026-09-24

## 六审评分（任务书数字取自当版文本，报告均先落盘 results/audit/nc52_final_review_r*.md）

| 审稿人 | 评分 | Verdict | 关键条件 |
|---|---|---|---|
| R1-stats | 7.5 | minor revision | 5 条必须（DeLong SI 方法段、per-cancer 计数、GTEx 队列说明、P≈0 规范、6.33–6.45 归因） |
| R2-sccomp | 7.5 | minor revision | A1–A5 必修 + B1–B3 建议（permute 指针落空、35,306、3,567、Fig. 5a、KIRC 754） |
| R3-cancer | 7.2 | accept after minor revisions | C1–C3 必修（35,306、k_n 括注、deconv 引用） |
| R4-brain | 7.0 | minor revision | 3 条可选（k_n-dominated、Note 13 指针、任务书口径更正） |
| R5-editor | 7.0 | major→修后可投 | M1–M5 投稿阻断（Table 1 表注、Fig 14 图注、CL 口径、Tables 1–4、5,151） |
| R6-repro | 7.5 | accept（条件性） | 唯一硬条件 = Zenodo v0.5.1 record → DOI 写回（生产流程阻塞中） |

均分 7.28；无 reject、无新增分析要求；全部必修项为文本/表格层面。

## 审稿裁定的 ground truth 反转（铁律：指控先复核再修）

1. **R5-M5 / R2-A1 部分反转**：MS "permuting k_n across the 5,151 human pairs" 非笔误——nc52_stats_omega_kf_math_floor.csv 逐字吻合（n_pairs=5,151, floor 0.524 [0.506, 0.541], observed 0.0895）。该置换跑在 102-entry 全量 inventory（phase33），与主分析 4,851（99 filtered entries）是不同输入集。修法 = MS 加 "full-inventory" 限定 + SI Note 9 补小节，**不改 4,851**。
2. **R4 揪出任务书旧口径**：脑 Strong 39（非 30）、全局家族无一 FDR 存活 q_min=0.520（brain_bs_null_results.csv q_fdr min=0.5202 实证）；MEMORY.md 已更正。
3. **R2-A5 KIRC 750 vs 754**：主链 pair-level 750（nc52_tcga_pancancer_excc.csv）与 deconv 全表达矩阵 754 是两种样本集定义；GTEx 同用全矩阵（495/535/398/754/1032）。修法 = SI 4.3 队列层级句统一说明，不重跑分析。
4. **R1-5 6.33–6.45 归因**：nc52_brain_quality_regression_classlib.csv 显示两值均来自 (class, region) 层（6.3276/±mito 6.4503），(class, library) 层仅 T3 系数；MS 已改、SI 原文本就正确。

## 修复清单（全部落地）

### MS（generate_manuscript_nc.py）
- Methods 分癌种计数括注 → "3,567 samples, of which 3,535 enter … all 32 excluded cell-line aliquots are LIHC tumors, leaving 366"（R1-2/R2-A3）
- Methods pair table → "34,828 pairs after dropping the 478 pairs touching the 32 cell-line-derived aliquots from the 35,306-pair table"（R3-C1/R2-A2）
- Discussion permute-k_n → "5,151 full-inventory human pairs"（R5-M5/R2-A1）
- Results 末 deconv 句 → "pending single-cell validation (reference-free composition check: ρ = 0.20–0.26 versus k_n; Supplementary Note 8)"（R3-C3/R2-B3）
- Discussion 末 → "the composition check … least certain."（原 deconvolution-based validation remains necessary 退役）
- 新增 Table 1 表注（复用 xlsx A1 文本，R5-M1）；新增 Supplementary Fig. 14 图注（microglia 21.83±7.20 vs 1.30±0.36、P=5.5e-14、AUC=1.00、k_n AUC=0.89，R5-M2）
- 6.33–6.45 归因改 (class, region) 层（R1-5）
- MAIN 词数：5,016 → 4,997（三处压缩：M4a 尾句精简、删重复尾句、pooled value→this、kidney 括注）

### SI（notebooks/68_gen_supplementary_nc.py）
- k_n 括注 "which includes 1" → "1.34 [1.02, 1.89] excludes 1 ex-CC, so the k_n elevation is nominally significant"（R3-C2/R2-SC1）
- Table 11 表注 Fig. 5a → Fig. 4a（R2-A4）
- 4.3 队列层级：3,567 pre-audit / 3,535 ex-CC / 3,596 全矩阵（GTEx+deconv 口径，KIRC 754）（R1-2/3、R2-A5）
- GTEx 段：liver 半句（healthy marginally above adjacent, P=3.8e-5）+ P≈0 → P≤3.2e-84（R1-4）
- severity JT P≈0 → P<10⁻¹⁵（两处 + Table 18 行）
- Note 1 新增 AUC interval methods 段（DeLong [0.770,0.838] + module-seed cluster bootstrap [0.771,0.836]、nc52_stats_auc_ci_methods.csv）（R1-1）
- Note 9 新增 k_n-permutation floor 段（human 5,151: floor 0.524 [0.506,0.541] vs 0.089；mouse 703: 0.857 [0.843,0.870] vs 0.821，dataset-dependent）（R2-A1）
- Note 8 新增 reference-free composition fallback 段（NNLS、split-half ρ 0.934/0.964、k_n 相关 0.20/0.26、CIBERSORTx/BayesPrism 不可行原因、脚本+输出清单）（R3-C3/R2-B3）
- 3.3 lower-tail 富集句尾加 Note 13 rule-matched null 指针（R4②）
- **xlsx 15→19 sheets**：Table 1（phase32_sweep 5 行）、Table 2（phase35_cross_organ 59 行）、Table 3（brain_ct_test 10 行）、Table 4（6,591 候选含 tier/residual/ω）；docx 四段描述各补 xlsx sheet 指针（R5-M4）

### CL（generate_cover_letter_nc.py）
- 3,567→3,535、1.10→1.11–2.46（R5-M3）
- "ranked first" → "gave the best functional-versus-neutral discrimination at bounded power (AUC = 0.80)"
- 新增 GTEx 句（adjacent-normal k_n at healthy-tissue levels in lung/liver/breast, arguing against a field-effect reading）

### 工程（R6 建议）
- Dockerfile 头注释 0.5.0→0.5.1
- run_all.py 加 Phase 6f (nc52) 作用域说明（指向 Guide 5.13）
- 删 _tmp_gen_dbg.py；tag 后再生的 figure2.pdf/Supplementary_Fig_14.pdf 随本批提交

## 断言同步（三层模式）

- 99_build：221/221（仅 3 个 run 子脚本失配→同步后归零）
- ms_verify：3,596 计数 2→3；+7 条 v53 断言（ex-CC 括注、34,828、full-inventory、Table 1 表注、Fig 14 图注、(class, region) 归因、deconv 引用）
- si_verify：sheets 15→19（range(1,20)）；3,596 计数 2→3；+6 条 v53 断言（k_n 括注、4.3 层级、DeLong、permutation floor、deconv fallback、GTEx liver+P 口径）
- cl_guide_verify：CL 3,567→3,535；ranges 1.10→1.11；+2 条（GTEx 句、bounded-power 措辞）
- XV8：63/63（MAIN 4,997/5,000）

## 全量验证

- 构建 221/221 ✓；XV8 63/63 ✓；pytest 29 passed ✓；spot_check ALL PASSED ✓

## 遗留（不阻断投稿文本）

- Zenodo v0.5.1 version record 未生成（webhook 409 锁，用户网页查证中）→ phase-2 DOI 写回 + 元数据 Genome Biology→Nature Communications（R6 唯一硬条件）
- R4① 摘要 "(k_n-dominated)" 可选未做（摘要 200 词踩线）
- R2-B1/B2 建议级措辞（摘要 field-effect 强度、KIRC 句）留待 proof 阶段
- R6 沿留项：pyproject description 命名、CI ubuntu-only、Guide 5.6f 6.67 外观项
