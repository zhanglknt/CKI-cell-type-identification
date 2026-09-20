# -*- coding: utf-8 -*-
# count abstract words precisely (from the p(...) string, minus the wrapper)
path = r'C:/Users/KnightZ/Desktop/细胞受选择/generate_manuscript_nc.py'
src = open(path, encoding='utf-8').read()
i = src.find("heading('Abstract', level=1)")
seg = src[i:i+4000]
import re
m = re.search(r"p\('(.+?)'\)", seg, re.S)
text = m.group(1)
# decode escapes for word counting
text_d = text.encode().decode('unicode_escape')
words = text_d.split()
print('Abstract word count (decoded):', len(words))
