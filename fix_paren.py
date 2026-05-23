import re

with open('generate_supplementary_v2.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    stripped = line.rstrip()
    # If line ends with '))' and contains add_para, remove one trailing )
    if stripped.endswith('))') and 'add_para(' in stripped:
        line = stripped[:-1] + '\n'  # remove one )
    new_lines.append(line)

with open('generate_supplementary_v2.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Fixed trailing double-paren on add_para lines')
