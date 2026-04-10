# Engine Architecture Nodes - Mega Pong Classic [VER.001] [SGDK 211] [GEN] [GAME] [ARCADE]

Overview of the technical structure of the Mega Pong Classic [VER.001] [SGDK 211] [GEN] [GAME] [ARCADE] engine.

## 1. Modular Structure
The engine is composed of the following core modules:
- **`main.c`**: Entry point and primary game loop.


## 2. Key Technical Nodes
### Game Loop
The heart of the engine is a `while(1)` loop in `main.c` that synchronizes with the VBlank.

### Core Systems
- **VDP Management**: Handles plane scrolling and tile loading.
- **Sprite Engine**: Enabled and active for entity management.
- **Resource Management**: Loads tilesets and palettes from `res/`.

## 3. Data Flow
```mermaid
graph TD
    Main[main.c] --> Init[Initialization]
    Main --> Loop[Game Loop]
    Loop --> Input[Input Management]
    Loop --> Logic[Game Logic]
    Loop --> Graphics[VDP/Sprite Update]
```

## 4. Primary Functions
Some of the key identified functions in this engine include:
sign, launchBall, updateScoreDisplay, while, moveBall, positionPlayer, endGame, if, showText, main
