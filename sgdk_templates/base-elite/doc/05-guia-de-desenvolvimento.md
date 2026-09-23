# 05 - Guia de Desenvolvimento — __PROJECT_NAME__

## Para adicionar nova cena/fase

1. Criar logica em `src/rooms/` ou equivalente.
2. Registrar no switcher de estados em `main.c`.
3. Documentar budget em `doc/07-budget-vram-dma.md` e `doc/13-spec-cenas.md`.

## Para adicionar novo efeito

Perguntas obrigatorias:

- usa `float` ou `double`?
- depende de DMA excessivo por frame?
- exige callback solta fora do modulo central de H-Int?

Se alguma resposta for `sim`, replaneje antes de codar.

## Para adicionar dialogo em gameplay

1. Usar sistema de dialogo no `window plane` para nao herdar scroll de BG.
2. Limitar a fala a poucas linhas de leitura rapida.
3. Consultar `doc/12-roteiro.md` antes de escrever texto.

## Para evoluir assets

1. Manter placeholder procedural funcionando.
2. Introduzir asset real em paralelo.
3. Validar paleta, grid e custo.
4. Trocar a fonte do dado sem quebrar a cena.

## Regra pratica

Nao empurre complexidade para `main.c`.
Se uma feature atravessa input, estado, render e docs, ela precisa nascer com interfaces claras.
