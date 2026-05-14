# 13 - Especificacao Tecnica por Cena - AXE DE ACO FIGHTER [VER.001] [SGDK 211] [GEN] [PROTOTIPO] [LUTA]

> Documento canonico para budgets por cena, contrato de evidencia e papel formal de cada surface.

## Scene Roadmap Vigente

### Cena 3 - fight_direct

- runtime_name na ROM: fight_direct
- app_scene_id: 3
- papel: gameplay
- objetivo: provar luta 1v1 autoral em ROM real com controles, IA simples, colisao, dano, HUD e FX separado.
- status atual: prototype_playable com visual_gate_blocked.
- boot atual: direto na luta, sem menu textual de debug.

## Resource Budget Model - Cena 3

- runtime_loading_model: scene_local_preload.
- rom_asset_cost: 30 assets visuais versionados em res/resources.res.
- vram_resident_set: BG_B, BG_A, sprite reserve via SPR_initEx(420), font/HUD e recursos de sprite declarados.
- sprite_reserve_tiles: 420.
- tile_max_before_maps: 1536.
- system_tiles: 16.
- user_tiles: 1004.
- font_tiles: 96.
- headroom_tiles_before_maps: 0.
- vram_overlap_count: 0.
- active_animation_window: P1 + P2 + spark + dust, com runtime peak 4 sprites no probe.
- scanline_sprite_pressure: max_scanline_sprites=18 no runtime capture.
- fallback_plan: reduzir tiles unicos de BG/sprites antes de aumentar a residencia ou mexer no mapa de planos.

## Contrato de Evidencia - Cena 3

- scene_contract_compile_report.json: ok.
- res_graph_report.json: ok, VRAM ok.
- vram_residency_report.json: ok.
- validation_report.json: errors=0, warnings=2, blockers=visual_gate_blocked, local_rasterization_used_as_final, source_to_rom_mismatch.
- runtime_metrics.json: real BlastEm MDRT, capture_status=partial, scene_id=3, frames_seen=151, samples=32.
- emulator_session.json: boot=ok, fresh_sram_confirmed=True, screenshot_method=window_capture.
- visual_delivery_gate_report.json: visual_gate_blocked, ready_for_aaa=False.
- scene_closeout_gate_report.json: blocked.

## Riscos Ativos

- VRAM esta no limite do modelo de 1536 tiles antes de mapas; qualquer asset novo precisa corte compensatorio.
- O gate visual bloqueia AAA ate existirem strips premium por acao com continuidade, pivo e escala validados.
- Audio ainda precisa validacao formal.
- Qualquer mudanca em C, res ou assets invalida a prova atual ate rebuild + BlastEm + validacao.
