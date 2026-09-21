# 15 - Technical Design Document - TAIKETSU ULTRA REBIRTH

## 1. Contexto tecnico

- SGDK 2.11, C 68000, alvo NTSC 320x224 a 60fps.
- O contrato machine-readable e `doc/contracts/tdd_contract.json`.
- A rota Linux e `tools/sgdk_wrapper/build.sh`, que delega para a Wine bridge e usa SDK staged sem LTO.
- Proibicoes: sem float/double, malloc/free, API SGDK 1.60, DMA fora do VBlank ou pixels finais desenhados por codigo.

## 2. Arquitetura

Scene manager deterministico com `enter/update/exit/cleanup`. Modulos previstos: `src/system/input_director.c`, `src/system/fight_camera.c`, `src/system/vblank_director.c`, `src/system/fighter_runtime.c`, `src/system/combat_fx.c`, `src/cutscenes/dialogue_runtime.c` e `src/system/audio_director.c`. Estado global fica em buffers estaticos de contexto; pools tem tamanho declarado no contrato e nao crescem no loop.

## 3. Input e combate

Leitura central por frame de pad 3/6 botoes; held/pressed/released e repeat ficam em `input_director`. O frame data de cada lutador vive em `doc/characters/<id>/moveset_frame_data.json` e sera transcrito para tabelas C somente depois do contrato visual.

O sistema de especial mantem `meter[6]` em inteiro 0..100: dano, defesa e whiff adicionam carga; gasto leva a zero; conexao do especial reescreve para 100. A condicao CS-B e `life <= 25% && meter == 100` antes da resolucao do golpe.

## 4. Render e VDP

- BG_A/BG_B para stage e planos; WINDOW para HUD/retratos; sprites para lutadores e FX.
- Dois lutadores ativos residentes; roster inativo fica em janela de streaming. A residencia dos tiles e medida antes da arte.
- A simulação usa H40 e os dois limites simultaneos: 20 sprites e 320 pixels por scanline. A margem nao e encerrada por intuicao; o degrau seguinte e medido.
- SAT, paleta, tilemap, CRAM e dirty regions entram em filas; somente `app_vblank_callback` faz flush.
- H-Int e false no D1; camera cinematografica usa scroll de plano e cortes de janela, sem criar terceiro plano BG.

## 5. Camera

`doc/camera_behavior_contract.json` define dead zone, look-ahead, bounds, room lock, pan/zoom cinematografico e snap inteiro. O owner unico e `code/camera-system-sgdk`; os lutadores nao escrevem camera diretamente.

## 6. Audio

XGM2 e owner unico. Musica, SFX e voice cues passam pelo `audio_director` com prioridade hit/special > dialogue cue > UI. Banco final e validado na ROM e escutado pelo humano em P2; nenhuma alegacao de audio final nasce do build sozinho.

## 7. Persistencia

SRAM de 32KB guarda apenas unlock de Vanta Zero e versao/checksum CRC16. O boot-to-unlock sera uma evidencia separada no D5; SRAM nao e usada para mascarar falha de gameplay.

## 8. Scene contracts e QA

Cada cena formal esta em `doc/13-spec-cenas.md` e sera compilada para `doc/scene-contracts.json`. A ordem de prova e: contexto/metodologia -> GDD/TDD -> contrato de especializacao -> medicao VDP/tiles -> arte -> runtime -> build bridge -> validation_report -> BlastEm -> freshness -> scene closeout.

O gap de medicao atual e 17/18, porque `validate_native_sprite_production.py` nao tem self-check. O TDD permite continuar fundacao e prototipo, mas impede `ready_for_aaa`.

## 9. Handoff de especializacao

`tdd_annex_opt_in` aponta para `doc/fighting_2d_design_contract.json`; o TDD continua dono de FSM, pools, ownership, save, regiao, mastering e riscos. O validator fighting roda separado e seu report fica em `out/logs/fighting_specialization_report.json`.
