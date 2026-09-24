<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-09-09T13:18:00-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 6
- Ultimo build versionado: build_v003
- ROM vigente: `0866208ba8d3fcd12cee5038b47491fb3cc2176352a4d66ddc88d78c28cdacac` (`262144` bytes)
- Validation summary: errors=4 warnings=15
- Blockers vigentes: project_naming_invalid, project_methodology_manifest_invalid, external_path_reference_outside_project, gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, procedural_fallback_as_final, visual_direction_failed, emulator_evidence_stale, freshness_audit_stale, scene_closeout_gate_stale
- Evidencia de emulador: `blastem-linux-20260909T160124Z-2601036`, BlastEm Flatpak Linux, sealed
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=observado_scene2 performance=unproven audio=dummy hardware_real=blastem_linux_flatpak
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â SCENE_TILEMAP_CURATION_FIXTURE

**Ultima atualizacao:** 2026-09-09
**Fase atual:** Runtime probe canônico buildado e observado no BlastEm Linux, com closeout bloqueado
**Proxima fase:** Reauthored visual final, cena 3 observada e prova de performance/audio sustentados

> **DIRETRIZ:** Este e o bloco de memoria primario do projeto.
> Leia integralmente antes de qualquer codigo ou decisao.
> Atualize ao encerrar sessoes relevantes.

---

## 1. ESTADO ATUAL DO PROJETO

### O que existe e funciona

- `APP_SCENE_BRANDING` e a primeira cena do modelo canonico.
- A cena usa cinco `IMAGE` reais em `res/branding/` declarados em `res/resources.res`.
- O baseline atual usa BG_A/B, scroll, HScroll line no slot project, palette cycling e skip por START/A.
- O runtime probe canonico existe e foi integrado ao boot/loop para gerar MDRT/READY em SRAM durante captura.
- A rota de audio foi corrigida para WAV XGM2 13300/6650 em vez de PCM bruto 11k.

### O que e placeholder

- A direcao sonora e funcional/sintetica, ainda nao e sample premium final.
- O cursor textual do slot author e efeito temporario em BG_A; nao deve ser vendido como visual AAA isolado.
- Monograma 3D/sprites complexos continuam fora do baseline ate novo asset pass e novo budget.

### O que falta para o slice ser completo

- Gerar `visual_vdp_dump.bin` ou atualizar formalmente o gate para aceitar MDRT+screenshot sem dump VDP.
- Resolver o pico isolado de CPU em `runtime_metrics.json` (`frame_index=128`, `cpu_load_ratio=401`) antes de declarar 60 FPS estavel.
- Resolver ou registrar explicitamente o rework visual apontado para `brand_author_logo.png`.
- Fechar o drift local de `.agent` e o GDD generico se o alvo for `ready_for_aaa`.

### Snapshot dos gates QA

- visual_lab_aprovado: false
- gameplay_rom_aprovada: false
- ready_for_aaa: false
- freshness_audit: ok
- scene_closeout_gate: blocked

### Blockers QA ativos

- `.agent` local teve caminhos ausentes materializados, mas segue com drift em `ARCHITECTURE.md` e `framework_manifest.json`.
- `doc/11-gdd.md` e generico; nao sustenta `ready_for_aaa` de projeto completo.
- `visual_aesthetic_report.json` marca `brand_author_logo.png` como `rework` e outros slots como `needs_review`.
- `visual_vdp_dump.bin` ainda nao existe em `out/evidence/blastem/`.
- Runtime probe registrou cena 0 no BlastEm, mas com captura parcial e um pico de CPU; budget segue nao validado.

### Metricas de codigo

- Branding baseline: 5 `IMAGE`, 5 `WAV XGM2`, 0 sprites runtime no baseline.
- `res_graph_report.json` passou com 10 declaracoes e 0 overlaps VRAM.
- Audio XGM2: maximo planejado de 2 PCM simultaneos, PSG ch0-ch2 como reforco tonal, PSG noise nao usado como canal tonal.
- `validate_audio.ps1` passou com 5 WAV XGM2 e estimativa de 29,97 KB (0,73% de 4096 KB).

