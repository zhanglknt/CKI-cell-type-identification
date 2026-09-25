# nc56 proof 沿留清单修复轮审计报告 — 2026-09-25（基线 v0.5.2 @c380e19）

用户指令：「1 切 3全部解决」之 ③proof 沿留清单全部解决（①v0.5.3 发布链随 #86 另行）。
修复矩阵：`results/audit/nc56_proof_fix_matrix.md`（含每项来源文件/原文引文/当版行号/词额收支/裁定）。

## 一、范围与来源状态
- 范围 = nc53_confirm_round_summary 第四节 6 类 + nc55_review_summary 类 B 12 项。
- 原文已落盘并逐条回查：R2-①②④⑦、R1-m5/m6、R5-③⑥、R4、R6 外观项、nc53-R5 五条、nc52-R2 B1/B2、nc52-R3 C6/C7。
- 原文未落盘（v51r2 时代 agent 消息，nc51r2_review_panel 自述）：R1-②–⑥、R2-M3、R3-①②⑤、R6-N3/N4 → 以 nc55 汇总描述为权威转述 + 当版文本 ground-truth adjudicate。

## 二、实施清单（全部完成）
### MS 生成器 generate_manuscript_nc.py（25 处）
- 摘要 7 处（净 0 词）：Inspired by Ka/Ks（−2）；housekeeping-anchored FPR（+1，R2-①）；GTEx 句 → "GTEx references in lung, liver, and breast are consistent with tumor-specific elevation"（+5，R2-B1/R3-m3/C7）；four of five CIs excluding 1（−2）；删 both（−1）；was explained by→reflected（−2）；3.7-fold gradient (k_n-dominated)（+1，R4）
- MAIN 18 处：L14 末句删除（−7）；L26 (one-significant-digit resolution) 前置（+2，R3-②）；L28 largest-donor pseudobulks 指针（+3，R2-⑦）；L30 also descriptive 重复（+2，R1-m5）；L32 Clopper-Pearson 区间指针（+6，R1-m6）；L37 four-tier（0，R5-③/R3-①）+ 删裸 Section 3.12（−2）；L38 small-stratum（+1，R5-⑥）；L45/L56 Note 指针去重（−3/−3）；L63 global / L65 within-family（+1/+1，R2-④）；L69 降级 indicative, dataset-relative（−10，兼 R5-⑤B）；L72 Section 1.4 全式（+4）；L75 consistent with…within cohorts（+3，R2-M1 残余）+ shifts 改写（+1，R5-⑥）；L78 ref. [14]（+1）；L79 panel 口径重写（−2，R2-②）
- Methods 2 处：three tiers 补第四层说明；Section 3.12 全式
- 图注 5 处：Fig 2(b) k_n 改写；Fig 3(a) 补对数 (2,161)/(1,089)/(1,656)（R6-N3）；Fig 3(c) 补 (T1: 28.6% versus 37.6–45.2%)（R6-N4）；Fig 5(d) conservative→conserved；Fig 14 validation→sanity-check（R4）
- 声明区 1 处：runs on Linux/macOS/Windows 补 CI 覆盖注明（R6-⑤；ci.yml 实证 ubuntu-latest only）

### SI 生成器 notebooks/68_gen_supplementary_nc.py（4 处）
- Note 8 插入跨队列不确定度量化句（GA/GG ≈ 1.8–2.3× 容差 + tentative 声明，R2-B1；GA/GG 记号展开为 GTEx–adjacent versus GTEx–GTEx，因 SI 全文无此缩写定义；数据出处 nc52_gtex_kn_by_grouptype.csv，肺 GA 2.07e-3 vs GG 1.14e-3）
- Note 3 "all key results" → "the calibration-relevant results"（R5-⑤A）
- Note 14 "Python 3.13" → "Python 3.14"（R2-⑤，对齐 MS 钉死环境 3.14.4）
- 3.13 节指针 "Section 5.10c" → "Section 5.13a"（R6；ex-CC 主链 nc52_tcga_excc_main.py 实际对应 Guide 5.13a）

### 仓库面（1 处 + 2 项裁定）
- pyproject.toml description → "Cell-type Ka/Ks-inspired Index: a framework for quantifying baseline-normalized transcriptomic remodeling"（R6-④）
- CL 两项（nc53-R5 #5）：**已不存在**——当版 CL 全文 grep 无 28.6/35.7/45.2/separation（早前压缩轮已删），L55 已是 "decomposes Jensen–Shannon divergence" → 不改
- Guide 5.6f（R6-⑥）：**已覆盖**——L514 已有 "deterministic division by 6.67, a legacy constant superseded by 7.70 in v44" → 不改

## 三、维持不改裁定（摘要）
R3-⑤ 摘要区间升序 vs Results 降序（升序惯例+Fig 4a ranked by effect size）；R2-M3 Bergmann 桥句（当版无 [3.16,11.69]，L56 已有 Two-controls-converge 桥式结构）；R1 放置类（DeLong SI-only/脑残差双载/n=21 已在 MS/internal pairing 由 M4 覆盖）；R1-m6 区间本体已在 SI Note 1 L155（仅补 MS 指针）；摘要 bounded-power 维持（nc54 决策 B，类 C 冲突项）；R4-m4 supercluster 可选不修；nc55 R1-m1/2/3/4/7、R2-m6 不在清单跳过。

## 四、断言面同步（教训复用：同一指针句多处钉住）
- 99_build_nc_v49.py 3 处：A3/N48 摘要句文本同步（+k_n-dominated）；N17 Section 3.12 计数 3→2；N58 attenuates→shifts
- results/audit/_nc49_ms_verify.py 5 处：摘要定位锚 "Inspired by the Ka/Ks ratio"→"Inspired by Ka/Ks"（级联修复 6 项摘要检查）；Section 3.12 计数 3→2；both survived→components survived；was explained by→reflected
- results/audit/_nc51_xv8.py 4 处：摘要锚 ×2；Section 3.12 计数 3→2；**citation groups 73→72（nc55 F1 的第三处钉点，前轮漏同步，本轮实测 72 确认）**

## 五、验证结果（全绿）
| 项 | 结果 |
|---|---|
| 99_build_nc_v49（含 ms 127/si 121/cl+guide self-check） | 221/221 PASS |
| spot_check | ALL PASS |
| pytest tests/ | 29 passed |
| XV8 交叉验证 | 63/63 ALL PASS |
| 摘要词数 | 196/200（净 0，矩阵精算一致） |
| MAIN 词数（XV8 口径） | 4,999/5,000（+1 vs 精算 −2，在限内） |

## 六、遗留
- v0.5.3 发布链（版本面/tag/Release/Zenodo/DOI 写回）= #86，本轮不动版本号
- 根目录 `nul` + `_tmp_nultest\nul`：用户手动删除项
- MAIN 余量仅 1 词：proof 后任何新增强制性插入须先找对冲
