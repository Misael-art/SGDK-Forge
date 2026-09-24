# Independent branch status - 2026-09-03

This is a causal triage of work that does not require inventing Kirby native
pixels. It records what can advance as documentation or measurement and what
is blocked by missing native visual authorship.

| Branch | Evidence in project | Status | Next causal action |
|---|---|---|---|
| Branding | `res/branding/*`, `src/scenes/scene_branding.c`, branding audio | existing indexed path | keep runtime/evidence audits separate from character art |
| Stage BG_A/B | `res/gfx/ph_*`, `res/bgs/*`, R1/R2 layer studies | placeholder/source-only | native tile/plane authoring plus scene budget and emulator proof |
| Terrain/tile kit | `data/source_art/r1/r1-05/concept.png`, placeholder terrain | conceptual only | author tileable 8x8-native kit; no direct concept conversion |
| Boss modular set | R1/R2 Whispy studies, `ph_branch`, `ph_boss_face`, `ph_apple` | placeholder/source-only | author independent segment sprites and validate pivots/collision |
| HUD/UI | runtime state/playtest code, no final visual pack in `res/` | visual branch blocked | author UI assets independently, then resource/provenance gates |
| Ability FX | staged fire/beam visual sources and `res/sprites/ph_ability_fx.png` | source/placeholder-only | native FX authoring route; no high-res rescue or resource promotion |
| Kirby idle | `native_idle_key_pose_elite_v01` | bounded isolated review scope | no expansion without a new authorized native pose gate |
| Kirby run/inhale/jump | staged guides only; no native final frames | blocked_native_pixel_authorship | wait for human 32x32 author or an authorized capable producer |
| Runtime/VDP | existing runtime, budget and emulator records | baseline only | measure any new asset only after native source exists |
| BG_A/B and foreground composition | `doc/13-spec-cenas.md`, R1 layer studies, `src/scenes/scene_stage.c` | source/placeholder-only | storyboard planes, measure tile residency, then author reusable native tiles |
| Scene palettes | R1-06, R2/R3 layer corrections, `doc/PALETTES.md` | palette-study-only | bind scene palettes to native tile and sprite owners |
| Parallax | `src/systems/raster.c`, stage layer plan | implemented runtime baseline | remeasure with final scene assets; no new art claim yet |
| HUD and icons | `src/system/overlay.c`, `src/system/playtest.c`, no final UI pack | missing_asset | author indexed UI assets and validate WINDOW ownership |
| Title screen and menus | `res/bgs/ph_title_*`, `res/gfx/ph_title_logo.png`, title/menu scenes | placeholder_in_res | replace only with approved native logo/background package |
| Game over and continue | `src/scenes/scene_gameover.c`, placeholder backgrounds | runtime state exists; final art missing | author scene-specific UI and capture emulator evidence |
| Typography | technical text paths in menu/overlay; no final font asset | missing_asset | select/author font contract and check readability at 1x |
| FX with usable sources | staged Fire/Beam guides, `res/sprites/ph_ability_fx.png` | visual_source/placeholder-only | native FX authoring or explicit valid conversion route |
| Enemies | `res/sprites/ph_enemy.png`, `src/entities/enemy.c` | placeholder_in_res | obtain/author enemy source, then native sprite and collision gates |
| Whispy and boss arena | R1/R2 studies, `ph_branch`, `ph_boss_face`, `ph_trunk`, `scene_boss.c` | visual_source/placeholder-only | separate modular segment authoring, pivots, arena composition and budget |
| Five ability contracts | Fire/Beam/Cutter/Stone/Sword states in `src/entities/ability.c` | runtime contract exists; visual assets missing | bind per-ability native FX/poses and individual budget evidence |
| Transitions | `contracts/transition_contract.json`, scene/app state code | documented/implemented baseline | validate ownership teardown with final assets; no visual promotion |
| Placeholder review | `res/resources.res`, `doc/art/production_asset_manifest.json`, provenance audit | audited; placeholders remain | keep placeholders explicitly non-final until replacement gates close |
| Aggregate scene budget | existing offline scene/budget reports and VDP self-check | baseline only | recompute after native tile/sprite package exists; no final budget claim |
| Build/runtime measurement | existing ROM and BlastEm evidence | existing baseline; no new visual integration | retain current proof and remeasure only after authorized resource changes |

No branch in this table is silently considered complete. A branch can be
advanced independently, but its final claim still requires its own native
source, provenance, resource, budget, and emulator gates.
