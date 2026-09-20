# v49.12 — v49.10 盲审遗留全清（N1–N5 + C2–C7）+ XV3 补丁

**日期**：2026-09-20 ｜ **轮次**：v49.12（commit d6540e5）+ XV3 补丁（本轮）
**输入**：v49.10 盲审汇总 results/audit/v4910_review_panel_summary_2026-09-20.md（N1–N6 / C1–C7）
**验证**：构建 165/165 全 PASS；ms_verify 117 + si_verify 109 + cl_guide_verify 39 全 0-fail；XV3 交叉验证 11 PASS + 1 FAIL → 补丁后 14/14 渲染复核全 PASS

---

## 一、v49.12 主体修复（12 项，commit d6540e5）

| 编号 | 问题 | 修复 |
|---|---|---|
| N1 | seed 20260905 未申报 | MS Methods 声明 "(notebooks/89_cluster_boot_v45.py), which used seed 20260905"；Guide seed checklist 补 "notebook 89 uses seed 20260905" |
| N2 | Discussion 引 superseded softmax −0.5% | Discussion 改引 linear −1.2%（后由 XV3 补丁进一步精确化，见下） |
| N3 | 阈值扫描 4 阈值只给 3 梯度值 | 补全 "endpoint gradients of 6.60, 6.10, and 4.12 at thresholds 10, 20, and 50 (at 100 nuclei the eight retained classes exclude Bergmann glia, so the endpoint gradient is undefined)"——ground truth: results/brain_v44_threshold_sensitivity.csv 显示 100 核下 Bergmann glia 被滤除，端点梯度**未定义**而非缺值 |
| N5 | Guide 依赖缺 4 包 | 环境清单补 seaborn 0.13.2 / statsmodels 0.14.6 / meld 1.0.2 / pyaugur 0.1.0（importlib.metadata 实测） |
| C2 | ω 相对 k_f 增量未证实 | 增量句：AUC 0.80 vs 0.72（marrow）、0.91 vs 0.86（skin replication）、drift rejection 有增量；real-data orderings 未证实，k_f+design-matched null 为默认 |
| C3 | Table 1 跨类型矛盾 | xlsx Table 1 A1 题注加 "cross-type gaps in mean ω are descriptive rather than calibrated" |
| C4 | CC 敏感性分析缺失 | **新计算** `_tmp_fa_review/_v4912_cc_sensitivity.py`：剔 32 CC（TSS 码 s[5:7]=="CC"）后 LIHC NN/TT 1.11 [0.93, 1.30]、TT/NN k_n 1.34 [1.00, 1.88]（cluster bootstrap B=1000 镜像 nc49_tcga_main.py）→ 零结果非 CC 修正伪影；"Three controls"→"Four controls" + 第四控制句 |
| C5 | Results/Discussion 仍 6.10 领衔 | 两处首句改为 1.74-fold size-balanced 领衔、6.10 作 uncorrected full-data 共报 |
| C6 | studentized 描述不足 | 补 influence-function (multiplier) sandwich SE + log-scale delta method studentization（B=5,000, seed 20260905, coverage 0.953/0.951） |
| C7 | Pearson −0.850 被 MS 隐去 | 补 "Pearson r = −0.850, P = 0.0018" |

构建断言 +N56–N64（162/162）。

## 二、XV3 交叉验证（11 PASS + 1 FAIL）

XV3 agent 对 v49.12 四件套做独立核验：11 PASS，1 FAIL——

**FAIL（N2 残留）**：MS 已洁净（linear −1.2%），但 SI Note 8 主段仍保留 softmax "−0.5% pooled (95% CI [−3.2%, +2.6%]; median −0.4%)"，且 MS Results/Discussion 均引 Supplementary Note 8 支持新数字 → 引用/数字不匹配。
**次要**：Guide §1.4 仍写 "three fixed exceptions"（实为四个，漏 notebook 89）。

## 三、XV3 补丁（本轮，5 文件）

ground truth 复核 results/tcga_composition_v44.txt：linear 口径 **pooled 点估计 −0.8%**（effect −0.008436）、**cluster-bootstrap median −1.2%** CI [−4.1%, +2.6%]、per-cancer median −1.6/−11.1/+37.1/+18.3/−16.2；Spearman ρ=0.355 pooled（0.146–0.492 per cancer）；|Δz| overall3 1.303-fold（P=7.87e-140）、overall4 1.227-fold（P=2.66e-74）。

| 文件 | 修改 |
|---|---|
| generate_manuscript_nc.py（Discussion） | 混口径数字全切 linear：\|Δz\| 1.30-fold three-panel composite / 1.23-fold four-panel（P = 8×10⁻¹⁴⁰ 与 3×10⁻⁷⁴）；Spearman ρ = 0.355 pooled; 0.15–0.49；attenuates by **−0.8% pooled (cluster-bootstrap median −1.2%, 95% CI [−4.1%, +2.6%])**；softmax 归档指针改 "Section 1.7 **and Note 8**"（softmax 组成检验数字存于 Note 8 非 1.7） |
| generate_manuscript_nc.py（Results 第一控制） | "(−0.8% pooled; cluster-bootstrap median −1.2%, 95% CI −4.1% to +2.6%; per cancer type −16% to +37%)"——点估计与 bootstrap median 分列，不再以 median 冒充 pooled |
| notebooks/68_gen_supplementary_nc.py（Note 8） | softmax 回归句加标签 "(softmax caliber; superseded by the linear-normalization update at the end of this note, the authoritative caliber for the regression and correlation estimates cited in the manuscript)"；更新段标题改 "Linear-normalization update (authoritative caliber)"、结尾加 "These linear-normalization estimates are the ones cited in the manuscript"——softmax 数字保留作归档记录 |
| notebooks/100_gen_reproducibility_nc.js（§1.4） | "three fixed exceptions"→"four fixed exceptions"，补 notebooks/89_cluster_boot_v45.py（small-cluster studentized bootstrap-t）seed 20260905 |
| 99_build_nc_v49.py | N58 改查 −0.8%/−1.2% 双数字 + 0.355 + 无 0.387；新增 N58b（Results 口径）/ N65（SI softmax 标签）/ N66（Guide 四例外） |

**核查**：残留 "0.387 pooled"/"1.33–1.46"/"three fixed exceptions" 仅存在于冻结的 GB 时期脚本（99_build_gb_v41–v47、CKI_Reproducibility_Package 快照），历史存档不动。

## 四、结果

- 构建 **165/165** 全 PASS（含新 N58b/N65/N66）
- ms_verify 117 + si_verify 109 + cl_guide_verify 39 全 0-fail
- 14/14 渲染复核全 PASS（docx 提取文本逐项确认）
- zip **12,260,471 B，27 条目，sha256 4c96ac95e7c36a24fed4c862bc000cbbe636cd5c9cc02d05d1ccc45b47166421**；主目录 = version3 字节一致
- CL 未涉及组成检验数字（grep 确认），零改动

## 五、教训

1. **口径切换要切全**：v49.12 只把 N2 的 headline 数字（−0.5%→−1.2%）切到 linear，但同句的 ρ=0.387、|Δz| 1.33–1.46/1.24 仍是 softmax——同一句话内混两种口径。修复时应整段按 ground truth 输出文件重写，而非只替换被点名的数字。
2. **点估计 vs bootstrap 摘要量要分列**：tcga_composition_v44.txt 中 pooled 点估计 −0.8% 与 bootstrap median −1.2% 是两个统计量；MS 原以 median 冒充 pooled。引用回归类结果前先读输出文件确认 estimator 身份。
