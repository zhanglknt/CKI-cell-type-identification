# v47.2 参考文献编号按首引顺序重排 — 审计与交叉验证报告

**日期**: 2026-09-14
**范围**: CKI_Manuscript.docx（v47 → v47.2）；56 条参考文献
**指令**: 参考文献编号按照出现的顺序

---

## 1. 审计方法

- 严格模式正则 `\[(\d+(?:\s*[,\u2013\-]\s*\d+)*)\]`（只匹配纯数字/逗号/短横线组）提取正文全部引用组（74 处），展开区间与列表后取每个编号的首次出现位置
- 与构建脚本 `_parse_citation_brackets` 口径独立；两侧均以 fresh DOCX 提取的 fulltext 为对象
- 附注（Supplementary Notes）扫描：无方括号数字引用，不受影响

## 2. 发现（v47/v47.1 基线）

首引序列为 `[1..37, 56, 38..43, (0), 44..53, (74), 54, 55]`，唯一真实乱序：

- **[56]（Skinnider/Augur）**唯一出现于 pos 56290（Results "Benchmarking against perturbation-response metrics" 小节），早于 **[38]（Waxman，housekeeping dysregulation）**的首引 pos 59605
- [38]-[55] 相互之间顺序递增，可整体 +1 顺移

误报裁定（非引用，不改）：
- `[0, 1]` @90256 — JS 散度取值范围
- `[12, 74]` @115872 — bootstrap 95% CI（Strong-candidate count 39）
- 宽松正则命中的 `[7.37, 8.02]`/`[−0.08, 0.38]` — 校准基线与 cross-organ CI

**构建断言矛盾 reconcile**：v47/v47.1 构建 665/665 通过而 [56] 乱序未被发现，根因是 `_parse_citation_brackets` 与 N5b 的解析上限仍为 55（v45 新增 Augur [56] 时未同步上限），[56] 被当作非引用静默过滤。**断言通过 ≠ 顺序正确，属断言口径缺陷。**

## 3. 重编号映射

| 旧编号 | 文献 | 新编号 |
|---|---|---|
| 1–37 | （不变） | 1–37 |
| 56 | Skinnider et al.（Augur） | **38** |
| 38–55 | Waxman … Liberzon | **39–56**（整体 +1） |

正文引用组改动共 **20 处**（含两组多值：`[40,41]→[41,42]`、`[46,47]→[47,48]`）；`_refs_nar` 列表按同映射物理重排（Skinnider 移至第 38 位）。

## 4. 实施与同步

- `generate_manuscript_gb.py`：正文引用 20 处置换（re.sub 单趟回调，无碰撞）+ `_refs_nar` 重排；镜像同步 `CKI_Reproducibility_Package/`
- `99_build_gb_v47.py`：`_parse_citation_brackets` 与 N5b 上限 55→56；断言更新 V42-1（首引顺序 1..56）、V42-3（stale Kang [55]/[56]）、V42-4（dysregulation [39]）、V42-5/E4-8 消息、N5b（56/56）；changelog 补 v47.2 条目；镜像同步

## 5. 交叉验证结果（fresh DOCX 重建后）

- 构建 **665/665 全 PASS**（含新 V42-1：首引顺序 1..56，56 unique cited）
- 独立审计复跑：真实引用首引序列严格递增 **1..56**；[38]=Augur@56290 早于 [39]=Waxman@59605；[56]=Liberzon 为最后首引；剩余乱序点仅 [0]/[74] 两处已知误报
- 56 条全部被正文引用（N5b 56/56）；参考文献列表编号 1..56 完整
- finalize：v47 zip 65,440,597 B / 34 条目 / 复现包 297 文件；主目录副本同步

## 6. 结论

**CLOSED** — 参考文献编号已按正文首引顺序排列，独立审计与构建断言（口径修复后）双通道一致。

审计脚本：`_tmp_fa_review/audit_refs_order_v472.py`（幂等可复核）、`_tmp_fa_review/renumber_refs_v472.py`（含 20 处置换与列表重排的全部锚点断言）
