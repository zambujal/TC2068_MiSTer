#!/usr/bin/env python3
# faz_vhd.py - the DivMMC card (a VHD) and boot1.rom for the TC2068 MiSTer core, from the esxDOS 0.8.9 package.
#
#   python faz_vhd.py                 a window (Windows: double-click the file)
#   python faz_vhd.py PACKAGE [-o FOLDER] [-s MB] [-e EXTRA_FOLDER]
#
# PACKAGE is the esxDOS 0.8.9 zip from esxdos.org, or the folder where it was unzipped. In FOLDER (by default a
# folder TC2068 next to the package) it writes:
#   boot1.rom      the ESXMMC.BIN of the package: the DivMMC ROM
#   esxdos089.vhd  a card image (MBR, one FAT32 partition) with the BIN, SYS and TMP folders of the package,
#                  and EXTRA_FOLDER if given (for example a folder of TAP files)
# Both go to games/TC2068 on the MiSTer SD card. In the core: F12 -> Load DivMMC -> esxdos089.vhd, then Ctrl+F11.
#
# Only Python 3 is needed (on Windows from python.org, with its tcl/tk for the window); nothing else.
# GPL v3, like the rest of the core. AI (Claude) used.

import argparse
import os
import random
import struct
import sys
import threading
import time
import zipfile

VERSAO = '1.0'

# ---------------------------------------------------------------------------------------------------- the texts
TEXTOS = {
    'pt': {
        'titulo': 'TC2068: o cartão do esxDOS (VHD)',
        'pacote': 'Pacote do esxDOS 0.8.9 (o zip de esxdos.org ou a pasta):',
        'zip': 'Zip...', 'pasta': 'Pasta...',
        'extra': 'Pasta extra para a VHD (opcional, por exemplo jogos em TAP):',
        'tamanho': 'Tamanho da VHD (MB):',
        'saida': 'Guardar em:',
        'fazer': 'Fazer', 'abrir': 'Abrir a pasta', 'fechar': 'Fechar',
        'falta_pacote': 'Escolha o pacote do esxDOS 0.8.9.',
        'nao_existe': 'Não encontrei {}',
        'lendo': 'A ler {}',
        'sem_sys': 'Não encontrei SYS/ESXDOS.SYS: não parece o pacote do esxDOS.',
        'sem_esxmmc': 'Não encontrei o ESXMMC.BIN no pacote.',
        'esxmmc_ok': 'ESXMMC.BIN: esxDOS 0.8.9 (o core corrige-o no TC2068).',
        'esxmmc_outro': 'AVISO: este ESXMMC.BIN não é o do esxDOS 0.8.9. No TC2068 o core só corrige o 0.8.9: '
                        'com este, o TC2068 fica sem esxDOS (as outras máquinas funcionam).',
        'sys_ok': 'SYS/ESXDOS.SYS: esxDOS 0.8.9.',
        'sys_outro': 'AVISO: o SYS/ESXDOS.SYS não é o do esxDOS 0.8.9; tem de ser da mesma versão do boot1.rom.',
        'ficheiros': '{} pastas e {} ficheiros para a VHD ({} KB).',
        'nao_cabe': 'Não cabe numa VHD de {} MB: escolha um tamanho maior.',
        'escrito': 'Escrito: {}',
        'feito': 'Feito. Copie o boot1.rom e o esxdos089.vhd para a pasta games/TC2068 do cartão do MiSTer.\n'
                 'No core TC2068: F12 -> Load DivMMC -> esxdos089.vhd, e depois Ctrl+F11.\n'
                 'Para pôr mais coisas na VHD (jogos, programas), use a pasta extra.',
        'erro': 'Erro: {}',
        'uso': 'Faz o boot1.rom e o esxdos089.vhd (o cartão da DivMMC) para o core TC2068 do MiSTer.',
        'a_pacote': 'o zip do esxDOS 0.8.9 de esxdos.org, ou a pasta onde foi descompactado',
        'a_saida': 'pasta onde escrever (por omissão: TC2068, ao lado do pacote)',
        'a_tamanho': 'tamanho da VHD em MB: 64, 128, 256, 512, 1024 ou 2048 (por omissão 128)',
        'a_extra': 'uma pasta a pôr também na VHD (por exemplo jogos)',
        'sem_janela': 'Não há tkinter para a janela; use a linha de comandos (python faz_vhd.py -h).',
    },
    'en': {
        'titulo': 'TC2068: the esxDOS card (VHD)',
        'pacote': 'esxDOS 0.8.9 package (the zip from esxdos.org, or its folder):',
        'zip': 'Zip...', 'pasta': 'Folder...',
        'extra': 'Extra folder for the VHD (optional, for example games as TAP):',
        'tamanho': 'VHD size (MB):',
        'saida': 'Save to:',
        'fazer': 'Make', 'abrir': 'Open the folder', 'fechar': 'Close',
        'falta_pacote': 'Choose the esxDOS 0.8.9 package.',
        'nao_existe': 'Not found: {}',
        'lendo': 'Reading {}',
        'sem_sys': 'SYS/ESXDOS.SYS not found: this does not look like the esxDOS package.',
        'sem_esxmmc': 'ESXMMC.BIN not found in the package.',
        'esxmmc_ok': 'ESXMMC.BIN: esxDOS 0.8.9 (the core patches it on the TC2068).',
        'esxmmc_outro': 'WARNING: this ESXMMC.BIN is not the esxDOS 0.8.9 one. On the TC2068 the core only patches '
                        '0.8.9: with this one the TC2068 has no esxDOS (the other machines work).',
        'sys_ok': 'SYS/ESXDOS.SYS: esxDOS 0.8.9.',
        'sys_outro': 'WARNING: SYS/ESXDOS.SYS is not the esxDOS 0.8.9 one; it must be the same version as boot1.rom.',
        'ficheiros': '{} folders and {} files for the VHD ({} KB).',
        'nao_cabe': 'It does not fit in a {} MB VHD: choose a bigger size.',
        'escrito': 'Written: {}',
        'feito': 'Done. Copy boot1.rom and esxdos089.vhd to the games/TC2068 folder of the MiSTer SD card.\n'
                 'In the TC2068 core: F12 -> Load DivMMC -> esxdos089.vhd, then Ctrl+F11.\n'
                 'To put more on the VHD (games, programs), use the extra folder.',
        'erro': 'Error: {}',
        'uso': 'Makes boot1.rom and esxdos089.vhd (the DivMMC card) for the TC2068 MiSTer core.',
        'a_pacote': 'the esxDOS 0.8.9 zip from esxdos.org, or the folder where it was unzipped',
        'a_saida': 'folder to write to (default: TC2068, next to the package)',
        'a_tamanho': 'VHD size in MB: 64, 128, 256, 512, 1024 or 2048 (default 128)',
        'a_extra': 'a folder to put on the VHD too (for example games)',
        'sem_janela': 'There is no tkinter for the window; use the command line (python faz_vhd.py -h).',
    },
}


