# Runtime mugen2sgdk_forge (C, SGDK 2.11)

Runtime genérico de luta 1×1 que executa os dados gerados pelo conversor. É instalado no
projeto por `python3 -m mugen2sgdk_forge install-runtime <projeto>` (cabeçalhos em `inc/mg/`,
fontes em `src/mg/`). **Edite aqui, nunca a cópia no projeto.** `mg_ops.h` é gerado a partir
de `ir/opcodes.py` e `ir/controllers.py`.

Regras: sem `float`/`double`/`malloc`; ponto fixo 24.8 (`mgfx`); nenhum DMA manual — o upload de
tiles é feito pelo `SPR_update()` do SGDK dentro do VBlank.

## Módulos

| Arquivo | Responsabilidade |
|---|---|
| `mg_types.h` | contrato de dados gerador ↔ runtime (`MgCharDef`, quadros, caixas, estados, comandos) |
| `mg_vm.c` | VM de expressões/triggers (espelho de `ir/vm.py`) |
| `mg_char.c` | estados e controladores MUGEN, custom state, animação, física, reconhecimento de comandos |
| `mg_fight.c` | ordem do tick, Clsn1×Clsn2, acerto/defesa, projéteis, explods, empurrão, câmera, render, rounds, HUD, CPU |

## Semântica MUGEN coberta

- Ordem por tick: entrada → estados −3/−2/−1 → estado atual (um `ChangeState` executa o novo
  estado no mesmo tick) → física → animação → projéteis/explods → colisões → empurrão/câmera.
- Statedef: `type`, `movetype`, `physics`, `anim`, `ctrl`, `velset`, `poweradd`, `sprpriority`,
  `juggle`, `facep2`, `hitdefpersist`, `movehitpersist`, `hitcountpersist`.
- Transições que o motor MUGEN faz sozinho com `ctrl=1` (andar, agachar, pular, defender) e o
  pouso automático de `physics = A` → 52.
- HitDef: dano/dano na defesa, `pausetime` (congela o atacante e treme o defensor), `hitflag` /
  `guardflag`, velocidades no chão e no ar, `fall`, `p1stateno` / `p2stateno` (custom state),
  `getpower` / `givepower`, `kill`, faísca (`sparkno` do próprio AIR) e sons de acerto/defesa.
- Projéteis (até 4 por jogador), explods (6 no total), SuperPause, Target* (arremessos), VarSet/Add/Random.

## Divergências declaradas

| Tema | Comportamento aqui | Motivo |
|---|---|---|
| Juggle | lido, não limita combos | falta o contador de juggle por golpe |
| `hitdef priority` / trade | o primeiro que colide vence | sem resolução de prioridade |
| `ChangeAnim2` | usa a animação do próprio personagem | as sheets são por personagem, sem busca cruzada por grupo/imagem |
| Blend (A/S) | desenhado opaco | o VDP não tem transparência |
| `AfterImage`, `PalFX`, `EnvColor` | ignorados (registrados no relatório) | exigiriam CRAM dinâmica ou sprites extras |
| Helpers | não suportados | seriam personagens completos |
| Efeitos dos 2 jogadores | compartilham PAL3 (paleta de efeitos do P1) | só há 4 paletas de hardware |
| VFlip | espelha sem corrigir o eixo | raro nos pacotes |
| Palco | limites de 640 px e chão fixo em y=200, sem arte | stage entra na Etapa 4 |
| HUD | texto provisório | a lifebar convertida entra na etapa de screenpack |
| IA | reproduz como entrada comandos aleatórios do `.cmd` | reimplementação; o personagem não tem IA própria |
