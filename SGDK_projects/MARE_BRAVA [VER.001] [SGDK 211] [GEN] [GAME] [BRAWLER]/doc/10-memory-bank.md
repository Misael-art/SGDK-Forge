<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `doc/aaa_pipeline_gate_report.json` + `out/logs/freshness_audit_report.json`
- Ultima sincronizacao: `2026-08-30T14:50:00-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 12
- Ultimo build versionado: build_v003
- ROM vigente: `144fb573b088375c68f71d4255282db315052fe0f8de351e595806e6b734abd4` (`262144` bytes)
- Validation summary: `errors=0`, `warnings=10`, `checked=20` (validacao de recursos concluida em 2026-08-30)
- Blockers vigentes: `taina_native_48x64_lineart_visual_fidelity_pending` (a representação 48x64 já foi produzida; o blocker anterior foi corrigido de `taina_native_48x64_lineart_missing` para `taina_native_48x64_lineart_representation_mismatch`), `tile_residency_over_ceiling`, `stage_bgm_source_missing`, `freshness_audit_stale`
- Evidencia de emulador: sessao BlastEm selada por hash em `out/evidence/blastem`, com `emulator_session.json` canonico
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker — MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

**Ultima atualizacao:** 2026-08-30 (Visual Forge P0.1-P0.6; migracao de lineage da TAÍNA executada; runtime_probe reconciliado e buildado)
**Fase atual:** `technical_runtime_visual_translation_authorized`. A ROM atual é uma prova técnica de integração; seus assets procedurais não constituem baseline visual. Não é vertical slice, NÃO é `ready_for_aaa`, NÃO é `visual_pass`.
**Proxima fase:** model sheet pixel nativo da TAÍNA a partir da fonte aprovada; congelar expansão de conteúdo sobre a arte provisória até que TAÍNA, CRIA, CAIS e FX tenham proveniência final, qualidade, budget e evidência.

### Sessao MODO GO — 2026-08-30 — S0 a S6 + ownership de runtime

- S0 foi reaberto com contexto `aaa_game`, teto `vertical_slice` e rota
  `source_translation` registrada em `doc/route_decision_record.json`.
- S1–S6 receberam os artefatos de radar criativo, mecânicas, level design,
  enemy design, áudio adaptativo e transições. O design está documentado, mas
  não sustenta `game_production_ready` enquanto áudio de gameplay e provas
  vivas forem pendentes.
- A ownership da câmera saiu do contrato para o runtime em
  `src/system/camera.c`; `scene_demo.c` agora consume `CAMERA_getX()` e a
  câmera usa fix32 interno, deadzone, lookahead, clamp de 192 px e snap inteiro.
- `scene_branding.c` deixou de escrever PSG diretamente: os pulsos passam por
  `AUDIO_pulsePsg()`. Atualizações de CRAM e HScroll por linha usam a fila DMA.
- Build limpo pela rota `linux_wine_bridge` gerou ROM de 262144 bytes com SHA
  `144fb573b088375c68f71d4255282db315052fe0f8de351e595806e6b734abd4`.
- `validate_resources.ps1`: `errors=0`, `warnings=10`; isto é build/validação
  estrutural, não prova de boot, gameplay, áudio ou performance em BlastEm.
- `audit_tile_residency.py` permanece bloqueado em `2117/1740` tiles únicos
  (122% do teto utilitário); a resolução arquitetural continua sendo
  `tilemap_streaming`/residência por janela, não reduzir o claim por silêncio.
- Estado honesto: `buildado`, `testado_em_emulador=false`,
  `validado_budget=false`, `ready_for_aaa=false`.

### Evidência BlastEm e revisão de runtime — 2026-08-30

- A rota Linux preparada pelo workspace executou BlastEm 0.6.2 via Flatpak e
  selou `out/blastem_evidence/blastem-linux-20260830T180348Z-3682089/` para a
  ROM `144fb573b088375c68f71d4255282db315052fe0f8de351e595806e6b734abd4`.
  O pacote contém screenshot, `save.sram`, `visual_vdp_dump.bin`,
  `runtime_metrics.json`, áudio raw e manifesto selado; a auditoria de
  evidência reportou `status=ok`, blockers=0.
- A screenshot é informativa (320×224, 401 cores únicas, sem captura vazia) e
  mostra CAIS_01 com TAÍNA e CRIA. O `runtime_metrics` identifica cena 3,
  frame 151, snapshot de 59.7 fps, 7 sprites ativos e 4 sprites máximos por
  scanline; isso prova boot/cena/semântica, não estabilidade sustentada.
- O mesmo snapshot mediu `max_cpu_load=172` e `over_budget_frames=61` em 32
  amostras. Performance fica bloqueada até reduzir redraw/DMA/residência e
  repetir a captura na mesma hash.
- `audit_tile_residency.py` com self-check passou, mas o parecer real continua
  bloqueado: 2.117 tiles simultâneos contra teto utilitário de 1.740 (122%).
  A próxima rota é `tilemap_streaming` ou escopo residente por janela, nunca
  esconder o excesso por compressão ROM.
- `scene_closeout_gate.ps1 -WarnOnly -SkipRuntimeCapture` gerou status
  `warn`; a captura posterior fechou o pacote de evidência, mas gameplay por
  input e regressão de câmera ainda não foram isolados.
- Revisão de código: `review_passed_with_risk`. APIs SGDK 2.11 foram conferidas,
  sem `float/double`, heap no loop ou PSG direto fora do owner de áudio; riscos
  restantes são performance, residência, áudio de gameplay e arte nativa.
- Sync final desta iteração: `validate_resources.ps1` concluiu com
  `errors=0`, `warnings=10`, e o `fresh_evidence_bundle_audit_report` canônico
  passou com blockers=0 usando `out/evidence/blastem/evidence_manifest.json`.
  O closeout terminou com 11/13 passos sucedidos, 1 pulado e 1 bloqueado.
  Freshness ainda aponta `runtime_metrics`/`emulator_session` stale e o gate
  global segue bloqueado por visual, tilemap, changelog e performance; nenhum
  status verde foi inferido.

### Reconciliacao operacional vigente — 2026-08-30

- O contrato machine-readable vigente e
  `doc/contracts/visual_toolchain_reconciliation_v01.json`.
- As tres imagens 1086x1448 sao **aprovadas artisticamente** pelo owner como
  referencias de construcao. O tamanho, RGB/RGBA e a ausencia de grid nativo
  impedem somente a promocao direta para `res/` e qualquer claim final.
- **[2026-08-30] Migracao de lineage executada.** As tres imagens saíram de
  `rejected/` para
  `data/source_art/concept/taina_pixel_model_sheet/construction_reference/`.
  O conteudo nao mudou: os tres SHA-256 declarados em
  `visual_source_of_truth_taina_v02.json`,
  `premium_source_manifest.json` e
  `taina_derived_visual_sources_human_approval_v01.json` foram reconferidos
  contra os arquivos movidos e batem. Os 5 contratos que citavam o caminho
  antigo foram repontados; o changelog nao foi reescrito, recebeu entrada nova.
- A pasta `rejected/` continua existindo e agora contem **apenas**
  `taina_native_pixel_model_sheet_candidate_rejected_v01.png`, que e de fato
  rejeitada e nao e citada por contrato nenhum. Nome e status coincidem.
- GIMP foi recuperado depois da tentativa historica, mas a automacao de
  ponteiro nao ofereceu precisao/observabilidade suficiente. GUI deixa de ser
  dependencia do pipeline; o core planejado e CLI deterministico.
- Ainda nao existe lineart 48x64 aceita. Conversao automatica da fonte pode
  gerar apenas `basic_control`; a candidata `elite` exige reconstrucao nativa e
  `model_sheet_to_sprite_fidelity_report`.
- Diagnostico, arquitetura, matriz de ferramentas, testes e roadmap estao em
  `../../doc/05_technical/visual_forge_toolchain_diagnostic_and_implementation_plan_2026-08-29.md`.
- Plano local: `doc/23-visual-forge-adoption-plan.md`. Prompt de execucao:
  `../../doc/prompts_modelo/prompt_mestre_visual_forge_e_mare_brava_aaa.md`.
- O registro e plano nao promovem nenhum PNG, nao alteram a ROM e mantem
  `ready_for_aaa=false`.
- Validacoes de registro em 2026-08-30: contexto `ok`, metodologia `passed` e
  higiene `passed`. O gate de source of truth permanece `blocked` por
  `visual_lineage_scan_read_failed` em JSONs profundos; e falha do parser/gate,
  nao da arte, e precisa de regressao antes de qualquer claim de lineage limpo.

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

### Baseline visual ratificado em 2026-08-29

- **ROM vigente:** `e07fa63b6aa6e7bec542814950eb9190f7a5e04732da362c27f01b84398dfd5e`
  (`out/rom.bin`, 262144 bytes). Hashes que aparecem nas entradas históricas
  abaixo são contexto auditável, nunca identidade da ROM atual.
- Nova prancha-fonte da TAÍNA em
  `data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png`
  (SHA-256 `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`)
  está registrada como `approved_authorial_source_for_pixel_translation` pelo
  owner humano. Ela preserva os marcadores de identidade, mas é conceito
  high-res e ainda falha a escala pixel de 3.5 cabeças; autoriza o model sheet
  48x64, não a promoção direta para `res/`.
- `doc/contracts/visual_source_of_truth_taina_v02.json` trava essa prancha
  como origem da próxima geração e rebaixa explicitamente todos os PNGs
  runtime da TAÍNA para evidência, jamais fonte. O contrato de tradução
  `doc/art/characters/taina/taina_reseed_native_translation_contract_v01.json`
  autoriza apenas a lineart 1 px em 48×64; ainda não existe pixel novo nem
  model sheet convertido.
- **[estado de 2026-08-29, SUPERADO em 2026-08-30 — ler o bloco de
  reconciliacao no topo deste arquivo antes de agir]** O gate físico da lineart
  48×64 tentou três rotas isoladas. A e C geraram ilustrações 1086×1448
  descritas na época como *rejeitadas*; **essa leitura foi revista**: o owner
  as aprovou artisticamente como referência de construção, e o que as impede é
  tamanho/RGB/ausência de grid nativo, não julgamento visual. B não abriu um
  editor interativo no host **naquela data**; o GIMP foi recuperado depois, e
  mesmo assim a GUI deixou de ser dependência do pipeline.
  O relatório `doc/art/characters/taina/taina_reseed_native_lineart_gate_attempts_v01.json`
  sela os resultados e exige um PNG nativo indexado de autoria externa ou em
  editor funcional. Não há novo asset jogável, conversão, mudança de ROM ou
  claim de progresso visual além dessa evidência negativa.
- `doc/asset_provenance_manifest.json` agora declara os 20 símbolos visuais
  ativos. Todos estão classificados como `procedural_primitive` e
  `placeholder`; o auditor de proveniência passou sem blockers porque o estado
  deixou de ser oculto, não porque algum asset foi aprovado como arte final.
- `doc/art/quality_reference_board.md` e a referencia local obrigatoria de
  qualidade. Os quatro PNGs copiados em `rascunho/entrada_bruta/quality_reference/`
  sao `quality_reference_only`, com hash no manifesto de higiene; nunca viram
  source art para copiar.
- Nenhuma avaliacao pode aprovar asset por melhora relativa ao placeholder,
  build verde ou screenshot. Personagem deve preservar anatomia, rosto,
  figurino, materiais e intencao de movimento; CAIS deve nascer de kit modular;
  FX deve ter fases por clusters e consequencia de jogo/mundo.
- O runtime atual CAIS/TAÍNA/CRIA/FX fica reclassificado como
  `technical_style_probe`, proibido como baseline ou fonte de nova geracao.
- `doc/aaa_pipeline_gate_report.json` e
  `doc/claim_owner_artifact_matrix_v01.json` reconciliam a ROM
  `e07fa63b6aa6e7bec542814950eb9190f7a5e04732da362c27f01b84398dfd5e`.
  O menor status consistente é `runtime_candidate`: fonte da TAÍNA e jab
  possuem evidência limitada; produção visual, slice, budget, áudio e AAA
  continuam bloqueados.

### Incremento técnico de combate — pendente de prova em emulador

- O primeiro seed jogável de combate agora separa explicitamente hit e hurt:
  jab da TAÍNA causa 15 de dano uma vez no frame ativo, e a CRIA possui 40 HP,
  8 VBlanks de invulnerabilidade, estado de hurt/recuo e desativação ao zerar
  HP. O ataque da CRIA aplica 5 de dano e 24 VBlanks de invulnerabilidade à
  TAÍNA. Isto é lógica técnica, não confirmação de feeling, balanceamento ou
  combate final.
- O contrato vivo é
  `doc/contracts/cais01_combat_seed_collision_topology_v01.json`. Coordenadas
  de colisão permanecem em mundo (`fix16`); câmera somente apresenta. Solid,
  push, hit, hurt e futuros grabs seguem domínios separados.
- Para promover este incremento além de `implementado`, faltam build limpo e
  prova controlada no BlastEm de dano único do jab e invulnerabilidade de ambos
  os combatentes. O build limpo e a sessão selada da ROM
  `e07fa63b6aa6e7bec542814950eb9190f7a5e04732da362c27f01b84398dfd5e`
  existem em `out/evidence/cais01_combat_seed/blastem-linux-20260829T220742Z-874842/`:
  screenshot, SRAM, VLAB/VDP dump e métricas pertencem ao mesmo hash.
- A sessão mede cena 3, 320×224, snapshot de 60.2 fps, `max_cpu_load=95`,
  `max_scanline_sprites=4` e sete sprites ativos. É uma observação de cena,
  não prova sustentada de performance ou budget final.
- O binding do BlastEm é `a -> gamepads.1.a`, mas requer o toggle de captura
  `Control_R`. Com foco, captura ligada e um único `a`, a sessão selada
  `blastem-linux-20260829T230057Z-984247` observou `C:040 -> C:025`: o jab
  causa exatamente 15 de dano na CRIA. A invulnerabilidade de 24 VBlanks da
  TAÍNA continua não isolada em emulador. Relatório:
  `out/logs/cais01_combat_seed_evidence_review_v01.json`. HUD continua
  telemetria técnica até existir UI autorada.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- Build Linux atual existe: `out/rom.bin`, 262144 bytes, SHA-256 `e07fa63b6aa6e7bec542814950eb9190f7a5e04732da362c27f01b84398dfd5e`, comprovado pelo build bridge e pelas sessões seladas de 2026-08-29. O SHA `e6b84c...` abaixo pertence a uma entrada histórica e não sustenta claim atual.
- O seletor canônico `out/logs/sgdk_build_route_report.json` classificou este host como `linux`, rota `linux_wine_bridge`, com `gcc.exe` 13.2.0, `libmd.a` de origem LTO 16.1.0 incompatível para link direto e biblioteca staged 13.2.0 sem LTO compatível.
- Evidência BlastEm da ROM atual existe em `out/blastem_env_taina_idle_guard_v02/blastem-linux-20260729T094431Z-325801/`: cena 3, screenshot, GIF, 12 quadros, SRAM e `runtime_metrics.json`. A captura sem VLAB/dump VDP é parcial e não fecha `testado_em_emulador`.
- `validate_resources.ps1` atualizado em 2026-07-08: `emulator_evidence_reason=ok`, `boot_emulador=ok`, `aggregate_status=emulator_observed_budget_pending`, `max_delivery_status=technical_artifact_only`; 0 erros/8 warnings.
- `scene_contract_compile_report.json` existe e compilou 4 cenas em modo production, mas o lint interno não rodou (`lint_ran=false`, `lint_status=error`); tratar como observação parcial, não fechamento.
- `res_graph_report.json` existe e passou 10 declarações em 1 `.res` sem issues/missing sources; porém `vram_residency_status=not_measured`, `measurement_level=estimated` e `tile_stats` das imagens falharam no host Linux por dependência de imagem/.NET. Não promove `validado_budget`.
- `visual_delivery_gate_report.json` existe em `out/logs/` e bloqueia explicitamente promoção visual: TAÍNA v05 melhora cabelo/rosto/guarda/roupa sobre v04, mas segue bloqueada por deriva chibi de escala e animation gate ausente; cena/tilemap/paleta não convertidos e captura BlastEm cobre apenas boot/menu.
- FASE 2 completa (2026-07-03): `doc/contracts/tdd_contract.json` (FSM, pools, DMA ownership, NTSC-first, tecnicas com registry) + `doc/contracts/brawler_belt_scroll_design_contract.json` (roster TAINA/JACO, 6 arquetipos com frame data, 3 stages com boss, combat/balance) + `mechanic_contract.json` (combo_de_mare), `level_blueprint.json` (cais_01), `enemy_roster.json`. TODOS 100% validos nos schemas; `audit_game_design_contracts`: passed, blockers=0; `validate_brawler_belt_scroll_specialization`: passed=11 failed=0.
- FASE 3 (direção): `doc/art/` com art_direction_decision_record (angular_cps2_fighter, confianca 0.70), concept_art_direction_brief, master_style_manifest, moodboard_manifest, brand_identity_manifest (planned), style_drift_policy, art_asset_diagnostic (rota 3_no_art), art_generation_brief.md pronto para disparo.
- 16 PRDs materializados (art bible, palette master, benchmark, rom mastering, ci, code review etc.); `check_prd_readiness`: ok, blockers=0 (target prototype).
- Validadores canonicos todos verdes: contexto, metodologia, higiene (corrigido caminho absoluto de drive Windows herdado do template em scene-contracts.json).
- Projeto nascido em 2026-07-03 via `new_project.sh` (template `tools/sgdk_wrapper/modelo`, rota Vibe Playable, `blocked_no_premium_source`).
- `doc/project_context_manifest.json` classificado `aaa_game`/`active`, teto `vertical_slice`; validado: `status=ok context=aaa_game phase=planning blockers=0`.
- `doc/genre_specialization_manifest.json` com opt-in humano em `brawler_belt_scroll`.
- FASE 1 completa: `doc/00-project-brief.md`, `doc/11-gdd.md` (core loop, feature scope map, técnicas com registry ids, radar criativo, seeds de escala/câmera/UI/brand), `doc/12-roteiro.md` (roteiro scope), `doc/13-spec-cenas.md` (roadmap 3 cenas + detalhamento CAIS_01 + seeds S2-S6).
- Herdados do template (estruturais): cena de branding com 5 `IMAGE` em `res/branding/`, runtime probe MDRT, contratos de scene-regression. São baseline de template, ainda `documentado` para este projeto (sem build próprio).

### O que e placeholder

- Assets de gameplay: concepts/source candidates existem; TAÍNA tem linearts técnicos v01-v05 em `data/processed/characters/taina/lineart/`, mas nenhum está aprovado/promovido para `res/`. Inimigos e cais ainda dependem de conversão/curadoria VDP.
- Exceção já promovida sob aprovação específica: `taina_idle_guard_48x64_v02.png` está em `res/`, compilada e observada no BlastEm; os linearts históricos continuam negativos/não promovidos.
- Branding herdada usa logos do template; precisará de art pass com a identidade MARÉ BRAVA.
- Áudio: nenhuma música/SFX do projeto; direção declarada no GDD apenas.

### O que falta para o slice ser completo

- CANAL DE GERAÇÃO (corrigido em 2026-07-09): quando a sessão do agente expõe
  ferramenta nativa de imagem, `out/logs/generation_channel_decision.json`
  deve selecionar `native_chat_image_generation_callable` e `next_action:
  use_native_channel`. Bonsai sem licença, host AMD e ComfyUI offline não são
  blockers nesse cenário; viram apenas fallback local se não houver nativo/API.
- Gerar premium source do CAIS_01 conforme `doc/art/art_generation_brief.md` + aprovação humana + conversão VDP.
- FASE 4: laudo `megadrive-vdp-budget-analyst` do CAIS_01.
- FASE 5: runtime C (FSM, combate, wave manager, câmera, HUD, XGM2).
- FASE 6: build + BlastEm + evidência (screenshot + save.sram MDRT + runtime_metrics 60fps).

### Snapshot dos gates QA

- visual_lab_aprovado: false (sem arte)
- gameplay_rom_aprovada: false (ROM existe, mas gameplay/performance/audio/hardware real nao foram provados)
- ready_for_aaa: false
- freshness_audit: warning atual com `stale_count=0` e `missing_required_count=2` (`out/logs/validation_report.json` e `out/logs/build_output.log` ausentes). O compilador de contratos e o grafo de recursos foram renovados em 2026-08-29; o lint do compilador segue `error`, portanto a renovação não é aprovação de cena.
- scene_closeout_gate: ausente
- build: sucesso_com_warnings
- boot_emulador: ok (BlastEm, escopo boot/menu)
- performance: nao_medido
- audio: nao_testado

### Ambiente de producao (host)

- Host atual: Manjaro Linux. A rota canônica de compilação é decidida por `tools/sgdk_wrapper/select_sgdk_build_route.py`.
- Linux: usar `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh --project-root <projeto>`. A bridge materializa staging em `out/host_tools/`, reconstrói `libmd.a` sem LTO com o GCC 13 empacotado e preserva o SDK de origem.
- Windows: usar `tools/sgdk_wrapper/build.bat <projeto>`. Antes do build, o seletor deve provar que `gcc.exe` e a `libmd.a` LTO possuem major compatível; em mismatch, restaurar/reconstruir a biblioteca com o compilador empacotado.
- Proibido misturar as rotas: `.bat`/PowerShell sob Wine não é a rota Linux, e a bridge Linux não é workaround para um SDK incoerente no Windows.
- Guard de ambiente roda com `pwsh` + `USERPROFILE=$HOME` + shim `powershell→pwsh`; Graphify com `-SkipGraphify` até o fix de `Get-Item -Force`.

---

## 2. O QUE ACABOU DE ACONTECER

**2026-07-04 (sessão 6) — Prompt mestre e contrato de aceite para agente de imagem**

- Pedido humano aplicado: o agente de imagem deve gerar matéria-prima premium organizada (`concept_art` / `source_candidate`), não level pronto, sprite final, tilemap final ou asset para `res/`.
- Criado `doc/art/prompt_pack/06_image_agent_master_prompt.md` como handoff autocontido para outro agente de imagem, com leituras obrigatórias, paleta, estilo, negative prompt, fluxo, asset IDs e status proibidos.
- Atualizados prompts 00-05: IDs de assets por pasta, geração de 4 variações, descarte em subpastas, relatórios obrigatórios, teste de silhueta, teste monocromático de logo, HUD/FX separados e `dock_pickups_small_props`.
- Criados `doc/art/prompt_revision_report.md` e `doc/art/asset_acceptance_report.json`.
- `data/source_art/premium_source_manifest.json` recebeu política de status; `bgb_loop` reclassificado para `mood_reference_only` (referência de bandas BG_B, não source direto para `res/`).
- `doc/art/art_asset_diagnostic.json` atualizado: o projeto não está mais em `3_no_art`; há concepts, mas todos seguem bloqueados para promoção até nova curadoria, ratificação humana e conversão VDP.
- Diagnóstico operacional rodado via `art_diagnostic.py`: cenário `2_res_inadequate_check`; concepts/source PNGs aparecem como RGB/RGBA não indexados e reforçam que nada pode ir para `res/` sem pipeline VDP.

**2026-07-03 (sessão 5) — Correção de autoria do level art do CAIS_01**

*Artefatos de montagem construídos pelo agente (continuação da sessão 5):*

- `doc/contracts/dock_scene_kit_inventory.json` — auditoria dos sources: bgb_loop = referência modular utilizável; 3 painéis de arena = mood/landmark_reference_only (reclassificados no premium_source_manifest); TODOS os 6 boards modulares (prompts A-F) = lacuna real de sourcing + 1 lacuna complementar (railing kit para bloquear ring-out nas arenas 1-2).
- `doc/contracts/object_role_map.json` — 25 objetos com função declarada no vocabulário canônico (cover/hazard/lane_guide/silhouette_landmark/occlusion_foreground/parallax_depth/ecology_loop/breakable_candidate/purely_decorative), plano (BG_A/BG_B/foreground/sprite) e classe de budget.
- `doc/contracts/object_placement_map.json` — autoria de level design: bandas de y (dressing 64-144, luta 144-208, beirada 208-224), script de câmera com 3 wave-locks (x=160/560/960), política de ring-out por trechos (exposto 480-560 ensaio + 960-1280 payoff; bloqueado por railing/barco/net wall no resto; grade quebrada em x=944 anuncia a regra), placements por fase, foreground nas bordas, costuras de variação (x=352/704/1056) e variação temporal.
- `doc/contracts/parallax_layer_contract.json` — BG_B residente 512px com 4 bandas line-scroll (0.125/0.25/0.375/0.5), guindaste fora da costura do loop (448-512 só céu/mar), far_boat_drift via hscroll (zero tiles), regra de contraste BG_B < sprites.
- `doc/contracts/background_ecology_card.json` — 7 loops com função e prioridade de corte: foam=NUNCA cortar (sinal de ring-out), net/cloth=primeiros cortes, gulls=sprites em disputa de budget (dispersam no splash — ecologia ligada a gameplay); teto alvo 98 patterns de animação a provar no laudo.
- `doc/art/world_layout_board_1344x224.png` — board visual revisável: fases calm/pressure/payoff, locks com extensão de viewport, beirada exposta vs bloqueada, landmarks, golden path (ARCH→crane→BOAT→BOOTH→NET WALL→grade quebrada→FAROLETE), régua de colunas de streaming e legenda. NÃO é arte final; é o plano de montagem.

*Status honesto:* `object_role_map_missing` e `world_layout_board_missing` LIMPOS; permanecem `dock_scene_kit_missing` (nenhum board modular gerado), `level_art_assembly_not_built` (montagem real só após kit + conversão), `budget_not_measured`, `blastem_evidence_missing`. Tudo `documentado`; nada implementado/buildado/testado_em_emulador/validado_budget.

- Parecer humano aceito: a rota anterior ainda tratava o CAIS como panoramas/painéis prontos demais, delegando criatividade de level design e montagem visual ao modelo de imagem.
- Novo contrato: `doc/contracts/level_art_assembly_contract.json` define ownership correto: modelo de imagem gera `scene_kit`; agente canônico monta o level com `level_blueprint`, câmera, streaming, parallax, foreground, ecology loops e gameplay anchors.
- `doc/art/art_generation_brief.md` atualizado para v3: Etapa A0 obrigatória (`level_art_assembly_contract`) antes de nova geração do cais; painéis existentes reclassificados como `mood_reference_only` / `landmark_reference_only`.
- `doc/art/prompt_pack/03_cais_world_concept.md` substituído por prompts de kit modular: floor/edge tiles, props/obstructions, landmarks, BG_B parallax, foreground/occlusion e background ecology loops.
- Status dos painéis atuais do cais: servem para paleta, atmosfera e alguns landmarks, mas NÃO autorizam tilemap final, streaming world source, `res/` ou `ready_for_aaa`.
- Novo blocker dominante para o CAIS: `level_art_assembly_not_built` / `dock_scene_kit_missing` / `world_layout_board_missing`.

**2026-07-03 (sessão 4) — Concepts recebidos, prova VDP e aprendizados registrados**

- Humano gerou 15 concepts via prompt pack (TAÍNA turnaround+9 poses+retrato, CRIA, ESTIVADOR, 3 arenas do cais, BG loop, HUD, FX, logo escolhido + estudos). Nomes normalizados (portable_descriptive_v1; CRIA estava na pasta errada) e todos registrados como `source_candidate` no premium_source_manifest.
- Prova de sobrevivência VDP construída (320x224 + 15 cores + snap 9-bit): CENÁRIOS/BG/LOGO SOBREVIVEM com leitura excelente; PERSONAGENS viram borrão no downscale direto — confirma objetivamente a rota autoral pixel (3.5 heads) exigida pelo parecer.
- Desvios registrados: proporção realista dos sheets (identidade ok, compressão devida) e texto diegético emergente no cenário (aceito como narrativa; tratar em tiles).
- 7 lições gravadas em `doc/agent_learning/learning_ledger.json` (6 candidatas canônicas: prompt pack como artefato, proporção ignorada por modelos, texto diegético, contact sheet VDP como gate, incompatibilidades pwsh/Linux, falso verde de contrato) + patterns + candidates para o estudo canônico posterior.
- Gate de arte atualizado: ratificação humana PENDENTE com evidência pronta; próximos blockers: `no_pixel_model_sheet`.

**2026-07-03 (sessão 3) — Resposta ao parecer curatorial**

- Status renomeado honestamente: pré-produção documentada com template técnico; nenhuma comparação com jogos reais do MD é cabível ainda.
- `doc/contracts/slice_scope_contract.json`: mata o falso verde — contrato de gênero descreve o JOGO; o slice é 1P, cap 4 inimigos, sem grab do herói, sem super bar, sem boss.
- `doc/contracts/tilemap_streaming_contract.json`: cais 1344px sai de scene_local_preload para streaming por colunas (janela 64x32, máx 2 colunas/frame, seam policy, fallbacks). Veredito VDP: não medido, contrato fechado; alvo "cabe com recuo".
- Direção de arte: trio de prova MD-nativo (SOR2, Shinobi III, Comix Zone) adicionado; `human_ratification: pending` — nada converte para res/ sem sua aprovação com contact sheet 320x224; fallback declarado (vibrant_16bit_pixel) se a linguagem não sobreviver ao VDP.
- Rota de arte corrigida: IA somente para concept (gate proíbe animated_sprite_final); `doc/art/prompt_pack/` criado com 6 documentos de prompts específicos para o humano gerar; depois model sheet autoral → lineart 1px → key poses → strips.
- `art_gameplay_direction_gate.json` preenchido: produção autorizada SÓ para Etapa A (concepts).
- TDD: áudio corrigido (XGM2 dono de FM+PSG; SFX via PCM do driver; proibido acesso direto), streamer de colunas adicionado ao ownership de DMA, riscos r5 (violação de ownership no branding herdado, high) e r6 (costura de streaming) registrados.
- Dívida de código declarada: scene_branding.c escreve CRAM/HScroll(CPU) no update e toca PSG com XGM2 carregado — refatorar antes do runtime.
- build.bat/rebuild/clean/run/resolve_wrapper locais corrigidos (profundidade de delegação de três para dois níveis; apontavam para fora do workspace).
- Metadados herdados build_v001/v002 removidos de doc/changelog/roms/ (eram do template, anteriores ao nascimento).
- 4 problemas de framework canônico encaminhados como tarefa separada (ready_for_aaa em planejamento, mistura source/res no diagnóstico, higiene vs texto histórico, visual gate procurado em out/logs).

**2026-07-03 (sessão 2) — FASES 2 e 3 completas, tudo validado**

- Cadeia de contratos emitida e 100% verde: TDD + brawler design + mechanic + level + enemy + frame data (auditoria passed, validador de especialização 11/0, schemas via jsonschema).
- Direção de arte congelada em `angular_cps2_fighter` (confiança 0.70 > limiar 0.65) com manifesto de estilo, moodboard, brand identity (planned) e política de drift.
- 16 PRDs materializados; PRD readiness ok. Higiene e metodologia corrigidas e passed.
- Canal de geração de imagem reclassificado: native-first. Em superfície Codex/ChatGPT
  capaz, usar geração nativa; Bonsai/ComfyUI ficam como fallback local, não como
  blocker de concept art.
- Fix canônico correlato em `tools/sgdk_wrapper/validate_brawler_belt_scroll_specialization.ps1` (pwsh 7.5+: OrderedDictionary + DateKind), CI 23/23.

**2026-07-03 — Nascimento do projeto + FASE 1 (sessão Linux)**

- Ambiente do agente validado no host Linux (`agent_environment_status=ready`, Graphify pulado por bug conhecido de dot-dirs).
- Loop build→emulador provado no host com SMOKE_TEST antes de abrir produção (out/rom.bin 262144 bytes + BlastEm 59.8 fps + SRAM heartbeat).
- Usuário escolheu no menu de sessão: criar novo jogo, especialização `brawler_belt_scroll`.
- Projeto criado via `new_project.sh` com nome canônico validado.
- Contexto classificado e validado (`aaa_game`, blockers=0). Opt-in de gênero registrado.
- GDD completo escrito: MARÉ BRAVA — belt scroller brasileiro (Porto Bravo, TAÍNA, Sindicato da Maré), pilar assinatura "Empurrão de Maré" (ring-out costeiro), técnicas `line_scrolling` + `camera_scroll_management` + `hitstop_camera_shake_feedback` (aptas no registry); `palette_cycling`/`shadow_highlight_mode` adiadas por status `LABORATORIO`.
- First playable slice congelado: CAIS_01 (1 heroína, 2 arquétipos, 1 onda/3 grupos, ring-out, pickup, HUD WINDOW, FSM completo, XGM2).
- Memory bank e changelog herdados do template foram corrigidos para a verdade do projeto (template trazia histórico de builds inexistentes aqui).

---

## 3. DECISOES PENDENTES

- RATIFICAR DIREÇÃO DE ARTE (humano): a ratificação agora é parcial. Logo/BG/mood podem ser ratificados como direção; painéis do cais ficam `mood_reference_only` até existir `dock_scene_kit` modular e `world_layout_board` montado pelo agente.
- Montar o CAIS_01 com autoria de level design: gerar/curar `dock_scene_kit`, emitir `dock_scene_kit_inventory`, `object_role_map`, `world_layout_board`, `object_placement_map`, `parallax_layer_contract` e `background_ecology_card`.
- Escolher quem faz o model sheet pixel autoral (humano no Aseprite/GraphicsGale ou agente via ferramenta de pixel) — próximo passo físico da arte.
- Aprovação humana dos premium sources quando gerados (gate obrigatório antes de conversão VDP).
- Art pass da branding com identidade MARÉ BRAVA (direção de arte agora existe).
- Nome/arte final do segundo herói JACO (capoeirista) — `entra_depois`.
- Reclassificar claim `critical_motion` para `required` quando strips de combate entrarem em produção com evidência.

---

## 4. DECISION LOG CONSERVADOR

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia | Proximo gate |
|------|----------|---------|------------------------|-----------|--------------|
| 2026-07-03 | Host de producao | Provar loop build→BlastEm no Linux ANTES de abrir projeto novo | Criar projeto e descobrir toolchain quebrada depois | SMOKE_TEST rom.bin + screenshots BlastEm (scratchpad da sessão) | primeiro build do MARE_BRAVA |
| 2026-07-03 | Genero | `brawler_belt_scroll` com opt-in humano explicito | Inferir genero sem consentimento (viola AGENTS.md) | `doc/genre_specialization_manifest.json` | brawler design contract |
| 2026-07-03 | Tecnicas | Somente registry status apto no slice; `LABORATORIO` adiadas | Prometer palette cycling/shadow highlight sem promocao | tabela de tecnicas no GDD | laudo VDP budget |
| 2026-07-03 | Verdade do template | Corrigir memory bank/changelog herdados com historico falso | Manter claims de build_v002 inexistente | este arquivo | primeiro build regenera bloco derivado |

---

## 5. ROTEIRO DE FECHAMENTO

- build/rebuild canonico: `build_v001` gerado via overlay temporário `/tmp/sgdk_win_overlay` usando SDK canônico `sdk/sgdk-2.11`; ROM snapshotada.
- contratos recompilados: `out/logs/scene_contract_compile_report.json` presente; 4 cenas compiladas, lint interno não executado (`lint_status=error`), então não fechar como gate limpo.
- grafo de recursos: `out/logs/res_graph_report.json` presente; 10 declarações ok, 0 issues, 5 imagens/5 áudios; budget VDP ainda não medido (`vram_residency_status=not_measured`) e tile stats falharam no host Linux.
- validator: `validate_resources.ps1` concluído com 0 erros/8 warnings; blockers atuais: `visual_gate_blocked`, `visual_direction_failed`, `animation_gate_failed`, `scene_tilemap_conversion_report_missing`, `per_tile_palette_conflict_report_missing`, `freshness_audit_stale`, `scene_closeout_gate_missing`.
- captura BlastEm: boot/menu observado e selado por screenshot manual fallback; `evidence_closeout_report.json` status `ok/sealed`; sem SRAM/VDP dump.
- regressao de cena: ausente/nao executada.
- freshness audit: warning com `stale_count=0`; falta apenas `build_output.log` como artefato obrigatório de freshness. Não reconstruir só para gerar log sem necessidade, pois rebuild pós-captura mudaria o contrato de evidência.
- closeout gate: ausente; nao declarar cena fechada.

---

## 6. REFERENCIAS RAPIDAS

- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- Brief: `doc/00-project-brief.md`
- Roteiro: `doc/12-roteiro.md`
- Contexto: `doc/project_context_manifest.json`
- Genero: `doc/genre_specialization_manifest.json`
- Diretrizes agente: `doc/00-diretrizes-agente.md`
- Plano de provas QA: `doc/14-plano-de-provas-qa.md`

---

## 7. ATUALIZACAO 2026-07-08 — TAÍNA animation planning + v07 scale probe

- Criados contratos de animação para a TAÍNA em `doc/art/characters/taina/animation/`: `animation_state_plan_v01.json`, `frame_budget_table_v01.json`, `pivot_and_scale_contract_v01.json`, `motion_phase_map_p0_v01.json`, `animation_direction_contract_v01.json` e `animation_planning_gate_report_v01.json`.
- Os contratos fixam célula 48x64, pivot bottom-center, alvo de 48px visíveis, P0 de estados de brawler, timing em VBlanks e regra de não assar FX na sheet do corpo. Status honesto: planejamento declarado, não evidência de animação.
- Gerados probes técnicos TAÍNA v06/v07; v07 é PNG indexado `P`, 192x64, índices `[0,1]`, index 0 magenta, cor visível na grade 9-bit, SHA-256 `b8342103628317977961f3e9ae764cd4c43b04280c66594ac601906faed2c6d1`.
- Relatório `doc/art/characters/taina/model_sheet_to_sprite_fidelity_report_v07.json`: v07 reduz drift de escala (v05 ~61–62px visíveis; v07 52px), mas regride identidade/hair/face e continua `visual_pass=false`. Uso permitido apenas como evidência negativa/scale probe.
- Atualizados `native_grid_translation_report_v01.json`, `lineart_blocking_report_v01.json`, `visual_dna_manifest.json` e `out/logs/visual_delivery_gate_report.json`. Nenhum asset foi promovido para `res/`; sem key poses, sem contact sheet, sem pivot overlay, sem foot contact/frame delta e sem BlastEm de animação.

## 8. ATUALIZACAO 2026-07-09 — TAÍNA native image source candidates

- Retomada a rota correta de geração visual pela capacidade nativa `native_chat_image_generation_callable`, conforme `doc/art/prompt_pack/06_image_agent_master_prompt.md` e `out/logs/generation_channel_decision.json`.
- Geradas 4 variações de `taina_identity_turnaround`; aceitas 2 como `source_candidate`: `data/source_art/concept/taina_identity_turnaround/taina_identity_turnaround_v01.png` (SHA-256 `d8e7036c8d79aa6cd03e8309ec883e287b27ca2986f8cad27f844cdf6b67710a`) e `taina_identity_turnaround_v02.png` (SHA-256 `715ebf7c75679391e6ccc31e9a2383a64b6029089d8fd079cf16bec177ef88ba`).
- Duas variações foram arquivadas em `data/source_art/concept/taina_identity_turnaround/descartes/` por drift de anatomia alta/ilustrativa.
- Criados `doc/art/characters/taina/taina_identity_turnaround_native_callable_review_v01.json`, prompt log em `doc/art/generated_prompts/taina_identity_turnaround/taina_identity_turnaround_native_callable_v01.md` e contact sheets `doc/art/characters/taina/review/taina_identity_turnaround_native_callable_contact_sheet_320x224_v01.png` / `_16c_v01.png`.
- Resultado honesto: a identidade fonte melhorou e sobrevive melhor à miniatura 320x224/16c, mas continua concept source. Próximo passo real: model sheet pixel 3.5 heads e lineart 1px a partir desse source; sem `res/`, sem build novo, sem ROM nova e sem evidência BlastEm nova.

## 9. ATUALIZACAO 2026-07-28 — parecer historico de direcao de arte

- Adicionado `doc/21-relatorio-direcao-de-arte-ver-001.md`: auditoria documental e visual do fluxo de criacao de assets ate 2026-07-09.
- O parecer separa a heranca de template de 2026-06-03 da producao de MARE BRAVA e consolida o inventario atual: 19 `source_candidate`, 4 referencias de mood/landmark, provas offline e linearts TAINA nao promovidos.
- Nenhum asset, manifest, recurso SGDK, ROM, budget ou status tecnico foi alterado por este parecer. O estado operacional permanece `technical_artifact_only` / `emulator_observed_budget_pending`, com o bloqueio visual vigente.

## 10. ATUALIZACAO 2026-07-28 — linha do tempo visual

- Adicionado `doc/22-linha-do-tempo-visual-ver-001.md`, com as imagens reais que marcam concept, prova VDP, montagem modular do CAIS_01, lote autoral e revisoes v04–v07/native source da TAINA.
- O documento e somente um apendice de leitura historica: nao promove nenhum concept, lineart ou branding herdado a arte final e nao muda o estado operacional.

## 11. ATUALIZACAO 2026-07-28 — protocolo local contra degradacao de iteracao visual

- Criado `doc/art/characters/taina/iteration_control_protocol.md`. O protocolo consolida os contratos ja existentes em uma rotina obrigatoria para o proximo candidato da TAÍNA: fonte autoral como incumbente, lista `must_preserve`, uma correcao por vez e comparacao em escala nativa antes de aceitar qualquer ganho tecnico.
- A licao local L10 foi registrada em `doc/agent_learning/failure_patterns.md`; o ledger nao foi editado manualmente porque e derivado dos markdowns.
- Consequencia de direcao: uma versao com grid, escala ou PNG melhores, mas que perca cabelo, face, assimetria, materiais ou guarda, recebe `cohesion_drift` e continua evidencia negativa. Nenhum asset, `res/`, ROM, budget ou status de entrega foi alterado.
- Selecao humana complementar: a imagem 04 da linha do tempo (`authorial_style_validation_contact_sheet_v01.png`) e a baseline de direcao; as imagens 05/06, de revisoes posteriores da TAÍNA, sao retrocessos e ficam restritas a comparacao/evidencia negativa.

## 12. ATUALIZACAO 2026-07-28 — linhagem visual travada para a proxima producao da TAÍNA

- Criado `doc/contracts/visual_source_of_truth_taina_v01.json`, validando a imagem 04 como baseline humana de direcao e a fonte individual autoral da TAÍNA como origem permitida para a proxima lineart.
- Os candidatos v05, v06 e v07 foram travados como `obsolete_for_generation_source`: so podem aparecer como evidencia negativa/comparacao, nunca como `source`, `baseline`, `reference_for_generation`, `img2img_base`, `generation_source` ou `image_reference`.
- Proxima etapa autorizada: nova `lineart_blocking_1px` que parte da fonte autoral, do DNA visual e do gate arte+gameplay; continua sem color blocking, sprite final, `res/`, ROM, budget ou promocao de status.
- Cartao de autoria criado: `doc/art/characters/taina/taina_lineart_v08_authoring_card.md` fecha o entregavel, a escala, o pivot, os marcadores a preservar e os criterios de reprovacao da v08. A producao fisica da prancha ainda e pendente; o cartao nao e asset.
- Persona de producao ativada: `art-director`, com `doc/art/characters/taina/taina_v08_visual_breakdown.md` como breakdown de linha, leitura, materiais, herancas tecnicas e veto contra arte generica. Nenhuma promocao visual foi liberada.
- Rascunho de direcao v08 gerado em `rascunho/taina_lineart_v08/taina_lineart_v08_directional_draft_v01.png` e revisado em `doc/art/characters/taina/taina_lineart_v08_directional_draft_review_v01.json`. Ele preserva a identidade da imagem 04, mas esta fora do grid/celula nativos e fica `directional_review_only`, sem uso como fonte, sprite, `res/` ou runtime.

## 13. ATUALIZACAO 2026-07-28 — primeiro ciclo idle direcional da TAÍNA

- Aprovacao humana recebida para iniciar sprites pelo fluxo de strip e animacao. O primeiro recorte e somente `idle_guard`, com seis celulas previstas de 48×64 px, pivot `(24,60)` e `ground_y=60`; contrato em `doc/art/characters/taina/animation/taina_idle_guard_strip_v01.json`.
- Gerada a prancha direcional `rascunho/taina_idle_guard_v01/taina_idle_guard_directional_draft_v01.png` e registrado o parecer em `doc/art/characters/taina/animation/taina_idle_guard_directional_draft_review_v01.json`.
- Diagnostico honesto: a prancha preserva cabelo, rosto, guarda e assimetria melhor que v05-v07, mas e RGB 2172×724, tem traco editorial e ainda nao mede pivot, pe, delta ou paleta. Portanto e guia de redesenho, nao sprite nativo, `data/`, `res/` ou evidencia runtime.
- Proximo gate: redesenhar as seis celulas na grade nativa, medir contato/pivot, validar index 0/paleta/tiles, gerar preview e somente entao submeter ao parecer de arte. Nenhuma ROM, budget ou estado tecnico foi promovido.

## 14. ATUALIZACAO 2026-07-28 — strip nativa idle_guard em staging de `res`

- Produzida `data/processed/characters/taina/animation/taina_idle_guard_native_48x64_v01.png`: strip horizontal de seis celulas 48×64, PNG indexado, 14 indices usados, indice 0 reservado e paleta ajustada a passos 9-bit. A mesma copia esta em `res/sprites/characters/taina/taina_idle_guard_48x64_v01.png` e declarada como `spr_taina_idle_guard` em `res/resources.res`.
- A integridade medida passou: bbox de 48 px de altura, top y=11, pe y=58, sem clipping, matte, ilhas externas ou FX embutido. Preview e reports em `doc/art/characters/taina/review/` e `doc/art/characters/taina/animation/`.
- Limite honesto: a declaracao nao foi compilada pelo ResComp porque o host atual nao tem Java; tambem nao ha ROM/emulador com o sprite. Status e `res_candidate_waiting_for_rescomp`, nao `testado_em_emulador`.

## 15. ATUALIZACAO 2026-07-29 — preparacao recuperavel do host Linux

- O ambiente efemero da sessao perdeu `pwsh`, Java e Wine apesar de a receita anterior estar documentada. Em 2026-07-29, com autorizacao humana, foram instalados pelo host Manjaro via `bigsudo pacman -S --needed --noconfirm powershell-bin jre17-openjdk wine`.
- Receita operacional: apos a instalacao, renovar o ambiente (`source /etc/profile` ou novo shell), executar `tools/sgdk_wrapper/assert_agent_environment.ps1`, `preflight_host.ps1` e recriar o overlay `/tmp/sgdk_win_overlay` antes do build. O Wine registra binfmt via hook; se executaveis `.exe` nao abrirem, usar `bigsudo systemctl restart systemd-binfmt` e revalidar.
- Esta atualizacao prepara o host; nao promove ROM, emulador, budget ou estado de entrega por si so.

## 16. ATUALIZACAO 2026-07-29 — ResComp da strip passou; link da ROM bloqueado por LTO do SDK

- `assert_agent_environment.ps1 -SkipGraphify` retornou `agent_environment_status=ready` e `preflight_host.ps1` reencontrou GDK, make, Java, Python e ImageMagick.
- A declaracao correta da strip e `SPRITE spr_taina_idle_guard ... 6 8 FAST 6`: ResComp interpreta largura/altura em **tiles**, portanto 6×8 = 48×64 px. Ele compilou os seis frames, cada um com 2 sprites VDP e 24 tiles; `res/resources.rs` foi regenerado com sucesso.
- O build pelo overlay recompilou fontes e recursos, mas o link falhou de modo deterministico: `sdk/sgdk-2.11/lib/libmd.a` carrega bytecode LTO 16, enquanto `sdk/sgdk-2.11/bin/gcc.exe` espera LTO 13. Nao existe `m68k-elf-gcc` alternativo neste host para casar com a biblioteca.
- Dependencias `.d` e objetos `.o` herdados foram movidos, de forma recuperavel, para `out/dependency_backup_20260729_host_recovery/` e `out/object_backup_20260729_host_recovery/`; a nova compilacao confirmou que o blocker nao era cache do projeto.
- Estado real: o sprite esta `rescomp_compiled`, mas a ROM nova continua bloqueada por `sdk_lto_version_mismatch`; nao ha prova em emulador para esta versao.

## 17. ATUALIZACAO 2026-07-29 — rota Linux isolada fecha o build; emulador continua pendente

- O parecer da seção 16 descreve corretamente a falha da tentativa direta, mas
  o blocker foi superado por uma rota específica de host, sem alterar o código
  do jogo nem a biblioteca canônica de origem.
- `tools/sgdk_wrapper/select_sgdk_build_route.py` provou: host `linux`;
  `gcc.exe` 13.2.0; `libmd.a` de origem com LTO 16.1.0 incompatível para link
  direto; biblioteca staged produzida por GCC 13.2.0, sem LTO e compatível.
- A rota selecionada foi
  `tools/sgdk_wrapper/build_sgdk_wine_bridge.sh --project-root <projeto>`.
  ResComp, fontes C e link terminaram com exit code 0.
- A blindagem foi acoplada às entradas reais: a bridge Linux chama o seletor
  antes de preparar o staging; o `build.bat` Windows chama o preflight de rota
  depois de resolver o ambiente e antes de entrar no make.
- ROM atual: 262144 bytes, SHA-256
  `8ed8f28bde41cc4987718079f7584c6d90cbe1cad22a73f1b953857b367a434d`.
  Evidências:
  `out/logs/linux_wine_build_report.json` e
  `out/logs/sgdk_build_route_report.json`.
- Regra permanente: em Linux, usar staging + bridge e preservar o SDK de
  origem; em Windows, usar o wrapper batch e bloquear se compilador/biblioteca
  LTO não forem coerentes. ResComp/C verdes seguidos de erro no link são
  incidente de toolchain até prova contrária, não autorização para editar
  assets ou runtime.
- Limite honesto: a ROM atual ainda não foi observada no BlastEm. A prova
  histórica da ROM `5c1489...e75` não transfere para `8ed8...434d`; status
  máximo atual é `buildado_emulator_pending`.

## 18. ATUALIZACAO 2026-07-29 — TAÍNA v01 observada no runtime e reprovada visualmente

- A strip `spr_taina_idle_guard` foi integrada a `scene_demo.c` e a cena recebeu
  injeção QA de boot por bloco assinado `SBIS` em SRAM. A rota normal de boot
  continua inalterada; a injeção existe somente para captura determinística.
- Build pela bridge Linux passou. ROM: 262144 bytes, SHA-256
  `3c4c6c5d4294a9f0042e1bbfdd1e66b7f2b2b3eca167489f23b54d2add99eb44`.
- A cena 3 foi vista no BlastEm. Evidência parcial:
  `out/blastem_env_taina_idle_guard_v01/blastem-linux-20260729T090809Z-192035/`,
  contendo screenshot, GIF, 12 frames, SRAM e métricas. O sprite apareceu e a
  animação executou; a captura não fechou o seal canônico porque faltam bloco
  VLAB e dump VDP.
- Parecer de arte: `technical_runtime_pass_visual_fail`. A v01 perdeu massa e
  ganchos do cabelo, face/expressão, proporção heroica, assimetria material e
  gesto de guarda da imagem 04. Ela permanece evidência técnica/negativa e foi
  travada como fonte obsoleta para novas gerações.
- Estado correto: `buildado` com observação parcial no BlastEm; não
  `testado_em_emulador`, não aprovado visualmente, não AAA e não validado em
  budget.

## 19. ATUALIZACAO 2026-07-29 — reconstrução autoral v02 e regra de pose-mestre

- Uma nova prancha foi gerada usando exclusivamente
  `taina_identity_turnaround_authorial_v01.png`, correspondente à imagem 04.
  A autoria visual voltou a aparecer: corpo alto/atlético, cabelo dominante,
  face angular, guarda elevada, top laranja, wraps/faixa teal e calça índigo.
- A prancha `rascunho/taina_idle_guard_v02/taina_idle_guard_authorial_study_v02.png`
  é RGB 2172×724 com 160957 cores e antialiasing; portanto é guia direcional,
  não asset nativo.
- Um proxy 288×64/14 cores foi produzido somente para diagnóstico. O primeiro
  quadro preserva identidade suficiente para virar incumbente de redesenho
  (`taina_idle_guard_key_pose_v02.png`, 48×64, ground y=60), mas ainda exige
  limpeza manual de face, cabelo, mãos e diagonal da guarda.
- O strip gerado foi reprovado: o eixo horizontal deriva 7 px, a bbox varia
  3 px e cabeça/corpo são redesenhados entre frames. Isso é morphing, não
  animação.
- Regra local permanente: aprovar uma pose-mestre nativa e derivar todos os
  frames por edição pixel controlada. É proibido gerar seis poses independentes
  e usar semelhança geral como continuidade. Relatório:
  `doc/art/characters/taina/animation/taina_idle_guard_v02_authorial_reconstruction_report.json`.
- Nenhum arquivo em `data/processed`, `res/` ou recurso SGDK foi substituído
  pela v02; build e evidência runtime continuam referentes à v01 reprovada.

## 20. ATUALIZACAO 2026-07-29 — idle_guard v02 promovida, buildada e observada no BlastEm

- O diretor de arte humano aprovou o resultado visual v02 e autorizou a
  continuidade. A pose-mestre limpa 48×64 foi fixada como incumbente; v01,
  proxy v02 com morphing e linearts v05-v07 continuam proibidos como fontes.
- Os cinco quadros derivados foram produzidos por edição de clusters sobre a
  mesma topologia: contorno, guarda, mãos, pés, pivot e bbox permaneceram
  fixos. O ciclo usa holds NTSC `[11,7,10,7,11,12]`; torso, cabelo e faixa
  respondem em fases diferentes.
- Strip promovida:
  `res/sprites/characters/taina/taina_idle_guard_48x64_v02.png`, SHA-256
  `5d17c164815eecf821cdd83dd45125fa0c57601facc7566307bc3c1cf6a58cde`.
  PNG indexado 4-bit, 16 entradas de paleta, 11 índices usados, 10 cores
  visíveis, grade de cor 9-bit e seis células 48×64.
- ResComp mediu 2 partes de metasprite e 24 tiles únicos por quadro. O ciclo
  completo contém 40 tiles únicos/1280 bytes. A ROM foi buildada pela bridge
  Linux: 262144 bytes, SHA-256
  `e6b84c604a2dd26662e2e4603ff79a276351cb77447bb9e8d4874a2c6ffaab15`.
- BlastEm abriu a cena 3 a 60.2 fps no snapshot da janela. A captura parcial
  registrou 151 frames, 32 amostras, 0 frames acima do budget, CPU máximo 28%,
  p95 27% e pressão máxima observada de 1 sprite por scanline.
- Parecer: `technical_runtime_pass_visual_direction_pass_partial_evidence`.
  A silhueta, identidade e materiais sobrevivem em 320×224 e o ciclo não
  apresenta morphing. O bundle não foi selado por falta de VLAB e
  `visual_vdp_dump.bin`; portanto o projeto continua `buildado` com observação
  parcial, não `testado_em_emulador` e não AAA.
- Aprendizado L13: uma pose-mestre aprovada e edição localizada de clusters
  preservam autoria; gerar quadros independentes não é uma rota aceita.
- Os contratos ativos de planejamento e budget foram sincronizados com a
  escala humana aprovada de 59 px, a strip v02 e seus holds. A referência
  antiga à v05/escala de 48 px foi removida da rota ativa para impedir
  regressão por um agente futuro.
**2026-07-04 (sessão 7) — Contrato de traço autoral e lote visual de validação**

- Parecer humano aplicado: `angular_cps2_fighter` era um rótulo amplo demais e permitia arte tecnicamente competente, porém genérica e intercambiável.
- Criado `doc/art/authorial_line_style_contract.json` com assinatura de contorno/sombra/gesto, gramática de rosto/mãos, hooks de silhueta por personagem, assimetria de figurino, marcas de material e blockers explícitos.
- Framework canônico endurecido em `art_style_catalog.json`, `SGDK_GLOBAL.md`, `art-creator.md`, `art-director.md` e documentos de qualidade visual; ausência do contrato agora bloqueia claims AAA/estáveis.
- Prompts 00-06 revisados para transportar a gramática autoral, não apenas referências ou adjetivos de estilo.
- Geradas 7 imagens: 6 candidatas autorais e 1 descarte auditável por texto indevido. Manifesto/hashes: `data/source_art/concept/authorial_style_validation_2026_07_04/generation_batch_manifest.json`.
- Contact sheet: `data/processed/contact_sheets/authorial_style_validation_contact_sheet_v01.png`.
- Status honesto: lote `source_candidate` aguardando ratificação humana; continuam bloqueados `no_pixel_model_sheet`, `dock_scene_kit_not_decomposed`, `budget_not_measured` e `blastem_evidence_missing`.

**2026-07-08 — TAÍNA lineart 48x64: v03/v04 registrados como falha visual rastreável**

- Produzidos candidatos técnicos `taina_lineart_clean_native_48x64_candidate_v03.png` e `v04.png` em `data/processed/characters/taina/lineart/`; ambos são PNG `P`, 192x64, índices `[0,1]`, índice 0 magenta de pipeline e cor visível na grade 9-bit.
- Criados `model_sheet_to_sprite_fidelity_report_v03.json` e `model_sheet_to_sprite_fidelity_report_v04.json`; decisão conservadora: ambos `rejected_as_clean_native_source`, uso permitido apenas como evidência negativa/referência de grid.
- Atualizados `lineart_blocking_report_v01.json`, `native_grid_translation_report_v01.json` e `visual_dna_manifest.json` para blocker atual `model_sheet_to_sprite_fidelity_failed_v04`.
- Diagnóstico de arte global rodado em `out/logs/art_asset_diagnostic_report.json`: 44 assets analisados, 15 ok, 29 precisam conversão; os linearts TAÍNA v01-v04 aparecem tecnicamente ok, mas a promoção visual segue bloqueada.
- Status honesto: sem color blocking, sem key poses, sem promoção para `res/`, sem build/ROM/emulador. Próxima rota: modelo/sheet nativo hand-authored ou tracing supervisionado do source aprovado, travando primeiro cabeça, hair hooks, face wedge e guarda diagonal.

**2026-07-08 — Build técnico v001 gerado; entrega segue bloqueada por visual/emulador**

- Preflight passou com variáveis temporárias Linux (`USERPROFILE`, `LOCALAPPDATA`, `ProgramFiles`) para contornar suposições Windows do checker; GDK canônico local, `make`, Java, Python e ImageMagick encontrados.
- Build Linux direto falhou primeiro por caminho com espaço no GDK e depois por mismatch `m68k-elf-gcc` 16.1.0 vs `libmd.a` LTO 13.0.
- Rota de smoke técnico bem-sucedida: overlay temporário `/tmp/sgdk_win_overlay` com symlinks para os binários Windows do `sdk/sgdk-2.11`, executados via Wine/binfmt; `make` terminou com código 0.
- ROM gerada e snapshotada em `doc/changelog/roms/build_v001/rom.bin`: 262144 bytes, SHA-256 `5c1489fa944be7f62a06192beef4c783c3f0f2d2939b59d08958b996b0131e75`; metadata em `doc/changelog/roms/build_v001/build_meta.json`.
- `validate_resources.ps1` reconheceu a ROM, mas fechou com 1 erro/7 warnings: `visual_gate_blocked`, `visual_delivery_gate_missing`, `res_graph_missing_for_visual_delivery`, `scene_tilemap_conversion_report_missing`, `per_tile_palette_conflict_report_missing`, `freshness_audit_stale`, `scene_closeout_gate_missing`.
- Status honesto: `buildado`/smoke técnico. Ainda não é `testado_em_emulador`, não tem BlastEm, não tem gameplay/performance/audio provados e não remove o bloqueio visual da TAÍNA.

## 21. ATUALIZACAO 2026-07-29 — direção do primeiro jab aberta sob gate de pose-chave

- A próxima ação foi separada corretamente como `combo_hit_1_jab`; o rótulo
  antigo `light_jab_cross` continua apenas como agrupamento de planejamento.
  O GDD permanece soberano: combo `jab -> cross -> low_kick`, com cada golpe
  tendo asset e janela de cancelamento próprios.
- Foi gerada uma única pose direcional de contato ativo usando somente a fonte
  autoral e a pose-mestre idle v02:
  `rascunho/taina_light_jab_cross_v01/taina_light_jab_active_directional_study_v01.png`,
  SHA-256
  `8b3c1a73623c7e279141c67fbe410ac6296d3b8b97ca53b7d08f9d8d626cac48`.
- Parecer: identidade, topologia, linha de ataque, guarda traseira, olhos e
  apoio dos pés passam como direção. A imagem é RGB 1024×1536, possui
  antialiasing e fundo cinza variável; fica `directional_review_only`.
- O envelope proposto para a ação é 64×64, pivot `(24,60)` e altura visível
  fixa de 59 px. A largura extra preserva o alcance do punho sem encolher a
  personagem para caber na célula idle 48×64.
- Contrato de produção:
  `doc/art/characters/taina/animation/taina_combo_hit_1_jab_production_contract_v01.json`.
  Ele fixa cinco fases `[3,2,2,3,4]`, frame ativo 2, hitstop de 2 frames,
  hitbox seed 24×16 na ponta do punho e proíbe geração independente dos
  quadros.
- Estado real: nenhuma lineart nativa, strip, `/data/processed`, `/res`, build
  ou ROM nova foi produzida nesta etapa. O próximo gate é aprovação humana da
  direção ativa, seguida de redesenho 1 px nativo.

## 22. ATUALIZACAO 2026-07-29 — primeira pose pixel nativa do jab em revisão

- O diretor de arte humano aprovou a direção da pose ativa com `Prossiga`.
  Essa aprovação cobre a direção high-res, não a nova candidata pixel.
- Um builder reprodutível foi criado em
  `tools/art/build_taina_combo_hit_1_jab_key_pose_v01.py`. A rota preserva a
  cabeça, a paleta, a escala de 59 px e a base corporal da idle v02; não usa
  v01, proxy v02 ou linearts v05-v07.
- Candidata nativa:
  `rascunho/taina_combo_hit_1_jab_v01/taina_combo_hit_1_jab_active_key_pose_64x64_v01.png`,
  SHA-256
  `a468a9099bb88264f58f4e0d54c959cbaa3929017166ad2cc695dcc0597a6ff6`.
- Medições: 64×64, PNG P 4-bit, 10 cores visíveis, bbox `[15,2,59,60]`,
  altura visível 59 px, uma ilha conectada, pivot `(24,60)`, sem clipping,
  AA, alpha parcial ou FX assado.
- O primeiro ensaio interno do builder foi descartado antes do gate porque
  ampliava demais o punho e blocava o tronco. Aprendizado aplicado: numa ação
  nova, preservar a maior quantidade possível da topologia humana aprovada e
  limitar alterações aos clusters cinéticos necessários.
- Estado real:
  `technical_pass_human_visual_review_pending`. O alcance lê em 320×224, mas
  escala do punho e posição da guarda traseira aguardam parecer humano. Os
  outros quatro frames, strip, `/res`, build e ROM continuam bloqueados.

## 23. ATUALIZACAO 2026-07-29 — primeiro jab promovido, buildado e observado parcialmente

- O diretor de arte humano aprovou a pose pixel nativa com `Prossiga`. A
  aprovação liberou a derivação controlada, mas não substituiu os gates
  técnicos.
- Cinco quadros 64×64 foram derivados da mesma topologia: antecipação,
  lançamento, contato ativo, recoil e recuperação. Holds NTSC:
  `[3,2,2,3,4]`, total de 14 VBlanks. Pivot `(24,60)`, altura visível de
  59 px e contato de solo `y=60` permanecem fixos.
- Strip promovida:
  `res/sprites/characters/taina/taina_combo_hit_1_jab_64x64_v01.png`,
  SHA-256
  `169f66374bb0d4b0916826c77fc3e0f00e3183d43f526a40db443f2b5a4ca876`.
  O mesmo hash existe em `data/processed`.
- `validate_strip` passou; a auditoria de artefatos passou com zero findings.
  O PNG é P 4-bit, tem dez cores visíveis na grade Mega Drive, uma única ilha
  conectada por quadro e nenhum AA, alpha parcial ou FX assado.
- ResComp passou. Frames 0–4 usam respectivamente `[24,28,28,28,24]` tiles
  e `[2,2,3,2,2]` partes de metasprite. O pico é o contato ativo: 28 tiles
  (896 bytes brutos) e três partes. A ação isolada cabe; a pressão combinada
  com inimigos, HUD e FX ainda não foi medida.
- O runtime troca de `spr_taina_idle_guard` para
  `spr_taina_combo_hit_1_jab`, toca manualmente os cinco quadros e restaura a
  idle. `C` e `X` disparam o golpe: o suporte a `C` corrige a falha descoberta
  no primeiro ensaio, em que um mapeamento apenas para `X` não atendia o pad
  padrão de três botões.
- Build Linux pela bridge passou. ROM: 262144 bytes, SHA-256
  `0c281347c4d1673855a45a646cd639a395d0ea7279e15cd0b28c49d538db3822`.
  A mesma identidade foi capturada no BlastEm, cena 3, janela a 60,1 fps.
- O burst visual mostra antecipação, extensão total, recoil e retorno à
  guarda. A silhueta, a escala, o cabelo e os materiais da TAÍNA v02
  permanecem legíveis. Evidência:
  `out/blastem_env_taina_combo_hit_1_jab_v01/blastem-linux-20260729T111215Z-598254/`.
- O selo canônico foi rejeitado por `vlab_block_missing`,
  `artifact_missing:vdp_dump` e `artifact_missing:runtime_metrics`.
  Consequentemente, o estado máximo é
  `buildado_runtime_animation_observed_partial_evidence`; não
  `testado_em_emulador`, não budget completo e não AAA.
- O hitstop de dois VBlanks continua contrato de gameplay, ainda não
  implementado: esta integração prova somente reprodução visual, não colisão,
  dano, cancelamento ou confirmação de impacto.

## 24. ATUALIZACAO 2026-07-29 — contact sheet corrigida e recurso do jab deduplicado

- A prancha 6×8 revisada pelo humano não era spritesheet: continha 48 amostras
  temporais consecutivas do BlastEm. As repetições de idle pertenciam à janela
  de captura e nunca foram 48 frames residentes em VRAM.
- A revisão revelou, porém, uma duplicação real: frames físicos 0 e 4 do jab
  eram idênticos, e o frame 0 também era idêntico à idle aprovada.
- O recurso runtime v02 agora armazena somente três desenhos novos:
  lançamento, contato ativo e recoil. Antecipação e recuperação reutilizam
  `spr_taina_idle_guard` frame 0. As cinco fases e holds `[3,2,2,3,4]`
  permanecem inalterados.
- Novo asset:
  `res/sprites/characters/taina/taina_combo_hit_1_jab_runtime_unique_64x64_v02.png`,
  192×64, três células 64×64, SHA-256
  `3032acffd192412005fd61ef30e95f8307a7806a4ed30ca253f67efca1aca783`.
- ResComp passou: `[28,28,28]` tiles e `[2,3,2]` partes. O recurso bruto caiu
  de 3668 para 2862 bytes, economia de 806 bytes/21,97%. O pico VRAM continua
  28 tiles/896 bytes porque o frame ativo não mudou.
- O marcador de mundo `START` em BG_B foi removido. Ele aparecia através dos
  pixels transparentes; nenhum pixel da personagem estava oculto ou destruído,
  portanto nenhuma reconstrução do sprite foi necessária.
- Todos os rótulos visíveis `START` foram removidos da cena de revisão; o
  controle continua respondendo ao botão `BUTTON_START`, mas o texto não
  contamina nenhuma captura.
- ROM final desta correção: 262144 bytes, SHA-256
  `825dc80baa346129512ea0ef0c0eba2ab09d2a4080824a07bdeb75ded532dd2a`.
  A cena 3 abriu no BlastEm e a captura confirma o fundo limpo, sem ocorrência
  visual de `START`.
- Limite honesto: o transporte automático não acionou o jab na captura desta
  ROM. O playback observado na ROM anterior não é transferido para o novo
  hash. Estado atual:
  `buildado_final_rom_boot_observed_attack_playback_recapture_pending`.

## 25. ATUALIZACAO 2026-07-29 — locomocao P0 e primeiro recorte modular do CAIS_01

- A fonte visual permaneceu restrita à TAÍNA idle v02 aprovada. Os linearts
  v05, v06 e v07 não foram usados. O builder determinístico
  `tools/art/build_taina_p0_locomotion_v01.py` produziu três strips sem
  duplicação física: caminhada de combate com seis quadros, corrida/avanço
  com quatro e pulo com oito.
- Os três relatórios `sprite_artifact_report.v2` passaram sem clipping,
  artefatos de borda, ilhas desconectadas ou matte residual. Todos os assets
  usam PAL1, pivot inferior coerente e células 48×64 ou 64×64. Ainda são
  `runtime_candidates`: a observação prova leitura e funcionamento, não
  aprovação artística quadro a quadro.
- O runtime de `APP_SCENE_DEMO` agora alterna idle, andar, correr, pular e
  jab. A corrida usa `B/Z`, o pulo `A/Y` e o jab `C/X`. O pulo escolhe
  takeoff, subida, ápice, queda e pouso a partir da velocidade vertical; o
  jab preserva cinco fases lógicas reutilizando idle na antecipação e
  recuperação.
- ResComp mediu os picos isolados: idle 40 tiles/2 partes, andar 32/5,
  corrida 48/6, pulo 33/4 e jab 28/3. O pior estado isolado é a corrida,
  48 tiles ou 1536 bytes. Pressão combinada com inimigos, HUD e FX ainda não
  foi medida.
- O primeiro recorte do CAIS_01 foi construído por montagem modular nativa,
  sem reduzir um panorama pronto. BG_B/PAL0 contém céu, silhueta industrial e
  mar; BG_A/PAL2 contém borda do píer, piso, caixas, cabeço, corda, poste,
  rede e espuma que sinaliza o ring-out à direita. É uma sala travada de
  320×224, não o mundo streamado final.
- ResComp deduplicou o cenário para 95 tiles em BG_B e 109 em BG_A: 204
  tiles/6528 bytes de gráficos, além de 4480 bytes de mapas. Parallax,
  streaming, foreground de oclusão e animação da espuma continuam pendentes.
- Build Linux pela bridge passou. ROM atual: 262144 bytes, SHA-256
  `e1fc0dd5180ffb09f74087248f1d4d363ace93b5c1a74f0e307c1b8f3e05c1c6`.
- O BlastEm mostrou a composição atual e capturas sincronizadas comprovam
  idle, andar, correr, pulo em subida/ápice/queda e extensão do jab na mesma
  ROM. Prancha:
  `out/evidence/taina_cais01_runtime_v01/taina_cais01_runtime_contact_sheet_v01.png`.
- O primeiro roteiro de captura de movimento abriu a cena errada e foi
  movido para `out/evidence/rejected/`; ele não conta como evidência. Duas
  tentativas posteriores erraram a duração dos eventos `pressed` e também
  não foram usadas para reivindicar pulo/golpe até a recaptura correta.
- O selo formal continua bloqueado por `vlab_block_missing`,
  `artifact_missing:vdp_dump` e `artifact_missing:runtime_metrics`.
  Status máximo desta rodada:
  `buildado_runtime_observed_partial`; não `testado_em_emulador`, não
  `validado_budget`, não arte final e não AAA.
- A auditoria global encontrou 62 assets em `/res`: 29 `ok`, 33 herdados ou
  antigos ainda necessitando conversão. Os cinco recursos novos desta rodada
  aparecem como `ok`, mas isso não limpa a dívida visual global.

## 26. ATUALIZACAO 2026-07-29 — passe de densidade visual v02 do CAIS_01

- O feedback humano registrou que o teste funcional ainda estava abaixo dos
  melhores jogos comerciais do Mega Drive em paleta, detalhe do lutador,
  profundidade do fundo e iluminação. A regra foi incorporada ao feedback bank
  como `Teste Funcional Nao Atinge Densidade Comercial`.
- O cenário v02 foi reconstruído diretamente da direção autoral do kit do cais,
  sem usar o PNG runtime v01 como fonte. BG_B agora tem 512×224 para suportar
  scroll por bandas, com cinco degraus de céu, cidade, guindastes, barco e mar;
  BG_A mantém 320×224 e ganhou madeira com nós/desgaste, fascia, props, espuma,
  lampião e reflexos molhados.
- O runtime usa `HSCROLL_TILE` com 28 linhas de tile, quatro bandas de
  profundidade e 112 bytes de tabela por quadro via `DMA_QUEUE`. O lampião
  atualiza apenas PAL2 índices 14–15, quatro estados, 4 bytes a cada 8
  VBlanks. Não há H-Int, alpha ou falso gradiente.
- Foi adicionada sombra de contato separada com três células, compartilhando
  os escuros de PAL1. O ResComp mediu pico de 8 tiles/256 bytes e uma parte;
  combinada ao pior estado atual da TAÍNA, são 56 tiles e sete partes.
- ResComp mediu 249 tiles em BG_B e 277 em BG_A: 526 tiles/16832 bytes de
  gráficos e 5824 bytes de tilemaps. Esse é budget do recorte; inimigos, HUD e
  hit FX ainda não estão incluídos.
- Build Linux pela bridge passou. ROM: 262144 bytes, SHA-256
  `52856afcda732128e13012797a1acab7732ef56f85bdbe698c31742246efd70c`.
  O BlastEm confirmou cena, parallax, pulso de paleta e sombra. Comparação:
  `out/evidence/cais01_visual_v02_hash52856/cais01_runtime_compare_v01_v02.png`.
- O pacote formal foi rejeitado por `vlab_block_missing`,
  `artifact_missing:vdp_dump` e `artifact_missing:runtime_metrics`. O
  `validate_resources.ps1` confirmou metodologia, higiene e caminhos do
  `.res`, mas ficou prolongado na agregação posterior e foi interrompido; não
  conta como validação completa.
- A TAÍNA runtime não foi usada como fonte de refinamento. O próximo passe está
  congelado em
  `doc/art/characters/taina/taina_visual_detail_reseed_brief_v03.json`: voltar
  à imagem 04/concept autoral, redesenhar model sheet pixel 48×64 e obter
  aprovação humana antes de recriar strips.
- Status máximo:
  `buildado_runtime_observed_partial`. O cenário melhorou de forma observável,
  mas arte final, `validado_budget`, `testado_em_emulador` e AAA permanecem
  bloqueados.

## 27. ATUALIZACAO 2026-07-29 — passe de assinatura visual v03 do CAIS_01

- O direcionamento humano pediu um porto ao pôr do sol no patamar dos jogos
  comerciais mais avançados do Mega Drive. Streets of Rage 2/3 e Sonic 2
  foram usados somente como referência técnica de contraste, hierarquia,
  textura e scroll; nenhum tile, layout, sprite ou paleta foi copiado. A fonte
  autoral continua sendo
  `data/source_art/concept/authorial_style_validation_2026_07_04/dock_scene_kit_authorial_v01.png`.
- `tools/art/build_cais01_signature_pass_v03.py` reconstrói os dois planos em
  512×224. BG_B/PAL0 recebeu sol com borda ditherizada, cidade distante
  violeta, cidade próxima quase preta, janelas quentes, dois guindastes,
  reflexo solar quebrado e clusters de água. BG_A/PAL2 recebeu píer integral,
  manchas de óleo, marcas de pneus, rachaduras, pregos, reflexos, stencil MB,
  caixas, corda, poste e sinalização de ring-out.
- O runtime passou de `HSCROLL_TILE` para `HSCROLL_LINE`, com owner único
  `SCENE_demo` e sem H-Int. As 224 linhas usam quatro regimes: céu 1/8,
  cidade distante 1/4, cidade próxima 1/2 e água 1/4 mais onda variável. BG_A
  acompanha a câmera em 1/1. As duas tabelas custam exatamente 896 bytes de
  DMA por quadro; o fallback é `HSCROLL_PLANE`.
- A TAÍNA recebeu apenas uma paleta runtime de contraluz, com penumbra
  violeta quase preta, borda quente e acento turquesa. A geometria não foi
  refinada a partir de strips runtime: o reseed de detalhe permanece obrigado
  a voltar para a imagem 04/model sheet autoral.
- Foram adicionados dois sprites de fumaça 32×32/4 quadros compartilhando
  PAL0 e duas partículas de poeira 16×16/4 quadros compartilhando PAL2.
  ResComp mediu 12 tiles/uma parte por fumaça e até 4 tiles/uma parte por
  poeira.
- A primeira captura da v03 revelou que a sombra checker v02 ficava ruidosa
  sob a nova PAL1. A sombra v03 foi refeita com núcleo sólido quase preto e
  borda violeta esparsa; a segunda captura confirmou a correção. Aprendizado:
  uma solução de transparência aceitável numa paleta pode falhar quando essa
  paleta é reinterpretada; todo compartilhamento deve ser revisto no contexto
  runtime final.
- ResComp mediu 431 tiles em BG_B e 384 em BG_A: 815 tiles/26080 bytes de
  gráficos. O pior conjunto autorado visível atual — corrida da TAÍNA, sombra,
  duas fumaças e duas poeiras — soma 88 tiles/2816 bytes e 11 partes de
  sprite. O teto conservador de DMA em um quadro de troca simultânea é 4356
  bytes, ainda estimativa; scanline e DMA reais não foram instrumentados.
- Build Linux pela rota `linux_wine_bridge` passou. ROM: 262144 bytes,
  SHA-256
  `9c2e3e9d82e4fa4ef678bd0a087ffd74a950bd5711ad4748c6a9278fc476ce4d`.
  O BlastEm abriu diretamente a cena 3 e confirmou composição, parallax por
  linha, água, contraluz, fumaça, poeira, pulso do lampião e sombra corrigida.
  Comparação e animação:
  `out/evidence/cais01_signature_v03_hash9c2e3e/`.
- O pacote canônico continua rejeitado por `vlab_block_missing`,
  `artifact_missing:vdp_dump` e `artifact_missing:runtime_metrics`. Também
  faltam inimigos, HUD e hit FX no orçamento conjunto. Status máximo:
  `buildado_runtime_observed_partial`; não `testado_em_emulador`, não
  `validado_budget`, não arte final e não AAA.

## 28. ATUALIZACAO 2026-07-29 — alinhamento autoral v04 do CAIS_01

- A revisão humana reconheceu os efeitos técnicos da v03, mas reprovou sua
  coesão: céu, skyline, piso e props pareciam colados e genéricos. O caso foi
  registrado no feedback bank como
  `Efeito Tecnico Forte Sobre Composicao Generica`.
- A v04 separa explicitamente as fontes. `bgb_loop_mar_ceu_v01.png` fornece
  ritmo de nuvens e massa portuária; `cais_arena1_entrada_v01.png` fornece
  composição de caixas/poste/rede/faixa; o kit autoral aprovado fornece marcas
  de madeira, corda, rede e metal. Painéis antigos continuam apenas
  mood/landmark reference e nunca viraram panorama final ou downscale direto.
- `tools/art/build_cais01_art_alignment_pass_v04.py` redesenha os dois planos
  em 512×224 no grid nativo. A composição recupera nuvens horizontais, porto
  industrial compacto, sol central ditherizado, uma caixa grande com duas
  menores à esquerda, poste/rede à direita e madeira com veios, nós,
  rachaduras, pregos e óleo.
- A primeira captura v04 mostrou a corda enrolada atrás da cabeça da TAÍNA e
  uma mancha de óleo confundindo a sombra de contato. Ambos foram deslocados;
  a captura final deixa a silhueta livre. A TAÍNA não teve geometria nem
  textura derivada de strip runtime: detalhe de tecido continua exigindo
  reseed pela imagem 04/model sheet aprovado.
- As técnicas v03 foram preservadas: `HSCROLL_LINE` via DMA em VBlank, sem
  H-Int; reflexo quebrado, fumaça, poeira, palette cycling e contraluz runtime.
- Pixel strict passou: PNG P, 512×224, grid 8×8, índice 0 magenta, até 15
  cores visíveis por plano, cores no grid de 9 bits e zero alpha parcial.
  ResComp mediu 484 tiles em BG_B e 385 em BG_A: 869 tiles/27808 bytes.
  Com o envelope atual de 948 tiles de usuário, restam 79; decisão de budget:
  `cabe com recuo`. Novos detalhes devem reutilizar tiles, e o mundo de
  1344px exige streaming.
- Build Linux pela bridge passou. ROM final: 262144 bytes, SHA-256
  `825e687c8f0513f2d2d9f634f980be83426a2b84a457b0ddef6978271bfba429`.
  O BlastEm abriu a cena 3; a janela registrou 61,1 fps e a comparação
  v03/v04 está em
  `doc/art/environments/cais01/review/cais01_runtime_compare_v03_v04.png`.
- O selo formal foi rejeitado por `vlab_block_missing`,
  `artifact_missing:vdp_dump` e `artifact_missing:runtime_metrics`. Status
  máximo: `buildado_runtime_observed_partial`; não `testado_em_emulador`, não
  `validado_budget`, não arte final e não AAA.
- `validate_resources.ps1` confirmou metodologia, higiene e os caminhos
  `.res`, então entrou na agregação prolongada sem concluir por mais de dois
  minutos e foi interrompido. Nenhum `validation_report.json` completo foi
  emitido. O freshness audit permanece `warning` por esse relatório ausente,
  `res_graph` stale, build output ausente e falta de scene contract compile.

## 29. ATUALIZACAO 2026-08-29 — CRIA idle nativo no CAIS_01

- Primeiro ciclo do pipeline F-R2 no jogo: construction Imagine 3/4 a partir
  da prancha autoral, lineart de construcao, pixels nativos 48x64, PAL3,
  idle 4 frames com chinelos plantados. O video de idle levantou o pe e foi
  recusado como fonte de pixel.
- ROM sha256
  `854a18bea4fc8bdff7d71908bc52d8796d7a08a3b77753a479ff16810720de54`.
  BlastEm cena 3 `blastem-linux-20260829T162243Z-2229911`. TAÍNA e CRIA
  visiveis no cais; a CRIA foi deslocada para fora da corda do lampiao.
- ResComp: 29-30 tiles / 3-4 partes por quadro. Bundle canonico rejeitado
  (`vlab_block_missing`, `vdp_dump`, `runtime_metrics`).
- A CRIA nativa ainda e mais blocada que a TAÍNA v02. Sem walk, telegraph,
  hit, IA ou ESTIVADOR. `visual_pass=false`. `ready_for_aaa=false`.
  Parecer humano da strip nativa ainda pendente.

## 30. ATUALIZACAO 2026-08-29 — CRIA walk 4 fases nativo

- Walk 3/4 no grid 48x64: contact_L / pass_R / contact_R / pass_L, times
  5-4-5-4. Um chinelo sempre plantado; passada ~4 px. Video Imagine so
  como referencia — harvest saiu aereo e foi recusado como pixel.
- Runtime troca idle/walk a cada 2 s via `SPR_setDefinition`. Sem H-flip.
- ROM sha256
  `4e9248a42f64e78590e85e4506729cc4bf9ad52e63298d3b3570104d1e8a7847`.
  BlastEm `blastem-linux-20260829T163328Z-2259788`: burst frame 1 (pass)
  vs frame 4 (contact) muda a passada. ResComp 27-32 tiles / 2-4 partes.
- Continua `visual_pass=false` / `ready_for_aaa=false`. Sem telegraph, IA
  ou ESTIVADOR.

## 31. ATUALIZACAO 2026-08-29 — CRIA telegraph 12 vbl nativo

- Cue do roster: corrida inclinada com braco armado. 4 fases coil/load/peak/
  hold, times 3-3-4-2 = 12 VBlanks. Dois chinelos plantados. Pulseira no
  braco armado de tras (o video trocou para a frente e foi recusado).
- Runtime: idle / walk / telegraph a cada 2 s; telegraph toca uma vez e
  segura o hold.
- ROM sha256
  `ed032430c6903e211efe4c2bd04090995171f1e49613ec6ab062f84d609ae36f`.
  BlastEm `blastem-linux-20260829T164437Z-2288660`. ResComp 33-34 tiles /
  3-4 partes. Bundle canonico rejeitado (VLAB/dump).
- Continua `visual_pass=false` / `ready_for_aaa=false`. Sem ataque, IA ou
  ESTIVADOR.

## 32. ATUALIZACAO 2026-08-29 — CRIA haymaker nativo apos telegraph

- Golpe no grid 48x64: launch / active / hitstop / recover, times 3-4-6-5.
  O punho armado viaja da direita (cock do telegraph) para a esquerda
  (Taina). Pulseira permanece no braco armado. Dois chinelos plantados.
  Video Imagine so referencia — harvest bateu com o braco da frente e
  foi recusado como pixel.
- Runtime: idle / walk / telegraph / hit a cada 2 s; hit toca launch+
  active+hitstop e segura o hitstop (recover existe na strip para o
  chain ATTACK->RECOVER). Sem H-flip.
- ROM sha256
  `c63092cf27dbb6fbcd87f684f02f89051e2b307b5957c7011d75b35a74d83de6`.
  BlastEm `blastem-linux-20260829T165936Z-2328459`. Burst frame 1
  (telegraph, punho a direita) vs frame 16 (haymaker, punho a esquerda).
  Still pos-warmup caiu no idle do ciclo seguinte. ResComp 28-32 tiles /
  2-3 partes. Bundle canonico rejeitado (VLAB/dump).
- Continua `visual_pass=false` / `ready_for_aaa=false`. Sem IA, recover
  como estado proprio, ou ESTIVADOR.

## 33. ATUALIZACAO 2026-08-29 — CRIA recover nativo apos haymaker

- Strip propria follow/retract/settle/hold, times 4-5-6-8. O punho
  armado recua da esquerda (hitstop) para o peito / hang traseiro.
  Pulseira permanece no braco armado. Dois chinelos plantados. Video
  Imagine so referencia — harvest virou walk (cabeca pra cima) e foi
  recusado como pixel.
- Runtime: no slice de 2 s do golpe, hit toca launch+active+hitstop e
  troca `SPR_setDefinition` para recover; segura o hold. Sem H-flip.
- ROM sha256
  `0bde1dd0cd9e3ed7b2958e88b3c1fbb8690cf5f6e4bdf5b29c2ab16b7b60b9a9`.
  BlastEm `blastem-linux-20260829T171301Z-2363210`. Burst frame 1
  (punho a esquerda) vs frame 16 (unload). ResComp 28-32 tiles /
  2 partes. Bundle canonico rejeitado (VLAB/dump).
- Continua `visual_pass=false` / `ready_for_aaa=false`. Sem IA ou
  ESTIVADOR. Kit de motion da CRIA no slice: idle, walk, telegraph,
  hit, recover.

## 34. ATUALIZACAO 2026-08-29 — CRIA IA perseguidor

- O ciclo de 2 s saiu. `src/entities/cria.c` implementa o chain do
  roster: APPROACH (walk 1.5 px/vbl para a esquerda) -> TELEGRAPH 12 vbl
  -> ATTACK 13 vbl -> RECOVER 23 vbl -> cooldown 24. Sem H-flip. Spawn
  em x=288 (esquerda do lampiao). Strike 40 px, aggro 200, faixa y 12.
- Hit no active/hitstop empurra a Taina 8 px e toca `AUDIO_CUE_STRIKE`.
  HP/HUD ainda nao entram.
- ROM sha256
  `6bf9e359ae6ed13f926db7e4ab631943bc001291c67e2aa6249358b5ca968686`.
  BlastEm `blastem-linux-20260829T172244Z-2390350`: burst 1 approach,
  burst 20 telegraph, still do golpe atravessando a Taina. Bundle
  canonico rejeitado (VLAB/dump).
- Continua `visual_pass=false` / `ready_for_aaa=false`. Sem ESTIVADOR.

## 35. ATUALIZACAO 2026-08-30 — fechamento Convert e gate visual TAÍNA v02

- `forge-art convert` agora e rota técnica testada: self-check 103/103 e
  `test_art_pipeline` 111/111. O cache agora
  revalida semanticamente `conversion_report`; remover `metrics` e resselar
  hashes/estado é rejeitado por `cached_conversion_report_invalid`.
- O audit isolado da ferramenta (`--tool forge_art/__main__.py`) passou 1/1.
  O audit global continua bloqueado por `runtime_probe` em nove projetos
  alheios; isso não inclui MARE_BRAVA e não autoriza claim global.
- `validate_visual_source_of_truth.ps1` foi corrigido: percorre somente
  objetos/dicionários e listas, tem limite explícito de profundidade e escolhe
  a maior versão `_vNN`. Com contrato explícito v02, terminou em ~6 s,
  varreu 141 arquivos e registrou `status=passed`, sem overflow.
- O BASIC técnico da prancha aprovada existe somente no job imutável
  `4ceca437f5dc5b2c`, hash canônico
  `6e94afcc14954a338175ba24440129351c3a5db4c077bab4c111902ba0402efd`.
  É controle comparativo `technical_candidate`, não ELITE, não arte nativa e
  não promovível.
- Uma tentativa raster de lineart foi preservada como evidência negativa em
  `data/source_art/concept/taina_pixel_model_sheet/rejected/` (SHA
  `70ea460cca819084cda5f2b439f3068afba8731e026fe52dbd56aee95276edc1`).
  Mede 1086×1448 RGB, não prova grid lógico 48×64 e não deve ser reduzida,
  quantizada, usada como fonte ou promovida.
- Estado registrado naquele ciclo: faltava autoria de lineart 1px no canvas
  48×64. A suposição de que isso exigia GIMP interativo foi superada pela
  curadoria CLI-first abaixo; o gate artístico continua válido.

## 36. ATUALIZACAO 2026-08-30 — persistencia causal e GIMP CLI-first

- Operação determinística por screenshots/ponteiro foi classificada como
  `interaction_channel_mismatch`. Automação de GUI deixou de ser rota de
  produção; GIMP GUI fica opcional e humano.
- `forge_art.gimp_batch` foi adicionado como adaptador headless restrito. O
  contrato rejeita scripts/operações arbitrárias e não registra nenhuma
  operação de produção por enquanto.
- Preflight real passou no GIMP 3.2.4 (`/usr/bin/gimp-3.2`) com
  `python-fu-eval`, `sentinel_observed=true`, exit 0. Warnings de plugins e
  recursos desativados foram preservados; uma operação futura que dependa
  desses recursos não poderá usar `-d/-f` cegamente.
- `forge-art self-check` passou 107/107 após a curadoria. Isso prova o contrato
  técnico do adaptador, não qualidade visual.
- Ordem ativa: `forge-art` para VDP/indexação; Pillow/ImageMagick para
  transformações mecânicas; GIMP batch apenas para operação GIMP/GEGL estática
  e testada; produtor visual capaz para tradução semântica da TAÍNA.
- O histórico das três tentativas foi preservado, mas a decisão
  `native_pixel_authoring_in_progress_in_recovered_gimp` foi substituída por
  `cli_first_gui_human_only`.
- Nenhum PNG de produção, `res/`, build ou ROM foi alterado. TAÍNA continua
  sem lineart nativa aprovada; `visual_pass=false` e `ready_for_aaa=false`.
- Próxima ação causal: obter uma candidata nativa 48×64 de produtor visual
  capaz, validar por `forge-art validate`, comparar em escala e abrir decisão
  humana antes de color blocking ou animação.

## 2026-08-30 — tentativa de autoria nativa TAÍNA e reclassificação causal

- O blocker de produção foi corrigido para `taina_native_48x64_lineart_representation_mismatch`: A/C devolveram 1086×1448 RGB/RGBA, B/GIMP falhou no init, e a direção já estava aprovada. Produzir a lineart não é gate humano; a única decisão humana remanescente é fonte/licença de BGM/SFX.
- A rota `author_stamp_8x8_grid` foi executada em três mapas explícitos de pixels, sempre somente a partir do model sheet aprovado SHA `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`; nenhum candidato rejeitado ou runtime candidate foi lido como fonte.
- D/v01, E/v02 e F/v03 foram exportados em escala 1:1, canvas 48×64, 6×8 tiles, PNG indexed color type 3, 4bpp, index 0 transparente e uma cor visível na grade 9-bit. `pixel_contract --self-check` passou 19/19 e F passou sem blockers com hash `a9a678480abed70c7ba1d5dc7bfd1a892e5fe84b8f9c2d9a1315bb700c9cab12`.
- A inspeção 1x/8x marcou os três como candidatos técnicos, não como lineart visual aprovada: face, guarda diagonal e assimetria ainda estão genéricas. Isso é `lineart_blocking_visual_pass_pending`/`generic_blocky_redraw`, não decisão humana. Basic/elite foram adiados e nenhum PNG foi promovido para `res/`.
- Artefatos: `native_author_stamp_report_v01/v02/v03.json`, `pixel_compliance_report_v03.json`, `native_grid_translation_report_v02.json`, `lineart_blocking_report_v02.json` e tentativas atualizadas. A rota author-stamp fica fechada após três evidências; próxima ação é trocar a representação/produtor visual capaz, então revalidar antes de basic+elite.
- Estado: `visual_pass=false`, `creative_ready=false`, `ready_for_aaa=false`.

## 38. ATUALIZACAO 2026-08-30 — candidato nativo editor e reconciliação de fonte

- A referência visual v02 foi movida de `rejected/` para `construction_reference/`
  sem alterar bytes; SHA256 `70ea460cca819084cda5f2b439f3068afba8731e026fe52dbd56aee95276edc1`.
  Continua `rejected_not_native_grid_candidate` para uso técnico e agora é
  `approved_visual_construction_reference_not_native` para construção; o
  histórico está em `doc/history/taina_visual_source_reconciliation_2026-08-30.json`.
- A rota do editor produziu lineart autoral 48×64, 1 px, 198 pixels. O PNG
  indexado `taina_reseed_native_lineart_editor_candidate_v01_indexed.png` tem
  SHA256 `9d6cd24ac58a0fdd50bb65ee200af01befb5fce35feabdffd6335c5b81b0daa3`.
  O registro `native_sprite_production_record.json` e o validador passaram.
- O pixel contract passou sem blockers; a prancha de revisão mostra identidade
  ainda genérica, portanto o status fica `technical_candidate`, sem BASIC/ELITE,
  `res/`, ROM ou claim AAA. `visual_pass=false` e `ready_for_aaa=false`.
- Regressão final do ciclo: `forge-art self-check` 107/107 e
  `test_art_pipeline.py` 116/116; `validate_native_sprite_production.py`,
  contexto, higiene e metodologia passaram. `git diff --check` está limpo.
- Uma segunda execução de `forge-art convert` retornou `cache_hit=true` para
  o mesmo job `22db1183a4d6a166`, repetindo todos os hashes de saída e o selo
  `e2ddd7d7249a504fb959eee5c11db92091961acadebb6afe872da5cde90e2792`.
- O manifesto de terceiros agora diferencia explicitamente
  `algorithm_studied_and_reimplemented` (SoftLK/tiledpalettequant),
  `runtime_dependency` (Pillow) e `development_dependency` (GIMP); não há
  alegação de código copiado.

## 39. ATUALIZACAO 2026-08-30 — recuperacao de conhecimento e hardening do validator

- **Recuperado o exercicio vencedor** `rascunho/taina_visual_challenger_exercise_v01/exercise_record.json`
  como `methodology_reference` (NUNCA fonte de pixels). Ele registra:
  `native_48x64_visual_gate=failed_face_hands_feet_and_presence`,
  `native_64x96_visual_gate=promising_pending_human_scale_camera_and_vdp_budget_gate`,
  `native_48x64_claim=false`, e `next_causal_step` = abrir scale gate formal
  comparando 48x64 direto-nativo contra 64x96 na camera real 320x224. A recaída
  para lineart esparsa (2 cores visiveis, 198 cliques) veio de discretizar a
  producao direto para 48x64 sem passar pela escada (silhueta -> regioes
  semanticas -> clusters -> color blocking -> palette clean) nem checar a escala.
- **Rota fechada** `binary_pointer_editor_as_primary_visual_producer`: o editor
  nativo e `qa_corrective`, nunca produtor visual primario. O produtor visual e
  modelo de imagem + representacoes intermediarias; Pillow/ImageMagick/forge-art
  so fazem operacoes deterministicas.
- **Curatia de proveniencia** `taina_reseed_native_lineart_editor_candidate_v01`
  reprovada pelo validador semantico com 5 blockers: `provenance_human_unproven`,
  `visual_evidence_not_distinct` (1 painel nos 4 papeis), `native_1x_not_candidate`,
  `palette_lock_on_binary_lineart`, `scale_pass_without_report`. Mantida apenas
  como `technical_pass_visual_fail` / evidencia negativa.
- **Incumbente comparativa** preservada (pose anterior com 11-14 cores, leitura
  muito superior). Challenger so substitui incumbent se vencer perceptiva E
  sistemicamente (regra de incumbencia). Nunca usar incumbent como fonte de pixels.
- **Hardening**: `validate_native_sprite_production.py` agora e fonte executavel
  da verdade semantica (CLI `--project-root`/`--record` + posicional; resolve
  paths com seguranca; re-deriva pixel contract e medicao do disco; exige 4
  evidencias distintas do mesmo hash com native_1x byte-a-byte; conferencia de
  proveniencia, scale/visual/budget/human independentes; incumbent + referencial
  metodologica com hash). Schema `native_sprite_production_record.schema.json`
  elevado a 1.1.0 com provenance/scale_report/incumbent/methodology_reference
  obrigatorios e visual_evidence obrigatoria. `aaa-pipeline-guardian` apenas
  CONSUME o veredito (`native_sprite_semantic_gate_failed`), sem duplicar logica.
- Estado: `visual_pass=false`, `ready_for_aaa=false`, `res/` nao alterado.
  Proxima acao causal: reabrir scale gate formal (48x64 vs 64x96).

## 40. ATUALIZACAO 2026-08-31 — probes de escala 48x64 vs 64x96 + validador semantico v2.2

- **Validador semantico endurecido** (`validate_native_sprite_production.py` v2.2):
  mede `filled_pixels` excluindo transparencia (a candidata antiga mede **198 px visiveis**,
  nao 3072), re-deriva pixel contract + `content_sha256` do disco, exige 4 evidencias
  DISTINTAS e determinadas (native_1x byte-a-byte, nearest NEAREST, light/dark recompostos),
  valida schema Draft 2020-12 exclusivamente com `jsonschema` completo, fecha proveniencia via
  campo `provenance`, mantem scale/visual/budget/human independentes, exige incumbent +
  methodology_reference e bloqueia challenger sem `perceptual_win`+`system_win`. O
  `shape_block_contract` agora e obrigatorio sempre que existe candidata, exige tres
  artefatos nativos distintos e o schema foi elevado a `1.2.0`.
- **Probes gerados** por reducao mecanica NEAREST da figura extraida do model sheet aprovado,
  classificados como `photo_or_render_derived` / `mechanical_scale_probe`. Nao sao autoria
  nativa, nao provam traducao artistica e nao podem alimentar pixels finais. O roteador atual
  detecta `native_chat_image_generation_callable`; a antiga alegacao `selected_source=blocked`
  nao descreve mais o host corrente:
  - `taina_probe_48x64_native_indexed.png`: 48x64, 15 cores, **796 px visiveis** (25.91%),
    30 tiles unicos/48 (0.62 dedup), 960B VRAM, metasprite 2x2 = 4 sprites VDP, 48px/scanline.
  - `taina_probe_64x96_native_indexed.png`: 64x96, 15 cores, **1396 px visiveis** (22.72%),
    49 tiles unicos/96 (0.51 dedup), 1568B VRAM, metasprite 2x3 = 6 sprites VDP, 64px/scanline.
  Ambas as poses estaticas isoladas cabem nos limites citados de H40. Isso nao mede animacao,
  camera real, coexistencia com inimigos/FX, DMA ou pior scanline da cena. Saida:
  `technical_candidate` (`basic_technical_control`), `visual_status=pending`,
  `promotable=false`.
- **Comparacao**: 64x96 tem 1.75x mais pixels visiveis e 1.63x mais tiles unicos que 48x64,
  preservando proporcionalmente mais massa/identidade (o que o exercise_record ja antecipava:
  48x64 visual_gate=failed_face_hands_feet_and_presence; 64x96 promising). Ambos sao
  probes, nenhum promotable; a decisao de escala permanece de gate humano APOS medicao de
  camera real e budget completo.
- **Estado corrigido**: status=`pending_scale_probe_generation`, `visual_pass=false`,
  `ready_for_aaa=false`, `res/` nao alterado. O record agora falha fechado porque os tres
  papeis de shape block apontam para artefatos high-res/reutilizados, nao para silhueta,
  mapa semantico e overlay distintos em grade nativa. O gate de escala esta `in_progress`;
  o gate humano permanece `not_started` ate existir comparacao visual e budget completos.

## 41. ATUALIZACAO 2026-08-31 — pacote de challengers visuais TAINA v02

- O canal de produção visual confirmado é `native_chat_image_generation_callable`,
  sempre referenciado ao model sheet aprovado (`324951fb...c0cf87a`). Foram persistidos
  dois challengers em 48x64 e dois em 64x96 dentro de `rascunho/`, sem alterar `res/`.
- Cada pacote contém PNG indexado em resolução exata, evidência 1x, nearest 8x, fundos
  claro/escuro e três artefatos shape block nativos distintos: `silhouette_mask`,
  `semantic_region_map` e `contour_overlay`. O mapa semântico traz oito rótulos
  obrigatórios com contagens rederiváveis, e cada artefato tem hash e link explícito.
- `validate_native_sprite_production.py` está em v2.3 e a suíte adversarial permanente
  está em 22/22. O registro atual passa o gate semântico, mas permanece
  `technical_candidate`, `promotable=false`, com `native_visual`, `scale`, `budget` e
  `human` em aberto.
- Painel e relatório: 48x64 A é a recomendação preliminar por equilíbrio visual/sistema;
  64x96 A é fallback de fidelidade. No worst case hero + quatro inimigos, 48x64 mede
  20 links/linha (limite H40) e 64x96 mede 22 (overflow). Isso não substitui captura em
  emulador nem decisão humana.
- Próxima ação causal: gate humano no painel comparativo, confirmar escala e candidato;
  só então iniciar autoria nativa refinada/animação, integração SGDK e evidência BlastEm.

## 42. CORRECAO DE CURADORIA 2026-08-31 — v02 reaberto antes do gate humano

- A conclusao da secao 41 foi reaberta: 48x64 A continha um matte retangular
  claro; 48x64 B continha halo conectado. O builder usava threshold global e
  LANCZOS. O mapa semantico era geometrico por bandas e fabricava rotulos de um
  pixel. Portanto o pacote v02 nao sustenta `semantic_parse=passed` nem gate
  humano final; permanece evidencia de retrabalho.
- O pixel contract v1.2 agora bloqueia `palette_alias_indices`. O schema nativo
  v1.3 e o validador v2.4 exigem `foreground_matte_report` para traducao
  assistida/mecanica, silhueta igual a mascara do candidato, uniao semantica
  exata, regioes com area significativa e contorno 4-neighbor rederivado.
- O simulador VDP v1.2 decompoe celulas <=32x32 por faixa Y. No mesmo cenario
  teorico (TAINA + quatro inimigos), 48x64 mede 12 links totais, pico 6/linha e
  176 px/linha; 64x96 mede 14 totais, pico 6/linha e 192 px/linha. O antigo
  resultado 20/22 links por linha era erro de medicao; a escala 64x96 esta
  reaberta, ainda pendente de layout real, camera, gameplay e BlastEm.
- Regeneracao temporaria com matte conectado as bordas + NEAREST removeu o
  retangulo/halo e manteve os quatro candidatos tecnicamente conformes, sem
  tocar `res/`. O parser anatomico automatico continuou fraco (bracos/guarda
  com 0-9 pixels), logo a proxima rota exige mapa semantico realmente curado e
  refinamento nativo, nao rotulos forjados.
- Regressao da curadoria: forge-art 111/111, gate semantico 28/28 e self-check
  do simulador passaram. Estado: `technical_candidate`, `visual_pass=false`,
  `human=not_started`, `ready_for_aaa=false`, `res/` intacto.

## 43. ATUALIZACAO 2026-08-31 — pacote visual TAINA v03 pronto para gate humano

- A guarda de ambiente foi executada por `pwsh` porque o alias `powershell` não
  existe neste host; `agent_environment_status=ready`, Graphify fresco e
  `persistence_route_report.json` emitido.
- Núcleo provado antes da produção: `forge-art` 111/111, art pipeline 116/116,
  semantic gate 28/28, simulador VDP 1.2 self-check aprovado e auditor isolado
  de ferramenta `verdict=OK` 1/1. O diagnóstico classificou
  `2_res_inadequate_check`, com 20 assets ativos sem blockers de build.
- O pacote `rascunho/taina_visual_challengers_v03/` foi gerado sem sobrescrever
  v02 e sem tocar `res/`. Hashes SHA-256 de bytes: A48
  `20e9c3b8cdb3d8620954b016131e1338b71087924518b24b1bebf9eed372e5dc`, B48
  `d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa`, A64
  `a7af68da88e977f2160a3304628be3cadc3bc5d71a8a6cea4b37ff119ffc314e`, B64
  `8b8b334e66094fb9db6b135c35e72b152279b2089f57a593f4713809f6aca200`.
- O matte usa `border_connected_color_flood_v1` com reports aprovados; os
  candidatos usam NEAREST, PNG P/4bpp, índice 0 transparente, alpha binário,
  paleta VDP sem aliases e sem halo/retângulo/franja. O mapa semântico foi
  curado como anotação anatômica por pose, não por bandas horizontais ou tokens;
  auditoria do pacote passou 4/4.
- Budget corrigido em `scale_budget_report_v03.json`: no caso TAÍNA + 2 CRIA +
  2 ESTIVADOR, 48x64 mede 20 links totais, pico 10 sprites/scanline e 248 px;
  64x96 mede 22 links, pico 10 e 264 px. Ambos cabem em H40. O próximo degrau
  3 CRIA + 3 ESTIVADOR estoura pixels: 348 px e 364 px. Tiles/únicos: A48
  48/29, B48 48/30, A64 96/53, B64 96/64; VRAM única 928/960/1696/2048 B.
  Hitbox segue `undeclared_requires_collision_contract`.
- Painel `taina_visual_comparison_panel_v03.png` inclui model sheet aprovado,
  incumbent `comparison_only`, quatro candidatos, 1x/NEAREST 8x,
  light/dark/chroma, câmera 320x224, footprint/pivot/ground cue e métricas.
  Challenger B é apenas `human_preference_prior`; não há score ou recomendação
  automática.
- Record está em `technical_candidate`, `promotable=false`, `human=not_started`,
  `visual_pass=false`, `ready_for_aaa=false`; semantic/pixel/budget técnicos
  passaram e escala/visual continuam independentes. O validador semântico passou
  sem erros. Próxima ação: decisão humana por `asset_id + SHA-256` e escala.
  Não iniciar animação, `res/`, integração SGDK ou BlastEm antes da decisão.

## 44. ATUALIZACAO 2026-08-31 — decisão humana e refinamento nativo TAINA B

- Decisão humana persistida em `doc/art/characters/taina/human_direction_scale_decision_v03.json`:
  `approved_for_native_refinement_only`, asset `taina_48x64_challenger_b`, SHA-256
  `d66110ba9a035dd1d4fbefd5c5692b4b66ce6a0af3b24543f6a9f0091d0975aa`, escala 48x64.
  O escopo não autoriza `res/`, animação final, ROM nem claim AAA; uma nova decisão
  visual BASIC/ELITE é obrigatória.
- O record foi atualizado para `native_authoring`, com aprovação humana em andamento,
  escala de produto registrada para o ramo de refinamento, mas gates visual, pixel final,
  integração e emulador permanecem independentes; `promotable=false`.
- O pacote `rascunho/taina_native_refinement_v01/` contém duas variantes derivadas
  somente do B aprovado: `taina_48x64_refined_basic_v01.png` (SHA-256
  `e78f77d92614eb0ec2c7a0ec529d7649db025a0a793b93f3b749323708a7b403`, 9 cores)
  e `taina_48x64_refined_elite_v01.png` (SHA-256
  `0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13`, 11 cores).
  Ambas preservam a silhueta pixel a pixel, usam limpeza de clusters sem interpolação,
  P/4bpp, índice 0 transparente e shape block herdado do B como contrato de forma.
- Validação específica passou: dois candidatos, alpha binário, 48x64, até 15 cores,
  silhueta preservada e `native_1x` byte-identical. Forge-art passou nos dois.
  Budget corrigido: ambos 48/30 tiles bruto/único, 960 B VRAM/DMA, 20 links,
  pico 10 sprites e 248 px no caso TAÍNA + quatro inimigos; próximo degrau 3+3 mede
  348 px e estoura o limite de 320.
- O painel `taina_native_refinement_comparison_panel_v01.png` não pontua nem escolhe
  automaticamente. O próximo gate é visual humano BASIC versus ELITE. `res/` não foi
  tocado e nenhuma animação, integração SGDK, ROM ou BlastEm foi iniciada.

## 45. ATUALIZACAO 2026-08-31 — reconciliação documental v03 e gate BASIC/ELITE

- O manifest v03 foi corrigido para separar `identity_source` (model sheet aprovado,
  SHA `324951fb...c0cf87a`) de `translation_input_sources`: os quatro producer outputs
  persistidos do v02, cada um com path e SHA-256. A anotação passou a se chamar
  `agent_curated_diagnostic_annotation`; ela continua diagnóstica, não aprovação humana.
- O budget v03 agora declara `budget_pass_scope=hero_plus_four_enemies_only`.
  O cenário 3+3 permanece somente `comparison_only_not_budget_pass`. A escala está
  travada em 48x64 para este slice; 64x96 está explicitamente `comparison_only`.
- O painel v03 foi regenerado com fonte Unicode que renderiza corretamente `TAÍNA`.
- A decisão humana continua limitada a `approved_for_native_refinement_only`; não foi
  convertida em `visual_pass`, `ready_for_res` ou claim AAA. O record permanece
  `native_authoring`, `human=in_progress`, `promotable=false`.
- O gate BASIC/ELITE está pronto com hashes: BASIC
  `e78f77d92614eb0ec2c7a0ec529d7649db025a0a793b93f3b749323708a7b403`; ELITE
  `0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13`. Ambos passaram
  a auditoria nativa específica, forge-art, shape/silhueta, palette role map e budget.

## 46. FECHAMENTO 2026-08-31 — gate BASIC/ELITE pronto para decisão

- Correção de portabilidade concluída: manifests de refinamento usam caminhos relativos
  ao workspace, sem alterar os hashes dos PNGs. Cada variante possui `palette_role_map`,
  `foreground_matte_report`, `silhouette_mask`, `semantic_region_map`, `contour_overlay`
  e evidências 1x/8x/light/dark/chroma/câmera.
- Painéis v03 e de refinamento foram regenerados com fonte Unicode; `TAÍNA` está renderizado
  corretamente. Não existe score estético ou vencedor automático.
- Tentativa ImageGen de edição foi descartada: retornou canvas grande com checkerboard
  assado e deriva de proporção/pose; não entrou no projeto. Uma primeira serialização dos
  refinamentos também foi descartada por PLTE 256/8bpp; a versão final P/4bpp passou.
- Validações finais: forge-art 111/111, art pipeline 116/116, semantic gate 28/28,
  v03 4/4, refinamento 2/2, VDP self-check, measurement audit, proveniência e record
  sem erros. Teto atual: `native_authoring`/review de pose; sem animação, `res/`, ROM,
  runtime ou AAA.

## 47. DECISAO HUMANA 2026-08-31 — rejeição do refinamento nativo

- A decisão humana foi `rejected_for_final_native_pose` para BASIC
  (`taina_48x64_refined_basic_v01`, SHA-256
  `e78f77d92614eb0ec2c7a0ec529d7649db025a0a793b93f3b749323708a7b403`) e ELITE
  (`taina_48x64_refined_elite_v01`, SHA-256
  `0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13`). Motivo
  registrado: `procedural_palette_cleanup_without_material_native_geometry_refinement`.
- ELITE foi preservado somente como `best_technical_control`; isso não é aprovação
  visual final nem autorização de promoção.
- A escala continua travada em 48x64 para este slice. 64x96 permanece
  `comparison_only`; a rejeição não reabre a escala.
- O record entrou em `rework`, com `native_visual=failed`, `human=failed` e
  `promotable=false`. O próximo trabalho exige nova hipótese de refinamento geométrico
  nativo por material antes de gerar novos candidatos.
- `res/`, animação, integração SGDK, ROM/BlastEm e claims `visual_pass`/AAA continuam
  bloqueados. Os PNGs rejeitados permanecem preservados como evidência técnica e
  negativa; nenhum pixel novo foi produzido nesta decisão.

## 48. RODADA 2026-08-31 — challengers de geometria nativa em gate humano

- A correção documental confirmou `gates.scale=passed` porque o contrato está locked;
  `native_visual=failed` e `human=failed` permaneceram independentes no record.
- Foram produzidas três hipóteses independentes a partir apenas do model sheet aprovado:
  A `FACE_AND_GUARD_TOPOLOGY`, B `SILHOUETTE_AND_WEIGHT` e C
  `INTEGRATED_NATIVE_REDRAW`. Nenhuma usa pixels de B/ELITE; esses arquivos aparecem
  somente como controles de comparação.
- A tradução usa matte conectado às bordas quando necessário, NEAREST e color blocking
  por rampa fixa de material; não usa GIMP, ponteiro, interpolação proibida, primitiva,
  morphology, neighbor voting ou quantização estatística. O fundo opaco de C foi
  tratado pelo matte conectado, com relatório persistido.
- Em 1x, A favorece leitura de face/guarda; B favorece centro de massa, separação de
  pernas e baseline; C favorece reconstrução compacta integrada. As perdas observáveis
  estão no parecer, sem score numérico ou vencedor automático.
- Todos os três passam o preflight técnico: 48x64, P/4bpp, PLTE 16, 12–13 cores
  visíveis, índice 0 transparente, aliases ausentes, shape coverage completa e
  evidências derivadas do mesmo SHA. Budget idêntico de cena: TAÍNA + quatro inimigos
  = 20 links, pico de 10 sprites e 248 pixels/scanline; 3+3 = 28 links e 348 pixels,
  mantido somente como comparação acima de H40.
- Contenção passou: `data_unchanged=true`, `res_unchanged=true`, staging-only e
  `res_promotion=false`. O pacote está em `pending_human_decision`; animação, `res/`,
  ROM e AAA continuam bloqueados.

## 49. DECISAO HUMANA 2026-08-31 — fonte A aprovada para nova autoria nativa

- A decisão exata foi `approved_as_visual_source_for_native_authoring` para
  `face_and_guard_topology_visual_source_v01`, SHA-256
  `b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf`, com alvo
  48x64.
- O PNG nativo derivado `taina_48x64_geometry_face_guard_v01`, SHA-256
  `1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830`, foi marcado
  explicitamente como `technical_control_only`; não é aprovação de pose final.
- A próxima autoria deve refinar geometria nativa por material a partir da fonte A,
  sem usar pixels dos controles rejeitados. 48x64 permanece travado e 64x96 continua
  `comparison_only`.
- `res/`, animação, integração SGDK, ROM/BlastEm e claims finais continuam bloqueados;
  o próximo gate é revisão humana da nova autoria nativa.

## 50. AUTORIA NATIVA 2026-08-31 — fonte A, nova candidata em gate humano

- A decisão humana aprovou somente `face_and_guard_topology_visual_source_v01`, SHA-256
  `b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf`, para autoria
  nativa com alvo 48x64. O candidato anterior A, SHA-256
  `1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830`, permanece
  `technical_control_only`.
- A primeira autoria intermediária v02 foi descartada em revisão 1x por ainda comprimir
  o rosto. A v03 foi produzida a partir de uma saída visual nova derivada da fonte A,
  sem pixels dos controles rejeitados.
- Nova candidata: `taina_48x64_native_authoring_face_guard_v03`, SHA-256
  `e3a35e5fad1a77c3931a0b3e0cf30e1f877b25e8fcf3d3ac87b5ca1d4a3f4d33`; 12 cores
  visíveis, 48x64, 4 células VDP, 20 links e 248 pixels/scanline no caso TAÍNA + quatro
  inimigos. A comparação mudou 90 pixels de máscara contra o controle A.
- O pacote v03 está em `pending_human_decision`. `res/`, animação, SGDK, ROM/BlastEm e
  claims de pose final/AAA continuam bloqueados.

## 51. AUTORIA NATIVA HEADLESS 2026-08-31 — A1/A2 em gate humano

- O pacote `taina_native_geometry_challengers_v01` foi reclassificado: A, B e C são
  `technical_candidate/mechanical_translation_probe`, produzidos por NEAREST, mapping
  mecânico de materiais e anotações coordenadas. Não são `native_author_output`.
- Os mapas antigos foram marcados como `diagnostic_coordinate_annotations`; o semantic
  gate anteriormente aprovado pertence somente ao record legado de
  `taina_48x64_challenger_b`.
- A fonte humana continua sendo `face_and_guard_topology_visual_source_v01`, SHA-256
  `b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf`. O probe A,
  SHA-256 `1177d2343b1b9e6fc0f2814add62a979067539cddb0c3ca4952ca7f754d73830`,
  permanece apenas como controle técnico.
- Foram produzidas por patches explícitos duas candidatas nativas: A1
  `taina_48x64_native_a1_face_guard_feet_v01`, SHA-256
  `1033e5a387047c320b9f2bbf6b0bddaafb2d29fd9b74810a40af8001c0947794`, e A2
  `taina_48x64_native_a2_weight_sash_v01`, SHA-256
  `041e6fd184bdff499f110075245be570f1597d9085689f7657ca2c55ed878ae0`.
- Cada variante possui patch com hashes, lineart/blocking, semantic map autoral por
  runs irregulares cobrindo exatamente a silhueta, contour, palette role map, evidências
  1x/8x/fundos/câmera, mask delta, budget e record temporário próprio. Ambos passaram
  o validator nativo com `errors=[]`.
- A1 enfatiza face, mandíbula, olho, separação de punhos e contato dos pés; A2 enfatiza
  peso da base, separação sash/calça e assimetria do cabelo. Sem score e sem vencedor
  automático. `res/`, animação, ROM/BlastEm e AAA continuam bloqueados.

## 52. CURADORIA 2026-08-31 — topologia de materiais antes do shading

- O feedback humano reprovou a separação top/pele em A1, A2 e PROBE A. A barra
  inferior do crop top deixa laranja invadir a barriga; os braços também herdam
  pixels laranja, com maior gravidade no braço esquerdo do espectador.
- A causa foi localizada no classificador posicional/de matiz do probe: `torso` e
  `arms_or_guard` são regiões anatômicas amplas e não provam propriedade de
  material. Os patches A1/A2 corrigiram outras regiões e herdaram esse erro.
- A1 permanece o melhor controle visual e foi autorizada somente como
  `explicit_pixel_patch_base`, nunca como fonte de identidade/geração. A próxima hipótese é
  `taina_48x64_native_a1_material_clean_v01`: patch mínimo e explícito, preservando
  pose, silhueta, rosto, guarda, cabelo, pés, sash, pivot e escala; não regenerar o
  personagem inteiro.
- O contrato causal está em
  `doc/art/characters/taina/taina_material_topology_correction_request_v01.json`.
  Ordem: barra do top/barriga, braço esquerdo, braço direito, wraps. Borda dura de
  1 px é o default; nenhum AA híbrido laranja/pele.
- O framework ganhou `native_sprite_production_record` 1.4.0 backward-compatible e
  `material_region_contract`, com mapa de proprietário, overlay de fronteiras,
  índices permitidos, outline compartilhado e fronteiras críticas. O validator
  rederiva vazamento e mantém records 1.3.0 legados válidos.
- Até um novo candidato passar material topology, pixel, visual e decisão humana,
  `res/`, animação derivada, integração, ROM/BlastEm e claims AAA continuam
  bloqueados.

## 53. REWORK 2026-08-31 — material-clean native challenger em gate humano

- A Source A aprovada foi revalidada por SHA-256 `b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf`; a base autorizada A1 foi revalidada por SHA-256 `1033e5a387047c320b9f2bbf6b0bddaafb2d29fd9b74810a40af8001c0947794`. Nenhum dos dois bytes foi alterado.
- Produzida a candidata `taina_48x64_native_a1_material_clean_v01`, SHA-256 `54df9fd341ad57bdc2c02c62db6366119c7d511ba8e14862666cf487366b2567`, somente por patch literal nativo. Patch SHA-256: `6bdeaba407613f675712ff5c23a1404a229125552533cfe84a494a5dbd959bfe`; 70 operações com `old_index` conferido.
- A hipótese mudou a topologia interna, não a escala nem a silhueta: 7 pixels laranja viraram hem compartilhado; 14 pixels laranja do abdômen viraram pele; 22 pixels laranja dos braços viraram pele; 20 pixels teal e 7 pixels índigo da ROI abdominal foram reatribuídos a pele/contorno para restaurar a propriedade material demonstrada pela Source A.
- A candidata preserva 48x64, pivot/ground contact, pose, guarda, cabelo assimétrico, rosto, sash e máscara externa da A1. Mantém 12 cores visíveis, P/4bpp, PLTE 16, índice 0 transparente, alpha binário, 48 tiles brutos/30 únicos e 4 células VDP.
- O record novo usa `schema_version=1.4.0` e `material_region_contract`: mapa completo de proprietário, rampas exclusivas, outline compartilhado no índice 1, overlay derivado, relatório de vazamento e quatro fronteiras críticas. `material_topology=passed`; `native_visual` e `human` permanecem em andamento por exigência do schema enquanto o pacote está `pending_human_decision`.
- Evidências persistidas: 1x, nearest 8x, claro, escuro, chroma, câmera 320x224, crops de abdômen/braço esquerdo/braço direito, mapa material, overlay, painel Source A/A1/nova candidata e manifests vinculados ao mesmo SHA.
- Validações: forge-art self-check 111/111; art pipeline 116/116; semantic fixtures 36/36; validator do record sem erros; pixel contract técnico sem blockers; material leakage report `passed`; provenance audit `OK blocking=[]`; VDP 4-inimigos `ok` (20 links, 10 sprites/scanline, 248 px/scanline) e 3+3 `error` apenas no controle comparison-only (348 px/scanline). O overlay inicialmente marcou transparência como fronteira; essa falha foi corrigida para derivar somente fronteiras entre materiais visíveis, e o validator passou.
- `audit_tile_residency` global permanece bloqueado por estado preexistente de todos os assets simultâneos (2117 tiles contra teto util de 1740); não é atribuído a esta candidata e não foi corrigido nesta rodada. O `res/` e `data/` permaneceram inalterados.
- Teto: `technical_candidate`, `material_topology=passed`, pacote `pending_human_decision`, `promotable=false`; sem visual_pass, ready_for_res, animação, integração SGDK, ROM/BlastEm, `ready_for_aaa` ou claim AAA. Próximo gate exclusivo: aprovação/rejeição humana do SHA acima como pose nativa final.

## 55. REJEIÇÃO HUMANA G2 E REABERTURA DE ESCALA — 2026-08-31

- A decisão humana rejeitou `taina_48x64_native_g2_volume_identity_v01`, SHA-256
  `e35ad9f4477d7d1912b94505932a547e639cdea8b8085e2062362db3f21dcb30`, como pose final.
  A classificação obrigatória é `technical_pass_visual_fail`, `source_detail_lost`,
  `generic_blocky_redraw` e `identity_hooks_lost`. O PNG, spans, lineart e mapas do pacote
  foram preservados somente como evidência negativa; não podem ser fonte de geração.
- A linhagem foi corrigida: a imagem `face_and_guard_topology_visual_source_v01.png`,
  SHA-256 `b2400128254e08c6aeeabd2feded594ef56762ae1a77a28f20f6076c5690bcaf`, é
  `ai_generated_high_res` e `visual_source_for_native_authoring`; a única fonte de
  decisões de pixel é o model sheet v02, SHA-256
  `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`.
- A saída do builder `build_taina_native_g2_volume_identity_v01.py` foi reclassificada
  como `procedural_primitive`/`visual_lab_control`, nunca `hand_authored_pixel`. Os mapas
  derivados da tabela de tokens são agora explicitamente `agent_curated_diagnostic_annotation`
  e evidência de consistência interna, não prova independente de lineart, semântica,
  fidelidade ou qualidade.
- `scale_gate_reopened_by_human_review=true` foi registrado. O record usa
  `scale=in_progress` e `scale_report=pending` porque `hitbox` continua
  `undeclared_requires_collision_contract`; 48x64 permanece o incumbent e 64x96 é
  `comparison_only` até um shootout nativo independente.
- Não há no host editor nativo de pixels disponível; GIMP pointer/batch e
  Python/PIL/ImageDraw/rasterização procedural estão proibidos para esta autoria. Por
  divergência de proveniência, nenhum challenger novo 48x64/64x96 foi fabricado. O
  bloqueio está registrado em `doc/art/characters/taina/native_authoring_blocker_v01.json`.
- Estado operacional: `status=native_candidate`, `promotable=false`, `res_unchanged=true`,
  `ready_for_aaa=false`. `res/`, animação, integração SGDK, ROM/BlastEm e qualquer claim
  de pose final continuam bloqueados.

## 54. DECISÃO HUMANA E G2 GEOMETRIA NATIVA — 2026-08-31 (REGISTRO HISTÓRICO SUPERADO)

- A decisão humana rejeitou `taina_48x64_refined_basic_v01`, SHA-256
  `e78f77d92614eb0ec2c7a0ec529d7649db025a0a793b93f3b749323708a7b403`, e
  `taina_48x64_refined_elite_v01`, SHA-256
  `0c30d7c449eda1086ecce917fa4fcd0403207ed06b28577f89ef3d0cc351ef13`, por
  `procedural_palette_cleanup_without_material_native_geometry_refinement`.
  O ELITE rejeitado permanece somente como `technical_control_only`; A1 material-clean
  permanece somente como `material_topology_control_only`. A decisão foi persistida em
  `doc/art/characters/taina/human_material_clean_rejection_v01.json`.
- O registro técnico da época descreveu G2 como autoria nativa produzida a partir da
  Source A. Essa descrição foi corrigida pela decisão humana posterior: a saída é
  `procedural_primitive`/`visual_lab_control`, não `hand_authored_pixel`; candidato:
  `taina_48x64_native_g2_volume_identity_v01`, SHA-256
  `e35ad9f4477d7d1912b94505932a547e639cdea8b8085e2062362db3f21dcb30`.
- A hipótese G2 tinha esses objetivos de geometria, mas a revisão 1x observou perda de
  detalhe de fonte, desenho genérico blocado e perda de hooks de identidade. Os 15
  índices, mapas e 48 tiles brutos/37 únicos continuam somente evidência técnica.
- O record 1.4.0, shape block, semantic map, contour, material map/boundary overlay,
  leakage report, paleta, evidências 1x/nearest/fundos/câmera/crops e comparação com
  Source A/MATERIAL CLEAN estão em `rascunho/taina_native_g2_volume_identity_v01/`.
- O record passa `validate_native_sprite_production` sem erros como controle técnico;
  `native_visual=failed`, `human=failed` e `scale=in_progress`.
- Budget medido: TAÍNA + quatro inimigos = 20 links, 10 sprites/scanline e 248
  pixels/scanline, H40 OK. O degrau 3+3 = 28 links, 14 sprites e 348 pixels/scanline,
  acima de 320, permanece comparison-only. `res/`, animação, SGDK, ROM/BlastEm e
  claims finais continuam bloqueados; a decisão humana sobre o SHA G2 já foi rejeitada
  e a escala foi reaberta para um shootout nativo independente.

## 56. DECISÃO HUMANA 56x80 E AUTORIA NATIVA EM STAGING — 2026-08-31

- A decisão humana vigente é `approved_for_native_authoring_scale` para
  `taina_idle_guard_56x80_visual_source_v01`, SHA-256
  `32c5a8089c52251c0276eb0c28406b44e7797455a767b4a498c1da74be094d4f`, escala
  56x80. O escopo é uma única pose idle/guard nativa em staging; não autoriza
  `res/`, animação completa, ROM, `visual_pass` ou AAA.
- O shootout contém fontes AI independentes 48x64
  `331ef5f4d0a16d8dee525229333c558fc0954c07b49a7ef2d7c46d606aa51301`, 56x80
  `32c5a8089c52251c0276eb0c28406b44e7797455a767b4a498c1da74be094d4f` e 64x96
  `b16e0cbebd5c4595ec875384476a8622cdafc5d3265160bdb71780265d613e8d`. Como
  mudam pose, anatomia e acabamento, são hipóteses direcionais e não isolamento
  puro de escala. Controles rejeitados não foram usados como fonte de pixels.
- O record operacional é `doc/art/characters/taina/native_scale_shootout_record_v01.json`;
  o record anterior do challenger B foi marcado `historical_superseded`.
  Requests 56x80 e 64x96 agora declaram suas próprias escalas, sem `sprite 48x64`.
- O budget atual é `planning_budget`, baseado nos footprints reais declarados:
  TAÍNA 56x80, CRIA 48x64 e ESTIVADOR 56x64. TAÍNA + 4 CRIAs = 22 links,
  10 sprites/scanline e 248 pixels/scanline; TAÍNA + 2 CRIAs + 2 ESTIVADORES =
  22 links, 10 sprites e 264 pixels/scanline; próximo stress 3 CRIAs + 3
  ESTIVADORES = 30 links, 14 sprites e 368 pixels/scanline, acima de 320. O
  fixture anterior com inimigos 32x48 foi invalidado e não entra no claim. Sem
  sprite nativo integrado e ROM observada, isso não é `validado_budget`.
- Próxima ação: autoria nativa direta 56x80 em ordem silhueta/volumes/materiais,
  depois paleta VDP. 64x96 só é fallback após duas iterações causais falharem;
  48x64 não é reaberto nesta rodada. `res/`, animação e ROM seguem bloqueados.

## 57. BLOCKER NATIVO REPRODUZIDO E BUDGET CORRIGIDO — 2026-08-31

- A rota autorizada foi tentada duas vezes: a primeira produziu checkerboard
  assado; a segunda produziu uma fonte RGB de alta resolução com leitura visual
  melhor, porém sem autoria de pixels no grid 56x80. O registro exato está em
  `rascunho/taina_native_authoring_56x80_v01/native_authoring_failure_report_v01.json`.
- A tradução assistida foi exercitada e parou corretamente em
  `blocked_pending_capable_producer`, sem inventar um PNG. GIMP só foi submetido
  a preflight batch, sem operações registradas; Aseprite não foi encontrado.
  Portanto o blocker atual é reproduzido após duas tentativas e substitui a
  formulação anterior de ausência de tentativa.
- Budget corrigido: TAÍNA 56x80 + 4 CRIAs 48x64 = 22 links, 10 sprites e 248
  pixels/scanline; composição + 2 CRIAs + 2 ESTIVADORES 56x64 = 22 links, 10
  sprites e 264 pixels/scanline; stress 3+3 = 30 links, 14 sprites e 368
  pixels/scanline. Estado: `planning_budget`, não `validado_budget`.
- Nenhuma evidência de candidato nativo foi fabricada. `res/`, animação,
  integração, ROM, `visual_pass` e AAA seguem bloqueados.

## 58. RECUPERAÇÃO DA ROTA NATIVA LOCAL E CANDIDATO 56x80 — 2026-08-31

- O blocker histórico foi preservado, mas superseded: a rota `editor_api_save` local
  foi exercitada com sessão 56x80, ações explícitas `pencil`/`eraser`/`fill`, restore,
  export PNG/log e validações negativas de path, `res/` e dimensões fora do grid.
  Self-check: 11/11.
- Foram produzidas quatro iterações causais em grid nativo: v01 SHA-256
  `7bfd7f57ec51f4a368917e7fc6e4655640ebae8cf4209ece219de14b3922aba8`, v02
  `23e1d3704797ba3c48306268d6e18f00dd4b3a3cfc870927ca40edfadbb6d404`, v03
  `2430a61f6f3c40b6cd26ed212215bc035f1bd76dffa9b2343316fa0eb7babc0c` e v04
  `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`.
  A v04 muda geometria, clusters de face/guarda e hierarquia de materiais; não é
  simples requantização da fonte 56x80 aprovada.
- O model sheet v02, SHA-256 `324951fb2c35da907229430ff128742a2cdb28632a098b1cb7b0c48c5c0cf87a`,
  continua sendo a fonte exclusiva de identidade. A fonte 56x80 aprovada,
  SHA-256 `32c5a8089c52251c0276eb0c28406b44e7797455a767b4a498c1da74be094d4f`,
  foi usada somente para direção e proporção. As três fontes do shootout mudam
  pose, anatomia e acabamento; não são comparação isolada de escala.
- O record operacional é
  `doc/art/characters/taina/native_authoring_route_recovery_record_v01.json`; o
  estado de recuperação é apontado por
  `doc/art/characters/taina/native_authoring_route_recovery_state_v01.json`.
  O shootout e o failure report anterior agora apontam para esse estado/record e
  não aparentam ser o estado vigente.
- v04 é P/4bpp 56x80, PLTE 16, índice 0 transparente, alpha binário e 15 cores
  visíveis. Evidências incluem 1x/2x/3x/nearest 8x, claro/escuro/chroma, silhueta,
  semantic/contour, materiais, crops, composição 320x224, comparação e reports.
  `native_visual` e `human` continuam em andamento; o pacote está pendente de gate
  humano e não é `visual_pass`.
- Budget continua `planning_budget`: quatro CRIAs = 22 links, pico 10 sprites e
  248 px/scanline; composição mista = 22/10/264; stress 3+3 = 30/14/368 e está
  fora do budget_pass. Sem res/ e ROM medida, não há `validado_budget`.
- Teto honesto: `native_candidate_pending_human_decision`; `res/`, animação,
  integração SGDK, ROM/BlastEm, `visual_pass`, ready_for_res e AAA continuam
  proibidos.

## 59. REJEIÇÃO HUMANA DA V04 — 2026-09-01

- A candidata `taina_idle_guard_56x80_native_authoring_v04`, SHA-256
  `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`, recebeu
  `technical_pass_visual_fail` e `human_rejected`.
- Motivos observáveis registrados: `anatomy_simplified_into_block_mass`,
  `face_or_eye_readability_lost`, `signature_feature_loss` e
  `generic_blocky_redraw`.
- A decisão está vinculada em
  `doc/art/characters/taina/human_native_pose_rejection_v01.json`. A v04 fica
  preservada como `technical_control_only`; não é fonte de pixels nem pose final.
- O record operacional permanece em `rework`: `pixel_contract`, escala e
  `material_topology` continuam tecnicamente válidos, enquanto
  `native_visual` e `human` estão falhos. 56x80 continua travado; 64x96 segue
  `comparison_only` e 48x64 não foi reaberto.
- Próximo trabalho autorizado: novo rework nativo causal em 56x80, sem promoção
  para `res/`, animação, integração SGDK, ROM, `visual_pass` ou AAA.

## 60. LABORATÓRIO DE ROTAS DE REDUÇÃO — 2026-09-01

- A decisão humana exata `rejected_requires_route_lab` foi registrada para v04 em
  `doc/art/characters/taina/human_native_pose_route_lab_rejection_v01.json`,
  vinculada ao SHA-256
  `0f0c758bd50fd41b028ad44f04a3c48e48faf1859f2b4e9769ca68621733800e`. v04 e
  v01-v03 permanecem apenas evidência negativa/controle técnico e são proibidos
  como fonte, baseline ou entrada de geração.
- A produção normal de TAÍNA foi pausada. O laboratório isolado operacional é
  `SGDK_projects/_agent_laboratory/TAINA_RESAMPLING_ROUTE_LAB [VER.001] [SGDK 211] [GEN] [LAB] [ART_TRANSLATION]`.
  Ele contém cópias locais, hashes e contratos; não escreve em `res/`.
- O experimento fixo separa identidade (model sheet v02), direção/proporção
  (fonte aprovada 56x80) e evidência negativa (v04). As três fontes do shootout
  alteram pose, anatomia e acabamento; portanto não foram tratadas como
  comparação isolada de escala.
- O laboratório executou probes mecânicos reproduzíveis, probes de paleta e dois
  guias de autoria nativa. Nenhum é pose final. O teto atual é
  `resampling_route_lab_evidence`; o gate humano de rota ainda está pendente.
- 56x80 continua travado; 64x96 é somente comparação. `res/`, animação,
  integração SGDK, ROM/BlastEm, `visual_pass`, `ready_for_res` e AAA seguem
  não autorizados.

## 61. SHOOTOUT DE LIMPEZA HÍBRIDA — 2026-09-01

- A decisão humana `approve_hybrid_cleanup_shootout` foi registrada em
  `doc/art/characters/taina/human_hybrid_cleanup_shootout_decision_v01.json`.
  Ela aprova somente o estudo híbrido em 56x80, com pixels das bases podendo
  sobreviver, mas com promoção cega explicitamente falsa.
- Bases aprovadas: `im_lanczos3` SHA-256
  `933caee8829970d0f8877712396b19b57e5843ef73481aceb047cf338cde72be`,
  `im_mitchell_netravali` SHA-256
  `ee524888bd0be4e146a3236a9480565772b8fa8e752818bf2c9717bf702b17b5` e
  `im_catmull_rom` SHA-256
  `169426ebbf40eb01631154610cd73fff959afde8540dfa5943c3528225b20cd5`.
- Foram produzidas três variantes de limpeza híbrida, cada uma com matte
  binário, paleta semântica e patches nativos explícitos. Todas permanecem
  `technical_candidate`/`human_gate_status=pending_human_decision`.
- Nenhuma variante foi promovida para `res/`, animação, runtime, ROM,
  `visual_pass` ou AAA; 56x80 continua travado e 64x96 continua somente
  comparação.

## 62. INCUMBENT HÍBRIDO SELECIONADO PARA REWORK LOCALIZADO — 2026-09-01

- A decisão humana selecionou `hybrid_cleanup_primary_im_lanczos3_v01`, SHA-256
  `3e60cd9efb233d0ce715c543e9cacdaacbe044b253c088dd06ada52f131b4cf1`, em
  56x80, com escopo exclusivo `localized_native_cleanup_only`.
- O rework gerado é
  `hybrid_cleanup_primary_im_lanczos3_rework_v01`, SHA-256
  `cb6ff5c695c5e7b76e80d84ebd497f8f55e162561c0f2caeb0f345604c31529e`.
  A intervenção removeu a faixa de sombra de chão assada entre os pés, removeu
  um pixel órfão do sash e aplicou separadores locais de rosto/guarda/sash.
- O candidato permanece `technical_candidate`, com validação pixel-strict
  independente e `human_gate_status=pending_human_decision`. Nenhuma promoção
  para `res/`, animação, runtime, ROM, `visual_pass` ou AAA ocorreu.

## 63. CORREÇÃO DE MÉTODO E REWORK ARTÍSTICO DA PRIMARY — 2026-09-01

- A revisão humana corrigiu a descrição da rota: `method=mechanical_palette_remap_with_minimal_native_patches`;
  `native_cleanup=incomplete`; `material_topology=not_run`; e
  `semantic_map=derived_diagnostic_not_independent`. O mapa semântico derivado
  diretamente do índice de paleta não é segmentação artística independente.
- A tentativa v02 de remapeamento amplo foi descartada como regressão visual:
  achatou pele, top, cabelo e calça em massas e não pode ser fonte, baseline ou
  candidata vigente. O registro está em `DISCARDED_VISUAL_REGRESSION.md` no
  laboratório.
- A v03 foi produzida somente sobre o controle v01 selecionado, preservando sua
  macrogeometria e registrando 44 patches não nulos nas regiões cabelo, rosto,
  guarda, top/abdômen, sash, calças e pés. Candidata vigente:
  `hybrid_cleanup_primary_im_lanczos3_rework_v03`, SHA-256
  `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`.
- O PNG passou o contrato técnico P/4bpp (56x80, 14 cores visíveis, PLTE 16,
  índice 0 transparente, sem blocker). A faixa central da linha 77 ficou com
  zero pixels visíveis; os pixels restantes são os dois intervalos de contato
  dos pés. Isso não prova `visual_pass`.
- O estado operacional aponta para v03 e permanece
  `technical_pass_visual_rework`, `human_gate_status=pending_human_decision`.
  `material_topology=not_run`; o mapa independente é só hipótese diagnóstica.
  Não houve promoção para `res/`, animação, runtime, ROM, `visual_pass` ou AAA.

## 64. V03 CONGELADA E V04 DE REWORK LOCALIZADO — 2026-09-01

- A decisão humana aprovou `hybrid_cleanup_primary_im_lanczos3_rework_v03`
  somente como checkpoint intermediário: `decision=approve_localized_native_cleanup`,
  SHA-256 `99160ec422010d2ac68fbb4b10cc03db72012316508882e1b9b8cf336ec51a33`,
  escala 56x80. A v03 é incumbent congelada, não `visual_pass` nem pose final.
- A v04 foi produzida somente sobre a v03, sem resize, filtro ou remapeamento
  global. Candidata atual:
  `hybrid_cleanup_primary_im_lanczos3_rework_v04`, SHA-256
  `791074aa6919ac0bac78a60693c12daee8f03169b216996758a8a272bc6b214e`.
  Foram registrados 36 patches não nulos em rosto, cabelo, guarda, abdômen,
  sash e calças.
- O mapa de materiais v04 atribui cada pixel visível a cabelo, pele, top, wraps,
  sash, calças, pés ou contorno compartilhado, independentemente do índice de
  paleta. O estado é `independent_candidate_pending_human_review`, não
  `material_topology=passed`.
- Estado atual: `technical_pass_visual_rework`, teto
  `localized_native_cleanup_candidate`, gate humano pendente. Próximo gate
  positivo separado: `approved_for_final_native_pose`. `res/`, animação,
  integração, ROM, `visual_pass` e AAA continuam bloqueados.

## 65. V05 DE REWORK LOCALIZADO — 2026-09-01

- A v04 foi rejeitada pela decisão humana somente como pose final e preservada
  como incumbent. A v05 atual foi produzida exclusivamente sobre ela, sem
  reabrir v03, v02, G2 ou rotas manuais rejeitadas.
- Candidata de laboratório:
  `hybrid_cleanup_primary_im_lanczos3_rework_v05`, SHA-256
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`, escala
  travada 56x80. Método honesto:
  `mechanical_palette_remap_with_minimal_native_patches`; `native_cleanup` é
  incompleto e `semantic_map` é diagnóstico derivado, não segmentação artística.
