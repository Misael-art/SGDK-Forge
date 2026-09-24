# Canonical fixture contracts

These seven rules protect technical fixtures from producing false-green results.
They are intentionally bounded: a passing report is **not** gameplay, performance,
audio, visual quality, budget validation, or `ready_for_aaa` evidence.

1. A sampled gate with zero samples fails (or warns when explicitly optional).
2. Versioned telemetry fails for a missing required field; missing optional fields warn.
3. ROM-side playtest evaluates observed states, never just requested inputs.
4. CRAM legality is evaluated from CRAM words; screenshot colour count is only contextual when raster changes palette mid-frame.
5. Evidence is fresh only when a sealed bundle and every referenced gate share one ROM SHA-256 and passed status.
6. A static table with unchanged input must not rebuild or upload DMA work.
7. A static contract may not claim feature readiness by aggregation or naming.

The executable implementation is `tools/sgdk_wrapper/canonical_fixture_gate.py` and
its ten regression checks live in `tools/sgdk_wrapper/ci/test_canonical_fixture_contracts.py`.
