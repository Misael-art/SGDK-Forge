# z80-audio-boundary-architect

Use when a Mega Drive project needs music/SFX separation, PCM sample playback, Z80 driver boundaries, DAC usage or audio work that must not starve the 68000 gameplay loop.

## Purpose

Make the Z80 audio boundary explicit. Advanced games often depend on keeping audio streaming and driver work isolated from main CPU gameplay and VDP scheduling.

## Required Inputs

- Driver choice or custom driver intent.
- Music format and SFX format.
- PCM/DAC sample requirements.
- 68000/Z80 communication points.
- Runtime moments with heavy DMA or CPU load.

## Required Outputs

- Audio ownership plan.
- Z80 communication contract.
- PCM/DAC budget risk.
- Fallback when samples compete with gameplay or streaming.

## Hard Rules

- Do not promise high-quality PCM without a driver and bandwidth plan.
- Do not let 68000 gameplay timing depend on blocking audio updates.
- Do not modify sound driver assumptions without updating docs and build resources.

## Handoff

- Use `sfx-prep-fm-psg-pcm` for asset preparation.
- Use `rom-mastering` and emulator evidence before release claims.
