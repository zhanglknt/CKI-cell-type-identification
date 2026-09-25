#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnose why root\\nul (Windows reserved-name junk file) refuses
delete/rename with error 5: probe CreateFileW access rights and dump
the file's DACL as SDDL."""
import ctypes
from ctypes import wintypes

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
adv = ctypes.WinDLL("advapi32", use_last_error=True)

PATH = "\\\\?\\C:\\Users\\KnightZ\\Desktop\\细胞受选择\\nul"

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
DELETE = 0x00010000
OPEN_EXISTING = 3

for label, access in [("GENERIC_READ", GENERIC_READ),
                      ("GENERIC_WRITE", GENERIC_WRITE),
                      ("DELETE", DELETE),
                      ("GENERIC_READ|GENERIC_WRITE", GENERIC_READ | GENERIC_WRITE)]:
    h = k32.CreateFileW(PATH, access, 7, None, OPEN_EXISTING, 0x80, None)
    if h == -1:
        print(f"{label}: FAIL error {ctypes.get_last_error()}")
    else:
        print(f"{label}: OK (handle {h})")
        k32.CloseHandle(h)

# dump DACL as SDDL
SDDL_REVISION_1 = 1
DACL_SECURITY_INFORMATION = 0x00000004
psd = wintypes.LPVOID()
rc = adv.GetNamedSecurityInfoW(PATH, 1, DACL_SECURITY_INFORMATION,
                               None, None, None, None, ctypes.byref(psd))
if rc != 0:
    print(f"GetNamedSecurityInfoW: error {rc}")
else:
    sddl = wintypes.LPWSTR()
    ok = adv.ConvertSecurityDescriptorToStringSecurityDescriptorW(
        psd, SDDL_REVISION_1, DACL_SECURITY_INFORMATION,
        ctypes.byref(sddl), None)
    if ok:
        print("DACL SDDL:", sddl.value)
        k32.LocalFree(sddl)
    else:
        print("ConvertSDToString: error", ctypes.get_last_error())
    k32.LocalFree(psd)
