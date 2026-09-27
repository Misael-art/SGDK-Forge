# Suzaku staging candidate review — 2026-09-26

## Decision

The locked-palette candidate is the strongest measured staging route so far. It
reduces tile count while preserving the project's previous six-color palette.
Keep it in `rascunho/processado/stage_takeover/`; do not copy it into
`res/` or call the stage complete. It has no visual approval, tilemap flag
proof, runtime residency, camera motion, DMA/VBlank, audio, or BlastEm evidence.

## Candidate and source binding

- Candidate directory:
  `rascunho/processado/stage_takeover/suzaku_panorama_world640_6color_simplified_locked_palette_planes_20260926/`
- The new far plate is an AI-generated concept asset staged at
  `rascunho/processado/stage_takeover/ai_concept_suzaku_panorama_bg_b_simplified_20260926.png`.
  Its prompt, source hash, dimensions, and pending approval are recorded in
  `doc/art/stage_panorama_bg_b_simplified_provenance_2026_09_26.json`.
- Cropping, world-width conversion, and recomposition are hash-bound by
  `doc/art/stage_panorama_world640_bg_b_simplified_provenance_2026_09_26.json`.
- The candidate keeps the old six-color palette through the new
  `locked_palette_v1` option in `forge-art`. Conversion report SHA-256:
  `c0bf48c2f7daa0610d9e1f026abf327924e78e0dc6b6e1d3021aaf83d31dc369`.
  The source-to-palette weighted MSE is `362.21763392857144`; this is a
  technical metric, not a visual quality score.
- Pixel reconstruction against the indexed palette candidate is exact
  (`mismatch_pixels=0`). The candidate is 640x224; it does not implement the
  proposed 768px source camera span or runtime scrolling.

## Measured comparison

All `.res` studies used the same pinned SGDK ResComp 3.95 jar.

| Route | BG_B tiles | BG_A tiles | Paired sum | Flat tiles | Paired bytes | Flat bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Previous six-color control | 208 | 252 | 460 | 425 | 16,574 | 15,222 |
| New locked-palette candidate | 186 | 252 | 438 | 408 | 15,876 | 14,648 |

The candidate saves 22 paired tiles and 17 flat tiles against the previous
control. The flat study is a capacity comparison only; it removes independent
BG_A/B scrolling. The paired route has 8 tiles of headroom against the current
446-tile capacity estimate. That estimate is not runtime proof and the small
margin means the live HUD, fighters, effects, transient uploads, and fragmented
VRAM must be measured before integration.

The exact indexed-pattern probe found four patterns shared across BG_A/B, for a
possible 434-tile union if runtime shares tile IDs. The runtime common-tileset
layout is not implemented or proven, so the official paired measurement remains
438. No four-tile saving is claimed.

The per-tile audit checks every 8x8 cell of each plane. It found zero palette
conflicts; the maximum visible indices in one tile are 4 for BG_B and 5 for
BG_A. BG_B keeps index 0 unused; BG_A uses index 0 only as declared
transparency. The generated report is
`per_tile_palette_conflict_report.json` in the candidate directory. The
reproducible report generator is `generate_candidate_audit_reports.py`.

The generated scene report is
`scene_tilemap_conversion_candidate_report.json`. It records the sources,
hashes, exact reconstruction, ResComp output and claim ceiling. This project
does not yet have a dedicated schema for that aggregate report.

## Rejected comparison

Unconstrained weighted re-quantization produced 487 paired tiles (BG_B 182 +
BG_A 305) and altered the existing BG_A palette. Its palette shift darkened and
changed the castle/floor. It is not the chosen route. The locked-palette
candidate held BG_A at 252 tiles and therefore isolates the far-plane change.

## Follow-up art alternatives

The first contact sheet places camera windows at x=0,160,320 side by side.
They overlap by 160 pixels; a moon or castle appearing in more than one panel
is the same world landmark, not duplicated artwork. An earlier suspicion of
repetition was corrected after checking source coordinates. The original V1
candidate remains a valid control.

Two additional art tests used the same 640x224 near plate, locked six-color
reference, scene decomposition, and ResComp 3.95:

| Candidate | Palette | BG_B + BG_A | Flat | Paired bytes | Weighted MSE | Budget estimate |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| V1 simple far plane | 6 colors, locked | 438 (186 + 252) | 408 | 15,876 | 362.218 | 8 tiles estimated spare |
| V2 detailed far castle | 8 colors, weighted | 1,664 (1,352 + 312) | 993 | 58,342 | 386.473 | 1,218 tiles over |
| V3 sparse atmosphere, locked | 6 colors, locked | 446 (194 + 252) | 391 | 16,084 | 337.696 | exactly at estimate |
| V3 sparse atmosphere, weighted | 8 colors, weighted | 571 (269 + 302) | 514 | 20,260 | 235.530 | 125 tiles over |

