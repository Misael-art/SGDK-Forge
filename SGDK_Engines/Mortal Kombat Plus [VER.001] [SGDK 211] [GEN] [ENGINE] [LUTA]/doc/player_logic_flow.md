# Player Logic Flow - Mortal Kombat Plus

This document maps the player experience and the structural state machine for the Mortal Kombat Plus engine. This engine is designed with modularity in mind, separating character logic from the core sequencer.

## 1. Character State Machine (Conceptual)

The engine follows the classic 1v1 Fighting Game structure. Transitions are handled by character-specific modules (e.g., `subzero.c`, `scorpion.c`).

### ASCII Logic Flow

```ascii
       [ SCREEN: INTRO ] --(Start)--> [ SCREEN: SELECT ]
                                             |
                                     [ SELECT CHARACTER ]
                                             |
                                     (Load Fighter Module)
                                             |
                                     [ SCREEN: FIGHT ]
                                             |
       +-------------------------------------+-------------------------------------+
       |                                     |                                     |
    [ P1 FSM ]                        [ SEQUENCER ]                         [ P2 FSM ]
       |                                     |                                     |
    [ IDLE ] <----------+             [ anima_system ]              [ IDLE ] <----------+
       |                |                    |                         |                |
    [ WALK ] --(Input)--+             (Frame Pacing)                [ WALK ] --(Input)--+
       |                                     |                         |
    [ ATK  ] --(Collision)--> [ HIT ]        |         [ HIT ] <--(Collision)-- [ ATK  ]
```

## 2. Character-Specific Modules

Unlike monolithic systems, each fighter in this engine has a dedicated setup:
*   **Sub-Zero**: Initialized in `playerState_SubZero`. Manages its own tile tracking and palette swapping (PAL2 for P1, PAL3 for P2).
*   **Kano / Raiden / etc.**: Follow the same initialization pattern, allowing for unique hitboxes and frame data per character.

## 3. Input & Interaction

The engine abstracts inputs through `input_system.c`, tracking four distinct states for every button:
1.  **Status 0**: Not pressed.
2.  **Status 1**: Just Pressed (Trigger).
3.  **Status 2**: Held down.
4.  **Status 3**: Just Released.

This allows for precise control over complex moves (e.g., holding a button for charging vs. tapping for a punch).

## 4. Game Loop Sequence

The game progresses through a global `gRoom` state:
*   **TELA_DEMO_INTRO**: High-fidelity intros with biographical text and digitized speech.
*   **SELECAO_PERSONAGENS**: Complex UI for character picking.
*   **PALACE_GATES**: The combat stage (in prototype/WIP state).
*   **BONUS_STAGE**: Separate logic for breaking objects (Test Your Might).
