# -*- coding: utf-8 -*-
import subprocess
out = subprocess.run(
    ["C:/Windows/System32/tasklist.exe", "/FI", "IMAGENAME eq python.exe",
     "/FO", "CSV"], capture_output=True, text=True).stdout
open(r"C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_procs.txt",
     "w", encoding="utf-8").write(out)
