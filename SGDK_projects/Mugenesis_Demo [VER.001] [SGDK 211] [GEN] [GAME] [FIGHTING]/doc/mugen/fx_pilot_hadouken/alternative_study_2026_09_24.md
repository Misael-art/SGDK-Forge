# Hadouken pose study — 2026-09-24

## Initial checkpoint

- Branch/commit: `feat/mugenesis-impact-fx-v2` / `7cf00ed8243536d73ea0affa07dba6822c1c511b`.
- Initial working tree already contained changes in `doc/06_AI_MEMORY_BANK.md`, `doc/curation/mugen_intake_index.{json,md}`, `tools/sgdk_wrapper/.agent/skills/art/art-conversion-pipeline/SKILL.md`, `tools/sgdk_wrapper/.agent/skills/code/sgdk-runtime-coder/SKILL.md`, plus untracked `doc/curation/2026_09_24_canonical/`, this continuation prompt, and the conversion safety reference. These were present before this task and were preserved.
- PR #20 was merged. PR #21 is still open on `fix/mugen-provenance-preserve` at `f3b92bb919ab2fd5a01f7a656d0893d1a0e7a2f9`; it is not included in this checkout. PR #22 is still open/draft on this branch at the checkpoint commit. No PR was merged or edited.
- The required suite ran once before changes: `python3 -m pytest tools/mugen2sgdk_forge/tests -q -ra` — 70 passed, no skips reported.

## Source and AIR verification

- Verified `source_750_0.png` and `source_750_1.png` SHA-256 against `source_hashes.json`; both match.
- The selected source is 56x28 RGBA. It has 414 alpha-zero pixels and 1,154 opaque pixels; all alpha-zero pixels use source RGB `(250,0,250)`. The dark core has 68 opaque `(8,8,8)` pixels, so black is not being treated as transparency.
- AIR table was read without edits. `750`: element 1 empty/time 1/offset `(0,0)`; element 2 sprite `750,0`/time 3/offset `(0,-2)`/axis `(20,17)`; element 3 empty/time 1/offset `(0,0)`; element 4 sprite `750,1`/time 3/offset `(0,-2)`/axis `(33,15)`; element 5 empty/time 1/offset `(0,0)`. `751`: sprite `750,2`/time 3/axis `(3,11)`; `750,3`/time 2/axis `(-8,14)`; `750,4`/time 3/axis `(5,16)`; each offset `(0,-2)`.
- The three empty frames, pivots, offsets, flip flags, hitboxes, and action order remain as recorded in `frame_contract.json`. No production frame or contract was changed.
- This RGBA source is not itself the indexed final asset: its height is 28 (the contracted source cell is 56x32), so conversion must pad/crop through the declared pivot-aware pipeline, not by changing gameplay scale.

## Source and human direction

- User supplied the displayed 56x28 projectile and said it is acceptable for the game's context unless a better result is found.
- Attached PNG SHA-256: `a27fba0915dc079d4e6638ddebf9a0efd652a19c69432762250a61855d92a463`.
- Package `source_750_1.png` SHA-256: `2a60f8b75e12156a6d4c8e2fb2a3bbb099cf4ed38a9210e3cd9a63d443764164`.
- The two PNG files have different byte hashes (56x28 RGBA). Their alpha masks and all 1,154 visible pixels match. The 414 transparent pixels differ only in hidden RGB: attachment `(0,0,0)`, package `(250,0,250)`. The package source hash matches `source_hashes.json`.
- The user's acceptance is recorded for this visual source only in `user_source_approval_2026_09_24.md`; it does not approve a palette mapping, indexed candidate, sequence, runtime integration, or ROM result.
- Hash-bound scope record: `doc/mugen/fx_pilot_hadouken/user_source_approval_2026_09_24.md` binds both attachment and project-copy hashes and records the user's approval limits.

## One alternate concept