### Estado de evidencia canonica

- ROM vigente: `out/rom.bin`, build pós-F01, SHA256 `0866208ba8d3fcd12cee5038b47491fb3cc2176352a4d66ddc88d78c28cdacac`
- `validation_report.json`: errors=4, warnings=15; blockers estruturais e visuais permanecem
- `runtime_metrics.json`: presente na sessão selada, scene_id=2, 32 amostras, 0 sprites/scanline, over_budget_frames=0, performance unproven
- `scene_regression_report.json`: ausente
- `emulator_session.json`: presente, BlastEm status ok, target_scene_match=true
- `freshness_audit_report.json`: presente, status ok
- `scene_closeout_gate_report.json`: presente com status blocked

---

## 2. O QUE ACABOU DE ACONTECER

**2026-05-24 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Branding intro AAA v1 com assets nativos e VDP**

- Criado builder deterministico `tools/image-tools/build_branding_intro_assets.py` para transformar fontes nativas em PNGs SGDK-safe: `brand_engine_logo`, `brand_author_logo`, `brand_project_logo`, `brand_presents_text` e `brand_fx_tiles`.
- `SCENE_branding` deixou de ser placeholder textual e passou a usar `IMAGE` real via `VDP_drawImageEx`, fundo de tiles FX, shimmer/pulse de paleta, PSG procedural e FSM engine/author/project.
- ROM direta SGDK buildada em `tools/sgdk_wrapper/modelo/out/rom.bin`; SHA256 `D012A842ADE368E25AE739F1DBB8A87F1DEAEDBE3799F407D24C2C4B170FD734`.
- Evidencia visual capturada no BlastEm para a mesma ROM final:
  - engine: `out/evidence/blastem_brand_intro_engine_final_rom/screenshot.png`
  - author: `out/evidence/blastem_brand_intro_author_final_rom/screenshot.png`
  - project/presents: `out/evidence/blastem_brand_intro_project_present_final/screenshot.png`
- `res_graph_audit.ps1` passou com status `warn` apenas por exigir evidencia VDP runtime para tiles carregados por codigo. O wrapper canonico ainda fica preso em `validate_resources.ps1`/gate `.agent` degradado; nao promover para closeout final ate corrigir esse gate.

**2026-06-03 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Fase 0 branding, XGM2 e runtime probe**

- Validado que os 5 PNGs atuais de `res/branding/` nao sao vazios e devem ser preservados como baseline.
- `branding_sequence_contract.json` foi expandido com `resource_plan_by_slot`, `palette_script`, `audio_cue_map`, `budget_summary`, teardown e `evidence_plan`.
- `scene-regression.json` e `doc/13-spec-cenas.md` passaram a registrar `branding_sequence` como cena formal com `app_scene_id=0`.
- `runtime_probe` foi integrado ao boot/loop para permitir `save.sram` com MDRT e heartbeat READY.
- Audio de branding passou a usar WAV XGM2 declarado em `.res`; PCM bruto 11k foi rejeitado como rota.
- Fixture de tilemap: `img_fixture_scene_tilemap` (320x224) declarado em `res/resources.res`, com reports de conversao/dedup/flags/conflicts gerados em `out/logs/`.
- Build wrapper gerou `out/rom.bin` pós-F01, SHA256 `0866208ba8d3fcd12cee5038b47491fb3cc2176352a4d66ddc88d78c28cdacac`.
- Captura Linux/BlastEm `target_scene=3` gerou screenshot, SRAM, manifest sealed e `visual_vdp_dump.bin` real.
- `runtime_metrics.json` confirmou cena 2, 32 amostras, 0 sprites/scanline e 0 frames acima do budget; o alvo 3 e performance sustentada seguem não provados.
- `scene_closeout_gate_report.json` fechou como `blocked`, nao como pronto.

---

## 3. DECISOES PENDENTES

