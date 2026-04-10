# 03 - Arquitetura

## Visao geral

`main.c` ficou minimo de proposito:

1. inicializa o `GameContext`
2. roda `Game_update()`
3. roda `Game_draw()`
4. fecha o frame com `SYS_doVBlankProcess()`

## Modulos

- `src/core/game.c`
  - bootstrap do VDP
  - leitura de input
  - troca de estados
  - callback de VBlank

- `src/states/flow.c`
  - `boot`
  - `title`
  - `story`
  - `planet`
  - `travel`
  - `pause`
  - `codex`
  - `credits`

- `src/game/player.c`
  - fisica em `fix16` / `fix32`
  - pulo e planar curto
  - cachecol segmentado
  - sprites de hardware

- `src/game/planets.c`
  - catalogo de planetas (baseline: 4; arquitetura: 12 ids com placeholders)
  - objetivos
  - paletas
  - scrolls e regras de progressao

- `src/game/travel.c`
  - mapeamento de pares de planetas para `TravelId` (A–K)
  - logica de transicao do estado `travel` (frame/radius/saida)

- `src/audio/audio.c`
  - voces e SFX curtos (XGM2) por encontro
  - init e rotas de execucao de audio (baseline)

- `src/render/render.c`
  - geracao procedural de tiles
  - HUD e telas textuais
  - discos/planetas, torres, dunas e travel

- `src/render/hint_manager.c`
  - configuracao de H-Int
  - split de paleta para o planeta do lampiao

## Interfaces centrais

`inc/project.h` define:

- `GameStateId`
- `PlanetId`
- `PlanetScene`
- `FxProfile`
- `PlayerController`
- `ScarfSegment`

## Politicas rigidas

- sem `float`
- sem `double`
- sem alocacao dinamica por frame
- sem dependencia externa ao SGDK/C padrao
- H-Int sempre centralizado no `hint_manager`
