# Mega Drive AAA Video Technique Curation

Status: `candidate_applied_not_verified`

This folder contains the curated, machine-readable intake of the Mega Drive video technique material provided in the thread. The package is intentionally conservative: direct case records are separated from aggregate claims, and every accepted technique must map to an owner skill, schema, gate, or backlog item.

## Canonical Rule

External video analysis is not accepted as production truth by prose alone.

Canonical entry points:

- `.agent/rules/AAA_VIDEO_CURATION.md`
- `doc/05_technical/aaa_next_agent_handoff.md`
- `doc/05_technical/aaa_video_curation_agent_bootstrap.md`

A concept becomes operational only when it has:

- a direct source/case record;
- an accepted or deferred decision;
- a canonical owner skill;
- a machine-readable contract when it affects build, runtime, VDP budget, assets or release gates;
- validation evidence before any `ready_for_aaa` or release claim.

## New Skills

- `collision-system-architect`: collision topology, semi-solid platforms, slope probing, hit/hurt/push boxes.
- `vram-streaming-dma-queue`: VRAM slot ownership, dirty uploads, tile animation windows and DMA budget discipline.
- `shadow-highlight-scroll-fx`: Shadow/Highlight, HScroll/VScroll, palette and raster-style scene effects.
- `entity-polymorphism-architect`: SGDK-safe entity catalogs, function-pointer vtables and static pools.
- `game-state-transition-architect`: fade, flush, transition mutex and VDP/CRAM/SAT cleanup during state changes.
- `aaa-pipeline-guardian`: routes ambitious AAA claims to required skills and blocks false readiness.
- `tilemap-attribute-director`: per-cell tilemap metadata, palette select, priority and H/V flip.
- `palette-cram-curator`: 9-bit color, CRAM ownership and palette conflict review.
- `sprite-scanline-budgeter`: SAT and per-scanline budget for large sprites, crowds and bosses.
- `hscroll-linescroll-road-fx`: line-scroll, road, water and pseudo-3D plane effects.
- `raster-palette-hint-director`: H-Interrupt and raster-style palette changes.
- `dither-composite-transparency`: checkerboard/composite transparency and display-risk review.
- `z80-audio-boundary-architect`: Z80/68000 audio driver boundary and PCM/DAC risk.
- `articulated-sprite-architect`: linked multi-part sprites, anchors and SAT order.
- `software-tile-rasterizer`: CPU-rendered tile-buffer effects and dirty upload control.
- `level-manifest-architect`: stage-level contract for camera, assets, collision, entities and evidence.
- `sprite-asset-budget-curator`: production sprite sheet budget, model-sheet fidelity and frame consistency.
- `color-conversion-curator`: high-color, SNES/PC-98 and AI art conversion into Mega Drive constraints.
- `sfx-prep-fm-psg-pcm`: FM, PSG and PCM sound-effect preparation.
- `emulator-vdp-evidence-curator`: BlastEm, screenshot, SRAM and VDP-dump evidence closeout.

## Updated Existing Skills

The new skills are not isolated documentation. Their handoff into pre-existing canonical skills is tracked in:

- `doc/05_technical/existing_skill_integration_manifest.json`

Current owner skills covered by the integration manifest:

- `megadrive-vdp-budget-analyst`
- `scene-direction-curator`
- `multi-plane-composition`
- `art-translation-to-vdp`
- `art-asset-diagnostic`
- `art-conversion-pipeline`
- `visual-excellence-standards`
- `rom-mastering`
- `sgdk-runtime-coder`
- `scene-state-architect`
- `sgdk-code-reviewer`
- `sgdk-build-wrapper-operator`
- `tiled-hybrid-parallax-curator`
- `cutscene-cinematic-direction`
- `project-methodology-adoption`

Four integrations are direct skill-section updates already applied earlier in the curation package. Eleven are conservative sidecar handoffs added inside the owner skill/workflow directories to avoid overwriting unknown existing skill content while local process execution is unavailable.

