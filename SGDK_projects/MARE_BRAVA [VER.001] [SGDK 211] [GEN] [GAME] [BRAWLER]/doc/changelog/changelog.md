# Changelog Canonico - MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

## 2026-08-30 — correcao do gap de gate humano (lineart nativa TAÍNA)

- O agente estacionou em `human_decision_required` para a lineart nativa 48x64
  (pergunta "quem fornece a lineart?"), mas os reportes de tentativa e o
  `generation_channel_decision` provam falha de **representacao**, nao de
  decisao humana: o canal `codex_builtin_image_generation` devolveu
  `1086x1448 RGB/RGBA` (nao grade nativa indexada 48x64), rejeitado como fake
  pixel art. A direcao ja esta aprovada (`human_approval_record`), portanto a
  producao da lineart nao e porta de gate humano.
- Corrigido `active_iteration.json`: `human_gate_pending` removido, classificado
  como `representation_mismatch`, `next_causal_action` redefinido para
  author/stamp em grade 8x8 a partir do model sheet aprovado.
- Removida a ficcao `human_pixel_model_sheet_reapproval` de
  `game_production_gate_report.json` (doc/ + out/logs) e de
  `visual_delivery_gate_report.json` (out/logs); blocker renomeado para
  `taina_native_48x64_lineart_representation_mismatch`.
- Framework: `causal_persistence_guard.py` ganhou a regra 1b — falha de
  representacao/capacidade nunca e decisao humana (devolve
  `retry_changed_representation`) — coberta pela fixture F7; prompt MODO GO
  registra o desempate de gate. Nenhuma mudanca em `res/`, build ou ROM;
  `ready_for_aaa=false` permanece.

## 2026-08-30 — captura BlastEm atual e budget medido

- BlastEm Linux 0.6.2 foi executado pela rota Flatpak e selou a sessão
  `blastem-linux-20260830T180348Z-3682089` para a ROM
  `144fb573b088375c68f71d4255282db315052fe0f8de351e595806e6b734abd4`.
  Manifesto de evidência passou (`status=ok`, blockers=0), com screenshot,
  SRAM, VDP dump e métricas vinculados à mesma hash.
- A captura mostra CAIS_01 com TAÍNA/CRIA e semântica de screenshot passou;
  o limite do claim permanece boot/cena observada porque input, áudio de
  gameplay e estabilidade ainda não foram isolados.
- Medição VLAB: `window_fps_snapshot=59.7`, `max_cpu_load=172`,
  `over_budget_frames=61/32`, 7 sprites ativos e máximo de 4 sprites por
  scanline. Performance não está verde.
- Relatório de residência persistido: `2117/1740` tiles, `122%`, blocker
  `tile_residency_over_ceiling`. Planner DMA self-check passou, mas o pior
  caso de runtime ainda requer medição.
- Revisão formal do código terminou em `review_passed_with_risk`; sem API
  inventada, `float/double`, heap no loop ou PSG direto fora de `audio.c`.
- Sync final: `validate_resources.ps1` terminou com `errors=0`, `warnings=10`;
  o auditor do manifesto em `out/evidence/blastem` passou com blockers=0.
  O closeout teve 11/13 passos sucedidos, 1 pulado e 1 bloqueado.
  `game_production_ready=false` permanece por blockers de produto medidos.

## 2026-08-30 — S0–S6 e fechamento de ownership de câmera/branding

- Emitidos os artefatos de radar criativo, mecânicas, level design, enemy
  design, áudio adaptativo, transições e gate agregado de produção. O produto
  segue `ready_for_aaa=false` por falta de arte nativa 48×64, BGM/SFX de
  gameplay, budget de residência e evidência BlastEm atual.
- Implementado `src/system/camera.c` com fix32 interno, deadzone, lookahead,
  clamp da janela CAIS_01 (`0..192` px), smoothing por passo de 4 px e snap
  inteiro. `scene_demo.c` passou a consumir o owner único da câmera.
- Corrigida a dívida de ownership do branding: PSG agora passa por
  `AUDIO_pulsePsg()`, enquanto mudanças de CRAM e HScroll por linha entram na
  fila DMA (`DMA_QUEUE`).
- Build limpo pela rota `linux_wine_bridge`: ROM 262144 bytes, SHA-256
  `144fb573b088375c68f71d4255282db315052fe0f8de351e595806e6b734abd4`.
- Validação de recursos concluída com `errors=0`, `warnings=12`.
- Status: `buildado`; ainda não `testado_em_emulador`, `validado_budget` ou
  `ready_for_aaa`.

## 2026-08-30 — P0.5/P0.6 do forge-art: lineage da TAÍNA e runtime_probe

**Migracao de lineage da TAÍNA (P0.5).** As tres ilustracoes 1086x1448
aprovadas pelo owner como referencia de construcao sairam de
`data/source_art/concept/taina_pixel_model_sheet/rejected/` para
`.../construction_reference/`. A pasta tinha nome que contradizia o contrato
`visual_source_of_truth_taina_v02.json`, e essa contradicao ja havia induzido
erro de leitura.

- conteudo inalterado: os tres SHA-256 declarados foram reconferidos contra os
  arquivos movidos e batem (`4de4b9be…`, `0981854f…`, `07c94fde…`);
- 5 contratos repontados: `premium_source_manifest.json`,
  `taina_derived_visual_sources_human_approval_v01.json`,
  `taina_reseed_native_lineart_candidate_review_v01.json`,
  `taina_reseed_native_lineart_gate_attempts_v01.json`,
  `visual_source_of_truth_taina_v02.json`;
- `rejected/` continua existindo com **apenas** a candidata que e de fato
  rejeitada e que nenhum contrato cita;
- o memory bank recebeu datacao explicita: a entrada de 2026-08-29 que dizia
  "ilustracoes rejeitadas" ficou marcada como SUPERADA, com o motivo.

**Proibicao preservada:** essas tres imagens continuam sem poder ser
quantizadas ou tracadas como asset final. Elas autorizam gerar
`technical_candidate` e servir de referencia de construcao — nada alem.

**`runtime_probe` reconciliado (P0.6).** `src/system/runtime_probe.c` e
`inc/system/runtime_probe.h` estavam na versao **pre-correcao**: sem varredura
completa de scanline (`s_linePressure`), sem quadro do pico
(`probe_note_peak_frame`) e sem re-export periodico (`s_lastExportSamples`) —
exatamente os defeitos que `SGDK_GLOBAL.md` secao 34 registra. Sincronizados
com a canonica `tools/sgdk_wrapper/modelo/` (0 linhas de divergencia).

- API compativel verificada antes da copia: a canonica e superconjunto e os
  campos `gApp.currentScene`/`gApp.totalFrames` existem no projeto;
- build limpo pela rota canonica `linux_wine_bridge`:
  ROM 262144 bytes, SHA-256
  `e07fa63b6aa6e7bec542814950eb9190f7a5e04732da362c27f01b84398dfd5e`.

**Teto de claim:** `buildado`. A ROM **nao** foi observada no BlastEm.
Toda telemetria anterior de performance deste projeto fica **invalidada**: ela
veio do instrumento defeituoso. `ready_for_aaa=false` permanece.


## 2026-08-29 — aprovação humana da fonte autoral da TAÍNA

- O owner aprovou a prancha high-res
  `data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png`
  (SHA-256 `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`)
  como fonte autoral para tradução pixel nativa.
- A decisão foi registrada em `doc/human_approval_record.md`, na revisão da
  fonte e em `data/source_art/premium_source_manifest.json`. O asset continua
  high-res; não entrou em `res/` e não aprova sprite, budget ou arte final.
- Preservado o report AAA de 2026-07-29 em `doc/history/`. O novo
  `doc/aaa_pipeline_gate_report.json` limita o estado atual a
  `runtime_candidate` e declara os blockers de produção visual, budget, áudio,
  live-scene e closeout.

## 2026-08-29 — seed técnico de combate CAIS_01 (invulnerabilidade pendente)

- TAÍNA passa a resolver um jab por frame ativo: 15 de dano, recuo direcional
  de 8 px e 2 VBlanks de hitstop somente quando `CRIA_receiveHit` aceita a
  colisão. A CRIA tem 40 HP, hurt/recuo, 8 VBlanks de invulnerabilidade e sai
  de cena ao zerar HP.
- O haymaker da CRIA agora reduz 5 HP da TAÍNA e respeita 24 VBlanks de
  invulnerabilidade do jogador. A leitura técnica `T:HP C:HP` não é HUD final.
- Criado `doc/contracts/cais01_combat_seed_collision_topology_v01.json` para
  separar ranges de hit/hurt de sólidos e push, fixar a ordem de atualização e
  declarar o que ainda não existe (combos, multi-inimigo, terreno e arte final).
- Estado: `jab_damage_testado_em_emulador_invulnerability_pending`; nenhuma
  promoção de qualidade visual, budget, vertical slice ou AAA.

## 2026-08-29 — VLAB e evidência selada do seed de combate

- A instrumentação de runtime passou a exportar um bloco VLAB com configuração
  VDP, CRAM e contadores acumulados, além do MDRT. A medição de sprites por
  scanline cobre as 224 linhas, substituindo a antiga amostra de quatro linhas.
- Build limpo pela bridge SGDK e pacote BlastEm selado para a ROM
  `e07fa63b6aa6e7bec542814950eb9190f7a5e04732da362c27f01b84398dfd5e`:
  `out/evidence/cais01_combat_seed/blastem-linux-20260829T220742Z-874842/`.
  O pacote contém screenshot, SRAM, dump VDP e `runtime_metrics.json`, todos
  com hash do mesmo binário. Snapshot: cena 3, 320×224, janela 60.2 fps,
  `max_cpu_load=95`, quatro sprites/scanline e sete ativos.
- O diagnóstico de input encontrou o binding real `a -> gamepads.1.a` e o
  requisito de captura de teclado por `Control_R`. A sessão selada
  `blastem-linux-20260829T230057Z-984247` enviou um único `a` e observou
  `C:040 -> C:025`, validando os 15 HP de dano do jab e o recuo da CRIA.
  A invulnerabilidade da TAÍNA ainda não foi isolada num teste de dois hits.
- Estado corrigido: `jab_damage_testado_em_emulador_invulnerability_pending`.
  Sem promoção
  para combate validado, performance sustentada, budget, vertical slice ou AAA.

## 2026-08-29 — nova prancha-fonte para o reseed da TAÍNA

- Gerada e persistida a candidata
  `data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png`
  (SHA-256 `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`).
- A prancha preserva cabelo, guarda, faixa assimétrica, bandagens e materiais,
  mas é uma fonte conceitual high-res, não pixel art nem strip. Esta entrada é
  histórica: a aprovação humana posterior autoriza agora o model sheet pixel
  48x64/3.5 heads, sem promoção direta para `res/`.

## 2026-08-29 — proveniência da arte técnica declarada

- Criado `doc/asset_provenance_manifest.json` com os 20 símbolos visuais
  ativos de `res/resources.res`. Todos foram declarados honestamente como
  `procedural_primitive` e `placeholder`; nenhum recebeu aprovação final.
- `audit_procedural_asset_provenance.py` passou com `blocking=[]`. Isso remove
  somente `asset_provenance_manifest_absent`, `asset_provenance_undeclared` e
  a promoção implícita de arte procedural; o reseed autoral e os demais gates
  visuais, de budget e de evidência continuam pendentes.

## 2026-08-29 — baseline visual humano e bloqueio de qualidade relativa

- Preservadas quatro referencias humanas em `rascunho/entrada_bruta/quality_reference/`,
  registradas com hash em `doc/project_hygiene_manifest.json` e classificadas
  somente como `quality_reference_only`.
- Criado `doc/art/quality_reference_board.md`. Ele exige que personagens
  preservem anatomia, materiais, marcadores e acting; que o CAIS venha de kit
  modular; e que FX tenham fases por clusters e consequencia de jogo/mundo.
- O runtime visual existente foi reclassificado como `technical_style_probe`:
  nao pode servir de baseline, source ou evidencia de qualidade final. A proxima
  acao e reseed visual, nao expansao de conteudo.

## 2026-08-29 — CRIA IA perseguidor (build_v009)

- FSM APPROACH->TELEGRAPH->ATTACK->RECOVER. Spawn x=288, aggro 200,
  strike 40, 1.5 px/vbl, sem H-flip. Hit conecta com recuo 8 px e SFX;
  HP ainda nao esta ligado.
- ROM
  `6bf9e359ae6ed13f926db7e4ab631943bc001291c67e2aa6249358b5ca968686`
  BlastEm `blastem-linux-20260829T172244Z-2390350`. Burst 1 = approach;
  burst 20 = telegraph; still = golpe na Taina.
- Continua `visual_pass=false`, `ready_for_aaa=false`.

## 2026-08-29 — CRIA recover nativo apos haymaker (build_v008)

- Follow/retract/settle/hold 4-5-6-8. Punho armado recua da esquerda para
  o peito. Video recusado (recoil virou walk). Demo: hitstop 6 vbl depois
  troca para a strip de recover e segura o hold.
- ROM
  `0bde1dd0cd9e3ed7b2958e88b3c1fbb8690cf5f6e4bdf5b29c2ab16b7b60b9a9`
  BlastEm `blastem-linux-20260829T171301Z-2363210`. Burst 1 = punho a
  esquerda; burst 16 = unload.
- Continua `visual_pass=false`, `ready_for_aaa=false`.

## 2026-08-29 — CRIA haymaker nativo apos telegraph (build_v007)

- Launch/active/hitstop/recover 3-4-6-5 no grid 48x64. Pulseira no braco
  armado; o punho viaja da direita (telegraph) para a esquerda (Taina).
- Video recusado (jab do braco da frente). Dois pes plantados. Demo segura
  o hitstop. ROM
  `c63092cf27dbb6fbcd87f684f02f89051e2b307b5957c7011d75b35a74d83de6`
  BlastEm `blastem-linux-20260829T165936Z-2328459`. Burst frame 16 = punho
  estendido; o still pos-warmup caiu no idle.
- Continua `visual_pass=false`, `ready_for_aaa=false`.

