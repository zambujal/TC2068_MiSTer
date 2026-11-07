# TC2068 para o MiSTer

*In English: [README.en.md](README.en.md)*

O core **ZX-Spectrum** oficial do MiSTer ([MiSTer-devel](https://github.com/MiSTer-devel/ZX-Spectrum_MISTer), de
Sorgelig e outros) com o **Timex Computer TC2068** como máquina principal. As máquinas do core oficial (Spectrum
48K, 128K, +2A/+3, Pentagon, Profi, Scorpion) continuam lá; o que o core oficial faz está em
[README_ZX-Spectrum.md](README_ZX-Spectrum.md).

Estado: em teste (Novembro de 2026). Arranca na simulação; ainda não foi experimentado num MiSTer.

## O que vai no cartão do MiSTer

- `TC2068.rbf` → `_Computer/`
- pasta `games/TC2068/`:

| Ficheiro | O que é | Onde se vai buscar |
|---|---|---|
| `boot1.rom` | esxDOS 0.8.9 (`ESXMMC.BIN`, 8192 bytes), para a DivMMC | o pacote do esxDOS 0.8.9 em [esxdos.org](https://www.esxdos.org) (o mesmo que o core oficial pede) |
| `boot.rom` | ROMs das outras máquinas (48K, 128K, +3, TR-DOS, +D…) | `releases/boot.rom` deste repositório (é o do core oficial), ou o `games/Spectrum/boot.rom` que já tens |
| `boot2.rom` | (opcional) outra ROM para o TC2068, em vez da que o core traz | em baixo |

A **ROM do 2068 vem dentro do core** (porquê, em baixo): sem nenhum ficheiro o TC2068 arranca. Sem o `boot1.rom`
não há esxDOS; sem o `boot.rom` não há as outras máquinas.

O `boot2.rom` serve para usar outra ROM: 24K (HOME 16K + EXROM 8K). Por exemplo, a do TC2068 português que
vem com o emulador [Fuse](https://fuse-emulator.sourceforge.net) (pasta `roms`), a HOME e depois a EXROM:

```
Windows:  copy /b tc2068-0.rom + tc2068-1.rom boot2.rom
Linux:    cat tc2068-0.rom tc2068-1.rom > boot2.rom
```

O esxDOS no TC2068 (em baixo) só foi feito e visto com a ROM que o core traz.

## Usar

- **A máquina** escolhe-se em F12 → Hardware → **Memory**: o TC2068 é o primeiro da lista e o de origem; depois
  de mudar, **Reset & Apply**. **Alt+F7** passa para o TC2068 (Alt+F1 a F6 são as do core oficial).
- **Cassetes:** TAP, TZX, PZX e CSW pelo F12 (Load Tape) e `LOAD ""`. Tocam como som: o carregamento rápido do
  core oficial só existe para a ROM do 48K.
- **Joysticks:** os dois do MiSTer são os dois do TC2068 (o `STICK` do BASIC); o Kempston também está.
- **Som:** o AY do TC2068, o TurboSound (dois AY nas portas do 128K), o General Sound e o beeper.
- **Vídeo:** os modos do TC2068 (segundo ecrã, hi-colour, hi-res 512×192) e o ULAplus.
- **DivMMC:** F12 → Hardware → MMC Mode (Auto = só com uma VHD escolhida; SD Card = o segundo cartão). No
  cartão (ou na VHD) vão as pastas `BIN`, `SYS` e `TMP` do pacote do esxDOS 0.8.9, como no core oficial; não é
  preciso mais nada. O **F11** é o NMI: abre o browser do esxDOS, como nos outros cores.

## O esxDOS no TC2068

O esxDOS chama rotinas da ROM do 48K pelo endereço; na ROM do 2068 essas rotinas estão noutros sítios, e o
esxDOS normal pendura. Neste core, no TC2068, o próprio core corrige o **esxDOS 0.8.9 enquanto o lê** — o
`boot1.rom` e o `/SYS/ESXDOS.SYS` do cartão, sem mexer nos ficheiros: 14 chamadas no firmware e 8 no
`ESXDOS.SYS` passam para as rotinas iguais da ROM do 2068 (as mesmas mudanças do ESX2068 do
[Kairos](https://github.com/zambujal/Kairos)). Cada byte só muda se ainda tiver o valor do 0.8.9: o mesmo cartão
serve para todas as máquinas, e as outras não vêem diferença nenhuma.

- Com outra versão do esxDOS no `boot1.rom`, a DivMMC fica sem esxDOS no TC2068 (só as portas do cartão).
  O `boot1.rom` e o `ESXDOS.SYS` do cartão têm de ser do mesmo 0.8.9 (o core oficial já pede que sejam iguais).
- `LOAD ""` com um TAP aberto pelo `.tapein`: enquanto o esxDOS está ligado (e não há cassete no F12), o
  LD-BYTES da EXROM entra no tratamento de cassete do esxDOS (JP 0562 em 0108, e o regresso por 0030, que na
  EXROM estava livre).
- Um `boot2.rom` de 32K com o ESX2068 do Kairos a seguir à EXROM também serve; esse procura `/SYS/ESXD68.SYS`.

## O TC2068 neste core

- ROM HOME de 16K em 0000–3FFF e EXROM de 8K. A porta **F4** escolhe, para cada bloco de 8K, a HOME (0) ou a
  EXROM/DOCK (1); a porta **FF**, no bit 7, a EXROM (1) ou o DOCK (0). O DOCK está vazio: lê FFh e não guarda o
  que se escreve. FF bit 6 = 1 desliga a interrupção. A F4 e a FF lêem-se de volta.
- A porta FE só responde ao endereço FE, como no 2068 (a F4 e a F6 também são pares).
- AY em **F5** (registo) e **F6** (dados): é o segundo chip do TurboSound, por isso FFFD/BFFD continuam a dar os
  dois AY. Joysticks no registo 14: A8 = joystick 1, A9 = joystick 2, activos a 0; bit 0 cima, 1 baixo,
  2 esquerda, 3 direita, 7 fogo.
- Sem 7FFD, TR-DOS, +D, Multiface nem a ROM do Gluk.
- DivMMC com as traps do modo TC2068 do Kairos: 0000, 0066 e 3Dxx sempre; 0008 e 0038 só com a HOME em
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

Foi com esta ROM que se fizeram e viram as mudanças do esxDOS (no Kairos e no emulador). O `.mif` faz-se com
`python3 tools/rom2mif.py 32768 rtl/tc2068.mif ts2068.rom`.

O **esxDOS não está aqui**: é de [esxdos.org](https://www.esxdos.org) e cada um põe o seu `boot1.rom`; o core
só leva a lista das mudanças (os endereços e os valores), não o código do esxDOS.

## Compilar

Quartus Prime Lite 17.0.2 (o do MiSTer): abrir `TC2068.qpf` e Processing → Start Compilation. Sai
`output_files/TC2068.rbf`. Em relação ao core oficial mudam `ZX-Spectrum.sv`, `rtl/turbosound.sv`,
`rtl/divmmc.v`, `ZX-Spectrum.sdc`, o projecto (`TC2068.qpf`, `.qsf`, `.srf`) e juntam-se `rtl/tc2068.mif` e
`tools/rom2mif.py`.

## De quem é

- **O core ZX-Spectrum do MiSTer:** Sorgelig e outros (GPL; ver [README_ZX-Spectrum.md](README_ZX-Spectrum.md)
  e os cabeçalhos dos ficheiros).
- **O TC2068** (GPL, como o resto): António Vitor. Escrito com ajuda de IA (Claude).
- **A ROM do TS2068:** Amstrad (Sinclair) e Timex; ver em cima.
