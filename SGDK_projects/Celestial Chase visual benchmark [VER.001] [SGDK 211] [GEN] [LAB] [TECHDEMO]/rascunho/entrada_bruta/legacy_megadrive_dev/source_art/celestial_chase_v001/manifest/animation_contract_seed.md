# Animation Contract Seed - Celestial Chase v001

Status: seed only. No accepted animation strip exists yet.

## Character: Star Wanderer

### Asset Kind Declaration

- `star_wanderer_model_sheet_approved_v001.png`: `model_sheet`
- `star_wanderer_key_poses_candidate_v001.png`: `key_pose_sheet`

Key pose sheet approval does not approve animation flow. Each runtime animation must be generated or curated as a one-action strip.

### Character Scale Choice

First target: 48x64 px sprite envelope.

Fallbacks:

- 40x56 if road/background readability suffers.
- 64x80 only for title/cutscene or if scanline pressure remains safe.

### Animation State Plan

| State | Priority | Frames | Notes |
|---|---:|---:|---|
| `run_toward_camera` | P0 | 6-8 | primary visual loop, cape secondary motion |
| `stumble_recovery` | P0 | 4 | slows palette cycling and communicates consequence |
| `dodge_left` | P1 | 3-4 | obstacle response |
| `dodge_right` | P1 | 3-4 | mirror or curated variant |
| `look_back_panic` | P1 | 2-3 | anticipation before boss stomp |
| `hurt_trip` | P1 | 3 | readable force direction |

### Pivot And Scale Contract

- Pivot: bottom-center feet.
- Ground contact: one foot or both feet must visually contact road line unless airborne/stumble state declares exception.
- Camera: forward-facing chase camera.
- Identity invariants: hair crescent lock, indigo cape, ivory tunic, blue-gold sash, telescope satchel and star clasp.
- Palette invariants: preserve PAL2 material slots.

### Motion Phase Map Seed

`run_toward_camera`:

1. contact: front foot plants, torso compressed.
2. down: weight drops, cape catches up.
3. passing: feet cross under body, satchel swings.
4. up: torso rises, hair/cape delayed.
5. contact alternate: opposite foot plants.
6. recovery/up alternate: loop closes without scale pop.

### Charisma Contracts

- `idle_breathing_cycle_contract`: required later for idle/menu; not needed for first chase-only loop.
- `facial_expression_phase_map`: required, face is readable in source art.
- `cloth_secondary_animation_contract`: required, cape/sash are part of silhouette.
- `hand_pose_keyframe_contract`: warning, hands are readable but not the focus of the chase loop.

## Character: Clockwork Desert Stag

### Asset Kind Declaration

- `clockwork_desert_stag_model_scale_candidate_v001.png`: `antagonist_model_sheet` + `scale_ladder_source`.

### Runtime Strategy Seed

- Use 4-5 discrete size variants.
- Keep far/mid variants resident for ordinary chase.
- Near/impact variant may be modular, staged or background-plane takeover.

### Modular Boss Rig Trigger

If near variant exceeds safe sprite envelope or scanline pressure, create:

- head/horns part
- torso/neck part
- front hoof left/right parts
- dust/impact FX separate

Do not bake dust or impact into boss body sprites.
