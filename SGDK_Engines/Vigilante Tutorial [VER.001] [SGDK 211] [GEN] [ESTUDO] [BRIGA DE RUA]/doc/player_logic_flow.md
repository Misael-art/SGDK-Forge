# Player Logic Flow - Vigilante Tutorial

This document maps the game design and player logic for the Vigilante Tutorial project, a comprehensive study of Beat 'em up mechanics on the Mega Drive.

## 1. Character State Machine (FSM)

The engine uses a highly granular State Machine to handle complex interactions between movement, combat, and weapon status.

### ASCII Flowchart

```ascii
       [ IDLE ] <-------------------------------------------+
          |                                                 |
          +---( D-Pad )-----> [ WALK ] ---------------------+
          |                                                 |
          +---( Down )------> [ CROUCH ] -------------------+
          |                                                 |
          +---( Button C )--> [ JUMP (Apply Gravity) ]      |
          |                        |                        |
          |           +------------+------------+           |
          |           v                         v           |
          |     [ JUMP KICK ]             [ JUMP PUNCH ]    |
          |           |                         |           |
          |           +------------+------------+           |
          |                        |                        |
          |                        v                        |
          +------------------ [ LANDING ] ------------------+
          |
    +-----+-----+
    |  COMBAT   |
    +-----------+
          |
          +---( Button B )--> [ PUNCH / NUNCHUCK ATK ]
          |
          +---( Button A )--> [ KICK ]
```

## 2. Weapon Handling (Nunchuck)

A unique feature of this engine is the procedural weapon system:
*   **Armed State**: If `player.armed == TRUE`, the engine tracks the `sprite_NUNCHUK`.
*   **Synchronized Positioning**: During attacks, the Nunchuck sprite is repositioned frame-by-frame (`SPR_setPosition`) relative to the player's hand to ensure alignment.
*   **Toggle Logic**: Grabbing a weapon changes the entire animation set used by the Punch/Crouch actions.

## 3. Input Model (Event-Based)

The tutorial utilizes `JOY_setEventHandler` for context-sensitive inputs:
*   **`logo_Callback`**: Standard Skip logic.
*   **`player_Callback`**: The core fighting logic handler. This decouples the "How to read" (main loop) from the "What to do" (callback logic).

## 4. Collision & Boundaries

*   **Axis Alignment**: Collisions are checked only when `LIST_ENEMIES[i].pos_Y == player.pos_Y`.
*   **Range-Based Detection**: Uses `ENEMY_LEFT_BOUND` and `ENEMY_RIGHT_BOUND` to create a virtual attack zone in front of the player based on their current `axis` (Direction).
*   **Camera Lock**: The player can only move 1px per frame when at the camera limit, and enemies are pushed/pulled along with the scrolling planes.
