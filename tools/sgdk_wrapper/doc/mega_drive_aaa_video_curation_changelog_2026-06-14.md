# Mega Drive AAA Video Curation Changelog

Date: 2026-06-15

Status: `candidate_applied_not_verified`

## Added

- Added twenty canonical skills covering collision topology, VRAM/DMA streaming, Shadow/Highlight plus scroll FX, entity polymorphism, state transitions, AAA pipeline gating, tilemap attributes, CRAM palette curation, sprite scanline budget, line scroll, raster palette effects, dithering/composite transparency, Z80 audio boundaries, articulated sprites, software tile rasterization, level manifests, sprite asset budgets, color conversion, SFX preparation and emulator/VDP evidence.
- Added machine-readable schemas for the new contracts and audit artifacts.
- Added minimal JSON examples for each new operational contract.
- Added direct curation records for the six video-derived cases available in the thread.
- Added human-readable case studies for 16 Tile tilemap attributes, Ranger X-like scroll/Shadow/Highlight direction and independent developer architecture patterns.
- Added prompt route fixtures for the `aaa-pipeline-guardian`.
- Added `existing_skill_integration_manifest.json` to declare which existing owner skills consume the new contracts.
- Added `existing_skill_integration_manifest.schema.json` and a minimal example so that the integration manifest is validated like the rest of the package.
- Added `aaa_video_curation_decision_matrix.json` to preserve the 20 new skills, 15 updates, 14 covered items, 8 discarded/deferred items, 3 case studies and 2 pipeline updates as auditable curation data.
- Added `aaa_skill_contract_catalog.json` to define trigger terms, required inputs, required outputs, blockers and handoffs for all twenty new skills.
- Added `aaa_skill_activation_matrix.json` and `aaa-skill-routing-workflow.md` to define deterministic activation order for real prompts that trigger multiple domains.
- Added `aaa_evidence_ladder.json` and `aaa-evidence-ladder-workflow.md` to block validation theater by tying each status claim to required evidence.
- Added `external_source_reliability_rubric.json` and `external-source-reliability-gate.md` to classify AI transcripts, timestamped summaries, aggregate claims and locally verified sources.
- Added `.agent/rules/AAA_VIDEO_CURATION.md` and `aaa_video_curation_agent_bootstrap.md` so future agents know how to load and apply the package.
- Added `aaa_agent_proficiency_matrix.json`, `aaa_agent_proficiency_eval_suite.json` and `aaa-agent-proficiency-eval.md` to evaluate whether agents can apply the package operationally.
- Added `aaa_source_to_skill_traceability_matrix.json` and `aaa-source-traceability-audit.md` to trace each source/case to accepted techniques, owner skills, artifacts, evidence and rejected/deferred claims.
- Added `aaa_curation_validation_recovery_plan.json` and `aaa-curation-validation-recovery.md` to define how the package can be validated, promoted, committed and pushed after runner recovery.
- Added `aaa_curation_package_inventory.json` and `aaa-curation-package-inventory-audit.md` to preserve expected package counts and detect drift.
- Added `aaa_curation_risk_register.json` and `aaa-curation-risk-audit.md` to track residual risks and block unsafe status promotion.
- Added `aaa_curation_memory_update.json` and `aaa-curation-memory-capture.md` to preserve operational memory while the primary memory bank cannot be safely inspected/merged.
- Added `aaa_video_source_intake_template.json` and `aaa-video-source-intake.md` to standardize future video/transcript ingestion.
- Added `aaa_validator_coverage_matrix.json` and `aaa-validator-coverage-audit.md` to map validator functions to mandatory artifacts and prevent coverage drift.
- Added `aaa_next_agent_handoff.md` as a compact resume point for future agents.
- Added `aaa_status_vocabulary_map.json` and `aaa-status-vocabulary-gate.md` to bind AGENTS.md status vocabulary to evidence requirements.

## Updated

