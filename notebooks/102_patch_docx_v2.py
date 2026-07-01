#!/usr/bin/env python3
"""
Patch the regenerated DOCX with fixes from THIS round that might not be
in the JS script (which was edited in the previous round).
"""

import zipfile
import re
from pathlib import Path

DOCX = "C:/Users/KnightZ/Desktop/细胞受选择/results/CKI_Reproducibility_Guide.docx"
EXTRACT = "C:/Users/KnightZ/Desktop/细胞受选择/results/docx_patch_tmp/"

def patch_docx():
    # 1. Extract DOCX (zip format)
    with zipfile.ZipFile(DOCX, 'r') as z:
        z.extractall(EXTRACT)

    doc_path = Path(EXTRACT) / "word" / "document.xml"
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    patches = [
        # Fix 1: Siletti URL (if JS script still has old URL)
        (
            "https://github.com/linnarsson-lab/snRNA_brain_atlas",
            "https://github.com/linnarsson-lab/adult-human-brain"
        ),
        # Fix 2: "median omega" -> "mean omega" in Strong tier
        (
            "pair median omega &gt; 20",
            "pair mean omega &gt; 20"
        ),
        # Fix 3: Bootstrap description in Section 5.1
        (
            "B = 500 or 1000",
            "B = 500 for mouse pilot; B is not applicable to human/TCGA/brain"
        ),
        # Fix 4: Parameter table - Tabula Sapiens HK method
        (
            "detect (combined)Tabula Sapiens",
            "direct loadTabula Sapiens"
        ),
        # Fix 5: Parameter table - Tabula Sapiens HRT Atlas reference
        (
            "noTabula Sapiens",
            "yesTabula Sapiens"
        ),
    ]

    patched = content
    for old, new in patches:
        if old in patched:
            patched = patched.replace(old, new)
            print(f"  Patched: {old[:50]}...")

    # Write back
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(patched)

    # Re-zip
    with zipfile.ZipFile(DOCX, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(EXTRACT):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(EXTRACT)
                z.write(file_path, arcname)

    print(f"Patched: {DOCX}")

if __name__ == "__main__":
    import os
    patch_docx()
