# -*- coding: utf-8 -*-
"""v47 参考文献真实性核查：CrossRef bibliographic 查询比对。
对每条文献：query.bibliographic=整条引用串，取 top hit，
比对 year / container-title / title 相似度 / DOI。"""
import io, json, time, urllib.request, urllib.parse, re, difflib

refs = [l.split('. ', 1)[1] for l in io.open(r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\refs_v47.txt', encoding='utf-8').read().split('\n') if l.strip()]
assert len(refs) == 56, len(refs)

MAILTO = 'knightz@pumc.edu.cn'
out = []

def crossref(ref):
    q = urllib.parse.urlencode({'query.bibliographic': ref, 'rows': 3, 'mailto': MAILTO})
    url = 'https://api.crossref.org/works?' + q
    req = urllib.request.Request(url, headers={'User-Agent': 'CKI-ref-check/1.0 (mailto:%s)' % MAILTO})
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
    items = d.get('message', {}).get('items', [])
    return items

def parse_ref(ref):
    # extract year
    ym = re.search(r'(\d{4})', ref)
    year = ym.group(1) if ym else None
    # extract title: text before the journal-year part; approximate: longest sentence-fragment
    # strategy: split by '. ' — authors are 1st, title is 2nd (if authors end with et al./initials)
    parts = ref.split('. ')
    return year, parts

for n, ref in enumerate(refs, 1):
    rec = {'n': n, 'ref': ref, 'status': 'pending'}
    try:
        items = crossref(ref)
    except Exception as e:
        rec['status'] = 'query_error'
        rec['error'] = str(e)[:200]
        out.append(rec)
        print(n, 'QUERY_ERROR', str(e)[:80])
        continue
    best = None
    for it in items:
        title = (it.get('title') or [''])[0] if it.get('title') else ''
        year = str((it.get('issued') or {}).get('date-parts', [[None]])[0][0] or '')
        cont = (it.get('container-title') or [''])[0] if it.get('container-title') else ''
        sim = difflib.SequenceMatcher(None, ref.lower()[:120], (title + ' ' + cont + ' ' + year).lower()[:120]).ratio()
        # better: title-vs-2nd-sentence similarity
        parts = ref.split('. ')
        ref_title = parts[1] if len(parts) > 2 else (parts[0] if parts else '')
        sim2 = difflib.SequenceMatcher(None, ref_title.lower()[:100], title.lower()[:100]).ratio()
        score = sim2
        if best is None or score > best['score']:
            best = {'score': round(score, 3), 'title': title[:150], 'year': year,
                    'journal': cont[:80], 'doi': it.get('DOI'), 'type': it.get('type'),
                    'authors': len(it.get('author', []))}
    rec['status'] = 'ok'
    rec['match'] = best
    out.append(rec)
    flag = 'WEAK' if best and best['score'] < 0.75 else ('OK' if best else 'NONE')
    print(n, flag, 'score=%.2f' % (best['score'] if best else -1), '|', (best['title'][:60] if best else ''), '|', (best['year'] if best else ''))
    time.sleep(1.0)

io.open(r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\refs_crossref_v47.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
print('saved JSON, total', len(out))
