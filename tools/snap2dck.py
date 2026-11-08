#!/usr/bin/env python3
# snap2dck.py - a 48K Spectrum snapshot (.z80 or .sna) -> a TC2068 DOCK cartridge (.dck) for the TC2068 core.
#
#   python3 snap2dck.py GAME.z80 ROM [-o GAME.dck]
#
# ROM is a 16K Spectrum ROM: the 48K one or the TC2048 one. The cartridge has it in DOCK chunks 0-1, so the game
# sees a 48K Spectrum: its ROM calls, the ROM font and the IM 1 interrupt at 0038h all go to that ROM, unchanged.
# The game's 48K of RAM goes in DOCK chunks 2-7 (64K in all). It is an LROS: at reset the 2068 ROM reads 0001h-0004h
# of the DOCK (type 1, entry point, chunks 0-1 in the DOCK), and the entry point is a loader in the free area of the
# Spectrum ROM (386Eh-3CFFh in the 48K ROM). The loader copies each 8K of the game from a DOCK chunk into the HOME
# RAM (from a different chunk: chunk s holds RAM chunk s-1, chunk 2 holds RAM chunk 7), leaves chunks 0-1 in the
# DOCK, restores the registers and jumps to the game. RST 0 still gives the Spectrum's cold start: 0000h is a JP to
# a copy of the ROM's first 8 bytes, also in the free area (the JP's address is made of the LROS bytes 0001h-0002h).
#
# Not for 128K games, nor for games that need what the 2068 does differently (port FF is the SCLD's: a game that
# writes it changes the screen mode or the memory map, and reading it does not give the floating bus).
# The cartridges made with it hold the ROM: keep them to yourself.
# GPL v3, like the rest of the core. AI (Claude) used.

import argparse
import os
import sys

RAM_CHUNKS = [(2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 2)]   # (HOME RAM chunk, DOCK chunk that holds it)


def w16(d, i):
    return d[i] | d[i + 1] << 8


def unpack(data, size):
    """The .z80 compression: ED ED n b = n times b."""
    out = bytearray()
    i = 0
    while len(out) < size and i < len(data):
        if data[i] == 0xED and i + 3 < len(data) and data[i + 1] == 0xED:
            out += bytes([data[i + 3]]) * data[i + 2]
            i += 4
        else:
            out.append(data[i])
            i += 1
    if len(out) < size:
        raise SystemExit('short memory block in the .z80 (%d of %d bytes)' % (len(out), size))
    return out[:size]


def read_z80(d):
    r = {'a': d[0], 'f': d[1], 'bc': w16(d, 2), 'hl': w16(d, 4), 'pc': w16(d, 6), 'sp': w16(d, 8), 'i': d[10],
         'de': w16(d, 13), 'bc_': w16(d, 15), 'de_': w16(d, 17), 'hl_': w16(d, 19), 'a_': d[21], 'f_': d[22],
         'iy': w16(d, 23), 'ix': w16(d, 25), 'iff': d[27] != 0, 'im': d[29] & 3}
    b12 = 1 if d[12] == 255 else d[12]
    r['r'] = (d[11] & 0x7F) | (b12 & 1) << 7
    r['border'] = b12 >> 1 & 7
    if r['pc']:                                             # version 1: always 48K
        ram = unpack(d[30:], 49152) if b12 & 0x20 else bytearray(d[30:30 + 49152])
        if len(ram) != 49152:
            raise SystemExit('short .z80')
        return r, ram
    ext = w16(d, 30)
    r['pc'] = w16(d, 32)
    hw = d[34]
    ok = (0, 1) if ext == 23 else (0, 1, 3)
    if hw not in ok or d[37] & 0x80:
        raise SystemExit('not a 48K snapshot (.z80 machine type %d): only 48K games' % hw)
    ram = bytearray(49152)
    got = set()
    i = 32 + ext
    while i + 3 <= len(d):
        n, page = w16(d, i), d[i + 2]
        i += 3
        block = bytearray(d[i:i + 16384]) if n == 0xFFFF else unpack(d[i:i + n], 16384)
        i += 16384 if n == 0xFFFF else n
        off = {8: 0, 4: 0x4000, 5: 0x8000}.get(page)
        if off is not None:
            ram[off:off + 16384] = block
            got.add(page)
    if got != {4, 5, 8}:
        raise SystemExit('the .z80 lacks memory pages (has %s)' % sorted(got))
    return r, ram


def read_sna(d, rom):
    if len(d) != 49179:
        raise SystemExit('not a 48K .sna (%d bytes)' % len(d))
    r = {'i': d[0], 'hl_': w16(d, 1), 'de_': w16(d, 3), 'bc_': w16(d, 5), 'f_': d[7], 'a_': d[8],
         'hl': w16(d, 9), 'de': w16(d, 11), 'bc': w16(d, 13), 'iy': w16(d, 15), 'ix': w16(d, 17),
         'iff': bool(d[19] & 4), 'r': d[20], 'f': d[21], 'a': d[22], 'sp': w16(d, 23), 'im': d[25] & 3,
         'border': d[26] & 7}
    ram = bytearray(d[27:])
    mem = lambda a: rom[a] if a < 0x4000 else ram[a - 0x4000]      # PC is on the stack (RETN)
    r['pc'] = mem(r['sp']) | mem((r['sp'] + 1) & 0xFFFF) << 8
    r['sp'] = (r['sp'] + 2) & 0xFFFF
    return r, ram


