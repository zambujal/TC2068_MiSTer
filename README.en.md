# TC2068 for MiSTer

*Em português: [README.md](README.md)*

The official MiSTer **ZX-Spectrum** core ([MiSTer-devel](https://github.com/MiSTer-devel/ZX-Spectrum_MISTer), by
Sorgelig and others) with the **Timex Computer TC2068** as its main machine. The machines of the official core
(Spectrum 48K, 128K, +2A/+3, Pentagon, Profi, Scorpion) are still there; what the official core does is in
[README_ZX-Spectrum.md](README_ZX-Spectrum.md).

Status: testing (November 2026). It boots in simulation; not yet tried on a MiSTer.

## What goes on the MiSTer SD card

- `TC2068.rbf` → `_Computer/`
- folder `games/TC2068/`:

| File | What it is | Where to get it |
|---|---|---|
| `boot2.rom` | TC2068 ROM: HOME 16K + EXROM 8K (24576 bytes) | the two TC2068 ROMs from Fuse, joined (below) |
| `boot1.rom` | esxDOS (`ESXMMC.BIN`, 8192 bytes), for the DivMMC | the esxDOS package at [esxdos.org](https://www.esxdos.org) (the same one the official core asks for) |
| `boot.rom` | ROMs of the other machines (48K, 128K, +3, TR-DOS, +D…) | `releases/boot.rom` in this repository (the official core's one), or the `games/Spectrum/boot.rom` you already have |

`boot2.rom` is the two TC2068 ROMs that come with the [Fuse](https://fuse-emulator.sourceforge.net) emulator
(`roms` folder), HOME first, then EXROM:

```
Windows:  copy /b tc2068-0.rom + tc2068-1.rom boot2.rom
Linux:    cat tc2068-0.rom tc2068-1.rom > boot2.rom
```

The TS2068 ones (`ts2068-0.rom` and `ts2068-1.rom`) work too. The
[TC2068 page on Spectrum Computing](https://spectrumcomputing.co.uk/entry/1000507) links to the ROM collection of
Phil Kendall, the author of Fuse.

Without `boot2.rom` the TC2068 starts as a Spectrum 48K. Without `boot1.rom` there is no esxDOS.

## Using it

- **The machine** is chosen in F12 → Hardware → **Memory**: the TC2068 is the first in the list and the default;
  after changing it, **Reset & Apply**. **Alt+F7** switches to the TC2068 (Alt+F1 to F6 are the official core's).
- **Tapes:** TAP, TZX, PZX and CSW through F12 (Load Tape) and `LOAD ""`. They play as sound: the official core's
  fast loading only exists for the 48K ROM.
- **Joysticks:** MiSTer's two joysticks are the TC2068's two (BASIC `STICK`); Kempston is there too.
- **Sound:** the TC2068 AY, TurboSound (two AY on the 128K ports), General Sound and the beeper.
- **Video:** the TC2068 modes (second screen, hi-colour, hi-res 512×192) and ULAplus.
- **DivMMC:** F12 → Hardware → MMC Mode (Auto = only with a VHD selected; SD Card = the secondary SD card). On
  the TC2068 there is no esxDOS yet: the normal esxDOS calls routines of the 48K ROM and hangs with the 2068 one.
  On the other machines it works as in the official core.

## The TC2068 in this core

- 16K HOME ROM at 0000–3FFF and 8K EXROM. Port **F4** selects, for each 8K chunk, HOME (0) or EXROM/DOCK (1);
  port **FF**, bit 7, EXROM (1) or DOCK (0). The DOCK is empty: it reads FFh and keeps no writes. FF bit 6 = 1
  disables the interrupt. F4 and FF read back.
- Port FE only answers at address FE, as on the 2068 (F4 and F6 are even too).
- AY on **F5** (register) and **F6** (data): it is the second TurboSound chip, so FFFD/BFFD still give the two
  AY. Joysticks on register 14: A8 = joystick 1, A9 = joystick 2, active low; bit 0 up, 1 down, 2 left,
  3 right, 7 fire.
- No 7FFD, TR-DOS, +D, Multiface or Gluk ROM.
- DivMMC with the traps of the TC2068 mode of [Kairos](https://github.com/zambujal/Kairos): 0000, 0066 and 3Dxx
  always; 0008 and 0038 only with HOME at 0000–1FFF; 04C6 never; 0562 only right after an M1 at 0108 with the
  EXROM. The esxDOS firmware on the TC2068 is whatever follows the EXROM in a 32K `boot2.rom`; without it the
  DivMMC only has the card ports.
- Savestates do not keep F4 or FF: they only save with F4 at 0 and come back in the normal video mode.

## Building

Quartus Prime Lite 17.0.2 (the MiSTer one): open `TC2068.qpf` and Processing → Start Compilation. The result is
`output_files/TC2068.rbf`. Compared with the official core, `ZX-Spectrum.sv`, `rtl/turbosound.sv`,
`rtl/divmmc.v`, `ZX-Spectrum.sdc` and the project (`TC2068.qpf`, `.qsf`, `.srf`) change.

## Credits

- **The MiSTer ZX-Spectrum core:** Sorgelig and others (GPL; see [README_ZX-Spectrum.md](README_ZX-Spectrum.md)
  and the file headers).
- **The TC2068** (GPL, like the rest): António Vitor. Written with the help of AI (Claude).
- **No ROMs and no esxDOS.** The TC2068 ROMs derive from the Sinclair ROM, which belongs to Amstrad; Amstrad
  allows them to be distributed and the Timex changes are in the public domain
  ([ROM note](https://k1.spdns.de/Develop/Projects/zxsp/Media/Roms/README.copyright)). esxDOS is from
  [esxdos.org](https://www.esxdos.org).
