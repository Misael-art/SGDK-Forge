#ifndef GAMEPLAY_CHASE_PURSUER_H
#define GAMEPLAY_CHASE_PURSUER_H

#include <genesis.h>

typedef struct ChaseCameraShake {
    s16 x;
    s16 y;
} ChaseCameraShake;

void CHASE_PURSUER_enter(void);
void CHASE_PURSUER_update(u16 pressure, bool allowAnimationUpload);
void CHASE_PURSUER_startImpact(s16 x, s16 y);
void CHASE_PURSUER_startPulse(s16 x, s16 y);
void CHASE_PURSUER_consumeShake(ChaseCameraShake* shake);
bool CHASE_PURSUER_isPulseActive(void);
void CHASE_PURSUER_hideFx(void);
void CHASE_PURSUER_setVisible(bool visible);
void CHASE_PURSUER_exit(void);

#endif
