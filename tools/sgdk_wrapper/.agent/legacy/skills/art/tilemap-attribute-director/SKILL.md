# tilemap-attribute-director

Use when a Mega Drive scene depends on per-cell tilemap attributes: palette select, priority, H-flip, V-flip, metatile grouping or 16 Tile-style exports.

## Purpose

Turn background composition into explicit VDP tile descriptor data instead of treating a PNG as a flat image. This skill exists because AAA-looking Mega Drive scenes need controlled priority, palette reuse and flip-based tile savings at tilemap level.

## Required Inputs

- Source tileset and tilemap export.
- Target plane: `BG_A`, `BG_B` or `WINDOW`.
- Intended metatile size.
- Palette ownership plan.
- Priority rules for player, enemies, props and foreground occluders.

## Required Outputs

- Tilemap attribute report with palette, priority, H/V flip and tile index policy.
- Explicit list of tiles that rely on priority for depth.
- Flip/deduplication notes for VRAM savings.
- Unique-tile report with normal/H/V/HV equivalence, saved tile count and any
  cell whose reuse depends on a flip flag.
- Per-tile palette conflict report: any 8x8 cell using more colors or palette
  slots than the selected sub-palette permits blocks promotion until the color
  owner resolves it.
- Handoff to `megadrive-vdp-budget-analyst` before any release or AAA claim.

## Hard Rules

- Do not approve a scene from visual similarity alone.
- Do not collapse all cells into one static `TILE_ATTR_FULL` unless every tile truly shares the same attributes.
- Do not use per-cell palette swaps as decoration without a CRAM ownership plan.
- Do not treat H/V flip as visual rotation. It is only axis mirroring encoded in
  tile descriptor flags.
- Do not assign high priority by visual guess. Priority tiles need a gameplay
  occlusion reason and a sprite interaction policy.
- Do not "fix" palette conflicts by blind quantization. Suggest hue/ramp
  consolidation, then require a new palette conflict report.
- If a tool export cannot preserve per-cell metadata, mark it `blocked_for_tilemap_attribute_pipeline`.

## Candidate Curation Note

Source: attached video-transcript summary reviewed on 2026-06-17,
`E1_text`. The useful addition is not the vocabulary of 16-bit tile words; that
was already covered. The retained rule is stricter reporting: unique tile count,
normal/H/V/HV reuse, priority intent and per-tile palette conflicts must be
explicit before a background can be treated as production-ready.

## Handoff

- Use `palette-cram-curator` for palette allocation.
- Use `multi-plane-composition` for plane ownership and camera behavior.
- Use `aaa-pipeline-guardian` for any advanced scene claim.
