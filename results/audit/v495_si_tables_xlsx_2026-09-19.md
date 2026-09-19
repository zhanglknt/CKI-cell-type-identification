# v49.5 SI 附表迁出审计报告

- 日期：2026-09-19
- 实施：c-drift
- 触发（用户指令）：「附表也单独拉出来放excel，附表按照出现顺序编号」
- 方案：team-lead v49.5 最终计划——SI docx 内嵌 15 表全部迁移至 `results/CKI_Supplementary_Tables_NC.xlsx`，按出现顺序编号 Supplementary Table 5–19（大表 CSV 指针表保留 1–4 号，MS 引用不变）；纯迁移，表内任何数值/符号/上下标串零字节改动

## 结果总览

| 项 | 结果 |
|---|---|
| SI docx 表格数 | 0（迁出前 15） |
| 新 xlsx | `results/CKI_Supplementary_Tables_NC.xlsx`，15 sheets：Table 5 … Table 19 |
| 版式 | A1 粗体完整题注（"Supplementary Table N: <原题注全文>"），第 2 行空，第 3 行粗体表头，第 4 行起数据 |
| si_verify | 109/109 PASS |
| ms_verify | 105/105 PASS（lead refs 重排轮） |
| 全量构建 | **126/126 ALL PASS**（lead 以 CKI_BUILD_NO_ARCHIVE=1 零删除模式执行） |
| 提交包 | 28 条目（27→28，新增本 xlsx）；zip 12,502,657 B |

## 15 表映射（docx 索引 → 新编号）

维度为 xlsx 总 rows×cols（含 A1 题注行 + 空行 + 表头行）；数据行数 = rows − 3。行号为改造后 `notebooks/68_gen_supplementary_nc.py` 中 add_table 调用点。

| docx 索引 | 新编号 | sheet | 原节 | 标题 | 维度 | add_table 行号 |
|---|---|---|---|---|---|---|
| [0] | Supplementary Table 5 | Table 5 | 1.7 | Linear-normalization robustness of the TCGA main pipeline | 8×5（5 数据行） | L461 |
| [1] | Supplementary Table 6 | Table 6 | 3.11a | Per-cell-type effects on Kang IFN-β | 9×5（6） | L833 |
| [2] | Supplementary Table 7 | Table 7 | 3.11b | Target-detection AUC (mean-shift simulation) | 6×8（3） | L866 |
| [3] | Supplementary Table 8 | Table 8 | 3.11c | Donor-paired detection power | 9×5（6） | L896 |
| [4] | Supplementary Table 9 | Table 9 | 3.12a | Kang batch-1 technical-replicate calibration | 8×4（5） | L993 |
| [5] | Supplementary Table 10 | Table 10 | 3.12b | Brain drift ladder by tier and metric | 10×4（7） | L1067 |
| [6] | Supplementary Table 11 | Table 11 | 3.13a | Pan-cancer NN/TT ratios | 8×5（5） | L1177 |
| [7] | Supplementary Table 12 | Table 12 | 3.13b | LUAD driver-group means | 6×5（3） | L1225 |
| [8] | Supplementary Table 13 | Table 13 | 3.13c | LUAD pairwise contrasts | 6×4（3） | L1253 |
| [9] | Supplementary Table 14 | Table 14 | 3.13d | LIHC overall-survival Cox models | 9×5（6） | L1274 |
| [10] | Supplementary Table 15 | Table 15 | 3.13e | Purity sensitivity of the pan-cancer reversal | 8×5（5） | L1324 |
| [11] | Supplementary Table 16 | Table 16 | 3.13f | LUAD admixture-adjusted contrasts | 6×4（3） | L1348 |
| [12] | Supplementary Table 17 | Table 17 | 3.13g | LUAD smoking-covariate adjustment | 7×5（4） | L1378 |
| [13] | Supplementary Table 18 | Table 18 | Note 9 | TCGA clinical-severity gradients | 6×6（3） | L2083 |
| [14] | Supplementary Table 19 | Table 19 | Note 10 | Brain min-cells threshold sensitivity | 7×6（4） | L2139 |

## Prose 指针（每表 ≥1 处散文指向）

| 表 | 位置（68 脚本行号） | 形式 |
|---|---|---|
| 5 | L455 | "…mapping choice drives no conclusion (Supplementary Table 5)."（新插） |
| 6 | L831 | "(Supplementary Table 6)."（新插，3.11a 段末） |
| 7 | L864 | "…Notes 1 and 6; Supplementary Table 7)."（新插） |
| 8 | L894 | "…CKI's design target (Supplementary Table 8)."（新插） |
| 9 | L981 | "…values are given in Supplementary Table 9;…"（原有引用改写） |
| 10 | L1056 | "…given in Supplementary Table 10;…"（原有引用改写） |
| 11–17 组 | L1127 | "(Supplementary Tables 11–17)."（新插，3.13 Purpose） |
| 12、13 | L1194 | "…P = 7.8 × 10⁻⁷; Supplementary Tables 12 and 13)."（引用改写） |
| 14 | L1148 | "…sensitivity models (Supplementary Table 14)."（新插） |
| 15 | L1298 | "…in all five cancer types (Supplementary Table 15)…"（新插） |
| 16 | L1301 | "…components (Supplementary Table 16);…"（新插） |
| 17 | L1303 | "…divergence association (Supplementary Table 17)."（新插） |
| 15–17 组 | L1207 | "(Supplementary Tables 15–17)"（引用改写，跨行字面量正则） |
| 18 | L2074 | "…test details are given in Supplementary Table 18."（新插） |
| 19 | L2137 | "The min-cells threshold sweep is given in Supplementary Table 19."（新插） |

