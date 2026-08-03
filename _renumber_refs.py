#!/usr/bin/env python3
"""
Renumber references in generate_manuscript_nar.py by order of first citation.
This addresses N5/Med3: references must appear in order of first citation (NAR requirement).

Approach:
1. Scan all p('...') text for (N) and (N,M) citation patterns
2. Determine first-appearance order
3. Create old→new mapping
4. Replace all citation numbers in text strings
5. Reorder _refs_nar list
6. Write modified file
"""

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
SRC = BASE_DIR / "generate_manuscript_nar.py"
OUT = BASE_DIR / "generate_manuscript_nar.py"  # in-place
BACKUP = BASE_DIR / "generate_manuscript_nar_v26_backup.py"

# ============================================================
# First-appearance order determined by manual scan of manuscript text.
# Each entry: (old_number, line_where_first_seen)
# ============================================================
first_appearance = [
    (16, 398),   # Human Cell Atlas / HCA
    (1, 398),    # Harmony
    (2, 398),    # scVI
    (3, 398),    # SATURN
    (32, 398),   # Tran batch-effect
    (31, 398),   # Nei Ka/Ks
    (5, 404),    # Tabula Muris
    (6, 404),    # Tabula Sapiens
    (7, 404),    # TCGA LUAD
    (8, 404),    # TCGA breast
    (9, 404),    # Siletti brain atlas
    (30, 412),   # Luecken best practices
    (4, 412),    # HRT Atlas
    (25, 423),   # Scanpy
    (26, 423),   # Seurat v4
    (27, 423),   # Seurat v5
    (28, 427),   # Weinstein TCGA Pan-Cancer
    (29, 427),   # Colaprico TCGAbiolinks
    (14, 427),   # Cerami cBioPortal
    (11, 427),   # Perou PAM50
    (12, 427),   # Parker PAM50 risk
    (10, 427),   # Edmondson grade
    (24, 446),   # Storey FDR
    (36, 508),   # Walchli brain vasculature
    (13, 532),   # Tsai OPC migration
    (17, 532),   # Akay astrocyte endfoot
    (35, 532),   # Foerster oligodendrocyte origin
    (41, 538),   # Reeber Bergmann glia
    (18, 538),   # Endo Tcf4 astrocytes
    (19, 541),   # Yang fetal cerebellum
    (37, 544),   # Shemer microglial colonization
    (20, 544),   # Menassa microglia lifespan
    (40, 544),   # Barry-Carroll microglia colonization
    (39, 547),   # Schaffenrath BBB heterogeneity
    (38, 550),   # Jones meningeal fibroblast
    (15, 563),   # Tarashansky SAMap
    (22, 563),   # Jiang CACIMAR
    (33, 579),   # CZ CELLxGENE (Data Availability)
    (34, 579),   # Liberzon MSigDB
]

# Uncited references (21=PAML4, 23=Tan microglial heterogeneity)
# Placed at end in original order
uncited = [21, 23]  # PAML 4, Tan microglial heterogeneity

# Build old→new mapping
new_num = 1
mapping = {}
for old, _line in first_appearance:
    mapping[old] = new_num
    new_num += 1
for old in uncited:
    mapping[old] = new_num
    new_num += 1

assert len(mapping) == 41, f"Expected 41 entries, got {len(mapping)}"
assert set(mapping.keys()) == set(range(1, 42)), "Missing reference numbers"

print("Mapping (old → new):")
for old in sorted(mapping.keys()):
    print(f"  {old:2d} → {mapping[old]:2d}")

