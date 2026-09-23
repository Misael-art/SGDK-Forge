# AAA Evidence Ladder Workflow

Status: `candidate_applied_not_verified`

Use this workflow whenever an agent wants to promote a Mega Drive/SGDK claim beyond documentation, especially for advanced visuals, generated assets, runtime behavior, budget validation or AAA closeout.

## Inputs

- Claim being made.
- Current project artifacts.
- Build/emulator/VDP evidence available.
- Activated skill outputs from the AAA routing workflow.

## Steps

1. Locate the relevant claim in `doc/05_technical/aaa_evidence_ladder.json`.
2. Determine the highest rung proven by concrete artifacts.
3. If multiple domains are involved, choose the lowest proven rung across all domains.
4. Reject any promotion based only on text, intent or old artifacts.
5. If a required evidence item is missing, return the exact missing item and the next allowed status.
6. If the claim concerns a failed visual asset, mark it as negative evidence or obsolete source, never as generation source truth.

## Output

- Requested claim.
- Highest proven rung.
- Missing evidence.
- Allowed status vocabulary.
- Blocked status vocabulary.

## Hard Stop

Do not output `ready_for_aaa`, `validado_budget`, `testado_em_emulador` or `pronto` unless the evidence ladder permits that exact term.
