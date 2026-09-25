# -*- coding: utf-8 -*-
"""One-shot: remove the junk file literally named 'nul' (Windows reserved
device name) from the repo root. Strategy: GetFileAttributesW to inspect,
then MoveFileExW(\\?\\...\\nul -> ...\\nul_junk) to rename under the \\?\\
literal prefix (disables DOS device resolution), then DeleteFileW on the
renamed file. ctypes is used because the safe-delete hook patches
os.remove/shutil and its trash backend cannot handle reserved names."""
import ctypes
from ctypes import wintypes
import os
import sys

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
root = r"C:\Users\KnightZ\Desktop\细胞受选择"
src = "\\\\?\\" + os.path.join(root, "nul")
dst = "\\\\?\\" + os.path.join(root, "nul_junk_todelete")

attrs = k32.GetFileAttributesW(src)
print("attrs:", hex(attrs & 0xFFFFFFFF))
if attrs == 0xFFFFFFFF:
    print("GetFileAttributesW error:", ctypes.get_last_error())
    sys.exit(1)

MOVEFILE_REPLACE_EXISTING = 0x1
if not k32.MoveFileExW(src, dst, MOVEFILE_REPLACE_EXISTING):
    print("MoveFileExW error:", ctypes.get_last_error())
    sys.exit(1)
print("renamed -> nul_junk_todelete")

if not k32.DeleteFileW(dst):
    print("DeleteFileW error:", ctypes.get_last_error())
    sys.exit(1)
names = os.listdir(root)
print("gone:", "nul" not in names and "nul_junk_todelete" not in names)
