# Fixed Point Math Contract

## Purpose

This contract is required before runtime code introduces gameplay math that could be written with `float`, `double`, direct trigonometry, or expensive per-frame divisions.

## Input

- scene or system id
- numeric variables affected by the feature
- unit scale in pixels, sub-pixels, angles, or timers
- selected representation: `u16`, `s16`, `s32`, `fix16`, `fix32`, LUT, or integer ratio
- overflow bounds and clamping policy
- cost note for any 68k ASM or Z80 ASM path

## Output

- `fixed_point_math_contract.md` or embedded section in `runtime_decision_log`
- list of conversions between gameplay units and render pixels
- proof that render output snaps to integer pixels
- fallback to LUT or preload when runtime math is too expensive

## Conservative Defaults

- Use `fix16` for player/camera movement and `fix32` only when range demands it.
- Prefer LUTs for sin/cos/atan-like behavior.
- Avoid per-frame division in hot loops.
- Do not use `float` or `double` in SGDK gameplay.
- Do not promote ASM as safe without cycle notes or a C fallback.

## Minimal Example

```json
{
  "system_id": "camera_lead",
  "representation": "fix16",
  "unit": "pixels_per_frame",
  "range": { "min": -320, "max": 320 },
  "render_snap": "fix16ToInt at sprite/plane write only",
  "overflow_policy": "clamp before accumulation",
  "lut_required": false,
  "asm_path": "not_used",
  "fallback": "integer camera step if budget fails"
}
```
