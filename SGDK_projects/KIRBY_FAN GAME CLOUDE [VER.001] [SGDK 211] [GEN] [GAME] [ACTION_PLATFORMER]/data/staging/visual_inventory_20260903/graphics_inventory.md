# Kirby graphics inventory - 2026-09-03

Scope: every raster animation, character, scene, branding, FX, source, staged
probe, and runtime resource found in this project. This is an inventory and
lineage record; it does not promote any asset.

## Authority and source material

| Area | Count | Role | State |
|---|---:|---|---|
| `data/source_art/r1/` | 20 PNG | R1 concepts, retained generated provenance, layer/palette studies | source-only; `r1-01/concept.png` is the identity authority |
| `data/source_art/r2/` | 7 PNG | surgical concept corrections and retained crops | source-only; no direct resource use |
| `data/source_art/r3/` | 1 PNG | layer/palette correction | source-only; no direct resource use |
| `data/source_art/branding_intro/production/` | 3 PNG | branding source panels | source for existing indexed branding resources |
| `data/source_art/model_sheet_v01/` | 1 PNG | legacy 160x32 model-sheet reference | reference-only; not a final animation source |
| `data/source_art/archive/` | 29 PNG | rejected P1 and obsolete technical evidence | negative evidence; never reuse |
| `rascunho/` | 144 PNG/GIF | prior visual studies, native idle proof, mechanical probes, rejected P2 material | staging/reference-only; not a direct final-art authority |

R1 identity authority:
`data/source_art/r1/r1-01/concept.png`

R1 SHA-256:
`591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`

The complete R1/R2 source SHA inventory remains in
`data/source_art/premium_source_manifest.json`,
`data/source_art/r1/r1_delivery_manifest.json`, and
`data/source_art/r2/r2_delivery_manifest.json`. Their policy is
`source_candidate_pending_human_judgment`; none authorizes direct `res/`
promotion.

## Existing runtime resources

`res/` contains 23 PNGs and is unchanged. The resource declaration is
`res/resources.res`.

| Group | Files | Runtime role | Honest state |
|---|---|---|---|
| Branding | `res/branding/brand_fx_tiles.png`, `brand_engine_logo.png`, `brand_author_logo.png`, `brand_project_logo.png`, `brand_presents_text.png` | `scene_branding.c` | indexed resource; existing branding path |
| Stage background | `res/gfx/ph_sky.png`, `ph_mount.png`, `ph_hills.png`, `ph_terrain.png` | `scene_stage.c`, `scene_boss.c`, `scene_gameover.c`, `scene_native_art_review.c` | placeholder |
| Title/background | `res/bgs/ph_title_hill.png`, `ph_title_stars.png`, `ph_trunk.png`, `res/gfx/ph_title_logo.png` | title, boss, gameover | placeholder |
| Hero and scene sprites | `res/sprites/ph_kirby.png`, `ph_fg.png`, `ph_enemy.png`, `ph_particle.png`, `ph_branch.png`, `ph_boss_face.png`, `ph_apple.png`, `ph_light.png` | stage, boss, gameover | placeholder |
| Ability FX | `res/sprites/ph_ability_fx.png` | stage ability shots | placeholder |
| Limited native idle | `res/sprites/native_idle_key_pose_elite_v01.png` | only `scene_native_art_review.c` | approved isolated review scope only; not animation approval |

Representative resource hashes:

- `res/sprites/ph_kirby.png`: `96784834be73d32956c2a6233de5a952b446bbe4c8cf72ffdc88c902995c3e88`
- `res/sprites/native_idle_key_pose_elite_v01.png`: `58004465b39c826ce970c5c8018cb202f2befbf45b8ce8c2fa355804daa9fb29`
- `res/gfx/ph_sky.png`: `97f9733c0f22f691b6edbfbf03bb82b99ab37afabfa5ea98edb4e50cb8d061e6`

The full 23-file dimensions/mode/SHA listing was measured directly from the
files and is preserved by the existing resource/provenance records; no file in
this inventory was edited.

## Current staging and visual-producer outputs

`data/staging/` contains 11 raster outputs relevant to this continuation:

- run key-pose guides: `run_contact_visual_producer_output.png`,
  `run_passing_visual_producer_output.png`,
  `run_flight_push_hypothesis2_visual_producer_output.png`;
- rejected run guide: `run_flight_push_visual_producer_output.png`;
- prior run guide boards: `animation_curation_run_contact_20260903/visual_producer_output.png`,
  `animation_curation_run_passing_20260903/visual_producer_output.png`;
- inhale/jump guides: `inhale_visual_pose_guide.png`,
  `jump_launch_visual_pose_guide.png`;
