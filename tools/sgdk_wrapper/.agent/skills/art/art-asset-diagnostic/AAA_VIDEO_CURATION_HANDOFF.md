# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when `art-asset-diagnostic` evaluates model sheets, sprite sheets, AI-generated art, animation frames or visual fidelity for Mega Drive assets.

## New Required Routes

- Route production sprite sheets to `sprite-asset-budget-curator`.
- Route palette/index/color claims to `palette-cram-curator`.
- Route generated-art conversion or high-color source material to `color-conversion-curator`.
- Route final visual closeout to `emulator-vdp-evidence-curator`.

## Anti-Polishing Rule

If a sprite sheet fails visual fidelity, human visual review, VDP dump evidence, palette/index constraints or model-sheet consistency, mark it as rejected/obsolete evidence. Do not improve by painting over the failed sheet. Restart from the approved model sheet, visual DNA, lineart/blocking and key poses.

## Blockers

- Rejected sheet used as `source`, `baseline`, `img2img_base` or `reference_for_generation`.
- Missing frame-origin and bounding-box policy.
- Character features mutate across frames.
- Indexed palette or transparency policy is unproven.
