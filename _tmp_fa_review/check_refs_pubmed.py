# -*- coding: utf-8 -*-
"""第二通道交叉验证：PubMed E-utilities。对 56 条文献用标题检索 PubMed，
取权威卷/页/年份/期刊/作者比对。"""
import io, json, re, time, urllib.request, urllib.parse

refs = [l.split('. ', 1)[1] for l in io.open(r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\refs_v47.txt', encoding='utf-8').read().split('\n') if l.strip()]
assert len(refs) == 56

def eutil(path, params):
    q = urllib.parse.urlencode(params)
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/%s?%s' % (path, q)
    req = urllib.request.Request(url, headers={'User-Agent': 'CKI-ref-check/1.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

out = []
for n, ref in enumerate(refs, 1):
    rec = {'n': n, 'ref': ref, 'status': 'pending'}
    # title = 2nd '. '-separated segment
    parts = ref.split('. ')
    title = parts[1] if len(parts) > 2 else parts[0]
    title_clean = re.sub(r'[^A-Za-z0-9 ]', ' ', title).strip()
    try:
        r = eutil('esearch.fcgi', {'db': 'pubmed', 'term': title_clean + '[Title]', 'retmode': 'json', 'retmax': 3})
        ids = r.get('esearchresult', {}).get('idlist', [])
        if not ids:
            rec['status'] = 'no_pmid'
            out.append(rec); print(n, 'NO_PMID |', title[:70]); time.sleep(0.5); continue
        s = eutil('esummary.fcgi', {'db': 'pubmed', 'id': ','.join(ids[:1]), 'retmode': 'json'})
        pm = s['result'][s['result']['uids'][0]]
        rec['status'] = 'ok'
        rec['pm'] = {
            'pmid': pm.get('uid'), 'title': pm.get('title', '')[:200],
            'journal': pm.get('source', ''), 'volume': pm.get('volume', ''),
            'pages': pm.get('pages', ''), 'articleids': [a.get('value') for a in pm.get('articleids', []) if a.get('idtype') == 'doi'],
            'pubyear': pm.get('pubdate', '')[:4],
            'lastauthor': pm.get('lastauthor', ''), 'nauthors': len(pm.get('authors', [])),
            'fulljournalname': pm.get('fulljournalname', ''),
        }
        out.append(rec)
        print(n, 'PMID', pm.get('uid'), '|', pm.get('source', ''), pm.get('pubdate', '')[:4], '|', pm.get('volume', '') + ':' + pm.get('pages', ''), '|', pm.get('title', '')[:60])
    except Exception as e:
        rec['status'] = 'error'
        rec['error'] = str(e)[:150]
        out.append(rec); print(n, 'ERROR', str(e)[:80])
    time.sleep(0.5)

io.open(r'C:\Users\KnightZ\Desktop\细胞受选择\_tmp_fa_review\refs_pubmed_v47.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
print('saved, total', len(out))
