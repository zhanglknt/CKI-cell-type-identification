# -*- coding: utf-8 -*-
"""nc60 A11: move the 14 supplementary figure legends from the manuscript
generator to the SI generator (new 'Supplementary Figures' section)."""
import re

MS = 'generate_manuscript_nc.py'
SI = 'notebooks/68_gen_supplementary_nc.py'

ms = open(MS, encoding='utf-8').read()

start_marker = "# ============================================================\n# Supplementary figure legends"
start = ms.find(start_marker)
assert start > 0, 'legend block header not found'

# block end = the '# == Save ==' marker that follows the Fig. 14 legend
end_marker = '# == Save =='
end = ms.find(end_marker, start)
assert end > 0, 'save marker not found'

block = ms[start:end]

# collect the 14 legend calls: single-line or multi-line p('Supplementary Fig. N. ...')
calls = []
for m in re.finditer(r"p\(f?'Supplementary Fig\. \d+\.", block):
    s = m.start()
    one = block.find("')\n", s)
    multi = block.find('\n)\n', s)
    if one != -1 and (multi == -1 or one < multi):
        e = one + 3
    elif multi != -1:
        e = multi + 3
    else:
        raise AssertionError('no call end at %d' % s)
    calls.append(block[s:e].strip())
assert len(calls) == 14, len(calls)

# 1) remove from MS
ms_new = ms[:start].rstrip('\n') + '\n\n\n' + ms[end:]
open(MS, 'w', encoding='utf-8', newline='').write(ms_new)
print('MS: removed', end - start, 'chars; legends:', len(calls))

# 2) build SI section
si_lines = [
    '# ===== Supplementary Figures (legends migrated from the main text, nc60) =====',
    "add_heading('Supplementary Figures', 2)",
    "add_para('Legends for Supplementary Figs. 1-14. Figure files are provided "
    "separately (results/ figures listed in the Reproducibility Guide).')",
    '',
]
for c in calls:
    assert c.startswith("p('") or c.startswith("p(f'"), c[:30]
    inner = c[2:]  # drop 'p'
    si_lines.append('add_para(' + inner)
    si_lines.append('')
si_section = '\n'.join(si_lines) + '\n\n'

si = open(SI, encoding='utf-8').read()
anchor = '# ===== Add line numbers (continuous, every line) ====='
k = si.find(anchor)
assert k > 0, 'line-numbers anchor not found'
si_new = si[:k] + si_section + si[k:]
open(SI, 'w', encoding='utf-8', newline='').write(si_new)
print('SI: inserted', len(si_section), 'chars before line-numbers block')

# sanity: MS no longer contains supplementary figure legends
assert 'Supplementary Fig. 1.' not in ms_new
print('OK')
