# 06 - AI Memory Bank (MegaDrive_DEV)

**Última atualização:** 2026-08-29
**Escopo:** Repositório MegaDrive_DEV (workspace global)
**Projeto em foco:** Barra viva da cena (oficio Rheo/Pigsy como piso, nao handle), plano para gerar pixel art nesse nivel, SGDK_GLOBAL §39

> **DIRETRIZ:** Este é o bloco de memória primário para o workspace global.
> Leia integralmente antes de decisões que afetem múltiplos projetos.
> Atualize ao encerrar sessões relevantes.

---

## 1. ESTADO ATUAL DO REPOSITÓRIO

### Build e validação
- **Wrapper centralizado:** `tools/sgdk_wrapper/` — única fonte de verdade para build, clean, run.
- **Validação:** `validate_resources.ps1` gera `validation_report.json` em `out/logs/`.
- **Loop detector (2026-06-06):** `detect_operational_loop.ps1` foi integrado ao `tools/sgdk_wrapper/build.bat`; bloqueia build apenas com 3 reports consecutivos com os mesmos blockers e destrava apenas com `doc/operational_loop_decision.json` valido.
- **Tool-first audit (2026-06-06):** `audit_tool_first.ps1` agora exige fixture executado ou `fixture_skip_reason` (skip ainda bloqueia uso canonico); `tools/mugen2sgdk` permanece `legacy_gui_tool_without_cli` ate auditoria real.
- **Evidence root gate (2026-06-06):** `audit_evidence_root.ps1` passou a bloquear paths absolutos fora do projeto em reports, exceto quando registrados em `doc/project_hygiene_manifest.json` como `external_inputs` com copia em `rascunho/` + sha256.
- **Orphan subproject gate (2026-06-06):** `audit_orphan_subproject.ps1` exige agregacao no root do estudo (manifesto `.mddev/project.json` com `nested_viewers`, memory bank, changelog, link, evidencia/lab e fechamento).
- **Art diagnostic output (2026-06-06):** `art_diagnostic.py` e ASCII-safe por default; `--unicode` e opcional e nenhum gate depende dele.
- **Curadoria cena/tilemap (2026-06-06):** conversão de cenário não pode ser "aprovada" sem reports estruturais (dedup/HV flip, flags, sub-paletas) e schema válido; enforcement é closeout/delivery (warning fora do closeout).
- **Scripts de projeto:** build.bat, clean.bat, run.bat delegam ao wrapper (2–3 níveis `..` conforme profundidade).
- **13/13 projetos compiláveis** geram ROM com sucesso (AGENTS.md).

### Projetos principais
| Projeto | Tipo | Memory Bank próprio |
|---------|------|---------------------|
| Pequeno Príncipe Cronicas das Estrelas | GAME [AVENTURA] | `doc/10-memory-bank.md` |
| Shadow Dancer Hamoopig | ENGINE [PLATAFORMA] | — |
| BLAZE_ENGINE | ENGINE [BRIGA DE RUA] | — |

---

## 2. O QUE ACABOU DE ACONTECER (2026-04-02)

### Barra viva da cena — oficio Rheo/Pigsy como piso (2026-08-29)

- Piso visual 2026 canonizado: `doc/03_art/18_live_scene_bar.md` +
  `doc/03_art/live_scene_bar.json` + schema
  `tools/sgdk_wrapper/schemas/live_scene_bar_report.schema.json`.
- Handles `RheoGamer` / `PigsyRetro` decodificados em axiomas (R1-R10,
  P1-P10) e 12 checks binarios. Expansao 2026-08-29b: Pyron (Y1-Y3 palco
  ~980 tiles), Chev (C1-C4 segundo passe / 320x224), Diggo (D1-D3 chip
  identity), MXRetroDev carta FFMD (M1-M4 paleta de roster), Shannon 3D
  Update 8 (S1-S5 DMA/inversao/FPS), Daniel Moura HAMOOPIG (H1-H5).
  Citar o nome sem o oficio e `name_drop_without_craft`. Pixels/PCM dos
  ports deles sao `clone_risk`.
- 2026-08-29c: tetos em `live_scene_bar_parameters.json`. G1/G2, D4, Z1, S6.
  Nao duplicar ensaio. XGM2 nao e automaticamente mais leve sob DMA alto.
- Tese: VRAM/CRAM sao a primeira decisao de arte; sem decisao artistica
  o hardware produz lixo; fonte de outra plataforma nao se quantiza cega.
- Amarra: AGENTS.md, SGDK_GLOBAL §39, `00_visual_quality_bar.md`,
  visual-excellence-standards, art-creation-sourcing (prompts de fonte,
  nao de sprite sheet MD), art-translation-to-vdp, aaa-pipeline-guardian,
  benchmark_usage_policy, radar, modelo `00-diretrizes-agente.md`.
- Plano de capacidade: `doc/03_art/19_plan_pixel_art_live_scene_capability.md`.
  `runtime_proof_status` desta barra: `PARCIAL_LAB`. F-R2 fase 1 teve ROM
  com paletas de papel (R2) mas sprites em downscale. F-R2 fase 2
  (2026-08-29d) redesenhou heroi/thug em lineart 1 px nativo 48x64;
  ROM `4c07c842…f5642d` vista no BlastEm. Nao e `visual_pass`. Cais
  ainda quantize; cor ainda nao comecou. Nao declarar que o Forge ja
  gera no piso Rheo/Pigsy.
- Prompts "pixel art sprite sheet Mega Drive" na Rota A foram substituidos
  por concept high-res; fake pixel art do gerador e rejeicao, nao input
  de quantize.

### Doutrina de capacidade com prova e Ramo C de roteamento visual (2026-08-25)
- Criada `SGDK_GLOBAL.md` §38: sonda real obrigatoria antes de prometer capacidade; vocabulario `capaz_com_prova_agora` / `capaz_apos_preparo_medido` / `nao_capaz_neste_host`; proibido claim por memoria, fama do modelo ou suposicao.
- `image-generation-routing` agora abre com a arvore obrigatoria de 3 ramos: A (nativo com prova -> gerar), B (host preparado -> circuito local), C (nem agente nem host -> emitir `successor_asset_directive`). Bloqueio morto sem diretriz e anti-padrao.
- Novo contrato machine-readable: `tools/sgdk_wrapper/schemas/successor_asset_directive.schema.json` + template `tools/sgdk_wrapper/.agent/references/successor_asset_directive_template.md`.
- **Protocolo de insatisfacao mensuravel** (`successor_quality_protocol`, "prompt magico" do Ramo C): min_rounds=3, pisos numericos com ferramenta (luma>=34, paleta 9-bit, silhueta B/N, grid 8px/index 0, dithering funcional), rejeicoes automaticas, `blind_critic_floor` default **8.5/10**, julgamento final ancorado em gates imparciais — o gerador nao aceita primeira versao nem se auto-satisfaz; lacuna nao resolvida e declarada honestamente (§38), nunca piso rebaixado.
- **Prompt modelo de direcionamento**: criado `doc/prompts_modelo/prompt_modelo_direcionamento_projeto.md` (v1.0.0) — contrato para reconciliar mega-prompts externos: 8 correcoes com gate provado, prompt magico embutido, esqueleto F0-F3 do modelo/, registro de incrementos com regras de auto-incremento; ponteiro na REFERENCIA RAPIDA do AGENTS.md.
- Drift curado: 7 schemas citados como canonicos pela skill e inexistentes em disco foram criados em `tools/ai_imagegen/reports/schema/`; path errado no tdd-authoring corrigido; `validate_skill_framework.py` agora reprova skill que cita path ancorado (`tools/...`, `.agent/...`) inexistente (calibrado contra falso positivo conforme §37); `imagegen_tool.py self-check` novo (PASS).
- Prova viva neste host (Linux, AMD VanGogh sem VRAM dedicada, 2.8GB RAM livres, ComfyUI/modelos ausentes): sondas reais -> `nao_capaz_neste_host`, desfecho Ramo C com artefatos schema-validos em `out/logs/generation_channel_decision.json`, `out/logs/successor_asset_directive_2026-08-25.json` (aponta para a spec real do GOTHAM_OVERDRIVE, ja com protocolo embutido) e `out/logs/tooling_capability_report.json`.
- Detalhe completo: `doc/agent_learning/changelog_2026-08-25.md`.

### Pontes de IDE e skills canonicas (2026-06-06)
- `.agents/skills` foi convertido de junction absoluta para symlink relativo apontando para `../tools/sgdk_wrapper/.agent/skills`.
- `.trae/skills` deixou de ser arvore isolada e agora tambem aponta por symlink relativo para a mesma fonte canonica.
- Graphify foi integrado de forma conservadora como indice consultivo (nao fonte de verdade):
  - wrapper: `tools/sgdk_wrapper/graphify_forge.ps1` (build/update/query/report + freshness/stale)
  - startup comum: `tools/sgdk_wrapper/assert_agent_environment.ps1` chama `prepare_agent_environment.ps1 -InstallMissing` automaticamente
  - workflow: `tools/sgdk_wrapper/.agent/workflows/agent-startup-environment.md`
  - report: `graphify-out/AGENT_ENVIRONMENT_REPORT.json`
  - concorrencia: `prepare_agent_environment.ps1` usa lock global para evitar disputa de cache quando varios agentes atualizam Graphify ao mesmo tempo
  - escopo: `.graphifyignore` limita a `tools/sgdk_wrapper/.agent/`, `doc/05_technical/`, `doc/07_game_design/` e `doc/06_AI_MEMORY_BANK.md`
  - auditoria de escopo: grafo/queries com fontes fora do escopo geram `graph_scope_violation` e bloqueiam `query`; correcao e `-Action build`
  - outputs: `graphify-out/` e gerado/cache e fica fora do Git
  - Obsidian e cockpit humano opcional; `.obsidian/` nao deve ser versionado
  - politica: `doc/GRAPHIFY_OBSIDIAN_POLICY.md`
- `.cursor`, `.serena`, `.superpowers`, `.trae`, `.agents` e `.claude` agora apontam para o mesmo preparo de ambiente e para Graphify apenas via wrapper/pwsh.
- Camada `ai-memory` integrada de forma complementar e controlada (2026-06-23):
  - wrapper: `tools/sgdk_wrapper/prepare_ai_memory_integration.ps1`
  - politica: `doc/AI_MEMORY_POLICY.md`
  - marcador raiz: `.ai-memory.toml` com `workspace = "sgdk_forge"` e `project = "workspace"`
  - report: `out/logs/ai_memory_integration_report.json`
  - `assert_agent_environment.ps1` agora prepara a camada junto do bootstrap comum
  - `adopt_project_methodology.ps1` cria marcador `.ai-memory.toml` dentro do projeto quando possivel
  - regra: ai-memory e consultivo, nao instala hooks/MCP globais automaticamente, nao roda bootstrap/auto-improve, nao substitui memory bank, learning ledger, Graphify, validators, changelog ou evidencia BlastEm
  - auto-improvement deve permanecer pendente de revisao humana (`require_approval=true`) e scheduler deve ficar desabilitado durante piloto
- Resiliencia de bootstrap Graphify (2026-06-23):
  - `tools/sgdk_wrapper/graphify_forge.ps1` agora aceita `-GraphifyTimeoutSeconds`
  - chamadas `build`, `update` e `query` executam `graphify` em processo controlado
  - bloqueio de Windows App Control vira `graphify_start_failed` em vez de stack trace solto
  - timeout vira `graphify_timeout` e nao deixa o agente esperando indefinidamente
  - `prepare_agent_environment.ps1` repassa o timeout e registra `graphify.timeout_seconds` no report
- `show_agent_menu.ps1` chama o guard de ambiente automaticamente, com opt-out explicito `SGDK_SKIP_AGENT_ENVIRONMENT_GUARD=1`.
- A skill reaproveitavel `tiled-hybrid-parallax-curator` foi promovida para `tools/sgdk_wrapper/.agent/skills/art/` com contrato operacional e metadados OpenAI.
- `.serena/project.yml` passou a indexar tambem Python, PowerShell, JSON e Markdown, mas ignora caches, SDK, emuladores e outputs pesados.
- `.claude`, `.cursor`, `.pytest_cache` e `.superpowers` foram mantidos como estado/configuracao especifica de ferramenta; nao sao fonte canonica de skills.

### Curadoria de camera 2D e game feel (2026-06-06)
- O material colado sobre camera 2D foi assimilado como curadoria secundaria em `doc/05_technical/curation_sources/2026-06-06_2d_camera_behavior_text.txt`.
- Foi criado `tools/sgdk_wrapper/schemas/camera_behavior_contract.schema.json` e o exemplo canonico `tools/sgdk_wrapper/.agent/references/agentic_aaa_contracts/examples/camera_behavior_contract.json`.
- `camera_scroll_management` continua `TEORICA_PRIORITARIA`, agora com exigencia de deadzone/lookahead/smoothing/clamp/triggers/shake/culling e snap final em pixels inteiros quando a camera afetar gameplay.
- `game-design-planning`, `level-design-canonical`, `tdd-authoring`, `scene-state-architect`, `sgdk-runtime-coder` e `systems-mechanics-validator` passaram a consumir camera como contrato de gameplay, nao como detalhe decorativo.
- Nenhuma tecnica de camera foi promovida para `MESTRE_*`; promocao continua exigindo ROM, BlastEm, budget, evidencia de movimento e aprovacao humana.

### Curadoria de direcao sonora Mega Drive (2026-06-06)
- O material colado sobre arquitetura sonora retro foi assimilado como curadoria secundaria em `doc/05_technical/curation_sources/2026-06-06_retro_audio_architecture_text.txt`.
- `audio_architecture_card` agora aceita `sound_chip_identity_plan` para declarar escola sonora alvo, paleta de timbres FM, papel do PSG, uso de DAC/PCM, politica de traducao de referencias e suposicoes proibidas.
- A skill `xgm2-audio-director` passou a exigir traducao de referencias SNES/orquestrais para papeis reais de YM2612/PSG/DAC, sem assumir echo nativo, sample RAM ampla ou trilha sample-heavy sem budget.
- Foi registrada `ym2612_fm_timbre_design` como `TEORICA_PRIORITARIA`: o agente entende a tecnica e deve planejar timbres FM, mas nao ha promocao para `MESTRE_*` sem ROM, BlastEm, audio limpo, ownership, budget e aprovacao humana.
- Nenhum conhecimento deste lote foi tratado como prova operacional; o ganho e direcional/metodologico para impedir musica generica e escolhas sonoras incompativeis com o Mega Drive.

### Gate ai_imagegen personagem e rebaixamento do canal local para AAA (2026-05-23)
- O gate `out/gates/ai_imagegen_character_test/` gerou quatro candidatos com `tools/ai_imagegen/` (`deck_safe_sd15`, 384x512, 20 steps).
- O melhor candidato (`seed 34567`) corrigiu apenas a falha extrema anterior de imagem indecifravel: existe leitura minima de cabeca, tronco, bracos e pernas.
- A qualidade visual continua longe de um asset AAA de jogo: composicao pobre, escala ruim, cenario/moldura contaminando a fonte e baixa direcao artistica.
- Decisao consolidada: `tools/ai_imagegen` no host atual fica como fallback tecnico/laboratorio/prova de canal, nao como caminho padrao para fonte premium.
- Para personagem, boss, HUD heroico, cena identitaria ou asset AAA, o agente deve preferir seu recurso proprio/nativo de geracao de imagem quando disponivel.
- Qualquer resultado local apenas "legivel" deve ser marcado como `reprovado_como_fonte_AAA` ou `aceito_apenas_como_prova_tecnica`, nunca como `fonte_premium_aprovada`.

### Telas padrao de assinatura incorporadas ao modelo (2026-05-23)
- O modelo canonico em `tools/sgdk_wrapper/modelo` passou a nascer com `APP_SCENE_BRANDING` antes do boot/menu.
- A sequencia padrao tem tres slots obrigatorios: tela engine, tela autor e tela projeto.
- Implementacao atual e `placeholder_runtime_structure`: texto/efeitos procedurais e PSG simples, sem assets finais de marca.
- Prompt mestre para agentes: `tools/sgdk_wrapper/modelo/doc/15-prompt-telas-assinatura.md`.
- Contrato machine-readable: `tools/sgdk_wrapper/modelo/doc/branding_sequence_contract.json`.
- Compilacao direta via SGDK make gerou `tools/sgdk_wrapper/modelo/out/rom.bin`; wrapper estrito ainda bloqueia por gate de governanca preexistente (`local_agent_physical`/`res_graph_report.json` ausente), portanto nao declarar `pronto` nem `testado_em_emulador`.

### Reconciliacao do diagnostico AAA externo (2026-04-10)
- O diagnostico externo de gaps AAA foi aceito parcialmente como disciplina de canonizacao, mas NAO como roadmap literal.
- Foi criado o protocolo-meta `doc/03_art/AAA_SKILL_CANONIZATION_PROTOCOL.md` para reger canonizacao de skills artisticas e tecnicas sem substituir protocolos especializados.
- `doc/03_art/04_art_translation_curation_protocol.md` permanece como protocolo especializado de `art-translation-to-vdp`.
- `doc/03_art/AAA_SKILL_CURATION_STATUS.md` passou a operar com dois eixos obrigatorios:
  - `doctrine_status`
  - `runtime_proof_status`
- Sprint 1 foi preservada como `INCORPORADO` em doutrina, sem ser promovida artificialmente para prova em ROM.
- `S5.1` Forward Kinematics e `S5.2` XGM2 Audio Architecture foram aceitas como backlog oficial futuro, ambas ainda bloqueadas antes de Fase 1.
- Regra consolidada para drafts de Sprint 2+: citar `92_frontdoor`, depois `92_registry`, e usar `99_appendix` apenas como evidencia bruta.
- Decisao consolidada: nao duplicar skills ja existentes (`sprite-animation`, `character-design`, `multi-plane-composition`) nem recriar docs que ja existem e devem ser revisados in place.

### Matriz de maestria hardware-level 16-bit (2026-04-10)
- Criada a nova camada de dominio em `doc/05_technical/93_16bit_hardware_mastery_matrix.md`, `doc/05_technical/93_16bit_hardware_mastery_registry.json` e `doc/05_technical/94_16bit_hardware_mastery_roadmap.md`.
- A nova camada NAO substitui `92_frontdoor` nem `92_registry`; ela organiza a maestria por tecnica e por owner skill.
- Estado consolidado do agente:
  - `incorporated`: tile flipping, DMA safety basico, sprite timing/pivot, multi-plano basico, budget VDP basico
  - `candidate_with_evidence`: line scroll, H-Int palette split, pseudo-3D road stack, priority split foreground, tile cache streaming
  - `partial`: column scroll, Shadow/Highlight como trilha dedicada, palette cycling formal, CRT-aware dithering, sprite multiplexing, BG_B bypassing, slot rule de S/H
  - `gap_pure`: forward kinematics, XGM2 audio
- Decisao consolidada: nao criar skills novas para tecnicas que ainda podem amadurecer dentro de `sgdk-runtime-coder`, `megadrive-vdp-budget-analyst`, `multi-plane-composition`, `visual-excellence-standards`, `sprite-animation` e `character-design`.
- Skills novas justificadas imediatamente:
  - `forward-kinematics-rigging`
  - `xgm2-audio-director`
- O `BENCHMARK_VISUAL_LAB` continua sendo o unico laboratorio oficial de prova. Nenhuma tecnica nova sobe acima de `blastem_proven` sem scene dedicada, budget line e evidence bundle rastreavel.

### Reconciliacao dos efeitos lendarios na malha de maestria (2026-04-10)
- `H-Int` deixou de existir apenas como restricao de budget e passou a ser tratado como substrato formal via `h_int_control_plane`.
- `mid-frame palette swap` foi explicitamente absorvido como alias visual de `hint_palette_blending`; nao virou trilha separada.
- `pseudo-3D` foi dividido em duas trilhas distintas:
  - `pseudo3d_road_stack`
  - `software_affine_pseudo3d`
- `Window Plane` entrou na matriz como competencia formal de HUD e arquitetura de display:
  - `window_plane_static_hud`
- `window alias` permanece tecnica avancada e nao-default; nunca deve ser confundida com uso normal da `WINDOW`.
- `interlaced_448_display_mode` entrou no core roadmap de maestria, mas com politica operacional `special_scene_only`.
- `sprite multiplexing` deixou de ser categoria unica e passou a ser dividido em:
  - `sprite_temporal_multiplexing`
  - `sprite_midframe_sat_reuse`
- `sprite_midframe_sat_reuse` depende formalmente de `h_int_control_plane` e ficou classificado como trilha futura perigosa.
- O contrato do `BENCHMARK_VISUAL_LAB` foi endurecido para exigir:
  - `intencao_da_cena`
  - `signature_moment`
  - `causa_de_gameplay`
  - `secondary_fx_pairings`
  - `hint_owner`
  - `operational_policy`
  - `budget_line`
- Decisao consolidada:
  - nao criar skill nova para H-Int, Window Plane, interlaced, palette split ou pseudo-3D road-stack
  - novas skills continuam restritas aos gaps puros ja aceitos (`forward-kinematics-rigging` e `xgm2-audio-director`)

### Avaliacao honesta de efeitos especulativos modernos (2026-04-10)
- Quatro propostas especulativas de "efeitos modernos no Mega" foram reconciliadas com nomes honestos e limites claros de hardware.
- Ranking consolidado de viabilidade:
  1. `procedural_raster_glitch_suite`
  2. `masked_shadow_highlight_lighting`
  3. `mutable_tile_decal_mutation`
  4. `cellular_microbuffer_sim`
- Decisoes consolidadas:
  - `procedural_raster_glitch_suite` e altamente viavel como combinacao dirigida de `line scroll`, `palette shock`, `WINDOW` e leitura dramatica sob controle
  - `masked_shadow_highlight_lighting` e viavel como ilusao forte de spotlight/lanterna, mas NAO equivale a iluminacao dinamica moderna nem a alpha blending
  - `mutable_tile_decal_mutation` so e honesto como dano persistente local por `RAM shadow copy` + `mutable tile pool`; VRAM nao deve ser tratada como framebuffer livre
  - `cellular_microbuffer_sim` so e honesto como microframebuffer local em ilha pequena; NAO equivale a sandbox global estilo Noita
- Alocacao no framework:
  - `procedural_raster_glitch_suite` entra em `S2.1`
  - `masked_shadow_highlight_lighting` entra em `S2.2`
  - `mutable_tile_decal_mutation` vira trilha futura `T3`
  - `cellular_microbuffer_sim` vira trilha futura tardia `T4`
