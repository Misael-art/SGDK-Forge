// Branding intro assets built by tools/image-tools/build_branding_v3_assets.py.
// Every PNG is indexed, 8px aligned, and limited to a single 16-color palette.

// --- v3 scene-local backgrounds and display marks ---
IMAGE img_brand_engine_bg_v3 "branding/brand_engine_bg_v3.png" BEST
IMAGE img_brand_author_bg_v3 "branding/brand_author_bg_v3.png" BEST
IMAGE img_brand_project_bg_v3 "branding/brand_project_bg_v3.png" BEST
IMAGE img_brand_engine_logo_v4 "branding/brand_engine_logo_v4.png" BEST
IMAGE img_brand_author_signature_v4 "branding/brand_author_signature_v4.png" BEST
IMAGE img_brand_project_logo_v4 "branding/brand_project_logo_v4.png" BEST
IMAGE img_brand_presents_v4 "branding/brand_presents_v4.png" BEST

// --- v4 identity bitmap fonts (37 glyphs each, 8x16, multi-layer shading) ---
// NONE keeps each tilemap addressable by the runtime glyph renderer.
IMAGE img_font_forge_v4 "branding/font_forge_v4.png" NONE
IMAGE img_font_terminal_v4 "branding/font_terminal_v4.png" NONE
IMAGE img_font_crest_v4 "branding/font_crest_v4.png" NONE

// --- v3 FX sprite sheets (procedural, identity-driven) ---
// SPRITE width/height are in 8x8 tiles, not pixels.
SPRITE spr_brand_spark_v3 "branding/fx_spark_v3.png" 1 1 BEST
SPRITE spr_brand_monogram_v3 "branding/fx_monogram_mo_v3.png" 4 4 BEST
SPRITE spr_brand_cursor_v3 "branding/fx_cursor_v3.png" 1 2 BEST
SPRITE spr_brand_shield_v3 "branding/fx_shield_v3.png" 8 4 BEST
SPRITE spr_brand_glow_v3 "branding/fx_glow_v3.png" 4 4 BEST
SPRITE spr_brand_debris_v3 "branding/fx_debris_v3.png" 1 1 BEST

// --- Branding intro audio: WAV resources for the XGM2 PCM path ---
WAV brand_bell_forge "audio/branding/bell_forge.wav" XGM2 13300
WAV brand_typewriter_click "audio/branding/typewriter_click.wav" XGM2 6650
WAV brand_bell_terminal "audio/branding/bell_terminal.wav" XGM2 13300
WAV brand_stamp_whoosh "audio/branding/stamp_whoosh.wav" XGM2 13300
WAV brand_reverb_tail "audio/branding/reverb_tail.wav" XGM2 13300
