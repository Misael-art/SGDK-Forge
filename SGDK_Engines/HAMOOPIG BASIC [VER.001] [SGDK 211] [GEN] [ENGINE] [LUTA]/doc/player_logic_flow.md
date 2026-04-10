# Player Logic Flow - HAMOOPIG (Ver. 001)

This version of HAMOOPIG is a minimalist prototype designed to demonstrate the core loop of a fighting game: character state initialization and manual animation synchronization.

## 1. Character State Machine (FSM)

The engine handles transitions through a centralized `PLAYER_STATE` function. In this minimalist version, only the Idle state (100) is fully implemented for Haohmaru.

### ASCII State Flow

```ascii
       [ INICIALIZACAO ]
               |
               v
       [ STATE: 100 (IDLE) ] <----------+
               |                        |
               +---> [ FRAME 1 ] --(8)-->+
               |                        |
               +---> [ FRAME 2 ] --(7)-->+
               |                        |
               +---> [ FRAME 3 ] --(7)-->+
               |                        |
               +---> [ LOOPING ] -------+
```

## 2. Animation Timing

Unlike SGDK's automatic animations, HAMOOPIG uses a manual `dataAnim` system:
*   **Duration Control**: Each frame has a specific duration (in frames) stored in `P[i].dataAnim`.
*   **Update Loop**: `FUNCAO_ANIMACAO` increments a counter (`frameTimeAtual`). When it reaches `frameTimeTotal`, it advances to the next `animFrame`.
*   **Synchronization**: This allows the developer to precisely time hitbox activation or sound triggers with specific sprite frames in future versions.

## 3. Visual Feedback Logic

The engine uses a `ping2` toggle variable (0 or 1) to create dynamic visual effects without extra sprites:
*   **Palette Pulsing**: Alternates the player's palette between two variations every frame, creating a glowing effect on the character's weapon/clothes.
*   **Shadow Flickering**: Toggles the visibility of the shadow sprite (`P[i].sombra`). This simulates the semi-transparent flickering shadows common in Neo Geo fighters.

## 4. Initialization & Depth

*   **Pivots (Axis)**: Characters are positioned using an `axisX/axisY` offset, ensuring the sprite's "feet" always touch the ground regardless of frame width.
*   **Layering**: Depth is manually assigned to prevent sprites from overlapping incorrectly:
    1.  **Depth 1-2**: Debug points (Axis).
    2.  **Depth 5-6**: Players.
    3.  **Depth 9-10**: Shadows.