def lingua():
    """'pt' on a Portuguese system, else 'en'."""
    try:
        if sys.platform == 'win32':
            import ctypes
            if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x16:   # LANG_PORTUGUESE
                return 'pt'
        import locale
        for v in (os.environ.get('LC_ALL'), os.environ.get('LC_MESSAGES'), os.environ.get('LANG'),
                  locale.getlocale()[0]):
            if v and v.lower().startswith(('pt', 'portuguese')):
                return 'pt'
    except Exception:
        pass
    return 'en'


T = TEXTOS[lingua()]


class Erro(Exception):
    pass


# ---------------------------------------------------------------------------------------------- the esxDOS check
# The bytes the core changes in esxDOS 0.8.9 on the TC2068 (ZX-Spectrum.sv, fw_tab and sys_tab): offset and the
# 0.8.9 value. If they are all there, it is 0.8.9.
ESXMMC_089 = {0x0175: 0xF4, 0x0176: 0x09, 0x0570: 0x64, 0x0571: 0x05, 0x06B8: 0x30, 0x06B9: 0x25,
              0x0C29: 0x30, 0x0C2A: 0x25, 0x0C2C: 0xC5, 0x0C2D: 0x16, 0x0C42: 0xB0, 0x0C43: 0x16,
              0x0C49: 0x6E, 0x0C4A: 0x0D, 0x0D0F: 0xC5, 0x0D10: 0x16, 0x0D5D: 0xFB, 0x0D5E: 0x19,
              0x0D69: 0x6E, 0x0D6A: 0x19, 0x0D79: 0x8B, 0x0D7A: 0x19, 0x0D80: 0xA7, 0x0D81: 0x11,
              0x0D83: 0xBF, 0x0D84: 0x16, 0x0DF3: 0x01, 0x0DF4: 0x16}
