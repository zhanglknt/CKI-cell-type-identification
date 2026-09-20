# Scan generate_manuscript_nc.py: extract citation groups in source line order,
# compute first-appearance sequence, simulate the planned remap, flag risky ranges.
import re, io, sys

SRC = r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_nc.py"
txt = io.open(SRC, encoding="utf-8").read()
lines = txt.split("\n")

# Same regex as generator _CITE_GROUP_RE: [n] or [n,m,...] or [n-m] (with optional spaces)
GRP = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")

def parse_group(inner):
    """Return sorted list of ints in group, expanding ranges; None if not a citation group."""
    parts = [p.strip() for p in inner.split(",")]
    nums = []
    for p in parts:
        m = re.match(r"^(\d+)\s*-\s*(\d+)$", p)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            nums.extend(range(a, b + 1))
        elif p.isdigit():
            nums.append(int(p))
        else:
            return None
    if not nums or any(n < 1 or n > 56 for n in nums):
        return None
    return nums

groups = []  # (lineno, raw, nums)
for i, ln in enumerate(lines, 1):
    # skip the refs list block itself (L280-337 region: lines starting with "    '" inside _refs_nc)
    for m in GRP.finditer(ln):
        nums = parse_group(m.group(1))
        if nums is None:
            continue
        groups.append((i, m.group(0), nums))

# Filter out groups inside the _refs_nc literal block (they are reference text, not citations)
# Locate _refs_nc block bounds
start = txt.index("_refs_nc = [")
end = txt.index("]", txt.index("Liberzon", start))
refs_start_line = txt[:start].count("\n") + 1
refs_end_line = txt[:end].count("\n") + 1
groups = [g for g in groups if not (refs_start_line <= g[0] <= refs_end_line)]

# Also drop groups inside helper code (the guard function definition etc.) - keep only lines that look like text
# Heuristic: drop lines containing "def " or "_is_citation" or "re.compile" or "assert" with _CITE
groups = [g for g in groups if "_is_citation" not in lines[g[0]-1] and "def " not in lines[g[0]-1]]

print("total citation groups in text order:", len(groups))

# first-appearance sequence
seen = []
first_line = {}
for ln, raw, nums in groups:
    for n in nums:
        if n not in first_line:
            first_line[n] = ln
            seen.append(n)
print("first-appearance sequence:", seen)
print("missing (orphans):", [n for n in range(1, 57) if n not in first_line])
print("monotonic?", seen == sorted(seen))

# where do key refs first appear
for n in [15, 16, 17, 49, 50, 51, 52, 53, 54, 55, 56]:
    print(f"  ref {n}: first at line {first_line.get(n)}")

# simulate adding [55] at the Tabula Sapiens methods paragraph (find line with 'accessed via CZ CELLxGENE Discover')
anchor = None
for i, ln in enumerate(lines, 1):
    if "accessed via CZ CELLxGENE Discover" in ln:
        anchor = i
        break
print("CELLxGENE anchor line:", anchor)

seq2 = []
fl2 = {}
for ln, raw, nums in groups:
    eff = list(nums)
    if ln == anchor:
        eff = eff + [55]  # appended citation
    for n in eff:
        if n not in fl2:
            fl2[n] = ln
            seq2.append(n)
print("sequence after adding [55] at anchor:", seq2)
print("orphans after add:", [n for n in range(1, 57) if n not in fl2])

# planned remap: old->new
def remap(n):
    if n <= 14: return n
    if n == 15: return 56
    if n == 16: return 54
    if n == 17: return 55
    if 18 <= n <= 54: return n - 2
    if n == 55: return 53
    if n == 56: return 15
    raise ValueError(n)

newseq = [remap(n) for n in seq2]
print("remapped first-appearance sequence:", newseq)
print("remapped monotonic 1..56?", newseq == list(range(1, 57)))

# list ALL groups with mapped output; flag any group whose mapped set is not expressible as same shape
print("\n--- all groups (line: raw -> mapped) ---")
risky = []
for ln, raw, nums in groups:
    eff = list(nums)
    if ln == anchor and raw == groups[[g[0] for g in groups].index(ln)][1] if False else False:
        pass
    mapped = sorted(set(remap(n) for n in nums))
    # recompress mapped into ranges
    def compress(ns):
        out = []
        i = 0
        while i < len(ns):
            j = i
            while j + 1 < len(ns) and ns[j+1] == ns[j] + 1:
                j += 1
            if j > i:
                out.append(f"{ns[i]}-{ns[j]}")
            else:
                out.append(str(ns[i]))
            i = j + 1
        return out
    comp = compress(mapped)
    newraw = "[" + ",".join(comp) + "]"
    # a group is risky if original had a range (dash) and mapped form has different element count of pieces
    had_range = "-" in raw
    pieces_changed = len(comp) != (len(raw.split(",")) )
    flag = ""
    if had_range and ("-" in raw and (len(comp) > 1 or (comp and "-" not in comp[0] and len(nums) > 1))):
        # check if original range stayed a single range
        orig_single_range = re.match(r"^\[\d+\s*-\s*\d+\]$", raw)
        if orig_single_range and not (len(comp) == 1 and "-" in comp[0]):
            flag = "  <<< RANGE BREAKS"
            risky.append((ln, raw, newraw))
    print(f"L{ln}: {raw} -> {newraw}{flag}")

print("\nrisky range groups:", len(risky))
for ln, raw, newraw in risky:
    print(f"  L{ln}: {raw} -> {newraw}")
