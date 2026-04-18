# SGDK-Forge

![SGDK 2.11](https://img.shields.io/badge/SGDK-2.11-1f6feb?style=flat-square)
![Sega Genesis](https://img.shields.io/badge/Sega%20Genesis-Compatible-00a86b?style=flat-square)
![Asset Pipeline](https://img.shields.io/badge/Asset%20Pipeline-Automated-ff8c00?style=flat-square)
![License MIT](https://img.shields.io/badge/License-MIT-black?style=flat-square)

**Modernizing the Sega Genesis Asset Pipeline**

SGDK-Forge is a public-facing SGDK sample repository focused on a modern, resilient asset workflow for the Sega Genesis / Mega Drive.

It demonstrates how the shared `sgdk_wrapper` can prepare raw art, validate palettes, avoid common `rescomp` failures, and keep `/data` as the source of truth for incoming assets.

## Features

- **Auto-Slicing** for large sheets and oversized source art.
- **Palette Validation** before `rescomp`, including indexed mode, transparency, and 8x8 alignment checks.
- **Zero-Config resource generation** from raw assets dropped into `/data`.
- **Resilient build orchestration** through the canonical wrapper pipeline.
- **Genesis-friendly defaults** tuned for SGDK 2.11.

## Quick Start

1. **Drop image**
   Put your raw assets in [`/data`](./data).
2. **Run Build**
   Execute [`build.bat`](./build.bat).
3. **Enjoy**
   Open the generated ROM and inspect the diagnostics in [`/out/logs`](./out/logs).

## Source of Truth

`/data` is the source of truth for new assets.

SGDK-Forge uses the wrapper to treat `/data` as the raw staging area, generate or sanitize compatible outputs in `/res`, and preserve older versions in `res/data/backup` whenever a file must be corrected or overwritten.

This keeps responsibilities clear:

- `/data` contains what artists and converters produce.
- `/res` contains what SGDK consumes.
- `/out` contains what the build generates.

## Technical Deep Dive

The most common SGDK image failures happen before gameplay code ever runs. SGDK-Forge addresses them in the wrapper layer.

### How the wrapper avoids palette-related failures

- It checks the real image mode instead of trusting the filename.
- It rejects non-indexed outputs before `rescomp` can break.
- It aligns sprite dimensions to Genesis-safe 8x8 boundaries.
- It constrains exported results to SGDK-friendly indexed palettes.
- It preserves transparency with explicit handling instead of relying on destructive corner-pixel guesses.
- It creates backups before rewriting incompatible outputs, making fixes traceable.

### What happens during build

[`sgdk_wrapper_env.bat`](./sgdk_wrapper_env.bat) enables:

- `SGDK_AUTO_PREPARE_ASSETS=1`
- `SGDK_AUTO_FIX_RESOURCES=1`

That means `build.bat` triggers:

1. raw asset preparation from `/data`;
2. validation and safe image sanitization;
3. the normal SGDK build flow.

### Diagnostics

After a build, check:

- [`asset_preparation_report.json`](./out/logs/asset_preparation_report.json)
- [`asset_preparation_preview.png`](./out/logs/asset_preparation_preview.png)
- [`validation_report.json`](./out/logs/validation_report.json)
- [`build_output.log`](./out/logs/build_output.log)

## Repository Layout

- [`/data`](./data): raw source assets.
- [`/res`](./res): SGDK-ready resources.
- [`/src`](./src): example ROM logic.
- [`/doc`](./doc): internal technical notes.
- [`/out`](./out): generated build artifacts.

## Git Bootstrap

To publish this as a fresh standalone repository:

```bash
git init
git add .
git commit -m "chore: initial forge structure and automated pipeline"
```

Then attach your remote and push:

```bash
git branch -M main
git remote add origin <your-github-url>
git push -u origin main
```

## Optional Portuguese Summary

<details>
<summary>Português</summary>

SGDK-Forge e uma base publica para demonstrar um pipeline moderno de assets para SGDK 2.11. O diretorio `/data` e a origem canonica dos assets brutos, o wrapper prepara a saida final em `/res`, valida paletas e evita erros classicos do `rescomp` antes do build da ROM.

</details>
