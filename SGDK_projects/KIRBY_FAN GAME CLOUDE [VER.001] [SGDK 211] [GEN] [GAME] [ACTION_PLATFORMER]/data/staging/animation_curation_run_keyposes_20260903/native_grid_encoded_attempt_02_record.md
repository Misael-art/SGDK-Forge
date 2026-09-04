# Native-grid encoded attempt 02

Status: rejected
Classification: producer_capability_failure
Route: native_grid_encoded
Attempt: 2 of 2

The second materially distinct request required an exact 1024x1024 output,
representing a 32x32 logical sprite enlarged by an integer factor of 32, with
binary alpha, hard edges, no grid, no background, and at most eight visible
colors. The image producer rejected the output at moderation with:

```text
HTTP 400 Bad Request
code: moderation_blocked
stage: output
category: other
```

No output file was returned, so no pixels were transformed or measured. This
is recorded as an external producer capability failure, not as evidence that
the requested native grid was achieved. No further equivalent attempts are
authorized in this route.
