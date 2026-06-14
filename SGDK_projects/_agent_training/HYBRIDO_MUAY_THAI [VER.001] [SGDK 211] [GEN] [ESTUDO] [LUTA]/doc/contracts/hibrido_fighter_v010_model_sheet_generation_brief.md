# Hibrido Fighter v010 Model Sheet Generation Brief

Status: `blocking_brief_before_sprite`

This brief exists because v008 is accepted as art direction, but not as a fully
locked sprite baseline. The v009 sprite sheet is rejected and must not be used
as visual baseline.

## Source Of Truth

- Direction source: `data/source_art/hibrido_fighter_v008/source_concept.png`
- Direction record: `doc/contracts/human_validation_record_v008.md`
- Direction gate: `doc/contracts/art_gameplay_direction_gate_v010.json`
- Cohesion audit: `out/logs/hibrido_v010_model_sheet_cohesion_audit_report.json`
- Palette reference: `doc/contracts/hibrido_fighter_v008_palette_map.json`

## Goal

Create a corrected model sheet that preserves the accepted v008 identity while
locking the character for native Mega Drive sprite production. This is not a
runtime sprite sheet and must not be downscaled into one.

## Required Poses

1. Front neutral stance.
2. Back neutral stance.
3. Guard stance in 3-4 side view.
4. Muay Thai knee strike.
5. Teep/front kick or equivalent attack pose with the lava hand visible above
   or beside the leg.

## Must Preserve

- Thick aggressive dark hair with one shared volume model across front, back and
  action poses.
- Focused eyes, strong brow line and expressive face.
- Athletic Muay Thai anatomy: readable chest, shoulders, hips, thighs, hands and
  feet.
- Exposed rock/lava arm with dark stone volume, orange/yellow fissures and a
  readable hand endpoint.
- No wrap, glove or bandage on the lava arm.
- Black Muay Thai shorts with gold trim/ornament.
- Red band on the non-lava biceps.
- Dirty white wraps on the human hand and feet.
- Bronze/dark warm skin separated from rock, shorts and wraps.
- Side-specific asymmetry: do not swap the lava arm, red band or wrap logic.

## Hair Tracking Lock

The first pose may show frontal hair symmetry, but it must map to the same hair
mass as the other poses:

- crown width stays consistent;
- top spikes keep the same number-family and height envelope;
- side spikes may rotate or be occluded by angle, not redesign;
- 3-4 action poses may sweep backward from force, but must keep the same root
  mass and silhouette landmarks;
- back pose must prove the same crown and side-volume, not a new haircut.

If the generated sheet cannot prove this, reject it before sprite planning.

## Face And Acting Lock

- Front/guard: cold focused stare, mouth closed or tense.
- Knee/teep/attack: jaw tension, teeth or kiai mouth where the face permits.
- Eyes always aim toward the opponent line.
- Do not simplify the face into a blank mask.

## Material And Palette Direction

Use the v008 16-color palette as material reference, not as blind quantization:

- index 0: transparent chroma key only in processed runtime assets;
- dark slots: outline, hair, shorts and rock separation;
- warm skin ramp: bronze base with stronger highlight and shadow clusters;
- wraps: dirty off-white, not pure flat white;
- lava cracks: orange/yellow/red clusters inside rock, no random spray;
- gold trim: small readable ornament clusters on shorts and belt.

## Sprite Translation Constraints

The model sheet must be drawable later in native Mega Drive grid:

- no soft AA, blur, smooth gradient or photoreal texture;
- clusters must be large enough to reinterpret in 48x64;
- hands, feet, hair and lava arm must not be clipped;
- silhouette must work in pure black;
- pose scale must support a future 48x64 cell with ground_y and pivot lock;
- FX sparks/glow should be shown as optional separated reference, not baked into
  the body silhouette.

## Rejection Criteria

Reject the model sheet if any of these appear:

- first-pose hair is a different haircut instead of a front-angle view;
- lava arm endpoint is absent, wrapped, gloved or amorphous;
- red biceps band switches side or disappears without occlusion;
- shorts lose black/gold identity;
- face becomes generic across attack poses;
- anatomy changes body scale between poses;
- microtexture/spray would become tile noise at 48x64.

## Next Step

Only after this corrected model sheet is accepted:

1. Write `visual_dna_manifest_v010.json`.
2. Write `animation_direction_contract_v010.json`.
3. Create `animation_state_plan`, `pose_roster`, `frame_budget_table`,
   `pivot_and_scale_contract` and `motion_phase_map`.
4. Produce native 48x64 `lineart_blocking_1px` per state.
5. Create sprite/key pose comparisons before any final sprite sheet.
