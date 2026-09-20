#!/usr/bin/env python3
"""
Convert all 40 references from Vancouver to NAR format.
NAR format: Author,A.B., Author,C.D. and Author,E.F. (Year) Title. *Journal.*, **Vol**, Pages.
- Journal in italics, Volume in bold
- Max 20 authors, then et al.
- Year in parentheses after last author
- Corporate/consortium authors spelled out
"""
import re
import subprocess
from lxml import etree

XML_PATH = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\unpacked_v12\manuscript\word\document.xml"
OUTPUT = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\v12_docx\CKI_NAR_Manuscript.docx"
UNPACKED = r"C:\Users\KnightZ\Desktop\细胞受选择\version3\unpacked_v12\manuscript"
PACK_SCRIPT = r"C:\Users\KnightZ\.workbuddy\plugins\marketplaces\codebuddy-plugins-official\plugins\docx\scripts\office\pack.py"
PYTHON = r"C:\Users\KnightZ\AppData\Local\Programs\Python\Python312\python.exe"

NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

# Known consortium/corporate author abbreviations
CONSORTIUM_EXPAND = {
    'Cancer Genome Atlas Research N': 'Cancer Genome Atlas Research Network',
    'Cancer Genome Atlas N': 'Cancer Genome Atlas Network',
    'Tabula Muris C': 'Tabula Muris Consortium',
    'Tabula Sapiens C': 'Tabula Sapiens Consortium',
}

# ============================================================
# Author name conversion
# ============================================================

def convert_author(name):
    """Convert 'Last AB' to 'Last,A.B.' Handle consortium names."""
    name = name.strip()
    
    # Check consortium expansions (case-insensitive match)
    for abbr, full in CONSORTIUM_EXPAND.items():
        if name.lower() == abbr.lower():
            return full
    
    # Normal author: 'Last AB' or 'Last A'
    parts = name.rsplit(' ', 1)
    if len(parts) == 2:
        last, initials = parts
        # Only convert if initials look like person initials (1-3 uppercase letters)
        if (initials.isalpha() and initials.upper() == initials 
            and len(initials) <= 3 and len(last) > 1):
            initials_fmt = '.'.join(list(initials)) + '.'
            return last + ',' + initials_fmt
    return name

def parse_authors(author_str):
    """Parse 'Author AB, Author CD and Author EF et al.' into NAR-formatted list."""
    has_et_al = False
    author_str = author_str.strip()
    
    # Remove trailing 'et al.' or 'et al'
    for pat in [' et al.', ' et al']:
        if author_str.endswith(pat):
            has_et_al = True
            author_str = author_str[:-len(pat)]
            break
    
    # Split by ' and ' for the last author
    if ' and ' in author_str:
        parts_before, last_author = author_str.rsplit(' and ', 1)
        authors = [a.strip() for a in parts_before.split(',') if a.strip()]
        if last_author.strip():
            authors.append(last_author.strip())
    else:
        authors = [a.strip() for a in author_str.split(',') if a.strip()]
    
    # Convert each author
    nar_authors = [convert_author(a) for a in authors if a]
    
    if has_et_al:
        nar_authors.append('et al.')
    
    return nar_authors

def format_nar_authors(authors):
    """Format authors for NAR: no 'and' before et al."""
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    
    # Check if last element is 'et al.'
    if authors[-1] == 'et al.':
        if len(authors) == 2:
            return authors[0] + ' et al.'
        else:
            return ', '.join(authors[:-1]) + ' et al.'
    else:
        if len(authors) == 2:
            return authors[0] + ' and ' + authors[1]
        else:
            return ', '.join(authors[:-1]) + ' and ' + authors[-1]


# ============================================================
# Vancouver reference parser
# ============================================================

def parse_vancouver_ref(ref_text):
    """Parse a Vancouver-format reference into components."""
    ref_text = re.sub(r'^\d+[\t. ]+', '', ref_text).strip()
    
    result = {
        'authors_raw': '', 'authors_nar': [], 'year': '', 'title': '',
        'journal': '', 'volume': '', 'pages': '', 'doi': '', 'is_book': False
    }
    
    # Extract DOI URL
    doi_match = re.search(r'https?://doi\.org/\S+', ref_text)
    if doi_match:
        result['doi'] = doi_match.group(0).rstrip('.')
        ref_text = ref_text[:doi_match.start()].strip()
    
    # Book check
    if ('University Press' in ref_text or 
        re.search(r'Press,\s*\w+,\s*\d{4}', ref_text)):
        result['is_book'] = True
        year_match = re.search(r',\s*(\d{4})\.?\s*$', ref_text)
        if year_match:
            result['year'] = year_match.group(1)
            ref_text = ref_text[:year_match.start()].strip()
        parts = ref_text.split('. ')
        if len(parts) >= 3:
            result['authors_nar'] = parse_authors(parts[0])
            result['title'] = '. '.join(parts[1:-1])
            result['journal'] = parts[-1]
        return result
    
    # Journal article: "Author AB et al. Title. Journal Year;Vol:Pages."
    # Journal name can contain: letters, space, &, -, accented chars, digits
    journal_match = re.search(
        r'\.\s+([A-Za-z &\-\u00C0-\u024F0-9]+)\s+(\d{4});(.+?):(.+?)\.?\s*$', ref_text)
    
    if not journal_match:
        print(f"  NO JOURNAL MATCH: [{ref_text[:120]}]")
        result['authors_raw'] = ref_text
        return result
    
    result['journal'] = journal_match.group(1).strip()
    result['year'] = journal_match.group(2)
    result['volume'] = journal_match.group(3).strip()
    result['pages'] = journal_match.group(4).strip().rstrip('.')
    before_journal = ref_text[:journal_match.start()].strip()
    
    # Parse authors + title from before_journal
    if 'et al.' in before_journal:
        idx = before_journal.rfind('et al.')
        authors_str = before_journal[:idx + len('et al.')].rstrip('.')
        title = before_journal[idx + len('et al.'):].strip().lstrip('.').strip()
    else:
        # No et al. - split on last ". " separating authors from title
        parts = before_journal.rsplit('. ', 1)
        if len(parts) == 2:
            authors_str = parts[0].strip()
            title = parts[1].strip()
        else:
            authors_str = before_journal
            title = ''
    
    result['authors_nar'] = parse_authors(authors_str)
    result['title'] = title.strip().rstrip('.')
    
    return result


