# 03 - Arquitetura

Arquitetura inicial:

- `src/main.c`: loop principal.
- `src/core/app.c`: inicializacao e roteamento de cenas.
- `src/system/input.c`: leitura de controles.
- `src/scenes/`: comportamento de cada tela.
- `src/game_vars.c`: estado global enxuto.

Principios:
- separar infraestrutura de gameplay;
- preferir funcoes pequenas e previsiveis;
- evitar logica escondida em variaveis globais sem contexto;
- manter o primeiro build simples e observavel.
