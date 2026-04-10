#ifndef ENEMY_H
#define ENEMY_H

#include <genesis.h>
#include "game_config.h"

/* =========================================================================
 * ENEMY — Object pool, patrol/chase AI
 * ========================================================================= */

typedef enum {
    ENEMY_DEAD   = 0,
    ENEMY_PATROL = 1,
    ENEMY_CHASE  = 2,
    ENEMY_HURT   = 3
} EnemyState;

typedef struct {
    EnemyState state;
    Sprite*    sprite;
    fix32      posX, posY;
    fix32      movX;
    s16        patrolLeft, patrolRight;
    u16        hurtTimer;
    u8         hp;
} Enemy;

extern Enemy enemies[MAX_ENEMIES];

/* Public API */
u16  ENEMY_init(u16 vramIndex);
void ENEMY_spawnAll(void);
void ENEMY_update(void);
void ENEMY_updateScreenPos(void);
void ENEMY_kill(u16 idx);

#endif /* ENEMY_H */
