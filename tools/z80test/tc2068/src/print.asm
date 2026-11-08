; Simple printing module.
;
; Copyright (C) 2012-2023 Patrik Rak (patrik@raxoft.cz)
;
; This source code is released under the MIT license, see included license.txt.
;
; Changed in 2026 for the TS2068/TC2068: printinit finds CHAN-OPEN in either ROM (see below), and
; printchr sets IM 1 before EI: the last test (IM N) leaves the Z80 in IM 0, where an interrupt runs
; the byte on the bus instead of RST 38h. That byte is FFh (= RST 38h) on a real Spectrum or Timex, not
; always on an FPGA core; BASIC runs in IM 1.


; CHAN-OPEN is at 0x1601 in the 48K ROM (and in the TC2048 one), at 0x1230 in the TS2068/TC2068 ROM
; (the same routine, moved; the 2068 has a RET at 0x1601). The 48K ROM has ADD A,A (0x87) at 0x1601.
printinit:  ld      a,(0x1601)
            cp      0x87
            ld      a,2
            jp      z,0x1601    ; CHAN-OPEN, 48K
            jp      0x1230      ; CHAN-OPEN, TS2068/TC2068


print:      ex      (sp),hl
            call    printhl
            ex      (sp),hl
            ret

printhl:
.loop       ld      a,(hl)
            inc     hl
            or      a
            ret     z
            call    printchr
            jr      .loop


printdeca:  ld      h,a
            ld      b,-100
            call    .digit
            ld      b,-10
            call    .digit
            ld      b,-1

.digit      ld      a,h
            ld      l,'0'-1
.loop       inc     l
            add     a,b
            jr      c,.loop
            sub     b
            ld      h,a
            ld      a,l
            jr      printchr


printcrc:   ld      b,4

printhexs:
.loop       ld      a,(hl)
            inc     hl
            call    printhexa
            djnz    .loop
            ret


printhexa:  push    af
            rrca
            rrca
            rrca
            rrca
            call    .nibble
            pop     af

.nibble     or      0xf0
            daa
            add     a,0xa0
            adc     a,0x40

printchr:   push    iy
            ld      iy,0x5c3a   ; ERR-NR
            push    de
            push    bc
            exx
            im      1           ; the IM N test leaves IM 0 (TC2068 change, see the top)
            ei
            ; out     (0xff),a
            rst     0x10
            di
            exx
            pop     bc
            pop     de
            pop     iy
            ret

; EOF ;