- Benchmarks oficiais reservados:
  - `fx_procedural_glitch_lab`
  - `fx_masked_light_lab`
  - `fx_decal_mutation_lab`
  - `fx_cellular_microbuffer_lab`
- Regra consolidada: nenhum desses quatro efeitos existe no framework sem ROM, BlastEm, budget aprovado e aprovacao humana.

### Assimilação do engine scan pass 2 (2026-04-10)
- Criado o front door canônico em `doc/05_technical/92_sgdk_engine_pattern_frontdoor.md` para resolver a ambiguidade de "pass 2 sem pass 1".
- Criado o registry machine-readable em `doc/05_technical/92_sgdk_engine_pattern_registry.json` com classificação explícita: `verified_example`, `interpreted_pattern`, `candidate_for_canon`, `blocked_pending_repro`.
- `doc/05_technical/99_sgdk_engines_scan_appendix.md` foi rebaixado semanticamente para `appendix / raw extraction log`; continua preservado, mas não funciona como registro canônico.
- A skill `sgdk-runtime-coder` e `references/pattern_catalog.json` passaram a apontar para o registry como fonte de padrões candidatos, sem promover scan para canon por inércia.
- `tools/sgdk_wrapper/.agent/lib_case/sgdk-runtime/index.json` recebeu `registry_path` e a wave 1 de casos executáveis:
  - `case_variable_width_font_tidytext`
  - `case_tile_text_stream_renderer`
  - `case_pseudo3d_road_zmap`
  - `case_tile_cache_streaming`
  - `case_hint_wobble_spotlight`
- Fila de canonização inicial registrada:
  1. TidyText
  2. pseudo-3D road stack
  3. tile refcount cache
  4. H-Int FX family
  5. platformer feel
  6. multi-rate deceleration
  7. entity manager
  8. HUD patterns
  9. slope collision
  10. trig library
- Regra consolidada: pesquisa validada de engine é insumo forte, mas não canon pronta; promoção depende de referência exata, descrição limpa, `lib_case` reprodutível e gate humano explícito.

### Sistema de decisao HUD/UI FX canonizado (2026-04-20)
- Criado `doc/03_art/13_hud_ui_fx_decision_system.md` como doutrina principal de `S3.2 HUD Design`.
- `ui_decision_card` passa a ser o artefato canonico para HUD, interface, overlay, subscreen, menu, title e FX de interface.
- `front_end_profile` deixa de existir como artefato separado e passa a sobreviver apenas como `profile_kind=front_end_profile` dentro do mesmo `ui_decision_card`.
- `AAA_SKILL_CURATION_STATUS.md` promoveu `S3.2` para `INCORPORADO`, mas `runtime_proof_status` continua `NAO_INICIADA`.
- Pipeline e workflows da `.agent` agora exigem que ownership, fallback e budget de UI sejam declarados antes de budget/runtime quando houver surface formal de interface.
- `scene-state-architect`, `visual-excellence-standards`, `megadrive-vdp-budget-analyst`, `sgdk-runtime-coder`, `sgdk-build-wrapper-operator` e `game-director-sgdk` foram alinhados ao novo contrato.
- Decisao consolidada:
  - `window_plane_static_hud` continua sendo o default seguro para leitura constante
  - `window_plane_lifebar` e `sonic_hud_physics_family` seguem como referencias de pattern, nao defaults universais
  - `procedural_raster_glitch_suite` continua tecnica de alto risco e so entra com owner explicito, reset simetrico e fallback honesto
- Politica tipografica consolidada:
  - `fixed_custom_hud_font` e a rota default para HUD, labels fixos e leitura rapida
  - `variable_width_tidytext` fica para dialogo, credito, lore e texto premium em PT-BR
  - `glyph_manifest` passa a ser obrigatorio sempre que a UI subir fonte dedicada, acentos ou compositor proporcional

### Apresentacao expressiva de texto canonizada (2026-04-22)
- Criado `doc/03_art/16_expressive_narrative_text_presentation.md` como doutrina principal de `S3.5 Expressive Narrative Text Presentation`.
- Texto dramatico, fala, alerta cinetico, painel, balao, retrato animado, typewriter voice e flavor text entram como anexo `text_presentation_profile` dentro do `ui_decision_card`.
- O anexo nao substitui `glyph_manifest`; ele declara encenacao, ritmo, owner, audio, budget, teardown e fallback.
- Status inicial e `INCORPORADO` em doutrina e `NAO_INICIADA` em runtime proof ate existir `expressive_text_lab` em BlastEm.
- Regra consolidada:
  - texto expressivo so entra quando melhora ritmo dramatico, identidade de personagem, leitura de mundo, alerta ou recompensa de exploracao
  - texto estiloso sem ganho de leitura ou funcao deve voltar para fonte simples

### Sistema de transicoes contextualizadas canonizado (2026-04-21)
- Criado `doc/03_art/14_contextual_scene_transition_system.md` como doutrina principal de `S3.4 Scene Transition Design`.
- `scene_transition_card` passa a ser o artefato canonico para troca de cena, zona, ato, menu, cutscene ou estado visual com peso dramatico/tecnico.
- `scene_transition_card` permanece separado de `ui_decision_card`, mas deve referenciar UI quando a transicao tocar HUD, menu, title, overlay ou texto critico.
- Classes canonicas registradas: `palette_fade_bridge`, `spatial_scroll_bridge`, `scripted_avatar_bridge`, `tile_mask_mosaic_transition`, `raster_distortion_bridge`, `lighting_state_transition`, `pseudo3d_perspective_bridge` e `meta_cut_bridge`.
- Pipeline, workflows, frontdoor tecnico, registry de engine patterns, registry de maestria 16-bit e contracts das skills foram alinhados ao novo contrato.
- Decisao consolidada:
  - fade preto generico deixa de ser reflexo default; fallback seguro e `palette_fade_bridge` contextualizado
  - H-Int, palette split, wobble, pseudo-3D, tile mutation e audio fade so entram com owner unico, budget, reset simetrico e fallback
  - status inicial e `INCORPORADO` em doutrina e `NAO_INICIADA` em runtime proof ate existir benchmark em BlastEm

### Roadmap de proficiencia AAA do agente canonizado (2026-04-21)
- O roadmap oficial de proficiencia AAA do agente passa a viver em quatro fontes sincronizadas:
  - `doc/03_art/AAA_SKILL_CURATION_STATUS.md` como placar executivo
  - `doc/05_technical/93_16bit_hardware_mastery_matrix.md` como mapa humano
  - `doc/05_technical/93_16bit_hardware_mastery_registry.json` como registry machine-readable
  - `doc/05_technical/94_16bit_hardware_mastery_roadmap.md` como ordem de execucao
- Menu, fontes, HUD/UI e transicoes ja tem doutrina canonizada, mas continuam sem equivaler a runtime proof completo.
- Raster/luz/feedback FX, boss/setpieces, tilemap avancado e audio senior tambem passam a ter doutrina canonizada por `doc/03_art/15_aaa_runtime_spectacle_decision_system.md`.
- Proxima lacuna prioritaria:
  - prova runtime de `P0 Raster + Lighting + Feedback FX` no `BENCHMARK_VISUAL_LAB`
- Ordem consolidada de proficiencia:
  1. `aaa_agent_proficiency_roadmap`
  2. `expressive_text_presentation_system`
  3. `feedback_fx_decision_system`
  4. `boss_setpiece_design`
  5. `advanced_tilemap_design`
  6. `xgm2_audio_architecture`
  7. kinematics e experimentos especiais
- Regra consolidada:
  - `INCORPORADO` em doutrina nao significa `VALIDADA_EM_ROM`
  - nenhuma tecnica vira default AAA sem benchmark em BlastEm, budget aprovado e evidencia rastreavel

### Reorganização do Workspace
- **Backup completo:** Criado `archives/backup_pre_reorg_2026/` com cópia de doc/, SGDK_projects/, SGDK_Engines/, assets/, tmp/.
- **Renomeações:** `Assets and Sprites/` → `assets/`; `tmp/` → `.tmp/`.
- **Consolidação de scripts:** Scripts raiz (new-project.bat, setup-env.bat, etc.) movidos para `scripts/`.
- **Organização de logs:** Logs temporários em `doc/` movidos para `doc/logs/` e arquivados em `archives/logs_build_2026/`.
- **Limpeza de arquivos soltos:** Scripts avulsos em `SGDK_Engines/` movidos para `tools/maintenance/`.
- **Estrutura atualizada:** README.md raiz atualizado para refletir nova organização.
- **Validação:** Builds testados; resource validation OK (0 erros).

### Bateria grep/read_file — confirmação de implementações

**Símbolos pesquisados:**

| Símbolo | Resultado | Localização |
|---------|-----------|-------------|
| **SceneLayer** | Não encontrado | 0 ocorrências no repositório |
| **CollisionMap** | Encontrado (várias variantes) | Ver tabela abaixo |
| **sgdk_emitter** | Não encontrado em código SGDK | Apenas em Godot/Freetype/Aseprite (externos) |

**Implementações de colisão:**

| Projeto | Implementação | Trecho relevante |
|---------|---------------|------------------|
| **Shadow Dancer Hamoopig** | `collisionMatrix[TOTAL_MAP_BOXES][5]`, `collisionMatrixB` | Caixas [x1,y1,x2,y2,plano]; `CHECK_COLLISION` + `COLLISION_HANDLING`; `playerLayer` para planos |
| **PlatformerEngine Toolkit** | `generateCollisionMap()`, `freeCollisionMap()` | `levelgenerator.c/h` — mapa u8[][] 48 colunas |
| **Example Platformer** | `collision_map1[1182]` | Tile-based; `collision.h` |
| **Platformer 2** | `collision_mapa2[3584]` | Tile-based; `mapa2.h` |
| **Mega Metroid** | `curr_collision_map` | `types.h` — conversão para array 2D |
| **PlatformerStudio** | `collisionMap1..126` (símbolos exportados) | Godot → SGDK export |

**Trecho importante — Shadow Dancer (main.c ~1856–1867):**
```c
// MAP PLANE A — colisão com caixas do cenário
if(( CHECK_COLLISION(P[1].x-8, P[1].y-32, P[1].x+8, P[1].y,
    collisionMatrix[i][0], collisionMatrix[i][1], collisionMatrix[i][2], collisionMatrix[i][3])==1 && collisionTest==1)
   && enableTestCollision==TRUE)
{
    if(P[1].playerLayer==collisionMatrix[i][4])
    {
        COLLISION_HANDLING(1, collisionMatrix[i][0], collisionMatrix[i][1], collisionMatrix[i][2], collisionMatrix[i][3]);
        collisionTest=0;
    }
}
```

### Documentos criados nesta sessão
- `doc/06_AI_MEMORY_BANK.md` — este arquivo (memory bank global).
- `doc/QA_CHECKLIST_ROTEIRO.md` — roteiro QA passo-a-passo e checklist de evidências para RC.

---

## 3. PRÓXIMO PASSO IMEDIATO

1. Rodar `build.bat` em um projeto alvo (ex.: Shadow Dancer ou Pequeno Príncipe) e validar ROM no emulador.
2. Executar `validate_resources.ps1` em projetos com recursos (res/) para checagem pré-build.
3. Seguir roteiro em `doc/QA_CHECKLIST_ROTEIRO.md` para testes manuais e coleta de evidências RC.

---

## 4. DECISÕES CONSOLIDADAS (NÃO ALTERAR SEM ORDEM EXPRESSA)

| Decisão | Razão |
|---------|-------|
| Wrapper em `tools/sgdk_wrapper/` é única fonte de build | Evitar duplicação e inconsistência |
| Projetos delegam via `call "..\..\tools\sgdk_wrapper\build.bat" "%~dp0"` | Padronização e automação |
| Documentação em `doc/` (não `docs/`) | Convenção do repositório |
| Shadow Dancer usa collisionMatrix (caixas AABB), não tile-based | Arquitetura original do engine |

---

## 5. RISCOS CONHECIDOS

| Risco | Mitigação |
|-------|-----------|
| Grep em repositório grande pode dar timeout | Restringir path (ex.: SGDK_Engines, projeto específico) |
| Scripts de validação exigem Java, ImageMagick, SGDK | Documentar dependências em README do wrapper |
| `SceneLayer` e `sgdk_emitter` não existem no codebase | Não são APIs do SGDK; usar nomenclatura existente |

---

## 6. REFERÊNCIAS RÁPIDAS

| O que você precisa | Arquivo |
|--------------------|---------|
| Diretrizes para agentes | `doc/AGENTS.md` |
| Índice da documentação | `doc/README.md` |
| Wrapper e build | `tools/sgdk_wrapper/README.md` |
| Roteiro QA e evidências RC | `doc/QA_CHECKLIST_ROTEIRO.md` |
| Memory Bank Pequeno Príncipe | `SGDK_projects/.../doc/10-memory-bank.md` |

---

## 7. CURADORIA 2026-05-24 — GATE SEMANTICO ANTI-PROCEDURAL

Foi canonizado o gate `tools/sgdk_wrapper/audit_effect_campaign_semantics.ps1` para impedir falso verde em campanhas multi-ROM de efeitos. A campanha `SGDK_projects/data/aaa_effect_lab_campaign` foi auditada e reprovada com `105` blockers e `17` warnings: ROMs com painel procedural/debug, fallback generico em massa, 140 entradas `proposal_only` sem catalogo 180 verificado, ausencia de lib_cases nos registry-backed e `ready_for_aaa=true` com reports obrigatorios ausentes/stale.

Documentos e regras relacionados:

- `doc/05_technical/98_16bit_effects_campaign_semantic_gate.md`
- `SGDK_projects/data/aaa_effect_lab_campaign/semantic_audit_report.json`
- `SGDK_projects/data/aaa_effect_lab_campaign/semantic_audit_report.md`
- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
- `tools/sgdk_wrapper/.agent/workflows/build-validate.md`

Decisao: ROM procedural/debug ou screenshot BlastEm sem gate semantico limpo nao pode ser chamada de AAA, nota 8, pronta ou validada.

---

## 8. CURADORIA 2026-05-30 — CONTRATOS AAA AGENTICOS MACHINE-READABLE

Foi implementada a camada de contratos machine-readable para o ecossistema agentico AAA Mega Drive/SGDK.

Arte/animacao:
- `visual_dna_manifest.schema.json`
- `design_inheritance.schema.json`
- `animation_strip_contract.schema.json`
- `validate_strip.py`

Runtime/VDP/audio/QA:
- `dma_queue_planner.py`
- `vdp_scanline_simulator.py`
- `ym2612_patch_validator.py`
- `audio_architecture_card.schema.json`
- `blastem_input_script.schema.json`
- `project_bible.schema.json`

Contratos e exemplos vivem em:
- `tools/sgdk_wrapper/.agent/references/agentic_aaa_contracts/`

Report principal:
- `doc/AGENTIC_AAA_MEGADRIVE_IMPLEMENTATION_REPORT.md`

Gap audit:
- `doc/agentic_aaa_ecosystem_gap_audit.md`

Validacao executada:
- `python tools/sgdk_wrapper/.agent/scripts/self_check_agentic_aaa_contracts.py`
- `python tools/sgdk_wrapper/.agent/scripts/validate_skill_framework.py`

Decisao: a camada de framework esta `implemented_verified`, mas nao prova nenhuma cena/ROM. Qualquer entrega de jogo continua dependendo de build, validator, BlastEm, evidencia fresca, changelog e memoria operacional do projeto.

---

## 9. CURADORIA 2026-05-30 — AUDITORIA ESTRUTURAL PROFUNDA DO WORKSPACE

Foi executada a rodada conservadora:

- `out/workspace_curation/20260530_0655_deep_structure_audit/`
- `_archive/workspace_curation/20260530_0655_deep_structure_audit/`

Status final: `blocked_dirty_state_risk`.

Resumo:
- 41631 arquivos inventariados.
- 4788 diretorios inventariados.
- 8188 entradas tracked modificadas.
- 7721 entradas tracked deletadas.
- 11427 itens classificados para review.
- 0 moves executados.

Decisao: nenhum arquivo foi movido porque o worktree estava sujo demais para organizacao fisica segura. Foram gerados `full_tree_before.txt`, `move_plan.json`, `archive_manifest.json`, `rollback_plan.ps1` e `final_workspace_curation_report.md`.

Documentos criados:
- `doc/WORKSPACE_STRUCTURE.md`
- `doc/ASSET_ORGANIZATION_POLICY.md`
- `doc/ARCHIVE_MANIFEST_INDEX.md`
- `doc/NAMING_CONVENTIONS_WORKSPACE.md`

Proxima acao exata: revisar `out/workspace_curation/20260530_0655_deep_structure_audit/06_review_queue/review_queue.json`, estabilizar ou separar o worktree sujo e entao promover manualmente candidatos `review` para moves com SHA-256 antes/depois.

---

## 10. CURADORIA 2026-05-30 — RECONCILIACAO DA SUBCURADORIA TOOLS

A rodada `20260530_0655_deep_structure_audit` foi reconciliada apos detectar divergencia entre o manifest macro e a subcuradoria `tools/`.

Estado reconciliado:
- auditoria macro do workspace: `blocked_dirty_state_risk`, 0 moves globais;
- subcuradoria `tools/`: 6 moves executados e registrados separadamente;
- `archive_manifest.json` agora aponta explicitamente para `tools_moves.csv`;
- `move_execution_log.ndjson` reconstruido com 6 linhas e `reconstructed=true`;
- `rollback_plan.ps1` preenchido com validacao de existencia, checksum/stats e abort se origem ja existir;
- `review_queue.json` confirmado como amostra truncada de 5000 entradas; total original: 11427 em `move_plan.json` e `summary.json`.

Quatro origens movidas eram tracked:
- `tools/sgdk_wrapper/tmp_copy.py`
- `tools/sgdk_wrapper/package-lock.json`
- `tools/16tile/16Tile_v1_0_0.zip`
- `tools/palette-batch/PaletteBatch_102.zip`

Decisao operacional: nao houve staging nem commit. Se a curadoria for mantida, tratar esses quatro caminhos como rename/archive no Git. Se for rejeitada, executar `out/workspace_curation/20260530_0655_deep_structure_audit/03_archive_manifest/rollback_plan.ps1` antes de staging.

---

## 11. CURADORIA 2026-05-30 10:56 - AUDITORIA FINAL DE DECISAO GIT

Status: `git_decision_audit_verified`.

Recomendacao geral: `KEEP_ARCHIVED` para os 6 moves da subcuradoria `tools/`.

Evidencia resumida:
- origens continuam ausentes e destinos preservados em `_archive`;
- quatro origens tracked seguem como `D` ate decisao de staging ou rollback;
- nao foi encontrada referencia funcional especifica aos caminhos originais completos fora de `_archive` e `out/workspace_curation`;
- `tools/sgdk_wrapper`, `sdk/sgdk-2.11` e emuladores criticos continuam presentes;
- zips movidos tem pastas extraidas presentes;
- `tmp_copy.py` e script one-shot; `package-lock.json` e lockfile orfao sem `package.json`.

Comandos recomendados, nao executados:
- KEEP: revisar e depois usar `git add -A -- <4 origens tracked> _archive/workspace_curation/20260530_0655_deep_structure_audit`, seguido de `git status --short --find-renames` e `git diff --cached --name-status --find-renames`.
- RESTORE: executar `powershell -NoProfile -ExecutionPolicy Bypass -File out/workspace_curation/20260530_0655_deep_structure_audit/03_archive_manifest/rollback_plan.ps1` e revalidar status/checks antes de qualquer staging.

Relatorio: `out/workspace_curation/20260530_0655_deep_structure_audit/04_reports/git_decision_audit.md`.

---

## 10. CURADORIA 2026-05-30 — `tools/` ISOLADA (continuação)

