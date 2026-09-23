# nc52 复现基础设施修复实现说明（R6 Major #2–#5 + minors）

执行人：W-repro。日期：2026-09-24。
环境说明：本机无 conda；`cki_env` 为仓库内 venv（`cki_env/Scripts/python.exe`，Python 3.14.4），
所有 `conda run -n cki_env python ...` 均以该解释器等价执行。因环境为 venv 而非 conda 管理，
`conda env export` 不适用，未生成 environment-lock.yml（pip 锁文件已覆盖）。

## F2 依赖钉死
- 新增 `requirements-lock.txt`：`pip freeze` 自验证环境（79 个钉死依赖；剔除 cki 自身的
  editable ssh 行，加头注释说明生成方式与 cki 需单独安装）。
- `Dockerfile`：版本漂移 v0.4.4 → v0.5.0（第 1/6/7 行）；改为
  `pip install -r requirements-lock.txt` 后 `pip install --no-deps .`。
- 指南（`notebooks/100_gen_reproducibility_nc.js`）：
  - 1.2 节安装指引指向 `requirements-lock.txt`（requirements.txt 标注为开发用宽松约束）；
  - 结尾 "obtain numerically identical results" 承诺改为 "within Monte-Carlo and
    floating-point tolerance"，并引 SI 5.12 的 MC 误差说明（TCGA subsampling/cluster
    bootstrap ±0.01–0.02、LUAD KRAS–EGFR 置换 P 末位不稳定）。
- 同步：`ENV_SETUP.md` 2.2 节新增锁文件安装方式（推荐）。

## F3 nc50 microglia 入复现体系
- 指南新增 5.12 节（nc50 Analyses）：设计（35 对 sample-matched microglial cell vs CNS
  macrophage 功能对；40 个 half-splits 中性对，每型 20；组规模下限 200/100；≥20 cells/组，
  563 合格组）、流程（CP10k+log1p group means，TS 聚合顺序）、HK 1,107、HVG2000 excl HK、
  kn_floor=1e-4、seed 42；结果 ω 21.83±7.20 vs 1.30±0.36，MWU P=5.5e-14，AUC=1.00；
  数据 data/human_brain_atlas_microglia.h5ad（CELLxGENE collection
  283d65eb-dd53-496d-adb7-7570c7caa443）；5.12b 为 nc50_fig_microglia.py（Supplementary Fig. 14）。
- 指南 Section 6 新增 nc50 输出条目（csv/txt）；图脚本行补 nc49/nc50 图脚本。
- 指南 Section 7 新增 nc50 checklist 条目。
- `scripts/spot_check.py` 新增第 10 节 6 条 nc50 断言（风格与既有 check() 一致：
  n=35/40、ω 均值 21.83/1.30（tol 0.01）、MWU P=5.49e-14、AUC=1.00）。
  断言总数 40 → 46，指南两处计数同步（5.7h 描述行 + Section 7 checklist 行）。
- minors (d)：指南 "7 tests" → "29 tests: 22 smoke + 7 reference-value tests"（已按
  pytest --collect-only 实测分布核实）。

## F4 run_all.py 更新
- 头注释去 "Genome Biology manuscript (v40+)"，改为 NC v50 说明（并解释 gb/nar 历史命名）。
- 编排扩展：新增 Phase 6c（v45：88/89/90 + 脑 91/91b）、Phase 6d（nc49：
  nc49_pilot_kang_techrep/92/nc49_agg_order_sensitivity；脑 nc49_brain_drift_ladder/95/96/97；
  TCGA nc49_tcga_main/nc49_pilot_lihc_cox/nc49_tcga_purity/nc49_tcga_luad_smoking/
  nc49_tcga_kf_composition/93/98/94/nc49_lihc_cox_excc）、Phase 6e（nc50 microglia，
  数据缺失时 SKIP）。Phase 7 增加 nc49_fig_drift_ladder（Fig. 3）、nc49_fig_tcga（Fig. 4）、
  nc50_fig_microglia（Supp. Fig. 14）。
- 脑 Group D 由 07c_brain_siletti_v3.py 切到 07d_brain_siletti_v4.py（07c 输出已 superseded）。
- verify-only 路径与 "Next steps" 指向 99_build_nc_v49.py；头部验证注释同步。
- `--dry-run` 与语法检查通过。
- `data/README_data.md`（及 CKI_Reproducibility_Package 副本）"main-figure pipeline" 修正为
  nc49_fig_drift_ladder.py / nc49_fig_tcga.py / nc50_fig_microglia.py。

## F5 SI 脚本索引勘误
- `notebooks/68_gen_supplementary_nc.py`（仅 Supplementary Data 1 "Analysis Script Index"
  那一处字符串）：脑条目 07c_brain_siletti_v3.py → 08d/08e block-shuffle null（注明 07c
  输出在 results/superseded/，与稿件矛盾）。
- 勘误 (b) 的实际情况：生成器与已构建 SI 中均不存在 "13_phase35_human_pairs.py" 字样
  （grep + docx 全文核查为 0 次）；索引原本未列 phase35 脚本。按勘误意图在同一字符串内
  补入正确名称 `notebooks/13_phase35_method_comparison.py`。未改任何其他位置。
