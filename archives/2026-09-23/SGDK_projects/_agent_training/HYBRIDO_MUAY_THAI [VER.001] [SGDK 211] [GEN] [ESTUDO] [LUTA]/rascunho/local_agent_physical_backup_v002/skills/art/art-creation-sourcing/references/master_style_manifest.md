# Master Style Manifest

Use this reference before generating the first original asset and before extending an existing art family.

## Purpose

The `master_style_manifest` is the style memory anchor. It keeps later assets inside the same world instead of relying on seed luck.

## Minimum Manifest

```json
{
  "schema": "master_style_manifest.v1",
  "style_anchor_id": "project_style_v1",
  "project": "<project name>",
  "visual_intent": "<short style statement>",
  "target_platform": "Mega Drive / SGDK 2.11",
  "resolution_contract": {
    "screen": "320x224",
    "primary_sprite": "32x32 or declared tile envelope",
    "tile_grid": "8x8"
  },
  "palette_contract": {
    "vdp_grid": "9-bit channels only",
    "visible_colors_per_palette": 15,
    "palette_hex": ["#000000"]
  },
  "line_contract": {
    "line_weight_px": 1,
    "outline_policy": "constant enough to read at native resolution"
  },
  "lighting_contract": {
    "direction": "top-left or declared",
    "shading": "flat cel shading, 2-3 tones per ramp",
    "forbidden": ["soft blur", "smooth gradients", "partial alpha"]
  },
  "dithering_contract": {
    "allowed": "controlled material/atmosphere transition",
    "forbidden": "random noise or fake gradient"
  },
  "style_drift_thresholds": {
    "color_value_variance_percent": 15,
    "saturation_shift_percent": 15,
    "line_weight_change": "requires review"
  },
  "reference_benchmarks": [
    {
      "name": "<commercial or internal benchmark>",
      "inherit": "<technique only>",
      "do_not_copy": "<asset/IP boundary>"
    }
  ]
}
```

## Prompt Contract

Use this shape for image generation prompts:

```text
Directive: act as a professional 16-bit game asset designer.
Subject: <asset name and role>.
Style anchor: <style_anchor_id>.
Inherit: palette, line weight, lighting, pixel density and material language from the master style manifest.
Format: orthographic sheet or declared gameplay view.
Constraints: indexed-palette intent, hard pixel edges, no anti-aliasing, no blur, no smooth gradients, no partial alpha.
Mega Drive target: 320x224 scene readability, 8x8 tile grid, 15 visible colors per palette.
Negative: soft edges, painterly, fake pixel filter, interpolation blur, inconsistent line weight, excessive colors.
```

## Acceptance Rule

Prefer a coherent asset with slightly lower isolated spectacle over a spectacular asset that breaks the visual world.

If a new asset fails the style anchor, emit `qa_findings` and `correction_request`; do not silently update the style.
