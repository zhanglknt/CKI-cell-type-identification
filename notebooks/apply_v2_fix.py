"""
Step 1: Insert add_panel_label() helper after rcParams (after line 98, 0-indexed 97).
Step 2: Fix savefig function (remove bbox_inches='tight').
Step 3: Fix 8 known bad panel label lines.
Output: 30_nar_figures_final_v2.py
"""
with open(r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks\30_nar_figures_final.py", 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original: {len(lines)} lines")

# ============================================================
# Step 1: Insert add_panel_label() after line 98 (0-indexed 97)
# ============================================================
helper = '''\
# ============================================================
# Helper: consistent panel label (ALL figures use this)
# ============================================================
def add_panel_label(ax, letter, col_pos='left'):
    """
    col_pos: 'left'   -> x=-0.18 (leftmost column panels)
              'center' -> x=-0.05 (center column panels)
              'right'  -> x=-0.05 (rightmost column panels)
    ALL use y=1.02 for HORIZONTAL ALIGNMENT across rows.
    """
    x = -0.18 if col_pos == 'left' else -0.05
    ax.text(x, 1.02, f'({letter})', fontweight='bold', fontsize=10,
            transform=ax.transAxes, va='bottom', ha='left',
            fontfamily='Arial')

'''

# Insert after line 98 (0-indexed 97 = line 98 in 1-indexed)
# lines[97] = "})\n"
insert_idx = 98  # after line 98 (0-indexed)
lines.insert(insert_idx, helper)
print(f"[Step 1] add_panel_label() helper inserted after line 98 (now at line {insert_idx+1})")
print(f"         New total: {len(lines)} lines")

# ============================================================
# Step 2: Fix savefig function (remove bbox_inches='tight')
# ============================================================
content = ''.join(lines)

old_savefig = '''def savefig(name, width, height):
    """Save as PNG + PDF with NAR-compliant settings."""
    plt.tight_layout(pad=0.5)
    plt.savefig(OUT_DIR / f'{name}.png', dpi=DPI,
                bbox_inches='tight', facecolor='white')
    plt.savefig(OUT_DIR / f'{name}.pdf', dpi=DPI,
                bbox_inches='tight', facecolor='white',
                metadata={'Creator': 'CKI NAR Figures'})
    print(f'  saved: {name}.png / .pdf')
    plt.close()'''

new_savefig = '''def savefig(name, width, height):
    """Save as PNG + PDF — NO bbox_inches='tight' (exact NAR size)."""
    fig = plt.gcf()
    fig.savefig(OUT_DIR / f'{name}.png', dpi=DPI, facecolor='white')
    fig.savefig(OUT_DIR / f'{name}.pdf', dpi=DPI, facecolor='white',
                metadata={'Creator': 'CKI NAR Figures v2'})
    print(f'  saved: {name}.png / .pdf')
    plt.close(fig)'''

if old_savefig in content:
    content = content.replace(old_savefig, new_savefig)
    print("[Step 2] savefig function fixed (removed bbox_inches='tight')")
else:
    print("[Step 2] WARNING: savefig pattern NOT found!")

# ============================================================
# Step 3: Fix known bad panel label lines
# ============================================================
replacements = [
    # (old_string, new_string)
    # Fig1 Panel A: (-0.03, 1.05) -> use helper
    ("""axA.text(-0.03, 1.05, 'A', fontweight='bold', fontsize=9,
         transform=axA.transAxes, va='bottom', ha='left')""",
     "add_panel_label(axA, 'A', col_pos='left')"),
    # Fig1 Panel B: (-0.03, 1.05) -> use helper
    ("""axB.text(-0.03, 1.05, 'B', fontweight='bold', fontsize=9,
         transform=axB.transAxes, va='bottom', ha='left')""",
     "add_panel_label(axB, 'B', col_pos='left')"),
    # Fig1 Panel C: (-0.12, 1.06) -> use helper (center)
    ("""axC.text(-0.12, 1.06, 'C', transform=axC.transAxes,
         fontsize=9, fontweight='bold', va='bottom', ha='left', clip_on=False)""",
     "add_panel_label(axC, 'C', col_pos='center')"),
    # Fig1 Panel D: (-0.12, 1.06) -> use helper (center)
    ("""axD.text(-0.12, 1.06, 'D', transform=axD.transAxes,
         fontsize=9, fontweight='bold', va='bottom', ha='left', clip_on=False)""",
     "add_panel_label(axD, 'D', col_pos='center')"),
    # Fig1 Panel E: (-0.12, 1.04) -> use helper (right)
    ("""axE.text(-0.12, 1.04, 'E', transform=axE.transAxes,
         fontsize=9, fontweight='bold', va='bottom', ha='left', clip_on=False)""",
     "add_panel_label(axE, 'E', col_pos='right')"),
    # Fig5 Panel B: (-1.5, 1.05) -> USE HELPER! (was WAY OFF)
    ("""axB.text(-1.5, 1.05, '(B)', fontweight='bold', fontsize=10, transform=axB.transAxes)""",
     "add_panel_label(axB, 'B', col_pos='center')"),
    # ED Fig3: fontsize=9 -> 10 (use helper)
    ("""    ax.text(-0.2, 1.02, f'({chr(65+i)})', fontweight='bold', fontsize=9, transform=ax.transAxes)""",
     "    add_panel_label(ax, chr(65+i), col_pos='left')  # ED Fig3"),
    # ED Fig6 Panel E: y=1.0 -> y=1.02 (use helper)
    ("""axE.text(-0.15, 1.0, '(E)', fontweight='bold', fontsize=10, transform=axE.transAxes)""",
     "add_panel_label(axE, 'E', col_pos='right')"),
]