ESXDOS_SYS_089 = {0x0368: 0x81, 0x0369: 0x0F, 0x04C5: 0x48, 0x04C6: 0x20, 0x04DA: 0x48, 0x04DB: 0x20,
                  0x057F: 0x8C, 0x0580: 0x1C, 0x0586: 0xF1, 0x0587: 0x2B, 0x05A9: 0x48, 0x05AA: 0x20,
                  0x05BA: 0xF4, 0x05C2: 0x7D, 0x05C3: 0x1B}


def e_089(dados, tabela, tamanho=None):
    if tamanho is not None and len(dados) != tamanho:
        return False
    return all(a < len(dados) and dados[a] == v for a, v in tabela.items())


# ------------------------------------------------------------------------------------------ reading the package
def le_pacote(caminho):
    """{relative path with '/': bytes} and the set of folders, from a zip or a folder."""
    ficheiros, pastas = {}, set()
    if not os.path.exists(caminho):
        raise Erro(T['nao_existe'].format(caminho))
    if os.path.isdir(caminho):
        for raiz, dirs, nomes in os.walk(caminho):
            rel = os.path.relpath(raiz, caminho).replace(os.sep, '/')
            rel = '' if rel == '.' else rel + '/'
            for d in dirs:
                pastas.add(rel + d)
            for n in nomes:
                with open(os.path.join(raiz, n), 'rb') as f:
                    ficheiros[rel + n] = f.read()
    elif zipfile.is_zipfile(caminho):
        with zipfile.ZipFile(caminho) as z:
            for i in z.infolist():
                nome = i.filename.replace('\\', '/')
                if nome.startswith('__MACOSX/') or '/__MACOSX/' in nome:
                    continue
                partes = nome.rstrip('/').split('/')
                for k in range(1, len(partes)):
                    pastas.add('/'.join(partes[:k]))
                if i.is_dir():
                    pastas.add(nome.rstrip('/'))
                else:
                    ficheiros[nome] = z.read(i)
    else:
        raise Erro(T['falta_pacote'])
    return ficheiros, pastas


def acha_esxdos(ficheiros, pastas):
    """The package prefix (where BIN, SYS and TMP are) and the ESXMMC.BIN bytes."""
    fim = 'sys/esxdos.sys'
    prefixos = [p[:-len(fim)] for p in ficheiros if p.lower() == fim or p.lower().endswith('/' + fim)]
    if not prefixos:
        raise Erro(T['sem_sys'])
    prefixo = min(prefixos, key=len)
    esxmmc = [p for p in ficheiros if p.lower() == (prefixo + 'esxmmc.bin').lower()]
    if not esxmmc:
        esxmmc = sorted((p for p in ficheiros if p.lower().split('/')[-1] == 'esxmmc.bin'), key=len)
    if not esxmmc:
        raise Erro(T['sem_esxmmc'])
    return prefixo, ficheiros[esxmmc[0]]


class No:
    """A file (dados = bytes) or a folder (dados = None) of the card."""
    def __init__(self, nome, dados=None):
        self.nome, self.dados, self.filhos = nome, dados, []

    def pasta(self, nome):
        for f in self.filhos:
            if f.dados is None and f.nome.upper() == nome.upper():
                return f
        f = No(nome)
        self.filhos.append(f)
        return f


