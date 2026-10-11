# nc72: renumber supplementary figures to strict first-citation order.
# Mapping old->new (audit _nc72_order_audit.py, MS first-appearance [1,9,2,3,6,4,8,5,7]):
#   1->1, 9->2, 2->3, 3->4, 6->5, 4->6, 8->7, 5->8, 7->9
# Handles: MS / SI / Guide text refs (regex single pass, no collision),
#          Guide shipped-filename mention Supplementary_Fig_3.pdf -> _4.pdf,
#          SI legend block reorder (add_para('Supplementary Fig. N. ...') sorted ascending).
# NOT idempotent: run exactly once (git checkout to roll back).
import re, ast, sys

MAP = {1: 1, 9: 2, 2: 3, 3: 4, 6: 5, 4: 6, 8: 7, 5: 8, 7: 9}
FILES = [
    "generate_manuscript_nc.py",
    "notebooks/68_gen_supplementary_nc.py",
    "notebooks/100_gen_reproducibility_nc.js",
]

pat = re.compile(r"Supplementary (Figs?)\. (\d+)")

def sub_file(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    counts = {}
    def repl(m):
        old = int(m.group(2))
        counts[old] = counts.get(old, 0) + 1
        return f"Supplementary {m.group(1)}. {MAP[old]}"
    out = pat.sub(repl, src)
    if path.endswith(".js"):
        n_fn = out.count("Supplementary_Fig_3.pdf")
        out = out.replace("Supplementary_Fig_3.pdf", "Supplementary_Fig_4.pdf")
        counts["filename _3.pdf"] = n_fn
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"{path}: refs per old-number {dict(sorted(counts.items(), key=lambda kv: str(kv[0])))}, total {sum(v for k, v in counts.items() if isinstance(k, int))}")
    return out

for p in FILES:
    sub_file(p)

# ---- SI legend reorder: sort add_para('Supplementary Fig. N. ...') blocks ascending ----
si = "notebooks/68_gen_supplementary_nc.py"
with open(si, encoding="utf-8") as f:
    lines = f.readlines()
head_idx = [i for i, ln in enumerate(lines)
            if re.match(r"^add_para\('Supplementary Fig\. \d+\. ", ln)]
assert len(head_idx) == 9, f"expected 9 legend paragraphs, found {len(head_idx)}"
start, end = head_idx[0], head_idx[-1]
# blocks: each legend line followed by exactly one blank line
blocks = []
for i in head_idx:
    blk = [lines[i]]
    j = i + 1
    while j < len(lines) and lines[j].strip() == "" and j <= end + 1:
        blk.append(lines[j])
        j += 1
        break
    num = int(re.match(r"^add_para\('Supplementary Fig\. (\d+)\. ", lines[i]).group(1))
    blocks.append((num, blk))
nums = [n for n, _ in blocks]
assert sorted(nums) == list(range(1, 10)), f"legend numbers not 1..9 after renumber: {nums}"
prefix = lines[:start]
suffix = lines[head_idx[-1] + 1:]
# strip the trailing blank lines that belonged to blocks from suffix handling:
# blocks consumed their own trailing blank line; suffix starts right after last legend line.
if suffix and suffix[0].strip() == "":
    suffix = suffix[1:]  # last block's blank line already included
blocks.sort(key=lambda x: x[0])
new_mid = []
for n, blk in blocks:
    new_mid.extend(blk)
out_lines = prefix + new_mid + suffix
with open(si, "w", encoding="utf-8") as f:
    f.writelines(out_lines)
print(f"SI legend order now: {[n for n, _ in blocks]}")

# ---- integrity: AST parse both python files + tail check ----
for p in ["generate_manuscript_nc.py", si]:
    src = open(p, encoding="utf-8").read()
    ast.parse(src)
    tail = src.rstrip().splitlines()[-1]
    print(f"{p}: AST OK, tail = {tail[:80]!r}")
js = open("notebooks/100_gen_reproducibility_nc.js", encoding="utf-8").read()
assert js.rstrip().endswith("});") or "main()" in js[-200:], "JS tail looks truncated"
print("JS tail OK")
print("DONE nc72 renumber")
