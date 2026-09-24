<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-06-28T10:29:54-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 11
- Ultimo build versionado: build_v020
- ROM vigente: `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e` (`131072` bytes)
- Validation summary: errors=1 warnings=2
- Blockers vigentes: visual_gate_blocked, code_loaded_tiles_unmeasured
- Evidencia de emulador: ok
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=funcional performance=estavel audio=ok hardware_real=blastem_reference_emulator
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank - Celestial Chase Revive

## Estado Atual

Data: 2026-06-19

Status operacional: `sector01_technical_closeout_complete_creative_hold`.

Foi criado o projeto canonico:

`Celestial Chase Revive [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_RACING]`

O nome solicitado sem `[TIPO] [GENERO]` foi validado como invalido. A decisao tomada foi criar o diretorio canonico com `[GAME] [ACTION_RACING]`.

## Verdade de Entrega

- Build: `buildado`; `build_v020`, ROM `out/rom.bin`, 131072 bytes, sha256 `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`.
- Boot, Title e abertura: `testado_em_emulador` no BlastEm.
- Sector 01: `testado_em_emulador`; rotas de sucesso e falha fechadas na mesma ROM.
- First playable tecnico do Sector 01: `true`; nao equivale a arte final, audio final, AAA ou release.
- Gameplay basico: funcional para 3 faixas, salto, Lumen, Pulse, Pressure Gate, perseguidor, Beacon, resultado e retorno ao Title.
- Performance: 1800 amostras por rota, zero frames acima do budget, pico CPU 53%, p95 34%.
- Sprites: pico de 15 links e 9 sprites por scanline.
- Memoria: 10.720 bytes de Work RAM estatica; sem `malloc/free` no runtime.
- VRAM: 17 tiles exatos residentes para `img_road_tiles`, sem overlap de ranges; dump VLAB capturado. O scanner central ainda emite `code_loaded_tiles_unmeasured` por classificar chamadas de nametable como carregamento de tiles.
- Evidencia: screenshot, SRAM, VDP dump e ROM selados contra o mesmo hash.
- Assets: placeholders tecnicos; nenhum asset premium final aprovado.
- Audio definitivo: nao iniciado.
- Gate criativo: bloqueado por decisao de escopo.

## Closeout Tecnico do Sector 01 - build_v020

Data: 2026-06-19

Fechamento confirmado:

- O `CreateProcessAsUserW failed: 5` deixou de se reproduzir; criacao de processo voltou a funcionar na sessao interativa correta.
- O transporte de input confiavel nesta maquina e `WM_KEYDOWN/WM_KEYUP` dirigido a janela SDL do BlastEm; `SendInput` por foreground continua nao confiavel.
- A causa exata do `AnimationFrame` invalido era `spr_lumen_orb`, animacao 0: o RESCOMP gerou `numFrame=3` e o helper instalava frame 3 por modulo hardcoded de 4.
- `race_scene.c` passou a consultar `SpriteDefinition->animations[0]->numFrame` e instalar animacao/frame atomicamente com `SPR_setAnimAndFrame`.
- Regressao especifica e contratos atuais passam: Python 14/14 e PowerShell `PASS`.
- O HUD usa WINDOW opaco e sprites de pista sao recortados antes da faixa do HUD; a captura do Beacon prova ausencia de bleed.
- Rotas BlastEm:
  - sucesso: `out/evidence/blastem/routes/success/route_manifest.json`;
  - falha: `out/evidence/blastem/routes/failure/route_manifest.json`;
  - Title para abertura: `out/evidence/blastem/scenes/title_opening/scene_manifest.json`.
- A ROM copiada em todas as rotas possui o mesmo sha256 da ROM vigente.
- `evidence_closeout_report.json`: `sealed`.
- `freshness_audit_report.json`: `ok`, sem stale ou artefato obrigatorio ausente na passagem de fechamento.
- `scene_closeout_gate_report.json`: produzido em `warn`, porque a promocao criativa continua deliberadamente bloqueada.

Hold obrigatorio:

- arte definitiva;
- audio definitivo;
- Upgrade Intermission;
- Sector 02.

Essas frentes so podem iniciar apos aceitacao humana deste closeout. O projeto nao esta `ready_for_aaa` nem `mastering_ready`.

## Auditoria de Recuperacao V014

Data: 2026-06-18

O retorno do agente anterior foi reavaliado contra codigo, logs, hash e BlastEm.

Achados decisivos:

- As capturas antigas pertenciam a ROMs anteriores e nao provavam a `v014`.
- A captura fresca do title mostrou colisao de tiles/VRAM e corrupcao severa.
- A corrida atual abriu com estrada/HUD corrompidos.
- A rota terminou em `ADDRESS ERROR`; o bloco `MTR` de corrida completa nao foi escrito.
- O Pursuer e os Pressure Gates sao descartados pela camada de entidades.
- O Pulse possui cooldown que nunca diminui.
- O HUD nao usa WINDOW e o asset `img_hud_elements` nao e desenhado.
- Os warnings de salto indicam comparacoes impossiveis e o offset visual e aplicado duas vezes.
- Os assets foram gerados por `tools/generate_assets.py` com primitivas Pillow e permanecem placeholders.
- O relatorio automatico de captura extrapolou boot para gameplay/performance/audio; foi normalizado para escopo `boot_title_only`.

