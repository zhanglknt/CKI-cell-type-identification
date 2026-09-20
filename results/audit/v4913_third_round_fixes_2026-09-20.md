# v49.13 第三轮盲审修复审计（2026-09-20）

**对象**：CKI_Submission_v49_NC.zip v49.12+XV3（commit 6a24578）第三轮盲审（7.73，6/6 Minor）确认的 A 文档级 7 项 / B 计算组 6 项 / C 论述级 5 项
**输入**：results/audit/v4912_review_{R1..R6}_2026-09-20.md + v4912_review_panel_summary_2026-09-20.md

## 一、指控裁定（主代理独立复算）

| 指控 | 裁定 | 处置 |
|---|---|---|
| R1-n1（panel 汇总 A5 前半）"Kang 0/30 CI [0.000,0.114] 标注 Wilson 实为 Clopper-Pearson" | **驳回** | 0/30 的 Wilson 上界 = z²/(n+z²) = 3.8416/33.8416 = 0.1135 ≈ 0.114，原文标注正确；审稿人所称 0.107 为代入 n=30 的另一口径。不改稿 |
| R4-N4 "−16%~+37% 区间数字硬伤" | 驳回（上轮已裁定，panel 汇总） | 无需改 |
| R4-N5 "absorb 措辞与符号矛盾" | 驳回（上轮已裁定） | 无需改 |
| R3-N4 Guide 5.7 softmax 残留 | 确认 | 本轮修复（见 A1） |
| R3-N5 MS \|Δz\| 数值不可溯源 | 确认+扩展 | 本轮发现 composition v44 输出早于 CC 修复未重跑（见二），重跑后全链同步（见 A2） |
| SI 1.6 "min 10 cells" vs 正文 "≥20" | 确认 | 1.6 已改 20 |

## 二、重大链式发现：composition 数字漂移（CC 修复链缺口）

`results/tcga_composition_v44.*` 生成于 2026-09-04，早于 09-18 CC/RG barcode 重归属修复。本轮在重归属后的 pair 表上重跑 86 号脚本，全部引用数字漂移：

| 指标 | 旧值（pre-CC-fix） | 新值（post-CC-fix，权威） |
|---|---|---|
| pooled 四面板衰减 | −0.8%（median −1.2% [−4.1,+2.6]） | **−1.3%（median −1.2% [−5.0,+2.3]）** |
| TT 内 ρ(k_n, 组成差) | 0.355 pooled（0.15–0.49） | **0.364 pooled（P<10⁻³⁰⁰；0.196–0.513）** |
| \|Δz\| overall3 / overall4 | 1.303（P=7.87e-140）/ 1.227（P=2.66e-74） | **1.305（P=3.57e-137）/ 1.216（P=1.28e-66）** |
| myeloid 单独 | 0.989 P=0.998 | 0.989 P=0.998（不变） |
| per-cancer 衰减 | LIHC +37.1 / KIRC +18.3 / BRCA −16.2 / LUSC −11.1 / LUAD −2.3 | **LIHC +31.7 / KIRC +19.4 / BRCA −15.9 / LUSC −9.5 / LUAD −2.3（区间 −16%~+32%）** |

旧输出归档 `results/superseded/tcga_composition_v44_pre_cc_fix_rerun.*`。定性结论全部不变。

## 三、B 组七脚本（新建，全部落盘）

| 脚本 | 项 | 核心结果 | 输出 |
|---|---|---|---|
| 95_brain_region_matched_v49.py | B1 | astrocytes 小脑内 21 对（与 Bergmann glia 同 7 区），span-matched 梯度 **3.68**（配对中位 4.30 [3.40,4.95]，B=10000）vs 全数据 6.10——梯度存留、幅度降 | nc49_brain_region_matched.* |
| 96_brain_downsample_decomp_v49.py | B2 | equal-n 复现 ω 梯度 1.7406 [1.635,1.836]；**k_f 梯度 2.09 [2.02,2.18] 主导，k_n 梯度 1.29 [1.21,1.41] 方向反转**（全数据 k_n 比 0.31）——残余梯度是 k_f 效应，Bergmann k_n 抬高是类大小伪影 | brain_v49_downsample_replicates_kfkn.csv + summary.json |
| 92_calib_leave_one_out_v49.py | B3 | hepatocyte 12.44±5.98（其余 5.77–7.36）剔后基线 **6.75（−12.3%）**；LOO 范围 [6.75,8.08]，中位 7.12；ω_cal 移 ≤14%，比值结论不变 | nc49_calib_leave_one_out.* |
| 93_luad_group_permutation_v49.py | B4 | whole-tumor label permutation（B=10000 seed42）：KW P=0.0001；KRAS–WT 0.0001、KRAS–EGFR 0.003、EGFR–WT 0.21——排序与显著性保持 | nc49_tcga_luad_mutation_perm.csv |
| 98_luad_logomega_sensitivity_v49.py | C4b | log-ω ANCOVA KRAS coef 0.1699 P=1.24e-05；**KRAS/WT 比 1.185 [1.117,1.257]**——尺度稳健 | nc49_tcga_luad_logomega_sensitivity.csv |
| 94_cc_audit_sensitivity_v49.py | B5+B6 | barcode 审计：五癌种全部仅 source 01/11，**32 LIHC CC 为唯一异常源**；剔 CC 高纯半区 LIHC 1.167→**1.188 [1.005,1.435]**；composition TT 对 291/2000 触 CC；临床 JSON 377 患者含 32 CC | nc49_cc_{barcode_audit,excl_sensitivity}.csv + nc49_cc_audit_report.txt |
| 97_donor_stratified_table_v49.py | A7 | 恒等置换占比全类 ≈0（最大 4.8e-231）；**3/10 类 donor-stratified q<0.05**（astro 0.005 / OPC 0.005 / cOPC 0.043） | nc49_donor_stratified_table.csv |