- Generated with the built-in image generation tool from the accepted original as a pose/style reference. Full prompt: `data/raw_ai/hadouken_fx_pilot_2026-09-24/alternate_01_prompt.md`.
- Output: `data/raw_ai/hadouken_fx_pilot_2026-09-24/alternate_01_visual_source.png`.
- SHA-256: `2d93604762706099fd390bf3969605b99a69e8db2d209bfb34c5ee57f8082721`.
- Dimensions/mode: 1774x887 RGBA; 55,313 RGBA colors; transparency present. This is an AI visual source, not an indexed or native sprite.
- Review: the alternate has a strong dark center and readable energy mass, but spreads the core into a broader wave, exceeds the locked palette, and has not been translated or measured against the 56x32 cell. It has no proven tile or hardware-sprite cost. It does not establish a better production candidate, so the user's original remains the selected visual direction.
- Status: `visual_lab_control`; do not use in `res/`, as a native-pixel source, or as evidence of palette compliance.
- `forge-art inspect` reports 8-bit RGBA/color type 6, 1774x887, no PLTE/tRNS. `forge-art validate --index0-role transparent0` rejects it with `output_not_indexed`, `bitdepth_not_4bpp_compatible`, `dimensions_not_multiple_of_8`, and `index0_contract_violation`. No quantization or resize was run.

## Second and final alternate concept

- Generated as the second permitted initial alternative from the user-accepted pose. Prompt: `data/raw_ai/hadouken_fx_pilot_2026-09-24/alternate_02_prompt.md`; source: `data/raw_ai/hadouken_fx_pilot_2026-09-24/alternate_02_visual_source.png`.
- SHA-256: `7df530ee8a86926b9544baf28195481e4cc14ff6b4110742a423c8726a42b2b2`; 1659x948 RGBA, 28,035 colors, 1,317,241 transparent / 253,685 partially transparent / 1,806 opaque pixels.
- Visual review: the core is compact, but the wide soft halo and motion blur make it less suitable for direct Mega Drive translation than the accepted source. The transparent/partial-alpha edges also do not define a native-pixel silhouette. It does not beat the source in the game's context.
- `forge-art source-audit` report: `rascunho/processado/fx_pilot_hadouken/alternate_02_source_triage_report.json`; blocker `motion_blur_blocks_direct_translation`, status `reference_only_requires_clean_source`, route exploration disallowed. Kept only as `effect_reference`; no resize, palette conversion, indexed candidate or production integration was performed.
- This exhausts the two-alternative limit. The user's provided pose remains selected. The attached-image acceptance does not approve palette slot 6 or any indexed candidate/runtime integration.

## Provisional slot-6 color study

Using the eight exact stable colors in `palette_roles.json`, the source RGB frequency tables in all 15 `source_by_family` entries, and the canonical `delta_e`/`vdp_rgb` functions, an exhaustive scan of the 512 valid VDP colors ranked `0xE82` (RGB 36,144,252) first under the objective of minimizing the worst per-family mean color error after nearest mapping to stable colors plus one candidate FX color. The worst family mean was 37.4 and the mean of family means was 28.1; for `g750_fx`, the mean was 35.8.

This is a measurable trade-off study, not a palette approval. Slot 6 remains null in the contract until the shared FX direction is approved. No clothing slot, body variant, source image, AIR timing, pivot, hitbox, scale, or gameplay value was changed.

## Stage 3 capture checkpoint

- Host preflight passed, and the route selector chose `linux_flatpak_blastem`; it reported `DISPLAY=:0`, Flatpak, xdotool, and ImageMagick capture dependencies present. At route selection, `free -h` showed 1.5 GiB available and 9 GiB swap used.
- The real project-local `out/rom.bin` SHA-256 is `595116bccccd83e0fc45c30cd8a3da9d31dfe0c385182854821eca02494d3623`, matching the known flash-only prefix. At this checkpoint the expected controlled 1200-frame matrix artifacts were incomplete. Separate root-level `out/mugenesis_evidence/fx_*` ROM snapshots do exist; they each provide only 32 profiler samples at different frame counters and are not replacements for the controlled matrix.
- One flash-only capture sealed as `out/mugenesis_evidence/stage3/blastem-linux-20260924T161051Z-3448566/`. It contains a dedicated screenshot, `save.sram`, `visual_vdp_dump.bin`, runtime metrics, audio, and 12 burst frames. `read_sram_metrics.py` reports 71/1141 post-warmup frames over budget (6.2%), max CPU 145, max 10 sprites/line, max 280 pixels/line, and zero frames beyond either H40 scanline limit. The sample denominator is 59 short of the required 1200. Window title was 59.6 fps; that snapshot does not prove sustained frame rate.
- The burst from this session captured the round intro and `FIGHT!`, not an impact flash or shake. It is not flash/shake event evidence.
- A second isolated attempt (`20260924T161519Z-3457713`, warmup 21 seconds, burst at 8 seconds) was rejected: screenshot was solid black (640x480, one color), audio was 0 bytes, SRAM only 300 bytes, and VDP dump/runtime metrics were absent. Exit code was 143. This is a failed host capture; it does not diagnose a game/runtime defect.
- After the failed attempt, memory was 1.7 GiB available with 11 GiB swap used. The 1200-frame A/B matrix remains invalid/incomplete and PR #22 remains draft. No other ROM captures or builds were started.

