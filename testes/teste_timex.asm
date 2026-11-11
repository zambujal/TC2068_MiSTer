; teste_timex.asm - teste do Timex TC2048 / TC2068 (os cores do MiSTer ou as maquinas verdadeiras)
; Ve a maquina pela ROM e testa: o Z80 (flags depois de SCF/CCF), o byte no bus na INT em IM 2, a porta FF
; (le-se de volta; o bit 6 desliga a INT), a 7FFD (48K), a F4 e a EXROM, o AY nas F5/F6 e nas FFFD/BFFD, o
; Kempston, a porta FE (so' no endereco FE), o preto com BRIGHT, os joysticks (em directo) e os modos de video
; da FF (teclas 1 a 3: ecra 1, hi-colour, hi-res). Corre em A000h e nao volta ao BASIC: sai-se com o reset.
;   TAP: 10 CLEAR 40959: LOAD "" CODE: RANDOMIZE USR 40960
;   DCK (TC2068): cartucho AROS no bloco 4 que copia o programa para A000h (cartucho.asm)
; sjasmplus teste_timex.asm -> teste_timex.bin
            device zxspectrum48
            org 0A000h

VARS        equ 0F000h
maq         equ VARS+0      ; 0 = ?, 1 = 48K, 2 = TC2048, 3 = TC2068 (pela ROM)
crc_rom     equ VARS+1      ; 2 bytes
crc_ex      equ VARS+3      ; 2 bytes
res1        equ VARS+5      ; Z80: POP AF (A=00h, F=28h) + SCF
res2        equ VARS+6      ; CP 28h, CP 28h, SCF
res3        equ VARS+7      ; CP 28h, CP 28h, CCF
res4        equ VARS+8      ; CP 28h, SET 0,B, SCF
resint      equ VARS+9      ; 0 = sem INT, 1 = o bus nao era FFh, 2 = FFh
ultvec      equ VARS+10     ; o vector da ultima INT (1 ou 2)
nints       equ VARS+11     ; INTs contadas
ff1         equ VARS+12     ; FF lida depois de B8h
ff2         equ VARS+13     ; FF lida depois de 00h
n0          equ VARS+14     ; INTs em ~3 imagens com FF bit 6 = 0
n1          equ VARS+15     ; o mesmo com FF bit 6 = 1
pag         equ VARS+16     ; C000h depois do teste da 7FFD (5Ah = nao pagina)
f4a         equ VARS+17     ; F4 lida depois de 01h
f4b         equ VARS+18     ; F4 lida depois de 00h
ay1a        equ VARS+19     ; F6 (registo 0) depois de 55h
ay1b        equ VARS+20     ; F6 depois de AAh
ay2a        equ VARS+21     ; FFFD (registo 0) depois de 55h
ay2b        equ VARS+22     ; FFFD depois de AAh
kemp        equ VARS+23     ; 1F (OR de 4 leituras)
tem_f4      equ VARS+24     ; 1 = a F4 le-se de volta
tem_ay68    equ VARS+25     ; 1 = AY nas F5/F6
tem_ay128   equ VARS+26     ; 1 = AY nas FFFD/BFFD
tem_kemp    equ VARS+27     ; 1 = Kempston
base_df     equ VARS+28     ; 40h (ecra 0) ou 60h (ecra 1): onde o chr escreve
base_at     equ VARS+29     ; 58h ou 78h: onde o corseg pinta
mjmask      equ VARS+30
mjcnt       equ VARS+31

TABL        equ 9E00h       ; tabela do CRC-16: bytes baixos
TABH        equ 9F00h       ;                   bytes altos

VERDE       equ 60h
AMARELO     equ 70h
VERMELHO    equ 57h
NEUTRO      equ 38h

R_MAQ       equ 1
R_ROM       equ 2
R_EX        equ 3
R_LEG       equ 4
R_Z80       equ 5
R_INT       equ 6
R_FF        equ 7
R_B6        equ 8
R_7FFD      equ 9
R_F4        equ 10
R_AY68      equ 11
R_AY128     equ 12
R_KEMP      equ 13
R_FE        equ 14
R_BR        equ 15
R_BR2       equ 16
R_JT        equ 18
R_JK        equ 19
R_J1        equ 20
R_J2        equ 21
R_T1        equ 22
R_T2        equ 23

inicio      di
            ld sp,0FE00h
            xor a
            out (0F4h),a    ; TC2068: tudo da HOME (no .dck desliga o cartucho)
            out (0FFh),a    ; ecra 0, INT ligada
            ld a,7
            out (0FEh),a
            call prepara
            call maquina
            call testes
            call desenha
ciclo       ei
            halt
            call joys
            ld bc,0F7FEh    ; teclas 1 a 5
            in a,(c)
            cpl
            and 7           ; 1, 2, 3
            jr z,ciclo
            rrca
            jp c,v_ecra1
            rrca
            jp c,v_hicol
            jp v_hires

; ---------------------------------------------------------------- preparacao
prepara     ld hl,VARS
            ld de,VARS+1
            ld bc,0FFh
            ld (hl),0
            ldir
            ld a,40h
            ld (base_df),a
            ld a,58h
            ld (base_at),a
            ld hl,0FE00h    ; IM 2: FE00h-FF00h = BBh e FF00h = BCh
            ld de,0FE01h
            ld bc,256
            ld (hl),0BBh
            ldir
            ld a,0BCh
            ld (0FF00h),a
            ld hl,stub1     ; bus 00h-FEh -> BBBBh
            ld de,0BBBBh
            ld bc,6
            ldir
            ld hl,stub2     ; bus FFh -> BCBBh
            ld de,0BCBBh
            ld bc,6
            ldir
            ld a,0FEh
            ld i,a
            im 2
            ld c,0          ; a tabela do CRC-16 (CCITT: 1021h)
pt1         ld h,c
            ld l,0
            ld b,8
pt2         add hl,hl
            jr nc,pt3
            ld a,h
            xor 10h
            ld h,a
            ld a,l
            xor 21h
            ld l,a
pt3         djnz pt2
            ld d,TABL/256
            ld e,c
            ld a,l
            ld (de),a
            inc d
            ld a,h
            ld (de),a
            inc c
            jr nz,pt1
            ret

stub1       push af         ; copiado para BBBBh
            ld a,1
            jp isr
stub2       push af         ; copiado para BCBBh
            ld a,2
            jp isr
isr         ld (ultvec),a
            ld a,(nints)
            inc a
            ld (nints),a
            pop af
            ei
            reti

; crc: o CRC-16 (CCITT, comeca em FFFFh) de BC bytes em HL -> DE
crc         ld de,0FFFFh
crc1        ld a,(hl)
            xor d
            push hl
            ld l,a
            ld h,TABH/256
            ld a,(hl)
            xor e
            ld d,a
            dec h
            ld e,(hl)
            pop hl
            inc hl
            dec bc
            ld a,b
            or c
            jr nz,crc1
            ret

; ---------------------------------------------------------------- a maquina, pela ROM
maquina     ld a,(0007h)    ; o JP do arranque: 11CBh no Spectrum e no TC2048, 0D31h no TC2068
            ld b,3
            cp 0Dh
            jr z,mq1
            ld b,0
            cp 11h
            jr nz,mq1
            ld a,(386Eh)    ; TC2048: OUT (FFh),A em 386Eh; no 48K e' FFh
            ld b,2
            cp 0D3h
            jr z,mq1
            ld b,1
            cp 0FFh
            jr z,mq1
            ld b,0
mq1         ld a,b
            ld (maq),a
            ld hl,0
            ld bc,4000h
            call crc
            ld (crc_rom),de
            ret

; ---------------------------------------------------------------- os testes (com a INT desligada)
testes
; 1. Z80: flags X/Y (bits 5 e 3) depois de SCF/CCF. Zilog 29 81 90 A9; o T80 do core oficial da' A9 e B8 nos do meio
            ld bc,0028h
            push bc
            pop af          ; o POP AF nao conta como escrita dos flags
            scf
            push af
            pop hl
            ld a,l
            ld (res1),a
            xor a
            cp 28h
            cp 28h          ; os flags escritos outra vez com o mesmo valor
            scf
            push af
            pop hl
            ld a,l
            ld (res2),a
            xor a
            cp 28h
            cp 28h
            ccf
            push af
            pop hl
            ld a,l
            ld (res3),a
            xor a
            cp 28h
            set 0,b         ; o SET nao escreve os flags
            scf
            push af
            pop hl
            ld a,l
            ld (res4),a

; 2. o byte no bus na aceitacao da INT (IM 2): FFh -> BCBBh (ultvec 2), outro -> BBBBh (ultvec 1)
            xor a
            out (0FFh),a
            ld (nints),a
            ld (ultvec),a
            ei
            ld bc,9000      ; ate' ~6 imagens
ti1         ld a,(nints)
            or a
            jr nz,ti2
            dec bc
            ld a,b
            or c
            jr nz,ti1
ti2         di
            ld a,(ultvec)
            ld (resint),a

; 3. a porta FF le-se de volta (B8h: modo 0, cores do hi-res 7, bit 7 = 1 sem nada na F4; depois 00h)
            ld a,0B8h
            out (0FFh),a
            in a,(0FFh)
            ld (ff1),a
            xor a
            out (0FFh),a
            in a,(0FFh)
            ld (ff2),a

; 4. FF bit 6 desliga a INT: as INTs num tempo fixo com o bit 6 a 0 e depois a 1
            call conta
            ld (n0),a
            ld a,40h
            out (0FFh),a
            call conta
            ld (n1),a
            xor a
            out (0FFh),a

; 5. 7FFD: o 48K nao pagina (C000h fica com o 5Ah escrito com a 7FFD a 17h)
            ld a,0A5h
            ld (0C000h),a
            ld bc,7FFDh
            ld a,17h
            out (c),a
            ld a,5Ah
            ld (0C000h),a
            ld a,10h
            out (c),a
            ld a,(0C000h)
            ld (pag),a

; 6. F4 e a EXROM (TC2068): FF bit 7 = 1 e F4 = 01h -> a EXROM em 0000h-1FFFh
            ld a,80h
            out (0FFh),a
            ld a,01h
            out (0F4h),a
            in a,(0F4h)
            ld (f4a),a
            cp 01h
            jr nz,t6b
            ld hl,0
            ld bc,2000h
            call crc
            ld (crc_ex),de
t6b         xor a
            out (0F4h),a
            in a,(0F4h)
            ld (f4b),a
            xor a
            out (0FFh),a
            ld a,(f4a)
            cp 01h
            jr nz,t7
            ld a,(f4b)
            or a
            jr nz,t7
            ld a,1
            ld (tem_f4),a

; 7. AY nas F5/F6 (TC2068): o registo 0 le-se de volta
t7          ld bc,00F5h
            xor a
            out (c),a
            ld c,0F6h
            ld a,55h
            out (c),a
            in a,(c)
            ld (ay1a),a
            ld a,0AAh
            out (c),a
            in a,(c)
            ld (ay1b),a
            xor a
            out (c),a       ; o registo 0 outra vez a 0
            ld c,0F5h
            ld a,7
            out (c),a
            ld c,0F6h
            ld a,3Fh
            out (c),a       ; registo 7: tudo calado, a porta A como entrada (os joysticks)
            ld a,(ay1a)
            cp 55h
            jr nz,t8
            ld a,(ay1b)
            cp 0AAh
            jr nz,t8
            ld a,1
            ld (tem_ay68),a

; 8. AY nas portas do 128 (FFFD selecciona, BFFD escreve, FFFD le)
t8          ld bc,0FFFDh
            xor a
            out (c),a
            ld b,0BFh
            ld a,55h
            out (c),a
            ld b,0FFh
            in a,(c)
            ld (ay2a),a
            ld b,0BFh
            ld a,0AAh
            out (c),a
            ld b,0FFh
            in a,(c)
            ld (ay2b),a
            ld b,0BFh
            xor a
            out (c),a
            ld a,(ay2a)
            cp 55h
            jr nz,t9
            ld a,(ay2b)
            cp 0AAh
            jr nz,t9
            ld a,1
            ld (tem_ay128),a

; 9. Kempston (1F): sem mexer le 000xxxxx; sem Kempston, normalmente FFh
t9          ld bc,001Fh
            ld de,0400h
t9a         in a,(c)
            or e
            ld e,a
            dec d
            jr nz,t9a
            ld a,e
            ld (kemp),a
            and 0E0h
            ret nz
            ld a,1
            ld (tem_kemp),a
            ret

; conta: as INTs em ~3,2 imagens (8600 x 26 T a 3,5 MHz) -> A
conta       xor a
            ld (nints),a
            ei
            ld bc,8600
co1         dec bc
            ld a,b
            or c
            jr nz,co1
            di
            ld a,(nints)
            ret

; ---------------------------------------------------------------- o ecra dos resultados
desenha     xor a
            out (0FFh),a
            ld a,40h
            ld (base_df),a
            ld a,58h
            ld (base_at),a
            ld a,NEUTRO
            call limpa
            ld a,7
            out (0FEh),a    ; borda branca
            ld bc,00FCh
            ld a,2
            out (c),a       ; vermelho na porta FC: so' uma ULA que so' veja o A0 (o 48K) muda a borda

            ld hl,t_tit     ; o titulo: preto com BRIGHT (no TC2068 sai cinzento escuro)
            ld bc,0000h
            call pr
            ld a,47h
            ld b,0
            call cor

            ld hl,t_maq
            ld bc,R_MAQ*256
            call pr
            ld a,(maq)
            add a,a
            ld e,a
            ld d,0
            ld hl,nomes_maq
            add hl,de
            ld a,(hl)
            inc hl
            ld h,(hl)
            ld l,a
            ld bc,R_MAQ*256+9
            call pr

            ld hl,t_rom
            ld bc,R_ROM*256
            call pr
            ld a,(crc_rom+1)
            ld bc,R_ROM*256+18
            call hex
            ld a,(crc_rom)
            call hex
            ld de,(crc_rom)
            ld ix,nomes_home
            call procura
            ld bc,R_ROM*256+23
            call pr

            ld a,(tem_f4)
            or a
            jr z,de1
            ld hl,t_ex
            ld bc,R_EX*256
            call pr
            ld a,(crc_ex+1)
            ld bc,R_EX*256+18
            call hex
            ld a,(crc_ex)
            call hex
            ld de,(crc_ex)
            ld ix,nomes_ex
            call procura
            ld bc,R_EX*256+23
            call pr
            jr de2
de1         ld hl,t_semex
            ld bc,R_EX*256
            call pr

de2         ld hl,t_leg
            ld bc,R_LEG*256
            call pr
            ld a,VERDE
            ld bc,R_LEG*256
            ld e,5
            call corseg
            ld a,AMARELO
            ld bc,R_LEG*256+15
            ld e,7
            call corseg

            ld hl,t_z80     ; 1. Z80
            ld bc,R_Z80*256
            call pr
            ld a,(res1)
            ld bc,R_Z80*256+13
            call hex
            inc c
            ld a,(res2)
            call hex
            inc c
            ld a,(res3)
            call hex
            inc c
            ld a,(res4)
            call hex
            ld a,(res1)
            cp 29h
            jr nz,z1
            ld a,(res2)
            cp 81h
            jr nz,z1
            ld a,(res3)
            cp 90h
            jr nz,z1
            ld a,(res4)
            cp 0A9h
            jr nz,z1
            ld hl,v_zilog
            ld a,VERDE
            jr z3
z1          ld a,(res2)
            cp 0A9h
            jr nz,z2
            ld a,(res3)
            cp 0B8h
            jr nz,z2
            ld hl,v_t80
            ld a,AMARELO
            jr z3
z2          ld hl,v_outro
            ld a,VERMELHO
z3          ld b,R_Z80
            call veredito

            ld hl,t_int     ; 2. INT
            ld bc,R_INT*256
            call pr
            ld a,(resint)
            cp 2
            jr nz,i1
            ld hl,t_vff
            ld bc,R_INT*256+13
            call pr
            ld hl,v_ok
            ld a,VERDE
            jr i3
i1          or a
            jr z,i2
            ld hl,t_vnff
            ld bc,R_INT*256+13
            call pr
            ld hl,v_falha
            ld a,VERMELHO
            jr i3
i2          ld hl,v_semint
            ld a,VERMELHO
i3          ld b,R_INT
            call veredito

            ld hl,t_ff      ; 3. FF le-se de volta
            ld bc,R_FF*256
            call pr
            ld a,(ff1)
            ld bc,R_FF*256+13
            call hex
            inc c
            ld a,(ff2)
            call hex
            ld a,(maq)
            cp 2
            jr c,f3         ; nao e' um Timex: so' os valores
            ld a,(ff1)
            cp 0B8h
            jr nz,f2
            ld a,(ff2)
            or a
            jr nz,f2
            ld hl,v_ok
            ld a,VERDE
            jr f2b
f2          ld hl,v_falha
            ld a,VERMELHO
f2b         ld b,R_FF
            call veredito

f3          ld hl,t_b6      ; 4. FF bit 6
            ld bc,R_B6*256
            call pr
            ld a,(n0)
            ld bc,R_B6*256+13
            call hex
            inc c
            ld a,(n1)
            call hex
            ld a,(n0)
            cp 2
            jr nc,b1
            ld hl,v_semint
            ld a,VERMELHO
            jr b3
b1          ld a,(n1)
            or a
            jr nz,b2
            ld hl,v_ok
            ld a,VERDE
            jr b3
b2          ld a,(maq)
            cp 2
            jr c,b4
            ld hl,v_falha
            ld a,VERMELHO
b3          ld b,R_B6
            call veredito

b4          ld hl,t_7ffd    ; 5. 7FFD
            ld bc,R_7FFD*256
            call pr
            ld a,(pag)
            ld bc,R_7FFD*256+13
            call hex
            ld a,(pag)
            cp 5Ah
            ld hl,v_48k
            ld a,VERDE
            jr z,p1
            ld hl,v_128k
            ld a,VERMELHO
p1          ld b,R_7FFD
            call veredito

            ld hl,t_f4      ; 6. F4 (so' o TC2068 a tem)
            ld bc,R_F4*256
            call pr
            ld a,(f4a)
            ld bc,R_F4*256+13
            call hex
            inc c
            ld a,(f4b)
            call hex
            ld a,(tem_f4)
            ld d,a
            ld e,2
            ld b,R_F4
            call vered2

            ld hl,t_ay68    ; 7. AY nas F5/F6 (so' o TC2068)
            ld bc,R_AY68*256
            call pr
            ld a,(ay1a)
            ld bc,R_AY68*256+13
            call hex
            inc c
            ld a,(ay1b)
            call hex
            ld a,(tem_ay68)
            ld d,a
            ld e,2
            ld b,R_AY68
            call vered2

            ld hl,t_ay128   ; 8. AY nas FFFD/BFFD (nenhum dos dois)
            ld bc,R_AY128*256
            call pr
            ld a,(ay2a)
            ld bc,R_AY128*256+13
            call hex
            inc c
            ld a,(ay2b)
            call hex
            ld a,(tem_ay128)
            ld d,a
            ld e,0
            ld b,R_AY128
            call vered2

            ld hl,t_kemp    ; 9. Kempston (so' o TC2048)
            ld bc,R_KEMP*256
            call pr
            ld a,(kemp)
            ld bc,R_KEMP*256+13
            call hex
            ld a,(tem_kemp)
            ld d,a
            ld e,1
            ld b,R_KEMP
            call vered2

            ld hl,t_fe      ; 10. FE so' no endereco FE (a borda)
            ld bc,R_FE*256
            call pr

            ld hl,t_br      ; 11. preto e preto com BRIGHT
            ld bc,R_BR*256
            call pr
            xor a
            ld bc,R_BR*256+22
            ld e,4
            call corseg
            ld a,40h
            ld bc,R_BR*256+27
            ld e,4
            call corseg
            ld hl,t_br48
            ld a,(maq)
            cp 3
            jr nz,br1
            ld hl,t_br68
br1         ld bc,R_BR2*256
            call pr

            ld hl,t_jt      ; os joysticks
            ld bc,R_JT*256
            call pr
            ld hl,t_jk
            ld bc,R_JK*256
            call pr
            ld a,(tem_ay68)
            or a
            jr z,dj1
            ld hl,t_j1
            ld bc,R_J1*256
            call pr
            ld hl,t_j2
            ld bc,R_J2*256
            call pr
            jr dj2
dj1         ld hl,t_jsem
            ld bc,R_J1*256
            call pr
dj2         ld hl,t_t1
            ld bc,R_T1*256
            call pr
            ld hl,t_t2
            ld bc,R_T2*256
            jp pr

; vered2: D = 1 se existe, E = quem o tem no original (bit 0 o TC2048, bit 1 o TC2068), B = linha
vered2      ld a,(maq)
            cp 2
            ret c           ; nao e' um Timex: so' os valores
            jr z,vd1
            rr e            ; TC2068: o bit 1
vd1         rr e            ; CF = o original tem
            ld a,d
            jr c,vd_orig
            or a
            jr nz,vd_amais
            ld hl,v_naoha
            ld a,VERDE
            jr veredito
vd_amais    ld hl,v_amais
            ld a,AMARELO
            jr veredito
vd_orig     or a
            jr z,vd_falta
            ld hl,v_ok
            ld a,VERDE
            jr veredito
vd_falta    ld hl,v_falta
            ld a,VERMELHO

; veredito: o texto HL na coluna 25 da linha B, com a cor A nas colunas 25 a 31
veredito    push hl
            push bc
            ld c,25
            ld e,7
            call corseg
            pop bc
            pop hl
            ld c,25
            jp pr

; procura: IX = tabela de (CRC, nome), acaba com o nome 0; DE = CRC -> HL = nome
procura     ld l,(ix+2)
            ld h,(ix+3)
            ld a,h
            or l
            jr z,pnao
            ld a,(ix+0)
            cp e
            jr nz,pseg
            ld a,(ix+1)
            cp d
            ret z
pseg        inc ix
            inc ix
            inc ix
            inc ix
            jr procura
pnao        ld hl,n_q
            ret

; ---------------------------------------------------------------- os joysticks, em cada imagem
joys        ld bc,001Fh
            in a,(c)
            ld d,a
            push de
            ld bc,R_JK*256+30
            call hex
            pop de
            xor a           ; Kempston: 0 direita, 1 esquerda, 2 baixo, 3 cima, 4 fogo (activos a 1)
            bit 3,d
            jr z,$+4
            or 1
            bit 2,d
            jr z,$+4
            or 2
            bit 1,d
            jr z,$+4
            or 4
            bit 0,d
            jr z,$+4
            or 8
            bit 4,d
            jr z,$+4
            or 10h
            ld e,a
            ld b,R_JK
            call mostrajoy
            ld a,(tem_ay68)
            or a
            ret z
            ld bc,00F5h     ; o registo 14 do AY: os joysticks do 2068 (A8 = o 1, A9 = o 2)
            ld a,14
            out (c),a
            ld bc,01F6h
            in a,(c)
            ld b,R_J1
            call joy68
            ld bc,02F6h
            in a,(c)
            ld b,R_J2
joy68       push bc
            push af
            ld c,30
            call hex
            pop af
            pop bc
            cpl             ; 0 cima, 1 baixo, 2 esquerda, 3 direita, 7 fogo (activos a 0)
            ld d,a
            and 0Fh
            bit 7,d
            jr z,$+4
            or 10h
            ld e,a

; mostrajoy: na linha B, as palavras CIM BAI ESQ DIR FOGO a verde se o bit (0 a 4) de E estiver a 1
mostrajoy   ld a,e
            ld (mjmask),a
            ld hl,posjoy
            ld a,5
mj1         ld (mjcnt),a
            ld c,(hl)
            inc hl
            ld e,(hl)
            inc hl
            push hl
            push bc
            ld a,(mjmask)
            rrca
            ld (mjmask),a
            ld a,NEUTRO
            jr nc,mj2
            ld a,VERDE
mj2         call corseg
            pop bc
            pop hl
            ld a,(mjcnt)
            dec a
            jr nz,mj1
            ret
posjoy      db 9,3, 13,3, 17,3, 21,3, 25,4

; ---------------------------------------------------------------- os modos de video da FF
v_ecra1     call solta      ; 1: o ecra 1 (6000h)
            ld a,60h
            ld (base_df),a
            ld a,78h
            ld (base_at),a
            ld a,28h        ; papel ciano
            call limpa
            ld hl,t_e1a
            ld bc,0100h
            call pr
            ld hl,t_e1b
            ld bc,0300h
            call pr
            ld hl,t_e1c
            ld bc,0400h
            call pr
            ld b,7          ; riscas de 4 pixeis nas linhas 7 a 14, uma cor de papel por linha
e1p         push bc
            ld d,0F0h
            ld e,0F0h
            call enche
            pop bc
            ld a,b
            sub 7
            ld c,a
            rlca
            rlca
            rlca
            ld d,a
            ld a,c
            xor 7
            or d
            push bc
            call cor
            pop bc
            inc b
            ld a,b
            cp 15
            jr nz,e1p
            ld hl,t_volta
            ld bc,1600h
            call pr
            ld a,40h
            ld (base_df),a
            ld a,58h
            ld (base_at),a
            ld a,01h
            out (0FFh),a
            call tecla
            jp volta

v_hicol     call solta      ; 2: hi-colour (as cores de cada linha de 8 pixeis em 6000h)
            ld a,NEUTRO
            call limpa      ; os atributos normais: sem o hi-colour ve-se preto em branco
            ld hl,t_hc1
            ld bc,0100h
            call pr
            ld hl,t_hc2
            ld bc,0200h
            call pr
            ld hl,t_hc3
            ld bc,0300h
            call pr
            ld b,6          ; linhas 6 a 17: metade tinta, metade papel
hcp         push bc
            ld d,0Fh
            ld e,0Fh
            call enche
            pop bc
            inc b
            ld a,b
            cp 18
            jr nz,hcp
            ld hl,t_volta
            ld bc,1600h
            call pr
            ld hl,6000h     ; as cores do hi-colour (6000h): preto em branco nos textos e
            ld de,6001h     ; uma cor por linha de pixeis nas linhas 6 a 17
            ld bc,17FFh
            ld (hl),NEUTRO
            ldir
            ld b,6
ar1         ld a,b
            and 18h
            or 60h
            ld h,a
            ld a,b
            and 7
            rrca
            rrca
            rrca
            ld l,a
            ld c,0          ; a linha de pixeis no caracter: papel C, tinta 7-C
ar2         ld a,c
            rlca
            rlca
            rlca
            ld d,a
            ld a,c
            xor 7
            or d
            push hl
            ld e,32
ar3         ld (hl),a
            inc l
            dec e
            jr nz,ar3
            pop hl
            inc h
            inc c
            ld a,c
            cp 8
            jr nz,ar2
            inc b
            ld a,b
            cp 18
            jr nz,ar1
            ld a,02h
            out (0FFh),a
            call tecla
            jp volta

v_hires     call solta      ; 3: hi-res 512x192 (as colunas pares do ecra 0, as impares do ecra 1)
            ld a,NEUTRO
            call limpa
            ld a,60h
            ld (base_df),a
            ld a,78h
            ld (base_at),a
            ld a,NEUTRO
            call limpa
            ld a,40h
            ld (base_df),a
            ld a,58h
            ld (base_at),a
            ld hl,t_hr1
            ld bc,0100h
            call pr64
            ld hl,t_regua
            ld bc,0300h
            call pr64
            ld hl,t_hr2
            ld bc,0C00h
            call pr64
            ld hl,t_volta
            ld bc,1600h
            call pr64
            ld b,6          ; linhas verticais de 1 pixel nas linhas 6 a 9 dos dois ecras
hrp         push bc
            ld d,0AAh
            ld e,0AAh
            call enche
            pop bc
            push bc
            ld a,60h
            ld (base_df),a
            ld d,0AAh
            ld e,0AAh
            call enche
            ld a,40h
            ld (base_df),a
            pop bc
            inc b
            ld a,b
            cp 10
            jr nz,hrp
            ld a,06h        ; hi-res, cores 000: tinta preta, papel branco
            out (0FFh),a
            call tecla

volta       xor a
            out (0FFh),a
            call desenha
            jp ciclo

; solta: espera que nao haja tecla nenhuma; tecla: espera uma tecla e que a soltem
solta       ei
            halt
            xor a
            in a,(0FEh)
            cpl
            and 1Fh
            jr nz,solta
            ret
tecla       ei
            halt
            xor a
            in a,(0FEh)
            cpl
            and 1Fh
            jr z,tecla
            jr solta

; ---------------------------------------------------------------- rotinas de ecra
; limpa: os pixeis em (base_df) a 0 e os atributos em (base_at) com A
limpa       push af
            ld a,(base_df)
            ld h,a
            ld l,0
            ld d,h
            ld e,1
            ld bc,17FFh
            ld (hl),l
            ldir
            ld a,(base_at)
            ld h,a
            ld l,0
            ld d,h
            ld e,1
            ld bc,2FFh
            pop af
            ld (hl),a
            ldir
            ret

; enche: as 8 linhas de pixeis da linha B (ecra em base_df): D nas pares, E nas impares
enche       ld a,b
            and 18h
            ld h,a
            ld a,(base_df)
            or h
            ld h,a
            ld a,b
            and 7
            rrca
            rrca
            rrca
            ld l,a
            ld c,8
en1         push hl
            ld a,c          ; C = 8..1: par na linha 0
            and 1
            ld a,d
            jr z,en2
            ld a,e
en2         ld b,32
en3         ld (hl),a
            inc l
            djnz en3
            pop hl
            inc h
            dec c
            jr nz,en1
            ret

; pr: a string em HL (acaba em 0) na linha B (0-23), coluna C (0-31)
pr          ld a,(hl)
            or a
            ret z
            push hl
            push bc
            call chr
            pop bc
            pop hl
            inc hl
            inc c
            jr pr

; pr64: o mesmo em hi-res, coluna C de 0 a 63
pr64        ld a,(hl)
            or a
            ret z
            push hl
            push bc
            call chr64
            pop bc
            pop hl
            inc hl
            inc c
            jr pr64

; chr64: o caracter A na coluna C (0-63) do hi-res: as pares no ecra 0, as impares no ecra 1
chr64       push af
            ld a,c
            srl a
            ld c,a
            ld a,40h
            jr nc,c64a
            ld a,60h
c64a        ld (base_df),a
            pop af
            call chr
            ld a,40h
            ld (base_df),a
            ret

; chr: o caracter A na linha B, coluna C, com a fonte da ROM (3D00h), no ecra em base_df
chr         ld l,a
            ld h,0
            add hl,hl
            add hl,hl
            add hl,hl
            ld de,3C00h
            add hl,de
            ld a,b
            and 18h
            ld d,a
            ld a,(base_df)
            or d
            ld d,a
            ld a,b
            and 7
            rrca
            rrca
            rrca
            or c
            ld e,a
            ld b,8
chr1        ld a,(hl)
            ld (de),a
            inc hl
            inc d
            djnz chr1
            ret

; hex: o byte A em hexadecimal na linha B, coluna C (C avanca 2)
hex         push af
            rrca
            rrca
            rrca
            rrca
            call nib
            pop af
nib         and 0Fh
            add a,'0'
            cp '9'+1
            jr c,nib1
            add a,7
nib1        push bc
            call chr
            pop bc
            inc c
            ret

; cor: a linha B toda com a cor A; corseg: E atributos com a cor A na linha B a partir da coluna C (em base_at)
cor         ld c,0
            ld e,32
corseg      push af
            ld l,b
            ld h,0
            add hl,hl
            add hl,hl
            add hl,hl
            add hl,hl
            add hl,hl
            ld a,(base_at)
            add a,h
            ld h,a
            ld a,l
            or c
            ld l,a
            pop af
            ld b,e
cs1         ld (hl),a
            inc hl
            djnz cs1
            ret

; ---------------------------------------------------------------- textos
nomes_maq   dw n_desc, n_48k, n_2048, n_2068
nomes_home  dw 0E848h, h_2068   ; HOME do TS2068 e do TC2068 (iguais)
            dw 018E8h, h_2048   ; TC2048
            dw 0FD5Eh, h_48     ; ZX Spectrum 48K
            dw 0, 0
nomes_ex    dw 0B9C6h, x_2068   ; EXROM do TS2068/TC2068
            dw 0192Eh, x_esx    ; a mesma com os traps do esxDOS (o core com o esxDOS ligado, o ESX2068)
            dw 0, 0

t_tit       db "TESTE DO TIMEX TC2048/TC2068 V1 ",0
t_maq       db "MAQUINA:",0
n_desc      db "DESCONHECIDA",0
n_48k       db "ZX SPECTRUM 48K",0
n_2048      db "TIMEX TC2048",0
n_2068      db "TIMEX TC2068",0
t_rom       db "ROM 0000-3FFF CRC",0
t_ex        db "EXROM (F4)    CRC",0
t_semex     db "EXROM (F4): NAO HA",0
h_2068      db "TS/TC2068",0
h_2048      db "TC2048",0
h_48        db "48K",0
x_2068      db "2068",0
x_esx       db "2068+ESX",0
n_q         db "?",0
t_leg       db "VERDE=ORIGINAL AMARELO=A MAIS",0
t_z80       db "Z80 SCF/CCF",0
t_int       db "INT IM 2 BUS",0
t_vff       db "FF",0
t_vnff      db "NAO FF",0
t_ff        db "PORTA FF",0
t_b6        db "FF BIT6 INT",0
t_7ffd      db "PORTA 7FFD",0
t_f4        db "PORTA F4",0
t_ay68      db "AY F5/F6",0
t_ay128     db "AY FFFD",0
t_kemp      db "KEMPSTON 1F",0
t_fe        db "FE SO EM FE: A BORDA FICA BRANCA",0
t_br        db "PRETO / PRETO+BRIGHT",0
t_br48      db "OS DOIS PRETOS (2048 E 48K)",0
t_br68      db "O 2.o CINZENTO ESCURO (2068)",0
t_jt        db "JOYSTICKS (MEXE-OS):",0
t_jk        db "KEMPSTON CIM BAI ESQ DIR FOGO",0
t_j1        db "2068 J1  CIM BAI ESQ DIR FOGO",0
t_j2        db "2068 J2  CIM BAI ESQ DIR FOGO",0
t_jsem      db "JOYSTICKS DO 2068: NAO HA",0
t_t1        db "TECLAS: 1 ECRA 1   2 HI-COLOUR",0
t_t2        db "3 HI-RES. NOS MODOS, TECLA VOLTA",0
v_zilog     db "ZILOG",0
v_t80       db "T80",0
v_outro     db "OUTRO",0
v_ok        db "OK",0
v_falha     db "FALHA",0
v_semint    db "SEM INT",0
v_48k       db "48K",0
v_128k      db "PAGINA",0
v_naoha     db "NAO HA",0
v_amais     db "A MAIS",0
v_falta     db "FALTA",0
t_e1a       db "ECRA 1 (6000h): MODO 1 DA FF",0
t_e1b       db "SE VES ISTO, O SEGUNDO ECRA",0
t_e1c       db "DO TIMEX FUNCIONA.",0
t_hc1       db "HI-COLOUR (MODO 2 DA PORTA FF):",0
t_hc2       db "UMA COR POR CADA LINHA DE 8",0
t_hc3       db "PIXEIS (CORES EM 6000h).",0
t_hr1       db "HI-RES 512 x 192 (MODO 6 DA PORTA FF): 64 COLUNAS DE TEXTO",0
t_regua     db "0123456789012345678901234567890123456789012345678901234567890123",0
t_hr2       db "SE A REGUA TEM OS 64 ALGARISMOS SEGUIDOS, O HI-RES FUNCIONA.",0
t_volta     db "QUALQUER TECLA VOLTA",0
fim
            assert fim <= 0BBBBh
            savebin "teste_timex.bin",inicio,fim-inicio
