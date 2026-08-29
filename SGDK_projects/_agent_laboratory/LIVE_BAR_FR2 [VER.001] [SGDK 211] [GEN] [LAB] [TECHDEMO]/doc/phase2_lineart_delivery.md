# F-R2 phase 2 — lineart_blocking_1px at 48x64

`lab_not_delivery=true`. Color blocking is not started.

## Scale

- `character_scale_choice`: 48x64 (6x8 tiles), FAST metasprite
- `scale_lock_status`: locked for this lab idle/guard pose
- FOV: H40 320x224
- Hitbox: not a gameplay fixture; feet planted at sprite y=63
- Head metric: ~11-13 px (L for a 64 px fighter; face reads by contrast, not iris)

## Silhouette

Black fill of the native sprites reads as two different fighters at 320x224:
hero = asymmetric raised fist + mullet; thug = barrel + hook + double guard.

## Lineart

- 1 px hard-edge outline
- One dark temp ink per sprite (hero `#220044`, thug `#440022`)
- Paper fill `#EEEECC` is construction, discarded at color blocking
- Ink maps to outline/dark_shadow in `palette_role_map`; not a swap slot
- Builder: `tools/build_lineart_blocking_1px.py`

## Deferred

- `material_color_ramp_plan` / hue-shift ramps
- color blocking
- motion / GIF
- dock native tiles (still quantized Imagine)

## Findings

- Native reconstruction, not a shrunken photo.
- Anatomy is readable and distinct, still blocky at joints and boots.
- `visual_pass=false`. `ready_for_aaa=false`.
