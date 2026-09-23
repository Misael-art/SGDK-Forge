# Native-grid encoded attempt 01

Status: rejected
Classification: visual_producer_output_rejected_as_mechanical_or_high_res
Route: native_grid_encoded
Attempt: 1 of 2

The producer output was measured directly from the persisted PNG. No resize,
crop, threshold, quantization, or other image transformation was applied to
the measurement.

| Check | Result |
|---|---|
| Output | `native_grid_encoded_attempt_01.png` |
| Dimensions | `1254 x 1254` |
| SHA-256 | `787e6232bd2012fae3ab409b55bbc4a0b727ba0b4795c014cc11cd4dc95875ca` |
| Dimensions divisible by 32 | `false` |
| Same integer enlargement factor on both axes | `false` |
| Every logical 32x32 block uniform | `false` |
| Binary alpha | `true` (RGB source has no alpha channel; treated as opaque) |
| Visible colors <= 15 | `false` (`28285`) |
| Decision | `mechanical_or_high_res_rejected` |
| Blocker | `native_grid_dimensions_not_divisible_by_32` |

This output is not a native sprite candidate and is not eligible for strip,
runtime, `res/`, or any authorship claim. The route remains open for exactly
one materially distinct attempt.
