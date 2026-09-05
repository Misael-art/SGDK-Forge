# Forward-test consolidated gate v01

Date: 2026-09-02. Scope: independent animated-sprite pipeline test across recursive `SGDK_projects` inventory.

## Human gate

No candidate below is approved for `res/`, runtime, ROM, or delivery. The human must decide, per eligible game:

1. identity source and rights/provenance;
2. native canvas, scale, pivot, and baseline;
3. native key-pose line art for idle plus one locomotion/action strip;
4. route-board preference and visual rejection notes;
5. authorization for native pixel authoring and then animation-contract validation.

## Independent results

- BLUE_CIRCUIT: source audit passed; 20-route board passed verification; 24x32 geometry probe passed; native authoring remains blocked.
- KIRBY_FAN GAME CLOUDE: source audit passed; canonical native 32x32 route stopped at `native_pixel_integer_scale_mismatch`; no strip promotion.
- KIRBY_FAN GAME GROK BUILD: source audit passed; canonical native 32x32 route stopped at `native_pixel_integer_scale_mismatch`; no strip promotion.
- MARE_BRAVA: source audit passed; 6-route board passed verification; 56x80 geometry probe passed; native authoring remains blocked.
- Celestial Chase Revive: no clean Lio identity/model-sheet authority in the inspected source set; production blocked before route generation.

## Technical truth

`forge-art convert` outputs for BLUE and MARE are `technical_candidate` only. Their generated chroma sources have non-uniform matte pixels and are rejected by the visual/fake-pixel-art gate. They are retained as evidence, not as sprite sources.

The VDP probes are single-actor geometry checks, not runtime budget proof. No ROM, `res/` promotion, build, or BlastEm gate was run in this forward-test because the human gate is still open.
