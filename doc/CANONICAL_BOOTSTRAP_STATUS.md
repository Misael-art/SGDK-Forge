# CANONICAL_BOOTSTRAP_STATUS

Status de bootstrap do root canônico `F:\Projects\Sgdk Forge`, criado em 2026-06-02 a partir de `F:\Projects\MegaDrive_DEV`.

## O que foi copiado

### Raiz (4 arquivos)

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `.gitignore`

### `tools/sgdk_wrapper/` (recursivo, com exclusões)

Wrapper de build completo:
- `.agent/` — framework canônico de agentes (skills, rules, scripts, pipelines, references, lib_case sem `case_editorial_board/`)
- `ci/` — suite de testes de contrato (39 scripts)
- `modelo/` — template canônico de projeto
- `lib/`, `schemas/`, `templates/`, `doc/`, `runtime_probe/`, `_lib/`
- Scripts operacionais: `env.bat`, `env.sh`, `preflight_host.ps1`, `build.bat`, `clean.bat`, `rebuild.bat`, `run.bat`, `new_project.bat`, `blastem_runner.ps1`, `resolve_project.ps1`, etc.
- Documentação interna: `README.md`, `RESILIENCE.md`, `MODELO.md`, `QUICKSTART.bat`

### `tools/ai_imagegen/` (recursivo, com exclusões)

- `workflows/`, `config/`, `imagegen_tool.*`, `run_imagegen_circuit.*`, `README.md`, `CHECKPOINT_*.md`

### `tools/emuladores/` (recursivo)

- `Blastem/`, `BizHawk/`, `Exodus_2.1/`, `GensKMod/` (binários)
- **NÃO** copiados: `Gens.cfg`, `GensKMod.cfg` (user config stale com paths de projetos antigos)

### `tools/image-tools/`, `tools/photo2sgdk/`, `tools/vscode-template/`, `tools/maintenance/`, `tools/gen-scripts/`

- Copiados recursivamente
- Em `tools/maintenance/`, removidos arquivos one-shot que referenciavam paths antigos: `battery_test.py`, `import_batch_20260314_lote2.py`, `survey_elite.py`, `elite_survey.txt`, `migration_scripts/` (todo o subdiretório)
- Em `tools/image-tools/`, removido `rework_viewer_needs_review.py` (one-shot específico de projeto antigo)
- Mantido `tools/maintenance/README.md` como placeholder

### `sdk/sgdk-2.11/` (recursivo, completo)

Toolchain SGDK 2.11 (135.6 MB, arquivos reais — não symlink).

### `.cursor/rules/` (recursivo)

- `megadrive-sgdk-aaa-pipeline.mdc` e subdirs `rules/`, `skills/`

### `doc/` (seleção + 4 subdiretórios)

Arquivos únicos:
- `06_AI_MEMORY_BANK.md`
- `AGENTS.md`
- `PADRAO_NOMENCLATURA.md`
- `TEMPLATE_REGISTRY.md`
- `WORKSPACE_STRUCTURE.md`
- `template_registry.json`

Subdiretórios recursivos:
- `agent_learning/`
- `migrations/`
- `05_technical/`
- `03_art/`

### `doc/migration/`

Criado no destino:
- `canonical_copy_manifest.json`
- `canonical_copy_report.md` (gerado no final)
- `dry_run.log`
- `real_copy.log`

### Estruturas vazias criadas

- `SGDK_projects/` — destino de novos projetos
- `SGDK_Engines/` — destino de engines portadas
- `.agents/` — recebe `README.md` e junction `skills` → `tools/sgdk_wrapper/.agent/skills`

## O que foi propositalmente deixado fora

