# -*- coding: utf-8 -*-
"""nc60 A7/A11 scan: locate SI table caption call sites, docx save point, and table block boundaries."""
import re

src = open('notebooks/68_gen_supplementary_nc.py', encoding='utf-8').read()
lines = src.splitlines()

for m in re.finditer(r'[^\n]*\.save\([^\n]*', src):
    print('SAVE::', m.group(0)[:120])

pat1 = re.compile(r"\s*si_caption\(\s*'(Supplementary Table (\d+)\.)")
pat2 = re.compile(r"\s*f?'(Supplementary Table (\d+)\.)")
for i, l in enumerate(lines, 1):
    m = pat1.match(l) or pat2.match(l)
    if m:
        print('CAPTION L%d Table %s :: %s' % (i, m.group(2), l.strip()[:90]))

# heading map for structure
for i, l in enumerate(lines, 1):
    if 'add_heading(' in l:
        print('HEAD L%d :: %s' % (i, l.strip()[:110]))
