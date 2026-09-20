# NAR 模拟审稿报告（Reviewer 5：可复现性与软件工程）

**期刊**: Nucleic Acids Research
**稿件**: CKI: A Cell-state Kinetic Index for Quantifying Baseline-Normalized Transcriptomic Remodeling（投稿包 v37，2026-08-28）
**审稿人角色**: 复现性 / 研究软件质量 / 数据与代码可得性
**审稿日期**: 2026-08-28
**核验范围**: 主稿、补充材料、复现指南、cover letter、Table 1–2、MANIFEST_v37；本地仓库 `cki/` 包源码、`pyproject.toml`、`requirements.txt`、`ENV_SETUP.md`、git 历史（tag/commit/工作区三态）、`results/` 下 reviewer_* 及关键输出文件、notebooks 脚本（06/07/07c/08d 等）。

---

## 一、贡献总结

本稿提出 CKI（cell-state kinetic index，ω = k_f/k_n），将两组细胞群体之间的 Jensen–Shannon 散度分解为 housekeeping 基因上的基线分歧率 k_n 与 identity 基因上的功能分歧率 k_f，类比 Ka/Ks 的启发式逻辑，量化"相对于内部基线的功能分化"。方法在四个数据集上验证：Tabula Muris 小鼠图谱（校准，split-half 基线 ω = 6.67）、Tabula Sapiens 人图谱（4,851 对，与四种标准度量的相关结构及 ratio-artifact 分解）、TCGA 泛癌（NN/TT 收敛，exploratory 定位）、Siletti 人脑 snRNA-seq 图谱（888,263 非神经元核，31,764 跨区对，6.88 倍区域分化梯度 + 乘法残差迁移候选筛选）。配套发布 Python 包 `cki` v0.3.1（MIT）及 GitHub/Zenodo 归档。

从可复现性视角看，本稿有多处值得肯定的努力：(1) 复现指南结构完整（环境、参数表、逐步 checklist、输出文件清单、脚本索引）；(2) v37 新增的 §5.6 将五项 reviewer 稳健性分析（脚本 38/39/41/42/43）连同输出文件一并文档化；(3) 我抽查了本地结果文件与手稿数字的一致性，均能对上——`results/reviewer_brain_splithalf_summary.txt` 的 brain 内部基线 12.29 [12.12, 12.47]、`results/brain_bs_null_ct_test.csv` 的 astrocyte ω=76.83 / 31,764 对、`results/mouse_pilot_v2_results.csv` 的六个 C_control（均值 6.67，range 1.59–12.16）、`results/reviewer_lineage_enrichment.txt` 的 55 Strong / 31,764 对。手稿在统计诚实性上（block-shuffle null、FDR 不可达的结构性说明、ω_cal 数据集相对性、TCGA exploratory 定位）较上一轮有明显改进。

然而，本次审稿的核心发现是：**手稿所描述的代码状态与实际可获取的代码状态之间存在系统性断裂**。发布 tag 的核心数学（JS 对数底）与论文不符；block-shuffle 等关键管线脚本与几乎全部结果文件不在公开仓库；Data availability 中至少两处声明（Dockerfile、"tag v0.3.1 包含全部 notebooks 与数据"）经核验为不实；包版本号在 `pyproject.toml`、`cki/__init__.py`、论文文本三处自相矛盾。以下逐条列出。

---

## 二、问题清单

### Critical

**C1. 发布的代码版本与论文方法不一致（"三态代码"问题）**
`cki/core.py` 的 `js_divergence` 与 ω 分母处理在三个代码状态下各不相同，而论文/指南/发布物各自只与其中一个状态一致：

| 代码状态 | JS 对数底 | k_n floor | 与之相符的文档 |
|---|---|---|---|
| tag `v0.3.1`（ed3409b，2026-07-05） | `np.log`（自然对数） | 无 floor（`omega = kf/kn if kn>0 else inf`） | 无 |
| HEAD（fd96207） | `np.log2` | **无条件** `kn_min=1e-4` clamp | 复现指南参数表（部分） |
| 工作区（**未提交**） | `np.log2` | `kn_floor=0.0` 可选参数，默认关闭 | 主稿 Methods |

