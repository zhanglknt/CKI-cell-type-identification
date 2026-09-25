# nc57 交叉验证报告（2026-09-25 晚，@93d03f4）

范围：F1–F9 + O1/O2 全部修复与 v0.5.4 发布链（含 O 修复后资产二刷）的端到端独立核销。
脚本：`results/audit/_nc57_cross_validation.py`（B–G 节 32 项程序化断言）；A/F 节为交互实测引用。

## A. 验证层（最终构建即时实测）

| 项 | 结果 |
|---|---|
| 99_build_nc_v49（含 ms 127/si 121 self-check） | **221/221 PASS** |
| XV8 | **63/63 ALL PASS**（MAIN 4,998/5,000、摘要 195/200、标题 13、图注 max 315、Discussion 无子标题） |
| spot_check | ALL PASS |
| pytest tests/ | **29 passed**（含 excc 口径新测试） |

## B. 修复落位（12 项全 PASS）

F1 括号配对、F2 across strata（small-stratum 绝迹）、F3 "35.7–45.2%" ×2（旧区间绝迹）、F4 kidney 1.6×、F5 L14 global、F6 SI sanity-check（validation value 绝迹）、F7 裸节号删且全式指针保留、F8 far 删、F9 excc 测试在、O1 null 枚举 + 双 trim、O2 摘要去重（195 词）。

## C. 版本面（8 项全 PASS）

MS v0.5.4 ×5（4 版本面 + DOI 句）；SI v0.5.4 ×2 + "version 0.5.4" ×1；Guide 0.5.4 ×3；pyproject/init/Dockerfile ×3；全文无 0.5.3 残留；MS DOI = 10.5281/zenodo.22958249（旧两版 DOI 均绝迹）。

## D. 发布链（7 项全 PASS）

local HEAD == remote main（93d03f4）；tag v0.5.4 在远端；Release 396502805 单资产 **588422612**，digest 与本地 zip sha256（43e7a7e6…）一致；body 含 v0.5.4 DOI + nc57-residual build 注明；Zenodo 22958249 = v0.5.4 state done；related → GitHub tree v0.5.4。

## E. 数据↔稿面独立复算（4 项全 PASS）

- excc 五癌种 NN/TT（2.464/1.708/1.112/1.880/1.567）与 MS L47 及摘要 1.11–2.46 逐值一致（±5e-4）
- 肾 GA/GG 中位数比独立复算 **1.566** → SI "kidney 1.6×" 成立
- SI 3.12 五度量 FPR 枚举（45.2/44.1/40.6/37.6/35.7）与 MS/Fig 3c "35.7–45.2%" 区间自洽
- 摘要 195、MAIN 4,998（XV8 口径复测）

## F. DOI 解析（交互实测，21:3x GMT+8）

| DOI | 状态 | 落点 |
|---|---|---|
| 10.5281/zenodo.22958249（v0.5.4） | **200** | records/22958249 |
| 10.5281/zenodo.22954782（v0.5.3） | **200**（DataCite 滞后已自愈） | records/22954782 |
| 10.5281/zenodo.20405458（concept） | **200** | records/**22958249**（latest 已指向 v0.5.4） |

R6 nc57 两条件项（N1/N2）+ v0.5.3 遗留复核项至此**全部 CLOSED**。

## G. git 卫生

工作区干净（脚本+本报告提交后复跑确认）。

## 判定

**ALL PASS（32/32 + A/F 节）——投稿包全链零开口，CLOSED。**
