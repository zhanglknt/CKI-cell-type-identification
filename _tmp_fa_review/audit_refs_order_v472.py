# -*- coding: utf-8 -*-
"""v47.2 参考文献编号顺序审计：
1) 严格模式全量 dump 引用组（pos + 内容）
2) 首引序列 vs 递增判定
3) 输出重编号映射所需的所有区间引用组（含 - 或 , 的组）
"""
import re, io, sys

FULL = r"version3/CKI_Submission_v47/CKI_Manuscript_fulltext.txt"
with io.open(FULL, "r", encoding="utf-8") as f:
    t = f.read()

# 严格模式：只匹配纯数字/逗号/短横线/En-dash 组
PAT = re.compile(r"\[(\d+(?:\s*[,\u2013\-]\s*\d+)*)\]")

groups = [(m.start(), m.group(1)) for m in PAT.finditer(t)]
print("total citation-like groups:", len(groups))

first_seen = {}  # refnum -> first pos
expanded_all = []  # (pos, raw, [nums])
for pos, raw in groups:
    # 展开区间与列表
    nums = []
    for part in re.split(r"\s*,\s*", raw):
        pm = re.match(r"^(\d+)\s*[\u2013\-]\s*(\d+)$", part)
        if pm:
            a, b = int(pm.group(1)), int(pm.group(2))
            if b > a and (b - a) <= 60:
                nums.extend(range(a, b + 1))
            else:
                nums.append(a); nums.append(b)
        else:
            nums.append(int(part))
    expanded_all.append((pos, raw, nums))
    for n in nums:
        if n not in first_seen:
            first_seen[n] = pos

order = sorted(first_seen.items(), key=lambda kv: kv[1])
seq = [n for n, _ in order]
print("\n首次引用顺序:", seq)

ok = True
for i in range(1, len(seq)):
    if seq[i] < seq[i - 1]:
        ok = False
        print("乱序点: [%d]@%d 在 [%d]@%d 之后" % (seq[i], first_seen[seq[i]], seq[i-1], first_seen[seq[i-1]]))
print("递增判定:", "PASS" if ok else "FAIL")

print("\n--- 每个引用编号的首引位置 ---")
for n, pos in order:
    print("ref %2d first@%d  ctx: %s" % (n, pos, t[max(0,pos-60):pos+10].replace("\n", " ")[-70:]))

print("\n--- 含区间/多值的引用组（重编号需展开重写）---")
for pos, raw, nums in expanded_all:
    if "," in raw or "\u2013" in raw or "-" in raw:
        print("pos %6d  [%s]  nums=%s" % (pos, raw, nums))

# [56] 上下文
print("\n--- [56] 全部出现 ---")
for pos, raw, nums in expanded_all:
    if 56 in nums:
        print("pos %d: %s" % (pos, t[max(0,pos-120):pos+120].replace("\n", " ")))
