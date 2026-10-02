# nc59 — 编号顺序 + S 前缀命名 + CL 论调一致性 确认方案（2026-10-02）

用户指令："所有图，表，附图，附表按照出现顺序编号。附图附表在数字前面加上S，其他命名方式一样。coverletter和附件材料跟正文论调保持一致。先不要动，都确定后再实际改动"

本文件只做盘点与方案，**未做任何改动**。

## 1. 出现顺序盘点（基于 v0.5.5 投稿包实测）

| 序列 | 首引顺序（MS 正文，图注节前） | 状态 |
|---|---|---|
| 主图 Fig. 1–6 | [1,2,3,4,5,6] | ✅ 已单调，无需动 |
| 主表 Table 1 | 仅 1 张 | ✅ 无需动 |
| 附图 Supplementary Fig. 1–14 | [1,2,…,14]（nc58 已重排） | ✅ 已单调，仅加 S |
| 附表 Supplementary Table 1–19 | **[1,5,14,2,3,4]**（MS 仅引 6 张；6–13、15–19 仅 SI 引用） | ❌ 需重排 |
| Supplementary Notes 1–16 | [1,2,9,16,6,7,…] 不单调 | ⚠️ 决策点（Notes 是 SI 章节号，惯例不按首引重排，建议不动） |

### 附表重排映射（MS 首引序优先，SI-only 表按 SI 现序递补）

| 旧号 | 新号 | 内容 | MS 首引位置 |
|---|---|---|---|
| 1 | S1 | Tabula Muris parameter sweep | ①（fixed-panel 段） |
| 5 | S2 | two-caliber NN/TT 反转表 (ex-CC) | ②（TCGA 段） |
| 14 | S3 | LIHC OS Cox 模型 | ③（TCGA 段） |
| 2 | S4 | 59 cross-organ pairs 全表 | ④（cross-organ 段） |
| 3 | S5 | 脑区 per-cell-type 汇总 | ⑤（脑段） |
| 4 | S6 | 脑候选 threshold-passing | ⑥（脑段） |
| 6–13 | S7–S14 | Kang 效应/AUC/power/batch1、脑 ladder、泛癌 ratio、LUAD 组均值/Dunn | 仅 SI |
| 15–19 | S15–S19 | purity 敏感性、LUAD admixture/smoking、severity 梯度、脑阈值敏感性 | 仅 SI |

影响面：MS 8 处引用、SI 44 处引用、xlsx 19 个 sheet 名+各表 A1 标题、Guide 1 处、
SI 内部表题、MS 尾句 "Supplementary Tables 1–19"→"S1–S19"、断言若干。
两遍占位符替换法防链式覆盖（同 nc58 附图重排，已验证可靠）。

## 2. S 前缀命名方案（按指令字面执行）

- 引用：`Supplementary Fig. 3` → `Supplementary Fig. S3`；`Supplementary Table 5` → `Supplementary Table S5`
- 面板引用：`Supplementary Fig. S5b`；范围：`Supplementary Figs. S1–S14`、`Supplementary Tables S1–S19`
- 图注节标题：`Supplementary Fig. S3. Human-brain sanity check…`
- xlsx sheet 名：`Table 1`→`Table S1`（主表 xlsx 保持 `Table 1`）
- PDF 文件名：`Supplementary_Fig_3.pdf`→`Supplementary_Fig_S3.pdf`（zip 内+MANIFEST 同步）
- 主图/主表命名完全不动（Fig. 1–6、Table 1）
- **风格提醒**：NC 现刊惯例是 "Supplementary Fig. 1"（无 S）；加 S 后偏离 NC house style
  （S 前缀为 Cell Press/Science 系风格）。指令已明确，默认照做；若编辑提出格式意见再回退成本低（机械替换可逆）。

涉及量：MS 29 处附图+8 处附表引用；SI 10+44；Guide 7+1；图注节 14 条标题；14 个 PDF 文件名。

## 3. Cover letter 论调比对（vs v5 新正文）

| 项 | CL 现状 | 新正文 | 判定 |
|---|---|---|---|
| six metrics / AUC 0.80 | "the other five"、"first of six metrics" | "among six metrics (AUC = 0.80)" | ✅ 一致 |
| drift 数字（0.00 vs 0.55–0.58；28.6% vs 35.7–45.2%；ladder 1.04→1.76→1.80） | 保留 | MS/SI 同值在 | ✅ 一致 |
| TCGA 区间数字 "NN/TT 1.11–2.46"、"1.3–3.3-fold" | 保留 | **新摘要已删这两组数**（Results 仍有 per-cancer 值支撑） | ⚠️ 决策点：保留（有 Results 支撑）或改写对齐新摘要措辞 |
| KRAS/EGFR 表述 | "dissolved under purity adjustment" | "abolished the apparent EGFR elevation" | ✅ 义同 |
| 脑图支柱 | **CL 无脑图内容**（仅 drift pairs） | 新摘要第四支柱："regional differentiation gradient + statistically calibrated framework" | ⚠️ 建议补一句脑图（保持三/四支柱与摘要呼应） |

## 4. 附件材料论调

- SI：已随 nc58 同步（重编号、Note 16↔SF3 图注、severity 5b 指针）✅；S 前缀方案通过后全量机械替换
- Guide：已同步（SF3 microglia 三面板描述、cross-species SF12）✅；同上
- xlsx：sheet 名/表题随 S 前缀与重排一次性处理

## 5. 执行顺序（确认后）

1. 附表重排（生成器两遍占位符法 + xlsx sheet 改名 + 断言同步）
2. S 前缀全量替换（MS/SI/Guide/图注/文件名/MANIFEST/断言）
3. CL 修 2 处（脑图支柱句 + TCGA 数字措辞裁定项）
4. 重建 → 218 断言 + XV8 + pytest 全绿 → zip 入主目录 → commit/push
5. 与 v0.5.5 phase-2（Zenodo DOI 回写，后台轮询中）合并为一次重建，避免双跑
