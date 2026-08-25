---
trigger: always_on
---

# SGDK Global Rules

Estas regras sao sempre ativas para qualquer projeto `MegaDrive_DEV` que use esta `.agent`.

## 1. Fonte de verdade

- Leia primeiro `doc/10-memory-bank.md`, `doc/11-gdd.md`, `doc/13-spec-cenas.md`, `doc/00-diretrizes-agente.md` e `doc/00-governance/08_maximalist_directive.md` quando existirem.
- Trate `.mddev/project.json` como manifesto estrutural, nao como substituto dos docs canonicos.
- Nunca trate README isolado como prova suficiente de implementacao ou validacao.
- Todos OS AGENTES DEVEM OBEDECER O **MASTER SYSTEM DIRECTOR** e aplicar a **Filosofia Maximalista**, priorizando excelencia visual e impulsionando o hardware com responsabilidade.

### 1.0.1 Context Pack antes de geracao

- Antes de gerar arte original, prompt de imagem, sourcing externo ou codigo SGDK com API sensivel, declare um `context_pack_manifest`.
- O manifesto deve listar docs canonicos, memoria operacional, source cases, feedback bank, engine profiles e headers SGDK consultados quando relevantes.
- Se `doc/10-memory-bank.md` nao existir no projeto, use `doc/06_AI_MEMORY_BANK.md` como fallback declarado; nao invente outro arquivo de memoria.
- RAG v1 neste workspace significa recuperacao controlada de arquivos auditaveis, nao dependencia obrigatoria de banco vetorial.
- Nao solicite nem exponha Chain of Thought; use `route_decision_record`, `art_generation_brief`, `master_style_manifest`, `qa_findings` e `correction_request`.

### 1.0.2 Isolamento de projeto e proficiencia de tecnicas

- Todo material especifico de um projeto deve nascer dentro do proprio projeto: codigo, headers, scripts locais, docs, manifests, evidencias, logs, assets, dados temporarios e experimentos.
- Dados brutos, conversoes intermediarias e rascunhos devem ficar em `rascunho/` e nas subpastas declaradas em `doc/project_hygiene_manifest.json`; arquivos temporarios soltos na raiz do projeto ou do workspace sao proibidos.
- Material ativo usa `naming_policy=portable_descriptive_v1`: ASCII, sem espacos, nomes descritivos em minusculas, `snake_case`/`kebab-case`; excecoes convencionais como `README.md` e `Makefile` sao permitidas. Copias brutas em `rascunho/` preservam o nome original.
- Dependencias compartilhadas canonicas permanecem centrais e nao sao copiadas por projeto: `tools/sgdk_wrapper/`, `sdk/sgdk-2.11/` e `tools/emuladores/`. Alteracoes nelas so sao permitidas quando a tarefa for explicitamente canonica/reutilizavel.
- O toolchain de build deve resolver primeiro e validar `sdk/sgdk-2.11/` do workspace ativo. Variavel `GDK` herdada de outro workspace nao pode dirigir build ou closeout.
- Material externo consultado precisa ser copiado para dentro do projeto, registrado em `doc/project_hygiene_manifest.json` e verificado por hash quando usado como entrada ou evidencia. Copias de diretorios devem possuir inventario verificavel arquivo a arquivo. Caminho externo nunca fecha gate, mesmo com autorizacao humana.
- Nenhum agente deve criar arquivos soltos na raiz do workspace ou misturar evidencia de projetos diferentes. Codigo, scripts, manifestos e documentacao ativa nao podem manter caminhos absolutos para outro workspace/projeto; referencias operacionais devem apontar para a copia local ou dependencia compartilhada canonica.
- `validate_project_hygiene.ps1` bloqueia artefato orfao, rascunho desorganizado, entrada externa sem copia local e referencia absoluta externa em material ativo. Logs historicos preservados em `out/` nao contam como dependencia ativa.
- Projetos que usam tecnicas hardware-level, efeitos visuais, audio senior, streaming, raster, multiplexing, parallax, composicao customizada, gerenciamento de VRAM ou semelhantes devem declarar `doc/technique_usage_manifest.json`.
- O manifesto de tecnicas deve referenciar `doc/05_technical/93_16bit_hardware_mastery_registry.json`, usar `registry_id`, `technique_tags`, `human_proficiency_status`, `owner_skills`, evidencias e `documentation_sync`.
- Cada tecnica aplicada deve referenciar concretamente `doc/13-spec-cenas.md`, `doc/10-memory-bank.md` e `doc/changelog/changelog.md`; booleano de sincronizacao sem docs locais verificaveis nao fecha gate.
- Tags humanas oficiais devem vir do registry: exemplos incluem `MULTIPLEXING`, `DMA_STREAMING`, `RASTER_EFFECTS`, `MID_FRAME_PALETTE_SWAPPING`, `VRAM_TILE_INDEX_MANAGEMENT`, `DELAYED_UPDATE`, `METASPRITE_OPTIMIZATION`, `CUSTOM_SPRITE_COMPOSITION`, `DMA_OPTIMIZADO`, `PALETTE_MANAGEMENT_AVANCADO` e `PARALLAX`.
- O painel humano vivo de capacidades do agente e `doc/05_technical/93_16bit_hardware_mastery_matrix.md`; o registry machine-readable permanece `doc/05_technical/93_16bit_hardware_mastery_registry.json`.
- Status humanos permitidos: `LABORATORIO`, `TEORICA_STANDARD`, `TEORICA_PRIORITARIA`, `MESTRE_STANDARD`, `MESTRE_PRIORITARIA`.
- `LABORATORIO` e transitório e so pode aparecer em labs/techdemos com `lab_not_delivery=true`; nao fecha `ready_for_aaa`, `delivery`, `stable` ou produto principal.
- `MESTRE_*` exige `promotion_evidence` completo: projeto aprovado, ROM hash, evidencia BlastEm, budget/report, docs sincronizados e aprovacao humana registrada.
- `TEORICA_*` informa conhecimento curado, mas nao autoriza o agente a tratar a tecnica como provada em jogo sem evidencia propria.
- `*_PRIORITARIA` exige decisao humana/canonica explicita de prioridade metodologica para barra AAA.
- Bloqueios canonicos: `technique_usage_manifest_invalid`, `technique_registry_id_unknown`, `technique_tag_unknown`, `technique_status_mismatch`, `laboratorio_technique_in_delivery_scope`, `technique_evidence_outside_project`, `technique_documentation_sync_missing`, `master_technique_evidence_missing`.

### 1.0.3 Adocao metodologica obrigatoria

- Todo projeto novo ou antigo deve possuir `doc/project_context_manifest.json` e passar por `tools/sgdk_wrapper/.agent/workflows/project-context-classification.md` antes de arte, runtime, build de entrega ou parecer final.
- `context_type` permitido: `aaa_game`, `technical_demo`, `exercise`, `game_review`, `consulting`. `unclassified` bloqueia abertura operacional.
- O contexto define quais documentos sao bloqueantes: jogo AAA exige pacote completo proporcional; demo tecnica exige evidencia tecnica; exercicio exige objetivo/learning; review e consultoria exigem escopo de parecer, nao ROM.
- O teto de promessa (`delivery_claim_ceiling`) nao pode exceder o contexto. Review/consultoria nao podem declarar `ready_for_aaa`; exercicio nao promove entrega; AAA nao pode fechar sem GDD/TDD/spec/QA/assets/roadmap proporcionais.
- Validador canonico: `tools/sgdk_wrapper/validate_project_context.ps1`, com report em `out/logs/project_context_report.json`.
- Todo projeto novo ou antigo deve possuir `doc/project_methodology_manifest.json`.
- Ao abrir projeto sem esse contrato, execute `tools/sgdk_wrapper/adopt_project_methodology.ps1`; o script cria apenas arquivos ausentes e nunca sobrescreve decisoes locais.
- O contrato deve declarar `project.lifecycle`, `active_workflow=production-loop`, skills obrigatorias, validacoes obrigatorias e claims estruturados.
- `review_required` bloqueia closeout. Cada claim deve virar `required` ou `not_applicable` com justificativa.
- Claims de `critical_motion`, `road_physics` e `modular_boss` nunca podem ser inferidos por palavras soltas como `chase`, `sBossBody` ou `impact_frame`.
- Claim `required` aciona seus owner skills, contrato e evidencias. Arquivo de contrato vazio ou sem simbolos runtime nao satisfaz o gate.
- `critical_motion=required` exige simultaneamente motion GIF, aprovacao humana, screenshot dedicado, SRAM fresca, VDP dump e `perceptual_check` com `fluidez`, `leitura`, `naturalidade` e `impacto` acima de zero.
- Nome placeholder ou divergente entre diretorio, metodologia e `.mddev/project.json` gera `project_naming_invalid`.
- Projeto `new`/`reseed` deve passar por `tools/sgdk_wrapper/validate_project_name.ps1` antes da criacao; projetos antigos nunca sao renomeados automaticamente.
- `freshness_audit` e validacao metodologica base obrigatoria para impedir closeout com docs/evidencias obsoletas.
- `project_hygiene` e `project_context` sao validacoes metodologicas base obrigatorias. Mudanca de implementacao ou arquitetura torna `doc/10-memory-bank.md` e `doc/changelog/changelog.md` obrigatoriamente atualizaveis; deriva gera `project_documentation_sync_stale`.
- Bloqueios canonicos: `project_naming_invalid`, `project_naming_policy_invalid`, `noncanonical_project_entry_name`, `project_methodology_manifest_missing`, `project_methodology_manifest_invalid`, `project_hygiene_manifest_missing`, `project_hygiene_manifest_invalid`, `external_input_inventory_invalid`, `external_path_reference_outside_project`, `project_hygiene_scan_failed`, `project_documentation_sync_stale`, `perceptual_motion_unvalidated`, `road_physics_contract_invalid`, `modular_boss_runtime_invalid`.

### 1.0.4 Ciclo fechado de aprendizado seguro

- Todo projeto novo ou antigo deve receber `doc/agent_learning/` por `adopt_project_methodology.ps1`, sem sobrescrever registros existentes.
- Na abertura, execute `audit_project_learning.ps1 -Mode Audit`; esse modo e estritamente read-only e deve carregar primeiro apenas o `candidate_index`.
- No fechamento de trabalho relevante, depois de registrar observacoes reais e gerar evidencias, execute `audit_project_learning.ps1 -Mode Capture`.
- `Capture` pode atualizar somente `doc/agent_learning/learning_ledger.json` e `out/logs/project_learning_report.json` dentro do projeto.
- O agente deve procurar owner canonico existente antes de propor skill nova. Falha isolada ou solucao ainda nao comprovada permanece local ou exige revisao humana.
- Toda proposta canonica nasce `not_applied`, com aprovacao humana `pending` e `canonical_promotion_performed=false`.
- Evidencia externa, stale ou apenas narrativa nao sustenta promocao. Nenhum status `MESTRE_*` pode nascer do ciclo automatico.
- Alterar `.agent`, rules, workflows, skills, schemas, validators, `lib_case` ou registries exige aprovacao humana explicita, patch controlado e regressao.

