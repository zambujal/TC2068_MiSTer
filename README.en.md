# TC2068 for MiSTer

*Em português: [README.md](README.md)*

The official MiSTer **ZX-Spectrum** core ([MiSTer-devel](https://github.com/MiSTer-devel/ZX-Spectrum_MISTer), by
Sorgelig and others) with the **Timex Computer TC2068** as its main machine: HOME ROM and EXROM, DOCK cartridges, AY,
joysticks, Timex video modes and DivMMC with esxDOS. A second core comes from the same code, the **Timex Computer
TC2048** (below, "The TC2048 core"). It is only for the TC2068 and the TC2048: for the other machines (Spectrum 48K,
128K, +2A/+3, Pentagon…) use the official core. What the official core does is in
[README_ZX-Spectrum.md](README_ZX-Spectrum.md).

Status: testing (November 2026); tried on a MiSTer (DE10-Nano with SDRAM).

## Installing

The **TC2068 ROM is inside the core** (why, below). The `.rbf` is all the TC2068 needs to boot:

- **`TC2068_T80Q_YYYYMMDD.rbf`, with the corrected Z80** (below, "The Z80"), or `TC2068_YYYYMMDD.rbf`, with the
  official core's T80 (the latest in [`releases/`](releases)) → folder `_Computer/` on the MiSTer SD card. The date in
  the name is the one the menu shows. Both can be there, and they use the same `games/TC2068/` folder.

What came in on 11 November 2026 (BRIGHT black as grey on the TC2068, the TC2048 core and the tests) is not yet in the
`.rbf` files in `releases/`: it is being tested and, for now, it is built from the code (below, "Building").

Everything else is optional and goes in the folder `games/TC2068/`:

| File | What for | Where to get it |
|---|---|---|
| `boot1.rom` | esxDOS: it is the DivMMC ROM | `ESXMMC.BIN` from the esxDOS 0.8.9 package at [esxdos.org](https://www.esxdos.org), renamed to `boot1.rom`; `tools/faz_vhd.py` does that (below, "esxDOS") |
| a VHD (`.vhd`) | the DivMMC card, with the `BIN`, `SYS` and `TMP` folders of the same package | made with `tools/faz_vhd.py`; the secondary SD card of the I/O board can be used instead |
| cartridges (`.dck`) | programs on cartridge, in the DOCK | below, "Cartridges" |
| `boot2.rom` | another TC2068 ROM, instead of the one in the core; normally not needed | below, "The 2068 ROM" |

## Using it

- **The machine:** the TC2068 is the default (F12 → Hardware → **Memory**, the first in the list; **Alt+F7**). The
  others in the list are the official core's and need its ROMs (`boot.rom`): use the official core for them.
- **Tapes:** TAP, TZX, PZX and CSW through F12 (**Load Tape**) and `LOAD ""`. They play as sound: the official core's
  fast loading only exists for the 48K ROM.
- **Cartridges:** F12 → **Load 2068 Cartridge** → a `.dck`; to remove it, **Reset & Detach Cartridge**.
- **DivMMC:** F12 → **Load DivMMC** → the VHD, then **Ctrl+F11**: first the esxDOS boot, then the 2068 one. With MMC
  Mode (F12 → Hardware) on SD Card, it is the secondary SD card. **F11** is NMI: it opens the esxDOS browser.
- **Joysticks:** MiSTer's two joysticks are the TC2068's two (BASIC `STICK`); Kempston is there too.
- **Sound:** the TC2068 AY, TurboSound (two AY on the 128K ports), General Sound and the beeper.
- **Video:** the TC2068 modes (second screen, hi-colour, hi-res 512×192) and ULAplus. BRIGHT black shows as dark
  grey, as on a real TC2068 (on the TC2048 and the Spectrum it is black).

## Cartridges

The TC2068 (and the American TS2068) has a cartridge port underneath, the **DOCK**: a 64K bank, in 8 chunks of 8K,
that port #F4 puts in place of the normal memory, chunk by chunk, with bit 7 of #FF at 0. At boot, the 2068 ROM looks
for a cartridge and starts it:

- **LROS** (header at DOCK 0000h): it takes the whole machine, without the 2068 ROM;
- **AROS** (header at DOCK 8000h): a machine code or BASIC program that uses the 2068 ROM. It starts by itself if the
  cartridge asks for it; a BASIC AROS without autostart waits for a `RUN`.

In this core, F12 → **Load 2068 Cartridge** loads a `.dck` file and resets, as when the machine is switched on with
the cartridge in; **Reset & Detach Cartridge** removes it (the same option removes the Dandanator cartridge). Without a
cartridge, the DOCK reads FFh.

Where to find cartridges in `.dck`:

- Androids (Timex, 1984): the [game page](https://timexsinclair.com/product/androids) and the
  [cartridge zip](https://archive.org/download/timex-sinclair-software-archive/Androids%20%281984%29%28Timex%20Computer%20Corp%29%28TS2068%29%28US%29%28Cartridge%29.zip), with the `.dck` inside;
- [Spectrum Emulator](https://spectrumcomputing.co.uk/entry/4000071/Timex/Spectrum_Emulator) (TMX Portugal, 1985):
  the Portuguese cartridge with the TC2048 ROM;
- [Zebra OS-64](https://spectrumcomputing.co.uk/entry/4000090/Timex/Zebra_OS64), and the other Timex cartridges
  (Flight Simulator, Pinball, Casino 1, Crazybugs…) at [timexsinclair.com](https://timexsinclair.com).

The `.dck` format (from the Warajevo emulator) has, for each bank, 9 header bytes (the bank number: 0 DOCK, 254
EXROM, 255 HOME; and one byte per 8K chunk: 0 none, 1 RAM, 2 ROM, 3 RAM with contents), followed by the images of the
chunks that have one. The core uses the DOCK bank, the cartridge one; EXROM and HOME banks in a `.dck` are left out.
The cartridge RAM chunks can be written; RAM chunks without contents in the file are not cleared. A `.bin` (just the
image) does not say which chunks it goes in: use the `.dck`.

### 48K games as cartridges

`tools/snap2dck.py` makes a cartridge from a 48K snapshot (`.z80` or `.sna`) and a Spectrum ROM (the 48K one or the
TC2048 one), like the TMX Spectrum Emulator:

    python3 tools/snap2dck.py GAME.z80 48.rom

The cartridge has the ROM in chunks 0-1 and the game's 48K in chunks 2-7: 64K, the whole DOCK. It is an LROS: the 2068
ROM starts a loader placed in the free area of the Spectrum ROM, which copies the game into RAM, leaves the Spectrum ROM
at 0000-3FFF, restores the registers and jumps to the game. The game sees a 48K Spectrum: ROM calls, the font and the
interrupt at 0038h go to the Spectrum ROM. It is not for 128K games, nor for games that write port FF (on the 2068 it
changes the screen mode and the memory map) or read it expecting the floating bus. The cartridge holds the ROM: keep it
to yourself.

## esxDOS

### Making the VHD

[`tools/faz_vhd.py`](tools/faz_vhd.py) makes `boot1.rom` and the VHD from the esxDOS 0.8.9 package, on Windows and
on Linux:

1. Download the esxDOS 0.8.9 package from [esxdos.org](https://www.esxdos.org). It is a zip; there is no need to
   unzip it.
2. Download [`faz_vhd.py`](tools/faz_vhd.py) (on the file's page, the **Download raw file** button).
3. Run it:
   - **Windows:** install Python 3 from [python.org](https://www.python.org/downloads/) (with the default options)
     and double-click `faz_vhd.py`. A window opens: in "esxDOS 0.8.9 package" choose the zip (**Zip...** button)
     and press **Make**.
   - **Linux:** `python3 faz_vhd.py` opens the same window (it needs tkinter: `sudo dnf install python3-tkinter` on
     Fedora, `sudo apt install python3-tk` on Debian/Ubuntu). Without a window: `python3 faz_vhd.py esxdos089.zip`
     (the name of the zip that was downloaded; `-h` shows the options).
4. Two files come out, in a `TC2068` folder next to the zip; both go to `games/TC2068/` on the MiSTer SD card:
   - `boot1.rom`: the `ESXMMC.BIN` of the package, the DivMMC ROM;
   - `esxdos089.vhd`: a 128 MB card (FAT32) with the `BIN`, `SYS` and `TMP` folders of the package.
5. In the TC2068 core: F12 → **Load DivMMC** → `esxdos089.vhd`, then **Ctrl+F11**.

In the window (or with `-e folder`) an **extra folder** can be chosen to go on the VHD too, for example games as TAP,
to open with `.tapein` or with the esxDOS browser (F11). The VHD size goes from 64 MB to 2 GB (`-s`). The program
warns if `ESXMMC.BIN` or `ESXDOS.SYS` are not from esxDOS 0.8.9.

### How it works on the TC2068

esxDOS does not come with the core: download it from [esxdos.org](https://www.esxdos.org), as for the official core.
esxDOS calls routines of the 48K ROM by address; in the 2068 ROM those routines are elsewhere, and the normal esxDOS
hangs. In this core, on the TC2068, the core itself patches **esxDOS 0.8.9 while reading it** — `boot1.rom` and the
card's `/SYS/ESXDOS.SYS`, without touching the files: 14 calls in the firmware and 8 in `ESXDOS.SYS` go to the same
routines of the 2068 ROM. For that the core only keeps a small table of the bytes to swap, not esxDOS itself. Each
byte only changes if it still has the 0.8.9 value: the same card works for every machine.

- With another esxDOS version in `boot1.rom`, the DivMMC has no esxDOS on the TC2068 (only the card ports).
  `boot1.rom` and the card's `ESXDOS.SYS` must be the same 0.8.9.
- `LOAD ""` with a TAP opened by `.tapein`: while esxDOS is on (and no tape is loaded from F12), the EXROM
  LD-BYTES enters the esxDOS tape handling (JP 0562 at 0108, and the return through 0030, which was free in the
  EXROM).

## The TC2068 in this core

- 16K HOME ROM at 0000–3FFF and 8K EXROM. Port **F4** selects, for each 8K chunk, HOME (0) or EXROM/DOCK (1);
  port **FF**, bit 7, EXROM (1) or DOCK (0). The DOCK is the cartridge (above); without one it reads FFh and keeps no
  writes. FF bit 6 = 1 disables the interrupt. F4 and FF read back.
- Port FE only answers at address FE, as on the 2068 (F4 and F6 are even too).
- AY on **F5** (register) and **F6** (data): it is the second TurboSound chip, so FFFD/BFFD still give the two
  AY. Joysticks on register 14: A8 = joystick 1, A9 = joystick 2, active low; bit 0 up, 1 down, 2 left,
  3 right, 7 fire.
- No 7FFD, TR-DOS, +D, Multiface or Gluk ROM.
- DivMMC with traps adapted to the TC2068: 0000, 0066 and 3Dxx always; 0008 and 0038 only with HOME at
  0000–1FFF; 04C6 never; 0562 only right after an M1 at 0108 with the EXROM.
- Savestates do not keep F4 or FF: they only save with F4 at 0 and come back in the normal video mode.

## The TC2048 core

A second core comes from the same code, the **Timex Computer TC2048**: `TC2048_YYYYMMDD.rbf` goes in the `_Computer/`
folder and uses the `games/TC2048/` folder (`boot1.rom` and the esxDOS VHD, as for the TC2068). It is the TC2048 as in
the [Fuse](https://fuse-emulator.sourceforge.net) emulator:

- the TC2048 ROM is inside the core (`rtl/tc2048.mif`; below, "The 2068 ROM"). It is the 48K one with 7 bytes changed:
  an OUT (#FF),A with A = 0 before the © message;
- the Timex video modes on port FF (second screen, hi-colour, hi-res 512×192). FF bit 6 = 1 stops the interrupt and
  FF reads back. Port FE only answers at address FE;
- the Kempston joystick, the TC2048's only port. There is no F4, DOCK, EXROM nor AY at F5/F6; the core's TurboSound
  stays (the TC2048 has no AY, but it does no harm);
- the DivMMC and esxDOS as on the 48K (esxDOS unchanged);
- BRIGHT black is black;
- 48K snapshots stay on the TC2048.

Status: to be tested on a MiSTer (November 2026).

## Tests

The [`testes/`](testes) folder has a program that tests the TC2048 and the TC2068, on both cores or on the real
machines. It tells the machine from its ROM; tests the Z80, the interrupt, the ports (FF, F4, FE, 7FFD), the EXROM,
the AY, the Kempston and BRIGHT black; shows the joysticks live and the port FF video modes. The results come in
colours: green = as on the original, yellow = extra, red = missing or wrong. `teste_timex.tap` is for both,
`teste_timex.dck` (cartridge) for the TC2068 and `teste_timex.sna` for the TC2048. More in
[testes/README.en.md](testes/README.en.md).

## The 2068 ROM

The ROM is in the core so that the TC2068 boots without anyone having to go looking for it. The one in
`rtl/tc2068.mif` is the TS2068 ROM as it is, unchanged (HOME + EXROM, 24576 bytes, md5
`9194283503a105f3f3dfba13e61e993f`): the same file the [ZEsarUX](https://github.com/chernandezba/zesarux) emulator
carries in its repository (`src/ts2068.rom`) and
[Spectrum Computing](https://spectrumcomputing.co.uk/entry/1000506/Hardware/TimexSinclair_TS2068) offers for
download. It is the Sinclair Spectrum ROM, now Amstrad's, with Timex's changes:

- Amstrad lets emulators include its ROMs ("Amstrad are happy for emulator writers to include images of our
  copyrighted code", Cliff Lawson, Amstrad; see the
  [copyright of the Debian spectrum-roms package](https://tracker.debian.org/media/packages/s/spectrum-roms/copyright-20081224-5));
- the ROM note of the zxsp emulator says of the TC2068 ones that they are made from Amstrad code and that Timex's
  changes are in the public domain
  ([README.copyright](https://k1.spdns.de/Develop/Projects/zxsp/Media/Roms/README.copyright)); the TS2068 one has
  the same origin.

The `.mif` is made with `python3 tools/rom2mif.py 32768 rtl/tc2068.mif ts2068.rom`.

The TC2048 core's one, in `rtl/tc2048.mif`, is the TC2048 ROM as it is (16384 bytes, md5
`9dd7ecf784a6c04265c073c236f5fadb`): the same as ZEsarUX's (`src/tc2048.rom`) and Debian's spectrum-roms package. The
zxsp note says it is Amstrad's and that Amstrad allows it to be distributed. It is made with
`python3 tools/rom2mif.py 32768 rtl/tc2048.mif tc2048.rom`.

**`boot2.rom`** is only for those who want another 24K ROM (HOME 16K + EXROM 8K) instead of the core's. For example
the Portuguese TC2068 one that comes with the [Fuse](https://fuse-emulator.sourceforge.net) emulator (`roms` folder),
HOME first, then EXROM:

```
Windows:  copy /b tc2068-0.rom + tc2068-1.rom boot2.rom
Linux:    cat tc2068-0.rom tc2068-1.rom > boot2.rom
```

esxDOS on the TC2068 was only made and checked with the ROM in the core.

The [`releases/`](releases) folder only has the core. For F12 → Savestate Disk, the official core has a
`savestates.sav` in its [releases folder](https://github.com/MiSTer-devel/ZX-Spectrum_MISTer/tree/master/releases).

## The Z80 (T80)

There are two versions of the core in `releases/`:

- **`TC2068_T80Q_YYYYMMDD.rbf`: the corrected Z80**, the T80 with the Q register of the Zilog Z80. This version's Z80
  code is in the [`t80q`](https://github.com/zambujal/TC2068_MiSTer/tree/t80q) branch.
- `TC2068_YYYYMMDD.rbf`: the official core's T80.

After SCF or CCF, the undocumented X and Y flags (bits 5 and 3 of F) depend on the previous instruction (found in
2012; the variants are on [David Banks's page](https://github.com/hoglet67/Z80Decoder/wiki/Undocumented-Flags#scfccf)).
On a Zilog Z80, if it wrote the flags, they come from A alone; if it did not, from A and F. The official core's T80
only checked whether the flags *changed*; the T80Q version checks whether they were *written*, even with the same
value (POP AF, EX AF and SET/RES do not count as a write). For example, `XOR A : CP 28h : CP 28h : SCF` gives F = 81h
on a Z80 and used to give A9h.

It only shows in programs that test the Z80. To compare the two versions, [`tools/z80test/`](tools/z80test) has
Patrik Rak's (Raxoft) z80test 1.2a, also in a version that runs with the 2068 ROM (`tools/z80test/tc2068/`): z80ccf
tests the flags after a CCF following each instruction. This T80 passes z80full and z80ccf in another core.

## Building

Quartus Prime Lite 17.0.2 (the MiSTer one) or Lite 25.1 (with Cyclone V support): open `TC2068.qpf` and
Processing → Start Compilation. The result is `output_files/TC2068.rbf`. `sys/sys.qip` picks `sys/pll_q<version>.qip`
for the Quartus version: there are 17 and 25 (the same as 17). Compared with the official core, `ZX-Spectrum.sv`,
`rtl/turbosound.sv`, `rtl/divmmc.v`, `ZX-Spectrum.sdc` and the project (`TC2068.qpf`, `.qsf`, `.srf`) change, and
`rtl/tc2068.mif`, `rtl/tc2048.mif`, `tools/rom2mif.py` and `tools/faz_vhd.py` are added. `TC2068_T80Q` is built from
the `t80q` branch (only `rtl/T80/T80.vhd` changes). The TC2048 core comes from `TC2048.qpf`: the same files, with
`TC2048` defined in the `.qsf`; it gives `output_files/TC2048.rbf`.

With Quartus Lite 25.1 timing is met (November 2026: +0.7 ns setup slack on the 112 MHz clock; +0.48 ns in the T80Q
version). For that, also for
the other machines: the copy of banks 5 and 7 for the video (the VRAM) is written a clock later, through a register;
and `ZX-Spectrum.sdc` gives two clocks to the paths that start at what only changes with an OUT (the TC2068 ports #F4
and #FF, the DivMMC #E3) and at the Z80 refresh signal on the way to the SDRAM.

## Credits

- **The MiSTer ZX-Spectrum core:** Sorgelig and others (GPL; see [README_ZX-Spectrum.md](README_ZX-Spectrum.md)
  and the file headers).
- **The TC2068** (GPL, like the rest): António Vitor. AI (Claude) used.
- **The TS2068 ROM:** Amstrad (Sinclair) and Timex; see above.
