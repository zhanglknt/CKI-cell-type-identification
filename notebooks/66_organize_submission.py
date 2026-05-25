"""
66_organize_submission.py — 整理NAR投稿材料到 NAR_Submission_Final_v2/
"""
import shutil, os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "results"
FIG = SRC / "figures_final"
DST = SRC / "NAR_Submission_Final_v2"

# ============================================================
# Step 1: 创建目录结构
# ============================================================
for d in [
    DST / "manuscript",
    DST / "cover_letter",
    DST / "supplementary",
    DST / "figures",
    DST / "extended_data",
    DST / "usage_guide",
    DST / "presentation",
]:
    d.mkdir(parents=True, exist_ok=True)
    print(f"[MKDIR] {d.relative_to(SRC)}")

# ============================================================
# Step 2: 复制投稿文档
# ============================================================
MANUSCRIPT_SRC = {
    SRC / "CKI_NAR_Manuscript_v4.docx": DST / "manuscript/CKI_NAR_Manuscript_v4.docx",
    SRC / "CKI_NAR_正文.docx": DST / "manuscript/CKI_NAR_正文.docx",
    SRC / "CKI_NAR_Cover_Letter.docx": DST / "cover_letter/CKI_NAR_Cover_Letter.docx",
    SRC / "CKI_NAR_投稿信.docx": DST / "cover_letter/CKI_NAR_投稿信.docx",
    SRC / "CKI_NAR_补充材料.docx": DST / "supplementary/CKI_NAR_Supplementary.docx",
}

for src, dst in MANUSCRIPT_SRC.items():
    if src.exists():
        if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy2(src, dst)
            print(f"[COPY] {dst.name}")
        else:
            print(f"[SKIP] {dst.name} (up to date)")

# ============================================================
# Step 3: 复制主图
# ============================================================
for f in sorted(FIG.glob("figure*.pdf")):
    if "ed_fig" not in f.name:
        dst = DST / "figures" / f.name
        shutil.copy2(f, dst)
        print(f"[COPY] figures/{f.name}")

# ============================================================
# Step 4: 复制扩展数据图
# ============================================================
for f in sorted(FIG.glob("ed_fig*.pdf")):
    dst = DST / "extended_data" / f.name
    shutil.copy2(f, dst)
    print(f"[COPY] extended_data/{f.name}")

# ============================================================
# Step 5: 复制使用指南
# ============================================================
for pattern in ["usage_guide_en.*", "usage_guide_zh.*"]:
    for f in sorted(FIG.glob(pattern)):
        dst = DST / "usage_guide" / f.name
        shutil.copy2(f, dst)
        print(f"[COPY] usage_guide/{f.name}")

# ============================================================
# Step 6: 复制讲座 PPTX
# ============================================================
for f in [FIG / "CKI_Lecture_2026_v4.pptx", FIG / "CKI_Lecture_2026_v4_ZH.pptx"]:
    if f.exists():
        dst = DST / "presentation" / f.name
        shutil.copy2(f, dst)
        print(f"[COPY] presentation/{f.name}")

# ============================================================
# Step 7: 清理 figures_final/ 中间文件
# ============================================================
CLEANUP_PATTERNS = [
    "CKI_Lecture_2026_v3*.pptx",           # v3 variants
    "_test_*.pptx",                          # test files
    "_test_*.svg",                           # test SVGs
    "_tmp_*",                                # temp files
    "_s15_baseline.html",                    # intermediate HTML
    "_s16_anomaly.html",
    "_s17_migration.html",
    "_s15_baseline.svg",                     # old SVGs (keep _v3)
    "_s16_anomaly.svg",
    "_s17_migration.svg",
    "_s2_cell_states.svg",
    "_s2_cell_states_en.svg",
    "_s2_cell_states_zh.svg",
    "_s15_baseline.png",                     # old PNGs (keep _v3)
    "_s15_baseline_v3.png",
    "_s16_anomaly.png",
    "_s17_migration.png",
    "_s2_cell_states.png",
    "_s2_cell_states_en.png",
    "_s2_cell_states_zh.png",
    "_s2_cell_states_zh_v2.png",             # old ZH PNG (now using unified EN v2)
    "_s15_wide.svg",
    "_s15_wide.png",
    "_s16_wide.svg",
    "_s16_wide.png",
    "_s17_migration_wide.svg",
    "_s17_wide.png",
    "_s17_brain.png",
    "_s17_brain_old.png",
    "_s17_brain_new.png",
    "_s17_brain_new.svg",
    "_tmp_brain.png",
]

removed = 0
for pattern in CLEANUP_PATTERNS:
    for f in FIG.glob(pattern):
        f.unlink()
        removed += 1
        print(f"[RM] {f.name}")

print(f"\n[DONE] {removed} intermediate files removed")

# ============================================================
# Step 8: 统计
# ============================================================
total_files = sum(1 for _ in DST.rglob("*") if _.is_file())
print(f"[STATS] NAR_Submission_Final_v2: {total_files} files total")
for d in sorted(DST.iterdir()):
    if d.is_dir():
        count = sum(1 for _ in d.glob("*") if _.is_file())
        print(f"  {d.name}/: {count} files")