### 1.0.5 Graphify e Obsidian (consultivo)

- No primeiro uso da sessao, execute `powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/assert_agent_environment.ps1`; ele prepara o ambiente automaticamente.
- Use Graphify apenas para localizar contexto e relacionamentos; valide sempre abrindo os arquivos canonicos citados.
- Use Graphify apenas por `pwsh` e pelo wrapper `tools/sgdk_wrapper/graphify_forge.ps1`; nunca use `graphify query` direto.
- Se `graph_status=stale`, rode update antes de usar resultados do grafo em decisao ou patch; grafo stale nunca e autoridade.
- Obsidian e cockpit humano opcional; nao entra no build, nao fecha gate e nao substitui docs/validators/evidencia.
- Superficies `.cursor`, `.serena`, `.superpowers`, `.trae`, `.agents` e `.claude` devem apontar para o mesmo workflow `tools/sgdk_wrapper/.agent/workflows/agent-startup-environment.md`.
- Referencia: `doc/GRAPHIFY_OBSIDIAN_POLICY.md`.

### 1.0.6 ai-memory (consultivo controlado)

- `ai-memory` pode ser usado apenas como memoria auxiliar de handoff, busca e recall operacional.
- O preparo automatico chama `tools/sgdk_wrapper/prepare_ai_memory_integration.ps1`, que pode criar `.ai-memory.toml`, `doc/AI_MEMORY_POLICY.md` e `out/logs/ai_memory_integration_report.json`.
- O wrapper nunca executa automaticamente `install-hooks --apply`, `install-mcp --apply`, `bootstrap`, `auto-improve` ou aprovacao de pending writes.
- Qualquer auto-improvement do ai-memory deve permanecer pendente de revisao humana; use `[auto_improve] require_approval = true` e mantenha scheduler desabilitado durante piloto.
- Pagina recuperada do ai-memory nao e fonte de verdade: abra os arquivos canonicos citados antes de decidir, editar ou promover status.
- `ai-memory` nao fecha build, budget, `testado_em_emulador`, `MESTRE_*`, `stable`, `release`, `ready_for_aaa` nem closeout.
- Projeto adotado por `adopt_project_methodology.ps1` deve receber marcador `.ai-memory.toml` local quando possivel, para evitar mistura de memoria entre projetos.

## 1.1 Prioridade arquitetural para cenas AAA compostas

- Quando a cena tiver composicao em camadas, foreground/oclusao, staging visual e forte relacao entre sprite e cenario, trate `tilemap streaming guiado pela camera` como baseline arquitetural prioritario.
- Essa prioridade e uma presuncao forte de metodo, nao uma obrigacao cega de replicacao.
- Antes de implementar ou depurar localmente uma cena desse perfil, registre uma triagem arquitetural minima contendo:
- `scene_profile`: `aaa_layered`, `single_plane`, `hud_heavy`, `boss_arena`, `cutscene`, `fx_driven` ou equivalente honesto
- `baseline_technique_applicability`: `sim`, `parcial` ou `nao`
- `baseline_contract`: divisao base/foreground, papel de cada plano, staging visual, organizacao de tilemaps, forma de oclusao e relacao sprite/cenario
- `baseline_decision`: `adotar`, `adaptar` ou `divergir`
- `divergence_reason`: obrigatorio quando a decisao for `divergir`
- A `BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BRIGA DE RUA]` entra apenas como referencia interna opcional de implementacao dessa familia tecnica.
- Se a cena divergir de `tilemap streaming guiado pela camera`, a justificativa deve citar constraints reais da cena, como budget, `WINDOW`, streaming, layout, telemetria, linguagem visual ou contrato de gameplay.
- Nao iniciar depuracao residual de VRAM, paleta, `rescomp`, upload de sprite ou workaround de plano antes de fechar essa triagem quando o perfil da cena for `aaa_layered`.
- A pergunta obrigatoria deixa de ser "como faco esta cena do zero?" e passa a ser "o que de `tilemap streaming guiado pela camera` se aplica aqui, o que nao se aplica e por que?".

### 1.1.1 Direcao de cenario monumental

- Cena, bioma, fase, boss arena, setpiece, abertura ou showcase visual que prometa profundidade, clima vivo, pseudo-3D, agua, calor, nevoa, destruicao, background em evento ou "cenario monumental" exige `scene_direction_record` antes da traducao para VDP.
- `scene_direction_record` deve consultar `tools/sgdk_wrapper/.agent/references/scene_archetype_catalog.json` e classificar a cena como `minimal`, `competent`, `monumental` ou `signature_only`.
- `monumental` exige pelo menos uma tecnica assinada com funcao narrativa ou de gameplay: escala, risco, maravilhamento, velocidade, isolamento, ameaca, transicao ou leitura de rota.
- `signature_only` exige fallback, budget e, quando quebrar a rota segura, `experimental_override_required=true`.
- Referencia a Mode 7, F-Zero, Super Mario Kart ou Zeal no Mega Drive deve ser redirecionada para tecnica real (`pseudo3d_road_stack`, `line_scroll_floor`, `zmap_road`, `palette_depth_bands` ou paineis pre-renderizados). Declarar Mode 7 em Mega Drive emite `mode7_claim_on_megadrive`.
- `scene_direction_undeclared`, `archetype_catalog_not_consulted`, `monumental_promised_without_budget`, `decorative_only_blocked`, `mode7_claim_on_megadrive`, `raster_fx_owner_collision` e `palette_cycle_ownership_conflict` bloqueiam AAA/stable/release/delivery.

## 2. Restricoes nao negociaveis

- Nao usar `float` ou `double` para gameplay SGDK.
- Nao usar `malloc` ou `free` no loop de jogo.
- Nao inventar APIs do SGDK.
- Nao duplicar logica de build em scripts de projeto.
- Nao alterar budgets sem evidencia e autorizacao quando o projeto exigir.
- Nao sobrescrever `.agent` local se ela ja existir.

### 2.1 Execucao automatica da proibicao de heap

- A validacao central varre `src/` em busca de `malloc/calloc/realloc/free`.
- Para bloquear merges com uso de heap, ativar `SGDK_ENFORCE_NO_HEAP=1` no ambiente de validacao.
- Mesmo em modo permissivo (sem a variavel), ocorrencias sao reportadas como `WARNING` e devem ser justificadas.

## 3. Governanca e status

- Diferencie sempre `documentado`, `implementado`, `buildado`, `testado_em_emulador`, `validado_budget`, `placeholder`, `parcial` e `futuro_arquitetural`.
- Nao use termos como `validado`, `pronto` ou `completo` sem evidencia verificavel.
- Se encontrar conflito entre docs e codigo, sinalize a divergencia explicitamente.
- Antes de produzir arte/runtime em projeto novo ou escopo reseed, gerar `prd_readiness_report` com `tools/sgdk_wrapper/check_prd_readiness.ps1`; PRD obrigatorio em `seed`, ausente ou sem frontmatter bloqueia AAA/stable/release.

### 3.2 Gate de runtime de producao AAA

- Percentual de cobertura, diagnostico executivo ou "infra forte" nao e gate de entrega. So artefato verificavel fecha status.
- Projeto que pedir `AAA`, `stable`, `release`, `delivery` ou `ready_for_aaa=true` precisa declarar e provar estes contratos:
  - `production_runtime_contract`
  - `scene_manager_contract`: enter/update/exit, loading, fade/transition, cleanup e scene id deterministico
  - `input_abstraction_contract`: 3/6 botoes, buffer, remap, pause/debug, frame-lag tolerance e ownership de leitura
  - `persistence_scope`: `none`, `optional` ou `required`, com `sram_policy` explicito
  - `save_system_contract` quando `persistence_scope=required`, `sram_policy!=none` ou o GDD declarar persistencia: SRAM magic, version, checksum, slots, inicializacao e tratamento de save invalido
  - `region_timing_contract`: `SYS_isPAL()`, alvo 50/60 Hz, timers, audio cadence, animacao e regressao PAL/NTSC
  - `asset_optimization_report`: compressao `.res`, dedup/reuse de tiles, custo ROM, custo VRAM e tradeoffs
  - `rom_mastering_report`: header, region flags, SRAM, checksum, product id, sizealign e hash
  - `code_review_report`: revisao formal de C/SGDK, `.res`, builders, budget, evidencias e APIs 2.11
  - `ci_gate_report` ou `local_ci_gate_report`: preflight, testes CI locais/host, validator e razao se GitHub Actions ainda nao existir; `local_ci_gate_report` segue `tools/sgdk_wrapper/schemas/local_ci_gate_report.schema.json`
- `save_system_contract_missing` so bloqueia quando `persistence_scope=required`, `sram_policy!=none` ou o GDD/feature_scope_map exigir persistencia. Com `persistence_scope=none`, registrar `save_system_contract_not_applicable`.
- Se algum contrato obrigatorio acima for ausente ou `nao_medido`, o status maximo e `prototype_playable` ou `visual_gate_blocked`, nunca AAA/stable/release.
- Scene manager, input, save e region nao precisam nascer como biblioteca global no primeiro slice, mas precisam ter contrato explicito e runtime proof no projeto piloto.
- Compressao `.res` reduz ROM/load; nao reduz VRAM residente. Dedup/reuse so conta quando medido por report, nunca por expectativa.
- `make -j`, debug symbols, hooks e CI/CD sao melhorias de pipeline. Ate existirem como evidencia, declarar `pipeline_gate_partial`, nao "pipeline AAA-grade".

## 3.1 Armadilhas SGDK que devem ser assumidas como suspeitas

- `VDP_drawTextBGFill()` no SGDK 2.11 nao trunca a string com seguranca. Se `strlen(str) > len`, a funcao pode corromper a stack e derrubar o 68000 alguns frames depois.
- Para overlays, HUDs e ferramentas de benchmark, nunca chame `VDP_drawTextBGFill()` com largura menor que o texto real. Use um wrapper local que trunque primeiro e so depois complete com espacos.
- Sintoma classico dessa corrupcao: BlastEm acusa `M68K attempted to execute code at unmapped or I/O address ...` sem apontar o overlay como origem imediata.

## 4. Operacao do wrapper

- Toda logica compartilhada deve morar em `tools/sgdk_wrapper/`.
- Melhorias genericas vao para o wrapper central, nao para wrappers locais do projeto.
- O bootstrap da `.agent` e feito apenas quando ausente.
- Se faltar apenas `framework_manifest.json`, `ensure_project_agent.ps1` pode **heal** copiando esse ficheiro da canonica (sem sobrescrever skills locais).
- Se ainda assim faltar manifesto, ou houver drift de versao/caminhos rastreados, trate como `bootstrap_degradado` ate auditoria explicita.
- O wrapper nao deve fingir saude canonica quando so consegue provar existencia de copia local.

## 5. Handoff

