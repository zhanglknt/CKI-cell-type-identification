#!/usr/bin/env python3
"""
Fix NAR reference format in manuscript DOCX.
NAR format: journal name in italics, volume number in bold.
Example: Smith,A.B. (2025) Title. J. Abbrev., **53**, 1234-1245.

Correct parsing strategy:
  After ") ": find last two ', ' separators.
  - Journal = everything between ") " and the LAST ', ' (exclusive)
    WAIT: last ', ' is volume→pages. Second-to-last ', ' is journal→volume.
    So: 
      journal_end = position of second-to-last ', '
      volume_end = position of last ', '
      journal = after_year[:journal_end]
      volume  = after_year[journal_end+2 : volume_end]
      pages   = after_year[volume_end+2:]
    
  BUT: if journal name has no ', ' — then there's only 2 ', ' total.
  If journal name has internal ', ' — unlikely for NAR abbrev.
  
  Actually: in NAR references, the journal abbreviation is followed by a comma
  (no space before comma): "eLife, 6, e27041." or "Mol. Syst. Biol., 15, e8746."
  The ", " appears EXACTLY 2 times in the journal+volume+pages suffix:
    ... JOURNAL, VOLUME, PAGES.
    → 2 occurrences of ", "
  
  Journal name itself does NOT contain ", " (NAR uses abbreviated journal names without commas).
  So: count ", " in the suffix after the title period.
  
  Correct approach:
  1. Find title end: the ". " that precedes the journal (capital letter after ". ")
  2. After title end: split by ", " → should be exactly 3 parts: [journal, volume, pages]
  
  But step 1 is hard. Instead:
  
  SIMPLE + CORRECT: Find the suffix after ") " 
  From the RIGHT, find the last two ", ":
    pages  = text after last ", "
    volume = text between second-last ", " and last ", "
    journal = text between ") " and second-last ", "
"""

import zipfile
import re
import os
import shutil
from lxml import etree

DOCX = "results/NAR_Submission_Final_v2/manuscript/CKI_NAR_Manuscript_v4.docx"
DOCX_FIXED = "results/NAR_Submission_Final_v2/manuscript/CKI_NAR_Manuscript_v4_refs_fixed.docx"

NS_W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def unzip_docx(path, extract_to):
    if os.path.exists(extract_to):
        shutil.rmtree(extract_to)
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(path) as z:
        z.extractall(extract_to)
    return extract_to

def repack_docx(folder, output_path):
    if os.path.exists(output_path):
        os.remove(output_path)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            for file in files:
                full = os.path.join(root, file)
                arcname = os.path.relpath(full, folder).replace(os.sep, '/')
                z.write(full, arcname)

