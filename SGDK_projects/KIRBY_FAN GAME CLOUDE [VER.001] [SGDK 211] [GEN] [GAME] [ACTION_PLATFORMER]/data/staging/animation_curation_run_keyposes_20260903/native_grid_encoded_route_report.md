# Native-grid encoded route report

Date: 2026-09-03
Route: `native_grid_encoded`
Authority: R1 `data/source_art/r1/r1-01/concept.png`
R1 SHA-256: `591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd`

## Decision

`route_closed_after_two_attempts`

The route did not produce an `ai_generated_native_grid_candidate`. Attempt 01
returned a 1254x1254 high-resolution RGB image that failed exact-grid and
palette recovery. Attempt 02 was rejected by the external producer at output
moderation and returned no image. No resize, crop, threshold, quantization,
vector rasterization, or other rescue operation was used.

| Attempt | Result | Evidence |
|---|---|---|
| 01 | `mechanical_or_high_res_rejected` | `native_grid_encoded_attempt_01_record.md` |
| 02 | `producer_capability_failure` | `native_grid_encoded_attempt_02_record.md` |

Route-level blocker: `native_grid_encoded_producer_unavailable`

The Kirby native-pixel branch remains `blocked_native_pixel_authorship`.
Existing high-resolution guides remain source material only. No final strip,
lineart, `res/` asset, runtime asset, or ROM was produced by this route.
