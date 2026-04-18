# Player Logic Flow - BLAZE_ENGINE (Beat 'em Up)

This document maps the player-facing logic and state machine for the BLAZE_ENGINE, specifically detailing how inputs translate into actions, combos, and interactions.

## 1. Fighter State Machine (FSM)

The fighter's behavior is driven by a State Machine where each numerical ID represents a specific posture or action.

### ASCII State Transition Flowchart

```ascii
       [ IDLE (100) ] <---------------------------+
             |                                     |
             +---( D-Pad )-----> [ WALKING (420) ]--+
             |                                     |
             +---( 2x D-Pad )--> [ RUNNING (430) ]--+
             |                                     |
             +---( Button C )--> [ JUMPING (300/320) ]
             |                        |
             |           +------------+------------+
             |           v                         v
             |     [ AIR ATK (301) ]       [ AIR DASH ATK (322) ]
             |           |                         |
             |           +------------+------------+
             |                        |
             |                        v
             +------------------ [ LANDING (606) ]
             |
    +--------+--------+
    | COMBAT SEQUENCE |
    +-----------------+
    |                 |
    +---> [ ATK 1 (101) ] --(Hit + Button B)--> [ ATK 2 (102/202) ]
                                                        |
                                                        v
                                                [ ATK 3 (103/203) ]
                                                        |
                                                        v
                                                [ FINISHER (104/204) ]
                                                        |
                                                 [ SPECIAL (199) ]
                                              (Uses Energy/Invinc)

    +-----------------+
    | DAMAGE REACTION |
    +-----------------+
    |
    +---> [ RECOIL (501) ] ----> [ RECOVER (100) ]
    |
    +---> [ KNOCKDOWN (550) ] -> [ ON GROUND (570) ] -> [ GET UP (606) ]
    |
    +---> [ SPECIAL DEATHS ] --> [ BURN (506) / ELEC (505) / MELT (509) ]
```

## 2. Combat Rules & Combo Mechanics

### Attack Alignment (Y-Axis Margin)
To prevent "ghost hits", the engine only checks for horizontal collisions if the Player and Enemy are on the same depth plane within a specific margin:
*   **Condition**: `|Player.y - Enemy.y| <= ATTACK_MARGIN`

### Chain Combo System
The engine uses a "Chain Sequence" flag to allow transitioning between attack states.
*   **Windowing**: You must hit the enemy (`activeHit == 1`) and press Button B during specific frames (usually frame 3 or later) of the current attack animation.
*   **Directional Variation**: Holding D-Pad towards the enemy during a combo can trigger alternate animations (e.g., State 102 vs 202).

### Finisher Logic
The final hit of a combo (Finisher) typically triggers a **Knockdown** state (550) in the enemy, pushing them back and forcing them to ground.

## 3. Interaction Table (Inputs to States)

| Input | Current State | New State | Action Description |
| :--- | :--- | :--- | :--- |
| **D-Pad** | IDLE | 420 | Basic Movement |
| **2x D-Pad** | IDLE / WALK | 430 | Sprint/Running |
| **Button B** | IDLE / WALK | 101 | Basic Attack 1 |
| **Button B** | ATK 1 (Hit) | 102 | Combo Attack 2 |
| **Button C** | GROUNDED | 300 | Neutral Jump |
| **Button C** | RUNNING | 320 | Long Jump |
| **Button B** | JUMPING | 301 | Air Attack |
| **Button A** | ANY (Grounded)| 199 | Special Move (Invincible) |

## 4. Reaction Logic

*   **Weak Hit**: Enemy enters state 501 (Recoil), briefly staggered.
*   **Strong Hit / Finisher**: Enemy enters state 550 (Fall), flies back and lands on state 570 (Down).
*   **Elemental Damage (Captain Commando specific)**:
    *   **Fire (P2 Dash Attack)**: Enemy burns (State 506).
    *   **Electricity (P2 Special)**: Enemy electrified (State 505).
    *   **Acid/Melt (Mummy Attacks)**: Enemy melts into pieces (State 509).