## 2026-08-29 — CRIA telegraph 12 vbl nativo (build_v006)

- Coil/load/peak/hold 3-3-4-2, braco armado, dois pes plantados.
- Video recusado (pulseira no braco da frente). ROM
  `ed032430c6903e211efe4c2bd04090995171f1e49613ec6ab062f84d609ae36f`
  BlastEm `blastem-linux-20260829T164437Z-2288660`.
- Continua `visual_pass=false`, `ready_for_aaa=false`.

## 2026-08-29 — CRIA walk 4 fases nativo (build_v005)

- Walk 3/4: contact/pass/contact/pass, 5-4-5-4, um pe plantado, passada 4 px.
- Video recusado (dois pes no ar). Pixels no grid travado da idle.
- ROM `4e9248a42f64e78590e85e4506729cc4bf9ad52e63298d3b3570104d1e8a7847`
  BlastEm `blastem-linux-20260829T163328Z-2259788`. Burst prova a passada.
- Continua `visual_pass=false`, `ready_for_aaa=false`.

## 2026-08-29 — CRIA idle nativo 48x64 no CAIS_01 (build_v004)

- Pipeline F-R2 aplicado ao jogo: Imagine construction (nao sprite sheet MD)
  + lineart 1px + color hue-shift + idle 4 frames no grid 48x64.
- Video idle recusado como fonte de pixel (harvest levantou o pe).
- PAL3 = roster inimigo. Sem H-flip (viseira assimetrica).
- ROM 262144 B sha256
  `854a18bea4fc8bdff7d71908bc52d8796d7a08a3b77753a479ff16810720de54`
- BlastEm cena 3 `blastem-linux-20260829T162243Z-2229911`, semantic gate
  `passed`. Bundle canonico rejeitado (VLAB/dump).
- CRIA nativa ainda abaixo da TAÍNA v02; `visual_pass=false`,
  `ready_for_aaa=false`. Sem IA, sem dano, sem ESTIVADOR.

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


## 2026-07-03 - project_birth_fase1

- Task: nascimento canonico + FASE 1 (GDD e first playable slice)
- Projeto criado via `new_project.sh` (template `tools/sgdk_wrapper/modelo`, rota Vibe Playable `blocked_no_premium_source`)
- NOTA DE VERDADE: as entradas de changelog acima desta (2026-06-03) foram herdadas do template e descrevem builds do projeto-modelo, nao deste projeto; `out/` foi removido no nascimento
- `doc/project_context_manifest.json` classificado `aaa_game`/`active` (validado: blockers=0)
- `doc/genre_specialization_manifest.json` criado com opt-in humano `brawler_belt_scroll`
- FASE 1 escrita: `doc/00-project-brief.md`, `doc/11-gdd.md`, `doc/12-roteiro.md` (roteiro scope), `doc/13-spec-cenas.md` (CAIS_01 + seeds S2-S6)
- Tecnicas do slice: `line_scrolling`, `camera_scroll_management`, `hitstop_camera_shake_feedback`; adiadas: `palette_cycling`, `shadow_highlight_mode` (status LABORATORIO)
- Host de producao: Manjaro Linux com loop build->BlastEm provado via SMOKE_TEST nesta mesma sessao (Wine/binfmt)
- Status geral do projeto: `documentado`; sem build, sem arte, sem evidencia (correto para FASE 1)
- Proxima fase: FASE 2 (tdd_contract + brawler design contract) e FASE 3 (direcao de arte CAIS_01)

## 2026-07-03 - fase2_fase3_contratos_e_direcao_de_arte

- Task: FASE 2 (architecture first) + FASE 3 (direção de arte)
- FASE 2: emitidos e validados doc/contracts/{tdd_contract, brawler_belt_scroll_design_contract, mechanic_contract, level_blueprint, enemy_roster}.json + frame_data/ (6 arquetipos)
- doc/genre_specialization_manifest.json reescrito schema-conform (opt-in humano, freeze_axes_acknowledgement)
- Gates: audit_game_design_contracts=passed blockers=0; brawler validator passed=11 failed=0 (CI 23/23); schemas 100% via jsonschema
- FASE 3: doc/art/ completo (decision record angular_cps2_fighter conf 0.70, master_style_manifest, moodboard, brand_identity planned, drift policy, diagnostic 3_no_art, art_generation_brief)
- 16 PRDs materializados; check_prd_readiness=ok blockers=0 (prototype)
- Higiene: corrigido compiled_from com caminho absoluto de drive Windows herdado do template; validate_project_hygiene=passed
- Metodologia: claims classificados (critical_motion not_applicable em planning, road_physics/modular_boss not_applicable); validate_project_methodology=passed
- BLOCKER ATIVO: canal de geração de imagem indisponível no host (generation_channel_decision.json); premium source aguarda canal
- Fix canônico correlato (tools/sgdk_wrapper): validate_brawler_belt_scroll_specialization.ps1 corrigido para pwsh 7.5+ (OrderedDictionary + DateKind String), CI 23/23

## 2026-07-03 - resposta_ao_parecer_curatorial

- Task: correcoes curatoriais (parecer humano de 2026-07-03)
- Status renomeado: pre_producao_documentada_com_template_tecnico (nao e prototipo/slice/jogo)
- Novos contratos: slice_scope_contract.json (anti-falso-verde) e tilemap_streaming_contract.json (cais 1344px: janela 64x32, max 2 colunas/frame, seam policy, fallbacks; scene_local_preload vetado)
- Direcao de arte: trio de prova MD-nativo (SOR2/Shinobi III/Comix Zone) + human_ratification=pending + vdp_survival_proof (contact sheet 320x224) + fallback vibrant_16bit_pixel
- Rota de arte corrigida: IA apenas concept_art; doc/art/prompt_pack/ com 6 docs de prompts especificos para geracao humana; sequencia autoral model sheet -> lineart 1px -> key poses -> strips
- art_gameplay_direction_gate.json preenchido (producao autorizada so para Etapa A)
- TDD: audio_ownership corrigido para XGM2 real (FM+PSG do driver, SFX via PCM, sem acesso direto), tilemap_column_streamer no DMA ownership, riscos r5/r6
- Divida declarada: scene_branding.c viola ownership (CRAM/HScroll CPU no update + PSG direto) - refatorar antes do runtime
- Wrappers locais .bat corrigidos (profundidade de delegacao corrigida de tres para dois niveis); metadados build_v001/v002 herdados removidos
- Framework canonico: 4 correcoes encaminhadas (ready_for_aaa em planning, source/res no diagnostico, higiene vs texto historico, visual gate em out/logs)
- validation_report regenerado: de 4 erros para 1 (res_graph ausente, honesto ate a conversao de arte). Corrigidos: doc_refs verificaveis das tecnicas (spec+memory bank+changelog), .agent local como symlink canonico, marcadores do GDD (kit do jogador, ensino invisivel, qualidade visual, direcao sonora). Blockers restantes sao estado honesto de pre-producao (gates visuais sem arte, closeout sem cena)

## 2026-07-03 - concepts_recebidos_prova_vdp_aprendizados

- Task: processamento dos concepts gerados pelo humano via prompt pack
- 15 concepts recebidos e normalizados (portable_descriptive_v1; par do CRIA movido da pasta do estivador)
- premium_source_manifest v2: 15 assets `source_candidate` com sha256, desvios globais declarados (proporcao realista; texto diegetico emergente)
- Prova VDP: data/processed/contact_sheets/vdp_survival_contact_sheet_v01.png (320x224+15c+snap 9-bit) — cenarios/BG/logo sobrevivem; personagens exigem model sheet pixel autoral (borrao no downscale direto)
- art_direction_decision_record + art_gameplay_direction_gate atualizados: ratificacao humana pendente com evidencia pronta; blocker novo `no_pixel_model_sheet`
- Aprendizado: 7 licoes no learning_ledger (6 candidatas canonicas), success/failure patterns e skill_promotion_candidates atualizados para o estudo canonico posterior; promocao automatica proibida (correto)

## 2026-07-03 - correcao_level_art_modular_cais01

- Task: corrigir rota de produção visual do CAIS_01 para impedir panorama-first e preservar autoria do level design pelo agente canônico
- Novo contrato: `doc/contracts/level_art_assembly_contract.json` (`cais_01_level_art_assembly_v1`) define `scene_kit` modular, ownership correto, gramática de montagem, blockers e artefatos esperados antes de qualquer `res/`
- `doc/art/art_generation_brief.md` atualizado para v3: Etapa A0 obrigatória antes da nova arte do cais; painéis atuais reclassificados como `mood_reference_only` / `landmark_reference_only`
- `doc/art/prompt_pack/03_cais_world_concept.md` substituído: sai o pedido de 3 painéis 16:9; entram prompts para floor/edge tiles, props, landmarks, BG_B parallax, foreground/occlusion e ecology loops
- Decisão curatorial: modelo de imagem gera matéria-prima; agente monta `world_layout_board` 1344x224 com `level_blueprint`, câmera, streaming, parallax, foreground e gameplay anchors
- Blockers novos do CAIS: `level_art_assembly_not_built`, `dock_scene_kit_missing`, `panorama_first_pipeline_rejected`, `world_layout_board_missing`, `budget_not_measured`, `blastem_evidence_missing`

## 2026-07-03 - cais01_level_art_modular_artefatos_de_montagem

- Task: etapa documental/curatorial do CAIS_01 como level modular (level_art_assembly_contract)
- Auditoria de sources: bgb_loop=modular_reference_usable; 3 paineis de arena reclassificados mood/landmark_reference_only no premium_source_manifest; lacuna real = 6 boards modulares (prompts A-F) + railing kit complementar
- Novos artefatos (doc/contracts/): dock_scene_kit_inventory, object_role_map (25 objetos, 9 funcoes canonicas), object_placement_map (camera script 3 locks, politica de ring-out por trechos com grade quebrada em x=944, costuras x=352/704/1056), parallax_layer_contract (4 bandas 0.125-0.5, costura do loop protegida), background_ecology_card (7 loops, foam nunca corta, teto 98 patterns)
- doc/art/world_layout_board_1344x224.png: board visual do plano de montagem (fases, locks, beirada, landmarks, golden path, regua de streaming)
- Blockers limpos: object_role_map_missing, world_layout_board_missing; mantidos: dock_scene_kit_missing, level_art_assembly_not_built, budget_not_measured, blastem_evidence_missing
- Vocabulario: tudo `documentado`; nada implementado/buildado/testado_em_emulador/validado_budget

## 2026-07-04 - prompt_mestre_source_candidates_imagem

- Task: aplicar correção humana do pack visual para que o agente de imagem gere matéria-prima premium organizada, não level/sprite/tilemap final
- Criado `doc/art/prompt_pack/06_image_agent_master_prompt.md` com contrato autocontido para outro agente de imagem: leituras obrigatórias, paleta, estilo, negative prompt, asset IDs, fluxo de 4 variações, registro de seed/config e status proibidos
- Atualizados prompts 00-05: tudo `concept_art` / `source_candidate`; saídas por `asset_id`; teste conjunto de silhueta; teste monocromático/miniatura do logo; HUD/FX separados; `dock_pickups_small_props` adicionado ao kit do cais
- Criados `doc/art/prompt_revision_report.md` e `doc/art/asset_acceptance_report.json`
- `premium_source_manifest.json`: adicionada política de status; `bgb_loop` reclassificado como `mood_reference_only` (referência de bandas BG_B, não camada final nem source direto para `res/`)
- `doc/art/art_asset_diagnostic.json` atualizado para o estado real: concepts existem, mas permanecem bloqueados para promoção; rota correta é `data/source_art/concept/<asset_id>/` + contact sheet + ratificação humana
- Diagnóstico de arte rodado: cenário `2_res_inadequate_check`; PNGs de concept/source estão RGB/RGBA e reforçam que nenhum asset pode ir para `res/` sem conversão VDP, budget e evidência
- Status: `documentado`; nenhuma imagem nova gerada, nenhum build, nenhuma ROM, nenhuma evidência BlastEm
## 2026-07-04 - contrato_traco_autoral_e_lote_visual

- Task: eliminar vagueza estética, corrigir agente canônico, revisar prompts e gerar novo lote visual para validação humana.
- Criado `doc/art/authorial_line_style_contract.json`; manifesto, drift policy, gate de arte e prompt pack 00-06 sincronizados.
- Framework canônico: catálogo `angular_cps2_fighter`, regras globais e personas de criação/direção agora exigem assinatura de linha, hooks de silhueta, gramática facial/material e veto à arte intercambiável.
- Geradas 6 pranchas `source_candidate`: TAÍNA turnaround, CRIA+ESTIVADOR/silhuetas, kit modular do cais, logo, HUD/FX e poses-chave da TAÍNA.
- Uma primeira geração do kit do cais foi rejeitada por inserir rótulos; ficou em `descartes/` com hash e motivo.
- Criados batch manifest, contact sheet e report AAA conservador; `premium_source_manifest.json` atualizado para 21 assets.
- Status: `documentado`; aguardando ratificação humana. Nenhum asset foi promovido a `res/`, nenhum budget foi validado e nenhuma ROM foi buildada/testada por esta mudança.

## 2026-07-08 - taina_lineart_v03_v04_reprovacao_visual

- Task: continuar tradução da TAÍNA para lineart nativo 48x64 sem promover asset visualmente fraco.
- Candidatos v03/v04 produzidos e validados tecnicamente: PNG indexado, 192x64, 4 células de 48x64, índices `[0,1]`, magenta no índice 0 e cor visível em grade Mega Drive.
- Criados relatórios `doc/art/characters/taina/model_sheet_to_sprite_fidelity_report_v03.json` e `v04.json`.
- Atualizados `lineart_blocking_report_v01.json`, `native_grid_translation_report_v01.json` e `visual_dna_manifest.json` para refletir `model_sheet_to_sprite_fidelity_failed_v04`.
- Resultado visual: v04 é ligeiramente mais limpo que v03, mas ainda genérico/simbólico; perde rosto, hair mass e guarda diagonal da TAÍNA. Uso autorizado apenas como evidência negativa.
- Diagnóstico global de arte salvo em `out/logs/art_asset_diagnostic_report.json`: 15 assets ok, 29 precisam conversão; linearts TAÍNA v01-v04 tecnicamente ok. Sem `res/`, sem color blocking, sem build, sem evidência BlastEm nesta mudança.

