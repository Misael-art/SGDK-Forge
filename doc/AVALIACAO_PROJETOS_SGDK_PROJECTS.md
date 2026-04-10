# Avaliação de Projetos em SGDK_projects

Data: 2026-03-19

## Objetivo

Avaliar os projetos `teste` e `ELITE_TEST_PROJECT` em `SGDK_projects/` conforme plano de análise de estrutura.

---

## 1. teste

### Estrutura observada

- Diretórios aninhados: `teste/2/3/MeuProjeto/`
- Conteúdo: `assets/`, `graphs/`, `prefabs/`, `scenes/`, `project.rds`
- Subpasta `build/megadrive/` com ROM compilada

### Avaliação

| Critério | Resultado |
|----------|-----------|
| Nomenclatura canônica | Não — nome genérico "teste" |
| Estrutura SGDK padrão | Não — layout com graphs/prefabs/scenes sugere export de outra ferramenta |
| Uso ativo | Incerto — estrutura de rascunho |

### Recomendação

**Arquivar** em `archives/cleanup_20260314-190609/sandbox/SGDK_projects/` ou criar `archives/manual_review/20260319-teste/`.

Motivo: não segue o padrão canônico; estrutura indica material de experimento/export, não projeto SGDK ativo.

---

## 2. ELITE_TEST_PROJECT

### Estrutura observada

- Estrutura canônica: `src/`, `res/`, `inc/`, `rds/`, `doc/`, `.mddev/`
- Wrappers: `build.bat`, `clean.bat`, `run.bat`, `rebuild.bat`
- README.md, .vscode/, .agent/, .cursor/

### Avaliação

| Critério | Resultado |
|----------|-----------|
| Nomenclatura canônica | Parcial — não segue `[VER.XXX] [SGDK 211]...` |
| Estrutura SGDK padrão | Sim |
| Uso ativo | Sim — fixture para validação de build e agentes |

### Recomendação

**Manter** em `SGDK_projects/`.

Motivo: projeto canônico usado como fixture para testes de build e validação. Opcionalmente renomear para `ELITE_TEST_PROJECT [VER.001] [SGDK 211] [GEN] [ESTUDO] [TESTE]` se desejar alinhar à nomenclatura.

---

## Resumo

| Projeto | Ação |
|---------|------|
| `teste` | Arquivar |
| `ELITE_TEST_PROJECT` | Manter |

---

## Próximos passos (opcional)

1. Executar movimentação de `teste` para `archives/` após confirmação.
2. Documentar `ELITE_TEST_PROJECT` como fixture oficial em `doc/` ou `SGDK_projects/README.md`.
