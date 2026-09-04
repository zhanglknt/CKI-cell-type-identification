# CKI v41 投稿包专家团盲审汇总报告（第一轮）

日期：2026-09-03　|　对象：version3/CKI_Submission_v41（344/344 断言版）　|　目标期刊：Genome Biology（Methodology）

## 一、评分与判定

| 专家 | 角色 | 评分 | 判定 | Major | Minor |
|---|---|---|---|---|---|
| E1-methods | 方法学/统计 | 7.0 | Major Revision（轻度） | 4 | 7 |
| E2-domain | 领域科学 | 5.5 | Major Revision | 6 | 8 |
| E3-consistency | 数据一致性 | 8.5 | Minor Revision | 1 | 7 |
| E4-repro | 可复现性 | 8.5 | Minor Revision | 3 | 9 |
| **加权（等权）** | | **7.4** | **Major Revision（轻度，7–8 交界）** | | |

口径说明：GB 惯例 8+ 接近接收、7–8 Minor、6–7 Major。E1 明示"M1–M4 落实后可转 Minor"；E2 为唯一低分离群（5.5），其 M2/M3 属概念定位层，措辞与范围限定可部分化解。

## 二、跨专家去重后的问题清单

### P0 投稿前必须修复（文档级冲突/机械修复）

| # | 问题 | 来源 | 依据 |
|---|---|---|---|
| P0-1 | **复现指南未随 v41 更新**：Guide 5.3(e) 仍为旧三面板口径（"6% pooled、ρ 0.21–0.46"）与正文四面板（−0.5% [−3.2,+2.6]、ρ 0.387）直接冲突；notebooks 74/77/78/79/80 与 tcga_composition_v2.*、pseudoregion_control_*、kang_ifnb_demo_*、axis_permutation_test.* 输出在 Guide 零记载；GSE96583 下载入口缺失 | E3-M1 + E4-M1 | 两位专家独立发现同一缺口，最高共识 |
| P0-2 | **NN/TT 比率统计量冲突**：Guide 4.3 写 mean(ω_NN)/mean(ω_TT)，正文与 Fig 4A 图注均为 median | E3-m5 | Guide 4.3 |
| P0-3 | **TCGA 基因过滤阈值三处不一**：Guide §4.3 ">1 TPM"、SN 5.2 "≥0.5 TPM"、正文 Methods 无阈值 | E4-M2 | 需统一并写入 Methods |
| P0-4 | **作者单位编号互换**：Guide 标题块使第一作者 Xianming Wu 隶属血输所（¹），正文/CL 均为 CIBR | E3-m4 | Guide 标题块 |
| P0-5 | **Bergmann glia 同稿双 CI**：13.56 [8.49,19.52] vs [9.09,19.35] 均称 region-clustered，来源未说明 | E3-m3 | 正文 29/59 行 |
| P0-6 | **superseded 输出文件随 v0.4.4 tag 发布**：brain_siletti_*_v3.csv 等数值与正文矛盾（103.08 vs 82.75），靠文字告诫"勿用"是复现陷阱 | E4-M3 + E1-m4 + E2-m8 | 三位专家共识，需移入 superseded/ 目录或移除 |
| P0-7 | **参考文献未按首现排序**：[50]–[55] 首现位置早于 [30]–[49]；[55] Kang 首现于 Results 却编最末 | E3-m1 | 需制作阶段重排 |
| P0-8 | **格式小项**：Supplementary Note 5 旧式引用（唯一一处，应改 Additional file 1: Note 5.2）；888,263 与过滤后 886,808 计数表述位置误导；舍入不一致（0.459→0.45、0.0035→0.003、1.005e-5→1.0e-5、摘要 0.55–0.58 顺序歧义） | E3-m2/m6/m7 | 机械修复 |
| P0-9 | Guide 参数表断裂（"All parameters…:" 后为空、表排至文末）、5.6(e) 层级混乱、02b/02c 脚本编号不一、spot_check.py 与 tests 未入核对清单 | E4-m1/m2/m3/m4 | 机械修复 |

### P1 高共识 Major（需实质分析/统计工作）

