# -*- coding: utf-8 -*-
"""
build_nc_guide.py — 由 100_gen_reproducibility_docx.js 生成 NC 命名版
100_gen_reproducibility_nc.js（复现指南 = Additional file 2，NC 命名）。

锚点断言：每个替换前先断言命中次数符合预期，任一不符即中止，不写文件。
Note 重编号采用占位符两步替换防循环。
"""
import re
import sys

ROOT = "C:/Users/KnightZ/Desktop/细胞受选择"
SRC = ROOT + "/notebooks/100_gen_reproducibility_docx.js"
DST = ROOT + "/notebooks/100_gen_reproducibility_nc.js"

# 旧 -> 新 Note 编号（team-lead 统一映射）
NOTE_MAP = {
    "3.12": 1, "3.21": 2, "3.5": 3, "3.20": 4, "3.22": 5,
    "3.15": 6, "3.13": 7, "5.2": 8, "3.16": 9, "3.17": 10,
    "3.14": 11, "4.6": 12, "5.1": 13, "3.23": 14, "3.6": 15,
    # 注：旧 3.11 不在此映射——经 team-lead/nc-sn 确认为正文未引用小节，
    # 按方案 B 不获 'Supplementary Note N' 编号，改为 SI 十进制小节引用（见下）。
}

# 指南正文中实际出现的 Note 引用锚点（断言用）
EXPECTED_NOTE_HITS = {
    "5.1": 1,    # 5.7e: 'Supplementary Note 5.1'
}

# 特殊引用：旧 Note 3.11 -> SI 十进制小节引用（team-lead 指定措辞）
NOTE_311_OLD = "Supplementary Note 3.11"
NOTE_311_NEW = ("Section 3.11 of the Supplementary Information "
                "(Parameter Justification)")

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("ANCHOR FAIL:", msg)
    return cond


