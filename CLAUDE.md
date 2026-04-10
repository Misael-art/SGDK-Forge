# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MegaDrive_DEV is an ELITE homebrew development workspace for **Sega Mega Drive / Genesis** using **SGDK v2.11**. It follows a rigorous methodological standard aimed at surpassing original hardware benchmarks through modular architecture, high-fidelity audio (XGM2), and visual excellence.

## Build Commands

All builds go through the centralized wrapper scripts in `tools/sgdk_wrapper/`. Projects delegate to these wrappers via relative paths — never duplicate build logic in individual projects.

```bat
# First-time environment setup (sets GDK, PATH, installs deps)
setup-env.bat

# Create a new project from the ELITE Golden Template
new_project.bat <project-name>

# Inside any project directory:
build.bat          # Compile ROM (delegates to wrapper, retries up to 3x with auto-fix)
clean.bat          # Remove build artifacts
run.bat            # Launch ROM in emulator (auto-builds if ROM missing)
rebuild.bat        # clean + build
```

There is no test suite — validation happens via `tools/sgdk_wrapper/validate_resources.ps1` which checks resource files pre-build and generates `validation_report.json`.

## Key Environment Variables

- `%GDK%` / `$env:GDK` — Path to SGDK installation (`sdk/sgdk-2.11`)
- `%MD_ROOT%` — Auto-discovered repo root (two levels up from `tools/sgdk_wrapper/`)
- `%JAVA_OPTS%` — Set to `-Xmx2g` for ResComp (SGDK resource compiler)
- `%SGDK_EMULATOR_PATH%` — Auto-detected emulator path from `tools/emuladores/`

## Architecture

### Centralized Build System (`tools/sgdk_wrapper/`)

This is the most critical directory. ALL build logic lives here:

- `env.bat` — Auto-discovers SGDK, configures GDK/PATH, detects Java and emulators
- `build.bat` → `build_inner.bat` — Converts paths to 8.3 short format (to handle `[brackets]` in directory names), then runs `make` with up to 3 retry attempts and automatic error correction
- `fix_migration_issues.ps1` — Converts deprecated SGDK 160 APIs to 211 equivalents
- `autofix_sprite_res.ps1` — Fixes sprite.res dimensions, paths, duplicates; enforces VDP 16-sprite limit
- `validate_resources.ps1` — Pre-build validation of all resource files
- `fix_transparency.ps1` — Corrects PNG palette/transparency issues via ImageMagick

### Project Delegation Pattern

Every project has 3 thin wrapper scripts that delegate up to `tools/sgdk_wrapper/`:

```bat
@echo off
call "%~dp0..\..\tools\sgdk_wrapper\build.bat" "%~dp0"
```

The number of `..` levels varies (2–3) depending on project depth. **Never add build logic to project-level scripts.**

### Directory Layout

- `sdk/sgdk-2.11/` — SGDK toolchain, headers, libraries (gitignored)
- `tools/sgdk_wrapper/` — Centralized build scripts (the single source of truth)
- `tools/emuladores/` — Bundled emulators (BizHawk, Blastem, Exodus, GensKMod)
- `SGDK_templates/base-elite/` — The ELITE Golden Template (Mandatory for new projects)
- `SGDK_projects/` — High-performance game implementations
- `SGDK_Engines/` — Game engine implementations (BLAZE, HAMOOPIG, etc.)
- `doc/` — All documentation (AGENTS.md, migrations, naming conventions)
- `tools/image-tools/` — Python PNG processing utilities
- `archives/` — Compressed backups (gitignored); third-party reference code (`examples/`) arquivado em `archives/cleanup_20260314-190609/reference/examples/`

### Naming Convention

Project directories follow a strict pattern:
```
NAME [VER.XXX] [SGDK YYY] [PLATAFORMA] [TIPO] [GENERO]
```
Example: `BLAZE_ENGINE [VER.001] [SGDK 211] [GEN] [ENGINE] [BRIGA DE RUA]`

Brackets in paths cause CMD parsing issues — the build system converts to 8.3 short paths to work around this.

### SGDK 160 → 211 Migration

Active migration is in progress. Key API changes handled automatically by `fix_migration_issues.ps1`:
- `VDP_setPalette` → `PAL_setPalette(..., DMA)`
- `VDP_setPaletteColors` → `PAL_setColors(..., DMA)`
- `SPR_FLAG_AUTO_SPRITE_ALLOC` → `SPR_FLAG_AUTO_VRAM_ALLOC`

Migration reports are stored in `doc/migrations/`.

## Rules for Modifications

- **Generic fixes** (build logic, error handling): modify only `tools/sgdk_wrapper/`
- **Project-specific fixes**: document in `doc/migrations/` and keep logic out of the wrapper
- Never create copies/forks of existing files — fix in-place
- Never duplicate build logic in project directories
- Documentation goes in `doc/`, not scattered through project folders
- New projects must follow the naming convention defined in `doc/PADRAO_NOMENCLATURA.md`