- Ao encerrar uma sessao relevante, atualize o documento de estado operacional do projeto se ele existir.
- Se a implementacao mudou e a documentacao ficou atras, nao silencie essa diferenca.
- Handoff de validacao em emulador exige sincronizar `emulator_session.json`, `validation_report.json` e memoria operacional na mesma narrativa factual.

## 6. Maximalismo Tecnico Obrigatorio

Nao basta adicionar FX isolado. O "Treasure Mindset" exige combinacao. E OBRIGATORIO:
- Combinar FX (ver `doc/05_technical/80_fx_combination_matrix.md`).
- Variar FX no tempo com uso obrigatorio de Timeline de cena e "pico".
- Reagir ao gameplay e otimizar para caber (multiplexing, blinking, streaming).
- Buscar sprites grandes, cenarios exuberantes, cores vivas, musica marcante, animacao rica e jogabilidade fluida sempre que o contexto, a direcao e o budget sustentarem a escolha.
- Registrar no GDD a ambicao tecnica/visual/sonora e no TDD cada tecnica escolhida, sua funcao, owner, budget, evidencia e fallback.
- Rejeitar ou adiar explicitamente tecnicas sem funcao, sem ownership, sem budget ou incompatíveis com a cena. Maximalismo e densidade de intencao, nao empilhamento decorativo.
Se uma cena usa tecnicas isoladas estaticas e sem evolucao temporal, ela e considerada INCOMPLETA.

## 7. Experimental Override (A Excecao AAA)

Embora as regras de VDP e Budget sejam lei, e encorajado recorrer ao `doc/00-governance/11_experimental_override.md`. E permitida UMA quebra premeditada das regras ou limites seguros por cena (geralmente no Signature Moment) para alcancar efeitos tidos como impossiveis no Mega Drive, DESDE QUE justificado e que o motor permaneca firmemente em 60fps constantes sem latencia de input.

## 8. Inteligencia Visual e Travas de Arte (CRITICO)

A credibilidade do espetaculo vem da consistencia visual. Para gerar ou instruir criacao de qualquer asset visual de uma cena, o pipeline DEVE obrigatoriamente cumprir a "Visual Quality Bar" (`doc/03_art/00_visual_quality_bar.md`) ativando 3 travas inviolaveis:
- **Trava 1:** Sem 3 referencias visuais reais explicitas justificando a heranca -> INVALIDO.
- **Trava 2:** Sem Visual Breakdown pre-definido (paleta, material, iluminacao e profundidade) -> INVALIDO.
- **Trava 3:** Sem a aprovacao do `art-director` para validar shading/volume -> INVALIDO.
- **Trava 4:** Sem `art_direction_decision_record` consultando `tools/sgdk_wrapper/.agent/references/art_style_catalog.json` antes de gerar, buscar, converter ou julgar arte -> INVALIDO.
- **Trava 5:** Sem `art_gameplay_direction_gate` para model sheet, background, sprite art, animation strip, sprite sheet final, FX sheet, HUD heroico, title/menu ou asset critico -> INVALIDO.
- **Trava 6:** Sem `authorial_line_contract` para asset critico autoral -> INVALIDO. O contrato deve declarar `line_signature`, `silhouette_hooks`, `face_grammar`, `hand_foot_grammar`, `costume_asymmetry`, `material_marks` e `generic_blockers`.
- Todo feedback corretivo de arte deve passar antes por `doc/03_art/02_visual_feedback_bank.md` e pela skill `visual-excellence-standards`.
- Drift de estilo no meio do projeto exige `style_drift_correction_brief` antes de regerar arte.
- `art_direction_undeclared`, `style_catalog_not_consulted`, `style_drift_uncorrected`, `authorial_line_contract_missing`, `generic_prompt_style_blocker`, `art_director_supervision_missing`, `game_design_context_missing`, `cohesion_drift` ou `director_gate_unapproved` bloqueiam `ready_for_aaa=true`, `AAA`, `stable`, `release` e `delivery`.
- Referencias esteticas sao ancoras tecnicas. Nunca transforme nome de artista, estudio, marca, jogo ou IP em prompt de copia; use descritores tecnicos neutros e `authoriality_gate_report`.

### 8.2 Gate visual fonte-ROM

- `local_author_pixel_rasterization`, `procedural_renderer` e scripts locais `draw_*` so podem ser `debug_lab`, `visual_lab_control` ou `placeholder`; nunca fonte final de personagem, cenario, boss, HUD heroico ou asset AAA.
- Todo simbolo visual de `res/*.res` (`IMAGE`, `SPRITE`, `TILESET`, `TILEMAP`, `MAP`, `BITMAP`) exige registro em `doc/asset_provenance_manifest.json` com `source_kind`, `acceptance_status` e `generated_by`. Simbolo sem registro e `asset_provenance_undeclared` e bloqueia entrega visual.
- `source_kind: procedural_primitive` nunca pode ter `acceptance_status: final`. `procedural_composed_from_authored` exige `authored_source` persistida em `data/source_art/` com hash: codigo pode montar, recortar e paletizar arte autoral, nunca desenha-la.
- PNG em disco nao prova autoria. O auditor casa cada arquivo do `.res` com os builders que o escrevem; declarar `hand_authored_pixel`, `ai_generated` ou `photo_or_render_derived` para arquivo produzido por builder de primitivas vira `procedural_asset_promoted_to_res`.
- Pixels de tile escritos como literal `const u32` em C e enviados para VRAM fora de escopo de debug/telemetria viram `runtime_authored_tile_pixels_outside_debug`. Endereçamento de VRAM (`TILE_USER_INDEX`) e composicao de mapa (`VDP_setTileMapXY`, `VDP_fillTileMapRect`) com asset importado permanecem uso legitimo.
- Grafico procedural e permitido apenas para telemetria, debug visual de elemento invisivel ao jogador e elemento transitorio de interface (barra de progresso simples). Nunca para personagem, inimigo, boss ou cenario.
- `context_type: technical_demo` com intencao visual cumpre o mesmo gate de asset externo de `aaa_game`. A unica excecao e `validator_fixture: true` em `doc/project_context_manifest.json`, que em troca prende `delivery_claim_ceiling` em `none`, `concept`, `lab` ou `exercise` e nunca sustenta claim de entrega visual.
- Enforcement: `tools/sgdk_wrapper/audit_procedural_asset_provenance.py`; contratos em `tools/sgdk_wrapper/schemas/asset_provenance_manifest.schema.json` e `asset_provenance_audit_report.schema.json`.
- Cada projeto carrega a diretriz e seu estado medido em `doc/00-diretrizes-agente.md`, entre os marcadores `diretriz-bloqueio-estetico v1`. Agente que assume continuidade le esse bloco antes de tocar em arte; projeto novo herda o bloco do template `tools/sgdk_wrapper/modelo/`. Injecao e refresh idempotentes via `tools/sgdk_wrapper/apply_aesthetic_directive.py`, que falha com `--check` quando um projeto esta sem diretriz ou com medicao velha.
- Arte premium so existe para o pipeline se estiver persistida em `data/source_art/` com `premium_source_manifest` e hash/timestamp. Imagem inline nao persistida e `generated_inline_pending_persistence`.
- Benchmark tecnico nunca pode virar `source_art`; ele so orienta escala, densidade, timing, presenca, budget e qualidade. Thresholds e metodo de similaridade pertencem ao `benchmark_profile` e ao `authoriality_gate_report`, nao a uma regra global fixa.
- `source_validity` passa antes de `source_to_rom_visual_match`. Fonte clone, benchmark-derived, sem autoria ou derivada sem autorizacao/licenca bloqueia a promocao mesmo que a imagem reduzida pareca parecida.
- Asset critico precisa declarar `license`, `authorial_source`, `derivative_of`, `derivative_license_status`, `clone_risk_score`, `clone_risk_method` e `benchmark_used_as`.
- Personagem principal autoral exige `authorial_model_sheet`; cenario autoral exige `authorial_stage_concept`; todo asset critico exige `clone_risk_score` medido por metodo declarado.
- Asset critico com `needs_review`, `rework`, `placeholder`, `debug_lab`, `benchmark-derived` ou `perceptual_quality=nao_medido` bloqueia `pronto`, `AAA`, `delivery` e `ready_for_aaa=true`.
- Todo asset critico em `res/` precisa de `elite_ready=true` e `source_to_rom_asset_map` com `source_to_rom_visual_match >= 8`.
- Se for laboratorio, declarar `lab_not_delivery=true`; isso nao autoriza status de entrega.
- Sprite heroico com gi branco ou tecido claro exige `white_material_palette_contract` com sombras frias azul/roxo, highlights limpos/quentes, distancia tonal minima e funcao por slot.
- `PALETTE_WASTE` em asset critico bloqueia visual delivery; quantizacao automatica nao substitui palette pass manual.
- `budget_pass` e `visual_pass` sao eixos separados. Quando o runtime cabe com folga, budget nao pode justificar empobrecimento visual.
- HUD de entrega nao pode parecer debug: precisa registrar `ui_attention_profile`, densidade alvo, hierarquia, area ocupada, contraste e interferencia no gameplay.
- Benchmark de genero usa `benchmark_profile.required_match`; HAMOOPIG e apenas um perfil possivel, nunca regra global.
- Build limpo e BlastEm observado nao reduzem o gate visual; se `validation_report.blocking_statuses` nao estiver vazio, closeout nao pode ser `ok`.
- Entrega visual AAA exige `measurement_level` formal: `measured`, `emulator_verified` ou `vdp_dump_verified`. `declared` e `estimated` servem para planejamento, nao para aprovacao.
- `leaf_blocker_propagation=true` e obrigatorio em `visual_delivery_gate_report`: qualquer `needs_review`, ilha, stale, `index0_high_risk`, dump VDP ausente ou evidencia `measured=false` em asset critico força `ready_for_aaa=false`.
- Para entrega AAA, `visual_vdp_dump.bin` e obrigatorio. Se screenshot sugerir faixa indevida, garbage, plano descoberto, conflito de paleta ou colisao VRAM, ausencia do dump vira blocker formal mesmo em prototipo.
- `visual_vdp_dump.bin` nao pode ser copia, alias ou hash igual ao `save.sram`; dump invalido equivale a `invalid_visual_vdp_dump`.
- Regressao de cena so valida visualmente quando compara contra baseline persistido. Captura sem baseline e evidencia de execucao, nao evidencia de qualidade visual.
- Screenshot com informacao visual baixa (`<=3` cores unicas ou cena quase vazia) e `blank_or_low_information_capture`; nao fecha gate, mesmo com emulador aberto.
- Projeto com intencao de entrega visual/gameplay e sem `res/resources.res` ou `.res` equivalente fica `resources_res_missing_for_visual_delivery` e `asset_pipeline_not_started`.
- Runtime que carrega/desenha tiles diretamente em C (`VDP_loadTileData`, `TILE_USER_INDEX`, arrays de tiles ou nametable manual) deve ser marcado como `code_loaded_tiles_unmeasured` ate ter budget especifico, screenshot util e/ou dump VDP. Ausencia de `.res` nao e validacao de budget.
- Cena alvo precisa casar com a evidencia: `TargetScene`, bootstrap SRAM/MDRT e `runtime_metrics.scene_id` divergentes geram `runtime_target_scene_mismatch`.
- `workspace_scope_isolation=true` deve declarar que sujeira global do workspace nao foi usada para promover, reprovar ou misturar evidencia de projeto. Mudancas fora do projeto precisam ficar fora do parecer de entrega.
- ROM visual de entrega nao pode ser painel de texto/procedural: uso dominante de `VDP_drawText`, ASCII art, nomes de efeito, barras de debug, `safe rhythm lane`, `efeito empurra`, `fallback procedural`, `lab_bg_b` unico ou template repetido bloqueia `AAA`, `delivery` e `ready_for_aaa=true`.
- Fallback so e valido quando preserva a intencao perceptiva e mecanica especifica do efeito. Fallback generico reutilizado em massa vira `mass_generic_procedural_fallback` e reprova a campanha inteira.
- Campanhas de tecnicas/eixos precisam rodar `tools/sgdk_wrapper/audit_effect_campaign_semantics.ps1` antes do closeout consolidado. Auditoria estrutural, screenshot e `validation_report` limpo nao substituem esse gate semantico.
- `ready_for_aaa=true` exige `blocking_statuses` vazio. Status bloqueante como warning ainda rebaixa a entrega; warning de closeout nao pode virar selo AAA.
- `ready_for_aaa` nunca pode ser derivado so de build, BlastEm, budget, screenshots ou reports tecnicos. O validador separa `technical_ready` de `creative_ready`; `technical_artifact_status` substitui o significado antigo de `aggregate_status`, que fica apenas como alias deprecated e nao e sinal de AAA.
- `ready_for_aaa=true` exige simultaneamente `technical_ready=true`, `creative_ready=true`, `summary.errors=0`, `blocking_statuses=[]`, `creative_blocking_statuses=[]` e `semantic_audit_status!=failed`.
- Se existir `semantic_audit_report.json` ou `.md` com status `failed`, registrar `semantic_audit_failed`; esse blocker impede AAA mesmo com ROM buildada, BlastEm ok e demais reports tecnicos limpos.
- GDD substancial e gate criativo. `doc/11-gdd.md` precisa cobrir fantasia, core loop, kit do jogador, regras sistemicas, progressao da fase, mapa/secoes, inimigos, riscos, ritmo, tutorial invisivel, climax e criterios de qualidade visual. Briefing minimo fica `gdd_substantial_insufficient`.
- Fallback procedural/debug/lab, `local_author_pixel_rasterization` ou `procedural_renderer` usados como asset final limitam `max_delivery_status` a `technical_lab_validated` e bloqueiam `creative_ready`.
- Julgamento visual real bloqueia `visual_direction_failed` quando screenshot, contact sheet ou report indicar padrao repetitivo, painel textual, personagem generico, chuva estatica, mosaico debug ou asset procedural pobre.
- Todo efeito precisa provar consequencia jogavel: rota muda, risco muda, timing muda, inimigo reage, camera comunica ou o jogador toma decisao diferente. Sem evidencia vira `gameplay_consequence_missing`.
- Cena de marca sem gameplay (branding, title card, selo de autor) nao tem rota, risco nem decisao do jogador para a arte alterar. Nesse escopo — e somente nesse — o eixo de consequencia jogavel e substituido por `brand_comprehension_consequence`: cada decisao de arte precisa mudar o que o espectador entende sobre quem fez o jogo. Aprovado por curadoria humana em 2026-08-17. Cena jogavel continua obrigada ao eixo canonico; nunca use essa substituicao para escapar dele.
- A substituicao so vale porque pode reprovar: toda tecnica declarada carrega `brand_comprehension_claim` com `brand_comprehension_negative_test` e `brand_comprehension_strength`, ou e classificada `enabling_discipline` (previne artefato, nao ensina nada ao espectador, isenta mas obrigatoria). Tecnica sem classificacao e espetaculo sem consequencia. Blockers: `brand_comprehension_missing`, `brand_comprehension_not_falsifiable`, `brand_comprehension_strength_undeclared`, `brand_comprehension_unjustified_technique`. Claim `weak` nao reprova, mas fica marcado e nao pode ser apresentado como forte no closeout.
- Enforcement: `tools/sgdk_wrapper/validate_brand_comprehension_gate.py`. O validador prova que nenhuma tecnica passou sem justificativa; ele nao julga se o claim e verdadeiro, o que continua sendo decisao humana no gate visual contra screenshot e `visual_vdp_dump` reais.
- Decision log precisa ser granular por eixo e decisao critica, com decisao, justificativa e evidencia; poucas linhas globais viram `decision_log_too_shallow`.
- Cada eixo precisa de evidencia especifica: audio-sync exige timeline/cue report, particulas exigem movimento temporal observavel, level design exige rota jogavel, visual exige medicao real e animacao exige contratos/artefatos de movimento.

