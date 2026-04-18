# Engine Architecture Nodes - Goblin SGDK [VER.001] [SGDK 211] [GEN] [GAME] [AVENTURA]

Overview of the technical structure of the Goblin SGDK [VER.001] [SGDK 211] [GEN] [GAME] [AVENTURA] engine.

## 1. Modular Structure
The engine is composed of the following core modules:
- **`main.c`**: Entry point and primary game loop.
- **`battle.c`**: Module file.
- **`camera.c`**: Module file.
- **`collision.c`**: Module file.
- **`debuginfo.c`**: Module file.
- **`dungeonGenerator.c`**: Module file.
- **`gamemanager.c`**: Module file.
- **`globals.c`**: Module file.
- **`inventory.c`**: Module file.
- **`level.c`**: Module file.
- **`makemap.c`**: Module file.
- **`player.c`**: Module file.
- **`titlescreen.c`**: Module file.

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
if, main, while
