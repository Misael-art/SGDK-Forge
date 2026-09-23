# Celestial Chase First Playable - Technical Design

## Runtime Shape

The slice uses SGDK 2.11 and C with a deterministic scene FSM and static subsystem pools. `APP_SCENE_CHASE` remains the playable scene; `scene_chase.c` only orchestrates composition and delegates gameplay to `chase_player`, `chase_obstacles`, `chase_pursuer`, `chase_hud` and `chase_rules`.

No gameplay system may use `malloc`, `free`, `float` or `double`.

## Scene and State Flow

The global flow is linear: branding, title, menu, chase and integrated result. The chase FSM owns `enter`, three gameplay phases, `paused`, victory/failure result and `exit`. Every result state has restart and menu transitions.

## Input

`src/system/input.c` is the only joypad abstraction. Left/right request a discrete lane change, A jumps, B activates a charged Pulse, START pauses/resumes and MODE is limited to non-active flow.

## Memory

Gameplay uses fixed pools: six obstacle slots, three telegraphs, four FX slots, fixed HUD fields and four string buffers. Sprite creation happens on scene enter; inactive objects remain hidden rather than allocated during play.

## VDP Ownership

`src/main.c` calls the SGDK VBlank process once per frame. Large resources load only during scene entry. Runtime sprite updates use the SGDK sprite engine; road scroll and phase palette changes are small fixed updates. H-Int is disabled in this version.

Palette ownership:

- PAL0: environment;
- PAL1: hero;
- PAL2: pursuer, obstacles and gameplay FX;
- PAL3: HUD and result text.

## Audio Ownership

`src/system/audio.c` is the single audio owner. The intended final driver is XGM2 with PSG/PCM feedback arbitration. Until a validated XGM2 song asset exists, PSG supplies a functional adaptive score and SFX without changing the ownership contract.

## Region and Mastering

NTSC at 60 FPS is the delivery performance gate. PAL remains functionally supported through `gApp.targetFps`. The slice has no persistent player save; SRAM is used only by the canonical runtime evidence probe.

## Scene Architecture Triage

- `scene_profile`: `aaa_layered`
- `baseline_technique`: tilemap streaming guided by camera
- `baseline_technique_applicability`: partial
- `baseline_decision`: adapt
- `plane_roles`: BG_B atmosphere, BG_A road/HUD fallback, sprites for actors/obstacles/FX, WINDOW reserved for a later measured HUD promotion
- `tilemap_strategy`: scene-local preload because the visible chase window is fixed and the approved v007 split already has a bounded resident set
- `occlusion_model`: road overlay and sprite priority only; WINDOW is not scenery
- `primary_risk_if_skipped`: hiding a VRAM residency problem behind a single flattened fallback image

## API Reality Check

The design uses SGDK 2.11 declarations verified in `sdk/sgdk-2.11/inc/`: `SPR_addSprite`, `SPR_setPosition`, `SPR_setVisibility`, `SPR_update`, `VDP_setScrollingMode`, `VDP_setHorizontalScrollLine`, `PAL_setPalette`, `XGM2_play`, `XGM2_pause` and `XGM2_resume`. XGM2 lives in `inc/snd/xgm2.h`.

## Fallback Order

1. reduce line scroll to plane scroll;
2. keep HUD on a fixed BG_A safe area;
3. reduce active obstacle/FX slots;
4. reduce road overlay height;
5. preserve approved hero and pursuer art;
6. retain `LAB/TECHDEMO` classification when creative or human gates remain blocked.
