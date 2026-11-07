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
| `boot1.rom` | esxDOS 0.8.9 (`ESXMMC.BIN`, 8192 bytes), for the DivMMC | the esxDOS 0.8.9 package at [esxdos.org](https://www.esxdos.org) (the same one the official core asks for) |
| `boot.rom` | ROMs of the other machines (48K, 128K, +3, TR-DOS, +D…) | `releases/boot.rom` in this repository (the official core's one), or the `games/Spectrum/boot.rom` you already have |
| `boot2.rom` | (optional) another ROM for the TC2068, instead of the one in the core | below |

The **2068 ROM is inside the core** (why, below): with no files at all the TC2068 boots. Without `boot1.rom`
there is no esxDOS; without `boot.rom` there are no other machines.

`boot2.rom` is for using another ROM: 24K (HOME 16K + EXROM 8K). For example the Portuguese TC2068 one that
comes with the [Fuse](https://fuse-emulator.sourceforge.net) emulator (`roms` folder), HOME first, then EXROM:

```
Windows:  copy /b tc2068-0.rom + tc2068-1.rom boot2.rom
Linux:    cat tc2068-0.rom tc2068-1.rom > boot2.rom
```

esxDOS on the TC2068 (below) was only made and checked with the ROM in the core.

## Using it

- **The machine** is chosen in F12 → Hardware → **Memory**: the TC2068 is the first in the list and the default;
  after changing it, **Reset & Apply**. **Alt+F7** switches to the TC2068 (Alt+F1 to F6 are the official core's).
- **Tapes:** TAP, TZX, PZX and CSW through F12 (Load Tape) and `LOAD ""`. They play as sound: the official core's
  fast loading only exists for the 48K ROM.
- **Joysticks:** MiSTer's two joysticks are the TC2068's two (BASIC `STICK`); Kempston is there too.
- **Sound:** the TC2068 AY, TurboSound (two AY on the 128K ports), General Sound and the beeper.
- **Video:** the TC2068 modes (second screen, hi-colour, hi-res 512×192) and ULAplus.
- **DivMMC:** F12 → Hardware → MMC Mode (Auto = only with a VHD selected; SD Card = the secondary SD card). The
  card (or the VHD) takes the `BIN`, `SYS` and `TMP` folders of the esxDOS 0.8.9 package, as with the official
  core; nothing else is needed. **F11** is NMI: it opens the esxDOS browser, as in the other cores.

## esxDOS on the TC2068

esxDOS calls routines of the 48K ROM by address; in the 2068 ROM those routines are elsewhere, and the normal
esxDOS hangs. In this core, on the TC2068, the core itself patches **esxDOS 0.8.9 while reading it** — `boot1.rom`
and the card's `/SYS/ESXDOS.SYS`, without touching the files: 14 calls in the firmware and 8 in `ESXDOS.SYS` go
to the same routines of the 2068 ROM (the same changes as the ESX2068 of
[Kairos](https://github.com/zambujal/Kairos)). Each byte only changes if it still has the 0.8.9 value: the same
card works for every machine, and the other machines see no difference at all.

- With another esxDOS version in `boot1.rom`, the DivMMC has no esxDOS on the TC2068 (only the card ports).
  `boot1.rom` and the card's `ESXDOS.SYS` must be the same 0.8.9 (the official core already asks for them to match).
- `LOAD ""` with a TAP opened by `.tapein`: while esxDOS is on (and no tape is loaded from F12), the EXROM
  LD-BYTES enters the esxDOS tape handling (JP 0562 at 0108, and the return through 0030, which was free in the
  EXROM).
- A 32K `boot2.rom` with the Kairos ESX2068 after the EXROM works too; that one looks for `/SYS/ESXD68.SYS`.

## The TC2068 in this core

- 16K HOME ROM at 0000–3FFF and 8K EXROM. Port **F4** selects, for each 8K chunk, HOME (0) or EXROM/DOCK (1);
  port **FF**, bit 7, EXROM (1) or DOCK (0). The DOCK is empty: it reads FFh and keeps no writes. FF bit 6 = 1
  disables the interrupt. F4 and FF read back.
- Port FE only answers at address FE, as on the 2068 (F4 and F6 are even too).
- AY on **F5** (register) and **F6** (data): it is the second TurboSound chip, so FFFD/BFFD still give the two
  AY. Joysticks on register 14: A8 = joystick 1, A9 = joystick 2, active low; bit 0 up, 1 down, 2 left,
  3 right, 7 fire.
- No 7FFD, TR-DOS, +D, Multiface or Gluk ROM.
- DivMMC with the traps of the Kairos TC2068 mode: 0000, 0066 and 3Dxx always; 0008 and 0038 only with HOME at
  0000–1FFF; 04C6 never; 0562 only right after an M1 at 0108 with the EXROM.
- Savestates do not keep F4 or FF: they only save with F4 at 0 and come back in the normal video mode.

## Why the 2068 ROM is in the core

So that the TC2068 boots without anyone having to go looking for a ROM. The one in `rtl/tc2068.mif` is the
TS2068 ROM (HOME + EXROM, 24576 bytes, md5 `9194283503a105f3f3dfba13e61e993f`): the same file the
[ZEsarUX](https://github.com/chernandezba/zesarux) emulator carries in its repository (`src/ts2068.rom`) and
[Spectrum Computing](https://spectrumcomputing.co.uk/entry/1000506/Hardware/TimexSinclair_TS2068) offers for
download. It is the Sinclair Spectrum ROM, now Amstrad's, with Timex's changes:

- Amstrad lets emulators include its ROMs ("Amstrad are happy for emulator writers to include images of our
  copyrighted code", Cliff Lawson, Amstrad; see the
  [copyright of the Debian spectrum-roms package](https://tracker.debian.org/media/packages/s/spectrum-roms/copyright-20081224-5));
- the ROM note of the zxsp emulator says of the TC2068 ones that they are made from Amstrad code and that Timex's
  changes are in the public domain
  ([README.copyright](https://k1.spdns.de/Develop/Projects/zxsp/Media/Roms/README.copyright)); the TS2068 one has
  the same origin.

The esxDOS changes were made and checked with this ROM (on Kairos and in the emulator). The `.mif` is made with
`python3 tools/rom2mif.py 32768 rtl/tc2068.mif ts2068.rom`.

**esxDOS is not here:** it is from [esxdos.org](https://www.esxdos.org) and everyone puts their own `boot1.rom`;
the core only carries the list of changes (addresses and values), not esxDOS code.

## Building

Quartus Prime Lite 17.0.2 (the MiSTer one) or Lite 25.1 (with Cyclone V support): open `TC2068.qpf` and
Processing → Start Compilation. The result is `output_files/TC2068.rbf`. `sys/sys.qip` picks `sys/pll_q<version>.qip`
for the Quartus version: there are 17 and 25 (the same as 17). Compared with the official core, `ZX-Spectrum.sv`, `rtl/turbosound.sv`,
`rtl/divmmc.v`, `ZX-Spectrum.sdc` and the project (`TC2068.qpf`, `.qsf`, `.srf`) change, and `rtl/tc2068.mif` and
`tools/rom2mif.py` are added.

## Credits

- **The MiSTer ZX-Spectrum core:** Sorgelig and others (GPL; see [README_ZX-Spectrum.md](README_ZX-Spectrum.md)
  and the file headers).
- **The TC2068** (GPL, like the rest): António Vitor. Written with the help of AI (Claude).
- **The TS2068 ROM:** Amstrad (Sinclair) and Timex; see above.