# ============================================================
# Read source file
# ============================================================
with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open(BACKUP, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\nBackup saved: {BACKUP}")

# ============================================================
# Step 1: Replace all citation numbers with unique placeholders
# Pattern: (N) or (N,M) or (N,M,O) — but only where N,M,O are pure
# integer strings that match our mapping keys.
# ============================================================

def replace_citations_with_placeholders(m):
    """Replace (N,M,...) with (__R_N__,__R_M__,...)"""
    inner = m.group(1)
    parts = [p.strip() for p in inner.split(',')]
    new_parts = []
    for p in parts:
        try:
            n = int(p)
            if n in mapping:
                new_parts.append(f'__R_{n}__')
            else:
                new_parts.append(p)
        except ValueError:
            new_parts.append(p)
    return '(' + ','.join(new_parts) + ')'

# Match (digits optionally comma-separated) — only pure digit groups
citation_pattern = r'\((\d+(?:\s*,\s*\d+)*)\)'
content = re.sub(citation_pattern, replace_citations_with_placeholders, content)

# Count replacements
placeholder_count = len(re.findall(r'__R_\d+__', content))
print(f"Placeholders inserted: {placeholder_count}")

# ============================================================
# Step 2: Replace placeholders with new citation numbers
# ============================================================
for old, new in mapping.items():
    content = content.replace(f'__R_{old}__', str(new))

# Verify no placeholders remain
remaining = re.findall(r'__R_\d+__', content)
if remaining:
    print(f"WARNING: {len(remaining)} unhandled placeholders: {remaining}")
else:
    print("All placeholders resolved.")

# ============================================================
# Step 3: Reorder _refs_nar list
# ============================================================
# Find the _refs_nar list in the file
refs_start = None
refs_end = None
lines = content.split('\n')

for i, line in enumerate(lines):
    if line.strip() == '_refs_nar = [':
        refs_start = i
    elif refs_start is not None and line.strip() == ']':
        refs_end = i
        break

if refs_start is None or refs_end is None:
    print("ERROR: Could not find _refs_nar list!")
    sys.exit(1)

print(f"_refs_nar list: lines {refs_start+1}-{refs_end+1}")

# Extract reference entries
ref_lines = lines[refs_start+1:refs_end]
ref_entries = []
current = []
in_string = False
for line in ref_lines:
    stripped = line.strip()
    if stripped.startswith("'"):
        # Start or middle of a string
        if current:
            # Continuing previous string (shouldn't happen in our format)
            current.append(line.rstrip())
        else:
            current.append(line.rstrip())
    elif current:
        # Continuation line
        current.append(line.rstrip())
    
    # Check if string ends on this line
    full = ' '.join([c.strip() for c in current]) if current else ''
    if current and ("'," in line or "'" in line and line.rstrip().endswith("',")):
        # End of entry
        ref_entries.append('\n'.join(current))
        current = []
    elif current and line.rstrip().endswith("'"):
        ref_entries.append('\n'.join(current))
        current = []

if current:
    ref_entries.append('\n'.join(current))

print(f"Extracted {len(ref_entries)} reference entries from _refs_nar")

if len(ref_entries) != 41:
    print(f"ERROR: Expected 41 entries, got {len(ref_entries)}")
    # Try alternative parsing
    # The references are single-line strings, so just count them
    single_lines = [l for l in ref_lines if l.strip().startswith("'")]
    print(f"Single-line entries: {len(single_lines)}")
    ref_entries = single_lines

# Build new order: entry at old_index (old_num-1) should be at new_index (new_num-1)
# new_index = mapping[old_num] - 1
# old_index = old_num - 1
new_refs = [None] * 41
for old_num in range(1, 42):
    old_idx = old_num - 1
    new_idx = mapping[old_num] - 1
    new_refs[new_idx] = ref_entries[old_idx]

assert all(r is not None for r in new_refs), "Some reference entries are missing"

# Rebuild the file content with reordered references
before_refs = '\n'.join(lines[:refs_start+1])
after_refs = '\n'.join(lines[refs_end:])
new_ref_block = '\n'.join(new_refs)

new_content = before_refs + '\n' + new_ref_block + '\n' + after_refs

# ============================================================
# Step 4: Write modified file
# ============================================================
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Modified file written: {OUT}")
print("\nDone! References renumbered by first citation order.")

# Print verification
print("\n=== Verification: key citation changes ===")
# Line 398 original: (16), (1), (2), (3), (32), (31) 
# Should now be: (1), (2), (3), (4), (5), (6)
print("Line ~398 (Introduction first paragraph):")
for i, line in enumerate(new_content.split('\n')):
    if "scVI" in line and "SATURN" in line:
        print(f"  L{i+1}: ...{line.strip()[:120]}...")
        break

print("\nLine ~404 (4 datasets intro):")
for i, line in enumerate(new_content.split('\n')):
    if "four scales" in line:
        print(f"  L{i+1}: ...{line.strip()[:120]}...")
        break
