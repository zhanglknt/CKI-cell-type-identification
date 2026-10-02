# _nc59_renumber.py — nc59: supplementary tables + Supplementary Notes renumbered
# by first-citation order (user directive 2026-10-02; plan: nc59_numbering_naming_plan_2026-10-02.md)
#
# Mappings (old -> new), derived from EXPANDED first-citation order in the built v0.5.5 MS:
#   Notes first-citation (expanded 'Notes 2-4', 'Notes 1, 5' groups):
#     [1@para13, 2/3/4@para26, 9@para30, 5@para32, 16@para39, 6/7@para41, 8@para45,
#      10@para52, 12@para54, 11@para59, 13@para63, 14@para70, 15@para84]
#   Tables first-citation: [1@para21, 5@para45, 14@para45, 2@para49, 3@para51, 4@para61],
#     SI-only tables 6-13, 15-19 keep relative order.
# Ranges 'Notes 1-16' / 'Tables 1-19' (span-all) are protected before renumbering.
import re

NOTE_MAP = {1: 1, 2: 2, 3: 3, 4: 4, 9: 5, 5: 6, 16: 7, 6: 8,
            7: 9, 8: 10, 10: 11, 12: 12, 11: 13, 13: 14, 14: 15, 15: 16}
TAB_MAP = {1: 1, 5: 2, 14: 3, 2: 4, 3: 5, 4: 6, 6: 7, 7: 8, 8: 9, 9: 10,
           10: 11, 11: 12, 12: 13, 13: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19}


def renumber_text(text, label):
    """Two-pass placeholder renumbering of 'Supplementary Note(s) N' and
    'Supplementary Table(s) N' citations. Span-all ranges protected first;
    grouped citations ('Notes 1, 5', 'Tables 11-17', 'Tables 12 and 13')
    mapped number-by-number BEFORE single-number passes and shell-protected.
    Returns (new_text, stats)."""
    stats = {'note': 0, 'tab': 0, 'combo': 0, 'range_n': 0, 'range_t': 0}
    # --- protect span-all ranges (both literal-escape and real en-dash forms) ---
    for old, ph in [(r'Supplementary Notes 1\u201316', '@@RANGEN_LIT@@'),
                    ('Supplementary Notes 1\u201316', '@@RANGEN_CHR@@'),
                    (r'Supplementary Tables 1\u201319', '@@RANGET_LIT@@'),
                    ('Supplementary Tables 1\u201319', '@@RANGET_CHR@@')]:
        n = text.count(old)
        if n:
            stats['range_n' if 'Note' in old else 'range_t'] += n
            text = text.replace(old, ph)

    # --- grouped citations first (every number inside is mapped) ---
    combo_pat = re.compile(
        r'Supplementary (Notes?|Tables?) ((?:\d+\s*(?:,|and|\\u2013|\u2013|-)\s*)+\d+)')

    def _rep_combo(m):
        mapping = NOTE_MAP if m.group(1).startswith('Note') else TAB_MAP
        # tokenize on separators so digits inside a literal '&#92;u2013' escape
        # are NOT treated as citation numbers
        tokens = re.split(r'(\\u2013|\u2013|,|and|-)', m.group(2))
        out = []
        for tok in tokens:
            t = tok.strip()
            out.append(tok.replace(t, str(mapping[int(t)])) if t.isdigit() else tok)
        stats['combo'] += 1
        return f'Supplementary {m.group(1)} @@C@@{"".join(out)}@@C@@'

    text = combo_pat.sub(_rep_combo, text)

    def _rep_note(m):
        stats['note'] += 1
        return f'Supplementary Note{m.group(1)} @@{NOTE_MAP[int(m.group(2))]}@@'

    def _rep_tab(m):
        stats['tab'] += 1
        return f'Supplementary Table{m.group(1)} @@{TAB_MAP[int(m.group(2))]}@@'

    text = re.sub(r'Supplementary Note(s?) (\d+)', _rep_note, text)
    text = re.sub(r'Supplementary Table(s?) (\d+)', _rep_tab, text)
    text = re.sub(r'@@(\d+)@@', r'\1', text)
    text = text.replace('@@C@@', '')  # strip group shells
    if stats['combo']:
        print(f'[{label}] grouped citations mapped: {stats["combo"]}')
    # --- restore ranges in their original form ---
    text = text.replace('@@RANGEN_LIT@@', r'Supplementary Notes 1\u201316')
    text = text.replace('@@RANGEN_CHR@@', 'Supplementary Notes 1\u201316')
    text = text.replace('@@RANGET_LIT@@', r'Supplementary Tables 1\u201319')
    text = text.replace('@@RANGET_CHR@@', 'Supplementary Tables 1\u201319')
    print(f'[{label}] notes renumbered: {stats["note"]}, tables: {stats["tab"]}, '
          f'ranges protected: notes={stats["range_n"]} tables={stats["range_t"]}')
    return text, stats


