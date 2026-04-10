# Player Logic Flow - Jogo de Nave (SHMUP Engine)

This document maps the game design and player logic for `Jogo de Nave`, a high-performance Shoot 'em Up engine for the Sega Mega Drive.

## 1. Ship State Machine & Stability

The engine features a dynamic ship movement system that prioritizes "feel" through procedural tilting.

### Tilting Mechanism
*   **Neutral**: Frame 4 (Stabilized horizontal).
*   **Climbing (UP)**: As the player holds UP, `ctrlTimer` increases. The ship tilts upward through frames 3 and 2.
*   **Diving (DOWN)**: Holding DOWN decreases `ctrlTimer`. The ship tilts downward through frames 5 and 6.
*   **Auto-Stabilization**: When no vertical input is detected, `ctrlTimer` gradually returns to 0, resetting the ship to the neutral frame.

## 2. Combat & Weaponry

### Standard Disparate
*   **Red Bullets (Linear)**: High-speed, straight-firing projectiles. Power levels (1-3) add more parallel bullets.
*   **Blue Bullets (Spread)**: Multi-directional firing patterns based on the numeric keypad directions (e.g., dir 9, 6, 3). Higher levels increase the spread coverage.

### Advanced Mechanics
*   **Charge Shot (Super Bar)**: Holding the fire button (Button A) fills the `super_bar`. Reaching 100% allows the player to release a massive `BULLET_SUPER` projectile.
*   **Screen Bombs**: Button C triggers a screen-clearing explosion (`BombDEF`). Limited quantity managed by `bomb_cont`.
*   **Auto-Fire**: Button B provides a standard 10Hz auto-fire loop for comfort.

## 3. Progression & Power-ups

The engine manages item drops through `Item_Box`.
*   **Speed Up**: Increases `velocidadeDaNave`.
*   **Extra Life**: Increments `lives`.
*   **Weapon Swap**: Toggles between Red and Blue weapon types and increments their respective levels.

## 4. Game Cycle (Room System)

```ascii
[ ROOM 1: Logo/Menu ] -> [ Start Pressed ] -> [ ROOM 2: In-Game ]
                                                    |
                                             [ Game Over / P1 Lives == 0 ]
                                                    |
                                             [ Return to Menu ]
```
