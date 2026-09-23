# Matriz de Contexto e Documentos de Projeto

Este documento e a referencia humana para decidir quais documentos bloqueiam cada tipo de trabalho no SGDK Forge.

## Contextos

| Contexto | Uso | Teto normal |
|---|---|---|
| `aaa_game` | jogo real, vertical slice, entrega jogavel ambiciosa | `vertical_slice`, `ready_for_aaa`, `release_candidate` |
| `technical_demo` | provar tecnica, benchmark, laboratorio com ROM demonstravel | `lab`, `prototype`, `technical_demo` |
| `exercise` | estudo, fixture, treino do agente | `exercise`, `prototype` |
| `game_review` | parecer sobre projeto/material existente | `none`, `concept` |
| `consulting` | orientacao, prompt, plano ou decisao sem implementacao | `none`, `concept` |

## Documentos Bloqueantes

| Documento | AAA | Demo tecnica | Exercicio | Review | Consultoria |
|---|---:|---:|---:|---:|---:|
| `doc/project_context_manifest.json` | B | B | B | B | B |
| `doc/00-project-brief.md` | B | B | B | - | - |
| `doc/11-gdd.md` | B | R | - | - | - |
| `doc/15-tdd.md` | B | F | - | - | - |
| `doc/13-spec-cenas.md` | B | B | - | - | - |
| `doc/14-plano-de-provas-qa.md` | B | B | - | - | - |
| `doc/16-ldd.md` | F | - | - | - | - |
| `doc/17-audio-design.md` | F | - | - | - | - |
| `doc/18-asset-register.json` | B | B | - | - | - |
| `doc/19-roadmap-risk-register.md` | B | R | - | - | - |
| `doc/20-release-marketing-legal.md` | F | - | - | - | - |
| `doc/21-review-consulting-context.md` | - | - | - | B | B |
| `doc/10-memory-bank.md` | B | B | B | B | B |
| `doc/changelog/changelog.md` | B | B | B | - | - |

Legenda: `B` bloqueante; `F` bloqueante por fase/promessa; `R` recomendado; `-` nao bloqueante por padrao.

## Regra Operacional

1. Rode `tools/sgdk_wrapper/adopt_project_methodology.ps1`.
2. Classifique `doc/project_context_manifest.json`.
3. Rode `tools/sgdk_wrapper/validate_project_context.ps1`.
4. So entao abra GDD, TDD, arte, runtime, review final ou consultoria.

`validate_project_context.ps1` e a fonte executavel dessa matriz. Este documento serve para leitura humana e orientacao do agente.
