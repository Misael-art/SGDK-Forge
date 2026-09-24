# Runtime decision log — VDP residency probe

Date: 2026-09-09
Project: TAIKETSU ULTRA REBIRTH [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]

## Decision

Instrument the D1 fight scene's real resource path with a small, project-local
VLAB extension. Record the tile ranges requested by the two `IMAGE` loads and
the two active `SPRITE` allocations. Keep the existing aggregate metrics and
append the ranges after them so older SRAM readers remain compatible.

## Runtime model

- model: `scene_local_preload`
- owner: `src/scenes/scene_demo.c` for scene requests; `src/system/runtime_probe.c` for telemetry
- scene enter loads `img_fighting_room_0_bgb` at `TILE_USER_INDEX`, then
  `img_fighting_room_0_bga` immediately after it;
- `SPR_addSprite`/`SPR_addSpriteSafe` use SGDK automatic VRAM allocation and
  automatic tile upload, so their returned `Sprite.attribut` is recorded only
  after allocation succeeds;
- the probe records distinct half-open tile ranges, deduplicates only already
  covered redraws, and carries an overflow bit;
- no manual DMA is added to gameplay and no VBlank ownership changes.

## Claim boundary

This proves the ranges requested/allocated by the observed D1 scene and binds
them to the captured ROM. It does not prove full VRAM occupancy for every
scene, final approved fighter art, sprite animation-window residency, DMA
worst-case under all transitions, or sustained performance. The VDP decision
therefore remains `cabe_com_recuo`, not `validado_budget`.

## Rejected routes

- no direct VRAM read is claimed from the partial VLAB dump;
- no inferred final-art residency is promoted from placeholder resources;
- no Windows/Win32 capture route is involved;
- no changes to game behavior or asset pixels are part of this decision.
