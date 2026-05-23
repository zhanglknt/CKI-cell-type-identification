# CKI 投稿 NAR — 最终交付清单

生成时间: 2026-05-23 23:52
目标期刊: Nucleic Acids Research (NAR)
GitHub: https://github.com/zhanglknt/CKI-cell-type-identification

---

## 一、交付文件总览

### A. 核心稿件文件

| # | 文件路径 | 说明 | 大小 |
|---|---------|------|------|
| 1 | results/CKI_NAR_Manuscript_v4.docx | 主稿件（含标题、摘要、正文、图注、36篇参考文献） | 57 KB |
| 2 | results/CKI_NAR_Manuscript_v4.pdf | 主稿件PDF版（Word导出） | 352 KB |
| 3 | results/CKI_NAR_Cover_Letter.docx | 投稿信（含ORCID: 0000-0002-0698-0754） | 38 KB |

### B. 图表文件（results/figures_final/）

| # | 文件名 | 描述 | 面板数 | 格式 |
|---|--------|------|--------|------|
| 1 | figure1_concept_pipeline | CKI框架：Ka/Ks类比 + 分析流程 + Bootstrap校准 | 3 | PNG+PDF |
| 2 | figure2_calibration_tabula_muris | Tabula Muris校准：k_f/k_n分解 + 基因JS距离 | 4 | PNG+PDF |
| 3 | figure3_orthogonal_information | 正交信息维度：omega vs 传统距离指标 | 4 | PNG+PDF |
| 4 | figure4_tcga_pancancer | TCGA泛癌分析：NN/TT比率 + PAM50验证 | 4 | PNG+PDF |
| 5 | figure5_cross_organ_conservation | 跨器官保守性：59对同细胞类型跨器官比较 | 3 | PNG+PDF |
| 6 | figure6_brain_regional_cki | 脑区CKI：888,263核 + 108脑区 + 8倍omega梯度 | 5 | PNG+PDF |
| ED1 | ed_fig1_parameter_sweep_pathway | 参数扫描 + 通路富集 | 2 | PNG+PDF |
| ED2 | ed_fig2_cross_species_validation | 跨物种验证（鼠→人） | 2 | PNG+PDF |
| ED3 | ed_fig3_tcga_per_cancer | TCGA各癌种矩阵 | 3 | PNG+PDF |
| ED4 | ed_fig4_method_comparison_auc | 方法学比较ROC-AUC | 1 | PNG+PDF |
| ED5 | ed_fig5_cross_organ_table | 跨器官原始数据表 | 1 | PNG+PDF |
| ED6 | ed_fig6_brain_analysis | 脑区分析详情 | 3 | PNG+PDF |
| ED7 | ed_fig7_migration_candidates | 迁移候选分析（OPC等） | 5 | PNG+PDF |

### C. 合并PDF

| # | 文件路径 | 说明 | 大小 |
|---|---------|------|------|
| 4 | results/CKI_NAR_Combined_Submission.pdf | 稿件+13张图表合并版（适合审稿人阅读） | 0.9 MB |

### D. 辅助文件

| # | 文件路径 | 说明 |
|---|---------|------|
| 5 | results/NAR_SUBMISSION_CHECKLIST.md | 投稿合规检查清单 |
| 6 | results/NAR_最终交付清单.md | 本文件 |

---

## 二、稿件技术参数

| 参数 | 值 | NAR要求 | 状态 |
|------|-----|---------|------|
| 文章类型 | Standard Research Article | — | ✓ |
| 摘要字数 | 189 words | ≤200 words | ✓ |
| 正文字数 | 5,875 words | 6,000-10,000（典型） | ✓ |
| 参考文献数 | 36篇 | 不限 | ✓ |
| PubMed可查 | 36/36 (100%) | 建议全部可查 | ✓ |
| 引用格式 | 括号数字 (1),(2,3),(4-7) | NAR parenthetical | ✓ |
| 参考文献格式 | Author, A.B. (Year) Title. *Journal.*, **Vol**, Pages. | NAR标准 | ✓ |
| 图表尺寸 | 单栏86mm / 双栏178mm | NAR规格 | ✓ |
| 图表分辨率 | 300 DPI | ≥300 DPI | ✓ |
| 图表字体 | Arial 7pt | Arial ≥6pt | ✓ |
| 图表格式 | PDF(矢量) + PNG(光栅) | TIFF/EPS/PDF | ✓ |
| ORCID | 0000-0002-0698-0754 | 建议提供 | ✓ |
| GitHub | https://github.com/zhanglknt/CKI-cell-type-identification | 建议公开 | ✓ |

---

## 三、参考文献验证状态

总计36篇参考文献，全部PubMed可查（100%验证通过）。

已删除的6篇非PubMed文献及其替换：
- Lin 1991 IEEE → numpy/scipy直接引用
- Efron 1979 Ann Stat → Bootstrap方法描述
- Benjamini 1995 JRSSB → Storey 2003 (PMID 12883005)
- Megill 2021 bioRxiv → CZ CELLxGENE Discover 2025 (PMID 39607691)
- Pedregosa 2011 JMLR → scikit-learn直接引用
- Sepp 2026 PNAS → Yang 2024 (PMID 38409116)

---

## 四、投稿流程（NAR ScholarOne）

### 投稿入口
http://mc.manuscriptcentral.com/nar

### 步骤指引

1. 注册/登录 ScholarOne Manuscripts
2. 选择 "Submit a Manuscript" → "Nucleic Acids Research"
3. 填写稿件信息：
   - Title: "CKI: A Cell-state Kinetic Index for Quantifying Selective Transcriptomic Remodeling"
   - Article Type: Standard Research Article
   - Corresponding Author: Li Zhang (knightz@pumc.edu.cn, ORCID: 0000-0002-0698-0754)
4. 上传文件：
   - Manuscript: results/CKI_NAR_Manuscript_v4.docx
   - Cover Letter: results/CKI_NAR_Cover_Letter.docx
   - Figures: results/figures_final/ (单独上传或合并PDF)
   - Supplementary: results/CKI_NAR_Supplementary_Info.docx（如有）
5. 填写作者信息（全部作者姓名+单位）
6. 确认利益冲突声明
7. 提交

### 作者待确认事项

- [ ] **终稿通读**：作者亲自全文校对一遍
- [ ] **作者名单**：确认全部作者姓名和单位无误
- [ ] **通讯作者信息**：knightz@pumc.edu.cn, ORCID 0000-0002-0698-0754
- [ ] **GitHub仓库**：确认代码仓库可以公开访问，README完整
- [ ] **数据可用性声明**：确认数据引用和获取方式描述准确
- [ ] **补充材料**：确认补充信息文件完整

---

## 五、快速命令参考

```bash
# 重新生成稿件（如需修改后）
cd /c/Users/KnightZ/Desktop/细胞受选择
python generate_manuscript_v4_nar.py

# 重新生成Cover Letter
python generate_cover_letter_nar.py

# 重新生成合并PDF
python generate_combined_pdf.py

# 推送GitHub
git add <files> && git commit -m "message" && git push origin main
```

---

## 六、版本历史

| 版本 | 日期 | 主要变更 |
|------|------|---------|
| v1 | 2026-05-22 | 初稿（NBT格式，39篇参考文献） |
| v2 | 2026-05-23 | NAR格式转换（引用格式、图表尺寸） |
| v3 | 2026-05-23 | 删除重号、修正PMID、ED Fig2 bug修复 |
| v4 | 2026-05-23 | PubMed验证→删除6篇→替换3篇→36篇 |
| v5 Final | 2026-05-23 | ORCID添加、GitHub推送、合并PDF、最终清单 |
