# Modelo Canonico do SGDK Wrapper

`tools/sgdk_wrapper/modelo` e a base oficial para novos projetos SGDK deste workspace.

## Proposito

- entregar um worktree completo, copiavel e pronto para edicao;
- padronizar a estrutura de codigo, documentacao e recursos;
- adotar o pipeline canonico `res/data -> res`;
- reduzir retrabalho ao iniciar projetos humanos ou assistidos por IA.

## O que vem pronto

- wrappers locais de `build`, `clean`, `rebuild` e `run`;
- configuracao local ativando `SGDK_AUTO_PREPARE_ASSETS=1` e `SGDK_AUTO_FIX_RESOURCES=1`;
- estrutura de `src/`, `inc/`, `res/`, `doc/`, `out/` e `.mddev/`;
- base em C com bootstrap, input, maquina de estados e cenas iniciais;
- diretorios `res/data/` e `res/data/backup/` ja preparados para o pipeline.

## Como usar

1. Copie `tools/sgdk_wrapper/modelo` para `SGDK_projects/<nome-do-projeto>`.
2. Atualize `.mddev/project.json`.
3. Coloque assets brutos em `res/data/`.
4. Declare os recursos finais em `res/resources.res` quando houver assets reais.
5. Edite `src/` e `inc/`.
6. Rode `build.bat`.

## Regra de ouro

`res/data/` e a origem dos brutos.

`res/` e a saida final consumida pelo SGDK.

`res/data/backup/` guarda o estado anterior sempre que o wrapper precisa corrigir ou sobrescrever um arquivo.
