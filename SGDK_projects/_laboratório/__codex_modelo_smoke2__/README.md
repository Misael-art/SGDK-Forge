# Modelo Canonico SGDK

Este diretorio e a base oficial para iniciar projetos SGDK dentro do workspace `MegaDrive_DEV`.

Proposito:
- entregar um worktree completo e copiavel;
- padronizar o uso do `sgdk_wrapper`;
- adotar `res/data/` como entrada bruta canonica para assets;
- deixar uma base pedagogica que compila antes mesmo de receber arte final.

## Como usar

1. Copie esta pasta para `SGDK_projects/<NOME_DO_PROJETO>`.
2. Ajuste o nome do projeto em [`.mddev/project.json`](F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/modelo/.mddev/project.json).
3. Coloque assets brutos em `res/data/`.
4. Edite o codigo em `src/` e `inc/`.
5. Rode `build.bat`.

Os wrappers locais ja tentam localizar `tools/sgdk_wrapper` tanto aqui dentro do diretorio `modelo` quanto depois que a pasta for copiada para `SGDK_projects/`.

## Estrutura recomendada

- `src/`: codigo C dividido por responsabilidade.
- `inc/`: headers publicos do projeto.
- `res/`: saida final pronta para o SGDK.
- `res/data/`: entrada bruta canonica dos assets.
- `res/data/backup/`: backup automatico antes de correcao ou sobrescrita.
- `doc/`: memoria arquitetural e diretrizes.
- `out/`: artefatos de build e logs.
- `.mddev/`: manifesto do projeto.

## O que ja compila

Esta base sobe uma ROM simples com:
- bootstrap do aplicativo;
- leitura de input;
- maquina de estados com cenas `BOOT`, `MENU` e `DEMO`;
- HUD textual opcional;
- comentarios e organizacao pensados para edicao.

## Arquivos importantes

- [`build.bat`](F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/modelo/build.bat)
- [`sgdk_wrapper_env.bat`](F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/modelo/sgdk_wrapper_env.bat)
- [`doc/02-build-wrapper.md`](F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/modelo/doc/02-build-wrapper.md)
- [`doc/04-recursos-e-pipeline.md`](F:/Projects/MegaDrive_DEV/tools/sgdk_wrapper/modelo/doc/04-recursos-e-pipeline.md)
