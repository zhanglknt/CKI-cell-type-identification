import sys, glob, os
sys.path.insert(0, r'C:\Users\KnightZ\.workbuddy\binaries\python\envs\default\Lib\site-packages')
import fitz

for fp in sorted(glob.glob('results/figures_submission_nc/figure*.pdf')):
    if 'merged' in fp or 'toprow' in fp:
        continue
    d = fitz.open(fp)
    sizes = {}
    fonts = set()
    for pg in d:
        for b in pg.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                for s in l['spans']:
                    k = round(s['size'], 1)
                    sizes[k] = sizes.get(k, 0) + 1
                    fonts.add(s['font'])
    sub7 = sum(c for sz, c in sizes.items() if sz < 6.95)
    tot = sum(sizes.values())
    print(f'{os.path.basename(fp):12s} pages={len(d)} spans={tot:4d} sub7pt={sub7:4d} '
          f'min={min(sizes) if sizes else 0}  fonts={sorted(fonts)}')
    small = {k: v for k, v in sorted(sizes.items()) if k < 6.95}
    if small:
        print('   sub-7pt sizes:', small)
