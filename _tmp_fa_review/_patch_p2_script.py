import io
p = r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\phase2_v47_zenodo.py'
t = io.open(p, encoding='utf-8').read()
old6 = ('    ("Package released as tag v0.5.0. MS Availability phase-1 cites the\'\\n"\n'
        '     "\'v0.4.9 Zenodo record (10.5281/zenodo.22333850); the v0.5.0\'\\n"\n'
        '     "\'record DOI is written in phase-2 after the release.\'",\n'
        '     "Package released as tag v0.5.0. MS Availability phase-2 cites the\'\\n"\n'
        '     "\'v0.5.0 Zenodo record (10.5281/zenodo.22735744). Phase-2 DONE\'\\n"\n'
        '     "\'2026-09-13.\'",')
new6 = ('    ("Package released as tag v0.5.0. MS Availability phase-1 cites the\\n"\n'
        '     "v0.4.9 Zenodo record (10.5281/zenodo.22333850); the v0.5.0\\n"\n'
        '     "record DOI is written in phase-2 after the release.",\n'
        '     "Package released as tag v0.5.0. MS Availability phase-2 cites the\\n"\n'
        '     "v0.5.0 Zenodo record (10.5281/zenodo.22735744). Phase-2 DONE\\n"\n'
        '     "2026-09-13.",')
n = t.count(old6)
print('pair6 anchor count:', n)
assert n == 1
t = t.replace(old6, new6)
io.open(p, 'w', encoding='utf-8', newline='').write(t)
print('script patched')
