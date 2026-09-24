# nc53 确认轮终审汇总（2026-09-25）

范围：六审对 nc53 修复后稿面（4a7a34c）的确认轮复审 + 重新打分；随后 nc54 微修轮（59a50cb）关闭确认轮发现的全部必修项。六份个人报告：results/audit/nc53_confirm_review_r{1..6}.md。

## 一、评分表（10 分制）

| 审稿人 | 领域 | 上轮（nc52 终审） | 确认轮初评 | 修后终分 | 推荐 | 分项分 |
|---|---|---|---|---|---|---|
| R1-stats | 统计方法学 | 7.5 | 7.5（minor revision） | **8.0** | accept | soundness 8 / novelty 6 / significance 6.5 / presentation 8.5 |
| R2-sccomp | 单细胞计算 | 7.5 | **8.0** | **8.0** | accept（条件性；③④⑤ nc54 已关闭，①②协商沿留 proof） | 未给分项 |
| R3-cancer | 肿瘤基因组 | 7.2 | **8.0** | **8.0** | accept after minor revisions（m1/m2 nc54 已修） | 未给分项 |
| R4-brain | 脑图谱 | 7.0 | **7.5** | **7.5** | accept（proof 两处一词级文字） | 未给分项 |
| R5-editor | 编辑/写作 | 7.0 | **9.0** | **9.0** | accept（投稿就绪） | 期刊合规全绿 |
| R6-repro | 可复现性 | 7.5 | **8.0** | **8.0** | accept | soundness 8.5 / novelty 7 / significance 6 / presentation 8.5 |
| **均分** | | **7.28** | **8.00** | **8.08** | **6/6 accept** | |

注：R3 初快报 8.5，正式报告 8.0，以正式报告为准；R5 初快报 8.5，正式报告 9.0，以正式报告为准。无 reject、无 major、无新增分析要求。

## 二、确认轮发现与 nc54 修复（全部 ground truth 裁定）

| # | 指控 | 裁定 | 修复（59a50cb） |
|---|---|---|---|
| R1-N1 / R3-m1 | SI Note 8 肝句 "liver healthy is marginally above adjacent, one-sided P = 3.8e-5" P 值方向错配 | **坐实**：json 键 p_MWU_GG_lt_NN=3.814e-5 为 GG<NN 方向；独立复算 alt=less 3.814e-5、alt=greater≈1.0；中位数 1.03× 重合但 NN 右尾更重（mean 3.77e-3 vs 2.38e-3） | 改为 "in liver the two medians coincide (ratio 1.03) but the distributions differ, one-sided MWU P = 3.8 × 10⁻⁵, with a heavier adjacent upper tail"（R3 建议措辞，R1 签收） |
| R1-N2 | GTEx 段 P 值未按惯例标注独立性/descriptive | 成立 | 段末补 "Pair-level P values in this GTEx comparison treat pairs as independent and are descriptive only."（R1 建议指明家族，采纳） |
| R2-C2 | "tumor is 2.0–2.7-fold higher" 低估上限 | **坐实**：BRCA TT/NN=2.776 | MS+SI 同步改 "2.0–2.8-fold"（覆盖 TT/NN 2.08–2.78 与 TT/GG 2.01–2.66 两种读法） |
| R3-m2 | Fig 4a 图注 "while k_f does not" 字面为假 | **坐实**：k_f TT/NN 均值比 1.25–2.07，五癌种 CI 全排 1（nc52_tcga_pancancer_excc.csv）；作者本意 NN/TT 口径（k_f 无反转） | 改 "while the NN/TT ratio of k_f does not" |
| R2-m1 | Table 5 表注（docx+xlsx A1）引用被取代的 −1.3% [−4.8,+2.0] | **坐实**：权威 ex-CC 口径为 pooled −0.9% / median −0.8% [−4.3,+2.5]（SI Note 8 与 MS 49 行一致） | 表注改 −0.9% / −0.8% [−4.3%, +2.5%] |
| R2-m2 | MS 49 行 "ρ = 0.20–0.26 versus k_n" 未说明 ρ 指代 | 成立 | 改 "non-parenchymal fraction versus k_n, ρ = 0.20–0.26"（+2 词） |
| R2-C4 | "38% misreports" 未挂模拟标签 | 成立 | 补 "(simulation)"（+1 词） |
| R1-N3 | SI 5.3 样本数镜像句式 | **裁定无需改**：当前文本已同段说明 3,567 before / 3,535 after | 不动 |
| 词数对冲 | 上述 MS 净 +3 词 | — | "retained the TT" → "retained TT"（−1）；MAIN 终值 4,999/5,000 |

## 三、验证状态（59a50cb）

构建 221/221；ms_verify 127/127；si_verify 121/121；XV8 63/63（MAIN 4,999 含子标题 / 4,932 不含；摘要 200/200；Methods 2,918；图注 max 302）；pytest tests/ 29 passed；spot_check ALL PASS。远端 main=59a50cb（ls-remote 核对）。

## 四、沿留 proof 阶段清单（各审确认接受）

1. R2-B1：四处 GTEx 断言式措辞（摘要 "argue against"、Intro "confirm as tumor-specific"、Results "tumor-specific rather than"、Discussion "supporting … over"）+ Note 8 跨队列不确定度量化句（GA/GG 1.8–2.3×）；候选插入 "(tentative, GTEx cross-cohort discrepancy unresolved)"。
2. R2-B2：KIRC 句改写。
3. R4：摘要 "(k_n-dominated)"（注意：摘要实测 200/200 三方口径一致，插入前须先减 1–2 词）；Fig 14 图注 "validation value lies" → "sanity-check value lies"。
4. R3-m3：摘要 GTEx 句补 "in lung, liver, and breast" 限定（与 #3 摘要词额统筹）；m4：Discussion attenuation 措辞弱化（可选）。
5. R5：5 条文字级 minor（见其报告 B 节）。
6. R6：外观项（pyproject description 命名、CI ubuntu-only vs 跨平台声称、Guide 5.6f 的 6.67）；SI 5.12 指针 5.10c→5.13；Dockerfile L6/L7 build 命令 cki:0.5.0→0.5.1。

## 五、决策项（待用户定夺）

A. **发布链快照错位**：tag v0.5.1=7133b43、Release 资产 586271335 为 nc53 前稿面；HEAD=59a50cb 又进两档（nc53+nc54）。代码与全部数值结果零差异（断言豁免合规）。选项：① 维持现状；② 移 tag 至 59a50cb + 替换资产 + Zenodo 重归档；③ 切 v0.5.2（最干净，推荐在 proof 改动落定后执行）。
B. **摘要词额**：200/200 零余量，proof 两处插入（(k_n-dominated)、"in lung, liver, and breast"）需同步减重 2–4 词。
C. 是否启动 response-to-reviewers 文档（六审 accept 条件清单已齐）。