## 2026-07-08 - build_v001_smoke_tecnico_sem_emulador

- Task: auditar rota de build do MARE_BRAVA após registrar a falha visual da TAÍNA.
- Preflight: passou com variáveis temporárias Linux para evitar `Path null` em helpers ainda orientados a Windows; GDK local, make, Java, Python e ImageMagick ok.
- Build direto Linux: falhou por caminho do GDK com espaço e por mismatch entre `/usr/sbin/m68k-elf-gcc` 16.1.0 e `libmd.a` LTO 13.0.
- Build smoke bem-sucedido via overlay temporário `/tmp/sgdk_win_overlay`, usando os binários Windows GCC 13.2.0 do `sdk/sgdk-2.11` via Wine/binfmt.
- ROM: `out/rom.bin` e snapshot `doc/changelog/roms/build_v001/rom.bin`, 262144 bytes, SHA-256 `5c1489fa944be7f62a06192beef4c783c3f0f2d2939b59d08958b996b0131e75`.
- Metadata: `doc/changelog/roms/build_v001/build_meta.json`.
- Validação pós-build: `validate_resources.ps1` reconheceu a ROM, mas segue com 1 erro/7 warnings por visual delivery, budget/tilemap reports, freshness e scene closeout ausentes.
- Status: `buildado` técnico apenas. Sem BlastEm, sem runtime capture, sem performance/gameplay/audio provados; entrega final continua bloqueada.

## 2026-07-08 - build_v001_boot_blastem_limitado_selado

- Task: completar a evidência mínima de emulador para a ROM build_v001 sem inflar claim de gameplay/AAA.
- A automação canônica `capture_blastem_evidence.ps1` falhou no host Linux antes de abrir sessão por dependência WinForms (`System.Windows.Forms.dll`) no módulo BlastEm; a falha ficou registrada como tentativa canônica.
- Fallback manual controlado: BlastEm rodou via Wine, exigiu fonte `arial.ttf` no Wine prefix temporário, e a janela principal apresentou `SAMPLE PROGRAM - BlastEm - 58.6 fps`.
- Screenshot selado: `out/blastem_env_manual_20260708_build_v001/screenshots/blastem_after_font_20260708_build_v001.png`, 640x480, SHA-256 `39223130566104848e310565216554f49ec1b274b68b3e0a6ce686dfbd71c3af`; visualmente mostra `MENU INICIAL` e HUD/debug do menu.
- Log selado: `out/blastem_env_manual_20260708_build_v001/blastem_stdout_stderr_after_font.log`, SHA-256 `3685bc1730e1b3f5e0d42267ca7798e50a16b2fcafa08ef674577ca77d3e8cdb`.
- `finalize_emulator_evidence.ps1` refechado com `seal_status=sealed`; ROM capturada e ROM atual compartilham SHA-256 `5c1489fa944be7f62a06192beef4c783c3f0f2d2939b59d08958b996b0131e75`.
- O Wine prefix temporário (~686 MB) foi removido após a captura porque não faz parte do pacote selado e travava varreduras recursivas do validator.
- `validate_resources.ps1` concluído depois da reconciliação: 1 erro/6 warnings; `emulator_evidence_reason=ok`, `boot_emulador=ok`, `testado_em_emulador=true`, `aggregate_status=emulator_observed_budget_pending`, `max_delivery_status=technical_artifact_only`.
- Status honesto: evidência BlastEm cobre boot/menu apenas. Sem `save.sram`, sem `visual_vdp_dump.bin`, sem gameplay básico, performance, áudio, hardware real ou budget VDP aprovados. Entrega visual/AAA continua bloqueada por `visual_gate_blocked`, `visual_delivery_gate_missing`, `res_graph_missing_for_visual_delivery`, `scene_tilemap_conversion_report_missing`, `per_tile_palette_conflict_report_missing`, `freshness_audit_stale` e `scene_closeout_gate_missing`.

## 2026-07-08 - scene_contract_e_res_graph_observados

- Task: atacar blockers observacionais sem promover arte nem reconstruir ROM.
- `scene_contract_compiler.ps1 -Mode production -WarnOnly` gerou `out/logs/scene_contract_compile_report.json` e recompilou `doc/scene-contracts.json` com 4 cenas; o report ficou `status=ok`, mas o lint interno não rodou (`lint_ran=false`, `lint_status=error`), então serve como observação parcial, não gate limpo.
- `res_graph_audit.ps1 -WarnOnly` gerou `out/logs/res_graph_report.json` e `out/logs/res_graph_summary.md`: 1 `.res`, 10 declarações ok, 0 missing, 0 unparsed, 5 imagens, 5 áudios, 0 issues.
- O blocker `res_graph_missing_for_visual_delivery` saiu do validator, e `validate_resources.ps1` passou a fechar com 0 erros/6 warnings.
- Limite técnico: `res_graph_report` ainda não valida budget VDP; `vram_residency_status=not_measured`, `measurement_level=estimated`, `sprite_reserve_tiles=420`, `vram_overlap_count=0`, e os `tile_stats` das imagens falharam no host Linux por dependência de imagem/.NET. Veredito VDP permanece “não medido”.
- Freshness final: `stale_count=0`, `missing_required_count=1`; falta `out/logs/build_output.log`. Não foi feito rebuild só para gerar log, porque rebuild pós-captura mexeria no contrato de evidência da ROM já selada.
- Blockers restantes: `visual_gate_blocked`, `visual_delivery_gate_missing`, `scene_tilemap_conversion_report_missing`, `per_tile_palette_conflict_report_missing`, `freshness_audit_stale` e `scene_closeout_gate_missing`.

## 2026-07-08 - visual_delivery_gate_report_bloqueado

- Task: substituir o blocker genérico `visual_delivery_gate_missing` por um relatório explícito e auditável de bloqueio visual.
- Criado `out/logs/visual_delivery_gate_report.json` com `ready_for_aaa=false`, `visual_route_status=visual_gate_blocked`, `max_delivery_status=technical_artifact_only` e critical assets para TAÍNA, CAIS_01 tilemap e evidência visual de boot/menu.
- O report declara que a lineart atual da TAÍNA segue rework e sem animation gate; CAIS_01 não tem `scene_tilemap_conversion_report` nem `per_tile_palette_conflict_report`; a captura BlastEm é evidência de boot/menu, não aprovação visual.
- `validate_resources.ps1` passou a fechar com 0 erros/8 warnings e blockers: `visual_gate_blocked`, `visual_direction_failed`, `animation_gate_failed`, `scene_tilemap_conversion_report_missing`, `per_tile_palette_conflict_report_missing`, `freshness_audit_stale`, `scene_closeout_gate_missing`.
- Freshness continua `stale_count=0`, `missing_required_count=1` (`out/logs/build_output.log` ausente). Sem rebuild por causa do contrato de evidência já selado.

## 2026-07-08 - taina_lineart_v05_melhoria_parcial

- Task: atacar o blocker visual da TAÍNA sem promover asset fraco para `res/`.
- Gerado `data/processed/characters/taina/lineart/taina_lineart_clean_native_48x64_candidate_v05.png`: PNG indexado `P`, 192x64, 4 células de 48x64, índices `[0,1]`, index 0 magenta, cor visível `#220044` na grade Mega Drive; SHA-256 `3fe2aa6de8f51170a32b66b3dfb5bda793e54d929a9b498d6b974129c945c615`.
- Reviews: `doc/art/characters/taina/review/taina_lineart_clean_native_48x64_candidate_review_8x_v05.png` e `doc/art/characters/taina/review/taina_lineart_v04_v05_compare_8x_v01.png`.
- Criado `doc/art/characters/taina/model_sheet_to_sprite_fidelity_report_v05.json`: decisão `partial_visual_improvement_not_promoted`. v05 recupera parte de cabelo cacheado, face wedge, guarda alta, luvas, faixa e calça larga, mas ainda deriva para proporção chibi e não possui animation gate.
- Atualizados `lineart_blocking_report_v01.json`, `native_grid_translation_report_v01.json`, `visual_dna_manifest.json` e `out/logs/visual_delivery_gate_report.json` para blocker `partial_visual_improvement_scale_and_animation_blocked_v05`.
- Diagnóstico de arte: 45 assets, 16 ok, 29 precisam conversão; v05 aparece como OK técnico. Status honesto: sem color blocking, sem key poses, sem animation strip, sem promoção para `res/`, sem aprovação visual.
- Revalidação pós-v05: `validate_resources.ps1` manteve 0 erros/8 warnings; `freshness_audit.ps1` manteve `stale_count=0`, `missing_required_count=1` (`out/logs/build_output.log`).

## 2026-07-08 - taina_animation_contracts_v01_e_scale_probe_v07

- Task: reduzir o blocker `animation_gate_failed` de forma honesta, criando planejamento de animação antes de qualquer strip/key pose e testando correção de escala sem promoção.
- Criados `doc/art/characters/taina/animation/animation_state_plan_v01.json`, `frame_budget_table_v01.json`, `pivot_and_scale_contract_v01.json`, `motion_phase_map_p0_v01.json`, `animation_direction_contract_v01.json` e `animation_planning_gate_report_v01.json`.
- Gerados scale probes `taina_lineart_clean_native_48x64_candidate_v06.png` e `v07.png`; ambos passam sintaxe técnica PNG/PLTE/grid, mas não passam visualmente.
- v07: SHA-256 `b8342103628317977961f3e9ae764cd4c43b04280c66594ac601906faed2c6d1`; review `doc/art/characters/taina/review/taina_lineart_clean_native_48x64_candidate_review_8x_v07.png`; comparação `doc/art/characters/taina/review/taina_lineart_v05_v06_v07_compare_6x_v01.png`.
- Criado `doc/art/characters/taina/model_sheet_to_sprite_fidelity_report_v07.json`: decisão `scale_probe_not_promoted`. v07 melhora altura visível em relação à v05, mas regride cabelo/rosto/identidade e continua bloqueado por falta de key poses, contact sheet, pivot overlay, foot contact, frame delta e runtime.
- Atualizados reports canônicos da TAÍNA e `out/logs/visual_delivery_gate_report.json`; status segue bloqueado, sem `res/`, sem color blocking, sem build novo e sem evidência BlastEm nova.

## 2026-07-09 - roteamento_imagem_native_first_e_limpeza_de_bloqueios

- Task: corrigir desperdício operacional no canal de geração visual.
- Framework atualizado: `tools/ai_imagegen/imagegen_tool.py` e `imagegen_circuit.py` agora tratam `native_chat_image_generation_callable` como rota default auto-detectada em Codex/ChatGPT; Bonsai sem licença, host AMD e ComfyUI offline só bloqueiam quando não houver canal nativo/API.
- Skills/docs atualizadas: `image-generation-routing`, `art-creation-sourcing`, referência de roteamento e README do `tools/ai_imagegen` agora declaram native-first e proíbem gastar energia em Bonsai/ComfyUI quando a sessão atual consegue gerar imagens.
- Compatibilidade Linux corrigida: `assert_agent_environment.ps1` e `prepare_agent_environment.ps1` resolvem `pwsh`/`powershell` dinamicamente; `audit_project_learning.ps1` resolve `python`/`python3`/`py`; `validate_resources.ps1` deixou de chamar `powershell.exe`; `_lib/sgdk_common.ps1` não quebra quando `ProgramFiles` inexiste.
- Projeto atualizado: `generation_channel_decision.json` deve passar a refletir `selected_source=native_chat_image_generation_callable`; o blocker antigo de canal local fica superado. Continuam blockers reais: TAÍNA v08/lineart visual aprovado, decomposição do `dock_scene_kit`, conversão VDP, `scene_tilemap_conversion_report`, `per_tile_palette_conflict_report`, budget e evidência BlastEm visual.

## 2026-07-09 - taina_identity_turnaround_native_callable_v01

- Task: retomar o desenvolvimento visual usando a geração nativa de imagem conforme a curadoria do projeto, sem voltar para rotas locais precárias.
- Geradas 4 variações de `taina_identity_turnaround` via `native_chat_image_generation_callable`.
- Aceitas como `source_candidate`: `data/source_art/concept/taina_identity_turnaround/taina_identity_turnaround_v01.png` e `taina_identity_turnaround_v02.png`.
- Descartes auditáveis: `data/source_art/concept/taina_identity_turnaround/descartes/taina_identity_turnaround_discard_v01_tall_illustrative.png` e `taina_identity_turnaround_discard_v02_tall_illustrative.png`.
- Criados report e prompt log: `doc/art/characters/taina/taina_identity_turnaround_native_callable_review_v01.json` e `doc/art/generated_prompts/taina_identity_turnaround/taina_identity_turnaround_native_callable_v01.md`.
- Criadas contact sheets de revisão 320x224 e 320x224/16c em `doc/art/characters/taina/review/`.
- Atualizados `data/source_art/premium_source_manifest.json`, `doc/art/asset_acceptance_report.json`, `doc/art/prompt_revision_report.md`, `out/logs/visual_delivery_gate_report.json` e `doc/10-memory-bank.md`.
- Status honesto: melhoria de source concept, não sprite final. Sem promoção para `res/`, sem build novo, sem ROM nova e sem evidência BlastEm nova.

## 2026-07-28 - relatorio_direcao_de_arte_ver_001

- Criado `doc/21-relatorio-direcao-de-arte-ver-001.md`, um parecer historico e tecnico sobre a criacao artistica ate 2026-07-09.
- O parecer reconcilia changelog, memory bank, manifests de fonte/aceite, contratos do CAIS_01, provas visuais e relatorios de fidelidade da TAÍNA; as entradas de 2026-06-03 permanecem classificadas como heranca do template.
- Nenhuma imagem foi criada, convertida ou promovida; nao houve build, mudanca de ROM, medicao de budget ou alteracao de status de entrega.

## 2026-07-28 - linha_do_tempo_visual_ver_001

