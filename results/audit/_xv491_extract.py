# xv491: dump paragraphs containing key phrases from MS/SI/CL
from pathlib import Path

ROOT = Path(r"C:/Users/KnightZ/Desktop/细胞受选择")
KEYS = ["admix", "purity", "smok", "3,563", "3563", "1.13", "2.46", "2.86",
        "KIRC", "LIHC", "ever-smoker", "baseline", "TODO", "metadata",
        "0/30", "28.6", "45.2", "Kang"]
for f in ["results/CKI_Manuscript_NC_fulltext.txt",
          "results/CKI_NC_Cover_Letter_fulltext.txt",
          "results/CKI_Reproducibility_Guide_NC_fulltext.txt"]:
    text = (ROOT / f).read_text(encoding="utf-8")
    print("=" * 100)
    print("FILE:", f)
    for i, para in enumerate(text.split("\n")):
        low = para.lower()
        if any(k.lower() in low for k in KEYS):
            print(f"--- [{f} line {i+1}] ---")
            print(para.strip())
