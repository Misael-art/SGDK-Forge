# palette-cram-curator

Use when a Mega Drive asset, scene or sprite set needs palette planning, 9-bit color quantization, CRAM ownership or per-palette conflict resolution.

## Purpose

Prevent dull, muddy or illegal color output by turning color choices into a measurable CRAM contract. The Mega Drive has 4 sub-palettes of 16 entries, 9-bit RGB color and strict index behavior.

## Required Inputs

- Source artwork.
- Intended owner of each palette: background, sprites, UI, FX or transition.
- Transparency index requirements.
- Color conversion target: native 9-bit, SGDK-safe RGB steps, or tool-specific indexed palette.

## Required Outputs

- Palette ownership table.
- Index 0 transparency policy.
- Quantization decision and known tradeoffs.
- Conflict list for colors shared across animated tiles, sprites and UI.

## Hard Rules

- Do not claim vibrant colors if the indexed palette has not been inspected.
- Do not mix sprite and background palette ownership casually.
- Do not count visual screenshots as palette proof without indexed source or VDP/CRAM evidence.
- Do not introduce high-color claims unless they are backed by H-Int, palette cycling, Shadow/Highlight or another explicit hardware strategy.

## Temporal CRAM techniques (curation_batch_2026_06_16)

Source: palette/CRAM items of batch `curation_batch_2026_06_16`, evidence
`E1_text`, candidate expansion. Reuses the palette ownership table and CRAM
contract outputs; no new schema, no AAA/runtime promotion.

- **Fade in/out** must declare a CRAM schedule across frames (which slots, which
  9-bit steps, how many frames) instead of an abstract "fade".
- **Crossfade between palettes** must declare 9-bit interpolation across N frames,
  with the per-slot start/end colors documented.
- **Hit flash** is 1-3 frames with an explicit restoration step: which slots are
  forced, for how long, and the exact restore back to the owned palette.
- **Palette cycling** must declare ownership, cadence, the CRAM slots it rotates
  and the scene reset; it cannot steal player, HUD, damage or critical-FX slots.
- A palette change never proves runtime behavior without capture/emulator
  evidence (screenshot + VDP/CRAM dump); without it the change stays planning
  only.

## Handoff

- Use `shadow-highlight-scroll-fx` for Shadow/Highlight scenes.
- Use `raster-palette-hint-director` for mid-frame palette changes.
- Use `art-translation-to-vdp` when converting high-color sources.
