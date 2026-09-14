# v47.1 图表编号顺序审计与重编号（2026-09-14）

## GB 惯例基准
Genome Biology 要求图表按正文首次引用顺序编码（Springer 官方投稿指南 + 已发表论文实参核验）。
主图 Figure 1-6、附图 Additional file 1: Figure S1-S13、主表 Table 1-2、附表 Table S1-S4、Additional file 1-2。

## 审计发现（修复前）
| 维度 | 首引顺序 | 判定 |
|---|---|---|
| 主图 | 1,2,3,4,5,6 | ✓ 合规 |
| **附图** | **1,2,S12,S3,S4,S5,S6,S7,S8,S13,S9,S10,S11** | **✗ 不合规** |
| 主表 | 1,2 | ✓ 合规 |
| 附表 | S1,S2,S3,S4 | ✓ 合规 |
| Additional file | 1,2 | ✓ 合规 |

根因：v47 Q5 重编号轮删除旧 S3（method-comparison）后，Kang（S12）与 QQ（S13）保持了旧高位编号，
但正文叙述中 Kang 首引（Results perturbation 段，pos 24273）早于 TCGA（pos 28161），QQ 首引（pos 47315）早于 Discussion 的 S9（pos 63856）。

## 重编号映射（按首引顺序）
- S1（parameter sweep）→ S1 不变；S2（calibrated ω）→ S2 不变
- **S12（Kang IFN-β）→ S3**；S3→S4，S4→S5，S5→S6，S6→S7，S7→S8，S8→S9
- **S13（permutation QQ）→ S10**；S9→S11，S10→S12，S11→S13

## PDF 内注核查
13 个附图 PDF 逐个文本提取：仅 S1 PDF 内注含 "Figure S1"（编号不变 ✓）；
S2-S13 PDF 内部无编号字样 → 重编号不破坏 PDF 内部一致性。源 PDF 文件名（figure_S1..S13.pdf）不变，
构建 FIGURE_MAP 目标键重映射（V47-2 断言同步改为 MAP 驱动字节比对）。

## 修改文件（4 + 镜像）
1. `generate_manuscript_gb.py`：正文引用置换（~17 处）+ Supplementary figure legends 13 段重排（物理顺序按新编号 1-13）
2. `notebooks/68_gen_supplementary_en.py`：SN Notes 交叉引用 7 处（S10→S12、S8→S9、S11→S13、S6→S7、S12→S3、S13→S10；S2 不变；scheme 标签 S0/S1-S3 非附图语义不动）
3. `notebooks/100_gen_reproducibility_docx.js`：Guide 4 处（S7→S8、S10→S12×2、S13→S10）
4. `99_build_gb_v47.py`：FIGURE_MAP 重映射 + 断言更新（V41-21/22/25/29/30、V47-3d/e/f、E4-M1、R2-4、E4-9、M3）+ V47-2 改 MAP 驱动 + docstring v47.1 说明
- 全部同步 CKI_Reproducibility_Package/ 镜像

## 交叉验证结果（修复后，audit_figure_order.py 复核）
- 主图首引顺序 [1,2,3,4,5,6] ✓
- **附图首引顺序 [1,2,3,4,5,6,7,8,9,10,11,12,13] ✓（递增无跳号）**
- 主表 [1,2] ✓；附表 [S1-S4] ✓；Additional file [1,2] ✓
- SN Notes 引用图集合 {S2,S3,S7,S9,S10,S12,S13} 与 E4-9 断言一致 ✓
- 构建 **665/665 checks ALL PASSED**；图例段物理顺序 = 新编号 1-13 ✓
- 附图 PDF 内注仅 S1 带编号且不变 ✓

## 产物
- 终包 `CKI_Submission_v47.zip` = **65,374,406 B，34 条目**（内嵌复现包 296 文件，sha 3215946f）
- Release v0.5.0 资产替换 + readback 校验（见资产 id 与 sha256 于 commit 信息）
- 附表/主表/Additional file 编号本就合规，未改动
