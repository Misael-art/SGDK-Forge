# SGDK-Forge

![SGDK 2.11](https://img.shields.io/badge/SGDK-2.11-1f6feb?style=flat-square)
![Sega Genesis](https://img.shields.io/badge/Sega%20Genesis-Compatible-00a86b?style=flat-square)
![Asset Pipeline](https://img.shields.io/badge/Asset%20Pipeline-Automated-ff8c00?style=flat-square)
![License MIT](https://img.shields.io/badge/License-MIT-black?style=flat-square)

**Modernizing the Sega Genesis Asset Pipeline**

SGDK-Forge is a public SGDK 2.11 sample repository that showcases a resilient, modern asset pipeline for the Sega Genesis / Mega Drive.

It demonstrates how the shared `sgdk_wrapper` prepares raw art, validates palettes, prevents common `rescomp` failures, and keeps `/data` as the source of truth for incoming assets.

This repository is **standalone** with a vendored wrapper in [`/tools/sgdk_wrapper`](./tools/sgdk_wrapper), so a fresh clone does not depend on your original `MegaDrive_DEV` workspace layout.

## Features

- **Auto-Slicing** for large sprite sheets and oversized source art.
- **Palette Validation** before `rescomp`, including indexed mode, transparency, and 8x8 alignment checks.
- **Zero-Config resource generation** from raw files dropped into `/data`.
- **Resilient build orchestration** through the canonical wrapper pipeline.
- **Genesis-friendly defaults** tuned for SGDK 2.11.

## Quick Start

1. **Drop image**  
   Put your raw assets in [`/data`](./data).
2. **Run build**  
   Execute [`build.bat`](./build.bat).
3. **Enjoy**  
   Launch the generated ROM and inspect the diagnostics in [`/out/logs`](./out/logs).

## Standalone Setup

The wrapper is committed inside this repository and the project-level `.bat` files resolve it locally before falling back to any parent workspace wrapper. [`resolve_wrapper.bat`](./resolve_wrapper.bat) is included as a small diagnostic helper.

To compile on a fresh host you still need a valid SGDK installation. Use either:

- an existing `GDK` environment variable that points to SGDK 2.11; or
- a local drop-in at [`/sdk/sgdk-2.11`](./sdk/README.md).

## Source of Truth

`/data` is the canonical home for new assets.

SGDK-Forge uses the wrapper to treat `/data` as the raw staging area, generate or sanitize SGDK-compatible outputs in `/res`, and preserve traceable backups whenever an incompatible file needs to be rewritten.

This keeps responsibilities clear:

- `/data` contains what artists and converters produce.
- `/res` contains what SGDK consumes.
- `/out` contains what the build generates.

## Technical Deep Dive

The most common SGDK image failures happen before gameplay code ever runs. SGDK-Forge addresses them in the wrapper layer.

### How the wrapper avoids palette-related failures

- It inspects the real image mode instead of trusting the file extension.
- It rejects non-indexed results before `rescomp` can fail.
- It aligns sprite dimensions to Genesis-safe 8x8 boundaries.
- It constrains exported results to SGDK-friendly indexed palettes.
- It preserves transparency with explicit handling instead of destructive corner-pixel guesses.
- It creates backups before rewriting incompatible outputs, making automatic fixes traceable.

### What happens during build

[`sgdk_wrapper_env.bat`](./sgdk_wrapper_env.bat) enables:

- `SGDK_AUTO_PREPARE_ASSETS=1`
- `SGDK_AUTO_FIX_RESOURCES=1`

That means [`build.bat`](./build.bat) triggers:

1. raw asset preparation from `/data`;
2. validation and safe image sanitization;
3. the standard SGDK build flow.

### Diagnostics

After a build, check:

- [`asset_preparation_report.json`](./out/logs/asset_preparation_report.json)
- [`asset_preparation_preview.png`](./out/logs/asset_preparation_preview.png)
- [`validation_report.json`](./out/logs/validation_report.json)
- [`build_output.log`](./out/logs/build_output.log)

## Repository Layout

- [`/data`](./data): raw source assets.
- [`/tools/sgdk_wrapper`](./tools/sgdk_wrapper): vendored canonical wrapper used by this repository.
- [`/sdk`](./sdk): optional local SGDK drop-in location for portable builds.
- [`/res`](./res): SGDK-ready resources.
- [`/src`](./src): example ROM logic.
- [`/doc`](./doc): technical notes.
- [`/out`](./out): generated build artifacts.

## Git Bootstrap

To publish this project as a fresh standalone repository:

```bash
git init
git branch -M main
git remote add origin https://github.com/Misael-art/SGDK-Forge.git
git add .
git commit -m "chore: initial forge structure and automated pipeline"
git push -u origin main
```

## Optional Portuguese Summary

<details>
<summary>Portuguese</summary>

SGDK-Forge e uma base publica para demonstrar um pipeline moderno de assets para SGDK 2.11. O diretorio `/data` e a origem canonica dos assets brutos, o wrapper prepara a saida final em `/res`, valida paletas e evita erros classicos do `rescomp` antes do build da ROM.

</details>