- ability FX guides: `fire_ability_fx_visual_source.png`,
  `beam_ability_fx_visual_source.png`;
- native-grid capability test: `native_grid_encoded_attempt_01.png`.

All are `visual_source`, diagnostic, or rejected probe outputs. None is a
native 32x32 authored frame, strip, lineart source, runtime resource, or ROM
input. The second native-grid attempt returned no file because the external
producer rejected output moderation.

Key staged hashes:

- run contact: `a09d47517e577d90dbcd6c4e7fb04b5b9fee12d20c2df34dc6045a7dd22bf519`
- run passing: `717dca21979690292d7278d9bab2f22334a1ac766d4cf240b67a89f0be56d66e`
- run flight hypothesis 2: `13cc7ff2bdbd0c474f3a96306e26b88d5ce19e15b5e02773ddefca57b338a67b`
- inhale guide: `e8326e0307aecbc0e02f4726b3c47dd843f5cb2335a0cb6ef44cb2fcc107240e`
- jump launch guide: `46fda9175fcd943eb9e6133f899584da2a3099634e7b5a69c1cb20676d97a81b`
- native-grid attempt 01: `787e6232bd2012fae3ab409b55bbc4a0b727ba0b4795c014cc11cd4dc95875ca`

## Runtime consumers and independent branches

The actual runtime roster includes `KIRBY_IDLE`, `KIRBY_RUN`, `KIRBY_JUMP`,
`KIRBY_FLOAT`, `KIRBY_INHALE`, `KIRBY_SWALLOW`, `KIRBY_HURT`, defeat, and the
Fire/Beam/Cutter/Stone/Sword ability states. The gameplay scenes still consume
`spr_ph_kirby`; only the isolated native-art review consumes
`spr_native_idle_elite`.

Independent material that can continue without Kirby native-pixel authorship:

- branding resources and their existing audio path;
- stage/title/background placeholder wiring and scene composition review;
- palette, tile, parallax, boss modularity, HUD/UI, and FX contracts as
  documentation/measurement work;
- runtime and VDP budget audits against existing placeholders.

These branches must remain claims below final visual delivery until their own
source, native asset, resource, budget, and emulator gates close. No independent
branch was silently promoted in this continuation.

## Inventory conclusion

`native_grid_encoded` is closed after two allowed attempts. The only current
Kirby character asset with a bounded native claim is the previously approved
isolated idle key pose. No valid native run, inhale, jump/float animation or
full visual package exists. No `res/`, runtime, ROM, v04, v05, v06, v07, v08,
or v09 content was changed.

## Per-file active hash ledger

The following active files were hashed directly during this inventory. `P`
means indexed PNG; `RGB` and `RGBA` are producer-source modes.

