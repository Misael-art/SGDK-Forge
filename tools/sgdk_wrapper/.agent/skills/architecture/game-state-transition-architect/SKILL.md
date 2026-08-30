---
name: game-state-transition-architect
description: Use quando cenas, menus, fases ou cutscenes SGDK precisarem trocar ownership de VRAM, CRAM, sprites, callbacks, input ou audio com fade e teardown deterministico.
---

# Game State Transition Architect

Define a fronteira entre estados. Nao implementa gameplay; impede heranca
acidental de recursos e callbacks.

## Contrato Operacional

### Entrada minima

- estados de origem e destino
- recursos e owners ativos
- politica de fade, input e audio
- filas DMA, H-Int/V-Int e callbacks aplicaveis

### Saida minima

- `state_transition_contract`
- ordem de teardown/load
- ownership antes/depois
- plano de rollback e fixtures

### Passa quando

- transicao e nao reentrante
- input fica bloqueado durante a janela critica
- callbacks, sprites, scroll, CRAM e audio antigos sao encerrados
- DMA pendente e drenado ou invalidado antes do novo owner
- destino restaura corretamente em retorno, reset e falha

### Handoff para proxima etapa

- entregar contrato a `scene-state-architect` e `sgdk-runtime-coder`
- entregar custos de reload a `megadrive-vdp-budget-analyst`

## Regras

- Cada recurso tem owner anterior, acao de saida e owner seguinte.
- Fade nao substitui teardown.
- Cena nova nao herda H-Int, palette cycling, camera shake ou input pendente.
- `VDP_clearPlane` limpa um plano; nao encerra sprites, WINDOW ou callbacks.
- `PAL_fadeInAll` exige paleta valida da cena destino.

## Anti-padroes

- liberar input antes do fim do load
- carregar nova cena sobre fila DMA antiga
- trocar scene id sem reset simetrico
- usar delay fixo como mutex
