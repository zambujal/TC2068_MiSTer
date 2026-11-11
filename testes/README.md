# Testes do Timex TC2048 / TC2068

[English](README.en.md)

Um programa que testa um Timex Computer TC2048 ou TC2068: os dois cores deste repositório ([README](../README.md))
ou as máquinas verdadeiras. Vê pela ROM qual é a máquina, corre os testes e mostra os resultados no ecrã.

## Ficheiros

| Ficheiro | Para quê |
|---|---|
| `teste_timex.tap` | Os dois. Carrega-se com `LOAD ""`. |
| `teste_timex.dck` | TC2068: cartucho. No MiSTer: F12 → Load 2068 Cartridge. |
| `teste_timex.sna` | TC2048: snapshot de 48K. No MiSTer: F12 → Load Snapshot; com o esxDOS: `.snapload`. |

O programa corre em A000h e não volta ao BASIC. Para sair, faz-se reset; com o cartucho, Reset & Detach Cartridge.

## O que testa

Cada linha mostra os valores lidos em hexadecimal e, num Timex, um veredito:
- **verde**: como no original;
- **amarelo**: a mais (o original não tem, mas não estorva);
- **vermelho**: falta ou está errado.

| Linha | O que é |
|---|---|
| MAQUINA | Vista pela ROM: o salto do arranque em 0005h e o byte em 386Eh. TC2048, TC2068 ou ZX Spectrum 48K. |
| ROM | O CRC-16 (CCITT, começa em FFFFh) de 0000-3FFF. 18E8 = TC2048; E848 = 2068 (as ROMs do TS2068 e do TC2068 do Fuse e do ZEsarUX são iguais); FD5E = 48K. |
| EXROM | Só no TC2068: o CRC de 0000-1FFF com a F4 a 01h e o bit 7 da FF a 1. B9C6 = a EXROM do 2068; 192E = a mesma com os traps do esxDOS (o core com a DivMMC ligada). |
| Z80 SCF/CCF | Os flags depois de quatro sequências com SCF e CCF. 29 81 90 A9 = Zilog. O T80 do core oficial dá A9 e B8 nos do meio. |
| INT IM 2 BUS | O byte no bus na aceitação da INT tem de ser FFh. |
| PORTA FF | Escreve B8h e 00h e lê-os de volta. |
| FF BIT6 INT | As INTs em cerca de 3 imagens com o bit 6 a 0 e depois a 1. Com o bit 6 a 1 tem de dar 0. |
| PORTA 7FFD | Não pagina: é um 48K. |
| PORTA F4 | Só o TC2068 a tem. Lê-se de volta. |
| AY F5/F6 | O AY do TC2068: o registo 0 lê-se de volta. |
| AY FFFD | O AY nas portas do Spectrum 128. Nenhum dos dois o tem; os cores sim. |
| KEMPSTON 1F | O TC2048 tem; o TC2068 não. |
| FE SO EM FE | Escreve vermelho na porta FC. Num Timex a borda fica branca; num 48K fica vermelha. |
| PRETO / PRETO+BRIGHT | No TC2068 o preto com BRIGHT sai cinzento escuro; no TC2048 e no 48K os dois são pretos. |
| JOYSTICKS | O Kempston e os dois joysticks do TC2068 (registo 14 do AY), em directo. O número à direita é o byte lido. |

As teclas 1, 2 e 3 mostram os modos de vídeo da porta FF: o ecrã 1 (6000h), o hi-colour e o hi-res 512×192.
Qualquer tecla volta aos resultados.

Os testes são para 3,5 MHz: o da INT conta as imagens num tempo de CPU fixo.

## Compilar

Com o [sjasmplus](https://github.com/z00m128/sjasmplus) e o Python 3:

```
sjasmplus teste_timex.asm     # teste_timex.bin
sjasmplus cartucho.asm        # cartucho.bin (inclui o teste_timex.bin)
python3 faz_ficheiros.py      # teste_timex.tap, teste_timex.dck e teste_timex.sna
```

Nenhum ficheiro leva ROMs: o programa lê a ROM da máquina onde corre.

António Vitor. Foi usada IA (Claude).
