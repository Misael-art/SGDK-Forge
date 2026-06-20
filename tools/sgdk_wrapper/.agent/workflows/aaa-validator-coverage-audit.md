# AAA Validator Coverage Audit

Status: `candidate_applied_not_verified`

Use this workflow when adding, removing or changing mandatory artifacts in the Mega Drive AAA video curation package.

## Inputs

- Changed artifact.
- `doc/05_technical/aaa_validator_coverage_matrix.json`.
- `tools/sgdk_wrapper/validate_aaa_video_curation.py`.

## Steps

1. Identify whether the changed artifact is mandatory, experimental or backlog.
2. If mandatory, add it to required file lists and the relevant validator function.
3. Add or update its schema and minimal example when schema-backed.
4. Update `aaa_validator_coverage_matrix.json` with the coverage group.
5. Update inventory counts and correlated docs.
6. Keep status as `candidate_applied_not_verified` until the validator actually runs.

## Output

- Artifact coverage status.
- Validator function changed or not required.
- Inventory update status.
- Remaining validation blocker.

## Hard Stop

Do not add a mandatory artifact that is absent from both the validator and the coverage matrix.
