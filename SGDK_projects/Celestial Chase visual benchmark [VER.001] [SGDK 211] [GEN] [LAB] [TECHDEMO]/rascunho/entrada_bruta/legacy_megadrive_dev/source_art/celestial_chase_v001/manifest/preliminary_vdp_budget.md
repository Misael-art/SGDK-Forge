# Preliminary VDP Budget - Celestial Chase v001

Status: planning estimate, not validated budget.

## Verdict

`cabe com recuo`

The scene is feasible as a first visual benchmark if the approved source art is translated intelligently. It does not safely fit as naive full-source conversion or full-resident high-detail multi-plane art.

## Required Recuos

- Do not convert high-res source images directly to `IMAGE`.
- Start with a 320x224 proof and a split/flat comparison.
- Use discrete sprite swaps for fake-3D scale; no runtime scaling claim.
- Keep road motion in palette cycling, not tile redraw.
- Keep character/FX separate from background palettes.
- Treat near clockwork stag as modular or staged; full near-frame boss plus hero plus FX may exceed sprite scanline comfort.

## Scene-Local Resource Model

- `resource_loading_model`: `scene_local_preload`
- `BG_B`: atmosphere and distant horizon
- `BG_A`: road and gameplay lane
- `SPRITES`: hero, boss scale swaps, obstacles and FX
- `WINDOW`: reserved, not used in first benchmark
- `H-Int`: not required for first benchmark
- `CRAM updates`: road palette cycling, 4 slots, VBlank-safe

## VRAM Reasoning

SGDK 2.11 practical background tile space must be budgeted before runtime. Do not assume 2048 tiles are free.

Planning target:

- Use `SPR_initEx(128)` or equivalent small sprite reserve for the first visual benchmark if background pressure is high.
- Keep background resident tiles under roughly 900-1100 user tiles until measured.
- Keep hero active animation window under 6-8 frames.
- Keep boss active scale variants scene-local; avoid keeping all large variants plus all obstacles resident if not visible together.

## Sprite Pressure Risks

Worst frame candidate:

- hero large forward-facing pose
- clockwork stag near/mid scale
- 2 obstacles
- dust burst
- impact spark

Risk: `scanline_sprite_pressure_unmeasured`

Recuo:

- reduce overlapping FX near the hero
- split boss into fewer sprite columns
- use `BG_A` takeover for one close-impact moment if needed
- keep particle FX temporal and short-lived

## Palette Budget

| Palette | Owner | Risk |
|---|---|---|
| PAL0 | sky/distant atmosphere | low |
| PAL1 | road + palette cycling | medium, CRAM ownership required |
| PAL2 | protagonist | medium, must protect hero readability |
| PAL3 | boss/props/FX | high, may need runtime phase split |

## DMA / VBlank

First benchmark should avoid per-frame tile uploads. Per-frame work:

- CRAM rotation for PAL1 road slots
- sprite position/animation updates
- small camera shake via scroll only when impact fires

Road palette cycling is cheap if performed in VBlank-safe cadence.

## Budget Status By Axis

- `rom_asset_cost`: not measured
- `vram_resident_set`: estimated only
- `load_time_dma_cost`: acceptable if scene preloads
- `per_frame_dma_cost`: should be low if no tile streaming initially
- `active_animation_window`: required, not yet measured
- `scene_local_scope`: defined
- `scanline_sprite_pressure`: not measured

## Gate To Promote Budget

Budget cannot become `validado_budget` until:

1. Processed 320x224 and sprite candidates exist.
2. Tile counts are measured after indexed conversion.
3. Sprite frame envelopes are measured.
4. `resources.res` exists in a project.
5. ROM is built.
6. BlastEm capture shows no over-budget or visual corruption.
