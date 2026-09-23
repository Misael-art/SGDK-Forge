#ifndef LANE_MOVEMENT_H
#define LANE_MOVEMENT_H

#include <genesis.h>
#include "data/track_data.h"

typedef struct {
    s16 x;
    s16 y;
    u16 w;
    u16 h;
} AABB;

void Player_init(void);
void Player_update(void);
s16 Player_getScreenX(void);
s16 Player_getScreenY(void);
u8 Player_getLane(void);
bool Player_isJumping(void);
bool Player_isInvulnerable(void);
AABB Player_getHurtbox(void);
AABB Player_getPickupBox(void);
bool Player_isOnGround(void);
bool Player_isPulseActive(void);
u8 Player_getPulseTimer(void);
void Player_applyDamage(void);
void Player_triggerPulse(void);
bool Player_isChangingLane(void);
bool Player_canAct(void);
s16 Player_getVisualXOffset(void);
s16 Player_getVisualYOffset(void);

#endif
