# Changelog Canonico - __PROJECT_NAME__

## 2026-08-18 - the_forge_learning_register

- Task: registrar o aprendizado da abertura para o proximo agente
- Caderno: `doc/agent_learning/the_forge_opening_lessons.md`
- Tabelas: success/failure/candidates/promotion_review atualizadas
- Capture local; canonical_promotion_performed=false
- Sem nova ROM

## 2026-08-18 - the_forge_starfield_v02

- Task: substituir o ceu vazio do Ato I sem vender arte final
- Canal: native image_gen (conceito B). Traducao VDP em
  `translate_starfield_v02.py` (campo navy, pulso PAL0[1]/[2], hem 24px)
- Tiles: unique 125→26. 4-bit PLTE 16. source_kind composed_from_authored
- ROM: 661e408694457859da97af6e3afa729be152bcff46b9984efd5eab3f777801a5
- BlastEm: d5_sky observado (selo recusa void); d5_lock/hit1/forge selados
  ob=0 cpu 45/83/83. Sem regressao da forja
- Nao promovido: ready_for_aaa, arte final, aprovacao humana

## 2026-08-18 - the_forge_nametable_baked_dma

- Task: baixar o pico residual 92 sem reabrir o enxame
- Runtime: assar TILE_ATTR no buffer do preludio; reveal em 4 metades
  via VDP_setTileMapDataRect+DMA_QUEUE; prefetch martelo 1/2 em F12-F13
- ROM: ceaa7028bf8fc3a350d4cacc901003f955de55a464f0fea3666a6079b0887fdf
- BlastEm: d4_reveal/d4_lock/d4_hit1/d4_forge selados blockers=[]
- Budget: cpu 92→83, ob=0, spr 13. Nao validado_budget
- Nao promovido: ready_for_aaa, arte final do ceu

## 2026-08-18 - the_forge_wall_unpack_off_display

- Task: achar o cpu 160 / over_budget 9 dos golpes
- Causa medida: unpack APLIB de `img_forge_bg_b`/`img_forge_bg_a_props`
  (40x28, 2240 B) em F154-F155 no display. HIT2 nao somava over_budget
- Cura: unpackTileMap em buffers estaticos no preludio F8-F10; reveal
  escreve o mapa ja aberto; prefetch do quadro 4 do martelo no lock
- ROM: e6437530f7951d404417f278c77fb93135822159a95e6f31075d5bc43756b7e5
- BlastEm: d3_reveal/d3_lock/d3_hit1/d3_forge selados blockers=[]
- Budget: ob 9→0; cpu 160→92; spr 13. Nao validado_budget
- Nao promovido: ready_for_aaa, arte final do ceu, sample de estudio

## 2026-08-18 - the_forge_descent_recapture

- Task: recapturar a ROM de descida/climax no BlastEm e fechar o claim
- Runtime ja no disco: ceu sai por VSCROLL t^2; parede/bigorna em 2
  quadros apos F154; paleta da forja so depois do tilemap; sem enxame
  de 56 estilhacos no 2o golpe (12 fagulhas sao o fio)
- ROM: e79a9de43b994cd799b4e7b60016672effe6f9cb1cb653778fc52c5761624b82
- BlastEm: d2_sky/d2_sky2/d2_drop observados (selo recusa ceu preto);
  d2_reveal/d2_lock/d2_hit1/d2_forge selados blockers=[]
- Budget medido: emerge/lock ob=0 cpu 45 spr 13; golpes ob=9 cpu 160
  spr 13 (antes 20/182/51). Nao validado_budget
- Gates: tile_residency OK, provenance OK, brand_comprehension exit 0
- Nao promovido: ready_for_aaa, descida continua, arte final do ceu,
  sample de estudio

## 2026-08-18 - the_forge_four_acts

- Task: traduzir o memorando The Forge em sequencia jogavel
- Ritmo: contemplacao (ceu+input) -> queda -> lock na bigorna -> 1o slam
  (materia) -> 2o slam (FORGE forjado). ~7 s. START skip. A nao salta.
- Asset: `img_starfield_v2` (IA, placeholder). Fagulhas sao o fio condutor.
- ROM: 5c625fe565a6b977dce07853445face0e2bfcf693782f214bcffc8aac4cf23ae
- BlastEm: sky/drop/hit1/forge. Climax com over_budget 20.
- Nao promovido: ready_for_aaa, descida continua, arte final do ceu

## 2026-08-18 - menu_slam_forge_bed

- Task: corrigir menu distorcido e dar peso sonoro ao martelo
- Menu: forja + FORGE + barra + PAL3 ouro; fonte recarregada; handoff da
  marca vai para MENU, nao para o boot de debug
