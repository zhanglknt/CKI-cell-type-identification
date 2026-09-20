# -*- coding: utf-8 -*-
"""v47.3 四项修复（用户 2026-09-15 指令）:
  1) 方案A: Abstract 改单段非结构化 ~155 词；Keywords 独立行（Arial 11 左对齐）
  2) Skinnider/Augur ref: 补第 6 作者 Matson KJE（对齐其余 6 作者+et al. 规则）
  3) Methods 'Reproducibility Guide, Section 1.3' -> 'Section 1.1'（环境在 1.1）
  4) 附图图注移到 'Additional file 1: Supplementary figure legends' 标题下
     （原来标题下为空、图注在 References 之后）
镜像同步 + py_compile + 词数断言
"""
import io, re, shutil, py_compile

ROOT = r"C:/Users/KnightZ/Desktop/细胞受选择"
GEN = ROOT + "/generate_manuscript_gb.py"
src = io.open(GEN, encoding="utf-8").read()

# ---------- 1) Abstract 非结构化 + Keywords 独立行 ----------
ab_start = src.find("# ABSTRACT (structured: Background / Results / Conclusions, <=250 words - GB)")
assert ab_start > 0
# 块从其上的 '# ===' 分隔线开始
blk_start = src.rfind("# ==========", 0, ab_start)
# 结束锚: KEYWORDS 块的 run.font.size = Pt(10)
kw_i = src.find("run.font.size = Pt(10)", ab_start)
assert kw_i > 0
blk_end = kw_i + len("run.font.size = Pt(10)")
old_block = src[blk_start:blk_end]
assert "ab('Background'" in old_block and "Keywords:" in old_block

NEW_ABSTRACT = (
    "Standard distance metrics conflate baseline variation with functional "
    "adaptation in single-cell genomics. Inspired by the Ka/Ks ratio, CKI "
    "decomposes divergence into a baseline rate k_n (housekeeping genes) and "
    "a functional rate k_f (identity genes); \\u03c9 = k_f/k_n quantifies "
    "baseline-normalized functional divergence. In ground-truth simulation, "
    "\\u03c9 rejected neutral housekeeping drift (false-positive rate 0.00, "
    "versus 0.55\\u20130.58 for raw JS and cosine; no anchoring artifact) and "
    "ranked first for functional-versus-neutral discrimination (AUC = 0.80), "
    "with power bounded to ~50\\u2013200 cells per donor per condition. We "
    "evaluated CKI on mouse, human, pan-cancer (TCGA; exploratory), and brain "
    "datasets: calibration fixed an equivalent-population baseline "
    "(\\u03c9 = 7.70, 95% CI [7.37, 8.02]), and brain analysis revealed a "
    "6.10-fold regional gradient across ten non-neuronal classes\\u2014an "
    "uncorrected upper bound inflated by class-size imbalance (equal-n "
    "downsampling: 1.74 [1.64, 1.84]). Per-pair gene selection inflates k_f "
    "(median 1.6-fold) yet preserves rankings. CKI is freely available as an "
    "open-source Python package."
)
# 词数（渲染后文本）
rendered = NEW_ABSTRACT.replace("\\u03c9", "\u03c9").replace("\\u2013", "\u2013").replace("\\u2014", "\u2014")
wc = len([w for w in rendered.split() if re.search(r"[A-Za-z0-9\u03c9~]", w)])
assert 120 <= wc <= 165, "abstract word count %d out of range" % wc
for anchor in ["raw JS and cosine", "no anchoring artifact", "1.74 [1.64, 1.84]",
               "~50\\u2013200 cells per donor per condition", "We evaluated CKI",
               "ground-truth simulation", "gene selection inflates",
               "uncorrected upper bound", "7.70, 95% CI"]:
    assert anchor in NEW_ABSTRACT, "missing anchor: " + anchor

