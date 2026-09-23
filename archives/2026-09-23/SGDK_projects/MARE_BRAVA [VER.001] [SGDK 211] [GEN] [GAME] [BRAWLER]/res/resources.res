// Branding intro assets built by tools/image-tools/build_branding_intro_assets.py.
// Every PNG is indexed, 8px aligned, and limited to a single 16-color palette.
IMAGE img_brand_fx_tiles "branding/brand_fx_tiles.png" BEST
IMAGE img_brand_engine_logo "branding/brand_engine_logo.png" BEST
IMAGE img_brand_author_logo "branding/brand_author_logo.png" BEST
IMAGE img_brand_project_logo "branding/brand_project_logo.png" BEST
IMAGE img_brand_presents_text "branding/brand_presents_text.png" BEST

// CAIS_01 art-alignment pass v04: source-locked composition with a clear hero silhouette.
// BG_B owns clouds/compact harbor/water (PAL0); BG_A owns authored pier props (PAL2).
IMAGE img_cais01_bg_b_mar_ceu "backgrounds/cais01/cais01_bg_b_harbor_sunset_512x224_v04.png" FAST
IMAGE img_cais01_bg_a_pier_modular "backgrounds/cais01/cais01_bg_a_industrial_pier_512x224_v04.png" FAST

// TAÍNA: one-action 6-frame idle strip. Width/height are in tiles: 6x8 = 48x64 px.
// Left-facing playback must use H-flip to preserve the authored asymmetric sash.
SPRITE spr_taina_idle_guard "sprites/characters/taina/taina_idle_guard_48x64_v02.png" 6 8 FAST 0

// CRIA: native 48x64 nervous lean idle. PAL3 enemy roster. No H-flip (cap visor).
SPRITE spr_cria_idle_lean "sprites/characters/cria/cria_idle_lean_48x64_v01.png" 6 8 FAST 0
SPRITE spr_cria_walk_lean "sprites/characters/cria/cria_walk_lean_48x64_v01.png" 6 8 FAST 0
SPRITE spr_cria_telegraph_lean "sprites/characters/cria/cria_telegraph_lean_48x64_v01.png" 6 8 FAST 0
SPRITE spr_cria_hit_lean "sprites/characters/cria/cria_hit_lean_48x64_v01.png" 6 8 FAST 0
SPRITE spr_cria_recover_lean "sprites/characters/cria/cria_recover_lean_48x64_v01.png" 6 8 FAST 0

// TAÍNA P0 locomotion candidates. Every strip contains one action and only
// unique physical drawings; timing remains manual to preserve the VBlank map.
SPRITE spr_taina_walk_combat_step "sprites/characters/taina/taina_walk_combat_step_48x64_v01.png" 6 8 FAST 0
SPRITE spr_taina_dash_or_step_in "sprites/characters/taina/taina_dash_or_step_in_64x64_v01.png" 8 8 FAST 0
SPRITE spr_taina_jump_rise_fall_landing "sprites/characters/taina/taina_jump_rise_fall_landing_48x64_v01.png" 6 8 FAST 0

// TAÍNA combo hit 1: only three unique attack drawings. 8x8 tiles = 64x64 px.
// Anticipation and recovery reuse idle frame 0; logical timing remains [3,2,2,3,4].
SPRITE spr_taina_combo_hit_1_jab "sprites/characters/taina/taina_combo_hit_1_jab_runtime_unique_64x64_v02.png" 8 8 FAST 0

// Three unique contact-shadow cells: grounded, low air and high air.
// The sheet reuses TAÍNA's dark PAL1 indices and therefore consumes no palette.
SPRITE spr_taina_ground_shadow "sprites/fx/taina_ground_shadow_48x16_3f_v03.png" 6 2 FAST 0

// Scene-local atmosphere. Smoke reuses PAL0; lamp dust reuses PAL2.
SPRITE spr_cais01_smoke "sprites/fx/cais01_smoke_32x32_4f_v01.png" 4 4 FAST 0
SPRITE spr_cais01_lamp_dust "sprites/fx/cais01_lamp_dust_16x16_4f_v01.png" 2 2 FAST 0

// Branding intro audio uses SGDK 2.11 WAV resources for the XGM2 PCM path.
WAV brand_bell_forge "audio/branding/bell_forge.wav" XGM2 13300
WAV brand_typewriter_click "audio/branding/typewriter_click.wav" XGM2 6650
WAV brand_bell_terminal "audio/branding/bell_terminal.wav" XGM2 13300
WAV brand_stamp_whoosh "audio/branding/stamp_whoosh.wav" XGM2 13300
WAV brand_reverb_tail "audio/branding/reverb_tail.wav" XGM2 13300
