# 13 - Especificacao de cenas - TAIKETSU ULTRA REBIRTH

Regra global: roteiro -> storyboard -> coreografia -> medicao -> budget -> contrato de asset -> model sheet -> assets -> runtime -> evidencia. Nenhuma arte final abre antes de `vdp_scanline_simulator.py` e `audit_tile_residency.py`.

### Cena 0 - front_end_main_menu

- `scene_id`: front_end_main_menu
- papel: title, select e acesso a versus/arcade/training
- tecnica: `camera_scroll_management` apenas no micro-pan do title; UI em WINDOW
- owner: scene-state-architect + input-system-sgdk
- budget: dois planos, fonte e cursor; sem lutadores residentes
- fallback: title estatico de debug, nunca claim visual final
- evidencia: boot BlastEm e screenshot hash-bound

### Cena 1 - stage_intro_cinder_circuit

- `scene_id`: stage_intro_cinder_circuit
- papel: cutscene CS-C do primeiro stage, apresenta a arena e prepara a entrada dos dois lutadores
- tecnica: transicao de paleta e scroll de plano; sem H-Int no D1
- owner: cutscene-cinematic-direction
- budget: stage tiles + dois portraits curtos; sprites de luta entram somente na saida sincronizada, apos a camera fechar
- fallback: pan inteiro sem zoom
- transicao: `stage_intro_cinder_circuit` libera scroll/portraits, revela Jack e Kairo juntos na saida e entrega ownership para `dialogue_cinematic_d1` / `character_intro_d1`
- evidencia: captura BlastEm + live scene bar quando virar signature scene

### Cena 2 - dialogue_cinematic_d1

- `scene_id`: dialogue_cinematic_d1
- papel: cutscene CS-E completa do par ordenado `jack -> kairo_vant`
- tres eixos simultaneos: retrato com boca/olhos/respiracao; dois corpos com apontar/cruzar bracos/recuar; camera com pan/zoom por scroll/corte de falante
- medicao: dois lutadores grandes + retratos + FX de troca de linha no simulador; tiles de retrato e lutadores auditados como janelas
- budget: apenas os dois ativos; troca de retrato fora do plano jogavel; no more than 20 sprites e 320 pixels por scanline em H40
- fallback: sem zoom, mas mantendo movimento de retrato, corpo e corte
- evidencia: screenshot mid-frame, GIF/animacao, SRAM/VDP dump quando exigidos, ROM hash e laudo live_scene_bar

### Cena 3 - combat_cinder_circuit

- `scene_id`: combat_cinder_circuit
- papel: gameplay vertical slice D1
- lutadores: Jack + Kairo Vant; somente estes dois residentes
- mecanicas: neutral, walk, jump, normals, guard, hit reaction, hitstop, special meter conforme tabela D1 do GDD, special connect refill 2 frames apos impacto, round end
- medicao antes da arte: H40/H32 scanline simulator com ambos + especial; tile residency por janela
- tecnica: `camera_scroll_management`, `hitstop_camera_shake_feedback`, `tile_cache_streaming_refcount`
- owner: sgdk-runtime-coder + camera-system-sgdk + megadrive-vdp-budget-analyst
- fallback: camera fixa, hitstop sem shake, FX reduzido sem flicker
- evidencia: build wrapper, validation report, BlastEm a 60fps, audio smoke, screenshot e laudo live_scene_bar

## Cenas futuras por degrau

- D2: roster_select_full, combat_roster_streaming
- D3: special_cs_a_all, clutch_cs_b_all, stage_intro_all, character_intro_all
- D4: dialogue_ordered_pairs_30
- D5: vanta_zero_unlock_and_boss
- D6: audio_final_mix_and_closeout

## Contratos de transicao

Toda transicao libera sprites, filas DMA, callbacks, CRAM e audio do owner anterior antes de transferir ownership. `scene_id`, `raw_input`, `observed_input` e hash de ROM devem aparecer na navegacao roteirizada do BlastEm.

Para D1, a cadeia fechada e `stage_intro_cinder_circuit` (CS-C stage-only) -> revelacao sincronizada -> `character_intro_d1` (CS-D) -> `dialogue_cinematic_d1` (CS-E) -> `combat_cinder_circuit`. O primeiro especial conectado abre CS-A, aplica refill para 100 dois frames apos o impacto e retorna ao combate; a transicao deve preservar o hash da ROM e o estado da barra.
