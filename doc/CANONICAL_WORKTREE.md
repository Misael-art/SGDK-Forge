# Worktree Canonico de Projeto

Este documento descreve o formato canonico para projetos SGDK dentro do
workspace `MegaDrive_DEV`.

## Objetivo

Padronizar como um projeto e apresentado para humanos e para o wrapper de build,
sem exigir que todo projeto antigo seja achatado imediatamente.

## Estrutura recomendada

```text
<PROJETO [VER] [SGDK] [PLAT] [TIPO] [GENERO]>/
  README.md
  .agent/
    ARCHITECTURE.md
    agents/
    rules/
    skills/
    workflows/
    scripts/
  doc/
    README.md
    00-diretrizes-agente.md
    01-visao-geral.md
    02-build-wrapper.md
    03-arquitetura.md
    04-recursos-e-pipeline.md
    05-guia-de-desenvolvimento.md
    06-debug-migracao.md
    07-budget-vram-dma.md
    08-bible-artistica.md
    09-checklist-anti-alucinacao.md
    10-memory-bank.md
    11-gdd.md
    12-roteiro.md
    13-spec-cenas.md

  Estrutura padrao completa e hierarquia de verdade: ver `ESTRUTURA_DOC_PROJETO.md` (nesta pasta).

  .mddev/
    project.json
  src/
  inc/
  res/
  out/
  .vscode/
  build.bat
  clean.bat
  run.bat
  rebuild.bat
```

## Separacao de responsabilidades

- `README.md`: onboarding, objetivo e comandos rapidos
- `.agent/`: bootstrap local da malha canonica de agentes hospedada no wrapper central
- `doc/`: conhecimento tecnico e pedagogico
- `.mddev/project.json`: manifesto estrutural consumido pelo wrapper
- `src/`, `inc/`, `res/`: conteudo editavel do projeto
- `out/`: artefatos gerados

## Layouts suportados

### `flat`

O SGDK root coincide com a raiz do projeto.

### `nested`

A raiz humana do projeto contem `README.md`, `doc/` e os `.bat`,
mas o SGDK root real esta em uma subpasta indicada por `.mddev/project.json`.

### `vendor`

Reservado para integracoes futuras com repositorios de terceiros, quando
o codigo importado nao deve ser reorganizado imediatamente.

### `collection`

Usado quando a raiz agrega mais de um papel tecnico relevante, por exemplo:

- uma engine SGDK buildavel
- uma ferramenta de host
- assets ou dados de referencia

Nesses casos, a raiz nao deve se apresentar como uma unica `ENGINE`.
Ela vira uma colecao canonica com:

- `variants/` para entradas buildaveis
- `companions/` para ferramentas ou componentes de host
- `upstream/` para preservacao do material importado
- `build_policy: "disabled"` no manifesto da raiz

## Regra de nomenclatura por papel

- Projeto buildavel unico:
  `<NOME> [VER] [SGDK] [PLAT] [ENGINE|GAME|TEMPLATE] [GENERO]`
- Raiz agregadora:
  `<NOME> Toolkit|Collection|Suite [VER] [SGDK] [PLAT] [COLLECTION] [GENERO]`
- Variante buildavel dentro da colecao:
  `<NOME> Core|<NOME DA DEMO> [VER] [SGDK] [PLAT] [ENGINE|GAME] [GENERO]`
- Ferramenta auxiliar de host:
  `<NOME DA FERRAMENTA> [VER] [HOST] [TOOL] [PIPELINE|EDITOR|AUDIO|...]`

## Manifesto `.mddev/project.json`

Campos minimos esperados:

```json
{
  "schema_version": 1,
  "display_name": "Meu Projeto [VER.001] [SGDK 211] [GEN] [GAME] [ARCADE]",
  "project_root": ".",
  "sgdk_root": ".",
  "layout": "flat"
}
```

## Regras operacionais

- Scripts locais nao carregam logica de build; apenas delegam ao wrapper central.
- A `.agent` canonica mora em `tools/sgdk_wrapper/.agent` e e copiada para o projeto apenas quando a pasta local nao existir.
- Correcoes genericas vao para `tools/sgdk_wrapper/`.
- Arquivos ambiguos, logs, wrappers legados e binarios soltos vao para
  `archives/manual_review/` para validacao manual.

## Automacao de canonicalizacao

Use:

```bat
python tools\sgdk_wrapper\canonicalize_projects.py --apply
```

Esse script:

- detecta `flat` e `nested`
- cria `.mddev/project.json`
- cria `README.md` e `doc/` onde estiver faltando
- padroniza `build.bat`, `clean.bat`, `run.bat` e `rebuild.bat`
- move wrappers legados e artefatos soltos para `archives/manual_review/`
