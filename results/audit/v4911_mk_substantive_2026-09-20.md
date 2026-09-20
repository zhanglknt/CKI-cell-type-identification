# v49.11 审计报告：MK 类比实质性重写轮（2026-09-20）

## 动机

v49.10 盲审 R2 判 MK 引用为 "name-drop"（C1）。小牛定夺：**类比实质性成立**——同义突变↔HK 差异（k_n）、非同义突变↔功能基因变化（k_f）、不同物种↔两群细胞。方向不是撤回类比而是把对应关系写透。

## 编辑（3 文件 +4 处）

1. **MS Discussion**（generate_manuscript_nc.py）：v49.10 的 MK 句重写——正面三重对应 "synonymous-site divergence (Ks) corresponds to HK-gene divergence (k_n), nonsynonymous divergence (Ka) to functional-gene divergence (k_f), and a species pair to the two cell populations being compared—the mapping of McDonald–Kreitman-style contrasts [34], with a constrained rather than neutral reference class"；声明 "The analogy is nonetheless substantive rather than nominal"；删除 "ω above 1" 锚点（改为读作 constrained baseline 之上的功能分歧，消除与校准基线 7.70/9.73 的冲突）；保留 "never as evidence of positive selection"
2. **SI 1.4**（68_gen_supplementary_nc.py）：在 "structurally similar but mathematically non-equivalent" 后同步三重对应句 + constrained 限定
3. **Fig 1a 图注**：k_n/k_f 命名为 synonymous/nonsynonymous 的 counterpart；ω 锚定改为 "read against the empirical calibration baseline rather than against 1"

## 构建与验证

- 断言 +N53/N54/N55，全量 **151/151** PASS；ms_verify 117 + si_verify 109 + cl_guide_verify 39 全 0-fail
- 摘要 199 词不变；渲染复核 10/10 句全对（旧 "ω above 1 should accordingly be read" 已清除）

## 包 / Git / CI / Release

- zip **12,259,589B**、27 条目、sha256 **a0f1a58a38cfe9b588602482b2e79059e1221a91c515e7fbfd022c84a14389d7**
- commit **688f1f9**（3 文件）；push + ls-remote MATCH
- CI 4/4 绿（py3.10-3.13）
- Release 387922141：旧资产 576574699 删 → 新资产 **576751282**（readback 12,259,589B MATCH）；正文 v49.11 块前置、latest 更新、旧 sha 替换

## 遗留（v49.10 盲审待办，本轮未处理）

N1 seed 20260905 申报、N2 Discussion softmax 口径、N3 阈值扫描第 4 梯度值、N5 Guide 依赖与参数表、C4 CC 敏感性分析、C5 Results/Discussion 6.10→1.74 领衔——待小牛指令。

## 判定：CLOSED
