# Mega Drive AAA Video Curation Registry

Status: `candidate_applied_not_verified`

Date: 2026-06-15

This registry tracks the canonical curation package created from the Mega Drive/SGDK technique material discussed in the thread. It does not certify runtime quality, ROM delivery, or AAA readiness. It certifies only that the candidate guardrails and documentation have been applied to the workspace tree.

## Scope

Accepted direct cases:

- 16 Tile tilemap attributes and per-cell hardware metadata.
- 16-bit sprite architecture and scanline constraints.
- Mega Drive VDP graphical tricks: scroll, priority, raster-style palette updates and dithering.
- Classic versus modern Mega Drive development pipeline.
- Mega Drive graphics pipeline: VRAM, CRAM, VSRAM, descriptors and DMA discipline.
- Independent developer architecture: articulated sprites, Z80 audio separation and software-driven effects.

Aggregate 64-video claims are recorded as backlog evidence only, not as proof.

## New Canonical Skills

- `tools/sgdk_wrapper/.agent/skills/code/collision-system-architect/`
- `tools/sgdk_wrapper/.agent/skills/hardware/vram-streaming-dma-queue/`
- `tools/sgdk_wrapper/.agent/skills/hardware/shadow-highlight-scroll-fx/`
- `tools/sgdk_wrapper/.agent/skills/code/entity-polymorphism-architect/`
- `tools/sgdk_wrapper/.agent/skills/architecture/game-state-transition-architect/`
- `tools/sgdk_wrapper/.agent/skills/governance/aaa-pipeline-guardian/`
- `tools/sgdk_wrapper/.agent/skills/art/tilemap-attribute-director/`
- `tools/sgdk_wrapper/.agent/skills/art/palette-cram-curator/`
- `tools/sgdk_wrapper/.agent/skills/hardware/sprite-scanline-budgeter/`
- `tools/sgdk_wrapper/.agent/skills/hardware/hscroll-linescroll-road-fx/`
- `tools/sgdk_wrapper/.agent/skills/hardware/raster-palette-hint-director/`
- `tools/sgdk_wrapper/.agent/skills/art/dither-composite-transparency/`
- `tools/sgdk_wrapper/.agent/skills/audio/z80-audio-boundary-architect/`
- `tools/sgdk_wrapper/.agent/skills/code/articulated-sprite-architect/`
- `tools/sgdk_wrapper/.agent/skills/code/software-tile-rasterizer/`
- `tools/sgdk_wrapper/.agent/skills/architecture/level-manifest-architect/`
- `tools/sgdk_wrapper/.agent/skills/art/sprite-asset-budget-curator/`
- `tools/sgdk_wrapper/.agent/skills/art/color-conversion-curator/`
- `tools/sgdk_wrapper/.agent/skills/audio/sfx-prep-fm-psg-pcm/`
- `tools/sgdk_wrapper/.agent/skills/operation/emulator-vdp-evidence-curator/`

## Existing Skill Handoff

The following existing skills were connected to the new contracts and gates:

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

The machine-readable owner map is:

- `tools/sgdk_wrapper/doc/05_technical/existing_skill_integration_manifest.json`

Integration mode: 4 direct skill-section updates and 11 sidecar handoffs, all tracked by the manifest and validator.

## Contracts

- `tools/sgdk_wrapper/schemas/collision_topology_report.schema.json`
- `tools/sgdk_wrapper/schemas/dma_queue_contract.schema.json`
- `tools/sgdk_wrapper/schemas/scroll_fx_contract.schema.json`
- `tools/sgdk_wrapper/schemas/entity_vtable_plan.schema.json`
- `tools/sgdk_wrapper/schemas/state_transition_contract.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_pipeline_gate_report.schema.json`
- `tools/sgdk_wrapper/schemas/external_technique_curation_record.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_video_curation_audit_report.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_prompt_route_fixture_pack.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_video_curation_manifest.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_video_curation_phase_matrix.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_pipeline_curated_skill_map.schema.json`
- `tools/sgdk_wrapper/schemas/existing_skill_integration_manifest.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_video_curation_decision_matrix.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_skill_contract_catalog.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_skill_activation_matrix.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_evidence_ladder.schema.json`
- `tools/sgdk_wrapper/schemas/external_source_reliability_rubric.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_agent_proficiency_matrix.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_agent_proficiency_eval_suite.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_source_to_skill_traceability_matrix.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_curation_validation_recovery_plan.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_curation_package_inventory.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_curation_risk_register.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_curation_memory_update.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_video_source_intake_template.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_validator_coverage_matrix.schema.json`
- `tools/sgdk_wrapper/schemas/aaa_status_vocabulary_map.schema.json`

## Operational References

- `tools/sgdk_wrapper/.agent/rules/AAA_VIDEO_CURATION.md`
- `tools/sgdk_wrapper/doc/05_technical/README.md`
- `tools/sgdk_wrapper/doc/05_technical/aaa_next_agent_handoff.md`
- `tools/sgdk_wrapper/doc/05_technical/aaa_video_curation_agent_bootstrap.md`
- `tools/sgdk_wrapper/doc/05_technical/pipeline_aaa_skill_gate_map.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_video_curation_manifest.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_video_curation_decision_matrix.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_skill_contract_catalog.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_skill_activation_matrix.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_evidence_ladder.json`
- `tools/sgdk_wrapper/doc/05_technical/external_source_reliability_rubric.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_agent_proficiency_matrix.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_agent_proficiency_eval_suite.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_source_to_skill_traceability_matrix.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_curation_validation_recovery_plan.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_curation_package_inventory.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_curation_risk_register.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_curation_memory_update.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_video_source_intake_template.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_validator_coverage_matrix.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_status_vocabulary_map.json`
- `tools/sgdk_wrapper/doc/05_technical/aaa_video_curation_phase_matrix.json`
- `tools/sgdk_wrapper/.agent/references/aaa_pipeline_curated_skill_map.json`
- `tools/sgdk_wrapper/doc/05_technical/guardian_fixtures/aaa_prompt_route_fixtures.json`

## Validation

Required command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_aaa_video_curation.ps1
```

Current blocker: the local runner in this Codex session cannot start processes and returns `CreateProcessAsUserW failed: 5`. Until validation runs locally, commit and push must not be claimed.
