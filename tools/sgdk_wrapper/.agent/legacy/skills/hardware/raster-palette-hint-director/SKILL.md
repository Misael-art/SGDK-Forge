# raster-palette-hint-director

Use when a scene claims raster color changes, mid-frame palette swaps, waterline color shifts, sky gradients or H-Interrupt-driven palette effects.

## Purpose

Keep raster-style color effects honest: they must declare timing, affected palettes and risk of CRAM artifacts.

## Required Inputs

- Target scanline or moving boundary.
- Palette entries to change.
- H-Int or timed update strategy.
- Interaction with fades, UI, sprites and Shadow/Highlight.

## Required Outputs

- Raster palette plan.
- CRAM write budget and affected palette slots.
- Fallback for emulators/hardware where artifacts appear.
- Evidence requirement before visual approval.

## Hard Rules

- Do not present mid-frame palette changes as free extra colors.
- Do not overwrite shared palette slots used by sprites or UI.
- Do not claim smooth alpha blending; Mega Drive has Shadow/Highlight and palette tricks, not general alpha.

## Scene-state raster rules (curation_batch_2026_06_16)

Source: raster/H-Int items of batch `curation_batch_2026_06_16`, evidence
`E1_text`, candidate expansion. Reuses the existing raster palette plan and CRAM
budget outputs; no new schema, no AAA/runtime promotion.

- H-Int / palette swap is a scene-state technique, not loose decoration: it must
  serve a declared scene state (waterline, sky band, boss room tint, weak spot),
  never be applied as a free cosmetic layer.
- When a frame has more than one split, require a per-frame interrupt map listing
  target scanlines, affected palette slots and reset order.
- Require a visual fallback if the H-Int is removed or the effect does not fit
  the frame budget; the scene must still read correctly without the raster trick.
- Production approval still requires a screenshot plus VDP/CRAM evidence for any
  mid-frame claim; without it the result stays lab evidence only.

## Handoff

- Use `palette-cram-curator` for ownership.
- Use `game-state-transition-architect` when fades also touch CRAM.
- Use `megadrive-vdp-budget-analyst` for timing risk.
