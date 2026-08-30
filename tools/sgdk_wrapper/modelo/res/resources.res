// Branding intro assets built by tools/image-tools/build_branding_intro_assets.py.
// Every PNG is indexed, 8px aligned, and limited to a single 16-color palette.
IMAGE img_brand_fx_tiles "branding/brand_fx_tiles.png" BEST
IMAGE img_brand_engine_logo "branding/brand_engine_logo.png" BEST
IMAGE img_brand_author_logo "branding/brand_author_logo.png" BEST
IMAGE img_brand_project_logo "branding/brand_project_logo.png" BEST
IMAGE img_brand_presents_text "branding/brand_presents_text.png" BEST

// Branding intro audio uses SGDK 2.11 WAV resources for the XGM2 PCM path.
WAV brand_bell_forge "audio/branding/bell_forge.wav" XGM2 13300
WAV brand_typewriter_click "audio/branding/typewriter_click.wav" XGM2 6650
WAV brand_bell_terminal "audio/branding/bell_terminal.wav" XGM2 13300
WAV brand_stamp_whoosh "audio/branding/stamp_whoosh.wav" XGM2 13300
WAV brand_reverb_tail "audio/branding/reverb_tail.wav" XGM2 13300

// =====================================================================
// branding_sequence_v2 — DECLARACOES PENDENTES DE ARTE
// Autoridade: doc/branding_sequence_contract.json
//
// Os 5 IMAGE brand_* acima sao PLACEHOLDERS desenhados por primitiva em
// tools/image-tools/build_branding_intro_assets.py. Estao declarados como
// source_kind=procedural_primitive / acceptance_status=placeholder em
// doc/asset_provenance_manifest.json e NUNCA podem ser promovidos a final.
//
// O agente de arte que entregar os assets do v2 deve, para cada linha:
//   1. produzir o PNG indexado (index 0 transparente, 15 cores visiveis);
//   2. descomentar a linha correspondente;
//   3. adicionar a entrada em doc/asset_provenance_manifest.json;
//   4. rodar audit_procedural_asset_provenance.py e o build pelo wrapper.
//
// Larguras/alturas de SPRITE sao em TILES e valem POR QUADRO do strip.
//
// IMAGE   img_forge_bg_b        "branding/forge_bg_b_320x224.png"          BEST
// IMAGE   img_forge_bg_a_props  "branding/forge_bg_a_props_320x224.png"    BEST
// SPRITE  spr_forge_ember       "branding/spr_forge_ember_16x16_strip.png" 2 2 FAST 0
// SPRITE  spr_forge_shard       "branding/spr_forge_shard_16x16_strip.png" 2 2 FAST 0
// IMAGE   img_logo_engine_v2    "branding/logo_engine_224x64.png"          BEST
// IMAGE   img_logo_author_v2    "branding/logo_author_192x32.png"          BEST
// IMAGE   img_logo_project_v2   "branding/logo_project_224x48.png"         BEST
// IMAGE   img_presents_text_v2  "branding/presents_text_96x16.png"         BEST
// =====================================================================
