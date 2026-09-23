# color-conversion-curator

Use when converting external art styles or source platforms into Mega Drive constraints, including SNES-like art, PC-98-inspired art, high-color paintings, arcade references or AI-generated images.

## Purpose

Protect visual quality during conversion by making palette, dithering, tile reuse and style loss explicit before assets enter SGDK.

## Required Inputs

- Source image or style reference.
- Target Mega Drive palette budget.
- Tile/sprite/background role.
- Required visual identity to preserve.
- Accepted conversion loss.

## Required Outputs

- Conversion plan.
- Palette reduction strategy.
- Tile/sprite separation notes.
- Rejection criteria for muddy, flat or off-style output.

## Hard Rules

- Do not call a source "converted" just because it was resized.
- Do not accept opaqueness, desaturation or style drift as unavoidable without documenting palette alternatives.
- Do not use external platform tricks as if they are Mega Drive-native.

## High-color to Mega Drive flow (curation_batch_2026_06_16)

Source: high-color/true-color items of batch `curation_batch_2026_06_16`,
evidence `E1_text`, candidate expansion. Reuses the conversion plan and palette
reduction outputs; no new schema, no AAA/runtime promotion.

- Reduce 16/24-bit sources to 9-bit while preserving the dominant hue and
  functional contrast (reading hierarchy), not just nearest-color accuracy.
- Declare accepted loss explicitly: discarded tones, merged ramps, simplified
  highlights; an undocumented "it looks close enough" is not a conversion plan.
- Faking techniques (H-Int swap, palette cycling, Shadow/Highlight, structural
  dithering) are allowed only when explicitly routed to their VDP/color owners
  (`shadow-highlight-scroll-fx`, `raster-palette-hint-director`,
  `palette-cram-curator`); this skill does not implement them inline.
- Never promise real "true color"; the Mega Drive has 60 visible colors and the
  illusion must be declared as a technique, not as native true color.

## Handoff

- Use `palette-cram-curator` for CRAM.
- Use `art-translation-to-vdp` for hardware mapping.
- Use `visual-excellence-standards` for aesthetic review.
