# AAA Video Curation Handoff

Status: `candidate_applied_not_verified`

Use this handoff when `scene-state-architect` designs scene lifecycle, scene transitions, menu/gameplay/cutscene boundaries or state cleanup.

## New Required Routes

- Route fade/flush/mutex contracts to `game-state-transition-architect`.
- Route level-level asset/camera/collision integration to `level-manifest-architect`.
- Route final runtime evidence to `emulator-vdp-evidence-curator`.

## State Rules

- No scene transition may be treated as safe until input lock, callback cleanup, SAT/sprite reset, CRAM policy and VRAM ownership are declared.
- Scene state and level manifest must share one coordinate truth.
- Any transition touching palettes must coordinate with palette/raster/fade owners.
