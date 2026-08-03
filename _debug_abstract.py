import re
t = open(r'version3\CKI_NAR_Submission_v31\CKI_NAR_Manuscript_fulltext.txt', encoding='utf-8').read()
ab_m = re.search(r'Abstract\n(.+?)\n(?:Keywords|Introduction)', t, re.DOTALL)
ab = ab_m.group(1) if ab_m else ''
words = re.findall(r'\b\w+\b', ab)
print(f'Matched {len(words)} words')
print(f'First 80: {ab[:80]!r}')
print(f'Last 60: {ab[-60:]!r}')
print()
# Try alternative: capture only paragraph between Abstract and Keywords
lines = t.split('\n')
for i, line in enumerate(lines):
    if line.strip() == 'Abstract':
        next_line = lines[i+1] if i+1 < len(lines) else ''
        wc = len(re.findall(r'\b\w+\b', next_line))
        print(f'Line-based: Abstract is line {i}, next line has {wc} words')
        print(f'Next line[:100]: {next_line[:100]!r}')
        break
