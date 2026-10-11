# nc70 图表精简 — Phase 0 盘点与 panel 字母映射表（2026-10-11）

目标：主图 7→5、附图 19→9，每图 4 或 6 panel。STAGE = results/figures_v58_author/（26 PDF）。

## 一、脚本归属（决定操作方式）

| 图 | 来源 | 操作方式 |
|---|---|---|
| Fig 1/3/4/5/6、SF 1–14 | 一作 v6 PDF，无源脚本 | PyMuPDF 矢量带裁块重排（先例 _tighten_figure1.py） |
| Fig 2 | notebooks/_regen_fig2_3tier_nc64.py + _regen_fig2_toprow_nc49.py + _merge_fig2_v497.py | 改脚本重绘 |
| Fig 7 | results/audit/_nc67_fig7.py | 改脚本重绘（并入新 Fig5 作 e,f） |
| SF 15–18 | results/audit/_nc66_figures.py | 改脚本重绘（合并为 SF7/SF8） |
| SF 19 | notebooks/_nc68_fig_theory.py | 不动（新 SF9 = 旧 SF19） |

注：Fig 3a panel 标签为轮廓 path 非文本（程序化检测用墨迹几何，勿靠文本抽取）。

## 二、主图映射（7→5）

| 新图 | 新 panel | 旧来源 | 内容 | MS 旧引用 → 新引用 |
|---|---|---|---|---|
| Fig 1 (4) | a | 旧 1a+1b 并排合并 | 概念+管线示意 | Fig. 1（495/509/513/524）不动 |
| | b | 旧 1c | bootstrap | |
| | c | 旧 1d | scatter | |
| | d | 旧 1e | full-matching expectation | |
| Fig 2 (6) | a | 旧 2a | k_n 校准 | Fig. 2a（526）不动 |
| | b | 旧 2b+2c 合并 | CSDX 分解+ω 类别 | Fig. 2b（528）不动；Fig. 2c（734）→Fig. 2b |
| | c | 旧 2d | TS 热图 | Fig. 2d（535）→Fig. 2c |
| | d | 旧 2e | 模拟检测 ROC | Fig. 2e（552/554）→Fig. 2d |
| | e | 旧 3a+3c 合并 | Kang FPR + 脑漂移误报 | Fig. 3a（558）→Fig. 2e；SI 'main-text Fig. 3a'→2e |
| | f | 旧 3b | 脑校准阶梯 | Fig. 3b（559）→Fig. 2f；SI 'main-text Fig. 3b,c'→2f |
| Fig 3 (4) | a–d | 旧 Fig 4 原样 | TCGA | Fig. 4（566/573）、Fig. 4a（573）、Fig. 4b/4c（575）→Fig. 3*；锁定串 'Fig. 4c, d'→'Fig. 3c, d' |
| Fig 4 (4) | a–d | 旧 Fig 5 原样 | 跨器官 | Fig. 5（573/583）→Fig. 4；锁定串 '(Fig. 5; Table 1; Supplementary Fig. 6)'、'(Table 1 / Fig. 5)' |
| Fig 5 (6) | a–d | 旧 Fig 6 原样 | 脑 | Fig. 6（583/590）→Fig. 5 |
| | e,f | 旧 Fig 7 a,b | 神经元超类 | Fig. 7（590/592）→Fig. 5e,f |

## 三、附图映射（19→9）

| 新 SF | panel | 旧来源 | MS/SI 引用改号 |
|---|---|---|---|
| SF1 (6) | a,b,c + d,e + f | S1(3) + S13(2) + S14(1) | S13（MS 682；SI 2893/3228）→SF1d,e；S14（MS 732；SI 794）→SF1f |
| SF2 (4) | a,b + c,d | S2(2) + S5(2) | S5（MS 573）→SF2c,d；锁定串 'Supplementary Fig. 5b'（SI 2129 + si_verify + ms_verify）→SF2d |
| SF3 (4) | a,b,c + d(并) | S3(3) + S4(2 并 1) | S4（MS 566；SI 2301）→SF3d |
| SF4 (4) | a,b,c + d(并) | S7(3) + S8(2 并 1) | S7（MS 590）不动号；S8（MS 598；SI 830）→SF4d |
| SF5 (4) | a,b,c + d(并) | S9(3) + S10(2 并 1) | S9（MS 610）→SF5；S10（MS 612；SI 795）→SF5d |
| SF6 (4) | a,b + c + d | S11(2) + S12(1) + S6(1) | S11（MS 614；SI 2672）→SF6a,b；S12（MS 643）→SF6c；S6（MS 583）→SF6d；锁定串 '(Fig. 5; Table 1; Supplementary Fig. 6)' 改号 |
| SF7 (6) | a,b,c + d,e,f | S15(3) + S16(3) | S15a/b/c（SI 2932/2947/2951）不动；S16c（SI 2953）→SF7f；S16b（SI 2957）→SF7e；MS 645 S15→SF7 |
| SF8 (4) | a,b + c,d | S17(2) + S18(2) | S17（MS 592/795；SI 3017）→SF8；S18（MS 645；SI 3057）→SF8c,d |
| SF9 (4) | a–d | S19 原样 | S19（MS 519；SI 3072）→SF9 |

「(并)」= 旧图两个 panel 并排收进一个字母下（奇数→偶数收敛）。

## 四、断言/锁定串同步清单（Phase 3/4 必改）

- `_nc49_ms_verify.py`：fignums == 1..7 → 1..5；'Fig. 4c, d'→'Fig. 3c, d'；'(Fig. 2d)' anchor 改号；'Fig. 2e'×2 改号；'(Fig. 5; Table 1; Supplementary Fig. 6)'；'Supplementary Fig. 5b'（sfull）
- `_nc49_si_verify.py`：'Supplementary Fig. 5b'→SF2d；'(Table 1 / Fig. 5)'→'(Table 1 / Fig. 4)'
- `_nc51_xv8.py`：legends 1..7→1..5；zip 34 条目→24；Supplementary_Fig_14.pdf 断言改；'Supplementary Figs. 1–19'→'1–9'
- `99_build_nc_v49.py`：staging 27→15（5 main + 9 supp + GA）；SF 拷贝循环 1..19→映射表；36 refs 断言重计；V49-N19 图 1-7→1-5；N20/N21 图注内容检查改号；'main-text Fig. 3a'/'3b,c'；Guide 'Supplementary Fig. 8)'；zip 条目白名单（figure6/7、SF 13-19 全改）
- SI legends 头：'Supplementary Figures (legends for Supplementary Figs. 1-19)' ×2 处（TOC + 正文）→1-9；19 条图注重写为 9 条（合并内容拼接）
- Guide（100_gen_reproducibility_nc.js）：附图文件清单 19→9

## 五、MAIN 词额纪律

仅改图号数字，不增删词；改后重跑 XV8 词额断言（MAIN 4,994/5,000 现状）。