Evidencias:

- `out/evidence/blastem_audit_v014/screenshot.png`
- `out/evidence/blastem_audit_v014_route2/race_current.png`
- `out/evidence/blastem_audit_v014_route2/result_current.png`
- `out/evidence/blastem_audit_v014_route2/save.sram`
- `doc/code_review_report.json`
- `doc/agent_learning/v014_recovery_audit.md`

Proximo passo autorizado: recuperar o Sector 01 atual. Nao iniciar Sector 02,
upgrade intermission, boss ou arte final antes de remover o crash, corrigir VRAM,
restaurar os contratos de gameplay e recapturar a rota completa.

### Recuperacao em andamento - 2026-06-19

- Uma ROM posterior removeu a corrupcao visual inicial, mas ainda reproduziu
  `ADDRESS ERROR` com PC `0x00F516`.
- Dois caminhos que chamavam `SPR_setVisibility` com ponteiro potencialmente
  nulo foram corrigidos e receberam regressao estatica.
- O PC `0x00F516` foi mapeado a `SPR_update+0x284`, durante o upload do
  tileset.
- A auditoria binaria do RESCOMP confirmou que `spr_lumen_orb` possui uma
  animacao com `numFrame=3`, mas o pool de pickups instalava
  `(frame_counter / 8) % 4`; o frame invalido preciso era
  `AnimationFrame(animation=0, frame=3)`.
- O quarto bloco 16x16 do PNG de Lumen esta vazio e nao vira frame gerado.
- A causa foi corrigida somente em `race_scene.c`: hazards e pickups agora
  consultam `def->animations[0]->numFrame` e usam
  `SPR_setAnimAndFrame`.
- Regressao especifica criada; suite Python atual: 8/8.
- Suite PowerShell continua falhando por contrato preexistente da tilemap da
  estrada (`TILE_ATTR_FULL`), fora da causa confirmada e sem alteracao nesta
  rodada.
- Build central: `build_v016`, ROM 131072 bytes, sha256
  `1ddb1a3155dd288e78dcf814776435512abf0ceb0ebd8e1a13d161597b8b2729`.
- O executor de processos voltou a funcionar no usuario e sessao interativa
  corretos; `CreateProcessAsUserW failed: 5` nao se reproduziu.
- BlastEm abriu a ROM v016 e o Title foi observado. A SRAM registrou
  `READY`, `SCN=1` e nenhum input observado.
- A rota navegada nao foi recapturada: o modulo canonico nao conseguiu
  foreground apos seis tentativas, e a ponte de controle do Windows falhou
  por incompatibilidade de pacote `@oai/sky`.
- Budget atual: `res_graph` estimado sem overlap (1004 tiles de usuario,
  reserva de sprites 420), mas sem metricas de frame; continua
  `nao_validado`.
- O compilador canonico de contratos reconheceu o manifesto de regressao,
  mas gerou zero cenas a partir do formato atual de `13-spec-cenas.md`;
  o artefato compilado nao foi corrigido manualmente e permanece blocker.
- O Sector 01 permanece `closeout_blocked`; first playable continua `false`.
- Arte definitiva, audio, Upgrade Intermission e Sector 02 continuam
  bloqueados.

## Analise do Benchmark

Projeto analisado:

`Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]`

Achados aproveitaveis:

- A familia de corrida celeste ja possui evidencia tecnica de laboratorio em BlastEm.
- BG_A/B + line scroll + pseudo3D road stack sao rota plausivel.
- O benchmark mostrou que visual bonito sem aprovacao perceptual nao fecha AAA.
- O bug de capsula opaca do heroi virou regra: sprite critico precisa provar index 0 transparente e ausencia de matte visivel.
- O budget de referencia para first playable ficou na ordem de 691/744 tiles de BG no estado v014, com sprite reserve alto.

Achados que nao podem ser herdados como prova:

- `ready_for_aaa=false` no benchmark.
- `perceptual_motion_unvalidated` segue bloqueando metodologia.
- Higiene do legado possui referencias absolutas antigas e inventario externo invalido.
- Algumas tecnicas do benchmark estao em `LABORATORIO` e nao podem entrar como entrega do Revive.

## Decisoes do Revive

- O Revive e `aaa_game` com teto atual `vertical_slice`.
- O pacote atual possui specs completas e runtime seed Fase A.
- Claims `critical_motion`, `road_physics` e `modular_boss` ficam `not_applicable` no manifesto metodologico atual para evitar falsa promessa runtime; o TDD declara quando devem virar `required`.
- Tecnicas selecionadas entram como planejamento com evidencia futura obrigatoria.
- O Mestre Perseguidor sera tratado primeiro como `boss_setpiece_card`; modularidade runtime so sera ativada depois de contrato de partes.

