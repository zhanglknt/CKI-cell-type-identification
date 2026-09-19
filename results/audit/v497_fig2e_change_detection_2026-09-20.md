# v49.7 — Figure 2E 场景替换审计（分类 ROC → 变化检测 ROC）

日期：2026-09-20（GMT+8）｜触发：一作科学判断 —— "CKI ω AUC 那么低，说明场景不对。应该展示 AUC 第一的场景。CKI 不是用来做细胞类型的，是用来看细胞类型的变化的。"

## 决策
方案 A（只换 E）：主图 Figure 2E 由 Tabula Sapiens 细胞型分类 ROC（CKI ω AUC = 0.680，5 指标垫底）替换为 ground-truth 模拟的功能变化 vs 中性漂变检测 ROC（CKI ω AUC 第一）。Panel D（TS 五指标相关性热图）保留；Table 1 保留分类性能作诚实披露。

## 数值核验（复算对齐，定义锚定）
- 定义：positives = signal & δ ≥ 0.25（600 reps）；negatives = neutral_hk + neutral_global（250 reps）；roc_auc_score。
- marrow（groundtruth_simulation_raw.csv vs metrics.json）：6/6 指标全对齐 —— ω 0.8042 / k_f 0.7159 / k_total 0.6401 / cosine 0.5842 / kf_over_kt 0.4370 / k_n 0.2127。
- skin 背景2（background2_raw vs background2_metrics.json）：6/6 全对齐 —— ω 0.9076（rank 1/6）。
- 与 SI line 1551 定义（"functional (delta ≥ 0.25) from neutral"）一致。

## 产物
- 新建 notebooks/_regen_fig2_bottomrow_v497.py：底排整排原生重绘（取代 v47 抠图+白底重标）。
  - D = TS 五指标相关性热图（results/figure_data_correlations.npy，内容不变）。
  - E = 6 指标变化检测 ROC（marrow），标题注释皮肤背景独立复现 ω AUC = 0.91 (rank 1/6)。
  - 178×72mm；纯 Arial ≥7pt（主文本 69 段 7.0–9.0pt；仅 mathtext 下标 4.9pt，与包内既有规范一致）；原生面板标签 D/E（Arial Bold 9pt）；Type 42。
- 新建 notebooks/_merge_fig2_v497.py：顶排（178×74mm）+ 6pt 间距 + 新底排 → results/figures_final/figure2_merged_nc49.pdf = 178.0×148.1mm（几何与 v49.6 完全一致）。
- 合并图字体审计：Arial-BoldMT/ArialMT + DejaVuSans-Oblique（mathtext）；≥7pt 主文本 144 段。

## 文稿同步（generate_manuscript_nc.py，5 处原子替换+读回）
1. Fig 2 图注标题：→ "...metric correlation structure on Tabula Sapiens, and functional-change detection in the ground-truth simulation."
2. 图注 (e)：→ 变化检测 ROC 完整描述（600 vs 250 reps、ω 第一 AUC = 0.80、皮肤复现 0.91、分类性能指向 Table 1）。
3. Result 3 锚点：(Fig. 2d, e) → (Fig. 2d)。
4. Result 3b AUC 句：加 "(Fig. 2e; AUC = 0.80, ..."。
5. Result 3b 背景2 句：加 "(Fig. 2e)"。
Table 1 段落（AUC = 0.680, ranked 5th of 5, "expected by design"）逐字未动。

## 断言联动
- results/audit/_nc49_ms_verify.py：新增 7 条 11b 断言（新图注、旧图注退场、锚点收窄、两处 Fig. 2e 引用、Table 1 保留）。
- 99_build_nc_v49.py：staging 接入 _regen_fig2_bottomrow_v497.py + _merge_fig2_v497.py；N21b 断言同步为新图注。
- results/audit/_nc49_cl_guide_verify.py：修复 v49.6 重编号遗留 stale 断言（Guide mean-ratio caliber 期望 'Fig. 5a' → 实际 TCGA 已是 Figure 4，改 'Fig. 4a'）。该失败与本次 Fig2E 无关，属 v49.6 7→6 重编号漏改。

## 构建与验证
- CKI_BUILD_NO_ARCHIVE=1 全量构建：**129/129 PASS**（旧 zip 已先备份 _tmp_archive/v496_zip_backup/；safe-delete 钩子拦截走 NO_ARCHIVE 约定）。
- MS verify 112/112、SI verify 109/109、CL+Guide verify 39/39。
- 包核验：CKI_Submission_v49_NC.zip = 12,259,408 B、27 条目、sha16 01a0e61cc1bbdb1f；包内 figure2.pdf 与本地合并图字节一致（sha16 a4cff9b23e202009）；包内 MS docx 8/8 文本断言全过。
- Abstract headline "ranked first for functional-versus-neutral discrimination (AUC = 0.80)" 现有主图（Fig. 2e）支撑，图文闭环。
