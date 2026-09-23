#ifndef ENTITIES_ENEMY_H
#define ENTITIES_ENEMY_H

#include <genesis.h>

/*
 * Enemy pool. FIXED SIZE, statically allocated: AGENTS.md forbids malloc, and
 * doc/ARCHITECTURE.md section 5 gives enemies a quota of 32 sprites from the
 * 80-sprite frame budget. At 16x16 each enemy is ONE hardware sprite, so the
 * pool size is the sprite cost.
 */
#define ENEMY_POOL_SIZE 6

typedef enum EnemyState {
    ENEMY_DEAD = 0,
    ENEMY_WALK = 1,
    ENEMY_PULLED = 2,   /* caught in the inhale vortex */
    ENEMY_SWALLOWED = 3
} EnemyState;

/* Which copy ability this enemy grants when swallowed. */
typedef enum CopyAbility {
    ABILITY_NONE = 0,
    ABILITY_FIRE = 1,
    ABILITY_BEAM = 2,
    ABILITY_CUTTER = 3,
    ABILITY_STONE = 4,
    ABILITY_SWORD = 5
} CopyAbility;

typedef struct Enemy {
    fix16 x;
    fix16 y;
    fix16 vx;
    EnemyState state;
    CopyAbility grants;
    u8 animFrame;
    u8 animTimer;
} Enemy;

void ENEMY_initPool(void);
Enemy* ENEMY_get(u16 index);
void ENEMY_spawn(u16 index, fix16 x, fix16 y, fix16 vx, CopyAbility grants);
void ENEMY_updateAll(fix16 kirbyX, fix16 kirbyY, bool inhaling, bool facingLeft);

/* Returns the ability of an enemy that finished being swallowed this frame,
 * or ABILITY_NONE. Clears the enemy. */
CopyAbility ENEMY_collectSwallowed(void);

u16 ENEMY_aliveCount(void);

#endif
