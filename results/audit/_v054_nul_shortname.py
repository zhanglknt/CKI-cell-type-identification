#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Get the 8.3 alias of root\\nul and try DeleteFileW via that alias
(device names like 'nul' are not recognized when the final component
carries an 8.3 alias such as 'NUL~1')."""
import ctypes
from ctypes import wintypes

k32 = ctypes.WinDLL("kernel32", use_last_error=True)

DIR = "C:\\Users\\KnightZ\\Desktop\\细胞受选择"
LONG = DIR + "\\nul"
UNC = "\\\\?\\" + LONG


class WIN32_FIND_DATAW(ctypes.Structure):
    _fields_ = [("dwFileAttributes", wintypes.DWORD),
                ("ftCreationTime", wintypes.FILETIME),
                ("ftLastAccessTime", wintypes.FILETIME),
                ("ftLastWriteTime", wintypes.FILETIME),
                ("nFileSizeHigh", wintypes.DWORD),
                ("nFileSizeLow", wintypes.DWORD),
                ("dwReserved0", wintypes.DWORD),
                ("dwReserved1", wintypes.DWORD),
                ("cFileName", wintypes.WCHAR * 260),
                ("cAlternateFileName", wintypes.WCHAR * 14)]


fd = WIN32_FIND_DATAW()
h = k32.FindFirstFileW(UNC, ctypes.byref(fd))
if h == -1:
    print("FindFirstFileW error", ctypes.get_last_error())
    raise SystemExit(1)
print("long:", repr(fd.cFileName), "| 8.3 alias:", repr(fd.cAlternateFileName))
k32.FindClose(h)

alias = fd.cAlternateFileName
candidates = []
if alias:
    candidates.append(DIR + "\\" + alias)          # plain path, alias final component
    candidates.append("\\\\?\\" + DIR + "\\" + alias)
candidates.append(UNC)                              # fallback: long UNC again

import os
for p in candidates:
    if not os.path.exists("\\\\?\\" + DIR + "\\nul"):
        break
    ok = k32.DeleteFileW(p)
    print(f"DeleteFileW({p!r}) -> {'OK' if ok else 'error %d' % ctypes.get_last_error()}")

print("still present:", os.path.exists("\\\\?\\" + DIR + "\\nul"))
