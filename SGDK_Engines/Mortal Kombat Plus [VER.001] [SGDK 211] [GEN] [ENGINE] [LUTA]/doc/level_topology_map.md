# Level Topology Map - Mortal Kombat Plus

This document maps the spatial and state-based progression of the Mortal Kombat Plus engine.

## 1. Spatial & State Topology (ASCII)

The game flows through a sequence of rooms managed by the `gRoom` variable.

```ascii
[ INTRO DEMO ] --(Start/Timer)--> [ TITLE SCREEN ]
       |                                |
       |                                v
       |                        [ MAIN MENU / OPTIONS ]
       |                                |
       +--------------------------------+
                                |
                                v
                   [ CHARACTER SELECTION GRID ]
                                |
             +------------------+------------------+
             |                                     |
             v                                     v
    [ STAGE: PALACE GATES ] <-----------> [ STAGE: BONUS (TYM) ]
    (Spawn P1: x24, y96)                  (Spawn P1: x24, y56)
    (Spawn P2: x168, y96)                 (Spawn P2: x176, y56)
             |                                     |
             +------------------+------------------+
                                |
                                v
                         [ GAME LOOP RESET ]
```

### Legend of POIs (Points of Interest)
- **Spawn P1/P2**: Initial positions defined in `palace_gates_room.c` and `bonus_stage_room.c`.
- **Boss**: Goro (Managed as bio in `intro_demo_room.c`).
- **Secret Route**: Bonus stage triggered via `gRoom = BONUS_STAGE`.

## 2. Technical Translation Table

| Topology Node | File / Logical Variable | Code Reference (Execution) |
| :--- | :--- | :--- |
| **Intro Demo** | `intro_demo_room.c` | `gRoom = TELA_DEMO_INTRO` |
| **Title Screen** | `press_start_room.c` | `gRoom = TELA_START` |
| **Character Select**| `char_select_room.c` | `gRoom = SELECAO_PERSONAGENS` |
| **Palace Gates** | `palace_gates_room.c` | `gRoom = PALACE_GATES` |
| **Bonus Stage** | `bonus_stage_room.c` | `gRoom = BONUS_STAGE` |
| **Language Select** | `GameLanguage language` | `language = BR; / language = EN;` |
| **Stage Dimensions**| `gBG_Width / gBG_Height`| `PALACE_GATES_W / PALACE_GATES_H` |
