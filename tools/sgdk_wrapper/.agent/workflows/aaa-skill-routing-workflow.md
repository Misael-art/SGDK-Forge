# AAA Skill Routing Workflow

Status: `candidate_applied_not_verified`

Use this workflow when a prompt mentions Mega Drive AAA quality, advanced graphics, sprite sheets, VDP tricks, runtime architecture, audio boundaries, release closeout or external video-derived techniques.

## Inputs

- User prompt.
- Project context classification.
- Any attached source material or prior curation record.
- Current asset/runtime/evidence status.

## Steps

1. Run `aaa-pipeline-guardian` first for classification.
2. Match the prompt against `doc/05_technical/aaa_skill_activation_matrix.json`.
3. Load only the skills in the required sequence for that prompt class.
4. If multiple domains are triggered, follow the global order in the activation matrix.
5. If conflict rules apply, resolve the conflict before producing implementation or asset instructions.
6. Generate or request the machine-readable contracts required by the activated skills.
7. Do not promote `ready_for_aaa`, `validado_budget` or `testado_em_emulador` unless the closeout skills have evidence.

## Output

- Activated skills.
- Required contracts.
- Blocked claims.
- Next concrete action.

## Hard Stop

If the prompt asks to improve a rejected asset, use the anti-polishing rule: reject the failed asset as generation source and return to the approved source of truth.
