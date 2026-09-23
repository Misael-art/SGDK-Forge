# AAA Video Source Intake

Status: `candidate_applied_not_verified`

Use this workflow whenever a new YouTube video, transcript, AI summary, interview, external article or aggregate analysis is proposed as input for Mega Drive AAA curation.

## Inputs

- Source text, link, transcript or attachment.
- Requested use: idea, skill, rule, case study, implementation guidance or validation evidence.
- Current curation package artifacts.

## Steps

1. Create an intake record using `doc/05_technical/aaa_video_source_intake_template.json`.
2. Classify the source with `external_source_reliability_rubric.json`.
3. Extract techniques as raw claims first; do not normalize them into canon yet.
4. For each technique, map to SGDK/Mega Drive constraints and candidate owner skills.
5. Decide `accept_with_constraints`, `defer` or `reject`.
6. Update `aaa_source_to_skill_traceability_matrix.json` before updating decision matrices or skills.
7. Update inventory, risk register and validator only when a new mandatory artifact is added.
8. Keep status as `candidate_applied_not_verified` until validation runs.

## Output

- Source reliability level.
- Accepted/deferred/rejected technique list.
- Owner skills and evidence path.
- Correlated artifacts that must be updated.

## Hard Stop

Do not create or update a canonical skill directly from a new source unless the intake record maps the technique to owner skills, evidence requirements and source reliability level.