## Technique Usage Sync

Tecnicas declaradas no manifesto e refletidas nos docs:

- `dma_transfer_safety`
- `line_scrolling`
- `pseudo3d_road_stack`
- `camera_scroll_management`
- `hitstop_camera_shake_feedback`
- `window_plane_static_hud`
- `palette_state_transitions`
- `prerendered_sprite_scaling`
- `xgm2_audio_architecture`
- `save_sram_checksum_redundancy`

Status das tecnicas de jogo: planejamento/documentacao. O runtime seed testado usa apenas VDP text, loop VBlank e heartbeat SRAM; pseudo3D, HUD, audio, gameplay, boss e FX ainda nao foram implementados.

## Rodada de Validacao de Specs

Data: 2026-06-16

Resultado:

- JSON de documentacao: `ok`.
- Contexto: `aaa_game` classificado.
- Metodologia: `passed`.
- Higiene: `passed`.
- GDD substancial: `passed`.
- Technique usage: pronto para specs.
- Validador de recursos: falha esperada para producao material ainda nao iniciada.

Bloqueios canonicos restantes:

- `resources_res_missing_for_visual_delivery`
- `asset_pipeline_not_started`
- `visual_gate_blocked`
- `visual_delivery_gate_missing`
- `res_graph_missing_for_visual_delivery`
- `scene_tilemap_conversion_report_missing`
- `per_tile_palette_conflict_report_missing`
- `freshness_audit_missing`
- `scene_closeout_gate_missing`

Leitura operacional: o pacote de specs pode orientar producao ponta a ponta, mas qualquer claim acima de `documentado` exige assets, build, medicoes e evidencia BlastEm.

## Auditoria Front-End

Data: 2026-06-16

Itens checados:

- Fonte: estava parcialmente documentada em `glyph_manifest`; agora possui `text_presentation_profile` e contrato de superficie pixel.
- Logo: estava citado em `S00`; agora possui `brand_identity_manifest` com testes planejados de silhueta, monocromatico, thumbnail e fundo dinamico.
- Menu: estava documentado em alto nivel; agora possui `front_end_menu_contract` com entradas, input, VDP plan e audio hooks.
- Creditos: estavam ausentes; agora possuem `credits_contract`, cena `credits_roll`, textos paginados, QA e regressao futura.

Status: `documentado`. Ainda faltam assets reais, atlas `.res`, capturas BlastEm e medicao de legibilidade nativa.

## Fechamento de Lacunas Criticas

Data: 2026-06-16

Rodada motivada por revisao critica apontando que a documentacao ainda nao guiava producao ponta-a-ponta.

Itens fechados em specs:

- Track data: `doc/track_data_format_contract.json` e `doc/sector_01_track_plan.json`.
- Colisao: `doc/collision_system_contract.json`.
- HUD: `doc/hud_layout_contract.json` e `doc/hud_wireframe.md`.
- Animacao: `doc/sprite_animation_contract.json`.
- Tuning numerico: `doc/progression_tuning_tables.json`.
- Asset production spec: `doc/asset_production_spec.json`.
- Build: `doc/build_system_contract.json`.
- Boss: `doc/boss_attack_pattern_contract.json`.
- Pause/game over/continue: `doc/game_flow_contract.json`.
- Concept/reference art: `doc/concept_art_brief.md` e `doc/concept_art_pack_manifest.json`.
- Auditoria machine-readable: `doc/critical_gap_audit.json`.

Decisoes importantes:

- `SECTOR_01` usa pista por eventos em faixas, nao tile collision.
- Estrada visual nao e fonte de colisao.
- HUD ocupa WINDOW 320x24 com coordenadas fixas.
- Lio usa metasprite 24x32 e hurtbox menor.
- Boss e setpiece de corrida; corpo visual-only, ataques e weakpoints sao entidades testaveis.
- Build continua centralizado no wrapper; Makefile local custom nao e fonte canonica.
- SVGs criados em `data/source_art/revive/concept/` sao mockups com hash, nao arte final.

Status permanece `documentado`; nenhuma dessas decisoes promove build, budget ou evidencia de emulador.

Validacao apos a rodada:

- JSON: `ok`.
- Contexto: `ok`.
- Metodologia: `passed`.
- Higiene: `passed`.
- `validate_resources`: segue bloqueado por ausencia material esperada: sem `.res`, sem `res_graph_report`, sem visual gate, sem reports de tilemap/paleta, sem freshness e sem scene closeout.

## Handoff para Curadoria Canonica

Data: 2026-06-16

Registro criado para avaliacao futura do agente canonico:

- `doc/canonical_planning_curation_handoff.json`
- `doc/agent_learning/planning_mode_curation_candidate.md`
- `doc/agent_learning/skill_promotion_candidates.md`
- `doc/agent_learning/canonical_promotion_review.md`
- `doc/agent_learning/learning_ledger.json`

Candidatos registrados:

