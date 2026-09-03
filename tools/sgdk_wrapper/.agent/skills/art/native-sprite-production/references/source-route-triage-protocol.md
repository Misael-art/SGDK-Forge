# Source Sanitation and Route Triage Protocol

Read this reference when a sprite starts from concept art, AI raster, render,
photo-derived art or any high-resolution source that is not already native
pixel art.

The goal is to spend cheap machine time before expensive artistic iteration:
validate the source, execute the applicable mechanical routes under the same
conditions, compare them, then use the best survivor only as an underlay for
native authorship.

## 1. Source roles

- `identity_authority`: defines anatomy, clothing and signature features.
- `translation_source`: clean single-pose image allowed into the route shootout.
- `pose_reference`: informs gesture, never owns hidden anatomy.
- `style_reference`: informs palette/material/finish, never owns geometry.
- `effect_reference`: informs dust, shadow, smoke or impact as a separate FX.

One file may be retained in several reference roles, but only a clean
`translation_source` may enter mechanical route exploration.

## 2. Source sanitation gate

Inspect the image itself, not only metadata. Record each condition in a
`source_triage_spec` and run:

```bash
PYTHONPATH=tools/sgdk_wrapper python3 -m forge_art source-audit \
  --project-root "<project>" \
  --spec "<project>/<spec.json>" \
  --out "<project>/out/logs/source_triage_report.json"
```

The following block direct translation when present, unknown or touching the
silhouette: baked checkerboard, ground shadow, floor line, dust, particles,
smoke, clouds, text, annotations, overlapping poses, cropped extremities,
occluded identity features, motion blur and background-color collision.

If an effect is detached and the identity remains visible, retain the source
as `identity_authority`, `pose_reference`, `style_reference` or
`effect_reference`, but request or generate a clean single-pose model sheet
before the route shootout. Never infer a foot, hand, hair mass or garment from
pixels hidden by an effect.

A clean character translation source has:

- one full-body pose;
- complete hands and feet;
- neutral/transparent background;
- no ground shadow, dust, smoke, cloud, particles or floor line;
- no labels, frame, checkerboard or other editorial content;
- stable anatomy and unobstructed signature features;
- real alpha, or a uniform border-compatible background explicitly routed
  through the border-connected matte extractor.

## 3. Historical priors are contextual

The machine-readable authority is
`tools/sgdk_wrapper/forge_art/route_prior_registry.json`.

For `high_res_full_body_character`, current curated priors are:

- preferred: ImageMagick Lanczos3 and Mitchell-Netravali;
- viable challengers: Catmull-Rom, B-spline, Pillow Lanczos and OpenCV
  Lanczos4;
- experiments: Lanczos2 and cubic variants;
- negative controls: nearest, box/area, bilinear/linear and Hamming;
- GIMP Console routes: host-optional placeholders until deterministic export
  exists.

These priors came from a bounded case. They order experiments; they do not
approve art and do not apply blindly to another source class. For
`native_pixel_art_integer_scale`, nearest-neighbor is the preferred invariant
and interpolating filters are negative controls.

## 4. Route shootout

After `source-audit` returns `route_exploration_allowed=true`, run:

```bash
PYTHONPATH=tools/sgdk_wrapper python3 -m forge_art route-shootout \
  --project-root "<project>" \
  --spec "<project>/<route_shootout_spec.json>"
```

`all_applicable` is the default for a new source class or important asset. It
runs every available deterministic backend and preserves unavailable routes as
explicit skips. `preferred_plus_challengers` is allowed only after the source
class already has useful evidence.

Every executed route must bind:

```text
source SHA-256 -> canonical matte SHA-256 -> backend/version/algorithm/params
-> output SHA-256
```

The suite emits one board and, per route, native-size output, nearest 8x,
silhouette, light/dark/chroma backgrounds, 320x224 composition and metrics.
Outputs remain `mechanical_geometry_probe`; no filter produces native or final
art.

## 5. Triage and native handoff

The route board must preserve the same source, target box, anchor, matte and
canvas. Select at most:

- one primary underlay;
- one challenger with a materially different visual hypothesis;
- one control.

Judge in this order:

1. silhouette and pose at 1x;
2. identity hooks, face/gaze, hands and feet;
3. anatomy and contact with the ground;
4. clothing and material boundaries;
5. edge artifacts, halo and microjaggies;
6. only then palette, tile and budget implications.

No numeric metric or historical prior chooses the winner automatically. A
challenger is invalid when it is only a recolor, near-duplicate or relabelled
output without a distinct hypothesis.

The selected method must be named causally, for example:
`native_reauthoring_over_im_lanczos3_guide`. Do not call a later redraw
`im_lanczos3`; the filter and native author are different stages.

## 6. Prohibitions

Never:

- draw a final character with ImageDraw, rectangles, polygons, spans or
  hardcoded coordinate masks;
- call a filled color mask `lineart_blocking_1px`;
- use semantic owner/shade maps to replace drawing or infer anatomy;
- label a candidate with a route whose source pixels were not causally used;
- use a rejected candidate as the next pixel source;
- promote a resize, quantization or route probe to native art;
- let pixel count, route delta, palette compliance or tile budget buy visual
  approval;
- open a human gate when every candidate already fails identity or source
  sanitation;
- ask a human to manufacture the missing PNG when a different safe producer or
  representation remains available.

## 7. Stop conditions

End a route, not the asset, after two equivalent failures. Change producer,
representation, source or hypothesis. Stop the asset only for missing rights or
identity authority, an indispensable product decision, measured hardware
impossibility, or real exhaustion of distinct safe routes.

No artifact from this protocol supports `visual_pass`, `ready_for_res`, ROM or
AAA without the downstream native, technical, budget, human and emulator gates.
