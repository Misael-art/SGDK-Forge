# 05 - Guia de Desenvolvimento

## Para adicionar um novo planeta

1. criar paletas e textos em `src/game/planets.c`
2. definir callbacks do `PlanetScene`
3. documentar tecnica dominante no codex
4. registrar o budget em `doc/07-budget-vram-dma.md`

## Para adicionar um novo efeito

Perguntas obrigatorias:

- usa `float` ou `double`?
- depende de DMA excessivo por frame?
- exige callback solta fora do `hint_manager`?

Se alguma resposta for `sim`, replaneje antes de codar.

## Para adicionar dialogo em gameplay

1. usar `Dialogue_open(...)` em vez de desenhar texto direto no planeta
2. manter a caixa no `window plane` para nao herdar scroll de `BG_A` ou `BG_B`
3. limitar a fala a poucas linhas de leitura rapida
4. decidir explicitamente se o dialogo so comenta ou se conclui o micro-objetivo

## Para evoluir assets

1. manter placeholder procedural funcionando
2. introduzir asset real em paralelo
3. validar paleta, grid e custo
4. trocar a fonte do dado sem quebrar a cena

## Regra pratica

Nao empurre complexidade para `main.c`.
Se uma feature atravessa input, estado, render e docs, ela precisa nascer com interfaces claras.
