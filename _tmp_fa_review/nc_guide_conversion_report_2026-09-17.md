# NC 命名改造报告：复现指南（Additional file 2）

- 日期：2026-09-17
- 执行人：nc-guide
- 源文件：`notebooks/100_gen_reproducibility_docx.js`（未改动）
- 新生成器：`notebooks/100_gen_reproducibility_nc.js`
- 产出：`results/CKI_Reproducibility_Guide_NC.docx`（37.6 KB）
- 实施脚本：`_tmp_fa_review/build_nc_guide.py`（锚点断言，全部通过后一次性写文件）
- 自检脚本：`_tmp_fa_review/verify_nc_guide.py`（python-docx 全文提取，VERIFY PASS）

## 替换明细（源文件锚点计数 → 替换结果）

| 类别 | 锚点 | 计数 | 结果 |
|---|---|---|---|
| 输出路径 | `results/CKI_Reproducibility_Guide.docx` | 1 | `results/CKI_Reproducibility_Guide_NC.docx` |
| Note 重编号 | `Supplementary Note 5.1`（5.7e 节） | 1 | `Supplementary Note 13`（映射 5.1→13） |
| Note 引用 | `Supplementary Note 3.11`（5.5j 节，Parameter Justification） | 1 | `Section 3.11 of the Supplementary Information (Parameter Justification)`（team-lead 定稿：3.11 为正文未引用小节，按方案 B 保留十进制小节，不获 Supplementary Note 编号） |
| 附图 | `Supplementary Fig. S8` ×1、`Supplementary Fig. S12` ×2 | 3 | `Supplementary Fig. 8` / `Supplementary Fig. 12` |
| 附图 | `Fig. S10`（5.7f 节 script 行） | 1 | `Supplementary Fig. 10` |
| 附图 | `Supplementary Figure 1`（3.2 节，写法不统一） | 1 | `Supplementary Fig. 1` |
| 附表 | `Table S\d+` | 0 | 无需处理 |
| Additional file | `Additional file 1:` / 任意 `Additional file` | 0 | 指南无此字样；亦无自称 Additional file 2 处 |
| 面板标签 | `Fig. 4A`（4.3 节） | 1 | `Fig. 4a` |
| 面板标签 | `Panel A over Panel B`（5.9f 节） | 1 | `panel a over panel b` |
| 期刊表述 | 头部注释 `NAR-compliant DOCX` | 1 | `Nature Communications-compliant DOCX`（仅代码注释） |
| 期刊表述 | 正文 `Genome Biology` | 0 | 无残留；`notebooks/30_genome_biology_figures.py` 为真实脚本文件名，原样保留 |

## 防循环与边界处理

- Note 重编号采用占位符两步法（`Supplementary Note @@N@@` → 定稿），映射为 team-lead 统一 15 条；旧 3.11 单独走 SI 小节引用规则。
- 附图替换顺序：先 `Supplementary Fig. S` 再裸 `Fig. S`/`Figure S`，避免双重前缀；`Fig. S1` 不会误吞 `Fig. S10/S12/S13`（`\d+` 贪婪 + `\b`）。
- `results/figures_submission/Supplementary_Figure_S13.pdf` 为 notebook 80 真实产物文件路径，含下划线不匹配 `Figure S\d` 模式，原样保留（若后续投稿包重命名该 PDF，需同步改此路径——已告知 team-lead）。
- 正文 `NAR 2021` 为 Hounkpe et al. 文献引用（Nucleic Acids Research），属合法书目，保留；自检规则已加年份白名单。

## 自检结果（verify_nc_guide.py，VERIFY PASS）

- 残留检查：`Note 3./4./5.`、`SN 3./4./5.`、`Fig. S`、`Figure S`、`Table S`、`Additional file`、`Supplementary Note 3.11`、`(A)-(E)`、`Fig. \d[A-E]`、`Genome Biology`、`NAR-compliant` 全部 0 命中。
- `Supplementary Note N` 出现 1 次（替换前需重编号的 `Note X.X` 计数 = 1，一致）：Supplementary Note 13。
- `Section 3.11 of the Supplementary Information (Parameter Justification)` 出现 1 次（3.11 按方案 B 的定稿引用形式）。
- 附图引用集合：Supplementary Fig. 1 / 8 / 10 / 12。

## 已关闭事项

1. ~~旧 Note 3.11 新编号~~：team-lead 2026-09-17 定稿——3.11 属正文未引用小节，按 nc-sn 方案 B 不获 `Supplementary Note N` 编号，指南引用改为 `Section 3.11 of the Supplementary Information (Parameter Justification)`。已实施、重跑、自检通过。
