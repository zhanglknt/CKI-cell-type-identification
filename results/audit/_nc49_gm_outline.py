# -*- coding: utf-8 -*-
p = r"C:/Users/KnightZ/Desktop/细胞受选择/generate_manuscript_nc.py"
src = open(p, encoding="utf-8").read()
lines = src.splitlines()
print("lines:", len(lines), "chars:", len(src))
out = []
for i, l in enumerate(lines, 1):
    if (l.startswith("def ") or l.startswith("class ") or l.startswith("# ")
            or ("add_heading" in l and any(
                k in l for k in ["Results", "Methods", "Discussion",
                                 "Figure", "Data", "Reference"]))):
        out.append(f"{i}: {l[:130]}")
open(r"C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_nc49_gm_outline.txt",
     "w", encoding="utf-8").write("\n".join(out))
