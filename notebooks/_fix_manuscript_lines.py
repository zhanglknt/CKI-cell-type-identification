"""Fix manuscript lines 395 and 397 with updated clinical analysis values."""
from pathlib import Path

MANUSCRIPT = Path("C:/Users/KnightZ/Desktop/细胞受选择/generate_manuscript_genome_biology.py")
with open(MANUSCRIPT, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Line 395 (index 394)
new_395 = ("p('Paired tumor-normal comparisons yielded higher \\u03c9 than unpaired "
           "comparisons in four of five cancer types (paired/unpaired "
           "ratio = 0.99\u20133.25, Mann-Whitney P = 0.024 for LIHC, not significant "
           "for others). However, the small number of patients with paired tumor "
           "and normal samples (n = 2\u20135 per cancer type) limits statistical "
           "power and precludes definitive conclusions about within-patient versus "
           "between-patient variation.')\n")

lines[394] = new_395
print("Line 395 updated")

# Line 397 (index 396)
new_397 = ("p('We then asked whether \\u03c9 tracks with clinical severity within "
           "cancer types. In liver cancer, \\u03c9 decreased with increasing "
           "Edmondson grade [10]: G1 (101.8 \\u00b1 46.8, n = 39) > "
           "G2 (100.2 \\u00b1 63.9, n = 133) > G3 (96.8 \\u00b1 58.2, n = 105) > "
           "G4 (90.0 \\u00b1 57.8, n = 11; Jonckheere-Terpstra trend test, "
           "P < 0.001). In breast cancer, PAM50 subtype analysis [11,12] "
           "revealed a gradient of transcriptional heterogeneity: Luminal A "
           "tumors had the highest intratumoral \\u03c9 (344.5 \\u00b1 323.4, "
           "n = 224), followed by Luminal B (313.6 \\u00b1 282.7, n = 123), "
           "HER2-enriched (263.0 \\u00b1 255.6, n = 55), and Basal-like tumors "
           "(223.4 \\u00b1 183.7, n = 97), with Normal-like tumors having the "
           "lowest \\u03c9 (108.0 \\u00b1 65.5, n = 7; Kruskal-Wallis, "
           "P = 0.0002). Lung adenocarcinoma mutation stratification showed "
           "significant differences (Kruskal-Wallis, P = 0.017), with "
           "EGFR-mutant (285.3 \\u00b1 180.1, n = 61) and KRAS-mutant tumors "
           "(284.6 \\u00b1 227.9, n = 120) exhibiting higher \\u03c9 than "
           "wild-type tumors (237.6 \\u00b1 195.4, n = 311).')\n")

lines[396] = new_397
print("Line 397 updated")

with open(MANUSCRIPT, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("\nDone. Verifying...")
with open(MANUSCRIPT, "r", encoding="utf-8") as f:
    vlines = f.readlines()
print(f"\nLine 395 ({len(vlines[394])} chars): {vlines[394][:80]}...")
print(f"Line 397 ({len(vlines[396])} chars): {vlines[396][:80]}...")
