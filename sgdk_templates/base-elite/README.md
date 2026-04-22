# __PROJECT_NAME__

Status: [PROTOTYPING/PRODUCTION]
Target: Sega Mega Drive / Genesis (SGDK 2.11)

## High-Level Vision

Defina o benchmark ELITE do projeto em:

- fantasia central
- loop principal
- first playable slice
- front-end profile

## Quick Start

1. Seedar `doc/11-gdd.md`, `doc/12-roteiro.md` e `doc/13-spec-cenas.md` com `planning/game-design-planning`.
2. `build.bat` para compilar.
3. `run.bat` para testar.

## Asset Staging

- Coloque imagens brutas em `res/data/`.
- Mantenha assets finais consumidos pelo SGDK em `res/`.
- O wrapper pode preparar `res/data/ -> res/` automaticamente.
- Arquivos sobrescritos vao para `res/data/backup/`.

## Documentation Suite (Required)

- `doc/10-memory-bank.md`
- `doc/11-gdd.md`
- `doc/12-roteiro.md`
- `doc/13-spec-cenas.md`
- `doc/03-arquitetura.md`
