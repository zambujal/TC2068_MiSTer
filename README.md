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
| `boot2.rom` | ROM do TC2068: HOME 16K + EXROM 8K (24576 bytes) | as duas ROMs do TC2068 do Fuse, juntas (em baixo) |
| `boot1.rom` | esxDOS (`ESXMMC.BIN`, 8192 bytes), para a DivMMC | o pacote do esxDOS em [esxdos.org](https://www.esxdos.org) (o mesmo que o core oficial pede) |
| `boot.rom` | ROMs das outras máquinas (48K, 128K, +3, TR-DOS, +D…) | `releases/boot.rom` deste repositório (é o do core oficial), ou o `games/Spectrum/boot.rom` que já tens |

O `boot2.rom` são as duas ROMs do TC2068 que vêm com o emulador [Fuse](https://fuse-emulator.sourceforge.net)
(pasta `roms`), a HOME e depois a EXROM:

```
Windows:  copy /b tc2068-0.rom + tc2068-1.rom boot2.rom
Linux:    cat tc2068-0.rom tc2068-1.rom > boot2.rom
```

As do TS2068 (`ts2068-0.rom` e `ts2068-1.rom`) também servem. A
[página do TC2068 no Spectrum Computing](https://spectrumcomputing.co.uk/entry/1000507) liga para a colecção de
ROMs do Phil Kendall, o autor do Fuse.

Sem o `boot2.rom` o TC2068 arranca como um Spectrum 48K. Sem o `boot1.rom` não há esxDOS.

## Usar

- **A máquina** escolhe-se em F12 → Hardware → **Memory**: o TC2068 é o primeiro da lista e o de origem; depois
  de mudar, **Reset & Apply**. **Alt+F7** passa para o TC2068 (Alt+F1 a F6 são as do core oficial).
- **Cassetes:** TAP, TZX, PZX e CSW pelo F12 (Load Tape) e `LOAD ""`. Tocam como som: o carregamento rápido do
  core oficial só existe para a ROM do 48K.
- **Joysticks:** os dois do MiSTer são os dois do TC2068 (o `STICK` do BASIC); o Kempston também está.
- **Som:** o AY do TC2068, o TurboSound (dois AY nas portas do 128K), o General Sound e o beeper.
- **Vídeo:** os modos do TC2068 (segundo ecrã, hi-colour, hi-res 512×192) e o ULAplus.
- **DivMMC:** F12 → Hardware → MMC Mode (Auto = só com uma VHD escolhida; SD Card = o segundo cartão). No
  TC2068 ainda não há esxDOS: o esxDOS normal chama rotinas da ROM do 48K e pendura com a do 2068. Nas outras
  máquinas funciona como no core oficial.

## O TC2068 neste core

- ROM HOME de 16K em 0000–3FFF e EXROM de 8K. A porta **F4** escolhe, para cada bloco de 8K, a HOME (0) ou a
  EXROM/DOCK (1); a porta **FF**, no bit 7, a EXROM (1) ou o DOCK (0). O DOCK está vazio: lê FFh e não guarda o
  que se escreve. FF bit 6 = 1 desliga a interrupção. A F4 e a FF lêem-se de volta.
- A porta FE só responde ao endereço FE, como no 2068 (a F4 e a F6 também são pares).
- AY em **F5** (registo) e **F6** (dados): é o segundo chip do TurboSound, por isso FFFD/BFFD continuam a dar os
  dois AY. Joysticks no registo 14: A8 = joystick 1, A9 = joystick 2, activos a 0; bit 0 cima, 1 baixo,
  2 esquerda, 3 direita, 7 fogo.
- Sem 7FFD, TR-DOS, +D, Multiface nem a ROM do Gluk.
- DivMMC com as traps do modo TC2068 do [Kairos](https://github.com/zambujal/Kairos): 0000, 0066 e 3Dxx sempre;
  0008 e 0038 só com a HOME em 0000–1FFF; 04C6 nunca; 0562 só logo a seguir a um M1 em 0108 com a EXROM. O
  firmware do esxDOS no TC2068 é o que vier a seguir à EXROM num `boot2.rom` de 32K; sem ele a DivMMC só tem
  as portas do cartão.
- Os savestates não guardam a F4 nem a FF: só gravam com a F4 a 0 e voltam no modo de vídeo normal.

## Compilar

Quartus Prime Lite 17.0.2 (o do MiSTer): abrir `TC2068.qpf` e Processing → Start Compilation. Sai
`output_files/TC2068.rbf`. Em relação ao core oficial mudam `ZX-Spectrum.sv`, `rtl/turbosound.sv`,
`rtl/divmmc.v`, `ZX-Spectrum.sdc` e o projecto (`TC2068.qpf`, `.qsf`, `.srf`).

## De quem é

- **O core ZX-Spectrum do MiSTer:** Sorgelig e outros (GPL; ver [README_ZX-Spectrum.md](README_ZX-Spectrum.md)
  e os cabeçalhos dos ficheiros).
- **O TC2068** (GPL, como o resto): António Vitor. Escrito com ajuda de IA (Claude).
- **Sem ROMs nem esxDOS.** As ROMs do TC2068 vêm da ROM do Sinclair, que é da Amstrad; a Amstrad deixa
  distribuí-las e as mudanças da Timex são de domínio público
  ([nota das ROMs](https://k1.spdns.de/Develop/Projects/zxsp/Media/Roms/README.copyright)). O esxDOS é de
  [esxdos.org](https://www.esxdos.org).
