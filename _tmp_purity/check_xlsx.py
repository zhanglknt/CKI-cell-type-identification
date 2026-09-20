# -*- coding: utf-8 -*-
p = r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/ncomms3612-s2.xlsx"
d = open(p, "rb").read()
out = []
out.append(f"size={len(d)}")
out.append(f"first_bytes={d[:8].hex()}")
out.append(f"is_zip={d[:2] == b'PK'}")
if not d[:2] == b"PK":
    out.append("preview:")
    out.append(d[:500].decode("utf-8", errors="replace"))
with open(r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/check_xlsx.txt", "w") as f:
    f.write("\n".join(out))