- Contratos materiais independentes foram produzidos para v04 e v05. A v05 tem
  cobertura geométrica exata e leakage de 505 ocorrências; logo
  `material_topology=failed_requires_localized_material_cleanup`.
- Validação técnica da v05: P/4bpp, 56x80, 15 cores visíveis, PLTE 16, índice 0
  transparente, alpha binário, sem blocker. Isso não é `visual_pass`.
- O estado operacional aponta para
  `doc/art/characters/taina/taina_localized_cleanup_operational_record_v05.json`
  e permanece `technical_pass_visual_rework`, `pending_human_decision`, com
  `res`, animação, SGDK, ROM, `visual_pass` e AAA falsos.
- O budget corrigido permanece `planning_budget`, usando footprints reais:
  TAÍNA 56x80 + quatro CRIA 48x64 = 22 links, pico 10 sprites e 248 pixels por
  scanline; 2 CRIA + 2 ESTIVADOR = 22 links, pico 10 e 264 pixels; 3 CRIA + 3
  ESTIVADOR = 30 links, pico 14 e 368 pixels, acima do limite H40 de 320.

## 66. MEDIDOR DE TOPOLOGIA V02 — 2026-09-01

- A v05 permanece incumbent visual de diagnóstico, sem alteração de pixels e
  sem v06. SHA-256 mantido:
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`.
- Corrigida a contagem do rework para 23 tentativas, 18 efetivas e 5 no-op em
  `cleanup_actions`, validation report, review index e registros operacionais.
- A topologia retangular deixou de ser canônica. O medidor usa mapa externo
  pixel-accurate, autorado contra v05/model sheet, com proprietários
  `outline_shared`, `hair`, `skin`, `orange_top`, `teal_fabric` e
  `indigo_trousers`, sem inferência por índice de paleta.
- Fixtures adversariais: 8/8. Rederivação: v04 ownership annotation error 4 /
  palette leakage 832; v05 ownership annotation error 0 / palette leakage 827.
  `ambiguous_requires_human_review` permanece verdadeiro; não há autorização
  para v06, patches, animação ou `res/`.

## 67. CONTRATO DE TOPOLOGIA V03 EM DUAS CAMADAS — 2026-09-01

- A v05 continua congelada como controle visual diagnóstico, sem alteração de
  pixels e sem v06. SHA-256 confirmado:
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`.
- O medidor agora persiste e relê
  `material_owner_shade_annotation_v01.json`: `material_owner_map` contém
  somente transparent, hair, skin, orange_top, teal_fabric e
  indigo_trousers; `shade_role_map` contém outline_shared,
  deep_shadow_shared, shadow, base e highlight. Não existe fallback para skin.
  Pés são skin; wraps e sash são sub-regiões semânticas de teal_fabric; os
  papéis compartilhados são autorizados por coordenadas explícitas.