- Updated the VDP budget, scene direction, multi-plane composition and art-to-VDP skill surfaces with handoff requirements for the new contracts.
- Added eleven conservative sidecar handoffs for existing skill/workflow updates that were previously pending: asset diagnostic, asset conversion, visual excellence, ROM mastering, runtime coding, scene state, code review, build wrapper, tiled/parallax, cutscene direction and methodology adoption.
- Updated the main curation manifest to include existing skill integration and runner-blocked status.
- Updated the technical README to expose the package as a single human entry point.
- Updated the validator so it checks skill directories, schemas, examples, curation records, pipeline maps, phase matrix, audit report, prompt fixtures and all fifteen existing skill/workflow integrations.
- Updated the validator so the real skill contract catalog must contain exactly twenty operational contracts.
- Updated the validator so the skill activation matrix must preserve global order, conflict rules, prompt classes and the anti-polishing conflict.
- Updated the validator so the evidence ladder must preserve status rungs from documentation through candidate AAA and block text-only runtime evidence.
- Updated the validator so the source reliability rubric must preserve confidence levels and keep the aggregate 64-video claim scoped as indirect evidence.
- Updated the validator so the canonical rule and agent bootstrap must point to the decision matrix, skill catalog, activation matrix, evidence ladder and source rubric.
- Updated the validator so the proficiency matrix must preserve levels/dimensions and the eval suite must preserve key anti-theater fixtures.
- Updated the validator so source-to-skill traceability must preserve the six direct cases plus the aggregate 64-video source.
- Updated the validator so recovery planning must preserve runner blocker, validation command, promotion rules and commit/push evidence requirements.
- Updated the validator so package inventory must preserve expected counts for skills, integrations, schemas, examples and workflows.
- Updated the validator so risk register must preserve known critical/high risks and blocked promotions.
- Updated the validator so the memory update capsule must preserve key decisions, load order and pending recovery actions.
- Updated the validator so the source intake template must preserve reliability, extraction, decision and traceability fields.
- Updated the validator so the coverage matrix must preserve core validator functions and the known runner-blocked state.
- Updated the validator so the next-agent handoff is a required curation document.
- Updated the validator so status vocabulary must preserve project/runtime/curation terms and forbidden ambiguous synonyms.
- Updated the guardian fixture pack and curated skill map to route prompts across all twenty new skill surfaces.

## Deferred

- Full validation, commit and push are deferred because this Codex runner cannot execute local processes (`CreateProcessAsUserW failed: 5`).
- Phase 4 asset-conversion automation remains backlog pending verified local assets, scripts and execution evidence.
- The broader 64-video claim remains evidence backlog, not accepted proof.

## Batch curation_batch_2026_06_16 (Phases 3-7, 2026-06-16)

- Registered `curation_batch_2026_06_16` (aggregate plan + character-proportion direct text analysis) as candidate backlog (Phase 3).
- Absorbed batch concepts as candidate operational rules into existing skills across Phases 4A-4F (character/animation/pixel-strict; VDP/color/high-color; entity/C-SGDK/Window-Plane; software tile rasterizer; FM/PSG/PCM audio; SGDK setup + VS Code). All recorded as `phase4X_skill_update_applied_candidate`, evidence_grade E1_text.
- Phase 5: created two new candidate P0 skills `input-system-sgdk` and `camera-system-sgdk` (each with `SKILL.md` + `agents/openai.yaml`), five new schemas (`input_mapping_contract`, `input_latency_contract`, `multiplayer_input_plan`, `camera_bounds_policy`, `parallax_camera_contract`), reusing `camera_behavior_contract`. `input-system-sgdk` uses only real `joy.h` APIs.
- Phase 6: materialized 16 reference case studies in `.agent/lib_case/video-curation-2026-06-16` (`declared_case_count_mismatch: declared_14_listed_16`, canonical_promotion=false).
- Phase 7: added `aaa_video_curation_final_review_2026-06-16.md` as the consolidated closeout report.
- Validator extended additively (`validate_phase5_input_camera`, `validate_phase6_case_studies`) without changing the original curated counts.
- Deferred, not created: `porting-techniques-sgdk` (P2/backlog), `software-polygon-renderer` (P3), `fmv-compression-megadrive` (P4).
- `validate_aaa_video_curation.ps1` = PASSED; `assert_agent_environment.ps1` = ready; global status stays `candidate_applied_not_verified`; commit/push pending; no `SGDK_projects` file altered by this curation.

## Release Gate

No `ready_for_aaa`, game delivery or release claim is authorized by this changelog. Runtime claims still require the AGENTS.md emulator evidence gate.