| Item | Motivo |
|------|--------|
| `assets/`, `data/`, `out/` (raiz) | Específicos de projetos antigos, não canônicos |
| `_archive/` (2 GB) | Já arquivado, sem valor operacional |
| `SGDK_projects/` antigo (1.3 GB) | Projetos permanecem no workspace antigo |
| `SGDK_Engines/` antigo | Engines permanecem no workspace antigo |
| `sgdk_templates/` inteiro | `tools/sgdk_wrapper/modelo/` é o template canônico |
| `tools/ai_imagegen/runtime/` (1.5 GB) | Bundled ComfyUI/venv, reinstalar sob demanda |
| `tools/ai_imagegen/models/` (4 GB) | Stable Diffusion checkpoints, reinstalar sob demanda |
| `tools/ai_imagegen/cache/`, `reports/` | Estado regenerável |
| `tools/16tile/`, `HAMOOPI-PcEngine/`, `nexxt/`, `palette-batch/`, `aseprite-suite/`, `ImageMagick/`, `mugen2sgdk/`, `paletteMergerForSGDK-main/` | Off-platform ou não essenciais |
| `tools/sgdk_wrapper/.agent/lib_case/art-translation/case_editorial_board/` | Caso Metal Slug Urban Sunset com 60+ paths hardcoded de `MegaDrive_DEV` |
| `tools/sgdk_wrapper/out/`, `__pycache__` | Saída e cache |
| `tools/sgdk_wrapper/reproduce_bug.py` | Debug script referenciando `SGDK_templates` (não copiado) |
| `tools/maintenance/*.py` one-shots | Referenciam `SGDK_templates`/`SGDK_Engines` antigos |
| Arquivos soltos da raiz antiga (`fix_mission1.py`, `fix_sky.py`, `inf.txt`, `rascunho.txt`, `*.log`, `*.yml` de CI antigo, `CURADORIA_CANONICA_APLICADA.md`, `STANDARDIZATION_PLAN.md`) | Experimentais ou one-shot |
| `.venv`, `.mypy_cache`, `.tmp`, `.playwright-cli`, `.trae`, `.kilocode`, `.openclaude` (state de IDE) | Estado transitório |

## Ponte `.agents/skills`

`.agents/skills` é uma **junction NTFS** (não diretório real) apontando para:
```
F:\Projects\Sgdk Forge\tools\sgdk_wrapper\.agent\skills
```

Se a junction for quebrada, recriar com:
```powershell
New-Item -ItemType Junction -Path ".agents\skills" -Target "tools\sgdk_wrapper\.agent\skills"
```

Fallback: `New-Item -ItemType SymbolicLink` se a junction falhar (sem dev mode habilitado).

## Como criar novo projeto

1. Via wrapper:
   ```powershell
   .\tools\sgdk_wrapper\new_project.bat
   ```
2. Cópia manual do template:
   ```powershell
   Copy-Item -Recurse .\tools\sgdk_wrapper\modelo `
             .\SGDK_projects\"MEU_PROJETO [VER.001] [SGDK 211] [GEN] [GAME] [ACAO]"
   ```

Convenção: `NOME [VER.XXX] [SGDK 211] [PLATAFORMA] [TIPO] [GENERO]`. Detalhes em `doc/PADRAO_NOMENCLATURA.md`.

## Como validar wrapper, SDK e emulador

```powershell
# 1. Host: Java, make, ImageMagick presentes
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\sgdk_wrapper\preflight_host.ps1

# 2. SDK: makefile.gen existe
Test-Path .\sdk\sgdk-2.11\makefile.gen   # True

# 3. Emulador: BlastEm.exe existe
Test-Path .\tools\emuladores\Blastem\Blastem.exe   # True

# 4. Framework .agent
python .\tools\sgdk_wrapper\.agent\scripts\validate_skill_framework.py
python .\tools\sgdk_wrapper\.agent\scripts\self_check_agentic_aaa_contracts.py
python .\tools\sgdk_wrapper\.agent\scripts\validate_template_registry.py

# 5. Contratos de game design
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\sgdk_wrapper\ci\test_game_design_contract_gates.ps1

# 6. Resolução de ambiente (auto-detecta MD_ROOT)
cmd /c "call .\tools\sgdk_wrapper\env.bat & set MD_ROOT"
# Esperado: MD_ROOT=F:\Projects\Sgdk Forge
```

## Aviso sobre o workspace antigo

`F:\Projects\MegaDrive_DEV` **permanece intocado** para arquivamento. Nada foi apagado, renomeado ou modificado na origem. Toda a operação foi de cópia unidirecional para o novo root.

Se precisar de assets, projetos antigos ou `_archive`, procure na origem. Este novo root é para o **futuro**, não para o passado.
