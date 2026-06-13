# Human Validation Record v009

Status: `rejected_human_visual_validation`

Asset: `hibrido_fighter_sprite_sheet_v009`

Candidate outputs:

- `data/processed/reports/hibrido_fighter_complete_contact_sheet_with_palette_v009_preview_x4.png`
- `data/processed/reports/hibrido_fighter_complete_contact_sheet_with_palette_v009.png`
- `data/processed/spritesheets/hibrido_fighter_complete_sprite_sheet_48x64_v009.png`
- `res/sprites/hibrido/hibrido_idle_body_48x64_strip_v009.png`
- `res/sprites/hibrido/hibrido_walk_step_body_48x64_strip_v009.png`
- `res/sprites/hibrido/hibrido_guard_block_body_48x64_strip_v009.png`
- `res/sprites/hibrido/hibrido_jab_body_48x64_strip_v009.png`
- `res/sprites/hibrido/hibrido_knee_body_48x64_strip_v009.png`
- `res/sprites/hibrido/hibrido_teep_body_48x64_strip_v009.png`

Runtime evidence:

- ROM: `out/rom.bin`
- ROM sha256: `764d5a95c5c6aa979905afaeba417c6225b0547299537bb27228c4c85a9b34da`
- BlastEm screenshot: `out/evidence/blastem/screenshot.png`
- BlastEm SRAM: `out/evidence/blastem/save.sram`
- Capture reconciliation: `out/logs/blastem_evidence_reconciliation_v009.json`

Decision:

- Technical sprite-strip conformance passed for the v009 runtime strips.
- The viewer ROM boots and displays the v009 fighter in BlastEm, but official evidence is partial because the capture script has a known minimal-mode artifact bug.
- Human visual review on 2026-06-13 rejected the candidate for failing model-sheet fidelity.
- Rejection report: `out/logs/hibrido_v009_model_sheet_to_sprite_fidelity_report.json`.
- The sheet is technically structured, but it lost the v008 model sheet's anatomical detail, face/eye focal point, lava-arm signature, black/gold shorts, wraps and Muay Thai acting.
- This candidate must not be marked `ready_for_aaa`, final art, or promoted as a visual baseline.
