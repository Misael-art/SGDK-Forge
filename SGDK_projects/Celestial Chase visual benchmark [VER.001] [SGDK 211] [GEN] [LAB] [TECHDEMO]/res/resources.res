// Branding intro assets built by tools/image-tools/build_branding_intro_assets.py.
// Every PNG is indexed, 8px aligned, and limited to a single 16-color palette.
IMAGE img_brand_fx_tiles "branding/brand_fx_tiles.png" BEST
IMAGE img_brand_engine_logo "branding/brand_engine_logo.png" BEST
IMAGE img_brand_author_logo "branding/brand_author_logo.png" BEST
IMAGE img_brand_project_logo "branding/brand_project_logo.png" BEST
IMAGE img_brand_presents_text "branding/brand_presents_text.png" BEST

// Celestial Chase v009 cinematic runtime.
IMAGE img_chase_bg_b_v011 "gfx/chase/chase_bg_b_v011.png" BEST
IMAGE img_chase_bg_a_v011 "gfx/chase/chase_bg_a_v011.png" BEST
TILESET ts_chase_letterbox_v009 "gfx/chase/chase_letterbox_tile_v009.png" NONE NONE
TILESET ts_chase_hud_font_v011 "gfx/chase/chase_hud_font_v011.png" BEST NONE
SPRITE spr_chase_cloud_v009 "sprites/chase/chase_cloud_64x32_strip_v009.png" 8 4 FAST 2
SPRITE spr_chase_hero_run_v009 "sprites/chase/hero_run_toward_64x80_strip_v009.png" 8 10 FAST 4
SPRITE spr_chase_hero_ghost_v009 "sprites/chase/hero_ghost_64x80_strip_v009.png" 8 10 FAST 4
SPRITE spr_chase_pursuer_torso_v011 "sprites/chase/pursuer_torso_96x80_strip_v011.png" 12 10 FAST 6
SPRITE spr_chase_pursuer_head_v009 "sprites/chase/pursuer_head_80x64_strip_v009.png" 10 8 FAST 6
SPRITE spr_chase_pursuer_claw_v009 "sprites/chase/pursuer_claw_64x64_strip_v009.png" 8 8 FAST 6
SPRITE spr_chase_pursuer_dust_impact "sprites/chase/pursuer_impact_dust_fx_64x32_strip_v005.png" 8 4 FAST 6

// First playable obstacles and animated feedback.
SPRITE spr_chase_obstacle_boulder_v011 "sprites/chase/chase_obstacle_boulder_64x48_strip_v011.png" 8 6 FAST 4
SPRITE spr_chase_obstacle_brand_v011 "sprites/chase/chase_obstacle_brand_64x48_strip_v011.png" 8 6 FAST 4
SPRITE spr_chase_contact_shadow_v011 "sprites/chase/chase_contact_shadow_16x8_strip_v011.png" 2 1 FAST 3
SPRITE spr_chase_energy_star_v009 "sprites/chase/chase_energy_star_32x32_strip_v009.png" 4 4 FAST 4
SPRITE spr_chase_pulse_impact_v009 "sprites/chase/chase_pulse_impact_64x48_strip_v009.png" 8 6 FAST 6

// Original project-local PCM score and feedback cues through the XGM2 driver.
WAV snd_chase_score_loop "audio/chase/chase_score_loop.wav" XGM2 13300
WAV snd_chase_menu "audio/chase/chase_menu.wav" XGM2 13300
WAV snd_chase_jump "audio/chase/chase_jump.wav" XGM2 13300
WAV snd_chase_land "audio/chase/chase_land.wav" XGM2 13300
WAV snd_chase_hit "audio/chase/chase_hit.wav" XGM2 13300
WAV snd_chase_pulse "audio/chase/chase_pulse.wav" XGM2 13300
WAV snd_chase_pickup "audio/chase/chase_pickup.wav" XGM2 13300
WAV snd_chase_victory "audio/chase/chase_victory.wav" XGM2 13300
WAV snd_chase_failure "audio/chase/chase_failure.wav" XGM2 13300
WAV snd_chase_pressure "audio/chase/chase_pressure.wav" XGM2 13300
