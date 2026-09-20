# xv491: dump full MS lines 51/123 and SI section 3.13
from pathlib import Path

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")

ms = (ROOT / "results/CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8").split("\n")
print("##### MS line 51 (full) #####")
print(ms[50])
print()
print("##### MS line 123 (full) #####")
print(ms[122])
print()

si = (ROOT / "results/CKI_Supplementary_NC_fulltext.txt").read_text(encoding="utf-8").split("\n")
# locate 3.13 section
start = None
for i, ln in enumerate(si):
    if "3.13" in ln and ("purit" in ln.lower() or "admix" in ln.lower() or "smok" in ln.lower() or "tcga" in ln.lower()):
        print(f"[SI line {i+1}] {ln[:200]}")
