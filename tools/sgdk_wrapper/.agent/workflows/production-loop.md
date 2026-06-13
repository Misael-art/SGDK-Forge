# Workflow: Production Loop

Use este fluxo para o pipeline completo de uma iteracao: design -> arte -> runtime -> QA -> evidencia.

Cada passo referencia skills reais. A ordem canonica da jornada de cena AAA vive em:

- `workflows/aaa-scene-pipeline.md`
- `pipelines/aaa_scene_v1.json`

Nenhum passo pode ser pulado.

---

## Pipeline: Design -> Art -> Code -> QA -> Iteracao

### 0. Abertura e classificacao do contexto

Workflow canonico de entrada:

- `workflows/project-opening.md`
- `workflows/project-context-classification.md`
- `workflows/project-methodology-adoption.md`
- `workflows/route-decision-gate.md`

O agente deve primeiro classificar o pedido como:

- `projeto_existente`
- `reseed`
- `projeto_novo`

E deve classificar o tipo de trabalho como:

- `aaa_game`
- `technical_demo`
- `exercise`
- `game_review`
- `consulting`

Regra:

- se for `projeto_existente`, continuar a iteracao vigente
- materializar e validar `doc/project_context_manifest.json`; `unclassified` bloqueia producao e parecer final
- use `validate_project_context.ps1` para saber quais documentos bloqueiam no contexto atual
- `game_review` e `consulting` nao exigem ROM por padrao, mas exigem escopo, evidencias citadas e limites do parecer
- `technical_demo` e `exercise` nao podem declarar `ready_for_aaa`; jogo AAA nao pode usar perfil reduzido para escapar de GDD/TDD/spec/QA
- materializar e classificar `doc/project_methodology_manifest.json` antes de arte/runtime; projetos antigos nao recebem claims inferidos por texto
- se for `reseed` ou `projeto_novo`, emitir fundacao documental minima antes de arte ou runtime
- se a rota tecnica da entrega ainda nao estiver declarada, emitir `route_decision_record` antes de escolher ferramenta ou skill de implementacao
- executar `audit_project_learning.ps1 -Mode Audit` e consultar primeiro o indice compacto de licoes/candidatos relevantes
- antes de gerar arte original, prompt de imagem, sourcing externo ou codigo SGDK sensivel, emitir `context_pack_manifest`
- antes de converter ou medir match visual de asset critico, emitir `source_validity_report`, `authoriality_gate_report` e `clone_risk_report`
- benchmark tecnico so pode orientar escala, densidade, timing, presenca, budget e qualidade; se virar fonte visual, pose, paleta, silhueta ou estrutura, a entrega bloqueia

### 1. Escopo, planejamento e mecanica

Papel humano: direcao de produto.

Skill canonica de apoio quando o projeto estiver nascendo ou precisar de reseed:

- `planning/game-design-planning`

- consultar `doc/11-gdd.md` e `doc/13-spec-cenas.md`
- em projeto novo ou reseed de escopo, emitir `project_brief`, `core_loop_statement`, `feature_scope_map`, `scene_roadmap`, `first_playable_slice`, `roteiro_scope` e `front_end_profile`
- declarar no GDD a ambicao tecnica, visual, sonora e de jogabilidade, incluindo a barra de qualidade pretendida e a estrategia real de hardware
- quando o projeto for novo, reseed, vertical slice ou claim AAA, emitir ou
  atualizar `doc/creative_director_radar.json`: promessa autoral, eixos de
  benchmark, pilares assinatura, lacunas propositivas, cena assinatura,
  fronteiras de nao-copia, evidencia e fallback
- o agente deve apontar o que esta correto e tambem o que ainda esta generico;
  parecer sem proposta de menor passo implementavel e evidencia esperada fica
  incompleto para direcao criativa
- nenhuma proposta do radar vira escopo silencioso: antes de runtime, ela deve
  estar aceita/deferida/rejeitada e refletida no GDD/spec/TDD quando aplicavel