def loader(r, org):
    """The LROS entry point: copy the game into the HOME RAM, then its registers, then JP to it."""
    c = bytearray([0xF3, 0xAF, 0xD3, 0xFF])                # DI; XOR A; OUT (FF),A: the DOCK, normal screen
    for ram, dock in RAM_CHUNKS:
        c += bytes([0x3E, 3 | 1 << dock, 0xD3, 0xF4,         # LD A,hsr; OUT (F4),A: chunks 0, 1 and the source
                    0x21, 0, dock * 0x20, 0x11, 0, ram * 0x20, 0x01, 0, 0x20, 0xED, 0xB0])   # LDIR 8K
    c += bytes([0x3E, 3, 0xD3, 0xF4,                        # the Spectrum ROM at 0000-3FFF, RAM at 4000-FFFF
                0x3E, r['border'], 0xD3, 0xFE,
                0x3E, r['i'], 0xED, 0x47,                   # LD I,A
                0xED, {0: 0x46, 1: 0x56, 2: 0x5E}.get(r['im'], 0x56)])   # IM 0/1/2
    regs = len(c) + 28
    c += bytes([0x31, (org + regs) & 0xFF, (org + regs) >> 8,   # LD SP,regs: they are popped from here
                0xC1, 0xD1, 0xE1, 0xD9,                     # BC' DE' HL'
                0xF1, 0x08,                                 # AF'
                0xDD, 0xE1, 0xFD, 0xE1,                     # IX IY
                0xC1, 0xD1, 0xE1,                           # BC DE HL
                0x3E, ((r['r'] - 4) & 0x7F) | (r['r'] & 0x80), 0xED, 0x4F,   # R: 4 opcodes to go
                0xF1,                                       # AF
                0x31, r['sp'] & 0xFF, r['sp'] >> 8,
                0xFB if r['iff'] else 0xF3,
                0xC3, r['pc'] & 0xFF, r['pc'] >> 8])
    assert len(c) == regs
    for v in (r['bc_'], r['de_'], r['hl_'], r['f_'] | r['a_'] << 8, r['ix'], r['iy'],
              r['bc'], r['de'], r['hl'], r['f'] | r['a'] << 8):
        c += bytes([v & 0xFF, v >> 8])
    return c


def free(rom, a, n):
    return 0x2000 <= a and a + n <= 0x4000 and all(b == 0xFF for b in rom[a:a + n])


def cartridge(r, ram, rom):
    rom = bytearray(rom)
    first8 = rom[0:8]
    size = len(loader(r, 0))
    # 0000h: JP (the LROS bytes 0001h-0002h) = JP L*256+1, where the ROM's first 8 bytes go; the entry is H*256+L
    for lo in [0x39] + list(range(0x20, 0x40)):
        for hi in [0x3A] + list(range(0x20, 0x40)):
            fix, entry = lo << 8 | 1, hi << 8 | lo
            if free(rom, fix, 8) and free(rom, entry, size) and (entry + size <= fix or fix + 8 <= entry):
                break
        else:
            continue
        break
    else:
        raise SystemExit('this ROM has no free area (FFh bytes) for the loader')
    rom[fix:fix + 8] = first8
    rom[entry:entry + size] = loader(r, entry)
    rom[0:5] = bytes([0xC3, 0x01, lo, hi, 0xFC])            # JP fix / LROS: type 1, entry, chunks 0-1 in the DOCK
    dock = [rom[0:0x2000], rom[0x2000:0x4000]] + [None] * 6
    for home, d in RAM_CHUNKS:
        dock[d] = ram[(home - 2) * 0x2000:(home - 1) * 0x2000]
    out = bytearray([0] + [2] * 8)                          # bank 0 (DOCK): 8 ROM chunks with images
    for c in dock:
        out += c
    return out, entry, fix


def main():
    p = argparse.ArgumentParser(description='48K snapshot (.z80/.sna) -> TC2068 DOCK cartridge (.dck)')
    p.add_argument('snapshot')
    p.add_argument('rom', help='16K Spectrum ROM (48K or TC2048)')
    p.add_argument('-o', '--output')
    a = p.parse_args()
    d = open(a.snapshot, 'rb').read()
    rom = open(a.rom, 'rb').read()
    if len(rom) != 16384:
        raise SystemExit('the ROM must have 16384 bytes (it has %d)' % len(rom))
    if rom[0:8] != bytes.fromhex('F3AF11FFFFC3CB11'):
        raise SystemExit('this does not look like a Spectrum ROM (it does not start F3 AF 11 FF FF C3 CB 11)')
    r, ram = read_sna(d, rom) if a.snapshot.lower().endswith('.sna') else read_z80(d)
    out, entry, fix = cartridge(r, ram, rom)
    name = a.output or os.path.splitext(a.snapshot)[0] + '.dck'
    open(name, 'wb').write(out)
    print('%s: PC=%04X SP=%04X IM %d %s, loader at %04X; %d bytes' %
          (name, r['pc'], r['sp'], r['im'], 'EI' if r['iff'] else 'DI', entry, len(out)))


if __name__ == '__main__':
    main()
