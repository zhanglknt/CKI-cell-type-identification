from pathlib import Path
t = Path(r"C:/Users/KnightZ/Desktop/细胞受选择/results/CKI_Manuscript_NC_fulltext.txt").read_text(encoding="utf-8")
for pat in ["3,567", "3,563", "1.88", "1.71 (1.38", "LIHC 1.10", "LIHC 1.13",
            "1.3\u20133.3", "2.1\u20133.6", "29 expression", "33 expression",
            "KIRC 1.90", "KIRC 3.29", "KIRC 3.21", "LUSC 1.82", "LUSC 1.71"]:
    print(repr(pat), t.count(pat))
