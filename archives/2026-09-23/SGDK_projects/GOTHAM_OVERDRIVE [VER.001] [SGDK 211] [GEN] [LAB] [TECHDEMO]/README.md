# Modelo Canonico SGDK

Este diretorio e a base oficial para iniciar projetos SGDK dentro do workspace `MegaDrive_DEV`.

Proposito:
- entregar um worktree completo e copiavel;
- padronizar o uso do `sgdk_wrapper`;
- adotar `res/data/` como entrada bruta canonica para assets;
- deixar uma base pedagogica que compila antes mesmo de receber arte final.

## Como usar

1. Copie esta pasta para `SGDK_projects/<NOME_DO_PROJETO>`.
2. Renomeie o diretorio conforme o documento do workspace `doc/PADRAO_NOMENCLATURA.md` e substitua `GOTHAM_OVERDRIVE [VER.001] [SGDK 211] [GEN] [LAB] [TECHDEMO]` nos documentos e em [`.mddev/project.json`](./.mddev/project.json).
3. Classifique `doc/project_methodology_manifest.json`, mantendo `lifecycle=new`, e declare as tecnicas usadas em `doc/technique_usage_manifest.json`.
4. Rode `adopt_project_methodology.ps1` e `validate_project_methodology.ps1`; a adocao cria apenas arquivos ausentes e a validacao bloqueia nome placeholder, claim nao classificado ou skill/validacao ausente.
5. Use `planning/game-design-planning` para seedar `project_brief`, `first_playable_slice`, roadmap de cenas e `front_end_profile`.
6. Defina em `doc/11-gdd.md` a identidade de front-end e o papel formal de menu/title.
7. Declare menu/title, cenas, budgets e tecnicas em `doc/13-spec-cenas.md`.
8. Preencha `doc/14-plano-de-provas-qa.md` com a rota minima para provar visual, audio e hardware real.
9. Coloque assets brutos em `res/data/`, edite o codigo em `src/` e `inc/` e mantenha evidencias/experimentos dentro do projeto.
10. Rode `build.bat` no Windows ou `../../tools/sgdk_wrapper/build.sh "$PWD"` em shell POSIX.

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
- leitura de input com suporte 3/6 botoes;
- maquina de estados com cenas `BOOT`, `MENU` e `DEMO`;
- `DEMO` jogavel com player `fix16`, pulo, aceleracao, corrida, camera lateral e pause;
- roteamento basico de audio PSG por `src/system/audio.c`;
- deteccao PAL/NTSC em `gApp.region` e `gApp.targetFps`;
- transicao visual curta entre cenas;
- HUD textual opcional;
- comentarios e organizacao pensados para edicao.

## Arquivos importantes

- [`build.bat`](./build.bat)
- [`clean.bat`](./clean.bat)
- [`rebuild.bat`](./rebuild.bat)
- [`resolve_wrapper.bat`](./resolve_wrapper.bat)
- [`run.bat`](./run.bat)
- [`sgdk_wrapper_env.bat`](./sgdk_wrapper_env.bat)
- [`doc/02-build-wrapper.md`](./doc/02-build-wrapper.md)
- [`doc/04-recursos-e-pipeline.md`](./doc/04-recursos-e-pipeline.md)
- [`doc/14-plano-de-provas-qa.md`](./doc/14-plano-de-provas-qa.md)
- [`doc/project_methodology_manifest.json`](./doc/project_methodology_manifest.json)
- [`doc/technique_usage_manifest.json`](./doc/technique_usage_manifest.json)

## O que cada .bat faz

[`build.bat`](./build.bat)

Aciona o pipeline completo de compilacao. Ele carrega as flags locais do projeto, localiza o `tools/sgdk_wrapper`, repassa o diretorio do projeto para o wrapper central e deixa o wrapper executar preparacao de assets, validacao de recursos e build da ROM.

[`clean.bat`](./clean.bat)

Limpa os artefatos gerados pelo projeto usando a logica central do wrapper. Serve para remover objetos, ROMs, logs de build e outros arquivos temporarios antes de um teste limpo.

[`rebuild.bat`](./rebuild.bat)

Executa um ciclo completo de limpeza e nova compilacao. E o caminho recomendado quando voce quer garantir que nada residual do build anterior esta influenciando o resultado.

[`resolve_wrapper.bat`](./resolve_wrapper.bat)

Resolve o caminho canonico `..\..\tools\sgdk_wrapper` a partir da raiz do projeto e define `SGDK_WRAPPER_ROOT`. Ele existe como utilitario de apoio e referencia para scripts customizados, diagnostico e manutencao. Os wrappers principais do modelo usam a mesma delegacao direta para manter o bootstrap novo coerente com o alinhador central.

[`run.bat`](./run.bat)

Dispara a execucao da ROM no emulador configurado. O wrapper central verifica se `out/rom.bin` existe e se esta atualizado; se a ROM estiver ausente ou defasada, ele builda primeiro e so depois abre o emulador.

[`sgdk_wrapper_env.bat`](./sgdk_wrapper_env.bat)

Define o comportamento padrao do projeto antes da delegacao ao wrapper. Neste modelo ele ativa `SGDK_AUTO_PREPARE_ASSETS=1` e `SGDK_AUTO_FIX_RESOURCES=1`, fazendo com que o pipeline canonico de `res/data -> res` e a correcao tecnica de imagens entrem automaticamente no build.