- Wordmarks MISAEL/MASTER: outline 1px + corpo ouro
- Slam: WAV 13.3 kHz sintetizado + PSG noise/thump no F120; shake 10
- BGM: VGM FM original `mus_forge_brand` (lab, retrigger se o loop falhar)
- ROM: f26ffc9a7eab50813ee35ce53601f042353c1bcb457adb0a28a915de2b832430
- BlastEm: wm4 F331, ms6 F451, front12 F691 scene=2
- Nao promovido: sample de estudio, trilha de compositor, ready_for_aaa

## 2026-08-18 - modelo_brand_locked_forge

- Task: subir a apresentacao da marca do template (engine brand, nao jogo AAA)
- Runtime: forja travada; FORGE sai por restore unico de props; MISAEL/MASTER
  na parede (y<64); PRESENTS no fogo em BG_A; sem VSCROLL_COLUMN, sem wipe
  da bigorna, sem WINDOW no closer, sem haze de linha no ato 3
- Hold da assinatura ate F600. Sem PAL_fadeOutAll. Sem mudar a matriz de
  estilhacos
- ROM: 40fec78b44c36200b2329d26bae7129062b2bba2b9240722700fb3c322ed73f9
- BlastEm: fin2 F271, fin4 F331, fin6 F451, fin72 F511; sealed blockers=[]
  over_budget=0 cpu 70/70/97/97
- Gates: tile_residency, brand_comprehension, provenance = exit 0
- Nao promovido: ready_for_aaa, arte final, aprovacao humana

## 2026-08-17 - act3_presents_contrast_shard_counter

- Task: fechar presents F480, contraste do MASTER e contador de estilhacos
- F480 mediu: WINDOW no topo (FALSE,22) comia a cena; PRESENTS em y=23
  estava fora da regiao. Flip para TRUE,22.
- MASTER: prioridade alta para nao levar shadow do S/H do ato 1
- Probe: `MDRuntimeProbe_noteSpriteAlloc` → probe[18]=spawned [19]=failed.
  Medido 56/0. O pico scanline 6 nao e pool esgotado.
- ROM: a5aec70049fcc9f96f8bd28feffea02f14772da7fe656d2498d03511d4771413
- BlastEm: act2_v2 F271, act3_author_v2 F331, act3_master F451,
  act3_pres_fix F480; sealed blockers=[] over_budget=0
- Gates: tile_residency, brand_comprehension, provenance = exit 0

## 2026-08-17 - act3_bisect_vram_reuse

- Task: bissectar o ato 3 da abertura v2 antes de corrigir
- Metodo: 6 desligamentos, um por build, warmup 6s → F451
- Achado: `sVramAuthor = sVramBgA` (ponto 6) apaga a bigorna. Ponto 2
  (wordmark projeto) só cobre o MISAEL e piora a corrupção. Cortina,
  SPR_reset, presents e fade não mudam os 3 sintomas em F451. Magenta
  das bordas não foi reproduzido em F451 (letterbox preta em todos).
- Correcao: wordmarks carregam depois da janela do martelo. Sem
  reuso de tiles sob o tilemap vivo de BG_A.
- ROM: 1d43242533bd853d185660e29b7eabb6f1924f7c7d579eb5ae457908665819c1
- BlastEm: F271 ato 2 `out/evidence/act2_noregress/`; F331 autor
  `out/evidence/act3_author/`; F451 `out/evidence/act3_fix/` selado
  blockers=[] over_budget=0 cpu=96
- Gates: tile_residency, brand_comprehension, provenance = exit 0
- Nao mexeu: SHARD_COUNT 56, SHARD_ROWS 7, SHARD_ROW_STAGGER 6, sector

## 2026-08-17 - branding_v2_forge_clean_lock

- Task: limpar FORGE, haze seguro, recaptura no lock
- ROM: 67fa8154b198e89705a06b1050a239ffc0fc4c4de74c2485538b27eef3e0c9c7
- BlastEm selado: out/evidence/v9_forge/blastem-linux-20260817T173744Z-2784610
- FORGE no plano via tileset no enter + VDP_setTileMapEx; sem unpack APLIB no display; haze so 48 linhas em HSCROLL_LINE; estilhaços lazy
- Screenshot do selo mostra FORGE limpo sobre a bigorna. over_budget_frames ainda 12 (cpu 116). Nao validado_budget / nao AAA.

## 2026-08-17 - branding_v2_aaa_pending_close

