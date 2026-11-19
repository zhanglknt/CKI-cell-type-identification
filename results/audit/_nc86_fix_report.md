# nc86 修复与重发报告 — A 类机械修复 + r6-alt 技术初筛线索 → v0.6.5

- **日期**：2026-11-19
- **作者裁定（本轮）**：A 类 8 项机械修复 → **执行并重发 v0.6.5**；B 类 → **启动 B1–B5 新分析**（路线见 `_nc86_b_class_roadmap.md`）
- **基线**：v0.6.4（远端 `main = d7e45cf4`，`tag v0.6.4 = 0d7d0576`），nc85 六人团均值 6.050 / 1 Reject + 5 Major
- **交付态**：包 23 文件、`CKI_Submission_NC.zip` **13,634,773 B**、sha256 `9a0fc8339f67fd2e9bca97ef6a04fa3111d069bb043acee804e9bf0443cef103`

---

## 1. 侦察先行：三个硬约束

改源前先做了精确落点侦察，避免盲改 374 KB 的 SI 生成器，查实三项约束：

| # | 约束 | 实测 | 处置 |
|---|---|---|---|
| C1 | **词额顶格** | MAIN（Abstract–Discussion）空格分词 **5,152**；摘要 148/150；CL 509/530；图注 max 337/350；Methods NC 软线 3,300 | 所有 MS 改动用**等长或净减**替换；图注新增披露压在 350 内 |
| C2 | **验证器硬锁定** | `_nc49_cl_guide_verify.py:51`（CL 56% 原句）、`99_build_nc_v49.py:771`（Guide 版本串）、`:586/:610/:636`（内部标签 / 因果动词）、`:270`（SI `Supplementary Fig. N` 计数 = 34）、`_nc49_ms_verify.py:417` | 改文案**同步改断言**，且每条新断言同时断言旧串消失 |
| C3 | **SF9 编号冲突** | MS 正文 `Supplementary Fig` 全称首现 `[11,1,2,3,4,10,5,6,8]`（SF7 只有裸 `Fig. 7`、SF9 零引用），与 SI「1–9 按首现」失配 | 补 SF4/SF7/SF9 全称 + Numbering note 加注，令 1–9 严格单调 |

---

## 2. A 类 8 项逐项核销

| # | 来源 | 落点（源码行） | 修改 | 状态 |
|---|---|---|---|---|
| A1 | R6 P1-2 / r6-alt P1-1 | `68:4368/4386/4436/4441` | `sheet Table 4/5/6` → `9/10/12`；`Tables 5 and 6` → `Supplementary Tables 10 and 12` | ✅ |
| A2 | R3 P1-1 + F7 | `68:4112/4119/4122`、`ms:573` | `creates rather than attenuates` → `tracks rather than`；`attributes 56% … to` → `associates at most 56% … with`（加上界）；主文 `creates` → `accompanies`、`attributes` → `apportions` | ✅ |
| A3 | R3 P2-1 / R6 P2 | `cl:117` + `_nc49_cl_guide_verify.py:51` | CL 补 `at most 56%`；验证器断言同步 | ✅ |
| A4 | R4 + R3 | `68:3855-3859`、`ms:618` | `decomposition is identified, not merely defined` → `identifiable in principle but is not estimated here`；`identified functional quantity` → `recovered`；`studentizes` → `rescales` | ✅（最小措辞降级，未引入新计算） |
| A5 | R5 P2-1/P2-4 | `ms:774` | Fig 4 图注补「Thalamic underpowered（Note 18）」与「lowest-CV anchor 消除超类信号 P = 0.72–0.92（Note 24）」；删 `anatomical` / `uncorrected` 抵冲 | ✅（337 → **348/350**） |
| A6 | R6 P1-3 | `ms:558` | 裸 `Fig. 4` → `Supplementary Fig. 4`；删 `cleanly` 抵冲 | ✅ |
| A7 | R6 P1-1 | 本报告 §5 | 出具实测词额凭证；确认净变化 **−1 词** | ✅（行政项，不进包） |
| A8 | R4 格式 | — | R4 判定标签 `<…>` 属**盲审报告原貌**，不篡改；在 panel 补记中注明 | ✅（记录不改） |

---

## 3. r6-alt 迟到报告（独立第七份技术初筛）的处置

`_nc85_review_R6_alt.md`：`7.0 / Minor Revision / P0 = 0 / 初筛「技术性退回」`。**不并入 nc85 六人团均值 6.050**，但技术线索全部纳入 A 类：

| 项 | 内容 | 处置 |
|---|---|---|
| P1-1 | SI 表注 3 处错误 sheet 指针 | ✅ 并入 A1 |
| P1-2 | SF9 零规范引用 + 裸 `Fig. 9` + Numbering note 失配 | ✅ 并入 C3 / A6，并在 SI Numbering note 补 SF9 引用位置与「`Note N, Fig. M / Table K` 简写」约定 |
| P2-1 | SI 旧图号 `global HVG set for Fig. 2` | ✅ → `Supplementary Fig. 1` |
| P2-2 | Guide `10x modular OC (Section 3.11; Fig. 2d)` 错配 | ✅ 去掉错误图号，保留节号 |
| P2-5 | MANIFEST / Guide 暴露内部轮次与批次标签 | ✅ MANIFEST 改中性描述、去 `v49` 批次标签；Guide 去 `(expert-panel round on v51r2)`、`(v49.14)`；**脚本文件名保留**（可复现性所需） |
| P2-6 | pip 安装方式不一致 + 词额顶格警告 | ✅ SI 统一 `pip install -e . at GitHub tag v0.6.5`；词额见 §5 |
| P2-3 / P2-4 / P2-7 | 2a/2b/2c 子面板标签、已清除残留、CL/推荐审稿人 | 记录不改（P2-3 非悬空、P2-4 已清除、P2-7 达标） |