- declarar tecnicas escolhidas e rejeitadas/adiadas com registry IDs, tags, funcao no jogo, owner skills, budget/evidencia e fallback
- delimitar escopo da iteracao
- quando o projeto ja declarou opt-in por uma especializacao de genero em `doc/genre_specialization_manifest.json`, o design de superficie dessa especializacao (ex: `fighting_2d_design_contract.json`) eh referencia obrigatoria para escopo; sem manifesto, o pipeline generalista continua valendo e nenhuma especializacao eh inferida por nome de pasta, codigo ou regex
- registrar criterio de aceitacao
- quando houver menu, title screen ou front-end, `front_end_profile` nasce aqui como seed de design e depois e formalizado como `ui_decision_card`
- quando houver logo, press-start, title screen, menu principal ou front-end autoral, declarar `brand_identity_manifest` junto do `ui_decision_card`
- quando a iteracao envolver HUD/UI formal, declarar `ui_decision_card` no GDD/spec antes de abrir arte/runtime
- quando a UI formal envolver health bar, fonte, caixa, micro-icone, cursor ou atlas pixel-perfect de entrega, declarar `ui_pixel_surface_contract`
- quando a UI tiver peso tipografico real, derivar `glyph_manifest` de strings reais e anexar `typography_role`, `font_render_mode`, `charset_profile`, `glyph_budget_class`, `font_owner` e `fallback_font_plan` ao mesmo card
- quando texto, fala, alerta cinetico, painel, balao, retrato, typewriter voice ou flavor text tiver peso dramatico, anexar `text_presentation_profile` ao mesmo card
- quando a iteracao envolver transicao formal entre cenas, zonas, atos, menu, cutscene ou estado visual, declarar `scene_transition_card` antes de abrir arte/runtime
- quando a transicao tocar HUD, menu, title, overlay ou texto critico, referenciar tambem o `ui_decision_card`
- quando a iteracao envolver menu, title screen ou front-end, o mesmo card deve usar `profile_kind=front_end_profile`
- quando a iteracao for o primeiro slice de projeto novo, declarar tambem `route_decision_record` com `dominant_route`, `first_skill`, `first_tool`, `resource_loading_model`, `asset_strategy`, evidencias e atalhos bloqueados
- para projeto autoral com personagem principal, declarar `authorial_model_sheet` antes de arte final; para cenario, declarar `authorial_stage_concept`
- para personagem novo, heroi, inimigo relevante, lutador, boss ou NPC expressivo, declarar `visual_dna_manifest.scale_contract` antes de model sheet, key poses ou strips; escala em `draft` nao aprova key poses
- para asset critico, o manifesto precisa trazer `license`, `authorial_source`, `derivative_of`, `derivative_license_status`, `clone_risk_score`, `clone_risk_method` e `benchmark_used_as`
- quando a iteracao envolver autoria visual nova, emitir ou atualizar `project_bible`, `visual_dna_manifest`, `design_inheritance`, `benchmark_usage_policy`, `authorial_consistency_report` e `style_drift_report` conforme aplicavel
- quando a iteracao envolver raster, H-Int, line scroll, palette split, Shadow/Highlight, palette cycling, hit sparks, particulas ou feedback dramatizado, declarar `feedback_fx_decision_card`
- quando a iteracao envolver boss, setpiece, weak point, telegraph, plane takeover ou arena especial, declarar `boss_setpiece_card`
- quando a iteracao envolver streaming, metatiles, priority foreground, destruicao local, parallax regional ou rota complexa, declarar `advanced_tilemap_design_card`
- quando a iteracao envolver XGM2, PCM ownership, ambience, stinger, boss cue, fade ou prioridade de SFX, declarar `audio_architecture_card`
- quando a iteracao envolver qualquer tecnica catalogada no painel de proficiencia do agente, declarar ou atualizar `doc/technique_usage_manifest.json` dentro do projeto antes de runtime/QA
- quando a iteracao envolver movimento critico, estrada/pseudo-3D ou boss modular, declarar o claim correspondente em `doc/project_methodology_manifest.json`; `required` aciona skills, contratos e gates, `not_applicable` exige justificativa
- o `technique_usage_manifest` deve mapear cada tecnica usada para `registry_id`, `technique_tags`, `human_proficiency_status`, `owner_skills`, evidencias e docs sincronizados; tags livres ou IDs fora do registry bloqueiam entrega
- tecnicas com `human_proficiency_status=LABORATORIO` so podem aparecer em projetos lab/techdemo com `lab_not_delivery=true`; produto principal, vertical slice de entrega ou claim AAA bloqueia
- todo material especifico do projeto deve permanecer dentro do proprio projeto; evidencia ou entrada externa so entra no fluxo depois de copiada, hashada e registrada em `doc/project_hygiene_manifest.json`
- quando houver audio declarado em `.res`, rodar `tools/sgdk_wrapper/validate_audio.ps1` e registrar `out/logs/audio_validation_report.json` antes do fechamento
- quando a cena tiver perfil `aaa_layered`, registrar antes da arte/runtime uma triagem arquitetural com `scene_profile`, `baseline_technique_applicability`, `baseline_contract`, `baseline_decision`, `divergence_reason` quando houver divergencia e `reference_implementation` quando houver referencia interna forte
- para esse perfil, `tilemap streaming guiado pela camera` vira baseline arquitetural prioritario de analise, sem obrigar replicacao cega
- se a tecnica for aplicavel em modo `sim` ou `parcial`, extrair dela explicitamente: divisao base/foreground, papel de cada plano, staging visual, organizacao de tilemaps, forma de oclusao e relacao sprite/cenario
- se houver uma referencia interna madura, como a `BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BRIGA DE RUA]`, usa-la como implementacao de apoio, nao como nome da tecnica
- se a cena divergir, justificar o desvio com constraints reais antes de abrir depuracao residual de VRAM, paleta, `rescomp`, `WINDOW` ou sprite runtime
- quando a cena prometer profundidade monumental, clima dinamico, bioma-chave, pseudo-3D, agua/calor/linha, fundo vivo ou setpiece de fundo, declarar que a etapa 2 deve emitir `scene_direction_record` via `art/scene-direction-curator`