## Core Contracts

- `collision_topology_report.schema.json`
- `dma_queue_contract.schema.json`
- `scroll_fx_contract.schema.json`
- `entity_vtable_plan.schema.json`
- `state_transition_contract.schema.json`
- `aaa_pipeline_gate_report.schema.json`
- `external_technique_curation_record.schema.json`
- `aaa_video_curation_audit_report.schema.json`
- `aaa_prompt_route_fixture_pack.schema.json`
- `aaa_video_curation_manifest.schema.json`
- `aaa_video_curation_phase_matrix.schema.json`
- `aaa_pipeline_curated_skill_map.schema.json`
- `existing_skill_integration_manifest.schema.json`
- `aaa_video_curation_decision_matrix.schema.json`
- `aaa_skill_contract_catalog.schema.json`
- `aaa_skill_activation_matrix.schema.json`
- `aaa_evidence_ladder.schema.json`
- `external_source_reliability_rubric.schema.json`
- `aaa_agent_proficiency_matrix.schema.json`
- `aaa_agent_proficiency_eval_suite.schema.json`
- `aaa_source_to_skill_traceability_matrix.schema.json`
- `aaa_curation_validation_recovery_plan.schema.json`
- `aaa_curation_package_inventory.schema.json`
- `aaa_curation_risk_register.schema.json`
- `aaa_curation_memory_update.schema.json`
- `aaa_video_source_intake_template.schema.json`
- `aaa_validator_coverage_matrix.schema.json`
- `aaa_status_vocabulary_map.schema.json`

Minimal examples live in `doc/05_technical/examples/`.

## Direct Cases

Machine-readable records:

- `curation_records/case_16tile_tilemap_attributes.json`
- `curation_records/case_sprites_16bit_architecture.json`
- `curation_records/case_graphical_tricks_vdp.json`
- `curation_records/case_modern_vs_classic_md_pipeline.json`
- `curation_records/case_megadrive_graphics_pipeline.json`
- `curation_records/case_independent_devs_architecture.json`

Human-readable technical case studies:

- `case_16tile_tilemap_attributes.md`
- `case_rangerx_shadow_highlight_scroll.md`
- `case_independent_devs_architecture.md`

## Pipeline References

- `pipeline_aaa_skill_gate_map.json`
- `aaa_video_curation_manifest.json`
- `aaa_next_agent_handoff.md`
- `aaa_video_curation_agent_bootstrap.md`
- `aaa_video_curation_decision_matrix.json`
- `aaa_skill_contract_catalog.json`
- `aaa_skill_activation_matrix.json`
- `aaa_evidence_ladder.json`
- `external_source_reliability_rubric.json`
- `aaa_agent_proficiency_matrix.json`
- `aaa_agent_proficiency_eval_suite.json`
- `aaa_source_to_skill_traceability_matrix.json`
- `aaa_curation_validation_recovery_plan.json`
- `aaa_curation_package_inventory.json`
- `aaa_curation_risk_register.json`
- `aaa_curation_memory_update.json`
- `aaa_video_source_intake_template.json`
- `aaa_validator_coverage_matrix.json`
- `aaa_status_vocabulary_map.json`
- `aaa_video_curation_phase_matrix.json`
- `aaa_video_curation_closeout_checklist.md`
- `aaa_video_curation_operational_summary.md`
- `prompt_to_pipeline_gate_checklist.md`
- `video_curation_evidence_backlog.json`
- `phase4_asset_conversion_backlog.md`

## Validation

Primary command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_aaa_video_curation.ps1
```

Fallback command:

```powershell
python tools/sgdk_wrapper/validate_aaa_video_curation.py
```

Local process execution has been restored (an earlier `CreateProcessAsUserW failed: 5` blocker no longer reproduces) and the package validator now reports `PASSED`. A package-validator PASS confirms documentation/guardrail integrity only; it is not ROM/emulator proof, so the package stays `candidate_applied_not_verified` until a build/emulator run produces runtime evidence.