- Criado `doc/22-linha-do-tempo-visual-ver-001.md`, apendice cronologico que liga cada imagem relevante a sua decisao de direcao de arte.
- A linha do tempo registra a transicao concept -> prova VDP -> scene kit modular -> assinatura autoral -> lineart iterativo -> source renovado, sem alterar assets ou status de producao.

## 2026-07-28 - protocolo_local_iteracao_visual_taina

- Registrado `doc/art/characters/taina/iteration_control_protocol.md` para impedir que uma iteracao tecnicamente conveniente substitua silenciosamente a fonte autoral da TAÍNA.
- A regra exige fonte incumbente, `must_preserve`, uma correcao visual por vez, comparacao nativa lado a lado e bloqueio de candidatos que regredirem identidade.
- Licao L10 adicionada a `doc/agent_learning/failure_patterns.md`; `learning_ledger.json` nao foi editado diretamente por ser derivado.
- Nenhuma imagem, recurso SGDK, ROM, budget ou status tecnico foi modificado.
- Decisao humana complementar: imagem 04 da linha do tempo e baseline de direcao; imagens 05/06 sao retrocessos e nao podem alimentar nova geracao.

## 2026-07-28 - visual_source_of_truth_taina_v01

- Fixada a imagem 04 como baseline humana e a fonte individual autoral da TAÍNA como origem permitida da proxima producao em `doc/contracts/visual_source_of_truth_taina_v01.json`.
- v05, v06 e v07 foram declarados `obsolete_for_generation_source`; uso limitado a evidencia negativa/comparacao.
- Nenhum novo PNG foi gerado, convertido ou promovido; a proxima entrega continua sendo lineart 1px, nao sprite final.
- Criado `doc/art/characters/taina/taina_lineart_v08_authoring_card.md`, cartao de producao da proxima prancha de lineart 1px: corrige apenas escala/proporcao e bloqueia qualquer regressao de identidade.
- Ativada a persona `art-director` para a v08 e criado `doc/art/characters/taina/taina_v08_visual_breakdown.md`, que transforma a imagem 04 em criterios de silhueta, linha, materiais e veto.
- Gerado e arquivado somente para revisao o rascunho `rascunho/taina_lineart_v08/taina_lineart_v08_directional_draft_v01.png`; o respectivo parecer declara que nao cabe no grid 48x64 e nao pode ser convertido/promovido diretamente.

## 2026-07-28 - taina_idle_guard_directional_draft_v01

- Aprovacao humana liberou a primeira etapa de sprites pelo fluxo de animacao: `idle_guard`, uma unica acao em seis celulas de 48×64, com pivô e contato de solo declarados no contrato `doc/art/characters/taina/animation/taina_idle_guard_strip_v01.json`.
- Gerada e arquivada para revisao a prancha `rascunho/taina_idle_guard_v01/taina_idle_guard_directional_draft_v01.png`; prompt em `doc/art/generated_prompts/taina_idle_guard_v01_directional_draft_v01.md` e parecer em `doc/art/characters/taina/animation/taina_idle_guard_directional_draft_review_v01.json`.
- Resultado: boa retomada de cabelo, rosto, guarda e faixa assimetrica da direcao aprovada, sem reutilizar v05/v06/v07. Continua uma prancha RGB em alta resolucao: nao e pixel sheet nativa e nao foi promovida para `data/` ou `res/`.
- Proxima entrega obrigatoria: redesenho nativo/medicao de pivot e pe, paleta/indexacao, preview e validacao da strip. Nao houve build, ROM, emulador ou budget novo.

## 2026-07-28 - taina_idle_guard_native_48x64_v01

- Traduzida a referencia direcional em strip horizontal de seis frames 48x64: `data/processed/characters/taina/animation/taina_idle_guard_native_48x64_v01.png`.
- Copia candidata a runtime em `res/sprites/characters/taina/taina_idle_guard_48x64_v01.png` e declaracao `SPRITE spr_taina_idle_guard` adicionada a `res/resources.res`.
- Integridade, grid, paleta indexada, indice 0 e passos de cor Mega Drive foram checados; o report nao encontrou clipping, matte ou FX embutido.
- ResComp nao foi executado porque este host nao oferece Java. Assim, o asset esta em staging de `res`, aguardando compilacao e prova em ROM/emulador; nenhum status de entrega foi promovido.

## 2026-07-29 - host_recovery_and_taina_idle_guard_rescomp

- Com autorizacao humana via `bigsudo`, o host Manjaro recebeu `powershell-bin`, `jre17-openjdk` e `wine`; `assert_agent_environment.ps1` e `preflight_host.ps1` voltaram a passar.
- Corrigida a declaracao SGDK da TAÍNA: `SPRITE` recebe dimensoes em tiles, logo a strip 48×64 usa `6 8`, nao `48 64`. ResComp 3.95 compilou os seis frames: 2 sprites VDP e 24 tiles por frame.
- O build recompilou fontes/resources depois de preservar caches LTO antigos em backup recuperavel, mas o link final falhou por incompatibilidade interna do SDK: `libmd.a` LTO 16 versus `gcc.exe` LTO 13.
- O asset passa a `rescomp_compiled`; build/ROM/emulador permanecem bloqueados por `sdk_lto_version_mismatch`.

## 2026-07-29 - linux_build_route_curation_and_success

- O mismatch observado no link foi reclassificado corretamente como
  `toolchain_wrapper`: o compilador empacotado é GCC 13.2.0 e a `libmd.a`
  canônica contém LTO produzido por GCC 16.1.0.
- Criado e executado o seletor canônico
  `tools/sgdk_wrapper/select_sgdk_build_route.py`; report local em
  `out/logs/sgdk_build_route_report.json`.
- No host Linux, a rota selecionada foi
  `build_sgdk_wine_bridge.sh`: staging isolado do SGDK, biblioteca reconstruída
  sem LTO pelo GCC 13 e build do projeto com `LTO=0`. O SDK de origem não foi
  alterado.
- ResComp, compilação C e link passaram. ROM:
  `out/rom.bin`, 262144 bytes, SHA-256
  `8ed8f28bde41cc4987718079f7584c6d90cbe1cad22a73f1b953857b367a434d`;
  prova em `out/logs/linux_wine_build_report.json`.
- Rota Windows registrada separadamente: usar `build.bat`, com gate prévio de
  coerência entre major do `gcc.exe` e produtor LTO da `libmd.a`; mismatch
  bloqueia e exige restaurar/reconstruir a biblioteca antes do build.
- Não houve execução da ROM nova no BlastEm. Evidência antiga não foi
  promovida; status máximo da ROM atual é `buildado_emulator_pending`.

## 2026-07-29 - taina_idle_guard_runtime_review_v01

- `spr_taina_idle_guard` integrado à cena demo com pivot `(24,60)`, ground
  `y=168`, PAL1 e flip horizontal por hardware.
- Adicionada injeção QA de cena por bloco `SBIS` assinado em SRAM; o boot normal
  não foi alterado.
- Build Linux pela bridge passou: ROM 262144 bytes, SHA-256
  `3c4c6c5d4294a9f0042e1bbfdd1e66b7f2b2b3eca167489f23b54d2add99eb44`.
- BlastEm capturou cena 3, screenshot, GIF, 12 frames, SRAM e métricas em
  `out/blastem_env_taina_idle_guard_v01/blastem-linux-20260729T090809Z-192035/`.
- Resultado: sprite e ciclo visíveis, mas revisão visual reprovada. A v01
  perdeu identidade, silhueta, rosto, materiais e gesto da imagem 04.
- Status: `technical_runtime_pass_visual_fail`; evidência parcial, sem VLAB e
  sem dump VDP. Não é entrega AAA nem `testado_em_emulador`.

## 2026-07-29 - taina_idle_guard_authorial_reconstruction_v02

- Nova prancha criada usando somente a fonte autoral da imagem 04; v01 e
  linearts v05-v07 permanecem proibidos como fontes de geração.
- `taina_idle_guard_authorial_study_v02.png`: recuperação visual bem-sucedida,
  mas 2172×724/160957 cores, mantida apenas em `rascunho/`.
- Proxy diagnóstico convertido para 288×64/14 cores. O frame 0 alinhado em
  ground y=60 foi preservado como candidato de pose-mestre v02.
- Strip completo reprovado por morphing: drift horizontal de 7 px, drift de
  altura de 3 px e redesenho de cabeça/corpo entre frames.
- Nova regra: uma pose-mestre aprovada e animação derivada por edição pixel
  controlada; geração independente de frames fica vetada.
- Nenhum asset foi promovido para `data/processed` ou `res/`; ROM não foi
  reconstruída com v02.

## 2026-07-29 - taina_idle_guard_v02_runtime_partial_pass

- Aprovação humana registrada para o resultado visual v02. A pose-mestre limpa
  48×64 tornou-se a incumbente da TAÍNA; v01, proxy v02 com morphing e
  linearts v05-v07 continuam proibidos como fontes.
- Strip final desta etapa promovida para
  `data/processed/characters/taina/animation/taina_idle_guard_native_48x64_v02.png`
  e `res/sprites/characters/taina/taina_idle_guard_48x64_v02.png`, SHA-256
  `5d17c164815eecf821cdd83dd45125fa0c57601facc7566307bc3c1cf6a58cde`.
- Seis quadros usam pivot/bbox/massa fixos e holds NTSC
  `[11,7,10,7,11,12]`; a animação manual foi integrada em `scene_demo.c`.
- ResComp passou com 2 partes de metasprite e 24 tiles por quadro. O ciclo
  mede 40 tiles únicos/1280 bytes. Build Linux passou: ROM 262144 bytes,
  SHA-256 `e6b84c604a2dd26662e2e4603ff79a276351cb77447bb9e8d4874a2c6ffaab15`.
- BlastEm capturou cena 3, screenshot, GIF, 12 quadros, SRAM e métricas em
  `out/blastem_env_taina_idle_guard_v02/blastem-linux-20260729T094431Z-325801/`.
  Janela: 60.2 fps; MDRT parcial: 151 frames, 32 amostras, CPU máximo 28%,
  p95 27%, 0 frames acima do budget.
- Parecer visual:
  `technical_runtime_pass_visual_direction_pass_partial_evidence`. A autoria e
  a estabilidade sobrevivem no runtime, mas faltam VLAB e dump VDP; não é
  `testado_em_emulador`, AAA nem budget completo.
- Aprendizado L13 registrado em `doc/agent_learning/success_patterns.md`.
- `animation_state_plan_v01.json`, `frame_budget_table_v01.json` e
  `animation_planning_gate_report_v01.json` foram sincronizados com a v02:
  fonte aprovada, escala fixa de 59 px, holds reais e veto às fontes
  reprovadas. O restante do P0 continua planejado/não produzido.
## 2026-07-29T06:52:24.2222439-03:00 - taina_idle_guard_v02_runtime_partial_pass

- Task: taina_idle_guard_v02_runtime_partial_pass
- Skills: sprite-animation,megadrive-pixel-strict-rules,megadrive-vdp-budget-analyst,sgdk-runtime-coder,sgdk-build-wrapper-operator,emulator-vdp-evidence-curator
- Asset snapshots:
  - spr_taina_idle_guard -> v001 (/res/sprites/characters/taina/taina_idle_guard_48x64_v02.png)
- ROM: build_v002 (sha256 e6b84c604a2dd26662e2e4603ff79a276351cb77447bb9e8d4874a2c6ffaab15, 262144 bytes)
- Notes: TAINA idle_guard v02 aprovada visualmente, promovida para res, buildada e observada na cena 3 do BlastEm. Evidencia parcial: faltam bloco VLAB e visual_vdp_dump.bin; sem claim testado_em_emulador ou AAA.

## 2026-07-29 - taina_combo_hit_1_jab_directional_study_v01

- Próximo estado de combate separado como `combo_hit_1_jab`; o legado
  `light_jab_cross` fica apenas como agrupamento do roster. Isso preserva o
  combo do GDD: `jab -> cross -> low_kick`.
- Gerada uma única pose de contato ativo a partir da fonte autoral e da pose
  idle v02 aprovada:
  `rascunho/taina_light_jab_cross_v01/taina_light_jab_active_directional_study_v01.png`,
  SHA-256
  `8b3c1a73623c7e279141c67fbe410ac6296d3b8b97ca53b7d08f9d8d626cac48`.
- A pose passa topologia e identidade como estudo direcional, mas é RGB
  1024×1536 com antialiasing/fundo variável. Status:
  `directional_study_pass_native_key_pose_pending`; sem promoção para
  `/data/processed` ou `/res`.
- Criados review, prompt e contrato de produção. A ação usará célula 64×64,
  pivot `(24,60)`, altura visível de 59 px, cinco fases `[3,2,2,3,4]` e frame
  ativo 2. Os quadros deverão ser derivados de uma pose nativa aprovada, não
  gerados independentemente.
- Nenhum recurso SGDK, código, build ou ROM mudou nesta etapa.

## 2026-07-29 - taina_combo_hit_1_jab_native_key_pose_v01

- A direção humana do contato ativo foi registrada como aprovada; o gate
  seguinte permaneceu separado para a pose pixel nativa.
- Criado builder determinístico local:
  `tools/art/build_taina_combo_hit_1_jab_key_pose_v01.py`. Ele reutiliza
  paleta, cabeça e base corporal da idle v02 aprovada e redesenha apenas os
  clusters do ombro e braço dianteiro.
- Gerada candidata 64×64:
  `rascunho/taina_combo_hit_1_jab_v01/taina_combo_hit_1_jab_active_key_pose_64x64_v01.png`,
  SHA-256
  `a468a9099bb88264f58f4e0d54c959cbaa3929017166ad2cc695dcc0597a6ff6`.
- Check técnico: PNG indexado, 10 cores visíveis, índice 0 transparente,
  cores na grade Mega Drive, bbox 45×59, uma única ilha conectada, pivot
  `(24,60)`, sem clipping, AA, alpha parcial ou FX assado.
