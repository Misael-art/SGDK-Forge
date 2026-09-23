# AAA Status Vocabulary Gate

Status: `candidate_applied_not_verified`

Use this workflow before reporting status for the Mega Drive AAA video curation package, a project, a ROM, a generated asset, a VDP budget claim or an AAA/release claim.

## Inputs

- Claim or status the agent wants to report.
- Evidence currently available.
- `doc/05_technical/aaa_status_vocabulary_map.json`.
- `doc/05_technical/aaa_evidence_ladder.json`.

## Steps

1. Identify the exact scope: curation package, project, runtime, hardware budget, asset or release.
2. Find the requested status term in the status vocabulary map.
3. Check the required evidence ladder rung.
4. If evidence is missing, downgrade to the highest allowed status.
5. Replace ambiguous terms such as `pronto`, `validado` or `AAA` with exact status vocabulary.
6. Report forbidden promotions explicitly.

## Output

- Requested status.
- Allowed exact status.
- Missing evidence.
- Forbidden terms avoided.

## Hard Stop

Do not use `pronto`, `validado` or `AAA` without the exact evidence-backed status term beside it.