- 构建脚本/_nc49_si_verify.py 对该段无脚本名级断言，改动与既有断言兼容。

## minors 打包
- (a) `.github/workflows/ci.yml`：matrix 加 "3.14"（注释说明 3.14 为验证环境版本）。
- (b) `data/README_data.md`：种子表述改为与指南 1.4/SI 5.13 一致的例外清单
  （77/78/79→20260903，77 另有 777000；89→20260905；仿真模块种子 137/2024，已核实
  45/49 脚本 MODULE_SEEDS = [42, 137, 2024]）；数据源表补 Kang GSE96583 与
  data/human_brain_atlas_microglia.h5ad 两行；包内副本同步。
- (c) `ENV_SETUP.md`：v0.4.4+ → v0.5.0+（第 3/50/280 行）；RAM 最低 16 GB → 32 GB
  （以指南 Section 1.3 为准，第 14/120/261 行）。
- (d) 见 F3 末节。
- (e) `results/phaseC_calibrated_cis.csv` 不加 csv 内注释（pandas 默认读取会将其误作数据行，
  且仓库无该文件读者）；改为新建 `results/README.md` 声明 legacy 6.67、superseded by 7.70
  （指南 5.7 已有同义声明，此处为文件侧落点）。

## 验证实跑结果
- `scripts/spot_check.py`：ALL CHECKS PASSED（46 断言，含 6 条新 nc50）。
- `pytest tests/ -q`：29 passed（22 smoke + 7 reference，警告 9 条均为既有 FutureWarning/
  UserWarning）。
- `99_build_nc_v49.py`（实跑 3 次，日志 results/audit/_build_nc52_repro.log）：
  - 第 1 次：在我全部改动提交后运行，全部已执行断言通过，但在 line 334
    `from openpyxl import load_workbook` 崩溃——构建顶层解释器（cki_env）缺 openpyxl
    （环境问题，与本次改动无关；此前构建由其他解释器/环境完成）。
  - 处理：向 cki_env 与构建 PY（workbuddy default env）均安装 openpyxl 3.1.5，
    并重新生成 requirements-lock.txt（81 pins，commit 240b324）。
  - 第 2 次：被 safe-delete 钩子拦下图归档移动（批量 ≥50）；改用仓库自带开关
    `CKI_BUILD_NO_ARCHIVE=1` 重跑（不删档，仅跳过归档移动）。
  - 第 3 次（NO_ARCHIVE）：**219 通过 / 2 失败**。仅有的 2 个 FAIL 是
    "run: Generate Manuscript (NC v49)" 与 "run: Generate Supplementary (NC v49)"，
    原因均为 FileNotFoundError: results/nc49_tcga_pancancer.csv——该文件被 W-tcga
    的 nc52-tcga 迁移（commit 621ef81，ex-CC 默认主链）移入 results/superseded/，
    而 MS/SI 生成器（我之禁区）尚未改读新表。**与本次改动无关**：68 生成器在
    line 116 即失败，远在我改的索引字符串（line ~2742）之前；指南（node 生成器、
    无 csv 依赖）成功重生成且全部指南断言 OK。
  - 已实核重生成产物：CKI_Reproducibility_Guide_NC.docx 含 5.12 nc50 节、
    46-assertion/29-tests 计数、Monte-Carlo tolerance 结尾；SI/MS docx 因上述
    输入缺失未重生成（盘上是 01:19 旧版），F5 索引改动将随 #18/#19 同步后的
    下一次构建生效。68 语法 ast.parse 通过。
  - 结论：构建 0-fail 当前被 W-tcga 迁移的生成器输入同步阻塞（已私信 W-tcga
    确认同步归属 #13 后续还是 #18/#19）；本任务范围内全部改动均已验证。

## Commits
- ea3884c  nc52-repro: F2 dependency pinning + F3 nc50 microglia into repro system
- 3562afd  nc52-repro: F4 run_all.py orchestration to NC v50 + README_data fixes
- 9705178  nc52-repro: F5 SI script-index errata + minors package
- 240b324  nc52-repro: lock file regenerated with openpyxl 3.1.5 (81 pins)

注意：ea3884c 意外裹入了队友已暂存的 `results/audit/nc52_impl_stats.md`（内容未改，
仅是落在本 commit 里）；已在汇报中向 team-lead 说明。

## 遗留问题
- 构建 0-fail 待 W-tcga/#18/#19 完成 MS/SI 生成器输入同步后复跑确认（当前 219/2，
  2 个 FAIL 均为缺失的 nc49_tcga_pancancer.csv，非本任务改动）。
- 未生成 environment-lock.yml（venv 环境，conda 不可用；pip 锁文件已覆盖钉死需求）。
- run_all.py 未实跑全编排（数据量大、耗时长）；仅做 dry-run/语法验证与既有输出存在性检查。
- 仓库根残留未跟踪文件 requirements-lock.tmp（safe-delete 钩子拦 rm 后的遗留，内容与
  锁文件相同，可随手清理）。
- 指南 5.12 文本为新增，未触及构建脚本与 results/audit/ 下 verify 脚本（禁区遵守）。