V3 locked-six is the strongest current art-to-cost candidate: the clouds and
moon read more naturally in a fighter/HUD context mock, and palette error is
lower than V1. Its paired tile count equals the 446 capacity estimate, leaving
no measured slack. It is not safe to integrate until the capacity is reconciled
with live VRAM, fragmenting, HUD, fighters, and simultaneous effects. V3
weighted-eight has lower color error but fails the estimate. V2's detailed
castle adds too many distinct tile patterns and is rejected for the current
resident route.

V3 locked-six reconstructs exactly from the separated indexed planes. The
per-tile scan found zero palette conflicts, with at most 2 visible indices in
BG_B and 5 in BG_A. Reports are
`suzaku_far_overlay_v3_world640_locked_palette_planes_20260926/per_tile_palette_conflict_report.json`
and `suzaku_far_overlay_v3_world640_locked_palette_planes_20260926/scene_tilemap_conversion_candidate_report.json`.
The tilemap flag report remains intentionally absent because the ResComp MAP
payload has not been decoded.

`suzaku_visual_context_mock_20260926.png` shows V1, V3 locked-six, and V3
weighted-eight behind fighters and HUD retained from an older 2026-09-25
capture. It replaces only exact matches to that screenshot's flat background
color and uses provisional far/near scroll rates at camera x=160. It is a
static composition mock, not a ROM screenshot, current-game validation, or
visual approval. Details and hashes are in
`suzaku_visual_context_mock_report.json`.

## Blockers before a real stage asset

1. Review the full-size 320x224 camera windows at 1x with fighters and the
   current HUD; the context mock is a static study based on an older ROM.
2. Resolve the world-width decision: the translation candidate is 640px, while
   the source storyboard proposes 768px and the runtime currently uses 640px.
3. Decode the actual ResComp `MAP` payload, or add a verified exporter, before
   issuing `tilemap_flag_report`. The current MAP metatiles and blocks are
   APLIB-packed. Do not invent tile indices or report assumed palette,
   priority, or H/V-flip flags as preserved.
4. Validate transparency/occlusion with the fighters, HUD, floor contact, and
   all camera endpoints. The current planes are not a camera-motion test.
5. Reconcile the 438-tile result with live VRAM residency, sprite-pool
   fragmentation, scanline pressure, transition DMA, per-frame DMA/VBlank,
   BG5 animation, and a maximal simultaneous-effects scene.
6. Author and integrate the Suzaku music only after selecting the runtime audio
   owner; confirm actual XGM2 playback with the stage and gameplay SFX.
7. Only after these checks: use the stage assets in `res/`, build a ROM, and
   capture the exact ROM in BlastEm. Visual, movement, audio, performance, and
   coverage gates stay separate.

## Reproducible evidence

- ResComp comparison: `rescomp_measurement_report.json`.
- Indexed planes and exact reconstruction: `stage_plane_assets_report.json`.
- Palette audit and this aggregate report: candidate directory above.
- Camera contact sheet: `camera_preview_contact_960x224.png` in the same folder.
- ResComp study is staging-only: `.res` is not referenced by project
  `res/resources.res`.
- Tests: `python3 -m pytest tools/mugen2sgdk_forge/tests -q` — **120 passed**.
- `forge-art self-check`: **142/142 fixtures passed** after adding
  `locked_palette_v1`.

No asset, camera profile, runtime integration, audio, or AAA claim is approved
by this report.

## Tile-economy follow-up — 2026-09-26

### Two-plane V8/V9 controls

The shared-15-color V8/V9 plates reconstruct their high-resolution composite
exactly, but the pinned ResComp count is **1,753 tiles** (BG_B 1,045 + BG_A
708), far above the historical 446-tile stage estimate. A deterministic
semantic/mask-constrained medoid experiment reduced that to 390/410/436 tiles
for budgets 400/420/446; ResComp matched the canonical H/V pattern counts and
the BG_A alpha mask remained pixel-identical. The controls visibly damage the
moon, castle masonry and platform with repeated/incorrect whole-tile detail, so
all three are rejected for production art. Evidence:

- `rascunho/processado/stage_takeover/suzaku_v8_v9_plane_rescomp_report_20260926.json`
- `rascunho/processado/stage_takeover/suzaku_v8_v9_semantic_tile_controls_20260926/semantic_mask_tile_compression_report.json`
- `rascunho/processado/stage_takeover/suzaku_v8_v9_semantic_tile_controls_20260926/semantic_mask_tile_rescomp_report.json`

