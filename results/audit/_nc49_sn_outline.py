# -*- coding: utf-8 -*-
p = r"C:/Users/KnightZ/Desktop/细胞受选择/notebooks/68_gen_supplementary_nc.py"
src = open(p, encoding="utf-8").read()
lines = src.splitlines()
print("lines:", len(lines))
out = []
for i, l in enumerate(lines, 1):
    if (l.startswith("def ") or l.startswith("class ") or l.startswith("# ")
            or ("Note" in l and ("add" in l or "section" in l.lower() or "heading" in l.lower()))
            or ("Section" in l and "Supplementary" in l)):
        out.append(f"{i}: {l[:130]}")
open(r"C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_sn_outline.txt",
     "w", encoding="utf-8").write("\n".join(out))