- Parecer:
  `technical_pass_human_visual_review_pending`. O jab lê em 320×224, mas o
  diretor deve julgar a escala do punho dianteiro e a guarda traseira, que
  permaneceu abaixo da posição de mandíbula do estudo direcional.
- Nenhum frame adicional, strip, `/data/processed`, `/res`, recurso SGDK,
  build ou ROM foi criado nesta etapa.

## 2026-07-29 - taina_combo_hit_1_jab_res_build_runtime_partial_v01

- A pose pixel nativa foi aprovada pelo diretor de arte e usada como frame
  ativo de uma strip determinística de cinco quadros 64×64. Nenhum quadro foi
  gerado independentemente.
- Strip promovida para
  `data/processed/characters/taina/animation/taina_combo_hit_1_jab_native_64x64_v01.png`
  e `res/sprites/characters/taina/taina_combo_hit_1_jab_64x64_v01.png`,
  SHA-256
  `169f66374bb0d4b0916826c77fc3e0f00e3183d43f526a40db443f2b5a4ca876`.
- `validate_strip` e auditoria de artefatos passaram. Pivot, altura, contato de
  solo, paleta e topologia foram preservados; os deltas adjacentes medidos são
  `[165,135,158,158]` pixels.
- Recurso `spr_taina_combo_hit_1_jab` integrado à cena demo com holds
  `[3,2,2,3,4]`. O golpe responde a `C` no pad de três botões e `X` no pad de
  seis botões, retornando à idle após 14 VBlanks.
- ResComp mediu `[24,28,28,28,24]` tiles e `[2,2,3,2,2]` partes por quadro.
  O pico isolado do contato ativo é 28 tiles/896 bytes e três partes.
- Build Linux passou: ROM 262144 bytes, SHA-256
  `0c281347c4d1673855a45a646cd639a395d0ea7279e15cd0b28c49d538db3822`.
- BlastEm exibiu o ciclo na cena 3; screenshot, GIF, 48 quadros e SRAM estão em
  `out/blastem_env_taina_combo_hit_1_jab_v01/blastem-linux-20260729T111215Z-598254/`.
  O selo ficou rejeitado apenas por falta de VLAB, dump VDP e métricas.
- Status honesto:
  `buildado_runtime_animation_observed_partial_evidence`. Colisão, dano,
  cancelamento, hitstop confirmado, budget combinado e closeout continuam
  pendentes.

## 2026-07-29 - taina_combo_hit_1_jab_runtime_unique_v02

- Corrigida a classificação da prancha 6×8: são 48 amostras temporais do
  BlastEm, não 48 células do spritesheet.
- Confirmada duplicação real entre os frames físicos 0/4 do jab e a pose idle.
  Criado recurso 192×64 com somente três desenhos únicos:
  `taina_combo_hit_1_jab_runtime_unique_64x64_v02.png`, SHA-256
  `3032acffd192412005fd61ef30e95f8307a7806a4ed30ca253f67efca1aca783`.
- O runtime preserva cinco fases `[3,2,2,3,4]`, reutilizando idle frame 0 na
  antecipação e recuperação.
- Removidos todos os rótulos visíveis `START` da cena de revisão, inclusive o
  marcador BG_B que aparecia através das áreas transparentes. Nenhum pixel do
  sprite precisou ser reconstruído.
- ResComp passou com três frames físicos: `[28,28,28]` tiles e `[2,3,2]`
  partes. O recurso bruto caiu de 3668 para 2862 bytes; pico VRAM permanece
  28 tiles/896 bytes.
- Build Linux passou. ROM: 262144 bytes, SHA-256
  `825dc80baa346129512ea0ef0c0eba2ab09d2a4080824a07bdeb75ded532dd2a`.
- BlastEm confirmou boot da cena 3 e ausência do marcador sobreposto. O jab
  não foi acionado pelo transporte automático nesta captura; playback da ROM
  final permanece `recapture_pending`, sem transferência da evidência antiga.

## 2026-07-29 - taina_p0_locomotion_and_cais01_modular_slice_v01

- Criadas e promovidas como candidatas runtime as strips únicas de caminhada
  (6 quadros), corrida/avanço (4) e pulo (8), todas derivadas exclusivamente
  da TAÍNA idle v02 aprovada.
- Auditorias de integridade passaram para as três strips. O runtime da cena
  demo agora reproduz idle, andar, correr, pulo e jab com pivô inferior
  estável e seleção manual de frames.
- Construído o primeiro recorte 320×224 do CAIS_01 por módulos nativos:
  BG_B/PAL0 com céu, indústria e mar; BG_A/PAL2 com píer e props jogáveis.
  Nenhum panorama pronto foi promovido.
- ResComp mediu 204 tiles/6528 bytes para o cenário. O maior estado isolado
  da personagem é corrida/avanço, com 48 tiles e 6 partes.
- Build Linux passou. ROM: 262144 bytes, SHA-256
  `e1fc0dd5180ffb09f74087248f1d4d363ace93b5c1a74f0e307c1b8f3e05c1c6`.
- BlastEm comprovou visualmente os cinco estados e o cenário na mesma ROM.
  Evidência:
  `out/evidence/taina_cais01_runtime_v01/taina_cais01_runtime_contact_sheet_v01.png`.
- O pacote formal permanece bloqueado por ausência de VLAB, dump VDP e
  métricas runtime. Status: `buildado_runtime_observed_partial`; sem claim de
  arte final, budget combinado, `testado_em_emulador` ou AAA.
## 2026-07-29T13:37:12.8268296-03:00 - taina_p0_locomotion_and_cais01_modular_slice_v01

- Task: taina_p0_locomotion_and_cais01_modular_slice_v01
- Skills: sprite-animation,megadrive-pixel-strict-rules,multi-plane-composition,megadrive-vdp-budget-analyst,sgdk-runtime-coder,sgdk-build-wrapper-operator,emulator-vdp-evidence-curator
- Asset snapshots:
  - img_cais01_bg_b_mar_ceu -> v001 (/res/backgrounds/cais01/cais01_bg_b_mar_ceu_320x224_v01.png)
  - img_cais01_bg_a_pier_modular -> v001 (/res/backgrounds/cais01/cais01_bg_a_pier_modular_320x224_v01.png)
  - spr_taina_walk_combat_step -> v001 (/res/sprites/characters/taina/taina_walk_combat_step_48x64_v01.png)
  - spr_taina_dash_or_step_in -> v001 (/res/sprites/characters/taina/taina_dash_or_step_in_64x64_v01.png)
  - spr_taina_jump_rise_fall_landing -> v001 (/res/sprites/characters/taina/taina_jump_rise_fall_landing_48x64_v01.png)
  - spr_taina_combo_hit_1_jab -> v001 (/res/sprites/characters/taina/taina_combo_hit_1_jab_runtime_unique_64x64_v02.png)
- ROM: build_v003 (sha256 e1fc0dd5180ffb09f74087248f1d4d363ace93b5c1a74f0e307c1b8f3e05c1c6, 262144 bytes)
- Notes: Idle, andar, correr, pulo e jab buildados e observados sobre o primeiro recorte modular do CAIS_01; evidencia formal ainda bloqueada por VLAB, VDP dump e metricas runtime.

## 2026-07-29 - cais01_visual_density_runtime_v02

- Registrado o feedback humano de que a prova funcional permanecia abaixo do
  benchmark comercial em paleta, detalhe, profundidade e iluminação.
- Criado `tools/art/build_cais01_visual_pass_v02.py`, partindo do kit autoral
  aprovado. O passe produz BG_B 512×224, BG_A 320×224, comparação v01/v02,
  sombra de contato e contratos de paleta/scroll/budget.
- Integrados `HSCROLL_TILE` por 28 linhas, quatro bandas de profundidade,
  palette cycling do lampião em PAL2 e sombra de contato de três estados.
  H-Int e Shadow/Highlight permanecem desativados.
- ResComp: BG_B 249 tiles, BG_A 277; sombra com pico de 8 tiles e uma parte.
  Pior TAÍNA + sombra: 56 tiles e sete partes. Budget combinado com inimigos,
  HUD e FX segue pendente.
- Build Linux passou. ROM 262144 bytes, SHA-256
  `52856afcda732128e13012797a1acab7732ef56f85bdbe698c31742246efd70c`.
- BlastEm observou o passe na cena 3. Evidências em
  `out/evidence/cais01_visual_v02_hash52856/`.
- O selo formal continua bloqueado por VLAB, dump VDP e métricas runtime. A
  execução parcial do validator confirmou metodologia/higiene e `.res`, mas
  foi interrompida na agregação posterior e não é um pass completo.
- A TAÍNA não foi refinada a partir das sheets runtime. O brief v03 exige
  reseed direto da imagem 04 e aprovação de model sheet pixel antes de novas
  strips. Status:
  `buildado_runtime_observed_partial`, sem claim de arte final ou AAA.

## 2026-07-29 - cais01_signature_runtime_v03

- Criado `tools/art/build_cais01_signature_pass_v03.py`, preservando o kit
  autoral do cais como fonte e usando referências comerciais apenas para
  princípios técnicos, sem copiar arte.
- BG_A e BG_B agora cobrem 512×224. A cena ganhou cidade distante/próxima,
  contraste quase preto, sol ditherizado, reflexo quebrado na água, piso com
  óleo/pneus/rachaduras/pregos, stencil de carga, fumaça e poeira do lampião.
- Integrado `HSCROLL_LINE` com 224 linhas nos dois planos: céu 1/8, cidade
  distante 1/4, cidade próxima 1/2, água 1/4 mais onda e píer 1/1. Owner:
  `SCENE_demo`; sem H-Int; teardown e fallback documentados.
- Aplicada paleta runtime de contraluz à TAÍNA sem alterar sua geometria. O
  reseed de detalhe continua congelado na imagem 04/model sheet autoral.
- A primeira captura mostrou ruído na sombra checker v02. Criada
  `taina_ground_shadow_48x16_3f_v03.png`, com núcleo sólido e borda discreta;
  a segunda captura no BlastEm confirmou a correção.
- ResComp: BG_B 431 tiles, BG_A 384; cada fumaça 12 tiles/uma parte, cada
  poeira até 4 tiles/uma parte. Conjunto autorado atual no pior estado:
  88 tiles e 11 partes de sprite. DMA de line scroll: 896 bytes/quadro;
  teto conservador total: 4356 bytes, ainda sem instrumentação runtime.
- Build Linux passou. ROM 262144 bytes, SHA-256
  `9c2e3e9d82e4fa4ef678bd0a087ffd74a950bd5711ad4748c6a9278fc476ce4d`.
  Evidência visual em
  `out/evidence/cais01_signature_v03_hash9c2e3e/`.
- O selo formal permanece bloqueado por falta de VLAB, dump VDP, métricas de
  runtime e orçamento com inimigos/HUD/hit FX. Status:
  `buildado_runtime_observed_partial`, sem claim de AAA ou arte final.

## 2026-07-29 - cais01_art_alignment_runtime_v04

- Registrado o aprendizado de que efeitos técnicos não compensam uma
  macrocomposição genérica. Criados matriz de fontes, gate conjunto de arte e
  gameplay, scene direction record, depth role map, composition schema e layer
  plan da v04.
- Criado `tools/art/build_cais01_art_alignment_pass_v04.py`. O builder
  reconstrói em grid nativo as nuvens horizontais, a massa industrial
  compacta, o sol ditherizado, o grupo de caixas, o poste/rede e a madeira
  irregular a partir das fontes autorais mapeadas.
- Promovidos:
  `res/backgrounds/cais01/cais01_bg_b_harbor_sunset_512x224_v04.png` e
  `res/backgrounds/cais01/cais01_bg_a_industrial_pier_512x224_v04.png`.
  Os recursos mantêm PAL0/PAL2 e os IDs SGDK anteriores.
- A primeira observação v04 encontrou corda e óleo tangenciando a personagem;
  o passe final deslocou ambos e preservou uma área limpa em torno da TAÍNA.
  Nenhum sprite de personagem foi redesenhado nesta entrega.
- Pixel strict passou. ResComp 3.95 mediu BG_B 484 tiles e BG_A 385 tiles,
  total de 869/27808 bytes. O budget é `cabe com recuo`: restam 79 tiles no
  envelope atual; o mundo de 1344px continua dependente de streaming.
- Build Linux pela rota selecionada passou. ROM: 262144 bytes, SHA-256
  `825e687c8f0513f2d2d9f634f980be83426a2b84a457b0ddef6978271bfba429`.
- O BlastEm exibiu a cena 3 a 61,1 fps na janela. Screenshot, GIF, SRAM e ROM
  selada estão em
  `out/evidence/cais01_art_alignment_v04_hash825e687/blastem-linux-20260729T203545Z-1153418/`.
  Comparação visual:
  `doc/art/environments/cais01/review/cais01_runtime_compare_v03_v04.png`.
- Evidência formal rejeitada por falta de VLAB, dump VDP e métricas runtime.
  Estado: `buildado_runtime_observed_partial`; sem promoção para arte final,
  `validado_budget`, `testado_em_emulador` ou AAA.
- O validator central passou metodologia, higiene e leitura do `.res`, mas não
  concluiu a agregação em mais de dois minutos e foi interrompido; portanto não
  há `validation_report.json` completo. O freshness audit registra warning por
  artefatos obrigatórios ausentes/stale, coerente com o status parcial.

## 2026-08-29 — selo append-only de reconciliação atual

- **ROM vigente:** `e07fa63b6aa6e7bec542814950eb9190f7a5e04732da362c27f01b84398dfd5e`
  (`out/rom.bin`, 262144 bytes). As entradas acima e abaixo desta data que
  citam outros hashes permanecem históricas/supersedidas.
- Fonte autoral da TAÍNA aprovada somente para tradução pixel; AAA, slice e
  arte final continuam bloqueados por `doc/aaa_pipeline_gate_report.json`.
- Frescor atual: `out/logs/freshness_audit_report.json` em `warning`, com
  `validation_report.json` e `build_output.log` ainda ausentes; não há claim
  de validação integral.

## 2026-08-29 — contrato de tradução nativa da TAÍNA

