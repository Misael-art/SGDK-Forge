# Sector 01 Closeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remover os blockers tecnicos do Sector 01, provar sucesso e falha no BlastEm e emitir o gate que autoriza as proximas etapas de producao.

**Architecture:** O fluxo normal do jogo permanece Branding -> Title -> Opening -> Race -> Result. Instrumentacao QA fica isolada em bootstrap SRAM `SBIS` e probe `MDRT`; reports do host apenas interpretam dados produzidos pela ROM e artefatos do mesmo hash.

**Tech Stack:** C SGDK 2.11, RESCOMP, PowerShell wrapper central, Python unittest, BlastEm, SRAM.

---

### Task 1: Road and WINDOW contracts

**Files:**
- Modify: `tools/test_sector01_recovery_contracts.ps1`
- Modify: `tools/tests/test_sector01_recovery.py`
- Modify: `src/race/road_renderer.c`
- Modify: `src/race/race_hud.c`

- [ ] Add assertions that every generated road tilemap entry uses
  `TILE_ATTR_FULL(PAL2, ...)` and that `Hud_init` calls
  `VDP_setWindowOnTop(3)`.
- [ ] Run both regression suites and verify the new assertions fail for the
  intended reason.
- [ ] Encode complete tile attributes in `fill_sky`, `fill_road` and the
  default map fill; give `Hud_init` explicit WINDOW ownership.
- [ ] Run both suites and verify this task is green.

### Task 2: Success/failure semantics and safe metrics

**Files:**
- Modify: `tools/test_sector01_recovery_contracts.ps1`
- Modify: `tools/tests/test_sector01_recovery.py`
- Modify: `inc/race/race_metrics.h`
- Modify: `src/race/race_metrics.c`
- Modify: `src/scenes/race_scene.c`
- Modify: `src/scenes/result_scene.c`

- [ ] Add assertions for `u32 pressure_sum`, persisted `sector_cleared`, result
  labels for both outcomes and the result transition payload.
- [ ] Run both suites and observe failure.
- [ ] Extend `MetricsReport` and `Metrics_raceComplete` with
  `bool sector_cleared`; persist it in the MTR block without changing MDRT.
- [ ] Pass `race_state == RSTATE_CLEAR` at race completion and render
  `SECTOR 01 COMPLETE` or `SECTOR 01 FAILED`.
- [ ] Run both suites and verify green.

### Task 3: Canonical scene contracts

**Files:**
- Modify: `doc/13-spec-cenas.md`
- Modify: `doc/scene-regression.json`
- Regenerate: `doc/scene-contracts.json`

- [ ] Add a regression that requires at least the implemented
  Branding/Title/Opening/Race/Result/Credits scenes in compiled contracts.
- [ ] Convert scene headings to the compiler-supported `### Cena N -
  \`scene_id\`` format while preserving prose.
- [ ] Correct `app_scene_id` mappings to the actual `SceneId` enum.
- [ ] Run compiler and lint; verify nonzero scene count and no blocking lint.

### Task 4: QA-only SBIS bootstrap

**Files:**
- Create: `inc/system/qa_bootstrap.h`
- Create: `src/system/qa_bootstrap.c`
- Modify: `src/main.c`
- Modify: `tools/tests/test_sector01_recovery.py`

- [ ] Add source-level and payload-fixture tests for magic `SBIS`, schema 1,
  size 12, checksum and normal-boot fallback.
- [ ] Run tests and observe failure.
- [ ] Read and validate the SRAM payload at `0x120` before `SM_init`; clear
  consumed magic and select only a valid `SceneId`.
- [ ] Keep Branding as the default for missing/invalid payload.
- [ ] Build and run bootstrap parser fixtures.

### Task 5: Canonical MDRT runtime probe

**Files:**
- Create: `inc/system/runtime_probe.h`
- Create: `src/system/runtime_probe.c`
- Modify: `src/main.c`
- Modify: `src/scenes/race_scene.c`
- Modify: `tools/tests/test_sector01_recovery.py`

- [ ] Add tests for `g_mdRuntimeProbe`, `MDRT`, `SYS_getCPULoad`,
  `SPR_getUsedVDPSprite`, scene id and SRAM offset `0x200`.
- [ ] Run tests and observe failure.
- [ ] Adapt the canonical probe from the workspace fixture, recording at least
  1800 samples without heap allocation.
- [ ] Tick once per frame and publish to SRAM at deterministic intervals and
  scene completion.
- [ ] Parse a synthetic and a real SRAM through
  `parse_blastem_sram_runtime.ps1`.

### Task 6: Canonical BlastEm transport

**Files:**
- Modify only if required:
  `tools/sgdk_wrapper/lib/blastem_automation.psm1`
- Test:
  `tools/sgdk_wrapper/ci/test_*blastem*.ps1`

- [ ] Reproduce foreground failure with a minimal canonical session and record
  target HWND, foreground HWND/PID/thread and Win32 return values.
- [ ] Add a wrapper CI regression that fails under the reproduced condition.
- [ ] Implement one canonical foreground/input path and remove any silent
  fallback.
- [ ] Prove `INP.observed_input != 0` in fresh SRAM.

### Task 7: Runtime routes and screenshots

**Files:**
- Create: `doc/blastem_sector01_success_input.json`
- Create: `doc/blastem_sector01_failure_input.json`
- Generate under: `out/evidence/sector01_vNNN/`

- [ ] Validate input scripts against
  `blastem_input_script.schema.json`.
- [ ] Capture Title and opening.
- [ ] Capture race start, jump, pursuer, Pressure Gate, Pulse, race midpoint
  and Beacon.
- [ ] Capture success result and returned Title.
- [ ] Capture a separate failure result and returned Title.
- [ ] Decode SRAM and assert scene sequence, observed input, success/failure
  bit and same ROM hash.

### Task 8: Hardware reports

**Files:**
- Generate: `out/logs/scene_tilemap_conversion_report.json`
- Generate: `out/logs/per_tile_palette_conflict_report.json`
- Generate: `doc/vram_residency_report.json`
- Generate: `out/logs/sprite_scanline_pressure_report.json`
- Generate: `out/logs/palette_slot_audit.json`

- [ ] Measure road tileset/map and create schema-valid conversion report.
- [ ] Audit each tile palette domain and require zero errors.
- [ ] Bind VRAM evidence to the current ROM and resource hashes.
- [ ] Simulate worst scanline with player, hazards, pickups and pursuer.
- [ ] Audit PAL0-PAL3 ownership and index 0 transparency.
- [ ] Run res graph and scene budget; apply required recuo before final build.

### Task 9: Final build and gates

**Files:**
- Update: `doc/code_review_report.json`
- Update: `doc/local_ci_gate_report.json`
- Update: `doc/rom_mastering_report.json`
- Update: `doc/scene_closeout_report.json`
- Update: `doc/10-memory-bank.md`
- Update: `doc/changelog/changelog.md`

- [ ] Run complete regression suites.
- [ ] Build once through the central wrapper with a declared blocker target.
- [ ] Freeze ROM hash and recapture all evidence.
- [ ] Run validation, freshness, budget, code review, mastering, local CI and
  `scene_closeout_gate.ps1`.
- [ ] Seal evidence with `finalize_emulator_evidence.ps1`.
- [ ] Set Sector 01 to `testado_em_emulador` and `validado_budget` only when
  reports prove both.
- [ ] Emit a production authorization record for definitive art, audio,
  Upgrade Intermission and Sector 02 without starting those scopes.
