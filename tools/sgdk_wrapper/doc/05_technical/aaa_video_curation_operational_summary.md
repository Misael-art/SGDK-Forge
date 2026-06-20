# AAA Video Curation Operational Summary

Status: `candidate_applied_not_verified`

This curation package converts the attached Mega Drive technique analysis into operational guardrails for the canonical SGDK Forge agent. It does not approve any game, ROM, art asset or scene as AAA by itself.

## Accepted As Operational

- Per-cell tilemap attributes: palette select, priority, H/V flip and tile index must be treated as hardware-level scene data, not merely visual editor convenience.
- Sprite work must be budgeted against SAT/OAM, scanline limits, 4bpp indexed color, palette selection and sprite decomposition.
- Advanced scene claims involving raster-like effects, Shadow/Highlight, scrolling, palette swaps or pseudo-3D must pass a VDP-oriented budget gate.
- Complex entity behavior should use explicit archetypes, static pools and function-pointer dispatch plans rather than ad hoc branching.
- Game-state transitions need a contract for fade, flush, callback cleanup, input lock and VRAM/CRAM/SAT reset.
- Tilemap exports need explicit per-cell attribute review for palette, priority, H-flip and V-flip.
- Palette work needs CRAM ownership and 9-bit/indexed color review before claiming vibrant output.
- Large sprites, bosses and crowds need per-scanline budgeting, not only total sprite counts.
- Line-scroll, H-Int palette effects, dithering/composite tricks and CPU-rendered tile effects need separate hardware-risk gates.
- Z80 audio, FM/PSG/PCM SFX and emulator/VDP evidence now have dedicated owner skills.
- AAA claims must pass the `aaa-pipeline-guardian` before being presented as ready.

## Accepted Only As Backlog

- The aggregate claim that 64 videos were analyzed.
- Phase 4 asset conversion automation.
- Any new skill proposal without a direct source case, owner skill and measurable SGDK/VDP consequence.

## New Guardrails

- `.agent/rules/AAA_VIDEO_CURATION.md`
- `aaa_next_agent_handoff.md`
- `aaa_video_curation_agent_bootstrap.md`
- `existing_skill_integration_manifest.json`
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

These prevent the new curation package from living as disconnected documentation. If a new contract affects art direction, VDP conversion, multi-plane composition, hardware budget, runtime code, code review, ROM mastering, visual excellence, asset conversion or methodology adoption, an owner skill/workflow must consume it.

The skill contract catalog also prevents name-only skills: every new skill must declare trigger terms, required inputs, required outputs, blockers and handoffs.

The activation matrix prevents chaotic multi-skill routing: real prompts must start with `aaa-pipeline-guardian`, then follow the declared order for level manifests, visual/VDP design, hardware budget, runtime architecture, audio and closeout evidence.

The evidence ladder prevents validation theater: an agent may only use the highest status proven by concrete artifacts, and must treat text-only reports as insufficient for runtime, budget or AAA claims.

The source reliability rubric prevents over-trusting AI summaries: attached/transcribed video analysis can seed candidate skills and backlog, but cannot become validated technical truth until promoted by source, tool, SGDK or local runtime evidence.

The proficiency matrix and eval suite turn this into measurable agent behavior: an agent must route skills correctly, produce contracts, block false claims and ask for the right evidence before it can be treated as proficient.

The source-to-skill traceability matrix explains why each accepted skill/artifact exists by tying it back to a direct case or explicitly scoped aggregate claim.

The validation recovery plan tells the next agent exactly how to move from `candidate_applied_not_verified` to `validated_curation` after command execution is restored, without accidentally claiming ROM, runtime or AAA release validation.

The package inventory preserves expected counts for skills, integrations, schemas, examples and workflows so later changes do not silently desynchronize the package.

The risk register records unresolved blockers and accepted constraints, especially runner execution failure, indirect source corpus, sidecar handoffs and the boundary between curation validation and project/runtime validation.

The memory update capsule preserves key operational decisions until the primary workspace memory bank can be safely inspected and updated.

The source intake template standardizes future video/transcript ingestion so new techniques enter through reliability classification, technique extraction, owner-skill mapping and evidence requirements.

The validator coverage matrix maps mandatory artifacts to validator functions so future package changes do not silently lose validation coverage.

The status vocabulary map binds AGENTS.md terms to evidence rungs so agents do not use ambiguous words like `pronto`, `validado` or `AAA` without exact proof.

Integration mode:

- 4 direct skill-section updates.
- 11 sidecar handoffs added inside owner skill/workflow directories because local file inspection/execution is blocked in this environment.

## Required Validation

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_aaa_video_curation.ps1
```

Current runner state:

- local process execution has been restored (the earlier `CreateProcessAsUserW failed: 5` blocker no longer reproduces);
- the package validator now reports `PASSED`, which confirms documentation/guardrail integrity only and is not ROM/emulator proof;
- no commit or push has been performed in this session;
- the correct status remains `candidate_applied_not_verified` until build/emulator runtime evidence exists.
