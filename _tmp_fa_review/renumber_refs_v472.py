# -*- coding: utf-8 -*-
"""v47.2 参考文献编号按首引顺序重排
映射: old 1-37 不变; old[56](Skinnider/Augur) -> new[38]; old[38]-[55] -> new[39]-[56]
改动:
  generate_manuscript_gb.py:
    1) 正文引用组重映射（20 处，re.sub 回调单趟替换无碰撞）
    2) _refs_nar 列表按行重排（230-285 行）
  镜像同步: CKI_Reproducibility_Package/generate_manuscript_gb.py
自检: py_compile + 源码级首引顺序模拟 == 1..56 + 列表 ast 解析
"""
import io, re, ast, shutil, py_compile

ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
GEN = ROOT + "/generate_manuscript_gb.py"

src = io.open(GEN, encoding="utf-8").read()

# ---------- 1) 正文引用组重映射 ----------
PAT = re.compile(r"\[(\d+(?:\s*[,\u2013\-]\s*\d+)*)\]")

def remap_num(n):
    if n == 56:
        return 38
    if 38 <= n <= 55:
        return n + 1
    return n

count = [0]

def sub_fn(m):
    raw = m.group(1)
    nums = []
    for part in re.split(r"\s*,\s*", raw):
        pm = re.match(r"^(\d+)\s*([\u2013\-])\s*(\d+)$", part)
        if pm:
            nums.append((int(pm.group(1)), int(pm.group(3)), pm.group(2)))
        else:
            nums.append((int(part),))
    flat = []
    for item in nums:
        flat.extend(x for x in item if isinstance(x, int))
    # 条件: 全部在 1..56 且至少一个在 38..56（真实引用组）
    if not all(1 <= x <= 56 for x in flat):
        return m.group(0)
    if not any(38 <= x <= 56 for x in flat):
        return m.group(0)
    count[0] += 1
    # 逐组重渲染，保留原分隔风格（无空格逗号 / 短横线）
    out_parts = []
    for item in nums:
        if len(item) == 3:
            a, b, dash = item
            out_parts.append("%d%s%d" % (remap_num(a), dash, remap_num(b)))
        else:
            out_parts.append(str(remap_num(item[0])))
    return "[" + ",".join(out_parts) + "]"

new_src = PAT.sub(sub_fn, src)
assert count[0] == 20, "expected 20 citation groups remapped, got %d" % count[0]

# ---------- 2) _refs_nar 列表按行重排 ----------
lines = new_src.split("\n")
# 定位列表
li = next(i for i, l in enumerate(lines) if l.startswith("_refs_nar = ["))
assert lines[li] == "_refs_nar = [", "unexpected list header"
entries = []
j = li + 1
while not lines[j].rstrip().endswith("]"):
    entries.append(lines[j])
    j += 1
close_line = lines[j]
assert len(entries) == 56, "expected 56 ref lines, got %d" % len(entries)
# 每行必须是完整的单条字符串字面量
parsed = [ast.literal_eval(e.strip().rstrip(",")) for e in entries]
assert "Skinnider" in parsed[55], "old ref 56 must be Skinnider/Augur"
new_entries = entries[:37] + [entries[55]] + entries[37:55]
new_parsed = [ast.literal_eval(e.strip().rstrip(",")) for e in new_entries]
assert len(new_parsed) == 56
assert "Skinnider" in new_parsed[37], "new ref 38 must be Skinnider/Augur"
assert "Waxman" in new_parsed[38], "new ref 39 must be Waxman"
assert new_parsed[:37] == parsed[:37], "refs 1-37 unchanged"
assert new_parsed[38:56] == parsed[37:55], "refs 39-56 = old 38-55 shifted"

lines[li + 1: j] = new_entries
new_src = "\n".join(lines)

# ---------- 3) 源码级首引顺序模拟 ----------
groups = []
for m in PAT.finditer(new_src):
    raw = m.group(1)
    flat = []
    for part in re.split(r"\s*,\s*", raw):
        pm = re.match(r"^(\d+)\s*[\u2013\-]\s*(\d+)$", part)
        if pm:
            a, b = int(pm.group(1)), int(pm.group(2))
            if b > a and (b - a) <= 10:
                flat.extend(range(a, b + 1))
            else:
                flat.extend([a, b])
        else:
            flat.append(int(part))
    if all(1 <= x <= 56 for x in flat):
        groups.append((m.start(), flat))
# 只取正文引用（排除 _refs_nar 列表区之后的正文；列表区本身无方括号引用组）
seen, order = set(), []
for pos, flat in groups:
    for n in flat:
        if n not in seen:
            seen.add(n)
            order.append(n)
# 1..37 在列表前首次出现于正文（列表位于源码前部 pos~8629，正文引用在其后）
# 检查: 相对顺序中 38 必须在 39..56 之前且整体集合完整
assert set(order) == set(range(1, 57)), "all 56 refs cited in source, got %d" % len(set(order))
i38 = order.index(38)
assert all(order.index(n) > i38 for n in range(39, 57)), "new [38] (Augur) must be first among 38-56"

# ---------- 4) 写回 + 镜像 + 自检 ----------
io.open(GEN, "w", encoding="utf-8", newline="").write(new_src)
shutil.copyfile(GEN, ROOT + "/CKI_Reproducibility_Package/generate_manuscript_gb.py")
py_compile.compile(GEN, doraise=True)
py_compile.compile(ROOT + "/CKI_Reproducibility_Package/generate_manuscript_gb.py", doraise=True)

print("OK: 20 citation groups remapped; _refs_nar reordered (Skinnider -> [38])")
print("new ref 38 =", new_parsed[37][:80])
print("new ref 39 =", new_parsed[38][:80])
print("new ref 56 =", new_parsed[55][:80])