- Decidir se o drift local de `.agent/ARCHITECTURE.md` e `.agent/framework_manifest.json` deve ser substituido pela canonica ou mantido como copia local auditada.
- Fazer novo art pass em `brand_author_logo.png` se o objetivo for remover `visual_gate_blocked`.
- Decidir se `visual_vdp_dump.bin` sera obrigatorio para este template ou se MDRT+screenshot sera aceito como evidencia canonica V2.

---

## 4. DECISION LOG CONSERVADOR

Registre aqui escolhas que evitaram tentativa-e-erro ou mudanca de rota.

| Data | Contexto | Escolha | Alternativas recusadas | Evidencia | Proximo gate |
|------|----------|---------|------------------------|-----------|--------------|
| 2026-06-03 | Branding baseline | Preservar `brand_*` atuais e adicionar audio XGM2 funcional | Apagar PNGs por suposicao; PCM bruto 11k | `res/resources.res`, `branding_sequence_contract.json` | build + validate_audio |
| 2026-06-03 | Runtime evidence | Integrar `MDRuntimeProbe` em boot/loop | Prometer runtime_metrics sem fonte ROM-side | `src/core/app.c`, `src/main.c` | BlastEm TargetScene=0 |
| 2026-06-03 | Runtime budget | Manter status bloqueado apesar de BlastEm OK | Declarar 60 FPS com `capture_status=partial` e pico CPU | `out/logs/runtime_metrics.json` | investigar frame_index 128 |

---

## 5. ROTEIRO DE FECHAMENTO

- build/rebuild canonico: ok (`out/rom.bin`, build_v002)
- contratos recompilados: ok
- grafo de recursos: ok
- validator: ok com warnings/bloqueios
- captura BlastEm: ok para boot/cena 0, parcial para performance
- regressao de cena: nao executada nesta rodada
- freshness audit: ok
- closeout gate: blocked

---

## 6. REFERENCIAS RAPIDAS

- GDD: `doc/11-gdd.md`
- Spec cenas: `doc/13-spec-cenas.md`
- Diretrizes agente: `doc/00-diretrizes-agente.md`
- Plano de provas QA: `doc/14-plano-de-provas-qa.md`

## 7. F01 — Merge do runtime probe canônico e evidência Linux

- Decisão registrada em `doc/runtime_probe_f01_merge_decision_20260909.json`: merge canônico preservando a ABI local de `gApp.currentScene`, o offset MDRT/heartbeat e os buffers estáticos do fixture.
- `inc/system/runtime_probe.h` e `src/system/runtime_probe.c` agora coincidem byte a byte com `tools/sgdk_wrapper/modelo/`: hashes `9ae8055f...bffed` e `9c6d905c...c2e1e`.
- Build observado pelo `linux_wine_bridge`; ROM antes `18aec2f5...9459ae`, ROM após `0866208b...cdacac`, 262144 bytes.
- Captura exclusiva Linux/BlastEm Flatpak: `out/evidence/runtime_probe_f01/blastem-linux-20260909T160124Z-2601036/`.
- Manifest sealed, screenshot semantically accepted, `save.sram` 32768 bytes, `visual_vdp_dump.bin` real de 200 bytes, freshness da sessão `ok`, emulator commit `c1f3f443...602221`.
- Runtime observado: `scene_id=2` apesar do alvo solicitado 3, 32 amostras, 0 sprites/scanline, 0 frames acima do budget, snapshot 59.9 fps. Isso prova somente boot/cena 2 e contrato de instrumentação; não prova cena 3, performance sustentada, qualidade visual ou áudio audível.
- Validator pós-build: 4 erros e 15 warnings; fixture segue laboratório e sem claim AAA.
- `out/logs/runtime_probe_f01_build_observation.json`, `runtime_metrics.json`, `performance_capture_report.json`, `emulator_session.json`, `visual_delivery_gate_report.json`, `claim_reconciliation_report.json` e `doc_sync_report.json` foram reconciliados ao mesmo hash/sessão; freshness final pode manter o próprio `validation_report` como stale por ter sido gerado antes deste fechamento.








