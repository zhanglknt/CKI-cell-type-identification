# v49.5 参考文献重排 + 补引 + 字段修复审计报告

日期：2026-09-19 ｜ 执行：team-lead ｜ 状态：编辑+静态验证完成（构建待 c-drift 新 turn）

## 1. 背景与问题（xv-numbers 交叉验证发现）

- 首引顺序非单调：[56] Liberzon 在 Results「Three controls」段首引（v49.2 新增 Hallmark 检查），早于 [15]-[18]。
- [16][17] Perou/Parker、[15] Edmondson 直到 Methods TCGA 数据源段才首引。
- [55] CZI CELLxGENE 全文零引用（孤儿；NC 转换时 Data Availability 不再编号引用所致）。
- 字段错误 3 处：[35] Raj 标题错误、[37] Jiang 标题截断、[47] Hao 页码缺 .e29（cosmetic）。

## 2. 权威首现序列复核（AST 法，去代码索引假阳性）

对 generate_manuscript_nc.py 做 AST 解析，仅提取顶层 p()/heading() 字符串常量中的引用组（排除 f-string 插值代码如 {t2[0][1]} 的假阳性），得 73 组（与生成器断言一致）：

**1..14, 56, 18..48, 49, 50, 51, 16, 17, 15, 52, 53, 54**（孤儿 55）

注：xv-numbers 报告的尾部（52/53/54 先于 16/17/15）经双通道复核证伪——[52] seaborn、[53] scikit-learn 首现于 L705 计算环境段，[54] Efron 首现于 L708 统计段，均晚于 L670 的 [16,17]/[15]。本映射以 AST 序列为准。

## 3. 重排方案

在 Methods Tabula Sapiens 数据源句（L668，先于 TCGA 段）补引 CELLxGENE 后，目标序列：
1..14, 56, 18..48, **55**, 49, 50, 51, 16, 17, 15, 52, 53, 54

旧→新映射：1-14 不变；56→15；18-48→16-46（n−2）；**55→47**；49→48、50→49、51→50；**16→51、17→52、15→53**；52→54、53→55、54→56。

新文献表位置：15=Liberzon、16-46=旧18-48、47=CZI CELLxGENE、48=Weinstein、49=Colaprico、50=Cerami、51=Perou、52=Parker、53=Edmondson、54=Waskom、55=Pedregosa、56=Efron。

## 4. 执行内容（results/audit/_v495_refs_renumber.py，单脚本全断言）

- A 字段修复 3 处：旧35 Raj 标题→"Nature, nurture, or chance: stochastic gene expression and its consequences"（PMID 18957198）；旧37 Jiang 补 "using single-cell RNA sequencing data"（DOI 10.1093/bib/bbae283）；旧47 Hao 页码→3573–3587.e29。
- B _refs_nc 56 条按 NEW_ORDER 重排；16 个新位置 spot-check 全过。
- C 正文引用组改写 41 组 / 22 行：区间 [22-24]→[20-22]、[33-35]→[31-33] 保持连续；逗号组 [16,17]→[51,52] 等保逗号；混合组 [13,32]→[13,30]；无跨边界断裂区间（0 risky）。
- D 补引 2 处：L668 "accessed via CZ CELLxGENE Discover [47]."；L672 "from CZ CELLxGENE Discover [47] (collection ID: …)"。
- E _cite_sup_count 断言 73→75（注释同步更新）。

## 5. 验证证据

- 脚本自检：AST 重提取 75 组，首现序列 == 1..56 单调 PASS；7 组关键行期望（L559[15]、L668[9]+[47]、L670[48][49][50][51,52][53]、L672[12]+[47]、L705[44][54][55]、L708[56][43]、L702[51,52][53]）全 PASS；py_compile PASS。
- 生成器重跑：75 superscripted groups，docx 落盘。
- **_nc49_ms_verify.py：105/105 PASS（含新增第 13 节 14 项）**——上标组数 75、docx 首现 1..56 单调、无孤儿、文献表 1..56 连号、新位置 15/33/35/45/47/51/52/53/56/48-50 内容与字段修复全核对。
- SI 侧零改动：68 脚本仅引 [12]/[13]（≤14 恒等）；复现指南/CL/GA 无编号引用；ms_verify 既有 91 项无回归。
- 影响面排查：99_build_nc_v49.py 无文献编号依赖断言；_nc49_si_verify.py 无依赖。

## 6. 遗留

- 全量构建（99_build_nc_v49.py）待 c-drift 新 turn 执行（safe-delete turn 配额）；预期 126/126（上轮 125/126，唯一 FAIL 的 S8 已由 lead 改为节标题锚点）。
- 构建绿后：commit/push + ls-remote 核对 + CI 查询 + zip 交付。
- 审计脚本与日志留存：_v495_refscan.py、_v495_refscan2.py、_v495_refs_renumber.py、_v495_renumber_log.txt、_v495_ms_verify_out.txt。
