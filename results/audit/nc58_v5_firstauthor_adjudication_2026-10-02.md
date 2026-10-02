# nc58 — 一作 v5 反馈裁定矩阵（2026-10-02）

来源：v5/extracted/v50问题.docx（11 条）+ v5/extracted/CKI_Manuscript_NC.docx（66 ins/56 del 修订，7 段 diff：para 7/11/12/13/14/36/196）+ v5/extracted/figures/（20 张 PDF）。
底稿与当前 MS 相似度 98.83%（仅 Figure 3 图注段基线不同：其底稿 Kang 文本在 (a)/(d) 重复）。

## 一、11 条反馈处置矩阵

| # | 反馈 | 裁定 | 实施 |
|---|------|------|------|
| 1 [3] | Abstract 改为"背景→问题→方法→证据→意义"，去不必要数字，"framework"升格 | **采纳**（其 docx 已改，167 词） | 移植 para7 + 修 5 处机械错误（下表） |
| 2 [4] | Introduction 去结果数字/防御表述，结尾改贡献声明 | **采纳**（其 docx 已改 para11-14） | 移植 + 修 6 处机械错误 |
| 3 [6] | Fig. 3d→3a，d 图挪到 a 位，删原 a（schematic） | **采纳** | para36 Fig.3d→3a；图注重构为 a=Kang/b=脑校准/c=FPR；(b) 补紧凑 tier 释义保图注自足；其重绘 figure3.pdf 版面已核验 = 新布局 |
| 4 [7] | IFN-β/Benchmarking/Fixed-panel ablation 三个"防御性"小节是否合并 | **讨论项 Q1** | 三小节 L522/526/530 各一段（~100 词×3），系 GB 反驳骨干证据 |
| 5 [8] | SF2/7/12 正文未引用；首引顺序乱（14 在 3 前） | **采纳（补 3 处引用）+ 讨论项 Q3（残留乱序）** | 补引：SF2@L487（9.73 基线句）、SF3@L694（ω 分布特征句）、SF8@L561（k_n 分析句） |
| 6 [9] | SF3 起标号错位，已重命名图片文件 | **采纳**（映射 old→new：3→4,4→5,5→6,6→7,7→8,8→9,9→11,10→12,11→13,12→3,13→10；1,2,14 不变） | MS+SI 全文引用两遍占位符替换；图注节按新序重排；STAGE 换其文件 |
| 7 [10] | Fig. 4 正文补 c/d 引用 | **采纳** | L540 "P = 0.015" 后加 (Fig. 4c, d)；c=k_f 分层，d=k_n 分层 |
| 8 [11] | Supplementary Note 15 正文未引用 | **采纳** | Note 15 = JS 维度不变性 → L644（Methods，与 SF13 同句）加 Supplementary Note 15 |
| 9 [12] | SF14 legend 1.30±0.36 不清；建议加自研 microglia/CNS-Mφ UMAP 为 A 图 | **legend 澄清采纳；UMAP = 讨论项 Q2** | legend 改 "ω = 21.83 ± 7.20 functional versus ω = 1.30 ± 0.36 neutral half-splits"；UMAP 数据本地有（data/human_brain_atlas_microglia.h5ad） |
| 10 [14] | Discussion "k_f follows neutral housekeeping drift (AUC 0.98)" 改 "k_f retains full separation of perturbation from donor drift (AUC 0.98)" | **采纳** | L593 改写，数值不变、更准确 |
| 11 [15] | "the absence of FDR-significant signals is itself informative" 改 "constrains the effect size of atlas-scale candidate genes rather than demonstrating their absence" | **采纳** | L605 末句替换；L629 结论段平行句保留（已是 bound 措辞） |

## 二、其 docx 修订的机械错误修复清单（采纳意图 + 修伤）