new_block = (
    "# ============================================================\n"
    "# ABSTRACT (GB Methodology: unstructured, single paragraph, ~" + str(wc) + " words)\n"
    "# ============================================================\n"
    "heading('Abstract', level=1)\n"
    "\n"
    "p('" + NEW_ABSTRACT + "')\n"
    "\n"
    "# ============================================================\n"
    "# KEYWORDS (GB: 3-10 keywords, independent line after the abstract)\n"
    "# ============================================================\n"
    "kw = doc.add_paragraph()\n"
    "run = kw.add_run('Keywords: cell-state divergence, housekeeping genes, "
    "Jensen-Shannon decomposition, baseline-normalized divergence, "
    "single-cell genomics')\n"
    "run.font.name = 'Arial'\n"
    "set_black(run)\n"
    "run.font.size = Pt(11)"
)
src = src[:blk_start] + new_block + src[blk_end:]

# ---------- 2) Skinnider ref: 5 -> 6 authors ----------
old_ski = "Skinnider MA, Squair JW, Kathe C, Anderson MA, Gautier M, et al. Cell type prioritization in single-cell data."
new_ski = "Skinnider MA, Squair JW, Kathe C, Anderson MA, Gautier M, Matson KJE, et al. Cell type prioritization in single-cell data."
assert src.count(old_ski) == 1, "Skinnider ref anchor count %d" % src.count(old_ski)
src = src.replace(old_ski, new_ski)

# ---------- 3) Section 1.3 -> 1.1 ----------
assert src.count("Section 1.3") == 1, "Section 1.3 count %d" % src.count("Section 1.3")
src = src.replace("Section 1.3", "Section 1.1")

# ---------- 4) 图注移到 legends 标题下 ----------
lines = src.split("\n")
h_idx = next(i for i, l in enumerate(lines)
             if l.strip() == "heading('Additional file 1: Supplementary figure legends', level=1)")
first_leg = next(i for i, l in enumerate(lines)
                 if l.startswith("p('Additional file 1: Figure S1."))
save_idx = next(i for i, l in enumerate(lines) if l.startswith("# == Save =="))
assert h_idx < first_leg < save_idx
# legend 块（去掉尾部空行）
leg_block = lines[first_leg:save_idx]
while leg_block and leg_block[-1].strip() == "":
    leg_block.pop()
assert len(leg_block) == 25, "legend block lines = %d (expect 13 p() + 12 blanks)" % len(leg_block)
assert sum(1 for l in leg_block if l.startswith("p('Additional file 1: Figure S")) == 13
# 删除原位置
del lines[first_leg:save_idx]
# 删除标题与 References 注释块之间的空行填充
ref_cmt = next(i for i, l in enumerate(lines) if l.startswith("# REFERENCES (GB: Vancouver"))
ref_blk_start = ref_cmt - 1  # 其上的 '# ====' 行
while lines[ref_blk_start - 1].strip() == "":
    ref_blk_start -= 1
# 移除 heading 之后到 References 注释块之间的所有旧行（空填充）
del lines[h_idx + 1: ref_blk_start]
# 在标题后插入图注块
inserted = [""] + leg_block + [""]
lines[h_idx + 1:h_idx + 1] = inserted
src = "\n".join(lines)

# 校验顺序: legends heading -> Figure S1 -> ... S13 -> References heading
m_h = src.find("heading('Additional file 1: Supplementary figure legends', level=1)")
m_s1 = src.find("p('Additional file 1: Figure S1.")
m_s13 = src.find("p('Additional file 1: Figure S13.")
m_refs = src.find("heading('References', level=1)")
assert m_h < m_s1 < m_s13 < m_refs, (m_h, m_s1, m_s13, m_refs)

# ---------- 写回 + 镜像 + 自检 ----------
io.open(GEN, "w", encoding="utf-8", newline="").write(src)
shutil.copyfile(GEN, ROOT + "/CKI_Reproducibility_Package/generate_manuscript_gb.py")
py_compile.compile(GEN, doraise=True)
py_compile.compile(ROOT + "/CKI_Reproducibility_Package/generate_manuscript_gb.py", doraise=True)
print("OK: abstract %d words unstructured; keywords independent; Matson KJE added;" % wc)
print("    Section 1.1 fix; 13 legends moved under AF1 legends heading (before References)")
