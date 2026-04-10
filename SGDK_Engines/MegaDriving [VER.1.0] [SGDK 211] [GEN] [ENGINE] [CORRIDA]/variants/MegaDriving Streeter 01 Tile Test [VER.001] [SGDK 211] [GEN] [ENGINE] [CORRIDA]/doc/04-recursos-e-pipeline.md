# Recursos e Pipeline

## Pasta `../../upstream/streeter/01_tile_test/res/`

Organize recursos por intencao, nao por acaso:

- `res/gfx/` para imagens gerais
- `res/sprites/` para personagens e animacoes
- `res/tilemaps/` para fases e cenarios
- `res/sfx/` para efeitos sonoros
- `res/music/` para musica

## Regras praticas do Mega Drive

- Sprites e tiles devem respeitar grade de 8x8 pixels
- Paletas devem ser pensadas cedo para evitar retrabalho
- Recursos grandes demais devem ser revisados antes de virar problema de VDP

## Papel do wrapper no pipeline

O wrapper central pode:

- validar recursos
- corrigir problemas comuns de transparencia
- aplicar autofix em `sprite.res`
- reaplicar migracoes SGDK quando necessario

## Boa pratica

Quando um recurso quebra o build, registre a causa e a solucao em `doc/`.
Isso transforma erro recorrente em conhecimento reaproveitavel.
