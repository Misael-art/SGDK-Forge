# Celestial Chase v011 Pixel-Exact Assessment

## Status

- state: `documentado`
- implementation: `nao_iniciada`
- build/emulator evidence: `nao_aplicavel_a_este_documento`
- budget verdict: `cabe_com_recuo`
- delivery ceiling remains `lab_not_delivery`

This assessment evaluates the proposed v011 corrections against the current
v010 ROM, SGDK 2.11 APIs, source-baked assets, runtime ownership and measured
budgets. It does not promote any v011 item to `implementado`, `buildado` or
`testado_em_emulador`.

## Evidence Read

- current ROM: `out/rom.bin`, SHA256
  `a685b460d5397f0c4fe809350a9da653f6e322531bd0b7e027922b32bbbe1176`
- active gameplay evidence:
  `out/evidence/blastem_gameplay_v009/screenshot.png`
- road owner: `src/gameplay/chase_road.c`
- obstacle/collision owner: `src/gameplay/chase_obstacles.c`
- modular boss owner: `src/gameplay/chase_pursuer.c`
- HUD owner: `src/gameplay/chase_hud.c`
- scene orchestration: `src/scenes/scene_chase.c`
- current budget: `doc/07-budget-vram-dma.md`
- current regression: `out/logs/scene_regression_report.json`
- current closeout: `out/logs/scene_closeout_gate_report.json`

## Executive Verdict

The visual observations are materially correct. The scene still has visible
grounding, continuity, articulation, UI and test-system gaps that prevent a
commercial-quality claim.

Three proposed mechanisms need correction before implementation:

1. The hardware plane is already `64x32` tiles (`512x256`). The road seam is
   caused by a `320x224` BG_A overlay populating only part of that plane while
   line scroll reaches `-64px..+17px`, plus camera shake. Empty columns and the
   incompatible BG_B road below become visible. This is not yet proven as VDP
   corruption or a physical 320px plane wrap.
2. Three horizontal BG_B speed bands must be authored through the existing
   `HSCROLL_LINE` table. `VSCROLL_COLUMN` changes vertical offset by 16px
   columns and cannot express horizontal parallax bands.
3. HBlank SAT multiplexing for stars and a sprite-based Moon are rejected for
   v011. The sprite reserve is `648/680` tiles and mid-frame SAT reuse remains
   a laboratory-only technique. The runtime field named
   `max_scanline_sprites=20` is also not valid scanline proof: the probe fills
   it from `SPR_getUsedVDPSprite()` and clamps it to 20.

## Finding Matrix

| Observation / proposal | Assessment | Correct v011 route |
|---|---|---|
| Road side seams | Confirmed and P0 | Populate safe gutters inside the existing 512px plane; measure tile cost before promotion |
| Full 512x224 BG_A bitmap | Conditional | Use a sparse/deduplicated 512px tilemap candidate, not an unconstrained unique bitmap |
| Contact shadows | Confirmed and high impact | Shared dithered shadow/rune sprites, budgeted and pruned; no alpha |
| Generic HUD typography | Confirmed | Fixed custom HUD font plus glyph manifest and small icon/frame set |
| Obstacle scale/hitbox mismatch | Confirmed and gameplay-critical | One shared Z state must drive position, lane spread, frame, hitbox, shadow and collision window |
| Random bounce/ricochet | Valid only with constraints | Deterministic motion profiles and telegraphs; no unbounded random behavior |
| Boss neck/back gap | Confirmed | Re-author overlap collar/socket and clamp FK amplitude to a proven minimum overlap |
| Static rear legs | Confirmed | Re-author the existing six torso frames with a counter-phased rear-leg gait |
| Independent claw scale stages | Partially already present | Retune the six existing frames and select them from attack/Z state; preserve the shared VRAM slot |
| Three BG_B horizontal bands | Valid with axis correction | Compute zones in the existing BG_B line-scroll table; keep one owner |
| Washed palette | Valid perceptual concern | Semantic CRAM remaster, contrast audit and restrained cycling |
| Moon as sprite | Rejected for v011 | Keep Moon baked into BG_B behind cloud sprites |
| More than 40 multiplexed star sprites | Rejected for v011 | Keep stars baked; twinkle through a few palette-cycle slots |
| Hero 8 run + 4 jump frames | Valid major art track | New source-baked animation contract, pixel lock, motion GIF and human approval |
| Broken baseline/input loop | Confirmed | Separate structural, visual and full-flow regression contracts |

## P0 - Structural Corrections

### 1. Formalize v011 Before Runtime

Create and approve these artifacts before changing production runtime:

- `advanced_tilemap_design_card` for road gutters and seam policy
- `parallax_layer_contract` for BG_B zones and cloud grafts
- `boss_setpiece_card` for torso/head/claw ownership and overlap limits
- `feedback_fx_decision_card` for contact shadows and impact feedback
- `ui_decision_card` plus `glyph_manifest` for the HUD
- scene-local `vram_residency_report`
- `sprite_scanline_pressure_report`
- updated DMA queue contract
- corrected runtime probe metric or an explicit replacement for the mislabeled
  `max_scanline_sprites` field

