# AAA Curation Risk Audit

Status: `candidate_applied_not_verified`

Use this workflow before promoting, committing, pushing or extending the Mega Drive AAA video curation package.

## Inputs

- `doc/05_technical/aaa_curation_risk_register.json`
- Proposed status change or new artifact.
- Available validation/evidence output.

## Steps

1. Read every open or accepted-with-constraint risk.
2. Check whether the proposed action is listed in `blocked_promotions`.
3. If blocked, require the listed resolution evidence before proceeding.
4. If a new risk is discovered, add it to the register before closing the turn.
5. If a risk is resolved, update its status only with concrete evidence.
6. Keep package status as `candidate_applied_not_verified` while critical risks remain open.

## Output

- Risks checked.
- Promotions blocked or allowed.
- Evidence still missing.
- Risk updates made.

## Hard Stop

Do not promote curation, runtime, ROM or AAA claims while a critical risk blocks that promotion.
