# AAA Video Curation Agent Bootstrap

Status: `candidate_applied_not_verified`

Use this bootstrap at the start of a session when the user asks for curation, Mega Drive AAA technique absorption, video-derived technique analysis, advanced SGDK graphics, high-quality sprite pipelines, or validation of AAA claims.

## Load Order

1. Read `.agent/rules/AAA_VIDEO_CURATION.md`.
2. Read `doc/05_technical/aaa_video_curation_manifest.json`.
3. Read `doc/05_technical/external_source_reliability_rubric.json`.
4. Read `doc/05_technical/aaa_skill_activation_matrix.json`.
5. Read only the specific skill contracts from `doc/05_technical/aaa_skill_contract_catalog.json` that match the prompt.
6. Before promoting any status, read `doc/05_technical/aaa_evidence_ladder.json`.

## Operating Mode

- Treat external AI transcripts as curation input, not proof.
- Route first, then implement or write.
- Prefer machine-readable contracts over narrative reports.
- Keep aggregate claims separate from direct cases.
- Preserve `candidate_applied_not_verified` until local validation succeeds.

## Required Answer Discipline

When closing a curation turn, report:

- what was added or updated;
- which canonical artifact now owns the rule;
- whether validation ran;
- if validation did not run, the exact blocker;
- the current status.

## Forbidden Shortcut

Do not answer with only a prose recommendation when the request asks to improve the ecosystem. Create or update the relevant canonical artifact, validator, workflow, manifest or skill handoff.
