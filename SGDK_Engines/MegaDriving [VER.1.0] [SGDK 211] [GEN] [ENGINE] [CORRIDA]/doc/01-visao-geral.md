# Visao Geral

`MegaDriving [VER.1.0] [SGDK 211] [GEN] [ENGINE] [CORRIDA]` e uma colecao
pedagogica de estudos sobre corrida pseudo-3D. O objetivo desta organizacao e
permitir que iniciantes naveguem por pequenos experimentos isolados em vez de
encarar uma arvore upstream heterogenea sem contexto.

## Como pensar na estrutura

- A raiz atual e a camada humana da colecao.
- `variants/` oferece uma entrada estavel e padronizada para cada experimento.
- `upstream/` preserva o conteudo historico original, incluindo assets e notas.
- O wrapper central entende cada variante via `.mddev/project.json`.

## Resultado pratico

Voce pode estudar a progressao de tecnicas em passos pequenos:

- curvas simples
- colinas
- pista colorida
- sprites na estrada
- steering
- abordagens alternativas como Spacer e Streeter