def arvore(ficheiros, pastas, prefixo, extra=None):
    raiz = No('')
    for topo in ('BIN', 'SYS', 'TMP'):
        raiz.pasta(topo)
    for p in sorted(pastas):
        if p.lower().startswith(prefixo.lower()):
            rel = p[len(prefixo):]
            if rel and rel.split('/')[0].upper() in ('BIN', 'SYS', 'TMP'):
                no = raiz
                for parte in rel.split('/'):
                    no = no.pasta(parte)
    for p, dados in sorted(ficheiros.items()):
        if not p.lower().startswith(prefixo.lower()):
            continue
        rel = p[len(prefixo):].split('/')
        if len(rel) < 2 or rel[0].upper() not in ('BIN', 'SYS', 'TMP'):
            continue
        no = raiz
        for parte in rel[:-1]:
            no = no.pasta(parte)
        no.filhos.append(No(rel[-1], dados))
    if extra:
        base = raiz.pasta(os.path.basename(os.path.normpath(extra)))
        for r, dirs, nomes in os.walk(extra):
            rel = os.path.relpath(r, extra)
            no = base
            if rel != '.':
                for parte in rel.split(os.sep):
                    no = no.pasta(parte)
            for d in dirs:
                no.pasta(d)
            for n in sorted(nomes):
                with open(os.path.join(r, n), 'rb') as f:
                    no.filhos.append(No(n, f.read()))
    return raiz


# -------------------------------------------------------------------------------------------------- FAT32 image
VALIDOS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&\'()-@^_`{}~')


def nome83(nome):
    """The 8.3 name (11 bytes) if the name fits in it (in capitals), else None."""
    n = nome.upper()
    if n.startswith('.') or n.count('.') > 1:
        return None
    base, _, ext = n.partition('.')
    if not base or len(base) > 8 or len(ext) > 3 or any(c not in VALIDOS for c in base + ext):
        return None
    return (base.ljust(8) + ext.ljust(3)).encode('ascii')


# the characters of a made-up short name: no ~ { | } ` (the 2068 ROM prints ~ as FREE, { | } as ON ERR, STICK,
# SOUND, and the Spectrum ROM prints ` as a pound sign)
SEGUROS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&\'()-@^_')


def curto(nome, usados):
    """A NAME_N.EXT short name for a long name (Windows uses NAME~N; ~ would show as FREE on the TC2068)."""
    limpo = lambda s: ''.join(c for c in s.upper() if c in SEGUROS)
    base, ponto, ext = nome.rpartition('.')
    if not ponto:
        base, ext = nome, ''
    base, ext = limpo(base) or 'FICH', limpo(ext)[:3]
    for n in range(1, 100000):
        sufixo = '_%d' % n
        s = (base[:8 - len(sufixo)] + sufixo).ljust(8) + ext.ljust(3)
        s = s.encode('ascii')
        if s not in usados:
            return s
    raise Erro('nomes')