证据：`git diff v0.3.1 -- cki/core.py` 显示 tag 版本使用 `np.log`；commit fd96207 的信息自述 "Restore v0.3.2 fixes to cki/core.py ... log2 JS divergence + kn_min=1e-4 clamp"；`git diff HEAD -- cki/core.py` 显示工作区把无条件 clamp 改成了 `kn_floor=0.0` 默认参数。主稿 Methods 明确写 "JS divergence uses the base-2 logarithm (range [0, 1])" 且 "the package default (kn_floor = 0) applies only a positivity guard ... so no reported single-cell ω was capped"——即论文对应的代码**只存在于未提交的本地工作区**。复现指南 §1.2 又声称 "Version: 0.3.1 (editable install from project root)"，等于承认验证环境绑定在本地不可获取的状态上。

后果：(a) tag `v0.3.1`（即 Data availability 指向的发布物）用自然对数，所有 k_n/k_f 分量绝对值与文档不符——影响 Fig. 2 的 k_n/k_f 分解、SN 3.7 的 k_n 统计（mean 0.0027 等）、dimensionality simulation 常数（0.155–0.159）——虽然 ω 本身因对数底在比值中抵消而不受影响；(b) HEAD 的无条件 1e-4 clamp 会让任何用公开代码复现 brain 分析的人（手稿报告 min brain k_n = 7.7×10⁻⁵ < 1e-4）得到与论文不同的 ω 值。

**要求**：提交工作区代码，bump 版本号，打新 tag，重新归档 Zenodo；在复现指南中写明确切的 commit hash 与 `pip install` 目标；逐处核对三态行为差异并出具说明（尤其是 1e-4 clamp 是否影响任何已报告数值）。

**C2. 公开仓库缺少论文引用的关键脚本与结果文件，Data availability 声明不实**
手稿 Data availability 称 "All analysis notebooks and processed data matrices are available in the same GitHub repository (tag v0.3.1)"；补充材料 Supplementary Data 1 称 "Complete analysis scripts used in this study are organized in the notebooks/ directory of the GitHub repository"。经核验（`git ls-tree -r HEAD`）：

- 公开仓库仅跟踪 **26 个 notebooks** 与 **4 个 results 文件**。缺失：`08d_brain_blockshuffle_null.py`、`08e_brain_blockshuffle_results.py`（block-shuffle 再分析的核心，Supplementary Tables 3–4 与手稿 brain 结果的全部基础）、`30_nar_figures_fixed_v2.py`（图件生成）、全部五个 reviewer 稳健性脚本 `38/39/41/42/43_reviewer_fix_*.py`（指南 §5.6 逐条引用的文件）。
- 复现指南 §6 列出的数十个输出文件（`brain_bs_null_*`、`phaseB_*`、`phaseC_*`、`phase35_all_metrics_pairs.csv`、`reviewer_*` 等）在公开仓库中**全部缺失**（我逐一用 `git ls-tree` 核验，10 个抽检文件 9 个 MISSING）。
- 指南 §1.4 声称 LIHC/LUAD 临床数据 "bundled in data/tcga/"，§3.1 指定 HK 参考文件路径 `data/housekeeping/Human_Mouse_Common.csv`——两者在本地工作区存在，但公开仓库的 `data/` 下只有一个 `README_data.md`。
- 上述删除来自 commit 403cfe7（"remove ... intermediate results, 475 files"）。

Zenodo 归档（DOI: 10.5281/zenodo.15670808）无法由审稿人核验，但鉴于 GitHub 端声明已证伪，作者必须提供归档内容的完整清单（含 checksums）供编辑部核验。按 NAR 对 methods 论文的标准，这是目前最接近拒稿理由的问题。

**要求**：将全部分析脚本、结果 CSV/JSON、bundled 临床数据恢复至发布仓库（或证明 Zenodo 归档完整覆盖）；给出文件级 checksum 清单；更正两处不实声明。

**C3. k_n floor 行为在三份文档间相互矛盾**
- 主稿 Methods（第 20 段）：kn_floor=0 用于 mouse/human/brain，仅 TCGA 用 1e-4；
- 补充材料 SN 1.1："a small floor value (1e-4) is applied to k_n to prevent inflated omega"，且 Algorithm 1 伪代码第 7 行 "if k_n < 1e-4: k_n <- 1e-4"（无条件）；
- 复现指南参数表："k_n floor (minimum) | 1e-4 | all analyses"。