| File | Format | SHA-256 | Classification |
|---|---|---|---|
| `res/branding/brand_author_logo.png` | P | `b3831cb5ee92541baaf77610681cb8a63d8c2890229a2d23141821e754397443` | existing branding resource |
| `res/branding/brand_engine_logo.png` | P | `958782dcfdf2cd892102b2436aabe5b5886b2cf75ef152ecfe424d11737d279f` | existing branding resource |
| `res/branding/brand_fx_tiles.png` | P | `60a67c72e517275f7aab298976944d3539e20d955d2821bcdd30710a71f8c9a9` | existing branding resource |
| `res/branding/brand_presents_text.png` | P | `bce36b6c56e8ef89993b7936d352b4829c3b433ecdc5a9dc2bff02633af907b5` | existing branding resource |
| `res/branding/brand_project_logo.png` | P | `2bf6726bc8f0bb649a3c505a6f26eba9af15cd36bbfc52c6ecc0f67193328955` | existing branding resource |
| `res/bgs/ph_title_hill.png` | P | `645d1e943c437f43b7b3d7db861345cb073f6dd7733c6c8906d4123f06d708e1` | placeholder_in_res |
| `res/bgs/ph_title_stars.png` | P | `9e67d97f7f62a18ef5433ef6637b4fa8863e355e96a832ba109d660495ac3758` | placeholder_in_res |
| `res/bgs/ph_trunk.png` | P | `ef948374a9f64673e9955ac7c0c42a2e67453790ada4d9e1cd153995efecef03` | placeholder_in_res |
| `res/gfx/ph_hills.png` | P | `763b336cc7349716daed67ad83db7a58046ec1049407fd90b672ba45874a9e04` | placeholder_in_res |
| `res/gfx/ph_mount.png` | P | `310c65b4399e384a1f5eb2b9f9b912e4760ab0761ed54d91e8f931b1283d7a6a` | placeholder_in_res |
| `res/gfx/ph_sky.png` | P | `97f9733c0f22f691b6edbfbf03bb82b99ab37afabfa5ea98edb4e50cb8d061e6` | placeholder_in_res |
| `res/gfx/ph_terrain.png` | P | `1a1d00c406e58802ae969c9f9d7ff51cee8c20cc7c807a67e6dc0ef9f71738e7` | placeholder_in_res |
| `res/gfx/ph_title_logo.png` | P | `b0a2a874bb0754f3155663259688f4f24d3816d97f98721f8aceafba912fcc93` | placeholder_in_res |
| `res/sprites/native_idle_key_pose_elite_v01.png` | P | `58004465b39c826ce970c5c8018cb202f2befbf45b8ce8c2fa355804daa9fb29` | native_ready_for_validation, isolated scope |
| `res/sprites/ph_ability_fx.png` | P | `3fbf25f050ced8b2bca78112d43e25dae0bb9751f5f857357e70660eaaa1955f` | placeholder_in_res |
| `res/sprites/ph_apple.png` | P | `c0dec8c61ab1e5ff2909e4a0ad3a8e1a6981e5a1be4e17662542cabbf2a650f3` | placeholder_in_res |
| `res/sprites/ph_boss_face.png` | P | `c195b2371217014a609b4ed524a526b02c7c0868985834a9976087c9fbc9e1c6` | placeholder_in_res |
| `res/sprites/ph_branch.png` | P | `ed0c8629a9411c1a25676b177cfd0fcc1a83596e5a4b4412d24edf742d69cf00` | placeholder_in_res |
| `res/sprites/ph_enemy.png` | P | `644f999bdbf45523ed107fc7d18e864df3f0b9eccaeac1cdf65a6664348a8990` | placeholder_in_res |
| `res/sprites/ph_fg.png` | P | `417e816c90a54b1562919847e5a243761ca56ed8dfc2823418885fa043a58258` | placeholder_in_res |
| `res/sprites/ph_kirby.png` | P | `96784834be73d32956c2a6233de5a952b446bbe4c8cf72ffdc88c902995c3e88` | placeholder_in_res |
| `res/sprites/ph_light.png` | P | `f687aaf673395baf8346ac9e09526d44ab7626bf46dbc5bae1435a16d3f78a81` | placeholder_in_res |
| `res/sprites/ph_particle.png` | P | `5f8e5ff3d0c4b52ebfed90e32df0a6c9cc50ec0db2a48f33591dc3d4c957998c` | placeholder_in_res |
| `data/staging/animation_curation_run_keyposes_20260903/native_grid_encoded_attempt_01.png` | RGB | `787e6232bd2012fae3ab409b55bbc4a0b727ba0b4795c014cc11cd4dc95875ca` | rejected native-grid probe |
| `data/staging/animation_curation_run_keyposes_20260903/run_contact_visual_producer_output.png` | RGB | `a09d47517e577d90dbcd6c4e7fb04b5b9fee12d20c2df34dc6045a7dd22bf519` | visual_source |
| `data/staging/animation_curation_run_keyposes_20260903/run_passing_visual_producer_output.png` | RGB | `717dca21979690292d7278d9bab2f22334a1ac766d4cf240b67a89f0be56d66e` | visual_source |
| `data/staging/animation_curation_run_keyposes_20260903/run_flight_push_hypothesis2_visual_producer_output.png` | RGB | `13cc7ff2bdbd0c474f3a96306e26b88d5ce19e15b5e02773ddefca57b338a67b` | visual_source |
| `data/staging/animation_curation_run_keyposes_20260903/run_flight_push_visual_producer_output.png` | RGB | `44a2e32271af197e092d7054d8cef1f19e7306bf780ed731b505fd8ea2d229e8` | rejected visual_source |
| `data/staging/visual_production_inhale_jump_20260903/inhale_visual_pose_guide.png` | RGB | `e8326e0307aecbc0e02f4726b3c47dd843f5cb2335a0cb6ef44cb2fcc107240e` | visual_source |
| `data/staging/visual_production_inhale_jump_20260903/jump_launch_visual_pose_guide.png` | RGB | `46fda9175fcd943eb9e6133f899584da2a3099634e7b5a69c1cb20676d97a81b` | visual_source |
| `data/staging/visual_production_ability_fx_20260903/fire_ability_fx_visual_source.png` | RGB | `bb074ae95676fb8a2108d363c03466740539e66a3336dae1b2881a5ff86470ef` | visual_source |
| `data/staging/visual_production_ability_fx_20260903/beam_ability_fx_visual_source.png` | RGBA | `35ffd38289563a53ecfcae5b318c5e806e6c813e95a943431680ecb09199ee64` | visual_source |

The remaining staged run contact/passing boards are evidence composites, not
independent sprite assets. Their lineage and hashes are in the corresponding
producer records and route reports.