def reorder_si_generator(path):
    """68_gen_supplementary_nc.py structural edits (AFTER citation renumbering):
    1) TOC list (Supplementary Note titles) sorted by new number
    2) Note section blocks physically reordered by new number
    3) 'Tables S3 and S4' legacy fix -> 'Tables 5 and 6'
    4) '(sheet Table N)' pointers -> new numbers
    5) write_si_tables_xlsx: sheet order + A1 titles by new number
    """
    src = open(path, encoding='utf-8').read()

    # ---- (3) legacy S-style leftovers in the Table-4 caption text ----
    assert 'Tables S3 and S4 share the same underlying data file' in src
    src = src.replace('Tables S3 and S4 share the same underlying data file',
                      'Tables 5 and 6 share the same underlying data file')
    print('[si] legacy "Tables S3 and S4" -> "Tables 5 and 6"')

    # ---- (4) xlsx sheet pointers in table-description blocks ----
    def _rep_sheet(m):
        return f'(sheet Table {TAB_MAP[int(m.group(1))]})'
    src, n_sheet = re.subn(r'\(sheet Table (\d+)\)', _rep_sheet, src)
    print(f'[si] sheet pointers renumbered: {n_sheet}')
    assert n_sheet == 4, f'expected 4 sheet pointers, got {n_sheet}'

    # ---- (1) TOC list reorder (positional substitution, keeps list slot layout) ----
    # entries look like:    'Supplementary Note N: Title...',
    # section headings (add_heading('...', 2)) do not match the ^\s*'...' anchor.
    toc_pat = re.compile(r"^(\s*)'Supplementary Note (\d+): (.+)',$", re.M)
    toc_entries = [(m.group(1), int(m.group(2)), m.group(3))
                   for m in toc_pat.finditer(src)]
    assert len(toc_entries) == 16, f'TOC entries != 16 ({len(toc_entries)})'
    toc_iter = iter(sorted(toc_entries, key=lambda e: e[1]))

    def _toc_sub(_m):
        ind, num, title = next(toc_iter)
        return f"{ind}'Supplementary Note {num}: {title}',"

    src = toc_pat.sub(_toc_sub, src)
    print('[si] TOC reordered by new note number')

    # ---- (2) section-block physical reorder ----
    lines = src.splitlines(keepends=True)
    head_idx = []  # (new_no, line_index)
    for i, ln in enumerate(lines):
        m = re.match(r"add_heading\('Supplementary Note (\d+): ", ln)
        if m:
            head_idx.append((int(m.group(1)), i))
    assert len(head_idx) == 16, f'section headings != 16 ({len(head_idx)})'
    # region ends at the '# ===== Supplementary Methods' comment line
    end_idx = next(i for i, ln in enumerate(lines)
                   if ln.startswith('# ===== Supplementary Methods'))
    blocks = {}
    for k, (num, i0) in enumerate(head_idx):
        i1 = head_idx[k + 1][1] if k + 1 < len(head_idx) else end_idx
        blocks[num] = lines[i0:i1]
    new_order = sorted(blocks)  # new numbers 1..16
    assert new_order == list(range(1, 17))
    merged = [ln for num in new_order for ln in blocks[num]]
    lines = lines[:head_idx[0][1]] + merged + lines[end_idx:]
    src = ''.join(lines)
    print(f'[si] 16 note blocks reordered: new sequence <- old '
          f'{[1, 2, 3, 4, 9, 5, 16, 6, 7, 8, 10, 12, 11, 13, 14, 15]}')

    # ---- (5) xlsx writer: sheet order + titles by new number ----
    old_writer = """    wb = Workbook()
    wb.remove(wb.active)
    for _i, (_df, _cap) in enumerate(_early):
        _n = _i + 1
        ws = wb.create_sheet(f'Table {_n}')
        ws['A1'] = f'Supplementary Table {_n}: {_cap}'
        ws['A1'].font = Font(bold=True)
        ws.append([])
        ws.append(list(_df.columns))
        for _c in ws[3]:
            _c.font = Font(bold=True)
        for _row in _df.itertuples(index=False):
            ws.append([None if pd.isna(_v) else _v for _v in _row])
        ws.column_dimensions['A'].width = 28
    for _i, (_rows, _cap) in enumerate(zip(_SI_TABLE_ROWS, _SI_TABLE_CAPS)):
        _n = _i + 5
        ws = wb.create_sheet(f'Table {_n}')
        ws['A1'] = f'Supplementary Table {_n}: {_cap}'
        ws['A1'].font = Font(bold=True)
        ws.append([])
        for _ri, _row in enumerate(_rows):
            ws.append(list(_row))
            if _ri == 0:
                for _c in ws[3]:
                    _c.font = Font(bold=True)
        ws.column_dimensions['A'].width = 28
"""
    new_writer = """    wb = Workbook()
    wb.remove(wb.active)
    # nc59: sheet order follows first-citation order in the main text
    # (old -> new): 1->1, 5->2, 14->3, 2->4, 3->5, 4->6, 6-13->7-14, 15-19->15-19
    _plan = [
        ('df', _early[0][0], _early[0][1]),            # old 1  -> new 1
        ('rows', _SI_TABLE_ROWS[0], _SI_TABLE_CAPS[0]),  # old 5  -> new 2
        ('rows', _SI_TABLE_ROWS[9], _SI_TABLE_CAPS[9]),  # old 14 -> new 3
        ('df', _early[1][0], _early[1][1]),            # old 2  -> new 4
        ('df', _early[2][0], _early[2][1]),            # old 3  -> new 5
        ('df', _early[3][0], _early[3][1]),            # old 4  -> new 6
    ]
    for _k in range(1, 9):                             # old 6-13 -> new 7-14
        _plan.append(('rows', _SI_TABLE_ROWS[_k], _SI_TABLE_CAPS[_k]))
    for _k in range(10, 15):                           # old 15-19 -> new 15-19
        _plan.append(('rows', _SI_TABLE_ROWS[_k], _SI_TABLE_CAPS[_k]))
    assert len(_plan) == 19
    for _n, (_kind, _payload, _cap) in enumerate(_plan, start=1):
        ws = wb.create_sheet(f'Table {_n}')
        ws['A1'] = f'Supplementary Table {_n}: {_cap}'
        ws['A1'].font = Font(bold=True)
        ws.append([])
        if _kind == 'df':
            ws.append(list(_payload.columns))
            for _c in ws[3]:
                _c.font = Font(bold=True)
            for _row in _payload.itertuples(index=False):
                ws.append([None if pd.isna(_v) else _v for _v in _row])
        else:
            for _ri, _row in enumerate(_payload):
                ws.append(list(_row))
                if _ri == 0:
                    for _c in ws[3]:
                        _c.font = Font(bold=True)
        ws.column_dimensions['A'].width = 28
"""
    assert old_writer in src, 'xlsx writer block not found verbatim'
    src = src.replace(old_writer, new_writer)
    print('[si] xlsx writer reordered (19 sheets by new number)')

    open(path, 'w', encoding='utf-8', newline='').write(src)
    return src