实际 notebook（`08d` 第 146 行 `kn > 1e-15`；`06_phase34_v2.py` 第 289 行 `kn_floor=1e-4`）支持主稿描述，即补充材料与复现指南是错的。但若作者按补充材料/指南的写法复现，brain 中 k_n < 1e-4 的对（手稿报告 min 7.7×10⁻⁵）会被 cap，得到不同的 ω 分布、不同的 tier 划分乃至不同的 55 个 Strong 候选。**要求**：统一三处文档；报告 floor 激活的 pair 数及其对结论的影响。

**C4. Methods 对 PAM50 分类的描述与实际管线不符**
主稿 Methods："PAM50 classification (23,24): nearest centroid (Pearson correlation), 44 of 47 PAM50 genes matched"。但实际脚本 `notebooks/07_phase34_clinical.py` 从 cBioPortal API（brca_tcga_pub，`PAM50_SUBTYPE` 属性）**拉取**子型标签（第 140–156 行，带本地 cache）；全仓库无任何脚本实现 nearest-centroid PAM50（`grep -rln "nearest centroid|centroid"` 无命中）。这不仅是复现问题，更是方法描述失实。附带问题：PAM50 依赖 live API 拉取（指南 §1.4 自认 "fetched live by script"），存在可用性与可复现性风险。**要求**：更正 Methods 或补充 centroid 实现脚本；将 PAM50 标签快照随仓库发布。

**C5. Dockerfile 声明不实**
Data availability："A Dockerfile is provided in the repository for containerized reproducibility"。工作区与 git 全树均无任何 Dockerfile（`git ls-files | grep -i docker` 返回 0；工作区 `ls Dockerfile` 失败）。在环境仅以 "editable install + Python 3.14.4 验证" 描述的情况下，容器化恰恰是最需要的复现手段。**要求**：提供 Dockerfile（并放入 CI），或删除该声明。

### Major

**M1. 环境规格互相矛盾且不可复现**
- scanpy 版本：主稿 Computational environment 写 "scanpy 1.12.1"，复现指南 §1.1 写 "scanpy: 1.10.4"——直接矛盾，必有一处不实。
- Python 3.14.4 声称 "verified environment"，但 `ENV_SETUP.md`（2026-08-10）推荐 3.11+；RAM 要求指南 >=32 GB vs ENV_SETUP 最低 16 GB；磁盘 5 GB vs 20 GB。
- `requirements.txt` 全部为 `>=` 下限约束且混入文档生成依赖（python-pptx、reportlab、PyPDF2、PyMuPDF、pywin32），不是分析环境的忠实规格；无 lockfile、无 conda env、无 pin。
- 指南结尾声称 "readers should obtain numerically identical results"——在上述条件下该承诺不成立。

**要求**：提供 pinned lockfile（或经 CI 验证的容器），统一三处环境描述，将文档生成依赖拆分。

**M2. 核心统计管线不在包 API 中，且 notebook 内重写了 ω 计算**
block-shuffle permutation null、multiplicative residual model、tier 划分——Results 5/6 与全部 brain 结论的统计基础——均以 notebook 脚本（08d/08e）内联实现，未进入 `cki` 包。更具体：`08d_brain_blockshuffle_null.py` 自定义 `pair_omegas()`（第 129–148 行）直接计算 `kf/kn`，**绕过了包的 `compute_omega()`**；两者之间无一致性校验或单元测试。同时高层 API `compute()` 不暴露 `kn_floor` 参数（`core.py:306-525` 的签名与调用均未传递），意味着用户无法通过包的公开 API 复现 TCGA 配置。**要求**：将 block-shuffle null 与 residual model 纳入包 API（或至少提供经测试的等价函数），并在文档中说明 notebook 与包实现的一致性验证。

**M3. 零测试**
仓库无 `tests/` 目录、无任何 `test_*.py`。对一个提出新数值度量的方法包：`js_divergence`（对数底、softmax、epsilon=1e-9）、`kn_floor` 分支、`calibrate_omega`、`benjamini_hochberg` 均无回归测试——而 C1 显示的对数底漂移正是缺测试的直接后果（自然对数版本可静默存活于 tag 中）。**要求**：为上述函数添加含已知值金标准的单元测试并接入 CI。

