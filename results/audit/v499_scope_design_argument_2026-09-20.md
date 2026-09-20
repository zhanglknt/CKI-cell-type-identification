# v49.9 审计报告 — Scope-of-index 设计论证（2026-09-20）

## 1. 动机（用户科学定位指令）

用户指令原文：「CKI不适合做细胞类型分类。不同细胞类型的CKI w区分度不大很正常，这恰恰说明CKI适合看相同细胞类型的变化。这不是诚实披露，这恰恰是帮助我们搞清楚了CKI的适应范围。不同细胞类型的HK基因集可能是不一样的」。

要点：跨细胞类型 ω 区分度低是**设计使然而非性能缺陷**（HK 基因集细胞类型特异 → k_n 锚点跨类型不可比），应作为正面界定 CKI 适应范围（同一细胞类型内的状态变化检测）的论证，反对「honest disclosure」框架。经方案比选（AskUserQuestion），用户选定「Scope 段加论证」：Discussion "Scope of the index" 段加 2-3 句设计论证，不带任何分类数字，与 v49.8 全切零冲突。

## 2. 编辑范围（2 文件，+5/−1）

`generate_manuscript_nc.py`（Discussion line 609，段题句 "Scope of the index, parameters, and test direction." 后插入 3 句）：

1. "CKI is designed to detect state changes within a given cell type, not to discriminate cell-type identity."
2. "Because the housekeeping anchor is cell-type-specific—housekeeping gene sets may differ across cell types—the k_n baseline is only directly comparable within the same cell type, so limited cross-type discrimination of ω is expected by design and delineates, rather than limits, the index's scope."
3. "The intended domain of CKI is thus the comparison of biologically matched populations—the same cell type across organs, brain regions, or perturbation states—as throughout the analyses reported here."

`99_build_nc_v49.py`：新增断言 V49-N38（论证三句关键片段在场）。

## 3. 构建与 verify

- 构建 exit=0，**133/133 全 PASS**（v49.8 132 + N38）
- ms_verify **116/116**、si_verify **109/109**、cl_guide_verify **39/39**，三套 0 failures（与 v49.8 持平）
- N38 PASS；N36 回归确认 '0.680' 不在 MS
- fresh docx 提取复核：3 句论证渲染正确（em-dash/ω/弯引号正常），位置=Scope 段题句之后

## 4. 包

- 主目录 `CKI_Submission_v49_NC.zip`：**12,258,746B**（v49.8 为 12,258,559B，+187B ≈ 新增句）
- sha256 **`43256f999d0007a4984f993d727daaa86b4dee67f0fa90f25a3ea705d79eed3e`**
- 27 条目不变；包内 CKI_Tables_NC.xlsx 单 sheet ['Table 1']、A1 题注正确
- v49.8 包备份：`_tmp_archive/CKI_Submission_v49_NC_v498_pre-v499.zip`

## 5. Git 与 CI

- commit **`fa775c3`**（全 SHA `fa775c3204d9ce2c271f35ba0c9df54cad4b9521`，2 文件 +5/−1）
- push `abfef12..fa775c3`，ls-remote 核对一致
- CI check-runs test（py3.10/3.11/3.12/3.13）**4/4 全绿**

## 6. Release（ID 387922141，tag v0.5.0）

- 删 v49.8 资产 575190894 → 传新资产 **575239545**（12,258,746B，state uploaded）
- 正文：头部 latest 改 v49.9；v49.9 块前置（动机+两句论证摘要+构建/CI 计数）；sha256 行更新；**v49.7 残留 "retained in Table 1 as honest disclosure" 顺手改写为范围界定框架**（"at that point retained in Table 1; cut entirely in v49.8 — cross-type discrimination lies outside the index's intended scope (v49.9)"）
- readback：下载 12,258,746B，**sha256 MATCH**，27 条目，xlsx 单 sheet 复核通过
- 补丁前后正文存档：`_tmp_fa_review/_rel_body_pre_v499.md` / `_rel_body_new.md`

## 7. 遗留观察项（不变）

- MS line ~750 "Supplementary Tables 1–4" 与 SI 实际 19 表不符（疑 v49.4 遗留，下轮修）

## 8. 判定

**CLOSED。** v49.9 单点论证落地，全链（编辑→断言→构建→verify→包→commit→push→CI→Release→readback）零失败；MS 与 Release 正文措辞已与用户「设计使然/适应范围」立场完全对齐，全文无 "honest disclosure" 残留。