### 8.2.1 Animacao premium e performance de movimento

- Personagem heroico, lutador, boss, golpe, dano, smear, hitstop ou alegacao premium/AAA exige `animation_direction_contract` alem de `motion_phase_map`.
- Personagem premium exige idle convincente, antecipacao, recuperacao, contato de pe, impacto e leitura de silhueta. Ausencia desses artefatos vira `animation_gate_failed`.
- Golpe premium precisa declarar startup/anticipation, active, hitstop frame, follow-through e recovery; ataque que comeca direto no active frame, volta instantaneamente ao idle ou nao informa hitstop fica `needs_review`.
- Smear frame deve ser intencional e declarado; se parecer blur, sujeira, ilha, halo ou fragmento de celula, ele bloqueia `elite_ready`.
- Dano precisa declarar direcao da forca, quebra de postura e escala; hurt/knockdown sem `hit_reaction_contract` nao e animacao AAA.
- Shading deve acompanhar volume em movimento. Luz estatica colada em corpo girando bloqueia premium mesmo quando o strip compila.
- Flash frame e FX de impacto dependem de `palette_flash_policy` e sprite/FX separado quando tiverem papel de gameplay; FX baked-in em sheet de personagem bloqueia entrega.
- Chefe/chefao ou criatura colossal deve usar `modular_boss_rig_contract` quando full-body sheet exceder budget seguro; partes, pivots e dominios de paleta precisam ser auditaveis.
- Personagem heroico, lutador ou boss em AAA exige `idle_breathing_cycle_contract` e `facial_expression_phase_map`, salvo `applicability=not_applicable` com justificativa anatomica ou de escala.
- Personagem com tecido, faixa, cabelo longo, capa, jaqueta ou item secundario visivel em dash, queda, ataque, idle ou cutscene exige `cloth_secondary_animation_contract`; na primeira iteracao de baseline pode ser warning, mas entrega AAA final nao ignora motion secundario quando ele define carisma ou leitura.
- Lutador, heroi com arma ou personagem expressivo exige `hand_pose_keyframe_contract` quando maos, garras, dedos, empunhadura ou gestos forem legiveis em 320x224; `not_applicable` precisa declarar motivo.
- Os contratos `cloth_secondary_animation_contract`, `facial_expression_phase_map`, `idle_breathing_cycle_contract` e `hand_pose_keyframe_contract` devem declarar `applicability`, `frame_budget_impact_estimate`, artefatos esperados e relacao com o budget VDP antes de virar promessa de animacao.

## 8.3 MENUS E TITLE SCREENS NAO PODEM SER GENERICOS

Menu e title screen sao superficies de showcase, nao telas utilitarias neutras.

Regra:
- devem refletir a fantasia, o genero e a temperatura do projeto
- devem permanecer legiveis em 320x224 nativo
- devem ter vida perceptivel em idle
- devem fornecer feedback ativo de selecao
- nao podem depender de fundo estatico morto com texto cru por cima

Default esperado:
- profundidade visual por planos, parallax ou equivalente tematico
- tipografia com separacao dura do fundo
- cursor ou item selecionado com animacao observavel
- paleta de alto contraste com hierarquia clara

Proibido por default:
- menu `placeholder funcional` entregue como front-end final
- sci-fi neon generico em projeto cuja fantasia pede outra linguagem
- texto critico desenhado em plano rolavel quando houver risco de conflito visual

## 9. EFEITO COLATERAL DE FX (OBRIGATORIO)

Nenhum FX age isoladamente. Todo FX principal deve gerar pelo menos 1 efeito secundario fisicamente real no ambiente:
- Chuva deve gerar reflexo no chao.
- Fogo deve espalhar fumaça ou glow na paleta adjacente.
- Impacto tem que gerar camera shake, poeira ou alteracao de estado temporal.
- FX de cenario declarado em `scene_signature_techniques` precisa de `parallax_layer_contract`, `palette_cycle_decision_card`, `raster_fx_ownership_map` ou `background_ecology_card` quando aplicavel.
- Palette cycling, line scroll, H-Int, heat haze, water wobble, pseudo-3D, foreground destrutivo e background vivo precisam declarar owner, custo de pior quadro, teardown e fallback antes do runtime.

## 10. GAMEPLAY VISUAL LINK

Nenhum efeito pode existir sem ligacao direta com o gameplay ou o pulso narrativo. O `Scene Architect` DEVE se fazer a seguinte pergunta obrigatoria:
"Como esse efeito ajuda o jogador a sentir a mecanica de jogo?"
Se nao ajuda ou e puramente "de enfeite" sem interagir, nao gaste VRAM. Repense o fluxo.

### 10.1 Cenario como gameplay/narrativa

- Cenario monumental sem `scene_narrative_function` e `gameplay_visual_link` vira `decorative_only_blocked`.
- Parallax, nevoa, godrays, agua, lava, cidade, nave de fundo ou ecologia viva precisam comunicar rota, risco, velocidade, escala, estado dramatico ou leitura mecanica.
- Quando o cenario e apenas atmosfera competente, declare `selected_profile=competent`; nao prometa `monumental` sem tecnica assinada e budget.

## 11. SISTEMA DISCRETO DE CUTSCENES ("FAKE CINEMA")

A partir deste trancamento, **"Cutscene nao e Gameplay"**. Se uma animacao narrativa for requisitada, o Pipeline DEVE operar sob as regras de *Economia Inteligente* e `Fake Cinema`. E obrigatório que o projeto:
- Importe o estrito arsenal narrativo ditado pelo documento `/doc/05_technical/90_cutscene_system.md` (Usando Pans, Holds e Som).
- Cumpra intencionalmente 3 regras cinematicas do `doc/01_game_design/30_cinematic_language.md`.
- Entregue a cena obedecendo religiosamente ao "Template de Cutscene", formalizando a prioridade *Imagem Bem Feita + Truques Visuais > Animacao Complexa*. A pergunta base passa a ser: *"Como conto isso com o minímo de movimento e maximo de impacto?"*