## 四、A/C 组文本修复

- **A1** Guide 5.3e + 5.7a 两处 softmax 组成检验数字补 superseded 标签（指向 5.8b linear 权威值；pre-reassignment 归档路径申报）
- **A2** Guide 5.8b 补 linear 全套数值（−1.3%/[−5.0,+2.3]/ρ=0.364/1.305/1.216/−16%~+32%）；SI Note 8 linear update 段切 post-CC 新值（上轮已重写，本轮修正 tumor–tumour 混拼）；新增断言 N65b
- **A3** MK 段补第四重对应（split-half 校准基线 ω=7.70 ↔ 多态类，ω_cal ∥ neutrality index 方向）+ 删自评 "substantive rather than nominal"；SI 1.4 同步（上轮）；断言 N53 重铸
- **A4** CL "the first framework" → "the first per-comparison, design-testable implementation"（NC 版 generate_cover_letter_nc.py）
- **A5** Wilson 驳回（见一）；SI 1.6 min cells 10→20（上轮）
- **A6** 密度核查：bootstrap-t 覆盖率（SI 指针）、MC 误差界 ±1.5pp/T2-T3、softmax 等价性推导三处均已在 Methods；B 值分层报告句与 CI 句拆分（上轮）
- **A7** SI Note 12 追加 donor-stratified 透明表段落（指针 97 号 + 恒等置换占比 + 3 存活类）
- **C1** permutation P>0.9 与 bootstrap CI 调和句（上轮，MS）
- **C2** Abstract 保留 "baseline-normalized" 限定 + size-balanced 梯度领衔 + span-matched 3.68 并报；Discussion scope 定位句（上轮）；标题不改（R2/R6 判为编辑权衡项）
- **C3** 聚合顺序包默认声明：MS Methods（v0.5.x brain order，上轮）+ Guide 2 节新增 Aggregation-order default 段（本轮）；top-200 N 敏感性声明补入 Methods Key parameters 句（本轮）；Augur 双 variant 并列 + pyaugur 自报声明 + variant 时序声明（MS 上轮 + SI Note 14 本轮重做成功）
- **C4** Abstract attributable 去因果化（上轮）；log-ω 敏感性（B/C4b 本轮）；TP53 共突变/黏液亚型披露（上轮）
- **C5** SI 1.4 第四条 ascertainment asymmetry（上轮）；constrained reference class 后果集中进化语言化（上轮）

## 五、Abstract 裁剪

本轮新增内容使 Abstract 涨至 211 词（NC 上限 200），裁剪至 **197 词**：divergence metrics→metrics、tumor specimens→tumors、EGFR 句 "in the adjusted model" 删除、span-matched 句压缩。N48 断言短语保留。

## 六、构建断言更新（99_build_nc_v49.py）

- N53 重铸：四重对应短语 + 'substantive rather than nominal' 不在场
- N58/N58b 切 post-CC 口径（−1.3%/0.364/1.31/1.22）
- N65b 新增：SI Note 8 linear = post-CC 口径
- N67–N77 新增：span-matched（3.68×2 处）、equal-n 分解（2.09/1.29/0.31）、LOO（6.75/8.08/7.12）、LUAD 置换（KW P=0.0001）、log-ω（1.19 [1.12,1.26]）、CC 剔除+barcode 审计、SI donor 表、SI Note 14 Augur、CL 限定语、Guide 5.11+superseded+聚合默认、B 组 8 个输出文件存在性

## 七、结论

第三轮全部 A/B/C 项修复闭环：B 组七脚本产出落盘且结论一致支持原判断（梯度存留、KRAS 稳健、CC 无实质影响、校准基线不过度依赖单群体）；composition 口径链三文档统一至 post-CC linear 权威值；两处审稿指控（Wilson、区间硬伤）经独立复算驳回并记录。构建断言 165→~180 项全绿后打包发布。