| # | 问题 | 来源 | 修复方向 |
|---|---|---|---|
| P1-1 | **Kang 演示 lane–condition 完全混淆未贯彻到结论**：正文 "detected at ω level in all six cell types" 等检出/归因句式应全部降级为"架构演示"层（各指标同受 lane 影响的相对比较）；ACTB/GAPDH ↓40% 的 anchor-visibility 归因可由 lane 解释；37 个 donor 级检验无多重性校正 | E1-M1 + E2-m5 | 结论措辞重写（不改数据） |
| P1-2 | **per-class 校准不确定性未传播**：29 个 split-half population 分摊 10 类，每类基线点估计抽样误差大，梯度 CI [4.86,7.42] 疑反保守；需报告每类基线 n 与 CI + 联合 bootstrap（同采 split-half population 与 region 对）重算 | E1-M2 | 需重跑统计（n=6 split-half 数据已有） |
| P1-3 | **自立判读标准未回溯**：论文自己结论"排序类问题诚实默认 k_f"，但 cross-organ 排序（Fig 5/Table 2）与 TCGA severity 梯度仍以 ω 排序呈现、无 k_f-only 对照或分解 | E1-M3 + E2-M1/m7 | 补 k_f-only 敏感性或降级为描述性 |
| P1-4 | **丘脑-颞叶轴 null 低于同文其他分析规格**：现有 10 对重抽未对 Strong 规则建模（低 ω 选择规则幸存者的区域组成非均匀）；microglia 组成分析已用 selection-rule-matched null，axis 检验应同规格或压缩为纯描述 | E1-M4 + E2-M5 | 补 design-matched null 或降级 |
| P1-5 | **锚定失效 scope 限制应前置集中**：HK 锚在疾病/强扰动场景失效的披露分散于 Results/Limitations/Note 3.12，应集中前置陈述 | E2-M4 | 措辞重组 |

### P2 概念定位层（一轮内部分化解）

| # | 问题 | 来源 | 处理方向 |
|---|---|---|---|
| P2-1 | ω 相对组件 k_f 的不可替代利基收窄：真实数据所有组件分解显示 ω 由分母主导，论文最终推荐默认做法即标准分析 | E2-M1 | 措辞定位 + P1-3 落实后如实呈现 |
| P2-2 | 与标准 pseudobulk DE 流程无定量基准；SAMap/SATURN 以"问题不同"跳过 | E2-M2 | 至少补一个 ω 优于标准 DE 的真实场景或强化范围限定 |
| P2-3 | 全部应用零 FDR 阳性发现（min q=0.520），方法学论文适用面经自身验证后收窄 | E2-M3 | "informative bound" 定位已诚实，可再强化 |
| P2-4 | TCGA cluster bootstrap B=200 偏小（建议 ≥2,000）；显著类 B=10,000 补跑非删失 P；摘要掩盖 per-cancer 异质性 | E1-m1/m3 + E4-m1 | 算力可行，建议补跑 |

## 三、专家共识的优点（四位均认可）

1. 统计自审计深度远超同类投稿：分母伪相关分解、leave-pair-out 消融、对抗性仿真 S1/S2、伪区域阴性对照、selection-rule FDR（null 148.3 vs 观测 39 的反富集如实报告）
2. 数字一致性罕见地好：E3 抽查 24 组（含组合数学复算 31,764 配对、TCGA 分层加总）全部通过，唯一冲突是 Guide 落后（文档维护滞后，非数据错误）
3. 真实扰动演示（Kang）实证锚可见性边界并给出可操作决策规则；"When to use CKI" 指引可执行
4. 复现基础设施完整：环境固定、45 断言 spot-check、7 回归测试、Docker、GitHub+Zenodo 双归档、双许可

## 四、总判定与建议路径

**7.4/10，Major Revision（轻度）**。核心矛盾：E2 从领域增量角度给 5.5（概念定位收窄），E1/E3/E4 从统计/一致性/复现角度给 7–8.5（技术执行扎实）。差异本质是"方法诚实性导致的适用面收窄"是否可接受——这通过 P1-3（k_f-only 对照回溯）与 P2 的范围限定措辞可大部分化解。

建议修复顺序：P0 全部（机械，半天）→ P1-1/P1-5（措辞，1 天）→ P1-2/P1-4（统计补跑，1–2 天）→ P1-3（k_f-only 对照，1 天）→ P2 视剩余周期取舍。完成后可清 P1-2/P1-4 部分数字入 build 断言，重建 v42。

## 附：各专家原始报告索引

- E1 方法学：7.0，M1 Kang 混淆 / M2 校准不确定性 / M3 k_f 标准未回溯 / M4 axis null 规格
- E2 领域：5.5，M1 ω 概念定位 / M2 无定量基准 / M3 零 FDR 阳性 / M4 锚定失效 scope / M5 axis 过度解读 / M6 脑结构限制
- E3 一致性：8.5，M1 Guide 未同步；m1–m7 编号/单位/统计量/舍入
- E4 可复现：8.5，M1 Guide 盲区 / M2 阈值口径 / M3 superseded 文件；m1–m9 结构/合规