### 11.1 Contrato canonico de cutscene

- Cutscene, abertura, cena de contexto, final, briefing, comunicador de piloto, retrato falante ou painel narrativo exige a skill `cutscene-cinematic-direction`.
- Cutscene nao e video continuo. Cada shot vira estado de FSM com `enter`, `update`, `advance` e `exit/teardown`.
- Antes de arte ou runtime, devem existir: `cutscene_scene_contract`, `cutscene_fsm_script`, `cutscene_storyboard_board`, `cutscene_panel_layout`, `cutscene_resource_plan`, `cutscene_palette_script`, `cutscene_text_timing_map`, `cutscene_audio_cue_map`, `cutscene_teardown_plan` e `cutscene_evidence_plan`.
- Cada estado declara assets carregados, surfaces (`BG_B`, `BG_A`, `WINDOW`, sprites), dominios de paleta, texto, trigger de avanco, duracao, FX, audio e reset.
- Painel/manga layout e o default seguro. Full-screen bitmap e permitido somente com `fullscreen_bitmap_justification`, contagem de tiles/paletas e fallback de pan/crop/painel.
- Storyboard ou board de cutscene deve passar por `translation_target=cutscene_board` e consultar `tools/sgdk_wrapper/.agent/lib_case/art-translation/case_cutscene_board`.
- Referencias como Phantasy Star IV, Valis III, Rondo of Blood, Tales of Phantasia, Snatcher e Princess Minerva orientam linguagem visual, staging e ritmo. Elas nao importam automaticamente recursos de PC Engine CD, SNES ou Sega CD para SGDK.
- Anime 90s em pixel art exige clusters limpos, olhos/rosto expressivos, linework duro, hue-shift em pele/cabelo/tecido, dithering funcional e leitura nativa em 320x224. Arte suave, borrada ou com gradiente de IA nao passa.
- Texto dramatico exige `glyph_manifest`, cadence por pontuacao, owner de `WINDOW` ou regiao de `BG_A`, controle de avanco e limite de linhas.
- H-Int, palette cycling, palette split, Shadow/Highlight e raster effects em cutscene exigem owner unico, budget por estado e teardown simetrico.
- Budget de cutscene e por estado. Nao assumir que todos os paineis, retratos e fontes ficam residentes ao mesmo tempo, nem herdar VRAM por acidente.
- Entrega AAA de cutscene exige screenshot dedicado da cena, `runtime_metrics.scene_id` correto, baseline comparativo, freshness limpo e `visual_vdp_dump.bin` quando AAA ou quando houver suspeita visual.

## 12. O SGDK MASTER BUILD & VISUAL VALIDATION LOOP

O executor/agente perde o direito de declarar sucesso baseado unicamente na "teoria ou codigo C limpo". Todos os processos agora respondem primeiramente ao documento `/doc/00-governance/12_master_build_validation_loop.md`.
**A Regra Final de Ferro:** Intencao nao e validacao. Funcao na tela sim. Se o pipeline falhar em compilar a ROM final, ou se a ROM rodando no emulador nao comprovar perfeitamente os 60FPS coerentes com a integracao das rules visuais AAA e os FX interagindo, a tarefa nao ta concluida.
A operacao entra em "Bloqueio de Progresso" e deve registrar o defeito imediatamente no artefato canonico de memoria operacional do contexto atual: `doc/10-memory-bank.md` para projetos SGDK e `doc/06_AI_MEMORY_BANK.md` para governanca do workspace. Nenhum agente deve exigir ou inventar `AI_MEMORY.md` fora desse fluxo canonico. A iteracao segue em `Cycle-rebuild` ate o sucesso real e empirico. "Se não foi visto rodando, não existe."

## 13. METRICAS DE RUNTIME E QUALIDADE PERCEPTIVA (OBRIGATORIO PARA AAA)

Para qualquer cena que queira alegar nivel AAA, nao basta "rodar". E obrigatorio declarar, quando houver instrumentacao ou checklist de QA:
- `frame_stability`: estabilidade de frame/jitter
- `sprite_pressure`: pressao de sprite/scanline
- `fx_load`: carga simultanea de FX
- `perceptual_quality`: julgamento perceptivo objetivo da cena

Se esses campos estiverem `nao_medido`, a cena pode estar funcional, mas nao deve ser vendida como validacao AAA completa.

Quando o wrapper central rodar com `SGDK_RUNTIME_CAPTURE=1`, o artefato `out/logs/runtime_metrics.json` passa a ser evidencia obrigatoria do estado observado em emulador e deve ser refletido em `out/logs/validation_report.json`, que se torna a fonte primaria do status panel junto com as metricas de runtime.

## 14. CRITERIO UNICO DE QA E EVIDENCIA EM EMULADOR

- **BlastEm** e o emulador de referencia obrigatorio para `boot_emulador` e gate de entrega.
- **BizHawk** com Genesis Plus GX e aceito como evidencia complementar para telemetria, frame advance e captura de `runtime_metrics.json`, mas nao substitui o gate obrigatorio em BlastEm.
- **Exodus** e aceito apenas para diagnostico de edge cases.
- **Gens KMod** e aceito somente para analise exploratoria de VRAM/registradores, nunca como evidencia de aprovacao.
- `testado_em_emulador` so pode ser promovido a verdadeiro quando houver evidencia rastreavel em `validation_report.json` e/ou artefato de sessao de emulador, sempre respeitando BlastEm como referencia de entrega.

### 14.1 Vinculo obrigatorio com a ROM validada

- Toda evidencia de emulador deve estar ligada a uma ROM identificavel por caminho e, quando possivel, hash, tamanho e timestamp.
- Abrir o emulador sem provar qual ROM estava em execucao nao fecha gate.
- Se a ROM for rebuildada depois da captura, a evidencia anterior vira obsoleta e os eixos de QA devem ser rebaixados ate nova validacao.

### 14.2 Ciclo de vida da sessao de emulador

- `emulator_session.json` nao pode parar em `launch_status=started` quando a sessao de QA foi usada como evidencia.
- O ciclo esperado e `started -> captured -> closed`, ou equivalente mais detalhado definido pelo wrapper.
- `boot_emulador` nao deve ser marcado como `ok` sem uma sessao ao menos capturada.
- `gameplay_basico` nao deve ser marcado como funcional se a sessao nao provar entrada, leitura de estado ou resposta visual coerente.
- scripts de automacao BlastEm devem consumir `tools/sgdk_wrapper/lib/blastem_automation.psm1`; duplicacao local de foco/input/close e regressao.
- quando a ROM expuser heartbeat `READY`, a navegacao deve preferir `press_until_ready:*` com leitura em SRAM `0x100`.
- no Windows, o sandbox do BlastEm deve refletir a topologia `HOME/AppData/Local/blastem`; escrever apenas em um `LocalAppData` paralelo nao e suficiente.

### 14.3 Captura dedicada e nao ambigua

- Screenshot para gate deve ser captura dedicada da janela do BlastEm ou screenshot interno do proprio emulador.
- Captura global da area de trabalho, IDE ou monitor errado nao conta como evidencia valida.
- Quando houver mais de uma janela candidata, o processo de QA deve verificar titulo da janela, PID ou outro identificador confiavel antes de salvar a evidencia.
- O framework deve preservar os arquivos de captura usados no gate em `source_artifacts` do `validation_report.json`.
- logs operacionais do BlastEm devem existir em JSONL sob `out/logs/*_blastem.log`.
- `save_path` e `screenshot_path` do BlastEm devem ser inseridos no bloco `ui {}` do cfg sandboxizado; no topo do arquivo a opcao pode ser ignorada pelo emulador.

### 14.3.1 Regra canonica para evidencia de VDP

- Quando o projeto ou laboratorio emitir um bloco de evidencia visual em SRAM auditavel, o gate pode ser fechado com o trio: `benchmark_visual.png` (ou screenshot equivalente da janela do BlastEm) + `save.sram` + `visual_vdp_dump.bin`.
- Nessa configuracao, o quicksave nativo do BlastEm passa a ser **evidencia redundante opcional**, nao requisito bloqueante.
- O `visual_vdp_dump.bin` deve ser derivado de um bloco assinado e limitado ao frame/estado relevante, nunca de inferencia textual ou de memoria inventada pelo agente.
- O wrapper deve rejeitar dump visual com o mesmo hash do `save.sram` e screenshot de baixa informacao; isso e evidencia defeituosa, nao evidencia parcial.
- Se o projeto nao tiver emissao canônica de dump visual em SRAM, a regra acima nao se aplica; nesse caso o gate continua dependendo da evidencia padrao registrada pelo wrapper e pelo `emulator_session.json`.

### 14.3.2 Sandbox e frescor de SRAM

- `save.sram`, screenshots e artefatos auxiliares do BlastEm devem nascer dentro de `out/blastem_env_*` do projeto.
- fallback para `LocalAppData\\blastem\\rom` ou qualquer save root global invalida a evidencia de gate.
- `fresh_sram_confirmed=false`, `outside_sandbox_candidate` ou `stale_sandbox_candidate` devem ser tratados como evidencia `stale`.
- o fechamento do BlastEm no wrapper deve seguir `ESC -> WM_CLOSE -> Alt+F4 -> kill`, registrando o resultado no log JSONL.
- se o smoke integrado falhar antes de abrir o emulador por blocker real de build/validator, isso deve ser reportado explicitamente como falha do projeto, nao mascarado como sucesso de emulacao.

### 14.4 Perfil minimo observacional quando nao houver telemetria forte

- Na ausencia de `runtime_metrics.json`, ainda e obrigatorio registrar um perfil observacional honesto com `frame_stability`, `sprite_pressure`, `fx_load` e `perceptual_quality`.
- Campos observacionais devem usar linguagem explicita como `observado`, `estimado` ou `nao_medido`, nunca fingir precisionismo inexistente.
- Silencio intencional tambem e evidência valida de audio, desde que sustentado pela ausencia rastreavel de assets e rotinas sonoras no slice.

## 15. Tool-first audit obrigatorio

- Antes de criar automacao nova, o agente deve procurar ferramenta existente em `tools/`, auditar capacidade real e registrar decisao.
- Toda nova automacao exige:
  - ferramenta existente avaliada;
  - fixture executado ou fixture_skip_reason documentado (ainda bloqueia uso canonico);
  - decisao registrada: `reuse`, `wrap`, `improve`, `replace` ou `reject`;
  - justificativa quando criar substituto.
- `tools/mugen2sgdk` e ferramenta existente `legacy/unaudited`. O estudo MUGEN SFF Showdown e fixture canonica futura. Nao assumir que funciona so porque existe; auditar primeiro.
- Bloqueios: `tool_first_audit_missing`, `tool_first_decision_absent`, `tool_first_fixture_missing`, `tool_first_fixture_skipped`.
- Enforcement: `tools/sgdk_wrapper/audit_tool_first.ps1`.

## 16. Loop detector e meaningful-change gate

