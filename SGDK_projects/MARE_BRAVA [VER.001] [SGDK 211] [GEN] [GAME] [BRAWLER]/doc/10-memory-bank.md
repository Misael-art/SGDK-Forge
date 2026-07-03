<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `herdada_do_template_2026-06-03` (STALE — sera regenerada no primeiro build deste projeto)
- Changelog canonico: `doc/changelog/changelog.md`
- AVISO: o bloco acima do template descrevia builds do projeto-modelo (`build_v001/v002`), que NAO existem neste projeto. `out/` foi removido no nascimento (Vibe Playable). Nenhuma ROM, evidencia ou runtime_metrics deste projeto existe ainda.
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker — MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

**Ultima atualizacao:** 2026-07-03 (sessao 5 — correcao level-art modular do CAIS_01)
**Fase atual:** `pre_producao_documentada_com_template_tecnico` (vocabulário do parecer 2026-07-03). NÃO é protótipo, NÃO é vertical slice, NÃO é jogo. Bloqueios curatoriais tratados: slice scope contract (anti-falso-verde), streaming do cais contratado, direção de arte com trio MD-nativo e RATIFICAÇÃO HUMANA PENDENTE, rota de arte corrigida para concept-first, e agora rota do CAIS corrigida para `dock_scene_kit` modular + montagem autoral pelo agente. Painéis prontos do cais ficam `mood_reference_only`, não fonte de produção.
**Proxima fase:** gerar/curar `dock_scene_kit` modular conforme `doc/contracts/level_art_assembly_contract.json` → montar `world_layout_board` 1344x224 pelo agente (object placement + parallax + ecology + collision visual) → ratificação humana do board/contact sheet → model sheet pixel autoral 3.5 heads (TAÍNA primeiro) → lineart 1px → key poses → strips → conversão VDP + laudo de budget. RUNTIME SÓ DEPOIS.

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

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

- Todos os assets de gameplay: NENHUMA arte de TAÍNA, inimigos ou cais existe (`blocked_no_premium_source`).
- Branding herdada usa logos do template; precisará de art pass com a identidade MARÉ BRAVA.
- Áudio: nenhuma música/SFX do projeto; direção declarada no GDD apenas.

### O que falta para o slice ser completo

- CANAL DE GERAÇÃO (blocker ativo): `out/logs/generation_channel_decision.json` = bloqueado. Sem callable nativo, sem API key no host, Bonsai exige NVIDIA (host é AMD VanGogh), ComfyUI local não instalado. Opções: instalar perfil `deck_safe_sd15` (download 4.2GB, qualidade exige revisão humana) ou fornecer API externa.
- Gerar premium source do CAIS_01 conforme `doc/art/art_generation_brief.md` + aprovação humana + conversão VDP.
- FASE 4: laudo `megadrive-vdp-budget-analyst` do CAIS_01.
- FASE 5: runtime C (FSM, combate, wave manager, câmera, HUD, XGM2).
- FASE 6: build + BlastEm + evidência (screenshot + save.sram MDRT + runtime_metrics 60fps).

### Snapshot dos gates QA

- visual_lab_aprovado: false (sem arte)
- gameplay_rom_aprovada: false (sem ROM)
- ready_for_aaa: false
- freshness_audit: nao_executado neste projeto
- scene_closeout_gate: nao_aplicavel ainda

### Ambiente de producao (host)

- Host atual: Manjaro Linux. Loop build→BlastEm foi PROVADO neste host em 2026-07-03 usando SMOKE_TEST (toolchain Windows do SDK via Wine/binfmt + binutils m68k nativos; BlastEm sob Wine a 59.8 fps com screenshot interno e save.sram).
- Receita completa na memória do agente do workspace; pontos-chave: symlink sem espaços para o SDK, `LIBGCC=<gdk>/lib/libgcc.a` no make, symlink `tmp` na raiz do cartão SD apontando para o tmp do sistema, fonte Arial registrada no prefixo Wine para o BlastEm.
- Guard de ambiente roda com `pwsh` + `USERPROFILE=$HOME` + shim `powershell→pwsh`; Graphify com `-SkipGraphify` até o fix de `Get-Item -Force`.

---

## 2. O QUE ACABOU DE ACONTECER

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
- Canal de geração de imagem BLOQUEADO no host (sem nativo/API; Bonsai exige NVIDIA; ComfyUI não instalado) — brief de geração pronto em `doc/art/art_generation_brief.md`.
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

- build/rebuild canonico: nao_executado (sem runtime ainda — correto para FASE 1)
- contratos recompilados: nao_aplicavel
- grafo de recursos: nao_aplicavel
- validator: project_context ok (blockers=0)
- captura BlastEm: nao_aplicavel (sem ROM do projeto)
- regressao de cena: nao_aplicavel
- freshness audit: pendente para proxima fase
- closeout gate: nao_aplicavel

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
