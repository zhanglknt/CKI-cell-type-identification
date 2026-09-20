# -*- coding: utf-8 -*-
import io
import re
from pathlib import Path

out = io.StringIO()
lines = Path(r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_gb.py").read_text(encoding="utf-8").splitlines()
for ln in (414, 462, 479, 485, 506, 522):
    out.write(f"--- L{ln} ---\n")
    out.write(lines[ln - 1] + "\n")

out.write("\n=== heading lengths >60 ===\n")
src = "\n".join(lines)
for m in re.finditer(r"heading\('([^']+)', level=(\d)\)", src):
    t, lv = m.group(1), m.group(2)
    if len(t) > 60:
        out.write(f"len={len(t)} L{lv}: {t}\n")

out.write("\n=== dangling xref candidates ===\n")
for pat in [r"Limitations", r"Practical usage", r"When to use CKI", r"usage guide",
            r"see Discussion", r"\(Discussion", r"Discussion\)", r"Conclusions\b",
            r"List of abbreviations", r"abbreviations\)", r"Background\)",
            r"Microglia: composition", r"thalamo-temporal", r"sparse candidates"]:
    for i, l in enumerate(lines):
        if re.search(pat, l):
            out.write(f"L{i+1} [{pat}]: {l.strip()[:300]}\n")

Path(r"C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\recon2_out.txt").write_text(out.getvalue(), encoding="utf-8")
print("done")
