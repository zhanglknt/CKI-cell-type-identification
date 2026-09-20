# xv495: extract references + citation order from MS
from pathlib import Path
import re, json

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
text = (ROOT / "results/CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
lines = text.split("\n")

# locate References section
ref_start = None
for i, ln in enumerate(lines):
    if ln.strip().lower() in ("references", "reference list") or re.match(r"^#{0,3}\s*references\s*$", ln.strip(), re.I):
        ref_start = i
        break
print("ref_start line:", ref_start + 1 if ref_start is not None else None)

# references are lines like "1. Regev, A. et al. ..." (possibly wrapped)
ref_text = "\n".join(lines[ref_start + 1:])
# split on ^N. at line starts
parts = re.split(r"(?m)^(\d+)\.\s+", ref_text)
# parts: [pre, num, body, num, body, ...]
refs = []
for i in range(1, len(parts) - 1, 2):
    num = int(parts[i])
    body = " ".join(parts[i + 1].split())  # unwrap
    refs.append((num, body))
print("n refs:", len(refs))
for num, body in refs:
    print(f"[{num}] {body}")

# citation order in main text (before References)
body_text = "\n".join(lines[:ref_start])
# remove figure legends? keep all; citations [n] or [n,m] or [n-m]
cites = []
for m in re.finditer(r"\[([0-9,\s\-–]+)\]", body_text):
    grp = m.group(1)
    for piece in grp.split(","):
        piece = piece.strip()
        if not piece:
            continue
        if "-" in piece or "–" in piece:
            a, b = re.split(r"[-–]", piece)
            cites.extend(range(int(a), int(b) + 1))
        else:
            cites.append(int(piece))
first_seen = []
seen = set()
for c in cites:
    if c not in seen:
        seen.add(c)
        first_seen.append(c)
print("\ntotal citation instances:", len(cites))
print("unique cited:", len(seen))
print("first-seen sequence:", first_seen)
mono = all(first_seen[i] < first_seen[i + 1] for i in range(len(first_seen) - 1))
print("monotone increasing:", mono)
if not mono:
    for i in range(len(first_seen) - 1):
        if first_seen[i] >= first_seen[i + 1]:
            print("  break:", first_seen[i], "->", first_seen[i + 1], "at position", i + 1)
print("orphans (in list, never cited):", sorted(set(range(1, len(refs) + 1)) - seen))
print("cited but not in list:", sorted(c for c in seen if c > len(refs)))
