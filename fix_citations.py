"""
Fix inline citations in generate_manuscript_v4_nar.py:
1. Map old reference numbers to new NAR ordering
2. Convert square brackets [n] to round brackets (n)
"""
import re

with open(r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_v4_nar.py", "r", encoding="utf-8") as f:
    content = f.read()

# ============================================================
# Old → New reference number mapping
# After removing duplicate ref 2/7 and adding ref 39 (Hao 2024 Seurat)
# ============================================================
mapping = {
    1: 1,    # Regev 2017 → 1
    2: 6,    # Tabula Sapiens (dup) → 6
    3: 2,    # Luecken 2019 → 2
    4: 3,    # Nei 1986 → 3
    5: 4,    # Hounkpe 2021 → 4
    6: 5,    # Tabula Muris → 5
    7: 6,    # Tabula Sapiens → 6
    8: 7,    # TCGA LUAD → 7
    9: 8,    # Weinstein 2013 → 8
    10: 9,   # TCGA BRCA → 9
    11: 10,  # Siletti 2023 → 10
    12: 11,  # Tran 2020 → 11
    13: 12,  # Korsunsky 2019 → 12
    14: 13,  # Lopez 2018 → 13
    15: 14,  # Rosen 2024 → 14
    16: 15,  # Lin 1991 → 15
    17: 16,  # Efron 1979 → 16
    18: 17,  # Benjamini 1995 → 17
    19: 18,  # Wolf 2018 → 18
    20: 19,  # Edmondson 1954 → 19
    21: 20,  # Perou 2000 → 20
    22: 21,  # Parker 2009 → 21
    23: 22,  # Yang 2007 → 22
    24: 23,  # Tarashansky 2021 → 23
    25: 24,  # Jiang 2024 → 24
    26: 25,  # Hao 2021 → 25
    27: 26,  # Megill 2021 → 26
    28: 27,  # Colaprico 2016 → 27
    29: 28,  # Cerami 2012 → 28
    30: 29,  # Pedregosa 2011 → 29
    31: 30,  # Liberzon 2015 → 30
    32: 31,  # Tsai 2016 → 31
    33: 32,  # Akay 2022 → 32
    34: 33,  # Foerster 2024 → 33
    35: 34,  # Endo 2024 → 34
    36: 35,  # Sepp 2026 → 35
    37: 36,  # Tan 2020 → 36
    38: 37,  # Menassa 2022 → 37
    39: 38,  # Walchli 2024 → 38
}

# Find all [n] or [n-m] or [n,m] citation patterns
# But only in string content (not in Python code syntax)
# Pattern: [digits, digits-dash, comma combinations]
def replace_citation(match):
    full = match.group(0)  # e.g., "[1-3]" or "[1,2,12]" or "[4]"
    inner = full[1:-1]     # e.g., "1-3" or "1,2,12" or "4"
    
    # Split by comma
    parts = re.split(r',\s*', inner)
    new_parts = []
    for part in parts:
        if '-' in part:
            # Range: 1-3 → new_low-new_high
            low, high = part.split('-')
            low = int(low)
            high = int(high)
            new_low = mapping.get(low, low)
            new_high = mapping.get(high, high)
            if new_low == new_high:
                new_parts.append(str(new_low))
            else:
                new_parts.append(f"{new_low}-{new_high}")
        else:
            num = int(part.strip())
            new_num = mapping.get(num, num)
            new_parts.append(str(new_num))
    
    # Deduplicate
    seen = set()
    unique = []
    for p in new_parts:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    
    return '(' + ','.join(unique) + ')'

# Apply replacements only inside string literals (p('...') function calls)
# Strategy: replace all [n], [n-m], [n,m,n] patterns that look like citations
# Citation pattern: [digits-only content, 1-3 digits, possibly with comma or dash]
citation_pattern = re.compile(r'\[(\d+(?:\s*[-,\s]\s*\d+)*)\]')

# We need to be careful: only replace citation brackets, not Python list brackets
# The citations appear inside string literals preceded by p(, ', or "
# Strategy: lines containing citation patterns are all inside string arguments to p()
# We can use a regex that only matches inside string context

# Simpler approach: replace all [digit...] patterns, skip lines that are pure Python
lines = content.split('\n')
new_lines = []
for line in lines:
    # Skip lines that are clearly Python code (not text content)
    stripped = line.strip()
    if stripped.startswith('#') or stripped.startswith('refs'):
        new_lines.append(line)
        continue
    
    # Only process lines that contain citation patterns in string context
    if '[' in line and re.search(r'\[\d+', line):
        # Check if this is inside a string (p('...'), p("..."), or '''...''')
        if "p('" in line or 'p("' in line or "'''" in line or '"""' in line:
            line = citation_pattern.sub(replace_citation, line)
        # Also handle lines with just string content (continuations)
        elif stripped.startswith("'") or stripped.startswith('"'):
            line = citation_pattern.sub(replace_citation, line)
    
    new_lines.append(line)

content = '\n'.join(new_lines)

# Also convert the figure script reference mentions in the DOCX text 
# (these are inside the p() calls but may have been missed)

with open(r"C:\Users\KnightZ\Desktop\细胞受选择\generate_manuscript_v4_nar.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Citation fix applied.")
print("Old → New mapping summary:")
for old, new in sorted(mapping.items()):
    if old != new:
        print(f"  [{old}] → ({new})")