- A matriz `owner × index × shade_role`, PLTE RGB 0–15, leakage completo por
  material, índice e componente conectado, overlays e comparação com o mapa
  legado foram persistidos e vinculados ao SHA da v05.
- A medição v03 separa os quatro eixos: `material_map_accuracy=passed`,
  `material_boundary_topology=passed`, `palette_role_conformance=failed` e
  `visual_material_readability=pending_human_review`. A anotação tem cobertura
  geométrica exata e zero `unassigned_visible_pixel`, mas isso não é aprovação.
- Leakage confiável: 829 pixels em 44 componentes conectados; leakage histórico
  do mapa legado com fallback: 827. A diferença é diagnóstica e não autoriza
  829 patches. Fixtures semânticas permanentes: 10/10.
- Como os conflitos atravessam interiores de cabelo, pele, top, teal e calças,
  a decisão de rota foi abrir `material_palette_reseed_v01` em staging, mantendo
  a v05 como controle. BASIC e ELITE foram produzidos por
  `material_owner + shade_role`, sem nearest-color ou remapeamento global, e
  foram rejeitados como challengers visuais. BASIC SHA-256
  `24bee2d802e9bda6cbbabd43637220b5c2c99b1d66ebdeba21fd24205fedd33a`; ELITE
  SHA-256 `753815ea994859cc52c35e701a505258cbb141896b44717fb7f8239aeb415f9b`.
