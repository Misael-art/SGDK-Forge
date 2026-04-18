# Player Logic Flow - HAMOOPIG (Ver. 1.0)

This document maps the game design and player logic for HAMOOPIG Ver. 1.0, a complete fighting game engine for the Sega Mega Drive.

## 1. Global Lifecycle & Room System

The engine uses a "Room" architecture to manage the transition between game states. Each room has its own logic and input processing.

*   **Room 1 (Company)**: Displays the developer logo and plays digitized speech.
*   **Room 2 (Title Intro)**: A complex cinematic with procedural flower petals that follow wind patterns (`PetalaPX/PetalaPY`).
*   **Room 3 (Selection)**: A dual-cursor character selection system with "Lock-in" FX and dynamic character portraits.
*   **Room 9 (Descompression)**: A technical state to clear VRAM and prepare the VDP for combat.
*   **Room 10 (Combat)**: The core fighting engine.

## 2. Combat State Machine (FSM)

The engine handles hundreds of states, categorized by ID ranges:
*   **100-199**: Standing Actions (Idle, Basic Attacks, Block).
*   **200-299**: Crouching Actions.
*   **300-399**: Jumping Actions / Air Attacks.
*   **600+**: Special states (Turn around, Getting Hit, Intro, Win Pose).

### Interaction Flow

```ascii
       [ JUMPING ] <---( Up )--- [ IDLE ] ---( Down )---> [ CROUCHING ]
            |                      |                         |
       [ AIR ATK ] <---( Btn )--   +---( Btn )---> [ GROUND ATK (Weak/Strong) ]
            |                      |                         |
       [ LANDED ]  <------------ [ PINNED ] <--( Hit )-- [ DAMAGE REACTION ]
```

## 3. Advanced Mechanics

*   **Rage System**: Inspired by Samurai Shodown, characters have a `rageLvl`. Taking damage increases this bar, triggering a "Furious" state that enhances attack power and palette effects for a duration (`RAGETIMER`).
*   **Input Buffering**: Special moves are detected by scanning a history of inputs (`inputArray`) against a timer (`gInputTimerCountDown`).
*   **Double Shadow System**: Depending on the `gSombraStyle`, characters can have standard or high-fidelity shadows (flickering vs. solid).

## 4. HUD & Rules

*   **Round Sequencer**: `FUNCAO_ROUND_INIT` manages the "Duel 1... Fight!" announcement sequence.
*   **Energy Management**: Two types of energy: `energia` (visual bar) and `energiaBase` (actual health), allowing for smooth bar-drain animations.
*   **Double KO Detection**: Logic to handle simultaneous defeats at the end of a frame.
