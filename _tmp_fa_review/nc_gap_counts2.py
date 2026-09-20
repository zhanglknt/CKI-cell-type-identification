# -*- coding: utf-8 -*-
import re, traceback
try:
    lines = open(r'C:\Users\KnightZ\Desktop\细胞受选择\version3\CKI_Submission_v47\CKI_Manuscript_fulltext.txt', encoding='utf-8').read().splitlines()
    out = open(r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\nc_gap_counts2_out.txt', 'w', encoding='utf-8')
    W = out.write
    for i, l in enumerate(lines, 1):
        m = re.match(r'^Figure (\d)\.', l)
        if m:
            W('Fig %s legend words: %d\n' % (m.group(1), len(l.split())))
    refs = [l for l in lines if re.match(r'^\d+\. ', l)]
    W('total refs matched: %d\n' % len(refs))
    full5 = []; sixplus = []; etal = 0
    for r in refs:
        no = r.split('.')[0]
        body = r[len(no) + 2:]
        if ' et al' in body:
            etal += 1
            auseg = body.split(' et al')[0]
            if auseg.count(',') + 1 < 6:
                W('  ! et al. but listed authors <6, check ref %s\n' % no)
        else:
            auseg = body.split('. ')[0]
            n = auseg.count(',') + 1
            if n <= 5:
                full5.append(no)
            else:
                sixplus.append((no, n))
    W('et al. refs: %d\n' % etal)
    W('no et al., <=5 authors (must list all; already complete): %s\n' % full5)
    W('no et al., >=6 authors (NC: truncate to first + et al.): %s\n' % sixplus)
    out.flush(); out.close()
except Exception:
    err = open(r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\nc_gap_counts2_err.txt', 'w', encoding='utf-8')
    err.write(traceback.format_exc()); err.close()