- Estado honesto permanece `pending_human_decision`,
  `native_cleanup=incomplete`, `material_topology=failed_requires_localized_material_cleanup`,
  `visual_pass=false`, `res_promotion=false`, `animation_authorization=false`,
  `rom_authorization=false` e `ready_for_aaa=false`. Nenhuma autorização para
  pose final foi solicitada.

## 68. REJEIÇÃO HUMANA DO RESEED DE PALETA — 2026-09-01

- Decisão exata: `reject_material_palette_reseed_as_visual_challengers`.
  Motivo: `semantic_flattening_destroyed_internal_drawing_and_identity`.
- BASIC e ELITE permanecem apenas como evidência rejeitada. A decisão registra
  `basic_elite_changed_pixels=4` e `basic_elite_changed_ratio=0.00271`; esses
  valores não são score de qualidade.
- A v05 continua controle congelado em 56x80, SHA-256
  `6ef8528a91f8cc32e15af5ce8c3e404a37e57927adb0be74f1298b106e7600d3`. Não há
  autorização para nova arte, `res/`, animação, ROM, `visual_pass` ou AAA.
- A classificação dos challengers é `method=diagnostic_semantic_color_blocking`,
  `acceptance_status=visual_lab_control`, `promotable=false` e
  `allowed_as_pixel_source=false`.