- Criado `doc/contracts/visual_source_of_truth_taina_v02.json`: a prancha
  autoral aprovada é a única origem permitida; sprites runtime e linearts
  reprovadas são explicitamente `obsolete_for_generation_source`.
- Criados o gate de direção `art_gameplay_direction_gate_reseed_v02.json` e
  o contrato de tradução 48×64. Eles autorizam exclusivamente a próxima
  lineart 1 px, mantendo color blocking, poses, strips e `res/` bloqueados.
- Estado: `visual_first_ready_for_translation`; não há novo PNG nem mudança
  da ROM nesta etapa.

## 2026-08-29 — candidata de lineart rejeitada antes de promoção

- A geração nativa produziu
  `data/source_art/concept/taina_pixel_model_sheet/rejected/taina_reseed_native_lineart_candidate_imagegen_v01.png`
  (SHA-256 `4de4b9beaa48b1b1959ee738dbb9afd9cdd08f5587e31ce09ddadf78f55ad736`).
- Ela preserva alguns marcadores de identidade, mas é RGB 1086×1448, sem
  célula 48×64, grid 8×8 ou lineart nativa. A revisão a marcou
  `rejected_not_generation_source`; foi preservada como evidência negativa,
  não entrou em `res/` e não altera a ROM.

## 2026-08-29 — gate físico de lineart nativa: três rotas sem promoção

- A rota A histórica segue rejeitada. A rota B tentou autoria manual no GIMP
  3.2.4 local; a aplicação encerrou na inicialização de plugins sem expor uma
  janela de editor, portanto não produziu arquivo.
- A rota C usou apenas a prancha autoral aprovada, em geração isolada. Os dois
  resultados foram selados em `data/source_art/concept/taina_pixel_model_sheet/rejected/`:
  ambos são 1086×1448, um RGB e outro RGBA. Não são 48×64 indexados, não têm
  prova de grid 8×8 e foram rebaixados para `rejected_not_generation_source`.
- `doc/art/characters/taina/taina_reseed_native_lineart_gate_attempts_v01.json`
  registra os três resultados. Nenhuma imagem rejeitada será reduzida,
  quantizada, traçada ou usada como entrada. O bloqueio agora é específico:
  falta uma autoria externa/interativa que entregue PNG 48×64 indexado nativo
  a partir da prancha aprovada e do contrato de tradução.

## 2026-08-30 — Visual Forge e reconciliacao da rota artistica

- Registrado `doc/contracts/visual_toolchain_reconciliation_v01.json` como
  reconciliacao operacional. Ele corrige o entendimento sem apagar o historico:
  as tres imagens 1086x1448 sao referencias de construcao aprovadas pelo owner,
  mas continuam proibidas para promocao direta.
- Registrado `doc/23-visual-forge-adoption-plan.md`, com gates sequenciais para
  ferramenta, TAÍNA, segundo personagem, CAIS, FX/HUD/audio, budget e ROM.
- O plano compartilhado completo foi persistido em
  `../../doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md`
  e o prompt executavel em
  `../../doc/prompts_modelo/prompt_mestre_visual_forge_e_mare_brava_aaa.md`.
- Estado mais novo do GIMP: funcional, mas automacao de ponteiro sem precisao
  suficiente; ele passa a ser frontend opcional, nunca dependencia do core.
- Conversao automatica fica autorizada apenas para gerar `basic_control` ou
  normalizar arte adequada. TAÍNA final continua exigindo reconstrucao 48x64
  no grid nativo, fidelidade, aprovacao, budget e evidencia.
- Nenhum asset foi promovido, nenhum build foi executado e nenhuma ROM mudou.
  Status: `approved_plan_pending_implementation`; `ready_for_aaa=false`.
- Validacao do registro: project context `ok`, metodologia `passed` e higiene
  `passed`. `validate_visual_source_of_truth.ps1` continuou bloqueado por
  `visual_lineage_scan_read_failed` ao ler JSONs profundos; o prompt exige
  corrigir o parser com regressao positiva/negativa, sem culpar ou alterar arte.

## 2026-08-30 — Convert revalidado e lineage v02 concluído

- `forge-art convert` passou a rederivar e verificar o `conversion_report`
  publicado, além dos hashes genéricos do job. A fixture
  `rejects_resealed_invalid_conversion_report` remove `metrics`, resela o job
  e prova rejeição fechada por `cached_conversion_report_invalid`.
- A matriz de rotas passou a limitar concept/render a
  `basic_technical_control`; `mechanical_asset_conversion` exige raster
  autoral/nativo. Nenhuma rota automática pode chamar uma prancha de personagem
  de final.
- O gate de fonte visual recebeu regressões para JSON profundo, escalares,
  referências proibidas e seleção v01/v02. A execução explícita com v02
  concluiu em tempo finito, `status=passed`, 141 arquivos e sem overflow.
- Foi gerado o BASIC técnico imutável `4ceca437f5dc5b2c` apenas para
  comparação; não alterou `res/`. A tentativa raster de lineart v02 falhou a
  exigência de grid nativo e foi registrada como evidência negativa, sem
  conversão para ELITE, animação ou promoção.

## 2026-08-30 — curadoria CLI-first e persistência causal

- Criado `workflows/causal-persistence-loop.md`: blocker folha, hipótese
  verificável, medição, mudança obrigatória de rota após repetição e parada
  apenas por blocker crítico comprovado.
- `art-conversion-pipeline` passou a classificar GUI automatizada em operação
  determinística como `interaction_channel_mismatch`.
- Adicionado `forge_art.gimp_batch` e o comando
  `gimp-batch-preflight`. O adaptador usa processo sem shell, perfil XDG
  isolado, timeout com encerramento do grupo de processos, schema fechado e
  rejeição de operação/script arbitrário.
- Preflight local: GIMP 3.2.4, `python-fu-eval`, sentinel observado, exit 0.
  Nenhuma operação GIMP de produção foi registrada; GIMP não virou oráculo de
  cor nem dependência do `convert`.
- `forge-art self-check`: 107/107. O teto continua técnico; nenhum asset visual
  foi aprovado ou promovido.
- Reconciliados o contrato de toolchain e o relatório histórico de tentativas
  da TAÍNA. O histórico permanece, mas automação de ponteiro foi encerrada.
- Nenhuma mudança em `res/`, build ou ROM. `ready_for_aaa=false`.

## 2026-08-30 — TAÍNA native lineart: representação trocada e rota medida

- Corrigida a classificação do gate para `taina_native_48x64_lineart_representation_mismatch`; a direção humana já aprovada não bloqueia autoria da lineart.
- Registradas as tentativas D/E/F em `taina_reseed_native_lineart_gate_attempts_v01.json`: três mapas author-stamp 1:1 em grade 6×8, sempre nascidos do model sheet aprovado e sem reutilização de candidatos negativos.
- O PNG F `taina_reseed_native_lineart_48x64_v03.png` passou `forge_art.pixel_contract` sem blockers: 48×64, indexed color type 3, 4bpp, index 0 transparente, PLTE 16, 1 cor visível e grid 9-bit; `--self-check` 19/19.
- A inspeção visual ainda encontrou `lineart_blocking_visual_pass_pending`, `face_or_eye_readability_lost` e `generic_blocky_redraw`. Basic/elite e `res/` permanecem bloqueados por qualidade visual; o blocker humano continua restrito à licença/fonte de BGM/SFX.

## 2026-08-30 — TAÍNA: candidato editor nativo e fonte reconciliada

- A referência v02 foi movida para `construction_reference/` sem alteração de
  conteúdo (SHA256 `70ea460cca819084cda5f2b439f3068afba8731e026fe52dbd56aee95276edc1`).
  Continua rejeitada como sprite nativo e aprovada apenas como referência de
  construção; a trilha está em `doc/history/taina_visual_source_reconciliation_2026-08-30.json`.
- Criados `native_sprite_production_record.json` e
  `tools/sgdk_wrapper/validate_native_sprite_production.py`. O candidato
  editor 48×64 indexado tem SHA256
  `9d6cd24ac58a0fdd50bb65ee200af01befb5fce35feabdffd6335c5b81b0daa3` e
  passou o contrato técnico de pixels.
- A prancha `out/evidence/taina_native_lineart_editor_v01/` registra o gate
  visual pendente/rework. Não houve promoção para `res/`, BASIC/ELITE,
  integração SGDK, ROM ou claim AAA.
- Fechamento técnico: `forge-art self-check` 107/107, suíte de arte
  116/116, registro nativo/contexto/higiene/metodologia válidos e
  `git diff --check` limpo.
- A execução seguinte do mesmo spec teve `cache_hit=true`, manteve o job
  `22db1183a4d6a166`, os hashes publicados e o selo de estado, provando a
  revalidação de resume/cache sem alterar `data/` ou `res/`.
## 2026-08-30 — recuperacao de conhecimento + hardening do validador nativo

- Reancorado `rascunho/taina_visual_challenger_exercise_v01/exercise_record.json`
  como `methodology_reference` (nunca fonte de pixels). O exercicio registra que
  48x64 perde rosto/maos/pes/presenca e 64x96 preserva identidade, com proxima
  acao = scale gate formal. A recaida veio de ignorar essa conclusao e produzir
  direto em 48x64 sem a escada visual.
- Fechada a rota `binary_pointer_editor_as_primary_visual_producer`: editor nativo
  e QA/correcao, nao produtor primario. A candidata
  `taina_reseed_native_lineart_editor_candidate_v01` ficou `technical_pass_visual_fail`.
- `validate_native_sprite_production.py` endurecido: CLI documentada, resolucao
  segura de paths, re-derivacao do pixel contract + medicao do disco, 4 evidencias
  distintas, proveniencia, gates independentes, incumbent/reference com hash.
  Schema 1.1.0. Guardian consome veredito. Reprova os falsos verdes (proveniencia,
  mesmo painel, scale sem report, palette_lock em lineart binaria, native_1x != candidato).
- `ready_for_aaa=false`, `res/` intacto. Proxima acao: scale gate 48x64 vs 64x96.

## 2026-08-31 — probes de escala 48x64 vs 64x96 + validador semantico v2.1

- `validate_native_sprite_production.py` v2.1: mede filled_pixels excluindo transparencia
  (candidata antiga = 198 px visiveis, nao 3072), re-deriva pixel contract + content_sha256
  do disco, exige 4 evidencias distintas e determinadas, valida schema Draft 2020-12,
  fecha proveniencia, mantem gates independentes. Fixtures 16/16.
- Probes gerados por autoria nativa deterministica (sem canal de geracao no host):
  48x64 (796 px, 25.91%, 30 tiles unicos, 4 sprites VDP) e 64x96 (1396 px, 22.72%,
  49 tiles unicos, 6 sprites VDP). Ambos technical_candidate nao-promotable.
- Comparacao: 64x96 preserva 1.75x mais pixels visiveis e 1.63x mais massa de tiles.
  Escala permanece gate humano apos camera real + budget completo.
- Estados: status=pending_scale_probe_generation, visual_pass=false, ready_for_aaa=false,
  res/ nao alterado. `native_sprite_production_record.json` passa no validador semantico.

## 2026-08-31 — correcao de falso verde dos probes e schema 1.2.0

- Corrigida a classificacao dos probes: sao `photo_or_render_derived` produzidos por
  `mechanical_scale_probe`, nao autoria nativa nem `assisted_native_translation`.
- `validate_native_sprite_production.py` v2.2 usa somente o executor completo Draft 2020-12
  (`jsonschema` preparado em `out/host_tools`) e falha fechado se a dependencia estiver
  ausente. O fallback parcial `schema_gate` deixou de sustentar este contrato.
- O shape block passou a ser obrigatorio sempre que existe candidata e seus tres papeis
  precisam apontar para artefatos distintos na grade nativa. Nova fixture adversarial:
  `rejects_reused_shape_block_artifact`; suite do gate = 17/17.
- O schema foi elevado a `1.2.0`. `gates.scale` foi normalizado para `in_progress` e o gate
  humano para `not_started`, pois a decisao humana so abre apos comparacao e budget reais.
- Consequencia honesta: o registro atual da TAINA falha fechado nos tres artefatos high-res
  de shape block e na reutilizacao da mascara. Os probes continuam controles tecnicos
  nao-promoviveis; nenhum pixel foi alterado em `res/` e nenhum claim visual/AAA foi aberto.

## 2026-08-31 — pacote visual TAINA v02 e hardening semântico v2.3

- Gerados e persistidos quatro challengers via `native_chat_image_generation_callable`,
  usando exclusivamente o model sheet aprovado: dois em 48x64 e dois em 64x96.
  Cada candidato recebeu PNG nativo de revisão, evidências 1x/nearest 8x/light/dark
  e shape block nativo com silhueta, mapa semântico e overlay distintos.
- `validate_native_sprite_production.py` v2.3 agora rederiva `producer_output` do PNG,
  valida `pixel_compliance_report.schema.json`, exige legendas/contagens semânticas
  reais, hashes individuais e links de asset/escala/fonte. A suíte adversarial permanente
  passou em 22/22.
- Painel comparativo e budget medido: 48x64 A é a recomendação preliminar; 64x96 A
  preserva mais detalhe, mas o cenário hero + quatro inimigos mede 22 links/linha e
  estoura o limite H40 de 20. Nenhuma decisão humana foi simulada.
- Registro TAINA atualizado para `technical_candidate`, `promotable=false`; gates
  visual/escala/budget/humano continuam abertos. `res/` não foi tocado e não há claim
  `visual_pass`, `ready_for_res`, ROM ou AAA.

## 2026-08-31 — curadoria corretiva de matte, semantica e budget

- Substituido o recorte por threshold global por matte deterministico conectado
  as bordas, com report e falha fechada; caminho nativo passou a usar NEAREST.
- `pixel_contract` v1.2 bloqueia aliases de indices com o mesmo RGB apos snap.
- Schema nativo v1.3 e `validate_native_sprite_production` v2.4 exigem matte
  report em traducao assistida, conferem silhueta, uniao semantica, area minima
  dos rotulos e contorno derivado; fixtures 28/28.
- `vdp_scanline_simulator` v1.2 mede celulas <=32x32 por faixa Y. O overflow
  64x96 anterior foi invalidado e o gate de escala reaberto.
