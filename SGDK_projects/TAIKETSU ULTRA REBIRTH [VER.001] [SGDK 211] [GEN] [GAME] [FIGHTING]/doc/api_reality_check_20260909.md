# API reality check — VDP residency probe

Date: 2026-09-09

Verified against `sdk/sgdk-2.11/inc/`:

- `VDP_drawImageEx(VDPPlane, const Image *, u16, u16, u16, bool, bool)` is
  the active image path; the final boolean is the SGDK DMA request flag;
- `Sprite.attribut` is the SGDK 2.11 runtime attribute field and contains the
  allocated tile index; `TILE_INDEX_MASK` is defined by `vdp.h`;
- `Sprite.frame->tileset->numTile` is the tile count for the current frame;
- `SPR_addSprite` and `SPR_addSpriteSafe` are the SGDK 2.11 signatures used by
  this project;
- no invented VRAM getter or `SPR_getAnimationIndex` is used;
- the telemetry uses `u16`, `u32`, static arrays, and no floating point,
  `malloc`, or `free`.

The probe is diagnostic only. It does not replace the VBlank DMA queue or
change the scene's resource ownership.
