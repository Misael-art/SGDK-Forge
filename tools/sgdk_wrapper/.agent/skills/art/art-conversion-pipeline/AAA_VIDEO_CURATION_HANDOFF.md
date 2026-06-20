# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when `art-conversion-pipeline` converts source art into Mega Drive-ready backgrounds, sprites, tilesets or effects.

## New Required Routes

- Route high-color, SNES-like, PC-98-like, arcade or AI source art to `color-conversion-curator`.
- Route palette ownership to `palette-cram-curator`.
- Route per-cell background metadata to `tilemap-attribute-director`.
- Route sprite sheets to `sprite-asset-budget-curator`.
- Route final hardware proof to `emulator-vdp-evidence-curator`.

## Acceptance Rules

- Conversion is not resize-only.
- Color vibrance must be supported by indexed palette decisions.
- Tile reuse, H/V flip and priority must be documented when background art becomes a tilemap.
- Asset conversion automation remains backlog until scripts and local corpus are validated.
