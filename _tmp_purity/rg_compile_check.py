# -*- coding: utf-8 -*-
import py_compile
files = [
    r"C:/Users/KnightZ/Desktop/细胞受选择/notebooks/06_phase34_tcga.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/notebooks/06_phase34_v2.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/notebooks/07_phase34_clinical.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/notebooks/08a_tcga_bootstrap.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/notebooks/08a_tcga_permutation.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/notebooks/83_kf_only_ordering.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/notebooks/85_tcga_linear_norm_v44.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/CKI_Reproducibility_Package/notebooks/06_phase34_v2.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/CKI_Reproducibility_Package/notebooks/07_phase34_clinical.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/CKI_Reproducibility_Package/notebooks/08a_tcga_bootstrap.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/CKI_Reproducibility_Package/notebooks/83_kf_only_ordering.py",
    r"C:/Users/KnightZ/Desktop/细胞受选择/CKI_Reproducibility_Package/notebooks/85_tcga_linear_norm_v44.py",
]
out = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
        # also verify RG no longer maps to KIRC and still maps to LIHC
        src = open(f, encoding="utf-8").read()
        rg_kirc = '"RG": "TCGA-KIRC"' in src or '"RG":"TCGA-KIRC"' in src
        rg_lihc = '"RG": "TCGA-LIHC"' in src or '"RG":"TCGA-LIHC"' in src
        out.append(f"OK {f.split('/')[-2]}/{f.split('/')[-1]}: RG->KIRC={rg_kirc}, RG->LIHC={rg_lihc}")
    except Exception as e:
        out.append(f"FAIL {f}: {e}")
open(r"C:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/rg_compile_check.txt", "w").write("\n".join(out))