**M4. API 文档错误与跨期刊遗留文本**
- `compute()` docstring 声称 "use_reference_hk ... Default True"（`cki/core.py:382`），但签名默认为 `False`（`core.py:313`）——文档与行为相反，且直接影响 HK 基因集选择这一方法核心参数。
- 三处 "Genome Biology manuscript" 遗留（`cki/core.py:390`、`cki/gene_sets.py:355`、`cki/gene_sets.py:545`），指涉另一期刊版本的手稿，暴露文本复用历史；正式发布的包 docstring 中出现其他期刊名不专业，也会引发关于版本谱系的疑问。
- `compute_omega` docstring 仍写 "omega < 1: Purifying selection / omega > 1: Positive selection"，与主稿反复强调的 "heuristic index, not a formal measure of Darwinian selection" 新口径相悖（v36→v37 已在论文中修正，包内未同步）。

**要求**：修正 docstring 默认值描述，清除跨期刊遗留，统一解释口径。

**M5. 脚本/输出编号与"权威版本"标识混乱**
- mouse pilot：指南 §4.1/§5.4a 引用 `02b_pilot_v2.py` 与 `results/mouse_pilot_v2_results.csv`，§6 输出清单却写 "Mouse (02c_pilot_v2b.py): results/mouse_pilot_v2b_results.csv"。两份 CSV 的 C_control 数值相同（已核对），但报告数值究竟出自哪个脚本未说明。
- results/ 中存在大量指南未提及的产物：`brain_siletti_v4_*`（07d 脚本，与 v3 并存）、`reviewer_decomposition_*`、`reviewer_donor_confounding_structure.csv`、`reviewer_kf_kn_decomposition.csv`、`reviewer_brain_pair_kf_kn.csv`——审稿人无法判断哪个是权威管线，v4 是否为又一次未文档化的修正。
- 指南 §2.1 "All parameters used in the reported analyses:" 之后参数表在文本提取中脱离正文、出现在文档最末（DOCX 表格锚定问题），"见 Section 2.1" 的交叉引用在导出文本中失效。
- 指南 §3.2 的 "adapted to min(2000, 0.8 * n_total_genes)" 自适应规则在主稿中完全未出现。

**要求**：提供 script → output → figure/table 的权威映射表；标注 superseded 与 authoritative；修正表格锚定。

**M6. 数据可得性与许可细节不足**
- Tabula Sapiens `TS_{Organ}.h5ad` 与 Siletti `Nonneurons.h5ad` 无直接下载 URL/命令/checksum；指南 §4.4 仅写 "collection ID as referenced in Siletti et al."（主稿倒是有 collection ID，指南本身没有），对复现者不友好。
- HRT Atlas CSV 打包再分发（`cki/data/hrt_atlas.csv`）需在 LICENSE/NOTICE 中确认原始数据许可条款并致谢；`data/tcga/` 下 cBioPortal 派生临床 JSON 的再分发许可未说明（且这些文件根本不在公开仓库，见 C2）。

### Minor

- **m1.** MANIFEST_v37 第 5 项 "Table1-2.docx - Standalone **parameter** tables" 与实际内容（classification AUC 表 + cross-organ conservation 排名表）不符；参数表实际在复现指南里。
- **m2.** Cover letter 声称包 "runs on Linux, macOS, and Windows"，复现指南 §1.3 只验证了 Windows 10/11 x64 与 Linux x86_64（无 macOS）。
- **m3.** softmax 实现为 `exp_x/(exp_x.sum()+epsilon)`（`cki/utils.py:45`），与论文/指南公式 `exp(x_i)/Σexp(x_j)` 有 1e-9 的分母修正——数值无关紧要，但应在文档中如实注明。
- **m4.** 指南参数表仍列出 "Permutation null iterations 10000 ... Phase B (C-S3)" 等已被 block-shuffle null（B=1,000）取代的条目，虽有 superseded 标注但混在现行参数中易误导；建议移入独立的 historical 附录。
- **m5.** `ENV_SETUP.md` 为中文文档，与英文投稿的复现生态不匹配，外部复现者难以使用；且其内容（RAM/Python 版本建议）与复现指南不一致（见 M1）。
- **m6.** Supplementary Table 3 标题下写 "Summary statistics for each cell type ... are provided in Supplementary Table 3"——自我指涉，措辞应修正。
- **m7.** 本地仓库根目录混有 `node_modules/`、`version3/4/5/`、`CKI_Data_Full.zip`、`99_build_nar_v37.py` 等大量构建/中间内容；虽然 GitHub 端做过清理，但这种状态使误发布（把整个工作区当归档）的风险很高，也使 C1 类"三态漂移"难以避免。建议以干净的 release 分支 + tag 流程发布。

