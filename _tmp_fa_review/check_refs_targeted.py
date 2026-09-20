# -*- coding: utf-8 -*-
"""定向核验：PMID 直查 / 作者+关键词检索 / DOI 元数据。"""
import io, json, time, urllib.request, urllib.parse, re

def eutil(path, params):
    q = urllib.parse.urlencode(params)
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/%s?%s' % (path, q)
    req = urllib.request.Request(url, headers={'User-Agent': 'CKI-ref-check/1.0'})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

def pm_summary(pmid):
    s = eutil('esummary.fcgi', {'db': 'pubmed', 'id': str(pmid), 'retmode': 'json'})
    uid = s['result']['uids'][0]
    pm = s['result'][uid]
    return ('%s | %s %s:%s %s | authors: %s...' % (
        pm.get('title', '')[:120], pm.get('source', ''), pm.get('volume', ''),
        pm.get('pages', ''), pm.get('pubdate', '')[:4],
        (pm.get('authors', [{}])[0].get('name', '') if pm.get('authors') else '')))

def search(term):
    r = eutil('esearch.fcgi', {'db': 'pubmed', 'term': term, 'retmode': 'json', 'retmax': 3})
    ids = r.get('esearchresult', {}).get('idlist', [])
    return ids

def doi_meta(doi):
    req = urllib.request.Request('https://api.crossref.org/works/' + doi,
                                 headers={'User-Agent': 'CKI-ref-check/1.0 (mailto:knightz@pumc.edu.cn)'})
    it = json.loads(urllib.request.urlopen(req, timeout=30).read())['message']
    return 'vol=%s page=%s artnum=%s year=%s | %s' % (
        it.get('volume', ''), it.get('page', ''), it.get('article-number', ''),
        str((it.get('issued') or {}).get('date-parts', [[None]])[0][0]),
        (it.get('title') or [''])[0][:100])

checks = [
    ('#19 PMID 39210068', lambda: pm_summary(39210068)),
    ('#26 PMID 36384142', lambda: pm_summary(36384142)),
    ('#27 PMID 38849524', lambda: pm_summary(38849524)),
    ('#29 PMID 38409116', lambda: pm_summary(38409116)),
    ('#30 PMID 39300210', lambda: pm_summary(39300210)),
    ('#34 yeast noise paper', lambda: pm_summary(search('Newman Single-cell proteomic analysis of S cerevisiae')[0])),
    ('#20 Jones Development', lambda: pm_summary(search('Coelho-Santos meningeal perivascular fibroblast')[0])),
    ('#22 Shemer Jung review', lambda: [pm_summary(i) for i in search('Shemer Jung microglial Nat Rev Neurosci')][:1][0]),
    ('#28 Reeber Cerebellum', lambda: [pm_summary(i) for i in search('Reeber Arancillo Sillitoe Bergmann glia')][:1][0]),
    ('#13 HRT Atlas', lambda: [pm_summary(i) for i in search('Hounkpe HRT Atlas')][:1][0]),
    ('#47 Seurat v5', lambda: doi_meta('10.1038/s41587-023-01767-y')),
    ('#54 CELLxGENE', lambda: doi_meta('10.1093/nar/gkae1142')),
    ('#18 Walchli', lambda: [pm_summary(i) for i in search('Walchli single-cell atlas human brain vasculature')][:1][0]),
    ('#4 SATURN', lambda: doi_meta('10.1038/s41592-023-02041-4')),
    ('#37 CACIMAR', lambda: [pm_summary(i) for i in search('CACIMAR cross-species cell identities')][:1][0]),
    ('#23 Menassa', lambda: [pm_summary(i) for i in search('Menassa spatiotemporal dynamics microglia human lifespan')][:1][0]),
    ('#24 Barry-Carroll', lambda: [pm_summary(i) for i in search('Barry-Carroll microglia clonal expansion')][:1][0]),
    ('#21 Tan', lambda: [pm_summary(i) for i in search('Tan Yuan Tian microglial regional heterogeneity')][:1][0]),
    ('#39 Bakken', lambda: [pm_summary(i) for i in search('Bakken comparative cellular analysis motor cortex marmoset')][:1][0]),
]

for name, fn in checks:
    try:
        print(name, '=>', fn())
    except Exception as e:
        print(name, '=> ERR', str(e)[:100])
    time.sleep(0.6)
