# v49.8: sync verify suites + build assertions with classification-benchmark cut.
import io, sys

# ---------- 1) _nc49_ms_verify.py : replace 11b block (lines 216-231) ----------
P = r'C:\Users\KnightZ\Desktop\细胞受选择\results\audit\_nc49_ms_verify.py'
lines = io.open(P, encoding='utf-8').read().split('\n')
assert lines[215].startswith('# 11b. v49.7'), f'anchor 11b: {lines[215]!r}'
assert "Table 1 classification disclosure retained" in lines[229], f'anchor tail: {lines[229]!r}'
new_block = [
    '# 11b. v49.7: Fig 2e = change-detection ROC',
    "chk('Fig 2 legend new scope',",
    "    'functional-change detection in the ground-truth simulation' in full)",
    "chk('Fig 2e legend change-detection ROC',",
    "    'ROC curves for discriminating injected functional signal' in full",
    "    and 'AUC = 0.80' in full and 'AUC = 0.91 (rank 1/6)' in full)",
    "chk('Fig 2e legend old classification ROC gone',",
    "    'ROC curves for cell-type classification across five metrics on Tabula Sapiens data' not in full)",
    "chk('Result 3 anchor narrowed to Fig. 2d',",
    "    'human column) (Fig. 2d).' in full and 'human column) (Fig. 2d, e).' not in full)",
    "chk('Result 3b AUC sentence cites Fig. 2e',",
    "    'from neutral perturbations (Fig. 2e; AUC = 0.80' in full)",
    "chk('Result 3b background2 cites Fig. 2e',",
    "    '= 0.859 (Fig. 2e), with the same metric ranking' in full)",
    '',
    '# 11c. v49.8: classification benchmark fully cut; main Table 2 renumbered to Table 1',
    "chk('classification benchmark paragraph removed',",
    "    'cell-type classification performance' not in full",
    "    and 'ranked 5th of 5 methods' not in full and '0.680' not in full)",
    "chk('Fig 2 legend Table 1 pointer removed',",
    "    'Cell-type classification performance on Tabula Sapiens is reported in Table 1' not in full)",
    "chk('Methods classification ROC-AUC removed',",
    "    'cell-type classification ROC-AUC' not in full)",
    "chk('main-text Table 2 retired',",
    "    not re.search(r'(?<!Supplementary )Table 2', full))",
    "chk('cross-organ Table 1 citations',",
    "    '(Fig. 5; Table 1; Supplementary Fig. 5)' in full",
    "    and 'upper block of Table 1' in full and 'lower block of Table 1' in full)",
]
lines = lines[:215] + new_block + lines[231:]
io.open(P, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
rb = io.open(P, encoding='utf-8').read()
assert '11c. v49.8' in rb and 'classification disclosure retained' not in rb
print('OK  ms_verify 11b/11c block')

# ---------- 2) _nc49_cl_guide_verify.py : line 18 ----------
P2 = r'C:\Users\KnightZ\Desktop\细胞受选择\results\audit\_nc49_cl_guide_verify.py'
s = io.open(P2, encoding='utf-8').read()
old = "chk('CL specificity-first AUC 0.680', 'specificity-first index' in clfull and '(0.680)' in clfull)"
new = ("chk('CL change-detection framing (no classification AUC)',\n"
       "    'specificity-first index' in clfull and '0.680' not in clfull\n"
       "    and 'dynamic cell-state changes' in clfull)")
assert s.count(old) == 1, 'CL verify anchor'
s = s.replace(old, new)
io.open(P2, 'w', encoding='utf-8', newline='').write(s)
print('OK  cl_guide_verify CL assertion')

# ---------- 3) 99_build_nc_v49.py ----------
P3 = r'C:\Users\KnightZ\Desktop\细胞受选择\99_build_nc_v49.py'
b = io.open(P3, encoding='utf-8').read()
old3 = '    check("0.680" in cl, "V49-C5 CL cites AUC 0.680 (by-design admission)")'
new3 = ('    check("0.680" not in cl and "dynamic cell-state changes" in cl,\n'
        '          "V49-C5 CL change-detection framing (no classification AUC)")')
assert b.count(old3) == 1, 'build C5 anchor'
b = b.replace(old3, new3)

lines = b.split('\n')
# insert N35-N37 right after the N26 check (line idx of N26 second line)
idx = next(i for i, t in enumerate(lines) if 'V49-N26 KIRC' in t)
ins = [
    '    _main_xlsx = _lwb(str(BASE / "results" / "CKI_Tables_NC.xlsx"))',
    '    check(_main_xlsx.sheetnames == [\'Table 1\']',
    '          and str(_main_xlsx[\'Table 1\'][\'A1\'].value).startswith(\'Table 1. Cross-organ conservation\'),',
    '          "V49-N35 main Tables xlsx = single Table 1 sheet (cross-organ)")',
    "    check('cell-type classification performance' not in ms and '0.680' not in ms",
    "          and 'ranked 5th of 5 methods' not in ms,",
    '          "V49-N36 classification benchmark cut from MS")',
    "    check('(Fig. 5; Table 1; Supplementary Fig. 5)' in ms and 'upper block of Table 1' in ms",
    "          and not re.search(r'(?<!Supplementary )Table 2', ms),",
    '          "V49-N37 main Table 2 renumbered to Table 1")',
]
lines = lines[:idx + 1] + ins + lines[idx + 1:]
io.open(P3, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
rb3 = io.open(P3, encoding='utf-8').read()
assert 'V49-N35' in rb3 and 'V49-N36' in rb3 and 'V49-N37' in rb3 and 'V49-C5 CL change-detection' in rb3
print('OK  build C5 flip + N35/N36/N37 inserted')
print('ALL VERIFY/BUILD SYNCS PASS')
