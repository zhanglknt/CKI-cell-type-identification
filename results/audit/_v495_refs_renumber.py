# v49.5 refs renumber: reorder _refs_nc by first-appearance, remap all in-text
# citation groups, add 2 CELLxGENE citations (new ref 47), fix 3 ref fields,
# bump cite count assertion 73 -> 75. Heavy asserts; prints change log.
import ast, re, io, sys, py_compile

SRC = r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_nc.py"
GRP = re.compile(r"\[(\d+(?:\s*[,\-]\s*\d+)*)\]")  # same as generator _CITE_GROUP_RE

def parse_group(inner):
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

# old -> new mapping (derived from AST-verified first-appearance order with the
# new CELLxGENE citation inserted at the Tabula Sapiens methods paragraph)
M = {}
for n in range(1, 15): M[n] = n
M[15] = 53; M[16] = 51; M[17] = 52
for n in range(18, 49): M[n] = n - 2          # 18..48 -> 16..46
M[49] = 48; M[50] = 49; M[51] = 50
M[52] = 54; M[53] = 55; M[54] = 56
M[55] = 47; M[56] = 15
assert sorted(M.values()) == list(range(1, 57))

# new position -> old ref (refs list permutation, 1-based old indices)
NEW_ORDER = list(range(1, 15)) + [56] + list(range(18, 49)) + [55] + [49, 50, 51] + [16, 17, 15] + [52, 53, 54]
assert len(NEW_ORDER) == 56 and sorted(NEW_ORDER) == list(range(1, 57))

txt = io.open(SRC, encoding="utf-8").read()
orig_txt = txt

# ---------- verified text lines (top-level p()/heading() calls) ----------
tree = ast.parse(txt)
verified = set()
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("p", "heading"):
        for ln in range(node.lineno, (node.end_lineno or node.lineno) + 1):
            verified.add(ln)

def repl_count(s, old, new, expect=1):
    c = s.count(old)
    assert c == expect, f"expected {expect} occurrence(s), got {c}: {old[:70]!r}"
    return s.replace(old, new)

log = []

# ---------- Phase A: field fixes inside ref entries ----------
txt = repl_count(txt,
    "Nature, nurture, or chance: stochastic gene expression variation and its consequences on individual cellular fitness.",
    "Nature, nurture, or chance: stochastic gene expression and its consequences.")
log.append("A1 Raj title fixed (old ref 35 -> new 33)")
txt = repl_count(txt,
    "regulations, and interactions. \u00abi\u00bbBrief. Bioinform.\u00ab/i\u00bb",
    "regulations, and interactions using single-cell RNA sequencing data. \u00abi\u00bbBrief. Bioinform.\u00ab/i\u00bb")
log.append("A2 Jiang CACIMAR title completed (old ref 37 -> new 35)")
txt = repl_count(txt,
    "\u00abb\u00bb184,\u00ab/b\u00bb 3573\u20133587 (2021).",
    "\u00abb\u00bb184,\u00ab/b\u00bb 3573\u20133587.e29 (2021).")
log.append("A3 Hao 2021 pages -> 3573-3587.e29 (old ref 47 -> new 45)")

# ---------- Phase B: reorder _refs_nc ----------
lines = txt.split("\n")
start = next(i for i, l in enumerate(lines) if l.strip() == "_refs_nc = [")
end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "]")
entries = lines[start + 1:end]
assert len(entries) == 56, f"refs entries parsed: {len(entries)}"
for e in entries:
    assert e.startswith("'") and e.rstrip().endswith(","), f"bad entry line: {e[:60]!r}"
new_entries = [entries[old - 1] for old in NEW_ORDER]
lines[start + 1:end] = new_entries
txt = "\n".join(lines)
log.append("B  _refs_nc reordered (56 entries)")
# spot-check new positions
checks = {15: "Liberzon", 16: "W\u00e4lchli", 33: "stochastic gene expression and its consequences.",
          35: "using single-cell RNA sequencing data", 45: "3573\u20133587.e29",
          46: "Dictionary learning", 47: "CELLxGENE", 48: "Weinstein", 49: "Colaprico",
          50: "Cerami", 51: "Perou", 52: "Parker", 53: "Edmondson",
          54: "Waskom", 55: "Pedregosa", 56: "Efron"}
for pos, needle in checks.items():
    assert needle in new_entries[pos - 1], f"new ref {pos} missing {needle!r}: {new_entries[pos-1][:80]!r}"
log.append("B  new-position spot checks PASS (" + ", ".join(map(str, sorted(checks))) + ")")

# ---------- Phase C: remap in-text citation groups on verified lines ----------
lines = txt.split("\n")
cite_changes = []
def cb(m):
    inner = m.group(1)
    nums = parse_group(inner)
    if nums is None:
        return m.group(0)
    mapped = [M[n] for n in nums]
    if mapped == nums:
        return m.group(0)
    assert len(set(mapped)) == len(mapped), f"collision in [{inner}] -> {mapped}"
    ms = sorted(mapped)
    if "-" in inner and "," not in inner:
        assert ms == list(range(ms[0], ms[0] + len(ms))), f"range breaks: [{inner}] -> {ms}"
        newinner = f"{ms[0]}-{ms[-1]}"
    else:
        newinner = ",".join(str(x) for x in ms)
    cite_changes.append((inner, newinner))
    return "[" + newinner + "]"