旧式 "Table (Section x)" 引用在 docx 全文零残留（si_verify 断言）。TOC 在 Supplementary Table 4 后插入 15 条（"Supplementary Table 5: TCGA Linear-Normalization Robustness" … "Supplementary Table 19: Brain min-cells Threshold Sensitivity"）。

## 68 脚本改造要点

1. `add_table(rows)` 改为采集器：追加 `[[str(v) for v in row] for row in rows]` 至 `_SI_TABLE_ROWS`，返回 None（docx 不再产出表格）。
2. 新增 `si_caption(text)`：剥离 `^Supplementary Table \d+\.\s*` 前缀后追加至 `_SI_TABLE_CAPS`；15 个题注由 `add_para(` 改为 `si_caption(`。
3. 15 个题注前缀全局改写："Table (Section 1.7). " → "Supplementary Table 5. " … "Table (Supplementary Note 10). " → "Supplementary Table 19. "（临时脚本 `_tmp_v495_replace.py`，含 3 处跨行字面量正则；lambda 替换规避 re 的 `\u` 转义限制）。
4. 8 处 prose 引用改新编号（同上脚本）；8 处新 prose 指针插入（1 处手工 Edit + `_tmp_v495_ptr.py` 7 处，写入前断言模式——匹配失败不落盘）。
5. `write_si_tables_xlsx()` 追加于 doc.save 之后：断言 15 行/15 题注，sheet 名 "Table 5".."Table 19"，A1 粗体 `f'Supplementary Table {_n}: {_cap}'`，空行，第 3 行粗体表头，数据行原样写出。

## 构建脚本（99_build_nc_v49.py）五处配套

1. 打包段：`CKI_Supplementary_Tables_NC.xlsx` 存在性检查 + 复制入 workdir（包条目 27→28）。
2. P2 清单新增 `"CKI_Submission_v49_NC/CKI_Supplementary_Tables_NC.xlsx"`。
3. N26：KIRC k_n~admix P（8.3 × 10⁻¹⁷）由 SI docx 改读 xlsx A1 题注（openpyxl）。
4. 新增 P6：SI docx 零表断言（P5 MS 零表不变）。
5. S7：SI docx "Supplementary Table \d+" 引用计数 14 → 41（逐一枚举核实：TOC 19 + 大表 1–4 散文引用 14 + 新表单数指针 8；复数/区间形式不计入该正则）。

## 验证链

| 层 | 结果 |
|---|---|
| SI 重跑内联检查 | docx tables=0；xlsx 15 sheets 名称序列正确；Table 5/11/14/18/19 A1 题注、表头、维度抽查通过 |
| `results/audit/_nc49_si_verify.py` | **109/109 PASS**——cellfull 改读 xlsx 全部单元格（第 3 行起），新增 capfull（15 个 A1）；MWU 注、Wilson/McNemar、1/31、class-composition、wild-type/pair-sharing、3.13e P 值、Cox 题注、χ²/百分比、admix 组均值、1.7 LIHC caveat（其文本本属 Table 5 题注）等题注断言全部指 capfull；表值断言指 cellfull；prose 断言不动；新增 docx 零表/15 sheets/A1 前缀/15 指针/旧引用零残留断言 |
| `results/audit/_nc49_ms_verify.py` | 105/105 PASS（MS 不受 v49.5 影响；lead refs 重排轮基线） |
| 全量构建 `99_build_nc_v49.py` | **126/126 ALL PASS**，含 P6 SI 零表、新 S8 节标题锚点、P2 双 xlsx |
| 提交包 | `version3/CKI_Submission_v49_NC.zip` 与主目录副本字节一致；12,502,657 B；28 条目 |

## 数值一致性

纯迁移：表内数值/符号/上下标串零改动。动态表（11、14、15、16、17 等）继续从 post-CC CSV 渲染，迁移前后取值不变（si_verify 的 cellfull 锚点逐项比对通过，如 Table 11 "1.88 [1.63, 2.16]"/"3.29 [2.54, 4.35]"、Table 14 "1.07 [0.88, 1.31]"、Table 18 "78.2 / 76.8 / 77.9 / 72.6"/"JT 6.9 × 10⁻¹⁵"）。

## 遗留事项

- 临时文件清理挂起（mv 在 c-drift 会话计入 safe-delete 删除配额，用户已取消该类确认；待用户授权后统一清）：`results/audit/_tmp_v495_replace.py`、`results/audit/_tmp_v495_ptr.py`、`results/audit/_dbg_si*.txt`、`results/audit/_dbg_dims*.txt`、根目录 `_tmp_v495_scan.py`、构建日志 `_build_v495*.log`。
- workdir `version3/CKI_Submission_v49_NC` 曾被守卫拦截留下半搬移状态；lead 以 NO_ARCHIVE 模式原地覆盖重建，包内容已核验字节一致，无影响。
- 未做 git 操作（lead 统一处理）。
