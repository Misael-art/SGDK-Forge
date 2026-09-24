#ifndef GAMEPLAY_GOTHAM_PLAYER_H
#define GAMEPLAY_GOTHAM_PLAYER_H

#include <genesis.h>
#include "gameplay/gotham_raster.h"

typedef struct GothamPlayer {
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    s16   health;
    s16   maxHealth;
    s16   energy;
    s16   maxEnergy;
    u8    vulcanCooldown;
    u8    missileCooldown;
    u8    turboTimer;
    u8    invulnerableTimer;
    u8    animFrame;
    bool  isTurboActive;
    Sprite* sprite;
} GothamPlayer;

void GOTHAM_PLAYER_init(void);
void GOTHAM_PLAYER_update(GothamRasterFx* rasterFx);
void GOTHAM_PLAYER_damage(s16 amount, GothamRasterFx* rasterFx);
void GOTHAM_PLAYER_reset(void);

s16  GOTHAM_PLAYER_getX(void);
s16  GOTHAM_PLAYER_getY(void);
GothamPlayer* GOTHAM_PLAYER_getState(void);

#endif
