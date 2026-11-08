# z80test 1.2a

Os testes do Z80 de Patrik Rak (Raxoft), tal como vêm no `z80test-1.2a.zip` de
[github.com/raxoft/z80test](https://github.com/raxoft/z80test) (sem as fontes, que estão lá). Licença MIT:
`license.txt`; o que o autor diz de cada teste: `readme.txt`.

- `z80full`: todos os flags e registos; `z80doc`: os registos e só os flags documentados;
- `z80flags`: todos os flags; `z80docflags`: só os flags documentados;
- `z80ccf`: os flags depois de um CCF a seguir a cada instrução. É o que mostra o registo Q (em "O Z80" no
  [README](../../README.md)): o `TC2068_T80Q` deve passar todos;
- `z80memptr`: os flags depois de um BIT N,(HL) a seguir a cada instrução (o MEMPTR);
- `z80ccfscr`: mostra no ecrã se o SCF/CCF dá flags ao acaso (num core dá sempre o mesmo).

No TC2068: F12 → **Load Tape** → o `.tap`, e `LOAD ""` (ou o `.tapein` do esxDOS). Os testes escrevem com o RST 10,
que a ROM do 2068 também tem. No "scroll?", carregar numa tecla e largar logo: uma tecla presa estraga os testes do
INI/IND (lêem a porta do teclado). O z80full demora vários minutos.

*In English:* Patrik Rak's Z80 tests, as in `z80test-1.2a.zip` from the link above (MIT licence, `license.txt`).
Load a `.tap` with F12 → Load Tape and `LOAD ""`; on "scroll?" tap a key, do not hold it. `z80ccf` is the one that
shows the Q register: `TC2068_T80Q` should pass all of it.
