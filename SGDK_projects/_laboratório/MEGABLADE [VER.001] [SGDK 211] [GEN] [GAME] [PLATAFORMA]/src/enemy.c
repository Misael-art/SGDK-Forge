/**
 * enemy.c — Enemy object pool with patrol/chase AI
 *
 * All enemies are pre-allocated at startup. No malloc during gameplay.
 * States: DEAD -> PATROL <-> CHASE -> HURT -> PATROL/DEAD
 *
 * Player collision:
 *   - Player rolling INTO enemy from above/side = kills enemy
 *   - Player touches enemy while standing = player takes damage
 */

#include <genesis.h>

#include "enemy.h"
#include "player.h"
#include "camera.h"
#include "effects.h"
#include "hud.h"
#include "game_config.h"

#include "res_sprite.h"
#include "res_sound.h"

/* =========================================================================
 * Pool
 * ========================================================================= */
Enemy enemies[MAX_ENEMIES];

/* Spawn positions (world X, world Y) */
static const s16 spawnX[MAX_ENEMIES] = { 300, 600, 900, 1200, 1600, 2100 };
static const s16 spawnY[MAX_ENEMIES] = { 152, 152, 152, 152,  152,  152  };
static const s16 patrolRange = 100;

/* Enemy animation indices (enemy01.png = 2 anims: walk=0, hurt=1) */
#define ENEMY_ANIM_WALK  0
#define ENEMY_ANIM_HURT  1

/* AABB helper */
typedef struct { s16 x, y, w, h; } AABB;

static bool aabb_overlaps(AABB* a, AABB* b) {
    return (a->x < b->x + b->w) && (a->x + a->w > b->x)
        && (a->y < b->y + b->h) && (a->y + a->h > b->y);
}

/* =========================================================================
 * Init — create all sprite instances (hidden until spawned)
 * ========================================================================= */
u16 ENEMY_init(u16 vramIndex) {
    /* Load enemy palette from sprite definition */
    PAL_setPalette(PAL1, enemy_sprite.palette->data, CPU);

    for (u16 i = 0; i < MAX_ENEMIES; i++) {
        enemies[i].state  = ENEMY_DEAD;
        enemies[i].sprite = SPR_addSprite(&enemy_sprite, -64, 0,
            TILE_ATTR(PAL1, FALSE, FALSE, FALSE));
        SPR_setVisibility(enemies[i].sprite, HIDDEN);
    }

    return vramIndex;
}

/* =========================================================================
 * Spawn all enemies at predefined positions
 * ========================================================================= */
void ENEMY_spawnAll(void) {
    for (u16 i = 0; i < MAX_ENEMIES; i++) {
        Enemy* e = &enemies[i];
        e->state       = ENEMY_PATROL;
        e->posX        = FIX32(spawnX[i]);
        e->posY        = FIX32(spawnY[i]);
        e->movX        = ENEMY_PATROL_SPEED;
        e->patrolLeft  = spawnX[i] - patrolRange;
        e->patrolRight = spawnX[i] + patrolRange;
        e->hp          = ENEMY_HP;
        e->hurtTimer   = 0;
        SPR_setVisibility(e->sprite, VISIBLE);
        SPR_setAnim(e->sprite, ENEMY_ANIM_WALK);
    }
}

/* =========================================================================
 * Kill one enemy
 * ========================================================================= */
void ENEMY_kill(u16 idx) {
    Enemy* e = &enemies[idx];
    e->state = ENEMY_DEAD;
    SPR_setVisibility(e->sprite, HIDDEN);
    PLAYER_addScore(SCORE_PER_ENEMY);
    XGM2_playPCM(snd_hit, sizeof(snd_hit), SOUND_PCM_CH3);
}

/* =========================================================================
 * Update — AI + player collision detection
 * ========================================================================= */
void ENEMY_update(void) {
    /* Build player AABB in world space */
    s16 px = F32_toInt(playerPosX);
    s16 py = F32_toInt(playerPosY);

    AABB playerBox = {
        px + PLAYER_HITBOX_OX,
        py + PLAYER_HITBOX_OY,
        PLAYER_HITBOX_W,
        PLAYER_HITBOX_H
    };

    /* Is player "attacking"? Rolling state = in the air */
    bool playerAttacking = !playerOnGround;

    for (u16 i = 0; i < MAX_ENEMIES; i++) {
        Enemy* e = &enemies[i];
        if (e->state == ENEMY_DEAD) continue;

        /* Hurt cooldown */
        if (e->hurtTimer > 0) {
            e->hurtTimer--;
            if (e->hurtTimer == 0) {
                if (e->hp > 0) {
                    e->state = ENEMY_PATROL;
                    SPR_setAnim(e->sprite, ENEMY_ANIM_WALK);
                } else {
                    ENEMY_kill(i);
                    continue;
                }
            }
        }

        /* --- AI movement --- */
        s16 ex = F32_toInt(e->posX);

        /* Chase if player is within range */
        s16 dist = ex - px;
        if (dist < 0) dist = -dist;

        if (e->state == ENEMY_PATROL && dist < ENEMY_CHASE_DIST) {
            e->state = ENEMY_CHASE;
        }
        if (e->state == ENEMY_CHASE && dist > ENEMY_CHASE_DIST + 40) {
            e->state = ENEMY_PATROL;
        }

        if (e->state == ENEMY_PATROL) {
            e->posX += e->movX;
            ex = F32_toInt(e->posX);
            if (ex >= e->patrolRight) { e->movX = -ENEMY_PATROL_SPEED; }
            if (ex <= e->patrolLeft)  { e->movX =  ENEMY_PATROL_SPEED; }
        } else if (e->state == ENEMY_CHASE) {
            /* Move toward player */
            if (F32_toInt(e->posX) < px)
                e->movX =  ENEMY_CHASE_SPEED;
            else
                e->movX = -ENEMY_CHASE_SPEED;
            e->posX += e->movX;
        }

        /* Flip sprite toward movement direction */
        SPR_setHFlip(e->sprite, e->movX < 0);

        /* --- Collision with player --- */
        AABB enemyBox = {
            F32_toInt(e->posX) + ENEMY_HITBOX_OX,
            F32_toInt(e->posY) + ENEMY_HITBOX_OY,
            ENEMY_HITBOX_W,
            ENEMY_HITBOX_H
        };

        if (e->state != ENEMY_HURT && aabb_overlaps(&playerBox, &enemyBox)) {
            if (playerAttacking) {
                /* Player rolling = damages enemy */
                e->hp--;
                e->hurtTimer = 20;
                e->state = ENEMY_HURT;
                SPR_setAnim(e->sprite, ENEMY_ANIM_HURT);
                /* Bounce player upward */
                playerMovY = FIX32(-4);
            } else {
                /* Enemy damages player */
                PLAYER_takeDamage();
            }
        }
    }
}

/* =========================================================================
 * Update sprite screen positions
 * ========================================================================= */
void ENEMY_updateScreenPos(void) {
    for (u16 i = 0; i < MAX_ENEMIES; i++) {
        Enemy* e = &enemies[i];
        if (e->state == ENEMY_DEAD) continue;

        s16 sx = F32_toInt(e->posX) - camX;
        s16 sy = F32_toInt(e->posY) - camY - 24; /* -24 = sprite offset from feet */

        /* Hide if off-screen (saves scanline sprite budget) */
        if (sx < -64 || sx > 384 || sy < -64 || sy > 256) {
            SPR_setVisibility(e->sprite, HIDDEN);
        } else {
            SPR_setVisibility(e->sprite, VISIBLE);
            SPR_setPosition(e->sprite, sx, sy);
        }
    }
}
