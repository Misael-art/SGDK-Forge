---
name: game-design-planning
description: Use quando um projeto SGDK estiver nascendo, quando o GDD/spec ainda nao derem conta do escopo atual, ou quando for preciso transformar nome + genero + fantasia + referencias + restricoes em briefing, seeds documentais e first playable slice antes de abrir arte ou runtime. Nao use quando a tarefa ja tem GDD/spec aprovados e o trabalho restante e apenas arte, budget, runtime ou validacao.
---

# Game Design Planning

Use esta skill para preencher o espaco entre intencao e producao.

Antes de usa-la, classifique o contexto via `workflows/project-opening.md`.

Regra:

- se for `projeto_existente`, esta skill nao deve reabrir briefing do zero sem pedido explicito
- se for `reseed` ou `projeto_novo`, esta skill vira a primeira superficie canonica antes de arte ou runtime

- `project_brief`
- `prd_readiness_report` ou `doc/prd_index.json` quando existir projeto local
- `core_loop_statement`
- `feature_scope_map`
- `scene_roadmap`
- `first_playable_slice`
- `route_decision_record` seed para o primeiro slice tecnico
- `front_end_profile`
- `creative_director_radar_seed`
- `brand_identity_seed` quando houver logo, title screen, press-start, menu principal ou front-end autoral
- `character_scale_seed` quando personagem, inimigo, lutador, boss ou avatar afetar FOV, hitbox, camera ou carga de animacao
- `ui_pixel_surface_seed` quando HUD/UI incluir health bar, fonte, caixa, micro-icone, cursor ou atlas pixel-perfect
- `technical_visual_audio_ambition`
- `technique_selection_seed`
- `scene_transition_card` seed quando houver troca de cena, zona, ato ou estado visual com peso dramatico/tecnico
- `cutscene_scene_contract` seed quando houver abertura, cena de contexto, final, briefing, painel narrativo ou retrato falante
- `production_runtime_contract` seed quando o alvo for jogo completo, AAA, stable, release ou projeto piloto
- `gdd_seed`
- `scene_spec_seed`
- `roteiro_scope`
- `mechanic_seed` (semeia o Chain de Producao canonico GDD->TDD->Mec->Level->Enemy->Audio->Art->Runtime->QA; ver `design/systems-mechanics-validator`)
- `level_design_seed` (semeia o `level_blueprint.json`; ver `design/level-design-canonical`)
- `enemy_roster_seed` (semeia o `enemy_roster.json`; ver `design/enemy-design-canonical`)
- `tdd_seed` (semeia o `tdd_contract.json`; ver `planning/tdd-authoring`)
- `adaptive_music_seed` (semeia o `adaptive_music_state_map.json` quando houver reacao do score a estado de gameplay; ver `code/xgm2-audio-director`)

Esta skill **nao auto-aprova o GDD**. Ela semeia e estrutura o projeto para a etapa humana de escopo.

---

## Entrada minima

- nome do projeto
- genero ou subgenero
- fantasia, tema ou fantasia-alvo
- referencias primarias
- plataforma alvo: Mega Drive / SGDK 2.11
- escopo desejado ou slice pretendido

Se ja existirem documentos canonicos, ler primeiro:

- `doc/11-gdd.md`
- `doc/13-spec-cenas.md`
- `doc/12-roteiro.md` quando houver narrativa
- `doc/10-memory-bank.md` quando houver historico real

Se o projeto ja existir e esses documentos sustentarem o escopo atual, prefira continuar a iteracao em vez de reseedar o planejamento.

---

## Saida minima

- `project_brief`
- `core_loop_statement`
- `feature_scope_map`
- `scene_roadmap`
- `first_playable_slice`
- `route_decision_record` seed
- `front_end_profile`
- `creative_director_radar_seed` com promessa autoral, eixos de benchmark, gaps
  propositivos, pilares assinatura e candidatos de cena memoravel