Apos o status `blocked_dirty_state_risk` do macro, foi executada uma sub-rodada cirurgica e segura restrita a `F:\Projects\MegaDrive_DEV\tools\`.

### Estado canonico (nao mover)
- **Wrapper unico:** `tools/sgdk_wrapper/` — entry points `build.bat`, `clean.bat`, `run.bat`, `rebuild.bat`, `env.bat`, `env.sh`, `build_inner.bat` + libs em `lib/`, helpers em `_lib/sgdk_common.ps1`.
- **SDK fora de tools:** `sdk/sgdk-2.11/` (`env.bat`/`env.sh` resolve `GDK=$MD_ROOT/sdk/sgdk-2.11`).
- **Emuladores:** `tools/emuladores/Blastem`, `BizHawk`, `Exodus_2.1`, `GensKMod` (autodeteccao em `env.bat:32-39`).

### Decisao registrada: NAO aplicar `\tools\bin\`, `\tools\sgdk\`, `\tools\blastem\`
A proposta de relayout quebraria `env.bat` (hardcoded em `tools/emuladores/...`) e todos os shims relativos `..\..\tools\sgdk_wrapper\...` espalhados por `SGDK_projects/`/`SGDK_Engines/`/`SGDK_templates/`. Alem disso, `CLAUDE.md` exige SDK fora de `tools/`. Caminhos atuais validados e mantidos.

### Moves executados (6, todos `confidence=high`, SHA-256 registrado)
Manifesto: `out/workspace_curation/20260530_0655_deep_structure_audit/03_archive_manifest/tools_moves.csv`.
Quarentena: `_archive/workspace_curation/20260530_0655_deep_structure_audit/`.

| Origem (em `tools/`)                       | Bucket de quarentena       |
|--------------------------------------------|-----------------------------|
| `sggdk_wrapper/` (typo de `sgdk_wrapper`)  | `obsolete_experiments/`     |
| `sgdk_wrapper/__pycache__/`                | `generated_tmp/`            |
| `sgdk_wrapper/tmp_copy.py`                 | `generated_tmp/`            |
| `sgdk_wrapper/package-lock.json` (orfao)   | `generated_tmp/`            |
| `16tile/16Tile_v1_0_0.zip` (instalador)    | `asset_packs_raw/`          |
| `palette-batch/PaletteBatch_102.zip` (instalador) | `asset_packs_raw/`   |

### Validacao pos-move
`blastem.exe`, `EmuHawk.exe`, `Exodus_2.1`, `gens.exe`, `rescomp.jar`, `make.exe`, `env.bat`, `build.bat`, `build_inner.bat`, `lib/blastem_automation.psm1`, `_lib/sgdk_common.ps1` — todos presentes nos caminhos canonicos.

### Documentacao gerada
- `tools/README.md` — mapa autoritativo da pasta (papel de cada subpasta, vinculacao `sgdk_wrapper` ↔ toolchain).
- `out/workspace_curation/20260530_0655_deep_structure_audit/01_findings/tools_findings.md`
- `out/workspace_curation/20260530_0655_deep_structure_audit/02_move_plan/tools_move_plan.json`
- `out/workspace_curation/20260530_0655_deep_structure_audit/00_inventory/tools_isolated_inventory.json`
- `out/workspace_curation/20260530_0655_deep_structure_audit/05_before_after/tools_{before,after}.txt`

### Diferida para revisao do dono
- `tools/out/.agent/` — placeholder vazio (possivel leak de `sgdk_wrapper/out/`).
- `tools/gen-scripts/cuphead_idle_0001.png` — asset solto.
- `tools/HAMOOPI-PcEngine/` — ferramenta off-platform (PC Engine), sem referencias do toolchain SGDK; candidata a sair de `tools/` em rodada futura.

---

## 12. CURADORIA 2026-05-30 18:58 - REAUDITORIA MACRO DE ESTRUTURA

Status: `macro_structure_reaudit_completed_no_moves`.

Rodada: `out/workspace_curation/20260530_1858_macro_structure_reaudit/`.

Decisoes recomendadas:
- `sdk/sgdk-2.11` continua canonico em `sdk/`; nao mover para `tools/`.
- `tools/sgdk_wrapper/modelo` continua fonte primaria de bootstrap porque `new_project.bat` e `new_project.sh` usam `modelo` antes do fallback.
- `sgdk_templates/base-elite`, `SimpleGameStates_Elite`, `sgdk_templates/templates` e `tools/sgdk_wrapper/templates/project-template-nested` precisam de registry antes de qualquer promocao/deprecacao.
- `assets`, `data` e `SGDK_projects/data` nao devem ser unidos fisicamente agora; precisam de inventario de origem/licenca/uso e buckets raw/source/reference, processed/generated, project-specific e rejected/third_party.
- `out` e `tools/sgdk_wrapper/out` devem ser tratados como output/evidencia com politica de retencao, nao como fonte canonica.
- `scripts/` pode migrar futuramente para `tools/bootstrap/`, mas somente com shims na raiz e atualizacao documental.

Itens bloqueados/OWNER_REVIEW:
- `SGDK_projects/data` tem mistura de tracked deleted e untracked packs.
- `sgdk_templates` e `tools/sgdk_wrapper/modelo` estao modificados/untracked e contem outputs/materializacoes que exigem branch propria.
- arquivos soltos tracked na raiz (`fix_mission1.py`, `fix_sky.py`, `get_issues.py`, `get_needs_review.py`, `inf.txt`) nao devem ser movidos sem decisao de historico/shim.
- `CURADORIA_CANONICA_APLICADA.md` e candidato a arquivo documental/arquivo, mas segue em review por ser untracked.

Proximos passos seguros:
1. Criar `tools/sgdk_wrapper/templates/registry.json` em uma rodada dedicada.
2. Gerar asset registry para `assets`, `data` e `SGDK_projects/data` antes de qualquer merge fisico.
3. Planejar migracao de `scripts/` para `tools/bootstrap/` com shims e rollback.
4. Arquivar outputs antigos somente por run datado, manifest, checksum e rollback.

---

## 13. CURADORIA 2026-05-30 19:07 - REGISTRY DE TEMPLATES E POLITICAS

Status: `registry_implementation_verified`.

Rodada: `out/workspace_curation/20260530_1907_registry_implementation/`.

Decisao registrada:
- `tools/sgdk_wrapper/modelo` e o `CANONICAL_BOOTSTRAP` porque `new_project.bat` e `new_project.sh` usam esse caminho antes do fallback.
- `sgdk_templates/base-elite` permanece `REFERENCE_TEMPLATE` ate revisao dedicada.
- `sgdk_templates/SimpleGameStates_Elite`, `sgdk_templates/templates` e `tools/sgdk_wrapper/templates/project-template-nested` permanecem registrados, mas exigem `OWNER_REVIEW` antes de promocao, limpeza ou deprecacao.

Arquivos criados/atualizados:
- `doc/template_registry.json`
- `doc/TEMPLATE_REGISTRY.md`
- `doc/ASSET_DATA_REGISTRY_POLICY.md`
- `doc/asset_data_registry.schema.json`
- `doc/ROOT_LOOSE_FILES_POLICY.md`
- `doc/OUTPUT_RETENTION_POLICY.md`
- `tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`
- `out/workspace_curation/20260530_1907_registry_implementation/04_reports/next_asset_registry_prompt.md`
- `doc/WORKSPACE_STRUCTURE.md`
- `tools/README.md`
- `README.md`

Proximos comandos sugeridos, nao executados:
- `python tools/sgdk_wrapper/.agent/scripts/validate_template_registry.py`
- gerar a proxima rodada `asset_data_registry` usando `out/workspace_curation/20260530_1907_registry_implementation/04_reports/next_asset_registry_prompt.md`
- revisar manualmente outputs dentro dos templates antes de qualquer limpeza fisica

---

## 14. CURADORIA 2026-05-30 19:35 - ASSET/DATA REGISTRY

Status: `asset_data_registry_generated_no_moves`.

Rodada: `out/workspace_curation/20260530_1935_asset_data_registry/`.

Escopo inventariado:
- `assets/`: 10491 arquivos, 272960369 bytes, todo o conteudo detectado como ignored.
- `data/`: 94 arquivos, 3537918 bytes, mistura de untracked e ignored.
- `SGDK_projects/data`: 13508 arquivos, 777714181 bytes, mistura de tracked clean, untracked e ignored.

Decisao recomendada: `MIXED_OWNER_REVIEW`.

Resultado:
- `00_inventory/asset_data_inventory.json` registra 24093 arquivos com SHA-256, tamanho, extensao, Git state, bucket conservador e recomendacao.
- `02_move_plan/proposed_asset_data_move_plan.json` tem zero moves executaveis; qualquer move futuro exige decisao de dono, manifest, checksum e rollback.
- `04_reports/asset_data_registry_audit.md` resume 2308 grupos duplicados por SHA-256 e 1779 grupos provaveis por nome/tamanho.
- `doc/asset_data_registry.json` nao foi promovido nesta rodada porque o inventario ainda exige revisao humana.

Proximos passos seguros:
1. Revisar primeiro `SGDK_projects/data` por pack/projeto e licenca.
2. Resolver duplicados por SHA-256 em lotes pequenos.
3. Criar plano de move estreito somente para itens com dono/licenca confirmados.
4. Manter layout fisico atual ate aprovacao explicita.

---

## 15. GAME DESIGN 2026-05-31 - NEON RAIN NINJA

Status: `milestone_2_testado_em_emulador_com_warnings`.

Projeto materializado:
- `SGDK_projects/Neon Rain Ninja action platformer  [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/`

Arquivo canonico atual:
- `SGDK_projects/Neon Rain Ninja action platformer  [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/doc/11-gdd.md`

Plano de implementacao:
- `SGDK_projects/Neon Rain Ninja action platformer  [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/doc/plans/2026-05-31-neon-rain-ninja-implementation-plan.md`

Marcos tecnicos implementados:
- `APP_SCENE_NEON_SLICE` com player textual `[N]`, controller `fix16`, camera lateral e regra simples luz/sombra.
- Primeiro guarda textual `G/G?/G!/gx` com suspeita, alerta e abatimento por golpe stealth em sombra.
- Bootstrap SRAM `SBIS` para boot deterministico da cena 4 nos capturadores.
- Runtime probe `MDRT` ativo no loop principal.
- Contratos canonicos: `doc/scene-contracts.json` compilado de `doc/13-spec-cenas.md` e `doc/scene-regression.json`.

Evidencia:
- ROM: `out/rom.bin`, SHA-256 `d096b13b5ede94f97626d842c59e4bde75a00c03e8cd9d0166f7411426b9c455`, 131072 bytes.
- BlastEm runtime capture: `out/logs/runtime_metrics.json`, `scene_id=4`, `cpu_load_max=15`, `over_budget_frames=0`.
- Screenshot: `out/evidence/blastem/screenshot.png`.
- Scene contract compile: 2 cenas compiladas; lint sem erros/warnings.
- Scene regression: `neon_rain_rooftop_slice` passed=1, baseline em `doc/baselines/neon_rain_rooftop_slice/`.
- Freshness audit: status=`ok`, stale=0, missing_required=0.

Decisao criativa registrada:
- Genero: action platformer cinematografico.
- Fantasia: ninja/cyberpunk tropical.
- Escopo: vertical slice completo.
- Pilar: stealth agressivo.
- Sistema central: luz/neon como regra de visibilidade, risco e ataque.
- Primeira fase: `Distrito Chuva Neon`.

Direcao recomendada:
- manter o jogo como fase-vitrine coesa, nao showroom de FX.
- cada tecnica deve afetar gameplay, leitura, rota, risco ou timing.
- a primeira ROM deve provar tutorial invisivel, rotas por sombra, cabos cortaveis, blackout e boss que reutiliza as regras da fase.

Proxima etapa segura:
1. Adicionar interacao simples de blackout/cabo cortavel como efeito colateral fisico do sistema de luz.
2. Criar captura dedicada com input script para provar movimento e golpe stealth, nao apenas boot/performance.
3. Rodar scene closeout e visual delivery antes de promover qualquer status AAA.
4. Manter `doc/10-memory-bank.md` do projeto como memoria operacional principal.

---

## 16. WRAPPER 2026-06-01 - CANONICAL GATE HARDENING

Status: `validator_hardened_pending_full_ci`.

Objetivo:
- impedir falso `ready_for_aaa` derivado apenas de build, BlastEm ou reports tecnicos.
- separar `technical_ready` de `creative_ready`.
- tratar `semantic_audit_status=failed` como blocker canonico.

Decisoes efetivas:
- `technical_artifact_status` e o novo nome canonico do antigo significado de `aggregate_status`; `aggregate_status` permanece apenas como alias deprecated.
- `ready_for_aaa=true` exige `technical_ready=true`, `creative_ready=true`, `summary.errors=0`, `blocking_statuses=[]`, `creative_blocking_statuses=[]` e `semantic_audit_status!=failed`.
- GDD substancial, decision log granular, evidencia por eixo, consequencia jogavel, julgamento visual real e animation gate premium passam a ser gates criativos.
- fallback procedural/debug/lab como final limita `max_delivery_status` a `technical_lab_validated` e bloqueia `creative_ready`.

Arquivos centrais:
- `tools/sgdk_wrapper/validate_resources.ps1`
- `tools/sgdk_wrapper/audit_effect_campaign_semantics.ps1`
- `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json`
- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
- `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`
- `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`

Observacao operacional:
- Esta rodada endurece o agente canonico e validadores. Nao entrega jogo/ROM.

---

## 17. EFFECT LAB 2026-06-01 - RECONSTRUCAO AAA BLOQUEADA COM EVIDENCIA

Status: `prototype_debug_lab_reclassified`.

Objetivo da rodada:
- rebaixar as 17 ROMs atuais para laboratorio/prototipo, sem reivindicacao AAA.
- endurecer gates para impedir promocao por build, texto debug, asset generico ou evidencia manual.
- regenerar as 17 bases jogaveis independentes como `AAA EFFECT LAB - <slug>`.
- comprovar pelo menos um eixo em BlastEm com budget medido e closeout formal.

Resultado confirmado:
- Build scan final: `status=ok`, `built=17`.
- Matriz de validacao: `project_count=17`, `ready_for_aaa_count=0`, `blocked_count=17`, `bad_lab_ceiling_count=0`.
- Todas as ROMs continuam sob teto `technical_lab_validated` / `vertical_slice_candidate`.
- Nenhuma das 17 deve ser chamada de AAA nesta fase.

Eixo piloto verificado:
- Projeto: `SGDK_projects/AAA EFFECT LAB - pseudo-3d [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/`
- Runtime BlastEm: `capture_status=ok`, `target_fps=60`, `samples_recorded=1800`, `over_budget_frames=0`, `frame_cpu_ratio_p95=31`.
- Budget: `scene_budget_report.json` status `ok`, `axis02_main`, `frames_analyzed=1800`, `sprite_count_peak=11`, `sprites_per_scanline_peak=12`, `cpu_overrun_count=0`.
- Evidencia canonica: `out/evidence/blastem/screenshot.png`, `save.sram`, `visual_vdp_dump.bin`.
- Closeout: `scene_closeout_gate_report.json` status `failed`.
- Mastering: `rom_mastering_report.json` decision `mastering_needs_fix`, SHA-256 `66f8ec60b0c3ec00f598c711ae60eff07510dc2b5e3e7cc78bcfca3e60ed0681`.

Bloqueios canonicos restantes:
- `scene_regression_baseline_missing`
- `freshness_audit_stale`
- `visual_gate_blocked`
- `procedural_fallback_as_final`
- `visual_direction_failed`
- `animation_gate_failed`

Arquivos centrais desta rodada:
- `tools/sgdk_wrapper/validate_resources.ps1`
- `tools/sgdk_wrapper/schemas/visual_delivery_gate_report.schema.json`
- `tools/sgdk_wrapper/run_effect_lab_validation_matrix.ps1`
- `tools/sgdk_wrapper/run_effect_lab_build_matrix.ps1`
- `tools/sgdk_wrapper/scan_effect_lab_build_outputs.ps1`
- `tools/sgdk_wrapper/audit_scene_budget.ps1`
- `SGDK_projects/ProjectLab_effect_campaign [VER.001] [SGDK 211] [GEN] [HOMEBREW] [DEMO]/tools/rebuild_aaa_effect_lab_axes.py`

Decisao operacional:
- O gap grande e real: as bases atuais sao procedurais e tecnicas, nao cenas autorais no nivel visual dos melhores jogos de Mega Drive.
- A reconstrucao precisa de direcao visual/art assets premium, baseline comercial comparativo, regressao visual canonica por eixo, audio/design final e closeout completo para cada ROM.
- Ate isso existir, o pipeline deve continuar bloqueando `ready_for_aaa=true`.

---

## 18. WRAPPER 2026-06-03 - ORGANIZACAO CANONICA E PROFICIENCIA HUMANA

Status: `implemented_validated`.

Objetivo:
- impedir que agentes criem material arbitrario fora do projeto e depois usem isso como evidencia;
- expor para humanos um painel vivo de proficiencia por tecnica;
- bloquear contaminacao canonica por tecnicas em `LABORATORIO`.

Decisoes efetivas:
- `doc/05_technical/93_16bit_hardware_mastery_registry.json` ganhou camada publica `human_proficiency_status`, `technique_tags` e `promotion_evidence`.
- Status humanos oficiais: `LABORATORIO`, `TEORICA_STANDARD`, `TEORICA_PRIORITARIA`, `MESTRE_STANDARD`, `MESTRE_PRIORITARIA`.
- `doc/05_technical/93_16bit_hardware_mastery_matrix.md` virou painel humano visivel sincronizado com o registry.
- Projetos passam a ter contrato `doc/technique_usage_manifest.json` para declarar tecnicas usadas, tags, owner skills, evidencias e sincronizacao documental.
- `validate_resources.ps1` passa a bloquear manifesto invalido, registry id desconhecido, tag desconhecida, status divergente, tecnica `LABORATORIO` fora de lab, evidencia fora do projeto sem autorizacao e docs nao sincronizados.
- `doc/ROOT_LOOSE_FILES_POLICY.md` foi materializado para fechar a politica de arquivos soltos citada em `doc/WORKSPACE_STRUCTURE.md`.

Arquivos centrais:
- `tools/sgdk_wrapper/validate_resources.ps1`
- `tools/sgdk_wrapper/schemas/technique_usage_manifest.schema.json`
- `tools/sgdk_wrapper/.agent/scripts/validate_technique_registry.py`
- `tools/sgdk_wrapper/.agent/rules/SGDK_GLOBAL.md`
- `tools/sgdk_wrapper/.agent/workflows/production-loop.md`
- `tools/sgdk_wrapper/.agent/workflows/aaa-scene-pipeline.md`
- `doc/05_technical/93_16bit_hardware_mastery_registry.json`
- `doc/05_technical/93_16bit_hardware_mastery_matrix.md`
- `doc/ROOT_LOOSE_FILES_POLICY.md`

Observacao operacional:
- Esta rodada endurece o agente canonico e o validator. Nao entrega jogo/ROM nem promove tecnica para `MESTRE_*`.

---

## 19. WRAPPER 2026-06-03 - ASSIMILACAO DE CURADORIA TECNICA MEGA DRIVE

Status: `implemented_validated`.

Objetivo:
- assimilar o texto externo colado pelo usuario como lote rastreavel de curadoria tecnica;
- enriquecer o vocabulario do agente sobre DMA/VBlank, sprites grandes, rescomp/metasprites, CRAM/H-Int, Shadow/Highlight, palette remastering, VSRAM e pseudo-3D;
- impedir que material secundario nao verificado promova tecnica para `MESTRE_*`.

Decisoes efetivas:
- `doc/05_technical/93_16bit_hardware_mastery_registry.json` passou para `version=4` e ganhou `external_curation_batches`.
- Lote canonico: `curation_2026_06_03_megadrive_video_text_batch`, marcado como `unverified_secondary_text`.
- Novas tecnicas adicionadas: `sprite_frame_vram_slot_streaming`, `animation_lookahead_dma_queue`, `large_metasprite_vblank_fit_audit`, `rescomp_metasprite_decomposition_audit`, `sat_double_buffering`, `sprite_band_slot_allocator`, `cram_dot_masking_strategy`, `palette_remastering_slot_audit`, `tile_dedup_hvflip_hashing`, `ghost_afterimage_sprites` e `arcade_tile_redraw_substitution`.
- Nenhuma tecnica foi promovida para `MESTRE_STANDARD` ou `MESTRE_PRIORITARIA`.
- Skills atualizadas: `megadrive-vdp-budget-analyst`, `sgdk-runtime-coder` e `art-conversion-pipeline`.

Regra operacional:
- claims como centenas de sprites, DMA em background, SAT rewrite mid-frame seguro, CRAM sem dots e switch H32/H40 em runtime continuam `LABORATORIO`/risco ate prova isolada em BlastEm, budget e aprovacao humana.

Validacao executada:
- `validate_technique_registry.py`: ok, 51 entradas, 45 tags, zero `MESTRE_*`.
- `validate_skill_framework.py`: ok.
- `validate_template_registry.py`: ok com warning preexistente de `sgdk_modelo` contendo `out/`.
- `validate_resources.ps1` no `SMOKE_TEST`: errors=0, warnings=14, `technique_usage_ready=true`, `ready_for_aaa=false`.
- Fixtures temporarios confirmaram: tag nova valida nao gera `technique_tag_unknown`; `LABORATORIO` fora de lab bloqueia; registry id ausente bloqueia; tag invalida bloqueia. Fixtures removidos apos a validacao.

---

## 20. WRAPPER 2026-06-03 - CURADORIA CELESTIAL CHASE: MOVIMENTO PERCEPTIVO E QUALIDADE VISUAL

Status: `implemented_validated`. Subscopo: gates de governanca + contratos/parciais derivados de LAB/TECHDEMO. ZERO promocao para `MESTRE_*`.

Fonte da licao: projeto `SGDK_projects/Celestial Chase visual benchmark [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]/`. Estado do projeto no momento da capturada: `pipeline_status=runtime_visual_lab`, `scene_id=chase_runtime_v005`, `target_scene=4`, ROM `9608a0f706b1242d89ba14ae30f899e0717808a1ea4e948352b4618384837bed` (262144 bytes), build_v004, `technical_ready=true` no memory bank mas `creative_ready=false` e `ready_for_aaa=false`, com 4 blockers ativos (`gdd_substantial_insufficient`, `visual_gate_blocked`, `procedural_fallback_as_final`, `visual_direction_failed`).

Sintese da licao em 3 frases:
1. **Movimento precisa de prova perceptiva, nao so de build verde.** Build OK + screenshot + SRAM nao bastam. O projeto tinha `boot_emulador=ok` + `gameplay_basico=funcional` + `performance=estavel` + `audio=ok` + `screenshot_present=true` + `sram_present=true`, mas `perceptual_check` zerado (fluidez/leitura/naturalidade/impacto=0) e `vdp_dump_present=false`. O sistema antigo aceitava essa combinacao como "pronto"; o novo exige motion_gif/visual_vdp_dump + perceptual_check nao-zero + human_approval_record.
2. **Claim de gameplay exige contrato.** O projeto declara `scene_id=chase_runtime_v005` + `CHASE_BOSS_IMPACT_FRAME=3` + `sBossBody` (sprite unico), mas nao tem `road_physics_contract` (lane model, parallax, curvature, impact frame origem) nem `boss_parts.json` + `FK chain`. Sem contrato, claim de "chase AAA" ou "boss modular" eh placeholder.
3. **Arte que nasce pixel nao passa por downscaling.** O usuario entregou source art autoral ja pixel-art. O pipeline de downscaling (`art-conversion-pipeline`) NAO foi aplicado. A trilha canonica para esse caso eh `source_baked_pixel_art_standard` (pixel_lock + animation_strip + motion_gif), separada de `art-conversion-pipeline` (fonte high-res) e `art-translation-to-vdp` (concept art forte).

Mudancas canonicas aplicadas:

1. `doc/05_technical/93_16bit_hardware_mastery_registry.json`:
   - Lote `celestial_chase_motion_visual_curation_2026_06_03` (source_type `project_lesson`, verification_status `project_evidence_partial`, `promotion_allowed=false`).
   - 8 entries adicionadas (versao do registry segue em `version=4`, `updated_at=2026-06-03`):
     - `perceptual_motion_gate` - `TEORICA_PRIORITARIA`, `default_safe`, dono `visual-excellence-standards + sgdk-runtime-coder + megadrive-vdp-budget-analyst`. Gate GOVERNANCA.
     - `source_baked_pixel_art_standard` - `TEORICA_PRIORITARIA`, `integrated_doctrine`, dono `art-conversion-pipeline + art-translation-to-vdp + megadrive-pixel-strict-rules`. Standard canonico.
     - `critical_visual_rework_blocker` - `TEORICA_PRIORITARIA`, `default_safe`, dono `visual-excellence-standards + status-panel-maintainer`. Gate GOVERNANCA.
     - `road_physics_contract` - `LABORATORIO`, `advanced_tradeoff`, dono `level-design-canonical + sgdk-runtime-coder + megadrive-vdp-budget-analyst`. Parcial/contrato.
     - `modular_boss_runtime_gate` - `LABORATORIO`, `advanced_tradeoff`, dono `forward-kinematics-rigging + sgdk-runtime-coder + boss_setpiece_design`. Parcial/contrato.
     - `gif_motion_approval_gate` - `TEORICA_PRIORITARIA`, `default_safe`, dono `art-conversion-pipeline + art-translation-to-vdp + sprite-animation`. Gate GOVERNANCA.
     - `perceptual_runtime_metrics` - `LABORATORIO`, `default_safe`, dono `sgdk-runtime-coder + megadrive-vdp-budget-analyst`. Instrumentacao.
     - `visual_regression_temporal_baseline` - `TEORICA_STANDARD`, `special_scene_only`, dono `multi-plane-composition + sgdk-runtime-coder + megadrive-vdp-budget-analyst`. Documentado.
   - Distribuicao de status humanos: `LABORATORIO=27`, `TEORICA_PRIORITARIA=18`, `TEORICA_STANDARD=14`, `MESTRE_STANDARD=0`, `MESTRE_PRIORITARIA=0`. ZERO `MESTRE_*`.
   - 11 novas tags adicionadas ao vocabulario canonico: `PERCEPTUAL_MOTION`, `SOURCE_BAKED_PIXEL_ART`, `CRITICAL_VISUAL_GATE`, `ROAD_PHYSICS`, `MODULAR_BOSS_RIG`, `GIF_MOTION_APPROVAL`, `PERCEPTUAL_RUNTIME_METRICS`, `VISUAL_REGRESSION`, `RUNTIME_EVIDENCE`, `REWORK_BLOCKER`, `TEMPORAL_BASELINE`, `FRAME_DIFF`, `REGRESSION_DRIFT`, `MOTION_GIF_VERSIONS`, `PIVOT_DECLARATION`, `CONTACT_POINTS`, `ART_PIPELINE_GATE`, `VDP_DUMP_EVIDENCE`, `GAMEPLAY_CONTRACT`, `FK_CHAIN`, `HSCROLL_TABLE`, `CHASE_CLAIM`, `BOSS_RUNTIME`, `SPRITE_PARTS`, `RUNTIME_INSTRUMENTATION`, `GATING`, `BLASTEM_EVIDENCE`, `PIXEL_LOCK`, `ANIMATION_STRIP`, `MOTION_GIF`, `ASSET_APPROVAL`, `VISUAL_DELIVERY`, `HUMAN_OVERRIDE`, `FRAME_METRICS`, `SPRITE_COUNT`, `PERCEPTUAL_CHECK`, `PSEUDO_3D`.

2. `doc/05_technical/93_16bit_hardware_mastery_matrix.md`:
   - Linha no painel de "Lotes externos de curadoria" para o novo lote.
   - 8 novas linhas no painel humano com id, titulo, status humano, tags.
   - Secao nova "Licao Celestial Chase 2026-06-03" com sintese, mapa rapido e regra de promocao.

3. Skills canonicamente atualizadas (sem quebrar `validate_skill_framework.py`):
   - `tools/sgdk_wrapper/.agent/skills/art/visual-excellence-standards/SKILL.md`: secao "Curadoria 2026-06-03 - Celestial Chase" com `perceptual_motion_gate` (5 sinais obrigatorios) + `critical_visual_rework_blocker` (override exige human_approval_record + visual_vdp_dump) + `visual_lab_static_floor` (piso honesto para LAB/TECHDEMO). Tambem adicionados 2 itens em "Gatilhos de reprovacao".
   - `tools/sgdk_wrapper/.agent/skills/art/art-conversion-pipeline/SKILL.md`: secao "Curadoria 2026-06-03 - Celestial Chase" com `source_baked_pixel_art_standard` (quando NAO usar este pipeline vs quando usar). Sintomas de violacao listados.
   - `tools/sgdk_wrapper/.agent/skills/art/art-translation-to-vdp/SKILL.md`: subsecao "Curadoria 2026-06-03" dentro de "Gates" com `motion_gif + pivots.json + contact_points.json + human_approval_record.md` como output obrigatorio para sprite strip de animacao.
   - `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/SKILL.md`: secao "Curadoria 2026-06-03" com taxonomia `runtime_funcional|animacao_observada|movimento_aprovado|visual_aprovado|gameplay_aprovado`, piso `visual_lab_static_floor` para LAB/TECHDEMO, e flag `asset_promovido_nao_usado` para detectar divergencia entre painel e codigo.
   - `tools/sgdk_wrapper/.agent/skills/hardware/megadrive-vdp-budget-analyst/SKILL.md`: secao "Curadoria 2026-06-03" separando resposta tecnica (`cabe|cabe com recuo|nao cabe`) de resposta perceptiva (`perceptivel|perceptivel com recuo|nao perceptivel`), com tabela de composicao dos 2 eixos.

4. `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`:
   - `framework_manifest_min_version` preservado em `2026.05.09`.
   - S1a_art_creation: 6 novos `optional_artifacts` (`source_baked_pixel_art_standard`, `pixel_lock_spec`, `animation_strip_spec`, `motion_gif_spec`, `pivots_contract`, `contact_points_contract`) + 2 novos `exit_conditions`.
   - S4_excellence: 3 novos `optional_artifacts` (`perceptual_motion_gate_report`, `critical_visual_rework_blocker_report`, `gif_motion_approval_record`) + 2 novos `exit_conditions`.
   - S5_budget: 1 novo `exit_condition` para `modular_boss_runtime_gate` (FK chain + scanline budget por parte).
   - S6_runtime: 2 novos `exit_conditions` para `road_physics_contract` + `perceptual_runtime_metrics`.
   - S7_validate: 1 novo `optional_artifact` (`visual_regression_temporal_baseline_spec`) + 1 novo `exit_condition`.
   - S8_qa_evidence: 1 novo `exit_condition` exigindo os 5 sinais de evidencia BlastEm (screenshot + SRAM + VDP dump + motion_gif + perceptual_check nao-zero).

5. `tools/sgdk_wrapper/validate_resources.ps1` (6028 linhas, sintaxe PowerShell verificada):
   - 3 novos statuses adicionados a `Test-CloseoutOnlyBlockingStatus`: `perceptual_motion_unvalidated`, `road_physics_contract_missing`, `modular_boss_runtime_missing`. Sao `warn_only` por padrao (LAB/TECHDEMO) e `fatal` quando `-CloseoutGate` eh passado.
   - 3 novos statuses adicionados ao regex `creative_blocking_statuses`, entao alimentam `creative_ready=false` e `ready_for_aaa=false` direto.
   - Bloco de deteccao `CURADORIA_2026_06_03_CELESTIAL_CHASE_GOVERNANCE_GATES` inserido apos `technical_ready` ser computado, com 3 funcoes de deteccao:
     - `perceptual_motion_unvalidated`: ativo quando `visualDeliveryIntent=true` + (`perceptual_check` zerado OU `vdp_dump_present=false` E `motion_gif_present=false`). Le `out/logs/runtime_metrics.json` (perceptual_check + capture_status) e `out/logs/blastem_evidence.json` (vdp_dump_present, motion_gif_present, screenshot_present, sram_present).
     - `road_physics_contract_missing`: ativo quando claim de chase/pseudo-3D detectado em `doc/10-memory-bank.md` (regex: `chase_runtime`, `chase.{0,40}scene`, `pseudo.{0,3}3d`, `chase.{0,20}claim`, `CHASE_BOSS_IMPACT_FRAME`, `chase_visual_benchmark`) ou em `src/scenes/*.c` (regex: `chase`, `CHASE_BOSS`, `road_physics`, `pseudo3d_road`) E `doc/contracts/road_physics_contract.json` ausente.
     - `modular_boss_runtime_missing`: ativo quando claim de boss modular detectado (regex: `modular.{0,20}boss`, `boss.{0,20}modular`, `sBossBody`, `sBossWing`, `sBossClaw`, `forward_kinematics`) ou quando `src/scenes/*.c` tem <= 1 `sBoss*` sprite + match em `sBossBody|chase_boss|impact_frame` E `doc/contracts/boss_parts.json` ausente.

6. `ready_for_aaa=false` quando `scope=lab` ja era enforced por `Test-ClaimCeilingAllowsReadyForAaa` + `claim_ceiling` machinery (linha 5724 do validator). A licao Celestial Chase reforca esse comportamento: `technical_ready=true` no memory bank do LAB eh correto (build verde, gameplay basico funcional, audio ok), mas `ready_for_aaa` permanece `false` ate o projeto sair de `LAB/TECHDEMO`.

Resultado da validacao no proprio Celestial Chase:
- `validate_resources.ps1 -WorkDir <celestial_chase>`: 9 `blocking_statuses` no total (6 existentes + 3 novos). 3 novos gates disparam:
  - `[WARN] perceptual_motion_unvalidated`: perceptual_check zerado + vdp_dump_present=false + motion_gif_present=false.
  - `[WARN] road_physics_contract_missing`: chase claim em memory bank/codigo, contract ausente.
  - `[WARN] modular_boss_runtime_missing`: boss modular claim + apenas 1 sprite `sBossBody` no `scene_chase.c`, contract ausente.
- `creative_blocking_statuses`: 7 (4 antigos + 3 novos), confirmando que os 3 gates alimentam `creative_ready`.
- `ready_for_aaa: false` (preservado por `claim_ceiling=technical_lab_validated`).

Regra operacional registrada:
- Claim de "asset critico" (hero, boss, veiculo, FX principal) NAO pode subir para `elite_ready` ou `delivered` sem a composicao completa de: motion_gif/visual_vdp_dump + perceptual_check nao-zero + screenshot dedicado + save.sram fresco + human_approval_record.
- Claim de chase/pseudo-3D exige `doc/contracts/road_physics_contract.json` com lane_model, parallax_equation, impact_frame, screen_shake, curvature.
- Claim de boss modular exige `doc/contracts/boss_parts.json` + N partes runtime no codigo (`sBossBody`, `sBossWing`, `sBossClaw`, ...) + `FK chain` declarada.
- Aprovacao de sprite de animacao exige motion_gif + pivos + contact points + human_approval_record.
- LAB/TECHDEMO tem `visual_lab_static_floor`: `technical_ready=true` eh possivel sem perceptual_motion_gate satisfeito, mas `ready_for_aaa=false` permanece ate sair do escopo.

## 21. WRAPPER 2026-06-04 - CORRECAO DE ENFORCEMENT METODOLOGICO

Esta secao substitui operacionalmente os gates textuais descritos na secao 20.
O aprendizado tecnico permanece valido, mas a primeira implementacao aceitava
bypasses e criava falsos positivos.

Correcoes canonicas:

- criado `doc/project_methodology_manifest.json` como contrato local para
  `project.lifecycle`, `production-loop`, skills, validacoes e claims;
- criado `adopt_project_methodology.ps1`, que materializa manifestos ausentes
  dentro de projetos novos/antigos sem sobrescrever arquivos existentes;
- criado `validate_project_methodology.ps1` e a suite executavel
  `ci/test_project_methodology_governance.ps1`;
- removida a inferencia por regex de `chase`, `sBossBody`, `impact_frame` e
  intencao visual generica;
- `critical_motion`, `road_physics` e `modular_boss` so ativam quando o
  manifesto declara `applicability=required`;
- `perceptual_motion_unvalidated` exige simultaneamente motion GIF, aprovacao
  humana, screenshot dedicado, SRAM fresca, VDP dump e os quatro eixos
  perceptivos acima de zero;
- contratos road/boss agora possuem schemas e verificacao de simbolos reais no
  runtime; arquivo vazio nao silencia blocker;
- nome placeholder ou divergente entre diretorio, `.mddev/project.json` e
  metodologia gera `project_naming_invalid`;
- `freshness_audit` passou a ser validacao base obrigatoria no schema e no
  validator, protegendo sincronizacao de docs/evidencias;
- statuses vigentes: `project_naming_invalid`, `project_methodology_manifest_missing`,
  `project_methodology_manifest_invalid`, `perceptual_motion_unvalidated`,
  `road_physics_contract_invalid`, `modular_boss_runtime_invalid`;
- os statuses antigos `road_physics_contract_missing` e
  `modular_boss_runtime_missing` ficam apenas como historico e nao sao mais
  produzidos pelo validator.

Validacao TDD inicial:

- `test_project_methodology_governance.ps1`: 16/16;
- `test_schema_contract_gates.py`: 21/21;
- `test_project_bootstrap_qaproof.ps1`: 18/18;
- template canonico limpo: `tools/sgdk_wrapper/modelo/out` removido para nao
  semear ROM, logs ou evidencia stale em projetos novos;
- `SGDK_GetPythonPath` agora testa Python com codigo valido e exige exit code 0,
  evitando falso aviso do preflight sob `StrictMode` + `ErrorAction Stop`;
- bootstrap descartavel confirmado: nome fora do padrao foi bloqueado por
  `project_naming_invalid`; nome canonico nasceu sem placeholders, com
  lifecycle `new`, manifests locais e closeout bloqueado apenas por claims
  `review_required`;
- validacao final do framework: contratos `60/60`, schemas `21/21`,
  metodologia `16/16`, bootstrap `18/18`, registry `59` entries/`82` tags,
  skill framework e template registry aprovados;
- projetos existentes: SMOKE com metodologia `passed` e closeout bloqueado por
  pendencias reais; Celestial bloqueado metodologicamente somente por
  `perceptual_motion_unvalidated`, sem falsos claims de road physics/boss;
- `validate_resources.ps1` agora propaga `freshness_audit_stale` quando um
  freshness report recente declara drift interno, stale ou artefato requerido
  ausente; relatorio novo dizendo "ha drift" nao silencia mais o closeout;
- nenhum status foi promovido para `MESTRE_*`.

## 22. WRAPPER 2026-06-04 - HIGIENE, GDD/TDD TECNICO E COBERTURA AVANCADA

Status: `implemented_validated_without_new_rom`.

Mudancas canonicas:

- criado enforcement executavel de higiene por projeto:
  - `validate_project_hygiene.ps1`;
  - `doc/project_hygiene_manifest.json`;
  - `rascunho/` organizado;
  - bloqueio de artefatos orfaos e entradas externas sem copia local/hash;
- `allowed_external_artifacts` foi descontinuado como permissao de evidencia; evidencia de projeto precisa existir dentro do projeto;
- mudanca de implementacao/arquitetura agora gera drift nominal quando `doc/10-memory-bank.md` ou `doc/changelog/changelog.md` nao acompanham o estado real;
- GDD passou a exigir ambicao tecnica, visual e sonora, tecnicas escolhidas e decisoes rejeitadas/adiadas;
- TDD passou a exigir `technique_selection.application_plan` por tecnica, com funcao, owner, budget/evidencia e fallback;
- registry passou para `version=5`, com `113` entradas, `159` tags e catalogo de cobertura:
  - `doc/05_technical/96_advanced_hardware_technique_coverage.json`;
  - `126` nomes humanos/aliases mapeados para IDs canonicos;
  - `LABORATORIO=49`, `TEORICA_STANDARD=31`, `TEORICA_PRIORITARIA=33`;
  - `MESTRE_STANDARD=0`, `MESTRE_PRIORITARIA=0`;
- material perigoso como HBlank DMA, CRAM overdrive, SAT rewrite mid-frame, direct vector patching, register pinning, SMC, active-display FIFO timing e GCC agressivo permanece `LABORATORIO`;
- claims sem prova, incluindo reducao de overhead SGDK em ate 80%, foram registrados como rejeitados, nao como promessa canonica;
- painel humano principal permanece `doc/05_technical/93_16bit_hardware_mastery_matrix.md`.

Validacao executada nesta etapa:

- `validate_technique_registry.py`: ok, `113` entradas/`159` tags/zero `MESTRE_*`;
- `validate_skill_framework.py`: ok;
- `validate_template_registry.py`: ok;
- schemas: `27/27`;
- game design contracts: `61/61`;
- freshness: passou e propaga `project_documentation_sync_stale`;
- technique usage governance: `3/3`;
- projetos reais:
  - SMOKE_TEST: metodologia e higiene `passed`;
  - Celestial Chase: higiene `passed`; metodologia bloqueada somente por `perceptual_motion_unvalidated`.

Regra factual:

- nenhuma ROM foi rebuildada ou revalidada em BlastEm durante esta curadoria;
- cobertura registrada aumenta capacidade de planejamento e auditoria, mas nao equivale a dominio pratico;
- nenhuma tecnica foi promovida para `MESTRE_*`.

Verificacao final:

- `run_all_contract_gates.ps1 -Mode full`: `combined_status=passed`;
- suites: game design `61/61`, schemas `27/27`, metodologia `16/16`, technique usage `3/3`, higiene `9/9`, bootstrap `22/22`;
- parsers PowerShell editados, JSON canonico e `new_project.sh -n`: ok;
- raiz do workspace sem arquivo tecnico/temporario orfao; template canonico sem `out/`;
- SMOKE_TEST e Celestial Chase: `project_hygiene_ready=true`, `technique_usage_ready=true`, sem blocker de sincronizacao documental;
- ambos permanecem corretamente `ready_for_aaa=false` por pendencias reais de produto/evidencia;
- nenhuma nova execucao de ROM ou validacao BlastEm foi realizada.

## 23. WRAPPER 2026-06-04 - REFERENCIAS EXTERNAS ATIVAS

Status: `implemented_validated_without_new_rom`.

- `validate_project_hygiene.ps1` passou a varrer codigo, scripts, manifestos e documentacao ativa por caminhos absolutos para outro workspace/projeto.
- Novo blocker canonico: `external_path_reference_outside_project`; falha de leitura da auditoria gera `project_hygiene_scan_failed`.
- Diretorios externos copiados exigem inventario SHA-256 e sao verificados arquivo a arquivo; divergencia gera `external_input_inventory_invalid`.
- `naming_policy=portable_descriptive_v1` tornou executavel o padrao de nomes ativos; nomes ambiguos, com espaco ou nao portateis geram `noncanonical_project_entry_name`.
- Dependencias compartilhadas canonicas continuam permitidas; `out/` e `rascunho/` preservam historico/copia local e nao sao tratados como dependencia ativa.
- O Celestial Chase teve source art, derivados historicos e scripts legados copiados para `rascunho/`, com inventarios SHA-256 registrados no manifesto de higiene.
- O template e os dois projetos reais deixaram de herdar hardcode para `F:\Projects\MegaDrive_DEV`.
- `preflight_host.ps1` e `env.bat` agora priorizam obrigatoriamente `sdk/sgdk-2.11/` do workspace ativo; GDK externo bloqueia preflight.
- Closeout real confirmou higiene e manifesto de tecnicas prontos nos dois projetos, mantendo `ready_for_aaa=false` pelos blockers reais.
- Nenhuma ROM foi rebuildada e nenhuma nova sessao BlastEm foi iniciada nesta migracao.

## 24. WRAPPER 2026-06-04 - SINCRONIZACAO DE ESTADO SEM SNAPSHOT

Status: `implemented_validated_without_new_rom`.

- `update_project_changelog.ps1` recebeu `-StatusOnly` para atualizar somente o bloco derivado de `doc/10-memory-bank.md`.
- O modo nao cria snapshots de assets/ROM, nao altera `build_meta.json` e nao acrescenta entrada artificial no changelog.
- Workflows de adocao e build/validacao agora exigem esse modo quando apenas reports, gates ou blockers mudarem.
- `test_changelog_status_sync.ps1` foi incorporado ao gate completo e prova a imutabilidade byte a byte da arvore `doc/changelog/`.
- Os blocos derivados de SMOKE_TEST e Celestial Chase foram sincronizados com seus `validation_report.json` vigentes.
- Freshness real:
  - SMOKE_TEST: `status=ok`, memoria e changelog frescos;
  - Celestial Chase: memoria e changelog frescos, com `scene_contract_compile_report.json` ainda stale e blocker preservado.
- Higiene real: ambos os projetos `passed`, sem blockers.
- Registry: `113` entradas, `159` tags, `LABORATORIO=49`, `TEORICA_STANDARD=31`, `TEORICA_PRIORITARIA=33`, zero `MESTRE_*`.
- Gate completo: `combined_status=passed`; status sync `6/6`, game design `61/61`, schemas `27/27`, metodologia `16/16`, technique usage `3/3`, higiene `9/9`, bootstrap `22/22`.
- Nenhuma ROM foi rebuildada e nenhuma nova sessao BlastEm foi iniciada nesta sincronizacao.

## 25. WRAPPER 2026-06-04 - CICLO FECHADO DE APRENDIZADO LOCAL

Status: `implemented_validated_without_new_rom`.

Politica canonica:

- o agente pode aprender automaticamente somente dentro do projeto ativo;
- `Audit` e read-only e deve ser executado na abertura de projeto novo ou antigo;
- `Capture` escreve somente `doc/agent_learning/learning_ledger.json` e
  `out/logs/project_learning_report.json`;
- toda proposta canonica nasce `not_applied`, com aprovacao humana `pending`;
- nenhuma captura automatica altera `.agent`, regras, skills, workflows,
  schemas, validators, registries ou `lib_case`;
- nenhuma captura automatica promove tecnica para `MESTRE_*`;
- captura repetida sem mudanca semantica preserva o ledger byte a byte.

Implementacao:

- schema versionado: `tools/sgdk_wrapper/schemas/learning_ledger.schema.json`;
- extrator deterministico:
  `tools/sgdk_wrapper/.agent/scripts/extract_project_learning.py`;
- auditor/capturador:
  `tools/sgdk_wrapper/audit_project_learning.ps1 -Mode Audit|Capture`;
- catalogo conservador de owners:
  `tools/sgdk_wrapper/.agent/references/learning_owner_catalog.json`;
- contrato e workflow:
  `project-learning-loop/references/closed_learning_loop_contract.md` e
  `.agent/workflows/project-learning-loop.md`;
- bootstrap/adocao materializa o contexto local ausente sem sobrescrever
  aprendizado existente;
- progressive disclosure usa `candidate_index` compacto antes de carregar
  licoes completas;
- proposta de skill nova so e permitida para gap procedural explicito sem
  owner existente e continua pendente de revisao humana.

Estudo de caso Celestial Chase:

- `11` licoes reais foram extraidas dos registros locais;
- todas receberam evidencia `E1_artifact` e status
  `human_review_required`;
- todas foram deduplicadas para owners canonicos existentes;
- `0` propostas de skill nova, `0` referencias externas aceitas,
  `0` mencoes/promocoes `MESTRE_*`;
- todas as propostas permanecem `pending`/`not_applied`;
- `canonical_promotion_performed=false`;
- comparacao SHA-256 antes/depois da captura confirmou zero alteracoes na
  arvore canonica;
- recaptura real confirmou idempotencia byte a byte.

Validacao direcionada:

- ciclo de aprendizado: `28/28`;
- schemas: `29/29`;
- bootstrap: `23/23`;
- skill framework e template registry: aprovados;
- registry tecnico: `113` entradas, `159` tags, zero `MESTRE_*`.
- gate completo: `combined_status=passed`, incluindo game design `61/61`,
  metodologia `16/16`, technique usage `3/3`, higiene `9/9`, status sync
  `6/6` e ciclo de aprendizado `28/28`;
- higiene real do Celestial Chase: `passed` apos remocao restrita de dois
  diretorios temporarios `__pycache__`;
- metodologia real do Celestial Chase permanece corretamente bloqueada apenas
  por `perceptual_motion_unvalidated`; o ciclo de aprendizado nao contorna
  evidencia perceptiva nem aprovacao humana.

Regra factual:

- o lote do Celestial Chase e uma fila local de propostas, nao uma promocao
  canonica;
- nenhuma ROM foi rebuildada e nenhuma nova sessao BlastEm foi executada
  durante esta implementacao.

## 26. WRAPPER 2026-06-04 - CONCEPT ART DIRECTION CANONICA

Status: `implemented_validated_without_new_rom`.

Curadoria absorvida:

- concept art passou a ser tratada como contrato de direcao visual, nao como
  ilustracao bonita isolada;
- novo guia humano/canonico:
  `doc/03_art/17_concept_art_direction_system.md`;
- `art-direction-selector` agora emite `concept_art_direction_brief` quando
  houver arte nova, sourcing, geracao, traducao ou conversao;
- o brief exige metodo de escolha visual:
  `production_driven`, `gameplay_driven`, `tone_driven`, `market_driven` ou
  combinacao declarada;
- o brief exige nove eixos visuais:
  dimensionalidade, fidelidade/detalhe, cor, luz/sombra, linguagem de formas,
  materialidade, UI, movimento e VFX;
- o brief exige cinco gates:
  escopo/estilo, silhueta/formas, hierarquia de valores, mapa de paleta e
  polish/VFX com sinal de gameplay;
- novos blockers de direcao: `concept_art_brief_missing`,
  `style_chosen_by_taste_only` e `concept_art_gate_failed`;
- `art-creation-sourcing`, `art-onboarding`, `aaa-scene-pipeline` e
  `aaa_scene_v1.json` foram alinhados para exigir o brief antes de prompt,
  busca, geracao ou conversao;
- template `doc/08-bible-artistica.md` agora traz campos objetivos para o
  brief, reduzindo risco de biblia artistica vaga.

Regra factual:

- esta curadoria aumenta a capacidade de planejamento e direcao de arte do
  agente, mas nao valida nenhum asset, ROM ou estilo especifico;
- nenhum projeto foi promovido para AAA e nenhuma nova sessao BlastEm foi
  executada nesta etapa.

## 27. WRAPPER 2026-06-04 - SPRITES, ASSETS E ANIMACAO PIXEL-PERFECT

Status: `implemented_validated_without_new_rom`.

Curadoria absorvida:

- problemas recorrentes de arte lavada, artefatos de cor, halos, ilhas fora
  de personagem e fake pixel art agora possuem donos canonicos claros;
- `character-design` recebeu `arcade_sprite_style_contract` para personagens
  grandes, lutadores, bosses humanoides e promessa arcade/hi-bit:
  proporcao 6-7 cabecas, 80-110 px apenas com metasprite/budget/residencia
  declarados, anatomia blocada e fundo subordinado;
- `character-design` recebeu `material_color_ramp_plan`: highlight, base,
  shadow e dark shadow por material quando o budget permitir, com hue shift
  controlado e sem quantizacao cinza/preta sem funcao;
- `sprite-animation` recebeu `pixel_perfect_animation_pass`,
  `line_cleaning_report`, `subpixel_shading_motion_report` e
  `cluster_motion_review`;
- subpixel visual real continua proibido; micro-movimento so pode existir como
  deslocamento interno de luz/sombra usando cores da rampa aprovada e sem
  alterar silhueta externa;
- `megadrive-pixel-strict-rules` recebeu `fake_pixel_art_rejection` para
  bloquear AA, blur, interpolacao, PLTE inflada, halos, microcores, matte
  residual e downscale que nao seja nearest-neighbor/redesenho nativo;
- `art-conversion-pipeline` agora exige gate anti-fake-pixel-art para fonte
  IA/high-res antes de qualquer promocao para `res/`;
- `art-translation-to-vdp` passou a exigir `native_grid_translation_report` e
  `fake_pixel_art_rejection` quando a fonte IA/high-res virar sprite/sheet;
- `cutscene-cinematic-direction` recebeu special cut-in de golpe como estado
  proprio de FSM, com gameplay pausado, rosto/busto em tiles grandes,
  speed lines/palette flash separados, budget por estado e teardown limpo;
- `aaa_scene_v1.json` foi alinhado com os novos artefatos:
  `arcade_sprite_style_contract`, `native_grid_prompt_contract`,
  `fake_pixel_art_rejection`, `pixel_perfect_animation_pass`,
  `line_cleaning_report`, `subpixel_shading_motion_report` e
  `cluster_motion_review`.

Feedback bank:

- adicionadas heuristicas para:
  - `Sprite Lavado Por Rampa Sem Funcao`;
  - `Fake Pixel Art Em Sprite Gerado`;
  - `Ilhas E Objetos Fora Da Celula Do Personagem`.

Validacao direcionada:

- JSON canonico parseado;
- `validate_skill_framework.py`: aprovado;
- `validate_template_registry.py`: aprovado;
- `test_schema_contract_gates.py`: `29/29`.

Regra factual:

- esta curadoria aumenta a capacidade de produzir, converter e revisar sprites
  memoraveis, mas nao valida nenhum asset especifico;
- nenhuma ROM foi rebuildada e nenhuma nova sessao BlastEm foi executada nesta
  etapa.

## 28. WRAPPER 2026-06-05 - ANIMACAO, VOLUME, FISICA E CUTSCENE BEATS

Status: `implemented_validated_without_new_rom`.

Curadoria absorvida:

- o material de animacao foi assimilado como camada operacional, nao como texto
  solto: estilo, perspectiva, fisica visual, transicao de estados e cutscenes
  agora possuem contratos nomeados;
- `sprite-animation` passou a exigir, quando aplicavel:
  `style_motion_reverse_engineering`, `turnaround_tracking_contract`,
  `motion_physics_contract` e `state_transition_motion_contract`;
- `doc/03_art/07_sprite_animation_standards.md` agora documenta:
  - estilo como restricoes de forma, proporcao, linha e shading;
  - turnaround com tracking lines, volume primitives, foreshortening e pivot;
  - fisica visual com center of mass, gravidade, contato, arcos, timing/spacing
    e inercia secundaria;
- `animation_production_contract.md` foi reorganizado para exigir esses
  contratos antes de key poses, strips, sheet final e QA;
- `premium_motion_direction_contract.md` agora bloqueia locomocao, pulo,
  landing, golpe, dano ou boss sem fisica visual legivel;
- `cutscene-cinematic-direction` recebeu `cutscene_motion_beat_map` e
  `cutscene_panel_animation_contract`, impedindo painel narrativo morto sem
  hold, pan, blink, mouth, reaction, impact motion ou stillness_justification;
- `visual-excellence-standards` recebeu poder de veto para:
  - drift de estilo entre model sheet/key poses/strips;
  - rotacao sem volume rastreado;
  - movimento sem peso/gravidade/arcos;
  - transicao de estado com snap visual;
  - cutscene AAA sem beat visual ou justificativa de quietude;
- `sgdk-runtime-coder` passou a consumir `motion_physics_contract`,
  `state_transition_motion_contract` e `cutscene_motion_beat_map`, preservando
  frame holds, landing, recovery, retorno de cutscene e cadencia planejada;
- `animation_strip_contract.schema.json` aceita referencias opcionais aos
  novos contratos, mantendo compatibilidade com strips antigas;
- `aaa_scene_v1.json` foi alinhado para propagar os novos artefatos em
  planejamento, geracao de arte, julgamento visual, budget e runtime.

Feedback bank:

- adicionadas heuristicas para:
  - `Rotacao Sem Volume Rastreado`;
  - `Movimento Sem Gravidade Ou Peso`;
  - `Estado Que Estala Sem Transicao`;
  - `Cutscene Com Painel Morto`.

Validacao:

- JSON canonico parseado:
  - `tools/sgdk_wrapper/.agent/pipelines/aaa_scene_v1.json`;
  - `tools/sgdk_wrapper/schemas/animation_strip_contract.schema.json`;
- `validate_skill_framework.py`: aprovado;
- `validate_template_registry.py`: aprovado;
- `validate_strip.py --self-check`: aprovado;
- `test_schema_contract_gates.py`: `29/29`;
- `validate_technique_registry.py`: aprovado;
- `run_all_contract_gates.ps1 -Mode full`: `combined_status=passed`.

Regra factual:

- esta curadoria aumenta a proficiencia do agente em animacao memoravel,
  spritesheets corretas e cutscenes com ritmo;
- nenhum asset especifico foi aprovado, nenhuma ROM foi rebuildada e nenhuma
  nova sessao BlastEm foi executada nesta etapa.

## 29. WRAPPER 2026-06-05 - LINEART 1PX E BLOQUEIO ANTES DA COR

Status: `implemented_validated_without_new_rom`.

Auditoria:

- o agente ja cobria proporcao arcade/hi-bit, rampas de 4 tons, hue shift,
  fundo menos saturado, fake pixel art, line cleaning e pixel-perfect;
- a lacuna encontrada era especifica: o esboco de linha 1px em cor escura
  unica aparecia como `outline`/`line weight`, mas nao como etapa canônica
  separada antes de color blocking e shading.

Curadoria aplicada:

- criado o contrato `lineart_blocking_1px` em
  `doc/03_art/08_character_design_standards.md`;
- `character-design` agora exige `lineart_blocking_1px` para personagem
  critico, heroi, lutador, boss, NPC expressivo ou asset autoral;
- `lineart_blocking_1px` define:
  - linha principal 1px, hard-edge, sem AA/blur/alpha;
  - uma unica cor escura temporaria, como azul escuro ou roxo escuro;
  - foco em silhueta, roupa, cabelo, anatomia e volume antes de saturacao;
  - limpeza de degraus, double corners, pixels orfaos e diagonais;
  - mapeamento posterior para outline/dark shadow no `palette_role_map`;
- `art-creation-sourcing` agora deve pedir esse contrato antes de prompt de
  arte final/colorida para personagem critico;
- `visual-excellence-standards` recebeu `lineart_cleanliness_check` como veto
  antes de paleta final;
- `aaa_scene_v1.json` propaga `lineart_blocking_1px` na etapa de geracao de
  arte e bloqueia `lineart_blocking_missing` quando aplicavel;
- `doc/03_art/02_visual_feedback_bank.md` recebeu a heuristica
  `Color Blocking Sem Lineart Limpa`.

Validacao direcionada:

- `aaa_scene_v1.json`: parse OK;
- `validate_skill_framework.py`: aprovado;
- `validate_template_registry.py`: aprovado;
- `test_schema_contract_gates.py`: `29/29`;
- varredura `rg` confirmou o contrato nos docs, skills e pipeline.

Regra factual:

- esta curadoria aumenta a disciplina de criacao de sprites e reduz risco de
  arte lavada, anatomia confusa e contorno corrigido tarde demais;
- nenhum asset especifico foi aprovado, nenhuma ROM foi rebuildada e nenhuma
  nova sessao BlastEm foi executada nesta etapa.

## 30. WRAPPER 2026-06-05 - COMPOSICAO POR ESCOPO E TRILHA MODULAR

Status: `implemented_validated_without_new_rom`.

Auditoria:

- `xgm2-audio-director` ja cobria ownership de canal, XGM2, SFX,
  pause/resume, loop limpo, PCM/DAC, sample audit e adaptive music;
- a lacuna era de processo composicional: o agente nao diferenciava
  rascunho emergencial, loop funcional e trilha modular profissional antes
  de integrar audio no projeto.

Curadoria aplicada:

- `xgm2-audio-director` agora exige `composition_scope_contract` com um dos
  escopos canonicos:
  - `micro_sketch_1m`;
  - `core_loop_10m`;
  - `modular_track_1h`;
  - `silence_intentional`;
- `micro_sketch_1m` ficou restrito a laboratorio, placeholder, loading,
  menu simples, game jam ou prototipo, sem permissao para fechar AAA;
- `core_loop_10m` passou a exigir loop de 8-16 compassos ou equivalente,
  `seamless_loop_report` e ausencia de clique, corte ou fadiga perceptiva;
- `modular_track_1h` passou a exigir A/B ou variacao formal, intro, ponte,
  stinger ou transicao, stems/layers quando aplicavel,
  `frequency_masking_plan` e `adaptive_music_state_map`;
- `doc/05_technical/99_aaa_audio_architecture_guide.md` recebeu a matriz
  "Escopo de Composicao - Contrato de Producao";
- criado `tools/sgdk_wrapper/schemas/composition_scope_contract.schema.json`
  para validar rascunho, loop funcional, trilha modular e silencio
  intencional sem ambiguidade;
- `game_production_v1.json` agora bloqueia:
  - `composition_scope_contract_missing`;
  - `prototype_music_used_as_final`;
  - `seamless_loop_report_missing`;
  - `music_masks_critical_sfx`;
  - `modular_track_stems_missing`;
- `game-director-sgdk`, `project-planner-sgdk` e `qa-hardware-tester`
  passaram a cobrar o contrato de escopo sonoro no planejamento e no QA.

Validacao:

- `game_production_v1.json`: parse OK;
- `composition_scope_contract.schema.json`: parse OK;
- `validate_skill_framework.py`: aprovado;
- `validate_template_registry.py`: aprovado;
- `test_schema_contract_gates.py`: `37/37`;
- `run_all_contract_gates.ps1 -Mode full`: `combined_status=passed`.

Regra factual:

- esta curadoria aumenta a proficiencia do agente como compositor/diretor
  sonoro para distinguir rascunho, loop funcional e score modular AAA;
- nenhum asset de audio especifico foi aprovado, nenhuma ROM foi rebuildada
  e nenhuma nova sessao BlastEm foi executada nesta etapa.

## 31. WRAPPER 2026-06-05 - IDENTIDADE DE MARCA, LOGO E FONTES

Status: `implemented_validated_without_new_rom`.

Auditoria:

- o agente ja possuia regras de HUD, menu, tipografia e excelencia visual;
- a lacuna era tratar logo, press-start, title screen e menu principal como
  overlays funcionais ou fonte generica, sem contrato de marca, leitura em
  escala, fallback e budget VDP;
- o estudo read-only de `Font Padrao [VER.001] [SGDK 211] [GEN] [ESTUDO]
  [TEXTO]` mostrou um caso util de fonte carregada por `VDP_loadFont`, mas sem
  ROM em `out/rom.bin`, sem uso real de texto, sem loop e sem evidencia
  BlastEm; portanto serviu como licao preventiva, nao como padrao aprovado.

Curadoria aplicada:

- criado `tools/sgdk_wrapper/schemas/brand_identity_manifest.schema.json`;
- `brand_identity_manifest` passa a ser exigido quando houver logo,
  press-start, title screen, menu principal ou front-end autoral;
- o contrato exige:
  - alinhamento com genero, tom e GDD;
  - metafora de gameplay subordinada a legibilidade;
  - testes de silhueta, monocromatico, thumbnail e fundo dinamico;
  - fonte display, corpo/HUD/narrativa e glyph manifest;
  - politica proibindo fonte default/generica como identidade final;
  - camadas runtime, fallback estatico, budget e evidencia BlastEm para
    `approved_for_runtime`;
- `production-loop`, `game-design-planning`, `game-director-sgdk`,
  `art-direction-selector`, `visual-excellence-standards`,
  `12_menu_visual_language` e `13_hud_ui_fx_decision_system` foram alinhados;
- `02_visual_feedback_bank` recebeu a heuristica
  `Logo Ou Fonte Generica Como Identidade Final`;
- `framework_manifest.json` passou a rastrear o schema novo;
- a skill `fighting-game-design` recebeu somente os blocos formais que faltavam
  para o validador do framework (`Passa quando` e `Handoff`).

Validacao:

- JSON parse do schema novo e do `framework_manifest.json`: aprovado;
- duplicidade de chaves no schema novo: nenhuma;
- `test_schema_contract_gates.py`: `43/43`, incluindo blockers para fonte
  generica final, thumbnail ausente, metafora que prejudica leitura e runtime
  aprovado sem evidencia BlastEm;
- `validate_skill_framework.py`: aprovado;
- `validate_template_registry.py`: aprovado;
- `run_all_contract_gates.ps1 -Mode full`: `combined_status=passed`.

Regra factual:

- esta curadoria aumenta a proficiencia do agente em branding, logo, fontes e
  front-end AAA para Mega Drive sem substituir o gate real de ROM;
- nenhum logo, fonte ou ROM especifica foi aprovado nesta etapa, e nenhuma nova
  sessao BlastEm foi executada.

## 32. WRAPPER 2026-06-05 - ESCALA, HUE SHIFT, UI PIXEL-PERFECT E HEALTH BAR

Status: `implemented_validated_without_new_rom`.

Auditoria:

- o agente ja possuia regras para fake pixel art, lineart 1px, animacao por
  passes, subpixel por shading, line cleaning, paleta por material e HUD/UI por
  `ui_decision_card`;
- as lacunas reais eram:
  - escala de personagem ainda podia ser tratada como tamanho visual, nao como
    contrato de FOV, hitbox, camera, pivot e carga de animacao;
  - UI/health bar ainda nao tinha contrato machine-readable para grid inteiro,
    atlas, fonte, buffer de dano latente e evidencia runtime;
  - hue shift existia como conceito, mas precisava ficar ligado a rampas de
    material e bloqueio contra straight shading lavado.

Curadoria aplicada:

- `visual_dna_manifest.schema.json` foi endurecido:
  - bbox nominal agora precisa respeitar multiplos de 8;
  - `scale_contract` exige `scale_class`, `scale_lock_status`,
    `gameplay_scale_fit` e `scale_change_policy`;
  - `approved_for_key_poses` exige `scale_lock_status=locked`;
- criado `tools/sgdk_wrapper/schemas/ui_pixel_surface_contract.schema.json`;
- `ui_pixel_surface_contract` cobre health bar, text box, micro-icons, menu
  cursor, mixed UI e title/front-end pixel-perfect;
- health bar agora exige container, buffer de dano latente, fill ativo, drain
  em 1 ou 2 pixels, threshold critico, low-HP feedback e edge hard-aliased;
- `doc/03_art/08_character_design_standards.md` recebeu
  `character_scale_contract` e hue shifting por material;
- `doc/03_art/07_sprite_animation_standards.md` passou a exigir scale lock
  antes de key poses/strips;
- `doc/03_art/13_hud_ui_fx_decision_system.md` recebeu o anexo
  pixel-perfect e a anatomia tecnica de health bar;
- skills atualizadas: `character-design`, `sprite-animation`,
  `visual-excellence-standards`, `megadrive-pixel-strict-rules`,
  `art-conversion-pipeline`, `sgdk-runtime-coder`,
  `megadrive-vdp-budget-analyst` e `game-design-planning`;
- `aaa_scene_v1.json` passou a propagar os contratos de escala e UI
  pixel-perfect no planejamento, arte, budget e runtime;
- `doc/03_art/02_visual_feedback_bank.md` recebeu:
  - `Escala De Personagem Alterada Tarde`;
  - `Health Bar Sem Sistema De Dano Latente`.

Validacao:

- JSON parse dos schemas e pipeline alterados: aprovado;
- duplicidade de chaves nos schemas novos/alterados: nenhuma;
- `test_schema_contract_gates.py`: `51/51`, incluindo blockers para escala
  nao travada, bbox fora de 8px, health bar sem buffer latente, UI fracionaria
  e runtime UI sem evidencia BlastEm;
- `validate_skill_framework.py`: aprovado;
- `self_check_agentic_aaa_contracts.py`: aprovado;
- `run_all_contract_gates.ps1 -Mode full`: `combined_status=passed`, report em
  `out/ci/contract_gates_report.json`.

Regra factual:

- esta curadoria aumenta a proficiencia do agente em escala de personagem,
  rampas de cor com temperatura, UI nativa e health bar de game feel;
- nenhum asset, UI, personagem ou ROM especifica foi aprovado nesta etapa, e
  nenhuma nova sessao BlastEm foi executada.

## 33. WRAPPER 2026-06-05 - CREATIVE DIRECTOR RADAR E PERSONALIDADE PROPOSITIVA

Status: `implemented_validated_without_new_rom`.

Auditoria:

- o agente ja possuia gates tecnicos, visuais, audio, UI, arte autoral e
  especializacao por genero, mas ainda podia agir de forma passiva:
  validar conformidade sem declarar o que faltava para o jogo ficar memoravel;
- o material de benchmark foi classificado como matriz de ambicao por eixo
  (mecanica, level design, audio, visual, game feel, front-end e setpiece), nao
  como fonte de copia;
- a lacuna canonica era transformar "personalidade" em contrato de decisao,
  com propostas rastreaveis, anti-feature-creep e evidencia.

Curadoria aplicada:

- criado `tools/sgdk_wrapper/schemas/creative_director_radar.schema.json`;
- criado exemplo canonico em
  `tools/sgdk_wrapper/.agent/references/agentic_aaa_contracts/examples/creative_director_radar.example.json`;
- `project_bible.schema.json` recebeu `signature_promise` e
  `creative_director_radar_ref` opcionais;
- criado `doc/07_game_design/00_creative_director_radar.md` como diretriz
  humana do radar;
- `game-design-planning` agora semeia `creative_director_radar_seed` para
  projeto novo, reseed, vertical slice, AAA ou lacuna de personalidade;
- `tdd-authoring` agora exige que tecnicas assinatura se liguem a pilar, gap
  aceito ou cena candidata do radar quando ele existir;
- `visual-excellence-standards` agora pode emitir `signature_gap` quando arte,
  cena, HUD, front-end ou efeito estao corretos, mas genericos;
- `production-loop.md` e `game_production_v1.json` passaram a propagar o radar
  no planejamento, TDD, cena e closeout;
- `doc/03_art/02_visual_feedback_bank.md` recebeu
  `Jogo Correto Mas Sem Momento Assinatura`;
- `doc/03_art/00_visual_quality_bar.md` recebeu complemento de assinatura do
  projeto.

Validacao:

- JSON parse dos schemas, exemplos, framework manifest e pipeline alterados:
  aprovado;
- `test_schema_contract_gates.py`: `56/56`, incluindo rejeicao de benchmark
  como source art, radar aprovado com menos de 5 eixos/gaps e feature creep
  guard desligado;
- `validate_skill_framework.py`: aprovado;
- `self_check_agentic_aaa_contracts.py`: aprovado;
- `run_all_contract_gates.ps1 -Mode full`: `combined_status=passed`, report em
  `out/ci/contract_gates_report.json`.

Regra factual:

- esta curadoria aumenta a proficiencia do agente como diretor propositivo:
  ele deve apontar o que esta generico, propor o menor movimento de assinatura,
  mapear docs/owner/evidencia/fallback e respeitar decisao humana de escopo;
- nenhum jogo, IP, asset, musica ou layout de benchmark foi canonizado como
  fonte copiavel;
- nenhum projeto ou ROM especifica foi promovido nesta etapa, e nenhuma nova
  sessao BlastEm foi executada.

## 34. WRAPPER 2026-06-05 - SESSION BOOTSTRAP E MODOS DE OPERACAO

Status: `implemented_validated_without_new_rom`.

Auditoria:

- os dois planos recebidos convergiam na necessidade de um menu inicial,
  modos de operacao, estado validavel e gate de troca de perspectiva;
- o risco principal era criar um segundo framework paralelo ou tornar o menu
  uma burocracia que atrasa tarefas diretas;
- a solucao canonica adotada foi uma camada fina chamada
  `Agent Session Bootstrap`, sem substituir `project-opening.md`,
  `production-loop.md`, `project-learning-loop.md` ou qualquer gate de
  entrega.

Curadoria aplicada:

- criado `doc/AGENT_OPERATION_MODES_PLAN.md` como plano completo e registro de
  decisao;
- criado `tools/sgdk_wrapper/schemas/agent_session_state.schema.json`;
- criado estado neutro em `doc/agent_session_state.json`;
- criado `tools/sgdk_wrapper/show_agent_menu.ps1` para renderizar o menu e
  atualizar estado somente com `-UserConfirmed`;
- criados workflows:
  - `agent-session-bootstrap.md`;
  - `perspective-switch-gate.md`;
  - `agent-training-mode.md`;
  - `laboratory-mode.md`;
  - `curation-mode.md`;
- criadas areas controladas:
  - `SGDK_projects/_agent_training/`;
  - `SGDK_projects/_agent_laboratory/`;
- atualizados `AGENTS.md`, `CLAUDE.md`, `.agents/README.md`,
  `.cursor/rules/session-bootstrap.mdc`, `ARCHITECTURE.md` e
  `framework_manifest.json`;
- `test_schema_contract_gates.py` passou a validar o estado de sessao e
  bloquear modo invalido, consentimento desligado, `idle` com projeto ativo e
  transicao sem confirmacao humana.

Regra operacional:

- quando a sessao for ambigua ou o usuario pedir menu/modo, o agente usa
  `FORGE-16` e oferece:
  `create_new_project`, `analyze_existing_project`, `train_agent`,
  `laboratory` e `curation`;
- pedido direto e claro ignora o menu e segue para o workflow adequado;
- troca de modo ou perspectiva exige consentimento humano;
- treino gera aprendizado local e proposta `not_applied`, nunca patch
  canonico automatico;
- laboratorio e sempre experimento, nunca entrega;
- curadoria canonica exige aprovacao humana, testes e memoria.

Validacao:

- JSON parse de `doc/agent_session_state.json`,
  `agent_session_state.schema.json` e `framework_manifest.json`: aprovado;
- `show_agent_menu.ps1`: renderizacao aprovada;
- `show_agent_menu.ps1 -Action Set` em arquivo temporario: aprovou transicao
  com `-UserConfirmed`;
- `test_schema_contract_gates.py`: `62/62`;
- `validate_skill_framework.py`: aprovado;
- `run_all_contract_gates.ps1 -Mode full`: `combined_status=passed`, report em
  `out/ci/contract_gates_report.json`.

Regra factual:

- esta curadoria organiza a atuacao do agente entre producao, analise, treino,
  laboratorio e curadoria sem alterar o gate final de ROM;
- nenhum projeto, tecnica, asset ou ROM foi promovido nesta etapa;
- nenhuma nova sessao BlastEm foi executada porque a mudanca e de framework
  operacional, nao entrega de jogo.

## 35. WRAPPER 2026-06-07 - CURADORIA DE CASES E LABORATORIOS

Status: `implemented_validated_without_new_rom`.

Auditoria:

- foram avaliados os roots de treino/laboratorio solicitados:
  `_agent_laboratory`, `_agent_training`, `Celestial Chase visual benchmark` e
  `SMOKE_TEST`;
- `adopt_project_methodology.ps1` foi executado nos estudos/projetos
  relevantes; apenas `[ESTUDO]_mugen_sff_showdown_v1` precisou materializar
  manifests ausentes, sem sobrescrever conteudo local;
- validators de metodologia, higiene, aprendizado e recursos foram rodados nos
  estudos/projetos com doc/evidencia propria;
- HYBRIDO e Celestial tinham candidatos uteis, mas varios permanecem com
  `human_review_required`, `evidence_incomplete`, visual gate bloqueado,
  freshness stale ou ausencia de fixture cruzada.

Curadoria aplicada:

- `megadrive-vdp-budget-analyst` agora declara explicitamente que
  `SPR_getUsedVDPSprite()` nao e pressao por scanline; scanline claim exige
  `vdp_scanline_simulator.py`, dump/telemetria equivalente ou auditoria de pior
  quadro;
- `megadrive-vdp-budget-analyst` tambem fixou o eixo de scroll: bandas
  horizontais de parallax usam `HSCROLL_LINE`/`HSCROLL_TILE`, enquanto
  `VSCROLL_COLUMN` altera offset vertical por coluna;
- `sgdk-runtime-coder` recebeu a regra `road_stack_runtime_budget`: evitar
  multiplicacao/divisao em loop de 224 linhas por frame quando tabela,
  diferenca finita ou acumulador fix16/fix32 resolvem, e exigir nova MDRT/
  `runtime_metrics` apos mudanca de equacao de estrada/line scroll;
- `multi-plane-composition` recebeu `populated_extent` e
  `signed_scroll_gutter`: plano VDP maior nao prova continuidade se a arte
  autorada nao cobre o maior deslocamento real;
- lixo gerado em `tools/sgdk_wrapper/modelo/out/` foi removido porque o gate do
  template exige que o modelo canonico nao carregue artefatos de execucao.

Nao canonizado:

- MUGEN SFF/DEF parser/export e `mugen_stage_logical_composition_gate`
  permanecem laboratorio; faltam fixtures cruzadas e politica de degradacao de
  paleta;
- `png_plte_trim_to_16` e `preflight_host_files_count_array_wrap` nao viraram
  skill nova;
- schema `road_physics_contract` nao foi endurecido para Z/collision/parallax
  nesta rodada, porque isso exigiria fixtures e migracao controlada;
- `blastem_automation.psm1` nao recebeu patch novo para captura preta porque a
  rejeicao de PrintWindow quase branco/preto ja estava implementada;
- regras de HYBRIDO sobre anatomia, acting facial, material lock, 48x64 e
  separacao `technical_pass`/`visual_pass` ja estavam cobertas por
  `visual-excellence-standards` e `art-translation-to-vdp`; nao houve skill
  duplicada.

Validacao:

- `validate_skill_framework.py`: aprovado;
- `test_schema_contract_gates.py`: `64/64`;
- `vdp_scanline_simulator.py --self-check`: aprovado;
- `run_all_contract_gates.ps1 -Mode full`: `combined_status=passed`, report em
  `out/ci/contract_gates_report.json`.

Regra factual:

- esta curadoria aumenta a precisao do agente canonico em budget VDP, scroll,
  pseudo-3D/road stack e composicao de planos;
- nenhum projeto, asset, ROM ou laboratorio foi promovido a entrega;
- nenhuma nova sessao BlastEm foi executada porque a mudanca e de framework
  operacional, nao entrega de jogo.

## 36. WRAPPER 2026-06-08 - CONTEXTO DE PRODUCAO E DOCUMENTACAO PROPORCIONAL

Status: `implemented_validated_without_new_rom`.

Problema tratado:

- o agente precisava distinguir jogo AAA, demo tecnica, exercicio, review e
  consultoria antes de iniciar arte, runtime, QA ou parecer final;
- projetos pequenos nao devem receber burocracia de jogo completo, mas jogo AAA
  tambem nao pode escapar de GDD/TDD/spec/QA/asset register/roadmap.

Curadoria aplicada:

- criado `doc/project_context_manifest.json` no template canonico;
- criado `tools/sgdk_wrapper/schemas/project_context_manifest.schema.json`;
- criado `tools/sgdk_wrapper/validate_project_context.ps1`;
- criado `tools/sgdk_wrapper/.agent/workflows/project-context-classification.md`;
- criado `doc/04_project_context_document_matrix.md`;
- adicionados ao template `00-project-brief`, `15-tdd`, `16-ldd`,
  `17-audio-design`, `18-asset-register`, `19-roadmap-risk-register`,
  `20-release-marketing-legal` e `21-review-consulting-context`;
- `adopt_project_methodology.ps1` agora materializa esses arquivos ausentes sem
  sobrescrever projetos existentes;
- `project_context` virou validacao metodologica base.

Validacao:

- `test_schema_contract_gates.py`: `67/67`;
- `test_project_context_governance.ps1`: `10/10`;
- `test_project_bootstrap_qaproof.ps1`: `27/27`;
- `validate_skill_framework.py`: aprovado;
- `validate_template_registry.py`: aprovado;
- `run_all_contract_gates.ps1 -Mode smoke`: `combined_status=passed`, report em
  `out/ci/contract_gates_report.json`.

Regra factual:

- esta curadoria melhora abertura, planejamento e contexto de ajuda do agente;
- nenhum projeto, asset, ROM ou tecnica foi promovido;
- nenhuma sessao BlastEm nova foi executada porque a mudanca e de framework
  operacional, nao entrega de jogo.

## 37. WRAPPER 2026-06-09 - CURADORIA MUGEN SHOWDOWN E HYBRIDO MUAY THAI

Status: `implemented_validated_without_new_rom`.

Estudos usados:

- `_agent_training/[ESTUDO]_mugen_sff_showdown_v1`;
- `_agent_training/HYBRIDO_MUAY_THAI [VER.001] [SGDK 211] [GEN] [ESTUDO] [LUTA]`.

Licoes qualificadas:

- MUGEN Showdown provou que stage grande derivado de SFF/DEF precisa separar
  mundo total, janela visivel, cache/streaming, recurso empacotado e evidencia
  de residencia VDP; `res_graph_report` com BIN customizado nao prova budget
  de runtime;
- relatórios de tilemap gerados por experimento nao podem usar campos soltos:
  o contrato deve aceitar streaming por janela de forma estruturada ou bloquear;
- `tilemap_flag_report` precisa aceitar `frame_index` opcional para assets
  animados/multiframe sem abrir campo arbitrario;
- HYBRIDO mostrou que estabilidade tecnica, PNG/PLTE correto, build e BlastEm
  nao aprovam qualidade artistica: model sheet de lutador so vira fonte de
  producao com escala, turnaround, marcadores de material/paleta e acting
  coerentes.

Curadoria aplicada:

- `scene_tilemap_conversion_report.schema.json` agora aceita
  `world_tilemap_with_camera_window_streaming` e exige `world_dimensions`,
  `viewport_dimensions` e `runtime_streaming`;
- `scene_tilemap_conversion_report.schema.json` aceita a estrategia
  `BIN_CUSTOM_TILE_GRAPHICS_AND_TILEMAP_WINDOW_STREAMING`, mas campos planos
  legados continuam rejeitados por `additionalProperties=false`;
- `tilemap_flag_report.schema.json` ganhou `frame_index` opcional por entrada;
- `mugen_sff_fixture_contract.json` agora exige reports de conversao tilemap,
  flags, conflito de paleta, res_graph, BlastEm e evidencia VDP/VRAM para subir
  status de budget;
- `megadrive-vdp-budget-analyst` agora explicita que streaming MUGEN/stage
  largo nao pode virar `validado_budget` com estimativa ou BIN customizado sem
  evidencia de runtime;
- `visual-excellence-standards` reforca que `authorial_model_sheet` sem escala,
  turnaround, marcadores e mapa de material/paleta e direcao visual, nao fonte
  de spritesheet final;
- `learning_owner_catalog.json` roteia recorrencias MUGEN/window streaming para
  schema + `megadrive-vdp-budget-analyst`, sem criar skill paralela.

Nao canonizado:

- `tools/mugen2sgdk` nao foi promovido; continua exigindo tool-first audit,
  fixture e evidencia antes de uso canonico;
- o parser/conversor MUGEN permanece no maximo laboratorio/teorico ate haver
  fixture cruzada com ROM, BlastEm, visual_vdp_dump/telemetria e budget medido;
- HYBRIDO nao gerou skill nova, porque as regras reais ja pertencem a
  `visual-excellence-standards` e `art-translation-to-vdp`.

Validacao:

- `test_schema_contract_gates.py`: `73/73`;
- `validate_skill_framework.py`: aprovado;
- `validate_template_registry.py`: aprovado;
- JSON parse: schemas alterados, fixture MUGEN, learning owner catalog e
  framework manifest validos.

Regra factual:

- esta curadoria aumenta a competencia do agente em conversao MUGEN/tilemap
  largo, evidencia de residencia VDP e julgamento visual de lutadores 48x64;
- nenhum projeto, asset, ROM, tecnica ou ferramenta foi promovido a entrega ou
  `MESTRE`;
- nenhuma nova sessao BlastEm foi executada porque a mudanca e de framework
  operacional, nao entrega de jogo.

## 38. WRAPPER 2026-06-13 - GATE ARTE + GAME DESIGN PARA ASSETS CRITICOS

Status: `implemented_validated_with_schema_runner_environment_gap`.

Estudo usado:

- `_agent_training/HYBRIDO_MUAY_THAI [VER.001] [SGDK 211] [GEN] [ESTUDO] [LUTA]`.

Licao qualificada:

- o agente nao pode gerar model sheet, background, sprite art, key pose,
  animation strip, sprite sheet final, FX sheet, HUD heroico ou title/menu
  critico apenas por prompt ou validacao tecnica;
- direcao de arte e game design precisam supervisionar a producao antes do
  primeiro prompt/redraw/conversao: GDD/spec, camera, interacoes, papel de
  gameplay, identidade visual, marcadores `must_preserve` e movimento/carismo;
- um model sheet aceito ainda pode conter drift interno, como cabelo diferente
  entre poses, e isso precisa ser resolvido antes de virar fonte canonica.

Curadoria aplicada:

- novo schema `tools/sgdk_wrapper/schemas/art_gameplay_direction_gate.schema.json`;
- novo teste `tools/sgdk_wrapper/ci/test_art_gameplay_direction_gate.ps1`;
- reforco em `SGDK_GLOBAL.md`, agentes `art-director` e
  `game-director-sgdk`, skills de arte, workflows e pipelines;
- novo contrato do estudo
  `doc/contracts/art_gameplay_direction_gate_v009.json`;
- contratos v009 do HYBRIDO sincronizados como rejeitados, nao pendentes.

Validacao:

- `test_art_gameplay_direction_gate.ps1`: `12/12` passed;
- `test_model_sheet_to_sprite_fidelity_report.ps1`: `9/9` passed;
- `test_visual_delivery_gate_required_fields.ps1`: `12/12` passed;
- `test_validation_report_visual_gate_blocker.ps1`: `5/5` passed;
- `test_visual_delivery_gate_report_blocks.ps1`: `13/13` passed;
- HYBRIDO: contexto, metodologia e higiene passaram; `validate_resources`
  retornou `errors=0`, `warnings=9`, `checked=6`; `freshness_audit` retornou
  `status=ok`.
- Captura local de aprendizado: `18` licoes, `18` candidatos,
  `canonical_promotion_performed=false`; os dois registros do novo gate foram
  marcados como `implemented` por diretiva humana desta curadoria.
- Limitacao: `run_all_contract_gates.ps1 -Mode schema` falhou no passo Python
  porque `py` e `jsonschema` nao estao disponiveis no PATH atual; o novo teste
  PowerShell dentro desse runner passou.

Regra factual:

- esta curadoria melhora a inteligencia do agente para preservar coesao,
  personalidade, carisma, contexto de camera/interacao e qualidade grafica;
- a v009 continua rejeitada e nao foi promovida;
- nenhuma ROM nova foi validada como entrega.

## 39. WRAPPER 2026-06-13 - CURADORIA MUGEN SHOWDOWN CAMERA/PALETA

Status: `curated_rework_required`.

Estudo usado:

- `_agent_training/[ESTUDO]_mugen_sff_showdown_v1`.

Licao qualificada:

- stage de luta importado de MUGEN/SFF/DEF nao pode ser aprovado so porque
  aparece no BlastEm;
- `showdown.def` contem deltas por camada, `zoffset`, bounds X/Y e
  `verticalfollow`; esses dados sao contrato de composicao/camera, nao
  metadata secundaria;
- paleta que passa por conflito de tile mas usa remap massivo pode destruir
  vitalidade cromatica, materiais e separacao de planos;
- diagnostico de arte convencional pode dizer `3_no_art` em laboratorio com
  arte aninhada em `work/`, `analysis/`, `evidence/` e viewer SGDK.

Curadoria aplicada:

- criado parecer do estudo:
  `doc/showdown_camera_palette_curation_2026-06-13.md`;
- contexto do estudo classificado como `exercise`;
- memory bank, changelog, asset register e aprendizado local sincronizados;
- reforco em skills canonicas:
  `multi-plane-composition`, `visual-excellence-standards`,
  `art-translation-to-vdp` e `art-asset-diagnostic`;
- feedback bank global atualizado com o padrao
  `Stage Visivel Mas Achatado E Opaco`.

Validacao:

- JSON do contexto/metodologia/asset register/learning ledger: parse OK;
- `validate_project_context`: passed, `context=exercise`, `blockers=0`;
- `validate_project_methodology`: passed, `blockers=0`;
- `validate_project_hygiene`: blocked, `blockers=3`;
- `freshness_audit`: warning, `stale=2`, `missing_required=2`;
- `validate_resources`: failed, `errors=8`, `warnings=6`, `checked=0`;
- `audit_project_learning` via Python embutido: `lessons=13`, `candidates=9`,
  `canonical_promotion_performed=false`;
- `validate_skill_framework.py` falhou por cinco skills de planejamento nao
  alteradas nesta curadoria (`brawler`, `platformer-puzzle`, `racing-sports`,
  `rpg`, `strategy`) sem blocos contratuais `passa quando`/`handoff`.

Blockers registrados:

- `flattened_mugen_parallax`;
- `fighting_stage_camera_contract_missing`;
- `palette_vibrancy_lost`;
- `visual_gate_too_narrow`;
- `nested_lab_art_not_detected`.

Regra factual:

- esta curadoria melhora a inteligencia do agente em camera de palco de luta,
  parallax multi-plano e vitalidade de paleta;
- nenhuma arte nova foi gerada;
- nenhuma ROM nova foi buildada ou validada como entrega;
- a evidencia BlastEm existente continua somente `testado_em_blastem_minimal`
  e `lab_not_delivery=true`.

## 40. WRAPPER 2026-06-17 - ENFORCEMENT DE PROGRESSO E EVIDENCIA

Status: `implemented_validated_without_new_rom`.

Curadoria aplicada:

- `detect_operational_loop.ps1` usa o historico imutavel de
  `doc/changelog/roms/build_v*/build_meta.json`, alerta apos dois ciclos sem
  blocker removido e bloqueia no terceiro sem decisao estrategica;
- `build.bat` exige blocker alvo, categoria e resumo quando ha
  `progress_warning`;
- captura e closeout executam `finalize_emulator_evidence.ps1`, que sela a ROM
  e os artefatos por SHA-256 e rejeita rebuild ou arquivo ausente;
- candidatos conhecidos de aprendizado sao roteados para owners existentes
  antes de qualquer proposta de skill nova.

Validacao:

- regressões de loop, meaningful change e evidence seal: passed;
- `test_scene_closeout_gate.ps1`: passed;
- `test_project_learning_loop.py`: `33/33` via `uv run --with jsonschema`;
- guard do ambiente: `agent_environment_status=ready`.

Limite factual: nenhuma ROM ou evidencia de jogo foi promovida; esta entrega
valida apenas o framework operacional.

## 41. CURADORIA CANONICA DE SKILLS 2026-06-18

Status: `implementado_validado_sem_rom`.

Decisoes:

- 47 owners permanecem na descoberta ativa;
- 13 aliases/tecnicas foram movidos integralmente para
  `.agent/legacy/skills/`, com hash SHA-256 deterministico e restauracao
  testada em fixture temporaria;
- 12 entradas legadas estao `merged`; `code/software-tile-rasterizer` esta
  `experimental` e exige benchmark dedicado;
- o lifecycle registry e o auditor read-only passam a ser a fonte operacional
  para owner ativo, substitutas, budget de contexto e condicoes de retorno;
- os oito owners tecnicos novos e cinco orchestrators foram compactados para
  2.615 palavras no total e receberam contrato `Entrada minima`, `Saida
  minima`, `Passa quando` e `Handoff`;
- a descoberta ativa tem 65.931 palavras; a quarentena removeu 4.111 palavras
  do caminho ativo (5,87% sobre a arvore pre-quarentena projetada);
- apenas `fighting_2d_traditional`, `brawler_belt_scroll`,
  `platformer_precision_2d`, `racing_arcade`, `rpg_turn_based_jrpg` e
  `strategy_tower_defense` permanecem especializacoes ativas;
- demais especializacoes sem schema, validator, owner, teste e opt-in
  simultaneos foram rebaixadas para `deferred`;
- limites arbitrarios de party, magias, fases, tracks, waves e save foram
  removidos dos cinco orchestrators; o dimensionamento pertence ao contrato do
  projeto e ao budget medido.

Validacao:

- framework de skills: passed;
- lifecycle, hashes e restauracao: passed;
- roteamento ativo/ponte `.agents/skills`: passed;
- registry de generos e cinco orchestrators: passed;
- curadoria AAA lifecycle-aware: passed;
- ambiente consultivo: `agent_environment_status=ready`,
  `graph_status=fresh`;
- `git diff --check` global encontrou apenas duas linhas em branco no EOF em
  arquivos preexistentes de `HYBRIDO_MUAY_THAI`, fora desta curadoria.

Limites factuais:

- nenhuma ROM foi gerada;
- nenhuma tecnica ganhou prova de runtime;
- lifecycle `active` significa owner operacional, nao dominio comprovado em
  hardware;
- tecnica experimental continua exigindo fixture, budget e BlastEm;
- documentos historicos podem preservar aliases e contagens antigas, mas nao
  sao rotas operacionais.

## 42. CURADORIA CLAIM → EVIDENCIA → ROM 2026-06-18

Status: `implementado_validado_sem_rom_nova`.

- criado `audit_promotion_claims.ps1` com schemas de manifesto e relatorio;
- `scene_closeout_gate.ps1` executa o auditor antes de freshness;
- claims fortes exigem hash da ROM, escopo observado e reconciliacao
  conservadora;
- MTR nao prova performance MDRT;
- asset procedural e score automatico nao provam arte premium;
- modulo presente/integrado nao prova reachability/runtime;
- crash, corrupcao visual e review bloqueado impedem avancar de fase;
- suite de pressao: 10/10 cenarios bloqueados;
- regressões de closeout, selo de evidencia, quarentena visual e freshness:
  passed.

Limite factual: nenhuma ROM foi buildada ou promovida nesta curadoria.
## 43. Coesao final da curadoria canonica (2026-06-19)

- O roteamento canonico foi reduzido a owners ativos e validado por schema proprio.
- Skills arquivadas permanecem no legado com hash e possibilidade de reversao, mas nao participam de roteamento, manifesto ativo ou bootstrap.
- Especializacoes de genero sao opt-in: seis permanecem ativas e as demais ficam diferidas ate possuirem schema, validator, testes e necessidade concreta.
- O gate agregado de curadoria cobre framework, lifecycle, rotas, registro de generos e contratos dos orchestrators.
- Status operacional: `validated_framework_no_rom`.
- Gate agregado, lifecycle, rotas e especializacoes passaram em 2026-06-20.

## 44. Aprendizado canonico do Celestial Chase Revive (2026-06-19)

- Curadoria humana autorizada promoveu somente invariantes comprovadas e de
  baixo risco; automacoes novas permanecem em piloto.
- A triagem canonica agora separa `host_executor`, `toolchain_wrapper`,
  `rom_runtime` e `creative_quality`.
- Metadados RESCOMP, input observado, hash da ROM e independencia entre
  fechamento tecnico e promocao criativa passaram a ser regras explicitas.
- Nao foram criadas novas skills redundantes. O conhecimento foi integrado por
  protocolo, workflow, route map, registro auditavel e gate contratual.
- Registro:
  `tools/sgdk_wrapper/.agent/references/celestial_chase_canonical_learning_review_2026-06-19.json`.
- Estado: `validated_framework_no_rom`.
- `test_celestial_chase_canonical_learning.ps1` passou dentro do gate agregado
  em 2026-06-20.

## 45. Fechamento de verificacao da curadoria (2026-06-20)

- `test_canonical_skill_curation.ps1`: passed;
- lifecycle: 13 owners ativos e 13 payloads legados, hashes reversiveis;
- `test_project_learning_loop.py`: 33/33;
- schemas: 73/73;
- startup/Graphify: 28/28;
- regressao de update Graphify recusado: passed;
- runner global passou a usar `uv run --with jsonschema`, sem depender de
  pacote Python global;
- guards de promocao e wrappers de registry foram sincronizados ao registry
  v3, sem dependencia de campos aposentados;
- smoke global de contratos: `combined_status=passed`;
- Graphify nao grava mais freshness quando o processo externo falha;
- nenhuma ROM, runtime, budget VDP ou claim AAA foi promovido por esta
  verificacao de framework.

## 46. Curadoria visual-first project lifecycle (2026-06-28)

Status: `curated_framework_no_rom`.

Projetos auditados:

- `_agent_laboratory`: raiz agregada de laboratorio, nao entrega AAA;
- `_agent_training`: raiz de treino, util para licoes apos promocao humana;
- `BLUE_CIRCUIT`: `aaa_game` em rota positiva visual-first, com fonte/gates
  antes de runtime final;
- `Celestial Chase Revive`: `aaa_game` com runtime tecnico, mas
  `creative_quality=blocked` por `visual_gate_blocked`;
- `Celestial Chase visual benchmark`: `technical_demo` util para movimento,
  budget e captura, ainda nao entrega;
- `SMOKE_TEST`: fixture smoke/lab, nao referencia de maturidade visual.

Licao canonica: BLUE_CIRCUIT avancou melhor porque estabilizou promessa visual,
fonte premium, aprovacao humana e bloqueio de runtime antes de transformar o
projeto em loop tecnico. Celestial Chase Revive preserva valor tecnico, mas e o
alerta de que ROM, rota, screenshot e correcoes pequenas nao substituem
direcao visual, animacao, fonte aprovada e gate perceptual.

Curadoria aplicada:

- novo workflow `tools/sgdk_wrapper/.agent/workflows/visual-first-project-lifecycle.md`;
- `production-loop.md` agora consulta esse workflow em projeto novo, reseed,
  retomada, amadurecimento, revisao e closeout visual;
- `visual-excellence-standards` e `sgdk-build-wrapper-operator` bloqueiam
  build que nao ataque o blocker visual dominante;
- `SGDK_GLOBAL.md` declara que `technical_runtime_creative_blocked`,
  `lab_evidence_not_delivery` e `smoke_only` nao podem virar progresso AAA por
  inercia de build.

Validacao:

- `assert_agent_environment.ps1`: `agent_environment_status=ready`;
- framework de skills: passed, 47 active e 13 legacy;
- schemas contratuais: 78/78;
- `run_all_contract_gates.ps1 -Mode smoke`: `combined_status=passed`.

Limite factual: nenhuma ROM, asset, benchmark ou projeto foi promovido a AAA
por esta curadoria. A mudanca fortalece o agente canonico e reduz diagnostico
repetido, mas cada jogo ainda precisa evidencias proprias de fonte, VDP,
BlastEm, animacao, audio, level design e aprovacao humana.
## 47. Contrato canonico de traco autoral (2026-07-04)

- Um style ID e referencias historicas nao bastam para impedir arte generica.
- O catalogo `angular_cps2_fighter` agora carrega `authorial_line_contract` com
  assinatura de linha, gramaticas de rosto/maos/materiais, assimetria e hooks
  de silhueta.
- `SGDK_GLOBAL.md`, `art-creator.md`, `art-director.md` e o quality bar vetam
  claims AAA quando o contrato falta ou quando o resultado e competente mas
  intercambiavel.
- Projetos devem especializar o contrato global em um arquivo local e propagar
  os mesmos campos aos prompts; adjetivos vagos e listas de referencias nao
  substituem regras visuais operacionais.
- Validacao aplicada em MARE_BRAVA com lote apenas `source_candidate`; nenhuma
  ROM, budget VDP ou promocao para `res/` foi inferida.

## 48. Diagnostico global de capacidade e backlog de correcao (2026-07-18)

Status: `diagnostic_registered_no_runtime_promotion`.

- diagnostico humano-operacional:
  `doc/agent_learning/agent_capability_diagnostic_2026-07-18.md`;
- backlog machine-readable:
  `doc/agent_learning/agent_capability_remediation_backlog_2026-07-18.json`;
- prompt executor persistente:
  `doc/agent_learning/agent_remediation_execution_prompt_2026-07-18.md`;
- classificacao atual do framework: `functional_with_human_supervision`;
- claim ceiling global: `technical_vertical_slice_candidate`;
- `ready_for_aaa=false`;
- blocker dominante: o gate visual aceitou uma captura praticamente branca de
  BLUE_CIRCUIT apesar de runtime parcial e metricas perceptuais zeradas;
- regra nova de trabalho: corrigir primeiro a validacao semantica de evidencia
  (`P0-001`) e depois reconciliar claims pelo menor status provado (`P0-002`);
- o utilitario untracked `tools/image-tools/screenshot_integrity.py` detectou o
  caso, mas continua apenas candidato a integracao ate review, testes e entrada
  no fluxo canonico;
- blockers adicionais: `jsonschema` ausente na sessao, 13 hashes lifecycle
  divergentes, evidencias historicas/stale e ausencia de hardware real e
  metricas de autonomia;
- nenhum projeto, ROM, asset, tecnica ou claim AAA foi promovido por este
  registro.

Continuidade: agentes devem consumir o backlog JSON, selecionar um unico item
`ready_for_assignment`, executar os acceptance checks e atualizar memoria e
changelog sem exceder o menor gate comprovado.

## 49. P0-001 — gate semantico de screenshot fechado (2026-07-18)

Status: `framework_gate_validated_no_runtime_promotion`.

- A captura canonica quase branca de BLUE_CIRCUIT agora falha com
  `blank_or_low_information_capture`.
- O report canônico registra SHA-256, dimensoes, `dominant_ratio`,
  `edge_density`, decisao e impactos de claim.
- Capturas escuras de Celestial Chase Revive e MUGEN permanecem validas no
  gate de integridade; essa validade nao prova qualidade, gameplay ou
  performance.
- `capture_blastem_evidence.ps1`, `finalize_emulator_evidence.ps1`,
  `scene_closeout_gate.ps1` e `validate_resources.ps1` consomem a mesma
  decisao semantica.
- Na validacao real de BLUE_CIRCUIT, `visual_gate_ready=false`,
  `gameplay_rom_aprovada=false`, `blastem_gate=false`, gameplay e performance
  ficaram `unproven`.
- Regressao: Python 3/3, integracao PowerShell passou, closeout plan passou e
  schemas passaram 81/81.
- Evidencia:
  `doc/agent_learning/p0_001_screenshot_semantic_remediation_report_2026-07-18.json`.
- `P0-001=completed`; blocker dominante promovido para `P0-002`.
- Nenhuma ROM, tecnica, asset, status de runtime ou claim AAA foi promovido.

## 50. P0-002 — reconciliacao conservadora de claims (2026-07-18)

Status: `framework_gate_validated_no_runtime_promotion`.

- `reconcile_claims.py` aplica `lowest_proven_status_wins` aos reports de
  validacao, entrega visual, admissao de runtime, metricas, emulador, gate de
  screenshot e selagem de evidencia.
- Gate bloqueado e claim positivo agora geram `report_status_conflict` e
  forcam `ready_for_aaa=false`.
- `capture_status=partial` força performance `unproven`.
- Metricas perceptuais integralmente zeradas forcam `creative_ready=false`.
- ROM e `evidence_session_id` ausentes ou divergentes recebem blockers
  explicitos; reports de uma decisao positiva precisam compartilhar ambos.
- BLUE_CIRCUIT foi reconciliado como bloqueado: `technical_ready=false`,
  `creative_ready=false`, `ready_for_aaa=false`, performance `unproven`.
- Regressao Python passou 4/4 e o report real passou pelo schema Draft 2020-12.
- Evidencia:
  `doc/agent_learning/p0_002_claim_reconciliation_report_2026-07-18.json`.
- `P0-002=completed`; blocker dominante promovido para `P0-003`.
- Nenhum runtime, ROM, tecnica ou claim AAA foi promovido.

## 51. P0-003 — schemas reproduziveis no Linux (2026-07-18)

Status: `framework_environment_validated_no_runtime_promotion`.

- PowerShell 7.6.2, Temurin JRE 21.0.11+10 e dependencias Python possuem
  provisionamento local ao workspace; os binarios externos usam SHA-256
  fixado.
- `jsonschema==4.25.1` e dependencias transitivas estao fixados com hashes em
  `linux_python_requirements.lock`.
- `ensure_linux_python_deps.sh` reconstruiu com sucesso um target limpo sem
  instalacao global/manual.
- `run_contract_gates_linux.sh` prepara PATH/PYTHONPATH e executa o runner
  canonico; falha de dependencia produz blocker explicito.
- Execucao schema: 84/84; gate art/gameplay complementar: 12/12;
  `combined_status=passed`.
- Evidencia:
  `doc/agent_learning/p0_003_reproducible_schema_environment_report_2026-07-18.json`.
- `P0-003=completed`; blocker dominante promovido para `P0-004`.
- BlastEm ainda nao foi reexecutado nesta sessao e nenhum runtime foi
  promovido.

## 52. P0-004 — hashes lifecycle reconciliados (2026-07-19)

Status: `framework_lifecycle_validated_no_runtime_promotion`.

- Os 13 payloads legados foram comparados com o commit de introducao
  `35dab34df2a8f12a577e9a30e0ab9f0092db0443` e permaneciam identicos, com
  arvore de trabalho limpa; as divergencias foram classificadas como
  `registry_obsolete_at_introduction`, nao como corrupcao.
- O algoritmo canonico passou a usar caminhos relativos, ordem ordinal UTF-8,
  normalizacao LF para texto e manifesto `path + NUL + sha256 + LF` em Python
  e PowerShell.
- O registry foi atualizado somente depois do report de review; o report
  posterior classificou os 13 registros como `already_consistent`.
- `validate_skill_framework.py` passou com 47 skills ativas e 13 legadas;
  o auditor lifecycle passou sem erros e o teste de restauracao reversivel
  tambem passou.
- Evidencia:
  `doc/agent_learning/p0_004_legacy_hash_reconciliation_report_2026-07-19.json`.
- `P0-004=completed`; blocker dominante promovido para `P0-005`.
- Nenhuma ROM, runtime, qualidade visual, performance ou claim AAA foi
  promovido.

## 53. P0-005 — bundle fresco da mesma sessao (2026-07-19)

Status: `blastem_front_end_evidence_sealed_no_aaa_promotion`.

- BlastEm Linux 0.6.2 foi provisionado pelo Flatpak oficial, fixado no commit
  `c1f3f4435e9d009fa001322e26e73e785fe443fcedfae1f3187836685c602221`.
- A sessao `blastem-linux-20260720T023600Z-152199` observou o front-end de
  Celestial Chase Revive na ROM
  `4c8302405accc7d414e2f29e0f77f3c4cdbac1f34f7d5760e5934ff48342d60e`.
- ROM, screenshot, SRAM, dump VLAB e metricas carregam o mesmo `session_id`,
  SHA-256 completo e timestamp; `freshness_report.status=ok`.
- Screenshot 640x480 passou o P0-001 com `dominant_ratio=0.407383` e
  `edge_density=0.080358`.
- O closeout agora revalida hashes, sessao e ROM corrente; fixtures provam
  bloqueio por stale, tamper e ROM divergente.
- A janela mostrou 60.9 fps e o VLAB reuniu 900 amostras, mas performance
  continua `unproven` porque esta captura isolada nao fecha uma janela
  sustentada.
- Mastering continua `mastering_needs_fix`: checksum/regiao/evidencia fresca
  passam, enquanto validacao limpa e closeout do jogo nao passam.
- Evidencia:
  `doc/agent_learning/p0_005_fresh_same_session_evidence_report_2026-07-19.json`.
- `P0-005=completed`; blocker dominante promovido para `P1-001`.
- Nenhum claim de gameplay amplo, audio, performance estavel, qualidade
  criativa ou AAA foi promovido.

## 54. P1-001 — discovery de arte laboratorial aninhada (2026-07-19)

Status: `framework_art_discovery_validated_no_runtime_promotion`.

- `art_diagnostic.py` agora reconhece o cenario
  `4_lab_nested_art_review` quando arte existe em `work/`, `analysis/`,
  `evidence/`, entradas de `rascunho/` ou subprojeto SGDK aninhado.
- O report separa `source_art`, `evidence_art`, `active_res_art`,
  `lab_work_art`, `analysis_art` e artefatos gerados; captura de evidencia nao
  e tratada como asset ativo.
- O discovery fica confinado ao root, usa `followlinks=false` e ignora arquivos
  e diretorios symlink; a regressao com alvo externo confirmou que nenhum
  arquivo externo entrou no inventario.
- A contagem de pixels usa `get_flattened_data` no Pillow atual e preserva
  fallback para releases anteriores; `DeprecationWarning` promovido a erro nao
  falhou.
- A suite passou 46/46 checks.
- O estudo MUGEN passou de `3_no_art`/exit 2 para
  `4_lab_nested_art_review`/exit 0, com 90 artefatos visuais descobertos:
  9 fontes, 3 evidencias, 5 recursos ativos e 73 imagens de trabalho; um
  viewer SGDK aninhado com hygiene manifest foi identificado.
- Evidencia:
  `doc/agent_learning/p1_001_nested_lab_art_discovery_report_2026-07-19.json`.
- `P1-001=completed`; blocker dominante promovido para `P1-002`.
- O estudo continua `controlled_training_area`; nenhuma conversao, ROM,
  qualidade visual, budget, runtime ou claim AAA foi promovido.

## 55. P1-002 — pipeline musical XGM2 FM/PSG (2026-07-19)

Status: `technical_complete_pending_external_human_audio_review`.

- Celestial Chase visual benchmark substituiu o score PCM_CH1 por
  `mus_chase_core`, XGM2 real com duas vozes YM2612 FM e pulso SN76489 PSG.
- XGM2 passou a ser owner unico de FM/PSG; PCM_CH1 fica reservado, PCM_CH2
  protege cues criticos e PCM_CH3 atende movimento/UI/pressao.
- `validate_audio` passou com 1 musica, 9 SFX, zero issues e 0,96% do budget.
- A ROM SGDK 2.11 foi buildada no container Linux recomendado pelo SGDK:
  SHA-256 `8eeef763a86f0997b83d9305971bf9aef6e598d18afd3151604e47117f02d450`.
- Bundle atual `blastem-linux-20260720T032218Z-267076` passou frescor/hash;
  AUD2 registrou 8 amostras music+SFX, 5/5 SFX aceitos e DMA wait maximo 0.
- A captura WAV tem 24,064 s, sinal presente e nenhum clipping digital.
- Warning conservador: 1 missed frame XGM2 em 1.363 frames; pico de carga 92.
- Evidencia:
  `doc/agent_learning/p1_002_xgm2_fm_psg_runtime_report_2026-07-19.json`.
- O item nao foi marcado `completed`: a revisao auditiva humana continua
  externa e pendente em `doc/human_audio_review_p1_002.md` do projeto.
- O blocker dominante avanca para `P1-003`; nenhum claim AAA/release foi
  promovido.

## 56. P1-003 — performance em janela completa NTSC/PAL (2026-07-20)

Status: `scene_3_performance_validated_in_blastem_windows`.

- BLUE_CIRCUIT passou de 32 amostras parciais para 900 quadros NTSC ou 750
  PAL, com flag explicita de conclusao e exportacao SRAM somente ao final.
- A medicao de DMA ocorre depois de `SPR_update` e antes do VBlank; o VLAB foi
  normalizado e o heartbeat pos-exportacao foi bloqueado para nao corromper a
  serie selada.
- ROM SGDK 2.11: SHA-256
  `40b924f7895386458c7810204464fe47207c40b7f97d0c4585e840ee8d21bbf5`.
- NTSC `blastem-linux-20260720T040940Z-424385`: 900/900, P95 44, max 44,
  zero over-budget, titulo 61.0 fps.
- PAL `blastem-linux-20260720T041233Z-435741`, forcado com `-r E`: 750/750,
  P95 17, max 17, zero over-budget, titulo 50.3 fps.
- Pico observado: 4 sprites ativos, 3/scanline, DMA 1 entrada/40 bytes.
- Freshness passou em ambos os bundles; parser 10/10; screenshot e schemas
  passaram.
- Evidencia:
  `doc/agent_learning/p1_003_full_window_performance_report_2026-07-20.json`.
- `P1-003=completed`; blocker dominante promovido para `P1-004`.
- O claim limita-se a cena 3 observada. Audio, outras cenas, hardware real,
  FPGA, release e AAA nao foram promovidos.

## 57. P1-004 — gate de hardware real ou FPGA (2026-07-20)

Status: `technical_gate_complete_external_session_missing`.

- Criados schema, validador e protocolo para sessao em console original ou
  FPGA, com identidade de dispositivo/regiao/revisao, carga/firmware, ROM,
  captura, decisoes de timing/audio e atestacao externa.
- O validador compara a ROM corrente com o bundle BlastEm aprovado, verifica
  hash/arquivo da captura e exige provas de boot, input, audio e gameplay.
- Regressao passou 3/3: fixture aceita, pendente bloqueado e hash divergente
  bloqueado.
- O mastering da ROM `40b924f7...d21bbf5` confirmou 262144 bytes, alinhamento,
  header JUE e checksum SGDK `sizebnd` `0x1527`.
- A sessao real continua pendente; o agente nao preencheu dispositivo, video
  nem atestacao humana.
- Evidencia:
  `doc/agent_learning/p1_004_hardware_gate_report_2026-07-20.json`.
- `P1-004=blocked_external_hardware_evidence`; blocker executavel avanca para
  `P1-005`.
- Nenhum claim de hardware real, release ou AAA foi promovido.

## 58. P1-005 — autonomia e intervencoes instrumentadas (2026-07-20)

Status: `framework_process_metrics_validated`.

- Criados schema, gravador atomico de eventos e derivador de metricas para
  inicio, conclusao, bloqueio, retrabalho e intervencao humana.
- Intervencoes aceitam somente categoria e reason code de allowlist; o gravador
  nao possui campo de texto humano e fixa `sensitive_content_stored=false`.
- A regressao passou 3 checks, incluindo rejeicao de intervencao sem categoria
  e derivacao exata das taxas.
- A sessao real registrou 9 eventos: 3 tarefas iniciadas, 2 concluidas, 1
  bloqueada e 1 refeita; completion 0,6667 e first-attempt success 0,5.
- Nao houve intervencao humana classificada na amostra real; a fixture cobre
  `correction` sem conteudo sensivel.
- Todo report fixa `quality_claim=unproven` e `ready_for_aaa=false`.
- Evidencia:
  `doc/agent_learning/p1_005_autonomy_instrumentation_report_2026-07-20.json`.
- `P1-005=completed`; P1-006 continua bloqueado pelas dependencias externas e
  o proximo item executavel e `P2-001`.

## 59. Checkpoint de curadoria do aprendizado da remediacao (2026-07-20)

Status: `captured_validated_pending_maturity`.

- O responsavel humano autorizou registrar os aprendizados ja maduros e manter
  os demais pontos em fila retomavel conforme novos insumos cumprirem seus
  criterios de maturidade.
- O checkpoint humano e machine-readable vive em:
  - `doc/agent_learning/remediation_learning_curation_checkpoint_2026-07-20.md`;
  - `doc/agent_learning/remediation_learning_curation_checkpoint_2026-07-20.json`.
- O BLUE_CIRCUIT recebeu registros locais de falhas, sucessos, candidatos e
  revisao de promocao em `doc/agent_learning/` do projeto; o ciclo Capture
  consolidou 15 licoes e 10 candidatos no ledger.
- Os cinco gaps procedurais foram deduplicados contra owners existentes; no
  ledger final existem 6 propostas `patch_existing_owner`, todas
  `not_applied`, e nenhuma proposta aplicada.
- Validacao: schema passou, Audit posterior foi read-only e a regressao do
  project learning loop passou 34/34.
- Itens integrados e verificados: P0-001 a P0-005 e P1-001.
- P1-003 possui prova runtime local forte, mas a generalizacao do probe exige
  segunda cena/projeto e parametros em vez de constantes do BLUE_CIRCUIT.
- P1-002 continua pendente de review auditivo humano; P1-004 continua pendente
  de hardware/FPGA real; P1-005 possui instrumentacao validada com amostra
  longitudinal ainda pequena.
- P2-001 foi iniciado, mas nao fechado; P2-002 e P2-003 ainda nao foram
  executados. A retomada conservadora comeca por P2-001.
- Esta captura nao aplicou patch canonico novo, nao promoveu tecnica, ROM,
  release ou `ready_for_aaa` e manteve
  `canonical_promotion_performed=false`.

## 60. Regra anti-falso-positivo para sprites e revalidacao (2026-07-24)

Status: `framework_gate_added_projects_revalidated`.

- Um strip que passa apenas dimensoes, paleta, index 0 e grid deve receber no
  maximo `technical_pass`; isso nao autoriza `visual_pass`.
- O novo `sprite_artifact_report.v2` e obrigatorio e mede clipping de borda,
  ilhas soltas, anatomia, pivot, contato de pes e delta entre frames.
- `validate_resources.ps1` rejeita report antigo, `visual_pass=false` ou
  qualquer um dos seis controles ausente.
- BLUE_CIRCUIT: strips antigos retraidos como
  `technical_pass_visual_fail`; player v002 reconstruido em 24x32, 14 frames
  sem findings, ROM `b2fbb1...e0b5` e bundle BlastEm fresco sem blockers.
  A aprovacao e estritamente `sprite_visual_pass`, nao `ready_for_aaa`.
- Celestial Chase Revive: Lio permanece `technical_pass_visual_fail` com 77
  blockers. A ROM `a69050...d26` mostrou `ANIM_DAMAGE` real em rajada
  BlastEm, mas a screenshot foi corretamente reprovada como
  `blank_or_low_information_capture`.
- Nunca converter compilacao, ResComp ou screenshot de boot em aprovacao de
  anatomia/animacao. O claim deve citar o artefato exato e seu limite.

## 61. Roteamento de compilacao SGDK por host e proveniencia LTO (2026-07-29)

Status: `canonical_rule_implemented_and_locally_validated`.

- A compilacao SGDK agora começa por
  `tools/sgdk_wrapper/select_sgdk_build_route.py`, que registra host,
  compilador, produtor/LTO de `libmd.a`, rota, blockers e teto de status em
  `out/logs/sgdk_build_route_report.json`.
- Linux usa exclusivamente
  `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh --project-root <projeto>`:
  staging isolado, executaveis SGDK via Wine e `libmd.a` reconstruida sem LTO
  pelo compilador empacotado. O SDK canonico de origem nao e mutado.
- Windows usa `tools/sgdk_wrapper/build.bat <projeto>`. Se a `libmd.a` contiver
  LTO de major diferente do `gcc.exe`, o build fica bloqueado ate a biblioteca
  ser restaurada ou reconstruida com o compilador empacotado. A bridge Linux
  nao e workaround Windows.
- Regra causal: ResComp e compilacao C aprovados seguidos de falha no link
  mantem o diagnostico em `toolchain_wrapper`; o agente nao deve editar codigo
  ou assets sem evidencia de erro nessas camadas.
- A skill `sgdk-build-wrapper-operator`, seu metadata e o workflow
  `production-diagnostic-triage` foram curados com a matriz Linux/Windows; o
  `preflight_host.ps1` materializa e verifica automaticamente o report quando
  recebe `ProjectRoot`.
- Enforcement nas entradas: `build_sgdk_wine_bridge.sh` chama o seletor antes
  do staging, e `build.bat` chama o preflight de rota antes do make. Projeto
  com `ProjectRoot` e sem Python agora bloqueia, pois nao pode provar a rota.
- Validacao no MARE_BRAVA: GCC 13.2.0 versus biblioteca canonica LTO 16.1.0;
  staging GCC 13.2.0 sem LTO; ROM de 262144 bytes, SHA-256
  `8ed8f28bde41cc4987718079f7584c6d90cbe1cad22a73f1b953857b367a434d`.
- O resultado prova `buildado_emulator_pending`, nao
  `testado_em_emulador`, gameplay, performance, audio, hardware ou AAA.

## 62. Curadoria generica de arte, claims, bootstrap e Linux (2026-07-30)

Status: `canonical_framework_rules_validated_with_synthetic_fixtures`.

- O diagnostico de arte separa `source_art` de `active_res_art`. Defeitos em
  concept, rascunho, contact sheet ou fonte nao referenciada roteiam conversao,
  mas nao podem contaminar o veredito do grafo `.res` ativo.
- Largura total de strip/sheet nao e tamanho de frame nem prova de metasprite.
  O budget deve usar a celula declarada no `.res` e o report do artefato.
- `sprite_artifact_report.v2` mantem os seis controles obrigatorios: clipping,
  ilhas soltas, anatomia, pivot, contato de pes e delta entre frames. Passar
  formato/paleta/grid sem passar esses controles resulta em
  `technical_pass_visual_fail`.
- O report tambem compara `required_actions` com os strips declarados. Toda
  acao prometida para o slice precisa existir no `animation_state_plan`, no
  artefato visual e no `runtime_animation_timing_map`; caso contrario, deve ser
  implementada ou removida/reclassificada no contrato.
- O closeout executa `audit_doc_sync.py`: ROM atual, memoria, changelog,
  relatorios e claims devem convergir para o menor status comprovado. Historico
  stale continua auditavel, mas nao pode agir como claim atual.
- Projeto novo passa por `reset_new_project_state.ps1`: nenhuma ROM, hash,
  snapshot, aprovacao ou evidencia do modelo e herdada. O nascimento declara
  explicitamente `buildado: nao`, `testado_em_emulador: nao` e
  `ready_for_aaa: false`.
- No Linux, `new_project.sh` restaura o PATH nativo depois de carregar as
  variaveis SGDK, impedindo que executaveis Wine substituam coreutils. O
  companion de cenas e recompilado no projeto novo antes da higiene.
- O bootstrap Python Linux fixa `jsonschema==4.25.1` e `pillow==12.3.0` com
  hashes e confirma que ambas as distribuicoes foram carregadas do target
  local do workspace, nao por acaso do Python global.
- O wrapper Graphify trata `.agent` como diretorio oculto no Unix e compara
  subpaths com o separador nativo da plataforma; workspace com espacos passou a
  fechar `agent_environment_status=ready`.
- Regressao canonica usa apenas fixtures sinteticas e cobre ownership de arte,
  falso positivo visual, cobertura de acoes, screenshot semantico,
  reconciliacao documental e roteamento de build. Projetos em amadurecimento
  nao sao usados como fixture, baseline ou referencia ativa.
- Limite factual: esta curadoria valida regras e infraestrutura do framework.
  Nao valida ROM, gameplay, performance, audio, hardware real, release ou AAA
  de qualquer jogo.

## 63. Inventario transversal de capacidade grafica (2026-08-06)

Status: `documentado_handoff_sem_promocao_canonica`.

- A varredura recursiva de `SGDK_projects/` e `SGDK_Engines/` identificou 10
  iniciativas graficas, 700 arquivos PNG/GIF/SVG e 166 licoes registradas;
  `SGDK_Engines/` estava vazio.
- O relatorio humano vive em
  `doc/curation/GRAPHICS_CAPABILITY_REPORT_2026-08-06.md`, o inventario
  machine-readable em
  `doc/curation/graphics_capability_inventory_2026-08-06.json` e o painel em
  `doc/curation/evidence/graphics_initiatives_board_2026-08-06.png`.
- A convergencia mais forte e um pipeline de veto e refinamento: fonte forte,
  model sheet, key poses, pixel nativo, artifact report, promocao controlada e
  comparacao source/asset/BlastEm. Quantizacao e build continuam gates
  tecnicos, nao aprovacao estetica.
- MARE_BRAVA concentra a rota visual-first mais madura; BLUE_CIRCUIT consolidou
  `technical_pass_visual_fail` e `sprite_artifact_report.v2`; Celestial Chase
  visual benchmark consolidou compare-flat, matte gate e baseline seletiva;
  Hibrido e MUGEN permanecem laboratorios com pendencias explicitadas.
- As tentativas P1, P2, P3 e P4 do Kirby permanecem evidencia negativa. P4 foi
  arquivada em
  `data/archive/p4_2026-08-06_vector_master_anatomy_rejected/` porque limpeza
  vetorial e conformidade flat nao compensaram anatomia/acting incorretos.
- Este registro nao altera skills, schemas ou politica canonica e nao promove
  projeto, asset, ferramenta, ROM, release ou status AAA.

## 2026-08-17 — Diretriz de bloqueio estetico ganhou medicao

Status: `documentado_bloqueio_sem_promocao`.

- A proibicao de grafico procedural como personagem/inimigo/boss/cenario final ja
  existia em `SGDK_GLOBAL.md` (8.2, 17, 22) e em cinco skills de arte, mas era
  prosa: o unico detector estatico era `VDP_drawText >= 8 && SPR_addSprite == 0`, e
  `audit_placeholder_quarantine.ps1` decidia por nome de arquivo e tag declarada.
- Furo fechado: PNG desenhado por `PIL/ImageDraw` e salvo com nome limpo satisfazia
  a letra de "consumir arquivo de imagem externo" e violava a diretriz inteira.
- Contrato novo: `doc/asset_provenance_manifest.json` por projeto, um registro por
  simbolo visual do `.res`, com `source_kind` e `acceptance_status`. Schema em
  `tools/sgdk_wrapper/schemas/asset_provenance_manifest.schema.json`.
- Enforcement novo: `tools/sgdk_wrapper/audit_procedural_asset_provenance.py` casa
  cada arquivo do `.res` com os builders que o escrevem; manifesto que declara
  `hand_authored_pixel` para arquivo escrito por builder de primitivas e detectado
  e bloqueado.
- Baseline retroativa: 9 projetos auditados, 8 bloqueados, 136 simbolos visuais,
  78 rastreados a builders de primitiva. Relatorio humano em
  `doc/curation/ASSET_PROVENANCE_BASELINE_2026-08-17.md`, machine-readable em
  `doc/curation/asset_provenance_baseline_2026-08-17.json`.
- Nenhum projeto sustentava `ready_for_aaa=true`; nao houve selo a revogar. O efeito
  retroativo recai nos tetos de claim (`vertical_slice` em 5, `technical_demo` em 2).
- `[TECHDEMO]` e `[RELEASE]` entraram em `doc/PADRAO_NOMENCLATURA.md` com a regra
  explicita de que a tag de pasta e rotulo humano: a autoridade executavel e
  `context_type` / `delivery_claim_ceiling` / `validator_fixture` no
  `project_context_manifest.json`.
- Excecao nomeada: `validator_fixture: true` dispensa asset externo e em troca prende
  `delivery_claim_ceiling` em `none`/`concept`/`lab`/`exercise`. FORGE_REFERENCE foi
  o primeiro caso e teve o teto corrigido de `technical_demo` para `lab`.
- Este registro nao promove projeto, asset, ROM, release ou status AAA.

## 2026-08-17 (fase 2) — Diretriz estetica residente em cada projeto

Status: `documentado_bloqueio_sem_promocao`.

- A diretriz de bloqueio estetico agora mora dentro de cada projeto, em
  `doc/00-diretrizes-agente.md` (autoridade #4), entre os marcadores
  `diretriz-bloqueio-estetico v1`, com o estado medido daquele projeto e a lista
  nominal dos simbolos escritos por builder de primitivas.
- Injetada em 12 projetos e no template `tools/sgdk_wrapper/modelo/`, portanto
  projeto novo nasce com a diretriz. `new_project.sh` e `new_project.bat` imprimem
  a regra e o comando do auditor no bootstrap.
- Ferramenta idempotente: `tools/sgdk_wrapper/apply_aesthetic_directive.py`;
  `--check` retorna exit 1 se algum projeto estiver sem diretriz ou desatualizado.
- Achado sistemico: `tools/image-tools/build_branding_intro_assets.py` desenha por
  primitiva os 5 simbolos de branding e 8 projetos os consomem como finais. Todo
  projeto que usa a intro herda 5 violacoes por default; corrigir na fonte resolve
  os 8. Decisao de curadoria humana, nao tomada nesta sessao.
- Achado: `SCENE_TILEMAP_CURATION_FIXTURE` nao tem
  `doc/project_context_manifest.json`, logo nao pode declarar `validator_fixture`
  nem teto de claim. Manifesto nao foi inventado; exige classificacao humana.
- Este registro nao promove projeto, asset, ROM, release ou status AAA.

## 2026-08-17 (fase 3) — Causa raiz do procedural e abertura v2

Status: `documentado`.

- Causa raiz encontrada: `doc/15-prompt-telas-assinatura.md`, o prompt mestre das
  telas de assinatura, mandava o agente entregar fallback procedural ("voce nao pode
  encerrar dizendo 'falta gerar assets' se ainda pode entregar a estrutura procedural
  placeholder que compila"). Existia em 10 projetos. Os 78 simbolos procedurais
  vieram de obediencia, nao de preguica.
- Prompt do template reescrito como v2 com politica invertida; banner de revogacao
  inserido nas 10 copias existentes sem alterar o corpo delas.
- `branding_sequence_v2` autorado no template: conceito "A FORJA", tomada continua de
  tres atos, 520 quadros NTSC, zero cortes a preto.
- 28 tecnicas com `registry_id` conferido contra
  `doc/05_technical/93_16bit_hardware_mastery_registry.json`; 4 rejeitadas com motivo.
- Diagnostico medido do v1: 0 sprites de 80, 0 de 20 por scanline, PAL2/PAL3 ociosas,
  nenhum H-Int, Shadow/Highlight nunca ligado — e ainda assim
  `over_budget_frames: 1` e `cpu_load_max: 401`. O spike vem do upload de HScroll por
  CPU e dos `VDP_drawImageEx` na troca de fase; o v2 nao tem troca de fase e usa DMA
  no VBlank. Corrigir isso e o passo 1 da implementacao.
- Fundamento no template: contrato v2, `inc/scenes/branding_v2.h`, 8 declaracoes `.res`
  comentadas e prompt de handoff com portao humano depois do model sheet.
- Nada foi buildado, implementado ou observado em emulador nesta fase.

## 2026-08-17 (fase 4) — Direcao de arte da abertura v2 fechada

Status: `documentado`.

- `doc/branding_v2_art_direction.md` e `doc/art_direction_decision_record.json` no
  template, com as 6 travas da Visual Quality Bar preenchidas antecipadamente. A
  direcao esta fechada; o agente de arte preenche apenas campos `execution_*`.
- Estilo primario `gothic_16bit_dark_fantasy`, secundario `vibrant_16bit_pixel` restrito
  ao emissivo; `baroque_32bit_gothic_pixel` e `digicel_16bit_animation` rejeitados por
  `vram_pressure_hint=high`. IDs conferidos contra `art_style_catalog.json`.
- Decisao central: a forja ilumina de baixo. Plano superior em sombra, face inferior
  iluminada, sombra subindo, contato com o piso como ponto mais quente. Sombra de metal
  quente e fria, nunca cinza neutro.
- Papel de indice de paleta e contrato, hex e seed. `PAL0[9..12]` fecha em ciclo para a
  rotacao de CRAM; `PAL1[13..14]` fica abaixo do branco para o operador de highlight ter
  para onde clarear.
- Model sheet de 5 paineis em 512x384; painel E exige FX a 16x16 real.
- PENDENCIA HUMANA: `trava_5_art_gameplay_direction_gate` com `needs_human_ruling`. Cena
  de marca nao tem consequencia jogavel; proposta e `brand_comprehension_consequence`.

## 2026-08-17 (fase 5) — trava_5 aplicada com eixo substituido

Status: `documentado`.

- `brand_comprehension_consequence` aprovado pela curadoria e aplicado. Escopo estrito:
  cena de marca sem gameplay. Cena jogavel continua obrigada ao eixo canonico; a
  substituicao nao e rota de fuga.
- Regra falsificavel: toda tecnica carrega claim + teste negativo + strength, ou e
  `enabling_discipline`. Tecnica sem classificacao reprova.
- Enforcement novo: `tools/sgdk_wrapper/validate_brand_comprehension_gate.py`, com os
  4 blockers `brand_comprehension_*`. Verificado nas duas direcoes: contrato real
  exit 0, contrato adulterado exit 1 com os 4 codigos.
- O gate achou problema real na primeira execucao: `xgm2_audio_architecture` sem
  justificativa. Reclassificado como `enabling_discipline` porque o ID descreve
  arquitetura de driver, nao afirmacao ao espectador.
- 24 tecnicas: 15 comprehension_bearing, 9 enabling_discipline. Dois claims marcados
  `weak` (`column_scrolling`, `expressive_text_presentation_system`) — exigem prova
  perceptiva no runtime e nao podem ser vendidos como fortes no closeout.
- Limite declarado: o validador prova que ninguem passou sem justificativa; nao julga se
  o claim e verdadeiro. Isso segue humano, contra screenshot e visual_vdp_dump reais.

## 2026-08-17 (fase 6) — Diretriz e gate aplicados nos projetos existentes

Status: `documentado`.

- Dois falsos verdes fechados ANTES de aplicar. Primeiro: o gate procurava tecnicas em
  `acts` (v2) e os projetos usam `screens` (v1) ou um v3 divergente, entao reportaria OK
  em 10 projetos sem julgar nada. Coleta virou varredura recursiva agnostica de formato,
  e contrato ativo sem tecnica declarada virou blocker
  `brand_comprehension_techniques_undeclared`.
- Segundo: `apply_aesthetic_directive.py` descia so um nivel e deixava o viewer aninhado
  em `_agent_training/[ESTUDO]_mugen_sff_showdown_v1/sgdk_viewer/showdown_viewer` sem
  diretriz. Descoberta virou profundidade arbitraria; cobertura 12 -> 13 projetos.
- Gate aplicado: 11 contratos, 10 bloqueados, 1 isento (BLUE_CIRCUIT declarou o contrato
  de branding inativo porque foi substituido pela title screen propria).
- Bloco de diretriz elevado a `diretriz-bloqueio-estetico v2` nos 13 projetos e no
  template, substituindo o v1 sem duplicar, e agora carregando o eixo
  `brand_comprehension_consequence` com escopo estrito.
- A direcao criativa "A FORJA" NAO foi propagada: ficou so no template. BLUE_CIRCUIT e
  SMOKE_TEST tem identidade de branding propria. Propagou-se a exigencia estrutural, nao
  o conceito.
- Higiene: `Celestial Chase Revive/doc/credits_contract.json` nao tem `contract_id`.

## 2026-08-17 (fase 7) — Gate do model sheet construido antes da arte

Status: `documentado`.

- `tools/sgdk_wrapper/validate_model_sheet_contract.py`: 6 checks especificos do contrato
  do model sheet v2, sem duplicar `art_diagnostic.py` nem `art_quality_gate.py`. O
  criterio de aceitacao fica medido antes do agente de arte comecar.
- Convencao adicionada a direcao: paleta do model sheet ordenada como PAL0=0-15,
  PAL1=16-31, PAL2=32-47, PAL3=48-63. Fora dessa ordem o gate nao pode verificar a folga
  de highlight nem o ciclo de brasa.
- Erro meu exposto pela construcao: seeds `0x0630` e `0x0CDD` na direcao de arte usam
  nibbles impares que nao existem no CRAM de 9 bits. Corrigidos para `0x0620` e `0x0CCC`.
- Erro meu exposto pelo teste: "ciclo fechado" definido como fechamento contra o maior
  passo interno e furado — salto interno gigante deixa qualquer fechamento passar, e o
  fixture aberto passou. Trocado por uniformidade do anel (razao <= 3.0) com deteccao
  separada de passo morto.
- Verificado nas duas direcoes com fixtures sinteticas em scratchpad.

## 2026-08-17 (fase 8) — Primeira entrega de arte revisada: rework

Status: `documentado`.

- O agente de arte entregou `model_sheet_forge_v01.png`. A rota de proveniencia
  funcionou: `assemble_model_sheet.py` tem zero primitivas (crop/resize/paste/chroma
  key/remap), fontes autorais em `raw/` com sha256 por painel em
  `model_sheet_lineage.json`. Gate de contrato exit 0.
- O agente declarou `visual_quality_bar_1994: no_not_yet` sozinho. A politica de parada
  honesta que substituiu o mandato de fallback procedural produziu o comportamento
  pretendido na primeira entrega.
- Revisao `rework` em `doc/model_sheet_review_v01.md`. Blockers: wordmark do painel D
  iluminado por cima, em paleta fria em vez da rampa de ferro de PAL1 e sem marca
  assimetrica; martelo do painel A tambem iluminado por cima dentro do painel que existe
  para provar a luz inferior; 4 quadros de brasa que nao formam rotacao; 4 estilhacos que
  ja sao espelhos entre si e colapsam o flip H/V.
- A lei da luz de baixo funciona no painel A: esse e o nucleo da direcao e ele passou.
- Correcao minha: especificar o painel B como "preto sobre transparente" era aperto sem
  ganho. Preto sobre branco e convencao de estudio e le igual. Direcao relaxada.
- Registrar que folga de highlight e ciclo de brasa passam porque o gate le a tabela de
  paleta do PNG, nao o painel C. Perder os rotulos do painel C custa revisao humana, nao
  verificacao mecanica.
