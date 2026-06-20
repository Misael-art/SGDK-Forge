# Celestial Chase Revive - Project Learning Case

Batch: `project_learning_curation_2026_06_16`

Evidence grade: `E1_project_artifact`

Canonical promotion: false

Source project:

`SGDK_projects/Celestial Chase Revive [VER.001] [SGDK 211] [GEN] [GAME] [ACTION_RACING]`

## Context

This project is an `aaa_game` foundation for a Mega Drive action-racing game.
It contains extensive planning contracts, a local agent learning ledger, a
runtime seed, build metadata and BlastEm evidence for the seed scope.

The key learning is not "this project is done". The useful pattern is how a
strict agent should prevent planning completeness, placeholder runtime and seed
evidence from being confused with full gameplay delivery.

## Observed Lessons

- Pre-runtime specs for an `aaa_game` need executable contracts before coding:
  track data, collision, HUD, animation, tuning, assets, build, boss/game flow
  and front-end identity.
- Input abstraction must exist before interactive scenes; scenes consume actions,
  not raw hardware reads.
- `START` is a game-flow button. If the future game reserves it for pause or
  confirm, placeholders should not reuse it casually as an exit key.
- Scene transitions need per-scene fade/palette policy, input lock, teardown,
  reset and handoff; generic fade is not enough.
- Cutscenes with many beats should use table-driven FSM data, not a growing
  monolithic `update()`.
- Boot seed evidence proves only the boot seed. It does not prove gameplay,
  visual delivery, audio, VDP budget or AAA readiness.
- Local mockups are useful only with hash and `mockup_reference_only` status.
  They do not become source art, final pixel art or emulator evidence.
- A creative cohesion pass can prevent a technically complete plan from becoming
  generic, but it remains design direction until runtime and playtest evidence
  exist.
- Status reports must be reconciled after build: ROM metadata, changelog, memory
  bank, mastering, local CI, validation blockers and emulator evidence can drift.
- Canonical build history must come from immutable
  `doc/changelog/roms/build_v*/build_meta.json`, not only from the latest mutable
  validation report.
- Repeated build/capture cycles with `blockers_removed=0` require an explicit
  blocker-removal intent before spending another build.
- Emulator evidence is sealed to one ROM hash after capture; a later rebuild
  invalidates the seal instead of silently triggering another capture loop.
- Local learning candidates must be deduplicated against existing owners before
  `create_skill` is proposed.

## Why This Did Not Become A New Skill

The project did not reveal a pure new domain. It strengthened existing owners:

- `aaa-pipeline-guardian`
- `project-methodology-adoption`
- `production-loop`
- `input-system-sgdk`
- `game-state-transition-architect`
- `cutscene-cinematic-direction`
- `sgdk-runtime-coder`
- `sgdk-build-wrapper-operator`
- `visual-excellence-standards`

Creating a new skill would duplicate ownership and make the agent slower.

## Applicable Limits

- This is one project, not a repeated corpus.
- Evidence is local and mostly documentary, with runtime proof only for the boot
  seed scope.
- No lesson here can promote `ready_for_aaa`, full gameplay, visual delivery,
  measured budget or audio quality.
- Future canonical promotion requires human review and stronger repeated
  evidence.

## Required Followups Before Production Claims

- Fresh status reconciliation after any new ROM.
- Scene closeout gate for any delivered scene.
- VDP/VRAM/CRAM/SAT/DMA evidence for visual or budget claims.
- BlastEm evidence tied to the exact ROM hash and scene scope.
- Code review for runtime patterns that use text, palette transitions, input and
  scene manager logic.
