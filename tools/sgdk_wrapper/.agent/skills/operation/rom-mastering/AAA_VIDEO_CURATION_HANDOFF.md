# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when `rom-mastering` closes a ROM, demo, training case or visual showcase.

## New Required Routes

- Route emulator and VDP proof to `emulator-vdp-evidence-curator`.
- Route advanced visual claims to `aaa-pipeline-guardian`.
- Route budget-sensitive scenes to `megadrive-vdp-budget-analyst`.

## Closeout Rules

- Build success is not runtime validation.
- ROM closeout must not claim `ready_for_aaa`, `testado_em_emulador` or `validado_budget` without evidence.
- For visual cases requiring SRAM/VDP proof, screenshot alone is insufficient.
- BlastEm remains the mandatory gate when the project requires emulator proof.