- `planning_mode_pre_runtime_spec_closure_checklist`
- `front_end_identity_minimum_contract`
- `central_build_contract_before_runtime_seed`
- `local_mockup_manifest_for_planning_art`
- `creative_cohesion_pass_before_runtime_seed`

Nenhuma promocao canonica foi feita. `canonical_promotion_performed=false` permanece verdadeiro como politica operacional; qualquer alteracao em `.agent` exige decisao humana, testes e memoria atualizada.

Verificacao:

- JSON: `ok`.
- `audit_project_learning.ps1 -Mode Audit`: `lessons=5`, `candidates=5`, `canonical_promotion_performed=false`.
- Contexto: `ok`.
- Metodologia: `passed`.
- Higiene: `passed`.
- Observacao: o reposititorio ja apresenta alteracoes na arvore canonica `.agent`, mas esta rodada nao promoveu nem editou o framework canonico.

## Creative Cohesion Pass

Data: 2026-06-16

Rodada motivada por critica criativa: o jogo estava tecnicamente correto, mas com risco de ser generico como experiencia.

Decisoes tomadas:

- O Mestre Perseguidor deve aparecer visualmente desde o Sector 01, nao apenas no boss final.
- Lumen deixa de ser moeda segura: Lumen carregado aumenta Pressure por faixas numericas.
- Cada setor jogavel precisa ter regra mecanica propria, alem de skin/paleta.
- A transicao Sector 03 -> Sector 04 possui setpiece obrigatorio: `shattered_lane_gauntlet`.
- Musica vira feedback de gameplay por Pressure, Lumen e fase do boss.
- Replayability entra por estrelas de setor, lore shards, concept unlocks e dificuldade extra.

Contratos criados:

- `doc/creative_cohesion_pass.md`
- `doc/pursuer_presence_contract.json`
- `doc/lumen_pressure_economy_contract.json`
- `doc/sector_mechanic_identity_contract.json`
- `doc/signature_setpiece_contract.json`
- `doc/reactive_music_gameplay_contract.json`
- `doc/replayability_score_contract.json`
- `doc/creative_cohesion_audit.json`

Documentos sincronizados:

- GDD, LDD, TDD, specs de cenas, QA, audio, tuning, track data, asset register, entity archetypes, save system, production runtime contract, radar criativo e level blueprint.

Status permanece `documentado`: a coesao criativa agora e testavel em specs, mas ainda depende de runtime, assets, audio real, capturas BlastEm, metricas e aprovacao perceptual.

## Runtime Seed - Fase A

Data: 2026-06-16

Escopo implementado:

- `src/main.c`
- `src/boot/sega.s`
- `src/boot/rom_head.c`
- `inc/project_config.h`
- `res/resources.res`

Resultado:

- Build pelo wrapper central: sucesso.
- ROM: `out/rom.bin`, 131072 bytes.
- ROM sha256: `8de2fef56a1db9b6992e4ebce4e76022576052721984d3482d5f21dc91ac8bf7`.
- BlastEm: `boot_emulador=ok`.
- Screenshot: `out/evidence/blastem/screenshot.png`.
- SRAM: `out/evidence/blastem/save.sram`.
- Heartbeat: `READY` confirmado em SRAM `0x100`.
- Tela observada: `CELESTIAL CHASE REVIVE`, `RUNTIME SEED 001`, `BOOT: OK`.

Limitacoes registradas:

- O seed nao possui scene manager, title interativo, cutscene, Sector 01, player, track data, collision, HUD ou audio.
- `runtime_metrics.json` nao existe porque o seed nao emite MDRT completo; a evidencia atual e screenshot + SRAM READY.
- `visual_vdp_dump.bin` nao existe e nao e requerido para este seed minimo.
- `rom_mastering_report.json` decidiu `mastering_needs_fix`: checksum e regiao estao ok, mas ainda faltam closeout, budget e validacao limpa de produto.
- O fixer do wrapper substituiu `src/boot/rom_head.c` pelo header padrao SGDK 2.11; por isso o mastering ainda mostra `SAMPLE PROGRAM` / `GM 00000000-00`. Corrigir identidade de header exige etapa propria sem quebrar a politica do wrapper.

Status correto: `buildado` e `testado_em_emulador` para Fase A runtime seed. Nao declarar `pronto`, `AAA`, `first_playable`, `gameplay_rom_aprovada` ou `ready_for_aaa`.

## Runtime Seed - Fase B Parcial

Data: 2026-06-17

Escopo implementado:

- `src/scene_manager.c` e `inc/scene_manager.h`: gerenciador de cenas com `enter/update/exit`, transicao solicitada e limpeza de BG_A/BG_B/WINDOW.
- `src/input_abstraction.c` e `inc/input_abstraction.h`: leitura de input com `pressed/held/released`.
- Cenas placeholder: `branding_scene`, `title_scene`, `opening_cutscene`, `race_scene` e `credits_scene`.
- Loop principal atualizado com `SPR_update()` antes de `SYS_doVBlankProcess()`.
- Paleta de texto corrigida: cor 15 da PAL0 reservada para o font padrao SGDK.
- Probe runtime em SRAM: `READY` em `0x100` e `SCN` + `scene_id` em `0x108`.

