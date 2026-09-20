# xv491: dump wrapped full text of MS lines 51,123 and SI 3.13 section
from pathlib import Path

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")

def dump(label, text, width=1400):
    print(f"##### {label} (len={len(text)}) #####")
    for i in range(0, len(text), width):
        print(f"[{label} chunk {i//width}]")
        print(text[i:i+width])
    print()

ms = (ROOT / "results/CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8").split("\n")
dump("MS51", ms[50])
dump("MS123", ms[122])

si = (ROOT / "results/CKI_Supplementary_NC_fulltext.txt").read_text(encoding="utf-8").split("\n")
# find start of 3.13 and start of next section 3.14
s = next(i for i, ln in enumerate(si) if ln.strip().startswith("3.13 "))
e = next((i for i in range(s + 1, len(si)) if si[i].strip().startswith("3.14 ")), min(s + 60, len(si)))
for i in range(s, e):
    dump(f"SI{i+1}", si[i])
