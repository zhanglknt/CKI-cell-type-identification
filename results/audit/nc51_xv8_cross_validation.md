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

## 8. 发布链（2026-09-24 执行完毕）

| 环节 | 结果 |
|---|---|
| commit | `89a157d`（40 文件：生成器/构建脚本/zip/审计脚本+报告）|
| push | `4f6fe68..89a157d main -> main`，`git ls-remote` 核对一致 |
| Release v0.5.0 资产 | 旧 583048429 已删；新 **584155033**（12,299,140 B）上传 |
| readback | sha256 `36b9d126e8e51eacbe51009e76e577a91702bdc365f1d03576d45df6a4f4c359` **MATCH** |
| CI @89a157d | 4/4 success（py 3.10 / 3.11 / 3.12 / 3.13）|

方法备注：gh CLI shim 本机损坏，Release 用 `results/audit/_v51_release_swap.py`（urllib + ~/.git-credentials PAT；DELETE 204 空体需容错），CI 用 api.github.com check-runs 直查。

## 9. v51r2 严格 NC 合规轮（2026-09-24，用户指令"严格按照 NC 要求"）

**唯一违例项修复**：MAIN 5,304 → **4,964**（含小标题；4,897 不含），NC ≤5,000 达标。

| 指标 | v51 | v51r2 |
|---|---|---|
| MAIN | 5,304（超建议 6%，曾接受）| **4,964** |
| ├ Introduction | 508 | 477 |
| ├ Results | 3,211 | 3,015 |
| └ Discussion | 1,585 | 1,472 |
| Methods | 2,802 | 2,802（不动）|

- **压缩**：`_v51r2_splice_b16.py` 53 处编辑（~340 词）；删除数字全部预探 SI 承载（6.4×10⁻¹³、0.025、9.03/10.53、7.39/8.00、2% overdispersion、group-size threshold sweep）；引用 73 组不变。
- **信息丢失修复**：k_n–admixture 相关性范围 r = −0.23 to −0.42 在 v51 压缩时丢失（MS/SI 均无），已从 v50 源码（232214e L542）逐字恢复进 SI Note 8 迁移注释（L2116 就地扩展，迁移标记仍为 6）。
- **verify 门硬化（重要）**：发现三个 verify 脚本恒退出 0，ms_verify 实际 39 项 FAIL、si_verify 1 项 FAIL 被掩盖（此前"原生通过"结论不成立）。`_v51r2_splice_b17_verify.py` 同步全部 40 项断言到 v51r2 措辞，并为三脚本加 `SystemExit(1 if nfail else 0)` 硬门。现 MS 117 / SI 109 / CL+Guide 39 全 0-fail 且真退出 0。
- **终验**：99_build **221/221 0-fail**（含硬化 verify 门）；XV8 **54/54 PASS**（MAIN 断言更新为 ≤5,000）。
- **包**：zip 28 项、12,298,400 B、sha256 `a5b8d07cfb52b2369735107a2e730c130a3ebdf05d6bef54d5fc02eb80ec1fb3`。
- **NC 合规终态**：标题 13 词 / 摘要 197 词无引用 / MAIN 4,964 / Methods 2,802 / 图注 max 302 / 图+表 7 / 文献 57 条 / 结构顺序正确 / Discussion 无子标题 / 声明区块齐备——**全部硬性指标零违例**。
- **发布链（v51r2）**：commit `426d0da`（19 文件）→ push（ls-remote 一致）；Release v0.5.0 资产旧 584155033 删、新 **584250331**（12,298,400 B）readback sha256 `a5b8d07c…ec1fb3` **MATCH**；CI @426d0da 4/4 success（py 3.10–3.13）。
