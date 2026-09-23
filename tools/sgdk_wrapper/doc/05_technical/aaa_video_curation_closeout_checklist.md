# AAA Video Curation Closeout Checklist

Status: `candidate_applied_not_verified`

Use this checklist before promoting the curation package beyond candidate status.

## Required Before Validation

- [ ] `.agent/rules/AAA_VIDEO_CURATION.md` exists and points to the canonical curation artifacts.
- [ ] `aaa_next_agent_handoff.md` exists and summarizes current truth, prohibitions and recovery path.
- [ ] `aaa_video_curation_agent_bootstrap.md` exists and defines the session load order.
- [ ] Direct case records exist for every accepted source.
- [ ] Aggregate claims remain separated as backlog evidence.
- [ ] New skills have `SKILL.md` and `agents/openai.yaml`.
- [ ] New contracts have JSON schemas and minimal examples.
- [ ] Existing owner skills are listed in `existing_skill_integration_manifest.json`.
- [ ] Existing owner integrations declare direct section or sidecar handoff mode.
- [ ] The 20/15/14/8 decision split is preserved in `aaa_video_curation_decision_matrix.json`.
- [ ] All twenty new skills have operational contracts in `aaa_skill_contract_catalog.json`.
- [ ] Multi-domain prompts follow `aaa_skill_activation_matrix.json` and `aaa-skill-routing-workflow.md`.
- [ ] Status promotions follow `aaa_evidence_ladder.json` and `aaa-evidence-ladder-workflow.md`.
- [ ] External source use follows `external_source_reliability_rubric.json` and `external-source-reliability-gate.md`.
- [ ] Agent proficiency can be evaluated with `aaa_agent_proficiency_matrix.json`, `aaa_agent_proficiency_eval_suite.json` and `aaa-agent-proficiency-eval.md`.
- [ ] Source-to-skill mapping is preserved in `aaa_source_to_skill_traceability_matrix.json` and `aaa-source-traceability-audit.md`.
- [ ] Runner recovery and promotion rules are preserved in `aaa_curation_validation_recovery_plan.json` and `aaa-curation-validation-recovery.md`.
- [ ] Package counts are preserved in `aaa_curation_package_inventory.json` and `aaa-curation-package-inventory-audit.md`.
- [ ] Open risks are preserved in `aaa_curation_risk_register.json` and `aaa-curation-risk-audit.md`.
- [ ] Operational memory is captured in `aaa_curation_memory_update.json` and `aaa-curation-memory-capture.md`.
- [ ] Future source ingestion is standardized by `aaa_video_source_intake_template.json` and `aaa-video-source-intake.md`.
- [ ] Validator coverage is preserved in `aaa_validator_coverage_matrix.json` and `aaa-validator-coverage-audit.md`.
- [ ] Status reports use `aaa_status_vocabulary_map.json` and `aaa-status-vocabulary-gate.md`.
- [ ] `aaa-pipeline-guardian` routes advanced claims before `ready_for_aaa`.
- [ ] Phase 4 asset conversion remains backlog until proven with local assets and scripts.

## Required Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_aaa_video_curation.ps1
```

Then run the workspace methodology, context, hygiene, freshness and learning audits required by `AGENTS.md`.

## Status Rules

- If validation cannot run, keep `candidate_applied_not_verified`.
- If validation fails, keep `rejected_or_partial` and fix the concrete issue.
- If validation passes, the curation package may become `validated_curation`.
- Do not use this checklist to claim any ROM, scene or asset is AAA-ready.

## Runner State

Local process execution has been restored (an earlier `CreateProcessAsUserW failed: 5` blocker no longer reproduces) and `validate_aaa_video_curation.ps1` now reports `PASSED`. That PASS confirms package documentation/guardrail integrity only and is not ROM/emulator proof; commit and push remain pending and the status stays `candidate_applied_not_verified`.

## Final Review (Phase 7)

Phases 1-6 are closed and consolidated in
`aaa_video_curation_final_review_2026-06-16.md`. That report records the phase
completions, the real new items (2 skills, 5 schemas, 16 case studies), the
three deferred skills, the no-promotion guarantees and the future commit
recommendation (commit `tools/sgdk_wrapper/` only, separate from the pre-existing
`SGDK_projects/` changes). Commit/push are still pending.
