# NC Cover Letter 修订（落款仅通讯作者 + 行距适度增加）

日期：2026-09-25（nc57 交叉验证 32/32 闭环之后）
指令原文：*"coverletter落款只写通讯作者。行间距适度增加"*

## 改动（仅改生成器 `generate_cover_letter_nc.py`，未碰产物源码）

1. **落款只留通讯作者**（L159–161 段）
   - 删除 `add_para("Xianming Wu (First Author)", doc, space_after=0)`
   - 保留 `Li Zhang (Corresponding Author)` 与 `ORCID (corresponding author): Li Zhang 0000-0002-0698-0754`
   - 正文 L74 客套语 "On behalf of my co-author, Dr. Xianming Wu …" 保留（非落款，照旧）

2. **行距适度增加**（L40）
   - 初设 `line_spacing = 1.15` → LibreOffice 渲染实测 **2 页**，违反生成器 docstring 的 one-page 硬约束
   - 实测单页上限：1.0 / 1.03 / **1.05 = 1 页**；1.08 / 1.1 / 1.15 = 2 页
   - 最终落定 `line_spacing = 1.05`（w:line=252, lineRule=auto），即适度 +5% 且保单页

## 精准刷新（未跑完整 `99_build_nc_v49.py`，避免重跑 figure-staging 脚本）

脚本 `results/audit/_cl_refresh.py`：
- 重生成 `results/CKI_NC_Cover_Letter.docx`（504 词，原 508）
- 提取 `results/CKI_NC_Cover_Letter_fulltext.txt`
- 拷入 `version3/CKI_Submission_v50_NC/CKI_NC_Cover_Letter.docx`
- 重算 `MANIFEST_v50.txt` 全部 sha256
- 重打包 `version3/CKI_Submission_v50_NC.zip` 与根 `CKI_Submission_v50_NC.zip`（12,894,515 B，原 12,894,522）

## 校验

- 行距 XML：`252/auto` 全段一致 ✓
- LibreOffice 渲染：**1 页** ✓
- 复用构建 cl 断言（V49-C1…C10 + 6 审稿人邮箱 + 3 条编辑断言）**20/20 ALL PASS** ✓
  - 含："Xianming Wu (First Author)" 不在文本、"Li Zhang (Corresponding Author)" 在文本

## 版本与发布决策

- **不切 v0.5.5**：本改为投稿信编辑性改动，非 CKI 包/代码版本；MS/SI/Guide 未动，包版本 v0.5.4 不变
- **Release 资产刷新（已执行）**：新根 zip 重新上传至 GitHub Release 396502805
  - 旧资产 588422612 删除 → 新资产 id **588514653**，size **12,894,515 B**
  - 资产元数据 size 与本地 zip 完全一致（上传为直传本地字节）→ 内容一致强证据
  - 字节级 readback（octet-stream / browser_download_url）在本环境被代理 502 拦截（curl exit 35 TLS、urllib 挂起），与 Zenodo 代理同症，改以 **size 校验兜底**
  - Release body 已追加 cover-letter 编辑注记；commit fe00e73 已推送（ls-remote 一致）

## 遗留可选项

若用户接受 cover letter 破单页以换取更大行距，可改 1.08/1.1/1.15（均 2 页）。当前默认 1.05 单页。