- `brand_identity_seed` quando houver logo, title screen, press-start, menu principal ou front-end autoral
- `character_scale_seed` quando personagem, inimigo, lutador, boss ou avatar afetar FOV, hitbox, camera ou carga de animacao
- `ui_pixel_surface_seed` quando HUD/UI incluir health bar, fonte, caixa, micro-icone, cursor ou atlas pixel-perfect
- `technical_visual_audio_ambition`
- `technique_selection_seed` com tecnicas escolhidas e rejeitadas/adiadas
- `scene_transition_card` seed quando houver transicao formal prevista
- `cutscene_scene_contract` seed quando houver cutscene prevista
- `production_runtime_contract` seed quando o alvo for jogo completo, AAA, stable, release ou projeto piloto
- `gdd_seed`
- `scene_spec_seed`
- `roteiro_scope`
- `mechanic_seed` (semeia `mechanic_contract.json`; usa o catalogo `mechanic_role_catalog.json`; 5 Leis Fundamentais; 5 Pilares: agency/feedback/flow/consistency/reward)
- `level_design_seed` (semeia `level_blueprint.json` + `level_design_report.json`; golden path + phase rhythm; reuse_map declarando mecanicas core)
- `enemy_roster_seed` (semeia `enemy_roster.json` + `enemy_design_report.json`; usa `enemy_ai_role_catalog.json` e `head_metric_reference.json`; boss exige XL)
- `tdd_seed` (semeia `tdd_contract.json`; scene manager, input abstraction, memory pool, VBlank/DMA ownership, region/timing, ROM mastering, code review, CI)
- `adaptive_music_seed` (semeia `adaptive_music_state_map.json` quando o score precisa reagir a gameplay; ver `code/xgm2-audio-director`)

### Mapeamento recomendado para docs

- `project_brief`, `core_loop_statement`, `feature_scope_map`, `front_end_profile`, `creative_director_radar_seed`, `brand_identity_seed`, `character_scale_seed`, `ui_pixel_surface_seed`, `technical_visual_audio_ambition` e `technique_selection_seed` -> `doc/11-gdd.md`
- PRDs de autonomia e escopo -> `doc/prd_index.json` + docs declarados no catalogo `tools/sgdk_wrapper/.agent/references/project_prd_catalog.json`
- `scene_roadmap`, `first_playable_slice`, `route_decision_record`, `scene_transition_card` seed, `cutscene_scene_contract` seed, `production_runtime_contract` seed, `scene_spec_seed`, `mechanic_seed`, `level_design_seed`, `enemy_roster_seed`, `tdd_seed` e `adaptive_music_seed` -> `doc/13-spec-cenas.md`
- `roteiro_scope` -> `doc/12-roteiro.md`

## Chain de Producao canonico (5 estagios)

Quando o alvo for `vertical_slice_candidate` ou alem, a `game-design-planning` deve semear os 5 seeds de design alem do GDD/PRD/roteiro, na ordem do pipeline machine-readable `tools/sgdk_wrapper/.agent/pipelines/game_production_v1.json`:

1. `tdd_seed` (S2) -> `tdd_authoring` skill produz `tdd_contract.json` com state_fsm_map, memory_pool_map, vblank_dma_ownership, h_int_ownership, audio_ownership, save_scope, region_timing_scope, rom_mastering_scope, risk_mitigation_table.
2. `mechanic_seed` (S3) -> `systems-mechanics-validator` skill produz `mechanic_contract.json` e `mechanic_validation_report.json` (5 Leis Fundamentais + 5 Pilares).
3. `level_design_seed` (S4) -> `level-design-canonical` skill produz `level_blueprint.json` e `level_design_report.json` (golden path, phase rhythm, reuse_map, breathing zones).
4. `enemy_roster_seed` (S5) -> `enemy-design-canonical` skill produz `enemy_roster.json` e `enemy_design_report.json` (6+ roles, head metric, telegraph, synergy).
5. `adaptive_music_seed` (S6) -> `xgm2-audio-director` skill (anexo adaptive music) produz `adaptive_music_state_map.json` quando o score reage a gameplay.

Apos S6, S7 reaproveita o `pipelines/aaa_scene_v1.json` por cena. S8 eh runtime (sgdk-runtime-coder). S9 eh QA (visual_gate, semantic_audit, rom-mastering, validate_resources, audit_game_design_contracts).

A promocao a `ready_for_aaa` exige `audit_game_design_contracts_report.json` com `status=passed`.

Regra:

- `front_end_profile` aqui e um **seed de planejamento**
- `creative_director_radar_seed` aqui e seed; antes de promover um projeto
  novo, reseed, vertical slice ou claim AAA, ele precisa virar
  `doc/creative_director_radar.json` validado contra
  `tools/sgdk_wrapper/schemas/creative_director_radar.schema.json`
- `brand_identity_seed` aqui e seed; antes de arte/runtime em logo, title screen, press-start, menu principal ou front-end autoral, precisa virar `doc/brand_identity_manifest.json` validado pelo schema `tools/sgdk_wrapper/schemas/brand_identity_manifest.schema.json`
- `character_scale_seed` aqui e seed; antes de key poses ou strips, precisa virar `visual_dna_manifest.scale_contract` com escala travada
- `ui_pixel_surface_seed` aqui e seed; antes de runtime de health bar/UI pixel-perfect, precisa virar `doc/ui_pixel_surface_contract.json`
- quando a iteracao tocar HUD/UI formal, ele deve ser formalizado depois via `ui_decision_card`
- em menu, title screen ou front-end, esse card usa `profile_kind=front_end_profile`
- `scene_transition_card` aqui nasce como seed; antes de arte/runtime, ele precisa virar contrato completo conforme `doc/03_art/14_contextual_scene_transition_system.md`
- `cutscene_scene_contract` aqui nasce como seed; antes de arte/runtime, ele precisa virar contrato completo via `cutscene-cinematic-direction`
- `production_runtime_contract` aqui nasce como seed; antes de fechar AAA/stable/release, ele precisa virar contratos reais de scene manager, input, save, region, ROM mastering, code review e CI/local CI
- antes de executar arte/runtime, rode `tools/sgdk_wrapper/check_prd_readiness.ps1`; PRD obrigatorio em `seed` e autoridade insuficiente, nao pergunta aberta

---

## Passa quando

- ha escopo fechado sem feature creep
- existe um `first_playable_slice` implementavel
- `doc/prd_index.json` declara quais PRDs sao obrigatorios, adiados ou `not_applicable`
- a ordem de cenas e o papel de cada uma estao claros o suficiente para handoff
- transicoes formais entre cenas, zonas, atos, menus ou cutscenes tem causa, controle do jogador e fallback declarados quando aplicavel
- cutscenes, aberturas e finais previstos tem objetivo dramatico, cenas/estados, speaker roster, ritmo de texto e evidencia esperada declarados
- se o alvo for jogo AAA/stable/release, scene manager, input abstraction, save/SRAM, PAL/NTSC, ROM mastering, code review e CI/local CI aparecem como escopo de entrega ou como blockers declarados
- menu, title screen e front-end ja tem papel declarado quando aplicavel
- projeto novo, reseed ou slice ambicioso possui radar propositivo: promessa
  autoral, eixos de benchmark, lacunas de personalidade, propostas priorizadas,
  docs alvo, owner skill, evidencia e fallback; benchmark e qualidade-bar, nao
  comando de copia
- logo, fonte de identidade e title/front-end autoral ja tem papel, teste de leitura, fonte custom/fallback e estrategia runtime declarados quando aplicavel
- escala de personagem ja declara impacto em FOV, hitbox, camera, carga de animacao e necessidade de travamento quando aplicavel
- health bar/UI pixel-perfect ja declara grid inteiro, atlas, fonte, buffer de dano e evidencia esperada quando aplicavel
- o primeiro slice tem `route_decision_record` suficiente para escolher skill, ferramenta e familia tecnica antes de asset/runtime
- arte, runtime e budget conseguem trabalhar sem adivinhacao de objetivo
- GDD declara barra tecnica, visual, sonora e de jogabilidade sem prometer recurso inexistente
- toda tecnica escolhida cita registry ID/tags, funcao no jogo, owner, budget/evidencia e fallback
- tecnicas rejeitadas ou adiadas possuem motivo; tecnica sem funcao nao entra apenas para aumentar contagem de FX

---

## Handoff para proxima etapa

- `art/art-asset-diagnostic`
  - quando a producao for seguir por descoberta de assets
- `art/multi-plane-composition`
  - quando a cena inicial ja estiver escolhida e precisar de desenho de planos
- `operation/sgdk-build-wrapper-operator`
  - quando o projeto estiver sendo bootstrapado ou reestruturado no wrapper

---

## Processo canonico

