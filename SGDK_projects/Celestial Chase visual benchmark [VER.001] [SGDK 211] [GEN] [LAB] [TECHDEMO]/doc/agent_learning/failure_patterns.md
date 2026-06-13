# Agent Learning - Failure Patterns

## Sprite Transparency Index 0 Needs A Runtime Color Gate

- date: 2026-06-07
- symptom: a technically green build rendered the hero inside an opaque blue/teal capsule.
- technical diagnosis: the asset remained indexed, but visible mantle/canvas pixels were written outside the silhouette; SGDK correctly drew those non-zero indices as solid sprite pixels.
- preventive heuristic: critical sprite promotion requires both an indexed PNG contract (`transparent_index=0`, bounded edge occupancy, no full-width frame touch) and a BlastEm screenshot color-sampling gate over the hero ROI.
- check in ROM: `out/logs/visual_screenshot_color_gate_report.json` must pass on active gameplay, with no tall forbidden-matte columns; compiler success never clears this gate.

## Road And Motion Claims Need Temporal Evidence

- date: 2026-06-07
- symptom: a single screenshot could hide road shearing, tile shimmer or motion that reads worse than the still frame.
- technical diagnosis: BG_A line/column scroll and pseudo-3D road polish are perceptual systems; static baseline equality cannot prove fluency, naturality or impact.
- preventive heuristic: after every road-equation or BG_A art change, capture a multi-frame emulator sequence and keep `perceptual_check` human-gated unless review scores are explicitly recorded.
- check in ROM: compare frames across the run (`frame_090`, `frame_120`, `frame_150`, `frame_180` or equivalent); road motion must stay coherent while runtime MDRT remains under budget.

## Derived Contract Compilation Must Be Idempotent

- date: 2026-06-04
- symptom: closeout recompiled an unchanged `scene-contracts.json`, changed only `compiled_at`, and immediately made the freshly passing scene regression stale.
- technical diagnosis: generated-artifact timestamps were treated as semantic changes, creating a validation cycle that could never remain fresh.
- preventive heuristic: compare generated contracts without volatile metadata and preserve the existing file timestamp when semantics are unchanged; closeout must compile with the same rigor mode used by the delivery contract.
- check in ROM: compile twice, confirm the contract timestamp is unchanged, then verify freshness keeps scene regression fresh.

## Shared App Scene IDs Need An Explicit Budget Alias Owner

- date: 2026-06-04
- symptom: runtime metrics for gameplay were assigned to the result state because both contracts use `expected_app_scene_id=4` and the last alias silently won.
- technical diagnosis: a numeric runtime scene id cannot distinguish substates that share the same app scene.
- preventive heuristic: declare one `budget_alias_owner` for shared runtime ids; the budget auditor must preserve that explicit owner when later aliases are registered.
- check in ROM: the first playable budget row must receive measured MDRT frames while the result-state row remains separate.

## Measurement Code Must Not Consume The Budget It Measures

- date: 2026-06-04
- symptom: the first true per-scanline runtime probe pushed the chase to `cpu_load_max=138` with 56 frame overruns.
- technical diagnosis: clearing and scanning all 224 visible lines every frame made the diagnostic path more expensive than the behavior under test.
- preventive heuristic: sample four evenly spaced real scanlines per frame and rotate the sampling window; cover all 224 lines over 56 frames while keeping the probe bounded.
- check in ROM: compare a fresh MDRT sample before and after enabling the probe; the instrumented build must keep `over_budget_frames=0`.

## Incremental Build Logs Are Not Durable ResComp Evidence

- date: 2026-06-04
- symptom: a valid measured residency report became unverifiable after an incremental build no longer emitted the original ResComp origin-size lines.
- technical diagnosis: build logs describe work performed in that invocation, not the complete current resource graph.
- preventive heuristic: preserve a ResComp origin-size snapshot bound to each source PNG SHA256 and to the final ROM SHA256; invalidate it when either identity changes.
- check in ROM: `res_graph_report.json` must report measured evidence as valid, zero overlaps and the exact current ROM hash.

## Window-Chrome Variance Needs A Narrow Regression Tolerance

- date: 2026-06-04
- symptom: the result-state regression differed by only 31 pixels because BlastEm's window title showed a variable FPS value.
- technical diagnosis: the whole-window capture included host chrome unrelated to the rendered Mega Drive frame.
- preventive heuristic: prefer content-only capture; when unavailable, scope tolerant comparison to the single affected scene with a threshold small enough to reject any gameplay-frame drift.
- check in ROM: menu and gameplay remain exact-hash comparisons; only the declared result capture may use the documented `0.0005` tolerance.

## Total VDP Sprite Usage Is Not Scanline Pressure

- date: 2026-06-04
- symptom: runtime reports claimed `max_scanline_sprites=20` and the budget gate treated the scene as exactly at the hardware scanline limit.
- technical diagnosis: the runtime probe populated that field from `SPR_getUsedVDPSprite()`, which SGDK documents as the maximum hardware sprite usage summed across all active sprites, then clamped the value to 20.
- preventive heuristic: never label total VDP sprite usage as per-scanline pressure; use the canonical scanline simulator and runtime/VDP evidence for scanline claims.
- check in ROM: regenerate worst-frame traffic, impact and Pulse reports after every sprite-layout change and keep every line at or below 20.

## Populated Width Matters More Than Declared Plane Width

- date: 2026-06-04
- symptom: a 512px hardware plane still exposed road seams during line scroll.
- technical diagnosis: the plane was `64x32` tiles, but the BG_A image populated only the first 320px while line scroll reached `-64px..+17px`; empty columns and an incompatible BG_B road became visible.
- preventive heuristic: audit populated tilemap width, safe gutters and maximum signed scroll together; a larger plane does not create authored continuity.
- check in ROM: test maximum left/right curve plus shake and require zero exposed empty gutter.