### 16.1 Loop detector

- Se os mesmos blockers aparecem em 3 builds consecutivos, bloquear novo build.
- O bloqueio so e removido com decisao estrategica documentada.
- Destravamento canonico: `doc/operational_loop_decision.json` valido (schema em `tools/sgdk_wrapper/schemas/operational_loop_decision.schema.json`).
- Metrica de progresso valida: blocker removido, status de entrega elevado, evidencia fresca compativel com ROM hash atual, visual/aprovação artistica quando o blocker dominante for visual.
- Numero de ROM/build isolado nao e progresso.
- Bloqueio: `operational_loop_detected`.
- Enforcement: `tools/sgdk_wrapper/detect_operational_loop.ps1`.

### 16.2 Meaningful-change gate

- O agente so pode gastar ciclo em mudanca que ataque explicitamente o blocker dominante.
- Se blocker dominante for `visual_gate_blocked` ou `perceptual_motion_unvalidated`, mudancas em wrapper/log/docs nao contam como avanco, exceto se forem necessarias para medir esse blocker.
- Bloqueio: `meaningful_change_absent`.
- Enforcement: `tools/sgdk_wrapper/audit_meaningful_change.ps1`.

### 16.3 Prioridade visual

- Se blockers dominantes forem visual/perceptual, bloquear trabalho de infraestrutura irrelevante.
- O agente deve priorizar mudanca significativa que ataque o blocker dominante.
- Para projeto `aaa_game` novo, retomado ou reaberto com intencao visual, seguir `tools/sgdk_wrapper/.agent/workflows/visual-first-project-lifecycle.md` antes de expandir runtime definitivo.
- Se o estado for `technical_runtime_creative_blocked`, `lab_evidence_not_delivery` ou `smoke_only`, nova ROM/build/screenshot so conta como progresso se remover ou reduzir blocker visual real: fonte premium, aprovacao humana, direcao arte-gameplay, conversao VDP, evidencia perceptual de movimento ou `visual_delivery_gate_report` canonico.
- A rota visual-first exige direcao, fonte e gate humano antes do runtime de entrega; runtime tecnico com placeholder e apenas smoke e nao substitui maturidade visual.

## 17. Placeholder quarantine

- Arte gerada por codigo geometrico, PIL/ImageDraw, procedural/debug/lab, builder tecnico ou fallback visual deve ser marcada como `placeholder` ou `technical_lab_asset`.
- Placeholder nunca pode ser promovido para entrega visual AAA.
- Placeholder pode validar pipeline tecnico, paleta, ResComp, VRAM ou animacao, mas nao pode satisfazer `visual_direction_approved`.
- HYBRIDO MUAY THAI usou geracao por PIL/ImageDraw; preservar aprendizado tecnico de PNG indexado/PLTE<=16/grid 9-bit, mas bloquear essa rota como solucao artistica final.
- Bloqueio: `placeholder_promoted_to_aaa`.
- Enforcement: `tools/sgdk_wrapper/audit_placeholder_quarantine.ps1` detecta por tag/nome declarado; `tools/sgdk_wrapper/audit_procedural_asset_provenance.py` mede a proveniencia real casando `.res` com builders. Arquivo com nome limpo produzido por `ImageDraw` passa pelo primeiro e reprova no segundo — rode os dois.

## 18. Qualidade tecnica vs qualidade artistica

- `art_diagnostic.py` valida formato tecnico: PNG indexado, PLTE, 9-bit, dimensoes, transparencia.
- `art_quality_gate.py` valida qualidade artistica: silhueta, escala, lineart, pose, appeal, coerencia fisica/animacao, aderencia ao GDD/DDA, coerencia com padrao AAA.
- Asset tecnicamente OK nao pode elevar `ready_for_aaa` se `artistic_gate_failed`.
- Saida de CLI do `art_diagnostic.py` deve ser ASCII-safe; icones Unicode quebram CP1252.
- Bloqueio: `artistic_gate_failed`.
- Enforcement: `tools/sgdk_wrapper/art_quality_gate.py`.

## 19. Gate de raiz/evidencia

- Bloquear quando relatorio, screenshot, ROM path, manifest, scene contract ou evidence JSON aponta para outro workspace/projeto.
- `project_root` reportado deve estar dentro do projeto ativo.
- ROM hash usado por validation, emulator evidence, scene regression e closeout deve ser o mesmo.
- Caminhos externos so sao aceitos se forem entradas copiadas para `rascunho/` com hash e manifest.
- Bloqueios: `evidence_root_mismatch`, `evidence_rom_hash_divergent`, `evidence_external_path_detected`.
- Enforcement: `tools/sgdk_wrapper/audit_evidence_root.ps1`.

## 20. Gate contra subprojeto orfao

- Se um estudo cria viewer SGDK aninhado, o root do estudo deve ter: manifesto agregador, memory bank, changelog, link para viewer, evidencia propria ou explicacao de status lab, fechamento do objetivo original.
- Subprojeto aninhado nao pode mascarar ausencia de projeto canonico no root.
- Bloqueio: `orphan_subproject_detected`.
- Enforcement: `tools/sgdk_wrapper/audit_orphan_subproject.ps1`.

## 21. Promocao por degraus

- `analise/conversao` != `implementado`;
- `assets exportados` != `ROM`;
- `ROM buildada` != `testada`;
- `screenshot` != `gameplay validado`;
- `tecnica documentada` != `tecnica dominada`.
- So elevar status quando houver evidencia correspondente.
- Nenhum status `MESTRE_*` pode nascer sem ROM, BlastEm, budget, uso real e aprovacao humana.

## 22. Visual gate antecipado

- Antes de loops longos de runtime, aprovar direcao visual minima.
- Procedural fallback/debug/lab nao pode virar final por exaustao.
- Se visual direction falhar, proxima etapa obrigatoria e remaster/direcao de arte, nao build incremental.
- Pipeline AAA: etapa `S1c_visual_gate_early` entre S1b e S2.

## 23. Deterministic boot obrigatorio

- Toda cena validavel precisa boot deterministico.
- Se `boot_mode` estiver `unsupported` ou `missing`, scene regression deve bloquear closeout.
- Nao permitir baseline/regression fake para cena nao bootavel.
- Bloqueio: `deterministic_boot_missing`.

## 24. Learning capture obrigatorio

- Closeout bloqueado com blockers recorrentes deve gerar lesson/failure_pattern ou justificar explicitamente no relatorio por que nao ha licao qualificada.
- Caso SMOKE_TEST: multiplos blockers recorrentes com learning ledger vazio deve ser tratado como falha de captura, nao como ausencia de aprendizado.
- Bloqueio: `learning_capture_skipped`.

## 25. Technique manifest obrigatorio em training/lab visual

- Estudos visuais tambem precisam declarar tecnica quando usarem paleta, sprite, animacao, DMA, VDP, pipeline de conversao ou tecnica de hardware.
- `technique_usage_manifest` vazio em estudo visual com assets/runtime deve bloquear closeout.
- Bloqueio: `technique_manifest_empty_in_lab`.

## 26. MUGEN como fixture canonica

- Contrato de fixture em `tools/sgdk_wrapper/.agent/references/mugen_sff_fixture_contract.json`.
- Entrada SFF/DEF local em `rascunho/` ou fixture controlada.
- Saida esperada: assets SGDK, resources.res, viewer ROM, screenshot BlastEm, reports de tilemap/paleta/budget/VRAM.
- Stage MUGEN largo com streaming por janela deve declarar `world_dimensions`, `viewport_dimensions` e `runtime_streaming` em `scene_tilemap_conversion_report.json`; campos experimentais soltos nao valem como contrato.
- `res_graph_report` com BIN customizado prova empacotamento, nao residencia; `validado_budget` exige evidencia de runtime, dump VDP/VRAM ou report de residencia vinculado ao hash da ROM.
- `mugen2sgdk` e `legacy_gui_tool_without_cli`; exigir wrapper/teste antes de uso canonico.
- Se falhar, justificar criacao ou incorporacao de parser/exportador alternativo.

## 27. Canonizacao conservadora de ferramentas

- MUGEN parser/export: `LABORATORIO` ou `TEORICA_STANDARD`.
- PNG palette validator / PLTE trim: `TEORICA_STANDARD` ate fixture aprovada.
- Runtime probe / scene regression: `TEORICA_STANDARD` ou `MESTRE` somente com evidencia canonica suficiente.
- Nunca promover para `MESTRE` neste lote sem aprovacao humana explicita.

## 28. Flags canonicas de script (WarnOnly, SkipManual, Force)

Scripts wrapper e gate devem expor consistentemente os seguintes flags canonicos quando aplicavel:

### 28.1 `-WarnOnly`
- Degrada falhas/erros para warning.
- O script continua executando mesmo quando encontraria blockers.
- Exit code normalmente e 0 quando combinado com erros degradados.
- Domínio: `scene_closeout_gate.ps1`, `validate_artifact_schema.ps1`, `validate_resources.ps1`.

### 28.2 `-SkipManual`
- Pula etapas que exigem intervencao humana ou confirmacao explicita.
- Nao equivalente a `-Force`; apenas omite passos com `manual_intervention_required=true`.
- Domínio: scripts de validacao com gate humano.

### 28.3 `-Force`
- Regenera ou reexecuta operacoes destrutivas/idempotentes.
- Nunca significa "skip validation"; forcar sobrescrita de artefato existente, recaptura de evidencia ou reavaliacao de blockers.
- Domínio: `capture_blastem_evidence.ps1`, `run_scene_regression.ps1`, scripts de conversao.
- `-Force` nao desliga outras validacoes; continua respeitando `-WarnOnly` se ambos forem passados.

## 29. Claim ceiling executavel

- antes de `first_playable`, `gameplay_rom_aprovada`,
  `performance=estavel`, `assets premium`, `scene closeout`,
  `validado_budget`, `ready_for_aaa` ou avancar de fase, execute
  `tools/sgdk_wrapper/audit_promotion_claims.ps1`;
- evidencia declara escopo e SHA-256 da ROM vigente;
- score tecnico de asset nunca equivale a aprovacao artistica;
- trabalho paralelo de runtime/visual exige `integration_owner`;
- divergencia entre memoria, validator e evidencia resolve pelo menor status
  consistente, nunca pelo relatorio mais otimista.

### 28.4 Convencao de step-skip
- Flags especificos de dominio como `-SkipBuild`, `-SkipRuntimeCapture`, `-SkipSceneRegression` permanece em `scene_closeout_gate.ps1`.
- Eles sao ortogonais aos canonicos: `-SkipBuild -WarnOnly` pula build e degrada falhas restantes.

### 28.5 Implementacao padrao
```powershell
param(
    [switch]$WarnOnly,
    [switch]$SkipManual,
    [switch]$Force
)
```
Scripts que consomem module `sgdk_artifact_contracts.psm1` herdam as helpers de envelope e fallback.
Exit code: `0` se `status != error` ou `WarnOnly` esta ativo; caso contrario `1`.

