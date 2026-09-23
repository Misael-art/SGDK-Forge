# 03 - Arquitetura - Celestial Chase Revive

## Status

Arquitetura especificada, ainda nao implementada.

## Modelo de Aplicacao

O runtime deve ser organizado como scene manager deterministico:

- `APP_SCENE_BRANDING`
- `APP_SCENE_TITLE`
- `APP_SCENE_OPENING_CUTSCENE`
- `APP_SCENE_RACE`
- `APP_SCENE_UPGRADE`
- `APP_SCENE_BOSS_APPROACH`
- `APP_SCENE_FINAL_BOSS`
- `APP_SCENE_RESULT`
- `APP_SCENE_CREDITS`
- `APP_SCENE_PAUSE`
- `APP_SCENE_GAME_OVER`
- `APP_SCENE_CONTINUE`

Cada cena possui `enter`, `update`, `exit` e `teardown`.

## Modulos Planejados

- `src/core/app.*`: boot, scene dispatch, frame clock.
- `src/core/scene_manager.*`: troca de cena, mutex de transicao, fade/flush.
- `src/system/input.*`: leitura de 3/6 botoes, buffer e pause.
- `src/system/audio.*`: XGM2, SFX, stingers e prioridades.
- `src/system/save_data.*`: SRAM, magic, versao, checksum.
- `src/ui/front_end.*`: branding, title, menu, records e creditos com atlas proprio.
- `src/ui/font.*`: glyph cache custom; SGDK default somente para debug.
- `src/render/vdp_owner.*`: owners de BG_A, BG_B, WINDOW, CRAM, HScroll e sprites.
- `src/cutscene/opening_cutscene.*`: FSM da abertura.
- `src/race/race_rules.*`: fase, pressao, integridade, Lumen e resultado.
- `src/race/race_track.*`: leitura de track data e spawn por eventos.
- `src/race/race_player.*`: faixas, salto, Pulse e estado do jogador.
- `src/race/race_collision.*`: AABB, layers, resposta a dano/coleta/Pulse.
- `src/race/race_hazards.*`: spawns, telegraphs e colisao.
- `src/race/race_road.*`: pseudo3D road stack e line scroll.
- `src/race/race_hud.*`: HUD fixo via WINDOW.
- `src/upgrade/upgrade_state.*`: escolha e aplicacao de upgrades.
- `src/boss/boss_setpiece.*`: approach e final boss.
- `src/flow/game_flow.*`: pause, game over, continue e retry.

## Owners Globais

- H-Int: nenhum owner no primeiro slice. Se line scroll exigir H-Int, owner unico sera `race_road`.
- WINDOW: owner unico de HUD/dialogo por cena; menu, creditos e cutscene fazem teardown antes da corrida.
- CRAM/paleta: owner de cena, com filas de transicao; sem write concorrente.
- DMA: somente preload de cena e commits VBlank.
- Audio: `system/audio` arbitra prioridade de SFX e stingers.
- Track data: `race_track` e unico dono de eventos de pista e spawn temporal.
- Colisao: `race_collision` resolve contato; nenhum modulo le cor de tile como solidez.
- HUD: `race_hud` usa `hud_layout_contract`; nenhuma cena escreve HUD durante gameplay sem owner.

## Politica de Transicao

Transicao usa mutex:

1. bloquear input;
2. fade/hold quando necessario;
3. parar update de sprites/audio temporario;
4. drenar/invalidation de DMA queue;
5. resetar scrolls, H-Int, WINDOW e paletas temporarias;
6. carregar recursos da proxima cena;
7. liberar input.

## Regras de Implementacao Futuras

- Tipos inteiros SGDK (`u8`, `u16`, `s16`, `fix16`) para gameplay.
- Tabelas LUT para curvas, sem `float`.
- Pools estaticos para hazards, particles e boss parts.
- `main.c` minimo.
- Nenhum callback global sem owner documentado.
