# Player Logic Flow - Sonic SMS Prototype [VER.001] [SGDK 211] [SMS] [ESTUDO] [PLATAFORMA]

This document describes the player control flow and state management for the Sonic SMS Prototype [VER.001] [SGDK 211] [SMS] [ESTUDO] [PLATAFORMA].

## 1. Character State Machine
The project manages player states through a central loop, typically using a switch-case structure or a sequence of update functions.

### Logic Flow

```ascii
    [ START ] --> [ INIT ]
                     |
              [ STATE MACHINE ]
                     |
       [ GAME LOOP ]
                     |
    [ INPUT ] --(Update)--> [ PHYSICS ]
```

## 2. Input Handling
Input is captured via SGDK's `JOY_read` or `JOY_setEventHandler`. 
The project uses active input handlers: joyEvent

## 3. Interaction & Physics
- **Physics**: Updates player position based on velocity and gravity.
- **Collisions**: Checks against tiles or other sprites to prevent overlapping.
- **Animations**: Uses `SPR_setAnim` to reflect the current logical state visually.
