# nc59 执行审计报告 — 编号/命名重排 + CL 修订

日期：2026-10-02
范围：任务 #1113（附表首引重排）、#1114（Supplementary Notes 首引重排）、#1115（CL 论调对齐）
方案依据：results/audit/nc59_numbering_naming_plan_2026-10-02.md
施工脚本：results/audit/_nc59_renumber.py

## 一、裁定回顾（四项 AskUserQuestion）

1. 附表按 MS 首引重排映射执行
2. 遵守 NC 现刊风格：附图附表**不加 S 前缀**
3. CL 补脑图句 + TCGA 数字对齐新摘要
4. Supplementary Notes 也按首引重排

## 二、编号映射（ground truth）

### Notes（展开组合引用后 16/16 均在 MS 有首引）
MS 首引序：[1,2,3,4,9,5,16,6,7,8,10,12,11,13,14,15]
映射：1→1, 2→2, 3→3, 4→4, 9→5, 5→6, 16→7, 6→8, 7→9, 8→10, 10→11, 12→12, 11→13, 13→14, 14→15, 15→16
关键修正：盘点时必须展开组合引用（"Supplementary Notes 2–4" para 26 同引 2/3/4；"Notes 1, 5" para 32 引 5），否则 3/4/5 被误判为 MS 无首引。

### Tables（复核确认不变）
映射：1→1, 5→2, 14→3, 2→4, 3→5, 4→6, 6→7, 7→8, 8→9, 9→10, 10→11, 11→12, 12→13, 13→14, 15-19 恒等
MS 首引 [1,5,14,2,3,4]（para 21/45/45/49/51/61）。

## 三、施工内容

### 生成器改号（_nc59_renumber.py 两遍占位符替换法）
- generate_manuscript_nc.py：Notes 40 单引 + 2 组合（"2–4" 恒等、"1, 5"→"1, 6"）+ 2 span-all 保护；Tables 6 单引 + 1 span-all
- notebooks/68_gen_supplementary_nc.py：Notes 55 单引 + TOC 16 + 标题 16；Tables 56 单引 + 4 组合（"11–17"→"12–17"、"12 and 13"→"13 and 14"、"15–17"/"16 and 17" 恒等）；3 注释行中和；"Tables S3 and S4"→"Tables 5 and 6" 遗留修复；4 处 "(sheet Table N)" 指针改号
- notebooks/100_gen_reproducibility_nc.js：Notes 3 处（8→10×2、13→14）+ Table 1 处（5→2）
- SI 16 章节块物理重排（块移动安全性已验证：跨块依赖均先于 Notes 区定义）；TOC 位置代入法重排
- xlsx writer `_plan` 19 项显式映射重排，sheet 名 + A1 标题统一按新号

### 组合引用处理（关键坑）
- 单数字正则只命中组合首数字 → 组合正则整体捕获、内部按分隔符 tokenize 逐数字映射、@@C@@ 保护壳
- 字面 \u2013 转义陷阱："2\u20134" 内 \d+ 会吞 "20134" → 先 tokenize 再映射纯数字 token
- 脚本不可重入：中途失败必须 git checkout 回滚再重跑

### 断言同步（12 处 + 1 历史脚本）
- _nc49_ms_verify.py L236（severity Note 9→5）
- _nc49_si_verify.py L94-106 九处（含 2 处假阳性 PASS 主动修正：L96→8、L99→11）
- 99_build_nc_v49.py L242（Guide Note 13→14）、L526（'Table 5)'→'Table 2)'、'Table 14)'→'Table 3)'）、L588（Note 10→11）
- _v054_cross_validation.py L152 worksheets[4]→worksheets[1]（two-caliber 旧5→新2）
- _nc49_cl_guide_verify.py：'CL CC new ranges (v53)' 替换为 2 条 v59 断言（TCGA 对齐 + 四支柱）

### #1115 CL 修订（generate_cover_letter_nc.py）
1. Pillar 3 TCGA 改写：删 "NN/TT ω ratio 1.11–2.46, bootstrap CIs excluding 1 in four of five" 与 "1.3–3.3-fold elevated housekeeping baseline, not reduced functional divergence"，改为对齐新摘要："tumors appear consistently less divergent than adjacent non-tumor tissue—a pan-cancer reversal driven by an elevated housekeeping baseline rather than reduced functional divergence"
2. 新增第四支柱："Fourth, in a human brain atlas spanning 108 regions, CKI quantified a regional differentiation gradient and provides a statistically calibrated framework for atlas-scale comparisons."；"three pillars"→"four pillars"
3. 文件头注记补 v59 变更说明

## 四、验证链（全绿）

| 环节 | 结果 |
|---|---|
| MS Notes 首引单调 | [1..16] ✓ |
| MS Tables 首引单调 | [1..6] ✓ |
| SI 章节物理序 | 新序正确 ✓ |
| xlsx 19 sheet + A1 标题 | 新序全对 ✓ |
| 构建 99_build_nc_v49.py | **218/218 PASS** |
| XV8 交叉验证 | **63/63 ALL PASS** |
| pytest tests/ | **29 passed** |
| CL+Guide 自验 | 42/42 PASS，CL 513 词（≤530 一页预算内） |

## 五、遗留 / 后续

- v0.5.5 phase-2 挂起：Zenodo version DOI 后台轮询（task 9A6kDx，代理 502 噪音，建档基线 ~91-97 分钟）→ DOI 回写 MS Code availability + 断言同步 → 重建 → 刷新 Release 401857516 资产（须含 nc59 全部变更）→ phase-2 commit/push
- 主目录 zip：version3/CKI_Submission_v50_NC.zip（13,880,601 B，本次重建刷新）