Resultado provado:

- Build pelo wrapper central: sucesso com warnings metodologicos de closeout.
- ROM: `out/rom.bin`, 131072 bytes.
- ROM sha256: `06b63c6be59b86947506cca94ff17dd7104eff366bc11b68b65187e5f2464796`.
- BlastEm: `boot_emulador=ok`, `blastem_gate=true`, `testado_em_emulador=true`.
- Screenshot: `out/evidence/blastem/screenshot.png`, sha256 `90ba0fe3853efbafe9f4dca72d794f92322a29f3f1e4448fa44f31c8edfc05b4`.
- SRAM: `out/evidence/blastem/save.sram`, sha256 `16d0af3cfdfbe48a6ba6a674db89a8a34e4be626b9b01ae2b18d38200859af54`.
- Heartbeat: `READY` confirmado em SRAM `0x100`, counter `174`.
- Scene probe: `SCN`, `scene_id=1`, correspondente a `APP_SCENE_TITLE`.
- Tela observada: `CELESTIAL CHASE REVIVE`, `START RUN`, `CREDITS`.
- Freshness audit: `status=ok`, `stale=0`, `missing_required=0`.

Limitacoes registradas:

- A navegacao `TITLE -> OPENING_CUTSCENE` ainda nao foi provada por input automatizado.
- `opening_cutscene`, `race_scene` e `credits_scene` existem em runtime, mas permanecem placeholders.
- Sector 01 jogavel ainda nao existe.
- `visual_vdp_dump.bin` e `runtime_metrics.json` continuam ausentes, aceitos apenas para este seed minimo.
- `rom_mastering_report.json` permanece `mastering_needs_fix`: BlastEm/checksum/regiao estao ok, mas faltam closeout visual, budget e identidade de header.
- Header ROM ainda mostra `SAMPLE PROGRAM` / `GM 00000000-00` por politica/fixer do wrapper.

Status correto: `buildado` e `testado_em_emulador` para boot ate TITLE com scene probe. Nao declarar `first_playable`, `gameplay_rom_aprovada`, `validado_budget`, `mastering_ready` ou `ready_for_aaa`.

## Runtime Seed - Fase B Gate TITLE -> OPENING

Data: 2026-06-17

Escopo implementado e provado:

- `TITLE -> OPENING_CUTSCENE` validado no BlastEm com input START.
- `src/input_abstraction.c` agora chama `JOY_init()` no init e `JOY_update()` antes de `JOY_readJoypad(JOY_1)`.
- Probe runtime ampliado: `READY` em `0x100`, `SCN` + `scene_id` em `0x108` e `INP` em `0x110`.
- A automacao por `SendInput` do wrapper foi diagnosticada como nao observada pela ROM nesta maquina (`observed_input=0`).
- A captura aprovada usou transporte `wm_key_message_to_sdl_window`, que foi observado como `BUTTON_START` (`observed_input=128`).

Resultado provado:

- Build pelo wrapper central: sucesso.
- ROM: `out/rom.bin`, 131072 bytes.
- ROM sha256: `e0bee897eeb6be1b5ac4d8ad746bb7172af3479e8627ff859762367f0e4a6e64`.
- BlastEm: `boot_emulador=ok`, transicao de cena funcional, fechamento gracioso `wm_close`.
- Screenshot: `out/evidence/blastem/screenshot.png`, sha256 `f6ff6c31590cbf861c330238da2c477b85766c0c8fbfb2a1b3007c0daae3b15e`.
- SRAM: `out/evidence/blastem/save.sram`, sha256 `273e4aae2b37689ebb2ad4f7343c54a6859d91c089b194a603fd36d6a0c4ca8c`.
- Scene probe: `SCN`, `scene_id=2`, correspondente a `APP_SCENE_OPENING_CUTSCENE`.
- Input probe: `INP`, `observed_input=128`, equivalente a `BUTTON_START`.
- Tela observada: opening cutscene com texto `UNTIL THE LAST BEACON CRACKED.`.
- Freshness audit: `status=ok`, `stale=0`, `missing_required=0`.
- Validation: errors=0, warnings=5.

Limitacoes registradas:

- A cutscene abre, mas o fluxo `OPENING_CUTSCENE -> RACE -> TITLE` ainda nao foi provado.
- `opening_cutscene`, `race_scene` e `credits_scene` seguem placeholders de runtime seed.
- Sector 01 jogavel ainda nao existe.
- `visual_vdp_dump.bin` e `runtime_metrics.json` continuam ausentes, aceitos apenas para este seed minimo.
- `rom_mastering_report.json` permanece `mastering_needs_fix`: faltam closeout visual, budget e identidade de header.
- Header ROM ainda mostra identidade padrao do wrapper (`SAMPLE PROGRAM` / `GM 00000000-00`).