Saida minima:

- briefing aceito
- seeds de planejamento suficientes quando o projeto estiver nascendo ou o escopo estiver sendo redefinido
- `route_decision_record` quando a rota tecnica ainda nao estiver congelada
- `creative_director_radar` quando o alvo for projeto novo, reseed,
  vertical_slice_candidate, ready_for_aaa ou quando houver lacuna de
  personalidade/signature
- `context_pack_manifest` quando a iteracao envolver arte original, sourcing externo ou API SGDK sensivel
- `ui_decision_card` quando houver surface formal de UI
- `ui_pixel_surface_contract` quando houver UI pixel-perfect, health bar, fonte, caixa, micro-icone, cursor ou atlas de entrega
- `brand_identity_manifest` quando houver logo, title screen, press-start, menu principal ou front-end autoral
- `glyph_manifest` + anexo tipografico quando a tipografia tiver peso dramatico ou de leitura
- anexo `ui_decision_card.text_presentation_profile` quando texto for encenacao, fala, alerta, flavor ou ritmo dramatico
- `scene_transition_card` quando houver transicao formal
- `feedback_fx_decision_card`, `boss_setpiece_card`, `advanced_tilemap_design_card` e `audio_architecture_card` quando a cena tocar esses dominios
- `doc/technique_usage_manifest.json` quando a cena usar tecnica catalogada ou tag de proficiencia humana do agente
- em audio senior, combinar `xgm2-audio-director` com `z80-pcm-custom-driver` apenas quando o XGM2 padrao nao cobrir a necessidade real
- em audio senior, materializar `audio_architecture_card`, `audio_channel_ownership_report`, `dac_stream_budget_report` e `sfx_priority_matrix` quando audio afetar gameplay, setpiece ou feedback

### 1a. Chain de Producao canonico (GDD -> TDD -> Mec -> Level -> Enemy -> Audio -> Art -> Runtime -> QA)

Quando o alvo for `vertical_slice_candidate` ou `ready_for_aaa`, a etapa 1 se subdivide em Chain de Producao canonico. O Chain e materializado em `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json` e referenciado por `workflows/5-stage-production.md`. Nenhuma etapa de arte/runtime/QA pode ser aberta sem as 5 sementes de design declaradas:

1. **1b. TDD (S2)** — `planning/tdd-authoring` produz `tdd_contract.json` com `state_fsm_map`, `memory_pool_map`, `vblank_dma_ownership`, `h_int_ownership`, `audio_ownership`, `save_scope`, `region_timing_scope`, `rom_mastering_scope`, `technique_selection` e `risk_mitigation_table`. Cada tecnica selecionada declara aplicacao, funcao, owner, budget/evidencia e fallback; rejeicoes/adiamentos ficam explícitos. O TDD nasce ANTES do codigo C; o `sgdk-runtime-coder` nao pode improvisar ownership.
2. **1c. Mecanica (S3)** — `design/systems-mechanics-validator` produz `mechanic_contract.json` e `mechanic_validation_report.json` contra as 5 Leis Fundamentais (Agency, Feedback, Flow, Consistency, Reward). Mecanica core precisa de versatility_cases >= 3, min_reuses >= 3, combination_map >= 1.
3. **1d. Level Design (S4)** — `design/level-design-canonical` produz `level_blueprint.json` e `level_design_report.json`. Toda mecanica core precisa aparecer em `mechanic_reuse_map`. `golden_path.waypoint_sequence` precisa de >= 2 waypoints e `phase_rhythm_map` precisa de fases `calm` E `pressure`.
4. **1e. Enemy Roster (S5)** — `design/enemy-design-canonical` produz `enemy_roster.json` e `enemy_design_report.json` contra `enemy_ai_role_catalog.json` e `head_metric_reference.json`. Toda entrada precisa de role, telegraph_model com `telegraph_frames >= 1`, synergy_partners (exceto `solo_tutorial` e `boss`), e head_metric compativel com role (boss exige XL).
5. **1f. Audio Adaptativo (S6)** — `code/xgm2-audio-director` (anexo adaptive music) produz `adaptive_music_state_map.json` quando o score reage a estado de gameplay. Cada `music_state` precisa de `transition_type`, `transition_frames >= 1` e `fallback_track_id`. `channel_ownership_reservation` precisa estar consistente com `audio_architecture_card` e `sfx_priority_matrix`.

Apos 1f, a etapa 2 (arte) so pode ser aberta com Chain completo. Etapas 3 (runtime) e 4 (QA) seguem o pipeline AAA. A promocao a `ready_for_aaa` exige `audit_game_design_contracts_report.json` com `status=passed` (gerado por `tools/sgdk_wrapper/audit_game_design_contracts.ps1`).

### 2. Arte e composicao

Skills oficiais:

1. `art/art-asset-diagnostic`
2. `art/art-creation-sourcing` quando o diagnostico apontar `3_no_art`
3. `art/multi-plane-composition`
4. `art/scene-direction-curator` quando houver cenario competente, monumental, signature-only ou tecnica de plano
5. `art/art-translation-to-vdp`
6. `art/visual-excellence-standards`
7. `hardware/megadrive-vdp-budget-analyst`

Saida minima:

- laudos e artefatos de arte completos
- quando a cena nascer sem arte, `context_pack_manifest`, `master_style_manifest`, `art_generation_brief` e `asset_lineage_record` antes de qualquer promocao para `res/`
- arte premium aceita deve ser persistida em `data/source_art/` com `premium_source_manifest`; imagem inline pendente ou prompt sem arquivo nao entra em `res/`
- se a rota visual terminar em `blocked_image_tooling` ou `blocked_no_premium_source`, pare a producao visual antes do runtime; qualquer ROM posterior e apenas smoke test com `lab_not_delivery=true`
- `source_validity` precisa passar antes de `source_to_rom_visual_match`; se a fonte premium for clone, derivada indevida, benchmark-derived ou sem autoria, nenhum match visual aprova a promocao
- `clone_risk_score` e `benchmark_similarity_index` acima dos limites declarados pelo `authoriality_gate_report` ou `benchmark_profile` bloqueiam asset critico autoral
- asset critico so entra em `res/` com `elite_ready=true`; `needs_review`, `placeholder`, `debug_lab`, `benchmark-derived`, `rework` ou `perceptual_quality=nao_medido` bloqueiam promocao
- laboratorio visual deve declarar `lab_not_delivery=true` e nao pode ser vendido como entrega
- `local_author_pixel_rasterization`, `procedural_renderer` e scripts locais de desenho ficam restritos a `data/debug_lab/` e nao podem ser fonte final de asset critico AAA
- sprite heroico com gi branco ou tecido claro exige `white_material_palette_contract`: sombras frias azul/roxo, highlights limpos/quentes, distancia tonal minima e funcao declarada por slot; `PALETTE_WASTE` bloqueia visual delivery
- personagem heroico, lutador, boss, golpe, dano, smear, hitstop ou alegacao premium/AAA exige `animation_direction_contract`; golpes precisam de timing/spacing, anticipation, active, hitstop, follow-through e recovery; dano precisa de direcao de forca e quebra de postura; smear, flash e shading motion precisam de contratos proprios quando aplicaveis
- personagem novo ou alteracao de escala exige `visual_dna_manifest.scale_contract` travado; mudar escala depois de key poses exige reseed, nao resize silencioso
- material critico exige `material_color_ramp_plan` com hue shift ou justificativa; straight shading lavado bloqueia asset premium
- quantizacao automatica nao substitui palette pass manual
- decisao explicita `cabe`, `cabe com recuo` ou `nao cabe`
- quando o projeto ja tiver builder dedicado em `tools/image-tools/build_*.py` ou `doc/source_cases/**/case_manifest.json`, essa rota curada deve ser tentada antes de OCR, thumbnailing, crop manual ou lote generico
- quando houver UI formal, `ui_decision_card` coerente com ownership, budget e fallback
- quando houver UI pixel-perfect ou health bar, `ui_pixel_surface_contract` coerente com grid, atlas, fonte, budget e evidencia
- quando houver logo/title/front-end autoral, `brand_identity_manifest` coerente com GDD, `master_style_manifest`, leitura, budget e fallback
- quando houver tipografia relevante, o card tambem precisa ficar coerente com `font_render_mode`, `charset_profile` e `fallback_font_plan`
- quando houver texto expressivo, o card tambem precisa declarar `text_surface_class`, ritmo, ancoragem, audio, teardown e fallback
- quando houver transicao formal, `scene_transition_card` coerente com continuidade, camera, ownership, audio, teardown e fallback
- quando houver feedback FX, boss/setpiece, tilemap avancado ou audio senior, os cards precisam ficar coerentes com gameplay_signal, leitura, ownership, budget e fallback
- quando houver cenario monumental, `scene_direction_record` precisa consultar `scene_archetype_catalog.json`, escolher perfil, declarar tecnicas assinadas, fallback e funcao de gameplay/narrativa
- tecnicas de cenario exigem card especifico antes do runtime: `parallax_layer_contract`, `palette_cycle_decision_card`, `raster_fx_ownership_map` ou `background_ecology_card`
- quando houver mais de uma rota visual honesta, `route_exploration_board` + `route_decision_record` antes do runtime
- `qa_findings` e `correction_request` devem substituir raciocinio interno exposto quando uma geracao falhar por drift de estilo

Regra de curadoria AAA:

