; cartucho.asm - o teste_timex.bin num cartucho do TC2068 (AROS no bloco 4 do DOCK): copia-o para A000h e salta
; sjasmplus cartucho.asm -> cartucho.bin (8K); o faz_ficheiros.py junta o cabecalho do .dck
            device zxspectrum48
            org 8000h
            db 2            ; codigo maquina
            db 2            ; AROS
            dw entrada      ; arranque
            db 0EFh         ; so' o bloco 4 (activo a 0)
            db 1            ; arranca sozinho
            dw 0            ; RAM a reservar
entrada     di
            ld sp,0FE00h
            ld hl,carga
            ld de,0A000h
            ld bc,fimcarga-carga
            ldir
            jp 0A000h       ; o programa desliga o cartucho (F4 = 0) logo no inicio
carga       incbin "teste_timex.bin"
fimcarga
            assert fimcarga <= 0A000h
            savebin "cartucho.bin",8000h,2000h
