# runtime_decision_log — HUD P2 WINDOW tiles

Date: 2026-09-11
Project: HAMOOPIG prototype / technical_demo
Claim ceiling: prototype. Not AAA.

## Why

P2 yellow as a 128px sprite disappeared on H40 (320 sprite-pixels/scanline and/or AUTO_VRAM after two large fighters). Pins inside 1532–1951 were evicted. Flipped PNG without HFlip still missing. Next honest lever: `window_plane_static_hud`.

## API

- `VDP_setWindowOnTop(2)` — `sdk/sgdk-2.11/inc/vdp.h`
- `VDP_fillTileMapRect` / `VDP_fillTileMapRectInc` / `VDP_setTileMapXY` on `WINDOW`
- `VDP_loadTileSet` + `VDP_loadTileData` after BG (`gInd_tileset`)
- `VDP_setWindowOff` + `VDP_clearPlane(WINDOW)` in `CLEAR_VDP`

## Contract

- owner: `src/hud.c`
- area: top 2 rows (16px), full 40 columns
- palette: PAL1
- priority: FALSE so P1/KO/clock sprites overlay
- Plane A: gameplay from y=16
- cadence: dirty tile columns when `hud_frame_for(energiaBase)` changes
- reset: `hud_p2_window_off()` on scene exit
- GE[4]/GE[6] not spawned

## Resource

- `TILESET ts_hud_p2_bar` NONE NONE ROW from `energy_yellow_p2_window.png` (frame 0, index 0→11)
- black fill tile: PAL1 index 11 via `VDP_loadTileData` (UI fill, not character art)

## Model

`full_resident` — 32 bar tiles + 1 black tile stacked after BG, below sprite pool.

## 2026-09-11 — P1 also WINDOW

Two Musgo idles (~95-100 tiles each) evicted the P1 128px sprite bar (`01_idle_hud.png` ROM c81fee9f, bar missing). Same contract as P2:

- `ts_hud_p1_bar` from `energy_yellow_p1_window.png` (frame 0, index 0→11)
- cols 1-16, depletes from the right toward KO
- `hud_window_load/init/update/off` owns both bars
- GE[3]/GE[5] not spawned
- ROM `77ea0cdd2433881b16d515ef5dd7af0e2c48475c987dc75cefdc6ff61202f8bc`
- Evidence: `out/emulator_evidence/interactive-musgo-fight-20260911T220349Z/01_idle_hud.png`

Resident now 32+32+1 tiles after BG. Red lag still omitted (same as P2). Prototype.

## 2026-09-11 — clock also WINDOW

`spr_n*` at y=26 used AUTO_VRAM (pins 1441/1447 still evictable). Clock is now plane tiles:

- `ts_hud_clock` from `clock_digits_window.png` (n0–n9 packed 160x16, index 0→11)
- WINDOW `VDP_setWindowOnTop(5)`: bars rows 0-1, digits rows 3-4 (y=24, under KO)
- cols 18-19 left digit, 20-21 right digit
- `ClockL`/`ClockR` not spawned
- ROM `a53bc06beba88ace362e8e4b226c5db0d22cb4a18a8c10cc7b818d11afec1561`
- Evidence: `out/emulator_evidence/interactive-musgo-fight-20260911T221658Z/01_idle_hud.png` (98), `06_hit.png` (89)

Resident +40 digit tiles. KO remains sprite. Prototype.
