<!-- SGDK GENERATED STATUS START -->
## 0. Estado Derivado dos Artefatos

- Fonte: `doc/changelog` + `validation_report.json`
- Ultima sincronizacao: `2026-06-06T23:43:37.7179979-03:00`
- Changelog canonico: `doc/changelog/changelog.md`
- Assets versionados rastreados: 6
- Ultimo build versionado: build_v003
- ROM vigente: `18aec2f55902aa572a7c49fbc15de27c2e2c8e8ad2f2693a691537f1289459ae` (`262144` bytes)
- Validation summary: errors=0 warnings=10
- Blockers vigentes: project_naming_invalid, project_methodology_manifest_invalid, gdd_substantial_insufficient, agent_context_degraded, visual_gate_blocked, visual_delivery_gate_missing, audio_validation_missing, freshness_audit_missing, scene_closeout_gate_missing
- Evidencia de emulador: sem_sessao
- Gate visual: visual_lab_aprovado=False
- Gate gameplay: gameplay_rom_aprovada=False
- Gate AAA: ready_for_aaa=False
- QA runtime: gameplay=nao_testado performance=nao_testado audio=nao_testado hardware_real=nao_testado
<!-- SGDK GENERATED STATUS END -->
# 10 - Memory Bank & Context Tracker ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â SCENE_TILEMAP_CURATION_FIXTURE

**Ultima atualizacao:** 2026-06-03
**Fase atual:** Branding sequence buildada e observada no BlastEm, com closeout bloqueado
**Proxima fase:** Rework visual, visual_vdp_dump e investigacao do pico CPU em runtime_metrics

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

- ROM vigente: `out/rom.bin`, build_v002, SHA256 `22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f`
- `validation_report.json`: errors=0, warnings ativos
- `runtime_metrics.json`: presente, scene_id=0, capture_status=partial, over_budget_frames=1
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
- Build wrapper gerou `out/rom.bin` build_v002, SHA256 `22a80b7cf9f514550f21073226c2bec63efdcc6a95af9d18c62d5e810ce95c8f`.
- Captura BlastEm `TargetScene=0` gerou `screenshot.png`, `save.sram`, `runtime_metrics.json` e `emulator_session.json`.
- `runtime_metrics.json` confirmou cena 0, 32 amostras, p95=6, 0 sprites, mas manteve 1 pico de CPU; performance segue bloqueada.
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