### 1. Congelar a promessa do projeto

Definir:

- o que o jogo e
- o que o jogo nao e
- qual fantasia ele promete no primeiro contato
- qual experencia precisa existir no primeiro slice jogavel
- qual momento assinatura deve fazer o jogador lembrar do projeto
- quais aspectos nao podem parecer genericos, mesmo que estejam funcionais

Emitir tambem o `creative_director_radar_seed`:

- `project_promise`: promessa em uma frase, sentimento alvo, identidade nao
  generica e teste dos primeiros 10 segundos
- `benchmark_axis_matrix`: referencias por eixo, qualidade herdavel, traducao
  autoral, fronteira de nao-copia e metrica de evidencia
- `signature_pillars`: 3 a 7 pilares que precisam aparecer em mecanica,
  level, audio, visual, front-end ou setpiece
- `proactive_gap_radar`: oportunidades que o agente percebe sem esperar o
  usuario pedir, sempre com docs alvo, owner skill, prioridade e fallback
- `signature_scene_candidates`: pelo menos um momento de cena que combine
  payoff jogavel, visual, sonoro e tecnico

Regra: o agente deve propor. Ele nao deve inserir feature nova no escopo sem
decisao humana ou GDD/spec ja autorizando.

### 2. Fechar o loop central

Emitir um `core_loop_statement` simples:

`acao principal -> feedback -> risco -> recompensa -> repeticao`

Se o loop nao couber em uma frase curta, o projeto ainda esta difuso.

### 3. Cortar escopo cedo

Emitir `feature_scope_map` com tres classes:

- `entra_no_slice`
- `entra_depois`
- `fora_de_escopo`

Nao promova backlog futuro como se fosse parte do escopo atual.

### 4. Planejar front-end desde o inicio

Se houver menu, title screen ou front-end:

- declarar `front_end_profile`
- declarar `brand_identity_seed` quando houver logo, press-start, fonte display custom ou identidade autoral
- dizer qual fantasia ele comunica
- dizer qual movimento/vida existe em idle
- dizer qual feedback de selecao existe
- dizer como o logo e as fontes comunicam genero, tom e mecanica sem perder legibilidade
- registrar que fonte default/generica e permitida apenas como debug, prototipo ou fallback, nunca como identidade final
- dizer o que seria fora de tom

Menu e title nao sao apendice tardio.

### 5. Fechar o first playable slice

O slice inicial deve responder:

- qual cena o jogador ve primeiro
- qual acao principal ele executa
- qual feedback prova que o jogo funciona
- quais sistemas ficam de fora nesta primeira entrega

Se o slice for anunciado como AAA/stable/release, ele nao pode deixar fora:

- scene manager deterministico
- input abstraction
- save/SRAM quando houver persistencia
- region/timing PAL/NTSC
- ROM mastering
- code review formal
- CI/local CI gate

### 6. Abrir o roadmap de cenas

Emitir `scene_roadmap` com:

- ordem de aparicao
- papel da cena
- objetivo no slice
- dependencia principal
- transicao de entrada/saida quando ela carregar geografia, ritmo, causa narrativa ou tecnica especial

Se a cena inicial ainda nao estiver clara, nao abrir runtime.

### 7. Emitir o route decision record inicial

Antes de abrir arte, conversor ou runtime, emitir um `route_decision_record` seed para a primeira cena/slice:

- `dominant_route`: `planning | art_diagnostic | source_translation | curated_builder | conversion_batch | scene_architecture | budget | runtime | validation`
- `first_skill`: skill que deve ser usada primeiro
- `first_tool`: ferramenta ou script canonico esperado, quando existir
- `resource_loading_model`: `full_resident`, `scene_local_preload`, `tilemap_streaming`, `animation_window_streaming` ou `fallback_reduced_residency`
- `asset_strategy`: fonte de assets, builder esperado, ou motivo para diagnostico antes de converter
- `evidence_required`: prova minima antes de promover a etapa
- `forbidden_shortcuts_until_evidence`: atalhos bloqueados ate a rota ser provada

Regra de inteligencia: este registro nao e burocracia. Ele impede que projeto novo comece por tentativa local quando ja existe skill, builder, manifesto, baseline interno ou ferramenta canonica.

### 8. Delimitar narrativa

