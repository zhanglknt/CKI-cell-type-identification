# -*- coding: utf-8 -*-
"""Renumber GB citations by first appearance in GB document order.

GB moves Methods after Conclusions, so the NAR reference numbering (assigned
by first appearance in the NAR layout) is no longer monotonic in the GB
layout.  This script:

  1. computes the true first-appearance order of references 1..49 from the
     string literals of generate_manuscript_gb.py in file order (file order
     == document order for this generator: sequential p() calls);
  2. cross-checks that order against the docx fulltext produced by the
     previous build (version3/CKI_Submission_v39/CKI_Manuscript_fulltext.txt),
     skipping the '[12-25]' omega-cap range which is NOT a citation;
  3. builds an old->new permutation, rewrites every citation group
     ('[n]', '[n,m]', '[a-b]') inside STRING and FSTRING_MIDDLE tokens only
     (code such as list indexing is never touched);
  4. reorders the _refs_nar list accordingly;
  5. verifies the result parses and that the new first-appearance order is
     exactly 1..49 monotonic.

Idempotent: run on an already-renumbered file, the map is the identity.
Pipeline: _make_gb_generator.py -> this script -> run generator -> build.
"""
import ast, io, re, sys, tokenize

PATH = 'generate_manuscript_gb.py'
FULLTEXT = 'version3/CKI_Submission_v39/CKI_Manuscript_fulltext.txt'

GROUP = re.compile(r'\[(\d{1,2}(?:\s*,\s*\d{1,2}|\s*-\s*\d{1,2})*)\]')

def parse_group(m):
    """Return the list of reference numbers a bracket group denotes, or None
    if it is not a citation (value guard 1..49; decimals never match)."""
    inner = m.group(1)
    parts = re.split(r'\s*,\s*|\s*-\s*', inner)
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if not nums or not all(1 <= n <= 49 for n in nums):
        return None
    if '-' in inner and len(nums) == 2:
        return list(range(nums[0], nums[1] + 1))
    return nums

src = open(PATH, encoding='utf-8').read()
tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))

# ---- 1. first-appearance order from string literals in file order ----
FSTRING_MIDDLE = getattr(tokenize, 'FSTRING_MIDDLE', -1)
lit_parts, lit_tokidx = [], []
for i, tok in enumerate(tokens):
    if tok.type == tokenize.STRING or tok.type == FSTRING_MIDDLE:
        lit_parts.append(tok.string)
        lit_tokidx.append(i)

first, seen = [], set()
for part in lit_parts:
    for m in GROUP.finditer(part):
        vals = parse_group(m)
        if not vals:
            continue
        for n in vals:
            if n not in seen:
                seen.add(n)
                first.append(n)

# ---- 2. cross-check against previous build's fulltext ----
# Only meaningful when the on-disk fulltext is still in the OLD numbering
# (i.e. not yet monotonic).  A monotonic fulltext comes from a previous
# renumbered build and corresponds to this script's OUTPUT, not its input.
try:
    ft = open(FULLTEXT, encoding='utf-8').read()
    ft_first, ft_seen = [], set()
    for m in GROUP.finditer(ft):
        if m.group(0) == '[12-25]':   # omega-cap grid, not a citation
            continue
        vals = parse_group(m)
        if not vals:
            continue
        for n in vals:
            if n not in ft_seen:
                ft_seen.add(n)
                ft_first.append(n)
    if ft_first == list(range(1, 50)):
        print('previous fulltext already renumbered; skipping order cross-check')
    elif ft_first != first:
        print('FATAL: literal order and fulltext order disagree')
        print(' literal :', first)
        print(' fulltext:', ft_first)
        sys.exit(1)
    else:
        print('cross-check vs previous fulltext: identical order OK')
except FileNotFoundError:
    print('no previous fulltext found; skipping cross-check')

if sorted(first) != list(range(1, 50)):
    sys.exit(f'FATAL: first-order does not cover 1..49: {sorted(first)}')

if first == list(range(1, 50)):
    print('already monotonic 1..49: identity map, nothing to do')
    sys.exit(0)

MAP = {old: i + 1 for i, old in enumerate(first)}
print('old->new map (changed only):')
for old in range(1, 50):
    if MAP[old] != old:
        print(f'  {old} -> {MAP[old]}')

# ---- 3. rewrite citation groups inside string literals ----
def remap_group(m):
    vals = parse_group(m)
    if not vals:
        return m.group(0)
    new = sorted(MAP[v] for v in vals)
    parts, i = [], 0
    while i < len(new):
        j = i
        while j + 1 < len(new) and new[j + 1] == new[j] + 1:
            j += 1
        if j - i >= 2:                       # runs of 3+ stay ranges
            parts.append(f'{new[i]}-{new[j]}')
        else:                                # singles/pairs stay comma lists
            parts.extend(str(x) for x in new[i:j + 1])
        i = j + 1
    return '[' + ','.join(parts) + ']'

# collect line-start offsets for (row, col) -> absolute offset
line_starts = [0]
for line in src.splitlines(keepends=True):
    line_starts.append(line_starts[-1] + len(line))

def span(tok):
    r, c = tok.start
    a = line_starts[r - 1] + c
    r2, c2 = tok.end
    b = line_starts[r2 - 1] + c2
    return a, b

edits = []
n_changed = 0
for i in lit_tokidx:
    tok = tokens[i]
    new_text = GROUP.sub(remap_group, tok.string)
    if new_text != tok.string:
        a, b = span(tok)
        edits.append((a, b, new_text))
        n_changed += 1

out = src
for a, b, t in sorted(edits, reverse=True):
    out = out[:a] + t + out[b:]
print(f'rewrote {n_changed} string literal token(s)')

# ---- 4. reorder _refs_nar ----
tree = ast.parse(out)
assign = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == '_refs_nar' for t in node.targets):
        assign = node
        break
if assign is None:
    sys.exit('FATAL: _refs_nar assignment not found')
refs = [ast.literal_eval(e) for e in assign.value.elts]
if len(refs) != 49:
    sys.exit(f'FATAL: _refs_nar has {len(refs)} entries, expected 49')
new_refs = [None] * 49
for old in range(1, 50):
    new_refs[MAP[old] - 1] = refs[old - 1]
assert all(r is not None for r in new_refs)

a = line_starts[assign.lineno - 1] + assign.col_offset
r2, c2 = assign.end_lineno, assign.end_col_offset
b = line_starts[r2 - 1] + c2
lit = ',\n'.join(repr(s) for s in new_refs)
out = out[:a] + '_refs_nar = [\n' + lit + ',\n]' + out[b:]
print('reordered _refs_nar to new numbering')

# ---- 5. verify ----
ast.parse(out)   # syntax check
toks2 = [t for t in tokenize.generate_tokens(io.StringIO(out).readline)
         if t.type == tokenize.STRING or t.type == FSTRING_MIDDLE]
first2, seen2 = [], set()
for tok in toks2:
    for m in GROUP.finditer(tok.string):
        vals = parse_group(m)
        if not vals:
            continue
        for n in vals:
            if n not in seen2:
                seen2.add(n)
                first2.append(n)
if first2 != list(range(1, 50)):
    sys.exit(f'FATAL: post-renumber first-order is not 1..49: {first2}')

open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('verified: first-appearance order now exactly 1..49 monotonic')
print(f'written -> {PATH}')