SI_COMMENT_FIXES = [
    # header docstring: stale count, would be mangled by the combo pass
    ('NC naming: Supplementary Note 1-15, Supplementary Fig., Supplementary Table.',
     'NC naming: Supplementary Note, Supplementary Fig., Supplementary Table (no S prefix).'),
    # v49.5 migration comment: old table span no longer literal after nc59
    ('# (Supplementary Tables 5-19, one sheet per table, in document order). The docx',
     '# (15 sheets, one per table; nc59: sheet order = first-citation order). The docx'),
    ('# ===== v49.5: export the 15 migrated tables as Supplementary Tables 5-19 =====',
     '# ===== v49.5: export the 15 migrated tables (nc59: reordered by first citation) ====='),
]


def main():
    # ---------- Phase 1: citation renumbering in the three text generators ----------
    for path, label in [
        ('generate_manuscript_nc.py', 'ms'),
        ('notebooks/68_gen_supplementary_nc.py', 'si'),
        ('notebooks/100_gen_reproducibility_nc.js', 'guide'),
    ]:
        src = open(path, encoding='utf-8').read()
        if label == 'si':
            for old_c, new_c in SI_COMMENT_FIXES:
                assert old_c in src, f'comment anchor missing: {old_c[:50]}'
                src = src.replace(old_c, new_c)
            print('[si] 3 comment lines neutralized')
        new_src, _ = renumber_text(src, label)
        open(path, 'w', encoding='utf-8', newline='').write(new_src)

    # ---------- Phase 2: SI generator structural edits ----------
    reorder_si_generator('notebooks/68_gen_supplementary_nc.py')
    print('DONE')


if __name__ == '__main__':
    main()
