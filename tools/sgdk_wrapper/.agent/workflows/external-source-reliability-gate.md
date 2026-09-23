# External Source Reliability Gate

Status: `candidate_applied_not_verified`

Use this workflow before importing external video-derived material, AI transcriptions, third-party summaries or aggregate analyses into canonical SGDK Forge skills, workflows or project claims.

## Inputs

- Source type.
- Source link, transcript or attachment if available.
- Technical claims extracted from the source.
- Requested promotion level.

## Steps

1. Classify the source with `doc/05_technical/external_source_reliability_rubric.json`.
2. Assign the current confidence level.
3. Compare the requested use against the allowed and forbidden uses for that level.
4. If the source is an aggregate claim, keep it as backlog until individual source records exist.
5. If the claim affects SGDK APIs, VDP behavior, assets or runtime status, require primary/local verification before promotion.
6. Record the classification in the relevant curation record, decision matrix or backlog.

## Output

- Source confidence level.
- Allowed use.
- Blocked use.
- Promotion requirements.

## Hard Stop

Do not promote an AI summary into a canonical validated rule unless it has been mapped to SGDK/Mega Drive constraints and the required local validation/evidence exists.
