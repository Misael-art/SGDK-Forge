# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Summary

"Pequeno Principe: Cronicas das Estrelas" — an original Sega Mega Drive / Genesis game built with **SGDK 2.11**. A poetic adventure inspired by The Little Prince, currently a **vertical slice** with 4 playable micro-planets (B-612, King, Lamplighter, Desert), designed to expand to 12 planets with 11 unique inter-planet travel sequences.

Documentation is in Portuguese (pt-BR). The parent workspace `CLAUDE.md` (two levels up) covers the centralized build system — do not duplicate that here.

## Build and Run

```bat
build.bat          # Compile ROM (delegates to ../../tools/sgdk_wrapper/)
run.bat            # Launch in emulator (auto-builds if ROM missing)
clean.bat          # Remove build artifacts
rebuild.bat        # clean + build
```

Output ROM: `out/rom.bin`. There is no test suite — validation is visual (emulator) and structural (`doc/13-spec-cenas.md` budgets).

## Mandatory Reading Before Any Code Change

Read these documents **in order** before writing code:

1. `doc/10-memory-bank.md` — Current project state and last session's work
2. `doc/11-gdd.md` — Game design: mechanics, progression, rules
3. `doc/13-spec-cenas.md` — Per-scene hardware budgets (VRAM, DMA, sprites, H-Int)
4. `doc/00-diretrizes-agente.md` — Agent workflow rules and prohibited actions
5. `doc/12-roteiro.md` — Script/dialogue (if touching narrative)
6. `doc/03-arquitetura.md` — Code architecture (if creating/moving files)

Respond with `[Contexto Carregado]` and a plan before generating code. Work that skips this flow is considered untrusted.

## Truth Hierarchy

When documents conflict, higher rank wins (see `AGENTS.md` for the full 10-level table). In practice: Memory Bank > GDD > Scene Spec > Agent Rules > Script > Architecture.

## Architecture

### Game Loop

`main.c` is minimal: init `GameContext` → `Game_update()` → `Game_draw()` → `SYS_doVBlankProcess()`.

### Central Header

`inc/project.h` defines all shared types and function prototypes:
- `GameStateId` (8 states: boot, title, story, planet, travel, pause, codex, credits)
- `PlanetId` (B612, King, Lamplighter, Desert — expanding to 12)
- `PlanetScene` (vtable with enter/handleInput/update/draw/exit per planet)
- `FxProfile` (per-scene flags for scroll, H-Int, hilight)
- `GameContext` (monolithic game state — player, scroll tables, dialogue, planet progress)
- `PlayerController`, `ScarfSegment`

### Module Map

| Module | Role |
|--------|------|
| `src/core/game.c` | VDP bootstrap, input, state transitions, VBlank callback |
| `src/states/flow.c` | State machine: enter/update/draw/exit for all 8 states |
| `src/game/player.c` | fix16/fix32 physics, jump, glide, scarf, sprite rendering |
| `src/game/planets.c` | Planet catalog, objectives, palettes, scroll rules, progression |
| `src/render/render.c` | Procedural tile generation, HUD, text screens, disc/tower/dune drawing, travel scene |
| `src/render/hint_manager.c` | H-Int configuration and palette split (Lamplighter) |
| `src/ui/dialogue.c` | Window plane dialogue system (speaker + lines) |
| `src/audio/audio.c` | XGM2 driver: dialogue voice and solve SFX per planet |
| `src/boot/rom_head.c` | ROM header |

### Resources (`res/resources.res`)

Currently hybrid: most tiles are procedural (code-generated in `render.c`), with 4 landmark tilesets + 1 shared sprite palette + 8 WAV files loaded via ResComp.

## Hardware Constraints (Non-Negotiable)

| Resource | Limit |
|----------|-------|
| VRAM | 64 KB (2048 tiles), use max 75% |
| Palettes | 4 x 16 colors (15 visible + transparent) |
| Sprites/scanline | 20 max, budget to 16 |
| Total sprite links | 80 max, budget to 40 |
| DMA/VBlank (NTSC) | ~7200 bytes, budget to 5000 |
| CPU/frame | 16.7ms at 60Hz, budget to 80% |
| H-Int | 1 callback — exclusively in `hint_manager.c` |
| Resolution | 320x224, do not change |

Per-scene budgets are in `doc/13-spec-cenas.md`. Every visual effect addition must be validated against that table first.

## Prohibited Actions

- **No `float`/`double`** — 68000 has no FPU. Use `fix16`/`fix32`.
- **No `malloc`/`free`** in gameplay loop — use static buffers only.
- **No `int`/`long`** — use explicit types: `u8`, `u16`, `s16`, `u32`, `fix16`, `fix32`.
- **No external libraries** beyond SGDK standard.
- **No invented SGDK APIs** — verify functions exist in SGDK 2.11 before using.
- **No deprecated SGDK 1.60 APIs** (`VDP_setPalette`, `VDP_setPaletteColors`, `SPR_addSpriteEx` with 6 args).
- **No DMA outside VBlank** without documented justification.
- **No scenes/planets/mechanics not in the GDD** (`doc/11-gdd.md`).
- **No dialogue changes** without consulting `doc/12-roteiro.md`.
- **No files outside the documented tree** (`doc/03-arquitetura.md`).
- **No modifications to `tools/sgdk_wrapper/`** without proven need.
- **No budget overruns** — if it doesn't fit, simplify the effect.

## Delivery Gate

A task is only "done" when:
1. `build.bat` compiles without errors and produces `out/rom.bin`
2. ROM runs in emulator without crash, jitter, tearing, or sprite overflow
3. Scene budgets from `doc/13-spec-cenas.md` are not violated
4. `doc/10-memory-bank.md` is updated with what changed

Do not use the words "pronto", "completo", "funcional", or "validado" without passing all gates.

## Common AI Hallucinations to Avoid

| Hallucination | Reality |
|---------------|---------|
| Alpha blending | Mega Drive has Hilight/Shadow only |
| Third background plane | 2 planes (BG_A + BG_B) + window, period |
| Sprites for text | Use tilemap or window plane |
| Smooth gradient fades | 61 simultaneous colors; fade is full-palette swap |
| DMA during active display | DMA is only safe during VBlank |
| `int` is 16-bit | GCC for 68000 makes `int` 32-bit; use `u16`/`s16` |
| Variable resolution | The game is 320x224, always |

## Session Handoff

When ending a relevant session:
1. Update `doc/10-memory-bank.md` with what happened
2. If budgets changed, update `doc/13-spec-cenas.md` (requires user authorization)
3. If dialogue changed, sync `doc/12-roteiro.md`
4. Ensure no canonical document contradicts actual code state

## Key Reference Docs

| Need | File |
|------|------|
| Project state | `doc/10-memory-bank.md` |
| Game design | `doc/11-gdd.md` |
| Script/dialogue | `doc/12-roteiro.md` |
| Scene budgets | `doc/13-spec-cenas.md` |
| Travel specs | `doc/14-spec-travel.md` |
| Agent rules | `doc/00-diretrizes-agente.md` |
| Architecture | `doc/03-arquitetura.md` |
| VRAM/DMA budget | `doc/07-budget-vram-dma.md` |
| Anti-hallucination gates | `doc/09-checklist-anti-alucinacao.md` |
| Asset pipeline | `doc/04-recursos-e-pipeline.md` |
| Art direction | `doc/08-bible-artistica.md` |
| Asset production rules | `doc/15-diretrizes-producao-assets.md` |