## Independent recheck on 2026-09-24 continuation

- Rechecked live GitHub state: PR #21 remains open, mergeable, at `f3b92bb919ab2fd5a01f7a656d0893d1a0e7a2f9`; PR #22 remains draft at this worktree's `7cf00ed8243536d73ea0affa07dba6822c1c511b`. The provenance protection is still absent from PR22's checkout.
- Tested PR21 in a detached temporary worktree without switching this task's branch or merging: `test_provenance_preserve.py` passed 4/4; the full converter suite passed 61, with 11 skipped. Skips: 7 host-runtime cases and 2 palette-contract cases lack converted Ken; 2 stage cases lack the third-party stage archive. No failures. These results validate PR21's own tree, not PR22 or a combined tree.
- A read-only `git merge-tree` preview of PR22 `7cf00ed8` with PR21 `f3b92bb9` reports content conflicts in `doc/changelog/changelog.md`, `doc/curation/lessons_2026-09-24_mugenesis.json`, `doc/curation/mugen_intake_index.json`, and `doc/curation/mugen_intake_index.md`. No branch/worktree merge was made. Resolve those after the human decides how PR21 should land; tests passing is not merge approval.
- Current PR22 checkout still contains no production asset reconversion. This safety gate is now independently verified, but is not present in the current integration branch; no merge or cherry-pick was made.
- Re-read the authoritative Stage 3 evidence in the project-local `out/`: the sealed flash-only session exists at `out/mugenesis_evidence/stage3/blastem-linux-20260924T161051Z-3448566/` and its SRAM yields 71/1141 post-warmup over-budget frames (6.2%), max 10 sprites/line and 280 pixels/line. It remains 59 frames short of the required 1200. The second session remains rejected with black screenshot, 0-byte audio, 300-byte SRAM and no runtime metrics/VDP dump.
- The separate workspace-root `out/mugenesis_evidence/fx_*` snapshots are not substitutes: their profiler sample count is 32, each session is a separate ROM/hash and frame counter, and they do not establish the controlled 1200-frame matrix.
- Current host reading after the PR21 tests: 1.3 GiB available, 14 GiB swap used. This is not improved from the failed Stage 3 retry checkpoint; the capture cycle remains closed after its two attempts.
- Later host recheck: `preflight_host.ps1` found the canonical SGDK `linux_wine_bridge`, make/java/Python/ImageMagick and reported “Preflight OK” with one existing `drawText-in-update` lint; process exit code was 2. The independent BlastEm capture selector chose `linux_flatpak_blastem` with no route blockers (target scene 3, warmup 21 s, burst delay 8 s/count 12). Neither check measures available capture memory or authorizes a capture.
- At the route recheck (2026-09-24T19:34Z), the host had 641 MiB available and 13 GiB swap used, worse than the previous 1.3 GiB/14 GiB reading. No new emulator process was started: the two-attempt Stage 3 cycle remains closed and the host has no memory relief.
- Recheck at 2026-09-24T19:47Z: available memory fluctuated from 856 MiB to 690 MiB during inspection, with 14 GiB swap used and 8.5 GiB swap free. Kernel memory pressure was sustained (`some avg10=16.04%`, `full avg10=13.48%`); `chrome-headless` alone held about 2.7 GiB RSS. The capture wrapper has no memory-pressure guard, so route readiness is not resource readiness. No user process was stopped and no capture was launched; the same host-pressure cause still blocks another Stage 3 cycle.
- Host recovery and a new capture cycle at 2026-09-24T23:55Z: 5.6 GiB available and PSI near zero before launch. Re-ran the existing flash-only ROM, SHA-256 `595116bccccd83e0fc45c30cd8a3da9d31dfe0c385182854821eca02494d3623`, in BlastEm NTSC, scene 3, disk audio, warmup 24 s, burst delay 18 s/12 frames/0.10 s. Sealed session: `out/mugenesis_evidence/stage3_matrix/flash_only/blastem-linux-20260924T235547Z-112747/`; exact 1200 post-warmup samples, 71 over budget (5.9%), max CPU 145, max 10 sprites/line, max 288 px/line, no scanline overflow. Screenshot, 32 KiB SRAM, VDP dump, audio (19,906,560 bytes) and 12 burst frames are present; title snapshot was 58.4 fps and is not sustained-FPS evidence. Visual burst shows active gameplay/special projectile but does not establish a hit flash or camera shake. This closes the missing 1200-frame capture for this ROM only; base/shake-only/both matrix and event bursts remain pending. The earlier historical `fx_*` snapshots still are not substitutes because their source state/window differs.