def entradas_lfn(nome, curto11):
    """The long-name entries (VFAT) that go before the short entry, in disk order."""
    soma = 0
    for b in curto11:
        soma = ((((soma & 1) << 7) | (soma >> 1)) + b) & 0xFF
    b = nome.encode('utf-16-le')
    u = list(struct.unpack('<%dH' % (len(b) // 2), b))
    if len(u) % 13:
        u.append(0)
        u += [0xFFFF] * (-len(u) % 13)
    partes = [u[i:i + 13] for i in range(0, len(u), 13)]
    ents = []
    for i, p in enumerate(partes):
        e = bytearray(32)
        e[0] = (i + 1) | (0x40 if i == len(partes) - 1 else 0)
        struct.pack_into('<5H', e, 1, *p[0:5])
        e[11], e[12], e[13] = 0x0F, 0, soma
        struct.pack_into('<6H', e, 14, *p[5:11])
        struct.pack_into('<2H', e, 28, *p[11:13])
        ents.append(bytes(e))
    return list(reversed(ents))


def data_dos(t):
    lt = time.localtime(t)
    return ((lt.tm_hour << 11) | (lt.tm_min << 5) | (lt.tm_sec // 2),
            ((max(lt.tm_year, 1980) - 1980) << 9) | (lt.tm_mon << 5) | lt.tm_mday)


def entrada(nome11, atributo, cluster, tamanho, hora, data):
    return struct.pack('<11sBBBHHHHHHHI', nome11, atributo, 0, 0, hora, data, data, cluster >> 16,
                       hora, data, cluster & 0xFFFF, tamanho)


def chs(lba):
    c, h, s = lba // (255 * 63), (lba // 63) % 255, lba % 63 + 1
    if c > 1023:
        c, h, s = 1023, 254, 63
    return bytes([h, ((c >> 2) & 0xC0) | s, c & 0xFF])


def faz_imagem(raiz, caminho, mb, etiqueta='ESXDOS', log=print):
    if mb not in (64, 128, 256, 512, 1024, 2048):
        raise Erro('MB')
    setor = 512
    total = mb * 1024 * 1024 // setor
    inicio = 2048                                   # the partition starts at 1 MiB
    part = total - inicio
    spc = mb // 64                                  # sectors per cluster: always ~131000 clusters
    rsvd, nfats = 32, 2
    fatsz = -(-(part - rsvd) // ((256 * spc + nfats) // 2))
    dados0 = rsvd + nfats * fatsz
    nclus = (part - dados0) // spc
    if nclus < 65525:
        raise Erro('FAT32')
    tam_cluster = spc * setor
    fat = [0] * (nclus + 2)
    fat[0], fat[1] = 0x0FFFFFF8, 0x0FFFFFFF
    proximo = [2]

    def aloca(nbytes, minimo=0):
        n = max(minimo, -(-nbytes // tam_cluster))
        if n == 0:
            return 0
        c0 = proximo[0]
        if c0 + n - 2 > nclus:
            raise Erro(T['nao_cabe'].format(mb))
        for i in range(n - 1):
            fat[c0 + i] = c0 + i + 1
        fat[c0 + n - 1] = 0x0FFFFFFF
        proximo[0] += n
        return c0

    hora, data = data_dos(time.time())

    def prepara(no, e_raiz):                        # the short names and the size of a folder
        usados, no.ents = set(), []
        for f in sorted(no.filhos, key=lambda x: (x.dados is not None, x.nome.upper())):
            s, lfn = nome83(f.nome), []
            if s is None or s in usados:
                s = curto(f.nome, usados)
                lfn = entradas_lfn(f.nome, s)
            usados.add(s)
            no.ents.append((f, s, lfn))
        return 32 * (sum(1 + len(l) for _, _, l in no.ents) + 1)   # + the label (root) or ".." (+ "." below)

    raiz.cluster = aloca(prepara(raiz, True), 1)
    fila = [raiz]
    while fila:
        no = fila.pop(0)
        for f, _, _ in no.ents:
            if f.dados is None:
                f.cluster = aloca(prepara(f, False) + 32, 1)
                f.pai = no
                fila.append(f)
            else:
                f.cluster = aloca(len(f.dados))

    usados_cl = proximo[0] - 2
    with open(caminho, 'wb') as img:
        img.truncate(total * setor)

        def escreve_cluster(c, b):
            img.seek((inicio + dados0 + (c - 2) * spc) * setor)
            img.write(b)

        # MBR: one partition, FAT32 with LBA (0x0C)
        mbr = bytearray(512)
        struct.pack_into('<I', mbr, 440, random.getrandbits(32))
        mbr[446:462] = bytes([0x00]) + chs(inicio) + bytes([0x0C]) + chs(total - 1) + struct.pack('<II', inicio, part)
        mbr[510:512] = b'\x55\xAA'
        img.seek(0)
        img.write(mbr)

        # boot sector, FSInfo and their copies at 6 and 7
        bs = bytearray(512)
        bs[0:3], bs[3:11] = b'\xEB\x58\x90', b'MSWIN4.1'
        struct.pack_into('<HBHBHHBHHHII', bs, 11, setor, spc, rsvd, nfats, 0, 0, 0xF8, 0, 63, 255, inicio, part)
        struct.pack_into('<IHHIHH', bs, 36, fatsz, 0, 0, raiz.cluster, 1, 6)
        bs[64], bs[66] = 0x80, 0x29
        struct.pack_into('<I', bs, 67, random.getrandbits(32))
        bs[71:82] = etiqueta.upper().ljust(11)[:11].encode('ascii')
        bs[82:90] = b'FAT32   '
        bs[510:512] = b'\x55\xAA'
        fi = bytearray(512)
        struct.pack_into('<I', fi, 0, 0x41615252)
        struct.pack_into('<III', fi, 484, 0x61417272, nclus - usados_cl, proximo[0])
        struct.pack_into('<I', fi, 508, 0xAA550000)
        for s, b in ((0, bs), (1, fi), (6, bs), (7, fi)):
            img.seek((inicio + s) * setor)
            img.write(b)

        # the two FATs
        tab = struct.pack('<%dI' % len(fat), *fat)
        for k in range(nfats):
            img.seek((inicio + rsvd + k * fatsz) * setor)
            img.write(tab)

        # the folders and the files
        fila = [raiz]
        while fila:
            no = fila.pop(0)
            if no is raiz:
                ents = [entrada(etiqueta.upper().ljust(11)[:11].encode('ascii'), 0x08, 0, 0, hora, data)]
            else:
                pai = 0 if no.pai is raiz else no.pai.cluster
                ents = [entrada(b'.          ', 0x10, no.cluster, 0, hora, data),
                        entrada(b'..         ', 0x10, pai, 0, hora, data)]
            for f, s, lfn in no.ents:
                ents += lfn
                if f.dados is None:
                    ents.append(entrada(s, 0x10, f.cluster, 0, hora, data))
                    fila.append(f)
                else:
                    ents.append(entrada(s, 0x20, f.cluster, len(f.dados), hora, data))
                    if f.dados:
                        escreve_cluster(f.cluster, f.dados)
            escreve_cluster(no.cluster, b''.join(ents))
    return usados_cl * tam_cluster


# ------------------------------------------------------------------------------------------------------ the work
def conta(no):
    pastas = ficheiros = tamanho = 0
    for f in no.filhos:
        if f.dados is None:
            p, fi, t = conta(f)
            pastas, ficheiros, tamanho = pastas + 1 + p, ficheiros + fi, tamanho + t
        else:
            ficheiros, tamanho = ficheiros + 1, tamanho + len(f.dados)
    return pastas, ficheiros, tamanho


def constroi(pacote, saida=None, mb=128, extra=None, log=print):
    log(T['lendo'].format(pacote))
    ficheiros, pastas = le_pacote(pacote)
    prefixo, esxmmc = acha_esxdos(ficheiros, pastas)
    log(T['esxmmc_ok'] if e_089(esxmmc, ESXMMC_089, 8192) else T['esxmmc_outro'])
    sys_ = next(d for p, d in ficheiros.items() if p.lower() == (prefixo + 'sys/esxdos.sys').lower())
    log(T['sys_ok'] if e_089(sys_, ESXDOS_SYS_089) else T['sys_outro'])
    raiz = arvore(ficheiros, pastas, prefixo, extra)
    p, f, t = conta(raiz)
    log(T['ficheiros'].format(p, f, (t + 1023) // 1024))
    if not saida:
        saida = os.path.join(os.path.dirname(os.path.abspath(pacote)), 'TC2068')
    os.makedirs(saida, exist_ok=True)
    rom = os.path.join(saida, 'boot1.rom')
    with open(rom, 'wb') as r:
        r.write(esxmmc)
    log(T['escrito'].format(rom))
    vhd = os.path.join(saida, 'esxdos089.vhd')
    faz_imagem(raiz, vhd, mb, log=log)
    log(T['escrito'].format(vhd))
    log('')
    log(T['feito'])
    return saida


def linha_de_comandos(args):
    ap = argparse.ArgumentParser(description=T['uso'])
    ap.add_argument('pacote', help=T['a_pacote'])
    ap.add_argument('-o', '--saida', help=T['a_saida'])
    ap.add_argument('-s', '--tamanho', type=int, default=128, choices=(64, 128, 256, 512, 1024, 2048),
                    help=T['a_tamanho'])
    ap.add_argument('-e', '--extra', help=T['a_extra'])
    ap.add_argument('--version', action='version', version=VERSAO)
    a = ap.parse_args(args)
    try:
        constroi(a.pacote, a.saida, a.tamanho, a.extra)
    except Erro as e:
        print(T['erro'].format(e))
        return 1
    return 0


def janela():
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
    except ImportError:
        print(T['sem_janela'])
        return 1
    r = tk.Tk()
    r.title(T['titulo'])
    r.minsize(640, 420)
    pacote, extra, saida, tamanho = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(value='128')
    q = ttk.Frame(r, padding=12)
    q.pack(fill='both', expand=True)
    q.columnconfigure(0, weight=1)

    def escolhe_pacote(zip_):
        c = (filedialog.askopenfilename(filetypes=[('zip', '*.zip'), ('*', '*')]) if zip_
             else filedialog.askdirectory())
        if c:
            pacote.set(c)
            if not saida.get():
                saida.set(os.path.join(os.path.dirname(os.path.abspath(c)), 'TC2068'))

    def escolhe(var):
        c = filedialog.askdirectory()
        if c:
            var.set(c)

    ttk.Label(q, text=T['pacote']).grid(row=0, column=0, columnspan=3, sticky='w')
    ttk.Entry(q, textvariable=pacote).grid(row=1, column=0, sticky='ew', pady=(2, 8))
    ttk.Button(q, text=T['zip'], command=lambda: escolhe_pacote(True)).grid(row=1, column=1, padx=(6, 0), pady=(2, 8))
    ttk.Button(q, text=T['pasta'], command=lambda: escolhe_pacote(False)).grid(row=1, column=2, padx=(6, 0), pady=(2, 8))
    ttk.Label(q, text=T['extra']).grid(row=2, column=0, columnspan=3, sticky='w')
    ttk.Entry(q, textvariable=extra).grid(row=3, column=0, sticky='ew', pady=(2, 8))
    ttk.Button(q, text=T['pasta'], command=lambda: escolhe(extra)).grid(row=3, column=2, padx=(6, 0), pady=(2, 8))
    ttk.Label(q, text=T['saida']).grid(row=4, column=0, columnspan=3, sticky='w')
    ttk.Entry(q, textvariable=saida).grid(row=5, column=0, sticky='ew', pady=(2, 8))
    ttk.Button(q, text=T['pasta'], command=lambda: escolhe(saida)).grid(row=5, column=2, padx=(6, 0), pady=(2, 8))
    linha = ttk.Frame(q)
    linha.grid(row=6, column=0, columnspan=3, sticky='ew', pady=(0, 8))
    ttk.Label(linha, text=T['tamanho']).pack(side='left')
    ttk.Combobox(linha, textvariable=tamanho, width=6, state='readonly',
                 values=('64', '128', '256', '512', '1024', '2048')).pack(side='left', padx=(6, 0))
    botao = ttk.Button(linha, text=T['fazer'])
    botao.pack(side='right')
    abrir = ttk.Button(linha, text=T['abrir'], state='disabled')
    abrir.pack(side='right', padx=(0, 6))
    texto = tk.Text(q, height=10, wrap='word', state='disabled')
    texto.grid(row=7, column=0, columnspan=3, sticky='nsew')
    q.rowconfigure(7, weight=1)

    def escreve(s):
        texto.configure(state='normal')
        texto.insert('end', s + '\n')
        texto.see('end')
        texto.configure(state='disabled')

    def log(s):
        r.after(0, escreve, s)

    feito = {}

    def trabalho():
        try:
            feito['pasta'] = constroi(pacote.get(), saida.get() or None, int(tamanho.get()), extra.get() or None, log)
            r.after(0, lambda: (abrir.configure(state='normal'), messagebox.showinfo(T['titulo'], T['feito'])))
        except Exception as e:
            r.after(0, lambda: (escreve(T['erro'].format(e)), messagebox.showerror(T['titulo'], T['erro'].format(e))))
        finally:
            r.after(0, lambda: botao.configure(state='normal'))

    def fazer():
        if not pacote.get():
            messagebox.showwarning(T['titulo'], T['falta_pacote'])
            return
        botao.configure(state='disabled')
        abrir.configure(state='disabled')
        texto.configure(state='normal')
        texto.delete('1.0', 'end')
        texto.configure(state='disabled')
        threading.Thread(target=trabalho, daemon=True).start()

    def abre():
        p = feito.get('pasta')
        if not p:
            return
        if sys.platform == 'win32':
            os.startfile(p)
        else:
            import subprocess
            subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', p])

    botao.configure(command=fazer)
    abrir.configure(command=abre)
    r.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(linha_de_comandos(sys.argv[1:]) if len(sys.argv) > 1 else janela())