## 69. BLOCKING NATIVO 56x80 — GATE HUMANO A/B — 2026-09-01

- A decisão humana `reject_material_palette_reseed_as_visual_challengers` foi
  preservada com os SHA BASIC `24bee2d802e9bda6cbbabd43637220b5c2c99b1d66ebdeba21fd24205fedd33a`
  e ELITE `753815ea994859cc52c35e701a505258cbb141896b44717fb7f8239aeb415f9b`.
  Ambos são apenas `visual_lab_control` e não são fonte de pixels.
- Foram tentadas três passagens de lineart blocking em staging. v01 e v02
  foram descartadas por leitura observável de massa genérica/guarda ambígua.
  A v03 vigente usa o model sheet v02 como autoridade de identidade e os
  underlays apenas como guias; não usa pixels de v05, G2, RGB maps ou reseed.
- A candidata A é `taina_56x80_native_lineart_blocking_a_v03`, SHA-256
  `cd911846f1eab6f05e59be714fdf0520a021ea88b9fdc008f2279112133c10ff`.
  A candidata B é `taina_56x80_native_lineart_blocking_b_v03`, SHA-256
  `2783c59c6c26e645825295d570c70d2a1ea01be1580fa02c306e35017e045264`.
  A/B diferem em 93 pixels de 1678 visíveis e em face, cabelo, guarda, hem,
  sash e pés; isso não é score estético.
- A etapa permanece `pending_human_decision`, `visual_pass=false`,
  `promotable=false`, `res_promotion=false`, `animation_authorization=false`,
  `rom_authorization=false` e `ready_for_aaa=false`. Não há autorização para
  materiais finais, animação, `res/`, SGDK, ROM ou claim AAA.
- O budget que já havia sido corrigido continua `planning_budget` e não foi
  promovido por estas linearts: TAÍNA 56x80 + quatro CRIA 48x64 = 22 links,
  pico 10 sprites/scanline e 248 pixels; 2 CRIA + 2 ESTIVADOR = 22 links,
  264 pixels; 3 CRIA + 3 ESTIVADOR = 30 links e 368 pixels, acima do H40.