### 2. Repair BG_A Continuity Without Spending the Whole Budget

Current facts:

- physical plane: `512x256`
- populated BG_A source: `320x224`
- current road line-scroll range before shake: `-64px..+17px`
- current background headroom: `70` tiles

Preferred implementation experiment:

- generate a `512x224` sparse road-overlay candidate centered around the
  visible 320px window;
- provide at least 96px of authored safe gutter on each side;
- make outer dunes, wall edges and road shoulders reuse repeatable metatiles;
- preserve transparent index 0 outside the overlay;
- add a base scroll origin and clamp the dynamic curve inside the safe gutter;
- verify maximum line scroll and maximum column scroll together.

Budget acceptance:

- target additional unique BG_A tiles: `<=48`
- hard acceptance maximum additional unique BG_A tiles: `<=56`, unless a new
  scene-local residency report proves a safe repartition
- current absolute background headroom is `70`; do not consume all of it by
  default
- if the candidate exceeds the target, keep the 320px road core and fill only
  side-gutter tilemap bands with reused tiles
- fallback: reduce maximum bend amplitude before accepting visible seams

### 3. Make Obstacle Rendering and Collision Share One Z Contract

The current obstacle runtime uses fixed lane X positions, linear Y movement,
one static hazard frame and a broad collision window at `y=148..178`. This
proves the reported visual/hitbox mismatch.

Replace the independent values with one deterministic Z state. A LUT derived
from that state must provide:

- screen Y
- lane convergence/spread from the vanishing point
- pre-rendered scale frame
- visual foot/contact point
- hitbox dimensions and collision-active interval
- contact-shadow scale
- bounce/roll offset
- telegraph phase

Motion profiles:

- boulder: roll with deterministic frame cadence and small grounded hop
- brand: bounce or ricochet only after a readable telegraph
- energy: float and pulse, never use the hazard collision profile

No visual variation may change the collision contract without using the same
Z state. Animated obstacle uploads must be scheduled away from the existing
`6404/7168` near-budget VBlank.

### 4. Close the Pursuer Rig

The gap is a real source-art and transform-boundary problem.

- extend the torso into a dark armor collar/socket
- require at least `6px` visible overlap at every head-bob and head-swing
  extreme
- clamp FK amplitudes when the overlap contract would fail
- re-author the existing six `96x80` torso frames with a rear-leg gait
- counter-phase the rear-leg gait against the forward claws
- preserve the existing torso slot size and staggered upload schedule

The existing claw strip already contains six pre-rendered stages. Both claws
share one VRAM slot and therefore must remain frame-locked. A second independent
`64x64` claw slot would add about 64 tiles and does not fit the current
`648/680` sprite allocation without a separate recuo. For v011, sell
independent attack weight through reach, timing and active pruning: only one
claw needs to own the largest attack stage at a time.

### 5. Repair the QA Loop Before Freezing a New Baseline

Do not promote the current visual mismatch by simply replacing the baseline.

Use three independent contracts:

- structural regression: scene id, READY heartbeat, SRAM schema, metrics and
  expected state
- visual regression: deterministic active-gameplay checkpoint, screenshot and
  VDP dump, frozen only after human visual approval
- full-flow regression: branding/menu/chase/pause/result/restart/menu/victory
  with deterministic commands plus a real BlastEm joypad smoke test

The QA-only SRAM bootstrap may be extended with a deterministic command
timeline, but it must remain disabled from the delivery input path. Real
BlastEm input still needs a separate smoke proof so the test does not bypass
`JOY_readJoypad`.

### 6. Correct Scanline Telemetry Before Adding SAT Cost

The current runtime probe does not measure sprites per scanline.
`SPR_getUsedVDPSprite()` returns the maximum number of hardware sprites used by
all active sprite definitions, and the probe clamps that total to 20 before
publishing it as `max_scanline_sprites`.

Current offline scenario simulations report:

- traffic: 14 sprites per scanline
- impact: 9 sprites per scanline
- Pulse: 12 sprites per scanline

These simulations are useful but must be regenerated after every v011 sprite
change. Fix the metric name/collection path or use the canonical scanline
simulator plus VDP evidence before claiming runtime scanline headroom.

## P1 - Cohesion And Readability

### 7. Add Budgeted Contact Shadows

Contact shadows are the highest-value cohesion improvement after the P0 fixes.
They cannot use alpha blending.

Recommended route:

- one small dithered/rune shadow definition shared by hero and active hazards
- one optional boss contact/rune shadow only during a committed attack
- order shadows behind actors in the SAT
- because BG_A road tiles are high priority, audit sprite priority in ROM; the
  shadow must remain visible without covering actor feet
- prune the least important shadow before pruning gameplay-critical sprites

Initial budget target:

- `<=12` additional sprite tiles
- `<=3` additional SAT links in the worst frame
- regenerated scanline simulation must remain `<=20`, with a preferred
  operating target of `<=18`

### 8. Replace the Terminal-Like HUD

Use a fixed custom HUD font, not a proportional compositor in the combat loop.

