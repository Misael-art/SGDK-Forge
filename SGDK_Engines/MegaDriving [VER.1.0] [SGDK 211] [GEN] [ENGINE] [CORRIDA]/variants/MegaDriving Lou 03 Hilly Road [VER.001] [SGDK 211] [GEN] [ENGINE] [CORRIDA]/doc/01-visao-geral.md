# Visao Geral

`MegaDriving Lou 03 Hilly Road [VER.001] [SGDK 211] [GEN] [ENGINE] [CORRIDA]` segue o worktree canônico do MegaDrive_DEV.
Isso significa que o projeto foi organizado para ser facil de entender,
facil de migrar e seguro para evoluir sem duplicar logica de build.

## Como pensar neste projeto

- A raiz do projeto e o ponto de entrada humano: `README.md`, `doc/` e scripts `.bat`
- O SGDK root e o ponto de entrada tecnico: `../../upstream/lou/03_hilly_road/src/`, `../../upstream/lou/03_hilly_road/res/`, `../../upstream/lou/03_hilly_road/inc/` e `../../upstream/lou/03_hilly_road/out/`
- O wrapper central em `tools/sgdk_wrapper/` faz o trabalho operacional pesado
- O manifesto `.mddev/project.json` diz ao wrapper onde esta o SGDK root real

## O que um iniciante deve fazer primeiro

1. Ler o `README.md`
2. Abrir `../../upstream/lou/03_hilly_road/src/main.c`
3. Ler `doc/02-build-wrapper.md`
4. Fazer um build com `build.bat`
5. Rodar com `run.bat`

## O que um mantenedor deve observar

- Se a estrutura do projeto mudar, atualize `.mddev/project.json`
- Se houver um problema generico de build, corrija o wrapper central
- Se houver uma decisao arquitetural importante, documente nesta pasta
