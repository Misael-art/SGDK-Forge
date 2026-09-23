# AAA Video Curation — Final Review (2026-06-16)

Closeout review of the Mega Drive AAA video-curation package after Phases 1–6.
This is a review document; it does not promote any runtime, ROM, build or visual
status.

## Global status

- `validate_aaa_video_curation.ps1` = **PASSED**
- `assert_agent_environment.ps1` = **agent_environment_status=ready**
- Global curation status = **candidate_applied_not_verified** — unchanged,
  because commit/push and ROM/emulator evidence do not exist yet.

## Phases completed

- **Phase 1** — Sanitization/validation: fixed evidence backlog, curation
  records, proficiency matrix; validator first reached PASSED.
- **Phase 2** — Framework/manifest sync: runner state updated (restored,
  validator PASSED) while keeping commit/push and ready_for_aaa false; framework
  manifest tracks the curated skills, workflows and schemas.
- **Phase 3** — Registered `curation_batch_2026_06_16` (aggregate plan +
  character-proportion direct text analysis) without promoting summary to proof.
- **Phase 4A** — Conservative updates to existing character/animation/pixel
  skills (character-design, sprite-animation, megadrive-pixel-strict-rules).
- **Phase 4B** — VDP/color/high-color illusion skills (shadow-highlight-scroll-fx,
  raster-palette-hint-director, visual-excellence-standards, palette-cram-curator,
  color-conversion-curator).
- **Phase 4C** — Entity/C-SGDK/Window-Plane skills (entity-polymorphism-architect,
  sgdk-runtime-coder, scene-state-architect).
- **Phase 4D** — software-tile-rasterizer (pseudo-3D / fake Mode 7 / rotozoom /
  wireframe / simple polygons), bounded and candidate.
- **Phase 4E** — sfx-prep-fm-psg-pcm (FM/PSG/PCM composition rules).
- **Phase 4F** — sgdk-build-wrapper-operator (SGDK Setup + VS Code as wrapper
  operation).
- **Phase 5** — Two new P0 canonical owner skills created: `input-system-sgdk`
  and `camera-system-sgdk`, with minimal contracts and synced validator.
- **Phase 6** — 16 reference case studies materialized in
  `lib_case/video-curation-2026-06-16`.

All Phase 4A–4F updates are recorded as `phase4X_skill_update_applied_candidate`
with `evidence_grade: E1_text`.

## Real new items

- **2 new skills**: `input-system-sgdk`, `camera-system-sgdk` (each with
  `SKILL.md` and `agents/openai.yaml`).
- **5 new schemas**: `input_mapping_contract`, `input_latency_contract`,
  `multiplayer_input_plan`, `camera_bounds_policy`, `parallax_camera_contract`.
  `camera_behavior_contract` was reused, not recreated.
- **16 case studies** in `tools/sgdk_wrapper/.agent/lib_case/video-curation-2026-06-16`
  (7 art, 3 hardware, 6 industry). Declared-vs-listed divergence recorded as
  `declared_case_count_mismatch: declared_14_listed_16`.

## Deferred (registered, NOT created)

- `porting-techniques-sgdk` — P2/backlog.
- `software-polygon-renderer` — P3.
- `fmv-compression-megadrive` — P4.

## Guarantees

- No promotion to `ready_for_aaa`, `testado_em_emulador`, `validado_budget` or
  `buildado` anywhere in this curation.
- No fake/invented SGDK input APIs; `input-system-sgdk` uses only real `joy.h`
  APIs (`JOY_init`, `JOY_update`, `JOY_readJoypad`, `JOY_getJoypadType`,
  `JOY_getPortType`, `JOY_setSupport`).
- No `SGDK_projects/` files were altered by this curation; the pre-existing
  changes there belong to the user and were left untouched.
- Commit and push remain pending.

## Validator coverage of Phase 5/6 additions

The validator (`validate_aaa_video_curation.py`) was extended additively with
`validate_phase5_input_camera` and `validate_phase6_case_studies`, leaving the
original curated counts (20 skills / 20 contracts / 28 schemas) intact. This
final review is an auxiliary document and is not required by the validator.

## Commit recommendation (future, not done here)

- Stage and commit **only** `tools/sgdk_wrapper/` for this curation, in a branch,
  separate from the unrelated pre-existing `SGDK_projects/` working-tree changes.
- Do not bundle `SGDK_projects/` edits into the curation commit.
- Promotion beyond `candidate_applied_not_verified` requires real build and
  emulator evidence, not this package alone.