The reusable lesson is that exact silhouette-mask preservation does not protect
semantic structure or visual quality when whole tiles are substituted. A
passing tile count is only a cost result; it cannot promote a visibly damaged
stage.

### V10 authored-pattern concept

An AI-generated tile-conscious concept is retained as a new laboratory source,
not an approved asset:

- Provenance: `doc/art/stage_v10_modular_tile_economy_provenance_2026_09_26.json`
- Source: `rascunho/inputs/suzaku_v10_modular_tile_economy_ai_concept_20260926.png`,
  SHA-256 `43cbd4ccb23ddd1bc01d855d2f0b4d56bee980e384d9154bf9f88dd30cb42d62`
- The 15-color shared-palette technical control measures **989 tiles / 34,776
  bytes**; an independently quantized eight-color control measures 961 / 33,856;
  the prior locked six-color palette measures **844 / 29,786**. Palette
  reduction alone is not the tile-economy route.
- The six-color candidate is readable in a 1x mock with fighters and HUD, but
  the mock uses the older 2026-09-25 capture and is not emulator evidence or
  visual approval. Mock: `rascunho/processado/stage_takeover/suzaku_stage_context_compare_20260926/fighter_hud_context_1x.png`.
- Exact H/V-canonical viewport counts for the locked-six candidate range
  424–471 tiles in aligned 320px windows, 442–483 for a sub-tile 41-column
  window, and 454–494 with one additional prefetch column. The peak exceeds
  the historical 446 estimate; profile:
  `rascunho/processado/stage_takeover/v10_6_viewport_tile_profile_20260926.json`.

The V10 source and controls are outside `res/`; no runtime or ROM changed. A
separate allocator probe on diagnostic ROM
`37fd9eb8e35464262bec4fa876c6ef0ff19d96d7678125152e42c534ae44ac11` observed
largest contiguous free block 72 tiles without a stage, dummy audio and no
production timing claim. It does not authorize reducing the 600-tile sprite
pool or imply that the historic 446 estimate is current.

### Next production route

Do not run more palette-only or generic medoid reductions against the same
full-detail source. Re-author the stage from a small, visually coherent set of
authored/reusable material tiles while preserving unique castle silhouettes,
moon, lanterns, platform edges and floor contact. Measure ResComp after each
authored module, then sweep every camera window and confirm that the full
fight-state residency still leaves a contiguous sprite-animation reserve.
Separately measure scanline pressure before testing shadow/adornment
multiplexing; those techniques do not free tile VRAM by themselves. Keep the
world-width, two-plane ownership, MAP flags, streaming/DMA, BG5 schedule, music,
current-ROM budget and BlastEm verification as independent gates.


## Isolated BGM audition capture — 2026-09-26

- The disposable audio-audition ROM built through the selected Linux SGDK bridge
  and was observed in fight scene `3` in BlastEm. ROM SHA-256:
  `fa7d859b666601ea3c0d2567031c15723a996d16237674c9c4b8076557427d72`. The
  sealed bundle is `rascunho/processado/suzaku_fight_audio/blastem_auditions/blastem-linux-20260926T090235Z-2327237/`; the capture is isolated from the
  production evidence root.
- BlastEm recorded 39.893333 seconds of 48 kHz stereo float output. The
  derived PCM WAV passes signal-presence, duration, and no-clipping checks
  (peak -7.96 dBFS; RMS -22.60 dBFS). Both stereo channels are identical, as
  expected from this mono-output capture. These metrics prove signal integrity
  only. They do not prove musical approval, loop seam, mix, or cue priority.
- The window title snapshot was 59.7 fps. The ROM probe reports 74 over-budget
  frames in its fixed 1200-frame measurement window, maximum CPU load 146,
  maximum scanline sprites 10, and maximum active sprites 5. Treat this as a
  performance warning for the instrumented fight ROM; the cause has not been
  isolated to BGM, and a single FPS title value does not clear sustained
  cadence.
- The captured frame is still the flat-background fight placeholder. It
  confirms scene execution for the audio audition and provides no Suzaku stage
  art evidence. Human listening and a matched BGM-off CPU control remain open.
- Full capture/audio facts, hashes, host/toolchain/runtime/creative classification,
  and exact invocation are in
  `rascunho/processado/suzaku_fight_audio/blastem_auditions/blastem-linux-20260926T090235Z-2327237/audio_audition_review.json`.

## V13–V16 floor and backdrop controls — 2026-09-26