Status correto: `buildado` e `testado_em_emulador` para TITLE -> OPENING_CUTSCENE. Nao declarar `first_playable`, `gameplay_rom_aprovada`, `validado_budget`, `mastering_ready` ou `ready_for_aaa`.

## Runtime Seed - Fase B Gate OPENING -> RACE -> TITLE

Data: 2026-06-17

Escopo provado:

- Fluxo `TITLE -> OPENING_CUTSCENE -> RACE -> TITLE` validado no BlastEm.
- `OPENING_CUTSCENE -> RACE` provado por probe dedicado com `scene_id=3`.
- `RACE -> TITLE` provado por probe dedicado com `scene_id=1`.
- `doc/blastem_input_script.json` atualizado para a rota completa.
- `emulator_session.json` e `blastem_evidence.json` normalizados para o contrato do wrapper, mantendo `opening_race_title_route_report.json` como evidencia detalhada da rota.

Resultado provado:

- ROM: `out/rom.bin`, 131072 bytes.
- ROM sha256: `e0bee897eeb6be1b5ac4d8ad746bb7172af3479e8627ff859762367f0e4a6e64`.
- Transporte de input: `wm_key_message_to_sdl_window`.
- Input observado pela ROM: `observed_input=128` (`BUTTON_START`).
- Rota esperada/observada: `[3, 1]`.
- Race screenshot: `out/evidence/blastem/opening_to_race.png`, sha256 `7cd4d82c1e9ac43edcf0f9f0c58ff5c34252c3d28d45804b6304e0db983a124d`.
- Race SRAM: `out/evidence/blastem/opening_to_race.sram`, sha256 `87148cb563cb3dbf9141af7bcb542e352f7ccb09f2caa2418976f560d3102382`.
- Canonical final screenshot: `out/evidence/blastem/screenshot.png`, sha256 `90ba0fe3853efbafe9f4dca72d794f92322a29f3f1e4448fa44f31c8edfc05b4`.
- Canonical final SRAM: `out/evidence/blastem/save.sram`, sha256 `6720ab42dcdab34840e7b1a71f4545fae29570912c6e9f693f9cbbd4234434fa`.
- `opening_race_title_route_report.json`: `status=ok`.
- `freshness_audit`: `status=ok`, `stale=0`, `missing_required=0`.
- `validate_resources`: errors=0, warnings=5.
- `rom_mastering_report`: `mastering_needs_fix`.

Limitacoes registradas:

- `race_scene` ainda e placeholder; a tela prova rota de cena, nao gameplay real de corrida.
- Sector 01 jogavel ainda nao existe.
- Sem player 3 faixas, track events, colisao, Lumen, Pulse, HUD ou perseguidor no runtime.
- `runtime_metrics.json`, `scene_closeout_gate_report.json`, budget, visual delivery e VDP dump continuam ausentes.
- Mastering segue bloqueado por closeout, budget, reports de conversao/paleta e identidade de produto no header.

Status correto: `buildado` e `testado_em_emulador` para rota runtime seed `TITLE -> OPENING_CUTSCENE -> RACE -> TITLE`. Nao declarar `first_playable`, `gameplay_rom_aprovada`, `validado_budget`, `mastering_ready` ou `ready_for_aaa`.

## Reavaliacao de Premissas Canonicas - 2026-06-27

Status operacional reavaliado: `sector01_technical_closeout_complete_creative_and_contract_hold`.

Diagnostico por camadas:

- `host_executor`: `warning`; processos PowerShell funcionam, mas `assert_agent_environment.ps1` nao fechou `ready` porque Graphify falhou com `uv trampoline failed to canonicalize script path`. Graphify fica consultivo e nao deve ser usado como fonte decisoria ate voltar a `fresh`.
- `toolchain_wrapper`: `warning`; wrapper e validadores executam, mas `validate_resources.ps1` ainda fecha com 1 erro e 7 warnings por promocao visual/AAA bloqueada, stale de tilemap conversion e documentacao/freshness.
- `rom_runtime`: `passed` somente no escopo `Sector 01 technical first playable`; a ROM vigente continua `build_v020`, sha256 `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`, com rotas BlastEm previamente seladas.
- `creative_quality`: `blocked`; assets atuais sao placeholders tecnicos. Nenhuma arte premium, audio final, mastering ou `ready_for_aaa` foi aprovado.

Premissas canonicas aceitas:

- Um closeout tecnico pode coexistir com promocao criativa bloqueada.
- Build, screenshot, SRAM e runtime metrics so provam o escopo declarado; nao provam automaticamente arte final, audio, Sector 02 ou AAA.
- O projeto correto deve atacar o blocker dominante antes de expandir conteudo.
- Cenas futuras precisam de contrato proprio antes de runtime: o compilador de cenas reconheceu 14 cenas, mas `opening_catalyst_cutscene` e `race_start_handoff` ainda exigem `cutscene_contract`; varias cenas futuras seguem com `boot_mode=unsupported`.

Leitura de retomada:

- Nao rebuildar nem recapturar a ROM sem mudanca causal.
- Nao iniciar Sector 02, Upgrade Intermission, boss, audio final ou arte final como implementacao ampla enquanto os gates de direcao visual e contratos de cena estiverem bloqueados.
- Proxima fatia segura: fechar alinhamento documental/freshness e, depois de aceite humano do closeout tecnico, iniciar uma fatia de direcao visual minima do front-end/Sector 01 com assets autorais nao-procedurais e gate perceptual antes de novo runtime.

## Contratos Cinematograficos - 2026-06-27

Status operacional: `documentado_com_compilador_corrigido_sem_nova_rom`.

Avanco feito:

- `opening_catalyst_cutscene` agora possui storyboard cinematico machine-readable em `doc/contracts/opening_cinematic_storyboard_contract.json`.
- `opening_cutscene_contract.json` foi expandido com ponteiros para FSM, resource plan, layout de paineis, paleta, texto, audio, teardown, evidence plan, glyph manifest e storyboard.
- `race_start_handoff` agora possui pacote de contratos proprio: contrato principal, FSM, resource plan, panel layout, text timing, palette script, teardown, evidence plan e storyboard cinematico.
- `doc/13-spec-cenas.md` referencia todos esses contratos nas Cenas 2 e 3.
- `art_diagnostic.py` classificou o projeto como `2_res_exists_check`: 11 assets em `res/`, todos carregaveis, mas ainda com avisos de paleta/transparencia e alguns sprites acima de 32x32 que exigem metasprite ou recorte correto.

Correcao aplicada apos aprovacao humana:

- `tools/sgdk_wrapper/scene_contract_compiler.ps1` agora descobre contratos de cutscene em `doc/contracts/*_contract.json` e projeta `cutscene_contract` no `doc/scene-contracts.json` por `scene_id`.
- O teste `tools/sgdk_wrapper/ci/test_scene_contract_compiler.ps1` foi ampliado para provar que um contrato de cutscene projetado remove `SC100`.
- `tools/sgdk_wrapper/ci/test_scene_contract_compiler.ps1`: 8/8 testes passaram.
- `tools/sgdk_wrapper/ci/test_cutscene_contract_lint.ps1`: 7/7 testes passaram.
- `scene_contract_compiler.ps1 -Mode production` no projeto reconheceu 14 cenas, gerou 0 erros e preservou `cutscene_contract` para `opening_catalyst_cutscene` e `race_start_handoff`.
- `lint_scene_contract.ps1 -Mode production` ficou sem erros e sem `SC100`; restam 7 warnings de cenas futuras/unsupported e regressao obrigatoria.

Limite importante:

- Esta correcao e documental/compilador de contrato; nenhuma ROM nova foi buildada ou vista no BlastEm nesta rodada.
- `race_start_handoff` ainda esta com `boot_mode=unsupported` no contrato compilado; isso e aceitavel como planejamento, mas bloqueia claim de runtime.
- `validate_resources.ps1` foi reproduzido com timeout maior; a validacao era longa e silenciosa, nao um travamento permanente.
- O report canonico foi atualizado e voltou a 1 erro/5 warnings; `freshness_audit.ps1` ficou `status=ok`, `stale=0`.
- A melhoria do wrapper permanece registrada para curadoria em `doc/agent_learning/cutscene_contract_compiler_curation_candidate.md`, agora com implementacao local aplicada.

Validacao desta rodada:

- `validate_project_context.ps1`: `ok`.
- `validate_project_methodology.ps1`: `passed`.
- `validate_project_hygiene.ps1`: `passed` apos remover de `doc/` um report operacional com caminhos absolutos.
- `scene_contract_compiler.ps1 -Mode production`: 0 erros, 7 warnings; `SC100` removido.
- `validate_resources.ps1`: 1 erro, 5 warnings; blockers reais: `visual_gate_blocked`, `procedural_fallback_as_final`, `visual_direction_failed`, `code_loaded_tiles_unmeasured`, `scene_tilemap_conversion_report_stale`.
- `freshness_audit.ps1`: `ok`, `stale=0`, `missing_required=0`.
- `audit_project_learning.ps1 -Mode Capture`: 18 licoes/candidatos, nenhuma promocao canonica.

Sem mudanca de ROM:

- ROM vigente continua `build_v020`.
- Nenhuma build, captura BlastEm ou claim novo de runtime foi feito nesta rodada.

## Proxima Fase

1. Converter `visual_slice_v001` em assets SGDK controlados para front-end/Sector 01, sem substituir a ROM vigente antes de budget e captura.
2. Resolver `code_loaded_tiles_unmeasured` com auditoria explicita das chamadas de nametable/tiles gerados por codigo ou dump VDP.
3. Recapturar no BlastEm somente depois da conversao visual real para `res/` e update de budget.
4. Manter a ROM v020 como baseline congelado ate haver mudanca causal de runtime ou asset real.
5. Manter arte definitiva ampla, audio definitivo, Upgrade Intermission e Sector 02 bloqueados ate aceite e gate visual.

## Blockers Atuais