def make_run(text, italic=False, bold=False, size="18", color="000000"):
    """Create a w:r element with given text and formatting."""
    r = etree.SubElement(etree.Element('dummy'), f'{NS_W}r')
    rpr = etree.SubElement(r, f'{NS_W}rPr')
    rf = etree.SubElement(rpr, f'{NS_W}rFonts')
    rf.set(f'{NS_W}ascii', 'Arial')
    rf.set(f'{NS_W}hAnsi', 'Arial')
    if bold:
        etree.SubElement(rpr, f'{NS_W}b')
    else:
        b = etree.SubElement(rpr, f'{NS_W}b')
        b.set(f'{NS_W}val', '0')
    if italic:
        etree.SubElement(rpr, f'{NS_W}i')
    else:
        i = etree.SubElement(rpr, f'{NS_W}i')
        i.set(f'{NS_W}val', '0')
    col = etree.SubElement(rpr, f'{NS_W}color')
    col.set(f'{NS_W}val', color)
    sz = etree.SubElement(rpr, f'{NS_W}sz')
    sz.set(f'{NS_W}val', size)
    sz2 = etree.SubElement(rpr, f'{NS_W}szCs')
    sz2.set(f'{NS_W}val', size)
    t = etree.SubElement(r, f'{NS_W}t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return r


def parse_reference(full_text):
    """
    Parse a single NAR reference string.
    Returns (num_prefix, authors_year, title_dot, journal, volume, pages)
    or None if parsing fails.
    
    Format: "1. Authors (year) Title. Journal, Volume, Pages."
    
    Key insight: In NAR format, after the title (ending with '. '),
    the remaining suffix has exactly 2 ', ' separators:
      "Journal, Volume, Pages."
    So we find the TITLE END ('. '), then split the suffix by ', '.
    """
    # Step 1: Extract numeric prefix "1. "
    num_match = re.match(r'^(\d+\.\s+)', full_text)
    if not num_match:
        return None
    num_prefix = num_match.group(1)
    rest = full_text[num_match.end():]
    
    # Step 2: Find "(year) " to separate authors from title+journal
    year_match = re.search(r'\(\d{4}\) ', rest)
    if not year_match:
        return None
    
    authors_part = rest[:year_match.end()]  # "Authors (year) "
    after_year = rest[year_match.end():]
    
    # Step 3: Find the title end.
    # The title ends with a '. ' where what follows is the journal name.
    # The journal+volume+pages suffix has exactly 2 ", " separators.
    # 
    # Find all '. ' positions in after_year.
    # The correct one is the one after which the remaining text has exactly 2 ", ".
    #
    # Actually: the title is a sentence. It ends with '. '.
    # After that: "Journal, Volume, Pages." — exactly 2 ", "s.
    #
    # Find the SHORTEST suffix that has exactly 2 ", "s
    # → that suffix starts right after the title's '. '.
    
    # Find all positions of '. ' in after_year
    dot_positions = [m.start() for m in re.finditer(r'\.\s+', after_year)]
    
    # Also check '\. ' (period + space, not ellipsis)
    # Actually just use all '. ' occurrences
    
    title_end_pos = None
    for pos in dot_positions:
        suffix = after_year[pos+1:].lstrip()
        # Count ', ' in suffix
        comma_count = suffix.count(', ')
        if comma_count == 2:
            # This '. ' is the title end (the suffix is "Journal, V, P.")
            # Journal name may start with lowercase (e.g. "eLife")
            if len(suffix) > 0:
                title_end_pos = pos
                break
    
    if title_end_pos is None:
        # Fallback: just find the last '. ' before ", \d" pattern
        # Actually let's try: find the LAST '. ' and check if suffix has 2 ", "
        if dot_positions:
            for pos in reversed(dot_positions):
                suffix = after_year[pos+1:].lstrip()
                if suffix.count(', ') == 2 and len(suffix) > 0:
                    title_end_pos = pos
                    break
    
    if title_end_pos is None:
        # Last resort: just use rfind('. ') — may be wrong for some titles
        # but let's try with the comma count check on the full after_year
        # Actually let me just try: split after_year into title + jvp suffix
        # by finding ", " from the end
        pass
    
    if title_end_pos is None:
        print(f"  -> CANNOT FIND title end in: {after_year[:100]}")
        return None
    
    # title = after_year[:title_end_pos+1]  (includes '.')
    title_part = after_year[:title_end_pos+1]
    jvp_suffix = after_year[title_end_pos+2:].strip()
    
    # Split jvp_suffix by ', ' → [journal, volume, pages]
    jvp_parts = jvp_suffix.split(', ')
    if len(jvp_parts) != 3:
        print(f"  -> JVP split gave {len(jvp_parts)} parts (expected 3): {jvp_parts}")
        return None
    
    journal_part = jvp_parts[0]
    volume_part = jvp_parts[1]
    pages_part = jvp_parts[2]
    
    return {
        'num_prefix': num_prefix,
        'authors_year': authors_part,
        'title': title_part + ' ',   # title + space before journal
        'journal': journal_part,
        'volume': volume_part,
        'pages': pages_part,
    }


def build_formatted_runs(parsed):
    """
    Build list of w:r elements from parsed reference dict.
    NAR format: *Journal*, **Volume**, pages.
    """
    runs_data = [
        (parsed['num_prefix'], False, False),
        (parsed['authors_year'], False, False),
        (parsed['title'], False, False),
        (parsed['journal'], True, False),   # italic
        (', ', False, False),
        (parsed['volume'], False, True),    # bold
        (', ', False, False),
        (parsed['pages'], False, False),
    ]
    return [make_run(text, italic=i, bold=b) for text, i, b in runs_data if text]


def fix_references_in_xml(xml_path):
    """Fix all reference paragraphs in document.xml."""
    tree = etree.parse(xml_path)
    root = tree.getroot()
    
    paragraphs = root.findall('.//' + NS_W + 'p')
    
    in_references = False
    ref_count = 0
    fixed_count = 0
    
    for para in paragraphs:
        text_elems = para.findall('.//' + NS_W + 't')
        if not text_elems:
            continue
        para_text = ''.join(t.text or '' for t in text_elems)
        
        if 'References' in para_text:
            in_references = True
            continue
        
        if not in_references:
            continue
        
        # Check if this is a reference entry
        if not re.match(r'^\d+\.', para_text.strip()):
            # Might be a continuation paragraph (hanging indent) — skip for now
            continue
        
        ref_count += 1
        print(f"  Ref #{ref_count}: {para_text[:80]}...")
        
        # Parse the reference
        parsed = parse_reference(para_text)
        if parsed is None:
            print(f"    -> PARSE FAILED, skipping")
            continue
        
        # Build new runs
        new_runs = build_formatted_runs(parsed)
        
        # Remove all existing w:r from paragraph
        existing_runs = para.findall(NS_W + 'r')
        for r in existing_runs:
            para.remove(r)
        
        # Add new runs
        for r in new_runs:
            para.append(r)
        
        fixed_count += 1
        print(f"    -> OK: journal=*{parsed['journal']}*, vol=**{parsed['volume']}**")
    
    print(f"\nTotal: {ref_count} references found, {fixed_count} fixed")
    return tree


def main():
    print("=" * 60)
    print("Fixing NAR reference format (journal italic, volume bold)")
    print("=" * 60)
    
    print(f"\nInput:  {DOCX}")
    print(f"Output: {DOCX_FIXED}")
    
    # Unzip
    temp_dir = unzip_docx(DOCX, "temp_docx_refs")
    xml_path = os.path.join(temp_dir, 'word', 'document.xml')
    
    # Fix references
    tree = fix_references_in_xml(xml_path)
    
    # Write back XML with proper declaration
    tree.write(xml_path, xml_declaration=True, encoding='UTF-8', standalone='yes')
    
    # Repack
    repack_docx(temp_dir, DOCX_FIXED)
    
    # Back up original and replace
    backup = DOCX + '.bak'
    print(f"\nBacking up original to: {backup}")
    shutil.copy2(DOCX, backup)
    
    print(f"Copying fixed file to: {DOCX}")
    shutil.copy2(DOCX_FIXED, DOCX)
    
    # Also keep the _fixed version
    print(f"Fixed version also saved as: {DOCX_FIXED}")
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("\nDone!")


if __name__ == '__main__':
    main()