- V13 keeps the authored composite and shifts it to place fighter feet on the
  planned contact line. Flat ResComp measures 915 unique tiles / 32,068 resource
  bytes; the worst 42-column camera window is 543 tiles.
- V14 is a new AI concept asked to use reusable tile materials. Its 12-color
  control still measures 1,344 tiles / 46,952 bytes, with a 762-tile worst
  viewport. Tile-conscious wording alone did not produce a viable economy.
- V15 tests the documented backdrop route: 64,630 connected sky pixels were
  made transparent and the exact reconstruction uses CRAM index 3. ResComp
  rises to 924 tiles / 32,380 bytes and the worst viewport to 547. This is a
  measured negative result: the candidate saves neither a CRAM slot nor tiles.
- V16 repeats one exact 64x8 authored deck-material module ten times in the
  floor-course band. It changes 2,459 pixels, introduces no palette indices or
  non-source tile patterns, and measures 846 tiles / 29,624 resource bytes.
  The worst 42-column window drops to 510 tiles, 33 below V13, but remains 64
  above the historical 446-tile estimate. The contact mock shows a more regular
  floor rhythm; human review of repetition and material continuity is pending.
- A static six-panel context mock compares V13 and V16 at camera offsets 0/160/320:
  `rascunho/processado/stage_takeover/suzaku_v13_v16_context_mock_20260926.png`.
  Its report binds the source screenshot and candidate hashes. It is not ROM,
  camera, palette, priority, or VDP evidence.
- `VDP_setBackgroundColor(u8)` selects a global CRAM index masked to 0..63; it
  does not load RGB or reserve a color. Reusing an exact loaded CRAM word is
  conditional, and transparent pixels reveal the backdrop only if lower planes
  leave them exposed. Opaque use of that color still requires the CRAM entry.
  The corresponding visual-direction and VDP-budget skill guidance now states
  these limits explicitly.

All V13–V16 files remain in staging; no resource, runtime, or production ROM
uses them. The stage, two-plane/camera contract, human art approval, audio
listening, and full-fight BlastEm budget remain open.

## Source-composited anchor and HUD-occlusion erratum — 2026-09-26

- The actual MUGEN DEF/SFF layers BG0a/BG0b and BG1..BG4 were recomposed at the
  center camera anchor (224). Before palette conversion, the two-plane
  reconstruction has zero pixel differences from the offline MUGEN compositor.
  This is the preferred fidelity control for later trials; it does not yet
  reproduce autonomous layer motion, the full camera world, or BG5 timing.
- At 15 shared stage colors, ResComp 3.95 reports 758 paired-plane tiles / 26,736
  resource bytes (flat control 712 / 24,994). At eight colors it reports 685 /
  24,182 (flat control 640 / 22,604). Against the source composite, RGB MAE/RMSE
  are 12.169/15.442 for 15 colors and 15.030/19.390 for eight. Neither version
  is art-approved. The 15-color route is visibly and numerically closer, but it
  conflicts with current CRAM ownership: PAL0 slots 1..8 stage, PAL0 slots 9..15
  HUD, PAL1/2 bodies, PAL3 effects. Do not load it until HUD/FX palette migration
  is complete and reviewed.
- Erratum: a previous residency report removed WINDOW rows 0..55 as if the whole
  region were opaque. `fight_hud.c` clears all 40x7 Window cells and writes only
  selected portrait/bar/text cells; color code zero is transparent. Counts 516
  (15-color) and 506 (eight-color) with that assumed clip are lower bounds for a
  hypothetical opaque overlay and cannot close production residency. See
  `rascunho/processado/stage_takeover/suzaku_visible_window_residency_20260926_v2/visible_window_report_erratum_20260926.json`.
- Pool repartition is only a measurement candidate: on SGDK 2.11 H40,
  `TILE_FONT_INDEX=1440`; `SPR_initEx(600)` begins at tile840, while
  `SPR_initEx(446)` would begin at994 and expand fixed-user space by154. That
  gives a theoretical 516 stage tiles when the 272-tile super BGFX area is
  borrowed. The unoccluded full-frame 15-color anchor is242 tiles above it;
  exact savings from source pixels fully hidden by HUD have not been measured.
  Existing
  sprite-pool telemetry (353 used, largest free block72) came from a no-stage,
  dummy-audio probe and does not justify reducing the production pool.
- Next: use the full top image region; optimize source-derived tile reuse by
  coherent semantic areas and camera windows; measure exact same-definition
  fighter-sheet sharing only where applicable; close palette owners and runtime
  residency before stage assets enter `res/`. Keep video/audio, DMA/VBlank,
  scanline, camera/parallax, BG5 and full-fight cadence as separate release gates.
