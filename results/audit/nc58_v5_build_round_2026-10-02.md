# nc58 — v5 一作反馈轮 构建+验证 审计报告（2026-10-02）

承接：nc58_v5_firstauthor_adjudication_2026-10-02.md（11 条裁定矩阵）。
本轮执行用户裁定：[7] 软合并、[12] SF14→SF3 加 UMAP 面板、[8][9] 完全单调重排；一作全部图片替换进包。

## 1. 图片替换（任务 #1110）

- **figure4 C/D 标签机械修复**：一作版图只有 A/B 标签（NC 硬性要求 + [10] 引 Fig. 4c,d 前提）。
  fitz 叠加 Arial Bold 9.0pt：C@x=280.2/y≈10.4、D@x=429.2/y≈10.4（A 模式：标签=标题 x0−30.2；
  实测 A@20.6/B@184.2，标题 "k_f component"@310.4、"k_n baseline"@459.4）。
  产物 results/figures_v58_author/figure4.pdf（1,171,966 B），300DPI 渲染复核通过（v5/preview/figure4_labels_fixed.png）。
- **results/figures_v58_author/ 组装（21 文件）**：
  - 主图：figure1/5/6 未动（拷自 v47 staging，md5 与一作版一致）；figure2/3 一作重绘直拷；figure4 修复版。
  - 附图映射（一作文件名 → 终号，基于 md5 内容同一性，与文本重编号互补自洽）：
    其 SF1→S1、SF2→S2、SF4→S4、SF5→S5、SF6→S6、SF7→S7、SF8→S8、SF9→S9、
    SF11→S10、SF12→S11、SF13→S12、SF10→S13、SF3→S14；S3=microglia 由 nc50_fig_microglia.py 重跑生成。
  - CKI_graphical_abstract.pdf 拷自 v47。
- **99_build_nc_v49.py staging 改写**：STAGE→figures_v58_author；停用 fig2 三脚本重跑（其产物会覆盖一作图版）；
  figure2/3/4 改从 STAGE 直拷；supp 循环 1..14 跳过 3；microglia 重跑段改输出 Supplementary_Fig_3.pdf。

## 2. 断言同步（首轮构建 211/218 → 7 FAIL 全修复）

| 失败项 | 根因 | 处置 |
|---|---|---|
| run: MS self-check | 10 条断言锚定 v52 摘要/旧编号 | _nc49_ms_verify.py 7 组替换（摘要 4 条锚定一作新摘要措辞；SF14→SF3 图注；KRAS/EGFR 两条改锚 Results 句；severity SI 4b→5b；Kang-brain 改锚 "ω FPR grows with group size"；cross-organ SF5→6） |
| run: SI self-check | Note 9 "(Supplementary Fig. 4b)" | →5b（旧 4→终 5） |
| run: CL+Guide self-check | 旧 "SF12→SF11" 断言过时 | 改锚 cross-species=SF12 两处、无 SF11 残留 |
| V49-A3 | gradient 句一作改措辞 | 锚 "combined span- and size-matched control yields 3.66 (donor-level bootstrap [1.92, 3.78]"（同值更精确，3.66[1.92,3.78]=旧 3.7[1.9,3.8]） |
| V49-N37 | cross-organ 引用 SF5→6 | 同步 |
| V49-N48 | 摘要不再含 gradient 句 | 改锚新摘要 "quantified a regional differentiation gradient and provided a statistically calibrated framework" |
| V49-N52 | Guide estimator 指针 7→8 | 同步（终映射旧 7→8） |

## 3. 词额（XV8 口径实测）

- 首轮 MAIN 5,013/5,000（含小标题）超帽 13 → 生成器 7 处外科手术削减（−21）：
  Intro 3 处（删 "—a pattern we dissect in Results"−6；"demonstrating that"→冒号−2；"after excluding"→"excluding"−1）；
  Discussion [15] 句压缩 −7（"bounds atlas-scale effect sizes rather than proving absence"，保义）；
  L555 SF8 指针 −2；合并段 framing −2、"largely" −1。
- **终态：MAIN 4,994/5,000（含小标题；4,937 不含）、摘要 168/200、Methods 2,936/3,000**。
- 被削短语经 grep 确认无任何断言锚定。

## 4. 终验链（全绿）

- 99_build：**218/218 PASS**（含 MS 127 + SI 121 + CL/Guide 41 自检内嵌）
- XV8：**63/63 ALL PASS**
- pytest：**29/29**（3.34s）
- zip 字节级核验：Supplementary_Fig_3.pdf=results 源 md5 2a8b260a7e ✓、figure4.pdf=95d287d564 ✓、Supplementary_Fig_14.pdf=cc8364895e ✓
- 主目录 CKI_Submission_v50_NC.zip 已刷新（13,880,257 B，28 entries）

## 5. 遗留决策项

- **版本/发布**：本轮改动面（MS 文本+全部图版+重编号）大于 nc57 cover-letter 微修（当时原位刷资产）。
  是否切 v0.5.5（新 tag+Zenodo version DOI→MS Code availability 回写）或沿 v0.5.4 原位刷资产，待用户裁定。