| 段落 | 机械错误 | 修复 |
|------|----------|------|
| para7 摘要 | "drift.Inspired" | "drift. Inspired" |
| para7 摘要 | "Ka/Ks ," | "Ka/Ks," |
| para7 摘要 | "cell-typeidentity" | "cell-type identity" |
| para7 摘要 | "whithe best" | "with the best" |
| para7 摘要 | "among five metrics (AUC = 0.80)" | **six** metrics（ground truth：Fig 2e 图注 six metrics，CL 同） |
| para11 | "Weadopt" | "We adopt"；段尾 ":" 改 "."（下段独立成句） |
| para12 | "define a functional divergence rate a baseline..."（丢 k_f 定义） | "We define a functional divergence rate k_f from cell-type identity genes, a baseline divergence rate k_n from housekeeping (HK) genes, and report..." |
| para13 | "k_f(Results; Discussion) and ." | "its components k_f and k_n (Results; Discussion)." |
| para14 | "inrandom" | "in random" |
| para14 | "Having established its statistical properties."（残句） | 删除；"On TCGA" 改 "Fourth, on TCGA" 保递进（First/Second/Third/Fourth/Finally） |
| para14 | "procell-type/region pairs" | "profile cell-type/region pairs" |
| para196 图3图注 | 尾部残留无标签 Kang 段（与 (a) 重复） | 删除；(b) 补 tier 紧凑释义（T1 同 donor 2,161 对/T2 跨 donor 1,089/T3 跨 region 1,656 + n-matched null） |

词额：摘要 195→167（余量 33）；MAIN 预计 4,998→~4,930（5,000 帽下安全；另加回 [10][11][15] 引用/句 ~25 词）。

## 三、图片处置（md5 精确映射）

- **重绘 4 张**：figure2（111,688→323,495 B；A-E 标签齐）、figure3（76,661→199,821 B；A=Kang/B=校准/C=FPR 已渲染核验）、figure4（83,719→1,768,288 B）、SF1（55,172→45,335 B；A-C 标签齐）
- **figure4 缺陷**：其重绘版只有 A/B 两个面板标签，k_f/k_n 两面板缺 C/D 标签（NC 面板标签硬性要求，且 [10] 要引 c/d）→ **直接机械修复**：fitz 叠加 Arial-BoldMT 9pt "C"@x≈308/y=10.5、"D"@x≈457/y=10.5（与 B 标签同款同位），不改其设计
- **置换 13 张**（字节不变仅改名）：其文件已是新编号 → STAGE figure_S1..13 整体替换
- **未动 4 张**：figure1/5/6 + SF14（SF14 由 nc50_fig_microglia.py 重建产物字节相同，无需处理）
- **build 适配**：99_build 对 figure3/4 改拷贝源为 v5 版；figure2 在 merge 步骤后覆盖为其重绘版（build 会用脚本重生成旧版，必须后置）

## 四、讨论项（待用户裁定）

### Q1 [7] 三个"防御性"小节是否合并
- 现状：L522（IFN-β demonstration）/L526（MELD、scDist benchmark）/L530（fixed-panel ablation），各 1 段 ~100 词，三段 ~300 词
- 选项 A（软合并）：并为一个 level-2 小节 + 一段，内部 First/Second/Third 连接，证据零删除；段长 ~300 词可接受
- 选项 B（保持）：三小节不动，回复一作说明理由（三段是 GB 两轮审稿反驳的骨干证据，各自回答不同问题：anchor 边界/检测功率边界/面板循环性）
- 倾向：A（采纳其"降低防御性视觉占比"意图且不损证据）

### Q2 [12] SF14 加自研 microglia/CNS-Mφ UMAP 面板 A
- 可行性：data/human_brain_atlas_microglia.h5ad 在本地（91,838 nuclei），scanpy 子采样 + UMAP + 叠加细胞类型着色，~1h；SF14 变 2 面板（a=UMAP, b=ω 分离），legend 加 (a) 描述
- 利：图更直观、回应其 legend 可读性疑虑；弊：新增分析产物 + 图版面变化 + 断言同步
- 倾向：做（其建议无实质错误，按"默认采纳"规则应做；数据现成）

### Q3 [8][9] 重编号残留乱序
- 其改名后首引顺序（含补引）= [1,2,14,4,5,6,7,8,9,11,12,13,10,3]：SF14 仍第 3 位（在 SF4 前），Methods 尾部 10 在 3 前 —— 他自己的投诉（"14 出现在 3 前"）只修了一半
- 选项 A（沿用其编号）：残留 SF14 一处 + Methods 尾两处乱序；其文件名不动
- 选项 B（完全单调）：按正文首引顺序再排——old14(microglia)→SF3、old3→SF4、…、old12(ω分布)→SF14、old13→SF13；首引 = 完美 1→14；其 PDF 文件名在 STAGE 层再映射（其原文件不动），需向他说明"我们把你的编号又顺了一遍"
- 倾向：B（彻底实现其 [8] 意图；NC 对附图引用顺序有明确要求）
