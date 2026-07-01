import subprocess, json, re, time, sys

# 读取参考文献
refs = []
with open('notebooks/_refs_extracted.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line:
            refs.append(line)

print(f"共 {len(refs)} 条参考文献，开始 PubMed 验证...\n")

results = []  # (num, ref_short, status, pmid, note)

for i, ref in enumerate(refs, 1):
    # 提取第一作者 + 年份 + 期刊作为搜索词
    # 格式: "1. Author,et al. (YYYY) Title. Journal, vol, pages."
    m = re.match(r'^\d+\.\s+(.+?)\s+\((\d{4})\)\s+(.+?),\s+', ref)
    if not m:
        # 尝试 Consortium 格式
        m2 = re.match(r'^\d+\.\s+(.+?Consortium\.)\s+\((\d{4})\)\s+(.+?),\s+', ref)
        if m2:
            author = m2.group(1).split()[0] + ' Consortium'
            year = m2.group(2)
            journal = m2.group(3)
        else:
            results.append((i, ref[:60], 'SKIP', '-', '无法解析'))
            continue
    else:
        # 取第一作者姓
        author_part = m.group(1).strip()
        # 取第一个作者姓
        first_author = author_part.split(',')[0].strip().rstrip('.')
        year = m.group(2)
        journal_part = m.group(3).strip()
        # 取期刊前3个词作为搜索词
        journal_words = re.findall(r'[A-Za-z]+', journal_part)[:4]
        journal_short = ' '.join(journal_words)
    
    # 构建搜索词: 第一作者 + 年份 + 期刊关键词
    term = f"{first_author} {year} {journal_short}"
    # 也尝试用 DOI 搜索
    doi_match = re.search(r'10\.\d{4,}/[^\s\.,;]+', ref)
    if doi_match:
        doi = doi_match.group(0).rstrip('.,;')
        term2 = f"doi {doi}"
    else:
        term2 = None
    
    # 尝试搜索
    found = False
    pmid = '-'
    note = ''
    
    for attempt, search_term in enumerate([term, term2]):
        if not search_term:
            continue
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={search_term.replace(' ', '+')}&retmode=json&retmax=1"
        cmd = ['curl', '-k', '-s', '--max-time', '10', url]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(out.stdout)
            count = int(data['esearchresult']['count'])
            if count > 0:
                pmid = data['esearchresult']['idlist'][0]
                found = True
                note = f"found via {'author+year' if attempt==0 else 'DOI'}"
                break
        except Exception as e:
            note = str(e)[:50]
            time.sleep(0.5)
    
    if found:
        results.append((i, ref[:70], 'OK', pmid, note))
    else:
        results.append((i, ref[:70], 'NOT_FOUND', '-', note or 'no match'))
    
    # 限速：每次查询间隔 0.34s (PubMed 要求 ≤3req/s)
    if i % 10 == 0:
        print(f"  进度: {i}/{len(refs)}")
    time.sleep(0.34)

# 输出报告
print("\n" + "="*80)
print("PubMed 验证报告")
print("="*80)
ok = [r for r in results if r[2] == 'OK']
nf = [r for r in results if r[2] == 'NOT_FOUND']
sk = [r for r in results if r[2] == 'SKIP']

print(f"\n总计: {len(refs)} 条")
print(f"  ✓ 找到: {len(ok)} 条")
print(f"  ✗ 未找到: {len(nf)} 条")
print(f"  - 跳过: {len(sk)} 条")

if ok:
    print(f"\n--- 找到的文献 (PMID) ---")
    for r in ok:
        print(f"  [{r[0]}] PMID:{r[3]}  {r[1][:60]}...")

if nf:
    print(f"\n--- 未找到的文献 (需人工核对) ---")
    for r in nf:
        print(f"  [{r[0]}] {r[1][:70]}...")

if sk:
    print(f"\n--- 跳过的文献 (格式无法解析) ---")
    for r in sk:
        print(f"  [{r[0]}] {r[1][:70]}...")

# 写报告文件
with open('notebooks/_pubmed_verify_report.txt', 'w', encoding='utf-8') as f:
    f.write("CKI NAR Manuscript - PubMed Reference Verification Report\n")
    f.write("="*70 + "\n\n")
    f.write(f"Total: {len(refs)}\nFound: {len(ok)}\nNot found: {len(nf)}\nSkipped: {len(sk)}\n\n")
    f.write("--- FOUND ---\n")
    for r in ok:
        f.write(f"[{r[0]}] PMID:{r[3]}  {refs[r[0]-1][:100]}\n")
    f.write("\n--- NOT FOUND (need manual check) ---\n")
    for r in nf:
        f.write(f"[{r[0]}] {refs[r[0]-1]}\n")
    f.write("\n--- SKIPPED ---\n")
    for r in sk:
        f.write(f"[{r[0]}] {refs[r[0]-1]}\n")

print(f"\n报告已写入: notebooks/_pubmed_verify_report.txt")
