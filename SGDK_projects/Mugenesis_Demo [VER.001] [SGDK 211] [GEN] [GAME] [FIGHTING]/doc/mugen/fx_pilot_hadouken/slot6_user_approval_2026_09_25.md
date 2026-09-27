# Aprovacao humana da cor compartilhada de FX

Data: 2026-09-25

## Decisao

O usuario aprovou a escolha apresentada para a cor do slot 6, compartilhado por todas as familias de FX de Ken. A escolha aprovada e a palavra CRAM `0xE82`, cuja representacao exata na grade de autoria canonica `forge_art.vdp_color` e RGB `(34,136,238)`.

A representacao RGB foi conferida por `python3 tools/sgdk_wrapper/forge_art/vdp_color.py --convert 34,136,238`: os oraculos ResComp e macro SGDK produzem ambos a palavra `0x0E82`, com niveis `[1,4,7]`. RGB aqui e a representacao de autoria; a expansao para monitor e distinta.

## Escopo

Esta decisao fixa somente a cor compartilhada do slot 6. Ela nao aprova qualquer hash de PNG indexado, a sequencia AIR, promocao para `res/`, integracao runtime, ROM ou qualidade artistica. A aprovacao da pose-fonte continua registrada separadamente em `user_source_approval_2026_09_24.md`.