n_lines_touched = 0
for i, ln in enumerate(lines, 1):
    if i not in verified:
        continue
    new_ln = GRP.sub(cb, ln)
    if new_ln != ln:
        lines[i] = new_ln if False else lines[i]  # placeholder, replaced below
        lines[i - 1] = new_ln
        n_lines_touched += 1
txt = "\n".join(lines)
log.append(f"C  in-text remap: {len(cite_changes)} groups rewritten on {n_lines_touched} lines")
for old, new in cite_changes:
    log.append(f"   [{old}] -> [{new}]")

# ---------- Phase D: insert CELLxGENE citations (new ref 47) ----------
txt = repl_count(txt,
    "accessed via CZ CELLxGENE Discover.",
    "accessed via CZ CELLxGENE Discover [47].")
log.append("D1 [47] added at Tabula Sapiens methods paragraph")
txt = repl_count(txt,
    "from CZ CELLxGENE Discover (collection ID:",
    "from CZ CELLxGENE Discover [47] (collection ID:")
log.append("D2 [47] added at brain atlas methods paragraph")

# ---------- Phase E: cite-count assertion ----------
NL = "\r\n" if "\r\n" in txt else "\n"
txt = repl_count(txt,
    NL.join(["# 73 = 72 legacy groups + 1 new in-text citation of ref [56] (Hallmark",
             "# enrichment sentence in the TCGA Results, added in the v49.1 xv round).",
             "assert _cite_sup_count == 73, f'Expected 73 superscripted citation groups, got {_cite_sup_count}'"]),
    NL.join(["# 75 = 73 groups of v49.4 + 2 new in-text citations of ref 47 (CZ CELLxGENE",
             "# Discover; Methods Tabula Sapiens and brain atlas dataset paragraphs, v49.5).",
             "assert _cite_sup_count == 75, f'Expected 75 superscripted citation groups, got {_cite_sup_count}'"]))
log.append("E  cite count assertion 73 -> 75")

# ---------- write + compile ----------
io.open(SRC, "w", encoding="utf-8", newline="\n").write(txt)
py_compile.compile(SRC, doraise=True)
log.append("F  written + py_compile PASS")

# ---------- Final: AST re-extraction on the NEW source ----------
txt2 = io.open(SRC, encoding="utf-8").read()
tree2 = ast.parse(txt2)
texts2 = []
for node in ast.walk(tree2):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("p", "heading"):
        parts = []
        for a in node.args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                parts.append(a.value)
            elif isinstance(a, ast.JoinedStr):
                for v in a.values:
                    if isinstance(v, ast.Constant) and isinstance(v.value, str):
                        parts.append(v.value)
        if parts:
            texts2.append((node.lineno, "".join(parts)))
groups2 = []
for ln, t in texts2:
    for m in GRP.finditer(t):
        nums = parse_group(m.group(1))
        if nums:
            groups2.append((ln, m.group(0), nums))
seen, fl = [], {}
for ln, raw, nums in groups2:
    for n in nums:
        if n not in fl:
            fl[n] = ln
            seen.append(n)
assert seen == list(range(1, 57)), f"first-appearance NOT monotonic: {seen}"
assert len(groups2) == 75, f"group count {len(groups2)} != 75"
log.append("G  AST re-extract: 75 groups, first-appearance == 1..56 monotonic PASS")

# per-line key expectations
line_groups = {}
for ln, raw, nums in groups2:
    line_groups.setdefault(ln, []).append(raw)
def expect_at(ln, raws):
    got = line_groups.get(ln, [])
    for r in raws:
        assert r in got, f"L{ln}: expected {r}, have {got}"
# locate lines dynamically by content
def find_line(snippet):
    for i, l in enumerate(txt2.split("\n"), 1):
        if snippet in l:
            return i
    raise AssertionError(f"not found: {snippet[:60]!r}")
l_marker = find_line("Three controls bound the interpretation")
expect_at(l_marker, ["[15]"])
l_ts = find_line("Tabula Sapiens v1.0 [9]: accessed via CZ CELLxGENE Discover [47]")
expect_at(l_ts, ["[9]", "[47]"])
l_tcga = find_line("TCGA bulk RNA-seq [48]:")
expect_at(l_tcga, ["[48]", "[49]", "[50]", "[51,52]", "[53]"])
l_brain = find_line("from CZ CELLxGENE Discover [47] (collection ID:")
expect_at(l_brain, ["[12]", "[47]"])
l_env = find_line("seaborn [54]")
expect_at(l_env, ["[44]", "[54]", "[55]"])
l_stat = find_line("Resampling-based inference [56]")
expect_at(l_stat, ["[56]", "[43]"])
l_sev = find_line("BRCA PAM50 subtype calls [51,52]")
expect_at(l_sev, ["[51,52]", "[53]"])
log.append("H  per-line key group expectations PASS")

print("\n".join(log))
print("\nALL RENUMBER STEPS PASS")
