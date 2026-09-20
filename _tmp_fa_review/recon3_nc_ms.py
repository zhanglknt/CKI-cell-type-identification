# -*- coding: utf-8 -*-
import io
import re
from pathlib import Path

out = io.StringIO()
src = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_gb.py").read_text(encoding="utf-8")

for pat in [r"Limitations", r"usage guide", r"When to use", r"Conclusions", r"abbreviations",
            r"Declarations", r"Additional files", r"Ethics", r"Consent",
            r"Ground-truth simulation dissociates", r"rankings robust",
            r"apparent tumor homogeneity", r"divergence gradients",
            r"hypothesis-generating screen", r"Background"]:
    out.write(f"\n=== {pat} ===\n")
    for m in re.finditer(pat, src):
        # skip heading lines themselves
        line_start = src.rfind("\n", 0, m.start()) + 1
        line = src[line_start:src.find("\n", m.start())]
        if line.strip().startswith("heading(") or line.strip().startswith("#"):
            continue
        s = max(0, m.start() - 140)
        e = min(len(src), m.end() + 140)
        out.write(f"  ...{src[s:e]}...\n")

Path(r"C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\recon3_out.txt").write_text(out.getvalue(), encoding="utf-8")
print("done")
