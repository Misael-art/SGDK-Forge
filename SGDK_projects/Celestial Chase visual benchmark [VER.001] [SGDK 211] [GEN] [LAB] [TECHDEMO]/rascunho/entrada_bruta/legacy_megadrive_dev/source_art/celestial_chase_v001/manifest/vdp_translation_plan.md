# VDP Translation Plan - Celestial Chase v001

Status: approved source art, translation planning.

## Scene Goal

Create a high-quality Mega Drive forced-perspective chase scene inspired by 1994-era hardware craft: a static-but-animated perspective stone road, fake-3D sprite scale swaps, palette cycling, dust/impact FX and strong anime storybook visual identity.

This is not a direct visual clone. The implementation preserves the technical family and creates original characters, props and scene language.

## Translation Targets

| Asset | Target | Status |
|---|---|---|
| `scene_concept` | reference anchor | approved source |
| `star_wanderer_model_sheet` | authorial model sheet | approved source |
| `star_wanderer_key_poses` | key pose sheet, not animation | approved source |
| `clockwork_desert_stag_model_scale` | boss scale-swap source | approved source |
| `cosmic_desert_chase_background` | `scene_slice`, background plate | approved source |
| `palette_cycling_stone_road_study` | material study for CRAM cycling | approved source |
| `chase_obstacle_props` | prop sprite/tile source | approved source |
| `chase_fx_sheet` | FX sprite source | approved source |

## Semantic Parse Report

### Background Plate

- `scene_plane_sky`: distant sky, stars, planetoids, low detail; intended for `BG_B`.
- `scene_plane_ground`: road, stone bands, perspective grooves; intended for `BG_A` or a flat scene proof depending on tile count.
- `scene_plane_foreground_composition`: large near-road stones and edge details; candidate for `BG_A` plus optional sprite grafts.
- `drop/ignore`: none in the approved source, but high-res source is not a playable asset by itself.

### Road Study

- `palette_cycle_band_group`: 4-tone stone bands must map to stable CRAM slots.
- `static_geometry`: slabs and grooves should remain mostly static; motion comes from color rotation.
- `must_drop`: random micro-cracks that destroy tile reuse or cycling readability.

### Characters

- `star_wanderer_key_poses`: `key_pose_sheet`, not an animation strip.
- `clockwork_desert_stag_model_scale`: scale ladder source for fake-3D sprite swaps; final runtime should use 4-5 discrete sizes, not smooth scaling.

### Props and FX

- `props`: isolate obstacle families into near/mid/far sprite variants.
- `fx`: isolate dust, sparks, chips and impact rings as separate sprites; never bake FX into character sheets.

## Layer Plan

### Preferred Route: `elite_split_scene`

- `BG_B`: sky, stars, distant dunes, far horizon, low-detail atmospheric depth.
- `BG_A`: stone road, perspective bands, near route markers and gameplay lane.
- `SPRITES`: protagonist, clockwork stag scale swaps, obstacles, dust puffs, impact rings and star sparks.
- `WINDOW`: reserved for no HUD in first visual benchmark; must stay available for later UI.

### Fallback Route: `compare_flat`

Use a single 320x224 translated background if the split background exceeds practical tile residency. This fallback is acceptable only as a first ROM proof and must be documented as budget fallback, not final visual ambition.

## Palette Plan

### PAL0 - Background Atmosphere

- Deep navy sky
- Blue-violet shadow
- Distant dune gray-blue
- Pale star/moon highlight
- Warm tiny star accent

### PAL1 - Road / Palette Cycling

Reserve contiguous slots for the cycling band group:

- `PAL1[4]`: dark trough
- `PAL1[5]`: violet stone shadow
- `PAL1[6]`: blue-gray stone base
- `PAL1[7]`: pale moonlit edge

Rotation cadence seed: rotate every 2 frames during normal sprint; slow to every 4-6 frames for stumble/recovery. This links visual FX to gameplay state.

### PAL2 - Protagonist / Hero Materials

- Transparent index 0
- Deep outline
- Ivory cloth base/highlight
- Cold blue cloth shadow
- Indigo cape ramp
- Auburn hair ramp
- Warm gold clasp/satchel accents
- Skin/face warm ramp

### PAL3 - Boss / Props / FX Shared

- Transparent index 0
- Dark violet outline
- Brass gold ramp
- Stone gray-blue ramp
- Amber eye/spark accent
- Dust pale highlight

If PAL3 becomes overloaded, split boss and FX into separate runtime phases or borrow small FX colors from PAL1/PAL2 only with explicit `borrowed_fx_ramp` decision.

## Sprite and Animation Contracts

### Protagonist

- `asset_kind`: model sheet approved; key pose sheet approved; no final animation strip yet.
- First playable visual benchmark can use 4 pose-swapped frames for a forward-run illusion.
- Production animation still requires one-action strips:
  - `run_toward_camera`: 6-8 frames
  - `stumble_recovery`: 4 frames
  - `dodge_left_right`: 3-4 frames
  - `look_back_panic`: 2-3 frames
- Pivot policy: bottom-center feet for all grounded poses.
- Frame envelope seed: 48x64 or 64x80 depending on readability after downscale.
- Hero must remain visually dominant over the road palette cycling.

### Clockwork Desert Stag

- First runtime route: 4 or 5 hand-drawn scale variants, swapped by distance state.
- Do not use runtime scaling. Mega Drive has no sprite scaling.
- Candidate scale ladder:
  - far: 48x40
  - mid: 80x64
  - near: 128x96
  - impact/close: modular head/hoof sprites or BG takeover if needed
- Giant near state may require modular boss rig or `BG_A/BG_B` plane takeover.

### Obstacles and FX

- Obstacles should have near/mid/far variants, not software scaling.
- Dust and impact rings are separate sprites with brief lifetimes.
- FX may use temporal alternation for non-critical particles only.

## Dithering and Material Plan

- Stone: controlled 2x2 and broken-band dithering, not random crack noise.
- Sky/dunes: lower detail than gameplay lane.
- Brass: hard highlight blocks, no photographic ramps.
- Dust: chunky clusters readable against both road and sky.

## Basic vs Elite Translation

### Basic

- Downscale/crop to 320x224.
- Quantize as a control image.
- Useful only to reveal what breaks.

### Elite

- Recompose from semantic regions.
- Preserve road band logic and palette slots.
- Reduce background detail before reducing protagonist readability.
- Use curated palettes and tile-aware simplification.
- Produce `original + basic + elite` contact board for review.

## Blockers Until Next Step

- `not_translated_to_vdp`
- `not_budget_validated`
- `no_animation_strip_contracts`
- `no_source_to_rom_asset_map`
- `not_built`
- `not_tested_in_emulator`

## Handoff

Next handoff goes to:

1. `multi-plane-composition` for exact `BG_A/BG_B/SPRITES` split and fallback.
2. `megadrive-vdp-budget-analyst` for preliminary `cabe/cabe com recuo/nao cabe`.
3. `art-conversion-pipeline` for processed preview variants, not direct `res/` promotion.
