# NC Cover Letter 生成报告（2026-09-17）

## 产出
- 生成器：`generate_cover_letter_nc.py`（新文件，未改动 `generate_cover_letter_nar.py`）
- 输出：`results/CKI_NC_Cover_Letter.docx`
- 自检脚本：`_tmp_fa_review/check_nc_cl.py`（python-docx 提取校验）

## 改写要点落实
1. 期刊名：Genome Biology → Nature Communications（全文 3 处：投稿请求句、"Nature Communications' tradition" 类比、未另投声明）
2. 文章类型：Methodology article → Article；新增方法学表述 "a novel computational method for quantifying functional divergence in single-cell genomics"
3. 新标题：「CKI is a Ka/Ks-inspired index quantifying functional divergence in single-cell genomics」（无冒号）
4. 声明块：未另投他刊声明改指 Nature Communications；作者/单位/通讯沿用 GB 版（Li Zhang 通讯、Xianming Wu 一作、CIBR Beijing、NSFC 32370682、AI 使用声明）
5. 建议审稿人 6 位保留（Theis / Welch / Linnarsson / Ståhl / Schäffer / Zemin Zhang）
6. 版式：Arial 11pt、1" 边距、单倍行距
7. 可复现性引用：v0.5.0、GitHub 链接、Zenodo DOI 10.5281/zenodo.22735744

## 自检结果（全部 PASS）
| 检查项 | 结果 |
|---|---|
| 'Nature Communications' ≥2 处 | PASS（3 处） |
| 'Genome Biology' 0 处 | PASS（0 处） |
| 新标题出现 | PASS |
| 无冒号标题 | PASS |
| 首句 "Dear Editors," | PASS |
| 词数 ≤550 | PASS（510 词） |
| DOI / v0.5.0 / GitHub URL | PASS |
| "as an Article in Nature Communications" | PASS |
| 方法学贡献表述 | PASS |
| 6 位建议审稿人 | PASS |

## 注意事项
- **DOI 变更**：GB 源文件写的是 Zenodo concept DOI 10.5281/zenodo.20405458；按任务指示改用 10.5281/zenodo.22735744（v0.5.0）。若该 DOI 尚未实际注册/解析，投稿前需核实。
- 词数 510，为后续微调留有 40 词余量。
- 未做 git commit；未触碰 version3/ 与 zip；未批量删除文件。
