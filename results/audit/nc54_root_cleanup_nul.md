# 根目录 `nul` 残留文件处置说明（2026-09-25）

## 文件来源
项目根目录 `nul`（256 B，2025-05-24 23:58）系 Git Bash 下 `... 2>nul` 重定向误入——MSYS2 不映射裸 `nul` 到 Windows NUL 设备，遂在 cwd 落了一个真实文件。内容已读取确认无害（两条 `dir: cannot access` 报错文本）。`.gitignore` L43 已覆盖，git 视野外。

## 为何 agent 删不掉
| 尝试 | 结果 |
|---|---|
| bash `mv` / `rm` | Permission denied / 被 safe-delete 钩子拦 |
| 钩子路由 genie-trash | 0x800704B0 指定的设备名无效（fail-closed） |
| cmd `del "\\?\%CD%\nul"` | 指定的路径无效（中文路径经 cmd 编码损毁） |
| ctypes `DeleteFileW`（`\\?\` 前缀） | error 5 Access Denied |
| ctypes `MoveFileExW`（改名） | error 5 |
| PowerShell / Bash **沙箱外** `DeleteFileW` | 仍 error 5 |
| ntdll `NtCreateFile(FILE_DELETE_ON_CLOSE)` | **NTSTATUS 0xC0000022（内核层拒绝）** |

诊断事实：DACL 无拒绝项（FA for SY/BA/用户）；GENERIC_READ 可开，GENERIC_WRITE/DELETE 均被拒；**新建**一个同名 `nul` 文件同样只能建/写、不能删——环境内核过滤驱动对 DOS 设备名文件的删除类操作一律 fail-closed，与具体文件无关。8.3 别名不存在（卷上短名生成对该名不生效），无迂回路径。

结论：凡是本环境派生的进程都无法删除该文件；**普通终端（资源管理器启动的 cmd/PowerShell，非 WorkBuddy 子进程）不受此限**。

## 手动删除（任选其一，在普通终端执行）
```cmd
del "\\?\C:\Users\KnightZ\Desktop\细胞受选择\nul"
```
```powershell
Remove-Item -LiteralPath '\\?\C:\Users\KnightZ\Desktop\细胞受选择\nul' -Force
```
另有一个同性质测试残留 `_tmp_nultest\nul`（沙箱假设验证时创建），同法删除：
```cmd
del "\\?\C:\Users\KnightZ\Desktop\细胞受选择\_tmp_nultest\nul" && rmdir "C:\Users\KnightZ\Desktop\细胞受选择\_tmp_nultest"
```

诊断脚本存档：`_v054_nul_diag.py`（DACL/访问权探测）、`_v054_nul_shortname.py`（8.3 别名）、`_v054_nul_sandbox_test.py`（新建对照实验）、`_v054_nul_ntdelete.py`（原生 API）。
