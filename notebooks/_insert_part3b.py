"""
Helper: Insert Part 3b cells into CKI_Reproducibility.ipynb
Inserts between cell-23 (Part 3 end) and cell-24 (Part 4 start)
"""
import json
from pathlib import Path

NB_PATH = Path("C:/Users/KnightZ/Desktop/细胞受选择/notebooks/CKI_Reproducibility.ipynb")

with open(NB_PATH) as f:
    nb = json.load(f)

# New cells to insert after index 23 (before Part 4)
new_cells = []

# Cell 3b-1: Markdown header
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "---\n",
        "# Part 3b: Paired/Unpaired + Clinical Severity\n",
        "\n",
        "**Source script**: `notebooks/07_phase34_clinical.py` (run separately; requires cBioPortal clinical metadata)\n",
        "\n",
        "This section loads the pre-computed clinical analysis results. The standalone script `07_phase34_clinical.py` handles clinical data fetching (LIHC Edmondson grade, BRCA PAM50 subtype, LUAD EGFR/KRAS mutations) and re-computes TCGA omega values with participant-level tracking for paired/unpaired comparisons.\n",
        "\n",
        "**Output files**:\n",
        "- `results/phase34_clinical_paired_unpaired.csv` — Paired vs unpaired TN omega\n",
        "- `results/phase34_clinical_severity.csv` — Clinical severity stratification\n",
        "- `results/phase34_clinical_plots.png` — Visualization\n",
        "- `results/phase34_clinical_report.md` — Summary report\n"
    ]
})

# Cell 3b-2: Load and display paired/unpaired results
new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "# Part 3b.1: Paired vs Unpaired Tumor-Normal Omega\n",
        "import json\n",
        "from pathlib import Path\n",
        "\n",
        "PAIRED_CSV = RESULTS_DIR / 'phase34_clinical_paired_unpaired.csv'\n",
        "\n",
        "if not PAIRED_CSV.exists():\n",
        "    print('WARNING: phase34_clinical_paired_unpaired.csv not found!')\n",
        "    print('Run notebooks/07_phase34_clinical.py first to generate clinical analysis results.')\n",
        "else:\n",
        "    paired_df = pd.read_csv(PAIRED_CSV)\n",
        "    print('=== Paired vs Unpaired TN Omega ===')\n",
        "    display(paired_df)\n",
        "    \n",
        "    print()\n",
        "    ratios = []\n",
        "    pvals = []\n",
        "    for _, row in paired_df.iterrows():\n",
        "        try:\n",
        "            r = float(row['Paired_Unpaired_ratio'])\n",
        "            p = float(row['P_value'])\n",
        "            ratios.append(r)\n",
        "            pvals.append(p)\n",
        "            sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'\n",
        "            print(f\"  {row['Cancer']}: n_paired={int(row['n_Paired_TN'])}, n_unpaired={int(row['n_Unpaired_TN'])}, ratio={r:.2f}, P={p:.2e} {sig}\")\n",
        "        except (ValueError, KeyError):\n",
        "            pass\n",
        "    \n",
        "    if ratios:\n",
        "        print(f\"\n  Ratio range: {min(ratios):.2f} - {max(ratios):.2f}\")\n",
        "        all_ns = all(p > 0.05 for p in pvals)\n",
        "        print(f\"  All non-significant (P > 0.05): {all_ns}\")\n",
        "        if not all_ns:\n",
        "            print(f\"  => Paired TN omega is SIGNIFICANTLY lower than unpaired.\")\n"
    ],
    "outputs": [],
    "execution_count": None
})

# Cell 3b-3: Load and display clinical severity results
new_cells.append({
    "cell_type": "code",
    "metadata": {},
    "source": [
        "# Part 3b.2: Clinical Severity Stratification\n",
        "CLINICAL_CSV = RESULTS_DIR / 'phase34_clinical_severity.csv'\n",
        "REPORT_MD = RESULTS_DIR / 'phase34_clinical_report.md'\n",
        "\n",
        "if not CLINICAL_CSV.exists():\n",
        "    print('WARNING: phase34_clinical_severity.csv not found!')\n",
        "    print('Run notebooks/07_phase34_clinical.py first to generate clinical analysis results.')\n",
        "else:\n",
        "    clinical_df = pd.read_csv(CLINICAL_CSV)\n",
        "    print('=== Clinical Severity Stratification ===')\n",
        "    print(f'Total groups: {len(clinical_df)}')\n",
        "    display(clinical_df)\n",
        "    \n",
        "    # Group by cancer + stratification\n",
        "    for (cancer, strat), grp in clinical_df.groupby(['cancer', 'stratification']):\n",
        "        print(f'\\n  {cancer} | {strat}:')\n",
        "        for _, row in grp.iterrows():\n",
        "            print(f\"    {row['group']}: n={int(row['n'])}, mean_omega={float(row['omega_mean']):.2f} +/- {float(row['omega_std']):.2f}\")\n",
        "\n",
        "# Also display the clinical report if available\n",
        "REPORT_MD = RESULTS_DIR / 'phase34_clinical_report.md'\n",
        "if REPORT_MD.exists():\n",
        "    print('\\n### Clinical Report Excerpt ###')\n",
        "    with open(REPORT_MD, 'r') as f:\n",
        "        content = f.read()\n",
        "    # Print first 800 chars\n",
        "    print(content[:800])\n"
    ],
    "outputs": [],
    "execution_count": None
})

