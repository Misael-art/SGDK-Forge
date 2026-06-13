# Referencia de Arte Conceito — MegaDrive_DEV

Este documento registra onde a arte conceito e as referencias visuais sao armazenadas nos projetos do workspace, para uso por agentes de IA, artistas e pipelines de validacao.

## Projeto Pequeno Principe: Cronicas das Estrelas

- **Concept art (biblia visual):**  
  `SGDK_projects/Pequeno Principe Cronicas das Estrelas [VER.001] [SGDK 211] [GEN] [GAME] [AVENTURA]/doc/Concept art.jpg`  
  Define paleta, contornos, ornamentacao, escala e mapeamento asset → elemento.

- **Documentacao da direcao artistica:**  
  `SGDK_projects/.../doc/08-bible-artistica.md`

- **Boards de referencia (cenas promovidas):**  
  `SGDK_projects/.../res/gfx/boards/`  
  (board_title_scene.png, board_b612.png, board_king.png, board_lamp.png, board_desert.png, board_travel.png)  
  Servem como documentacao e guia para conversao em tilemap.

- **Prompt canônico para agente de arte:**  
  `tmp/imagegen/PROMPT_AGENTE_ASSETS_PEQUENO_PRINCIPE.md`

## Convencao

Para novos projetos que usem lote de arte com validacao:

1. Manter arte conceito em `doc/` do projeto (ex.: `doc/Concept art.jpg`).
2. Referenciar no `08-bible-artistica.md` ou equivalente como referencia canonica.
3. Boards e referencias promovidas podem ficar em `res/gfx/boards/` ou em `doc/art/` conforme o pipeline do projeto.