# ============================================================
# XML paragraph builder with formatting
# ============================================================

def build_nar_paragraph(parsed):
    """Build an XML paragraph for NAR-format reference with proper formatting.
    
    Format: Authors (Year) Title. *Journal*, **Vol**, Pages. DOI
    """
    p_elem = etree.Element(f'{{{NS}}}p')
    pPr = etree.SubElement(p_elem, f'{{{NS}}}pPr')
    
    # --- Authors + Year + Title (plain text) ---
    prefix_parts = []
    prefix_parts.append(format_nar_authors(parsed['authors_nar']))
    if parsed['year']:
        prefix_parts.append('(' + parsed['year'] + ')')
    if parsed['title']:
        prefix_parts.append(parsed['title'] + '.')
    
    prefix = ' '.join(prefix_parts)
    
    if prefix:
        r = etree.SubElement(p_elem, f'{{{NS}}}r')
        rPr = etree.SubElement(r, f'{{{NS}}}rPr')
        t = etree.SubElement(r, f'{{{NS}}}t')
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = prefix
    
    if parsed['is_book']:
        # Book: Publisher info in italics
        if parsed['journal']:
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = ' '
            
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            etree.SubElement(rPr, f'{{{NS}}}i')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = parsed['journal'] + '.'
        
        if parsed['doi']:
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = ' ' + parsed['doi']
    else:
        # Journal article: *Journal*, **Vol**, Pages. DOI
        if parsed['journal']:
            # Space before journal
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = ' '
            
            # Journal in italics
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            etree.SubElement(rPr, f'{{{NS}}}i')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = parsed['journal']
            
            # Comma
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = ', '
        
        if parsed['volume']:
            # Volume in bold
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            etree.SubElement(rPr, f'{{{NS}}}b')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = parsed['volume']
            
            # Comma
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = ', '
        
        if parsed['pages']:
            # Pages + period
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = parsed['pages'] + '.'
        
        if parsed['doi']:
            # DOI
            r = etree.SubElement(p_elem, f'{{{NS}}}r')
            rPr = etree.SubElement(r, f'{{{NS}}}rPr')
            t = etree.SubElement(r, f'{{{NS}}}t')
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = ' ' + parsed['doi']
    
    return p_elem


# ============================================================
# Main
# ============================================================

def main():
    print("Reading document XML...")
    with open(XML_PATH, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    tree = etree.fromstring(xml_content.encode())
    body = tree.find(f'{{{NS}}}body')
    
    # Find reference section
    all_paras = list(body.iter(f'{{{NS}}}p'))
    ref_paras = []
    ref_texts = []
    in_refs = False
    
    for para in all_paras:
        texts = []
        for t in para.iter(f'{{{NS}}}t'):
            if t.text:
                texts.append(t.text)
        full_text = ''.join(texts).strip()
        
        if full_text in ('References', 'REFERENCES'):
            in_refs = True
            continue
        
        if not in_refs:
            continue
        
        # Check if it's a numbered reference
        if full_text and re.match(r'^\d+[\t. ]', full_text):
            ref_paras.append(para)
            ref_texts.append(full_text)
        elif full_text and not full_text[0].isdigit():
            # Non-reference content after refs (e.g. Data Availability)
            break
    
    print(f"Found {len(ref_paras)} reference paragraphs")
    
    if len(ref_paras) != 40:
        print(f"WARNING: Expected 40 refs, found {len(ref_paras)}")
    
    # Parse and convert each reference
    conversions = 0
    errors = 0
    
    for i, (para, ref_text) in enumerate(zip(ref_paras, ref_texts)):
        ref_num = i + 1
        print(f"\n--- Ref {ref_num} ---")
        print(f"  Vancouver: {ref_text[:120]}...")
        
        try:
            parsed = parse_vancouver_ref(ref_text)
            
            # Debug output
            authors_nar = format_nar_authors(parsed['authors_nar'])
            print(f"  NAR:       {authors_nar} ({parsed['year']}) {parsed['title'][:60]}...")
            
            # Build new XML paragraph and replace old one
            new_para = build_nar_paragraph(parsed)
            parent = para.getparent()
            parent.replace(para, new_para)
            conversions += 1
            
        except Exception as e:
            print(f"  ERROR parsing ref {ref_num}: {e}")
            import traceback
            traceback.print_exc()
            errors += 1
    
    print(f"\n{conversions}/{len(ref_paras)} references converted ({errors} errors)")
    
    # Write modified XML
    xml_out = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    with open(XML_PATH, 'wb') as f:
        f.write(xml_out)
    
    print("XML written. Repacking DOCX...")
    
    # Repack DOCX
    result = subprocess.run(
        [PYTHON, PACK_SCRIPT, UNPACKED, OUTPUT],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:500])
    
    print(f"\nDone! Output: {OUTPUT}")


if __name__ == '__main__':
    main()
