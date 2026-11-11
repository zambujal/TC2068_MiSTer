# Timex TC2048 / TC2068 tests

[Português](README.md)

A program that tests a Timex Computer TC2048 or TC2068: the two cores in this repository
([README](../README.en.md)) or the real machines. It tells the machine from its ROM, runs the tests and shows the
results on the screen.

## Files

| File | For |
|---|---|
| `teste_timex.tap` | Both. Load it with `LOAD ""`. |
| `teste_timex.dck` | TC2068: cartridge. On the MiSTer: F12 → Load 2068 Cartridge. |
| `teste_timex.sna` | TC2048: 48K snapshot. On the MiSTer: F12 → Load Snapshot; with esxDOS: `.snapload`. |

The program runs at A000h and does not go back to BASIC. To leave it, reset; with the cartridge, Reset & Detach
Cartridge.

## What it tests

Each line shows the values read, in hex, and on a Timex a verdict:
- **green**: as on the original;
- **yellow**: extra (the original does not have it, but it does no harm);
- **red**: missing or wrong.

The screen is in Portuguese.

| Line | What it is |
|---|---|
| MAQUINA (machine) | From the ROM: the start-up jump at 0005h and the byte at 386Eh. TC2048, TC2068 or ZX Spectrum 48K. |
| ROM | The CRC-16 (CCITT, starting at FFFFh) of 0000-3FFF. 18E8 = TC2048; E848 = 2068 (the TS2068 and TC2068 ROMs that come with Fuse and ZEsarUX are the same); FD5E = 48K. |
| EXROM | TC2068 only: the CRC of 0000-1FFF with F4 at 01h and FF bit 7 set. B9C6 = the 2068 EXROM; 192E = the same with the esxDOS traps (the core with the DivMMC on). |
| Z80 SCF/CCF | The flags after four sequences with SCF and CCF. 29 81 90 A9 = Zilog. The official core's T80 gives A9 and B8 in the middle ones. |
| INT IM 2 BUS | The bus byte on interrupt acknowledge must be FFh. |
| PORTA FF | Writes B8h and 00h and reads them back. |
| FF BIT6 INT | Interrupts in about 3 frames with bit 6 at 0 and then at 1. With bit 6 at 1 it must be 0. |
| PORTA 7FFD | No paging: it is a 48K. |
| PORTA F4 | Only the TC2068 has it. It reads back. |
| AY F5/F6 | The TC2068 AY: register 0 reads back. |
| AY FFFD | The AY on the Spectrum 128 ports. Neither machine has it; the cores do. |
| KEMPSTON 1F | The TC2048 has it; the TC2068 does not. |
| FE SO EM FE | Writes red to port FC. On a Timex the border stays white; on a 48K it turns red. |
| PRETO / PRETO+BRIGHT | On the TC2068 BRIGHT black shows as dark grey; on the TC2048 and the 48K both are black. |
| JOYSTICKS | The Kempston and the two TC2068 joysticks (AY register 14), live. The number on the right is the byte read. |

Keys 1, 2 and 3 show the port FF video modes: screen 1 (6000h), hi-colour and hi-res 512×192. Any key goes back
to the results.

The tests are for 3.5 MHz: the interrupt one counts frames in a fixed CPU time.

## Building

With [sjasmplus](https://github.com/z00m128/sjasmplus) and Python 3:

```
sjasmplus teste_timex.asm     # teste_timex.bin
sjasmplus cartucho.asm        # cartucho.bin (includes teste_timex.bin)
python3 faz_ficheiros.py      # teste_timex.tap, teste_timex.dck and teste_timex.sna
```

No file carries ROMs: the program reads the ROM of the machine it runs on.

António Vitor. AI (Claude) used.
