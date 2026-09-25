#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sandbox hypothesis test: create a NEW file literally named 'nul'
in a scratch subdir via \\\\?\\ prefix, write to it, then delete it.
If creation/write/delete of a fresh 'nul' also fails, the environment
name-filters device-name files; if it succeeds, the root 'nul' file
itself carries some external protection."""
import ctypes
import os
from ctypes import wintypes

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
BASE = "C:\\Users\\KnightZ\\Desktop\\细胞受选择"
SCRATCH = BASE + "\\_tmp_nultest"
os.makedirs(SCRATCH, exist_ok=True)

TARGET = "\\\\?\\" + SCRATCH + "\\nul"
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
CREATE_ALWAYS = 2

h = k32.CreateFileW(TARGET, GENERIC_READ | GENERIC_WRITE, 0, None,
                    CREATE_ALWAYS, 0x80, None)
if h == -1:
    print("create fresh 'nul': FAIL error", ctypes.get_last_error())
else:
    written = wintypes.DWORD(0)
    k32.WriteFile(h, b"x", 1, ctypes.byref(written), None)
    k32.CloseHandle(h)
    print("create+write fresh 'nul': OK")

ok = k32.DeleteFileW(TARGET)
print("delete fresh 'nul':", "OK" if ok else "error %d" % ctypes.get_last_error())

# cleanup scratch dir (rmdir works on normal dirs)
try:
    os.rmdir(SCRATCH)
    print("scratch dir removed")
except OSError as e:
    print("scratch dir kept:", e)