Quando houver historia, `roteiro_scope` deve dizer:

- quais cenas/telas precisam de texto neste slice
- qual tom geral
- se o texto e leitura simples ou precisa de painel, balao, retrato, hype text, typewriter voice ou flavor text
- o que fica fora por enquanto

Nao abrir dialogo aprovado sem saber em que slice ele cabe.
Nao abrir texto expressivo sem `text_presentation_profile` quando ele tiver peso dramatico, diegetico ou cinetico.

Quando houver abertura, cutscene, briefing, final ou cena de contexto, o planejamento tambem deve emitir um seed de `cutscene_scene_contract` com:

- lista de cutscenes no slice
- objetivo dramatico de cada cena
- formato dominante: `panel_sequence`, `portrait_dialog`, `pan_hold`, `object_insert`, `full_screen_justified` ou `mixed`
- roster de falantes e tom de voz
- quantidade maxima de shots/estados
- modelo de avanco: input, timer, texto concluido ou misto
- budget de texto e glyph subset previsto
- referencia visual herdada por jogo, sem copiar tecnologia de plataforma nao-SGDK
- requisito inicial de evidencia em BlastEm

Sem esse seed, a cutscene fica `documentado`, nao pronta para arte ou runtime.

### 9. Delimitar runtime de producao

Quando o objetivo for jogo completo, AAA, stable, release ou projeto piloto, emitir `production_runtime_contract` seed com:

- `scene_manager_scope`
- `input_abstraction_scope`
- `persistence_scope` e `save_system_scope` quando `required` ou `optional`
- `region_timing_scope`
- `rom_mastering_scope`
- `code_review_scope`
- `ci_gate_scope`
- `asset_optimization_scope`

Se persistencia for `none`, declarar `save_system_contract_not_applicable`. Se for `required`/`optional` e ficar fora do slice, declarar blocker ou `futuro_arquitetural`. Nao esconder como detalhe tecnico.

---

## Anti-padroes

- pular de pitch para runtime
- tratar ausencia de PRD como permissao para improvisar decisao criativa bloqueante
- tratar GDD como texto bonito sem corte de escopo
- colocar menu/title fora do planejamento inicial
- confundir wishlist com `feature_scope_map`
- escrever `scene_spec_seed` sem `first_playable_slice`
- abrir arte sem cena inicial escolhida
- abrir cutscene por prompt visual sem `cutscene_scene_contract` seed
- chamar projeto de AAA/stable/release sem `production_runtime_contract` seed
- abrir conversao de imagem, OCR/crop manual, `resources.res` ou runtime sem `route_decision_record` quando a rota tecnica ainda nao estiver declarada
- abrir arte/runtime sem semear TDD, mecanica, level, enemy e audio adaptativo quando o alvo for `vertical_slice_candidate` ou `ready_for_aaa`

---

## Saida esperada

Quando responder usando esta skill, entregar algo suficientemente concreto para popular os docs canonicos com:

- `project_brief`
- `core_loop_statement`
- `feature_scope_map`
- `scene_roadmap`
- `first_playable_slice`
- `route_decision_record`
- `front_end_profile`
- `creative_director_radar_seed`
- `brand_identity_seed` quando houver logo, title screen, press-start, menu principal ou front-end autoral
- `character_scale_seed` quando houver escala de personagem com impacto mecanico
- `ui_pixel_surface_seed` quando houver health bar/UI pixel-perfect de entrega
- `scene_transition_card` seed quando houver transicao formal
- `cutscene_scene_contract` seed quando houver abertura, cutscene, cena de contexto ou final
- `production_runtime_contract` seed quando o alvo for jogo completo, AAA, stable, release ou projeto piloto
- `roteiro_scope`
- `mechanic_seed` quando o alvo for `vertical_slice_candidate` ou `ready_for_aaa`
- `level_design_seed` quando o alvo for `vertical_slice_candidate` ou `ready_for_aaa`
- `enemy_roster_seed` quando o alvo for `vertical_slice_candidate` ou `ready_for_aaa`
- `tdd_seed` quando o alvo for `vertical_slice_candidate` ou `ready_for_aaa`
- `adaptive_music_seed` quando o score reage a estado de gameplay

Se faltar algum desses blocos, o planejamento ainda esta parcial.
