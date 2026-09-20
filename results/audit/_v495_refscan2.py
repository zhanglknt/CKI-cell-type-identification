# AST-based: extract citation groups from p()/heading() string literals in emission order.
# Then extract from built DOCX (superscript runs) and compare first-appearance sequences.
import ast, re, io, sys

SRC = r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_nc.py"
DOCX = r"C:\Users\KnightZ\Desktop\细胞受选择\results\CKI_Manuscript_NC.docx"

GRP = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")

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

src = io.open(SRC, encoding="utf-8").read()
tree = ast.parse(src)

texts = []  # (lineno, text) in source order for top-level statements
class V(ast.NodeVisitor):
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ("p", "heading"):
            parts = []
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    parts.append(a.value)
                elif isinstance(a, ast.JoinedStr):
                    for v in a.values:
                        if isinstance(v, ast.Constant) and isinstance(v.value, str):
                            parts.append(v.value)
                        # FormattedValue = code, skipped
            if parts:
                texts.append((node.lineno, "".join(parts)))
        self.generic_visit(node)

# Only top-level module body emission order
for stmt in tree.body:
    V().visit(stmt)

groups = []
for ln, t in texts:
    for m in GRP.finditer(t):
        nums = parse_group(m.group(1))
        if nums:
            groups.append((ln, m.group(0), nums))

def firstseq(groups, extra=None):
    seen, fl = [], {}
    for ln, raw, nums in groups:
        eff = list(nums)
        if extra and ln == extra[0]:
            eff = eff + [extra[1]]
        for n in eff:
            if n not in fl:
                fl[n] = ln
                seen.append(n)
    return seen, fl

seen, fl = firstseq(groups)
print("AST source-order group count:", len(groups))
print("AST first-appearance seq:", seen)
print("orphans:", [n for n in range(1, 57) if n not in fl])
for n in [15, 16, 17, 49, 50, 51, 52, 53, 54, 55, 56]:
    print(f"  ref {n}: first at line {fl.get(n)}")

# --- DOCX extraction ---
from docx import Document
doc = Document(DOCX)
def iter_paras(doc):
    for p in doc.paragraphs:
        yield p
dseq, dfl = [], {}
dcount = 0
in_refs = False
for p in iter_paras(doc):
    st = (p.style.name or "")
    if st.startswith("Heading") and p.text.strip().startswith("References"):
        in_refs = True
    if in_refs:
        continue
    # collect superscript runs
    sup = []
    for r in p.runs:
        if r.font.superscript:
            sup.append(r.text)
    if not sup:
        continue
    s = "".join(sup)
    # the generator formats groups like "1,2" or "1-3" possibly with brackets stripped
    for m in GRP.finditer(s):
        nums = parse_group(m.group(1))
        if nums:
            dcount += 1
            for n in nums:
                if n not in dfl:
                    dfl[n] = p.text[:60]
                    dseq.append(n)
print("\nDOCX superscript group count:", dcount)
print("DOCX first-appearance seq:", dseq)
print("DOCX orphans:", [n for n in range(1, 57) if n not in dfl])
for n in [15, 16, 17, 49, 50, 51, 52, 53, 54, 55, 56]:
    print(f"  ref {n}: first in para: {repr(dfl.get(n))}")
