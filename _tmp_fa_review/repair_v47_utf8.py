# repair_v47_utf8.py -- byte-level repair of GBK-mangled chars in 99_build_gb_v47.py
# Mechanism: the Edit tool round-trips files through GBK (cp936); chars whose
# GBK byte-pairing breaks (--, approx, ge, minus, sup4) had the 3rd UTF-8 byte
# replaced with '?' (0x3F). All repairs are 3-byte -> 3-byte, in-place, so
# offsets never drift. Every replacement is guarded by a prefix assertion.
from pathlib import Path
import re
import py_compile

P47 = Path(r'C:/Users/KnightZ/Desktop/细胞受选择/99_build_gb_v47.py')
P46 = Path(r'C:/Users/KnightZ/Desktop/细胞受选择/99_build_gb_v46.py')

EM = b'\xe2\x80\x94'     # U+2014 em dash
APPROX = b'\xe2\x89\x88'  # U+2248 almost-equal
GE = b'\xe2\x89\xa5'      # U+2265 greater-or-equal
MINUS = b'\xe2\x88\x92'   # U+2212 minus sign
SUP4 = b'\xe2\x81\xb4'    # U+2074 superscript four

REPAIRS = {
    3700: EM,      # docstring: drift -- omega FPR
    4094: EM,      # docstring: primary -- vs omega
    20583: APPROX,  # regex: preserve only ~3%|approx 0.03
    24030: GE,     # label: CL old '>=2-fold shifts'
    90993: MINUS,   # regex: minus0.36 to minus0.46 (1st)
    91009: MINUS,   # regex: minus0.36 to minus0.46 (2nd)
    95659: SUP4,    # regex: 10[sup-4].*sup4
    102010: EM,    # docstring: coverage --
    145018: EM,    # docstring: drift -- omega
    145206: EM,    # docstring: primary -- omega
    154707: EM,    # docstring: 0.98 -- the anchor
    156105: EM,    # docstring: 2.27 -- replaces
    158497: EM,    # docstring: per cancer) -- composition
    167727: EM,    # docstring: 6.4e-13) -- k_n CV
    173372: EM,    # banner: PASSED -- v47 (GB) FINAL
    173451: EM,    # banner: FAILURES -- review above
}

raw = bytearray(P47.read_bytes())
assert len(REPAIRS) == 16, len(REPAIRS)
for off, orig in sorted(REPAIRS.items()):
    cur = bytes(raw[off:off + 3])
    assert cur[0] == 0xE2 and cur[1] == orig[1] and cur[2] == 0x3F, \
        (off, cur.hex(), orig.hex())
    raw[off:off + 3] = orig
    print(f'  fixed @{off}: {cur.hex()} -> {orig.hex()}')

out = bytes(raw)
txt = out.decode('utf-8')  # raises if still invalid anywhere
P47.write_bytes(out)
print('decode OK; wrote', len(out), 'bytes')

# residual mangled pattern scan (any lead-byte + '?' tail)
assert not re.search(rb'[\xe0-\xef][\x80-\xbf]\x3f', out), 'residual mangled!'
print('no residual mangled sequences')

print('U+2500 count:', txt.count(chr(0x2500)), '(expect 46)')
t46 = P46.read_text(encoding='utf-8')
print('U+2014 count v47:', txt.count(chr(0x2014)),
      '| v46:', t46.count(chr(0x2014)))
print('U+2248 v47:', txt.count(chr(0x2248)), '| v46:', t46.count(chr(0x2248)))
print('U+2265 v47:', txt.count(chr(0x2265)), '| v46:', t46.count(chr(0x2265)))
print('U+2212 v47:', txt.count(chr(0x2212)), '| v46:', t46.count(chr(0x2212)))
print('U+2074 v47:', txt.count(chr(0x2074)), '| v46:', t46.count(chr(0x2074)))

for ln in t46.splitlines():
    if 'preserve only ~3%' in ln:
        print('v46 ref line:', repr(ln[:90]))
        break

py_compile.compile(str(P47), doraise=True)
print('py_compile OK')

# confirm the 9 earlier version-fix edits survived the repair
assert txt.count('MANIFEST_v47') >= 3, 'MANIFEST refs lost'
assert '"v0.5.0" in cl' in txt and '"cki:0.5.0" in _readme' in txt
assert '"releases/tag/v0.5.0" in _data_readme' in txt
assert "__version__ = \"0.5.0\"' in _pkg_init" in txt
assert 'v0\\.5\\.0|0\\.5\\.0' in txt
print('earlier version-fix edits intact')
print('ALL REPAIR CHECKS PASSED')