**额外收紧（本轮新发现）**：只补 SF9 会使全称序列变成 `[11,1,2,3,4,10,5,6,8,9]`，SF7 仍缺位。故再补 MS 两处裸 `Fig. 7`（`ms:587/630`），并删 `known` / `directionally but` 抵冲。最终：

```
MS Supplementary Fig 首现序列 = [11, 1, 2, 3, 4, 10, 5, 6, 7, 8, 9]
SF 1–9 严格单调 = True（10/11 为已追认的伴生图例外）
裸 Fig. 7 / Fig. 9 残留 = 0
```

---

## 4. 版本号闭环与验证器同步

- 全部 `v0.6.4` → `v0.6.5`：`ms:664/733`（全文 5 处）、`68:693/1049/4453`（3 处）、Guide `:204/827/952`（3 处）、`99_build:216/770-771`、`_nc49_ms_verify.py:417`、`_nc49_cl_guide_verify.py:158-159`。
- MANIFEST：`tag: v0.6.5 | cross-reference and wording consistency revision; …`；`CKI Submission Package v49` → 去掉批次号；Note 改为中性。
- Zenodo 措辞「An earlier release is archived」**保持不变**（concept DOI 最新归档仍 v0.5.6，措辞不依赖 v0.6.5 归档存在）。

**首轮构建的 4 条 FAIL 全部为「断言锁定旧措辞」，非修复错误**，逐条诊断后同步断言：

| 断言 | 原值 | 新值 | 原因 |
|---|---|---|---|
| `V49-S6` SI `Supplementary Fig. N` 计数 | 34 | **36** | 新增 SF1（旧图号修正）+ SF9（Numbering note）两处正确引用 |
| `V49-N88` | 锁 `(v49.14)` | 去标签 | r6-alt P2-5 要求清理内部批次标签 |
| `V49-N101` | 锁 `creates rather than attenuates` | `tracks rather than attenuates` | A2 因果动词降级 |
| `V49-N90` | 锁 `(v49.14)` | 去标签 | 同上 |

另新增 10 条 `V49-NC86-*` 断言（A 类逐项生效 + 版本串统一 + SF1–9 首现单调），每条同时断言旧串消失。

---

## 5. 词额凭证（A7）

实测口径：`python-docx` 提取段落文本后按空格分词；NC 正式口径为 Word word count，两者对公式/连字符的处理不同。

| 项目 | v0.6.4 | **v0.6.5** | 限额 | 变化 |
|---|---|---|---|---|
| MAIN（Abstract–Discussion） | 5,152 | **5,151** | 5,000（团队声明口径） | **−1** |
| Abstract | 148 | 148 | 150 | 0 |
| Methods（含 Data/Code availability） | — | 3,474 | 3,300 软线 | 0（本轮未增词） |
| Cover Letter | 509 | **511** | 530 | +2（`at most`） |
| 图注 max（Fig 4） | 337 | **348** | 350 | +11（A5 披露）−2（删词） |

**结论**：MS 主文词额**净减 1 词**，未挤占任何缓冲；CL 与图注增量均在限额内。R6/r6-alt 所指「空格分词 ≈5,152 与 NC 正式口径 5,000 的差异」属计数口径差异而非硬超标，本轮未改变该差异，投稿前另附 Word 官方计数即可。

---

## 6. 全链交叉验证（0 failure）

| 环节 | 结果 |
|---|---|
| `99_build_nc_v49.py`（NO_ARCHIVE） | **250 / 250** |
| `_nc49_ms_verify.py` | 134 / 134 |
| `_nc49_si_verify.py` | 120 / 120 |
| `_nc49_cl_guide_verify.py` | 45 / 45 |
| `_nc51_xv8.py` | exit 0 |
| `_nc80_mj_crossval.py` | 137 / 137 |
| `scripts/check_figure_spec.py` | **15 / 15**（主图 ≥7 pt、附图 ≥5 pt、宽 ≤180 mm） |
| `pytest -q` | **29 passed** |
| 三方逐 sha256（`version3/` = 根包 = zip 内 23 条目） | **0 mismatch** |

`CKI_Submission_NC.zip` = 13,634,773 B，sha256 `9a0fc8339f67fd2e9bca97ef6a04fa3111d069bb043acee804e9bf0443cef103`。

---

## 7. 残余 minor（不阻断）

1. **Zenodo v0.6.5 版本归档未执行**：缺 API token；稿件措辞不依赖其存在。
2. **代码包版本串**：`pyproject.toml` / `cki/__init__.py` 仍为 `0.5.6`（v0.6.4 发布时即如此，本轮保持一致）；稿件声明的是 GitHub **tag** v0.6.5，二者不同层，未改以缩小未审计面。
3. **裸 `Table 11` / `Tables 12, 13` / `Table 14` 简写**：r6-alt 建议全稿统一 `Supplementary Table` 前缀，因词额顶格未做；已由 SI Numbering note 的简写约定明确定义，不构成悬空引用。
4. **B 类结构性问题**：nc85 判定仍为 Major Revision / 不 CLOSED；路线见 `_nc86_b_class_roadmap.md`。
5. **nc83 审计文件 / 大量 untracked 数据**：本轮未触碰。
