# Player Logic Flow - KOF94 HAMOOPIG MINIMALIST

This document maps the game design and player logic for the KOF94 variant of the HAMOOPIG engine, focusing on "Snk-style" fighting mechanics.

## 1. Modular State Machine (FSM)

Unlike earlier HAMOOPIG versions, the FSM here is categorized to handle complex fighting game interactions more efficiently:
*   **Neutral State (100)**: Standard idle.
*   **Normal Attacks**: Handled by `FUNCAO_FSM_NORMAL_ATTACKS`. Focuses on standard punches and kicks (LP, MP, HP, LK, MK, HK).
*   **Special Attacks**: Handled by `FUNCAO_FSM_SPECIAL_ATTACKS`. Includes KOF-style specials like "Ko-Ou Ken" (Fireball).
*   **Defense System**: Handled by `FUNCAO_FSM_DEFENSE`. Features a `guardFlag` system (0: No guard, 1: High/Low, 2: Low-only, 3: High-only).

## 2. Competitive Features

*   **Frame Data tracking**: The engine calculates `frameAdvCounterP1/P2`, allowing developers to tune the "tightness" of combos and punishes.
*   **Slow-Motion KO**: Upon a round-ending hit, the engine triggers `gPauseKoTimer`, creating a dramatic slowdown effect.
*   **Double Hit Detection**: Uses `doubleHitStep` to prevent multiple damage registers from the same active hit-frame unless specified.

## 3. Advanced Movement

*   **Short Jumps**: Implements `shotJump` logic, a staple of KOF gameplay, allowing for faster overhead pressure.
*   **Command Buffering**: The engine uses `bufferSpecial` to store complex motion inputs (like Quarter-Circle Forward) while the player is in hit-pause or a prior animation.

## 4. Visual Feedback (HUD)

The HUD is synchronized with the `energiaBase` and `energiaSP` (Special/Super) variables, providing real-time feedback on the health and tactical resources of both players.