- explorar alternativas e permitido
- reabrir a direcao visual do zero a cada iteracao, nao e permitido
- consistencia de mundo vence asset isolado mais bonito
- banco vetorial e futuro opcional; em v1, `style_memory_index` em arquivo e a memoria auditavel
- a exploracao deve acontecer dentro do mesmo `shared_canvas_contract` e congelar uma `locked_visual_direction` escolhida pelo usuario ou recomendada pelo juiz estetico
- em cenas `aaa_layered`, a exploracao visual deve acontecer depois da comparacao com o baseline de `tilemap streaming guiado pela camera`, nunca no lugar dela
- `needs_review`, `placeholder`, `debug_lab`, `benchmark-derived`, `perceptual_quality=nao_medido`, `source_to_rom_visual_match < 8`, `source_validity=false`, `authoriality_gate!=passed`, `clone_risk_score` acima do limite declarado, `PALETTE_WASTE`, `model_sheet_to_sprite_fidelity_failed`, `signature_feature_loss`, `generic_blocky_redraw`, `blocked_image_tooling`, `blocked_no_premium_source`, `lab_not_delivery` ou `benchmark_match` abaixo de `benchmark_profile.required_match` bloqueiam `pronto`, `AAA`, `delivery` e `ready_for_aaa=true`
- ataque que comeca direto no active frame, sem recovery, com hitstop frame fraco, smear sujo, shading estatico ou hurt sem direcao de forca bloqueia `elite_ready` mesmo quando o PNG e o build estao limpos
- `budget_pass` e `visual_pass` sao eixos separados; se o runtime cabe com folga, budget nao pode ser usado como desculpa para arte pobre
- HUD de entrega nao pode parecer debug: precisa registrar `ui_attention_profile`, densidade alvo, hierarquia, area ocupada, contraste e interferencia no gameplay
- logo, title screen e front-end de entrega nao podem usar fonte generica/default como identidade final; precisam de `brand_identity_manifest`, testes de leitura e fallback
- cenario monumental nao pode ser decoracao sem leitura; `decorative_only_blocked`, `monumental_promised_without_budget`, `archetype_catalog_not_consulted`, `mode7_claim_on_megadrive`, `raster_fx_owner_collision` e `palette_cycle_ownership_conflict` bloqueiam `ready_for_aaa=true`
- cena ou produto que passa tecnicamente mas nao responde aos pilares aceitos do
  `creative_director_radar` deve receber `signature_gap` ou rebaixamento de
  claim ate GDD/spec/runtime evidenciarem a proposta

### 3. Integracao runtime

Skills oficiais:

- `code/sgdk-runtime-coder`
- `architecture/scene-state-architect`
- `operation/sgdk-build-wrapper-operator`

Saida minima:

- build limpo
- `runtime_decision_log`
- `runtime_animation_timing_map` quando houver golpes, dano, hitstop, flash, boss ou animacao premium
- `api_reality_check` citando header SGDK ou referencia local antes de usar API sensivel
- ownership de `WINDOW`, `H-Int` e FX de interface rastreavel quando houver UI formal
- runtime de health bar/UI pixel-perfect consome `ui_pixel_surface_contract`: pixels inteiros, atlas, fonte, buffer de dano e fallback
- ownership, paleta, superficie VDP, fallback e budget rastreaveis quando houver logo/title/front-end com `brand_identity_manifest`
- ownership de fonte, cache temporario de glifos e fallback_font_plan rastreavel quando houver anexo tipografico
- ownership de paineis, baloes, retratos, texto cinetico, SFX de texto e teardown rastreavel quando houver `text_presentation_profile`
- `runtime_state_handoff`, `teardown_reset_plan` e fallback rastreaveis quando houver transicao formal
- ownership, teardown e fallback rastreaveis para feedback FX, boss/setpiece, tilemap avancado e audio senior quando seus cards existirem
- ownership, teardown, fallback e downgrade rastreaveis para parallax, palette cycling, H-Int/raster, background ecology e foreground mutavel quando `scene_direction_record` existir
- active frames, recovery, hitstop, FX separado, flash frame e camera shake implementados de acordo com `animation_direction_contract` quando houver combate premium
- se houver audio declarado, `validation_report.json` deve refletir o estado de `audio_validation_report.json`; trilha de audio fora do validator principal nao fecha gate
- ROM gerada
- nenhum status de entrega visual AAA e promovido sem `visual_delivery_gate_report` limpo
- build limpo e BlastEm observado nao reduzem a exigencia visual; gate visual bloqueado continua bloqueado
- ROM que usa majoritariamente `VDP_drawText`, ASCII art, painel de nomes de efeito, `lab_bg_b` generico, fallback procedural repetido ou marcadores de debug e laboratorio deve ficar em `lab_not_delivery=true`; nao pode virar microfase AAA por narrativa em Markdown
- campanha de multiplas tecnicas/eixos deve passar por `tools/sgdk_wrapper/audit_effect_campaign_semantics.ps1` antes do closeout final; se o auditor emitir blocker, corrija a ROM ou rebaixe o status para rejeitado
- `validate_resources.ps1` deve bloquear `ready_for_aaa` quando `doc/technique_usage_manifest.json` estiver invalido, usar tecnica/tag fora do registry, declarar `LABORATORIO` em escopo de entrega, apontar evidencia fora do projeto ou deixar docs locais/freshness incompletos
- `blocking_statuses` nao vazio impede `ready_for_aaa=true`, mesmo que o blocker esteja em modo closeout-only ou que `summary.errors == 0`

