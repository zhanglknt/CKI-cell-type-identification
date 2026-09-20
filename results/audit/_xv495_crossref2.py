# xv495 pass 2: targeted re-query with author+title for refs with weak first-pass hits
import json, re, time, urllib.parse, urllib.request

UA = {"User-Agent": "CKI-ref-check/1.0 (mailto:knightz@pumc.edu.cn)"}
TARGETS = {
    1: ("Regev Human Cell Atlas eLife 2017", "Regev", "eLife", "6", "e27041", "2017"),
    3: ("Lopez Regier Deep generative modeling single-cell transcriptomics Nature Methods 2018", "Lopez", "Nature Methods", "15", "1053-1058", "2018"),
    6: ("Nei Gojobori Simple methods estimating synonymous nonsynonymous nucleotide substitutions 1986", "Nei", "Molecular Biology and Evolution", "3", "418-426", "1986"),
    7: ("Yang PAML 4 phylogenetic analysis maximum likelihood Molecular Biology Evolution 2007", "Yang", "Molecular Biology and Evolution", "24", "1586-1591", "2007"),
    9: ("Tabula Sapiens multiple-organ single-cell transcriptomic atlas humans Science 2022", "Tabula Sapiens", "Science", "376", "eabl4896", "2022"),
    11: ("Comprehensive molecular portraits human breast tumours Nature 2012 Cancer Genome Atlas", "Cancer Genome Atlas", "Nature", "490", "61-70", "2012"),
    16: ("Perou Molecular portraits human breast tumours Nature 2000", "Perou", "Nature", "406", "747-752", "2000"),
    17: ("Parker Supervised risk predictor breast cancer intrinsic subtypes Journal Clinical Oncology 2009", "Parker", "Journal of Clinical Oncology", "27", "1160-1167", "2009"),
    18: ("Walchli Single-cell atlas human brain vasculature development adulthood disease Nature 2024", "W\u00e4lchli", "Nature", "632", "603-613", "2024"),
    20: ("Jones Meningeal origins dynamics perivascular fibroblast development mouse cerebral vasculature Development 2023", "Jones", "Development", "150", "dev201805", "2023"),
    27: ("Foerster Developmental origin oligodendrocytes determines function adult brain Nature Neuroscience 2024", "Foerster", "Nature Neuroscience", "27", "1545-1554", "2024"),
    30: ("Zhang Astrocyte allocation brain development Tcf4 fate restriction EMBO Journal 2024", "Zhang", "EMBO Journal", "43", "5114-5140", "2024"),
    33: ("Elowitz Levine Siggia Swain Stochastic gene expression single cell Science 2002", "Elowitz", "Science", "297", "1183-1186", "2002"),
    35: ("Raj van Oudenaarden Nature nurture chance stochastic gene expression Cell 2008", "Raj", "Cell", "135", "216-226", "2008"),
    36: ("Tarashansky Mapping single-cell atlases Metazoa cell type evolution eLife 2021", "Tarashansky", "eLife", "10", "e66747", "2021"),
    37: ("Jiang CACIMAR cross-species cell identities markers regulations interactions Briefings Bioinformatics 2024", "Jiang", "Briefings in Bioinformatics", "25", "bbae283", "2024"),
    38: ("Skinnider Cell type prioritization single-cell data Nature Biotechnology 2021", "Skinnider", "Nature Biotechnology", "39", "30-34", "2021"),
    40: ("Bakken Comparative cellular analysis motor cortex human marmoset mouse Nature 2021", "Bakken", "Nature", "598", "111-119", "2021"),
    41: ("Marques Oligodendrocyte heterogeneity mouse juvenile adult central nervous system Science 2016", "Marques", "Science", "352", "1326-1329", "2016"),
    43: ("Luecken Theis Current best practices single-cell RNA-seq analysis tutorial Molecular Systems Biology 2019", "Luecken", "Molecular Systems Biology", "15", "e8746", "2019"),
    45: ("Benjamini Hochberg Controlling false discovery rate practical powerful approach multiple testing 1995", "Benjamini", "Journal of the Royal Statistical Society Series B", "57", "289-300", "1995"),
    47: ("Hao Integrated analysis multimodal single-cell data Cell 2021", "Hao", "Cell", "184", "3573-3587", "2021"),
    53: ("Pedregosa Scikit-learn machine learning Python Journal Machine Learning Research 2011", "Pedregosa", "Journal of Machine Learning Research", "12", "2825-2830", "2011"),
    54: ("Efron Tibshirani An Introduction to the Bootstrap 1994", "Efron", "Chapman and Hall", "", "", "1994"),
}

def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

def sim(a, b):
    ta, tb = norm(a), norm(b)
    if not ta or not tb:
        return 0.0
    sa, sb = set(ta.split()), set(tb.split())
    return len(sa & sb) / max(len(sa), len(sb))

def q(title, rows=5):
    qs = urllib.parse.urlencode({"query.bibliographic": title, "rows": rows})
    req = urllib.request.Request(f"https://api.crossref.org/works?{qs}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

out = {}
for num, (query, want_auth, want_jrnl, want_vol, want_page, want_year) in TARGETS.items():
    try:
        items = q(query).get("message", {}).get("items", [])
    except Exception as e:
        print(f"[{num}] ERROR {e}", flush=True)
        time.sleep(1.0)
        continue
    scored = []
    for it in items:
        t = " ".join(it.get("title", [])[:1])
        auths = it.get("author", [])
        fam = auths[0].get("family", "") or auths[0].get("name", "") if auths else ""
        c = " ".join(it.get("container-title", [])[:1])
        vol = it.get("volume", "")
        page = it.get("page", "") or it.get("article-number", "")
        dp = it.get("published-print") or it.get("published") or it.get("issued") or {}
        yr = str((dp.get("date-parts", [[None]]) or [[None]])[0][0])
        s = sim(t, query)
        scored.append((s, fam, yr, c, vol, page, it.get("DOI", ""), t, len(auths), it.get("type","")))
    scored.sort(key=lambda x: -x[0])
    out[num] = [{"sim": round(s, 3), "fam": f, "yr": y, "container": c, "vol": v,
                 "page": p, "doi": d, "title": t, "n_auth": na, "type": ty}
                for s, f, y, c, v, p, d, t, na, ty in scored[:3]]
    top = out[num][0] if out[num] else None
    print(f"[{num}] top: {top}", flush=True)
    time.sleep(0.8)

with open(r"C:/Users/KnightZ/Desktop/细胞受选择/results/audit/_xv495_crossref2.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("saved")
