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
- contratos `doc/project_methodology_manifest.json`, `doc/project_hygiene_manifest.json` e `doc/technique_usage_manifest.json` prontos para classificacao.
- `rascunho/` organizado para entradas brutas, processados e temporarios locais.

## Como usar

1. Copie `tools/sgdk_wrapper/modelo` para `SGDK_projects/<nome-do-projeto>`.
2. Renomeie o diretorio conforme o documento do workspace `doc/PADRAO_NOMENCLATURA.md`; `new_project.bat`/`.sh` rejeitam nomes novos fora do padrao.
3. Classifique `doc/project_methodology_manifest.json`, valide a higiene local e declare as tecnicas usadas em `doc/technique_usage_manifest.json`.
4. Rode `adopt_project_methodology.ps1` e `validate_project_methodology.ps1`.
5. Coloque assets brutos em `res/data/`.
6. Declare os recursos finais em `res/resources.res` quando houver assets reais.
7. Edite `src/` e `inc/`.
8. Rode `build.bat`.

## Regra de ouro

`res/data/` e a origem dos brutos.

`res/` e a saida final consumida pelo SGDK.

`res/data/backup/` guarda o estado anterior sempre que o wrapper precisa corrigir ou sobrescrever um arquivo.