- Task: logo legivel, martelo no contacto, bundle BlastEm com VLAB
- ROM: da5843354459c42329f5f6f4d6bfe9d49ba4d0fc630edcd8c81c6cbebc4f1d82
- BlastEm: bundle selado em out/evidence/v7_aaa/blastem-linux-20260817T172506Z-2759956 (screenshot, save.sram, visual_vdp_dump.bin, runtime_metrics)
- VLAB: scene 0, 60.2 fps, scanline peak 11, over_budget_frames=12, cpu_max=113
- Runtime: VDP_drawImageEx do FORGE (tilemap real, prio 1); martelo sobe e bate com smear; 32 estilhacos; probe exporta VLAB@0x200
- Nao promovido: validado_budget (over_budget>0), ready_for_aaa (logo ainda tem ghost/sujeira a esquerda)

## 2026-08-17 - branding_v2_hint_why_and_bg_b_budget

- Task: close H-Int WHY and re-author img_forge_bg_b toward 644 unique tiles
- Skills: sgdk-runtime-coder, megadrive-vdp-budget-analyst, shadow-highlight-scroll-fx, art-translation-to-vdp
- Runtime: HINTERRUPT_CALLBACK + delayed acquire + V-Int mask + VBlank rearm; full ember/shard frame residency; act 3 VRAM derived
- Art: forge_bg_b_v02.jpg composed to unique_with_flip=642 (ResComp 642, dedup 43%)
- ROM: tools/sgdk_wrapper/modelo/out/rom.bin sha256 b85c67b91acbab563913c2e9faf8500fdb0074b536702c2cdc81d2b4b83cf467
- Tile residency: peak act2 1216/1740 (70%), margem 30% (era 1667/96%)
- BlastEm: rodou a abertura sem crash; burst em out/evidence/v5_hint_bgb/; bundle rejeitado (vdp_dump + runtime_metrics)
- Status: implementado + buildado; observed_in_blastem; not testado_em_emulador
- Claims not made: ready_for_aaa, validado_budget, testado_em_emulador

## Estado Inicial

- projeto bootstrapado a partir do wrapper central
- documentacao minima materializada
- scene regression declarada em `doc/scene-regression.json`
- companion inicial esperado em `doc/scene-contracts.json`
## 2026-06-03T10:55:11.3513283-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots:
  - img_brand_fx_tiles -> v001 (res/branding/brand_fx_tiles.png)
  - img_brand_engine_logo -> v001 (res/branding/brand_engine_logo.png)
  - img_brand_author_logo -> v001 (res/branding/brand_author_logo.png)
  - img_brand_project_logo -> v001 (res/branding/brand_project_logo.png)
  - img_brand_presents_text -> v001 (res/branding/brand_presents_text.png)
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=10
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, changelog_missing, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: report_older_than_rom

## 2026-06-03T10:55:35.2022830-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=7
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao

## 2026-06-03T10:56:07.3006878-03:00 - branding_sequence_xgm2_probe

- Task: branding_sequence_xgm2_probe
- Skills: sgdk-build-wrapper-operator, sgdk-runtime-coder, scene-state-architect, megadrive-vdp-budget-analyst, xgm2-audio-director
- Asset snapshots: nenhum hash novo
- ROM: build_v001 (sha256 5c1baf95c2d4646f5bd01f74eac9b6a1b1fce604ce8f99fd523e325147977dab, 262144 bytes)
- Validation: errors=0, warnings=7
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: sem_sessao
- Notes: Fase 0 branding: preserved existing brand_* PNG baseline, added WAV XGM2 cue declarations/assets, integrated runtime_probe boot/tick, generated explicit blocked visual_delivery_gate_report.

## 2026-06-03T11:09:40.7744181-03:00 - build_snapshot

- Task: build_snapshot
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=9
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: rom_identity_mismatch

## 2026-06-03T11:10:00.1427886-03:00 - post_validate_refresh

- Task: post_validate_refresh
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, emulator_evidence_stale, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale

## 2026-06-03T11:11:36.1661598-03:00 - branding_sequence_xgm2_probe_capture

- Task: branding_sequence_xgm2_probe_capture
- Skills: sgdk-build-wrapper-operator, sgdk-runtime-coder, scene-state-architect, megadrive-vdp-budget-analyst, xgm2-audio-director
- Asset snapshots: nenhum hash novo
- ROM: build_v002 (sha256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, 262144 bytes)
- Validation: errors=0, warnings=8
- Blockers: gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_direction_failed, emulator_evidence_stale, freshness_audit_missing, scene_closeout_gate_missing
- Emulator evidence: runtime_metrics_stale
- Notes: Fase 0/branding: preserved brand_* PNG baseline, added XGM2 WAV cues, integrated MDRuntimeProbe boot/tick, reduced inactive line-scroll uploads, rebuilt ROM SHA256 22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f, captured TargetScene 0 in BlastEm with screenshot/save.sram/runtime_metrics partial; one CPU budget spike remains at frame_index 128 so performance gate stays blocked.
