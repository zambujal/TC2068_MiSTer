# z80test 1.2a para o TC2068

O z80test original chama o CHAN-OPEN da ROM do 48K em `0x1601` para escrever no ecrã de cima. Na ROM do TS2068/TC2068
a mesma rotina está em `0x1230` e em `0x1601` há um RET: o canal fica o que estava e os testes acabam com o erro
"Out of screen". Esta versão muda só o `src/print.asm`:
- o `printinit` vê o byte de `0x1601` (`87h`, ADD A,A, na ROM do 48K e na do TC2048) e chama o CHAN-OPEN de uma ROM
  ou da outra. Serve nas duas;
- o `printchr` põe IM 1 antes do EI. O último teste (IM N) deixa o Z80 em IM 0, e em IM 0 uma interrupção executa o
  byte que está no barramento em vez do RST 38h. Num Spectrum ou Timex verdadeiro esse byte é FFh (= RST 38h); no
  core, no modo TC2068, não era, e no fim do teste o 2068 não voltava bem ao BASIC.

Os `.tap` desta pasta fazem-se com o sjasm 0.42c (o assembler do autor; com ele, as fontes sem esta mudança dão os
`.tap` originais byte a byte) e o mktap, como no `Makefile`. O `z80ccfscr` não escreve com a ROM: usa-se o original.

No TC2068: F12 → Load Tape → `z80ccf.tap` (ou outro) e `LOAD ""`. No "scroll?", carregar numa tecla e largar logo.

z80test: Copyright (c) 2012-2023 Patrik Rak, licença MIT (`license.txt`); original em
[github.com/raxoft/z80test](https://github.com/raxoft/z80test).

*In English:* the original z80test calls the 48K ROM's CHAN-OPEN at `0x1601`; on the TS2068/TC2068 ROM it is at
`0x1230` (`0x1601` holds a RET), so the tests stop with "Out of screen". Here `printinit` checks the byte at `0x1601`
and calls the right one: these TAPs work with both ROMs. `printchr` also sets IM 1 before EI: the last test (IM N)
leaves IM 0, where an interrupt runs the byte on the bus (FFh = RST 38h on real hardware, not always on a core).
Built with sjasm 0.42c (which reproduces the original TAPs from the unchanged sources).
