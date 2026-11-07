# TC2068 para o MiSTer

*In English: [README.en.md](README.en.md)*

O core **ZX-Spectrum** oficial do MiSTer ([MiSTer-devel](https://github.com/MiSTer-devel/ZX-Spectrum_MISTer), de
Sorgelig e outros) com o **Timex Computer TC2068** como máquina principal. As máquinas do core oficial (Spectrum
48K, 128K, +2A/+3, Pentagon, Profi, Scorpion) continuam lá; o que o core oficial faz está em
[README_ZX-Spectrum.md](README_ZX-Spectrum.md).

Estado: em teste (Novembro de 2026); experimentado num MiSTer (DE10-Nano com SDRAM).

## O que vai no cartão do MiSTer

A **ROM do TC2068 vem dentro do core** (porquê, em baixo). Para o TC2068 arrancar basta o `.rbf`:

- `TC2068_AAAAMMDD.rbf` (o mais recente de [`releases/`](releases)) → pasta `_Computer/`. A data no nome é a que o menu
  mostra.

O resto é opcional e vai na pasta `games/TC2068/`:

| Ficheiro | Para quê | Onde se vai buscar |
|---|---|---|
| `boot1.rom` | o esxDOS: é a ROM da DivMMC | o `ESXMMC.BIN` do pacote do esxDOS 0.8.9, em [esxdos.org](https://www.esxdos.org), com o nome mudado para `boot1.rom` (é o que o core oficial também pede) |
| uma VHD (`.vhd`) | o cartão da DivMMC, com as pastas `BIN`, `SYS` e `TMP` do mesmo pacote do esxDOS | faz-se com o `tools/faz_vhd.py` (em baixo, "Fazer a VHD do esxDOS"); em vez dela pode servir o segundo cartão SD da placa de I/O |
| `boot.rom` | só para as outras máquinas do core (48K, 128K, +3, TR-DOS, +D…); o TC2068 não precisa dele | é o do core ZX-Spectrum oficial: `releases/boot.rom` deste repositório, ou o `games/Spectrum/boot.rom` se o core oficial já estiver no cartão |
| `boot2.rom` | outra ROM para o TC2068, em vez da que vem no core | em baixo |

O `boot2.rom` serve para usar outra ROM: 24K (HOME 16K + EXROM 8K). Por exemplo, a do TC2068 português que
vem com o emulador [Fuse](https://fuse-emulator.sourceforge.net) (pasta `roms`), a HOME e depois a EXROM:

```
Windows:  copy /b tc2068-0.rom + tc2068-1.rom boot2.rom
Linux:    cat tc2068-0.rom tc2068-1.rom > boot2.rom
```

O esxDOS no TC2068 (em baixo) só foi feito e visto com a ROM que o core traz.

## Fazer a VHD do esxDOS

O [`tools/faz_vhd.py`](tools/faz_vhd.py) faz o `boot1.rom` e a VHD a partir do pacote do esxDOS 0.8.9, em Windows e
em Linux:

1. Descarregar o pacote do esxDOS 0.8.9 de [esxdos.org](https://www.esxdos.org). É um zip; não é preciso
   descompactá-lo.
2. Descarregar o [`faz_vhd.py`](tools/faz_vhd.py) (na página do ficheiro, o botão **Download raw file**).
3. Correr o programa:
   - **Windows:** instalar o Python 3 de [python.org](https://www.python.org/downloads/) (com as opções de origem)
     e fazer duplo clique no `faz_vhd.py`. Abre-se uma janela: em "Pacote do esxDOS 0.8.9" escolher o zip
     (botão **Zip...**) e carregar em **Fazer**.
   - **Linux:** `python3 faz_vhd.py` abre a mesma janela (precisa do tkinter: `sudo dnf install python3-tkinter`
     no Fedora, `sudo apt install python3-tk` no Debian/Ubuntu). Sem janela: `python3 faz_vhd.py esxdos089.zip`
     (o nome do zip que se descarregou; `-h` mostra as opções).
4. Saem dois ficheiros, numa pasta `TC2068` ao lado do zip:
   - `boot1.rom`: o `ESXMMC.BIN` do pacote, a ROM da DivMMC;
   - `esxdos089.vhd`: um cartão de 128 MB (FAT32) com as pastas `BIN`, `SYS` e `TMP` do pacote.

   Os dois vão para `games/TC2068/` no cartão do MiSTer.
5. No core TC2068: F12 → **Load DivMMC** → `esxdos089.vhd`, e **Ctrl+F11**.

Na janela (ou com `-e pasta`) pode-se escolher uma **pasta extra** que vai também para a VHD, por exemplo jogos em
TAP, para abrir com o `.tapein` ou com o browser do esxDOS (F11). O tamanho da VHD vai de 64 MB a 2 GB (`-s`). O
programa avisa se o `ESXMMC.BIN` ou o `ESXDOS.SYS` não forem do esxDOS 0.8.9: no TC2068, o core só corrige essa
versão.

## Usar

- **A máquina** escolhe-se em F12 → Hardware → **Memory**: o TC2068 é o primeiro da lista e o de origem; depois
  de mudar, **Reset & Apply**. **Alt+F7** passa para o TC2068 (Alt+F1 a F6 são as do core oficial).
- **Cassetes:** TAP, TZX, PZX e CSW pelo F12 (Load Tape) e `LOAD ""`. Tocam como som: o carregamento rápido do
  core oficial só existe para a ROM do 48K.
- **Joysticks:** os dois do MiSTer são os dois do TC2068 (o `STICK` do BASIC); o Kempston também está.
- **Som:** o AY do TC2068, o TurboSound (dois AY nas portas do 128K), o General Sound e o beeper.
- **Vídeo:** os modos do TC2068 (segundo ecrã, hi-colour, hi-res 512×192) e o ULAplus.
- **DivMMC:** com o MMC Mode (F12 → Hardware) em Auto, o de origem, escolhe-se a VHD em F12 → **Load DivMMC**;
  com o MMC Mode em SD Card, é o segundo cartão. A DivMMC liga-se no reset (**Ctrl+F11**): aparece primeiro o
  arranque do esxDOS e depois o do 2068. Na VHD (ou no cartão) vão as pastas `BIN`, `SYS` e `TMP` do pacote do
  esxDOS 0.8.9, como no core oficial; não é preciso mais nada. O **F11** é o NMI: abre o browser do esxDOS, como
  nos outros cores.

## O esxDOS no TC2068

O esxDOS chama rotinas da ROM do 48K pelo endereço; na ROM do 2068 essas rotinas estão noutros sítios, e o
esxDOS normal pendura. Neste core, no TC2068, o próprio core corrige o **esxDOS 0.8.9 enquanto o lê** — o
`boot1.rom` e o `/SYS/ESXDOS.SYS` do cartão, sem mexer nos ficheiros: 14 chamadas no firmware e 8 no
`ESXDOS.SYS` passam para as rotinas iguais da ROM do 2068. Cada byte só muda se ainda tiver o valor do 0.8.9: o
mesmo cartão serve para todas as máquinas, e as outras não vêem diferença nenhuma.

- Com outra versão do esxDOS no `boot1.rom`, a DivMMC fica sem esxDOS no TC2068 (só as portas do cartão).
  O `boot1.rom` e o `ESXDOS.SYS` do cartão têm de ser do mesmo 0.8.9 (o core oficial já pede que sejam iguais).
- `LOAD ""` com um TAP aberto pelo `.tapein`: enquanto o esxDOS está ligado (e não há cassete no F12), o
  LD-BYTES da EXROM entra no tratamento de cassete do esxDOS (JP 0562 em 0108, e o regresso por 0030, que na
  EXROM estava livre).

## O TC2068 neste core

- ROM HOME de 16K em 0000–3FFF e EXROM de 8K. A porta **F4** escolhe, para cada bloco de 8K, a HOME (0) ou a
  EXROM/DOCK (1); a porta **FF**, no bit 7, a EXROM (1) ou o DOCK (0). O DOCK está vazio: lê FFh e não guarda o
  que se escreve. FF bit 6 = 1 desliga a interrupção. A F4 e a FF lêem-se de volta.
- A porta FE só responde ao endereço FE, como no 2068 (a F4 e a F6 também são pares).
- AY em **F5** (registo) e **F6** (dados): é o segundo chip do TurboSound, por isso FFFD/BFFD continuam a dar os
  dois AY. Joysticks no registo 14: A8 = joystick 1, A9 = joystick 2, activos a 0; bit 0 cima, 1 baixo,
  2 esquerda, 3 direita, 7 fogo.
- Sem 7FFD, TR-DOS, +D, Multiface nem a ROM do Gluk.
- DivMMC com as traps adaptadas ao TC2068: 0000, 0066 e 3Dxx sempre; 0008 e 0038 só com a HOME em
  0000–1FFF; 04C6 nunca; 0562 só logo a seguir a um M1 em 0108 com a EXROM.
- Os savestates não guardam a F4 nem a FF: só gravam com a F4 a 0 e voltam no modo de vídeo normal.

## Porque é que a ROM do 2068 está no core

Para o TC2068 arrancar sem ninguém ter de ir à procura de uma ROM. A que está em `rtl/tc2068.mif` é a ROM do
TS2068 (HOME + EXROM, 24576 bytes, md5 `9194283503a105f3f3dfba13e61e993f`): o mesmo ficheiro que o emulador
[ZEsarUX](https://github.com/chernandezba/zesarux) traz no seu repositório (`src/ts2068.rom`) e que o
[Spectrum Computing](https://spectrumcomputing.co.uk/entry/1000506/Hardware/TimexSinclair_TS2068) tem para
descarregar. É a ROM do Spectrum da Sinclair, hoje da Amstrad, com as mudanças da Timex:

- a Amstrad deixa os emuladores incluírem as suas ROMs ("Amstrad are happy for emulator writers to include
  images of our copyrighted code", Cliff Lawson, Amstrad; ver o
  [copyright do pacote spectrum-roms do Debian](https://tracker.debian.org/media/packages/s/spectrum-roms/copyright-20081224-5));
- a nota das ROMs do emulador zxsp diz das do TC2068 que são feitas do código da Amstrad e que as mudanças
  da Timex estão no domínio público
  ([README.copyright](https://k1.spdns.de/Develop/Projects/zxsp/Media/Roms/README.copyright)); a do TS2068 tem a
  mesma origem.

Foi com esta ROM que se fizeram e viram as mudanças do esxDOS. O `.mif` faz-se com
`python3 tools/rom2mif.py 32768 rtl/tc2068.mif ts2068.rom`.

**O esxDOS não vem com o core.** Descarrega-se o pacote do esxDOS 0.8.9 de [esxdos.org](https://www.esxdos.org), como
para o core oficial. O pacote tem duas partes:

- o ficheiro `ESXMMC.BIN`, a ROM da DivMMC (8 KB; numa DivMMC verdadeira vai gravada na EEPROM). No MiSTer muda-se-lhe
  o nome para `boot1.rom` e põe-se em `games/TC2068/`;
- as pastas `BIN`, `SYS` e `TMP`, que vão para a VHD (ou para o segundo cartão).

Para o esxDOS funcionar com a ROM do 2068, o core troca alguns bytes enquanto o lê. Para isso guarda só uma pequena
tabela com os bytes a trocar, não o esxDOS.

## Compilar

Quartus Prime Lite 17.0.2 (o do MiSTer) ou o Lite 25.1 (com o suporte do Cyclone V): abrir `TC2068.qpf` e
Processing → Start Compilation. Sai `output_files/TC2068.rbf`. O `sys/sys.qip` vai buscar o `sys/pll_q<versão>.qip`
da versão do Quartus: há o 17 e o 25 (igual ao 17). Em relação ao core oficial mudam `ZX-Spectrum.sv`, `rtl/turbosound.sv`,
`rtl/divmmc.v`, `ZX-Spectrum.sdc`, o projecto (`TC2068.qpf`, `.qsf`, `.srf`) e juntam-se `rtl/tc2068.mif`,
`tools/rom2mif.py` e `tools/faz_vhd.py`.

No Quartus Lite 25.1 os tempos cumprem-se (Novembro de 2026: no relógio de 112 MHz, slack de setup de +0,5 ns). Para
isso, também para as outras máquinas: a cópia dos bancos 5 e 7 para o vídeo (a VRAM) é escrita um ciclo depois, por
um registo; e o `ZX-Spectrum.sdc` dá dois ciclos aos caminhos que partem do que só muda com um OUT (as portas #F4 e
#FF do TC2068, a #E3 da DivMMC) e do sinal de refresh do Z80 até à SDRAM.

## De quem é

- **O core ZX-Spectrum do MiSTer:** Sorgelig e outros (GPL; ver [README_ZX-Spectrum.md](README_ZX-Spectrum.md)
  e os cabeçalhos dos ficheiros).
- **O TC2068** (GPL, como o resto): António Vitor. Foi usada IA (Claude).
- **A ROM do TS2068:** Amstrad (Sinclair) e Timex; ver em cima.