## Visual Z And Collision Must Share One State

- date: 2026-06-04
- symptom: hazards appeared visually distant or clear while the fixed lane/Y collision window registered damage.
- technical diagnosis: render position, scale frame and collision activation were independent values.
- preventive heuristic: derive screen position, lane spread, scale frame, contact shadow, hitbox and collision interval from one deterministic Z state.
- check in ROM: capture and test the exact frames immediately before, during and after the collision-active interval.

## Horizontal Parallax Bands Use HScroll

- date: 2026-06-04
- symptom: a proposed BG_B design assigned horizontal speed bands to column scrolling.
- technical diagnosis: `VSCROLL_COLUMN` changes vertical offset by 16px columns; it cannot express horizontal bands moving at different horizontal speeds.
- preventive heuristic: horizontal speed bands belong to `HSCROLL_LINE` or `HSCROLL_TILE`; keep one scroll-table owner and author safe band boundaries into the art.
- check in ROM: verify that sky/Moon stay fixed, the mountain band moves slowly and no line boundary tears a silhouette.

## Signature Raster Tricks Do Not Enter A Saturated Scene By Default

- date: 2026-06-04
- symptom: HBlank SAT multiplexing was proposed to add star sprites while the scene already reached the sprite-per-scanline limit.
- technical diagnosis: the proposal added mid-frame SAT risk, raster ownership and CPU pressure without a gameplay benefit that justified the cost.
- preventive heuristic: keep baked atmospheric detail in BG_B and reserve SAT/HBlank experiments for isolated benchmark ROMs with a declared fallback.
- check in ROM: no signature-only raster technique enters the delivery route without its own scanline, CPU, teardown and corruption evidence.

## v008 Technical Stability Masked Visual Failure

- date: 2026-06-04
- symptom: ROM booted and held frame budget, but the chase composition contained opaque FX mattes, broken hero anatomy, a flat pursuer and inverted plane motion.
- technical diagnosis:
  - FX declared transparency at palette index 0 while their background pixels used index 1.
  - BG_B reserved a beige color at palette index 0, contaminating the global backdrop.
  - The runtime instantiated only the pursuer body despite approved head and hoof modules.
  - BG_B moved faster than BG_A and the road only slid laterally.
  - The methodology incorrectly classified road physics and modular boss as not applicable.
- preventive heuristic:
  - never promote a visual chase by performance metrics alone;
  - validate every critical asset at pixel-index level and in active composition;
  - require depth motion ownership and modular boss runtime symbols when they are part of the scene fantasy;
  - budget pass and visual pass remain independent gates.
- affected metrics:
  - silhouette_readability
  - layer_separation
  - palette_efficiency
  - frame_flow_readability
  - gameplay_visual_link
- check in ROM:
  - active gameplay screenshot must show fixed deep sky, road depth motion, transparent FX and articulated pursuer;
  - multi-frame evidence must prove hero cycle, Pulse expansion and rig motion.

## Static Sprite Scaling Is Not A Modular Boss

- date: 2026-06-04
- symptom: the pursuer appeared as a flat image moving vertically despite the project declaring modular assets.
- technical diagnosis: the body sprite owned the complete silhouette and child modules were never instantiated or updated.
- preventive heuristic: a modular boss claim requires separate runtime sprites, a parent-before-child update order, visible relative motion, SAT pruning and a worst-scanline report.
- check in ROM: capture at least two frames where head and claws change relative position against the torso.

## Z-Axis Chase Cannot Use Inverted Parallax

- date: 2026-06-04
- symptom: distant sky moved faster than the road and the road slid left without forward depth.
- technical diagnosis: both planes were treated as generic horizontal scroll layers without a vanishing-point contract.
- preventive heuristic: keep deep sky fixed or near-fixed; drive forward travel through road depth tables and move atmospheric grafts slower than the playable plane.
- check in ROM: compare consecutive frames at the horizon and screen edge; edge road displacement must exceed horizon and sky displacement.

## Source-Derived Modular Torso Must Exclude External Limbs

- date: 2026-06-04
- symptom: separate runtime claws existed, but residual arms in the derived torso made the pursuer read as having duplicated or tangled limbs.
- technical diagnosis: modularity in code does not repair a source crop that still owns the child module silhouette.
- preventive heuristic: a torso module may retain shoulder sockets and core mass, but must remove the external silhouette owned by separate claws, hooves or weapons.
- check in ROM: inspect a temporal sequence, not one frame; exactly the intended child limbs must dominate at every articulation extreme.

## Per-Scanline Multiplication Can Destroy The Frame Budget

- date: 2026-06-04
- symptom: the cinematic road looked correct but drove the runtime sample to roughly 160% CPU.
- technical diagnosis: multiple multiplications inside a 224-line loop executed every frame overwhelmed the 68000.
- preventive heuristic: derive line deformation with finite differences/addition, update visual tables at 30 Hz when perceptually safe, and keep actor/gameplay logic at 60 Hz.
- check in ROM: require a fresh MDRT sample after every road-equation change; visual correctness does not excuse frame overruns.

## A Black PrintWindow Capture Is Not Emulator Evidence

- date: 2026-06-04
- symptom: the evidence tool reported screenshot success while the PNG contained only black pixels.
- technical diagnosis: the host capturer rejected nearly white `PrintWindow` failures but accepted nearly black failures.
- preventive heuristic: treat almost-uniform white or black `PrintWindow` output as invalid and fall back to a real screen capture.
- check in ROM: visually inspect the dedicated screenshot and require recognizable active gameplay before citing it as evidence.