## Project governance gates

- Classified the previously unclassified project as `technical_demo` for this bounded Mugenesis FX pilot. Evidence: the project is named `Mugenesis_Demo`; this request does not promise a complete game or AAA delivery; the current brief/GDD/TDD contain template placeholders. The manifest caps claims at `technical_demo`, records `agent_inferred`, and retains human confirmation for any later context change.
- `validate_project_context.ps1` passed for `planning` and `implementation`, with no blockers. This is a manifest/profile gate; it does not certify placeholder documents as complete.
- Repaired the existing project hygiene manifest to the validator's current schema: classified `.gitignore` and existing build-output roots, and recorded the already-local source archive using `source`, `copied_to`, purpose, authorization and SHA without the legacy absolute origin path. `validate_project_hygiene.ps1` now passes with zero blockers.
- Classified methodology claims from the pilot scope: `critical_motion=required` for `fx_pilot_hadouken_750_751`; `road_physics` and `modular_boss` are `not_applicable`. Added canonical visual/runtime skills. The methodology validator now reports one substantive blocker, `perceptual_motion_unvalidated`: the four positive perceptual axes are absent for the integrated candidate. Existing ROM capture belongs to the prior flash-only build and cannot satisfy this asset-specific gate.
- These governance edits do not approve slot 6 or promote the art. The context and hygiene reports pass; production methodology remains blocked until the candidate is approved, integrated and observed with hash-bound evidence.

## One indexed pose probe and visual comparison

- Created `candidate_750_1_slot6_e82.png` in project staging from the accepted source using a fixed pixel-to-index map. This is deterministic palette conversion, not new pixel drawing. The source and its alpha mask remain unchanged; all 68 opaque black pixels map to index 15. The cell is 56x32 with two transparent padding rows and keeps the contracted anchor `[33,17]` relative to source axis `[33,15]`.
- Slot 6 remains provisional: CRAM word `0xE82`; canonical authoring RGB `(34,136,238)`. The slot contract still has `rgb: null`/`vdp_word: null`; no clothing index is used. This color ranked first in the 15-family error study, but is not human-approved.
- Candidate SHA-256: `4f9f30abcfa23dc6d7db21369d64c689d3b1d2d61764c8bfca68e57bc1a75d66`. A second deterministic generation produced the same SHA-256.
- `forge-art validate --index0-role transparent0` passes as a **technical candidate**: 56x32, indexed color type 3, 4bpp, 16 PLTE entries, three visible indices plus transparent index 0, ResComp color oracle, no blockers. This is not a visual pass.
- Contact sheets: `rascunho/processado/fx_pilot_hadouken/contact_source_vs_candidate.png` is native 1x; `_3x.png` is nearest-neighbor magnification. At 1x and magnified scale, the remap turns much of the cyan/white ramp into a blue/cream two-color mass and looks flatter/warmer than the accepted source. It did not demonstrate a better result. The accepted source remains preferred; do not promote this candidate.
- `source_air_preview.gif` previews the source AIR order only, retaining all eight elements and the three intentional empty frames at their relative durations. It does not claim a converted temporal sequence or movement approval.
- Static geometry estimate remains 26 nonempty 8x8 tiles and 2 32x32 hardware cells for this pose, matching the stated per-frame ceiling. Compiled tile cost and scanline pressure remain unmeasured.
- Added `doc/art/visual_workset_manifest.json`, hash-bound to the accepted source and limited to audit, pixel validation and technical conversion. Workset validation passes with no blocker; native authoring and `res/` promotion are not allowed by this epoch.

## Scope and next step

No production `res/` data changed, no ROM was built, and no art-integrated ROM was captured. The pose-level technical probe is complete; the visual result did not beat the human-approved original. Keep the original selected. To proceed toward integration, a human must explicitly choose the shared slot-6 color and approve the candidate hash or request another palette treatment; only then can the remaining seven AIR elements be converted as an isolated family, reviewed as a temporal sequence, and measured in compiled form. Stage 3 capture remains a separate blocked task as recorded above. No merge or PR action was taken.

