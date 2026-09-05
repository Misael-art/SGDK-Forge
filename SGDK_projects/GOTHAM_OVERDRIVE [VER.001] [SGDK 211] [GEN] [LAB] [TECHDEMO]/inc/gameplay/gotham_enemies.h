#ifndef GAMEPLAY_GOTHAM_ENEMIES_H
#define GAMEPLAY_GOTHAM_ENEMIES_H

#include <genesis.h>
#include "gameplay/gotham_raster.h"

#define MAX_DRONES 4

typedef struct GothamDrone {
    fix16 x;
    fix16 y;
    fix16 vx;
    fix16 vy;
    s16   health;
    u8    fireCooldown;
    u8    swoopPhase;
    bool  active;
    Sprite* sprite;
} GothamDrone;

void GOTHAM_ENEMIES_init(void);
void GOTHAM_ENEMIES_update(GothamRasterFx* rasterFx, s16 playerX, s16 playerY);
void GOTHAM_ENEMIES_reset(void);

u16 GOTHAM_ENEMIES_getActiveCount(void);

#endif
