# Arquitetura do Projeto — BENCHMARK_VISUAL_LAB [VER.001] [SGDK 211] [GEN] [TOOL] [TEST]

## Estrutura Modular (Padrao Elite)

- `src/main.c`: Switcher central de estados (Rooms).
- `src/rooms/`: Logica especifica de cada tela/fase.
- `src/modulos/`: Sistemas globais (Input, Colisao, Animacao).
- `src/entities/`: Fabrica de entidades (Players, Inimigos).
- `src/game_vars.c`: Definicao de variaveis globais e globais compartilhadas.

## Fluxo de Dados

```
Input -> FSM (Main) -> Room Update -> Entity Logic -> Sound/GFX Updates
```

## Gestao de VRAM e Paletas

- Palette 0: Background Layer A
- Palette 1: Background Layer B
- Palette 2: Personagens e Objetos
- Palette 3: UI / Efeitos Especiais

