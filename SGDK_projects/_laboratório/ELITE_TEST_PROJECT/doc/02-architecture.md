# Arquitetura do Projeto - __PROJECT_NAME__

## Estrutura Modular (Padrão Elite)

- `src/main.c`: Switcher central de estados (Rooms).
- `src/rooms/`: Lógica específica de cada tela/fase.
- `src/modulos/`: Sistemas globais (Input, Colisão, Animação).
- `src/entities/`: Fábrica de entidades (Players, Inimigos).
- `src/game_vars.c`: Definição de variáveis globais e globais compartilhadas.

## Fluxo de Dados
[ Mermaid Diagram placeholder ]
`Input -> FSM (Main) -> Room Update -> Entity Logic -> Sound/GFX Updates`

## Gestão de VRAM e Paletas
- Palette 0: Background Layer A
- Palette 1: Background Layer B
- Palette 2: Personagens e Objetos
- Palette 3: UI / Efeitos Especiais