## 30. Doutrina de audacia — folga nao medida e timidez

O teto do hardware e o **alvo**, nao a margem de seguranca. Entregar uma cena a 40% do
orcamento sem ter medido ate onde dava nao e prudencia: e uma decisao que ninguem tomou.

- **Audacia e sobre a ambicao, nunca sobre o claim.** Empurre o que voce tenta; meca o que
  voce afirma. As duas coisas crescem juntas: quanto mais ousado o alvo, mais rigorosa
  precisa ser a medicao. Ambicao alta com claim medido e o padrao; ambicao baixa e desperdicio
  de hardware; claim alto sem medicao e falso verde, que o resto deste documento ja bloqueia.
- **Antes de fechar um orcamento, meca o proximo degrau.** Se 32 objetos cabem, meca 48 e 64.
  Pare quando **medir** o estouro, nao quando sentir receio. O numero que voce entrega tem que
  ser o resultado de uma busca, nao o primeiro que funcionou.
- **`unexploited_headroom`** e emitido por `tools/sgdk_wrapper/.agent/scripts/vdp_scanline_simulator.py`
  quando a utilizacao de pico fica abaixo de 60% sem justificativa. E **aviso, nunca blocker**:
  limpa-se declarando `headroom_justification` no input. O objetivo e forcar uma decisao
  consciente, nao proibir cenas leves.
- **Direcao de arte, level design, leitura de gameplay e demais premissas vencem a densidade** —
  mas precisam vencer **por declaracao**, nao por omissao. "Menos sprites porque a cena precisa
  respirar" e uma razao legitima e declarada; silencio nao e.
- **Falsa audacia** e a que parece ousada e piora o resultado: flicker para mascarar overflow,
  efeito sem consequencia, densidade que destroi leitura de silhueta, tecnica citada por nome
  em vez de por funcao. O canon ja bloqueia cada uma delas, e nenhuma vira permitida em nome
  de ser ousado.
- **Os dois limites por scanline sao medidos juntos.** O VDP impoe contagem de sprites **e**
  pixels de sprite por linha ao mesmo tempo (H40: 20 e 320; H32: 16 e 256). Para sprites de
  16px os dois fecham no mesmo ponto, o que faz parecer que existe so um. Claim de densidade
  exige os dois.

Caso canonico de audacia correta: a abertura `branding_sequence_v2` media 15 de 20 sprites por
linha e foi declarada segura. Medir o degrau seguinte mostrou que 56 estilhacos cabiam no lugar
de 32 — **+75% de densidade, sem tecnica nova e sem flicker**, apenas folga que estava sobrando
na mesa. Registro em `doc/curation/ASSET_PROVENANCE_BASELINE_2026-08-17.md`.

Caso canonico de falsa audacia, no mesmo episodio: multiplexacao com flicker foi proposta como
rota para "dobrar os sprites". Ela e vedada pelo proprio skill de budget (`ausencia de flicker`
e requisito de claim canonico) e, numa abertura de marca, degradaria a primeira impressao de
acabamento em painel moderno. Parecia mais ousada e entregaria menos.


## 31. Residencia de tiles medida no asset, antes do runtime

`res_graph_audit.ps1` confere VRAM lendo um projeto **construido**: ele nao responde nada
enquanto o runtime nao referencia os assets. Isso abre uma janela em que a arte esta pronta, o
orcamento ja quebrou e ninguem consegue dizer.

- **Residencia de tiles e medida no asset.** `tools/sgdk_wrapper/audit_tile_residency.py` le
  `res/*.res`, abre cada asset e conta tiles unicos de 8x8 com deduplicacao por flip H/V, que e
  o que de fato ocupa VRAM. Nao precisa de runtime.
- **Teto util derivado, nao inventado:** 2048 tiles, menos as nametables de BG_A/BG_B a 64x32,
  menos a SAT, menos a tabela de scroll por linha. O relatorio publica a derivacao.
- **Asset com streaming ocupa a janela declarada**, nao o conjunto inteiro. O gate le
  `vram_slots` do `dma_queue_contract` do projeto. Sem isso ele cobra o custo total de um asset
  cuja decisao de streaming ja foi tomada, e a diferenca decide entre estourar e caber.
- **`tile_residency_over_ceiling` bloqueia**: excesso de VRAM e fato de hardware.
- **`low_tile_dedup_ratio` avisa**: fundo grande com menos de 30% de deduplicacao foi composto
  como imagem fotografica e quantizado, nao autorado como conjunto de tiles. Custa como arte
  unica e costuma **ainda parecer repetitivo** — o pior dos dois mundos. E sintoma, nao
  violacao, entao nomeia o suspeito sem reprovar.
- **`unexploited_vram_headroom`** abaixo de 40% de utilizacao, por simetria com a secao 30.

Caso canonico: `branding_sequence_v2` entregou `img_forge_bg_b` com **2% de deduplicacao**
(1093 tiles unicos de 1120), contra uma linha de contrato orcada em 640 para todo o conjunto de
fundo. O agente de arte havia escrito que a parede "le como fiada", ou seja modular demais aos
olhos; a medicao mostrou o oposto na VRAM. Percepcao e custo divergiram, e so a medicao
explicou por que.

## 32. Fatos de hardware e de SGDK pagos com build

Cada item abaixo custou pelo menos um ciclo de build e captura na curadoria de 2026-08-17.
Registro em `doc/curation/ASSET_PROVENANCE_BASELINE_2026-08-17.md`.

- **Callback de H-Int precisa de `HINTERRUPT_CALLBACK`.** Handler declarado `void` faz o GCC
  emitir `RTS`. H-Int e excecao de nivel 4 e a pilha tem SR+PC: `RTS` desempilha so o PC e o SR
  vira a word alta do endereco de retorno. Sintoma exato: `M68K attempted to execute code at
  unmapped address 0x23080000`, onde `0x2308` e o proprio SR. Custou dois builds atacando o
  metodo de escrita no CRAM, que era risco secundario.
- **O VDP impoe DOIS limites por scanline ao mesmo tempo**: H40 da 20 sprites **e** 320 pixels;
  H32 da 16 e 256. Para sprites de 16px os dois fecham no mesmo ponto, o que faz parecer que
  existe so um.
- **Formula de setor acoplada a contagem gera duplicata invisivel.** `sector = index * 16 /
  SHARD_COUNT` com 32 objetos da `index/2`; se `born` tambem for `index/2`, todo par consecutivo
  nasce no mesmo quadro no mesmo angulo. Foram 16 pares perfeitamente sobrepostos: 32 sprites no
  SAT rendendo 16 posicoes visiveis. Use stride coprimo do numero de setores (`index * 5 & 15`).
  Corrigir isso **baixou** a pressao de scanline e destravou densidade que a medicao tinha
  reprovado.
- **`DIVS` de 32 bits no 68000 custa ~150 ciclos.** Um loop com 4 divisoes por objeto e 32
  objetos consome ~15% do quadro. Precompute em `enter` e troque divisao por reciproco em ponto
  fixo: `(delta * t^2 * (65536/dur^2)) >> 16`. Isso levou `over_budget_frames` de 12 para 0.
- **Offset de VRAM nunca e escrito a mao.** Derive de `tileset->numTile`. Uma contagem propria
  de dedup deu 304 onde o ResComp gerou 309, e os cinco tiles de diferenca sobrepuseram o
  recurso seguinte e encheram a tela de lixo.
- **`SPR_addSprite` com auto-alocacao esgota o pool em silencio e devolve `NULL`.** 56 objetos
  alocando os proprios quadros pediam 1292 tiles contra reserva de 320. Use tileset
  compartilhado com `SPR_setVRAMTileIndex` e `SPR_setAutoTileUpload(FALSE)`, e **conte as
  falhas**: caminho de erro mudo transforma claim de contagem em ficcao.
- **`VDP_setWindowVPos(FALSE, n)` liga a WINDOW nas fileiras 0..n-1; `TRUE` liga em n..27.**
  Desenhar fora da metade ativa come a tela.
- **Prioridade baixa com Shadow/Highlight ligado sai sombreada.** Wordmark que precisa ler pede
  prioridade alta, ou o operador escurece o tile.
- **Nibble impar nao existe no CRAM de 9 bits.** `0x0630` e `0x0CDD` sao invalidos; `0x0620` e
  `0x0CCC` sao validos.
- **`PAL_setColor` no indice 0 tem que rodar depois de carregar as paletas**, senao a carga
  devolve o magenta de transparencia do PNG ao backdrop.
- **Deduplicacao com flip H/V e o que ocupa VRAM**, nao a contagem bruta de tiles. Fundo
  fotografico quantizado deduplica quase nada: 1120 tiles brutos viraram 1093 unicos, 2%, contra
  73% de um irmao autorado com formas limpas.

## 33. Hierarquia de evidencia visual

Nem toda imagem de captura vale o mesmo. Julgar pelo artefato errado produz bug inexistente.

```
dump de VDP  >  screenshot  >  quadro de burst
```

- **Backdrop, paleta, prioridade e residencia se julgam pelo `visual_vdp_dump.bin`**, que
  carrega o CRAM real. Foi assim que se provou que `PAL0[0]` era `0x0000` enquanto um PNG
  mostrava borda magenta.
- **O primeiro quadro de um burst com delay zero e invalido.** A janela do emulador ainda nao
  terminou de compor e a superficie nao inicializada e gravada como magenta puro. Medido em
  cinco sessoes: `screenshot.png` e `frame_3` pretos, so `frame_1` magenta. O
  `capture_blastem_evidence_linux.sh` ja tem guarda; nao a remova.
- **Amostra pontual de telemetria nao substitui varredura.** Uma probe que amostrava 4 de 224
  scanlines por quadro reportou 6 onde a varredura media 23 — falso verde para configuracao que
  causaria dropout no console. Probe de pressao conta **todas** as linhas.
- **Probe que exporta uma vez so mede uma janela so.** Condicao de export atrelada a contagem
  de amostras satura e congela: o maximo acumulado cobria F90-F151 e nenhum pico posterior
  chegava a SRAM. Re-exporte periodicamente enquanto a cena roda.
- **Numero medido em uma geometria nao transfere para outra.** "56 estilhacos cabem a 18/20" foi
  medido com o logo em y=80; movido para y=64 o mesmo arranjo deu 22/20 e reprovou.
- **Quando modelo e hardware divergem, o hardware manda** — e a divergencia fica registrada em
  vez de ser resolvida por teoria.

**Bissecte antes de teorizar.** Duas hipoteses plausiveis e dois builds foram gastos num crash
cujo endereco ja apontava a causa. Um desligamento por vez encontra em minutos o que a teoria
nao encontra em horas.

## 34. Self-check obrigatorio em ferramenta de medicao

Na curadoria de 2026-08-17 **tres ferramentas de medicao apresentaram defeito na mesma
sessao**, e as tres davam leituras plausiveis:

| Ferramenta | Defeito | Consequencia |
|---|---|---|
| `vdp_scanline_simulator.py` | media contagem de sprites e ignorava o limite de 320 px por linha | metade do orcamento por scanline descoberta em todo projeto que a usou |
| `runtime_probe.c` | amostrava 4 de 224 scanlines por quadro | reportou 6 onde a varredura media 23: falso verde para configuracao que causaria dropout |
| `runtime_probe.c` | dois campos exportavam a constante `1` | `active_sprite_count` nunca mediu nada |

Duas delas me fizeram reportar bug que nao existia. Uma quase aprovou hardware estourado.
**Nenhuma acusou defeito por conta propria.**

- **Antes de a leitura de uma ferramenta valer em qualquer claim, o self-check dela precisa
  passar.** Numero vindo de instrumento nao verificado nao sustenta contrato, report nem
  promocao de status.
- **O self-check exercita os DOIS sentidos:** uma fixture que passa e uma que reprova.
  Ferramenta que so sabe dizer `ok` nao esta medindo — esta concordando.
- **Cada blocker que a ferramenta pode emitir merece uma fixture** que o dispare. Blocker sem
  fixture e blocker que ninguem sabe se funciona.
- **Enforcement:** `tools/sgdk_wrapper/validate_measurement_tools.py` roda o self-check de
  cada ferramenta canonica de medicao e reprova com
  `measurement_tool_self_check_failed`, `..._no_self_check`, `..._missing` ou `..._timeout`.
  O proprio meta-gate tem self-check e se submete a regra que aplica.
- **Ferramenta nova de medicao entra na lista `MEASUREMENT_TOOLS`** no mesmo commit em que
  nasce. Injetor e gerador ficam fora: eles nao produzem numero que vira claim.

- **Copia local de ferramenta de medicao precisa estar identica a canonica.** Self-check que
  passa **nao prova que a ferramenta esta atual**: uma copia da v1.0.0 do simulador passa no
  proprio self-check, porque ele so testa o que aquela versao faz, e **aprova uma cena com
  512 px numa linha contra um teto de 320**. Ferramenta obsoleta com self-check verde e pior
  que ferramenta sem self-check, porque parece verificada. Blocker:
  `measurement_tool_stale_copy`. Copia sob `out/`, `rascunho/` ou `__pycache__` e backup morto
  e sai como aviso.

Limite declarado: o meta-gate garante que o self-check existe, roda e passa. **Ele nao julga se
o self-check cobre o que deveria** — isso continua sendo leitura humana, e e por isso que a
mensagem de cada self-check diz em texto o que ele exercitou.

Corolario da secao 33: quando modelo e hardware divergem, verifique o instrumento **antes** de
escolher em quem acreditar. Nas tres vezes em que isso aconteceu nesta curadoria, o instrumento
estava errado.

## 35. Nenhum gate ve composicao

Todo validador deste workspace mede **hardware**: residencia de tiles, pressao por scanline,
procedencia de asset, compreensao de marca, orcamento de CPU. Nenhum deles olha para **onde as
coisas estao na tela**.

Medido: o ato 3 do branding do modelo tinha 0 sprites, 865 de 1740 tiles e `over_budget: 0` —
**todos os gates verdes** — com quatro wordmarks empilhados na mesma faixa `y=80..128` no quadro
451 (bigorna, FORGE, MISAEL, MASTER). A cena estava ilegivel e nenhum numero acusou.

- **Composicao se pega com planta baixa, nao com validador.** Storyboard com posicao na tela,
  por quadro-chave, antes do primeiro asset. Ver `workflows/scene-direction-first.md`.
- **Continuidade nao e ausencia de remocao.** Proibir corte a preto sem dizer COMO cada elemento
  sai produz acumulo. O contrato do ato 3 dizia apenas "nunca use `VDP_clearPlane`", e o
  resultado foi zero remocoes no codigo. **Todo elemento que entra precisa de saida desenhada** —
  scroll, fade, varredura ou substituicao — declarada no storyboard junto com a entrada.
- **Gate verde nao e cena aprovada.** Aprovacao artistica se le em captura; ela nunca sai de um
  exit code.

Estado de enforcement: **medido** por `audit_stage_occupancy.py`. Declare um bloco
`stage_occupancy` no storyboard com zonas (faixa + `max_concurrent`) e elementos (faixa + janela
de quadros + `exit`). A varredura devolve o pior quadro por zona. Blockers:
`stage_zone_over_capacity`, `element_without_declared_exit`,
`declared_band_diverges_from_runtime`.

**Declare a faixa com `runtime_ref` apontando para as constantes do C.** Declaracao envelhece: o
`vertical_rhythm` deste storyboard ainda dizia baseline y=128 com `author_tile [8,12]` depois que
o codigo ja tinha ido para `[8,3]` — descrevia uma cena que nao existia mais. Com `runtime_ref`, o
gate reprova quando o runtime anda sem a planta baixa junto.

Limite declarado: isto mede **sobreposicao de faixa**, a metade geometrica da composicao. Nao le
hierarquia, peso, direcao de leitura nem ritmo. Ocupacao 1 nao significa cena bem composta, e a
captura continua obrigatoria.

## 36. Adjetivo de direcao precisa de piso numerico

Palavra qualitativa em brief de arte vira defeito reproduzivel quando nao carrega numero.

Medido: "leve, sem chanfro" para o PRESENTS produziu **99% da tinta num indice de luma 38 contra
fundo de luma 46** — contraste de **-8**, texto mais escuro que o fundo. O adjetivo pedia
discricao e o artista entregou discricao; o brief e que confundiu dois eixos.

- **"Discreto" e sobre tamanho e peso. Nunca sobre contraste.** Elemento pequeno com contraste
  alto le como discreto; elemento grande com contraste baixo le como borrao.
- **Todo adjetivo de direcao carrega piso**: "leve" precisa de piso de luma, "sutil" precisa de
  delta minimo, "denso" precisa de contagem.
- **A direcao pode estar errada.** Quando o artista entrega diferente do pedido e a entrega le
  melhor, corrija a direcao em vez de reprovar o trabalho. A silhueta "sobre transparente" era
  aperto sem ganho, e foi a entrega que mostrou isso.

Corolario da secao 30: o indice de paleta e **contrato** porque o runtime depende do papel dele;
o valor hex e **semente** que o artista refina. Trocar hex e passe de arte; trocar papel quebra
runtime.

Estado de enforcement: **medido** por `audit_luma_floor.py`. Declare um bloco `luma_floor` com
pares elemento/fundo, a regiao exata onde o elemento e carimbado e as camadas de fundo compostas
de tras para frente.

**O piso e 34** — um degrau de componente do Mega Drive (0,34,68,...,238). Contraste abaixo de um
degrau nao existe no console. Blockers: `luma_contrast_below_floor` quando mais de um terco da
tinta cai sob o piso, e `no_readable_highlight_mass` quando intencao de realce nao tem 20% de
massa com contraste positivo.

**A metrica e massa de tinta, nunca media de luma.** A primeira versao desta ferramenta usava
media e reprovou o PRESENTS, que le muito bem: 58,8% da tinta dele e contorno preto, e contorno
escuro e recurso de legibilidade, nao defeito. Media de contorno com preenchimento nao mede nada.
Calibrar contra falso positivo antes de publicar e a secao 37.

Limite declarado: mede **luma**, nao legibilidade. Tinta e fundo podem estar longe em luma e
brigar por matiz; serifa fina ou fundo ruidoso continuam ilegiveis com contraste alto.

## 37. Gate precisa reprovar em teste e ser calibrado contra falso positivo

Duas metades da mesma regra, e este workspace errou as duas.

- **Gate que nunca reprovou nao esta medindo.** Toda trava precisa de fixture que passa **e**
  fixture que reprova, exercitadas no self-check da secao 34.
- **Gate que reprova projeto saudavel sera desligado.** A primeira versao do detector de arte
  procedural reprovou **9 de 9 projetos** por confundir enderecamento de VRAM (`TILE_USER_INDEX`,
  `VDP_setTileMapXY`) e paleta autoral com desenho por codigo. Um gate assim nao protege nada:
  ele treina o time a ignorar o vermelho. Calibre contra a arvore existente **antes** de publicar.
- **Caminho de erro sem contador transforma claim de contagem em ficcao.** `brandEnsureShard`
  retornava mudo em `NULL`; a contagem de 56 estilhacos so virou fato quando um contador provou
  `spawned=56, failed=0`. Todo `return` de falha precisa incrementar algo que seja exportado.

Corolario da secao 15: antes de escrever regra nova, **procure a existente e leia o enforcement**.
A proibicao de arte procedural ja existia em 8 lugares em prosa e nao era medida em nenhum — 78
de 136 simbolos violavam. Quando a regra ja esta escrita, o gap e medicao, nao vocabulario.

## 38. Capacidade declarada com prova antes de promessa

Agente que promete o que nao sondou engana o usuario duas vezes: na promessa e na correcao
tarde. Este workspace ja perdeu tempo nos dois sentidos — agente alegando gerar imagem nativa
sem ter canal nenhum, e skill canonica citando schemas que nao existiam em disco.

**Regra:** antes de aceitar ou iniciar qualquer tarefa dependente de capacidade (gerar imagem,
buildar, rodar emulador, tocar audio), o agente executa uma **sonda real** — comando rodado,
output capturado — e declara a capacidade em um de tres estados:

```
capaz_com_prova_agora      -> sonda passou agora, nesta sessao
capaz_apos_preparo_medido  -> sonda falhou por preparo ausente, custo de preparo medido e declarado
nao_capaz_neste_host       -> sonda falhou por limite estrutural do host/agente, declarado sem promessa futura
```

Nao existe quarto estado. "Acho que consigo", "deve funcionar" e "um modelo como eu normalmente
faz isso" sao proibidos como base de decisao.

**Proibições duras:**

- Prometer resultado ao usuario antes da sonda.
- Basear claim de capacidade em memoria de outra sessao, em fama do modelo ou em documentacao
  desatualizada.
- Silenciar quando a sonda contradiz a suposicao inicial — a correcao e imediata e explicita.

**Arvore de roteamento quando existem multiplas vias** (caso concreto: geracao visual):

```
Ramo A: agente gera nativo com prova   -> gera e persiste agora
Ramo B: host tem requisitos            -> prepara via circuito local e gera
Ramo C: nem agente nem host            -> emite diretriz para modelo sucessor capaz
```

O Ramo C e entrega, nao bloqueio morto: `successor_asset_directive` com papel, contexto,
assets, proveniencia exigida e gates de chegada. Skill dona: `image-generation-routing`.

**Limite declarado:** isto mede honestidade de claim na porta de entrada da tarefa, nao
qualidade da execucao. Sonda que passa nao garante asset bom; sonda que nao passa impede
promessa falsa. Enforcement: toda decisao de canal/capacidade registra report JSON com os
campos `probe_attempted`, `probe_output` e estado final do vocabulario — sem report, o claim
nao existe.
