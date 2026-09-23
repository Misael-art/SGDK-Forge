# runtime_decision_log — Showdown park (compare_flat)

Date: 2026-09-11
Project: HAMOOPIG prototype / technical_demo
Claim ceiling: `compare_flat_runtime_prototype`. Capcom XMvSF park is study/placeholder (same policy as Ken). Not AAA. Not delivery IP.

## Why

Fight BG was the upstream `gfx_bgb1`/`gfx_bgb2` plates. User asked to put the Showdown-at-the-Park GIF into the live fight while keeping visual masses, H/V flow and jump camera.

Source: `data/source_art/showdown/xmen-vs-streetfighter-stage-showdown-at-the-park.gif` plus MUGEN `showdown.def`.

## VRAM / palette

- Native GIF: 639x449, 84 colours, 17 frames RGB-identical (water anim not in this GIF).
- Unique 8x8 tiles at native: ~3191. Cannot reside next to two Musgo fighters + WINDOW HUD.
- Four palettes already taken: PAL0 BG, PAL1 HUD, PAL2/PAL3 fighters. No second BG pal.
- Route: `compare_flat` one IMAGE on BG_B.
- Builder `data/source_art/showdown/convert_showdown.py`: nearest 512x256, 4px block, 10-colour median-cut + 9-bit snap → 444 unique tiles, 10 colours on PAL0.

## Camera (from showdown.def)

MUGEN: boundleft/right ±224, boundhigh -240, verticalfollow 0.5, tension 50, zoffset 215.

MD runtime (`FUNCAO_CAMERA_BGANIM`):

- H: midpoint of the two fighters, clamp 0 … `gBG_Width-320` (192 px travel).
- V: `camPosY = max(air1,air2)/2` clamped 0 … 32 (`gBG_Height-224`).
- Rest: `VDP_setVerticalScroll(BG_B, 32)` so the floor is in the 224 viewport.
- Jump: vscroll decreases toward 0 (look up / extra sky). Fighters and shadows get `+camPosY` so they stay with the floor.
- WINDOW HUD (5 rows / 40 px) stays pinned; it eats part of the extra sky but the park masses still drop on screen.

Parallax deltas BG0 0.43/0.285, BG1/BG2 0.71/0.635, BG3 1/1 are recorded in `doc/art/showdown/camera_motion_contract.json` and **not executed**. One pal / one plane.

## Spark / fireball

Spawn and fireball screen Y now include `+camPosY`. Sparks still do not track after spawn (28-frame life).

## Not done

- Multi-plane parallax
- Water animation (GIF frames are RGB-identical)
- Native tile residency of the 3191-tile source
- V travel of 240 px (MUGEN boundhigh); MD has 32 px on a 64x32 plane
- Authorial replacement of Capcom park

## Evidence (2026-09-11)

- ROM sha256 `1eb99f6c33cc6fe1c7fb776f5635f31b453a6419f27ff77cd4a215db9e6b00d6`
- wine_bridge `buildado` `out/logs/linux_wine_build_report.json`
- BlastEm 59.6 fps `out/emulator_evidence/interactive-showdown-20260911T225648Z/`
  - `01_idle_hud.png` park + WINDOW bars/clock 98
  - `02_walk_left.png` / `03_walk_right.png` H camera
  - `05_jump_peak.png` P1 airborne, clock 99
  - `06_land.png` camera rest
  - `07_hit.png` spark, clock 88
- Bundle VLAB not sealed. Prototype.
