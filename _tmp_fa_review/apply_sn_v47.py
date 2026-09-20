# -*- coding: utf-8 -*-
"""Apply v47 cross-reference renumbering + Table S3/S4 clarification to
notebooks/68_gen_supplementary_en.py. Raw strings keep \\uXXXX literal."""
import io, sys

PATH = r'C:/Users/KnightZ/Desktop/细胞受选择/notebooks/68_gen_supplementary_en.py'
src = io.open(PATH, encoding='utf-8', newline='').read()

E = []

# SN cross-reference renumbering (old -> new after deleting old S3)
E.append(('N1  Figure S11 -> S10 (omega dist)',
 r"(Figure S11: \u03c9 distribution ",
 r"(Figure S10: \u03c9 distribution "))
E.append(('N2  Figure S9 -> S8 (block-shuffle null)',
 r"characterization; Figure S9: block-shuffle null distribution",
 r"characterization; Figure S8: block-shuffle null distribution"))
E.append(('N3  Figure S12 -> S11 (JS dimensionality)',
 r"consistency. (Figure S12.)",
 r"consistency. (Figure S11.)"))
E.append(('N4  Figure S7 -> S6 (pair-specific kn)',
 r"choice in mind. (Figure S7.)",
 r"choice in mind. (Figure S6.)"))
E.append(('N5  Fig. S13 -> S12 (Kang)',
 r"'(Fig. S13). '",
 r"'(Fig. S12). '"))
E.append(('N6  Fig. S14 -> S13 (QQ)',
 r"Additional file 1: Fig. S14.'",
 r"Additional file 1: Fig. S13.'"))

# Q2: Table S3/S4 same-source clarification (CRLF line endings)
CRLF = '\r\n'
E.append(('N7  Table S3/S4 same-source note',
 "    f'Complete candidate dataset: results/brain_bs_null_observed_pairs.csv '" + CRLF +
 "    f'({n_candidates:,} threshold-passing rows of 31,764 total). '",
 "    f'Complete candidate dataset: results/brain_bs_null_observed_pairs.csv '" + CRLF +
 "    f'({n_candidates:,} threshold-passing rows of 31,764 total). '" + CRLF +
 "    f'Tables S3 and S4 share the same underlying data file ' " + CRLF +
 "    f'(results/brain_bs_null_observed_pairs.csv): Table S3 reports all 31,764 pairs ' " + CRLF +
 "    f'with per-cell-type summary statistics, whereas Table S4 retains the ' " + CRLF +
 "    f'{n_candidates:,} threshold-passing rows with their tier, residual, and ' " + CRLF +
 "    f'\\u03c9 annotations. '"))

fails = []
for tag, old, new in E:
    n = src.count(old)
    if n != 1:
        fails.append((tag, n)); continue
    src = src.replace(old, new)

if fails:
    print('FAILED (tag, occurrences):')
    for t, n in fails: print(f'  {t} -> {n}')
    sys.exit(1)

io.open(PATH, 'w', encoding='utf-8', newline='').write(src)
print(f'OK: {len(E)} replacements applied to 68_gen_supplementary_en.py')
