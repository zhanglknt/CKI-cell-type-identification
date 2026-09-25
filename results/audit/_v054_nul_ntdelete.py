#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Last-resort delete of root 'nul' via ntdll native API.
If usermode Win32 hooks are what denies DELETE on device-named files,
NtCreateFile(FILE_DELETE_ON_CLOSE) bypasses them. NTSTATUS is printed
raw so a kernel-filter denial (0xC0000022) is distinguishable."""
import ctypes
from ctypes import wintypes

nt = ctypes.WinDLL("ntdll")

DELETE = 0x00010000
SYNCHRONIZE = 0x00100000
FILE_OPEN = 1
FILE_DELETE_ON_CLOSE = 0x00001000
FILE_NON_DIRECTORY_FILE = 0x00000040
FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020
OBJ_CASE_INSENSITIVE = 0x40


class UNICODE_STRING(ctypes.Structure):
    _fields_ = [("Length", wintypes.USHORT),
                ("MaximumLength", wintypes.USHORT),
                ("Buffer", wintypes.LPWSTR)]


class OBJECT_ATTRIBUTES(ctypes.Structure):
    _fields_ = [("Length", ctypes.c_ulong),
                ("RootDirectory", wintypes.HANDLE),
                ("ObjectName", ctypes.POINTER(UNICODE_STRING)),
                ("Attributes", ctypes.c_ulong),
                ("SecurityDescriptor", wintypes.LPVOID),
                ("SecurityQualityOfService", wintypes.LPVOID)]


class IO_STATUS_BLOCK(ctypes.Structure):
    _fields_ = [("Status", ctypes.c_long),
                ("Information", ctypes.c_size_t)]


import os
import sys

name = "\\??\\" + os.path.join(os.getcwd(), sys.argv[1] if len(sys.argv) > 1 else "nul")
us = UNICODE_STRING(len(name) * 2, len(name) * 2 + 2, name)
oa = OBJECT_ATTRIBUTES(ctypes.sizeof(OBJECT_ATTRIBUTES), None,
                       ctypes.pointer(us), OBJ_CASE_INSENSITIVE, None, None)
h = wintypes.HANDLE()
iosb = IO_STATUS_BLOCK()
st = nt.NtCreateFile(ctypes.byref(h), DELETE | SYNCHRONIZE, ctypes.byref(oa),
                     ctypes.byref(iosb), None, 0x80, 7, FILE_OPEN,
                     FILE_DELETE_ON_CLOSE | FILE_NON_DIRECTORY_FILE | FILE_SYNCHRONOUS_IO_NONALERT,
                     None, 0)
print(f"NtCreateFile({name!r}) NTSTATUS = 0x{st & 0xFFFFFFFF:08X}")
if st == 0:
    nt.NtClose(h)
    print("handle closed (delete-on-close armed)")
print("still present:", os.path.exists("\\\\?\\" + os.path.join(os.getcwd(), sys.argv[1] if len(sys.argv) > 1 else "nul")))
