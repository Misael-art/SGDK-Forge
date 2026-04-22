# Validação dos .bat em Relação ao Wrapper

Data: 2026-03-19

## Objetivo

Garantir que todos os arquivos `.bat` do projeto deleguem corretamente ao wrapper centralizado em `tools/sgdk_wrapper/`, sem duplicar lógica de build.

---

## Padrão Canônico

### Projetos em 2 níveis (SGDK_projects, SGDK_Engines, SGDK_templates)

```
call "%~dp0..\..\tools\sgdk_wrapper\build.bat" "%~dp0"
call "%~dp0..\..\tools\sgdk_wrapper\clean.bat" "%~dp0"
call "%~dp0..\..\tools\sgdk_wrapper\run.bat" "%~dp0"
call "%~dp0..\..\tools\sgdk_wrapper\rebuild.bat" "%~dp0"
```

Caminho: `..\..` (2 níveis até a raiz do workspace).

### Projetos em variants/ (4 níveis)

```
call "%~dp0..\..\..\..\tools\sgdk_wrapper\build.bat" "%~dp0"
call "%~dp0..\..\..\..\tools\sgdk_wrapper\clean.bat" "%~dp0"
call "%~dp0..\..\..\..\tools\sgdk_wrapper\run.bat" "%~dp0"
call "%~dp0..\..\..\..\tools\sgdk_wrapper\rebuild.bat" "%~dp0"
```

Caminho: `..\..\..\..` (4 níveis: variant → variants → collection → SGDK_Engines → raiz).

---

## Resultado da Validação (2026-03-19)

### Categorias de .bat

| Categoria | Caminho | Status |
|-----------|---------|--------|
| **Raiz** | `new-project.bat`, `setup-env.bat` | OK — delegam a `tools\sgdk_wrapper\` |
| **Wrapper** | `tools/sgdk_wrapper/*.bat` | OK — lógica central (build, clean, run, rebuild, env, load_project_context, new_project, ensure_project_agent) |
| **Projetos 2 níveis** | SGDK_projects, SGDK_Engines, SGDK_templates, tools/sgdk_wrapper/modelo | OK — usam `..\..\tools\sgdk_wrapper\` |
| **Projetos variants** | SGDK_Engines/*/variants/*/ | Corrigido — passaram de `..\..\` para `..\..\..\..\` |
| **Outros tools** | `tools/photo2sgdk/run.bat` | N/A — não é SGDK; launcher próprio |

### Correções Aplicadas

- **76 arquivos** em `variants/` tinham caminho incorreto (`..\..\` em vez de `..\..\..\..\`).
- Todos foram corrigidos em 2026-03-19.

### Coleções com variants corrigidas

- XGM2 Driver Samples (XGM2 Sound Test, XGM2 Sonic Audio Demo)
- PlatformerEngine Toolkit (PlatformerEngine Core)
- MegaDriving (19 variantes: Lou, Spacer, Streeter)

---

## Regras para Novos Projetos

1. **Projeto na raiz de SGDK_projects ou SGDK_Engines:** use `..\..\tools\sgdk_wrapper\`.
2. **Projeto dentro de `variants/`:** use `..\..\..\..\tools\sgdk_wrapper\`.
3. **Projeto em subpasta mais profunda:** calcule os níveis até a raiz do workspace e use `..\` × N + `tools\sgdk_wrapper\`.
4. **Bootstrap de projeto novo:** `new_project.bat` e `new_project.sh` partem de `tools/sgdk_wrapper/modelo`, com fallback para `SGDK_templates/base-elite`.

---

## Referências

- [AGENTS.md](AGENTS.md) — Delegação obrigatória
- [tools/sgdk_wrapper/README.md](../tools/sgdk_wrapper/README.md)
- [CANONICAL_WORKTREE.md](CANONICAL_WORKTREE.md)
