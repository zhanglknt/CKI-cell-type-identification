# -*- coding: utf-8 -*-
d = open(r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/ncomms3612-s2.xlsx", "rb").read()
open(r"c:/Users/KnightZ/Desktop/细胞受选择/_tmp_purity/interstitial.txt", "w", encoding="utf-8", errors="replace").write(d.decode("utf-8", errors="replace"))