def main():
    with open(SRC, encoding="utf-8") as f:
        s = f.read()
    log = []

    # ---------- 0. 输出路径与打印名 ----------
    check(s.count("results/CKI_Reproducibility_Guide.docx") == 1,
          "OUT path anchor")
    s = s.replace("results/CKI_Reproducibility_Guide.docx",
                  "results/CKI_Reproducibility_Guide_NC.docx")
    log.append("OUT -> results/CKI_Reproducibility_Guide_NC.docx (1)")

    # 头部注释期刊表述中立化（仅代码注释，不进正文）
    check(s.count("NAR-compliant DOCX") == 1, "header comment anchor")
    s = s.replace("NAR-compliant DOCX",
                  "Nature Communications-compliant DOCX")
    log.append("header comment: NAR-compliant -> Nature Communications-compliant (1)")

    # ---------- 1. Note 引用重编号（占位符两步） ----------
    # 1a. 特殊：旧 Note 3.11 -> SI 十进制小节引用（方案 B，无 Supplementary Note 编号）
    hits = s.count(NOTE_311_OLD)
    check(hits == 1, f"'{NOTE_311_OLD}': expected 1, found {hits}")
    s = s.replace(NOTE_311_OLD, NOTE_311_NEW)
    log.append(f"'{NOTE_311_OLD}' -> '{NOTE_311_NEW}' ({hits})")

    # 1b. 形式: 'Note X.X' / 'Supplementary Note X.X' / 'SN X.X' 统一为 'Supplementary Note N'
    total_note_refs = 0
    for old, new in NOTE_MAP.items():
        pat = re.compile(r"(?:Supplementary\s+)?Note\s+" + re.escape(old) + r"\b"
                         r"|SN\s+" + re.escape(old) + r"\b")
        hits = len(pat.findall(s))
        total_note_refs += hits
        exp = EXPECTED_NOTE_HITS.get(old, 0)
        check(hits == exp, f"Note {old}: expected {exp} hit(s), found {hits}")
        if hits:
            s = pat.sub(f"Supplementary Note @@{new}@@", s)
            log.append(f"Note {old} -> Supplementary Note {new} ({hits})")
    # 未映射的 Note X.X 残留必须为零
    leftover = re.findall(r"(?:Supplementary\s+)?Note\s+\d+\.\d+\b|SN\s+\d+\.\d+\b", s)
    check(not leftover, f"unmapped Note refs left: {leftover}")
    # 第二步：占位符 -> 最终编号
    s = re.sub(r"Supplementary Note @@(\d+)@@", r"Supplementary Note \1", s)

    # ---------- 2. 附图/附表命名 ----------
    # 顺序敏感：先 'Supplementary Fig. S'，再裸 'Fig. S'/'Figure S'，再 'Table S'
    rules = [
        (r"Supplementary Fig\. S(\d+)\b", r"Supplementary Fig. \1", 3,
         "Supplementary Fig. S -> Supplementary Fig."),
        (r"(?<!Supplementary )Fig\. S(\d+)\b", r"Supplementary Fig. \1", 1,
         "Fig. S -> Supplementary Fig."),
        (r"(?<!Supplementary )(?<!_)Figure S(\d+)\b", r"Supplementary Fig. \1", 0,
         "Figure S -> Supplementary Fig."),
        (r"Table S(\d+)\b", r"Supplementary Table \1", 0,
         "Table S -> Supplementary Table"),
        # 已为新式但写法不统一：'Supplementary Figure 1' -> 'Supplementary Fig. 1'
        (r"Supplementary Figure (\d+)\b", r"Supplementary Fig. \1", 1,
         "Supplementary Figure N -> Supplementary Fig. N"),
    ]
    for pat, rep, exp, desc in rules:
        hits = len(re.findall(pat, s))
        check(hits == exp, f"{desc}: expected {exp}, found {hits}")
        s = re.sub(pat, rep, s)
        if hits:
            log.append(f"{desc} ({hits})")

    # ---------- 3. Additional file ----------
    af1 = s.count("Additional file 1:")
    check(af1 == 0, f"'Additional file 1:' expected 0, found {af1}")
    s = s.replace("Additional file 1:", "Supplementary Information")
    af_any = len(re.findall(r"Additional file", s))
    check(af_any == 0, f"'Additional file' any form expected 0, found {af_any}")
    log.append("Additional file 1: none present (0); no self-reference to Additional file 2")

    # ---------- 4. 面板标签小写 ----------
    panel_rules = [
        ("Fig. 4A", "Fig. 4a", 1),
        ("Panel A over Panel B", "panel a over panel b", 1),
    ]
    for old, new, exp in panel_rules:
        hits = s.count(old)
        check(hits == exp, f"panel '{old}': expected {exp}, found {hits}")
        s = s.replace(old, new)
        if hits:
            log.append(f"panel '{old}' -> '{new}' ({hits})")
    check(not re.search(r"\([A-E]\)", s), "parenthesized panel labels (A)-(E) remain")

    # ---------- 5. 期刊表述 ----------
    gb = [m for m in re.findall(r"Genome Biology", s)]
    # 仅允许出现在真实脚本文件名 30_genome_biology_figures.py（小写，不匹配上式）
    check(len(gb) == 0, f"'Genome Biology' in prose: {len(gb)}")
    check(s.count("30_genome_biology_figures.py") == 1,
          "script filename 30_genome_biology_figures.py missing (must keep verbatim)")
    log.append("journal wording: no 'Genome Biology' prose; script filename kept verbatim")

    if failures:
        print(f"\nABORT: {len(failures)} anchor assertion(s) failed; no file written.")
        sys.exit(1)

    with open(DST, "w", encoding="utf-8") as f:
        f.write(s)
    print(f"WROTE {DST}")
    print(f"total note refs rewritten: {total_note_refs}")
    for line in log:
        print(" -", line)


if __name__ == "__main__":
    main()
