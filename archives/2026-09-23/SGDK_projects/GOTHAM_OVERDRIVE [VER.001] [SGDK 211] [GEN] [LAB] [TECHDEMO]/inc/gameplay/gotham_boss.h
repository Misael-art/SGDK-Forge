#ifndef GAMEPLAY_GOTHAM_BOSS_H
#define GAMEPLAY_GOTHAM_BOSS_H

#include <genesis.h>
#include "gameplay/gotham_raster.h"

typedef enum BossState {
    BOSS_STATE_INTRO = 0,
    BOSS_STATE_STRAFE_CANNON,
    BOSS_STATE_MISSILE_BARRAGE,
    BOSS_STATE_RAM_CHARGE,
    BOSS_STATE_OVERHEAT_RAGE,
    BOSS_STATE_DEFEATED
} BossState;

typedef struct GothamBoss {
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    s16   health;
    s16   maxHealth;
    BossState state;
    u16   stateTimer;
    u8    attackCooldown;
    u8    turretAngleFrame;
    u8    treadAnimFrame;
    u8    flashTimer;
    u8    defeatTimer;
    bool  missilePodOpen;
    bool  active;

    Sprite* sprChassis;
    Sprite* sprTurret;
    Sprite* sprLeftTread;
    Sprite* sprRightTread;
    Sprite* sprMissilePod;
} GothamBoss;

void GOTHAM_BOSS_init(void);
void GOTHAM_BOSS_update(GothamRasterFx* rasterFx, s16 playerX, s16 playerY);
void GOTHAM_BOSS_damage(s16 amount, GothamRasterFx* rasterFx);
void GOTHAM_BOSS_reset(void);

s16  GOTHAM_BOSS_getHealth(void);
s16  GOTHAM_BOSS_getMaxHealth(void);
GothamBoss* GOTHAM_BOSS_getState(void);

#endif
