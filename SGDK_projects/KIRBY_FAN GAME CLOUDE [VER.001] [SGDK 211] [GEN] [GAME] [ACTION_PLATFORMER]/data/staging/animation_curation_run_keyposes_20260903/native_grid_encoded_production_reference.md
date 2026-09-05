# Native-grid encoded production reference

## Causal route

- blocker before: native_pixel_authorship_producer_unavailable
- hypothesis: image producer may emit a logical 32x32 pixel grid encoded as uniform integer blocks
- route: native_grid_encoded
- attempt budget: two materially distinct attempts maximum
- output classification if it passes: ai_generated_native_grid_candidate
- forbidden claims: hand_authored_pixel, native_reauthored, ready_for_res

## Authority and guide

- identity authority: data/source_art/r1/r1-01/concept.png
- authority SHA-256: 591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd
- directional guide: data/staging/animation_curation_run_keyposes_20260903/run_contact_visual_producer_output.png
- guide SHA-256: a09d47517e577d90dbcd6c4e7fb04b5b9fee12d20c2df34dc6045a7dd22bf519
- guide role: reference only, never pixel source or final asset

## Logical target

- canvas: 32x32 logical pixels
- encoded output: both dimensions divisible by 32
- scale: one identical positive integer factor on X and Y
- alpha: binary only
- palette: no more than 15 visible colors plus transparent background
- pivot: bottom-center
- ground line: common baseline through the lower feet
- grid: reference-only; must not appear in the generated art

## Must preserve

- round body and R1 proportions
- eyes, gaze direction, cheeks and mouth
- two short arms
- two dark red feet with coherent volume and direction
- strict right-facing lateral contact pose
- readable compressed body and planted front foot
- no hair, crest, glow, dust, ground shadow, text or speed lines

## Objective measurement

Recover the logical image by taking one representative pixel from each factor-by-factor block. Reject if any block is non-uniform, if scale differs between axes, if an intermediate edge or antialiasing appears, if a grid is baked in, or if the recovered 32x32 image is not legible at 1x.
