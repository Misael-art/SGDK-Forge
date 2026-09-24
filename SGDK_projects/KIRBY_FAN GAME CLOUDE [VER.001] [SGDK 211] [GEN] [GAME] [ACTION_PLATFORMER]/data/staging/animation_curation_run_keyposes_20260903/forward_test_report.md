# Forward visual production report — 2026-09-03

## Scope

- branch: codex/curadoria-animacao-canonica-v09
- animation authority commit: 61fb89285267c2cfdb3695ea308eb18c0e0e2c19
- artistic lifecycle authority commit: 1ee9f3ef6f4327a714ec73658b04b644037c8b16
- R1 authority SHA-256: 591d310623aaf37426af1cb846a715c1fd88e905163364d64565278ed31303cd
- policy: deferred_nonpromotional_review
- scope: new staging only; no v04-v09, res/, runtime or ROM promotion

## Visual producer outputs

| pose | file | SHA-256 | classification | triage |
|---|---|---|---|---|
| run_contact | run_contact_visual_producer_output.png | a09d47517e577d90dbcd6c4e7fb04b5b9fee12d20c2df34dc6045a7dd22bf519 | visual_producer_output | survives initial right-facing/contact review |
| run_passing | run_passing_visual_producer_output.png | 717dca21979690292d7278d9bab2f22334a1ac766d4cf240b67a89f0be56d66e | visual_producer_output | survives initial right-facing/passing review after one blocked attempt |
| run_flight_push | run_flight_push_hypothesis2_visual_producer_output.png | 13cc7ff2bdbd0c474f3a96306e26b88d5ce19e15b5e02773ddefca57b338a67b | visual_producer_output | survives initial right-facing/extension review |

All three are RGB high-resolution sources. They are not native 32x32 sprites, not lineart, not strips, and not promotion candidates. The first flight output (44a2e32271af197e092d7054d8cef1f19e7306bf780ed731b505fd8ea2d229e8) was retained as negative evidence and rejected for front/three-quarter viewpoint discontinuity.

## Source audit and route exploration

- forge_art source-audit: all three corrected runs rc=0, status=accepted_translation_source, blockers=[]; automatic alpha measurement reported full opaque RGB canvases, so no transparency was falsely claimed.
- forge_art route-shootout: contact, passing and flight each rc=0, status=completed, verification.status=passed, automatic_winner=null, claim_ceiling=mechanical_geometry_probe; each board was explicitly guide-only. The current registry expanded preferred_plus_challengers to 16 executed routes per pose, exceeding the requested three-route cap; this is recorded as a tooling limitation, not a selection or winner.
- forge_art translate: each pose rc=3, status=blocked_pending_capable_producer; no pixels were produced.

## Native and animation status

No authorized native pixel producer was available. No resize, crop, quantization, SVG, primitive drawing, ImageDraw, or mechanical conversion was used as final art. Consequently no native 32x32 key pose, native lineart, inbetween, run strip, GIF, composition, contact overlay, motion report or 12-principles report was fabricated.

The trio is therefore not complete at the required gate: the causal high-resolution reference set survived, but native reauthoring is blocked pending a capable producer. Human review remains pending and is not simulated.

## Validation results

- forge-art self-check: rc=0, 126/126, blocking false; framework emitted its designed protected-tree rollback warning during hostile fixtures.
- test_art_pipeline.py: rc=0, 128/128.
- test_animation_validation.py: rc=0, 29/29.
- test_native_sprite_semantic_gate.py: entrypoint present; no native record existed, so not run against a nonexistent candidate.
- No new strip/motion/candidate validator invocation was applicable because no native strip was created.

## Budget

planning_budget only. No native frame exists to measure unique/raw tiles, DMA, VRAM or scanline pressure. Target remains one 32x32 cell, shared palette of at most 15 visible colors plus transparent index, with runtime/budget validation deferred until a real native record exists.

## Claim

status=technical_pass_visual_semantic_fail
claim_ceiling=technical_temporal_probe
animation_candidate=false
human_gate_ready=false
human_gate_status=pending
promotable=false
res_promotion=false
runtime_authorization=false
rom_authorization=false
ready_for_aaa=false

## Next causal gate

Provide or authorize a visual producer capable of native 32x32 pixel authorship. Then reauthor one run_contact key pose directly on-grid, independently validate it, and only after it survives 1x proceed to passing, flight, inbetweens and a diagnostic run strip. No promotion is authorized by this report.
