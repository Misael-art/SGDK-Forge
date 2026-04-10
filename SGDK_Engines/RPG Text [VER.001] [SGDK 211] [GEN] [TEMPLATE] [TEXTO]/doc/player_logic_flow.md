# Player Logic Flow - RPG Text [VER.001] [SGDK 211] [GEN] [TEMPLATE] [TEXTO]

This document describes the player control flow and state management for the RPG Text [VER.001] [SGDK 211] [GEN] [TEMPLATE] [TEXTO].

## 1. Character State Machine
The project manages player states through a central loop, typically using a switch-case structure or a sequence of update functions.

### Logic Flow

```ascii
    [ START ] --> [ INIT ]
                     |
              [ STATE MACHINE ]
                     |
       14 -> 10 -> 4 -> 3 -> 15
                     |
    [ INPUT ] --(Update)--> [ PHYSICS ]
```

## 2. Input Handling
Input is captured via SGDK's `JOY_read` or `JOY_setEventHandler`. 
The project typically reads input within the main game loop.

## 3. Interaction & Physics
- **Physics**: Updates player position based on velocity and gravity.
- **Collisions**: Checks against tiles or other sprites to prevent overlapping.
- **Animations**: Uses `SPR_setAnim` to reflect the current logical state visually.
