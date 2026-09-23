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

- Driver XGM2 é dono de FM **e** PSG (o arranjo decide o uso dos canais na composição — o código não reserva canais FM).
- SFX roteados pelos canais PCM do XGM2 (2-3 simultâneos, 13300 Hz), prioridade hit > telegraph > pickup > ui.
- PROIBIDO: escrita direta em PSG/FM pelo código do jogo com o driver carregado (correção do parecer curatorial 2026-07-03 — a divisão anterior "FM1-4 música / FM5-6 SFX" estava errada para XGM2).

### Streaming de tilemap (BG_A do cais)

- `scene_local_preload` foi vetado para o mapa de 1344px. Contrato fechado em `doc/contracts/tilemap_streaming_contract.json`: janela 64x32 circular, margem de 12 colunas, custo de 64 bytes/coluna de tilemap, máx 2 colunas/frame na fila DMA do VBlank, costura sempre fora da viewport, fallbacks ordenados (1024px → 2 sub-cenas → densidade). Veredito VDP atual: `nao_medido_contrato_fechado`; alvo `cabe_com_recuo` após medições.

### Save

- Nenhum save de jogo; SRAM usada apenas para heartbeat de evidencia MDRT (runtime probe)

## 4. Tecnicas (registry)

Selecionadas: `line_scrolling` (parallax mar/ceu), `camera_scroll_management` (wave-lock), `hitstop_camera_shake_feedback` (assinatura). Adiadas: `palette_cycling`, `shadow_highlight_mode` (status LABORATORIO). Detalhe completo com owners, budget e fallback em `technique_selection` do contrato e `doc/technique_usage_manifest.json`.

## 5. ROM Mastering

- Alvo 512KB com sizebnd (checksum + size align); header autoral; SRAM 32KB declarada para o probe

## 6. Riscos e dívidas técnicas declaradas

Ver `risk_mitigation_table` no contrato: pressão de sprites por scanline (high), consistência de arte IA (high), toolchain Linux/Wine (medium), pico de DMA no spawn (medium), **violação de ownership no branding herdado (high)** e **costura do streaming (medium)**.

Dívida de código herdada do template (bloqueia abertura do runtime do slice, não o planejamento):
- [scene_branding.c:253](src/scenes/scene_branding.c) usa `VDP_setHorizontalScrollLine(..., CPU)` e escreve CRAM dentro do update — contradiz o ownership de VBlank deste TDD.
- O mesmo código toca PSG diretamente com XGM2 carregado — contradiz o ownership de áudio.
- Correção obrigatória (fila VBlank + remover acesso direto a PSG) antes de qualquer claim visual/sonoro do branding ou abertura do runtime do CAIS_01.

## 6b. Escopo do slice vs contrato de jogo

O contrato de gênero descreve o JOGO (eixos congelados: 8 inimigos, grab, super bar, 3 stages com boss). O slice usa o subconjunto declarado em `doc/contracts/slice_scope_contract.json` (1 jogador, cap 4 inimigos, herói sem grab, sem super bar, sem boss). Validador verde no contrato de jogo NÃO significa slice implementado — guarda anti-falso-verde registrada no próprio contrato.

## 7. Contratos irmãos

- `doc/contracts/brawler_belt_scroll_design_contract.json` — design da especializacao (validador: passed=11, failed=0)
- `doc/contracts/mechanic_contract.json` — mecanica core `combo_de_mare`
- `doc/contracts/level_blueprint.json` — blueprint do `cais_01`
- `doc/contracts/enemy_roster.json` — roster do slice (CRIA, ESTIVADOR)
- `doc/contracts/frame_data/*.json` — frame data por archetype
- `doc/contracts/slice_scope_contract.json` — subconjunto do slice (guarda anti-falso-verde)
- `doc/contracts/tilemap_streaming_contract.json` — streaming do cais 1344px (janela, custos, seam policy)
- `doc/contracts/art_gameplay_direction_gate.json` — gate do primeiro pacote visual (produção autorizada só para concepts)
