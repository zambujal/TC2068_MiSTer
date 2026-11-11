# faz_ficheiros.py: teste_timex.bin (A000h) e cartucho.bin -> teste_timex.tap, teste_timex.dck e teste_timex.sna
import struct
code = open('teste_timex.bin', 'rb').read()
# TAP: 10 CLEAR 40959: LOAD "" CODE: RANDOMIZE USR 40960
T = {'CLEAR': 0xFD, 'LOAD': 0xEF, 'CODE': 0xAF, 'RANDOMIZE': 0xF9, 'USR': 0xC0}
def num(n): return str(n).encode() + bytes([0x0E, 0, 0, n & 255, n >> 8, 0])
def linha(nr, partes):
    b = b''
    for p in partes:
        if isinstance(p, int): b += num(p)
        elif p in T: b += bytes([T[p]])
        else: b += p.encode()
    b += b'\x0d'
    return struct.pack('>H', nr) + struct.pack('<H', len(b)) + b
prog = linha(10, ['CLEAR', 40959, ':', 'LOAD', '""', 'CODE', ':', 'RANDOMIZE', 'USR', 40960])
def bloco(flag, data):
    b = bytes([flag]) + data; x = 0
    for c in b: x ^= c
    return struct.pack('<H', len(b) + 1) + b + bytes([x])
def cab(tipo, nome, ln, p1, p2): return bloco(0, bytes([tipo]) + nome.ljust(10).encode() + struct.pack('<HHH', ln, p1, p2))
open('teste_timex.tap', 'wb').write(cab(0, 'testetimex', len(prog), 10, len(prog)) + bloco(0xFF, prog) +
                                    cab(3, 'testetimex', len(code), 0xA000, 0x8000) + bloco(0xFF, code))
# DCK: banco 0 (DOCK), so' o bloco 4, ROM
c = open('cartucho.bin', 'rb').read(); assert len(c) == 8192
open('teste_timex.dck', 'wb').write(bytes([0, 0, 0, 0, 0, 2, 0, 0, 0]) + c)
# SNA de 48K: o programa em A000h; o PC (A000h) na pilha em FDFEh
ram = bytearray(49152)
ram[0x1800:0x1B00] = b'\x38' * 0x300                    # atributos: preto em branco
ram[0xA000 - 0x4000:0xA000 - 0x4000 + len(code)] = code
ram[0xFDFE - 0x4000] = 0x00; ram[0xFDFF - 0x4000] = 0xA0
# I, HL' DE' BC' AF', HL DE BC IY IX, IFF2, R, AF, SP, IM, borda
hdr = bytes([0x3F]) + bytes(8) + bytes(6) + bytes(4) + bytes([0]) + bytes([0]) + bytes(2) + struct.pack('<H', 0xFDFE) + bytes([1, 7])
assert len(hdr) == 27, len(hdr)
open('teste_timex.sna', 'wb').write(hdr + ram)
print('tap/dck/sna feitos; codigo', len(code), 'bytes')
