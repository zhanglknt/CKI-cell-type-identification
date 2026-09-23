# v51 (NC 格式压缩轮) 收尾审计 — XV8 交叉验证

日期：2026-09-23 ・ 范围：v51 全部改动（MAIN/Methods 压缩 + SI 迁移 + 构建断言同步）

## 1. NC 格式硬指标（XV8 实测，54/54 PASS）

| 指标 | NC 要求 | v51 实测 | 判定 |
|---|---|---|---|
| 标题 | ≤15 词 | 13 词 | PASS |
| 摘要 | ≤200 词、无引用 | 197 词、0 上标引用 | PASS |
| MAIN（Intro+Results+Discussion） | 建议 ≤5,000 | **5,304**（含小标题；5,237 不含）| PASS（用户已确认接受，超建议 6%）|
| ├ Introduction | — | 508 | — |
| ├ Results | — | 3,211 | — |
| └ Discussion | — | 1,585 | — |
| Methods | 通常 <3,000 | **2,802** | PASS |
| 每图注 | ≤350 词 | Fig 1–6: 220/239/302/212/108/194 | PASS（max Fig 3 = 302）|
| 图+表 | ≤10 | 6 图 + 1 表 | PASS |
| 参考文献 | 建议 ≤70 | 57 条 | PASS |
| 结构顺序 | Intro→Results→Discussion→Methods | Abstract(6)→Intro(8)→Results(14)→Discussion(67)→Methods(80)→Refs(125) | PASS |
| Discussion 子标题 | 不允许 | 0 个 Heading 样式段落 | PASS |
| 引用组 | 全程无损 | **73 组**，首现 1..57 单调、无孤儿 | PASS |
| 声明区块 | 投稿前必需 | Acknowledgements / Author contributions / Competing interests / Data availability / Code availability 齐备 | PASS |

## 2. 压缩总账（v50 → v51）

- MAIN：7,991 → **5,304**（−34%）。Intro 716→508；Results 4,434→3,211；Discussion 2,841→1,585。
- Methods：5,964 → **2,802**（−53%）；23 段程序性原文**逐字**迁入 SI 新节 "Supplementary Methods"（5.1–5.14），MS 侧留公式/核心参数 + 19 处 "(Supplementary Methods 5.x)" 指针。
- SI：→ 23,069 词（271 段）；6 处迁移数字注释插入 Note 1/6/7/8/9/12（带 "migrated from the main text in v51" 标记）。
- 引用 73 组全程无损（两次 73→72 事故均定位补回：L608 [14]、L676 [13]）。

## 3. 构建断言同步（批次 15）

99_build_nc_v49.py 中 38 项 v50 措辞断言失败 → 39 处编辑全部同步，重跑 **221/221，0 FAIL**（`_v51_build_log2.txt`，EXIT=0）。同步分类：

- **翻转到 SI（ms→sn）**：N1（0.963）、N6（90.9）、N25（2.86）、N31（P=0.48）、N50（CC provenance）、N51（percentile 区间）、N56（seed 20260905）、N81（3,593 等样本数）、N82 第二段（+13.3, P=1.4×10⁻³）、N87（per-cancer attenuation，删 ms 子句）、N88（Spearman ρ=0.78）、N100（k_f 1.39/k_n 0.33）、N104（6.46→10.94）
- **改期望串为 v51 措辞**：A13（absorbs ratio bias）、N15、N27、N37、N38、N40、N47、N49、N57、N58、N58b、N60、N62、N67、N68、N69、N70、N78、N82 首段、N86、N101、N102、N53
- **计数更新**：S6（SI Supplementary Fig. refs 9→10）、N9/N17（Section 3.12 短指针 ×3）
- verify 三套件（MS/SI/CL+Guide self-check）无需改动：结构性断言在 v51 下原生通过。

## 4. SI 迁移抽查（XV8 第 8 节，21 项全 PASS）

0.963 / 90.9 / 2.86 / CC provenance (positions 14–15) / percentile bootstrap / seed 20260905 / 3,593 barcodes / +13.3 P=1.4×10⁻³ / ρ=0.78 / 6.46→10.94 / k_f 1.39+k_n 0.33 / NN/TT 1.11 [0.93, 1.30] / ρ=0.364 / |Δz| 1.305 / 0.247+0.250 / 0.0130+0.0148 / 0.86–0.88 / 75.18+16.73 / 1.1–2.0-fold / 0.98–1.00+0.04–0.20 / P=0.48。

## 5. 独立重算（XV8 第 9 节）

microglia headline 从 CSV 重算：ω 21.83±7.20 vs 1.30±0.36，MWU P=5.49e-14 — 与正文一致。

## 6. 包完整性

- zip：28 项、12,299,140 B（<15 MB）、含 Supplementary_Fig_14.pdf。
- sha256 = `36b9d126e8e51eacbe51009e76e577a91702bdc365f1d03576d45df6a4f4c359`
- L733 SI 清单修正已固化：Supplementary Notes 1–16、Supplementary Figs. 1–14。

## 7. 遗留事项

- MAIN 5,304 超 NC 建议上限（5,000）约 6%——用户已确认接受，投稿时如编辑要求可再做一轮 SI 迁移。
- 发布链（Release 资产替换 / push / CI）待用户确认后执行（任务 #9）。