- `visual_gate_blocked`: `visual_slice_v001` criou direcao visual medida, mas os assets seguem `needs_review`, sem conversao para `res/`, sem captura BlastEm nova e sem `visual_vdp_dump`.
- `code_loaded_tiles_unmeasured`: falso positivo conservador do scanner central para chamadas de nametable; budget independente, ranges e dump VLAB estao registrados.
- Header ROM ainda segue a identidade padrao do wrapper; mastering/release permanece bloqueado.
- Audio definitivo nao foi produzido nem autorizado.

Esses blockers nao invalidam o first playable tecnico do Sector 01. Eles bloqueiam promocao visual, mastering, AAA, arte definitiva, audio, Upgrade Intermission e Sector 02.

## Visual Slice V001 - 2026-06-28

Status operacional: `source_direction_established_runtime_pending`.

Avanco feito:

- Criado `tools/build_visual_slice_v001.py` para gerar uma fatia visual autoral e mensuravel sem tocar em `res/` nem rebuildar a ROM.
- Criados source PNGs em `data/source_art/revive/visual_slice_v001/`: `title_frontend_source_v001.png` e `sector01_playfield_source_v001.png`.
- Criado painel de revisao `data/processed/visual_slice_v001/visual_slice_contact_sheet_v001.png`.
- Criados `doc/visual_slice_v001_manifest.json` e `doc/locked_visual_direction_v001.json`.
- Atualizados `doc/source_validity_report.json` e `doc/authoriality_gate_report.json` para `passed_for_source_direction_only`; promocao para `res/` continua bloqueada.
- Atualizado `out/logs/visual_delivery_gate_report.json` com `visual_direction_status=passed`, assets criticos em `needs_review`, `ready_for_aaa=false`.
- Atualizados `out/logs/scene_tilemap_conversion_report.json`, `out/logs/per_tile_palette_conflict_report.json` e `out/logs/tilemap_flag_report.json`.

Medicao:

- PNGs do slice: `P`, `bitDepth=4`, `colorType=3`, `PLTE=16`, dimensoes multiplas de 8, cores visiveis em grid 9-bit.
- Sector 01 source: 1120 tiles totais, 202 tiles unicos finais com dedup HV, estimativa 6464 bytes de VRAM e 2240 bytes de mapa.
- `validate_project_hygiene.ps1`: `passed`.
- `validate_resources.ps1`: 1 erro, 2 warnings; blockers reduzidos para `visual_gate_blocked` e `code_loaded_tiles_unmeasured`.

Sem mudanca de ROM:

- Nenhuma build, captura BlastEm ou claim novo de runtime foi feito nesta rodada.
- A ROM vigente continua `build_v020`.

## Evidencia fresca Linux P0-005 - 2026-07-19

- BlastEm Linux 0.6.2, Flatpak commit
  `c1f3f4435e9d009fa001322e26e73e785fe443fcedfae1f3187836685c602221`.
- Sessao: `blastem-linux-20260720T023600Z-152199`.
- ROM preservada: `build_v020`, SHA-256
  `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`.
- Front-end observado; screenshot, SRAM, VLAB e metricas foram selados com o
  mesmo identificador e passaram o auditor pos-selagem.
- O screenshot passou integridade semantica. Isso nao aprova a direcao
  criativa nem substitui a pendencia dos assets definitivos.
- A leitura de 60.9 fps e as 900 amostras VLAB pertencem a uma captura isolada;
  performance ampla continua `unproven` ate o P1-003.
- `rom_mastering_report.decision=mastering_needs_fix`, pois validacao limpa e
  closeout continuam bloqueados apesar de checksum, regiao e evidencia fresca
  estarem coerentes.
- O bundle anterior foi preservado em
  `out/evidence/blastem/archive_pre_p0_005_20260719/`.

## Correcao do contrato de dano e reprova visual de Lio — 2026-07-24

- O strip `lio_all.png` foi auditado com `sprite_artifact_report.v2`:
  `technical_pass_visual_fail`, 19 frames e 77 blockers. A anatomia
  geometrica, silhueta e composicao nao foram aprovadas.
- O runtime agora da prioridade ao dano sobre salto e pulso, seleciona
  `ANIM_DAMAGE`, percorre 3 frames com hold de 6 frames e usa blink esparso.
- A regressao estatica passou e `race_scene.c` compilou na ROM SGDK 2.11.
- Build Linux/Wine: ROM de 131072 bytes, SHA-256
  `a69050c105c6da29ff47dc098438e2da07b93a34cf03916949168b249adccd26`.
- Na sessao BlastEm fresca `blastem-linux-20260724T034731Z-512798`, a rajada
  animada observou o estado de dano e seus frames reais. O GIF e a prancha
  vivem na raiz da sessao.
- O gate semantico da screenshot reprovou a cena como
  `blank_or_low_information_capture`; portanto o contrato de runtime esta
  cumprido, mas `sprite_visual_pass=false`, `scene_visual_pass=false` e
  `ready_for_aaa=false`.
- Parecer:
  `doc/contracts/damage_animation_revalidation_report_20260724.json`.
