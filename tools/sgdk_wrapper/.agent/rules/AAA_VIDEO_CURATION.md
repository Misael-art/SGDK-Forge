# AAA Video Curation Rule

Status: `candidate_applied_not_verified`

Use this rule whenever a prompt, project, training case or curation task references Mega Drive/Genesis AAA techniques, external video-derived development knowledge, advanced VDP effects, generated sprite sheets, hardware-budget claims, or release/AAA readiness.

## Mandatory Entry Points

- Decision matrix: `tools/sgdk_wrapper/doc/05_technical/aaa_video_curation_decision_matrix.json`
- Skill contracts: `tools/sgdk_wrapper/doc/05_technical/aaa_skill_contract_catalog.json`
- Skill activation order: `tools/sgdk_wrapper/doc/05_technical/aaa_skill_activation_matrix.json`
- Evidence ladder: `tools/sgdk_wrapper/doc/05_technical/aaa_evidence_ladder.json`
- Source reliability rubric: `tools/sgdk_wrapper/doc/05_technical/external_source_reliability_rubric.json`
- Existing skill integration manifest: `tools/sgdk_wrapper/doc/05_technical/existing_skill_integration_manifest.json`

## Non-Negotiable Behavior

- Start multi-domain AAA requests with `aaa-pipeline-guardian`.
- Do not promote an AI video summary into validated technical truth without source/tool/local evidence.
- Do not claim `ready_for_aaa`, `validado_budget`, `testado_em_emulador` or `pronto` unless the evidence ladder allows the exact status.
- Do not use a rejected or partial sprite sheet as source, baseline, reference for generation or img2img base.
- If a prompt requests advanced VDP, sprite, audio, collision, state-transition or asset-conversion work, activate the relevant curated skills from the skill contract catalog.
- If the runner cannot execute validation commands, keep the status as `candidate_applied_not_verified`.

## Validation Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sgdk_wrapper/validate_aaa_video_curation.ps1
```

This validation checks package coherence only. It does not replace project context validation, hygiene validation, build validation, emulator evidence, VDP dump evidence or ROM mastering.
