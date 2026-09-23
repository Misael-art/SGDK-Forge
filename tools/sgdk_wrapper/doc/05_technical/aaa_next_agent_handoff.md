# AAA Next Agent Handoff

Status: `candidate_applied_not_verified`

This is the compact handoff for the next agent or curator resuming the Mega Drive AAA video curation package.

## Start Here

1. Read `tools/sgdk_wrapper/.agent/rules/AAA_VIDEO_CURATION.md`.
2. Read `tools/sgdk_wrapper/doc/05_technical/aaa_video_curation_manifest.json`.
3. Read `tools/sgdk_wrapper/doc/05_technical/aaa_curation_risk_register.json`.
4. Read `tools/sgdk_wrapper/doc/05_technical/aaa_curation_validation_recovery_plan.json`.
5. Run the validator only if local process execution works.

## Current Truth

- Package status is `candidate_applied_not_verified`.
- The package contains 20 new candidate skills and 15 integrations with existing skills/workflows.
- The broader 64-video claim is indirect aggregate evidence, not proof.
- Local process execution has been restored (an earlier `CreateProcessAsUserW failed: 5` blocker no longer reproduces) and `validate_aaa_video_curation.ps1` now reports `PASSED`; that PASS is package documentation/guardrail integrity only, not ROM/emulator proof.
- Phases 1-6 are complete; the consolidated closeout is in `aaa_video_curation_final_review_2026-06-16.md`.
- Phase 5 added 2 new skills (`input-system-sgdk`, `camera-system-sgdk`) and 5 new schemas; Phase 6 added 16 case studies in `.agent/lib_case/video-curation-2026-06-16`.
- Deferred, not created: `porting-techniques-sgdk` (P2), `software-polygon-renderer` (P3), `fmv-compression-megadrive` (P4).
- No commit or push has been proven.

## Do Not Do

- Do not mark this package as validated from file presence alone.
- Do not claim ROM, runtime, VDP, sprite fidelity or AAA release validation from this package.
- Do not merge sidecar handoffs into `SKILL.md` bodies without reading the original skill content.
- Do not treat AI video summaries as primary technical proof.
- Do not use failed sprite sheets as generation sources.

## Recovery Path

When process execution works:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_aaa_video_curation.ps1
```

Then run the workspace audits required by `AGENTS.md`, review git status, stage only intended files, commit and push only after real command output exists.

## If You Add New Material

Use:

- `aaa_video_source_intake_template.json`
- `external_source_reliability_rubric.json`
- `aaa_source_to_skill_traceability_matrix.json`
- `aaa_validator_coverage_matrix.json`
- `aaa_curation_package_inventory.json`

Any mandatory new artifact must update the validator, inventory, manifest, registry, changelog, checklist, operational summary, audit report and memory capsule.
