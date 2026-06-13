# SimpleGameStates [VER.1.0] [SGDK 211] [GEN] [TEMPLATE] [LOGICA]

Template de arquitetura para organização de lógica de jogo usando Máquinas de Estado Finitas (FSM).

## Diferenciais Técnicos
- **Ponteiros de Função**: Evita o uso excessivo de `switch/case` aninhados, tornando o código modular.
- **Ciclo de Vida Claro**: Estados com funções dedicadas de `init`, `update` e `exit`.
- **Escalabilidade**: Fácil adição de novos estados (Menu, Intro, Game, GameOver) sem poluir o `main.c`.

## Como Explorar
1. Veja `src/main.c` para o loop principal minimalista.
2. Observe como os estados são trocados alterando o ponteiro da função de atualização.

---
*Baseado nos padrões pedagógicos do OHSAT Games.*