- Painel deixou de usar LANCZOS nos candidatos, de chamar footprint de hitbox e
  de emitir scores/recomendacao nao medidos. Assembler agora exige selecao
  explicita por `--selected-asset-id`.
- `res/` nao foi alterado; pacote v02 permanece retrabalho, sem visual/AAA claim.
## 2026-08-31 — pacote visual TAINA v03 e gate humano reaberto

- Regenerado `rascunho/taina_visual_challengers_v03/` com matte conectado às
  bordas, NEAREST, quatro candidatos 48x64/64x96, evidências 1x/8x/light/dark/
  chroma e shape block nativo. v02 foi preservado como comparação/evidência
  negativa e `res/` não foi tocado.
- Produzida anotação semântica anatômica por candidato, substituindo o mapa de
  pré-triagem geométrico. A auditoria `v03_package_validation_report.json`
  passou 4/4; o record nativo usa provisoriamente `taina_48x64_challenger_b`,
  mas continua `technical_candidate`/`promotable=false`.
- Budget rederivado por `vdp_scanline_simulator` 1.2.0:
  48x64 = 20 links totais, 10/scanline, 248 px no caso TAÍNA + 4 inimigos;
  64x96 = 22, 10/scanline, 264 px. O próximo degrau 3 CRIA + 3 ESTIVADOR
  mede 348/364 px e estoura o eixo de pixels. O resultado histórico 20/22
  links por linha foi descartado.
- Painel `taina_visual_comparison_panel_v03.png` não contém scores estéticos
  nem vencedor automático. B é somente `human_preference_prior`. A decisão
  humana deve citar asset_id e SHA-256: A48
  `20e9c3b8cdb3d8620954b016131e1338b71087924518b24b1bebf9eed372e5dc`, B48
  `d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa`, A64
  `a7af68da88e977f2160a3304628be3cadc3bc5d71a8a6cea4b37ff119ffc314e`, B64
  `8b8b334e66094fb9db6b135c35e72b152279b2089f57a593f4713809f6aca200`.
- Checks finais: forge-art 111/111, art pipeline 116/116, semantic gate 28/28,
  VDP self-check aprovado, measurement audit 1/1 e
  `validate_native_sprite_production.py --shape-block-contract` sem erros.
  Human gate permanece `not_started`; animação, SGDK, ROM e BlastEm aguardam a
  decisão vinculada ao hash.

## 2026-08-31 — decisão humana B e refinamento nativo BASIC/ELITE

- Persistida a decisão `approved_for_native_refinement_only` para
  `taina_48x64_challenger_b`, escala 48x64, SHA-256
  `d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa`.
- Geradas duas variantes de refinamento nativo fora de `res/`: BASIC com 9 cores,
  SHA-256 `e78f77d92614eb0ec2c7a0ec529d7649db025a0a793b93f3b749323708a7b403`, e
  ELITE com 11 cores, SHA-256
  `0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13`.
- Ambas passaram forge-art P/4bpp, índice 0 transparente, alpha binário, dimensão
  48x64, até 15 cores e preservação pixel a pixel da silhueta B. A auditoria do
  pacote e o relatório VDP passaram; não há vencedor automático.
- Record atualizado para `native_authoring`/`promotable=false`. A decisão não autoriza
  `res/`, animação final, ROM ou claim AAA. Próximo gate: decisão visual humana sobre
  BASIC ou ELITE refinado.

## 2026-08-31 — reconciliação documental v03 e gate BASIC/ELITE

- Manifest v03 corrigido: model sheet aprovado separado como `identity_source`; quatro
  producer outputs persistidos do v02 registrados como `translation_input_sources` com
  hashes; anotação renomeada para `agent_curated_diagnostic_annotation`.
- Budget pass limitado ao caso estático TAINA + quatro inimigos; 3+3 retido somente como
  medição de ambição. 48x64 travado para o slice e 64x96 marcado como comparison_only.
- Painel v03 regenerado com renderização correta de `TAÍNA`.
- Gate BASIC/ELITE persistido fora de `res/`: BASIC SHA-256
  `e78f77d92614eb0ec2c7a0ec529d7649db025a0a793b93f3b749323708a7b403`; ELITE SHA-256
  `0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13`.
- Validações finais: forge-art 111/111, art pipeline 116/116, semantic fixtures 28/28,
  pacote v03 4/4, refinamento 2/2, VDP self-check, measurement audit e record semântico
  sem erros. Nenhum vencedor automático; animação, `res/`, ROM e AAA continuam bloqueados.

## 2026-08-31 — fechamento do pacote BASIC/ELITE

- Manifests corrigidos para paths relativos ao workspace; cada variant recebeu palette
  role map, matte report e shape block materializado. Os bytes e SHA-256 permaneceram
  estáveis.
- Painéis regenerados com `TAÍNA` corretamente renderizado. Tentativa ImageGen com
  checkerboard/proporção divergente e primeira serialização P/8bpp foram descartadas;
  nenhuma entrou como asset final.
- Checks finais: forge-art 111/111, art pipeline 116/116, semantic gate 28/28, pacote
  v03 4/4, refinamento 2/2, VDP self-check, measurement audit, proveniência e record
  sem erros. Teto permanece native_authoring; aguardando escolha humana BASIC/ELITE.

## 2026-08-31 — rejeição humana do refinamento nativo

- Registrada a decisão `rejected_for_final_native_pose` para BASIC e ELITE, vinculada
  aos SHA-256 exatos no registro de rejeição. Motivo: limpeza procedural de paleta sem
  refinamento geométrico nativo por material.
- ELITE permanece preservado como melhor controle técnico, sem aprovação final. O
  record foi movido para `rework`, com gates visual/humano falhos e promoção bloqueada.
- 48x64 continua travado; 64x96 continua `comparison_only`. `res/`, animação,
  integração, ROM/BlastEm e claims finais permanecem bloqueados. Próximo gate:
  formular uma nova hipótese geométrica nativa antes de gerar candidatos.

## 2026-08-31 — três challengers de geometria nativa

- Gate de escala corrigido para `passed` sem alterar os demais gates. Produzidas as
  rotas independentes A `FACE_AND_GUARD_TOPOLOGY`, B `SILHOUETTE_AND_WEIGHT` e C
  `INTEGRATED_NATIVE_REDRAW`, sempre a partir do model sheet aprovado.
- Tradução nativa assistida refeita com matte conectado, NEAREST e rampas fixas por
  material. A primeira versão global de palette mapping foi descartada por colapsar
  pele/cabelo/índigo em 1x; a falha e os hashes observados ficaram no manifest.
- Candidatos, shape blocks, palette role maps, matte reports, evidências e budget foram
  persistidos em staging. Preflight passou para os três; não há score nem vencedor
  automático. `data/` e `res/` permaneceram inalterados.
- Status do pacote: `pending_human_decision`; promoção para `res/`, animação, ROM e
  claims AAA continuam proibidas.

## 2026-08-31 — fonte A aprovada para nova autoria nativa

- Registrada a decisão humana `approved_as_visual_source_for_native_authoring` para
  `face_and_guard_topology_visual_source_v01`, SHA-256
  `b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf`, alvo 48x64.
- O candidato nativo A, SHA-256
  `1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830`, permanece
  somente controle técnico; a decisão não autoriza pose final, `res/` ou animação.

## 2026-08-31 — rejeição visual G2, linhagem corrigida e escala reaberta

- Registrada a rejeição humana exata de `taina_48x64_native_g2_volume_identity_v01`,
  SHA-256 `e35ad9f4477d7d1912b94505932a547e639cdea8b8085e2062362db3f21dcb30`, com
  `technical_pass_visual_fail`, `source_detail_lost`, `generic_blocky_redraw` e
  `identity_hooks_lost`. O pacote permanece como evidência negativa somente.
- Corrigida a linhagem: Source A `b2400128...` agora é `ai_generated_high_res` /
  `visual_source_for_native_authoring`; o model sheet v02 `324951fb...` é a fonte
  exclusiva das decisões de pixel. A saída do builder é `procedural_primitive` /
  `visual_lab_control`, e seus mapas são `agent_curated_diagnostic_annotation` de
  consistência interna, não prova independente.
- Registrado `scale_gate_reopened_by_human_review=true`; hitbox segue não declarado,
  então o gate de escala está em andamento. O orçamento corrigido mantém 48x64 como
  incumbent e 64x96 como comparação até autoria independente.
- Não foram criados challengers novos: este host não possui editor nativo de pixels e
  as rotas GIMP pointer/batch e rasterização procedural estão proibidas. O bloqueio e a
  próxima ação estão em `doc/art/characters/taina/native_authoring_blocker_v01.json`.
  `res/`, animação e integração permanecem inalterados/bloqueados.
- Próxima etapa: nova autoria nativa com revisão humana posterior, mantendo 64x96 como
  `comparison_only` e sem alterar `data/` ou `res/`.

## 2026-08-31 — autoria nativa A v03 em gate humano

- A decisão humana foi registrada como aprovação da fonte visual A para nova autoria
  nativa, não como aprovação do PNG candidato A. O candidato
  `taina_48x64_geometry_face_guard_v01`, SHA-256
  `1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830`, segue somente
  como controle técnico.
- A tentativa v02 foi descartada por compressão observável do rosto em 1x. A nova
  candidata `taina_48x64_native_authoring_face_guard_v03` foi produzida a partir de
  saída visual nova derivada da fonte aprovada; SHA-256
  `e3a35e5fad1a77c3931a0b3e0cf30e1f877b25e8fcf3d3ac87b5ca1d4a3f4d33`.
- Preflight passou: P/4bpp, índice 0 transparente, alpha binário, 48x64, 12 cores,
  shape block, matte, evidências e budget. O pacote permanece em staging, sem `res/`,
  animação, integração SGDK, ROM/BlastEm ou claim final.

## 2026-08-31 — autoria nativa headless A1/A2

- A/B/C foram corrigidos para `technical_candidate/mechanical_translation_probe`; o
  semantic gate antigo não é atribuído a esses probes e seus mapas são somente
  `diagnostic_coordinate_annotations`.
- A1 foi produzida por patch explícito para face/guarda/pés: SHA-256
  `1033e5a387047c320b9f2bbf6b0bddaafb2d29fd9b74810a40af8001c0947794`; A2 foi produzida
  por patch explícito para peso/faixa: SHA-256
  `041e6fd184bdff499f110075245be570f1597d9085689f7657ca2c55ed878ae0`.
- Ambos têm records temporários separados, semantic maps autorais com cobertura exata,
  pixel reports, evidências e budget vinculados ao mesmo SHA. Validator nativo passou
  para A1 e A2. Nenhuma variante foi aprovada visualmente ou promovida para `res/`.

## 2026-08-31 — gate de topologia de materiais

- Feedback humano classificou como blocker o vazamento da rampa laranja do crop top
  para barriga e braços em A1, A2 e PROBE A. A1 é apenas controle e base autorizada
  para o patch explícito de rework; não é fonte de identidade/geração nem pose final.
- Registrado
  `doc/art/characters/taina/taina_material_topology_correction_request_v01.json` com
  fonte/hash, severidade por região, diagnóstico causal, ordem de patch, materiais,
  fronteiras críticas, artefatos obrigatórios e teto de claim.
- Pipeline canônico evoluído de forma backward-compatible: records novos 1.4.0 podem
  declarar `material_region_contract` e gate `material_topology`; o validator mede
  cobertura, índices por material, exclusividade de rampas, overlay e contatos de
  fronteira. Records 1.3.0 continuam aceitos como legado.
- Próxima produção autorizada é apenas um challenger material-clean baseado em A1,
  staging-only. Regeneração integral, animação, `res/`, ROM e claim AAA permanecem
  bloqueados até revisão humana do novo SHA-256.

## 2026-08-31 — TAINA material-clean native rework

- Aplicado patch nativo literal sobre A1, vinculado à Source A aprovada e ao SHA da base; nenhum pixel foi gerado por ImageGen, primitiva, interpolação ou segmentação automática.
- Nova candidata: `taina_48x64_native_a1_material_clean_v01`, SHA-256 `54df9fd341ad57bdc2c02c62db6366119c7d511ba8e14862666cf487366b2567`; patch SHA-256 `6bdeaba407613f675712ff5c23a1404a229125552533cfe84a494a5dbd959bfe`.
- Corrigidos hem/abdômen e braços por propriedade material: 43 pixels antigos da rampa laranja deixaram de ser laranja (7 para outline do hem, 14 para pele no abdômen, 22 para pele nos braços); 20 pixels teal e 7 pixels índigo da ROI abdominal foram reatribuídos para pele/outline.
- Record 1.4.0 e `material_region_contract` persistidos com mapa completo, overlay rederivado, quatro ROIs críticas e leakage report. Primeiro overlay incorreto incluía transparência; corrigido e revalidado.
- Evidências e painel em `rascunho/taina_native_material_clean_rework_v01/`; `res/` e `data/` inalterados. Status do pacote: `pending_human_decision`; nenhum vencedor ou promoção automática.
- Checks: 111/111 forge-art; 116/116 art pipeline; 36/36 semantic fixtures; record sem erros; pixel/material/proveniência OK; budget específico 20 links/10 sprites/248 px, 3+3 comparison-only em 348 px. Auditoria global de tile residency continua bloqueada por baseline preexistente 2117/1740 e não foi usada para promover a candidata.

## 2026-08-31 — rejeição de refinamento e G2 geométrico nativo

- Registrada a rejeição humana de BASIC e ELITE refinados pelos SHA-256 exatos e pelo
  motivo `procedural_palette_cleanup_without_material_native_geometry_refinement`.
  ELITE foi preservado como `technical_control_only`; A1 material-clean como
  `material_topology_control_only`.
- Produzida em staging a nova candidata `taina_48x64_native_g2_volume_identity_v01`,
  SHA-256 `e35ad9f4477d7d1912b94505932a547e639cdea8b8085e2062362db3f21dcb30`, por
  raster nativo explícito a partir da Source A aprovada. 48x64 permanece locked;
  64x96 permanece comparison-only.