# Cell 3b-4: Markdown summary
new_cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Part 3b Summary\n",
        "\n",
        "**Paired vs Unpaired TN**: \n",
        "- The paired/unpaired ratio and P-values are displayed above\n",
        "- Interpretation depends on whether the ratio is significantly different from 1.0\n",
        "\n",
        "**Clinical Severity**:\n",
        "- LIHC: Edmondson grade trend (Jonckheere-Terpstra test)\n",
        "- BRCA: PAM50 subtype differences (Kruskal-Wallis test)  \n",
        "- LUAD: EGFR/KRAS mutation stratification (Kruskal-Wallis test)\n",
        "\n",
        "The full analysis pipeline is in `notebooks/07_phase34_clinical.py`.\n"
    ]
})

# Insert after cell 23 (index 23)
insert_pos = 24  # After cell-23 (0-indexed: cell 0-23 = 24 cells)
for i, cell in enumerate(new_cells):
    nb['cells'].insert(insert_pos + i, cell)

with open(NB_PATH, 'w') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Inserted {len(new_cells)} cells after cell-23 (Part 3 end).")
print(f"Total cells now: {len(nb['cells'])}")

# ====================================================================
# Part 2: Update manuscript with actual paired/unpaired values
# ====================================================================
import pandas as pd
import numpy as np

PAIRED_CSV = Path("C:/Users/KnightZ/Desktop/细胞受选择/results/phase34_clinical_paired_unpaired.csv")
MANUSCRIPT = Path("C:/Users/KnightZ/Desktop/细胞受选择/generate_manuscript_genome_biology.py")

if not PAIRED_CSV.exists():
    print("\nWARNING: paired_unpaired CSV not found, skipping manuscript update.")
    print("Run 07_phase34_clinical.py first.")
else:
    df = pd.read_csv(PAIRED_CSV)
    ratios = []
    pvals = []
    for _, row in df.iterrows():
        try:
            r = float(row['Paired_Unpaired_ratio'])
            p = float(row['P_value'])
            ratios.append(r)
            pvals.append(p)
        except (ValueError, KeyError):
            pass
    
    if ratios:
        ratio_min = min(ratios)
        ratio_max = max(ratios)
        # Find the minimum P-value
        p_min = min(pvals)
        p_max = max(pvals)
        
        # Determine significance
        if p_min < 0.001:
            sig_text = f"P<{p_min:.0e}"
        elif p_min < 0.01:
            sig_text = f"P={p_min:.0e}"
        else:
            sig_text = f"P={p_min:.2g}"
        
        print(f"\n=== Paired/Unpaired Results ===")
        print(f"  Ratio range: {ratio_min:.2f} - {ratio_max:.2f}")
        print(f"  P-value range: {p_min:.2e} - {p_max:.2e}")
        print(f"  Significance: {sig_text}")
        
        # Update manuscript
        with open(MANUSCRIPT, 'r', encoding='utf-8') as f:
            ms = f.read()
        
        # The manuscript uses en-dash (U+2013) for ranges: "0.83–1.13"
        # Exact pattern: "ratio = 0.83–1.13, all P > 0.05"
        import re
        pattern = r'ratio\s*=\s*[\d.]+\u2013[\d.]+,\s*all\s+P\s*>\s*[\d.]+'
        match = re.search(pattern, ms)
        
        if match:
            old_text = match.group()
            # Only count valid (non-NA) P-values
            valid_pvals = [p for p in pvals if not np.isnan(p)]
            if valid_pvals:
                p_str = f"{min(valid_pvals):.0e}" if min(valid_pvals) < 0.01 else f"{min(valid_pvals):.2g}"
                new_text = f"ratio = {ratio_min:.2f}\u2013{ratio_max:.2f}, P = {p_str}"
            else:
                new_text = f"ratio = {ratio_min:.2f}\u2013{ratio_max:.2f}"
            
            ms = ms.replace(old_text, new_text)
            with open(MANUSCRIPT, 'w', encoding='utf-8') as f:
                f.write(ms)
            print(f"\n  Updated manuscript line 395:")
            print(f"  Old: {old_text}")
            print(f"  New: {new_text}")
            print(f"\n  NOTE: Clinical severity paragraph (line 397) also needs manual update")
            print(f"  because the omega values changed significantly (see report.md).")
        else:
            print(f"\n  WARNING: pattern not found in manuscript!")
            for i, line in enumerate(ms.split('\n')):
                if 'paired' in line.lower() and ('unpaired' in line.lower()):
                    print(f"  Found at line {i+1}: {line.strip()[:150]}")
                    m = re.search(r'ratio\s*=\s*[\d.\u2013\-,]+.*?P\s*[><=]', line)
                    if m:
                        print(f"  Substring match: {m.group()}")
    else:
        print("\n  WARNING: No valid ratio values in CSV.")
        
print("\nDone.")
