# HAMOOPIG [VER.1.0] - Player Logic Flow

This document maps the player experience to the underlying system rules, focusing on the character state machine, input handling, and combat mechanics.

## Fighter State Machine (FSM)

The core logic of the fighters is governed by a Finite State Machine where inputs and game conditions trigger transitions between states.

### Core FSM ASCII Flowchart

```text
       [ START ]
           |
           v
    +--------------+      (Up / Diag-Up)       +--------------+
    |   STANDING   | ------------------------> |   JUMPING    |
    |   (IDLE 100) | <------------------------ |  (300-320)   |
    +-------+------+       (Land/Y>=Floor)     +-------+------+
        ^   |                                          |
        |   | (Down)                                   | (A/B/C/X/Y/Z)
 (Up)   |   v                                          |
    +-------+------+      (Attack In Range)    +-------+------+
    |  CROUCHING   | <------------------------ | AIR ATTACK   |
    |   (IDLE 200) | ------------------------> |  (301-326)   |
    +-------+------+      (Back Hold)          +--------------+
        |   |
        |   | (A/B/C/X/Y/Z)
        |   v
        | +----------------+      (Hit)        +--------------+
        | | NORMAL ATTACK  | ----------------> | HURT / REEL  |
        | | (101-210)      | <---------------- |  (501-570)   |
        | +----------------+    (End Anim)     +-------+------+
        |                                              |
        | (Motion + P/K)                               | (Life=0)
        v                                              v
    +----------------+                         +--------------+
    | SPECIAL MOVE   |                         |  KNOCKDOWN   |
    | (700-790)      |                         |    (DEATH)   |
    +----------------+                         +--------------+
```

### State Definitions

| State Range | Description | Notes |
|:---:|:---|:---|
| **100** | Standing Idle | Main neutral state. Can walk, jump, crouch, or attack. |
| **200** | Crouching Idle | Neutral crouching. Lowers hitbox, allows low attacks. |
| **101-156** | Standing Attacks | **Close/Far** variations triggered by `gDistancia`. (Punches/Kicks). |
| **201-206** | Crouching Attacks | LP, MP, HP, LK, MK, HK while crouching. |
| **301-326** | Aerial Attacks | Vary based on jump direction (Vertical, Forward, Backward). |
| **410-420** | Walk Forward/Back | Speed varies by character. |
| **471-472** | Dash / Dodge | Triggered by double-tap (`key_JOY_countdown`). |
| **107-110** | Standing Defense | Triggered when holding Back while an attack is active. |
| **207-210** | Crouching Defense | Triggered when holding Down-Back while an attack is active. |
| **501-570** | Hurt States | Includes light/medium/heavy hit reels and blowbacks (`PLAYER_STATE(PR,550)`). |
| **618** | Rage Explosion | Triggered when `energiaSP >= 32`. |
| **700-790** | Special Moves | Defined per character (Fireballs, Uppercuts, etc.). |

---

## Combo & Special Move List

The input system buffers directions into `inputArray` [Buffer size: 5] to detect motion patterns.

### Haohmaru (ID 1)

| Move Name | Motion (NumPad) | Button | State | Description |
|:---|:---:|:---:|:---:|:---|
| **Ougi Kogetsu Zan** | `6, 2, 4` | P | 700 | Secret Skill Arc Moon Slash (DP-like). |
| **Ougi Senpuu Retsu Zan**| `2, 3, 6` | P | 710 | Whirlwind Rending Slash (Fireball). |
| **Ougi Resshin Zan** | `6, 2, 4` | K | 720 | Violent Quake Slash. |
| **Sake Kougeki** | `2, 1, 4` | LP | 730 | Sake Attack (Deflects projectiles). |

### Gillius (ID 2)

| Move Name | Motion (NumPad) | Button | State | Description |
|:---|:---:|:---:|:---:|:---|
| **Rock Throw** | `2, 3, 6` | P | 700 | Throws a projectile (Fireball). |
| **Axe Spin** | `2, 1, 4` | P | 710 | Multi-hit axe spinning attack. |
| **Shoulder Ram** | `2, 3, 6` | K | 720 | Forward dash with shoulder strike. |

---

## Combat Mechanics & Rules

### 1. Rage System (SP)
- **Charge**: Players gain SP energy (`energiaSP`) when taking damage.
- **Max Rage**: When `energiaSP` reaches **32**, the character enters a Rage state.
- **Rage Explosion**: A forced state (618) occurs, increasing damage and enabling specific visual effects.
- **Countdown**: A `rageTimerCountdown` starts, eventually resetting SP to 0.

### 2. Hitboxes & Hurtboxes
- **Hurtbox (BBox)**: Defines the area where the character can be hit (e.g., `P[Player].dataBBox`).
- **Hitbox (HBox)**: Defensive area of an attack (e.g., `P[Player].dataHBox`).
- **Collision**: Calculated in `FUNCAO_FSM` using `FUNCAO_COLISAO`.
- **Hit-Pause**: A freeze effect (`hitPause`) is applied upon impact to emphasize the weight of the blow.

### 3. Guard (Defense)
- **Automatic Trigger**: If a player holds **Back** (relative to the opponent) while an attack is in range, the state changes to **107/207**.
- **Guard Crush**: Not present in VER.1.0, but hit-pause applies to the defender.
- **Projectile Guard**: Projectiles (`fBall`) can be guarded if the player holds the correct direction before impact.

### 4. Distance-Based Attacks
- The engine checks `gDistancia`.
- **> 64 pixels**: Triggers "Far" attacks (State 101-106).
- **<= 64 pixels**: Triggers "Close" attacks (State 151-156).
