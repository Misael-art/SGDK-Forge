# 15 - Technical Design Document - MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

O TDD descreve como o jogo sera construido. Ele nao substitui o GDD; traduz as escolhas de design em arquitetura, memoria, VDP, audio, input e validacao.

> **Contrato canonico machine-readable:** `doc/contracts/tdd_contract.json` (tdd_id `mare_brava_tdd_v1`).
> Este documento e o resumo narrativo; em conflito, o contrato validado vence.
> Auditado em 2026-07-03 por `audit_game_design_contracts.ps1`: status=passed, blockers=0.

## 1. Contexto Tecnico

- Contexto do projeto: `aaa_game` (ver `doc/project_context_manifest.json`)
- Teto de entrega tecnica: vertical_slice
- Hardware alvo: Mega Drive
- SDK: SGDK 2.11
- Regiao alvo: NTSC-first (60fps); PAL por flag de timing, validacao futura

## 2. Arquitetura

- Modelo de cenas: FSM linear deterministico com enter/update/exit/cleanup — app_root: BOOT → BRANDING → TITLE → GAMEPLAY_CAIS01 → DEMO_CLEAR/GAME_OVER → TITLE; cais_01: ENTER_PRELOAD → WAVE_INTRO → COMBATE → WAVE_CLEAR/PLAYER_DOWN → RESULTADO
- Estrutura de modulos: `src/core` (app/FSM), `src/scenes`, `src/system` (input, audio, camera, wave_manager, fx), `res/` declarativo
- Estado global permitido: contexto de app (cena atual), estado da heroina, pools estaticos
- Buffers estaticos: enemy_pool[4], fx_pool[4], hud_widgets[3], string buffer unico de HUD (ver `memory_pool_map` no contrato)
- Proibicoes: sem `float` (fix16/fix32), sem `malloc/free`, sem API SGDK inventada (verificar `sdk/sgdk-2.11/inc/`), sem DMA fora do VBlank

## 3. Sistemas

### Input

- Camada unica de leitura por frame sobre JOY (3 e 6 botoes); latencia alvo 1 frame (~17ms)
- Prioridade de decisao: A+B (especial) > A aereo (joelhada) > A solo (combo)
- Sem rebind no slice

### Camera

- Owner: `code/camera-system-sgdk`; mundo em fix32, tela em s16 com snap inteiro no render
- Deadzone 16px, wave-lock por onda, clamp nos limites; shake apenas por evento de impacto

### VBlank / DMA

- Callback unico de VBlank e o dono de todo DMA: SPR_update, tabela HScroll do BG_B, fila CRAM
- max_pending_dma=3; tudo enfileirado no update e flushado no VBlank

### Audio

- Driver XGM2; FM1-4 musica, FM5-6 SFX prioritario, PSG reforco tonal/UI; PCM 13300 Hz

### Save

- Nenhum save de jogo; SRAM usada apenas para heartbeat de evidencia MDRT (runtime probe)

## 4. Tecnicas (registry)

Selecionadas: `line_scrolling` (parallax mar/ceu), `camera_scroll_management` (wave-lock), `hitstop_camera_shake_feedback` (assinatura). Adiadas: `palette_cycling`, `shadow_highlight_mode` (status LABORATORIO). Detalhe completo com owners, budget e fallback em `technique_selection` do contrato e `doc/technique_usage_manifest.json`.

## 5. ROM Mastering

- Alvo 512KB com sizebnd (checksum + size align); header autoral; SRAM 32KB declarada para o probe

## 6. Riscos

Ver `risk_mitigation_table` no contrato: pressao de sprites por scanline (high), consistencia de arte IA (high), toolchain Linux/Wine (medium), pico de DMA no spawn (medium).

## 7. Contratos irmãos

- `doc/contracts/brawler_belt_scroll_design_contract.json` — design da especializacao (validador: passed=11, failed=0)
- `doc/contracts/mechanic_contract.json` — mecanica core `combo_de_mare`
- `doc/contracts/level_blueprint.json` — blueprint do `cais_01`
- `doc/contracts/enemy_roster.json` — roster do slice (CRIA, ESTIVADOR)
- `doc/contracts/frame_data/*.json` — frame data por archetype
