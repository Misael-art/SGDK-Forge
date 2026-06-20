# sprite-asset-budget-curator

Use when designing or converting playable characters, enemies, bosses, FX or sprite sheets for SGDK/Mega Drive.

## Purpose

Ensure sprite art is not merely pretty but hardware-shaped: indexed color, consistent bounding boxes, palette discipline, animation readability and scanline-aware decomposition.

## Required Inputs

- Model sheet or approved visual source.
- Animation list.
- Frame dimensions and origin.
- Palette target.
- Runtime sprite assembly plan.

## Required Outputs

- Sprite asset budget report.
- Palette and index policy.
- Frame origin/alignment policy.
- Hardware risks for scanline density and animation memory.

## Hard Rules

- Do not refine from rejected sprite sheets.
- Do not accept mutated design features across frames.
- Do not approve generated sheets without indexed palette, frame alignment and visual review evidence.

## Handoff

- Use `sprite-scanline-budgeter` for runtime limits.
- Use `palette-cram-curator` for palette ownership.
- Use `art-asset-diagnostic` when fidelity is in doubt.