done = 0
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        done += 1
        print(f"  [Step 3.{done}] Patched: {old[:60].replace(chr(10), ' ')}...")
    else:
        print(f"  [Step 3] SKIP (not found): {old[:60].replace(chr(10), ' ')}...")

print(f"\n[Step 3] Total: {done}/{len(replacements)} panel label replacements")

# ============================================================
# Step 4: Add panel labels to ED Fig4 and ED Fig5 (were missing)
# ============================================================
# ED Fig4: single-panel figure, add (A) label before savefig
ed4_marker = "plt.savefig(OUT_DIR / 'ed_fig4_method_comparison_auc.png'"
if ed4_marker in content and 'add_panel_label(ax, 'A'' not in content[content.find('ED Figure 4'):content.find('ED Figure 5')]:
    # Find position before ed4_marker
    pos = content.find(ed4_marker)
    # Find preceding newline
    insert_pos = content.rfind('\n', 0, pos) + 1
    label_line = '\n# Panel label\nadd_panel_label(ax, 'A', col_pos='left')\n'
    content = content[:insert_pos] + label_line + content[insert_pos:]
    print("[Step 4] Panel label added to ED Fig4")
else:
    print("[Step 4] ED Fig4 already has panel label (or skipped)")

# ED Fig5: single-panel table figure, add (A) label
ed5_marker = "plt.savefig(OUT_DIR / 'ed_fig5_cross_organ_table.png'"
if ed5_marker in content and 'add_panel_label' not in content[content.find('ED Figure 5'):content.find('ED Figure 6')]:
    pos = content.find(ed5_marker)
    insert_pos = content.rfind('\n', 0, pos) + 1
    label_line = '\n# Panel label\nadd_panel_label(ax, 'A', col_pos='center')\n'
    content = content[:insert_pos] + label_line + content[insert_pos:]
    print("[Step 4] Panel label added to ED Fig5")
else:
    print("[Step 4] ED Fig5 already has panel label (or skipped)")

# ============================================================
# Step 5: Remove ALL remaining bbox_inches='tight' from savefig calls
#          (ED Fig4 and ED Fig5 have SEPARATE savefig calls)
# ============================================================
import re
# Remove bbox_inches='tight' kwarg from ALL savefig calls
# Pattern: , bbox_inches='tight' [optional closing ]
old_pattern = r""",\s*bbox_inches\s*=\s*'tight'\s*""")
content = re.sub(old_pattern, '', content)
print("[Step 5] All bbox_inches='tight' removed from savefig calls")

# Also remove plt.tight_layout(pad=0.5) from savefig
content = content.replace('    plt.tight_layout(pad=0.5)\n', '')
print("[Step 5] plt.tight_layout(pad=0.5) removed from savefig")

# ============================================================
# Write output
# ============================================================
dst = r"C:\Users\KnightZ\Desktop\细胞受选择\notebooks\30_nar_figures_final_v2.py"
with open(dst, 'w', encoding='utf-8') as f:
    f.write(content)

n_lines = content.count('\n')
print(f"\nDone! Output: {dst}")
print(f"New: {len(content)} chars, {n_lines} lines")

# ============================================================
# Syntax check
# ============================================================
try:
    compile(content, dst, 'exec')
    print("\nSyntax check: PASSED ✓")
except SyntaxError as e:
    print(f"\nSyntax check: FAILED ✗")
    print(f"  Line {e.lineno}: {e.msg}")
    print(f"  Text: {e.text.rstrip()}")
