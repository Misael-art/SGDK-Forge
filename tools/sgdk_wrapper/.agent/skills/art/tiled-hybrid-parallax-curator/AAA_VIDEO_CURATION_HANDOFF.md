# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when `tiled-hybrid-parallax-curator` maps Tiled or hybrid scene art into Mega Drive plane composition.

## New Required Routes

- Route per-cell palette/priority/flip decisions to `tilemap-attribute-director`.
- Route CRAM conflicts to `palette-cram-curator`.
- Route line-scroll or water/road effects to `hscroll-linescroll-road-fx`.
- Route Shadow/Highlight or raster palette claims to the dedicated hardware skills.

## Scene Rules

- Do not flatten parallax art if priority, palette or flip metadata is required.
- Plane composition must declare camera behavior and gameplay interaction.
- Tilemap metadata and art conversion must remain traceable to local project assets.
