# PROJECT_NAME

Status: [PROTOTYPING/PRODUCTION]
Target: Sega Mega Drive / Genesis (SGDK 211)

## High-Level Vision
Define the "Elite" benchmark this project aims to achieve in graphics, sound, and special effects.

## Quick Start
1. `build.bat` to compile.
2. `run.bat` to test.

## Asset Staging
- Put raw images in `res/data/`.
- Keep generated final assets in `res/`.
- The wrapper can mirror `res/data/` into `res/` automatically.
- Old overwritten outputs are backed up to `res/data/backup/`.

## Documentation Suite (Required)
- `doc/01-vision.md`
- `doc/02-architecture.md`
- `doc/03-pipeline.md`
- `doc/player_logic_flow.md`
- `doc/architecture_nodes.md`
