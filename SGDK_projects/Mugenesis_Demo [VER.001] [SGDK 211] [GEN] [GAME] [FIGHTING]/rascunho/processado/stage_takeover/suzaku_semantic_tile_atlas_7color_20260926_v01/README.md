# Suzaku semantic palette and tile-atlas study

Status: source-derived, static anchor-camera experiment. It changes no `res/`, runtime code, ROM, or canonical project document.

The input is the exact DEF/SFF-derived `far_bg0a_bg0b_anchor.png` and `near_bg1_bg4_anchor.png` pair bundled under `source/`, with its source-lineage record. The two plates are a camera-224 still; the original layer sprites and MUGEN source remain the visual authority. The raw MUGEN ZIP is not bundled; its SHA-256 is recorded in the lineage, and the builder verifies it when that archive is available locally.

The 7-color candidate uses the proposed role palette, with `#4488CC` removed. The 8-color control retains it. Both variants quantize the supplied approximate swatches through the project's canonical `vdp_word` / `vdp_rgb`, and map source colors only within declared semantic ramps: cool sky/architecture above y=176, wood deck below y=176, with deep shadow shared. Index 0 is reserved for transparency. No new stage pixels were drawn.

Measured atlas results with exact H/V tile reuse:

- 7 colors: 615 shared patterns, 19680 pattern bytes, 4,480 bytes for the two 40x28 maps, 24160 bytes total.
- 8-color control: 668 shared patterns, 21376 pattern bytes, 4,480 bytes for the two maps, 25856 bytes total.
- 7-color color-error control: MSE 1654.46; 8-color: MSE 1547.24. This metric is not an aesthetic approval.
- Removing the vivid-blue swatch changes 6454 of 71680 composed pixels versus the 8-color control; RGB MSE between candidates is 129.24.

The shared 4bpp planar tilebank and name tables were decoded back into both indexed planes and matched pixel-for-pixel. See `scene_tilemap_conversion_report.json`, `tilemap_flag_report.json`, and `per_tile_palette_conflict_report.json` under each variant.

Limit: this combines static source layers into BG_B/BG_A anchor plates at camera 224. Its 615 unique patterns remain 169 above the historical 446-tile stage allocation, which is conditional and not the physical VDP ceiling. It does not preserve independent parallax motion, the sky's autonomous velocity, BG4a's row-varying scale, BG5 animation, HUD/FX palette ownership, camera sweep, ROM residency, or DMA. It is not ready for `res/` or a game build.
