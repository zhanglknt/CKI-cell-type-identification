# -*- coding: utf-8 -*-
"""全表作者核验：PubMed 精确标题检索 → 第一作者姓氏比对。"""
import io, json, re, time, urllib.request, urllib.parse, difflib

refs = [l.split('. ', 1)[1] for l in io.open(r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\refs_v47.txt', encoding='utf-8').read().split('\n') if l.strip()]

def eutil(path, params):
    q = urllib.parse.urlencode(params)
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/%s?%s' % (path, q)
    req = urllib.request.Request(url, headers={'User-Agent': 'CKI-ref-check/1.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def search(term, n=2):
    r = eutil('esearch.fcgi', {'db': 'pubmed', 'term': term, 'retmode': 'json', 'retmax': n})
    return r.get('esearchresult', {}).get('idlist', [])

def pm(pmid):
    s = eutil('esummary.fcgi', {'db': 'pubmed', 'id': str(pmid), 'retmode': 'json'})
    uid = s['result']['uids'][0]
    p = s['result'][uid]
    return p

results = []
for n, ref in enumerate(refs, 1):
    parts = ref.split('. ')
    ref_title = parts[1] if len(parts) > 2 else parts[0]
    our_first = parts[0].split(' ')[0].rstrip(',')
    rec = {'n': n, 'our_first': our_first}
    try:
        ids = search('"%s"[Title]' % ref_title.strip('.'))
        if not ids:
            rec['status'] = 'not_found'
        else:
            p = pm(ids[0])
            auths = [a['name'] for a in p.get('authors', [])]
            pm_first = auths[0].split(' ')[0] if auths else ''
            # consortium-style authors pass
            ok = our_first.lower() in [a.split(' ')[0].lower() for a in auths[:3]] or \
                 our_first.lower().replace('consortium', '') in p.get('title', '').lower() or \
                 'consortium' in our_first.lower() or 'network' in our_first.lower() or \
                 'program' in our_first.lower()
            # title match check (ensure right paper)
            sim = difflib.SequenceMatcher(None, ref_title.lower()[:70], p.get('title', '').lower()[:70]).ratio()
            rec.update({'status': 'ok' if ok else 'AUTHOR_MISMATCH',
                        'pm_first': pm_first, 'sim': round(sim, 2),
                        'pm_title': p.get('title', '')[:100],
                        'journal': p.get('source', ''), 'vol': p.get('volume', ''),
                        'pages': p.get('pages', ''), 'year': p.get('pubdate', '')[:4]})
    except Exception as e:
        rec['status'] = 'error'; rec['error'] = str(e)[:100]
    results.append(rec)
    tag = rec.get('status', '?')
    if tag != 'ok' or rec.get('sim', 1) < 0.85:
        print(n, tag, '| ours:', rec['our_first'], '| pm:', rec.get('pm_first', ''), '| sim', rec.get('sim', ''),
              '|', rec.get('journal', ''), rec.get('vol', '') + ':' + rec.get('pages', ''), rec.get('year', ''))
    time.sleep(0.5)

io.open(r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\refs_authors_v47.json', 'w', encoding='utf-8').write(json.dumps(results, ensure_ascii=False, indent=1))
print('done', len(results))
