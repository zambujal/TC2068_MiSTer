#!/usr/bin/env python3
# rom2mif.py: ROM files (joined in order) -> Quartus .mif of 8-bit words, padded with 00.
#   python3 tools/rom2mif.py <depth> <out.mif> <rom> [<rom>...]
# rtl/tc2068.mif: python3 tools/rom2mif.py 32768 rtl/tc2068.mif ts2068.rom   (HOME 16K + EXROM 8K)
import sys
depth, out, roms = int(sys.argv[1]), sys.argv[2], sys.argv[3:]
d = b''.join(open(r, 'rb').read() for r in roms)
if len(d) > depth:
    raise SystemExit('%d bytes, more than %d' % (len(d), depth))
with open(out, 'w') as f:
    f.write('DEPTH = %d;\nWIDTH = 8;\nADDRESS_RADIX = HEX;\nDATA_RADIX = HEX;\nCONTENT BEGIN\n' % depth)
    for a in range(0, len(d), 16):
        f.write('%04X: %s;\n' % (a, ' '.join('%02X' % b for b in d[a:a + 16])))
    if len(d) < depth:
        f.write('[%04X..%04X]: 00;\n' % (len(d), depth - 1))
    f.write('END;\n')
print('%s: %d bytes of ROM, depth %d' % (out, len(d), depth))