- create `ui_decision_card` and a glyph manifest from the actual HUD strings
- use a celestial display face for short labels/numbers
- keep a compact 2-row gameplay HUD and the existing WINDOW ownership
- use a small icon/frame tile set for life, Pulse and pressure
- update text at the current restrained cadence rather than redrawing every
  frame
- reuse the reserved font region where possible

The current ownership documentation says PAL1 owns hero/text, while runtime
sets the WINDOW text palette to PAL2. Resolve this contradiction before art
promotion; no fifth palette exists.

### 9. Improve BG_B Without Creating New Raster Owners

The current BG_B table already costs 448 bytes when committed, so different
values inside that same table do not add another DMA table.

Recommended zones:

- deep sky, stars and Moon: zero scroll except attenuated camera shake
- mountain/horizon band: very slow inverse horizontal parallax
- lower road/base band: zero or road-compatible offset to avoid a new seam

Author the band boundaries into the art so line transitions do not cut through
cloud masses or mountain silhouettes. Keep the Moon and stars baked in BG_B;
keep the existing cloud sprites as the moving atmospheric layer.

Palette route:

- increase separation between black, indigo, blue-violet, ivory and gold
- remove near-duplicate low-contrast CRAM entries
- restrict palette cycling to a few emissive/star slots
- reject 60Hz temporal alternation when it creates shimmer at native scale

## P2 - Premium Animation Pass

### 10. Re-author Hero Motion

An 8-frame run and 4-frame jump are valid commercial-quality goals, but this
is new critical source art, not a runtime patch.

Required gates:

- `animation_direction_contract`
- stable foot-contact and pivot contract
- shoulder/arm projection for the Z-axis camera
- cloth secondary-motion contract
- pixel-lock and palette-index audit
- motion GIF from the final promoted strip
- human approval before `res/`

The current four accepted frames remain the fallback until the new full cycle
passes those gates.

### 11. Retune Claw Scale Read

Keep the six current pre-rendered stages, but select attack emphasis from the
same boss attack/Z state that drives reach. Do not allocate an independent far
claw slot in v011 unless a new sprite-residency report first frees at least 64
tiles and the scanline report remains within budget.

## Rejected Or Deferred Techniques

- `sprite_midframe_sat_reuse` / HBlank star multiplexing: `LABORATORIO`,
  signature-only, requires an isolated benchmark ROM and cannot enter v011;
  current runtime scanline headroom is not directly measured
- sprite Moon: spends SAT/VRAM for an element already correctly layered in BG_B
- alpha or semitransparent cloud pixels: unavailable; use deliberate dithering
- independent large claw VRAM slots: does not fit the current sprite allocation
- blind baseline replacement: hides regressions instead of fixing the capture
  contract
- blind 512px unique bitmap: may consume the remaining 70 background tiles
  without solving seam authorship

## Budget Guardrails

| Axis | Current evidence | v011 guardrail |
|---|---:|---:|
| Background tiles | `674/744`, absolute headroom `70` | gutter target `<=48`; default hard acceptance `<=56` extra unique tiles |
| Sprite allocation | `648/680`, headroom `32` | no independent 64-tile far claw slot |
| VBlank DMA peak | `6404/7168` | schedule new obstacle uploads outside near-budget frame |
| Scanline sprites | runtime field is mislabeled; offline scenarios peak at `14` | regenerate report; hard `<=20`, preferred `<=18` |
| CPU | partial sample max `51%` | no regression above stable 60fps envelope |
| H-Int / HBlank | unused / no owner | remains unused in v011 safe route |
| Palettes | PAL0-PAL3 occupied | resolve ownership; no new palette domain |

## Recommended Execution Order

1. Produce the missing design/budget cards and scene-local residency report.
2. Implement shared obstacle Z/collision contract and deterministic tests.
3. Build and compare sparse 512px road-gutter candidates with ResComp counts.
4. Repair boss collar overlap and rear-leg torso cycle.
5. Correct scanline telemetry and regenerate worst-frame reports.
6. Repair structural/visual/full-flow regression contracts.
7. Add pruned contact shadows.
8. Promote fixed custom HUD typography and resolve palette ownership.
9. Add BG_B line-scroll zones and semantic palette remaster.
10. Re-author premium hero motion and retune claw scale read.
11. Build, validate, capture BlastEm, capture VDP dump and request human
    perceptual approval.

## v011 Acceptance Gates

- zero visible BG_A seam at maximum left/right curve plus maximum shake
- no exposed empty gutter or incompatible BG_B road under the overlay
- no head/torso gap at any FK extreme
- readable rear-leg gait in multi-frame evidence
- zero invisible obstacle hits in deterministic collision boundary tests
- obstacle visual frame, shadow and hitbox all derived from the same Z state
- contact shadows do not flicker or exceed the scanline limit
- custom HUD remains readable at native 320x224 and does not look like debug UI
- BG_B bands preserve the Moon/stars as distant fixed anchors
- build passes, validation passes, full-flow regression passes
- BlastEm proves active gameplay, Pulse, collision, result, restart/menu and
  victory on the same ROM hash
- `visual_vdp_dump.bin`, fresh SRAM and human perceptual review are present

Until every gate is met, v011 remains `documentado` or `parcial`, never AAA.
