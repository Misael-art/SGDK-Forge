# SimpleGameStates - [ELITE LOGIC TEMPLATE]

Template focado em Maquina de Estados Finitos (FSM) modular.

## Estrutura
- `src/rooms/`: Adicione novos arquivos `.c` para cada tela do jogo.
- `src/modulos/`: Contém o `fsm_system.c`.

## Como usar
1. Defina o protótipo da função em `game_states.h`.
2. Implemente a função em um novo arquivo em `rooms/`.
3. Use `set_state(sua_funcao)` para transitar.