### 4. Validacao e evidencia

Ferramentas e gates:

- `validate_resources.ps1`
- `validate_project_methodology.ps1`
- `freshness_audit.ps1`
- `scene_closeout_gate.ps1` no fechamento de cena
- `workflows/build-validate.md`
- BlastEm obrigatorio
- `doc/changelog`
- `doc/10-memory-bank.md`

Saida minima:

- `validation_report.json`
- `freshness_audit_report.json`
- `scene_closeout_gate_report.json` quando a cena for fechada
- `emulator_session.json`
- `qa_emulator_report.json`, `softlock_detection_report.json` e `runtime_fuzz_report.json` quando houver gate de entrega, regressao ou fuzz de runtime
- changelog atualizado
- memoria operacional coerente
- `creative_director_radar` atualizado quando o trabalho alterou personalidade,
  promessa, benchmark axis, momento assinatura ou gap aceito

Regra de promocao:

- se `runtime_metrics`, `scene_regression`, `emulator_session`, `validation_report` ou docs divergirem, corrija o ponto central e rode `freshness_audit.ps1` antes de promover status
- se o projeto reivindica vertical slice ou AAA, o radar criativo nao pode estar
  ausente, contradizer a ROM ou manter gaps assinatura aceitos sem plano
- se a cena for declarada entregue, `scene_closeout_gate.ps1` deve registrar build, contratos, grafo de recursos, validator, captura/regressao e freshness na mesma linha de evidencia
- se `scene_closeout_gate_report.json` ou `freshness_audit_report.json` apontar stale/falha, a cena volta para a etapa que gerou o drift
- se `validation_report.blocking_statuses` nao estiver vazio, o closeout final e `blocked` ou `failed`, nunca `ok` ou `pronto`

### 5. Iteracao

- triagem humana
- voltar para a skill da etapa afetada
- nunca corrigir no escuro sem registrar a classe real do erro
- em cenas `aaa_layered`, revisar primeiro se o erro e de contrato arquitetural antes de descer para depuracao residual de recurso, VDP ou sprite
- depois de registrar sucesso/falha real e gerar evidencias, executar `audit_project_learning.ps1 -Mode Capture`
- revisar o `candidate_index`; proposta de patch permanece `not_applied` e nao autoriza mudanca canonica

---

## Regras do Loop

- nenhum passo pode ser pulado
- assets nao validados nao entram no build
- budget nao e declarado por intuicao
- ROM nao testada nao e entregue
- ROM funcional com gate visual bloqueado continua sendo `buildado` ou `testado_em_emulador_com_visual_gate_blocked`, nunca `pronto`
- changelog nao e opcional
- memoria operacional nao substitui evidência
- aprendizado local pode ser atualizado automaticamente; alteracao canonica exige aprovacao humana, patch controlado e regressao
- BlastEm fecha gate de entrega
- freshness sem warnings bloqueantes e closeout registrado evitam falso verde
- FX de interface sem owner, teardown e fallback nao sobe
- UI pixel-perfect, health bar, fonte ou micro-icone sem contrato de grid/atlas/budget nao sobe
- menu/title screen segue a mesma barra AAA das cenas jogaveis e nao pode ser tratado como overlay funcional tardio
- transicao de cena sem `scene_transition_card`, causa dramatica, teardown e fallback nao sobe
- raster/luz/particula/boss/tilemap/audio sem card formal, owner, budget e fallback nao sobe
- logo/title/front-end sem manifesto de marca, leitura em escala e fallback nao sobe
