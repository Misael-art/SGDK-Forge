# Case: Scene Route Variants for `METAL_SLUG_URBAN_SUNSET`

## Purpose

This case teaches that a hero scene can admit more than one strong artistic route without breaking the Mega Drive contract, as long as the scene stays spatially frozen and the user explicitly chooses the route to keep.

## Locked Inputs

- original board: `source_original.png`
- study crop: `study_crop_448x224.png`
- base scene fantasy: urban street at sunset / early evening
- fixed framing: same building masses, same bridge, same road curvature, same focal corner
- fixed target mindset: Mega Drive scene slice with 15 visible colors plus transparency where needed

## Route Register

### Route A: `high_key_haze`

- file: `route_a_high_key_haze.png`
- visual story: pale high-key sky, bright ambient haze, warm windows, cleaner illustration-like read
- why it is interesting:
  - increases perceived modern polish
  - makes windows and storefront lights read quickly
  - reduces visual heaviness in the upper half
- risks:
  - weakens the dramatic sunset identity from the original board
  - can flatten `BG_B` atmosphere if the final scene still wants a strong warm sky layer
  - may make the stage feel more "clean concept render" than "war-torn urban sunset"

### Route B: `high_key_haze_duplicate`

- file: `route_b_high_key_duplicate.png`
- note: same SHA-256 as Route A
- function in the case:
  - proves that route studies may arrive duplicated under different labels
  - teaches the skill to collapse duplicates instead of pretending there are more options than actually exist

### Route C: `grid_alignment`

- file: `route_c_grid_alignment.png`
- visual story: diagnostic board, not a final route
- why it is useful:
  - helps verify alignment, pixel rhythm and shared-canvas discipline
  - clarifies that a route board may include one diagnostic overlay alongside production routes
- rule:
  - do not promote this board as final art

### Route D: `cool_evening`

- file: `route_d_cool_evening.png`
- visual story: cooler blue sky, stronger warm-vs-cool separation, more classic evening readability
- why it is interesting:
  - improves thermal separation between warm windows and cool air
  - likely gives `BG_B` a clearer atmospheric role
  - can produce stronger gameplay read if the player and foreground stay warm or neutral
- risks:
  - drifts away from the red-orange sunset expectation of the original source board
  - if pushed too far, the scene stops belonging to the "urban sunset" fantasy and becomes generic dusk

### Route E: `anime_style`

- file: `route_e_anime_style.png`
- visual story: anime-background philosophy with clean sky bands, cel-shaded masses and simplified material ramps
- why it is interesting:
  - proves that a flatter, more directed color script can become more Mega Drive-friendly without looking cheap
  - can win on silhouette, palette efficiency and tile reuse instead of trying to preserve every source gradient
  - opens a route where the scene feels intentional, stylized and ROM-honest at the same time
- risks:
  - if over-flattened, the scene may lose too much of the gritty material density expected from the original fantasy
  - because it changes the painting philosophy, it requires explicit human freeze before replacing an incumbent route

## Canonical Lessons

1. A route board is valid only when all candidates share the same scene contract.
2. The route board may vary mood, palette temperature, contrast, dithering character and plane emphasis.
3. The route board may not vary perspective, focal geometry or scene identity without reopening composition.
4. Duplicate studies must be collapsed honestly.
5. A flat `anime_style` route is allowed when it wins by hardware honesty, not only by illustration novelty.
6. The user may choose between surviving routes, but once chosen the route becomes `locked_visual_direction`.

## Recommended Comparison Matrix

Evaluate each surviving route on:

- adherence to original scene fantasy
- readability at native scale
- `BG_A` / `BG_B` separation potential
- likely palette pressure
- likely tile uniqueness pressure
- whether a flatter anime-style route is improving structure or just erasing material richness
- fit with the rest of the project's visual language

## Recommended Freeze Rule

- if two routes are both strong, keep at most two survivors for user choice
- if a new route changes the painting philosophy, keep the incumbent locked until the user explicitly approves the swap
- record the preferred route from the aesthetic judge
- record the chosen route from the user
- treat the chosen route as binding for future scene iterations
