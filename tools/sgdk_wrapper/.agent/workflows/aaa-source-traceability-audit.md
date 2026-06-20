# AAA Source Traceability Audit

Status: `candidate_applied_not_verified`

Use this workflow when importing, reviewing or extending the Mega Drive AAA video curation package.

## Inputs

- Source or case id.
- Extracted techniques.
- Proposed owner skills.
- Proposed contracts or validator changes.

## Steps

1. Classify the source with `external_source_reliability_rubric.json`.
2. Add or update the source in `aaa_source_to_skill_traceability_matrix.json`.
3. For each accepted technique, declare owner skills, contract/artifact owners and required evidence.
4. For each rejected or deferred claim, write an explicit decision and reason.
5. Update the decision matrix only after traceability exists.
6. Do not create a canonical skill from a technique that lacks owner, artifact and evidence mapping.

## Output

- Source id.
- Reliability level.
- Accepted technique mappings.
- Rejected/deferred claims.
- Missing artifacts or evidence.

## Hard Stop

If a technique has no owner skill or no evidence path, it remains backlog and cannot become canonical behavior.
