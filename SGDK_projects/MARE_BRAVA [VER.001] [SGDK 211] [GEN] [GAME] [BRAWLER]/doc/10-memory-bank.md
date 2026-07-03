<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `herdada_do_template_2026-06-03` (STALE — sera regenerada no primeiro build deste projeto)
- Changelog canonico: `doc/changelog/changelog.md`
- AVISO: o bloco acima do template descrevia builds do projeto-modelo (`build_v001/v002`), que NAO existem neste projeto. `out/` foi removido no nascimento (Vibe Playable). Nenhuma ROM, evidencia ou runtime_metrics deste projeto existe ainda.
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker — MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]

**Ultima atualizacao:** 2026-07-03 (sessao 2)
**Fase atual:** FASES 1-3 concluídas — GDD + cadeia completa de contratos (TDD, brawler design, mechanic, level, enemy, frame data) validada, direção de arte congelada (`angular_cps2_fighter`) e PRDs em seed. Status geral: `documentado`. Geração de premium source BLOQUEADA por ausência de canal (ver abaixo).
**Proxima fase:** habilitar canal de geração (instalar ComfyUI `deck_safe_sd15` OU fornecer API key OU gerar em host com canal nativo) → gerar premium source do CAIS_01 → aprovação humana → FASE 4 (laudo VDP budget).

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- FASE 2 completa (2026-07-03): `doc/contracts/tdd_contract.json` (FSM, pools, DMA ownership, NTSC-first, tecnicas com registry) + `doc/contracts/brawler_belt_scroll_design_contract.json` (roster TAINA/JACO, 6 arquetipos com frame data, 3 stages com boss, combat/balance) + `mechanic_contract.json` (combo_de_mare), `level_blueprint.json` (cais_01), `enemy_roster.json`. TODOS 100% validos nos schemas; `audit_game_design_contracts`: passed, blockers=0; `validate_brawler_belt_scroll_specialization`: passed=11 failed=0.
- FASE 3 (direção): `doc/art/` com art_direction_decision_record (angular_cps2_fighter, confianca 0.70), concept_art_direction_brief, master_style_manifest, moodboard_manifest, brand_identity_manifest (planned), style_drift_policy, art_asset_diagnostic (rota 3_no_art), art_generation_brief.md pronto para disparo.
- 16 PRDs materializados (art bible, palette master, benchmark, rom mastering, ci, code review etc.); `check_prd_readiness`: ok, blockers=0 (target prototype).
- Validadores canonicos todos verdes: contexto, metodologia, higiene (corrigido caminho F:\ herdado do template em scene-contracts.json).
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
- Receita completa na memória do agente do workspace; pontos-chave: symlink sem espaços para o SDK, `LIBGCC=<gdk>/lib/libgcc.a` no make, symlink `/mnt/sdcard/tmp -> /tmp`, fonte Arial registrada no prefixo Wine para o BlastEm.
- Guard de ambiente roda com `pwsh` + `USERPROFILE=$HOME` + shim `powershell→pwsh`; Graphify com `-SkipGraphify` até o fix de `Get-Item -Force`.

---

## 2. O QUE ACABOU DE ACONTECER

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

- CANAL DE GERAÇÃO (decisão humana): instalar ComfyUI `deck_safe_sd15` neste host (4.2GB, qualidade SD1.5 exige revisão) OU fornecer API key externa OU rodar geração em host com canal nativo.
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
