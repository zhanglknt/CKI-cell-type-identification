# v47 phase-2：Zenodo v0.5.0 记录 DOI 写回（2026-09-13）

## 背景
- v47 phase-1 时 MS Availability 引用 v0.4.9 记录 `10.5281/zenodo.22333850`，约定 Zenodo v0.5.0 记录归档后在 phase-2 写回（范本 = v46 phase-2，commit 6760995）。
- Release v0.5.0 于 2026-09-13 14:16 UTC 发布，但 Zenodo webhook 全部投递失败（release created=403，published/released/edited=500 context deadline exceeded），记录未自动归档。
- 处置：GitHub API 重投递 `released` 事件（delivery 3842531815617200128，HTTP 202 OK），Zenodo 约 16:52 UTC 完成归档。

## Zenodo v0.5.0 记录
- 记录 ID：**22735744**；版本 DOI：**10.5281/zenodo.22735744**；概念 DOI 不变 10.5281/zenodo.20405458
- 标题 "zhanglknt/CKI-cell-type-identification: v0.5.0: v47 submission package (first-author revision integration)"，status published，is_last=true，版本 index 11
- 文件 zhanglknt/CKI-cell-type-identification-v0.5.0.zip（65,114,533 B）

## 修改内容（4 文件，v46 phase-2 同构）
1. `generate_manuscript_gb.py`（根 + 镜像）：Availability 行 `version DOI for v0.4.9: 10.5281/zenodo.22333850` → `version DOI for v0.5.0: 10.5281/zenodo.22735744`
2. `99_build_gb_v47.py`（根 + 镜像）：
   - 头注 phase-1 说明 → `phase-2 DONE 2026-09-13`
   - V45-2a 断言 → 检查 `10.5281/zenodo.22735744` in MS
   - V46-i2 窗口串 `22333850` → `22735744`（消息同步）
   - V47-10c → 断言 `version DOI for v0.5.0: 10.5281/zenodo.22735744`；新增 **V47-10c2** 断言旧记录 DOI 已从 MS 消失
   - 尾注 docstring → phase-2 DONE 2026-09-13
   - 保留：L23 v46 历史行（22333850 系 v46 合法记录）
- 编辑方式：python utf-8 字节级（规避 Edit 工具 GBK 往返损坏风险）

## 重建与重打包
- 构建：系统 Python 3.12（PyPDF2 仅装在该环境；default venv 无 PyPDF2——首轮失败原因）→ **665/665 checks ALL PASSED — v47 (GB) FINAL**（较 phase-1 664 新增 V47-10c2）
- finalize 脚本打补丁支持 integrate 模式（新构建裸包 33 条目，无 item 10/checksum/内嵌 repro zip，原脚本仅支持 update 模式）
- 终包：`version3/CKI_Submission_v47.zip` = **65,373,942 B，34 条目**；内嵌 `CKI_Reproducibility_Package.zip` 296 文件（52,570,434 B，sha 796cba6b…）；MANIFEST item 10 + checksum 行（CRLF、2 空格缩进）；WORK_DIR 与主目录副本同步

## Release 资产替换
- Release v0.5.0（id 387922141）旧资产 561336387 删除，新资产 **561604006**（65,373,942 B）上传 33s 完成；readback sha256 = **40264fdd5551b5704ecb743687abeda96523572699530641b7ced4cb291410bb**，与本地一致

## 经验教训
- Zenodo-GitHub webhook 会因 Zenodo 侧超时/403 静默失败——Release 后应查 hook deliveries（`GET /repos/{o}/{r}/hooks/{id}/deliveries`），失败可 `POST .../deliveries/{delivery_id}/attempts` 重投递
- 构建必须用系统 Python 3.12（PyPDF2 依赖）；构建前先把 `results/figures_submission` 与 `version3/CKI_Submission_v47` mv 至 `_tmp_archive/`（safe-delete 钩子 >50 文件拦截，且残留半成品目录会再次触发）
- 兜底一次性自动化（f2966ce0，原定 23:35）已在 phase-2 手动完成后删除，避免重复执行
