# Changelog Canonico - MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

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
