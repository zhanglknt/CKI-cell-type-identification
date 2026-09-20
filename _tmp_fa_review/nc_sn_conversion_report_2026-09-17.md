# CKI Supplementary Notes -> NC 格式转换报告

- 日期：2026-09-17
- 输入：`notebooks/68_gen_supplementary_en.py`（未改动）
- 产出：`notebooks/68_gen_supplementary_nc.py` + `results/CKI_Supplementary_NC.docx`
- 构建脚本：`_tmp_fa_review/build_nc_sn.py`（全部锚点断言通过）

## 1. Note 重编号映射（旧 -> 新，与文稿侧一致）

| 旧编号 | 新 Supplementary Note | 标题 |
|---|---|---|
| 3.12 | 1 | Ground-Truth Simulation |
| 3.21 | 2 | Small-Cluster Bootstrap Corrections for Region-Clustered CIs (v45) |
| 3.5 | 3 | Calibrated Omega Normalization |
| 3.20 | 4 | Ratio-Estimator Bias\u2013Variance Characterization (v45) |
| 3.22 | 5 | Non-HK-Anchored Neutral Drift Controls (v45) |
| 3.15 | 6 | Real Perturbation Demonstration (Kang et al. IFN-beta PBMC) |
| 3.13 | 7 | Fixed Gene-Panel Ablation |
| 5.2 | 8 | TCGA composition-contribution check for the NN/TT k_n reversal |
| 3.16 | 9 | k_f-only Ordering Controls (Cross-Organ Ranking and TCGA Severity) |
| 3.17 | 10 | Brain Class-Size Confounding Controls and min-cells Threshold Sensitivity (v44) |
| 3.14 | 11 | Region Glossary (Siletti et al. Dissection Nomenclature) |
| 4.6 | 12 | Pseudo-Region Negative Control (Block-Shuffle Null Calibration) |
| 5.1 | 13 | Brain set-level enrichment of the block-shuffle signal (post-hoc) |
| 3.23 | 14 | Comparison with Augur Cell-Type Prioritization (v45) |
| 3.6 | 15 | JS Divergence Dimensionality Invariance |

## 2. 结构调整

- 原 5 个 'Supplementary Note 1-5' 大节标题去前缀降级为普通章节标题：CKI Mathematical Derivation / CKI Algorithm Pseudocode / Statistical Testing Details / Dataset Quality Control and Filtering Criteria。
- 原 Note 5 大节（Post-hoc Coherence Checks）的两个子节 5.1/5.2 均在映射表内被抽出，该大节标题已删除（避免空节）。
- 15 个被引用小节物理重排为 Supplementary Note 1-15，置于 4 个主题节之后、Supplementary Tables 之前；节间保留分页符（6 个）。
- 未被正文引用的小节（1.1-1.7、3.1-3.4、3.7-3.11、3.18、3.19、4.1-4.5）原地保留十进制编号，文内引用统一改写为 Section X.Y。

## 3. 替换计数

- **markers**: sub=38 grp=5 pb=6 tbl=4 cmt=5
- **note headings converted**: 3.12->1; 3.21->2; 3.5->3; 3.20->4; 3.22->5; 3.15->6; 3.13->7; 5.2->8; 3.16->9; 3.17->10; 3.14->11; 4.6->12; 5.1->13; 3.23->14; 3.6->15
- **HEAD**: docstring, title 'Supplementary Information', TOC rebuilt (24 entries)
- **Notes 3.12 and 3.15 -> Supplementary Notes 1 and 6**: 1 replacement(s) [literal]
- **Note 3.12's -> Supplementary Note 1's**: 1 replacement(s) [literal]
- **Additional file 1: Fig. S10 -> Supplementary Fig. 10**: 1 replacement(s) [literal]
- **note references**: 1.1x1; 1.7x3; 3.12x1; 3.15x4; 3.16x2; 3.17x1; 3.18x1; 3.19ax1; 3.19bx1; 3.19cx1; 3.21x1; 3.5x1; 5.2x1
- **SN 1.5 -> Section 1.5**: 1
- **figure refs**: S2x1; S3x1; S7x1; S9x1; S12x1; S13x1
- **table refs (headings+body; TOC rebuilt separately)**: S1x3; S2x2; S3x3; S4x2
- **panel labels (A)-(E)**: 0 occurrences (no replacement needed)

## 4. DOCX 自检结果（全部通过）

- [x] residual Note X.Y — clean
- [x] residual SN X.Y — clean
- [x] residual Fig. S — clean
- [x] residual Figure S — clean
- [x] residual Table S — clean
- [x] residual Additional file — clean
- [x] residual Supplementary Materials — clean
- [x] py_compile 68_gen_supplementary_nc.py — ok
- [x] generator run — Saved: results/CKI_Supplementary_NC.docx | Paragraphs: 196
- [x] DOCX residual Note X.Y — clean
- [x] DOCX residual Notes X.Y — clean
- [x] DOCX residual SN X.Y — clean
- [x] DOCX residual Fig. S — clean
- [x] DOCX residual Figure S — clean
- [x] DOCX residual Table S — clean
- [x] DOCX residual Additional file — clean
- [x] DOCX residual Supplementary Materials — clean
- [x] Supplementary Note 1-15 headings in order — [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
- [x] TOC Supplementary Note 1-15 in order — [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
- [x] TOC titles == heading titles
- [x] Supplementary Fig. count == original Figure/Fig. S count (7) — new=[2, 3, 7, 9, 10, 12, 13]
- [x] Supplementary Table count == original Table S count (14) — new=[1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4]
- [x] document title 'Supplementary Information'
- [x] panel labels (A)-(E) in DOCX — 0
- [x] Section X.Y refs (uncited subsections) — 1.1, 1.5, 1.7, 3.18, 3.19a, 3.19b, 3.19c

## 5. 偏差与说明

- 'Additional file 1: Fig. S10.'（全文唯一 Additional file 出现）按语境转换为 'Supplementary Fig. 10.'，而非字面替换为 'Supplementary Information'（后者语义不通）。
- 面板标签 (A)-(E)：本生成器输出文本中 0 出现（面板标签在主文稿与图 PDF 内，不在本文件），无需替换。
- 跨字面量换行的引用 2 处已定点处理：'see also Notes 3.12 and 3.15'、'Note 3.12\u2019s'。
- 统计正文 (S1)/(S2) 为 split-half 重复标签（L910 附近），非面板/图引用，未改动。
- `\uXXXX` 字面转义全部按原样保留（纯文本级手术，未经过编解码）。