---

## 三、重点审视维度小结

| 维度 | 评价 |
|---|---|
| 复现指南可操作性 | 结构良好、checklist 详尽，本地数字抽查全部一致（这是亮点）；但环境无 lockfile、指南与主稿/ENV_SETUP 三处版本矛盾、参数表锚定错误、mouse pilot 脚本归属含糊 → **不及格边缘** |
| 包 API 与论文方法一致性 | `kn_floor` 默认值（工作区）与 TCGA 显式 1e-4 的设计本身合理，但 tag/HEAD/工作区三态不一致（C1）、三文档 floor 矛盾（C3）、`compute()` 不暴露 kn_floor、08d 绕开 `compute_omega`（M2）→ **不通过** |
| 版本管理 | `pyproject.toml`=0.3.1 vs `cki/__init__.py`=0.3.2 vs 论文/信/指南=0.3.1；"v0.3.2 fix" commit 从未 bump 版本或打 tag；Data availability 指向错误的 tag → **不通过** |
| 数据可得性与许可 | TCGA/Tabula 下载路径基本给出，但 brain/Tabula Sapiens 无直接命令与 checksum；HRT Atlas/cBioPortal 再分发许可未说明；更严重的是声称 bundled 的文件不在公开仓库（C2）→ **需大修** |
| 审稿人新增分析文档化 | 指南 §5.6 对五项 reviewer 分析的脚本、参数、输出记录完整，本地抽查数值一致——这是本稿做得最好的部分；但产物未进公开仓库（C2），且另有六七个 reviewer_*/v4 输出未文档化 → **方向正确，执行未闭环** |
| zip 包内容完整性 | MANIFEST 与实际文件相符（除 m1 的 "parameter tables" 描述错误）；但投稿包本身不含任何代码/结果，完全依赖外部仓库——而外部仓库已被证伪（C2）→ **不足以支撑复现** |

---

## 四、总分与推荐决定

**总分：4.5 / 10**（NAR 标准：1–3 拒稿，4–5 Major Revision，6–7 Minor Revision，8+ 接收边缘）

**推荐决定：Major Revision**

理由：科学内容与统计诚实性在 v37 轮已达到可发表方向的形态——本地材料完整、数字可对上、局限披露充分。但作为方法学论文，其核心承诺（"readers should obtain numerically identical results"）在现有发布物上无法兑现：tag v0.3.1 的 JS 对数底与论文不符、floor 行为三文档三说法、block-shuffle 等关键脚本与全部结果文件不在公开仓库、Dockerfile 与 "tag v0.3.1 包含全部数据" 两处声明不实、PAM50 方法描述与代码不符、包版本号三处矛盾、零测试。这些问题全部可修复且不需要新的科学结论，因此不建议拒稿；但在完成 C1–C5 之前，任何数值复现都无法成立，故不能给予 Minor Revision。

**给作者的修改清单（按优先级）**：
1. 提交与论文一致的代码（log2 + kn_floor 参数化，默认 0），bump 至 v0.4.0，打 tag，重发 Zenodo，指南写明确切 commit hash（C1）。
2. 恢复全部脚本（08d/08e/30/38/39/41/42/43）、结果文件、bundled 临床数据与 HK 参考文件至公开仓库，附 checksum 清单（C2）。
3. 统一 k_n floor 的三处文档描述，报告 floor 激活情况（C3）。
4. 更正 PAM50 Methods 描述并随仓库发布标签快照（C4）。
5. 提供或删除 Dockerfile 声明（C5）。
6. lockfile + 环境三处矛盾修正（M1）；核心管线进包 API + 单元测试（M2/M3）；docstring 修正与 "Genome Biology" 遗留清除（M4）；权威管线映射表（M5）；数据下载命令与许可说明（M6）。

修改后若以上全部落实，本人愿意在下一轮以 Minor Revision 标准复审。
