# Emulator QA Harness Contract

## Purpose

BlastEm remains the delivery gate. A build, screenshot, or intent note is not enough unless the ROM identity, emulator session, capture, and validation reports all point to the same ROM.

## Input

- absolute project root
- `out/rom.bin`
- expected `TargetScene` or scene id
- optional `blastem_input_script.json`
- `validation_report.json`
- `runtime_metrics.json` when the ROM emits runtime telemetry

## Output

- `out/logs/emulator_session.json`
- dedicated screenshot from the BlastEm window
- `save.sram` when the ROM emits canonical SRAM evidence
- `visual_vdp_dump.bin` when the project declares visual dump evidence
- SHA-256 of the tested ROM
- closed emulator lifecycle: `started -> captured -> closed`

## Rules

- Use `tools/sgdk_wrapper/lib/blastem_automation.psm1` for focus, input, screenshot, and closeout.
- Evidence must live inside `out/blastem_env_*` or project-owned evidence directories.
- `outside_sandbox_candidate`, `stale_sandbox_candidate`, and `fresh_sram_confirmed=false` invalidate evidence.
- `visual_vdp_dump.bin` with the same SHA-256 as `save.sram` is invalid evidence.
- Rebuilding `out/rom.bin` makes prior emulator evidence stale.

## Minimal Example

See `examples/blastem_input_script.example.json` and `examples/qa_emulator_report.json`.
