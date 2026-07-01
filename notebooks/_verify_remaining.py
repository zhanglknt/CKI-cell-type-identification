import subprocess, json, time

queries = [
    (4,  "Hounkpe HRT Atlas 2021 Nucleic Acids Research", "Hounkpe+2021+HRT+Atlas"),
    (7,  "TCGA lung adenocarcinoma 2014 Nature", "TCGA+lung+adenocarcinoma+2014+Nature"),
    (14, "Rosen universal cell type embeddings 2024 Nature Methods", "Rosen+universal+cell+type+2024"),
    (25, "Colaprico TCGAbiolinks 2016 Nucleic Acids", "Colaprico+TCGAbiolinks+2016"),
    (29, "Akay astrocyte endfoot 2022 Neuron", "Akay+astrocyte+2022+Neuron"),
    (31, "Endo astrocyte Tcf4 2024 EMBO", "Endo+astrocyte+Tcf4+2024+EMBO"),
]

print("逐条查询 6 条未找到文献...\n")
results = {}

for num, desc, term in queries:
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={term.replace(' ', '+')}&retmode=json&retmax=3"
    cmd = ['curl', '-k', '-s', '--max-time', '10', url]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    try:
        data = json.loads(out.stdout)
        count = int(data['esearchresult']['count'])
        ids = data['esearchresult']['idlist']
        if count > 0:
            pmid = ids[0]
            # 取文章详情确认
            url2 = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            out2 = subprocess.run(['curl', '-k', '-s', '--max-time', '10', url2], capture_output=True, text=True, timeout=15)
            info = json.loads(out2.stdout)
            if 'result' in info and pmid in info['result']:
                title = info['result'][pmid].get('title', '')[:60]
                journal = info['result'][pmid].get('fulljournalname', '')
                print(f"  [{num}] ✓ FOUND  PMID:{pmid}")
                print(f"       Title: {title}...")
                print(f"       Journal: {journal}")
                results[num] = ('OK', pmid, title)
            else:
                print(f"  [{num}] ? FOUND PMID:{pmid} (无法获取详情)")
                results[num] = ('OK', pmid, '')
        else:
            print(f"  [{num}] ✗ NOT FOUND (count=0)")
            print(f"       query: {term}")
            results[num] = ('NOT_FOUND', '-', '')
    except Exception as e:
        print(f"  [{num}] ✗ ERROR: {e}")
        results[num] = ('ERROR', '-', str(e))
    time.sleep(0.4)

print("\n" + "="*60)
print("汇总:")
for num, desc, _ in queries:
    status, pmid, title = results[num]
    print(f"  [{num}] {status:15s}  PMID:{pmid}  {desc[:50]}")