- Persistidos shape block, geometria/proporções, máscara delta, semântica, contour,
  topologia de materiais, leakage, palette role map, evidências e painel comparativo.
  `validate_native_sprite_production --shape-block-contract` passou sem erros.
- Medição: P/4bpp, PLTE 16, índice 0 transparente, 15 cores visíveis, 48 tiles/37
  únicos; TAÍNA + quatro inimigos em H40 = 20 links, 10 sprites e 248 px/scanline.
  3+3 = 348 px/scanline, comparação somente e fora do `budget_pass`.
- Sem alteração em `res/`, sem animação, sem integração SGDK, sem ROM/BlastEm e sem
  claim `visual_pass`/AAA. Estado do pacote: `pending_human_decision`.

## 2026-08-31 — decisão humana 56x80 e autoria nativa em staging

- A decisão humana aprovou exclusivamente `taina_idle_guard_56x80_visual_source_v01`,
  SHA-256 `32c5a8089c52251c0276eb0c28406b44e7797455a767b4a498c1da74be094d4f`, para
  produzir uma única pose idle/guard nativa 56x80 em staging. Não é aprovação de
  pixel final, `res/`, animação, ROM, `visual_pass` ou AAA.
- O shootout persistido contém fontes independentes 48x64
  `331ef5f4d0a16d8dee525229333c558fc0954c07b49a7ef2d7c46d606aa51301`, 56x80
  `32c5a8089c52251c0276eb0c28406b44e7797455a767b4a498c1da74be094d4f` e 64x96
  `b16e0cbebd5c4595ec875384476a8622cdafc5d3265160bdb71780265d613e8d`. Elas mudam
  pose, anatomia e acabamento; são hipóteses direcionais, não comparação isolada de
  escala. Nenhum pixel de G2, A1, A2, BASIC, ELITE ou challenger B foi reutilizado.
- `native_scale_shootout_record_v01.json` tornou-se o record operacional; o antigo
  `native_sprite_production_record.json` foi marcado `historical_superseded`.
  Requests 56x80 e 64x96 foram corrigidos para remover o texto hardcoded `sprite 48x64`.
- O budget foi refeito como `planning_budget` com footprints reais declarados no
  slice: TAÍNA 56x80, CRIA 48x64 e ESTIVADOR 56x64. A medição corrigida registra
  TAÍNA + quatro CRIAs = 22 links, 10 sprites/scanline e 248 pixels/scanline;
  TAÍNA + 2 CRIAs + 2 ESTIVADORES = 22 links, 10 sprites e 264 pixels/scanline;
  próximo stress 3 CRIAs + 3 ESTIVADORES = 30 links, 14 sprites e 368
  pixels/scanline, acima do limite H40 de 320. O fixture anterior com inimigos
  32x48 não foi usado. Sem sprite nativo integrado e ROM, nenhum resultado é
  `validado_budget`.
- A autoria nativa 56x80 está autorizada apenas em staging. 64x96 só pode ser
  fallback após duas iterações causais 56x80 falharem; 48x64 não é reaberto nesta rodada.

## 2026-08-31 — budget corrigido e blocker nativo reproduzido

- A tentativa de autoria nativa 56x80 foi efetivamente exercitada em duas rotas
  causais. A primeira devolveu checkerboard assado; a segunda devolveu uma fonte
  visual RGB de alta resolução, visualmente séria, mas sem pixels nativos 56x80.
  O relatório reproduzível é
  `rascunho/taina_native_authoring_56x80_v01/native_authoring_failure_report_v01.json`.
- A tradução assistida apenas registrou handoff sem fabricar pixels; GIMP ficou
  restrito a preflight de capacidade batch sem operação de produção registrada e
  Aseprite não existe no host. O estado atual é blocker de autoria nativa após duas
  tentativas, não o blocker antigo sem tentativa.
- Corrigido o budget: 56x80 + quatro CRIAs 48x64 = 22 links, 10 sprites e 248
  pixels/scanline; composição 56x80 + 2 CRIAs + 2 ESTIVADORES = 22 links, 10
  sprites e 264 pixels/scanline; stress 3+3 = 30 links, 14 sprites e 368
  pixels/scanline. Tudo permanece `planning_budget`; o stress é comparison-only.
- Nenhum PNG nativo, evidência de candidato, `res/`, animação, ROM, `visual_pass`
  ou claim AAA foi produzido nesta etapa.

## 2026-08-31 — recuperação da autoria nativa 56x80

- O relatório de falha das duas rotas visuais anteriores foi marcado como histórico
  superseded. A rota segura `editor_api_save` foi executada no editor local com
  sessão 56x80, ações explícitas, restore, export PNG/log e guards de path. Self-check
  reproduzível: 11/11.
- Iterações nativas causais persistidas: v01 `7bfd7f57ec51f4a368917e7fc6e4655640ebae8cf4209ece219de14b3922aba8`,
  v02 `23e1d3704797ba3c48306268d6e18f00dd4b3a3cfc870927ca40edfadbb6d404`, v03
  `2430a61f6f3c40b6cd26ed212215bc035f1bd76dffa9b2343316fa0eb7babc0c` e v04
  `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`.
- v04 possui PNG P/4bpp 56x80, 15 cores visíveis, índice 0 transparente e evidências
  completas de pixel, shape, material, composição e comparação. A fonte de identidade
  é exclusivamente o model sheet v02; a fonte 56x80 aprovada é apenas direção/proporção.
- O record operacional agora é
  `doc/art/characters/taina/native_authoring_route_recovery_record_v01.json`, com
  `native_visual`/`human` em andamento e promoção falsa bloqueada. O estado legível
  da recuperação está em `native_authoring_route_recovery_state_v01.json`.
- O budget corrigido permanece `planning_budget`: 22 links/10 sprites/248 px para
  TAÍNA + quatro CRIAs; 22/10/264 na composição mista; 30/14/368 no stress 3+3,
  comparison-only. Não houve escrita em `res/`, animação, SGDK, ROM ou AAA.

## 2026-09-01 — rejeição humana da candidata nativa 56x80 v04

- Registrada a decisão `technical_pass_visual_fail` / `human_rejected` para
  `taina_idle_guard_56x80_native_authoring_v04`, SHA-256
  `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`.
- Razões: anatomia simplificada em bloco, perda de legibilidade de rosto/olho,
  perda de assinatura e redesenho genérico blocado.
- Decisão persistida em `doc/art/characters/taina/human_native_pose_rejection_v01.json`.
  A arte é preservada como `technical_control_only`; o record foi movido para
  `rework` e a promoção permanece falsa.
- Escala 56x80 continua travada, 64x96 continua comparação somente, sem
  reabertura de 48x64. Próximo gate é rework nativo causal em 56x80; animação,
  `res/`, ROM, `visual_pass` e AAA continuam não autorizados.

## 2026-09-01 — decisão humana exige laboratório de rotas

- Registrada a decisão exata `rejected_requires_route_lab` para
  `taina_idle_guard_56x80_native_authoring_v04`, SHA-256
  `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`, com os
  nove motivos anatômicos, de leitura, assinatura e similaridade observável.
- O novo registro é
  `doc/art/characters/taina/human_native_pose_route_lab_rejection_v01.json`;
  a decisão anterior permanece histórica. v01-v04 não podem alimentar uma nova
  geração, baseline ou img2img.
- Criado/ativado o laboratório isolado
  `SGDK_projects/_agent_laboratory/TAINA_RESAMPLING_ROUTE_LAB [VER.001] [SGDK 211] [GEN] [LAB] [ART_TRANSLATION]`.
  A produção normal está pausada até o gate humano do laboratório.
- A rota de produção foi corrigida para aguardar o gate de rotas; não foi criado
  v05 pelo método rejeitado e nenhum arquivo de `res/` foi alterado nesta etapa.
- O teto honesto passou a `resampling_route_lab_evidence`; 56x80 continua
  travado, 64x96 permanece `comparison_only`, e animação/ROM/visual_pass/AAA
  seguem bloqueados.

## 2026-09-01 — shootout de limpeza híbrida aprovado para staging

- Persistida a decisão `approve_hybrid_cleanup_shootout`, escala 56x80, com as
  bases Lanczos3, Mitchell-Netravali e Catmull-Rom vinculadas aos hashes exatos.
- Produzidas três variantes híbridas com pixels-base permitidos, matte binário,
  paleta semântica e patches nativos explícitos. O relatório separa validação
  técnica de escolha visual; não há vencedor automático.
- O próximo gate é seleção humana de uma candidata. `res_promotion=false`;
  produção normal, animação, runtime, ROM, `visual_pass` e AAA continuam
  pausados/bloqueados.

## 2026-09-01 — incumbent híbrido selecionado para rework localizado

- Persistida a seleção humana de `hybrid_cleanup_primary_im_lanczos3_v01`, SHA-256
  `3e60cd9efb233d0ce715c543e9cacdaacbe044b253c088dd06ada52f131b4cf1`, em
  56x80, com escopo `localized_native_cleanup_only`.
- Produzido `hybrid_cleanup_primary_im_lanczos3_rework_v01`, SHA-256
  `cb6ff5c695c5e7b76e80d84ebd497f8f55e162561c0f2caeb0f345604c31529e`.
  A limpeza é localizada e registrada por 27 patches nativos; a faixa de chão
  assada e o pixel órfão do sash foram removidos.
- O rework aguarda nova decisão humana. Não houve promoção para `res/`, animação,
  runtime, ROM, `visual_pass` ou AAA.

## 2026-09-01 — correção de método e rework artístico da PRIMARY

- Corrigido o rótulo para `mechanical_palette_remap_with_minimal_native_patches`,
  com `native_cleanup=incomplete`, `material_topology=not_run` e
  `semantic_map=derived_diagnostic_not_independent`. O mapa derivado do índice
  de paleta não é tratado como segmentação artística.
- A v02 foi descartada por regressão visual causada pelo remapeamento amplo; não
  é fonte nem baseline. A v03 foi refeita a partir do controle v01, sem
  regeneração integral, com 44 patches não nulos e evidência de linha 77 sem
  pixels na faixa central de chão.
- Candidata vigente: `hybrid_cleanup_primary_im_lanczos3_rework_v03`, SHA-256
  `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`.
  Contrato técnico passou, mas `technical_pass_visual_rework` permanece
  pendente de decisão humana. `res/`, animação, runtime, ROM, `visual_pass` e
  AAA continuam bloqueados.

## 2026-09-01 — v03 congelada como checkpoint; v04 em rework localizado

- Registrada a aprovação humana formal da v03 como checkpoint intermediário:
  `decision=approve_localized_native_cleanup`, asset
  `hybrid_cleanup_primary_im_lanczos3_rework_v03`, SHA-256
  `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`, escala
  56x80. A decisão não é `visual_pass`, pose final ou autorização de animação.
- Produzida a v04 sobre a v03, estritamente localizada, sem resize, filtro ou
  remapeamento global. SHA-256
  `791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e`; 36
  patches não nulos. O mapa material é independente da paleta, porém ainda
  aguarda revisão artística.
- Próximo gate separado: `approved_for_final_native_pose`. Permanecem falsas as
  promoções para `res/`, animação, runtime, ROM, `visual_pass` e AAA.

## 2026-09-01 — v04 preservada como incumbent; v05 em pending_human_decision

- Registrada a rejeição humana da v04 somente como pose final. A v05 foi gerada
  exclusivamente por clusters localizados sobre a v04, sem resize, filtro,
  nova quantização, remapeamento global ou regeneração integral.
- SHA-256 da candidata v05:
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`.
  Foram persistidos delta, mapas material/boundary independentes, palette role,
  evidências 1x/2x/3x/8x, silhueta, fundos, composição, crops, pixel, matte,
  provenance e topology reports.
- Estado: `technical_pass_visual_rework`, `native_cleanup=incomplete`,
  `material_topology=failed_requires_localized_material_cleanup`,
  `visual_pass=false`, `pending_human_decision`. `res/`, animação, SGDK, ROM e
  AAA permanecem intocados e não autorizados.

## 2026-09-01 — reparo do medidor de topologia, v05 congelada

- Mantida a v05 como incumbent diagnóstico, sem mudar pixels, gerar v06 ou
  alterar escala. SHA-256:
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`.
- Persistida a contabilidade exata: 23 patches tentados, 18 efetivos e 5
  no-op. A métrica não é usada como prova estética.
- Corrigida a topologia para mapa externo pixel-accurate, com fronteiras
  esperadas e fixtures adversariais permanentes. Fixtures: 8/8.
- Nova medição: v04 = ownership annotation error 4 / material palette leakage
  832; v05 = ownership annotation error 0 / material palette leakage 827.
  Topologia permanece `failed_requires_localized_material_cleanup` e o estado
  segue `pending_human_decision`.

## 2026-09-01 — blocking nativo 56x80 em staging, aguardando gate humano

- Registrada a rejeição humana dos challengers de reseed como controles
  diagnósticos, com `allowed_as_pixel_source=false`; não foram apagados nem
  promovidos.
- v01 e v02 do blocking foram tentadas e descartadas por falhas visuais
  observáveis: torso massudo e guarda lateral/ambígua. A v03 reconstrói a
  máscara estrutural na grade nativa, preservando 56x80 e o model sheet como
  autoridade de identidade. Os underlays Lanczos3/Mitchell são somente guias.
- A: `taina_56x80_native_lineart_blocking_a_v03`, SHA-256
  `cd911846f1eab6f05e59be714fdf0520a021ea88b9fdc008f2279112133c10ff`.
  B: `taina_56x80_native_lineart_blocking_b_v03`, SHA-256
  `2783c59c6c26e645825295d570c70d2a1ea01be1580fa02c306e35017e045264`.
  Diferença observável A/B: 93 pixels de 1678 visíveis (0.055423...), em seis
  regiões; não é score nem prova de qualidade.
- Relatório técnico e fixtures passaram 5/5. O gate visual humano continua
  pendente; sem `visual_pass`, pose final, animação, `res/`, runtime, ROM ou
  AAA. O budget segue apenas planning_budget, sem nova medição em ROM.