## Stage 3 continuation update — 2026-09-25

- The controlled matrix now has four sealed 1200-frame MDRT sessions, one ROM build per toggle combination. Complete hashes and capture settings are in the project report `doc/mugen/stage3_matrix_2026_09_25.json`.
- All four variants measured 250/1200 (20.8%) over budget with max CPU 145, 9 sprites per line, 248 pixels per line, and no scanline overflow. These test-script results are separate from the historical flash-only ROM (`595116bc...`, 71/1200) and must not be blended.
- Reviewed contact sheets for the four matrix bursts, then captured the valid `both` ROM with a 90-frame high-frequency burst. The defender's palette flash is visible around frames 83-85. A subsequent 150-frame high-power event probe was reviewed frame by frame: the attacker pose matches at 95-98% after a (+4,+4) capture-pixel translation in frames 26-28, then returns/reverses in frames 29-31 while the HUD remains fixed; the floor shadow shifts vertically too. This confirms a visible transient in the running `both` ROM. The separate base capture is not phase-synchronized, and legacy EnvShake also contributes to vertical movement, so isolated attribution and perceptual-quality approval remain pending. Details and frame hashes: `doc/mugen/stage3_event_probe_2026_09_25.json`. The screenshot/title snapshot does not prove steady 60 fps; the audio sidecar does not establish audible quality.
- One event attempt accidentally launched the ELF linker output `rom.out` (not a console ROM) and was rejected for black/low-information screenshot and missing VDP/VLAB artifacts. It is retained only as a failed diagnostic; the corrected run used `rom.bin` and sealed against SHA `94139f16...`.
- Existing host-runtime tests include 36,000 ticks for Stage 3 impact effects and cover flash-only-on-hit, exact restoration, hitstop, repeated hits, projectile hits, superpause, KO/round transitions, and direction/variation. The suite result recorded at the initial checkpoint is 70 passed; after adding test-only compile gates, the focused `test_impact_fx_shake_on_heavy_flash_on_hit` passed 1/1. No second full suite run was made.
- The accepted source image and slot-6 decision are unaffected. No candidate sequence or integration was approved, and nothing was added to production `res/`.


## Update 2026-09-25 — slot 6 approved, AIR candidate staged

- The user approved the shared slot-6 choice `0xE82`; canonical authoring RGB is `(34,136,238)`. Record: `slot6_user_approval_2026_09_25.md`. This approves only the shared palette word. The earlier `(36,144,252)` in the provisional metric paragraph is the legacy MUGEN converter display grid; under ResComp both representations encode levels `[1,4,7]` and the same CRAM word. The palette contract records the `forge_art` authoring-grid representation.
- Staged index candidates now cover all five source sprites used by AIR 750/751. The contract still has 8 elements, including intentional empty elements 1, 3 and 5; timings, offsets, axes and hitboxes were not edited. Contact sheet and temporal preview are review artifacts only.
- Source-to-candidate native contact: `rascunho/processado/fx_pilot_hadouken/sequence_source_vs_candidate_native.png` (SHA-256 `866f7d2c31c5b63e0fe12246a487abbc9b41c0a33d7a40967975e554df675def`). The candidate appears lighter and less blue-varied than the source at 1x; no visual approval is inferred.
- ResComp `BALANCED FAST`, raw tile counts for sprites 750,0..4: `24, 28, 12, 8, 16`; active hardware sprites: `2, 2, 1, 1, 1`. In a single AIR `SPRITE` resource, ResComp keeps 8 frames, the three empties and timers `[1,3,1,3,1,3,2,3]`. `BALANCED MEDIUM/SLOW` and `TILE MEDIUM` produce 25 tiles/3 sprites on 750,1; `SPRITE MEDIUM/SLOW`, `TILE SLOW` and `NONE FAST` produce 28/2. The 13-configuration sweep, including BALANCED MAX (25/3) and SPRITE/TILE MAX (28/2), found no joint fit; full-AIR and single-frame probe scopes plus assembly hashes are recorded in the sequence report.
- No production `res/` integration, final game build, DMA/VBlank measurement, scanline simulation or BlastEm evidence. Candidate hashes, strategy data and limits are in `candidate_sequence_slot6_e82_report.json`; promotion remains blocked on hash-bound visual approval and resolving the joint tile/sprite budget.
