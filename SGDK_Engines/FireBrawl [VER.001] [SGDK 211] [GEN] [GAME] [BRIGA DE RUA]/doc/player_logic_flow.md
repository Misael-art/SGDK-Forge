# Player Logic Flow - FireBrawl

This document maps the game design and player logic for FireBrawl, a project featuring projectile-based combat and physics-driven movement.

## 1. Interaction & Combat Machine

FireBrawl focuses on a "Fireball & Jump" mechanic, where positioning and projectile management are key.

### ASCII Flowchart

```ascii
       [ IDLE / MID-AIR ] <--------------------------+
             |                                       |
             +---( D-Pad )-----> [ MOVE X ] ---------+
             |                                       |
             +---( Button C )--> [ JUMP (Apply ddy) ]-+
             |                        |
             |           +------------+------------+
             |           v                         v
       [ LANDED ]  <-- [ FALLING ]           [ DOUBLE JUMP ]
             |                                     |
             +---( Button B )--> [ FIREBALL (Projectile) ]
                                          |
                                  +-------+-------+
                                  |               |
                           [ HIT ENEMY ]   [ HIT BULLET ]
                                  |               |
                         [ DAMAGE / OOF ]  [ NULLIFIED ]
```

## 2. Movement Mechanics

*   **Momentum-Based**: Unlike static grid movement, characters have `dx` (velocity) and `ddx` (acceleration). Releasing the D-Pad allows for a slight slide effect.
*   **Verticality**: Characters can perform up to two jumps (Double Jump). Jumping creates a puff of particles (`add_particles`).
*   **Directional Fire**: Holding Up or Down while pressing Button B changes the vertical trajectory (`dy`) of the fireball.

## 3. Enemy AI Behavior

The AI in FireBrawl is predictive rather than reactive:
*   **Defense Mode**: If it detects an incoming fireball that *will* collide, it attempts to jump over it or fire a counter-projectile to nullify it.
*   **Attack Mode**: Automatically calculates the player's Y position to fire straight, upward, or downward fireballs.
*   **State Switching**: Randomly alternates between Attacking and Defending to keep the player off-balance.

## 4. Health & HUD

*   **Notch System**: Health is represented by physical sprites ("Notches") above the characters.
*   **Circular Collision**: Hits are detected based on distance from the center of the entity. If a projectile gets too close, a "Spark" particle effect is triggered and a health notch is removed.
