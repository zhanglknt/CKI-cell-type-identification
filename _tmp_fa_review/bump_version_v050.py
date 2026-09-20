#!/usr/bin/env python3
"""v47 phase-1 version bump: v0.4.9 -> v0.5.0.

Keeps the MS Zenodo phase-1 line 'version DOI for v0.4.9:
10.5281/zenodo.22333850' untouched (updated in phase-2 after the
v0.5.0 Zenodo record is minted). Each replacement asserts a unique
match before writing; any failure aborts without writing.
"""
import io, os, sys

BASE = r"C:\Users\KnightZ\Desktop\细胞受选择"

# (file, [(old, new), ...])
EDITS = {
    "cki/__init__.py": [
        ('__version__ = "0.4.9"', '__version__ = "0.5.0"'),
    ],
    "pyproject.toml": [
        ('version = "0.4.9"', 'version = "0.5.0"'),
    ],
    "README.md": [
        ("docker build -t cki:0.4.9 .", "docker build -t cki:0.5.0 ."),
        ("docker run --rm cki:0.4.9", "docker run --rm cki:0.5.0"),
    ],
    "notebooks/68_gen_supplementary_en.py": [
        ("in the released cki package (v0.4.9), bootstrap_test()",
         "in the released cki package (v0.5.0), bootstrap_test()"),
        ("cki package (v0.4.9), the tested tail is selected",
         "cki package (v0.5.0), the tested tail is selected"),
    ],
    "generate_cover_letter_nar.py": [
        ("release tag v0.4.9", "release tag v0.5.0"),
    ],
    "notebooks/100_gen_reproducibility_docx.js": [
        ('Version: 0.4.9 (editable install from project root)',
         'Version: 0.5.0 (editable install from project root)'),
        ("Install CKI v0.4.9: pip install -e .",
         "Install CKI v0.5.0: pip install -e ."),
    ],
    "generate_manuscript_gb.py": [
        ("The CKI Python package (v0.4.9) and all analysis notebooks",
         "The CKI Python package (v0.5.0) and all analysis notebooks"),
        ("The CKI source code (v0.4.9) is publicly available",
         "The CKI source code (v0.5.0) is publicly available"),
        ("(tag v0.4.9) under the MIT License",
         "(tag v0.5.0) under the MIT License"),
        ("(tag v0.4.9) and are included in the Zenodo archive",
         "(tag v0.5.0) and are included in the Zenodo archive"),
        ("in package version 0.4.9. All \\u03c9 values reported here",
         "in package version 0.5.0. All \\u03c9 values reported here"),
    ],
}

def main():
    # phase-1 guard: the MS Zenodo line must stay on the v0.4.9 record
    ms_path = os.path.join(BASE, "generate_manuscript_gb.py")
    n_fail = 0
    for rel, pairs in EDITS.items():
        path = os.path.join(BASE, rel)
        src = io.open(path, encoding="utf-8", newline="").read()
        out = src
        for old, new in pairs:
            n = out.count(old)
            if n != 1:
                print(f"FAIL [{rel}]: expected 1 match, got {n}: {old[:60]!r}")
                n_fail += 1
                continue
            out = out.replace(old, new)
        if n_fail:
            print("ABORT: no files written")
            sys.exit(1)
        io.open(path, "w", encoding="utf-8", newline="").write(out)
        print(f"OK [{rel}]: {len(pairs)} replacements")

    ms = io.open(ms_path, encoding="utf-8", newline="").read()
    assert "version DOI for v0.4.9: 10.5281/zenodo.22333850" in ms, \
        "phase-1 Zenodo line must still cite the v0.4.9 record"
    assert "v0.4.9" in ms and ms.count("v0.4.9") == 1, \
        f"only the Zenodo line may keep v0.4.9 (got {ms.count('v0.4.9')})"
    print("OK: phase-1 version bump complete (MS Zenodo line kept on v0.4.9 record)")

if __name__ == "__main__":
    main()
